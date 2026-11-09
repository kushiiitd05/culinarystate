"""Verification pack for the physical-layer drivers (S178 PHYS2, T4-C07-R1). DRAFT, AI_DRAFTED. Not a validation against food.

The drivers of ``physics_drivers`` (slab series, local temperature, Plank, Fickian slab) and ``nonheat_drivers`` (the exact modal
stepper) are compared with independent references that do not use their code paths:

- analytic limits: lumped (Bi -> 0), Dirichlet (Bi -> infinity), convective semi-infinite solid at short times, the one-term series
  (the curve behind the Heisler charts) at Fo >= 0.2, short- and long-time Fickian limits;
- a finite-difference solve (Crank-Nicolson with Rannacher start, dense solve, 200 nodes) of the same slab problem;
- the exact modal stepper of ``nonheat_drivers.slab_two_stage`` (exact in time for its n-node system) against the series, with a
  convergence study in n, against the analytic superposition for a two-stage ambient change and against its Crank-Nicolson mode;
- the N_TERMS convergence of the series;
- Plank's equation against an independent integration of the quasi-steady front ODE and against an enthalpy-method Stefan solve at
  decreasing Stefan number (Plank is the Ste -> 0 limit);
- textbook constants (plane-wall first-term eigenvalue zeta_1 and coefficient C_1 versus Bi; the slab half-uptake time). These constants
  are recalled by the agent from the heat-transfer textbook tables and are tagged SOURCE_UNVERIFIED_AGENT_RECALLED: they are compared at the
  4-decimal precision of the tables and are not treated as a source.

Each check returns {id, what, reference, n_cases, max_abs_error, max_rel_error, tolerance, passed, independence}; ``run_all`` returns
the list. Relative error is |a - b| / max(|b|, floor) with the floor named in each check. Nothing here holds a food value.

S178 FIX-PHYS (version 1.1.0, SCI-A m7 / m9):
- every check carries an ``independence`` class (INDEPENDENT: a reference that shares no code path or formula with the driver;
  IDENTITY: the same closed form or the same ODE in another form; SELF_CONSISTENCY: the driver against itself (more terms, its own
  operator); LOOSE_TOLERANCE: a tolerance wide enough that a wrong trend could pass; RECALLED_CONSTANTS: depends on agent-recalled
  table values). The report counts them separately, so "N of N pass" is never read as N independent checks.
- V14 passes only if the Plank error also falls with the Stefan number (``error_decreases_with_stefan_number``).
- V16: the short-time (Fo < 0.02) front solution of the local theta against a fine finite-difference solve at Fo 0.002 and 0.01,
  xi 0.5 and 0.9 (the front was compared with the FD solve only indirectly before).
- V17: the 8-node, 48-time zone-mean dose of the layer against a dense reference (24 Gauss-Legendre nodes, 1,200 uniform times).
- V18 (m9): the numerical bias of the two dose rules of the layer, measured against the same dense reference: the trapezoid on the
  graded node grid (zone mean) and the midpoint temperature on a uniform 40-step grid (dose at the volume-average temperature).
- V13 wording: with identical k and dT the thaw formula reduces to Plank's form (it is not an independent mirror check).
"""
from __future__ import annotations

import functools
import math
from typing import Callable

import numpy as np

from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import physics_drivers as PD

VERSION = "phys-verification-1.1.0-draft"
VERSION_V10 = "phys-verification-1.0.0-draft"  # SUPERSEDED: no independence classes, V14 not gated on the Stefan trend
INDEPENDENCE = {"V01": "INDEPENDENT", "V02": "INDEPENDENT", "V03": "IDENTITY", "V04": "INDEPENDENT", "V05": "RECALLED_CONSTANTS",
                "V06": "LOOSE_TOLERANCE", "V07": "INDEPENDENT", "V08": "INDEPENDENT", "V09": "INDEPENDENT", "V10": "INDEPENDENT",
                "V11": "SELF_CONSISTENCY", "V12": "SELF_CONSISTENCY", "V13": "IDENTITY", "V14": "LOOSE_TOLERANCE", "V15": "INDEPENDENT",
                "V16": "INDEPENDENT", "V17": "INDEPENDENT", "V18": "INDEPENDENT"}
INDEPENDENCE_CLASSES = ("INDEPENDENT", "IDENTITY", "SELF_CONSISTENCY", "LOOSE_TOLERANCE", "RECALLED_CONSTANTS")
RECALLED = "SOURCE_UNVERIFIED_AGENT_RECALLED"

# plane-wall first-term constants (zeta_1 [rad], C_1) versus Bi: Incropera & DeWitt-type table, recalled, 4 decimals
TEXTBOOK_PLANE_WALL = {0.01: (0.0998, 1.0017), 0.02: (0.1410, 1.0033), 0.05: (0.2218, 1.0082), 0.1: (0.3111, 1.0161),
                       0.2: (0.4328, 1.0311), 0.5: (0.6533, 1.0701), 1.0: (0.8603, 1.1191), 2.0: (1.0769, 1.1785),
                       5.0: (1.3138, 1.2403), 10.0: (1.4289, 1.2620), 20.0: (1.4961, 1.2699), 50.0: (1.5400, 1.2727),
                       100.0: (1.5552, 1.2731)}
TEXTBOOK_BI_INFINITY = (math.pi / 2, 4 / math.pi)  # exact, not recalled
SLAB_HALF_UPTAKE_TAU = 4 * 0.04919  # D t / L^2 at M_t/M_inf = 1/2 for a slab of half-thickness L (Crank: t_1/2 = 0.04919 l^2 / D, l = 2L), recalled


