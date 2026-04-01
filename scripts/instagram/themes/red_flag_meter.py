"""Red Flag Meter theme — red/green flag scorecard with speedometer gauge.

Each content slide grades a behavior on a visual gauge (0-10 scale, green→yellow→red)
with a verdict badge and running tally. Drives debate engagement through binary judgments.

Content slide lines format:
  - Line 1: score as float (e.g., "8.7")
  - Line 2: verdict string ("RED FLAG" or "GREEN FLAG")
  - Line 3: explanation text
"""

from __future__ import annotations

import math
import random as _random
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    FONT_SIZES, IMPACT_FONTS, ROUNDED_BODY_FONTS, ROUNDED_FONTS,
    SAFETY_DISCLAIMER, find_font, line_height, strip_emoji, text_width, wrap_text,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_RUN_SEED = 0

_FONT_SIZES = {
    "title": 82,
    "subtitle": 56,
    "score": 90,
    "body": 42,
    "verdict": 52,
    "behavior": 44,
    "small": 30,
    "tally": 28,
    "tiny": 22,
}

# Colors
_BG = (13, 13, 13)
_RED_FLAG = (255, 45, 45)
_YELLOW = (255, 215, 0)
_GREEN_FLAG = (0, 210, 106)
_TEXT_WHITE = (255, 255, 255)
_TEXT_DIM = (160, 160, 170)
_TEXT_MUTED = (100, 100, 110)
_GAUGE_BG = (30, 30, 35)

# Running tally state (module-level, resets per run via seed)
_red_count = 0
_green_count = 0


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in IMPACT_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in ROUNDED_FONTS:
        if p.exists():
            fonts["body"] = str(p)
            break
    for p in ROUNDED_BODY_FONTS:
        if p.exists():
            fonts["small"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 28)
    if size_key in ("title", "subtitle", "verdict", "score"):
        font_path = fonts.get("headline")
    elif size_key in ("body", "behavior"):
        font_path = fonts.get("body")
        if font_path and font_path.endswith(".ttc"):
            try:
                return ImageFont.truetype(font_path, size, index=0)
            except (OSError, IOError):
                pass
    else:
        font_path = fonts.get("small") or fonts.get("body")
    if font_path:
        try:
            if font_path.endswith(".ttc"):
                return ImageFont.truetype(font_path, size, index=0)
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Score-based color interpolation
# ---------------------------------------------------------------------------

def _score_color(score: float) -> Tuple[int, int, int]:
    """Interpolate green→yellow→red based on 0-10 score."""
    t = max(0.0, min(score / 10.0, 1.0))
    if t < 0.4:
        # Green to yellow
        s = t / 0.4
        r = int(_GREEN_FLAG[0] + (_YELLOW[0] - _GREEN_FLAG[0]) * s)
        g = int(_GREEN_FLAG[1] + (_YELLOW[1] - _GREEN_FLAG[1]) * s)
        b = int(_GREEN_FLAG[2] + (_YELLOW[2] - _GREEN_FLAG[2]) * s)
    else:
        # Yellow to red
        s = (t - 0.4) / 0.6
        r = int(_YELLOW[0] + (_RED_FLAG[0] - _YELLOW[0]) * s)
        g = int(_YELLOW[1] + (_RED_FLAG[1] - _YELLOW[1]) * s)
        b = int(_YELLOW[2] + (_RED_FLAG[2] - _YELLOW[2]) * s)
    return (r, g, b)


# ---------------------------------------------------------------------------
# Semicircular gauge
# ---------------------------------------------------------------------------

