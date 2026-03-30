"""
Set the YouTube channel description using the Data API v3 (channels.update).
Requires: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN,
          YOUTUBE_CHANNEL_ID in .env.local
"""
import os
import sys
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv('/Users/biswa/toxshield/.env.local')
load_dotenv('/Users/biswa/toxshield/.env')

CHANNEL_DESCRIPTION = """\
ToxShield — AI-powered forensic behavioral analyzer.

We analyze toxic relationship patterns, score them 0–10, and give you the exact protection strategies to protect yourself.

Topics: toxic relationships, gaslighting, narcissism, DARVO, love bombing, coercive control, trauma bonding, behavioral analysis.

New videos every Mon–Sat. Subscribe to see the truth clearly.

Try ToxShield: https://toxshield.in/"""

def get_youtube_client():
    creds = Credentials(
        token=None,
        refresh_token=os.environ['YOUTUBE_REFRESH_TOKEN'],
        client_id=os.environ['YOUTUBE_CLIENT_ID'],
        client_secret=os.environ['YOUTUBE_CLIENT_SECRET'],
        token_uri='https://oauth2.googleapis.com/token',
    )
    return build('youtube', 'v3', credentials=creds)

def set_channel_description(description: str):
    youtube = get_youtube_client()
    channel_id = os.environ['YOUTUBE_CHANNEL_ID']

    # Fetch current channel snippet to show the existing description
    print(f"Fetching current channel metadata for {channel_id}...")
    list_response = youtube.channels().list(
        part='snippet',
        id=channel_id
    ).execute()

    items = list_response.get('items', [])
    if not items:
        print(f"ERROR: Channel {channel_id} not found or not accessible.")
        sys.exit(1)

    old_description = items[0]['snippet'].get('description', '')
    print(f"Current description: {'(empty)' if not old_description.strip() else repr(old_description[:80]) + '...'}")
    print(f"New description (first line): {description.splitlines()[0]}")

    # channels.update via 'snippet' part rejects read-only fields with ERROR_PART_UNEXPECTED.
    # The reliable cross-account approach is to use the 'brandingSettings' part,
    # which only requires brandingSettings.channel.description to be set.
    print("\nSending channels.update request (brandingSettings)...")
    update_response = youtube.channels().update(
        part='brandingSettings',
        body={
            'id': channel_id,
            'brandingSettings': {
                'channel': {
                    'description': description,
                }
            }
        }
    ).execute()

    updated_desc = update_response['brandingSettings']['channel']['description']
    print(f"\nSUCCESS — Channel description updated.")
    print(f"First line: {updated_desc.splitlines()[0]}")
    print(f"Full description:\n{updated_desc}")
    return update_response

if __name__ == '__main__':
    try:
        set_channel_description(CHANNEL_DESCRIPTION)
    except HttpError as e:
        error_detail = json.loads(e.content.decode())
        print(f"YouTube API error {e.resp.status}: {json.dumps(error_detail, indent=2)}")
        sys.exit(1)
