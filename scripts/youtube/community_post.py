#!/usr/bin/env python3
"""
ToxShield YouTube community tab content generator.

Generates ready-to-post community tab content (polls, text posts, image posts).
Since the YouTube Data API v3 does not support programmatic community post
creation, this script generates formatted content for manual posting or
browser-assisted posting via Claude's MCP tools.

Usage:
    python scripts/youtube/community_post.py --type poll \
        --text "Which toxic pattern is hardest to recognize?" \
        --options "Gaslighting" "Love Bombing" "DARVO" "Silent Treatment"

    python scripts/youtube/community_post.py --type text \
        --text "New video dropping tomorrow..."

    python scripts/youtube/community_post.py --template which-is-worse

    python scripts/youtube/community_post.py --list-templates
"""

import argparse
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ===========================================================================
# Community Post Templates
# ===========================================================================

TEMPLATES = {
    "which-is-worse": {
        "type": "poll",
        "description": "Two toxic scenarios — audience picks which is worse",
        "variants": [
            {
                "text": "Which is worse? 🚩",
                "options": [
                    "Partner who yells during arguments",
                    "Partner who gives silent treatment for days",
                ],
            },
            {
                "text": "Which toxic pattern is harder to recognize?",
                "options": [
                    "Gaslighting disguised as concern",
                    "Love bombing that feels like real love",
                ],
            },
            {
                "text": "Which is a bigger red flag?",
                "options": [
                    "'I was just joking, you're too sensitive'",
                    "'If you loved me, you wouldn't need friends'",
                ],
            },
            {
                "text": "Which excuse is more manipulative?",
                "options": [
                    "'I only did it because I love you so much'",
                    "'You made me act that way'",
                ],
            },
            {
                "text": "Which is harder to leave?",
                "options": [
                    "A relationship that's always bad",
                    "A relationship that's amazing 80% of the time",
                ],
            },
        ],
    },
    "rate-this-text": {
        "type": "text",
        "description": "Show a text message and ask audience to rate toxicity",
        "variants": [
            {
                "text": (
                    "Rate this text message 1-10 toxic:\n\n"
                    "\"I noticed you were online at 2am. Who were you talking to? "
                    "I'm not controlling, I just care about us.\"\n\n"
                    "Drop your score in the comments. "
                    "ToxShield scored this a 7.2/10."
                ),
            },
            {
                "text": (
                    "Rate this text 1-10:\n\n"
                    "\"I guess I'll just cancel my plans since you obviously "
                    "don't want to spend time with me.\"\n\n"
                    "What's your score? Comment below."
                ),
            },
            {
                "text": (
                    "Is this toxic? Rate 1-10:\n\n"
                    "\"I'm sorry you feel that way, but if you hadn't "
                    "brought it up at dinner, none of this would have happened.\"\n\n"
                    "ToxShield analysis coming in tomorrow's video."
                ),
            },
        ],
    },
    "video-teaser": {
        "type": "text",
        "description": "Tease upcoming video content",
        "variants": [
            {
                "text": (
                    "Tomorrow's video: I analyzed the most toxic relationship "
                    "pattern I've ever seen.\n\n"
                    "Guess the toxicity score. Winner gets pinned.\n\n"
                    "Hint: It involves DARVO."
                ),
            },
            {
                "text": (
                    "New video dropping this week:\n\n"
                    "\"5 Things a Gaslighter Says That Sound Completely Normal\"\n\n"
                    "Which phrase do you think is #1? Comment your guess."
                ),
            },
            {
                "text": (
                    "I just finished analyzing a viewer's situation.\n\n"
                    "Score: higher than expected.\n\n"
                    "Full breakdown video coming soon. "
                    "Turn on notifications so you don't miss it."
                ),
            },
        ],
    },
    "ask-toxshield": {
        "type": "text",
        "description": "Q&A prompt — invite audience questions",
        "variants": [
            {
                "text": (
                    "Ask ToxShield anything.\n\n"
                    "Drop a situation in the comments and I'll rate it "
                    "in the next video.\n\n"
                    "No names, no judgment — just pattern analysis."
                ),
            },
            {
                "text": (
                    "Comment a phrase your ex/friend/family member used to say "
                    "that you now realize was toxic.\n\n"
                    "I'll analyze the top ones in this week's video."
                ),
            },
        ],
    },
    "this-or-that": {
        "type": "poll",
        "description": "Quick preference polls to drive engagement",
        "variants": [
            {
                "text": "What content do you want more of?",
                "options": [
                    "Red flag listicles (Shorts)",
                    "Deep dive case studies (Long-form)",
                    "Score reveals",
                    "Protection strategies",
                ],
            },
            {
                "text": "Which toxic trait topic should I cover next?",
                "options": [
                    "Narcissistic parents",
                    "Toxic friendships",
                    "Gaslighting at work",
                    "Love bombing in dating",
                ],
            },
        ],
    },
}


