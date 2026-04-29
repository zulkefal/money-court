"""Finance topic bank, scoped per character. Tracks usage to avoid 30-day repeats."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from config.settings import OUTPUT_DIR

TOPIC_BANK: dict[str, list[str]] = {
    "judge_vera": [
        "Ignoring credit card debt letters vs responding to them",
        "Co-signing a loan — when it goes wrong vs when it works",
        "Reading a contract before signing vs signing blind",
        "Disputing a wrong charge vs paying it",
        "Filing taxes on time vs ignoring the IRS",
        "Settling a debt in writing vs verbal agreement",
        "Checking your credit report vs ignoring it for years",
        "Responding to a court summons vs missing the hearing",
        "Saving receipts for tax write-offs vs guessing later",
        "Reading the fine print on a payday loan vs signing fast",
    ],
    "detective_cash": [
        "Romance scam — spotting the red flags vs falling for it",
        "Phishing email — verifying the sender vs clicking the link",
        "Crypto rugpull — researching the project vs ape-buying",
        "Fake check overpayment scam — stopping the wire vs sending it",
        "Identity theft — freezing your credit vs ignoring the breach",
        "IRS impersonation call — hanging up vs paying the gift card",
        "Job offer scam — verifying the company vs sending personal info",
        "Investment too-good-to-be-true vs real diversified investing",
        "Tech support pop-up scam — closing the tab vs calling the number",
        "Marketplace overpayment — refusing the deal vs cashing the check",
    ],
    "coach_vault": [
        "Building a 1000 dollar emergency fund — drills vs procrastinating",
        "Saving 20 percent of every paycheck vs spending it all",
        "Cutting one daily expense vs keeping every habit",
        "30-day no-spend challenge vs business-as-usual",
        "Debt snowball workout — smallest first vs avoiding the bill",
        "Automating savings transfers vs relying on willpower",
        "Tracking every expense for a month vs eyeballing it",
        "Cash envelope budgeting vs swiping every card",
        "Cooking at home five nights vs eating out five nights",
        "Cancelling unused subscriptions vs leaving them running",
    ],
    "doctor_dollar": [
        "Credit score 580 vs 780 — five-year financial health checkup",
        "Debt to income 50 percent vs 20 percent — long-term prognosis",
        "Auditing your net worth yearly vs never tracking it",
        "Maxing a 401k match vs leaving it on the table",
        "Roth IRA at 25 vs starting at 45",
        "High-interest debt vs the same money in an index fund",
        "Term life insurance at 30 vs trying to buy it at 50",
        "Reviewing your insurance coverage yearly vs autopilot",
        "Three-month emergency fund vs paycheck to paycheck",
        "Annual financial physical vs ignoring your money for a decade",
    ],
}

USED_TOPICS_FILE = OUTPUT_DIR / "used_topics.json"
COOLDOWN_DAYS = 30


def _load_history() -> list[dict]:
    if not USED_TOPICS_FILE.exists():
        return []
    return json.loads(USED_TOPICS_FILE.read_text())


def _save_history(history: list[dict]) -> None:
    USED_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USED_TOPICS_FILE.write_text(json.dumps(history, indent=2))


def pick_topic(character_slug: str, today: date | None = None) -> str:
    """Return the next un-cooled-down topic for the given character.

    Raises if every topic has been used within COOLDOWN_DAYS — caller should
    extend the topic bank when this happens.
    """
    today = today or date.today()
    cutoff = today - timedelta(days=COOLDOWN_DAYS)
    history = _load_history()
    recently_used = {
        entry["topic"]
        for entry in history
        if date.fromisoformat(entry["date"]) >= cutoff
        and entry["character"] == character_slug
    }
    for topic in TOPIC_BANK[character_slug]:
        if topic not in recently_used:
            return topic
    raise RuntimeError(
        f"All topics for {character_slug} used within {COOLDOWN_DAYS} days — extend topic bank"
    )


def record_topic(character_slug: str, topic: str, today: date | None = None) -> None:
    today = today or date.today()
    history = _load_history()
    history.append(
        {"date": today.isoformat(), "character": character_slug, "topic": topic}
    )
    _save_history(history)
