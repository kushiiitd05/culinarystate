"""C15 multi-objective selector (SSOT §257B.15): Pareto front over candidate process options.

Objectives (each option must report; UNKNOWN is valid):
- **retention**: median retention factor for the target nutrient (higher is better)
- **time**: typical process duration in minutes (lower is better; UNKNOWN = neutral)
- **feasibility**: ALLOWED/CONSTRAINED/REJECTED (categorical; REJECTED → dominated)

Pareto front: an option is non-dominated if no other option is better on ALL objectives
simultaneously. UNKNOWN objectives are neutral (neither dominate nor dominated on that axis).
No hidden weights — the user sees the full trade-off set.

Usage:
  options = [Option("boil", retention=0.50, time=15.0, feasibility="ALLOWED"),
             Option("steam", retention=0.85, time=20.0, feasibility="ALLOWED")]
  result = select(options)
  # result.front = [steam] because steam dominates boil on retention;
  # boil dominates steam on time, so both are on the front.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

VERSION = "selector@0.1"

Feasibility = Literal["ALLOWED", "CONSTRAINED", "REJECTED", "UNKNOWN"]


@dataclass(frozen=True)
class Option:
    name: str
    retention: float | None = None       # 0–1 (higher better); None = UNKNOWN
    time_minutes: float | None = None    # lower better; None = UNKNOWN
    feasibility: Feasibility = "UNKNOWN"
    process_id: str | None = None
    evidence_count: int = 0


@dataclass(frozen=True)
class Selection:
    front: tuple[Option, ...]            # Pareto-optimal options
    dominated: tuple[Option, ...]        # options dominated by at least one front option
    rejected: tuple[Option, ...]         # options with feasibility=REJECTED (excluded from front)
    version: str = VERSION


def _dominates(a: Option, b: Option) -> bool:
    """True if a dominates b: a is at least as good on every objective and strictly better on at least one.
    UNKNOWN objectives are neutral (not compared). REJECTED feasibility makes an option dominated."""
    if b.feasibility == "REJECTED":
        return a.feasibility != "REJECTED"
    if a.feasibility == "REJECTED":
        return False
    scores = []  # (a_better, b_better) per objective
    # retention: higher better
    if a.retention is not None and b.retention is not None:
        scores.append((a.retention > b.retention, b.retention > a.retention))
    # time: lower better
    if a.time_minutes is not None and b.time_minutes is not None:
        scores.append((a.time_minutes < b.time_minutes, b.time_minutes < a.time_minutes))
    # feasibility: ALLOWED > CONSTRAINED > UNKNOWN
    feas_rank = {"ALLOWED": 2, "CONSTRAINED": 1, "UNKNOWN": 0}
    fa, fb = feas_rank.get(a.feasibility, 0), feas_rank.get(b.feasibility, 0)
    if fa != fb:
        scores.append((fa > fb, fb > fa))
    if not scores:
        return False  # nothing to compare
    a_any_better = any(ab for ab, _ in scores)
    b_any_better = any(bb for _, bb in scores)
    return a_any_better and not b_any_better


def select(options: list[Option]) -> Selection:
    """Compute Pareto front over options. REJECTED options excluded from front."""
    rejected = [o for o in options if o.feasibility == "REJECTED"]
    active = [o for o in options if o.feasibility != "REJECTED"]
    dominated = []
    front = []
    for i, a in enumerate(active):
        is_dominated = any(_dominates(b, a) for j, b in enumerate(active) if j != i)
        if is_dominated:
            dominated.append(a)
        else:
            front.append(a)
    # sort front by retention descending (primary), then time ascending
    front.sort(key=lambda o: (-(o.retention or 0), o.time_minutes or float("inf")))
    return Selection(front=tuple(front), dominated=tuple(dominated), rejected=tuple(rejected))
