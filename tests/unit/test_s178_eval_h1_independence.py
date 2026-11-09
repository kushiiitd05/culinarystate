"""S178 / T8-C04-R2: H1 gold-independence checks and the pre-cut / no-answer-line contexts. Fake embedder, no LLM."""
from __future__ import annotations

import pytest

from culinarystate.evaluation import d5_state as DS
from culinarystate.evaluation import h1_independence as I
from culinarystate.evaluation import h1_rungs as H

STEPS = ["Peel and dice the potatoes.", "Boil the potatoes for 20 minutes.", "Chop the parsley.",
         "Drain the potatoes and mash with butter."]
Q1 = "I have just finished step 2 of this recipe. Which ingredients have been heated so far?"
Q2 = "I have just finished step 3 of this recipe. What do I do next?"


def fake_embed(texts):
    vocab = ["potato", "boil", "parsley", "butter", "heat", "drain", "mash"]
    return [[float(w in t.lower()) for w in vocab] for t in texts]


def s1_row(engine):
    return {"qid": "D5-S1-001", "block": "S1", "gold_ingredient_ids": "|".join(engine["heated_ids"])}


def s2_row(engine):
    return {"qid": "D5-S2-001", "block": "S2", "gold_next_process_id": engine["next_process_id"] or ""}


# ---------------------------------------------------------------- provenance gate

def test_gold_origin_inference():
    assert I.gold_origin({"status": "DRAFT_FOR_REVIEW", "drafted_by": "AI_AGENT_S171"}) == "ENGINE_DRAFT"
    assert I.gold_origin({"verdict": "KEEP"}) == "HUMAN_AFTER_SEEING_ENGINE"
    assert I.gold_origin({"verdict": "EDIT", "seen_system_output": "true"}) == "HUMAN_AFTER_SEEING_ENGINE"
    assert I.gold_origin({"verdict": "KEEP", "seen_system_output": "false"}) == "HUMAN_BLIND"
    assert I.gold_origin({"gold_origin": "human_blind"}) == "HUMAN_BLIND"
    assert I.gold_origin({"gold_origin": "nonsense", "verdict": ""}) == "ENGINE_DRAFT"


def test_independence_report_labels():
    draft = [{"qid": f"D5-S1-{i}", "block": "S1"} for i in range(3)] + [{"qid": "D5-S2-1", "block": "S2"}]
    rep = I.gold_independence_report(draft)
    assert rep["label"] == "CIRCULAR_SELF_CONSISTENCY_ONLY" and rep["n_independent"] == 0
    assert rep["by_block"]["S1"]["ENGINE_DRAFT"] == 3 and len(rep["not_independent_qids"]) == 4
    mixed = [{**draft[0], "gold_origin": "HUMAN_BLIND"}] + draft[1:]
    assert I.gold_independence_report(mixed)["label"] == "PARTLY_INDEPENDENT"
    allb = [{**r, "gold_origin": "HUMAN_BLIND"} for r in draft]
    assert I.gold_independence_report(allb)["label"] == "INDEPENDENT_GOLD"
    assert I.gold_independence_report([{"qid": "x", "block": "P1"}])["n_rows"] == 0      # other blocks ignored


# ---------------------------------------------------------------- the gold-vs-context test

def test_legacy_context_shares_engine_output_with_gold():
    """S173 behaviour: the B4 context prints the heated set that the S1 gold was drafted from -> must be flagged."""
    eng = I.engine_outputs(STEPS, 2)
    assert eng["heated_ids"], "fixture should heat the potatoes"
    ctx = H.context("B4", Q1, STEPS, cut=2, embed=fake_embed)                       # legacy defaults
    assert "Heated so far:" in ctx
    assert I.shared_engine_outputs(s1_row(eng), ctx, eng) == ["heated_ids"]
    with pytest.raises(I.GoldContextOverlap) as e:
        I.assert_independent(s1_row(eng), ctx, eng, cut=2)
    assert any("SHARED_ENGINE_OUTPUT: heated_ids" in f for f in e.value.findings)
    assert any("AGGREGATE_ANSWER_FIELD" in f for f in e.value.findings)


