#!/usr/bin/env python3
"""
ToxShield Instagram publisher — upload to Cloudinary + publish via Graph API.

Standalone CLI script that handles the full publishing pipeline:
1. Upload images to Cloudinary (get public URLs)
2. Create Instagram media containers via Graph API
3. Publish carousel or single-image post
4. Clean up Cloudinary images after successful publish

Usage:
    # Publish carousel from a directory of images
    python scripts/instagram/publish_post.py \
        --images output/instagram/2026-03-24/toxic_callout/ \
        --caption "They're not 'brutally honest.' They're just brutal." \
        --hashtags "#ToxShield #ToxicRelationships #GaslightingAwareness"

    # Publish single image
    python scripts/instagram/publish_post.py \
        --single-image output/instagram/post.png \
        --caption "Pattern detected."

    # Dry run (upload to Cloudinary but don't publish to Instagram)
    python scripts/instagram/publish_post.py \
        --images output/instagram/toxic_callout/ \
        --caption "..." \
        --dry-run
"""

import argparse
import glob
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load env from .env.local first, then .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.local")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # Env vars must be set in the shell if python-dotenv is not installed

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ===========================================================================
# Exception Classes
# ===========================================================================

class InstagramPublishError(Exception):
    pass

class InstagramRateLimitError(InstagramPublishError):
    pass

class InstagramAuthError(InstagramPublishError):
    pass

class CloudinaryUploadError(Exception):
    pass


# ===========================================================================
# Cloudinary Uploader
# ===========================================================================

class CloudinaryUploader:
    """Upload images to Cloudinary for public URL access."""

    MAX_RETRIES = 2

    def __init__(self):
        if not CLOUDINARY_AVAILABLE:
            raise ImportError("cloudinary not installed. Run: pip install cloudinary>=1.38.0")

        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Cloudinary credentials missing. Set CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in .env.local"
            )

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    def upload_image(self, file_path: str, folder: str = "toxshield-instagram") -> Dict[str, str]:
        path = Path(file_path)
        if not path.exists():
            raise CloudinaryUploadError(f"File not found: {file_path}")

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                result = cloudinary.uploader.upload(
                    str(path),
                    folder=folder,
                    resource_type="image",
                    overwrite=True,
                    unique_filename=True,
                )
                upload_data = {
                    "public_id": result["public_id"],
                    "secure_url": result["secure_url"],
                    "width": result.get("width", 0),
                    "height": result.get("height", 0),
                }

                if not self._verify_url(upload_data["secure_url"]):
                    raise CloudinaryUploadError(f"URL not accessible: {upload_data['secure_url']}")

                logger.info(f"Uploaded {path.name} -> {upload_data['secure_url']}")
                return upload_data

            except cloudinary.exceptions.Error as e:
                if attempt < self.MAX_RETRIES:
                    wait = 2 ** attempt
                    logger.warning(f"Upload failed, retrying in {wait}s: {e}")
                    time.sleep(wait)
                else:
                    raise CloudinaryUploadError(f"Upload failed after {self.MAX_RETRIES + 1} attempts: {e}")

    def upload_carousel(self, file_paths: List[str]) -> List[Dict[str, str]]:
        results = []
        for i, fp in enumerate(file_paths):
            logger.info(f"Uploading slide {i + 1}/{len(file_paths)}: {fp}")
            result = self.upload_image(fp)
            results.append(result)
        return results

    def delete_image(self, public_id: str) -> bool:
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"Error deleting {public_id}: {e}")
            return False

    def upload_video(self, file_path: str, folder: str = "toxshield-instagram") -> Dict[str, str]:
        """Upload a video file to Cloudinary for Reel publishing."""
        path = Path(file_path)
        if not path.exists():
            raise CloudinaryUploadError(f"Video file not found: {file_path}")

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                result = cloudinary.uploader.upload(
                    str(path),
                    folder=folder,
                    resource_type="video",
                    overwrite=True,
                    unique_filename=True,
                )
                upload_data = {
                    "public_id": result["public_id"],
                    "secure_url": result["secure_url"],
                    "duration": str(result.get("duration", 0)),
                    "format": result.get("format", "mp4"),
                    "width": result.get("width", 0),
                    "height": result.get("height", 0),
                }

                if not self._verify_url(upload_data["secure_url"], timeout=30):
                    raise CloudinaryUploadError(f"Video URL not accessible: {upload_data['secure_url']}")

                logger.info(f"Uploaded video {path.name} -> {upload_data['secure_url']}")
                return upload_data

            except cloudinary.exceptions.Error as e:
                if attempt < self.MAX_RETRIES:
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"Video upload failed, retrying in {wait}s: {e}")
                    time.sleep(wait)
                else:
                    raise CloudinaryUploadError(f"Video upload failed after {self.MAX_RETRIES + 1} attempts: {e}")

    def delete_video(self, public_id: str) -> bool:
        """Delete a video from Cloudinary."""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type="video")
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"Error deleting video {public_id}: {e}")
            return False

    def cleanup_uploads(self, upload_results: List[Dict[str, str]]) -> int:
        deleted = 0
        for result in upload_results:
            if self.delete_image(result["public_id"]):
                deleted += 1
        return deleted

    def _verify_url(self, url: str, timeout: int = 10) -> bool:
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException:
            return False


