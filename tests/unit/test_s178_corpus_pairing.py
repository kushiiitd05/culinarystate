"""S178 corpus lane: Food.com quantity/part pairing rules (opt-in) and the alignment tool helpers. Invented foods only."""
from __future__ import annotations

import math
import random

import pytest

from culinarystate.quantity import foodcom_pairing as FP
from tests.unit.test_s178_analysis_helpers import load_tool

A = load_tool("s178_corpus_foodcom_alignment")
FS = "⁄"


# ------------------------------------------------------------------ quantity strings
@pytest.mark.parametrize("q,expect", [
    ("1", 1.0), ("12", 12.0), (f"1{FS}2", 0.5), (f"1 1{FS}2", 1.5), ("1.5", 1.5), ("2 -3", 2.0), (f"1{FS}2 - 3{FS}4", 0.5),
    ("1  - 2 1/2", 1.0), (None, None), ("", None), ("abc", None), (f"1{FS}0", None),
])
def test_qty_low_value(q, expect):
    assert FP.qty_low_value(q) == expect


@pytest.mark.parametrize("q,b", [
    (None, "NONE"), ("", "NONE"), ("  ", "NONE"), ("x", "UNPARSED"), (f"1{FS}2", "LT1"), ("1", "E1"), (f"1 1{FS}2", "F1"), ("2", "E2"),
    ("3", "M4"), ("4", "M4"), ("6", "M8"), ("10", "M16"), ("100", "BIG"),
])
def test_bucket_of(q, b):
    assert FP.bucket_of(q) == b
    assert b in FP.BUCKETS


def test_part_keys():
    assert FP.part_keys("Zorb Fruits, rind of") == ("zorb fruits", "fruit")
    assert FP.part_keys("glass") == ("glass", "glass")          # a double s is not a plural
    assert FP.part_keys("moss") == ("moss", "moss")
    assert FP.part_keys(None) == ("", "")


# ------------------------------------------------------------------ rules 1 and 2
def test_positional_is_the_frozen_behaviour():
    out = FP.pair_positional(["1", "2"], ["a", "b", "c"])
    assert [(q, p) for q, p, _ in out] == [("1", "a"), ("2", "b"), (None, "c")]
    out = FP.pair_positional(["1", "2", "3"], ["a"])
    assert [(q, p) for q, p, _ in out] == [("1", "a")]
    assert FP.pair_positional([None, ""], ["a", "b"])[0][0] is None


def test_equal_length_only():
    out = FP.pair_equal_length(["1", None, "3"], ["a", "b", "c"])
    assert out == [("1", "a", FP.STATUS_PAIRED), (None, "b", FP.STATUS_PAIRED), ("3", "c", FP.STATUS_PAIRED)]
    for q in (["1", "2", "3"], ["1"], []):
        out = FP.pair_equal_length(q, ["a", "b"])
        assert out == [(None, "a", FP.STATUS_UNKNOWN), (None, "b", FP.STATUS_UNKNOWN)]
    assert FP.pair_equal_length([], []) == []


# ------------------------------------------------------------------ rule 3 (experimental)
def _model(seed=1, n=400):
    """Invented foods with strongly different quantity buckets so that alignment has signal."""
    rng = random.Random(seed)
    table = {"zorbfruit": "1", "quibbleroot": "2", "snarfleaf": "6", "wumpus meal": "100", "glimmerseed": None, "plinth cress": "3"}
    m = FP.AlignmentModel(min_phrase=5)
    for _ in range(n):
        for part, q in table.items():
            m.add(part, q if rng.random() < 0.95 else "1")
    return m, table


def test_model_probabilities_sum_to_one_and_prefer_the_trained_bucket():
    m, _ = _model()
    for part in ("zorbfruit", "never seen before", "wumpus meal"):
        assert abs(sum(m.prob(part, b) for b in FP.BUCKETS) - 1.0) < 1e-9, part
    assert m.prob("wumpus meal", "BIG") > 0.8
    assert m.prob("wumpus meal", "BIG") > m.prob("never seen before", "BIG")


def test_posteriors_are_valid_and_identity_on_equal_lists():
    m, t = _model()
    parts = ["zorbfruit", "quibbleroot", "snarfleaf", "wumpus meal"]
    qs = [t[p] for p in parts]
    post = FP.alignment_posteriors(m, qs, parts)
    for i, row in enumerate(post):
        assert sum(row) <= 1.0 + 1e-9 and all(0 <= x <= 1 + 1e-9 for x in row)
        assert max(range(len(row)), key=lambda j: row[j]) == i
    pairs = FP.align_pairs(m, qs, parts, threshold=0.5)
    assert [(q, p, s) for q, p, s in pairs] == [(t[p], p, FP.STATUS_ALIGNED) for p in parts]


