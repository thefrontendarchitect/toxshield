#!/usr/bin/env python3
"""
ToxShield long-form video generator.

Generates 5-20 minute slide-based MP4 videos from structured JSON scripts,
suitable for YouTube long-form content (storytime, deep dives, explainers).

Uses the same Pillow slide rendering + FFmpeg assembly pipeline as Shorts,
but with section-aware timing, variable per-slide durations, and chapter
marker generation.

Requirements:
    - FFmpeg >= 5.0 (brew install ffmpeg)
    - Pillow >= 10.2.0

Usage:
    # Generate from a JSON script
    python scripts/youtube/generate_longform.py \
        --script output/youtube/scripts/narcissist_storytime.json \
        --output output/youtube/longform/narcissist_storytime/video.mp4

    # With background music (looped)
    python scripts/youtube/generate_longform.py \
        --script output/youtube/scripts/narcissist_storytime.json \
        --mood dark-ambient

    # With custom crossfade
    python scripts/youtube/generate_longform.py \
        --script output/youtube/scripts/narcissist_storytime.json \
        --crossfade 0.5
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Add instagram scripts to path for imports
sys.path.insert(0, str(SCRIPTS_DIR / "instagram"))

# ===========================================================================
# Constants
# ===========================================================================

MIN_DURATION = 300   # 5 minutes minimum
MAX_DURATION = 1200  # 20 minutes maximum
MAX_SLIDES = 100
DEFAULT_SLIDE_DURATION = 15  # seconds per slide (overridden by section config)
DEFAULT_CROSSFADE_DURATION = 1.0
MAX_SLIDE_DURATION = 12.0   # Maximum seconds any single slide stays on screen
MIN_SLIDE_DURATION = 6.0    # Minimum seconds (prevents too-fast sub-slides)
STRUCTURAL_MAX_DURATION = 20.0  # Higher cap for title/CTA slides
ASPECT_RATIO = "9:16"  # Vertical format for consistency with Shorts


# ===========================================================================
# Script Loader
# ===========================================================================

def load_script(script_path: str) -> Dict[str, Any]:
    """Load and validate a long-form video script from JSON."""
    path = Path(script_path)
    if not path.exists():
        logger.error(f"Script file not found: {path}")
        sys.exit(1)

    with open(path) as f:
        script = json.load(f)

    # Validate required fields
    if "title" not in script:
        logger.error("Script missing required field: title")
        sys.exit(1)
    if "sections" not in script or not script["sections"]:
        logger.error("Script missing required field: sections (must be non-empty)")
        sys.exit(1)

    # Validate each section
    total_duration = 0
    total_slides = 0
    for i, section in enumerate(script["sections"]):
        if "name" not in section:
            logger.error(f"Section {i} missing required field: name")
            sys.exit(1)
        if "slides" not in section or not section["slides"]:
            logger.error(f"Section '{section['name']}' missing required field: slides")
            sys.exit(1)

        duration = section.get("duration_seconds", len(section["slides"]) * DEFAULT_SLIDE_DURATION)
        section["duration_seconds"] = duration
        total_duration += duration
        total_slides += len(section["slides"])

    if total_slides > MAX_SLIDES:
        logger.warning(f"Script has {total_slides} slides (max {MAX_SLIDES}), will truncate")

    if total_duration < MIN_DURATION:
        logger.warning(
            f"Script total duration {total_duration}s is below minimum {MIN_DURATION}s. "
            "Consider adding more content."
        )
    elif total_duration > MAX_DURATION:
        logger.warning(
            f"Script total duration {total_duration}s exceeds maximum {MAX_DURATION}s. "
            "Consider splitting into multiple videos."
        )

    logger.info(f"Loaded script: \"{script['title']}\"")
    logger.info(f"  Sections: {len(script['sections'])}, Slides: {total_slides}, Duration: {total_duration}s ({total_duration / 60:.1f}m)")

    return script


# ===========================================================================
# Auto-Split Engine
# ===========================================================================

def _parse_body_groups(body: List[str]) -> List[List[str]]:
    """Split body lines into paragraph groups delimited by empty lines."""
    groups: List[List[str]] = []
    current: List[str] = []
    for line in body:
        if not line.strip():
            if current:
                groups.append(current)
                current = []
        else:
            current.append(line)
    if current:
        groups.append(current)
    return groups if groups else [[]]


def _distribute_groups(groups: List[List[str]], num_sub_slides: int) -> List[List[str]]:
    """Distribute paragraph groups across sub-slides as a progressive reveal.

    Returns a list of num_sub_slides items, each being a flat list of body lines.
    """
    if not groups or num_sub_slides <= 1:
        flat: List[str] = []
        for g in groups:
            if flat:
                flat.append("")
            flat.extend(g)
        return [flat]

    # If more sub-slides than groups, break groups into individual lines
    if num_sub_slides > len(groups):
        all_lines = [line for g in groups for line in g if line.strip()]
        groups = [[line] for line in all_lines]

    # Still more sub-slides than lines? Cap sub-slide count
    if num_sub_slides > len(groups):
        num_sub_slides = max(len(groups), 1)

    result: List[List[str]] = [[] for _ in range(num_sub_slides)]
    for i, group in enumerate(groups):
        target = i % num_sub_slides
        if result[target]:
            result[target].append("")
        result[target].extend(group)

    return result


def split_section_slides(
    section_slides: List[Dict[str, Any]],
    section_duration: float,
    max_slide_duration: float = MAX_SLIDE_DURATION,
    min_slide_duration: float = MIN_SLIDE_DURATION,
) -> List[Dict[str, Any]]:
    """Expand a section's slides so no single slide exceeds max_slide_duration.

    Uses progressive-reveal splitting: body text is distributed across sub-slides
    so each sub-slide shows a subset of the content.
    """
    from math import ceil

    num_original = len(section_slides)
    if num_original == 0:
        return section_slides

    time_share = section_duration / num_original
    if time_share <= max_slide_duration:
        return section_slides

    expanded: List[Dict[str, Any]] = []
    for slide_data in section_slides:
        slide_type = slide_data.get("type", "content")

        # Title/CTA slides get a higher duration cap
        effective_max = STRUCTURAL_MAX_DURATION if slide_type in ("title", "cta") else max_slide_duration
        if time_share <= effective_max:
            expanded.append(slide_data)
            continue

        # Calculate how many sub-slides we need
        num_sub = ceil(time_share / effective_max)
        # Ensure each sub-slide meets minimum duration
        while num_sub > 1 and (time_share / num_sub) < min_slide_duration:
            num_sub -= 1

        if num_sub <= 1:
            expanded.append(slide_data)
            continue

        # Split body across sub-slides
        headline = slide_data.get("headline", "")
        body = slide_data.get("body", [])
        groups = _parse_body_groups(body)
        distributed = _distribute_groups(groups, num_sub)

        for sub_body in distributed:
            expanded.append({
                "headline": headline,
                "body": sub_body,
                "type": slide_type,
            })

    return expanded


# ===========================================================================
# Slide Generator
# ===========================================================================

def generate_slides(
    script: Dict[str, Any],
    output_dir: Path,
) -> tuple[List[Path], List[float]]:
    """Generate PNG slides from script sections.

    Returns (slide_paths, slide_durations) where each slide has its
    own duration based on the section it belongs to.
    """
    try:
        from generate_carousel import (
            generate_carousel,
            load_fonts,
            render_title_slide,
            render_content_slide,
            render_cta_slide,
            draw_background,
            ASPECT_RATIOS,
        )
    except ImportError:
        logger.error(
            "Cannot import generate_carousel. Ensure scripts/instagram/generate_carousel.py exists "
            "and Pillow is installed."
        )
        sys.exit(1)

    from PIL import Image

    output_dir.mkdir(parents=True, exist_ok=True)

    # Set canvas height for 9:16 aspect ratio
    height = ASPECT_RATIOS.get(ASPECT_RATIO, 1920)

    fonts = load_fonts()
    slide_paths: List[Path] = []
    slide_durations: List[float] = []
    slide_index = 0

    for section in script["sections"]:
        section_slides = section["slides"]
        section_duration = section["duration_seconds"]

        # Auto-split slides that would exceed MAX_SLIDE_DURATION
        expanded_slides = split_section_slides(section_slides, section_duration)
        per_slide_duration = section_duration / len(expanded_slides)

        if len(expanded_slides) != len(section_slides):
            logger.info(
                f"  Section '{section['name']}': {len(section_slides)} -> "
                f"{len(expanded_slides)} slides ({per_slide_duration:.1f}s each)"
            )

        for slide_data in expanded_slides:
            headline = slide_data.get("headline", "")
            body = slide_data.get("body", [])
            slide_type = slide_data.get("type", "content")

            # Render the slide
            if slide_type == "title" or (slide_index == 0 and headline and not body):
                img = render_title_slide(fonts, headline, slide_num=slide_index + 1)
            elif slide_type == "cta":
                img = render_cta_slide(fonts, headline or "Follow for more", slide_num=slide_index + 1)
            else:
                img = render_content_slide(
                    fonts,
                    headline=headline,
                    lines=body if isinstance(body, list) else [body],
                    slide_num=slide_index + 1,
                )

            # Resize to 9:16 if needed (render functions use module-level HEIGHT)
            if img.height != height:
                img = img.resize((1080, height), Image.LANCZOS)

            # Save
            slide_path = output_dir / f"slide_{slide_index + 1:03d}.png"
            img.save(slide_path, "PNG")
            slide_paths.append(slide_path)
            slide_durations.append(per_slide_duration)
            slide_index += 1

            if slide_index >= MAX_SLIDES:
                logger.warning(f"Reached max slides ({MAX_SLIDES}), stopping")
                return slide_paths, slide_durations

    avg_duration = sum(slide_durations) / len(slide_durations) if slide_durations else 0
    logger.info(f"Generated {len(slide_paths)} slides in {output_dir}")
    logger.info(f"  Average slide duration: {avg_duration:.1f}s (max allowed: {MAX_SLIDE_DURATION}s)")
    return slide_paths, slide_durations


# ===========================================================================
# Chapter Marker Generator
# ===========================================================================

def generate_chapters(script: Dict[str, Any], output_path: Path) -> str:
    """Generate YouTube chapter markers from script sections.

    Returns the formatted chapters string and writes to file.
    """
    lines = ["Chapters:"]
    cumulative = 0

    for section in script["sections"]:
        minutes = int(cumulative) // 60
        seconds = int(cumulative) % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        lines.append(f"{timestamp} {section['name']}")
        cumulative += section["duration_seconds"]

    chapters_text = "\n".join(lines)
    output_path.write_text(chapters_text)
    logger.info(f"Chapter markers written to {output_path}")
    return chapters_text


# ===========================================================================
# Video Assembly
# ===========================================================================

def assemble_video(
    slides_dir: Path,
    slide_durations: List[float],
    output_path: Path,
    crossfade: float = DEFAULT_CROSSFADE_DURATION,
    audio_path: Optional[str] = None,
    audio_volume: float = 0.5,
    transition: str = "crossfade",
) -> Path:
    """Assemble slides into a long-form MP4 video using ReelGenerator."""
    try:
        from generate_reel import ReelGenerator
    except ImportError:
        logger.error(
            "Cannot import generate_reel. Ensure scripts/instagram/generate_reel.py exists."
        )
        sys.exit(1)

    generator = ReelGenerator(
        slides_dir=str(slides_dir),
        output_path=str(output_path),
        slide_duration=DEFAULT_SLIDE_DURATION,  # Fallback for any slides without explicit duration
        crossfade_duration=crossfade,
        transition=transition,
        audio_path=audio_path,
        audio_volume=audio_volume,
        slide_durations=slide_durations,
        max_slides=MAX_SLIDES,
        audio_loop=True,  # Loop audio for long-form
    )

    return generator.generate()


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate long-form YouTube video from structured script"
    )
    parser.add_argument(
        "--script", "-s", required=True,
        help="Path to JSON script file",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output MP4 path (default: output/youtube/longform/<title>/video.mp4)",
    )
    parser.add_argument(
        "--crossfade", type=float, default=DEFAULT_CROSSFADE_DURATION,
        help=f"Crossfade duration in seconds (default: {DEFAULT_CROSSFADE_DURATION})",
    )
    parser.add_argument(
        "--transition", "-t", choices=["crossfade", "kenburns"],
        default="crossfade",
        help="Transition type (default: crossfade)",
    )
    parser.add_argument(
        "--audio", "-a",
        help="Path to background audio file (will be looped)",
    )
    parser.add_argument(
        "--mood", "-m",
        choices=["dark-ambient", "tension", "empowering", "trending-beat"],
        help="Auto-select background track by mood (overridden by --audio)",
    )
    parser.add_argument(
        "--audio-volume", type=float, default=0.5,
        help="Audio volume 0.0-1.0 (default: 0.5, lower than Shorts for readability)",
    )
    parser.add_argument(
        "--slides-only", action="store_true",
        help="Generate slides only, skip video assembly",
    )

    args = parser.parse_args()

    # Step 1: Load script
    print("=== Step 1: Loading script ===")
    script = load_script(args.script)

    # Determine output paths
    title_slug = script["title"][:40].lower().replace(" ", "_").replace("'", "")
    title_slug = "".join(c for c in title_slug if c.isalnum() or c == "_")
    base_dir = PROJECT_ROOT / "output" / "youtube" / "longform" / title_slug

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = base_dir / "video.mp4"

    slides_dir = output_path.parent / "slides"
    chapters_path = output_path.parent / "chapters.txt"

    # Step 2: Generate slides
    print("\n=== Step 2: Generating slides ===")
    # Set HEIGHT for carousel module before generating slides
    try:
        import generate_carousel
        generate_carousel.HEIGHT = 1920  # 9:16 for YouTube
    except ImportError:
        pass

    slide_paths, slide_durations = generate_slides(script, slides_dir)

    if not slide_paths:
        print("Error: No slides generated", file=sys.stderr)
        sys.exit(1)

    # Step 3: Generate chapter markers
    print("\n=== Step 3: Generating chapter markers ===")
    chapters_text = generate_chapters(script, chapters_path)
    print(chapters_text)

    if args.slides_only:
        print(f"\n=== Slides only mode — skipping video assembly ===")
        print(f"Slides: {slides_dir}")
        print(f"Chapters: {chapters_path}")
        return

    # Step 4: Resolve audio
    audio_path = args.audio
    if not audio_path and args.mood:
        try:
            from download_music import get_track_for_mood
            audio_path = get_track_for_mood(args.mood)
            if audio_path:
                logger.info(f"Selected {args.mood} track: {audio_path}")
        except ImportError:
            logger.warning("download_music.py not found, skipping mood-based audio")

    # Step 5: Assemble video
    print("\n=== Step 4: Assembling video ===")
    total_duration = sum(slide_durations) - (len(slide_durations) - 1) * args.crossfade
    print(f"  Slides: {len(slide_paths)}")
    print(f"  Duration: {total_duration:.1f}s ({total_duration / 60:.1f} minutes)")
    print(f"  Transition: {args.transition}")
    print(f"  Audio: {audio_path or 'silent'} (volume: {args.audio_volume})")

    video_path = assemble_video(
        slides_dir=slides_dir,
        slide_durations=slide_durations,
        output_path=output_path,
        crossfade=args.crossfade,
        audio_path=audio_path,
        audio_volume=args.audio_volume,
        transition=args.transition,
    )

    # Step 6: Summary
    size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"\n=== Long-form video generated ===")
    print(f"  Video: {video_path} ({size_mb:.1f}MB)")
    print(f"  Duration: {total_duration / 60:.1f} minutes")
    print(f"  Chapters: {chapters_path}")
    print(f"  Slides: {slides_dir}")

    # Machine-readable output
    print(f"\n{json.dumps({
        'output': str(video_path),
        'duration_seconds': round(total_duration, 1),
        'duration_minutes': round(total_duration / 60, 1),
        'slides': len(slide_paths),
        'chapters': str(chapters_path),
        'size_mb': round(size_mb, 1),
    })}")


if __name__ == "__main__":
    main()
