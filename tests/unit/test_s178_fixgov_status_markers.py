"""S178 FIX-GOV, GOV-8: machine tables carry their own AI_DRAFTED status, so a table copied out of its folder keeps it.

- registry/ssot_coverage_classes_S178.csv has a ``status`` column, AI_DRAFTED_PENDING_REVIEW on every row;
- the PREREG calc JSON tables carry a top-level ``status`` key, and their producing scripts write it;
- the can-say figures carry AI_DRAFTED in the SVG <desc>; CSVs name their sibling .md in the producing tool's docstring.
"""
from __future__ import annotations

import csv
import json
import xml.dom.minidom
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_ssot_coverage_classes_have_a_status_column_on_every_row():
    with open(ROOT / "registry/ssot_coverage_classes_S178.csv", newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        rows = list(rdr)
    assert rdr.fieldnames == ["section", "class", "owner_or_superseded_by", "rationale", "status"]
    assert rows and all(r["status"] == "AI_DRAFTED_PENDING_REVIEW" for r in rows)


@pytest.mark.parametrize("name", ["power_s178", "ac1_s178"])
def test_prereg_calc_tables_and_scripts_carry_the_marker(name):
    d = json.loads((ROOT / f"reports/orchestration/S178_PREREG_calc/{name}.json").read_text(encoding="utf-8"))
    assert d["status"].startswith("AI_DRAFTED")
    assert '"status": "AI_DRAFTED' in (ROOT / f"reports/orchestration/S178_PREREG_calc/{name}.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("svg", ["fig1_heat_time_temperature_joint.svg", "fig2_foodcom_heat_inputs_by_family.svg", "fig3_foodcom_top_unknown_reasons.svg"])
def test_can_say_figures_say_ai_drafted_in_their_description(svg):
    doc = xml.dom.minidom.parse(str(ROOT / "reports/s178/analysis" / svg))
    assert "AI_DRAFTED" in doc.getElementsByTagName("desc")[0].firstChild.data


def test_evd_coverage_figure_says_ai_drafted():
    doc = xml.dom.minidom.parse(str(ROOT / "reports/s178/evd/fig_evd_coverage_by_family_v1.svg"))
    assert "AI_DRAFTED" in doc.getElementsByTagName("desc")[0].firstChild.data


@pytest.mark.parametrize("tool,sibling", [("tools/s178_analysis_corpus_can_say_render.py", "corpus_can_say_v2.md"),
                                          ("tools/s178_evd_coverage.py", "evd_coverage_vs_corpus_demand_v2.md")])
def test_csv_producers_name_the_sibling_md_that_states_the_status(tool, sibling):
    src = (ROOT / tool).read_text(encoding="utf-8")
    assert "GOV-8" in src and sibling in src
