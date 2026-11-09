"""S171 / M5: D5 P/C-block question drafting (reports/del5/d5_benchmark_preregistration_DRAFT.md §1). Synthetic."""
from __future__ import annotations

import pytest

from culinarystate.evaluation import d5_draft as D5

PAIRS = {("ING-1", "PROC-B"): ["EVD-1", "EVD-2"], ("ING-P", "PROC-S"): ["EVD-3"]}
PARENTS = {"ING-2": ("ING-P",), "ING-1": ()}


def test_stratum_direct_similar_none():
    assert D5.stratum("ING-1", "PROC-B", PAIRS, PARENTS) == ("DIRECT", ["EVD-1", "EVD-2"])
    assert D5.stratum("ING-2", "PROC-S", PAIRS, PARENTS) == ("SIMILAR_ONLY", ["EVD-3"])
    assert D5.stratum("ING-2", "PROC-B", PAIRS, PARENTS) == ("NONE", [])
    assert D5.stratum(None, "PROC-B", PAIRS, PARENTS) == ("NONE", [])


def test_gold_mode_per_stratum():
    assert D5.GOLD_MODE == {"DIRECT": "ANSWER", "SIMILAR_ONLY": "ANSWER_SIMILAR_ONLY", "NONE": "ABSTAIN"}


def test_phrasings_vary_and_fill_slots():
    qs = {D5.phrase_effect(i, "spinach", "boiled", "boil", "vitamin C") for i in range(len(D5.EFFECT_TEMPLATES))}
    assert len(qs) == len(D5.EFFECT_TEMPLATES) >= 4
    assert all("spinach" in q and "vitamin C" in q and "{" not in q for q in qs)
    c = D5.phrase_compare(0, "carrot", ("boil", "steam"), "folate")
    assert "carrot" in c and "boil" in c and "steam" in c and "folate" in c


def test_seeded_pick_is_deterministic_and_respects_quota():
    cells = [{"cell": f"C{i}", "stratum": s} for i, s in enumerate(["DIRECT"] * 30 + ["NONE"] * 30)]
    a = D5.seeded_pick(cells, seed="s", quota={"DIRECT": 5, "NONE": 3})
    b = D5.seeded_pick(cells, seed="s", quota={"DIRECT": 5, "NONE": 3})
    assert a == b and [c["stratum"] for c in a].count("DIRECT") == 5 and len(a) == 8
    with pytest.raises(ValueError):
        D5.seeded_pick(cells, seed="s", quota={"SIMILAR_ONLY": 1})


def test_diversity_cap_limits_repeats_of_one_ingredient():
    cells = [{"cell": f"C{i}", "stratum": "DIRECT", "ingredient_id": "ING-1" if i < 20 else f"ING-{i}"}
             for i in range(40)]
    out = D5.seeded_pick(cells, seed="s", quota={"DIRECT": 10}, max_per_ingredient=2)
    assert sum(c["ingredient_id"] == "ING-1" for c in out) <= 2
