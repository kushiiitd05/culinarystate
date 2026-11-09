"""S178 / T8-C12-R1: human claim-audit sample generator (stratified, seeded, rung-blind) and checker-quality estimate."""
from __future__ import annotations

import csv
import hashlib

import pytest

from culinarystate.evaluation import claim_audit as CA
from culinarystate.evaluation import h3_independent as H3


def evd_row(i, rf):
    return {"id": f"EVD-{i:06d}", "matrix": {"ingredient_id": "ING-1", "raw_name": "broccoli"},
            "process": {"process_id": "PROC-19", "steps": ["boil"], "raw_name": "boil"},
            "target": {"state_variable_id": "SVAR-9", "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": "MEASURED", "value": rf, "unit": "fraction"}}}


EVD = {r["id"]: r for r in [evd_row(1, 0.65), evd_row(2, 0.40)]}
CELL = {"ingredient_ids": ["ING-1"], "process_ids": ["PROC-19"], "target_svars": ["SVAR-9"]}   # S178 FIX-EVAL E4: cell given


def make_answers():
    """B2: mixed; B5T: all supported; B7: all supported by the independent scorer, but half wrong-cell-free."""
    texts = {
        "B2": ["Keeps 65% [EVD-000001].", "Keeps 50% [EVD-000001].", "Keeps 65%.", "Keeps 40% [EVD-000002]."],
        "B5T": ["Keeps 0.65 [EVD-000001].", "Keeps 0.40 [EVD-000002]."],
        "B7": ["Keeps 65% [EVD-000001].", "Keeps 40% [EVD-000002]."],
    }
    out = []
    for rung, ts in texts.items():
        for n, t in enumerate(ts):
            sc = H3.score_answer(t, evd=EVD, cell=CELL)
            out.append({"qid": f"Q{n}", "rung": rung, "question": "How much vitamin C does boiled broccoli keep?",
                        "answer": t, "scored": sc, "checker_unsupported": 0 if rung == "B7" else sc["n_numeric_unsupported"]})
    return out


def test_items_carry_strata_from_both_scorers():
    items = CA.audit_items(make_answers())
    by = {(i["rung"], i["qid"]): i for i in items}
    assert by[("B2", "Q1")]["stratum"] == "INDEP_UNSUPPORTED|CHECKER_FLAGGED"
    assert by[("B2", "Q0")]["stratum"] == "INDEP_SUPPORTED|CHECKER_CLEAN"
    assert all(i["item_id"].startswith("ITM-") and len(i["item_id"]) == 20 for i in items)
    assert len({i["item_id"] for i in items}) == len(items)


def test_stratified_sample_is_seeded_and_prefers_disagreement_strata():
    items = CA.audit_items(make_answers())
    items += [dict(items[0], item_id=f"ITM-X{n:03d}", rung="B7", independent_verdict="WRONG_CELL", independent_unsupported=True,
                   checker_flags_answer=False, stratum="INDEP_UNSUPPORTED|CHECKER_CLEAN") for n in range(10)]
    s1 = CA.stratified_audit_sample(items, per_rung=4, seed="s178")
    s2 = CA.stratified_audit_sample(items, per_rung=4, seed="s178")
    assert [i["item_id"] for i in s1["sample"]] == [i["item_id"] for i in s2["sample"]]
    s3 = CA.stratified_audit_sample(items, per_rung=4, seed="other")
    assert s1["seed_sha256"] != s3["seed_sha256"]
    b7 = [i for i in s1["sample"] if i["rung"] == "B7"]
    assert len(b7) == 4
    d7 = s1["design"]["B7"]
    assert d7["INDEP_UNSUPPORTED|CHECKER_CLEAN"]["population"] == 10 and d7["INDEP_UNSUPPORTED|CHECKER_CLEAN"]["sampled"] == 2
    assert d7["INDEP_SUPPORTED|CHECKER_CLEAN"]["sampled"] == 2                       # equal shares of non-empty strata
    assert d7["INDEP_UNSUPPORTED|CHECKER_CLEAN"]["weight"] == 5.0
    assert d7["INDEP_SUPPORTED|CHECKER_FLAGGED"]["population"] == 0 and d7["INDEP_SUPPORTED|CHECKER_FLAGGED"]["weight"] is None
    assert s1["shortfalls"] == [{"rung": "B5T", "requested": 4, "available": 2}]    # only 2 B5T claims exist


def test_shortfall_is_reported_and_all_items_taken():
    items = CA.audit_items(make_answers())
    s = CA.stratified_audit_sample(items, per_rung=50, seed="s178")
    assert {x["rung"] for x in s["shortfalls"]} == {"B2", "B5T", "B7"}
    assert len([i for i in s["sample"] if i["rung"] == "B2"]) == 4
    with pytest.raises(ValueError):
        CA.stratified_audit_sample(items, per_rung=0, seed="s")