def test_independent_context_passes_for_every_rung_and_block():
    eng1, eng2 = I.engine_outputs(STEPS, 2), I.engine_outputs(STEPS, 3)
    for rung in ("B0", "B1", "B2", "B4"):
        c1 = H.independent_context(rung, Q1, STEPS, cut=2, embed=fake_embed)
        I.assert_independent(s1_row(eng1), c1, eng1, cut=2)
        c2 = H.independent_context(rung, Q2, STEPS, cut=3, embed=fake_embed)
        I.assert_independent(s2_row(eng2), c2, eng2, cut=3)


def test_legacy_retrieval_can_hand_over_the_next_step_and_pre_cut_cannot():
    eng = I.engine_outputs(STEPS, 3)
    assert eng["next_step_index"] == 4 and eng["next_process_id"]
    row = s2_row(eng)
    q = "What do I do next? drain the potatoes and mash with butter"                    # B1/B2 rank step 4 first
    legacy = H.context("B2", q, STEPS, cut=3, embed=fake_embed)
    assert "Step 4:" in legacy and I.shared_engine_outputs(row, legacy, eng) == ["next_process_id"]
    assert any("POST_CUT_STEP" in f for f in I.context_leaks(row, legacy, cut=3))
    fixed = H.independent_context("B2", q, STEPS, cut=3, embed=fake_embed)
    assert "Step 4:" not in fixed and not I.context_leaks(row, fixed, cut=3)


def test_independent_b4_never_calls_the_gold_function(monkeypatch):
    """The S1 gold function (heated_ingredient_ids) must not run when building an independent B4 context."""
    def boom(*a, **k):
        raise AssertionError("independent B4 context called heated_ingredient_ids")
    monkeypatch.setattr(DS, "heated_ingredient_ids", boom)
    ctx = H.independent_context("B4", Q1, STEPS, cut=2, embed=fake_embed, state_view="PRIMITIVES")
    assert "Actions so far:" in ctx and "Heated so far" not in ctx and "State after step 2" in ctx
    assert "boil" in ctx.split("Actions so far:")[1].lower()
    with pytest.raises(AssertionError):                                           # the legacy view does call it
        H.context("B4", Q1, STEPS, cut=2, embed=fake_embed)


def test_default_independent_view_is_minimal_and_prints_no_event_list():
    ctx = H.independent_context("B4", Q1, STEPS, cut=2, embed=fake_embed)
    assert "Ingredients used:" in ctx and "Last action:" in ctx
    assert "Actions so far" not in ctx and "Heated so far" not in ctx
    eng = I.engine_outputs(STEPS, 2)
    assert eng["used_ids"] and set(eng["heated_ids"]) <= set(eng["used_ids"])


def test_aggregate_field_is_only_an_s1_leak():
    eng = I.engine_outputs(STEPS, 3)
    legacy = H.context("B4", Q2, STEPS, cut=3, embed=fake_embed)
    assert "Heated so far:" in legacy
    assert not any("AGGREGATE" in f for f in I.context_leaks(s2_row(eng), legacy, cut=3))
    assert any("AGGREGATE" in f for f in I.context_leaks({"block": "S1"}, legacy, cut=3))


def test_independent_contexts_only_cite_steps_up_to_the_cut():
    for rung in ("B1", "B2", "B4"):
        for cut in (1, 2, 3):
            ctx = H.independent_context(rung, "boil drain mash", STEPS, cut=cut, embed=fake_embed)
            assert all(int(n) <= cut for n in I.STEP_LINE.findall(ctx))


def test_state_views_and_defaults_are_backward_compatible():
    legacy = H.context("B4", Q1, STEPS, cut=2, embed=fake_embed)
    assert legacy == H.context("B4", Q1, STEPS, cut=2, embed=fake_embed, pre_cut_only=False, state_view="ANSWER")
    assert H.state_block(STEPS, 2, view="NONE") == ""
    mini = H.state_block(STEPS, 2, view="MINIMAL")
    assert mini.splitlines() == ["State after step 2:", "Ingredients used: potatoes", "Last action: boil"]
    b2 = H.context("B2", Q1, STEPS, cut=2, embed=fake_embed, pre_cut_only=True)
    assert H.context("B4", Q1, STEPS, cut=2, embed=fake_embed, pre_cut_only=True, state_view="NONE") == b2
    with pytest.raises(ValueError):
        H.state_block(STEPS, 2, view="GOLD")


