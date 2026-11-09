"""Physics drivers θ(t) for the physical-state dataset (S172, D-077; SSOT §141). MODEL_DERIVED, never evidence.

Textbook transient conduction in an infinite slab of half-thickness L with a convective boundary (bath temperature
T_b, coefficient h), uniform start T_0, constant properties (k, α): the dimensionless centre temperature is the
eigenfunction series θ(0, Fo) = Σ C_n exp(-ζ_n² Fo), C_n = 4 sin ζ_n / (2ζ_n + sin 2ζ_n), with ζ_n tan ζ_n = Bi,
Bi = hL/k, Fo = αt/L². The slab bounds faster-heating shapes (cylinder, sphere) from the slow side; every value
here is a function of caller inputs, and the inputs (h, k, α, L, T_0) are scenario values with registry ids.
Thermal dose: equivalent minutes at T_ref, ∫ 10^((T - T_ref)/z) dt (z = 10 °C for the F-value convention,
z = 33 °C for the cook-value convention), on a piecewise-constant temperature history.

S176 L-PHYS additions (the functions above keep their behaviour): the slab VOLUME-AVERAGE temperature (the zone quality
doses use, SSOT v16 DRAFT 284.4) and ``zone_trajectory``. The evaporation cap itself lives in ``phase_change``: callers pass
the capped boundary temperature min(T_medium, T_boil) as ``bath_c``, so nothing here knows about it.

S177 SCIFIX-PHYS (FINAL-SCI row 2): the zone-resolved field. ``slab_theta`` is the local dimensionless temperature at
x/L (series for Fo >= 0.02, the convective semi-infinite solution below it), ``zone_node_histories`` samples the slab at
Gauss-Legendre nodes of the half slab, and ``zone_mean_dose`` / ``zone_mean_survival`` integrate a LOCAL history per node
and average over the volume: mean_i w_i F(T_i(t)) and mean_i w_i exp(-int k(T_i) dt). Both differ from the dose of the
volume-average temperature (``trajectory_dose`` of ``zone_trajectory``), which for a convex dose rate is never larger.
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Callable, Sequence

import numpy as np

N_TERMS = 60
FO_FRONT = 0.02


@lru_cache(maxsize=16384)
def _eigenvalues(bi: float, n: int) -> tuple[float, ...]:
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
    return tuple(out)


def slab_eigenvalues(bi: float, n: int) -> list[float]:
    """First n roots of ζ tan ζ = Bi (one per interval ((k-1)π, (k-1)π + π/2)), by bisection (cached per Bi and n)."""
    if not bi > 0 or n < 1:
        raise ValueError("Bi must be positive and n >= 1")
    return list(_eigenvalues(float(bi), int(n)))


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


def _erfcx(u: float) -> float:
    """exp(u²) erfc(u) for u >= 0 (direct below 26, asymptotic series above)."""
    if u < 26.0:
        return math.exp(u * u) * math.erfc(u)
    x2 = 1.0 / (2 * u * u)
    return (1.0 - x2 + 3 * x2 ** 2 - 15 * x2 ** 3 + 105 * x2 ** 4) / (u * math.sqrt(math.pi))


def slab_mean_theta(*, fo: float, bi: float, n_terms: int = N_TERMS) -> float:
    """Dimensionless VOLUME-AVERAGE temperature θ̄ of the slab, θ = (T - T_bath)/(T_0 - T_bath).

    Fo >= FO_FRONT: θ̄ = Σ C_n (sin ζ_n / ζ_n) exp(-ζ_n² Fo) with the centre-temperature C_n (the mean of cos(ζ x) over the
    half-thickness is sin ζ / ζ). Fo < FO_FRONT (the two heat fronts have not met): the semi-infinite solid with a convective
    surface, θ̄ = 1 - (1/Bi)[exp(u²) erfc(u) - 1 + 2u/√π], u = Bi √Fo, whose integral is closed form.
    """
    if fo < 0:
        raise ValueError("Fo must be >= 0")
    if fo == 0:
        return 1.0
    if fo < FO_FRONT:
        u = bi * math.sqrt(fo)
        sp = math.sqrt(math.pi)
        g = (u * u - 4 * u ** 3 / (3 * sp) + u ** 4 / 2 - 8 * u ** 5 / (15 * sp)) if u < 1e-3 else \
            _erfcx(u) - 1.0 + 2.0 * u / sp  # the series avoids cancellation for tiny u
        return min(1.0, max(0.0, 1.0 - g / bi))
    s = 0.0
    for z in slab_eigenvalues(bi, n_terms):
        s += 4 * math.sin(z) / (2 * z + math.sin(2 * z)) * math.sin(z) / z * math.exp(-z * z * fo)
    return min(1.0, max(0.0, s))


def core_and_mean_temperature(*, t0_c: float, bath_c: float, time_s: float, half_thickness_m: float, alpha_m2_s: float,
                              h_w_m2k: float, k_w_mk: float) -> tuple[float, float]:
    """(centre °C, volume-average °C) of the slab at one time, same inputs as ``core_temperature``."""
    for name, v in (("half_thickness_m", half_thickness_m), ("alpha_m2_s", alpha_m2_s), ("h_w_m2k", h_w_m2k),
                    ("k_w_mk", k_w_mk)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    if time_s < 0:
        raise ValueError("time must be >= 0")
    fo = alpha_m2_s * time_s / half_thickness_m ** 2
    bi = h_w_m2k * half_thickness_m / k_w_mk
    d = t0_c - bath_c
    return bath_c + d * slab_center_theta(fo=fo, bi=bi), bath_c + d * slab_mean_theta(fo=fo, bi=bi)


def core_trajectory(*, t0_c: float, bath_c: float, duration_min: float, steps: int = 60, **props) -> list[tuple]:
    """[(minute, core °C)] at steps+1 evenly spaced times over [0, duration]."""
    if duration_min <= 0 or steps < 1:
        raise ValueError("duration must be positive and steps >= 1")
    return [(duration_min * i / steps,
             core_temperature(t0_c=t0_c, bath_c=bath_c, time_s=60.0 * duration_min * i / steps, **props))
            for i in range(steps + 1)]


def zone_trajectory(*, t0_c: float, bath_c: float, duration_min: float, steps: int = 60, **props) -> list[tuple]:
    """[(minute, centre °C, volume-average °C)] at steps+1 evenly spaced times over [0, duration] (S176 L-PHYS)."""
    if duration_min <= 0 or steps < 1:
        raise ValueError("duration must be positive and steps >= 1")
    out = []
    for i in range(steps + 1):
        m = duration_min * i / steps
        c, a = core_and_mean_temperature(t0_c=t0_c, bath_c=bath_c, time_s=60.0 * m, **props)
        out.append((m, c, a))
    return out


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


# ---------------------------------------------------------------------------------------------------- S177 zone field
N_ZONE_NODES = 8
N_ZONE_TIMES = 48
ZONE_TIME_POWER = 2.0
ZONE_NODE_RANGE = (6, 8)  # FINAL-SCI row 2: "6-8 Gauss-Legendre nodes per bracket"


@lru_cache(maxsize=16)
def gauss_legendre_half_slab(n: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """(xi_i, w_i): Gauss-Legendre nodes on the half slab, xi = x/L in (0, 1) (0 = centre, 1 = surface), weights summing to 1.

    The volume mean of any f(xi) over the symmetric slab is sum_i w_i f(xi_i) (exact for polynomials of degree 2n - 1)."""
    if not 1 <= int(n) <= 64:
        raise ValueError("n must be between 1 and 64")
    x, w = np.polynomial.legendre.leggauss(int(n))
    return tuple(float(0.5 * (v + 1.0)) for v in x), tuple(float(0.5 * v) for v in w)


@lru_cache(maxsize=4096)
def _series_coefficients(bi: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    z = np.asarray(slab_eigenvalues(bi, n), dtype=float)
    return z, 4 * np.sin(z) / (2 * z + np.sin(2 * z))


def _theta_front(xi: float, fo: float, bi: float) -> float:
    """Semi-infinite solid with a convective surface, at depth (1 - xi) L from the surface (valid for Fo < FO_FRONT).

    1 - theta = erfc(a) - exp(Bi (1-xi) + Bi^2 Fo) erfc(a + u), a = (1 - xi) / (2 sqrt Fo), u = Bi sqrt Fo; the exponential is
    rewritten as exp(-a^2) erfcx(a + u), which cannot overflow."""
    a, u = (1.0 - xi) / (2.0 * math.sqrt(fo)), bi * math.sqrt(fo)
    return min(1.0, max(0.0, 1.0 - (math.erfc(a) - math.exp(-a * a) * _erfcx(a + u))))


def slab_theta(xi: float, *, fo: float, bi: float, n_terms: int = N_TERMS) -> float:
    """Local dimensionless temperature theta = (T - T_bath)/(T_0 - T_bath) of the infinite slab at x/L = xi.

    Fo >= FO_FRONT: sum C_n cos(zeta_n xi) exp(-zeta_n^2 Fo); xi = 0 is ``slab_center_theta`` and xi = 1 is the surface.
    Fo < FO_FRONT (the two heat fronts have not met): the convective semi-infinite solution (``_theta_front``)."""
    if fo < 0:
        raise ValueError("Fo must be >= 0")
    if not 0.0 <= xi <= 1.0:
        raise ValueError("xi = x/L must be in [0, 1]")
    if fo == 0:
        return 1.0
    if fo < FO_FRONT:
        return _theta_front(xi, fo, bi)
    z, c = _series_coefficients(float(bi), int(n_terms))
    return min(1.0, max(0.0, float(np.sum(c * np.cos(z * xi) * np.exp(-z * z * fo)))))


def zone_time_grid(duration_min: float, *, n_times: int = N_ZONE_TIMES, power: float = ZONE_TIME_POWER) -> list[float]:
    """Minutes 0 = t_0 < ... < t_n = duration, t_j = D (j/n)^power: fine steps early, where a node next to the surface moves
    within seconds, and coarse steps late. The grid is stored with the histories, so any reader integrates on it."""
    if not duration_min > 0 or n_times < 1 or not power >= 1.0:
        raise ValueError("duration must be positive, n_times >= 1 and power >= 1")
    return [duration_min * (j / n_times) ** power for j in range(n_times + 1)]


def zone_node_histories(*, t0_c: float, bath_c: float, duration_min: float, half_thickness_m: float, alpha_m2_s: float,
                        h_w_m2k: float, k_w_mk: float, n_nodes: int = N_ZONE_NODES, n_times: int = N_ZONE_TIMES,
                        power: float = ZONE_TIME_POWER) -> dict:
    """Temperature histories (deg C) of the slab at the Gauss-Legendre nodes of the half slab.

    Returns {"xi": [...], "weights": [...], "times_min": [...], "temps_c": [[...per time...] per node]}. Same inputs as
    ``core_temperature``; the boundary temperature ``bath_c`` is whatever the caller passes (the capped boundary in L2)."""
    for name, v in (("half_thickness_m", half_thickness_m), ("alpha_m2_s", alpha_m2_s), ("h_w_m2k", h_w_m2k),
                    ("k_w_mk", k_w_mk)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    xi, w = gauss_legendre_half_slab(n_nodes)
    times = zone_time_grid(duration_min, n_times=n_times, power=power)
    bi = h_w_m2k * half_thickness_m / k_w_mk
    fos = [alpha_m2_s * 60.0 * t / half_thickness_m ** 2 for t in times]
    d = t0_c - bath_c
    theta = np.empty((len(xi), len(times)))
    series = [j for j, fo in enumerate(fos) if fo >= FO_FRONT]
    if series:
        z, c = _series_coefficients(float(bi), N_TERMS)
        decay = np.exp(-np.outer(z * z, np.asarray([fos[j] for j in series])))  # (terms, times)
        for i, x in enumerate(xi):
            theta[i, series] = np.clip((c * np.cos(z * x)) @ decay, 0.0, 1.0)
    for j, fo in enumerate(fos):
        if fo < FO_FRONT:
            for i, x in enumerate(xi):
                theta[i, j] = 1.0 if fo == 0 else _theta_front(x, fo, bi)
    return {"xi": list(xi), "weights": list(w), "times_min": times,
            "temps_c": [[float(bath_c + d * theta[i, j]) for j in range(len(times))] for i in range(len(xi))]}


def _trapz(times: Sequence[float], values: Sequence[float]) -> float:
    return sum(0.5 * (values[j] + values[j + 1]) * (times[j + 1] - times[j]) for j in range(len(times) - 1))


def local_dose(times_min: Sequence[float], temps_c: Sequence[float], *, t_ref_c: float, z_c: float) -> float:
    """Equivalent minutes int 10^((T - T_ref)/z) dt of ONE local history (trapezoid on the dose RATE, not on T)."""
    if z_c <= 0:
        raise ValueError("z must be positive")
    return _trapz(times_min, [10 ** ((t - t_ref_c) / z_c) for t in temps_c])


def node_doses(hist: dict, *, t_ref_c: float, z_c: float) -> list[float]:
    return [local_dose(hist["times_min"], row, t_ref_c=t_ref_c, z_c=z_c) for row in hist["temps_c"]]


def zone_mean_dose(hist: dict, *, t_ref_c: float, z_c: float) -> float:
    """VOLUME MEAN of the local dose: sum_i w_i F_i (not the dose of the volume-average temperature)."""
    return sum(w * f for w, f in zip(hist["weights"], node_doses(hist, t_ref_c=t_ref_c, z_c=z_c)))


def zone_mean_survival(hist: dict, rate_per_min: Callable[[float], float]) -> float:
    """VOLUME MEAN of the local survival, sum_i w_i exp(-int k(T_i(t)) dt), for any first-order rate k(T) (per minute) a
    later kinetic model supplies (its own Ea / z). Trapezoid on the rate; mass-average retention of a zone-resolved piece."""
    out = 0.0
    for w, row in zip(hist["weights"], hist["temps_c"]):
        out += w * math.exp(-_trapz(hist["times_min"], [rate_per_min(t) for t in row]))
    return out


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
