"""S177 SCIFIX-PHYS row 2 (FINAL-SCI): zone-resolved local doses.

The 0.2.0 field ``quality_cook_value_min`` was the dose of the volume-average TEMPERATURE. By convexity of 10^(T/z) that is
never larger than the volume average of the LOCAL dose. 0.3.0 renames it ``cook_value_at_volume_avg_t_min`` (flag
NOT_A_ZONE_MEAN_DOSE), emits the local temperature histories at Gauss-Legendre nodes of the half slab and their volume-mean
dose, and lets a later kinetic model compute mean(exp(-int k dt)) from the stored histories.
"""
from __future__ import annotations

import math

import pytest

from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import physics_drivers as PD
from culinarystate.simulation import scenario_layer as SL
from tests.unit.test_s176_phys_cap import ALPHA, B, K, _rec

PROPS = dict(alpha_m2_s=ALPHA, k_w_mk=K)


@pytest.fixture(scope="module")
def new():
    return SL.ScenarioLayer.load()


# ------------------------------------------------------------------------------------------------ quadrature
@pytest.mark.parametrize("n", [6, 7, 8, 12])
def test_gauss_legendre_half_slab_weights_nodes_and_exactness(n):
    xi, w = PD.gauss_legendre_half_slab(n)
    assert len(xi) == len(w) == n and sum(w) == pytest.approx(1.0, abs=1e-14)
    assert all(0.0 < x < 1.0 for x in xi) and list(xi) == sorted(xi) and all(v > 0 for v in w)
    for k in range(2 * n):  # exact for polynomials of degree 2n - 1: mean of xi^k over [0, 1] is 1 / (k + 1)
        assert sum(wi * x ** k for wi, x in zip(w, xi)) == pytest.approx(1.0 / (k + 1), abs=1e-12)


def test_gauss_legendre_rejects_nonsense():
    for bad in (0, 65):
        with pytest.raises(ValueError):
            PD.gauss_legendre_half_slab(bad)


# ------------------------------------------------------------------------------------------------ local temperature
@pytest.mark.parametrize("bi", [0.5, 6.0, 40.0])
@pytest.mark.parametrize("fo", [0.005, 0.0199, 0.05, 0.3, 1.5])
def test_slab_theta_centre_equals_the_centre_series(bi, fo):
    assert PD.slab_theta(0.0, fo=fo, bi=bi) == pytest.approx(PD.slab_center_theta(fo=fo, bi=bi), abs=2e-6)


@pytest.mark.parametrize("bi", [0.5, 6.0, 40.0])
@pytest.mark.parametrize("xi", [0.0, 0.2, 0.7, 0.95, 1.0])
def test_slab_theta_is_continuous_across_the_front_switch(bi, xi):
    lo, hi = PD.slab_theta(xi, fo=PD.FO_FRONT * (1 - 1e-9), bi=bi), PD.slab_theta(xi, fo=PD.FO_FRONT * (1 + 1e-9), bi=bi)
    assert abs(lo - hi) < 2e-6


@pytest.mark.parametrize("bi,fo", [(6, 0.05), (6, 0.5), (2, 0.1), (30, 0.02), (30, 0.3), (0.5, 2.0)])
def test_mean_of_local_theta_equals_the_volume_average_series(bi, fo):
    xi, w = PD.gauss_legendre_half_slab(12)
    assert sum(wi * PD.slab_theta(x, fo=fo, bi=bi) for x, wi in zip(xi, w)) == pytest.approx(PD.slab_mean_theta(fo=fo, bi=bi), abs=1e-6)


def test_slab_theta_surface_in_the_front_regime_is_the_closed_form():
    bi, fo = 6.0, 0.004
    u = bi * math.sqrt(fo)
    assert PD.slab_theta(1.0, fo=fo, bi=bi) == pytest.approx(math.exp(u * u) * math.erfc(u), abs=1e-12)


