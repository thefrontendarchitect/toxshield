"""Meme Chat theme — fake iMessage thread on LOUD arcane aurora background.

Accumulating messages over dense arcane aurora + neon graffiti doodles.
Chaotic Jinx-energy aesthetic — doodles everywhere, aurora punching through.

Content format for lines:
  - Lines starting with ">" = SENT (neon blue bubble, right-aligned)
  - Lines starting with "<" or no prefix = RECEIVED (dark glass bubble, left-aligned)
  - Lines starting with "@" = timestamp/status (e.g., "@Read 11:42 PM", "@2:47 AM")
  - Lines starting with "~" = typing indicator
"""

from __future__ import annotations

import math
import random as _random
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import arcane as _arcane
from . import (
    FONT_SIZES, ROUNDED_FONTS, ROUNDED_BODY_FONTS, SAFETY_DISCLAIMER,
    find_font, line_height, strip_emoji, text_width, wrap_text,
)

_RUN_SEED = 0

# Accumulated messages across slides (reset on title slide)
_accumulated_messages: List[dict] = []

_FONT_SIZES = {
    "message": 50,
    "contact": 48,
    "timestamp": 28,
    "status": 26,
    "input": 36,
    "small": 32,
    "tiny": 22,
}

# Neon-tinted chat bubble colors
_SENT_BUBBLE = (0, 120, 255)        # vivid blue
_RECV_BUBBLE = (20, 16, 40)         # deep purple-black
_TEXT_WHITE = (255, 255, 255)
_TEXT_CYAN = (120, 220, 255)         # neon cyan for timestamps
_TEXT_MAGENTA = (255, 100, 180)      # neon magenta for status
_HEADER_BG = (8, 5, 25, 180)
_SEPARATOR = (80, 40, 160)          # purple separator


def load_fonts() -> Dict[str, Optional[str]]:
    fonts: Dict[str, Optional[str]] = {"headline": None, "body": None, "small": None}
    for p in ROUNDED_FONTS:
        if p.exists():
            fonts["headline"] = str(p)
            break
    for p in ROUNDED_BODY_FONTS:
        if p.exists():
            fonts["body"] = fonts["small"] = str(p)
            break
    return fonts


def _get_font(fonts: Dict, size_key: str) -> ImageFont.FreeTypeFont:
    size = _FONT_SIZES.get(size_key, 32)
    font_path = fonts.get("body") or fonts.get("headline")
    if size_key == "contact":
        font_path = fonts.get("headline")
    if font_path:
        try:
            idx = 2 if (font_path.endswith(".ttc") and size_key == "contact") else 0
            if font_path.endswith(".ttc"):
                return ImageFont.truetype(font_path, size, index=idx)
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Arcane background — LOUD, less overlay
# ---------------------------------------------------------------------------

def _make_bg(width: int, height: int, slide_num: int) -> Image.Image:
    """Create arcane aurora background with LIGHT overlay — aurora punches through."""
    _arcane._RUN_SEED = _RUN_SEED
    img = _arcane._render_aurora_bg(width, height, slide_num)

    # Light overlay — let the aurora BREATHE (was 175, now 105)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 105))
    img = Image.alpha_composite(img, overlay)

    return img


def _draw_doodles_layer(
    draw: ImageDraw.Draw, width: int, height: int,
    slide_num: int, y_start: int, y_end: int,
    count: int = 15, scale_range: Tuple[float, float] = (0.6, 1.5),
    seed_offset: int = 0,
):
    """Draw dense arcane neon doodles across an area."""
    pal = _arcane._palette(slide_num)
    rng = _random.Random(slide_num * 777 + _RUN_SEED + seed_offset)

    available_h = y_end - y_start
    if available_h < 40:
        return

    # ALL doodle functions for maximum variety
    doodle_funcs = [
        _arcane._doodle_explosion_star,
        _arcane._doodle_graffiti_arrow,
        _arcane._doodle_x_mark,
        _arcane._doodle_scribble_circle,
        _arcane._doodle_lightning,
        _arcane._doodle_hex_crystal,
        _arcane._doodle_gear,
        _arcane._doodle_rune,
        _arcane._doodle_bomb,
        _arcane._doodle_bear_face,
        _arcane._doodle_scratchy_lines,
        _arcane._doodle_zigzag,
    ]

    for _ in range(count):
        fn = rng.choice(doodle_funcs)
        x = rng.randint(20, width - 20)
        y = rng.randint(y_start, max(y_start + 1, y_end - 10))
        scale = rng.uniform(*scale_range)
        color = _arcane._pick_neon(pal, rng)
        fn(draw, x, y, scale, rng, color)


