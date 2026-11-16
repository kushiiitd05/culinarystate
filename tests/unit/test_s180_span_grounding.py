"""S180: a span must ground the value, not merely be in range.

The 15 Nov directive requires that "every proposal must carry source-span grounding", and the step-7
pre-registration claims the gate enforces it. It did not. The gate checked only
``0 <= start < end <= len(raw)``, so **any** in-range offsets passed.

The ksh+prv evidence pass found the consequence: **0 of 14 accepted proposals had a span that
supported its value**, with distances of 43 to 530 characters to the real evidence. In one case the
nearest coordinator to the span was a different choice entirely ("tea-towel or paper towel") while
the licensed one was 317 characters away.

``alternative_group`` is the only proposable field and it is licensed only by
``VNEXT_ALTERNATIVE_SKIPPED``, which fires on coordinated text. So the span must contain a
coordinator. ``or until`` is excluded: it is an endpoint condition, not a branch, and it is very
common in recipe prose.
"""
from __future__ import annotations

from culinarystate.composition import layer1_proposer as LP
from culinarystate.extraction.interfaces import (
    EventCandidate, EventGraph, SourceText, StageConfig,
)

RAW = "Add the lemon juice or the vinegar, then simmer for 20 minutes or until thickened."
CFG = StageConfig(rung_id="A", params={"v": 0}, claim_route="INFERRED_RULE",
                  annotated_labels=frozenset({"FOOD_MENTION"}))


def _src(raw):
    return SourceText.from_raw("SYN-SPAN", raw)


def ev(eid, order=(0, 0)):
    return EventCandidate(eid, order)


def graph(events, raw=RAW):
    src = _src(raw)
    return EventGraph(src.text_id, src.sha256, tuple(events), (), (), {},
                      CFG.provenance("build_events"))


def prop(**kw):
    base = dict(trigger="VNEXT_ALTERNATIVE_SKIPPED", field="alternative_group",
                value="lemon_juice_or_vinegar", event_id="E1",
                span_start=4, span_end=34, rationale='"or" binds a choice')
    base.update(kw)
    return LP.Proposal(**base)


def test_grounding_code_is_declared():
    assert "SPAN_DOES_NOT_GROUND_VALUE" in LP.REJECTION_CODES


def test_span_containing_a_coordinator_is_accepted():
    d = LP.review([prop()], graph([ev("E1")]), triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert not d.rejected, d.rejected


def test_in_range_span_without_a_coordinator_is_refused():
    """This is the defect: 'then simmer' is a valid range and grounds nothing."""
    d = LP.review([prop(span_start=36, span_end=47)], graph([ev("E1")]),
                  triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "SPAN_DOES_NOT_GROUND_VALUE"


def test_or_until_is_an_endpoint_not_a_branch():
    """'simmer for 20 minutes or until thickened' is a stopping condition."""
    i = RAW.index("20 minutes or until")
    d = LP.review([prop(span_start=i, span_end=i + len("20 minutes or until thickened"))],
                  graph([ev("E1")]), triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "SPAN_DOES_NOT_GROUND_VALUE"


def test_either_counts_as_a_coordinator():
    raw = "Either proceed to the cooking stage, or freeze the dumplings."
    d = LP.review([prop(value="cooking_or_freezing", span_start=0, span_end=47)],
                  graph([ev("E1")], raw), triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=raw)
    assert not d.rejected, d.rejected


def test_a_bare_or_inside_a_word_does_not_count():
    """'for', 'colour', 'coriander' all contain 'or'. Only the standalone token grounds."""
    raw = "Add coriander for colour and flavour before serving the dish."
    d = LP.review([prop(span_start=0, span_end=40)], graph([ev("E1")], raw),
                  triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=raw)
    assert d.rejected and d.rejected[0][1] == "SPAN_DOES_NOT_GROUND_VALUE"


def test_range_check_still_runs_first():
    """An out-of-range span is still SPAN_OUT_OF_RANGE, not a grounding failure."""
    d = LP.review([prop(span_end=9999)], graph([ev("E1")]),
                  triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "SPAN_OUT_OF_RANGE"


def test_the_fourteen_recorded_proposals_would_now_all_be_refused():
    """The evidence pass judged 0 of 14 spans to support their value. The gate must agree."""
    import csv, json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    packet = root / "data/interim/s180_hardcases/hardcases_60_s180-layer1-hardcases-2026-11-15.jsonl"
    if not packet.exists():
        import pytest
        pytest.skip("sealed packet is git-ignored and absent")
    raws = {str(json.loads(l)["pageid"]): json.loads(l)["raw"] for l in packet.open(encoding="utf-8")}
    rows = list(csv.DictReader(
        (root / "reports/s180/alternatives_verification_2026-11-15/alternatives_to_verify.csv")
        .open(encoding="utf-8")))
    assert rows
    for r in rows:
        a, b = (int(x) for x in r["span"].split("-"))
        assert not LP.span_grounds_value(raws[r["pageid"]], a, b), \
            f"{r['verify_id']} span was judged ungrounded by review but the gate accepts it"
