"""Generate YouTube title/description/tags from a script.

Each script JSON can override any of `title`, `description`, `tags`. If absent,
we generate them deterministically from the script's `topic`, `character`, and
narration. No API call needed (would need an Anthropic key for that — deferred).
"""
from __future__ import annotations

import re
from typing import TypedDict


class VideoMetadata(TypedDict):
    title: str
    description: str
    tags: list[str]


CHANNEL_PITCH = (
    "🎬 Welcome to Money Court — Judge Vera, Detective Cash, Coach Vault & Doctor Dollar\n"
    "    break down real-world money cases every day!\n"
    "📱 New episode daily\n"
)

DEFAULT_HASHTAGS = (
    "#MoneyTips #PersonalFinance #DebtAdvice #CreditScore #FinancialEducation "
    "#Shorts #MoneyCourt"
)

# Long-form (opportunity_cost / case_study): no #Shorts tag, SEO-leaning
LONG_HASHTAGS = (
    "#PersonalFinance #InvestingForBeginners #StockMarket #FinancialEducation "
    "#MoneyLessons #WealthBuilding #FinancialFreedom #MoneyCrew"
)

# SEO keywords for long-form opportunity-cost videos
LONG_OPPORTUNITY_TAGS = [
    "what if i had bought stock instead",
    "opportunity cost", "stock vs product", "investing instead of spending",
    "long term investing", "compound returns", "stock market history",
    "personal finance long form",
]
LONG_CASE_STUDY_TAGS = [
    "millionaire case study", "hidden millionaire", "frugal millionaire",
    "wealth building story", "real millionaire", "personal finance story",
    "financial freedom", "money lessons",
]

# Stable per-character tag mix
CHARACTER_TAGS = {
    "judge_vera": [
        "debt", "credit cards", "credit score", "financial law",
        "judge vera", "money court", "debt collection", "lawsuits",
    ],
    "detective_cash": [
        "scams", "fraud", "phishing", "identity theft", "romance scams",
        "crypto scams", "fake checks", "detective cash", "money court",
    ],
    "coach_vault": [
        "saving money", "emergency fund", "budget discipline",
        "debt payoff", "savings habit", "spending diet",
        "coach vault", "money court",
    ],
    "doctor_dollar": [
        "credit score", "net worth", "debt to income", "retirement readiness",
        "financial health", "money checkup", "doctor dollar", "money court",
    ],
}

CORE_TAGS = [
    "money", "finance", "personal finance", "money court",
    "shorts", "money lessons", "financial education",
    "debt advice", "credit advice",
]

# Per-character emoji pair — used when generating a clickbaity title fallback
CHARACTER_EMOJI = {
    "judge_vera":     "⚖️🔨",
    "detective_cash": "🕵️🔍",
    "coach_vault":    "💪💰",
    "doctor_dollar":  "🩺💊",
}

# Word-form numbers spoken in narration → numeric strings, for title extraction
NUMBER_WORDS = {
    "hundred": "00", "thousand": "000", "million": "000000",
    "two hundred": "200", "three hundred": "300", "four hundred": "400",
    "five hundred": "500", "six hundred": "600", "seven hundred": "700",
    "eight hundred": "800", "nine hundred": "900",
    "one thousand": "1,000", "two thousand": "2,000", "five thousand": "5,000",
    "ten thousand": "10,000", "thirty thousand": "30,000",
    "one hundred thousand": "100,000",
}


