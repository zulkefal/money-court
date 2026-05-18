"""Assemble final video with FFmpeg.

Default output is 1080x1920 vertical (Shorts). For 16:9 long-form, pass
width=1920, height=1080 to assemble(). All filter chains, motion presets,
and caption positions scale to the requested dimensions.

Per scene: gentle Ken Burns drift on illustrated comic art + drawtext
captions timed from word-level TTS output. Scenes are then concatenated.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from PIL import ImageFont

from config.settings import (
    CAPTION_FONT,
    FFMPEG_BIN,
    FFPROBE_BIN,
    FINAL_DIR,
    MUSIC_DIR,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)
from pipeline.logger import get_logger

logger = get_logger("assembler")

# 60-sec Shorts caption styling: bold-condensed font, dead-center of the
# frame. The full 3-word cue is rendered in white on a black box for the
# whole cue duration; the word currently being spoken is overlaid in yellow
# (karaoke-style) using the per-word timings from voiceover.py.
CAPTION_FONTSIZE = 66
CAPTION_BASE_COLOR = "white"
CAPTION_HIGHLIGHT_COLOR = "yellow"
CAPTION_HIGHLIGHT_BOX_COLOR = "black@0.7"
CAPTION_HIGHLIGHT_BOX_PADDING = 8

# Background music volume relative to narrator. 0.10 = music at 10% — present
# but stays well under the voice. Tune higher for more prominent music.
MUSIC_VOLUME = 0.10
MUSIC_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".aac"}


def _ffprobe_duration(audio: Path) -> float:
    out = subprocess.check_output(
        [
            FFPROBE_BIN, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio),
        ]
    )
    return float(out.strip())


# Horror Shorts motion: noticeable but not jumpy. Scenes are ~6 sec each,
# so we want ~10-18% zoom over the scene = visible drift but still
# atmospheric. Faster than the original "barely-perceptible" horror presets
# (which were tuned for 30-sec scenes) but slower than money-crew's 30-40%.
# Rates assume 30 fps × 6 sec = 180 frames per scene.
MOTION_PRESETS = [
    # Slow zoom-in, centered. Building dread.
    ("min(zoom+0.0010,1.18)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    # Pull-back from a slight zoom — reveal something we missed
    ("if(eq(on,1),1.18,max(zoom-0.0008,1.0))", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    # Drift left to right at 1.10 zoom
    ("1.10", "(iw-iw/zoom)*on/{D}", "ih/2-(ih/zoom/2)"),
    # Drift right to left
    ("1.10", "(iw-iw/zoom)*(1-on/{D})", "ih/2-(ih/zoom/2)"),
    # Drift downward — gravity, dread
    ("1.10", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*on/{D}"),
    # Slow off-center push toward upper-left
    ("min(zoom+0.0012,1.18)", "(iw-iw/zoom)*0.15", "(ih-ih/zoom)*0.15"),
    # Subtle slow zoom-in (most still preset, for "wrong note" beats)
    ("min(zoom+0.0005,1.08)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
]


def _motion_filter(scene_idx: int, total_frames: int, width: int, height: int) -> str:
    z_expr, x_expr, y_expr = MOTION_PRESETS[(scene_idx - 1) % len(MOTION_PRESETS)]
    x_expr = x_expr.replace("{D}", str(total_frames))
    y_expr = y_expr.replace("{D}", str(total_frames))
    return (
        f"scale=8000:-1,"
        f"zoompan=z='{z_expr}':d={total_frames}:s={width}x{height}:fps={VIDEO_FPS}"
        f":x='{x_expr}':y='{y_expr}'"
    )


def _captions_filter(
    captions_json: Path, width: int, height: int, fontsize: int
) -> str:
    """Build a chain of drawtext filters with karaoke-style per-word highlight.

    For each cue:
      1. Base layer: full cue text in white on a black box, visible for the
         whole cue interval.
      2. Per-word overlay: the word currently being spoken is redrawn in
         yellow, positioned exactly over its white twin, enabled only during
         that word's interval (from voiceover.py's WordBoundary timings).

    Per-word x positions are pre-measured with PIL so the yellow word lands
    pixel-aligned over the white text underneath. text_h is identical for the
    base line and each word (same font/size, all-caps sanitized text → no
    descenders) so y=(h-text_h)/2 lines them up vertically.
    """
    cues = json.loads(captions_json.read_text())
    if not cues:
        return ""

    font = ImageFont.truetype(CAPTION_FONT, fontsize)

    parts: list[str] = []
    for cue in cues:
        line = cue["text"]
        line_w = font.getlength(line)
        line_start_x = f"(w-{line_w:.1f})/2"

        # Base: white line on black box for the whole cue duration.
        enable_cue = f"between(t\\,{cue['start']:.3f}\\,{cue['end']:.3f})"
        parts.append(
            f"drawtext=fontfile={CAPTION_FONT}"
            f":text='{line}'"
            f":fontsize={fontsize}"
            f":fontcolor={CAPTION_BASE_COLOR}"
            f":box=1"
            f":boxcolor={CAPTION_HIGHLIGHT_BOX_COLOR}"
            f":boxborderw={CAPTION_HIGHLIGHT_BOX_PADDING}"
            f":x={line_start_x}"
            f":y=(h-text_h)/2"
            f":enable='{enable_cue}'"
        )

        # Per-word yellow overlay, positioned at each word's offset in the line.
        char_offset = 0
        for w in cue["words"]:
            prefix = line[:char_offset]
            prefix_w = font.getlength(prefix)
            word_x = f"({line_start_x})+{prefix_w:.1f}"
            enable_word = f"between(t\\,{w['start']:.3f}\\,{w['end']:.3f})"
            parts.append(
                f"drawtext=fontfile={CAPTION_FONT}"
                f":text='{w['text']}'"
                f":fontsize={fontsize}"
                f":fontcolor={CAPTION_HIGHLIGHT_COLOR}"
                f":x={word_x}"
                f":y=(h-text_h)/2"
                f":enable='{enable_word}'"
            )
            char_offset += len(w["text"]) + 1  # +1 for the joining space
    return ",".join(parts)


def _build_scene_clip(
    image: Path, audio: Path, captions: Path, out_clip: Path, scene_idx: int,
    width: int, height: int, fontsize: int,
) -> None:
    """Render one scene with motion + drawtext captions."""
    duration = _ffprobe_duration(audio)
    total_frames = max(1, int(round(duration * VIDEO_FPS)))
    work_dir = out_clip.parent
    work_dir.mkdir(parents=True, exist_ok=True)
    motion = _motion_filter(scene_idx, total_frames, width, height)
    caps = _captions_filter(captions, width, height, fontsize)
    vf = motion + ("," + caps if caps else "")
    cmd = [
        FFMPEG_BIN, "-y", "-loglevel", "error",
        "-loop", "1", "-i", str(image.resolve()),
        "-i", str(audio.resolve()),
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-b:v", "6M", "-maxrate", "8M", "-bufsize", "16M",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_clip.resolve()),
    ]
    logger.info(f"render scene {scene_idx}: {out_clip.name} ({duration:.2f}s, {len(json.loads(captions.read_text()))} cues)")
    subprocess.run(cmd, check=True)


def _concat_clips(clips: list[Path], out_file: Path) -> None:
    list_file = out_file.with_suffix(".txt")
    list_file.write_text("\n".join(f"file '{c.resolve()}'" for c in clips))
    cmd = [
        FFMPEG_BIN, "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(out_file),
    ]
    logger.info(f"concat -> {out_file}")
    subprocess.run(cmd, check=True)
    list_file.unlink(missing_ok=True)


def _pick_music(video_id: str) -> Path | None:
    """Choose a music track from assets/music/ deterministically per video_id.

    Same video_id -> same track (so re-runs are stable). Returns None if the
    music dir is missing or has no audio files — pipeline runs music-free.
    """
    if not MUSIC_DIR.exists():
        return None
    tracks = sorted(
        f for f in MUSIC_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in MUSIC_EXTENSIONS
    )
    if not tracks:
        return None
    h = int(hashlib.sha256(video_id.encode()).hexdigest(), 16)
    return tracks[h % len(tracks)]


def _mix_music(video_path: Path, music_path: Path, out_path: Path) -> None:
    """Re-mux the video with looped background music at MUSIC_VOLUME below the narrator."""
    cmd = [
        FFMPEG_BIN, "-y", "-loglevel", "error",
        "-i", str(video_path),
        "-stream_loop", "-1", "-i", str(music_path),
        "-filter_complex",
        f"[1:a]volume={MUSIC_VOLUME}[bg];"
        f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_path),
    ]
    logger.info(f"music: {music_path.name} (vol {MUSIC_VOLUME}) -> {out_path.name}")
    subprocess.run(cmd, check=True)


def assemble(
    video_id: str,
    images: list[Path],
    audio_clips: list[Path],
    caption_clips: list[Path],
    width: int | None = None,
    height: int | None = None,
    fontsize: int | None = None,
) -> Path:
    """Assemble the per-scene clips into the final mp4.

    width/height default to the Shorts dimensions (1080x1920). For 16:9
    long-form, pass width=1920, height=1080. fontsize defaults to 80px which
    works well for both — pass a smaller value if long-form captions feel
    overweight.
    """
    if not (len(images) == len(audio_clips) == len(caption_clips)):
        raise ValueError(
            f"count mismatch: {len(images)} imgs, {len(audio_clips)} audio, {len(caption_clips)} caps"
        )
    # shutil.which handles both absolute paths (Mac dev: /usr/local/opt/ffmpeg-full/bin/ffmpeg)
    # and bare names on PATH (CI: just "ffmpeg" after apt install).
    if shutil.which(FFMPEG_BIN) is None or shutil.which(FFPROBE_BIN) is None:
        raise RuntimeError(
            f"ffmpeg/ffprobe missing: {FFMPEG_BIN}, {FFPROBE_BIN}"
        )
    target_w = width or VIDEO_WIDTH
    target_h = height or VIDEO_HEIGHT
    target_fontsize = fontsize or CAPTION_FONTSIZE
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    final = FINAL_DIR / f"{video_id}.mp4"
    if final.exists():
        logger.info(f"final cached: {final}")
        return final
    work = FINAL_DIR / video_id
    work.mkdir(parents=True, exist_ok=True)
    scene_clips: list[Path] = []
    for i, (img, aud, cap) in enumerate(zip(images, audio_clips, caption_clips), start=1):
        out = work / f"scene_{i:02d}.mp4"
        if out.exists():
            logger.info(f"scene {i:02d}: cached")
        else:
            _build_scene_clip(
                img, aud, cap, out, scene_idx=i,
                width=target_w, height=target_h, fontsize=target_fontsize,
            )
        scene_clips.append(out)

    music = _pick_music(video_id)
    if music is None:
        _concat_clips(scene_clips, final)
        return final
    # Concat to a tmp file first, then mux music in a second pass
    tmp = work / "_concat_no_music.mp4"
    _concat_clips(scene_clips, tmp)
    _mix_music(tmp, music, final)
    tmp.unlink(missing_ok=True)
    return final


