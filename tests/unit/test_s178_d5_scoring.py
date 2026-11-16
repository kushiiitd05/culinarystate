"""S178 H1H3H: D5 scoring metrics on small hand-computed SYNTHETIC inputs (router, slots, C block, OOD abstention,
decision-mode F1 with zero denominators, citations, enforcement cost, H1, H3 options, audit merge)."""
from __future__ import annotations

import pytest
from scipy.stats import beta

from culinarystate.evaluation import d5_scoring as DS
from culinarystate.evaluation import h3_independent as H3
from culinarystate.evaluation import paired_stats as PS


def cp_ref(x, n):
    lo = 0.0 if x == 0 else beta.ppf(0.025, x, n - x + 1)
    hi = 1.0 if x == n else beta.ppf(0.975, x + 1, n - x)
    return [round(lo, 4), round(hi, 4)]


def R(qid, block, **kw):
    return {"qid": qid, "block": block, **kw}


# ------------------------------------------------------------------ router

def test_router_accuracy_confusion_and_missing_gold():
    rows = [R("q1", "P1", gold_branch="TRANSFORMATION"), R("q2", "X", gold_branch="SAFETY"),
            R("q3", "X", gold_branch="UNKNOWN"), R("q4", "S1", gold_branch="")]
    pred = {"q1": "TRANSFORMATION", "q2": "SAFETY", "q3": "TRANSFORMATION", "q4": "UNKNOWN"}
    r = DS.router_branch_accuracy(rows, pred)
    assert r["status"] == "INCOMPLETE_GOLD_BRANCH" and r["gold_branch_missing"] == ["q4"]
    assert (r["accuracy"]["x"], r["accuracy"]["n"]) == (2, 3) and r["accuracy"]["cp95"] == cp_ref(2, 3)
    assert r["confusion_matrix"]["counts"] == {"SAFETY": {"SAFETY": 1, "TRANSFORMATION": 0},
                                               "TRANSFORMATION": {"SAFETY": 0, "TRANSFORMATION": 1},
                                               "UNKNOWN": {"SAFETY": 0, "TRANSFORMATION": 1}}
    assert r["per_block"]["X"]["x"] == 1 and r["per_block"]["X"]["n"] == 2
    assert r["x_controls"] == {"n": 2, "correct": 1, "pairs": {"SAFETY->SAFETY": 1, "UNKNOWN->TRANSFORMATION": 1}}
    assert r["per_gold_branch_recall"]["UNKNOWN"]["x"] == 0
    assert DS.router_branch_accuracy(rows, {})["accuracy"]["x"] == 0      # no prediction is wrong, never skipped


def test_predicted_branches_must_agree_and_live_router():
    rows = [R("q1", "P1", question="")]
    recs = {"B2": {"q1": {"route": {"branch": "UNKNOWN"}}}, "B7": {"q1": {"route": {"branch": "SAFETY"}}}}
    with pytest.raises(ValueError):
        DS.predicted_branches(rows, recs)
    assert DS.predicted_branches(rows, {"B2": {"q1": {"route": None}}}) == {"q1": None}
    live = DS.live_router_branches([R("q1", "X", question=""), R("q2", "X", question="Here is a photo of my bread")])
    assert live == {"q1": "MALFORMED", "q2": "MULTIMODAL"}


# ------------------------------------------------------------------ slots

def test_slot_accuracy():
    rows = [R("p1", "P1", ingredient_id="I1", process_id="P1", target_svars="S1"),
            R("c1", "C", ingredient_id="I1", process_id="P1", process_id_2="P2", target_svars="S1|S2"),
            R("u1", "U", ingredient_id="I9")]
    recs = {"p1": {"slots": {"ingredient_id": "I1", "process_ids": ["P1"], "target_svar": "S1"}},
            "c1": {"slots": {"ingredient_id": "I2", "process_ids": ["P1"], "target": "vitamin c"}}}
    s = DS.slot_accuracy(rows, recs)["slots"]
    assert (s["ingredient"]["all"]["x"], s["ingredient"]["all"]["n"], s["ingredient"]["all"]["missing_prediction"]) == (1, 3, 1)
    assert (s["process"]["all"]["x"], s["process"]["all"]["n"]) == (1, 2)          # {P1} != {P1, P2}
    t = s["target"]["all"]
    assert (t["x"], t["n"], t["target_name_without_svar"], t["missing_prediction"]) == (1, 2, 1, 0)


