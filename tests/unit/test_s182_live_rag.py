"""Tests for the S182 live RAG console engine (tools/s182_live_rag.py).

The LLM is always a fake here: no test sends anything to NVIDIA. One integration test loads the
real StateBuilder (~6 s) so the packet path is exercised end to end on a self-written recipe.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("s182_live_rag", ROOT / "tools/s182_live_rag.py")
LR = importlib.util.module_from_spec(_spec)
sys.modules["s182_live_rag"] = LR
_spec.loader.exec_module(LR)


# ------------------------------------------------------------------ question parsing
@pytest.mark.parametrize("q,target", [
    ("How much vitamin C remains?", "vitc"),
    ("how much vit c is left", "vitc"),
    ("Is ascorbic acid lost?", "vitc"),
    ("What about lycopene?", "lycopene"),
    ("How much iron remains?", None),
])
def test_target(q, target):
    assert LR.parse_target(q) == target


@pytest.mark.parametrize("q,kind", [
    ("Does vitamin C leach into the water?", "LEACHING"),
    ("How much vitamin C remains after boiling?", "RETENTION_NUMERIC"),
    ("What percent of lycopene is retained?", "RETENTION_NUMERIC"),
    ("How does boiling affect vitamin C?", "PROCESS_EFFECT"),
    ("Does this dish taste of lycopene?", "FLAVOUR"),
    ("Vitamin C?", "RETENTION_NUMERIC"),
])
def test_kind(q, kind):
    assert LR.parse_kind(q) == kind


def test_food_named_in_question_wins():
    assert LR.pick_food("vitamin C in the carrots?", ["tomato", "carrot"]) == "carrot"


def test_food_single_candidate_is_used():
    assert LR.pick_food("how much vitamin C remains?", ["tomato"]) == "tomato"


def test_food_ambiguous_is_none():
    assert LR.pick_food("how much vitamin C remains?", ["tomato", "carrot"]) is None


# ------------------------------------------------------------------ prompts
PACKET = {"food": "tomato", "step": 2, "action": "Boil", "target": "vitc", "question_kind": "RETENTION_NUMERIC",
          "route": "DIRECT", "allowed_claims": ["NUMERIC"], "required_caveats": [], "forbidden_claims": [],
          "evidence_ids": ["EVD-002765"], "evidence_values": ["EVD-002765=95.0%"], "near_evidence_ids": [],
          "unknown_reasons": {}, "max_allowed_precision": 1}


def test_verbaliser_prompt_contains_packet_and_not_recipe():
    p = LR.verbaliser_prompt("How much vitamin C remains?", PACKET)
    assert "EVD-002765" in p and "DIRECT" in p and "How much vitamin C remains?" in p
    assert "Recipe:" not in p


def test_plain_prompt_has_no_contract():
    p = LR.plain_prompt("Boil tomatoes.", "How much vitamin C remains?")
    assert p.startswith("Recipe: Boil tomatoes.") and "EVD" not in p


def test_strip_think():
    assert LR.strip_think("<think>long chain</think>\n Answer.") == "Answer."
    assert LR.strip_think("Answer.") == "Answer."


# ------------------------------------------------------------------ licence gate
def test_licence_scan_flags_bbc_markers():
    assert LR.licence_hits({"a": ["x", {"b": "SRC-000002"}]}) == ["SRC-000002"]
    assert LR.licence_hits({"a": "BBCGF-A1 row"}) == ["BBCGF-A1"]
    assert LR.licence_hits(PACKET) == []


# ------------------------------------------------------------------ request validation
@pytest.mark.parametrize("body,err", [
    ({}, "question"),
    ({"question": "", "recipe_text": "x"}, "question"),
    ({"question": "q", "recipe_text": ""}, "recipe_text"),
    ({"question": "q" * 501, "recipe_text": "x"}, "question"),
    ({"question": "q", "recipe_text": "x" * 6001}, "recipe_text"),
    ({"question": "q", "recipe_text": "x", "self_written": "yes"}, "self_written"),
])
def test_validate_rejects(body, err):
    with pytest.raises(LR.RequestError, match=err):
        LR.validate(body)


def test_validate_accepts_and_does_not_mutate():
    body = {"question": " How much? ", "recipe_text": "Boil.", "self_written": True}
    out = LR.validate(body)
    assert out == {"question": "How much?", "recipe_text": "Boil.", "self_written": True}
    assert body["question"] == " How much? "


# ------------------------------------------------------------------ end to end, fake LLM
class FakeLLM:
    model = "fake-model"

    def __init__(self, contract_reply: str, plain_reply: str, advice_reply: str = "Rinse the pasta."):
        self.contract_reply, self.plain_reply, self.advice_reply = contract_reply, plain_reply, advice_reply
        self.prompts = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if "CLAIM PACKET" in prompt:
            return self.contract_reply
        return self.advice_reply if "STATE TRACE" in prompt else self.plain_reply


@pytest.fixture(scope="module")
def engine():
    return LR.LiveEngine.load()


RECIPE_A = "Chop the tomatoes. Boil the tomatoes in water for 15 minutes."
RECIPE_B = "Chop the tomatoes. Boil the tomatoes in water with salt for 15 minutes."


def test_direct_case_llm_passes_verifier(engine):
    llm = FakeLLM("About 95.0% of the vitamin C remains [EVD-002765].", "Roughly 50% is lost.")
    r = engine.answer("How much vitamin C remains in the tomatoes?", RECIPE_A, llm=llm, self_written=True)
    assert r["system"]["route"] == "DIRECT"
    assert r["system"]["used_template"] is False
    assert r["system"]["final"].startswith("About 95.0%")
    assert r["plain"]["text"] == "Roughly 50% is lost."
    assert r["plain"]["check"]["ok"] is False
    assert r["evidence"] and r["evidence"][0]["id"] == "EVD-002765"


def test_unknown_case_invented_number_falls_back_to_template(engine):
    llm = FakeLLM("About 70% remains.", "About 70% remains.")
    r = engine.answer("How much vitamin C remains in the tomatoes?", RECIPE_B, llm=llm, self_written=True)
    assert r["system"]["route"] == "UNKNOWN"
    assert r["system"]["used_template"] is True
    assert "FORBIDDEN_NUMERIC_CLAIM" in r["system"]["draft_check"]["codes"]
    assert "not known" in r["system"]["final"]


def test_not_self_written_never_calls_llm(engine):
    llm = FakeLLM("x", "y")
    r = engine.answer("How much vitamin C remains in the tomatoes?", RECIPE_A, llm=llm, self_written=False)
    assert llm.prompts == []
    assert r["plain"]["status"] == "NOT_SENT_TEXT_NOT_SELF_WRITTEN"
    assert r["system"]["used_template"] is True


def test_unwired_nutrient_number_abstains_but_plain_still_answers(engine):
    llm = FakeLLM("x", "Iron stays.")
    r = engine.answer("How much iron remains in the tomatoes?", RECIPE_A, llm=llm, self_written=True)
    assert r["system"]["status"] == "ABSTAIN_TARGET_NOT_WIRED"
    assert r["plain"]["text"] == "Iron stays."


# ------------------------------------------------------------------ state-aware advice
PASTA = "Boil the pasta in water with vinegar for 10 minutes. Drain the pasta."
PASTA_Q = "Oops, I boiled the pasta with vinegar by mistake. How can I fix it?"


@pytest.mark.parametrize("q,mode", [
    (PASTA_Q, "ADVICE"),
    ("What can I use instead of vinegar?", "ADVICE"),
    ("How much vitamin C remains?", "NUTRIENT"),
    ("How much iron remains in the tomatoes?", "NUTRIENT"),
    ("Is this pasta safe to eat tomorrow?", "SAFETY"),
    ("How long does cooked pasta keep in the fridge?", "SAFETY"),
])
def test_question_mode(q, mode):
    assert LR.question_mode(q) == mode


def test_state_trace_names_known_and_unknown_facts(engine):
    states = engine.snap.jsonable(engine.builder.build(PASTA))
    trace = LR.state_trace(states)
    assert trace[0]["step"] == 1 and trace[0]["action"] == "Boil"
    assert trace[0]["known"]["acid_present"] is True
    assert trace[0]["known"]["lot_members"] == ["pasta", "vinegar", "water"]
    assert "lipid_present" in trace[0]["unknown"]
    assert "member_composition" not in trace[0]["known"]


def test_advice_prompt_carries_trace_not_evidence():
    p = LR.advice_prompt(PASTA_Q, [{"step": 1, "action": "Boil", "food": "pasta", "known": {"acid_present": True}, "unknown": {}}])
    assert "STATE TRACE" in p and "acid_present" in p and PASTA_Q in p


def test_advice_mode_uses_state_and_is_labelled_suggested(engine):
    llm = FakeLLM("x", "You didn't make a mistake.", "Rinse it: acid_present was true in the water at step 1.")
    r = engine.answer(PASTA_Q, PASTA, llm=llm, self_written=True)
    s = r["system"]
    assert s["status"] == "STATE_AWARE_ADVICE" and s["used_template"] is False
    assert s["final"].startswith("Rinse it")
    assert s["label"] == "AI_SUGGESTED_STATE_GROUNDED"
    assert r["trace"][0]["known"]["acid_present"] is True
    advice_prompt = next(p for p in llm.prompts if "STATE TRACE" in p)
    assert "vinegar" in advice_prompt
    assert r["plain"]["text"] == "You didn't make a mistake."


def test_advice_flags_unsourced_percentages(engine):
    llm = FakeLLM("x", "y", "Rinse it; this removes 80% of the acid.")
    r = engine.answer(PASTA_Q, PASTA, llm=llm, self_written=True)
    assert r["system"]["warnings"] == ["UNSOURCED_PERCENT: 80"]


def test_safety_question_is_refused_without_llm_for_system(engine):
    llm = FakeLLM("x", "Sure, 3 days.")
    r = engine.answer("Is this pasta safe to eat tomorrow?", PASTA, llm=llm, self_written=True)
    assert r["system"]["status"] == "ABSTAIN_SAFETY"
    assert not any("STATE TRACE" in p for p in llm.prompts)


def test_advice_not_self_written_sends_nothing(engine):
    llm = FakeLLM("x", "y")
    r = engine.answer(PASTA_Q, PASTA, llm=llm, self_written=False)
    assert llm.prompts == [] and r["system"]["status"] == "ADVICE_NOT_SENT"


def test_llm_error_is_reported_not_hidden(engine):
    def boom(prompt: str) -> str:
        raise RuntimeError("HTTP 503")
    boom.model = "fake"
    r = engine.answer("How much vitamin C remains in the tomatoes?", RECIPE_A, llm=boom, self_written=True)
    assert r["plain"]["status"] == "LLM_ERROR" and "503" in r["plain"]["reason"]
    assert r["system"]["used_template"] is True and r["system"]["final"]


# ------------------------------------------------------------------ citation check against the trace
TRACE = [{"step": 1, "action": "Boil", "food": "pasta",
          "known": {"acid_present": True, "acid_exposure_before": False, "lot_members": ["pasta", "vinegar", "water"],
                    "hot_aqueous_minutes": 10.0},
          "unknown": {"lipid_present": "NO_RECOGNIZED_MARKER"}}]


def test_citation_check_true_false_and_unknown():
    text = ("Rinse (step 1: acid_present = true). Balance it (step 1: acid_exposure_before = true). "
            "Add fat (step 1: lipid_present = NO_RECOGNIZED_MARKER). Long boil (step 1: hot_aqueous_minutes = 10.0).")
    rows = LR.citation_check(text, TRACE)
    assert [(r["field"], r["ok"]) for r in rows] == [
        ("acid_present", True), ("acid_exposure_before", False), ("lipid_present", True), ("hot_aqueous_minutes", True)]
    assert rows[1]["actual"] == "false"


def test_citation_check_unknown_field_or_step():
    rows = LR.citation_check("x (step 3: acid_present = true) y (step 1: colour = red)", TRACE)
    assert [r["actual"] for r in rows] == ["NO_SUCH_STEP", "NOT_IN_TRACE"] and not any(r["ok"] for r in rows)


def test_citation_check_none_cited():
    assert LR.citation_check("Rinse the pasta.", TRACE) == []


def test_citation_check_mixed_case_field():
    trace = [{"step": 1, "action": "Boil", "food": "pasta", "known": {"temperature_C": "100"}, "unknown": {}}]
    rows = LR.citation_check("(step 1: temperature_C = 100)", trace)
    assert rows == [{"step": 1, "field": "temperature_C", "claimed": "100", "actual": "100", "ok": True}]


# ------------------------------------------------------------------ state coverage
def test_coverage_classifies_filled_not_applicable_unknown():
    states = [{"step": 1, "action": "Dice", "food": "carrot",
               "G": {"process": {"v": "PROC-1 dice", "b": "RUNG_A"}},
               "C": {"lot_acidity_band": {"v": None, "u": "LOT_PH_NOT_COMPUTED"}},
               "Q": {"duration_min": {"v": None, "u": "NOT_A_HEAT_EVENT"},
                     "food_T_typical_C": {"v": 100.0, "b": "SCENARIO_DEFAULT"}}}]
    cov = LR.coverage(states)
    row = cov[0]
    assert row["counts"] == {"FILLED": 2, "NOT_APPLICABLE": 1, "UNKNOWN": 1}
    cells = {c["field"]: c for c in row["cells"]}
    assert cells["food_T_typical_C"] == {"field": "food_T_typical_C", "group": "simulation", "status": "FILLED",
                                         "value": 100.0, "source": "SCENARIO_DEFAULT"}
    assert cells["duration_min"]["status"] == "NOT_APPLICABLE"
    assert cells["lot_acidity_band"] == {"field": "lot_acidity_band", "group": "composition", "status": "UNKNOWN",
                                         "value": None, "source": "LOT_PH_NOT_COMPUTED"}


def test_coverage_on_showcase_recipe_fills_simulation(engine):
    states = engine.snap.jsonable(engine.builder.build(
        "Peel and dice the carrots. Boil the carrots in water with the lid on for 10 minutes. Drain the carrots."))
    boil = next(r for r in LR.coverage(states) if r["action"] == "Boil")
    sim = [c for c in boil["cells"] if c["group"] == "simulation" and c["status"] == "FILLED"]
    assert len(sim) >= 4


def test_advice_prompt_says_simulated_values_are_not_measurements():
    assert "simulated" in LR.advice_prompt("q", {}).lower()


def test_response_carries_coverage(engine):
    r = engine.answer(PASTA_Q, PASTA, llm=FakeLLM("x", "y"), self_written=False)
    assert r["coverage"] and r["coverage"][0]["counts"]["FILLED"] > 0


@pytest.mark.parametrize("claimed,actual,ok", [
    ("6.4 simulated", "6.426", True),
    ("6.43", "6.426", True),
    ("6", "6.426", True),
    ("6.5", "6.426", False),
    ("100 C", "100", True),
    ("true (simulated)", "true", True),
    ("DICED", "DICED", True),
    ("CUT", "DICED", False),
])
def test_same_accepts_rounding_and_trailing_words(claimed, actual, ok):
    assert LR._same(claimed, actual) is ok


# ------------------------------------------------------------------ duration ranges (live path crashed, batch did not)
@pytest.mark.parametrize("text", ["Scramble the eggs and cook for 2-5 min.", "Boil the eggs for 2 to 5 minutes."])
def test_duration_range_does_not_crash_and_is_kept(engine, text):
    r = engine.answer("How do I fix too much salt?", text, llm=FakeLLM("x", "y"), self_written=False)
    heat = [c for c in r["coverage"] if any(x["field"] == "duration_min" and x["status"] == "FILLED" for x in c["cells"])]
    assert heat, "the stated range should fill duration_min"


def test_lists_converts_tuples_without_mutating():
    rec = {"inputs": {"duration": {"value": (2, 5)}}, "x": [(1, 2)]}
    out = LR._lists(rec)
    assert out == {"inputs": {"duration": {"value": [2, 5]}}, "x": [[1, 2]]}
    assert rec["inputs"]["duration"]["value"] == (2, 5)


# ------------------------------------------------------------------ analyse phase, pipeline status, similar recipes
CARROTS = "Peel and dice the carrots. Boil the carrots in water with the lid on for 10 minutes. Drain the carrots."
SIM_DOCS = [
    {"id": "WIKIBOOKS:1", "family": "WIKIBOOKS", "title": "Boiled Carrots", "text": "carrot", "url": "https://wb/1",
     "steps": "Slice the carrots. Boil the carrots in salted water for 8 minutes. Drain the carrots."},
    {"id": "WIKIBOOKS:2", "family": "WIKIBOOKS", "title": "Carrot Cookies", "text": "carrot flour", "url": "https://wb/2",
     "steps": "Mix the carrots with the flour. Bake the cookies at 180 C for 12 minutes."},
    {"id": "R1", "family": "FOODCOM", "title": "Glazed carrots", "text": "", "url": None, "steps": None},
]


@pytest.fixture
def engine_with_index(engine):
    sim = LR._tool("s182_similar")
    old = engine.similar
    engine.similar = sim.SimilarIndex.from_docs(SIM_DOCS, min_df=1)
    yield engine
    engine.similar = old


def test_analyse_reports_every_pre_model_stage(engine_with_index):
    a = engine_with_index.analyse("My carrots came out too soft. What should I change?", CARROTS)
    ids = [s["id"] for s in a["pipeline"]]
    assert ids == ["parse", "state", "simulate", "evidence", "similar", "model", "verify"]
    by = {s["id"]: s for s in a["pipeline"]}
    assert all(by[k]["status"] == "done" for k in ("parse", "state", "simulate", "evidence", "similar"))
    assert by["model"]["status"] == "pending" and by["verify"]["status"] == "pending"
    assert "Boil" in by["simulate"]["detail"] and "simulated" in by["simulate"]["detail"]


def test_simulation_stage_not_applicable_without_heat(engine_with_index):
    a = engine_with_index.analyse("How do I fix this?", "Chop the tomatoes. Mix the tomatoes with salt.")
    sim = next(s for s in a["pipeline"] if s["id"] == "simulate")
    assert sim["status"] == "skipped"


def test_similar_reference_prefers_same_cooking_process(engine_with_index):
    a = engine_with_index.analyse("My carrots came out too soft. What should I change?", CARROTS)
    ref = a["similar"]["reference"]
    assert ref["title"] == "Boiled Carrots" and ref["licence"].startswith("CC BY-SA")
    assert any(h["process"].endswith("boil") or "boil" in h["process"] for h in ref["heat_steps"])
    assert a["similar"]["search"]["counts"]["FOODCOM"] == 1
    assert "Glazed carrots" not in str(a["similar"])


def test_advice_context_carries_reference_labelled_as_other_recipe(engine_with_index):
    llm = FakeLLM("x", "y", "Boil for less time (step 3: duration_min = 10).")
    r = engine_with_index.answer("My carrots came out too soft. What should I change?", CARROTS, llm=llm,
                                 self_written=True)
    prompt = next(p for p in llm.prompts if "STATE TRACE" in p)
    assert "similar_public_recipe_reference" in prompt and "Boiled Carrots" in prompt
    assert "Glazed carrots" not in prompt
    by = {s["id"]: s for s in r["pipeline"]}
    assert by["model"]["status"] == "done" and by["verify"]["status"] == "done"


def test_engine_without_index_skips_similar_stage(engine):
    old = engine.similar
    engine.similar = None
    try:
        a = engine.analyse("How do I fix this?", CARROTS)
    finally:
        engine.similar = old
    assert next(s for s in a["pipeline"] if s["id"] == "similar")["status"] == "skipped"


def test_missing_similar_data_degrades_to_none(monkeypatch, capsys):
    sim = LR._tool("s182_similar")

    def boom(*a, **k):
        raise FileNotFoundError("ledgers/recipe_base/recipe_base_v1.parquet")
    monkeypatch.setattr(sim.SimilarIndex, "load", classmethod(lambda cls, *a, **k: boom()))
    assert LR.load_similar() is None
    assert "similar-recipe search disabled" in capsys.readouterr().err
