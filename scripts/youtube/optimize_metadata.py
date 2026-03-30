#!/usr/bin/env python3
"""
ToxShield YouTube SEO Metadata Optimizer — analyze titles, generate descriptions,
tags, and keyword suggestions for maximum discoverability.

Usage:
    python scripts/youtube/optimize_metadata.py --title "5 Signs You're Being Gaslighted"
    python scripts/youtube/optimize_metadata.py --suggest-titles --topic "gaslighting red flags"
    python scripts/youtube/optimize_metadata.py --generate-description --title "..." --include-timestamps
    python scripts/youtube/optimize_metadata.py --generate-tags --topic "gaslighting" --count 20
    python scripts/youtube/optimize_metadata.py --keywords --topic "narcissist red flags"
    Append --output-format json to any command for structured output.
"""
from __future__ import annotations

import argparse, json, logging, re, sys, urllib.parse, urllib.request
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
# Constants
# ===========================================================================

CONTENT_TYPES = [
    "storytime_toxic", "red_flag_listicle", "is_this_toxic_reaction",
    "pattern_deep_dive", "score_reveal", "psychology_explainer",
    "protection_strategy", "app_demo",
]
POWER_WORDS = [
    "never", "always", "actually", "secretly", "stop", "why",
    "you", "your", "you're", "truth", "real", "shocking",
    "warning", "exposed", "finally", "worst", "best", "proven",
]
EMOTIONAL_TRIGGERS = [
    "toxic", "narcissist", "gaslight", "manipulat", "abuse",
    "red flag", "trauma", "surviv", "escape", "protect",
    "dangerous", "silent treatment", "love bombing", "control",
]
BRANDED_TAGS = ["ToxShield", "ToxicityScore", "ToxShieldApp"]
BROAD_TAGS = [
    "toxic relationships", "relationship advice", "psychology",
    "mental health", "emotional abuse", "narcissistic abuse",
    "red flags", "self help", "relationship tips", "boundaries",
]
YOUTUBE_TAG_CHAR_LIMIT = 500
SHORTS_TITLE_RANGE = (40, 60)
LONG_FORM_TITLE_RANGE = (50, 70)
TOXSHIELD_URL = "https://toxshield.in/"
YOUTUBE_SUGGEST_URL = (
    "https://suggestqueries.google.com/complete/search"
    "?client=youtube&ds=yt&q={query}"
)
_KEYWORD_DISPLAY: Dict[str, str] = {
    "gaslight": "gaslighting", "manipulat": "manipulation",
    "narcissist": "narcissism", "surviv": "survival",
}

# ===========================================================================
# Title Analysis
# ===========================================================================

def analyze_title(title: str, content_type: Optional[str] = None, is_short: bool = True) -> Dict[str, Any]:
    """Score a YouTube title 0-100 and provide improvement suggestions."""
    score, deductions, suggestions = 100, [], []
    min_len, max_len = SHORTS_TITLE_RANGE if is_short else LONG_FORM_TITLE_RANGE
    length, title_lower = len(title), title.lower()

    if length < min_len:
        p = min(20, (min_len - length) * 2); score -= p
        deductions.append(f"-{p}: Too short ({length} chars, optimal {min_len}-{max_len})")
        suggestions.append(f"Expand to at least {min_len} characters for better CTR.")
    elif length > max_len:
        p = min(15, length - max_len); score -= p
        deductions.append(f"-{p}: Too long ({length} chars, optimal {min_len}-{max_len})")
        suggestions.append(f"Trim to under {max_len} characters to avoid truncation.")

    found_power = [w for w in POWER_WORDS if w in title_lower]
    if not found_power:
        score -= 15; deductions.append("-15: No power words detected")
        suggestions.append(f"Add power words like: {', '.join(POWER_WORDS[:6])}")

    has_number = bool(re.search(r"\d+", title))
    if not has_number:
        score -= 10; deductions.append("-10: No number in title")
        suggestions.append("Titles with numbers get ~36% higher CTR. Add a count or score.")

    found_triggers = [t for t in EMOTIONAL_TRIGGERS if t in title_lower]
    if not found_triggers:
        score -= 10; deductions.append("-10: No emotional trigger keywords")
        suggestions.append(f"Include emotional hooks: {', '.join(EMOTIONAL_TRIGGERS[:5])}")

    if found_triggers and not any(t in title_lower[:50] for t in EMOTIONAL_TRIGGERS):
        score -= 10; deductions.append("-10: Primary keyword not in first 50 characters")
        suggestions.append("Move your main keyword closer to the start of the title.")

    if sum(1 for c in title if c.isupper()) / max(length, 1) > 0.5:
        score -= 10; deductions.append("-10: Excessive capitalization (looks spammy)")
        suggestions.append("Use title case or sentence case. ALL CAPS hurts trust.")

    if content_type and content_type not in CONTENT_TYPES:
        suggestions.append(f"Unknown content type '{content_type}'. Valid: {', '.join(CONTENT_TYPES)}")

    return {
        "title": title, "score": max(0, min(100, score)), "length": length,
        "is_short": is_short, "optimal_range": f"{min_len}-{max_len}",
        "power_words_found": found_power, "emotional_triggers_found": found_triggers,
        "has_number": has_number, "deductions": deductions, "suggestions": suggestions,
    }

