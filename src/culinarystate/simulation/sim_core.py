"""Step 26b simulator core shared by sim_aa_1 and sim_chl_1 (S159, DRAFT_PENDING_26_0_H4).

Status DRAFT_PENDING_26_0_H4: the 26.0 system selection record (Kush + Parv, transcribing the single 11.D entry)
is not written, the model form / assumptions / M&S limits have no expert sign-off and no PARAM row exists. This
core runs the card's model structures on caller-supplied values only; it is engineering verification, never an
estimate for a recipe user, never evidence, and ``validation_status`` is always NOT_VALIDATED (Step 27 absent).

Contract (Plan v2 Step 26 card, "Architecture detail"; D-027 R-14 / R-15; D-045):
- Every parameter is a required ``ParamValue`` in coherent SI with a PARAM / SYNTHETIC / MODEL_DERIVED id. The core
  holds no parameter value, default, prior, typical value or literature number (no float literal in the module).
- Refusal (``status = SIM_PROHIBITED``) unless an APPDEC record (Step 23a, schema-valid, content id intact) for
  the same event has ``route = SIMULATE`` and ``applicability = APPLICABLE``. UNKNOWN never simulates. Any missing
  input, unexpected parameter, unit / dimension mismatch, matrix-class or size-class mismatch (NO_COMPATIBLE_SET),
  M&S-limit breach (caller-supplied ``MSLimits``; the 26e model card owns the values), a solver that cannot
  represent the problem, or a fixed step beyond its stiffness limit is a refusal with reason codes.
- Both systems are linear in their composition state given the product temperature: x' = M(T_p(t)) x. Bath
  temperature is piecewise constant. T_p = T_b (BATH_EQUALS_PRODUCT) or the card's lumped lag
  dT_p/dt = (T_b - T_p) / tau_h (LUMPED_LAG, flagged T_P_LAG_EXTRAPOLATED until validated, E26-6).
- Solvers: EXPM_PIECEWISE (matrix exponential per constant interval, the analytic reference; bath mode
  only), TRAPEZOID_FIXED (implicit trapezoid, order 2), RK4_FIXED (classical Runge-Kutta, order 4), and with the
  optional scipy extra (D-050) SCIPY_BDF / SCIPY_RADAU / SCIPY_LSODA, which integrate T_p as a state in lag mode.
  Fixed-step methods need a caller stiffness limit on max|lambda| * h; beyond it the run is refused.
- Invariants checked every run: conservation rows of the system (mass balance) and non-negativity, both against
  caller tolerances; a breach is FAILED_INVARIANT and no output is returned. Semigroup residual is reported for
  the analytic solver; the full semigroup test lives in the 26c suite.
- Deterministic: same inputs give byte-identical ``run_sha256``. Provenance: system and structure id, FORM id,
  26a kinetic form names, PARAM ids and origins, APPDEC id, solver metadata and config hash, code and input
  hashes. ``sim_run_id`` stays null: minting belongs to the 26f SIM writer.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from culinarystate.lineage.kinetic_contract import SECONDS_PER_UNIT
from culinarystate.mechanism import applicability as AP
from culinarystate.simulation.kinetics import units as U

STATUS = "DRAFT_PENDING_26_0_H4"
CORE_VERSION = "step26b-sim-core-0.1.0-draft"
CELSIUS_OFFSET_K = Fraction(27315, 100)              # exact: definition of the Celsius scale
SECONDS_PER_MINUTE = Fraction(SECONDS_PER_UNIT["min"])
PARAM_ORIGINS = ("PARAM_RECORD", "SYNTHETIC", "MODEL_DERIVED")
TP_MODES = ("BATH_EQUALS_PRODUCT", "LUMPED_LAG")
CONSTRAINTS = ("POSITIVE", "NONNEGATIVE", "FINITE")
RUN_STATUSES = ("COMPLETED", "SIM_PROHIBITED", "FAILED_INVARIANT")
_PID = {"PARAM_RECORD": re.compile(r"^PARAM-\d{6}$"), "SYNTHETIC": re.compile(r"^SYNTH-PARAM-[A-Z0-9_-]+$"),
        "MODEL_DERIVED": re.compile(r"^DERIVED-[0-9a-f]{16}$")}
_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")
FORM_ID_PATTERN = re.compile(r"^((FORM|MODEL)-\d{6}|SYNTH-FORM-\d{6})$")
_UNV = "AI_RECALLED_UNVERIFIED"
SOLVER_METHODS: Mapping[str, Mapping[str, Any]] = {
    "EXPM_PIECEWISE": {"kind": "ANALYTIC", "stiff_capable": True, "fixed_step": False, "scipy": None, "order": None,
                       "kisao": None, "kisao_status": "NOT_APPLICABLE"},
    "TRAPEZOID_FIXED": {"kind": "FIXED_STEP_IMPLICIT", "stiff_capable": False, "fixed_step": True, "scipy": None,
                        "order": 2, "kisao": None, "kisao_status": "NOT_APPLICABLE"},
    "RK4_FIXED": {"kind": "FIXED_STEP_EXPLICIT", "stiff_capable": False, "fixed_step": True, "scipy": None,
                  "order": 4, "kisao": "KISAO:0000032", "kisao_status": _UNV},
    "SCIPY_BDF": {"kind": "ADAPTIVE_IMPLICIT", "stiff_capable": True, "fixed_step": False, "scipy": "BDF",
                  "order": None, "kisao": "KISAO:0000288", "kisao_status": _UNV},
    "SCIPY_RADAU": {"kind": "ADAPTIVE_IMPLICIT", "stiff_capable": True, "fixed_step": False, "scipy": "Radau",
                    "order": None, "kisao": "KISAO:0000304", "kisao_status": _UNV},
    "SCIPY_LSODA": {"kind": "ADAPTIVE_SWITCHING", "stiff_capable": True, "fixed_step": False, "scipy": "LSODA",
                    "order": None, "kisao": "KISAO:0000088", "kisao_status": _UNV},
}


class SimulationError(ValueError):
    """Structural / programming error in a simulator call (never a data verdict; those are reason codes)."""


def _finite(x: Any, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)) or not math.isfinite(float(x)):
        raise SimulationError(f"{name} must be a finite number")
    return float(x)


def _nonblank(x: Any, name: str) -> None:
    if not isinstance(x, str) or not x.strip():
        raise SimulationError(f"{name} must be a nonblank string")


def _code(x: Any, name: str) -> None:
    if not (isinstance(x, str) and _CODE.match(x)):
        raise SimulationError(f"{name} must be an upper-case code")


def _canon(x: Any) -> Any:
    if isinstance(x, float):
        return x.hex()
    if isinstance(x, Fraction):
        return f"{x.numerator}/{x.denominator}"
    if isinstance(x, np.ndarray):
        return [_canon(v) for v in x.tolist()]
    if isinstance(x, Mapping):
        return {str(k): _canon(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list, tuple)):
        return [_canon(v) for v in x]
    if hasattr(x, "__dataclass_fields__"):
        return {k: _canon(getattr(x, k)) for k in x.__dataclass_fields__}
    return x


def sha256_canonical(x: Any) -> str:
    blob = json.dumps(_canon(x), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ----------------------------------------------------------------------------- inputs
@dataclass(frozen=True)
class ParamValue:
    """One caller-supplied parameter value in coherent SI, traced to a PARAM / SYNTHETIC / MODEL_DERIVED id."""

    param_id: str
    symbol: str
    value_si: float
    unit_si: str
    matrix_class: str
    piece_size_class: str | None
    ph_validity: tuple[float, float] | None
    origin: str

    def __post_init__(self) -> None:
        if self.origin not in PARAM_ORIGINS:
            raise SimulationError(f"origin must be one of {PARAM_ORIGINS}")
        if not (isinstance(self.param_id, str) and _PID[self.origin].match(self.param_id)):
            raise SimulationError(f"param_id {self.param_id!r} does not match the {self.origin} id pattern")
        _nonblank(self.symbol, "symbol")
        object.__setattr__(self, "value_si", _finite(self.value_si, "value_si"))
        _nonblank(self.unit_si, "unit_si")
        _code(self.matrix_class, "matrix_class")
        if self.piece_size_class is not None:
            _code(self.piece_size_class, "piece_size_class")
        if self.ph_validity is not None:
            v = self.ph_validity
            if not (isinstance(v, tuple) and len(v) == 2):
                raise SimulationError("ph_validity is a (low, high) pair or None")
            lo, hi = _finite(v[0], "ph low"), _finite(v[1], "ph high")
            if lo > hi:
                raise SimulationError("ph_validity is inverted")
            object.__setattr__(self, "ph_validity", (lo, hi))


def param_from_record(record: Mapping[str, Any], *, matrix_class: str, piece_size_class: str | None,
                      ph_validity: tuple[float, float] | None) -> ParamValue:
    """ParamValue from a 24a PARAM record with an exact SI value. Calibration eligibility is 26d's question."""
    if record.get("record_type") != "PARAM" or record.get("status") != "ACTIVE":
        raise SimulationError("only an ACTIVE PARAM record can supply a value")
    si = record.get("value_si") or {}
    if si.get("status") != "CONVERTED_EXACT" or si.get("value") is None or not si.get("unit_si"):
        raise SimulationError("PARAM value_si must be CONVERTED_EXACT (no conversion happens here)")
    return ParamValue(record["id"], record["slot_symbol"], si["value"], si["unit_si"], matrix_class,
                      piece_size_class, ph_validity, "PARAM_RECORD")