def test_alignment_skips_an_extra_quantity():
    m, t = _model()
    parts = ["zorbfruit", "quibbleroot", "snarfleaf", "wumpus meal", "plinth cress"]
    true_q = [t[p] for p in parts]
    qs = true_q[:2] + ["100"] + true_q[2:]               # an extra, very distinctive quantity after the second
    # the extra "100" competes with the wumpus meal's own: the monotone alignment keeps order
    post = FP.alignment_posteriors(m, qs, parts)
    assert max(range(len(qs)), key=lambda j: post[0][j]) == 0
    assert max(range(len(qs)), key=lambda j: post[1][j]) == 1
    assert max(range(len(qs)), key=lambda j: post[4][j]) == 5          # the last part pairs with the last quantity
    pos = FP.pair_positional(qs, parts)
    assert pos[2][0] == "100" and pos[4][0] == "100"               # positional puts the wrong quantity on snarfleaf and plinth cress
    gated = FP.align_pairs(m, qs, parts, threshold=0.9)
    assert gated[4][0] == "3" or gated[4][2] == FP.STATUS_UNPAIRED   # never the wrong one when it does pair
    for (q, p, s) in gated:
        if s == FP.STATUS_ALIGNED:
            assert q == t[p] or p == "wumpus meal"                 # only the ambiguous 100 pair may differ


def test_alignment_handles_empty_and_unequal_sizes():
    m, _ = _model()
    assert FP.align_pairs(m, ["1"], []) == []
    assert FP.align_pairs(m, [], ["zorbfruit"]) == [(None, "zorbfruit", FP.STATUS_UNPAIRED)]
    post = FP.alignment_posteriors(m, ["1"], ["zorbfruit", "quibbleroot"])          # more parts than quantities
    assert len(post) == 2 and all(len(r) == 1 for r in post)
    assert sum(post[0]) + sum(post[1]) <= 1.0 + 1e-9                               # one quantity can serve one part


def test_posterior_mass_conservation():
    """Each quantity is used at most once and each part at most once under every alignment, so column and row sums are <= 1."""
    m, t = _model()
    parts = ["zorbfruit", "snarfleaf", "glimmerseed", "wumpus meal"]
    qs = ["1", "6", "100", None, "2"]
    post = FP.alignment_posteriors(m, qs, parts)
    for row in post:
        assert sum(row) <= 1.0 + 1e-9
    for j in range(len(qs)):
        assert sum(post[i][j] for i in range(len(parts))) <= 1.0 + 1e-9


# ------------------------------------------------------------------ tool helpers
def test_split_is_deterministic_and_roughly_60_20_20():
    ids = range(20000)
    c = {"train": 0, "dev": 0, "test": 0}
    for i in ids:
        s = A.split_of(i)
        assert s == A.split_of(i)
        c[s] += 1
    assert 0.55 < c["train"] / 20000 < 0.65 and 0.15 < c["dev"] / 20000 < 0.25 and 0.15 < c["test"] / 20000 < 0.25


def test_corrupt_truth_mapping():
    rng = random.Random(3)
    q = [str(i) for i in range(1, 9)]
    p = [f"part{i}" for i in range(8)]
    q2, p2, truth = A.corrupt(rng, q, p, "PARTS", 2)
    assert len(p2) == 6 and q2 == q
    assert [q2[truth[r]] for r in range(6)] == [q[int(x[4:])] for x in p2]     # kept part r pairs with its own original quantity
    q2, p2, truth = A.corrupt(rng, q, p, "QUANTITIES", 2)
    assert len(q2) == 6 and p2 == p
    assert sum(t is None for t in truth) == 2
    for i, t in enumerate(truth):
        if t is not None:
            assert q2[t] == q[i]
    assert A.corrupt(rng, q[:2], p[:2], "PARTS", 1) is None                   # too short to corrupt


def test_code_safe_keys_and_prose_strip():
    assert A.tk(0.9) == "T_0_9" and A.dk(-2) == "M2" and A.dk(3) == "P3" and A.dk(0) == "P0"
    from culinarystate.quantity.rc2_dryrun import assert_counts_only
    obj = {"a": 1, "note": "some prose, with spaces", "nested": {"statement": "more prose", "n": 2}}
    assert_counts_only(A.strip_prose(obj))
    with pytest.raises(Exception):
        assert_counts_only(obj)


