"""Step 17a invented-value auditor on synthetic outputs (DRAFT_PENDING_16c).

Every numeric or categorical output value must trace to a raw source span
(literally, or through a reproducible deterministic rule), to a supplied
candidate set, or to a grounded rc2 QNT record whose grams pass the existing
``rc2_grounding.audit_invented_values`` (Q0 arithmetic or a selected
HUMAN_VERIFIED POR). The invented count is an integer. Synthetic texts only.
"""
from __future__ import annotations

import copy
import json
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from culinarystate.extraction import auditor as aud
from culinarystate.extraction.interfaces import (
    EntityCandidate, EventCandidate, EventGraph, LinkCandidate, LinkResult, Mention, MentionSet,
    QuantityGroundingResult, QuantityParseResult, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim,
    ValueKind,
)
from culinarystate.extraction.quantity_stages import ground_quantity, parse_quantity
from culinarystate.quantity.rc2_grounding import GroundingContext

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:17a"]}
LINK_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
             "evidence_refs": ["synthetic:link"]}
LOCALE_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
               "evidence_refs": ["synthetic:locale"]}
CFG = StageConfig(rung_id="A", params={"v": 0}, claim_route="INFERRED_RULE",
                  annotated_labels=frozenset({"ACTION", "DURATION"}))
RAW = "Simmer for 10 minutes, then bake 20–25 minutes at 180C until golden. Rest ten minutes."


def src(raw=RAW):
    return SourceText.from_raw("SYN-A", raw)


def at(s, needle, occurrence=0):
    start = -1
    for _ in range(occurrence + 1):
        start = s.raw.index(needle, start + 1)
    return Span.of(s, start, start + len(needle))


def claim(field, kind, value, span=None, trace=TraceKind.SPAN_LITERAL, **kw):
    t = kw.pop("trace_obj", None) or Trace(trace, rule_id=kw.pop("rule_id", None),
                                           ref_ids=kw.pop("ref_ids", ()), candidates=kw.pop("candidates", ()))
    kw.setdefault("origin", "EXPLICIT_SOURCE" if trace is TraceKind.SPAN_LITERAL else "DERIVED_DETERMINISTIC")
    kw.setdefault("claim_route", "EXPLICIT" if trace is TraceKind.SPAN_LITERAL else "INFERRED_RULE")
    return ValueClaim(field=field, kind=kind, value=value, span=span, trace=t, **kw)


def graph_with(s, *attrs):
    return EventGraph("SYN-A", s.sha256, (EventCandidate("E1", (0, 0), at(s, "Simmer"), attributes=tuple(attrs)),),
                      (), (), {}, CFG.provenance("build_events"))


def audit(s, *outputs, **kw):
    return aud.audit_outputs(s, list(outputs), **kw)


def icodes(report):
    return sorted(f.code for f in report.findings if f.invented)


def test_module_is_draft_and_versioned():
    assert "DRAFT_PENDING_16c" in aud.__doc__.splitlines()[0]
    assert aud.AUDITOR_VERSION.endswith("_DRAFT")


@pytest.mark.parametrize("text,expected", [
    ("Bake 20–25 minutes at 180C", {20, 25, 180}),
    ("Add 1 1/2 cups", {Fraction(3, 2)}),
    ("Add ½ cup", {Fraction(1, 2)}),
    ("Add 1½ tsp", {Fraction(3, 2)}),
    ("Add 2.5 kg", {Fraction(5, 2)}),
    ("Add ⅓ cup", {Fraction(1, 3)}),
    ("Cook १० मिनट", {10}),
    ("Rest ten minutes", set()),
    ("Divide by 3/0", {3, 0}),
])
def test_numbers_in_text_reads_literal_numbers_only(text, expected):
    assert aud.numbers_in_text(text) == frozenset(Fraction(x) for x in expected)


def test_thousands_separator_is_not_read_as_one_number():
    assert Fraction(1000) not in aud.numbers_in_text("Add 1,000 g")


def test_literal_span_values_pass_and_invented_magnitudes_fail():
    s = src()
    ok = graph_with(s, claim("duration", ValueKind.DURATION, 10, at(s, "10 minutes"), unit="minutes"),
                    claim("bake_time", ValueKind.DURATION, (20, 25), at(s, "20–25 minutes")),
                    claim("temperature", ValueKind.TEMPERATURE, 180, at(s, "180C"), unit="C"),
                    claim("endpoint", ValueKind.TEXT, "until golden", at(s, "until golden")))
    r = audit(s, ok)
    assert r.invented_count == 0 and r.status == "PASS" and r.values_checked == 4
    bad = graph_with(s, claim("duration", ValueKind.DURATION, 12, at(s, "10 minutes")),
                     claim("temperature", ValueKind.TEMPERATURE, 160, at(s, "until golden"), unit="degC"),
                     claim("endpoint", ValueKind.TEXT, "until browned", at(s, "until golden")))
    r = audit(s, bad)
    assert r.invented_count == 3 and r.status == "FAIL"
    assert icodes(r) == ["NUMERIC_NOT_IN_SPAN", "NUMERIC_NOT_IN_SPAN", "VALUE_NOT_IN_SPAN"]


