#!/usr/bin/env python3
"""
ToxShield YouTube content calendar planner.

Generates weekly/monthly content calendars with topic suggestions,
content type rotation, seasonal relevance, and cross-platform repurposing.

Usage:
    python scripts/youtube/content_planner.py --weeks 1
    python scripts/youtube/content_planner.py --weeks 4
    python scripts/youtube/content_planner.py --analyze-gaps
    python scripts/youtube/content_planner.py --trending
    python scripts/youtube/content_planner.py --json
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.local")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


# ===========================================================================
# Content Type Taxonomy (Performance-Ranked)
# ===========================================================================

CONTENT_TYPES = [
    {
        "type": "storytime_toxic",
        "format": "long-form",
        "duration": "8-15min",
        "engagement": "HIGHEST",
        "weekly_target": 1,
        "description": "Dramatic case studies — 'I analyzed a textbook narcissist'",
        "topics": [
            "I Analyzed a Textbook Narcissist — Here's What I Found",
            "This Relationship Scored 9.2/10 Toxic — The Breakdown",
            "The Most Toxic Person I've Ever Analyzed",
            "Inside the Mind of a Gaslighter — Case Study",
            "When 'Love' Is Actually Coercive Control — Full Analysis",
        ],
    },
    {
        "type": "red_flag_listicle",
        "format": "shorts",
        "duration": "30-60s",
        "engagement": "HIGH",
        "weekly_target": 3,
        "description": "Fast-paced red flag reveals",
        "topics": [
            "5 Signs You're Being Gaslighted",
            "7 Things a Narcissist Says That Sound Normal",
            "3 Red Flags in a Text Message",
            "6 Manipulation Tactics Hidden in 'Jokes'",
            "4 Signs of Love Bombing You're Missing",
            "5 Things Controlling Partners Always Say",
            "3 Phrases That Are Actually Emotional Abuse",
            "7 Signs You're Trauma Bonded",
            "5 Red Flags in How They Apologize",
            "4 Ways Guilt-Tripping Sounds Like Caring",
        ],
    },
    {
        "type": "is_this_toxic_reaction",
        "format": "shorts",
        "duration": "30-60s",
        "engagement": "HIGH",
        "weekly_target": 2,
        "description": "React to scenarios, score them live",
        "topics": [
            "Your partner says 'you're too sensitive.' Is this toxic?",
            "They check your phone 'because they care.' Is this toxic?",
            "They give you the silent treatment after a disagreement.",
            "'I was just joking, you can't take a joke.'",
            "'If you loved me, you wouldn't hang out with them.'",
            "'No one else would put up with you.'",
            "They apologize but add 'but you also...'",
            "'I'm not controlling, I'm protective.'",
        ],
    },
    {
        "type": "pattern_deep_dive",
        "format": "long-form",
        "duration": "10-20min",
        "engagement": "HIGH",
        "weekly_target": 1,
        "description": "DARVO, trauma bonding cycle breakdowns",
        "topics": [
            "DARVO Explained — The Manipulation You Don't See Coming",
            "The Trauma Bonding Cycle — Why You Can't Leave",
            "Coercive Control — The Invisible Prison",
            "The Narcissistic Supply Cycle: Idealize, Devalue, Discard",
            "Why Gaslighting Works — The Psychology Behind It",
            "Grey Rocking: The Protection Strategy That Actually Works",
        ],
    },
    {
        "type": "score_reveal",
        "format": "shorts",
        "duration": "15-30s",
        "engagement": "HIGH",
        "weekly_target": 2,
        "description": "Dramatic toxicity score reveals",
        "topics": [
            "This relationship scored {score}/10 toxic",
            "Analyzing a viewer's situation — score reveal",
            "Is your boss toxic? Score: {score}/10",
            "Rating toxic friendships — the results are shocking",
            "Parent toxicity score reveal — this one hurt",
        ],
    },
    {
        "type": "psychology_explainer",
        "format": "long-form",
        "duration": "8-12min",
        "engagement": "MEDIUM",
        "weekly_target": 0.5,
        "description": "Educational deep dives",
        "topics": [
            "What Is Coercive Control? (And Why It's Not Just 'Being Strict')",
            "The Science of Trauma Bonding — Your Brain on Toxic Love",
            "Why Toxic People Never Think They're Toxic",
            "Attachment Styles and Toxic Relationships — The Connection",
            "The Psychology of Why We Ignore Red Flags",
        ],
    },
    {
        "type": "protection_strategy",
        "format": "shorts",
        "duration": "30-45s",
        "engagement": "MEDIUM",
        "weekly_target": 1,
        "description": "Quick actionable tips",
        "topics": [
            "The Grey Rock Method in 30 seconds",
            "How to Set Boundaries Without Guilt",
            "JADE: The 4 Things You Should Stop Doing",
            "How to Respond to Gaslighting",
            "The No-Contact Rule — How to Actually Do It",
            "What to Say When Someone Guilt-Trips You",
        ],
    },
    {
        "type": "app_demo",
        "format": "shorts",
        "duration": "30-60s",
        "engagement": "LOW",
        "weekly_target": 0.5,
        "description": "ToxShield product showcase",
        "topics": [
            "I built an AI that detects toxic people — here's how it works",
            "Paste a text conversation and get a toxicity score",
            "ToxShield analysis walkthrough — threat profile demo",
            "How ToxShield detects gaslighting patterns",
        ],
    },
]

# Shorts-to-Long pipeline mapping
REPURPOSING_MAP = {
    "red_flag_listicle": "pattern_deep_dive",
    "is_this_toxic_reaction": "storytime_toxic",
    "score_reveal": "storytime_toxic",
    "protection_strategy": "psychology_explainer",
    "app_demo": "storytime_toxic",
}


# ===========================================================================
# Seasonal Events & Awareness Months
# ===========================================================================

SEASONAL_EVENTS = {
    1: {"name": "New Year / Fresh Start", "topics": ["toxic New Year's resolutions", "leaving toxic relationships in the new year"]},
    2: {"name": "Valentine's Day", "topics": ["Is your relationship actually healthy?", "love bombing vs real love", "toxic Valentine's red flags"]},
    3: {"name": "Women's History Month", "topics": ["coercive control awareness", "recognizing emotional abuse"]},
    4: {"name": "Sexual Assault Awareness Month", "topics": ["consent and coercive control", "boundary violations"]},
    5: {"name": "Mental Health Awareness Month", "topics": ["toxic relationships and mental health", "healing from emotional abuse", "therapy after toxic relationships"]},
    7: {"name": "Self-Care Month", "topics": ["recovery after toxic relationships", "rebuilding self-worth"]},
    9: {"name": "Suicide Prevention Month", "topics": ["when toxic relationships affect mental health", "getting help"]},
    10: {"name": "DV Awareness Month", "topics": ["domestic violence patterns", "coercive control signs", "how to help someone in a toxic relationship"]},
    11: {"name": "Gratitude / Boundaries", "topics": ["setting boundaries during holidays", "toxic family dynamics at Thanksgiving"]},
    12: {"name": "Holiday Season", "topics": ["surviving toxic family holidays", "holiday guilt-tripping", "New Year boundary setting"]},
}


# ===========================================================================
# Posting Schedule
# ===========================================================================

WEEKLY_SCHEDULE = {
    "Monday":    {"shorts": ["red_flag_listicle"], "long_form": None, "priority": "HIGH"},
    "Tuesday":   {"shorts": ["is_this_toxic_reaction"], "long_form": "storytime_toxic", "priority": "HIGH"},
    "Wednesday": {"shorts": ["score_reveal"], "long_form": None, "priority": "MEDIUM"},
    "Thursday":  {"shorts": ["protection_strategy"], "long_form": None, "priority": "HIGH"},
    "Friday":    {"shorts": ["red_flag_listicle"], "long_form": "pattern_deep_dive", "priority": "MEDIUM"},
    "Saturday":  {"shorts": ["is_this_toxic_reaction"], "long_form": None, "priority": "MEDIUM"},
    "Sunday":    {"shorts": [], "long_form": None, "priority": "LOW"},
}

BEST_TIMES_UTC = {
    "shorts": "14:00",
    "long_form": "17:00",
}


# ===========================================================================
# Content Planner
# ===========================================================================

class ContentPlanner:
    """Generate YouTube content calendars for ToxShield."""

    def __init__(self, channel_data: Optional[Dict] = None):
        self.channel_data = channel_data
        self.used_topics: set = set()

    def generate_calendar(self, weeks: int = 1, start_date: Optional[datetime] = None) -> List[Dict]:
        """Generate a content calendar for N weeks."""
        if start_date is None:
            start_date = datetime.now()
            # Start from next Monday
            days_ahead = (7 - start_date.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            start_date = start_date + timedelta(days=days_ahead)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        calendar: List[Dict] = []

        for week in range(weeks):
            week_start = start_date + timedelta(weeks=week)
            week_entries = self._plan_week(week_start, week_number=week + 1)
            calendar.extend(week_entries)

        return calendar

    def _plan_week(self, week_start: datetime, week_number: int) -> List[Dict]:
        """Plan content for a single week."""
        entries = []
        month = week_start.month
        seasonal = SEASONAL_EVENTS.get(month)

        for day_offset in range(7):
            date = week_start + timedelta(days=day_offset)
            day_name = date.strftime("%A")
            schedule = WEEKLY_SCHEDULE.get(day_name, {})

            # Shorts for this day
            for content_type in schedule.get("shorts", []):
                topic = self._pick_topic(content_type, seasonal)
                entries.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "week": week_number,
                    "format": "shorts",
                    "content_type": content_type,
                    "time_utc": BEST_TIMES_UTC["shorts"],
                    "topic": topic,
                    "priority": schedule.get("priority", "MEDIUM"),
                    "cross_platform": self._cross_platform_note(content_type, "shorts"),
                    "seasonal_tie": seasonal["name"] if seasonal else None,
                })

            # Long-form for this day
            long_form_type = schedule.get("long_form")
            if long_form_type:
                topic = self._pick_topic(long_form_type, seasonal)
                entries.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "week": week_number,
                    "format": "long-form",
                    "content_type": long_form_type,
                    "time_utc": BEST_TIMES_UTC["long_form"],
                    "topic": topic,
                    "priority": schedule.get("priority", "MEDIUM"),
                    "cross_platform": self._cross_platform_note(long_form_type, "long-form"),
                    "seasonal_tie": seasonal["name"] if seasonal else None,
                })

        return entries

    def _pick_topic(self, content_type: str, seasonal: Optional[Dict] = None) -> str:
        """Pick a topic for a content type, avoiding repeats."""
        ct = next((c for c in CONTENT_TYPES if c["type"] == content_type), None)
        if not ct:
            return f"[{content_type}] topic TBD"

        # Try seasonal topic first (20% chance)
        if seasonal and seasonal.get("topics"):
            import random
            if random.random() < 0.2:
                for topic in seasonal["topics"]:
                    if topic not in self.used_topics:
                        self.used_topics.add(topic)
                        return f"[SEASONAL: {seasonal['name']}] {topic}"

        # Pick from content type topics
        for topic in ct["topics"]:
            if topic not in self.used_topics:
                self.used_topics.add(topic)
                return topic

        # All used — reset and pick first
        self.used_topics = set()
        return ct["topics"][0] if ct["topics"] else f"[{content_type}] topic TBD"

    def _cross_platform_note(self, content_type: str, fmt: str) -> str:
        """Generate cross-platform repurposing notes."""
        if fmt == "shorts":
            long_form = REPURPOSING_MAP.get(content_type)
            if long_form:
                return f"Expand into {long_form} long-form if this Short performs well"
            return "Repost to Instagram Reels"
        elif fmt == "long-form":
            return "Clip into 3-5 Shorts after publishing. Repurpose key slides as Instagram carousel"
        return ""

    def analyze_gaps(self) -> Dict[str, Any]:
        """Analyze content gaps based on channel data."""
        if not self.channel_data:
            return {
                "error": "No channel data provided. Run: python scripts/youtube/analyze_channel.py --json",
                "recommendation": "Run analyze_channel.py first, then pass output via --channel-data",
            }

        videos = self.channel_data.get("recent_videos", [])
        if not videos:
            return {
                "status": "recovery_mode",
                "message": "No recent videos found. Starting recovery mode: post daily for 14 days.",
                "plan": "Day 1: red_flag_listicle Short, Day 2: storytime_toxic long-form, ...",
            }

        # Count content types in recent videos (by keyword matching)
        type_counts = {ct["type"]: 0 for ct in CONTENT_TYPES}
        for video in videos:
            title = video.get("title", "").lower()
            if any(kw in title for kw in ["sign", "red flag", "things"]):
                type_counts["red_flag_listicle"] += 1
            elif any(kw in title for kw in ["is this toxic", "toxic?"]):
                type_counts["is_this_toxic_reaction"] += 1
            elif any(kw in title for kw in ["score", "rated", "/10"]):
                type_counts["score_reveal"] += 1
            elif any(kw in title for kw in ["analyzed", "case study", "story"]):
                type_counts["storytime_toxic"] += 1
            elif any(kw in title for kw in ["explained", "what is", "why"]):
                type_counts["psychology_explainer"] += 1
            elif any(kw in title for kw in ["how to", "strategy", "method"]):
                type_counts["protection_strategy"] += 1
            elif any(kw in title for kw in ["darvo", "trauma bond", "pattern"]):
                type_counts["pattern_deep_dive"] += 1
            elif any(kw in title for kw in ["toxshield", "app", "demo"]):
                type_counts["app_demo"] += 1

        # Find gaps
        gaps = []
        for ct in CONTENT_TYPES:
            count = type_counts[ct["type"]]
            target = ct["weekly_target"] * 4  # Monthly target
            if count < target * 0.5:
                gaps.append({
                    "type": ct["type"],
                    "current": count,
                    "target": target,
                    "deficit": target - count,
                    "priority": ct["engagement"],
                })

        gaps.sort(key=lambda g: g["deficit"], reverse=True)

        # Shorts vs long-form ratio
        shorts_data = self.channel_data.get("shorts_vs_longform", {})
        shorts_count = shorts_data.get("shorts", {}).get("count", 0)
        longform_count = shorts_data.get("longform", {}).get("count", 0)
        total = shorts_count + longform_count
        ratio = f"{shorts_count}:{longform_count}" if total > 0 else "N/A"
        ideal_ratio = "3:1 (Shorts:Long-form)"

        return {
            "content_type_gaps": gaps,
            "format_ratio": {"current": ratio, "ideal": ideal_ratio},
            "total_videos_analyzed": len(videos),
            "recommendations": [
                f"Increase {g['type']} posts (currently {g['current']}, target {g['target']}/month)"
                for g in gaps[:3]
            ],
        }


# ===========================================================================
# Output Formatters
# ===========================================================================

def format_calendar_text(calendar: List[Dict]) -> str:
    """Format calendar as readable text."""
    lines = ["=" * 70, "TOXSHIELD // YOUTUBE CONTENT CALENDAR", "=" * 70, ""]

    current_week = 0
    for entry in calendar:
        if entry["week"] != current_week:
            current_week = entry["week"]
            lines.append(f"\n--- WEEK {current_week} ---\n")

        fmt_badge = "SHORT" if entry["format"] == "shorts" else "LONG "
        priority_marker = {"HIGH": "*", "MEDIUM": " ", "LOW": "."}
        marker = priority_marker.get(entry["priority"], " ")

        lines.append(
            f"{marker} {entry['date']} ({entry['day'][:3]}) "
            f"[{fmt_badge}] {entry['time_utc']} UTC  "
            f"{entry['content_type']}"
        )
        lines.append(f"    Topic: {entry['topic']}")
        if entry.get("cross_platform"):
            lines.append(f"    Cross: {entry['cross_platform']}")
        if entry.get("seasonal_tie"):
            lines.append(f"    Seasonal: {entry['seasonal_tie']}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("* = HIGH priority   (space) = MEDIUM   . = LOW")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)


def format_gaps_text(gaps: Dict) -> str:
    """Format gap analysis as readable text."""
    lines = ["=" * 70, "TOXSHIELD // YOUTUBE CONTENT GAP ANALYSIS", "=" * 70, ""]

    if "error" in gaps:
        lines.append(f"Error: {gaps['error']}")
        lines.append(f"Recommendation: {gaps.get('recommendation', '')}")
        return "\n".join(lines)

    if gaps.get("status") == "recovery_mode":
        lines.append(f"STATUS: RECOVERY MODE")
        lines.append(f"Message: {gaps['message']}")
        return "\n".join(lines)

    lines.append(f"Videos analyzed: {gaps['total_videos_analyzed']}")
    lines.append(f"Format ratio: {gaps['format_ratio']['current']} (ideal: {gaps['format_ratio']['ideal']})")
    lines.append("")

    if gaps["content_type_gaps"]:
        lines.append("CONTENT GAPS (priority order):")
        for gap in gaps["content_type_gaps"]:
            bar_len = min(int(gap["deficit"] * 3), 30)
            bar = "#" * bar_len
            lines.append(
                f"  {gap['type']:<30} {gap['current']:>2}/{gap['target']:<3} "
                f"[{bar}] deficit: {gap['deficit']}"
            )
    else:
        lines.append("No significant content gaps found.")

    lines.append("")
    if gaps.get("recommendations"):
        lines.append("RECOMMENDATIONS:")
        for rec in gaps["recommendations"]:
            lines.append(f"  > {rec}")

    return "\n".join(lines)


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate ToxShield YouTube content calendars"
    )
    parser.add_argument(
        "--weeks", "-w", type=int, default=1,
        help="Number of weeks to plan (default: 1)",
    )
    parser.add_argument(
        "--analyze-gaps", action="store_true",
        help="Analyze content gaps based on channel data",
    )
    parser.add_argument(
        "--channel-data",
        help="Path to channel data JSON (from analyze_channel.py --json)",
    )
    parser.add_argument(
        "--trending", action="store_true",
        help="Include seasonal/trending topic suggestions",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--output", "-o",
        help="Save output to file (default: stdout)",
    )

    args = parser.parse_args()

    # Load channel data if provided
    channel_data = None
    if args.channel_data:
        try:
            with open(args.channel_data) as f:
                channel_data = json.load(f)
            logger.info(f"Loaded channel data from {args.channel_data}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load channel data: {e}")

    planner = ContentPlanner(channel_data)

    if args.analyze_gaps:
        gaps = planner.analyze_gaps()
        if args.json:
            output = json.dumps(gaps, indent=2, default=str)
        else:
            output = format_gaps_text(gaps)
    else:
        calendar = planner.generate_calendar(weeks=args.weeks)

        if args.trending:
            month = datetime.now().month
            seasonal = SEASONAL_EVENTS.get(month)
            if seasonal:
                logger.info(f"Seasonal context: {seasonal['name']}")

        if args.json:
            output = json.dumps(calendar, indent=2, default=str)
        else:
            output = format_calendar_text(calendar)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
        print(f"Saved to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
