"""Step 12-local staging writer, EVD diff (G08-9 context, report only) and counts-only report.

PROVISIONAL_PENDING_G12_AUDIT. Synthetic inputs only (see test_step12_local_parsers.py). The staging
area holds raw third-party text and must stay out of git; the committed report holds counts/hashes only.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.evidence import step12_local as S
from culinarystate.ingest import bognar_remaining as B
from culinarystate.ingest import usda_yields_r2 as Y

from tests.unit.test_step12_local_parsers import bognar_text, r2_text

ROOT = Path(__file__).resolve().parents[2]


def evd_file(tmp: Path) -> Path:
    rows = [
        {"id": "EVD-900001", "status": "ACTIVE", "source_family_id": "BOGNAR-2002",
         "extraction_version": "bognar_parser@0.1", "matrix": {"raw_name": "synthetic group one"},
         "process": {"raw_name": "boil", "modifiers": {}}, "target": {"raw_name": "Vitamin C"},
         "provenance": {"locator": "bognar_2002.txt line 9 (Part 2 table 1, boil, A)"}},
        {"id": "EVD-900002", "status": "ACTIVE", "source_family_id": "BOGNAR-2002",
         "extraction_version": "bognar_parser@0.1", "matrix": {"raw_name": "synthetic group two"},
         "process": {"raw_name": "boil", "modifiers": {}}, "target": {"raw_name": "Folate"},
         "provenance": {"locator": "bognar_2002.txt line 99 (Part 2 table 2, boil, A)"}},
        {"id": "EVD-900002", "status": "DEPRECATED", "source_family_id": "BOGNAR-2002",
         "extraction_version": "bognar_parser@0.1", "matrix": {"raw_name": "synthetic group two"},
         "process": {"raw_name": "boil", "modifiers": {}}, "target": {"raw_name": "Folate"},
         "provenance": {"locator": "bognar_2002.txt line 99 (Part 2 table 2, boil, A)"}},
        {"id": "EVD-900003", "status": "ACTIVE", "source_family_id": "USDA-RETN-R6",
         "extraction_version": "usda_r6_parser@0.2", "matrix": {"raw_name": "SYNTHETIC CUT"},
         "process": {"raw_name": "SYNTHETIC CUT,BRAISED", "modifiers": {}}, "target": {"raw_name": "Thiamin"},
         "provenance": {"locator": "retn06.txt line 1"}},
        {"id": "EVD-900004", "status": "ACTIVE", "source_family_id": "PHENOL-EXPLORER-3.6",
         "extraction_version": "phenol_explorer_parser@0.1",
         "matrix": {"raw_name": "SYNTHETIC beef cut A, separable lean"},
         "process": {"raw_name": "braised", "modifiers": {"yield_source": "SYNTH_USDA_2010"}},
         "target": {"raw_name": "Quercetin"}, "derived": {"yield_factor": {"status": "MEASURED", "value": 0.7}},
         "provenance": {"locator": "pe"}},
        {"id": "EVD-900005", "status": "ACTIVE", "source_family_id": "BOGNAR-2002",
         "extraction_version": "bognar_yield@0.1", "matrix": {"raw_name": "Synthetic dish"},
         "process": {"raw_name": "boil", "modifiers": {}}, "target": {"raw_name": "weight yield"},
         "derived": {"yield_factor": {"status": "MEASURED", "value": 0.95}},
         "provenance": {"locator": "bognar_2002.txt line 3 (Part 1 table 2, FOOD_EDIBLE_PART)"}},
    ]
    p = tmp / "EVD.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return p


def parsed() -> tuple[Y.R2Result, B.BognarResult]:
    return Y.parse_r2_text(r2_text()), B.parse_remaining(bognar_text())


# ---------------------------------------------------------------- staging guard
def test_status() -> None:
    assert S.STATUS == "PROVISIONAL_PENDING_G12_AUDIT"
    assert S.DEFAULT_STAGING_DIR == "data/interim/step12_local_staging_v1"


@pytest.mark.parametrize("rel", ["ledgers/data/stage", "ledgers/stage", "exports/evd/stage", "registry/staging/x",
                                 "reports/step12/stage", "src/stage", "tests/stage", "annotation/gold/x", "stage",
                                 "LEDGERS/data/x"])
def test_staging_dir_refuses_tracked_or_protected_areas(tmp_path: Path, rel: str) -> None:
    with pytest.raises(S.StagingError):
        S.guard_staging_dir(tmp_path / rel, root=tmp_path)


def test_staging_dir_allows_ignored_data_area_and_outside_root(tmp_path: Path) -> None:
    assert S.guard_staging_dir(tmp_path / "data" / "interim" / "s", root=tmp_path)
    other = tmp_path / "outside"
    assert S.guard_staging_dir(other / "s", root=tmp_path / "repo")


def test_real_default_staging_dir_is_git_ignored() -> None:
    import subprocess
    r = subprocess.run(["git", "check-ignore", "-q", S.DEFAULT_STAGING_DIR + "/x.jsonl"], cwd=ROOT)
    assert r.returncode == 0


def test_write_staging_files_and_refuse_overwrite(tmp_path: Path) -> None:
    r2, bog = parsed()
    out = tmp_path / "data" / "interim" / "stage"
    written = S.write_staging(out, r2=r2, bognar=bog, root=tmp_path)
    assert set(written) == {"r2_rows.jsonl", "bognar_remaining_cells.jsonl", "bognar_remaining_tables.jsonl"}
    rows = [json.loads(x) for x in (out / "r2_rows.jsonl").read_text(encoding="utf-8").splitlines()]
    assert rows[0]["record"] == "STAGING_HEADER" and rows[0]["status"] == S.STATUS
    assert len(rows) == 1 + len(r2.rows)
    with pytest.raises(S.StagingError):
        S.write_staging(out, r2=r2, bognar=bog, root=tmp_path)


# ---------------------------------------------------------------- diff against EVD (report, never merge)
def test_diff_counts(tmp_path: Path) -> None:
    r2, bog = parsed()
    d = S.diff_against_evd(evd_file(tmp_path), r2=r2, bognar=bog)
    assert d["evd_rows_read_latest_active"] == 4            # EVD-900002 latest version is DEPRECATED
    bg = d["bognar_remaining"]
    assert set(bg["existing_evd_rows_in_remaining_tables"]) == {f"T{t}" for t in B.REMAINING_TABLES}
    assert set(bg["existing_evd_rows_in_remaining_tables"].values()) == {0}
    assert bg["staged_cells_exact_key_in_existing_evd"] == 0
    assert bg["staged_constituent_method_pairs_seen_in_existing_bognar"] >= 1    # Vitamin C + boil (table 1)
    assert bg["g08_9_context_constituents_shared_with_usda_r6"] == 1             # Thiamin
    r = d["r2"]
    assert r["existing_evd_rows_with_yield_factor_by_family"] == {"BOGNAR-2002": 1, "PHENOL-EXPLORER-3.6": 1}
    assert r["pe_rows_with_usda_yield_source"] == 1
    assert r["staged_rows_description_exact_match_in_evd_by_family"] == {"PHENOL-EXPLORER-3.6": 1}
    assert d["resolution"] == "NOT_RESOLVED_REPORT_ONLY"


def test_deprecated_latest_version_is_not_counted(tmp_path: Path) -> None:
    r2, bog = parsed()
    d = S.diff_against_evd(evd_file(tmp_path), r2=r2, bognar=bog)
    assert d["bognar_remaining"]["existing_evd_rows_in_remaining_tables"]["T2"] == 0


# ---------------------------------------------------------------- counts-only report
def test_counts_report_has_no_text(tmp_path: Path) -> None:
    r2, bog = parsed()
    rep = S.counts_report(r2=r2, bognar=bog, diff=S.diff_against_evd(evd_file(tmp_path), r2=r2, bognar=bog),
                          inputs={"r2_csv": {"locator": "data/external/x.csv", "sha256": "a" * 64, "bytes": 10}})
    S.assert_counts_only(rep)
    blob = json.dumps(rep)
    for word in ("SYNTHETIC", "Vitamin", "Thiamin", "boil", "beef", "variant"):
        assert word not in blob
    assert rep["r2"]["rows_staged"] == 3 and rep["bognar_remaining"]["cells_staged"] == len(bog.cells)
    assert rep["status"] == S.STATUS and rep["ledger_rows_appended"] == 0


@pytest.mark.parametrize("bad", [{"x": "Vitamin C"}, {"x": ["boil"]}, {"food name": 1}, {"x": {"y": "beef cut"}},
                                 {"x": 1.5}])
def test_assert_counts_only_rejects_text(bad: dict) -> None:
    with pytest.raises(S.StagingError):
        S.assert_counts_only(bad)


def test_write_report_refuses_overwrite_and_protected(tmp_path: Path) -> None:
    rep = {"status": S.STATUS, "n": 1}
    p = S.write_report(rep, tmp_path / "reports" / "r.json", root=tmp_path)
    assert json.loads(p.read_text(encoding="utf-8")) == rep
    with pytest.raises(S.StagingError):
        S.write_report(rep, p, root=tmp_path)
    with pytest.raises(S.StagingError):
        S.write_report(rep, tmp_path / "ledgers" / "data" / "r.json", root=tmp_path)
    with pytest.raises(S.StagingError):
        S.write_report(rep, tmp_path / "data" / "interim" / "r.json", root=tmp_path)


# ---------------------------------------------------------------- tool
def load_tool():
    spec = importlib.util.spec_from_file_location("stage_tool", ROOT / "tools" / "step12_local_stage.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_tool_end_to_end(tmp_path: Path) -> None:
    mod = load_tool()
    r2p = tmp_path / "r2.csv"
    r2p.write_text(r2_text(), encoding="utf-8")
    txt = tmp_path / "bognar.txt"
    txt.write_text(bognar_text(), encoding="utf-8")
    stage, rep = tmp_path / "data" / "interim" / "stage", tmp_path / "reports" / "counts.json"
    rc = mod.main(["--root", str(tmp_path), "--r2-csv", str(r2p), "--bognar-txt", str(txt),
                   "--evd", str(evd_file(tmp_path)), "--staging-dir", str(stage), "--report", str(rep)])
    assert rc == 0
    data = json.loads(rep.read_text(encoding="utf-8"))
    S.assert_counts_only(data)
    assert set(data["inputs"]) == {"r2_csv", "bognar_txt", "evd"}
    assert len(data["inputs"]["r2_csv"]["sha256"]) == 64
    assert (stage / "r2_rows.jsonl").is_file()
    assert mod.main(["--root", str(tmp_path), "--r2-csv", str(r2p), "--evd", str(evd_file(tmp_path)),
                     "--staging-dir", str(stage), "--report", str(tmp_path / "reports" / "c2.json")]) == 2


def test_tool_requires_an_input_and_reports_missing(tmp_path: Path) -> None:
    mod = load_tool()
    assert mod.main(["--root", str(tmp_path), "--evd", str(evd_file(tmp_path))]) == 2
    assert mod.main(["--root", str(tmp_path), "--r2-csv", str(tmp_path / "nope.csv"),
                     "--evd", str(evd_file(tmp_path))]) == 2


def test_tool_defaults() -> None:
    mod = load_tool()
    assert mod.DEFAULT_R2 == "data/external/usda_yields/cooking_yields_meat_poultry_r2.csv"
    assert mod.DEFAULT_BOGNAR_TXT == "data/raw/bognar/bognar_2002.txt"
    assert mod.DEFAULT_REPORT == "reports/step12/step12_local_counts_v1.json"


def test_existing_key_reads_methods_containing_a_comma(tmp_path: Path) -> None:
    """Real v1 locators look like 'Part 2 table 3, stew, braise, A)': the basis letter must still be read."""
    rows = [{"id": "EVD-900010", "status": "ACTIVE", "source_family_id": "BOGNAR-2002",
             "matrix": {"raw_name": "x"}, "process": {"raw_name": "stew, braise", "modifiers": {}},
             "target": {"raw_name": "Vitamin C"},
             "provenance": {"locator": "bognar_2002.txt line 7 (Part 2 table 2, stew, braise, A)"}}]
    p = tmp_path / "EVD.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    cell = {"table": 2, "constituent_raw": "Vitamin C", "method_raw": "stew, braise", "basis": "A"}
    bog = B.BognarResult(cells=[cell])
    d = S.diff_against_evd(p, bognar=bog)
    assert d["bognar_remaining"]["staged_cells_exact_key_in_existing_evd"] == 1
    assert d["bognar_remaining"]["existing_evd_rows_in_remaining_tables"]["T2"] == 1