@dataclass(frozen=True)
class BathSegment:
    t_start_s: float
    t_end_s: float
    T_K: float

    def __post_init__(self) -> None:
        a, b, t = (_finite(getattr(self, n), n) for n in ("t_start_s", "t_end_s", "T_K"))
        if a < 0 or b <= a or t <= 0:
            raise SimulationError("bath segment needs 0 <= t_start < t_end and T_K > 0 (absolute)")
        object.__setattr__(self, "t_start_s", a)
        object.__setattr__(self, "t_end_s", b)
        object.__setattr__(self, "T_K", t)


@dataclass(frozen=True)
class EventConditions:
    """Conditions of one event, already resolved to SI. ``None`` marks an UNKNOWN input (refused, never filled)."""

    event_id: str
    matrix_class: str
    bath_schedule: tuple[BathSegment, ...]
    duration_s: float
    product_temperature_mode: str
    initial_product_temperature_K: float | None
    piece_size_class: str
    system_inputs: Mapping[str, Any]
    carried_codes: Mapping[str, str]
    input_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _nonblank(self.event_id, "event_id")
        _code(self.matrix_class, "matrix_class")
        _code(self.piece_size_class, "piece_size_class")
        sched = self.bath_schedule
        if not (isinstance(sched, tuple) and sched and all(isinstance(s, BathSegment) for s in sched)):
            raise SimulationError("bath_schedule is a non-empty tuple of BathSegment")
        if sched[0].t_start_s != 0 or any(x.t_end_s != y.t_start_s for x, y in zip(sched, sched[1:])):
            raise SimulationError("bath segments must start at 0 and be contiguous")
        d = _finite(self.duration_s, "duration_s")
        if d <= 0:
            raise SimulationError("duration_s must be > 0")
        object.__setattr__(self, "duration_s", d)
        if not isinstance(self.product_temperature_mode, str):
            raise SimulationError("product_temperature_mode must be a string")
        if self.initial_product_temperature_K is not None:
            tp0 = _finite(self.initial_product_temperature_K, "initial_product_temperature_K")
            if tp0 <= 0:
                raise SimulationError("initial_product_temperature_K must be absolute (K, > 0)")
            object.__setattr__(self, "initial_product_temperature_K", tp0)
        if not isinstance(self.system_inputs, Mapping) or not isinstance(self.carried_codes, Mapping):
            raise SimulationError("system_inputs and carried_codes are mappings")
        for k, v in self.carried_codes.items():
            _code(v, f"carried code {k}")
        object.__setattr__(self, "system_inputs", dict(self.system_inputs))
        object.__setattr__(self, "carried_codes", dict(self.carried_codes))
        if not (isinstance(self.input_refs, tuple) and all(isinstance(r, str) and r for r in self.input_refs)):
            raise SimulationError("input_refs is a tuple of nonblank strings")

    @property
    def lag(self) -> bool:
        return self.product_temperature_mode == "LUMPED_LAG"


