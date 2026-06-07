"""Generate scene images via Pollinations.ai (free, key-less Flux backend).

Default output is 1080x1920 vertical (Shorts). For long-form 16:9 horizontal,
pass width=1920, height=1080 to generate_for_video().

Pollinations is a free public proxy in front of Flux Schnell. Same quality
profile as paid Replicate Flux Schnell, just queued and rate-limited.
"""
from __future__ import annotations

import time
import urllib.parse
from pathlib import Path
from typing import Iterable

import requests
from PIL import Image, ImageFilter

from config.settings import (
    IMAGES_DIR,
    POLLINATIONS_API_KEY,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)
from pipeline.logger import get_logger

logger = get_logger("image_generator")

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
# Style suffix is orientation-neutral. Per-scene image_prompt provides the
# composition cue ("vertical comic panel composition" for Shorts,
# "horizontal widescreen comic panel composition" for long-form).
STYLE_SUFFIX = (
    ", kids graphic novel illustration, bold flat colors, clean black ink outlines, "
    "expressive comic book characters, friendly storybook art, vibrant, "
    "page from a children's comic book"
)
NEGATIVE_HINT = (
    " (avoid: 3D render, photorealistic, dark, scary, manga screentone, anime, "
    "ugly, blurry, watermark, speech bubble)"
)


def _build_url(prompt: str, seed: int, width: int, height: int) -> str:
    full_prompt = prompt + STYLE_SUFFIX + NEGATIVE_HINT
    encoded = urllib.parse.quote(full_prompt, safe="")
    params = {
        "width": str(width),
        "height": str(height),
        "seed": str(seed),
        "model": "flux",
        "nologo": "true",
        "enhance": "true",
        # private=true keeps generations out of the public Pollinations feed.
        # This is a paid feature — it requires the API key sent in _headers().
        "private": "true",
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{POLLINATIONS_BASE}/{encoded}?{qs}"


def _headers() -> dict[str, str]:
    """Auth header for Pollinations. The anonymous tier now returns 402 Payment
    Required, so requests must carry the API key as a Bearer token. Sent via a
    header (not a query param) so the key never lands in logged URLs."""
    if POLLINATIONS_API_KEY:
        return {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}
    return {}


def _upscale_to_target(path: Path, width: int, height: int) -> None:
    """Pollinations silently downscales to its free-tier cap (~576px on the
    short side) even when we ask for full HD. Upscale in place with Pillow
    LANCZOS + UnsharpMask so the cached PNG matches target resolution and
    stays sharp."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        if im.size == (width, height):
            return
        im = im.resize((width, height), Image.Resampling.LANCZOS)
        # Compensate for upscale softness — moderate sharpen, not aggressive
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=110, threshold=3))
        im.save(path, format="PNG", optimize=True)


def generate_scene_image(prompt: str, seed: int, dest: Path, width: int, height: int) -> Path:
    """Hit Pollinations, save the PNG, then upscale to target resolution."""
    url = _build_url(prompt, seed, width, height)
    logger.info(f"pollinations: seed={seed} prompt={prompt[:90]}...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=_headers(), stream=True, timeout=180) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    _upscale_to_target(dest, width, height)
    return dest


def generate_for_video(
    video_id: str,
    scenes: Iterable[dict],
    seed: int = 42,
    width: int | None = None,
    height: int | None = None,
) -> list[Path]:
    """Generate one image per scene; return ordered list of saved paths.

    width/height default to the Shorts dimensions (1080x1920). Pass 1920x1080
    for 16:9 long-form. Aspect framing is also influenced by the per-scene
    image_prompt (include "horizontal widescreen comic panel composition" for
    long-form scenes so Pollinations frames characters correctly).
    """
    target_w = width or VIDEO_WIDTH
    target_h = height or VIDEO_HEIGHT
    out_dir = IMAGES_DIR / video_id
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for scene in scenes:
        idx = scene["id"]
        dest = out_dir / f"scene_{idx:02d}.png"
        if dest.exists() and dest.stat().st_size > 0:
            logger.info(f"scene {idx}: cached at {dest}")
            paths.append(dest)
            continue
        attempts = 0
        while True:
            attempts += 1
            try:
                generate_scene_image(
                    scene["image_prompt"], seed=seed + idx, dest=dest,
                    width=target_w, height=target_h,
                )
                if dest.stat().st_size < 5_000:
                    raise RuntimeError(f"image too small: {dest.stat().st_size} bytes")
                logger.info(f"scene {idx}: saved ({dest.stat().st_size:,} bytes)")
                paths.append(dest)
                break
            except Exception as e:
                logger.warning(f"scene {idx} attempt {attempts} failed: {e}")
                dest.unlink(missing_ok=True)
                if attempts >= 6:
                    raise
                # Pollinations is aggressive on parallel callers; back off long.
                time.sleep(min(15 * attempts, 60))
    return paths
