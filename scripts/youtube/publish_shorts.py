#!/usr/bin/env python3
"""
ToxShield YouTube Shorts publisher — upload video directly via YouTube Data API v3.

Standalone CLI script that handles the full YouTube Shorts publishing pipeline:
1. Validate video (duration, aspect ratio, codec)
2. Authenticate with YouTube via OAuth 2.0 refresh token
3. Upload video via resumable upload
4. Return video ID and Shorts URL

Usage:
    # Publish a Short with title and description
    python scripts/youtube/publish_shorts.py \
        --video output/instagram/2026-03-25/toxic_callout/reel.mp4 \
        --title "5 things a gaslighter says that sound normal" \
        --description "Your gut was right. ..." \
        --tags "ToxShield,ToxicRelationships,Shorts"

    # Publish from content.json metadata
    python scripts/youtube/publish_shorts.py \
        --video output/instagram/2026-03-25/toxic_callout/reel.mp4 \
        --content-file output/instagram/2026-03-25/toxic_callout/content.json

    # Dry run (validate only, no upload)
    python scripts/youtube/publish_shorts.py \
        --video output/instagram/2026-03-25/toxic_callout/reel.mp4 \
        --title "Test" --dry-run
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load env from .env.local first, then .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.local")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

# ===========================================================================
# Upload Spacing & Posting Time Constants
# ===========================================================================

UPLOAD_LOG_PATH = PROJECT_ROOT / ".youtube_upload_log.json"
UPLOAD_COOLDOWN_HOURS = 4  # Minimum hours between uploads
OPTIMAL_SHORTS_WINDOW = (14, 15)  # 14:00-15:00 UTC
OPTIMAL_LONGFORM_WINDOW = (17, 18)  # 17:00-18:00 UTC


# ===========================================================================
# Upload Log Helpers
# ===========================================================================

def _read_upload_log() -> List[Dict[str, str]]:
    """Read upload log from disk. Returns empty list if file doesn't exist."""
    if not UPLOAD_LOG_PATH.exists():
        return []
    try:
        with open(UPLOAD_LOG_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _write_upload_log(entries: List[Dict[str, str]]) -> None:
    """Write upload log, keeping last 100 entries."""
    entries = entries[-100:]
    with open(UPLOAD_LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def _log_upload(video_id: str, title: str, video_path: str) -> None:
    """Append a successful upload to the log."""
    entries = _read_upload_log()
    entries.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "title": title,
        "path": video_path,
    })
    _write_upload_log(entries)


def _check_cooldown(force: bool = False) -> Tuple[bool, str]:
    """Check if enough time has passed since last upload.

    Returns (ok_to_upload, message).
    """
    if force:
        return True, "Cooldown overridden with --force"

    entries = _read_upload_log()
    if not entries:
        return True, "No previous uploads found"

    last = entries[-1]
    last_time = datetime.fromisoformat(last["timestamp"])
    now = datetime.now(timezone.utc)
    elapsed = now - last_time
    elapsed_hours = elapsed.total_seconds() / 3600
    remaining = UPLOAD_COOLDOWN_HOURS - elapsed_hours

    if remaining <= 0:
        return True, f"Last upload was {elapsed_hours:.1f}h ago (cooldown: {UPLOAD_COOLDOWN_HOURS}h)"

    return False, (
        f"Last upload was {elapsed_hours:.1f}h ago "
        f"(\"{last['title'][:50]}\" -> {last['video_id']}). "
        f"Cooldown: {UPLOAD_COOLDOWN_HOURS}h, wait {remaining:.1f}h more. "
        f"Use --force to override."
    )


# ===========================================================================
# Posting Time Helpers
# ===========================================================================

def _check_posting_time(is_short: bool = True) -> Tuple[bool, str]:
    """Check if current UTC time is within optimal posting window.

    Returns (in_window, message).
    """
    now = datetime.now(timezone.utc)
    window = OPTIMAL_SHORTS_WINDOW if is_short else OPTIMAL_LONGFORM_WINDOW
    hour = now.hour
    in_window = window[0] <= hour < window[1]

    if in_window:
        return True, (
            f"Current time {now.strftime('%H:%M')} UTC is within optimal window "
            f"({window[0]:02d}:00-{window[1]:02d}:00 UTC)"
        )

    next_window = now.replace(hour=window[0], minute=0, second=0, microsecond=0)
    if next_window <= now:
        next_window += timedelta(days=1)
    wait_seconds = (next_window - now).total_seconds()
    wait_hours = wait_seconds / 3600

    return False, (
        f"Current time {now.strftime('%H:%M')} UTC is outside optimal window "
        f"({window[0]:02d}:00-{window[1]:02d}:00 UTC). "
        f"Next window in {wait_hours:.1f}h ({next_window.strftime('%Y-%m-%d %H:%M')} UTC). "
        f"Use --schedule to queue for next optimal window."
    )


