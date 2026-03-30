"""Arcane theme — dense neon graffiti + hextech energy on dark backgrounds.

Inspired by Netflix's Arcane series — Jinx's chaotic graffiti aesthetic with
multi-color neon doodles (blue, pink, green) covering the entire canvas,
energy glow effects, and dramatic atmospheric backgrounds.
"""

from __future__ import annotations

import math
import random as _random
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    FONT_SIZES, IMPACT_FONTS, MONO_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, wrap_text,
)

# ---------------------------------------------------------------------------
# Palettes — each slide gets a unique mood with 3 neon doodle colors
# ---------------------------------------------------------------------------

_AURORA_PALETTES = [
    # 1: Hextech Core
    {
        "base": (8, 5, 25),
        "blobs": [
            (0.15, 0.15, (0, 140, 255), 0.50, 100),
            (0.85, 0.30, (120, 40, 200), 0.40, 90),
            (0.50, 0.80, (0, 100, 220), 0.45, 80),
            (0.20, 0.70, (80, 0, 180), 0.35, 70),
        ],
        "neon": [(0, 180, 255), (255, 40, 120), (80, 255, 160)],
        "text": (210, 235, 255),
        "text_secondary": (160, 200, 240),
        "text_muted": (80, 110, 150),
    },
    # 2: Jinx's Chaos
    {
        "base": (20, 5, 30),
        "blobs": [
            (0.20, 0.20, (200, 0, 100), 0.45, 100),
            (0.80, 0.25, (180, 40, 220), 0.40, 90),
            (0.45, 0.75, (100, 20, 180), 0.50, 85),
            (0.85, 0.70, (0, 100, 255), 0.35, 80),
        ],
        "neon": [(255, 50, 130), (50, 160, 255), (100, 255, 180)],
        "text": (255, 230, 245),
        "text_secondary": (240, 190, 225),
        "text_muted": (150, 100, 140),
    },
    # 3: Zaun Undercity
    {
        "base": (5, 15, 10),
        "blobs": [
            (0.20, 0.15, (0, 180, 80), 0.45, 100),
            (0.75, 0.30, (0, 140, 120), 0.40, 90),
            (0.45, 0.75, (150, 120, 0), 0.40, 75),
            (0.10, 0.80, (0, 200, 50), 0.35, 80),
        ],
        "neon": [(50, 255, 80), (0, 180, 255), (255, 60, 140)],
        "text": (220, 255, 230),
        "text_secondary": (180, 235, 195),
        "text_muted": (90, 140, 100),
    },
    # 4: Piltover Gold
    {
        "base": (12, 8, 20),
        "blobs": [
            (0.20, 0.20, (180, 150, 50), 0.45, 100),
            (0.80, 0.25, (200, 170, 20), 0.40, 90),
            (0.45, 0.75, (160, 120, 40), 0.45, 80),
            (0.80, 0.80, (100, 80, 200), 0.35, 70),
        ],
        "neon": [(255, 200, 50), (50, 160, 255), (100, 255, 150)],
        "text": (255, 245, 220),
        "text_secondary": (230, 210, 170),
        "text_muted": (140, 120, 80),
    },
    # 5: Shimmer
    {
        "base": (22, 5, 22),
        "blobs": [
            (0.15, 0.25, (180, 50, 150), 0.45, 100),
            (0.80, 0.20, (120, 30, 220), 0.40, 95),
            (0.50, 0.70, (160, 40, 180), 0.50, 85),
            (0.20, 0.80, (80, 120, 240), 0.35, 80),
        ],
        "neon": [(220, 60, 255), (0, 200, 255), (255, 80, 150)],
        "text": (245, 225, 250),
        "text_secondary": (220, 195, 235),
        "text_muted": (140, 110, 155),
    },
]

_FONT_SIZES = {**FONT_SIZES, "title": 92, "subtitle": 64, "body": 48}

# Run-level seed — set by generate_carousel.py for unique images each run
_RUN_SEED = 0


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


def _palette(slide_num: int) -> dict:
    return _AURORA_PALETTES[(slide_num - 1) % len(_AURORA_PALETTES)]


def _pick_neon(pal: dict, rng) -> tuple:
    """Pick a random neon color from the palette's 3 neon colors."""
    return rng.choice(pal["neon"])


# ---------------------------------------------------------------------------
# Aurora gradient background
# ---------------------------------------------------------------------------

def _render_aurora_bg(width: int, height: int, slide_num: int) -> Image.Image:
    pal = _palette(slide_num)
    hw, hh = width // 2, height // 2
    img = Image.new("RGBA", (hw, hh), (*pal["base"], 255))

    for bx_rel, by_rel, color, r_factor, alpha in pal["blobs"]:
        layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        cx, cy = int(bx_rel * hw), int(by_rel * hh)
        r = int(min(hw, hh) * r_factor)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, alpha))
        layer = layer.filter(ImageFilter.GaussianBlur(radius=int(r * 0.6)))
        img = Image.alpha_composite(img, layer)

    return img.resize((width, height), Image.LANCZOS)


