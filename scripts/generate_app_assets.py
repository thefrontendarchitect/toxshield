"""
ToxShield App Assets — Arcane Graffiti Neon Art.

Jinx-style chaotic graffiti, aurora backgrounds, neon energy, paint drips.
NOT a corporate shield icon — this is Zaun undercity street art.

Output:
  - android/app/src/main/res/mipmap-*/ic_launcher*.png
  - android/app/src/main/res/drawable*/splash.png
  - src/app/favicon.ico + apple-icon.png
"""

from __future__ import annotations

import math
import random as _random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
ANDROID_RES = ROOT / "android" / "app" / "src" / "main" / "res"

# ---------------------------------------------------------------------------
# Arcane Color Palette
# ---------------------------------------------------------------------------
BG = (8, 5, 25)
NEON_MINT = (80, 255, 160)
NEON_CYAN = (0, 180, 255)
NEON_MAGENTA = (255, 40, 120)
NEON_COLORS = [NEON_MINT, NEON_CYAN, NEON_MAGENTA]

# The T color for icon and splash
T_COLOR = NEON_MAGENTA

# Aurora blobs for backgrounds
AURORA_BLOBS = [
    (0.15, 0.15, (0, 140, 255), 0.50, 100),
    (0.85, 0.30, (120, 40, 200), 0.40, 90),
    (0.50, 0.80, (0, 100, 220), 0.45, 80),
    (0.20, 0.70, (80, 0, 180), 0.35, 70),
    (0.65, 0.15, (200, 0, 100), 0.30, 60),
]


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
def load_bold_font(size: int) -> ImageFont.FreeTypeFont:
    """Generic bold font for non-icon text."""
    for path, idx in [
        ("/System/Library/Fonts/Supplemental/Futura.ttc", 4),
        ("/System/Library/Fonts/Avenir Next.ttc", 8),
        ("/System/Library/Fonts/Supplemental/Futura.ttc", 2),
        ("/System/Library/Fonts/Helvetica.ttc", 1),
    ]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# Arcane-style font for the icon "T" — Bodoni 72 Bold (Art Nouveau high-contrast serifs)
_FONTS_DIR = Path(__file__).parent / "fonts"

def load_arcane_font(size: int) -> ImageFont.FreeTypeFont:
    """Load Arcane-style font for the icon T — dramatic serif with Art Nouveau feel."""
    candidates = [
        ("/System/Library/Fonts/Supplemental/Copperplate.ttc", 2),  # Copperplate Bold
        (str(_FONTS_DIR / "Arcane Nine.otf"), None),                 # Arcane Nine fan font
        ("/System/Library/Fonts/Supplemental/Didot.ttc", 2),        # Didot Bold
        ("/System/Library/Fonts/Supplemental/Bodoni 72.ttc", 1),    # Bodoni 72 Bold
    ]
    for path, idx in candidates:
        try:
            if idx is not None:
                return ImageFont.truetype(path, size, index=idx)
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return load_bold_font(size)


