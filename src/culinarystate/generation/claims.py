"""C17 claim checker: numeric claims must be cited and match the cited evidence (SSOT §257B C17; UCR, DEL-4).

A numeric claim = a percentage, a decimal/fraction in [0, 1.5], or "N times"; durations/temperatures/step numbers are
not claims here. Supported iff it cites ≥ 1 packet row (nearest following [EVD-…] ids in the same sentence) and the
value is within tolerance of one cited row's retention (fraction or % scale). Citations to ids outside the packet are
fabricated. UCR = unsupported / numeric claims.
"""
from __future__ import annotations

import re

from culinarystate.retrieval.retriever import EvidencePacket

CIT = re.compile(r"EVD-\d{6}")                       # any id, incl. "[EVD-1, EVD-2]" lists
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(%|percent)|(?<![\w.\d])(0?\.\d+|1\.\d+|1)(?![\w%.\d])(?!\s*(?:min|hour|°|degree|step))")
NOT_CLAIM = re.compile(r"\b(?:step|minutes?|mins?|hours?|°|degrees?|cups?|tbsp|tsp|grams?|g\b|ml\b)", re.I)
TOL = 0.03


def _row_values(p: EvidencePacket) -> dict:
    vals = {}
    for h in p.direct + p.near:
        rf = (h.row.get("derived") or {}).get("retention_factor") or {}
        scale = 0.01 if rf.get("unit") == "%" else 1.0
        v = rf.get("value") if rf.get("status") == "MEASURED" else (rf.get("censor") or {}).get("limit")
        if v is not None:
            vals[h.evd_id] = v * scale
    return vals


def check_claims(text: str, p: EvidencePacket) -> dict:
    vals, packet_ids = _row_values(p), {h.evd_id for h in p.direct + p.near}
    claims = []
    for sent in re.split(r"(?<=[.!?])\s+", text or ""):
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
    return {"numeric_claims": len(claims), "unsupported": bad, "ucr": round(bad / len(claims), 4) if claims else None,
            "fabricated_citations": sorted(set(CIT.findall(text or "")) - packet_ids), "claims": claims}