# ---------------------------------------------------------------------------
# GRAFFITI DOODLES — dense, chaotic, multi-color, full-canvas coverage
# ---------------------------------------------------------------------------

def _doodle_explosion_star(draw, x, y, scale, rng, color):
    """Large spiky explosion star — Jinx's chaos."""
    w = max(2, int(3 * scale))
    rays = rng.randint(6, 12)
    outer_r = int(rng.randint(25, 55) * scale)
    inner_r = int(outer_r * 0.4)
    offset = rng.uniform(0, math.pi / rays)

    points = []
    for i in range(rays * 2):
        angle = offset + (math.pi / rays) * i
        r = outer_r if i % 2 == 0 else inner_r
        points.append((x + int(r * math.cos(angle)), y + int(r * math.sin(angle))))
    draw.polygon(points, outline=(*color, rng.randint(160, 240)))


def _doodle_graffiti_arrow(draw, x, y, scale, rng, color):
    """Thick angular graffiti arrow."""
    w = max(3, int(4 * scale))
    opacity = rng.randint(160, 240)
    c = (*color, opacity)
    length = int(rng.randint(40, 80) * scale)
    angle = rng.uniform(0, math.pi * 2)
    x2 = x + int(length * math.cos(angle))
    y2 = y + int(length * math.sin(angle))
    draw.line([(x, y), (x2, y2)], fill=c, width=w)
    # Arrow head
    head = int(18 * scale)
    for da in [0.5, -0.5]:
        hx = x2 - int(head * math.cos(angle + da))
        hy = y2 - int(head * math.sin(angle + da))
        draw.line([(x2, y2), (hx, hy)], fill=c, width=w)


def _doodle_x_mark(draw, x, y, scale, rng, color):
    """Bold X mark — chaos symbol."""
    w = max(3, int(4 * scale))
    opacity = rng.randint(160, 240)
    c = (*color, opacity)
    size = int(rng.randint(15, 35) * scale)
    draw.line([(x - size, y - size), (x + size, y + size)], fill=c, width=w)
    draw.line([(x + size, y - size), (x - size, y + size)], fill=c, width=w)


def _doodle_scribble_circle(draw, x, y, scale, rng, color):
    """Messy hand-drawn circle — overlapping strokes."""
    w = max(2, int(3 * scale))
    opacity = rng.randint(140, 220)
    c = (*color, opacity)
    r = int(rng.randint(20, 50) * scale)
    for _ in range(rng.randint(2, 4)):
        dx, dy = rng.randint(-5, 5), rng.randint(-5, 5)
        draw.ellipse([x - r + dx, y - r + dy, x + r + dx, y + r + dy], outline=c, width=w)


def _doodle_lightning(draw, x, y, scale, rng, color):
    """Jagged lightning bolt."""
    w = max(2, int(3 * scale))
    opacity = rng.randint(170, 245)
    c = (*color, opacity)
    segments = rng.randint(4, 7)
    bolt_h = int(rng.randint(50, 110) * scale)
    seg_h = bolt_h // segments
    points = [(x, y)]
    cx, cy = x, y
    for _ in range(segments):
        cx += rng.randint(-int(22 * scale), int(22 * scale))
        cy += seg_h
        points.append((cx, cy))
    if len(points) >= 2:
        draw.line(points, fill=c, width=w, joint="curve")


