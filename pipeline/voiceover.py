"""Generate per-scene narration mp3 + word-timed captions JSON via edge-tts.

Each scene gets:
  outputs/voiceovers/<video_id>/scene_NN.mp3
  outputs/voiceovers/<video_id>/scene_NN.captions.json
    -> [{"start": 0.0, "end": 1.5, "text": "COURT IS IN SESSION"}, ...]
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Iterable

import edge_tts

from config.settings import VOICEOVERS_DIR
from pipeline.logger import get_logger

logger = get_logger("voiceover")

CHARACTER_VOICES = {
    "judge_vera":     "en-US-AriaNeural",     # confident, authoritative adult female — judge tone
    "detective_cash": "en-US-RogerNeural",    # mature, serious male — noir detective (Davis was retired by MS)
    "coach_vault":    "en-US-GuyNeural",      # energetic upbeat male — fitness coach
    "doctor_dollar":  "en-US-EmmaNeural",     # warm reassuring female — doctor tone
}

WORDS_PER_CAPTION = 3  # short caption groups so they're readable in Shorts


_DRAWTEXT_SAFE = re.compile(r"[^A-Z0-9 \!\?]")


def _sanitize_caption(text: str) -> str:
    """Strip everything but uppercase letters, digits, spaces, ! and ? for safe drawtext."""
    return _DRAWTEXT_SAFE.sub("", text.upper()).strip()


def _build_captions(
    boundaries: list[dict], group_size: int = WORDS_PER_CAPTION
) -> list[dict]:
    """Group word boundaries into N-word captions; return list of timed cues."""
    cues: list[dict] = []
    for start in range(0, len(boundaries), group_size):
        group = boundaries[start : start + group_size]
        if not group:
            continue
        first = group[0]
        last = group[-1]
        start_s = first["offset"] / 10_000_000
        end_s = (last["offset"] + last["duration"]) / 10_000_000
        text = _sanitize_caption(" ".join(b["text"] for b in group))
        if text:
            cues.append({"start": round(start_s, 3), "end": round(end_s, 3), "text": text})
    return cues


async def _generate_async(
    text: str, voice: str, mp3_dest: Path, captions_dest: Path
) -> None:
    mp3_dest.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(
        text, voice=voice, rate="+12%", boundary="WordBoundary"
    )
    boundaries: list[dict] = []
    with mp3_dest.open("wb") as f:
        async for chunk in communicate.stream():
            t = chunk.get("type")
            if t == "audio":
                f.write(chunk["data"])
            elif t == "WordBoundary":
                boundaries.append(
                    {
                        "offset": chunk["offset"],
                        "duration": chunk["duration"],
                        "text": chunk["text"],
                    }
                )
    cues = _build_captions(boundaries)
    captions_dest.write_text(json.dumps(cues, indent=2))


def generate_clip(
    text: str, voice: str, mp3_dest: Path, captions_dest: Path
) -> None:
    asyncio.run(_generate_async(text, voice, mp3_dest, captions_dest))


def _resolve_scene_voice(scene: dict, default_voice: str) -> str:
    """Per-scene voice override: scene["voice"] can be a CHARACTER_VOICES key
    (e.g. "judge_vera") or a raw edge-tts voice id (e.g. "en-US-AriaNeural")."""
    override = scene.get("voice")
    if not override:
        return default_voice
    return CHARACTER_VOICES.get(override, override)


def generate_for_video(
    video_id: str, scenes: Iterable[dict], voice: str
) -> tuple[list[Path], list[Path]]:
    """Return (mp3_paths, captions_json_paths) parallel to scenes order.

    Each scene may include a "voice" key to override the host's voice for
    that scene only — used by long-form scripts that switch narrators.
    """
    out_dir = VOICEOVERS_DIR / video_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3s: list[Path] = []
    caps: list[Path] = []
    for scene in scenes:
        idx = scene["id"]
        scene_voice = _resolve_scene_voice(scene, voice)
        mp3 = out_dir / f"scene_{idx:02d}.mp3"
        cap = out_dir / f"scene_{idx:02d}.captions.json"
        if mp3.exists() and cap.exists() and mp3.stat().st_size > 0:
            logger.info(f"scene {idx} voice: cached")
            mp3s.append(mp3)
            caps.append(cap)
            continue
        attempts = 0
        while True:
            attempts += 1
            try:
                logger.info(
                    f"edge-tts: voice={scene_voice} scene={idx} text={scene['narration'][:80]!r}"
                )
                generate_clip(scene["narration"], scene_voice, mp3, cap)
                if mp3.stat().st_size < 1_000:
                    raise RuntimeError(f"audio too small: {mp3.stat().st_size}")
                logger.info(
                    f"scene {idx} voice + captions saved ({mp3.stat().st_size:,} bytes)"
                )
                mp3s.append(mp3)
                caps.append(cap)
                break
            except Exception as e:
                logger.warning(f"scene {idx} attempt {attempts} failed: {e}")
                mp3.unlink(missing_ok=True)
                cap.unlink(missing_ok=True)
                if attempts >= 3:
                    raise
                time.sleep(3)
    return mp3s, caps
