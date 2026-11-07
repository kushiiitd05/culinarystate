"""S171 / D-075 M4: demo context helpers (target -> SVAR, cited ids) + one real-ledger integration (-m ledgers)."""
from __future__ import annotations

import pytest

from culinarystate.decision import demo_context as DC

REG = [{"state_variable_id": "SVAR-000009", "name": "Vitamin C, total ascorbic acid content", "current_row_count": "900"},
       {"state_variable_id": "SVAR-000215", "name": "Vitamin C content", "current_row_count": "40"},
       {"state_variable_id": "SVAR-000010", "name": "Thiamin content", "current_row_count": "500"}]


def test_svar_for_picks_name_match_with_most_rows():
    assert DC.svar_for("vitamin c", REG) == "SVAR-000009"
    assert DC.svar_for("Thiamin", REG) == "SVAR-000010"
    assert DC.svar_for("texture", REG) is None and DC.svar_for(None, REG) is None


def test_cited_ids_in_order_without_duplicates():
    assert DC.cited_ids("a [EVD-017045] b [EVD-017049] c [EVD-017045]") == ["EVD-017045", "EVD-017049"]
    assert DC.cited_ids("none") == []


def test_recipe_summary_counts_routes_per_event():
    items = [{"event_id": "E1", "action": "Boil", "process_id": "PROC-1", "ingredient_id": "ING-1", "route": "DIRECT",
              "reasons": ["EVIDENCE_PREEMPTS"], "evidence": [{"evd_id": "EVD-9"}]},
             {"event_id": "E2", "action": "Stir", "process_id": None, "ingredient_id": None, "route": "UNKNOWN",
              "reasons": ["EVENT_UNRESOLVED", "NO_LINKED_INGREDIENT"], "evidence": []}]
    s = DC.recipe_summary({"items": items, "target_svar": "SVAR-000009"})
    assert s["routes"] == {"DIRECT": 1, "UNKNOWN": 1} and s["steps"][0]["evidence"] == ["EVD-9"]
    assert s["steps"][1]["route"] == "UNKNOWN" and "NO_LINKED_INGREDIENT" in s["steps"][1]["reasons"]


@pytest.mark.ledgers
def test_real_transformation_answer_cites_evidence_and_routes_recipe():
    ctx = DC.DemoContext.load()
    out = ctx.respond("How much vitamin C does boiled cabbage keep?",
                      recipe_text="Boil the cabbage for 10 minutes. Drain and serve.")
    assert out["route"]["branch"] == "TRANSFORMATION" and out["citable"] is False
    assert out["cited"] and all(c.startswith("EVD-") for c in out["cited"])
    assert out["detail"]["recipe"]["target_svar"] == "SVAR-000009"
    assert ctx.respond("Here is a photo of my bread")["mode"] == "ABSTAIN_UNSUPPORTED"


def test_relationship_answer_says_corpus_pattern_not_equivalence():
    from culinarystate.decision.candidates import Candidate
    cands = [Candidate(type="SUBSTITUTION", id="ING-2", name="yogurt", confidence=0.42, evidence_count=0,
                       source_predicate="ING_ALTERNATIVE_TO", reason="r")]
    out = DC.relationship_answer("buttermilk", cands)
    assert out["mode"] == "ANSWER_CORPUS_PATTERN" and out["cited"] == []
    assert "yogurt" in out["answer"] and "42%" in out["answer"] and "not" in out["answer"].lower()
    none = DC.relationship_answer("buttermilk", [])
    assert none["mode"] == "ABSTAIN_NO_EDGES"
    assert DC.relationship_answer(None, cands)["mode"] == "ASK"
