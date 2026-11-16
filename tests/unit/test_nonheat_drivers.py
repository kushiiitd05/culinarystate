"""S176 L-NH: non-heat physics drivers against analytic solutions and limit cases. No recipe text, no registry."""
from __future__ import annotations

import math

import pytest

from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import physics_drivers as PD

ALPHA, K = 1.4e-7, 0.5


@pytest.mark.parametrize("h,L,dur", [(25, 0.01, 30), (500, 0.005, 10), (1500, 0.0025, 3), (10, 0.02, 60)])
def test_finite_difference_slab_matches_analytic_series(h, L, dur):
    fd = ND.slab_two_stage(t0_c=20.0, stages=[(dur, 180.0, h)], half_thickness_m=L, alpha_m2_s=ALPHA, k_w_mk=K)
    an = PD.core_temperature(t0_c=20.0, bath_c=180.0, time_s=60.0 * dur, half_thickness_m=L, alpha_m2_s=ALPHA,
                             h_w_m2k=h, k_w_mk=K)
    assert fd["stage_end"][0]["centre_c"] == pytest.approx(an, abs=0.05)


def test_finite_difference_cooling_matches_series_with_cold_bath():
    fd = ND.slab_two_stage(t0_c=90.0, stages=[(120.0, 4.0, 10.0)], half_thickness_m=0.02, alpha_m2_s=ALPHA, k_w_mk=K)
    an = PD.core_temperature(t0_c=90.0, bath_c=4.0, time_s=7200.0, half_thickness_m=0.02, alpha_m2_s=ALPHA,
                             h_w_m2k=10.0, k_w_mk=K)
    assert fd["stage_end"][0]["centre_c"] == pytest.approx(an, abs=0.05)


def test_carryover_centre_keeps_rising_after_heat_stops_and_never_exceeds_the_hot_medium():
    r = ND.slab_two_stage(t0_c=20.0, stages=[(20.0, 200.0, 25.0), (10.0, 21.0, 10.0)], half_thickness_m=0.02,
                          alpha_m2_s=ALPHA, k_w_mk=K)
    heat_end, rest_end = r["stage_end"]
    assert r["centre_peak_last_stage_c"] > heat_end["centre_c"] + 1.0  # carry-over exists for a thick piece
    assert rest_end["surface_c"] < heat_end["surface_c"]  # the surface cools in still air
    assert r["centre_peak_last_stage_c"] < 200.0


def test_second_stage_at_the_same_ambient_is_the_same_as_one_long_stage():
    one = ND.slab_two_stage(t0_c=20.0, stages=[(30.0, 150.0, 40.0)], half_thickness_m=0.01, alpha_m2_s=ALPHA, k_w_mk=K)
    two = ND.slab_two_stage(t0_c=20.0, stages=[(10.0, 150.0, 40.0), (20.0, 150.0, 40.0)], half_thickness_m=0.01,
                            alpha_m2_s=ALPHA, k_w_mk=K)
    assert two["stage_end"][1]["centre_c"] == pytest.approx(one["stage_end"][0]["centre_c"], abs=0.05)


def test_slab_inputs_validated():
    with pytest.raises(ValueError):
        ND.slab_two_stage(t0_c=20.0, stages=[], half_thickness_m=0.01, alpha_m2_s=ALPHA, k_w_mk=K)
    with pytest.raises(ValueError):
        ND.slab_two_stage(t0_c=20.0, stages=[(10.0, 100.0, 0.0)], half_thickness_m=0.01, alpha_m2_s=ALPHA, k_w_mk=K)


# ------------------------------------------------------------------------------------------------ Plank limit cases
PL = dict(rho=1000.0, latent_j_kg=250e3, t_freeze_c=-1.0, t_air_c=-20.0, thickness_m=0.02, k_frozen_w_mk=1.5)


def test_plank_conduction_limit_h_to_infinity():
    t = PD.plank_freezing_time_s(**PL, h_w_m2k=1e12)
    assert t == pytest.approx(1000 * 250e3 / 19.0 * 0.125 * 0.02 ** 2 / 1.5, rel=1e-9)


def test_plank_convection_limit_k_to_infinity():
    t = PD.plank_freezing_time_s(**{**PL, "k_frozen_w_mk": 1e15}, h_w_m2k=20.0)
    assert t == pytest.approx(1000 * 250e3 / 19.0 * 0.5 * 0.02 / 20.0, rel=1e-9)


def test_plank_scales_inversely_with_driving_force_and_quadratically_with_thickness_in_conduction_limit():
    t1 = PD.plank_freezing_time_s(**PL, h_w_m2k=1e12)
    t2 = PD.plank_freezing_time_s(**{**PL, "t_air_c": -39.0}, h_w_m2k=1e12)  # driving force 19 -> 38
    assert t2 == pytest.approx(t1 / 2, rel=1e-9)
    t3 = PD.plank_freezing_time_s(**{**PL, "thickness_m": 0.04}, h_w_m2k=1e12)
    assert t3 == pytest.approx(4 * t1, rel=1e-9)


def test_thaw_is_plank_run_in_reverse_with_the_unfrozen_conductivity():
    t = ND.thaw_time_s(rho=1000.0, latent_j_kg=250e3, t_freeze_c=-1.0, t_medium_c=19.0, thickness_m=0.02,
                       h_w_m2k=20.0, k_unfrozen_w_mk=0.5)
    assert t == pytest.approx(1000 * 250e3 / 20.0 * (0.5 * 0.02 / 20.0 + 0.125 * 0.02 ** 2 / 0.5), rel=1e-9)
    with pytest.raises(ValueError):
        ND.thaw_time_s(rho=1000.0, latent_j_kg=250e3, t_freeze_c=-1.0, t_medium_c=-1.0, thickness_m=0.02,
                       h_w_m2k=20.0, k_unfrozen_w_mk=0.5)


