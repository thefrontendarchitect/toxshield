#!/usr/bin/env python3
"""
ToxShield YouTube long-form video publisher.

Uploads long-form videos (5-20 minutes) via YouTube Data API v3. Reuses the
same OAuth and upload infrastructure as publish_shorts.py but with different
validation rules and no #Shorts tag injection.

Supports chapter markers via --chapters-file and respects the 17:00 UTC
optimal posting window for long-form content.

Usage:
    # Publish a long-form video
    python scripts/youtube/publish_longform.py \
        --video output/youtube/longform/narcissist_storytime/video.mp4 \
        --title "I Analyzed a Textbook Narcissist — Score: 9.2/10" \
        --description "Full forensic breakdown..." \
        --chapters-file output/youtube/longform/narcissist_storytime/chapters.txt

    # Dry run (validate only)
    python scripts/youtube/publish_longform.py \
        --video output/youtube/longform/video.mp4 \
        --title "Test" --dry-run

    # Schedule for optimal window (17:00 UTC)
    python scripts/youtube/publish_longform.py \
        --video output/youtube/longform/video.mp4 \
        --title "Pattern Deep Dive" --schedule
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Import shared infrastructure from publish_shorts
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "youtube"))
from publish_shorts import (
    YouTubePublisher,
    YouTubeAuthError,
    YouTubePublishError,
    YouTubeQuotaError,
    VideoValidator,
    read_content_file,
    _check_cooldown,
    _check_posting_time,
    _log_upload,
    _read_upload_log,
    OPTIMAL_LONGFORM_WINDOW,
)


# ===========================================================================
# Long-Form Video Validator
# ===========================================================================

class LongFormValidator(VideoValidator):
    """Validate video for long-form YouTube (not Shorts)."""

    MAX_DURATION = 1200  # 20 minutes
    MIN_DURATION = 300   # 5 minutes

    def validate(self):
        metadata = super().validate()

        duration = metadata.get("duration", 0)
        if duration > 0:
            if duration < self.MIN_DURATION:
                logger.warning(
                    f"Video is {duration:.1f}s ({duration / 60:.1f}m), "
                    f"below recommended minimum {self.MIN_DURATION}s ({self.MIN_DURATION / 60:.0f}m) "
                    "for long-form content."
                )
            elif duration > self.MAX_DURATION:
                logger.warning(
                    f"Video is {duration:.1f}s ({duration / 60:.1f}m), "
                    f"above recommended maximum {self.MAX_DURATION}s ({self.MAX_DURATION / 60:.0f}m)."
                )
            else:
                logger.info(
                    f"Duration: {duration:.1f}s ({duration / 60:.1f}m) — OK for long-form"
                )

        return metadata


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Upload long-form video to YouTube for ToxShield"
    )
    parser.add_argument("--video", "-v", required=True, help="Path to MP4 video file")
    parser.add_argument("--title", "-t", help="Video title (max 100 chars)")
    parser.add_argument("--description", "-d", help="Video description")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--content-file", help="JSON file with content metadata")
    parser.add_argument("--chapters-file", help="Path to chapters.txt (prepended to description)")
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
    parser.add_argument("--schedule", action="store_true", help="Wait until next optimal window (17:00 UTC)")
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

    # Prepend chapter markers to description
    if args.chapters_file:
        chapters_path = Path(args.chapters_file)
        if chapters_path.exists():
            chapters_text = chapters_path.read_text().strip()
            if description:
                description = f"{description}\n\n{chapters_text}"
            else:
                description = chapters_text
            logger.info(f"Prepended chapter markers from {chapters_path}")
        else:
            logger.warning(f"Chapters file not found: {chapters_path}")

    # Parse tags (no #Shorts tag for long-form)
    if not tags_list:
        tags_list = ["ToxShield", "ToxicRelationships", "BehavioralAnalysis"]

    print(f"Title: {title}")
    print(f"Description ({len(description)} chars): {description[:150]}{'...' if len(description) > 150 else ''}")
    print(f"Tags: {', '.join(tags_list)}")
    print(f"Privacy: {args.privacy}")

    # Step 1: Validate video (long-form rules)
    print("\n--- Step 1: Validating video ---")
    validator = LongFormValidator(args.video)
    metadata = validator.validate()
    print(f"  File: {metadata['path']} ({metadata.get('size_mb', '?')}MB)")
    if "duration" in metadata:
        print(f"  Duration: {metadata['duration']}s ({metadata['duration'] / 60:.1f}m)")
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

    # Step 3: Check posting time (17:00 UTC for long-form)
    if not args.ignore_time:
        print("\n--- Step 3: Checking posting time ---")
        in_window, time_msg = _check_posting_time(is_short=False)
        print(f"  {time_msg}")
        if not in_window:
            if args.schedule:
                now = datetime.now(timezone.utc)
                next_window = now.replace(hour=OPTIMAL_LONGFORM_WINDOW[0], minute=0, second=0, microsecond=0)
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
        # Use the underlying API directly to skip #Shorts tag injection
        from googleapiclient.http import MediaFileUpload

        if len(title) > 100:
            logger.warning(f"Title too long ({len(title)} chars), truncating to 100")
            title = title[:97] + "..."

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags_list,
                "categoryId": args.category_id,
            },
            "status": {
                "privacyStatus": args.privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            args.video,
            mimetype="video/mp4",
            resumable=True,
            chunksize=publisher.CHUNK_SIZE,
        )

        logger.info(f"Uploading: {title}")
        request = publisher.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = publisher._upload_with_retry(request)
        video_id = response["id"]

        result = {
            "video_id": video_id,
            "url": f"https://youtube.com/watch?v={video_id}",
            "status": "published" if args.privacy == "public" else args.privacy,
        }

        _log_upload(video_id, title, args.video)

        print(f"\nYouTube long-form video published successfully!")
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
