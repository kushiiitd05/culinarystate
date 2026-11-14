"""D-116 item 4: composition-aware applicability on top of the frozen router (existing enums only).

`composition_route` takes one `router_demo.route_text` item plus the food's C_t v1.2 context and returns a new dict:
- context has added SALT / ACID / LIPID (TRUE)         -> CONTEXT_MISMATCH; the plain evidence is kept as near evidence
- context UNKNOWN on an axis and nothing TRUE           -> UNKNOWN (COMPOSITION_UNKNOWN), never DIRECT
- merged only with plain water (no other co-member)      -> the ungated route is restored (same context as "boil in water")
- otherwise                                              -> the frozen route is kept unchanged
EVD rows here (USDA R6 etc.) record no added salt/acid/lipid, so a stated addition is a context difference.

`suggest_context` adds the most probable unstated context, never as fact:
- INGREDIENT_LIST_UNPLACED: a SALT/ACID/LIPID ingredient is listed but appears in no step (recipe-level evidence)
- CORPUS_PRIOR: share of events with the same (food, process) where the axis is stated TRUE (PROPOSED cut-offs)
`scenario_route` turns a suggestion into a SCENARIO item (existing enum) with the near evidence attached.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

CONTEXT_MISMATCH = "CONTEXT_MISMATCH"
AXES = ("salt", "acid", "lipid")
WATER_ONLY = frozenset({"ING-000109"})
# PROPOSED cut-offs for the corpus prior (pending review): PROBABLE p >= 0.5, POSSIBLE p >= 0.2, both with n >= 30.
PRIOR_MIN_N, PROBABLE_P, POSSIBLE_P = 30, 0.5, 0.2


def _evidence(item: Mapping[str, Any]) -> list:
    return list(item.get("evidence") or item.get("evidence_not_applied") or [])


def composition_route(item: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(item)
    added = [a.upper() for a in AXES if ctx[f"{a}_present"].get("v") is True]
    unknown = [a.upper() for a in AXES if ctx[f"{a}_present"].get("v") is None]
    members = frozenset(ctx["context_members"].get("v") or ())
    if added:
        out.update(route=CONTEXT_MISMATCH, near_evidence=_evidence(item), evidence=[],
                   composition_reasons=["COMPOSITION_CONTEXT_DIFFERS:" + "+".join(added), "EVD_NO_ADDED_CONTEXT_RECORDED"])
    elif unknown:
        out.update(route="UNKNOWN", near_evidence=_evidence(item), evidence=[],
                   composition_reasons=["COMPOSITION_UNKNOWN:" + "+".join(unknown)])
    elif members <= WATER_ONLY and item.get("route_ungated") == "DIRECT" and item.get("route") != "DIRECT":
        out.update(route="DIRECT", evidence=_evidence(item), composition_reasons=["COMPOSITION_COMPATIBLE_WATER_ONLY"])
    else:
        out["composition_reasons"] = ["COMPOSITION_NO_CHANGE"]
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