def _doodle_hex_crystal(draw, x, y, scale, rng, color):
    """Elongated hexagonal crystal."""
    opacity = rng.randint(150, 235)
    c = (*color, opacity)
    ic = (*color, opacity // 2)
    w = max(2, int(3 * scale))
    h_size = int(rng.randint(25, 55) * scale)
    w_size = int(h_size * 0.45)
    points = [
        (x, y - h_size), (x + w_size, y - h_size // 2),
        (x + w_size, y + h_size // 2), (x, y + h_size),
        (x - w_size, y + h_size // 2), (x - w_size, y - h_size // 2),
    ]
    draw.polygon(points, outline=c)
    draw.line([(x, y - h_size + 4), (x, y + h_size - 4)], fill=ic, width=w)


def _doodle_gear(draw, x, y, scale, rng, color):
    """Steampunk gear/cog."""
    w = max(2, int(3 * scale))
    opacity = rng.randint(140, 220)
    c = (*color, opacity)
    r = int(rng.randint(22, 48) * scale)
    teeth = rng.choice([6, 8, 10])
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    tooth_len = int(r * 0.35)
    for i in range(teeth):
        angle = (math.pi * 2 / teeth) * i
        x1 = x + int(r * math.cos(angle))
        y1 = y + int(r * math.sin(angle))
        x2 = x + int((r + tooth_len) * math.cos(angle))
        y2 = y + int((r + tooth_len) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=c, width=w + 1)
    cr = max(3, int(4 * scale))
    draw.ellipse([x - cr, y - cr, x + cr, y + cr], fill=c)


def _doodle_rune(draw, x, y, scale, rng, color):
    """Arcane rune circle with geometric inner pattern."""
    opacity = rng.randint(140, 220)
    c = (*color, opacity)
    ic = (*color, opacity // 2)
    w = max(2, int(3 * scale))
    r = int(rng.randint(18, 42) * scale)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    ir = int(r * 0.6)
    pattern = rng.randint(0, 3)
    if pattern == 0:
        draw.line([(x - ir, y), (x + ir, y)], fill=ic, width=w)
        draw.line([(x, y - ir), (x, y + ir)], fill=ic, width=w)
    elif pattern == 1:
        pts = [(x + int(ir * math.cos(a)), y + int(ir * math.sin(a)))
               for a in [i * math.pi * 2 / 3 - math.pi / 2 for i in range(3)]]
        draw.polygon(pts, outline=ic)
    elif pattern == 2:
        draw.ellipse([x - ir, y - ir, x + ir, y + ir], outline=ic, width=w)
        dr = max(3, int(4 * scale))
        draw.ellipse([x - dr, y - dr, x + dr, y + dr], fill=c)
    else:
        draw.line([(x - ir, y - ir), (x + ir, y + ir)], fill=ic, width=w)
        draw.line([(x + ir, y - ir), (x - ir, y + ir)], fill=ic, width=w)


def _doodle_bomb(draw, x, y, scale, rng, color):
    """Cartoon bomb shape — Jinx's specialty."""
    opacity = rng.randint(150, 230)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(16, 35) * scale)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    # Fuse
    fuse_len = int(r * 0.8)
    fx, fy = x + r - 4, y - r + 4
    draw.line([(fx, fy), (fx + fuse_len // 2, fy - fuse_len)], fill=c, width=w)
    # Spark at tip
    sx, sy = fx + fuse_len // 2, fy - fuse_len
    spark = int(6 * scale)
    draw.line([(sx - spark, sy), (sx + spark, sy)], fill=c, width=2)
    draw.line([(sx, sy - spark), (sx, sy + spark)], fill=c, width=2)


def _doodle_bear_face(draw, x, y, scale, rng, color):
    """Abstract bear/animal face outline — from Arcane graffiti."""
    opacity = rng.randint(140, 220)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(22, 45) * scale)
    # Head
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    # Ears
    ear_r = int(r * 0.4)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.7)
        ey = y - int(r * 0.85)
        draw.ellipse([ex - ear_r, ey - ear_r, ex + ear_r, ey + ear_r], outline=c, width=w)
    # Eyes (X marks)
    eye_size = int(r * 0.2)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.35)
        ey = y - int(r * 0.1)
        draw.line([(ex - eye_size, ey - eye_size), (ex + eye_size, ey + eye_size)], fill=c, width=2)
        draw.line([(ex + eye_size, ey - eye_size), (ex - eye_size, ey + eye_size)], fill=c, width=2)


def _doodle_scratchy_lines(draw, x, y, scale, rng, color):
    """Cluster of short parallel scratchy lines."""
    w = max(2, int(2 * scale))
    opacity = rng.randint(120, 200)
    c = (*color, opacity)
    count = rng.randint(4, 9)
    line_len = int(rng.randint(15, 35) * scale)
    gap = int(rng.randint(5, 9) * scale)
    angle = rng.uniform(-0.5, 0.5)
    for i in range(count):
        x1 = x + i * gap
        x2 = x1 + int(line_len * math.sin(angle))
        y2 = y + int(line_len * math.cos(angle))
        draw.line([(x1, y), (x2, y2)], fill=c, width=w)


def _doodle_zigzag(draw, x, y, scale, rng, color):
    """Large zigzag line."""
    w = max(2, int(3 * scale))
    opacity = rng.randint(150, 230)
    c = (*color, opacity)
    segments = rng.randint(4, 8)
    step_x = int(rng.randint(14, 25) * scale)
    step_y = int(rng.randint(12, 22) * scale)
    angle = rng.uniform(-0.4, 0.4)
    points = []
    for i in range(segments):
        px = x + int(i * step_x * math.cos(angle))
        py = y + int(i * step_x * math.sin(angle)) + (step_y if i % 2 else -step_y)
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=c, width=w)


def _doodle_hex_particle(draw, x, y, scale, rng, color):
    """Diamond/rhombus hex particle."""
    opacity = rng.randint(140, 230)
    c = (*color, opacity)
    size = int(rng.randint(8, 22) * scale)
    points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
    if rng.random() > 0.4:
        draw.polygon(points, fill=c)
    else:
        draw.polygon(points, outline=c)


def _doodle_energy_arc(draw, x, y, scale, rng, color):
    """Curved energy arc with endpoint dots."""
    w = max(2, int(3 * scale))
    opacity = rng.randint(150, 230)
    c = (*color, opacity)
    length = int(rng.randint(50, 110) * scale)
    curve = rng.uniform(0.03, 0.08)
    angle = rng.uniform(0, math.pi * 2)
    points = []
    for t in range(0, length, 3):
        px = x + int(t * math.cos(angle + curve * t))
        py = y + int(t * math.sin(angle + curve * t))
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=c, width=w, joint="curve")
        dr = max(3, int(4 * scale))
        for px, py in [points[0], points[-1]]:
            draw.ellipse([px - dr, py - dr, px + dr, py + dr], fill=c)


def _doodle_heart(draw, x, y, scale, rng, color):
    """Graffiti heart."""
    opacity = rng.randint(150, 230)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    size = int(rng.randint(15, 30) * scale)
    draw.ellipse([x - size, y - size, x, y], outline=c, width=w)
    draw.ellipse([x, y - size, x + size, y], outline=c, width=w)
    draw.line([(x - size, y - size // 4), (x, y + size)], fill=c, width=w)
    draw.line([(x + size, y - size // 4), (x, y + size)], fill=c, width=w)


def _doodle_splatter(draw, x, y, scale, rng, color):
    """Cluster of dots — paint splatter."""
    opacity = rng.randint(140, 220)
    spread = int(30 * scale)
    for _ in range(rng.randint(5, 14)):
        dx = rng.randint(-spread, spread)
        dy = rng.randint(-spread, spread)
        r = int(rng.randint(2, 7) * scale)
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r],
                     fill=(*color, opacity))


def _doodle_potion(draw, x, y, scale, rng, color):
    """Potion vial silhouette."""
    opacity = rng.randint(150, 230)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    h = int(rng.randint(35, 60) * scale)
    neck_w = int(8 * scale)
    body_w = int(20 * scale)
    neck_h = int(h * 0.35)
    draw.rectangle([x - neck_w // 2, y, x + neck_w // 2, y + neck_h], outline=c, width=w)
    draw.ellipse([x - body_w, y + neck_h - 2, x + body_w, y + h], outline=c, width=w)
    draw.line([(x - neck_w // 2 - 3, y), (x + neck_w // 2 + 3, y)], fill=c, width=w + 1)


# ---------------------------------------------------------------------------
# NEW CHARACTER FACES — Jinx graffiti reference art
# ---------------------------------------------------------------------------

def _doodle_jinx_skull(draw, x, y, scale, rng, color):
    """Jinx's signature monster skull — spiky crown, spiral eyes, grid teeth."""
    opacity = rng.randint(160, 240)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(30, 55) * scale)

    # Head circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)

    # Spiky hair rays radiating from top half
    spikes = rng.randint(6, 10)
    spike_len = int(r * rng.uniform(0.5, 0.8))
    for i in range(spikes):
        angle = math.pi + (math.pi / (spikes + 1)) * (i + 1)  # top half arc
        angle += rng.uniform(-0.15, 0.15)  # roughen
        x1 = x + int(r * math.cos(angle))
        y1 = y + int(r * math.sin(angle))
        x2 = x + int((r + spike_len) * math.cos(angle))
        y2 = y + int((r + spike_len) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=c, width=max(2, w - 1))

    # Spiral eyes — concentric circles
    eye_r = int(r * 0.22)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.35)
        ey = y - int(r * 0.15)
        for ring in range(3):
            rr = eye_r - ring * int(eye_r * 0.3)
            if rr > 1:
                draw.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], outline=c, width=max(1, w - 1))

    # Grid teeth mouth — horizontal bars
    mouth_top = y + int(r * 0.25)
    mouth_bot = y + int(r * 0.65)
    mouth_left = x - int(r * 0.55)
    mouth_right = x + int(r * 0.55)
    bars = rng.randint(4, 6)
    bar_gap = (mouth_bot - mouth_top) / bars
    for i in range(bars + 1):
        by = int(mouth_top + i * bar_gap)
        draw.line([(mouth_left, by), (mouth_right, by)], fill=c, width=max(1, w - 1))
    # Vertical edges of mouth
    draw.line([(mouth_left, mouth_top), (mouth_left, mouth_bot)], fill=c, width=w)
    draw.line([(mouth_right, mouth_top), (mouth_right, mouth_bot)], fill=c, width=w)


def _doodle_xx_smiley(draw, x, y, scale, rng, color):
    """X-X dead eyes smiley — round face, X eyes, mouth variants."""
    opacity = rng.randint(160, 240)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(25, 50) * scale)

    # Head
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)

    # X eyes
    eye_size = int(r * 0.25)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.35)
        ey = y - int(r * 0.15)
        draw.line([(ex - eye_size, ey - eye_size), (ex + eye_size, ey + eye_size)], fill=c, width=w)
        draw.line([(ex + eye_size, ey - eye_size), (ex - eye_size, ey + eye_size)], fill=c, width=w)

    # Mouth variant
    mouth_y = y + int(r * 0.35)
    mouth_w = int(r * 0.5)
    variant = rng.randint(0, 2)
    if variant == 0:
        # Curved smile
        draw.arc([x - mouth_w, mouth_y - int(mouth_w * 0.5),
                  x + mouth_w, mouth_y + int(mouth_w * 0.5)],
                 start=0, end=180, fill=c, width=w)
    elif variant == 1:
        # Stitched zigzag mouth
        segs = rng.randint(5, 8)
        pts = []
        for i in range(segs):
            px = x - mouth_w + int((2 * mouth_w / (segs - 1)) * i)
            py = mouth_y + (int(6 * scale) if i % 2 else -int(6 * scale))
            pts.append((px, py))
        if len(pts) >= 2:
            draw.line(pts, fill=c, width=w)
    else:
        # W-wave mouth
        qw = mouth_w // 2
        pts = [(x - mouth_w, mouth_y), (x - qw, mouth_y + int(8 * scale)),
               (x, mouth_y - int(4 * scale)), (x + qw, mouth_y + int(8 * scale)),
               (x + mouth_w, mouth_y)]
        draw.line(pts, fill=c, width=w)

    # 30% chance of drip trails
    if rng.random() < 0.3:
        for _ in range(rng.randint(2, 4)):
            dx = rng.randint(-int(r * 0.6), int(r * 0.6))
            drip_len = int(rng.randint(20, 60) * scale)
            draw.line([(x + dx, y + r), (x + dx + rng.randint(-3, 3), y + r + drip_len)],
                      fill=c, width=max(1, w - 1))
            # Bulb at drip tip
            br = max(2, int(3 * scale))
            draw.ellipse([x + dx - br, y + r + drip_len - br,
                          x + dx + br, y + r + drip_len + br], fill=c)


def _doodle_simple_smiley(draw, x, y, scale, rng, color):
    """Simple smiley face — circle, dot eyes, curved smile."""
    opacity = rng.randint(150, 235)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(20, 45) * scale)

    # Head
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)

    # Dot eyes
    eye_r = max(2, int(r * 0.12))
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.3)
        ey = y - int(r * 0.2)
        draw.ellipse([ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r], fill=c)

    # U-smile
    smile_w = int(r * 0.45)
    smile_y = y + int(r * 0.1)
    draw.arc([x - smile_w, smile_y, x + smile_w, smile_y + int(smile_w * 0.8)],
             start=0, end=180, fill=c, width=w)

    # 25% chance of drip trails
    if rng.random() < 0.25:
        for _ in range(rng.randint(2, 5)):
            dx = rng.randint(-int(r * 0.7), int(r * 0.7))
            drip_len = int(rng.randint(25, 70) * scale)
            draw.line([(x + dx, y + r), (x + dx, y + r + drip_len)],
                      fill=c, width=max(1, w - 1))
            br = max(2, int(2 * scale))
            draw.ellipse([x + dx - br, y + r + drip_len - br,
                          x + dx + br, y + r + drip_len + br], fill=c)


def _doodle_three_bumps_skull(draw, x, y, scale, rng, color):
    """Skull with three rounded bumps on top (brain/crown variant)."""
    opacity = rng.randint(160, 240)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(28, 50) * scale)

    # Head circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)

    # Three bumps on top
    bump_r = int(r * 0.32)
    for bx_off in [-0.5, 0, 0.5]:
        bx = x + int(r * bx_off)
        by = y - r - int(bump_r * 0.4)
        draw.ellipse([bx - bump_r, by - bump_r, bx + bump_r, by + bump_r],
                     outline=c, width=w)

    # Spiral eyes (same as jinx_skull)
    eye_r = int(r * 0.2)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.35)
        ey = y - int(r * 0.1)
        for ring in range(2):
            rr = eye_r - ring * int(eye_r * 0.4)
            if rr > 1:
                draw.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], outline=c, width=max(1, w - 1))

    # Grid teeth
    mouth_top = y + int(r * 0.3)
    mouth_bot = y + int(r * 0.6)
    mouth_left = x - int(r * 0.5)
    mouth_right = x + int(r * 0.5)
    bars = rng.randint(3, 5)
    bar_gap = (mouth_bot - mouth_top) / bars
    for i in range(bars + 1):
        by = int(mouth_top + i * bar_gap)
        draw.line([(mouth_left, by), (mouth_right, by)], fill=c, width=max(1, w - 1))
    draw.line([(mouth_left, mouth_top), (mouth_left, mouth_bot)], fill=c, width=w)
    draw.line([(mouth_right, mouth_top), (mouth_right, mouth_bot)], fill=c, width=w)