@dataclass(frozen=True)
class MSLimits:
    """Caller-supplied M&S temperature ceiling (the card's T <= 100 degC ambient; values belong to 26e)."""

    T_max_K: float
    source_ref: str

    def __post_init__(self) -> None:
        t = _finite(self.T_max_K, "T_max_K")
        if t <= 0:
            raise SimulationError("T_max_K must be absolute (K, > 0)")
        object.__setattr__(self, "T_max_K", t)
        _nonblank(self.source_ref, "source_ref")


@dataclass(frozen=True)
class SolverConfig:
    """Solver settings; every setting the method uses is required and the others must be None (no default)."""

    method: str
    output_times_s: tuple[float, ...]
    rtol: float | None
    atol: float | None
    steps_per_interval: int | None
    fixed_step_limit: float | None
    mass_balance_tol: float
    nonnegativity_tol: float

    def __post_init__(self) -> None:
        meta = SOLVER_METHODS.get(self.method)
        if meta is None:
            raise SimulationError(f"method must be one of {tuple(SOLVER_METHODS)}")
        ts = tuple(_finite(t, "output time") for t in self.output_times_s)
        if not ts or ts[0] < 0 or any(b <= a for a, b in zip(ts, ts[1:])):
            raise SimulationError("output_times_s must be non-empty, >= 0 and strictly increasing")
        object.__setattr__(self, "output_times_s", ts)
        adaptive, fixed = meta["scipy"] is not None, bool(meta["fixed_step"])
        for name, used in (("rtol", adaptive), ("atol", adaptive), ("steps_per_interval", fixed),
                           ("fixed_step_limit", fixed)):
            v = getattr(self, name)
            if used and v is None:
                raise SimulationError(f"{self.method} needs {name} (no default)")
            if not used and v is not None:
                raise SimulationError(f"{self.method} does not use {name}")
        if adaptive:
            for name in ("rtol", "atol"):
                if not _finite(getattr(self, name), name) > 0:
                    raise SimulationError(f"{name} must be > 0")
        if fixed:
            if isinstance(self.steps_per_interval, bool) or not isinstance(self.steps_per_interval, int) \
                    or self.steps_per_interval < 1:
                raise SimulationError("steps_per_interval must be an int >= 1")
            if not _finite(self.fixed_step_limit, "fixed_step_limit") > 0:
                raise SimulationError("fixed_step_limit must be > 0")
        for name in ("mass_balance_tol", "nonnegativity_tol"):
            if not _finite(getattr(self, name), name) >= 0:
                raise SimulationError(f"{name} must be >= 0")

    @property
    def sha256(self) -> str:
        return sha256_canonical({"core": CORE_VERSION, "config": self})