# ===========================================================================
# Exception Classes
# ===========================================================================

class YouTubePublishError(Exception):
    pass

class YouTubeAuthError(YouTubePublishError):
    pass

class YouTubeQuotaError(YouTubePublishError):
    pass


# ===========================================================================
# Video Validator
# ===========================================================================

class VideoValidator:
    """Validate video file for YouTube Shorts compatibility using ffprobe."""

    MAX_DURATION = 60  # seconds
    EXPECTED_WIDTH = 1080
    EXPECTED_HEIGHT = 1920

    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        self.ffprobe = shutil.which("ffprobe")

    def validate(self) -> Dict[str, Any]:
        """Run all validations. Returns metadata dict. Raises on hard failures."""
        if not self.video_path.exists():
            raise YouTubePublishError(f"Video file not found: {self.video_path}")

        size_mb = self.video_path.stat().st_size / (1024 * 1024)
        if size_mb < 0.1:
            raise YouTubePublishError(f"Video too small ({size_mb:.1f}MB), likely corrupt")

        metadata = {"path": str(self.video_path), "size_mb": round(size_mb, 1)}

        if not self.ffprobe:
            logger.warning("ffprobe not found, skipping video validation")
            return metadata

        probe = self._probe()
        if not probe:
            logger.warning("ffprobe failed, skipping video validation")
            return metadata

        # Duration check
        duration = float(probe.get("format", {}).get("duration", 0))
        metadata["duration"] = round(duration, 1)
        if duration > self.MAX_DURATION:
            logger.warning(
                f"Video is {duration:.1f}s (max {self.MAX_DURATION}s for Shorts). "
                "YouTube may not classify this as a Short."
            )
        elif duration > 0:
            logger.info(f"Duration: {duration:.1f}s (OK for Shorts)")

        # Resolution and aspect ratio check
        video_stream = next(
            (s for s in probe.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )
        if video_stream:
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            metadata["width"] = width
            metadata["height"] = height
            metadata["codec"] = video_stream.get("codec_name", "unknown")

            if width > 0 and height > 0:
                if height > width:
                    logger.info(f"Resolution: {width}x{height} (vertical, OK for Shorts)")
                else:
                    logger.warning(
                        f"Resolution: {width}x{height} (not vertical). "
                        "Shorts require vertical (9:16) video."
                    )

        return metadata

    def _probe(self) -> Optional[Dict]:
        """Run ffprobe and return parsed JSON output."""
        try:
            result = subprocess.run(
                [
                    self.ffprobe, "-v", "quiet",
                    "-print_format", "json",
                    "-show_format", "-show_streams",
                    str(self.video_path),
                ],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        return None


# ===========================================================================
# YouTube Publisher
# ===========================================================================

class YouTubePublisher:
    """Upload videos to YouTube Shorts via Data API v3 resumable upload."""

    MAX_RETRIES = 3
    CHUNK_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

        if not all([client_id, client_secret, refresh_token]):
            missing = []
            if not client_id:
                missing.append("YOUTUBE_CLIENT_ID")
            if not client_secret:
                missing.append("YOUTUBE_CLIENT_SECRET")
            if not refresh_token:
                missing.append("YOUTUBE_REFRESH_TOKEN")
            raise YouTubeAuthError(
                f"YouTube credentials missing: {', '.join(missing)}. "
                "Run: python scripts/youtube/auth_setup.py --client-secrets <path>"
            )

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            raise ImportError(
                "Google API client not installed. Run:\n"
                "  pip install -r scripts/youtube/requirements.txt"
            )

        self.credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )

        self.youtube = build("youtube", "v3", credentials=self.credentials)

    def publish_short(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        category_id: str = "22",
        privacy: str = "public",
    ) -> Dict[str, Any]:
        """Upload a video as a YouTube Short."""
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError

        # Enforce title length
        if len(title) > 100:
            logger.warning(f"Title too long ({len(title)} chars), truncating to 100")
            title = title[:97] + "..."

        # Ensure #Shorts tag in description
        description = self._ensure_shorts_tag(title, description)

        # Build tags list
        if tags is None:
            tags = []
        if "Shorts" not in tags:
            tags.insert(0, "Shorts")

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=self.CHUNK_SIZE,
        )

        logger.info(f"Uploading: {title}")
        logger.info(f"Privacy: {privacy}, Category: {category_id}")

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = self._upload_with_retry(request)

        video_id = response["id"]
        result = {
            "video_id": video_id,
            "url": f"https://youtube.com/shorts/{video_id}",
            "status": "published" if privacy == "public" else privacy,
        }

        logger.info(f"Upload complete: {result['url']}")
        return result

    def _upload_with_retry(self, request) -> Dict:
        """Execute resumable upload with exponential backoff retry."""
        from googleapiclient.errors import HttpError

        response = None
        retry = 0

        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")
            except HttpError as e:
                error_code = e.resp.status
                error_reason = ""
                try:
                    error_detail = json.loads(e.content)
                    errors = error_detail.get("error", {}).get("errors", [])
                    if errors:
                        error_reason = errors[0].get("reason", "")
                except (json.JSONDecodeError, KeyError):
                    pass

                if error_code == 403 and "quotaExceeded" in str(e.content):
                    raise YouTubeQuotaError(
                        "YouTube daily quota exceeded (~6 uploads/day with default quota). "
                        "Try again after midnight Pacific Time."
                    )

                if error_code == 401:
                    raise YouTubeAuthError(
                        "YouTube authentication failed. Token may be expired or revoked. "
                        "Re-run: python scripts/youtube/auth_setup.py"
                    )

                if error_code == 400:
                    raise YouTubePublishError(
                        f"YouTube rejected the request: {e.content.decode('utf-8', errors='replace')}"
                    )

                if error_code >= 500 and retry < self.MAX_RETRIES:
                    retry += 1
                    wait = 2 ** retry
                    logger.warning(
                        f"Server error ({error_code}), retrying in {wait}s "
                        f"({retry}/{self.MAX_RETRIES})"
                    )
                    time.sleep(wait)
                    continue

                raise YouTubePublishError(
                    f"Upload failed (HTTP {error_code}): "
                    f"{e.content.decode('utf-8', errors='replace')}"
                )

            except Exception as e:
                if retry < self.MAX_RETRIES:
                    retry += 1
                    wait = 2 ** retry
                    logger.warning(f"Upload error: {e}, retrying in {wait}s ({retry}/{self.MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                raise YouTubePublishError(f"Upload failed after {self.MAX_RETRIES} retries: {e}")

        return response

    @staticmethod
    def _ensure_shorts_tag(title: str, description: str) -> str:
        """Auto-append #Shorts to description if not found in title or description."""
        shorts_pattern = re.compile(r"#Shorts", re.IGNORECASE)
        if not shorts_pattern.search(title) and not shorts_pattern.search(description):
            description = description.rstrip() + "\n\n#Shorts"
        return description


# ===========================================================================
# Content File Reader
# ===========================================================================

def read_content_file(path: str) -> Dict[str, str]:
    """Read content.json and derive YouTube title/description."""
    with open(path) as f:
        data = json.load(f)

    headline = data.get("headline", "")
    cta = data.get("cta", "")
    adaptations = data.get("format_adaptations", {})

    # Build description from slide content
    desc_parts = []
    if headline:
        desc_parts.append(headline)
        desc_parts.append("")

    # Collect slide text in order
    for i in range(2, 11):
        slide_title = adaptations.get(f"slide_{i}_title", "")
        slide_lines = adaptations.get(f"slide_{i}_lines", [])
        if slide_title:
            desc_parts.append(slide_title)
        if slide_lines:
            desc_parts.extend(slide_lines)
        if slide_title or slide_lines:
            desc_parts.append("")

    if cta:
        desc_parts.append(cta)
        desc_parts.append("")

    desc_parts.append("Go to https://toxshield.in/ to analyze the toxic people in your life.")

    return {
        "title": headline[:100] if headline else "",
        "description": "\n".join(desc_parts),
    }


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Upload video to YouTube Shorts for ToxShield"
    )
    parser.add_argument("--video", "-v", required=True, help="Path to MP4 video file")
    parser.add_argument("--title", "-t", help="Video title (max 100 chars)")
    parser.add_argument("--description", "-d", help="Video description")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--content-file", help="JSON file with content metadata")
    parser.add_argument(
        "--category-id", default="22",
        help="YouTube category ID (default: 22 = People & Blogs)",
    )
    parser.add_argument(
        "--privacy", choices=["public", "unlisted", "private"],
        default="public", help="Privacy status (default: public)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't upload")
    parser.add_argument("--force", action="store_true", help="Override upload cooldown (4h spacing)")
    parser.add_argument("--show-log", action="store_true", help="Show recent upload log and exit")
    parser.add_argument("--schedule", action="store_true", help="Wait until next optimal posting window (14:00 UTC)")
    parser.add_argument("--ignore-time", action="store_true", help="Skip posting time check")

    args = parser.parse_args()

    # Show upload log and exit
    if args.show_log:
        entries = _read_upload_log()
        if not entries:
            print("No uploads logged yet.")
        else:
            print(f"Last {min(len(entries), 10)} uploads:")
            for entry in entries[-10:]:
                print(f"  {entry['timestamp']}  {entry['video_id']}  {entry['title'][:60]}")
        return

    # Determine title and description
    title = args.title or ""
    description = args.description or ""
    tags_list = [t.strip() for t in args.tags.split(",")] if args.tags else []

    if args.content_file:
        content = read_content_file(args.content_file)
        if not title:
            title = content["title"]
        if not description:
            description = content["description"]

    if not title:
        parser.error("Title required. Provide --title or --content-file with a headline")

    # Parse tags
    if not tags_list:
        tags_list = ["ToxShield", "ToxicRelationships", "Shorts"]

    print(f"Title: {title}")
    print(f"Description ({len(description)} chars): {description[:150]}{'...' if len(description) > 150 else ''}")
    print(f"Tags: {', '.join(tags_list)}")
    print(f"Privacy: {args.privacy}")

    # Step 1: Validate video
    print("\n--- Step 1: Validating video ---")
    validator = VideoValidator(args.video)
    metadata = validator.validate()
    print(f"  File: {metadata['path']} ({metadata.get('size_mb', '?')}MB)")
    if "duration" in metadata:
        print(f"  Duration: {metadata['duration']}s")
    if "width" in metadata:
        print(f"  Resolution: {metadata['width']}x{metadata['height']}")
    if "codec" in metadata:
        print(f"  Codec: {metadata['codec']}")

    if args.dry_run:
        print("\n--- DRY RUN: Skipping YouTube upload ---")
        result = {"status": "dry_run", "title": title, "video": args.video, **metadata}
        print(json.dumps(result))
        return

    # Step 2: Check upload cooldown
    print("\n--- Step 2: Checking upload spacing ---")
    ok, msg = _check_cooldown(force=args.force)
    print(f"  {msg}")
    if not ok:
        print("\nUpload blocked. Space uploads at least 4 hours apart.", file=sys.stderr)
        sys.exit(1)

    # Step 3: Check posting time
    if not args.ignore_time:
        print("\n--- Step 3: Checking posting time ---")
        in_window, time_msg = _check_posting_time(is_short=True)
        print(f"  {time_msg}")
        if not in_window:
            if args.schedule:
                now = datetime.now(timezone.utc)
                next_window = now.replace(hour=OPTIMAL_SHORTS_WINDOW[0], minute=0, second=0, microsecond=0)
                if next_window <= now:
                    next_window += timedelta(days=1)
                wait_seconds = (next_window - now).total_seconds()
                print(f"\n  Scheduled: will upload at {next_window.strftime('%Y-%m-%d %H:%M')} UTC "
                      f"(waiting {wait_seconds / 3600:.1f}h)")
                time.sleep(wait_seconds)
                print(f"\n  Wake up! Proceeding with upload...")
            else:
                print("  (Proceeding anyway. Use --schedule to wait for optimal window.)")

    # Step 4: Upload to YouTube
    print("\n--- Step 4: Uploading to YouTube ---")
    try:
        publisher = YouTubePublisher()
    except (YouTubeAuthError, ImportError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = publisher.publish_short(
            video_path=args.video,
            title=title,
            description=description,
            tags=tags_list,
            category_id=args.category_id,
            privacy=args.privacy,
        )

        _log_upload(result["video_id"], title, args.video)

        print(f"\nYouTube Short published successfully!")
        print(f"  Video ID: {result['video_id']}")
        print(f"  URL: {result['url']}")
        print(f"  Status: {result['status']}")
        print(f"\n{json.dumps(result)}")

    except YouTubeQuotaError as e:
        print(f"\nQuota exceeded: {e}", file=sys.stderr)
        print("Fix: Wait until midnight PT (quota resets daily).", file=sys.stderr)
        sys.exit(1)

    except YouTubeAuthError as e:
        print(f"\nAuth error: {e}", file=sys.stderr)
        print("Fix: Re-run: python scripts/youtube/auth_setup.py", file=sys.stderr)
        sys.exit(1)

    except YouTubePublishError as e:
        print(f"\nUpload failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
