"""Real-data finding (full-corpus Rung A prep): "<number>degF" made the auditor flag real units.

A seeded 2,000-recipe Step 17b sample (seed sha256 1037f2ed...) reported invented_count 4,
all UNIT_NOT_IN_SPAN, all TEMPERATURE claims in Food.com texts. Character-shape masks
(digits->9, letters->a) gave "999aaaa" for every span, and a boolean check confirmed the form
"<digits>deg<C|F>" with no space. The temperature rule (``evidence.conditions.TEMP_RE``)
accepts "deg", "degree(s)" and "deg." straight before the unit, but the auditor's whole-token
check (S155 review R1) read "degF" as one word and refused the literal unit.

Synthetic text only; no recipe text from the corpus.
"""
from __future__ import annotations

from culinarystate.extraction import auditor as aud
from culinarystate.extraction.interfaces import (
    EventCandidate, EventGraph, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim, ValueKind,
)
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity import rc2_dryrun as D

CFG = StageConfig(rung_id="S163", params={"v": 0}, claim_route="INFERRED_RULE")


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


def test_deg_prefix_without_space_is_a_literal_unit_token():
    s = SourceText.from_raw("SYN-S163-A", "Bake at 350degF. Bake at 180DegC. Bake at 400degreesF. Bake at 200deg.C.")
    assert invented(s, literal(350, at(s, "350degF"), "F")) == []
    assert invented(s, literal(180, at(s, "180DegC"), "C")) == []
    assert invented(s, literal(400, at(s, "400degreesF"), "F")) == []
    assert invented(s, literal(200, at(s, "200deg.C"), "C")) == []


def test_letter_boundaries_still_refuse():
    s = SourceText.from_raw("SYN-S163-B", "Bake at 90aF. Bake at 90xdegF. Bake: Cook 180 then rest.")
    assert invented(s, literal(90, at(s, "90aF"), "F")) == ["UNIT_NOT_IN_SPAN"]
    assert invented(s, literal(90, at(s, "90xdegF"), "F")) == ["UNIT_NOT_IN_SPAN"]
    assert invented(s, literal(180, at(s, "Cook 180"), "C")) == ["UNIT_NOT_IN_SPAN"]


def test_rung_a_on_deg_prefix_text_invents_nothing():
    s = SourceText.from_raw("SYN-S163-C", "Preheat oven to 350degF.\nBake the dough for 20 minutes at 180degC.")
    rung = RungA()
    res = rung.run(s, rung.config(), schema=D.load_schema())
    report = aud.audit_outputs(s, res.all(), recomputers=rung.recomputers())
    assert report.invented_count == 0, report.invented_by_code