def _res(cid: str, what: str, ref: str, errs_abs: list[float], errs_rel: list[float], tol: float, tol_kind: str = "rel",
         **extra) -> dict:
    ma, mr = (max(errs_abs) if errs_abs else 0.0), (max(errs_rel) if errs_rel else 0.0)
    val = mr if tol_kind == "rel" else ma
    gate = extra.pop("_gate", True)
    return {"id": cid, "what": what, "reference": ref, "n_cases": len(errs_abs), "max_abs_error": ma, "max_rel_error": mr,
            "tolerance": tol, "tolerance_on": tol_kind, "passed": bool(val <= tol and gate),
            "independence": INDEPENDENCE.get(cid, "UNCLASSIFIED"), **extra}


def _rel(a: float, b: float, floor: float = 1e-12) -> float:
    return abs(a - b) / max(abs(b), floor)


# ------------------------------------------------------------------------------------------------ independent references
def theta_lumped(bi: float, fo: float) -> float:
    return math.exp(-bi * fo)


def theta_center_dirichlet(fo: float, terms: int = 400) -> float:
    return 4 / math.pi * sum((-1) ** n / (2 * n + 1) * math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 * fo / 4) for n in range(terms))


def theta_mean_dirichlet(fo: float, terms: int = 400) -> float:
    return 8 / math.pi ** 2 * sum(math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 * fo / 4) / (2 * n + 1) ** 2 for n in range(terms))


def theta_surface_semi_infinite(bi: float, fo: float) -> float:
    u = bi * math.sqrt(fo)
    if u > 20:
        raise ValueError("direct evaluation of exp(u^2) erfc(u) is limited to u <= 20")
    return math.exp(u * u) * math.erfc(u)


def one_term(xi: float, fo: float, zeta1: float, c1: float) -> float:
    return c1 * math.cos(zeta1 * xi) * math.exp(-zeta1 ** 2 * fo)


def fd_slab(bi: float, fos: list[float], n: int = 200, steps_per_unit: float = 6000.0) -> dict[float, tuple[float, float, float]]:
    """Dimensionless FD reference {Fo: (theta centre, theta surface, theta volume mean)} for the infinite slab, uniform start.

    Half slab xi in [0, 1], n intervals, ghost-node symmetric centre and Robin surface; Crank-Nicolson with four implicit-Euler
    half steps first (Rannacher) so the start-up discontinuity does not ring; dense solves of an (n+1) system. Independent of the
    eigenfunction series and of the modal stepper."""
    prof = fd_slab_profiles(bi, fos, n=n, steps_per_unit=steps_per_unit)
    dx = 1.0 / n
    w = np.full(n + 1, dx)
    w[0] = w[n] = dx / 2
    return {fo: (float(th[0]), float(th[n]), float(w @ th)) for fo, th in prof.items()}


def fd_slab_profiles(bi: float, fos: list[float], n: int = 200, steps_per_unit: float = 6000.0) -> dict[float, np.ndarray]:
    """The full FD theta profile (nodes xi = i / n) at each Fo; the solver of ``fd_slab``."""
    dx = 1.0 / n
    a = np.zeros((n + 1, n + 1))
    c = 1.0 / dx ** 2
    a[0, 0], a[0, 1] = -2 * c, 2 * c
    for i in range(1, n):
        a[i, i - 1], a[i, i], a[i, i + 1] = c, -2 * c, c
    a[n, n - 1], a[n, n] = 2 * c, -2 * c - 2 * bi / dx
    w = np.full(n + 1, dx)
    w[0] = w[n] = dx / 2
    th = np.ones(n + 1)
    eye = np.eye(n + 1)
    out, t = {}, 0.0
    dt = 1.0 / steps_per_unit
    for fo in sorted(fos):
        todo = fo - t
        m = max(8, int(round(todo / dt)))
        h = todo / m
        cn_l, cn_r = np.linalg.inv(eye - 0.5 * h * a), eye + 0.5 * h * a
        start = 0
        if t == 0.0:  # Rannacher start: four implicit-Euler half steps (two full steps) damp the start-up discontinuity
            ie = np.linalg.inv(eye - 0.5 * h * a)
            for _ in range(4):
                th = ie @ th
            start = 2
        for _ in range(start, m):
            th = cn_l @ (cn_r @ th)
        t = fo
        out[fo] = th.copy()
    return out


def fd_diffusion_uptake(taus: list[float], n: int = 200, steps_per_unit: float = 4000.0) -> dict[float, float]:
    """Mean uptake M_t/M_inf of a slab (half-thickness 1, D = 1, surface held at equilibrium) by Crank-Nicolson with a Rannacher
    start: independent of the series in ``physics_drivers.slab_uptake_fraction``. Returns {tau: uptake}."""
    dx = 1.0 / n
    a = np.zeros((n + 1, n + 1))
    c = 1.0 / dx ** 2
    a[0, 0], a[0, 1] = -2 * c, 2 * c
    for i in range(1, n):
        a[i, i - 1], a[i, i], a[i, i + 1] = c, -2 * c, c
    a = a[:n, :n]  # surface node n is Dirichlet (held at 1 in uptake variables)
    b = np.zeros(n)
    b[n - 1] = c
    w = np.full(n, dx)
    w[0] = dx / 2
    th = np.zeros(n)  # uptake variable u = 1 - concentration/equilibrium... here u(0)=0 inside, u=1 at the surface
    eye = np.eye(n)
    out, t = {}, 0.0
    dt = 1.0 / steps_per_unit
    for tau in sorted(taus):
        m = max(8, int(round((tau - t) / dt)))
        h = (tau - t) / m
        left = np.linalg.inv(eye - 0.5 * h * a)
        right = eye + 0.5 * h * a
        start = 0
        if t == 0.0:
            ie = np.linalg.inv(eye - 0.5 * h * a)
            for _ in range(4):
                th = ie @ (th + 0.5 * h * b)
            start = 2
        for _ in range(start, m):
            th = left @ (right @ th + h * b)
        t = tau
        out[tau] = float(w @ th + dx / 2 * 1.0)  # trapezoid including the surface node (held at 1)
    return out


