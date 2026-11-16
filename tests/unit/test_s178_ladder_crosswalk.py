"""S178 T6-C02-R1: the transition ladder crosswalk agrees with the code and the 29-diag prereg text.

Reads registry/transition_ladder_crosswalk_v1.csv, src/culinarystate/transition/baselines.py (no fit, so no
scikit-learn needed), evaluation/diag29_runner._key and bakeoff.LADDER_RUNGS, and the 29-diag prereg draft text.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XW = ROOT / "registry/transition_ladder_crosswalk_v1.csv"
PREREG = ROOT / "reports/step29/29diag_preregistration_DRAFT.md"
COLS = ["xw_id", "tbv0_rung", "ssot_d_rung", "code_class", "code_model_name", "runner_key", "step30_rung",
        "ssot_m_rung", "what_it_computes", "match_status", "prereg_draft_label", "prereg_label_status",
        "fix_or_note", "evidence"]


def _rows():
    with XW.open(newline="") as fh:
        return list(csv.DictReader(fh))


def test_header_and_unique_ids():
    rows = _rows()
    assert list(rows[0].keys()) == COLS
    ids = [r["xw_id"] for r in rows]
    assert len(ids) == len(set(ids))


def test_every_model_in_all_models_is_mapped_with_its_runner_key():
    from culinarystate.evaluation.diag29_runner import _key
    from culinarystate.transition.baselines import all_models

    by_class = {r["code_class"]: r for r in _rows() if r["match_status"] in {"EXACT", "VARIANT"}}
    for m in all_models():
        row = by_class.get(type(m).__name__)
        assert row is not None, f"{type(m).__name__} missing from the crosswalk"
        assert row["code_model_name"] == m.name
        assert row["runner_key"] == _key(m.name)


def test_d3_is_never_mapped_to_b2_and_b2_is_not_implemented():
    from culinarystate.transition import baselines

    rows = _rows()
    for r in rows:
        if r["code_class"] == "D3Hierarchical":
            assert r["tbv0_rung"] != "B-2"
    b2 = [r for r in rows if r["tbv0_rung"] == "B-2"]
    assert len(b2) == 1
    has_b2_class = any(n.startswith("B2") for n in dir(baselines))
    assert (b2[0]["match_status"] != "NOT_IMPLEMENTED") == has_b2_class


def test_m_ladder_m0_to_m11_each_present_once():
    ms = [r["ssot_m_rung"] for r in _rows() if r["ssot_m_rung"]]
    assert sorted(ms, key=lambda x: int(x[1:])) == [f"M{i}" for i in range(12)]


def test_step30_rung_names_are_all_covered():
    from culinarystate.evaluation.bakeoff import LADDER_RUNGS

    covered = set()
    for r in _rows():
        covered |= {t.strip() for t in r["step30_rung"].split(";") if t.strip()}
    missing = [x for x in LADDER_RUNGS if x not in covered]
    assert missing == [], missing


def test_prereg_draft_label_status_matches_the_prereg_text():
    text = PREREG.read_text()
    row = next(r for r in _rows() if r["code_class"] == "D3Hierarchical")
    still_wrong = "D3 = B-2" in text
    assert (row["prereg_label_status"] == "MISMATCH") == still_wrong
