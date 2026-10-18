import pytest

from culinarystate.decision.relevance import intent, relevance_gate

LOW = ["Move the chopped onions into a bowl.", "What is the next instruction?", "How many teaspoons were used?"]
HIGH = ["Can I boil this instead of frying it?", "Why do I need to brown the onions?",
        "I accidentally boiled it; how can I recover?", "Will microwaving produce the same texture?",
        "What changes if I roast instead of steam?"]


@pytest.mark.parametrize("q", LOW)
def test_ssot_low_relevance_examples(q):
    assert relevance_gate(q)["relevant"] is False


@pytest.mark.parametrize("q", HIGH)
def test_ssot_high_relevance_examples(q):
    assert relevance_gate(q)["relevant"] is True


def test_unknown_is_explicit_and_malformed_rejected():
    g = relevance_gate("Tell me about paneer")
    assert g["relevant"] is None and g["reason"] == "NO_CUE"
    assert relevance_gate("   ")["reason"] == "MALFORMED_EMPTY"


def test_intent():
    assert intent("I accidentally boiled it; how can I recover?") == "RECOVER"
    assert intent("Why did my sauce split?") == "DIAGNOSE"
    assert intent("What changes if I roast instead of steam?") == "COMPARE"
    assert intent("How should I cook spinach to keep vitamin C?") == "RECOMMEND"
    assert intent("How much vitamin C does boiled broccoli keep?") == "ANSWER"


@pytest.mark.parametrize("q", ["Does roasting or braising keep more thiamin in beef?", "Is steaming or boiling better for folate?",
                               "Which keeps less vitamin C, frying or baking?"])
def test_or_with_comparative_is_compare(q):
    assert intent(q) == "COMPARE"


def test_plain_or_without_comparative_is_not_compare():
    assert intent("Can I use butter or oil to fry onions?") != "COMPARE"
