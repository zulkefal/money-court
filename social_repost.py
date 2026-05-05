"""Re-render an archived script and cross-post to Facebook + Instagram only.

Use this when you want to backfill social platforms with content that's already
been published to YouTube — for example, walking back through scripts/archive/
and pushing each one to FB/IG without re-uploading to YouTube.

The render step is cached by video_id: if outputs/final/<video_id>.mp4 already
exists, it's reused. Same for per-scene images and voiceovers. So re-running on
an already-rendered archive script is fast — it goes straight to upload.

Usage:
    ./venv/bin/python social_repost.py scripts/archive/verdict-dan-vs-zoe-credit-card-debt.json
    ./venv/bin/python social_repost.py scripts/archive/some-script.json --fb-only
    ./venv/bin/python social_repost.py scripts/archive/some-script.json --ig-only
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from config.settings import (
    FB_PAGE_ACCESS_TOKEN,
    FB_PAGE_ID,
    IG_USER_ID,
)
from pipeline import assembler, image_generator, voiceover
from pipeline import metadata as meta_mod
from pipeline.logger import get_logger

logger = get_logger("social_repost")


def _render(script_path: Path) -> tuple[Path, dict]:
    """Run the standard 3-step render pipeline and return (final_mp4, script)."""
    script = json.loads(script_path.read_text())
    video_id = script["video_id"]
    character = script["character"]
    scenes = script["scenes"]
    voice = script.get("voice") or voiceover.CHARACTER_VOICES[character]

    logger.info(f"=== Rendering {video_id} ({len(scenes)} scenes) ===")

    logger.info("Step 1: scene images")
    images = image_generator.generate_for_video(video_id, scenes)

    logger.info("Step 2: narration + captions")
    audio, caps = voiceover.generate_for_video(video_id, scenes, voice=voice)

    logger.info("Step 3: assemble final mp4")
    final = assembler.assemble(video_id, images, audio, caps)

    logger.info(f"=== Render done: {final} ===")
    return final, script


def main(script_path: Path, do_fb: bool, do_ig: bool) -> None:
    if not script_path.exists():
        raise SystemExit(f"script not found: {script_path}")

    final, script = _render(script_path)
    meta = meta_mod.metadata_for(script)
    logger.info(f"  title: {meta['title']}")

    posted_any = False

    if do_fb:
        if not (FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN):
            logger.error("FB skipped: FB_PAGE_ID / FB_PAGE_ACCESS_TOKEN not set in .env")
        else:
            from pipeline import facebook_uploader
            logger.info("Uploading to Facebook Reels")
            try:
                fb_url = facebook_uploader.upload(
                    video_path=final,
                    title=meta["title"],
                    description=meta["description"],
                )
                print(f"Facebook URL: {fb_url}")
                posted_any = True
            except Exception as e:
                logger.error(f"Facebook upload failed: {e}")

    if do_ig:
        if not (IG_USER_ID and FB_PAGE_ACCESS_TOKEN):
            logger.error("IG skipped: IG_USER_ID / FB_PAGE_ACCESS_TOKEN not set in .env")
        else:
            from pipeline import instagram_uploader
            logger.info("Uploading to Instagram Reels")
            try:
                ig_url = instagram_uploader.upload(
                    video_path=final,
                    title=meta["title"],
                    description=meta["description"],
                )
                print(f"Instagram URL: {ig_url}")
                posted_any = True
            except Exception as e:
                logger.error(f"Instagram upload failed: {e}")

    if not posted_any:
        raise SystemExit("nothing was posted — check creds in .env")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="Path to a script JSON (typically in scripts/archive/).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fb-only", action="store_true", help="Skip Instagram, post to Facebook only.")
    group.add_argument("--ig-only", action="store_true", help="Skip Facebook, post to Instagram only.")
    args = parser.parse_args()

    main(
        script_path=args.script,
        do_fb=not args.ig_only,
        do_ig=not args.fb_only,
    )
