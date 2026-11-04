"""S157 AI cross-review (worker prv) regression tests for ksh's S157 parts A-C.

AI verdict, pending Kush/Parv review (D-045). Each test pins one finding of
``reports/step09/S157_ai_review.md`` (R1-R4). All documents, values, extractor names and table
layouts are SYNTHETIC fixtures; none is a real measurement or a real Bognar table.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from culinarystate.evidence import machinery as M
from culinarystate.evidence import registration as R
from culinarystate.ingest import bognar_remaining as B

SPAN = "SYNTHETIC Table 9. Analyte Q in test food Z: 12.5 mg/100 g after 5 min at 90 °C."


def _prop(raw: str, extractor: str, kind: str = "AI_MODEL") -> M.Proposal:
    loc = M.Locator(document_id="DOC-SYNTH-0009", kind="SPAN", char_start=0, char_end=len(SPAN))
    return M.Proposal(field_class="numeric_value", raw_value=raw, extractor_id=extractor, extractor_kind=kind,
                      locator=loc)


def _blind_confirm(tmp: Path, item: M.QueueItem, reviewer: str = "Kush") -> M.QueueItem:
    p = tmp / "review.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(M.REVIEW_SHEET_COLUMNS))
        w.writeheader()
        w.writerow({"queue_item_id": item.queue_item_id, "human_decision": "CONFIRM", "reviewer": reviewer,
                    "reviewed_at": "2026-11-03", "review_mode": "INDEPENDENT_BLIND", "seen_model_output": "false",
                    "checked_locator": "Table 9 row 1", "minutes": "2"})
    reviews, errors = M.read_human_reviews(p)
    assert not errors
    return item.with_human_review(reviews[item.queue_item_id])


# ---------------------------------------------------------------- R1: extractor family is case-insensitive
def test_r1_same_extractor_in_two_casings_is_not_dual_extraction(tmp_path: Path) -> None:
    it = M.QueueItem.build([_prop("12.5", "ai:synthetic-model-x@1"), _prop("12.5", "AI:Synthetic-Model-X@2")],
                           span_text=SPAN)
    done = _blind_confirm(tmp_path, it)
    assert done.verification_status == "HUMAN_VERIFIED"
    assert done.evidence_tier_candidate == "E5"


def test_r1_distinct_families_still_eligible(tmp_path: Path) -> None:
    it = M.QueueItem.build([_prop("12.5", "ai:synthetic-model-x@1"), _prop("12.5", "ai:synthetic-model-y@1")],
                           span_text=SPAN)
    assert _blind_confirm(tmp_path, it).evidence_tier_candidate == "E4_ELIGIBLE_PENDING_ADJ"


# ---------------------------------------------------------------- R2: the confirming human did not extract it
def test_r2_human_extractor_cannot_be_the_blind_confirmer(tmp_path: Path) -> None:
    it = M.QueueItem.build([_prop("12.5", "Kush", kind="HUMAN_EXTRACTOR"), _prop("12.5", "ai:synthetic-model-x@1")],
                           span_text=SPAN)
    assert _blind_confirm(tmp_path, it, reviewer="Kush").evidence_tier_candidate == "E5"
    assert _blind_confirm(tmp_path, it, reviewer="Parv").evidence_tier_candidate == "E4_ELIGIBLE_PENDING_ADJ"


# ---------------------------------------------------------------- R3: licence mapping never upgrades a qualified status
@pytest.mark.parametrize("raw,mapped", [
    ("VERIFIED_AT_INGESTION; re-check failed (synthetic TLS error); search found no terms page", "UNKNOWN"),
    ("VERIFIED_PENDING_RECHECK", "UNKNOWN"),
    ("VERIFIED_AT_INGESTION", "VERIFIED"),
    ("VERIFIED", "VERIFIED"),
    ("RESTRICTIVE_AGREEMENT", "RESTRICTED"),
])
def test_r3_licence_mapping_is_literal(raw: str, mapped: str) -> None:
    assert R.map_licence_status(raw) == mapped


# ---------------------------------------------------------------- R4: every sub-variant mark line is kept raw
def _at(*pairs: tuple[int, str]) -> str:
    out = ""
    for col, tok in pairs:
        out = out.ljust(col) + tok
    return out


def test_r4_stacked_mark_lines_are_all_preserved() -> None:
    lines = ["Part 2 : Average retention factors of food constituents",
             "Table 35: Retention factors by cooking of synthetic group",
             _at((25, "Retention factor")),
             _at((0, "Constituentss"), (22, "boil")),
             _at((22, "a)")),
             _at((40, "boil")),
             _at((40, "b)")),
             _at((22, "A"), (40, "A")),
             _at((0, "Vitamin C"), (21, "0.70"), (39, "0.80"))]
    res = B.parse_remaining("\n".join(lines) + "\n", tables=(35,))
    cells = res.cells
    assert [c["sub_variant_raw"] for c in cells] == ["a)", "b)"]
    assert "a)" in cells[0]["column_header_raw"] and "b)" in cells[1]["column_header_raw"]
