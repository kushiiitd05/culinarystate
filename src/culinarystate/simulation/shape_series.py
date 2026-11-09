"""Eigen-series for transient conduction in a slab, infinite cylinder, sphere and the Heisler product shapes (finite cylinder,
rectangular brick / cube). S178 PHYS3, T4-C08-R1. DRAFT, AI_DRAFTED, MODEL_DERIVED, never evidence.

Problem (all shapes): uniform start T_0, surrounding medium T_b, convective surface (coefficient h), constant k and alpha,
theta = (T - T_b) / (T_0 - T_b). One-dimensional shapes, with L = half-thickness (slab) or R = radius, Fo = alpha t / L^2,
Bi = h L / k and position p = x / L or r / R in [0, 1] (0 = centre, 1 = surface):

- SLAB:              zeta tan zeta = Bi;                  X_n(p) = cos(zeta p);      C_n = 4 sin z / (2 z + sin 2z)
- INFINITE_CYLINDER: zeta J1(zeta) / J0(zeta) = Bi;       X_n(p) = J0(zeta p);       C_n = 2 J1(z) / (z (J0(z)^2 + J1(z)^2))
- SPHERE:            1 - zeta cot zeta = Bi;              X_n(p) = sin(zeta p)/(zeta p); C_n = 4 (sin z - z cos z) / (2z - sin 2z)

theta(p, Fo) = sum_n C_n X_n(p) exp(-zeta_n^2 Fo); the volume mean replaces X_n(p) by its volume average (sin z / z,
2 J1(z) / z, 3 (sin z - z cos z) / z^3). Bi = math.inf gives the Dirichlet roots exactly ((n - 1/2) pi, j_{0,n}, n pi).
The number of terms is chosen from Fo so that the dropped tail is below ``EPS_TAIL`` (no front / semi-infinite switch is used,
unlike ``physics_drivers``): n >= 1 + sqrt(ln(2 / EPS_TAIL) / Fo) / pi, capped at ``MAX_TERMS`` (Fo below ``fo_min()`` is refused).

Product shapes (separation of variables, exact for constant properties and the same h on every face): the FINITE_CYLINDER of
radius R and half-height Lz is theta_cyl(r/R, Fo_R, Bi_R) x theta_slab(z/Lz, Fo_Lz, Bi_Lz); a BRICK of half-sides (a, b, c) is
the product of three slabs; the CUBE is a brick with a = b = c. The volume mean of a product is the product of the means.

Slab bound (the stated bound kept by Layer 2, ``physics_drivers``): for a shape whose smallest half-dimension is L, the slab of
half-thickness L at the same h, k, alpha has centre and mean theta at least as large (it heats slowest). For the product shapes this
holds factor by factor (every factor is in [0, 1]); for the cylinder and sphere it is checked numerically on a grid in
``phys_verification_shapes`` (not proven here). Nothing in this module holds a food value; the inputs are caller (scenario) values.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy import optimize, special

VERSION = "shape-series-0.1.0-draft"
STATUS = "AI_DRAFTED_NOT_WIRED_INTO_LAYER2"
SHAPES_1D = ("SLAB", "INFINITE_CYLINDER", "SPHERE")
SHAPES = SHAPES_1D + ("FINITE_CYLINDER", "CUBE", "BRICK")
EPS_TAIL = 1e-14
MIN_TERMS = 8
MAX_TERMS = 4000


def n_terms_for(fo: float, eps: float = EPS_TAIL) -> int:
    """Terms needed so that every dropped term is below eps (|C_n X_n| <= 2 for all three shapes, zeta_n >= (n - 1) pi)."""
    if not fo > 0:
        raise ValueError("Fo must be positive")
    n = int(math.ceil(1.0 + math.sqrt(math.log(2.0 / eps) / fo) / math.pi)) + 2
    return max(MIN_TERMS, n)


def fo_min(eps: float = EPS_TAIL) -> float:
    """Smallest Fo the series evaluates within MAX_TERMS terms."""
    return math.log(2.0 / eps) / (math.pi * (MAX_TERMS - 3)) ** 2


# ------------------------------------------------------------------------------------------------ roots
def _check_bi(bi: float) -> float:
    bi = float(bi)
    if not bi > 0:
        raise ValueError("Bi must be positive (Bi = math.inf is the Dirichlet limit)")
    return bi


def _roots(shape: str, bi: float, n: int) -> np.ndarray:
    k = np.arange(1, n + 1, dtype=float)
    if shape == "SLAB":
        if math.isinf(bi):
            return (k - 0.5) * math.pi
        f = lambda z: z * math.sin(z) - bi * math.cos(z)  # noqa: E731  (= cos z (z tan z - Bi), no pole)
        return np.array([optimize.brentq(f, (i - 1) * math.pi, (i - 0.5) * math.pi, xtol=1e-15, rtol=8.9e-16, maxiter=300)
                         for i in range(1, n + 1)])
    if shape == "INFINITE_CYLINDER":
        j0 = special.jn_zeros(0, n)
        if math.isinf(bi):
            return np.asarray(j0, dtype=float)
        j1 = np.concatenate(([0.0], special.jn_zeros(1, n - 1))) if n > 1 else np.array([0.0])
        g = lambda z: z * special.j1(z) - bi * special.j0(z)  # noqa: E731
        return np.array([optimize.brentq(g, j1[i], j0[i], xtol=1e-15, rtol=8.9e-16, maxiter=300) for i in range(n)])
    if shape == "SPHERE":
        if math.isinf(bi):
            return k * math.pi
        g = lambda z: (1.0 - bi) * (math.sin(z) / z if z else 1.0) - math.cos(z)  # noqa: E731  (zeta cot zeta = 1 - Bi, / sin)
        return np.array([optimize.brentq(g, (i - 1) * math.pi, i * math.pi, xtol=1e-15, rtol=8.9e-16, maxiter=300)
                         for i in range(1, n + 1)])
    raise ValueError(f"shape must be one of {SHAPES_1D}")


def eigenvalues(shape: str, bi: float, n: int) -> np.ndarray:
    """First n positive roots zeta_n of the shape's eigen-condition (bracketed root finding; cached per shape, Bi, n)."""
    if shape not in SHAPES_1D:
        raise ValueError(f"shape must be one of {SHAPES_1D}")
    if not 1 <= int(n) <= MAX_TERMS:
        raise ValueError(f"n must be between 1 and {MAX_TERMS}")
    return _coeffs(shape, _check_bi(bi), int(n))[0].copy()