# ===========================================================================
# Title Suggestions
# ===========================================================================

TITLE_TEMPLATES = {
    "listicle": "{n} Signs of {pattern} You're Ignoring",
    "reaction": "Is This Toxic? {scenario}",
    "storytime": "I Analyzed a {relationship} \u2014 Score: {score}/10",
    "hot_take": "Stop Saying \"{phrase}\" \u2014 Here's Why",
    "question": "Why Does {pattern} Feel Normal?",
}

def suggest_titles(topic: str, count: int = 5) -> List[Dict[str, str]]:
    """Generate title suggestions from proven templates."""
    words = topic.strip().split()
    pattern = topic.title()
    scenario = f"When They Say \"{pattern}\""
    relationship = words[0].title() if words else "Relationship"
    phrase = " ".join(words[:3]).title() if len(words) >= 2 else pattern

    raw = [
        {"template": "listicle", "title": TITLE_TEMPLATES["listicle"].format(n=5, pattern=pattern)},
        {"template": "listicle", "title": TITLE_TEMPLATES["listicle"].format(n=7, pattern=pattern)},
        {"template": "reaction", "title": TITLE_TEMPLATES["reaction"].format(scenario=scenario)},
        {"template": "storytime", "title": TITLE_TEMPLATES["storytime"].format(relationship=relationship, score=8)},
        {"template": "hot_take", "title": TITLE_TEMPLATES["hot_take"].format(phrase=phrase)},
        {"template": "question", "title": TITLE_TEMPLATES["question"].format(pattern=pattern)},
    ]
    return raw[:count]

# ===========================================================================
# Description Generator
# ===========================================================================

DISCLAIMER = (
    "Disclaimer: This content is for educational purposes only and does not "
    "constitute professional psychological or legal advice. If you are in an "
    "abusive situation, please contact a local helpline or professional."
)

def generate_description(
    title: str, topic: Optional[str] = None,
    include_timestamps: bool = False, include_disclaimer: bool = True,
) -> str:
    """Build a full YouTube description from template sections."""
    kw = topic or _extract_keyword(title)
    sections = [
        f"If you recognize these patterns, trust your gut.\n{title} \u2014 watch before it's too late.",
        (f"In this video we break down the psychology behind {kw}. "
         f"Learn the exact signs, what they mean, and how to protect yourself. "
         f"ToxShield's AI behavioral analyzer scores every pattern so you can see the truth clearly."),
    ]
    if include_timestamps:
        sections.append(
            f"\u23f0 Timestamps:\n0:00 \u2014 Intro\n0:15 \u2014 What is {kw}?\n"
            f"0:45 \u2014 Sign #1\n1:15 \u2014 Sign #2\n1:45 \u2014 Sign #3\n"
            f"2:15 \u2014 How to protect yourself\n2:45 \u2014 ToxShield demo")
    sections.append(
        f"\U0001f6e1\ufe0f Try ToxShield free: {TOXSHIELD_URL}\n"
        f"Analyze anyone in your life \u2014 get a toxicity score in seconds.")
    sections.append(
        "\U0001f4f2 Follow ToxShield:\n"
        "Instagram: https://instagram.com/toxshield.in\n"
        "YouTube: https://youtube.com/@toxshield")
    sections.append(
        f"Understanding {kw} is essential for maintaining healthy relationships. "
        f"Many people experience {kw} without recognizing the warning signs. "
        f"This video covers the most common patterns of {kw}, how to identify them "
        f"early, and practical strategies to protect your mental health and emotional "
        f"well-being. Whether you are dealing with a toxic partner, family member, "
        f"friend, or coworker, these insights apply across all relationship types. "
        f"ToxShield uses AI behavioral analysis to detect toxic personality patterns "
        f"and generate a forensic threat profile with a toxicity score from 0 to 10. "
        f"Share this video with someone who needs to see it.")
    tag_slug = kw.lower().replace(" ", "")
    sections.append(f"#{tag_slug} #toxicrelationships #toxshield #mentalhealth #redflags")
    if include_disclaimer:
        sections.append(DISCLAIMER)
    return "\n\n".join(sections)


