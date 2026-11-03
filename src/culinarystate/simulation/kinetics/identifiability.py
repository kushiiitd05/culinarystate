"""Step 26a identifiability: local sensitivity, profile likelihood, per-parameter verdicts (S159).

Status DRAFT_PENDING_26_0_H4. Pure and deterministic; nothing reads or writes a ledger.

Method (Plan v2 Step 26 card: "scaled-sensitivity / Fisher-information identifiability and condition number",
"profile-likelihood ... CIs", identifiability class per parameter STRUCTURAL / PRACTICAL / PROFILE_FLAT, R-19
negative identifiability results retained):

- Local sensitivity: S = d f / d ln|theta| (theta * d f / d theta; for LOG parameters this is d f / d u),
  rows divided by sigma when given. Numerical rank from the singular values of S with a relative tolerance;
  a parameter loading on a null direction is STRUCTURALLY_NON_IDENTIFIABLE. The reported condition number is
  that of the scaled Fisher information S'S, i.e. (s_max / s_min)^2.
- Profile likelihood: the parameter is held on a grid in the transformed space u (ln theta for LOG) and the
  others re-fitted. Delta = chi^2 difference when sigma is known, n * ln(SSR / SSR_min) otherwise; the CI ends
  where Delta first crosses the chi^2_1 quantile of the level (from the normal quantile, no scipy); the grid
  brackets the crossing and bisection locates it, so the CI does not depend on the grid spacing.
  No crossing inside the caller's scan range = PROFILE_FLAT on that side = PRACTICALLY_NON_IDENTIFIABLE.
- Verdicts: IDENTIFIABLE only when nothing above fires. A NOT_IDENTIFIABLE parameter keeps its raw estimate
  for diagnosis but is excluded from ``reportable_estimates`` and has no closed CI: it is never fitted
  "confidently". A non-converged fit, a profile that finds a lower objective than the fit, or an unknown sigma
  without residual degrees of freedom (n <= p), is UNKNOWN.

All decision settings are caller-supplied ``IdentifiabilityCriteria`` without defaults. The G26-CAL numbers in
the card (condition number < 1e6, >= 5 observations per parameter) are PROPOSED_PILOT and unsigned; they are
not encoded here and become values only through the signed 26.0 pre-registration.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from statistics import NormalDist
from typing import Any

import numpy as np

from culinarystate.simulation.kinetics.fitting import (
    FitResult, Observations, Problem, jacobian, minimise, resolve_backend)
from culinarystate.simulation.kinetics.models import KineticForm

STATUS = "DRAFT_PENDING_26_0_H4"
VERDICTS = ("IDENTIFIABLE", "NOT_IDENTIFIABLE", "UNKNOWN")
CLASSES = ("PRACTICALLY_IDENTIFIABLE", "STRUCTURALLY_NON_IDENTIFIABLE", "PRACTICALLY_NON_IDENTIFIABLE", "UNKNOWN")
REASONS = ("STRUCTURAL_RANK_DEFICIENT", "PROFILE_FLAT_LOWER", "PROFILE_FLAT_UPPER", "ILL_CONDITIONED",
           "TOO_FEW_OBSERVATIONS", "FIT_NOT_CONVERGED", "PROFILE_BELOW_FIT_MINIMUM", "NO_RESIDUAL_DOF_SIGMA_UNKNOWN")
_NULL_LOADING = 1e-6
_BISECT_STEPS = 60


class IdentifiabilityError(ValueError):
    """Refused setting (never a verdict)."""


def chi2_1_quantile(level: float) -> float:
    """Quantile of chi^2 with 1 degree of freedom: z_{(1+level)/2}^2."""
    if not 0.0 < level < 1.0:
        raise IdentifiabilityError("level must be in (0, 1)")
    return NormalDist().inv_cdf((1.0 + level) / 2.0) ** 2


@dataclass(frozen=True)
class IdentifiabilityCriteria:
    profile_level: float                       # e.g. 0.95 (test setting, not a signed value)
    profile_half_width: Mapping[str, float]    # scan half-width per parameter, transformed scale u
    n_profile_points: int                      # grid points per side
    rank_rtol: float                           # singular-value ratio below which a direction is null
    max_condition_number: float | None         # None = not applied
    min_observations_per_parameter: int | None  # None = not applied

    def __post_init__(self) -> None:
        if not 0.0 < self.profile_level < 1.0:
            raise IdentifiabilityError("profile_level must be in (0, 1)")
        if self.n_profile_points < 2:
            raise IdentifiabilityError("n_profile_points must be >= 2")
        if not 0.0 < self.rank_rtol < 1.0:
            raise IdentifiabilityError("rank_rtol must be in (0, 1)")
        if any(not (np.isfinite(v) and v > 0) for v in self.profile_half_width.values()):
            raise IdentifiabilityError("profile half-widths must be finite and > 0")
        if self.max_condition_number is not None and not self.max_condition_number > 0:
            raise IdentifiabilityError("max_condition_number must be > 0 or None")
        if self.min_observations_per_parameter is not None and self.min_observations_per_parameter < 1:
            raise IdentifiabilityError("min_observations_per_parameter must be >= 1 or None")


# ----------------------------------------------------------------------------- local sensitivity
@dataclass(frozen=True)
class LocalSensitivity:
    parameters: tuple[str, ...]
    jacobian: np.ndarray            # d f / d u (u = ln theta for LOG, theta for IDENTITY), unweighted
    scaled: np.ndarray              # d f / d ln|theta|, unweighted
    singular_values: np.ndarray     # of the sigma-weighted scaled matrix
    condition_number: float         # of the scaled Fisher information, (s_max / s_min)^2
    numerical_rank: int
    null_loadings: np.ndarray       # parameters x null directions
    correlation: np.ndarray | None  # from the inverse scaled Fisher information; None when rank-deficient

    def structural_parameters(self) -> tuple[str, ...]:
        if self.null_loadings.size == 0:
            return ()
        hit = np.max(np.abs(self.null_loadings), axis=1) > _NULL_LOADING
        return tuple(p for p, h in zip(self.parameters, hit) if h)


def local_sensitivity(form: KineticForm, theta: Mapping[str, float], covariates: Mapping[str, np.ndarray],
                      fixed: Mapping[str, float] | None = None, *, sigma: np.ndarray | None = None,
                      rank_rtol: float = 1e-8) -> LocalSensitivity:
    """Sensitivities at ``theta``. ``rank_rtol`` default 1e-8 is a numerical tolerance tied to the
    central-difference accuracy (about 1e-10 relative), not a scientific threshold."""
    form.check_inputs(theta, covariates, fixed)
    log = np.array([p.transform == "LOG" for p in form.parameters])
    v = np.array([float(theta[s]) for s in form.symbols])
    u0 = np.where(log, np.log(np.where(log, v, 1.0)), v)

    def f(u: np.ndarray) -> np.ndarray:
        th = {s: float(x) for s, x in zip(form.symbols, np.where(log, np.exp(np.where(log, u, 0.0)), u))}
        return form.predict(th, covariates, fixed)

    J = jacobian(f, u0)
    scale = np.where(log | (v == 0), 1.0, v)
    S = J * scale[None, :]
    Sw = S / np.asarray(sigma, dtype=float)[:, None] if sigma is not None else S
    _, s, Vt = np.linalg.svd(Sw, full_matrices=True)
    smax = float(s.max()) if s.size else 0.0
    rank = int(np.sum(s > rank_rtol * smax)) if smax > 0 else 0
    cond = float("inf") if (s.size < len(v) or s.min() <= 0) else float((smax / s.min()) ** 2)
    null = Vt[rank:].T if rank < len(v) else np.zeros((len(v), 0))
    corr = None
    if rank == len(v):
        C = np.linalg.inv(Sw.T @ Sw)
        d = np.sqrt(np.diag(C))
        corr = C / np.outer(d, d)
    return LocalSensitivity(form.symbols, J, S, s, cond, rank, null, corr)


# ----------------------------------------------------------------------------- profile likelihood
@dataclass(frozen=True)
class Profile:
    parameter: str
    level: float
    threshold: float
    grid_transformed: tuple[float, ...]
    grid_natural: tuple[float, ...]
    delta: tuple[float, ...]
    ci_low: float | None
    ci_high: float | None
    lower_closed: bool
    upper_closed: bool
    below_fit_minimum: bool


def _delta(f: float, f_min: float, n: int, sigma_known: bool) -> float:
    if not np.isfinite(f):
        return float("inf")
    if sigma_known:
        return f - f_min
    return n * float(np.log(max(f, 1e-300) / max(f_min, 1e-300)))


def profile_likelihood(form: KineticForm, obs: Observations, fit: FitResult, parameter: str, *, half_width: float,
                       n_points: int, level: float, backend: str = "auto", max_iter: int = 200) -> Profile:
    if parameter not in form.symbols:
        raise IdentifiabilityError(f"{form.name} has no parameter {parameter!r}")
    if not (np.isfinite(half_width) and half_width > 0) or n_points < 2:
        raise IdentifiabilityError("half_width must be > 0 and n_points >= 2")
    be = resolve_backend(backend)
    prob = Problem(form, obs, fit.fixed)
    j = form.symbols.index(parameter)
    u_hat = np.array([fit.transformed[s] for s in form.symbols])
    free = [i for i in range(len(u_hat)) if i != j]
    thr = chi2_1_quantile(level)
    log = form.spec(parameter).transform == "LOG"

    def solve(uj: float, warm: np.ndarray) -> tuple[float, np.ndarray]:
        def fun(uf: np.ndarray) -> np.ndarray:
            u = u_hat.copy()
            u[j] = uj
            u[free] = uf
            return prob.residual(u)
        best_f, best_u = np.inf, warm
        for u0 in (warm, u_hat[free]):
            uf, fv, _ = minimise(fun, np.array(u0, dtype=float), backend=be, max_iter=max_iter, xtol=1e-14,
                                 ftol=1e-15)
            if fv < best_f:
                best_f, best_u = fv, uf
        return best_f, best_u

    sides: dict[int, list[tuple[float, float, np.ndarray]]] = {}
    for side in (-1, 1):
        warm = u_hat[free].copy()
        pts = []
        for i in range(1, n_points + 1):
            uj = float(u_hat[j] + side * half_width * i / n_points)
            fv, warm = solve(uj, warm)
            pts.append((uj, fv, warm))
        sides[side] = pts
    f_min = fit.objective
    all_f = [fv for pts in sides.values() for _, fv, _ in pts]
    below = any(fv < f_min - 1e-9 * max(abs(f_min), 1.0) for fv in all_f)

    def delta(fv: float) -> float:
        return _delta(fv, f_min, obs.n, fit.sigma_known)

    bounds: dict[int, float | None] = {}
    for side, pts in sides.items():
        inside, inside_warm = float(u_hat[j]), u_hat[free].copy()
        bounds[side] = None
        for uj, fv, uf in pts:
            if delta(fv) > thr:
                # Bisection between the last grid point inside and the first outside (grid-independent CI end).
                lo, hi, warm = inside, uj, inside_warm
                for _ in range(_BISECT_STEPS):
                    mid = 0.5 * (lo + hi)
                    fm, wm = solve(mid, warm)
                    if delta(fm) > thr:
                        hi = mid
                    else:
                        lo, warm = mid, wm
                    if abs(hi - lo) <= 1e-12 * max(1.0, abs(mid)):
                        break
                bounds[side] = 0.5 * (lo + hi)
                break
            inside, inside_warm = uj, uf

    def nat(x: float | None) -> float | None:
        return None if x is None else float(np.exp(x) if log else x)

    grid = [uj for uj, _, _ in reversed(sides[-1])] + [float(u_hat[j])] + [uj for uj, _, _ in sides[1]]
    fs = [fv for _, fv, _ in reversed(sides[-1])] + [f_min] + [fv for _, fv, _ in sides[1]]
    return Profile(parameter, level, thr, tuple(grid), tuple(nat(g) for g in grid),  # type: ignore[misc]
                   tuple(delta(fv) for fv in fs),
                   nat(bounds[-1]), nat(bounds[1]), bounds[-1] is not None, bounds[1] is not None, below)


# ----------------------------------------------------------------------------- verdicts
@dataclass(frozen=True)
class ParameterIdentifiability:
    parameter: str
    verdict: str
    identifiability_class: str
    reasons: tuple[str, ...]
    estimate: float                  # raw estimate, diagnostic only unless verdict IDENTIFIABLE
    ci_low: float | None
    ci_high: float | None
    profile: Profile | None


@dataclass(frozen=True)
class IdentifiabilityReport:
    form_name: str
    fit_id: str
    overall_verdict: str
    parameters: tuple[ParameterIdentifiability, ...]
    condition_number: float | None
    numerical_rank: int | None
    n_obs: int
    criteria: IdentifiabilityCriteria
    status: str = STATUS

    def reportable_estimates(self) -> dict[str, float]:
        return {p.parameter: p.estimate for p in self.parameters if p.verdict == "IDENTIFIABLE"}

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["criteria"] = {**asdict(self.criteria), "profile_half_width": dict(self.criteria.profile_half_width)}
        return out


def _class(reasons: list[str]) -> tuple[str, str]:
    if "FIT_NOT_CONVERGED" in reasons or "PROFILE_BELOW_FIT_MINIMUM" in reasons:
        return "UNKNOWN", "UNKNOWN"
    if "STRUCTURAL_RANK_DEFICIENT" in reasons:
        return "NOT_IDENTIFIABLE", "STRUCTURALLY_NON_IDENTIFIABLE"
    if reasons:
        return "NOT_IDENTIFIABLE", "PRACTICALLY_NON_IDENTIFIABLE"
    return "IDENTIFIABLE", "PRACTICALLY_IDENTIFIABLE"


def assess_identifiability(form: KineticForm, obs: Observations, fit: FitResult, criteria: IdentifiabilityCriteria,
                           *, backend: str = "auto") -> IdentifiabilityReport:
    missing = [s for s in form.symbols if s not in criteria.profile_half_width]
    if missing:
        raise IdentifiabilityError(f"profile_half_width missing for {missing}")
    if fit.form_name != form.name:
        raise IdentifiabilityError("fit and form differ")
    blocking = ("FIT_NOT_CONVERGED",) if not fit.converged else ()
    if not fit.sigma_known and fit.dof <= 0:
        # S159 review R2: with sigma unknown and n <= p the residual scale is not estimable; n*ln(SSR/SSR_min)
        # on an exact fit collapses every profile CI to the estimate, which would read as IDENTIFIABLE.
        blocking += ("NO_RESIDUAL_DOF_SIGMA_UNKNOWN",)
    if blocking:
        params = tuple(ParameterIdentifiability(s, "UNKNOWN", "UNKNOWN", blocking,
                                                float(fit.estimates[s]), None, None, None) for s in form.symbols)
        return IdentifiabilityReport(form.name, fit.fit_id, "UNKNOWN", params, None, None, obs.n, criteria)
    sens = local_sensitivity(form, fit.estimates, obs.covariates, fit.fixed, sigma=obs.sigma,
                             rank_rtol=criteria.rank_rtol)
    structural = set(sens.structural_parameters())
    common: list[str] = []
    if criteria.max_condition_number is not None and not sens.condition_number < criteria.max_condition_number:
        common.append("ILL_CONDITIONED")
    if (criteria.min_observations_per_parameter is not None
            and obs.n < criteria.min_observations_per_parameter * len(form.symbols)):
        common.append("TOO_FEW_OBSERVATIONS")
    out = []
    for s in form.symbols:
        pr = profile_likelihood(form, obs, fit, s, half_width=float(criteria.profile_half_width[s]),
                                n_points=criteria.n_profile_points, level=criteria.profile_level, backend=backend)
        reasons = ["STRUCTURAL_RANK_DEFICIENT"] if s in structural else []
        reasons += ["PROFILE_FLAT_LOWER"] if not pr.lower_closed else []
        reasons += ["PROFILE_FLAT_UPPER"] if not pr.upper_closed else []
        reasons += ["PROFILE_BELOW_FIT_MINIMUM"] if pr.below_fit_minimum else []
        reasons += common
        verdict, cls = _class(reasons)
        closed = verdict == "IDENTIFIABLE"
        out.append(ParameterIdentifiability(s, verdict, cls, tuple(reasons), float(fit.estimates[s]),
                                            pr.ci_low if closed else None, pr.ci_high if closed else None, pr))
    verdicts = {p.verdict for p in out}
    overall = ("NOT_IDENTIFIABLE" if "NOT_IDENTIFIABLE" in verdicts
               else "UNKNOWN" if "UNKNOWN" in verdicts else "IDENTIFIABLE")
    return IdentifiabilityReport(form.name, fit.fit_id, overall, tuple(out), sens.condition_number,
                                 sens.numerical_rank, obs.n, criteria)
