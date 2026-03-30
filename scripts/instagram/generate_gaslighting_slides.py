#!/usr/bin/env python3
"""
Custom ToxShield carousel generator for the gaslighting red flags post.
7 slides, 1080x1920 (9:16), dark terminal aesthetic with neon green accents,
scanline overlay, monospace font.
"""

from __future__ import annotations

import math
import os
import random
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Canvas & colour constants
# ---------------------------------------------------------------------------

WIDTH  = 1080
HEIGHT = 1920

BG_COLOR          = (0, 0, 0)
NEON_GREEN        = (0, 255, 65)        # #00ff41
NEON_GREEN_DIM    = (0, 180, 45)        # dim accent
WHITE             = (255, 255, 255)
LIGHT_GRAY        = (220, 220, 220)
MID_GRAY          = (160, 160, 160)
DARK_GRAY         = (80, 80, 80)
MUTED_TEXT        = (100, 100, 100)
RED_ACCENT        = (220, 50, 50)       # for emphasis marks

BRANDING_TEXT     = "toxshield.in"
HANDLE_TEXT       = "@toxshield.ai"

# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------

MONO_PATHS = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
]

BOLD_PATHS = [
    "/System/Library/Fonts/Menlo.ttc",   # index 1 = bold
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
]


def _load(paths: List[str], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for p in paths:
        if os.path.exists(p):
            try:
                if p.endswith(".ttc"):
                    return ImageFont.truetype(p, size, index=index)
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def load_fonts():
    return {
        "hook":      _load(BOLD_PATHS,  88, index=1),
        "phrase":    _load(BOLD_PATHS,  72, index=1),
        "body":      _load(MONO_PATHS,  46, index=0),
        "small":     _load(MONO_PATHS,  36, index=0),
        "tiny":      _load(MONO_PATHS,  28, index=0),
        "micro":     _load(MONO_PATHS,  24, index=0),
        "branding":  _load(MONO_PATHS,  30, index=0),
    }


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def text_width(font: ImageFont.FreeTypeFont, text: str) -> int:
    bb = font.getbbox(text)
    return bb[2] - bb[0]


def text_height(font: ImageFont.FreeTypeFont) -> int:
    bb = font.getbbox("Ag")
    return bb[3] - bb[1]


def wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    cur = ""
    for w in words:
        probe = (cur + " " + w).strip()
        if text_width(font, probe) <= max_w:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def center_x(font: ImageFont.FreeTypeFont, text: str) -> int:
    return (WIDTH - text_width(font, text)) // 2


def draw_wrapped_centered(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int,
    max_w: int,
    color: Tuple,
    line_gap: int = 16,
) -> int:
    """Draw centered wrapped text, return y after last line."""
    lines = wrap(text, font, max_w)
    lh = text_height(font) + line_gap
    for line in lines:
        x = center_x(font, line)
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y


# ---------------------------------------------------------------------------
# Scanline overlay
# ---------------------------------------------------------------------------

def apply_scanlines(img: Image.Image, opacity: int = 22) -> Image.Image:
    """Overlay horizontal scanlines (every other pixel row slightly darkened)."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for y in range(0, HEIGHT, 3):
        d.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


# ---------------------------------------------------------------------------
# Corner bracket decorations
# ---------------------------------------------------------------------------

def draw_corner_brackets(draw: ImageDraw.Draw, color: Tuple, margin: int = 60, size: int = 80, width: int = 4):
    """Draw terminal-style corner brackets on all four corners."""
    corners = [
        # top-left
        [(margin, margin + size), (margin, margin), (margin + size, margin)],
        # top-right
        [(WIDTH - margin - size, margin), (WIDTH - margin, margin), (WIDTH - margin, margin + size)],
        # bottom-left
        [(margin, HEIGHT - margin - size), (margin, HEIGHT - margin), (margin + size, HEIGHT - margin)],
        # bottom-right
        [(WIDTH - margin - size, HEIGHT - margin), (WIDTH - margin, HEIGHT - margin), (WIDTH - margin, HEIGHT - margin - size)],
    ]
    for pts in corners:
        draw.line(pts, fill=color, width=width)


# ---------------------------------------------------------------------------
# Accent bar
# ---------------------------------------------------------------------------

def draw_accent_bar(draw: ImageDraw.Draw, y: int, color: Tuple, width: int = 4, margin: int = 120):
    draw.line([(margin, y), (WIDTH - margin, y)], fill=color, width=width)


# ---------------------------------------------------------------------------
# Glitch / noise stripes  (subtle, adds tension)
# ---------------------------------------------------------------------------

def draw_glitch_stripes(draw: ImageDraw.Draw, seed: int = 0, count: int = 3):
    rng = random.Random(seed)
    for _ in range(count):
        y = rng.randint(80, HEIGHT - 80)
        h = rng.randint(1, 3)
        x_off = rng.randint(0, 40) - 20
        alpha = rng.randint(15, 35)
        color = (*NEON_GREEN, alpha)
        draw.rectangle([(x_off, y), (WIDTH + x_off, y + h)], fill=color)


# ---------------------------------------------------------------------------
# Branding strip at bottom of every slide
# ---------------------------------------------------------------------------

def draw_branding(draw: ImageDraw.Draw, fonts: dict, y_bottom: int = HEIGHT - 70):
    font = fonts["branding"]
    lh = text_height(font)
    y = y_bottom - lh // 2
    # Left: toxshield.in
    draw.text((80, y), BRANDING_TEXT, fill=NEON_GREEN_DIM, font=font)
    # Right: slide handle
    hw = text_width(font, HANDLE_TEXT)
    draw.text((WIDTH - 80 - hw, y), HANDLE_TEXT, fill=DARK_GRAY, font=font)


# ---------------------------------------------------------------------------
# Slide 1 — Hook
# ---------------------------------------------------------------------------

def slide_01_hook(fonts: dict) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Subtle green gradient strip at top — very faint
    for i in range(160):
        alpha = int(22 * (1 - i / 160))
        draw.line([(0, i), (WIDTH, i)], fill=(*NEON_GREEN, alpha))

    draw_corner_brackets(draw, NEON_GREEN, margin=55, size=90, width=5)
    draw_glitch_stripes(draw, seed=1, count=4)

    # "PATTERN DETECTED." label at top
    label_font = fonts["small"]
    label = "PATTERN DETECTED."
    draw.text((center_x(label_font, label), 180), label, fill=NEON_GREEN, font=label_font)

    # Thin accent line under label
    draw_accent_bar(draw, 240, NEON_GREEN, width=2, margin=200)

    # Main hook text — wrap each explicit line to canvas width
    hook_font = fonts["hook"]
    hook = "\u201cYou\u2019re too sensitive\nto even realize\nit\u2019s happening.\u201d"
    max_hook_w = WIDTH - 120
    raw_lines = hook.split("\n")
    lines: List[str] = []
    for rl in raw_lines:
        lines.extend(wrap(rl, hook_font, max_hook_w))
    lh = text_height(hook_font) + 28
    total = lh * len(lines)
    y = (HEIGHT - total) // 2 - 60

    for line in lines:
        x = center_x(hook_font, line)
        # Subtle green shadow offset
        draw.text((x + 3, y + 3), line, fill=(*NEON_GREEN, 40), font=hook_font)
        draw.text((x, y), line, fill=WHITE, font=hook_font)
        y += lh

    # Accent bar below text
    draw_accent_bar(draw, y + 40, NEON_GREEN, width=2, margin=200)

    # Sub-label
    sub_font = fonts["tiny"]
    sub = "5 phrases gaslighters actually use"
    draw.text((center_x(sub_font, sub), y + 70), sub, fill=MID_GRAY, font=sub_font)

    draw_branding(draw, fonts)

    img = img.convert("RGB")
    return apply_scanlines(img, opacity=18)


# ---------------------------------------------------------------------------
# Slide 2-6 — Content slides
# ---------------------------------------------------------------------------

CONTENT_SLIDES = [
    {
        "number": "01",
        "phrase": "\u201cThat never\nhappened.\u201d",
        "body": (
            "The gold standard of gaslighting.\n"
            "Denying events you both lived through\n"
            "isn\u2019t a memory issue \u2014 it\u2019s a control strategy."
        ),
    },
    {
        "number": "02",
        "phrase": "\u201cYou\u2019re too\nsensitive.\u201d",
        "body": (
            "Translation: your reaction to my behavior\n"
            "is the problem,\n"
            "not my behavior."
        ),
    },
    {
        "number": "03",
        "phrase": "\u201cYou always twist\nmy words.\u201d",
        "body": (
            "Notice the word \u201calways.\u201d\n"
            "Absolute language is designed to make\n"
            "you feel like a chronic, unfixable problem."
        ),
    },
    {
        "number": "04",
        "phrase": "\u201cEveryone agrees\nwith me, not you.\u201d",
        "body": (
            "Invoking a silent jury that conveniently\n"
            "never testifies.\n"
            "Classic isolation tactic."
        ),
    },
    {
        "number": "05",
        "phrase": "\u201cI was just joking.\nYou have no sense\nof humor.\u201d",
        "body": (
            "The retroactive joke.\n"
            "Any behavior becomes a \u201cjoke\u201d\n"
            "the moment you object to it."
        ),
    },
]


def slide_content(fonts: dict, data: dict, slide_num: int) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_corner_brackets(draw, DARK_GRAY, margin=55, size=70, width=3)
    draw_glitch_stripes(draw, seed=slide_num * 17, count=2)

    # Phrase number — top left (large, dim green)
    num_font = fonts["hook"]
    num_str = f"#{data['number']}"
    draw.text((80, 130), num_str, fill=(*NEON_GREEN, 55), font=num_font)

    # Accent line
    draw_accent_bar(draw, 290, NEON_GREEN, width=3, margin=80)

    # Phrase — white, bold (wrap to canvas width)
    phrase_font = fonts["phrase"]
    max_phrase_w = WIDTH - 120
    phrase_lines: List[str] = []
    for rl in data["phrase"].split("\n"):
        phrase_lines.extend(wrap(rl, phrase_font, max_phrase_w))
    lh_phrase = text_height(phrase_font) + 22

    # Place phrase starting at ~330
    y = 330
    for line in phrase_lines:
        x = center_x(phrase_font, line)
        draw.text((x + 2, y + 2), line, fill=(*NEON_GREEN, 30), font=phrase_font)
        draw.text((x, y), line, fill=WHITE, font=phrase_font)
        y += lh_phrase

    y += 50  # gap

    # Thin divider
    draw_accent_bar(draw, y, DARK_GRAY, width=1, margin=200)
    y += 40

    # Body text — light gray, monospace (wrap each explicit line to max_w)
    body_font = fonts["body"]
    lh_body = text_height(body_font) + 18
    max_body_w = WIDTH - 160
    for raw_line in data["body"].split("\n"):
        for subline in wrap(raw_line.strip(), body_font, max_body_w):
            x = center_x(body_font, subline)
            draw.text((x, y), subline, fill=LIGHT_GRAY, font=body_font)
            y += lh_body

    draw_branding(draw, fonts)

    img = img.convert("RGB")
    return apply_scanlines(img, opacity=18)


# ---------------------------------------------------------------------------
# Slide 7 — CTA
# ---------------------------------------------------------------------------

SAFETY_DISCLAIMER = (
    "ToxShield identifies behavioral patterns. Not a substitute for professional counseling.",
    "If you are in danger, contact emergency services.",
)


def slide_07_cta(fonts: dict) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Green glow band at bottom — very subtle
    for i in range(300):
        alpha = int(20 * (i / 300))
        draw.line([(0, HEIGHT - 300 + i), (WIDTH, HEIGHT - 300 + i)], fill=(*NEON_GREEN, alpha))

    draw_corner_brackets(draw, NEON_GREEN, margin=55, size=90, width=5)
    draw_glitch_stripes(draw, seed=77, count=5)

    # "YOUR GUT WAS RIGHT." — center
    gut_font = fonts["hook"]
    line1 = "Your gut was right."
    y = 280
    x = center_x(gut_font, line1)
    draw.text((x + 3, y + 3), line1, fill=(*NEON_GREEN, 40), font=gut_font)
    draw.text((x, y), line1, fill=NEON_GREEN, font=gut_font)
    y += text_height(gut_font) + 30

    draw_accent_bar(draw, y + 10, NEON_GREEN, width=3, margin=100)
    y += 70

    # Body copy
    body_lines = [
        "If these phrases sound familiar,",
        "trust what you already know.",
    ]
    body_font = fonts["body"]
    lh = text_height(body_font) + 20
    for line in body_lines:
        draw.text((center_x(body_font, line), y), line, fill=LIGHT_GRAY, font=body_font)
        y += lh

    y += 50

    # CTA box
    cta_font = fonts["small"]
    cta_lines = [
        "Go to toxshield.in",
        "to see the toxic people in your life.",
    ]
    box_pad = 40
    cta_lh = text_height(cta_font) + 16
    box_h = cta_lh * len(cta_lines) + box_pad * 2
    box_w = 820
    box_x = (WIDTH - box_w) // 2
    # Border only — fill is handled via a separate composited overlay below
    draw.rectangle(
        [(box_x, y), (box_x + box_w, y + box_h)],
        outline=NEON_GREEN, width=3,
    )
    # Subtle inner tint: composite a separate RGBA patch
    tint = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tint_draw = ImageDraw.Draw(tint)
    tint_draw.rectangle(
        [(box_x + 3, y + 3), (box_x + box_w - 3, y + box_h - 3)],
        fill=(*NEON_GREEN, 14),
    )
    img = Image.alpha_composite(img, tint)
    draw = ImageDraw.Draw(img, "RGBA")  # re-acquire draw handle after composite
    ty = y + box_pad
    for line in cta_lines:
        draw.text((center_x(cta_font, line), ty), line, fill=NEON_GREEN, font=cta_font)
        ty += cta_lh
    y += box_h + 60

    # Follow prompt
    follow_font = fonts["small"]
    follow = f"Follow {HANDLE_TEXT} for more."
    draw.text((center_x(follow_font, follow), y), follow, fill=MID_GRAY, font=follow_font)
    y += text_height(follow_font) + 80

    # Safety disclaimer — bottom
    disc_font = fonts["micro"]
    disc_y = HEIGHT - 220
    for line in SAFETY_DISCLAIMER:
        draw.text((center_x(disc_font, line), disc_y), line, fill=(*MUTED_TEXT, 180), font=disc_font)
        disc_y += text_height(disc_font) + 12

    draw_branding(draw, fonts)

    img = img.convert("RGB")
    return apply_scanlines(img, opacity=18)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = Path("/Users/biswa/toxshield/output/instagram/2026-03-25/toxic_callout")
    out_dir.mkdir(parents=True, exist_ok=True)

    fonts = load_fonts()
    print("Fonts loaded.")

    slides = []

    # Slide 1
    s1 = slide_01_hook(fonts)
    slides.append(s1)
    p = out_dir / "slide_01.png"
    s1.save(str(p), "PNG")
    print(f"  Saved {p}")

    # Slides 2-6
    for i, data in enumerate(CONTENT_SLIDES):
        slide = slide_content(fonts, data, slide_num=i + 2)
        slides.append(slide)
        p = out_dir / f"slide_{i + 2:02d}.png"
        slide.save(str(p), "PNG")
        print(f"  Saved {p}")

    # Slide 7
    s7 = slide_07_cta(fonts)
    slides.append(s7)
    p = out_dir / "slide_07.png"
    s7.save(str(p), "PNG")
    print(f"  Saved {p}")

    print(f"\nDone — {len(slides)} slides in {out_dir}")


if __name__ == "__main__":
    main()
