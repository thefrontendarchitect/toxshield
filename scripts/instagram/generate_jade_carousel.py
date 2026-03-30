#!/usr/bin/env python3
"""
One-shot generator for the ToxShield JADE carousel post.

7-slide toxic_callout carousel — "5 things JADE-ing sounds like in real life"
Canvas: 1080x1350px, pure black background, white hand-drawn doodle aesthetic.
Every slide carries a small "toxshield.in" watermark at the bottom.
"""

from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow>=10.2.0", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "instagram" / "2026-03-24" / "toxic_callout"

# ---------------------------------------------------------------------------
# Canvas / Colour constants
# ---------------------------------------------------------------------------

W, H = 1080, 1350
BG       = (0,   0,   0)
WHITE    = (255, 255, 255)
MUTED    = (140, 140, 140)
DIM      = (85,  85,  85)

WATERMARK_TEXT = "toxshield.in — see the toxic people in your life"
SAFETY_TEXT = (
    "ToxShield identifies behavioral patterns. It is not a substitute\n"
    "for professional counseling. If you are in danger, contact emergency services."
)

# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------

def _try_fonts(paths: list[str | Path], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for p in paths:
        p = Path(p)
        if p.exists():
            try:
                if str(p).endswith(".ttc"):
                    return ImageFont.truetype(str(p), size, index=index)
                return ImageFont.truetype(str(p), size)
            except (OSError, IOError):
                continue
    return ImageFont.load_default()


FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    Path.home() / "Library/Fonts/Poppins-Bold.ttf",
    Path.home() / "Library/Fonts/Nunito-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_CANDIDATES_REG = [
    "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    Path.home() / "Library/Fonts/Poppins-Regular.ttf",
    Path.home() / "Library/Fonts/Nunito-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_fonts() -> dict:
    return {
        "hook":      _try_fonts(FONT_CANDIDATES_BOLD, 82, index=2),
        "label":     _try_fonts(FONT_CANDIDATES_BOLD, 52, index=2),
        "quote":     _try_fonts(FONT_CANDIDATES_REG,  44),
        "body":      _try_fonts(FONT_CANDIDATES_REG,  42),
        "stop":      _try_fonts(FONT_CANDIDATES_BOLD, 92, index=2),
        "subhook":   _try_fonts(FONT_CANDIDATES_BOLD, 58, index=2),
        "cta_big":   _try_fonts(FONT_CANDIDATES_BOLD, 60, index=2),
        "cta_small": _try_fonts(FONT_CANDIDATES_REG,  40),
        "watermark": _try_fonts(FONT_CANDIDATES_REG,  26),
        "tiny":      _try_fonts(FONT_CANDIDATES_REG,  24),
    }


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        test = (cur + " " + word).strip()
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


def text_w(text: str, font: ImageFont.FreeTypeFont) -> int:
    bb = font.getbbox(text)
    return bb[2] - bb[0]


def text_h(font: ImageFont.FreeTypeFont) -> int:
    bb = font.getbbox("Ag")
    return bb[3] - bb[1]


def draw_centered(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                  y: int, color: tuple = WHITE, max_w: int = W - 200) -> int:
    """Draw wrapped, horizontally centered text. Returns new y below last line."""
    lines = wrap(text, font, max_w)
    lh = text_h(font) + 16
    for line in lines:
        tw = text_w(line, font)
        x = (W - tw) // 2
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y


def draw_centered_block(draw: ImageDraw.Draw, lines: list[str],
                        font: ImageFont.FreeTypeFont, y: int,
                        color: tuple = WHITE, max_w: int = W - 200) -> int:
    """Draw a list of already-wrapped lines centered. Returns y below block."""
    lh = text_h(font) + 16
    for line in lines:
        tw = text_w(line, font)
        x = (W - tw) // 2
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y


# ---------------------------------------------------------------------------
# Doodle decorations  (same engine as generate_carousel.py, seeded per slide)
# ---------------------------------------------------------------------------

def _squiggle(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(3 * sc))
    pts = []
    ln = int(rng.randint(60, 110) * sc)
    amp = int(rng.randint(8, 16) * sc)
    angle = rng.uniform(0, math.pi * 2)
    for t in range(0, ln, 4):
        px = x + int(t * math.cos(angle) - amp * math.sin(t * 0.15) * math.sin(angle))
        py = y + int(t * math.sin(angle) + amp * math.sin(t * 0.15) * math.cos(angle))
        pts.append((px, py))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w, joint="curve")


def _star(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(2 * sc))
    size = int(rng.randint(14, 28) * sc)
    rays = rng.choice([4, 5, 6])
    off = rng.uniform(0, math.pi / rays)
    for i in range(rays):
        a = off + (math.pi * 2 / rays) * i
        draw.line([(x, y), (x + int(size * math.cos(a)), y + int(size * math.sin(a)))],
                  fill=c, width=w)


