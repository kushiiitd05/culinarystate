"""S161 real-data finding: "º" (U+00BA) used as a degree sign made the auditor flag real units.

The S161 Step 17b real-data dry-run (seed sha256 1037f2ed..., 1,000 recipes) reported
invented_count 23, all UNIT_NOT_IN_SPAN, all TEMPERATURE claims in Food.com texts written
as "<number>ºF" / "<number>ºC". The temperature rule (``evidence.conditions.TEMP_RE``)
accepts "º" as a degree marker, but U+00BA is a Unicode letter (category Lo), so the
auditor's whole-token check read "ºF" as one word and refused the literal unit.

Synthetic text only; no recipe text from the corpus.
"""
from __future__ import annotations

from culinarystate.extraction import auditor as aud
from culinarystate.extraction.interfaces import (
    EventCandidate, EventGraph, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim, ValueKind,
)
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity import rc2_dryrun as D

CFG = StageConfig(rung_id="S161", params={"v": 0}, claim_route="INFERRED_RULE")


def at(s: SourceText, needle: str) -> Span:
    i = s.raw.index(needle)
    return Span.of(s, i, i + len(needle))


def literal(value, span: Span, unit: str) -> ValueClaim:
    return ValueClaim("temperature", ValueKind.TEMPERATURE, value, origin="EXPLICIT_SOURCE", claim_route="EXPLICIT",
                      span=span, trace=Trace(TraceKind.SPAN_LITERAL), unit=unit)


def invented(s: SourceText, claim: ValueClaim) -> list[str]:
    g = EventGraph(s.text_id, s.sha256, (EventCandidate("E1", (0, 0), at(s, "Bake"), attributes=(claim,)),),
                   (), (), {}, CFG.provenance("build_events"))
    return sorted(f.code for f in aud.audit_outputs(s, [g]).findings if f.invented)


def test_ordinal_indicator_degree_sign_unit_is_a_literal_token():
    s = SourceText.from_raw("SYN-S161-A", "Bake at 350ºF. Bake at 180ºC. Bake at 200 ºC.")
    assert invented(s, literal(350, at(s, "350ºF"), "F")) == []
    assert invented(s, literal(180, at(s, "180ºC"), "C")) == []
    assert invented(s, literal(200, at(s, "200 ºC"), "C")) == []


def test_degree_sign_and_letter_boundaries_unchanged():
    s = SourceText.from_raw("SYN-S161-B", "Bake at 350°F. Bake: Cook 180 then rest. Bake at 90aF.")
    assert invented(s, literal(350, at(s, "350°F"), "F")) == []
    assert invented(s, literal(180, at(s, "Cook 180"), "C")) == ["UNIT_NOT_IN_SPAN"]
    assert invented(s, literal(90, at(s, "90aF"), "F")) == ["UNIT_NOT_IN_SPAN"]


def test_rung_a_on_ordinal_degree_text_invents_nothing():
    s = SourceText.from_raw("SYN-S161-C", "Preheat oven to 350ºF.\nBake the dough for 20 minutes at 180ºC.")
    rung = RungA()
    res = rung.run(s, rung.config(), schema=D.load_schema())
    report = aud.audit_outputs(s, res.all(), recomputers=rung.recomputers())
    assert report.invented_count == 0, report.invented_by_code
