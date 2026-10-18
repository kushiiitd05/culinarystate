from culinarystate.decision.policy import decide
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i):
    v = {"matrix": "MATCH", "state": "UNKNOWN", "process": "MATCH", "time": "UNKNOWN", "temperature": "UNKNOWN",
         "medium": "UNKNOWN", "target": "MATCH", "basis": "UNKNOWN", "tier": "E3"}
    return Hit(f"EVD-{i}", 0.8, 1.0, {"vector": v, "score": 0.7, "hard_mismatch": False},
               {"id": f"EVD-{i}", "tier": "E3", "independence_group": "G", "derived": {"direction": "DECREASE"}})


def _p(cls, hits=()):
    return EvidencePacket("q", Query(ingredient_id="ING-1"), cls, list(hits) if cls == "DIRECT" else [],
                          list(hits) if cls != "DIRECT" else [])


SLOTS = {"ingredient": "ING-1", "process": "PROC-1"}


def test_low_relevance_skips_process_reasoning():
    d = decide("What is the next instruction?", {}, SLOTS)
    assert d["mode"] == "ANSWER" and d["route"] == "RECIPE_STATE"


def test_direct_evidence_answers_quantitatively():
    d = decide("How much vitamin C does boiled broccoli keep?", {"main": _p("DIRECT", [_hit(1)])}, SLOTS)
    assert (d["mode"], d["precision"], d["route"]) == ("ANSWER", "QUANTITATIVE", "PROCESS_EFFECT")


def test_missing_critical_slot_asks():
    d = decide("Will microwaving produce the same texture?", {}, {"ingredient": None, "process": "PROC-2"})
    assert d["mode"] == "ASK" and d["ask_for"] == ["ingredient"]


def test_unsupported_abstains_and_conflict_is_reported():
    assert decide("How much folate does fried okra keep?", {"main": _p("UNSUPPORTED")}, SLOTS)["mode"] == "ABSTAIN"
    d = decide("How much folate does fried okra keep?", {"main": _p("CONFLICT", [_hit(1)])}, SLOTS)
    assert d["mode"] == "ANSWER" and d["precision"] == "REPORT_CONFLICT"


def test_compare_needs_evidence_for_each_side():
    d = decide("What changes if I roast instead of steam?", {"roast": _p("DIRECT", [_hit(1)]), "steam": _p("UNSUPPORTED")}, SLOTS)
    assert d["mode"] == "COMPARE" and d["per_option"]["steam"]["precision"] == "ABSTAIN"
    assert decide("roast vs steam?", {"roast": _p("UNSUPPORTED"), "steam": _p("UNSUPPORTED")}, SLOTS)["mode"] == "ABSTAIN"


def test_recommend_filters_infeasible_before_ranking_and_keeps_alternatives():
    feas = {"bake": {"decision": "REJECT", "checks": {}}, "steam": {"decision": "ALLOW", "checks": {}},
            "boil": {"decision": "ALLOW", "checks": {}}}
    pk = {"bake": _p("DIRECT", [_hit(1)]), "steam": _p("INTERPOLATED", [_hit(2)]), "boil": _p("UNSUPPORTED")}
    d = decide("How should I cook spinach to keep vitamin C?", pk, SLOTS, feasibility=feas)
    assert d["mode"] == "RECOMMEND" and d["alternatives"] == ["steam", "boil"] and d["rejected"] == ["bake"]
    none = {k: {"decision": "REJECT", "checks": {}} for k in feas}
    assert decide("How should I cook spinach to keep vitamin C?", pk, SLOTS, feasibility=none)["reason"] == "NO_FEASIBLE_ACTION"


def test_diagnosis_language_is_qualified():
    d = decide("Why did my sauce split?", {"main": _p("QUALITATIVE", [_hit(1)])}, SLOTS)
    assert d["mode"] == "DIAGNOSE" and d["causal_language"] == "QUALIFIED"


