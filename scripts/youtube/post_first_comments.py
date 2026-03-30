#!/usr/bin/env python3
"""
Post creator first-comments on ToxShield YouTube videos.

Matches videos by title keywords and posts pre-written relatable comments.
"""

import json
import os
import sys
import time
import requests

# ── Credentials (from environment variables) ─────────────────────────────────
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UCsC8iYzCqGhJwqkZ_FlG3pg")

# ── Comment map: keyword list → comment ─────────────────────────────────────
# Each entry: (search_keywords, comment_text)
# Keywords are checked case-insensitively against the video title.
# The FIRST matching rule wins.
COMMENT_MAP = [
    (
        ["empath", "ex said"],
        "I made this and then remembered every time he cried at a commercial but never noticed when I was crying. Drop a 🚩 if your ex's 'empathy' only activated when they needed something",
    ),
    (
        ["future fake", "future faker"],
        "Future fakers are built different — they can cry at the wedding venue they already plan to ghost you from. What's the most elaborate future they sold you?",
    ),
    (
        ["idealize", "devalue", "discard"],
        "Once you learn the cycle you can PREDICT when the devalue hits and you still stay. Like knowing the jump scare is coming and still screaming. Drop a 🚩 if you've been through this loop more than once",
    ),
    (
        ["trauma bond"],
        "You're not in love with them — you're in love with who they were on a random Tuesday in month two. That person was never real. Which sign hit hardest?",
    ),
    (
        ["gaslight", "gaslighted", "5 signs"],
        "I made this and my brain went 'wait, I've said maybe you're right to someone who was definitely not right'. Drop a 🚩 if #3 made your stomach drop",
    ),
    (
        ["love bomb"],
        "8.7/10 and he still had her blocked by the time this uploaded. Love bombing speedrun any%. What's the fastest someone went from 'soulmate' to stranger?",
    ),
    (
        ["darvo", "9.1"],
        "9.1/10 and somehow YOU were the one apologizing after every fight. Drop a 🚩 if you ever apologized for bringing up something completely valid",
    ),
    (
        ["after everything", "everything i've done", "everything i have done"],
        "'After everything I've done for you' is the DARVO starter pack. What triggered yours? Mine was literally just asking why they were late",
    ),
    (
        ["grey rock", "gray rock"],
        "Grey rock is just playing dead until the bear leaves. And when they call you boring, you KNOW it's working. Drop a 🚩 if grey rock changed your life",
    ),
    (
        ["just stressed", "he's just", "hes just"],
        "500 relationships. 67% scored 6+. 'He's just stressed' is one of the most load-bearing sentences in the English language. How many years did you carry that excuse? toxshield.in has the receipts",
    ),
    (
        ["you're the problem", "youre the problem"],
        "The pipeline from 'I need to talk about something' to 'I'm sorry for bringing it up' is a 3-minute speedrun with some people. Sound familiar?",
    ),
    (
        ["that never happened", "never happened"],
        "'That never happened' is wild because you WERE there. And somehow they say it with such confidence you start Googling early memory loss. What's the most specific thing someone insisted never happened?",
    ),
    (
        ["too sensitive", "you're too sensitive", "youre too sensitive"],
        "'You're too sensitive' said by the person who caused the thing you're sensitive about. The audacity is genuinely a skill set. Drop a 🚩 if you spent years believing you were the problem",
    ),
]


def refresh_access_token() -> str:
    """Exchange the refresh token for a fresh access token."""
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError(f"No access_token in response: {resp.text}")
    print(f"[auth] Access token obtained (expires in {resp.json().get('expires_in')}s)")
    return token


