#!/usr/bin/env python3
"""
ToxShield YouTube OAuth 2.0 setup — one-time browser consent flow.

Creates a refresh token for the YouTube Data API v3 and saves credentials
to .env.local for use by publish_shorts.py.

Prerequisites:
    1. Go to https://console.cloud.google.com
    2. Create or select a project
    3. Enable "YouTube Data API v3" in APIs & Services
    4. Go to Credentials > Create Credentials > OAuth 2.0 Client ID
    5. Application type: "Desktop app"
    6. Download the JSON file

Usage:
    python scripts/youtube/auth_setup.py --client-secrets ~/Downloads/client_secret.json
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_LOCAL_PATH = PROJECT_ROOT / ".env.local"

SCOPE_PRESETS = {
    "upload": ["https://www.googleapis.com/auth/youtube.upload"],
    "analytics": [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
    ],
    "all": [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
    ],
}

SCOPES = SCOPE_PRESETS["all"]


def load_client_secrets(path: str) -> dict:
    """Load and validate client secrets JSON file."""
    secrets_path = Path(path)
    if not secrets_path.exists():
        logger.error(f"Client secrets file not found: {path}")
        sys.exit(1)

    with open(secrets_path) as f:
        data = json.load(f)

    # Google exports secrets under "installed" or "web" key
    if "installed" in data:
        config = data["installed"]
    elif "web" in data:
        config = data["web"]
    else:
        logger.error("Invalid client secrets file. Expected 'installed' or 'web' key.")
        sys.exit(1)

    required = ["client_id", "client_secret"]
    for key in required:
        if key not in config:
            logger.error(f"Missing '{key}' in client secrets file")
            sys.exit(1)

    return config


def run_consent_flow(client_secrets_path: str):
    """Run the OAuth 2.0 consent flow and return credentials."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        logger.error(
            "google-auth-oauthlib not installed. Run:\n"
            "  pip install -r scripts/youtube/requirements.txt"
        )
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)

    logger.info("Opening browser for Google consent...")
    logger.info("(If the browser doesn't open, check the URL printed below)")

    credentials = flow.run_local_server(
        port=8090,
        prompt="consent",
        access_type="offline",
    )

    if not credentials.refresh_token:
        logger.error(
            "No refresh token received. This can happen if you've already "
            "authorized this app. Revoke access at https://myaccount.google.com/permissions "
            "and try again."
        )
        sys.exit(1)

    return credentials


def verify_credentials(credentials):
    """Verify credentials by fetching the authenticated channel.

    Returns (channel_name, channel_id) or (None, None) if verification
    fails due to insufficient scopes (upload-only scope can't list channels).
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError:
        logger.warning("google-api-python-client not available for verification")
        return None, None

    try:
        youtube = build("youtube", "v3", credentials=credentials)
        response = youtube.channels().list(part="snippet", mine=True).execute()

        items = response.get("items", [])
        if not items:
            logger.warning("No YouTube channel found — credentials saved anyway")
            return None, None

        channel = items[0]
        channel_name = channel["snippet"]["title"]
        channel_id = channel["id"]

        logger.info(f"Authenticated channel: {channel_name} ({channel_id})")
        return channel_name, channel_id
    except HttpError as e:
        # youtube.upload scope is not enough to call channels.list
        # This is fine — credentials are still valid for uploading
        logger.warning(f"Channel verification skipped (upload-only scope): {e.resp.status}")
        return None, None


def save_to_env_local(client_id: str, client_secret: str, refresh_token: str):
    """Save YouTube credentials to .env.local."""
    youtube_vars = {
        "YOUTUBE_CLIENT_ID": client_id,
        "YOUTUBE_CLIENT_SECRET": client_secret,
        "YOUTUBE_REFRESH_TOKEN": refresh_token,
    }

    if ENV_LOCAL_PATH.exists():
        content = ENV_LOCAL_PATH.read_text()
    else:
        content = ""

    for key, value in youtube_vars.items():
        pattern = re.compile(rf"^#?\s*{key}=.*$", re.MULTILINE)
        new_line = f"{key}={value}"

        if pattern.search(content):
            content = pattern.sub(new_line, content)
        else:
            if content and not content.endswith("\n"):
                content += "\n"
            if key == "YOUTUBE_CLIENT_ID" and "YOUTUBE" not in content:
                content += "\n# YouTube Shorts publishing\n"
            content += new_line + "\n"

    ENV_LOCAL_PATH.write_text(content)
    logger.info(f"Saved credentials to {ENV_LOCAL_PATH}")


def main():
    global SCOPES
    parser = argparse.ArgumentParser(
        description="Set up YouTube OAuth 2.0 for ToxShield (publishing + analytics)"
    )
    parser.add_argument(
        "--client-secrets", "-c", required=True,
        help="Path to client_secret.json from Google Cloud Console",
    )
    parser.add_argument(
        "--scopes", choices=["all", "upload", "analytics"], default="all",
        help="Scope preset: all (default), upload (Shorts only), analytics (read-only)",
    )
    args = parser.parse_args()

    SCOPES = SCOPE_PRESETS[args.scopes]
    logger.info(f"Using scope preset: {args.scopes} ({len(SCOPES)} scopes)")

    # Step 1: Load and validate client secrets
    config = load_client_secrets(args.client_secrets)
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    logger.info(f"Loaded client secrets (client_id: {client_id[:20]}...)")

    # Step 2: Run OAuth consent flow
    credentials = run_consent_flow(args.client_secrets)

    # Step 3: Verify by fetching channel info
    channel_name, channel_id = verify_credentials(credentials)

    # Step 4: Save to .env.local
    save_to_env_local(client_id, client_secret, credentials.refresh_token)

    print(f"\nYouTube auth configured successfully!")
    if channel_name:
        print(f"  Channel: {channel_name}")
        print(f"  Channel ID: {channel_id}")
    else:
        print(f"  Channel verification skipped (upload-only scope — this is normal)")
    print(f"  Credentials saved to: {ENV_LOCAL_PATH}")
    print(f"\nYou can now publish Shorts with:")
    print(f"  python scripts/youtube/publish_shorts.py --video <path> --title <title>")


if __name__ == "__main__":
    main()