# ----------------------------------------------------------------------------- system specification
@dataclass(frozen=True)
class Slot:
    symbol: str
    dimension: str
    si_unit: str
    constraint: str
    description: str


TAU_H_SLOT = Slot("tau_h", "TIME", "s", "POSITIVE", "lumped product-temperature time constant for the size class")


def lag_slots(conditions: EventConditions) -> dict[str, Slot]:
    return {"tau_h": TAU_H_SLOT} if conditions.lag else {}


@dataclass(frozen=True)
class SystemSpec:
    system_id: str
    model_structure_id: str
    card_ref: str
    state_names: tuple[str, ...]
    initial_state: tuple[int, ...]
    conservation: tuple[tuple[int, ...], ...]
    kinetic_forms: tuple[str, ...]
    all_slots: Mapping[str, Slot]
    rate_terms: Mapping[str, tuple[tuple[str, int], ...]]   # each must have dimension TIME^-1
    term_inputs: Mapping[str, str]                          # dimensions of condition inputs in the terms
    dimensionless_groups: tuple[tuple[tuple[str, int], ...], ...]
    slots: Callable[[EventConditions], dict[str, Slot]]
    check_conditions: Callable[[EventConditions], list[str]]
    param_checks: Callable[[EventConditions, Mapping[str, ParamValue]], list[str]]
    rate_matrix: Callable[[Mapping[str, float], EventConditions, float], np.ndarray]
    d_rate_matrix_dT: Callable[[Mapping[str, float], EventConditions, float], np.ndarray]
    outputs: Callable[[Mapping[str, np.ndarray]], dict[str, tuple[float | None, ...]]]
    module_path: Path


@dataclass(frozen=True)
class SimulationRun:
    system_id: str
    status: str
    reasons: tuple[str, ...]
    times_s: tuple[float, ...]
    states: Mapping[str, tuple[float, ...]] | None
    outputs: Mapping[str, tuple[float | None, ...]] | None
    diagnostics: Mapping[str, Any]
    provenance: Mapping[str, Any]
    flags: tuple[str, ...]
    validation_status: str = "NOT_VALIDATED"
    domain_flag: str = "NOT_VALIDATED"
    is_evidence: bool = False
    sim_run_id: None = None
    label: str = STATUS

    @property
    def run_sha256(self) -> str:
        return sha256_canonical(self)


