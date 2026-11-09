"""S171 / D-075 M4: SSOT §39 query router (intent -> branch). Rule-based, explicit UNKNOWN, no guessing."""
from __future__ import annotations

import pytest

from culinarystate.decision import query_router as QR


@pytest.mark.parametrize("q,branch", [
    ("How much vitamin C does boiling broccoli destroy?", "TRANSFORMATION"),
    ("Will steaming instead of boiling keep more vitamin C in spinach?", "TRANSFORMATION"),
    ("Why did my sauce split after I added the lemon?", "TRANSFORMATION"),
    ("What is the vitamin C content of raw red pepper?", "METADATA"),
    ("How many calories are in 100 g of rice?", "METADATA"),
    ("What can I use instead of buttermilk?", "RELATIONSHIP"),
    ("Which ingredients pair well with saffron?", "RELATIONSHIP"),
    ("Find me a recipe like a creamy mushroom risotto", "SEMANTIC"),
    ("Show me recipes similar to chicken tikka masala", "SEMANTIC"),
    ("Is this onion caramelised enough? Here is a photo", "MULTIMODAL"),
    ("Listen to this sizzle, is the oil hot enough?", "MULTIMODAL"),
])
def test_branch_per_ssot_39(q, branch):
    assert QR.route(q)["branch"] == branch


def test_unknown_when_no_cue_and_empty_is_malformed():
    assert QR.route("hello there")["branch"] == "UNKNOWN"
    assert QR.route("   ")["branch"] == "MALFORMED"


def test_multimodal_is_explicitly_unsupported_not_answered():
    out = QR.route("Here is a photo of my bread, is it proofed?")
    assert out["branch"] == "MULTIMODAL" and out["supported"] is False and out["action"] == "ABSTAIN_UNSUPPORTED"


def test_transformation_carries_gate_and_intent_and_needs_process_model():
    out = QR.route("Will steaming instead of boiling keep more vitamin C in spinach?")
    assert out["needs_process_model"] is True and out["relevance"]["relevant"] is True
    assert out["intent"] == "COMPARE" and out["supported"] is True and out["action"] == "PROCESS_MODEL_PLUS_EVIDENCE"


def test_metadata_does_not_trigger_process_model():
    out = QR.route("What is the vitamin C content of raw red pepper?")
    assert out["needs_process_model"] is False and out["action"] == "STRUCTURED_LOOKUP"


def test_route_is_deterministic_and_whitespace_invariant():
    a = QR.route("How much vitamin C does boiling broccoli destroy?")
    b = QR.route("  How much   vitamin C does boiling\nbroccoli destroy?  ")
    assert {k: v for k, v in a.items() if k != "raw"} == {k: v for k, v in b.items() if k != "raw"}
