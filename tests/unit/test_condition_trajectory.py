"""Step 07H: trajectories are first-class: every point normalised inside the normalizer; no caller bypass."""
import pytest

from culinarystate.evidence import condition_normalizer as N

PTS = [{"time": 0, "time_unit": "min", "value": 20, "unit": "degC"}, {"time": 1, "time_unit": "h", "value": 150, "unit": "degC"}, {"time": 90, "time_unit": "min", "value": 356, "unit": "degF"}]


def test_points_fully_normalised_on_common_axis():
    t = N.normalize_value("temp_trajectory", trajectory=PTS, location="CORE")
    assert t["value_type"] == "TRAJECTORY" and t["status"] == N.VALID and t["canonical_time_unit"] == "s" and t["canonical_unit"] == "K"
    assert [p["canonical_time"] for p in t["points"]] == [0.0, 3600.0, 5400.0]
    assert t["points"][1]["canonical_value"] == pytest.approx(423.15) and t["points"][2]["canonical_value"] == pytest.approx(453.15)
    p = t["points"][0]
    assert {"raw_time", "raw_time_unit", "canonical_time", "raw_value", "raw_value_unit", "canonical_value", "location", "uncertainty"} <= set(p)


def test_non_increasing_time_after_conversion_invalid():
    bad = [PTS[0], {"time": 60, "time_unit": "min", "value": 100, "unit": "degC"}, {"time": 1, "time_unit": "h", "value": 120, "unit": "degC"}]
    assert N.normalize_value("temp_trajectory", trajectory=bad, location="CORE")["status"] == N.INVALID


def test_unspecified_location_ambiguous_and_missing_ok_only_if_stated():
    t = N.normalize_value("temp_trajectory", trajectory=PTS)
    assert t["status"] == N.AMBIGUOUS and N.R_LOCATION_MISSING in t["reasons"]
    assert N.normalize_value("temp_trajectory", trajectory=PTS, location="UNSPECIFIED")["status"] == N.AMBIGUOUS
    per_point = [dict(p, location="SURFACE") for p in PTS]
    assert N.normalize_value("temp_trajectory", trajectory=per_point)["status"] == N.VALID


def test_no_unit_bypass():
    t = N.normalize_value("temp_trajectory", trajectory=[(0, 20), (60, 55)], location="CORE")
    assert t["status"] == N.AMBIGUOUS and all(p["canonical_time"] is None for p in t["points"])
    ok = N.normalize_value("temp_trajectory", trajectory=[(0, 20), (60, 55)], location="CORE", time_unit="s", unit="degC")
    assert ok["status"] == N.VALID


def test_short_invalid_and_calendar_time_not_common_axis():
    assert N.normalize_value("temp_trajectory", trajectory=PTS[:1], location="CORE")["status"] == N.INVALID
    cal = [{"time": 0, "time_unit": "d", "value": 4, "unit": "degC"}, {"time": 1, "time_unit": "month", "value": 4, "unit": "degC"}]
    r = N.normalize_value("temp_trajectory", trajectory=cal, location="CORE")
    assert r["status"] == N.AMBIGUOUS and "TRAJECTORY_TIME_AXIS_NOT_COMMON" in r["reasons"]


def test_point_uncertainty_preserved_and_physical_limit_enforced():
    p = [dict(PTS[0], uncertainty={"value": 1.5, "unit_text": "degC", "type": "SD"}), PTS[1]]
    t = N.normalize_value("temp_trajectory", trajectory=p, location="CORE")
    assert t["points"][0]["uncertainty"]["type"] == "SD" and t["points"][0]["uncertainty"]["canonical_value"] == pytest.approx(1.5)
    bad = [PTS[0], {"time": 5, "time_unit": "min", "value": -300, "unit": "degC"}]
    assert N.normalize_value("temp_trajectory", trajectory=bad, location="CORE")["status"] == N.INVALID
