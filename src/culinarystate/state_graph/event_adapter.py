"""Step 18d adapter: S155 extraction ``EventGraph`` -> engine events (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c. Hard gate 16c is open; this maps the Step 17a candidate
graph (``extraction.interfaces.EventGraph`` with rc2 ``QuantityGroundingResult``s)
onto ``event_log.EngineEvent``s for the Step 18 replayer. It is the oracle /
predicted replay entry point (plan 18d); it is not the Plan 26g simulation adapter,
which consumes the replay output.

Rules
- Events keep the graph's order and are never re-sorted, so a shuffled graph shows
  invariant issues in replay. Ingredient-list lots with no producing event get one
  ``INTRO/<entity_id>`` event each, ordered ``(-1, k)`` before the first step.
- The existing invented-value auditor (``extraction.auditor.audit_outputs``) runs on
  every call. Any value it flags as invented is excluded from the engine events and
  reported as ``INVENTED_VALUE_EXCLUDED``; ``invented_count`` is carried through.
- Only entity-level MASS_G / VOLUME_ML claims traced to a supplied grounding enter
  as ``QuantityTerm``s (exact ``Fraction`` bounds; floats read by their decimal
  text). Event-level amounts are not bound to an entity (UNKNOWN, reported). COUNT
  amounts are not mapped until count-unit identity is decided (OPEN).
- Only CATEGORICAL / IDENTIFIER attribute values (codes and ids) are copied; text
  values and spans are not, so engine events and replay output carry no raw text.
- Structural gaps (missing producer, orphan allocation, unknown allocation kind,
  source mismatch) are adapter issues, never repaired.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from culinarystate.extraction.auditor import Recomputer, audit_outputs
from culinarystate.extraction.interfaces import (
    EventGraph, QuantityGroundingResult, SourceText, TraceKind, ValueClaim, ValueKind,
)

from .event_log import Allocation, EngineEvent, EventLog, EventLogError, QuantityTerm
from .replay import Issue, ReplayConfig, ReplayResult, replay_events

STATUS = "DRAFT_PENDING_16c"
ADAPTER_VERSION = "step18-extraction-adapter-0.1.0-draft"
LOT_TYPES = frozenset({"INGREDIENT_LOT"})
QUANTITY_DIM = {ValueKind.MASS_G: "g", ValueKind.VOLUME_ML: "mL"}
AMOUNT_KINDS = frozenset({ValueKind.MASS_G, ValueKind.VOLUME_ML, ValueKind.COUNT})
ATTRIBUTE_KINDS = frozenset({ValueKind.CATEGORICAL, ValueKind.IDENTIFIER})
ADAPTER_ISSUE_CODES = frozenset({"SOURCE_MISMATCH", "GRAPH_FAILED", "INVENTED_VALUE_EXCLUDED",
                                 "ENTITY_WITHOUT_PRODUCER", "ALLOC_WITHOUT_EVENT", "ALLOC_NOT_ADAPTABLE",
                                 "EVENT_NOT_ADAPTABLE", "QUANTITY_NOT_ADAPTABLE"})
ADAPTER_UNKNOWN_CODES = frozenset({"EVENT_QUANTITY_NOT_BOUND_TO_ENTITY", "COUNT_QUANTITY_NOT_MAPPED",
                                   "FRACTION_NOT_EXACT"})


def _exact(v: Any) -> Fraction | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, Fraction)):
        return Fraction(v)
    if isinstance(v, float) and math.isfinite(v):
        return Fraction(str(v))
    return None


def _bounds(value: Any) -> tuple[Fraction, Fraction] | None:
    if isinstance(value, tuple) and len(value) == 2:
        lo, hi = _exact(value[0]), _exact(value[1])
        return (lo, hi) if lo is not None and hi is not None else None
    v = _exact(value)
    return (v, v) if v is not None else None


@dataclass(frozen=True)
class AdaptedGraph:
    """Engine events for one source text plus what the adapter could not carry over."""
    source_text_id: str
    raw_sha256: str
    events: tuple[EngineEvent, ...]
    lot_accounting: Mapping[str, str]
    issues: tuple[Issue, ...]
    unknown: tuple[Issue, ...]
    audit_counts: Mapping[str, Any]
    graph_config_hash: str
    adapter_version: str = ADAPTER_VERSION

    @property
    def invented_count(self) -> int:
        return int(self.audit_counts["invented_count"])

    def log(self) -> EventLog:
        log = EventLog()
        for e in self.events:
            log.append(e)
        return log

    def replay(self, config: ReplayConfig | None = None) -> ReplayResult:
        return replay_events(self.events, config, lot_accounting=self.lot_accounting)


class _Adapter:
    def __init__(self, source: SourceText, graph: EventGraph, groundings: Sequence[QuantityGroundingResult],
                 por_records: Sequence[Mapping], recomputers: Mapping[str, Recomputer] | None,
                 trajectory: str, lot_types: frozenset[str]) -> None:
        self.graph, self.trajectory, self.lot_types = graph, trajectory, lot_types
        self.route = graph.provenance.claim_route
        self.issues: list[Issue] = []
        self.unknown: list[Issue] = []
        if graph.raw_sha256 != source.sha256 or graph.source_text_id != source.text_id:
            self.issues.append(Issue("SOURCE_MISMATCH", "source"))
        if graph.failure is not None:
            self.issues.append(Issue("GRAPH_FAILED", graph.failure.code.value))
        self.report = audit_outputs(source, [graph, *groundings], por_records=por_records, recomputers=recomputers)
        self.invented = frozenset(f.path for f in self.report.findings if f.invented)
        self.event_ids = {e.event_id for e in graph.events}
        self.produced = {p for e in graph.events for p in e.produces}
        self.types = {n.entity_id: n.entity_type for n in graph.entities}

    def usable(self, claim: ValueClaim, path: str) -> bool:
        if path in self.invented:
            self.issues.append(Issue("INVENTED_VALUE_EXCLUDED", path))
            return False
        return claim.status == "KNOWN" and claim.value is not None

    def terms(self) -> dict[str, QuantityTerm]:
        out: dict[str, QuantityTerm] = {}
        for n in self.graph.entities:
            for c in n.attributes:
                path = f"{n.entity_id}/{c.field}"
                if c.kind is ValueKind.COUNT:
                    if c.value is not None:
                        self.unknown.append(Issue("COUNT_QUANTITY_NOT_MAPPED", path))
                    continue
                dim = QUANTITY_DIM.get(c.kind)
                if dim is None or not self.usable(c, path):
                    continue
                b = _bounds(c.value)
                ref = c.trace.ref_ids[0] if c.trace.kind is TraceKind.QNT_RECORD and c.trace.ref_ids else ""
                try:
                    if b is None:
                        raise EventLogError("amount is not an exact number")
                    term = QuantityTerm(n.entity_id, dim, b[0], b[1], ref)
                except EventLogError:
                    self.issues.append(Issue("QUANTITY_NOT_ADAPTABLE", path))
                    continue
                if n.entity_id in out:
                    self.issues.append(Issue("QUANTITY_NOT_ADAPTABLE", path))
                    continue
                out[n.entity_id] = term
        for e in self.graph.events:
            for c in e.attributes:
                if c.kind in AMOUNT_KINDS and c.value is not None:
                    self.unknown.append(Issue("EVENT_QUANTITY_NOT_BOUND_TO_ENTITY", f"{e.event_id}/{c.field}"))
        return out

    def allocations(self) -> dict[str, list[Allocation]]:
        out: dict[str, list[Allocation]] = {}
        for a in self.graph.allocations:
            if a.event_id is None or a.event_id not in self.event_ids:
                self.issues.append(Issue("ALLOC_WITHOUT_EVENT", a.alloc_id))
                continue
            frac: Any = None
            if a.fraction is not None and self.usable(a.fraction, f"{a.alloc_id}/{a.fraction.field}"):
                b = _bounds(a.fraction.value)
                if b is None:
                    self.unknown.append(Issue("FRACTION_NOT_EXACT", a.alloc_id))
                else:
                    frac = b[0] if b[0] == b[1] and not isinstance(a.fraction.value, tuple) else b
            try:
                out.setdefault(a.event_id, []).append(
                    Allocation(a.alloc_id, a.kind, a.basis, a.parent_entity_id, a.child_entity_id, frac))
            except EventLogError:
                self.issues.append(Issue("ALLOC_NOT_ADAPTABLE", a.alloc_id))
        return out

    def events(self) -> tuple[EngineEvent, ...]:
        terms, allocs = self.terms(), self.allocations()
        out: list[EngineEvent] = []
        k = 0
        for n in self.graph.entities:
            if n.entity_id in self.produced:
                continue
            if n.entity_type not in self.lot_types:
                self.issues.append(Issue("ENTITY_WITHOUT_PRODUCER", n.entity_id))
                continue
            q = terms.pop(n.entity_id, None)
            out.append(EngineEvent(f"INTRO/{n.entity_id}", (-1, k), kind="INTRODUCE_LOT", produces=(n.entity_id,),
                                   produced_types=((n.entity_id, n.entity_type),), quantities=(q,) if q else (),
                                   claim_route=self.route, trajectory=self.trajectory,
                                   source_ref=f"{self.graph.source_text_id}#{n.entity_id}"))
            k += 1
        for e in self.graph.events:
            attrs: dict[str, str] = {}
            for c in e.attributes:
                if c.kind in ATTRIBUTE_KINDS and self.usable(c, f"{e.event_id}/{c.field}"):
                    attrs[c.field] = str(c.value)
            produced = tuple(dict.fromkeys(e.produces))
            try:
                out.append(EngineEvent(
                    e.event_id, e.order, kind=attrs.get("event_kind", "UNSPECIFIED"), consumes=tuple(e.consumes),
                    produces=tuple(e.produces), discards=tuple(e.discards), depends_on=tuple(e.depends_on),
                    produced_types=tuple((p, self.types[p]) for p in produced if p in self.types),
                    allocations=tuple(allocs.get(e.event_id, ())),
                    quantities=tuple(terms.pop(p) for p in produced if p in terms),
                    attributes=tuple(attrs.items()), claim_route=e.claim_route or self.route,
                    trajectory=self.trajectory, source_ref=f"{self.graph.source_text_id}#{e.event_id}"))
            except EventLogError:
                self.issues.append(Issue("EVENT_NOT_ADAPTABLE", e.event_id))
        for entity_id in sorted(terms):
            self.issues.append(Issue("QUANTITY_NOT_ADAPTABLE", entity_id))
        return tuple(out)


def adapt_event_graph(source: SourceText, graph: EventGraph, *, groundings: Sequence[QuantityGroundingResult] = (),
                      por_records: Sequence[Mapping] = (), recomputers: Mapping[str, Recomputer] | None = None,
                      trajectory: str = "PLANNED", lot_types: frozenset[str] = LOT_TYPES) -> AdaptedGraph:
    """Map one candidate graph (and its groundings) to engine events; audit first, never guess."""
    ad = _Adapter(source, graph, groundings, por_records, recomputers, trajectory, lot_types)
    events = ad.events()
    return AdaptedGraph(graph.source_text_id, graph.raw_sha256, events, dict(graph.lot_accounting),
                        tuple(ad.issues), tuple(ad.unknown), ad.report.counts(), graph.provenance.config_hash)