# ----------------------------------------------------------------------------- APPDEC gate (R-15)
def _appdec_bytes(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def appdec_reasons(appdec: Mapping[str, Any] | None, event_id: str) -> list[str]:
    """[] only for a schema-valid, untampered APPDEC with route SIMULATE, APPLICABLE, for this event."""
    if appdec is None:
        return ["APPDEC_MISSING"]
    if not isinstance(appdec, Mapping):
        raise SimulationError("appdec must be an APPDEC record (mapping) or None")
    if AP.appdec_schema_errors(appdec):
        return ["APPDEC_INVALID"]
    body = {k: v for k, v in appdec.items() if k != "appdec_id"}
    if "APPDEC-DRAFT-" + hashlib.sha256(_appdec_bytes(body)).hexdigest()[:16] != appdec["appdec_id"]:
        return ["APPDEC_ID_MISMATCH"]
    out = []
    if appdec["query"]["event_id"] != event_id:
        out.append("APPDEC_OTHER_EVENT")
    if appdec["route"] != "SIMULATE":
        out.append(f"APPDEC_ROUTE_{appdec['route']}")
    if appdec["applicability"] != "APPLICABLE":
        out.append(f"APPDEC_APPLICABILITY_{appdec['applicability']}")
    return out


# ----------------------------------------------------------------------------- numerics
_PADE_M = 13
_PADE_C = tuple(float(Fraction(math.factorial(2 * _PADE_M - k) * math.factorial(_PADE_M),
                               math.factorial(2 * _PADE_M) * math.factorial(k) * math.factorial(_PADE_M - k)))
                for k in range(_PADE_M + 1))
_PADE_NORM = 4      # scaling target ||A / 2^s||_1 <= 4, below the degree-13 backward-error bound (Higham 2005)


def expm(A: np.ndarray) -> np.ndarray:
    """Matrix exponential: scaling and squaring with the [13/13] Pade approximant (exact rational coefficients)."""
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1] or not np.all(np.isfinite(A)):
        raise SimulationError("expm needs a finite square matrix")
    norm = float(np.max(np.sum(np.abs(A), axis=0))) if A.size else 0
    s = max(0, math.ceil(math.log2(norm / _PADE_NORM))) if norm > _PADE_NORM else 0
    B = A / float(2 ** s)
    c = _PADE_C
    eye = np.eye(A.shape[0])
    B2 = B @ B
    B4 = B2 @ B2
    B6 = B4 @ B2
    U = B @ (B6 @ (c[13] * B6 + c[11] * B4 + c[9] * B2) + c[7] * B6 + c[5] * B4 + c[3] * B2 + c[1] * eye)
    V = B6 @ (c[12] * B6 + c[10] * B4 + c[8] * B2) + c[6] * B6 + c[4] * B4 + c[2] * B2 + c[0] * eye
    E = np.linalg.solve(V - U, V + U)
    for _ in range(s):
        E = E @ E
    return E


def scipy_available() -> bool:
    return importlib.util.find_spec("scipy") is not None


def _intervals(conditions: EventConditions, t_last: float, times: Sequence[float]) -> list[tuple[float, float, float]]:
    sched = conditions.bath_schedule
    pts = sorted({float(0), *(s.t_start_s for s in sched if s.t_start_s < t_last), *(t for t in times if t > 0)})
    out = []
    for a, b in zip(pts, pts[1:]):
        seg = next(s for s in sched if s.t_start_s <= a < s.t_end_s)
        out.append((a, b, seg.T_K))
    return out


class _SolverFailure(RuntimeError):
    pass


def _tp(tp_a: float, tb: float, tau: float, dt: float) -> float:
    return tb + (tp_a - tb) * math.exp(-dt / tau)


def _propagate(method: str, spec: SystemSpec, theta: Mapping[str, float], cond: EventConditions, x: np.ndarray,
               tp_a: float, a: float, b: float, tb: float, cfg: SolverConfig) -> tuple[np.ndarray, float]:
    lag = cond.lag
    tau = theta["tau_h"] if lag else 0

    def M(T: float) -> np.ndarray:
        return spec.rate_matrix(theta, cond, T)

    def Tp(t: float) -> float:
        return _tp(tp_a, tb, tau, t - a) if lag else tb

    if method == "EXPM_PIECEWISE":
        return expm(M(tb) * (b - a)) @ x, tb
    if method in ("TRAPEZOID_FIXED", "RK4_FIXED"):
        n = int(cfg.steps_per_interval)       # type: ignore[arg-type]
        h0 = (b - a) / n
        eye = np.eye(x.size)
        Mb = None if lag else M(tb)
        for i in range(n):
            t0 = a + i * h0
            t1 = a + (i + 1) * h0 if i + 1 < n else b
            h = t1 - t0
            A0 = Mb if Mb is not None else M(Tp(t0))
            A1 = Mb if Mb is not None else M(Tp(t1))
            if method == "TRAPEZOID_FIXED":
                x = np.linalg.solve(eye - h / 2 * A1, (eye + h / 2 * A0) @ x)
            else:
                Am = Mb if Mb is not None else M(Tp(t0 + h / 2))
                k1 = A0 @ x
                k2 = Am @ (x + h / 2 * k1)
                k3 = Am @ (x + h / 2 * k2)
                k4 = A1 @ (x + h * k3)
                x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        return x, Tp(b)
    from scipy.integrate import solve_ivp  # optional dependency (D-050)

    sc = SOLVER_METHODS[method]["scipy"]
    if not lag:
        Mb = M(tb)
        sol = solve_ivp(lambda t, y: Mb @ y, (a, b), x, method=sc, rtol=cfg.rtol, atol=cfg.atol,
                        jac=lambda t, y: Mb)
        if not sol.success:
            raise _SolverFailure(sol.message)
        return sol.y[:, -1].copy(), tb
    n = x.size

    def fun(t: float, y: np.ndarray) -> np.ndarray:
        return np.concatenate([M(y[n]) @ y[:n], [(tb - y[n]) / tau]])

    def jac(t: float, y: np.ndarray) -> np.ndarray:
        J = np.zeros((n + 1, n + 1))
        J[:n, :n] = M(y[n])
        J[:n, n] = spec.d_rate_matrix_dT(theta, cond, y[n]) @ y[:n]
        J[n, n] = -1 / tau
        return J

    sol = solve_ivp(fun, (a, b), np.concatenate([x, [tp_a]]), method=sc, rtol=cfg.rtol, atol=cfg.atol, jac=jac)
    if not sol.success:
        raise _SolverFailure(sol.message)
    return sol.y[:n, -1].copy(), float(sol.y[n, -1])


