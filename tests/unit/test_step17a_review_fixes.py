"""S155 AI cross-review of Step 17a: failing controls for defects found (DRAFT_PENDING_16c).

Each test reproduces one finding of ``reports/step17/S155_17a_ai_review.md``
(AI verdict, pending Kush/Parv review) on synthetic text only:

- R1 a literal magnitude was accepted when its number and unit came from
  different places of a wide span ("Bake 20 minutes at 180C" -> 180 minutes);
- R2 a minus sign was dropped, so +18 was accepted for "-18°C";
- R3 ``StageConfig.config_hash`` ignored claim_route and annotation coverage;
- R4 cross-output references (link/ref mention ids, antecedent entity ids) were
  never checked, so ghost ids passed V1-V4;
- R5 categorical / identifier claims without a vocabulary or id set were silently
  unchecked by V3 (not even listed in ``not_checked``).
"""
from __future__ import annotations

from fractions import Fraction

from culinarystate.extraction import auditor as aud
from culinarystate.extraction.interfaces import (
    EntityCandidate, EventCandidate, EventGraph, LinkCandidate, LinkResult, Mention, MentionSet, ReferenceResult,
    SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim, ValueKind,
)
from culinarystate.extraction.invariants import run_validators
from culinarystate.extraction.validators import v3_vocabulary

RAW = "Bake 20 minutes at 180C. Freeze at -18°C. Stir 1 -2 times. Cook 1 - 2 hours."
CFG = StageConfig(rung_id="REVIEW", params={"v": 0}, claim_route="INFERRED_RULE")


def src() -> SourceText:
    return SourceText.from_raw("SYN-REVIEW", RAW)


def at(s: SourceText, needle: str) -> Span:
    i = s.raw.index(needle)
    return Span.of(s, i, i + len(needle))


def literal(field: str, kind: ValueKind, value, span: Span, unit: str | None = None) -> ValueClaim:
    return ValueClaim(field, kind, value, origin="EXPLICIT_SOURCE", claim_route="EXPLICIT", span=span,
                      trace=Trace(TraceKind.SPAN_LITERAL), unit=unit)


def graph(s: SourceText, *attrs: ValueClaim, entities=(), lots=None) -> EventGraph:
    return EventGraph(s.text_id, s.sha256, (EventCandidate("E1", (0, 0), at(s, "Bake"), attributes=attrs),),
                      tuple(entities), (), dict(lots or {}), CFG.provenance("build_events"))


def invented(s: SourceText, *outputs) -> list[str]:
    return sorted(f.code for f in aud.audit_outputs(s, list(outputs)).findings if f.invented)


# ---------------------------------------------------------------- R1
def test_r1_literal_number_and_unit_must_not_come_from_different_parts_of_a_wide_span():
    s = src()
    wide = at(s, "Bake 20 minutes at 180C")
    assert invented(s, graph(s, literal("duration", ValueKind.DURATION, 180, wide, "minutes"))) != []
    assert invented(s, graph(s, literal("temperature", ValueKind.TEMPERATURE, 20, wide, "C"))) != []


def test_r1_tight_literal_spans_still_pass():
    s = src()
    ok = graph(s, literal("duration", ValueKind.DURATION, 20, at(s, "20 minutes"), "minutes"),
               literal("temperature", ValueKind.TEMPERATURE, 180, at(s, "180C"), "C"),
               literal("cook", ValueKind.DURATION, (1, 2), at(s, "1 - 2 hours"), "hours"))
    assert invented(s, ok) == []


def test_r1_literal_unit_must_be_a_whole_unit_token_not_a_letter_inside_a_word():
    s = SourceText.from_raw("SYN-REVIEW-U", "Bake: Cook 180 then rest.")
    assert invented(s, graph(s, literal("temperature", ValueKind.TEMPERATURE, 180, at(s, "Cook 180"), "C"))) \
        == ["UNIT_NOT_IN_SPAN"]


# ---------------------------------------------------------------- R2
def test_r2_attached_minus_sign_is_read_and_positive_value_is_not_accepted():
    assert aud.numbers_in_text("-18°C") == frozenset({Fraction(-18)})
    assert aud.numbers_in_text("at −5 C") == frozenset({Fraction(-5)})
    s = src()
    assert invented(s, graph(s, literal("t", ValueKind.TEMPERATURE, 18, at(s, "-18°C"), "C"))) != []
    assert invented(s, graph(s, literal("t", ValueKind.TEMPERATURE, -18, at(s, "-18°C"), "C"))) == []


def test_r2_range_dashes_are_not_signs():
    assert aud.numbers_in_text("20-25 minutes") == frozenset({Fraction(20), Fraction(25)})
    assert aud.numbers_in_text("1 -2 times") == frozenset({Fraction(1), Fraction(2)})
    assert aud.numbers_in_text("1 - 2 hours") == frozenset({Fraction(1), Fraction(2)})


