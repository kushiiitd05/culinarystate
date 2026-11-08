"""S176 L-PHYS: evaporation / phase-change cap, qualitative surface state, volume-average dose, exact two-stage slab.

Invariants (SSOT v16 DRAFT 284.3): no moist zone exceeds T_boil + 0.5 C while water remains; a water bath below the boil
is unchanged; a pressure process may exceed 100 C and nothing else may; a dry-class matrix is not capped; altitude lowers the
cap; non-heat RESTING is capped; a very long thin RESTING stage finishes in under a second.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import pytest

from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import nonheat_scenario as NS
from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import physics_drivers as PD
from culinarystate.simulation import scenario_layer as SL

ROOT = Path(__file__).resolve().parents[2]
B = ("GENTLE", "TYPICAL", "INTENSE")
ALPHA, K = 1.4e-7, 0.5
TOL = 0.5


def _rec(proc, medium, dur, temp=None, size="DICED", matrix=None, temp_basis="TEXT_STATED"):
    inp = {k: {"value": None, "status": "UNKNOWN", "basis": None, "span": None}
           for k in ("duration", "temperature_profile", "medium", "lid_state", "start_mode", "piece_size_class",
                     "water_ratio", "matrix_class")}
    inp["duration"] = {"value": str(dur), "status": "MEASURED", "basis": "TEXT_STATED", "span": None}
    inp["medium"] = {"value": medium, "status": "MEASURED", "basis": "PROCESS_DEFINITION", "span": None}
    if temp is not None:
        inp["temperature_profile"] = {"value": str(temp), "status": "MEASURED", "basis": temp_basis, "span": None}
    if size:
        inp["piece_size_class"] = {"value": size, "status": "MEASURED", "basis": "CUT_HISTORY", "span": None}
    if matrix:
        inp["matrix_class"] = {"value": matrix, "status": "MEASURED", "basis": "FOOD_GROUP", "span": None}
    return {"recipe_id": "R", "event_id": "E1", "process_id": proc, "family": "X", "inputs": inp, "oven_setpoint_code": None}


@pytest.fixture(scope="module")
def new():
    return SL.ScenarioLayer.load()


@pytest.fixture(scope="module")
def old():
    return SL.ScenarioLayer.load(policy=PC.CapPolicy(enabled=False))


@pytest.fixture(scope="module")
def pc():
    return PC.PhaseChange.load()


# ------------------------------------------------------------------------------------------------ the invariant
@pytest.mark.parametrize("proc,medium,temp", [("PROC-000001", "OVEN_AIR", 200), ("PROC-000008", "OVEN_AIR_FORCED", 200),
                                              ("PROC-000011", "OIL_IMMERSION", 190), ("PROC-000012", "OIL_SHALLOW", 190),
                                              ("PROC-000013", "PAN_CONTACT_OIL", 200), ("PROC-000015", "PAN_CONTACT_OIL", 230)])
@pytest.mark.parametrize("size", ["MINCED", "SLICED", "DICED", "CHOPPED"])
@pytest.mark.parametrize("dur", [1, 8, 30, 240, 5000])
def test_moist_slab_never_exceeds_tboil_in_oven_oil_or_pan(new, proc, medium, temp, size, dur):
    out = new.run(_rec(proc, medium, dur, temp, size))
    assert out["version"] == SL.VERSION and out["cap_model"] == PC.VERSION
    for b in B:
        s = out["scenarios"][b]
        assert s["t_cap_c"] == 100.0 and s["boundary_c"] == 100.0 and s["bath_c"] == temp
        assert s["core_end_c"] <= 100.0 + TOL and s["volume_avg_end_c"] <= 100.0 + TOL
        assert "EVAPORATION_CAP_APPLIED" in s["flags"] and "PRESSURE_ASSUMED_1ATM" in s["flags"]
        assert "ALTITUDE_ASSUMED_SEA_LEVEL" in s["flags"] and "CAP_NOT_LIFTED_NO_DRYING_MODEL" in s["flags"]
        assert s["volume_avg_end_c"] >= s["core_end_c"] - 1e-9  # heating: the mean leads the centre
        if s["surface_cook_value_min"] is not None:  # oil immersion: the wet surface sits at T_boil, not at the oil temperature
            assert s["surface_cook_value_min"] == pytest.approx(s["duration_min"] * 1.0, rel=1e-3)


def test_whole_trajectory_stays_under_the_cap():
    for bi_h in (25, 450, 1500):
        zt = PD.zone_trajectory(t0_c=4.0, bath_c=min(220.0, 100.0), duration_min=600, steps=200, half_thickness_m=0.003,
                                alpha_m2_s=ALPHA, h_w_m2k=bi_h, k_w_mk=K)
        assert all(c <= 100.0 + 1e-6 and a <= 100.0 + 1e-6 for _, c, a in zt)


def test_reproduces_rev_a_illustration_and_the_old_model_is_kept(new, old):
    r = _rec("PROC-000001", "OVEN_AIR", 30)  # default oven bracket 180 C, diced, TYPICAL
    o, n = old.run(r), new.run(r)
    assert o["version"] == SL.VERSION_UNCAPPED != n["version"] and "cap_model" not in o
    to, tn = o["scenarios"]["TYPICAL"], n["scenarios"]["TYPICAL"]
    assert to["core_end_c"] == pytest.approx(163.73, abs=0.01) and to["core_cook_value_min"] == pytest.approx(601.88, abs=0.01)
    assert tn["core_end_c"] == pytest.approx(91.865, abs=0.01) and tn["core_cook_value_min"] == pytest.approx(6.26, abs=0.01)
    assert "boundary_c" not in to and "surface_state" not in to  # 0.1.0 records have none of the new fields
    d = new.run(_rec("PROC-000011", "OIL_IMMERSION", 5))["scenarios"]["TYPICAL"]
    assert d["core_end_c"] == pytest.approx(94.0, abs=0.01) and d["core_cook_value_min"] == pytest.approx(1.2, abs=0.01)


# ------------------------------------------------------------------------------------------------ unchanged below the boil
@pytest.mark.parametrize("proc,medium,temp", [("PROC-000020", "WATER", None), ("PROC-000021", "WATER", None),
                                              ("PROC-000019", "WATER", 100), ("PROC-000023", "WATER", None),
                                              ("PROC-000022", "STEAM", 100), ("PROC-000149", "WATER_BATH_SEALED", 62),
                                              ("PROC-000150", "LIQUID", None)])
def test_water_bath_at_or_below_the_boil_is_unchanged_against_the_old_version(new, old, proc, medium, temp):
    r = _rec(proc, medium, 25, temp, "SLICED", temp_basis="PHYSICAL_DEFINITION" if temp == 100 else "TEXT_STATED")
    o, n = old.run(r)["scenarios"], new.run(r)["scenarios"]
    for b in B:
        for k in ("bath_c", "core_end_c", "core_minutes_above_70", "core_cook_value_min", "surface_cook_value_min"):
            assert n[b][k] == o[b][k], (proc, b, k)
        assert n[b]["boundary_c"] == n[b]["bath_c"]
        assert "EVAPORATION_CAP_NOT_BINDING" in n[b]["flags"] and "EVAPORATION_CAP_APPLIED" not in n[b]["flags"]
        assert n[b]["surface_state"] == PC.IMMERSED_WET


# ------------------------------------------------------------------------------------------------ pressure
def test_pressure_cooking_exceeds_100_only_with_a_pressure_process(new, pc):
    p = new.run(_rec("PROC-000027", "WATER_PRESSURIZED", 30, size="MINCED"))["scenarios"]
    assert [p[b]["t_cap_c"] for b in B] == [108.4, 115.2, 121.0]  # 5 / 10 / 15 psig bracket, PC-002
    assert [p[b]["boundary_c"] for b in B] == [108.4, 115.2, 121.0]  # SD-006 bath 110 / 118 / 121 is cut to the saturation T
    assert p["TYPICAL"]["core_end_c"] > 110.0 and p["INTENSE"]["core_end_c"] > 100.0 + TOL
    assert all(p[b]["core_end_c"] <= p[b]["t_cap_c"] + TOL for b in B)
    assert p["TYPICAL"]["bases"]["t_cap_c"] == "PC-002"
    # the same temperatures without a pressure medium stay under 100
    q = new.run(_rec("PROC-000009", "PAN_CONTACT_OIL", 30, 118, "MINCED"))["scenarios"]["TYPICAL"]
    assert q["core_end_c"] <= 100.0 + TOL and q["t_cap_c"] == 100.0
    # a stated gauge pressure sets the cap from the saturation table
    s15 = SL.ScenarioLayer.load(policy=PC.CapPolicy(pressure_psig=15.0))
    assert s15.run(_rec("PROC-000027", "WATER_PRESSURIZED", 30, size="MINCED"))["scenarios"]["GENTLE"]["t_cap_c"] == 121.0
    with pytest.raises(ValueError):
        pc.t_sat_gauge_c(20.0)  # beyond the tabulated range: no extrapolation


def test_pressure_cap_does_not_use_altitude(pc):
    c = pc.cap(medium="WATER_PRESSURIZED", matrix_class="MEAT", bracket=2, policy=PC.CapPolicy(altitude_m=2000.0))
    assert c.t_c == 121.0 and "ALTITUDE_NOT_APPLIED_TO_PRESSURE_PROCESS" in c.flags


# ------------------------------------------------------------------------------------------------ dry class
def test_dry_class_matrix_is_not_capped_and_the_class_list_is_explicit(new, old, pc):
    assert pc.dry_classes == ("FAT_OIL", "NUT_SEED", "SWEETENER")
    for cls in pc.dry_classes:
        r = _rec("PROC-000001", "OVEN_AIR", 30, 200, "DICED", matrix=cls)
        n, o = new.run(r)["scenarios"], old.run(r)["scenarios"]
        for b in B:
            assert n[b]["t_cap_c"] is None and n[b]["boundary_c"] == 200.0
            assert n[b]["core_end_c"] == o[b]["core_end_c"] and n[b]["core_cook_value_min"] == o[b]["core_cook_value_min"]
            assert "MATRIX_DRY_CLASS_UNCAPPED" in n[b]["flags"] and "EVAPORATION_CAP_APPLIED" not in n[b]["flags"]
            assert n[b]["surface_state"] == PC.NOT_APPLICABLE_DRY
    assert new.run(_rec("PROC-000001", "OVEN_AIR", 30, 200, "DICED", matrix="NUT_SEED"))["scenarios"]["TYPICAL"]["core_end_c"] > 150
    # moist, ambiguous and unknown classes are capped, with the reason flagged
    for cls, flag in (("MEAT", None), ("CEREAL", "MATRIX_AMBIGUOUS_MOIST_ASSUMED"), (None, "MATRIX_UNKNOWN_MOIST_ASSUMED")):
        s = new.run(_rec("PROC-000001", "OVEN_AIR", 30, 200, "DICED", matrix=cls))["scenarios"]["TYPICAL"]
        assert s["core_end_c"] <= 100.0 + TOL and (flag is None or flag in s["flags"])


def test_every_ingredient_group_has_a_regime():
    groups = set()
    with open(ROOT / "ledgers/data/ING.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            g = r.get("category") or r.get("food_group")
            if g:
                groups.add(g)
    with open(ROOT / PC.REGIME_REGISTRY, newline="", encoding="utf-8") as fh:
        rows = {r["matrix_class"]: r for r in csv.DictReader(fh)}
    assert groups <= set(rows), groups - set(rows)
    assert {r["regime"] for r in rows.values()} <= {PC.MOIST, PC.AMBIGUOUS, PC.DRY}
    assert all(r["source_status"] == "SOURCE_UNVERIFIED_AGENT_RECALLED" for r in rows.values())


# ------------------------------------------------------------------------------------------------ altitude, boiling points
def test_altitude_lowers_the_cap_and_the_default_is_flagged_sea_level(pc):
    assert pc.t_boil_atmospheric_c() == (100.0, "PC-001", ("PRESSURE_ASSUMED_1ATM", "ALTITUDE_ASSUMED_SEA_LEVEL"))
    caps = [pc.t_boil_atmospheric_c(h)[0] for h in (0, 500, 1000, 1500, 2000, 3000)]
    assert caps == sorted(caps, reverse=True) and caps[0] == 99.97 and caps[-1] == 89.97
    assert pc.t_boil_atmospheric_c(2000)[0] == 93.31
    assert pc.t_boil_atmospheric_c(500)[0] == pytest.approx((99.97 + 96.65) / 2)  # linear between the tabulated rows
    with pytest.raises(ValueError):
        pc.t_boil_atmospheric_c(5000)
    layer = SL.ScenarioLayer.load(policy=PC.CapPolicy(altitude_m=2000.0))
    s = layer.run(_rec("PROC-000001", "OVEN_AIR", 240, 200, "MINCED"))["scenarios"]["TYPICAL"]
    assert s["t_cap_c"] == 93.31 and s["core_end_c"] <= 93.31 + TOL and "ALTITUDE_USER_SUPPLIED" in s["flags"]
    assert "ALTITUDE_ASSUMED_SEA_LEVEL" not in s["flags"]
    # a water bath at the sea-level boil is cut at altitude (blanch at 100 C cannot be 100 C at 2000 m)
    w = layer.run(_rec("PROC-000019", "WATER", 60, 100, "MINCED", temp_basis="PHYSICAL_DEFINITION"))["scenarios"]["TYPICAL"]
    assert w["boundary_c"] == 93.31 and w["core_end_c"] <= 93.31 + TOL


def test_saturation_table_anchor_rows(pc):
    assert pc.t_sat_gauge_c(0.0) == 100.0 and pc.t_sat_gauge_c(5.0) == 108.4 and pc.t_sat_gauge_c(15.0) == 121.0
    assert 108.4 < pc.t_sat_gauge_c(7.5) < 115.2 and pc.t_sat_gauge_c(15.552) == 121.54
    for r in csv.DictReader(open(ROOT / PC.REGISTRY, newline="", encoding="utf-8")):
        assert r["source_status"] != "SOURCE_VERIFIED" and r["source_status"]  # nothing here is human verified


# ------------------------------------------------------------------------------------------------ surface state
def test_surface_state_is_qualitative_wet_then_drying(new):
    thick = new.run(_rec("PROC-000001", "OVEN_AIR", 5, 200, "CHOPPED"))["scenarios"]
    thin = new.run(_rec("PROC-000013", "PAN_CONTACT_OIL", 600, 200, "MINCED"))["scenarios"]
    assert thick["GENTLE"]["surface_state"] == PC.WET_AT_TBOIL  # core far below the boil, surface held at T_boil
    assert thin["INTENSE"]["surface_state"] == PC.DRYING_POSSIBLE  # piece saturated: further flux can only dry the surface
    for sc in (thick, thin):
        for s in sc.values():
            assert isinstance(s["surface_state"], str)
            assert not any("crust" in k.lower() for k in s) and not any("crust" in f.lower() for f in s["flags"])
    no_size = new.run(_rec("PROC-000001", "OVEN_AIR", 30, 200, None))["scenarios"]["TYPICAL"]
    assert no_size["core_end_c"] is None and no_size["surface_state"] == PC.STATE_UNKNOWN  # never defaulted


def test_quality_dose_uses_the_volume_average_trajectory(new):
    s = new.run(_rec("PROC-000001", "OVEN_AIR", 20, 200, "DICED"))["scenarios"]["TYPICAL"]
    zt = PD.zone_trajectory(t0_c=s["initial_c"], bath_c=100.0, duration_min=20, steps=40, half_thickness_m=s["half_thickness_m"],
                            alpha_m2_s=1.4e-7, h_w_m2k=s["h"], k_w_mk=0.5)
    want = PD.trajectory_dose([(m, a) for m, _, a in zt], t_ref_c=100.0, z_c=33.0)
    assert s["quality_cook_value_min"] == pytest.approx(want, abs=1e-4)
    assert s["quality_cook_value_min"] >= s["core_cook_value_min"]  # the core dose is the lower bound
    assert s["volume_avg_end_c"] == pytest.approx(zt[-1][2], abs=1e-3)


# ------------------------------------------------------------------------------------------------ mean temperature
@pytest.mark.parametrize("h,L,t", [(25, 0.01, 600), (500, 0.005, 60), (1500, 0.0025, 10), (10, 0.02, 3600), (450, 0.005, 3),
                                   (25, 0.0005, 5)])
def test_slab_volume_average_matches_a_fine_finite_difference_reference(h, L, t):
    c, a = PD.core_and_mean_temperature(t0_c=20.0, bath_c=100.0, time_s=t, half_thickness_m=L, alpha_m2_s=ALPHA,
                                        h_w_m2k=h, k_w_mk=K)
    ref = ND.slab_two_stage(t0_c=20.0, stages=[(t / 60.0, 100.0, h)], half_thickness_m=L, alpha_m2_s=ALPHA, k_w_mk=K, n=400)
    assert a == pytest.approx(ref["stage_end"][0]["volume_avg_c"], abs=0.02)
    assert c == pytest.approx(ref["stage_end"][0]["centre_c"], abs=0.02)


def test_slab_mean_theta_limits_and_continuity():
    assert PD.slab_mean_theta(fo=0.0, bi=5.0) == 1.0 and PD.slab_mean_theta(fo=20.0, bi=5.0) == pytest.approx(0.0, abs=1e-9)
    for bi in (0.05, 1.0, 36.0):
        lo = PD.slab_mean_theta(fo=PD.FO_FRONT * (1 - 1e-9), bi=bi)
        hi = PD.slab_mean_theta(fo=PD.FO_FRONT * (1 + 1e-9), bi=bi)
        assert lo == pytest.approx(hi, abs=2e-6)  # semi-infinite branch meets the series
        assert PD.slab_mean_theta(fo=0.5, bi=bi) <= PD.slab_mean_theta(fo=0.2, bi=bi)
    assert PD.slab_mean_theta(fo=1e-9, bi=1e-3) == pytest.approx(1.0, abs=1e-9)
    with pytest.raises(ValueError):
        PD.slab_mean_theta(fo=-1.0, bi=1.0)


# ------------------------------------------------------------------------------------------------ exact two-stage slab
def test_exact_scheme_equals_the_old_crank_nicolson_on_normal_cases():
    worst_c = worst_p = worst_s = 0.0
    for L in (0.0025, 0.005, 0.012):
        for hdur, hh in ((10, 25), (30, 50), (8, 450), (3, 15)):
            for rdur in (5, 30):
                st = [(hdur, 180.0, hh), (rdur, 21.0, 10.0)]
                a = ND.slab_two_stage(t0_c=20.0, stages=st, half_thickness_m=L, alpha_m2_s=ALPHA, k_w_mk=K, method="cn")
                b = ND.slab_two_stage(t0_c=20.0, stages=st, half_thickness_m=L, alpha_m2_s=ALPHA, k_w_mk=K)
                for i in (0, 1):
                    worst_c = max(worst_c, abs(a["stage_end"][i]["centre_c"] - b["stage_end"][i]["centre_c"]))
                    worst_s = max(worst_s, abs(a["stage_end"][i]["surface_c"] - b["stage_end"][i]["surface_c"]))
                worst_p = max(worst_p, abs(a["centre_peak_last_stage_c"] - b["centre_peak_last_stage_c"]))
    assert worst_c < 0.01 and worst_p < 0.01 and worst_s < 0.1


def test_exact_scheme_surface_agrees_with_the_analytic_series_where_the_old_stepper_does_not():
    # Bi = 60, Fo = 0.063: Crank-Nicolson at Fo_step 0.004 is about 1.1 C low at the surface node, the exact scheme is not
    st = [(3.0, 180.0, 1500.0)]
    fo, bi = ALPHA * 180.0 / 0.02 ** 2, 1500.0 * 0.02 / K
    series = 180.0 - 160.0 * sum(4 * math.sin(z) / (2 * z + math.sin(2 * z)) * math.cos(z) * math.exp(-z * z * fo)
                                 for z in PD.slab_eigenvalues(bi, 60))
    exact = ND.slab_two_stage(t0_c=20.0, stages=st, half_thickness_m=0.02, alpha_m2_s=ALPHA, k_w_mk=K)["stage_end"][0]["surface_c"]
    cn = ND.slab_two_stage(t0_c=20.0, stages=st, half_thickness_m=0.02, alpha_m2_s=ALPHA, k_w_mk=K,
                           method="cn")["stage_end"][0]["surface_c"]
    assert exact == pytest.approx(series, abs=0.05) and abs(cn - series) > 0.5


def test_very_long_thin_resting_stage_finishes_fast():
    t = time.perf_counter()
    r = ND.slab_two_stage(t0_c=20.0, stages=[(10080.0, 180.0, 25.0), (20160.0, 21.0, 10.0)], half_thickness_m=0.0005,
                          alpha_m2_s=ALPHA, k_w_mk=K, caps=[100.0, 100.0])
    assert time.perf_counter() - t < 1.0  # the Crank-Nicolson stepper needed about 1.7e8 steps here
    assert r["stage_end"][0]["centre_c"] == pytest.approx(100.0, abs=1e-6)
    assert r["stage_end"][1]["centre_c"] == pytest.approx(21.0, abs=1e-6) and r["centre_peak_last_stage_c"] == pytest.approx(100.0, abs=1e-3)


def test_two_stage_validation_and_caps_clip():
    with pytest.raises(ValueError):
        ND.slab_two_stage(t0_c=20.0, stages=[(10.0, 100.0, 5.0)], half_thickness_m=0.01, alpha_m2_s=ALPHA, k_w_mk=K, caps=[1.0, 2.0])
    with pytest.raises(ValueError):
        ND.slab_two_stage(t0_c=20.0, stages=[(10.0, 100.0, 5.0)], half_thickness_m=0.01, alpha_m2_s=ALPHA, k_w_mk=K, method="x")
    # a pressure stage handed to an atmospheric stage is clipped to the atmospheric T_boil
    r = ND.slab_two_stage(t0_c=20.0, stages=[(60.0, 121.0, 3000.0), (5.0, 21.0, 10.0)], half_thickness_m=0.002,
                          alpha_m2_s=ALPHA, k_w_mk=K, caps=[121.0, 100.0])
    assert r["stage_end"][0]["clamped_at_start"] is False and r["stage_end"][1]["clamped_at_start"] is True
    assert r["stage_end"][0]["centre_c"] > 119.0 and r["centre_peak_last_stage_c"] <= 100.0 + 1e-6


# ------------------------------------------------------------------------------------------------ non-heat RESTING
def _rest_rec(medium="OVEN_AIR", matrix=None, hdur="30", bath="200", rest="10", size="DICED", proc="PROC-000002",
              hbasis="TEXT_STATED"):
    def known(v, b):
        return {"value": v, "status": "MEASURED", "basis": b, "span": None}

    def unk():
        return {"value": None, "status": "UNKNOWN", "basis": None, "span": None}
    hinp = {k: unk() for k in ("duration", "temperature_profile", "medium", "lid_state", "start_mode", "piece_size_class",
                               "water_ratio", "matrix_class")}
    hinp.update(duration=known(hdur, "TEXT_STATED"), temperature_profile=known(bath, hbasis), medium=known(medium, "PROCESS_DEFINITION"),
                piece_size_class=known(size, "CUT_HISTORY"))
    if matrix:
        hinp["matrix_class"] = known(matrix, "FOOD_GROUP")
    inputs = {"duration": known(rest, "TEXT_STATED"), "environment": unk(), "cover_state": unk(), "piece_size_class": unk()}
    return {"recipe_id": "R", "event_id": "E2", "process_id": "PROC-000042", "nh_family": "RESTING", "process_role": "rest",
            "form_candidate": "CARRYOVER_CONDUCTION_STILL_AIR", "cues": [], "inputs": inputs,
            "history": {"prior_heat": {"process_id": proc, "inputs": hinp, "oven_setpoint_code": None, "basis": "LINEAGE"}}}


@pytest.fixture(scope="module")
def nh_new():
    return NS.NonHeatScenario.load()


@pytest.fixture(scope="module")
def nh_old():
    return NS.NonHeatScenario.load(policy=PC.CapPolicy(enabled=False))


def test_nonheat_resting_is_capped_and_the_old_model_is_not(nh_new, nh_old):
    r = _rest_rec()
    n, o = nh_new.run(r), nh_old.run(r)
    assert n["status"] == o["status"] == "SCENARIO_COMPUTED" and n["version"] == NS.VERSION != o["version"]
    for b in B:
        s = n["scenarios"][b]
        assert s["core_peak_c"] <= 100.0 + TOL and s["core_end_of_heat_c"] <= 100.0 + TOL
        assert s["volume_avg_end_c"] <= 100.0 + TOL and s["t_cap_c"] == 100.0 and s["boundary_c"] == 100.0
        assert "EVAPORATION_CAP_APPLIED" in s["flags"] and "NO_EVAPORATION_CAP_AT_100C" not in s["flags"]
        so = o["scenarios"][b]
        assert "NO_EVAPORATION_CAP_AT_100C" in so["flags"] and "t_cap_c" not in so
    assert o["scenarios"]["INTENSE"]["core_peak_c"] > 150.0  # the SUPERSEDED value


def test_nonheat_resting_after_water_bath_unchanged_and_after_dry_matrix_uncapped(nh_new, nh_old):
    r = _rest_rec(medium="WATER", bath="90", proc="PROC-000020", hdur="20")
    n, o = nh_new.run(r)["scenarios"], nh_old.run(r)["scenarios"]
    for b in B:
        for k in ("core_end_of_heat_c", "core_peak_c", "core_end_c", "carryover_rise_c"):
            assert n[b][k] == pytest.approx(o[b][k], abs=1e-9)
    d = nh_new.run(_rest_rec(matrix="NUT_SEED"))["scenarios"]["TYPICAL"]
    assert d["t_cap_c"] is None and d["core_peak_c"] > 150.0 and "MATRIX_DRY_CLASS_UNCAPPED" in d["flags"]


def test_nonheat_resting_after_pressure_cooking_can_exceed_100_and_is_clipped_on_release(nh_new):
    r = _rest_rec(medium="WATER_PRESSURIZED", proc="PROC-000027", hdur="40", bath="118", rest="10", size="MINCED")
    s = nh_new.run(r)["scenarios"]
    assert s["INTENSE"]["core_end_of_heat_c"] > 100.0 + TOL  # pressure process
    assert s["INTENSE"]["core_peak_c"] <= s["INTENSE"]["core_end_of_heat_c"] + 1e-6
    assert "PRESSURE_RELEASE_PROFILE_CLIPPED_TO_ATMOSPHERIC_TBOIL" in s["INTENSE"]["flags"]
    assert s["INTENSE"]["core_end_c"] <= 100.0 + TOL


def test_nonheat_resting_very_long_prior_heat_on_a_thin_piece_runs_in_under_a_second(nh_new):
    r = _rest_rec(hdur="20160", rest="20160", size="MINCED")
    t = time.perf_counter()
    out = nh_new.run(r)
    assert time.perf_counter() - t < 1.0 and out["status"] == "SCENARIO_COMPUTED"
    assert all(out["scenarios"][b]["core_peak_c"] <= 100.0 + TOL for b in B)


# ------------------------------------------------------------------------------------------------ tools
@pytest.fixture(scope="module")
def l2_tool():
    spec = importlib.util.spec_from_file_location("scenario_layer_run", ROOT / "tools/scenario_layer_run.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["scenario_layer_run"] = m
    spec.loader.exec_module(m)
    return m


def test_scenario_tool_compare_uncapped_counts_only(l2_tool, tmp_path):
    l1 = tmp_path / "l1"
    l1.mkdir()
    recs = [_rec("PROC-000001", "OVEN_AIR", 30, 200), _rec("PROC-000011", "OIL_IMMERSION", 5), _rec("PROC-000019", "WATER", 20, 100,
            temp_basis="PHYSICAL_DEFINITION"), _rec("PROC-000027", "WATER_PRESSURIZED", 20, size="MINCED"),
            _rec("PROC-000001", "OVEN_AIR", 30, 200, matrix="NUT_SEED")]
    (l1 / "part-0.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    out = tmp_path / "rep.json"
    assert l2_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2"), "--out", str(out), "--compare-uncapped"]) == 0
    rep = json.loads(out.read_text())
    ba = rep["before_after"]["counts"]
    assert rep["layer_version"] == SL.VERSION and rep["cap_model"] == PC.VERSION and rep["counts_as_human_gate"] is False
    assert ba["after"]["heat_events"] == ba["before"]["heat_events"] == 5
    assert ba["after"]["core_computed"] == ba["before"]["core_computed"]  # coverage unchanged
    assert ba["before"]["events_core_gt_100_nonpressure_any_bracket"] == 3  # oven, oil, uncapped dry class
    assert ba["after"]["events_core_gt_100_nonpressure_any_bracket"] == 1  # only the dry-class nut matrix
    assert "events_violating_cap_any_bracket" not in ba["after"]
    assert "events_core_gt_100_nonpressure_moist_class_any_bracket" not in ba["after"]  # moist matrix: never above the cap
    assert ba["before"]["events_core_gt_100_nonpressure_moist_class_any_bracket"] == 2
    assert ba["after"]["typical_core_computed_dry_class"] == 1
    q = rep["before_after"]["dose_quantiles"]
    assert q["before"]["core_cook_value_min"]["TYPICAL"]["max"] > 10 * q["after"]["core_cook_value_min"]["TYPICAL"]["p50"]
    assert rep["dry_low_moisture_classes"] == ["FAT_OIL", "NUT_SEED", "SWEETENER"]
    with pytest.raises(SystemExit):  # never overwrites
        l2_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2b"), "--out", str(out)])
    written = [json.loads(x) for x in (tmp_path / "l2" / "part-0.jsonl").read_text().splitlines()]
    assert all(w["version"] == SL.VERSION for w in written)  # per-event records are the capped model's
