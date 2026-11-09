"""S178 PHYS3 (T4-C21-R1): Step 26g census with Layer 1 bindings, counts only. Synthetic records; no real-data number here.

The Layer 1 records are written by the real Layer 1 binder (``binding_census`` with a records dir) from the same synthetic recipes, so
the join, the decode and the binding rule are tested end to end. The S166 census path (``census_chain`` + ``tools/step26g_census.py``)
is not edited: its census must equal the baseline arm of the new tool byte for byte.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import binding_census as BC
from culinarystate.simulation import census_chain as C
from culinarystate.simulation import condition_binding as CB

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"


def records(n: int = 6) -> list[dict]:
    return [{"recipe_id": f"SYN-{SENTINEL}-{i}", "source_family": ("FOODCOM", "WIKIBOOKS")[i % 2],
             "steps": [f"Dice the potatoes {SENTINEL}.", "Boil the potatoes for 20 minutes.",
                       "Preheat the oven to 200C.", "Bake for 25 mins, covered.",
                       "Heat the oil. Add the onion and fry for 5 minutes."] if i != 2 else []} for i in range(n)]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # the fork pool pickles functions by module name
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tool():
    return _load("s178_phys3_census_l1", "tools/s178_phys3_census_l1.py")


@pytest.fixture(scope="module")
def l1_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("l1")
    BC.census_from_records(records(9), seed="7", size=9, records_dir=d)
    return d


def test_report_is_counts_only_and_sentinel_free(tool, l1_dir):
    rep = tool.census_from_records(records(), seed="7", size=6, layer1_dirs=[l1_dir])
    D.assert_counts_only(rep)
    text = json.dumps(rep)
    assert SENTINEL not in text and "SYN-" not in text
    assert rep["contains_ids"] is False and rep["contains_text"] is False and rep["counts_as_human_gate"] is False
    assert rep["applicability_supplied"] == 0


def test_baseline_arm_is_the_s166_census_byte_for_byte(tool, l1_dir):
    old = C.census_from_records(records(), seed="7", size=6)
    new = tool.census_from_records(records(), seed="7", size=6, layer1_dirs=[l1_dir])
    assert new["baseline_no_bindings"]["census"] == old["census"]
    assert new["baseline_no_bindings"]["census_sha256"] == old["census_sha256"]
    for k in ("recipes_seen", "recipes_sampled", "texts_with_steps", "engine_events", "adapter_invented_excluded",
              "adapter_issue_codes", "exceptions_by_class", "seed_sha256"):
        assert new[k] == old[k], k
    # with no Layer 1 directory both arms are the S166 census
    none = tool.census_from_records(records(), seed="7", size=6, layer1_dirs=[])
    assert none["with_layer1_bindings"]["census_sha256"] == old["census_sha256"] == none["baseline_no_bindings"]["census_sha256"]


def test_flushing_in_blocks_gives_the_same_census(tool, l1_dir, monkeypatch):
    whole = tool.census_from_records(records(9), seed="7", size=9, layer1_dirs=[l1_dir])
    monkeypatch.setattr(tool, "FLUSH_EVERY", 2)
    blocks = tool.census_from_records(records(9), seed="7", size=9, layer1_dirs=[l1_dir])
    assert json.dumps(blocks, sort_keys=True) == json.dumps(whole, sort_keys=True)
    assert blocks["baseline_no_bindings"]["census_sha256"] == C.census_from_records(records(9), seed="7", size=9)["census_sha256"]


def test_duplicate_recipe_ids_are_refused_like_s166(tool, l1_dir):
    recs = records(4) + [records(4)[1]]
    with pytest.raises(Exception, match="counted twice"):
        tool.census_from_records(recs, seed="7", size=5, layer1_dirs=[l1_dir])


def test_s166_files_are_unchanged_against_git_head():
    for rel in ("tools/step26g_census.py", "src/culinarystate/simulation/census_chain.py",
                "src/culinarystate/simulation/recipe_adapter.py"):
        try:
            blob = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"], capture_output=True, timeout=30, check=True).stdout
        except (OSError, subprocess.SubprocessError):
            pytest.skip("git not available")
        assert hashlib.sha256(blob).hexdigest() == hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), rel


def test_layer1_bindings_drop_missing_reasons_for_bound_events(tool, l1_dir):
    rep = tool.census_from_records(records(), seed="7", size=6, layer1_dirs=[l1_dir])
    l1 = rep["layer1"]
    assert l1["records_event_not_in_replay"] == 0 and l1["records_event_in_replay"] == l1["records_for_sampled_recipes"] > 0
    assert l1["decode_exceptions_by_class"] == {} and l1["duplicate_event_rows"] == 0
    p = rep["paired_by_event"]["sim_aa_1"]
    drop = p["input_reasons_before_after_dropped"]
    for r in ("MISSING_DURATION", "MISSING_MEDIUM", "MISSING_TEMPERATURE_PROFILE"):
        assert drop[r]["dropped"] > 0 and drop[r]["after"] == drop[r]["before"] - drop[r]["dropped"], r
    assert drop["MISSING_WATER_RATIO"]["dropped"] == 0  # Layer 1 v0 never binds the water ratio
    assert p["events_with_a_missing_reason_dropped"] <= p["events_with_l1_record"] <= p["events"]
    assert sum(r["events"] for r in p["l1_events_reason_sets_after"]) == p["events_with_l1_record"]
    # the lid cue of "Bake ..., covered" is bound
    assert l1["contract_bindings_by_input"]["lid_state"] > 0
    assert rep["simulate_by_system"]["sim_aa_1"] == {"baseline": 0, "with_layer1": 0}
    bound = rep["with_layer1_bindings"]["census"]["systems"]["sim_aa_1"]
    assert bound["route"]["SIMULATE"] == 0 and bound["applicability"]["UNKNOWN"] == bound["events"]


def test_decoded_records_give_the_live_binder_bindings(tool, l1_dir):
    """Round trip: the bindings rebuilt from the written records equal the binder's own bindings for the same text."""
    binder = CB.Binder.load()
    rows = [json.loads(line) for f in sorted(Path(l1_dir).glob("*.jsonl")) for line in f.read_text().splitlines() if line.strip()]
    by_recipe: dict[str, list[dict]] = {}
    for r in rows:
        by_recipe.setdefault(r["recipe_id"], []).append(r)
    for rec in records(9):
        if not rec["steps"]:
            continue
        live = binder.bind_text("\n".join(rec["steps"]), "en")["bindings"]
        got = tool.bindings_from_records(by_recipe[rec["recipe_id"]])
        assert sorted(map(repr, got)) == sorted(map(repr, live))
    assert any(isinstance(b.value, Fraction) for b in got)


