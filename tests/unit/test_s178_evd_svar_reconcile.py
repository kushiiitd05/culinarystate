"""S178 EVD lane, T2-C03-R3: SVAR reconciliation on a tiny synthetic tree (counts, FUTURE ids, stale-quote scan)."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
_spec = importlib.util.spec_from_file_location("s178_evd_svar_reconcile", ROOT / "tools/s178_evd_svar_reconcile.py")
SR = importlib.util.module_from_spec(_spec)
sys.modules["s178_evd_svar_reconcile"] = SR
_spec.loader.exec_module(SR)


def jl(path, recs):
    path.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")


def tree(tmp_path):
    led = tmp_path / "ledgers" / "data"
    led.mkdir(parents=True)
    sv = lambda i, v, fam="CHEMICAL": {"id": f"SVAR-{i:06d}", "version": v, "status": "ACTIVE", "family": fam, "canonical_name": f"n{i}"}   # noqa: E731
    jl(led / "SVAR.jsonl", [sv(1, 1), sv(1, 2), sv(2, 1), sv(3, 1, "PHYSICAL")])
    ev = lambda i, s: {"id": f"EVD-{i:06d}", "version": 1, "status": "ACTIVE", "target": {"state_variable_id": f"SVAR-{s:06d}"}}   # noqa: E731
    jl(led / "EVD.jsonl", [ev(1, 1), ev(2, 2), ev(3, 3)])
    for n in ("COND", "SRC", "MEAS", "SNAP"):
        (led / f"{n}.jsonl").write_text("", encoding="utf-8")
    reg = tmp_path / "registry"
    reg.mkdir()
    cols = ["state_variable_id", "name", "family", "status", "current_row_count"]
    rows = [["SVAR-000001", "a", "CHEMICAL", "ACTIVE", "1"], ["SVAR-000002", "b", "CHEMICAL", "DUPLICATE", "1"], ["SVAR-000003", "c", "PHYSICAL", "ACTIVE", "1"],
            ["SVAR-FUT-001", "f", "PHYSICAL", "FUTURE", "0"]]
    with open(reg / "state_variable_registry_v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    with open(reg / "svar_duplicate_mapping_v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["duplicate_id", "canonical_id", "relation"])
        w.writerow(["SVAR-000002", "SVAR-000001", "DUPLICATE_SAME_ANALYTE"])
    return tmp_path


def test_lines_distinct_ids_registry_and_canonical(tmp_path):
    root = tree(tmp_path)
    d = SR.build(root)
    t = d["table"]
    L, R, E, M = t["ledger_SVAR_jsonl"], t["registry_csv"], t["evd_usage"], t["duplicate_mapping"]
    assert (L["version_lines"], L["distinct_ids"], L["ids_with_two_or_more_versions"]) == (4, 3, 1)
    assert L["lines_by_family"] == {"CHEMICAL": 3, "PHYSICAL": 1} and L["distinct_ids_by_family_latest_version"] == {"CHEMICAL": 2, "PHYSICAL": 1}
    assert R["rows"] == 4 and R["FUTURE_rows"] == 1 and R["non_FUTURE_rows"] == 3 and R["non_FUTURE_ids_equal_ledger_distinct_ids"] is True
    assert E["distinct_svar_ids_on_active_rows"] == 3 and E["ledger_ids_not_used_by_any_active_row"] == 0
    assert M["canonical_variables_after_mapping_on_active_rows"] == 2                       # SVAR-000002 folds into SVAR-000001
    assert "4 version lines = 3 distinct ids" in t["one_line_summary"]


def test_stale_quote_regex_flags_count_wording_but_not_line_wording():
    assert SR.STALE.search("registry (355 SVAR: 354 chemical, 1 physical)")
    assert SR.STALE.search("SVAR.jsonl 355 rows: 354 CHEMICAL")
    assert not SR.STALE.search("355 lines / 254 registry rows")
    assert SR.FIXED.search("355 version records = 224 distinct ids")


def test_run_is_deterministic_and_does_not_touch_ledgers(tmp_path):
    root = tree(tmp_path)
    before = {p.name: p.read_bytes() for p in (root / "ledgers" / "data").iterdir()}
    r1 = SR.run(tmp_path / "o1", root)
    r2 = SR.run(tmp_path / "o2", root)
    assert r1 == r2
    assert before == {p.name: p.read_bytes() for p in (root / "ledgers" / "data").iterdir()}
