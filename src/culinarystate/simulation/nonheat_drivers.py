"""Physics drivers for the non-heat process families (S176 L-NH, D-077 extension). MODEL_DERIVED, never evidence.

Extends ``physics_drivers`` (which stays untouched and is reused for the slab series, Fickian uptake and Plank
freezing) with the few drivers it lacks:

- ``thaw_time_s``: Plank's equation run in reverse (thawed-layer conductivity, medium warmer than the freezing point).
- ``slab_two_stage``: 1-D finite-difference slab (Crank-Nicolson, symmetric centre, Robin surface) with a piecewise
  constant ambient and film coefficient. Used for carry-over resting, where the initial profile is not uniform. It is
  checked against the analytic series in ``physics_drivers`` (tests).
- ``drying_state``: constant-rate period then a linear falling-rate period (textbook two-stage drying) on a slab
  that dries from both faces.
- ``f0_minutes``: thermal-lethality equivalent minutes with the F0 convention (T_ref and z passed in).
- ``slab_av`` / ``cube_av``: surface-to-volume ratio from a characteristic half-thickness.

S176 L-PHYS: ``slab_two_stage`` is now exact in time (modal solution of the same finite-difference system), so a very long
thin stage costs one eigen-decomposition instead of up to 1e8 steps; the Crank-Nicolson stepper is kept as ``method="cn"``
for the equality tests. It also accepts an evaporation cap per stage (``caps``) and returns the volume-average temperature.

No function holds a default value; every constant is a caller argument that traces to a registry row. Outputs are
temperatures, times and dimensionless fractions: no nutrient or compound quantity can come out of this module (SSOT §141).
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Sequence

import numpy as np

from culinarystate.simulation import physics_drivers as PD


def thaw_time_s(*, rho: float, latent_j_kg: float, t_freeze_c: float, t_medium_c: float, thickness_m: float,
                h_w_m2k: float, k_unfrozen_w_mk: float, p: float = 0.5, r: float = 0.125) -> float:
    """Plank's equation for thawing (slab): the mirror image of freezing with the unfrozen conductivity.

    t = rho L / (T_medium - T_freeze) * (P a / h + R a^2 / k_unfrozen). Initial temperature is taken as the freezing
    point (sub-cooling of the frozen core is not included, so the time is a lower bound for a deeply frozen piece).
    """
    if t_medium_c <= t_freeze_c:
        raise ValueError("medium must be warmer than the freezing point")
    return PD.plank_freezing_time_s(rho=rho, latent_j_kg=latent_j_kg, t_freeze_c=-t_freeze_c, t_air_c=-t_medium_c,
                                    thickness_m=thickness_m, h_w_m2k=h_w_m2k, k_frozen_w_mk=k_unfrozen_w_mk, p=p, r=r)


def _slab_operator(n: int, dx: float, alpha: float, h_over_k: float) -> tuple[np.ndarray, np.ndarray]:
    """A (n+1)x(n+1) matrix and b (per K of ambient) such that dT/dt = A T + b T_inf. Node 0 = centre, node n = surface."""
    a = np.zeros((n + 1, n + 1))
    c = alpha / dx ** 2
    a[0, 0], a[0, 1] = -2 * c, 2 * c
    for i in range(1, n):
        a[i, i - 1], a[i, i], a[i, i + 1] = c, -2 * c, c
    a[n, n - 1], a[n, n] = 2 * c, -2 * c - 2 * alpha * h_over_k / dx
    b = np.zeros(n + 1)
    b[n] = 2 * alpha * h_over_k / dx
    return a, b


@lru_cache(maxsize=1024)
def _slab_modes(n: int, dx: float, alpha: float, h_over_k: float):
    """Modal form of dT/dt = A T + b T_inf. With trapezoid weights w (half weight at both ends) D A is symmetric, so
    A_s = D^1/2 A D^-1/2 is symmetric: eigh gives real decay rates and an orthogonal basis (no ill-conditioning)."""
    a, _ = _slab_operator(n, dx, alpha, h_over_k)
    w = np.ones(n + 1)
    w[0] = w[n] = 0.5
    sq = np.sqrt(w)
    a_sym = (sq[:, None] * a) / sq[None, :]
    lam, q = np.linalg.eigh(0.5 * (a_sym + a_sym.T))
    return lam, q.T * sq[None, :], q / sq[:, None], w / w.sum()


def _peak_centre(coef: np.ndarray, lam: np.ndarray, amb: float, total_s: float) -> float:
    """Maximum over [0, total_s] of amb + sum_k coef_k exp(lam_k t): geometric grid over the modal time scales, then a
    golden-section refinement around the best grid time."""
    rate = -lam
    tau_min, tau_max = 1.0 / rate.max(), 1.0 / rate.min()
    t_hi = min(total_s, 60.0 * tau_max)  # beyond this every mode has decayed below 1e-26
    lo = tau_min / 8.0
    ts = np.unique(np.concatenate(([0.0, t_hi, total_s], np.geomspace(lo, t_hi, 400) if t_hi > lo else [])))

    def f(t):
        return amb + float(coef @ np.exp(lam * t))

    vals = amb + np.exp(np.outer(ts, lam)) @ coef
    j = int(np.argmax(vals))
    best = float(vals[j])
    a, b = float(ts[max(j - 1, 0)]), float(ts[min(j + 1, len(ts) - 1)])
    g = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(60):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    return max(best, fc, fd)


def slab_two_stage(*, t0_c: float, stages: Sequence[tuple[float, float, float]], half_thickness_m: float,
                   alpha_m2_s: float, k_w_mk: float, n: int = 30, fo_step: float = 0.004, method: str = "exact",
                   caps: Sequence[float | None] | None = None) -> dict:
    """Finite-difference slab history. ``stages`` = [(duration_min, ambient_c, h_w_m2k), ...] applied in order.

    Returns per stage the centre, surface and volume-average temperature at the stage end, and for the LAST stage the
    centre peak. ``method="exact"`` (default): the exact-in-time solution of the n-node finite-difference system, cost
    independent of the stage length; the peak is a grid search plus golden-section refinement. ``method="cn"``: the
    earlier Crank-Nicolson stepper (Fourier number ``fo_step`` per step, at least 20 steps per stage), kept as the
    reference; it needs about alpha t / (L^2 fo_step) steps and is not usable for very long thin stages.

    ``caps`` (S176 L-PHYS, evaporation cap): one value per stage or None. Stage i then uses the ambient min(ambient, cap_i)
    and the profile entering the stage is clipped to cap_i (a moist piece cannot hold more than T_boil at that pressure; the
    clip is how a pressure stage hands over to an atmospheric one). ``clamped_at_start`` reports whether it acted.
    """
    for name, v in (("half_thickness_m", half_thickness_m), ("alpha_m2_s", alpha_m2_s), ("k_w_mk", k_w_mk)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    if not stages or any(not (d > 0 and h > 0) for d, _, h in stages):
        raise ValueError("every stage needs a positive duration and film coefficient")
    if method not in ("exact", "cn"):
        raise ValueError("method must be 'exact' or 'cn'")
    if caps is not None and len(caps) != len(stages):
        raise ValueError("caps needs one entry per stage")
    dx = half_thickness_m / n
    temp = np.full(n + 1, float(t0_c))
    ends, peak, eye = [], float(t0_c), np.eye(n + 1)
    wavg = np.full(n + 1, 1.0 / n)
    wavg[0] = wavg[n] = 0.5 / n
    for si, (dur_min, amb, h) in enumerate(stages):
        total = 60.0 * dur_min
        last = si == len(stages) - 1
        cap = None if caps is None else caps[si]
        clamped = False
        if cap is not None:
            clamped = bool(temp.max() > cap)
            temp = np.minimum(temp, cap)
            amb = min(amb, cap)
        if method == "exact":
            lam, to_modal, from_modal, wavg = _slab_modes(n, dx, alpha_m2_s, h / k_w_mk)
            y = to_modal @ (temp - amb)
            if last and len(stages) > 1:
                peak = max(peak, _peak_centre(from_modal[0] * y, lam, amb, total))
            temp = amb + from_modal @ (y * np.exp(lam * total))
        else:
            steps = max(20, math.ceil(alpha_m2_s * total / half_thickness_m ** 2 / fo_step))
            dt = total / steps
            a, b = _slab_operator(n, dx, alpha_m2_s, h / k_w_mk)
            lhs_inv = np.linalg.inv(eye - 0.5 * dt * a)
            rhs = eye + 0.5 * dt * a
            src = dt * b * amb
            for _ in range(steps):
                temp = lhs_inv @ (rhs @ temp + src)
                if last:
                    peak = max(peak, float(temp[0]))
        ends.append({"centre_c": float(temp[0]), "surface_c": float(temp[n]), "volume_avg_c": float(wavg @ temp),
                     "clamped_at_start": clamped})
    return {"stage_end": ends, "centre_peak_last_stage_c": peak if len(stages) > 1 else None, "method": method}


def drying_state(*, t_min: float, h_w_m2k: float, t_air_c: float, t_wet_bulb_c: float, latent_j_kg: float,
                 rho_kg_m3: float, half_thickness_m: float, x0_db: float, xc_db: float, xe_db: float) -> dict:
    """Two-stage drying of a slab drying from both faces (per face: half-thickness L of wet material).

    Constant rate N_c = h (T_air - T_wb) / lambda [kg/m2/s]; dry solids per face area M_s = rho L / (1 + X0).
    Constant-rate period ends at t_c = M_s (X0 - X_c) / N_c; afterwards N = N_c (X - X_e)/(X_c - X_e), so
    X = X_e + (X_c - X_e) exp(-(t - t_c)/tau_f) with tau_f = M_s (X_c - X_e) / N_c. Moisture ratio MR = (X - X_e)/(X0 - X_e).
    Water contents are dry basis (kg water per kg dry solids): drying-state variables, not nutrient values.
    """
    for name, v in (("h", h_w_m2k), ("latent", latent_j_kg), ("rho", rho_kg_m3), ("L", half_thickness_m)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    if not t_air_c > t_wet_bulb_c:
        raise ValueError("air must be warmer than the wet-bulb temperature")
    if not (x0_db > xe_db >= 0) or t_min < 0 or xc_db <= xe_db:
        raise ValueError("need X0 > Xe >= 0, Xc > Xe and t >= 0")
    n_c = h_w_m2k * (t_air_c - t_wet_bulb_c) / latent_j_kg
    m_s = rho_kg_m3 * half_thickness_m / (1.0 + x0_db)
    xc = min(xc_db, x0_db)
    t_c = m_s * (x0_db - xc) / n_c
    tau_f = m_s * (xc - xe_db) / n_c
    t = 60.0 * t_min
    x = x0_db - n_c * t / m_s if t <= t_c else xe_db + (xc - xe_db) * math.exp(-(t - t_c) / tau_f)
    x = max(x, xe_db)
    return {"constant_rate_end_min": t_c / 60.0, "falling_rate_tau_min": tau_f / 60.0, "x_end_db": x,
            "moisture_ratio": (x - xe_db) / (x0_db - xe_db),
            "time_class": "CONSTANT_RATE_ONLY" if t <= t_c else "FALLING_RATE_REACHED"}


def f0_minutes(*, minutes: float, t_c: float, t_ref_c: float, z_c: float) -> float:
    """Equivalent minutes at T_ref for a constant temperature (F0 convention: z and T_ref come from the registry)."""
    return PD.equivalent_minutes([(minutes, t_c)], t_ref_c=t_ref_c, z_c=z_c)


def slab_av(half_thickness_m: float) -> float:
    """Surface/volume of an infinite slab of half-thickness L: 2A / (2 L A) = 1/L."""
    if not half_thickness_m > 0:
        raise ValueError("half-thickness must be positive")
    return 1.0 / half_thickness_m


def cube_av(half_thickness_m: float) -> float:
    """Surface/volume of a cube of half-side L: 6 (2L)^2 / (2L)^3 = 3/L."""
    return 3.0 * slab_av(half_thickness_m)