def _extract_keyword(title: str) -> str:
    """Pull the most relevant keyword phrase from a title."""
    t = title.lower()
    for trigger in EMOTIONAL_TRIGGERS:
        if trigger in t:
            return _KEYWORD_DISPLAY.get(trigger, trigger)
    words = [w for w in re.findall(r"[a-zA-Z]+", title) if len(w) > 4]
    return words[0] if words else "toxic behavior"

# ===========================================================================
# Tag Generation
# ===========================================================================

_TAG_EXPANSIONS: Dict[str, List[str]] = {
    "gaslighting": ["gaslighter", "am I being gaslighted", "gaslighting examples"],
    "narcissist": ["narcissistic abuse", "covert narcissist", "narcissist red flags"],
    "toxic": ["toxic behavior", "toxic partner", "toxic traits"],
    "manipulation": ["manipulative tactics", "emotional manipulation"],
    "love bombing": ["love bomb", "love bombing signs"],
    "silent treatment": ["stonewalling", "silent treatment narcissist"],
    "boundaries": ["setting boundaries", "boundary violations"],
}

def generate_tags(topic: str, count: int = 20) -> Dict[str, Any]:
    """Generate YouTube tags within the 500-char limit."""
    # Topic-specific tags
    specific: List[str] = [topic.strip()]
    for w in topic.lower().split():
        if len(w) > 3 and w not in {"with", "that", "this", "from", "they"}:
            specific.append(w)
    for key, expanded in _TAG_EXPANSIONS.items():
        if key in topic.lower():
            specific.extend(expanded)

    trending = ["relationship psychology", "emotional intelligence",
                "attachment styles", "therapy tok", "dating red flags", "know your worth"]

    # Assemble: branded > specific > broad > trending, deduplicate
    pool = BRANDED_TAGS + specific + BROAD_TAGS + trending
    seen: set[str] = set()
    unique = []
    for tag in pool:
        k = tag.lower().strip()
        if k not in seen:
            seen.add(k); unique.append(tag.strip())

    selected, total_len = [], 0
    for tag in unique[:count]:
        addition = len(tag) + (2 if selected else 0)
        if total_len + addition > YOUTUBE_TAG_CHAR_LIMIT:
            break
        selected.append(tag); total_len += addition

    tag_string = ", ".join(selected)
    return {"tags": selected, "count": len(selected), "total_chars": len(tag_string),
            "char_limit": YOUTUBE_TAG_CHAR_LIMIT, "tag_string": tag_string}

# ===========================================================================
# Keyword Research
# ===========================================================================

def research_keywords(topic: str) -> Dict[str, Any]:
    """Scrape YouTube search suggestions and combine with ToxShield terms."""
    suggestions = _fetch_youtube_suggestions(topic)
    toxshield_terms = [
        f"{topic} toxicity score", f"{topic} analysis", f"is {topic} toxic",
        f"{topic} red flags", f"{topic} signs", f"how to deal with {topic}",
    ]
    seen: set[str] = set()
    merged = []
    for term in suggestions + toxshield_terms:
        k = term.lower().strip()
        if k and k not in seen:
            seen.add(k); merged.append(term.strip())
    return {"topic": topic, "youtube_suggestions": suggestions,
            "toxshield_terms": toxshield_terms, "combined": merged, "total": len(merged)}


def _fetch_youtube_suggestions(query: str) -> List[str]:
    """Fetch autocomplete suggestions from YouTube's suggest API."""
    url = YOUTUBE_SUGGEST_URL.format(query=urllib.parse.quote_plus(query))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
        match = re.search(r"\((.+)\)\s*$", raw, re.DOTALL)
        if not match:
            logger.warning("Could not parse YouTube suggest JSONP response"); return []
        data = json.loads(match.group(1))
        if isinstance(data, list) and len(data) > 1:
            return [item[0] for item in data[1] if isinstance(item, list)]
        return []
    except Exception as exc:
        logger.warning("YouTube suggest API failed: %s", exc); return []

# ===========================================================================
# Output Formatting
# ===========================================================================

def _fmt_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)