def _extract_biggest_dollar_amount(narrations: list[str]) -> str | None:
    """Find the biggest spelled-out dollar amount in narration. Returns formatted string ('$1,800') or None."""
    text = " ".join(narrations).lower()
    candidates: list[int] = []
    # Match patterns like "eighteen hundred dollars", "one hundred thousand dollars"
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
        "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
        "seventy": 70, "eighty": 80, "ninety": 90,
        "hundred": 100, "thousand": 1000, "million": 1000000,
        "eighteen": 18, "thirteen": 13, "fourteen": 14,
        "sixteen": 16, "seventeen": 17, "nineteen": 19,
    }
    # Look for "<number-words> (hundred|thousand|million)? dollars"
    pattern = re.compile(
        r"\b((?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
        r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
        r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|"
        r"and|\s)+)\s+dollars?",
        re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        words = m.group(1).strip().split()
        words = [w for w in words if w not in ("and",)]
        # Cheap left-to-right multiplier evaluation
        total = 0
        running = 0
        for w in words:
            n = word_to_num.get(w)
            if n is None:
                continue
            if n in (100, 1000, 1000000):
                running = max(running, 1) * n
                total += running
                running = 0
            else:
                running += n
        total += running
        if total > 0:
            candidates.append(total)
    if not candidates:
        return None
    biggest = max(candidates)
    return f"${biggest:,}"


def _default_title(topic: str, character: str, narrations: list[str]) -> str:
    """Clickbaity fallback title — leads with a $ figure + emoji."""
    emoji = CHARACTER_EMOJI.get(character, "💰")
    amount = _extract_biggest_dollar_amount(narrations)
    # Pull the "X vs Y" comparison out of the topic if present
    comparison = ""
    if "(" in topic and ")" in topic:
        _, _, comp = topic.partition("(")
        comparison = comp.rstrip(")").strip()
    suffix = " | Money Court #shorts"
    if amount and comparison:
        head = f"{amount} {emoji} {comparison}"
    elif amount:
        head = f"{amount} {emoji} {topic.split('(')[0].strip()}"
    elif comparison:
        head = f"{emoji} {comparison}"
    else:
        head = f"{emoji} {topic[:60]}"
    title = head + suffix
    # YouTube hard cap is 100; aim for ≤75 for better mobile display
    if len(title) > 100:
        title = title[:97] + "…"
    return title


def _default_description(topic: str, character: str, narrations: list[str]) -> str:
    """Multi-line description: one-liner hook, blurb, channel pitch, hashtags."""
    cname = character.capitalize()
    hook = narrations[0].strip() if narrations else ""
    lesson = narrations[-1].strip() if narrations else ""
    blurb_lines = [
        f"{cname} shares the story behind today's money lesson: {topic}",
        "",
        hook,
        "",
        lesson,
        "",
        CHANNEL_PITCH,
        "Subscribe and follow for more money tips!",
        "",
        DEFAULT_HASHTAGS,
    ]
    return "\n".join(blurb_lines)


def _default_tags(character: str) -> list[str]:
    return CORE_TAGS + CHARACTER_TAGS.get(character, []) + ["money court", "comic finance"]


def _long_default_title(topic: str, format_: str) -> str:
    """SEO-friendly fallback title for long-form. No emoji, no shorts suffix."""
    base = topic.strip()
    # If the topic isn't already shaped like a question/headline, append a curiosity gap
    suffix_options = {
        "opportunity_cost": " (The Math Will Shock You)",
        "case_study": " (The Story Behind the Money)",
    }
    suffix = suffix_options.get(format_, "")
    title = base + suffix
    if len(title) > 100:
        title = title[:97] + "..."
    return title


def _long_default_description(topic: str, host: str, narrations: list[str], format_: str) -> str:
    """Description for long-form. Hook in scene 1, takeaway in last scene, no #shorts."""
    hook = narrations[0].strip() if narrations else ""
    lesson = narrations[-1].strip() if len(narrations) > 1 else ""
    body_summary = " ".join(narrations[1:4]).strip()[:400] if len(narrations) > 4 else ""
    lines = [
        topic,
        "",
        hook,
        "",
    ]
    if body_summary:
        lines.extend([body_summary, ""])
    if lesson:
        lines.extend([lesson, ""])
    lines.extend([
        "Subscribe to Money Court for weekly long-form money breakdowns.",
        "",
        "Hosted by " + host.replace("_", " ").title() + " — Money Court verdicts.",
        "",
        LONG_HASHTAGS,
    ])
    return "\n".join(lines)


def _long_default_tags(host: str, format_: str) -> list[str]:
    base = ["money", "personal finance", "money court", "finance education"]
    base += CHARACTER_TAGS.get(host, [])
    if format_ == "opportunity_cost":
        base += LONG_OPPORTUNITY_TAGS
    elif format_ == "case_study":
        base += LONG_CASE_STUDY_TAGS
    # Dedupe, preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in base:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out


def metadata_for(script: dict) -> VideoMetadata:
    """Pull or generate title/description/tags from a parsed script JSON.

    Branches on script.get("format"):
      - "opportunity_cost" / "case_study": long-form (no emoji, no #shorts, SEO-first)
      - anything else (or absent): Shorts (clickbaity emoji + #shorts)
    """
    fmt = script.get("format")
    is_long = fmt in ("opportunity_cost", "case_study")
    topic = script.get("topic", "")
    narrations = [s.get("narration", "") for s in script.get("scenes", [])]

    if is_long:
        host = script.get("host") or script.get("character") or "judge_vera"
        title = script.get("title") or _long_default_title(topic, fmt)
        description = script.get("description") or _long_default_description(
            topic, host, narrations, fmt
        )
        tags = script.get("tags") or _long_default_tags(host, fmt)
    else:
        character = script["character"]
        title = script.get("title") or _default_title(topic, character, narrations)
        description = script.get("description") or _default_description(
            topic, character, narrations
        )
        tags = script.get("tags") or _default_tags(character)

    return {"title": title[:100], "description": description[:5000], "tags": tags[:30]}
