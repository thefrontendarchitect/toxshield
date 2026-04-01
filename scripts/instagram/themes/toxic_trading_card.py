"""Toxic Trading Card theme — collectible trading cards for toxic personality archetypes.

Pokemon/Yu-Gi-Oh inspired card layout with holographic borders, stat bars,
rarity badges, abstract portraits, and flavor text. Each content slide is a
self-contained collectible card.

Content slide lines format:
  - "STAT_NAME: NUMBER" → rendered as progress bar (e.g., "MANIPULATION: 8.7")
  - Any other text → rendered as italic flavor text
"""

from __future__ import annotations

import colorsys
import math
import random as _random
from io import BytesIO
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    FONT_SIZES, IMPACT_FONTS, MONO_FONTS, MONO_BOLD_FONTS, ROUNDED_BODY_FONTS,
    SAFETY_DISCLAIMER, find_font, line_height, strip_emoji, text_width, wrap_text,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_RUN_SEED = 0

_FONT_SIZES = {
    "title": 88,
    "subtitle": 60,
    "card_name": 52,
    "stat_name": 30,
    "stat_value": 34,
    "flavor": 32,
    "body": 44,
    "small": 28,
    "tiny": 22,
    "rarity": 22,
    "card_num": 20,
}

# Rarity levels: threshold (score avg), label, border hue offset, accent color
_RARITY_TIERS = [
    {"label": "COMMON RED FLAG",     "color": (180, 180, 180), "glow": (140, 140, 160), "stars": 1},
    {"label": "UNCOMMON TRAIT",      "color": (100, 220, 100), "glow": (60, 180, 80),   "stars": 2},
    {"label": "RARE MANIPULATOR",    "color": (80, 160, 255),  "glow": (40, 120, 255),  "stars": 3},
    {"label": "EPIC ABUSER",         "color": (200, 80, 255),  "glow": (180, 40, 255),  "stars": 4},
    {"label": "LEGENDARY TOXIC",     "color": (255, 200, 50),  "glow": (255, 180, 0),   "stars": 5},
]

# Archetype tint palettes for abstract portrait zone
_ARCHETYPE_TINTS = [
    {"base": (40, 8, 8),   "blobs": [(255, 60, 60), (200, 40, 100), (255, 100, 60)]},    # red / gaslighter
    {"base": (30, 8, 40),  "blobs": [(180, 50, 255), (120, 30, 200), (200, 80, 255)]},    # purple / narcissist
    {"base": (8, 30, 15),  "blobs": [(50, 255, 100), (30, 200, 150), (100, 255, 80)]},    # green / lovebomber
    {"base": (40, 25, 8),  "blobs": [(255, 180, 50), (255, 140, 30), (200, 160, 80)]},    # gold / controller
    {"base": (8, 20, 40),  "blobs": [(50, 150, 255), (30, 100, 220), (80, 180, 255)]},    # blue / passive-agg
]

# Card background
_CARD_BG = (18, 16, 28)
_OUTER_BG = (8, 6, 14)


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {
        "headline": None, "body": None, "small": None, "mono": None,
    }
    for p in IMPACT_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in ROUNDED_BODY_FONTS:
        if p.exists():
            fonts["body"] = fonts["small"] = str(p)
            break
    for p in MONO_BOLD_FONTS:
        if p.exists():
            fonts["mono"] = str(p)
            break
    if not fonts["mono"]:
        for p in MONO_FONTS:
            if p.exists():
                fonts["mono"] = str(p)
                break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 28)
    if size_key in ("title", "subtitle", "card_name"):
        font_path = fonts.get("headline")
    elif size_key in ("stat_name", "stat_value", "rarity", "card_num"):
        font_path = fonts.get("mono")
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
# Stat parsing
# ---------------------------------------------------------------------------