# ------------------------------------------------------------------------------------------------ checks
def check_lumped_limit() -> dict:
    ea, er = [], []
    for bi in (1e-4, 1e-3):
        for fo in (0.5, 2.0, 5.0):
            for got, tag in ((PD.slab_mean_theta(fo=fo, bi=bi), "mean"), (PD.slab_center_theta(fo=fo, bi=bi), "center")):
                ref = theta_lumped(bi, fo)
                ea.append(abs(got - ref))
                er.append(_rel(got, ref))
    return _res("V01", "Bi -> 0: volume-average and centre theta against exp(-Bi Fo) (lumped capacitance)",
                "exp(-Bi Fo); the lumped model itself differs from the exact slab by O(Bi)", ea, er, 1e-3,
                note="tolerance 1e-3 = the O(Bi) difference of the lumped model at Bi = 1e-3")


def check_dirichlet_limit() -> dict:
    ea, er = [], []
    for fo in (0.02, 0.05, 0.1, 0.3, 1.0):
        for got, ref in ((PD.slab_center_theta(fo=fo, bi=1e8), theta_center_dirichlet(fo)),
                         (PD.slab_mean_theta(fo=fo, bi=1e8), theta_mean_dirichlet(fo))):
            ea.append(abs(got - ref))
            er.append(_rel(got, ref, 1e-12) if ref > 1e-9 else 0.0)
    return _res("V02", "Bi -> infinity: centre and volume-average theta against the Dirichlet series (4/pi, 8/pi^2)",
                "Carslaw-Jaeger Dirichlet slab series (400 terms, independent code)", ea, er, 1e-5,
                note="Fo >= 0.02; Bi = 1e8")


def check_semi_infinite_surface() -> dict:
    ea, er = [], []
    for bi in (0.5, 2.0, 10.0, 50.0):
        for fo in (0.0005, 0.002, 0.008, 0.0199):
            if bi * math.sqrt(fo) > 20:
                continue
            got, ref = PD.slab_theta(1.0, fo=fo, bi=bi), theta_surface_semi_infinite(bi, fo)
            ea.append(abs(got - ref))
            er.append(_rel(got, ref, 1e-9))
    return _res("V03", "Fo < 0.02: surface theta against the convective semi-infinite solution exp(u^2) erfc(u), u = Bi sqrt(Fo)",
                "exact for the slab until the fronts meet (error ~ erfc(1/sqrt(Fo)) < 1e-12)", ea, er, 1e-9)


def check_front_to_series_continuity() -> dict:
    ea, er = [], []
    eps = 1e-9
    for bi in (0.1, 1.0, 10.0, 100.0):
        for xi in (0.0, 0.25, 0.5, 0.75, 1.0):
            lo, hi = PD.slab_theta(xi, fo=PD.FO_FRONT - eps, bi=bi), PD.slab_theta(xi, fo=PD.FO_FRONT + eps, bi=bi)
            ea.append(abs(hi - lo))
            er.append(_rel(hi, lo, 1e-9))
        for a_, b_ in ((PD.slab_mean_theta(fo=PD.FO_FRONT - eps, bi=bi), PD.slab_mean_theta(fo=PD.FO_FRONT + eps, bi=bi)),):
            ea.append(abs(a_ - b_))
            er.append(_rel(a_, b_, 1e-9))
    return _res("V04", "continuity of the local and mean theta across the series / front switch at Fo = 0.02",
                "left and right limits at Fo = 0.02 -/+ 1e-9", ea, er, 1e-6, tol_kind="abs")


def check_textbook_constants() -> dict:
    ea, er = [], []
    for bi, (z, c) in TEXTBOOK_PLANE_WALL.items():
        z1 = PD.slab_eigenvalues(bi, 1)[0]
        c1 = 4 * math.sin(z1) / (2 * z1 + math.sin(2 * z1))
        ea += [abs(z1 - z), abs(c1 - c)]
        er += [_rel(z1, z), _rel(c1, c)]
    z1 = PD.slab_eigenvalues(1e9, 1)[0]
    ea.append(abs(z1 - TEXTBOOK_BI_INFINITY[0]))
    er.append(_rel(z1, TEXTBOOK_BI_INFINITY[0]))
    return _res("V05", "plane-wall first-term zeta_1 and C_1 versus Bi (textbook table, 4 decimals) against the root finder",
                f"recalled textbook table ({RECALLED}); Bi = infinity is exact (pi/2)", ea, er, 6e-4, tol_kind="abs",
                source_status=RECALLED, note="tolerance 6e-4 = rounding of a 4-decimal table")


