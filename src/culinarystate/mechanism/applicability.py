"""Step 23a mechanism applicability engine: K3 gates, reason codes, route rule, APPDEC records (S158).

Status DRAFT_PENDING_21b_22a_H4: MECH seed entries (21b) and process signatures (22a) are drafts, no reviewed
MECH entry exists, the 22c case set is not sealed and no threshold is signed. This is engine verification on
constructed cases (spine 23a: "no COND consumed"). 23b, scientific application to COND-bearing rows and recipe
events, is BLOCKED (07.A gate, 15b DATA-EVIDENCE v1): ``evaluate(mode="23b")`` raises.

Design (Plan Step 23 card, 23-M; D-027 R-15; R-05; R-20)
- Decision unit: (entity_version_id, event_id, target). Gate verdicts are APPLICABLE / NOT_APPLICABLE / UNKNOWN
  combined by Kleene strong conjunction (any NA -> NA, else any U -> U, else A). NOT_REQUIRED marks G0 / G2 / G9.
- G1 event resolution; G2 deterministic changes referenced from 22a signatures, never recomputed; G3 candidate
  mechanisms from matching 22a signatures whose candidate effects name the query target; G4 per mechanism:
  refusal of entries that ``consumable_for_applicability`` rejects (UNKNOWN with the reasons propagated),
  matrix scope, preconditions, NECESSARY / INHIBITING gates, inhibitors (PARTIAL -> QUALITATIVE only);
  MODULATING gates and catalysts never change G4 (rule M-1) but a missing input makes G7 UNKNOWN.
  Target-level G4: A if some candidate is A, else U if some is U, else NA. G5 competition: >= 2 A without a
  joint FORM -> NA; one A plus an U competitor -> U. G6 / G8 (Steps 24 / 25 absent) and the FORM-input part of
  G7 are UNKNOWN unless the constructed case states them (``CaseGate``). G0 is a case-stated evidence pre-check.
- No imputation: an axis value is a point, a closed interval, a category or None (UNKNOWN); it must match the
  gate's CV id, location, unit and basis exactly; no conversion, default, midpoint or typical value. A value
  beyond an OPEN_STATED or NOT_REPORTED side, or straddling a bound, is UNKNOWN.
- Route rule (SIMULATE is the narrowest branch): G0 DIRECT -> DIRECT, BRACKETING -> INTERPOLATE (cross-check
  SIMULATE only under the SIMULATE conditions); all of G1, G4..G8 APPLICABLE, no partial inhibition, domain
  IN_VALIDATION_DOMAIN and safety NO -> SIMULATE; same but domain IN_CALIBRATION_ONLY / EXTRAPOLATED_WITHIN_LIMITS
  -> QUALITATIVE + RESEARCH_ONLY / EXTRAPOLATED label; G4 A with one known sign -> QUALITATIVE; a missing input the
  case marks user-observable -> ASK (value of information not computed; design only); else UNKNOWN.
  Invariant (property-tested, and in the APPDEC schema): no UNKNOWN or NOT_APPLICABLE in G1 / G4..G8 reaches
  SIMULATE. SIMULATE is a design label: no simulator runs and sim_run_id is null.
- Output: an APPDEC record (registry/schemas/APPDEC.draft_v1.schema.json), validated before it is returned,
  with a content id; ``to_applicability_binding`` projects it onto the S156 26g ApplicabilityBinding.
"""
from __future__ import annotations

import csv
import functools
import hashlib
import io
import json
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from culinarystate.mechanism import mech_contract as MC
from culinarystate.mechanism import process_signatures as PS

STATUS = "DRAFT_PENDING_21b_22a_H4"
ENGINE_VERSION = "step23a-engine-0.1.0-draft"
APPDEC_SCHEMA_VERSION = "0.1.0-draft"
MODE_23A = "23a"
BLOCKED_MODES = {"23b": "23b BLOCKED: scientific use needs the Step-07 gate (07.A, pooled kappa >= 0.80 and no "
                        "systematic critical-field failure) validly passed and a frozen DATA-EVIDENCE v1 (15b)"}
A, NA, U = MC.APPLICABLE, MC.NOT_APPLICABLE, MC.UNKNOWN
VERDICTS = (A, NA, U)
NOT_REQUIRED = "NOT_REQUIRED"
ROUTES = ("DIRECT", "INTERPOLATE", "SIMULATE", "QUALITATIVE", "ASK", "UNKNOWN")
DOMAIN_FLAGS = ("IN_VALIDATION_DOMAIN", "IN_CALIBRATION_ONLY", "EXTRAPOLATED_WITHIN_LIMITS", "SIM_PROHIBITED", "UNKNOWN")
EVIDENCE_PRECHECK = ("DIRECT", "BRACKETING", "NONE", "NOT_EVALUATED")
SAFETY = ("YES", "NO", "UNKNOWN")
CONSTRUCTED_CASE = "CONSTRUCTED_CASE"
SIM_GATES = ("G1", "G4", "G5", "G6", "G7", "G8")

