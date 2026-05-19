"""Generate a video script JSON via the Claude API in the same schema we hand-write.

Activated when ANTHROPIC_API_KEY is set in .env. The system prompt below encodes
all the lessons we learned hand-writing scripts: 7 scenes, comparison-story format
with character-specific framing (verdict / case file / training session / checkup),
kids comic prompt anchors, no embedded text-heavy instructions, etc.

Usage:
    from pipeline import script_generator
    script = script_generator.generate(
        character="detective_cash",
        topic="Romance scam — spotting the red flags vs falling for it",
    )
    # -> dict matching scripts/*.json schema; pass to make_video.py
"""
from __future__ import annotations

import json
import re
from datetime import date

from config.settings import ANTHROPIC_API_KEY
from pipeline.logger import get_logger

logger = get_logger("script_generator")

CLAUDE_MODEL = "claude-sonnet-4-6"

VALID_CHARACTERS = ("judge_vera", "detective_cash", "coach_vault", "doctor_dollar")

SYSTEM_PROMPT = """\
You write 60-second YouTube Shorts scripts for "Money Court" — a finance channel
with four mascots, each running a distinct format in the same comic-book universe:

  - JUDGE VERA — courtroom judge. Format: "Court is in session!" → verdict → "Court dismissed!"
    Niche: debt, contracts, lawsuits, scams, financial law.
  - DETECTIVE CASH — 1940s noir investigator. Format: "Case file 0042. Time of incident..." → "Case closed."
    Niche: scams, fraud, phishing, identity theft, romance scams, crypto rugpulls.
  - COACH VAULT — financial fitness coach. Format: "Today's training session..." → "Drop and give me twenty bucks!"
    Niche: emergency fund, savings habits, debt-payoff workout, spending diet, discipline.
  - DOCTOR DOLLAR — financial-health doctor. Format: "Today's patient checkup..." → "See you next visit. Stay financially healthy!"
    Niche: credit score, debt-to-income, net worth audit, retirement readiness.

Every script follows this winning structure (validated by user data):
- Scene 1 is a SHOCKER HOOK + the mascot's signature opener. The viewer must NOT scroll
  past the first 3 seconds.
- The mascot is the NARRATOR / presiding professional, not the subject of the story.
- The lesson is told as a COMPARISON CASE between TWO named secondary characters
  (Dan vs Zoe, Mike vs Lisa, Sam vs Pat — never reuse names from prior videos).
- 12 scenes total, each ~5 seconds of narration (~10–13 words). Scene images
  swap every 5 seconds, so each scene must be a tight, self-contained beat that
  the visual change can punctuate cleanly.
- Story arc: shocker hook → opener → setup A → setup B → divergence A → divergence B
  → mid-jump A → mid-jump B → time-jump → reveal A → reveal B → mascot's signature
  closer + lesson

You output ONLY valid JSON in this exact schema:
{
  "video_id": "<character-slug>-<name1>-vs-<name2>-<topic-slug>-001",
  "character": "<judge_vera|detective_cash|coach_vault|doctor_dollar>",
  "topic": "<short topic line, may include '(Name1 vs Name2)'>",
  "title": "<clickbaity title with $AMOUNT + emoji + comparison, see TITLE rules>",
  "scenes": [
    {"id": 1, "narration": "...", "image_prompt": "..."},
    ... (exactly 12 scenes)
  ]
}

Replace <character-slug> in `video_id` with the actual character's slug (e.g.
"verdict-dan-vs-zoe-..." for judge_vera, "case-file-mark-vs-rita-..." for
detective_cash, "workout-sam-vs-pat-..." for coach_vault, "checkup-lily-vs-eve-..."
for doctor_dollar).

NARRATION rules:
- 8th-grade reading level. Short, punchy sentences.
- Use only letters, digits, spaces, periods, commas, ! and ? — no quote marks.
- Spell out numbers in narration ("eight thousand dollars" not "$8,000").
- TARGET 10–13 WORDS PER SCENE (≈5 seconds at our TTS rate). Hard cap: 15 words.
  Going over breaks the 5-second image cadence.
- Scene 1 must lead with a shocker stat or counterintuitive fact, then transition
  into the mascot's signature opener.
- Scene 12 ends with the mascot's signature closer + an action lesson.

Per-character signature lines:

  judge_vera:
    Scene 1 ends with: "...Court is in session!"
    Scene 12 ends with: "...Court dismissed!"

  detective_cash:
    Scene 1 ends with something like: "...Case file 0042. Let's open the evidence."
    Scene 12 ends with: "...Case closed."

  coach_vault:
    Scene 1 ends with: "...Today's training session begins now!"
    Scene 12 ends with: "...Drop and give me twenty bucks!"

  doctor_dollar:
    Scene 1 ends with: "...Today's patient checkup starts here."
    Scene 12 ends with: "...See you next visit. Stay financially healthy!"

TITLE rules (for the JSON's `title` field):
- Lead with a $ amount or shocking number — quantify the hook
- NO emojis, NO icons, NO unicode symbols — plain ASCII text only
- Keep <= 75 chars total
- End with " | Money Court #shorts"

IMAGE_PROMPT rules:
- Always start with the exact phrase:
  "kids graphic novel page panel, illustrated comic book art, bold flat colors clean black ink lines"
- Always end with: "kids comic book illustration"
- Describe what's IN the panel: characters' looks, poses, props, dollar amounts shown
  as part of the art (signs, banners, comic burst lettering), backgrounds.
- Use comic conventions: motion lines, sparkles, comic burst banners.
- For the host mascot (in scenes 1 and 12), always include their canonical look:

    judge_vera = "cartoon woman named judge vera, silver hair in a neat bun, sharp dark eyes, black judge robes with a gold gavel badge, holding wooden gavel"

    detective_cash = "cartoon man named detective cash, sharp blue eyes, gray fedora hat, beige trench coat, five o'clock shadow, holding magnifying glass and a manila file folder labeled with dollar signs"

    coach_vault = "cartoon man named coach vault, athletic build, buzzcut brown hair, red track jacket with gold dollar sign logo, silver whistle, clipboard covered in dollar sign stickers, fingerless training gloves, sweatband"

    doctor_dollar = "cartoon woman named doctor dollar, dark curly hair, round gold-rim glasses, kind smile, white doctor coat over teal scrubs, golden stethoscope shaped like a dollar sign, holding a clipboard with a credit-score chart"

- For comparison scenes (side-by-side), describe both secondary characters' positions and contrast.
- Match the scene background to the character's universe:
    judge_vera     -> courtroom (bench, gavel, columns)
    detective_cash -> noir office (file cabinets, desk lamp, manila folders), or crime scene
    coach_vault    -> gym / training facility (weights, treadmills, scoreboards), or outdoor track
    doctor_dollar  -> doctor's office (exam table, blood-pressure cuff, charts on wall), or patient room

Return ONLY the JSON. No prose, no markdown fences, no explanation.
"""


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def generate(character: str, topic: str, used_names: list[str] | None = None) -> dict:
    """Generate one script via Claude. Caller is responsible for validating + saving."""
    if character not in VALID_CHARACTERS:
        raise ValueError(
            f"unknown character {character!r}. Must be one of {VALID_CHARACTERS}"
        )
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set in .env — script_generator needs it. "
            "Get one at https://console.anthropic.com (free $5 credit on signup)."
        )

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_msg = (
        f"Mascot: {character}\n"
        f"Topic: {topic}\n"
        f"Today: {date.today().isoformat()}\n"
    )
    if used_names:
        user_msg += f"\nDo NOT reuse these secondary character names: {', '.join(used_names)}\n"
    user_msg += "\nReturn the JSON now."

    logger.info(f"claude: character={character} topic={topic[:60]!r}")
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.content[0].text.strip()
    # In case Claude wraps in fences despite instructions
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    script = json.loads(raw)

    # Light validation
    assert script["character"] == character, (
        f"character mismatch: asked for {character!r}, got {script.get('character')!r}"
    )
    assert isinstance(script["scenes"], list) and len(script["scenes"]) == 12, (
        f"expected 12 scenes, got {len(script.get('scenes', []))}"
    )
    for s in script["scenes"]:
        assert "narration" in s and "image_prompt" in s, f"malformed scene: {s}"

    logger.info(f"claude: generated video_id={script['video_id']}")
    return script