def test_slab_theta_surface_and_centre_against_the_finite_difference_slab():
    # independent reference: the exact-in-time modal solution of a 200-node finite-difference slab
    for bi, minutes in ((6.0, 4.0), (20.0, 12.0), (2.0, 30.0)):
        L, h = 0.005, bi * K / 0.005
        res = ND.slab_two_stage(t0_c=20.0, stages=[(minutes, 100.0, h)], half_thickness_m=L, n=200, **PROPS)["stage_end"][0]
        fo = ALPHA * 60 * minutes / L ** 2
        assert 100.0 + (20.0 - 100.0) * PD.slab_theta(1.0, fo=fo, bi=bi) == pytest.approx(res["surface_c"], abs=0.06)
        assert 100.0 + (20.0 - 100.0) * PD.slab_theta(0.0, fo=fo, bi=bi) == pytest.approx(res["centre_c"], abs=0.02)


def test_slab_theta_is_ordered_in_depth_and_time_and_validates():
    fo, bi = 0.08, 8.0
    th = [PD.slab_theta(x / 10, fo=fo, bi=bi) for x in range(11)]
    assert th == sorted(th, reverse=True)  # theta = (T - T_bath)/(T_0 - T_bath): smallest at the surface (most heated)
    assert PD.slab_theta(0.5, fo=0.0, bi=bi) == 1.0
    series = [PD.slab_theta(0.6, fo=f, bi=bi) for f in (0.001, 0.01, 0.03, 0.1, 0.4)]
    assert series == sorted(series, reverse=True)
    for kw in ({"xi": -0.1, "fo": 0.1}, {"xi": 1.1, "fo": 0.1}, {"xi": 0.5, "fo": -0.1}):
        with pytest.raises(ValueError):
            PD.slab_theta(kw["xi"], fo=kw["fo"], bi=bi)


# ------------------------------------------------------------------------------------------------ histories and doses
def _hist(t0=20.0, bath=98.0, dur=10.0, L=0.005, h=600.0, **kw):
    return PD.zone_node_histories(t0_c=t0, bath_c=bath, duration_min=dur, half_thickness_m=L, h_w_m2k=h, **PROPS, **kw)


def test_zone_node_histories_shape_grid_and_limits():
    hist = _hist()
    assert len(hist["xi"]) == len(hist["weights"]) == 8 and len(hist["temps_c"]) == 8
    assert len(hist["times_min"]) == PD.N_ZONE_TIMES + 1 == len(hist["temps_c"][0])
    t = hist["times_min"]
    assert t[0] == 0.0 and t[-1] == pytest.approx(10.0) and all(b > a for a, b in zip(t, t[1:]))
    assert t[1] < 10.0 / PD.N_ZONE_TIMES  # fine steps early (a node near the surface moves within seconds)
    assert all(row[0] == pytest.approx(20.0) for row in hist["temps_c"])
    ends = [row[-1] for row in hist["temps_c"]]
    assert ends == sorted(ends) and all(20.0 < e < 98.0 for e in ends)  # outer nodes are hotter
    for row in hist["temps_c"]:
        assert all(b >= a - 1e-9 for a, b in zip(row, row[1:]))  # heating, never cooling


def test_zone_node_histories_match_core_temperature_for_a_thin_set_of_nodes_and_validate():
    hist = PD.zone_node_histories(t0_c=20.0, bath_c=100.0, duration_min=20.0, half_thickness_m=0.005, h_w_m2k=600.0, n_nodes=6, **PROPS)
    for i, x in enumerate(hist["xi"]):
        for j in (10, 30, 48):
            fo = ALPHA * 60 * hist["times_min"][j] / 0.005 ** 2
            assert hist["temps_c"][i][j] == pytest.approx(100.0 + (20.0 - 100.0) * PD.slab_theta(x, fo=fo, bi=6.0), abs=1e-9)
    for kw in ({"half_thickness_m": 0.0}, {"alpha_m2_s": -1.0}, {"h_w_m2k": 0.0}, {"k_w_mk": 0.0}):
        args = dict(t0_c=20.0, bath_c=98.0, duration_min=5.0, half_thickness_m=0.005, alpha_m2_s=ALPHA, h_w_m2k=600.0, k_w_mk=K)
        args.update(kw)
        with pytest.raises(ValueError):
            PD.zone_node_histories(**args)
    with pytest.raises(ValueError):
        PD.zone_time_grid(0.0)


