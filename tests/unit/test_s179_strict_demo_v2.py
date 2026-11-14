"""Strict demo is separately versioned; linked identities cannot be replaced by caller context."""
from types import SimpleNamespace as NS

from culinarystate.decision.demo_context import DemoContext
from culinarystate.decision.demo_context_v2 import StrictDemoContext
from tests.unit.test_s179_strict_emission_v2 import fixture


def context(monkeypatch, *, wrong_food=False, wrong_packet_process=False):
    c, cond, row, packet = fixture()
    if wrong_food:
        row["matrix"]["ingredient_id"] = "ING-990002"
    packet.query = NS(process_id="PROC-990002" if wrong_packet_process else "PROC-990001")
    if wrong_packet_process:
        row["process"]["process_id"] = "PROC-990002"
    slots = NS(target="vitamin c", ingredient_id="ING-990001", ingredient_name="synthetic carrot", processes=[("boil", "PROC-990001")])
    result = {"decision": {"mode": "ANSWER", "precision": "QUANTITATIVE"}, "slots": slots, "packets": {"boil": packet}}
    from culinarystate.decision import pipeline
    monkeypatch.setattr(pipeline, "answer", lambda *a, **k: result)
    ctx = StrictDemoContext(lex=None, retriever=NS(cond={cond["id"]: cond}), req=None, family=None,
                            sup=None, ts=None, gates=None,
                            registry=[{"state_variable_id": "SVAR-990001", "name": "Vitamin C"}])
    return ctx, c


def test_default_demo_cannot_turn_missing_context_into_numeric_permission(monkeypatch):
    ctx, _ = context(monkeypatch)
    out = ctx._transform("How much vitamin C remains after boiling carrot?")
    assert out["mode"] == "ABSTAIN" and out["numeric_provenance"] == []
    assert "0.55" not in out["answer"]


def test_explicit_source_context_only_yields_unverified_table_report(monkeypatch):
    ctx, c = context(monkeypatch)
    out = ctx._transform("How much vitamin C remains after boiling carrot?", source_contexts={"boil": c})
    assert out["mode"] == "ANSWER" and "0.55" in out["answer"]
    assert out["evidence"]["from_data"] is False
    assert out["numeric_provenance"][0]["validated"] is False


def test_user_context_cannot_replace_linked_food_identity(monkeypatch):
    ctx, c = context(monkeypatch, wrong_food=True)
    c["ingredient_id"] = "ING-990002"
    out = ctx._transform("How much vitamin C remains after boiling carrot?", source_contexts={"boil": c})
    assert out["mode"] == "ABSTAIN" and out["numeric_provenance"] == []


def test_ambiguous_target_registry_is_not_resolved_by_row_count(monkeypatch):
    ctx, c = context(monkeypatch)
    ctx.registry.append({"state_variable_id": "SVAR-990002", "name": "Vitamin C, another basis", "current_row_count": "999999"})
    assert ctx._transform("How much vitamin C remains after boiling carrot?", source_contexts={"boil": c})["mode"] == "ABSTAIN"


def test_packet_query_cannot_replace_linked_process_identity(monkeypatch):
    ctx, c = context(monkeypatch, wrong_packet_process=True)
    c["process_id"] = "PROC-990002"
    out = ctx._transform("How much vitamin C remains after boiling carrot?", source_contexts={"boil": c})
    assert out["mode"] == "ABSTAIN" and out["numeric_provenance"] == []


def test_relationship_keeps_patterns_but_drops_unbound_numeric_scores(monkeypatch):
    monkeypatch.setattr(DemoContext, "_relationship", lambda *a, **k: {
        "mode": "ANSWER_CORPUS_PATTERN", "answer": "synthetic score 0.55",
        "candidates": [{"id": "ING-990002", "name": "synthetic alternative", "confidence": .55}], "cited": []})
    ctx = StrictDemoContext()
    out = ctx._relationship("replace synthetic food")
    assert "0.55" not in out["answer"] and "confidence" not in out["candidates"][0]
    assert out["pattern_basis"] == "CORPUS_PATTERN_UNVERIFIED"


def test_version_is_explicit_without_changing_legacy_class():
    assert StrictDemoContext().mode_info()["emission_policy"].startswith("strict-emission-v2")
    assert "emission_policy" not in DemoContext().mode_info()
