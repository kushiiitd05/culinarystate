"""Step 17a validators V1-V3 on synthetic fixtures (DRAFT_PENDING_16c).

V1 span round-trip (RD invariant 1; SSOT §240.2 "Every EXPLICIT_SOURCE field has a
source span"), V2 schema validation against the Step 16 rc1/rc2 draft schemas
(SSOT §240.2 "JSON parses and exactly matches declared schema version") and V3
vocabulary membership against the draft registries. All texts are synthetic.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from culinarystate.extraction import validators as val
from culinarystate.extraction.interfaces import (
    AllocationCandidate, EntityCandidate, EventCandidate, EventGraph, LinkCandidate, LinkResult, Mention,
    MentionSet, QuantityGroundingResult, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim, ValueKind,
)
from culinarystate.extraction.quantity_stages import ground_quantity
from culinarystate.quantity.draft_contract import ORIGINS
from culinarystate.quantity.rc2_grounding import GroundingContext
from tests.fixtures.ledger_examples import base, i

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "registry" / "recipe_semantics"
META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:17a"]}
CFG = StageConfig(rung_id="A", params={"v": 0}, claim_route="INFERRED_RULE",
                  annotated_labels=frozenset({"ACTION", "FOOD_MENTION"}))
RAW = "Simmer the lentils for 10 minutes, then reserve half."


def src(raw=RAW):
    return SourceText.from_raw("SYN-V", raw)


def mset(s, *mentions):
    return MentionSet("SYN-V", s.sha256, tuple(mentions), CFG.provenance("extract_mentions"))


def codes(report):
    return [x.code for x in report.issues]


# ------------------------------------------------------------------ V1
def test_v1_passes_on_spans_built_from_the_source():
    s = src()
    r = val.v1_span_roundtrip(s, [mset(s, Mention("M1", "FOOD_MENTION", Span.of(s, 11, 18)))])
    assert r.validator == "V1_SPAN_ROUNDTRIP" and r.status == "PASS" and r.issues == ()


@pytest.mark.parametrize("raw,needle,occurrence", [
    ("Add ½ cup water.", "½ cup", 0),                                # vulgar fraction
    ("Add 1 1/2 cups flour.", "1 1/2 cups", 0),                      # mixed number
    ("Bake 20–25 minutes.", "20–25 minutes", 0),                     # en-dash range
    ("Add the crème fraîche.", "crème fraîche", 0),                  # accented food name
    ("जीरा डालें और भूनें।", "जीरा", 0),                               # Devanagari
    ("Add jeera aur haldi, then bhuno.", "haldi", 0),                # Hindi/English code mixing
    ("Add 2 tbsp oil.", "2 tbsp", 0),                      # nonbreaking space
    ("Mix.\nAdd the salt.", "salt", 0),                              # line break
    ("Add onion. Fry the onion.", "onion", 1),                       # repeated food name
    ("🔥 Sear the steak.", "steak", 0),                              # emoji before a labeled span
])
def test_v1_offset_fixtures_round_trip(raw, needle, occurrence):
    s = src(raw)
    start = -1
    for _ in range(occurrence + 1):
        start = raw.index(needle, start + 1)
    sp = Span.of(s, start, start + len(needle))
    assert val.v1_span_roundtrip(s, [mset(s, Mention("M1", "FOOD_MENTION", sp))]).status == "PASS"


def test_v1_utf8_byte_offsets_are_rejected_as_mismatch():
    raw = "🔥 Sear the steak, then rest it."
    s = src(raw)
    b = raw.encode("utf-8")
    start = b.index("steak".encode())
    bad = Span(s.text_id, s.sha256, ((start, start + 5),), ("steak",))
    assert "SPAN_TEXT_MISMATCH" in codes(val.v1_span_roundtrip(s, [mset(s, Mention("M1", "FOOD_MENTION", bad))]))


@pytest.mark.parametrize("mutate,code", [
    (lambda sp, s: replace(sp, texts=("lentil",)), "SPAN_TEXT_MISMATCH"),
    (lambda sp, s: replace(sp, raw_sha256="0" * 64), "SPAN_RAW_HASH_MISMATCH"),
    (lambda sp, s: replace(sp, text_id="OTHER"), "SPAN_TEXT_ID_MISMATCH"),
    (lambda sp, s: replace(sp, segments=((50, 60),)), "SPAN_OUT_OF_BOUNDS"),
    (lambda sp, s: replace(sp, segments=((11, 18), (0, 6)), texts=("lentils", "Simmer"), join_policy=" "),
     "SPAN_SEGMENTS_UNORDERED_OR_OVERLAPPING"),
    (lambda sp, s: replace(sp, segments=((0, 6), (11, 18)), texts=("Simmer", "lentils")),
     "SPAN_JOIN_POLICY_MISSING"),
    (lambda sp, s: replace(sp, segments=((0, 6), (11, 18)), texts=("Simmer",), join_policy=" "),
     "SPAN_TEXT_COUNT"),
    (lambda sp, s: replace(sp, segments=()), "SPAN_EMPTY"),
])
def test_v1_detects_tampered_spans(mutate, code):
    s = src()
    sp = mutate(Span.of(s, 11, 18), s)
    assert code in codes(val.v1_span_roundtrip(s, [mset(s, Mention("M1", "FOOD_MENTION", sp))]))


def test_v1_checks_source_integrity_and_output_hash():
    s = src()
    good = mset(s, Mention("M1", "FOOD_MENTION", Span.of(s, 11, 18)))
    tampered = SourceText.from_raw("SYN-V", RAW)
    object.__setattr__(tampered, "raw", RAW.replace("lentils", "beans!!"))
    assert "SOURCE_HASH_MISMATCH" in codes(val.v1_span_roundtrip(tampered, [good]))
    other = MentionSet("SYN-V", "f" * 64, (), CFG.provenance("extract_mentions"))
    assert "OUTPUT_RAW_HASH_MISMATCH" in codes(val.v1_span_roundtrip(s, [other]))


def test_v1_explicit_claims_need_a_span():
    s = src()
    claim = ValueClaim(field="duration", kind=ValueKind.DURATION, value=10, unit="min",
                       origin="EXPLICIT_SOURCE", claim_route="EXPLICIT", trace=Trace(TraceKind.SPAN_LITERAL))
    m = Mention("M1", "ACTION", Span.of(s, 0, 6), attributes=(claim,))
    r = val.v1_span_roundtrip(s, [mset(s, m)])
    assert codes(r) == ["EXPLICIT_WITHOUT_SPAN"] and r.issues[0].path.endswith("M1/duration")


def test_v1_quantity_record_raw_must_equal_its_span():
    raw = "Add 200 g lentils."
    s = src(raw)
    sp = Span.of(s, 4, 9)
    g = ground_quantity(s, sp, GroundingContext(source_metadata=META), CFG, schema=val.load_draft_schema("QNT", 2),
                        result_id="Q1")
    assert val.v1_span_roundtrip(s, [g]).status == "PASS"
    rec = copy.deepcopy(g.record)
    rec["raw"] = "300 g"
    bad = QuantityGroundingResult("Q1", sp, g.provenance, record=rec, grounding=g.grounding)
    assert "QNT_RAW_NOT_SPAN" in codes(val.v1_span_roundtrip(s, [bad]))


# ------------------------------------------------------------------ V2
def test_declared_schema_versions_come_from_the_draft_files():
    assert val.declared_schema_version(val.load_draft_schema("QNT", 2)) == "1.0.0-rc2"
    assert val.declared_schema_version(val.load_draft_schema("EVT", 1)) == "1.0.0-rc"
    assert val.declared_schema_version({"type": "object"}) is None


def test_v2_rc2_grounded_record_passes_and_missing_metadata_fails():
    raw = "Add 2 x 400 g tomatoes."
    s = src(raw)
    schema = val.load_draft_schema("QNT", 2)
    g = ground_quantity(s, Span.of(s, 4, 13), GroundingContext(source_metadata=META), CFG, schema=schema,
                        result_id="Q1")
    assert val.v2_schema(g.record, schema).status == "PASS"
    rec = copy.deepcopy(g.record)
    del rec["field_metadata"]["/mass_g"]
    assert "MISSING_METADATA" in codes(val.v2_schema(rec, schema))
    assert val.v2_quantity_records([g], schema).status == "PASS"


def evt(**kw):
    return base("EVT", recipe_id=i("REC"), step_index=0, ordinal=0, trajectory="PLANNED",
                **{"schema_version": "1.0.0-rc", **kw})


def test_v2_rc1_records_validate_and_version_must_match_exactly():
    schema = val.load_draft_schema("EVT", 1)
    assert val.v2_schema(evt(event_kind="ACTION", action_raw="simmer"), schema).status == "PASS"
    assert "SCHEMA" in codes(val.v2_schema(evt(event_kind="SAUTE"), schema))
    assert codes(val.v2_schema(evt(schema_version="1.0.0"), schema)) == ["SCHEMA_VERSION_MISMATCH"]
    rec = evt()
    del rec["schema_version"]
    assert codes(val.v2_schema(rec, schema)) == ["SCHEMA_VERSION_MISSING"]
    assert codes(val.v2_schema(evt(), {"type": "object"})) == ["SCHEMA_VERSION_UNDECLARED"]


def test_v2_json_text_must_parse_strictly():
    schema = val.load_draft_schema("EVT", 1)
    assert val.v2_schema(json.dumps(evt()), schema).status == "PASS"
    assert codes(val.v2_schema('{"id": NaN}', schema)) == ["JSON_PARSE"]
    assert codes(val.v2_schema("{not json", schema)) == ["JSON_PARSE"]
    assert codes(val.v2_schema("[1, 2]", schema)) == ["JSON_NOT_OBJECT"]


def test_v2_rc1_review_overlay_flags_inverted_interval():
    schema = val.load_draft_schema("ALLOC", 1)
    rec = base("ALLOC", parent_entity_id=i("ENTITY"), child_entity_id=i("ENTITY", 2), kind="SPLIT",
               schema_version="1.0.0-rc", fraction={"status": "RANGE", "low": 0.6, "high": 0.4})
    assert "INVERTED_INTERVAL" in codes(val.v2_schema(rec, schema))


# ------------------------------------------------------------------ V3
def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_draft_vocabularies_are_read_from_registries_and_draft_schemas():
    before = {p.name: _sha(p) for p in REG.glob("*.csv")}
    v = val.load_draft_vocabularies()
    assert v["claim_route"].codes == frozenset({"EXPLICIT", "INFERRED_RULE", "INFERRED_LLM", "MODEL", "SIMULATED"})
    assert v["lifecycle"].codes == frozenset({"ACTIVE", "RESERVED", "INCORPORATED", "DISCARDED", "SERVED",
                                              "UNRESOLVED"})
    assert v["annotation_mode"].enumerated is False
    assert v["claim_route"].statuses == frozenset({"DRAFT_PENDING_H4"})
    assert v["claim_route"].sha256 == before["claim_route_registry_v1_DRAFT.csv"]
    assert v["origin"].codes == frozenset(ORIGINS)
    assert v["alloc_kind"].codes == frozenset({"SPLIT", "RESERVE", "REMAINDER", "RECOMBINE", "DISCARD"})
    assert v["alloc_basis"].codes == frozenset({"MASS", "VOLUME", "COUNT", "UNSPECIFIED"})
    assert {p.name: _sha(p) for p in REG.glob("*.csv")} == before


def _claim(field, value, **kw):
    kw.setdefault("kind", ValueKind.CATEGORICAL)
    kw.setdefault("origin", "DERIVED_DETERMINISTIC")
    kw.setdefault("trace", Trace(TraceKind.REGISTRY_LABEL))
    return ValueClaim(field=field, value=value, **kw)


def _graph(s, *, entities=None, attrs=(), allocations=(), config=CFG):
    return EventGraph(
        "SYN-V", s.sha256,
        events=(EventCandidate("E1", (0, 0), Span.of(s, 0, 6), consumes=("N1",), produces=("N2",), attributes=attrs),),
        entities=entities or (EntityCandidate("N1", "INGREDIENT_LOT", "INCORPORATED"),
                              EntityCandidate("N2", "INTERMEDIATE", "ACTIVE", ("N1",), "E1")),
        allocations=allocations, lot_accounting={"N1": "USED"}, provenance=config.provenance("build_events"))


def test_v3_passes_on_registry_codes_and_reports_unchecked_scopes():
    s = src()
    attrs = (_claim("event_kind", "ACTION", span=Span.of(s, 0, 6)),
             _claim("modality", "REQUIRED", span=Span.of(s, 0, 6)))
    r = val.v3_vocabulary([_graph(s, attrs=attrs)])
    assert r.status == "PASS" and r.issues == ()


@pytest.mark.parametrize("build,code", [
    (lambda s: _graph(s, entities=(EntityCandidate("N1", "SAUCE", "ACTIVE"),)), "ENTITY_TYPE_NOT_IN_VOCAB"),
    (lambda s: _graph(s, entities=(EntityCandidate("N1", "INGREDIENT_LOT", "GONE"),)), "LIFECYCLE_NOT_IN_VOCAB"),
    (lambda s: _graph(s, attrs=(_claim("event_kind", "SAUTE"),)), "VOCAB_MEMBERSHIP"),
    (lambda s: _graph(s, attrs=(_claim("event_kind", "ACTION", status="MAYBE"),)), "CLAIM_STATUS_NOT_IN_VOCAB"),
    (lambda s: _graph(s, attrs=(_claim("event_kind", "ACTION", claim_route="GUESS"),)), "CLAIM_ROUTE_NOT_IN_VOCAB"),
    (lambda s: _graph(s, attrs=(_claim("event_kind", "ACTION", origin="HUNCH"),)), "CLAIM_ORIGIN_NOT_IN_VOCAB"),
    (lambda s: _graph(s, config=StageConfig("A", {}, "HUMAN")), "PROVENANCE_CLAIM_ROUTE_NOT_IN_VOCAB"),
    (lambda s: _graph(s, allocations=(AllocationCandidate("A1", "HALVE", "MASS", "N1", "N2"),)),
     "ALLOC_KIND_NOT_IN_VOCAB"),
    (lambda s: _graph(s, allocations=(AllocationCandidate("A1", "SPLIT", "WEIGHT", "N1", "N2"),)),
     "ALLOC_BASIS_NOT_IN_VOCAB"),
])
def test_v3_flags_codes_outside_the_draft_vocabularies(build, code):
    assert code in codes(val.v3_vocabulary([build(src())]))


def test_v3_mention_labels_are_checked_only_against_a_supplied_label_set():
    s = src()
    ms = mset(s, Mention("M1", "FOOD_MENTION", Span.of(s, 11, 18)), Mention("M2", "TOOL", Span.of(s, 0, 6)))
    r = val.v3_vocabulary([ms])
    assert "MENTION_LABELS" in r.not_checked
    assert codes(r) == ["MENTION_LABEL_NOT_ANNOTATED"]
    r2 = val.v3_vocabulary([ms], mention_labels=frozenset({"FOOD_MENTION", "ACTION"}))
    assert "MENTION_LABEL_NOT_IN_VOCAB" in codes(r2) and "MENTION_LABELS" not in r2.not_checked


def test_v3_link_targets_need_a_supplied_id_set():
    s = src()
    link = LinkResult("M1", Span.of(s, 11, 18), (LinkCandidate("ING-000001"),), CFG.provenance("link"),
                      selected_id="ING-000001")
    r = val.v3_vocabulary([link])
    assert r.status == "PASS" and "LINK_TARGET_IDS:ING" in r.not_checked
    r2 = val.v3_vocabulary([link], id_sets={"ING": frozenset({"ING-000002"})})
    assert codes(r2) == ["LINK_TARGET_NOT_IN_VOCAB"]
    assert val.v3_vocabulary([link], id_sets={"ING": frozenset({"ING-000001"})}).not_checked == ()


def test_v3_annotation_mode_cannot_be_checked_while_registry_is_open():
    s = src()
    cfg = StageConfig("A", {}, "INFERRED_RULE", annotation_mode="MODEL_ASSISTED")
    r = val.v3_vocabulary([MentionSet("SYN-V", s.sha256, (), cfg.provenance("extract_mentions"))])
    assert r.status == "UNKNOWN" and [u.code for u in r.unknown] == ["ANNOTATION_MODE_REGISTRY_OPEN"]
