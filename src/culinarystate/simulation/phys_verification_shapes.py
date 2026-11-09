"""Verification pack for the shape eigen-series of ``shape_series`` (S178 PHYS3, T4-C08-R1). DRAFT, AI_DRAFTED.

Extends ``phys_verification`` (the slab pack, unchanged) to the infinite cylinder, the sphere and the Heisler product shapes. Each
check compares the series with a reference that does not use its code path:

- analytic limits: Dirichlet (Bi = inf exactly, and Bi -> inf), lumped capacitance (Bi -> 0), the long-cylinder limit of the finite
  cylinder (and the thin-disk limit to the slab), short times (slab surface = semi-infinite solid exactly; sphere surface -> the
  semi-infinite solid as Fo -> 0; the exact short-time Dirichlet sphere uptake 6 sqrt(Fo/pi) - 3 Fo);
- finite-volume method-of-lines solves (independent of the eigenfunctions): 1-D radial (slab / cylinder / sphere, 200 cells, exact
  in time through the symmetric eigen-decomposition of the semi-discrete operator) and 2-D (r, z) and (x, y) Crank-Nicolson solves
  (Rannacher start, sparse LU) of the finite cylinder and the square bar, which test the product rule;
- root and coefficient identities (eigen-condition residuals, exact roots at Bi = 1 (sphere) and Bi = inf, the closed-form mean
  coefficients, completeness sum_n C_n m_n = 1);
- the slab bound kept by Layer 2 (every shape's centre and mean theta <= the slab of its smallest half-dimension) on a grid;
- consistency with ``physics_drivers`` (slab) and the truncation rule; first-term constants of the cylinder and sphere recalled from
  heat-transfer textbook tables (tagged SOURCE_UNVERIFIED_AGENT_RECALLED, compared at their 4-decimal precision, not a source).

Each check returns {id, what, reference, n_cases, max_abs_error, max_rel_error, tolerance, tolerance_on, passed, ...}, as the slab
pack does. Nothing here holds a food value.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
from scipy import linalg, sparse, special
from scipy.sparse import linalg as splinalg

from culinarystate.simulation import physics_drivers as PD
from culinarystate.simulation import shape_series as S

VERSION = "phys-verification-shapes-0.1.0-draft"
RECALLED = "SOURCE_UNVERIFIED_AGENT_RECALLED"
CYL, SPH, SLAB = "INFINITE_CYLINDER", "SPHERE", "SLAB"

# first-term constants (zeta_1, C_1) versus Bi for the infinite cylinder and the sphere: Incropera & DeWitt-type table, recalled,
# 4 decimals (the Bi = 1 sphere row and the Bi = inf rows are exact and are also checked exactly in SV07)
TEXTBOOK_CYLINDER = {0.01: (0.1412, 1.0025), 0.02: (0.1995, 1.0050), 0.05: (0.3142, 1.0124), 0.1: (0.4417, 1.0246),
                     0.2: (0.6170, 1.0483), 0.5: (0.9408, 1.1143), 1.0: (1.2558, 1.2071), 2.0: (1.5995, 1.3384),
                     5.0: (1.9898, 1.5029), 10.0: (2.1795, 1.5677), 20.0: (2.2880, 1.5919), 50.0: (2.3572, 1.6002),
                     100.0: (2.3809, 1.6015)}
TEXTBOOK_SPHERE = {0.01: (0.1730, 1.0030), 0.02: (0.2445, 1.0060), 0.05: (0.3854, 1.0150), 0.1: (0.5423, 1.0298),
                   0.2: (0.7593, 1.0592), 0.5: (1.1656, 1.1441), 1.0: (1.5708, 1.2732), 2.0: (2.0288, 1.4793),
                   5.0: (2.5704, 1.7870), 10.0: (2.8363, 1.9249), 20.0: (2.9857, 1.9781), 50.0: (3.0788, 1.9962),
                   100.0: (3.1102, 1.9990)}


def _res(cid: str, what: str, ref: str, errs_abs: list[float], errs_rel: list[float], tol: float, tol_kind: str = "abs",
         **extra) -> dict:
    ma, mr = (max(errs_abs) if errs_abs else 0.0), (max(errs_rel) if errs_rel else 0.0)
    val = mr if tol_kind == "rel" else ma
    passed = bool(val <= tol) and all(extra.get(k, True) for k in ("monotone", "order_ok", "no_violations"))
    return {"id": cid, "what": what, "reference": ref, "n_cases": len(errs_abs), "max_abs_error": float(ma),
            "max_rel_error": float(mr), "tolerance": tol, "tolerance_on": tol_kind, "passed": passed, **extra}


def _rel(a: float, b: float, floor: float = 1e-12) -> float:
    return abs(a - b) / max(abs(b), floor)


# ------------------------------------------------------------------------------------------------ independent references
def dirichlet_center(shape: str, fo: float, terms: int = 400) -> float:
    if shape == SLAB:
        return 4 / math.pi * sum((-1) ** n / (2 * n + 1) * math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 * fo / 4) for n in range(terms))
    if shape == CYL:
        j = special.jn_zeros(0, terms)
        return float(np.sum(2 / (j * special.j1(j)) * np.exp(-j * j * fo)))
    return 2 * sum((-1) ** (n + 1) * math.exp(-(n * math.pi) ** 2 * fo) for n in range(1, terms + 1))


def dirichlet_mean(shape: str, fo: float, terms: int = 400) -> float:
    if shape == SLAB:
        return 8 / math.pi ** 2 * sum(math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 * fo / 4) / (2 * n + 1) ** 2 for n in range(terms))
    if shape == CYL:
        j = special.jn_zeros(0, terms)
        return float(np.sum(4 / (j * j) * np.exp(-j * j * fo)))
    return 6 / math.pi ** 2 * sum(math.exp(-(n * math.pi) ** 2 * fo) / n ** 2 for n in range(1, terms + 1))


def theta_surface_semi_infinite(bi: float, fo: float) -> float:
    u = bi * math.sqrt(fo)
    return float(special.erfcx(u))


def _fv_1d(m: int, n: int, bi: float, length: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Finite-volume operator on [0, length] with a symmetric centre and a Robin surface (-d theta/dn = bi theta), metric r^m.

    Returns (V, K): cell volumes (per unit angle) and the conductance matrix, V d theta/dt = K theta."""
    dr = length / n
    r = np.arange(n + 1) * dr
    a, b = np.clip(r - dr / 2, 0.0, length), np.clip(r + dr / 2, 0.0, length)
    V = (b ** (m + 1) - a ** (m + 1)) / (m + 1)
    K = np.zeros((n + 1, n + 1))
    for i in range(n):
        g = ((i + 0.5) * dr) ** m / dr
        K[i, i] -= g
        K[i, i + 1] += g
        K[i + 1, i + 1] -= g
        K[i + 1, i] += g
    K[n, n] -= bi * length ** m
    return V, K


