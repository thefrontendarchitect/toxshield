#!/usr/bin/env python3
"""
ToxShield Instagram background music manager.

Downloads royalty-free tracks from Pixabay or generates synthetic
atmospheric audio using FFmpeg for Instagram Reel backgrounds.

Usage:
    # Generate synthetic fallback tracks for all moods
    python scripts/instagram/download_music.py --generate-synthetic

    # Download from Pixabay for a specific mood
    python scripts/instagram/download_music.py --mood dark-ambient --pixabay-key YOUR_KEY

    # List available tracks
    python scripts/instagram/download_music.py --list
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
AUDIO_DIR = PROJECT_ROOT / "output" / "instagram" / "audio"
TRACKS_JSON = AUDIO_DIR / "tracks.json"

MOODS = {
    "dark-ambient": {
        "description": "Dark atmospheric drone — forensic/investigation vibe",
        "pixabay_query": "dark ambient atmospheric",
        "use_for": ["toxic_callout", "is_this_toxic", "pattern_breakdown"],
    },
    "tension": {
        "description": "Suspenseful cinematic tension — reveals and scores",
        "pixabay_query": "tension suspense cinematic",
        "use_for": ["score_reveal", "protection_tip"],
    },
    "empowering": {
        "description": "Uplifting motivational — self-reflection and growth",
        "pixabay_query": "empowering motivational",
        "use_for": ["self_check", "testimonial"],
    },
    "trending-beat": {
        "description": "Modern viral beat — memes and showcases",
        "pixabay_query": "trending viral beat",
        "use_for": ["meme_relatable", "app_showcase"],
    },
}

DURATION = 30  # seconds — Reel sweet spot


# ===========================================================================
# FFmpeg Synthetic Audio Generation
# ===========================================================================

def _check_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        logger.error("FFmpeg not found. Install: brew install ffmpeg")
        sys.exit(1)
    return ffmpeg


def generate_dark_ambient(ffmpeg: str, output: Path) -> bool:
    """Deep drone with pink noise — dark forensic investigation vibe."""
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", f"sine=frequency=65:duration={DURATION}",
        "-f", "lavfi", "-i", f"sine=frequency=98:duration={DURATION}",
        "-f", "lavfi", "-i", f"sine=frequency=130:duration={DURATION}",
        "-f", "lavfi", "-i", f"anoisesrc=d={DURATION}:c=pink:a=0.15",
        "-filter_complex",
        "[0]volume=1.0[s0];"
        "[1]volume=0.8[s1];"
        "[2]volume=0.6[s2];"
        "[3]volume=0.5[n];"
        "[s0][s1][s2][n]amix=inputs=4:duration=longest,"
        "lowpass=f=400,highpass=f=30,"
        f"afade=t=in:d=3,afade=t=out:st={DURATION - 3}:d=3,"
        "aecho=0.8:0.7:40:0.3,"
        "loudnorm=I=-14:TP=-1:LRA=11",
        "-ac", "2",
        "-b:a", "128k", "-ar", "44100",
        str(output),
    ]
    return _run_ffmpeg(cmd, output)


def generate_tension(ffmpeg: str, output: Path) -> bool:
    """Rising suspense with tremolo — score reveals and protection tips."""
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", f"sine=frequency=110:duration={DURATION}",
        "-f", "lavfi", "-i", f"sine=frequency=147:duration={DURATION}",
        "-f", "lavfi", "-i", f"anoisesrc=d={DURATION}:c=brown:a=0.12",
        "-filter_complex",
        "[0]volume=0.9,tremolo=f=4:d=0.3[s0];"
        "[1]volume=0.7,tremolo=f=3:d=0.2[s1];"
        "[2]volume=0.5[n];"
        "[s0][s1][n]amix=inputs=3:duration=longest,"
        "lowpass=f=500,highpass=f=40,"
        f"afade=t=in:d=2,afade=t=out:st={DURATION - 3}:d=3,"
        "loudnorm=I=-14:TP=-1:LRA=11",
        "-ac", "2",
        "-b:a", "128k", "-ar", "44100",
        str(output),
    ]
    return _run_ffmpeg(cmd, output)


def generate_empowering(ffmpeg: str, output: Path) -> bool:
    """Warm rising tones — growth and self-reflection."""
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", f"sine=frequency=220:duration={DURATION}",
        "-f", "lavfi", "-i", f"sine=frequency=330:duration={DURATION}",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={DURATION}",
        "-filter_complex",
        "[0]volume=0.8[s0];"
        "[1]volume=0.7[s1];"
        "[2]volume=0.5[s2];"
        "[s0][s1][s2]amix=inputs=3:duration=longest,"
        "lowpass=f=800,highpass=f=100,"
        f"afade=t=in:d=2,afade=t=out:st={DURATION - 3}:d=3,"
        "aecho=0.6:0.5:60:0.25,"
        "loudnorm=I=-14:TP=-1:LRA=11",
        "-ac", "2",
        "-b:a", "128k", "-ar", "44100",
        str(output),
    ]
    return _run_ffmpeg(cmd, output)


def generate_trending_beat(ffmpeg: str, output: Path) -> bool:
    """Lo-fi pulse beat — modern viral feel."""
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", f"sine=frequency=55:duration={DURATION}",
        "-f", "lavfi", "-i", f"sine=frequency=82:duration={DURATION}",
        "-f", "lavfi", "-i", f"anoisesrc=d={DURATION}:c=white:a=0.08",
        "-filter_complex",
        "[0]volume=1.0,tremolo=f=2:d=0.7[bass];"
        "[1]volume=0.7[mid];"
        "[2]volume=0.4,lowpass=f=200[click];"
        "[bass][mid][click]amix=inputs=3:duration=longest,"
        "lowpass=f=350,highpass=f=25,"
        f"afade=t=in:d=2,afade=t=out:st={DURATION - 3}:d=3,"
        "loudnorm=I=-14:TP=-1:LRA=11",
        "-ac", "2",
        "-b:a", "128k", "-ar", "44100",
        str(output),
    ]
    return _run_ffmpeg(cmd, output)


GENERATORS = {
    "dark-ambient": generate_dark_ambient,
    "tension": generate_tension,
    "empowering": generate_empowering,
    "trending-beat": generate_trending_beat,
}


def _run_ffmpeg(cmd: List[str], output: Path) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr[-200:]}")
            return False
        if output.exists() and output.stat().st_size > 1000:
            size_kb = output.stat().st_size / 1024
            logger.info(f"Generated: {output} ({size_kb:.0f}KB)")
            return True
        logger.error(f"Output too small or missing: {output}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg timed out")
        return False


def generate_all_synthetic() -> Dict[str, str]:
    """Generate synthetic tracks for all moods."""
    ffmpeg = _check_ffmpeg()
    results = {}

    for mood, generator in GENERATORS.items():
        mood_dir = AUDIO_DIR / mood
        mood_dir.mkdir(parents=True, exist_ok=True)
        output = mood_dir / "synth_track.mp3"
        logger.info(f"Generating {mood} track...")
        if generator(ffmpeg, output):
            results[mood] = str(output)
        else:
            logger.error(f"Failed to generate {mood}")

    # Save tracks index
    _update_tracks_json(results)
    return results


def generate_single_synthetic(mood: str) -> Optional[str]:
    """Generate a synthetic track for a single mood."""
    if mood not in GENERATORS:
        logger.error(f"Unknown mood: {mood}. Choose from: {list(GENERATORS.keys())}")
        return None

    ffmpeg = _check_ffmpeg()
    mood_dir = AUDIO_DIR / mood
    mood_dir.mkdir(parents=True, exist_ok=True)
    output = mood_dir / "synth_track.mp3"

    if GENERATORS[mood](ffmpeg, output):
        return str(output)
    return None


# ===========================================================================
# Track Management
# ===========================================================================

def _update_tracks_json(tracks: Dict[str, str]) -> None:
    existing = {}
    if TRACKS_JSON.exists():
        with open(TRACKS_JSON) as f:
            existing = json.load(f)

    for mood, path in tracks.items():
        if mood not in existing:
            existing[mood] = []
        entry = {
            "path": path,
            "source": "synthetic",
            "duration": DURATION,
        }
        # Replace existing synthetic entry or append
        existing[mood] = [e for e in existing[mood] if e.get("source") != "synthetic"]
        existing[mood].append(entry)

    with open(TRACKS_JSON, "w") as f:
        json.dump(existing, f, indent=2)
    logger.info(f"Updated {TRACKS_JSON}")


def list_tracks() -> None:
    """List all available tracks."""
    if not TRACKS_JSON.exists():
        print("No tracks found. Run with --generate-synthetic first.")
        return

    with open(TRACKS_JSON) as f:
        tracks = json.load(f)

    for mood, entries in tracks.items():
        info = MOODS.get(mood, {})
        print(f"\n{mood}: {info.get('description', '')}")
        print(f"  Content types: {', '.join(info.get('use_for', []))}")
        for entry in entries:
            path = entry["path"]
            exists = Path(path).exists()
            status = "OK" if exists else "MISSING"
            print(f"  [{status}] {path} ({entry.get('source', 'unknown')}, {entry.get('duration', '?')}s)")


def get_track_for_mood(mood: str) -> Optional[str]:
    """Get a track path for the given mood. Used by generate_reel.py."""
    if not TRACKS_JSON.exists():
        return None

    with open(TRACKS_JSON) as f:
        tracks = json.load(f)

    entries = tracks.get(mood, [])
    for entry in entries:
        path = Path(entry["path"])
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.exists():
            return str(path)
    return None


def get_mood_for_content_type(content_type: str) -> str:
    """Map content type to recommended mood."""
    for mood, info in MOODS.items():
        if content_type in info.get("use_for", []):
            return mood
    return "dark-ambient"  # default


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description="ToxShield Instagram background music manager")
    parser.add_argument("--generate-synthetic", action="store_true",
                        help="Generate synthetic tracks for all moods using FFmpeg")
    parser.add_argument("--mood", choices=list(MOODS.keys()),
                        help="Generate synthetic track for a single mood")
    parser.add_argument("--list", action="store_true",
                        help="List all available tracks")

    args = parser.parse_args()

    if args.list:
        list_tracks()
    elif args.generate_synthetic:
        results = generate_all_synthetic()
        print(f"\nGenerated {len(results)} tracks:")
        for mood, path in results.items():
            print(f"  {mood}: {path}")
        print(f"\n{json.dumps({'tracks': results, 'count': len(results)})}")
    elif args.mood:
        path = generate_single_synthetic(args.mood)
        if path:
            print(f"\nGenerated: {path}")
            print(f"\n{json.dumps({'mood': args.mood, 'path': path})}")
        else:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
