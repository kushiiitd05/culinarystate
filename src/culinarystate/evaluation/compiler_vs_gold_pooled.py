"""Rule compiler vs a gold-1.0 set: pooled tuple counts with Wilson intervals, counts only (S179, T3-C11-R1).

Same cascade and event tuples as ``tools/eval_compiler_vs_gold.py`` (S107-S109): P predicted, O1 oracle concepts,
O2 gold Add events + predicted step events, G gold replay (ceiling). That tool reports per-recipe means with a
bootstrap and writes recipe ids; this module pools tp/fp/fn over the set so precision and recall get Wilson
intervals, and its output holds no recipe id and no text. Gold here is never independent: the caller states the
label basis (D-017, D-060).
"""
from __future__ import annotations

import hashlib
import random
from collections import Counter
from typing import Iterable, Mapping, Sequence

from culinarystate.annotation.gold import to_events
from culinarystate.lineage.wilson import wilson_interval
from culinarystate.scoring.metrics import PRF, tuple_prf
from culinarystate.scoring.state_metrics import (
    STRUCTURAL, align_entities, edge_tuples, final_fields, relabel,
)
from culinarystate.state_graph.engine import Add, replay
from culinarystate.state_graph.rule_compiler import compile_recipe

LEVELS = ("P", "O1", "O2", "G")
TUPLE_KEYS = ("alive_entities", "structural_edges", "all_edges", "events_loose", "events_type_only")


def _etuple_loose(ev) -> tuple:
    tgt = getattr(ev, "target", None) or getattr(ev, "source", None) or getattr(ev, "reserved", None) or \
        "+".join(getattr(ev, "inputs", ()) or ()) or getattr(ev, "label", "")
    return (type(ev).__name__, tgt)


def _build(level: str, doc: Mapping, reg_names: set[str]) -> list:
    lines = [x["text"] for x in doc["ingredient_lines"]]
    steps = [x["text"] for x in doc["steps"]]
    gold = to_events(doc)
    if level == "G":
        return gold
    if level == "P":
        return compile_recipe(lines, steps, reg_names)
    if level == "O1":
        return compile_recipe(lines, steps, {li["concept"] for li in doc["ingredient_lines"] if li["concept"] != "UNKNOWN"})
    pred = compile_recipe(lines, steps, reg_names)                                    # O2
    p_adds = [e.label for e in pred if isinstance(e, Add)]
    g_adds = [e for e in gold if isinstance(e, Add)]
    mapping = dict(zip(p_adds, [e.label for e in g_adds]))
    return g_adds + relabel([e for e in pred if not isinstance(e, Add)], mapping)


def _recipe_counts(gold: list, pred: list) -> dict:
    mapping = align_entities(gold, pred)
    pred_r = relabel(pred, mapping)
    gg, pg = replay(gold), replay(pred_r)
    gf, pf = final_fields(gg), final_fields(pg)
    ge = [_etuple_loose(e) for e in gold if not isinstance(e, Add)]
    pe = [_etuple_loose(e) for e in pred_r if not isinstance(e, Add)]
    return {
        "alive_entities": tuple_prf(gg.alive(), pg.alive()),
        "structural_edges": tuple_prf(edge_tuples(gg, STRUCTURAL), edge_tuples(pg, STRUCTURAL)),
        "all_edges": tuple_prf(edge_tuples(gg), edge_tuples(pg)),
        "events_loose": tuple_prf(ge, pe),
        "events_type_only": tuple_prf(Counter(t for t, _ in ge).elements(), Counter(t for t, _ in pe).elements()),
        "state_correct": sum(1 for k in gf if pf.get(k) == gf[k]),
        "state_total": len(gf),
        "replay_issue": bool(pg.issues),
    }