def check_one_term_chart_curve() -> dict:
    """The Heisler centre-temperature chart is the one-term series for Fo >= 0.2: compare it, with the textbook zeta_1 and C_1,
    against the full series used by the driver. Textbooks state the one-term error as about 2 % at Fo = 0.2 and smaller later."""
    ea, er, by_fo = [], [], {}
    for fo in (0.2, 0.3, 0.5, 1.0, 2.0):
        worst = 0.0
        for bi, (z, c) in TEXTBOOK_PLANE_WALL.items():
            got, ref = PD.slab_center_theta(fo=fo, bi=bi), one_term(0.0, fo, z, c)
            ea.append(abs(got - ref))
            er.append(_rel(ref, got, 1e-9))
            worst = max(worst, er[-1])
        by_fo[str(fo)] = worst
    return _res("V06", "centre theta at Fo >= 0.2: full series against the one-term chart curve built from textbook zeta_1, C_1",
                f"one-term series with recalled textbook constants ({RECALLED})", ea, er, 2e-2,
                source_status=RECALLED, max_rel_error_by_fo=by_fo,
                note="tolerance 2e-2 = the textbook accuracy of the one-term curve at Fo = 0.2 (second term dropped); the error falls "
                     "with Fo; includes the 4-decimal rounding of the constants")


def check_mean_by_quadrature() -> dict:
    ea, er = [], []
    xi, w = PD.gauss_legendre_half_slab(32)
    for bi in (0.1, 1.0, 10.0, 100.0):
        for fo in (0.005, 0.02, 0.1, 0.5, 1.5):
            quad = sum(wi * PD.slab_theta(x, fo=fo, bi=bi) for x, wi in zip(xi, w))
            got = PD.slab_mean_theta(fo=fo, bi=bi)
            ea.append(abs(got - quad))
            er.append(_rel(got, quad, 1e-9))
    return _res("V07", "volume-average theta against 32-node Gauss-Legendre integration of the local theta over the slab",
                "quadrature of slab_theta (independent of the closed-form mean)", ea, er, 2e-6, tol_kind="abs")


def check_fd_reference(n: int = 200) -> dict:
    ea, er = [], []
    fos = [0.05, 0.2, 0.5, 1.0]
    for bi in (0.1, 1.0, 10.0, 100.0):
        ref = fd_slab(bi, fos, n=n)
        for fo in fos:
            fc, fs, fm = ref[fo]
            got = (PD.slab_center_theta(fo=fo, bi=bi), PD.slab_theta(1.0, fo=fo, bi=bi), PD.slab_mean_theta(fo=fo, bi=bi))
            for g, r in zip(got, (fc, fs, fm)):
                ea.append(abs(g - r))
                er.append(_rel(g, r, 1e-3))
    return _res("V08", "centre, surface and volume-average theta against a 200-node Crank-Nicolson finite-difference solve",
                "dense CN solve, Rannacher start (independent of the series)", ea, er, 2e-3, tol_kind="abs",
                note="FD spatial error ~ 1/n^2; relative error uses a floor of 1e-3 in theta")


def _two_stage_dimensional(n: int, bi: float, fo_total: float, method: str = "exact") -> tuple[float, float, float]:
    L, alpha, k = 0.01, 1.4e-7, 0.5
    h = bi * k / L
    minutes = fo_total * L ** 2 / alpha / 60.0
    r = ND.slab_two_stage(t0_c=0.0, stages=[(minutes, 100.0, h)], half_thickness_m=L, alpha_m2_s=alpha, k_w_mk=k, n=n, method=method)
    s = r["stage_end"][0]
    return s["centre_c"] / 100.0, s["surface_c"] / 100.0, s["volume_avg_c"] / 100.0  # 1 - theta


def check_modal_stepper_convergence() -> dict:
    ea, er, orders = [], [], {}
    for bi in (1.0, 10.0):
        for fo in (0.2, 0.5):
            ref = (1 - PD.slab_center_theta(fo=fo, bi=bi), 1 - PD.slab_theta(1.0, fo=fo, bi=bi), 1 - PD.slab_mean_theta(fo=fo, bi=bi))
            errs = []
            for n in (10, 20, 40, 80, 160):
                got = _two_stage_dimensional(n, bi, fo)
                errs.append(max(abs(g - r) for g, r in zip(got, ref)))
            orders[f"Bi{bi}_Fo{fo}"] = [round(math.log(errs[i] / errs[i + 1], 2), 3) for i in range(len(errs) - 1) if errs[i + 1] > 1e-14]
            ea.append(errs[-1])
            er.append(errs[-1] / max(abs(r) for r in ref))
    return _res("V09", "exact modal stepper (n = 160 nodes) against the series for (1 - theta) at the centre, surface and volume mean",
                "analytic series; the stepper is exact in time, so the difference is the spatial discretisation (2nd order)", ea, er,
                2e-4, tol_kind="abs", observed_order_by_case=orders,
                note="observed order = log2(error(n) / error(2n)) for n = 10, 20, 40, 80, 160")


