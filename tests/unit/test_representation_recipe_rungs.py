"""Toy-data tests for the 35c recipe rungs. No real data is read."""
import math

import pytest

from culinarystate.representation import recipe_rungs as rr


def test_r0_jaccard_cosine():
    a, b = {"x", "y", "z"}, {"y", "z", "w"}
    assert rr.r0_jaccard(a, b) == pytest.approx(2 / 4)
    assert rr.r0_cosine(a, b) == pytest.approx(2 / 3)
    assert rr.r0_jaccard(set(), set()) is None  # UNKNOWN, not 0
    assert rr.r0_cosine(a, set()) is None


def test_idf_rec_known_answer():
    train = [{"a", "b"}, {"a", "c"}, {"a"}, {"d"}]
    idf = rr.compute_idf_rec(train)
    n = 4
    assert idf["a"] == pytest.approx(max(0.0, math.log(n / 4)))  # df=3 -> ln(1)=0
    assert idf["a"] == 0.0
    assert idf["b"] == pytest.approx(math.log(4 / 2))
    assert rr.idf_rec_weight(idf, n, "unseen") == pytest.approx(math.log(4 / 1))


def test_idf_rec_clamped_at_zero():
    idf = rr.compute_idf_rec([{"a"}, {"a"}])  # df=N -> ln(2/3)<0 -> 0
    assert idf["a"] == 0.0


def test_r2_tfidf_cosine_and_idf_jaccard():
    train = [{"a", "b"}, {"a", "c"}, {"a"}, {"d"}]
    idf = rr.compute_idf_rec(train)
    w = math.log(2)
    # recipes {a,b} vs {b,c}: only b shared; idf a=0,b=ln2,c=ln2
    assert rr.r2_tfidf_cosine({"a", "b"}, {"b", "c"}, idf, 4) == pytest.approx(
        1 / 2 ** 0.5)  # norms ln2 and sqrt2*ln2, dot ln2^2
    assert rr.r2_tfidf_cosine({"a"}, {"a"}, idf, 4) is None  # zero norm -> masked
    assert rr.idf_jaccard({"a", "b"}, {"b", "c"}, idf, 4) == pytest.approx(w / (2 * w))
    assert rr.idf_jaccard({"a"}, {"a"}, idf, 4) is None


def test_r1_mean_masks_unprofiled():
    z = {"a": (1.0, 3.0), "b": (3.0, 5.0)}
    res = rr.r1_mean_profile({"a", "b", "q"}, z)
    assert res.vector == (2.0, 4.0)
    assert res.n_profiled == 2 and res.n_total == 3
    assert res.coverage == pytest.approx(2 / 3)
    none = rr.r1_mean_profile({"q"}, z)
    assert none.vector is None and none.coverage == 0.0


def test_r3_mass_shares_masked_when_missing():
    assert rr.r3_mass_shares({"a": 30.0, "b": 70.0}) == {"a": 0.3, "b": 0.7}
    assert rr.r3_mass_shares({"a": 30.0, "b": None}) is None
    assert rr.r3_mass_shares({}) is None


def test_frequency_only_ranking_deterministic():
    train = [{"a", "b"}, {"a", "c"}, {"a"}, {"b"}]
    assert rr.frequency_only_ranking(train) == ("a", "b", "c")
    assert rr.frequency_only_ranking(train, exclude={"a"}) == ("b", "c")
    assert rr.frequency_only_ranking([{"x"}, {"y"}]) == ("x", "y")  # tie -> id order


def test_coverage_floor_masking():
    recs = {"r1": (8, 10), "r2": (7, 10), "r3": (0, 0), "r4": (10, 10)}
    res = rr.apply_link_coverage_floor(recs, floor=0.80)
    assert res.kept == ("r1", "r4")
    assert res.excluded == ("r2", "r3")
    assert res.n_excluded == 2 and res.n_no_lines == 1
    assert res.coverage["r2"] == pytest.approx(0.7)
    assert res.coverage["r3"] is None
    with pytest.raises(ValueError):
        rr.apply_link_coverage_floor({"r": (11, 10)}, floor=0.8)
    with pytest.raises(ValueError):
        rr.apply_link_coverage_floor({}, floor=1.5)


