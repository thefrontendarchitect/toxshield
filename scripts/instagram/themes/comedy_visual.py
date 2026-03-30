"""Comedy Visual theme — standup comedy stage with Arcane graffiti base.

Draws a comedy club stage scene ON TOP of the Arcane graffiti background:
brick wall, stage floor, spotlight, microphone, stage lights, and a screen
where joke text appears. Beat-driven lighting shifts with joke rhythm.
"""

from __future__ import annotations

import math
import random as _random
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import arcane as _arcane
from . import (
    FONT_SIZES, IMPACT_FONTS, MONO_FONTS,
    find_font, wrap_text, line_height, strip_emoji, SAFETY_DISCLAIMER,
)

# ---------------------------------------------------------------------------
# Run-level seed — set by generate_carousel.py
# ---------------------------------------------------------------------------

_RUN_SEED = 0
_TOTAL_SLIDES = 9

_FONT_SIZES = {**FONT_SIZES, "title": 92, "subtitle": 56, "body": 48, "small": 32}


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in IMPACT_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in MONO_FONTS:
        if p.exists():
            fonts["body"] = fonts["small"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 28)
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
# Beat System — controls lighting, colors, intensity
# ---------------------------------------------------------------------------

_BEAT_CONFIG = {
    "opener": {
        "graffiti": 65, "splatter": 10, "glow": 4, "particles": 20,
        "palette_idx": 2,
        "spotlight_alpha": 35, "overlay_alpha": 50,
        "stage_lights": [(200, 160, 80, 70), (80, 120, 200, 55)],
        "screen_glow": (80, 255, 140),
    },
    "setup": {
        "graffiti": 75, "splatter": 12, "glow": 4, "particles": 25,
        "palette_idx": 0,
        "spotlight_alpha": 50, "overlay_alpha": 40,
        "stage_lights": [(60, 100, 220, 70), (140, 60, 200, 60), (60, 180, 220, 50)],
        "screen_glow": (60, 160, 255),
    },
    "punchline": {
        "graffiti": 120, "splatter": 20, "glow": 7, "particles": 50,
        "palette_idx": 1,
        "spotlight_alpha": 90, "overlay_alpha": 25,
        "stage_lights": [(255, 50, 130, 90), (0, 220, 255, 80), (200, 60, 255, 70)],
        "screen_glow": (255, 50, 150),
    },
    "callback": {
        "graffiti": 110, "splatter": 18, "glow": 6, "particles": 45,
        "palette_idx": 4,
        "spotlight_alpha": 70, "overlay_alpha": 35,
        "stage_lights": [(160, 60, 255, 80), (60, 120, 255, 70)],
        "screen_glow": (200, 80, 255),
    },
    "closer": {
        "graffiti": 115, "splatter": 22, "glow": 8, "particles": 55,
        "palette_idx": 3,
        "spotlight_alpha": 80, "overlay_alpha": 30,
        "stage_lights": [(255, 200, 50, 85), (220, 160, 40, 70), (200, 140, 60, 60)],
        "screen_glow": (255, 210, 60),
    },
}


def _get_beat_type(slide_num: int, total_slides: int = 9,
                   hint: Optional[str] = None) -> str:
    if hint:
        return hint
    if slide_num == 1:
        return "opener"
    if slide_num >= total_slides:
        return "closer"
    if slide_num == total_slides - 1:
        return "callback"
    return "punchline" if slide_num % 2 == 1 else "setup"


# ---------------------------------------------------------------------------
# Filtered doodle list — NO text doodles for background graffiti
# ---------------------------------------------------------------------------

_COMEDY_DOODLE_FUNCS = [f for f in _arcane._DOODLE_FUNCS
                         if f is not _arcane._doodle_graffiti_text]