# ------------------------------------------------------------------ C block

def test_c_block_gold_derivation_and_scores():
    rows = [R("c1", "C", process_id="PA", process_id_2="PB", gold_retention_range="0.70-0.80 x",
              gold_retention_range_2="0.40-0.50 x"),
            R("c2", "C", process_id="PA", process_id_2="PB", gold_retention_range="0.50-0.70 x",
              gold_retention_range_2="0.60-0.80 x"),
            R("c3", "C", process_id="PA", process_id_2="PB", gold_compare="ARM2_BETTER")]
    assert DS.gold_compare_label(rows[0]) == ("ARM1_BETTER", "DERIVED_FROM_GOLD_RANGES")
    assert DS.gold_compare_label(rows[1]) == ("CANNOT_SEPARATE", "DERIVED_FROM_GOLD_RANGES")
    assert DS.gold_compare_label(rows[2]) == ("ARM2_BETTER", "REVIEWED_GOLD_COMPARE")
    assert DS.gold_compare_label(R("c4", "C")) == (None, "NO_GOLD_COMPARE")
    sep = lambda first: {"mode": "COMPARE", "comparison": {"verdict": "SEPARATED", "order": [first]},   # noqa: E731
                         "per_option": {"a": {"process_id": "PA"}, "b": {"process_id": "PB"}}}
    recs = {"B7": {"c1": {"decision": sep("a")}, "c2": {"decision": {"mode": "COMPARE", "comparison": {"verdict": "OVERLAPPING"}}},
                   "c3": {"decision": sep("a")}},
            "B2": {"c1": {"predicted_compare": "ARM1_BETTER"}, "c2": {"answer": "x"}, "c3": {}}}
    scored = {"B2": {"c2": {"abstained": True}}}
    out = DS.c_block_scores(rows, recs, scored)
    b7 = out["rungs"]["B7"]
    assert (b7["agreement_with_gold"]["x"], b7["agreement_with_gold"]["n"]) == (2, 3)
    assert (b7["cannot_separate_rate"]["x"], b7["wrong_order"]) == (1, 1)
    assert b7["confusion_gold_x_pred"]["ARM2_BETTER"]["ARM1_BETTER"] == 1
    b2 = out["rungs"]["B2"]
    assert (b2["agreement_with_gold"]["x"], b2["abstained"], b2["unresolved"]) == (1, 1, 1)
    assert (b2["agreement_among_resolved"]["x"], b2["agreement_among_resolved"]["n"]) == (1, 1)
    assert out["gold_cannot_separate"]["x"] == 1 and out["gold_origin"] == {"DERIVED_FROM_GOLD_RANGES": 2, "REVIEWED_GOLD_COMPARE": 1}


# ------------------------------------------------------------------ OOD abstention

def test_ood_abstention_recall_false_abstain():
    rows = [R("a", "P3"), R("b", "P3"), R("c", "P1"), R("d", "P2")]
    sc = {"B7": {"a": {"abstained": True}, "b": {"abstained": True}, "c": {"abstained": False}, "d": {"abstained": True}}}
    recs = {"B7": {"a": {"decision": {"mode": "ABSTAIN", "ood": True}}, "b": {"decision": {"mode": "ANSWER", "ood": False}},
                   "c": {"decision": {"mode": "ANSWER", "per_option": {"x": {"support": {"ood": False}}}}}, "d": {}}}
    out = DS.ood_abstention(rows, recs, sc)
    e = out["rungs"]["B7"]
    assert (e["abstain_recall_P3"]["x"], e["abstain_recall_P3"]["n"]) == (2, 2)
    assert (e["false_abstain_rate_P1_P2"]["x"], e["false_abstain_rate_P1_P2"]["n"]) == (1, 2)
    assert (e["P1"]["text_abstention"]["x"], e["P2"]["text_abstention"]["x"]) == (0, 1)
    assert (e["P3"]["decision_mode_abstain"]["x"], e["P3"]["decision_mode_abstain"]["n"]) == (1, 2)
    assert (e["P3"]["ood_gate_fired"]["x"], e["P3"]["ood_gate_fired"]["n"]) == (1, 2)
    assert (e["P1+P2"]["ood_gate_fired"]["x"], e["P1+P2"]["ood_gate_fired"]["n"]) == (0, 1)
    assert "by construction" in out["caveat"]


