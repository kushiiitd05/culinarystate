"""Step 17b Rung A counts-only measurement and read-only dry-run (DRAFT_PENDING_16c).

The synthetic report covers synthetic fixtures and the 17 synthetic hard-case
prompts and is labelled SYNTHETIC (never gold). The dry-run CLI samples recipes by
sha256(seed || recipe_id) rank and reports integer counts only. The real data bundle
is absent here: the CLI is exercised with injected synthetic records carrying
sentinel tokens that must never reach the output. No real-data number is produced.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.extraction import rung_a_measure as M
from culinarystate.quantity import rc2_dryrun as D

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"
COMMITTED = ROOT / "reports/step17/rung_a_synthetic_counts.json"


def _tool(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def records(n: int = 6) -> list[dict]:
    out = []
    for i in range(n):
        out.append({"recipe_id": f"SYN-{SENTINEL}-{i}", "source_family": ("FOODCOM", "A1_BBC_GOOD_FOOD")[i % 2],
                    "ingredient_lines": [f"200 g {SENTINEL} onion"],
                    "steps": [f"Heat the oil. Add 200 g {SENTINEL}onion and fry for 5 minutes.",
                              "Stir it, then bake at 180°C for 20 minutes."] if i != 3 else []})
    return out


@pytest.fixture(scope="module")
def synthetic() -> dict:
    return M.synthetic_report(ROOT)


# ---------------------------------------------------------------- synthetic report
def test_synthetic_report_is_labelled_synthetic_counts_only_and_has_zero_invented(synthetic):
    D.assert_counts_only(synthetic)
    assert synthetic["label"] == "SYNTHETIC_NOT_GOLD" and synthetic["counts_as_human_gate"] is False
    assert synthetic["contains_text"] is False and synthetic["contains_ids"] is False
    for part in ("fixtures", "hard_cases"):
        assert synthetic[part]["invented_count"] == 0 and synthetic[part]["exceptions"] == {}
    assert synthetic["hard_cases"]["texts"] == 17
    assert synthetic["fixtures"]["texts"] == len(M.SYNTHETIC_FIXTURES)
    blob = json.dumps(synthetic)
    for word in ("onion", "synthetic", "frying", "SYNTHETIC-HC"):
        assert word not in blob


def test_synthetic_report_has_validator_counts_per_v_and_failure_codes(synthetic):
    fx = synthetic["fixtures"]
    assert set(fx["validators"]) == {"V1", "V2", "V3", "V4"}
    for v in fx["validators"].values():
        assert set(v) == {"issues", "unknown", "not_checked", "texts_failed"}
    assert fx["validators"]["V1"]["issues"] == {} and fx["validators"]["V2"]["texts_failed"] == 0
    assert set(fx["failures"]) == {"extract_mentions", "link", "ground_quantity", "build_events", "resolve_refs"}
    assert fx["ambiguity_count"] >= 1 and fx["mentions"]["ACTION"] >= 1


def test_synthetic_report_is_deterministic_and_the_committed_file_reproduces(tmp_path, synthetic):
    assert M.synthetic_report(ROOT) == synthetic
    tool = _tool("step17b_rung_a_synthetic_report")
    out = tmp_path / "counts.json"
    assert tool.main(["--out", str(out)]) == 0
    assert json.loads(out.read_text()) == json.loads(COMMITTED.read_text())
    with pytest.raises(SystemExit):
        tool.main(["--out", str(out)])


def test_hard_case_catalog_is_read_not_written():
    path = ROOT / "annotation/hard_case_catalog_v2_DRAFT.jsonl"
    before = path.read_bytes()
    prompts = M.hard_case_prompts(ROOT)
    assert len(prompts) == 17 and path.read_bytes() == before


# ---------------------------------------------------------------- seeded sampling
def test_seeded_sample_ranks_by_sha256_of_seed_and_recipe_id():
    recs = [{"recipe_id": f"R{i}"} for i in range(50)]
    got = M.seeded_sample(recs, "s1", 10)
    want = sorted(recs, key=lambda r: (hashlib.sha256(b"s1" + r["recipe_id"].encode()).hexdigest(),
                                       r["recipe_id"]))[:10]
    assert got == want
    assert M.seeded_sample(list(reversed(recs)), "s1", 10) == want
    assert M.seeded_sample(recs, "s2", 10) != want
    assert len(M.seeded_sample(recs, "s1", 1000)) == 50


def test_seeded_sample_skips_records_without_a_recipe_id():
    assert M.seeded_sample([{"recipe_id": None}, {}, {"recipe_id": "R1"}], "s", 5) == [{"recipe_id": "R1"}]


def test_record_summary_is_counts_only_with_no_ids_or_text():
    report = M.summarise_records(records(), seed="seed-1", size=4)
    D.assert_counts_only(report)
    blob = json.dumps(report)
    for banned in (SENTINEL, "SYN-", "onion", "Heat the", "seed-1"):
        assert banned not in blob
    t = report["totals"]
    assert t["recipes_seen"] == 6 and t["recipes_sampled"] == 4
    assert t["recipes_sampled"] == t["recipes_with_steps"] + t["recipes_without_steps"]
    assert t["invented_count"] == 0 and set(report["by_family"]) <= {"FOODCOM", "A1_BBC_GOOD_FOOD"}
    assert report["sample_seed_sha256"] == hashlib.sha256(b"seed-1").hexdigest()
    assert t["rule_compiler_floor"]["events"] >= 0


# ---------------------------------------------------------------- dry-run CLI
def test_dryrun_cli_with_injected_records_writes_counts_only(tmp_path):
    tool = _tool("step17b_rung_a_dryrun")
    out = tmp_path / "dry.json"
    code = tool.main(["--seed", "7", "--sample-size", "5", "--out", str(out)],
                     record_source=lambda fams, root: iter(records()))
    assert code == 0
    text = out.read_text()
    assert SENTINEL not in text and "SYN-" not in text
    report = json.loads(text)
    assert report["baseline_check"] == "PASS_BEFORE_AND_AFTER"
    assert report["totals"]["recipes_sampled"] == 5 and report["sample_size_requested"] == 5
    assert report["status"] == "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY" and report["counts_as_human_gate"] is False
    with pytest.raises(SystemExit):
        tool.main(["--seed", "7", "--out", str(out), "--no-baseline-check"],
                  record_source=lambda fams, root: iter(records()))


def test_dryrun_cli_refuses_protected_destinations(tmp_path):
    tool = _tool("step17b_rung_a_dryrun")
    for rel in ("ledgers/x.json", "data/x.json", "exports/x.json", "annotation/gold/x.json"):
        with pytest.raises(SystemExit):
            tool.main(["--seed", "1", "--root", str(tmp_path), "--out", str(tmp_path / rel), "--no-baseline-check"],
                      record_source=lambda fams, root: iter(records()))
        assert not (tmp_path / rel).exists()


def test_dryrun_cli_refuses_to_run_when_the_ledger_baseline_cannot_be_checked(tmp_path, capsys):
    tool = _tool("step17b_rung_a_dryrun")
    code = tool.main(["--seed", "1", "--root", str(tmp_path), "--out", str(tmp_path / "r.json")],
                     record_source=lambda fams, root: iter(records()))
    assert code == 2 and not (tmp_path / "r.json").exists()
    assert "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN" in capsys.readouterr().out


def test_dryrun_cli_seed_is_required():
    tool = _tool("step17b_rung_a_dryrun")
    with pytest.raises(SystemExit):
        tool.main(["--no-baseline-check"], record_source=lambda fams, root: iter(records()))


@pytest.mark.skipif((ROOT / "data/raw/tasteset/TASTEset.csv").exists(), reason="local data bundle present")
def test_dryrun_cli_reports_missing_inputs_without_fabricating_counts(tmp_path):
    tool = _tool("step17b_rung_a_dryrun")
    out = tmp_path / "missing.json"
    assert tool.main(["--seed", "1", "--families", "TASTESET", "--out", str(out), "--no-baseline-check"]) == 3
    report = json.loads(out.read_text())
    assert report["family_status"] == {"TASTESET": "INPUT_MISSING"}
    assert report["totals"]["recipes_seen"] == 0 and report["totals"]["recipes_sampled"] == 0
