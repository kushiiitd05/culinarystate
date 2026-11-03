"""Step 17a common extraction interface (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c. Hard gate 16c (Step 16 schema pack v1) is open, so these
types are an engineering draft for Rung A (17b) and later rungs to implement. They are
not a frozen ledger schema, carry no human verification and read or write no file.

Common interface (Plan Step 17-M; RD B.5): six stage functions

    extract_mentions(source, config) -> MentionSet
    link(source, mention, config) -> LinkResult
    parse_quantity(source, span, config, *, source_metadata, locale=None) -> QuantityParseResult
    ground_quantity(source, span, context, config, *, schema, result_id) -> QuantityGroundingResult
    build_events(source, mentions, links, quantities, config) -> EventGraph
    resolve_refs(source, mentions, graph, config) -> tuple[ReferenceResult, ...]

Each returns an explicit failure result (``Failure`` with one of UNRESOLVED,
NO_VALID_CANDIDATE, PARSE_FAIL, NO_COMPATIBLE_RECORD), never a guess. Each output
carries a ``Provenance`` (stage, rung_id, config/model hash, schema_version,
claim_route, annotation provenance). A label never annotated is MISSING, not O.

Offsets are half-open ``[char_start, char_end)`` Python ``str`` indices (Unicode code
points) into ``SourceText.raw``; the raw text is identified by the SHA-256 of its
UTF-8 bytes. Every semantic output value is a ``ValueClaim`` with a ``Trace`` so the
auditor can check it against the raw span, a deterministic rule, a candidate set or a
grounded rc2 QNT record. Draft choices that need H4/16c review are listed in the
Step 17a report, not decided here.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from enum import Enum
from fractions import Fraction
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Mapping, Protocol, Sequence, Union, runtime_checkable

from culinarystate.quantity.draft_contract import CLAIM_ROUTES

if TYPE_CHECKING:  # pragma: no cover - typing only
    from culinarystate.quantity.parse_adapter import ParsedQuantityV2
    from culinarystate.quantity.rc2_grounding import GroundingContext, GroundingResult

STATUS = "DRAFT_PENDING_16c"
INTERFACE_SCHEMA_VERSION = "step17a-interface-0.1.0-draft"
OFFSET_UNIT = "PYTHON_STR_CODEPOINT"
STAGES = ("extract_mentions", "link", "parse_quantity", "ground_quantity", "build_events", "resolve_refs")

# Draft mapping used when an output's origin is derived from its claim route
# (pairs follow the rc2 grounding/history conventions; needs H4 confirmation).
ROUTE_TO_ORIGIN = {"EXPLICIT": "EXPLICIT_SOURCE", "INFERRED_RULE": "DERIVED_DETERMINISTIC",
                   "INFERRED_LLM": "INFERRED_LLM", "MODEL": "MODEL_ESTIMATED", "SIMULATED": "SIMULATED"}
assert set(ROUTE_TO_ORIGIN) == set(CLAIM_ROUTES)

# Mention label lists as written in the sources; neither is a registry (OPEN, needs H4).
MENTION_LABELS_PLAN_17M = ("ACTION", "FOOD_MENTION", "INTERMEDIATE_MENTION", "TOOL", "DURATION", "TEMPERATURE",
                           "ENDPOINT", "MEDIUM", "QUANTITY_IN_STEP", "CONDITION_CUE")
MENTION_LABELS_SSOT_245_2 = ("FOOD", "QUANTITY", "UNIT", "FORM", "STATE", "TOOL", "ACTION", "DURATION",
                             "TEMPERATURE")


class InterfaceError(ValueError):
    """An output violates the structural interface contract (programming error, not a data failure)."""


class FailureCode(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    NO_VALID_CANDIDATE = "NO_VALID_CANDIDATE"
    PARSE_FAIL = "PARSE_FAIL"
    NO_COMPATIBLE_RECORD = "NO_COMPATIBLE_RECORD"


# Draft per-stage allowance (the plan lists the four codes, not which stage uses which).
ALLOWED_FAILURES: dict[str, frozenset[FailureCode]] = {
    "extract_mentions": frozenset({FailureCode.UNRESOLVED, FailureCode.PARSE_FAIL}),
    "link": frozenset({FailureCode.NO_VALID_CANDIDATE, FailureCode.UNRESOLVED}),
    "parse_quantity": frozenset({FailureCode.PARSE_FAIL}),
    "ground_quantity": frozenset({FailureCode.NO_COMPATIBLE_RECORD, FailureCode.UNRESOLVED, FailureCode.PARSE_FAIL}),
    "build_events": frozenset({FailureCode.UNRESOLVED}),
    "resolve_refs": frozenset({FailureCode.UNRESOLVED, FailureCode.NO_VALID_CANDIDATE}),
}


def _nonblank(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InterfaceError(f"{name} must be a nonblank string")


def sha256_text(raw: str) -> str:
    """SHA-256 hex digest of the UTF-8 bytes of ``raw``."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def config_hash(config: Mapping[str, Any]) -> str:
    """Canonical JSON (sorted keys, no NaN/inf) SHA-256 of a configuration mapping."""
    try:
        blob = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False,
                          default=_json_default)
    except (TypeError, ValueError) as exc:
        raise InterfaceError(f"Configuration is not canonical JSON: {exc}") from exc
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (frozenset, set)):
        return sorted(obj)
    if isinstance(obj, tuple):
        return list(obj)
    raise TypeError(f"{type(obj).__name__} is not JSON serialisable")


