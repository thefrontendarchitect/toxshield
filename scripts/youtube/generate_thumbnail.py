#!/usr/bin/env python3
"""
ToxShield YouTube thumbnail generator using Pillow.

Generates 1280x720 (16:9) click-optimized PNG thumbnails with neon accent
glow effects, text stroke outlines, and a face placeholder zone.

Styles:
    danger  — red accent (#e53e3e) for high-toxicity content (score 7+)
    warning — amber accent (#d69e2e) for moderate content / listicles
    toxic   — green accent (#00ff41) signature ToxShield neon
    versus  — split red/green for "Is this toxic?" comparisons
    score   — score-dependent color with arc ring visualization

Usage:
    python scripts/youtube/generate_thumbnail.py \
        --title "5 Signs You're Being Gaslighted" \
        --style danger --variants 2 \
        --output-dir output/youtube/thumbnails/

    python scripts/youtube/generate_thumbnail.py \
        --title "Toxicity Score: 8.5" --style score --score 8.5

    python scripts/youtube/generate_thumbnail.py \
        --title "Is This Toxic?" --subtitle "Your partner says..." --style versus
"""

from __future__ import annotations

import argparse
import logging
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# ===========================================================================
# Design Constants
# ===========================================================================

WIDTH = 1280
HEIGHT = 720

COLORS = {
    "bg":        (0, 0, 0),
    "white":     (255, 255, 255),
    "muted":     (80, 80, 80),
    # Accent palette (matches ToxShield design system)
    "danger":    (229, 62, 62),    # #e53e3e
    "warning":   (214, 158, 46),   # #d69e2e
    "toxic":     (0, 255, 65),     # #00ff41
    "safe":      (66, 153, 225),   # #4299e1
    "critical":  (213, 63, 140),   # #d53f8c
}

STYLE_ACCENTS = {
    "danger":  COLORS["danger"],
    "warning": COLORS["warning"],
    "toxic":   COLORS["toxic"],
    "versus":  COLORS["danger"],   # primary; green used as secondary
    "score":   COLORS["toxic"],    # overridden at runtime by score value
}

# Title text zone: left 55% of frame
TEXT_ZONE_RIGHT = int(WIDTH * 0.55)
TEXT_PADDING = 60

# Face placeholder: right 40% kept clear
FACE_ZONE_LEFT = int(WIDTH * 0.60)

_SANITIZE_RE = re.compile(r"[^a-zA-Z0-9_\- ]")


# ===========================================================================
# Font Loading
# ===========================================================================

