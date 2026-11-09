"""S178 FIX-EVAL: SCI-B E1 (gold origin) and E6 (h1_rungs docstring, leaky context() defaults). Synthetic rows only.

E1 failure scenario (review): under D5 option G-B a row {drafted_by AI_AGENT_S171, KEEP, seen false, gold = engine output} became
HUMAN_BLIND and the set was labelled INDEPENDENT_GOLD; an explicit gold_origin column won with no evidence.
E6 failure scenario: a D5 runner that calls context() with its defaults re-leaks the S1 gold (20/20 contexts).
"""
from __future__ import annotations

import inspect

import pytest

from culinarystate.evaluation import h1_independence as I
from culinarystate.evaluation import h1_rungs as H

ENGINE_ROW = {"qid": "D5-S1-001", "block": "S1", "gold_ingredient_ids": "ING-000326", "drafted_by": "AI_AGENT_S171",
              "status": "DRAFT_FOR_REVIEW"}


# ------------------------------------------------------------------ E1
def test_keep_of_an_engine_draft_after_a_blind_pass_is_not_human_blind():
    row = {**ENGINE_ROW, "verdict": "KEEP", "seen_system_output": "false"}             # the reviewer's G-B row
    assert I.gold_origin(row) == "HUMAN_AFTER_SEEING_ENGINE"
    assert I.gold_origin_detail(row) == ("HUMAN_AFTER_SEEING_ENGINE", "ENGINE_DRAFT_KEPT")
    edit = {**row, "verdict": "EDIT"}
    assert I.gold_origin_detail(edit) == ("HUMAN_AFTER_SEEING_ENGINE", "ENGINE_DRAFT_EDITED")
    rep = I.gold_independence_report([row, {**row, "qid": "D5-S1-002"}])
    assert rep["label"] == "CIRCULAR_SELF_CONSISTENCY_ONLY" and rep["n_independent"] == 0
    assert rep["by_reason"] == {"ENGINE_DRAFT_KEPT": 2}


def test_keep_without_a_drafter_is_still_anchored():
    assert I.gold_origin({"verdict": "KEEP", "seen_system_output": "false"}) == "HUMAN_AFTER_SEEING_ENGINE"


def test_human_blind_needs_a_filled_blind_answer_column():
    row = {**ENGINE_ROW, "gold_source": "BLIND_HUMAN", "blind_answer_r1": "cider", "seen_system_output": "false"}
    assert I.gold_origin_detail(row) == ("HUMAN_BLIND", "BLIND_ANSWER_COLUMN")
    assert I.gold_origin({**row, "seen_system_output": "true"}) == "HUMAN_AFTER_SEEING_ENGINE"
    assert I.gold_origin({**row, "seen_system_output": ""}) == "HUMAN_AFTER_SEEING_ENGINE"    # unrecorded flag: fail closed
    with pytest.raises(I.GoldOriginRefused):
        I.gold_origin({**row, "blind_answer_r1": ""})                                 # BLIND_HUMAN claimed, no blind answer


def test_explicit_human_blind_on_an_ai_drafted_row_with_empty_blind_columns_is_refused():
    row = {**ENGINE_ROW, "gold_origin": "HUMAN_BLIND"}
    with pytest.raises(I.GoldOriginRefused) as e:
        I.gold_origin(row)
    assert "AI_DRAFTED" in str(e.value)
    with pytest.raises(I.GoldOriginRefused):
        I.gold_origin({"qid": "x", "block": "S1", "gold_origin": "HUMAN_BLIND", "verdict": "KEEP"})   # a kept draft
    with pytest.raises(I.GoldOriginRefused):
        I.gold_origin({"qid": "x", "block": "S1", "gold_origin": "HUMAN_BLIND", "seen_system_output": "true"})
    rep = I.gold_independence_report([row, {**ENGINE_ROW, "qid": "D5-S1-002", "gold_origin": "HUMAN_BLIND",
                                            "gold_source": "BLIND_HUMAN", "blind_answer_r1": "x", "seen_system_output": "false"}])
    assert rep["label"] == "REFUSED_GOLD_PROVENANCE_CONFLICT" and rep["n_refused"] == 1 and rep["n_independent"] == 1
    assert list(rep["refused"]) == ["D5-S1-001"]


