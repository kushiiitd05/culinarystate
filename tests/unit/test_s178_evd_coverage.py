"""S178 EVD lane, T2-C13-R1: pure helpers of the coverage tool (routable pairs, family roll-ups, rendering)."""
from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
_spec = importlib.util.spec_from_file_location("s178_evd_coverage", ROOT / "tools/s178_evd_coverage.py")
CV = importlib.util.module_from_spec(_spec)
sys.modules["s178_evd_coverage"] = CV
_spec.loader.exec_module(CV)


def evd(i, ing, proc, svar="SVAR-000009", rf="MEASURED", status="ACTIVE"):
    return {"id": f"EVD-{i}", "status": status, "matrix": {"ingredient_id": ing}, "process": {"process_id": proc},
            "target": {"state_variable_id": svar}, "derived": {"retention_factor": {"status": rf}} if rf else {}}


ROWS = [evd(1, "ING-1", "PROC-A"), evd(2, "ING-1", "PROC-A", svar="SVAR-000010"), evd(3, "ING-2", "PROC-A", rf="CENSORED"), evd(4, "ING-3", "PROC-B", rf="UNKNOWN"),
        evd(5, "ING-4", "PROC-B", rf=None), evd(6, None, "PROC-B"), evd(7, "ING-5", None), evd(8, "ING-6", "PROC-B", status="DEPRECATED")]


def test_routable_pairs_need_ing_proc_active_and_measured_or_censored():
    assert CV.routable_pairs(ROWS) == {("ING-1", "PROC-A"), ("ING-2", "PROC-A")}
    assert CV.routable_pairs(ROWS, "SVAR-000009") == {("ING-1", "PROC-A"), ("ING-2", "PROC-A")}
    assert CV.routable_pairs(ROWS, "SVAR-000010") == {("ING-1", "PROC-A")}


def test_events_by_family_counts_events_whose_proc_has_evd():
    fam = {"PROC-A": "WET_HEAT", "PROC-B": "WET_HEAT", "PROC-C": "COOLING"}
    out = CV.events_by_family({"PROC-A": 10, "PROC-B": 5, "PROC-C": 7, "PROC-X": 3}, fam, {"PROC-A", "PROC-C"})
    assert out["WET_HEAT"] == {"events": 15, "events_with_evd_proc": 10, "procs_with_events": 2, "procs_with_events_and_evd": 1}
    assert out["COOLING"]["events_with_evd_proc"] == 7
    assert out[CV.UNMAPPED]["events"] == 3 and out[CV.UNMAPPED]["events_with_evd_proc"] == 0


def test_pairs_by_family_hit_rate():
    fam = {"PROC-A": "WET_HEAT", "PROC-B": "DRY_HEAT"}
    sample = {("ING-1", "PROC-A"), ("ING-9", "PROC-A"), ("ING-1", "PROC-B")}
    out = CV.pairs_by_family(sample, {("ING-1", "PROC-A")}, fam)
    assert out["WET_HEAT"] == {"sample_distinct_pairs": 2, "sample_pairs_with_evd": 1}
    assert out["DRY_HEAT"] == {"sample_distinct_pairs": 1, "sample_pairs_with_evd": 0}


def test_family_order_puts_known_families_first_then_the_rest_sorted():
    assert CV.ordered({"ZZZ", "WET_HEAT", "DRY_HEAT", "AAA"}) == ["DRY_HEAT", "WET_HEAT", "AAA", "ZZZ"]


def test_figure_is_well_formed_svg_and_csv_has_one_row_per_family():
    table = [{"process_family": "DRY_HEAT", "corpus_events": 10, "pct_events_with_evd_proc": 50.0, "evd_rows": 3, "evd_procs": 1, "evd_ing_proc_pairs_routable": 2,
              "sample_distinct_pairs": 4, "sample_pairs_with_evd": 1, "pct_sample_pairs_with_evd": 25.0, "router_vitc_direct_items_gated_full_nonBBC": 0},
             {"process_family": "COOLING", "corpus_events": 20, "pct_events_with_evd_proc": 10.0, "evd_rows": 1, "evd_procs": 1, "evd_ing_proc_pairs_routable": 1,
              "sample_distinct_pairs": 8, "sample_pairs_with_evd": 0, "pct_sample_pairs_with_evd": 0.0, "router_vitc_direct_items_gated_full_nonBBC": 5}]
    d = {"table": table}
    svg = CV.render_svg(d)
    ET.fromstring(svg)                                                       # parses as XML
    assert "DRY_HEAT" in svg and "COOLING" in svg
    assert len(CV.render_csv(d).splitlines()) == 3