def _draw_comedy_graffiti(draw, width, height, slide_num, count, palette_idx):
    rng = _random.Random(slide_num * 777 + _RUN_SEED)
    pal = _arcane._AURORA_PALETTES[palette_idx % len(_arcane._AURORA_PALETTES)]
    for _ in range(count):
        x = rng.randint(10, width - 10)
        y = rng.randint(10, height - 10)
        scale = rng.uniform(0.6, 1.5)
        func = rng.choice(_COMEDY_DOODLE_FUNCS)
        neon_color = rng.choice(pal["neon"])
        func(draw, x, y, scale, rng, neon_color)


# ---------------------------------------------------------------------------
# Arcane graffiti base layer
# ---------------------------------------------------------------------------

def _make_graffiti_base(width, height, slide_num, beat_type):
    params = _BEAT_CONFIG[beat_type]
    pal_idx = params["palette_idx"]
    _arcane._RUN_SEED = _RUN_SEED

    forced_slide = pal_idx + 1
    img = _arcane._render_aurora_bg(width, height, forced_slide)
    img = _arcane._draw_splatter_layer(img, slide_num, count=params["splatter"])
    img = _arcane._draw_energy_glow(img, slide_num, count=params["glow"])

    draw = ImageDraw.Draw(img, "RGBA")
    _draw_comedy_graffiti(draw, width, height, slide_num,
                          count=params["graffiti"], palette_idx=pal_idx)

    img = _arcane._draw_energy_particles(img, slide_num, count=params["particles"])
    return img


# ---------------------------------------------------------------------------
# Stage Elements
# ---------------------------------------------------------------------------

