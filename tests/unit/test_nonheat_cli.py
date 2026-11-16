"""S176 L-NH: tools/nonheat_layer_run.py end to end on synthetic records (L1 census, L2 run, counts-only reports)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SENT = "ZQXSENTINEL"


@pytest.fixture(scope="module")
def tool():
    spec = importlib.util.spec_from_file_location("nonheat_layer_run", ROOT / "tools/nonheat_layer_run.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["nonheat_layer_run"] = m  # worker processes unpickle the tool's functions by module name
    spec.loader.exec_module(m)
    return m


def source(families, root):
    for i in range(8):
        yield {"recipe_id": f"SYN-{i}", "source_family": families[0],
               "steps": [f"Dice the carrots {SENT}.", "Boil the carrots for 20 minutes.", "Chill the carrots in the fridge for 2 hours.",
                         "Freeze the carrots at -18C for 3 hours.", "Soak the beans overnight, then drain and rinse.",
                         "Whisk the eggs until frothy.", "Store in the fridge for up to 3 days."] if i != 3 else []}


def run(tool, tmp_path, workers=1, name="a"):
    argv = ["--seed", "7", "--sample-size", "8", "--workers", str(workers), "--families", "WIKIBOOKS", "--no-baseline-check",
            "--root", str(ROOT), "--l1-out", str(tmp_path / f"{name}_l1.json"), "--l2-out", str(tmp_path / f"{name}_l2.json"),
            "--l1-records-dir", str(tmp_path / f"{name}_r1"), "--l2-records-dir", str(tmp_path / f"{name}_r2")]
    assert tool.main(argv, record_source=source) == 0
    return json.loads((tmp_path / f"{name}_l1.json").read_text()), json.loads((tmp_path / f"{name}_l2.json").read_text())


def test_reports_are_counts_only_and_consistent(tool, tmp_path):
    l1, l2 = run(tool, tmp_path)
    assert SENT not in json.dumps(l1) + json.dumps(l2)
    assert l1["record"] == "NONHEAT_BINDING_CENSUS_L1" and l2["record"] == "NONHEAT_SCENARIO_L2_SUMMARY"
    assert l1["baseline_check"] == "SKIPPED_BY_FLAG" and l2["citable"] is False and l2["counts_as_human_gate"] is False
    assert l2["counts"]["events_by_family"] == l1["events_by_family"]
    for fam, n in l1["events_by_family"].items():
        assert sum(l2["counts"]["status"].get(fam, {}).values()) == n
        assert sum(l2["counts"]["transition"].get(fam, {}).values()) == n
    assert l2["counts"]["bracket_order_check"]  # computed events were order-checked
    flat = json.dumps(l2["counts"]["bracket_order_check"])
    assert "VIOLATION" not in flat
    assert len(l2["scenario_registry_nonheat_sha256"]) == 64 and len(l2["records_manifest_sha256"]) == 64


def test_records_are_written_and_l2_matches_l1_row_for_row(tool, tmp_path):
    l1, l2 = run(tool, tmp_path)
    r1 = [json.loads(l) for f in sorted((tmp_path / "a_r1").glob("*.jsonl")) for l in f.read_text().splitlines()]
    r2 = [json.loads(l) for f in sorted((tmp_path / "a_r2").glob("*.jsonl")) for l in f.read_text().splitlines()]
    assert len(r1) == len(r2) == l1["nonheat_events"] > 0
    assert [(a["recipe_id"], a["event_id"]) for a in r1] == [(b["recipe_id"], b["event_id"]) for b in r2]
    assert all(b["layer"] == "SCENARIO" and a["layer"] == "TEXT_STATED" for a, b in zip(r1, r2))
    assert SENT not in json.dumps(r1) + json.dumps(r2)


def test_workers_give_identical_counts_and_refuses_overwrite(tool, tmp_path):
    a1, a2 = run(tool, tmp_path, 1, "w1")
    b1, b2 = run(tool, tmp_path, 2, "w2")
    drop = ("code_provenance", "started_at_utc", "ended_at_utc", "wall_seconds_l1", "wall_seconds_l2", "workers",
            "records_manifest_sha256", "code_unchanged_during_run")
    assert {k: v for k, v in a1.items() if k not in drop} == {k: v for k, v in b1.items() if k not in drop}
    for r in (a2, b2):
        r["counts"].pop("l1_files")  # one part file per chunk: depends on the worker count only
    assert {k: v for k, v in a2.items() if k not in drop} == {k: v for k, v in b2.items() if k not in drop}
    with pytest.raises(SystemExit):
        tool.main(["--seed", "7", "--sample-size", "8", "--families", "WIKIBOOKS", "--no-baseline-check",
                   "--l1-out", str(tmp_path / "w1_l1.json"), "--l2-out", str(tmp_path / "x_l2.json"),
                   "--l1-records-dir", str(tmp_path / "x1"), "--l2-records-dir", str(tmp_path / "x2")], record_source=source)


def test_records_dir_inside_the_repository_outside_data_is_refused(tool, tmp_path):
    with pytest.raises(SystemExit):
        tool.main(["--seed", "7", "--sample-size", "8", "--families", "WIKIBOOKS", "--no-baseline-check",
                   "--l1-out", str(tmp_path / "y_l1.json"), "--l2-out", str(tmp_path / "y_l2.json"),
                   "--l1-records-dir", str(ROOT / "reports/should_not_exist_nh"), "--l2-records-dir", str(tmp_path / "y2")],
                  record_source=source)
    assert not (ROOT / "reports/should_not_exist_nh").exists()