def _doodle_crosshair_target(draw, x, y, scale, rng, color):
    """Crosshair target — circle with + lines through center."""
    opacity = rng.randint(150, 235)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(18, 40) * scale)

    # Circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    # Crosshair lines extending slightly beyond circle
    ext = int(r * 0.2)
    draw.line([(x - r - ext, y), (x + r + ext, y)], fill=c, width=w)
    draw.line([(x, y - r - ext), (x, y + r + ext)], fill=c, width=w)
    # Center dot (50% chance)
    if rng.random() > 0.5:
        dr = max(2, int(4 * scale))
        draw.ellipse([x - dr, y - dr, x + dr, y + dr], fill=c)


def _doodle_halfmoon_grin(draw, x, y, scale, rng, color):
    """Crescent half-moon face with sharp teeth."""
    opacity = rng.randint(150, 235)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    r = int(rng.randint(22, 45) * scale)

    # Crescent arc (bottom half)
    draw.arc([x - r, y - r, x + r, y + r], start=10, end=170, fill=c, width=w)

    # Sharp teeth along the inner curve
    teeth = rng.randint(5, 9)
    for i in range(teeth):
        angle = math.radians(10 + (160 / (teeth + 1)) * (i + 1))
        tx = x + int(r * math.cos(angle))
        ty = y + int(r * math.sin(angle))
        tooth_h = int(rng.randint(6, 14) * scale)
        tooth_w = int(5 * scale)
        pts = [(tx - tooth_w, ty), (tx, ty - tooth_h), (tx + tooth_w, ty)]
        draw.polygon(pts, fill=c)

    # Eyes above the crescent
    eye_size = int(r * 0.15)
    ey = y - int(r * 0.15)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.35)
        # X-eye or dot (50/50)
        if rng.random() > 0.5:
            draw.line([(ex - eye_size, ey - eye_size), (ex + eye_size, ey + eye_size)], fill=c, width=w)
            draw.line([(ex + eye_size, ey - eye_size), (ex - eye_size, ey + eye_size)], fill=c, width=w)
        else:
            draw.ellipse([ex - eye_size, ey - eye_size, ex + eye_size, ey + eye_size], fill=c)


