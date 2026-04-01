"""Meme Classic theme — black background, white text, nothing else.

The #1 most viral meme format. Looks like it was made in 30 seconds.
Used for: "my toxic trait is...", dark humor, uncomfortable truths.
NO decorations, NO branding on content slides. Just text.
"""

from __future__ import annotations

import random as _random
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from . import (
    FONT_SIZES, ROUNDED_FONTS, ROUNDED_BODY_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

_RUN_SEED = 0

_FONT_SIZES = {
    "hook": 72,
    "body": 58,
    "small": 38,
    "tiny": 22,
}

_BG = (0, 0, 0)
_TEXT = (255, 255, 255)
_TEXT_DIM = (170, 170, 170)
_TEXT_MUTED = (90, 90, 90)


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    # Prefer clean sans-serif (Arial/Helvetica/Avenir), NOT Impact
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
    size = _FONT_SIZES.get(size_key, 48)
    font_path = fonts.get("headline") if size_key == "hook" else (fonts.get("body") or fonts.get("headline"))
    idx = 2 if (font_path and font_path.endswith(".ttc") and size_key == "hook") else 0
    if font_path:
        try:
            if font_path.endswith(".ttc"):
                return ImageFont.truetype(font_path, size, index=idx)
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def render_title_slide(fonts, headline, slide_num, width, height):
    """Hook slide — just text on black. Could be 'my toxic trait is...' or 'nobody:'"""
    img = Image.new("RGB", (width, height), _BG)
    draw = ImageDraw.Draw(img)

    headline = strip_emoji(headline)
    font = _get_font(fonts, "hook")
    max_w = width - 160

    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 24)
    total_h = len(wrapped) * lh

    # Center vertically
    y = (height - total_h) // 2
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=_TEXT, font=font)
        y += lh

    return img


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    """One punchline per slide. Clean, centered, no distractions."""
    img = Image.new("RGB", (width, height), _BG)
    draw = ImageDraw.Draw(img)

    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    body_font = _get_font(fonts, "body")
    max_w = width - 160

    # Combine all text
    all_text = []
    if headline:
        all_text.append(headline)
    all_text.extend(lines)
    full_text = " ".join(all_text)

    wrapped = wrap_text(full_text, body_font, max_w)
    lh = line_height(body_font, 22)
    total_h = len(wrapped) * lh

    y = (height - total_h) // 2
    for ln in wrapped:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=_TEXT, font=body_font)
        y += lh

    return img


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    """CTA slide — still minimal but with branding."""
    img = Image.new("RGB", (width, height), _BG)
    draw = ImageDraw.Draw(img)

    cta_text = strip_emoji(cta_text)
    body_font = _get_font(fonts, "body")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 160

    # CTA text
    wrapped = wrap_text(cta_text, body_font, max_w)
    lh = line_height(body_font, 20)
    total_h = len(wrapped) * lh

    y = (height - total_h) // 2 - 80
    for ln in wrapped:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=_TEXT, font=body_font)
        y += lh

    # Handle
    y += 50
    handle = "@toxshield.ai"
    hw = text_width(handle, small_font)
    draw.text(((width - hw) // 2, y), handle, fill=_TEXT_DIM, font=small_font)

    # Disclaimer at bottom
    disc_y = height - 110
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        dw = text_width(disc_line, tiny_font)
        draw.text(((width - dw) // 2, disc_y), disc_line,
                  fill=_TEXT_MUTED, font=tiny_font)
        disc_y += 26

    return img