def check_modal_stepper_two_stage_superposition() -> dict:
    """Ambient step at t1 for a uniform start: T = Tinf1 + (T0 - Tinf1) theta(t) + (Tinf2 - Tinf1) (1 - theta(t - t1)) (same h)."""
    ea, er = [], []
    L, alpha, k = 0.01, 1.4e-7, 0.5
    for bi in (1.0, 10.0):
        h = bi * k / L
        for fo1, fo2 in ((0.1, 0.3), (0.3, 0.2), (0.5, 0.5)):
            m1, m2 = fo1 * L ** 2 / alpha / 60.0, fo2 * L ** 2 / alpha / 60.0
            r = ND.slab_two_stage(t0_c=20.0, stages=[(m1, 150.0, h), (m2, 60.0, h)], half_thickness_m=L, alpha_m2_s=alpha, k_w_mk=k,
                                  n=160)
            s = r["stage_end"][1]
            fo = fo1 + fo2
            th = (PD.slab_center_theta(fo=fo, bi=bi), PD.slab_theta(1.0, fo=fo, bi=bi), PD.slab_mean_theta(fo=fo, bi=bi))
            th2 = (PD.slab_center_theta(fo=fo2, bi=bi), PD.slab_theta(1.0, fo=fo2, bi=bi), PD.slab_mean_theta(fo=fo2, bi=bi))
            for got, a, b in zip((s["centre_c"], s["surface_c"], s["volume_avg_c"]), th, th2):
                ref = 150.0 + (20.0 - 150.0) * a + (60.0 - 150.0) * (1 - b)
                ea.append(abs(got - ref))
                er.append(_rel(got, ref, 1.0))
    return _res("V10", "exact modal stepper, two stages (ambient 150 -> 60 C), against the analytic superposition of two series",
                "linear superposition of the series (same film coefficient in both stages)", ea, er, 0.05, tol_kind="abs",
                note="deg C; n = 160 nodes; the difference is the spatial error of the stepper")


def check_modal_vs_crank_nicolson() -> dict:
    ea, er = [], []
    L, alpha, k = 0.01, 1.4e-7, 0.5
    for bi1, bi2 in ((1.0, 3.0), (10.0, 0.5), (5.0, 5.0)):
        stages = [(8.0, 180.0, bi1 * k / L), (12.0, 25.0, bi2 * k / L)]
        ex = ND.slab_two_stage(t0_c=4.0, stages=stages, half_thickness_m=L, alpha_m2_s=alpha, k_w_mk=k, n=30)
        cn = ND.slab_two_stage(t0_c=4.0, stages=stages, half_thickness_m=L, alpha_m2_s=alpha, k_w_mk=k, n=30, method="cn",
                               fo_step=0.0005)
        for key in ("centre_c", "surface_c", "volume_avg_c"):
            for i in range(2):
                a, b = ex["stage_end"][i][key], cn["stage_end"][i][key]
                ea.append(abs(a - b))
                er.append(_rel(a, b, 1.0))
        ea.append(abs(ex["centre_peak_last_stage_c"] - cn["centre_peak_last_stage_c"]))
        er.append(_rel(ex["centre_peak_last_stage_c"], cn["centre_peak_last_stage_c"], 1.0))
    return _res("V11", "exact modal stepper against its own Crank-Nicolson mode (same 30-node system, Fo step 5e-4), two stages",
                "Crank-Nicolson time stepping of the same finite-difference operator", ea, er, 0.05, tol_kind="abs",
                note="deg C; the CN time-stepping error is the difference")


def check_n_terms_convergence() -> dict:
    ea, er, need = [], [], {}
    ref_n = 400
    for bi in (0.1, 1.0, 10.0, 100.0, 1000.0):
        for fo in (PD.FO_FRONT, 0.05, 0.1, 0.3, 1.0):
            ref = PD.slab_center_theta(fo=fo, bi=bi, n_terms=ref_n)
            refm = PD.slab_mean_theta(fo=fo, bi=bi, n_terms=ref_n)
            errs = {n: max(abs(PD.slab_center_theta(fo=fo, bi=bi, n_terms=n) - ref), abs(PD.slab_mean_theta(fo=fo, bi=bi, n_terms=n) - refm))
                    for n in (5, 10, 20, 30, 40, 60, 120)}
            need[f"Bi{bi}_Fo{fo}"] = next((n for n in sorted(errs) if errs[n] <= 1e-10), None)
            ea.append(errs[PD.N_TERMS])
            er.append(errs[PD.N_TERMS] / max(abs(ref), 1e-12))
    worst_fo = max(v for v in need.values() if v is not None)
    return _res("V12", f"N_TERMS = {PD.N_TERMS} convergence: centre and mean theta against a {ref_n}-term series, Fo >= 0.02",
                f"{ref_n}-term series (same formula)", ea, er, 1e-10, tol_kind="abs", n_terms_default=PD.N_TERMS,
                smallest_n_for_1e_10_by_case=need, largest_needed_n=worst_fo,
                note="at Fo >= 0.02 the series is converged to 1e-10 with far fewer than N_TERMS terms; the default has a margin of "
                     f"{PD.N_TERMS / worst_fo:.1f}x over the worst case")


def plank_ode_time(*, rho: float, latent: float, t_freeze: float, t_air: float, thickness: float, h: float, k: float) -> float:
    """Independent time to freeze a slab of full thickness ``a`` cooled from both faces: integrate rho L ds/dt = dT / (1/h + s/k) for
    the front depth s from 0 to a/2 (RK4 in s, t as the integral of the inverse rate)."""
    dT = t_freeze - t_air
    n, s_end = 2000, thickness / 2.0
    f = lambda s: rho * latent / dT * (1.0 / h + s / k)  # dt/ds  # noqa: E731
    ds = s_end / n
    tot = 0.0
    for i in range(n):
        s0 = i * ds
        tot += ds / 6.0 * (f(s0) + 4 * f(s0 + ds / 2) + f(s0 + ds))
    return tot