def _rates(spec: SystemSpec, theta: Mapping[str, float], cond: EventConditions,
           temps: Sequence[float]) -> tuple[float, float | None]:
    """max |lambda| and stiffness ratio max/min over non-conserved modes at the extreme temperatures."""
    n_cons = len(spec.conservation)
    mags: list[float] = []
    rest: list[float] = []
    for T in temps:
        lam = np.sort(np.abs(np.linalg.eigvals(spec.rate_matrix(theta, cond, T))))
        mags += lam.tolist()
        rest += lam[n_cons:].tolist()
    if cond.lag:
        mags.append(1 / theta["tau_h"])
        rest.append(1 / theta["tau_h"])
    mx = max(mags) if mags else 0
    mn = min(rest) if rest else 0
    return float(mx), (float(mx / mn) if mn > 0 else None)


# ----------------------------------------------------------------------------- checks
def _param_reasons(spec: SystemSpec, cond: EventConditions, params: Sequence[ParamValue]) -> tuple[list[str], dict]:
    slots = spec.slots(cond)
    by: dict[str, ParamValue] = {}
    out: list[str] = []
    for pv in params:
        if pv.symbol in by:
            out.append(f"PARAM_DUPLICATE_{pv.symbol.upper()}")
        else:
            by[pv.symbol] = pv
    out += [f"PARAM_MISSING_{s.upper()}" for s in slots if s not in by]
    out += [f"PARAM_UNEXPECTED_{s.upper()}" for s in by if s not in slots]
    for sym, slot in slots.items():
        pv = by.get(sym)
        if pv is None:
            continue
        tag = sym.upper()
        chk = U.check_unit(pv.unit_si, slot.dimension)
        parsed = U.parse_unit(pv.unit_si) if chk.verdict == U.CONSISTENT else None
        if parsed is None or parsed.factor_to_si != 1:
            out.append(f"PARAM_UNIT_{tag}")
        v = pv.value_si
        if (slot.constraint == "POSITIVE" and not v > 0) or (slot.constraint == "NONNEGATIVE" and not v >= 0):
            out.append(f"PARAM_CONSTRAINT_{tag}")
        if pv.matrix_class != cond.matrix_class:
            out.append(f"NO_COMPATIBLE_SET_{tag}")
        if sym == "tau_h" and pv.piece_size_class != cond.piece_size_class:
            out.append("NO_COMPATIBLE_SIZE_CLASS_TAU_H")
    out += spec.param_checks(cond, by)
    return out, by


def _condition_reasons(cond: EventConditions, cfg: SolverConfig, limits: MSLimits) -> list[str]:
    out: list[str] = []
    mode = cond.product_temperature_mode
    if mode not in TP_MODES:
        out.append("INPUT_INVALID_PRODUCT_TEMPERATURE_MODE")
    elif cond.lag and cond.initial_product_temperature_K is None:
        out.append("INPUT_MISSING_INITIAL_PRODUCT_TEMPERATURE")
    elif not cond.lag and cond.initial_product_temperature_K is not None:
        out.append("INPUT_UNEXPECTED_INITIAL_PRODUCT_TEMPERATURE")
    if cond.bath_schedule[-1].t_end_s < cond.duration_s:
        out.append("DURATION_BEYOND_SCHEDULE")
    if cfg.output_times_s[-1] > cond.duration_s:
        out.append("OUTPUT_TIME_BEYOND_DURATION")
    temps = [s.T_K for s in cond.bath_schedule if s.t_start_s < cond.duration_s]
    if cond.initial_product_temperature_K is not None:
        temps.append(cond.initial_product_temperature_K)
    if any(t > limits.T_max_K for t in temps):
        out.append("OUT_OF_MS_LIMITS_TEMPERATURE")
    if cfg.method == "EXPM_PIECEWISE" and cond.lag:
        out.append("SOLVER_NOT_APPLICABLE_TIME_VARYING")
    if SOLVER_METHODS[cfg.method]["scipy"] is not None and not scipy_available():
        out.append("SOLVER_UNAVAILABLE_SCIPY")
    return out


