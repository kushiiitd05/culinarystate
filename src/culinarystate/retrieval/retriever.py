"""Hybrid evidence retriever + Evidence Packet (DEL-4; plan P10, AO1, AO2).

candidates = BM25(text) ∪ structured filter (ING / parents / process family / target)
rank       = 0.35·bm25_norm + 0.65·compatibility  (hard matrix/process/target mismatch ×0.3)
dedup      = best row per (cell, independence group) — lineage-safe
classify   = DIRECT | INTERPOLATED | QUALITATIVE | CONFLICT | UNSUPPORTED   (MODEL_ESTIMATED added by DEL-2 models)
Dense retrieval plugs in through `dense_scores` (dict row_index -> score) when an embedding model is available.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from culinarystate.eda.report import cell_key

from .bm25 import BM25
from .compatibility import Query, compatibility

GROUNDED = {"E1", "E2", "E3", "E4"}


def evd_text(e: dict, c: dict | None) -> str:
    m, p, t = e["matrix"], e["process"], e["target"]
    mods = p.get("modifiers") or {}
    parts = [m.get("raw_name", ""), m.get("food_group") or "", m.get("form") or "", p.get("raw_name", ""),
             " ".join(p.get("steps", [])), t.get("raw_name", ""), str(mods.get("food_after_raw") or ""),
             (c or {}).get("medium") or "", e["derived"].get("direction", "")]
    return " ".join(x for x in parts if x)


@dataclass
class Hit:
    evd_id: str
    score: float
    bm25: float
    compat: dict
    row: dict


@dataclass
class EvidencePacket:
    question: str
    query: Query
    evidence_class: str
    direct: list[Hit] = field(default_factory=list)
    near: list[Hit] = field(default_factory=list)
    conflicts: list[list[str]] = field(default_factory=list)
    condition_differences: list[str] = field(default_factory=list)
    known_unknowns: list[str] = field(default_factory=list)
    disallowed_claims: list[str] = field(default_factory=list)
    citation_map: dict[str, str] = field(default_factory=dict)

    def summary(self) -> dict:
        return {"class": self.evidence_class, "direct": [h.evd_id for h in self.direct],
                "near": [h.evd_id for h in self.near], "conflicts": self.conflicts,
                "known_unknowns": self.known_unknowns, "disallowed_claims": self.disallowed_claims}


class EvidenceRetriever:
    def __init__(self, evd: list[dict], cond: dict[str, dict], proc_family: dict[str, str]):
        self.evd = [e for e in evd if e["status"] == "ACTIVE"]
        self.cond = cond
        self.proc_family = proc_family
        self.bm25 = BM25([evd_text(e, cond.get(e["process"].get("condition_id") or "")) for e in self.evd])
        self.by_ing: dict[str, list[int]] = {}
        self.by_target: dict[str, list[int]] = {}
        for i, e in enumerate(self.evd):
            if e["matrix"].get("ingredient_id"):
                self.by_ing.setdefault(e["matrix"]["ingredient_id"], []).append(i)
            self.by_target.setdefault(e["target"]["raw_name"].lower(), []).append(i)

    def _candidates(self, text: str, q: Query, k_bm25: int) -> dict[int, float]:
        bm = dict(self.bm25.top(text, k_bm25))
        pool = set(bm)
        related = {i for i, _ in q.ingredient_relations}                    # R4 graph expansion
        for ing in ({q.ingredient_id} if q.ingredient_id else set()) | set(q.ingredient_parents) | related:
            pool |= set(self.by_ing.get(ing, []))
        if q.target:
            pool &= pool if not self.by_target else pool | {i for t, ix in self.by_target.items()
                                                            if q.target.lower() in t for i in ix}
        return {i: bm.get(i, 0.0) for i in pool}

    def search(self, text: str, q: Query, k: int = 10, k_bm25: int = 300,
               dense_scores: dict[int, float] | None = None, exclude: set | None = None) -> list[Hit]:
        """exclude: row indices hidden from this search (leave-cell-out evaluation)."""
        cands = {i: b for i, b in self._candidates(text, q, k_bm25).items() if not exclude or i not in exclude}
        if not cands:
            return []
        mx = max(cands.values()) or 1.0
        hits = []
        for i, b in cands.items():
            e = self.evd[i]
            c = compatibility(q, e, self.cond.get(e["process"].get("condition_id") or ""), self.proc_family)
            s = 0.35 * (b / mx) + 0.65 * c["score"] + (0.1 * dense_scores.get(i, 0) if dense_scores else 0)
            if c["hard_mismatch"]:
                s *= 0.3
            hits.append(Hit(e["id"], round(s, 4), round(b, 3), c, e))
        hits.sort(key=lambda h: (-h.score, h.evd_id))
        seen, out = set(), []
        for h in hits:
            key = (cell_key(h.row, self.cond), h.row.get("independence_group"))
            if key in seen:
                continue
            seen.add(key)
            out.append(h)
            if len(out) >= k:
                break
        return out

    def packet(self, question: str, q: Query, k: int = 10) -> EvidencePacket:
        hits = self.search(question, q, k)
        direct = [h for h in hits if not h.compat["hard_mismatch"] and h.row["tier"] in GROUNDED and
                  all(h.compat["vector"][a] == "MATCH" for a in ("matrix", "process", "target"))]
        near = [h for h in hits if h not in direct and not h.compat["hard_mismatch"] and
                h.compat["vector"]["target"] in ("MATCH", "UNKNOWN") and
                sum(h.compat["vector"][a] in ("MATCH", "NEAR") for a in ("matrix", "process")) >= 1]
        broad_only = False
        if q.ingredient_id or q.ingredient_name:     # a food was asked: unlinked-food rows are BROAD, never NEAR
            strict = [h for h in near if h.compat["vector"]["matrix"] in ("MATCH", "NEAR")]
            broad_only = not strict and bool(near)   # (graph_expansion_v1: such rows lose to the global median)
            near = strict or near
        pool = direct or near
        dirs = {}
        for h in pool:
            d = h.row["derived"].get("direction")
            if d in ("INCREASE", "DECREASE"):
                dirs.setdefault(d, []).append(h.evd_id)
        conflicts = [dirs["INCREASE"] + dirs["DECREASE"]] if len(dirs) == 2 else []
        has_numeric = any(h.row["derived"].get("retention_factor", {}).get("status") == "MEASURED" for h in pool)
        if conflicts:
            cls = "CONFLICT"
        elif direct:
            cls = "DIRECT" if has_numeric else "QUALITATIVE"
        elif near:
            cls = "INTERPOLATED" if has_numeric and not broad_only else "QUALITATIVE"
        else:
            cls = "UNSUPPORTED"
        unknowns = sorted({a for h in pool[:5] for a, v in h.compat["vector"].items() if v == "UNKNOWN"})
        diffs = sorted({f"{a}: {v}" for h in near[:5] for a, v in h.compat["vector"].items() if v in ("NEAR",
                                                                                                    "MISMATCH")}
                       | ({"matrix: UNKNOWN (relation of these foods to the asked food is unknown)"} if broad_only else set()))
        disallowed = []
        if cls in ("INTERPOLATED", "QUALITATIVE"):
            disallowed.append("no exact numeric claim for the asked condition; state the nearest evidence and its differences")
        if cls == "UNSUPPORTED":
            disallowed.append("no factual claim about the process effect; ABSTAIN or ASK")
        if cls == "CONFLICT":
            disallowed.append("no single-direction claim; report the conflict and its sources")
        cmap = {h.evd_id: h.row["source_id"] for h in pool}
        return EvidencePacket(question, q, cls, direct, near, conflicts, diffs, unknowns, disallowed, cmap)