def check_plank_identities() -> dict:
    ea, er = [], []
    cases = [dict(rho=1000.0, latent=3.34e5, t_freeze=-1.0, t_air=-30.0, thickness=0.05, h=20.0, k=2.2),
             dict(rho=1050.0, latent=2.8e5, t_freeze=-2.0, t_air=-18.0, thickness=0.02, h=12.0, k=1.8),
             dict(rho=900.0, latent=2.0e5, t_freeze=-0.5, t_air=-40.0, thickness=0.1, h=100.0, k=2.5)]
    for c in cases:
        got = PD.plank_freezing_time_s(rho=c["rho"], latent_j_kg=c["latent"], t_freeze_c=c["t_freeze"], t_air_c=c["t_air"],
                                       thickness_m=c["thickness"], h_w_m2k=c["h"], k_frozen_w_mk=c["k"])
        ref = plank_ode_time(**c)
        ea.append(abs(got - ref))
        er.append(_rel(got, ref))
        # thaw is the mirror image: the same time with the sign of the temperatures reversed
        thaw = ND.thaw_time_s(rho=c["rho"], latent_j_kg=c["latent"], t_freeze_c=-c["t_freeze"], t_medium_c=-c["t_air"],
                              thickness_m=c["thickness"], h_w_m2k=c["h"], k_unfrozen_w_mk=c["k"])
        ea.append(abs(thaw - got))
        er.append(_rel(thaw, got))
        # limits: conduction-only and convection-only forms
        big_h = PD.plank_freezing_time_s(rho=c["rho"], latent_j_kg=c["latent"], t_freeze_c=c["t_freeze"], t_air_c=c["t_air"],
                                         thickness_m=c["thickness"], h_w_m2k=1e12, k_frozen_w_mk=c["k"])
        cond = c["rho"] * c["latent"] / (c["t_freeze"] - c["t_air"]) * 0.125 * c["thickness"] ** 2 / c["k"]
        ea.append(abs(big_h - cond))
        er.append(_rel(big_h, cond))
        big_k = PD.plank_freezing_time_s(rho=c["rho"], latent_j_kg=c["latent"], t_freeze_c=c["t_freeze"], t_air_c=c["t_air"],
                                         thickness_m=c["thickness"], h_w_m2k=c["h"], k_frozen_w_mk=1e12)
        conv = c["rho"] * c["latent"] / (c["t_freeze"] - c["t_air"]) * 0.5 * c["thickness"] / c["h"]
        ea.append(abs(big_k - conv))
        er.append(_rel(big_k, conv))
        # scaling: t is linear in 1/dT; conduction term ~ a^2, convection term ~ a
        dbl = PD.plank_freezing_time_s(rho=c["rho"], latent_j_kg=c["latent"], t_freeze_c=c["t_freeze"], t_air_c=c["t_freeze"] - 2 * (c["t_freeze"] - c["t_air"]),
                                       thickness_m=c["thickness"], h_w_m2k=c["h"], k_frozen_w_mk=c["k"])
        ea.append(abs(dbl - got / 2))
        er.append(_rel(dbl, got / 2))
    return _res("V13", "Plank slab freezing time against an integration of the same quasi-steady front ODE (identity), the thaw "
                       "formula (with identical k and dT it reduces to Plank's form), conduction-only and convection-only limits and 1/dT "
                       "scaling",
                "RK4 integral of rho L ds/dt = dT / (1/h + s/k), s = 0 .. a/2; closed-form limits", ea, er, 1e-6)


def stefan_enthalpy_time(*, ste: float, n_half: int = 40, biot_like: float = 5.0) -> tuple[float, float]:
    """(enthalpy-method freezing time, Plank time) in seconds for a slab of full thickness 1 cm frozen from both faces by air at
    -20 C through h; the frozen specific heat is set from the Stefan number ste = c dT / L. Explicit enthalpy scheme, symmetric
    centre. Plank neglects the sensible heat: it is the ste -> 0 limit."""
    rho, latent, k, dT = 1000.0, 3.34e5, 2.2, 20.0
    c = ste * latent / dT
    a = 0.01
    h = biot_like * k / (a / 2)
    dx = (a / 2) / n_half
    dt = 0.4 * min(dx * dx / (k / (rho * c)), rho * c * dx / 2.0 / h)
    H = np.full(n_half + 1, rho * latent)  # J/m3 relative to the fully frozen state at 0 C: frozen below 0 C has H < 0, T = H / (rho c)

    def temp(Hv):
        return np.where(Hv < 0.0, Hv / (rho * c), 0.0)  # the phase-change band 0 <= H <= rho L sits at the freezing point, 0 C

    t = 0.0
    div = np.empty(n_half + 1)
    while H[0] > 0.0:
        T = temp(H)
        q = -k * (T[1:] - T[:-1]) / dx  # q[i]: flux between node i and i + 1, positive towards the surface
        qs = h * (T[-1] + dT)  # loss to the air at -dT
        div[0] = q[0] / (dx / 2)
        div[1:n_half] = (q[1:] - q[:-1]) / dx
        div[n_half] = (qs - q[-1]) / (dx / 2)
        H = H - dt * div
        t += dt
        if t > 1e6:
            raise RuntimeError("enthalpy freezing did not finish")
    plank = PD.plank_freezing_time_s(rho=rho, latent_j_kg=latent, t_freeze_c=0.0, t_air_c=-dT, thickness_m=a, h_w_m2k=h,
                                     k_frozen_w_mk=k)
    return t, plank


