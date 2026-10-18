from culinarystate.eda.report import build_report, cell_key, to_html, to_markdown
from culinarystate.ingest.acquire import Snapshot
from culinarystate.ingest.usda_r6 import R6Row
from culinarystate.ingest.usda_r6_build import build
from culinarystate.ledgers.store import LedgerStore


def _store(tmp_path):
    st = LedgerStore(tmp_path)
    rows = [R6Row(1, "0101", "15", "FINFISH,BAKED,W/DRIPPINGS", "401", "Vitamin C", "80", "09/1975"),
            R6Row(2, "0102", "15", "FINFISH,BAKED,WO/DRIPPINGS", "401", "Vitamin C", "70", "09/1975"),
            R6Row(3, "0103", "15", "FINFISH,BAKED,WO/DRIPPINGS", "301", "Calcium", "100", "09/1975")]
    build(st, rows, [Snapshot("u", "p", "d" * 64, 1, "2026-10-18T05:00:00+00:00", 200)])
    return st


def test_cell_key_separates_modifiers(tmp_path):
    st = _store(tmp_path)
    cond = {c["id"]: c for c in st.all_latest("COND")}
    keys = {cell_key(e, cond) for e in st.all_latest("EVD")}
    assert len(keys) == 3                                     # W/ vs WO/ drippings are different cells


def test_report_sections_and_render(tmp_path):
    rep = build_report(_store(tmp_path))
    ev = rep["evidence"]
    assert ev["rows"] == 3 and ev["censored_rows"] == 1 and ev["replicate_rows_same_cell_same_group"] == 0
    assert rep["ledgers"]["EVD"]["records"] == 3
    assert "<table>" in to_html(rep) and "## Evidence" in to_markdown(rep)
