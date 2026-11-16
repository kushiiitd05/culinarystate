"""Honest evidence label for an answer (S176, L-ROUTER): what the answer is actually built from.

Before S176 the page showed a green "Answered from data" badge for every ANSWER, including answers whose numbers or
directions came from similar or unrelated foods or from a different process. The label is derived from the evidence
packet itself (never from the answer text):

  MEASURED_FOR_FOOD   class DIRECT or INTERPOLATED, numbers shown, every pooled row is for the ASKED food (compat
                      match EXACT) and measured under the asked process (EXACT or STEP). The only "from data" label.
  OTHER_PROCESS       rows are for the asked food but under another process of the same family
  SIMILAR_FOODS       rows are for related foods (parent / child / sibling / group row), relation known
  OTHER_FOODS         rows are for foods whose relation to the asked food is unknown (broad rows)
  DIRECTION_ONLY      the packet supports a direction only (class QUALITATIVE or precision QUALITATIVE), no numbers
  SOURCES_DISAGREE    the pooled rows conflict (class CONFLICT)

A mixed pool takes the weakest basis. A COMPARE answer takes the weakest option. Codes only plus fixed display
strings; no recipe text. The EVD ids of the asked food are listed separately from the other rows.
"""
from __future__ import annotations

from typing import Any, Mapping

VERSION = "evidence_label@0.1"
MEASURED, OTHER_PROCESS, SIMILAR, OTHER_FOODS, DIRECTION, CONFLICT = (
    "MEASURED_FOR_FOOD", "OTHER_PROCESS", "SIMILAR_FOODS", "OTHER_FOODS", "DIRECTION_ONLY", "SOURCES_DISAGREE")
STRENGTH = {MEASURED: 5, OTHER_PROCESS: 4, SIMILAR: 3, OTHER_FOODS: 2, DIRECTION: 1, CONFLICT: 0}
BADGE = {MEASURED: "Answered from data", OTHER_PROCESS: "Same food, different process", SIMILAR: "Similar foods only",
         OTHER_FOODS: "Other foods only", DIRECTION: "Direction only", CONFLICT: "Sources disagree"}
BADGE_COMPARE = {MEASURED: "Compared from data", OTHER_PROCESS: "Compared: different process",
                 SIMILAR: "Compared: similar foods only", OTHER_FOODS: "Compared: other foods only",
                 DIRECTION: "Compared: direction only", CONFLICT: "Compared: sources disagree"}
DETAIL = {
    MEASURED: "Numbers come from table rows measured for this food and process.",
    OTHER_PROCESS: "The rows are for this food but under a different cooking process, so they do not measure this one.",
    SIMILAR: "No row measures this exact food; the numbers are from related foods.",
    OTHER_FOODS: "No row measures this food; the rows are for other foods and how they relate to yours is unknown.",
    DIRECTION: "The data only shows which way the nutrient moves, not by how much.",
    CONFLICT: "The rows disagree on the direction, so no single claim is made.",
}
DIRECTION_SUFFIX = {OTHER_PROCESS: " (different process)", SIMILAR: " (similar foods)", OTHER_FOODS: " (other foods)"}
SAME_PROCESS = ("EXACT", "STEP")


def _pool(p: Any) -> list:
    return list(p.direct or p.near)


def option_basis(p: Any, precision: str | None) -> dict[str, Any]:
    """Label of one evidence packet (duck-typed on ``EvidencePacket``)."""
    pool = _pool(p)
    kinds = [((h.compat.get("match") or {}).get("matrix"), (h.compat.get("match") or {}).get("process")) for h in pool]
    exact = [h for h, (m, _) in zip(pool, kinds) if m == "EXACT"]
    if not pool:
        return {"code": None, "basis": None, "evd_ids_asked_food": [], "evd_ids_other": []}
    basis = None
    if p.evidence_class == "CONFLICT" or precision == "REPORT_CONFLICT":
        code = CONFLICT
    else:
        if all(m == "EXACT" for m, _ in kinds):
            basis = MEASURED if all(pr in SAME_PROCESS for _, pr in kinds) else OTHER_PROCESS
        elif any(m == "UNKNOWN" for m, _ in kinds):
            basis = OTHER_FOODS
        else:
            basis = SIMILAR
        numeric = precision in ("QUANTITATIVE", "INTERVAL") and p.evidence_class in ("DIRECT", "INTERPOLATED")
        code = basis if numeric else DIRECTION     # no numbers shown: at most a direction is claimed
    exact_ids = {h.evd_id for h in exact}
    return {"code": code, "basis": basis, "evd_ids_asked_food": [h.evd_id for h in pool if h.evd_id in exact_ids],
            "evd_ids_other": [h.evd_id for h in pool if h.evd_id not in exact_ids]}


def label(decision: Mapping[str, Any], packets: Mapping[str, Any]) -> dict[str, Any] | None:
    """Evidence label for ANSWER / COMPARE decisions; None for every other mode (nothing is claimed from data)."""
    mode = decision.get("mode")
    if mode not in ("ANSWER", "COMPARE"):
        return None
    per = decision.get("per_option") or {}
    keys = [k for k in (per or packets) if k in packets] or list(packets)
    opts = {k: option_basis(packets[k], (per.get(k) or {}).get("precision", decision.get("precision"))) for k in keys}
    coded = {k: v for k, v in opts.items() if v["code"]}
    if not coded:
        return None
    weakest = min((v["code"] for v in coded.values()), key=STRENGTH.__getitem__)
    badge = (BADGE_COMPARE if mode == "COMPARE" else BADGE)[weakest]
    if weakest == DIRECTION:                   # say what the direction rests on
        bases = [v["basis"] for v in coded.values() if v["code"] == DIRECTION and v["basis"]]
        badge += DIRECTION_SUFFIX.get(min(bases, key=STRENGTH.__getitem__), "") if bases else ""
    return {"version": VERSION, "code": weakest, "badge": badge, "detail": DETAIL[weakest],
            "from_data": weakest == MEASURED,
            "options": {k: v["code"] for k, v in coded.items()},
            "evd_ids_asked_food": sorted({i for v in coded.values() for i in v["evd_ids_asked_food"]}),
            "evd_ids_other": sorted({i for v in coded.values() for i in v["evd_ids_other"]})}