# ------------------------------------------------------------------ decision mode F1

def test_f1_table_hand_computed_with_zero_denominators():
    gold = ["ANSWER", "ANSWER", "ANSWER_SIMILAR_ONLY", "ABSTAIN", "COMPARE"]
    pred = ["ANSWER", "ABSTAIN", "ANSWER", "ABSTAIN", "OTHER:ASK"]
    t = DS.f1_table(gold, pred, DS.GOLD_MODES)
    pc = t["per_class"]
    assert pc["ANSWER"] == {"tp": 1, "fp": 1, "fn": 1, "n_gold": 2, "n_pred": 2, "precision": 0.5, "recall": 0.5, "f1": 0.5}
    assert pc["ANSWER_SIMILAR_ONLY"]["precision"] is None and pc["ANSWER_SIMILAR_ONLY"]["recall"] == 0.0
    assert pc["ANSWER_SIMILAR_ONLY"]["f1"] == 0.0
    assert pc["ABSTAIN"]["f1"] == 0.6667 and pc["ABSTAIN"]["recall"] == 1.0
    assert pc["COMPARE"]["f1"] == 0.0 and pc["COMPARE"]["precision"] is None
    assert t["macro_f1"] == 0.2917 and t["accuracy"]["x"] == 2 and t["n_outside_classes"] == 1
    t2 = DS.f1_table(["ANSWER"], ["ANSWER"], ("ANSWER", "COMPARE"))
    assert t2["per_class"]["COMPARE"]["f1"] is None and t2["classes_excluded_absent_both_sides"] == ["COMPARE"]
    assert t2["macro_f1"] == 1.0
    assert DS.f1_table([], [], ("A",))["macro_f1"] is None


def test_predicted_mode_mapping():
    pm = lambda d: DS.predicted_mode({"decision": d})[0]          # noqa: E731
    assert pm({"mode": "ANSWER", "reason": "DIRECT"}) == "ANSWER"
    assert pm({"mode": "ANSWER", "reason": "NEAR_PARTIAL"}) == "ANSWER_SIMILAR_ONLY"
    assert pm({"mode": "ANSWER", "reason": "BROAD_QUALITATIVE", "evidence_basis": "SIMILAR_ONLY"}) == "ANSWER_SIMILAR_ONLY"
    assert pm({"mode": "ANSWER", "reason": "BROAD_QUALITATIVE"}) == "OTHER:ANSWER_BROAD_QUALITATIVE"
    assert pm({"mode": "ASK"}) == "OTHER:ASK" and pm({"mode": "COMPARE"}) == "COMPARE"
    assert DS.predicted_mode({"answer": "x"}) == (None, "TEXT_ONLY")


def test_mode_f1_text_only_rung_gets_binary_only():
    rows = [R("a", "P1", gold_mode="ANSWER"), R("b", "P3", gold_mode="ABSTAIN")]
    recs = {"B2": {"a": {"answer": "x"}, "b": {"answer": "y"}},
            "B7": {"a": {"decision": {"mode": "ANSWER", "reason": "DIRECT"}}, "b": {"decision": {"mode": "ABSTAIN"}}}}
    sc = {"B2": {"a": {"abstained": False}, "b": {"abstained": False}}, "B7": {"a": {"abstained": False}, "b": {"abstained": True}}}
    out = DS.mode_f1(rows, recs, sc)
    assert out["rungs"]["B2"]["four_class"].startswith("NOT_DEFINED")
    assert out["rungs"]["B2"]["binary_abstain"]["per_class"]["ABSTAIN"]["f1"] == 0.0
    assert out["rungs"]["B7"]["four_class"]["accuracy"]["x"] == 2
    assert out["rungs"]["B7"]["four_class"]["classes_excluded_absent_both_sides"] == ["ANSWER_SIMILAR_ONLY", "COMPARE"]


