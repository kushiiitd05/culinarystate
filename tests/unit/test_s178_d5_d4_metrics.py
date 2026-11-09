"""S178 H1H3H: D4 metrics (Recall@K, condition-compatible Recall@K, MRR, bootstrap, risk-coverage, selective risk)
on small hand-computed SYNTHETIC inputs; no ECE / Brier."""
from __future__ import annotations

import hashlib
import math
import random

import pytest
from scipy.stats import beta

from culinarystate.evaluation import d4_metrics as D4

M = {"matrix": "MATCH", "process": "MATCH", "target": "MATCH", "time": "UNKNOWN", "temperature": "UNKNOWN", "medium": "UNKNOWN"}


def test_compat_ok_rules():
    assert D4.compat_ok(M)
    assert D4.compat_ok({**M, "matrix": "NEAR", "time": "UNKNOWN"})            # NEAR / UNKNOWN are not mismatches
    assert D4.compat_ok({**M, "state": "MISMATCH"})                             # state is not a listed axis
    for a in D4.COMPAT_AXES:
        assert not D4.compat_ok({**M, a: "MISMATCH"})
    assert not D4.compat_ok(None) and not D4.compat_ok({})


def test_recall_compat_recall_rr_hand_computed():
    gold, ranked = ["a", "b"], ["x", "a", "y", "b"]
    assert [D4.recall_at_k(gold, ranked, k) for k in (1, 3, 5)] == [0.0, 0.5, 1.0]
    vec = {"a": M, "b": {**M, "time": "MISMATCH"}}
    assert D4.compat_recall_at_k(gold, ranked, 5, vec) == 0.5
    assert D4.compat_recall_at_k(gold, ranked, 5, {"a": M}) == 0.5              # no vector for b: not credited
    assert D4.reciprocal_rank(gold, ranked) == 0.5 and D4.reciprocal_rank(gold, ["z"]) == 0.0
    assert D4.all_gold_in_top_k(gold, ranked, 3) is False and D4.all_gold_in_top_k(gold, ranked, 4) is True
    assert D4.recall_at_k([], ranked, 3) is None and D4.reciprocal_rank([], ranked) is None


def test_question_retrieval_c_arms_are_averaged():
    row = {"qid": "c", "block": "C", "gold_evd_ids": "a|b", "gold_evd_ids_2": "c"}
    rec = {"retrieval": {"arm1": ["a", "b"], "arm2": ["a", "c"]}, "gold_compat": {"a": M, "b": M, "c": M}}
    q = D4.question_retrieval(row, rec)
    assert q["recall@1"] == pytest.approx((0.5 + 0.0) / 2) and q["recall@3"] == 1.0
    assert q["rr"] == pytest.approx((1.0 + 0.5) / 2) and q["n_arms"] == 2 and q["states_condition"] is False
    assert D4.question_retrieval(row, {"retrieval": {"arm1": ["a"]}}) is None               # arm2 list missing
    assert D4.question_retrieval({"qid": "p3", "block": "P3"}, rec) is None                 # no gold
    assert D4.question_retrieval(row, {**rec, "gold_compat": {"a": {**M, "time": "MATCH"}}})["states_condition"] is True


def test_bootstrap_matches_independent_reimplementation():
    vals = [0.0, 0.5, 1.0, 1.0, 0.25]
    out = D4.bootstrap_mean_ci(vals, seed="s", n_boot=400)
    rng = random.Random(int(hashlib.sha256(b"s").hexdigest(), 16))
    means = sorted(sum(vals[rng.randrange(5)] for _ in range(5)) / 5 for _ in range(400))
    assert out["boot95"] == [round(means[math.ceil(0.025 * 400) - 1], 4), round(means[math.ceil(0.975 * 400) - 1], 4)]
    assert out["mean"] == 0.55 and out["n"] == 5
    assert D4.bootstrap_mean_ci([0.7] * 4, n_boot=50)["boot95"] == [0.7, 0.7]
    assert D4.bootstrap_mean_ci([], n_boot=50)["mean"] is None
    assert D4.N_BOOT == 10_000 and D4.BOOT_SEED == "d5-d4-recall"


