"""Unhinged Text theme — deep-fried shitpost / 3am rage-post aesthetic.

Intentionally ugly, raw, and chaotic. Aggressive solid color backgrounds,
JPEG compression artifacts, over-sharpened text, red circle overlays,
and deliberately off-center positioning. The anti-aesthetic that gets
screenshotted and shared in group chats.
"""

from __future__ import annotations

import random as _random
from io import BytesIO
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from . import (
    FONT_SIZES, IMPACT_FONTS, ROUNDED_BODY_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_RUN_SEED = 0

_FONT_SIZES = {
    "title": 96,
    "subtitle": 64,
    "body": 56,
    "small": 38,
    "tiny": 24,
    "nobody": 48,
}

# Aggressive color rotation — each slide gets a different bg
_COLOR_ROTATION = [
    {"bg": (255, 20, 147),  "text": (0, 0, 0),       "name": "hot_pink"},      # #FF1493
    {"bg": (255, 225, 0),   "text": (0, 0, 0),       "name": "electric_yellow"},# #FFE100
    {"bg": (57, 255, 20),   "text": (0, 0, 0),       "name": "toxic_green"},    # #39FF14
    {"bg": (255, 255, 255), "text": (220, 20, 20),    "name": "white_rage"},     # white + red text
    {"bg": (0, 0, 0),       "text": (255, 255, 255),  "name": "void_black"},     # black + white
    {"bg": (255, 100, 0),   "text": (0, 0, 0),       "name": "danger_orange"},  # #FF6400
]

# Red overlay elements
_RED = (255, 20, 20, 200)


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in IMPACT_FONTS:
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
    if size_key in ("title", "subtitle"):
        font_path = fonts.get("headline")
    else:
        font_path = fonts.get("body") or fonts.get("small")
    if font_path:
        try:
            if font_path.endswith(".ttc"):
                return ImageFont.truetype(font_path, size, index=0)
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Deep-fry effect
# ---------------------------------------------------------------------------

def _deep_fry(img: Image.Image, intensity: float = 1.0) -> Image.Image:
    """Apply deep-fry effect: JPEG artifacts + over-sharpen + contrast boost."""
    rgb = img.convert("RGB")

    # JPEG round-trip at very low quality for compression artifacts
    quality = max(2, int(8 - intensity * 5))
    buf = BytesIO()
    rgb.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    fried = Image.open(buf).copy()

    # Over-sharpen
    sharpen_passes = int(2 + intensity * 3)
    for _ in range(sharpen_passes):
        fried = fried.filter(ImageFilter.SHARPEN)

    # Boost contrast and color saturation
    fried = ImageEnhance.Contrast(fried).enhance(1.0 + intensity * 0.4)
    fried = ImageEnhance.Color(fried).enhance(1.0 + intensity * 0.5)

    return fried.convert("RGBA")


# ---------------------------------------------------------------------------
# Red circle / arrow overlays
# ---------------------------------------------------------------------------

def _draw_red_overlays(draw: ImageDraw.Draw, width: int, height: int, rng: _random.Random,
                       count: int = 2):
    """Draw crude red circles and arrows pointing at random areas."""
    for _ in range(count):
        kind = rng.random()
        if kind < 0.6:
            # Red circle
            cx = rng.randint(width // 4, 3 * width // 4)
            cy = rng.randint(height // 4, 3 * height // 4)
            rx = rng.randint(60, 140)
            ry = rng.randint(50, 120)
            thickness = rng.randint(4, 8)
            draw.ellipse(
                [cx - rx, cy - ry, cx + rx, cy + ry],
                outline=_RED, width=thickness,
            )
        else:
            # Red arrow
            x1 = rng.randint(width // 6, width // 2)
            y1 = rng.randint(height // 6, height // 2)
            x2 = x1 + rng.randint(80, 200)
            y2 = y1 + rng.randint(60, 150)
            draw.line([(x1, y1), (x2, y2)], fill=_RED, width=rng.randint(4, 7))
            # Arrow head
            draw.polygon([
                (x2, y2),
                (x2 - 20, y2 - 15),
                (x2 - 15, y2 + 10),
            ], fill=_RED)


# ---------------------------------------------------------------------------
# Slide helpers
# ---------------------------------------------------------------------------

def _get_palette(slide_num: int) -> dict:
    return _COLOR_ROTATION[(slide_num - 1) % len(_COLOR_ROTATION)]


def _render_text_block(
    img: Image.Image, draw: ImageDraw.Draw, fonts: Dict,
    text: str, width: int, height: int, slide_num: int,
    font_key: str = "body",
) -> Image.Image:
    """Render text deliberately off-center with chaotic energy."""
    rng = _random.Random(slide_num * 777 + _RUN_SEED)
    pal = _get_palette(slide_num)
    text_color = (*pal["text"], 255)

    font = _get_font(fonts, font_key)
    max_w = width - 120  # tight margins

    wrapped = wrap_text(text, font, max_w)
    lh = line_height(font, 18)
    total_h = len(wrapped) * lh

    # Deliberately off-center
    offset_x = rng.randint(-35, 35)
    offset_y = rng.randint(-30, 30)
    base_y = (height - total_h) // 2 + offset_y

    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2 + offset_x
        draw.text((x, base_y), ln, fill=text_color, font=font)
        base_y += lh

    return img


# ===========================================================================
# Slide Rendering (standard theme API)
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    """Solid color background + massive text + deep-fry."""
    rng = _random.Random(slide_num * 100 + _RUN_SEED)
    pal = _get_palette(slide_num)

    img = Image.new("RGBA", (width, height), (*pal["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")

    headline = strip_emoji(headline)

    # Check for "nobody:" format — split and render differently
    if "nobody" in headline.lower() or "\n" in headline:
        parts = headline.replace("\\n", "\n").split("\n")
        nobody_font = _get_font(fonts, "nobody")
        title_font = _get_font(fonts, "title")

        y = height // 5
        text_color = (*pal["text"], 255)

        # Render "nobody:" lines in smaller font
        for part in parts[:-1]:
            part = part.strip()
            if not part:
                continue
            tw = text_width(part, nobody_font)
            x = (width - tw) // 2 + rng.randint(-20, 20)
            draw.text((x, y), part, fill=(*pal["text"], 160), font=nobody_font)
            y += line_height(nobody_font, 12)

        # Last line (the punchline) in massive font
        if parts:
            punchline = parts[-1].strip()
            max_w = width - 100
            wrapped = wrap_text(punchline, title_font, max_w)
            lh = line_height(title_font, 14)
            y += 30
            for ln in wrapped:
                tw = text_width(ln, title_font)
                x = (width - tw) // 2 + rng.randint(-25, 25)
                draw.text((x, y), ln, fill=text_color, font=title_font)
                y += lh
    else:
        # Simple massive text
        _render_text_block(img, draw, fonts, headline.upper(), width, height, slide_num,
                          font_key="title")

    # Red overlays (sometimes)
    if rng.random() > 0.5:
        _draw_red_overlays(draw, width, height, rng, count=1)

    # Apply deep-fry
    img = _deep_fry(img, intensity=0.7)

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    """Single color bg + relatable statement + artifacts."""
    rng = _random.Random(slide_num * 200 + _RUN_SEED)
    pal = _get_palette(slide_num)

    img = Image.new("RGBA", (width, height), (*pal["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Combine headline + lines
    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    text_parts = []
    if headline:
        text_parts.append(headline)
    text_parts.extend(lines)
    full_text = " ".join(text_parts)

    _render_text_block(img, draw, fonts, full_text, width, height, slide_num,
                      font_key="body")

    # Red overlays
    if rng.random() > 0.4:
        _draw_red_overlays(draw, width, height, rng, count=rng.randint(1, 2))

    # Watermark
    tiny_font = _get_font(fonts, "tiny")
    wm = "toxshield.in"
    ww = text_width(wm, tiny_font)
    wm_color = (*pal["text"], 80)
    draw.text(((width - ww) // 2, height - 60), wm, fill=wm_color, font=tiny_font)

    # Deep-fry (vary intensity per slide)
    fry_intensity = 0.5 + rng.random() * 0.5
    img = _deep_fry(img, intensity=fry_intensity)

    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    """Deliberately casual CTA + disclaimer."""
    rng = _random.Random(slide_num * 300 + _RUN_SEED)
    pal = _get_palette(slide_num)

    img = Image.new("RGBA", (width, height), (*pal["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")

    cta_text = strip_emoji(cta_text)
    text_color = (*pal["text"], 255)

    # CTA in body font (deliberately casual, not Impact)
    body_font = _get_font(fonts, "body")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")

    max_w = width - 140
    # Lowercase the CTA for casual energy
    wrapped = wrap_text(cta_text.lower(), body_font, max_w)
    lh = line_height(body_font, 16)
    total_h = len(wrapped) * lh

    offset_x = rng.randint(-20, 20)
    y = (height - total_h) // 2 - 60 + rng.randint(-20, 20)

    for ln in wrapped:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2 + offset_x
        draw.text((x, y), ln, fill=text_color, font=body_font)
        y += lh

    # Sub-text
    y += 40
    sub = "toxshield.in | @toxshield.ai"
    sw = text_width(sub, small_font)
    draw.text(((width - sw) // 2, y), sub, fill=(*pal["text"], 150), font=small_font)

    # Disclaimer at bottom
    disc_y = height - 120
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        dw = text_width(disc_line, tiny_font)
        draw.text(((width - dw) // 2, disc_y), disc_line,
                  fill=(*pal["text"], 100), font=tiny_font)
        disc_y += 28

    # Light deep-fry on CTA
    img = _deep_fry(img, intensity=0.4)

    return img.convert("RGB")