def check_plank_vs_stefan_enthalpy(stes=(0.4, 0.2, 0.1)) -> dict:
    ea, er, table = [], [], {}
    for ste in stes:
        t_num, t_plank = stefan_enthalpy_time(ste=ste)
        table[f"Ste_{ste}"] = {"enthalpy_s": round(t_num, 2), "plank_s": round(t_plank, 2), "plank_over_enthalpy": round(t_plank / t_num, 4)}
        ea.append(abs(t_plank - t_num))
        er.append(_rel(t_plank, t_num))
    mono = all(er[i] > er[i + 1] for i in range(len(er) - 1))
    return _res("V14", "Plank time against an enthalpy-method Stefan solve at decreasing Stefan number (Plank = the Ste -> 0 limit)",
                "explicit enthalpy FD, 40 nodes in the half slab, sensible heat of the frozen layer included", ea, er, 0.25,
                results_by_stefan_number=table, error_decreases_with_stefan_number=bool(mono), _gate=bool(mono),
                note="the error is the neglected sensible heat; it must fall with Ste, here from the largest Ste to the smallest; "
                     "S178 FIX-PHYS: the pass needs the fall too (a reversed trend fails)")


def check_fickian_slab() -> dict:
    ea, er, extra = [], [], {}
    taus = [0.0005, 0.002, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5]
    D, L = 1.0e-9, 0.005
    got = {tau: PD.slab_uptake_fraction(d_m2_s=D, half_thickness_m=L, time_s=tau * L ** 2 / D) for tau in taus}
    fd = fd_diffusion_uptake(taus, n=200)
    for tau in taus:
        ea.append(abs(got[tau] - fd[tau]))
        er.append(_rel(got[tau], fd[tau], 1e-3))
    extra["max_abs_error_vs_fd"] = max(ea)
    # analytic limits
    short = [(tau, 2 * math.sqrt(tau / math.pi)) for tau in (1e-5, 1e-4, 5e-4)]
    ea_s = [abs(PD.slab_uptake_fraction(d_m2_s=D, half_thickness_m=L, time_s=t * L ** 2 / D) - r) for t, r in short]
    long_ = [(tau, 1 - 8 / math.pi ** 2 * math.exp(-math.pi ** 2 * tau / 4)) for tau in (1.0, 1.5, 2.5)]
    ea_l = [abs(PD.slab_uptake_fraction(d_m2_s=D, half_thickness_m=L, time_s=t * L ** 2 / D) - r) for t, r in long_]
    extra["max_abs_error_short_time_sqrt_limit"], extra["max_abs_error_long_time_one_term"] = max(ea_s), max(ea_l)
    # half-uptake time (recalled textbook value)
    lo, hi = 0.01, 1.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if PD.slab_uptake_fraction(d_m2_s=D, half_thickness_m=L, time_s=mid * L ** 2 / D) < 0.5:
            lo = mid
        else:
            hi = mid
    extra["half_uptake_tau_code"], extra["half_uptake_tau_textbook"] = round(0.5 * (lo + hi), 5), SLAB_HALF_UPTAKE_TAU
    extra["half_uptake_source_status"] = RECALLED
    ea += ea_s + ea_l + [abs(0.5 * (lo + hi) - SLAB_HALF_UPTAKE_TAU)]
    er += [0.0] * (len(ea_s) + len(ea_l)) + [_rel(0.5 * (lo + hi), SLAB_HALF_UPTAKE_TAU)]
    mono = all(got[taus[i]] < got[taus[i + 1]] for i in range(len(taus) - 1)) and all(0 <= v <= 1 for v in got.values())
    extra["monotone_and_bounded"] = bool(mono)
    return _res("V15", "Fickian slab uptake fraction against a 200-node Crank-Nicolson diffusion solve, the short-time sqrt and long-time "
                       "one-term limits and the textbook half-uptake time", "FD diffusion solve; limits; recalled half-time "
                       f"({RECALLED})", ea, er, 5e-4, tol_kind="abs", **extra)


def check_short_time_front_vs_fd(n: int = 400, steps_per_unit: float = 200000.0) -> dict:
    """V16 (m7): local theta of the convective front solution (Fo < 0.02) against a fine FD solve at xi 0.5 and 0.9."""
    ea, er, table = [], [], {}
    fos, xis = [0.002, 0.01], [0.5, 0.9]
    for bi in (1.0, 10.0, 100.0):
        prof = fd_slab_profiles(bi, fos, n=n, steps_per_unit=steps_per_unit)
        for fo in fos:
            for xi in xis:
                ref = float(prof[fo][int(round(xi * n))])
                got = PD.slab_theta(xi, fo=fo, bi=bi)
                ea.append(abs(got - ref))
                er.append(_rel(got, ref, 1e-3))
                table[f"Bi_{bi:g}_Fo_{fo:g}_xi_{xi:g}"] = {"front": round(got, 6), "fd": round(ref, 6)}
    return _res("V16", "Fo < 0.02: local theta of the convective front solution at xi 0.5 and 0.9 against a 400-node Crank-Nicolson "
                       "solve (time step Fo 5e-6)", "fine FD solve (independent of the front formula)", ea, er, 2e-3, tol_kind="abs",
                local_theta_by_case=table)


_DOSE_CASES = ((4.0, 100.0, 2.0, 0.004, 200.0, 33.0), (4.0, 100.0, 30.0, 0.01, 500.0, 10.0), (20.0, 98.0, 1.0, 0.005, 300.0, 10.0))
_K, _ALPHA = 0.5, 1.4e-7  # engineering test settings (the registry k / alpha are not read here)