# ===========================================================================
# Instagram Publisher
# ===========================================================================

class InstagramPublisher:
    """Publish content to Instagram via Graph API."""

    BASE_URL = "https://graph.facebook.com/v17.0"
    MAX_RETRIES = 3
    POLL_INTERVAL = 5
    MAX_POLL_ATTEMPTS = 24
    CONTAINER_DELAY = 1

    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN")
        self.user_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

        if not self.access_token:
            raise ValueError("INSTAGRAM_PAGE_ACCESS_TOKEN not set in .env.local")
        if not self.user_id:
            raise ValueError("INSTAGRAM_BUSINESS_ACCOUNT_ID not set in .env.local")

    def publish_carousel(self, image_urls: List[str], caption: str) -> Dict[str, Any]:
        if len(image_urls) < 2:
            raise InstagramPublishError("Carousel requires at least 2 images")
        if len(image_urls) > 10:
            raise InstagramPublishError("Carousel allows maximum 10 images")
        if len(caption) > 2200:
            logger.warning(f"Caption too long ({len(caption)} chars), truncating")
            caption = caption[:2200]

        logger.info(f"Publishing carousel with {len(image_urls)} images")

        # Step 1: Create individual media containers
        children_ids = []
        for i, url in enumerate(image_urls):
            logger.info(f"Creating container {i + 1}/{len(image_urls)}")
            container_id = self._create_media_container(image_url=url, is_carousel_item=True)
            children_ids.append(container_id)
            if i < len(image_urls) - 1:
                time.sleep(self.CONTAINER_DELAY)

        # Step 2: Create carousel container
        carousel_id = self._create_carousel_container(children_ids, caption)

        # Step 3: Wait and publish
        self._wait_for_container(carousel_id)
        result = self._publish_media(carousel_id)

        logger.info(f"Carousel published: {result}")
        return result

    def publish_single_image(self, image_url: str, caption: str) -> Dict[str, Any]:
        if len(caption) > 2200:
            caption = caption[:2200]

        container_id = self._create_media_container(image_url=image_url, caption=caption)
        self._wait_for_container(container_id)
        return self._publish_media(container_id)

    def publish_reel(
        self, video_url: str, caption: str, share_to_feed: bool = True,
    ) -> Dict[str, Any]:
        """Publish a Reel via Instagram Graph API."""
        if len(caption) > 2200:
            logger.warning(f"Caption too long ({len(caption)} chars), truncating")
            caption = caption[:2200]

        logger.info("Publishing Reel...")
        container_id = self._create_reel_container(video_url, caption, share_to_feed)

        # Video containers take longer to process (30-120s)
        self._wait_for_container(container_id, max_attempts=36)
        result = self._publish_media(container_id)

        logger.info(f"Reel published: {result}")
        return result

    def _create_reel_container(
        self, video_url: str, caption: str, share_to_feed: bool = True,
    ) -> str:
        """Create a Reel media container."""
        url = f"{self.BASE_URL}/{self.user_id}/media"
        data = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true" if share_to_feed else "false",
            "access_token": self.access_token,
        }
        result = self._make_request("POST", url, data=data)
        container_id = result.get("id")
        if not container_id:
            raise InstagramPublishError(f"No reel container ID returned: {result}")
        return container_id

    def _create_media_container(
        self, image_url: str, is_carousel_item: bool = False, caption: Optional[str] = None,
    ) -> str:
        url = f"{self.BASE_URL}/{self.user_id}/media"
        data = {"image_url": image_url, "access_token": self.access_token}
        if is_carousel_item:
            data["is_carousel_item"] = "true"
        if caption:
            data["caption"] = caption

        result = self._make_request("POST", url, data=data)
        container_id = result.get("id")
        if not container_id:
            raise InstagramPublishError(f"No container ID returned: {result}")
        return container_id

    def _create_carousel_container(self, children_ids: List[str], caption: str) -> str:
        url = f"{self.BASE_URL}/{self.user_id}/media"
        data = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": self.access_token,
        }
        result = self._make_request("POST", url, data=data)
        container_id = result.get("id")
        if not container_id:
            raise InstagramPublishError(f"No carousel container ID: {result}")
        return container_id

    def _wait_for_container(self, container_id: str, max_attempts: Optional[int] = None) -> None:
        attempts = max_attempts or self.MAX_POLL_ATTEMPTS
        for attempt in range(attempts):
            status = self._check_container_status(container_id)
            if status == "FINISHED":
                return
            elif status == "ERROR":
                raise InstagramPublishError(f"Container {container_id} failed")
            elif status == "EXPIRED":
                raise InstagramPublishError(f"Container {container_id} expired")
            logger.info(f"Processing... ({attempt + 1}/{attempts})")
            time.sleep(self.POLL_INTERVAL)

        raise InstagramPublishError(
            f"Container timeout after {attempts * self.POLL_INTERVAL}s"
        )

    def _check_container_status(self, container_id: str) -> str:
        url = f"{self.BASE_URL}/{container_id}"
        params = {"fields": "status_code", "access_token": self.access_token}
        result = self._make_request("GET", url, params=params)
        return result.get("status_code", "IN_PROGRESS")

    def _publish_media(self, creation_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{self.user_id}/media_publish"
        data = {"creation_id": creation_id, "access_token": self.access_token}
        result = self._make_request("POST", url, data=data)
        post_id = result.get("id")
        if not post_id:
            raise InstagramPublishError(f"No post ID returned: {result}")
        return {"post_id": post_id, "status": "published"}

    def _make_request(
        self, method: str, url: str,
        params: Optional[Dict] = None, data: Optional[Dict] = None,
        attempt: int = 0,
    ) -> Dict[str, Any]:
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, data=data, timeout=60)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            result = response.json()

            if "error" in result:
                return self._handle_api_error(result["error"], method, url, params, data, attempt)
            return result

        except requests.Timeout:
            if attempt < self.MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning(f"Timeout, retrying in {wait}s ({attempt + 1}/{self.MAX_RETRIES})")
                time.sleep(wait)
                return self._make_request(method, url, params, data, attempt + 1)
            raise InstagramPublishError(f"Timeout after {self.MAX_RETRIES} attempts")

        except requests.RequestException as e:
            if attempt < self.MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning(f"Request failed: {e}, retrying in {wait}s")
                time.sleep(wait)
                return self._make_request(method, url, params, data, attempt + 1)
            raise InstagramPublishError(f"Request failed: {e}")

    def _handle_api_error(
        self, error: Dict, method: str, url: str,
        params: Optional[Dict], data: Optional[Dict], attempt: int,
    ) -> Dict[str, Any]:
        error_code = error.get("code")
        error_msg = error.get("message", "Unknown error")

        logger.error(f"Instagram API error: code={error_code}, message={error_msg}")

        if error_code in [4, 17, 32, 613]:
            if attempt < self.MAX_RETRIES - 1:
                wait = (2 ** attempt) * 60
                logger.warning(f"Rate limit, waiting {wait}s")
                time.sleep(wait)
                return self._make_request(method, url, params, data, attempt + 1)
            raise InstagramRateLimitError(f"Rate limit: {error_msg}")

        if error_code in [190, 200]:
            raise InstagramAuthError(f"Auth error: {error_msg}")

        raise InstagramPublishError(f"API error {error_code}: {error_msg}")


