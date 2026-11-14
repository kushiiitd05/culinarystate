"""Claim Packet (freeze step 4): what may be said, what must be said, what may never be said.

``rag_packet.ALLOWED`` returned one string per route. The Claim Packet carries the seven fields the
freeze names: allowed_claims, required_caveats, forbidden_claims, evidence ids, compatibility,
maximum allowed precision, and UNKNOWN reasons.

Everything is decided deterministically from the compiled evidence. The LLM verbaliser may explain
a packet but can never upgrade it, and the claim verifier (step 5) checks its output against this.
ABSTAIN is always allowed: abstaining is never forbidden.

Maximum allowed precision is read from the evidence as reported — never more decimals than the
source (MP "value as reported + unit + reported precision"). With no applied evidence there is no
precision budget at all, which is ``None``, not zero.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from culinarystate.composition import evidence_compiler as EC

#: Claim kinds. ABSTAIN is in every packet.
NUMERIC = "NUMERIC_FROM_CITED_EVIDENCE"
SCENARIO = "SCENARIO_LABELLED"
QUALITATIVE = "QUALITATIVE_DIRECTION"
ABSTAIN = "ABSTAIN"
NEAR_TRANSFER = "NUMERIC_TRANSFER_FROM_NEAR_EVIDENCE"
UNKNOWN_AS_ZERO = "TREAT_UNKNOWN_AS_ZERO"
UPGRADE_ROUTE = "UPGRADE_ROUTE_OR_COMPATIBILITY"
UNCITED_NUMBER = "ANY_NUMBER_WITHOUT_AN_EVIDENCE_ID"

#: Allowed and forbidden claims per router route. Routes outside this map abstain.
_BY_ROUTE: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "DIRECT": ((NUMERIC, QUALITATIVE, ABSTAIN), (NEAR_TRANSFER, UNKNOWN_AS_ZERO, UPGRADE_ROUTE, UNCITED_NUMBER)),
    "SCENARIO": ((SCENARIO, QUALITATIVE, ABSTAIN), (NUMERIC, NEAR_TRANSFER, UNKNOWN_AS_ZERO, UPGRADE_ROUTE,
                                                    UNCITED_NUMBER)),
    "QUALITATIVE": ((QUALITATIVE, ABSTAIN), (NUMERIC, SCENARIO, NEAR_TRANSFER, UNKNOWN_AS_ZERO, UPGRADE_ROUTE,
                                             UNCITED_NUMBER)),
    "CONTEXT_MISMATCH": ((QUALITATIVE, ABSTAIN), (NUMERIC, SCENARIO, NEAR_TRANSFER, UNKNOWN_AS_ZERO, UPGRADE_ROUTE,
                                                  UNCITED_NUMBER)),
    "UNKNOWN": ((ABSTAIN,), (NUMERIC, SCENARIO, NEAR_TRANSFER, UNKNOWN_AS_ZERO, UPGRADE_ROUTE, UNCITED_NUMBER)),
}

_NUM = re.compile(r"=\s*(-?\d+(?:\.(\d+))?)")


def reported_precision(evidence_values: list[str]) -> int | None:
    """Decimals as reported by the evidence, the tightest cap across rows. None = no budget."""
    decimals = [len(m.group(2) or "") for v in evidence_values if (m := _NUM.search(v))]
    return min(decimals) if decimals else None


def _caveats(compiled: Mapping[str, Any]) -> list[str]:
    """Caveats the verbaliser must state. Built from what is actually UNKNOWN, never boilerplate."""
    out: list[str] = []
    compat = compiled["compatibility"]
    if compiled["unknown_axes"]:
        named = ", ".join(compat[k]["axis"].split(" (")[0] for k in compiled["unknown_axes"])
        out.append(f"STATE_UNKNOWN_ON_AXES: {named}")
    if any(c["status"] == "UNKNOWN" and c["hard_exclusion"] for c in compat.values()):
        out.append("HARD_EXCLUSION_AXIS_IS_UNKNOWN_SO_DIRECT_IS_NOT_SUPPORTED")
    if compiled["near_evidence_ids"]:
        out.append("NEAR_EVIDENCE_MAY_BE_NAMED_BUT_ITS_NUMBER_CANNOT_BE_TRANSFERRED")
    if compiled["frozen_router_reasons"]:
        out.append("FROZEN_ROUTER_REASONS: " + ", ".join(compiled["frozen_router_reasons"]))
    if compiled["route"] == "SCENARIO":
        out.append("SCENARIO_IS_NOT_A_MEASUREMENT")
    return out


def _unknown_reasons(compiled: Mapping[str, Any]) -> dict[str, str]:
    compat = compiled["compatibility"]
    return {k: compat[k]["reason"] or "NO_REASON_RECORDED" for k in compiled["unknown_axes"]}


def claim_packet(state: Mapping[str, Any], target: str, question_kind: str) -> dict[str, Any]:
    """Compile the evidence, then decide what may be said about it. Returns a new dict."""
    compiled = EC.compile_evidence(state, target, question_kind)
    allowed, forbidden = _BY_ROUTE.get(compiled["route"], ((ABSTAIN,), tuple(_BY_ROUTE["UNKNOWN"][1])))
    precision = reported_precision(compiled["evidence_values"]) if NUMERIC in allowed else None

    return {
        "food": compiled["food"], "step": compiled["step"], "action": compiled["action"],
        "target": target, "question_kind": question_kind,
        "route": compiled["route"],
        "allowed_claims": list(allowed),
        "required_caveats": _caveats(compiled),
        "forbidden_claims": list(forbidden),
        "evidence_ids": list(compiled["evidence_ids"]),
        "evidence_values": list(compiled["evidence_values"]),
        "near_evidence_ids": list(compiled["near_evidence_ids"]),
        "compatibility": compiled["compatibility"],
        "selected_axes": list(compiled["selected_axes"]),
        "max_allowed_precision": precision,
        "unknown_reasons": _unknown_reasons(compiled),
    }
