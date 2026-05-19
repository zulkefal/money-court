"""One-off rewriter: convert old 7-scene scripts to 12-scene × ~5s format.

The pipeline switched to 5-second image swaps; every script in scripts/*.json
needs to be 12 scenes of ~10–13 words each. This script asks Claude to
restructure each existing script while preserving video_id, character, topic,
the two named secondary characters, the comparison arc, and the host's
canonical look.

Run:  ./venv/bin/python tools/rewrite_to_12_scenes.py
      ./venv/bin/python tools/rewrite_to_12_scenes.py --dry-run
      ./venv/bin/python tools/rewrite_to_12_scenes.py --only verdict-kyle
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import ANTHROPIC_API_KEY
from pipeline.logger import get_logger

logger = get_logger("rewrite_to_12_scenes")

CLAUDE_MODEL = "claude-sonnet-4-6"
SCRIPTS_DIR = ROOT / "scripts"

SIGNATURE_OPEN = {
    "judge_vera": "Court is in session!",
    "detective_cash": "Case file 0042. Let's open the evidence.",
    "coach_vault": "Today's training session begins now!",
    "doctor_dollar": "Today's patient checkup starts here.",
}
SIGNATURE_CLOSE = {
    "judge_vera": "Court dismissed!",
    "detective_cash": "Case closed.",
    "coach_vault": "Drop and give me twenty bucks!",
    "doctor_dollar": "See you next visit. Stay financially healthy!",
}

SYSTEM_PROMPT = """\
You are restructuring an existing Money Court Shorts script from 7 long scenes
into 12 short scenes. The story, characters, comparison, and mascot stay the
same — only the pacing changes.

HARD RULES:
- Output EXACTLY 12 scenes.
- Each scene's narration: TARGET 10–13 words, hard cap 15. Going over breaks
  the 5-second per-image cadence.
- Preserve: video_id, character, topic, title, and the two named secondary
  characters from the input.
- Preserve the narrative arc and verdict/lesson — just split each old scene
  into ~2 tighter beats so the total story still resolves.
- Scene 1 must end with the mascot's signature opener.
- Scene 12 must end with the mascot's signature closer + action lesson.
- Use only letters, digits, spaces, periods, commas, ! and ? — no quote marks.
- Spell out numbers (eight thousand dollars, not $8,000).

IMAGE PROMPT RULES:
- Always start with: "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines"
- Always end with: "kids comic book illustration"
- Scenes 1 and 12 must include the host mascot's canonical look (use the same
  description from the input — copy it verbatim).
- Each scene needs its own panel concept — visually distinct so the 5-second
  swap feels intentional.

OUTPUT: ONLY valid JSON in this exact schema:
{
  "video_id": "<same as input>",
  "character": "<same as input>",
  "topic": "<same as input>",
  "title": "<same as input>",
  "scenes": [
    {"id": 1, "narration": "...", "image_prompt": "..."},
    ... (exactly 12 scenes, ids 1 through 12)
  ]
}

No prose, no markdown fences, no explanation.
"""


def rewrite(old: dict, client) -> dict:
    user_msg = (
        "Restructure this 7-scene script into 12 scenes. Keep all metadata identical.\n\n"
        f"OPENER (scene 1 must end with): {SIGNATURE_OPEN[old['character']]}\n"
        f"CLOSER (scene 12 must end with): {SIGNATURE_CLOSE[old['character']]}\n\n"
        f"INPUT SCRIPT:\n{json.dumps(old, indent=2)}\n\n"
        "Return the new JSON now."
    )

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    new = json.loads(raw)

    # Strict validation
    assert new["video_id"] == old["video_id"], (
        f"video_id changed: {old['video_id']!r} -> {new.get('video_id')!r}"
    )
    assert new["character"] == old["character"], "character changed"
    assert isinstance(new["scenes"], list) and len(new["scenes"]) == 12, (
        f"expected 12 scenes, got {len(new.get('scenes', []))}"
    )
    for i, s in enumerate(new["scenes"], start=1):
        assert s.get("id") == i, f"scene {i} has wrong id {s.get('id')}"
        assert s.get("narration"), f"scene {i} missing narration"
        assert s.get("image_prompt"), f"scene {i} missing image_prompt"
        wc = len(s["narration"].split())
        if wc > 15:
            logger.warning(f"  scene {i} word count {wc} > 15 cap: {s['narration'][:80]}")
    return new


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print plan, don't write")
    ap.add_argument("--only", help="only rewrite scripts whose stem starts with this prefix")
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between API calls")
    args = ap.parse_args()

    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set in .env")
        return 1

    targets = sorted(SCRIPTS_DIR.glob("*.json"))
    if args.only:
        targets = [p for p in targets if p.stem.startswith(args.only)]
    if not targets:
        logger.error("no scripts matched")
        return 1

    logger.info(f"found {len(targets)} script(s) to rewrite")
    if args.dry_run:
        for p in targets:
            logger.info(f"  would rewrite {p.name}")
        return 0

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    ok = fail = 0
    for p in targets:
        old = json.loads(p.read_text())
        if len(old.get("scenes", [])) == 12:
            logger.info(f"skip {p.name}: already 12 scenes")
            continue
        try:
            logger.info(f"rewriting {p.name} ({len(old['scenes'])} -> 12 scenes)")
            new = rewrite(old, client)
            p.write_text(json.dumps(new, indent=2) + "\n")
            ok += 1
            time.sleep(args.sleep)
        except Exception as e:
            logger.error(f"  FAILED {p.name}: {e}")
            fail += 1
            continue

    logger.info(f"done: {ok} rewritten, {fail} failed")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
