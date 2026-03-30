"""
update_shorts_metadata.py — Updates titles and descriptions for 6 ToxShield Shorts.

Uses YouTube Data API v3 videos.update with the snippet part.
Credentials loaded from .env.local (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN).
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------------------------------------------------------------------------
# 1. Load credentials
# ---------------------------------------------------------------------------

load_dotenv("/Users/biswa/toxshield/.env.local")
load_dotenv("/Users/biswa/toxshield/.env")

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("ERROR: Missing YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, or YOUTUBE_REFRESH_TOKEN in .env.local")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Exchange refresh token for an access token
# ---------------------------------------------------------------------------

def get_access_token() -> str:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"ERROR: Token refresh failed — {resp.status_code} {resp.text}")
        sys.exit(1)
    token = resp.json().get("access_token")
    if not token:
        print(f"ERROR: No access_token in response — {resp.text}")
        sys.exit(1)
    print("OK   Access token refreshed successfully\n")
    return token


# ---------------------------------------------------------------------------
# 3. Video metadata — titles, descriptions, and hashtags from optimized_shorts_v2.md
# ---------------------------------------------------------------------------

SHORTS_UPDATES = [
    {
        "video_id": "4-ocLAQg5s8",
        "title": '"You\'re Too Sensitive" — That\'s Gaslighting',
        "description": (
            '"You\'re too sensitive" is not feedback — it\'s a silencing tactic designed to make you doubt your own reactions.\n'
            'ToxShield forensic analysis: this phrase alone adds +2.4 to the toxicity score. Analyze your situation at toxshield.in.\n'
            '\n'
            'Try ToxShield — analyze the toxic people in your life: https://toxshield.in/\n'
            '\n'
            'Follow ToxShield:\n'
            'Instagram: https://instagram.com/toxshield.ai\n'
            'YouTube: https://youtube.com/channel/UCsC8iYzCqGhJwqkZ_FlG3pg\n'
            '\n'
            'Gaslighting is a control strategy that works by making you question your own perception and reactions. '
            'When someone tells you "you\'re too sensitive," they are not giving you feedback — they are shifting the focus '
            'from their behavior to your response. ToxShield\'s forensic behavioral analysis identifies this as a core '
            'gaslighting pattern that adds +2.4 points to the toxicity index.\n'
            '\n'
            '#Shorts #ToxShield #Gaslighting #ToxicRelationships #RedFlags\n'
            '\n'
            'ToxShield identifies behavioral patterns. Not a substitute for professional counseling. '
            'If you are in danger, contact emergency services.'
        ),
    },
    {
        "video_id": "1Wk4XUem2Ak",
        "title": '"That Never Happened" — The #1 Gaslighting Phrase',
        "description": (
            '"That never happened" forces you to choose between your memory and the relationship — that is the goal.\n'
            'ToxShield forensic pattern: reality reconstruction. Run your own behavioral analysis at toxshield.in.\n'
            '\n'
            'Try ToxShield — analyze the toxic people in your life: https://toxshield.in/\n'
            '\n'
            'Follow ToxShield:\n'
            'Instagram: https://instagram.com/toxshield.ai\n'
            'YouTube: https://youtube.com/channel/UCsC8iYzCqGhJwqkZ_FlG3pg\n'
            '\n'
            'Memory denial is not a memory issue — it is a control strategy. When someone denies events you both '
            'experienced, they force you to choose between trusting your own memory and preserving the relationship. '
            'ToxShield classifies this as reality reconstruction, the gold standard of gaslighting and one of the '
            'most severe behavioral patterns in the toxicity index.\n'
            '\n'
            '#Shorts #ToxShield #GaslightingAwareness #NarcissisticAbuse #ToxicRelationships\n'
            '\n'
            'ToxShield identifies behavioral patterns. Not a substitute for professional counseling. '
            'If you are in danger, contact emergency services.'
        ),
    },
    {
        "video_id": "UJOQf_7rAXY",
        "title": '"You\'re the Problem Here" — That\'s DARVO',
        "description": (
            'You raised a concern and left the conversation as the problem. That pattern has a name: DARVO.\n'
            'ToxShield forensic analysis: Deny, Attack, Reverse Victim and Offender — detected in 1 in 3 high-score profiles.\n'
            '\n'
            'Try ToxShield — analyze the toxic people in your life: https://toxshield.in/\n'
            '\n'
            'Follow ToxShield:\n'
            'Instagram: https://instagram.com/toxshield.ai\n'
            'YouTube: https://youtube.com/channel/UCsC8iYzCqGhJwqkZ_FlG3pg\n'
            '\n'
            'DARVO — Deny, Attack, Reverse Victim and Offender — is a learned defense mechanism that prevents '
            'accountability by converting your valid concern into evidence of your own wrongdoing. You enter the '
            'conversation with a concern and leave defending yourself. ToxShield detects this pattern in 1 in 3 '
            'high-score profiles. It is not accidental — it is a strategy.\n'
            '\n'
            '#Shorts #ToxShield #DARVO #ManipulationTactics #GaslightingAwareness\n'
            '\n'
            'ToxShield identifies behavioral patterns. Not a substitute for professional counseling. '
            'If you are in danger, contact emergency services.'
        ),
    },
    {
        "video_id": "RXEEfCa5D-Q",
        "title": '"He\'s Just Stressed" — 500 Scores Say Otherwise',
        "description": (
            'ToxShield analyzed 500 relationships where "he\'s just stressed" was the explanation. 67% scored 6+ toxic.\n'
            'Stress was never the variable. The pattern was. Run your own behavioral analysis at toxshield.in.\n'
            '\n'
            'Try ToxShield — analyze the toxic people in your life: https://toxshield.in/\n'
            '\n'
            'Follow ToxShield:\n'
            'Instagram: https://instagram.com/toxshield.ai\n'
            'YouTube: https://youtube.com/channel/UCsC8iYzCqGhJwqkZ_FlG3pg\n'
            '\n'
            'Across 500 relationships where "he\'s just stressed" was the primary explanation for harmful behavior, '
            '67% scored 6 or higher on the ToxShield toxicity index and 1 in 5 hit a score of 9/10. The most common '
            'pattern across all 500 relationships: DARVO — every single time. Stress was never the variable. '
            'The relationship dynamic was.\n'
            '\n'
            '#Shorts #ToxShield #ToxicityScore #ForensicBehavioralAnalysis #ToxicRelationships\n'
            '\n'
            'ToxShield identifies behavioral patterns. Not a substitute for professional counseling. '
            'If you are in danger, contact emergency services.'
        ),
    },
    {
        "video_id": "iXY7T8Q3Lt4",
        "title": '"After Everything I\'ve Done for You" — DARVO',
        "description": (
            '"After everything I\'ve done for you" — said when you tried to hold them accountable. That\'s DARVO Step 3: Reverse.\n'
            'ToxShield forensic pattern: role inversion — a top-5 pattern in every high-score profile. Analyze at toxshield.in.\n'
            '\n'
            'Try ToxShield — analyze the toxic people in your life: https://toxshield.in/\n'
            '\n'
            'Follow ToxShield:\n'
            'Instagram: https://instagram.com/toxshield.ai\n'
            'YouTube: https://youtube.com/channel/UCsC8iYzCqGhJwqkZ_FlG3pg\n'
            '\n'
            'This is the Reverse phase of DARVO: Deny, Attack, Reverse Victim and Offender. In Step 3, '
            'your valid concern is converted into evidence of your ingratitude. Their history of generosity '
            'becomes your debt for daring to raise a question. ToxShield classifies this as role inversion — '
            'a top-5 pattern in every high-scoring profile. You left the conversation guilty for asking a question. '
            'That is DARVO.\n'
            '\n'
            '#Shorts #ToxShield #DARVO #NarcissisticAbuse #ManipulationTactics\n'
            '\n'
            'ToxShield identifies behavioral patterns. Not a substitute for professional counseling. '
            'If you are in danger, contact emergency services.'
        ),
    },
    {
        "video_id": "Zcu4_Tl45iA",
        "title": '"Why Are You So Boring Now?" — The Grey Rock Method',
        "description": (
            'When a manipulator calls you "boring," that is the grey rock method working exactly as intended.\n'
            'No reaction = no fuel. ToxShield protection strategy breakdown. Try it at toxshield.in.\n'
            '\n'
            'Try ToxShield — analyze the toxic people in your life: https://toxshield.in/\n'
            '\n'
            'Follow ToxShield:\n'
            'Instagram: https://instagram.com/toxshield.ai\n'
            'YouTube: https://youtube.com/channel/UCsC8iYzCqGhJwqkZ_FlG3pg\n'
            '\n'
            'Manipulators feed on emotional reactions — the arguments, the tears, the highs and lows. '
            'The grey rock method removes that fuel entirely. You respond with yes, no, fine — as dull and '
            'unremarkable as a grey rock. When they call you boring, that is confirmation the strategy is working. '
            'ToxShield protection strategy rating: highly effective for disrupting DARVO and emotional manipulation patterns.\n'
            '\n'
            '#Shorts #ToxShield #GreyRockMethod #ProtectionStrategy #ManipulationTactics\n'
            '\n'
            'ToxShield identifies behavioral patterns. Not a substitute for professional counseling. '
            'If you are in danger, contact emergency services.'
        ),
    },
]


# ---------------------------------------------------------------------------
# 4. Update function
# ---------------------------------------------------------------------------

def build_youtube_client(access_token: str):
    """Build a YouTube API client using a pre-obtained access token."""
    from google.oauth2.credentials import Credentials
    credentials = Credentials(token=access_token)
    return build("youtube", "v3", credentials=credentials)


def update_video(youtube, video_id: str, new_title: str, new_description: str) -> dict:
    """
    Fetch the current snippet for video_id (to preserve categoryId, tags, etc.),
    then update title and description via videos.update.
    """
    # Fetch current snippet
    list_response = youtube.videos().list(
        part="snippet",
        id=video_id,
    ).execute()

    items = list_response.get("items", [])
    if not items:
        return {"success": False, "error": f"Video {video_id} not found or not accessible"}

    snippet = items[0]["snippet"]

    # Enforce YouTube title limit
    if len(new_title) > 100:
        new_title = new_title[:97] + "..."

    # Apply updates — preserve everything else in snippet
    snippet["title"] = new_title
    snippet["description"] = new_description

    update_response = youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": snippet,
        },
    ).execute()

    updated_title = update_response.get("snippet", {}).get("title", "")
    updated_desc_preview = update_response.get("snippet", {}).get("description", "")[:80]

    return {
        "success": True,
        "video_id": video_id,
        "updated_title": updated_title,
        "description_preview": updated_desc_preview,
        "url": f"https://www.youtube.com/shorts/{video_id}",
    }


# ---------------------------------------------------------------------------
# 5. Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("ToxShield — YouTube Shorts Metadata Updater")
    print("Phase 4: Publishing (metadata update for 6 existing Shorts)")
    print("=" * 70)
    print()

    # Get access token
    print("Refreshing access token...")
    access_token = get_access_token()

    # Build API client
    youtube = build_youtube_client(access_token)

    # Process each video
    results = []
    for i, video in enumerate(SHORTS_UPDATES, start=1):
        vid_id = video["video_id"]
        new_title = video["title"]
        new_desc = video["description"]

        print(f"[{i}/6] Updating {vid_id}")
        print(f"      Title: {new_title}")

        try:
            result = update_video(youtube, vid_id, new_title, new_desc)
            if result["success"]:
                print(f"      OK   Updated — {result['url']}")
                print(f"      Confirmed title: {result['updated_title']}")
            else:
                print(f"      FAIL {result['error']}")
            results.append(result)
        except HttpError as e:
            error_msg = f"HttpError {e.status_code}: {e.error_details}"
            print(f"      FAIL {error_msg}")
            results.append({"success": False, "video_id": vid_id, "error": error_msg})
        except Exception as e:
            print(f"      FAIL Unexpected error: {e}")
            results.append({"success": False, "video_id": vid_id, "error": str(e)})

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    successes = [r for r in results if r.get("success")]
    failures = [r for r in results if not r.get("success")]

    print(f"Updated successfully: {len(successes)}/6")
    if failures:
        print(f"Failed:              {len(failures)}/6")
        for f in failures:
            print(f"  - {f['video_id']}: {f['error']}")

    print()
    if successes:
        print("Updated videos:")
        for r in successes:
            print(f"  {r['video_id']} — {r['url']}")
            print(f"    Title: {r['updated_title']}")

    print()
    print("Phase 5 recommendations:")
    print("  - Upload thumbnail A/B variants via YouTube Studio for each video")
    print("  - Monitor CTR at 48h; switch to variant B if CTR < 8%")
    print("  - Cross-post all 6 Shorts to Instagram Reels via instagram-content-orchestrator")
    print("  - Check updated videos in YouTube Studio: https://studio.youtube.com/")
    print()
    print("YPP tracking:")
    print("  Run: python3 /Users/biswa/toxshield/scripts/youtube/analyze_channel.py --quick")


if __name__ == "__main__":
    main()