@functools.lru_cache(maxsize=2)
def _dose_rule_cases(nn: int = 24, nt: int = 1200) -> tuple[dict, ...]:
    """Per case: the layer's zone-mean dose and dose at the volume-average temperature, and the same two quantities from a dense
    reference (``nn`` Gauss-Legendre nodes, ``nt`` uniform times, trapezoid on the dose rate)."""
    out = []
    for t0, bath, dur, L, h, z in _DOSE_CASES:
        props = dict(half_thickness_m=L, alpha_m2_s=_ALPHA, h_w_m2k=h, k_w_mk=_K)
        hist = PD.zone_node_histories(t0_c=t0, bath_c=bath, duration_min=dur, **props)
        zone = PD.zone_mean_dose(hist, t_ref_c=100.0, z_c=z)
        zt = PD.zone_trajectory(t0_c=t0, bath_c=bath, duration_min=dur, steps=40, **props)
        vol = PD.trajectory_dose([(m, v) for m, _, v in zt], t_ref_c=100.0, z_c=z)
        xi, w = PD.gauss_legendre_half_slab(nn)
        ts = np.linspace(0.0, dur, nt + 1)
        bi = h * L / _K
        T = np.array([[bath + (t0 - bath) * (PD.slab_theta(x, fo=_ALPHA * 60.0 * t / L ** 2, bi=bi) if t > 0 else 1.0) for t in ts]
                      for x in xi])
        rate = 10.0 ** ((T - 100.0) / z)
        trap = lambda y: float(np.sum((y[1:] + y[:-1]) * np.diff(ts)) / 2.0)  # noqa: E731
        zone_ref = sum(wi * trap(rate[i]) for i, wi in enumerate(w))
        vavg = np.asarray(w) @ T
        vol_ref = trap(10.0 ** ((vavg - 100.0) / z))
        out.append({"case": f"t0_{t0:g}_bath_{bath:g}_min_{dur:g}_L_{L:g}_h_{h:g}_z_{z:g}", "zone": zone, "zone_ref": zone_ref,
                    "vol": vol, "vol_ref": vol_ref})
    return tuple(out)


def check_zone_dose_vs_dense_reference() -> dict:
    """V17 (m7): the layer's 8-node, 48-time zone-mean dose against a dense reference."""
    cases = _dose_rule_cases()
    ea = [abs(c["zone"] - c["zone_ref"]) for c in cases]
    er = [_rel(c["zone"], c["zone_ref"]) for c in cases]
    return _res("V17", "zone-mean dose of the layer (8 Gauss-Legendre nodes, 48 graded times) against a dense reference (24 nodes, "
                       "1,200 uniform times)", "dense quadrature of the series temperature field", ea, er, 1e-2)


def check_dose_rule_biases() -> dict:
    """V18 (m9): signed numerical bias of the two dose rules against the dense reference, and whether the zone-mean >= volume-average
    inequality of the layer is larger than those biases."""
    cases = _dose_rule_cases()
    zb = [c["zone"] / c["zone_ref"] - 1.0 for c in cases]
    vb = [c["vol"] / c["vol_ref"] - 1.0 for c in cases]
    margin = [c["zone_ref"] / c["vol_ref"] - 1.0 for c in cases]
    bias = max(abs(x) for x in zb + vb)
    ok = all(m > 2 * bias for m in margin)
    table = {c["case"]: {"zone_mean_bias": round(z_, 6), "volume_avg_t_bias": round(v_, 6), "reference_ratio_minus_1": round(m, 6)}
             for c, z_, v_, m in zip(cases, zb, vb, margin)}
    return _res("V18", "numerical bias of the zone-mean dose (trapezoid on the graded node grid) and of the dose at the volume-average "
                       "temperature (midpoint T, uniform 40 steps) against the dense reference; the physical zone / volume-average "
                       "ratio must exceed twice the bias", "dense reference of V17", [abs(x) for x in zb + vb], [abs(x) for x in zb + vb],
                5e-3, _gate=ok, bias_by_case=table, volume_avg_t_bias_sign="NEGATIVE" if all(x < 0 for x in vb) else "MIXED",
                zone_mean_bias_sign="POSITIVE" if all(x > 0 for x in zb) else "NEGATIVE" if all(x < 0 for x in zb) else "MIXED",
                inequality_exceeds_twice_the_bias=bool(ok))


def independence_counts(checks: list[dict]) -> dict:
    """{class: {"checks": n, "passed": n}} (m7: the headline counts independent checks apart from the rest)."""
    out = {k: {"checks": 0, "passed": 0} for k in INDEPENDENCE_CLASSES}
    for c in checks:
        d = out.setdefault(c.get("independence", "UNCLASSIFIED"), {"checks": 0, "passed": 0})
        d["checks"] += 1
        d["passed"] += int(bool(c["passed"]))
    return out


def run_all(*, quick: bool = False) -> list[dict]:
    checks: list[Callable[[], dict]] = [
        check_lumped_limit, check_dirichlet_limit, check_semi_infinite_surface, check_front_to_series_continuity,
        check_textbook_constants, check_one_term_chart_curve, check_mean_by_quadrature, check_fd_reference,
        check_modal_stepper_convergence, check_modal_stepper_two_stage_superposition, check_modal_vs_crank_nicolson,
        check_n_terms_convergence, check_plank_identities,
        (lambda: check_plank_vs_stefan_enthalpy(stes=(0.4, 0.2))) if quick else check_plank_vs_stefan_enthalpy, check_fickian_slab,
        (lambda: check_short_time_front_vs_fd(n=200, steps_per_unit=50000.0)) if quick else check_short_time_front_vs_fd,
        check_zone_dose_vs_dense_reference, check_dose_rule_biases]
    return [c() for c in checks]
