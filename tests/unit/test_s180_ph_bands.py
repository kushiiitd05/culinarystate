"""S180 freeze step 8 / axis 7: pH bands from the in-repo FDA/CFSAN 2003 table.

The gap matrix recorded pH as 0% fill, "schema only", and the known limitations said there was no
sourced pH table so tomato sauce could not be called acidic. A sourced table was in fact already in
the repo: ``registry/food_ph_fda2003_v1.csv`` (479 rows, FDA/CFSAN Oct 2003, public domain, carrying
its own source sha256), with an ING crosswalk.

Only EXACT / FULL crosswalk rows are used. Everything else stays UNKNOWN, because the crosswalk is
AI_DRAFTED and a LOW-confidence generalisation is not evidence.

Intervals stay intervals: no midpoint, no clipping (D-013).
"""
from __future__ import annotations

import pytest

from culinarystate.composition import ph_bands as PH


def test_table_loads_and_is_not_empty():
    bands = PH.load_ph_bands()
    assert bands


def test_only_exact_full_crosswalk_rows_are_used():
    for band in PH.load_ph_bands().values():
        assert band.confidence == "EXACT"
        assert band.match_basis == "FULL"


def test_tomato_vinegar_and_lemon_juice_resolve():
    bands = PH.load_ph_bands()
    for ing in ("ING-000010", "ING-000556", "ING-000043"):
        assert ing in bands, f"{ing} should have a pH band"


def test_tomato_band_is_the_reported_interval():
    b = PH.band_for("ING-000010")
    assert (b.ph_low, b.ph_high) == (4.3, 4.9)
    assert b.value_type == "INTERVAL"


def test_vinegar_band_is_the_reported_interval():
    b = PH.band_for("ING-000556")
    assert (b.ph_low, b.ph_high) == (2.4, 3.4)


def test_no_midpoint_is_ever_computed():
    """An interval is carried as an interval; a single collapsed value would be invented."""
    b = PH.band_for("ING-000010")
    assert b.ph_low != b.ph_high
    assert not hasattr(b, "ph_midpoint")


def test_lower_bound_only_rows_keep_a_none_high():
    rows = [b for b in PH.load_ph_bands().values() if b.value_type == "LOWER_BOUND_ONLY"]
    for b in rows:
        assert b.ph_high is None


def test_every_band_carries_its_source_and_hash():
    for b in PH.load_ph_bands().values():
        assert "FDA" in b.source
        assert len(b.source_sha256) == 64


def test_basis_says_the_crosswalk_is_ai_drafted():
    """Human verification is still owed: the band is sourced, the mapping is not yet verified."""
    assert PH.BASIS == "FDA_PH_2003_VIA_AI_DRAFTED_CROSSWALK"
    assert PH.band_for("ING-000010").verify_status == "UNVERIFIED_CROSSWALK_AI_DRAFTED"


def test_unknown_ingredient_returns_none_not_a_guess():
    assert PH.band_for("ING-999999") is None


def test_acidity_classification_is_interval_aware():
    """FDA's 4.6 acid-food threshold. A band straddling it is INCONCLUSIVE, never forced."""
    assert PH.acidity_band(2.4, 3.4) == "ACIDIC"
    assert PH.acidity_band(4.3, 4.9) == "INCONCLUSIVE_SPANS_THRESHOLD"
    assert PH.acidity_band(5.1, 5.8) == "LOW_ACID"
    assert PH.acidity_band(3.83, 3.83) == "ACIDIC"


def test_acidity_of_an_open_interval_is_inconclusive_when_it_cannot_be_decided():
    assert PH.acidity_band(5.5, None) == "LOW_ACID"
    assert PH.acidity_band(3.0, None) == "INCONCLUSIVE_OPEN_INTERVAL"


def test_band_is_immutable():
    b = PH.band_for("ING-000010")
    with pytest.raises(Exception):
        b.ph_low = 1.0


# --- axis 7 is no longer schema-only for covered ingredients ----------------------

def test_compiler_fills_axis_7_for_a_covered_food():
    from culinarystate.composition import evidence_compiler as EC
    state = {"food": "tomato", "food_id": "ING-000010", "step": 1, "action": "Boil",
             "G": {}, "C": {}, "Q": {}, "Y": {}}
    cell = EC.ph_axis_cell(state)
    assert cell["status"] == "EVALUABLE"
    assert cell["ph_low"] == 4.3 and cell["ph_high"] == 4.9
    assert cell["acidity"] == "INCONCLUSIVE_SPANS_THRESHOLD"


def test_compiler_keeps_axis_7_unknown_for_an_uncovered_food():
    from culinarystate.composition import evidence_compiler as EC
    state = {"food": "mystery", "food_id": "ING-999999", "step": 1, "action": "Boil",
             "G": {}, "C": {}, "Q": {}, "Y": {}}
    cell = EC.ph_axis_cell(state)
    assert cell["status"] == "UNKNOWN"
    assert cell["reason"] == "NO_PH_BAND_FOR_THIS_INGREDIENT"