def test_explicit_downgrade_wins_and_human_declared_blind_without_ai_drafter_is_kept():
    blind = {**ENGINE_ROW, "gold_source": "BLIND_HUMAN", "blind_answer_r1": "cider", "seen_system_output": "false"}
    assert I.gold_origin({**blind, "gold_origin": "ENGINE_DRAFT"}) == "ENGINE_DRAFT"      # tightening is always allowed
    fixture = {"qid": "SYN-S1-001", "block": "S1", "gold_origin": "HUMAN_BLIND", "drafted_by": "SYNTHETIC_FIXTURE"}
    assert I.gold_origin_detail(fixture) == ("HUMAN_BLIND", "EXPLICIT_DECLARED_NON_AI_DRAFTER")


def test_ai_drafter_detection():
    for d in ("AI_AGENT_S171", "ai-agent", "Claude", "engine_rung_a", "LLM_DRAFT", "agent"):
        assert I.is_ai_drafted({"drafted_by": d}), d
    for d in ("", "SYNTHETIC_FIXTURE", "Kush Tokas", "Parv Goyal", "MAINTAINER"):
        assert not I.is_ai_drafted({"drafted_by": d}), d


def test_the_committed_draft_counts_are_unchanged_by_the_fix():
    import csv
    from pathlib import Path
    rows = list(csv.DictReader(open(Path(I.__file__).resolve().parents[3] / "benchmark/d5/d5_draft_S_v1.csv", encoding="utf-8-sig")))
    rep = I.gold_independence_report(rows)
    assert rep["n_rows"] == 40 and rep["n_independent"] == 0 and rep["by_block"]["S1"]["ENGINE_DRAFT"] == 20
    assert rep["label"] == "CIRCULAR_SELF_CONSISTENCY_ONLY" and rep["by_reason"] == {"NO_HUMAN_VERDICT": 40}


# ------------------------------------------------------------------ E6
STEPS = ["Peel and dice the potatoes.", "Boil the potatoes for 20 minutes.", "Chop the parsley.",
         "Drain the potatoes and mash with butter."]


def fake_embed(texts):
    vocab = ["potato", "boil", "parsley", "butter"]
    return [[float(w in t.lower()) for w in vocab] for t in texts]


def test_state_block_docstring_no_longer_claims_no_parent_lot_walk():
    doc = inspect.getdoc(H.state_block)
    assert "no parent-lot walk" not in doc
    assert "parent" in doc and "_lot_ingredients" in doc


def test_context_refuses_legacy_defaults_for_a_d5_question():
    q = "I have just finished step 2 of this recipe. Which ingredients have been heated so far?"
    with pytest.raises(H.LeakyContextRefused):
        H.context("B4", q, STEPS, cut=2, embed=fake_embed, qid="D5-S1-001")
    with pytest.raises(H.LeakyContextRefused):
        H.context("B2", q, STEPS, cut=2, embed=fake_embed, qid="D5-S2-003")            # post-cut retrieval leaks S2 too
    with pytest.raises(H.LeakyContextRefused):
        H.context("B4", q, STEPS, cut=2, embed=fake_embed, qid="D5-S1-001", pre_cut_only=True)     # ANSWER view still leaks
    ok = H.context("B4", q, STEPS, cut=2, embed=fake_embed, qid="D5-S1-001", pre_cut_only=True, state_view="MINIMAL")
    assert "Heated so far" not in ok
    assert ok == H.independent_context("B4", q, STEPS, cut=2, embed=fake_embed, qid="D5-S1-001")
    legacy = H.context("B4", q, STEPS, cut=2, embed=fake_embed)                       # S173 replication without a D5 qid
    assert "Heated so far" in legacy
    assert H.context("B0", q, STEPS, cut=2, embed=fake_embed, qid="D5-S1-001") == ""   # B0 has no context to leak
