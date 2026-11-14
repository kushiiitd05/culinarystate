"""S180 freeze step 5: lightweight claim verifier and deterministic template fallback.

The verifier runs *after* LLM generation and checks the text against the Claim Packet. If
verification fails the answer is replaced by a deterministic template, never permitted through.
The verifier reads the packet; it never consults the model and never repairs the text.
"""
from __future__ import annotations

import pytest

from culinarystate.composition import claim_packet as CP
from culinarystate.composition import claim_verifier as CV
from culinarystate.composition.state_full import StateBuilder

TOMATO_A = "Boil the tomatoes in water for 20 minutes."
TOMATO_D = "Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes."


@pytest.fixture(scope="module")
def B():
    return StateBuilder()


@pytest.fixture(scope="module")
def direct(B):
    s = next(x for x in B.build(TOMATO_A) if x["food"] == "tomato" and x["step"] == 1)
    return CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")


@pytest.fixture(scope="module")
def unknown(B):
    s = next(x for x in B.build(TOMATO_D) if x["food"] == "tomato" and x["step"] == 2)
    return CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")


# --- numbers must come from the evidence ------------------------------------------

def test_cited_number_from_the_evidence_passes(direct):
    r = CV.verify("About 95.0% of the vitamin C remains [EVD-002765].", direct)
    assert r.ok, r.violations


def test_invented_number_fails(direct):
    r = CV.verify("About 73.2% of the vitamin C remains [EVD-002765].", direct)
    assert not r.ok
    assert "NUMBER_NOT_IN_EVIDENCE" in r.codes


def test_number_exceeding_reported_precision_fails(direct):
    """The source reports 95.0, one decimal; 95.04 claims precision the source does not have."""
    r = CV.verify("Retention is 95.04% [EVD-002765].", direct)
    assert not r.ok
    assert "PRECISION_EXCEEDS_SOURCE" in r.codes


def test_numeric_claim_without_an_evidence_id_fails(direct):
    r = CV.verify("About 95.0% of the vitamin C remains.", direct)
    assert not r.ok
    assert "NUMBER_WITHOUT_EVIDENCE_ID" in r.codes


def test_step_and_duration_from_the_action_are_not_treated_as_claims(direct):
    """The recipe's own 20 minutes is context, not an evidence number."""
    r = CV.verify("After boiling for 20 minutes, 95.0% remains [EVD-002765].", direct)
    assert r.ok, r.violations


# --- forbidden claims -------------------------------------------------------------

def test_transferring_a_near_evidence_number_fails(unknown):
    r = CV.verify("Vitamin C retention is about 95.0% [EVD-002765].", unknown)
    assert not r.ok
    assert "FORBIDDEN_NUMERIC_CLAIM" in r.codes


def test_naming_near_evidence_without_its_number_passes(unknown):
    r = CV.verify(
        "Retention is not known here. A nearby row [EVD-002765] measured plain boiled tomato, "
        "but its number cannot be transferred because the salt and acid context is unconfirmed.",
        unknown,
    )
    assert r.ok, r.violations


def test_stating_unknown_as_zero_fails(unknown):
    r = CV.verify("There is no vitamin C left, so retention is 0.", unknown)
    assert not r.ok
    assert r.codes & {"UNKNOWN_STATED_AS_ZERO", "FORBIDDEN_NUMERIC_CLAIM"}


def test_claiming_a_better_route_fails(unknown):
    r = CV.verify("This is a DIRECT measurement for this exact context.", unknown)
    assert not r.ok
    assert "ROUTE_UPGRADED" in r.codes


# --- required caveats -------------------------------------------------------------

def test_missing_a_required_caveat_fails(unknown):
    assert unknown["required_caveats"], "fixture must have caveats to test"
    r = CV.verify("Retention is not known here.", unknown)
    assert not r.ok
    assert "REQUIRED_CAVEAT_MISSING" in r.codes


def test_abstention_that_states_the_reason_passes(unknown):
    r = CV.verify(
        "Retention is not known for this step. The salt and acid context is unconfirmed and the pH "
        "is unknown, and the nearby row [EVD-002765] cannot have its number transferred.",
        unknown,
    )
    assert r.ok, r.violations


# --- template fallback ------------------------------------------------------------

def test_template_is_produced_for_an_unknown_route(unknown):
    t = CV.template_answer(unknown)
    assert t
    assert "not known" in t.lower()


def test_template_always_verifies_against_its_own_packet(direct, unknown):
    for p in (direct, unknown):
        t = CV.template_answer(p)
        r = CV.verify(t, p)
        assert r.ok, f"template must pass its own verifier: {r.violations}"


def test_template_for_unknown_route_carries_no_retention_number(unknown):
    t = CV.template_answer(unknown)
    assert "95" not in t


def test_template_for_direct_route_cites_its_evidence(direct):
    t = CV.template_answer(direct)
    assert "EVD-002765" in t


def test_answer_or_template_falls_back_on_a_bad_answer(unknown):
    text, used_template, report = CV.answer_or_template("Retention is 95.0% [EVD-002765].", unknown)
    assert used_template
    assert not report.ok
    assert text == CV.template_answer(unknown)


def test_answer_or_template_keeps_a_good_answer(direct):
    good = "About 95.0% of the vitamin C remains [EVD-002765]."
    text, used_template, report = CV.answer_or_template(good, direct)
    assert not used_template and report.ok
    assert text == good


def test_verifier_never_mutates_the_packet(direct):
    before = repr(direct)
    CV.verify("About 95.0% of the vitamin C remains [EVD-002765].", direct)
    CV.template_answer(direct)
    assert repr(direct) == before