def _draw_dark_overlay(img, alpha):
    """Semi-transparent dark overlay to dim graffiti for stage elements."""
    overlay = Image.new("RGBA", img.size, (5, 5, 10, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _draw_brick_wall(img, width, height, slide_num):
    """Dark brick wall in upper portion — semi-transparent so graffiti bleeds through."""
    rng = _random.Random(slide_num * 111 + _RUN_SEED + 42)
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    wall_bottom = int(height * 0.76)
    brick_w, brick_h = 82, 36
    mortar = 3
    row_h = brick_h + mortar

    y = 0
    row = 0
    while y < wall_bottom:
        offset = (brick_w // 2) if row % 2 else 0
        x = -offset
        while x < width + brick_w:
            # Zaun industrial concrete tones (grey-green-brown, not warm red)
            r = 28 + rng.randint(-6, 8)
            g = 26 + rng.randint(-5, 8)
            b = 22 + rng.randint(-4, 6)
            draw.rectangle(
                [x + mortar, y + mortar, x + brick_w - 1, y + brick_h - 1],
                fill=(r, g, b, 85),
            )
            x += brick_w + mortar
        y += row_h
        row += 1

    return Image.alpha_composite(img.convert("RGBA"), layer)


def _draw_stage_floor(img, width, height):
    """Dark wood stage floor at bottom."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    floor_top = int(height * 0.78)

    # Floor gradient (dark wood)
    for y in range(floor_top, height):
        progress = (y - floor_top) / (height - floor_top)
        r = int(38 - 15 * progress)
        g = int(26 - 12 * progress)
        b = int(18 - 10 * progress)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 230))

    # Stage edge highlight
    draw.line([(0, floor_top), (width, floor_top)], fill=(60, 45, 30, 200), width=3)
    draw.line([(0, floor_top + 3), (width, floor_top + 3)], fill=(45, 32, 20, 150), width=1)

    # Wood plank lines
    plank_gap = (height - floor_top) // 5
    for i in range(1, 5):
        py = floor_top + i * plank_gap
        draw.line([(0, py), (width, py)], fill=(25, 16, 10, 100), width=1)

    return Image.alpha_composite(img.convert("RGBA"), layer)


def _draw_spotlight(img, width, height, alpha):
    """Spotlight cone from above — warm white, soft edges."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Trapezoid spotlight cone
    top_w = int(width * 0.08)
    bot_w = int(width * 0.55)
    top_y = 0
    bot_y = int(height * 0.82)
    cx = int(width * 0.45)  # Slightly left of center (where mic is)

    # Draw gradient trapezoid with decreasing alpha
    steps = 40
    for i in range(steps):
        progress = i / steps
        y1 = int(top_y + (bot_y - top_y) * progress)
        y2 = int(top_y + (bot_y - top_y) * (progress + 1 / steps))
        w1 = int(top_w + (bot_w - top_w) * progress)
        w2 = int(top_w + (bot_w - top_w) * (progress + 1 / steps))
        a = int(alpha * (1 - progress * 0.6))
        draw.polygon(
            [(cx - w1, y1), (cx + w1, y1), (cx + w2, y2), (cx - w2, y2)],
            fill=(220, 240, 255, a),  # Hex-tech blue-white
        )

    layer = layer.filter(ImageFilter.GaussianBlur(radius=35))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def _draw_stage_lights(img, width, height, light_configs):
    """Colored stage lights along top edge."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    n = len(light_configs)
    for i, (r, g, b, a) in enumerate(light_configs):
        x = int(width * (i + 1) / (n + 1))
        radius = 80
        # Light fixture dot
        draw.ellipse([x - 8, 5, x + 8, 21], fill=(60, 60, 70, 200))
        # Glow cone
        draw.ellipse([x - radius, -radius // 2, x + radius, radius],
                     fill=(r, g, b, a))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=25))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def _draw_microphone(img, width, height):
    """Microphone stand silhouette — center-left of stage."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    cx = int(width * 0.43)
    stand_top = int(height * 0.52)
    stand_bot = int(height * 0.77)

    # Stand pole
    draw.line([(cx, stand_top + 25), (cx, stand_bot)], fill=(50, 50, 55, 200), width=4)

    # Base spread (V-shape)
    base_w = 35
    draw.line([(cx - base_w, stand_bot + 5), (cx, stand_bot - 8)], fill=(50, 50, 55, 180), width=3)
    draw.line([(cx + base_w, stand_bot + 5), (cx, stand_bot - 8)], fill=(50, 50, 55, 180), width=3)

    # Mic head (rounded rectangle)
    mic_w, mic_h = 16, 28
    draw.rounded_rectangle(
        [cx - mic_w, stand_top, cx + mic_w, stand_top + mic_h],
        radius=10, fill=(55, 55, 60, 220),
    )

    # Highlight edge on mic
    draw.rounded_rectangle(
        [cx - mic_w + 3, stand_top + 2, cx - mic_w + 6, stand_top + mic_h - 4],
        radius=3, fill=(80, 80, 90, 120),
    )

    # Mic clip
    draw.rectangle([cx - 6, stand_top + mic_h, cx + 6, stand_top + mic_h + 8],
                   fill=(45, 45, 50, 200))

    return Image.alpha_composite(img.convert("RGBA"), layer)


def _draw_stage_screen(img, width, height, text_lines, font, glow_color, is_title=False):
    """Screen/monitor on stage wall with joke text inside."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Screen dimensions
    scr_w = int(width * 0.78)
    scr_h = int(height * 0.30)
    scr_x = (width - scr_w) // 2
    scr_y = int(height * 0.14)

    # Screen background (very dark)
    draw.rounded_rectangle(
        [scr_x, scr_y, scr_x + scr_w, scr_y + scr_h],
        radius=12, fill=(8, 8, 15, 225),
    )

    # Screen border glow — hex-tech energy border
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.rounded_rectangle(
        [scr_x - 3, scr_y - 3, scr_x + scr_w + 3, scr_y + scr_h + 3],
        radius=15, outline=(*glow_color, 220), width=4,
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))
    layer = Image.alpha_composite(layer, glow_layer)

    # Sharp border on top
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        [scr_x, scr_y, scr_x + scr_w, scr_y + scr_h],
        radius=12, outline=(*glow_color, 200), width=2,
    )

    # Render text inside screen — WHITE text with colored glow behind
    text_area_w = scr_w - 60
    text_area_x = scr_x + 30
    lh = line_height(font, 14 if is_title else 18)

    all_wrapped = []
    for line in text_lines:
        if line:
            all_wrapped.extend(wrap_text(line, font, text_area_w))
    total_text_h = len(all_wrapped) * lh
    text_y = scr_y + (scr_h - total_text_h) // 2

    for ln in all_wrapped:
        bbox = font.getbbox(ln)
        tw = bbox[2] - bbox[0]
        tx = text_area_x + (text_area_w - tw) // 2
        # Layer 1: Colored glow shadow (behind)
        draw.text((tx, text_y), ln, fill=(*glow_color, 80), font=font,
                  stroke_width=6, stroke_fill=(*glow_color, 40))
        # Layer 2: Dark stroke for contrast
        draw.text((tx, text_y), ln, fill=(240, 240, 245, 255), font=font,
                  stroke_width=3, stroke_fill=(5, 5, 15, 200))
        text_y += lh

    return Image.alpha_composite(img.convert("RGBA"), layer)


# ---------------------------------------------------------------------------
# Full Stage Composition
# ---------------------------------------------------------------------------

def _compose_stage(width, height, slide_num, beat_type,
                   text_lines, font, is_title=False):
    """Full composition: graffiti base → stage elements → screen with text."""
    cfg = _BEAT_CONFIG[beat_type]

    # 1. Arcane graffiti base
    img = _make_graffiti_base(width, height, slide_num, beat_type)

    # 2. Dark overlay (dim graffiti for stage)
    img = _draw_dark_overlay(img, cfg["overlay_alpha"])

    # 3. Brick wall (subtle texture — graffiti dominates)
    img = _draw_brick_wall(img, width, height, slide_num)

    # 4. Graffiti ON TOP of brick wall (Zaun style — walls are tagged)
    wall_graffiti_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wall_draw = ImageDraw.Draw(wall_graffiti_layer, "RGBA")
    _draw_comedy_graffiti(wall_draw, width, int(height * 0.76),
                          slide_num + 100, count=cfg["graffiti"] // 2,
                          palette_idx=cfg["palette_idx"])
    img = Image.alpha_composite(img.convert("RGBA"), wall_graffiti_layer)

    # 5. Stage floor
    img = _draw_stage_floor(img, width, height)

    # 6. Stage lights (intense)
    img = _draw_stage_lights(img, width, height, cfg["stage_lights"])

    # 6. Spotlight
    img = _draw_spotlight(img, width, height, cfg["spotlight_alpha"])

    # 7. Microphone
    img = _draw_microphone(img, width, height)

    # 8. Screen with text
    if text_lines:
        img = _draw_stage_screen(img, width, height, text_lines, font,
                                 cfg["screen_glow"], is_title=is_title)

    return img


# ===========================================================================
# Slide Rendering
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    beat = _get_beat_type(slide_num, _TOTAL_SLIDES, hint="opener")
    headline = strip_emoji(headline).upper()
    font = _get_font(fonts, "title")
    img = _compose_stage(width, height, slide_num, beat,
                         [headline], font, is_title=True)
    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    beat = _get_beat_type(slide_num, _TOTAL_SLIDES)
    body_font = _get_font(fonts, "body")

    text_lines = []
    if headline:
        text_lines.append(strip_emoji(headline))
    for line in lines:
        text_lines.append(strip_emoji(line))

    img = _compose_stage(width, height, slide_num, beat, text_lines, body_font)
    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    beat = _get_beat_type(slide_num, _TOTAL_SLIDES, hint="closer")
    cta_text = strip_emoji(cta_text)
    font = _get_font(fonts, "subtitle")

    text_lines = [cta_text, "", "toxshield.in | @toxshield.ai"]
    img = _compose_stage(width, height, slide_num, beat, text_lines, font)

    # Safety disclaimer at bottom
    tiny_font = _get_font(fonts, "tiny")
    draw = ImageDraw.Draw(img, "RGBA")
    disclaimer_y = height - 120
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(120, 120, 130, 150), font=tiny_font)
        disclaimer_y += 28

    return img.convert("RGB")
