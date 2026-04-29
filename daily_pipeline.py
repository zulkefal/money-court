"""Daily Money Court automation — one command, one video, scheduled to YouTube.

Logic:
  1. Pick the next un-cooled-down topic from config/topics.py
  2. Generate a verdict-format script via Claude (pipeline/script_generator.py)
     — needs ANTHROPIC_API_KEY
  3. Run the standard render pipeline (image gen + voice + assemble)
  4. Upload to YouTube with publishAt = today at 12:00 PKT (or override via --publish-at)
  5. Record the topic so it cools down for 30 days

Usage:
    ./venv/bin/python daily_pipeline.py                    # full auto, schedules for noon today PKT
    ./venv/bin/python daily_pipeline.py --topic "Co-signing a loan when it goes wrong vs when it works"
    ./venv/bin/python daily_pipeline.py --dry-run          # generate the script, don't render or upload
    ./venv/bin/python daily_pipeline.py --no-upload        # render but skip upload

Cron (later):
    0 9 * * * cd /path/to/Youtube && ./venv/bin/python daily_pipeline.py >> logs/cron.log 2>&1
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from config.settings import ANTHROPIC_API_KEY, SCRIPTS_DIR
from config.topics import pick_topic, record_topic
from pipeline.logger import get_logger

logger = get_logger("daily")

# Daily mascot rotation. Cycles in this order so each character gets equal screen time.
ROTATION = ("judge_vera", "detective_cash", "coach_vault", "doctor_dollar")
PKT = timezone(timedelta(hours=5))

# Hand-written + auto-generated scripts both live here. After successful upload,
# scripts are moved to QUEUE_DIR / "archive" so the queue only ever shows pending work.
QUEUE_DIR = Path("scripts")
ARCHIVE_DIR = QUEUE_DIR / "archive"
TARGET_QUEUE_DEPTH = 5

# Random publishAt windows per slot. Two-slot day = morning + evening, with
# random minute offsets so the channel doesn't always post at the same exact
# time (looks more human, gives broader algo testing across hours).
SLOT_WINDOWS = {
    1: [(11, 14)],                  # 1/day: midday block
    2: [(9, 12), (17, 20)],         # 2/day: late-morning + early-evening
    3: [(9, 11), (13, 16), (18, 21)],  # 3/day: morning, afternoon, evening
}


def _next_character(history_path: Path) -> str:
    """Pick whichever mascot was last used the longest ago (rotate)."""
    if not history_path.exists():
        return ROTATION[0]
    history = json.loads(history_path.read_text())
    if not history:
        return ROTATION[0]
    last_char = history[-1]["character"]
    idx = ROTATION.index(last_char) if last_char in ROTATION else -1
    return ROTATION[(idx + 1) % len(ROTATION)]


def _random_publish_at(target_date: date, slot_idx: int, slots_per_day: int) -> str:
    """Pick a random RFC-3339 timestamp inside the slot's window for `target_date`."""
    windows = SLOT_WINDOWS.get(slots_per_day, SLOT_WINDOWS[1])
    start_h, end_h = windows[slot_idx]
    hour = random.randint(start_h, max(start_h, end_h - 1))
    minute = random.choice([0, 7, 13, 19, 22, 27, 31, 38, 41, 47, 53, 58])
    dt = datetime(target_date.year, target_date.month, target_date.day,
                  hour, minute, 0, tzinfo=PKT)
    # If chosen time has already passed today, push to tomorrow's same window
    if dt < datetime.now(PKT) + timedelta(minutes=10):
        dt += timedelta(days=1)
    return dt.isoformat()


def _queued_scripts() -> list[Path]:
    """Pending scripts in scripts/*.json (NOT scripts/archive/*.json)."""
    QUEUE_DIR.mkdir(exist_ok=True)
    return sorted(p for p in QUEUE_DIR.glob("*.json") if p.is_file())


def _generate_and_save(character: str, topic: str) -> Path:
    """Call Claude, save the result to scripts/<id>.json, return the path."""
    from pipeline import script_generator
    script = script_generator.generate(character=character, topic=topic)
    QUEUE_DIR.mkdir(exist_ok=True)
    path = QUEUE_DIR / f"{script['video_id']}.json"
    path.write_text(json.dumps(script, indent=2))
    logger.info(f"  generated: {path.name}")
    return path


def _topic_already_queued(character: str, topic: str, queued: list[Path]) -> bool:
    """Avoid generating a script for a topic that's already sitting in the queue."""
    for p in queued:
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        if data.get("character") == character and data.get("topic", "").startswith(topic):
            return True
    return False