def _fmt_title_analysis(d: Dict[str, Any]) -> str:
    sep = "=" * 60
    lines = [sep, "  TITLE ANALYSIS", sep,
             f"  Title   : {d['title']}", f"  Length  : {d['length']} chars (optimal {d['optimal_range']})",
             f"  Score   : {d['score']}/100", f"  Format  : {'Shorts' if d.get('is_short') else 'Long-form'}"]
    if d.get("power_words_found"):
        lines.append(f"  Power   : {', '.join(d['power_words_found'])}")
    if d.get("emotional_triggers_found"):
        lines.append(f"  Triggers: {', '.join(d['emotional_triggers_found'])}")
    lines.append(f"  Number  : {'Yes' if d.get('has_number') else 'No'}")
    if d["deductions"]:
        lines.append("\n  Deductions:")
        lines.extend(f"    {x}" for x in d["deductions"])
    if d["suggestions"]:
        lines.append("\n  Suggestions:")
        lines.extend(f"    -> {x}" for x in d["suggestions"])
    lines.append(sep)
    return "\n".join(lines)

def _fmt_suggestions(items: List[Dict[str, str]]) -> str:
    sep = "=" * 60
    lines = [sep, "  TITLE SUGGESTIONS", sep]
    lines.extend(f"  {i}. [{s['template']}] {s['title']}" for i, s in enumerate(items, 1))
    lines.append(sep)
    return "\n".join(lines)

def _fmt_tags(d: Dict[str, Any]) -> str:
    sep = "=" * 60
    lines = [sep, "  TAG GENERATION", sep, f"  Count : {d['count']} tags",
             f"  Chars : {d['total_chars']}/{d['char_limit']}", "\n  Tags:"]
    lines.extend(f"    - {t}" for t in d["tags"])
    lines += ["\n  Copy-paste string:", f"    {d['tag_string']}", sep]
    return "\n".join(lines)

def _fmt_keywords(d: Dict[str, Any]) -> str:
    sep = "=" * 60
    lines = [sep, f"  KEYWORD RESEARCH: {d['topic']}", sep,
             f"  YouTube Suggestions ({len(d['youtube_suggestions'])}):"]
    lines.extend(f"    - {kw}" for kw in d["youtube_suggestions"])
    lines.append("\n  ToxShield Terms:")
    lines.extend(f"    - {kw}" for kw in d["toxshield_terms"])
    lines += [f"\n  Total combined: {d['total']}", sep]
    return "\n".join(lines)

# ===========================================================================
# CLI
# ===========================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ToxShield YouTube SEO metadata optimizer",
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--title", type=str, help="Analyze this title")
    p.add_argument("--suggest-titles", action="store_true", help="Generate title suggestions")
    p.add_argument("--generate-description", action="store_true", help="Generate a full description")
    p.add_argument("--generate-tags", action="store_true", help="Generate optimized tags")
    p.add_argument("--keywords", action="store_true", help="Research keywords via YouTube suggest")
    p.add_argument("--topic", type=str, help="Topic for suggestions/tags/keywords")
    p.add_argument("--content-type", type=str, choices=CONTENT_TYPES, help="Content type context")
    p.add_argument("--count", type=int, default=5, help="Number of results (default: 5)")
    p.add_argument("--long-form", action="store_true", help="Optimize for long-form (default: Shorts)")
    p.add_argument("--include-timestamps", action="store_true", help="Include timestamp placeholders")
    p.add_argument("--no-disclaimer", action="store_true", help="Omit safety disclaimer")
    p.add_argument("--output-format", choices=["text", "json"], default="text", help="Output format")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    as_json = args.output_format == "json"

    if args.title and not args.generate_description:
        result = analyze_title(args.title, args.content_type, is_short=not args.long_form)
        print(_fmt_json(result) if as_json else _fmt_title_analysis(result))

    elif args.suggest_titles:
        if not args.topic: parser.error("--suggest-titles requires --topic")
        items = suggest_titles(args.topic, count=args.count)
        print(_fmt_json(items) if as_json else _fmt_suggestions(items))

    elif args.generate_description:
        if not args.title: parser.error("--generate-description requires --title")
        desc = generate_description(args.title, args.topic, args.include_timestamps,
                                    include_disclaimer=not args.no_disclaimer)
        print(_fmt_json({"description": desc}) if as_json else desc)

    elif args.generate_tags:
        if not args.topic: parser.error("--generate-tags requires --topic")
        result = generate_tags(args.topic, count=args.count)
        print(_fmt_json(result) if as_json else _fmt_tags(result))

    elif args.keywords:
        if not args.topic: parser.error("--keywords requires --topic")
        result = research_keywords(args.topic)
        print(_fmt_json(result) if as_json else _fmt_keywords(result))

    else:
        parser.print_help(); sys.exit(1)


if __name__ == "__main__":
    main()
