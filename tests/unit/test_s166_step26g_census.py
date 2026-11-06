"""S166: committed Step 26g simulability census (review block J8).

Parv's 2026-11-04 census (reports/step26/simulability_census_real_sample_counts.json) came from an ad hoc
chain, so it could not be rerun on the fixed Rung A. This pins a committed chain
Rung A -> event adapter -> replay -> build_simulation_inputs -> simulability_census over a seeded sample,
counts only. Synthetic records carry a sentinel that must never reach the output. No real-data number here.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import census_chain as C
from culinarystate.simulation.recipe_adapter import census_sha256

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"
PARV_KEYS = {"adapter_invented_excluded", "adapter_issue_codes", "census", "census_sha256", "chain", "contains_ids",
             "contains_text", "engine_events", "exceptions_by_class", "label", "recipes_sampled", "seed_sha256",
             "status", "texts_with_steps"}


def records(n: int = 6) -> list[dict]:
    return [{"recipe_id": f"SYN-{SENTINEL}-{i}", "source_family": ("FOODCOM", "A1_BBC_GOOD_FOOD")[i % 2],
             "ingredient_lines": [f"200 g {SENTINEL} onion"],
             "steps": [f"Heat the oil. Add 200 g {SENTINEL}onion and fry for 5 minutes.",
                       "Stir it, then bake at 180°C for 20 minutes."] if i != 3 else []}
            for i in range(n)]


def _tool():
    spec = importlib.util.spec_from_file_location("step26g_census", ROOT / "tools/step26g_census.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_report_is_counts_only_and_keeps_parvs_layout():
    rep = C.census_from_records(records(), seed="7", size=5)
    text = json.dumps(rep)
    assert SENTINEL not in text and "SYN-" not in text
    D.assert_counts_only(rep)
    assert PARV_KEYS <= set(rep)
    assert rep["chain"] == "RUNG_A|EVENT_ADAPTER|REPLAY|STEP26G:sim_aa_1"  # guard-safe form of Parv's chain label
    assert rep["contains_ids"] is False and rep["contains_text"] is False
    assert rep["label"] == "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD" and rep["status"] == "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY"


def test_counts_add_up_and_nothing_is_simulated_without_bindings():
    sample = C.census_from_records(records(), seed="7", size=6)
    assert sample["recipes_seen"] == 6 and sample["recipes_sampled"] == 6
    assert sample["texts_with_steps"] == 5  # record 3 has no steps
    sys_ = sample["census"]["systems"]["sim_aa_1"]
    assert sample["engine_events"] == sys_["events"] > 0
    assert sys_["route"]["SIMULATE"] == 0 and sys_["route"]["SIM_PROHIBITED"] == sys_["events"]
    assert sample["census"]["sets"] == 5
    assert sample["census"]["sim_run_ids_minted"] == 0 and sample["census"]["estimates_emitted"] == 0
    assert sample["census_sha256"] == census_sha256(sample["census"])


def test_deterministic_and_sample_follows_the_seed():
    a = C.census_from_records(records(), seed="7", size=3)
    assert json.dumps(a, sort_keys=True) == json.dumps(C.census_from_records(records(), seed="7", size=3), sort_keys=True)
    assert a["seed_sha256"] == __import__("hashlib").sha256(b"7").hexdigest()


def test_an_exception_is_counted_by_class_name_only(monkeypatch):
    class Boom(C.RungA):
        def run(self, *a, **k):
            raise ValueError(f"{SENTINEL} secret text")

    rep = C.census_from_records(records(), seed="7", size=6, rung=Boom())
    assert rep["exceptions_by_class"] == {"ValueError": 5}
    assert SENTINEL not in json.dumps(rep) and rep["census"]["sets"] == 0


def test_unknown_system_is_refused():
    with pytest.raises(ValueError):
        C.census_from_records(records(), seed="7", size=2, system_id="sim_unknown")


def test_cli_writes_once_with_provenance_and_refuses_protected_places(tmp_path):
    tool = _tool()
    out = tmp_path / "census.json"
    src = lambda fams, root: iter(records())  # noqa: E731
    assert tool.main(["--seed", "7", "--sample-size", "4", "--out", str(out), "--no-baseline-check"],
                     record_source=src) == 0
    rep = json.loads(out.read_text())
    assert SENTINEL not in out.read_text()
    assert rep["baseline_check"] == "SKIPPED_BY_FLAG" and rep["recipes_sampled"] == 4
    assert rep["code_provenance"]["src_tree_sha256"] and rep["family_status"]["FOODCOM"] == "READ"
    with pytest.raises(SystemExit):
        tool.main(["--seed", "7", "--out", str(out), "--no-baseline-check"], record_source=src)
    for rel in ("ledgers/x.json", "data/x.json"):
        with pytest.raises(SystemExit):
            tool.main(["--seed", "7", "--root", str(tmp_path), "--out", str(tmp_path / rel), "--no-baseline-check"],
                      record_source=src)


def test_cli_refuses_when_the_ledger_baseline_cannot_be_checked(tmp_path, capsys):
    tool = _tool()
    code = tool.main(["--seed", "1", "--root", str(tmp_path), "--out", str(tmp_path / "r.json")],
                     record_source=lambda fams, root: iter(records()))
    assert code == 2 and "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN" in capsys.readouterr().out
    assert not (tmp_path / "r.json").exists()
