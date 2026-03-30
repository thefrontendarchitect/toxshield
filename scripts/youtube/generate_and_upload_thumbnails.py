#!/usr/bin/env python3
"""
ToxShield — Batch thumbnail generator + uploader for existing YouTube Shorts.

Generates 2 A/B variant thumbnails per video (1280x720 PNG) using ToxShield's
dark terminal aesthetic, then uploads Variant A to each video via the YouTube
Data API v3 thumbnails.set endpoint.

Usage:
    python scripts/youtube/generate_and_upload_thumbnails.py
    python scripts/youtube/generate_and_upload_thumbnails.py --dry-run
    python scripts/youtube/generate_and_upload_thumbnails.py --generate-only
    python scripts/youtube/generate_and_upload_thumbnails.py --upload-only
"""

from __future__ import annotations

import argparse
import logging
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env.local")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False
    logger.error("Pillow not installed. Run: pip install -r scripts/youtube/requirements.txt")

# ===========================================================================
# Video Manifest
# Each entry defines the content for one Short.
#   video_id    — YouTube video ID
#   quote       — The weaponised phrase (displayed large)
#   label       — Forensic classification label (GASLIGHTING / DARVO / etc.)
#   context     — Short explanatory line
#   style       — Thumbnail style: danger | warning | toxic
#   score       — Toxicity score shown in badge (None to omit)
# ===========================================================================

VIDEOS: List[Dict] = [
    {
        "video_id": "4-ocLAQg5s8",
        "quote": '"You\'re Too Sensitive"',
        "label": "GASLIGHTING",
        "context": "Invalidating your reality",
        "style": "danger",
        "score": 8.4,
    },
    {
        "video_id": "1Wk4XUem2Ak",
        "quote": '"That Never Happened"',
        "label": "GASLIGHTING",
        "context": "The #1 gaslighting phrase",
        "style": "danger",
        "score": 9.1,
    },
    {
        "video_id": "UJOQf_7rAXY",
        "quote": '"You\'re the Problem Here"',
        "label": "DARVO",
        "context": "Deny, attack, reverse victim & offender",
        "style": "danger",
        "score": 8.7,
    },
    {
        "video_id": "RXEEfCa5D-Q",
        "quote": '"He\'s Just Stressed"',
        "label": "EXCUSE MAKING",
        "context": "500 analyses say otherwise",
        "style": "warning",
        "score": 7.2,
    },
    {
        "video_id": "iXY7T8Q3Lt4",
        "quote": '"After Everything I\'ve Done"',
        "label": "DARVO",
        "context": "Weaponised obligation",
        "style": "danger",
        "score": 8.9,
    },
    {
        "video_id": "Zcu4_Tl45iA",
        "quote": '"Why Are You So Boring Now?"',
        "label": "GREY ROCK",
        "context": "The method they're trying to break",
        "style": "warning",
        "score": None,
    },
]

# ===========================================================================
# Design constants (mirrors generate_thumbnail.py palette)
# ===========================================================================

W, H = 1280, 720

COLORS = {
    "bg":       (10,  10,  10),
    "surface1": (20,  20,  20),
    "white":    (255, 255, 255),
    "muted":    (90,  90,  90),
    "dim":      (50,  50,  50),
    "danger":   (229, 62,  62),
    "warning":  (214, 158, 46),
    "toxic":    (0,   255, 65),
    "safe":     (66,  153, 225),
    "critical": (213, 63,  140),
}

STYLE_ACCENT = {
    "danger":  COLORS["danger"],
    "warning": COLORS["warning"],
    "toxic":   COLORS["toxic"],
}

QUOTE_ZONE_W = int(W * 0.65)   # left 65% for the quote block
BADGE_CX = int(W * 0.83)       # score badge horizontal centre
BADGE_CY = H // 2
PADDING = 56


# ===========================================================================
# Font helpers
# ===========================================================================

def _find_first(candidates: List[Path]) -> Optional[str]:
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def _load_title_font_path() -> Optional[str]:
    return _find_first([
        Path("/System/Library/Fonts/Supplemental/Impact.ttf"),
        Path("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/SFCompact.ttf"),
    ])


