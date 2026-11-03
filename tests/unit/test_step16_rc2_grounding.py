"""Synthetic controls for the explicit, opt-in rc2 CQPO grounding pipeline (S154).

Plan Step 17d order: grammar parse -> unit resolution (locale from source, else
AMBIGUOUS) -> deterministic same-dimension conversion (Q0) -> POR selection by
hard filters (else NO_COMPATIBLE_RECORD) -> interval + Q-level + conversion
record, or UNKNOWN. Invented grams = 0. All inputs are synthetic.
"""
import copy
import json
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.quantity.draft_contract import ContractError
from culinarystate.quantity.rc2_grounding import (
    PIPELINE_VERSION, GroundingContext, audit_invented_values, ground_quantity_rc2,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:grounding"]}
LOCALE_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
               "evidence_refs": ["synthetic:locale"]}
LINK_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
             "evidence_refs": ["synthetic:link"]}


def ctx(**kw):
    base = {"source_metadata": META}
    if kw.get("locale"):
        base["locale_metadata"] = LOCALE_META
    base.update(kw)
    return GroundingContext(**base)


def por(pid="POR-000001", grams=50, basis="DATABASE", verification="HUMAN_VERIFIED", **kw):
    rec = {"id": pid, "record_type": "POR", "version": 1, "status": "ACTIVE",
           "created_at": "2026-11-03T00:00:00Z", "created_by": "synthetic",
           "provenance": {"method": "MANUAL", "source_ids": []},
           "verification": {"status": verification}, "ingredient_id": "ING-000001",
           "from_unit_id": "UNIT-000001", "grams_per_unit": {"status": "MEASURED", "value": grams, "unit": "g"},
           "basis": basis, "state": None, "form": None, "packing": None, "locale": None}
    rec.update(kw)
    return rec


def egg_ctx(*records, q_levels=None):
    return ctx(ingredient_id="ING-000001", ingredient_metadata=LINK_META, por_records=records,
               unit_ids={"item": "UNIT-000001"}, por_q_levels={"DATABASE": "Q1"} if q_levels is None else q_levels)


def ground(raw, context=None):
    return ground_quantity_rc2(raw, context or ctx(), schema=SCHEMA)


def test_version_is_explicit_and_non_rc2_schema_is_refused():
    assert PIPELINE_VERSION == "CQPO_RC2_GROUNDING_V1_DRAFT"
    legacy = copy.deepcopy(SCHEMA)
    legacy["properties"]["schema_version"] = {"const": "1.0.0-rc"}
    with pytest.raises(ContractError):
        ground_quantity_rc2("200 g synthetic flour", ctx(), schema=legacy)


def test_exact_mass_is_q0_from_ast_and_validates():
    r = ground("200 g synthetic flour")
    rec = r.record
    assert rec["mass_g"] == {"status": "MEASURED", "value": 200, "unit": "g"}
    assert rec["q_level"] == "Q0" and rec["conversion_method"] == "EXACT_PHYSICAL"
    assert rec["normalized_mass_low_g"] == rec["normalized_mass_high_g"] == 200
    assert r.mass_route == "AST_EXACT_PHYSICAL" and r.issues == ()
    assert rec["raw"] == "200 g synthetic flour" and rec["schema_version"] == "1.0.0-rc2"


def test_mixed_fraction_pounds_use_exact_rationals():
    r = ground("1 1/2 lb synthetic beef")
    assert r.exact_mass == (Fraction(3, 2) * Fraction("453.59237"),) * 2
    assert r.record["mass_g"]["value"] == pytest.approx(680.388555)
    assert r.issues == ()


def test_compound_amount_masks_the_legacy_compatible_mass():
    r = ground("1 lb plus 2 oz synthetic beef")
    assert r.record["mass_g"]["status"] == "UNKNOWN" and r.record["q_level"] == "Q6"
    assert r.mass_route == "UNSUPPORTED_EXPRESSION"
    assert "UNSUPPORTED_COMPOUND_AMOUNT" in r.flags and "COMPATIBILITY_CHANNEL_MASKED" in r.flags
    assert r.issues == ()


def test_locale_convention_volume_range_with_locale_and_never_mass():
    r = ground("2-3 tbsp synthetic oil", ctx(locale="US"))
    rec = r.record
    assert r.unit_resolution == "VOLUME_LOCALE_CONVENTION"
    assert rec["volume_ml"]["status"] == "RANGE" and rec["mass_g"]["status"] == "UNKNOWN"
    assert {"kind": "SOURCE_RANGE", "low": rec["volume_ml"]["low"], "high": rec["volume_ml"]["high"],
            "unit": "mL"} in rec["intervals"]
    assert rec["q_level"] == "Q6" and r.issues == ()


