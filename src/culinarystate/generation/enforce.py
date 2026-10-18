"""Post-hoc enforcement of a generated answer (C16/C17, SSOT §242.7 precision cap, §257B.17).

Sentence-level filter over LLM output: drop sentences with numbers not matching their cited packet rows, citations
outside the packet, non-evidence citations like "[1]", and any numeric claim when the decision's cap forbids numbers.
Every removal carries a machine-readable reason. If nothing survives, the deterministic verbaliser answers instead.
"""
from __future__ import annotations

import re

from culinarystate.generation.claims import CIT, check_claims, split_sentences
from culinarystate.generation.verbalize import NO_NUMBERS, verbalize
from culinarystate.retrieval.retriever import EvidencePacket

VERSION = "enforce@0.1"
NUM_BRACKET = re.compile(r"\[\d+(?:,\s*\d+)*\]")
MALFORMED = re.compile(r"\[\s*EVD(?!-\d{6}(?!\d))[^\]]*\]", re.I)     # "[EVD-1]", "[EVD-0000011]"


def number_cap(d: dict) -> bool:
    """True when the decision allows no numeric claims at all."""
    if d.get("mode") in ("ASK", "ABSTAIN", "RECOVER", "DIAGNOSE") or d.get("route") in ("DIAGNOSIS", "RECIPE_STATE"):
        return True
    if d.get("mode") in ("COMPARE", "RECOMMEND"):
        return all((o or {}).get("precision") in NO_NUMBERS for o in (d.get("per_option") or {}).values())
    return d.get("precision") in NO_NUMBERS or d.get("precision") is None


def _union(packets: dict[str, EvidencePacket]) -> EvidencePacket:
    direct = [h for p in packets.values() for h in p.direct]
    near = [h for p in packets.values() for h in p.near]
    return EvidencePacket("", None, "UNION", direct, near)


def enforce(text: str, d: dict, packets: dict[str, EvidencePacket]) -> dict:
    pk, cap, kept, removed = _union(packets), number_cap(d), [], []
    ids = {h.evd_id for h in pk.direct + pk.near}
    for s in split_sentences(text):
        c = check_claims(s, pk)
        reason = ("FABRICATED_CITATION" if set(CIT.findall(s)) - ids else
                  "NON_EVIDENCE_CITATION" if NUM_BRACKET.search(s) or MALFORMED.search(s) else
                  "PRECISION_CAP" if cap and c["numeric_claims"] else
                  "UNSUPPORTED_NUMBER" if c["unsupported"] else None)
        if reason:
            removed.append({"sentence": s, "reason": reason})
        else:
            kept.append(s)
    out = " ".join(kept)
    mode_bad = bool(out) and d.get("mode") == "ASK" and "?" not in out          # an ASK must ask
    ok = out and not mode_bad
    return {"version": VERSION, "text": out if ok else verbalize("", d, packets), "fallback": not ok,
            "mode_fallback": mode_bad, "removed": removed}