def test_literal_unit_must_be_raw_unit_text_in_the_span():
    s = src()
    r = audit(s, graph_with(s, claim("temperature", ValueKind.TEMPERATURE, 180, at(s, "180C"), unit="degF")))
    assert icodes(r) == ["UNIT_NOT_IN_SPAN"]


def test_untraced_values_and_missing_spans_are_invented():
    s = src()
    r = audit(s, graph_with(s, claim("temperature", ValueKind.TEMPERATURE, 180, None, trace=TraceKind.NONE),
                            claim("ph", ValueKind.PH, 4.6, None, trace=TraceKind.SPAN_LITERAL),
                            claim("event_kind", ValueKind.CATEGORICAL, "ACTION", None, trace=TraceKind.REGISTRY_LABEL)))
    assert r.invented_count == 3
    assert icodes(r) == ["SPAN_MISSING", "SPAN_MISSING", "UNTRACED_VALUE"]


def test_unknown_is_valid_but_unknown_with_a_value_is_invented():
    s = src()
    r = audit(s, graph_with(s, claim("temperature", ValueKind.TEMPERATURE, None, None, trace=TraceKind.NONE,
                                     status="UNKNOWN", origin="UNKNOWN")))
    assert r.invented_count == 0 and r.findings == ()
    r = audit(s, graph_with(s, claim("temperature", ValueKind.TEMPERATURE, 180, None, trace=TraceKind.NONE,
                                     status="UNKNOWN")))
    assert icodes(r) == ["UNKNOWN_WITH_VALUE"]
    r = audit(s, graph_with(s, claim("temperature", ValueKind.TEMPERATURE, None, at(s, "180C"))))
    assert r.invented_count == 0 and [f.code for f in r.findings] == ["KNOWN_WITHOUT_VALUE"]


def word_number(text):
    words = {"ten": 10}
    first, _, rest = text.partition(" ")
    return words[first], "min" if rest == "minutes" else None


def test_rule_traces_must_be_reproducible_from_the_span_text():
    s = src()
    span = at(s, "ten minutes")
    good = claim("rest", ValueKind.DURATION, 10, span, trace=TraceKind.SPAN_RULE, rule_id="WORD_NUMBER_V0", unit="min")
    assert audit(s, graph_with(s, good), recomputers={"WORD_NUMBER_V0": word_number}).invented_count == 0
    assert icodes(audit(s, graph_with(s, good))) == ["RULE_NOT_REPRODUCIBLE"]
    wrong = replace(good, value=12)
    assert icodes(audit(s, graph_with(s, wrong), recomputers={"WORD_NUMBER_V0": word_number})) == ["RULE_MISMATCH"]
    wrong_unit = replace(good, unit="h")
    assert icodes(audit(s, graph_with(s, wrong_unit), recomputers={"WORD_NUMBER_V0": word_number})) == \
        ["RULE_MISMATCH"]
    no_id = replace(good, trace=Trace(TraceKind.SPAN_RULE))
    assert icodes(audit(s, graph_with(s, no_id))) == ["RULE_ID_MISSING"]

    def boom(text):
        raise KeyError(text)

    assert icodes(audit(s, graph_with(s, good), recomputers={"WORD_NUMBER_V0": boom})) == ["RULE_NOT_REPRODUCIBLE"]


def test_trace_kinds_are_restricted_per_value_kind():
    s = src()
    sp = at(s, "180C")
    r = audit(s, graph_with(s,
                            claim("t1", ValueKind.TEMPERATURE, 180, sp, trace=TraceKind.REGISTRY_LABEL),
                            claim("t2", ValueKind.TEMPERATURE, 180, sp, trace=TraceKind.CANDIDATE_SELECTION,
                                  candidates=("180",)),
                            claim("t3", ValueKind.TEMPERATURE, 180, sp, trace=TraceKind.QNT_RECORD, ref_ids=("Q1",)),
                            claim("m1", ValueKind.MASS_G, 180, sp),
                            claim("c1", ValueKind.COUNT, 180, sp, trace=TraceKind.REGISTRY_LABEL)))
    assert icodes(r) == ["MAGNITUDE_TRACE_NOT_ALLOWED"] * 4 + ["TRACE_KIND_NOT_ALLOWED"]


