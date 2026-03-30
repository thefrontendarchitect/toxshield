"""Glitch theme — digital corruption with RGB channel offset and scan artifacts."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

# Run-level seed — set by generate_carousel.py for unique images each run
_RUN_SEED = 0

from PIL import Image, ImageDraw, ImageFont

from . import (
    FONT_SIZES, ROUNDED_BODY_FONTS, ROUNDED_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

COLORS = {
    "bg":           (0, 0, 0),
    "text_primary": (255, 255, 255),
    "text_secondary": (200, 200, 200),
    "text_muted":   (80, 80, 80),
}


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in ROUNDED_FONTS:
        if p.exists():
            fonts["headline"] = fonts["body"] = fonts["small"] = str(p)
            break
    for p in ROUNDED_BODY_FONTS:
        if p.exists():
            fonts["body"] = fonts["small"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = FONT_SIZES.get(size_key, 28)
    font_path = fonts.get("headline") if size_key in ("title", "subtitle") else fonts.get("body")
    if font_path:
        try:
            idx = 2 if font_path.endswith(".ttc") and size_key in ("title", "subtitle") else 0
            return ImageFont.truetype(font_path, size, index=idx)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _apply_rgb_split(img: Image.Image, offset: int = 4) -> Image.Image:
    """Split RGB channels with offset for chromatic aberration."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    r, g, b = img.split()

    # Offset red channel left, blue channel right
    from PIL import ImageChops
    r_shifted = ImageChops.offset(r, -offset, 0)
    b_shifted = ImageChops.offset(b, offset, 1)

    return Image.merge("RGB", (r_shifted, g, b_shifted))


def _apply_displacement(img: Image.Image, seed: int) -> Image.Image:
    """Randomly shift horizontal strips for glitch displacement."""
    rng = random.Random(seed)
    w, h = img.size
    pixels = img.load()
    result = img.copy()
    result_pixels = result.load()

    for _ in range(rng.randint(5, 9)):
        strip_y = rng.randint(0, h - 1)
        strip_h = rng.randint(8, 30)
        shift = rng.randint(-25, 25)

        for y in range(strip_y, min(strip_y + strip_h, h)):
            for x in range(w):
                src_x = (x - shift) % w
                result_pixels[x, y] = pixels[src_x, y]

    return result


def _apply_noise_lines(draw: ImageDraw.Draw, width: int, height: int, seed: int):
    """Draw random thin colored noise strips."""
    rng = random.Random(seed + 999)
    noise_colors = [
        (255, 0, 80), (0, 255, 200), (255, 255, 0),
        (0, 150, 255), (255, 100, 255),
    ]
    for _ in range(rng.randint(3, 6)):
        y = rng.randint(0, height - 1)
        h = rng.randint(1, 3)
        color = (*rng.choice(noise_colors), rng.randint(60, 120))
        x_start = rng.randint(0, width // 3)
        x_end = rng.randint(width // 2, width)
        draw.rectangle([(x_start, y), (x_end, y + h)], fill=color)


def _render_text_to_img(width, height, draw_fn):
    """Render text to an RGBA image, apply glitch effects, return RGB."""
    # Base with text
    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw_fn(draw)

    # Apply glitch effects
    img = _apply_rgb_split(img, offset=4)
    img = _apply_displacement(img, seed=hash(str(width) + str(height)) & 0xFFFF)

    # Noise lines on top
    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    _apply_noise_lines(overlay_draw, width, height, seed=hash(str(width)) & 0xFFFF)
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    return img_rgba.convert("RGB")


def render_title_slide(fonts, headline, slide_num, width, height):
    headline = strip_emoji(headline)
    font = _get_font(fonts, "title")
    max_w = width - 200
    wrapped = wrap_text(headline, font, max_w)
    lh = line_height(font, 24)
    total_h = len(wrapped) * lh

    def draw_fn(draw):
        y = (height - total_h) // 2
        for ln in wrapped:
            tw = text_width(ln, font)
            x = (width - tw) // 2
            draw.text((x, y), ln, fill=COLORS["text_primary"], font=font)
            y += lh

    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw_fn(draw)
    img = _apply_rgb_split(img, offset=5)
    img = _apply_displacement(img, seed=slide_num * 1000 + _RUN_SEED)

    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    _apply_noise_lines(ImageDraw.Draw(overlay, "RGBA"), width, height, slide_num * 1000)
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    return img_rgba.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
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
    body_lh = line_height(body_font, 24)

    total_h = 0
    if wrapped_hl:
        total_h += len(wrapped_hl) * hl_lh + 40
    total_h += len(body_wrapped) * body_lh

    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    y = (height - total_h) // 2

    if wrapped_hl:
        for ln in wrapped_hl:
            tw = text_width(ln, subtitle_font)
            x = (width - tw) // 2
            draw.text((x, y), ln, fill=COLORS["text_primary"], font=subtitle_font)
            y += hl_lh
        y += 40

    for ln in body_wrapped:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_secondary"], font=body_font)
        y += body_lh

    img = _apply_rgb_split(img, offset=3)
    img = _apply_displacement(img, seed=slide_num * 1000 + _RUN_SEED)

    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    _apply_noise_lines(ImageDraw.Draw(overlay, "RGBA"), width, height, slide_num * 1000)
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    return img_rgba.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    cta_text = strip_emoji(cta_text)
    cta_font = _get_font(fonts, "subtitle")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_w = width - 200

    wrapped = wrap_text(cta_text, cta_font, max_w)
    cta_lh = line_height(cta_font, 15)
    sub_lines = ["@toxshield.ai", "toxshield.in"]
    sl_lh = line_height(small_font, 12)

    total_h = len(wrapped) * cta_lh + 50 + len(sub_lines) * sl_lh

    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    y = (height - total_h) // 2

    for ln in wrapped:
        tw = text_width(ln, cta_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=cta_font)
        y += cta_lh

    y += 50
    for ln in sub_lines:
        tw = text_width(ln, small_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=COLORS["text_secondary"], font=small_font)
        y += sl_lh

    # Disclaimer before glitch (stays readable)
    disclaimer_y = height - 130
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=COLORS["text_muted"], font=tiny_font)
        disclaimer_y += 28

    img = _apply_rgb_split(img, offset=3)
    img = _apply_displacement(img, seed=slide_num * 1000 + _RUN_SEED)

    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    _apply_noise_lines(ImageDraw.Draw(overlay, "RGBA"), width, height, slide_num * 1000)
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    return img_rgba.convert("RGB")
