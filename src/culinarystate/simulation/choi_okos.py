"""Choi-Okos composition property structure for the product-temperature lag (S159, DRAFT_PENDING_26_0_H4).

Step 24 card 24b names "one PROPERTY_MODEL (Choi-Okos 1986, composition correlation, MODEL_DERIVED, never
measured EVD)"; Step 26 uses a lumped product-temperature lag with tau_h per size class. This module provides the
structure only and enters NO coefficient: every component correlation (a polynomial in T in degC, its validity
range), the surface heat-transfer coefficient h, the characteristic length V/A and the Biot ceiling of the lumped
approximation are caller inputs with PARAM / SYNTHETIC ids. Results are MODEL_DERIVED, never evidence.

Mixing structure (as recalled by the AI from the Choi-Okos approach; to be checked against the paper, OPEN):
    cp  = sum_i x_i cp_i(T)                      (mass fractions x_i)
    rho = 1 / sum_i (x_i / rho_i(T))
    k   = sum_i v_i k_i(T),  v_i = (x_i / rho_i) * rho   (volume fractions, parallel model)
Lumped capacitance: tau_h = rho * cp * L / h with L = V/A, valid only when Bi = h L / k <= the caller's ceiling.
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from culinarystate.simulation import sim_core as SC

STATUS = "DRAFT_PENDING_26_0_H4"
PROPERTY_UNITS: Mapping[str, str] = {"cp": "J/(kg*K)", "rho": "kg/m^3", "k": "J/(s*m*K)"}
H_UNIT = "J/(s*m^2*K)"
_ORIGINS = ("PARAM_RECORD", "SYNTHETIC")
_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")
OPEN_FOR_HUMANS: tuple[str, ...] = (
    "Choi-Okos 1986 component coefficients and validity ranges: OPEN, caller-supplied PARAM rows (none entered)",
    "Choi-Okos mixing rules (mass-fraction cp, inverse-sum rho, volume-fraction parallel k): OPEN, AI recollection",
    "surface heat-transfer coefficient h, geometry V/A per size class and the Biot ceiling: OPEN, caller inputs",
    "whether tau_h is taken from Choi-Okos or fitted per size class (card: tau_h(size class)): OPEN, H4 / 26.0",
)


class ChoiOkosError(ValueError):
    """Structural input error."""


class ChoiOkosRefusal(ValueError):
    """A refused computation; the message starts with a reason code."""


def _fin(x: object, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(float(x)):
        raise ChoiOkosError(f"{name} must be a finite number")
    return float(x)


def _pid(pid: object, origin: str) -> None:
    if origin not in _ORIGINS:
        raise ChoiOkosError(f"origin must be one of {_ORIGINS}")
    if not (isinstance(pid, str) and SC._PID[origin].match(pid)):
        raise ChoiOkosError(f"param id {pid!r} does not match the {origin} pattern")


@dataclass(frozen=True)
class PropertyCorrelation:
    """property_i(T) = sum_j coefficients[j] * (T_K - 273.15)^j, valid on validity_T_K (caller-supplied)."""

    param_id: str
    component: str
    property: str
    coefficients: tuple[float, ...]
    unit_si: str
    validity_T_K: tuple[float, float]
    origin: str

    def __post_init__(self) -> None:
        _pid(self.param_id, self.origin)
        if not (isinstance(self.component, str) and _CODE.match(self.component)):
            raise ChoiOkosError("component must be an upper-case code")
        if self.property not in PROPERTY_UNITS:
            raise ChoiOkosError(f"property must be one of {tuple(PROPERTY_UNITS)}")
        if self.unit_si != PROPERTY_UNITS[self.property]:
            raise ChoiOkosError(f"{self.property} correlations are in {PROPERTY_UNITS[self.property]} (no conversion)")
        if not (isinstance(self.coefficients, tuple) and self.coefficients):
            raise ChoiOkosError("coefficients must be a non-empty tuple")
        object.__setattr__(self, "coefficients", tuple(_fin(c, "coefficient") for c in self.coefficients))
        lo, hi = (_fin(v, "validity") for v in self.validity_T_K)
        if not 0 < lo < hi:
            raise ChoiOkosError("validity_T_K must be 0 < low < high (K)")
        object.__setattr__(self, "validity_T_K", (lo, hi))


@dataclass(frozen=True)
class SurfaceCoefficient:
    param_id: str
    value_si: float
    unit_si: str
    origin: str

    def __post_init__(self) -> None:
        _pid(self.param_id, self.origin)
        if self.unit_si != H_UNIT:
            raise ChoiOkosError(f"h is in {H_UNIT}")
        if not _fin(self.value_si, "h") > 0:
            raise ChoiOkosError("h must be > 0")


@dataclass(frozen=True)
class PropertyEstimate:
    cp: float
    rho: float
    k: float
    T_K: float
    composition: Mapping[str, float]
    derived_from: tuple[str, ...]
    origin: str = "MODEL_DERIVED"
    is_evidence: bool = False
    status: str = STATUS


def component_property(corr: PropertyCorrelation, T_K: float) -> float:
    T = _fin(T_K, "T_K")
    lo, hi = corr.validity_T_K
    if not lo <= T <= hi:
        raise ChoiOkosRefusal(f"CORRELATION_OUTSIDE_T_VALIDITY {corr.component}/{corr.property} at {T} K")
    t_c = T - float(SC.CELSIUS_OFFSET_K)
    out = 0
    for c in reversed(corr.coefficients):
        out = out * t_c + c
    return float(out)


def mixture_properties(mass_fractions: Mapping[str, float], correlations: Sequence[PropertyCorrelation],
                       T_K: float, *, fraction_sum_tol: float) -> PropertyEstimate:
    tol = _fin(fraction_sum_tol, "fraction_sum_tol")
    x = {c: _fin(v, f"mass fraction {c}") for c, v in mass_fractions.items()}
    if not x:
        raise ChoiOkosError("composition is empty")
    if any(v < 0 for v in x.values()):
        raise ChoiOkosRefusal("FRACTION_NEGATIVE")
    if abs(math.fsum(x.values()) - 1) > tol:
        raise ChoiOkosRefusal(f"FRACTIONS_DO_NOT_SUM {math.fsum(x.values())!r}")
    table: dict[tuple[str, str], PropertyCorrelation] = {}
    for c in correlations:
        if not isinstance(c, PropertyCorrelation):
            raise ChoiOkosError("correlations must be PropertyCorrelation instances")
        if (c.component, c.property) in table:
            raise ChoiOkosRefusal(f"CORRELATION_DUPLICATE {c.component}/{c.property}")
        table[(c.component, c.property)] = c
    used: list[PropertyCorrelation] = []
    vals: dict[tuple[str, str], float] = {}
    for comp in sorted(x):
        for prop in PROPERTY_UNITS:
            c = table.get((comp, prop))
            if c is None:
                raise ChoiOkosRefusal(f"CORRELATION_MISSING {comp}/{prop}")
            v = component_property(c, T_K)
            if not v > 0:
                raise ChoiOkosRefusal(f"PROPERTY_NOT_POSITIVE {comp}/{prop}")
            vals[(comp, prop)] = v
            used.append(c)
    cp = math.fsum(x[c] * vals[(c, "cp")] for c in x)
    rho = 1 / math.fsum(x[c] / vals[(c, "rho")] for c in x)
    k = math.fsum(x[c] / vals[(c, "rho")] * rho * vals[(c, "k")] for c in x)
    return PropertyEstimate(cp, rho, k, float(T_K), dict(sorted(x.items())), tuple(sorted(c.param_id for c in used)))


def biot_number(h: float, characteristic_length_m: float, k: float) -> float:
    return _fin(h, "h") * _fin(characteristic_length_m, "L") / _fin(k, "k")


def tau_h_param(est: PropertyEstimate, h: SurfaceCoefficient, *, characteristic_length_m: float, geometry_ref: str,
                max_biot: float, matrix_class: str, piece_size_class: str) -> SC.ParamValue:
    """MODEL_DERIVED tau_h = rho cp L / h for the size class, refused when the lumped approximation is invalid."""
    L = _fin(characteristic_length_m, "characteristic_length_m")
    ceiling = _fin(max_biot, "max_biot")
    if not (L > 0 and ceiling > 0):
        raise ChoiOkosError("characteristic length and Biot ceiling must be > 0")
    if not (isinstance(geometry_ref, str) and geometry_ref.strip()):
        raise ChoiOkosError("geometry_ref must be nonblank")
    bi = biot_number(h.value_si, L, est.k)
    if bi > ceiling:
        raise ChoiOkosRefusal(f"LUMPED_CAPACITANCE_INVALID Bi={bi!r}")
    tau = est.rho * est.cp * L / h.value_si
    digest = SC.sha256_canonical({"estimate": est, "h": h, "L": L, "geometry_ref": geometry_ref,
                                  "max_biot": ceiling, "matrix": matrix_class, "size": piece_size_class})
    return SC.ParamValue("DERIVED-" + digest[:16], "tau_h", tau, "s", matrix_class, piece_size_class, None,
                         "MODEL_DERIVED")
