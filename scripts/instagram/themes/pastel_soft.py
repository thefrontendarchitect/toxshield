"""Pastel Soft theme — dreamy aurora gradients with grain texture and glassmorphism.

2026-trending aesthetic: saturated pastel aurora blobs on rich dark-tinted bases,
grainy texture overlay, glassmorphism text cards, sparkle accents.
"""

from __future__ import annotations

import math
import random as _random
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    FONT_SIZES, ROUNDED_BODY_FONTS, ROUNDED_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, wrap_text,
)

# ---------------------------------------------------------------------------
# Aurora gradient palettes — one per slide, rotating
# Each entry: (base_color, [blob definitions])
# blob: (relative_x, relative_y, color, radius_factor, alpha)
# ---------------------------------------------------------------------------

_AURORA_PALETTES = [
    # 1: Sakura Dream — deep rose base + pink/coral/lavender blobs
    {
        "base": (45, 20, 40),
        "blobs": [
            (0.15, 0.20, (255, 107, 151), 0.45, 130),  # hot pink
            (0.80, 0.25, (232, 121, 249), 0.40, 120),   # orchid
            (0.50, 0.75, (255, 182, 193), 0.50, 110),   # light pink
            (0.20, 0.85, (200, 150, 255), 0.35, 100),   # lavender
        ],
        "text": (255, 245, 250),
        "text_secondary": (255, 220, 235),
        "text_muted": (180, 140, 165),
        "sparkle": (255, 200, 220),
    },
    # 2: Ocean Breath — deep teal base + aqua/cyan/mint blobs
    {
        "base": (15, 35, 50),
        "blobs": [
            (0.20, 0.15, (0, 206, 209), 0.45, 120),    # dark turquoise
            (0.75, 0.30, (100, 220, 255), 0.40, 130),   # sky blue
            (0.40, 0.80, (150, 255, 220), 0.45, 110),   # aquamarine
            (0.85, 0.75, (80, 180, 255), 0.35, 100),    # cornflower
        ],
        "text": (240, 255, 255),
        "text_secondary": (200, 240, 245),
        "text_muted": (120, 170, 180),
        "sparkle": (180, 255, 240),
    },
    # 3: Lavender Field — deep violet base + purple/lilac/pink blobs
    {
        "base": (30, 15, 55),
        "blobs": [
            (0.15, 0.25, (181, 123, 238), 0.45, 130),   # medium purple
            (0.80, 0.20, (232, 121, 249), 0.40, 120),    # orchid
            (0.50, 0.70, (167, 139, 250), 0.50, 110),    # periwinkle
            (0.25, 0.80, (255, 150, 200), 0.35, 115),    # pink accent
        ],
        "text": (250, 240, 255),
        "text_secondary": (225, 210, 245),
        "text_muted": (160, 140, 185),
        "sparkle": (210, 180, 255),
    },
    # 4: Sunset Glow — deep amber base + peach/coral/gold blobs
    {
        "base": (50, 25, 20),
        "blobs": [
            (0.20, 0.20, (255, 150, 100), 0.45, 130),   # coral
            (0.75, 0.30, (255, 200, 100), 0.40, 120),    # gold
            (0.45, 0.75, (255, 130, 150), 0.45, 115),    # salmon pink
            (0.80, 0.80, (255, 180, 130), 0.35, 110),    # peach
        ],
        "text": (255, 250, 245),
        "text_secondary": (255, 230, 215),
        "text_muted": (185, 150, 130),
        "sparkle": (255, 220, 180),
    },
    # 5: Cosmic Mint — deep green base + mint/sage/teal/emerald blobs
    {
        "base": (15, 40, 35),
        "blobs": [
            (0.20, 0.15, (100, 255, 200), 0.45, 120),   # mint
            (0.80, 0.25, (80, 220, 180), 0.40, 130),     # emerald light
            (0.45, 0.80, (150, 250, 200), 0.50, 110),    # light green
            (0.15, 0.75, (120, 200, 255), 0.35, 100),    # sky accent
        ],
        "text": (240, 255, 250),
        "text_secondary": (210, 245, 230),
        "text_muted": (130, 175, 160),
        "sparkle": (180, 255, 220),
    },
]

