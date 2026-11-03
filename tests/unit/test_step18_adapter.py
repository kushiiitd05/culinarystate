"""Step 18d adapter: S155 extraction EventGraph -> engine events -> replay (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c (hard gate 16c open). Synthetic text and the synthetic
Rung A lexicon of the S155 tests only; outputs are SYNTHETIC_NOT_GOLD. No EVT /
ENTITY / STATE ledger row is read or written. The adapter never re-sorts events,
never binds an amount it cannot trace, runs the existing invented-value auditor and
excludes any value it flags; outputs carry ids only, never raw text.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.extraction import rung_a as ra
from culinarystate.extraction import rung_a_lexicon as lx
from culinarystate.extraction.interfaces import (
    AllocationCandidate, EntityCandidate, EventCandidate, EventGraph, SourceText, Span, StageConfig, Trace, TraceKind,
    ValueClaim, ValueKind,
)
from culinarystate.extraction.invariants import v4_invariants
from culinarystate.state_graph import event_adapter as ad
from culinarystate.state_graph.event_adapter import adapt_event_graph
from culinarystate.state_graph.replay import ReplayConfig, replay_log
from tests.unit.test_step17b_rung_a import SCHEMA, SYN, TEXT

CFG = StageConfig("RA_TEST_GRAPH", {}, "INFERRED_RULE")


@pytest.fixture(scope="module")
def rung() -> ra.RungA:
    return ra.RungA(lx.build_lexicon(**SYN))


def run(rung: ra.RungA, raw: str):
    s = SourceText.from_raw("SYN-18", raw)
    return s, rung.run(s, rung.config(), schema=SCHEMA)


def adapt(rung, s, out, **kw):
    return adapt_event_graph(s, out.graph, groundings=out.quantities, recomputers=rung.recomputers(), **kw)


def codes(items) -> set[str]:
    return {i.code for i in items}


def graph(s: SourceText, events=(), entities=(), allocations=(), lots=None) -> EventGraph:
    lots = lots if lots is not None else {n.entity_id: "USED" for n in entities if n.entity_type == "INGREDIENT_LOT"}
    return EventGraph(s.text_id, s.sha256, tuple(events), tuple(entities), tuple(allocations), lots,
                      CFG.provenance("build_events"))


def lot(eid: str, attrs=()) -> EntityCandidate:
    return EntityCandidate(eid, "INGREDIENT_LOT", "INCORPORATED", attributes=tuple(attrs))


def mid(eid: str, parents: tuple[str, ...], by: str, etype: str = "INTERMEDIATE") -> EntityCandidate:
    return EntityCandidate(eid, etype, "ACTIVE", parents, by)


# ---------------------------------------------------------------- module
def test_module_is_draft_pending_16c_and_imports_no_pandas():
    assert ad.STATUS == "DRAFT_PENDING_16c"
    src = Path(ad.__file__).read_text(encoding="utf-8")
    assert "DRAFT_PENDING_16c" in src.splitlines()[0]
    assert "import pandas" not in src and "import numpy" not in src


# ---------------------------------------------------------------- Rung A end to end
def test_rung_a_graph_replays_cleanly_and_deterministically(rung):
    s, out = run(rung, TEXT)
    a = adapt(rung, s, out)
    assert a.issues == () and a.invented_count == 0
    lots = [n.entity_id for n in out.graph.entities if n.entity_type == "INGREDIENT_LOT"]
    assert [e.event_id for e in a.events] == [f"INTRO/{x}" for x in lots] + [e.event_id for e in out.graph.events]
    r1, r2 = a.replay(), adapt(rung, s, out).replay()
    assert r1.to_jsonl() == r2.to_jsonl() and r1.issues == ()
    assert all(r1.snapshot.current(x).lifecycle == "INCORPORATED" for x in lots)
    e2 = next(e for e in a.events if e.event_id == "E2")
    assert dict(e2.attributes)["proc_id"] == "PROC-000088" and e2.kind == "ACTION"
    assert e2.claim_route == "INFERRED_RULE" and e2.trajectory == "PLANNED"


def test_log_view_matches_direct_replay(rung):
    s, out = run(rung, TEXT)
    a = adapt(rung, s, out)
    log = a.log()
    assert len(log) == len(a.events)
    assert replay_log(log, lot_accounting=a.lot_accounting).to_jsonl() == a.replay().to_jsonl()


def test_reserve_split_and_discard_templates_replay(rung):
    s, out = run(rung, "Reserve half of the liquid. Add the liquid to the onion.")
    r = adapt(rung, s, out).replay()
    assert r.issues == () and "FRACTION_BASIS_UNSPECIFIED" in codes(r.unknown)
    reserved = next(n.entity_id for n in out.graph.entities if n.entity_type == "RESERVED_PORTION")
    assert r.snapshot.current(reserved).lifecycle == "RESERVED"
    s2, out2 = run(rung, "Add the leaf if desired. Discard the liquid.")
    r2 = adapt(rung, s2, out2).replay()
    assert r2.issues == () and r2.snapshot.current("N3").lifecycle == "DISCARDED"
    s3, out3 = run(rung, "Divide the dough into four portions.")
    r3 = adapt(rung, s3, out3).replay()
    assert r3.issues == () and len([v for v in r3.transactions[-1].output_entity_versions if v.version == 0]) == 4


def test_explicit_only_scope_excludes_rung_a_inferences(rung):
    s, out = run(rung, TEXT)
    r = adapt(rung, s, out).replay(ReplayConfig(scope="EXPLICIT_ONLY"))
    assert {t.status for t in r.transactions} == {"SKIPPED_SCOPE"} and r.snapshot.entity_ids() == ()


def test_outputs_carry_ids_not_raw_text(rung):
    s, out = run(rung, TEXT)
    a = adapt(rung, s, out)
    blob = a.log().to_jsonl() + a.replay().to_jsonl()
    for word in ("onion", "garlic", "frying", "golden", "minutes", "Heat"):
        assert word not in blob


def test_event_level_amounts_are_not_bound_to_an_entity(rung):
    s, out = run(rung, TEXT)
    a = adapt(rung, s, out)
    assert "EVENT_QUANTITY_NOT_BOUND_TO_ENTITY" in codes(a.unknown)
    assert all(not e.quantities for e in a.events)


# ---------------------------------------------------------------- negative controls via the adapter
def test_shuffled_graph_is_not_re_sorted_and_raises_issues(rung):
    s, out = run(rung, TEXT)
    shuffled = replace(out.graph, events=tuple(reversed(out.graph.events)))
    r = adapt_event_graph(s, shuffled, groundings=out.quantities, recomputers=rung.recomputers()).replay()
    assert {"ORDER_REGRESSION", "ENTITY_UNKNOWN"} <= codes(r.issues)


def test_reuse_of_a_discarded_lot_fails_in_v4_and_in_replay():
    s = SourceText.from_raw("SYN-18", "Discard the liquid. Add the liquid.")
    g = graph(s, events=[EventCandidate("E1", (0, 0), discards=("N1",)),
                         EventCandidate("E2", (1, 0), consumes=("N1",), produces=("N2",))],
              entities=[lot("N1"), mid("N2", ("N1",), "E2")], lots={"N1": "DISCARDED"})
    assert "CONSUMED_AFTER_DISCARD" in codes(v4_invariants(g).issues)
    r = adapt_event_graph(s, g).replay()
    assert "ENTITY_REUSED_AFTER_DISCARD" in codes(r.issues)


# ---------------------------------------------------------------- quantities and the auditor
def _grounded(rung):
    s, out = run(rung, "Add 200 g onion.")
    q = next(x for x in out.quantities if x.record is not None)
    return s, q


def _mass_claim(q, value) -> ValueClaim:
    return ValueClaim("amount_g", ValueKind.MASS_G, value, origin="DERIVED_DETERMINISTIC", claim_route="INFERRED_RULE",
                      span=q.span, trace=Trace(TraceKind.QNT_RECORD, ref_ids=(q.result_id,)), unit="g")


def test_traced_entity_amount_enters_as_a_quantity_term(rung):
    s, q = _grounded(rung)
    g = graph(s, entities=[lot("N1", [_mass_claim(q, 200)])], lots={"N1": "APPARENTLY_UNUSED"})
    a = adapt_event_graph(s, g, groundings=(q,))
    assert a.issues == () and a.invented_count == 0
    (term,) = a.events[0].quantities
    assert (term.entity_id, term.dim, term.low, term.high, term.ref) == ("N1", "g", Fraction(200), Fraction(200),
                                                                         q.result_id)
    assert a.replay().snapshot.current("N1").quantity.bounds() == ("g", Fraction(200), Fraction(200))


def test_invented_amount_is_excluded_and_counted(rung):
    s, q = _grounded(rung)
    g = graph(s, entities=[lot("N1", [_mass_claim(q, 250)])], lots={"N1": "APPARENTLY_UNUSED"})
    a = adapt_event_graph(s, g, groundings=(q,))
    assert a.invented_count == 1 and "INVENTED_VALUE_EXCLUDED" in codes(a.issues)
    assert a.events[0].quantities == ()
    assert a.replay().snapshot.current("N1").quantity is None


def test_amount_without_its_grounding_is_excluded(rung):
    s, q = _grounded(rung)
    g = graph(s, entities=[lot("N1", [_mass_claim(q, 200)])], lots={"N1": "APPARENTLY_UNUSED"})
    a = adapt_event_graph(s, g)                                            # grounding not supplied
    assert a.invented_count >= 1 and a.events[0].quantities == ()


def test_rule_traced_attributes_need_their_recomputers(rung):
    s, out = run(rung, TEXT)
    a = adapt_event_graph(s, out.graph, groundings=out.quantities)        # no recomputers
    assert a.invented_count > 0 and "INVENTED_VALUE_EXCLUDED" in codes(a.issues)
    assert all("proc_id" not in dict(e.attributes) for e in a.events) and {e.kind for e in a.events} == {
        "INTRODUCE_LOT", "UNSPECIFIED"}


def test_fraction_claim_maps_to_an_exact_allocation_fraction(rung):
    s, out = run(rung, "Reserve half of the liquid.")
    a = adapt(rung, s, out)
    allocs = {al.kind: al for e in a.events for al in e.allocations}
    assert allocs["RESERVE"].fraction == Fraction(1, 2) and allocs["REMAINDER"].fraction is None
    assert allocs["RESERVE"].basis == "UNSPECIFIED"


# ---------------------------------------------------------------- structural adapter issues
def test_entity_without_producer_and_orphan_allocation_are_reported():
    s = SourceText.from_raw("SYN-18", "Mix it.")
    g = graph(s, events=[EventCandidate("E1", (0, 0), consumes=("N9",), produces=("N2",))],
              entities=[mid("N9", (), None), mid("N2", ("N9",), "E1")],
              allocations=[AllocationCandidate("A1", "SPLIT", "MASS", "N9", "N2", None)])
    a = adapt_event_graph(s, g)
    assert {"ENTITY_WITHOUT_PRODUCER", "ALLOC_WITHOUT_EVENT"} <= codes(a.issues)
    assert "ENTITY_UNKNOWN" in codes(a.replay().issues)


def test_unknown_allocation_kind_and_source_mismatch_are_reported():
    s = SourceText.from_raw("SYN-18", "Split it.")
    g = graph(s, events=[EventCandidate("E1", (0, 0), consumes=("N1",), produces=("N2",))],
              entities=[lot("N1"), mid("N2", ("N1",), "E1")],
              allocations=[AllocationCandidate("A1", "HALVE", "MASS", "N1", "N2", "E1")])
    a = adapt_event_graph(s, g)
    assert "ALLOC_NOT_ADAPTABLE" in codes(a.issues)
    other = SourceText.from_raw("SYN-18", "Different text.")
    assert "SOURCE_MISMATCH" in codes(adapt_event_graph(other, g).issues)


def test_count_amounts_are_not_mapped_until_count_units_are_decided(rung):
    s, q = _grounded(rung)
    claim = ValueClaim("count", ValueKind.COUNT, 2, span=Span.of(s, 4, 7), trace=Trace(TraceKind.QNT_RECORD,
                                                                                         ref_ids=(q.result_id,)))
    g = graph(s, entities=[lot("N1", [claim])], lots={"N1": "APPARENTLY_UNUSED"})
    a = adapt_event_graph(s, g, groundings=(q,))
    assert "COUNT_QUANTITY_NOT_MAPPED" in codes(a.unknown) and a.events[0].quantities == ()
