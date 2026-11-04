"""Step 17a validator V4: Step-18 invariants on candidate event graphs (DRAFT_PENDING_16c).

Implements only invariants stated in the sources, on the 17a ``EventGraph``
candidate types (the Step 18 v1 ledgers do not exist yet; 16c is open):

- referenced IDs exist (SSOT §240.2 "All referenced IDs exist"); duplicate ids; in
  ``run_validators`` also across outputs (link/ref mention ids, ref entity ids; S155 review R4);
- nothing is consumed before it is produced (RD invariant 3; SSOT §240.2);
- nothing is consumed after DISCARD (RD invariant 3);
- every new intermediate has a producing event (SSOT §240.2);
- every split/merge relation has consistent parent/child references (SSOT §240.2);
- split fractions sum to <= 1 per compatible basis (RD invariant 4);
- every ingredient-list lot is accounted for (RD invariant 2);
- execution dependencies form a DAG (EVT draft ``depends_on[]`` "execution DAG"; RD DAG rules);
- mass balance only where every term is known, otherwise UNKNOWN not FAIL
  (RD invariant 5) as ``check_mass_balance`` over caller-selected terms.

Unstated details are parameters (event order basis, which entity types count as
"new intermediates", which allocation kinds partition a parent) or produce
UNKNOWN entries; the defaults are the literal reading and need H4 / 16c review.
Not implementable here and reported as not checked: inferred events never feed
explicit-only queries (RD 6, query layer); state replay from event history
(Step 18 engine); invented grams (see ``auditor``); span round-trip (see V1).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable, Iterable, Mapping, Sequence

from .interfaces import (
    EventCandidate, EventGraph, LinkResult, MentionSet, QuantityGroundingResult, ReferenceResult, SourceText,
    StageOutput,
)
from .validators import (
    ValidationReport, ValidatorIssue, Vocabulary, _Collector, v1_span_roundtrip, v2_quantity_records, v3_vocabulary,
)

STATUS = "DRAFT_PENDING_16c"
VALIDATOR_ID = "V4_STEP18_INVARIANTS"
LOT_ACCOUNTING_STATUSES = ("USED", "OPTIONAL", "ALTERNATIVE", "GARNISH", "DISCARDED", "UNRESOLVED",
                           "APPARENTLY_UNUSED")
PARTITION_KINDS = frozenset({"SPLIT", "RESERVE", "REMAINDER", "DISCARD"})
OPEN_INVARIANTS = ("INFERRED_EVENTS_NOT_IN_EXPLICIT_ONLY_QUERIES", "STATE_REPLAY_FROM_EVENT_HISTORY",
                   "MASS_BALANCE_SCOPE", "INVENTED_GRAMS_SEE_AUDITOR", "SPAN_ROUNDTRIP_SEE_V1")


def text_order(event: EventCandidate) -> tuple[int, int]:
    """Default order basis: text order (step_index, ordinal). Execution order is a caller choice."""
    return tuple(event.order)


def _bounds(value: Any) -> tuple[Fraction, Fraction] | None:
    """Exact (low, high) for a scalar or a (low, high) pair; None when not a finite number."""
    def one(v: Any) -> Fraction | None:
        if isinstance(v, bool):
            return None
        if isinstance(v, (int, Fraction)):
            return Fraction(v)
        if isinstance(v, float) and math.isfinite(v):
            return Fraction(str(v))
        return None

    if isinstance(value, tuple) and len(value) == 2:
        lo, hi = one(value[0]), one(value[1])
        return (lo, hi) if lo is not None and hi is not None else None
    v = one(value)
    return (v, v) if v is not None else None


def _ids(c: _Collector, items: Iterable[Any], attr: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in items:
        key = getattr(item, attr)
        if key in out:
            c.fail("DUPLICATE_ID", key, f"{attr} {key!r} is used more than once")
        out.setdefault(key, item)
    return out


def v4_invariants(graph: EventGraph, *, order: Callable[[EventCandidate], Any] = text_order,
                  intermediate_types: frozenset[str] = frozenset({"INTERMEDIATE"}),
                  lot_types: frozenset[str] = frozenset({"INGREDIENT_LOT"}),
                  partition_kinds: frozenset[str] = PARTITION_KINDS) -> ValidationReport:
    """V4 over one candidate graph. Returns issues / unknowns; never repairs the graph."""
    c = _Collector(VALIDATOR_ID)
    for name in OPEN_INVARIANTS:
        c.skip(name)
    events = _ids(c, graph.events, "event_id")
    entities = _ids(c, graph.entities, "entity_id")
    _ids(c, graph.allocations, "alloc_id")
    _references(c, graph, events, entities)
    producers = _producers(c, graph, events, entities)
    for n in graph.entities:
        if n.entity_type in intermediate_types and not producers.get(n.entity_id):
            c.fail("INTERMEDIATE_WITHOUT_PRODUCER", n.entity_id, "A new intermediate needs a producing event")
    _consumption_order(c, graph, events, producers, order)
    _allocations(c, graph, entities, partition_kinds)
    _lots(c, graph, entities, lot_types)
    _cycles(c, graph, events)
    return c.report()


def _references(c: _Collector, graph: EventGraph, events: Mapping, entities: Mapping) -> None:
    def need(ok: bool, path: str) -> None:
        if not ok:
            c.fail("REFERENCED_ID_MISSING", path, "Referenced id does not exist in this graph")

    for e in graph.events:
        for role in ("consumes", "produces", "discards"):
            for nid in getattr(e, role):
                need(nid in entities, f"{e.event_id}/{role}/{nid}")
        for dep in e.depends_on:
            need(dep in events, f"{e.event_id}/depends_on/{dep}")
    for n in graph.entities:
        for p in n.parent_entity_ids:
            need(p in entities, f"{n.entity_id}/parent/{p}")
        if n.created_by_event_id is not None:
            need(n.created_by_event_id in events, f"{n.entity_id}/created_by/{n.created_by_event_id}")
    for a in graph.allocations:
        need(a.parent_entity_id in entities, f"{a.alloc_id}/parent/{a.parent_entity_id}")
        need(a.child_entity_id in entities, f"{a.alloc_id}/child/{a.child_entity_id}")
        if a.event_id is not None:
            need(a.event_id in events, f"{a.alloc_id}/event/{a.event_id}")


def _producers(c: _Collector, graph: EventGraph, events: Mapping, entities: Mapping) -> dict[str, set[str]]:
    from_events: dict[str, set[str]] = {}
    for e in graph.events:
        for nid in e.produces:
            from_events.setdefault(nid, set()).add(e.event_id)
    out: dict[str, set[str]] = {}
    for nid, n in entities.items():
        declared = {n.created_by_event_id} & set(events)
        listed = from_events.get(nid, set())
        if declared and declared != listed:
            c.undecided("PRODUCER_REFERENCES_DISAGREE", nid,
                        "created_by_event_id and event produces[] name different producers")
        out[nid] = declared | listed
    return out


def _consumption_order(c: _Collector, graph: EventGraph, events: Mapping, producers: Mapping,
                       order: Callable[[EventCandidate], Any]) -> None:
    key = {eid: order(e) for eid, e in events.items()}
    discards: dict[str, set[str]] = {}
    for e in graph.events:
        for nid in e.discards:
            discards.setdefault(nid, set()).add(e.event_id)
    for e in graph.events:
        if e.event_id not in key:
            continue
        k = key[e.event_id]
        for nid in e.consumes:
            path = f"{e.event_id}/consumes/{nid}"
            prods = [p for p in producers.get(nid, ()) if p in key]
            if prods:
                first = min(key[p] for p in prods)
                if k < first:
                    c.fail("CONSUMED_BEFORE_PRODUCED", path, "Entity is consumed before its producing event")
                elif k == first and e.event_id not in prods:
                    c.undecided("ORDER_TIE", path, "Consumer and producer share one order position")
            for d in discards.get(nid, ()):
                if d == e.event_id or d not in key:
                    continue
                if k > key[d]:
                    c.fail("CONSUMED_AFTER_DISCARD", path, "Entity is consumed after it was discarded")
                elif k == key[d]:
                    c.undecided("ORDER_TIE", path, "Consumer and discard share one order position")


def _allocations(c: _Collector, graph: EventGraph, entities: Mapping, partition_kinds: frozenset[str]) -> None:
    groups: dict[tuple, list] = {}
    for a in graph.allocations:
        child = entities.get(a.child_entity_id)
        if child is not None:
            if a.parent_entity_id not in child.parent_entity_ids:
                c.fail("ALLOC_PARENT_NOT_LISTED", a.alloc_id, "Child entity does not list the allocation parent")
            if a.event_id is not None and child.created_by_event_id is not None \
                    and a.event_id != child.created_by_event_id:
                c.fail("ALLOC_EVENT_MISMATCH", a.alloc_id, "Allocation event differs from the child's producing event")
        if a.kind in partition_kinds:
            groups.setdefault((a.parent_entity_id, a.event_id, a.basis), []).append(a)
    for (parent, event_id, basis), allocs in groups.items():
        path = f"{parent}@{event_id}/{basis}"
        if basis == "UNSPECIFIED":
            c.undecided("FRACTION_BASIS_UNSPECIFIED", path, "Fractions without a basis are not summed")
            continue
        code, lo_sum, hi_sum = None, Fraction(0), Fraction(0)
        for a in allocs:
            f = a.fraction
            if f is None or f.status != "KNOWN" or f.value is None:
                code = "FRACTION_UNKNOWN"
                break
            b = _bounds(f.value)
            if b is None:
                code = "FRACTION_NOT_NUMERIC"
                break
            if b[0] > b[1]:
                code = "FRACTION_INTERVAL_INVERTED"
                break
            if b[0] < 0:
                code = "NEGATIVE_FRACTION_RULE_OPEN"
                break
            lo_sum, hi_sum = lo_sum + b[0], hi_sum + b[1]
        if code is not None:
            c.undecided(code, path, "Split-fraction sum cannot be decided")
        elif lo_sum > 1:
            c.fail("SPLIT_FRACTIONS_EXCEED_ONE", path, "Split fractions sum to more than 1 on one basis")
        elif hi_sum > 1:
            c.undecided("FRACTION_INTERVAL_UNDECIDED", path, "Interval fractions may or may not exceed 1")


def _lots(c: _Collector, graph: EventGraph, entities: Mapping, lot_types: frozenset[str]) -> None:
    lots = {nid for nid, n in entities.items() if n.entity_type in lot_types}
    for nid in sorted(lots):
        status = graph.lot_accounting.get(nid)
        if status is None:
            c.fail("LOT_UNACCOUNTED", nid, "Ingredient-list lot has no accounting status")
        elif status not in LOT_ACCOUNTING_STATUSES:
            c.fail("LOT_STATUS_INVALID", nid, f"{status!r} is not a lot accounting status")
    for nid in sorted(set(graph.lot_accounting) - lots):
        c.fail("LOT_ACCOUNTING_UNKNOWN_ENTITY", nid, "Accounting entry does not name an ingredient-list lot")


def _cycles(c: _Collector, graph: EventGraph, events: Mapping) -> None:
    deps = {e.event_id: [d for d in e.depends_on if d in events] for e in graph.events}
    state: dict[str, int] = {}

    def visit(node: str) -> bool:
        state[node] = 1
        for nxt in deps.get(node, ()):
            if state.get(nxt) == 1 or (state.get(nxt) is None and visit(nxt)):
                return True
        state[node] = 2
        return False

    for node in deps:
        if state.get(node) is None and visit(node):
            c.fail("DEPENDS_ON_CYCLE", node, "Execution dependencies contain a cycle")
            return


# ------------------------------------------------------------------ mass balance
@dataclass(frozen=True)
class MassBalanceResult:
    status: str  # PASS | FAIL | UNKNOWN
    reason: str | None = None
    input_bounds: tuple[Fraction, Fraction] | None = None
    output_bounds: tuple[Fraction, Fraction] | None = None


def check_mass_balance(inputs: Sequence[Any], outputs: Sequence[Any]) -> MassBalanceResult:
    """Exact conservation check between caller-selected terms (scalars or (low, high) pairs).

    Any missing, non-numeric or negative term gives UNKNOWN, never FAIL. FAIL only when
    the summed intervals are disjoint. Which events must conserve mass, and any
    tolerance, are not stated in the sources (OPEN): no tolerance is applied.
    """
    if not inputs or not outputs:
        return MassBalanceResult("UNKNOWN", "NO_TERMS")
    sums = []
    for terms in (inputs, outputs):
        lo = hi = Fraction(0)
        for term in terms:
            if term is None:
                return MassBalanceResult("UNKNOWN", "TERM_UNKNOWN")
            b = _bounds(term)
            if b is None or b[0] > b[1]:
                return MassBalanceResult("UNKNOWN", "TERM_NOT_NUMERIC")
            if b[0] < 0:
                return MassBalanceResult("UNKNOWN", "NEGATIVE_TERM_RULE_OPEN")
            lo, hi = lo + b[0], hi + b[1]
        sums.append((lo, hi))
    (ilo, ihi), (olo, ohi) = sums
    if ihi < olo or ohi < ilo:
        return MassBalanceResult("FAIL", "DISJOINT", sums[0], sums[1])
    if ilo == ihi == olo == ohi:
        return MassBalanceResult("PASS", None, sums[0], sums[1])
    return MassBalanceResult("UNKNOWN", "INTERVALS_OVERLAP", sums[0], sums[1])


# ------------------------------------------------------------------ bundle
def run_validators(source: SourceText, outputs: Iterable[StageOutput], *, qnt_schema: Mapping | None = None,
                   vocabularies: Mapping[str, Vocabulary] | None = None, mention_labels: frozenset[str] | None = None,
                   id_sets: Mapping[str, frozenset[str]] | None = None,
                   **v4_options: Any) -> dict[str, ValidationReport]:
    """Run V1-V4 over one source text's outputs. V2 covers rc2 QNT records when a schema is supplied."""
    outs = list(outputs)
    reports = {"V1": v1_span_roundtrip(source, outs)}
    groundings = [o for o in outs if isinstance(o, QuantityGroundingResult)]
    if qnt_schema is None:
        reports["V2"] = ValidationReport("V2_SCHEMA", not_checked=("QNT_SCHEMA_NOT_SUPPLIED",))
    else:
        reports["V2"] = v2_quantity_records(groundings, qnt_schema)
    reports["V3"] = v3_vocabulary(outs, vocabularies, mention_labels=mention_labels, id_sets=id_sets)
    c = _Collector(VALIDATOR_ID)
    graphs = [(i, o) for i, o in enumerate(outs) if isinstance(o, EventGraph)]
    if not graphs:
        c.skip("NO_EVENT_GRAPH")
    for i, g in graphs:
        sub = v4_invariants(g, **v4_options)
        c.issues.extend(ValidatorIssue(x.validator, x.code, f"outputs[{i}]/{x.path}", x.message) for x in sub.issues)
        c.unknown.extend(ValidatorIssue(x.validator, x.code, f"outputs[{i}]/{x.path}", x.message)
                         for x in sub.unknown)
        for name in sub.not_checked:
            c.skip(name)
    _cross_references(c, outs)
    reports["V4"] = c.report()
    return reports


