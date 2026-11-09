"""S172 / D-077: physics drivers θ(t) (SSOT §141) — slab conduction series and equivalent-time thermal dose."""
from __future__ import annotations

import math

import pytest

from culinarystate.simulation import physics_drivers as PD


def test_slab_eigenvalues_satisfy_the_characteristic_equation():
    for bi in (0.1, 1.0, 10.0, 100.0):
        for z in PD.slab_eigenvalues(bi, 5):
            assert z * math.tan(z) == pytest.approx(bi, rel=1e-9)


def test_center_temperature_limits_and_known_value():
    assert PD.slab_center_theta(fo=0.0, bi=1e6) == pytest.approx(1.0, abs=1e-3)
    assert PD.slab_center_theta(fo=10.0, bi=1e6) == pytest.approx(0.0, abs=1e-6)
    # Bi -> infinity, Fo = 0.5: first term (4/pi) exp(-(pi/2)^2 * 0.5) dominates
    assert PD.slab_center_theta(fo=0.5, bi=1e6) == pytest.approx(4 / math.pi * math.exp(-(math.pi / 2) ** 2 * 0.5),
                                                                 rel=2e-3)


def test_core_temperature_moves_from_start_to_bath():
    t = PD.core_temperature(t0_c=20.0, bath_c=100.0, time_s=0.0, half_thickness_m=0.005, alpha_m2_s=1.4e-7,
                            h_w_m2k=1000.0, k_w_mk=0.5)
    assert t == pytest.approx(20.0, abs=0.5)
    t_late = PD.core_temperature(t0_c=20.0, bath_c=100.0, time_s=3600.0, half_thickness_m=0.005,
                                 alpha_m2_s=1.4e-7, h_w_m2k=1000.0, k_w_mk=0.5)
    assert 99.0 < t_late <= 100.0


def test_equivalent_time_definitions():
    assert PD.equivalent_minutes([(10.0, 100.0)], t_ref_c=100.0, z_c=33.0) == pytest.approx(10.0)
    assert PD.equivalent_minutes([(10.0, 133.0)], t_ref_c=100.0, z_c=33.0) == pytest.approx(100.0)
    assert PD.equivalent_minutes([(5.0, 90.0), (5.0, 110.0)], t_ref_c=100.0, z_c=10.0) == pytest.approx(5.0 * 0.1 + 50.0)


def test_core_trajectory_and_time_above():
    traj = PD.core_trajectory(t0_c=20.0, bath_c=100.0, duration_min=20.0, half_thickness_m=0.005, alpha_m2_s=1.4e-7,
                              h_w_m2k=1000.0, k_w_mk=0.5, steps=40)
    assert len(traj) == 41 and traj[0][1] == pytest.approx(20.0, abs=0.5) and traj[-1][1] > 95
    assert all(b[1] >= a[1] - 1e-9 for a, b in zip(traj, traj[1:]))
    assert 0 < PD.minutes_above(traj, 70.0) < 20.0


def test_inputs_validated():
    with pytest.raises(ValueError):
        PD.core_temperature(t0_c=20.0, bath_c=100.0, time_s=-1.0, half_thickness_m=0.005, alpha_m2_s=1.4e-7,
                            h_w_m2k=1000.0, k_w_mk=0.5)
    with pytest.raises(ValueError):
        PD.slab_eigenvalues(0.0, 3)


def test_cooling_reuses_conduction_with_cold_bath():
    t = PD.core_temperature(t0_c=90.0, bath_c=4.0, time_s=4 * 3600.0, half_thickness_m=0.01, alpha_m2_s=1.4e-7,
                            h_w_m2k=15.0, k_w_mk=0.5)
    assert 4.0 <= t < 90.0


def test_slab_uptake_fraction_limits_and_known_value():
    assert PD.slab_uptake_fraction(d_m2_s=1e-9, half_thickness_m=0.005, time_s=0.0) == 0.0
    assert PD.slab_uptake_fraction(d_m2_s=1e-9, half_thickness_m=0.005, time_s=1e9) == pytest.approx(1.0, abs=1e-6)
    # short time: M/M_inf ~ 2 sqrt(D t / (pi L^2))
    f = PD.slab_uptake_fraction(d_m2_s=1e-9, half_thickness_m=0.005, time_s=600.0)
    assert f == pytest.approx(2 * math.sqrt(1e-9 * 600 / (math.pi * 0.005 ** 2)), rel=0.02)


def test_plank_freezing_time():
    # t = (rho L_f / (T_f - T_a)) * (P a / h + R a^2 / k), slab P = 1/2, R = 1/8, a = full thickness
    t = PD.plank_freezing_time_s(rho=1000.0, latent_j_kg=250e3, t_freeze_c=-1.0, t_air_c=-20.0, thickness_m=0.02,
                                 h_w_m2k=20.0, k_frozen_w_mk=1.5)
    expect = (1000 * 250e3 / 19.0) * (0.5 * 0.02 / 20.0 + 0.125 * 0.02 ** 2 / 1.5)
    assert t == pytest.approx(expect)
    with pytest.raises(ValueError):
        PD.plank_freezing_time_s(rho=1000.0, latent_j_kg=250e3, t_freeze_c=-1.0, t_air_c=0.0, thickness_m=0.02,
                                 h_w_m2k=20.0, k_frozen_w_mk=1.5)
