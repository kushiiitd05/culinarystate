"""S178 FIX-PHYS: Layer 2 0.5.0 / cap model 0.3.0 fixes of the SCI-A review (M4, M5, m3, m10, m11). Synthetic sentences only.

M4 (Q1 PROPOSED default): a stated aqueous-liquid temperature above T_boil lifts the cap only when the liquid step owns it AND a
sugar-phase member, a syrup / stage cue or a pressure cue (up to PC-002 INTENSE + PC-041) is present. M5: a lifted value is the
liquid's; a moist cut piece in it is bounded by its own T_boil (invariant below). m10: split solute flags. m11: implausible canner T.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

import pytest

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import nonheat_scenario as NS
from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import scenario_layer as SL
from tests.unit.test_s176_phys_cap import B, TOL, _rec

OWN = "CB_RULE:TEMPERATURE_OWN_CLAUSE"


@pytest.fixture(scope="module")
def binder():
    return CB.Binder.load()


@pytest.fixture(scope="module")
def layer():
    return SL.ScenarioLayer.load()


@pytest.fixture(scope="module")
def pc():
    return PC.PhaseChange.load()


def s_(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, tuple):
        return [s_(x) for x in v]
    return v


def run_text(binder, layer, text, pid):
    e = [x for x in binder.bind_text(text)["events"] if x["process_id"] == pid][0]
    rec = {"recipe_id": "R", "event_id": e["event_id"], "process_id": pid, "oven_setpoint_code": e.get("oven_setpoint_code"),
           "inputs": {k: {**v, "value": s_(v["value"])} for k, v in e["inputs"].items()}}
    return layer.run(rec)


def lifted(out) -> bool:
    return any("STATED_LIQUID_T_ABOVE_TBOIL" in s["flags"] for s in out["scenarios"].values())


# ------------------------------------------------------------------------------------------------ M4: the reviewer's inputs
@pytest.mark.parametrize("text, pid", [
    ("Reduce heat to 325 F and simmer for 1 hour.", "PROC-000020"),
    ("Simmer over medium heat, about 300 F, for 20 minutes.", "PROC-000020"),
    ("Simmer in an electric skillet at 300 F for 20 minutes.", "PROC-000020"),
    ("Stew in a slow cooker on high (300 F) for 4 hours.", "PROC-000025"),
    ("Braise in an electric frying pan set to 325 F for 1 hour.", "PROC-000024"),
    ("Simmer 10 minutes at 350 F.", "PROC-000020"),
    ("Simmer the stock with 250 c. of water for 20 minutes.", "PROC-000020"),
])
def test_m4_no_dilute_water_phase_is_lifted_above_the_boil(binder, layer, text, pid):
    out = run_text(binder, layer, text, pid)
    assert not lifted(out), text
    for s in out["scenarios"].values():
        assert s["t_cap_c"] == 100.0 and s["boundary_c"] <= 100.0, text


def test_m4_an_owned_dilute_value_is_kept_in_layer1_and_flagged_in_layer2(binder, layer):
    out = run_text(binder, layer, "Simmer 10 minutes at 350 F.", "PROC-000020")
    t = out["scenarios"]["TYPICAL"]
    assert t["bath_c"] == pytest.approx(176.667, abs=1e-2) and t["bases"]["bath_c"] == "L1:TEXT_STATED"
    assert "STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE" in t["flags"]


@pytest.mark.parametrize("text, reason", [
    ("Boil to 240 F, soft ball stage, about 10 minutes.", "SYRUP_STAGE_CUE"),
    ("Boil the jam for 10 minutes until it reaches 220 F.", "SYRUP_STAGE_CUE"),
    ("Boil in a pressure cooker at 15 psi (250 F) for 10 minutes.", "PRESSURE_CUE"),
])
def test_m4_candy_jam_and_pressure_stages_still_lift(binder, layer, text, reason):
    out = run_text(binder, layer, text, "PROC-000019")
    assert lifted(out), text
    assert all(f"STATED_LIQUID_LIFT_{reason}" in s["flags"] for s in out["scenarios"].values()), text


def test_m4_a_sugar_only_syrup_is_a_dry_class_and_never_capped_below_its_stage(binder, layer):
    out = run_text(binder, layer, "Boil the syrup to 240 F for 5 minutes.", "PROC-000019")
    for s in out["scenarios"].values():  # SWEETENER-only lot: dry regime, uncapped (S177), so nothing to lift
        assert s["t_cap_c"] is None and s["boundary_c"] == pytest.approx(115.556, abs=1e-2)


def test_m4_a_pressure_cue_lifts_only_up_to_the_scenario_saturation_maximum(pc):
    mx, basis = pc.pressure_max_c()
    assert mx == 121.0 + 0.5 and basis == "PC-002+PC-041"
    ok = pc.stated_liquid_lift(medium="WATER", stated_c=121.1, stated_row=OWN, pressure_cue=True)
    assert ok[0] == 121.1 and ok[1] == "PRESSURE_CUE"
    no = pc.stated_liquid_lift(medium="WATER", stated_c=148.9, stated_row=OWN, pressure_cue=True)
    assert no[0] is None and "STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_ABOVE_PRESSURE_MAX" in no[2]


def test_m4_gate_table(pc):
    g = pc.stated_liquid_lift
    assert g(medium="WATER", stated_c=110.0, stated_row="CB_RULE:TEMPERATURE_FROM_SETTER_STEP", member_groups=("FRUIT", "SWEETENER"))[2] \
        == ("STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED",)
    assert g(medium="WATER", stated_c=110.0, stated_row=OWN, member_groups=("FRUIT", "SWEETENER"))[1] == "SUGAR_PHASE_MEMBER"
    assert g(medium="WATER", stated_c=110.0, stated_row=OWN, member_groups=("MEAT", "CONDIMENT"))[2] == \
        ("STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE",)  # salt alone never lifts (m10)
    assert g(medium="WATER", stated_c=110.0, stated_row=OWN, syrup_cue=True)[1] == "SYRUP_STAGE_CUE"
    assert g(medium="WATER", stated_c=99.0, stated_row=OWN, syrup_cue=True) == (None, None, ())  # nothing to lift
    assert g(medium="OIL_IMMERSION", stated_c=180.0, stated_row=OWN, syrup_cue=True) == (None, None, ())  # never an oil


# ------------------------------------------------------------------------------------------------ M5: moist pieces stay at T_boil
def test_m5_a_cut_piece_in_a_lifted_syrup_is_bounded_by_its_own_boil(binder, layer):
    out = run_text(binder, layer, "Dice the potatoes and boil them in the syrup at 350 F for 10 minutes.", "PROC-000019")
    for s in out["scenarios"].values():
        assert s["t_cap_c"] == pytest.approx(176.667, abs=1e-2)          # the liquid's own (lifted) cap
        assert s["boundary_c"] == 100.0 and s["core_end_c"] <= 100.0 + TOL  # the piece: its own T_boil
        assert "STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE" in s["flags"]
        assert s["surface_cook_value_min"] == pytest.approx(10 * 10 ** ((176.667 - 100.0) / 33.0), rel=1e-3)


def test_m5_invariant_no_moist_piece_core_above_tboil_unless_a_pressure_cue(layer):
    """Property: over stated temperatures, media, members, cues and sizes, no CUT_HISTORY moist-piece core exceeds T_boil + PC-041
    unless a pressure cue (then the PC-002 maximum + PC-041); dry lots are uncapped by design and are skipped."""
    n = 0
    for temp, medium, groups, syrup, pressure, size in itertools.product(
            (101, 115, 150, 177, 250), ("WATER", "LIQUID", "LIQUID_PARTIAL"), ((), ("FRUIT", "SWEETENER"), ("MEAT", "CONDIMENT")),
            (False, True), (False, True), ("DICED", "MINCED", "SLICED")):
        r = _rec("PROC-000019", medium, 30, temp, size)
        r["inputs"]["temperature_profile"]["row"] = OWN
        if groups:
            r["inputs"]["matrix_groups"] = {"value": list(groups), "status": "MEASURED", "basis": "FOOD_GROUP", "span": None}
        for ax, on in (("syrup_stage_cue", syrup), ("pressure_cue", pressure)):
            if on:
                r["inputs"][ax] = {"value": "X", "status": "QUALITATIVE", "basis": "CUE", "span": [0, 1], "span_id": "C:0-1", "row": "T"}
        out = layer.run(r)
        for s in out["scenarios"].values():
            if s.get("t_cap_c") is None or s.get("core_end_c") is None:
                continue
            limit = (121.0 if pressure else 100.0) + 0.5
            assert s["core_end_c"] <= limit and s["boundary_c"] <= limit, (temp, medium, groups, syrup, pressure, size, s["core_end_c"])
            n += 1
    assert n > 500


def test_m5_resting_piece_after_a_lifted_liquid_is_bounded_too():
    from tests.unit.test_s176_phys_cap import _rest_rec
    nh = NS.NonHeatScenario.load()
    r = _rest_rec(medium="WATER", proc="PROC-000019", bath="105", hdur="30", rest="5", size="DICED")
    ph = r["history"]["prior_heat"]["inputs"]
    ph["temperature_profile"]["row"] = OWN
    ph["matrix_groups"] = {"value": ["FRUIT", "SWEETENER"], "status": "MEASURED", "basis": "FOOD_GROUP", "span": None}
    for s in nh.run(r)["scenarios"].values():
        assert s["t_cap_c"] == 100.0 and s["core_peak_c"] <= 100.0 + TOL
        assert "STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE" in s["flags"]


# ------------------------------------------------------------------------------------------------ m10 split flags, m11 canner
def test_m10_salt_and_sugar_flags_are_split(pc):
    salted = pc.cap(medium="WATER", matrix_class=None, member_groups=("VEGETABLE", "CONDIMENT"))
    assert PC.SALT_FLAG in salted.flags and PC.SUGAR_FLAG not in salted.flags and PC.LEGACY_SOLUTE_FLAG not in salted.flags
    jam = pc.cap(medium="WATER", matrix_class=None, member_groups=("FRUIT", "SWEETENER"))
    assert PC.SUGAR_FLAG in jam.flags and PC.SALT_FLAG not in jam.flags
    assert pc.sugar_classes == frozenset({"SWEETENER"}) and pc.salt_classes == frozenset({"CONDIMENT"})


def test_m11_an_implausible_stated_canner_temperature_gets_no_f0():
    nb, nh = NB.NonHeatBinder.load(), NS.NonHeatScenario.load()
    r = next(e for e in nb.bind_text("Canning the beans in a pressure canner at 300 F for 40 minutes.")["events"]
             if e["process_id"] == "PROC-000132")
    out = nh.run(r)
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY"
    for s in out["scenarios"].values():
        assert "STATED_CANNER_T_IMPLAUSIBLE" in s["flags"] and "f0_upper_bound_at_medium_t_min" not in s
    ok = next(e for e in nb.bind_text("Canning the beans in a pressure canner at 240 F for 40 minutes.")["events"]
              if e["process_id"] == "PROC-000132")
    assert nh.run(ok)["status"] == "SCENARIO_COMPUTED"  # 115.6 C is a canner temperature


def test_m4_m10_layer2_versions():
    assert SL.VERSION == "scenario-layer-L2-0.5.0-draft" and NS.VERSION == "nonheat-scenario-L2-0.5.0-draft"
    assert NB.VERSION == "nonheat-binding-L1-0.3.0-draft" and PC.VERSION == "evaporation-cap-0.3.0-draft"