# Override font sizes — slightly bolder
_FONT_SIZES = {**FONT_SIZES, "title": 90, "subtitle": 62, "body": 50}

# Grain opacity (0-255), 20% = 51
_GRAIN_ALPHA = 45

# Run-level seed — set by generate_carousel.py for unique images each run
_RUN_SEED = 0


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
    size = _FONT_SIZES.get(size_key, 28)
    if size_key in ("title", "subtitle"):
        font_path = fonts.get("headline")
        font_index = 2 if font_path and font_path.endswith(".ttc") else 0
    else:
        font_path = fonts.get("body") or fonts.get("small")
        font_index = 0
    if font_path:
        try:
            if font_path.endswith(".ttc"):
                return ImageFont.truetype(font_path, size, index=font_index)
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _palette(slide_num: int) -> dict:
    return _AURORA_PALETTES[(slide_num - 1) % len(_AURORA_PALETTES)]


# ---------------------------------------------------------------------------
# Aurora gradient background
# ---------------------------------------------------------------------------

def _render_aurora_bg(width: int, height: int, slide_num: int) -> Image.Image:
    """Create an aurora gradient background with blurred color blobs."""
    pal = _palette(slide_num)
    base = pal["base"]

    # Work at half resolution for performance, then scale up
    hw, hh = width // 2, height // 2
    img = Image.new("RGBA", (hw, hh), (*base, 255))

    for bx_rel, by_rel, color, r_factor, alpha in pal["blobs"]:
        layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        cx = int(bx_rel * hw)
        cy = int(by_rel * hh)
        r = int(min(hw, hh) * r_factor)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, alpha))
        # Heavy blur for aurora effect
        layer = layer.filter(ImageFilter.GaussianBlur(radius=int(r * 0.6)))
        img = Image.alpha_composite(img, layer)

    # Scale up to full resolution with smooth resampling
    img = img.resize((width, height), Image.LANCZOS)
    return img


# ---------------------------------------------------------------------------
# Grain texture overlay
# ---------------------------------------------------------------------------