def _load_mono_font_path() -> Optional[str]:
    return _find_first([
        Path("/System/Library/Fonts/Menlo.ttc"),
        Path("/System/Library/Fonts/SFNSMono.ttf"),
        Path("/System/Library/Fonts/Supplemental/Courier New.ttf"),
    ])


def _font(path: Optional[str], size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    if path:
        try:
            if path.endswith(".ttc"):
                return ImageFont.truetype(path, size, index=index)
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ===========================================================================
# Drawing helpers
# ===========================================================================

def _stroke_text(
    draw: ImageDraw.Draw,
    xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, ...],
    stroke: int = 3,
    stroke_fill: Tuple[int, ...] = (0, 0, 0),
) -> None:
    x, y = xy
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
    draw.text((x, y), text, font=font, fill=fill)


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> List[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        bb = font.getbbox(test)
        if (bb[2] - bb[0]) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def _glow(
    width: int, height: int,
    color: Tuple[int, int, int],
    rects: List[Tuple[int, int, int, int]],
    blur: int = 30,
    alpha: int = 130,
) -> Image.Image:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in rects:
        d.rectangle(r, fill=(*color, alpha))
    return layer.filter(ImageFilter.GaussianBlur(radius=blur))


def _score_ring(
    img: Image.Image,
    score: float,
    cx: int, cy: int,
    radius: int = 100,
    ring_w: int = 13,
    title_path: Optional[str] = None,
) -> None:
    """Draw a ToxicityRing arc with the score centred inside."""
    if score <= 3.0:
        color = COLORS["safe"]
    elif score <= 6.0:
        color = COLORS["warning"]
    elif score <= 8.0:
        color = COLORS["danger"]
    else:
        color = COLORS["critical"]

    draw = ImageDraw.Draw(img)
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]

    # Track
    draw.arc(bbox, start=0, end=360, fill=(*COLORS["dim"],), width=ring_w)
    # Filled arc
    sweep = (score / 10.0) * 360
    draw.arc(bbox, start=-90, end=-90 + sweep, fill=color, width=ring_w)

    # Score number
    sf = _font(title_path, 68, index=2)
    score_str = f"{score:.1f}"
    bb = sf.getbbox(score_str)
    sw, sh = bb[2] - bb[0], bb[3] - bb[1]
    _stroke_text(draw, (cx - sw // 2, cy - sh // 2 - 4), score_str, sf, color, stroke=2)

    # "/10" label
    lf = _font(title_path, 24)
    lb = lf.getbbox("/10")
    lw = lb[2] - lb[0]
    draw.text((cx - lw // 2, cy + sh // 2 + 4), "/10", font=lf, fill=COLORS["muted"])


def _watermark(draw: ImageDraw.Draw, mono_path: Optional[str]) -> None:
    f = _font(mono_path, 15)
    text = "TOXSHIELD"
    bb = f.getbbox(text)
    tw = bb[2] - bb[0]
    draw.text((W - tw - 18, H - 28), text, font=f, fill=COLORS["dim"])


# ===========================================================================
# Variant A — accent strip + quote block + score ring
# Layout:
#   Left strip (12px) in accent color with glow
#   Large quote in white (word-wrapped, left-aligned)
#   Label tag below quote in accent color
#   Score ring on right third (if score provided)
# ===========================================================================

def render_variant_a(v: Dict, title_path: Optional[str], mono_path: Optional[str]) -> Image.Image:
    accent = STYLE_ACCENT[v["style"]]
    img = Image.new("RGBA", (W, H), (*COLORS["bg"], 255))

    # Left accent glow + strip
    gl = _glow(W, H, accent, [(0, 0, 12, H)], blur=28, alpha=155)
    img = Image.alpha_composite(img, gl)
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (12, H)], fill=(*accent, 255))

    # Subtle vignette-style panel behind text
    panel_glow = _glow(W, H, accent, [(PADDING, H // 5, QUOTE_ZONE_W - 20, H * 4 // 5)],
                       blur=70, alpha=18)
    img = Image.alpha_composite(img, panel_glow)

    quote = v["quote"]
    label = v["label"]
    context = v["context"]
    score = v.get("score")

    # Compute quote font size adaptively
    qlen = len(quote)
    if qlen <= 18:
        qsize = 108
    elif qlen <= 26:
        qsize = 94
    elif qlen <= 36:
        qsize = 80
    else:
        qsize = 68

    qfont = _font(title_path, qsize, index=2)
    max_w = QUOTE_ZONE_W - PADDING * 2 - 20

    lines = _wrap(quote, qfont, max_w)
    lh = qfont.getbbox("Ag")[3] - qfont.getbbox("Ag")[1] + 10
    total_h = len(lines) * lh

    # Label above the quote
    label_font = _font(title_path, 32)
    lb_bb = label_font.getbbox(label)
    lb_h = lb_bb[3] - lb_bb[1]

    context_font = _font(mono_path or title_path, 22)
    ctx_bb = context_font.getbbox(context)
    ctx_h = ctx_bb[3] - ctx_bb[1]

    block_h = lb_h + 10 + total_h + 16 + ctx_h
    y = (H - block_h) // 2

    d = ImageDraw.Draw(img)

    # Label (e.g. "GASLIGHTING") in accent colour above the quote
    _stroke_text(d, (PADDING + 14, y), label, label_font, accent, stroke=2)
    y += lb_h + 10

    # Quote lines in white
    for line in lines:
        _stroke_text(d, (PADDING + 14, y), line, qfont, COLORS["white"], stroke=3)
        y += lh

    # Context line in muted
    d.text((PADDING + 16, y + 10), context, font=context_font, fill=COLORS["muted"])

    # Score ring on right panel
    if score is not None:
        _score_ring(img, score, BADGE_CX, BADGE_CY, radius=95, ring_w=13,
                    title_path=title_path)

    _watermark(ImageDraw.Draw(img), mono_path)
    return img.convert("RGB")


# ===========================================================================
# Variant B — bottom bar + centered quote + red/amber highlight on key word
# Layout:
#   Dark background with subtle noise overlay (scanline dots)
#   Bottom colour bar (8px) with glow
#   Quote centred horizontally (first keyword in accent, rest white)
#   Label pill badge top-right
# ===========================================================================

def render_variant_b(v: Dict, title_path: Optional[str], mono_path: Optional[str]) -> Image.Image:
    accent = STYLE_ACCENT[v["style"]]
    img = Image.new("RGBA", (W, H), (*COLORS["bg"], 255))

    # Very subtle scanline-style horizontal lines
    sl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sl_d = ImageDraw.Draw(sl)
    for y in range(0, H, 6):
        sl_d.line([(0, y), (W, y)], fill=(255, 255, 255, 6))
    img = Image.alpha_composite(img, sl)

    # Bottom accent bar with glow
    bar_glow = _glow(W, H, accent, [(0, H - 8, W, H)], blur=35, alpha=140)
    img = Image.alpha_composite(img, bar_glow)
    d = ImageDraw.Draw(img)
    d.rectangle([(0, H - 8), (W, H)], fill=(*accent, 255))

    # Top accent bar (thinner, 4px)
    d.rectangle([(0, 0), (W, 4)], fill=(*accent, 200))

    quote = v["quote"]
    label = v["label"]
    context = v["context"]
    score = v.get("score")

    qlen = len(quote)
    if qlen <= 18:
        qsize = 102
    elif qlen <= 26:
        qsize = 88
    elif qlen <= 36:
        qsize = 76
    else:
        qsize = 64

    qfont = _font(title_path, qsize, index=2)
    max_w = QUOTE_ZONE_W - PADDING * 2 - 20

    lines = _wrap(quote, qfont, max_w)
    lh = qfont.getbbox("Ag")[3] - qfont.getbbox("Ag")[1] + 10
    total_h = len(lines) * lh

    label_font = _font(title_path, 30)
    lb_bb = label_font.getbbox(label)
    lb_h = lb_bb[3] - lb_bb[1]

    context_font = _font(mono_path or title_path, 21)
    ctx_bb = context_font.getbbox(context)
    ctx_h = ctx_bb[3] - ctx_bb[1]

    block_h = total_h + 14 + ctx_h
    y_quote = (H - block_h) // 2

    d = ImageDraw.Draw(img)

    # Quote: colour the longest word in accent, rest white
    # Find longest token in the quote (strip punctuation for comparison)
    import re
    tokens = re.findall(r"[\w']+", quote)
    keyword = max(tokens, key=len) if tokens else ""

    for line in lines:
        # Render word by word with accent on the keyword
        words_in_line = line.split()
        x_cursor = PADDING + 14
        for wi, word in enumerate(words_in_line):
            clean = re.sub(r"[^a-zA-Z0-9']", "", word)
            color = accent if clean.lower() == keyword.lower() else COLORS["white"]
            _stroke_text(d, (x_cursor, y_quote), word, qfont, color, stroke=3)
            bb = qfont.getbbox(word + " ")
            x_cursor += bb[2] - bb[0]
        y_quote += lh

    # Context
    d.text((PADDING + 16, y_quote + 10), context, font=context_font, fill=COLORS["muted"])

    # Label pill — top-left corner
    pill_x, pill_y = PADDING + 14, 22
    pad = 10
    lb_w = lb_bb[2] - lb_bb[0]
    pill_rect = [pill_x - pad, pill_y - 4, pill_x + lb_w + pad, pill_y + lb_h + 4]
    d.rectangle(pill_rect, fill=(*accent, 220))
    d.text((pill_x, pill_y), label, font=label_font, fill=COLORS["bg"])

    # Score ring on right
    if score is not None:
        _score_ring(img, score, BADGE_CX, BADGE_CY, radius=95, ring_w=13,
                    title_path=title_path)

    _watermark(ImageDraw.Draw(img), mono_path)
    return img.convert("RGB")


# ===========================================================================
# Generate all thumbnails
# ===========================================================================

def generate_all(output_dir: Path) -> Dict[str, Dict[str, str]]:
    """Generate A + B variants for every video. Returns {video_id: {A: path, B: path}}."""
    output_dir.mkdir(parents=True, exist_ok=True)
    title_path = _load_title_font_path()
    mono_path = _load_mono_font_path()
    logger.info(f"Title font: {title_path or 'Pillow default'}")
    logger.info(f"Mono font:  {mono_path or 'Pillow default'}")

    results = {}
    for v in VIDEOS:
        vid = v["video_id"]
        logger.info(f"\nGenerating thumbnails for {vid} — {v['label']}")

        img_a = render_variant_a(v, title_path, mono_path)
        path_a = output_dir / f"{vid}_A.png"
        img_a.save(str(path_a), "PNG")
        logger.info(f"  Saved Variant A: {path_a}")

        img_b = render_variant_b(v, title_path, mono_path)
        path_b = output_dir / f"{vid}_B.png"
        img_b.save(str(path_b), "PNG")
        logger.info(f"  Saved Variant B: {path_b}")

        results[vid] = {"A": str(path_a), "B": str(path_b)}

    return results


# ===========================================================================
# Upload thumbnail via YouTube Data API v3 thumbnails.set
# ===========================================================================

def build_youtube_client():
    """Build authenticated YouTube API client from env vars."""
    client_id     = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        missing = [k for k, v in {
            "YOUTUBE_CLIENT_ID": client_id,
            "YOUTUBE_CLIENT_SECRET": client_secret,
            "YOUTUBE_REFRESH_TOKEN": refresh_token,
        }.items() if not v]
        raise RuntimeError(
            f"Missing YouTube credentials: {', '.join(missing)}. "
            "Run: python scripts/youtube/auth_setup.py --client-secrets <path>"
        )

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    return build("youtube", "v3", credentials=creds)


def upload_thumbnail(youtube, video_id: str, thumbnail_path: str, dry_run: bool = False) -> bool:
    """Upload a single thumbnail PNG via thumbnails.set. Returns True on success."""
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError

    if dry_run:
        logger.info(f"  [DRY RUN] Would upload {thumbnail_path} to video {video_id}")
        return True

    logger.info(f"  Uploading {thumbnail_path} -> video {video_id}")
    try:
        media = MediaFileUpload(thumbnail_path, mimetype="image/png")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=media,
        ).execute()
        logger.info(f"  OK — thumbnail set for {video_id}")
        return True
    except HttpError as e:
        code = e.resp.status
        if code == 403:
            body = e.content.decode("utf-8", errors="replace")
            if "quotaExceeded" in body:
                logger.error(
                    f"  Quota exceeded uploading thumbnail for {video_id}. "
                    "Resets at midnight PT."
                )
            elif "insufficientPermissions" in body:
                logger.error(
                    f"  Insufficient permissions for {video_id}. "
                    "Revoke at myaccount.google.com/permissions and re-run auth_setup.py --scopes all"
                )
            else:
                logger.error(f"  HTTP 403 for {video_id}: {body[:200]}")
        elif code == 404:
            logger.error(f"  Video not found: {video_id} (check video ID is correct)")
        else:
            logger.error(
                f"  HTTP {code} uploading thumbnail for {video_id}: "
                f"{e.content.decode('utf-8', errors='replace')[:200]}"
            )
        return False


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate A/B thumbnails for ToxShield Shorts and upload Variant A",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=str(PROJECT_ROOT / "output" / "youtube" / "thumbnails"),
        help="Output directory for PNG thumbnails",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Generate thumbnails but do not upload",
    )
    parser.add_argument(
        "--generate-only", action="store_true",
        help="Generate thumbnails only, skip upload entirely",
    )
    parser.add_argument(
        "--upload-only", action="store_true",
        help="Skip generation; upload existing Variant A thumbnails from output dir",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    # ------- Phase 3c: Generate thumbnails -------
    thumbnail_map: Dict[str, Dict[str, str]] = {}

    if args.upload_only:
        logger.info("Skipping generation (--upload-only)")
        for v in VIDEOS:
            vid = v["video_id"]
            path_a = output_dir / f"{vid}_A.png"
            path_b = output_dir / f"{vid}_B.png"
            thumbnail_map[vid] = {"A": str(path_a), "B": str(path_b)}
    else:
        if not PILLOW_OK:
            logger.error("Pillow not available. Install it first.")
            sys.exit(1)
        logger.info("=" * 60)
        logger.info("Phase 3c: Generating A/B thumbnails (1280x720)")
        logger.info("=" * 60)
        thumbnail_map = generate_all(output_dir)

    # Print summary of generated files
    print("\n--- Generated Thumbnails ---")
    for vid, paths in thumbnail_map.items():
        print(f"  {vid}:")
        print(f"    A: {paths['A']}")
        print(f"    B: {paths['B']}")

    if args.generate_only:
        print("\nGeneration complete (--generate-only, skipping upload).")
        return

    # ------- Phase 4c: Upload Variant A -------
    print("\n--- Phase 4c: Uploading Variant A thumbnails ---")
    print("(thumbnails.set costs 50 quota units each; 6 uploads = 300 units)\n")

    try:
        youtube = build_youtube_client()
    except Exception as e:
        logger.error(f"Failed to build YouTube client: {e}")
        sys.exit(1)

    results = {}
    for i, v in enumerate(VIDEOS):
        vid = v["video_id"]
        path_a = thumbnail_map[vid]["A"]

        if not Path(path_a).exists():
            logger.error(f"Thumbnail not found: {path_a}")
            results[vid] = "FAILED (file not found)"
            continue

        success = upload_thumbnail(youtube, vid, path_a, dry_run=args.dry_run)
        results[vid] = "OK" if success else "FAILED"

        # Throttle between requests to be courteous to the API
        if i < len(VIDEOS) - 1:
            time.sleep(1.0)

    # Final report
    print("\n" + "=" * 60)
    print("Upload Results")
    print("=" * 60)
    for v in VIDEOS:
        vid = v["video_id"]
        status = results.get(vid, "SKIPPED")
        icon = "OK" if status == "OK" else ("DRY_RUN" if args.dry_run else "FAIL")
        label = v["label"]
        print(f"  [{icon:7s}] {vid}  {label:15s}  {v['quote'][:40]}")

    successes = sum(1 for s in results.values() if s == "OK")
    print(f"\n{successes}/{len(VIDEOS)} thumbnails uploaded successfully.")
    if args.dry_run:
        print("(Dry run — no actual uploads performed)")

    print(f"\nThumbnail variants A/B saved to: {output_dir}")
    print("Switch to Variant B after 48h if CTR < 8% via YouTube Studio.")


if __name__ == "__main__":
    main()
