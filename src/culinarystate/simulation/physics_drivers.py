"""Physics drivers θ(t) for the physical-state dataset (S172, D-077; SSOT §141). MODEL_DERIVED, never evidence.

Textbook transient conduction in an infinite slab of half-thickness L with a convective boundary (bath temperature
T_b, coefficient h), uniform start T_0, constant properties (k, α): the dimensionless centre temperature is the
eigenfunction series θ(0, Fo) = Σ C_n exp(-ζ_n² Fo), C_n = 4 sin ζ_n / (2ζ_n + sin 2ζ_n), with ζ_n tan ζ_n = Bi,
Bi = hL/k, Fo = αt/L². The slab bounds faster-heating shapes (cylinder, sphere) from the slow side; every value
here is a function of caller inputs, and the inputs (h, k, α, L, T_0) are scenario values with registry ids.
Thermal dose: equivalent minutes at T_ref, ∫ 10^((T - T_ref)/z) dt (z = 10 °C for the F-value convention,
z = 33 °C for the cook-value convention), on a piecewise-constant temperature history.
"""
from __future__ import annotations

import math
from typing import Sequence

N_TERMS = 60
FO_FRONT = 0.02


def slab_eigenvalues(bi: float, n: int) -> list[float]:
    """First n roots of ζ tan ζ = Bi (one per interval ((k-1)π, (k-1)π + π/2)), by bisection."""
    if not bi > 0 or n < 1:
        raise ValueError("Bi must be positive and n >= 1")
    out = []
    for k in range(n):
        lo, hi = k * math.pi + 1e-12, k * math.pi + math.pi / 2 - 1e-12
        f = lambda z: z * math.tan(z) - bi  # noqa: E731
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                hi = mid
            else:
                lo = mid
        out.append(0.5 * (lo + hi))
    return out


def slab_center_theta(*, fo: float, bi: float, n_terms: int = N_TERMS) -> float:
    if fo < 0:
        raise ValueError("Fo must be >= 0")
    if fo < FO_FRONT:  # heat front has not reached the centre: semi-infinite bound erfc(1/(2 sqrt Fo)) < 1e-6
        return 1.0
    s = 0.0
    for z in slab_eigenvalues(bi, n_terms):
        s += 4 * math.sin(z) / (2 * z + math.sin(2 * z)) * math.exp(-z * z * fo)
    return min(1.0, max(0.0, s))


def core_temperature(*, t0_c: float, bath_c: float, time_s: float, half_thickness_m: float, alpha_m2_s: float,
                     h_w_m2k: float, k_w_mk: float) -> float:
    for name, v in (("half_thickness_m", half_thickness_m), ("alpha_m2_s", alpha_m2_s), ("h_w_m2k", h_w_m2k),
                    ("k_w_mk", k_w_mk)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    if time_s < 0:
        raise ValueError("time must be >= 0")
    fo = alpha_m2_s * time_s / half_thickness_m ** 2
    bi = h_w_m2k * half_thickness_m / k_w_mk
    return bath_c + (t0_c - bath_c) * slab_center_theta(fo=fo, bi=bi)


def core_trajectory(*, t0_c: float, bath_c: float, duration_min: float, steps: int = 60, **props) -> list[tuple]:
    """[(minute, core °C)] at steps+1 evenly spaced times over [0, duration]."""
    if duration_min <= 0 or steps < 1:
        raise ValueError("duration must be positive and steps >= 1")
    return [(duration_min * i / steps,
             core_temperature(t0_c=t0_c, bath_c=bath_c, time_s=60.0 * duration_min * i / steps, **props))
            for i in range(steps + 1)]


def minutes_above(traj: Sequence[tuple[float, float]], threshold_c: float) -> float:
    """Time the trajectory spends above threshold (trapezoid on the crossing interval)."""
    total = 0.0
    for (t1, y1), (t2, y2) in zip(traj, traj[1:]):
        if y1 >= threshold_c and y2 >= threshold_c:
            total += t2 - t1
        elif (y1 - threshold_c) * (y2 - threshold_c) < 0:
            frac = (max(y1, y2) - threshold_c) / abs(y2 - y1)
            total += (t2 - t1) * frac
    return total


def equivalent_minutes(segments: Sequence[tuple[float, float]], *, t_ref_c: float, z_c: float) -> float:
    """∫ 10^((T - T_ref)/z) dt over piecewise-constant (minutes, °C) segments."""
    if z_c <= 0:
        raise ValueError("z must be positive")
    return sum(m * 10 ** ((t - t_ref_c) / z_c) for m, t in segments)


def trajectory_dose(traj: Sequence[tuple[float, float]], *, t_ref_c: float, z_c: float) -> float:
    """Equivalent minutes for a sampled trajectory (midpoint temperature per interval)."""
    return equivalent_minutes([(t2 - t1, 0.5 * (y1 + y2)) for (t1, y1), (t2, y2) in zip(traj, traj[1:])],
                              t_ref_c=t_ref_c, z_c=z_c)


def slab_uptake_fraction(*, d_m2_s: float, half_thickness_m: float, time_s: float, n_terms: int = 200) -> float:
    """Mean fractional uptake M_t/M_inf in a slab with surface at equilibrium (Crank, Bi -> infinity):
    1 - sum 8/((2n+1)^2 pi^2) exp(-(2n+1)^2 pi^2 D t / (4 L^2)). Used for soak, marinate, brine (D-077 family 3)."""
    if not (d_m2_s > 0 and half_thickness_m > 0) or time_s < 0:
        raise ValueError("D and L must be positive and t >= 0")
    if time_s == 0:
        return 0.0
    tau = d_m2_s * time_s / half_thickness_m ** 2
    if tau < 1e-3:  # short-time limit avoids slow series convergence
        return min(1.0, 2 * math.sqrt(tau / math.pi))
    s = sum(8 / ((2 * n + 1) ** 2 * math.pi ** 2) * math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 * tau / 4)
            for n in range(n_terms))
    return min(1.0, max(0.0, 1 - s))


def plank_freezing_time_s(*, rho: float, latent_j_kg: float, t_freeze_c: float, t_air_c: float, thickness_m: float,
                          h_w_m2k: float, k_frozen_w_mk: float, p: float = 0.5, r: float = 0.125) -> float:
    """Plank's equation (slab: P = 1/2, R = 1/8; a = full thickness). D-077 family 1 (freeze)."""
    if t_air_c >= t_freeze_c:
        raise ValueError("air must be colder than the freezing point")
    for name, v in (("rho", rho), ("latent", latent_j_kg), ("thickness", thickness_m), ("h", h_w_m2k),
                    ("k", k_frozen_w_mk)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    return rho * latent_j_kg / (t_freeze_c - t_air_c) * (p * thickness_m / h_w_m2k + r * thickness_m ** 2 / k_frozen_w_mk)
