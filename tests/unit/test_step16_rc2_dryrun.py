"""Synthetic controls for the read-only rc2 grounding dry-run (S154).

The dry-run reports counts only. These tests plant unique sentinel tokens in
synthetic recipe ids and lines and assert they never reach the report.
"""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.quantity import rc2_dryrun as D

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"


def recipes():
    return [
        {"recipe_id": f"SYN-{SENTINEL}-1", "source_family": "FOODCOM",
         "ingredient_lines": [f"200 g {SENTINEL} flour", "2 tbsp synthetic oil", "", "1 lb plus 2 oz synthetic",
                              f"3 {SENTINEL}eggs", "a pinch of synthetic salt"]},
        {"recipe_id": f"SYN-{SENTINEL}-2", "source_family": "A1_BBC_GOOD_FOOD",
         "ingredient_lines": ["1 cup synthetic milk", "2 x 400g cans synthetic tomatoes", "   ",
                              f"1 cup/{SENTINEL}zz synthetic"]},
        {"recipe_id": f"SYN-{SENTINEL}-3", "source_family": "GUTENBERG_SEGMENT", "ingredient_lines": []},
        {"recipe_id": f"SYN-{SENTINEL}-4", "source_family": "WIKIBOOKS", "ingredient_lines": ["2 or 3 synthetic carrots"]},
    ]


def run(records=None, **kw):
    return D.summarise(records if records is not None else recipes(), **kw)


def test_report_contains_no_text_ids_or_ingredient_words():
    report = run()
    text = json.dumps(report)
    for banned in (SENTINEL, "flour", "synthetic", "SYN-", "eggs", "carrots", "pinch"):
        assert banned not in text
    D.assert_counts_only(report)
    assert report["contains_recipe_text"] is False and report["counts_as_human_gate"] is False


def test_line_and_recipe_totals_are_consistent():
    t = run()["totals"]
    assert t["recipes"] == 4 and t["recipes_without_ingredient_lines"] == 1
    assert t["lines_total"] == 11 and t["lines_blank"] == 2 and t["lines_grounded"] == 9
    for axis in ("mass_route", "unit_resolution", "ast_root", "arithmetic_status", "q_level"):
        assert sum(t[axis].values()) == t["lines_grounded"]
    assert t["mass_route"]["AST_EXACT_PHYSICAL"] == 1 and t["mass_route"]["AST_PACKAGE_SOURCE_STATED"] == 1
    assert t["lines_with_rc2_mass"] == 2 and t["exceptions"] == {}


def test_per_family_counts_and_legacy_locale_map_are_used():
    r = run()
    assert set(r["by_family"]) == {"FOODCOM", "A1_BBC_GOOD_FOOD", "GUTENBERG_SEGMENT", "WIKIBOOKS"}
    assert r["by_family"]["FOODCOM"]["unit_resolution"]["VOLUME_LOCALE_CONVENTION"] == 1
    # UK has no cup convention in the frozen catalogue: stays ambiguous, never guessed.
    assert r["by_family"]["A1_BBC_GOOD_FOOD"]["unit_resolution"]["VOLUME_LOCALE_AMBIGUOUS"] >= 1
    assert r["locale_source"] == "LEGACY_SOURCE_FAMILY_LOCALE_MAP"


def test_unsupported_expressions_and_legacy_disagreement_are_counted():
    t = run()["totals"]
    # "1 lb plus 2 oz" and the slash after "1 cup/..." (conservatively read as an operator).
    assert t["flags"]["UNSUPPORTED_COMPOUND_AMOUNT"] == 2
    assert t["flags"]["COMPATIBILITY_CHANNEL_MASKED"] == 1
    assert t["legacy_vs_rc2_mass"]["legacy_MEASURED__rc2_UNKNOWN"] == 1


def test_flag_payloads_after_a_colon_are_dropped():
    assert D.flag_code("second_unit_ignored:ZQXSENTINEL") == "second_unit_ignored"
    assert D.flag_code("non_standard_vessel:katori") == "non_standard_vessel"
    assert D.flag_code("free text with spaces") == "OTHER_FLAG"


def test_workers_give_identical_counts_and_inputs_are_not_mutated():
    data = recipes()
    before = copy.deepcopy(data)
    assert run(data, workers=1)["totals"] == run(data, workers=2, chunk_size=1)["totals"]
    assert data == before


def test_exceptions_are_counted_by_class_name_only(monkeypatch):
    real = D.ground_quantity_rc2

    def boom(raw, context, *, schema):
        if SENTINEL in raw:
            raise ValueError(f"bad {raw}")
        return real(raw, context, schema=schema)

    monkeypatch.setattr(D, "ground_quantity_rc2", boom)
    report = run(workers=1)
    assert report["totals"]["exceptions"] == {"ValueError": 3}
    assert SENTINEL not in json.dumps(report)


def test_limit_stops_after_n_recipes():
    assert run(limit=2)["totals"]["recipes"] == 2


@pytest.mark.parametrize("bad", [{"free text": 1}, {"k": "two words"}, {"k": ["x" * 200]},
                                 {"k": {"nested": f"{SENTINEL} flour"}}])
def test_counts_only_guard_rejects_free_text(bad):
    with pytest.raises(D.DryRunError):
        D.assert_counts_only(bad)


def test_writer_refuses_protected_existing_and_data_paths(tmp_path):
    report = run()
    for rel in ("ledgers/data/x.json", "data/out.json", "exports/evd/x.json", "ledgers/recipe_base/x.json"):
        with pytest.raises(D.DryRunError):
            D.write_report(tmp_path / rel, report, root=tmp_path)
    target = tmp_path / "reports/step16/counts.json"
    D.write_report(target, report, root=tmp_path)
    assert json.loads(target.read_text())["totals"] == report["totals"]
    with pytest.raises(D.DryRunError):
        D.write_report(target, report, root=tmp_path)


def _tool():
    spec = importlib.util.spec_from_file_location("dryrun_tool", ROOT / "tools/step16_rc2_grounding_dryrun.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_uses_injected_records_and_records_skipped_baseline(tmp_path, capsys):
    tool = _tool()
    out = tmp_path / "reports/counts.json"
    code = tool.main(["--root", str(tmp_path), "--out", str(out), "--no-baseline-check", "--workers", "1"],
                     record_source=lambda families, root: iter([r for r in recipes() if r["source_family"] in families]))
    assert code == 0
    report = json.loads(out.read_text())
    assert report["baseline_check"] == "SKIPPED_BY_FLAG" and SENTINEL not in out.read_text()
    assert SENTINEL not in capsys.readouterr().out


def test_cli_refuses_to_run_when_baseline_check_fails(tmp_path):
    tool = _tool()
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/baseline_ledger_hashes_08a_v1.csv").write_text("path,sha256,bytes\nledgers/data/EVD.jsonl,00,1\n")
    code = tool.main(["--root", str(tmp_path), "--out", str(tmp_path / "reports/c.json")],
                     record_source=lambda families, root: iter(recipes()))
    assert code == 2 and not (tmp_path / "reports/c.json").exists()


def test_cli_reports_missing_family_inputs_without_text(tmp_path):
    tool = _tool()
    out = tmp_path / "reports/m.json"

    def missing(families, root):
        raise FileNotFoundError(str(root / "data/external/foodcom/recipes.parquet"))

    code = tool.main(["--root", str(tmp_path), "--out", str(out), "--no-baseline-check", "--families", "FOODCOM"],
                     record_source=missing)
    assert code == 3
    assert json.loads(out.read_text())["family_status"] == {"FOODCOM": "INPUT_MISSING"}
