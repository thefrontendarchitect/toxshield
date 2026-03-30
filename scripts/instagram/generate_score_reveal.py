#!/usr/bin/env python3
"""
ToxShield score_reveal carousel generator.

7 slides, 1080x1350px, black-and-white hand-drawn doodle aesthetic.
Every slide has a 'toxshield.in' footer. Slide 7 is the CTA.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow>=10.2.0", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
WIDTH = 1080
HEIGHT = 1350

BG       = (0, 0, 0)
WHITE    = (255, 255, 255)
OFFWHITE = (220, 220, 220)
MUTED    = (130, 130, 130)
DIM      = (90, 90, 90)

MARGIN_H = 90   # horizontal text margin from edge
FOOTER_H = 80   # reserved height at very bottom for footer

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_CANDIDATES = {
    "bold": [
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ],
    "regular": [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ],
}

def _load(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont | None:
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return None

def load_font(role: str, size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES.get(role, FONT_CANDIDATES["regular"]):
        if Path(path).exists():
            # For .ttc files, index 2 is often the bold variant
            idx = 2 if path.endswith(".ttc") and role == "bold" else 0
            f = _load(path, size, idx)
            if f:
                return f
            # Fallback: try index 0
            f = _load(path, size, 0)
            if f:
                return f
    return ImageFont.load_default()

# Pre-load font catalogue
FONTS = {}

def init_fonts():
    FONTS["hook"]      = load_font("bold",    78)   # slide 1 big hook
    FONTS["score_num"] = load_font("bold",   120)   # the "8.4" number
    FONTS["label"]     = load_font("bold",    36)   # section labels e.g. "TOXICITY SCORE:"
    FONTS["title"]     = load_font("bold",    58)   # slide titles
    FONTS["body"]      = load_font("regular", 44)   # body text
    FONTS["body_sm"]   = load_font("regular", 38)   # smaller body
    FONTS["handle"]    = load_font("bold",    32)   # @toxshield.ai handle
    FONTS["footer"]    = load_font("regular", 22)   # footer text
    FONTS["disc"]      = load_font("regular", 20)   # disclaimer tiny
    FONTS["cta_big"]   = load_font("bold",    52)   # CTA main line
    FONTS["cta_sub"]   = load_font("regular", 36)   # CTA sub-lines

# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def text_w(text: str, font) -> int:
    bb = font.getbbox(text)
    return bb[2] - bb[0]

def text_h(font) -> int:
    bb = font.getbbox("Ag")
    return bb[3] - bb[1]

def wrap(text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        candidate = f"{cur} {w}".strip()
        if text_w(candidate, font) <= max_w:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]

def draw_centered(draw, y: int, text: str, font, color=WHITE, max_w: int | None = None) -> int:
    """Draw centered text starting at y, return new y after last line."""
    mw = max_w or (WIDTH - MARGIN_H * 2)
    lines = wrap(text, font, mw)
    lh = text_h(font) + 10
    for line in lines:
        tw = text_w(line, font)
        x = (WIDTH - tw) // 2
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y

def draw_left(draw, x: int, y: int, text: str, font, color=WHITE, max_w: int | None = None) -> int:
    mw = max_w or (WIDTH - x - MARGIN_H)
    lines = wrap(text, font, mw)
    lh = text_h(font) + 10
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y

# ---------------------------------------------------------------------------
# Doodle engine (identical to generate_carousel.py)
# ---------------------------------------------------------------------------

def _doodle_squiggle(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(3 * scale))
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
    color = (255, 255, 255, opacity)
    w = max(1, int(2 * scale))
    size = int(rng.randint(15, 30) * scale)
    num_rays = rng.choice([4, 5, 6])
    offset = rng.uniform(0, math.pi / num_rays)
    for i in range(num_rays):
        angle = offset + (math.pi * 2 / num_rays) * i
        x2 = x + int(size * math.cos(angle))
        y2 = y + int(size * math.sin(angle))
        draw.line([(x, y), (x2, y2)], fill=color, width=w)

def _doodle_zigzag(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(2 * scale))
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

def _doodle_circle(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(2 * scale))
    r = int(rng.randint(18, 40) * scale)
    for _ in range(rng.randint(2, 3)):
        dx, dy = rng.randint(-4, 4), rng.randint(-4, 4)
        draw.ellipse([x - r + dx, y - r + dy, x + r + dx, y + r + dy], outline=color, width=w)

def _doodle_hatching(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(2 * scale))
    count = rng.randint(4, 8)
    h = int(rng.randint(20, 45) * scale)
    gap = int(rng.randint(6, 10) * scale)
    angle = rng.uniform(-0.3, 0.3)
    for i in range(count):
        x1 = x + i * gap
        draw.line([(x1, y), (x1 + int(h * math.sin(angle)), y + int(h * math.cos(angle)))], fill=color, width=w)

def _doodle_swoosh(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(3 * scale))
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

def _doodle_spiral(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(2 * scale))
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

def _doodle_dots(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    spread = int(20 * scale)
    for _ in range(rng.randint(3, 7)):
        dx, dy = rng.randint(-spread, spread), rng.randint(-spread, spread)
        r = max(1, int(rng.randint(2, 5) * scale))
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=color)

def _doodle_arrow(draw, x, y, scale, opacity, rng):
    color = (255, 255, 255, opacity)
    w = max(1, int(2 * scale))
    length = int(rng.randint(30, 60) * scale)
    angle = rng.uniform(0, math.pi * 2)
    x2 = x + int(length * math.cos(angle))
    y2 = y + int(length * math.sin(angle))
    draw.line([(x, y), (x2, y2)], fill=color, width=w)
    head = int(12 * scale)
    for da in [0.4, -0.4]:
        draw.line([(x2, y2), (x2 - int(head * math.cos(angle + da)), y2 - int(head * math.sin(angle + da)))], fill=color, width=w)

_DOODLE_FUNCS = [
    _doodle_squiggle, _doodle_star, _doodle_zigzag, _doodle_circle,
    _doodle_hatching, _doodle_swoosh, _doodle_spiral, _doodle_dots, _doodle_arrow,
]

def draw_doodles(draw, seed: int, count: int = 14, bottom_margin: int = 160 + FOOTER_H):
    rng = random.Random(seed)
    margin = 155
    zones = [
        (20, 20, WIDTH - 20, margin),
        (20, HEIGHT - bottom_margin, WIDTH - 20, HEIGHT - FOOTER_H - 10),
        (20, margin, margin, HEIGHT - bottom_margin),
        (WIDTH - margin, margin, WIDTH - 20, HEIGHT - bottom_margin),
    ]
    for _ in range(count):
        zone = rng.choice(zones)
        x = rng.randint(zone[0], max(zone[0], zone[2] - 1))
        y = rng.randint(zone[1], max(zone[1], zone[3] - 1))
        func = rng.choice(_DOODLE_FUNCS)
        opacity = rng.randint(160, 240)
        scale = rng.uniform(0.7, 1.3)
        func(draw, x, y, scale, opacity, rng)

# ---------------------------------------------------------------------------
# Footer (appears on every slide)
# ---------------------------------------------------------------------------

FOOTER_TEXT = "toxshield.in — see the toxic people in your life"

def draw_footer(draw, slide_num: int):
    """Draw a subtle footer at the very bottom of every slide."""
    font = FONTS["footer"]
    # Thin separator line
    sep_y = HEIGHT - FOOTER_H + 6
    draw.line([(MARGIN_H, sep_y), (WIDTH - MARGIN_H, sep_y)], fill=(60, 60, 60, 200), width=1)
    # Footer text centered
    tw = text_w(FOOTER_TEXT, font)
    x = (WIDTH - tw) // 2
    y = HEIGHT - FOOTER_H + 18
    draw.text((x, y), FOOTER_TEXT, fill=(110, 110, 110, 220), font=font)

# ---------------------------------------------------------------------------
# Base image factory
# ---------------------------------------------------------------------------

def new_slide(seed: int, doodle_count: int = 14, bottom_margin: int = None) -> tuple[Image.Image, ImageDraw.Draw]:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    bm = bottom_margin if bottom_margin is not None else (160 + FOOTER_H)
    draw_doodles(draw, seed=seed, count=doodle_count, bottom_margin=bm)
    draw_footer(draw, seed)
    return img, draw

def finalize(img: Image.Image) -> Image.Image:
    return img.convert("RGB")

# ---------------------------------------------------------------------------
# Slide 1 — Hook
# ---------------------------------------------------------------------------

def slide_01() -> Image.Image:
    img, draw = new_slide(seed=1000)
    font_hook = FONTS["hook"]
    font_handle = FONTS["handle"]

    # Main hook text — very large, centered, vertically centered above footer
    hook_lines_1 = "We ran this relationship"
    hook_lines_2 = "through ToxShield."
    hook_lines_3 = "The score was"

    content_top = 180
    y = content_top

    for line in [hook_lines_1, hook_lines_2]:
        tw = text_w(line, font_hook)
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=font_hook)
        y += text_h(font_hook) + 18

    y += 20  # extra gap before score line
    tw = text_w(hook_lines_3, font_hook)
    draw.text(((WIDTH - tw) // 2, y), hook_lines_3, fill=OFFWHITE, font=font_hook)
    y += text_h(font_hook) + 10

    # The score "8.4" — giant, dramatic
    score_font = FONTS["score_num"]
    score_str = "8.4"
    tw = text_w(score_str, score_font)
    draw.text(((WIDTH - tw) // 2, y), score_str, fill=WHITE, font=score_font)
    y += text_h(score_font) + 30

    # Handle
    handle_str = "@toxshield.ai"
    tw = text_w(handle_str, font_handle)
    draw.text(((WIDTH - tw) // 2, y), handle_str, fill=(160, 160, 160, 200), font=font_handle)

    return finalize(img)

# ---------------------------------------------------------------------------
# Slide 2 — Set the scene
# ---------------------------------------------------------------------------

def slide_02() -> Image.Image:
    img, draw = new_slide(seed=2000)

    label_font = FONTS["label"]
    title_font = FONTS["title"]
    body_font  = FONTS["body"]

    y = 200

    # Label
    label = "THE SUBJECT:"
    tw = text_w(label, label_font)
    draw.text(((WIDTH - tw) // 2, y), label, fill=(160, 160, 160), font=label_font)
    y += text_h(label_font) + 20

    # Title
    title = "A partner who"
    tw = text_w(title, title_font)
    draw.text(((WIDTH - tw) // 2, y), title, fill=WHITE, font=title_font)
    y += text_h(title_font) + 14

    title2 = '"just has high standards."'
    tw = text_w(title2, title_font)
    draw.text(((WIDTH - tw) // 2, y), title2, fill=WHITE, font=title_font)
    y += text_h(title_font) + 50

    # Divider
    draw.line([(MARGIN_H + 60, y), (WIDTH - MARGIN_H - 60, y)], fill=(60, 60, 60), width=1)
    y += 30

    # Body lines
    body_lines = [
        "On paper: demanding, passionate,",
        "particular about everything.",
        "",
        "In practice: nothing you do",
        "is ever good enough.",
        "",
        "ToxShield ran the pattern analysis.",
        "The numbers told a different story.",
    ]
    for line in body_lines:
        if line == "":
            y += 18
            continue
        tw = text_w(line, body_font)
        draw.text(((WIDTH - tw) // 2, y), line, fill=OFFWHITE, font=body_font)
        y += text_h(body_font) + 12

    return finalize(img)

# ---------------------------------------------------------------------------
# Slide 3 — Detected traits
# ---------------------------------------------------------------------------

def slide_03() -> Image.Image:
    img, draw = new_slide(seed=3000)

    label_font = FONTS["label"]
    title_font = FONTS["title"]
    body_font  = FONTS["body"]
    body_sm    = FONTS["body_sm"]

    y = 190

    # Label
    label = "DETECTED TRAITS:"
    tw = text_w(label, label_font)
    draw.text(((WIDTH - tw) // 2, y), label, fill=(160, 160, 160), font=label_font)
    y += text_h(label_font) + 28

    # Traits with scores — left-aligned block, centered as a unit
    traits = [
        ("Gaslighting",           "9.1"),
        ("Emotional manipulation","8.7"),
        ("Boundary violations",   "7.9"),
    ]

    trait_font = load_font("bold", 48)   # smaller so long names don't overflow
    score_font = load_font("bold", 48)
    score_col_w = 90                      # fixed right column width for the score
    block_w = 760
    block_x = (WIDTH - block_w) // 2
    name_max_w = block_w - score_col_w - 20

    for trait_name, score_val in traits:
        th = text_h(trait_font)

        # Trait name — left side, hard max width so it wraps if needed
        name_lines = wrap(trait_name, trait_font, name_max_w)
        name_block_h = len(name_lines) * (th + 6)
        ny = y
        for nl in name_lines:
            draw.text((block_x, ny), nl, fill=WHITE, font=trait_font)
            ny += th + 6

        # Score — right-aligned in score column, vertically centered on first name line
        sw = text_w(score_val, score_font)
        score_x = block_x + block_w - sw
        score_y = y + (th - text_h(score_font)) // 2
        draw.text((score_x, score_y), score_val, fill=OFFWHITE, font=score_font)

        y += name_block_h + 6

        # Thin bar under each trait
        draw.line([(block_x, y), (block_x + block_w, y)], fill=(55, 55, 55), width=1)
        y += 28

    y += 20

    # Forensic note
    note = "Behavioral forensics confirms:"
    tw = text_w(note, body_sm)
    draw.text(((WIDTH - tw) // 2, y), note, fill=(130, 130, 130), font=body_sm)
    y += text_h(body_sm) + 14

    note2 = "these are not personality quirks."
    tw = text_w(note2, body_sm)
    draw.text(((WIDTH - tw) // 2, y), note2, fill=(130, 130, 130), font=body_sm)
    y += text_h(body_sm) + 14

    note3 = "They are patterns."
    tw = text_w(note3, body_font)
    draw.text(((WIDTH - tw) // 2, y), note3, fill=WHITE, font=body_font)

    return finalize(img)

# ---------------------------------------------------------------------------
# Slide 4 — The pattern
# ---------------------------------------------------------------------------

def slide_04() -> Image.Image:
    img, draw = new_slide(seed=4000)

    label_font = FONTS["label"]
    title_font = FONTS["title"]
    body_font  = FONTS["body"]
    body_sm    = FONTS["body_sm"]

    y = 200

    # Label
    label = "THE PATTERN:"
    tw = text_w(label, label_font)
    draw.text(((WIDTH - tw) // 2, y), label, fill=(160, 160, 160), font=label_font)
    y += text_h(label_font) + 30

    # Cycle steps — displayed as a vertical flow
    steps = ["Idealize", "Devalue", "Discard", "Hoover"]
    step_font = FONTS["title"]

    for i, step in enumerate(steps):
        tw = text_w(step, step_font)
        draw.text(((WIDTH - tw) // 2, y), step, fill=WHITE, font=step_font)
        y += text_h(step_font) + 8

        # Arrow between steps (not after last)
        if i < len(steps) - 1:
            arr_x = WIDTH // 2
            arr_y = y + 4
            draw.line([(arr_x, arr_y), (arr_x, arr_y + 22)], fill=(100, 100, 100), width=2)
            # arrowhead
            draw.polygon([(arr_x - 8, arr_y + 18), (arr_x + 8, arr_y + 18), (arr_x, arr_y + 30)], fill=(100, 100, 100))
            y += 38

    y += 28

    # Explanation
    exp_lines = [
        "Textbook narcissistic supply cycle.",
        "You are not imagining it.",
        "This has a name.",
    ]
    for line in exp_lines:
        tw = text_w(line, body_sm)
        draw.text(((WIDTH - tw) // 2, y), line, fill=OFFWHITE, font=body_sm)
        y += text_h(body_sm) + 14

    return finalize(img)

# ---------------------------------------------------------------------------
# Slide 5 — What they said vs reality
# ---------------------------------------------------------------------------

def slide_05() -> Image.Image:
    img, draw = new_slide(seed=5000)

    label_font = FONTS["label"]
    title_font = FONTS["title"]
    body_font  = FONTS["body"]
    body_sm    = FONTS["body_sm"]

    y = 190

    # Label
    label = "WHAT THEY SAID:"
    tw = text_w(label, label_font)
    draw.text(((WIDTH - tw) // 2, y), label, fill=(160, 160, 160), font=label_font)
    y += text_h(label_font) + 22

    # The quote — quoted, large
    quote = '"I\'m the only one'
    quote2 = 'who truly loves you."'
    for q in [quote, quote2]:
        tw = text_w(q, title_font)
        draw.text(((WIDTH - tw) // 2, y), q, fill=WHITE, font=title_font)
        y += text_h(title_font) + 14

    y += 24

    # VS divider
    vs_font = FONTS["label"]
    vs_str = "vs."
    tw = text_w(vs_str, vs_font)
    draw.text(((WIDTH - tw) // 2, y), vs_str, fill=(90, 90, 90), font=vs_font)
    y += text_h(vs_font) + 22

    # Reality label
    real_label = "REALITY:"
    tw = text_w(real_label, label_font)
    draw.text(((WIDTH - tw) // 2, y), real_label, fill=(160, 160, 160), font=label_font)
    y += text_h(label_font) + 18

    # Reality text
    real_lines = [
        "Isolation tactic detected.",
        "",
        "Cutting you off from friends",
        "and family is a control mechanism,",
        "not a declaration of love.",
    ]
    for line in real_lines:
        if line == "":
            y += 14
            continue
        tw = text_w(line, body_sm)
        draw.text(((WIDTH - tw) // 2, y), line, fill=OFFWHITE, font=body_sm)
        y += text_h(body_sm) + 12

    return finalize(img)

# ---------------------------------------------------------------------------
# Slide 6 — Protection protocol
# ---------------------------------------------------------------------------

def slide_06() -> Image.Image:
    img, draw = new_slide(seed=6000)

    label_font = FONTS["label"]
    title_font = FONTS["title"]
    body_font  = FONTS["body"]
    body_sm    = FONTS["body_sm"]

    y = 190

    # Label
    label = "PROTECTION PROTOCOL:"
    tw = text_w(label, label_font)
    draw.text(((WIDTH - tw) // 2, y), label, fill=(160, 160, 160), font=label_font)
    y += text_h(label_font) + 32

    # Three protocol items, left-aligned in a centered block
    block_w = 760
    block_x = (WIDTH - block_w) // 2

    protocols = [
        ("01", "Grey rock method.",    "Give nothing that feeds the cycle."),
        ("02", "Document everything.", "Patterns require evidence."),
        ("03", "Build your network.",  "Isolation is their weapon. Connection is yours."),
    ]

    num_font  = FONTS["label"]
    name_font = FONTS["body"]
    desc_font = FONTS["body_sm"]

    for num, name, desc in protocols:
        # Number
        draw.text((block_x, y), num, fill=(90, 90, 90), font=num_font)
        # Name (indented)
        draw.text((block_x + 60, y), name, fill=WHITE, font=name_font)
        y += text_h(name_font) + 8
        # Description
        y_after = draw_left(draw, block_x + 60, y, desc, desc_font, color=MUTED, max_w=block_w - 60)
        y = y_after + 28

    return finalize(img)

# ---------------------------------------------------------------------------
# Slide 7 — CTA
# ---------------------------------------------------------------------------

SAFETY_TEXT = (
    "ToxShield identifies behavioral patterns. Not a substitute\n"
    "for professional counseling. If in danger, contact emergency services."
)

def slide_07() -> Image.Image:
    img, draw = new_slide(seed=7000, doodle_count=10, bottom_margin=260 + FOOTER_H)

    cta_big  = FONTS["cta_big"]
    cta_sub  = FONTS["cta_sub"]
    handle_f = FONTS["handle"]
    disc_f   = FONTS["disc"]

    y = 170

    # Main CTA
    cta_lines = [
        "Go to toxshield.in",
        "to see the toxic people",
        "in your life.",
    ]
    for line in cta_lines:
        tw = text_w(line, cta_big)
        draw.text(((WIDTH - tw) // 2, y), line, fill=WHITE, font=cta_big)
        y += text_h(cta_big) + 16

    y += 36

    # Divider
    draw.line([(MARGIN_H + 80, y), (WIDTH - MARGIN_H - 80, y)], fill=(55, 55, 55), width=1)
    y += 32

    # Sub-lines
    sub_lines = [
        "Share with someone who needs this.",
        "Follow @toxshield.ai",
        "Free analysis — link in bio.",
    ]
    for line in sub_lines:
        tw = text_w(line, cta_sub)
        draw.text(((WIDTH - tw) // 2, y), line, fill=OFFWHITE, font=cta_sub)
        y += text_h(cta_sub) + 18

    y += 12

    # Handle large
    tw = text_w("@toxshield.ai", handle_f)
    draw.text(((WIDTH - tw) // 2, y), "@toxshield.ai", fill=(140, 140, 140), font=handle_f)

    # Safety disclaimer — pinned above footer
    disc_y = HEIGHT - FOOTER_H - 90
    for line in SAFETY_TEXT.split("\n"):
        line = line.strip()
        tw = text_w(line, disc_f)
        draw.text(((WIDTH - tw) // 2, disc_y), line, fill=(70, 70, 70), font=disc_f)
        disc_y += text_h(disc_f) + 6

    return finalize(img)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    init_fonts()

    out_dir = Path("/Users/biswa/toxshield/output/instagram/2026-03-24/score_reveal")
    out_dir.mkdir(parents=True, exist_ok=True)

    generators = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06, slide_07]

    paths = []
    for i, gen in enumerate(generators, start=1):
        img = gen()
        path = out_dir / f"slide_{i:02d}.png"
        img.save(str(path), "PNG")
        print(f"  Generated slide {i}/7: {path}")
        paths.append(str(path))

    print(f"\nAll 7 slides saved to {out_dir}")
    return paths

if __name__ == "__main__":
    main()