@dataclass(frozen=True)
class Failure:
    """Explicit failure result. ``reason`` is a short machine code; ``detail`` holds codes only."""
    code: FailureCode
    reason: str
    detail: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.code, FailureCode):
            raise InterfaceError("Failure code must be a FailureCode member")
        _nonblank(self.reason, "Failure reason")


def _check_failure(stage: str, failure: Failure | None) -> None:
    if failure is not None and failure.code not in ALLOWED_FAILURES[stage]:
        raise InterfaceError(f"{failure.code.value} is not an allowed failure for {stage}")


def _check_stage(stage: str, provenance: "Provenance") -> None:
    if not isinstance(provenance, Provenance) or provenance.stage != stage:
        raise InterfaceError(f"Output of {stage} needs provenance for stage {stage}")


@dataclass(frozen=True)
class SourceText:
    """Raw text preserved byte-for-byte with its hash. Normalised views are separate."""
    text_id: str
    raw: str
    sha256: str

    def __post_init__(self) -> None:
        _nonblank(self.text_id, "text_id")
        if not isinstance(self.raw, str):
            raise InterfaceError("raw must be a string")
        if self.sha256 != sha256_text(self.raw):
            raise InterfaceError("RAW_HASH_MISMATCH: sha256 must equal SHA-256 of the UTF-8 raw text")

    @classmethod
    def from_raw(cls, text_id: str, raw: str) -> "SourceText":
        return cls(text_id, raw, sha256_text(raw))


@dataclass(frozen=True)
class Span:
    """One or more ordered, non-overlapping raw segments with their claimed texts.

    ``texts[i]`` is what the producer claims ``raw[start_i:end_i]`` is; V1 checks it.
    A multi-segment (discontinuous) span needs an explicit ``join_policy`` separator
    used for display only.
    """
    text_id: str
    raw_sha256: str
    segments: tuple[tuple[int, int], ...]
    texts: tuple[str, ...]
    join_policy: str | None = None

    @property
    def char_start(self) -> int:
        return self.segments[0][0]

    @property
    def char_end(self) -> int:
        return self.segments[-1][1]

    @property
    def surface(self) -> str:
        if len(self.texts) == 1:
            return self.texts[0]
        return (self.join_policy or "").join(self.texts)

    @classmethod
    def of(cls, source: SourceText, start: int, end: int) -> "Span":
        return cls.multi(source, [(start, end)])

    @classmethod
    def multi(cls, source: SourceText, segments: Sequence[tuple[int, int]],
              join_policy: str | None = None) -> "Span":
        segs = tuple((int(s), int(e)) for s, e in segments)
        problem = segment_problem(segs, len(source.raw), join_policy)
        if problem:
            raise InterfaceError(problem)
        return cls(source.text_id, source.sha256, segs, tuple(source.raw[s:e] for s, e in segs), join_policy)


def segment_problem(segments: Sequence[tuple[int, int]], raw_len: int, join_policy: str | None) -> str | None:
    """Return an issue code for malformed segments, else None (shared with V1)."""
    if not segments:
        return "SPAN_EMPTY"
    prev_end = None
    for seg in segments:
        if not (isinstance(seg, tuple) and len(seg) == 2 and all(type(x) is int for x in seg)):
            return "SPAN_SEGMENT_TYPE"
        s, e = seg
        if not 0 <= s < e <= raw_len:
            return "SPAN_OUT_OF_BOUNDS"
        if prev_end is not None and s < prev_end:
            return "SPAN_SEGMENTS_UNORDERED_OR_OVERLAPPING"
        prev_end = e
    if len(segments) > 1 and join_policy is None:
        return "SPAN_JOIN_POLICY_MISSING"
    return None