def _draw_gauge(
    draw: ImageDraw.Draw, cx: int, cy: int, radius: int,
    score: float, thickness: int = 28,
):
    """Draw a semicircular speedometer gauge from green(0) to red(10)."""
    # Gauge arc: from 180° (left) to 0° (right), going clockwise
    # PIL arc angles: 0° = 3 o'clock, 90° = 6 o'clock, etc.
    # We want bottom semicircle: 180° to 360°
    arc_start = 180
    arc_end = 360

    # Background arc
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.arc(bbox, arc_start, arc_end, fill=(*_GAUGE_BG, 200), width=thickness)

    # Colored arc segments (draw many small segments for gradient effect)
    segments = 60
    for i in range(segments):
        seg_score = (i / segments) * 10.0
        if seg_score > score:
            break
        angle_start = 180 + (i / segments) * 180
        angle_end = 180 + ((i + 1) / segments) * 180
        color = _score_color(seg_score)
        draw.arc(bbox, angle_start, angle_end, fill=(*color, 230), width=thickness)

    # Tick marks at 0, 2.5, 5, 7.5, 10
    tick_r_outer = radius + thickness // 2 + 8
    tick_r_inner = radius + thickness // 2 + 2
    for tick_val in [0, 2.5, 5, 7.5, 10]:
        t = tick_val / 10.0
        angle = math.pi - t * math.pi  # 180° to 0° in radians
        x1 = cx + tick_r_inner * math.cos(angle)
        y1 = cy - tick_r_inner * math.sin(angle)
        x2 = cx + tick_r_outer * math.cos(angle)
        y2 = cy - tick_r_outer * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=(*_TEXT_DIM, 150), width=2)

    # Needle
    t = max(0.0, min(score / 10.0, 1.0))
    needle_angle = math.pi - t * math.pi  # radians
    needle_len = radius - thickness // 2 - 10
    needle_tip_x = cx + needle_len * math.cos(needle_angle)
    needle_tip_y = cy - needle_len * math.sin(needle_angle)

    # Needle as triangle
    perp_angle = needle_angle + math.pi / 2
    base_offset = 8
    base_x1 = cx + base_offset * math.cos(perp_angle)
    base_y1 = cy - base_offset * math.sin(perp_angle)
    base_x2 = cx - base_offset * math.cos(perp_angle)
    base_y2 = cy + base_offset * math.sin(perp_angle)

    draw.polygon(
        [(needle_tip_x, needle_tip_y), (base_x1, base_y1), (base_x2, base_y2)],
        fill=(*_TEXT_WHITE, 240),
    )
    # Center circle
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(*_TEXT_WHITE, 255))


# ---------------------------------------------------------------------------
# Parse content slide data
# ---------------------------------------------------------------------------

def _parse_verdict_data(lines: List[str]) -> Tuple[float, str, str]:
    """Parse score, verdict, and explanation from lines."""
    score = 5.0
    verdict = "RED FLAG"
    explanation = ""

    if len(lines) >= 1:
        try:
            score = float(lines[0].strip())
        except ValueError:
            pass
    if len(lines) >= 2:
        verdict = lines[1].strip().upper()
    if len(lines) >= 3:
        explanation = lines[2].strip()

    return score, verdict, explanation