# ------------------------------------------------------------------ citations, enforcement

def test_citation_metrics_both_readings():
    rows = [R("a", "P1", gold_evd_ids="EVD-990001|EVD-990002")]
    scored = {"B2": {"a": {"claims": [{"verdict": "SUPPORTED", "cites": ["EVD-990001", "EVD-990003"],
                                       "supporting_ids": ["EVD-990001"]},
                                      {"verdict": "UNCITED", "cites": [], "supporting_ids": []}]}}}
    recs = {"B2": {"a": {"answer": "65 % [EVD-990001, EVD-990003]. About half."}}}
    c = DS.citation_metrics(rows, scored, recs)["rungs"]["B2"]
    assert (c["support_based"]["precision"]["x"], c["support_based"]["precision"]["n"]) == (1, 2)
    assert (c["support_based"]["recall"]["x"], c["support_based"]["recall"]["n"]) == (1, 2)
    assert (c["gold_based"]["precision"]["x"], c["gold_based"]["precision"]["n"]) == (1, 2)
    assert (c["gold_based"]["recall"]["x"], c["gold_based"]["recall"]["n"]) == (1, 2)
    empty = DS.citation_metrics(rows, {"B2": {"a": {"claims": []}}}, {"B2": {"a": {"answer": ""}}})["rungs"]["B2"]
    assert empty["support_based"]["precision"]["rate"] is None and empty["gold_based"]["precision"]["rate"] is None


def test_enforcement_cost():
    rows = [R("a", "P1"), R("b", "P3")]
    recs = {"B7": {"a": {"answer": "a b c", "enforce": {"removed": [{"reason": "UNSUPPORTED_NUMBER"}, {"reason": "PRECISION_CAP"}],
                                                        "fallback": False, "mode_fallback": False}},
                   "b": {"answer": "a b", "enforce": {"removed": [], "fallback": True, "mode_fallback": True}}},
            "B2": {"a": {"answer": "one"}}}
    out = DS.enforcement_cost(rows, recs, {"B7": {"coverage_answerable": {"x": 1, "n": 1}}})["rungs"]
    e = out["B7"]
    assert e["sentences_removed"] == 2 and e["removed_by_reason"] == {"PRECISION_CAP": 1, "UNSUPPORTED_NUMBER": 1}
    assert e["answers_with_removal"] == 1 and (e["template_fallback"]["x"], e["template_fallback"]["n"]) == (1, 2)
    assert e["mode_fallback"] == 1 and e["words"] == {"mean": 2.5, "median": 2.5} and e["characters_mean"] == 4.0
    assert e["coverage_answerable"] == {"x": 1, "n": 1}
    assert out["B2"]["enforcement"].startswith("NA")


# ------------------------------------------------------------------ H1

def s_rows(n=6):
    return [R(f"s{i}", "S1" if i < 3 else "S2", gold_origin="HUMAN_BLIND") for i in range(n)]


def outcomes(rung_vals):
    return {rung: {f"s{i}": {"s_outcome": v} for i, v in enumerate(vals)} for rung, vals in rung_vals.items()}