# ---------------------------------------------------------------------------
# GRAFFITI TEXT — ToxShield-adapted tags
# ---------------------------------------------------------------------------

_GRAFFITI_WORDS = [
    "TOXIC!", "BOOM", "HAHA", "LIAR", "RUN", "FAKE",
    "DENY", "TRAP", "NAH", "HA HA HA",
]


def _doodle_graffiti_text(draw, x, y, scale, rng, color):
    """Scratchy graffiti text tag — ToxShield toxic relationship words."""
    opacity = rng.randint(120, 200)
    c = (*color, opacity)
    word = rng.choice(_GRAFFITI_WORDS)

    # Find a bold font
    font_size = int(rng.randint(28, 48) * scale)
    font = None
    for p in IMPACT_FONTS:
        if p.exists():
            try:
                font = ImageFont.truetype(str(p), font_size,
                                          index=0 if str(p).endswith(".ttc") else 0)
                break
            except (OSError, IOError):
                continue
    if font is None:
        font = ImageFont.load_default()

    # Draw with stroke for spray-paint feel
    stroke_w = max(1, int(2 * scale))
    stroke_c = (*color, opacity // 3)

    # Draw text with stroke outline
    draw.text((x, y), word, fill=c, font=font,
              stroke_width=stroke_w, stroke_fill=stroke_c)


# ---------------------------------------------------------------------------
# NEW SMALL DOODLE ELEMENTS
# ---------------------------------------------------------------------------

def _doodle_splatter_drip(draw, x, y, scale, rng, color):
    """Paint splatter with dripping trails — upgraded from simple dots."""
    opacity = rng.randint(140, 220)
    c = (*color, opacity)

    # Large center blob
    blob_r = int(rng.randint(8, 18) * scale)
    draw.ellipse([x - blob_r, y - blob_r, x + blob_r, y + blob_r], fill=c)

    # Drip trails hanging down
    drips = rng.randint(2, 5)
    for _ in range(drips):
        dx = rng.randint(-blob_r, blob_r)
        drip_len = int(rng.randint(30, 120) * scale)
        wobble = rng.randint(-4, 4)
        drip_w = max(1, int(rng.randint(2, 4) * scale))
        draw.line([(x + dx, y + blob_r), (x + dx + wobble, y + blob_r + drip_len)],
                  fill=c, width=drip_w)
        # Bulb at drip tip
        br = max(2, int(drip_w * 0.8))
        draw.ellipse([x + dx + wobble - br, y + blob_r + drip_len - br,
                      x + dx + wobble + br, y + blob_r + drip_len + br], fill=c)

    # Satellite dots
    spread = int(35 * scale)
    for _ in range(rng.randint(4, 10)):
        sx = rng.randint(-spread, spread)
        sy = rng.randint(-spread, spread)
        sr = int(rng.randint(1, 5) * scale)
        draw.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=c)


