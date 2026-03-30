#!/usr/bin/env python3
"""
ToxShield Instagram carousel image generator with theme support.

Supports multiple visual themes: arcane (default), doodle, neon-terminal, forensic,
brutalist, glitch, surveillance, pastel-soft.

Usage:
    python scripts/instagram/generate_carousel.py \
        --headline "They're not 'brutally honest.' They're just brutal." \
        --body "Gaslighting disguised as feedback" "The DARVO pattern explained" \
        --cta "Save this for when you need the reminder" \
        --slides 7

    # With a different theme
    python scripts/instagram/generate_carousel.py --theme neon-terminal \
        --headline "Pattern Detected." --body "Line 1" "Line 2" --slides 5

    python scripts/instagram/generate_carousel.py --json-file content_data.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Ensure themes package is importable
_scripts_dir = str(Path(__file__).parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from themes import AVAILABLE_THEMES, get_theme  # noqa: E402

# ===========================================================================
# Constants
# ===========================================================================

WIDTH = 1080
HEIGHT = 1350  # 4:5 portrait (default, overridden by --aspect-ratio)

ASPECT_RATIOS = {
    "4:5": 1350,
    "9:16": 1920,
}

CONTENT_TYPES = [
    "toxic_callout", "is_this_toxic", "score_reveal", "protection_tip",
    "pattern_breakdown", "self_check", "meme_relatable", "app_showcase",
    "testimonial", "edu_deep_dive",
]

# ===========================================================================
# Backward-compatible re-exports (used by generate_longform.py, generate_dp.py)
# ===========================================================================

# Lazy-load doodle theme for backward compat — these are accessed by external scripts
def _get_doodle():
    return get_theme("doodle")

# Re-export constants from doodle theme
from themes.doodle import COLORS, _DOODLE_FUNCS  # noqa: E402, F401
from themes import FONT_SIZES, SAFETY_DISCLAIMER, strip_emoji, wrap_text  # noqa: E402, F401


def load_fonts():
    """Backward-compatible: load doodle theme fonts."""
    return _get_doodle().load_fonts()


def get_font(fonts, size_key):
    """Backward-compatible: get doodle theme font."""
    return _get_doodle().get_font(fonts, size_key)


def draw_doodles(draw, seed=0, count=14, bottom_margin=160):
    """Backward-compatible: draw doodles using module-level WIDTH/HEIGHT."""
    _get_doodle().draw_doodles(draw, WIDTH, HEIGHT, seed=seed, count=count, bottom_margin=bottom_margin)


def draw_background(img):
    """Backward-compatible: fill with doodle theme background."""
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (WIDTH, HEIGHT)], fill=(*COLORS["bg"], 255))


def render_title_slide(fonts, headline, slide_num=1):
    """Backward-compatible wrapper using module-level WIDTH/HEIGHT."""
    return _get_doodle().render_title_slide(fonts, headline, slide_num, WIDTH, HEIGHT)


def render_content_slide(fonts, headline, lines, slide_num):
    """Backward-compatible wrapper using module-level WIDTH/HEIGHT."""
    return _get_doodle().render_content_slide(fonts, headline, lines, slide_num, WIDTH, HEIGHT)


def render_cta_slide(fonts, cta_text, slide_num, include_disclaimer=True):
    """Backward-compatible wrapper using module-level WIDTH/HEIGHT."""
    return _get_doodle().render_cta_slide(fonts, cta_text, slide_num, WIDTH, HEIGHT)


# ===========================================================================
# Carousel Generation
# ===========================================================================

def build_slides(content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    slides = []
    headline = content_data.get("headline", "")
    body = content_data.get("body", [])
    cta = content_data.get("cta", "Save this for when you need it")
    adaptations = content_data.get("format_adaptations", {})
    num_slides = adaptations.get("carousel_slides", len(body) + 2)
    num_slides = max(5, min(num_slides, 10))

    slides.append({"type": "title", "headline": headline})

    for i in range(2, num_slides):
        lines_key = f"slide_{i}_lines"
        title_key = f"slide_{i}_title"
        slide_key = f"slide_{i}"
        slide_title = adaptations.get(title_key, "")

        if lines_key in adaptations:
            slide_lines = adaptations[lines_key]
            if isinstance(slide_lines, str):
                slide_lines = [slide_lines]
            slides.append({"type": "content", "headline": slide_title, "lines": slide_lines})
        elif slide_key in adaptations:
            slides.append({"type": "content", "headline": slide_title, "lines": [adaptations[slide_key]]})
        elif i - 2 < len(body):
            slides.append({"type": "content", "headline": slide_title, "lines": [body[i - 2]]})
        else:
            slides.append({"type": "content", "headline": "", "lines": ["Protect your peace."]})

    slides.append({"type": "cta", "headline": cta})
    return slides[:num_slides]


def generate_carousel(
    content_data: Dict[str, Any],
    content_type: str = "custom",
    date_str: str = "manual",
    output_dir: str = "",
    aspect_ratio: str = "4:5",
    subdir: str = "",
    theme_name: str = "arcane",
    seed: int | None = None,
) -> List[str]:
    global HEIGHT
    if not PILLOW_AVAILABLE:
        print("Error: Pillow not installed. Run: pip install Pillow>=10.2.0", file=sys.stderr)
        sys.exit(1)

    HEIGHT = ASPECT_RATIOS.get(aspect_ratio, 1350)
    logger.info(f"Canvas: {WIDTH}x{HEIGHT} (aspect ratio: {aspect_ratio})")

    theme = get_theme(theme_name)
    fonts = theme.load_fonts()

    # Set run-level seed for unique images each run
    run_seed = seed if seed is not None else int(time.time())
    theme._RUN_SEED = run_seed
    logger.info(f"Seed: {run_seed} (use --seed {run_seed} to reproduce)")
    slides = build_slides(content_data)

    logger.info(f"Theme: {theme_name} | Slides: {len(slides)}")

    out_dir = Path(output_dir or str(PROJECT_ROOT / "output" / "instagram")) / date_str / content_type
    if subdir:
        out_dir = out_dir / subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save content data so narration generator can use --content-file for exact slide matching
    content_json_path = out_dir / "content.json"
    with open(content_json_path, "w") as f:
        json.dump(content_data, f, indent=2)
    logger.info(f"Saved content data: {content_json_path}")

    paths = []
    for i, slide in enumerate(slides):
        slide_num = i + 1
        slide_type = slide.get("type", "content")

        if slide_type == "title":
            img = theme.render_title_slide(fonts, slide["headline"], slide_num, WIDTH, HEIGHT)
        elif slide_type == "cta":
            img = theme.render_cta_slide(fonts, slide["headline"], slide_num, WIDTH, HEIGHT)
        else:
            img = theme.render_content_slide(
                fonts, slide.get("headline", ""), slide.get("lines", []), slide_num, WIDTH, HEIGHT,
            )

        path = out_dir / f"slide_{slide_num:02d}.png"
        img.save(str(path), "PNG", quality=95)
        paths.append(str(path))
        logger.info(f"Generated slide {slide_num}/{len(slides)}: {path}")

    return paths


# ===========================================================================
# CLI
# ===========================================================================

def build_template_content(args) -> Dict[str, Any]:
    body = args.body or ["Protect your peace."]
    num_slides = args.slides or (len(body) + 2)
    format_adaptations = {"carousel_slides": num_slides}
    for i, line in enumerate(body):
        format_adaptations[f"slide_{i + 2}"] = line
    return {
        "headline": args.headline or "Pattern Detected.",
        "body": body,
        "cta": args.cta or "Save this for when you need it",
        "format_adaptations": format_adaptations,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Instagram carousel images for ToxShield")
    parser.add_argument("--content-type", "-t", choices=CONTENT_TYPES + ["custom"], default="custom")
    parser.add_argument("--date", "-d", help="Content date (YYYY-MM-DD)")
    parser.add_argument("--json-file", "-j", help="JSON file with content data")
    parser.add_argument("--headline", help="Headline text (scroll-stopping hook)")
    parser.add_argument("--body", nargs="+", help="Body text lines (one per slide)")
    parser.add_argument("--cta", help="Call-to-action text for final slide")
    parser.add_argument("--slides", type=int, help="Number of slides (3-10)")
    parser.add_argument("--aspect-ratio", "-a", choices=["4:5", "9:16"], default="4:5",
                        help="Aspect ratio: 4:5 for carousels (1080x1350), 9:16 for Reels (1080x1920)")
    parser.add_argument("--theme", choices=AVAILABLE_THEMES, default="arcane",
                        help=f"Visual theme (default: arcane). Options: {', '.join(AVAILABLE_THEMES)}")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible output. Omit for unique images each run.")
    parser.add_argument("--output-dir", "-o", default=str(PROJECT_ROOT / "output" / "instagram"))
    parser.add_argument("--subdir", help="Subdirectory under content type (e.g., 'carousel' or 'reel')")

    args = parser.parse_args()

    content_data = None
    if args.json_file:
        with open(args.json_file) as f:
            content_data = json.load(f)
    elif args.headline:
        content_data = build_template_content(args)
    else:
        parser.error("Provide --headline or --json-file")

    if content_data is None:
        content_data = build_template_content(args)

    paths = generate_carousel(
        content_data=content_data,
        content_type=args.content_type or "custom",
        date_str=args.date or "manual",
        output_dir=args.output_dir,
        aspect_ratio=args.aspect_ratio,
        subdir=args.subdir or "",
        theme_name=args.theme,
        seed=args.seed,
    )

    print(f"\nGenerated {len(paths)} carousel slides:")
    for p in paths:
        print(f"  {p}")
    print(f"\n{json.dumps({'slides': paths, 'count': len(paths)})}")


if __name__ == "__main__":
    main()