def _code_sha256(spec: SystemSpec) -> str:
    from culinarystate.simulation.kinetics import models
    h = hashlib.sha256()
    for p in (Path(__file__), spec.module_path, Path(models.__file__)):
        h.update(p.read_bytes())
    return h.hexdigest()


def _solver_meta(method: str) -> dict[str, Any]:
    meta = dict(SOLVER_METHODS[method])
    meta["method"] = method
    if meta["scipy"] is not None and scipy_available():
        import scipy
        meta["scipy_version"] = scipy.__version__
    else:
        meta["scipy_version"] = None
    return meta


# ----------------------------------------------------------------------------- run
PROVENANCE_KEYS = ("system_id", "model_structure_id", "card_ref", "form_id", "kinetic_forms", "param_ids",
                   "param_origins", "appdec_id", "condition_source", "event_id", "input_refs", "carried_codes",
                   "ms_limits_ref", "solver", "solver_config_sha256", "code_sha256", "core_version", "inputs_sha256",
                   "recipe_event_id", "simulation_input_sha256")
DIAGNOSTIC_KEYS = ("mass_balance_residual", "min_state", "max_rate_per_s", "stiffness_ratio", "semigroup_residual",
                   "n_intervals")


def run(spec: SystemSpec, conditions: EventConditions, params: Sequence[ParamValue], *,
        appdec: Mapping[str, Any] | None, solver: SolverConfig, ms_limits: MSLimits, form_id: str,
        context: Mapping[str, Any] | None = None) -> SimulationRun:
    """Run one system on one event, or refuse with reason codes. Pure and deterministic."""
    if not isinstance(conditions, EventConditions):
        raise SimulationError("conditions must be EventConditions")
    params = tuple(params)
    if not all(isinstance(p, ParamValue) for p in params):
        raise SimulationError("params must be ParamValue instances")
    if not isinstance(solver, SolverConfig) or not isinstance(ms_limits, MSLimits):
        raise SimulationError("solver must be SolverConfig and ms_limits MSLimits")
    if not (isinstance(form_id, str) and FORM_ID_PATTERN.match(form_id)):
        raise SimulationError("form_id must be FORM-/MODEL-###### (24f OPEN) or SYNTH-FORM-######")
    reasons = appdec_reasons(appdec, conditions.event_id)
    reasons += _condition_reasons(conditions, solver, ms_limits)
    reasons += spec.check_conditions(conditions)
    preasons, by = _param_reasons(spec, conditions, params)
    reasons += preasons
    ctx = dict(context or {})
    flags = sorted({f"{p.origin}_PARAMETERS" for p in params if p.origin != "PARAM_RECORD"}
                   | ({"T_P_LAG_EXTRAPOLATED"} if conditions.lag else set()))
    prov = {
        "system_id": spec.system_id, "model_structure_id": spec.model_structure_id, "card_ref": spec.card_ref,
        "form_id": form_id, "kinetic_forms": list(spec.kinetic_forms),
        "param_ids": sorted(p.param_id for p in params), "param_origins": sorted({p.origin for p in params}),
        "appdec_id": appdec.get("appdec_id") if isinstance(appdec, Mapping) else None,
        "condition_source": appdec.get("condition_source") if isinstance(appdec, Mapping) else None,
        "event_id": conditions.event_id, "input_refs": list(conditions.input_refs),
        "carried_codes": dict(conditions.carried_codes), "ms_limits_ref": ms_limits.source_ref,
        "solver": _solver_meta(solver.method), "solver_config_sha256": solver.sha256,
        "code_sha256": _code_sha256(spec), "core_version": CORE_VERSION,
        "inputs_sha256": sha256_canonical({"system": spec.system_id, "conditions": conditions, "form_id": form_id,
                                           "params": sorted(params, key=lambda p: (p.symbol, p.param_id)),
                                           "ms_limits": ms_limits, "context": ctx}),
        "recipe_event_id": ctx.get("recipe_event_id"), "simulation_input_sha256": ctx.get("simulation_input_sha256"),
    }
    diag: dict[str, Any] = {k: None for k in DIAGNOSTIC_KEYS}

    def refuse(status: str, why: Sequence[str]) -> SimulationRun:
        return SimulationRun(spec.system_id, status, tuple(sorted(set(why))), solver.output_times_s, None, None,
                             diag, prov, tuple(flags))

    if reasons:
        return refuse("SIM_PROHIBITED", reasons)
    theta = {s: p.value_si for s, p in by.items()}
    times = solver.output_times_s
    ivals = _intervals(conditions, times[-1], times)
    temps = sorted({tb for _, _, tb in ivals} | ({conditions.initial_product_temperature_K} if conditions.lag
                                                 else set()) | {conditions.bath_schedule[0].T_K})
    diag["max_rate_per_s"], diag["stiffness_ratio"] = _rates(spec, theta, conditions, temps)
    diag["n_intervals"] = len(ivals)
    if SOLVER_METHODS[solver.method]["fixed_step"] and ivals:
        h_max = max(b - a for a, b, _ in ivals) / int(solver.steps_per_interval)  # type: ignore[arg-type]
        if diag["max_rate_per_s"] * h_max > float(solver.fixed_step_limit):      # type: ignore[arg-type]
            return refuse("SIM_PROHIBITED", ["STIFF_FOR_FIXED_STEP"])
    x = np.array(spec.initial_state, dtype=float)
    x0 = x.copy()
    tp = conditions.initial_product_temperature_K if conditions.lag else conditions.bath_schedule[0].T_K
    rows, tps = [], []
    if times[0] == 0:
        rows.append(x.copy())
        tps.append(float(tp))
    try:
        for a, b, tb in ivals:
            x, tp = _propagate(solver.method, spec, theta, conditions, x, float(tp), a, b, tb, solver)
            if b in times:
                rows.append(x.copy())
                tps.append(float(tp))
    except (_SolverFailure, np.linalg.LinAlgError, FloatingPointError) as exc:
        diag["solver_message"] = str(exc)
        return refuse("FAILED_INVARIANT", ["SOLVER_FAILED"])
    X = np.array(rows)
    C = np.array(spec.conservation, dtype=float)
    if not np.all(np.isfinite(X)):
        return refuse("FAILED_INVARIANT", ["NON_FINITE_STATE"])
    diag["mass_balance_residual"] = float(np.max(np.abs(X @ C.T - C @ x0)))
    diag["min_state"] = float(np.min(X))
    if solver.method == "EXPM_PIECEWISE" and ivals:
        a, b, tb = ivals[0]
        Mx = spec.rate_matrix(theta, conditions, tb)
        half = expm(Mx * ((b - a) / 2))
        diag["semigroup_residual"] = float(np.max(np.abs(expm(Mx * (b - a)) - half @ half)))
    bad = []
    if diag["mass_balance_residual"] > solver.mass_balance_tol:
        bad.append("MASS_BALANCE_VIOLATED")
    if diag["min_state"] < -solver.nonnegativity_tol:
        bad.append("NEGATIVE_STATE")
    if bad:
        return refuse("FAILED_INVARIANT", bad)
    states = {n: X[:, i] for i, n in enumerate(spec.state_names)}
    outputs = dict(spec.outputs(states))
    if conditions.lag:
        outputs["T_p_K"] = tuple(tps)
    return SimulationRun(spec.system_id, "COMPLETED", (), times,
                         {n: tuple(float(v) for v in col) for n, col in states.items()}, outputs, diag, prov,
                         tuple(flags))