def fd_radial(shape: str, bi: float, fos: list[float], n: int = 200) -> dict[float, tuple[float, float, float]]:
    """{Fo: (centre, surface, volume mean)} of the semi-discrete finite-volume problem, exact in time:
    theta(Fo) = V^-1/2 Q exp(Lambda Fo) Q^T V^1/2 theta_0 with Q Lambda Q^T = V^-1/2 K V^-1/2 (symmetric)."""
    m = {SLAB: 0, CYL: 1, SPH: 2}[shape]
    V, K = _fv_1d(m, n, bi)
    s = 1.0 / np.sqrt(V)
    lam, q = linalg.eigh(s[:, None] * K * s[None, :])
    c0 = q.T @ (np.sqrt(V) * np.ones(n + 1))
    out = {}
    for fo in fos:
        th = s * (q @ (np.exp(lam * fo) * c0))
        out[fo] = (float(th[0]), float(th[n]), float(V @ th / V.sum()))
    return out


def fd_2d(kind: str, bi: float, height: float, fos: list[float], n_r: int = 60, steps_per_unit: float = 4000.0
          ) -> dict[float, tuple[float, float, float]]:
    """2-D Crank-Nicolson finite-volume solve (Rannacher start, sparse LU) on [0, 1] x [0, height] with symmetric planes at 0 and
    Robin faces at 1 and at height (Bi = h R / k in units of the first dimension). kind = "FINITE_CYLINDER" ((r, z), r-metric) or
    "SQUARE_BAR" ((x, y), Cartesian). Returns {Fo: (centre, outer corner, volume mean)}; Fo in units of the first dimension."""
    m = {"FINITE_CYLINDER": 1, "SQUARE_BAR": 0}[kind]
    n_z = max(8, int(round(n_r * height)))
    Vr, Kr = _fv_1d(m, n_r, bi)
    Vz, Kz = _fv_1d(0, n_z, bi, length=height)
    V = sparse.diags(np.kron(Vr, Vz))
    K = sparse.kron(sparse.csr_matrix(Kr), sparse.diags(Vz)) + sparse.kron(sparse.diags(Vr), sparse.csr_matrix(Kz))
    w = np.kron(Vr, Vz)
    th = np.ones(w.size)
    out, t = {}, 0.0
    dt = 1.0 / steps_per_unit
    for fo in sorted(fos):
        steps = max(8, int(round((fo - t) / dt)))
        h = (fo - t) / steps
        lu = splinalg.splu(sparse.csc_matrix(V - 0.5 * h * K))
        rhs_m = (V + 0.5 * h * K).tocsr()
        start = 0
        if t == 0.0:  # four implicit-Euler half steps: (V - h/2 K) theta' = V theta, the same matrix as the CN step
            for _ in range(4):
                th = lu.solve(V @ th)
            start = 2
        for _ in range(start, steps):
            th = lu.solve(rhs_m @ th)
        t = fo
        out[fo] = (float(th[0]), float(th[-1]), float(w @ th / w.sum()))
    return out


