"""S178 FIX-PHYS: SCI-A M6 (Q3 PROPOSED caveat) and m8 (split basis kinds, one reach-70 test) in the sensitivity generator; the
generalised stated-liquid report labels. Synthetic records only."""
from __future__ import annotations

import copy
import json

from tests.unit.test_s178_phys2_reports import _bracket, _l2, _load, _write


def test_m6_caveat_and_m8_basis_split(tmp_path):
    sens = _load("s178_phys_sensitivity")
    heat = tmp_path / "heat"
    a = _bracket(100, 20, 90, 95, 10)
    a["bases"]["bath_c"], a["bases"]["duration_min"] = "L1:PHYSICAL_DEFINITION", "L1:TEXT_STATED"
    b = _bracket(200, 30, 60, 65, 0)  # core end 60 C but minutes above 70 > 0 would say yes: the end value says no
    b["core_minutes_above_70"] = 0.5
    _write(heat, [_l2("PROC-000019", copy.deepcopy(a), copy.deepcopy(a), copy.deepcopy(a)),
                  _l2("PROC-000001", copy.deepcopy(b), copy.deepcopy(b), copy.deepcopy(b))])
    out, md = tmp_path / "s.json", tmp_path / "s.md"
    assert sens.main(["--heat-l2", str(heat), "--out", str(out), "--out-md", str(md)]) == 0
    rep = json.loads(out.read_text())
    assert rep["caveat"] == list(sens.CAVEAT_CODES) and rep["boundary_model_axis"] == "OPEN_NOT_COMPUTED" and rep["version"] == sens.VERSION
    for phrase in ("JOINT corners", "ONE boundary-condition model", "pan geometry", "robust within the Robin-at-T_cap model",
                   "consequence of the cap"):
        assert phrase in sens.CAVEAT
    text = md.read_text()
    assert text.index("## Caveat") < text.index("## Heat families") and sens.CAVEAT in text
    assert "bath_PHYSICAL_DEFINITION_duration_TEXT_STATED" in rep["heat"]["WET_HEAT"]["by_input_basis"]
    assert rep["heat"]["DRY_HEAT"]["conclusions"]["core_reaches_70c"]["robust_no"] == 1  # end value 60 C < 70 C
    assert sens._basis_kind("L1:CARRIED_SETPOINT") == "CARRIED_SETPOINT" and sens._basis_kind("SD-012") == "DEFAULT"
    assert sens._basis_kind("L1:TEXT_STATED|PC-001") == "TEXT_STATED"


def test_stated_liquid_report_labels_are_options(tmp_path):
    stated = _load("s178_phys_stated_liquid_report")
    ap_defaults = stated.run_family.__defaults__
    assert ap_defaults[-1] == ("before_l2_0_3_0", "after_l2_0_4_0")
    d = tmp_path / "e"
    d.mkdir()
    rep = stated.run_family("T", d, d, d, d, 1, ("before_l2_0_4_0", "after_l2_0_5_0"))
    assert set(rep["l2"]) == {"before_l2_0_4_0", "after_l2_0_5_0"}