_ROOT = Path(__file__).resolve().parents[3]
APPDEC_SCHEMA_PATH = _ROOT / "registry" / "schemas" / "APPDEC.draft_v1.schema.json"
REASON_REGISTRY_PATH = _ROOT / "registry" / "mechanisms" / "applicability_reason_code_registry_v1_DRAFT.csv"
ROUTE_ENUM_PATH = _ROOT / "registry" / "mechanisms" / "route_enum_v1_DRAFT.csv"
_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")


class ApplicabilityError(ValueError):
    """Refused input or mode (programming / contract error, never a verdict)."""


@functools.cache
def _reason_rows() -> tuple[dict[str, str], ...]:
    return tuple(csv.DictReader(io.StringIO(REASON_REGISTRY_PATH.read_text(encoding="utf-8"))))


REASON_CODES: dict[str, str] = {r["reason_code"]: r["gate"] for r in _reason_rows()}
_CASE_GATE_CODES = {"G6": frozenset({"NO_FORM", "ASSUMPTION_VIOLATED"}), "G7": frozenset({"INPUT_UNOBSERVED"}),
                    "G8": frozenset({"NO_COMPATIBLE_PARAM", "PARAM_UNCONFIRMABLE"})}
_CASE_GATE_DEFAULT = {"G6": "NO_FORM", "G7": "INPUT_UNOBSERVED", "G8": "PARAM_UNCONFIRMABLE"}


@functools.cache
def _registry_versions() -> dict[str, str]:
    return {"engine": ENGINE_VERSION, "mech_schema": MC.SCHEMA_VERSION, "signature_contract": PS.CONTRACT_VERSION,
            "reason_code_registry_sha256": hashlib.sha256(REASON_REGISTRY_PATH.read_bytes()).hexdigest(),
            "route_enum_sha256": hashlib.sha256(ROUTE_ENUM_PATH.read_bytes()).hexdigest()}