def _doodle_small_star(draw, x, y, scale, rng, color):
    """Small 4-pointed decorative star — scatter element."""
    opacity = rng.randint(150, 240)
    c = (*color, opacity)
    size = int(rng.randint(8, 18) * scale)
    inner = int(size * 0.3)

    points = []
    for i in range(8):
        angle = (math.pi / 4) * i - math.pi / 8
        r = size if i % 2 == 0 else inner
        points.append((x + int(r * math.cos(angle)), y + int(r * math.sin(angle))))

    if rng.random() > 0.5:
        draw.polygon(points, fill=c)
    else:
        draw.polygon(points, outline=c)


def _doodle_checkmark(draw, x, y, scale, rng, color):
    """Simple V-shaped checkmark."""
    opacity = rng.randint(150, 235)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    size = int(rng.randint(10, 20) * scale)

    # V-shape
    draw.line([(x - int(size * 0.5), y - int(size * 0.2)),
               (x, y + int(size * 0.5))], fill=c, width=w)
    draw.line([(x, y + int(size * 0.5)),
               (x + int(size * 0.7), y - int(size * 0.6))], fill=c, width=w)


def _doodle_exclamation(draw, x, y, scale, rng, color):
    """Exclamation mark — vertical line + dot."""
    opacity = rng.randint(150, 235)
    c = (*color, opacity)
    w = max(2, int(3 * scale))
    h = int(rng.randint(15, 30) * scale)

    # Vertical bar
    draw.line([(x, y), (x, y + h)], fill=c, width=w + 1)
    # Dot below
    gap = int(5 * scale)
    dr = max(2, int(3 * scale))
    draw.ellipse([x - dr, y + h + gap - dr, x + dr, y + h + gap + dr], fill=c)


