"""Synthetic-fixture tests for the 35d cuisine rungs (no real data)."""
import math

import pytest

from culinarystate.representation import cuisine_rungs as cr


def R(rid, ings, level="CUISINE", cuisine=None):
    return cr.LabelledRecipe(rid, frozenset(ings), level, cuisine)


@pytest.fixture
def toy():
    recs = [
        R("a1", {"salt", "rice"}, cuisine="A"),
        R("a2", {"salt", "soy"}, cuisine="A"),
        R("b1", {"salt", "butter"}, cuisine="B"),
        R("b2", {"butter", "wine"}, cuisine="B"),
        R("c1", {"salt", "rice"}, cuisine="C"),
        R("c2", {"cumin", "rice"}, cuisine="C"),
    ]
    return cr.build_corpus(recs)


def test_exclusions_counted_never_guessed():
    recs = [
        R("1", {"x"}, cuisine="A"),
        R("2", {"x"}, level="REGION", cuisine=None),
        R("3", {"x"}, level="UNKNOWN"),
        R("4", {"x"}, level="CONFLICTING"),
        R("5", {"x"}, level="NEEDS_HUMAN"),
    ]
    corpus = cr.build_corpus(recs)
    assert corpus.n_recipes == {"A": 1}
    assert corpus.excluded == {"REGION": 1, "UNKNOWN": 1, "CONFLICTING": 1, "NEEDS_HUMAN": 1}


def test_region_rejected_strict_and_direct():
    with pytest.raises(ValueError, match="REGION"):
        cr.build_corpus([R("2", {"x"}, level="REGION")], strict=True)
    with pytest.raises(ValueError, match="REGION"):
        cr.require_single_cuisine(R("2", {"x"}, level="REGION", cuisine="Europe"))
    with pytest.raises(ValueError):
        cr.require_single_cuisine(R("3", {"x"}, level="CUISINE", cuisine=None))


def test_c0_known_answer(toy):
    p = cr.c0_prevalence(toy)
    assert p["A"]["salt"] == 1.0 and p["A"]["rice"] == 0.5
    assert p["B"]["butter"] == 1.0 and p["B"]["salt"] == 0.5
    assert p["C"]["rice"] == 1.0 and "wine" not in p["C"]


def test_c1_known_answer_uses_k_minus_1(toy):
    a = cr.c1_specificity(toy)
    # K=3; salt: A=1, B=.5, C=.5 -> 1 - (1/2)(1.0) = 0.5
    assert a["A"]["salt"] == pytest.approx(0.5)
    # rice in C: 1 - (1/2)(0.5+0) = 0.75
    assert a["C"]["rice"] == pytest.approx(0.75)
    # butter in B: 1 - 0 = 1
    assert a["B"]["butter"] == pytest.approx(1.0)
    # wine in B: 0.5 ; in A: 0 - (1/2)(0.5+0) = -0.25 (absent ingredient reported as negative)
    assert a["B"]["wine"] == pytest.approx(0.5)
    assert a["A"]["wine"] == pytest.approx(-0.25)


def test_c1_needs_two_classes():
    one = cr.build_corpus([R("1", {"x"}, cuisine="A")])
    with pytest.raises(ValueError):
        cr.c1_specificity(one)


def test_idf_cuis_known_answer(toy):
    idf = cr.idf_cuis(toy)
    assert idf["cumin"] == pytest.approx(math.log(3 / 1))
    assert idf["salt"] == pytest.approx(0.0 + math.log(3 / 3))
    assert idf["rice"] == pytest.approx(math.log(3 / 2))


def test_heldout_cuisine_never_used(toy):
    a = cr.c1_specificity(toy, exclude=["C"])
    assert "C" not in a
    # K=2 now: salt in A = 1 - (1/1)(.5) = .5 ; cumin vanishes
    assert a["A"]["salt"] == pytest.approx(0.5)
    assert "cumin" not in a["A"]
    idf = cr.idf_cuis(toy, exclude=["C"])
    assert "cumin" not in idf and idf["rice"] == pytest.approx(math.log(2 / 1))


def test_leakage_guards():
    with pytest.raises(cr.LeakageError):
        cr.assert_no_heldout(used_cuisines=["A", "C"], heldout="C")
    cr.assert_no_heldout(used_cuisines=["A", "B"], heldout="C")
    with pytest.raises(cr.LeakageError):
        cr.assert_weight_not_target_derived(weight_source="B", predicting="B")
    cr.assert_weight_not_target_derived(weight_source="A", predicting="B")