def _pooled(prfs: Iterable[PRF]) -> dict:
    tp = fp = fn = 0
    for p in prfs:
        tp, fp, fn = tp + int(p.tp), fp + int(p.fp), fn + int(p.fn)
    prec_lo, prec_hi = wilson_interval(tp, tp + fp)
    rec_lo, rec_hi = wilson_interval(tp, tp + fn)
    pooled = PRF(tp, fp, fn)
    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": round(pooled.precision, 4), "precision_ci95": [round(prec_lo, 4), round(prec_hi, 4)],
            "recall": round(pooled.recall, 4), "recall_ci95": [round(rec_lo, 4), round(rec_hi, 4)],
            "f1": round(pooled.f1, 4)}


def score_set(docs: Sequence[Mapping], reg_names: set[str], *, label_basis: str) -> dict:
    """Score every cascade level over ``docs``; return pooled counts only (no ids, no text)."""
    if not docs:
        raise ValueError("empty gold set")
    levels = {}
    for lv in LEVELS:
        rows = [_recipe_counts(to_events(d), _build(lv, d, reg_names)) for d in docs]
        out = {k: _pooled(r[k] for r in rows) for k in TUPLE_KEYS}
        correct, total = sum(r["state_correct"] for r in rows), sum(r["state_total"] for r in rows)
        lo, hi = wilson_interval(correct, total)
        out["state_fields"] = {"correct": correct, "total": total,
                               "accuracy": round(correct / total, 4) if total else None,
                               "ci95": [round(lo, 4), round(hi, 4)]}
        out["recipes_with_replay_issues"] = sum(r["replay_issue"] for r in rows)
        levels[lv] = out
    return {"n_recipes": len(docs), "label_basis": label_basis, "independent": False,
            "contains_ids": False, "contains_text": False, "interval": "Wilson 95% on pooled counts",
            "levels": levels}


def _type_counts(doc: Mapping, reg_names: set[str]) -> tuple[Counter, Counter]:
    gold = to_events(doc)
    pred = _build("P", doc, reg_names)
    g = Counter(type(e).__name__ for e in gold if not isinstance(e, Add))
    p = Counter(type(e).__name__ for e in pred if not isinstance(e, Add))
    return g, p


def _ratio(num: int, den: int) -> float | None:
    return round(num / den, 4) if den else None


def type_table(docs: Sequence[Mapping], reg_names: set[str], *, label_basis: str, n_boot: int = 2000,
               seed: str = "s179-type-table") -> dict:
    """Per event type at level P: gold count, predicted count, matched = sum over recipes of min(gold, pred), with
    precision / recall intervals from a bootstrap that resamples whole recipes (cluster bootstrap). Counts only."""
    if not docs:
        raise ValueError("empty gold set")
    per = [_type_counts(d, reg_names) for d in docs]
    types = sorted(set().union(*(set(g) | set(p) for g, p in per)))

    def totals(rows):
        out = {}
        for t in types:
            g = sum(r[0][t] for r in rows)
            p = sum(r[1][t] for r in rows)
            m = sum(min(r[0][t], r[1][t]) for r in rows)
            out[t] = (g, p, m)
        return out

    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    boots = [totals([per[rng.randrange(len(per))] for _ in per]) for _ in range(n_boot)]

    def ci(t, idx):
        vals = sorted(v for v in ((b[t][2] / b[t][idx]) if b[t][idx] else None for b in boots) if v is not None)
        if not vals:
            return None
        return [round(vals[int(0.025 * (len(vals) - 1))], 4), round(vals[int(0.975 * (len(vals) - 1))], 4)]

    tot = totals(per)
    rows = {}
    for t in types:
        g, p, m = tot[t]
        rows[t] = {"gold": g, "pred": p, "matched": m, "precision": _ratio(m, p), "recall": _ratio(m, g),
                   "precision_ci95": ci(t, 1) if p else None, "recall_ci95": ci(t, 0) if g else None}
    return {"n_recipes": len(docs), "label_basis": label_basis, "independent": False, "level": "P",
            "matching": "per recipe, matched = min(gold count, predicted count) for the type (count match, no alignment)",
            "bootstrap": {"unit": "recipe", "n": n_boot, "seed": seed, "interval": "percentile 95%"},
            "contains_ids": False, "contains_text": False, "types": rows}
