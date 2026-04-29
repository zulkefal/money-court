"""Money Court character definitions: prompts, voice traits, motion style."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Character:
    name: str
    slug: str
    personality: str
    topics: str
    prompt: str
    negative_extra: str
    motion_style: str
    voice_traits: str
    palette: tuple[str, ...]


JUDGE_VERA = Character(
    name="Judge Vera",
    slug="judge_vera",
    personality="stern but fair courtroom judge",
    topics="debt, contracts, lawsuits, scams, financial law verdicts",
    prompt=(
        "judge vera, cartoon woman, silver hair in a neat bun, sharp dark eyes, "
        "black judge robes with a gold gavel badge, holding wooden gavel, "
        "flat cartoon style, ToonYou style"
    ),
    negative_extra="kid, child, young, casual clothes",
    motion_style="firm steady motion, gavel banging, courtroom camera push-in",
    voice_traits="adult woman, confident, authoritative",
    palette=("#1F2233", "#C9A227", "#7A1E1E"),
)

DETECTIVE_CASH = Character(
    name="Detective Cash",
    slug="detective_cash",
    personality="hardboiled 1940s noir investigator",
    topics="scams, fraud, phishing, identity theft, romance scams, crypto rugpulls, fake checks",
    prompt=(
        "detective cash, cartoon man, sharp blue eyes, gray fedora hat, beige trench coat, "
        "five o'clock shadow, holding magnifying glass and a manila file folder labeled with dollar signs, "
        "flat cartoon style, ToonYou style"
    ),
    negative_extra="kid, child, young, female",
    motion_style="film noir camera moves, slow zoom on evidence, dramatic spotlight",
    voice_traits="adult man, gruff, investigative",
    palette=("#3B3122", "#C28840", "#1F2A38"),
)

COACH_VAULT = Character(
    name="Coach Vault",
    slug="coach_vault",
    personality="energetic financial fitness coach",
    topics="emergency fund, savings streaks, debt payoff workout, spending diet, budget discipline",
    prompt=(
        "coach vault, cartoon man, athletic build, buzzcut brown hair, red track jacket with gold dollar sign logo, "
        "silver whistle around neck, holding a clipboard covered in dollar sign stickers, "
        "fingerless training gloves, sweatband, flat cartoon style, ToonYou style"
    ),
    negative_extra="kid, child, female, weak, unhealthy",
    motion_style="energetic motion, whistle blowing, push-up countdown, gym camera pan",
    voice_traits="adult man, energetic, motivating",
    palette=("#C8102E", "#F5C842", "#1A1A1A"),
)

DOCTOR_DOLLAR = Character(
    name="Doctor Dollar",
    slug="doctor_dollar",
    personality="warm financial-health doctor",
    topics="credit score health, debt to income ratio, net worth audit, retirement readiness, financial checkup",
    prompt=(
        "doctor dollar, cartoon woman, dark curly hair, round gold-rim glasses, kind smile, "
        "white doctor coat over teal scrubs, golden stethoscope shaped like a dollar sign, "
        "holding a clipboard with a credit-score chart, flat cartoon style, ToonYou style"
    ),
    negative_extra="kid, child, scary, sick-looking",
    motion_style="gentle motion, stethoscope swing, clipboard reveal, calm camera",
    voice_traits="adult woman, warm, reassuring",
    palette=("#2BB3A3", "#F5F5F5", "#C9A227"),
)

ROSTER: tuple[Character, ...] = (JUDGE_VERA, DETECTIVE_CASH, COACH_VAULT, DOCTOR_DOLLAR)
BY_SLUG: dict[str, Character] = {c.slug: c for c in ROSTER}

POSITIVE_GLOBAL = (
    "flat cartoon style, bright colors, clean lines, kids friendly, finance theme, "
    "high quality, sharp, vibrant, vertical 9:16 composition"
)
NEGATIVE_GLOBAL = (
    "realistic, photo, dark, scary, violent, ugly, blurry, watermark, logo, text, "
    "nsfw, adult content, weapons, blood, deformed, extra fingers, bad anatomy"
)