class ValueKind(str, Enum):
    CATEGORICAL = "CATEGORICAL"
    IDENTIFIER = "IDENTIFIER"
    TEXT = "TEXT"
    COUNT = "COUNT"
    FRACTION = "FRACTION"
    MASS_G = "MASS_G"
    VOLUME_ML = "VOLUME_ML"
    TEMPERATURE = "TEMPERATURE"
    DURATION = "DURATION"
    PH = "PH"
    OTHER_NUMERIC = "OTHER_NUMERIC"


MAGNITUDE_KINDS = frozenset({ValueKind.MASS_G, ValueKind.VOLUME_ML, ValueKind.TEMPERATURE, ValueKind.DURATION,
                             ValueKind.PH})
NUMERIC_KINDS = MAGNITUDE_KINDS | {ValueKind.COUNT, ValueKind.FRACTION, ValueKind.OTHER_NUMERIC}


class TraceKind(str, Enum):
    SPAN_LITERAL = "SPAN_LITERAL"            # value appears literally in the span text
    SPAN_RULE = "SPAN_RULE"                  # deterministic rule ``rule_id`` applied to the span text
    CANDIDATE_SELECTION = "CANDIDATE_SELECTION"  # value chosen among ``candidates``
    QNT_RECORD = "QNT_RECORD"                # value read from a grounded rc2 QNT record (Q0 or POR)
    REGISTRY_LABEL = "REGISTRY_LABEL"        # categorical code assigned to the span text
    NONE = "NONE"                            # untraced: always flagged by the auditor


@dataclass(frozen=True)
class Trace:
    kind: TraceKind
    rule_id: str | None = None
    ref_ids: tuple[str, ...] = ()
    candidates: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, TraceKind):
            raise InterfaceError("Trace kind must be a TraceKind member")


Scalar = Union[str, int, float, Fraction]
ClaimValue = Union[Scalar, tuple[Scalar, Scalar], None]


@dataclass(frozen=True)
class ValueClaim:
    """One semantic output value. ``value`` may be a (low, high) pair for an interval.

    Construction checks types only; vocabulary (V3) and traceability (auditor) are
    checked separately so that bad outputs can be reported rather than hidden.
    """
    field: str
    kind: ValueKind
    value: ClaimValue
    status: str = "KNOWN"
    origin: str = "UNKNOWN"
    claim_route: str = "INFERRED_RULE"
    span: Span | None = None
    trace: Trace = Trace(TraceKind.NONE)
    unit: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.field, "Claim field")
        if not isinstance(self.kind, ValueKind):
            raise InterfaceError("Claim kind must be a ValueKind member")
        if not isinstance(self.trace, Trace):
            raise InterfaceError("Claim trace must be a Trace")

    def qualified(self, prefix: str) -> "ValueClaim":
        return replace(self, field=f"{prefix}/{self.field}")


@dataclass(frozen=True)
class Provenance:
    stage: str
    rung_id: str
    config_hash: str
    schema_version: str
    claim_route: str
    annotated_labels: frozenset[str] | None = None
    annotation_mode: str | None = None
    model_id: str | None = None
    offset_unit: str = OFFSET_UNIT
    status: str = STATUS

    def label_status(self, label: str) -> str:
        """ANNOTATED when the producer covered ``label``; otherwise MISSING (never O / negative)."""
        return "ANNOTATED" if self.annotated_labels is not None and label in self.annotated_labels else "MISSING"


@dataclass(frozen=True)
class StageConfig:
    """Rung configuration. ``config_hash`` covers rung, params, model id, schema version, claim route and
    annotation provenance (labels, mode): every field that changes the outputs (S155 review R3)."""
    rung_id: str
    params: Mapping[str, Any]
    claim_route: str
    schema_version: str = INTERFACE_SCHEMA_VERSION
    model_id: str | None = None
    annotated_labels: frozenset[str] | None = None
    annotation_mode: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.rung_id, "rung_id")
        _nonblank(self.claim_route, "claim_route")

    @property
    def config_hash(self) -> str:
        labels = None if self.annotated_labels is None else sorted(self.annotated_labels)
        return config_hash({"rung_id": self.rung_id, "params": dict(self.params), "model_id": self.model_id,
                            "schema_version": self.schema_version, "claim_route": self.claim_route,
                            "annotated_labels": labels, "annotation_mode": self.annotation_mode})

    def provenance(self, stage: str) -> Provenance:
        if stage not in STAGES:
            raise InterfaceError(f"Unknown stage {stage!r}")
        return Provenance(stage, self.rung_id, self.config_hash, self.schema_version, self.claim_route,
                          self.annotated_labels, self.annotation_mode, self.model_id)


