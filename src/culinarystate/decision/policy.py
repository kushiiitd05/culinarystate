"""Decision policy: ANSWER / COMPARE / ASK / DIAGNOSE / RECOVER / RECOMMEND / ABSTAIN (SSOT §243.1; DEL-5).

Order: relevance gate (§7) -> intent -> critical-slot check (ASK; §243.8, simplified VOI: ask only for slots that
change which evidence applies) -> feasibility before utility (§243.3) -> evidence sufficiency + precision cap
(§242.6–242.8). Several feasible options are returned as alternatives in input order, never ranked by hidden
weights (§243.5). Diagnosis/recovery cause language is QUALIFIED: our evidence is not controlled causal evidence
(§243.6). This is the rule baseline (B5 must beat simpler rungs on dev, plan AI8).
"""
from __future__ import annotations

from culinarystate.retrieval.retriever import EvidencePacket

from . import safety as SF
from .comparator import compare
from .confidence import confidence_vector, output_precision, sufficiency
from .ood import cap_precision
from .relevance import intent, relevance_gate

VERSION = "policy_rules@0.1"
CRITICAL = ("ingredient", "process")


def _option(p: EvidencePacket, numeric_target: bool, support: dict | None = None) -> dict:
    mode = sufficiency(p)
    precision, cap = cap_precision(output_precision(mode, numeric_target), support or {})
    return {"sufficiency": mode, "precision": precision, "cap": cap, "support": support,
            "confidence": confidence_vector(p, ood=(support or {}).get("ood")), "disallowed_claims": p.disallowed_claims}


def decide(query: str, packets: dict[str, EvidencePacket], slots: dict, feasibility: dict | None = None,
           numeric_target: bool = True, support: dict | None = None, diagnosis: dict | None = None) -> dict:
    gate = relevance_gate(query)
    base = {"version": VERSION, "query": query, "gate": gate, "intent": intent(query)}
    if base["intent"] == "SAFETY":          # S176: never answered, whichever caller reaches the policy
        return {**base, "mode": "ABSTAIN", "route": "SAFETY", "reason": SF.REASON}
    if gate["reason"] == "OUT_OF_SCOPE":
        return {**base, "mode": "ABSTAIN", "route": "OUT_OF_SCOPE", "reason": "OUT_OF_SCOPE"}
    if gate["relevant"] is False:
        return {**base, "mode": "ANSWER", "route": "RECIPE_STATE", "reason": "LOW_PROCESS_RELEVANCE"}
    if base["intent"] in ("DIAGNOSE", "RECOVER") and diagnosis and diagnosis.get("failure"):
        return _diagnose_or_recover(base, diagnosis)
    missing = [s for s in CRITICAL if not slots.get(s)]
    if missing:
        return {**base, "mode": "ASK", "ask_for": missing, "route": "CLARIFY", "reason": "CRITICAL_SLOT_MISSING"}
    if slots.get("contradictions"):
        return {**base, "mode": "ASK", "ask_for": ["process"], "route": "CLARIFY", "reason": "CONTRADICTORY_SLOTS"}
    if slots.get("needs_target") and not slots.get("target"):    # target decides which evidence applies (§243.8)
        opts = slots.get("target_options")
        if opts is not None and not opts:                         # asking has no decision value: nothing to answer with
            return {**base, "mode": "ABSTAIN", "route": "CLARIFY", "reason": "NO_EVIDENCE_FOR_ANY_TARGET"}
        return {**base, "mode": "ASK", "ask_for": ["target"], "ask_options": list(opts or [])[:5], "route": "CLARIFY",
                "reason": "TARGET_MISSING"}
    feas = feasibility or {}
    rejected = [k for k in packets if feas.get(k, {}).get("decision") == "REJECT"]
    options = {k: _option(p, numeric_target, (support or {}).get(k)) for k, p in packets.items() if k not in rejected}
    usable = [k for k, o in options.items() if o["precision"] != "ABSTAIN"]
    out = {**base, "route": "PROCESS_EFFECT", "per_option": options, "rejected": rejected}
    it = base["intent"]
    if it == "RECOVER":                    # §243.7: cause evidence ≠ recovery evidence; no recovery KB yet
        return {**out, "mode": "RECOVER", "cause_evidence": options, "recovery_options": [],
                "recoverability": "UNKNOWN", "causal_language": "QUALIFIED", "reason": "NO_RECOVERY_EVIDENCE"}
    if it == "RECOMMEND":
        if not options:
            return {**out, "mode": "ABSTAIN", "reason": "NO_FEASIBLE_ACTION"}
        return {**out, "mode": it, "alternatives": list(options), "reason": "FEASIBLE_ALTERNATIVES"}
    if not usable:
        return {**out, "mode": "ABSTAIN", "reason": "INSUFFICIENT_EVIDENCE"}
    if it == "COMPARE":
        return {**out, "mode": "COMPARE", "reason": "PER_OPTION_EVIDENCE",
                "comparison": compare({k: packets[k] for k in options})}
    main = options[usable[0]]
    if it == "DIAGNOSE":
        return {**out, "mode": it, "precision": main["precision"], "causal_language": "QUALIFIED",
                "reason": "CANDIDATE_CAUSES_NEED_VERIFICATION"}
    return {**out, "mode": "ANSWER", "precision": main["precision"], "reason": main["sufficiency"]}


def _diagnose_or_recover(base: dict, dg: dict) -> dict:
    """§243.6–243.7: corroborated candidate causes (qualified) / recovery from its own index; abstain when empty."""
    out = {**base, "route": "DIAGNOSIS", "diagnosis": dg, "causal_language": "QUALIFIED",
           "recoverability": dg.get("recoverability", "UNKNOWN")}
    if base["intent"] == "RECOVER":
        opts = [r["action"] for r in dg.get("recovery", [])]
        if not opts:
            return {**out, "mode": "ABSTAIN", "reason": "NO_CORROBORATED_RECOVERY", "recovery_options": []}
        return {**out, "mode": "RECOVER", "reason": "RECOVERY_INDEX", "recovery_options": opts}
    if not dg.get("causes"):
        return {**out, "mode": "ABSTAIN", "reason": "NO_CORROBORATED_CAUSE"}
    return {**out, "mode": "DIAGNOSE", "reason": "CANDIDATE_CAUSES_VERIFIED_AGAINST_HISTORY",
            "next_observations": dg.get("next_observations", [])}

