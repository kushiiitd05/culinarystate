"""Step 07 tests: deterministic condition/measurement normalisation, no inference."""
import math

import pytest

from culinarystate.evidence import condition_normalizer as N


def test_value_types_point_interval_qualitative_unknown():
    p = N.normalize_value("temp_medium", value=180, unit="degC")
    assert p["value_type"] == "POINT" and p["status"] == N.VALID and math.isclose(p["canonical_value"], 453.15)
    i = N.normalize_value("temp_medium", low=170, high=190, unit="degC")
    assert i["value_type"] == "INTERVAL" and i["canonical_low"] < i["canonical_high"]
    q = N.normalize_value("temp_equipment_setpoint", qualitative="medium heat")
    assert q["value_type"] == "QUALITATIVE" and "canonical_value" not in q and N.R_NO_NUMERIC_MAPPING in q["reasons"]
    u = N.normalize_value("ph")
    assert u["value_type"] == "UNKNOWN" and u["status"] == N.UNKNOWN and "canonical_value" not in u


def test_boiling_is_never_100c_and_unknown_ph_never_7():
    q = N.normalize_value("temp_medium", qualitative="boiling")
    assert q["value_type"] == "QUALITATIVE" and N.R_BOILING in q["reasons"]
    assert "canonical_value" not in N.normalize_value("ph", raw=None)


def test_explicit_sourced_mapping_only():
    r = N.normalize_value("temp_equipment_setpoint", qualitative="medium heat", sourced_mapping={"medium heat": {"value": 450.0, "source": "SRC-X"}})
    assert r["value_type"] == "POINT" and r["mapping_source"] == "SRC-X"


def test_temperature_absolute_vs_difference_and_location_separate():
    assert math.isclose(N.convert_temperature(100, "degC"), 373.15)
    assert math.isclose(N.convert_temperature(10, "degC", "difference"), 10)
    assert math.isclose(N.convert_temperature(18, "degF", "difference"), 10)
    assert N.normalize_value("temp_core", value=-300, unit="degC")["status"] == N.INVALID
    assert N.temperature_variable_for("SETPOINT") != N.temperature_variable_for("CORE") != N.temperature_variable_for(None)
    assert N.normalize_value("temp_unspecified", value=100, unit="degC")["status"] == N.AMBIGUOUS


def test_pressure_reference_and_units():
    a = N.normalize_value("pressure", value=15, unit="psi")
    assert a["status"] == N.AMBIGUOUS and N.R_PRESSURE_REF in a["reasons"] and math.isclose(a["canonical_value"], 15 * 6894.757293168)
    g = N.normalize_value("pressure", value=1, unit="barg")
    assert g["status"] == N.VALID and g["pressure_reference"] == "GAUGE"
    assert N.normalize_value("pressure", value=-5, unit="kPa(abs)")["status"] == N.INVALID


def test_ph_aw_bounds_and_no_defaults():
    assert N.normalize_value("ph", value=3.5, unit="pH")["status"] == N.VALID
    assert N.normalize_value("ph", value=15, unit="pH")["status"] == N.INVALID
    assert N.normalize_value("water_activity", value=1.2, unit="aw")["status"] == N.INVALID
    assert N.normalize_value("water_activity")["status"] == N.UNKNOWN


def test_percent_fraction_and_moisture_basis():
    assert N.normalize_value("salt_content", value=2, unit="percent")["canonical_value"] == pytest.approx(0.02)
    assert N.normalize_value("salt_content", value=2)["status"] == N.AMBIGUOUS
    assert N.normalize_value("dry_matter", value=20, unit="fraction")["status"] == N.INVALID
    assert N.normalize_value("moisture_content", value=70, unit="percent")["status"] == N.AMBIGUOUS
    assert N.normalize_value("moisture_content", value=70, unit="percent", basis="WET")["status"] == N.VALID
    assert N.normalize_value("moisture_content", value=150, unit="percent", basis="WET")["status"] == N.INVALID
    assert N.normalize_value("moisture_content", value=150, unit="percent", basis="DRY")["status"] == N.VALID