def _parse_stats(lines: List[str]) -> Tuple[List[Tuple[str, float]], List[str]]:
    """Parse lines into stats and flavor text.

    Lines matching 'NAME: NUMBER' become stats, others become flavor text.
    """
    stats: List[Tuple[str, float]] = []
    flavor: List[str] = []
    for line in lines:
        parts = line.rsplit(":", 1)
        if len(parts) == 2:
            try:
                val = float(parts[1].strip())
                stats.append((parts[0].strip().upper(), min(val, 10.0)))
                continue
            except ValueError:
                pass
        flavor.append(line)
    return stats, flavor


def _rarity_from_stats(stats: List[Tuple[str, float]]) -> dict:
    """Determine rarity tier based on average stat value."""
    if not stats:
        return _RARITY_TIERS[2]  # default to rare
    avg = sum(v for _, v in stats) / len(stats)
    if avg >= 9.0:
        return _RARITY_TIERS[4]
    elif avg >= 7.5:
        return _RARITY_TIERS[3]
    elif avg >= 6.0:
        return _RARITY_TIERS[2]
    elif avg >= 4.0:
        return _RARITY_TIERS[1]
    return _RARITY_TIERS[0]


# ---------------------------------------------------------------------------
# Holographic border
# ---------------------------------------------------------------------------

def _draw_holographic_border(
    draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
    thickness: int = 4, seed: int = 0,
):
    """Draw a rainbow-cycling holographic border around a rectangle."""
    rng = _random.Random(seed)
    hue_offset = rng.random()
    perimeter = 2 * (w + h)

    # Draw colored segments along the perimeter
    segments = 180
    for i in range(segments):
        t = i / segments
        hue = (hue_offset + t) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
        color = (int(r * 255), int(g * 255), int(b * 255), 230)

        dist = t * perimeter
        # Map distance to position along rectangle
        if dist < w:  # top edge
            px, py = x + dist, y
            draw.rectangle([int(px), int(py), int(px) + thickness, int(py) + thickness], fill=color)
        elif dist < w + h:  # right edge
            d = dist - w
            px, py = x + w - thickness, y + d
            draw.rectangle([int(px), int(py), int(px) + thickness, int(py) + thickness], fill=color)
        elif dist < 2 * w + h:  # bottom edge
            d = dist - w - h
            px, py = x + w - d, y + h - thickness
            draw.rectangle([int(px), int(py), int(px) + thickness, int(py) + thickness], fill=color)
        else:  # left edge
            d = dist - 2 * w - h
            px, py = x, y + h - d
            draw.rectangle([int(px), int(py), int(px) + thickness, int(py) + thickness], fill=color)


# ---------------------------------------------------------------------------
# Abstract portrait (aurora blobs tinted to archetype)
# ---------------------------------------------------------------------------

