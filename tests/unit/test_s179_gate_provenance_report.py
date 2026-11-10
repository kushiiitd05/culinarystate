"""T9-C07-R3 gate provenance section (S179): generated from DECISIONS, every entry classed."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("gp", ROOT / "tools/s179_gate_provenance_report.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)


def _rows():
    return {r["id"]: r for r in G.entries(G.DECISIONS.read_text(encoding="utf-8"))}


def test_every_entry_is_classed_and_none_unknown():
    rows = _rows()
    assert rows and all(r["class"] in G.CLASSES for r in rows.values())
    assert not [k for k, r in rows.items() if r["class"] == "NO_APPROVER_LINE"]


def test_d085_is_human_and_its_delegate_acts_are_not():
    rows = _rows()
    assert rows["D-085"]["class"] == "HUMAN" and rows["D-084"]["class"] == "HUMAN"
    for d in ("D-086", "D-087", "D-088", "D-089", "D-090"):
        assert rows[d]["class"] == "AI_DELEGATED_D085", d
    assert rows["D-083"]["class"] == "AI_PERSONA_D071" and rows["D-002"]["class"] == "AI_AGENT_PROVISIONAL"


def test_classify_rules():
    assert G.classify("ksh+prv (AI, D-085).") == "AI_DELEGATED_D085"
    assert G.classify("Claude (reversible).") == "AI_AGENT_PROVISIONAL"
    assert G.classify("Kush and Parv (Parv relayed by Kush).") == "HUMAN"
    assert G.classify(None) == "NO_APPROVER_LINE"


def test_committed_section_is_current():
    assert G.main(["--check"]) == 0
