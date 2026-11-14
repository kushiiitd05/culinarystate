import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("reproduction", Path(__file__).parents[2] / "tools/s179_artifact_reproduction.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def test_compares_metrics_but_explicitly_discloses_provenance_differences():
    a = {"recipes_sampled": 5, "code_provenance": {"commit": "old"}, "records_written": True}
    b = {"recipes_sampled": 5, "code_provenance": {"commit": "new"}, "records_written": False}
    out = tool.compare(a, b)
    assert out["metrics_equal"] and not out["raw_json_equal"]
    assert set(out["metadata_difference_keys"]) == {"code_provenance", "records_written"}


def test_changed_counts_are_not_normalized_away():
    out = tool.compare({"counts": {"DIRECT": 4}}, {"counts": {"DIRECT": 5}})
    assert not out["metrics_equal"]
    assert out["metric_difference_keys"] == ["counts"]