def test_candidate_selection_must_stay_inside_candidates():
    s = src()
    sp = at(s, "Simmer")
    link = LinkResult("M1", sp, (LinkCandidate("PROC-000001"),), CFG.provenance("link"), selected_id="PROC-000001")
    assert audit(s, link).invented_count == 0
    bad = claim("process_id", ValueKind.IDENTIFIER, "PROC-000009", sp, trace=TraceKind.CANDIDATE_SELECTION,
                candidates=("PROC-000001",))
    assert icodes(audit(s, graph_with(s, bad))) == ["SELECTION_OUTSIDE_CANDIDATES"]
    forged = replace(link.claims()[0], value="PROC-000002")
    assert icodes(audit(s, graph_with(s, forged))) == ["SELECTION_OUTSIDE_CANDIDATES"]


def test_span_that_does_not_round_trip_is_not_evidence():
    s = src()
    sp = at(s, "10 minutes")
    forged = Span(sp.text_id, sp.raw_sha256, sp.segments, ("12 minutes",))
    r = audit(s, graph_with(s, claim("duration", ValueKind.DURATION, 12, forged)))
    assert icodes(r) == ["SPAN_NOT_IN_SOURCE"]


def test_mention_labels_are_audited_as_registry_labels_on_their_span():
    s = src()
    ms = MentionSet("SYN-A", s.sha256, (Mention("M1", "ACTION", at(s, "Simmer")),), CFG.provenance("extract_mentions"))
    r = audit(s, ms)
    assert r.invented_count == 0 and r.values_checked == 1


# ------------------------------------------------------------------ quantity records
def qsrc(expr):
    s = SourceText.from_raw("SYN-Q", f"Add {expr} to the pot.")
    return s, Span.of(s, 4, 4 + len(expr))


def por(grams=50):
    return {"id": "POR-000001", "record_type": "POR", "version": 1, "status": "ACTIVE",
            "created_at": "2026-11-03T00:00:00Z", "created_by": "synthetic",
            "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "HUMAN_VERIFIED"},
            "ingredient_id": "ING-000001", "from_unit_id": "UNIT-000001",
            "grams_per_unit": {"status": "MEASURED", "value": grams, "unit": "g"}, "basis": "DATABASE",
            "state": None, "form": None, "packing": None, "locale": None}


def grounded(expr, context=None, rid="Q1"):
    s, sp = qsrc(expr)
    return s, ground_quantity(s, sp, context or GroundingContext(source_metadata=META), CFG, schema=SCHEMA,
                              result_id=rid)


def tampered(g, **changes):
    rec = copy.deepcopy(g.record)
    for key, value in changes.items():
        rec[key] = value
    return QuantityGroundingResult(g.result_id, g.span, g.provenance, record=rec, grounding=g.grounding,
                                   failure=g.failure)


@pytest.mark.parametrize("expr", ["200 g", "2 x 400 g", "1 1/2 kg", "1-2 lb", "500 ml", "2", "to taste", "1 cup",
                                  "1 lb plus 2 oz", "salt"])
def test_pipeline_records_have_zero_invented_values(expr):
    s, g = grounded(expr)
    before = copy.deepcopy(g.record)
    r = audit(s, g)
    assert r.invented_count == 0, r.findings
    assert g.record == before


def test_tampered_grams_are_one_invented_value_via_rc2_audit():
    s, g = grounded("2 x 400 g")
    bad = tampered(g, mass_g={"status": "MEASURED", "value": 900, "unit": "g"},
                   normalized_mass_low_g=900, normalized_mass_high_g=900)
    r = audit(s, bad)
    assert r.invented_count == 1
    assert "MASS_TRACE_MISMATCH" in icodes(r)
    assert {f.path for f in r.findings if f.invented} == {"Q1/mass_g"}


def test_grams_from_a_por_need_the_selected_human_verified_record():
    ctx = GroundingContext(source_metadata=META, ingredient_id="ING-000001", ingredient_metadata=LINK_META,
                           por_records=(por(),), unit_ids={"item": "UNIT-000001"}, por_q_levels={"DATABASE": "Q1"})
    s, g = grounded("2", ctx)
    assert g.record["mass_g"]["value"] == 100
    assert audit(s, g, por_records=[por()]).invented_count == 0
    r = audit(s, g)
    assert r.invented_count == 1 and "MASS_WITHOUT_TRACE" in icodes(r)


