"""Step 26g recipe-event -> simulation-input adapter, SIMLINK records, simulability census (DRAFT_PENDING_16c_23a_26b).

Status: DRAFT_PENDING_16c_23a_26b. The 26g hard dependencies are not built: Step 18 exists
only as the S156 draft replay (16c open), 23a (APPLICABLE / NOT_APPLICABLE / UNKNOWN
engine) and 26b (``sim_aa_1`` / ``sim_chl_1``) do not exist. So this module is a
**contract stub**: it states what a future simulator call would need for one replayed
recipe event, says which inputs are present, and counts the reasons. It runs no
simulator, emits no estimate, mints no ``sim_run_id`` and reads or writes no ledger.

Contract (Plan Step 26 card, 26g; D-027 R-15 three-valued applicability; R-20)
- Required inputs per system (``SYSTEM_REQUIREMENTS``) are taken from the card's
  architecture detail (initial / boundary conditions, product temperature, fallback
  system). They are PROPOSED_PENDING_26b: 26b owns the real interface.
- Each input is MEASURED (an exact point value), RANGE (an exact interval) or UNKNOWN.
  "MEASURED" names the value shape (a stated point value traced to an EVT / COND / QNT /
  ING record); it is not a claim of a laboratory measurement. Status is derived from
  the value, never declared. UNKNOWN carries no value.
- Values come only from caller-supplied ``ConditionBinding``s traced to a record id.
  Nothing is defaulted, inferred from a verb or taken from literature: a binding whose
  ``SourceClass`` is not a recipe-side class (``PERMITTED_SOURCE_CLASSES``) is not used
  (S116 contract: evidence-side or model classes do not describe a recipe event).
- Units are fixed per input and never converted. Numbers are exact ``Fraction``s.
  Categorical values are upper-case codes, so no recipe text can enter.
- Conflicting bindings make the input UNKNOWN (``CONFLICTING_<INPUT>``); none is picked.
- Route: SIMULATE only when the replay has no issue, the event was APPLIED and consumed
  at least one entity, applicability is APPLICABLE (23a record reference) and every
  required input is MEASURED or RANGE. Anything else is SIM_PROHIBITED with reason codes.
  UNKNOWN never becomes SIMULATE. SIMULATE does not mean a run exists: the simulator is
  not built (``simulator_status``) and ``sim_run_id`` stays null.
- Not checked here (``NOT_CHECKED``): M&S limits of the model card (26b / 26e), the
  NO_COMPATIBLE_SET parameter check (24/25), the DIRECT / INTERPOLATE pre-emption (Step 36)
  and any cross-check between ``duration`` and the temperature profile end.

The census (``simulability_census``) counts routes, reasons and input statuses. It holds
counts and code tokens only: no ids, values or text.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, fields
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, Union

from culinarystate.state_graph.event_log import ROOT, canonical_json, sha256_canonical, write_canonical_jsonl
from culinarystate.state_graph.replay import ReplayResult
from culinarystate.state_graph.source_class import SourceClass

STATUS = "DRAFT_PENDING_16c_23a_26b"
CONTRACT_VERSION = "step26g-sim-input-0.1.0-draft"
LINK_SCHEMA_VERSION = "step26g-simlink-0.1.0-draft"
CENSUS_VERSION = "step26g-census-0.1.0-draft"
REQUIREMENTS_STATUS = "PROPOSED_PENDING_26b"
SIMULATOR_STATUS = "NOT_BUILT_PENDING_26b"

INPUT_STATUSES = ("MEASURED", "RANGE", "UNKNOWN")
APPLICABILITY_STATUSES = ("APPLICABLE", "NOT_APPLICABLE", "UNKNOWN")
ROUTES = ("SIMULATE", "SIM_PROHIBITED")
REF_KINDS = ("EVT", "COND", "QNT", "ING")
PERMITTED_SOURCE_CLASSES = frozenset({SourceClass.STRUCTURAL_RECIPE, SourceClass.SYNTHETIC})
CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
PROTECTED_NAME = re.compile(r"^SIM(LINK)?(_V\d+)?\.JSONL$")
NOT_CHECKED = ("MS_LIMITS_SEE_26B_26E_MODEL_CARD", "NO_COMPATIBLE_SET_SEE_24_25",
               "DIRECT_INTERPOLATE_PREEMPTION_SEE_36", "DURATION_VS_PROFILE_END_NOT_CROSS_CHECKED")


class SimInputError(ValueError):
    """Structural contract violation (programming error, not a data issue)."""


# ---------------------------------------------------------------- input specifications
@dataclass(frozen=True)
class InputSpec:
    name: str
    kind: str          # PROFILE | NUMBER | CODE
    unit: str | None   # fixed unit; never converted
    card_ref: str


_CARD = "Plan v2 Step 26 architecture detail"
INPUT_SPECS: dict[str, InputSpec] = {s.name: s for s in (
    InputSpec("temperature_profile", "PROFILE", "min|degC", f"{_CARD}: initial/boundary conditions, bath schedule T_b(t)"),
    InputSpec("duration", "NUMBER", "min", f"{_CARD}: predictive interval at requested times"),
    InputSpec("medium", "CODE", None, f"{_CARD}: initial/boundary conditions, medium"),
    InputSpec("water_ratio", "NUMBER", "mL/g", f"{_CARD}: equations, r = V_w/m_t"),
    InputSpec("start_mode", "CODE", None, f"{_CARD}: initial/boundary conditions, start mode"),
    InputSpec("lid_state", "CODE", None, f"{_CARD}: initial/boundary conditions, lid"),
    InputSpec("medium_ph", "NUMBER", "pH", f"{_CARD}: fallback system, pH is a required input"),
    InputSpec("piece_size_class", "CODE", None, f"{_CARD}: product temperature, size class"),
    InputSpec("matrix_class", "CODE", None, f"{_CARD}: parameters per matrix class m"),
)}
SYSTEM_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "sim_aa_1": ("temperature_profile", "duration", "medium", "water_ratio", "start_mode", "lid_state",
                 "piece_size_class", "matrix_class"),
    "sim_chl_1": ("temperature_profile", "duration", "medium", "medium_ph", "piece_size_class", "matrix_class"),
}
EVENT_REASONS = ("REPLAY_HAS_ISSUES", "EVENT_REJECTED_IN_REPLAY", "EVENT_SKIPPED_SCOPE", "NO_CONSUMED_ENTITY",
                 "APPLICABILITY_UNKNOWN", "APPLICABILITY_NOT_APPLICABLE")
INPUT_REASON_PREFIXES = ("MISSING_", "CONFLICTING_", "SOURCE_NOT_PERMITTED_")
REASON_CODES = frozenset(EVENT_REASONS) | frozenset(p + n.upper() for p in INPUT_REASON_PREFIXES for n in INPUT_SPECS)
BINDING_COUNT_CODES = ("BINDING_EVENT_NOT_IN_REPLAY", "BINDING_INPUT_NOT_REQUIRED", "SOURCE_CLASS_NOT_PERMITTED",
                       "APPLICABILITY_EVENT_NOT_IN_REPLAY", "APPLICABILITY_OTHER_SYSTEM", "APPLICABILITY_CONFLICT")

Number = Union[Fraction, tuple[Fraction, Fraction]]


def _fs(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def _nonblank(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SimInputError(f"{name} must be a nonblank string")


def _exact(value: Any, name: str) -> None:
    if type(value) is not Fraction:
        raise SimInputError(f"{name} must be an exact Fraction (no floats)")


# ---------------------------------------------------------------- bindings (caller-supplied, traced)
@dataclass(frozen=True)
class ProfileSegment:
    """Temperature in [low, high] degC over process time [start, end) min, exact."""
    start: Fraction
    end: Fraction
    low: Fraction
    high: Fraction

    def __post_init__(self) -> None:
        for name in ("start", "end", "low", "high"):
            _exact(getattr(self, name), f"profile {name}")
        if self.start < 0 or self.end <= self.start:
            raise SimInputError("profile segment needs 0 <= start < end")
        if self.low > self.high:
            raise SimInputError("profile temperature interval is inverted")

    @property
    def is_point(self) -> bool:
        return self.low == self.high

    def to_canonical(self) -> dict:
        return {"start": _fs(self.start), "end": _fs(self.end), "low": _fs(self.low), "high": _fs(self.high)}


def _value_canonical(value: Any) -> Any:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, Fraction):
        return _fs(value)
    if value and isinstance(value[0], ProfileSegment):
        return [s.to_canonical() for s in value]
    return [_fs(value[0]), _fs(value[1])]


@dataclass(frozen=True)
class ConditionBinding:
    """One traced value for one required input of one replayed event."""
    event_id: str
    input_name: str
    value: Any
    ref_kind: str
    ref: str
    source_class: SourceClass
    unit: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.event_id, "binding event_id")
        spec = INPUT_SPECS.get(self.input_name)
        if spec is None:
            raise SimInputError(f"unknown input {self.input_name!r}; known: {tuple(INPUT_SPECS)}")
        if self.ref_kind not in REF_KINDS:
            raise SimInputError(f"provenance ref_kind must be one of {REF_KINDS}")
        _nonblank(self.ref, "INPUT_UNTRACED: binding ref")
        if not isinstance(self.source_class, SourceClass):
            raise SimInputError("source_class must be a SourceClass member")
        if self.unit != spec.unit:
            raise SimInputError(f"{self.input_name} unit must be {spec.unit!r} (no unit conversion here)")
        getattr(self, f"_check_{spec.kind.lower()}")()

    def _check_code(self) -> None:
        if not (isinstance(self.value, str) and CODE_PATTERN.match(self.value)):
            raise SimInputError("categorical inputs are upper-case codes, never text")

    def _check_number(self) -> None:
        v = self.value
        if isinstance(v, tuple):
            if len(v) != 2:
                raise SimInputError("a range is a (low, high) pair")
            _exact(v[0], "range low")
            _exact(v[1], "range high")
            lo, hi = v
        else:
            _exact(v, "value")
            lo = hi = v
        if lo > hi:
            raise SimInputError("range is inverted")
        if self.input_name != "medium_ph" and lo < 0:
            raise SimInputError(f"{self.input_name} cannot be negative")

    def _check_profile(self) -> None:
        v = self.value
        if not (isinstance(v, tuple) and v and all(isinstance(s, ProfileSegment) for s in v)):
            raise SimInputError("temperature_profile is a non-empty tuple of ProfileSegment")
        if v[0].start != 0 or any(a.end != b.start for a, b in zip(v, v[1:])):
            raise SimInputError("profile segments must start at 0 and be contiguous")

    @property
    def status(self) -> str:
        v = self.value
        if isinstance(v, str) or isinstance(v, Fraction):
            return "MEASURED"
        if isinstance(v[0], ProfileSegment):
            return "MEASURED" if all(s.is_point for s in v) else "RANGE"
        return "MEASURED" if v[0] == v[1] else "RANGE"

    @property
    def normalised_value(self) -> Any:
        v = self.value
        return v[0] if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], Fraction) and v[0] == v[1] else v


@dataclass(frozen=True)
class ApplicabilityBinding:
    """A 23a applicability verdict for (event, system); APPLICABLE / NOT_APPLICABLE need a record ref."""
    event_id: str
    system_id: str
    status: str
    ref: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.event_id, "applicability event_id")
        if self.system_id not in SYSTEM_REQUIREMENTS:
            raise SimInputError(f"system_id must be one of {tuple(SYSTEM_REQUIREMENTS)}")
        if self.status not in APPLICABILITY_STATUSES:
            raise SimInputError(f"applicability must be one of {APPLICABILITY_STATUSES}")
        if self.status != "UNKNOWN":
            _nonblank(self.ref, "applicability ref (23a record)")


# ---------------------------------------------------------------- resolved contract records
@dataclass(frozen=True)
class SimInput:
    name: str
    status: str
    value: Any
    unit: str | None
    provenance: tuple[tuple[str, str], ...]
    source_classes: tuple[str, ...]
    reason: str | None

    def to_canonical(self) -> dict:
        return {"name": self.name, "status": self.status, "value": _value_canonical(self.value), "unit": self.unit,
                "provenance": [list(p) for p in self.provenance], "source_classes": list(self.source_classes),
                "reason": self.reason}


@dataclass(frozen=True)
class SimulationInputRecord:
    system_id: str
    recipe_id: str
    event_id: str
    event_revision: int
    event_sha256: str
    seq: int
    transaction_status: str
    trajectory: str
    targets: tuple[tuple[str, int, str], ...]
    inputs: tuple[SimInput, ...]
    applicability: str
    applicability_refs: tuple[str, ...]
    route: str
    reasons: tuple[str, ...]
    synthetic_inputs: bool
    replay_snapshot_sha256: str
    replay_config_sha256: str
    simulator_status: str = SIMULATOR_STATUS

    @property
    def recipe_event_id(self) -> str:
        return f"{self.recipe_id}#{self.event_id}"

    @property
    def all_inputs_present(self) -> bool:
        return all(i.status != "UNKNOWN" for i in self.inputs)

    def to_canonical(self) -> dict:
        return {"record": "SIM_INPUT", "contract_version": CONTRACT_VERSION, "draft_status": STATUS,
                "requirements_status": REQUIREMENTS_STATUS, "system_id": self.system_id,
                "recipe_id": self.recipe_id, "recipe_event_id": self.recipe_event_id, "event_id": self.event_id,
                "event_revision": self.event_revision, "event_sha256": self.event_sha256, "seq": self.seq,
                "transaction_status": self.transaction_status, "trajectory": self.trajectory,
                "targets": [list(t) for t in self.targets], "inputs": [i.to_canonical() for i in self.inputs],
                "applicability": self.applicability, "applicability_refs": list(self.applicability_refs),
                "route": self.route, "reasons": list(self.reasons), "synthetic_inputs": self.synthetic_inputs,
                "replay_snapshot_sha256": self.replay_snapshot_sha256,
                "replay_config_sha256": self.replay_config_sha256, "simulator_status": self.simulator_status,
                "not_checked": list(NOT_CHECKED)}

    @property
    def sha256(self) -> str:
        return sha256_canonical(self.to_canonical())


@dataclass(frozen=True)
class SimulationInputSet:
    """All replayed events of one recipe for one system, plus counts of bindings that were not attached."""
    recipe_id: str
    system_id: str
    records: tuple[SimulationInputRecord, ...]
    binding_counts: Mapping[str, int]
    replay_snapshot_sha256: str

    def header(self) -> dict:
        return {"record": "SIM_INPUT_SET", "contract_version": CONTRACT_VERSION, "draft_status": STATUS,
                "recipe_id": self.recipe_id, "system_id": self.system_id, "count": len(self.records),
                "binding_counts": dict(self.binding_counts), "replay_snapshot_sha256": self.replay_snapshot_sha256}

    def to_jsonl(self) -> str:
        return "".join(canonical_json(r) + "\n" for r in [self.header(), *(x.to_canonical() for x in self.records)])

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_jsonl().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- adapter
def _resolve(spec: InputSpec, found: Sequence[ConditionBinding]) -> tuple[SimInput, int]:
    """One required input from its bindings; returns (input, number of bindings not permitted)."""
    usable = [x for x in found if x.source_class in PERMITTED_SOURCE_CLASSES]
    refused = len(found) - len(usable)
    prov = tuple(sorted({(x.ref_kind, x.ref) for x in usable}))
    classes = tuple(sorted({x.source_class.value for x in usable}))
    tag = spec.name.upper()
    if not usable:
        reason = f"SOURCE_NOT_PERMITTED_{tag}" if refused else f"MISSING_{tag}"
        return SimInput(spec.name, "UNKNOWN", None, spec.unit, (), (), reason), refused
    values = {canonical_json(_value_canonical(x.normalised_value)) for x in usable}
    if len(values) > 1:
        return SimInput(spec.name, "UNKNOWN", None, spec.unit, prov, classes, f"CONFLICTING_{tag}"), refused
    first = usable[0]
    return SimInput(spec.name, first.status, first.normalised_value, spec.unit, prov, classes, None), refused


def build_simulation_inputs(replay: ReplayResult, *, recipe_id: str, system_id: str,
                            bindings: Iterable[ConditionBinding] = (),
                            applicability: Iterable[ApplicabilityBinding] = ()) -> SimulationInputSet:
    """Simulation-input contract records for every replayed event of one recipe (no estimate, no run)."""
    if not isinstance(replay, ReplayResult):
        raise SimInputError("build_simulation_inputs takes a ReplayResult")
    _nonblank(recipe_id, "recipe_id")
    if system_id not in SYSTEM_REQUIREMENTS:
        raise SimInputError(f"system_id must be one of {tuple(SYSTEM_REQUIREMENTS)}")
    ids = [t.event_id for t in replay.transactions]
    if len(ids) != len(set(ids)):
        raise SimInputError("EVENT_ID_REUSED: replay holds an event id twice; recipe_event_id would be ambiguous")
    required = SYSTEM_REQUIREMENTS[system_id]
    counts = {c: 0 for c in BINDING_COUNT_CODES}
    by_key: dict[tuple[str, str], list[ConditionBinding]] = {}
    for x in bindings:
        if not isinstance(x, ConditionBinding):
            raise SimInputError("bindings must be ConditionBinding instances")
        if x.event_id not in ids:
            counts["BINDING_EVENT_NOT_IN_REPLAY"] += 1
        elif x.input_name not in required:
            counts["BINDING_INPUT_NOT_REQUIRED"] += 1
        else:
            by_key.setdefault((x.event_id, x.input_name), []).append(x)
    apps: dict[str, list[ApplicabilityBinding]] = {}
    for a in applicability:
        if not isinstance(a, ApplicabilityBinding):
            raise SimInputError("applicability must be ApplicabilityBinding instances")
        if a.system_id != system_id:
            counts["APPLICABILITY_OTHER_SYSTEM"] += 1
        elif a.event_id not in ids:
            counts["APPLICABILITY_EVENT_NOT_IN_REPLAY"] += 1
        else:
            apps.setdefault(a.event_id, []).append(a)
    replay_failed = replay.status == "FAIL"
    snap, cfg = replay.snapshot_sha256, replay.config.config_sha256
    records = []
    for t in replay.transactions:
        reasons: list[str] = []
        if replay_failed:
            reasons.append("REPLAY_HAS_ISSUES")
        if t.status == "REJECTED":
            reasons.append("EVENT_REJECTED_IN_REPLAY")
        elif t.status == "SKIPPED_SCOPE":
            reasons.append("EVENT_SKIPPED_SCOPE")
        targets = tuple((v.entity_id, v.version, v.entity_type) for v in t.output_entity_versions
                        if v.version > 0 and v.lifecycle == "INCORPORATED")
        if t.status == "APPLIED" and not targets:
            reasons.append("NO_CONSUMED_ENTITY")
        verdicts = apps.get(t.event_id, [])
        statuses = {a.status for a in verdicts}
        if len(statuses) > 1:
            counts["APPLICABILITY_CONFLICT"] += 1
            applic = "UNKNOWN"
        else:
            applic = statuses.pop() if statuses else "UNKNOWN"
        if applic != "APPLICABLE":
            reasons.append(f"APPLICABILITY_{applic}")
        inputs = []
        for name in required:
            item, refused = _resolve(INPUT_SPECS[name], by_key.get((t.event_id, name), []))
            counts["SOURCE_CLASS_NOT_PERMITTED"] += refused
            inputs.append(item)
            if item.reason is not None:
                reasons.append(item.reason)
        synthetic = any(SourceClass.SYNTHETIC.value in i.source_classes for i in inputs)
        route = "SIM_PROHIBITED" if reasons else "SIMULATE"
        records.append(SimulationInputRecord(
            system_id, recipe_id, t.event_id, t.event_revision, t.event_sha256, t.seq, t.status,
            replay.config.trajectory, targets, tuple(inputs), applic,
            tuple(sorted({a.ref for a in verdicts if a.ref is not None})), route, tuple(sorted(reasons)), synthetic,
            snap, cfg))
    return SimulationInputSet(recipe_id, system_id, tuple(records), counts, snap)


# ---------------------------------------------------------------- SIMLINK link records
@dataclass(frozen=True)
class SimLinkRecord:
    """``recipe_event_id -> sim_run_id`` row. ``sim_run_id`` stays null: no run exists and none is minted here."""
    recipe_event_id: str
    recipe_id: str
    event_id: str
    event_revision: int
    event_sha256: str
    system_id: str
    route: str
    reasons: tuple[str, ...]
    simulation_input_sha256: str
    replay_snapshot_sha256: str
    replay_config_sha256: str
    sim_run_id: None = None
    simulator_status: str = SIMULATOR_STATUS

    def __post_init__(self) -> None:
        if self.sim_run_id is not None:
            raise SimInputError("SIM_RUN_ID_NOT_MINTED_HERE: sim_run_id stays null until a real 26b/26f run")
        for name in ("recipe_event_id", "recipe_id", "event_id", "event_sha256", "simulation_input_sha256",
                     "replay_snapshot_sha256", "replay_config_sha256"):
            _nonblank(getattr(self, name), name)
        if self.recipe_event_id != f"{self.recipe_id}#{self.event_id}":
            raise SimInputError("recipe_event_id must be recipe_id#event_id")
        if self.system_id not in SYSTEM_REQUIREMENTS or self.route not in ROUTES:
            raise SimInputError("unknown system_id or route")
        if not (isinstance(self.reasons, tuple) and set(self.reasons) <= REASON_CODES):
            raise SimInputError("reasons must be a tuple of REASON_CODES")
        if (self.route == "SIMULATE") != (self.reasons == ()):
            raise SimInputError("SIMULATE exactly when there is no reason")
        if self.simulator_status != SIMULATOR_STATUS:
            raise SimInputError("simulator_status is fixed until 26b exists")

    def fields(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def to_canonical(self) -> dict:
        return {"record": "SIMLINK", "link_schema_version": LINK_SCHEMA_VERSION, "draft_status": STATUS,
                **{k: list(v) if isinstance(v, tuple) else v for k, v in self.fields().items()}}


def link_records(inputs: SimulationInputSet) -> tuple[SimLinkRecord, ...]:
    return tuple(SimLinkRecord(r.recipe_event_id, r.recipe_id, r.event_id, r.event_revision, r.event_sha256,
                               r.system_id, r.route, r.reasons, r.sha256, r.replay_snapshot_sha256,
                               r.replay_config_sha256) for r in inputs.records)


def write_simlink_jsonl(records: Sequence[SimLinkRecord], path: Path | str, *, root: Path = ROOT) -> Path:
    """Write draft link records to a new file outside protected areas (never ``ledgers/sim/SIMLINK_v1.jsonl``)."""
    if PROTECTED_NAME.match(Path(path).name.upper()):
        raise SimInputError("refusing a SIM / SIMLINK ledger file name for a draft")
    seen: set[tuple[str, int, str]] = set()
    for r in records:
        if not isinstance(r, SimLinkRecord):
            raise SimInputError("write_simlink_jsonl takes SimLinkRecord instances")
        key = (r.recipe_event_id, r.event_revision, r.system_id)
        if key in seen:
            raise SimInputError("duplicate (recipe_event_id, event_revision, system_id)")
        seen.add(key)
    head = {"record": "SIMLINK_HEADER", "draft_status": STATUS, "link_schema_version": LINK_SCHEMA_VERSION,
            "count": len(records), "sim_run_ids_minted": 0}
    return write_canonical_jsonl([head, *(r.to_canonical() for r in records)], path, root=root)


# ---------------------------------------------------------------- census (counts only)
def simulability_census(sets: Iterable[SimulationInputSet]) -> dict:
    """Counts per system of routes, reasons, input statuses and applicability; no ids, values or text."""
    systems: dict[str, dict] = {}
    seen: set[tuple[str, str]] = set()
    bindings = {c: 0 for c in BINDING_COUNT_CODES}
    n_sets = 0
    for s in sets:
        if not isinstance(s, SimulationInputSet):
            raise SimInputError("simulability_census takes SimulationInputSet instances")
        if (s.recipe_id, s.system_id) in seen:
            raise SimInputError("the same recipe and system are counted twice")
        seen.add((s.recipe_id, s.system_id))
        n_sets += 1
        for code, k in s.binding_counts.items():
            bindings[code] += k
        required = SYSTEM_REQUIREMENTS[s.system_id]
        c = systems.setdefault(s.system_id, {
            "events": 0, "route": {r: 0 for r in ROUTES}, "all_inputs_present": 0,
            "applicability": {a: 0 for a in APPLICABILITY_STATUSES}, "reasons": {},
            "input_status": {n: {st: 0 for st in INPUT_STATUSES} for n in required},
            "missing_input_count": {}, "synthetic_input_events": 0,
            "transaction_status": {}})
        for r in s.records:
            c["events"] += 1
            c["route"][r.route] += 1
            c["all_inputs_present"] += int(r.all_inputs_present)
            c["applicability"][r.applicability] += 1
            c["synthetic_input_events"] += int(r.synthetic_inputs)
            c["transaction_status"][r.transaction_status] = c["transaction_status"].get(r.transaction_status, 0) + 1
            for code in r.reasons:
                c["reasons"][code] = c["reasons"].get(code, 0) + 1
            missing = 0
            for i in r.inputs:
                c["input_status"][i.name][i.status] += 1
                missing += int(i.status == "UNKNOWN")
            key = str(missing)
            c["missing_input_count"][key] = c["missing_input_count"].get(key, 0) + 1
    return {"record": "SIMULABILITY_CENSUS", "census_version": CENSUS_VERSION, "draft_status": STATUS,
            "requirements_status": REQUIREMENTS_STATUS, "simulator_status": SIMULATOR_STATUS, "sets": n_sets,
            "systems": systems, "binding_counts": bindings, "sim_run_ids_minted": 0, "estimates_emitted": 0,
            "not_checked": list(NOT_CHECKED)}


def census_sha256(census: Mapping[str, Any]) -> str:
    return sha256_canonical(census)