def _backfill_queue() -> None:
    """If queue depth < TARGET_QUEUE_DEPTH, generate enough scripts to fill it.

    No-op if ANTHROPIC_API_KEY is not set — user is in JSON-only mode. Rotates
    across mascots so the queue is balanced.
    """
    if not ANTHROPIC_API_KEY:
        logger.info("  backfill: ANTHROPIC_API_KEY not set, skipping (JSON-only mode)")
        return

    queued = _queued_scripts()
    needed = TARGET_QUEUE_DEPTH - len(queued)
    if needed <= 0:
        logger.info(f"  backfill: queue depth {len(queued)} >= target {TARGET_QUEUE_DEPTH}, nothing to do")
        return

    logger.info(f"  backfill: queue has {len(queued)}, generating {needed} more")
    char_iter = iter([ROTATION[i % len(ROTATION)] for i in range(needed * 2)])
    for _ in range(needed):
        for _attempt in range(len(ROTATION) * 2):
            character = next(char_iter, ROTATION[0])
            try:
                topic = pick_topic(character)
            except RuntimeError:
                continue  # this character has nothing fresh; try next
            if _topic_already_queued(character, topic, _queued_scripts()):
                continue
            _generate_and_save(character, topic)
            break
        else:
            logger.warning("  backfill: ran out of (character, topic) combos — extend TOPIC_BANK")
            break


def _archive(script_path: Path) -> Path:
    """Move a used script from queue to archive so it doesn't get re-rendered."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    target = ARCHIVE_DIR / script_path.name
    script_path.rename(target)
    logger.info(f"  archived: {target}")
    return target


def _run_one_slot(
    slot_idx: int,
    slots_per_day: int,
    character: str | None,
    topic: str | None,
    dry_run: bool,
    no_upload: bool,
    publish_at_override: str | None,
) -> None:
    # Step 1: pick a script from the queue. If the queue is empty, generate one
    # via Claude (or fail loudly if we're in JSON-only mode).
    queue = _queued_scripts()
    if queue:
        script_path = queue[0]
        script = json.loads(script_path.read_text())
        logger.info(
            f"slot {slot_idx + 1}/{slots_per_day}: queue has {len(queue)}, "
            f"using {script_path.name}"
        )
    else:
        if not ANTHROPIC_API_KEY:
            raise SystemExit(
                "Queue is empty (scripts/*.json) and ANTHROPIC_API_KEY is not set. "
                "Either drop a hand-written script into scripts/ or set the API key."
            )
        if character is None:
            from config.topics import USED_TOPICS_FILE
            character = _next_character(USED_TOPICS_FILE)
        if character not in ROTATION:
            raise SystemExit(f"unknown character: {character}. Choices: {list(ROTATION)}")
        if topic is None:
            topic = pick_topic(character)
        logger.info(
            f"slot {slot_idx + 1}/{slots_per_day}: queue empty, "
            f"generating fresh script ({character} / {topic!r})"
        )
        script_path = _generate_and_save(character=character, topic=topic)
        script = json.loads(script_path.read_text())

    character = script["character"]
    topic = script.get("topic", "")

    if dry_run:
        logger.info("  --dry-run set; stopping after script selection")
        return

    publish_at = publish_at_override or _random_publish_at(date.today(), slot_idx, slots_per_day)
    logger.info(f"  publishAt: {publish_at}")

    from make_video import main as render_main
    render_main(
        script_path=script_path,
        upload=not no_upload,
        privacy="private",
        made_for_kids=False,
        publish_at=publish_at,
    )

    # Only mark as used after a successful render (and upload, if requested).
    if not no_upload:
        _archive(script_path)
        record_topic(character, topic)
        logger.info(f"  topic recorded: {character} / {topic}")
    else:
        logger.info("  --no-upload: leaving script in queue, not recording topic")

    # Top up the queue for tomorrow.
    _backfill_queue()


def main(
    character: str | None,
    topic: str | None,
    dry_run: bool,
    no_upload: bool,
    publish_at: str | None,
    slots: int,
) -> None:
    if slots not in SLOT_WINDOWS:
        raise SystemExit(f"--slots must be one of {sorted(SLOT_WINDOWS)}")
    for slot_idx in range(slots):
        _run_one_slot(
            slot_idx=slot_idx,
            slots_per_day=slots,
            character=character if slots == 1 else None,
            topic=topic if slots == 1 else None,
            dry_run=dry_run,
            no_upload=no_upload,
            publish_at_override=publish_at if slots == 1 else None,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", choices=ROTATION, default=None,
                        help="Force a specific mascot. Empty = auto-rotate.")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument(
        "--publish-at",
        default=None,
        help="Override scheduled publish time (RFC-3339). Single-slot only.",
    )
    parser.add_argument(
        "--slots",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="Videos per day. 2 = morning + evening. Each slot picks a random "
             "minute within its hour-window so post times don't look robotic.",
    )
    args = parser.parse_args()
    main(
        character=args.character,
        topic=args.topic,
        dry_run=args.dry_run,
        no_upload=args.no_upload,
        publish_at=args.publish_at,
        slots=args.slots,
    )