# ---------------------------------------------------------------- link failures and plausibility

def test_score_s1_detail_keeps_link_failures():
    link = {"potatoes": "ING-1", "butter": "ING-2"}.get
    assert H.score_s1_detail("potatoes", {"ING-1"}, link) == {"correct": True, "link_failed": False, "n_items": 1,
                                                              "n_unlinked": 0, "said_none": False}
    d = H.score_s1_detail("potatoes, taters", {"ING-1"}, link)
    assert d["correct"] is False and d["link_failed"] is True and d["n_unlinked"] == 1
    assert H.score_s1_detail("none", set(), link)["correct"] is True
    for ans, gold in [("potatoes", {"ING-1"}), ("potatoes, butter", {"ING-1"}), ("none", set()), ("", {"ING-1"}),
                      ("potatoes and taters", {"ING-1"})]:
        assert H.score_s1(ans, gold, link) is H.score_s1_detail(ans, gold, link)["correct"]
    rate = H.link_failure_rate([d, H.score_s1_detail("potatoes", {"ING-1"}, link), H.score_s1_detail("none", set(), link)])
    assert rate == {"n_questions": 3, "n_named": 2, "n_link_failed": 1, "rate": 0.5}
    assert H.link_failure_rate([])["rate"] is None


def test_heat_presence_agreement_is_engine_free():
    assert I.heat_presence_agreement(STEPS, 2, {"ING-1"}) == "AGREE"
    assert I.heat_presence_agreement(STEPS, 1, set()) == "AGREE"
    assert I.heat_presence_agreement(STEPS, 1, {"ING-1"}) == "GOLD_WITHOUT_HEAT_WORD"
    assert I.heat_presence_agreement(STEPS, 2, set()) == "HEAT_WORD_WITHOUT_GOLD"


def test_gold_agreement_engine_vs_edited():
    draft = [{"qid": "a", "block": "S1", "gold_ingredient_ids": "ING-1|ING-2"},
             {"qid": "b", "block": "S1", "gold_ingredient_ids": "ING-3"},
             {"qid": "c", "block": "S1", "gold_ingredient_ids": "ING-4"},
             {"qid": "d", "block": "S2", "gold_next_process_id": "PROC-1"},
             {"qid": "e", "block": "S2", "gold_next_process_id": "PROC-2"}]
    final = [{"qid": "a", "gold_ingredient_ids": "ING-2|ING-1"}, {"qid": "b", "gold_ingredient_ids": "ING-3|ING-9"},
             {"qid": "c", "verdict": "DROP"}, {"qid": "d", "gold_next_process_id": "PROC-1"},
             {"qid": "e", "gold_next_process_id": "PROC-7"}]
    rep = I.gold_agreement(draft, final)
    assert rep["S1"]["n_scored"] == 2 and rep["S1"]["n_exact_agree"] == 1 and rep["S1"]["n_dropped"] == 1
    assert rep["S1"]["mean_jaccard"] == pytest.approx(0.75)
    assert rep["S2"]["exact_agreement"] == 0.5 and rep["S2"]["wilson95"][0] < 0.5 < rep["S2"]["wilson95"][1]
    assert I.gold_agreement(draft, [])["S1"]["n_missing_final"] == 3


def test_primitives_still_determine_part_of_the_gold_and_that_is_measurable():
    ev = I.primitive_events(STEPS, 2)
    assert [e["surface"] for e in ev][-1] == "boil" and ev[-1]["ing_ids"]
    eng = I.engine_outputs(STEPS, 2)
    assert I.heated_from_primitives(ev) == set(eng["heated_ids"])           # a plain heat-verb rule reconstructs the gold here
    assert I.heated_from_primitives([{"surface": "peel", "ing_ids": ["ING-1"]}]) == set()
    assert I.heated_from_primitives([{"surface": "Simmering", "ing_ids": ["ING-2", "ING-3"]}]) == {"ING-2", "ING-3"}
