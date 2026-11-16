"""D-073 R1 precision sample: where would ``RA_IMPLICIT_CURRENT_V1`` fire, and is it right? (S170). DRAFT.

Pre-registration: ``reports/step17/d073_implicit_binding_precision_PREREG.md``. R1 = at an event with no explicit,
reference or product argument, when the most-recent live tier holds two or more entities and the binder's current
mixture is live, bind the current mixture. This module only OBSERVES the unchanged binder (a subclass records the
state before each event); it never changes a graph. ``score`` applies the pre-registered landing rule.
"""
from __future__ import annotations

import hashlib
import math
from collections import Counter
from typing import Iterable, Mapping

from culinarystate.extraction import rung_a_binding as B
from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA

RULE_ID = "RA_IMPLICIT_CURRENT_V1"
LABELS = ("CORRECT", "WRONG_OBJECT", "NO_OBJECT", "NOT_AN_ACTION", "UNCLEAR")
FULL_N, FULL_MIN_CORRECT, WILSON_MIN = 60, 54, 0.80


class _Observer(B._Binder):
    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.r1: list[dict] = []

    def _leaves(self, eid: str) -> list[str]:
        out, stack, seen = [], [eid], set()
        while stack:
            e = self.ents[stack.pop()]
            if e.eid in seen:
                continue
            seen.add(e.eid)
            if e.parents:
                stack.extend(e.parents)
            elif e.span is not None:
                out.append(e.span.surface)
        return sorted(out)

    def _event(self, si, oi, act, window, margs) -> None:
        tier, cur, n_flags = self._tier(self._live()), self.current, len(self.flags)
        cur_live = bool(cur and self.ents[cur].live)
        leaves = self._leaves(cur) if cur_live else []
        super()._event(si, oi, act, window, margs)
        if cur_live and "IMPLICIT_ARG_AMBIGUOUS" in self.flags[n_flags:]:
            self.r1.append({"offset": act.span.char_start, "surface": act.span.surface,
                            "tier_size": len(tier), "current_leaves": leaves})


def r1_candidates(raw: str, *, locale: str | None, rung: RungA | None = None) -> list[dict]:
    """Every event of ``raw`` where R1 would fire, with the current mixture's ingredient leaves."""
    rung = rung or RungA()
    source = SourceText.from_raw("D073", raw)
    mentions = rung.extract_mentions(source, rung.config(locale=locale))
    obs = _Observer(source, mentions, rung.lexicon, rung.recomputers())
    obs.run()
    return obs.r1


def rank(seed: str, *parts: object) -> str:
    """sha256(seed || part || ...), plain concatenation (``rank(seed, rid)`` equals Step 17b's recipe rank)."""
    return hashlib.sha256("".join([seed, *map(str, parts)]).encode("utf-8")).hexdigest()


def pick_sample(cands: Mapping[str, Iterable[Mapping]], *, seed: str, n: int, excluded: set[str]) -> list[dict]:
    """At most one candidate per recipe (smallest offset rank), then the ``n`` recipes of smallest rank."""
    chosen = []
    for rid, items in cands.items():
        items = list(items)
        if rid in excluded or not items:
            continue
        best = min(items, key=lambda c: rank(seed, rid, c["offset"]))
        chosen.append({"recipe_id": rid, **best})
    chosen.sort(key=lambda c: rank(seed, c["recipe_id"]))
    return chosen[:n]


def wilson_lower(k: int, n: int, z: float = 1.959963984540054) -> float:
    p = k / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - spread) / (1 + z * z / n)


def score(labels: Iterable[str]) -> dict:
    """Counts, precision, Wilson 95 % lower bound and the pre-registered verdict (LAND / DO_NOT_LAND)."""
    labels = list(labels)
    bad = sorted({lab for lab in labels if lab not in LABELS})
    if bad or not labels:
        raise ValueError(f"labels must be non-empty and in {LABELS}; got {bad or 'none'}")
    counts = Counter(labels)
    n, k = len(labels), counts["CORRECT"]
    lower = wilson_lower(k, n)
    land = k >= FULL_MIN_CORRECT if n >= FULL_N else lower >= WILSON_MIN
    return {"rule_id": RULE_ID, "n": n, "label_counts": {lab: counts.get(lab, 0) for lab in LABELS},
            "precision": round(k / n, 4), "wilson95_lower": round(lower, 4),
            "landing_rule": f"n>={FULL_N}: CORRECT>={FULL_MIN_CORRECT}; else Wilson95 lower>={WILSON_MIN}",
            "verdict": "LAND" if land else "DO_NOT_LAND"}
