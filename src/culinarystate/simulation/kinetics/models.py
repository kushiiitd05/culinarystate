"""Step 26a kinetic model forms (S159, DRAFT_PENDING_26_0_H4).

Only the forms the Plan v2 cards name are implemented (``CARD_NAMED_FORMS``); there are no AI-proposed
extra forms (``AI_PROPOSED_FORMS`` is empty). A form holds equations, parameter slots and dimensions only:
**no parameter value, no default and no prior**. Every value reaches a form from the caller.

| name | equation (response) | card source |
|---|---|---|
| ZERO_ORDER | C = C0 - k0 * tau (CONCENTRATION) | Step 24 card 24b "zero / first-order at fixed T"; SSOT 210.3 |
| FIRST_ORDER | ln(C/C0) = -k * tau (LN_RETENTION) | Step 24 card 24b; Step 26 card baseline "first-order"; SSOT 210.4 |
| WEIBULL | ln(C/C0) = -(tau/alpha)^beta (LN_RETENTION) | Step 24 card 24b "Weibull as alternative"; Step 26 card advanced rung, E26-3 |
| ARRHENIUS_REF_T | ln k(T) = ln k_ref - (Ea/R)(1/T - 1/T_ref) (LN_RATE_CONSTANT, k in s^-1) | Step 26 architecture "Equations"; Step 24 card "reference-T Arrhenius" |
| FIRST_ORDER_ARRHENIUS | ln(C/C0) = -k(T) * tau, k(T) as above (LN_RETENTION) | Step 26 shipped strong rung "per-matrix first-order + reference-T Arrhenius", one-step global fit |

``ln_retention_first_order_piecewise`` is the analytic solution of the first-order Arrhenius form under a
piecewise-constant temperature schedule (Step 26 architecture "Solver": analytic piecewise reference).

Card-named but **not** here (26b scope, prv): the AA compartment model with lumped leaching and k_dw, the
lumped product-temperature lag, the chlorophyll pH-gated form (g(pH) is PROPOSED in the card), Choi-Okos.

Units inside this module are SI: tau in s (KIN ``normalised_seconds``, clock PROCESS_TAU), T in K, Ea in
J/mol, k in s^-1 (first order). T_ref is a declared fixed input (``fixed["T_ref_K"]``), never defaulted.
The Weibull parameterisation (scale alpha, shape beta) is an AI choice among equivalent forms (OPEN).
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from culinarystate.simulation.kinetics import units as U

STATUS = "DRAFT_PENDING_26_0_H4"
LIBRARY_VERSION = "step26a-kinetics-0.1.0-draft"
R = U.GAS_CONSTANT_J_PER_MOL_K

Array = np.ndarray
Theta = Mapping[str, float]
Covariates = Mapping[str, Array]


class ModelError(ValueError):
    """Bad model input (missing parameter, covariate or fixed value; non-physical covariate)."""


@dataclass(frozen=True)
class ParameterSpec:
    symbol: str
    dimension: str       # dimension expression (units.dimension)
    transform: str       # LOG (strictly positive; fitted as ln theta) or IDENTITY
    role: str            # FORM parameter-slot role vocabulary (24a)
    description: str


COVARIATE_DIMENSIONS: Mapping[str, str] = {"tau_s": "TIME", "T_K": "TEMPERATURE"}
FIXED_DIMENSIONS: Mapping[str, str] = {"T_ref_K": "TEMPERATURE"}
RESPONSE_DIMENSIONS: Mapping[str, str] = {"LN_RETENTION": "1", "CONCENTRATION": "CONCENTRATION",
                                          "LN_RATE_CONSTANT": "1"}


@dataclass(frozen=True)
class KineticForm:
    name: str
    kin_family: str                       # KIN v1.1 candidate_model_family token
    kin_model_level: str                  # KIN v1.1 fit.model_level token
    response: str                         # RESPONSE_DIMENSIONS key
    parameters: tuple[ParameterSpec, ...]
    covariates: tuple[str, ...]
    fixed: tuple[str, ...]
    equation: str
    card_ref: str
    # Dimensionless groups: each a tuple of (symbol, power) over parameters, covariates, fixed and "R".
    dimensionless_groups: tuple[tuple[tuple[str, int], ...], ...]
    _fn: Callable[[Mapping[str, float], Covariates, Mapping[str, float]], Array]

    @property
    def symbols(self) -> tuple[str, ...]:
        return tuple(p.symbol for p in self.parameters)

    def spec(self, symbol: str) -> ParameterSpec:
        for p in self.parameters:
            if p.symbol == symbol:
                return p
        raise ModelError(f"{self.name} has no parameter {symbol!r}")

    def check_inputs(self, theta: Theta, covariates: Covariates,
                     fixed: Mapping[str, float] | None) -> tuple[dict[str, float], dict[str, Array], dict[str, float]]:
        missing = [s for s in self.symbols if s not in theta]
        if missing:
            raise ModelError(f"{self.name}: missing parameter(s) {missing}")
        th = {s: float(theta[s]) for s in self.symbols}
        for p in self.parameters:
            if not np.isfinite(th[p.symbol]) or (p.transform == "LOG" and th[p.symbol] <= 0):
                raise ModelError(f"{self.name}: parameter {p.symbol} must be finite"
                                 + (" and > 0" if p.transform == "LOG" else ""))
        fx = dict(fixed or {})
        for name in self.fixed:
            if name not in fx:
                raise ModelError(f"{self.name}: fixed input {name} is required and has no default")
            if not np.isfinite(fx[name]) or fx[name] <= 0:
                raise ModelError(f"{self.name}: {name} must be an absolute temperature in K (> 0)")
        cov: dict[str, Array] = {}
        n = None
        for name in self.covariates:
            if name not in covariates:
                raise ModelError(f"{self.name}: missing covariate {name}")
            a = np.asarray(covariates[name], dtype=float)
            if a.ndim != 1 or not np.all(np.isfinite(a)):
                raise ModelError(f"{self.name}: covariate {name} must be a finite 1-d array")
            if name == "tau_s" and np.any(a < 0):
                raise ModelError(f"{self.name}: tau_s must be >= 0 (process time since t0)")
            if name == "T_K" and np.any(a <= 0):
                raise ModelError(f"{self.name}: T_K must be an absolute temperature in K (> 0)")
            if n is not None and a.shape[0] != n:
                raise ModelError(f"{self.name}: covariates differ in length")
            n = a.shape[0]
            cov[name] = a
        return th, cov, fx

    def predict(self, theta: Theta, covariates: Covariates, fixed: Mapping[str, float] | None = None) -> Array:
        th, cov, fx = self.check_inputs(theta, covariates, fixed)
        return self._fn(th, cov, fx)


def arrhenius_rate(k_ref: float, ea: float, T_K: Array, T_ref_K: float) -> Array:
    """k(T) = k_ref * exp(-(Ea/R) (1/T - 1/T_ref)); temperatures in K only."""
    T = np.asarray(T_K, dtype=float)
    if np.any(~np.isfinite(T)) or np.any(T <= 0) or not np.isfinite(T_ref_K) or T_ref_K <= 0:
        raise ModelError("Arrhenius temperatures must be absolute (K, > 0)")
    if not np.isfinite(k_ref) or k_ref <= 0 or not np.isfinite(ea):
        raise ModelError("k_ref must be > 0 and Ea finite")
    return k_ref * np.exp(-(ea / R) * (1.0 / T - 1.0 / T_ref_K))


def _zero(th: Mapping[str, float], cov: Covariates, fx: Mapping[str, float]) -> Array:
    return th["C0"] - th["k0"] * cov["tau_s"]


def _first(th: Mapping[str, float], cov: Covariates, fx: Mapping[str, float]) -> Array:
    return -th["k"] * cov["tau_s"]


def _weibull(th: Mapping[str, float], cov: Covariates, fx: Mapping[str, float]) -> Array:
    t = cov["tau_s"]
    out = np.zeros_like(t)
    pos = t > 0
    out[pos] = -np.power(t[pos] / th["alpha"], th["beta"])
    return out


def _arrhenius(th: Mapping[str, float], cov: Covariates, fx: Mapping[str, float]) -> Array:
    return np.log(arrhenius_rate(th["k_ref"], th["Ea"], cov["T_K"], fx["T_ref_K"]))


def _first_arrhenius(th: Mapping[str, float], cov: Covariates, fx: Mapping[str, float]) -> Array:
    return -arrhenius_rate(th["k_ref"], th["Ea"], cov["T_K"], fx["T_ref_K"]) * cov["tau_s"]


_K = ParameterSpec("k", "TIME^-1", "LOG", "RATE_CONSTANT", "first-order rate constant (order 1), s^-1")
_KREF = ParameterSpec("k_ref", "TIME^-1", "LOG", "RATE_CONSTANT", "first-order rate constant at T_ref, s^-1")
_EA = ParameterSpec("Ea", "ENERGY*AMOUNT^-1", "IDENTITY", "ACTIVATION_ENERGY",
                    "activation energy, J/mol; sign not constrained by the library")
_C24 = "Plan v2 Step 24 card 24b"
_C26 = "Plan v2 Step 26 card"

FORMS: Mapping[str, KineticForm] = {f.name: f for f in (
    KineticForm("ZERO_ORDER", "ZERO_ORDER", "PRIMARY_RATE", "CONCENTRATION",
                (ParameterSpec("C0", "CONCENTRATION", "LOG", "INITIAL_VALUE", "initial concentration"),
                 ParameterSpec("k0", "CONCENTRATION*TIME^-1", "LOG", "RATE_CONSTANT",
                               "zero-order rate constant (order 0); valid while C >= 0")),
                ("tau_s",), (), "C = C0 - k0*tau", f"{_C24} (zero-order at fixed T); SSOT 210.3",
                ((("k0", 1), ("tau_s", 1), ("C0", -1)),), _zero),
    KineticForm("FIRST_ORDER", "FIRST_ORDER", "PRIMARY_RATE", "LN_RETENTION", (_K,), ("tau_s",), (),
                "ln(C/C0) = -k*tau",
                f"{_C24} (first-order at fixed T); {_C26} baseline; SSOT 210.4",
                ((("k", 1), ("tau_s", 1)),), _first),
    KineticForm("WEIBULL", "WEIBULL", "PRIMARY_RATE", "LN_RETENTION",
                (ParameterSpec("alpha", "TIME", "LOG", "SCALE_TIME", "Weibull scale, s"),
                 ParameterSpec("beta", "1", "LOG", "SHAPE", "Weibull shape (dimensionless)")),
                ("tau_s",), (), "ln(C/C0) = -(tau/alpha)^beta",
                f"{_C24} (Weibull as alternative); {_C26} advanced rung / E26-3",
                ((("tau_s", 1), ("alpha", -1)), (("beta", 1),)), _weibull),
    KineticForm("ARRHENIUS_REF_T", "ARRHENIUS_SECONDARY", "SECONDARY_ARRHENIUS", "LN_RATE_CONSTANT",
                (_KREF, _EA), ("T_K",), ("T_ref_K",),
                "ln k(T) = ln k_ref - (Ea/R)*(1/T - 1/T_ref)",
                f"{_C26} architecture detail, Equations (reference-T Arrhenius)",
                ((("Ea", 1), ("R", -1), ("T_K", -1)), (("Ea", 1), ("R", -1), ("T_ref_K", -1))), _arrhenius),
    KineticForm("FIRST_ORDER_ARRHENIUS", "FIRST_ORDER", "ONE_STEP_GLOBAL", "LN_RETENTION",
                (_KREF, _EA), ("tau_s", "T_K"), ("T_ref_K",),
                "ln(C/C0) = -k_ref*exp(-(Ea/R)*(1/T - 1/T_ref))*tau",
                f"{_C26} shipped strong rung (first-order + reference-T Arrhenius, one-step global fit)",
                ((("k_ref", 1), ("tau_s", 1)), (("Ea", 1), ("R", -1), ("T_K", -1)),
                 (("Ea", 1), ("R", -1), ("T_ref_K", -1))), _first_arrhenius),
)}
CARD_NAMED_FORMS: tuple[str, ...] = tuple(FORMS)
AI_PROPOSED_FORMS: tuple[str, ...] = ()


def check_form_dimensions(form: KineticForm) -> U.UnitCheck:
    """Every declared dimensionless group of ``form`` has dimension 1 (G24.3, 100 % dimensional consistency)."""
    dims = {p.symbol: U.dimension(p.dimension) for p in form.parameters}
    dims.update({c: U.dimension(COVARIATE_DIMENSIONS[c]) for c in form.covariates})
    dims.update({f: U.dimension(FIXED_DIMENSIONS[f]) for f in form.fixed})
    dims["R"] = U.parse_unit(U.GAS_CONSTANT_UNIT).dimension
    for group in form.dimensionless_groups:
        out = U.ONE
        for sym, power in group:
            if sym not in dims:
                return U.UnitCheck(U.INCONSISTENT, f"{form.name}: unknown symbol {sym!r} in a group")
            out = out * dims[sym] ** power
        if not out.is_dimensionless():
            return U.UnitCheck(U.INCONSISTENT, f"{form.name}: group {group} has dimension {out}")
    # The response of a CONCENTRATION form carries the dimension of its INITIAL_VALUE slot.
    if form.response == "CONCENTRATION" and not any(
            U.dimension(p.dimension) == U.dimension("CONCENTRATION") for p in form.parameters):
        return U.UnitCheck(U.INCONSISTENT, f"{form.name}: no CONCENTRATION parameter for the response")
    return U.UnitCheck(U.CONSISTENT)


def _validate_segments(segments: Sequence[tuple[float, float, float]]) -> np.ndarray:
    seg = np.asarray(segments, dtype=float)
    if seg.ndim != 2 or seg.shape[1] != 3 or seg.shape[0] == 0 or not np.all(np.isfinite(seg)):
        raise ModelError("segments must be a non-empty sequence of (t_start_s, t_end_s, T_K)")
    if seg[0, 0] != 0.0:
        raise ModelError("the temperature schedule must start at tau = 0")
    if np.any(seg[:, 1] <= seg[:, 0]):
        raise ModelError("each segment needs t_end_s > t_start_s")
    if np.any(seg[1:, 0] != seg[:-1, 1]):
        raise ModelError("segments must be contiguous (no gap, no overlap)")
    if np.any(seg[:, 2] <= 0):
        raise ModelError("segment temperatures must be absolute (K, > 0)")
    return seg


def ln_retention_first_order_piecewise(k_ref: float, ea: float, T_ref_K: float,
                                       segments: Sequence[tuple[float, float, float]], tau_s: Array) -> Array:
    """Exact ln(C/C0) = -sum_seg k(T_seg) * overlap(seg, [0, tau]) for a piecewise-constant T schedule."""
    seg = _validate_segments(segments)
    tau = np.asarray(tau_s, dtype=float)
    if tau.ndim != 1 or np.any(~np.isfinite(tau)) or np.any(tau < 0):
        raise ModelError("tau_s must be a finite 1-d array >= 0")
    if np.any(tau > seg[-1, 1]):
        raise ModelError("tau beyond the end of the temperature schedule (no extrapolation)")
    k = arrhenius_rate(k_ref, ea, seg[:, 2], T_ref_K)
    overlap = np.clip(tau[:, None] - seg[None, :, 0], 0.0, (seg[:, 1] - seg[:, 0])[None, :])
    return -(overlap * k[None, :]).sum(axis=1)