def _find_font(candidates: List[Path]) -> Optional[str]:
    """Return the first existing font path from a list of candidates."""
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def load_title_font() -> Optional[str]:
    """Load a bold condensed font for thumbnail titles."""
    candidates = [
        # macOS system fonts (bold / condensed preferred)
        Path("/System/Library/Fonts/Supplemental/Impact.ttf"),
        Path("/Library/Fonts/Impact.ttf"),
        Path("/System/Library/Fonts/Supplemental/Futura.ttc"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/SFCompact.ttf"),
        # User fonts
        Path.home() / "Library/Fonts/Impact.ttf",
        Path.home() / "Library/Fonts/Futura-Bold.ttf",
        Path.home() / "Library/Fonts/Montserrat-ExtraBold.ttf",
        Path.home() / "Library/Fonts/Oswald-Bold.ttf",
        # Linux
        Path("/usr/share/fonts/truetype/msttcorefonts/Impact.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
    ]
    path = _find_font(candidates)
    if not path:
        logger.warning("No bold title font found, using Pillow default")
    return path


def load_mono_font() -> Optional[str]:
    """Load a monospace font for the watermark."""
    candidates = [
        Path("/System/Library/Fonts/Menlo.ttc"),
        Path("/System/Library/Fonts/SFMono-Regular.otf"),
        Path.home() / "Library/Fonts/JetBrainsMono-Regular.ttf",
        Path("/System/Library/Fonts/Supplemental/Courier New.ttf"),
        # Linux
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        Path("/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"),
    ]
    return _find_font(candidates)


def get_font(path: Optional[str], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    """Get a font at the given size, falling back to Pillow default."""
    if path:
        try:
            if path.endswith(".ttc"):
                return ImageFont.truetype(path, size, index=index)
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def compute_title_size(text: str) -> int:
    """Choose font size (80-120px) based on text length for best readability."""
    length = len(text)
    if length <= 20:
        return 120
    elif length <= 35:
        return 105
    elif length <= 50:
        return 90
    else:
        return 80


# ===========================================================================
# Text Utilities
# ===========================================================================

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines: List[str] = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines or [text]


def draw_text_with_stroke(
    draw: ImageDraw.Draw,
    xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, ...] = (255, 255, 255),
    stroke_width: int = 3,
    stroke_fill: Tuple[int, ...] = (0, 0, 0),
) -> None:
    """Draw text with a dark outline for readability over any background."""
    x, y = xy
    # Draw stroke by rendering text at offsets
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)


def sanitize_filename(text: str) -> str:
    """Convert title text to a safe filename slug."""
    slug = _SANITIZE_RE.sub("", text.lower().strip())
    slug = re.sub(r"\s+", "_", slug)
    return slug[:60] or "thumbnail"


# ===========================================================================
# Glow Effects
# ===========================================================================

def create_glow_layer(
    width: int,
    height: int,
    color: Tuple[int, int, int],
    regions: List[Tuple[int, int, int, int]],
    blur_radius: int = 30,
    opacity: int = 120,
) -> Image.Image:
    """Create a soft neon glow layer by drawing colored rectangles and blurring.

    Args:
        width: Canvas width.
        height: Canvas height.
        color: RGB accent color for the glow.
        regions: List of (x1, y1, x2, y2) rectangles to glow.
        blur_radius: Gaussian blur radius for softness.
        opacity: Max opacity of the glow (0-255).
    """
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for rect in regions:
        draw.rectangle(rect, fill=(*color, opacity))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return glow


# ===========================================================================
# Score Ring
# ===========================================================================

def score_to_color(score: float) -> Tuple[int, int, int]:
    """Map a toxicity score (0-10) to an accent color."""
    if score <= 3.0:
        return COLORS["safe"]       # blue
    elif score <= 6.0:
        return COLORS["warning"]    # amber
    elif score <= 8.0:
        return COLORS["danger"]     # red
    else:
        return COLORS["critical"]   # magenta


def draw_score_ring(
    img: Image.Image,
    score: float,
    center: Tuple[int, int],
    radius: int = 110,
    ring_width: int = 14,
    font_path: Optional[str] = None,
) -> None:
    """Draw a simplified score ring (arc) with the score number centered."""
    color = score_to_color(score)
    draw = ImageDraw.Draw(img)

    # Background circle (dim track)
    bbox = [
        center[0] - radius, center[1] - radius,
        center[0] + radius, center[1] + radius,
    ]
    draw.arc(bbox, start=0, end=360, fill=(*COLORS["muted"],), width=ring_width)

    # Score arc — sweep proportional to score/10 starting from top (-90 deg)
    sweep = (score / 10.0) * 360
    start_angle = -90
    end_angle = start_angle + sweep
    draw.arc(bbox, start=start_angle, end=end_angle, fill=color, width=ring_width)

    # Score number
    score_text = f"{score:.1f}" if score != int(score) else str(int(score))
    score_font = get_font(font_path, 72, index=2)
    text_bbox = score_font.getbbox(score_text)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]
    draw_text_with_stroke(
        draw,
        (center[0] - tw // 2, center[1] - th // 2 - 5),
        score_text,
        font=score_font,
        fill=color,
        stroke_width=2,
    )

    # "/10" label below
    label_font = get_font(font_path, 28)
    label = "/10"
    lb = label_font.getbbox(label)
    lw = lb[2] - lb[0]
    draw.text(
        (center[0] - lw // 2, center[1] + th // 2 + 5),
        label, font=label_font, fill=COLORS["muted"],
    )


# ===========================================================================
# Thumbnail Rendering — Variant A
# ===========================================================================

def render_variant_a(
    title: str,
    subtitle: Optional[str],
    style: str,
    accent: Tuple[int, int, int],
    title_font_path: Optional[str],
    mono_font_path: Optional[str],
    score: Optional[float] = None,
) -> Image.Image:
    """Variant A: Title left-aligned, accent color strip on left edge."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*COLORS["bg"], 255))

    # --- Accent strip on left edge ---
    strip_width = 12
    glow = create_glow_layer(
        WIDTH, HEIGHT, accent,
        regions=[(0, 0, strip_width, HEIGHT)],
        blur_radius=25, opacity=160,
    )
    img = Image.alpha_composite(img, glow)

    # Draw the solid strip on top of the glow
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (strip_width, HEIGHT)], fill=(*accent, 255))

    # --- Versus style: secondary green strip on right edge ---
    if style == "versus":
        green = COLORS["toxic"]
        glow_r = create_glow_layer(
            WIDTH, HEIGHT, green,
            regions=[(WIDTH - strip_width, 0, WIDTH, HEIGHT)],
            blur_radius=25, opacity=160,
        )
        img = Image.alpha_composite(img, glow_r)
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [(WIDTH - strip_width, 0), (WIDTH, HEIGHT)],
            fill=(*green, 255),
        )

    # --- Title text ---
    draw = ImageDraw.Draw(img)
    font_size = compute_title_size(title)
    title_font = get_font(title_font_path, font_size, index=2)
    max_text_w = TEXT_ZONE_RIGHT - TEXT_PADDING * 2

    lines = wrap_text(title.upper(), title_font, max_text_w)
    line_height = title_font.getbbox("Ag")[3] - title_font.getbbox("Ag")[1] + 12
    total_h = len(lines) * line_height

    y_start = (HEIGHT - total_h) // 2
    if subtitle:
        y_start -= 25  # shift up to make room

    for line in lines:
        draw_text_with_stroke(
            draw, (TEXT_PADDING + strip_width + 10, y_start),
            line, font=title_font, fill=COLORS["white"], stroke_width=3,
        )
        y_start += line_height

    # --- Subtitle ---
    if subtitle:
        sub_font = get_font(title_font_path, 36)
        y_start += 10
        draw_text_with_stroke(
            draw, (TEXT_PADDING + strip_width + 10, y_start),
            subtitle, font=sub_font, fill=(*accent,), stroke_width=2,
        )

    # --- Score ring (score mode only) ---
    if style == "score" and score is not None:
        ring_center = (FACE_ZONE_LEFT + (WIDTH - FACE_ZONE_LEFT) // 2, HEIGHT // 2)
        draw_score_ring(img, score, ring_center, font_path=title_font_path)

    # --- Watermark ---
    _draw_watermark(ImageDraw.Draw(img), mono_font_path)

    return img.convert("RGB")


# ===========================================================================
# Thumbnail Rendering — Variant B
# ===========================================================================

def render_variant_b(
    title: str,
    subtitle: Optional[str],
    style: str,
    accent: Tuple[int, int, int],
    title_font_path: Optional[str],
    mono_font_path: Optional[str],
    score: Optional[float] = None,
) -> Image.Image:
    """Variant B: Title with keyword highlight, accent glow at bottom."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*COLORS["bg"], 255))

    # --- Bottom glow bar ---
    bar_height = 8
    glow = create_glow_layer(
        WIDTH, HEIGHT, accent,
        regions=[(0, HEIGHT - bar_height, WIDTH, HEIGHT)],
        blur_radius=35, opacity=140,
    )
    img = Image.alpha_composite(img, glow)

    # Solid bar
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        [(0, HEIGHT - bar_height), (WIDTH, HEIGHT)],
        fill=(*accent, 255),
    )

    # --- Subtle glow behind text area ---
    text_glow = create_glow_layer(
        WIDTH, HEIGHT, accent,
        regions=[(TEXT_PADDING, HEIGHT // 4, TEXT_ZONE_RIGHT, HEIGHT * 3 // 4)],
        blur_radius=60, opacity=40,
    )
    img = Image.alpha_composite(img, text_glow)

    # --- Title with keyword highlight ---
    draw = ImageDraw.Draw(img)
    font_size = compute_title_size(title)
    title_font = get_font(title_font_path, font_size, index=2)
    max_text_w = TEXT_ZONE_RIGHT - TEXT_PADDING * 2

    words = title.upper().split()
    # Highlight the longest word as the "keyword"
    keyword = max(words, key=len) if words else ""

    full_lines = wrap_text(title.upper(), title_font, max_text_w)
    line_height = title_font.getbbox("Ag")[3] - title_font.getbbox("Ag")[1] + 12
    total_h = len(full_lines) * line_height

    y_start = (HEIGHT - total_h) // 2
    if subtitle:
        y_start -= 25

    for line in full_lines:
        x_pos = TEXT_PADDING
        # Split line into segments to colorize the keyword
        remaining = line
        while remaining:
            kw_upper = keyword.upper()
            idx = remaining.upper().find(kw_upper)
            if idx == -1:
                # No keyword in this segment — draw in white
                draw_text_with_stroke(
                    draw, (x_pos, y_start), remaining,
                    font=title_font, fill=COLORS["white"], stroke_width=3,
                )
                break
            else:
                # Draw prefix in white
                prefix = remaining[:idx]
                if prefix:
                    draw_text_with_stroke(
                        draw, (x_pos, y_start), prefix,
                        font=title_font, fill=COLORS["white"], stroke_width=3,
                    )
                    pw = title_font.getbbox(prefix)[2] - title_font.getbbox(prefix)[0]
                    x_pos += pw

                # Draw keyword in accent color
                kw_segment = remaining[idx:idx + len(kw_upper)]
                draw_text_with_stroke(
                    draw, (x_pos, y_start), kw_segment,
                    font=title_font, fill=accent, stroke_width=3,
                    stroke_fill=(0, 0, 0),
                )
                kw_w = title_font.getbbox(kw_segment)[2] - title_font.getbbox(kw_segment)[0]
                x_pos += kw_w
                remaining = remaining[idx + len(kw_upper):]
        y_start += line_height

    # --- Subtitle ---
    if subtitle:
        sub_font = get_font(title_font_path, 36)
        y_start += 10
        draw_text_with_stroke(
            draw, (TEXT_PADDING, y_start),
            subtitle, font=sub_font, fill=(*accent,), stroke_width=2,
        )

    # --- Score ring (score mode only) ---
    if style == "score" and score is not None:
        ring_center = (FACE_ZONE_LEFT + (WIDTH - FACE_ZONE_LEFT) // 2, HEIGHT // 2)
        draw_score_ring(img, score, ring_center, font_path=title_font_path)

    # --- Watermark ---
    _draw_watermark(ImageDraw.Draw(img), mono_font_path)

    return img.convert("RGB")


# ===========================================================================
# Watermark
# ===========================================================================

def _draw_watermark(draw: ImageDraw.Draw, mono_font_path: Optional[str]) -> None:
    """Draw muted 'TOXSHIELD' monospace watermark in the bottom-right corner."""
    wm_font = get_font(mono_font_path, 16)
    wm_text = "TOXSHIELD"
    bbox = wm_font.getbbox(wm_text)
    tw = bbox[2] - bbox[0]
    x = WIDTH - tw - 20
    y = HEIGHT - 30
    draw.text((x, y), wm_text, font=wm_font, fill=COLORS["muted"])


# ===========================================================================
# Thumbnail Generation Pipeline
# ===========================================================================

def resolve_accent(style: str, score: Optional[float]) -> Tuple[int, int, int]:
    """Resolve the accent color based on style and optional score."""
    if style == "score" and score is not None:
        return score_to_color(score)
    return STYLE_ACCENTS.get(style, COLORS["toxic"])


def generate_thumbnail(
    title: str,
    style: str = "toxic",
    subtitle: Optional[str] = None,
    score: Optional[float] = None,
    variants: int = 1,
    output_dir: str = "",
) -> List[str]:
    """Generate one or two thumbnail variants and save as PNG.

    Args:
        title: Main title text.
        style: Visual style (danger, warning, toxic, versus, score).
        subtitle: Optional subtitle line.
        score: Toxicity score (0-10) for 'score' style.
        variants: Number of variants (1 = A only, 2 = A + B).
        output_dir: Output directory path.

    Returns:
        List of saved file paths.
    """
    if not PILLOW_AVAILABLE:
        print("Error: Pillow not installed. Run: pip install Pillow>=10.2.0", file=sys.stderr)
        sys.exit(1)

    accent = resolve_accent(style, score)
    title_font_path = load_title_font()
    mono_font_path = load_mono_font()

    out = Path(output_dir or str(PROJECT_ROOT / "output" / "youtube" / "thumbnails"))
    out.mkdir(parents=True, exist_ok=True)

    slug = sanitize_filename(title)
    renderers = [render_variant_a, render_variant_b]
    labels = ["A", "B"]
    paths: List[str] = []

    for i in range(min(variants, 2)):
        logger.info(f"Rendering variant {labels[i]} ({style} style)...")
        img = renderers[i](
            title=title,
            subtitle=subtitle,
            style=style,
            accent=accent,
            title_font_path=title_font_path,
            mono_font_path=mono_font_path,
            score=score,
        )
        filename = f"{slug}_{labels[i]}.png"
        filepath = out / filename
        img.save(str(filepath), "PNG", quality=95)
        paths.append(str(filepath))
        logger.info(f"Saved: {filepath} ({WIDTH}x{HEIGHT})")

    return paths


# ===========================================================================
# CLI
# ===========================================================================

VALID_STYLES = ["danger", "warning", "toxic", "versus", "score"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate click-optimized YouTube thumbnails for ToxShield",
    )
    parser.add_argument(
        "--title", "-t", required=True,
        help="Main title text for the thumbnail",
    )
    parser.add_argument(
        "--subtitle", "-s", default=None,
        help="Optional subtitle line below the title",
    )
    parser.add_argument(
        "--style", choices=VALID_STYLES, default="toxic",
        help="Visual style / accent color theme (default: toxic)",
    )
    parser.add_argument(
        "--score", type=float, default=None,
        help="Toxicity score 0-10 (used with --style score)",
    )
    parser.add_argument(
        "--variants", type=int, default=1, choices=[1, 2],
        help="Number of A/B variants to generate (default: 1)",
    )
    parser.add_argument(
        "--output-dir", "-o", default="",
        help="Output directory (default: output/youtube/thumbnails/)",
    )

    args = parser.parse_args()

    if args.style == "score" and args.score is None:
        parser.error("--score is required when using --style score")
    if args.score is not None and not (0 <= args.score <= 10):
        parser.error("--score must be between 0 and 10")

    paths = generate_thumbnail(
        title=args.title,
        style=args.style,
        subtitle=args.subtitle,
        score=args.score,
        variants=args.variants,
        output_dir=args.output_dir,
    )

    print(f"\nGenerated {len(paths)} thumbnail(s):")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