# ===========================================================================
# CLI
# ===========================================================================

def collect_images(image_path: str) -> List[str]:
    """Collect image file paths from a directory or glob pattern."""
    path = Path(image_path)
    if path.is_dir():
        images = sorted(
            list(path.glob("*.png")) + list(path.glob("*.jpg")) + list(path.glob("*.jpeg"))
        )
        return [str(p) for p in images]
    elif path.is_file():
        return [str(path)]
    else:
        return sorted(glob.glob(image_path))


def build_caption(caption: str, hashtags: str = "") -> str:
    """Assemble final caption with hashtags."""
    parts = [caption.strip()]
    if hashtags:
        parts.append("")
        parts.append(hashtags.strip())

    full_caption = "\n".join(parts)

    if len(full_caption) > 2200:
        print(f"Warning: Caption is {len(full_caption)} chars (max 2200), truncating hashtags")
        available = 2200 - len(caption) - 2
        if available > 0:
            full_caption = caption.strip() + "\n\n" + hashtags.strip()[:available]
        else:
            full_caption = caption.strip()[:2200]

    return full_caption


def main():
    parser = argparse.ArgumentParser(
        description="Upload images and publish to Instagram for ToxShield"
    )
    parser.add_argument("--images", "-i", help="Directory or glob pattern for carousel images")
    parser.add_argument("--single-image", help="Path to a single image to publish")
    parser.add_argument("--video", help="Path to video file for Reel publishing")
    parser.add_argument("--format", "-f", choices=["carousel", "image", "reel"],
                        default=None, help="Post format (auto-detected if not specified)")
    parser.add_argument("--caption", "-c", help="Post caption text")
    parser.add_argument("--hashtags", default="", help="Hashtags to append to caption")
    parser.add_argument("--content-file", help="JSON file with content data")
    parser.add_argument("--dry-run", action="store_true", help="Upload to Cloudinary only")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep files on Cloudinary")
    parser.add_argument("--no-share-to-feed", action="store_true",
                        help="Don't share Reel to main feed")

    args = parser.parse_args()

    # Determine caption
    caption = args.caption or ""
    hashtags = args.hashtags or ""

    if args.content_file:
        with open(args.content_file) as f:
            content_data = json.load(f)
        if not caption:
            caption = content_data.get("caption", "")
        if not hashtags:
            tags = content_data.get("hashtags", [])
            hashtags = " ".join(tags) if isinstance(tags, list) else str(tags)

    if not caption:
        parser.error("Caption required. Provide --caption or --content-file")

    full_caption = build_caption(caption, hashtags)
    print(f"Caption ({len(full_caption)} chars):")
    print(f"  {full_caption[:200]}{'...' if len(full_caption) > 200 else ''}")

    # Determine format
    is_reel = args.format == "reel" or args.video

    try:
        uploader = CloudinaryUploader()
    except (ImportError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if is_reel:
        # ---- Reel publishing path ----
        video_path = args.video
        if not video_path:
            parser.error("--video required for Reel format")
        if not Path(video_path).exists():
            print(f"Error: Video file not found: {video_path}", file=sys.stderr)
            sys.exit(1)

        print(f"\nPublishing Reel from: {video_path}")

        # Step 1: Upload video to Cloudinary
        print("\n--- Step 1: Uploading video to Cloudinary ---")
        upload_result = uploader.upload_video(video_path)
        video_url = upload_result["secure_url"]
        print(f"  Video URL: {video_url}")

        if args.dry_run:
            print("\n--- DRY RUN: Skipping Instagram publish ---")
            print(json.dumps({"status": "dry_run", "video_url": video_url}))
            return

        # Step 2: Publish Reel to Instagram
        print("\n--- Step 2: Publishing Reel to Instagram ---")
        try:
            publisher = InstagramPublisher()
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            result = publisher.publish_reel(
                video_url, full_caption,
                share_to_feed=not args.no_share_to_feed,
            )
            print(f"\nReel published successfully!")
            print(f"  Post ID: {result['post_id']}")

            if not args.no_cleanup:
                print("\n--- Step 3: Cleaning up Cloudinary ---")
                if uploader.delete_video(upload_result["public_id"]):
                    print("  Deleted temporary video")

            print(f"\n{json.dumps(result)}")

        except InstagramPublishError as e:
            print(f"\nReel publish failed: {e}", file=sys.stderr)
            error_str = str(e)
            if "Auth" in error_str or "190" in error_str:
                print("Fix: Token may have expired. Refresh or generate a new one.", file=sys.stderr)
            elif "Rate limit" in error_str:
                print("Fix: Rate limit hit. Wait 60s and retry.", file=sys.stderr)
            elif "EXPIRED" in error_str:
                print("Fix: Container expired. Re-run the script.", file=sys.stderr)
            print(f"\nCloudinary video preserved for retry: {video_url}", file=sys.stderr)
            sys.exit(1)

    else:
        # ---- Image/Carousel publishing path (existing) ----
        image_paths = []
        if args.single_image:
            image_paths = [args.single_image]
        elif args.images:
            image_paths = collect_images(args.images)
        else:
            parser.error("Provide --images, --single-image, or --video")

        if not image_paths:
            print("Error: No images found", file=sys.stderr)
            sys.exit(1)

        print(f"\nFound {len(image_paths)} image(s):")
        for p in image_paths:
            print(f"  {p}")

        # Step 1: Upload to Cloudinary
        print("\n--- Step 1: Uploading to Cloudinary ---")
        upload_results = uploader.upload_carousel(image_paths)
        image_urls = [r["secure_url"] for r in upload_results]

        print(f"\nUploaded {len(image_urls)} images:")
        for url in image_urls:
            print(f"  {url}")

        if args.dry_run:
            print("\n--- DRY RUN: Skipping Instagram publish ---")
            print(json.dumps({"status": "dry_run", "image_urls": image_urls}))
            return

        # Step 2: Publish to Instagram
        print("\n--- Step 2: Publishing to Instagram ---")
        try:
            publisher = InstagramPublisher()
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            if len(image_urls) == 1:
                result = publisher.publish_single_image(image_urls[0], full_caption)
            else:
                result = publisher.publish_carousel(image_urls, full_caption)

            print(f"\nPublished successfully!")
            print(f"  Post ID: {result['post_id']}")

            # Cleanup
            if not args.no_cleanup:
                print("\n--- Step 3: Cleaning up Cloudinary ---")
                deleted = uploader.cleanup_uploads(upload_results)
                print(f"  Deleted {deleted}/{len(upload_results)} temporary images")

            print(f"\n{json.dumps(result)}")

        except InstagramPublishError as e:
            print(f"\nPublish failed: {e}", file=sys.stderr)
            error_str = str(e)
            if "Auth" in error_str or "190" in error_str:
                print("Fix: Token may have expired. Refresh or generate a new one.", file=sys.stderr)
            elif "Rate limit" in error_str:
                print("Fix: Rate limit hit. Wait 60s and retry.", file=sys.stderr)
            elif "EXPIRED" in error_str:
                print("Fix: Container expired. Re-run the script.", file=sys.stderr)

            print(f"\nCloudinary images preserved for retry:", file=sys.stderr)
            for url in image_urls:
                print(f"  {url}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
