# CLAUDE.md — Money Court YouTube Automation

## Project Overview

Fully automated YouTube Shorts pipeline for a finance channel built around four professional mascots in the same comic-book universe — Judge Vera, Detective Cash, Coach Vault, and Doctor Dollar — each running a distinct narrative format.

- **Channel niche:** Finance & Money — multi-format pro universe
- **Style:** **Kids comic-book / graphic novel illustration** (story-driven comparison narratives)
- **Audience:** Adults (and older kids) interested in debt, scams, savings discipline, and financial health
- **Format:** YouTube Shorts (vertical 9:16, ~45–75 sec)
- **Posting schedule:** Daily, automated via cron — rotates through the four mascots
- **Cost:** ~$0/video — fully free pipeline (Pollinations + edge-tts)

> Repo directory is still named `money-crew/` (legacy). The channel/brand is **Money Court**.

---

## The Cast — Four Mascots

Four permanent mascots. Always use these consistently. Never invent new characters without explicit instruction.

| Character | Niche | Format opener | Format closer | Voice (edge-tts) |
|-----------|-------|---------------|---------------|-------------------|
| **Judge Vera** | Debt, contracts, lawsuits, financial law | "Court is in session!" | "Court dismissed!" | `en-US-AriaNeural` |
| **Detective Cash** | Scams, fraud, phishing, identity theft, romance scams, crypto rugpulls | "Case file 0042. Time of incident…" | "Case closed." | `en-US-RogerNeural` |
| **Coach Vault** | Savings discipline, emergency fund, debt-payoff workout, spending diet | "Today's training session begins now!" | "Drop and give me twenty bucks!" | `en-US-GuyNeural` |
| **Doctor Dollar** | Credit score, debt-to-income, net worth audit, retirement readiness | "Today's patient checkup starts here." | "See you next visit. Stay financially healthy!" | `en-US-EmmaNeural` |

**Canonical looks** (always include in the host's scene 1 + scene 7 image prompts):

- **Judge Vera** — `cartoon woman named judge vera, silver hair in a neat bun, sharp dark eyes, black judge robes with a gold gavel badge, holding wooden gavel`
- **Detective Cash** — `cartoon man named detective cash, sharp blue eyes, gray fedora hat, beige trench coat, five o'clock shadow, holding magnifying glass and a manila file folder labeled with dollar signs`
- **Coach Vault** — `cartoon man named coach vault, athletic build, buzzcut brown hair, red track jacket with gold dollar sign logo, silver whistle, clipboard covered in dollar sign stickers, fingerless training gloves, sweatband`
- **Doctor Dollar** — `cartoon woman named doctor dollar, dark curly hair, round gold-rim glasses, kind smile, white doctor coat over teal scrubs, golden stethoscope shaped like a dollar sign, holding a clipboard with a credit-score chart`

Per-scene background should match the host's universe (courtroom / noir office / gym / doctor's office). Character prompt details live in [config/characters.py](config/characters.py).

---

## Tech Stack (what we actually use)

| Component | Tool | Why |
|-----------|------|-----|
| Image generation | **Pollinations.ai** (free Flux Schnell wrapper) | Free, no key, decent quality |
| Image upscaling | **Pillow LANCZOS + UnsharpMask** | Pollinations silently downscales to 576×1024; we upscale to 1080×1920 in `image_generator.py` |
| Voiceover | **edge-tts** (Microsoft Edge online TTS) | Free, no key, word-level timing for captions |
| Captions | **FFmpeg drawtext** (Impact, white on black outline) | Native to FFmpeg, no libass needed |
| Video assembly | **FFmpeg full** (`/usr/local/opt/ffmpeg-full/bin/ffmpeg`) | Needs libfreetype for drawtext; Homebrew `ffmpeg-full` formula |
| Motion | **FFmpeg zoompan** (Ken Burns) | Built-in; 7 motion presets cycle per scene |
| Upload | **YouTube Data API v3** (google-api-python-client) | Free within 10k units/day quota |
| Language | **Python 3.11** in venv | |
| Schedule | macOS cron (later: Linux cron on VPS) | |

