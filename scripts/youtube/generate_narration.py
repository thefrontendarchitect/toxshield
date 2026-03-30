#!/usr/bin/env python3
"""
ToxShield narration generator using OpenAI gpt-4o-mini-tts.

Generates per-slide TTS voice narration for Shorts and long-form videos,
measures audio durations, and outputs timing metadata for video sync.

Requirements:
    - openai>=1.30.0 (pip install openai)
    - FFmpeg >= 5.0 (for audio concatenation and duration measurement)
    - OPENAI_API_KEY in .env.local or environment

Usage:
    # From content.json (standard carousel pipeline)
    python scripts/youtube/generate_narration.py \
        --content-file output/instagram/2026-03-25/toxic_callout/content.json \
        --voice onyx

    # From direct slide text
    python scripts/youtube/generate_narration.py \
        --slides-json '[{"headline":"Hook","body":["Line 1","Line 2"]}]' \
        --voice onyx

    # With custom voice instructions
    python scripts/youtube/generate_narration.py \
        --content-file content.json \
        --instructions "Speak like a true crime documentary narrator"
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# ===========================================================================
# Constants
# ===========================================================================

DEFAULT_VOICE = "onyx"
DEFAULT_MODEL = "gpt-4o-mini-tts"
DEFAULT_BUFFER = 0.5  # seconds of silence after each clip
DEFAULT_SPEED = 1.0
MIN_SLIDE_DURATION = 3.0  # minimum seconds per slide (prevents jarring cuts)
MAX_SHORT_DURATION = 58.0  # warn if total exceeds this (60s limit minus safety margin)

DEFAULT_INSTRUCTIONS = (
    "You are a forensic behavioral analyst narrating a short documentary. "
    "Speak in a calm, measured, authoritative tone. Direct and confident. "
    "Pace yourself slightly slower than conversational speed. "
    "Add subtle dramatic weight to key phrases without being theatrical. "
    "No filler words. No upspeak. Clear enunciation."
)

# Voice instruction presets per content type
VOICE_PRESETS = {
    "toxic_callout": (
        "You are a forensic behavioral analyst exposing a toxic pattern. "
        "Authoritative, measured, with controlled intensity. "
        "Deliver each point like presenting evidence in a courtroom."
    ),
    "is_this_toxic": (
        "You are reacting to a scenario and scoring it in real time. "
        "Slightly more conversational, as if thinking aloud. "
        "Build tension before revealing the verdict."
    ),
    "score_reveal": (
        "You are revealing a toxicity score dramatically. "
        "Start measured, build intensity toward the number reveal. "
        "The score itself should land with weight."
    ),
    "protection_tip": (
        "You are a supportive guide teaching a protection strategy. "
        "Warm but authoritative. Empowering, not fearful. "
        "Speak as if coaching someone through a difficult situation."
    ),
    "pattern_breakdown": (
        "You are a psychology educator explaining a manipulation pattern. "
        "Clear, clinical, but accessible. "
        "Use the tone of a documentary explaining a complex phenomenon."
    ),
    "storytime_toxic": (
        "You are telling a dramatic case study story. "
        "Build narrative tension. Pause for effect at key reveals. "
        "Like a true crime narrator uncovering a pattern."
    ),
    "red_flag_listicle": (
        "You are rapidly revealing red flags one by one. "
        "Punchy, direct delivery. Each flag should hit like a headline. "
        "Slight urgency in your tone."
    ),
    "standup_comedy_male": (
        "You are performing standup comedy live on stage. Talk like a real person telling "
        "a funny story to friends at a bar — NOT like a narrator or announcer. "
        "Vary your pitch and energy naturally. Lean into words that matter. "
        "Speed up during setups like you're excited to get to the point. "
        "Then SLOW down right before the punchline — let it hang — then land it flat and dry. "
        "After a punchline, pause like you're waiting for the laugh. Smirk in your voice. "
        "Sound like you've told this story before and still find it ridiculous. "
        "Conversational. Slightly amused at your own pain. Dark but charming. "
        "Think of how a guy tells his buddy about his crazy ex — that's the energy."
    ),
    "standup_comedy_female": (
        "You are performing standup comedy live on stage. Talk like a real woman telling "
        "a hilarious dating horror story to her best friends over wine — NOT like a narrator. "
        "Vary your pitch and energy naturally. Get animated during setups. "
        "Speed up when building the absurdity, like you still can't believe it happened. "
        "Then SLOW down right before the punchline — pause — then deliver it deadpan. "
        "After a punchline, pause like you're letting the audience process what you just said. "
        "Sound exasperated, amused, and completely over it — all at once. "
        "Conversational. Knowing. Sharp. The kind of delivery where people say 'she's so real.' "
        "Think of how a woman roasts her toxic ex at brunch — that's the energy."
    ),
}


# ===========================================================================
# Audio Utilities
# ===========================================================================

def get_audio_duration(path: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(path),
            ],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except (subprocess.TimeoutExpired, KeyError, json.JSONDecodeError, ValueError) as e:
        logger.warning(f"ffprobe failed for {path}: {e}")
        # Fallback: estimate from file size (rough MP3 estimate: 16KB/s at 128kbps)
        size_kb = path.stat().st_size / 1024
        return size_kb / 16.0


def generate_silence(output_path: Path, duration: float) -> None:
    """Generate a silent audio file of the specified duration."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        logger.error("FFmpeg not found. Install: brew install ffmpeg")
        sys.exit(1)

    subprocess.run(
        [
            ffmpeg, "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono",
            "-t", str(duration),
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            str(output_path),
        ],
        capture_output=True, text=True, timeout=30,
    )