def _add_grain(img: Image.Image, seed: int = 0) -> Image.Image:
    """Add monochromatic fine grain noise at ~18% opacity."""
    w, h = img.size
    rng = _random.Random(seed)

    # Generate noise — use chunks for performance
    chunk_size = 270  # generate at 1/4 res and scale up for organic look
    noise_small = Image.new("L", (w // 4, h // 4))
    pix = noise_small.load()
    for y in range(h // 4):
        for x in range(w // 4):
            pix[x, y] = rng.randint(0, 255)

    noise = noise_small.resize((w, h), Image.BILINEAR)
    # Create RGBA grain layer
    grain_layer = Image.merge("RGBA", [noise, noise, noise, Image.new("L", (w, h), _GRAIN_ALPHA)])
    return Image.alpha_composite(img.convert("RGBA"), grain_layer)


# ---------------------------------------------------------------------------
# Glassmorphism text card
# ---------------------------------------------------------------------------

def _draw_glass_card(bg: Image.Image, x: int, y: int, w: int, h: int,
                     blur_radius: int = 12, white_alpha: int = 35,
                     border_alpha: int = 50, corner_radius: int = 24) -> Image.Image:
    """Draw a frosted glass card over the background."""
    result = bg.copy()

    # Crop region, blur it
    region = bg.crop((x, y, x + w, y + h)).convert("RGBA")
    blurred = region.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # White overlay
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, white_alpha))
    card = Image.alpha_composite(blurred, overlay)

    # Subtle border
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        [1, 1, w - 2, h - 2],
        radius=corner_radius,
        outline=(255, 255, 255, border_alpha),
        width=2,
    )

    result.paste(card.convert("RGB"), (x, y), card)
    return result


# ---------------------------------------------------------------------------
# Sparkle / star decorations
# ---------------------------------------------------------------------------

def _draw_sparkles(draw: ImageDraw.Draw, width: int, height: int, slide_num: int,
                   count: int = 18, bottom_margin: int = 160):
    """Draw small 4-point star sparkles and soft dots in the margins."""
    rng = _random.Random(slide_num * 777 + _RUN_SEED)
    pal = _palette(slide_num)
    sparkle_color = pal["sparkle"]

    margin = 130
    zones = [
        (20, 20, width - 20, margin),                          # top
        (20, height - bottom_margin, width - 20, height - 20), # bottom
        (20, margin, margin, height - bottom_margin),           # left
        (width - margin, margin, width - 20, height - bottom_margin),  # right
    ]

    for _ in range(count):
        zone = zones[rng.randint(0, len(zones) - 1)]
        x = rng.randint(zone[0], max(zone[0], zone[2] - 1))
        y = rng.randint(zone[1], max(zone[1], zone[3] - 1))
        opacity = rng.randint(100, 220)
        color = (*sparkle_color, opacity)
        kind = rng.random()

        if kind < 0.45:
            # 4-point star sparkle
            size = rng.randint(6, 18)
            w = max(1, size // 6)
            draw.line([(x - size, y), (x + size, y)], fill=color, width=w)
            draw.line([(x, y - size), (x, y + size)], fill=color, width=w)
            # Diagonal shorter rays
            ds = size // 2
            draw.line([(x - ds, y - ds), (x + ds, y + ds)], fill=color, width=w)
            draw.line([(x + ds, y - ds), (x - ds, y + ds)], fill=color, width=w)
        elif kind < 0.70:
            # Soft dot
            r = rng.randint(2, 6)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        elif kind < 0.85:
            # Tiny circle outline
            r = rng.randint(8, 20)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=(*sparkle_color, opacity // 2), width=2)
        else:
            # Small plus/cross
            size = rng.randint(5, 12)
            draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
            draw.line([(x, y - size), (x, y + size)], fill=color, width=2)


# ---------------------------------------------------------------------------
# Bokeh light circles
# ---------------------------------------------------------------------------

def _draw_bokeh(img: Image.Image, slide_num: int, count: int = 5) -> Image.Image:
    """Draw soft, large bokeh circles for dreamy depth."""
    w, h = img.size
    rng = _random.Random(slide_num * 333 + _RUN_SEED)
    pal = _palette(slide_num)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for _ in range(count):
        x = rng.randint(-50, w + 50)
        y = rng.randint(-50, h + 50)
        r = rng.randint(40, 120)
        # Use sparkle color with very low opacity
        alpha = rng.randint(12, 30)
        color = (*pal["sparkle"], alpha)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    # Blur the bokeh for softness
    layer = layer.filter(ImageFilter.GaussianBlur(radius=20))
    return Image.alpha_composite(img.convert("RGBA"), layer)


# ---------------------------------------------------------------------------
# Full background: aurora + bokeh + grain + sparkles
# ---------------------------------------------------------------------------

def _make_background(width: int, height: int, slide_num: int,
                     sparkle_count: int = 18, bottom_margin: int = 160) -> Image.Image:
    """Compose full background: aurora gradient + bokeh + grain + sparkles."""
    img = _render_aurora_bg(width, height, slide_num)
    img = _draw_bokeh(img, slide_num)
    img = _add_grain(img, seed=slide_num * 1000 + _RUN_SEED)

    # Sparkles drawn on top
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_sparkles(draw, width, height, slide_num,
                   count=sparkle_count, bottom_margin=bottom_margin)
    return img


# ===========================================================================
# Slide Rendering
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    img = _make_background(width, height, slide_num)
    pal = _palette(slide_num)

    headline = strip_emoji(headline)
    font = _get_font(fonts, "title")
    max_text_w = width - 200
    wrapped = wrap_text(headline, font, max_text_w)
    lh = line_height(font, 28)
    total_h = len(wrapped) * lh

    # Glassmorphism card behind text
    card_pad_x, card_pad_y = 60, 50
    card_w = max_text_w + card_pad_x * 2
    card_h = total_h + card_pad_y * 2
    card_x = (width - card_w) // 2
    card_y = (height - card_h) // 2
    img = _draw_glass_card(img, card_x, card_y, card_w, card_h)

    draw = ImageDraw.Draw(img, "RGBA")
    y = card_y + card_pad_y
    for ln in wrapped:
        bbox = font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=pal["text"], font=font)
        y += lh

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    img = _make_background(width, height, slide_num)
    pal = _palette(slide_num)

    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    subtitle_font = _get_font(fonts, "subtitle")
    body_font = _get_font(fonts, "body")
    max_text_w = width - 200

    wrapped_hl = wrap_text(headline, subtitle_font, max_text_w) if headline else []
    hl_lh = line_height(subtitle_font, 22)

    all_wrapped = []
    for line in lines:
        for sub in line.split("\n"):
            all_wrapped.extend(wrap_text(sub, body_font, max_text_w))
    body_lh = line_height(body_font, 26)

    total_h = 0
    if wrapped_hl:
        total_h += len(wrapped_hl) * hl_lh + 40
    total_h += len(all_wrapped) * body_lh

    # Glassmorphism card
    card_pad_x, card_pad_y = 60, 50
    card_w = max_text_w + card_pad_x * 2
    card_h = total_h + card_pad_y * 2
    card_x = (width - card_w) // 2
    card_y = (height - card_h) // 2
    img = _draw_glass_card(img, card_x, card_y, card_w, card_h)

    draw = ImageDraw.Draw(img, "RGBA")
    y = card_y + card_pad_y

    if wrapped_hl:
        for ln in wrapped_hl:
            bbox = subtitle_font.getbbox(ln)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), ln, fill=pal["text"], font=subtitle_font)
            y += hl_lh
        y += 40

    for ln in all_wrapped:
        bbox = body_font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=pal["text_secondary"], font=body_font)
        y += body_lh

    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    img = _make_background(width, height, slide_num, sparkle_count=14, bottom_margin=280)
    pal = _palette(slide_num)

    cta_text = strip_emoji(cta_text)
    cta_font = _get_font(fonts, "subtitle")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")
    max_text_w = width - 200

    wrapped_cta = wrap_text(cta_text, cta_font, max_text_w)
    cta_lh = line_height(cta_font, 18)

    sub_lines = ["Follow @toxshield.ai", "Link in bio"]
    sl_lh = line_height(small_font, 14)

    card_content_h = len(wrapped_cta) * cta_lh + 50 + len(sub_lines) * sl_lh
    card_pad_x, card_pad_y = 60, 50
    card_w = max_text_w + card_pad_x * 2
    card_h = card_content_h + card_pad_y * 2
    card_x = (width - card_w) // 2
    card_y = (height - card_h) // 2 - 60  # shift up to make room for disclaimer
    img = _draw_glass_card(img, card_x, card_y, card_w, card_h)

    draw = ImageDraw.Draw(img, "RGBA")
    y = card_y + card_pad_y

    for ln in wrapped_cta:
        bbox = cta_font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=pal["text"], font=cta_font)
        y += cta_lh

    y += 50
    for ln in sub_lines:
        bbox = small_font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=pal["text_secondary"], font=small_font)
        y += sl_lh

    # Disclaimer at bottom
    disclaimer_y = height - 140
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*pal["text_muted"], 180), font=tiny_font)
        disclaimer_y += 30

    return img.convert("RGB")
