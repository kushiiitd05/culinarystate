"""S176 / L-ROUTER: the question router recognises inflected and compound process words ("fried" was missed)."""
from __future__ import annotations

import re

import pytest

from culinarystate.decision import query_router as QR
from culinarystate.decision import relevance as RV

# every question names a nutrient or quality target, so a process cue alone decides TRANSFORMATION
PROCESS_QS = [
    "How much vitamin C do fried potatoes keep?",              # the S176 miss: "fried"
    "What happens to vitamin C in deep-fried potatoes?",
    "Do pan-fried peppers keep their vitamin C?",
    "How much folate is left in stir-fried spinach?",
    "Do air fried potatoes keep vitamin C?",
    "Does shallow fried broccoli lose vitamin C?",
    "Do sautéed onions keep their colour?",
    "Does seared steak lose protein?",
    "Do charred peppers keep their vitamin C?",
    "Does broiled salmon keep its protein?",
    "How much vitamin C do barbecued peppers keep?",
    "Does BBQ change the colour of corn?",
    "Do scrambled eggs lose protein?",
    "How much folate do parboiled potatoes lose?",
    "Does caramelised onion keep vitamin C?",
    "Does caramelized sugar change colour?",
    "Is vitamin C kept when soup is reheated?",
    "How much vitamin C does frozen broccoli keep after thawing?",
    "Does freezing change the texture of berries?",
    "Do fermented vegetables keep their vitamin C?",
    "Do pickled beets keep their colour?",
    "How much vitamin C is left in dried tomatoes?",
    "Does canning reduce the vitamin C in tomatoes?",
    "Does sous vide keep the texture of salmon?",
    "Do roasted peppers keep vitamin C?",                      # the existing lexicon still works
    "Is steamed broccoli better than boiled for vitamin C?",
]
NOT_PROCESS_QS = [
    "What is vitamin C good for?",                             # target, no process
    "Is the search result about protein relevant?",            # "search" is not "sear"
    "Is charcoal a good colour for my kitchen?",               # "charcoal" is not "charred"
    "Does smoking affect vitamin C levels?",                   # smoking (cigarettes): deliberately not a process word
    "How many vitamins are in french fries?",                  # "fries" is a noun
    "hello there",
]


@pytest.mark.parametrize("q", PROCESS_QS)
def test_process_word_routes_to_transformation(q):
    r = QR.route(q)
    assert r["branch"] == "TRANSFORMATION", (q, r["branch"], r["reason"])


@pytest.mark.parametrize("q", NOT_PROCESS_QS)
def test_non_process_words_do_not_route_to_transformation_by_process_cue(q):
    assert QR.route(q)["reason"] != "PROCESS_AND_TARGET_OR_EFFECT"


def test_fried_was_unknown_before_and_is_a_relevance_cue_now():
    assert QR.route("How much vitamin C do fried potatoes keep?")["reason"] == "PROCESS_AND_TARGET_OR_EFFECT"
    assert RV.relevance_gate("Why do I need to sear the meat first?")["relevant"] is True
    assert re.search(rf"\b{RV._P}", "pan-fried") and re.search(rf"\b{RV._P}", "deep-fried")


def test_fold_accents_only_removes_marks():
    assert RV.fold_accents("sautéed crème brûlée") == "sauteed creme brulee"
    assert RV.fold_accents("plain text 100 C") == "plain text 100 C"


def test_existing_cues_are_unchanged():
    assert QR.route("What can I use instead of buttermilk?")["branch"] == "RELATIONSHIP"
    assert QR.route("Is this onion caramelised enough? Here is a photo")["branch"] == "MULTIMODAL"
    assert RV.intent("I accidentally boiled it; how can I recover?") == "RECOVER"


def test_slot_parser_lexicon_is_ascii_so_folding_is_what_makes_saute_parse():
    from culinarystate.state_graph.rule_compiler import step_processes
    q = "How much folate is left in sautéed spinach?"
    assert [n for _, n in step_processes(q)] == []                              # the S176 miss
    assert [n for _, n in step_processes(RV.fold_accents(q))] == ["saute"]      # pipeline.parse_query folds first
    assert [n for _, n in step_processes("fried potatoes")] == ["fry"]           # "fried" was already a slot-parser verb
