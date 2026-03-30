#!/usr/bin/env python3
"""
ToxShield Instagram account analytics and strategy report generator.

Standalone CLI script that fetches recent posts, analyzes engagement patterns,
and generates an HTML strategy report with ToxShield's monochrome dark theme.

Usage:
    python scripts/instagram/analyze_account.py
    python scripts/instagram/analyze_account.py --output report.html
    python scripts/instagram/analyze_account.py --last-n-posts 50 --json
"""

import argparse
import json
import logging
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

PROJECT_ROOT = Path(__file__).parent.parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.local")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # Env vars must be set in the shell if python-dotenv is not installed

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ===========================================================================
# Instagram API Client (standalone, no service imports)
# ===========================================================================

class InstagramAPIError(Exception):
    pass

class InstagramRateLimitError(InstagramAPIError):
    pass

class InstagramAuthError(InstagramAPIError):
    pass


class InstagramAPIClient:
    """Client for Instagram Graph API — read-only operations."""

    BASE_URL = "https://graph.instagram.com"
    MAX_RETRIES = 3

    def __init__(self, access_token: str):
        self.access_token = access_token

    def fetch_user_media(
        self, user_id: str, limit: int = 100, max_posts: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        all_posts = []
        fields = "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url,like_count"
        url = f"{self.BASE_URL}/{user_id}/media"
        params = {"fields": fields, "access_token": self.access_token, "limit": limit}

        while url:
            logger.info(f"Fetching posts... (current: {len(all_posts)})")
            data = self._make_request(url, params)
            media_items = data.get("data", [])

            for item in media_items:
                if item.get("media_type") == "CAROUSEL_ALBUM":
                    children = self._fetch_carousel_children(item["id"])
                    item["children"] = children

            all_posts.extend(media_items)

            if max_posts and len(all_posts) >= max_posts:
                all_posts = all_posts[:max_posts]
                break

            url = data.get("paging", {}).get("next")
            params = {}

        logger.info(f"Fetched {len(all_posts)} posts")
        return all_posts

    def _fetch_carousel_children(self, media_id: str) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{media_id}/children"
        params = {
            "fields": "id,media_type,media_url,thumbnail_url",
            "access_token": self.access_token,
        }
        try:
            data = self._make_request(url, params)
            return data.get("data", [])
        except Exception as e:
            logger.warning(f"Failed to fetch carousel children for {media_id}: {e}")
            return []

    def refresh_access_token(self, current_token: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/refresh_access_token"
        params = {"grant_type": "ig_refresh_token", "access_token": current_token}
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise InstagramAPIError(f"Token refresh failed: {data['error'].get('message')}")
            logger.info("Token refreshed successfully")
            return data
        except requests.RequestException as e:
            raise InstagramAPIError(f"Token refresh failed: {e}")

    def _make_request(self, url: str, params: Dict[str, Any], attempt: int = 0) -> Dict[str, Any]:
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                return self._handle_api_error(data["error"], url, params, attempt)
            return data

        except requests.Timeout:
            if attempt < self.MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning(f"Timeout, retrying in {wait}s ({attempt + 1}/{self.MAX_RETRIES})")
                time.sleep(wait)
                return self._make_request(url, params, attempt + 1)
            raise InstagramAPIError(f"Timeout after {self.MAX_RETRIES} attempts")

        except requests.RequestException as e:
            if attempt < self.MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning(f"Request failed: {e}, retrying in {wait}s")
                time.sleep(wait)
                return self._make_request(url, params, attempt + 1)
            raise InstagramAPIError(f"Request failed: {e}")

    def _handle_api_error(
        self, error: Dict, url: str, params: Dict, attempt: int,
    ) -> Dict[str, Any]:
        error_code = error.get("code")
        error_msg = error.get("message", "Unknown error")

        logger.error(f"API error: code={error_code}, message={error_msg}")

        if error_code in [4, 17, 32, 613]:
            if attempt < self.MAX_RETRIES - 1:
                wait = (2 ** attempt) * 60
                logger.warning(f"Rate limit, waiting {wait}s")
                time.sleep(wait)
                return self._make_request(url, params, attempt + 1)
            raise InstagramRateLimitError(f"Rate limit: {error_msg}")

        if error_code in [190, 200]:
            raise InstagramAuthError(f"Auth error: {error_msg}")

        raise InstagramAPIError(f"API error {error_code}: {error_msg}")


# ===========================================================================
# Analytics
# ===========================================================================

def analyze_posts(posts: list) -> dict:
    """Analyze post data for patterns and insights."""
    if not posts:
        return {"error": "No posts found"}

    total = len(posts)
    media_types = Counter()
    likes = []
    post_times = []
    weekday_engagement = defaultdict(list)
    hour_engagement = defaultdict(list)
    hashtag_counts = Counter()
    caption_lengths = []

    for post in posts:
        media_types[post.get("media_type", "UNKNOWN")] += 1
        like_count = post.get("like_count", 0)
        likes.append(like_count)

        ts = post.get("timestamp", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                post_times.append(dt)
                weekday_engagement[dt.strftime("%A")].append(like_count)
                hour_engagement[dt.hour].append(like_count)
            except (ValueError, TypeError):
                pass

        caption = post.get("caption", "")
        if caption:
            caption_lengths.append(len(caption))
            for word in caption.split():
                if word.startswith("#"):
                    hashtag_counts[word.lower()] += 1

    avg_likes = sum(likes) / len(likes) if likes else 0
    max_likes = max(likes) if likes else 0
    min_likes = min(likes) if likes else 0

    best_days = {}
    for day, day_likes in weekday_engagement.items():
        best_days[day] = sum(day_likes) / len(day_likes)
    best_days = dict(sorted(best_days.items(), key=lambda x: x[1], reverse=True))

    best_hours = {}
    for hour, hour_likes in hour_engagement.items():
        best_hours[f"{hour:02d}:00"] = sum(hour_likes) / len(hour_likes)
    best_hours = dict(sorted(best_hours.items(), key=lambda x: x[1], reverse=True))

    top_hashtags = hashtag_counts.most_common(15)

    if len(post_times) >= 2:
        date_range = (max(post_times) - min(post_times)).days
        posts_per_week = total / max(date_range / 7, 1)
    else:
        posts_per_week = 0
        date_range = 0

    top_posts = sorted(posts, key=lambda p: p.get("like_count", 0), reverse=True)[:5]

    return {
        "total_posts_analyzed": total,
        "date_range_days": date_range,
        "posts_per_week": round(posts_per_week, 1),
        "engagement": {
            "average_likes": round(avg_likes, 1),
            "max_likes": max_likes,
            "min_likes": min_likes,
            "total_likes": sum(likes),
        },
        "media_types": dict(media_types),
        "best_posting_days": {k: round(v, 1) for k, v in list(best_days.items())[:3]},
        "best_posting_hours": {k: round(v, 1) for k, v in list(best_hours.items())[:5]},
        "top_hashtags": top_hashtags,
        "caption_avg_length": round(sum(caption_lengths) / len(caption_lengths)) if caption_lengths else 0,
        "top_posts": [
            {
                "permalink": p.get("permalink", ""),
                "like_count": p.get("like_count", 0),
                "media_type": p.get("media_type", ""),
                "caption_preview": (p.get("caption", "")[:80] + "...") if p.get("caption") else "",
            }
            for p in top_posts
        ],
    }


# ===========================================================================
# HTML Report — ToxShield Monochrome Dark Theme
# ===========================================================================

def generate_html_report(analysis: dict, output_path: str) -> None:
    """Generate an HTML strategy report with ToxShield monochrome theme."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ToxShield Instagram Strategy Report</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #000;
    color: #fff;
    min-height: 100vh;
    padding: 40px 20px;
}}
.container {{ max-width: 900px; margin: 0 auto; }}
h1 {{
    font-family: 'JetBrains Mono', 'Menlo', monospace;
    font-size: 1.75rem;
    color: #fff;
    text-shadow: 0 0 10px #fff, 0 0 30px rgba(255,255,255,0.5);
    margin-bottom: 8px;
}}
h2 {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem;
    color: #fff;
    margin: 32px 0 16px;
    border-bottom: 1px solid #1a1a1a;
    padding-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.subtitle {{ color: #666; font-size: 0.9rem; margin-bottom: 32px; font-family: monospace; }}
.card {{
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 20px;
}}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }}
.stat {{
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}}
.stat .value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    text-shadow: 0 0 8px rgba(255,255,255,0.3);
}}
.stat .label {{ font-size: 0.8rem; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em; }}
.bar {{
    display: flex;
    align-items: center;
    margin: 8px 0;
}}
.bar .name {{ width: 120px; font-size: 0.85rem; color: #666; font-family: monospace; }}
.bar .fill {{
    height: 20px;
    background: #fff;
    border-radius: 2px;
    min-width: 4px;
    box-shadow: 0 0 8px rgba(255,255,255,0.15);
}}
.bar .val {{ margin-left: 8px; font-size: 0.8rem; color: #666; font-family: monospace; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ text-align: left; color: #666; font-size: 0.8rem; padding: 8px; border-bottom: 1px solid #1a1a1a; text-transform: uppercase; letter-spacing: 0.05em; }}
td {{ padding: 8px; font-size: 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.03); }}
.tag {{
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    padding: 4px 10px;
    margin: 3px;
    font-size: 0.75rem;
    font-family: monospace;
    color: #666;
}}
.footer {{
    text-align: center;
    color: #333;
    margin-top: 40px;
    font-size: 0.75rem;
    font-family: monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
</style>
</head>
<body>
<div class="container">
<h1>ToxShield // Instagram Strategy Report</h1>
<p class="subtitle">Generated {datetime.now().strftime('%Y-%m-%d')} // {analysis['total_posts_analyzed']} posts analyzed // {analysis['date_range_days']} days</p>

<h2>Overview</h2>
<div class="grid">
<div class="stat">
    <div class="value">{analysis['total_posts_analyzed']}</div>
    <div class="label">Posts Analyzed</div>
</div>
<div class="stat">
    <div class="value">{analysis['posts_per_week']}</div>
    <div class="label">Posts / Week</div>
</div>
<div class="stat">
    <div class="value">{analysis['engagement']['average_likes']}</div>
    <div class="label">Avg Likes</div>
</div>
<div class="stat">
    <div class="value">{analysis['engagement']['max_likes']}</div>
    <div class="label">Best Post</div>
</div>
</div>

<h2>Content Type Distribution</h2>
<div class="card">
{''.join(f'<div class="bar"><div class="name">{k}</div><div class="fill" style="width: {v/max(analysis["media_types"].values())*300}px"></div><div class="val">{v}</div></div>' for k, v in analysis['media_types'].items())}
</div>

<h2>Best Posting Days</h2>
<div class="card">
{''.join(f'<div class="bar"><div class="name">{day}</div><div class="fill" style="width: {avg/max(analysis["best_posting_days"].values())*300 if analysis["best_posting_days"] else 0}px"></div><div class="val">{avg} avg</div></div>' for day, avg in analysis['best_posting_days'].items())}
</div>

<h2>Best Posting Hours (UTC)</h2>
<div class="card">
{''.join(f'<div class="bar"><div class="name">{hour}</div><div class="fill" style="width: {avg/max(analysis["best_posting_hours"].values())*300 if analysis["best_posting_hours"] else 0}px"></div><div class="val">{avg} avg</div></div>' for hour, avg in list(analysis['best_posting_hours'].items())[:5])}
</div>

<h2>Top Hashtags</h2>
<div class="card">
{''.join(f'<span class="tag">{tag} ({count})</span>' for tag, count in analysis['top_hashtags'])}
</div>

<h2>Top Performing Posts</h2>
<div class="card">
<table>
<tr><th>Likes</th><th>Type</th><th>Caption</th></tr>
{''.join(f'<tr><td style="color:#fff;font-weight:700;font-family:monospace">{p["like_count"]}</td><td style="font-family:monospace;color:#666">{p["media_type"]}</td><td style="color:#666">{p["caption_preview"]}</td></tr>' for p in analysis['top_posts'])}
</table>
</div>

<h2>Recommendations</h2>
<div class="card">
<ul style="list-style:none;padding:0;color:#666">
<li style="margin:12px 0;border-left:2px solid #fff;padding-left:12px">{'Increase posting frequency to 7+/week' if analysis['posts_per_week'] < 7 else 'Posting frequency is solid. Maintain consistency.'}</li>
<li style="margin:12px 0;border-left:2px solid #fff;padding-left:12px">{'Use more CAROUSEL posts — they drive saves and shares' if analysis['media_types'].get('IMAGE', 0) > analysis['media_types'].get('CAROUSEL_ALBUM', 0) else 'Good carousel usage.'}</li>
<li style="margin:12px 0;border-left:2px solid #fff;padding-left:12px">Best days: {', '.join(list(analysis['best_posting_days'].keys())[:2]) or 'N/A'}</li>
<li style="margin:12px 0;border-left:2px solid #fff;padding-left:12px">Best hours: {', '.join(list(analysis['best_posting_hours'].keys())[:3]) or 'N/A'}</li>
<li style="margin:12px 0;border-left:2px solid #fff;padding-left:12px">Avg caption length: {analysis['caption_avg_length']} chars — {'write longer captions for SEO' if analysis['caption_avg_length'] < 200 else 'good length'}</li>
</ul>
</div>

<div class="footer">ToxShield // Instagram Strategy Report // Powered by Claude</div>
</div>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"Report saved to: {output_path}")


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze ToxShield Instagram account and generate strategy report"
    )
    parser.add_argument(
        "--last-n-posts", "-n", type=int, default=50,
        help="Number of recent posts to analyze (default: 50)",
    )
    parser.add_argument(
        "--output", "-o",
        default=str(PROJECT_ROOT / "output" / "instagram" / "strategy_report.html"),
        help="Output file path",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output analysis as JSON instead of HTML",
    )
    parser.add_argument(
        "--refresh-token", action="store_true",
        help="Refresh the Instagram access token before analyzing",
    )

    args = parser.parse_args()

    access_token = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN") or os.getenv("INSTAGRAM_ACCESS_TOKEN")
    user_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID") or os.getenv("INSTAGRAM_USER_ID")

    if not access_token or not user_id:
        print(
            "Error: Set INSTAGRAM_PAGE_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env.local",
            file=sys.stderr,
        )
        sys.exit(1)

    client = InstagramAPIClient(access_token)

    if args.refresh_token:
        print("Refreshing access token...")
        try:
            result = client.refresh_access_token(access_token)
            print(f"New token expires in {result.get('expires_in', 0) // 86400} days")
            print(f"Update INSTAGRAM_PAGE_ACCESS_TOKEN in .env.local with:")
            print(f"  {result['access_token'][:20]}...")
        except InstagramAPIError as e:
            print(f"Token refresh failed: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"Fetching last {args.last_n_posts} posts...")
    posts = client.fetch_user_media(user_id, max_posts=args.last_n_posts)
    print(f"Fetched {len(posts)} posts")

    print("Analyzing engagement patterns...")
    analysis = analyze_posts(posts)

    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        generate_html_report(analysis, args.output)
        print(f"\nKey Metrics:")
        print(f"  Posts/week: {analysis['posts_per_week']}")
        print(f"  Avg likes: {analysis['engagement']['average_likes']}")
        print(f"  Best post: {analysis['engagement']['max_likes']} likes")
        print(f"  Top days: {', '.join(list(analysis['best_posting_days'].keys())[:2]) or 'N/A'}")


if __name__ == "__main__":
    main()