def test_npmi_known_answer():
    # N=4; x in 2, y in 2, xy in 2 -> perfect association -> 1
    assert cr.npmi(2, [2, 2], 4) == pytest.approx(1.0)
    # independent: x 2, y 2, xy 1, N 4 -> 0
    assert cr.npmi(1, [2, 2], 4) == pytest.approx(0.0)
    # ln(.25/(.5*.25))/(-ln .25) with x=2,y=1,xy=1
    assert cr.npmi(1, [2, 1], 4) == pytest.approx(math.log(2) / math.log(4))
    # triplet
    assert cr.npmi(2, [2, 2, 2], 4) == pytest.approx(math.log(0.5 / 0.125) / -math.log(0.5))
    assert cr.npmi(4, [4, 4], 4) == 1.0
    with pytest.raises(ValueError):
        cr.npmi(0, [1, 1], 4)


@pytest.mark.parametrize("joint,marginals,total", [
    (5, [5, 5], 4), (2, [1, 2], 4), (1, [5, 1], 4),
    (1, [], 4), (1, [float("nan"), 1], 4),
    (1, [3, 3], 4), (0.5, [1, 1], 4),
])
def test_npmi_rejects_impossible_or_nonfinite_support(joint, marginals, total):
    with pytest.raises(ValueError, match="support"):
        cr.npmi(joint, marginals, total)


def test_c2_support_thresholds():
    recs = [R(f"a{i}", {"p", "q", "r"}, cuisine="A") for i in range(10)]
    recs += [R(f"a{i}x", {"p", "q"}, cuisine="A") for i in range(10, 20)]
    recs += [R("b1", {"p"}, cuisine="B")]
    corpus = cr.build_corpus(recs)
    m = cr.c2_motifs(corpus, "A")  # defaults pair 20, triplet 10
    assert set(m["pairs"]) == {("p", "q")}
    assert m["pairs"][("p", "q")]["support"] == 20
    assert set(m["triplets"]) == {("p", "q", "r")}
    assert m["pairs"][("p", "q")]["npmi"] == 1.0 or m["pairs"][("p", "q")]["npmi"] > 0
    m2 = cr.c2_motifs(corpus, "A", min_pair=21, min_triplet=11)
    assert m2["pairs"] == {} and m2["triplets"] == {}
    with pytest.raises(LookupError):
        cr.c2_motifs(corpus, "Z")


def _inc():
    return {
        "r1": frozenset({"a", "b", "c"}),
        "r2": frozenset({"b", "c"}),
        "r3": frozenset({"a", "d"}),
        "r4": frozenset({"c", "d", "e"}),
        "r5": frozenset({"a", "e"}),
    }


def _sums(inc):
    rows = {k: len(v) for k, v in inc.items()}
    cols = {}
    for v in inc.values():
        for i in v:
            cols[i] = cols.get(i, 0) + 1
    return rows, cols


def test_curveball_preserves_margins_and_deterministic():
    inc = _inc()
    out = cr.curveball(inc, seed=7, n_trades=200)
    assert _sums(out) == _sums(inc)
    assert out != inc
    assert cr.curveball(inc, seed=7, n_trades=200) == out
    assert inc == _inc()  # input not mutated


def test_null_models_shapes_and_determinism():
    inc = _inc()
    cat = {"a": "g", "b": "g", "c": "h", "d": "h", "e": "h"}
    for model in cr.NULL_MODELS:
        out = cr.null_draw(inc, model, seed=3, categories=cat)
        assert {k: len(v) for k, v in out.items()} == {k: len(v) for k, v in inc.items()}
        assert out == cr.null_draw(inc, model, seed=3, categories=cat)
    for model in ("C", "FC"):
        out = cr.null_draw(inc, model, seed=1, categories=cat)
        for k, v in inc.items():
            comp = sorted(cat[i] for i in v)
            assert sorted(cat[i] for i in out[k]) == comp
    with pytest.raises(ValueError):
        cr.null_draw(inc, "C", seed=1)
    with pytest.raises(ValueError):
        cr.null_draw(inc, "ZZ", seed=1)