# ------------------------------------------------------------------------------------------------ checks
def check_dirichlet_exact() -> dict:
    ea, er = [], []
    for shape in (SLAB, CYL, SPH):
        for fo in (0.005, 0.02, 0.05, 0.1, 0.3, 1.0):
            for got, ref in ((S.center_theta(shape, fo=fo, bi=math.inf), dirichlet_center(shape, fo)),
                             (S.mean_theta(shape, fo=fo, bi=math.inf), dirichlet_mean(shape, fo))):
                ea.append(abs(got - ref))
                er.append(_rel(got, ref, 1e-9))
    return _res("SV01", "Bi = inf: centre and volume-mean theta of slab, cylinder, sphere against independent Dirichlet series",
                "Dirichlet series with (n - 1/2) pi, scipy jn_zeros(0) and n pi (400 terms)", ea, er, 1e-12)


def check_dirichlet_limit() -> dict:
    ea, er = [], []
    for shape in (CYL, SPH):
        for fo in (0.02, 0.05, 0.1, 0.3, 1.0):
            for got, ref in ((S.center_theta(shape, fo=fo, bi=1e8), dirichlet_center(shape, fo)),
                             (S.mean_theta(shape, fo=fo, bi=1e8), dirichlet_mean(shape, fo))):
                ea.append(abs(got - ref))
                er.append(_rel(got, ref, 1e-9) if ref > 1e-9 else 0.0)
    return _res("SV02", "Bi -> infinity (Bi = 1e8): cylinder and sphere centre and mean theta against the Dirichlet series",
                "Dirichlet series; the difference is O(1/Bi)", ea, er, 1e-6)


def check_lumped_limit() -> dict:
    ea, er, scaled = [], [], []
    for bi in (1e-4, 1e-3):
        for fo in (0.5, 2.0, 5.0):
            cases = [(S.center_theta(CYL, fo=fo, bi=bi), S.mean_theta(CYL, fo=fo, bi=bi), math.exp(-2 * bi * fo)),
                     (S.center_theta(SPH, fo=fo, bi=bi), S.mean_theta(SPH, fo=fo, bi=bi), math.exp(-3 * bi * fo))]
            for hr in (1.0, 2.0):  # finite cylinder, half-height = hr R: A/V = 2/R + 1/Lz
                fz, bz = fo / hr ** 2, bi * hr
                cases.append((S.finite_cylinder_theta(0, 0, fo_r=fo, bi_r=bi, fo_z=fz, bi_z=bz),
                              S.finite_cylinder_mean_theta(fo_r=fo, bi_r=bi, fo_z=fz, bi_z=bz), math.exp(-(2 * bi * fo + bz * fz))))
            cases.append((S.brick_theta((0, 0, 0), fos=(fo,) * 3, bis=(bi,) * 3), S.brick_mean_theta(fos=(fo,) * 3, bis=(bi,) * 3),
                          math.exp(-3 * bi * fo)))
            for c, mn, ref in cases:
                for got in (c, mn):
                    ea.append(abs(got - ref))
                    er.append(_rel(got, ref))
                    scaled.append(abs(got - ref) / bi)
    return _res("SV03", "Bi -> 0: centre and mean theta of cylinder, sphere, finite cylinder (Lz = R, 2R) and cube against lumped "
                        "capacitance exp(-(h A / k V) alpha t)", "lumped model; it differs from the exact solution by O(Bi)",
                ea, er, 1e-3, max_error_over_bi=float(max(scaled)),
                note="tolerance 1e-3 = the O(Bi) error of the lumped model at Bi = 1e-3; max_error_over_bi stays O(1)")