# ------------------------------------------------------------------------------------------------ Fickian series
def test_fickian_uptake_against_the_known_series_values():
    # tau = D t / L^2.  Exact mean uptake of a plane sheet (Crank): 1 - sum 8/((2n+1)^2 pi^2) exp(-(2n+1)^2 pi^2 tau/4)
    def exact(tau):
        return 1 - sum(8 / ((2 * n + 1) ** 2 * math.pi ** 2) * math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 * tau / 4)
                       for n in range(400))

    for tau in (0.01, 0.1, 0.5, 1.0, 2.0):
        got = PD.slab_uptake_fraction(d_m2_s=1e-10, half_thickness_m=0.005, time_s=tau * 0.005 ** 2 / 1e-10)
        assert got == pytest.approx(exact(tau), abs=2e-4), tau
    assert exact(1.0) == pytest.approx(0.9313, abs=2e-4)  # hand value: 1 - (8/pi^2) exp(-pi^2/4)
    # short-time law 2 sqrt(tau/pi) holds to < 0.3 percent at tau = 0.1
    assert PD.slab_uptake_fraction(d_m2_s=1e-10, half_thickness_m=0.005, time_s=0.1 * 0.005 ** 2 / 1e-10) == \
        pytest.approx(2 * math.sqrt(0.1 / math.pi), rel=3e-3)


def test_fickian_uptake_is_monotone_and_bounded():
    vals = [PD.slab_uptake_fraction(d_m2_s=1e-10, half_thickness_m=0.004, time_s=t) for t in (0, 60, 600, 6e3, 6e4, 6e6)]
    assert vals == sorted(vals) and vals[0] == 0.0 and vals[-1] == pytest.approx(1.0, abs=1e-9)


# ------------------------------------------------------------------------------------------------ drying
DRY = dict(h_w_m2k=50.0, t_air_c=60.0, t_wet_bulb_c=32.0, latent_j_kg=2.36e6, rho_kg_m3=1050.0, half_thickness_m=0.003,
           x0_db=6.0, xc_db=2.5, xe_db=0.1)


def test_drying_constant_rate_period_is_linear_and_ends_at_the_critical_moisture():
    n_c = 50.0 * 28.0 / 2.36e6
    m_s = 1050.0 * 0.003 / 7.0
    t_c_min = m_s * (6.0 - 2.5) / n_c / 60.0
    r = ND.drying_state(t_min=0.5 * t_c_min, **DRY)
    assert r["time_class"] == "CONSTANT_RATE_ONLY"
    assert r["x_end_db"] == pytest.approx(6.0 - n_c * 0.5 * t_c_min * 60.0 / m_s, rel=1e-9)
    end = ND.drying_state(t_min=t_c_min, **DRY)
    assert end["x_end_db"] == pytest.approx(2.5, rel=1e-9) and end["constant_rate_end_min"] == pytest.approx(t_c_min)
    after = ND.drying_state(t_min=t_c_min + 1e-6, **DRY)  # continuous across the break
    assert after["x_end_db"] == pytest.approx(2.5, abs=1e-4)


def test_drying_falling_rate_is_exponential_and_tends_to_equilibrium():
    r0 = ND.drying_state(t_min=1.0, **DRY)
    tc, tau = r0["constant_rate_end_min"], r0["falling_rate_tau_min"]
    r = ND.drying_state(t_min=tc + tau, **DRY)
    assert r["time_class"] == "FALLING_RATE_REACHED"
    assert r["x_end_db"] == pytest.approx(0.1 + (2.5 - 0.1) * math.exp(-1.0), rel=1e-9)
    assert ND.drying_state(t_min=tc + 40 * tau, **DRY)["x_end_db"] == pytest.approx(0.1, abs=1e-9)
    xs = [ND.drying_state(t_min=t, **DRY)["x_end_db"] for t in (10, 60, 120, 240, 480, 960)]
    assert xs == sorted(xs, reverse=True)


def test_drying_inputs_validated():
    with pytest.raises(ValueError):
        ND.drying_state(t_min=10.0, **{**DRY, "t_air_c": 30.0})
    with pytest.raises(ValueError):
        ND.drying_state(t_min=10.0, **{**DRY, "xe_db": 7.0})


# ------------------------------------------------------------------------------------------------ F0, geometry
def test_f0_convention():
    assert ND.f0_minutes(minutes=10.0, t_c=121.1, t_ref_c=121.1, z_c=10.0) == pytest.approx(10.0)
    assert ND.f0_minutes(minutes=10.0, t_c=111.1, t_ref_c=121.1, z_c=10.0) == pytest.approx(1.0)
    assert ND.f0_minutes(minutes=1.0, t_c=131.1, t_ref_c=121.1, z_c=10.0) == pytest.approx(10.0)


def test_surface_to_volume():
    assert ND.slab_av(0.005) == pytest.approx(200.0)
    assert ND.cube_av(0.005) == pytest.approx(600.0)  # cube of side 1 cm: 6 / 0.01
    with pytest.raises(ValueError):
        ND.slab_av(0.0)
