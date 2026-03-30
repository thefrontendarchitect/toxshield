#!/usr/bin/env python3
"""
ToxShield YouTube channel analytics and strategy report generator.

Standalone CLI script that fetches channel stats, recent videos, and growth
trends via YouTube Data API v3, then generates an HTML strategy report with
ToxShield's monochrome dark theme.

Usage:
    python scripts/youtube/analyze_channel.py                      # Full report
    python scripts/youtube/analyze_channel.py --quick              # Snapshot
    python scripts/youtube/analyze_channel.py --json               # JSON output
    python scripts/youtube/analyze_channel.py --report report.html # Custom output path
    python scripts/youtube/analyze_channel.py --top-performers 10  # Top N videos
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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
# Exception Classes
# ===========================================================================

class YouTubeAnalyticsError(Exception):
    """Base exception for YouTube analytics operations."""
    pass

class YouTubeAuthError(YouTubeAnalyticsError):
    """Authentication or credential errors."""
    pass

class YouTubeQuotaError(YouTubeAnalyticsError):
    """API quota exceeded."""
    pass


# ===========================================================================
# YouTube Analytics Client
# ===========================================================================

class YouTubeAnalyticsClient:
    """Client for YouTube Data API v3 and YouTube Analytics API — read-only."""

    SHORTS_MAX_DURATION = 60  # seconds

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
        self.youtube_analytics = build(
            "youtubeAnalytics", "v2", credentials=self.credentials,
        )
        self._quota_used = 0

    @property
    def quota_used(self) -> int:
        """Total API quota units consumed this session."""
        return self._quota_used

    def _track_quota(self, units: int, method: str) -> None:
        """Log and accumulate quota usage."""
        self._quota_used += units
        logger.debug(f"Quota: +{units} ({method}) → {self._quota_used} total")

    # --- Channel Stats ---------------------------------------------------

    def get_channel_stats(self) -> Dict[str, Any]:
        """Fetch channel-level statistics and snippet info.

        Returns dict with subscribers, total_views, video_count, title,
        description, published_at, and thumbnail URL.
        Quota cost: 1 unit (channels.list).
        """
        response = self.youtube.channels().list(
            part="statistics,snippet",
            mine=True,
        ).execute()
        self._track_quota(1, "channels.list")

        items = response.get("items", [])
        if not items:
            raise YouTubeAnalyticsError("No channel found for authenticated user")

        channel = items[0]
        stats = channel.get("statistics", {})
        snippet = channel.get("snippet", {})

        return {
            "channel_id": channel["id"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "hidden_subscriber_count": stats.get("hiddenSubscriberCount", False),
        }

    # --- Recent Videos ----------------------------------------------------

    def get_recent_videos(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent uploads with full statistics.

        Uses search.list (100 units) to find video IDs, then videos.list
        (1 unit) for details. Returns list of video dicts sorted by date.
        Quota cost: 100 + 1 = 101 units per call.
        """
        # search.list — expensive (100 units), but needed for forMine
        search_response = self.youtube.search().list(
            part="id",
            forMine=True,
            type="video",
            order="date",
            maxResults=min(limit, 50),
        ).execute()
        self._track_quota(100, "search.list")

        video_ids = [
            item["id"]["videoId"]
            for item in search_response.get("items", [])
            if item.get("id", {}).get("videoId")
        ]

        if not video_ids:
            logger.warning("No videos found via search.list")
            return []

        # videos.list — cheap (1 unit) — batch up to 50 IDs
        videos_response = self.youtube.videos().list(
            part="statistics,snippet,contentDetails",
            id=",".join(video_ids),
        ).execute()
        self._track_quota(1, "videos.list")

        videos = []
        for item in videos_response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            duration_seconds = self._parse_duration(content.get("duration", "PT0S"))

            videos.append({
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "duration_seconds": duration_seconds,
                "duration_label": self._format_duration(duration_seconds),
                "is_short": duration_seconds <= self.SHORTS_MAX_DURATION,
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            })

        videos.sort(key=lambda v: v["published_at"], reverse=True)
        logger.info(f"Fetched {len(videos)} videos (quota used: {self._quota_used})")
        return videos

    # --- Shorts vs Long-form ---------------------------------------------

    def get_shorts_vs_longform(self, videos: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Separate metrics for Shorts (<=60s) vs long-form content.

        If videos are not provided, fetches them first.
        Returns counts, average views, average likes for each category.
        """
        if videos is None:
            videos = self.get_recent_videos()

        shorts = [v for v in videos if v["is_short"]]
        longform = [v for v in videos if not v["is_short"]]

        def _aggregate(vids: List[Dict]) -> Dict[str, Any]:
            if not vids:
                return {"count": 0, "avg_views": 0, "avg_likes": 0, "total_views": 0}
            return {
                "count": len(vids),
                "avg_views": round(sum(v["views"] for v in vids) / len(vids), 1),
                "avg_likes": round(sum(v["likes"] for v in vids) / len(vids), 1),
                "total_views": sum(v["views"] for v in vids),
            }

        return {
            "shorts": _aggregate(shorts),
            "longform": _aggregate(longform),
        }

    # --- Growth Trends (YouTube Analytics API) ----------------------------

    def get_growth_trends(self, days: int = 90) -> Dict[str, Any]:
        """Fetch daily views and subscriber changes via YouTube Analytics API.

        Quota cost: 1 unit (reports.query).
        Returns daily time-series plus totals for the period.
        """
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=days)

        try:
            response = self.youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date.isoformat(),
                endDate=end_date.isoformat(),
                metrics="views,subscribersGained,subscribersLost,estimatedMinutesWatched",
                dimensions="day",
                sort="day",
            ).execute()
            self._track_quota(1, "youtubeAnalytics.reports.query")
        except Exception as e:
            logger.warning(f"YouTube Analytics API query failed: {e}")
            return {"daily": [], "period_days": days, "error": str(e)}

        rows = response.get("rows", [])
        daily = []
        total_views = 0
        total_subs_gained = 0
        total_subs_lost = 0
        total_watch_minutes = 0

        for row in rows:
            day_str, views, gained, lost, watch_min = row
            total_views += views
            total_subs_gained += gained
            total_subs_lost += lost
            total_watch_minutes += watch_min
            daily.append({
                "date": day_str,
                "views": views,
                "subs_gained": gained,
                "subs_lost": lost,
                "watch_minutes": round(watch_min, 1),
            })

        return {
            "period_days": days,
            "daily": daily,
            "total_views": total_views,
            "total_subs_gained": total_subs_gained,
            "total_subs_lost": total_subs_lost,
            "net_subs": total_subs_gained - total_subs_lost,
            "total_watch_hours": round(total_watch_minutes / 60, 1),
        }

    # --- YPP Progress -----------------------------------------------------

    def get_ypp_progress(
        self,
        channel_stats: Optional[Dict] = None,
        growth_trends: Optional[Dict] = None,
        shorts_vs_long: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Calculate progress toward YouTube Partner Program thresholds.

        Standard path:   1,000 subscribers + 4,000 public watch hours (12 months)
        Shorts path:     1,000 subscribers + 10,000,000 Shorts views (90 days)
        """
        if channel_stats is None:
            channel_stats = self.get_channel_stats()

        subs = channel_stats.get("subscribers", 0)
        subs_pct = min(round(subs / 1000 * 100, 1), 100.0) if subs else 0.0

        # Watch hours — use analytics data if available
        watch_hours = 0.0
        if growth_trends and "total_watch_hours" in growth_trends:
            watch_hours = growth_trends["total_watch_hours"]
        watch_hours_pct = min(round(watch_hours / 4000 * 100, 1), 100.0)

        # Shorts views in last 90 days
        shorts_views_90d = 0
        if shorts_vs_long:
            shorts_views_90d = shorts_vs_long.get("shorts", {}).get("total_views", 0)
        shorts_views_pct = min(round(shorts_views_90d / 10_000_000 * 100, 1), 100.0)

        standard_eligible = subs >= 1000 and watch_hours >= 4000
        shorts_eligible = subs >= 1000 and shorts_views_90d >= 10_000_000

        return {
            "subscribers": {"current": subs, "target": 1000, "percent": subs_pct},
            "watch_hours": {"current": round(watch_hours, 1), "target": 4000, "percent": watch_hours_pct},
            "shorts_views_90d": {"current": shorts_views_90d, "target": 10_000_000, "percent": shorts_views_pct},
            "standard_path_eligible": standard_eligible,
            "shorts_path_eligible": shorts_eligible,
        }

    # --- Helpers ----------------------------------------------------------

    @staticmethod
    def _parse_duration(iso_duration: str) -> int:
        """Parse ISO 8601 duration (PT1H2M3S) to total seconds."""
        match = re.match(
            r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration,
        )
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds as human-readable duration (e.g. '2:34' or '1:02:15')."""
        if seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d}"
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h}:{m:02d}:{s:02d}"


# ===========================================================================
# Analytics
# ===========================================================================

def analyze_channel(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute insights from raw channel data.

    Args:
        data: dict with keys 'channel', 'videos', 'shorts_vs_long',
              'growth_trends', 'ypp_progress'.

    Returns:
        Enriched analysis dict with computed recommendations.
    """
    channel = data.get("channel", {})
    videos = data.get("videos", [])
    shorts_vs_long = data.get("shorts_vs_long", {})
    growth = data.get("growth_trends", {})
    ypp = data.get("ypp_progress", {})

    # --- Upload frequency -------------------------------------------------
    publish_dates: List[datetime] = []
    weekday_counts: Counter = Counter()
    hour_counts: Counter = Counter()

    for v in videos:
        ts = v.get("published_at", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                publish_dates.append(dt)
                weekday_counts[dt.strftime("%A")] += 1
                hour_counts[dt.hour] += 1
            except (ValueError, TypeError):
                pass

    if len(publish_dates) >= 2:
        date_range = (max(publish_dates) - min(publish_dates)).days
        uploads_per_week = len(videos) / max(date_range / 7, 1)
    else:
        date_range = 0
        uploads_per_week = 0

    best_days = dict(
        sorted(weekday_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    )
    best_hours = dict(
        sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    )

    # --- Top performers ---------------------------------------------------
    top_by_views = sorted(videos, key=lambda v: v.get("views", 0), reverse=True)
    top_by_likes = sorted(videos, key=lambda v: v.get("likes", 0), reverse=True)

    # --- Engagement rate --------------------------------------------------
    total_views = sum(v.get("views", 0) for v in videos)
    total_likes = sum(v.get("likes", 0) for v in videos)
    total_comments = sum(v.get("comments", 0) for v in videos)
    avg_engagement = (
        round((total_likes + total_comments) / total_views * 100, 2)
        if total_views > 0 else 0
    )

    # --- Recommendations --------------------------------------------------
    recommendations: List[str] = []

    if uploads_per_week < 3:
        recommendations.append(
            "Increase upload frequency to at least 3 videos/week for better algorithmic reach."
        )
    else:
        recommendations.append(
            f"Upload cadence is solid at {uploads_per_week:.1f}/week. Stay consistent."
        )

    shorts_data = shorts_vs_long.get("shorts", {})
    longform_data = shorts_vs_long.get("longform", {})

    if shorts_data.get("count", 0) == 0:
        recommendations.append(
            "Start posting Shorts — they drive subscriber growth and are "
            "a separate YPP monetization path (10M views in 90 days)."
        )
    elif longform_data.get("count", 0) == 0:
        recommendations.append(
            "Add long-form videos (8-15 min) for higher watch time and ad revenue. "
            "Shorts alone may not hit 4,000 watch hours for YPP."
        )
    else:
        shorts_avg = shorts_data.get("avg_views", 0)
        long_avg = longform_data.get("avg_views", 0)
        if shorts_avg > long_avg * 2:
            recommendations.append(
                f"Shorts outperform long-form by {shorts_avg / max(long_avg, 1):.1f}x on avg views. "
                "Double down on Shorts while using long-form for depth."
            )
        else:
            recommendations.append(
                "Balance is good between Shorts and long-form. Keep both formats."
            )

    if avg_engagement < 3:
        recommendations.append(
            "Engagement rate is low. Add stronger CTAs, ask questions, "
            "and reply to comments in the first hour."
        )

    ypp_subs = ypp.get("subscribers", {})
    if ypp_subs.get("percent", 0) < 100:
        recommendations.append(
            f"YPP: {ypp_subs.get('current', 0)}/1,000 subscribers. "
            "Focus on Shorts virality and end-screen subscribe prompts."
        )

    return {
        "channel": channel,
        "total_videos_analyzed": len(videos),
        "date_range_days": date_range,
        "uploads_per_week": round(uploads_per_week, 1),
        "engagement": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_engagement_pct": avg_engagement,
        },
        "shorts_vs_longform": shorts_vs_long,
        "growth_trends": growth,
        "ypp_progress": ypp,
        "best_posting_days": best_days,
        "best_posting_hours": {f"{h:02d}:00": c for h, c in best_hours.items()},
        "top_by_views": [
            {
                "title": v["title"][:60],
                "views": v["views"],
                "likes": v["likes"],
                "duration": v["duration_label"],
                "is_short": v["is_short"],
            }
            for v in top_by_views[:10]
        ],
        "top_by_likes": [
            {
                "title": v["title"][:60],
                "likes": v["likes"],
                "views": v["views"],
            }
            for v in top_by_likes[:5]
        ],
        "recommendations": recommendations,
    }


# ===========================================================================
# HTML Report — ToxShield Monochrome Dark Theme
# ===========================================================================

def generate_html_report(analysis: Dict[str, Any], output_path: str) -> None:
    """Generate an HTML strategy report with ToxShield monochrome theme."""
    channel = analysis.get("channel", {})
    ypp = analysis.get("ypp_progress", {})
    svl = analysis.get("shorts_vs_longform", {})
    engagement = analysis.get("engagement", {})

    # --- YPP progress bars ------------------------------------------------
    subs_pct = ypp.get("subscribers", {}).get("percent", 0)
    subs_cur = ypp.get("subscribers", {}).get("current", 0)
    wh_pct = ypp.get("watch_hours", {}).get("percent", 0)
    wh_cur = ypp.get("watch_hours", {}).get("current", 0)
    sv_pct = ypp.get("shorts_views_90d", {}).get("percent", 0)
    sv_cur = ypp.get("shorts_views_90d", {}).get("current", 0)

    # --- Top videos table rows --------------------------------------------
    top_rows = ""
    for v in analysis.get("top_by_views", []):
        tag = "SHORT" if v.get("is_short") else "LONG"
        top_rows += (
            f'<tr>'
            f'<td style="color:#fff;font-weight:500">{v["title"]}</td>'
            f'<td style="font-family:monospace;color:#fff;text-align:right">{v["views"]:,}</td>'
            f'<td style="font-family:monospace;color:#666;text-align:right">{v["likes"]:,}</td>'
            f'<td style="font-family:monospace;color:#666;text-align:center">{v["duration"]}</td>'
            f'<td style="font-family:monospace;color:#666;text-align:center">{tag}</td>'
            f'</tr>'
        )

    # --- Best days bars ---------------------------------------------------
    best_days = analysis.get("best_posting_days", {})
    max_day_val = max(best_days.values()) if best_days else 1
    days_bars = "".join(
        f'<div class="bar"><div class="name">{day}</div>'
        f'<div class="fill" style="width: {val / max_day_val * 300}px"></div>'
        f'<div class="val">{val} uploads</div></div>'
        for day, val in best_days.items()
    )

    # --- Best hours bars --------------------------------------------------
    best_hours = analysis.get("best_posting_hours", {})
    max_hour_val = max(best_hours.values()) if best_hours else 1
    hours_bars = "".join(
        f'<div class="bar"><div class="name">{hour}</div>'
        f'<div class="fill" style="width: {val / max_hour_val * 300}px"></div>'
        f'<div class="val">{val} uploads</div></div>'
        for hour, val in list(best_hours.items())[:5]
    )

    # --- Recommendations list ---------------------------------------------
    rec_items = "".join(
        f'<li style="margin:12px 0;border-left:2px solid #fff;padding-left:12px">{r}</li>'
        for r in analysis.get("recommendations", [])
    )

    # --- Shorts vs Long-form comparison -----------------------------------
    shorts = svl.get("shorts", {})
    longform = svl.get("longform", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ToxShield YouTube Strategy Report</title>
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
.progress-track {{
    background: #111;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    height: 24px;
    overflow: hidden;
    margin: 6px 0 12px;
}}
.progress-fill {{
    height: 100%;
    background: #fff;
    border-radius: 3px;
    box-shadow: 0 0 8px rgba(255,255,255,0.2);
    transition: width 0.3s;
}}
.progress-label {{
    font-family: monospace;
    font-size: 0.85rem;
    color: #999;
    display: flex;
    justify-content: space-between;
}}
.compare-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}}
.compare-col {{
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}}
.compare-col .col-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}}
.compare-col .metric {{
    margin: 10px 0;
}}
.compare-col .metric .val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
}}
.compare-col .metric .lbl {{
    font-size: 0.75rem;
    color: #666;
    text-transform: uppercase;
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
<h1>ToxShield // YouTube Strategy Report</h1>
<p class="subtitle">Generated {datetime.now().strftime('%Y-%m-%d')} // {channel.get('title', 'Channel')} // {analysis['total_videos_analyzed']} videos analyzed</p>

<h2>Channel Overview</h2>
<div class="grid">
<div class="stat">
    <div class="value">{channel.get('subscribers', 0):,}</div>
    <div class="label">Subscribers</div>
</div>
<div class="stat">
    <div class="value">{channel.get('total_views', 0):,}</div>
    <div class="label">Total Views</div>
</div>
<div class="stat">
    <div class="value">{channel.get('video_count', 0)}</div>
    <div class="label">Videos</div>
</div>
<div class="stat">
    <div class="value">{analysis['uploads_per_week']}</div>
    <div class="label">Uploads / Week</div>
</div>
</div>

<h2>YPP Monetization Progress</h2>
<div class="card">
<div class="progress-label">
    <span>Subscribers</span>
    <span>{subs_cur:,} / 1,000 ({subs_pct}%)</span>
</div>
<div class="progress-track">
    <div class="progress-fill" style="width: {subs_pct}%"></div>
</div>

<div class="progress-label">
    <span>Watch Hours (last 12 months)</span>
    <span>{wh_cur:,.1f} / 4,000 ({wh_pct}%)</span>
</div>
<div class="progress-track">
    <div class="progress-fill" style="width: {wh_pct}%"></div>
</div>

<div class="progress-label">
    <span>Shorts Views (90 days)</span>
    <span>{sv_cur:,} / 10,000,000 ({sv_pct}%)</span>
</div>
<div class="progress-track">
    <div class="progress-fill" style="width: {sv_pct}%"></div>
</div>
</div>

<h2>Shorts vs Long-form Performance</h2>
<div class="compare-grid">
<div class="compare-col">
    <div class="col-title">Shorts (&le;60s)</div>
    <div class="metric"><div class="val">{shorts.get('count', 0)}</div><div class="lbl">Videos</div></div>
    <div class="metric"><div class="val">{shorts.get('avg_views', 0):,.0f}</div><div class="lbl">Avg Views</div></div>
    <div class="metric"><div class="val">{shorts.get('avg_likes', 0):,.0f}</div><div class="lbl">Avg Likes</div></div>
</div>
<div class="compare-col">
    <div class="col-title">Long-form (&gt;60s)</div>
    <div class="metric"><div class="val">{longform.get('count', 0)}</div><div class="lbl">Videos</div></div>
    <div class="metric"><div class="val">{longform.get('avg_views', 0):,.0f}</div><div class="lbl">Avg Views</div></div>
    <div class="metric"><div class="val">{longform.get('avg_likes', 0):,.0f}</div><div class="lbl">Avg Likes</div></div>
</div>
</div>

<h2>Top Performing Videos</h2>
<div class="card">
<table>
<tr><th>Title</th><th style="text-align:right">Views</th><th style="text-align:right">Likes</th><th style="text-align:center">Duration</th><th style="text-align:center">Type</th></tr>
{top_rows}
</table>
</div>

<h2>Upload Frequency &amp; Best Days/Hours</h2>
<div class="card">
<p style="color:#666;font-family:monospace;margin-bottom:16px">
    {analysis['total_videos_analyzed']} videos over {analysis['date_range_days']} days
    ({analysis['uploads_per_week']} uploads/week)
</p>
<h3 style="font-size:0.9rem;color:#999;margin-bottom:8px;font-family:monospace">BEST DAYS</h3>
{days_bars}
<h3 style="font-size:0.9rem;color:#999;margin:16px 0 8px;font-family:monospace">BEST HOURS (UTC)</h3>
{hours_bars}
</div>

<h2>Engagement Summary</h2>
<div class="grid">
<div class="stat">
    <div class="value">{engagement.get('total_views', 0):,}</div>
    <div class="label">Total Views</div>
</div>
<div class="stat">
    <div class="value">{engagement.get('total_likes', 0):,}</div>
    <div class="label">Total Likes</div>
</div>
<div class="stat">
    <div class="value">{engagement.get('total_comments', 0):,}</div>
    <div class="label">Total Comments</div>
</div>
<div class="stat">
    <div class="value">{engagement.get('avg_engagement_pct', 0)}%</div>
    <div class="label">Engagement Rate</div>
</div>
</div>

<h2>Recommendations</h2>
<div class="card">
<ul style="list-style:none;padding:0;color:#666">
{rec_items}
</ul>
</div>

<div class="footer">ToxShield // YouTube Strategy Report // Powered by Claude</div>
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
        description="Analyze ToxShield YouTube channel and generate strategy report",
    )
    parser.add_argument(
        "--report", "-r",
        default=str(PROJECT_ROOT / "output" / "youtube" / "strategy_report.html"),
        help="Output HTML report path (default: output/youtube/strategy_report.html)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output analysis as JSON instead of HTML",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick snapshot: channel stats + last 10 videos only (saves quota)",
    )
    parser.add_argument(
        "--top-performers", type=int, default=10,
        help="Number of top videos to include (default: 10)",
    )
    parser.add_argument(
        "--days", type=int, default=90,
        help="Number of days for growth trends (default: 90)",
    )

    args = parser.parse_args()

    # --- Initialize client ------------------------------------------------
    try:
        client = YouTubeAnalyticsClient()
    except (YouTubeAuthError, ImportError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Fetch data -------------------------------------------------------
    try:
        print("Fetching channel stats...")
        channel_stats = client.get_channel_stats()
        print(f"  Channel: {channel_stats['title']}")
        print(f"  Subscribers: {channel_stats['subscribers']:,}")
        print(f"  Total views: {channel_stats['total_views']:,}")

        video_limit = 10 if args.quick else 50
        print(f"\nFetching last {video_limit} videos...")
        videos = client.get_recent_videos(limit=video_limit)
        print(f"  Retrieved {len(videos)} videos")

        print("Analyzing Shorts vs long-form...")
        shorts_vs_long = client.get_shorts_vs_longform(videos)
        shorts_count = shorts_vs_long["shorts"]["count"]
        long_count = shorts_vs_long["longform"]["count"]
        print(f"  Shorts: {shorts_count}, Long-form: {long_count}")

        growth = {}
        if not args.quick:
            print(f"\nFetching growth trends ({args.days} days)...")
            growth = client.get_growth_trends(days=args.days)
            if "error" not in growth:
                print(f"  Period views: {growth['total_views']:,}")
                print(f"  Net subscribers: {growth['net_subs']:+,}")
                print(f"  Watch hours: {growth['total_watch_hours']:,.1f}")
            else:
                print(f"  Analytics API unavailable: {growth['error']}")

        print("\nCalculating YPP progress...")
        ypp = client.get_ypp_progress(channel_stats, growth, shorts_vs_long)
        print(f"  Subscribers: {ypp['subscribers']['percent']}% toward 1K")
        print(f"  Watch hours: {ypp['watch_hours']['percent']}% toward 4K")

        print(f"\nAPI quota used: {client.quota_used} units")

    except YouTubeQuotaError as e:
        print(f"\nQuota exceeded: {e}", file=sys.stderr)
        print("Fix: Wait until midnight PT (quota resets daily).", file=sys.stderr)
        sys.exit(1)

    except YouTubeAuthError as e:
        print(f"\nAuth error: {e}", file=sys.stderr)
        print("Fix: Re-run: python scripts/youtube/auth_setup.py", file=sys.stderr)
        sys.exit(1)

    except YouTubeAnalyticsError as e:
        print(f"\nAnalytics error: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Analyze ----------------------------------------------------------
    print("\nAnalyzing channel data...")
    raw_data = {
        "channel": channel_stats,
        "videos": videos,
        "shorts_vs_long": shorts_vs_long,
        "growth_trends": growth,
        "ypp_progress": ypp,
    }
    analysis = analyze_channel(raw_data)

    # Respect --top-performers flag
    analysis["top_by_views"] = analysis["top_by_views"][:args.top_performers]

    # --- Output -----------------------------------------------------------
    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        generate_html_report(analysis, args.report)
        print(f"\nKey Metrics:")
        print(f"  Subscribers: {channel_stats['subscribers']:,}")
        print(f"  Uploads/week: {analysis['uploads_per_week']}")
        print(f"  Engagement rate: {analysis['engagement']['avg_engagement_pct']}%")
        print(f"  Shorts: {shorts_count} | Long-form: {long_count}")
        print(f"  YPP subs progress: {ypp['subscribers']['percent']}%")


if __name__ == "__main__":
    main()