def _zigzag(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(2 * sc))
    segs = rng.randint(4, 8)
    sx = int(rng.randint(12, 22) * sc)
    sy = int(rng.randint(10, 18) * sc)
    pts = [(x + i * sx, y + (sy if i % 2 else -sy)) for i in range(segs)]
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w)


def _scribble_circle(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(2 * sc))
    r = int(rng.randint(18, 38) * sc)
    for _ in range(rng.randint(2, 3)):
        dx, dy = rng.randint(-4, 4), rng.randint(-4, 4)
        draw.ellipse([x - r + dx, y - r + dy, x + r + dx, y + r + dy], outline=c, width=w)


def _hatching(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(2 * sc))
    cnt = rng.randint(4, 7)
    h = int(rng.randint(20, 40) * sc)
    gap = int(rng.randint(6, 10) * sc)
    ang = rng.uniform(-0.3, 0.3)
    for i in range(cnt):
        x1 = x + i * gap
        draw.line([(x1, y), (x1 + int(h * math.sin(ang)), y + int(h * math.cos(ang)))],
                  fill=c, width=w)


def _swoosh(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(3 * sc))
    ln = int(rng.randint(50, 95) * sc)
    curve = rng.uniform(0.02, 0.06)
    angle = rng.uniform(0, math.pi * 2)
    pts = []
    for t in range(0, ln, 3):
        pts.append((x + int(t * math.cos(angle + curve * t)),
                    y + int(t * math.sin(angle + curve * t))))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w, joint="curve")


def _spiral(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(2 * sc))
    turns = rng.uniform(1.5, 2.5)
    max_r = int(rng.randint(14, 28) * sc)
    direction = rng.choice([1, -1])
    pts = []
    for t in range(int(turns * 60)):
        a = direction * t * math.pi / 30
        r = max_r * t / (turns * 60)
        pts.append((x + int(r * math.cos(a)), y + int(r * math.sin(a))))
    if len(pts) >= 2:
        draw.line(pts, fill=c, width=w, joint="curve")


def _dots(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    spread = int(20 * sc)
    for _ in range(rng.randint(3, 7)):
        dx, dy = rng.randint(-spread, spread), rng.randint(-spread, spread)
        r = int(rng.randint(2, 5) * sc)
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=c)


def _arrow(draw, x, y, sc, op, rng):
    c = (*WHITE, op)
    w = max(2, int(2 * sc))
    ln = int(rng.randint(28, 55) * sc)
    angle = rng.uniform(0, math.pi * 2)
    x2 = x + int(ln * math.cos(angle))
    y2 = y + int(ln * math.sin(angle))
    draw.line([(x, y), (x2, y2)], fill=c, width=w)
    hs = int(11 * sc)
    for da in [0.4, -0.4]:
        draw.line([(x2, y2),
                   (x2 - int(hs * math.cos(angle + da)),
                    y2 - int(hs * math.sin(angle + da)))], fill=c, width=w)


_DOODLE_FUNCS = [_squiggle, _star, _zigzag, _scribble_circle,
                 _hatching, _swoosh, _spiral, _dots, _arrow]


def draw_doodles(draw: ImageDraw.Draw, seed: int, count: int = 14,
                 bottom_margin: int = 180) -> None:
    """Scatter hand-drawn doodles in the slide margins."""
    rng = random.Random(seed)
    margin = 160
    zones = [
        (20, 20, W - 20, margin),
        (20, H - bottom_margin, W - 20, H - 20),
        (20, margin, margin, H - bottom_margin),
        (W - margin, margin, W - 20, H - bottom_margin),
    ]
    for _ in range(count):
        zone = zones[rng.randint(0, len(zones) - 1)]
        x = rng.randint(zone[0], max(zone[0], zone[2] - 1))
        y = rng.randint(zone[1], max(zone[1], zone[3] - 1))
        func = rng.choice(_DOODLE_FUNCS)
        opacity = rng.randint(160, 240)
        scale = rng.uniform(0.7, 1.3)
        func(draw, x, y, scale, opacity, rng)


# ---------------------------------------------------------------------------
# Watermark helper
# ---------------------------------------------------------------------------

def draw_watermark(draw: ImageDraw.Draw, font: ImageFont.FreeTypeFont) -> None:
    """Draw the toxshield.in footer watermark near the very bottom of every slide."""
    tw = text_w(WATERMARK_TEXT, font)
    x = (W - tw) // 2
    y = H - 46
    draw.text((x, y), WATERMARK_TEXT, fill=(*MUTED, 200), font=font)


# ---------------------------------------------------------------------------
# Base canvas
# ---------------------------------------------------------------------------

