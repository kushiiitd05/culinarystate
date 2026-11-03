"""DRAFT_PENDING_34a_0 -- Step 34a composition-consistency test scaffold (G15-8; synthetic-tested).

Plan Step 34 and its architecture detail: for a composite row start -> P1 -> P2 -> end, the
M2-chain prediction applies the one-step model per step with multiplicative composition
RF1 x RF2 (independence between steps is an ASSUMPTION, flagged), compared with M1
composite lookup. G34a: "chain-consistent" iff chain composite error <= (1 + rho) x
composite-lookup error AND propagated coverage >= c_floor; either verdict passes, an
inconsistent chain is a retained negative ("one-step models must not be chained").

``rho`` and ``c_floor`` are PROPOSED_PILOT in the plan; both are required arguments here.
Errors are mean absolute errors (the plan's "composite MAE").

34a.0 circularity: every source family needs a recorded circularity status. ``UNKNOWN``
(the 34a.0 check of e.g. USDA multi-step factors not done) refuses the run;
``DERIVED_MULTIPLICATIVE`` excludes that source (plan: then USDA is excluded, PE only).

Fold integrity: composite rows and their single-step constituents from the same lineage
component must sit in one fold, otherwise the chain trivially reproduces the composite.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

STATUS = "DRAFT_PENDING_34a_0"
CIRCULARITY_STATUSES = ("CHECKED_NOT_DERIVED", "DERIVED_MULTIPLICATIVE", "UNKNOWN")
LABELS = ("DIAGNOSTIC_ONLY", "STEP_INDEPENDENCE_ASSUMED")


class CompositionRefused(RuntimeError):
    """34a cannot run as asked; ``blockers`` lists every reason as ``CODE: detail``."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("34a refused: " + "; ".join(self.blockers))


@dataclass(frozen=True)
class CompositeRow:
    row_id: str
    source_family: str
    steps: tuple[str, ...]
    observed: float
    component: str
    interval: Optional[tuple[float, float]] = None  # propagated chain interval, if computed


@dataclass(frozen=True)
class SingleStepRow:
    row_id: str
    step: str
    component: str


def chain_prediction(steps: Sequence[str], one_step: Callable[[str], float]) -> float:
    """Multiplicative composition of one-step retention factors over >= 2 steps."""
    if len(steps) < 2:
        raise CompositionRefused([f"NOT_MULTI_STEP: {len(steps)} step(s); a composite needs >= 2"])
    out = 1.0
    for s in steps:
        out *= float(one_step(s))
    return out


def check_fold_integrity(composites: Sequence[CompositeRow], singles: Sequence[SingleStepRow],
                         assignment: Mapping[str, str]) -> list[str]:
    """Constituent single-step rows in another fold than their composite's (same component)."""
    role_of_comp: dict[str, set[str]] = {}
    for c in composites:
        if c.row_id in assignment:
            role_of_comp.setdefault(c.component, set()).add(assignment[c.row_id])
    bad = [s.row_id for s in singles
           if s.row_id in assignment and s.component in role_of_comp
           and role_of_comp[s.component] != {assignment[s.row_id]}]
    return [f"CONSTITUENT_IN_OTHER_FOLD: {len(bad)} single-step row(s) share a lineage component "
            "with a composite in another fold"] if bad else []


def assert_fold_integrity(composites: Sequence[CompositeRow], singles: Sequence[SingleStepRow],
                          assignment: Mapping[str, str]) -> None:
    found = check_fold_integrity(composites, singles, assignment)
    if found:
        raise CompositionRefused(found)


def _real(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def composition_consistency(rows: Sequence[CompositeRow], *, one_step: Callable[[str], float],
                            lookup: Callable[[CompositeRow], float], rho: float, c_floor: float,
                            circularity: Mapping[str, str]) -> dict[str, Any]:
    """G34a verdict on composite rows; refuses with every blocker collected."""
    blockers: list[str] = []
    if not _real(rho) or rho < 0:
        blockers.append("RHO_INVALID: a finite pre-registered rho >= 0 is required (no default)")
    if not _real(c_floor) or not 0 <= c_floor <= 1:
        blockers.append("C_FLOOR_INVALID: a pre-registered coverage floor in [0, 1] is required (no default)")
    if not rows:
        blockers.append("NO_COMPOSITE_ROWS: nothing to test")
    sources = sorted({r.source_family for r in rows})
    for s in sources:
        status = circularity.get(s)
        if status not in CIRCULARITY_STATUSES:
            blockers.append(f"CIRCULARITY_UNCHECKED: source {s!r} has no 34a.0 circularity status")
        elif status == "UNKNOWN":
            blockers.append(f"CIRCULARITY_UNCHECKED: source {s!r} circularity is UNKNOWN (34a.0 not done)")
    short = [r.row_id for r in rows if len(r.steps) < 2]
    if short:
        blockers.append(f"NOT_MULTI_STEP: {len(short)} row(s) have fewer than 2 steps")
    if blockers:
        raise CompositionRefused(blockers)
    excluded = sorted(s for s in sources if circularity[s] == "DERIVED_MULTIPLICATIVE")
    used = [r for r in rows if r.source_family not in excluded]
    if not used:
        raise CompositionRefused(["NO_COMPOSITE_ROWS: every source is excluded by 34a.0"])
    e_chain = sum(abs(chain_prediction(r.steps, one_step) - r.observed) for r in used) / len(used)
    e_lookup = sum(abs(float(lookup(r)) - r.observed) for r in used) / len(used)
    if all(r.interval is not None for r in used):
        coverage: Optional[float] = sum(1 for r in used if r.interval[0] <= r.observed <= r.interval[1]) / len(used)
    else:
        coverage = None
    error_ok = e_chain <= (1 + rho) * e_lookup
    if coverage is None:
        verdict = "UNKNOWN"
    else:
        verdict = "CHAIN_CONSISTENT" if error_ok and coverage >= c_floor else "CHAIN_INCONSISTENT"
    return {"status": STATUS, "labels": list(LABELS), "verdict": verdict, "e_chain": e_chain,
            "e_lookup": e_lookup, "error_criterion_met": error_ok, "coverage": coverage, "rho": float(rho),
            "c_floor": float(c_floor), "n_rows": len(used), "n_components": len({r.component for r in used}),
            "excluded_sources": excluded}
