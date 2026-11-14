"""RAG packet v2 (SSOT v16 CR-57..61, design subset): the LLM gets the explicit State v2, not an opaque vector.

`packet(state, target)` -> dict with the food/lot, event, lineage, C/Q/Y cells (value+basis or UNKNOWN+reason),
candidate and near evidence, per-axis compatibility (ingredient, process, salt, acid, lipid), the route and the
ALLOWED CLAIM. `render(packet)` -> the text block given to the LLM. `SYSTEM_RULES` is the fixed instruction.
The allowed claim is decided here, deterministically; the LLM may explain it but never upgrade it.
"""
from __future__ import annotations

from typing import Any, Mapping

ALLOWED = {
    "DIRECT": "NUMERIC_FROM_CITED_EVIDENCE_ONLY",
    "SCENARIO": "SCENARIO_LABELLED_ONLY",
    "QUALITATIVE": "QUALITATIVE_DIRECTION_ONLY",
    "CONTEXT_MISMATCH": "QUALITATIVE_ONLY_NO_NUMERIC_TRANSFER",
    "UNKNOWN_WITH_NEAR": "QUALITATIVE_ONLY_NO_NUMERIC_TRANSFER",
    "UNKNOWN": "ABSTAIN",
}
SYSTEM_RULES = """You explain a cooking-state record. Rules:
1. Use only the values in the packet. Never produce a number that is not in the packet's evidence.
2. Obey ALLOWED_CLAIM exactly: ABSTAIN = say it is not known and why; QUALITATIVE_ONLY_NO_NUMERIC_TRANSFER = you may
   name the near evidence but must say its number cannot be transferred and why; NUMERIC_FROM_CITED_EVIDENCE_ONLY =
   give the number with its evidence id; SCENARIO_LABELLED_ONLY = say it is a scenario, not a measurement.
3. Every UNKNOWN stays UNKNOWN; say its reason in plain words.
4. Cite evidence ids. Do not change routes, compatibility or provenance."""


def _cell(c: Mapping[str, Any] | None) -> str:
    if not c:
        return "UNKNOWN (no cell)"
    v = c.get("v")
    if v is None:
        return f"UNKNOWN ({c.get('u')})"
    return f"{v} [{c.get('b')}]"


def packet(state: Mapping[str, Any], target: str) -> dict[str, Any]:
    y = state["Y"]
    route = (y.get(f"{target}_route") or {}).get("v") or "UNKNOWN"
    ev = y.get(f"{target}_evidence") or {}
    applied = ev.get("b") == "APPLIED"
    near = [] if applied or ev.get("v") is None else list(ev["v"])
    compat = (y.get(f"{target}_compat") or {}).get("v") or {}
    frozen = (y.get(f"{target}_frozen_reasons") or {}).get("v") or []
    key = "UNKNOWN_WITH_NEAR" if route == "UNKNOWN" and near else route
    per_axis = {"ingredient": "MATCH" if (applied or near) else "NO_EVIDENCE_ROW",
                "process": "MATCH" if (applied or near) else "NO_EVIDENCE_ROW",
                **{a: compat.get(a, "NOT_EVALUATED") for a in ("salt", "acid", "lipid")}}
    if "MERGED_LOT_CONTEXT" in frozen:
        per_axis["lot"] = "MERGED_LOT_NOT_IN_SOURCE"
    return {"food": state["food"], "step": state["step"], "action": state["action"], "target": target,
            "structure": {k: _cell(v) for k, v in state["G"].items()},
            "composition": {k: _cell(v) for k, v in state["C"].items() if k not in ("member_composition",)},
            "physics": {k: _cell(v) for k, v in state["Q"].items()},
            "evidence_applied": list(ev.get("v") or []) if applied else [],
            "near_evidence": near, "compatibility": per_axis, "route": route,
            "route_reasons": _cell(y.get(f"{target}_route")), "frozen_router_reasons": frozen,
            "formula": _cell(y.get("vitc_formula_retention_typical")) if target == "vitc" else "n/a",
            "allowed_claim": ALLOWED.get(key, "ABSTAIN")}


def render(p: Mapping[str, Any]) -> str:
    lines = [f"FOOD LOT: {p['food']} | STEP {p['step']}: {p['action']} | TARGET: {p['target']}"]
    for blk in ("structure", "composition", "physics"):
        lines.append(f"{blk.upper()}:")
        lines += [f"  {k}: {v}" for k, v in p[blk].items()]
    lines += [f"EVIDENCE APPLIED: {p['evidence_applied'] or 'none'}", f"NEAR EVIDENCE: {p['near_evidence'] or 'none'}",
              "COMPATIBILITY: " + ", ".join(f"{k}={v}" for k, v in p["compatibility"].items()),
              f"ROUTE: {p['route']} ({p['route_reasons']}); frozen reasons: {p['frozen_router_reasons']}",
              f"FORMULA: {p['formula']}", f"ALLOWED_CLAIM: {p['allowed_claim']}"]
    return "\n".join(lines)