@pytest.mark.parametrize("L,h,dur,bath", [(0.005, 600.0, 2.0, 98.0), (0.0025, 1500.0, 5.0, 100.0), (0.0125, 25.0, 30.0, 100.0),
                                           (0.003, 500.0, 8.0, 121.0), (0.0005, 200.0, 1.0, 100.0)])
def test_zone_mean_dose_against_a_dense_reference(L, h, dur, bath):
    got = PD.zone_mean_dose(_hist(bath=bath, dur=dur, L=L, h=h), t_ref_c=100.0, z_c=33.0)
    ref = PD.zone_mean_dose(_hist(bath=bath, dur=dur, L=L, h=h, n_nodes=64, n_times=1200, power=3.0), t_ref_c=100.0, z_c=33.0)
    assert got == pytest.approx(ref, rel=0.01)  # 8 nodes, 48 graded times: within 1 % of a 64-node, 1,200-time reference


def test_the_dose_at_the_volume_average_temperature_is_low_early_and_converges_late():
    """Hand calculation of FINAL-SCI row 2: 1 cm dice, bath 98 C, Bi = 6, z = 33 (the exact factor is pinned here)."""
    ratios = {}
    for dur in (0.5, 2.0, 15.0):
        zt = PD.zone_trajectory(t0_c=20.0, bath_c=98.0, duration_min=dur, steps=40, half_thickness_m=0.005, alpha_m2_s=ALPHA,
                                h_w_m2k=600.0, k_w_mk=K)
        at_mean = PD.trajectory_dose([(m, v) for m, _, v in zt], t_ref_c=100.0, z_c=33.0)
        zone = PD.zone_mean_dose(_hist(dur=dur), t_ref_c=100.0, z_c=33.0)
        ratios[dur] = zone / at_mean
    assert ratios[0.5] > 1.5 and ratios[2.0] > 1.2 and 1.0 < ratios[15.0] < 1.05  # the old field was low by these factors
    assert ratios[0.5] > ratios[2.0] > ratios[15.0]


@pytest.mark.parametrize("z", [10.0, 20.0, 33.0])
def test_zone_mean_dose_is_never_below_the_dose_of_the_mean_temperature_and_is_worse_for_small_z(z):
    zt = PD.zone_trajectory(t0_c=20.0, bath_c=98.0, duration_min=3.0, steps=40, half_thickness_m=0.005, alpha_m2_s=ALPHA,
                            h_w_m2k=600.0, k_w_mk=K)
    at_mean = PD.trajectory_dose([(m, v) for m, _, v in zt], t_ref_c=100.0, z_c=z)
    assert PD.zone_mean_dose(_hist(dur=3.0), t_ref_c=100.0, z_c=z) >= at_mean


def test_smaller_z_widens_the_gap():
    def gap(z):
        zt = PD.zone_trajectory(t0_c=20.0, bath_c=98.0, duration_min=3.0, steps=40, half_thickness_m=0.005, alpha_m2_s=ALPHA,
                                h_w_m2k=600.0, k_w_mk=K)
        return PD.zone_mean_dose(_hist(dur=3.0), t_ref_c=100.0, z_c=z) / PD.trajectory_dose([(m, v) for m, _, v in zt],
                                                                                              t_ref_c=100.0, z_c=z)
    assert gap(10.0) > gap(20.0) > gap(33.0) > 1.0


def test_local_dose_constant_temperature_and_validation():
    assert PD.local_dose([0.0, 5.0, 10.0], [110.0, 110.0, 110.0], t_ref_c=100.0, z_c=10.0) == pytest.approx(100.0)
    with pytest.raises(ValueError):
        PD.local_dose([0.0, 1.0], [100.0, 100.0], t_ref_c=100.0, z_c=0.0)