def test_h1_mcnemar_hand_computed():
    rows = s_rows()
    recs = outcomes({"B4": [True] * 6, "B1": [False] * 6, "B2": [True, False, False, False, False, True]})
    out = DS.h1_analysis(rows, recs)
    c1 = out["comparisons"]["B4_vs_B1"]["pooled"]
    assert (c1["a_both"], c1["b_treatment_only"], c1["c_control_only"], c1["d_neither"]) == (0, 6, 0, 0)
    assert c1["p_exact_two_sided"] == pytest.approx(2 / 64)
    lo, hi = PS.newcombe_paired(0, 6, 0, 0)
    assert c1["newcombe95_descriptive"] == [round(lo, 4), round(hi, 4)] and c1["diff"] == 1.0
    c2 = out["comparisons"]["B4_vs_B2"]["pooled"]
    assert (c2["b_treatment_only"], c2["c_control_only"]) == (4, 0) and c2["p_exact_two_sided"] == pytest.approx(2 / 16)
    assert c2["realised"]["statement"] == "cannot be significant at this n: 4 discordant pairs < 6"
    assert out["comparisons"]["B4_vs_B1"]["treatment_better_and_significant"] is True
    assert out["verdict"]["code"] == "RULE_NOT_MET" and out["verdict"]["wording_amendment_C5"] == "not shown at this n"
    assert out["verdict"]["gold_label"] == "INDEPENDENT_GOLD"
    assert out["accuracy"]["B2"]["all"]["x"] == 2 and out["accuracy"]["B2"]["S1"]["x"] == 1
    recs2 = outcomes({"B4": [True] * 6, "B1": [False] * 6, "B2": [False] * 6})
    assert DS.h1_analysis(rows, recs2)["verdict"]["code"] == "RULE_MET"


def test_h1_unresolved_blocks_and_engine_gold_label():
    rows = [{**r, "gold_origin": "ENGINE_DRAFT"} for r in s_rows()]
    recs = outcomes({"B4": [True] * 6, "B1": [False, "UNRESOLVED", False, False, False, False], "B2": [False] * 6})
    out = DS.h1_analysis(rows, recs)
    assert out["comparisons"]["B4_vs_B1"]["status"] == "BLOCKED_UNRESOLVED_OR_MISSING"
    assert out["verdict"]["code"] == "NOT_COMPUTED" and out["verdict"]["wording_base"] is None
    assert out["accuracy"]["B1"]["unresolved"] == 1 and out["accuracy"]["B1"]["all"]["n"] == 5
    assert out["verdict"]["gold_label"] == "CIRCULAR_SELF_CONSISTENCY_ONLY"


# ------------------------------------------------------------------ H3

def sc(n, u, ab=False):
    return {"n_numeric": n, "n_numeric_unsupported": u, "abstained": ab, "claims": []}


def h3_fixture():
    rows = ([R(f"q{i}", "P1", gold_mode="ANSWER") for i in (1, 2, 3)] + [R(f"q{i}", "P2", gold_mode="ANSWER_SIMILAR_ONLY") for i in (4, 5)]
            + [R("q6", "C", gold_mode="COMPARE")] + [R(f"q{i}", "P3", gold_mode="ABSTAIN") for i in (7, 8)])
    b2 = {**{f"q{i}": sc(1, 1) for i in range(1, 6)}, "q6": sc(2, 0), "q7": sc(1, 1), "q8": sc(0, 0, True)}
    b7 = {**{f"q{i}": sc(1, 0) for i in range(1, 7)}, "q7": sc(0, 0, True), "q8": sc(0, 0, True)}
    return rows, {"B2": b2, "B7": b7, "B5T": dict(b7)}


def test_h3_options_hand_computed():
    rows, scored = h3_fixture()
    out = DS.h3_verdicts(rows, scored, n_boot=500)
    st1 = out["options"]["H3-B|one-sided"]["sign_test"]
    assert (st1["b_worse_only_unsupported"], st1["c_better_only_unsupported"]) == (6, 0)
    assert st1["p"] == pytest.approx(1 / 64) and st1["min_discordant_for_alpha"] == 5 and st1["passes"]
    st2 = out["options"]["H3-B|two-sided"]["sign_test"]
    assert st2["p"] == pytest.approx(2 / 64) and st2["min_discordant_for_alpha"] == 6
    assert out["p3_abstention"]["B2"]["rate"] == 0.5 and out["p3_abstention"]["B7"]["rate"] == 1.0
    assert out["p3_condition_met"] is True
    assert out["options"]["H3-B|one-sided"]["meets_rule"] is True
    assert out["options"]["H3-A|one-sided"]["meets_rule"] == "PENDING_HUMAN_AUDIT"
    assert out["bootstrap_ucr_diff_B7_minus_B2_upper95"] < 0 and out["options"]["H3-C"]["meets_rule"] is True
    assert "by construction" in out["options"]["H3-C"]["caveat"]
    assert out["B5T_vs_B7_descriptive"]["one-sided"]["b_worse_only_unsupported"] == 0
    ok = DS.h3_verdicts(rows, scored, n_boot=50, audit_shares={"B2": {"weighted_unsupported_share": 0.5},
                                                                "B7": {"weighted_unsupported_share": 0.0}})
    assert ok["audit_veto_fires"] is False and ok["options"]["H3-A|one-sided"]["meets_rule"] is True
    veto = DS.h3_verdicts(rows, scored, n_boot=50, audit_shares={"B2": {"weighted_unsupported_share": 0.5},
                                                                  "B7": {"weighted_unsupported_share": 0.5}})
    assert veto["audit_veto_fires"] is True and veto["options"]["H3-A|one-sided"]["meets_rule"] is False


