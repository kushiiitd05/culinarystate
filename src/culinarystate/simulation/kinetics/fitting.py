"""Step 26a weighted least-squares fitting with multi-start (S159, DRAFT_PENDING_26_0_H4).

Method (Plan v2 Step 26 card, "Fitting (26a library)"): one-step global nonlinear least squares on the
form's response (ln-retention for the first-order family), positive reparameterisation theta = exp(u) for
LOG parameters, weighted residuals (y - f) / sigma_i when the caller supplies per-observation SDs
(heteroscedastic WLS from reported SD / n is the caller's job), and multi-start from caller-supplied starts.

Backends: ``numpy`` (a Levenberg-Marquardt implementation in this module, always available) and ``scipy``
(``scipy.optimize.least_squares``; optional extra ``step26`` approved in D-050). ``auto`` picks scipy when it
imports. The Jacobian is the same central finite difference for both, so the backends differ only in the
step logic. The backend is part of the fit identity.

What the library never does: invent a start, a bound, a prior or a parameter value; pool across studies;
read or write a ledger. ``fit_id`` is a deterministic content id (``FITRUN-`` + 16 hex of SHA-256 over the
inputs, settings, backend and library version), not a minted ledger id. Not implemented here (card items left
for 26b-26d or later): censored likelihood for ND / <LOD points, hierarchical partial pooling, lab-cluster
bootstrap, the D-optimal design helper.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from culinarystate.simulation.kinetics.models import LIBRARY_VERSION, KineticForm, ModelError

STATUS = "DRAFT_PENDING_26_0_H4"
ORIGINS = ("SYNTHETIC", "KIN_SERIES")
BACKENDS = ("auto", "numpy", "scipy")
_FD_REL = 1e-6


class FitError(ValueError):
    """Refused fit input or setting (never a fit verdict)."""


def _farray(a: Any, name: str) -> np.ndarray:
    arr = np.array(a, dtype=float, copy=True)
    if arr.ndim != 1 or arr.size == 0 or not np.all(np.isfinite(arr)):
        raise FitError(f"{name} must be a non-empty finite 1-d array")
    arr.setflags(write=False)
    return arr


@dataclass(frozen=True)
class Observations:
    """Responses with their covariates. ``sigma`` None = unweighted, residual SD estimated from the fit."""

    response: np.ndarray
    covariates: Mapping[str, np.ndarray]
    sigma: np.ndarray | None
    response_kind: str
    origin: str
    kin_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        y = _farray(self.response, "response")
        cov = {k: _farray(v, f"covariate {k}") for k, v in self.covariates.items()}
        if any(v.shape != y.shape for v in cov.values()):
            raise FitError("every covariate must have one value per response")
        sig = None
        if self.sigma is not None:
            sig = _farray(self.sigma, "sigma")
            if sig.shape != y.shape or np.any(sig <= 0):
                raise FitError("sigma must be > 0 with one value per response")
        if self.origin not in ORIGINS:
            raise FitError(f"origin must be one of {ORIGINS}")
        if self.origin == "KIN_SERIES" and not self.kin_ids:
            raise FitError("KIN_SERIES observations must name their KIN ids")
        object.__setattr__(self, "response", y)
        object.__setattr__(self, "covariates", cov)
        object.__setattr__(self, "sigma", sig)
        object.__setattr__(self, "kin_ids", tuple(self.kin_ids))

    @property
    def n(self) -> int:
        return int(self.response.shape[0])


class Problem:
    """Residual function of a form on observations in the transformed parameter space u."""

    def __init__(self, form: KineticForm, obs: Observations, fixed: Mapping[str, float] | None) -> None:
        if obs.response_kind != form.response:
            raise FitError(f"{form.name} fits {form.response}, observations are {obs.response_kind}")
        self.form, self.obs, self.fixed = form, obs, dict(fixed or {})
        self.log = np.array([p.transform == "LOG" for p in form.parameters])
        self.w = 1.0 / obs.sigma if obs.sigma is not None else np.ones(obs.n)

    def to_u(self, theta: Mapping[str, float]) -> np.ndarray:
        v = np.array([float(theta[s]) for s in self.form.symbols])
        if np.any(v[self.log] <= 0):
            raise FitError("LOG-transformed parameters need values > 0")
        return np.where(self.log, np.log(np.where(self.log, v, 1.0)), v)

    def theta(self, u: np.ndarray) -> dict[str, float]:
        with np.errstate(over="ignore"):
            v = np.where(self.log, np.exp(np.where(self.log, u, 0.0)), u)
        return {s: float(x) for s, x in zip(self.form.symbols, v)}

    def residual(self, u: np.ndarray) -> np.ndarray:
        try:
            with np.errstate(over="ignore", invalid="ignore"):
                pred = self.form.predict(self.theta(u), self.obs.covariates, self.fixed)
        except ModelError:
            return np.full(self.obs.n, np.inf)
        with np.errstate(over="ignore", invalid="ignore"):
            r = (self.obs.response - pred) * self.w
            ok = np.all(np.isfinite(r)) and np.isfinite(r @ r)
        return r if ok else np.full(self.obs.n, np.inf)


def jacobian(fun: Callable[[np.ndarray], np.ndarray], u: np.ndarray) -> np.ndarray:
    """Central finite-difference Jacobian of ``fun`` at ``u`` (relative step 1e-6)."""
    cols = []
    for j in range(u.size):
        h = _FD_REL * max(1.0, abs(u[j]))
        up, dn = u.copy(), u.copy()
        up[j] += h
        dn[j] -= h
        cols.append((fun(up) - fun(dn)) / (2 * h))
    return np.column_stack(cols) if cols else np.zeros((fun(u).size, 0))


def _lm(fun: Callable[[np.ndarray], np.ndarray], u0: np.ndarray, max_iter: int, xtol: float,
        ftol: float) -> tuple[np.ndarray, float, bool]:
    u = u0.astype(float).copy()
    r = fun(u)
    with np.errstate(over="ignore", invalid="ignore"):
        f = float(r @ r)
    if not np.isfinite(f):
        return u, np.inf, False
    lam = 1e-3
    for _ in range(max_iter):
        J = jacobian(fun, u)
        if not np.all(np.isfinite(J)):
            return u, f, False
        g, A = J.T @ r, J.T @ J
        d = np.diag(A).copy()
        floor = max(float(d.max()) if d.size else 1.0, 1.0) * 1e-12
        d[d < floor] = floor
        improved = False
        while lam <= 1e16:
            try:
                step = np.linalg.solve(A + lam * np.diag(d), -g)
            except np.linalg.LinAlgError:
                lam *= 10
                continue
            un = u + step
            rn = fun(un)
            with np.errstate(over="ignore", invalid="ignore"):
                fn = float(rn @ rn)
            if np.isfinite(fn) and fn < f:
                improved = True
                break
            lam *= 10
        if not improved:
            return u, f, True       # no decrease possible: numerical stationary point
        df = f - fn
        u, r, f = un, rn, fn
        lam = max(lam * 0.1, 1e-15)
        if df <= ftol * max(f, 1e-300) or float(np.linalg.norm(step)) <= xtol * (float(np.linalg.norm(u)) + xtol):
            return u, f, True
    return u, f, False


def resolve_backend(backend: str) -> str:
    if backend not in BACKENDS:
        raise FitError(f"backend must be one of {BACKENDS}")
    has = importlib.util.find_spec("scipy") is not None
    if backend == "scipy" and not has:
        raise FitError("scipy backend requested but scipy is not installed (optional extra step26)")
    return ("scipy" if has else "numpy") if backend == "auto" else backend


def minimise(fun: Callable[[np.ndarray], np.ndarray], u0: np.ndarray, *, backend: str, max_iter: int,
             xtol: float, ftol: float) -> tuple[np.ndarray, float, bool]:
    """Minimise sum(fun(u)**2) from u0 with a resolved backend; returns (u, objective, converged)."""
    if u0.size == 0:
        r = fun(u0)
        return u0, float(r @ r), bool(np.all(np.isfinite(r)))
    if backend == "numpy":
        return _lm(fun, u0, max_iter, xtol, ftol)
    from scipy.optimize import least_squares  # optional dependency (D-050)

    r0 = fun(u0)
    if not np.all(np.isfinite(r0)):
        return u0, np.inf, False
    method = "lm" if r0.size >= u0.size else "trf"
    tol = max(min(xtol, ftol), 2.3e-16)
    res = least_squares(fun, u0, jac=lambda u: jacobian(fun, u), method=method, xtol=tol, ftol=tol,
                        gtol=tol, max_nfev=max_iter * 100)
    r = fun(res.x)
    return res.x, float(r @ r), bool(res.status > 0 and np.all(np.isfinite(r)))


def starts_from_bounds(form: KineticForm, bounds: Mapping[str, tuple[float, float]], *, n: int,
                       seed: int) -> list[dict[str, float]]:
    """``n`` deterministic starts inside caller-supplied bounds (log-uniform for LOG parameters)."""
    if n < 1:
        raise FitError("n must be >= 1")
    missing = [s for s in form.symbols if s not in bounds]
    if missing:
        raise FitError(f"bounds missing for {missing}")
    rng = np.random.default_rng(seed)
    cols: dict[str, np.ndarray] = {}
    for p in form.parameters:
        lo, hi = (float(x) for x in bounds[p.symbol])
        if not (np.isfinite(lo) and np.isfinite(hi) and lo < hi):
            raise FitError(f"bounds for {p.symbol} must be finite with low < high")
        if p.transform == "LOG":
            if lo <= 0:
                raise FitError(f"LOG parameter {p.symbol} needs bounds > 0")
            cols[p.symbol] = np.exp(rng.uniform(np.log(lo), np.log(hi), n))
        else:
            cols[p.symbol] = rng.uniform(lo, hi, n)
    return [{s: float(cols[s][i]) for s in form.symbols} for i in range(n)]


def _hex(a: np.ndarray | Sequence[float]) -> list[str]:
    return [float(x).hex() for x in np.asarray(a, dtype=float)]


def _fit_id(payload: Mapping[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "FITRUN-" + hashlib.sha256(blob).hexdigest()[:16]


@dataclass(frozen=True)
class FitResult:
    form_name: str
    estimates: Mapping[str, float]
    transformed: Mapping[str, float]
    objective: float                 # sum of squared (weighted) residuals at the best start
    n_obs: int
    n_params: int
    sigma_known: bool
    converged: bool
    backend: str
    n_starts: int
    n_converged_starts: int
    start_objectives: tuple[float, ...]
    fixed: Mapping[str, float]
    jacobian: np.ndarray = field(repr=False)   # d residual / d u at the estimate
    origin: str
    kin_ids: tuple[str, ...]
    fit_id: str
    library_version: str = LIBRARY_VERSION
    status: str = STATUS

    @property
    def dof(self) -> int:
        return self.n_obs - self.n_params

    @property
    def sigma_hat(self) -> float:
        return float(np.sqrt(self.objective / self.dof)) if self.dof > 0 else float("nan")

    def covariance_transformed(self) -> np.ndarray | None:
        """Gauss-Newton covariance of u; None when J'J is singular to numpy's default rank tolerance, or when
        sigma is unknown and there is no residual degree of freedom to estimate it (S159 review R3)."""
        A = self.jacobian.T @ self.jacobian
        if A.size == 0 or np.linalg.matrix_rank(A) < self.n_params:
            return None
        if not self.sigma_known and self.dof <= 0:
            return None
        s2 = 1.0 if self.sigma_known else (self.objective / self.dof if self.dof > 0 else float("nan"))
        return s2 * np.linalg.inv(A)

    def as_param_provenance(self) -> dict[str, Any]:
        """PARAM ``value_provenance`` block of a PROJECT_REFIT row; synthetic fits never become PARAM rows."""
        if self.origin != "KIN_SERIES":
            raise FitError("only fits on KIN series can provide PARAM provenance")
        return {"source_class": "PROJECT_REFIT", "kin_ids": list(self.kin_ids), "author_fit_ref": None,
                "fit_run_id": self.fit_id, "fitting_library_version": self.library_version}


def fit_least_squares(form: KineticForm, obs: Observations, *, starts: Sequence[Mapping[str, float]],
                      fixed: Mapping[str, float] | None = None, backend: str = "auto", max_iter: int = 200,
                      xtol: float = 1e-14, ftol: float = 1e-15) -> FitResult:
    """Multi-start weighted least squares; the best converged start wins (ties: first start)."""
    be = resolve_backend(backend)
    if not starts:
        raise FitError("at least one start is required; the library has no default start")
    prob = Problem(form, obs, fixed)
    us = []
    for s in starts:
        if set(s) != set(form.symbols):
            raise FitError(f"each start must give exactly {form.symbols}")
        us.append(prob.to_u(s))
        form.check_inputs(s, obs.covariates, fixed)
    runs = [minimise(prob.residual, u0, backend=be, max_iter=max_iter, xtol=xtol, ftol=ftol) for u0 in us]
    order = sorted(range(len(runs)), key=lambda i: (not runs[i][2], runs[i][1], i))
    best_u, best_f, best_ok = runs[order[0]]
    payload = {"library": LIBRARY_VERSION, "form": form.name, "backend": be, "response": _hex(obs.response),
               "covariates": {k: _hex(v) for k, v in sorted(obs.covariates.items())},
               "sigma": None if obs.sigma is None else _hex(obs.sigma),
               "fixed": {k: float(v).hex() for k, v in sorted(prob.fixed.items())},
               "starts": [_hex(u) for u in us], "origin": obs.origin, "kin_ids": list(obs.kin_ids),
               "settings": [max_iter, float(xtol).hex(), float(ftol).hex()]}
    return FitResult(
        form_name=form.name, estimates=prob.theta(best_u),
        transformed={s: float(x) for s, x in zip(form.symbols, best_u)}, objective=best_f, n_obs=obs.n,
        n_params=len(form.symbols), sigma_known=obs.sigma is not None, converged=best_ok, backend=be,
        n_starts=len(runs), n_converged_starts=sum(1 for r in runs if r[2]),
        start_objectives=tuple(r[1] for r in runs), fixed=dict(prob.fixed),
        jacobian=jacobian(prob.residual, best_u), origin=obs.origin, kin_ids=obs.kin_ids, fit_id=_fit_id(payload))
