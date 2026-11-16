"""Metrics keep false negatives, false positives and UNKNOWN coverage separate."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("gate_diagnostic", Path(__file__).parents[2] / "tools/s179_gate_set_diagnostic.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def test_operational_unknown_counts_as_not_activated_but_is_not_hidden():
    result = gate.binary_metrics([True, True, False, False], [True, None, True, None])
    assert result["counts"] == {"TP": 1, "FN": 1, "FP": 1, "TN": 1}
    assert result["unknown"] == {"all": 2, "gold_positive": 1, "gold_negative": 1}
    assert result["false_negative_rate"]["value"] == .5
    assert result["false_positive_rate"]["value"] == .5
    assert result["precision"]["denominator"] == 2


def test_wilson_zero_denominator_is_null_and_zero_failures_not_certainty():
    assert gate.rate(0, 0) == {"numerator": 0, "denominator": 0, "value": None, "wilson95": None}
    out = gate.rate(0, 5)
    assert out["value"] == 0 and 0 < out["wilson95"][1] < 1
    assert gate.rate(5, 5)["wilson95"][0] < 1


def test_freeze_checks_annotations_and_producer_bytes(tmp_path):
    f = tmp_path / "labels.csv"
    f.write_text("before")
    manifest = {"files": {str(f): gate.sha(f)}}
    gate.check_manifest(manifest)
    f.write_text("after")
    import pytest
    with pytest.raises(ValueError, match="changed"):
        gate.check_manifest(manifest)
