"""Concept-level edge statistics with support, association and confidence (X3c, D-011).

Association edges: support = distinct recipes containing subject AND object (in the stated scope), lift =
P(o|s)/P(o), confidence = 95% Wilson lower bound of P(o|s). Bands: HIGH (support ≥ 30, lift ≥ 2),
MEDIUM (support ≥ 10, lift ≥ 1.5), LOW otherwise. Quantile edges (timers/temperatures): confidence = n/(n+20).
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import numpy as np

Z = 1.96


def wilson_lower(k: int, n: int) -> float:
    if n == 0:
        return 0.0
    p = k / n
    den = 1 + Z * Z / n
    centre = p + Z * Z / (2 * n)
    margin = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return round(max(0.0, (centre - margin) / den), 4)


def band(support: int, lift: float | None) -> str:
    lift = lift if lift is not None else 0.0
    if support >= 30 and lift >= 2:
        return "HIGH"
    if support >= 10 and lift >= 1.5:
        return "MEDIUM"
    return "LOW"


@dataclass
class PairCounter:
    """Recipe-level co-occurrence of subject and object keys, with per-source support."""
    subj: Counter = field(default_factory=Counter)
    obj: Counter = field(default_factory=Counter)
    pair: Counter = field(default_factory=Counter)
    mentions: Counter = field(default_factory=Counter)
    by_src: dict = field(default_factory=lambda: defaultdict(Counter))
    n: int = 0

    def add_recipe(self, family: str, subjects: set, objects: set, pairs: set, mentions: Counter | None = None):
        self.n += 1
        self.subj.update(subjects)
        self.obj.update(objects)
        self.pair.update(pairs)
        for p in pairs:
            self.by_src[p][family] += 1
        if mentions:
            self.mentions.update(mentions)

    def edges(self, min_support: int, min_lift: float, top_k: int) -> list[dict]:
        rows = defaultdict(list)
        for (s, o), k in self.pair.items():
            if k < min_support or s == o:
                continue
            p_os = k / self.subj[s]
            lift = p_os / (self.obj[o] / self.n) if self.obj[o] else 0.0
            if lift < min_lift:
                continue
            rows[s].append({"subject": s, "object": o, "support": k, "subject_recipes": self.subj[s],
                            "object_recipes": self.obj[o], "mentions": self.mentions.get((s, o), k),
                            "p": round(p_os, 4), "lift": round(lift, 3), "pmi": round(math.log2(lift), 3) if lift else None,
                            "confidence": wilson_lower(k, self.subj[s]), "band": band(k, lift),
                            "by_source": dict(self.by_src[(s, o)])})
        out = []
        for s, rs in rows.items():
            out += sorted(rs, key=lambda r: (-r["confidence"], -r["support"], str(r["object"])))[:top_k]
        return out


def quantiles(values: list[float], unit: str) -> dict:
    a = np.asarray(values, dtype=float)
    return {"n": int(a.size), "unit": unit, "p10": round(float(np.percentile(a, 10)), 2),
            "p50": round(float(np.percentile(a, 50)), 2), "p90": round(float(np.percentile(a, 90)), 2),
            "min": round(float(a.min()), 2), "max": round(float(a.max()), 2)}


def quantile_confidence(n: int) -> tuple[float, str]:
    c = round(n / (n + 20), 4)
    return c, ("HIGH" if n >= 100 else "MEDIUM" if n >= 30 else "LOW")
