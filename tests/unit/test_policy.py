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
