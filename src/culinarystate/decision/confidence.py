"""Confidence vector, evidence-sufficiency mode and output-precision cap (DEL-4; SSOT §242.1, §242.6, §242.7).

The vector keeps interpretable dimensions instead of one score (§242.1). Values are ordinal features in [0, 1] for
a later calibrator (§242.4) — not probabilities. None = unknown / not computed; it is never coerced to 0.
Dimensions filled by other modules (entity link, quantity, state, transition model, OOD) are passed in.
"""
from __future__ import annotations

from collections import Counter

from culinarystate.retrieval.compatibility import TIER_RANK
from culinarystate.retrieval.retriever import EvidencePacket

AXIS_VALUE = {"MATCH": 1.0, "NEAR": 0.5, "MISMATCH": 0.0}           # UNKNOWN -> None
CONDITION_AXES = ("time", "temperature", "medium")
SUFFICIENCY = {"DIRECT": "DIRECT", "INTERPOLATED": "NEAR_PARTIAL", "MODEL_ESTIMATED": "MODEL_INTERPOLATION",
               "QUALITATIVE": "BROAD_QUALITATIVE", "CONFLICT": "CONFLICTING"}
PRECISION = {"DIRECT": "QUANTITATIVE", "NEAR_PARTIAL": "INTERVAL", "MODEL_INTERPOLATION": "INTERVAL",
             "BROAD_QUALITATIVE": "QUALITATIVE", "CONFLICTING": "REPORT_CONFLICT", "IRRELEVANT_EVIDENCE": "ABSTAIN",
             "NO_EVIDENCE": "ABSTAIN"}


def _axis(vec: dict, axis: str) -> float | None:
    return AXIS_VALUE.get(vec.get(axis))


def confidence_vector(p: EvidencePacket, entity: float | None = None, quantity: float | None = None,
                      state: float | None = None, model: float | None = None, ood: bool | None = None) -> dict:
    pool = p.direct or p.near
    top = pool[0] if pool else None
    vec = top.compat["vector"] if top else {}
    cond = [v for a in CONDITION_AXES if (v := _axis(vec, a)) is not None]
    dirs = Counter(h.row["derived"].get("direction") for h in pool
                   if h.row["derived"].get("direction") in ("INCREASE", "DECREASE"))
    return {"retrieval": top.score if top else 0.0, "entity": entity, "quantity": quantity,
            "process": _axis(vec, "process"), "condition": sum(cond) / len(cond) if cond else None,
            "target": _axis(vec, "target"), "source": TIER_RANK.get(top.row["tier"]) if top else None,
            "measurement": _axis(vec, "basis"),
            "extraction": (top.row.get("verification") or {}).get("status") if top else None,
            "agreement": max(dirs.values()) / sum(dirs.values()) if sum(dirs.values()) >= 2 else None,
            "independent_sources": len({h.row.get("independence_group") for h in pool}),
            "state": state, "model": model, "ood": ood}


def sufficiency(p: EvidencePacket) -> str:
    if p.evidence_class in SUFFICIENCY:
        return SUFFICIENCY[p.evidence_class]
    return "IRRELEVANT_EVIDENCE" if (p.direct or p.near) else "NO_EVIDENCE"


def output_precision(mode: str, numeric_target: bool = True) -> str:
    """§242.7: output precision ≤ evidence precision; quantitative only if the target definition supports it."""
    out = PRECISION[mode]
    return "QUALITATIVE" if out == "QUANTITATIVE" and not numeric_target else out
