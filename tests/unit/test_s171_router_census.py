"""S171 / D-075 M1: counts-only route census of the router demo over a seeded recipe sample.

Synthetic records carry a sentinel that must never reach the output. The engine stays 23a, no COND is consumed and
the report is NON_CITABLE. No real-data number here.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.mechanism import router_census as RC
from culinarystate.mechanism import router_demo as RD
from culinarystate.quantity import rc2_dryrun as D

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"
VC = "SVAR-000009"


def records(n: int = 6) -> list[dict]:
    return [{"recipe_id": f"SYN-{SENTINEL}-{i}", "source_family": ("FOODCOM", "A1_BBC_GOOD_FOOD")[i % 2],
             "ingredient_lines": ["500 g potatoes", "2 carrots"],
             "steps": ["Boil the potatoes for 20 minutes.", f"Roast the carrots {SENTINEL}. Stir well."]
             if i != 3 else []}
            for i in range(n)]


def _boil_key():
    items = RD.route_text("Boil the potatoes for 20 minutes.", index=RD.EvidenceIndex.from_rows([]),
                          target_svar=VC)["items"]
    return items[0]["ingredient_id"], items[0]["process_id"]


def _row(evd_id, ing, proc, svar=VC, status="MEASURED"):
    return {"id": evd_id, "version": 1, "status": "ACTIVE", "tier": "E3", "source_id": "SRC-1",
            "matrix": {"ingredient_id": ing}, "process": {"process_id": proc},
            "target": {"state_variable_id": svar, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": status, "value": 60.0, "unit": "%", "raw": "60"}},
            "verification": {"status": "UNVERIFIED"}}


def _tool():
    spec = importlib.util.spec_from_file_location("router_demo_census", ROOT / "tools/router_demo_census.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_index_pairs_lists_measured_pairs_for_the_target_only():
    idx = RD.EvidenceIndex.from_rows([_row("E1", "ING-1", "PROC-1"), _row("E2", "ING-2", "PROC-1", status="UNKNOWN"),
                                      _row("E3", "ING-3", "PROC-2", svar="SVAR-X")])
    assert idx.pairs(VC) == {("ING-1", "PROC-1")}
    assert idx.ingredients(VC) == {"ING-1"}


def test_report_is_counts_only_non_citable_and_engine_23a():
    rep = RC.census_from_records(records(), seed="7", size=5, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    text = json.dumps(rep)
    assert SENTINEL not in text and "SYN-" not in text
    D.assert_counts_only(rep)
    assert rep["contains_ids"] is False and rep["contains_text"] is False and rep["citable"] is False
    assert "NON_CITABLE" in rep["labels"] and rep["engine_mode"] == "23a" and rep["conditions_consumed"] is False
    assert rep["counts_as_human_gate"] is False


def test_counts_add_up_without_evidence():
    rep = RC.census_from_records(records(), seed="7", size=6, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    assert rep["recipes_seen"] == 6 and rep["recipes_sampled"] == 6 and rep["texts_with_steps"] == 5
    assert rep["items"] > 0 and sum(rep["route"].values()) == rep["items"]
    assert rep["route"].get("DIRECT", 0) == 0 and rep["route"]["UNKNOWN"] == rep["items"]
    assert rep["items_linked"] + rep["items_unlinked"] == rep["items"]
    assert rep["items_with_process"] + rep["items_without_process"] == rep["items"]
    assert rep["reason_counts"]["NO_LINKED_INGREDIENT"] == rep["items_unlinked"] > 0  # "Stir well."
    assert rep["recipes_with_any_direct"] == 0


def test_direct_counted_and_coverage_reported_with_evidence():
    ing, proc = _boil_key()
    idx = RD.EvidenceIndex.from_rows([_row("E1", ing, proc), _row("E2", "ING-ZZ", proc)])
    rep = RC.census_from_records(records(), seed="7", size=6, index=idx, target_svar=VC)
    assert rep["route"]["DIRECT"] == 5 and rep["recipes_with_any_direct"] == 5
    assert rep["direct_by_process"] == {proc: 5}
    cov = rep["evidence_coverage"]
    assert cov["evd_pairs_for_target"] == 2 and cov["evd_pairs_seen_in_sample"] == 1
    assert cov["evd_ingredients_for_target"] == 2 and cov["sample_ingredients_with_target_evidence"] == 1
    assert cov["sample_distinct_pairs"] >= 1 and cov["sample_distinct_ingredients"] >= 1


def test_deterministic_and_target_required():
    a = RC.census_from_records(records(), seed="7", size=4, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    b = RC.census_from_records(records(), seed="7", size=4, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    assert a == b
    with pytest.raises(ValueError):
        RC.census_from_records(records(), seed="7", size=4, index=RD.EvidenceIndex.from_rows([]), target_svar="")


def test_exception_counted_by_class_name_only(monkeypatch):
    def boom(*a, **k):
        raise KeyError(SENTINEL)
    monkeypatch.setattr(RC.RD, "route_text", boom)
    rep = RC.census_from_records(records(), seed="7", size=6, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    assert rep["exceptions_by_class"] == {"KeyError": 5} and SENTINEL not in json.dumps(rep)


def test_cli_writes_once_and_refuses_protected_places(tmp_path):
    tool = _tool()
    out = tmp_path / "census.json"
    src = lambda families, root: iter(records())  # noqa: E731
    argv = ["--seed", "7", "--sample-size", "6", "--out", str(out), "--root", str(tmp_path), "--no-baseline-check",
            "--evd", str(tmp_path / "missing.jsonl")]
    (tmp_path / "missing.jsonl").write_text("")
    assert tool.main(argv, record_source=src) in (0, 3)
    rep = json.loads(out.read_text())
    assert rep["baseline_check"] == "SKIPPED_BY_FLAG" and rep["code_provenance"]["code_sha256"]
    with pytest.raises(SystemExit):
        tool.main(argv, record_source=src)  # refuses overwrite
    bad = argv[:5] + [str(tmp_path / "ledgers" / "x.json")] + argv[6:]
    with pytest.raises(SystemExit):
        tool.main(bad, record_source=src)