def prohibited(spec: SystemSpec, reasons: Sequence[str], solver: SolverConfig, *, form_id: str,
               appdec: Mapping[str, Any] | None, context: Mapping[str, Any]) -> SimulationRun:
    """A SIM_PROHIBITED record for a call refused before EventConditions exist (for example from 26g)."""
    if not reasons:
        raise SimulationError("a prohibited run needs at least one reason")
    dec = appdec if isinstance(appdec, Mapping) else {}
    prov = {k: None for k in PROVENANCE_KEYS}
    prov.update({"system_id": spec.system_id, "model_structure_id": spec.model_structure_id,
                 "card_ref": spec.card_ref, "form_id": form_id, "kinetic_forms": list(spec.kinetic_forms),
                 "appdec_id": dec.get("appdec_id"), "condition_source": dec.get("condition_source"),
                 "solver": _solver_meta(solver.method), "solver_config_sha256": solver.sha256,
                 "code_sha256": _code_sha256(spec), "core_version": CORE_VERSION,
                 "recipe_event_id": context.get("recipe_event_id"),
                 "simulation_input_sha256": context.get("simulation_input_sha256")})
    diag = {k: None for k in DIAGNOSTIC_KEYS}
    return SimulationRun(spec.system_id, "SIM_PROHIBITED", tuple(sorted(set(reasons))), solver.output_times_s, None,
                         None, diag, prov, ())


def ln_or_none(values: np.ndarray) -> tuple[float | None, ...]:
    return tuple(float(math.log(v)) if v > 0 else None for v in np.asarray(values, dtype=float))


__all__ = ["BathSegment", "EventConditions", "MSLimits", "ParamValue", "SimulationError", "SimulationRun",
           "SolverConfig", "Slot", "SystemSpec", "appdec_reasons", "expm", "lag_slots", "param_from_record", "prohibited", "run"]