def _draw_full_doodle_bg(draw: ImageDraw.Draw, width: int, height: int,
                          slide_num: int):
    """Draw doodles across the ENTIRE canvas as a background layer."""
    # Margin doodles — left and right edges
    _draw_doodles_layer(draw, width, height, slide_num,
                        y_start=100, y_end=height - 90,
                        count=20, scale_range=(0.4, 1.3), seed_offset=100)


# ---------------------------------------------------------------------------
# Chat bubble drawing — BIGGER padding and font
# ---------------------------------------------------------------------------

def _bubble_height(font: ImageFont.FreeTypeFont, text: str, max_inner: int) -> int:
    """Calculate the height a bubble would take."""
    pad_y = 24
    wrapped = wrap_text(text, font, max_inner)
    lh = line_height(font, 12)
    return len(wrapped) * lh + pad_y * 2 + 18  # +18 for gap between bubbles


def _msg_height(msg: dict, msg_font, ts_font, status_font, max_inner: int,
                prev_type: str = "") -> int:
    """Calculate height of a single message element, including sender-switch margin."""
    extra = 0
    # Add margin when switching between sent↔received
    if prev_type and msg["type"] in ("sent", "received") and prev_type in ("sent", "received"):
        if msg["type"] != prev_type:
            extra = 28  # big margin between different senders

    if msg["type"] in ("sent", "received"):
        return _bubble_height(msg_font, msg["text"], max_inner) + extra
    elif msg["type"] == "timestamp":
        return line_height(ts_font, 12) + 28
    elif msg["type"] == "status":
        return line_height(status_font, 12)
    elif msg["type"] == "typing":
        return 68
    return 0


def _draw_bubble(
    draw: ImageDraw.Draw, font: ImageFont.FreeTypeFont,
    text: str, y: int, max_width: int,
    is_sent: bool, canvas_width: int,
) -> int:
    """Draw clean Arcane chat bubble — pink for sent, gold for received. No clutter."""
    pad_x, pad_y = 34, 24
    text_color = _TEXT_WHITE

    inner_max = max_width - pad_x * 2
    wrapped = wrap_text(text, font, inner_max)
    lh = line_height(font, 12)

    max_line_w = max(text_width(ln, font) for ln in wrapped) if wrapped else 100
    bubble_w = max_line_w + pad_x * 2
    bubble_h = len(wrapped) * lh + pad_y * 2

    margin = 32
    if is_sent:
        bx = canvas_width - margin - bubble_w
    else:
        bx = margin

    if is_sent:
        # SENT: clean neon pink/magenta
        draw.rounded_rectangle(
            [bx, y, bx + bubble_w, y + bubble_h],
            radius=22, fill=(220, 30, 100, 235),
        )
    else:
        # RECEIVED: clean warm amber/gold
        draw.rounded_rectangle(
            [bx, y, bx + bubble_w, y + bubble_h],
            radius=22, fill=(180, 140, 20, 230),
        )
        text_color = (15, 10, 5)  # dark text on gold for readability

    ty = y + pad_y
    for ln in wrapped:
        if is_sent:
            tw = text_width(ln, font)
            tx = bx + bubble_w - pad_x - tw
        else:
            tx = bx + pad_x
        draw.text((tx, ty), ln, fill=text_color, font=font)
        ty += lh

    return y + bubble_h + 18


