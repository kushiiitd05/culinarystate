"""D-097: Rung A event candidates typed by structure only, scored against gold-1.0 step events by per-type count
match (T3-C11-R1 / T3-C17-R2). Counts only; no ids, no text.

Mapping (fixed in DECISIONS D-097 before any score): discards -> Discard; consumes>=2 & produces==1 -> Merge;
consumes==1 & produces>=2 -> Split; consumes==1 & produces==1 -> Transform; else UNMAPPED. Transfer, Reserve and
Recombine are never predicted. Method = ``compiler_vs_gold_pooled.type_table`` (matched = min(gold, pred) per type
per recipe, no alignment) with a recipe-cluster bootstrap, plus Wilson 95% on pooled counts.
"""
from __future__ import annotations

import hashlib
import random
from collections import Counter
from typing import Any, Mapping, Optional, Sequence

from culinarystate.lineage.wilson import wilson_interval

PREDICTABLE = ("Discard", "Merge", "Split", "Transform")
GOLD_TYPES = ("Discard", "Merge", "Recombine", "Reserve", "Split", "Transfer", "Transform")
SEED = "s179-d097-type-table"


def map_event(ev: Any) -> Optional[str]:
    """D-097 structural type of one Rung A EventCandidate, or None (abstain)."""
    n_in, n_out = len(ev.consumes or ()), len(ev.produces or ())
    if ev.discards:
        return "Discard"
    if n_in >= 2 and n_out == 1:
        return "Merge"
    if n_in == 1 and n_out >= 2:
        return "Split"
    if n_in == 1 and n_out == 1:
        return "Transform"
    return None


PROC_FAMILY_TYPE_V2 = {"TRANSFER": "Transfer", "RESERVATION": "Reserve"}


def map_event_v2(ev: Any, proc_family: Optional[str]) -> Optional[str]:
    """D-102 (post-hoc amendment of D-097): discards first, then PROC family TRANSFER/RESERVATION, else D-097."""
    if ev.discards:
        return "Discard"
    return PROC_FAMILY_TYPE_V2.get(proc_family or "") or map_event(ev)


def _ratio(num: int, den: int) -> Optional[float]:
    return round(num / den, 4) if den else None


def _totals(rows: Sequence[tuple[Counter, Counter]], types: Sequence[str]) -> dict[str, tuple[int, int, int]]:
    return {t: (sum(g[t] for g, _ in rows), sum(p[t] for _, p in rows), sum(min(g[t], p[t]) for g, p in rows))
            for t in types}


def type_table_from_counts(per: Sequence[tuple[Counter, Counter]], *, n_boot: int = 2000, seed: str = SEED,
                           unmapped: int) -> dict:
    """``per`` = one (gold type Counter, predicted type Counter) pair per recipe."""
    if not per:
        raise ValueError("empty gold set")
    types = sorted(set(GOLD_TYPES) | set().union(*(set(g) | set(p) for g, p in per)))
    tot = _totals(per, types)
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    boots = [_totals([per[rng.randrange(len(per))] for _ in per], types) for _ in range(n_boot)]

    def ci(t: str, idx: int) -> Optional[list[float]]:
        vals = sorted(b[t][2] / b[t][idx] for b in boots if b[t][idx])
        if not vals:
            return None
        return [round(vals[int(0.025 * (len(vals) - 1))], 4), round(vals[int(0.975 * (len(vals) - 1))], 4)]

    rows = {}
    for t in types:
        g, p, m = tot[t]
        rows[t] = {"gold": g, "pred": p, "matched": m, "precision": _ratio(m, p), "recall": _ratio(m, g),
                   "precision_ci95": ci(t, 1) if p else None, "recall_ci95": ci(t, 0) if g else None,
                   "predictable_under_d097": t in PREDICTABLE}
    tp = sum(m for _, _, m in tot.values())
    fp = sum(p - m for _, p, m in tot.values())
    fn = sum(g - m for g, _, m in tot.values())
    plo, phi = wilson_interval(tp, tp + fp)
    rlo, rhi = wilson_interval(tp, tp + fn)
    return {"n_recipes": len(per), "unmapped_candidate_events": unmapped,
            "pooled": {"tp": tp, "fp": fp, "fn": fn, "precision": _ratio(tp, tp + fp), "recall": _ratio(tp, tp + fn),
                       "precision_ci95": [round(plo, 4), round(phi, 4)], "recall_ci95": [round(rlo, 4), round(rhi, 4)],
                       "interval": "Wilson 95% on pooled type-count matches"},
            "matching": "per recipe, matched = min(gold count, predicted count) for the type (count match, no alignment)",
            "bootstrap": {"unit": "recipe", "n": n_boot, "seed": seed, "interval": "percentile 95%"},
            "types": rows, "contains_ids": False, "contains_text": False}


def recipe_counts(doc: Mapping, rung: Any, schema: Mapping, *, to_events, Add, SourceText, idx: int,
                  proc_family: Optional[Mapping[str, str]] = None) -> tuple[Counter, Counter, int]:
    """(gold step-event type counts, predicted type counts, unmapped count) for one gold-1.0 doc.
    ``proc_family`` (PROC id -> family) switches to the D-102 v2 mapping; None keeps D-097."""
    gold = Counter(type(e).__name__ for e in to_events(doc) if not isinstance(e, Add))
    raw = "\n".join(s["text"] for s in doc["steps"])
    parsed = rung.run(SourceText.from_raw(f"D097_{idx}", raw), rung.config(), schema=schema)
    pred, unmapped = Counter(), 0
    for e in parsed.graph.events:
        if proc_family is None:
            t = map_event(e)
        else:
            proc = next((a.value for a in e.attributes if a.field == "proc_id"), None)
            t = map_event_v2(e, proc_family.get(proc))
        if t is None:
            unmapped += 1
        else:
            pred[t] += 1
    return gold, pred, unmapped
