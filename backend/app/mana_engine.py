from __future__ import annotations

from datetime import datetime
from typing import Any


def _by_time(task_rows: list[dict]) -> list[dict]:
    def k(t: dict) -> datetime:
        x = t.get("scheduled_time")
        return x if isinstance(x, datetime) else datetime.min
    return sorted(task_rows, key=k)


def run_mana_engine(
    current_energy: float,
    remaining_cost: float,
    estimated_end: float,
    remaining_tasks: list[dict],
) -> dict[str, Any]:
    ce = max(0.0, float(current_energy))
    rc = max(0.0, float(remaining_cost))
    ee = max(0.0, float(estimated_end))

    stress = 0.0
    if rc > 0 and ce > 0:
        stress = min(10.0, round((rc / ce) * 4.0, 1))
    elif rc > 0 and ce <= 0:
        stress = 10.0

    overload = rc > ce + 0.01

    upcoming = _by_time(remaining_tasks)
    next_title = None
    next_cost = None
    if upcoming:
        next_title = str(upcoming[0].get("title", "task"))[:80]
        next_cost = float(upcoming[0].get("energy_cost", 0))

    tip = _make_tip(stress, ee, overload, next_cost, next_title)

    return {
        "mana_stress": stress,
        "overload_warning": overload,
        "scheduling_tip": tip,
        "next_up_title": next_title,
        "next_up_energy": next_cost,
    }


def _make_tip(
    stress: float,
    est_end: float,
    overload: bool,
    next_cost: float | None,
    next_title: str | None,
) -> str:
    if est_end <= 0.5:
        return "Energy math says you'll be empty — skip or move something unless you log more mana later."
    if overload:
        return "Planned stuff costs more than you've got left. Drop the smallest task or push it to tomorrow."
    if stress >= 7.5:
        return "Pretty packed. Do the easiest thing on the list first so you get a win."
    if stress >= 4.0:
        return "Kinda tight — don't chain big tasks back to back if you can help it."
    if next_cost is not None and next_cost >= 7 and next_title:
        return f"'{next_title}' is a big drain — quick break before you dive in helps."
    if next_title:
        return f"Next: {next_title}. Keep it one thing at a time."
    return "Nothing huge queued — still log mana when it changes."