def _derived_claim(field_name: str, kind: ValueKind, value: ClaimValue, provenance: Provenance,
                   span: Span | None, trace: Trace) -> ValueClaim:
    route = provenance.claim_route
    return ValueClaim(field=field_name, kind=kind, value=value, origin=ROUTE_TO_ORIGIN.get(route, "UNKNOWN"),
                      claim_route=route, span=span, trace=trace)


def _claim_spans(claims: Iterable[ValueClaim]) -> Iterator[Span]:
    for c in claims:
        if c.span is not None:
            yield c.span


# ---------------------------------------------------------------- stage outputs
@dataclass(frozen=True)
class Mention:
    mention_id: str
    label: str
    span: Span
    attributes: tuple[ValueClaim, ...] = ()

    def __post_init__(self) -> None:
        _nonblank(self.mention_id, "mention_id")
        _nonblank(self.label, "mention label")


@dataclass(frozen=True)
class MentionSet:
    """Output of ``extract_mentions``. An empty tuple is a valid "no mentions" result."""
    source_text_id: str
    raw_sha256: str
    mentions: tuple[Mention, ...]
    provenance: Provenance
    failure: Failure | None = None
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _check_stage("extract_mentions", self.provenance)
        _check_failure("extract_mentions", self.failure)
        if self.failure is not None and self.mentions:
            raise InterfaceError("A failed extract_mentions result carries no partial mentions")
        ids = [m.mention_id for m in self.mentions]
        if len(ids) != len(set(ids)):
            raise InterfaceError("mention_id values must be unique")

    def claims(self) -> tuple[ValueClaim, ...]:
        out: list[ValueClaim] = []
        for m in self.mentions:
            out.append(_derived_claim(f"{m.mention_id}/label", ValueKind.CATEGORICAL, m.label, self.provenance,
                                      m.span, Trace(TraceKind.REGISTRY_LABEL)))
            out.extend(a.qualified(m.mention_id) for a in m.attributes)
        return tuple(out)

    def spans(self) -> tuple[Span, ...]:
        out: list[Span] = []
        for m in self.mentions:
            out.append(m.span)
            out.extend(_claim_spans(m.attributes))
        return tuple(out)


@dataclass(frozen=True)
class LinkCandidate:
    """A candidate concept. ``score`` is a model diagnostic, not an audited output value."""
    concept_id: str
    score: float | None = None


@dataclass(frozen=True)
class LinkResult:
    mention_id: str
    span: Span
    candidates: tuple[LinkCandidate, ...]
    provenance: Provenance
    selected_id: str | None = None
    failure: Failure | None = None
    registry_snapshot: str | None = None

    def __post_init__(self) -> None:
        _check_stage("link", self.provenance)
        _check_failure("link", self.failure)
        if (self.selected_id is None) == (self.failure is None):
            raise InterfaceError("link returns exactly one of selected_id or failure")
        if self.selected_id is not None and self.selected_id not in self.candidate_ids:
            raise InterfaceError("selected_id must be one of the supplied candidates (never a nearest-ID guess)")

    @property
    def candidate_ids(self) -> tuple[str, ...]:
        return tuple(c.concept_id for c in self.candidates)

    def claims(self) -> tuple[ValueClaim, ...]:
        if self.selected_id is None:
            return ()
        return (_derived_claim(f"{self.mention_id}/link", ValueKind.IDENTIFIER, self.selected_id, self.provenance,
                               self.span, Trace(TraceKind.CANDIDATE_SELECTION, candidates=self.candidate_ids)),)

    def spans(self) -> tuple[Span, ...]:
        return (self.span,)


@dataclass(frozen=True)
class QuantityParseResult:
    """Output of ``parse_quantity``. AST values are audited by deterministic re-parse."""
    result_id: str
    span: Span
    expression: str
    source_metadata: Mapping[str, Any]
    provenance: Provenance
    ast: dict | None = None
    arithmetic_status: str | None = None
    flags: tuple[str, ...] = ()
    adapter_version: str | None = None
    locale: str | None = None
    failure: Failure | None = None
    parsed: "ParsedQuantityV2 | None" = None

    def __post_init__(self) -> None:
        _nonblank(self.result_id, "result_id")
        _check_stage("parse_quantity", self.provenance)
        _check_failure("parse_quantity", self.failure)
        if self.failure is None and self.ast is None:
            raise InterfaceError("A successful parse_quantity result carries an AST")

    def claims(self) -> tuple[ValueClaim, ...]:
        return ()

    def spans(self) -> tuple[Span, ...]:
        return (self.span,)


