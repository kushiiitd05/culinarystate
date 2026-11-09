"""S177 SCIFIX-PHYS row 3 (FINAL-SCI): 100 C is not an upper bound for solute-rich water phases.

Never cap below a text-stated aqueous liquid temperature (STATED_LIQUID_T_ABOVE_TBOIL); boiling-point elevation is not
modelled (BOILING_POINT_ELEVATION_NOT_MODELLED) and a solute-rich member makes the cap a lower estimate; the regime is DRY when
every member is a dry class; CAP_IS_UPPER_BOUND_NOT_VALIDATED is replaced by TBOIL_CEILING_DILUTE_AQUEOUS_ONLY.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from culinarystate.simulation import nonheat_scenario as NS
from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import scenario_layer as SL
from tests.unit.test_s176_phys_cap import B, TOL, _rec, _rest_rec

ROOT = Path(__file__).resolve().parents[2]
LOWER = "TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER"


@pytest.fixture(scope="module")
def pc():
    return PC.PhaseChange.load()


@pytest.fixture(scope="module")
def new():
    return SL.ScenarioLayer.load()


def _groups(rec, groups):
    rec["inputs"]["matrix_groups"] = {"value": list(groups), "status": "MEASURED", "basis": "FOOD_GROUP", "span": None}
    return rec


# ------------------------------------------------------------------------------------------------ rename and flags
def test_the_upper_bound_flag_is_replaced_everywhere(pc):
    for medium, pol in (("OVEN_AIR", None), ("WATER", PC.CapPolicy(altitude_m=1500.0)), ("WATER_PRESSURIZED", None),
                        ("WATER_PRESSURIZED", PC.CapPolicy(pressure_psig=12.0))):
        for b in range(3):
            f = pc.cap(medium=medium, matrix_class="MEAT", bracket=b, policy=pol).flags
            assert "TBOIL_CEILING_DILUTE_AQUEOUS_ONLY" in f and "CAP_IS_UPPER_BOUND_NOT_VALIDATED" not in f
            assert "CAP_NOT_LIFTED_NO_DRYING_MODEL" in f and "BOILING_POINT_ELEVATION_NOT_MODELLED" in f


def test_dry_and_disabled_caps_carry_no_boiling_point_flag(pc):
    assert "BOILING_POINT_ELEVATION_NOT_MODELLED" not in pc.cap(medium="OVEN_AIR", matrix_class="NUT_SEED").flags
    assert "BOILING_POINT_ELEVATION_NOT_MODELLED" not in pc.cap(medium="OVEN_AIR", matrix_class="MEAT",
                                                                policy=PC.CapPolicy(enabled=False)).flags


def test_layer_records_carry_the_new_flags_and_not_the_old_one(new):
    s = new.run(_rec("PROC-000001", "OVEN_AIR", 30, 200, "DICED"))["scenarios"]["TYPICAL"]
    assert "TBOIL_CEILING_DILUTE_AQUEOUS_ONLY" in s["flags"] and "BOILING_POINT_ELEVATION_NOT_MODELLED" in s["flags"]
    assert "CAP_IS_UPPER_BOUND_NOT_VALIDATED" not in s["flags"] and "STATED_LIQUID_T_ABOVE_TBOIL" not in s["flags"]
    assert s["t_cap_c"] == 100.0 and s["boundary_c"] == 100.0


# ------------------------------------------------------------------------------------------------ (a) stated liquid T
def test_stated_aqueous_liquid_above_the_boil_is_never_capped_below(pc):
    c = pc.cap(medium="WATER", matrix_class="FRUIT", bracket=1, stated_liquid_c=105.0, stated_basis="L1:TEXT_STATED")
    assert c.t_c == 105.0 and not c.binding(105.0) and c.boundary(105.0) == 105.0
    assert "STATED_LIQUID_T_ABOVE_TBOIL" in c.flags and "BOILING_POINT_ELEVATION_NOT_MODELLED" in c.flags
    assert c.basis.startswith("L1:TEXT_STATED|") and c.basis.endswith("PC-001")
    for med in ("LIQUID", "LIQUID_PARTIAL", "WATER_BATH_SEALED"):
        assert pc.cap(medium=med, matrix_class=None, stated_liquid_c=104.0, stated_basis="L1:TEXT_STATED").t_c == 104.0


def test_a_stated_temperature_at_or_below_the_boil_changes_nothing(pc):
    for t in (60.0, 99.99, 100.0):
        c = pc.cap(medium="WATER", matrix_class="MEAT", stated_liquid_c=t, stated_basis="L1:TEXT_STATED")
        assert c.t_c == 100.0 and "STATED_LIQUID_T_ABOVE_TBOIL" not in c.flags and c.basis == "PC-001"


def test_a_stated_oil_or_oven_temperature_never_lifts_the_cap(pc):
    for med in ("OIL_IMMERSION", "OIL_SHALLOW", "OVEN_AIR", "PAN_CONTACT_OIL", "STEAM"):
        c = pc.cap(medium=med, matrix_class="MEAT", stated_liquid_c=180.0, stated_basis="L1:TEXT_STATED")
        assert c.t_c == 100.0 and "STATED_LIQUID_T_ABOVE_TBOIL" not in c.flags


def test_a_stated_pressure_vessel_temperature_is_not_cut_to_the_bracket(pc):
    low = pc.cap(medium="WATER_PRESSURIZED", matrix_class="MEAT", bracket=0, stated_liquid_c=118.0, stated_basis="L1:TEXT_STATED")
    mid = pc.cap(medium="WATER_PRESSURIZED", matrix_class="MEAT", bracket=1, stated_liquid_c=118.0, stated_basis="L1:TEXT_STATED")
    high = pc.cap(medium="WATER_PRESSURIZED", matrix_class="MEAT", bracket=2, stated_liquid_c=118.0, stated_basis="L1:TEXT_STATED")
    assert (low.t_c, mid.t_c, high.t_c) == (118.0, 118.0, 121.0)  # 108.4 and 115.2 are below the text; 121.0 is not
    assert "STATED_LIQUID_T_ABOVE_TBOIL" in low.flags and "STATED_LIQUID_T_ABOVE_TBOIL" in mid.flags
    assert "STATED_LIQUID_T_ABOVE_TBOIL" not in high.flags


def test_a_dry_class_is_still_uncapped_and_a_disabled_cap_stays_disabled(pc):
    assert pc.cap(medium="WATER", matrix_class="SWEETENER", stated_liquid_c=110.0).t_c is None
    assert pc.cap(medium="WATER", matrix_class="MEAT", stated_liquid_c=110.0, policy=PC.CapPolicy(enabled=False)).t_c is None


def test_layer_boil_to_105_is_a_105_boundary_not_a_100_boundary(new):
    out = new.run(_rec("PROC-000019", "WATER", 60, 105, "DICED", matrix="FRUIT"))
    for b in B:
        s = out["scenarios"][b]
        assert s["bath_c"] == 105.0 and s["t_cap_c"] == 105.0 and s["boundary_c"] == 105.0
        assert "STATED_LIQUID_T_ABOVE_TBOIL" in s["flags"] and "EVAPORATION_CAP_NOT_BINDING" in s["flags"]
        assert "EVAPORATION_CAP_APPLIED" not in s["flags"]
        assert s["core_end_c"] <= 105.0 + TOL and s["volume_avg_end_c"] <= 105.0 + TOL
        assert s["surface_cook_value_min"] == pytest.approx(60 * 10 ** ((105.0 - 100.0) / 33.0), rel=1e-3)  # surface at 105
    assert out["scenarios"]["INTENSE"]["core_end_c"] > 100.0 + TOL  # the text-stated liquid really heats past 100
    # the same event stated at 98 C is untouched
    s98 = new.run(_rec("PROC-000019", "WATER", 60, 98, "DICED", matrix="FRUIT"))["scenarios"]["TYPICAL"]
    assert s98["t_cap_c"] == 100.0 and "STATED_LIQUID_T_ABOVE_TBOIL" not in s98["flags"]


def test_layer_oil_stays_capped_when_the_text_states_the_oil_temperature(new):
    s = new.run(_rec("PROC-000011", "OIL_IMMERSION", 10, 180, "DICED", matrix="MEAT"))["scenarios"]["TYPICAL"]
    assert s["t_cap_c"] == 100.0 and "STATED_LIQUID_T_ABOVE_TBOIL" not in s["flags"] and s["core_end_c"] <= 100.0 + TOL


def test_a_carried_setpoint_counts_as_text_stated_and_a_default_does_not(new):
    carried = new.run(_rec("PROC-000019", "WATER", 30, 105, "DICED", temp_basis="CARRIED_SETPOINT"))["scenarios"]["TYPICAL"]
    assert carried["t_cap_c"] == 105.0 and "STATED_LIQUID_T_ABOVE_TBOIL" in carried["flags"]
    assert PC.STATED_BASES == ("L1:TEXT_STATED", "L1:CARRIED_SETPOINT")
    # PHYSICAL_DEFINITION is not a stated value: the cap stays at the physical boil
    pdv = new.run(_rec("PROC-000019", "WATER", 30, 105, "DICED", temp_basis="PHYSICAL_DEFINITION"))["scenarios"]["TYPICAL"]
    assert pdv["t_cap_c"] == 100.0 and "STATED_LIQUID_T_ABOVE_TBOIL" not in pdv["flags"]


# ------------------------------------------------------------------------------------------------ (b) solute-rich members
def test_registry_marks_exactly_the_solute_rich_classes():
    with open(ROOT / PC.REGIME_REGISTRY, newline="", encoding="utf-8") as fh:
        rows = {r["matrix_class"]: r for r in csv.DictReader(fh)}
    assert {k for k, r in rows.items() if r["solute_rich"] == "YES"} == {"SWEETENER", "CONDIMENT"}
    assert all(r["solute_rich"] in ("YES", "NO") for r in rows.values())
    assert PC.PhaseChange.load().solute_rich_classes == frozenset({"SWEETENER", "CONDIMENT"})


@pytest.mark.parametrize("groups,lower", [(("FRUIT", "SWEETENER"), True), (("MEAT", "CONDIMENT"), True), (("VEGETABLE", "CONDIMENT", "FAT_OIL"), True),
                                          (("FRUIT", "MEAT"), False), (("VEGETABLE", "FAT_OIL"), False), (("DAIRY", "EGG"), False)])
def test_solute_rich_member_makes_the_cap_a_lower_estimate(pc, groups, lower):
    c = pc.cap(medium="WATER", matrix_class=None, member_groups=groups)
    assert c.t_c == 100.0 and "BOILING_POINT_ELEVATION_NOT_MODELLED" in c.flags
    assert (LOWER in c.flags) is lower


def test_single_class_condiment_is_a_lower_estimate_and_sweetener_is_dry(pc):
    assert LOWER in pc.cap(medium="WATER", matrix_class="CONDIMENT").flags
    assert pc.cap(medium="WATER", matrix_class="SWEETENER").t_c is None  # dry class: not capped at all
    assert LOWER not in pc.cap(medium="WATER", matrix_class="MEAT").flags


def test_layer_jam_lot_is_flagged_a_lower_estimate(new):
    out = new.run(_groups(_rec("PROC-000019", "WATER", 20, 100, "DICED", temp_basis="PHYSICAL_DEFINITION"), ("FRUIT", "SWEETENER")))
    for b in B:
        f = out["scenarios"][b]["flags"]
        assert LOWER in f and "BOILING_POINT_ELEVATION_NOT_MODELLED" in f and out["scenarios"][b]["t_cap_c"] == 100.0
    plain = new.run(_groups(_rec("PROC-000019", "WATER", 20, 100, "DICED", temp_basis="PHYSICAL_DEFINITION"), ("FRUIT", "MEAT")))
    assert LOWER not in plain["scenarios"]["TYPICAL"]["flags"]


# ------------------------------------------------------------------------------------------------ (c) dry regime
def test_regime_of_members_rules(pc):
    r = pc.regime_of_members
    assert r(("NUT_SEED", "SWEETENER")) == PC.DRY and r(("SWEETENER", "FAT_OIL")) == PC.DRY and r(("FAT_OIL",)) == PC.DRY
    assert r(("MEAT", "FAT_OIL")) == PC.MOIST and r(("FRUIT", "SWEETENER")) == PC.MOIST
    assert r(("CEREAL", "FAT_OIL")) == PC.AMBIGUOUS  # a roux: flour is ambiguous, not a dry class, so it stays capped
    assert r(("LEGUME", "HERB_SPICE")) == PC.AMBIGUOUS
    assert r(("NUT_SEED", "NOT_A_GROUP")) == PC.UNKNOWN_CLASS and r(()) == PC.UNKNOWN_CLASS and r(None) == PC.UNKNOWN_CLASS
    assert r(("NUT_SEED", None, "")) == PC.DRY  # empty entries are ignored


def test_every_member_dry_lot_is_uncapped_with_a_flag(pc):
    c = pc.cap(medium="OVEN_AIR", matrix_class=None, member_groups=("NUT_SEED", "SWEETENER"))
    assert c.t_c is None and c.regime == PC.DRY and "MATRIX_DRY_CLASS_UNCAPPED" in c.flags and "ALL_MEMBERS_DRY_CLASS" in c.flags
    single = pc.cap(medium="OVEN_AIR", matrix_class="NUT_SEED", member_groups=("NUT_SEED",))
    assert single.t_c is None and "ALL_MEMBERS_DRY_CLASS" not in single.flags
    mixed = pc.cap(medium="OVEN_AIR", matrix_class=None, member_groups=("NUT_SEED", "MEAT"))
    assert mixed.t_c == 100.0 and mixed.regime == PC.MOIST


def test_member_groups_override_a_missing_matrix_class_in_the_layer(new):
    praline = new.run(_groups(_rec("PROC-000001", "OVEN_AIR", 30, 200, "DICED"), ("NUT_SEED", "SWEETENER")))["scenarios"]["TYPICAL"]
    assert praline["t_cap_c"] is None and "ALL_MEMBERS_DRY_CLASS" in praline["flags"] and "DRY_MATRIX_CONDUCTION_PROPERTIES_NOT_IN_REGISTRY" in praline["flags"]
    assert praline["core_end_c"] > 150.0  # uncapped, as the dry classes always were
    unknown = new.run(_rec("PROC-000001", "OVEN_AIR", 30, 200, "DICED"))["scenarios"]["TYPICAL"]
    assert unknown["t_cap_c"] == 100.0 and "MATRIX_UNKNOWN_MOIST_ASSUMED" in unknown["flags"]  # no groups: never guessed dry


def test_member_groups_reader():
    rec = _groups(_rec("PROC-000001", "OVEN_AIR", 30, 200), ["SWEETENER", "FRUIT", "FRUIT"])
    assert SL.member_groups(rec["inputs"]) == ("FRUIT", "SWEETENER")
    assert SL.member_groups(_rec("PROC-000001", "OVEN_AIR", 30, 200)["inputs"]) == ()
    unknown = {"matrix_groups": {"value": None, "status": "UNKNOWN", "basis": None, "span": None}}
    assert SL.member_groups(unknown) == ()


# ------------------------------------------------------------------------------------------------ non-heat RESTING
def test_resting_after_a_105_c_stated_boil_is_not_capped_below_the_text():
    nh = NS.NonHeatScenario.load()
    out = nh.run(_rest_rec(medium="WATER", proc="PROC-000019", bath="105", hdur="30", rest="5", size="DICED"))
    for b in B:
        s = out["scenarios"][b]
        assert s["t_cap_c"] == 105.0 and "STATED_LIQUID_T_ABOVE_TBOIL" in s["flags"]
        assert s["core_end_of_heat_c"] <= 105.0 + TOL and s["core_peak_c"] <= 105.0 + TOL
        assert "PRESSURE_RELEASE_PROFILE_CLIPPED_TO_ATMOSPHERIC_TBOIL" not in s["flags"]
        assert "REST_PROFILE_CLIPPED_TO_ATMOSPHERIC_TBOIL_AFTER_STATED_LIQUID_T" in s["flags"]
    assert out["version"] == NS.VERSION == "nonheat-scenario-L2-0.3.0-draft"
    plain = nh.run(_rest_rec(medium="WATER", proc="PROC-000019", bath="98", hdur="30", rest="5", size="DICED"))["scenarios"]["TYPICAL"]
    assert plain["t_cap_c"] == 100.0 and "STATED_LIQUID_T_ABOVE_TBOIL" not in plain["flags"]