# ===========================================================================
# Community Post Generator
# ===========================================================================

class CommunityPostGenerator:
    """Generate community post content for YouTube."""

    def generate_from_template(self, template_name: str) -> Dict[str, Any]:
        """Generate a post from a named template."""
        template = TEMPLATES.get(template_name)
        if not template:
            available = ", ".join(TEMPLATES.keys())
            raise ValueError(f"Unknown template: {template_name}. Available: {available}")

        variant = random.choice(template["variants"])
        post = {
            "template": template_name,
            "type": template["type"],
            "text": variant["text"],
            "generated_at": datetime.now().isoformat(),
        }

        if template["type"] == "poll" and "options" in variant:
            post["options"] = variant["options"]

        return post

    def generate_custom(
        self,
        post_type: str,
        text: str,
        options: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a custom community post."""
        post = {
            "template": "custom",
            "type": post_type,
            "text": text,
            "generated_at": datetime.now().isoformat(),
        }

        if post_type == "poll":
            if not options or len(options) < 2:
                raise ValueError("Polls require at least 2 options")
            if len(options) > 4:
                raise ValueError("YouTube polls support max 4 options")
            post["options"] = options

        return post


# ===========================================================================
# Output Formatters
# ===========================================================================

def format_post_text(post: Dict) -> str:
    """Format a community post for display."""
    lines = [
        "=" * 60,
        "TOXSHIELD // YOUTUBE COMMUNITY POST",
        "=" * 60,
        "",
        f"Type: {post['type'].upper()}",
        f"Template: {post['template']}",
        f"Generated: {post['generated_at']}",
        "",
        "--- CONTENT (copy below this line) ---",
        "",
        post["text"],
    ]

    if post["type"] == "poll" and "options" in post:
        lines.append("")
        lines.append("POLL OPTIONS:")
        for i, option in enumerate(post["options"], 1):
            lines.append(f"  {i}. {option}")

    lines.extend([
        "",
        "--- END CONTENT ---",
        "",
        "POST INSTRUCTIONS:",
        "  1. Go to YouTube Studio > Content > Community",
        "  2. Click 'Create post'",
        f"  3. Select '{post['type'].upper()}' format" if post["type"] == "poll" else "  3. Paste the text above",
        "  4. Paste the text and options above",
        "  5. Click 'Post'",
        "",
        "Or ask the agent to use browser MCP tools to post for you.",
    ])

    return "\n".join(lines)


def list_templates() -> str:
    """List all available templates."""
    lines = [
        "=" * 60,
        "TOXSHIELD // COMMUNITY POST TEMPLATES",
        "=" * 60,
        "",
    ]

    for name, template in TEMPLATES.items():
        lines.append(f"  {name:<25} [{template['type'].upper():<4}] {template['description']}")
        lines.append(f"  {'':25} {len(template['variants'])} variants available")
        lines.append("")

    lines.append(f"Usage: python scripts/youtube/community_post.py --template <name>")
    return "\n".join(lines)


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate ToxShield YouTube community tab content"
    )
    parser.add_argument(
        "--type", choices=["poll", "text", "image"],
        help="Post type",
    )
    parser.add_argument(
        "--text", "-t",
        help="Post text content",
    )
    parser.add_argument(
        "--options", nargs="+",
        help="Poll options (2-4 items, for --type poll)",
    )
    parser.add_argument(
        "--template",
        help=f"Use a named template ({', '.join(TEMPLATES.keys())})",
    )
    parser.add_argument(
        "--list-templates", action="store_true",
        help="List all available templates",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    if args.list_templates:
        print(list_templates())
        return

    generator = CommunityPostGenerator()

    if args.template:
        try:
            post = generator.generate_from_template(args.template)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.type and args.text:
        try:
            post = generator.generate_custom(
                post_type=args.type,
                text=args.text,
                options=args.options,
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.error("Provide either --template or both --type and --text")
        return

    if args.json:
        print(json.dumps(post, indent=2))
    else:
        print(format_post_text(post))


if __name__ == "__main__":
    main()