def _cross_references(c: _Collector, outs: Sequence[StageOutput]) -> None:
    """S155 review R4: ids referenced across outputs exist ("All referenced IDs exist", SSOT §240.2).

    Link / reference mention ids must name a mention of a supplied MentionSet; reference
    candidates and antecedents must name entities of a supplied EventGraph. Without the
    target output the check is reported as not checked.
    """
    mention_ids = {m.mention_id for o in outs if isinstance(o, MentionSet) for m in o.mentions}
    has_mentions = any(isinstance(o, MentionSet) for o in outs)
    entity_ids = {n.entity_id for o in outs if isinstance(o, EventGraph) for n in o.entities}
    has_graph = any(isinstance(o, EventGraph) for o in outs)
    for i, out in enumerate(outs):
        if not isinstance(out, (LinkResult, ReferenceResult)):
            continue
        if not has_mentions:
            c.skip("CROSS_REF_NO_MENTION_SET")
        elif out.mention_id not in mention_ids:
            c.fail("REFERENCED_ID_MISSING", f"outputs[{i}]/mention/{out.mention_id}",
                   "Referenced mention id does not exist in the supplied mention sets")
        if not isinstance(out, ReferenceResult):
            continue
        if not has_graph:
            c.skip("CROSS_REF_NO_EVENT_GRAPH")
            continue
        for nid in dict.fromkeys((*out.candidates, *out.antecedent_ids)):
            if nid not in entity_ids:
                c.fail("REFERENCED_ID_MISSING", f"outputs[{i}]/entity/{nid}",
                       "Referenced entity id does not exist in the supplied event graphs")