def new_canvas() -> tuple[Image.Image, ImageDraw.Draw]:
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W, H)], fill=(*BG, 255))
    return img, draw


# ---------------------------------------------------------------------------
# Slide renderers
# ---------------------------------------------------------------------------

def render_slide1(fonts: dict) -> Image.Image:
    """Hook — 'You're not explaining yourself. You're feeding the cycle.' + STOP JADE-ING label."""
    img, draw = new_canvas()
    draw_doodles(draw, seed=1000)

    center_y = H // 2

    # "STOP JADE-ING" badge at top-center (pill label feel)
    label = "STOP JADE-ING"
    lf = fonts["label"]
    lw = text_w(label, lf)
    lh = text_h(lf)
    pad_x, pad_y = 44, 18
    badge_x = (W - lw - pad_x * 2) // 2
    badge_y = 180
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + lw + pad_x * 2, badge_y + lh + pad_y * 2],
        radius=18, outline=(*WHITE, 220), width=3
    )
    draw.text((badge_x + pad_x, badge_y + pad_y), label, fill=WHITE, font=lf)

    # Main hook — two lines, large
    hook1 = "You're not explaining"
    hook2 = "yourself."
    hook3 = "You're feeding"
    hook4 = "the cycle."

    hf = fonts["hook"]
    lh_hook = text_h(hf) + 20

    block_h = lh_hook * 4 + 30  # 4 lines + gap
    y = center_y - block_h // 2 + 20

    for line in [hook1, hook2, hook3, hook4]:
        tw = text_w(line, hf)
        draw.text(((W - tw) // 2, y), line, fill=WHITE, font=hf)
        y += lh_hook
        if line == hook2:
            y += 30  # gap between sentences

    draw_watermark(draw, fonts["watermark"])
    return img.convert("RGB")


def render_slide2(fonts: dict) -> Image.Image:
    """What is JADE — the 4-part definition."""
    img, draw = new_canvas()
    draw_doodles(draw, seed=2000)

    MAX_W = W - 180

    # Title
    title = "What is JADE?"
    tf = fonts["subhook"]
    th = text_h(tf)

    # Acronym expansion lines
    lines = [
        "Justify.  Argue.  Defend.  Explain.",
        "",
        "The 4 responses toxic people",
        "train you to give.",
    ]

    bf = fonts["body"]
    bh = text_h(bf) + 18

    total_h = (th + 24) + 48 + len([l for l in lines if l]) * bh + bh  # approx
    y = (H - total_h) // 2 - 40

    # Draw title
    tw = text_w(title, tf)
    draw.text(((W - tw) // 2, y), title, fill=WHITE, font=tf)
    y += th + 24 + 48

    # Horizontal rule — subtle
    rule_y = y - 28
    draw.line([(200, rule_y), (W - 200, rule_y)], fill=(*WHITE, 60), width=1)

    for line in lines:
        if not line:
            y += bh // 2
            continue
        tw = text_w(line, bf)
        if tw > MAX_W:
            y = draw_centered(draw, line, bf, y, WHITE, MAX_W)
        else:
            draw.text(((W - tw) // 2, y), line, fill=WHITE, font=bf)
            y += bh

    draw_watermark(draw, fonts["watermark"])
    return img.convert("RGB")


def _render_jade_slide(fonts: dict, seed: int, number: str, label: str,
                       quote: str, explanation: str) -> Image.Image:
    """
    Template for slides 3-6.
    Layout (top to bottom):
      - JADE number + label  (e.g. "JADE #1 — JUSTIFY:")
      - Quoted phrase        (italic-ish, slightly dimmer)
      - "STOP." in large bold
      - Explanation line
    """
    img, draw = new_canvas()
    draw_doodles(draw, seed=seed)

    MAX_W = W - 180
    lf = fonts["label"]    # 52px bold  — number+label
    qf = fonts["quote"]    # 44px reg   — quoted text
    sf = fonts["stop"]     # 92px bold  — STOP.
    bf = fonts["body"]     # 42px reg   — explanation

    lh_label = text_h(lf) + 14
    lh_quote = text_h(qf) + 14
    lh_stop  = text_h(sf) + 14
    lh_body  = text_h(bf) + 14

    # Wrap quote and explanation
    wrapped_quote = wrap(quote, qf, MAX_W)
    wrapped_exp   = wrap(explanation, bf, MAX_W)

    block_h = (lh_label
               + 32                              # gap after label
               + len(wrapped_quote) * lh_quote
               + 40                              # gap before STOP
               + lh_stop
               + 32                              # gap after STOP
               + len(wrapped_exp) * lh_body)

    y = (H - block_h) // 2

    # Number + label line  e.g. "JADE #1 — JUSTIFY:"
    header = f"{number} — {label}"
    hw = text_w(header, lf)
    draw.text(((W - hw) // 2, y), header, fill=WHITE, font=lf)
    y += lh_label + 32

    # Quoted phrase — slightly dimmer
    for line in wrapped_quote:
        tw = text_w(line, qf)
        draw.text(((W - tw) // 2, y), line, fill=(*MUTED, 255), font=qf)
        y += lh_quote
    y += 40

    # "STOP." — dominant, white
    stop_w = text_w("STOP.", sf)
    draw.text(((W - stop_w) // 2, y), "STOP.", fill=WHITE, font=sf)
    y += lh_stop + 32

    # Explanation
    for line in wrapped_exp:
        tw = text_w(line, bf)
        draw.text(((W - tw) // 2, y), line, fill=WHITE, font=bf)
        y += lh_body

    draw_watermark(draw, fonts["watermark"])
    return img.convert("RGB")


def render_slide3(fonts: dict) -> Image.Image:
    return _render_jade_slide(
        fonts, seed=3000,
        number="JADE #1",
        label="JUSTIFY:",
        quote='"I went out because I haven\'t seen my\nfriends in months and I just needed—"',
        explanation="You don't owe an essay for having a life.",
    )


def render_slide4(fonts: dict) -> Image.Image:
    return _render_jade_slide(
        fonts, seed=4000,
        number="JADE #2",
        label="ARGUE:",
        quote='"That\'s not what happened! Let me tell\nyou exactly what I said—"',
        explanation="You're playing their game. They don't want truth, they want control.",
    )


def render_slide5(fonts: dict) -> Image.Image:
    return _render_jade_slide(
        fonts, seed=5000,
        number="JADE #3",
        label="DEFEND:",
        quote='"I\'m not a bad person, I always try to—"',
        explanation="If you're constantly proving you're good enough, the problem isn't you.",
    )


def render_slide6(fonts: dict) -> Image.Image:
    return _render_jade_slide(
        fonts, seed=6000,
        number="JADE #4",
        label="EXPLAIN:",
        quote='"The reason I did that was because—"',
        explanation="Explanations become ammunition. The more you give, the more they twist.",
    )


def render_slide7(fonts: dict) -> Image.Image:
    """CTA slide — toxshield.in promo + follow + safety disclaimer."""
    img, draw = new_canvas()
    draw_doodles(draw, seed=7000, count=10, bottom_margin=300)

    MAX_W = W - 180
    cf  = fonts["cta_big"]   # 60px bold
    csf = fonts["cta_small"] # 40px reg
    tf  = fonts["tiny"]      # 24px reg

    lh_cta  = text_h(cf)  + 14
    lh_cs   = text_h(csf) + 14
    lh_tiny = text_h(tf)  + 12

    cta_lines = wrap("Go to toxshield.in to see the toxic people in your life", cf, MAX_W)
    sub_lines = [
        "Free behavioral analysis.",
        "Follow @toxshield.ai for more.",
    ]

    disc_lines = SAFETY_TEXT.split("\n")

    block_h = (len(cta_lines) * lh_cta
               + 48
               + len(sub_lines) * lh_cs
               + 60
               + len(disc_lines) * lh_tiny)

    y = (H - block_h) // 2

    # CTA — big white text
    for line in cta_lines:
        tw = text_w(line, cf)
        draw.text(((W - tw) // 2, y), line, fill=WHITE, font=cf)
        y += lh_cta
    y += 48

    # Sub-lines
    for line in sub_lines:
        tw = text_w(line, csf)
        draw.text(((W - tw) // 2, y), line, fill=(*MUTED, 255), font=csf)
        y += lh_cs
    y += 60

    # Safety disclaimer at bottom of block
    for line in disc_lines:
        line = line.strip()
        if not line:
            continue
        tw = text_w(line, tf)
        draw.text(((W - tw) // 2, y), line, fill=(*DIM, 200), font=tf)
        y += lh_tiny

    # watermark
    draw_watermark(draw, fonts["watermark"])
    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> list[str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()

    slides = [
        (render_slide1, "slide_01.png"),
        (render_slide2, "slide_02.png"),
        (render_slide3, "slide_03.png"),
        (render_slide4, "slide_04.png"),
        (render_slide5, "slide_05.png"),
        (render_slide6, "slide_06.png"),
        (render_slide7, "slide_07.png"),
    ]

    paths = []
    for i, (renderer, filename) in enumerate(slides, 1):
        img = renderer(fonts)
        out_path = OUTPUT_DIR / filename
        img.save(str(out_path), "PNG")
        paths.append(str(out_path))
        print(f"  Generated slide {i}/7: {out_path}")

    print(f"\nAll 7 slides saved to: {OUTPUT_DIR}")
    return paths


if __name__ == "__main__":
    main()
