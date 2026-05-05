"""Upload a finished video to an Instagram Business account as a Reel.

Auth model: reuses the same Page Access Token as pipeline/facebook_uploader.py
(FB Login for Business path). The IG account must be a Business/Creator account
linked to the FB Page identified by FB_PAGE_ID.

Required app permissions: instagram_basic, instagram_content_publish,
pages_read_engagement.

Graph API 4-step Reels upload (resumable / binary):
  1. POST /{ig_user_id}/media  upload_type=resumable, media_type=REELS, caption
       -> { "id": "<container_id>" }
  2. POST rupload.facebook.com/ig-api-upload/{api_version}/{container_id}
       (raw mp4 bytes; Authorization: OAuth header) -> { "success": true }
  3. Poll  GET /{container_id}?fields=status_code  until "FINISHED"
       (max ~5 min, once per minute per Meta's recommendation)
  4. POST /{ig_user_id}/media_publish  creation_id=<container_id>
       -> { "id": "<media_id>" }

Usage:
    from pipeline import instagram_uploader
    url = instagram_uploader.upload(
        video_path=Path("outputs/final/verdict-xyz.mp4"),
        title="...",
        description="...",
    )
"""
from __future__ import annotations

import time
from pathlib import Path

import requests

from config.settings import FB_PAGE_ACCESS_TOKEN, IG_USER_ID
from pipeline.logger import get_logger

logger = get_logger("instagram_uploader")

GRAPH_API_VERSION = "v19.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
RUPLOAD_BASE = f"https://rupload.facebook.com/ig-api-upload/{GRAPH_API_VERSION}"

# IG caption hard limit is 2200 chars including hashtags. Leave headroom.
CAPTION_MAX = 2200

# Container processing can take a while for longer videos. Poll once per ~10s
# up to ~5 min total — Meta's docs recommend "once per minute for no more than
# 5 minutes" but Reels under 90s usually finish in 30-60s.
STATUS_POLL_INTERVAL = 10
STATUS_POLL_TIMEOUT = 300


def _check_config() -> None:
    missing = [
        name for name, val in (
            ("IG_USER_ID", IG_USER_ID),
            ("FB_PAGE_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN),
        )
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"missing in .env: {', '.join(missing)} — "
            "set IG_USER_ID and FB_PAGE_ACCESS_TOKEN to enable Instagram Reels upload."
        )


def _build_caption(title: str, description: str) -> str:
    """Combine title + description into a single IG caption, capped at CAPTION_MAX."""
    caption = title.strip()
    desc = description.strip()
    if desc:
        caption = f"{caption}\n\n{desc}"
    return caption[:CAPTION_MAX]


def _create_container(caption: str) -> str:
    """Phase 1: create a resumable upload container for a Reel. Returns container_id."""
    resp = requests.post(
        f"{GRAPH_BASE}/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["id"]


def _transfer_video(container_id: str, video_path: Path) -> None:
    """Phase 2: stream the mp4 binary to rupload.facebook.com."""
    file_size = video_path.stat().st_size
    with video_path.open("rb") as fh:
        resp = requests.post(
            f"{RUPLOAD_BASE}/{container_id}",
            headers={
                "Authorization": f"OAuth {FB_PAGE_ACCESS_TOKEN}",
                "offset": "0",
                "file_size": str(file_size),
            },
            data=fh,
            timeout=600,
        )
    resp.raise_for_status()
    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"IG video transfer failed: {result}")


def _wait_finished(container_id: str) -> None:
    """Phase 3: poll the container status until FINISHED (or fail)."""
    deadline = time.time() + STATUS_POLL_TIMEOUT
    while time.time() < deadline:
        resp = requests.get(
            f"{GRAPH_BASE}/{container_id}",
            params={"fields": "status_code", "access_token": FB_PAGE_ACCESS_TOKEN},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        logger.info(f"  ig container status: {status}")
        if status == "FINISHED":
            return
        if status in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"IG container {container_id} ended in status {status}")
        time.sleep(STATUS_POLL_INTERVAL)
    raise RuntimeError(
        f"IG container {container_id} did not reach FINISHED within {STATUS_POLL_TIMEOUT}s"
    )


def _publish(container_id: str) -> str:
    """Phase 4: publish the container; returns the published media_id."""
    resp = requests.post(
        f"{GRAPH_BASE}/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": FB_PAGE_ACCESS_TOKEN},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    media_id = data.get("id")
    if not media_id:
        raise RuntimeError(f"IG publish missing media id: {data}")
    return media_id


def upload(video_path: Path, title: str, description: str) -> str:
    """Upload `video_path` as an Instagram Reel; return the IG media URL.

    Non-fatal caller pattern: wrap in try/except so an IG failure doesn't
    block YouTube archival or FB upload in make_video.py.
    """
    _check_config()
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    file_size = video_path.stat().st_size
    logger.info(f"ig upload start: {video_path.name} ({file_size:,} bytes)")

    caption = _build_caption(title, description)
    container_id = _create_container(caption)
    logger.info(f"  ig container: {container_id}")

    _transfer_video(container_id, video_path)
    logger.info(f"  ig transfer: complete")

    _wait_finished(container_id)

    media_id = _publish(container_id)
    url = f"https://www.instagram.com/reel/{media_id}/"
    logger.info(f"ig upload OK: {url}")
    return url
