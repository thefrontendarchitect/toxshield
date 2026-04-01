"""
ToxShield carousel theme system.

Each theme is a Python module that exports:
    load_fonts() -> Dict[str, Optional[str]]
    render_title_slide(fonts, headline, slide_num, width, height) -> Image
    render_content_slide(fonts, headline, lines, slide_num, width, height) -> Image
    render_cta_slide(fonts, cta_text, slide_num, width, height) -> Image
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pass

# ===========================================================================
# Theme Registry
# ===========================================================================

_THEMES: Dict[str, object] = {}

AVAILABLE_THEMES = [
    "doodle", "neon-terminal", "forensic", "brutalist", "glitch", "surveillance",
    "pastel-soft",
    "arcane",
    "comedy-visual",
    "toxic-trading-card",
    "unhinged-text",
    "red-flag-meter",
    "meme-classic",
    "meme-chat",
    "meme-redflag",
]


def get_theme(name: str):
    """Load and return a theme module by name."""
    if name not in _THEMES:
        mod_name = name.replace("-", "_")
        try:
            module = importlib.import_module(f".{mod_name}", package="themes")
        except ImportError:
            # Try absolute import for when scripts are run from different dirs
            module = importlib.import_module(
                f"themes.{mod_name}",
            )
        _THEMES[name] = module
    return _THEMES[name]


# ===========================================================================
# Shared Constants
# ===========================================================================

FONT_SIZES = {
    "title":    86,
    "subtitle": 58,
    "body":     48,
    "small":    34,
    "tiny":     24,
}

SAFETY_DISCLAIMER = (
    "ToxShield identifies behavioral patterns. It is not a substitute\n"
    "for professional counseling. If you are in danger, contact\n"
    "emergency services."
)

_EMOJI_RE = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)


# ===========================================================================
# Shared Text Utilities
# ===========================================================================

def strip_emoji(text: str) -> str:
    return _EMOJI_RE.sub("", text).strip()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines or [text]


def line_height(font: ImageFont.FreeTypeFont, extra: int = 24) -> int:
    bbox = font.getbbox("Ag")
    return bbox[3] - bbox[1] + extra


def text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def draw_centered_lines(
    draw: ImageDraw.Draw,
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    y: int,
    color,
    width: int,
    lh: int,
) -> int:
    """Draw centered text lines. Returns y after last line."""
    for ln in lines:
        tw = text_width(ln, font)
        x = (width - tw) // 2
        draw.text((x, y), ln, fill=color, font=font)
        y += lh
    return y


# ===========================================================================
# Shared Font Utilities
# ===========================================================================

def find_font(candidates: List[Path], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    """Try font candidates in order, return first found or Pillow default."""
    for p in candidates:
        if p.exists():
            try:
                if str(p).endswith(".ttc"):
                    return ImageFont.truetype(str(p), size, index=index)
                return ImageFont.truetype(str(p), size)
            except (OSError, IOError):
                continue
    return ImageFont.load_default()


# Common font candidate lists
ROUNDED_FONTS = [
    Path("/System/Library/Fonts/Supplemental/Futura.ttc"),
    Path("/System/Library/Fonts/Supplemental/Avenir Next.ttc"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
    Path.home() / "Library/Fonts/Nunito-Bold.ttf",
    Path.home() / "Library/Fonts/Quicksand-Bold.ttf",
    Path.home() / "Library/Fonts/Poppins-Bold.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
]

ROUNDED_BODY_FONTS = [
    Path("/System/Library/Fonts/Supplemental/Avenir Next.ttc"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
    Path.home() / "Library/Fonts/Nunito-Regular.ttf",
    Path.home() / "Library/Fonts/Poppins-Regular.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]

MONO_FONTS = [
    Path("/System/Library/Fonts/Menlo.ttc"),
    Path("/System/Library/Fonts/SFMono.ttf"),
    Path("/System/Library/Fonts/Monaco.ttf"),
    Path.home() / "Library/Fonts/JetBrainsMono-Regular.ttf",
    Path("/System/Library/Fonts/Supplemental/Courier New.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
]

MONO_BOLD_FONTS = [
    Path("/System/Library/Fonts/Menlo.ttc"),
    Path.home() / "Library/Fonts/JetBrainsMono-Bold.ttf",
    Path("/System/Library/Fonts/Supplemental/Courier New Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
]

IMPACT_FONTS = [
    Path("/System/Library/Fonts/Supplemental/Impact.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Black.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]

TYPEWRITER_FONTS = [
    Path("/System/Library/Fonts/Supplemental/Courier New.ttf"),
    Path("/System/Library/Fonts/Supplemental/American Typewriter.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
]
