"""Step 17a quantity stages delegate to the S154 rc2 pipeline (DRAFT_PENDING_16c).

parse_quantity wraps parse_adapter.parse_quantity_v2 and ground_quantity wraps
rc2_grounding.ground_quantity_rc2: no arithmetic, unit or POR logic is
reimplemented. Every input below is synthetic.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from culinarystate.extraction import quantity_stages as qs
from culinarystate.extraction.interfaces import (
    FailureCode, InterfaceError, QuantityGroundingResult, QuantityParseResult, SourceText, Span, StageConfig,
    TraceKind, ValueKind,
)
from culinarystate.quantity.draft_contract import ContractError
from culinarystate.quantity.parse_adapter import ADAPTER_VERSION, parse_quantity_v2
from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:17a"]}
LINK_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
             "evidence_refs": ["synthetic:link"]}
LOCALE_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
               "evidence_refs": ["synthetic:locale"]}
CFG = StageConfig(rung_id="A", params={"quantity": "rc2"}, claim_route="INFERRED_RULE")


def source_with(expr, prefix="Add ", suffix=" to the pan."):
    s = SourceText.from_raw("SYN-Q", prefix + expr + suffix)
    return s, Span.of(s, len(prefix), len(prefix) + len(expr))


def por(pid="POR-000001", grams=50, **kw):
    rec = {"id": pid, "record_type": "POR", "version": 1, "status": "ACTIVE",
           "created_at": "2026-11-03T00:00:00Z", "created_by": "synthetic",
           "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "HUMAN_VERIFIED"},
           "ingredient_id": "ING-000001", "from_unit_id": "UNIT-000001",
           "grams_per_unit": {"status": "MEASURED", "value": grams, "unit": "g"}, "basis": "DATABASE",
           "state": None, "form": None, "packing": None, "locale": None}
    rec.update(kw)
    return rec


def item_ctx(*records):
    return GroundingContext(source_metadata=META, ingredient_id="ING-000001", ingredient_metadata=LINK_META,
                            por_records=records, unit_ids={"item": "UNIT-000001"}, por_q_levels={"DATABASE": "Q1"})


def ground(expr, context=None, result_id="Q1"):
    s, sp = source_with(expr)
    return qs.ground_quantity(s, sp, context or GroundingContext(source_metadata=META), CFG, schema=SCHEMA,
                              result_id=result_id)


def test_module_is_draft_pending_16c_and_versioned():
    assert "DRAFT_PENDING_16c" in qs.__doc__.splitlines()[0]
    assert qs.QUANTITY_STAGE_VERSION.endswith("_DRAFT")


def test_parse_quantity_delegates_to_adapter_and_keeps_raw_expression():
    s, sp = source_with("1-2 tbsp")
    r = qs.parse_quantity(s, sp, CFG, source_metadata=META)
    assert isinstance(r, QuantityParseResult) and r.failure is None
    assert r.expression == "1-2 tbsp" == sp.surface
    direct = parse_quantity_v2("1-2 tbsp", source_metadata=META)
    assert r.ast == direct.ast and r.arithmetic_status == "RANGE" and r.flags == direct.flags
    assert r.adapter_version == ADAPTER_VERSION
    assert r.provenance.stage == "parse_quantity" and r.provenance.config_hash == CFG.config_hash
    assert r.source_metadata == META and r.result_id.startswith("parse:")


@pytest.mark.parametrize("expr,reason", [("1 lb plus 2 oz", "AST_UNKNOWN"), ("salt", "AST_UNKNOWN")])
def test_parse_quantity_unknown_ast_is_explicit_parse_fail_with_ast_retained(expr, reason):
    s, sp = source_with(expr)
    r = qs.parse_quantity(s, sp, CFG, source_metadata=META, result_id="P9")
    assert r.failure.code is FailureCode.PARSE_FAIL and r.failure.reason == reason
    assert r.ast["node_type"] == "UNKNOWN" and r.result_id == "P9"
    assert set(r.failure.detail) == set(r.flags)


def test_parse_quantity_qualitative_is_not_a_failure_and_not_numericised():
    s, sp = source_with("to taste")
    r = qs.parse_quantity(s, sp, CFG, source_metadata=META)
    assert r.failure is None and r.ast["node_type"] == "QUALITATIVE" and r.arithmetic_status == "QUALITATIVE"


def test_parse_quantity_refuses_spans_of_other_texts_and_bad_metadata():
    s, sp = source_with("200 g")
    other = SourceText.from_raw("SYN-OTHER", "Add 200 g to the bowl.")
    with pytest.raises(InterfaceError):
        qs.parse_quantity(other, sp, CFG, source_metadata=META)
    tampered = Span(sp.text_id, sp.raw_sha256, sp.segments, ("300 g",))
    with pytest.raises(InterfaceError):
        qs.parse_quantity(s, tampered, CFG, source_metadata=META)
    with pytest.raises(ContractError):
        qs.parse_quantity(s, sp, CFG, source_metadata={"origin": "GUESS"})


def test_ground_quantity_record_is_exactly_the_rc2_pipeline_record():
    r = ground("2 x 400 g")
    direct = ground_quantity_rc2("2 x 400 g", GroundingContext(source_metadata=META), schema=SCHEMA)
    assert isinstance(r, QuantityGroundingResult) and r.failure is None
    assert r.record == direct.record and r.grounding.mass_route == "AST_PACKAGE_SOURCE_STATED"
    assert r.issues == ()
    mass = [c for c in r.claims() if c.kind is ValueKind.MASS_G]
    assert [(c.field, c.value, c.unit) for c in mass] == [("Q1/mass_g", 800, "g")]
    assert mass[0].trace.kind is TraceKind.QNT_RECORD and mass[0].trace.ref_ids == ("Q1",)
    assert mass[0].origin == "DERIVED_DETERMINISTIC" and mass[0].span.surface == "2 x 400 g"


def test_ground_quantity_without_link_is_unresolved_and_keeps_symbolic_amount():
    r = ground("2")
    assert r.failure.code is FailureCode.UNRESOLVED and r.failure.reason == "NO_INGREDIENT_LINK"
    assert r.record["mass_g"] == {"status": "UNKNOWN"} and r.record["raw"] == "2"
    assert [(c.kind, c.value) for c in r.claims()] == [(ValueKind.COUNT, 2)]


def test_ground_quantity_no_compatible_por_is_explicit():
    r = ground("2", item_ctx(por(ingredient_id="ING-000009")))
    assert r.failure.code is FailureCode.NO_COMPATIBLE_RECORD
    assert r.record["mass_g"] == {"status": "UNKNOWN"}


def test_ground_quantity_with_human_verified_por_is_grounded():
    r = ground("2", item_ctx(por(grams=50)))
    assert r.failure is None and r.record["mass_g"]["value"] == 100 and r.record["portion_id"] == "POR-000001"
    assert r.record["q_level"] == "Q1"


@pytest.mark.parametrize("expr,code,reason", [
    ("1 lb plus 2 oz", FailureCode.PARSE_FAIL, "UNSUPPORTED_EXPRESSION"),
    ("salt", FailureCode.PARSE_FAIL, "NO_QUANTITY"),
    ("to taste", FailureCode.UNRESOLVED, "QUALITATIVE"),
    ("1 cup", FailureCode.UNRESOLVED, "NO_INGREDIENT_LINK"),
])
def test_ground_quantity_failure_mapping(expr, code, reason):
    r = ground(expr)
    assert r.failure.code is code and r.failure.reason == reason


def test_volume_with_locale_is_q0_volume_but_mass_stays_unknown():
    ctx = GroundingContext(source_metadata=META, locale="US", locale_metadata=LOCALE_META)
    r = ground("1 cup", ctx)
    assert r.record["volume_ml"]["status"] == "MEASURED" and r.record["mass_g"] == {"status": "UNKNOWN"}
    assert r.failure.code is FailureCode.UNRESOLVED
    assert [c.kind for c in r.claims()] == [ValueKind.VOLUME_ML]


def test_failure_map_covers_every_non_grounded_route_and_unknown_routes_stay_unresolved():
    routes = {"NO_COMPATIBLE_RECORD", "AMBIGUOUS_POR_RECORDS", "POR_Q_LEVEL_RULING_PENDING", "NO_INGREDIENT_LINK",
              "UNIT_ID_UNMAPPED", "QUALITATIVE", "ALTERNATIVE", "UNSUPPORTED_EXPRESSION", "NO_QUANTITY",
              "OPEN_OR_UNAVAILABLE_OPERAND", "NONE"}
    assert routes <= set(qs.GROUNDING_FAILURE_MAP)
    assert qs.failure_for_route("SOMETHING_NEW").code is FailureCode.UNRESOLVED
    assert qs.failure_for_route("NO_COMPATIBLE_RECORD").code is FailureCode.NO_COMPATIBLE_RECORD


def test_ground_quantity_refuses_non_rc2_schema():
    legacy = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v1.schema.json").read_text())
    s, sp = source_with("200 g")
    with pytest.raises(ContractError):
        qs.ground_quantity(s, sp, GroundingContext(source_metadata=META), CFG, schema=legacy, result_id="Q1")