@functools.cache
def _code_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@functools.cache
def _appdec_validator() -> Draft202012Validator:
    schema = json.loads(APPDEC_SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator({k: v for k, v in schema.items() if k != "$id"})


@functools.cache
def _cv_rows() -> tuple[dict[str, str], ...]:
    return tuple(MC.read_cv_rows())


@functools.cache
def _effect_rows() -> tuple[dict[str, str], ...]:
    return tuple(MC.read_effect_rows())


def appdec_schema_errors(record: Mapping[str, Any]) -> list[str]:
    return sorted("/".join(map(str, e.absolute_path)) + " :: " + e.message
                  for e in _appdec_validator().iter_errors(record))


def k3_and(verdicts: Iterable[str]) -> str:
    vs = list(verdicts)
    return NA if NA in vs else (U if U in vs else A)


def _canon(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


# ----------------------------------------------------------------------------- inputs
def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


@dataclass(frozen=True)
class AxisValue:
    """A case-stated condition value. value: number, (lo, hi), upper-case category, or None (= UNKNOWN)."""

    cv_id: str
    location: str
    value: float | tuple[float, float] | str | None
    unit: str | None = None
    basis: str = "NOT_APPLICABLE"
    source_kind: str = CONSTRUCTED_CASE
    source_ref: str = ""

    def __post_init__(self) -> None:
        v = self.value
        if v is None or _is_num(v):
            pass
        elif isinstance(v, tuple):
            if len(v) != 2 or not all(_is_num(x) for x in v) or v[0] > v[1]:
                raise ApplicabilityError(f"{self.cv_id}: an interval is (lo, hi) with finite numbers and lo <= hi")
        elif isinstance(v, str):
            if not _CODE.match(v):
                raise ApplicabilityError(f"{self.cv_id}: a category is an upper-case code (no free text)")
        else:
            raise ApplicabilityError(f"{self.cv_id}: value must be a finite number, an interval, a category or None")

    @property
    def token(self) -> str:
        return f"axis:{self.cv_id}@{self.location}"

    def to_canonical(self) -> dict[str, Any]:
        v = list(self.value) if isinstance(self.value, tuple) else self.value
        return {"cv_id": self.cv_id, "location": self.location, "value": v, "unit": self.unit, "basis": self.basis,
                "source_kind": self.source_kind, "source_ref": self.source_ref}


@dataclass(frozen=True)
class CaseGate:
    """A constructed case's statement of G6 / G7 (FORM inputs) / G8 while Steps 24 / 25 do not exist."""

    verdict: str
    reasons: tuple[str, ...] = ()
    ref: str | None = None


@dataclass(frozen=True)
class ApplicabilityQuery:
    case_id: str
    entity_version_id: str
    event_id: str
    target_svar_id: str | None
    target_state_key: str | None
    process_id: str | None
    event_resolved: bool = True
    modifiers: Mapping[str, str | None] = field(default_factory=dict)
    matrix: str | None = None
    states: Mapping[str, str | None] = field(default_factory=dict)
    axes: tuple[AxisValue, ...] = ()
    evidence_precheck: str = "NOT_EVALUATED"
    formula: CaseGate | None = None
    observability: CaseGate | None = None
    parameters: CaseGate | None = None
    domain_flag: str = "UNKNOWN"
    safety_critical: str = "UNKNOWN"
    user_observable: tuple[str, ...] = ()
    joint_form_ref: str | None = None

    def __post_init__(self) -> None:
        for name in ("case_id", "entity_version_id", "event_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ApplicabilityError(f"{name} must be non-blank")
        if not (self.target_svar_id or self.target_state_key):
            raise ApplicabilityError("the query needs a target svar_id or state_key")
        for name, allowed in (("evidence_precheck", EVIDENCE_PRECHECK), ("domain_flag", DOMAIN_FLAGS),
                              ("safety_critical", SAFETY)):
            if getattr(self, name) not in allowed:
                raise ApplicabilityError(f"{name} must be one of {allowed}")
        if not all(isinstance(a, AxisValue) for a in self.axes):
            raise ApplicabilityError("axes must be AxisValue instances")

    def to_canonical(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "entity_version_id": self.entity_version_id, "event_id": self.event_id,
                "target": {"svar_id": self.target_svar_id, "state_key": self.target_state_key},
                "process_id": self.process_id, "event_resolved": self.event_resolved,
                "matrix": self.matrix, "modifiers": dict(sorted(self.modifiers.items()))}

    def full_canonical(self) -> dict[str, Any]:
        def cg(x: CaseGate | None) -> Any:
            return None if x is None else {"verdict": x.verdict, "reasons": list(x.reasons), "ref": x.ref}
        return {**self.to_canonical(), "states": dict(sorted(self.states.items())),
                "axes": [a.to_canonical() for a in self.axes], "evidence_precheck": self.evidence_precheck,
                "formula": cg(self.formula), "observability": cg(self.observability),
                "parameters": cg(self.parameters), "domain_flag": self.domain_flag,
                "safety_critical": self.safety_critical, "user_observable": sorted(self.user_observable),
                "joint_form_ref": self.joint_form_ref}


# ----------------------------------------------------------------------------- per-mechanism evaluation (G4 + G7 parts)
@dataclass
class _Part:
    verdict: str = A
    reasons: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    obs_reasons: list[str] = field(default_factory=list)
    qualitative_only: bool = False

    def add(self, verdict: str, *reasons: str, missing: str | None = None) -> None:
        self.verdict = k3_and([self.verdict, verdict])
        if verdict != A:
            self.reasons += reasons
        if missing:
            self.missing.append(missing)

    def unobserved(self, reason: str, missing: str | None = None) -> None:
        self.obs_reasons.append(reason)
        if missing:
            self.missing.append(missing)


@dataclass(frozen=True)
class MechanismVerdict:
    mechanism_key: str
    mechanism_id: str
    signature_keys: tuple[str, ...]
    consumable: bool
    refusal_reasons: tuple[str, ...]
    verdict: str
    reasons: tuple[str, ...]
    directions: tuple[str, ...]
    qualitative_only: bool
    missing_inputs: tuple[str, ...]
    observability_reasons: tuple[str, ...]
    competition_reasons: tuple[str, ...]

    def to_canonical(self) -> dict[str, Any]:
        return {"mechanism_key": self.mechanism_key, "mechanism_id": self.mechanism_id,
                "signature_keys": list(self.signature_keys), "consumable": self.consumable,
                "refusal_reasons": list(self.refusal_reasons), "verdict": self.verdict, "reasons": list(self.reasons),
                "directions": list(self.directions), "qualitative_only": self.qualitative_only,
                "missing_inputs": list(self.missing_inputs)}


def _state_key(ref: Mapping[str, Any]) -> str:
    return ref["state_key"] if ref["state_key"] is not None else ref["svar_id"]


def _state(q: ApplicabilityQuery, ref: Mapping[str, Any]) -> str | None:
    v = q.states.get(_state_key(ref))
    return None if v is None or str(v).upper() == "UNKNOWN" else v


def _scope_verdict(scope: Mapping[str, Any], matrix: str | None) -> tuple[str, str | None]:
    if matrix is None:
        return U, "MATRIX_UNKNOWN"
    if matrix in {i["ref"] for i in scope["excluded"]}:
        return NA, "MATRIX_EXCLUDED"
    if matrix in {i["ref"] for i in scope["included"]}:
        return A, None
    return U, "MATRIX_UNLISTED"


def _side(b: Mapping[str, Any], lo: float, hi: float, lower: bool) -> str:
    """One side of a window against [lo, hi]: A fully inside, NA fully outside a STATED side, else U."""
    if b["status"] == "NOT_REPORTED":
        return U
    x, inc = b["value"], b["inclusive"]
    def inside(v: float) -> bool:
        return (v >= x if inc else v > x) if lower else (v <= x if inc else v < x)
    if inside(lo if lower else hi):
        return A
    if b["status"] == "STATED" and not inside(hi if lower else lo):
        return NA
    return U


def window_verdict(interval: Mapping[str, Any], value: float | tuple[float, float]) -> str:
    lo, hi = value if isinstance(value, tuple) else (value, value)
    return k3_and([_side(interval["min"], lo, hi, True), _side(interval["max"], lo, hi, False)])


def _axis_window(g: Mapping[str, Any], q: ApplicabilityQuery) -> tuple[str, str | None]:
    """Window verdict for a gate (A = inside / allowed) and the reason when not decided."""
    vals = [a for a in q.axes if a.cv_id == g["cv_id"] and a.location == g["location"]]
    if not vals or all(a.value is None for a in vals):
        return U, "MISSING"
    if len({json.dumps(a.to_canonical(), sort_keys=True) for a in vals}) > 1:
        return U, "AXIS_CONFLICT"
    a = vals[0]
    if a.value is None:
        return U, "MISSING"
    if g["basis"] != "NOT_APPLICABLE" and a.basis != g["basis"]:
        return U, "AXIS_BASIS_MISMATCH"
    if g["domain_kind"] == "NUMERIC_INTERVAL":
        if isinstance(a.value, str):
            return U, "AXIS_TYPE_MISMATCH"
        if a.unit != g["interval"]["unit"]:
            return U, "AXIS_UNIT_MISMATCH"
        w = window_verdict(g["interval"], a.value)
        return w, (None if w == A else "NECESSARY_AXIS_OUTSIDE" if w == NA else "AXIS_NOT_DECIDABLE")
    if not isinstance(a.value, str):
        return U, "AXIS_TYPE_MISMATCH"
    cats = g["categories"]
    if a.value in cats["allowed"]:
        return A, None
    if a.value in cats["excluded"]:
        return NA, "CATEGORY_EXCLUDED"
    return U, "CATEGORY_UNLISTED"


def _present(part: _Part, extent: str, *, item_status: str = "ACCEPTED") -> None:
    """An inhibitor / mitigator is present: COMPLETE -> NA, PARTIAL -> A but QUALITATIVE only, else U."""
    if item_status != "ACCEPTED":
        part.add(U, "ITEM_NOT_ACCEPTED")
    elif extent == "COMPLETE":
        part.add(NA, "INHIBITOR_PRESENT")
    elif extent == "PARTIAL":
        part.qualitative_only = True
        part.reasons.append("INHIBITOR_PARTIAL")
    else:
        part.add(U, "INHIBITOR_EXTENT_UNKNOWN")


def _gates(e: Mapping[str, Any], q: ApplicabilityQuery, part: _Part) -> None:
    via = {i["evaluated_via"]["gate_key"]: i for i in e["inhibitors_mitigators"] if i["evaluated_via"]["mode"] == "GATE"}
    for g in e["condition_gates"]:
        token = f"axis:{g['cv_id']}@{g['location']}"
        if g["gate_type"] == "MODULATING":
            if g["status"] != "ACCEPTED":
                part.unobserved("MODIFIER_ITEM_NOT_ACCEPTED")
            elif _axis_window(g, q)[1] in ("MISSING", "AXIS_CONFLICT", "AXIS_UNIT_MISMATCH", "AXIS_BASIS_MISMATCH",
                                           "AXIS_TYPE_MISMATCH"):
                part.unobserved("MODIFIER_INPUT_UNOBSERVED", token)
            continue
        if g["status"] != "ACCEPTED":
            part.add(U, "ITEM_NOT_ACCEPTED")
            continue
        if q.matrix is None or q.matrix not in {i["ref"] for i in g["matrix_scope"]["included"]}:
            part.add(U, "GATE_MATRIX_UNLISTED")
            continue
        w, why = _axis_window(g, q)
        missing = token if why == "MISSING" else None
        if g["gate_type"] == "NECESSARY":
            if w == NA and why == "CATEGORY_EXCLUDED":
                part.add(NA, "CATEGORY_EXCLUDED")
            else:
                part.add(w, "NECESSARY_AXIS_UNKNOWN" if why == "MISSING" else (why or ""), missing=missing)
        elif w == A:                                    # INHIBITING window holds: agent or condition present
            i = via.get(g["gate_key"])
            if i is None:
                part.add(NA, "INHIBITOR_PRESENT")
            else:
                _present(part, i["extent"], item_status=i["status"])
        elif w == U:
            part.add(U, "INHIBITOR_UNKNOWN", *([why] if why not in (None, "MISSING") else []), missing=missing)


def _inhibitors(e: Mapping[str, Any], q: ApplicabilityQuery, part: _Part) -> None:
    for i in e["inhibitors_mitigators"]:
        v, blocking = i["evaluated_via"], i["role"] in ("INHIBITOR", "MITIGATOR")
        if v["mode"] == "GATE":
            continue
        if v["mode"] == "NOT_EVALUABLE_YET":
            part.add(U, "INHIBITOR_NOT_EVALUABLE") if blocking else part.unobserved("MODIFIER_ITEM_NOT_ACCEPTED")
            continue
        token = "state:" + _state_key(v["state_ref"])
        if i["status"] != "ACCEPTED":
            part.add(U, "ITEM_NOT_ACCEPTED") if blocking else part.unobserved("MODIFIER_ITEM_NOT_ACCEPTED")
            continue
        s = _state(q, v["state_ref"])
        if s is None:
            part.add(U, "INHIBITOR_UNKNOWN", missing=token) if blocking else part.unobserved(
                "MODIFIER_INPUT_UNOBSERVED", token)
        elif blocking and _predicate(v["predicate"], s):
            _present(part, i["extent"])


def _predicate(p: Mapping[str, Any], v: str) -> bool:
    op, vals = p["operator"], p["values"]
    return {"IS": v in vals, "IN": v in vals, "IS_NOT": v not in vals, "NOT_IN": v not in vals,
            "PRESENT": v == "PRESENT", "ABSENT": v == "ABSENT"}[op]


def _target(e: Mapping[str, Any], q: ApplicabilityQuery) -> Mapping[str, Any] | None:
    for t in e["affected_targets"]:
        ref = t["target"]
        if (q.target_svar_id and ref["svar_id"] == q.target_svar_id) or \
                (q.target_state_key and ref["state_key"] == q.target_state_key):
            return t
    return None


def evaluate_mechanism(e: Mapping[str, Any], q: ApplicabilityQuery, *, signature_keys: tuple[str, ...] = (),
                       trigger_unknown: bool = False, missing_modifiers: Iterable[str] = ()) -> MechanismVerdict:
    """G4 verdict (plus G7 observability and G5 competition notes) of one candidate mechanism for the target."""
    ok, why = MC.consumable_for_applicability(e)
    t = _target(e, q)
    dirs = tuple(sorted(t["allowed_directions"])) if t else ()
    part = _Part()
    if trigger_unknown:
        part.add(U, "TRIGGER_MODIFIER_UNKNOWN")
        part.missing += [f"modifier:{m}" for m in missing_modifiers]
    comp: list[str] = []
    if not ok:
        part.add(U, "MECH_NOT_CONSUMABLE", *(f"MECH_{r}" for r in why))
    else:
        if t is None or t["status"] != "ACCEPTED":
            part.add(U, "TARGET_NOT_ACCEPTED")
        v, r = _scope_verdict(e["matrix_scope"], q.matrix)
        part.add(v, r or "")
        for p in e["preconditions"]:
            token = "state:" + _state_key(p["state_ref"])
            if p["status"] != "ACCEPTED":
                part.add(U, "ITEM_NOT_ACCEPTED")
                continue
            s = _state(q, p["state_ref"])
            if s is None:
                part.add(U, "PRECONDITION_UNKNOWN", missing=token)
            elif not _predicate(p["predicate"], s):
                part.add(NA, "PRECONDITION_FAIL")
        _gates(e, q, part)
        _inhibitors(e, q, part)
        for h in e["history_dependence"]:
            if h["status"] != "ACCEPTED":
                part.unobserved("HISTORY_ITEM_NOT_ACCEPTED")
            elif _state(q, h["state_ref"]) is None:
                part.unobserved("HISTORY_INPUT_UNOBSERVED", "state:" + _state_key(h["state_ref"]))
        comp = [c["mechanism_key"] for c in e["competes_with"] if c["status"] != "ACCEPTED"]
    return MechanismVerdict(
        e["mechanism_key"], e["id"], tuple(sorted(signature_keys)), ok, why, part.verdict,
        tuple(sorted({x for x in part.reasons if x})), dirs, part.qualitative_only,
        tuple(sorted(set(part.missing))), tuple(sorted(set(part.obs_reasons))), tuple(sorted(comp)))


# ----------------------------------------------------------------------------- engine
def _case_gate(name: str, cg: CaseGate | None) -> tuple[str, list[str]]:
    if cg is None:
        return U, [_CASE_GATE_DEFAULT[name]]
    if not isinstance(cg, CaseGate) or cg.verdict not in VERDICTS:
        raise ApplicabilityError(f"{name}: a case gate verdict is one of {VERDICTS}")
    if name == "G7" and cg.verdict == NA:
        raise ApplicabilityError("G7: input observability is never NOT_APPLICABLE (missing -> UNKNOWN)")
    if cg.verdict == A:
        if cg.reasons or not (cg.ref or "").strip():
            raise ApplicabilityError(f"{name}: APPLICABLE needs a constructed reference and no reason")
        return A, []
    if not cg.reasons or not set(cg.reasons) <= _CASE_GATE_CODES[name]:
        raise ApplicabilityError(f"{name}: {cg.verdict} needs reasons from {sorted(_CASE_GATE_CODES[name])}")
    return cg.verdict, sorted(set(cg.reasons))


def _check_inputs(q: ApplicabilityQuery, entries: Sequence[Mapping[str, Any]],
                  signatures: Sequence[PS.ProcessSignature], hierarchy: PS.ProcessHierarchy) -> None:
    for a in q.axes:
        if a.source_kind != CONSTRUCTED_CASE or a.source_ref.upper().startswith("COND"):
            raise ApplicabilityError(f"{a.token}: 23a consumes no COND value (spine 23a); constructed cases only")
    for e in entries:
        problem = _entry_problem(_canon(e))
        if problem:
            raise ApplicabilityError(f"{e.get('mechanism_key')}: {problem}")
    for s in signatures:
        if not isinstance(s, PS.ProcessSignature):
            raise ApplicabilityError("signatures must be ProcessSignature instances")
        probs = PS.signature_problems(s.to_canonical(), entries, hierarchy)
        if probs:
            raise ApplicabilityError(f"refused signature {s.signature_key}: {probs[0]}")


@functools.lru_cache(maxsize=4096)
def _entry_problem(entry_bytes: bytes) -> str | None:
    """First schema or semantic problem of a MECH entry, memoised on its canonical bytes (pure)."""
    e = json.loads(entry_bytes)
    errs = MC.schema_errors(e)
    if errs:
        return f"MECH v1.1 schema errors: {errs[0]}"
    probs = MC.semantic_problems(e, _cv_rows(), effect_rows=_effect_rows())
    return f"MECH v1.1 semantic problems: {probs[0]}" if probs else None


def _candidates(q: ApplicabilityQuery, signatures: Sequence[PS.ProcessSignature],
                by_key: Mapping[str, Mapping[str, Any]]) -> tuple[list[MechanismVerdict], list[str]]:
    try:
        matches = PS.match_signatures(signatures, q.process_id or "", q.modifiers)
    except PS.SignatureError as exc:
        raise ApplicabilityError(str(exc)) from exc
    grouped: dict[str, list[PS.SignatureMatch]] = {}
    for m in matches:
        e = by_key[m.signature.mechanism_key]
        if any(c.target_key == (_target(e, q) or {}).get("target_key") for c in m.signature.candidate_effects):
            grouped.setdefault(m.signature.mechanism_key, []).append(m)
    out = []
    for key in sorted(grouped):
        ms = grouped[key]
        unknown = all(m.modifier_status == PS.MODIFIER_UNKNOWN for m in ms)
        missing = sorted({x for m in ms for x in m.missing_modifiers}) if unknown else []
        out.append(evaluate_mechanism(by_key[key], q, signature_keys=tuple(m.signature.signature_key for m in ms),
                                      trigger_unknown=unknown, missing_modifiers=missing))
    if not out:
        return out, ["NO_CANDIDATE_MECHANISM"]
    if all("TRIGGER_MODIFIER_UNKNOWN" in mv.reasons for mv in out):
        return out, ["TRIGGER_MODIFIER_UNKNOWN"]
    return out, []


def _g5(mvs: Sequence[MechanismVerdict], q: ApplicabilityQuery) -> tuple[str, list[str]]:
    act = [m for m in mvs if m.verdict == A]
    unk = [m for m in mvs if m.verdict == U]
    if not act:
        return U, ["NO_SINGLE_APPLICABLE_MECHANISM"]
    if len(act) >= 2 and not q.joint_form_ref:
        return NA, ["COMPETING_BOTH_APPLICABLE"]
    if unk:
        return U, ["COMPETING_UNRESOLVED"]
    if any(m.competition_reasons for m in act):
        return U, ["COMPETITION_NOT_ACCEPTED"]
    return A, []


def evaluate(query: ApplicabilityQuery, signatures: Sequence[PS.ProcessSignature],
             entries: Sequence[Mapping[str, Any]], hierarchy: PS.ProcessHierarchy, *,
             mode: str = MODE_23A) -> dict[str, Any]:
    """One APPDEC record (dict, schema-validated) for the query. Pure and deterministic."""
    if mode in BLOCKED_MODES:
        raise ApplicabilityError(BLOCKED_MODES[mode])
    if mode != MODE_23A:
        raise ApplicabilityError(f"unknown mode {mode!r}: only {MODE_23A!r} (engine verification) exists")
    if not isinstance(query, ApplicabilityQuery):
        raise ApplicabilityError("query must be an ApplicabilityQuery")
    signatures, entries = tuple(signatures), tuple(entries)
    _check_inputs(query, entries, signatures, hierarchy)
    by_key = {e["mechanism_key"]: e for e in entries}
    gates: dict[str, dict[str, Any]] = {}
    gates["G0"] = {"verdict": NOT_REQUIRED,
                   "reasons": ["G0_NOT_EVALUATED"] if query.evidence_precheck == "NOT_EVALUATED" else []}
    missing: set[str] = set()
    if not query.event_resolved or query.process_id is None:
        gates["G1"] = {"verdict": U, "reasons": ["EVENT_UNRESOLVED"]}
        missing.add("event:process")
    elif not hierarchy.contains(query.process_id):
        gates["G1"] = {"verdict": U, "reasons": ["PROCESS_NOT_IN_HIERARCHY"]}
    else:
        gates["G1"] = {"verdict": A, "reasons": []}
    mvs, g3 = _candidates(query, signatures, by_key) if gates["G1"]["verdict"] == A else ([], ["NO_CANDIDATE_MECHANISM"])
    matched = [m for m in signatures if any(m.signature_key in mv.signature_keys for mv in mvs)]
    gates["G2"] = {"verdict": NOT_REQUIRED, "reasons": []}
    gates["G3"] = {"verdict": U if g3 else A, "reasons": g3}
    vs = [m.verdict for m in mvs]
    g4 = A if A in vs else (U if U in vs or not vs else NA)
    gates["G4"] = {"verdict": g4, "reasons": [] if g4 == A else (
        sorted({r for m in mvs if m.verdict == g4 for r in m.reasons}) or ["NO_CANDIDATE_MECHANISM"])}
    gates["G5"] = dict(zip(("verdict", "reasons"), _g5(mvs, query)))
    act = [m for m in mvs if m.verdict == A]
    for name, cg in (("G6", query.formula), ("G8", query.parameters)):
        gates[name] = dict(zip(("verdict", "reasons"), _case_gate(name, cg)))
    _, r7 = _case_gate("G7", query.observability)
    obs = {r for m in act for r in m.observability_reasons} | set(r7)
    if not act:                                  # nothing applicable: no input set to observe
        obs.add("INPUT_UNOBSERVED")
    gates["G7"] = {"verdict": U if obs else A, "reasons": sorted(obs)}
    for m in mvs:
        if m.verdict != NA:
            missing |= set(m.missing_inputs)
    applicability = k3_and(gates[g]["verdict"] for g in SIM_GATES)
    rec = _route(query, gates, mvs, act, applicability, sorted(missing))
    rec.update({
        "record_type": "APPDEC", "schema_version": APPDEC_SCHEMA_VERSION, "status": STATUS, "mode": MODE_23A,
        "is_evidence": False, "provenance_class": PS.PROVENANCE_CLASS, "condition_source": CONSTRUCTED_CASE,
        "query": query.to_canonical(), "evidence_precheck": query.evidence_precheck,
        "deterministic_change_refs": sorted({d for s in matched for d in s.deterministic_change_refs}),
        "mechanisms": [m.to_canonical() for m in mvs], "applicability": applicability,
        "domain_flag": query.domain_flag, "safety_critical": query.safety_critical,
        "registry_versions": _registry_versions(), "code_sha256": _code_sha256(), "sim_run_id": None,
        "input_sha256": hashlib.sha256(_canon({"query": query.full_canonical(),
                                               "signatures": sorted(s.sha256() for s in signatures),
                                               "entries": sorted(hashlib.sha256(_canon(e)).hexdigest()
                                                                 for e in entries)})).hexdigest(),
    })
    rec["gates"] = {k: rec["gates"][k] for k in sorted(rec["gates"])}
    rec["appdec_id"] = "APPDEC-DRAFT-" + hashlib.sha256(_canon(rec)).hexdigest()[:16]
    errs = appdec_schema_errors(rec)
    if errs:
        raise ApplicabilityError(f"engine produced an invalid APPDEC record: {errs[0]}")
    return rec


def _route(q: ApplicabilityQuery, gates: dict[str, dict[str, Any]], mvs: Sequence[MechanismVerdict],
           act: Sequence[MechanismVerdict], applicability: str, missing: list[str]) -> dict[str, Any]:
    open_dirs = sorted({d for m in mvs if m.verdict in (A, U) for d in m.directions})
    unambiguous = len(open_dirs) == 1 and open_dirs[0] != "UNKNOWN"
    partial = any(m.qualitative_only for m in act)
    all_a = applicability == A and not partial
    g9: list[str] = []
    if q.domain_flag == "SIM_PROHIBITED":
        g9.append("OUT_OF_MS_LIMITS")
    elif q.domain_flag == "UNKNOWN":
        g9.append("DOMAIN_UNKNOWN")
    elif q.domain_flag != "IN_VALIDATION_DOMAIN":
        g9.append("DOMAIN_NOT_VALIDATED")
    if q.safety_critical != "NO":
        g9.append("SAFETY_CRITICAL" if q.safety_critical == "YES" else "SAFETY_UNKNOWN")
    if partial:
        g9.append("QUALITATIVE_ONLY_PARTIAL_INHIBITION")
    sim_ok = all_a and q.domain_flag == "IN_VALIDATION_DOMAIN" and q.safety_critical == "NO"
    ask = sorted(set(missing) & set(q.user_observable))
    cross, label = "NONE", "NONE"
    if q.evidence_precheck in ("DIRECT", "BRACKETING"):
        route = "DIRECT" if q.evidence_precheck == "DIRECT" else "INTERPOLATE"
        cross = "SIMULATE" if sim_ok else "NONE"
        g9.append("EVIDENCE_PREEMPTS")
    elif sim_ok:
        route = "SIMULATE"
    elif all_a and q.safety_critical == "NO" and q.domain_flag in ("IN_CALIBRATION_ONLY", "EXTRAPOLATED_WITHIN_LIMITS"):
        route = "QUALITATIVE"
        label = "RESEARCH_ONLY" if q.domain_flag == "IN_CALIBRATION_ONLY" else "EXTRAPOLATED"
    elif gates["G4"]["verdict"] == A and unambiguous:
        route = "QUALITATIVE"
    elif ask:
        route = "ASK"
    else:
        route = "UNKNOWN"
    if gates["G4"]["verdict"] == A and not unambiguous:
        g9.append("DIRECTION_AMBIGUOUS")
    gates["G9"] = {"verdict": NOT_REQUIRED, "reasons": sorted(set(g9))}
    return {"gates": gates, "route": route, "cross_check": cross, "model_estimate_label": label,
            "direction_set": open_dirs, "conflict_flag": {"INCREASE", "DECREASE"} <= set(open_dirs),
            "missing_inputs": missing, "ask_candidates": ask}


# ----------------------------------------------------------------------------- 26g projection
def to_applicability_binding(record: Mapping[str, Any], system_id: str) -> Any:
    """Project an APPDEC record onto the S156 26g ApplicabilityBinding (event_id, system_id, status, ref).

    Conservative: APPLICABLE only for route SIMULATE; NOT_APPLICABLE when the record's applicability is
    NOT_APPLICABLE; every other record (UNKNOWN, QUALITATIVE, ASK, DIRECT / INTERPOLATE pre-emption) is UNKNOWN.
    The ref is always the appdec_id. Which simulator system a target belongs to is a 26b matter: the caller
    names system_id; this module names no system.
    """
    from culinarystate.simulation.recipe_adapter import ApplicabilityBinding

    errs = appdec_schema_errors(record)
    if errs:
        raise ApplicabilityError(f"not a valid APPDEC record: {errs[0]}")
    status = A if record["route"] == "SIMULATE" else (NA if record["applicability"] == NA else U)
    return ApplicabilityBinding(record["query"]["event_id"], system_id, status, record["appdec_id"])
