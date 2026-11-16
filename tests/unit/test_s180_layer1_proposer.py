"""S180 freeze step 6: Layer-1 LLM structured proposer, gated by ambiguity triggers.

Rules and frozen models run first. The LLM proposes structured event/state changes only when an
ambiguity trigger fires, every proposal carries source-span grounding, and the validator decides
acceptance. The proposer never writes state.

No network here: the client is injected, so the deterministic gate is tested offline. The hosted
comparison is step 7.
"""
from __future__ import annotations

import pytest

from culinarystate.composition import layer1_proposer as L1
from culinarystate.extraction.interfaces import (
    EntityCandidate, EventCandidate, EventGraph, SourceText, StageConfig,
)

RAW = "Add the lemon juice or the vinegar, then simmer the sauce."
CFG = StageConfig(rung_id="A", params={"v": 0}, claim_route="INFERRED_RULE",
                  annotated_labels=frozenset({"FOOD_MENTION"}))
SRC = SourceText.from_raw("SYN-L1", RAW)


def graph(events=(), entities=(), lots=None):
    return EventGraph(SRC.text_id, SRC.sha256, tuple(events), tuple(entities), (),
                      {} if lots is None else lots, CFG.provenance("build_events"))


def ev(eid, order, **kw):
    return EventCandidate(eid, order, **kw)


def ent(nid, etype="INTERMEDIATE", lifecycle="ACTIVE", parents=(), by=None):
    return EntityCandidate(nid, etype, lifecycle, tuple(parents), by)


def prop(**kw):
    base = dict(trigger="VNEXT_ALTERNATIVE_SKIPPED", field="alternative_group", value="ALT-1",
                event_id="E1", span_start=4, span_end=34, rationale="\"or\" binds a choice")
# span 4:34 is "the lemon juice or the vinegar". It used to end at 21, which cut "or" in half, so the
# fixture's own span grounded nothing - caught by the S180 grounding check, not by the old range test.
    base.update(kw)
    return L1.Proposal(**base)


# --- triggers are a closed set of signals that already exist ----------------------

def test_trigger_vocabulary_is_closed_and_non_empty():
    assert L1.TRIGGERS
    assert "VNEXT_ALTERNATIVE_SKIPPED" in L1.TRIGGERS
    assert "AMBIGUOUS_ANTECEDENT" in L1.TRIGGERS


def test_no_trigger_means_no_proposal_is_even_requested():
    assert L1.triggers_for(flags=(), lot_accounting={}) == ()


def test_known_flag_fires_a_trigger():
    assert L1.triggers_for(flags=("VNEXT_MIXTURE_COREF",), lot_accounting={}) == ("VNEXT_MIXTURE_COREF",)


def test_unknown_flag_is_ignored_not_escalated():
    assert L1.triggers_for(flags=("SOMETHING_ELSE",), lot_accounting={}) == ()


def test_unresolved_lot_status_fires_a_trigger():
    assert "UNRESOLVED_LOT" in L1.triggers_for(flags=(), lot_accounting={"N1": "UNRESOLVED"})


def test_triggers_are_deduplicated_and_ordered():
    got = L1.triggers_for(flags=("VNEXT_FAT_STAYS", "VNEXT_FAT_STAYS", "AMBIGUOUS_ACTION"),
                          lot_accounting={})
    assert got == tuple(sorted(set(got)))


# --- a proposal is a typed, span-grounded object ----------------------------------

def test_proposal_requires_a_span():
    with pytest.raises(L1.ProposalError):
        prop(span_start=None, span_end=None)


def test_proposal_rejects_an_inverted_or_empty_span():
    for s, e in ((21, 4), (4, 4)):
        with pytest.raises(L1.ProposalError):
            prop(span_start=s, span_end=e)


def test_proposal_claim_route_records_model_origin():
    assert prop().claim_route == "LLM_PROPOSED"


def test_proposal_is_immutable():
    p = prop()
    with pytest.raises(Exception):
        p.value = "ALT-2"


# --- review: the validator decides, not the model ---------------------------------

def test_proposal_with_an_untriggered_reason_is_rejected():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(trigger="NOT_A_TRIGGER")], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "TRIGGER_NOT_IN_VOCABULARY"


def test_proposal_whose_trigger_did_not_fire_is_rejected():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(trigger="VNEXT_FAT_STAYS")], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "TRIGGER_DID_NOT_FIRE"


def test_proposal_for_an_unknown_event_is_rejected():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(event_id="E9")], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "EVENT_NOT_IN_GRAPH"


def test_proposal_outside_the_allowed_fields_is_rejected():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(field="produces", value="N9")], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "FIELD_NOT_PROPOSABLE"


def test_numeric_proposals_are_always_rejected():
    """No numeric chemistry from the model, per the freeze."""
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(field="condition_profile_id", value="95.0")], g,
                  triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "NUMERIC_VALUE_NOT_ALLOWED"


