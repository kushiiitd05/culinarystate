"""Tests for the S182 similar-recipe index (tools/s182_similar.py). Tiny in-memory corpora only."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("s182_similar", ROOT / "tools/s182_similar.py")
SIM = importlib.util.module_from_spec(_spec)
sys.modules["s182_similar"] = SIM
_spec.loader.exec_module(SIM)

DOCS = [
    {"id": "W1", "family": "WIKIBOOKS", "title": "Scrambled Eggs with Cheese", "text": "egg cheese butter scramble",
     "url": "https://en.wikibooks.org/wiki/Cookbook:Scrambled_Eggs", "steps": "Beat the eggs. Cook in butter for 3 minutes."},
    {"id": "W2", "family": "WIKIBOOKS", "title": "Boiled Carrots", "text": "carrot boil water", "url": "u2", "steps": "Boil."},
    {"id": "F1", "family": "FOODCOM", "title": "Cheese Scrambled Eggs", "text": "", "url": None, "steps": None},
    {"id": "F2", "family": "FOODCOM", "title": "Garlic Cheese Scrambled Eggs", "text": "", "url": None, "steps": None},
    {"id": "B1", "family": "A1_BBC_GOOD_FOOD", "title": "Perfect scrambled eggs", "text": "", "url": None, "steps": None},
    {"id": "G1", "family": "GUTENBERG_SEGMENT", "title": "To Scramble Eggs", "text": "", "url": None, "steps": None},
]


def index():
    return SIM.SimilarIndex.from_docs(DOCS, min_df=1)


def test_search_ranks_the_closest_public_recipe_first():
    r = index().search("crack the eggs, add cheese and butter, scramble", ["egg", "cheese"])
    assert r["shown"][0]["id"] == "W1"
    assert r["shown"][0]["licence"].startswith("CC BY-SA")


def test_local_only_families_are_counted_never_shown():
    r = index().search("scrambled eggs", ["egg"])
    shown_families = {s["family"] for s in r["shown"]}
    assert shown_families <= {"WIKIBOOKS", "GUTENBERG_SEGMENT"}
    assert r["counts"]["FOODCOM"] == 2 and r["counts"]["A1_BBC_GOOD_FOOD"] == 1
    assert all("title" not in h for h in r["hidden"])


def test_gutenberg_title_is_shown_without_steps():
    r = index().search("to scramble eggs", ["egg"])
    g = next(s for s in r["shown"] if s["family"] == "GUTENBERG_SEGMENT")
    assert g["steps_available"] is False


def test_best_public_with_steps_is_wikibooks():
    r = index().search("scrambled eggs cheese", ["egg", "cheese"])
    assert index().best_public_steps(r)["id"] == "W1"


def test_unrelated_query_matches_nothing():
    r = index().search("zzzz qqqq", [])
    assert r["shown"] == [] and sum(r["counts"].values()) == 0


def test_policy_covers_every_family_and_defaults_to_count_only():
    assert SIM.policy("WIKIBOOKS") == "SHOW_AND_SEND"
    assert SIM.policy("GUTENBERG_SEGMENT") == "SHOW_TITLE"
    assert SIM.policy("FOODCOM") == "COUNT_ONLY"
    assert SIM.policy("SOMETHING_NEW") == "COUNT_ONLY"


def test_match_must_contain_a_query_food_and_titles_are_deduped():
    docs = DOCS + [{"id": "G2", "family": "GUTENBERG_SEGMENT", "title": "To Boil", "text": "", "url": None, "steps": None},
                   {"id": "G3", "family": "GUTENBERG_SEGMENT", "title": "To Scramble Eggs", "text": "", "url": None, "steps": None}]
    r = SIM.SimilarIndex.from_docs(docs, min_df=1).search("boil the carrots in water", ["carrot"], ["boil"])
    titles = [s["title"] for s in r["shown"]]
    assert "To Boil" not in titles
    r2 = SIM.SimilarIndex.from_docs(docs, min_df=1).search("scramble eggs", ["egg"], ["scramble"])
    assert [s["title"] for s in r2["shown"]].count("To Scramble Eggs") == 1


def test_reference_searches_all_wikibooks_not_only_shown():
    docs = [{"id": f"G{i}", "family": "GUTENBERG_SEGMENT", "title": f"Carrot dish {i}", "text": "", "url": None,
             "steps": None} for i in range(10)]
    docs.append({"id": "W9", "family": "WIKIBOOKS", "title": "Glazed Carrots", "text": "carrot butter", "url": "u",
                 "steps": "Boil the carrots for 8 minutes."})
    idx = SIM.SimilarIndex.from_docs(docs, min_df=1)
    r = idx.search("boil carrots", ["carrot"], ["boil"])
    assert idx.best_public_steps(r)["id"] == "W9"


def test_shown_list_includes_wikibooks_even_when_outranked():
    docs = [{"id": f"G{i}", "family": "GUTENBERG_SEGMENT", "title": "Potatoes", "text": "", "url": None, "steps": None}
            for i in range(3)] + [{"id": f"G{i}x", "family": "GUTENBERG_SEGMENT", "title": f"To Boil Potatoes {i}",
                                   "text": "", "url": None, "steps": None} for i in range(5)]
    docs.append({"id": "W1", "family": "WIKIBOOKS", "title": "Roast Potatoes with Rosemary and Garlic", "text": "potato",
                 "url": "u", "steps": "Roast the potatoes for 40 minutes."})
    r = SIM.SimilarIndex.from_docs(docs, min_df=1).search("", ["potato"], ["roast"])
    assert r["shown"][0]["id"] == "W1"
