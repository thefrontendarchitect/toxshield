"""
ToxShield Instagram DP — black & white hand-drawn doodle aesthetic.
Matches the carousel slide style from scripts/instagram/generate_carousel.py.

Output: 1080x1080 square PNG optimized for Instagram circular crop.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Import doodle functions from carousel module
sys.path.insert(0, str(Path(__file__).parent / "instagram"))
from generate_carousel import _DOODLE_FUNCS, COLORS  # noqa: E402

SIZE = 1080
CENTER = SIZE // 2
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_dp_font(size: int) -> ImageFont.FreeTypeFont:
    """Load the best available bold font for the T."""
    candidates = [
        # Futura Condensed ExtraBold — punchy geometric feel
        ("/System/Library/Fonts/Supplemental/Futura.ttc", 4),
        # Avenir Next Heavy
        ("/System/Library/Fonts/Avenir Next.ttc", 8),
        # Futura Bold
        ("/System/Library/Fonts/Supplemental/Futura.ttc", 2),
        # Helvetica
        ("/System/Library/Fonts/Helvetica.ttc", 0),
    ]
    for path, index in candidates:
        try:
            return ImageFont.truetype(path, size, index=index)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def draw_edge_doodles(draw: ImageDraw.Draw, seed: int = 7, count: int = 24):
    """Draw doodles scattered in edge margin zones."""
    rng = random.Random(seed)
    margin = 160
    zones = [
        (20, 20, SIZE - 20, margin),                        # top
        (20, SIZE - margin, SIZE - 20, SIZE - 20),           # bottom
        (20, margin, margin, SIZE - margin),                  # left
        (SIZE - margin, margin, SIZE - 20, SIZE - margin),    # right
    ]
    for _ in range(count):
        zone = zones[rng.randint(0, len(zones) - 1)]
        x = rng.randint(zone[0], max(zone[0], zone[2] - 1))
        y = rng.randint(zone[1], max(zone[1], zone[3] - 1))
        func = rng.choice(_DOODLE_FUNCS)
        opacity = rng.randint(170, 245)
        scale = rng.uniform(0.9, 1.5)
        func(draw, x, y, scale, opacity, rng)


def draw_inner_doodles(draw: ImageDraw.Draw, t_bbox: tuple, seed: int = 42, count: int = 14):
    """Draw fun doodles in a ring around the T — close but not overlapping."""
    rng = random.Random(seed)
    tx1, ty1, tx2, ty2 = t_bbox
    tcx = (tx1 + tx2) // 2
    tcy = (ty1 + ty2) // 2

    # Ring zone: just outside the T bounding box
    pad = 40   # min distance from T edge
    ring = 120  # max distance from T edge

    for _ in range(count):
        # Pick a random angle and distance in the ring
        angle = rng.uniform(0, math.pi * 2)
        # Elliptical ring to match the T shape (wider than tall)
        half_w = (tx2 - tx1) // 2 + pad
        half_h = (ty2 - ty1) // 2 + pad
        dist = rng.uniform(0, ring)
        x = int(tcx + (half_w + dist) * math.cos(angle))
        y = int(tcy + (half_h + dist) * math.sin(angle))

        # Keep within canvas
        x = max(30, min(SIZE - 30, x))
        y = max(30, min(SIZE - 30, y))

        func = rng.choice(_DOODLE_FUNCS)
        opacity = rng.randint(180, 250)
        scale = rng.uniform(0.7, 1.2)
        func(draw, x, y, scale, opacity, rng)


def draw_accent_elements(draw: ImageDraw.Draw, t_bbox: tuple):
    """Draw specific accent doodles that interact with the T — underline, circles, sparkles."""
    tx1, ty1, tx2, ty2 = t_bbox
    tcx = (tx1 + tx2) // 2
    white = (*COLORS["doodle"], 220)
    dim = (*COLORS["doodle"], 140)

    # Sketchy underline below the T
    y_under = ty2 + 25
    points = []
    for t in range(tx1 - 20, tx2 + 20, 3):
        wobble = random.Random(t).gauss(0, 2.5)
        points.append((t, int(y_under + wobble)))
    if len(points) >= 2:
        draw.line(points, fill=white, width=4, joint="curve")

    # Second offset underline (hand-drawn = imperfect doubles)
    points2 = []
    for t in range(tx1 + 10, tx2 + 10, 3):
        wobble = random.Random(t + 999).gauss(0, 2)
        points2.append((t, int(y_under + 12 + wobble)))
    if len(points2) >= 2:
        draw.line(points2, fill=dim, width=2, joint="curve")

    # Sparkle burst top-right of T
    sx, sy = tx2 + 30, ty1 - 20
    for i in range(6):
        angle = (math.pi * 2 / 6) * i + 0.2
        length = random.Random(i + 77).randint(12, 28)
        x2 = sx + int(length * math.cos(angle))
        y2 = sy + int(length * math.sin(angle))
        draw.line([(sx, sy), (x2, y2)], fill=white, width=2)
    # Center dot
    draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=white)

    # Small sparkle top-left
    sx2, sy2 = tx1 - 40, ty1 + 10
    for i in range(4):
        angle = (math.pi * 2 / 4) * i + 0.5
        length = random.Random(i + 200).randint(8, 16)
        x2 = sx2 + int(length * math.cos(angle))
        y2 = sy2 + int(length * math.sin(angle))
        draw.line([(sx2, sy2), (x2, y2)], fill=dim, width=2)

    # Scribble circle around the T (loose, hand-drawn)
    r = max(tx2 - tx1, ty2 - ty1) // 2 + 55
    for offset_pass in range(2):
        circle_points = []
        rng = random.Random(offset_pass * 500 + 123)
        for deg in range(0, 370, 3):
            rad = math.radians(deg)
            wobble_r = r + rng.gauss(0, 4)
            px = tcx + int(wobble_r * math.cos(rad))
            py = (ty1 + ty2) // 2 + int(wobble_r * math.sin(rad))
            circle_points.append((px, py))
        if len(circle_points) >= 2:
            opacity = 100 if offset_pass == 0 else 60
            draw.line(circle_points, fill=(*COLORS["doodle"], opacity), width=2, joint="curve")

    # Arrow pointing at T from bottom-left
    ax, ay = tx1 - 80, ty2 + 70
    ax2, ay2 = tx1 - 15, ty2 + 10
    draw.line([(ax, ay), (ax2, ay2)], fill=dim, width=3)
    # Arrowhead
    for da in [0.5, -0.5]:
        a = math.atan2(ay2 - ay, ax2 - ax) + math.pi + da
        hx = ax2 + int(14 * math.cos(a))
        hy = ay2 + int(14 * math.sin(a))
        draw.line([(ax2, ay2), (hx, hy)], fill=dim, width=3)


def generate_dp():
    img = Image.new("RGBA", (SIZE, SIZE), (*COLORS["bg"], 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Edge doodles (background layer)
    draw_edge_doodles(draw, seed=7, count=26)

    # 2. Draw the T and get its bounding box
    font = load_dp_font(380)
    bbox = draw.textbbox((0, 0), "T", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = CENTER - tw // 2
    ty = CENTER - th // 2 - bbox[1]
    t_bbox = (tx, ty, tx + tw, ty + th)

    # 3. Inner ring doodles (around the T)
    draw_inner_doodles(draw, t_bbox, seed=42, count=14)

    # 4. Accent elements that interact with the T
    draw_accent_elements(draw, t_bbox)

    # 5. Draw the T last (on top of everything)
    draw.text((tx, ty), "T", fill=COLORS["text_primary"], font=font)

    output_path = OUTPUT_DIR / "toxshield_dp.png"
    img.save(str(output_path), "PNG", quality=100)
    print(f"DP saved to: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    generate_dp()
