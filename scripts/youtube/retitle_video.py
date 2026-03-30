"""
Retitle a YouTube video using the Data API v3 (videos.update).
Requires: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN in .env.local
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

VIDEO_ID = "1Wk4XUem2Ak"
NEW_TITLE = "Stop Saying \"You're Too Sensitive\" — Why It's Gaslighting"

def get_youtube_client():
    creds = Credentials(
        token=None,
        refresh_token=os.environ['YOUTUBE_REFRESH_TOKEN'],
        client_id=os.environ['YOUTUBE_CLIENT_ID'],
        client_secret=os.environ['YOUTUBE_CLIENT_SECRET'],
        token_uri='https://oauth2.googleapis.com/token',
    )
    return build('youtube', 'v3', credentials=creds)

def retitle_video(video_id: str, new_title: str):
    youtube = get_youtube_client()

    # First, fetch the existing snippet so we preserve all other fields
    print(f"Fetching current metadata for video {video_id}...")
    list_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    items = list_response.get('items', [])
    if not items:
        print(f"ERROR: Video {video_id} not found or not accessible.")
        sys.exit(1)

    snippet = items[0]['snippet']
    old_title = snippet.get('title', '')
    print(f"Current title : {old_title}")
    print(f"New title     : {new_title}")

    if len(new_title) > 100:
        print(f"ERROR: New title is {len(new_title)} chars — exceeds 100-char YouTube limit.")
        sys.exit(1)

    # Patch only the title; preserve categoryId, description, tags, defaultLanguage
    snippet['title'] = new_title

    print("\nSending videos.update request...")
    update_response = youtube.videos().update(
        part='snippet',
        body={
            'id': video_id,
            'snippet': snippet,
        }
    ).execute()

    updated_title = update_response['snippet']['title']
    print(f"\nSUCCESS — Title updated to: {updated_title}")
    print(f"Video URL: https://www.youtube.com/watch?v={video_id}")
    return update_response

if __name__ == '__main__':
    try:
        retitle_video(VIDEO_ID, NEW_TITLE)
    except HttpError as e:
        error_detail = json.loads(e.content.decode())
        print(f"YouTube API error {e.resp.status}: {json.dumps(error_detail, indent=2)}")
        sys.exit(1)