def test_metrics_known_answers():
    ranked = ["a", "b", "c", "d"]
    rel = {"c", "z"}
    assert rr.hit_at_k(ranked, rel, 2) == 0.0
    assert rr.hit_at_k(ranked, rel, 3) == 1.0
    assert rr.recall_at_k(ranked, rel, 3) == pytest.approx(0.5)
    assert rr.mrr(ranked, rel) == pytest.approx(1 / 3)
    assert rr.mrr(["a"], {"q"}) == 0.0
    # nDCG@4: dcg = 1/log2(4); idcg = 1 + 1/log2(3)
    expect = (1 / math.log2(4)) / (1 + 1 / math.log2(3))
    assert rr.ndcg_at_k(ranked, rel, 4) == pytest.approx(expect)
    assert rr.ndcg_at_k(["c", "z"], rel, 2) == pytest.approx(1.0)
    assert rr.recall_at_k(ranked, set(), 3) is None
    with pytest.raises(ValueError):
        rr.recall_at_k(ranked, rel, 0)


def test_frequency_stratified_macro_recall():
    # bins by item frequency, explicit edges: [0,5) low, [5,inf) high
    freq = {"a": 1, "b": 2, "c": 10}
    queries = [("a", ["a", "x"]), ("b", ["x", "y"]), ("c", ["c"])]
    out = rr.frequency_stratified_macro_recall(queries, freq, edges=(5,), k=1)
    assert out.per_bin == {0: pytest.approx(0.5), 1: pytest.approx(1.0)}
    assert out.macro == pytest.approx(0.75)
    assert out.n_per_bin == {0: 2, 1: 1}


def test_split_group_aware_and_leakage():
    table = {f"r{i}": f"g{i % 10}" for i in range(100)}
    res = rr.split_by_group(table, seed=7)
    assert res.grouping_label == "DESCRIPTIVE_CONSERVATIVE_GROUPING"
    assert res.headline_eligible is False
    assert "single" in res.caveat.lower()
    rr.assert_group_disjoint(table, res.recipe_partition)
    assert set(res.recipe_partition.values()) <= {"train", "dev", "test"}
    for g in set(table.values()):
        parts = {res.recipe_partition[r] for r, gg in table.items() if gg == g}
        assert len(parts) == 1
    assert rr.split_by_group(table, seed=7) == res  # determinism
    assert rr.split_by_group(table, seed=8) != res


def test_split_proportions_on_many_groups():
    table = {f"r{i}": f"g{i}" for i in range(100)}
    res = rr.split_by_group(table, seed=1)
    counts = {p: sum(1 for v in res.recipe_partition.values() if v == p)
              for p in ("train", "dev", "test")}
    assert counts == {"train": 60, "dev": 20, "test": 20}


def test_planted_leak_rejected():
    table = {"r1": "g1", "r2": "g1", "r3": "g2"}
    leaked = {"r1": "train", "r2": "test", "r3": "train"}
    with pytest.raises(rr.LeakageError):
        rr.assert_group_disjoint(table, leaked)
    with pytest.raises(rr.LeakageError):
        rr.assert_group_disjoint(table, {"r1": "train", "r2": "train"})  # r3 missing


def test_split_rejects_bad_input():
    with pytest.raises(ValueError):
        rr.split_by_group({}, seed=1)
    with pytest.raises(ValueError):
        rr.split_by_group({"r": "g"}, seed=1, fractions=(0.5, 0.2, 0.2))


def test_inputs_not_mutated():
    s = {"a", "b"}
    t = {"b"}
    rr.r0_jaccard(s, t)
    assert s == {"a", "b"} and t == {"b"}


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf")])
def test_mass_shares_reject_invalid_physical_mass(bad):
    with pytest.raises(ValueError, match="mass"):
        rr.r3_mass_shares({"a": bad, "b": 10.0})


@pytest.mark.parametrize("metric", [rr.hit_at_k, rr.recall_at_k, rr.ndcg_at_k])
def test_rank_metrics_reject_repeated_candidates(metric):
    # Repeated relevant candidates otherwise inflate nDCG beyond 1.
    with pytest.raises(ValueError, match="duplicate"):
        metric(["a", "a"], {"a"}, 2)


def test_mrr_rejects_repeated_candidates():
    with pytest.raises(ValueError, match="duplicate"):
        rr.mrr(["a", "a"], {"a"})


@pytest.mark.parametrize("profile", [(2.0, 3.0, 4.0), (float("nan"), 2.0)])
def test_mean_profile_rejects_incompatible_or_nonfinite_vectors(profile):
    with pytest.raises(ValueError, match="profile"):
        rr.r1_mean_profile({"a", "b"}, {"a": (1.0, 2.0), "b": profile})