**Models / services we evaluated and dropped:**
- ComfyUI / ToonYou / fal.ai / VoxCPM (original spec) — replaced by simpler API-based stack for VPS portability
- SadTalker / AniPortrait / MuseTalk lipsync — uncanny output on cartoon characters; user dropped lipsync entirely (don't suggest reviving)
- Rhubarb 2D mouth overlays — built but rejected
- Replicate paid image gen — available as upgrade if Pollinations quality insufficient (~$0.10/batch)

---

## Project Structure

```
money-crew/
├── CLAUDE.md
├── .env                         # API keys (gitignored)
├── .env.example
├── .gitignore
├── requirements.txt
├── make_video.py                # entry point: ./venv/bin/python make_video.py scripts/<X>.json
│
├── config/
│   ├── settings.py              # paths, ffmpeg bin path, video dims
│   ├── characters.py            # Judge Vera definition (prompt, voice, palette)
│   └── topics.py                # finance topic bank with 30-day cooldown
│
├── pipeline/
│   ├── logger.py                # rotating-file logger
│   ├── image_generator.py       # Pollinations -> 576x1024 -> upscale to 1080x1920
│   ├── voiceover.py             # edge-tts -> mp3 + word-timed captions JSON
│   ├── assembler.py             # FFmpeg ken burns + drawtext captions + concat
│   ├── metadata.py              # title/description/tag generation
│   ├── script_generator.py      # Claude API -> script JSON (optional)
│   ├── stats.py                 # YouTube performance digest
│   └── uploader.py              # YouTube Data API v3 upload
│
├── scripts/                     # Hand-written video scripts (JSON)
│   └── verdict_dan_vs_zoe_credit_card_debt.json
│
├── assets/
│   └── music/                   # background music (YouTube Audio Library)
│
├── outputs/
│   ├── images/<video_id>/scene_NN.png
│   ├── voiceovers/<video_id>/scene_NN.mp3 + scene_NN.captions.json
│   └── final/<video_id>.mp4
│
├── logs/
│   └── pipeline.log
│
└── venv/                        # Python 3.11 virtualenv
```

---

## Pipeline Flow

```
make_video.py <script.json>
  │
  ├── 1. image_generator.generate_for_video()
  │      • For each scene: Pollinations.ai HTTP GET with prompt + style suffix
  │      • Pollinations returns 576×1024 PNG (capped on free tier)
  │      • Pillow LANCZOS upscale to 1080×1920 + UnsharpMask sharpen
  │      • Cache: outputs/images/<video_id>/scene_NN.png
  │
  ├── 2. voiceover.generate_for_video()
  │      • For each scene: edge-tts with Judge Vera's voice + WordBoundary
  │      • Outputs mp3 + JSON of word-timed caption groups
  │      • Cache: outputs/voiceovers/<video_id>/scene_NN.{mp3,captions.json}
  │
  └── 3. assembler.assemble()
         • Per scene: FFmpeg loop image, apply zoompan (Ken Burns), overlay
           drawtext captions timed to caption JSON, mux with mp3
         • One of 7 motion presets cycles per scene index
         • Concat all scenes, output 1080x1920 H.264 + AAC
         • Cache: outputs/final/<video_id>.mp4
```

All steps cache by file existence — re-runs only do new work.

---

## Script Format

Hand-written JSON (eventual: Claude API generates these). Schema:

```json
{
  "video_id": "verdict-dan-vs-zoe-credit-card-debt-001",
  "character": "judge_vera",
  "topic": "Ignoring credit card debt letters vs responding to them (Dan vs Zoe)",
  "scenes": [
    {
      "id": 1,
      "narration": "I'm Judge Vera, and today's case is one I see every single day... Court is in session!",
      "image_prompt": "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines, cartoon woman named judge vera..."
    },
    ...
  ]
}
```

**Verdict format that wins:**
- Judge Vera is the narrator / presiding judge
- Lesson told as a comparison case between TWO named litigants (Dan vs Zoe, Mike vs Lisa, etc.)
- Story arc: shocker hook + "Court is in session!" → setup → divergence → time-jump → reveal → verdict + "Court dismissed!"
- **12 scenes total, each ~5 seconds of narration (~10–13 words, hard cap 15).** Images
  swap every 5 seconds, so each scene must be a tight self-contained beat.
- Scene 1: shocker stat + Judge Vera intro ending with "Court is in session!"
- Scene 12: Judge Vera delivers the verdict + actionable lesson + "Court dismissed!"
- `video_id` prefix is `verdict-`

**Image prompt anchor** (in `image_generator.py`):
- `"kids graphic novel illustration, bold flat colors, clean black ink outlines, expressive comic book characters, friendly storybook art, vertical comic panel composition"`
- Negative: `"3D render, photorealistic, dark, scary, manga, anime, ugly, blurry, watermark, speech bubble"`

---

## Image Generation Rules

- Resolution target: 1080×1920 (vertical 9:16)
- Pollinations.ai free tier returns 576×1024 (silently downscaled)
- **Always upscale via `_upscale_to_target` in image_generator.py** — Pillow LANCZOS + moderate UnsharpMask
- Per-scene prompt = scene-specific description + global STYLE_SUFFIX + NEGATIVE_HINT
- Pollinations is queued; sequential calls work, parallel calls hit 429s
- Retry up to 6 times with backoff (15s × attempt, capped 60s)

---

## Voiceover Rules

- edge-tts at `rate="-8%"`
- `boundary="WordBoundary"` for word-level timing
- Single voice: `en-US-AriaNeural` for Judge Vera
- Output: `scene_NN.mp3` + `scene_NN.captions.json` (word-grouped timed cues)

---

## Captions

- Burnt-in via FFmpeg `drawtext` filter (no libass needed)
- Font: `/System/Library/Fonts/Supplemental/Impact.ttf` at 80pt
- White text, 6px black border
- `y=h-460` (bottom-third, above mobile UI overlap)
- 3 words per cue, ALL CAPS, sanitized to letters/digits/spaces/!?

---

## Assembler / FFmpeg Rules

- **Always use the full ffmpeg build** at `/usr/local/opt/ffmpeg-full/bin/ffmpeg` (Homebrew core `ffmpeg` lacks libfreetype; needs `brew install ffmpeg-full`)
- Per scene: `scale=8000:-1, zoompan=...:s=1080x1920:fps=30, [drawtext per caption cue]`
- Concat via `-f concat -safe 0`
- Output: H.264 CRF 20, AAC 128k, yuv420p, 30fps
- 7 motion presets cycle (zoom-in, zoom-out, pan, drift)

---

## Intel Mac vs VPS-Portable Design

Dev machine is **Intel x86_64 Mac**. The pipeline is API-based + FFmpeg, no GPU required. **VPS-portable from day one** — install Python 3.11 + ffmpeg-full equivalent, copy `.env`, `pip install -r requirements.txt`, run.

---

## Coding Standards

- Python 3.11+, PEP 8, type hints, docstrings
- `pathlib.Path` for all paths
- `pipeline.logger.get_logger()` for logging — never `print()` in production code
- `python-dotenv` for `.env`
- No hardcoded paths — env vars or `config/settings.py`

---

## Commands

```bash
# Setup (one-time)
brew install python@3.11 ffmpeg-full
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate one video
./venv/bin/python make_video.py scripts/verdict_dan_vs_zoe_credit_card_debt.json

# Tail logs
tail -f logs/pipeline.log
```

---

## What Claude Code Should Always Do

1. **Never change mascot designs** — Judge Vera, Detective Cash, Coach Vault, and Doctor Dollar's canonical looks are final (see table above)
2. **Never reintroduce the original four** (Rico, Penny, Max, Nana) — retired in favor of the professional cast
3. **Never reintroduce lipsync** — user evaluated 4 approaches and dropped it
4. **Never hardcode API keys** — always use `.env`
5. **Always validate** final video is 1080×1920 9:16 before declaring success
6. **Always log** every step with timestamps via `pipeline.logger`
7. **Always upscale Pollinations output** via `_upscale_to_target`
8. **Always match the host's signature format** — opener in scene 1, closer in scene 7, two named secondary characters, comparison story
9. **Always keep outputs** organized by `video_id`. Per-character prefixes: `verdict-` (Judge Vera), `case-file-` (Detective Cash), `workout-` (Coach Vault), `checkup-` (Doctor Dollar)
10. **Never delete outputs on failure** — keep for debugging
11. **Keep videos ~60 seconds** — YouTube Shorts limit. Target is **12 scenes × ~5s = ~60s** so the image swaps every 5 seconds throughout the video