_CHANNELS = (("mass_g", ValueKind.MASS_G), ("volume_ml", ValueKind.VOLUME_ML), ("count", ValueKind.COUNT))


def channel_value(channel: Mapping | None) -> ClaimValue:
    """Value of an rc2 measurement channel: scalar for MEASURED, (low, high) for RANGE, else None."""
    if not isinstance(channel, Mapping):
        return None
    if channel.get("status") == "MEASURED":
        return channel.get("value")
    if channel.get("status") == "RANGE":
        return (channel.get("low"), channel.get("high"))
    return None


@dataclass(frozen=True)
class QuantityGroundingResult:
    """Output of ``ground_quantity``. The rc2 record is always kept (symbolic amount retained)."""
    result_id: str
    span: Span
    provenance: Provenance
    record: dict | None = None
    grounding: "GroundingResult | None" = None
    failure: Failure | None = None

    def __post_init__(self) -> None:
        _nonblank(self.result_id, "result_id")
        _check_stage("ground_quantity", self.provenance)
        _check_failure("ground_quantity", self.failure)
        if self.failure is None and self.record is None:
            raise InterfaceError("A successful ground_quantity result carries its rc2 record")

    @property
    def issues(self) -> tuple:
        """rc2 validator and invented-value audit issues reported by the pipeline (never hidden)."""
        return tuple(self.grounding.issues) if self.grounding is not None else ()

    def claims(self) -> tuple[ValueClaim, ...]:
        if self.record is None:
            return ()
        out = []
        meta = self.record.get("field_metadata") or {}
        for key, kind in _CHANNELS:
            channel = self.record.get(key)
            value = channel_value(channel)
            if value is None:
                continue
            m = meta.get("/" + key) or {}
            out.append(ValueClaim(field=f"{self.result_id}/{key}", kind=kind, value=value,
                                  origin=m.get("origin", "UNKNOWN"),
                                  claim_route=m.get("claim_route", self.provenance.claim_route), span=self.span,
                                  trace=Trace(TraceKind.QNT_RECORD, ref_ids=(self.result_id,)),
                                  unit=channel.get("unit")))
        return tuple(out)

    def spans(self) -> tuple[Span, ...]:
        return (self.span,)


@dataclass(frozen=True)
class EventCandidate:
    """Atomic event candidate. ``order`` is text order (step_index, ordinal); ids are local, never minted."""
    event_id: str
    order: tuple[int, int]
    span: Span | None = None
    consumes: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    discards: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    attributes: tuple[ValueClaim, ...] = ()
    claim_route: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.event_id, "event_id")


@dataclass(frozen=True)
class EntityCandidate:
    entity_id: str
    entity_type: str
    lifecycle: str
    parent_entity_ids: tuple[str, ...] = ()
    created_by_event_id: str | None = None
    span: Span | None = None
    attributes: tuple[ValueClaim, ...] = ()

    def __post_init__(self) -> None:
        _nonblank(self.entity_id, "entity_id")


@dataclass(frozen=True)
class AllocationCandidate:
    """Split / reserve / remainder / recombine / discard relation (ALLOC draft enums)."""
    alloc_id: str
    kind: str
    basis: str
    parent_entity_id: str
    child_entity_id: str
    event_id: str | None = None
    fraction: ValueClaim | None = None

    def __post_init__(self) -> None:
        _nonblank(self.alloc_id, "alloc_id")


@dataclass(frozen=True)
class EventGraph:
    """Output of ``build_events``: candidate events, entities, allocations and lot accounting."""
    source_text_id: str
    raw_sha256: str
    events: tuple[EventCandidate, ...]
    entities: tuple[EntityCandidate, ...]
    allocations: tuple[AllocationCandidate, ...]
    lot_accounting: Mapping[str, str]
    provenance: Provenance
    failure: Failure | None = None
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _check_stage("build_events", self.provenance)
        _check_failure("build_events", self.failure)

    def claims(self) -> tuple[ValueClaim, ...]:
        out: list[ValueClaim] = []
        for e in self.events:
            out.extend(a.qualified(e.event_id) for a in e.attributes)
        for n in self.entities:
            out.extend(a.qualified(n.entity_id) for a in n.attributes)
        for a in self.allocations:
            if a.fraction is not None:
                out.append(a.fraction.qualified(a.alloc_id))
        return tuple(out)

    def spans(self) -> tuple[Span, ...]:
        out: list[Span] = [e.span for e in self.events if e.span is not None]
        out.extend(n.span for n in self.entities if n.span is not None)
        out.extend(_claim_spans(self.claims()))
        return tuple(out)


