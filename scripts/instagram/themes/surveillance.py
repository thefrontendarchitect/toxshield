"""Surveillance theme — CCTV camera overlay with timestamp, REC indicator, grid."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    FONT_SIZES, MONO_BOLD_FONTS, MONO_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

COLORS = {
    "bg":           (10, 26, 10),
    "text_primary": (0, 204, 51),
    "text_dim":     (0, 150, 38),
    "text_muted":   (0, 90, 22),
    "grid":         (0, 80, 20),
    "rec_dot":      (255, 0, 0),
    "rec_text":     (255, 60, 60),
}

_FONT_SIZES = {**FONT_SIZES, "title": 72, "subtitle": 48, "body": 40, "small": 28, "tiny": 20}


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in MONO_BOLD_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in MONO_FONTS:
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
            idx = 1 if font_path.endswith(".ttc") else 0
            return ImageFont.truetype(font_path, size, index=idx)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _draw_grid(draw: ImageDraw.Draw, width: int, height: int):
    """Thin grid overlay like a surveillance monitor."""
    grid_color = (*COLORS["grid"], 15)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)


def _draw_rec_indicator(draw: ImageDraw.Draw, width: int, font: ImageFont.FreeTypeFont):
    """REC indicator with red dot in top-right."""
    dot_x, dot_y = width - 120, 40
    draw.ellipse([dot_x - 8, dot_y - 8, dot_x + 8, dot_y + 8], fill=COLORS["rec_dot"])
    draw.text((dot_x + 16, dot_y - 12), "REC", fill=COLORS["rec_text"], font=font)


def _draw_timestamp(draw: ImageDraw.Draw, height: int, slide_num: int, font: ImageFont.FreeTypeFont):
    """Bottom-left timestamp."""
    now = datetime.now()
    ts = now.strftime(f"%Y-%m-%d %H:%M:{slide_num:02d}")
    draw.text((40, height - 50), ts, fill=(*COLORS["text_dim"], 180), font=font)


def _draw_cam_label(draw: ImageDraw.Draw, font: ImageFont.FreeTypeFont):
    """Camera label in top-left."""
    draw.text((40, 35), "CAM-TX01", fill=(*COLORS["text_muted"], 160), font=font)


def _apply_vignette(img: Image.Image) -> Image.Image:
    """Darken edges for lens vignette effect."""
    w, h = img.size
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)

    # Draw concentric rectangles with increasing opacity at edges
    max_alpha = 100
    border = min(w, h) // 4
    for i in range(border):
        alpha = int(max_alpha * (1 - i / border) ** 2)
        if alpha > 0:
            draw.rectangle([(i, i), (w - i, h - i)], outline=(0, 0, 0, alpha))

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return Image.alpha_composite(img, vignette)


def render_title_slide(fonts, headline, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_grid(draw, width, height)

    small_font = _get_font(fonts, "tiny")
    _draw_cam_label(draw, small_font)
    _draw_rec_indicator(draw, width, small_font)
    _draw_timestamp(draw, height, slide_num, small_font)

    headline = strip_emoji(headline).upper()
    font = _get_font(fonts, "title")
    max_w = width - 200
    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 28)
    total_h = len(wrapped) * lh
    y = (height - total_h) // 2

    # Subtle glow
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    gy = y
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        glow_draw.text((x, gy), ln, fill=(*COLORS["text_primary"], 40), font=font)
        gy += lh
    glow = glow.filter(ImageFilter.GaussianBlur(radius=15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=font)
        y += lh

    img = _apply_vignette(img)
    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_grid(draw, width, height)

    small_font = _get_font(fonts, "tiny")
    _draw_cam_label(draw, small_font)
    _draw_rec_indicator(draw, width, small_font)
    _draw_timestamp(draw, height, slide_num, small_font)

    headline = strip_emoji(headline).upper() if headline else ""
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
            draw.text((x, y), ln, fill=COLORS["text_primary"], font=subtitle_font)
            y += hl_lh
        y += 40

    for ln in body_wrapped:
        draw.text((100, y), ln, fill=COLORS["text_dim"], font=body_font)
        y += body_lh

    img = _apply_vignette(img)
    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_grid(draw, width, height)

    small_font = _get_font(fonts, "tiny")
    _draw_cam_label(draw, small_font)
    _draw_rec_indicator(draw, width, small_font)
    _draw_timestamp(draw, height, slide_num, small_font)

    cta_text = strip_emoji(cta_text).upper()
    cta_font = _get_font(fonts, "subtitle")
    body_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 200

    wrapped = wrap_text(cta_text, cta_font, max_w)
    cta_lh = line_height(cta_font, 18)

    sub_lines = ["TARGET: @TOXSHIELD.AI", "ACCESS: TOXSHIELD.IN"]
    sl_lh = line_height(body_font, 14)

    total_h = len(wrapped) * cta_lh + 60 + len(sub_lines) * sl_lh + 120
    y = (height - total_h) // 2

    for ln in wrapped:
        tw = text_width(ln, cta_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=cta_font)
        y += cta_lh

    y += 60
    for ln in sub_lines:
        draw.text((100, y), ln, fill=COLORS["text_dim"], font=body_font)
        y += sl_lh

    disclaimer_y = height - 120
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*COLORS["text_muted"], 140), font=tiny_font)
        disclaimer_y += 26

    img = _apply_vignette(img)
    return img.convert("RGB")
