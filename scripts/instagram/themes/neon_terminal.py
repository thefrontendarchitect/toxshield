"""Neon Terminal theme — dark bg, toxic-green text, CRT scanlines, monospace."""

from __future__ import annotations

from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    FONT_SIZES, MONO_BOLD_FONTS, MONO_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

COLORS = {
    "bg":           (10, 10, 10),
    "text_primary": (0, 255, 65),
    "text_dim":     (0, 180, 45),
    "text_muted":   (0, 100, 25),
    "glow":         (0, 255, 65),
    "scanline":     (255, 255, 255),
}

_FONT_SIZES = {**FONT_SIZES, "title": 78, "subtitle": 52, "body": 42}


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


def _apply_scanlines(img: Image.Image) -> Image.Image:
    """CRT horizontal scanline overlay."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, img.size[1], 4):
        draw.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, 18), width=1)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay)


def _apply_glow(img: Image.Image, text_img: Image.Image) -> Image.Image:
    """Gaussian blur glow behind text."""
    glow = text_img.copy()
    glow = glow.filter(ImageFilter.GaussianBlur(radius=20))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return Image.alpha_composite(img, glow)


def _draw_corner_brackets(draw: ImageDraw.Draw, width: int, height: int):
    """Draw corner bracket decorations."""
    color = (*COLORS["text_dim"], 120)
    blen = 40
    bw = 2
    m = 30
    for cx, cy, dx, dy in [
        (m, m, 1, 1), (width - m, m, -1, 1),
        (m, height - m, 1, -1), (width - m, height - m, -1, -1),
    ]:
        draw.line([(cx, cy), (cx + blen * dx, cy)], fill=color, width=bw)
        draw.line([(cx, cy), (cx, cy + blen * dy)], fill=color, width=bw)


def render_title_slide(fonts, headline, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_corner_brackets(draw, width, height)

    headline = strip_emoji(headline).upper()
    font = _get_font(fonts, "title")
    max_w = width - 200
    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 28)
    total_h = len(wrapped) * lh
    y = (height - total_h) // 2

    # Glow layer
    glow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img, "RGBA")
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        glow_draw.text((x, y), ln, fill=(*COLORS["glow"], 60), font=font)
        y += lh
    img = _apply_glow(img, glow_img)

    # Sharp text on top
    draw = ImageDraw.Draw(img, "RGBA")
    y = (height - total_h) // 2
    for ln in wrapped:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=font)
        y += lh

    # Status line
    small = _get_font(fonts, "tiny")
    status = f"> TOXSHIELD v2.0 // SLIDE {slide_num:02d}"
    draw.text((40, height - 60), status, fill=(*COLORS["text_muted"], 150), font=small)

    img = _apply_scanlines(img)
    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_corner_brackets(draw, width, height)

    headline = strip_emoji(headline).upper() if headline else ""
    lines = [strip_emoji(line) for line in lines]

    subtitle_font = _get_font(fonts, "subtitle")
    body_font = _get_font(fonts, "body")
    max_w = width - 200

    wrapped_hl = wrap_text(headline, subtitle_font, max_w) if headline else []
    hl_lh = line_height(subtitle_font, 20)

    body_lines = []
    for line in lines:
        for sub in line.split("\n"):
            body_lines.extend(wrap_text(f"> {sub}", body_font, max_w))
    body_lh = line_height(body_font, 28)

    total_h = 0
    if wrapped_hl:
        total_h += len(wrapped_hl) * hl_lh + 40
    total_h += len(body_lines) * body_lh
    y = (height - total_h) // 2

    if wrapped_hl:
        for ln in wrapped_hl:
            tw = text_width(ln, subtitle_font)
            x = (width - tw) // 2
            draw.text((x, y), ln, fill=COLORS["text_primary"], font=subtitle_font)
            y += hl_lh
        y += 40

    for ln in body_lines:
        draw.text((100, y), ln, fill=COLORS["text_dim"], font=body_font)
        y += body_lh

    small = _get_font(fonts, "tiny")
    draw.text((40, height - 60), f"> SCAN {slide_num:02d} // ACTIVE", fill=(*COLORS["text_muted"], 150), font=small)

    img = _apply_scanlines(img)
    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    img = Image.new("RGBA", (width, height), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_corner_brackets(draw, width, height)

    cta_text = strip_emoji(cta_text).upper()
    cta_font = _get_font(fonts, "subtitle")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 200

    wrapped = wrap_text(cta_text, cta_font, max_w)
    cta_lh = line_height(cta_font, 18)

    sub_lines = ["> FOLLOW @TOXSHIELD.AI", "> TOXSHIELD.IN"]
    sl_lh = line_height(small_font, 16)

    total_h = len(wrapped) * cta_lh + 60 + len(sub_lines) * sl_lh + 120
    y = (height - total_h) // 2

    for ln in wrapped:
        tw = text_width(ln, cta_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=cta_font)
        y += cta_lh

    y += 60
    for ln in sub_lines:
        draw.text((100, y), ln, fill=COLORS["text_dim"], font=small_font)
        y += sl_lh

    disclaimer_y = height - 140
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*COLORS["text_muted"], 140), font=tiny_font)
        disclaimer_y += 30

    img = _apply_scanlines(img)
    return img.convert("RGB")
