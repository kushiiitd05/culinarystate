"""Inspectable condition-compatibility vector between a query context and an evidence row (plan AO2).

Each axis returns MATCH / NEAR / MISMATCH / UNKNOWN. UNKNOWN on either side is never a mismatch
(proposal: "unknown is not a mismatch"). The scalar score is only for ranking; the vector is kept.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

AXES = ("matrix", "state", "process", "time", "temperature", "medium", "target", "basis", "tier")
WEIGHTS = {"matrix": 3.0, "process": 3.0, "target": 3.0, "state": 1.0, "time": 1.0, "temperature": 1.0,
           "medium": 1.0, "basis": 0.5, "tier": 0.5}
VALUE = {"MATCH": 1.0, "NEAR": 0.5, "UNKNOWN": 0.25, "MISMATCH": 0.0}
TIER_RANK = {"E1": 1.0, "E2": 0.9, "E3": 0.8, "E4": 0.8, "E5": 0.3, "E6": 0.1, "E7": 0.05}


@dataclass(frozen=True)
class Query:
    ingredient_id: str | None = None
    ingredient_name: str | None = None
    ingredient_parents: frozenset = field(default_factory=frozenset)   # ING ids of FORM_OF/VARIANT_OF parents
    food_group: str | None = None
    state: str | None = None
    process_id: str | None = None
    process_family: str | None = None
    time_min: tuple[float, float] | None = None
    temperature_c: tuple[float, float] | None = None
    medium: str | None = None
    target: str | None = None
    basis: str | None = None


def _interval(q: tuple[float, float] | None, ev: dict | None, near_frac: float = 0.5) -> str:
    if q is None or not ev or ev.get("status") not in ("MEASURED", "RANGE"):
        return "UNKNOWN"
    lo, hi = (ev["value"], ev["value"]) if ev["status"] == "MEASURED" else (ev["low"], ev["high"])
    if lo <= q[1] and q[0] <= hi:
        return "MATCH"
    gap = min(abs(lo - q[1]), abs(q[0] - hi))
    return "NEAR" if gap <= near_frac * max(abs(q[1]), 1) else "MISMATCH"


def compatibility(q: Query, e: dict, cond: dict | None, proc_family: dict[str, str]) -> dict:
    m, p, t = e["matrix"], e["process"], e["target"]
    v = {}
    if q.ingredient_id and m.get("ingredient_id"):
        v["matrix"] = "MATCH" if q.ingredient_id == m["ingredient_id"] else (
            "NEAR" if m["ingredient_id"] in q.ingredient_parents else "MISMATCH")
    elif q.ingredient_name and re.search(rf"\b{re.escape(q.ingredient_name.lower())}\b", (m.get("raw_name") or "").lower()):
        v["matrix"] = "NEAR"                 # named inside a group row ("vegetables, such as broccoli"): group-level evidence
    elif q.food_group and m.get("food_group"):
        v["matrix"] = "NEAR" if q.food_group.split()[0].lower() in m["food_group"].lower() else "UNKNOWN"
    else:
        v["matrix"] = "UNKNOWN"
    v["state"] = "UNKNOWN" if not (q.state and m.get("initial_state")) else (
        "MATCH" if q.state.lower() in m["initial_state"].lower() else "NEAR")
    pid = p.get("process_id")
    if q.process_id and pid:
        same_fam = proc_family.get(q.process_id) and proc_family.get(q.process_id) == proc_family.get(pid)
        v["process"] = "MATCH" if pid == q.process_id or q.process_id in (p.get("step_process_ids") or []) else (
            "NEAR" if same_fam else "MISMATCH")
    else:
        v["process"] = "UNKNOWN"
    c = cond or {}
    v["time"] = _interval(q.time_min, c.get("duration"))
    temps = [x["value"] for x in c.get("temperatures", []) if x["value"].get("unit") == "degC"]
    v["temperature"] = _interval(q.temperature_c, temps[0] if temps else None)
    med = c.get("medium") or p.get("medium")
    v["medium"] = "UNKNOWN" if not (q.medium and med) else ("MATCH" if q.medium.lower() in med.lower() else "MISMATCH")
    tgt = t.get("raw_name", "").lower()
    v["target"] = "UNKNOWN" if not q.target else ("MATCH" if q.target.lower() in tgt or tgt in q.target.lower()
                                                  else "MISMATCH")
    v["basis"] = "UNKNOWN" if not q.basis else ("MATCH" if q.basis == t.get("basis") else "NEAR")
    v["tier"] = e["tier"]
    score = sum(WEIGHTS[a] * (TIER_RANK.get(v[a], 0) if a == "tier" else VALUE[v[a]]) for a in AXES)
    hard_mismatch = any(v[a] == "MISMATCH" for a in ("matrix", "process", "target"))
    return {"vector": v, "score": round(score / sum(WEIGHTS.values()), 4), "hard_mismatch": hard_mismatch}
