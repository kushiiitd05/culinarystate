from collections import Counter

from culinarystate.kg.corpus import component_name
from culinarystate.kg.edges import PairCounter, band, quantile_confidence, quantiles, wilson_lower


def test_wilson_and_band():
    assert wilson_lower(0, 10) == 0.0 and wilson_lower(10, 10) < 1.0
    assert wilson_lower(50, 100) > wilson_lower(5, 10)                    # more data, tighter bound
    assert band(40, 3) == "HIGH" and band(12, 1.6) == "MEDIUM" and band(5, 5) == "LOW"


def test_pair_counter_lift_and_topk():
    pc = PairCounter()
    for _ in range(20):
        pc.add_recipe("A", {"onion"}, {"fry"}, {("onion", "fry")})
    for _ in range(80):
        pc.add_recipe("B", {"sugar"}, {"bake"}, {("sugar", "bake")})
    e = pc.edges(min_support=5, min_lift=1.0, top_k=5)
    onion = next(x for x in e if x["subject"] == "onion")
    assert onion["lift"] == 5.0 and onion["by_source"] == {"A": 20} and onion["p"] == 1.0


def test_quantiles_and_components():
    q = quantiles([5, 10, 10, 15, 20], "min")
    assert q["p50"] == 10 and q["n"] == 5 and quantile_confidence(100)[1] == "HIGH"
    assert component_name("For the filling:") == "filling" and component_name("Ingredients") is None
    assert component_name(None) is None
