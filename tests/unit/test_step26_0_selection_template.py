"""Step 26.0 system selection record TEMPLATE stays unsigned and undecided (S159).

The 26.0 record transcribes the single 11.D DECISIONS entry (AA, CHL or NEED_DATA) and the pre-registered quotas;
Kush and Parv sign it before any parameter fit (Plan v2 Step 26 card, R-14, D-027). An AI worker prepares the
template only: no choice, no quota value, no evidence count and no signature may appear in it.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD = ROOT / "reports" / "step26" / "system_selection_record_TEMPLATE.md"
JS = ROOT / "reports" / "step26" / "system_selection_record_TEMPLATE.UNSIGNED.json"


def test_json_template_is_unsigned_and_chooses_nothing() -> None:
    rec = json.loads(JS.read_text(encoding="utf-8"))
    assert rec["status"] == "UNSIGNED_TEMPLATE" and rec["counts_as_human_gate"] is False
    assert rec["selection"]["system_id"] is None and rec["selection"]["transcribed_11d_entry"] is None
    assert {c["system_id"] for c in rec["candidates"]} == {"sim_aa_1", "sim_chl_1"}
    assert {c["role"] for c in rec["candidates"]} == {"LEADING_CANDIDATE_D027", "PREREGISTERED_FALLBACK_D027"}
    assert rec["selection"]["allowed_values"] == ["sim_aa_1", "sim_chl_1", "NEED_DATA"]
    for crit in rec["criteria"]:
        assert crit["preregistered_value"] is None and crit["verified_count"] is None
        assert crit["evidence_refs"] == [] and crit["met"] is None
    for s in rec["signatures"]:
        assert s["signed"] is False and s["signed_at"] is None and s["signature_file_sha256"] is None
    assert {s["signer"] for s in rec["signatures"]} == {"Kush Tokas", "Parv Goyal"}
    assert rec["prepared_by"].startswith("AI worker prv")


def test_markdown_template_is_headed_unsigned_and_has_blank_fields() -> None:
    text = MD.read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("# ") and "UNSIGNED" in text.splitlines()[0]
    assert "D-027" in text and "R-14" in text and "11.D" in text
    assert "Selected system: ____" in text
    assert len(text.splitlines()) < 800