def check_long_cylinder_limit() -> dict:
    ea, er, by_ratio, mono = [], [], {}, True
    ratios = (1.0, 2.0, 5.0, 10.0, 30.0, 100.0)
    for bi in (0.5, 5.0, 50.0):
        for fo in (0.05, 0.2, 0.5, 1.0):
            ref_c, ref_m = S.center_theta(CYL, fo=fo, bi=bi), S.mean_theta(CYL, fo=fo, bi=bi)
            prev = None
            for hr in ratios:
                fz, bz = fo / hr ** 2, bi * hr
                c = S.finite_cylinder_theta(0, 0, fo_r=fo, bi_r=bi, fo_z=fz, bi_z=bz)
                mn = S.finite_cylinder_mean_theta(fo_r=fo, bi_r=bi, fo_z=fz, bi_z=bz)
                e_c, e_m = abs(c - ref_c), abs(mn - ref_m) / max(ref_m, 1e-12)
                by_ratio.setdefault(str(hr), [0.0, 0.0])
                by_ratio[str(hr)] = [max(by_ratio[str(hr)][0], e_c), max(by_ratio[str(hr)][1], e_m)]
                if prev is not None and e_m > prev + 1e-15:
                    mono = False
                prev = e_m
                if hr >= 10.0:
                    ea.append(e_c)
                    er.append(e_c / max(ref_c, 1e-12))
    # thin-disk limit: radius >> half-height -> slab of the half-height
    disk = []
    for bi in (0.5, 5.0):
        for fo in (0.05, 0.5):
            for rr in (10.0, 100.0):  # R / Lz; dimensionless on Lz
                c = S.finite_cylinder_theta(0, 0, fo_r=fo / rr ** 2, bi_r=bi * rr, fo_z=fo, bi_z=bi)
                disk.append(abs(c - S.center_theta(SLAB, fo=fo, bi=bi)))
    ea += disk
    er += [0.0] * len(disk)
    return _res("SV04", "long-cylinder limit: finite-cylinder centre theta -> infinite cylinder at half-height >= 10 R (and the "
                        "thin disk -> slab); the mean converges monotonically in Lz / R",
                "infinite-cylinder series (thin disk: slab series); the end-face influence at the centre is ~ erfc(Lz / (2 sqrt(alpha t)))",
                ea, er, 1e-9, monotone=mono, error_by_half_height_over_radius={k: [float(v[0]), float(v[1])] for k, v in by_ratio.items()},
                note="error_by_half_height_over_radius = [max centre abs error, max mean rel error]; the mean error falls ~ R / Lz")


def check_short_time() -> dict:
    ea, er, extra = [], [], {}
    # (a) slab surface equals the semi-infinite solid exactly until the fronts meet
    for bi in (0.5, 2.0, 10.0, 50.0):
        for fo in (1e-4, 5e-4, 2e-3, 1e-2):
            got, ref = S.theta(SLAB, 1.0, fo=fo, bi=bi), theta_surface_semi_infinite(bi, fo)
            ea.append(abs(got - ref))
            er.append(_rel(got, ref, 1e-9))
    # (b) exact short-time Dirichlet sphere uptake: 1 - mean = 6 sqrt(Fo/pi) - 3 Fo + 12 sqrt(Fo) sum ierfc(n / sqrt Fo)
    for fo in (1e-5, 1e-4, 1e-3, 1e-2, 2e-2):
        got, ref = 1 - S.mean_theta(SPH, fo=fo, bi=math.inf), 6 * math.sqrt(fo / math.pi) - 3 * fo
        ea.append(abs(got - ref))
        er.append(_rel(got, ref, 1e-12))
    # (c) sphere surface -> semi-infinite solid as Fo -> 0, with the curvature error O(sqrt Fo)
    fos = (1e-5, 4e-5, 1.6e-4, 6.4e-4, 2.56e-3)
    orders = {}
    order_ok = True
    for bi in (0.5, 2.0, 10.0, 50.0):
        errs = [abs(S.theta(SPH, 1.0, fo=fo, bi=bi) - theta_surface_semi_infinite(bi, fo)) for fo in fos]
        obs = [math.log(errs[i + 1] / errs[i], 4.0) for i in range(len(errs) - 1) if errs[i] > 0]
        orders[f"Bi{bi}"] = [round(o, 3) for o in obs]
        order_ok &= all(errs[i] < errs[i + 1] for i in range(len(errs) - 1)) and obs[0] >= 0.5
        extra[f"sphere_surface_error_at_fo_1e_5_Bi{bi}"] = float(errs[0])
        extra[f"sphere_surface_error_over_bi_fo_at_fo_1e_5_Bi{bi}"] = float(errs[0] / (bi * fos[0]))
    extra["sphere_surface_observed_order_in_fo"] = orders
    return _res("SV05", "short times: slab surface = semi-infinite solid (exact before the fronts meet); Dirichlet sphere uptake "
                        "= 6 sqrt(Fo/pi) - 3 Fo (exact up to ierfc terms < 1e-40 at Fo <= 0.02); sphere surface -> semi-infinite "
                        "solid (error falls monotonically as Fo -> 0, observed order >= 0.5 at the smallest Fo)",
                "exp(u^2) erfc(u); Crank-type short-time sphere series", ea, er, 1e-10, order_ok=order_ok, **extra,
                note="the max errors are over (a) and (b); (c) is a convergence test: the curvature error is about Bi Fo (order 1) "
                     "while Bi sqrt(Fo) << 1 and flattens where Bi sqrt(Fo) is large")