def _draw_abstract_portrait(
    width: int, height: int, slide_num: int,
) -> Image.Image:
    """Create an abstract aurora portrait zone."""
    tint = _ARCHETYPE_TINTS[(slide_num - 1) % len(_ARCHETYPE_TINTS)]
    hw, hh = width // 2, height // 2
    img = Image.new("RGBA", (hw, hh), (*tint["base"], 255))

    rng = _random.Random(slide_num * 999 + _RUN_SEED)
    for blob_color in tint["blobs"]:
        layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        cx = rng.randint(hw // 4, 3 * hw // 4)
        cy = rng.randint(hh // 4, 3 * hh // 4)
        r = rng.randint(min(hw, hh) // 3, min(hw, hh) // 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*blob_color, rng.randint(80, 140)))
        layer = layer.filter(ImageFilter.GaussianBlur(radius=r // 2))
        img = Image.alpha_composite(img, layer)

    img = img.resize((width, height), Image.LANCZOS)
    return img


# ---------------------------------------------------------------------------
# Stat bar rendering
# ---------------------------------------------------------------------------

def _draw_stat_bar(
    draw: ImageDraw.Draw, fonts: Dict,
    x: int, y: int, bar_width: int,
    name: str, value: float,
) -> int:
    """Draw a single stat bar. Returns y after the bar."""
    name_font = _get_font(fonts, "stat_name")
    val_font = _get_font(fonts, "stat_value")
    bar_height = 22
    bar_y_offset = 36
    spacing = 12

    # Stat name
    draw.text((x, y), name, fill=(200, 200, 220, 255), font=name_font)

    # Value text (right-aligned)
    val_str = f"{value:.1f}"
    vw = text_width(val_str, val_font)
    draw.text((x + bar_width - vw, y), val_str, fill=(255, 255, 255, 255), font=val_font)

    # Bar background
    by = y + bar_y_offset
    draw.rounded_rectangle(
        [x, by, x + bar_width, by + bar_height],
        radius=6, fill=(40, 36, 55, 200),
    )

    # Bar fill — green→yellow→red based on value
    fill_width = int((value / 10.0) * bar_width)
    if fill_width > 0:
        t = value / 10.0
        if t < 0.4:
            r, g, b = 80, 220, 100   # green
        elif t < 0.7:
            r, g, b = 255, 200, 50    # yellow
        else:
            r, g, b = 255, 60, 80     # red

        draw.rounded_rectangle(
            [x, by, x + fill_width, by + bar_height],
            radius=6, fill=(r, g, b, 220),
        )

    return by + bar_height + spacing


# ---------------------------------------------------------------------------
# Rarity stars
# ---------------------------------------------------------------------------

def _draw_stars(draw: ImageDraw.Draw, x: int, y: int, count: int, max_count: int = 5):
    """Draw filled/unfilled star indicators."""
    star_size = 14
    star_gap = 8
    for i in range(max_count):
        cx = x + i * (star_size * 2 + star_gap) + star_size
        cy = y + star_size
        filled = i < count
        color = (255, 200, 50, 255) if filled else (60, 55, 80, 200)
        # 5-point star via polygon
        points = []
        for j in range(10):
            angle = math.pi / 2 + j * math.pi / 5
            r = star_size if j % 2 == 0 else star_size // 2
            points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
        draw.polygon(points, fill=color)


# ---------------------------------------------------------------------------
# Card frame
# ---------------------------------------------------------------------------

def _draw_card(
    fonts: Dict, card_name: str, stats: List[Tuple[str, float]],
    flavor: List[str], slide_num: int, width: int, height: int,
    card_number: str = "",
) -> Image.Image:
    """Draw a complete trading card."""
    rarity = _rarity_from_stats(stats)
    rng = _random.Random(slide_num * 500 + _RUN_SEED)

    # Dark outer background with subtle glow
    img = Image.new("RGBA", (width, height), (*_OUTER_BG, 255))

    # Card dimensions (centered, with margins)
    margin_x = 60
    margin_top = 50
    margin_bot = 80
    card_x = margin_x
    card_y = margin_top
    card_w = width - 2 * margin_x
    card_h = height - margin_top - margin_bot

    # Glow behind card
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_color = (*rarity["glow"], 40)
    glow_draw.rounded_rectangle(
        [card_x - 20, card_y - 20, card_x + card_w + 20, card_y + card_h + 20],
        radius=28, fill=glow_color,
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img, glow_layer)

    # Card background
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=20, fill=(*_CARD_BG, 245),
    )

    # Holographic border
    _draw_holographic_border(draw, card_x, card_y, card_w, card_h,
                             thickness=5, seed=slide_num + _RUN_SEED)

    # -- Portrait zone (upper ~28% of card) --
    portrait_h = int(card_h * 0.28)
    portrait_margin = 18
    px = card_x + portrait_margin
    py = card_y + portrait_margin
    pw = card_w - 2 * portrait_margin
    ph = portrait_h

    portrait = _draw_abstract_portrait(pw, ph, slide_num)
    # Rounded mask
    mask = Image.new("L", (pw, ph), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=12, fill=255)
    img.paste(portrait.convert("RGB"), (px, py), mask)

    # Rarity badge (top-left of portrait)
    rarity_font = _get_font(fonts, "rarity")
    badge_text = rarity["label"]
    badge_tw = text_width(badge_text, rarity_font)
    badge_pad = 10
    badge_x = px + 8
    badge_y = py + 8
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_tw + badge_pad * 2, badge_y + 30],
        radius=6, fill=(0, 0, 0, 180),
    )
    draw.text(
        (badge_x + badge_pad, badge_y + 3),
        badge_text, fill=(*rarity["color"], 255), font=rarity_font,
    )

    # -- Name plate (metallic gradient band) --
    name_y = py + ph + 12
    name_h = 64
    # Draw gradient band
    for row in range(name_h):
        t = row / name_h
        r = int(35 + 25 * (1 - abs(2 * t - 1)))  # brighter in middle
        g = int(30 + 20 * (1 - abs(2 * t - 1)))
        b = int(50 + 35 * (1 - abs(2 * t - 1)))
        draw.line(
            [(card_x + portrait_margin, name_y + row),
             (card_x + card_w - portrait_margin, name_y + row)],
            fill=(r, g, b, 255),
        )

    # Card name centered on plate
    name_font = _get_font(fonts, "card_name")
    wrapped_name = wrap_text(card_name.upper(), name_font, pw - 20)
    name_lh = line_height(name_font, 6)
    ny = name_y + (name_h - len(wrapped_name) * name_lh) // 2
    for ln in wrapped_name:
        tw = text_width(ln, name_font)
        nx = card_x + (card_w - tw) // 2
        draw.text((nx, ny), ln, fill=(255, 255, 255, 255), font=name_font)
        ny += name_lh

    # -- Stats block --
    stats_y = name_y + name_h + 20
    stats_x = card_x + portrait_margin + 10
    bar_width = pw - 20

    for stat_name, stat_val in stats[:5]:  # max 5 stats
        stats_y = _draw_stat_bar(draw, fonts, stats_x, stats_y, bar_width, stat_name, stat_val)

    # -- Flavor text --
    if flavor:
        flavor_font = _get_font(fonts, "flavor")
        flavor_y = stats_y + 10
        max_flavor_w = pw - 20
        for fl in flavor[:2]:  # max 2 flavor lines
            wrapped_fl = wrap_text(fl, flavor_font, max_flavor_w)
            for wl in wrapped_fl[:3]:  # max 3 wrapped lines per flavor
                tw = text_width(wl, flavor_font)
                fx = card_x + (card_w - tw) // 2
                draw.text((fx, flavor_y), wl, fill=(180, 175, 200, 200), font=flavor_font)
                flavor_y += line_height(flavor_font, 8)

    # -- Footer: stars + card number --
    footer_y = card_y + card_h - 50
    _draw_stars(draw, card_x + portrait_margin + 10, footer_y, rarity["stars"])

    if card_number:
        num_font = _get_font(fonts, "card_num")
        nw = text_width(card_number, num_font)
        draw.text(
            (card_x + card_w - portrait_margin - nw - 10, footer_y + 6),
            card_number, fill=(120, 115, 150, 200), font=num_font,
        )

    # Watermark
    wm_font = _get_font(fonts, "tiny")
    wm = "toxshield.in"
    ww = text_width(wm, wm_font)
    draw.text(
        ((width - ww) // 2, height - margin_bot + 20),
        wm, fill=(100, 95, 130, 150), font=wm_font,
    )

    return img


# ===========================================================================
# Slide Rendering (standard theme API)
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    """Pack opening slide — holographic shimmer + 'RARE PULL' text."""
    rng = _random.Random(slide_num * 100 + _RUN_SEED)
    img = Image.new("RGBA", (width, height), (*_OUTER_BG, 255))

    # Holographic shimmer background — rainbow radial blobs
    for i in range(8):
        layer = Image.new("RGBA", (width // 2, height // 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        hue = (i / 8 + rng.random() * 0.1) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        cx = rng.randint(0, width // 2)
        cy = rng.randint(0, height // 2)
        rad = rng.randint(min(width, height) // 6, min(width, height) // 3)
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                  fill=(int(r * 255), int(g * 255), int(b * 255), rng.randint(40, 80)))
        layer = layer.filter(ImageFilter.GaussianBlur(radius=rad // 2))
        scaled = layer.resize((width, height), Image.LANCZOS)
        img = Image.alpha_composite(img, scaled)

    draw = ImageDraw.Draw(img, "RGBA")

    # Central text
    headline = strip_emoji(headline)
    title_font = _get_font(fonts, "title")
    sub_font = _get_font(fonts, "subtitle")

    max_w = width - 160
    wrapped = wrap_text(headline.upper(), title_font, max_w)
    lh = line_height(title_font, 20)
    total_h = len(wrapped) * lh + 80

    y = (height - total_h) // 2
    for ln in wrapped:
        tw = text_width(ln, title_font)
        x = (width - tw) // 2
        # Glow behind text
        draw.text((x + 2, y + 2), ln, fill=(255, 200, 50, 60), font=title_font)
        draw.text((x, y), ln, fill=(255, 255, 255, 255), font=title_font)
        y += lh

    # Subtitle
    y += 30
    sub_text = "SWIPE TO REVEAL"
    sw = text_width(sub_text, sub_font)
    draw.text(((width - sw) // 2, y), sub_text, fill=(200, 200, 220, 180), font=sub_font)

    # Holographic border around entire slide edge
    _draw_holographic_border(draw, 20, 20, width - 40, height - 40, thickness=6, seed=_RUN_SEED)

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    """Trading card slide — parse stats from lines, render full card."""
    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    stats, flavor = _parse_stats(lines)

    # Generate card number based on slide position
    card_number = f"#{slide_num:03d} / 100"

    img = _draw_card(
        fonts, headline or f"ARCHETYPE {slide_num}",
        stats, flavor, slide_num, width, height,
        card_number=card_number,
    )
    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    """Card back design — holographic pattern + CTA + disclaimer."""
    rng = _random.Random(slide_num * 200 + _RUN_SEED)
    img = Image.new("RGBA", (width, height), (*_OUTER_BG, 255))

    margin_x = 60
    margin_top = 50
    margin_bot = 80
    card_x = margin_x
    card_y = margin_top
    card_w = width - 2 * margin_x
    card_h = height - margin_top - margin_bot

    # Card back
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=20, fill=(*_CARD_BG, 245),
    )

    # Dense holographic pattern (crossing lines)
    for i in range(0, card_w, 30):
        hue = (i / card_w) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.8)
        draw.line(
            [(card_x + i, card_y), (card_x + card_w, card_y + card_h * i // card_w)],
            fill=(int(r * 255), int(g * 255), int(b * 255), 25), width=2,
        )
        draw.line(
            [(card_x, card_y + i * card_h // card_w), (card_x + i, card_y + card_h)],
            fill=(int(r * 255), int(g * 255), int(b * 255), 25), width=2,
        )

    # Holographic border
    _draw_holographic_border(draw, card_x, card_y, card_w, card_h,
                             thickness=5, seed=slide_num + _RUN_SEED)

    # Central logo / brand text
    cta_text = strip_emoji(cta_text)
    title_font = _get_font(fonts, "title")
    body_font = _get_font(fonts, "body")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")

    # "COLLECT THEM ALL" or CTA
    max_w = card_w - 100
    wrapped = wrap_text(cta_text.upper(), title_font, max_w)
    lh = line_height(title_font, 18)
    total_text_h = len(wrapped) * lh

    y = card_y + (card_h - total_text_h) // 2 - 60
    for ln in wrapped:
        tw = text_width(ln, title_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=(255, 255, 255, 255), font=title_font)
        y += lh

    # Sub-text
    y += 40
    sub_lines = ["toxshield.in", "Follow @toxshield.ai"]
    slh = line_height(small_font, 10)
    for sl in sub_lines:
        sw = text_width(sl, small_font)
        draw.text(((width - sw) // 2, y), sl, fill=(180, 175, 210, 200), font=small_font)
        y += slh

    # Disclaimer at bottom
    disc_y = card_y + card_h - 100
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        dw = text_width(disc_line, tiny_font)
        draw.text(((width - dw) // 2, disc_y), disc_line,
                  fill=(100, 95, 130, 160), font=tiny_font)
        disc_y += 28

    return img.convert("RGB")
