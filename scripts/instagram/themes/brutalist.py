"""Brutalist theme — massive harsh typography, no decorations, raw and aggressive."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

# Run-level seed — set by generate_carousel.py for unique images each run
_RUN_SEED = 0

from PIL import Image, ImageDraw, ImageFont

from . import (
    FONT_SIZES, IMPACT_FONTS, ROUNDED_BODY_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

COLORS = {
    "bg":           (0, 0, 0),
    "text_primary": (255, 255, 255),
    "text_secondary": (200, 200, 200),
    "text_muted":   (80, 80, 80),
}

_FONT_SIZES = {**FONT_SIZES, "title": 120, "subtitle": 64, "body": 52, "small": 32, "tiny": 22}


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in IMPACT_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in ROUNDED_BODY_FONTS:
        if p.exists():
            fonts["body"] = fonts["small"] = str(p)
            if not fonts["headline"]:
                fonts["headline"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 28)
    font_path = fonts.get("headline") if size_key in ("title", "subtitle") else fonts.get("body")
    if font_path:
        try:
            idx = 2 if font_path.endswith(".ttc") and size_key in ("title", "subtitle") else 0
            return ImageFont.truetype(font_path, size, index=idx)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _rotate_text_block(text_img: Image.Image, seed: int) -> Image.Image:
    """Slightly rotate text for brutalist misalignment."""
    rng = random.Random(seed)
    angle = rng.uniform(-2.5, 2.5)
    return text_img.rotate(angle, expand=False, fillcolor=(0, 0, 0, 0), resample=Image.BICUBIC)


def render_title_slide(fonts, headline, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))

    headline = strip_emoji(headline).upper()
    font = _get_font(fonts, "title")
    max_w = width - 80  # Minimal margins — text bleeds to edges
    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 20)
    total_h = len(wrapped) * lh

    # Render text to separate layer for rotation
    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer, "RGBA")
    y = (height - total_h) // 2
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        text_draw.text((x, y), ln, fill=(*COLORS["text_primary"], 255), font=font)
        y += lh

    text_layer = _rotate_text_block(text_layer, slide_num + _RUN_SEED)
    img = Image.alpha_composite(img, text_layer)
    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))

    headline = strip_emoji(headline).upper() if headline else ""
    lines = [strip_emoji(line).upper() for line in lines]

    subtitle_font = _get_font(fonts, "subtitle")
    body_font = _get_font(fonts, "body")
    max_w = width - 100

    wrapped_hl = wrap_text(headline, subtitle_font, max_w) if headline else []
    hl_lh = line_height(subtitle_font, 16)

    body_wrapped = []
    for line in lines:
        for sub in line.split("\n"):
            body_wrapped.extend(wrap_text(sub, body_font, max_w))
    body_lh = line_height(body_font, 24)

    total_h = 0
    if wrapped_hl:
        total_h += len(wrapped_hl) * hl_lh + 30
    total_h += len(body_wrapped) * body_lh

    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer, "RGBA")
    y = (height - total_h) // 2

    if wrapped_hl:
        for ln in wrapped_hl:
            tw = text_width(ln, subtitle_font)
            x = (width - tw) // 2
            text_draw.text((x, y), ln, fill=(*COLORS["text_primary"], 255), font=subtitle_font)
            y += hl_lh
        y += 30

    for ln in body_wrapped:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2
        text_draw.text((x, y), ln, fill=(*COLORS["text_secondary"], 255), font=body_font)
        y += body_lh

    text_layer = _rotate_text_block(text_layer, slide_num + _RUN_SEED)
    img = Image.alpha_composite(img, text_layer)
    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))

    cta_text = strip_emoji(cta_text).upper()
    cta_font = _get_font(fonts, "subtitle")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 100

    wrapped = wrap_text(cta_text, cta_font, max_w)
    cta_lh = line_height(cta_font, 16)

    sub_lines = ["@TOXSHIELD.AI", "TOXSHIELD.IN"]
    sl_lh = line_height(small_font, 14)

    total_h = len(wrapped) * cta_lh + 50 + len(sub_lines) * sl_lh

    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer, "RGBA")
    y = (height - total_h) // 2

    for ln in wrapped:
        tw = text_width(ln, cta_font)
        x = (width - tw) // 2
        text_draw.text((x, y), ln, fill=(*COLORS["text_primary"], 255), font=cta_font)
        y += cta_lh

    y += 50
    for ln in sub_lines:
        tw = text_width(ln, small_font)
        x = (width - tw) // 2
        text_draw.text((x, y), ln, fill=(*COLORS["text_secondary"], 200), font=small_font)
        y += sl_lh

    text_layer = _rotate_text_block(text_layer, slide_num + _RUN_SEED)
    img = Image.alpha_composite(img, text_layer)

    # Disclaimer stays straight
    draw = ImageDraw.Draw(img, "RGBA")
    disclaimer_y = height - 120
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*COLORS["text_muted"], 160), font=tiny_font)
        disclaimer_y += 28

    return img.convert("RGB")
