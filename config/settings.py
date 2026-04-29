"""Central config for The Money Crew pipeline. All paths and constants live here."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# YouTube Data API v3 — see uploader.py for the OAuth flow.
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "outputs")).resolve()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

ASSETS_DIR = PROJECT_ROOT / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

SCRIPTS_DIR = OUTPUT_DIR / "scripts"
IMAGES_DIR = OUTPUT_DIR / "images"
VOICEOVERS_DIR = OUTPUT_DIR / "voiceovers"
FINAL_DIR = OUTPUT_DIR / "final"
STATS_DIR = OUTPUT_DIR / "stats"

LOGS_DIR = PROJECT_ROOT / "logs"

CLAUDE_MODEL = "claude-sonnet-4-6"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
SCENES_PER_VIDEO = 10
SCENE_DURATION_SECONDS = 5

# Need a full ffmpeg with libfreetype for drawtext/captions.
# On this Mac, ffmpeg-full is keg-only at /usr/local/opt/ffmpeg-full/bin.
# On VPS this should be `ffmpeg`/`ffprobe` once a full build is installed there.
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "/usr/local/opt/ffmpeg-full/bin/ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "/usr/local/opt/ffmpeg-full/bin/ffprobe")

# Caption font path. Overridable via env so CI/Linux can swap Impact (Mac-only,
# proprietary) for Liberation Sans Bold (apt: fonts-liberation) or DejaVu.
CAPTION_FONT = os.getenv(
    "CAPTION_FONT",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
)
