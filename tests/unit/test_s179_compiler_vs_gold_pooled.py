"""S179 (T3-C11-R1): rule compiler vs the P1 and dev gold sets, pooled counts with Wilson intervals, counts only."""
from __future__ import annotations

import json

import pytest

from culinarystate.annotation.examples import white_sauce
from culinarystate.evaluation import compiler_vs_gold_pooled as P

REG = {"butter", "flour", "milk"}


def test_gold_level_is_a_perfect_ceiling():
    out = P.score_set([white_sauce()], REG, label_basis="TEST")
    g = out["levels"]["G"]
    for k in P.TUPLE_KEYS:
        assert g[k]["fp"] == 0 and g[k]["fn"] == 0
    assert g["state_fields"]["correct"] == g["state_fields"]["total"] > 0


def test_pooled_counts_add_up_and_intervals_are_wilson():
    out = P.score_set([white_sauce(), white_sauce()], REG, label_basis="TEST")
    one = P.score_set([white_sauce()], REG, label_basis="TEST")
    for k in P.TUPLE_KEYS:
        a, b = out["levels"]["P"][k], one["levels"]["P"][k]
        assert (a["tp"], a["fp"], a["fn"]) == (2 * b["tp"], 2 * b["fp"], 2 * b["fn"])
        lo, hi = a["precision_ci95"]
        assert 0.0 <= lo <= a["precision"] <= hi <= 1.0
    assert out["n_recipes"] == 2


def test_output_is_counts_only():
    doc = white_sauce()
    out = P.score_set([doc], REG, label_basis="TEST")
    blob = json.dumps(out)
    assert doc["recipe_id"] not in blob
    assert all(s["text"] not in blob for s in doc["steps"])
    assert out["label_basis"] == "TEST" and out["contains_ids"] is False and out["contains_text"] is False


def test_empty_set_refused():
    with pytest.raises(ValueError):
        P.score_set([], REG, label_basis="TEST")