@dataclass(frozen=True)
class ReferenceResult:
    """Output of ``resolve_refs`` for one referring mention."""
    mention_id: str
    span: Span
    candidates: tuple[str, ...]
    provenance: Provenance
    antecedent_ids: tuple[str, ...] = ()
    failure: Failure | None = None

    def __post_init__(self) -> None:
        _check_stage("resolve_refs", self.provenance)
        _check_failure("resolve_refs", self.failure)
        if bool(self.antecedent_ids) == (self.failure is not None):
            raise InterfaceError("resolve_refs returns antecedents or an explicit failure, not both or neither")
        if not set(self.antecedent_ids) <= set(self.candidates):
            raise InterfaceError("Antecedents must be among the supplied candidates")

    def claims(self) -> tuple[ValueClaim, ...]:
        return tuple(_derived_claim(f"{self.mention_id}/antecedent/{i}", ValueKind.IDENTIFIER, a, self.provenance,
                                    self.span, Trace(TraceKind.CANDIDATE_SELECTION, candidates=self.candidates))
                     for i, a in enumerate(self.antecedent_ids))

    def spans(self) -> tuple[Span, ...]:
        return (self.span,)


StageOutput = Union[MentionSet, LinkResult, QuantityParseResult, QuantityGroundingResult, EventGraph,
                    ReferenceResult]


def iter_claims(outputs: Iterable[StageOutput]) -> Iterator[ValueClaim]:
    for out in outputs:
        yield from out.claims()


def iter_spans(output: StageOutput | Iterable[StageOutput]) -> Iterator[Span]:
    items = [output] if hasattr(output, "spans") else list(output)
    for out in items:
        yield from out.spans()


# ---------------------------------------------------------------- stage protocols
class ExtractMentions(Protocol):
    def __call__(self, source: SourceText, config: StageConfig) -> MentionSet: ...


class Link(Protocol):
    def __call__(self, source: SourceText, mention: Mention, config: StageConfig) -> LinkResult: ...


class ParseQuantity(Protocol):
    def __call__(self, source: SourceText, span: Span, config: StageConfig, *, source_metadata: Mapping,
                 locale: str | None = None) -> QuantityParseResult: ...


class GroundQuantity(Protocol):
    def __call__(self, source: SourceText, span: Span, context: "GroundingContext", config: StageConfig, *,
                 schema: Mapping, result_id: str) -> QuantityGroundingResult: ...


class BuildEvents(Protocol):
    def __call__(self, source: SourceText, mentions: MentionSet, links: Sequence[LinkResult],
                 quantities: Sequence[QuantityGroundingResult], config: StageConfig) -> EventGraph: ...


class ResolveRefs(Protocol):
    def __call__(self, source: SourceText, mentions: MentionSet, graph: EventGraph,
                 config: StageConfig) -> tuple[ReferenceResult, ...]: ...


@runtime_checkable
class RungInterface(Protocol):
    """A rung implements all six stages (quantity stages may reuse ``quantity_stages``)."""

    def extract_mentions(self, source: SourceText, config: StageConfig) -> MentionSet: ...

    def link(self, source: SourceText, mention: Mention, config: StageConfig) -> LinkResult: ...

    def parse_quantity(self, source: SourceText, span: Span, config: StageConfig, *, source_metadata: Mapping,
                       locale: str | None = None) -> QuantityParseResult: ...

    def ground_quantity(self, source: SourceText, span: Span, context: "GroundingContext", config: StageConfig, *,
                        schema: Mapping, result_id: str) -> QuantityGroundingResult: ...

    def build_events(self, source: SourceText, mentions: MentionSet, links: Sequence[LinkResult],
                     quantities: Sequence[QuantityGroundingResult], config: StageConfig) -> EventGraph: ...

    def resolve_refs(self, source: SourceText, mentions: MentionSet, graph: EventGraph,
                     config: StageConfig) -> tuple[ReferenceResult, ...]: ...
