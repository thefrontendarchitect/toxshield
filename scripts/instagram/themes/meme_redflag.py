"""Meme Red Flag theme — statement + red flag emoji flood.

The viral red flag meme format: a statement about a behavior,
followed by rows and rows of red flag symbols.
Simple, instantly recognizable, massively shareable.
"""

from __future__ import annotations

import math
import random as _random
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from . import (
    FONT_SIZES, ROUNDED_FONTS, ROUNDED_BODY_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

_RUN_SEED = 0

_FONT_SIZES = {
    "statement": 52,
    "body": 48,
    "label": 28,
    "small": 30,
    "tiny": 20,
}

_BG = (255, 255, 255)
_TEXT = (0, 0, 0)
_TEXT_DIM = (120, 120, 120)
_TEXT_MUTED = (180, 180, 180)
_RED = (255, 0, 0)
_GREEN = (34, 170, 68)
_FLAG_RED = (220, 38, 38)
_FLAG_GREEN = (22, 163, 74)
_FLAG_POLE = (80, 80, 80)


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in ROUNDED_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in ROUNDED_BODY_FONTS:
        if p.exists():
            fonts["body"] = fonts["small"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 36)
    font_path = fonts.get("headline") if size_key == "statement" else (fonts.get("body") or fonts.get("headline"))
    idx = 2 if (font_path and font_path.endswith(".ttc") and size_key == "statement") else 0
    if font_path:
        try:
            if font_path.endswith(".ttc"):
                return ImageFont.truetype(font_path, size, index=idx)
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Red/Green flag drawing
# ---------------------------------------------------------------------------

def _draw_flag(draw: ImageDraw.Draw, x: int, y: int, size: int,
               color: tuple, angle_deg: float = 0):
    """Draw a simple flag shape: pole + triangular flag."""
    pole_w = max(2, size // 12)
    pole_h = size
    flag_w = int(size * 0.7)
    flag_h = int(size * 0.45)

    rng = _random.Random(int(x * 1000 + y))

    # Pole
    px = x + size // 4
    draw.line([(px, y + 2), (px, y + pole_h)], fill=_FLAG_POLE, width=pole_w)

    # Flag (triangle/pennant shape)
    flag_points = [
        (px + 1, y + 2),                          # top-left (at pole)
        (px + flag_w, y + flag_h // 2 + 2),       # right point
        (px + 1, y + flag_h + 2),                  # bottom-left (at pole)
    ]
    draw.polygon(flag_points, fill=color)


def _draw_flag_grid(draw: ImageDraw.Draw, x_start: int, y_start: int,
                    width: int, height: int, flag_size: int = 48,
                    color: tuple = None, density: float = 1.0):
    """Fill an area with a grid of flags."""
    if color is None:
        color = _FLAG_RED

    gap_x = flag_size + 8
    gap_y = flag_size + 6
    rng = _random.Random(_RUN_SEED + int(y_start))

    cols = max(1, (width - 20) // gap_x)
    rows = max(1, (height - 10) // gap_y)

    for row in range(rows):
        for col in range(cols):
            if rng.random() > density:
                continue
            fx = x_start + 10 + col * gap_x + rng.randint(-3, 3)
            fy = y_start + 5 + row * gap_y + rng.randint(-2, 2)
            angle = rng.uniform(-5, 5)
            _draw_flag(draw, fx, fy, flag_size, color, angle)


def _detect_flag_type(text: str) -> str:
    """Detect if the text is about a red flag or green flag."""
    lower = text.lower()
    if "green flag" in lower or "good sign" in lower:
        return "green"
    return "red"


# ===========================================================================
# Slide Rendering
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    """Hook slide — the question or setup."""
    img = Image.new("RGB", (width, height), _BG)
    draw = ImageDraw.Draw(img)

    headline = strip_emoji(headline)
    font = _get_font(fonts, "statement")
    max_w = width - 120

    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 20)
    total_h = len(wrapped) * lh

    # Text in upper third
    y = height // 3 - total_h // 2
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=_TEXT, font=font)
        y += lh

    # Scattered flags below as decoration
    flag_zone_y = y + 60
    flag_zone_h = height - flag_zone_y - 40
    if flag_zone_h > 80:
        _draw_flag_grid(draw, 40, flag_zone_y, width - 80, flag_zone_h,
                       flag_size=44, density=0.6)

    return img


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    """Statement at top + flag flood below."""
    img = Image.new("RGB", (width, height), _BG)
    draw = ImageDraw.Draw(img)

    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    # Combine into statement
    statement_parts = []
    if headline:
        statement_parts.append(headline)
    statement_parts.extend(lines)
    statement = " ".join(statement_parts)

    # Detect flag type
    flag_type = _detect_flag_type(statement)
    flag_color = _FLAG_GREEN if flag_type == "green" else _FLAG_RED

    # Render statement text (top ~35%)
    font = _get_font(fonts, "statement")
    max_w = width - 120

    wrapped = wrap_text(statement, font, max_w)
    lh = line_height(font, 18)

    text_y = 80
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, text_y), ln, fill=_TEXT, font=font)
        text_y += lh

    # Flag flood below (remaining space)
    flag_zone_y = text_y + 50
    flag_zone_h = height - flag_zone_y - 30
    if flag_zone_h > 60:
        _draw_flag_grid(draw, 30, flag_zone_y, width - 60, flag_zone_h,
                       flag_size=46, color=flag_color, density=0.92)

    return img


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    """CTA with minimal flags and branding."""
    img = Image.new("RGB", (width, height), _BG)
    draw = ImageDraw.Draw(img)

    cta_text = strip_emoji(cta_text)
    font = _get_font(fonts, "body")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 140

    # Some flags at top
    _draw_flag_grid(draw, 40, 40, width - 80, 200,
                   flag_size=40, density=0.4)

    # CTA text centered
    wrapped = wrap_text(cta_text, font, max_w)
    lh = line_height(font, 16)
    total_h = len(wrapped) * lh

    y = (height - total_h) // 2 - 40
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=_TEXT, font=font)
        y += lh

    # Branding
    y += 40
    handle = "@toxshield.ai"
    hw = text_width(handle, small_font)
    draw.text(((width - hw) // 2, y), handle, fill=_TEXT_DIM, font=small_font)

    y += 50
    site = "toxshield.in"
    sw = text_width(site, small_font)
    draw.text(((width - sw) // 2, y), site, fill=_TEXT_DIM, font=small_font)

    # Flags at bottom
    _draw_flag_grid(draw, 40, height - 220, width - 80, 180,
                   flag_size=40, density=0.4)

    # Disclaimer
    disc_y = height - 90
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        dw = text_width(disc_line, tiny_font)
        draw.text(((width - dw) // 2, disc_y), disc_line,
                  fill=_TEXT_MUTED, font=tiny_font)
        disc_y += 24

    return img
