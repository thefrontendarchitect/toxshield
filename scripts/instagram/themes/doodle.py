"""Doodle theme — B&W hand-drawn sketch aesthetic (ToxShield default)."""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from . import (
    FONT_SIZES, ROUNDED_BODY_FONTS, ROUNDED_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, wrap_text,
)

# Run-level seed — set by generate_carousel.py for unique images each run
_RUN_SEED = 0

COLORS = {
    "bg":             (0, 0, 0),
    "text_primary":   (255, 255, 255),
    "text_secondary": (200, 200, 200),
    "text_muted":     (100, 100, 100),
    "doodle":         (255, 255, 255),
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


def get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = FONT_SIZES.get(size_key, 28)
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


# ===========================================================================
# Doodle Drawing Functions
# ===========================================================================

def _doodle_squiggle(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(3 * scale)
    points = []
    length = int(rng.randint(60, 120) * scale)
    amplitude = int(rng.randint(8, 18) * scale)
    angle = rng.uniform(0, math.pi * 2)
    for t in range(0, length, 4):
        px = x + int(t * math.cos(angle) - amplitude * math.sin(t * 0.15) * math.sin(angle))
        py = y + int(t * math.sin(angle) + amplitude * math.sin(t * 0.15) * math.cos(angle))
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w, joint="curve")


def _doodle_star(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(2 * scale)
    size = int(rng.randint(15, 30) * scale)
    num_rays = rng.choice([4, 5, 6])
    offset = rng.uniform(0, math.pi / num_rays)
    for i in range(num_rays):
        angle = offset + (math.pi * 2 / num_rays) * i
        x2 = x + int(size * math.cos(angle))
        y2 = y + int(size * math.sin(angle))
        draw.line([(x, y), (x2, y2)], fill=color, width=w)


def _doodle_zigzag(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(2 * scale)
    points = []
    segments = rng.randint(4, 8)
    step_x = int(rng.randint(12, 22) * scale)
    step_y = int(rng.randint(10, 18) * scale)
    angle = rng.uniform(-0.3, 0.3)
    for i in range(segments):
        px = x + int(i * step_x * math.cos(angle))
        py = y + int(i * step_x * math.sin(angle)) + (step_y if i % 2 else -step_y)
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w)


def _doodle_scribble_circle(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(2 * scale)
    r = int(rng.randint(18, 40) * scale)
    for _ in range(rng.randint(2, 3)):
        dx, dy = rng.randint(-4, 4), rng.randint(-4, 4)
        draw.ellipse([x - r + dx, y - r + dy, x + r + dx, y + r + dy], outline=color, width=w)


def _doodle_hatching(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(2 * scale)
    count = rng.randint(4, 8)
    h = int(rng.randint(20, 45) * scale)
    gap = int(rng.randint(6, 10) * scale)
    angle = rng.uniform(-0.3, 0.3)
    for i in range(count):
        x1 = x + i * gap
        x2 = x1 + int(h * math.sin(angle))
        y2 = y + int(h * math.cos(angle))
        draw.line([(x1, y), (x2, y2)], fill=color, width=w)


def _doodle_swoosh(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(3 * scale)
    length = int(rng.randint(50, 100) * scale)
    curve = rng.uniform(0.02, 0.06)
    angle = rng.uniform(0, math.pi * 2)
    points = []
    for t in range(0, length, 3):
        px = x + int(t * math.cos(angle + curve * t))
        py = y + int(t * math.sin(angle + curve * t))
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w, joint="curve")


def _doodle_checkmark(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(3 * scale)
    size = int(rng.randint(15, 25) * scale)
    if rng.random() > 0.5:
        draw.line([(x, y), (x + size // 3, y + size)], fill=color, width=w)
        draw.line([(x + size // 3, y + size), (x + size, y - size // 3)], fill=color, width=w)
    else:
        draw.line([(x, y), (x + size, y + size)], fill=color, width=w)
        draw.line([(x + size, y), (x, y + size)], fill=color, width=w)


def _doodle_spiral(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(2 * scale)
    points = []
    turns = rng.uniform(1.5, 3.0)
    max_r = int(rng.randint(15, 30) * scale)
    direction = rng.choice([1, -1])
    for t in range(0, int(turns * 60)):
        a = direction * t * math.pi / 30
        r = max_r * t / (turns * 60)
        points.append((x + int(r * math.cos(a)), y + int(r * math.sin(a))))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w, joint="curve")


def _doodle_dots(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    spread = int(20 * scale)
    for _ in range(rng.randint(3, 7)):
        dx, dy = rng.randint(-spread, spread), rng.randint(-spread, spread)
        r = int(rng.randint(2, 5) * scale)
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=color)


def _doodle_arrow(draw, x, y, scale, opacity, rng):
    color = (*COLORS["doodle"], opacity)
    w = int(2 * scale)
    length = int(rng.randint(30, 60) * scale)
    angle = rng.uniform(0, math.pi * 2)
    x2 = x + int(length * math.cos(angle))
    y2 = y + int(length * math.sin(angle))
    draw.line([(x, y), (x2, y2)], fill=color, width=w)
    head_size = int(12 * scale)
    for da in [0.4, -0.4]:
        hx = x2 - int(head_size * math.cos(angle + da))
        hy = y2 - int(head_size * math.sin(angle + da))
        draw.line([(x2, y2), (hx, hy)], fill=color, width=w)


_DOODLE_FUNCS = [
    _doodle_squiggle, _doodle_star, _doodle_zigzag, _doodle_scribble_circle,
    _doodle_hatching, _doodle_swoosh, _doodle_checkmark, _doodle_spiral,
    _doodle_dots, _doodle_arrow,
]


def draw_doodles(draw, width, height, seed=0, count=14, bottom_margin=160):
    rng = random.Random(seed)
    margin = 160
    zones = [
        (20, 20, width - 20, margin),
        (20, height - bottom_margin, width - 20, height - 20),
        (20, margin, margin, height - bottom_margin),
        (width - margin, margin, width - 20, height - bottom_margin),
    ]
    for _ in range(count):
        zone = zones[rng.randint(0, len(zones) - 1)]
        x = rng.randint(zone[0], max(zone[0], zone[2] - 1))
        y = rng.randint(zone[1], max(zone[1], zone[3] - 1))
        func = rng.choice(_DOODLE_FUNCS)
        opacity = rng.randint(160, 240)
        scale = rng.uniform(0.7, 1.3)
        func(draw, x, y, scale, opacity, rng)


# ===========================================================================
# Slide Rendering
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (width, height)], fill=(*COLORS["bg"], 255))
    draw_doodles(draw, width, height, seed=slide_num * 1000 + _RUN_SEED)

    headline = strip_emoji(headline)
    font = get_font(fonts, "title")
    max_text_w = width - 240
    wrapped = wrap_text(headline, font, max_text_w)
    lh = line_height(font, 24)
    total_h = len(wrapped) * lh
    y = (height - total_h) // 2

    for ln in wrapped:
        bbox = font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=font)
        y += lh

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (width, height)], fill=(*COLORS["bg"], 255))
    draw_doodles(draw, width, height, seed=slide_num * 1000 + _RUN_SEED)

    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    subtitle_font = get_font(fonts, "subtitle")
    body_font = get_font(fonts, "body")
    max_text_w = width - 240

    wrapped_hl = wrap_text(headline, subtitle_font, max_text_w) if headline else []
    hl_lh = line_height(subtitle_font, 20)

    all_wrapped = []
    for line in lines:
        for sub in line.split("\n"):
            all_wrapped.extend(wrap_text(sub, body_font, max_text_w))
    body_lh = line_height(body_font, 24)

    total_h = 0
    if wrapped_hl:
        total_h += len(wrapped_hl) * hl_lh + 40
    total_h += len(all_wrapped) * body_lh
    y = (height - total_h) // 2

    if wrapped_hl:
        for ln in wrapped_hl:
            bbox = subtitle_font.getbbox(ln)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), ln, fill=COLORS["text_primary"], font=subtitle_font)
            y += hl_lh
        y += 40

    body_color = COLORS["text_secondary"] if headline else COLORS["text_primary"]
    for ln in all_wrapped:
        bbox = body_font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=body_color, font=body_font)
        y += body_lh

    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (width, height)], fill=(*COLORS["bg"], 255))
    draw_doodles(draw, width, height, seed=slide_num * 1000, count=10, bottom_margin=280)

    cta_text = strip_emoji(cta_text)
    cta_font = get_font(fonts, "subtitle")
    small_font = get_font(fonts, "small")
    tiny_font = get_font(fonts, "tiny")
    max_text_w = width - 240

    wrapped_cta = wrap_text(cta_text, cta_font, max_text_w)
    cta_lh = line_height(cta_font, 15)

    sub_lines = ["Follow @toxshield.ai", "Link in bio"]
    sl_lh = line_height(small_font, 12)

    total_h = len(wrapped_cta) * cta_lh + 50 + len(sub_lines) * sl_lh + 120
    y = (height - total_h) // 2

    for ln in wrapped_cta:
        bbox = cta_font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=COLORS["text_primary"], font=cta_font)
        y += cta_lh

    y += 50
    for ln in sub_lines:
        bbox = small_font.getbbox(ln)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, fill=COLORS["text_secondary"], font=small_font)
        y += sl_lh

    disclaimer_y = height - 140
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*COLORS["text_muted"], 180), font=tiny_font)
        disclaimer_y += 30

    return img.convert("RGB")