def test_interval_order_and_trajectory():
    assert N.normalize_value("temp_medium", low=190, high=170, unit="degC")["status"] == N.INVALID
    t = N.normalize_value("temp_core", trajectory=[(0, 20), (60, 55), (120, 70)], location="CORE")
    assert t["value_type"] == "TRAJECTORY" and t["status"] == N.VALID
    assert N.normalize_value("temp_core", trajectory=[(0, 20), (0, 55)], location="CORE")["status"] == N.INVALID
    assert N.normalize_value("temp_core", trajectory=[(0, 20), (5, 30)])["status"] == N.AMBIGUOUS


def test_time_units_and_qvalue_adapter():
    assert N.normalize_value("time_duration", value=2, unit="h")["canonical_value"] == 7200
    r = N.from_qvalue("time_duration", {"status": "RANGE", "low": 15, "high": 20, "unit": "min", "raw": "15/20MIN"})
    assert r["value_type"] == "INTERVAL" and r["raw"] == "15/20MIN"
    c = N.from_qvalue("temp_medium", {"status": "CENSORED", "unit": "degC", "censor": {"kind": "GT_STATED", "limit": 100}, "raw": ">100C"})
    assert c["value_type"] == "INTERVAL" and c["open_high"] is True
    assert N.from_qvalue("pressure", {"status": "UNKNOWN", "raw": None})["value_type"] == "UNKNOWN"


def test_basis_retention_censoring_method_and_combination():
    assert N.classify_basis("FRESH_WEIGHT")["basis_id"] == "MB-001" and N.classify_basis(None)["basis_id"] == "MB-008"
    assert N.can_combine_basis("MB-001", "MB-002")[0] is False and N.can_combine_basis("MB-008", "MB-008")[0] is False and N.can_combine_basis("MB-001", "MB-001")[0] is True
    assert N.classify_retention_type("USDA-RETN-R6", "RETENTION_TR_OR_AR", True)["retention_type_id"] == "RT-004"
    assert N.classify_retention_type("BOGNAR-2002", "TRUE_RETENTION", True)["retention_type_id"] == "RT-001"
    pe = N.classify_retention_type("PHENOL-EXPLORER-3.6", "FRESH_WEIGHT", True)
    assert pe["retention_type_id"] == "RT-003" and pe["status"] == N.AMBIGUOUS
    assert N.can_combine_retention("RT-001", "RT-003")[0] is False and N.can_combine_retention("RT-004", "RT-004")[0] is False
    assert N.classify_censoring({"status": "UNKNOWN"})["name"] == "NOT_REPORTED"
    assert N.classify_censoring({"status": "CENSORED", "censor": {"kind": "GT_CAP", "limit": 97.5}})["name"] == "ABOVE_CAP"
    assert N.classify_censoring({"status": "MEASURED", "value": 1.0})["name"] == "DETECTED"
    assert N.classify_method(None)["name"] == "UNKNOWN" and N.classify_method("HPLC-DAD analysis")["name"] == "HPLC" and N.classify_method(None, "CALCULATION")["name"] == "CALCULATION"


def test_outputs_validate_against_schema_and_registries_consistent():
    import csv
    import json
    from pathlib import Path

    import jsonschema
    root = Path(__file__).resolve().parents[2]
    sch = json.loads((root / "registry/schemas/condition_value_v1.schema.json").read_text())
    v = jsonschema.Draft202012Validator(sch)
    outs = [N.normalize_value("temp_core", value=70, unit="degC"), N.normalize_value("ph"), N.normalize_value("temp_medium", qualitative="boiling"),
            N.normalize_value("pressure", value=15, unit="psi"), N.normalize_value("temp_medium", low=170, high=190, unit="degC"), N.from_qvalue("time_duration", {"status": "MEASURED", "value": 5, "unit": "min", "raw": "5 min"})]
    for o in outs:
        v.validate(o)
    for name in ("condition_variable_registry_v1", "measurement_basis_registry_v1", "retention_type_registry_v1", "censoring_registry_v1", "measurement_method_registry_v1", "measurement_location_registry_v1", "heat_transfer_mode_registry_v1", "value_type_registry_v1"):
        rows = list(csv.DictReader(open(root / f"registry/{name}.csv", newline="", encoding="utf-8")))
        ids = [r[list(r)[0]] for r in rows]
        assert rows and len(ids) == len(set(ids)), name
    assert {r["name"] for r in csv.DictReader(open(root / "registry/value_type_registry_v1.csv"))} == set(N.VALUE_TYPES)