def _doodle_drip_line(draw, x, y, scale, rng, color):
    """Long vertical drip line with bulb tip — paint drip."""
    opacity = rng.randint(130, 220)
    c = (*color, opacity)
    w = max(1, int(rng.randint(2, 3) * scale))
    length = int(rng.randint(40, 150) * scale)

    # Slightly wobbly vertical line
    points = [(x, y)]
    segments = max(2, length // 20)
    for i in range(1, segments + 1):
        px = x + rng.randint(-3, 3)
        py = y + int((length / segments) * i)
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=c, width=w, joint="curve")

    # Bulb at tip
    br = max(2, int(w * 1.5))
    tip_x, tip_y = points[-1]
    draw.ellipse([tip_x - br, tip_y - br, tip_x + br, tip_y + br], fill=c)


# All doodle functions — weighted for variety
_DOODLE_FUNCS = [
    # Character faces — signature Jinx graffiti elements
    _doodle_jinx_skull,
    _doodle_jinx_skull,
    _doodle_xx_smiley,
    _doodle_xx_smiley,
    _doodle_simple_smiley,
    _doodle_three_bumps_skull,
    _doodle_crosshair_target,
    _doodle_halfmoon_grin,
    # Graffiti text tags — high frequency (refs are packed with them)
    _doodle_graffiti_text,
    _doodle_graffiti_text,
    _doodle_graffiti_text,
    # Existing doodles (kept, reweighted)
    _doodle_explosion_star,
    _doodle_graffiti_arrow,
    _doodle_graffiti_arrow,
    _doodle_x_mark,
    _doodle_x_mark,
    _doodle_x_mark,
    _doodle_scribble_circle,
    _doodle_lightning,
    _doodle_lightning,
    _doodle_zigzag,
    _doodle_zigzag,
    _doodle_splatter_drip,
    _doodle_splatter_drip,
    # New small scatter elements
    _doodle_small_star,
    _doodle_small_star,
    _doodle_small_star,
    _doodle_checkmark,
    _doodle_exclamation,
    _doodle_drip_line,
    _doodle_drip_line,
    # Reduced-weight existing doodles
    _doodle_hex_crystal,
    _doodle_bomb,
    _doodle_bear_face,
    _doodle_scratchy_lines,
    _doodle_hex_particle,
    _doodle_energy_arc,
    _doodle_heart,
]


def _draw_graffiti(draw: ImageDraw.Draw, width: int, height: int, slide_num: int,
                   count: int = 60, clear_center: bool = True):
    """Draw dense chaotic graffiti covering the ENTIRE canvas.

    If clear_center=True, reduces density in the center zone where text goes.
    If clear_center=False (no-text mode), graffiti goes EVERYWHERE.
    """
    rng = _random.Random(slide_num * 777 + _RUN_SEED)
    pal = _palette(slide_num)

    # Define zones — full canvas coverage
    margin = 80
    center_x1 = width // 4
    center_x2 = width * 3 // 4
    center_y1 = height // 3
    center_y2 = height * 2 // 3

    for _ in range(count):
        # Pick position — anywhere on canvas
        x = rng.randint(10, width - 10)
        y = rng.randint(10, height - 10)

        # Skip some items in center zone if text mode
        if clear_center and center_x1 < x < center_x2 and center_y1 < y < center_y2:
            if rng.random() < 0.7:  # 70% chance to skip center
                continue

        scale = rng.uniform(0.6, 1.5)
        func = rng.choice(_DOODLE_FUNCS)
        neon_color = _pick_neon(pal, rng)
        func(draw, x, y, scale, rng, neon_color)


# ---------------------------------------------------------------------------
# Energy particles — falling hex energy drops
# ---------------------------------------------------------------------------