def concatenate_audio(clips: List[Path], output_path: Path) -> None:
    """Concatenate audio clips using FFmpeg concat demuxer."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        logger.error("FFmpeg not found. Install: brew install ffmpeg")
        sys.exit(1)

    # Write concat file list
    concat_file = output_path.parent / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            # Resolve to absolute path so ffmpeg concat works from any cwd
            escaped = str(clip.resolve()).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

    subprocess.run(
        [
            ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            str(output_path),
        ],
        capture_output=True, text=True, timeout=60,
    )

    # Clean up concat list
    concat_file.unlink(missing_ok=True)


# ===========================================================================
# Text Extraction
# ===========================================================================

def extract_slide_texts(content_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract narration text from content.json structure.

    Returns a list of dicts with 'type', 'headline', 'body', and 'narration'
    (the text to speak) for each slide.
    """
    slides = []
    headline = content_data.get("headline", "")
    cta = content_data.get("cta", "Save this for when you need it")
    adaptations = content_data.get("format_adaptations", {})
    num_slides = adaptations.get("carousel_slides", 7)
    num_slides = max(5, min(num_slides, 10))

    # Slide 1: Title/hook
    slides.append({
        "type": "title",
        "headline": headline,
        "body": "",
        "narration": headline,
    })

    # Content slides (2 through num_slides-1)
    for i in range(2, num_slides):
        title_key = f"slide_{i}_title"
        lines_key = f"slide_{i}_lines"
        slide_key = f"slide_{i}"

        slide_title = adaptations.get(title_key, "")
        slide_lines: List[str] = []

        if lines_key in adaptations:
            raw = adaptations[lines_key]
            slide_lines = raw if isinstance(raw, list) else [raw]
        elif slide_key in adaptations:
            slide_lines = [adaptations[slide_key]]

        body_text = " ".join(line.strip() for line in slide_lines if line.strip())

        # Build narration: title + body, natural speech flow
        parts = []
        if slide_title:
            parts.append(slide_title.strip('"').strip())
        if body_text:
            parts.append(body_text)
        narration = ". ".join(parts) if parts else "Protect your peace."

        slides.append({
            "type": "content",
            "headline": slide_title,
            "body": body_text,
            "narration": narration,
        })

    # CTA slide: adapt URL for speech
    cta_speech = cta
    # Make URLs speakable
    cta_speech = cta_speech.replace("toxshield.in", "tox shield dot in")
    cta_speech = cta_speech.replace("@toxshield.ai", "at tox shield dot A I")
    slides.append({
        "type": "cta",
        "headline": cta,
        "body": "",
        "narration": cta_speech,
    })

    return slides


def parse_slides_json(slides_json: str) -> List[Dict[str, str]]:
    """Parse direct JSON slide input."""
    raw = json.loads(slides_json)
    slides = []
    for item in raw:
        headline = item.get("headline", "")
        body_lines = item.get("body", [])
        body_text = " ".join(line.strip() for line in body_lines if line.strip())
        parts = [headline] if headline else []
        if body_text:
            parts.append(body_text)
        narration = ". ".join(parts) if parts else ""
        slides.append({
            "type": item.get("type", "content"),
            "headline": headline,
            "body": body_text,
            "narration": narration,
        })
    return slides