def test_cp_matches_scipy():
    for x, n in ((0, 10), (5, 10), (10, 10), (1, 7), (3, 30)):
        lo = 0.0 if x == 0 else beta.ppf(0.025, x, n - x + 1)
        hi = 1.0 if x == n else beta.ppf(0.975, x + 1, n - x)
        assert D4.cp(x, n)["cp95"] == [round(lo, 4), round(hi, 4)]
    assert D4.cp(0, 0) == {"x": 0, "n": 0, "rate": None, "cp95": None}


def test_retrieval_table_na_p3_and_family():
    rows = [{"qid": "p1", "block": "P1", "gold_evd_ids": "a"}, {"qid": "p3", "block": "P3"},
            {"qid": "p3b", "block": "P3"}]
    recs = {"B0": {"p1": {"answer": "x"}, "p3": {}},
            "B2": {"p1": {"retrieval": {"arm1": ["a"]}, "gold_compat": {"a": M}}, "p3": {"retrieval": {"arm1": ["z"]}},
                   "p3b": {"retrieval": {"arm1": []}}}}
    out = D4.retrieval_table(rows, recs, {"a": {"source_family_id": "FAM-A"}}, n_boot=20)
    assert out["rungs"]["B0"]["status"] == "NA_NO_RETRIEVAL_LIST"
    b2 = out["rungs"]["B2"]
    assert b2["blocks"]["P1"]["K=1"]["recall"]["mean"] == 1.0
    assert b2["blocks"]["P1"]["note"].startswith("no question states")
    assert (b2["p3_returned_evidence_anyway"]["x"], b2["p3_returned_evidence_anyway"]["n"]) == (1, 2)
    assert list(b2["source_disjoint_diagnostic"]["families"]) == ["FAM-A"]
    assert b2["blocks"]["P2"]["n_questions"] == 0 and b2["blocks"]["P2"]["K=1"]["recall"]["mean"] is None
    assert b2["blocks"]["pooled_P1_P2_C"]["mrr"]["prereg_status"] == D4.EXPLORATORY


def test_gold_source_family():
    evd = {"a": {"source_family_id": "F1"}, "b": {"source_family_id": "F2"}}
    assert D4.gold_source_family({"block": "P1", "gold_evd_ids": "a"}, evd) == "F1"
    assert D4.gold_source_family({"block": "C", "gold_evd_ids": "a", "gold_evd_ids_2": "b"}, evd) == "MIXED"
    assert D4.gold_source_family({"block": "P3"}, evd) == "NO_GOLD_ROW"


def scored(bad=False, abstained=False, value=None):
    claims = [{"verdict": "VALUE_MISMATCH" if bad else "SUPPORTED", "kind": "NUMERIC", "value": value}] if (bad or value) else []
    return {"claims": claims, "abstained": abstained}


def test_question_error_e1_e2():
    row = {"gold_mode": "ANSWER", "gold_retention_range": "0.60-0.70 fraction retained (n=2)"}
    assert D4.question_error(row, scored(value=0.9)) == 0
    assert D4.question_error(row, scored(value=0.9), option="E2") == 1
    assert D4.question_error(row, scored(value=0.65), option="E2") == 0
    assert D4.question_error(row, scored(bad=True)) == 1
    assert D4.question_error({"gold_mode": "ABSTAIN"}, scored()) == 1
    assert D4.question_error({"gold_mode": "ABSTAIN"}, scored(abstained=True)) == 0
    assert D4.question_error(row, {"claims": [{"verdict": "UNCITED", "kind": "DIRECTION_UNCITED"}], "abstained": False}) == 1
    with pytest.raises(ValueError):
        D4.question_error(row, scored(), option="E3")
    assert D4.parse_gold_range("") is None and D4.parse_gold_range("0.8-0.6 x") == (0.6, 0.8)