def check_fd_radial(n: int = 200) -> dict:
    ea, er = [], []
    fos = [0.05, 0.2, 0.5, 1.0]
    by_shape = {}
    for shape in (SLAB, CYL, SPH):
        worst = 0.0
        for bi in (0.1, 1.0, 10.0, 100.0):
            ref = fd_radial(shape, bi, fos, n=n)
            for fo in fos:
                got = (S.center_theta(shape, fo=fo, bi=bi), S.theta(shape, 1.0, fo=fo, bi=bi), S.mean_theta(shape, fo=fo, bi=bi))
                for g, r in zip(got, ref[fo]):
                    ea.append(abs(g - r))
                    er.append(_rel(g, r, 1e-3))
                    worst = max(worst, ea[-1])
        by_shape[shape] = worst
    return _res("SV06", f"centre, surface and mean theta of slab, cylinder, sphere against a {n}-cell finite-volume solve",
                "finite-volume method of lines, exact in time (symmetric eigen-decomposition); independent of the series", ea, er,
                2e-3, max_abs_error_by_shape=by_shape, note="FV spatial error ~ 1/n^2; relative error floor 1e-3 in theta")


def check_fd_2d_products(n_r: int = 60) -> dict:
    ea, er, by = [], [], {}
    fos = [0.1, 0.4]
    for kind in ("FINITE_CYLINDER", "SQUARE_BAR"):
        for height in ((0.5, 1.0, 2.0) if kind == "FINITE_CYLINDER" else (1.0,)):
            for bi in (1.0, 10.0):
                ref = fd_2d(kind, bi, height, fos, n_r=n_r)
                for fo in fos:
                    fz, bz = fo / height ** 2, bi * height
                    first = CYL if kind == "FINITE_CYLINDER" else SLAB
                    got = (S.center_theta(first, fo=fo, bi=bi) * S.center_theta(SLAB, fo=fz, bi=bz),
                           S.theta(first, 1.0, fo=fo, bi=bi) * S.theta(SLAB, 1.0, fo=fz, bi=bz),
                           S.mean_theta(first, fo=fo, bi=bi) * S.mean_theta(SLAB, fo=fz, bi=bz))
                    for g, r in zip(got, ref[fo]):
                        ea.append(abs(g - r))
                        er.append(_rel(g, r, 1e-3))
                        key = f"{kind}_H{height}"
                        by[key] = max(by.get(key, 0.0), ea[-1])
    return _res("SV07", "product rule: finite cylinder (half-height 0.5, 1, 2 R) and square bar, centre, outer corner and mean theta "
                        f"against a 2-D Crank-Nicolson finite-volume solve ({n_r} cells per radius)",
                "2-D CN (Rannacher start, sparse LU) of the (r, z) / (x, y) heat equation; independent of the series", ea, er,
                3e-3, max_abs_error_by_case=by, note="spatial error ~ 1/n^2 at 60 cells; corner = the most demanding point")


