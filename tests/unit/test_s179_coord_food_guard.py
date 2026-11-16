"""D-116 prerequisite: coordinated-list food words stay ingredients, not verbs (guard off by default = frozen behaviour)."""
from __future__ import annotations

import pytest

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity.rc2_dryrun import load_schema

SCHEMA = load_schema()


def _labels(rung, text):
    ms = rung.extract_mentions(SourceText.from_raw("T", text), rung.config())
    return [(" ".join(m.span.texts).lower(), m.label) for m in ms.mentions]


@pytest.mark.parametrize("text,word", [
    ("Mix the tomatoes, salt and vinegar.", "salt"),
    ("Mix the tomatoes, salt, oil and vinegar.", "oil"),
    ("Mix the tomatoes, salt, oil and vinegar.", "salt"),
])
def test_guard_keeps_coordinated_food_as_ingredient(text, word):
    assert (word, "ACTION") in _labels(RungA(), text)                       # frozen behaviour (the bug)
    got = _labels(RungA(coord_food_guard=True), text)
    assert (word, "ACTION") not in got and (word, "FOOD_MENTION") in got


@pytest.mark.parametrize("text,word", [
    ("Drain the pasta, salt it and serve.", "salt"),
    ("Boil the potatoes, then salt them well.", "salt"),
    ("Chop the onion and fry it.", "fry"),
])
def test_guard_leaves_real_verbs(text, word):
    assert (word, "ACTION") in _labels(RungA(coord_food_guard=True), text)


def test_guard_records_a_flag():
    rung = RungA(coord_food_guard=True)
    ms = rung.extract_mentions(SourceText.from_raw("T", "Mix the tomatoes, salt and vinegar."), rung.config())
    assert "COORD_FOOD_GUARD" in ms.diagnostics


@pytest.mark.parametrize("text,word", [
    ("Add the onion, garlic and fry until brown.", "fry"),
    ("Mix the flour, sugar and sprinkle on top.", "sprinkle"),
])
def test_guard_v2_blocklist_keeps_verbs(text, word):
    assert (word, "FOOD_MENTION") not in _labels(RungA(coord_food_guard=True), text)
