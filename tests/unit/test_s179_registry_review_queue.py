"""S179 P9: mention-weighted human verification queue over registry/ing_sr_defaults_v1.csv (packet Q44)."""
from __future__ import annotations

import pytest

from culinarystate.composition import review_queue as RQ

REG = [
    {"term": "onion", "sr_description": "Onions, raw", "fdc_id": "170000", "kind": "DIRECT"},
    {"term": "double cream", "sr_description": "Cream, fluid, heavy whipping", "fdc_id": "170859", "kind": "UK_US"},
    {"term": "red", "sr_description": "", "fdc_id": "", "kind": "NOT_A_FOOD"},
    {"term": "saffron", "sr_description": "Spices, saffron", "fdc_id": "170936", "kind": "DIRECT"},
]


def test_rows_ordered_by_mentions_with_cumulative_share() -> None:
    rows = RQ.review_rows(REG, {"onion": 60, "double cream": 30, "red": 10}, total_mentions=200)
    assert [r["term"] for r in rows] == ["onion", "double cream", "red", "saffron"]
    assert [r["rank"] for r in rows] == [1, 2, 3, 4]
    assert rows[0]["mention_share"] == pytest.approx(0.30)
    assert rows[1]["cumulative_share"] == pytest.approx(0.45)
    assert rows[3]["mentions"] == 0 and rows[3]["cumulative_share"] == pytest.approx(0.50)


def test_human_columns_start_empty_and_priority_flags_material_kinds() -> None:
    rows = RQ.review_rows(REG, {"onion": 60, "double cream": 30}, total_mentions=100)
    by = {r["term"]: r for r in rows}
    for r in rows:
        assert r["human_decision"] == "" and r["human_reviewer"] == "" and r["verification"] == "UNVERIFIED"
    assert by["double cream"]["review_reason"] == "UK_US_DEFAULT_FORM_CHECK"
    assert by["onion"]["review_reason"] == "TOP_MENTION"
    assert by["saffron"]["review_reason"] == ""


def test_top_n_marks_the_sample_audit() -> None:
    rows = RQ.review_rows(REG, {"onion": 60, "double cream": 30, "red": 10, "saffron": 1}, total_mentions=101,
                          top_n=2)
    assert [r["in_top_n"] for r in rows] == [True, True, False, False]


def test_unknown_terms_in_counts_are_ignored_and_totals_validated() -> None:
    rows = RQ.review_rows(REG, {"onion": 5, "not in registry": 99}, total_mentions=104)
    assert sum(r["mentions"] for r in rows) == 5
    with pytest.raises(ValueError):
        RQ.review_rows(REG, {"onion": 5}, total_mentions=0)
