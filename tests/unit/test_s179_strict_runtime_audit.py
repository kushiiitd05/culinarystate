"""Audit must detect omitted provenance as well as explicitly unknown provenance."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("runtime_audit", Path(__file__).parents[2] / "tools/s179_strict_runtime_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def payload():
    return {"mode": "ABSTAIN", "citable": False, "labels": ["NON_CITABLE"], "detail": {
        "numeric_provenance": [], "recipe": {"physics": {"steps": [{
            "stated": {"duration_min": "5", "temperature_c": None},
            "scenario": {"typical_core_end_c": 40, "range_core_end_c": [None, 50]},
            "numeric_provenance": {"stated.duration_min": {"basis": "TEXT_STATED", "status": "MEASURED"},
                "scenario.typical_core_end_c": {"basis": "MODEL_DERIVED", "status": "MODEL_DERIVED"},
                "scenario.range_core_end_c.1": {"basis": "UNKNOWN", "status": "UNKNOWN"}}}]}}}}


def test_counts_each_display_endpoint_and_preserves_unknown():
    result = audit.inspect_payload(payload())
    assert result["numeric_fields"] == 3
    assert result["unknown_numeric_fields"] == 1
    assert result["missing_numeric_provenance"] == 0


def test_omitted_metadata_is_detected_independently_of_complete_flag():
    p = payload()
    p["detail"]["recipe"]["physics"]["numeric_provenance_complete"] = True
    del p["detail"]["recipe"]["physics"]["steps"][0]["numeric_provenance"]["scenario.range_core_end_c.1"]
    assert audit.inspect_payload(p)["missing_numeric_provenance"] == 1


def test_errors_and_citability_and_simulate_are_not_silent_passes():
    p = payload()
    p.update(mode="ABSTAIN_ERROR", citable=True)
    result = audit.inspect_payload(p)
    assert result["handler_errors"] == result["citability_violations"] == 1
    p["mode"] = "SIMULATE"
    assert audit.inspect_payload(p)["unexpected_simulate"] == 1
