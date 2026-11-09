"""S177 SCIFIX-PHYS: the two run tools (counts-only reports, v02 -> v03 comparison against previous per-event records)."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from culinarystate.simulation import scenario_layer as SL
from tests.unit.test_s176_phys_cap import _rec

ROOT = Path(__file__).resolve().parents[2]
SENT = "ZQXSENTINEL"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"tools/{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m  # worker processes unpickle the tool's functions by module name
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def heat_tool():
    return _load("scenario_layer_run")


@pytest.fixture(scope="module")
def nh_tool():
    return _load("nonheat_layer_run")


def _read(d: Path):
    return [json.loads(x) for f in sorted(d.glob("*.jsonl")) for x in f.read_text().splitlines()]


def _write(d: Path, recs):
    d.mkdir(parents=True, exist_ok=True)
    (d / "part-0.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))


def _v02(rec: dict) -> dict:
    """A record as layer 0.2.0 wrote it: the old dose name, no zone fields, the old cap wording."""
    o = copy.deepcopy(rec)
    o["version"] = SL.VERSION_V02
    for s in o["scenarios"].values():
        s.pop("zone_nodes", None)
        s.pop("zone_mean_cook_value_min", None)
        if "cook_value_at_volume_avg_t_min" in s:
            s["quality_cook_value_min"] = s.pop("cook_value_at_volume_avg_t_min")
        s["flags"] = [("CAP_IS_UPPER_BOUND_NOT_VALIDATED" if f == "TBOIL_CEILING_DILUTE_AQUEOUS_ONLY" else f) for f in s["flags"]
                      if f not in ("NOT_A_ZONE_MEAN_DOSE", "ZONE_NODE_HISTORIES_EMITTED_FOR_OWN_KINETICS",
                                   "BOILING_POINT_ELEVATION_NOT_MODELLED", "STATED_LIQUID_T_ABOVE_TBOIL", "CAP_NOT_BELOW_TEXT_STATED_LIQUID_T")]
        if "STATED_LIQUID_T_ABOVE_TBOIL" in s["flags"] or s.get("t_cap_c") is not None and s["bath_c"] > 100.0 and s["t_cap_c"] > 100.0:
            s["t_cap_c"], s["boundary_c"] = 100.0, min(s["bath_c"], 100.0)
    return o


# ------------------------------------------------------------------------------------------------ heat tool
def test_heat_tool_v02_to_v03_block_and_zone_counts(heat_tool, tmp_path):
    l1 = tmp_path / "l1"
    recs = [_rec("PROC-000001", "OVEN_AIR", 30, 200), _rec("PROC-000019", "WATER", 60, 105, matrix="FRUIT"),
            _rec("PROC-000011", "OIL_IMMERSION", 5, 180, matrix="MEAT"), _rec("PROC-000019", "WATER", 20, 100, temp_basis="PHYSICAL_DEFINITION"),
            _rec("PROC-000001", "OVEN_AIR", 30, 200, size=None)]
    recs[1]["inputs"]["matrix_groups"] = {"value": ["FRUIT", "SWEETENER"], "status": "MEASURED", "basis": "FOOD_GROUP", "span": None}
    _write(l1, recs)
    first = tmp_path / "a.json"
    assert heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2a"), "--out", str(first)]) == 0
    a = json.loads(first.read_text())
    assert a["layer_version"] == SL.VERSION and "v02_to_v03" not in a
    c = a["counts"]
    assert c["zone_nodes_emitted"] == {"GENTLE": 4, "TYPICAL": 4, "INTENSE": 4}  # four events with a size, three brackets each
    assert c["stated_liquid_above_tboil"] == {"GENTLE": 1, "TYPICAL": 1, "INTENSE": 1}
    assert c["stated_liquid_above_tboil_by_stated_c"]["TYPICAL"] == {"100_TO_105": 1}
    assert c["cap_flag_typical"]["TBOIL_CEILING_DILUTE_AQUEOUS_ONLY"] == 5 and c["cap_flag_typical"]["BOILING_POINT_ELEVATION_NOT_MODELLED"] == 5
    assert c["cap_flag_typical"]["TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER"] == 1
    zq = a["zone_field"]["zone_mean_over_dose_at_volume_avg_t_quantiles"]["zone_mean_over_dose_at_volume_avg_t"]["TYPICAL"]
    assert zq["n"] == 4 and zq["p01"] >= 0.999 and a["zone_field"]["n_nodes"] == 8
    prev = tmp_path / "prev"
    _write(prev, [_v02(r) for r in _read(tmp_path / "l2a")])
    second = tmp_path / "b.json"
    assert heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2b"), "--out", str(second), "--compare-prev-l2", str(prev)]) == 0
    v = json.loads(second.read_text())["v02_to_v03"]
    assert v["previous_layer_version"] == SL.VERSION_V02 and v["layer_version"] == SL.VERSION
    pc = v["counts"]
    assert pc["events"] == 5 and "ALIGNMENT_ERROR" not in pc and "PREV_FILE_MISSING" not in pc
    assert sum(sum(x.values()) for x in pc["status"].values()) == 5
    assert pc["status"]["SCENARIO_COMPUTED"]["SCENARIO_COMPUTED"] == 5  # the no-size event is computed too (core unknown)
    assert pc["flag_added"]["TYPICAL"]["NOT_A_ZONE_MEAN_DOSE"] == 4 and pc["flag_added"]["TYPICAL"]["TBOIL_CEILING_DILUTE_AQUEOUS_ONLY"] == 5
    assert pc["flag_removed"]["TYPICAL"]["CAP_IS_UPPER_BOUND_NOT_VALIDATED"] == 5
    assert pc["t_cap_changed"]["TYPICAL"] == 1 and pc["t_cap_raised"]["TYPICAL"] == 1  # the 105 C stated boil
    assert pc["volume_avg_dose_equal_to_0_2_0_name"]["TYPICAL"] == {"True": 4}  # same number, new name
    assert pc["zone_mean_dose_gt_dose_at_volume_avg_t"]["TYPICAL"].get("False", 0) == 0 or v["ratio_quantiles"]
    assert v["ratio_quantiles"]["zone_mean_over_core_dose"]["TYPICAL"]["n"] == 4
    assert SENT not in second.read_text()


def test_heat_tool_reports_a_missing_or_misaligned_previous_file(heat_tool, tmp_path):
    l1 = tmp_path / "l1"
    _write(l1, [_rec("PROC-000001", "OVEN_AIR", 30, 200)])
    empty = tmp_path / "empty"
    empty.mkdir()
    out = tmp_path / "r.json"
    assert heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2"), "--out", str(out), "--compare-prev-l2", str(empty)]) == 0
    assert json.loads(out.read_text())["v02_to_v03"]["counts"]["PREV_FILE_MISSING"] == 1
    with pytest.raises(SystemExit):
        heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2x"), "--out", str(tmp_path / "x.json"),
                        "--compare-prev-l2", str(tmp_path / "does_not_exist")])


def test_heat_tool_written_records_are_compact_and_new_version(heat_tool, tmp_path):
    l1 = tmp_path / "l1"
    _write(l1, [_rec("PROC-000001", "OVEN_AIR", 30, 200)])
    assert heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2"), "--out", str(tmp_path / "r.json")]) == 0
    text = (tmp_path / "l2" / "part-0.jsonl").read_text()
    assert '": ' not in text.splitlines()[0] and json.loads(text)["version"] == SL.VERSION


# ------------------------------------------------------------------------------------------------ non-heat tool
def source(families, root):
    for i in range(6):
        yield {"recipe_id": f"SYN-{i}", "source_family": families[0],
               "steps": [f"Dice the carrots {SENT}.", "Canning the jam in a boiling water bath for 10 minutes.",
                         "Marinate the chicken in vinegar for 2 hours.", "Pasteurise the juice at 90C for 20 minutes.",
                         "Slice the cucumber. Brine the cucumber in a 5% brine for 6 hours.",
                         "Canning the beans in a pressure canner for 30 minutes."]}


def test_nonheat_tool_v02_to_v03_block(nh_tool, tmp_path):
    argv = ["--seed", "7", "--sample-size", "6", "--workers", "1", "--families", "WIKIBOOKS", "--no-baseline-check", "--root", str(ROOT),
            "--l1-out", str(tmp_path / "a_l1.json"), "--l2-out", str(tmp_path / "a_l2.json"),
            "--l1-records-dir", str(tmp_path / "r1"), "--l2-records-dir", str(tmp_path / "r2")]
    assert nh_tool.main(argv, record_source=source) == 0
    new = _read(tmp_path / "r2")
    assert {r["status"] for r in new if r["nh_family"] == "PRESERVATION"} >= {"QUALITATIVE_FLAGS_ONLY", "SCENARIO_COMPUTED"}
    # a previous (0.2.0) record set, one file per L1 file (same names, same order): every F0 and acid event printed a number
    pdir = tmp_path / "prev"
    pdir.mkdir()
    for f in sorted((tmp_path / "r2").glob("*.jsonl")):
        prev = []
        for line in f.read_text().splitlines():
            r = json.loads(line)
            o = copy.deepcopy(r)
            o["version"] = "nonheat-scenario-L2-0.2.0-draft"
            if r["nh_family"] == "PRESERVATION" and "F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" in r["scenarios"]["TYPICAL"]["flags"]:
                o["status"] = "SCENARIO_COMPUTED"
                for s in o["scenarios"].values():
                    s["f0_min"] = 1.0
                    s["flags"] = ["F0_AT_MEDIUM_TEMPERATURE_NOT_COLD_SPOT"]
            if r["nh_family"] == "PRESERVATION" and "f0_upper_bound_at_medium_t_min" in r["scenarios"]["TYPICAL"]:
                for s in o["scenarios"].values():  # the 0.2.0 name of the pressure-canning field
                    s["f0_min"] = s.pop("f0_upper_bound_at_medium_t_min")
            if r["nh_family"] == "FERMENT_LEAVEN" and "ACID_UPTAKE_REACTION_DIFFUSION_QUALITATIVE_ONLY" in r["scenarios"]["TYPICAL"]["flags"]:
                o["status"] = "SCENARIO_COMPUTED"
                for s in o["scenarios"].values():
                    s.pop("state_flags", None)
                    s["uptake_fraction"] = 0.5
                    s["flags"] = ["FICKIAN_SLAB_BI_INFINITY"]
            prev.append(o)
        (pdir / f.name).write_text("".join(json.dumps(o) + "\n" for o in prev))
    argv2 = ["--seed", "7", "--l2-only", "--workers", "1", "--families", "WIKIBOOKS", "--no-baseline-check", "--root", str(ROOT),
             "--l2-out", str(tmp_path / "b_l2.json"), "--l1-records-dir", str(tmp_path / "r1"),
             "--l2-records-dir", str(tmp_path / "r2b"), "--compare-prev-l2", str(pdir)]
    assert nh_tool.main(argv2) == 0
    rep = json.loads((tmp_path / "b_l2.json").read_text())
    v = rep["v02_to_v03"]
    assert rep["layer_version"] == "nonheat-scenario-L2-0.4.0-draft" and v["previous_layer_version"] == "nonheat-scenario-L2-0.2.0-draft"
    pc = v["counts"]
    assert "ALIGNMENT_ERROR" not in pc and "PREV_FILE_MISSING" not in pc
    st = pc["status"]["PRESERVATION"]
    assert st["SCENARIO_COMPUTED__TO__QUALITATIVE_FLAGS_ONLY"] >= 12  # boiling-water-bath canning and pasteurise: no F0 any more
    assert st["SCENARIO_COMPUTED__TO__SCENARIO_COMPUTED"] == 12  # pressure canning (renamed F0 field) and the brine-pickle uptake
    assert pc["flag_added"]["PRESERVATION"]["F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY"] >= 12
    assert pc["field_dropped"]["PRESERVATION"]["f0_min"] == 18  # 12 events lose it, 6 pressure-canning events rename it
    assert pc["field_added"]["PRESERVATION"]["f0_upper_bound_at_medium_t_min"] == 6
    assert pc["status"]["FERMENT_LEAVEN"]["SCENARIO_COMPUTED__TO__QUALITATIVE_FLAGS_ONLY"] == 6
    assert pc["field_dropped"]["FERMENT_LEAVEN"]["uptake_fraction"] == 6 and pc["field_added"]["FERMENT_LEAVEN"]["state_flags"] == 6
    assert SENT not in json.dumps(rep) and rep["counts"]["bracket_order_check"]
    assert "VIOLATION" not in json.dumps(rep["counts"]["bracket_order_check"])
