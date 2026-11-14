"""S178 FIX-EVAL: SCI-B E8 (the D5 leakage audit's id scan skipped all of reports/s178/). Synthetic files in tmp_path only.

Failure scenario (review): S recipe ids named in the ANALYSIS, CORPUS or EVD outputs under reports/s178/ went unscanned.
"""
from __future__ import annotations

from tests.unit.test_s178_analysis_helpers import load_tool

LT = load_tool("s178_leakage_audit_d5")
IDS = {"REC-000001", "REC-000002"}


def _w(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_other_lanes_outputs_under_reports_s178_are_scanned(tmp_path):
    _w(tmp_path, "reports/s178/analysis/table.md", "row REC-000001 and REC-000002")
    _w(tmp_path, "reports/s178/corpus/x.json", '{"r": "REC-000002"}')
    _w(tmp_path, "reports/s178/split_registry_units_v1.csv", "SPL,D5-S1-001,draft,recipe_id=REC-000001")
    _w(tmp_path, "benchmark/d5/d5_draft_S_v1.csv", "REC-000001,REC-000002")
    _w(tmp_path, "data/derived/hidden.csv", "REC-000001")                               # data/ stays out of scope
    _w(tmp_path, "notes.md", "nothing here")
    got = LT.id_reference_scan(tmp_path, IDS)
    assert got["files_with_distinct_s_ids"] == {"reports/s178/analysis/table.md": 2, "reports/s178/corpus/x.json": 1}
    assert got["n_files_under_reports_s178"] == 2
    assert set(got["allow_listed_files"]) == {"reports/s178/split_registry_units_v1.csv", "benchmark/d5/d5_draft_S_v1.csv"}
    assert got["allow_listed_files"]["benchmark/d5/d5_draft_S_v1.csv"] == {"distinct_s_ids": 2, "reason": "D5_S_DRAFT_THE_IDS_THEMSELVES"}


def test_allow_list_is_explicit_file_paths_not_prefixes():
    assert all(not k.endswith("/") for k in LT.ID_SCAN_ALLOW)
    assert not any(k.startswith("reports/s178/") and k.count("/") > 2 for k in LT.ID_SCAN_ALLOW)   # no other lane's subfolder
    src = (LT.ROOT / "tools/s178_leakage_audit_d5.py").read_text(encoding="utf-8")
    assert 'rel.startswith("reports/s178/")' not in src