def test_h3_cannot_be_shown_and_missing_rung():
    rows, scored = h3_fixture()
    for q in ("q4", "q5"):
        scored["B2"][q] = sc(1, 0)                           # 4 discordant questions left
    out = DS.h3_verdicts(rows, scored, n_boot=50)
    st = out["options"]["H3-B|one-sided"]["sign_test"]
    assert st["statement"] == "cannot be shown at this n: 4 discordant questions < 5" and not st["passes"]
    assert out["options"]["H3-A|one-sided"]["meets_rule"] is False          # sign test fails: no PENDING
    assert DS.h3_verdicts(rows, {"B2": scored["B2"]})["status"].startswith("NOT_COMPUTED")


def test_h3_bootstrap_reuses_paired_stats():
    rows, scored = h3_fixture()
    out = DS.h3_verdicts(rows, scored, n_boot=300, boot_seed="d5-h3")
    q = sorted(scored["B2"])
    t = lambda s: [(s[x]["n_numeric"], s[x]["n_numeric_unsupported"]) for x in q]      # noqa: E731
    assert out["bootstrap_ucr_diff_B7_minus_B2_upper95"] == PS.ucr_diff_upper95(t(scored["B7"]), t(scored["B2"]), n_boot=300)


def test_score_rung_uses_independent_scorer_with_block_relevance():
    evd = {"EVD-990001": {"id": "EVD-990001", "matrix": {"ingredient_id": "ING-990009", "raw_name": "fixturegroup"},
                          "process": {"process_id": "PROC-990001", "steps": ["boil"], "raw_name": "boil"},
                          "target": {"state_variable_id": "SVAR-990001", "raw_name": "Vitamin C"},
                          "derived": {"retention_factor": {"status": "MEASURED", "value": 0.55, "unit": "fraction"}}}}
    base = dict(ingredient_id="ING-990002", food="fixtureleaf", process="boil", process_id="PROC-990001",
                target_svars="SVAR-990001")
    rows = [R("p2", "P2", **base), R("p1", "P1", **base)]
    recs = {"p2": {"answer": "About 55 % is kept [EVD-990001]."}, "p1": {"answer": "About 55 % is kept [EVD-990001]."}}
    out = DS.score_rung(rows, recs, evd, {"ING-990002": ["ING-990009"]})
    assert out["p2"]["claims"][0]["verdict"] == "SUPPORTED"          # P2: SIMILAR (parent row) is enough
    assert out["p1"]["claims"][0]["verdict"] == "WRONG_CELL"         # P1: EXACT required
    assert out["p1"]["version"] == H3.VERSION


# ------------------------------------------------------------------ audit

