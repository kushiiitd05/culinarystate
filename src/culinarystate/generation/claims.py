"""C17 claim checker: numeric claims must be cited and match the cited evidence (SSOT §257B C17; UCR, DEL-4).

A numeric claim = a percentage or a decimal fraction (0.x / 1.x; a bare "1" is a count, not a claim);
durations/temperatures/step numbers are not claims here. Supported iff it cites ≥ 1 packet row ([EVD-…] ids in
the same sentence, or in a citation-only fragment right after it) and the value is within tolerance of one cited
row's retention (fraction or % scale). Citations to ids outside the packet are
fabricated. UCR = unsupported / numeric claims.
"""
from __future__ import annotations

import re

from culinarystate.retrieval.retriever import EvidencePacket

VERSION = "claims@0.2"
CIT = re.compile(r"EVD-\d{6}(?!\d)")                # any well-formed id, incl. "[EVD-1, EVD-2]" lists
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(%|percent)|(?<![\w.\d])(0?\.\d+|1\.\d+)(?![\w%.\d])(?!\s*(?:min|hour|°|degree|step))")
NOT_CLAIM = re.compile(r"\b(?:step|minutes?|mins?|hours?|°|degrees?|cups?|tbsp|tsp|grams?|g\b|ml\b)", re.I)
TOL = 0.03
SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
CIT_ONLY = re.compile(r"^(?:[\[\](),;\s]|EVD-\d{6}(?!\d))+[.]?$")


def row_value(row: dict) -> float | None:
    """Retention factor on the fraction scale (MEASURED value or CENSORED limit); None otherwise."""
    rf = (row.get("derived") or {}).get("retention_factor") or {}
    v = rf.get("value") if rf.get("status") == "MEASURED" else (rf.get("censor") or {}).get("limit")
    return None if v is None else v * (0.01 if rf.get("unit") == "%" else 1.0)


def _row_values(p: EvidencePacket) -> dict:
    return {h.evd_id: v for h in p.direct + p.near if (v := row_value(h.row)) is not None}


def split_sentences(text: str) -> list[str]:
    """Sentence split; a citation-only fragment ("... 55%. [EVD-000001]") belongs to the sentence before it."""
    out = []
    for s in (x.strip() for x in SPLIT.split(text or "")):
        if s and CIT_ONLY.match(s) and out:
            out[-1] = f"{out[-1]} {s}"
        elif s:
            out.append(s)
    return out


def check_claims(text: str, p: EvidencePacket) -> dict:
    vals, packet_ids = _row_values(p), {h.evd_id for h in p.direct + p.near}
    claims = []
    for sent in split_sentences(text):
        cites = CIT.findall(sent)
        for m in NUM.finditer(sent):
            if NOT_CLAIM.match(sent[m.end():m.end() + 10].strip() or "x") and not m.group(2):
                continue
            v = float(m.group(1)) / 100 if m.group(2) else float(m.group(3))
            if not cites:
                claims.append({"value": v, "supported": False, "reason": "UNCITED"})
                continue
            ok = any(abs(vals.get(c, 99) - v) <= TOL for c in cites)
            claims.append({"value": v, "supported": ok, "cites": cites,
                           "reason": None if ok else "VALUE_NOT_IN_CITED_EVIDENCE"})
    bad = sum(not c["supported"] for c in claims)
    return {"version": VERSION, "numeric_claims": len(claims), "unsupported": bad,
            "ucr": round(bad / len(claims), 4) if claims else None,
            "fabricated_citations": sorted(set(CIT.findall(text or "")) - packet_ids), "claims": claims}