def _draw_timestamp(draw: ImageDraw.Draw, font: ImageFont.FreeTypeFont,
                    text: str, y: int, width: int) -> int:
    tw = text_width(text, font)
    draw.text(((width - tw) // 2, y), text, fill=_TEXT_CYAN, font=font)
    return y + line_height(font, 14)


def _draw_status(draw: ImageDraw.Draw, font: ImageFont.FreeTypeFont,
                 text: str, y: int, width: int) -> int:
    margin = 32
    tw = text_width(text, font)
    # Magenta for "Read" status, cyan for others
    color = _TEXT_MAGENTA if "read" in text.lower() else _TEXT_CYAN
    draw.text((width - margin - tw, y), text, fill=color, font=font)
    return y + line_height(font, 10)


def _draw_typing_indicator(draw: ImageDraw.Draw, y: int) -> int:
    bw, bh = 100, 50
    margin = 28
    draw.rounded_rectangle(
        [margin, y, margin + bw, y + bh],
        radius=20, fill=(*_RECV_BUBBLE, 180),
    )
    draw.rounded_rectangle(
        [margin, y, margin + bw, y + bh],
        radius=20, outline=(100, 60, 200, 40), width=1,
    )
    dot_r = 6
    dot_y = y + bh // 2
    for i, dx in enumerate([30, 50, 70]):
        draw.ellipse(
            [margin + dx - dot_r, dot_y - dot_r,
             margin + dx + dot_r, dot_y + dot_r],
            fill=(*_TEXT_CYAN, 200 - i * 40),
        )
    return y + bh + 10


def _draw_contact_header(img: Image.Image, fonts: Dict,
                         name: str, width: int) -> int:
    """Draw contact header with semi-transparent bg."""
    header_h = 96
    header_overlay = Image.new("RGBA", (width, header_h), _HEADER_BG)
    img.paste(
        Image.alpha_composite(
            img.crop((0, 0, width, header_h)).convert("RGBA"),
            header_overlay,
        ).convert("RGB"),
        (0, 0),
    )
    draw = ImageDraw.Draw(img, "RGBA")
    font = _get_font(fonts, "contact")
    tw = text_width(name, font)
    draw.text(((width - tw) // 2, 30), name, fill=_TEXT_WHITE, font=font)

    # Neon separator line
    draw.line([(0, header_h), (width, header_h)],
              fill=(*_SEPARATOR, 120), width=2)
    return header_h + 6


def _draw_input_bar(img: Image.Image, fonts: Dict,
                    width: int, height: int) -> None:
    """Draw tall arcane-glass input bar."""
    bar_h = 120
    bar_y = height - bar_h
    bar_overlay = Image.new("RGBA", (width, bar_h), (8, 5, 25, 210))
    img.paste(
        Image.alpha_composite(
            img.crop((0, bar_y, width, height)).convert("RGBA"),
            bar_overlay,
        ).convert("RGB"),
        (0, bar_y),
    )
    draw = ImageDraw.Draw(img, "RGBA")
    # Neon top border — double line for arcane feel
    draw.line([(0, bar_y), (width, bar_y)],
              fill=(120, 60, 220, 80), width=1)
    draw.line([(0, bar_y + 2), (width, bar_y + 2)],
              fill=(0, 160, 255, 40), width=1)

    margin = 24
    field_y = bar_y + 22
    field_h = bar_h - 44
    # Input field — arcane glass with glow
    # Outer glow
    draw.rounded_rectangle(
        [margin - 2, field_y - 2, width - margin + 2, field_y + field_h + 2],
        radius=28, fill=(60, 30, 140, 15),
    )
    # Glass fill
    draw.rounded_rectangle(
        [margin, field_y, width - margin, field_y + field_h],
        radius=26, fill=(15, 10, 35, 180),
    )
    # Glass highlight on top half
    draw.rounded_rectangle(
        [margin + 2, field_y + 2, width - margin - 2, field_y + field_h // 2],
        radius=24, fill=(60, 40, 100, 20),
    )
    # Neon purple border
    draw.rounded_rectangle(
        [margin, field_y, width - margin, field_y + field_h],
        radius=26, outline=(120, 60, 220, 100), width=2,
    )
    font = _get_font(fonts, "input")
    text_y = field_y + (field_h - _FONT_SIZES["input"]) // 2
    draw.text((margin + 28, text_y), "iMessage",
              fill=(120, 100, 180, 140), font=font)


# ---------------------------------------------------------------------------
# Parse message lines
# ---------------------------------------------------------------------------

def _parse_messages(lines: List[str]) -> List[dict]:
    """Parse lines into message objects."""
    messages = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            messages.append({"type": "sent", "text": line[1:].strip()})
        elif line.startswith("@"):
            text = line[1:].strip()
            if any(kw in text.lower() for kw in ["read", "delivered", "sent"]):
                messages.append({"type": "status", "text": text})
            else:
                messages.append({"type": "timestamp", "text": text})
        elif line.startswith("~"):
            messages.append({"type": "typing"})
        elif line.startswith("<"):
            messages.append({"type": "received", "text": line[1:].strip()})
        else:
            messages.append({"type": "received", "text": line})
    return messages


# ---------------------------------------------------------------------------
# Render all accumulated messages (bottom-aligned, scroll up)
# ---------------------------------------------------------------------------

def _render_messages(
    img: Image.Image, fonts: Dict,
    messages: List[dict], width: int,
    y_top: int, y_bottom: int,
) -> int:
    """Render messages bottom-aligned with sender-switch margins."""
    draw = ImageDraw.Draw(img, "RGBA")
    msg_font = _get_font(fonts, "message")
    ts_font = _get_font(fonts, "timestamp")
    status_font = _get_font(fonts, "status")
    max_bubble_w = int(width * 0.72)
    max_inner = max_bubble_w - 64  # account for bigger padding

    # Calculate heights with sender-switch awareness
    heights = []
    prev_type = ""
    for m in messages:
        h = _msg_height(m, msg_font, ts_font, status_font, max_inner, prev_type)
        heights.append(h)
        if m["type"] in ("sent", "received"):
            prev_type = m["type"]

    total_h = sum(heights)
    available_h = y_bottom - y_top

    # If overflow, show only the most recent that fit
    if total_h > available_h:
        cumulative = 0
        start_idx = len(messages)
        for i in range(len(messages) - 1, -1, -1):
            cumulative += heights[i]
            if cumulative > available_h:
                start_idx = i + 1
                break
            start_idx = i
        messages = messages[start_idx:]
        # Recalculate heights for trimmed list
        heights = []
        prev_type = ""
        for m in messages:
            h = _msg_height(m, msg_font, ts_font, status_font, max_inner, prev_type)
            heights.append(h)
            if m["type"] in ("sent", "received"):
                prev_type = m["type"]
        total_h = sum(heights)

    # Bottom-align
    y = y_bottom - total_h
    prev_type = ""

    for msg in messages:
        # Add margin when sender switches
        if msg["type"] in ("sent", "received") and prev_type in ("sent", "received"):
            if msg["type"] != prev_type:
                y += 28

        if msg["type"] == "sent":
            y = _draw_bubble(draw, msg_font, msg["text"], y, max_bubble_w, True, width)
            prev_type = "sent"
        elif msg["type"] == "received":
            y = _draw_bubble(draw, msg_font, msg["text"], y, max_bubble_w, False, width)
            prev_type = "received"
        elif msg["type"] == "timestamp":
            y += 10
            y = _draw_timestamp(draw, ts_font, msg["text"], y, width)
            y += 8
        elif msg["type"] == "status":
            y = _draw_status(draw, status_font, msg["text"], y, width)
        elif msg["type"] == "typing":
            y += 4
            y = _draw_typing_indicator(draw, y)

    return y


# ===========================================================================
# Slide Rendering
# ===========================================================================

def render_title_slide(fonts, headline, slide_num, width, height):
    """Title slide — dramatic hook text on arcane bg. No empty chat waste."""
    global _accumulated_messages
    _accumulated_messages = []

    img = _make_bg(width, height, slide_num)

    # Dense doodles behind
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_full_doodle_bg(draw, width, height, slide_num)

    headline = strip_emoji(headline)

    # Render headline as BIG dramatic centered text — immediate hook
    font = _get_font(fonts, "contact")
    # Use a larger size for the title
    title_size = _FONT_SIZES.get("message", 50) + 10
    font_path = fonts.get("headline") or fonts.get("body")
    if font_path:
        try:
            idx = 2 if font_path.endswith(".ttc") else 0
            if font_path.endswith(".ttc"):
                title_font = ImageFont.truetype(font_path, title_size, index=idx)
            else:
                title_font = ImageFont.truetype(font_path, title_size)
        except (OSError, IOError):
            title_font = font
    else:
        title_font = font

    display = headline.upper() if headline else "TOXIC EX"
    max_w = width - 140
    wrapped = wrap_text(display, title_font, max_w)
    lh = line_height(title_font, 16)
    total_h = len(wrapped) * lh

    y = (height - total_h) // 2
    for ln in wrapped:
        tw = text_width(ln, title_font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=(255, 255, 255, 255), font=title_font)
        y += lh

    return img.convert("RGB")


def render_content_slide(fonts, headline, lines, slide_num, width, height):
    """Chat slide — accumulating messages on arcane bg with doodles."""
    global _accumulated_messages

    headline = strip_emoji(headline)
    lines = [strip_emoji(line) for line in lines]

    # Parse and accumulate
    new_msgs = _parse_messages(lines)
    _accumulated_messages.extend(new_msgs)

    # Arcane aurora bg
    img = _make_bg(width, height, slide_num)

    # Draw doodle layer BEHIND the chat
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_full_doodle_bg(draw, width, height, slide_num)

    # Contact header
    contact = headline if headline and len(headline) < 30 else "toxic ex"
    header_bottom = _draw_contact_header(img, fonts, contact, width)

    # Chat zone
    chat_top = header_bottom
    chat_bottom = height - 128  # above taller input bar

    # Render ALL accumulated messages (bottom-aligned)
    _render_messages(img, fonts, _accumulated_messages,
                     width, chat_top, chat_bottom)

    _draw_input_bar(img, fonts, width, height)
    return img.convert("RGB")


def render_cta_slide(fonts, cta_text, slide_num, width, height):
    """CTA slide — arcane bg + doodles + chat-style CTA."""
    img = _make_bg(width, height, slide_num)

    draw = ImageDraw.Draw(img, "RGBA")
    _draw_full_doodle_bg(draw, width, height, slide_num)

    cta_text = strip_emoji(cta_text)
    header_bottom = _draw_contact_header(img, fonts, "toxshield.in", width)

    cta_messages = [
        {"type": "received", "text": cta_text},
        {"type": "received", "text": "toxshield.in"},
        {"type": "received", "text": "see the toxic people in your life"},
    ]

    chat_bottom = height - 96
    _render_messages(img, fonts, cta_messages, width, header_bottom, chat_bottom)

    # Disclaimer
    tiny_font = _get_font(fonts, "tiny")
    disc_y = height - 150
    for disc_line in SAFETY_DISCLAIMER.split("\n"):
        disc_line = disc_line.strip()
        dw = text_width(disc_line, tiny_font)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text(((width - dw) // 2, disc_y), disc_line,
                  fill=(100, 80, 140, 150), font=tiny_font)
        disc_y += 24

    _draw_input_bar(img, fonts, width, height)
    return img.convert("RGB")
