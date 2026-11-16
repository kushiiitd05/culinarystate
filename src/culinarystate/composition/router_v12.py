"""D-116 item 4 (v1.2.1): composition-aware applicability on top of the frozen router (existing enums only).

Per axis (salt, acid, lipid), the query context (C_t v1.2: TRUE / NO_RECOGNIZED_MARKER / UNKNOWN) is compared with
the evidence row's own context (`source_context`: PRESENT / ABSENT / UNKNOWN_IN_SOURCE). ACTIVE EVD rows record no salt
or acid; lipid is PRESENT only for an oil medium or an oil/fat process name. Nothing is recorded ABSENT.

  query TRUE   x source PRESENT            -> MATCH
  query TRUE   x source ABSENT             -> MISMATCH
  query TRUE   x source UNKNOWN_IN_SOURCE  -> UNCONFIRMED
  query NO_REC x source PRESENT            -> UNCONFIRMED (the query may carry an unrecognised fat)
  query NO_REC x source ABSENT / UNKNOWN   -> NO_STATED_DIFFERENCE
  query UNKNOWN                             -> QUERY_UNKNOWN
Item route: any MISMATCH -> CONTEXT_MISMATCH; else any UNCONFIRMED or QUERY_UNKNOWN -> UNKNOWN; else the frozen route
unchanged (no restore of a gated route). Evidence is kept as near evidence whenever the route is lowered.

`suggest_context` adds the most probable unstated context, never as fact:
- INGREDIENT_LIST_UNPLACED: a SALT/ACID/LIPID ingredient is listed but appears in no step (recipe-level evidence)
- CORPUS_PRIOR: share of events with the same (food, process) where the axis is stated TRUE (PROPOSED cut-offs)
`scenario_route` turns a suggestion into a SCENARIO item (existing enum) with the near evidence attached.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Mapping, Optional

CONTEXT_MISMATCH = "CONTEXT_MISMATCH"
AXES = ("salt", "acid", "lipid")
PRESENT, ABSENT, UNKNOWN_IN_SOURCE = "PRESENT", "ABSENT", "UNKNOWN_IN_SOURCE"
_LIPID_PROC = re.compile(r"\b(?:oil|fat|fried|fry|frying|butter)\b", re.IGNORECASE)
# PROPOSED cut-offs for the corpus prior (pending review): PROBABLE p >= 0.5, POSSIBLE p >= 0.2, both with n >= 30.
PRIOR_MIN_N, PROBABLE_P, POSSIBLE_P = 30, 0.5, 0.2


def _evidence(item: Mapping[str, Any]) -> list:
    return list(item.get("evidence") or item.get("evidence_not_applied") or [])


def source_context(evd: Optional[Mapping[str, Any]]) -> dict[str, str]:
    """Context the evidence row itself records, per axis."""
    proc = (evd or {}).get("process") or {}
    lipid = PRESENT if (proc.get("medium") == "oil" or _LIPID_PROC.search(str(proc.get("raw_name") or ""))) \
        else UNKNOWN_IN_SOURCE
    return {"salt": UNKNOWN_IN_SOURCE, "acid": UNKNOWN_IN_SOURCE, "lipid": lipid}


def axis_compat(q: Any, s: str) -> str:
    if q is None:
        return "QUERY_UNKNOWN"
    if q is True:
        return {PRESENT: "MATCH", ABSENT: "MISMATCH"}.get(s, "UNCONFIRMED")
    return "UNCONFIRMED" if s == PRESENT else "NO_STATED_DIFFERENCE"


def composition_route(item: Mapping[str, Any], ctx: Mapping[str, Any],
                      evd_by_id: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    out = dict(item)
    ev = _evidence(item)
    rows = [evd_by_id.get(e.get("evd_id")) for e in ev] or [None]
    q = {a: ctx[f"{a}_present"].get("v") for a in AXES}
    per_row = [{a: axis_compat(q[a], source_context(r)[a]) for a in AXES} for r in rows]
    best = min(per_row, key=lambda c: (sum(v == "MISMATCH" for v in c.values()),
                                       sum(v in ("UNCONFIRMED", "QUERY_UNKNOWN") for v in c.values())))
    out["composition_compat"] = best
    tag = lambda kinds: "+".join(a.upper() for a in AXES if best[a] in kinds)
    if tag({"MISMATCH"}):
        out.update(route=CONTEXT_MISMATCH, near_evidence=ev, evidence=[],
                   composition_reasons=["COMPOSITION_MISMATCH:" + tag({"MISMATCH"})])
    elif tag({"UNCONFIRMED", "QUERY_UNKNOWN"}):
        reasons = []
        if tag({"UNCONFIRMED"}):
            reasons.append("COMPOSITION_UNCONFIRMED_IN_SOURCE:" + tag({"UNCONFIRMED"}))
        if tag({"QUERY_UNKNOWN"}):
            reasons.append("COMPOSITION_UNKNOWN_IN_QUERY:" + tag({"QUERY_UNKNOWN"}))
        out.update(route="UNKNOWN", near_evidence=ev, evidence=[], composition_reasons=reasons)
    else:
        out["composition_reasons"] = ["COMPOSITION_NO_STATED_DIFFERENCE"]
    return out


def unplaced_from_list(list_ings: Iterable[str], step_ings: Iterable[str], markers: Mapping[str, frozenset]) -> dict:
    """axis -> ingredient ids listed in the recipe but never in a step lineage."""
    unplaced = set(list_ings) - set(step_ings)
    return {a: sorted(i for i in unplaced if a.upper() in markers.get(i, ())) for a in AXES}


def prior_label(n: int, k: int) -> Optional[str]:
    if n < PRIOR_MIN_N:
        return None
    p = k / n
    return "PROBABLE" if p >= PROBABLE_P else "POSSIBLE" if p >= POSSIBLE_P else None


def suggest_context(ctx: Mapping[str, Any], unplaced: Mapping[str, list], prior: Optional[Mapping[str, int]]) -> dict:
    """Per axis that is not stated TRUE: a suggestion with its basis, or None."""
    out = {}
    for a in AXES:
        if ctx[f"{a}_present"].get("v") is True:
            out[a] = None
            continue
        if unplaced.get(a):
            out[a] = {"label": "SUGGESTED", "basis": "INGREDIENT_LIST_UNPLACED", "members": unplaced[a]}
            continue
        if prior:
            lab = prior_label(prior.get("n", 0), prior.get(a, 0))
            if lab:
                out[a] = {"label": lab, "basis": "CORPUS_PRIOR", "k": prior.get(a, 0), "n": prior["n"]}
                continue
        out[a] = None
    return out


def scenario_route(item: Mapping[str, Any], suggestion: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    axes = [a.upper() for a, s in suggestion.items() if s]
    if not axes:
        return None
    return {**dict(item), "route": "SCENARIO", "evidence": [], "near_evidence": _evidence(item),
            "scenario_context": {a: s for a, s in suggestion.items() if s},
            "composition_reasons": ["SCENARIO_UNSTATED_CONTEXT:" + "+".join(axes), "NOT_STATED_IN_TEXT"]}