def test_missing_locale_is_ambiguous_not_guessed():
    r = ground("2 tbsp synthetic oil")
    assert r.unit_resolution == "VOLUME_LOCALE_AMBIGUOUS"
    assert r.record["volume_ml"]["status"] == "UNKNOWN" and "LOCALE_AMBIGUOUS" in r.flags
    assert r.record.get("locale") is None and r.issues == ()


def test_convention_without_pinned_authority_is_flagged():
    r = ground("1 tbsp synthetic oil", ctx(locale="UK"))
    assert r.record["volume_ml"]["value"] == 15 and "CONVENTION_NEEDS_SOURCE" in r.flags


def test_physical_volume_is_exact_and_not_converted_to_mass():
    r = ground("200ml synthetic stock")
    assert r.record["volume_ml"] == {"status": "MEASURED", "value": 200, "unit": "mL"}
    assert r.record["mass_g"]["status"] == "UNKNOWN" and r.unit_resolution == "VOLUME_PHYSICAL"


@pytest.mark.parametrize("raw,grams", [("2 x 400g cans synthetic tomatoes", 800),
                                       ("0 x 400g cans synthetic tomatoes", 0)])
def test_package_content_is_source_stated_and_zero_stays_zero(raw, grams):
    r = ground(raw)
    assert r.record["mass_g"]["value"] == grams and r.record["mass_g"]["status"] == "MEASURED"
    assert r.record["conversion_method"] == "SOURCE_STATED" and r.mass_route == "AST_PACKAGE_SOURCE_STATED"
    assert r.issues == ()


def test_parenthetical_mass_is_source_stated_and_dual_expression_recorded():
    r = ground("1 cup (240 g) synthetic sugar", ctx(locale="US"))
    rec = r.record
    assert rec["mass_g"]["value"] == 240 and r.mass_route == "PARENTHETICAL_SOURCE_STATED"
    assert rec["volume_ml"]["status"] == "MEASURED" and rec["dual_expression_check"]["conflict"] is None
    assert r.issues == ()


def test_count_without_ingredient_link_has_no_grams():
    r = ground("3 synthetic eggs")
    assert r.record["count"] == {"status": "MEASURED", "value": 3, "unit": "item"}
    assert r.record["mass_g"]["status"] == "UNKNOWN" and r.mass_route == "NO_INGREDIENT_LINK"


def test_single_human_verified_por_is_selected_with_trace():
    r = ground("3 synthetic eggs", egg_ctx(por()))
    rec = r.record
    assert r.mass_route == "POR_SELECTED" and rec["portion_id"] == "POR-000001"
    assert rec["mass_g"]["value"] == 150 and rec["q_level"] == "Q1"
    assert rec["conversion_method"] == "PORTION_RECORD" and r.issues == ()
    assert audit_invented_values(rec, por_records=[por()]) == []


@pytest.mark.parametrize("record,route", [
    (por(verification="UNVERIFIED"), "NO_COMPATIBLE_RECORD"),
    (por(verification="AI_PRECHECKED"), "NO_COMPATIBLE_RECORD"),
    (por(state="cooked"), "NO_COMPATIBLE_RECORD"),
    (por(ingredient_id="ING-000002"), "NO_COMPATIBLE_RECORD"),
    (por(status="DEPRECATED"), "NO_COMPATIBLE_RECORD"),
    (por(basis="CONVENTION"), "POR_Q_LEVEL_RULING_PENDING"),
])
def test_por_hard_filters_and_open_rulings_leave_mass_unknown(record, route):
    r = ground("3 synthetic eggs", egg_ctx(record))
    assert r.mass_route == route and r.record["mass_g"]["status"] == "UNKNOWN"
    assert r.record.get("portion_id") is None and r.record["q_level"] == "Q6"


def test_two_compatible_por_records_are_not_tie_broken():
    r = ground("3 synthetic eggs", egg_ctx(por(), por(pid="POR-000002", grams=55)))
    assert r.mass_route == "AMBIGUOUS_POR_RECORDS" and r.record["mass_g"]["status"] == "UNKNOWN"


def test_unmapped_unit_id_cannot_select_a_portion():
    c = egg_ctx(por())
    c = GroundingContext(**{**c.__dict__, "unit_ids": {}})
    assert ground("3 synthetic eggs", c).mass_route == "UNIT_ID_UNMAPPED"


@pytest.mark.parametrize("raw,route", [("a pinch of synthetic salt", "QUALITATIVE"),
                                       ("synthetic pepper to taste", "QUALITATIVE"),
                                       ("2 or 3 synthetic carrots", "ALTERNATIVE"),
                                       ("juice of 1 synthetic lemon", "UNSUPPORTED_EXPRESSION")])
def test_qualitative_alternative_and_unsupported_lines_stay_unknown(raw, route):
    r = ground(raw)
    assert r.mass_route == route and r.record["mass_g"]["status"] == "UNKNOWN"
    assert r.record["q_level"] == "Q6" and r.issues == ()