# ---------------------------------------------------------------- R3
def test_r3_config_hash_covers_claim_route_and_annotation_provenance():
    base = StageConfig("A", {"x": 1}, "INFERRED_RULE")
    assert base.config_hash != StageConfig("A", {"x": 1}, "INFERRED_LLM").config_hash
    assert base.config_hash != StageConfig("A", {"x": 1}, "INFERRED_RULE",
                                           annotated_labels=frozenset({"ACTION"})).config_hash
    assert base.config_hash != StageConfig("A", {"x": 1}, "INFERRED_RULE", annotation_mode="OPEN").config_hash
    same = StageConfig("A", {"x": 1}, "INFERRED_RULE", annotated_labels=frozenset({"B", "A"}))
    assert same.config_hash == StageConfig("A", {"x": 1}, "INFERRED_RULE",
                                           annotated_labels=frozenset({"A", "B"})).config_hash


# ---------------------------------------------------------------- R4
def _mentions(s: SourceText) -> MentionSet:
    return MentionSet(s.text_id, s.sha256, (Mention("M1", "ACTION", at(s, "Bake")),),
                      CFG.provenance("extract_mentions"))


def test_r4_reference_to_a_ghost_entity_or_mention_fails_v4():
    s = src()
    g = graph(s, entities=(EntityCandidate("N1", "INGREDIENT_LOT", "ACTIVE"),), lots={"N1": "USED"})
    ghost = ReferenceResult("M404", at(s, "Freeze"), ("N_GHOST",), CFG.provenance("resolve_refs"),
                            antecedent_ids=("N_GHOST",))
    link = LinkResult("M405", at(s, "Bake"), (LinkCandidate("PROC-000001"),), CFG.provenance("link"),
                      selected_id="PROC-000001")
    reports = run_validators(s, [_mentions(s), g, ghost, link])
    codes = [i.code for i in reports["V4"].issues]
    assert codes.count("REFERENCED_ID_MISSING") == 3 and reports["V4"].status == "FAIL"


def test_r4_valid_cross_references_pass_and_missing_targets_are_reported_not_checked():
    s = src()
    g = graph(s, entities=(EntityCandidate("N1", "INGREDIENT_LOT", "ACTIVE"),), lots={"N1": "USED"})
    ok = ReferenceResult("M1", at(s, "Bake"), ("N1",), CFG.provenance("resolve_refs"), antecedent_ids=("N1",))
    assert run_validators(s, [_mentions(s), g, ok])["V4"].status == "PASS"
    alone = run_validators(s, [ok])["V4"]
    assert alone.issues == () and "CROSS_REF_NO_MENTION_SET" in alone.not_checked
    assert "CROSS_REF_NO_EVENT_GRAPH" in alone.not_checked


# ---------------------------------------------------------------- R5
def test_r5_categorical_claims_without_a_vocabulary_are_listed_as_not_checked():
    s = src()
    c = ValueClaim("process_family", ValueKind.CATEGORICAL, "MADE_UP", origin="DERIVED_DETERMINISTIC",
                   span=at(s, "Bake"), trace=Trace(TraceKind.REGISTRY_LABEL))
    r = v3_vocabulary([graph(s, c)])
    assert "CATEGORICAL_FIELD_NO_VOCAB:process_family" in r.not_checked


def test_r5_identifier_claims_are_checked_against_supplied_id_sets():
    s = src()
    c = ValueClaim("process_id", ValueKind.IDENTIFIER, "PROC-999999", origin="DERIVED_DETERMINISTIC",
                   span=at(s, "Bake"), trace=Trace(TraceKind.SPAN_RULE, rule_id="X"))
    assert "ID_SET:PROC" in v3_vocabulary([graph(s, c)]).not_checked
    bad = v3_vocabulary([graph(s, c)], id_sets={"PROC": frozenset({"PROC-000001"})})
    assert [i.code for i in bad.issues] == ["IDENTIFIER_NOT_IN_ID_SET"]
    good = v3_vocabulary([graph(s, c)], id_sets={"PROC": frozenset({"PROC-999999"})})
    assert good.status == "PASS" and "ID_SET:PROC" not in good.not_checked


# ---------------------------------------------------------------- R6 / R7
def test_r6_span_offsets_must_be_integers_not_silently_truncated():
    import pytest

    from culinarystate.extraction.interfaces import InterfaceError
    s = src()
    for bad in ((1.7, 3), (True, 3), (0, 2.0)):
        with pytest.raises(InterfaceError):
            Span.of(s, *bad)


def test_r7_event_order_must_be_two_integers_so_v4_cannot_crash():
    import pytest

    from culinarystate.extraction.interfaces import InterfaceError
    for bad in ((0, "x"), (0,), (0, 1, 2), (True, 0), [0, 1]):
        with pytest.raises(InterfaceError):
            EventCandidate("E1", bad)
    assert EventCandidate("E1", (0, 1)).order == (0, 1)