def test_weighted_human_share_and_audit_report():
    key = [{"audit_id": "AUD-0001", "rung": "B7", "stratum_population": "4", "stratum_sampled": "2",
            "independent_verdict": "SUPPORTED", "checker_flags_answer": "False"},
           {"audit_id": "AUD-0002", "rung": "B7", "stratum_population": "1", "stratum_sampled": "1",
            "independent_verdict": "SUPPORTED", "checker_flags_answer": "False"},
           {"audit_id": "AUD-0003", "rung": "B2", "stratum_population": "1", "stratum_sampled": "1",
            "independent_verdict": "UNCITED", "checker_flags_answer": "True"}]
    lab = lambda s, m: {"claim_supported_by_cited_row": s, "cited_row_matches_question": m}      # noqa: E731
    a = [{"audit_id": "AUD-0001", **lab("NO", "")}, {"audit_id": "AUD-0002", **lab("YES", "RIGHT_CELL")},
         {"audit_id": "AUD-0003", **lab("NO", "NO_CITATION")}]
    b = [dict(x) for x in a]
    rep = DS.audit_report(key, a, b, {"B7": {"ucr": 0.0}, "B2": {"ucr": 0.5}})
    sh = rep["human_weighted_unsupported_share"]
    assert sh["B7"]["weighted_unsupported_share"] == round(2 / 3, 4) and sh["B2"]["weighted_unsupported_share"] == 1.0
    assert sh["B7"]["independent_scorer_ucr"] == 0.0
    assert rep["reviewer_raw_agreement"] == 1.0 and rep["n_agreed"] == 3
    ag = rep["human_vs_automatic_raw_agreement"]["independent"]
    assert (ag["x"], ag["n"]) == (2, 3)                       # AUD-0001: scorer says supported, humans say not
    b[0] = {"audit_id": "AUD-0001", **lab("YES", "RIGHT_CELL")}
    assert DS.audit_report(key, a, b)["disputed"] == ["AUD-0001"]


def test_index_runs_validation():
    with pytest.raises(ValueError):
        DS.index_runs([{"qid": "a", "rung": "B2", "invented_field": 1}])
    with pytest.raises(ValueError):
        DS.index_runs([{"qid": "a", "rung": "B2"}, {"qid": "a", "rung": "B2"}])
    with pytest.raises(ValueError):
        DS.validate_rows([R("a", "P1"), R("a", "P1")])
    with pytest.raises(ValueError):
        DS.validate_rows([R("a", "Z9")])


def test_metric_registry_marks_unregistered_metrics_exploratory():
    for m in ("retrieval_mrr", "slot_accuracy", "decision_mode_f1", "citation_precision_recall",
              "c_block_accuracy_cannot_separate", "d4_selective_risk_50_70_90", "ablation_table", "answer_length"):
        assert DS.METRIC_REGISTRY[m]["prereg"].startswith(DS.EXPLORATORY), m
    assert DS.METRIC_REGISTRY["router_branch_accuracy"]["prereg"].startswith("BASE")


def test_scoring_modules_do_not_import_the_enforcement_checker():
    import ast
    from pathlib import Path
    root = Path(__file__).resolve().parents[2] / "src/culinarystate/evaluation"
    for f in ("d5_scoring.py", "d4_metrics.py", "ablation.py", "frozen_guard.py"):
        mods = {(n.module or "") for n in ast.walk(ast.parse((root / f).read_text())) if isinstance(n, ast.ImportFrom)}
        mods |= {a.name for n in ast.walk(ast.parse((root / f).read_text())) if isinstance(n, ast.Import) for a in n.names}
        assert not any(m.startswith("culinarystate.generation") for m in mods), f


def test_s_outcomes_unresolved_and_human_resolution():
    assert DS.s1_outcome({"correct": False, "link_failed": True}) == "UNRESOLVED"
    assert DS.s1_outcome({"correct": True, "link_failed": False}) is True
    proc = {"boil": "PROC-1", "simmer": "PROC-2"}.get
    assert DS.s2_outcome("Boil the water.", "PROC-1", proc) is True
    assert DS.s2_outcome("simmer", "PROC-1", proc) is False
    assert DS.s2_outcome("blorp it", "PROC-1", proc) == "UNRESOLVED" and DS.s2_outcome("", "PROC-1", proc) is False
    recs = {"B1": {"s0": {"s_outcome": "UNRESOLVED"}, "s1": {"s_outcome": False}}}
    out = DS.apply_human_resolutions(recs, {("s0", "B1"): True})
    assert out["B1"]["s0"]["s_outcome"] is True and recs["B1"]["s0"]["s_outcome"] == "UNRESOLVED"
    with pytest.raises(ValueError):
        DS.apply_human_resolutions(recs, {("s1", "B1"): True})          # a decided item cannot be re-scored
