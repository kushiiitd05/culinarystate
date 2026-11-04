"""Step 17a common extraction interface: synthetic controls (DRAFT_PENDING_16c).

Hard gate 16c is open; every type under test is an engineering draft. The six
stage names and the four failure codes come from Plan Step 17-M ("Common
interface"). All texts are synthetic; no real recipe text is used.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from culinarystate.extraction import interfaces as itf
from culinarystate.extraction.interfaces import (
    ALLOWED_FAILURES, STAGES, STATUS, AllocationCandidate, EntityCandidate, EventCandidate, EventGraph,
    Failure, FailureCode, InterfaceError, LinkCandidate, LinkResult, Mention, MentionSet, Provenance,
    ReferenceResult, RungInterface, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim, ValueKind,
    config_hash, iter_claims, iter_spans,
)

RAW = "Simmer the lentils for 10 minutes, then reserve half."


def src(raw=RAW, text_id="SYN-1"):
    return SourceText.from_raw(text_id, raw)


def cfg(route="INFERRED_RULE", **kw):
    return StageConfig(rung_id="A", params={"lexicon": "synthetic-v0"}, claim_route=route, **kw)


def test_status_and_stage_names_follow_plan_17m():
    assert STATUS == "DRAFT_PENDING_16c"
    assert STAGES == ("extract_mentions", "link", "parse_quantity", "ground_quantity", "build_events",
                      "resolve_refs")
    assert {c.value for c in FailureCode} == {"UNRESOLVED", "NO_VALID_CANDIDATE", "PARSE_FAIL",
                                              "NO_COMPATIBLE_RECORD"}
    assert set(ALLOWED_FAILURES) == set(STAGES)
    assert ALLOWED_FAILURES["parse_quantity"] == frozenset({FailureCode.PARSE_FAIL})
    assert FailureCode.NO_COMPATIBLE_RECORD in ALLOWED_FAILURES["ground_quantity"]
    assert FailureCode.NO_VALID_CANDIDATE in ALLOWED_FAILURES["link"]


def test_every_module_header_declares_draft_pending_16c():
    assert "DRAFT_PENDING_16c" in (itf.__doc__ or "").splitlines()[0]


def test_source_text_hash_is_sha256_of_utf8_raw():
    s = src("Stir 1½ cups água 🍋.")
    assert s.sha256 == hashlib.sha256("Stir 1½ cups água 🍋.".encode("utf-8")).hexdigest()
    with pytest.raises(InterfaceError):
        SourceText("SYN-1", RAW, "0" * 64)
    with pytest.raises(FrozenInstanceError):
        s.raw = "changed"


def test_span_of_copies_raw_slice_and_exposes_char_offsets():
    s = src()
    sp = Span.of(s, 11, 18)
    assert sp.texts == ("lentils",) and sp.surface == "lentils"
    assert (sp.char_start, sp.char_end) == (11, 18)
    assert sp.raw_sha256 == s.sha256 and sp.text_id == "SYN-1"
    for bad in [(-1, 3), (5, 5), (8, 3), (0, len(RAW) + 1)]:
        with pytest.raises(InterfaceError):
            Span.of(s, *bad)


def test_offsets_are_codepoints_with_non_ascii_text():
    s = src("🍋 Add ½ tsp jeera")
    i = s.raw.index("½")
    assert Span.of(s, i, i + 1).surface == "½"
    assert itf.OFFSET_UNIT == "PYTHON_STR_CODEPOINT"


def test_multi_segment_span_needs_ordered_segments_and_join_policy():
    s = src("Chop the red and the green peppers.")
    sp = Span.multi(s, [(9, 12), (27, 34)], join_policy=" ")
    assert sp.surface == "red peppers" and sp.char_start == 9 and sp.char_end == 34
    with pytest.raises(InterfaceError):
        Span.multi(s, [(9, 12), (27, 34)], join_policy=None)
    with pytest.raises(InterfaceError):
        Span.multi(s, [(27, 34), (9, 12)], join_policy=" ")
    with pytest.raises(InterfaceError):
        Span.multi(s, [(9, 30), (27, 34)], join_policy=" ")


def test_config_hash_is_canonical_and_rejects_non_finite():
    a = config_hash({"b": 1, "a": [1, 2], "c": {"y": "z"}})
    b = config_hash({"c": {"y": "z"}, "a": [1, 2], "b": 1})
    assert a == b and len(a) == 64
    assert a != config_hash({"b": 2, "a": [1, 2], "c": {"y": "z"}})
    with pytest.raises(InterfaceError):
        config_hash({"x": math.nan})


def test_stage_config_provenance_carries_required_fields():
    c = cfg(model_id="rules-only", annotated_labels=frozenset({"ACTION", "FOOD_MENTION"}))
    p = c.provenance("extract_mentions")
    assert isinstance(p, Provenance)
    assert p.stage == "extract_mentions" and p.rung_id == "A"
    assert p.config_hash == c.config_hash and len(p.config_hash) == 64
    assert p.schema_version == itf.INTERFACE_SCHEMA_VERSION
    assert p.claim_route == "INFERRED_RULE" and p.status == STATUS
    assert p.offset_unit == "PYTHON_STR_CODEPOINT"
    assert p.label_status("ACTION") == "ANNOTATED"
    assert p.label_status("TOOL") == "MISSING"
    assert cfg().provenance("link").label_status("ACTION") == "MISSING"
    with pytest.raises(InterfaceError):
        c.provenance("summarise")
    assert cfg(model_id="m1").config_hash != cfg(model_id="m2").config_hash


def test_failure_requires_enum_code_and_reason():
    f = Failure(FailureCode.UNRESOLVED, "NO_ANTECEDENT")
    assert f.code is FailureCode.UNRESOLVED
    with pytest.raises(InterfaceError):
        Failure("UNRESOLVED", "x")
    with pytest.raises(InterfaceError):
        Failure(FailureCode.UNRESOLVED, " ")


def _mention(s, mid="M1", start=11, end=18, label="FOOD_MENTION", attributes=()):
    return Mention(mention_id=mid, label=label, span=Span.of(s, start, end), attributes=attributes)


def test_mention_set_claims_include_label_with_route_origin_and_qualified_field():
    s = src()
    dur_span = Span.of(s, 23, 25)
    dur = ValueClaim(field="duration", kind=ValueKind.DURATION, value=10, unit="min",
                     origin="EXPLICIT_SOURCE", claim_route="EXPLICIT", span=dur_span,
                     trace=Trace(TraceKind.SPAN_LITERAL))
    ms = MentionSet(source_text_id="SYN-1", raw_sha256=s.sha256,
                    mentions=(_mention(s), _mention(s, "M2", 23, 33, "DURATION", (dur,))),
                    provenance=cfg().provenance("extract_mentions"))
    claims = list(ms.claims())
    fields = [c.field for c in claims]
    assert fields == ["M1/label", "M2/label", "M2/duration"]
    label = claims[0]
    assert label.kind is ValueKind.CATEGORICAL and label.value == "FOOD_MENTION"
    assert label.trace.kind is TraceKind.REGISTRY_LABEL and label.span.surface == "lentils"
    assert label.claim_route == "INFERRED_RULE" and label.origin == "DERIVED_DETERMINISTIC"
    assert [sp.surface for sp in ms.spans()] == ["lentils", "10 minutes", "10"]


def test_mention_set_failure_is_explicit_and_never_partial():
    s = src()
    p = cfg().provenance("extract_mentions")
    MentionSet("SYN-1", s.sha256, (), p, failure=Failure(FailureCode.UNRESOLVED, "TEXT_NOT_PROCESSED"))
    with pytest.raises(InterfaceError):
        MentionSet("SYN-1", s.sha256, (_mention(s),), p, failure=Failure(FailureCode.UNRESOLVED, "x"))
    with pytest.raises(InterfaceError):
        MentionSet("SYN-1", s.sha256, (), p, failure=Failure(FailureCode.NO_COMPATIBLE_RECORD, "x"))
    with pytest.raises(InterfaceError):
        MentionSet("SYN-1", s.sha256, (), cfg().provenance("link"))


def test_link_result_selects_only_among_candidates_or_fails_explicitly():
    s = src()
    sp = Span.of(s, 11, 18)
    p = cfg().provenance("link")
    cands = (LinkCandidate("ING-000001", 0.9), LinkCandidate("ING-000002", None))
    ok = LinkResult("M1", sp, cands, p, selected_id="ING-000001")
    (claim,) = ok.claims()
    assert claim.field == "M1/link" and claim.kind is ValueKind.IDENTIFIER
    assert claim.trace.kind is TraceKind.CANDIDATE_SELECTION
    assert claim.trace.candidates == ("ING-000001", "ING-000002")
    nvc = LinkResult("M1", sp, cands, p, failure=Failure(FailureCode.NO_VALID_CANDIDATE, "ALL_REJECTED"))
    assert nvc.claims() == ()
    with pytest.raises(InterfaceError):
        LinkResult("M1", sp, cands, p, selected_id="ING-000003")
    with pytest.raises(InterfaceError):
        LinkResult("M1", sp, cands, p)
    with pytest.raises(InterfaceError):
        LinkResult("M1", sp, cands, p, selected_id="ING-000001",
                   failure=Failure(FailureCode.NO_VALID_CANDIDATE, "x"))
    with pytest.raises(InterfaceError):
        LinkResult("M1", sp, cands, p, failure=Failure(FailureCode.PARSE_FAIL, "x"))


def test_reference_result_antecedents_must_be_candidates():
    s = src()
    sp = Span.of(s, 48, 52)
    p = cfg().provenance("resolve_refs")
    r = ReferenceResult("M9", sp, ("N1", "N2"), p, antecedent_ids=("N1",))
    assert [c.value for c in r.claims()] == ["N1"]
    ReferenceResult("M9", sp, ("N1",), p, failure=Failure(FailureCode.UNRESOLVED, "NO_COMPATIBLE_ANTECEDENT"))
    with pytest.raises(InterfaceError):
        ReferenceResult("M9", sp, ("N1",), p, antecedent_ids=("N3",))
    with pytest.raises(InterfaceError):
        ReferenceResult("M9", sp, ("N1",), p)


def _graph(s, **kw):
    half = ValueClaim(field="fraction", kind=ValueKind.FRACTION, value=Fraction(1, 2), span=Span.of(s, 48, 52),
                      origin="DERIVED_DETERMINISTIC", claim_route="INFERRED_RULE",
                      trace=Trace(TraceKind.SPAN_RULE, rule_id="WORD_FRACTION_V0"))
    kind = ValueClaim(field="event_kind", kind=ValueKind.CATEGORICAL, value="ACTION", span=Span.of(s, 0, 6),
                      origin="DERIVED_DETERMINISTIC", claim_route="INFERRED_RULE",
                      trace=Trace(TraceKind.REGISTRY_LABEL))
    base = dict(
        source_text_id="SYN-1", raw_sha256=s.sha256,
        events=(EventCandidate("E1", (0, 0), Span.of(s, 0, 6), consumes=("N1",), produces=("N2",),
                               attributes=(kind,)),
                EventCandidate("E2", (0, 1), Span.of(s, 40, 47), consumes=("N2",), produces=("N3",))),
        entities=(EntityCandidate("N1", "INGREDIENT_LOT", "INCORPORATED", span=Span.of(s, 11, 18)),
                  EntityCandidate("N2", "INTERMEDIATE", "ACTIVE", parent_entity_ids=("N1",), created_by_event_id="E1"),
                  EntityCandidate("N3", "RESERVED_PORTION", "RESERVED", parent_entity_ids=("N2",),
                                  created_by_event_id="E2")),
        allocations=(AllocationCandidate("A1", "RESERVE", "UNSPECIFIED", "N2", "N3", event_id="E2", fraction=half),),
        lot_accounting={"N1": "USED"},
        provenance=cfg().provenance("build_events"))
    base.update(kw)
    return EventGraph(**base)


def test_event_graph_claims_cover_event_and_allocation_values():
    s = src()
    g = _graph(s)
    assert [c.field for c in g.claims()] == ["E1/event_kind", "A1/fraction"]
    surfaces = [sp.surface for sp in iter_spans(g)]
    assert "Simmer" in surfaces and "half" in surfaces and "lentils" in surfaces
    assert [c.field for c in iter_claims([g])] == ["E1/event_kind", "A1/fraction"]
    with pytest.raises(InterfaceError):
        _graph(s, failure=Failure(FailureCode.NO_COMPATIBLE_RECORD, "x"))


def test_value_claim_is_frozen_and_typed():
    c = ValueClaim(field="x", kind=ValueKind.TEMPERATURE, value=180, unit="degC")
    assert c.status == "KNOWN" and c.trace.kind is TraceKind.NONE
    with pytest.raises(FrozenInstanceError):
        c.value = 200
    with pytest.raises(InterfaceError):
        ValueClaim(field="", kind=ValueKind.TEMPERATURE, value=180)
    with pytest.raises(InterfaceError):
        ValueClaim(field="x", kind="TEMPERATURE", value=180)
    assert ValueKind.TEMPERATURE in itf.MAGNITUDE_KINDS and ValueKind.PH in itf.MAGNITUDE_KINDS
    assert ValueKind.CATEGORICAL not in itf.MAGNITUDE_KINDS


def test_route_to_origin_mapping_is_total_over_registry_routes():
    assert set(itf.ROUTE_TO_ORIGIN) == {"EXPLICIT", "INFERRED_RULE", "INFERRED_LLM", "MODEL", "SIMULATED"}


def test_rung_protocol_is_runtime_checkable():
    class Dummy:
        def extract_mentions(self, source, config): ...
        def link(self, source, mention, config): ...
        def parse_quantity(self, source, span, config, *, source_metadata, locale=None): ...
        def ground_quantity(self, source, span, context, config, *, schema, result_id): ...
        def build_events(self, source, mentions, links, quantities, config): ...
        def resolve_refs(self, source, mentions, graph, config): ...

    class Partial:
        def link(self, source, mention, config): ...

    assert isinstance(Dummy(), RungInterface)
    assert not isinstance(Partial(), RungInterface)