def test_workers_identical(tool, l1_dir):
    a = tool.census_from_records(records(9), seed="7", size=9, layer1_dirs=[l1_dir], systems=("sim_aa_1", "sim_chl_1"))
    b = tool.census_from_records(records(9), seed="7", size=9, layer1_dirs=[l1_dir], systems=("sim_aa_1", "sim_chl_1"), workers=2)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert set(a["with_layer1_bindings"]["census"]["systems"]) == {"sim_aa_1", "sim_chl_1"}


def test_unknown_event_ids_and_bad_values_are_counted(tool, l1_dir, tmp_path):
    rows = [json.loads(line) for f in sorted(Path(l1_dir).glob("*.jsonl")) for line in f.read_text().splitlines() if line.strip()]
    rows[0] = {**rows[0], "event_id": "E9999"}
    bad = dict(rows[1])
    bad["inputs"] = {**bad["inputs"], "duration": {"value": "not-a-number", "status": "MEASURED", "basis": "TEXT_STATED", "span": None}}
    rows[1] = bad
    (tmp_path / "part-00000.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    rep = tool.census_from_records(records(9), seed="7", size=9, layer1_dirs=[tmp_path])
    assert rep["layer1"]["records_event_not_in_replay"] == 1
    assert rep["layer1"]["decode_exceptions_by_class"] == {"ValueError": 1}
    assert SENTINEL not in json.dumps(rep)


def test_merge_census_sums_and_refuses_mismatched_constants(tool):
    a = {"sets": 1, "x": {"y": 2, "v": "C1"}, "flag": True}
    assert tool.merge_census(a, {"sets": 2, "x": {"y": 3, "v": "C1", "z": 1}, "flag": True}) == \
        {"sets": 3, "x": {"y": 5, "v": "C1", "z": 1}, "flag": True}
    with pytest.raises(ValueError):
        tool.merge_census(a, {"x": {"v": "C2"}})


def test_param_ledger_reader(tool, tmp_path):
    assert tool.human_verified_param_rows(tmp_path) == ("ABSENT", 0)
    p = tmp_path / "ledgers" / "data"
    p.mkdir(parents=True)
    rows = [{"id": "PARAM-1", "verification": {"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": "2026-11-09"}},
            {"id": "PARAM-2", "verification": {"status": "AI_DRAFTED", "verifier": "claude"}},
            {"id": "PARAM-3", "verification": {"status": "HUMAN_VERIFIED", "verifier": "Parv"}}]
    (p / "PARAM.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert tool.human_verified_param_rows(tmp_path) == ("PRESENT", 1)


def test_cli_writes_once_with_gate_and_refuses_bad_arguments(tool, l1_dir, tmp_path):
    out = tmp_path / "c.json"
    src = lambda fams, root: iter(records())  # noqa: E731
    args = ["--seed", "7", "--sample-size", "4", "--layer1-records", str(l1_dir), "--out", str(out), "--no-baseline-check"]
    assert tool.main(args, record_source=src) == 0
    rep = json.loads(out.read_text())
    assert SENTINEL not in out.read_text()
    assert rep["simulate_gate"]["result"] == "PASS" and rep["simulate_gate"]["simulate_total"] == 0
    assert rep["simulate_gate"]["param_rows_human_verified"] == 0 and rep["baseline_check"] == "SKIPPED_BY_FLAG"
    assert rep["code_unchanged_during_run"] is True
    with pytest.raises(SystemExit):  # no overwrite
        tool.main(args, record_source=src)
    for bad in (["--workers", "25"], ["--layer1-records", str(tmp_path / "missing")]):
        with pytest.raises(SystemExit):
            tool.main(args[:-3] + ["--out", str(tmp_path / "d.json"), "--no-baseline-check"] + bad, record_source=src)
    with pytest.raises(SystemExit):  # protected place
        tool.main(["--seed", "7", "--layer1-records", str(l1_dir), "--root", str(tmp_path), "--out",
                   str(tmp_path / "data" / "x.json"), "--no-baseline-check"], record_source=src)


def test_cli_refuses_without_ledger_baseline(tool, l1_dir, tmp_path, capsys):
    code = tool.main(["--seed", "1", "--layer1-records", str(l1_dir), "--root", str(tmp_path), "--out", str(tmp_path / "r.json")],
                     record_source=lambda fams, root: iter(records()))
    assert code == 2 and "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN" in capsys.readouterr().out
    assert not (tmp_path / "r.json").exists()


def test_cli_refuses_to_write_when_simulate_appears(tool, l1_dir, tmp_path, monkeypatch, capsys):
    real = tool.census_from_records

    def fake(*a, **k):
        rep = real(*a, **k)
        rep["simulate_by_system"]["sim_aa_1"]["with_layer1"] = 1
        return rep

    monkeypatch.setattr(tool, "census_from_records", fake)
    out = tmp_path / "s.json"
    code = tool.main(["--seed", "7", "--sample-size", "3", "--layer1-records", str(l1_dir), "--out", str(out), "--no-baseline-check"],
                     record_source=lambda fams, root: iter(records()))
    assert code == 5 and not out.exists() and "SIMULATE_ROUTE_WITHOUT_HUMAN_VERIFIED_PARAM" in capsys.readouterr().out


def test_index_merges_contiguous_lines_and_keeps_only_wanted(tool, tmp_path):
    lines = [{"recipe_id": "A", "event_id": "E1"}, {"recipe_id": "A", "event_id": "E2"}, {"recipe_id": "B", "event_id": "E1"},
             {"recipe_id": "A", "event_id": "E3"}]
    f = tmp_path / "part-00000.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in lines))
    idx, c = tool.l1_index([f], {"A"})
    assert len(idx["A"]) == 2 and "B" not in idx and c["lines"] == 4 and c["lines_for_sampled_recipes"] == 3
    tool._CTX.update(l1_files=[f], l1_index=idx, handles={})
    try:
        assert [r["event_id"] for r in tool.read_l1("A")] == ["E1", "E2", "E3"]
    finally:
        for fh in tool._CTX["handles"].values():
            fh.close()
        tool._CTX.clear()
