"""SSOT §39 query router: intent -> branch (S171, D-075 M4). Rule-based; no cue -> UNKNOWN, never a guess.

S176: a SAFETY branch (doneness, pathogens, safe temperature, storage safety) is checked first and abstains with a
referral to official guidance (``decision/safety.py``); it never produces a number.

Branches (§39): METADATA (exact food metadata -> structured EVD/composition lookup), RELATIONSHIP (food graph:
substitutes, pairings), SEMANTIC (recipe-similarity retrieval), TRANSFORMATION (process model + evidence: the
23a router demo and EVD packets), MULTIMODAL (vision/audio: not built, so ABSTAIN_UNSUPPORTED). Cues are checked in a
fixed order; the existing relevance gate and intent are carried along for the downstream policy.
"""
from __future__ import annotations

import re

from culinarystate.decision import relevance as RV
from culinarystate.decision import safety as SF

VERSION = "query_router_rules@0.2"      # S176: SAFETY branch (explicit abstention) before every other cue
_PROC = RV._P
_TARGET = SF.NUTRIENT_CUE
_EFFECT = r"\b(?:destroy\w*|lose|loss|losses|retain\w*|retention|keep|kept|degrad\w*|change\w*|affect\w*|reduce\w*)\b"
CUES = (
    ("MULTIMODAL", r"\b(?:photo|picture|image|video|camera|listen|sound|sizzl\w*|audio|look at this)\b"),
    ("SEMANTIC", r"\brecipes? (?:like|similar to)\b|\bsimilar to\b.*\brecipe|\bfind (?:me )?(?:a )?recipes?\b|"
                 r"\bshow me recipes?\b|\brecipes? (?:for|with)\b"),
)
METADATA = (r"\b(?:content of|how many calories|calories in|nutrition(?:al)? (?:facts|value)|how much \w+(?: \w+)? "
            r"(?:is|are) in|composition of)\b")
RELATIONSHIP = r"\binstead of\b|\bsubstitut\w*|\bswap\b|\breplace\w*\b|\bpair\w* (?:well )?with\b|\bgoes? with\b"
ACTIONS = {"METADATA": "STRUCTURED_LOOKUP", "RELATIONSHIP": "GRAPH_LOOKUP", "SEMANTIC": "RECIPE_RETRIEVAL",
           "TRANSFORMATION": "PROCESS_MODEL_PLUS_EVIDENCE", "MULTIMODAL": "ABSTAIN_UNSUPPORTED",
           "SAFETY": "ABSTAIN_REFER_OFFICIAL_FOOD_SAFETY",
           "UNKNOWN": "ASK_CLARIFY", "MALFORMED": "ASK_CLARIFY"}


def _branch(q: str, gate: dict) -> tuple[str, str]:
    if SF.is_safety(q):                 # S176: a safety question is never answered, whatever else it mentions
        return "SAFETY", "FOOD_SAFETY_CUE"
    for name, pat in CUES:
        if re.search(pat, q):
            return name, name
    has_proc = re.search(rf"\b{_PROC}", q) is not None
    if has_proc and (re.search(_TARGET, q) or re.search(_EFFECT, q)):
        return "TRANSFORMATION", "PROCESS_AND_TARGET_OR_EFFECT"
    if gate["relevant"] is True and (has_proc or gate["reason"] not in ("SUBSTITUTION",)):
        return "TRANSFORMATION", f"GATE_{gate['reason']}"
    if re.search(METADATA, q):
        return "METADATA", "METADATA_CUE"
    if re.search(RELATIONSHIP, q):
        return "RELATIONSHIP", "RELATIONSHIP_CUE"
    return "UNKNOWN", "NO_CUE"


def route(query: str) -> dict:
    q = re.sub(r"\s+", " ", (query or "").lower()).strip()
    if not q:
        return {"branch": "MALFORMED", "reason": "EMPTY", "action": ACTIONS["MALFORMED"], "supported": False,
                "needs_process_model": False, "relevance": None, "intent": None, "version": VERSION, "raw": query}
    gate = RV.relevance_gate(q)
    branch, reason = _branch(q, gate)
    return {"branch": branch, "reason": reason, "action": ACTIONS[branch], "supported": branch not in ("MULTIMODAL", "SAFETY"),
            "needs_process_model": branch == "TRANSFORMATION",
            "relevance": {k: gate[k] for k in ("relevant", "reason", "cue")}, "intent": RV.intent(q),
            "version": VERSION, "raw": query}