def test_diagnostic_counts_on_synthetic_lists():
    recs = [(1, ["1", "2"], ["a", "b"]),                 # equal
            (2, ["1", "2", "3"], ["a", "b"]),            # quantities longer by 1 (one dropped beyond)
            (3, ["1"], ["a", "b", "c"]),                 # quantities shorter by 2 (padded)
            (4, [None, f"1{FS}2"], ["a", "b"]),          # equal, one null, one U+2044
            (5, [f"1{FS}2", "5"], ["a"])]                # longer by 1; the dropped one has no slash, the paired one does
    d = A.diagnostic(recs)
    assert d["recipes"] == 5 and d["lines_parts_total"] == 10
    assert d["recipes_by_length_relation"] == {"EQUAL": 2, "QUANTITIES_LONGER": 2, "QUANTITIES_SHORTER": 1}
    assert d["recipes_unequal"] == 3 and d["pct_recipes_unequal"] == 60.0
    assert d["lines_in_unequal_recipes"] == 6                     # 2 + 3 + 1
    pp = d["positional_pairing"]
    assert pp["padding_positions_parts_without_a_quantity_slot"] == 2
    assert pp["quantity_strings_dropped_beyond_the_parts_list"] == 2
    assert pp["lines_with_a_paired_quantity"] == 2 + 2 + 1 + 1 + 1 and pp["quantities_with_u2044_paired"] == 2
    assert d["equal_length_only_rule"] == {"recipes_paired": 2, "lines_paired": 4, "pct_of_lines": 40.0,
                                           "lines_with_null_quantity_in_those_recipes": 1, "lines_left_without_quantity": 6}
    assert d["quantity_strings_total"] == 10 and d["quantities_minus_parts_total"] == 0
    from culinarystate.quantity.rc2_dryrun import assert_counts_only
    assert_counts_only(A.strip_prose(d))


def test_simulation_beats_positional_on_synthetic_data():
    """With an informative model a planted dropped part is recovered far better than by position (method sanity, not corpus evidence)."""
    m, t = _model(n=600)
    foods = list(t)
    rng = random.Random(11)
    recs = []
    for rid in range(300):
        parts = [rng.choice(foods) for _ in range(8)]
        recs.append((rid, [t[p] for p in parts], parts))
    e = A.evaluate(m, recs, "PARTS", 1, random.Random(2), 3.0, 200)
    assert e["recipes"] == 200
    assert e["map_alignment_accuracy_pct"] > e["positional_accuracy_pct"] + 10
    t9 = e["thresholds"][A.tk(0.9)]
    assert t9["precision_pct"] is None or t9["precision_pct"] >= 70
    assert e["posterior_weighted_mean_nll_nats"] is not None


def test_pair_lines_positional_equals_the_frozen_line_builder():
    """POSITIONAL must reproduce `recipes.corpus.iter_foodcom`'s line construction exactly (same expression, synthetic lists)."""
    cases = [(["1", "2"], ["a", "b", "c"]), (["1", None, "3"], ["a", "b", "c"]), (["1", "2", "3"], ["a"]), ([], ["a"]), ([f"1{FS}2"], ["x y"]), (["", "2"], ["a", "b"])]
    for q, p in cases:
        frozen = [f"{(q[i] if i < len(q) and q[i] else '')} {p[i]}".strip() for i in range(len(p))]      # the expression in corpus.py
        assert FP.pair_lines(q, p, "POSITIONAL") == frozen, (q, p)


def test_pair_lines_rules():
    assert FP.pair_lines(["1", "2"], ["a", "b"]) == ["1 a", "2 b"]
    assert FP.pair_lines(["1", "2", "3"], ["a", "b"]) == ["a", "b"]                 # unequal: no quantity
    m, t = _model()
    parts = ["zorbfruit", "quibbleroot", "snarfleaf"]
    assert FP.pair_lines([t[p] for p in parts], parts, "ALIGN_MODEL", model=m, threshold=0.5) == [f"{t[p]} {p}" for p in parts]
    with pytest.raises(ValueError):
        FP.pair_lines(["1"], ["a"], "ALIGN_MODEL")
    with pytest.raises(ValueError):
        FP.pair_lines(["1"], ["a"], "NOPE")
