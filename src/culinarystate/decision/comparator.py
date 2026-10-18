"""C12 outcome comparator: which option keeps more of the target, only as far as evidence separates them.

Per option: retention factors from the packet pool (direct, else near), median per independence group (lineage-safe),
range = min..max of group medians; censored rows enter at their bound and are counted (SSOT §242.7: output precision
≤ evidence precision). Verdict: SEPARATED (ranges disjoint -> ordered), OVERLAPPING (no order claimed), INSUFFICIENT
(an option has < 2 independent groups). Never weights other objectives (§243.5).
"""
from __future__ import annotations

import statistics as stats
from collections import defaultdict

from culinarystate.retrieval.retriever import EvidencePacket

MIN_GROUPS = 2


def _value(row: dict) -> tuple[float | None, bool]:
    rf = (row.get("derived") or {}).get("retention_factor") or {}
    scale = 0.01 if rf.get("unit") == "%" else 1.0
    if rf.get("status") == "MEASURED":
        return rf["value"] * scale, False
    if rf.get("status") == "CENSORED" and (rf.get("censor") or {}).get("limit") is not None:
        return rf["censor"]["limit"] * scale, True
    return None, False


def summarise(p: EvidencePacket) -> dict:
    groups, n, cens = defaultdict(list), 0, 0
    for h in (p.direct or p.near):
        v, c = _value(h.row)
        if v is None:
            continue
        groups[h.row.get("independence_group") or h.evd_id].append(v)
        n, cens = n + 1, cens + c
    meds = [stats.median(v) for v in groups.values()]
    return {"n_rows": n, "n_groups": len(groups), "median": round(stats.median(meds), 4) if meds else None,
            "low": round(min(meds), 4) if meds else None, "high": round(max(meds), 4) if meds else None,
            "censored_share": round(cens / n, 4) if n else None, "direct": bool(p.direct)}


def compare(packets: dict[str, EvidencePacket]) -> dict:
    s = {k: summarise(p) for k, p in packets.items()}
    thin = [k for k, v in s.items() if v["n_groups"] < MIN_GROUPS]
    basis = "DIRECT_ONLY" if all(v["direct"] for v in s.values()) else "INCLUDES_NEAR_EVIDENCE"
    if thin:
        return {"verdict": "INSUFFICIENT", "order": None, "insufficient": thin, "summaries": s, "basis": basis}
    ranked = sorted(s, key=lambda k: -s[k]["median"])
    separated = all(s[a]["low"] > s[b]["high"] for a, b in zip(ranked, ranked[1:]))
    return {"verdict": "SEPARATED" if separated else "OVERLAPPING", "order": ranked if separated else None,
            "insufficient": [], "summaries": s, "basis": basis}
