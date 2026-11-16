"""D-085 in the D5 freeze guard and the H1 gold-origin gate (S179), test-first.

The AI delegate ``ksh+prv (AI, D-085)`` may approve a D5 freeze for both humans only when the entry names D-085 and
carries NO_HUMAN_SIGNOFF_D085; every other AI name stays refused. AI-written S gold is AI_DRAFTED_GOLD: never
HUMAN_BLIND, so H1 is never INDEPENDENT_GOLD on it.
"""
from __future__ import annotations

import pytest

from culinarystate.evaluation import frozen_guard as FG
from culinarystate.evaluation import h1_independence as HI
from culinarystate.evaluation.freeze_records import AI_DELEGATE

DELEGATE = {"approved_by": AI_DELEGATE, "approved_date": "2026-11-10", "decision": "D-085",
            "label": "NO_HUMAN_SIGNOFF_D085"}


def test_delegate_entry_satisfies_both_humans():
    assert FG.approval_problems({"approvals": [DELEGATE]}) == []
    assert FG.signoff_kind({"approvals": [DELEGATE]}) == "AI_DELEGATED_D085"


@pytest.mark.parametrize("drop", ["decision", "label", "approved_date"])
def test_delegate_entry_needs_decision_label_and_date(drop):
    entry = {k: v for k, v in DELEGATE.items() if k != drop}
    assert FG.approval_problems({"approvals": [entry]}) != []


@pytest.mark.parametrize("who", ["ksh", "prv", "ksh+prv (AI)", "Claude", "AI_AGENT", "ksh+prv (AI, D-084)"])
def test_other_ai_names_still_refused(who):
    entry = {**DELEGATE, "approved_by": who}
    assert any(p.startswith(("AI_APPROVAL", "APPROVER_NOT_HUMAN")) for p in FG.approval_problems({"approvals": [entry]}))


def test_human_approvals_unchanged():
    rec = {"approvals": [{"approved_by": "Kush Tokas", "approved_date": "2026-11-10"},
                         {"approved_by": "Parv Goyal", "approved_date": "2026-11-10"}]}
    assert FG.approval_problems(rec) == [] and FG.signoff_kind(rec) == "HUMAN"
    assert FG.approval_problems({"approvals": rec["approvals"][:1]}) == ["MISSING_APPROVER: Parv Goyal"]


def test_ai_drafted_gold_is_its_own_origin_and_never_independent():
    assert "AI_DRAFTED_GOLD" in HI.GOLD_ORIGINS
    rows = [{"qid": f"D5-S1-00{i}", "block": "S1", "drafted_by": "AI_AGENT_S171", "gold_origin": "AI_DRAFTED_GOLD",
             "gold_source": "AI_DELEGATE_D085", "seen_system_output": "false", "verdict": "KEEP"} for i in range(3)]
    assert HI.gold_origin_detail(rows[0]) == ("AI_DRAFTED_GOLD", "EXPLICIT_AI_DELEGATE_D085")
    rep = HI.gold_independence_report(rows)
    assert rep["n_independent"] == 0 and rep["label"] == "CIRCULAR_SELF_CONSISTENCY_ONLY"
    assert rep["by_block"]["S1"]["AI_DRAFTED_GOLD"] == 3


def test_ai_gold_cannot_claim_blind_human_source():
    row = {"qid": "D5-S1-001", "block": "S1", "gold_origin": "AI_DRAFTED_GOLD", "gold_source": "BLIND_HUMAN",
           "blind_answer_r1": "x", "seen_system_output": "false"}
    with pytest.raises(HI.GoldOriginRefused):
        HI.gold_origin_detail(row)
