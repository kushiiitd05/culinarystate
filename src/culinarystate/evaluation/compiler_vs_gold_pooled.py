"""Rule compiler vs a gold-1.0 set: pooled tuple counts with Wilson intervals, counts only (S179, T3-C11-R1).

Same cascade and event tuples as ``tools/eval_compiler_vs_gold.py`` (S107-S109): P predicted, O1 oracle concepts,
O2 gold Add events + predicted step events, G gold replay (ceiling). That tool reports per-recipe means with a
bootstrap and writes recipe ids; this module pools tp/fp/fn over the set so precision and recall get Wilson
intervals, and its output holds no recipe id and no text. Gold here is never independent: the caller states the
label basis (D-017, D-060).
"""
from __future__ import annotations

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