def check_roots_exact_and_residuals() -> dict:
    ea, er = [], []
    resid = 0.0
    increasing = True
    for shape in (SLAB, CYL, SPH):
        for bi in (1e-6, 1e-3, 0.1, 1.0, 10.0, 1e3, 1e6):
            z = S.eigenvalues(shape, bi, 200)
            increasing &= bool(np.all(np.diff(z) > 0))
            if shape == SLAB:
                f = z * np.sin(z) - bi * np.cos(z)
                scale = z + bi
            elif shape == CYL:
                f = z * special.j1(z) - bi * special.j0(z)
                scale = (z + bi) / np.sqrt(z)
            else:
                f = (1 - bi) * np.sin(z) - z * np.cos(z)
                scale = z + bi
            resid = max(resid, float(np.max(np.abs(f) / scale)))
    ea.append(resid)
    er.append(resid)
    # exact cases
    z, c, _ = S.coefficients(SPH, 1.0, 1)
    ea += [abs(z[0] - math.pi / 2), abs(c[0] - 4 / math.pi)]
    j01 = float(special.jn_zeros(0, 1)[0])
    z, c, _ = S.coefficients(CYL, math.inf, 1)
    ea += [abs(z[0] - j01), abs(c[0] - 2 / (j01 * special.j1(j01)))]
    z, c, _ = S.coefficients(SPH, math.inf, 50)
    ea.append(float(np.max(np.abs(c - 2 * (-1.0) ** np.arange(50)))))
    z, c, _ = S.coefficients(SLAB, math.inf, 50)
    k = np.arange(1, 51)
    ea.append(float(np.max(np.abs(c - 4 * (-1.0) ** (k + 1) / ((2 * k - 1) * math.pi)))))
    er += [0.0] * (len(ea) - len(er))
    return _res("SV08", "roots: scaled eigen-condition residual of the first 200 roots (Bi 1e-6 .. 1e6), strictly increasing; exact "
                        "roots and C_n at Bi = 1 (sphere: pi/2, 4/pi) and Bi = inf (j_01, 2/(j_01 J1(j_01)); 2(-1)^(n+1); "
                        "4(-1)^(n+1)/((2n-1) pi))", "eigen-conditions; closed forms", ea, er, 1e-12, monotone=increasing)


def check_textbook_first_term() -> dict:
    ea, er = [], []
    for shape, table in ((CYL, TEXTBOOK_CYLINDER), (SPH, TEXTBOOK_SPHERE)):
        for bi, (zt, ct) in table.items():
            z, c, _ = S.coefficients(shape, bi, 1)
            ea += [abs(z[0] - zt), abs(c[0] - ct)]
            er += [_rel(z[0], zt), _rel(c[0], ct)]
    return _res("SV09", "first-term zeta_1 and C_1 of cylinder and sphere versus Bi (textbook table, 4 decimals) against the root finder",
                f"recalled textbook table ({RECALLED})", ea, er, 6e-4, source_status=RECALLED,
                note="tolerance 6e-4 = rounding of a 4-decimal table; not a source")


def check_coefficient_identities() -> dict:
    ea, er, raw = [], [], 0.0
    for shape in (SLAB, CYL, SPH):
        for bi in (0.01, 0.3, 1.0, 3.0, 30.0, 300.0):
            z, c, m = S.coefficients(shape, bi, S.MAX_TERMS)
            if shape == SLAB:
                closed = 2 * bi ** 2 / (z ** 2 * (z ** 2 + bi ** 2 + bi))
            elif shape == CYL:
                closed = 4 * bi ** 2 / (z ** 2 * (z ** 2 + bi ** 2))
            else:
                closed = 6 * bi ** 2 / (z ** 2 * (z ** 2 + bi ** 2 - bi))
            d = np.abs(c * m - closed)
            ea.append(float(np.max(d)))
            er.append(float(np.max(d / np.maximum(np.abs(closed), 1e-300))))
            # completeness: mean theta at Fo = 0+ is 1; the dropped tail is k Bi^2 / (pi^4 N^3) (zeta_n ~ n pi), k = 2/3, 4/3, 2
            k = {SLAB: 2 / 3, CYL: 4 / 3, SPH: 2.0}[shape]
            tail = k * bi ** 2 / (math.pi ** 4 * S.MAX_TERMS ** 3)
            total = float(np.sum(c * m))
            ea.append(abs(total + tail - 1.0))
            er.append(abs(total + tail - 1.0))
            raw = max(raw, abs(total - 1.0))
    return _res("SV10", "coefficients: C_n x mean factor against the closed forms 2Bi^2/(z^2(z^2+Bi^2+Bi)), 4Bi^2/(z^2(z^2+Bi^2)), "
                        f"6Bi^2/(z^2(z^2+Bi^2-Bi)); completeness sum_n C_n m_n + analytic tail = 1 over {S.MAX_TERMS} terms",
                "closed forms from the eigen-conditions; analytic tail k Bi^2 / (pi^4 N^3)", ea, er, 1e-10,
                max_completeness_deficit_without_tail=float(raw),
                note="absolute errors gate; relative errors are large only for coefficients near 1e-19 (n ~ 4000)")


