"""S171 / D-075 M4: front door = §39 router -> branch handler; unbuilt branches abstain explicitly. No ledgers."""
from __future__ import annotations

import pytest

from culinarystate.decision import front_door as FD


def _handlers(calls):
    def transformation(q, recipe_text=None):
        calls.append(("T", q, recipe_text))
        return {"answer": "cited text [EVD-1]", "mode": "ANSWER", "cited": ["EVD-1"]}

    def relationship(q):
        calls.append(("R", q))
        return {"answer": "graph text", "mode": "ANSWER", "cited": []}
    return {"TRANSFORMATION": transformation, "RELATIONSHIP": relationship}


def test_transformation_goes_to_process_handler_with_recipe_text():
    calls = []
    out = FD.respond("Does boiling spinach destroy vitamin C?", handlers=_handlers(calls), recipe_text="Boil it.")
    assert out["route"]["branch"] == "TRANSFORMATION" and out["mode"] == "ANSWER"
    assert calls == [("T", "Does boiling spinach destroy vitamin C?", "Boil it.")]


@pytest.mark.parametrize("q,branch,mode", [
    ("Here is a photo, is my bread proofed?", "MULTIMODAL", "ABSTAIN_UNSUPPORTED"),
    ("Find me a recipe like mushroom risotto", "SEMANTIC", "ABSTAIN_NOT_BUILT"),
    ("What is the vitamin C content of raw red pepper?", "METADATA", "ABSTAIN_NOT_BUILT"),
    ("hello there", "UNKNOWN", "ASK"),
    ("", "MALFORMED", "ASK"),
])
def test_unbuilt_or_unsupported_branches_never_answer(q, branch, mode):
    calls = []
    out = FD.respond(q, handlers=_handlers(calls))
    assert out["route"]["branch"] == branch and out["mode"] == mode and out["cited"] == [] and calls == []
    assert out["answer"]  # always says why, never empty


def test_handler_exception_becomes_abstention_with_class_name_only():
    def boom(q, recipe_text=None):
        raise KeyError("secret detail")
    out = FD.respond("Does boiling spinach destroy vitamin C?", handlers={"TRANSFORMATION": boom})
    assert out["mode"] == "ABSTAIN_ERROR" and out["error_class"] == "KeyError" and "secret" not in out["answer"]


def test_output_is_labelled_demo_and_non_citable():
    out = FD.respond("hello there", handlers={})
    assert out["citable"] is False and "DEMO_ONLY" in out["labels"]
