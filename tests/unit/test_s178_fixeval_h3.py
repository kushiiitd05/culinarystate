"""S178 FIX-EVAL: SCI-B E2 (one-sided floor), E3 (token boundary), E4 (cell=None never SUPPORTED). Synthetic EVD rows only.

Failure scenarios (review):
- E2: a 5-0 split gives one-sided p = 0.03125, yet ``can_be_significant`` was False (two-sided floor 6 hard-coded).
- E3: question "pea" against row "Peanuts, raw" was SIMILAR.
- E4: with cell=None relevance is NOT_CHECKED and the claim counted as SUPPORTED (a D5 runner that omits the cell silently falls
  back to "value matches any cited row").
"""
from __future__ import annotations

import pytest

from culinarystate.evaluation import h3_independent as H3


def row(i, rf, *, ing="ING-1", raw="broccoli", proc="PROC-19", steps=("boil",), svar="SVAR-9"):
    return {"id": f"EVD-{i:06d}", "status": "ACTIVE", "matrix": {"ingredient_id": ing, "raw_name": raw},
            "process": {"process_id": proc, "steps": list(steps), "raw_name": steps[0]},
            "target": {"state_variable_id": svar, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": "MEASURED", "value": rf, "unit": "fraction"}}}


EVD = {r["id"]: r for r in [row(1, 0.65), row(3, 0.65, ing="ING-9", raw="spinach"),
                            row(20, 0.65, ing="ING-50", raw="Peanuts, raw"), row(21, 0.65, ing="ING-51", raw="Peas, green, raw"),
                            row(22, 0.65, ing="ING-52", raw="Tomatoes, red, ripe"), row(23, 0.65, ing="ING-53", raw="Chickpeas, mature")]}
CELL = {"ingredient_ids": ["ING-1"], "ingredient_names": ["broccoli"], "process_ids": ["PROC-19"], "target_svars": ["SVAR-9"]}


def _res(n, bad, nc=0):
    return {"n_numeric": n, "n_numeric_unsupported": bad, "n_numeric_cell_not_checked": nc}


# ------------------------------------------------------------------ E2
def test_five_zero_split_can_be_significant_one_sided_but_not_two_sided():
    worse = {f"q{i}": _res(1, 1 if i < 5 else 0) for i in range(10)}
    better = {f"q{i}": _res(1, 0) for i in range(10)}
    r = H3.compare_rungs(worse, better)
    assert (r["b_worse_only_unsupported"], r["c_better_only_unsupported"]) == (5, 0)
    assert r["p_one_sided_exact"] == pytest.approx(0.03125)
    assert r["min_discordant_one_sided"] == 5 and r["min_discordant_two_sided"] == 6
    assert r["can_be_significant_one_sided"] is True and r["can_be_significant_two_sided"] is False
    assert r["can_be_significant"] is True and r["sidedness"] == "one-sided"            # the H3 test is one-sided
    two = H3.compare_rungs(worse, better, sidedness="two-sided")
    assert two["can_be_significant"] is False
    with pytest.raises(ValueError):
        H3.compare_rungs(worse, better, sidedness="left")


def test_floors_are_derived_from_the_exact_test():
    assert H3.min_discordant_for_alpha("one-sided") == 5 and H3.min_discordant_for_alpha("two-sided") == 6
    assert H3.min_discordant_for_alpha("one-sided", alpha=0.01) == 7


# ------------------------------------------------------------------ E3
@pytest.mark.parametrize("name,raw,level", [
    ("pea", "Peanuts, raw", "MISMATCH_INGREDIENT"), ("pea", "Peas, green, raw", "SIMILAR"), ("pea", "Chickpeas, mature", "MISMATCH_INGREDIENT"),
    ("tomato", "Tomatoes, red, ripe", "SIMILAR"), ("broccoli", "broccoli", "SIMILAR"), ("peanut", "Peanuts, raw", "SIMILAR"),
])
def test_ingredient_name_matches_on_token_boundaries(name, raw, level):
    r = row(99, 0.65, ing="ING-X", raw=raw)
    assert H3.row_relevance(r, {"ingredient_names": [name]})["level"] == level


# ------------------------------------------------------------------ E4
def test_value_match_without_a_cell_is_never_supported():
    s = H3.score_answer("Keeps 65% [EVD-000003].", evd=EVD, cell=None)
    c = s["claims"][0]
    assert c["verdict"] == "CELL_NOT_CHECKED" and c["relevance"] == "NOT_CHECKED" and c["supporting_ids"] == []
    assert s["n_numeric_cell_not_checked"] == 1 and s["n_numeric_supported"] == 0
    assert s["n_numeric_unsupported"] == 1                                              # fail-closed: not shown supported
    assert "CELL_NOT_CHECKED" in H3.VERDICTS
    assert H3.score_answer("Keeps 65% [EVD-000001].", evd=EVD, cell=CELL)["claims"][0]["verdict"] == "SUPPORTED"


def test_require_cell_refuses_a_missing_cell():
    with pytest.raises(ValueError):
        H3.score_answer("Keeps 65% [EVD-000001].", evd=EVD, cell=None, require_cell=True)
    with pytest.raises(ValueError):
        H3.score_answer("Keeps 65% [EVD-000001].", evd=EVD, cell={}, require_cell=True)
    assert H3.score_answer("Keeps 65% [EVD-000001].", evd=EVD, cell=CELL, require_cell=True)["n_numeric_supported"] == 1


def test_summarize_rung_counts_not_checked_separately():
    res = {"q1": H3.score_answer("Keeps 65% [EVD-000001].", evd=EVD, cell=None),
           "q2": H3.score_answer("Keeps 65% [EVD-000001].", evd=EVD, cell=CELL),
           "q3": H3.score_answer("Keeps 40% [EVD-000001].", evd=EVD, cell=CELL)}
    s = H3.summarize_rung(res, {"q1": "ANSWER", "q2": "ANSWER", "q3": "ANSWER"})
    assert s["n_numeric_claims"] == 3 and s["n_cell_not_checked"] == 1
    assert s["n_unsupported"] == 2 and s["ucr"] == round(2 / 3, 4)                 # fail-closed UCR
    assert s["ucr_cell_checked_claims_only"] == 0.5                    # q2 supported, q3 mismatch
    assert s["coverage_answerable"]["x"] == 1                                           # only q2 has a SUPPORTED claim
    assert s["ucr_status"] == "CELL_NOT_CHECKED_COUNTED_AS_UNSUPPORTED"


def test_compare_rungs_sets_aside_questions_with_unchecked_claims():
    worse = {"q1": _res(1, 1, nc=1), "q2": _res(1, 1), "q3": _res(1, 0)}
    better = {"q1": _res(1, 0), "q2": _res(1, 0), "q3": _res(1, 0, nc=0)}
    r = H3.compare_rungs(worse, better)
    assert r["n_paired"] == 3 and r["n_set_aside_cell_not_checked"] == 1 and r["n_compared"] == 2
    assert (r["b_worse_only_unsupported"], r["c_better_only_unsupported"]) == (1, 0)