def test_zone_mean_survival_is_first_order_exact_and_jensen_bounded():
    hist = _hist(dur=10.0)
    assert PD.zone_mean_survival(hist, lambda t: 0.1) == pytest.approx(math.exp(-0.1 * 10.0), rel=1e-12)  # k constant
    kref = 0.05  # per minute at T_ref
    rate = lambda t: kref * 10 ** ((t - 100.0) / 33.0)  # noqa: E731 - the dose rate scaled by kref: a z-model of M3's form
    mean_surv = PD.zone_mean_survival(hist, rate)
    doses = PD.node_doses(hist, t_ref_c=100.0, z_c=33.0)
    want = sum(w * math.exp(-kref * f) for w, f in zip(hist["weights"], doses))
    assert mean_surv == pytest.approx(want, rel=1e-12)
    # retention of the mean dose over-states the loss: mean exp(-k F) >= exp(-k mean F) (Jensen)
    assert mean_surv >= math.exp(-kref * PD.zone_mean_dose(hist, t_ref_c=100.0, z_c=33.0)) - 1e-12


# ------------------------------------------------------------------------------------------------ Layer 2 records
def _typical(new, dur=20, temp=200, size="DICED", **kw):
    return new.run(_rec("PROC-000001", "OVEN_AIR", dur, temp, size, **kw))["scenarios"]["TYPICAL"]


def test_layer_renames_the_field_and_flags_it_and_keeps_the_core_dose(new):
    assert SL.VERSION == "scenario-layer-L2-0.3.0-draft" and PC.VERSION == "evaporation-cap-0.2.0-draft"
    out = new.run(_rec("PROC-000001", "OVEN_AIR", 20, 200, "DICED"))
    assert out["version"] == SL.VERSION
    for b in B:
        s = out["scenarios"][b]
        assert "quality_cook_value_min" not in s and s["cook_value_at_volume_avg_t_min"] is not None
        assert "NOT_A_ZONE_MEAN_DOSE" in s["flags"] and s["core_cook_value_min"] is not None


def test_layer_emits_zone_nodes_consistent_with_its_own_fields(new):
    out = new.run(_rec("PROC-000001", "OVEN_AIR", 20, 200, "DICED"))
    for b in B:
        s = out["scenarios"][b]
        zn = s["zone_nodes"]
        assert zn["n_nodes"] == 8 and zn["scheme"] == "GAUSS_LEGENDRE_HALF_SLAB_8" and zn["z_c"] == 33.0 and zn["t_ref_c"] == 100.0
        assert sum(zn["weights"]) == pytest.approx(1.0, abs=1e-6) and len(zn["temps_c"]) == 8
        assert all(len(row) == len(zn["times_min"]) for row in zn["temps_c"]) and zn["times_min"][-1] == pytest.approx(s["duration_min"], abs=1e-4)
        # the stored histories reproduce the stored node doses and the zone-mean dose (storage rounds temperatures to 0.01 C)
        redo = [PD.local_dose(zn["times_min"], row, t_ref_c=100.0, z_c=33.0) for row in zn["temps_c"]]
        assert redo == pytest.approx(zn["node_cook_value_min"], rel=2e-3, abs=1e-3)
        assert s["zone_mean_cook_value_min"] == pytest.approx(sum(w * f for w, f in zip(zn["weights"], zn["node_cook_value_min"])), rel=1e-3,
                                                              abs=1e-3)
        # the weighted end temperature is the volume-average temperature
        end = sum(w * row[-1] for w, row in zip(zn["weights"], zn["temps_c"]))
        assert end == pytest.approx(s["volume_avg_end_c"], abs=0.1)
        # ordering: core dose <= dose at the volume-average temperature <= zone-mean dose
        assert s["core_cook_value_min"] <= s["cook_value_at_volume_avg_t_min"] + 1e-4
        assert s["zone_mean_cook_value_min"] >= s["cook_value_at_volume_avg_t_min"] - 1e-3
        assert "ZONE_NODE_HISTORIES_EMITTED_FOR_OWN_KINETICS" in s["flags"]


