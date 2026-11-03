"""S156 AI cross-review of the Step 18 engine drafts: regression tests (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c. Each test reproduces one defect found by the AI cross-review
(worker "prv", an AI verdict pending Kush/Parv review; reports/step18/S156_18_ai_review.md).
They were committed RED before the fixes. Synthetic fixtures only (SYNTHETIC_NOT_GOLD);
no ledger row is read or written.
"""
from __future__ import annotations

import json
from fractions import Fraction

import pytest

from culinarystate.extraction.interfaces import (
    EntityCandidate, EventCandidate, EventGraph, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim,
    ValueKind,
)
from culinarystate.state_graph.event_adapter import adapt_event_graph
from culinarystate.state_graph.event_log import (
    Allocation, EngineEvent, EventLog, EventLogError, QuantityTerm, canonical_json, guard_output_path,
)
from culinarystate.state_graph.replay import ISSUE_CODES, replay_events

F = Fraction
CFG = StageConfig("RA_TEST_GRAPH", {}, "INFERRED_RULE")


def _log_line() -> str:
    log = EventLog()
    log.append(EngineEvent("E1", (0, 0), produces=("N1",)))
    return log.to_jsonl().rstrip("\n")


# ---------------------------------------------------------------- R1 adapter copies literal source text
def test_r1_adapter_never_copies_span_literal_attribute_text():
    s = SourceText.from_raw("SYN-18R", "Stir the secret sauce.")
    claim = ValueClaim("style", ValueKind.CATEGORICAL, "secret sauce", span=Span.of(s, 9, 21),
                       trace=Trace(TraceKind.SPAN_LITERAL))
    ident = ValueClaim("label", ValueKind.IDENTIFIER, "Stir", span=Span.of(s, 0, 4),
                       trace=Trace(TraceKind.SPAN_LITERAL))
    g = EventGraph(s.text_id, s.sha256,
                   (EventCandidate("E1", (0, 0), consumes=("N1",), produces=("N2",), attributes=(claim, ident)),),
                   (EntityCandidate("N1", "INGREDIENT_LOT", "INCORPORATED"),
                    EntityCandidate("N2", "INTERMEDIATE", "ACTIVE", ("N1",), "E1")),
                   (), {"N1": "USED"}, CFG.provenance("build_events"))
    a = adapt_event_graph(s, g)
    assert a.invented_count == 0                                   # the literal values are genuine, not invented
    blob = a.log().to_jsonl() + a.replay().to_jsonl()
    assert "secret" not in blob and "Stir" not in blob
    assert {"LITERAL_TEXT_ATTRIBUTE_NOT_COPIED"} <= {i.code for i in a.unknown}


# ---------------------------------------------------------------- R2 from_jsonl drops unknown fields silently
def test_r2_from_jsonl_refuses_fields_outside_the_schema():
    rec = json.loads(_log_line())
    rec["event"]["zz_injected"] = "x"
    with pytest.raises(EventLogError):
        EventLog.from_jsonl(canonical_json(rec) + "\n")
    rec = json.loads(_log_line())
    rec["zz_injected"] = 1
    with pytest.raises(EventLogError):
        EventLog.from_jsonl(canonical_json(rec) + "\n")


# ---------------------------------------------------------------- R3 event ids may be reused within one replay
def test_r3_replay_rejects_a_reused_event_id():
    assert "EVENT_ID_REUSED" in ISSUE_CODES
    r = replay_events([EngineEvent("E1", (0, 0), produces=("N1",)), EngineEvent("E1", (1, 0), produces=("N2",))])
    assert [t.status for t in r.transactions] == ["APPLIED", "REJECTED"]
    assert "EVENT_ID_REUSED" in {i.code for i in r.issues}
    assert r.snapshot.applied == (("E1", 0),)


# ---------------------------------------------------------------- R4 JSONL split on Unicode line separators
@pytest.mark.parametrize("sep", [" ", " ", "\x85"])
def test_r4_jsonl_round_trips_ids_holding_unicode_line_separators(sep):
    log = EventLog()
    log.append(EngineEvent(f"E{sep}1", (0, 0), produces=(f"N{sep}1",)))
    text = log.to_jsonl()
    assert text.count("\n") == 1
    assert EventLog.from_jsonl(text).to_jsonl() == text


# ---------------------------------------------------------------- R5 protected prefixes are case-sensitive
@pytest.mark.parametrize("rel", ["Ledgers/x.jsonl", "DATA/x.jsonl", "Exports/x.jsonl", "annotation/Gold/x.jsonl"])
def test_r5_protected_areas_are_refused_in_any_letter_case(tmp_path, rel):
    with pytest.raises(EventLogError):
        guard_output_path(tmp_path / rel, root=tmp_path)


# ---------------------------------------------------------------- R6 correlated over-allocation is not failed
def test_r6_known_outputs_exceeding_a_correlated_input_fail_even_with_an_unknown_sibling():
    p = EngineEvent("INTRO/p", (-1, 0), produces=("p",), quantities=(QuantityTerm("p", "g", F(100), F(120), "Q1"),))
    s = EngineEvent("S1", (0, 0), consumes=("p",), produces=("a", "b", "c"),
                    allocations=(Allocation("A0", "SPLIT", "MASS", "p", "a", F(9, 10)),
                                 Allocation("A1", "SPLIT", "MASS", "p", "b", None),
                                 Allocation("A2", "SPLIT", "MASS", "p", "c", None)),
                    quantities=(QuantityTerm("b", "g", F(25), F(25), "Q2"),))
    # a = 0.9 p and b = 25 g: a + b exceeds p for every p in [100, 120] (0.1 p <= 12 < 25)
    r = replay_events([p, s])
    assert r.transactions[1].status == "REJECTED" and "MASS_BALANCE_FAIL" in {i.code for i in r.issues}
    ok = EngineEvent("S1", (0, 0), consumes=("p",), produces=("a", "b", "c"),
                     allocations=s.allocations, quantities=(QuantityTerm("b", "g", F(5), F(5), "Q2"),))
    assert replay_events([p, ok]).transactions[1].status == "APPLIED"      # 0.1 p >= 10 > 5: still UNKNOWN only