def check_slab_bound() -> dict:
    bis, fos = np.logspace(-2, 2, 9), np.logspace(-3, 0.7, 12)
    violations, n, margin = 0, 0, math.inf
    order_viol = 0
    for bi in bis:
        for fo in fos:
            sc, sm = S.center_theta(SLAB, fo=fo, bi=bi), S.mean_theta(SLAB, fo=fo, bi=bi)
            cc, cm = S.center_theta(CYL, fo=fo, bi=bi), S.mean_theta(CYL, fo=fo, bi=bi)
            pc, pm = S.center_theta(SPH, fo=fo, bi=bi), S.mean_theta(SPH, fo=fo, bi=bi)
            cases = [(cc, cm), (pc, pm)]
            for hr in (0.5, 1.0, 2.0):  # finite cylinder; bound dimension = min(R, Lz)
                # dimensionless on L_min: R = 1 / min(1, hr), Lz = hr / min(1, hr)
                lmin = min(1.0, hr)
                r_, lz = 1.0 / lmin, hr / lmin
                cases.append((S.finite_cylinder_theta(0, 0, fo_r=fo / r_ ** 2, bi_r=bi * r_, fo_z=fo / lz ** 2, bi_z=bi * lz),
                              S.finite_cylinder_mean_theta(fo_r=fo / r_ ** 2, bi_r=bi * r_, fo_z=fo / lz ** 2, bi_z=bi * lz)))
            for sides in ((1.0, 1.0, 1.0), (1.0, 2.0, 3.0)):
                fs, bs = tuple(fo / s ** 2 for s in sides), tuple(bi * s for s in sides)
                cases.append((S.brick_theta((0, 0, 0), fos=fs, bis=bs), S.brick_mean_theta(fos=fs, bis=bs)))
            for c, m in cases:
                n += 2
                violations += int(c > sc + 1e-12) + int(m > sm + 1e-12)
                margin = min(margin, sc - c, sm - m)
            order_viol += int(not (pc <= cc + 1e-12 <= sc + 2e-12)) + int(not (pm <= cm + 1e-12 <= sm + 2e-12))
    return _res("SV11", "slab bound: centre and mean theta of cylinder, sphere, finite cylinder (Lz = 0.5, 1, 2 R), cube and brick "
                        "(1:2:3) <= the slab of the smallest half-dimension (Bi 0.01 .. 100, Fo 1e-3 .. 5); sphere <= cylinder <= slab",
                "the slab series (the Layer 2 bound); a numerical check on a grid, not a proof", [float(violations + order_viol)],
                [0.0], 0.0, no_violations=(violations + order_viol) == 0, comparisons=n, violations=violations,
                ordering_violations=order_viol, smallest_margin_theta=float(margin))


def check_consistency_with_slab_driver() -> dict:
    ea, er = [], []
    small = []
    for bi in (0.1, 1.0, 10.0, 100.0):
        for fo in (0.02, 0.05, 0.2, 1.0, 3.0):
            for xi in (0.0, 0.5, 1.0):
                g, r = S.theta(SLAB, xi, fo=fo, bi=bi), PD.slab_theta(xi, fo=fo, bi=bi)
                ea.append(abs(g - r))
                er.append(_rel(g, r, 1e-9))
            g, r = S.mean_theta(SLAB, fo=fo, bi=bi), PD.slab_mean_theta(fo=fo, bi=bi)
            ea.append(abs(g - r))
            er.append(_rel(g, r, 1e-9))
        for fo in (1e-4, 1e-3, 0.0199):  # PD switches to the semi-infinite front; its centre returns 1 (bound < 1e-6)
            small.append(abs(S.center_theta(SLAB, fo=fo, bi=bi) - PD.slab_center_theta(fo=fo, bi=bi)))
            small.append(abs(S.mean_theta(SLAB, fo=fo, bi=bi) - PD.slab_mean_theta(fo=fo, bi=bi)))
            small.append(abs(S.theta(SLAB, 1.0, fo=fo, bi=bi) - PD.slab_theta(1.0, fo=fo, bi=bi)))
    return _res("SV12", "shape_series slab against physics_drivers (the Layer 2 slab): local and mean theta, Fo >= 0.02",
                "physics_drivers slab series (N_TERMS = 60); Fo < 0.02 reported apart (driver uses the front solution)", ea, er,
                1e-10, max_abs_error_fo_below_0_02=float(max(small)), fo_below_0_02_ok=bool(max(small) <= 1e-6))


def check_one_term() -> dict:
    ea, er, by = [], [], {}
    for shape in (CYL, SPH):
        for fo in (0.2, 0.5, 1.0):
            worst = 0.0
            for bi in (0.1, 1.0, 10.0, 100.0):
                got, ref = S.one_term(shape, 0.0, fo=fo, bi=bi), S.center_theta(shape, fo=fo, bi=bi)
                ea.append(abs(got - ref))
                er.append(_rel(got, ref, 1e-9))
                worst = max(worst, er[-1])
            by[f"{shape}_Fo{fo}"] = worst
    return _res("SV13", "one-term (Heisler chart) centre theta of cylinder and sphere against the full series at Fo >= 0.2",
                f"full series; the textbook statement that one term is within about 2 % at Fo >= 0.2 is recalled ({RECALLED})",
                ea, er, 2e-2, tol_kind="rel", max_rel_error_by_case=by)