# ------------------------------------------------------------------------------------------------ coefficients
def _s1(z: np.ndarray) -> np.ndarray:
    """sin z - z cos z without cancellation at small z (series below 0.1)."""
    z = np.asarray(z, dtype=float)
    out = np.sin(z) - z * np.cos(z)
    small = z < 0.1
    if small.any():
        zs = z[small]
        out[small] = sum((-1) ** (j + 1) * 2 * j * zs ** (2 * j + 1) / math.factorial(2 * j + 1) for j in range(1, 7))
    return out


def _s2(z: np.ndarray) -> np.ndarray:
    """2 z - sin 2z without cancellation at small z."""
    z = np.asarray(z, dtype=float)
    out = 2 * z - np.sin(2 * z)
    small = z < 0.1
    if small.any():
        zs = 2 * z[small]
        out[small] = sum((-1) ** (j + 1) * zs ** (2 * j + 1) / math.factorial(2 * j + 1) for j in range(1, 7))
    return out


BLOCK = 64


def _coeffs(shape: str, bi: float, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(zeta, C_n, mean factor of X_n) for the first n terms (computed in blocks of 64 terms and cached)."""
    z, c, m = _coeffs_block(shape, bi, min(MAX_TERMS, -(-int(n) // BLOCK) * BLOCK))
    return z[:n], c[:n], m[:n]


@lru_cache(maxsize=1024)
def _coeffs_block(shape: str, bi: float, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = _roots(shape, bi, n)
    if shape == "SLAB":
        c = 4 * np.sin(z) / (2 * z + np.sin(2 * z))
        m = np.sin(z) / z
    elif shape == "INFINITE_CYLINDER":
        j0, j1 = special.j0(z), special.j1(z)
        c = 2 * j1 / (z * (j0 ** 2 + j1 ** 2))
        m = 2 * j1 / z
    else:
        s1 = _s1(z)
        c = 4 * s1 / _s2(z)
        m = 3 * s1 / z ** 3
    return z, c, m


def coefficients(shape: str, bi: float, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(zeta_n, C_n, volume-mean factor of X_n), n terms."""
    eigenvalues(shape, bi, n)  # validates
    z, c, m = _coeffs(shape, _check_bi(bi), int(n))
    return z.copy(), c.copy(), m.copy()


def _basis(shape: str, z: np.ndarray, p: float) -> np.ndarray:
    if shape == "SLAB":
        return np.cos(z * p)
    if shape == "INFINITE_CYLINDER":
        return special.j0(z * p)
    zp = z * p
    return np.sinc(zp / math.pi)  # sin(zp) / zp, = 1 at p = 0


def _prep(shape: str, fo: float, bi: float, n_terms: int | None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None:
    if shape not in SHAPES_1D:
        raise ValueError(f"shape must be one of {SHAPES_1D}")
    bi = _check_bi(bi)
    if fo < 0 or math.isnan(fo):
        raise ValueError("Fo must be >= 0")
    if fo == 0:
        return None
    n = n_terms if n_terms is not None else n_terms_for(fo)
    if n > MAX_TERMS:
        raise ValueError(f"Fo = {fo:g} needs more than {MAX_TERMS} terms (Fo below {fo_min():.3g}); use a semi-infinite solution")
    z, c, m = _coeffs(shape, bi, int(n))
    return z, c, m, np.exp(-z * z * fo)


def theta(shape: str, p: float, *, fo: float, bi: float, n_terms: int | None = None) -> float:
    """Local dimensionless temperature at p = x/L or r/R in [0, 1] (0 = centre)."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("position must be in [0, 1]")
    pr = _prep(shape, fo, bi, n_terms)
    if pr is None:
        return 1.0
    z, c, _, e = pr
    return float(np.sum(c * _basis(shape, z, p) * e))


def center_theta(shape: str, *, fo: float, bi: float, n_terms: int | None = None) -> float:
    return theta(shape, 0.0, fo=fo, bi=bi, n_terms=n_terms)


def mean_theta(shape: str, *, fo: float, bi: float, n_terms: int | None = None) -> float:
    """Volume-average dimensionless temperature."""
    pr = _prep(shape, fo, bi, n_terms)
    if pr is None:
        return 1.0
    _, c, m, e = pr
    return float(np.sum(c * m * e))


def one_term(shape: str, p: float, *, fo: float, bi: float) -> float:
    """First term only (the curve behind the Heisler charts, Fo >= 0.2)."""
    z, c, _ = _coeffs(shape, _check_bi(bi), 1)
    return float(c[0] * _basis(shape, z, p)[0] * math.exp(-z[0] ** 2 * fo))


# ------------------------------------------------------------------------------------------------ product shapes
def finite_cylinder_theta(p_r: float, p_z: float, *, fo_r: float, bi_r: float, fo_z: float, bi_z: float) -> float:
    """theta_cyl(r/R; Fo_R, Bi_R) x theta_slab(z/Lz; Fo_Lz, Bi_Lz) (Lz = half-height)."""
    return theta("INFINITE_CYLINDER", p_r, fo=fo_r, bi=bi_r) * theta("SLAB", p_z, fo=fo_z, bi=bi_z)


def finite_cylinder_mean_theta(*, fo_r: float, bi_r: float, fo_z: float, bi_z: float) -> float:
    return mean_theta("INFINITE_CYLINDER", fo=fo_r, bi=bi_r) * mean_theta("SLAB", fo=fo_z, bi=bi_z)


def brick_theta(ps: tuple[float, float, float], *, fos: tuple[float, float, float], bis: tuple[float, float, float]) -> float:
    return math.prod(theta("SLAB", p, fo=f, bi=b) for p, f, b in zip(ps, fos, bis, strict=True))


def brick_mean_theta(*, fos: tuple[float, float, float], bis: tuple[float, float, float]) -> float:
    return math.prod(mean_theta("SLAB", fo=f, bi=b) for f, b in zip(fos, bis, strict=True))


# ------------------------------------------------------------------------------------------------ dimensional geometry
@dataclass(frozen=True)
class Geometry:
    """A piece shape with its half-dimensions in metres.

    SLAB (L,), INFINITE_CYLINDER (R,), SPHERE (R,), FINITE_CYLINDER (R, Lz) with Lz the half-height, CUBE (a,) the half-side,
    BRICK (a, b, c) the half-sides."""
    shape: str
    dims_m: tuple[float, ...]

    def __post_init__(self) -> None:
        need = {"SLAB": 1, "INFINITE_CYLINDER": 1, "SPHERE": 1, "FINITE_CYLINDER": 2, "CUBE": 1, "BRICK": 3}
        if self.shape not in need:
            raise ValueError(f"shape must be one of {SHAPES}")
        if len(self.dims_m) != need[self.shape] or not all(isinstance(d, (int, float)) and d > 0 for d in self.dims_m):
            raise ValueError(f"{self.shape} needs {need[self.shape]} positive half-dimension(s) in metres")

    @property
    def bound_half_thickness_m(self) -> float:
        """Half-thickness of the slab that bounds this shape from the slow side (its smallest half-dimension)."""
        return float(min(self.dims_m))

    @property
    def volume_to_surface_m(self) -> float:
        """V / A (per unit length or area for the infinite shapes)."""
        s, d = self.shape, self.dims_m
        if s == "SLAB":
            return d[0]
        if s == "INFINITE_CYLINDER":
            return d[0] / 2
        if s == "SPHERE":
            return d[0] / 3
        if s == "FINITE_CYLINDER":
            r, lz = d
            return (r * r * lz) / (r * r + 2 * r * lz)  # V = 2 pi r^2 lz, A = 2 pi r^2 + 4 pi r lz
        a, b, c = (d * 3) if s == "CUBE" else d
        return a * b * c / (a * b + b * c + a * c)


def theta_center_and_mean(geom: Geometry, *, time_s: float, alpha_m2_s: float, h_w_m2k: float, k_w_mk: float) -> tuple[float, float]:
    """(centre theta, volume-mean theta) of a geometry at one time."""
    for name, v in (("alpha_m2_s", alpha_m2_s), ("h_w_m2k", h_w_m2k), ("k_w_mk", k_w_mk)):
        if not v > 0:
            raise ValueError(f"{name} must be positive")
    if time_s < 0:
        raise ValueError("time must be >= 0")
    s, d = geom.shape, geom.dims_m

    def fb(L: float) -> tuple[float, float]:
        return alpha_m2_s * time_s / L ** 2, h_w_m2k * L / k_w_mk

    if s in SHAPES_1D:
        fo, bi = fb(d[0])
        return center_theta(s, fo=fo, bi=bi), mean_theta(s, fo=fo, bi=bi)
    if s == "FINITE_CYLINDER":
        (fr, br), (fz, bz) = fb(d[0]), fb(d[1])
        return (finite_cylinder_theta(0.0, 0.0, fo_r=fr, bi_r=br, fo_z=fz, bi_z=bz),
                finite_cylinder_mean_theta(fo_r=fr, bi_r=br, fo_z=fz, bi_z=bz))
    halves = d * 3 if s == "CUBE" else d
    fbs = [fb(x) for x in halves]
    fos, bis = tuple(f for f, _ in fbs), tuple(b for _, b in fbs)
    return brick_theta((0.0, 0.0, 0.0), fos=fos, bis=bis), brick_mean_theta(fos=fos, bis=bis)


def core_and_mean_temperature(geom: Geometry, *, t0_c: float, bath_c: float, time_s: float, alpha_m2_s: float, h_w_m2k: float,
                              k_w_mk: float) -> tuple[float, float]:
    """(centre degC, volume-mean degC); same inputs as ``physics_drivers.core_and_mean_temperature`` plus a geometry."""
    c, m = theta_center_and_mean(geom, time_s=time_s, alpha_m2_s=alpha_m2_s, h_w_m2k=h_w_m2k, k_w_mk=k_w_mk)
    return bath_c + (t0_c - bath_c) * c, bath_c + (t0_c - bath_c) * m


# ------------------------------------------------------------------------------------------------ cut / ingredient class -> shape
MAP_SHAPES = ("SLAB", "INFINITE_CYLINDER", "FINITE_CYLINDER", "SPHERE", "CUBE", "SLAB_BOUND_UNRESOLVED")
UNCHANGED = ("SLAB", "SLAB_BOUND_UNRESOLVED")  # shapes for which Layer 2's slab stays the geometry


@dataclass(frozen=True)
class ShapeRow:
    map_id: str
    cut_class: str          # a cut class code, "*" (any) or "NONE" (no cut class bound)
    ingredient_classes: tuple[str, ...]  # food groups, or ("*",)
    shape: str
    aspect: tuple[float, float, float] | None
    basis: str


def load_shape_map(path) -> tuple[ShapeRow, ...]:
    """Rows of ``registry/shape_map_v1.csv`` (basis ASSUMED_DEFAULT)."""
    import csv
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["shape"] not in MAP_SHAPES:
                raise ValueError(f"{r['map_id']}: unknown shape {r['shape']!r}")
            if r["basis"] != "ASSUMED_DEFAULT":
                raise ValueError(f"{r['map_id']}: shape rows are ASSUMED_DEFAULT")
            asp = None
            if r["aspect_mid"]:
                asp = (float(r["aspect_low"]), float(r["aspect_mid"]), float(r["aspect_high"]))
                if not 0 < asp[0] <= asp[1] <= asp[2]:
                    raise ValueError(f"{r['map_id']}: aspect must be 0 < low <= mid <= high")
            if (r["shape"] == "FINITE_CYLINDER") != (asp is not None):
                raise ValueError(f"{r['map_id']}: a FINITE_CYLINDER row (and only it) needs an aspect ratio")
            rows.append(ShapeRow(r["map_id"], r["cut_class"], tuple(r["ingredient_class"].split("|")), r["shape"], asp, r["basis"]))
    ids = [r.map_id for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate map_id")
    keys = [(r.cut_class, g) for r in rows for g in r.ingredient_classes]
    if len(keys) != len(set(keys)):
        raise ValueError("two rows cover the same (cut class, ingredient class)")
    if not any(r.cut_class == "NONE" and r.ingredient_classes == ("*",) for r in rows):
        raise ValueError("the map needs a NONE / * default row")
    return tuple(rows)


def shape_for(rows: tuple[ShapeRow, ...], cut_class: str | None, ingredient_class: str | None) -> ShapeRow:
    """The row for one event: exact (cut, class) > (cut, *) > (NONE, class) when no cut is bound > (NONE, *).

    ``cut_class`` is the Layer 1 piece_size_class (None when UNKNOWN); ``ingredient_class`` the single food group of the consumed lot
    (None when UNKNOWN or several groups). A cut class with no row of its own falls to the NONE rows' default only, never to an
    ingredient-class row (cutting fixes the piece geometry, not the food group)."""
    cut = cut_class or "NONE"
    exact = {(r.cut_class, g): r for r in rows for g in r.ingredient_classes}
    for key in ((cut, ingredient_class), (cut, "*")):
        if key[1] is not None and key in exact:
            return exact[key]
    if cut == "NONE" and ingredient_class is not None and ("NONE", ingredient_class) in exact:
        return exact[("NONE", ingredient_class)]
    return exact[("NONE", "*")]


def geometry_for(row: ShapeRow, half_thickness_m: float, bracket: int = 1) -> Geometry | None:
    """Geometry of a mapped shape from the size class half-dimension L (bracket 0/1/2 = low/mid/high aspect); None if unresolved."""
    L = float(half_thickness_m)
    if row.shape == "SLAB_BOUND_UNRESOLVED":
        return None
    if row.shape == "FINITE_CYLINDER":
        return Geometry("FINITE_CYLINDER", (row.aspect[bracket] * L, L))
    return Geometry(row.shape, (L,))
