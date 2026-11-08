"""S173 / M5 H1 rungs (prereg §2, §4): contexts per rung, strict prompts, id-level scoring. Fake embedder, no LLM."""
from __future__ import annotations

import pytest

from culinarystate.evaluation import h1_rungs as H

STEPS = ["Peel and dice the potatoes.", "Boil the potatoes for 20 minutes.", "Chop the parsley.",
         "Drain the potatoes and mash with butter."]


def fake_embed(texts):
    vocab = ["potato", "boil", "parsley", "butter", "heat", "drain"]
    return [[float(w in t.lower()) for w in vocab] for t in texts]


def test_chunks_are_numbered_steps():
    assert H.chunks(STEPS)[1] == (2, "Step 2: Boil the potatoes for 20 minutes.")


def test_rrf_fuses_two_rankings():
    assert H.rrf([[0, 1, 2], [2, 0, 1]], k=60)[0] in (0, 2)
    assert sorted(H.rrf([[0, 1], [1, 0]])) == [0, 1]


def test_contexts_per_rung():
    q = "I have just finished step 2 of this recipe. Which ingredients have been heated so far?"
    b0 = H.context("B0", q, STEPS, cut=2, embed=fake_embed)
    b1 = H.context("B1", q, STEPS, cut=2, embed=fake_embed)
    b2 = H.context("B2", q, STEPS, cut=2, embed=fake_embed)
    b4 = H.context("B4", q, STEPS, cut=2, embed=fake_embed)
    assert b0 == "" and "Step" in b1 and "Step" in b2
    assert b4.startswith(b2) and "State after step 2" in b4 and "Heated so far: potatoes" in b4
    with pytest.raises(ValueError):
        H.context("B3", q, STEPS, cut=2, embed=fake_embed)


def test_prompt_demands_strict_format():
    p1 = H.prompt("S1", "q?", "ctx")
    p2 = H.prompt("S2", "q?", "")
    assert "comma-separated" in p1 and "ctx" in p1
    assert "one cooking verb" in p2 and "Context" not in p2


def test_scoring_links_to_ids():
    link = {"potatoes": "ING-1", "potato": "ING-1", "butter": "ING-2"}.get
    assert H.score_s1("Potatoes", {"ING-1"}, link) is True
    assert H.score_s1("potatoes, butter", {"ING-1"}, link) is False
    assert H.score_s1("none", set(), link) is True
    proc = {"drain": "PROC-78", "mash": "PROC-71"}.get
    assert H.score_s2("Drain.", "PROC-78", proc) is True
    assert H.score_s2("mash", "PROC-78", proc) is False
    assert H.score_s2("", "PROC-78", proc) is False
