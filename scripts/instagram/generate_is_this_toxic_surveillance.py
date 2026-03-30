#!/usr/bin/env python3
"""
Custom generator for the 'Is this toxic?' surveillance carousel.
7 slides, 1080x1350px, black bg, white hand-drawn doodle aesthetic.
Every slide includes 'toxshield.in' footer text.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow>=10.2.0", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIDTH = 1080
HEIGHT = 1350

BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
DIM_WHITE = (200, 200, 200)
MUTED = (120, 120, 120)

FOOTER_TEXT = "toxshield.in — see the toxic people in your life"

OUTPUT_DIR = Path("/Users/biswa/toxshield/output/instagram/2026-03-24/is_this_toxic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Font Loading
# ---------------------------------------------------------------------------

def load_fonts():
    font_candidates_bold = [
        Path("/System/Library/Fonts/Supplemental/Futura.ttc"),
        Path("/System/Library/Fonts/Supplemental/Avenir Next.ttc"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/Arial.ttf"),
    ]
    font_candidates_regular = [
        Path("/System/Library/Fonts/Supplemental/Avenir Next.ttc"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/Arial.ttf"),
    ]

    bold_path = None
    for p in font_candidates_bold:
        if p.exists():
            bold_path = str(p)
            break

    reg_path = None
    for p in font_candidates_regular:
        if p.exists():
            reg_path = str(p)
            break

    def make_font(path, size, index=0):
        if path is None:
            return ImageFont.load_default()
        try:
            if path.endswith(".ttc"):
                return ImageFont.truetype(path, size, index=index)
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            return ImageFont.load_default()

    # Bold index 2 on Futura/Avenir ttc for bold weight
    return {
        "hook":     make_font(bold_path, 72, index=2),   # Slide 1 hook — large
        "label":    make_font(bold_path, 38, index=2),   # "WHAT THEY SAY:" labels
        "quote":    make_font(reg_path,  52, index=0),   # Quote text
        "title":    make_font(bold_path, 58, index=2),   # Slide titles
        "body":     make_font(reg_path,  46, index=0),   # Body text
        "body_sm":  make_font(reg_path,  40, index=0),   # Smaller body
        "cta":      make_font(bold_path, 62, index=2),   # CTA main
        "handle":   make_font(bold_path, 38, index=2),   # @toxshield.ai
        "footer":   make_font(reg_path,  26, index=0),   # toxshield.in footer
        "disc":     make_font(reg_path,  22, index=0),   # Safety disclaimer
    }


# ---------------------------------------------------------------------------
# Text Utilities
# ---------------------------------------------------------------------------

def wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> List[str]:
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        test = f"{cur} {word}".strip()
        bb = font.getbbox(test)
        if (bb[2] - bb[0]) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [text]


def draw_centered_text(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int,
    color: Tuple,
    max_w: int = WIDTH - 200,
) -> int:
    """Draw centered text, wrapping as needed. Returns y position after text."""
    lines = wrap(text, font, max_w)
    bb = font.getbbox("Ag")
    lh = (bb[3] - bb[1]) + 18
    for line in lines:
        bb2 = font.getbbox(line)
        tw = bb2[2] - bb2[0]
        x = (WIDTH - tw) // 2
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y


def text_block_height(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> int:
    lines = wrap(text, font, max_w)
    bb = font.getbbox("Ag")
    lh = (bb[3] - bb[1]) + 18
    return len(lines) * lh


# ---------------------------------------------------------------------------
# Doodle Decorations
# ---------------------------------------------------------------------------

def doodle_squiggle(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(3 * scale))
    length = int(rng.randint(60, 120) * scale)
    amplitude = int(rng.randint(8, 18) * scale)
    angle = rng.uniform(0, math.pi * 2)
    points = []
    for t in range(0, length, 4):
        px = x + int(t * math.cos(angle) - amplitude * math.sin(t * 0.15) * math.sin(angle))
        py = y + int(t * math.sin(angle) + amplitude * math.sin(t * 0.15) * math.cos(angle))
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w, joint="curve")


def doodle_star(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(2 * scale))
    size = int(rng.randint(15, 30) * scale)
    num_rays = rng.choice([4, 5, 6])
    offset = rng.uniform(0, math.pi / num_rays)
    for i in range(num_rays):
        angle = offset + (math.pi * 2 / num_rays) * i
        x2 = x + int(size * math.cos(angle))
        y2 = y + int(size * math.sin(angle))
        draw.line([(x, y), (x2, y2)], fill=color, width=w)


def doodle_zigzag(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(2 * scale))
    segments = rng.randint(4, 8)
    step_x = int(rng.randint(12, 22) * scale)
    step_y = int(rng.randint(10, 18) * scale)
    angle = rng.uniform(-0.3, 0.3)
    points = []
    for i in range(segments):
        px = x + int(i * step_x * math.cos(angle))
        py = y + int(i * step_x * math.sin(angle)) + (step_y if i % 2 else -step_y)
        points.append((px, py))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w)


def doodle_circle(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(2 * scale))
    r = int(rng.randint(18, 40) * scale)
    for _ in range(rng.randint(2, 3)):
        dx = rng.randint(-4, 4)
        dy = rng.randint(-4, 4)
        draw.ellipse([x-r+dx, y-r+dy, x+r+dx, y+r+dy], outline=color, width=w)


def doodle_hatching(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(2 * scale))
    count = rng.randint(4, 8)
    h = int(rng.randint(20, 45) * scale)
    gap = int(rng.randint(6, 10) * scale)
    angle = rng.uniform(-0.3, 0.3)
    for i in range(count):
        x1 = x + i * gap
        draw.line([(x1, y), (x1 + int(h * math.sin(angle)), y + int(h * math.cos(angle)))], fill=color, width=w)


def doodle_dots(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    count = rng.randint(3, 7)
    spread = int(20 * scale)
    for _ in range(count):
        dx = rng.randint(-spread, spread)
        dy = rng.randint(-spread, spread)
        r = int(rng.randint(2, 5) * scale)
        draw.ellipse([x+dx-r, y+dy-r, x+dx+r, y+dy+r], fill=color)


def doodle_arrow(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(2 * scale))
    length = int(rng.randint(30, 60) * scale)
    angle = rng.uniform(0, math.pi * 2)
    x2 = x + int(length * math.cos(angle))
    y2 = y + int(length * math.sin(angle))
    draw.line([(x, y), (x2, y2)], fill=color, width=w)
    hs = int(12 * scale)
    for da in [0.4, -0.4]:
        hx = x2 - int(hs * math.cos(angle + da))
        hy = y2 - int(hs * math.sin(angle + da))
        draw.line([(x2, y2), (hx, hy)], fill=color, width=w)


def doodle_spiral(draw, x, y, scale, opacity, rng):
    color = (*WHITE, opacity)
    w = max(2, int(2 * scale))
    turns = rng.uniform(1.5, 3.0)
    max_r = int(rng.randint(15, 30) * scale)
    direction = rng.choice([1, -1])
    points = []
    for t in range(0, int(turns * 60)):
        angle = direction * t * math.pi / 30
        r = max_r * t / (turns * 60)
        points.append((x + int(r * math.cos(angle)), y + int(r * math.sin(angle))))
    if len(points) >= 2:
        draw.line(points, fill=color, width=w, joint="curve")


DOODLE_FUNCS = [
    doodle_squiggle, doodle_star, doodle_zigzag, doodle_circle,
    doodle_hatching, doodle_dots, doodle_arrow, doodle_spiral,
]


def draw_doodles(
    draw: ImageDraw.Draw,
    seed: int,
    count: int = 14,
    bottom_margin: int = 180,
    top_margin: int = 160,
    side_margin: int = 160,
    center_clear_top: int = 0,
    center_clear_bottom: int = 0,
):
    """Draw doodles confined to the edge margins only.

    center_clear_top / center_clear_bottom allow callers to shrink the left/right
    side strips so doodles never reach the vertical band where center text lives.
    """
    rng = random.Random(seed)

    # Effective safe y range for left/right side strips
    side_top = top_margin + center_clear_top
    side_bot = HEIGHT - bottom_margin - center_clear_bottom

    zones = [
        (20, 20, WIDTH - 20, top_margin),                          # top strip
        (20, HEIGHT - bottom_margin, WIDTH - 20, HEIGHT - 40),     # bottom strip
        (20, side_top, side_margin, side_bot),                     # left strip
        (WIDTH - side_margin, side_top, WIDTH - 20, side_bot),     # right strip
    ]

    # Filter out degenerate zones
    valid_zones = [z for z in zones if z[2] > z[0] + 5 and z[3] > z[1] + 5]
    if not valid_zones:
        return

    for _ in range(count):
        zone = valid_zones[rng.randint(0, len(valid_zones) - 1)]
        x = rng.randint(zone[0], zone[2] - 1)
        y = rng.randint(zone[1], zone[3] - 1)
        func = rng.choice(DOODLE_FUNCS)
        opacity = rng.randint(160, 230)
        scale = rng.uniform(0.7, 1.3)
        func(draw, x, y, scale, opacity, rng)


# ---------------------------------------------------------------------------
# Footer — appears on every slide
# ---------------------------------------------------------------------------

def draw_footer(draw: ImageDraw.Draw, fonts: dict):
    """Draw 'toxshield.in — see the toxic people in your life' at the bottom."""
    font = fonts["footer"]
    bb = font.getbbox(FOOTER_TEXT)
    tw = bb[2] - bb[0]
    x = (WIDTH - tw) // 2
    y = HEIGHT - 52
    draw.text((x, y), FOOTER_TEXT, fill=(*MUTED, 220), font=font)


# ---------------------------------------------------------------------------
# Slide Builders
# ---------------------------------------------------------------------------

def new_slide() -> tuple:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    return img, draw


def finalize(img: Image.Image) -> Image.Image:
    return img.convert("RGB")


def slide_01_hook(fonts: dict) -> Image.Image:
    """Slide 1: Bold hook question — large, scroll-stopping."""
    img, draw = new_slide()
    draw_doodles(draw, seed=1000, count=14, bottom_margin=180)

    # "IS THIS TOXIC?" — small label up top
    label = "IS THIS TOXIC?"
    label_font = fonts["label"]
    bb = label_font.getbbox(label)
    lw = bb[2] - bb[0]
    draw.text(((WIDTH - lw) // 2, 200), label, fill=(*MUTED, 220), font=label_font)

    # Main hook — large
    hook = "Your partner reads your messages and calls it 'just checking in.'"
    hook_font = fonts["hook"]
    max_w = WIDTH - 180
    lines = wrap(hook, hook_font, max_w)
    bb2 = hook_font.getbbox("Ag")
    lh = (bb2[3] - bb2[1]) + 22
    total_h = len(lines) * lh
    y = (HEIGHT - total_h) // 2 - 30
    for line in lines:
        bb3 = hook_font.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=hook_font)
        y += lh

    # "Swipe to find out." nudge
    nudge = "Swipe to find out."
    nudge_font = fonts["body_sm"]
    bb4 = nudge_font.getbbox(nudge)
    nw = bb4[2] - bb4[0]
    draw.text(((WIDTH - nw) // 2, HEIGHT - 130), nudge, fill=(*DIM_WHITE, 200), font=nudge_font)

    draw_footer(draw, fonts)
    return finalize(img)


def slide_02_what_they_say(fonts: dict) -> Image.Image:
    """Slide 2: What they say."""
    img, draw = new_slide()
    draw_doodles(draw, seed=2000, count=13)

    # Label
    label = "WHAT THEY SAY:"
    lf = fonts["label"]
    bb = lf.getbbox(label)
    draw.text(((WIDTH - (bb[2]-bb[0])) // 2, 210), label, fill=(*MUTED, 220), font=lf)

    # Quote text — large, centered
    quote = '"I just want to make sure you\'re okay. I worry about you."'
    qf = fonts["quote"]
    max_w = WIDTH - 200
    lines = wrap(quote, qf, max_w)
    bb2 = qf.getbbox("Ag")
    lh = (bb2[3] - bb2[1]) + 22
    total_h = len(lines) * lh
    y = (HEIGHT - total_h) // 2
    for line in lines:
        bb3 = qf.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=qf)
        y += lh

    # Sub note
    note = "Sounds caring. Keep reading."
    nf = fonts["body_sm"]
    bb4 = nf.getbbox(note)
    draw.text(((WIDTH - (bb4[2]-bb4[0])) // 2, HEIGHT - 130), note, fill=(*DIM_WHITE, 180), font=nf)

    draw_footer(draw, fonts)
    return finalize(img)


def slide_03_what_it_is(fonts: dict) -> Image.Image:
    """Slide 3: What it actually is."""
    img, draw = new_slide()
    # Text block runs through lower half — restrict side strips to upper portion only
    draw_doodles(draw, seed=3000, count=14, center_clear_top=160, center_clear_bottom=300)

    label = "WHAT IT ACTUALLY IS:"
    lf = fonts["label"]
    bb = lf.getbbox(label)
    draw.text(((WIDTH - (bb[2]-bb[0])) // 2, 210), label, fill=(*MUTED, 220), font=lf)

    title = "Surveillance disguised as care."
    tf = fonts["title"]
    max_w = WIDTH - 200
    lines = wrap(title, tf, max_w)
    bb2 = tf.getbbox("Ag")
    lh = (bb2[3] - bb2[1]) + 22
    total_h = len(lines) * lh
    y = (HEIGHT - total_h) // 2 - 40
    for line in lines:
        bb3 = tf.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=tf)
        y += lh

    y += 50
    sub = "They've repackaged monitoring as love.\nYour gut noticed before your brain did."
    bf = fonts["body"]
    for part in sub.split("\n"):
        sub_lines = wrap(part, bf, max_w)
        bb4 = bf.getbbox("Ag")
        slh = (bb4[3] - bb4[1]) + 18
        for sl in sub_lines:
            bb5 = bf.getbbox(sl)
            tw = bb5[2] - bb5[0]
            draw.text(((WIDTH - tw) // 2, y), sl, fill=DIM_WHITE, font=bf)
            y += slh
        y += 10

    draw_footer(draw, fonts)
    return finalize(img)


def slide_04_the_pattern(fonts: dict) -> Image.Image:
    """Slide 4: The pattern."""
    img, draw = new_slide()
    draw_doodles(draw, seed=4000, count=13)

    label = "THE PATTERN:"
    lf = fonts["label"]
    bb = lf.getbbox(label)
    draw.text(((WIDTH - (bb[2]-bb[0])) // 2, 210), label, fill=(*MUTED, 220), font=lf)

    title = "Normalizing boundary violations by framing control as love."
    tf = fonts["title"]
    max_w = WIDTH - 200
    lines = wrap(title, tf, max_w)
    bb2 = tf.getbbox("Ag")
    lh = (bb2[3] - bb2[1]) + 22
    total_h = len(lines) * lh
    y = (HEIGHT - total_h) // 2 - 60
    for line in lines:
        bb3 = tf.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=tf)
        y += lh

    y += 50
    bullets = [
        "Access to your phone becomes expected.",
        "Checking becomes the new normal.",
        "Objecting makes you look guilty.",
    ]
    bf = fonts["body_sm"]
    bb4 = bf.getbbox("Ag")
    blh = (bb4[3] - bb4[1]) + 16
    for b in bullets:
        blines = wrap(b, bf, max_w - 40)
        for bl in blines:
            bb5 = bf.getbbox(bl)
            tw = bb5[2] - bb5[0]
            draw.text(((WIDTH - tw) // 2, y), bl, fill=DIM_WHITE, font=bf)
            y += blh
        y += 6

    draw_footer(draw, fonts)
    return finalize(img)


def slide_05_why_toxic(fonts: dict) -> Image.Image:
    """Slide 5: Why it's toxic."""
    img, draw = new_slide()
    # Dense text block — keep side doodles away from center text rows
    draw_doodles(draw, seed=5000, count=14, center_clear_top=120, center_clear_bottom=280)

    label = "WHY IT'S TOXIC:"
    lf = fonts["label"]
    bb = lf.getbbox(label)
    draw.text(((WIDTH - (bb[2]-bb[0])) // 2, 210), label, fill=(*MUTED, 220), font=lf)

    title = "Trust doesn't require access to everything."
    tf = fonts["title"]
    max_w = WIDTH - 200
    lines = wrap(title, tf, max_w)
    bb2 = tf.getbbox("Ag")
    lh = (bb2[3] - bb2[1]) + 22
    total_h = len(lines) * lh
    y = (HEIGHT - total_h) // 2 - 80
    for line in lines:
        bb3 = tf.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=tf)
        y += lh

    y += 50
    core = "Monitoring = control, not love."
    cf = fonts["body"]
    clines = wrap(core, cf, max_w)
    bb4 = cf.getbbox("Ag")
    clh = (bb4[3] - bb4[1]) + 18
    for cl in clines:
        bb5 = cf.getbbox(cl)
        tw = bb5[2] - bb5[0]
        draw.text(((WIDTH - tw) // 2, y), cl, fill=WHITE, font=cf)
        y += clh

    y += 30
    sub = "Coercive control patterns use care language\nto normalize surveillance. This is textbook."
    sf = fonts["body_sm"]
    bb6 = sf.getbbox("Ag")
    slh = (bb6[3] - bb6[1]) + 16
    for part in sub.split("\n"):
        plines = wrap(part, sf, max_w)
        for pl in plines:
            bb7 = sf.getbbox(pl)
            tw = bb7[2] - bb7[0]
            draw.text(((WIDTH - tw) // 2, y), pl, fill=DIM_WHITE, font=sf)
            y += slh
        y += 6

    draw_footer(draw, fonts)
    return finalize(img)


def slide_06_healthy_alternative(fonts: dict) -> Image.Image:
    """Slide 6: What healthy looks like."""
    img, draw = new_slide()
    draw_doodles(draw, seed=6000, count=13)

    label = "WHAT HEALTHY LOOKS LIKE:"
    lf = fonts["label"]
    bb = lf.getbbox(label)
    draw.text(((WIDTH - (bb[2]-bb[0])) // 2, 210), label, fill=(*MUTED, 220), font=lf)

    quote = '"I trust you. If something\'s wrong, I know you\'ll tell me."'
    qf = fonts["quote"]
    max_w = WIDTH - 200
    lines = wrap(quote, qf, max_w)
    bb2 = qf.getbbox("Ag")
    lh = (bb2[3] - bb2[1]) + 22
    total_h = len(lines) * lh
    y = (HEIGHT - total_h) // 2 - 40
    for line in lines:
        bb3 = qf.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=qf)
        y += lh

    y += 60
    sub = "Healthy relationships are built on trust,\nnot access."
    sf = fonts["body"]
    bb4 = sf.getbbox("Ag")
    slh = (bb4[3] - bb4[1]) + 18
    for part in sub.split("\n"):
        slines = wrap(part, sf, max_w)
        for sl in slines:
            bb5 = sf.getbbox(sl)
            tw = bb5[2] - bb5[0]
            draw.text(((WIDTH - tw) // 2, y), sl, fill=DIM_WHITE, font=sf)
            y += slh
        y += 8

    draw_footer(draw, fonts)
    return finalize(img)


def slide_07_cta(fonts: dict) -> Image.Image:
    """Slide 7: CTA — toxshield.in + follow + safety disclaimer."""
    img, draw = new_slide()
    # Large bottom_margin keeps doodles well above footer/disclaimer area
    draw_doodles(draw, seed=7000, count=10, bottom_margin=380, center_clear_top=80, center_clear_bottom=100)

    # Main CTA block — center of slide
    cta_line1 = "Go to toxshield.in to see"
    cta_line2 = "the toxic people in your life"
    ctaf = fonts["cta"]
    max_w = WIDTH - 160
    bb = ctaf.getbbox("Ag")
    lh = (bb[3] - bb[1]) + 18

    lines_to_draw = []
    for line in [cta_line1, cta_line2]:
        wrapped = wrap(line, ctaf, max_w)
        lines_to_draw.extend(wrapped)

    total_cta_h = len(lines_to_draw) * lh

    # Handle line height
    handle = "Follow @toxshield.ai"
    hf = fonts["handle"]
    bb2 = hf.getbbox("Ag")
    hlh = (bb2[3] - bb2[1]) + 14

    gap = 60
    total_block_h = total_cta_h + gap + hlh

    y = (HEIGHT - total_block_h) // 2 - 40

    for line in lines_to_draw:
        bb3 = ctaf.getbbox(line)
        tw = bb3[2] - bb3[0]
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=ctaf)
        y += lh

    y += gap

    # @toxshield.ai handle
    bb4 = hf.getbbox(handle)
    tw = bb4[2] - bb4[0]
    draw.text(((WIDTH - tw) // 2, y), handle, fill=DIM_WHITE, font=hf)

    # Safety disclaimer at bottom
    disclaimer_lines = [
        "ToxShield identifies behavioral patterns. Not a substitute for",
        "professional counseling. If you are in danger, contact emergency services.",
    ]
    df = fonts["disc"]
    bb5 = df.getbbox("Ag")
    dlh = (bb5[3] - bb5[1]) + 8
    dy = HEIGHT - 160
    for dl in disclaimer_lines:
        bb6 = df.getbbox(dl)
        tw = bb6[2] - bb6[0]
        draw.text(((WIDTH - tw) // 2, dy), dl, fill=(*MUTED, 200), font=df)
        dy += dlh

    # Footer — toxshield.in (slightly above the disclaimer)
    footer_font = fonts["footer"]
    ft = FOOTER_TEXT
    bb7 = footer_font.getbbox(ft)
    tw = bb7[2] - bb7[0]
    draw.text(((WIDTH - tw) // 2, HEIGHT - 200), ft, fill=(*MUTED, 200), font=footer_font)

    return finalize(img)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading fonts...")
    fonts = load_fonts()

    slides = [
        ("01", slide_01_hook),
        ("02", slide_02_what_they_say),
        ("03", slide_03_what_it_is),
        ("04", slide_04_the_pattern),
        ("05", slide_05_why_toxic),
        ("06", slide_06_healthy_alternative),
        ("07", slide_07_cta),
    ]

    generated = []
    for num, builder in slides:
        print(f"Generating slide {num}...")
        img = builder(fonts)
        path = OUTPUT_DIR / f"slide_{num}.png"
        img.save(str(path), "PNG")
        generated.append(str(path))
        print(f"  Saved: {path}")

    print(f"\nAll {len(generated)} slides generated:")
    for p in generated:
        print(f"  {p}")
    return generated


if __name__ == "__main__":
    main()