def test_stored_histories_feed_a_kinetic_model_with_its_own_rate(new):
    zn = _typical(new)["zone_nodes"]
    hist = {"weights": zn["weights"], "times_min": zn["times_min"], "temps_c": zn["temps_c"]}
    ea_over_r, t_ref = 12000.0, 373.15  # an Arrhenius rate with its own Ea, not the cook-value convention
    k = lambda tc: 0.01 * math.exp(-ea_over_r * (1.0 / (tc + 273.15) - 1.0 / t_ref))  # noqa: E731
    r = PD.zone_mean_survival(hist, k)
    assert 0.0 < r < 1.0 and r == pytest.approx(PD.zone_mean_survival(hist, k))


def test_nodes_obey_the_capped_boundary_and_the_cap_is_unchanged_for_moist_dry_heat(new):
    s = _typical(new, dur=60)
    assert s["t_cap_c"] == 100.0
    assert max(max(row) for row in s["zone_nodes"]["temps_c"]) <= 100.0 + 0.5
    assert s["zone_mean_cook_value_min"] > 0


def test_uncapped_superseded_model_has_no_zone_fields_and_equal_core_fields():
    old = SL.ScenarioLayer.load(policy=PC.CapPolicy(enabled=False))
    s = old.run(_rec("PROC-000001", "OVEN_AIR", 20, 200, "DICED"))["scenarios"]["TYPICAL"]
    assert "zone_nodes" not in s and "cook_value_at_volume_avg_t_min" not in s and "NOT_A_ZONE_MEAN_DOSE" not in s["flags"]
    assert s["core_cook_value_min"] > 100  # the SUPERSEDED value is still reproduced


def test_unknown_size_gives_no_zone_fields(new):
    s = _typical(new, size=None)
    assert s["core_end_c"] is None and s["zone_mean_cook_value_min"] is None and "zone_nodes" not in s


def test_node_count_is_limited_to_six_to_eight():
    for n in (6, 7, 8):
        assert SL.ScenarioLayer.load(n_nodes=n).run(_rec("PROC-000001", "OVEN_AIR", 20, 200, "DICED"))["scenarios"]["TYPICAL"][
            "zone_nodes"]["n_nodes"] == n
    for n in (4, 5, 9, 16):
        with pytest.raises(ValueError):
            SL.ScenarioLayer.load(n_nodes=n)


# ------------------------------------------------------------------------------------------------ old records are still read
def test_volume_avg_dose_reads_the_new_and_the_legacy_name():
    assert SL.volume_avg_dose({"cook_value_at_volume_avg_t_min": 2.5}) == 2.5
    assert SL.volume_avg_dose({"quality_cook_value_min": 3.5}) == 3.5  # a 0.2.0 record
    assert SL.volume_avg_dose({"cook_value_at_volume_avg_t_min": 2.5, "quality_cook_value_min": 3.5}) == 2.5
    assert SL.volume_avg_dose({"core_cook_value_min": 1.0}) is None
    assert SL.volume_avg_dose({"cook_value_at_volume_avg_t_min": None, "quality_cook_value_min": None}) is None


def test_the_run_tool_reads_old_records_through_the_same_reader():
    import importlib.util
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("scenario_layer_run", root / "tools/scenario_layer_run.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["scenario_layer_run"] = m
    spec.loader.exec_module(m)
    assert "quality_cook_value_min" not in m.DOSE_FIELDS and "cook_value_at_volume_avg_t_min" in m.DOSE_FIELDS
    assert m._dose({"quality_cook_value_min": 4.0}, "cook_value_at_volume_avg_t_min") == 4.0
    assert m._dose({"cook_value_at_volume_avg_t_min": 5.0}, "cook_value_at_volume_avg_t_min") == 5.0
    assert m._dose({"core_cook_value_min": 6.0}, "core_cook_value_min") == 6.0
