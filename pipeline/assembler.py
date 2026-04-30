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

CAPTION_FONTSIZE = 60
# Caption Y as a fraction of frame height (~24% from bottom). Works for both
# 9:16 (h=1920 -> 460px from bottom, above mobile UI overlap) and 16:9
# (h=1080 -> 259px from bottom, comfortably below the action).
CAPTION_Y_FRACTION_FROM_BOTTOM = 0.24
CAPTION_FONTCOLOR = "white"
CAPTION_BORDERCOLOR = "black"
CAPTION_BORDERW = 6
# Karaoke highlight: yellow box behind the currently-spoken word.
CAPTION_HIGHLIGHT_COLOR = "yellow"
CAPTION_HIGHLIGHT_PADDING = 8  # boxborderw, in px — small visual padding around the word

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


# Each scene gets a different motion preset so the video doesn't feel static.
MOTION_PRESETS = [
    ("min(zoom+0.0025,1.5)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("if(eq(on,1),1.5,max(zoom-0.0020,1.05))", "(iw-iw/zoom)*on/{D}", "ih/2-(ih/zoom/2)"),
    ("min(zoom+0.0022,1.45)", "(iw-iw/zoom)*0.2", "(ih-ih/zoom)*0.15"),
    ("min(zoom+0.0018,1.4)", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*0.25"),
    ("min(zoom+0.0010,1.2)", "(iw-iw/zoom)*on/{D}", "ih/2-(ih/zoom/2)"),
    ("min(zoom+0.0030,1.6)", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*0.35"),
    ("if(eq(on,1),1.5,max(zoom-0.0018,1.0))", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
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


def _measure_word_widths(font_path: Path, fontsize: int, words: list[str]) -> tuple[list[int], int]:
    """Return (per-word pixel widths, space width) using Pillow + freetype.

    Pillow and FFmpeg drawtext both rasterize via freetype, so the measurements
    line up closely enough that per-word X positions look natural inside the
    centered phrase. Sub-pixel drift is invisible at video scale.
    """
    from PIL import ImageFont

    font = ImageFont.truetype(str(font_path), fontsize)
    widths: list[int] = []
    for w in words:
        bbox = font.getbbox(w)
        widths.append(int(round(bbox[2] - bbox[0])))
    space_bbox = font.getbbox(" ")
    space_w = int(round(space_bbox[2] - space_bbox[0]))
    return widths, space_w


def _captions_filter(captions_json: Path, height: int, fontsize: int) -> str:
    """Build a drawtext chain that renders captions with a karaoke yellow highlight.

    Per cue we emit two drawtext layers per word:
      1. base   — white text + black border, visible for the whole cue
      2. accent — same text on a yellow `box=1` background, visible only during
                  that word's WordBoundary window

    Words are positioned individually using freetype-measured widths so the trio
    stays centered as a phrase. Falls back to the legacy single-phrase render if
    a cue lacks per-word timings (older cached captions JSON).
    """
    cues = json.loads(captions_json.read_text())
    if not cues:
        return ""
    caption_y = f"h-{int(height * CAPTION_Y_FRACTION_FROM_BOTTOM)}"
    parts: list[str] = []
    for c in cues:
        words = c.get("words")
        if not words:
            enable = f"between(t\\,{c['start']:.3f}\\,{c['end']:.3f})"
            parts.append(
                f"drawtext=fontfile={CAPTION_FONT}"
                f":text='{c['text']}'"
                f":fontsize={fontsize}"
                f":fontcolor={CAPTION_FONTCOLOR}"
                f":bordercolor={CAPTION_BORDERCOLOR}"
                f":borderw={CAPTION_BORDERW}"
                f":x=(w-text_w)/2"
                f":y={caption_y}"
                f":enable='{enable}'"
            )
            continue

        word_texts = [w["text"] for w in words]
        widths, space_w = _measure_word_widths(CAPTION_FONT, fontsize, word_texts)
        phrase_w = sum(widths) + space_w * (len(words) - 1)
        cue_enable = f"between(t\\,{c['start']:.3f}\\,{c['end']:.3f})"

        cur_x = 0
        for i, w in enumerate(words):
            x_expr = f"(w-{phrase_w})/2+{cur_x}"
            word_enable = f"between(t\\,{w['start']:.3f}\\,{w['end']:.3f})"
            # Base white-on-black-border layer for the full cue duration.
            parts.append(
                f"drawtext=fontfile={CAPTION_FONT}"
                f":text='{w['text']}'"
                f":fontsize={fontsize}"
                f":fontcolor={CAPTION_FONTCOLOR}"
                f":bordercolor={CAPTION_BORDERCOLOR}"
                f":borderw={CAPTION_BORDERW}"
                f":x={x_expr}"
                f":y={caption_y}"
                f":enable='{cue_enable}'"
            )
            # Yellow-box accent during this word's WordBoundary window.
            parts.append(
                f"drawtext=fontfile={CAPTION_FONT}"
                f":text='{w['text']}'"
                f":fontsize={fontsize}"
                f":fontcolor={CAPTION_FONTCOLOR}"
                f":bordercolor={CAPTION_BORDERCOLOR}"
                f":borderw={CAPTION_BORDERW}"
                f":box=1"
                f":boxcolor={CAPTION_HIGHLIGHT_COLOR}"
                f":boxborderw={CAPTION_HIGHLIGHT_PADDING}"
                f":x={x_expr}"
                f":y={caption_y}"
                f":enable='{word_enable}'"
            )
            cur_x += widths[i] + space_w
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
    caps = _captions_filter(captions, height, fontsize)
    vf = motion + ("," + caps if caps else "")
    cmd = [
        FFMPEG_BIN, "-y", "-loglevel", "error",
        "-loop", "1", "-i", str(image.resolve()),
        "-i", str(audio.resolve()),
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
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
    work = FINAL_DIR / video_id
    work.mkdir(parents=True, exist_ok=True)
    scene_clips: list[Path] = []
    for i, (img, aud, cap) in enumerate(zip(images, audio_clips, caption_clips), start=1):
        out = work / f"scene_{i:02d}.mp4"
        _build_scene_clip(
            img, aud, cap, out, scene_idx=i,
            width=target_w, height=target_h, fontsize=target_fontsize,
        )
        scene_clips.append(out)
    final = FINAL_DIR / f"{video_id}.mp4"

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