def test_span_must_match_the_raw_text():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(span_end=9999)], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "SPAN_OUT_OF_RANGE"


def test_review_requires_raw_so_spans_are_always_checked():
    g = graph([ev("E1", (0, 0))])
    with pytest.raises(TypeError):
        L1.review([prop()], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",))


def test_a_clean_proposal_is_accepted():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop()], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert not d.rejected, d.rejected
    assert len(d.accepted) == 1


def test_a_proposal_that_would_break_an_invariant_is_rejected():
    """Grouping two committed events as alternatives is a conjunction error, so V4 refuses it."""
    g = graph([ev("E1", (0, 0), produces=("N1",), alternative_group="ALT-1"),
               ev("E2", (0, 1), produces=("N2",))],
              [ent("N1", by="E1"), ent("N2", by="E2")])
    d = L1.review([prop(event_id="E2")], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "WOULD_VIOLATE_INVARIANT"


def test_review_never_mutates_the_input_graph():
    g = graph([ev("E1", (0, 0))])
    before = repr(g)
    L1.review([prop()], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert repr(g) == before


def test_apply_returns_a_new_graph_leaving_the_original_alone():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop()], g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    g2 = L1.apply(d.accepted, g)
    assert g2 is not g
    assert g.events[0].alternative_group is None
    assert g2.events[0].alternative_group == "ALT-1"


# --- the client is injected; nothing runs without a trigger -----------------------

class FakeClient:
    def __init__(self, payload):
        self.payload, self.calls = payload, 0

    def propose(self, *, raw, triggers, graph):
        self.calls += 1
        return self.payload


def test_client_is_not_called_when_no_trigger_fired():
    c = FakeClient([])
    out = L1.run(raw=RAW, graph=graph([ev("E1", (0, 0))]), flags=(), lot_accounting={}, client=c)
    assert c.calls == 0
    assert out.accepted == () and out.rejected == ()


def test_client_is_called_once_when_a_trigger_fires():
    c = FakeClient([prop()])
    L1.run(raw=RAW, graph=graph([ev("E1", (0, 0))]),
           flags=("VNEXT_ALTERNATIVE_SKIPPED",), lot_accounting={}, client=c)
    assert c.calls == 1


def test_malformed_client_output_is_rejected_not_raised():
    c = FakeClient([{"not": "a proposal"}])
    out = L1.run(raw=RAW, graph=graph([ev("E1", (0, 0))]),
                 flags=("VNEXT_ALTERNATIVE_SKIPPED",), lot_accounting={}, client=c)
    assert out.rejected and out.rejected[0][1] == "MALFORMED_PROPOSAL"
    assert out.accepted == ()


# --- a trigger only licenses the field it is actually about -----------------------

def test_trigger_field_licensing_is_declared_for_every_trigger():
    assert set(L1.TRIGGER_FIELDS) == set(L1.TRIGGERS)
    for fields in L1.TRIGGER_FIELDS.values():
        assert set(fields) <= set(L1.PROPOSABLE_FIELDS)


def test_coref_trigger_may_not_bind_an_alternative_group():
    """A "the sauce" coreference answer is not an alternatives binding."""
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(trigger="VNEXT_MIXTURE_COREF", field="alternative_group", value="filling")],
                  g, triggers=("VNEXT_MIXTURE_COREF",), raw=RAW)
    assert d.rejected and d.rejected[0][1] == "FIELD_NOT_LICENSED_BY_TRIGGER"


def test_alternative_trigger_may_bind_an_alternative_group():
    g = graph([ev("E1", (0, 0))])
    d = L1.review([prop(trigger="VNEXT_ALTERNATIVE_SKIPPED", field="alternative_group", value="ALT-1")],
                  g, triggers=("VNEXT_ALTERNATIVE_SKIPPED",), raw=RAW)
    assert not d.rejected, d.rejected


def test_fat_stays_trigger_licenses_nothing_at_all():
    """P2: the rule has already merged fat into the lot before the flag is raised, so there is no
    open question. Whether frying fat stays with the food is a mass-transfer question the text does
    not state; it belongs to the simulator, not to Layer-1."""
    g = graph([ev("E1", (0, 0))])
    bad = L1.review([prop(trigger="VNEXT_FAT_STAYS", field="alternative_group", value="X")],
                    g, triggers=("VNEXT_FAT_STAYS",), raw=RAW)
    assert bad.rejected and bad.rejected[0][1] == "FIELD_NOT_LICENSED_BY_TRIGGER"
    ref = L1.review([prop(trigger="VNEXT_FAT_STAYS", field="condition_profile_id", value="fat_retained")],
                    g, triggers=("VNEXT_FAT_STAYS",), raw=RAW)
    assert ref.rejected and ref.rejected[0][1] == "FIELD_REQUIRES_EXISTING_REFERENT"