def load_impact_font(size: int) -> ImageFont.FreeTypeFont:
    for path in [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def load_mono_font(size: int) -> ImageFont.FreeTypeFont:
    for path in [
        "/System/Library/Fonts/SFMono-Bold.otf",
        "/System/Library/Fonts/Menlo.ttc",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Glow Effect (multi-layer)
# ---------------------------------------------------------------------------
def apply_glow(
    base: Image.Image,
    shape: Image.Image,
    layers: list[tuple[int, int]] | None = None,
) -> Image.Image:
    """Apply multi-layer glow. layers = [(blur_radius, max_alpha), ...]"""
    if layers is None:
        layers = [(30, 60), (12, 150)]
    result = base.copy()
    for blur_r, max_a in layers:
        g = shape.copy().filter(ImageFilter.GaussianBlur(radius=blur_r))
        r, gr, b, a = g.split()
        a = a.point(lambda x, ma=max_a: min(x, ma))
        g = Image.merge("RGBA", (r, gr, b, a))
        result = Image.alpha_composite(result, g)
    result = Image.alpha_composite(result, shape)
    return result


# ---------------------------------------------------------------------------
# Aurora Background
# ---------------------------------------------------------------------------
def render_aurora(width: int, height: int, blobs=None, intensity: float = 1.0) -> Image.Image:
    """Rich aurora gradient background with visible color blobs."""
    hw, hh = max(1, width // 2), max(1, height // 2)
    img = Image.new("RGBA", (hw, hh), (*BG, 255))
    if blobs is None:
        blobs = AURORA_BLOBS
    for bx, by, color, rf, alpha in blobs:
        layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        cx, cy = int(bx * hw), int(by * hh)
        r = int(min(hw, hh) * rf)
        a = int(alpha * intensity)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
        layer = layer.filter(ImageFilter.GaussianBlur(radius=int(r * 0.6)))
        img = Image.alpha_composite(img, layer)
    return img.resize((width, height), Image.LANCZOS)


# ---------------------------------------------------------------------------
# DOODLE FUNCTIONS — Ported from arcane.py
# ---------------------------------------------------------------------------
def doodle_x_mark(draw, x, y, scale, rng, color):
    w = max(3, int(4 * scale))
    c = (*color, rng.randint(160, 240))
    size = int(rng.randint(15, 35) * scale)
    draw.line([(x - size, y - size), (x + size, y + size)], fill=c, width=w)
    draw.line([(x + size, y - size), (x - size, y + size)], fill=c, width=w)


def doodle_lightning(draw, x, y, scale, rng, color):
    w = max(2, int(3 * scale))
    c = (*color, rng.randint(170, 245))
    segs = rng.randint(4, 7)
    bolt_h = int(rng.randint(50, 110) * scale)
    seg_h = bolt_h // segs
    pts = [(x, y)]
    cx, cy = x, y
    for _ in range(segs):
        cx += rng.randint(-int(22 * scale), int(22 * scale))
        cy += seg_h
        pts.append((cx, cy))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w, joint="curve")


def doodle_hex_crystal(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(150, 235))
    ic = (*color, rng.randint(60, 120))
    w = max(2, int(3 * scale))
    h_size = int(rng.randint(25, 55) * scale)
    w_size = int(h_size * 0.45)
    pts = [
        (x, y - h_size), (x + w_size, y - h_size // 2),
        (x + w_size, y + h_size // 2), (x, y + h_size),
        (x - w_size, y + h_size // 2), (x - w_size, y - h_size // 2),
    ]
    draw.polygon(pts, outline=c)
    draw.line([(x, y - h_size + 4), (x, y + h_size - 4)], fill=ic, width=w)


def doodle_hex_particle(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(140, 230))
    size = int(rng.randint(8, 22) * scale)
    pts = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
    if rng.random() > 0.4:
        draw.polygon(pts, fill=c)
    else:
        draw.polygon(pts, outline=c)


def doodle_small_star(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(150, 240))
    size = int(rng.randint(8, 18) * scale)
    inner = int(size * 0.3)
    pts = []
    for i in range(8):
        angle = (math.pi / 4) * i - math.pi / 8
        r = size if i % 2 == 0 else inner
        pts.append((x + int(r * math.cos(angle)), y + int(r * math.sin(angle))))
    if rng.random() > 0.5:
        draw.polygon(pts, fill=c)
    else:
        draw.polygon(pts, outline=c)


def doodle_explosion_star(draw, x, y, scale, rng, color):
    w = max(2, int(3 * scale))
    rays = rng.randint(6, 12)
    outer_r = int(rng.randint(25, 55) * scale)
    inner_r = int(outer_r * 0.4)
    offset = rng.uniform(0, math.pi / rays)
    pts = []
    for i in range(rays * 2):
        angle = offset + (math.pi / rays) * i
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((x + int(r * math.cos(angle)), y + int(r * math.sin(angle))))
    draw.polygon(pts, outline=(*color, rng.randint(160, 240)))


def doodle_energy_arc(draw, x, y, scale, rng, color):
    w = max(2, int(3 * scale))
    c = (*color, rng.randint(150, 230))
    length = int(rng.randint(50, 110) * scale)
    curve = rng.uniform(0.03, 0.08)
    angle = rng.uniform(0, math.pi * 2)
    pts = []
    for t in range(0, length, 3):
        px = x + int(t * math.cos(angle + curve * t))
        py = y + int(t * math.sin(angle + curve * t))
        pts.append((px, py))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w, joint="curve")
        dr = max(3, int(4 * scale))
        for px, py in [pts[0], pts[-1]]:
            draw.ellipse([px - dr, py - dr, px + dr, py + dr], fill=c)


def doodle_splatter_drip(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(140, 220))
    blob_r = int(rng.randint(8, 18) * scale)
    draw.ellipse([x - blob_r, y - blob_r, x + blob_r, y + blob_r], fill=c)
    for _ in range(rng.randint(2, 5)):
        dx = rng.randint(-blob_r, blob_r)
        drip_len = int(rng.randint(30, 120) * scale)
        wobble = rng.randint(-4, 4)
        drip_w = max(1, int(rng.randint(2, 4) * scale))
        draw.line([(x + dx, y + blob_r), (x + dx + wobble, y + blob_r + drip_len)],
                  fill=c, width=drip_w)
        br = max(2, int(drip_w * 0.8))
        draw.ellipse([x + dx + wobble - br, y + blob_r + drip_len - br,
                      x + dx + wobble + br, y + blob_r + drip_len + br], fill=c)
    spread = int(35 * scale)
    for _ in range(rng.randint(4, 10)):
        sx = rng.randint(-spread, spread)
        sy = rng.randint(-spread, spread)
        sr = int(rng.randint(1, 5) * scale)
        draw.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=c)


def doodle_scribble_circle(draw, x, y, scale, rng, color):
    w = max(2, int(3 * scale))
    c = (*color, rng.randint(140, 220))
    r = int(rng.randint(20, 50) * scale)
    for _ in range(rng.randint(2, 4)):
        dx, dy = rng.randint(-5, 5), rng.randint(-5, 5)
        draw.ellipse([x - r + dx, y - r + dy, x + r + dx, y + r + dy], outline=c, width=w)


def doodle_graffiti_arrow(draw, x, y, scale, rng, color):
    w = max(3, int(4 * scale))
    c = (*color, rng.randint(160, 240))
    length = int(rng.randint(40, 80) * scale)
    angle = rng.uniform(0, math.pi * 2)
    x2 = x + int(length * math.cos(angle))
    y2 = y + int(length * math.sin(angle))
    draw.line([(x, y), (x2, y2)], fill=c, width=w)
    head = int(18 * scale)
    for da in [0.5, -0.5]:
        hx = x2 - int(head * math.cos(angle + da))
        hy = y2 - int(head * math.sin(angle + da))
        draw.line([(x2, y2), (hx, hy)], fill=c, width=w)


def doodle_drip_line(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(130, 220))
    w = max(1, int(rng.randint(2, 3) * scale))
    length = int(rng.randint(40, 150) * scale)
    pts = [(x, y)]
    segs = max(2, length // 20)
    for i in range(1, segs + 1):
        px = x + rng.randint(-3, 3)
        py = y + int((length / segs) * i)
        pts.append((px, py))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w, joint="curve")
    br = max(2, int(w * 1.5))
    tip_x, tip_y = pts[-1]
    draw.ellipse([tip_x - br, tip_y - br, tip_x + br, tip_y + br], fill=c)


def doodle_rune_circle(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(100, 180))
    ic = (*color, rng.randint(40, 90))
    w = max(2, int(3 * scale))
    r = int(rng.randint(18, 42) * scale)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    ir = int(r * 0.6)
    pattern = rng.randint(0, 2)
    if pattern == 0:
        draw.line([(x - ir, y), (x + ir, y)], fill=ic, width=w)
        draw.line([(x, y - ir), (x, y + ir)], fill=ic, width=w)
    elif pattern == 1:
        pts = [(x + int(ir * math.cos(a)), y + int(ir * math.sin(a)))
               for a in [i * math.pi * 2 / 3 - math.pi / 2 for i in range(3)]]
        draw.polygon(pts, outline=ic)
    else:
        draw.ellipse([x - ir, y - ir, x + ir, y + ir], outline=ic, width=w)


def doodle_crosshair(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(150, 235))
    w = max(2, int(3 * scale))
    r = int(rng.randint(18, 40) * scale)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    ext = int(r * 0.2)
    draw.line([(x - r - ext, y), (x + r + ext, y)], fill=c, width=w)
    draw.line([(x, y - r - ext), (x, y + r + ext)], fill=c, width=w)
    if rng.random() > 0.5:
        dr = max(2, int(4 * scale))
        draw.ellipse([x - dr, y - dr, x + dr, y + dr], fill=c)


def doodle_gear(draw, x, y, scale, rng, color):
    w = max(2, int(3 * scale))
    c = (*color, rng.randint(140, 220))
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


def doodle_xx_smiley(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(160, 240))
    w = max(2, int(3 * scale))
    r = int(rng.randint(25, 50) * scale)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    eye_size = int(r * 0.25)
    for dx in [-1, 1]:
        ex = x + dx * int(r * 0.35)
        ey = y - int(r * 0.15)
        draw.line([(ex - eye_size, ey - eye_size), (ex + eye_size, ey + eye_size)], fill=c, width=w)
        draw.line([(ex + eye_size, ey - eye_size), (ex - eye_size, ey + eye_size)], fill=c, width=w)
    mouth_y = y + int(r * 0.35)
    mouth_w = int(r * 0.5)
    draw.arc([x - mouth_w, mouth_y - int(mouth_w * 0.5),
              x + mouth_w, mouth_y + int(mouth_w * 0.5)],
             start=0, end=180, fill=c, width=w)


_GRAFFITI_WORDS = ["TOXIC!", "LIAR", "RUN", "FAKE", "NAH", "HA HA", "DENY", "TRAP", "BOOM"]


def doodle_graffiti_text(draw, x, y, scale, rng, color):
    c = (*color, rng.randint(140, 220))
    word = rng.choice(_GRAFFITI_WORDS)
    font_size = int(rng.randint(28, 48) * scale)
    font = load_impact_font(font_size)
    stroke_w = max(1, int(2 * scale))
    stroke_c = (*color, rng.randint(30, 70))
    draw.text((x, y), word, fill=c, font=font,
              stroke_width=stroke_w, stroke_fill=stroke_c)


def doodle_zigzag(draw, x, y, scale, rng, color):
    w = max(2, int(3 * scale))
    c = (*color, rng.randint(150, 230))
    segs = rng.randint(4, 8)
    step_x = int(rng.randint(14, 25) * scale)
    step_y = int(rng.randint(12, 22) * scale)
    angle = rng.uniform(-0.4, 0.4)
    pts = []
    for i in range(segs):
        px = x + int(i * step_x * math.cos(angle))
        py = y + int(i * step_x * math.sin(angle)) + (step_y if i % 2 else -step_y)
        pts.append((px, py))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w)


# All doodle functions with weights
DOODLE_FUNCS = [
    doodle_x_mark, doodle_x_mark, doodle_x_mark,
    doodle_lightning, doodle_lightning,
    doodle_small_star, doodle_small_star, doodle_small_star,
    doodle_hex_particle, doodle_hex_particle,
    doodle_hex_crystal,
    doodle_explosion_star,
    doodle_energy_arc,
    doodle_splatter_drip,
    doodle_scribble_circle,
    doodle_graffiti_arrow, doodle_graffiti_arrow,
    doodle_drip_line, doodle_drip_line,
    doodle_rune_circle,
    doodle_crosshair, doodle_crosshair,
    doodle_gear,
    doodle_xx_smiley,
    doodle_graffiti_text, doodle_graffiti_text, doodle_graffiti_text,
    doodle_zigzag, doodle_zigzag,
]


def draw_graffiti(draw, width, height, count, rng, clear_center=True, center_r=0.3):
    """Scatter graffiti doodles across the canvas."""
    cx, cy = width // 2, height // 2
    max_dim = max(width, height)
    clear_r = min(width, height) * center_r

    for _ in range(count):
        x = rng.randint(0, width)
        y = rng.randint(0, height)

        # Reduce density near center if requested
        if clear_center:
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist < clear_r and rng.random() < 0.7:
                continue

        scale = rng.uniform(0.4, 1.2) * (max_dim / 1024)
        color = rng.choice(NEON_COLORS)
        func = rng.choice(DOODLE_FUNCS)
        func(draw, x, y, scale, rng, color)


# ---------------------------------------------------------------------------
# T WITH PAINT DRIPS
# ---------------------------------------------------------------------------
def draw_t_with_drips(draw, cx, cy, font_size, rng):
    """Draw a bold T with paint drip trails from the bottom."""
    font = load_arcane_font(font_size)
    bbox = draw.textbbox((0, 0), "T", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]

    # Draw the T
    draw.text((tx, ty), "T", fill=(*T_COLOR, 255), font=font)

    # Paint drip trails from the bottom of the T
    t_bottom = ty + th
    t_left = tx
    t_right = tx + tw
    for _ in range(rng.randint(3, 6)):
        dx = rng.randint(t_left + int(tw * 0.1), t_right - int(tw * 0.1))
        drip_len = rng.randint(int(font_size * 0.3), int(font_size * 0.8))
        drip_w = max(2, int(font_size * 0.02))
        pts = [(dx, t_bottom)]
        py = t_bottom
        for _ in range(drip_len // 8):
            py += 8
            px = dx + rng.randint(-2, 2)
            pts.append((px, py))
        if len(pts) >= 2:
            draw.line(pts, fill=(*T_COLOR, 200), width=drip_w, joint="curve")
        # Bulb at drip tip
        br = max(2, drip_w + 1)
        draw.ellipse([pts[-1][0] - br, pts[-1][1] - br,
                      pts[-1][0] + br, pts[-1][1] + br],
                     fill=(*T_COLOR, 200))

    return tx, ty, tw, th


# ---------------------------------------------------------------------------
# ICON RENDERER — Toxic Targeting Reticle
# ---------------------------------------------------------------------------
def render_icon(size: int = 1024, transparent_bg: bool = False) -> Image.Image:
    """Render the Toxic Targeting Reticle icon."""
    M = 1024
    cx, cy = M // 2, M // 2

    # --- Background: dark + subtle hex grid ---
    if transparent_bg:
        img = Image.new("RGBA", (M, M), (0, 0, 0, 0))
        # Subtle aurora tint within the adaptive safe zone
        aurora = render_aurora(M, M, intensity=0.35)
        img = Image.alpha_composite(img, aurora)
    else:
        img = render_aurora(M, M, intensity=0.35)

    # Hex grid
    grid = render_hex_grid(M, M)
    img = Image.alpha_composite(img, grid)

    # Content radius (for adaptive icons, stay within 66% safe zone)
    safe = int(M * 0.30) if transparent_bg else int(M * 0.40)

    # --- Layer 1: Outer targeting ring with notch gaps ---
    reticle = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    rd = ImageDraw.Draw(reticle)
    ring_r = safe
    ring_w = max(5, int(M * 0.008))
    gap = 18  # degrees of gap at N/S/E/W

    # Draw ring as arcs with gaps at 0, 90, 180, 270 degrees
    for start_deg in [0, 90, 180, 270]:
        rd.arc([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
               start=start_deg + gap // 2, end=start_deg + 90 - gap // 2,
               fill=(*NEON_CYAN, 200), width=ring_w)

    # Notch tick marks at the gaps (small perpendicular lines)
    tick_len = int(M * 0.03)
    for angle_deg in [0, 90, 180, 270]:
        rad = math.radians(angle_deg)
        # Outer tick
        ox = cx + int((ring_r + tick_len) * math.cos(rad))
        oy = cy + int((ring_r + tick_len) * math.sin(rad))
        ix = cx + int((ring_r - tick_len) * math.cos(rad))
        iy = cy + int((ring_r - tick_len) * math.sin(rad))
        rd.line([(ix, iy), (ox, oy)], fill=(*NEON_CYAN, 200), width=ring_w)

    img = apply_glow(img, reticle, layers=[(18, 60), (6, 120)])

    # --- Layer 2: Inner magenta ring ---
    inner = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    inner_d = ImageDraw.Draw(inner)
    inner_r = int(ring_r * 0.65)
    inner_d.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                    outline=(*NEON_MAGENTA, 80), width=max(2, int(M * 0.003)))
    img = apply_glow(img, inner, layers=[(10, 40), (4, 70)])

    # --- Layer 3: Crosshair lines (stop before the T) ---
    cross = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cross)
    cross_w = max(2, int(M * 0.003))
    t_gap = int(M * 0.14)  # gap around center where T goes

    # Horizontal lines
    cd.line([(cx - ring_r + tick_len, cy), (cx - t_gap, cy)],
            fill=(*NEON_CYAN, 70), width=cross_w)
    cd.line([(cx + t_gap, cy), (cx + ring_r - tick_len, cy)],
            fill=(*NEON_CYAN, 70), width=cross_w)
    # Vertical lines
    cd.line([(cx, cy - ring_r + tick_len), (cx, cy - t_gap)],
            fill=(*NEON_CYAN, 70), width=cross_w)
    cd.line([(cx, cy + t_gap), (cx, cy + ring_r - tick_len)],
            fill=(*NEON_CYAN, 70), width=cross_w)
    img = Image.alpha_composite(img, cross)

    # --- Layer 4: Scan lines ---
    scan = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for y_off in [-0.12, 0.08, 0.22]:
        sy = cy + int(ring_r * y_off)
        sd.line([(cx - ring_r, sy), (cx + ring_r, sy)],
                fill=(*NEON_CYAN, 20), width=1)
    img = Image.alpha_composite(img, scan)

    # --- Layer 5: The "T" — massive, bold, triple glow ---
    t_size = int(M * 0.48)
    font = load_arcane_font(t_size)
    bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), "T", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = cx - tw // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]

    # Cyan outer halo
    t_cyan = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    ImageDraw.Draw(t_cyan).text((tx, ty), "T", fill=(*NEON_CYAN, 255), font=font)
    img = apply_glow(img, t_cyan, layers=[(45, 40), (20, 70)])

    # Mint main T
    t_mint = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    ImageDraw.Draw(t_mint).text((tx, ty), "T", fill=(*T_COLOR, 255), font=font)
    img = apply_glow(img, t_mint, layers=[(16, 120), (6, 200)])

    # White-hot center
    wf = load_arcane_font(int(t_size * 0.88))
    wbb = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), "T", font=wf)
    wtw, wth = wbb[2] - wbb[0], wbb[3] - wbb[1]
    t_white = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    ImageDraw.Draw(t_white).text(
        (cx - wtw // 2 - wbb[0], cy - wth // 2 - wbb[1]),
        "T", fill=(255, 255, 255, 130), font=wf)
    t_white = t_white.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.alpha_composite(img, t_white)

    # --- Layer 6: Corner doodles (sharp, full opacity) ---
    doodle_layer = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    dd = ImageDraw.Draw(doodle_layer, "RGBA")
    drng = _random.Random(77)

    # Place doodles in 4 corners, outside the ring
    corners = [
        (int(M * 0.12), int(M * 0.12)),   # top-left
        (int(M * 0.88), int(M * 0.12)),   # top-right
        (int(M * 0.12), int(M * 0.88)),   # bottom-left
        (int(M * 0.88), int(M * 0.88)),   # bottom-right
    ]
    icon_doodles = [doodle_x_mark, doodle_small_star, doodle_hex_particle,
                    doodle_lightning, doodle_zigzag, doodle_scribble_circle]

    for corner_x, corner_y in corners:
        # 1-2 doodles per corner
        for _ in range(drng.randint(1, 2)):
            dx = corner_x + drng.randint(-int(M * 0.06), int(M * 0.06))
            dy = corner_y + drng.randint(-int(M * 0.06), int(M * 0.06))
            color = drng.choice(NEON_COLORS)
            func = drng.choice(icon_doodles)
            func(dd, dx, dy, 0.7, drng, color)

    # A few extra doodles along edges
    for _ in range(4):
        edge = drng.randint(0, 3)
        if edge == 0:  # top
            dx, dy = drng.randint(int(M * 0.2), int(M * 0.8)), int(M * 0.06)
        elif edge == 1:  # bottom
            dx, dy = drng.randint(int(M * 0.2), int(M * 0.8)), int(M * 0.94)
        elif edge == 2:  # left
            dx, dy = int(M * 0.06), drng.randint(int(M * 0.2), int(M * 0.8))
        else:  # right
            dx, dy = int(M * 0.94), drng.randint(int(M * 0.2), int(M * 0.8))
        color = drng.choice(NEON_COLORS)
        func = drng.choice(icon_doodles)
        func(dd, dx, dy, 0.5, drng, color)

    img = Image.alpha_composite(img, doodle_layer)

    if size != M:
        img = img.resize((size, size), Image.LANCZOS)
    return img


# ---------------------------------------------------------------------------
# Hex Grid Background (like the Wrapped page)
# ---------------------------------------------------------------------------
def render_hex_grid(width: int, height: int) -> Image.Image:
    """Subtle hex grid overlay like the Wrapped page background."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    hex_r = max(12, int(min(width, height) * 0.03))
    row_h = hex_r * math.sqrt(3)
    col_w = hex_r * 1.5
    row = 0
    y = -hex_r
    while y <= height + hex_r:
        x_off = hex_r * 0.75 if row % 2 else 0
        x = -hex_r + x_off
        while x <= width + hex_r:
            pts = []
            for i in range(6):
                angle = math.radians(60 * i + 30)
                pts.append((int(x + hex_r * 0.95 * math.cos(angle)),
                            int(y + hex_r * 0.95 * math.sin(angle))))
            # Very subtle grid lines
            draw.polygon(pts, outline=(80, 100, 140, 12))
            x += col_w
        y += row_h * 0.5
        row += 1
    return layer


# ---------------------------------------------------------------------------
# SPLASH SCREEN — Wrapped-style graffiti wall
# ---------------------------------------------------------------------------
def render_splash(width: int, height: int) -> Image.Image:
    """Render splash screen — dark bg, hex grid, sharp full-opacity graffiti."""
    # Flat dark background with very subtle aurora tint
    img = render_aurora(width, height, intensity=0.4)

    # Subtle hex grid overlay
    grid = render_hex_grid(width, height)
    img = Image.alpha_composite(img, grid)

    # Sharp graffiti doodles at FULL opacity — no fading
    graffiti_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    graffiti_draw = ImageDraw.Draw(graffiti_layer, "RGBA")
    rng = _random.Random(314)
    draw_graffiti(graffiti_draw, width, height, count=60, rng=rng,
                  clear_center=True, center_r=0.22)
    # NO opacity reduction — sharp and loud
    img = Image.alpha_composite(img, graffiti_layer)

    # Centered "T" — big, bold, glowing
    short = min(width, height)
    t_font_size = int(short * 0.22)

    # Cyan outer halo
    t_cyan = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    t_cyan_d = ImageDraw.Draw(t_cyan)
    font = load_arcane_font(t_font_size)
    bbox = t_cyan_d.textbbox((0, 0), "T", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx, cy = width // 2, height // 2 - int(height * 0.06)
    tx = cx - tw // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]
    t_cyan_d.text((tx, ty), "T", fill=(*NEON_CYAN, 255), font=font)
    img = apply_glow(img, t_cyan, layers=[(40, 40), (18, 70)])

    # Mint main T with drips
    t_main = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    t_main_d = ImageDraw.Draw(t_main, "RGBA")
    draw_t_with_drips(t_main_d, cx, cy, t_font_size, _random.Random(7))
    img = apply_glow(img, t_main, layers=[(15, 100), (6, 180)])

    # White-hot center
    t_white = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    t_white_d = ImageDraw.Draw(t_white)
    wf = load_arcane_font(int(t_font_size * 0.9))
    wbb = t_white_d.textbbox((0, 0), "T", font=wf)
    wtw, wth = wbb[2] - wbb[0], wbb[3] - wbb[1]
    t_white_d.text((cx - wtw // 2 - wbb[0], cy - wth // 2 - wbb[1]),
                   "T", fill=(255, 255, 255, 120), font=wf)
    t_white = t_white.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.alpha_composite(img, t_white)

    # "TOXSHIELD" text with letter spacing and glow
    text_size = max(16, int(short * 0.055))
    text_font = load_impact_font(text_size)
    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text = "TOXSHIELD"
    char_widths = []
    for ch in text:
        bb = text_draw.textbbox((0, 0), ch, font=text_font)
        char_widths.append(bb[2] - bb[0])
    spacing = int(text_size * 0.2)
    total_w = sum(char_widths) + spacing * (len(text) - 1)
    start_x = (width - total_w) // 2
    text_y = cy + th // 2 + int(height * 0.05)
    cursor_x = start_x
    for ch, cw in zip(text, char_widths):
        bb = text_draw.textbbox((0, 0), ch, font=text_font)
        text_draw.text((cursor_x - bb[0], text_y - bb[1]), ch,
                       fill=(*T_COLOR, 230), font=text_font)
        cursor_x += cw + spacing
    img = apply_glow(img, text_layer, layers=[(12, 70), (5, 140)])

    # Tagline
    tag_size = max(10, int(text_size * 0.45))
    tag_font = load_mono_font(tag_size)
    tag = "FORENSIC RELATIONSHIP ANALYZER"
    tag_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    tag_draw = ImageDraw.Draw(tag_layer)
    tag_bb = tag_draw.textbbox((0, 0), tag, font=tag_font)
    tag_w = tag_bb[2] - tag_bb[0]
    tag_x = (width - tag_w) // 2 - tag_bb[0]
    tag_text_y = text_y + int(text_size * 1.3)
    tag_draw.text((tag_x, tag_text_y), tag, fill=(*NEON_CYAN, 100), font=tag_font)
    img = Image.alpha_composite(img, tag_layer)

    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Output Generation
# ---------------------------------------------------------------------------
MIPMAP_DENSITIES = {
    "mdpi":    {"icon": 48,  "fg": 108},
    "hdpi":    {"icon": 72,  "fg": 162},
    "xhdpi":   {"icon": 96,  "fg": 216},
    "xxhdpi":  {"icon": 144, "fg": 324},
    "xxxhdpi": {"icon": 192, "fg": 432},
}

SPLASH_PORTRAIT = {
    "port-mdpi":    (320, 480),
    "port-hdpi":    (480, 800),
    "port-xhdpi":   (720, 1280),
    "port-xxhdpi":  (960, 1600),
    "port-xxxhdpi": (1280, 1920),
}

SPLASH_LANDSCAPE = {
    "land-mdpi":    (480, 320),
    "land-hdpi":    (800, 480),
    "land-xhdpi":   (1280, 720),
    "land-xxhdpi":  (1600, 960),
    "land-xxxhdpi": (1920, 1280),
}


def generate_android_icons():
    print("Generating Android icons...")
    master_fg = render_icon(1024, transparent_bg=True)
    master_legacy = render_icon(1024, transparent_bg=False)

    for density, sizes in MIPMAP_DENSITIES.items():
        d = ANDROID_RES / f"mipmap-{density}"
        d.mkdir(parents=True, exist_ok=True)

        fg = master_fg.resize((sizes["fg"], sizes["fg"]), Image.LANCZOS)
        fg.save(str(d / "ic_launcher_foreground.png"), "PNG")

        legacy = master_legacy.resize((sizes["icon"], sizes["icon"]), Image.LANCZOS)
        bg = Image.new("RGBA", (sizes["icon"], sizes["icon"]), (*BG, 255))
        bg = Image.alpha_composite(bg, legacy)
        bg.convert("RGB").save(str(d / "ic_launcher.png"), "PNG")

        rnd = bg.copy()
        mask = Image.new("L", (sizes["icon"], sizes["icon"]), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, sizes["icon"] - 1, sizes["icon"] - 1], fill=255)
        rnd.putalpha(mask)
        rnd.save(str(d / "ic_launcher_round.png"), "PNG")

        print(f"  {density}: fg={sizes['fg']}px, icon={sizes['icon']}px")


def generate_splash_screens():
    print("Generating splash screens...")

    base = ANDROID_RES / "drawable"
    base.mkdir(parents=True, exist_ok=True)
    render_splash(480, 320).save(str(base / "splash.png"), "PNG")
    print("  base: 480x320")

    for name, (w, h) in {**SPLASH_PORTRAIT, **SPLASH_LANDSCAPE}.items():
        out = ANDROID_RES / f"drawable-{name}"
        out.mkdir(parents=True, exist_ok=True)
        render_splash(w, h).save(str(out / "splash.png"), "PNG")
        print(f"  {name}: {w}x{h}")


def generate_web_assets():
    print("Generating web assets...")
    icon = render_icon(256, transparent_bg=False)
    bg = Image.new("RGBA", (256, 256), (*BG, 255))
    bg = Image.alpha_composite(bg, icon)

    i32 = bg.resize((32, 32), Image.LANCZOS)
    i32.save(str(ROOT / "src" / "app" / "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32)])
    print("  favicon.ico: 16+32")

    bg.resize((180, 180), Image.LANCZOS).convert("RGB").save(
        str(ROOT / "src" / "app" / "apple-icon.png"), "PNG")
    print("  apple-icon.png: 180x180")


def main():
    print("=" * 50)
    print("ToxShield Arcane Graffiti Asset Generator")
    print("=" * 50)
    generate_android_icons()
    print()
    generate_splash_screens()
    print()
    generate_web_assets()
    print()
    print("Done!")


if __name__ == "__main__":
    main()
