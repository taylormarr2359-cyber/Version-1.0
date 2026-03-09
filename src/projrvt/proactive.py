from __future__ import annotations

from datetime import datetime
from typing import Iterable


def build_daily_briefing(
    notes: Iterable[str] | None = None,
    calendar_items: Iterable[str] | None = None,
    wake_word: str = "atlas",
) -> str:
    now = datetime.now()
    part = "morning" if now.hour < 12 else "afternoon" if now.hour < 18 else "evening"
    notes_list = [n for n in (notes or []) if str(n).strip()]
    cal_list = [c for c in (calendar_items or []) if str(c).strip()]

    lines = [
        f"Good {part}.",
        f"Wake word is set to '{wake_word}'.",
        f"You have {len(cal_list)} calendar item(s) and {len(notes_list)} note(s).",
    ]

    if cal_list:
        lines.append("Next up: " + cal_list[0])
    if notes_list:
        lines.append("Top note: " + notes_list[0])

    return "\n".join(lines)


def build_insights(memory_lines: Iterable[str] | None = None) -> str:
    lines = [l.strip() for l in (memory_lines or []) if str(l).strip()]
    if not lines:
        return "No notable patterns yet. Keep using ATLAS and I will learn your routines."

    weather_mentions = sum(1 for l in lines if "weather" in l.lower())
    planning_mentions = sum(1 for l in lines if l.lower().startswith("user: plan"))
    note_mentions = sum(1 for l in lines if "notes" in l.lower())

    insights: list[str] = []
    if weather_mentions >= 2:
        insights.append("You often ask about weather; consider a scheduled daily forecast briefing.")
    if planning_mentions >= 2:
        insights.append("You frequently create plans; I can pre-generate a daily priority plan.")
    if note_mentions >= 2:
        insights.append("You rely on notes heavily; I can suggest weekly note summaries.")

    if not insights:
        insights.append("Usage is balanced. I recommend enabling daily briefing for proactive support.")

    return "\n".join(f"- {i}" for i in insights)