def test_sheets_are_rung_blind_identical_and_key_is_separate(tmp_path):
    items = CA.audit_items(make_answers())
    s = CA.stratified_audit_sample(items, per_rung=3, seed="s178")
    rep = CA.write_audit_files(s["sample"], EVD, tmp_path, seed="s178")
    assert rep["n_items"] == 7 and set(rep["paths"]) == {"Kush", "Parv", "key"}
    rows = {w: list(csv.DictReader(open(rep["paths"][w], newline="", encoding="utf-8-sig"))) for w in ("Kush", "Parv")}
    assert [r["audit_id"] for r in rows["Kush"]] == [r["audit_id"] for r in rows["Parv"]]
    assert {r["reviewer"] for r in rows["Kush"]} == {"Kush"} and {r["reviewer"] for r in rows["Parv"]} == {"Parv"}
    for col in rows["Kush"][0]:
        assert col not in ("rung", "qid", "independent_verdict", "stratum", "checker_flags_answer")
    blob = open(rep["paths"]["Kush"], encoding="utf-8-sig").read()
    assert "B7" not in blob and "INDEP_" not in blob and "VALUE_MISMATCH" not in blob and "UNCITED" not in blob
    assert "EVD-000001 | broccoli | boil | Vitamin C | retention 0.65 (MEASURED)" in blob
    key = list(csv.DictReader(open(rep["paths"]["key"], newline="", encoding="utf-8")))
    assert {k["rung"] for k in key} == {"B2", "B5T", "B7"} and len(key) == 7
    assert rep["sha256"]["Kush"] == hashlib.sha256(open(rep["paths"]["Kush"], "rb").read()).hexdigest()
    order = [k["rung"] for k in key]
    assert order != sorted(order)                                                    # shuffled across rungs
    with pytest.raises(FileExistsError):
        CA.write_audit_files(s["sample"], EVD, tmp_path, seed="s178")                # never overwrites


def test_human_label_rules_and_reviewer_merge():
    assert CA.human_unsupported("YES", "RIGHT_CELL") is False
    assert CA.human_unsupported("YES", "SIMILAR") is False
    assert CA.human_unsupported("YES", "WRONG_CELL") is True
    assert CA.human_unsupported("NO", "") is True and CA.human_unsupported("PARTLY", "RIGHT_CELL") is True
    assert CA.human_unsupported("CANNOT_TELL", "") is None and CA.human_unsupported("", "") is None
    assert CA.human_unsupported("YES", "MAYBE") is None
    a = [{"audit_id": "A1", "claim_supported_by_cited_row": "YES", "cited_row_matches_question": "RIGHT_CELL"},
         {"audit_id": "A2", "claim_supported_by_cited_row": "NO", "cited_row_matches_question": ""},
         {"audit_id": "A3", "claim_supported_by_cited_row": "YES", "cited_row_matches_question": ""},
         {"audit_id": "A4", "claim_supported_by_cited_row": "", "cited_row_matches_question": ""}]
    b = [{"audit_id": "A1", "claim_supported_by_cited_row": "YES", "cited_row_matches_question": ""},
         {"audit_id": "A2", "claim_supported_by_cited_row": "NO", "cited_row_matches_question": ""},
         {"audit_id": "A3", "claim_supported_by_cited_row": "NO", "cited_row_matches_question": ""},
         {"audit_id": "A4", "claim_supported_by_cited_row": "YES", "cited_row_matches_question": ""}]
    m = CA.merge_reviewer_labels(a, b)
    assert m["agreed"] == {"A1": False, "A2": True} and m["disputed"] == ["A3"] and m["unusable"] == ["A4"]
    assert m["raw_agreement"] == pytest.approx(2 / 3, abs=1e-3)


def test_estimate_checker_quality_weights_by_stratum():
    key = []
    # stratum S_u (independent unsupported, checker clean): population 10, sampled 2 -> weight 5
    # stratum S_s (independent supported, checker clean): population 90, sampled 2 -> weight 45
    for n in range(2):
        key.append({"audit_id": f"U{n}", "rung": "B7", "independent_verdict": "WRONG_CELL", "checker_flags_answer": "False",
                    "stratum_population": 10, "stratum_sampled": 2})
        key.append({"audit_id": f"S{n}", "rung": "B7", "independent_verdict": "SUPPORTED", "checker_flags_answer": "False",
                    "stratum_population": 90, "stratum_sampled": 2})
    labels = {"U0": True, "U1": True, "S0": False, "S1": True}                       # humans agree with 2 of 2, miss 1 of 2
    est = CA.estimate_checker_quality(key, labels)
    ind, chk = est["pooled"]["independent"], est["pooled"]["s173_checker"]
    # independent: flagged U0,U1 (TP weight 5 each = 10); S1 is an FN (weight 45); S0 TN (45)
    assert ind["precision"] == 1.0 and ind["recall"] == pytest.approx(10 / 55, abs=1e-4)
    assert ind["raw_counts"] == {"tp": 2, "fp": 0, "fn": 1, "tn": 1}
    assert chk["precision"] is None and chk["recall"] == 0.0                         # the S173 checker flagged nothing
    assert est["n_labelled"] == 4 and "B7" in est["rungs"]
