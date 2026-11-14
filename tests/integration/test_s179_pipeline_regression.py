"""Source-to-replay/route/packet/strict-display engineering regression, not scientific gold."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("pipeline_regression", ROOT / "tools/s179_pipeline_regression.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def recipe(family, number):
    return {"recipe_id": f"{family}{number}", "source_family": family, "title": "synthetic",
            "ingredient_lines": ["100 g carrot"], "steps": ["Boil carrot in water for 5 minutes."]}


def test_preselection_is_balanced_order_independent_and_never_uses_outcomes():
    rows = [recipe(f, i) for f in ["A", "B", "C", "D", "E"] for i in range(20)]
    a = tool.select_recipes(rows, families=["A", "B", "C", "D", "E"], per_family=10, seed="fixed")
    b = tool.select_recipes(reversed(rows), families=["A", "B", "C", "D", "E"], per_family=10, seed="fixed")
    assert [(r["source_family"], r["recipe_id"]) for r in a] == [(r["source_family"], r["recipe_id"]) for r in b]
    assert len(a) == 50
    assert all(sum(r["source_family"] == f for r in a) == 10 for f in ["A", "B", "C", "D", "E"])


def test_selection_refuses_missing_stratum_and_source_hash_detects_change():
    rows = [recipe("A", 1)]
    with pytest.raises(ValueError): tool.select_recipes(rows, families=["A", "B"], per_family=1, seed="fixed")
    original = tool.source_hash(rows[0])
    rows[0]["steps"].append("Discard the water.")
    assert tool.source_hash(rows[0]) != original


def test_synthetic_real_components_connect_replay_route_packet_and_strict_refusal():
    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    context = StrictDemoContext.load(public=True, host="127.0.0.1")
    result = tool.run_case(recipe("SYNTHETIC", 1), context)
    assert result["parse_events"] > 0 and result["engine_events"] > 0
    assert result["route_items"] > 0 and result["packet_count"] > 0
    assert result["adapter_invented_count"] == 0
    assert result["invalid_packet_refs"] == 0 and result["handler_errors"] == 0
    assert result["table_retention_numbers"] == 0
    assert result["citable"] is False
    assert len(result["replay_sha256"]) == len(result["display_sha256"]) == 64


def test_fixed_fifty_case_engineering_goldens_match_source_bound_repeat():
    golden = json.loads((ROOT / "reports/s179/pipeline_regression_golden_2026-11-12.json").read_text())
    baseline = json.loads((ROOT / golden["baseline_path"]).read_text())
    repeat = json.loads((ROOT / golden["repeat_path"]).read_text())
    manifest = json.loads((ROOT / golden["manifest_path"]).read_text())
    assert tool.sha(ROOT / golden["baseline_path"]) == golden["baseline_sha256"]
    assert tool.sha(ROOT / golden["repeat_path"]) == golden["repeat_sha256"]
    assert tool.sha(ROOT / golden["manifest_path"]) == golden["manifest_sha256"]
    assert len({row["recipe_id"] for row in baseline["cases"]}) == len(manifest["units"]) == 50
    assert baseline["cases"] == repeat["cases"]
    assert tool.digest(baseline["cases"]) == golden["core_sha256"] == repeat["core_sha256"]
    assert repeat["second_run_matches_baseline"] is True
    assert baseline["totals"]["invalid_packet_refs"] == baseline["totals"]["handler_errors"] == 0
    assert baseline["scientific_gate_pass"] is golden["scientific_gate_pass"] is False
    for expected, case in zip(golden["cases"], baseline["cases"]):
        assert all(case[key] == value for key, value in expected.items())
