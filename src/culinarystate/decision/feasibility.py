"""Feasibility filter: allow / reject / unknown + machine-readable reasons (SSOT §243.3, C11; DEL-5).

Checks run before any utility ranking: input well-formed, process known (else OOD -> UNKNOWN), required tool,
time budget, excluded allergens. A constraint the user did not state is NOT_APPLICABLE, never assumed.
Requirements come from ledgers (`load_requirements`): tools = PROC_USES_TOOL edges with band HIGH and
P(tool | process) ≥ 0.5 (an association, so the reason says "required" only in that sense); durations = the
PROC_TYPICAL_DURATION quantiles; allergens = ALLERGEN.ingredient_ids (authority-backed table, FSSAI).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

VERSION = "feasibility@0.1"
PROC_ID = re.compile(r"^PROC-\d{6}$")


@dataclass(frozen=True)
class Action:
    process_id: str
    ingredient_ids: tuple[str, ...] = ()
    duration_min: float | None = None


@dataclass(frozen=True)
class Constraints:
    available_tools: frozenset | None = None          # None = not stated
    time_budget_min: float | None = None
    excluded_allergens: frozenset = field(default_factory=frozenset)


@dataclass(frozen=True)
class Requirements:
    processes: dict                                    # PROC id -> name
    required_tools: dict                               # PROC id -> frozenset of TOOL ids (any one suffices)
    typical_minutes: dict                              # PROC id -> (p10, p50, p90)
    allergen_of: dict                                  # ING id -> frozenset of ALLERGEN ids


def _c(status: str, reason: str | None = None, detail=None) -> dict:
    return {"status": status, "reason": reason, "detail": detail}


def _tool(a: Action, c: Constraints, r: Requirements) -> dict:
    need = r.required_tools.get(a.process_id)
    if c.available_tools is None or not need:
        return _c("NOT_APPLICABLE", None if need else "NO_TOOL_REQUIREMENT_KNOWN")
    return _c("PASS") if need & c.available_tools else _c("FAIL", "MISSING_REQUIRED_TOOL", sorted(need))


def _time(a: Action, c: Constraints, r: Requirements) -> dict:
    if c.time_budget_min is None:
        return _c("NOT_APPLICABLE")
    if a.duration_min is not None:
        return _c("PASS") if a.duration_min <= c.time_budget_min else _c("FAIL", "DURATION_EXCEEDS_BUDGET", a.duration_min)
    q = r.typical_minutes.get(a.process_id)
    if q is None:
        return _c("UNKNOWN", "DURATION_UNKNOWN")
    return _c("FAIL", "TYPICAL_MEDIAN_EXCEEDS_BUDGET", q) if q[1] > c.time_budget_min else _c("PASS", "TYPICAL_MEDIAN", q)


def _allergen(a: Action, c: Constraints, r: Requirements) -> dict:
    if not c.excluded_allergens:
        return _c("NOT_APPLICABLE")
    hits = {i: sorted(r.allergen_of.get(i, frozenset()) & c.excluded_allergens) for i in a.ingredient_ids}
    hits = {i: h for i, h in hits.items() if h}
    return _c("FAIL", "EXCLUDED_ALLERGEN", hits) if hits else _c("PASS")


def check(a: Action, c: Constraints, r: Requirements) -> dict:
    out = {"version": VERSION, "action": a, "checks": {}}
    if not PROC_ID.match(a.process_id or ""):
        out["checks"]["input"] = _c("FAIL", "MALFORMED_PROCESS_ID", a.process_id)
    elif a.duration_min is not None and a.duration_min < 0:
        out["checks"]["input"] = _c("FAIL", "NEGATIVE_DURATION", a.duration_min)
    else:
        out["checks"]["input"] = _c("PASS")
        known = a.process_id in r.processes
        out["checks"]["process"] = _c("PASS") if known else _c("UNKNOWN", "OOD_PROCESS", a.process_id)
        out["checks"].update(tool=_tool(a, c, r), time=_time(a, c, r), allergen=_allergen(a, c, r))
    st = {x["status"] for x in out["checks"].values()}
    out["decision"] = "REJECT" if "FAIL" in st else "UNKNOWN" if "UNKNOWN" in st else "ALLOW"
    return out


def load_requirements(store) -> Requirements:
    procs = {p["id"]: p["canonical_name"] for p in store.all_latest("PROC") if p["status"] == "ACTIVE"}
    tools: dict = {}
    minutes: dict = {}
    for e in store.all_latest("KGE"):
        if e["status"] != "ACTIVE":
            continue
        if e["predicate"] == "PROC_USES_TOOL" and e["confidence_band"] == "HIGH" and \
                (e.get("association") or {}).get("p_object_given_subject", 0) >= 0.5:
            tools.setdefault(e["subject_id"], set()).add(e["object_id"])
        elif e["predicate"] == "PROC_TYPICAL_DURATION" and e.get("quantiles"):
            q = e["quantiles"]
            minutes[e["subject_id"]] = (q["p10"], q["p50"], q["p90"])
    allergen_of: dict = {}
    for a in store.all_latest("ALLERGEN"):
        for i in a.get("ingredient_ids") or []:
            allergen_of.setdefault(i, set()).add(a["id"])
    return Requirements(procs, {k: frozenset(v) for k, v in tools.items()}, minutes,
                        {k: frozenset(v) for k, v in allergen_of.items()})