def list_channel_videos(access_token: str) -> list[dict]:
    """Return all public videos on the channel (id + title)."""
    videos = []
    page_token = None
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 1: get uploads playlist ID
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "contentDetails", "id": CHANNEL_ID},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    if not items:
        raise RuntimeError("Channel not found or no items returned")

    uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    print(f"[list] Uploads playlist: {uploads_playlist}")

    # Step 2: page through playlistItems
    while True:
        params = {
            "part": "snippet",
            "playlistId": uploads_playlist,
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token

        r = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params,
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()

        for item in data.get("items", []):
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            title = snippet["title"]
            videos.append({"id": video_id, "title": title})

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    print(f"[list] Found {len(videos)} videos")
    return videos


def match_comment(title: str) -> str | None:
    """Return the pre-written comment for a video title, or None if no match."""
    lower = title.lower()
    for keywords, comment in COMMENT_MAP:
        if any(kw in lower for kw in keywords):
            return comment
    return None


def post_comment(access_token: str, video_id: str, text: str) -> dict:
    """Post a top-level comment on a video. Returns the API response."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": text,
                }
            },
        }
    }
    r = requests.post(
        "https://www.googleapis.com/youtube/v3/commentThreads",
        params={"part": "snippet"},
        headers=headers,
        json=body,
        timeout=30,
    )
    return r


def main():
    print("=" * 60)
    print("ToxShield — Creator First-Comment Poster")
    print("=" * 60)

    # Authenticate
    try:
        access_token = refresh_access_token()
    except Exception as e:
        print(f"[FATAL] Auth failed: {e}")
        sys.exit(1)

    # List videos
    try:
        videos = list_channel_videos(access_token)
    except Exception as e:
        print(f"[FATAL] Could not list videos: {e}")
        sys.exit(1)

    if not videos:
        print("[INFO] No videos found on channel.")
        sys.exit(0)

    print("\nVideos found:")
    for v in videos:
        print(f"  [{v['id']}] {v['title']}")

    print("\n" + "=" * 60)
    print("Posting comments...")
    print("=" * 60)

    results = {"posted": [], "skipped": [], "failed": []}

    for v in videos:
        video_id = v["id"]
        title = v["title"]
        comment = match_comment(title)

        if comment is None:
            print(f"\n[SKIP] No comment mapped for: \"{title}\"")
            results["skipped"].append({"id": video_id, "title": title})
            continue

        print(f"\n[POST] \"{title}\" ({video_id})")
        print(f"       Comment: {comment[:80]}...")

        try:
            resp = post_comment(access_token, video_id, comment)

            if resp.status_code == 200:
                resp_data = resp.json()
                comment_id = resp_data.get("id", "unknown")
                print(f"       [OK] Comment ID: {comment_id}")
                results["posted"].append({
                    "id": video_id,
                    "title": title,
                    "comment_id": comment_id,
                    "comment_preview": comment[:60] + "...",
                })
            else:
                error_info = resp.json()
                error_msg = error_info.get("error", {}).get("message", resp.text)
                error_code = error_info.get("error", {}).get("code", resp.status_code)
                print(f"       [FAIL] HTTP {resp.status_code} — {error_msg}")
                results["failed"].append({
                    "id": video_id,
                    "title": title,
                    "error": f"HTTP {error_code}: {error_msg}",
                })

        except Exception as e:
            print(f"       [FAIL] Exception: {e}")
            results["failed"].append({"id": video_id, "title": title, "error": str(e)})

        # Be polite to the API — 1 second between requests
        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Posted:  {len(results['posted'])}")
    print(f"  Skipped: {len(results['skipped'])} (no comment mapped)")
    print(f"  Failed:  {len(results['failed'])}")

    if results["posted"]:
        print("\nSuccessfully posted:")
        for r in results["posted"]:
            print(f"  - \"{r['title']}\" -> comment {r['comment_id']}")

    if results["skipped"]:
        print("\nSkipped (no match):")
        for r in results["skipped"]:
            print(f"  - \"{r['title']}\" ({r['id']})")

    if results["failed"]:
        print("\nFailed:")
        for r in results["failed"]:
            print(f"  - \"{r['title']}\": {r['error']}")

    # Save results to file
    out_path = "/Users/biswa/toxshield/output/youtube/first_comments_results.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    if results["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