def check_truncation() -> dict:
    ea, er, worst_n = [], [], 0
    for shape in (SLAB, CYL, SPH):
        for bi in (0.1, 10.0, 1e4):
            for fo in (1e-5, 1e-4, 1e-3, 1e-2, 0.1, 1.0):
                n = S.n_terms_for(fo)
                worst_n = max(worst_n, n)
                ref_n = min(S.MAX_TERMS, 2 * n)
                for p in (0.0, 0.5, 0.9, 1.0):
                    a, b = S.theta(shape, p, fo=fo, bi=bi), S.theta(shape, p, fo=fo, bi=bi, n_terms=ref_n)
                    ea.append(abs(a - b))
                    er.append(_rel(a, b, 1e-9))
                a, b = S.mean_theta(shape, fo=fo, bi=bi), S.mean_theta(shape, fo=fo, bi=bi, n_terms=ref_n)
                ea.append(abs(a - b))
                er.append(_rel(a, b, 1e-9))
    return _res("SV14", "truncation: the Fo-adaptive term count against twice as many terms (Fo 1e-5 .. 1, centre to surface, mean)",
                "same series with 2N terms", ea, er, 1e-12, largest_n_terms=worst_n, fo_min=S.fo_min(), max_terms=S.MAX_TERMS)


def check_dimensional_wrapper() -> dict:
    ea, er = [], []
    props = dict(alpha_m2_s=1.4e-7, h_w_m2k=600.0, k_w_mk=0.5)
    for L in (0.001, 0.0025, 0.005, 0.012):
        for t in (5.0, 60.0, 600.0, 3600.0):
            got = S.core_and_mean_temperature(S.Geometry("SLAB", (L,)), t0_c=20.0, bath_c=100.0, time_s=t, **props)
            ref = PD.core_and_mean_temperature(t0_c=20.0, bath_c=100.0, time_s=t, half_thickness_m=L, **props)
            fo = props["alpha_m2_s"] * t / L ** 2
            tol_ok = fo >= PD.FO_FRONT  # below the switch the driver's centre is the front bound (<= 1e-6 in theta)
            for g, r in zip(got, ref):
                ea.append(abs(g - r) if tol_ok else 0.0)
                er.append(_rel(g, r, 1.0) if tol_ok else 0.0)
            cube = S.theta_center_and_mean(S.Geometry("CUBE", (L,)), time_s=t, **props)
            sl = S.theta_center_and_mean(S.Geometry("SLAB", (L,)), time_s=t, **props)
            ea += [abs(cube[0] - sl[0] ** 3), abs(cube[1] - sl[1] ** 3)]
            er += [0.0, 0.0]
    va = {"SLAB": (S.Geometry("SLAB", (1.0,)).volume_to_surface_m, 1.0),
          "CYL": (S.Geometry("INFINITE_CYLINDER", (1.0,)).volume_to_surface_m, 0.5),
          "SPH": (S.Geometry("SPHERE", (1.0,)).volume_to_surface_m, 1 / 3),
          "CUBE": (S.Geometry("CUBE", (1.0,)).volume_to_surface_m, 1 / 3),
          "FC": (S.Geometry("FINITE_CYLINDER", (1.0, 1.0)).volume_to_surface_m, 1 / 3)}
    ea += [abs(a - b) for a, b in va.values()]
    er += [0.0] * len(va)
    return _res("SV15", "dimensional wrapper: slab geometry against physics_drivers.core_and_mean_temperature (degC), cube = slab^3, "
                        "V/A of each shape", "physics_drivers; closed-form V/A", ea, er, 1e-8,
                note="degC; cases with Fo < 0.02 are not compared (driver front bound)")


def run_all(*, quick: bool = False) -> list[dict]:
    checks: list[Callable[[], dict]] = [
        check_dirichlet_exact, check_dirichlet_limit, check_lumped_limit, check_long_cylinder_limit, check_short_time,
        (lambda: check_fd_radial(n=100)) if quick else check_fd_radial,
        (lambda: check_fd_2d_products(n_r=30)) if quick else check_fd_2d_products,
        check_roots_exact_and_residuals, check_textbook_first_term, check_coefficient_identities, check_slab_bound,
        check_consistency_with_slab_driver, check_one_term, check_truncation, check_dimensional_wrapper]
    return [c() for c in checks]
