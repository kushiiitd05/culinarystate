import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("audit_v3", Path(__file__).parents[2] / "tools/s179_strict_runtime_audit_v3.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_display_numbers_need_finite_value_unit_and_known_basis():
    p = {"mode": "ABSTAIN", "citable": False, "labels": ["NON_CITABLE"], "detail": {
        "recipe_display": {"steps": [{"physics": {"numbers": [
            {"value": 90., "unit": "degC", "basis": "TEXT_STATED", "status": "MEASURED"},
            {"value": None, "unit": "degC", "basis": "TEXT_STATED", "status": "MEASURED"},
            {"value": 1., "basis": "SCENARIO", "status": "SCENARIO"},
            {"value": 1., "unit": "min", "basis": "UNKNOWN", "status": "UNKNOWN"}]}}]}}}
    out = audit.inspect_payload(p)
    assert out["display_numbers"] == 4
    assert out["display_provenance_violations"] == 3