LINES = ["200 g synthetic flour", "1/3 cup synthetic milk", "2 katori synthetic dal", "1 (14 oz) can synthetic beans",
         "1.5 kg synthetic potatoes", "2 large synthetic onions", "synthetic salt", "3-4 synthetic cloves",
         "1 heaped tbsp synthetic sugar", "about 2 cups synthetic water", "1 1/2 cups synthetic rice plus extra"]


@pytest.mark.parametrize("raw", LINES)
@pytest.mark.parametrize("locale", [None, "US", "UK", "IN"])
def test_every_record_is_contract_valid_deterministic_and_audit_clean(raw, locale):
    c = ctx(locale=locale) if locale else ctx()
    before = copy.deepcopy(c)
    a, b = ground(raw, c), ground(raw, c)
    assert a.issues == ()
    assert json.dumps(a.record, sort_keys=True) == json.dumps(b.record, sort_keys=True)
    assert a.record["raw"] == raw and c == before


def test_audit_catches_a_tampered_or_untraced_mass():
    rec = copy.deepcopy(ground("200 g synthetic flour").record)
    rec["mass_g"]["value"] = 201
    assert "MASS_TRACE_MISMATCH" in {i.code for i in audit_invented_values(rec)}
    rec = copy.deepcopy(ground("3 synthetic eggs").record)
    rec["mass_g"] = {"status": "MEASURED", "value": 150, "unit": "g"}
    assert "MASS_WITHOUT_TRACE" in {i.code for i in audit_invented_values(rec)}


def test_audit_rejects_a_portion_trace_not_backed_by_a_supplied_record():
    rec = ground("3 synthetic eggs", egg_ctx(por())).record
    assert "MASS_TRACE_MISMATCH" in {i.code for i in audit_invented_values(rec, por_records=[por(grams=60)])}
    assert "MASS_WITHOUT_TRACE" in {i.code for i in audit_invented_values(rec, por_records=[])}


def test_audit_checks_normalized_bounds_match_mass():
    rec = copy.deepcopy(ground("200 g synthetic flour").record)
    rec["normalized_mass_high_g"] = 250
    assert "NORMALIZED_BOUNDS_MISMATCH" in {i.code for i in audit_invented_values(rec)}


def test_supplied_envelope_is_used_without_minting_ids():
    env = {"id": "QNT-000123", "version": 2, "status": "ACTIVE", "created_at": "2026-11-03T00:00:00Z",
           "created_by": "synthetic", "provenance": {"method": "RULE", "source_ids": []},
           "verification": {"status": "UNVERIFIED"}}
    r = ground("200 g synthetic flour", ctx(envelope=env))
    assert r.record["id"] == "QNT-000123" and r.record["version"] == 2
    assert ground("200 g synthetic flour").record["id"] == "QNT-000000"


@pytest.mark.parametrize("raw", ["", "   "])
def test_blank_lines_are_refused_not_turned_into_records(raw):
    with pytest.raises(ContractError):
        ground(raw)


def test_line_without_any_amount_is_no_quantity_not_unsupported():
    r = ground("synthetic salt")
    assert r.mass_route == "NO_QUANTITY" and r.record["mass_g"]["status"] == "UNKNOWN"


def test_inverted_source_range_is_reported_and_not_repaired():
    r = ground("3 - 2 g synthetic flour")
    assert r.record["parsed"]["low"] == 3 and r.record["parsed"]["high"] == 2
    assert r.record["mass_g"]["status"] == "UNKNOWN"
    assert "INVERTED_INTERVAL" in {i.code for i in r.issues}


from hypothesis import given, settings, strategies as st  # noqa: E402

TOKENS = ["1", "2", "0", "1/2", "3/4", "1 1/2", "-", "to", "or", "x", "plus", "(", ")", "g", "kg", "oz", "lb",
          "ml", "l", "cup", "cups", "tbsp", "tsp", "can", "cans", "pinch", "about", "heaped", "katori",
          "synthetic", "item", "of", "large", "juice", "400g", "2x"]


@settings(max_examples=300, deadline=None)
@given(st.lists(st.sampled_from(TOKENS), min_size=1, max_size=7), st.sampled_from([None, "US", "UK", "IN", "AU"]))
def test_property_no_generated_gram_lacks_a_trace(tokens, locale):
    raw = " ".join(tokens)
    if not raw.strip():
        return
    try:
        r = ground(raw, ctx(locale=locale) if locale else ctx())
    except ContractError:
        return  # explicit refusal is allowed; silently invented grams are not
    assert audit_invented_values(r.record) == []
    assert r.record["raw"] == raw
    if r.record["mass_g"]["status"] != "UNKNOWN":
        assert r.record["q_level"] == "Q0" and r.mass_route.startswith(("AST_", "PARENTHETICAL"))