# ===========================================================================
# Slide Rendering (standard theme API)
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    """Split-screen red/green + title + central gauge."""
    global _red_count, _green_count
    _red_count = 0
    _green_count = 0

    img = Image.new("RGBA", (width, height), (*_BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Split-screen background (red left, green right, with gradient blend)
    half = width // 2
    # Red half
    for x in range(half):
        alpha = int(40 + 30 * (x / half))
        draw.line([(x, 0), (x, height)], fill=(*_RED_FLAG, alpha))
    # Green half
    for x in range(half, width):
        alpha = int(70 - 30 * ((x - half) / half))
        draw.line([(x, 0), (x, height)], fill=(*_GREEN_FLAG, alpha))

    headline = strip_emoji(headline)
    title_font = _get_font(fonts, "title")
    sub_font = _get_font(fonts, "subtitle")

    # Title text
    max_w = width - 140
    wrapped = wrap_text(headline.upper(), title_font, max_w)
    lh = line_height(title_font, 16)
    total_h = len(wrapped) * lh

    y = height // 5
    for ln in wrapped:
        tw = text_width(ln, title_font)
        x = (width - tw) // 2
        # Shadow
        draw.text((x + 3, y + 3), ln, fill=(0, 0, 0, 150), font=title_font)
        draw.text((x, y), ln, fill=(*_TEXT_WHITE, 255), font=title_font)
        y += lh

    # Central gauge (decorative, needle at midpoint)
    gauge_y = height // 2 + 40
    _draw_gauge(draw, width // 2, gauge_y, 160, 5.0, thickness=24)

    # Score "?" in center
    q_font = _get_font(fonts, "score")
    q_text = "?"
    qw = text_width(q_text, q_font)
    draw.text(((width - qw) // 2, gauge_y - 80), q_text,
              fill=(*_TEXT_WHITE, 200), font=q_font)

    # "SWIPE TO JUDGE" subtitle
    sub_text = "SWIPE TO JUDGE"
    sw = text_width(sub_text, sub_font)
    draw.text(((width - sw) // 2, gauge_y + 50), sub_text,
              fill=(*_TEXT_DIM, 180), font=sub_font)

    # Watermark
    tiny_font = _get_font(fonts, "tiny")
    wm = "toxshield.in"
    ww = text_width(wm, tiny_font)
    draw.text(((width - ww) // 2, height - 60), wm,
              fill=(*_TEXT_MUTED, 150), font=tiny_font)

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    """Verdict card — behavior quote + gauge + verdict badge + tally."""
    global _red_count, _green_count

    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    score, verdict, explanation = _parse_verdict_data(lines)
    is_red = "RED" in verdict.upper()

    if is_red:
        _red_count += 1
    else:
        _green_count += 1

    accent = _RED_FLAG if is_red else _GREEN_FLAG

    img = Image.new("RGBA", (width, height), (*_BG, 255))

    # Subtle glow at top matching verdict color
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse(
        [width // 4, -200, 3 * width // 4, 200],
        fill=(*accent, 30),
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=60))
    img = Image.alpha_composite(img, glow_layer)

    draw = ImageDraw.Draw(img, "RGBA")

    # -- Behavior quote (top 25%) --
    behavior_font = _get_font(fonts, "behavior")
    max_w = width - 120
    behavior_text = headline or "Unknown behavior"
    wrapped_beh = wrap_text(f'"{behavior_text}"', behavior_font, max_w)
    beh_lh = line_height(behavior_font, 14)

    beh_y = 80
    for ln in wrapped_beh:
        tw = text_width(ln, behavior_font)
        x = (width - tw) // 2
        draw.text((x, beh_y), ln, fill=(*_TEXT_WHITE, 240), font=behavior_font)
        beh_y += beh_lh

    # -- Gauge (middle) --
    gauge_cx = width // 2
    gauge_cy = beh_y + 80 + 180  # 180 = radius
    gauge_radius = min(180, (width - 160) // 2)
    _draw_gauge(draw, gauge_cx, gauge_cy, gauge_radius, score, thickness=26)

    # Score number inside gauge
    score_font = _get_font(fonts, "score")
    score_text = f"{score:.1f}"
    stw = text_width(score_text, score_font)
    draw.text(
        ((width - stw) // 2, gauge_cy - 100),
        score_text, fill=(*_score_color(score), 255), font=score_font,
    )

    # -- Verdict badge --
    verdict_font = _get_font(fonts, "verdict")
    verdict_text = verdict.upper()
    vtw = text_width(verdict_text, verdict_font)
    badge_w = vtw + 60
    badge_h = 64
    badge_x = (width - badge_w) // 2
    badge_y = gauge_cy + 30

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=12, fill=(*accent, 230),
    )
    draw.text(
        ((width - vtw) // 2, badge_y + 8),
        verdict_text, fill=(*_TEXT_WHITE, 255), font=verdict_font,
    )

    # -- Explanation --
    if explanation:
        exp_font = _get_font(fonts, "small")
        exp_y = badge_y + badge_h + 30
        wrapped_exp = wrap_text(explanation, exp_font, max_w)
        exp_lh = line_height(exp_font, 10)
        for ln in wrapped_exp:
            tw = text_width(ln, exp_font)
            x = (width - tw) // 2
            draw.text((x, exp_y), ln, fill=(*_TEXT_DIM, 200), font=exp_font)
            exp_y += exp_lh

    # -- Running tally (footer) --
    tally_font = _get_font(fonts, "tally")
    tally_text = f"Red Flags: {_red_count}  |  Green Flags: {_green_count}"
    ttw = text_width(tally_text, tally_font)
    tally_y = height - 80

    # Tally background bar
    draw.rectangle(
        [0, tally_y - 10, width, tally_y + 40],
        fill=(20, 20, 25, 200),
    )
    draw.text(
        ((width - ttw) // 2, tally_y),
        tally_text, fill=(*_TEXT_DIM, 200), font=tally_font,
    )

    # Watermark
    tiny_font = _get_font(fonts, "tiny")
    wm = "toxshield.in"
    ww = text_width(wm, tiny_font)
    draw.text(((width - ww) // 2, height - 45), wm,
              fill=(*_TEXT_MUTED, 120), font=tiny_font)

    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    """Final scorecard with tally + CTA + disclaimer."""
    img = Image.new("RGBA", (width, height), (*_BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    cta_text = strip_emoji(cta_text)
    title_font = _get_font(fonts, "title")
    sub_font = _get_font(fonts, "subtitle")
    body_font = _get_font(fonts, "body")
    small_font = _get_font(fonts, "small")
    tiny_font = _get_font(fonts, "tiny")

    max_w = width - 140

    # Final score header
    header = "FINAL SCORE"
    hw = text_width(header, title_font)
    y = 100
    draw.text(((width - hw) // 2, y), header, fill=(*_TEXT_WHITE, 255), font=title_font)
    y += line_height(title_font, 30)

    # Red flag count (big, red)
    red_text = f"{_red_count} RED FLAG{'S' if _red_count != 1 else ''}"
    rw = text_width(red_text, sub_font)
    draw.text(((width - rw) // 2, y), red_text, fill=(*_RED_FLAG, 255), font=sub_font)
    y += line_height(sub_font, 20)

    # Green flag count (big, green)
    green_text = f"{_green_count} GREEN FLAG{'S' if _green_count != 1 else ''}"
    gw = text_width(green_text, sub_font)
    draw.text(((width - gw) // 2, y), green_text, fill=(*_GREEN_FLAG, 255), font=sub_font)
    y += line_height(sub_font, 50)

    # Divider line
    draw.line(
        [(width // 4, y), (3 * width // 4, y)],
        fill=(*_TEXT_MUTED, 100), width=2,
    )
    y += 40

    # CTA
    wrapped_cta = wrap_text(cta_text, body_font, max_w)
    cta_lh = line_height(body_font, 14)
    for ln in wrapped_cta:
        tw = text_width(ln, body_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=(*_TEXT_WHITE, 230), font=body_font)
        y += cta_lh

    # Sub-text
    y += 30
    sub_lines = ["toxshield.in", "Follow @toxshield.ai"]
    slh = line_height(small_font, 10)
    for sl in sub_lines:
        sw = text_width(sl, small_font)
        draw.text(((width - sw) // 2, y), sl, fill=(*_TEXT_DIM, 180), font=small_font)
        y += slh

    # Disclaimer
    disc_y = height - 120
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        dw = text_width(disc_line, tiny_font)
        draw.text(((width - dw) // 2, disc_y), disc_line,
                  fill=(*_TEXT_MUTED, 150), font=tiny_font)
        disc_y += 28

    return img.convert("RGB")
