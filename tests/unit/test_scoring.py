from fractions import Fraction

import pytest

from culinarystate.scoring.metrics import (NIL, b_cubed, coref_scores, corpus_span_scores, grouped_bootstrap,
                                           linking_scores, quantity_scores, relation_scores, span_prf)
from culinarystate.scoring.state_metrics import replay_consistency, state_scores
from culinarystate.state_graph.engine import Add, Merge, Reserve, Split, Transform, replay
from culinarystate.state_graph.symqty import Base


def test_span_exact_vs_relaxed():
    gold = [(0, 3, "QTY"), (4, 9, "FOOD")]
    pred = [(0, 3, "QTY"), (4, 7, "FOOD"), (10, 12, "UNIT")]
    ex = corpus_span_scores([(gold, pred)], "exact")
    rx = corpus_span_scores([(gold, pred)], "relaxed")
    assert ex["micro"]["tp"] == 1 and ex["micro"]["fp"] == 2 and ex["micro"]["fn"] == 1
    assert rx["micro"]["tp"] == 2 and rx["micro"]["fp"] == 1 and rx["micro"]["fn"] == 0
    assert ex["per_label"]["QTY"]["f1"] == 1.0


def test_span_label_filter_size_excluded():
    gold = [(0, 3, "SIZE"), (4, 9, "FOOD")]
    pred = [(4, 9, "FOOD")]
    assert corpus_span_scores([(gold, pred)], labels={"FOOD"})["micro"]["f1"] == 1.0
    assert corpus_span_scores([(gold, pred)])["micro"]["f1"] < 1.0      # SIZE included changes the number


def test_relaxed_is_one_to_one():
    prf = span_prf([(0, 10, "FOOD")], [(0, 4, "FOOD"), (5, 10, "FOOD")], "relaxed")["FOOD"]
    assert (prf.tp, prf.fp) == (1, 1)


def test_macro_vs_micro():
    docs = [([(0, 1, "A")] * 1 + [(i, i + 1, "B") for i in range(2, 20)], [(0, 1, "A")])]
    s = corpus_span_scores(docs)
    assert s["per_label"]["A"]["f1"] == 1.0 and s["per_label"]["B"]["f1"] == 0.0 and s["macro_f1"] == 0.5


def test_linking_with_nil():
    s = linking_scores([("ING-1", ["ING-1", "ING-2"]), ("ING-3", ["ING-2", "ING-3"]),
                        (NIL, [NIL]), (NIL, ["ING-9"])])
    assert s["acc@1"] == 0.5 and s["recall@5"] == 0.75 and s["over_link_rate_on_nil"] == 0.5
    assert s["mrr"] == pytest.approx((1 + 0.5 + 1 + 0) / 4)


def test_relation_scores():
    g = [("onion", "TRANSFORMS_INTO", "onion"), ("onion", "MERGES_INTO", "sauce")]
    p = [("onion", "MERGES_INTO", "sauce"), ("garlic", "MERGES_INTO", "sauce")]
    s = relation_scores(g, p)
    assert s["overall"]["tp"] == 1 and s["per_relation"]["MERGES_INTO"]["precision"] == 0.5


def test_b_cubed_and_pairwise():
    gold = [{"m1", "m2", "m3"}, {"m4"}]
    pred = [{"m1", "m2"}, {"m3", "m4"}]
    b3 = b_cubed(gold, pred)
    assert b3["precision"] == pytest.approx((1 + 1 + 0.5 + 0.5) / 4, abs=1e-4)
    assert b3["recall"] == pytest.approx((2 / 3 + 2 / 3 + 1 / 3 + 1) / 4, abs=1e-4)
    assert coref_scores(gold, gold)["pairwise"]["f1"] == 1.0


def test_quantity_invented_value_rate():
    pairs = [({"status": "MEASURED", "value": 100}, {"status": "MEASURED", "value": 103}),
             ({"status": "UNKNOWN"}, {"status": "MEASURED", "value": 5}),          # invented grams
             ({"status": "RANGE", "low": 10, "high": 20}, {"status": "MEASURED", "value": 15}),
             ({"status": "MEASURED", "value": 50}, {"status": "UNKNOWN"})]
    s = quantity_scores(pairs)
    assert s["invented_value_rate"] == 0.25 and s["missed_value_rate"] == 0.25 and s["numeric_accuracy"] == 1.0


def test_grouped_bootstrap_resamples_groups():
    groups = {"famA": [1, 1, 1, 1], "famB": [0], "famC": [1]}
    ci = grouped_bootstrap(groups, lambda xs: sum(xs) / len(xs), n_boot=500)
    assert ci["n_groups"] == 3 and ci["low"] <= ci["estimate"] <= ci["high"]
    assert grouped_bootstrap(groups, lambda xs: sum(xs) / len(xs), n_boot=500) == ci   # seeded


G = lambda v: Base.amount("g", v, f"{v:g} g")  # noqa: E731


def test_state_scores_perfect_and_degraded():
    gold_ev = [Add("butter", None, G(50)), Reserve("butter", "reserved", portion=Base.amount("mL", 15, "1 tbsp")),
               Add("flour", None, G(100)), Merge(("butter", "flour"), "roux"), Transform("roux", "cook")]
    pred_ev = [Add("butter", None, G(50)), Add("flour", None, G(100)), Merge(("butter", "flour"), "roux"),
               Transform("roux", "cook")]                                          # missed the reserve
    gold, pred = replay(gold_ev), replay(pred_ev)
    perfect = state_scores(gold, gold)
    assert perfect["state_field_accuracy"] == 1.0 and perfect["merge_split_f1"]["f1"] == 1.0
    bad = state_scores(gold, pred)
    assert bad["merge_split_f1"]["recall"] < 1.0 and bad["alive_entities"]["recall"] < 1.0
    assert bad["state_field_accuracy"] < 1.0                                       # roux qty differs


def test_replay_consistency():
    r = replay_consistency([Add("dough", None, G(500)), Split("dough", (("a", Fraction(1, 2)), ("b", Fraction(1, 2))))])
    assert r["deterministic"] and r["issues"] == []