# ===========================================================================
# TTS Generation
# ===========================================================================

def generate_tts(
    text: str,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
    model: str = DEFAULT_MODEL,
    instructions: str = DEFAULT_INSTRUCTIONS,
    speed: float = DEFAULT_SPEED,
    max_retries: int = 3,
) -> None:
    """Generate TTS audio using OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai>=1.30.0")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set. Add it to .env.local or environment.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                instructions=instructions,
                response_format="mp3",
                speed=speed,
            )
            response.stream_to_file(str(output_path))
            return
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"TTS generation failed after {max_retries} attempts: {e}")
                raise
            wait = 2 ** attempt
            logger.warning(f"TTS attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)


# ===========================================================================
# Main Pipeline
# ===========================================================================

def generate_narration(
    slides: List[Dict[str, str]],
    output_dir: Path,
    voice: str = DEFAULT_VOICE,
    model: str = DEFAULT_MODEL,
    instructions: str = DEFAULT_INSTRUCTIONS,
    speed: float = DEFAULT_SPEED,
    buffer: float = DEFAULT_BUFFER,
    crossfade: float = 1.0,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate narration for all slides and return timing metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use content-type-specific voice preset if no custom instructions given
    if instructions == DEFAULT_INSTRUCTIONS and content_type and content_type in VOICE_PRESETS:
        instructions = VOICE_PRESETS[content_type]
        logger.info(f"Using voice preset for content type: {content_type}")

    # Check prerequisites
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        logger.error("ffprobe not found. Install FFmpeg: brew install ffmpeg")
        sys.exit(1)

    clips_data = []
    concat_parts: List[Path] = []  # alternating: clip, silence, clip, silence, ...

    logger.info(f"Generating narration for {len(slides)} slides (voice={voice}, model={model})")

    for i, slide in enumerate(slides):
        slide_num = i + 1
        narration_text = slide["narration"]

        if not narration_text.strip():
            logger.warning(f"Slide {slide_num}: empty narration text, skipping")
            # Generate a short silence for empty slides
            silence_path = output_dir / f"clip_{slide_num:02d}.mp3"
            generate_silence(silence_path, MIN_SLIDE_DURATION)
            duration = MIN_SLIDE_DURATION
            slide_duration = max(duration + buffer + crossfade, MIN_SLIDE_DURATION)
            clips_data.append({
                "slide": slide_num,
                "file": f"clip_{slide_num:02d}.mp3",
                "duration": round(duration, 2),
                "slide_duration": round(slide_duration, 2),
                "text": "",
                "type": slide["type"],
            })
            concat_parts.append(silence_path)
            continue

        # Generate TTS clip
        clip_path = output_dir / f"clip_{slide_num:02d}.mp3"
        logger.info(f"Slide {slide_num}/{len(slides)}: \"{narration_text[:60]}...\"")
        generate_tts(
            text=narration_text,
            output_path=clip_path,
            voice=voice,
            model=model,
            instructions=instructions,
            speed=speed,
        )

        # Measure duration
        # slide_duration must account for crossfade overlap: during crossfade,
        # the video timeline advances but the slide is already transitioning.
        # Without this, each crossfade steals ~1s, causing progressive desync.
        duration = get_audio_duration(clip_path)
        slide_duration = max(duration + buffer + crossfade, MIN_SLIDE_DURATION)

        clips_data.append({
            "slide": slide_num,
            "file": f"clip_{slide_num:02d}.mp3",
            "duration": round(duration, 2),
            "slide_duration": round(slide_duration, 2),
            "text": narration_text,
            "type": slide["type"],
        })

        concat_parts.append(clip_path)

        # Add silence buffer between clips (not after the last one)
        if buffer > 0 and i < len(slides) - 1:
            silence_path = output_dir / f"silence_{slide_num:02d}.mp3"
            generate_silence(silence_path, buffer)
            concat_parts.append(silence_path)

    # Concatenate all clips into full narration
    full_narration_path = output_dir / "full_narration.mp3"
    if concat_parts:
        logger.info("Concatenating clips into full narration...")
        concatenate_audio(concat_parts, full_narration_path)
    else:
        logger.error("No clips generated")
        sys.exit(1)

    total_duration = get_audio_duration(full_narration_path)
    slide_durations = [c["slide_duration"] for c in clips_data]

    # Duration warning for Shorts
    video_duration = sum(slide_durations) - (len(slides) - 1) * crossfade
    if video_duration > MAX_SHORT_DURATION:
        logger.warning(
            f"Estimated video duration ({video_duration:.1f}s) exceeds {MAX_SHORT_DURATION}s. "
            f"Consider reducing slides or increasing TTS speed (current: {speed}x)."
        )

    # Write timing metadata
    timing = {
        "voice": voice,
        "model": model,
        "instructions": instructions,
        "speed": speed,
        "buffer_seconds": buffer,
        "crossfade_seconds": crossfade,
        "total_narration_duration": round(total_duration, 2),
        "estimated_video_duration": round(video_duration, 2),
        "clips": clips_data,
        "full_narration": "full_narration.mp3",
        "slide_durations": slide_durations,
    }

    timing_path = output_dir / "timing.json"
    with open(timing_path, "w") as f:
        json.dump(timing, f, indent=2)

    logger.info(f"Narration generated: {len(clips_data)} clips, {total_duration:.1f}s total")
    logger.info(f"Estimated video duration: {video_duration:.1f}s")
    logger.info(f"Timing metadata: {timing_path}")

    # Clean up silence files
    for p in output_dir.glob("silence_*.mp3"):
        p.unlink(missing_ok=True)

    return timing


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate TTS narration for ToxShield video slides"
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--content-file", "-c",
        help="Path to content.json from generate_carousel.py",
    )
    input_group.add_argument(
        "--slides-json", "-j",
        help='Direct JSON array of slides: [{"headline":"...","body":["..."]}]',
    )

    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for narration clips (default: <content-dir>/narration/)",
    )
    parser.add_argument(
        "--voice", "-v", default=DEFAULT_VOICE,
        help=f"OpenAI TTS voice (default: {DEFAULT_VOICE}). Options: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"OpenAI TTS model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--instructions", "-i",
        help="Voice style instructions (overrides content-type preset)",
    )
    parser.add_argument(
        "--content-type", "-t",
        choices=list(VOICE_PRESETS.keys()),
        help="Content type for automatic voice preset selection",
    )
    parser.add_argument(
        "--speed", "-s", type=float, default=DEFAULT_SPEED,
        help=f"TTS speed multiplier 0.25-4.0 (default: {DEFAULT_SPEED})",
    )
    parser.add_argument(
        "--buffer", "-b", type=float, default=DEFAULT_BUFFER,
        help=f"Seconds of silence between clips (default: {DEFAULT_BUFFER})",
    )
    parser.add_argument(
        "--crossfade", type=float, default=1.0,
        help="Crossfade duration in generate_reel.py (default: 1.0). "
             "Used to compute slide durations that account for transition overlap.",
    )

    args = parser.parse_args()

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env.local")
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass  # dotenv is optional if env vars are set directly

    # Parse slide text
    if args.content_file:
        content_path = Path(args.content_file)
        if not content_path.exists():
            logger.error(f"Content file not found: {content_path}")
            sys.exit(1)
        with open(content_path) as f:
            content_data = json.load(f)
        slides = extract_slide_texts(content_data)
        default_output = content_path.parent / "narration"
    else:
        slides = parse_slides_json(args.slides_json)
        default_output = PROJECT_ROOT / "output" / "narration"

    output_dir = Path(args.output_dir) if args.output_dir else default_output
    instructions = args.instructions or DEFAULT_INSTRUCTIONS

    # Generate narration
    timing = generate_narration(
        slides=slides,
        output_dir=output_dir,
        voice=args.voice,
        model=args.model,
        instructions=instructions,
        speed=args.speed,
        buffer=args.buffer,
        crossfade=args.crossfade,
        content_type=args.content_type,
    )

    # Machine-readable output
    print(f"\n{json.dumps({
        'narration_dir': str(output_dir),
        'full_narration': str(output_dir / timing['full_narration']),
        'timing_file': str(output_dir / 'timing.json'),
        'total_duration': timing['total_narration_duration'],
        'estimated_video_duration': timing['estimated_video_duration'],
        'clips': len(timing['clips']),
        'slide_durations': timing['slide_durations'],
    })}")


if __name__ == "__main__":
    main()
