"""Forensic theme — classified document aesthetic with typewriter font."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

# Run-level seed — set by generate_carousel.py for unique images each run
_RUN_SEED = 0

from PIL import Image, ImageDraw, ImageFont

from . import (
    FONT_SIZES, SAFETY_DISCLAIMER, TYPEWRITER_FONTS,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

COLORS = {
    "bg":           (245, 240, 232),
    "text_primary": (26, 26, 26),
    "text_secondary": (60, 60, 60),
    "text_muted":   (140, 140, 140),
    "redaction":    (20, 20, 20),
    "stamp":        (180, 40, 40),
    "border":       (80, 80, 80),
}

_FONT_SIZES = {**FONT_SIZES, "title": 72, "subtitle": 48, "body": 40, "small": 30, "tiny": 22}


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in TYPEWRITER_FONTS:
        if p.exists():
            fonts["headline"] = fonts["body"] = fonts["small"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 28)
    font_path = fonts.get("headline") if size_key in ("title", "subtitle") else fonts.get("body")
    if font_path:
        try:
            idx = 0
            if font_path.endswith(".ttc"):
                idx = 1 if size_key in ("title", "subtitle") else 0
            return ImageFont.truetype(font_path, size, index=idx)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _draw_border(draw: ImageDraw.Draw, width: int, height: int):
    inset = 30
    draw.rectangle(
        [(inset, inset), (width - inset, height - inset)],
        outline=COLORS["border"], width=2,
    )


def _draw_watermark(draw: ImageDraw.Draw, width: int, height: int, font: ImageFont.FreeTypeFont):
    """Diagonal CONFIDENTIAL watermark."""
    wm = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm, "RGBA")
    wm_draw.text(
        (width // 2 - 300, height // 2 - 40),
        "CONFIDENTIAL",
        fill=(*COLORS["stamp"], 22),
        font=font,
    )
    rotated = wm.rotate(35, expand=False, center=(width // 2, height // 2))
    return rotated


def _draw_evidence_tag(draw: ImageDraw.Draw, slide_num: int, width: int, font: ImageFont.FreeTypeFont):
    tag = f"EXHIBIT A-{slide_num}"
    draw.text((width - 220, 45), tag, fill=COLORS["text_muted"], font=font)


def _draw_redaction_bars(draw: ImageDraw.Draw, width: int, height: int, seed: int, count: int = 4):
    """Random decorative redaction bars in margins."""
    rng = random.Random(seed)
    margin = 180
    for _ in range(count):
        zone = rng.choice(["top", "bottom", "left", "right"])
        if zone == "top":
            x = rng.randint(60, width - 200)
            y = rng.randint(60, margin)
            w = rng.randint(60, 160)
            h = rng.randint(14, 22)
        elif zone == "bottom":
            x = rng.randint(60, width - 200)
            y = rng.randint(height - margin, height - 60)
            w = rng.randint(60, 160)
            h = rng.randint(14, 22)
        elif zone == "left":
            x = rng.randint(40, margin)
            y = rng.randint(margin, height - margin)
            w = rng.randint(50, 120)
            h = rng.randint(14, 22)
        else:
            x = rng.randint(width - margin, width - 60)
            y = rng.randint(margin, height - margin)
            w = rng.randint(50, 120)
            h = rng.randint(14, 22)
        draw.rectangle([(x, y), (x + w, y + h)], fill=(*COLORS["redaction"], 200))


def render_title_slide(fonts, headline, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_border(draw, width, height)
    _draw_redaction_bars(draw, width, height, seed=slide_num * 1000 + _RUN_SEED)

    small_font = _get_font(fonts, "small")
    _draw_evidence_tag(draw, slide_num, width, small_font)

    # Watermark
    wm_font = _get_font(fonts, "title")
    wm = _draw_watermark(draw, width, height, wm_font)
    img = Image.alpha_composite(img, wm)
    draw = ImageDraw.Draw(img, "RGBA")

    # Classification header
    tiny_font = _get_font(fonts, "tiny")
    header = "BEHAVIORAL FORENSICS DIVISION — CLASSIFIED"
    hw = text_width(header, tiny_font)
    draw.text(((width - hw) // 2, 50), header, fill=COLORS["stamp"], font=tiny_font)

    # Title
    headline = strip_emoji(headline)
    font = _get_font(fonts, "title")
    max_w = width - 200
    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 28)
    total_h = len(wrapped) * lh
    y = (height - total_h) // 2

    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=font)
        y += lh

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_border(draw, width, height)
    _draw_redaction_bars(draw, width, height, seed=slide_num * 1000 + _RUN_SEED, count=3)

    small_font = _get_font(fonts, "small")
    _draw_evidence_tag(draw, slide_num, width, small_font)

    headline = strip_emoji(headline) if headline else ""
    lines = [strip_emoji(line) for line in lines]

    subtitle_font = _get_font(fonts, "subtitle")
    body_font = _get_font(fonts, "body")
    max_w = width - 200

    wrapped_hl = wrap_text(headline, subtitle_font, max_w) if headline else []
    hl_lh = line_height(subtitle_font, 20)

    body_wrapped = []
    for line in lines:
        for sub in line.split("\n"):
            body_wrapped.extend(wrap_text(sub, body_font, max_w))
    body_lh = line_height(body_font, 28)

    total_h = 0
    if wrapped_hl:
        total_h += len(wrapped_hl) * hl_lh + 40
    total_h += len(body_wrapped) * body_lh
    y = (height - total_h) // 2

    if wrapped_hl:
        for ln in wrapped_hl:
            tw = text_width(ln, subtitle_font)
            x = (width - tw) // 2
            # Underlined subtitle
            draw.text((x, y), ln, fill=COLORS["text_primary"], font=subtitle_font)
            draw.line([(x, y + hl_lh - 8), (x + tw, y + hl_lh - 8)], fill=COLORS["text_muted"], width=1)
            y += hl_lh
        y += 40

    for ln in body_wrapped:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_secondary"], font=body_font)
        y += body_lh

    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_border(draw, width, height)

    small_font = _get_font(fonts, "small")
    _draw_evidence_tag(draw, slide_num, width, small_font)

    # Watermark
    wm_font = _get_font(fonts, "title")
    wm = _draw_watermark(draw, width, height, wm_font)
    img = Image.alpha_composite(img, wm)
    draw = ImageDraw.Draw(img, "RGBA")

    cta_text = strip_emoji(cta_text)
    cta_font = _get_font(fonts, "subtitle")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 200

    wrapped = wrap_text(cta_text, cta_font, max_w)
    cta_lh = line_height(cta_font, 18)

    sub_lines = ["CASE FILE: @toxshield.ai", "ACCESS: toxshield.in"]
    sl_lh = line_height(small_font, 14)

    total_h = len(wrapped) * cta_lh + 60 + len(sub_lines) * sl_lh + 120
    y = (height - total_h) // 2

    for ln in wrapped:
        tw = text_width(ln, cta_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=cta_font)
        y += cta_lh

    y += 60
    for ln in sub_lines:
        tw = text_width(ln, small_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_muted"], font=small_font)
        y += sl_lh

    disclaimer_y = height - 140
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*COLORS["text_muted"], 160), font=tiny_font)
        disclaimer_y += 30

    return img.convert("RGB")