def _draw_energy_particles(img: Image.Image, slide_num: int, count: int = 30) -> Image.Image:
    """Falling energy particles / hex rain effect."""
    w, h = img.size
    rng = _random.Random(slide_num * 555 + _RUN_SEED)
    pal = _palette(slide_num)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for _ in range(count):
        px = rng.randint(0, w)
        py = rng.randint(0, h)
        neon = _pick_neon(pal, rng)
        opacity = rng.randint(60, 180)

        kind = rng.random()
        if kind < 0.5:
            # Falling line (short vertical streak)
            length = rng.randint(8, 30)
            draw.line([(px, py), (px + rng.randint(-3, 3), py + length)],
                      fill=(*neon, opacity), width=2)
        elif kind < 0.8:
            # Glowing dot
            r = rng.randint(2, 5)
            draw.ellipse([px - r, py - r, px + r, py + r], fill=(*neon, opacity))
        else:
            # Tiny diamond
            s = rng.randint(3, 7)
            pts = [(px, py - s), (px + s, py), (px, py + s), (px - s, py)]
            draw.polygon(pts, fill=(*neon, opacity))

    return Image.alpha_composite(img.convert("RGBA"), layer)


# ---------------------------------------------------------------------------
# Hex energy glow — large atmospheric glow effects
# ---------------------------------------------------------------------------

def _draw_energy_glow(img: Image.Image, slide_num: int, count: int = 4) -> Image.Image:
    """Large soft energy glow circles for atmospheric depth."""
    w, h = img.size
    rng = _random.Random(slide_num * 333 + _RUN_SEED)
    pal = _palette(slide_num)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for _ in range(count):
        bx = rng.randint(-100, w + 100)
        by = rng.randint(-100, h + 100)
        r = rng.randint(80, 200)
        neon = _pick_neon(pal, rng)
        alpha = rng.randint(15, 35)
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=(*neon, alpha))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=30))
    return Image.alpha_composite(img.convert("RGBA"), layer)


# ---------------------------------------------------------------------------
# Full background composition
# ---------------------------------------------------------------------------

def _draw_splatter_layer(img: Image.Image, slide_num: int, count: int = 12) -> Image.Image:
    """Large soft paint splatter blobs — background layer before graffiti."""
    w, h = img.size
    rng = _random.Random(slide_num * 222 + _RUN_SEED)
    pal = _palette(slide_num)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for _ in range(count):
        sx = rng.randint(-50, w + 50)
        sy = rng.randint(-50, h + 50)
        sr = rng.randint(40, 120)
        neon = _pick_neon(pal, rng)
        alpha = rng.randint(20, 50)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(*neon, alpha))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=25))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def _make_background(width: int, height: int, slide_num: int,
                     graffiti_count: int = 75, clear_center: bool = True) -> Image.Image:
    """Compose: aurora bg + splatter layer + energy glow + graffiti doodles + energy particles."""
    img = _render_aurora_bg(width, height, slide_num)
    img = _draw_splatter_layer(img, slide_num)
    img = _draw_energy_glow(img, slide_num)

    # Graffiti drawn on top
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_graffiti(draw, width, height, slide_num,
                   count=graffiti_count, clear_center=clear_center)

    # Energy particles on top of everything
    img = _draw_energy_particles(img, slide_num)
    return img


# ---------------------------------------------------------------------------
# Glassmorphism card — dark moody frosted glass
# ---------------------------------------------------------------------------

def _draw_glass_card(bg: Image.Image, x: int, y: int, w: int, h: int) -> Image.Image:
    result = bg.copy()
    region = bg.crop((x, y, x + w, y + h)).convert("RGBA")
    blurred = region.filter(ImageFilter.GaussianBlur(radius=15))
    overlay = Image.new("RGBA", (w, h), (5, 5, 20, 100))
    card = Image.alpha_composite(blurred, overlay)
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        [1, 1, w - 2, h - 2], radius=20,
        outline=(150, 180, 255, 40), width=2,
    )
    result.paste(card.convert("RGB"), (x, y), card)
    return result


# ===========================================================================
# Slide Rendering
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    img = _make_background(width, height, slide_num, graffiti_count=80)
    pal = _palette(slide_num)

    headline = strip_emoji(headline).upper()
    font = _get_font(fonts, "title")
    max_text_w = width - 200
    wrapped = wrap_text(headline, font, max_text_w)
    lh = line_height(font, 28)
    total_h = len(wrapped) * lh

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
    img = _make_background(width, height, slide_num, graffiti_count=75)
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
    img = _make_background(width, height, slide_num, graffiti_count=70)
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
    card_y = (height - card_h) // 2 - 60
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

    disclaimer_y = height - 140
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        bbox = tiny_font.getbbox(disc_line)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, disclaimer_y), disc_line, fill=(*pal["text_muted"], 180), font=tiny_font)
        disclaimer_y += 30

    return img.convert("RGB")
