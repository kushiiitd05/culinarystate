"""S176 / L-ROUTER: food-safety questions are refused with a referral to official guidance, never answered.

Rule baseline on a labelled example set (recall-oriented; not a calibrated classifier). No ledgers, no numbers.
"""
from __future__ import annotations

import re

import pytest

from culinarystate.decision import front_door as FD
from culinarystate.decision import policy as PO
from culinarystate.decision import query_router as QR
from culinarystate.decision import relevance as RV
from culinarystate.decision import safety as SF

SAFETY_QS = [
    "Is chicken safe to eat if it is still pink inside?",
    "What internal temperature should chicken reach?",
    "What is the safe minimum temperature for pork?",
    "How do I know when the chicken is done?",
    "Is the steak done yet?",
    "Can I eat raw eggs?",
    "Is it okay to eat undercooked chicken?",
    "How long can cooked rice sit out on the counter?",
    "How long can cooked chicken stay in the fridge?",
    "How long does leftover soup last?",
    "Can I refreeze thawed chicken?",
    "Will this give me food poisoning?",
    "Does boiling kill salmonella in eggs?",
    "Does microwaving kill bacteria?",
    "Is it listeria if the cheese smells off?",
    "Has my milk gone bad? It is past the use by date.",
    "How do I avoid botulism when canning beans?",
    "Is reheating rice twice dangerous?",
    "Is my burger cooked through?",
    "What is the danger zone for food temperature?",
    "Is it unsafe to leave stew out overnight?",
    "What doneness is medium-rare for beef?",
    "Is this photo of chicken safe to eat?",              # safety wins over MULTIMODAL
]
RETENTION_QS = [
    "How much vitamin C does boiled cabbage keep?",
    "How much vitamin C is left when the potatoes are done?",
    "How long can I boil broccoli and still keep the vitamin C?",
    "Does boiling destroy vitamin C in spinach?",
    "Is steaming or boiling better for keeping vitamin C in broccoli?",
    "What can I use instead of ricotta?",
    "Why did my sauce split after I added the lemon?",
    "How much protein does a raw egg have compared with a cooked egg?",
    "Will roasting change the colour of the peppers?",
    "How long does it take to boil potatoes?",
]


def _no_digit(text: str) -> bool:
    return not re.search(r"\d", text)


@pytest.mark.parametrize("q", SAFETY_QS)
def test_safety_questions_are_detected_routed_and_refused(q):
    assert SF.is_safety(q) is True
    route = QR.route(q)
    assert route["branch"] == "SAFETY" and route["supported"] is False and route["needs_process_model"] is False
    assert route["action"] == "ABSTAIN_REFER_OFFICIAL_FOOD_SAFETY" and route["intent"] == "SAFETY"
    called = []

    def boom(*a, **k):
        called.append(a)
        raise AssertionError("no handler may run for a safety question")

    out = FD.respond(q, handlers={"TRANSFORMATION": boom, "RELATIONSHIP": boom}, recipe_text="Boil it.")
    assert out["mode"] == "ABSTAIN_SAFETY" and out["reason"] == "FOOD_SAFETY_REFER_OFFICIAL" and not called
    assert out["cited"] == [] and out["citable"] is False and "NON_CITABLE" in out["labels"]
    assert _no_digit(out["answer"])                                # no number of any kind
    assert "official" in out["answer"] and out["referral"] == list(SF.REFERRAL)


@pytest.mark.parametrize("q", RETENTION_QS)
def test_retention_and_other_questions_are_not_refused_as_safety(q):
    assert SF.is_safety(q) is False
    assert QR.route(q)["branch"] != "SAFETY" and RV.intent(q) != "SAFETY"


def test_strong_cue_beats_a_nutrient_word_but_weak_cue_does_not():
    assert SF.is_safety("Is it safe to eat spinach with vitamin C supplements?")          # strong: safe
    assert not SF.is_safety("How much vitamin C is left when the potatoes are done?")       # weak: done + nutrient
    assert SF.is_safety("Are the potatoes done?")                                           # weak, no nutrient: refuse


def test_policy_refuses_a_safety_question_for_any_caller():
    d = PO.decide("What internal temperature should chicken reach?", {}, {"ingredient": "ING-1", "process": "PROC-1"})
    assert d["mode"] == "ABSTAIN" and d["route"] == "SAFETY" and d["reason"] == SF.REASON and "per_option" not in d


def test_message_and_referral_are_flagged_unverified_in_the_docstring_and_carry_no_number():
    assert _no_digit(SF.MESSAGE) and "SOURCE_UNVERIFIED_AGENT_RECALLED" in SF.__doc__
    assert all(_no_digit(x) for x in SF.REFERRAL)


def test_verbalizer_abstains_with_the_safety_text():
    from culinarystate.generation.verbalize import ABSTAIN_TEXT
    assert ABSTAIN_TEXT[SF.REASON] == SF.MESSAGE
