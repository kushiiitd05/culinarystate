"""S178 FIX-PHYS: the Layer 1 census counts the SCI-A M1 corpus check (bound temperatures inside until-clauses by role) and the new
cue axes; the endpoint report carries the check. Synthetic recipes only."""
from __future__ import annotations

import json

from culinarystate.simulation import binding_census as BC
from culinarystate.simulation import condition_binding as CB
from tests.unit.test_s178_phys2_reports import _load

RECIPES = [
    {"recipe_id": "R1", "source_family": "TEST", "steps": ["Roast the turkey until the thigh reaches 180 F.", "Bake until golden at 350 F."]},
    {"recipe_id": "R2", "source_family": "TEST", "steps": ["Boil the jam until it reaches 220 F.", "Heat the oil until it reaches 375 F."]},
    {"recipe_id": "R3", "source_family": "TEST", "steps": ["Boil in a pressure cooker at 15 psi (250 F) for 10 minutes.",
                                                           "Bake the custard in a water bath at 325 F for 40 minutes.",
                                                           "Bake at 200C/180C fan for 20 minutes."]},
]


def test_census_counts_the_until_clause_check_and_the_cue_axes(tmp_path):
    rep = BC.census_from_records(iter(RECIPES), seed="20261104", size=10, workers=1, binder=CB.Binder.load())
    fx = rep["fixphys_layer1"]
    assert rep["census_version"] == "binding-census-L1-0.3.0-draft" and rep["binder_version"] == CB.VERSION
    roles = fx["temperatures_in_until_clauses_by_role"]
    assert roles.get("TARGET_UNTIL_CLAUSE", 0) >= 1 and roles.get("EXEMPT_SYRUP_OR_CANDY", 0) >= 1
    bound = fx["bound_text_stated_temperature_inside_an_until_clause_by_role"]
    assert set(bound) <= {"EXEMPT_SYRUP_OR_CANDY", "EXEMPT_LIQUID_OR_MEDIUM_SUBJECT", "EXEMPT_SETTING_PHRASE",
                          "EXEMPT_MEDIUM_THERMOMETER"}, bound  # a target is never bound as the medium temperature
    assert fx["cue_axis_events_by_family"]["pressure_cue"] and fx["cue_axis_events_by_family"]["water_bath_cue"]
    assert fx["temperature_flags"]["FAN_VS_CONVENTIONAL_UNRESOLVED"] == 1 and fx["temperature_range_events"] >= 1
    p = tmp_path / "c.json"
    p.write_text(json.dumps(rep))
    tool = _load("s178_phys_endpoint_report")
    out, md = tmp_path / "e.json", tmp_path / "e.md"
    assert tool.main(["--census", f"TEST={p}", "--out", str(out), "--out-md", str(md)]) == 0
    e = json.loads(out.read_text())
    assert e["summary"]["until_clause_check"]["all_non_bbc_families"]["until_clauses"] == fx["until_clauses"]
    assert "Until-clause check" in md.read_text()