def test_score_level_rules():
    assert D4.score_level({"decision": {"mode": "ANSWER", "precision": "INTERVAL"}}) == ("INTERVAL", "DECISION_FIELD")
    assert D4.score_level({"decision": {"mode": "ABSTAIN", "precision": "QUANTITATIVE"}})[0] == "ABSTAIN"
    assert D4.score_level({"decision": {"mode": "ASK"}}) == ("ABSTAIN", "MODE_ASK")
    cmp_ = {"decision": {"mode": "COMPARE", "per_option": {"a": {"precision": "QUANTITATIVE", "sufficiency": "DIRECT"},
                                                           "b": {"precision": "QUALITATIVE", "sufficiency": "NEAR_PARTIAL"}}}}
    assert D4.score_level(cmp_) == ("QUALITATIVE", "COMPARE_MIN_OVER_OPTIONS")
    assert D4.score_level(cmp_, order=D4.SECONDARY_ORDER)[0] == "NEAR_PARTIAL"
    assert D4.score_level({"decision": {"mode": "ABSTAIN", "sufficiency": "IRRELEVANT_EVIDENCE"}},
                          order=D4.SECONDARY_ORDER) == ("IRRELEVANT_EVIDENCE", "DECISION_FIELD")
    assert D4.score_level({}) == ("ABSTAIN", "LEVEL_MISSING")


def test_risk_coverage_and_selective_risk_hand_computed():
    rows = [{"qid": f"q{i}", "block": b, "gold_mode": g} for i, (b, g) in
            enumerate([("P1", "ANSWER"), ("P1", "ANSWER"), ("P2", "ANSWER_SIMILAR_ONLY"), ("C", "COMPARE"), ("P3", "ABSTAIN")], 1)]
    lv = ["QUANTITATIVE", "QUANTITATIVE", "INTERVAL", "QUALITATIVE"]
    recs = {f"q{i}": {"decision": {"mode": "ANSWER", "precision": p}} for i, p in enumerate(lv, 1)}
    recs["q5"] = {"decision": {"mode": "ABSTAIN"}}
    sc = {"q1": scored(), "q2": scored(bad=True), "q3": scored(), "q4": scored(), "q5": scored(abstained=True)}
    curve = D4.risk_coverage(rows, recs, sc)
    pts = [(p["threshold"], p["answered"], p["coverage"], p["risk"]["x"], p["risk"]["n"]) for p in curve["points"]]
    assert pts == [("QUANTITATIVE", 2, 0.4, 1, 2), ("INTERVAL", 3, 0.6, 1, 3), ("QUALITATIVE", 4, 0.8, 1, 4),
                   ("ABSTAIN", 5, 1.0, 1, 5)]                                  # no REPORT_CONFLICT point (absent level)
    sr = D4.selective_risk_at_coverage(curve)["targets"]
    assert (sr["50%"]["threshold"], sr["50%"]["x"], sr["50%"]["n"]) == ("INTERVAL", 1, 3)
    assert (sr["70%"]["threshold"], sr["70%"]["achieved_coverage"]) == ("QUALITATIVE", 0.8)
    assert (sr["90%"]["threshold"], sr["90%"]["n"]) == ("ABSTAIN", 5)
    assert curve["all_answered_risk"]["x"] == 1 and curve["all_answered_risk"]["n"] == 5
    sc["q5"] = scored()                                                          # P3 not abstained -> error
    assert D4.risk_coverage(rows, recs, sc)["points"][-1]["risk"]["x"] == 2
    assert D4.all_answered_risk(rows, sc)["x"] == 2
    assert D4.risk_coverage(rows, {}, sc)["missing_questions"] == [f"q{i}" for i in range(1, 6)]


def test_abstention_precision_recall():
    rows = [{"qid": "a", "block": "P3", "gold_mode": "ABSTAIN"}, {"qid": "b", "block": "P1", "gold_mode": "ANSWER"},
            {"qid": "c", "block": "P3", "gold_mode": "ABSTAIN"}]
    sc = {"a": {"abstained": True}, "b": {"abstained": True}, "c": {"abstained": False}}
    out = D4.abstention_precision_recall(rows, sc)
    assert (out["precision"]["x"], out["precision"]["n"]) == (1, 2) and (out["recall"]["x"], out["recall"]["n"]) == (1, 2)


def test_no_ece_or_brier():
    names = [n.lower() for n in dir(D4)]
    assert not any("ece" == n or "brier" in n or "auroc" in n or "reliability" in n for n in names)
    assert {"ECE", "Brier score", "AUROC"} <= set(D4.NOT_REPORTED)