def test_volume_and_count_channels_are_recomputed_from_q0():
    ctx = GroundingContext(source_metadata=META, locale="US", locale_metadata=LOCALE_META)
    s, g = grounded("1 cup", ctx)
    assert audit(s, g).invented_count == 0
    assert icodes(audit(s, tampered(g, volume_ml={"status": "MEASURED", "value": 250, "unit": "mL"}))) == \
        ["QNT_VOLUME_NOT_Q0"]
    s2, g2 = grounded("200 g")
    assert icodes(audit(s2, tampered(g2, volume_ml={"status": "MEASURED", "value": 200, "unit": "mL"}))) == \
        ["QNT_VOLUME_NOT_Q0"]
    s3, g3 = grounded("2")
    assert icodes(audit(s3, tampered(g3, count={"status": "MEASURED", "value": 3, "unit": "item"}))) == \
        ["QNT_COUNT_MISMATCH"]
    assert icodes(audit(s2, tampered(g2, normalized={"status": "MEASURED", "value": 2, "unit": "kg"}))) == \
        ["QNT_NORMALIZED_MISMATCH"]


def test_record_must_be_reproducible_from_its_raw_span():
    s, g = grounded("200 g")
    ast = copy.deepcopy(g.record["ast"])
    ast["numerator"] = 300
    r = audit(s, tampered(g, ast=ast))
    assert "QNT_AST_NOT_REPRODUCIBLE" in icodes(r)
    parsed = dict(g.record["parsed"], value=300)
    assert "QNT_PARSED_NOT_REPRODUCIBLE" in icodes(audit(s, tampered(g, parsed=parsed)))
    assert "QNT_RAW_NOT_SPAN" in icodes(audit(s, tampered(g, raw="300 g")))


def test_qnt_record_traces_from_other_outputs_must_match_the_record():
    s, g = grounded("2 x 400 g")
    sp = g.span
    ok = claim("amount", ValueKind.MASS_G, 800, sp, trace=TraceKind.QNT_RECORD, ref_ids=("Q1",), unit="g")
    ev = EventGraph("SYN-Q", s.sha256, (EventCandidate("E1", (0, 0), attributes=(ok,)),), (), (), {},
                    CFG.provenance("build_events"))
    assert audit(s, g, ev).invented_count == 0
    ev_bad = EventGraph("SYN-Q", s.sha256, (EventCandidate("E1", (0, 0), attributes=(replace(ok, value=900),)),),
                        (), (), {}, CFG.provenance("build_events"))
    assert icodes(audit(s, g, ev_bad)) == ["QNT_VALUE_MISMATCH"]
    assert icodes(audit(s, ev)) == ["QNT_REF_MISSING"]
    bad_g = tampered(g, mass_g={"status": "MEASURED", "value": 900, "unit": "g"},
                     normalized_mass_low_g=900, normalized_mass_high_g=900)
    ev_900 = EventGraph("SYN-Q", s.sha256, (EventCandidate("E1", (0, 0), attributes=(replace(ok, value=900),)),),
                        (), (), {}, CFG.provenance("build_events"))
    assert "QNT_REF_INVENTED" in icodes(audit(s, bad_g, ev_900))


def test_quantity_parse_results_are_recomputed():
    s, sp = qsrc("1 1/2 kg")
    p = parse_quantity(s, sp, CFG, source_metadata=META, result_id="P1")
    assert audit(s, p).invented_count == 0
    ast = copy.deepcopy(p.ast)
    ast["numerator"] = 7
    forged = QuantityParseResult(p.result_id, p.span, p.expression, p.source_metadata, p.provenance, ast=ast,
                                 arithmetic_status=p.arithmetic_status)
    assert icodes(audit(s, forged)) == ["QPARSE_AST_NOT_REPRODUCIBLE"]


def test_duplicate_result_ids_are_reported_not_merged():
    s, g = grounded("200 g")
    r = audit(s, g, g)
    assert "DUPLICATE_RESULT_ID" in [f.code for f in r.findings if not f.invented]


def test_counts_are_integers_and_text_free():
    s = src()
    r = audit(s, graph_with(s, claim("duration", ValueKind.DURATION, 12, at(s, "10 minutes")),
                            claim("t", ValueKind.TEMPERATURE, 180, None, trace=TraceKind.NONE)))
    counts = r.counts()
    assert counts["invented_count"] == 2 and type(counts["invented_count"]) is int
    assert all(type(v) is int for v in counts["invented_by_code"].values())
    assert set(counts) == {"invented_count", "values_checked", "findings_total", "invented_by_code"}
    assert "minutes" not in json.dumps(counts)


@settings(max_examples=60, deadline=None)
@given(n=st.integers(min_value=0, max_value=5000), unit=st.sampled_from(["g", "kg", "mg", "oz", "lb"]),
       delta=st.integers(min_value=1, max_value=50))
def test_property_grounded_grams_trace_and_any_shift_is_caught(n, unit, delta):
    s, g = grounded(f"{n} {unit}")
    assert audit(s, g).invented_count == 0
    mass = g.record["mass_g"]
    shifted = mass["value"] + delta
    bad = tampered(g, mass_g=dict(mass, value=shifted), normalized_mass_low_g=shifted, normalized_mass_high_g=shifted)
    assert audit(s, bad).invented_count == 1
