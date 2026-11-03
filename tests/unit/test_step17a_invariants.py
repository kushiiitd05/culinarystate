"""Step 17a validator V4: Step-18 invariants on candidate graphs (DRAFT_PENDING_16c).

Only invariants stated in RD "Invariants checked in CI" (1-7) and SSOT §240.2 are
checked. Unstated details (order basis, which entity types are "new
intermediates", fraction reference, mass-balance scope) are parameters or are
reported as UNKNOWN / not checked, never decided. Synthetic graphs only.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.extraction import invariants as inv
from culinarystate.extraction.interfaces import (
    AllocationCandidate, EntityCandidate, EventCandidate, EventGraph, Failure, FailureCode, Mention, MentionSet,
    SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim, ValueKind,
)
from culinarystate.extraction.quantity_stages import ground_quantity
from culinarystate.quantity.rc2_grounding import GroundingContext

ROOT = Path(__file__).resolve().parents[2]
RAW = "Simmer the lentils, then reserve half."
CFG = StageConfig(rung_id="A", params={"v": 0}, claim_route="INFERRED_RULE",
                  annotated_labels=frozenset({"FOOD_MENTION"}))
SRC = SourceText.from_raw("SYN-G", RAW)
META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:17a"]}


def ev(eid, order, **kw):
    return EventCandidate(eid, order, **kw)


def ent(nid, etype="INTERMEDIATE", lifecycle="ACTIVE", parents=(), by=None):
    return EntityCandidate(nid, etype, lifecycle, tuple(parents), by)


def frac(value, status="KNOWN"):
    return ValueClaim(field="fraction", kind=ValueKind.FRACTION, value=value, status=status,
                      origin="DERIVED_DETERMINISTIC", trace=Trace(TraceKind.SPAN_RULE, rule_id="R"))


def graph(events=None, entities=None, allocations=(), lots=None, failure=None):
    events = events if events is not None else (ev("E1", (0, 0), consumes=("N1",), produces=("N2",)),)
    entities = entities if entities is not None else (ent("N1", "INGREDIENT_LOT", "INCORPORATED"),
                                                      ent("N2", parents=("N1",), by="E1"))
    return EventGraph("SYN-G", SRC.sha256, tuple(events), tuple(entities), tuple(allocations),
                      {"N1": "USED"} if lots is None else lots, CFG.provenance("build_events"), failure=failure)


def codes(report):
    return [x.code for x in report.issues]


def ucodes(report):
    return [x.code for x in report.unknown]


def test_module_is_draft_and_lists_open_invariants():
    assert "DRAFT_PENDING_16c" in inv.__doc__.splitlines()[0]
    assert inv.LOT_ACCOUNTING_STATUSES == ("USED", "OPTIONAL", "ALTERNATIVE", "GARNISH", "DISCARDED", "UNRESOLVED",
                                           "APPARENTLY_UNUSED")
    r = inv.v4_invariants(graph())
    assert r.validator == "V4_STEP18_INVARIANTS" and r.status == "PASS"
    for name in ("INFERRED_EVENTS_NOT_IN_EXPLICIT_ONLY_QUERIES", "STATE_REPLAY_FROM_EVENT_HISTORY",
                 "MASS_BALANCE_SCOPE", "INVENTED_GRAMS_SEE_AUDITOR", "SPAN_ROUNDTRIP_SEE_V1"):
        assert name in r.not_checked


def test_referenced_ids_must_exist():
    g = graph(events=(ev("E1", (0, 0), consumes=("N9",), produces=("N2",), depends_on=("E7",)),),
              entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N8",), by="E5")),
              allocations=(AllocationCandidate("A1", "SPLIT", "MASS", "N6", "N2", event_id="E4"),))
    missing = [x for x in inv.v4_invariants(g).issues if x.code == "REFERENCED_ID_MISSING"]
    assert sorted(x.path for x in missing) == sorted(["E1/consumes/N9", "E1/depends_on/E7", "N2/parent/N8",
                                                      "N2/created_by/E5", "A1/parent/N6", "A1/event/E4"])


def test_duplicate_ids_are_reported():
    g = graph(entities=(ent("N1", "INGREDIENT_LOT"), ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E1")))
    assert "DUPLICATE_ID" in codes(inv.v4_invariants(g))


def test_nothing_consumed_before_it_is_produced():
    g = graph(events=(ev("E1", (0, 0), consumes=("N2",)), ev("E2", (0, 1), consumes=("N1",), produces=("N2",))),
              entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E2")))
    assert codes(inv.v4_invariants(g)) == ["CONSUMED_BEFORE_PRODUCED"]


def test_order_basis_is_a_parameter():
    g = graph(events=(ev("E1", (0, 0), consumes=("N2",)), ev("E2", (0, 1), consumes=("N1",), produces=("N2",))),
              entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E2")))
    exec_order = {"E2": 0, "E1": 1}
    assert inv.v4_invariants(g, order=lambda e: exec_order[e.event_id]).status == "PASS"
    assert inv.text_order(g.events[0]) == (0, 0)


def test_equal_order_is_undecided_not_failed():
    g = graph(events=(ev("E1", (0, 0), consumes=("N2",)), ev("E2", (0, 0), consumes=("N1",), produces=("N2",))),
              entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E2")))
    r = inv.v4_invariants(g)
    assert r.issues == () and "ORDER_TIE" in ucodes(r) and r.status == "UNKNOWN"


def test_every_new_intermediate_has_a_producing_event():
    g = graph(entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E1"), ent("N3")))
    r = inv.v4_invariants(g)
    assert codes(r) == ["INTERMEDIATE_WITHOUT_PRODUCER"] and r.issues[0].path == "N3"
    mixture = graph(entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E1"), ent("N3", "MIXTURE")))
    assert inv.v4_invariants(mixture).status == "PASS"
    wider = inv.v4_invariants(mixture, intermediate_types=frozenset({"INTERMEDIATE", "MIXTURE"}))
    assert codes(wider) == ["INTERMEDIATE_WITHOUT_PRODUCER"]


def test_disagreeing_producer_references_are_undecided():
    g = graph(events=(ev("E1", (0, 0), consumes=("N1",)), ev("E2", (0, 1), produces=("N2",))),
              entities=(ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E1")))
    assert "PRODUCER_REFERENCES_DISAGREE" in ucodes(inv.v4_invariants(g))


def test_nothing_consumed_after_discard():
    g = graph(events=(ev("E1", (0, 0), discards=("N1",)), ev("E2", (1, 0), consumes=("N1",), produces=("N2",))),
              entities=(ent("N1", "INGREDIENT_LOT", "DISCARDED"), ent("N2", parents=("N1",), by="E2")),
              lots={"N1": "DISCARDED"})
    assert codes(inv.v4_invariants(g)) == ["CONSUMED_AFTER_DISCARD"]


def test_split_merge_relations_have_consistent_parent_child_references():
    base_entities = (ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E1"), ent("N3", by="E1"))
    g = graph(events=(ev("E1", (0, 0), consumes=("N1",), produces=("N2", "N3")),), entities=base_entities,
              allocations=(AllocationCandidate("A1", "RESERVE", "MASS", "N1", "N3", event_id="E1"),))
    assert "ALLOC_PARENT_NOT_LISTED" in codes(inv.v4_invariants(g))
    g2 = graph(events=(ev("E1", (0, 0), consumes=("N1",), produces=("N2",)), ev("E2", (0, 1))),
               allocations=(AllocationCandidate("A1", "SPLIT", "MASS", "N1", "N2", event_id="E2"),))
    assert codes(inv.v4_invariants(g2)) == ["ALLOC_EVENT_MISMATCH"]


def split_graph(*allocs):
    ents = (ent("N1", "INGREDIENT_LOT"), ent("N2", parents=("N1",), by="E1"), ent("N3", parents=("N1",), by="E1"),
            ent("N4", parents=("N1",), by="E2"))
    events = (ev("E1", (0, 0), consumes=("N1",), produces=("N2", "N3")), ev("E2", (1, 0), produces=("N4",)))
    return graph(events=events, entities=ents, allocations=allocs)


def A(aid, child, value, basis="MASS", kind="SPLIT", event="E1", status="KNOWN"):
    return AllocationCandidate(aid, kind, basis, "N1", child, event_id=event,
                               fraction=None if value is None else frac(value, status))


@pytest.mark.parametrize("allocs,issue,unknown", [
    ((A("A1", "N2", Fraction(1, 2)), A("A2", "N3", Fraction(1, 2))), [], []),
    ((A("A1", "N2", Fraction(2, 3)), A("A2", "N3", Fraction(1, 2))), ["SPLIT_FRACTIONS_EXCEED_ONE"], []),
    ((A("A1", "N2", Fraction(2, 3)), A("A2", "N3", None)), [], ["FRACTION_UNKNOWN"]),
    ((A("A1", "N2", Fraction(2, 3)), A("A2", "N3", None, status="UNKNOWN")), [], ["FRACTION_UNKNOWN"]),
    ((A("A1", "N2", Fraction(2, 3), basis="UNSPECIFIED"),), [], ["FRACTION_BASIS_UNSPECIFIED"]),
    ((A("A1", "N2", (Fraction(1, 2), Fraction(2, 3))), A("A2", "N3", Fraction(1, 2))), [],
     ["FRACTION_INTERVAL_UNDECIDED"]),
    ((A("A1", "N2", (Fraction(3, 5), Fraction(2, 3))), A("A2", "N3", Fraction(1, 2))),
     ["SPLIT_FRACTIONS_EXCEED_ONE"], []),
    ((A("A1", "N2", Fraction(2, 3)), A("A2", "N3", Fraction(1, 2), basis="VOLUME")), [], []),
    ((A("A1", "N2", Fraction(2, 3)), A("A2", "N3", Fraction(1, 2), kind="RECOMBINE")), [], []),
    ((A("A1", "N2", Fraction(2, 3)), A("A2", "N4", Fraction(1, 2), event="E2")), [], []),
    ((A("A1", "N2", Fraction(-1, 2)), A("A2", "N3", Fraction(1, 2))), [], ["NEGATIVE_FRACTION_RULE_OPEN"]),
    ((A("A1", "N2", "half"),), [], ["FRACTION_NOT_NUMERIC"]),
    ((A("A1", "N2", 0.5), A("A2", "N3", 0.5)), [], []),
])
def test_split_fractions_sum_to_at_most_one_per_compatible_basis(allocs, issue, unknown):
    r = inv.v4_invariants(split_graph(*allocs))
    assert codes(r) == issue and ucodes(r) == unknown


def test_every_ingredient_lot_is_accounted_for():
    assert codes(inv.v4_invariants(graph(lots={}))) == ["LOT_UNACCOUNTED"]
    assert codes(inv.v4_invariants(graph(lots={"N1": "EATEN"}))) == ["LOT_STATUS_INVALID"]
    assert codes(inv.v4_invariants(graph(lots={"N1": "USED", "N2": "USED"}))) == ["LOT_ACCOUNTING_UNKNOWN_ENTITY"]
    for status in inv.LOT_ACCOUNTING_STATUSES:
        assert inv.v4_invariants(graph(lots={"N1": status})).status == "PASS"


def test_execution_dependencies_must_be_acyclic():
    g = graph(events=(ev("E1", (0, 0), consumes=("N1",), produces=("N2",), depends_on=("E2",)),
                      ev("E2", (0, 1), depends_on=("E1",))))
    assert codes(inv.v4_invariants(g)) == ["DEPENDS_ON_CYCLE"]


def test_failed_graph_is_still_checked():
    g = graph(lots={}, failure=Failure(FailureCode.UNRESOLVED, "EVENT_BOUNDARIES_UNRESOLVED"))
    assert codes(inv.v4_invariants(g)) == ["LOT_UNACCOUNTED"]


@pytest.mark.parametrize("inputs,outputs,status", [
    ([100, 50], [150], "PASS"),
    ([Fraction(1, 3), Fraction(2, 3)], [1], "PASS"),
    ([100, None], [150], "UNKNOWN"),
    ([100], [None], "UNKNOWN"),
    ([100], [90], "FAIL"),
    ([(90, 110)], [100], "UNKNOWN"),
    ([(90, 95)], [100], "FAIL"),
    ([], [], "UNKNOWN"),
])
def test_mass_balance_is_checked_only_when_every_term_is_known(inputs, outputs, status):
    r = inv.check_mass_balance(inputs, outputs)
    assert r.status == status
    if status == "UNKNOWN":
        assert r.reason


def test_mass_balance_rejects_non_finite_or_boolean_terms():
    assert inv.check_mass_balance([float("nan")], [1]).status == "UNKNOWN"
    assert inv.check_mass_balance([True], [1]).status == "UNKNOWN"


def test_run_validators_bundles_v1_to_v4():
    raw = "Add 200 g lentils."
    s = SourceText.from_raw("SYN-R", raw)
    schema = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
    q = ground_quantity(s, Span.of(s, 4, 9), GroundingContext(source_metadata=META), CFG, schema=schema,
                        result_id="Q1")
    ms = MentionSet("SYN-R", s.sha256, (Mention("M1", "FOOD_MENTION", Span.of(s, 10, 17)),),
                    CFG.provenance("extract_mentions"))
    g = EventGraph("SYN-R", s.sha256, (ev("E1", (0, 0), span=Span.of(s, 0, 3), consumes=("N1",)),),
                   (ent("N1", "INGREDIENT_LOT", "INCORPORATED"),), (), {"N1": "USED"}, CFG.provenance("build_events"))
    out = inv.run_validators(s, [ms, q, g], qnt_schema=schema, mention_labels=frozenset({"FOOD_MENTION"}))
    assert set(out) == {"V1", "V2", "V3", "V4"}
    assert all(r.status == "PASS" for r in out.values()), {k: r.issues for k, r in out.items()}
    no_schema = inv.run_validators(s, [ms, q, g])
    assert "QNT_SCHEMA_NOT_SUPPLIED" in no_schema["V2"].not_checked