def test_recover_reports_cause_evidence_and_unknown_recoverability():
    d = decide("I accidentally boiled it too long; how can I recover?", {"boil": _p("CONFLICT", [_hit(1)])}, SLOTS)
    assert d["mode"] == "RECOVER" and d["recoverability"] == "UNKNOWN" and d["recovery_options"] == []
    assert d["cause_evidence"]["boil"]["precision"] == "REPORT_CONFLICT" and d["causal_language"] == "QUALIFIED"


def test_ood_support_caps_numeric_precision():
    sup = {"main": {"ood": True, "cold_axes": ["ingredient"]}}
    d = decide("How much vitamin C does boiled kohlrabi keep?", {"main": _p("INTERPOLATED", [_hit(1)])}, SLOTS, support=sup)
    assert d["precision"] == "QUALITATIVE" and d["per_option"]["main"]["cap"] == "OOD_SUPPORT_CAP"
    assert d["per_option"]["main"]["confidence"]["ood"] is True


def test_process_effect_answer_without_target_asks_for_it():
    d = decide("What happens when I boil broccoli?", {"main": _p("DIRECT", [_hit(1)])},
               {**SLOTS, "target": None, "needs_target": True})
    assert d["mode"] == "ASK" and d["ask_for"] == ["target"]


def test_contradictory_slots_ask():
    d = decide("boiled and not boiled broccoli vitamin C?", {"main": _p("DIRECT", [_hit(1)])},
               {**SLOTS, "contradictions": ["PROC-1"]})
    assert d["mode"] == "ASK" and d["reason"] == "CONTRADICTORY_SLOTS"


def test_compare_includes_outcome_comparison():
    d = decide("What changes if I roast instead of steam?", {"roast": _p("DIRECT", [_hit(1)]), "steam": _p("DIRECT", [_hit(2)])}, SLOTS)
    assert d["mode"] == "COMPARE" and d["comparison"]["verdict"] in {"SEPARATED", "OVERLAPPING", "INSUFFICIENT"}


def test_voi_target_missing_no_options_abstains_one_option_answers_many_asks():
    base = {**SLOTS, "target": None, "needs_target": True}
    pk = {"main": _p("DIRECT", [_hit(1)])}
    assert decide("What happens when I boil broccoli?", pk, {**base, "target_options": []})["reason"] == "NO_EVIDENCE_FOR_ANY_TARGET"
    d = decide("What happens when I boil broccoli?", pk, {**base, "target_options": ["vitamin c", "folate", "calcium"]})
    assert d["mode"] == "ASK" and d["ask_options"] == ["vitamin c", "folate", "calcium"]


DIAG = {"failure": "CURDLE", "causes": [{"cause": "boiled", "verdict": "CONSISTENT", "support_sources": 2}],
        "recovery": [{"action": "begin again with a fresh yolk", "support_sources": 2}], "prevention": [],
        "next_observations": [], "recoverability": "UNKNOWN", "causal_language": "QUALIFIED"}


def test_diagnose_uses_symptom_without_process_slot():
    d = decide("Why did my custard curdle?", {}, {"ingredient": None, "process": None}, diagnosis=DIAG)
    assert d["mode"] == "DIAGNOSE" and d["diagnosis"]["causes"][0]["cause"] == "boiled"
    assert d["causal_language"] == "QUALIFIED"


def test_recover_takes_options_from_recovery_index():
    d = decide("It curdled, how can I recover?", {}, {"ingredient": None, "process": None}, diagnosis=DIAG)
    assert d["mode"] == "RECOVER" and d["recovery_options"] == ["begin again with a fresh yolk"]
    assert d["recoverability"] == "UNKNOWN"


def test_diagnose_without_candidates_abstains():
    empty = {**DIAG, "causes": [], "recovery": []}
    assert decide("Why did my custard curdle?", {}, {"ingredient": None, "process": None}, diagnosis=empty)["mode"] == "ABSTAIN"


def test_out_of_scope_requests_abstain():
    from culinarystate.decision.policy import decide
    d = decide("Tell me a joke about pasta.", {}, {})
    assert d["mode"] == "ABSTAIN" and d["route"] == "OUT_OF_SCOPE" and d["reason"] == "OUT_OF_SCOPE"
