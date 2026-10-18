from culinarystate.generation.claims import check_claims
from culinarystate.generation.verbalize import VERSION, facts, verbalize
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i, rf, name="cabbage", unit="fraction", direction="DECREASE", status="MEASURED"):
    rfv = {"status": status, "value": rf, "unit": unit} if status == "MEASURED" else {"status": status}
    row = {"id": f"EVD-00000{i}", "tier": "E3", "independence_group": f"G{i}", "matrix": {"raw_name": name},
           "process": {"raw_name": "boiled"}, "target": {"raw_name": "Vitamin C"},
           "derived": {"retention_factor": rfv, "direction": direction}}
    return Hit(row["id"], 0.8, 1.0, {}, row)


DIRECT = EvidencePacket("q", Query(), "DIRECT", [_hit(1, 0.55, "broccoli"), _hit(2, 0.62, "broccoli")], [])
NEAR = EvidencePacket("q", Query(), "INTERPOLATED", [], [_hit(3, 0.6), _hit(4, 70, "potato", "%")])
EMPTY = EvidencePacket("q", Query(), "UNSUPPORTED")


def _ans(prec):
    return {"mode": "ANSWER", "route": "PROCESS_EFFECT", "precision": prec}


def test_direct_interval_is_cited_and_passes_checker():
    t = verbalize("q", _ans("INTERVAL"), {"boil": DIRECT})
    assert "0.55" in t and "0.62" in t and "EVD-000001" in t and "EVD-000002" in t
    assert check_claims(t, DIRECT)["unsupported"] == 0


def test_near_evidence_is_labelled_similar_and_names_foods():
    t = verbalize("q", _ans("INTERVAL"), {"boil": NEAR})
    assert "similar" in t.lower() and "cabbage" in t and "potato" in t
    assert check_claims(t, NEAR)["unsupported"] == 0 and check_claims(t, NEAR)["numeric_claims"] == 2


def test_qualitative_cap_gives_direction_without_numbers():
    t = verbalize("q", _ans("QUALITATIVE"), {"boil": NEAR})
    assert check_claims(t, NEAR)["numeric_claims"] == 0 and "decrease" in t.lower() and "EVD-000003" in t


def test_conflict_reports_disagreement_without_numbers():
    pk = EvidencePacket("q", Query(), "CONFLICT", [_hit(1, 0.5), _hit(2, 1.4, direction="INCREASE")], [])
    t = verbalize("q", _ans("REPORT_CONFLICT"), {"boil": pk})
    assert "disagree" in t.lower() and check_claims(t, pk)["numeric_claims"] == 0


def test_ask_abstain_and_recipe_state_routes():
    assert "?" in verbalize("q", {"mode": "ASK", "ask_for": ["ingredient"]}, {})
    assert "potato" in verbalize("q", {"mode": "ASK", "ask_for": ["target"], "ask_options": ["potato"]}, {})
    assert "not enough evidence" in verbalize("q", {"mode": "ABSTAIN", "reason": "INSUFFICIENT_EVIDENCE"}, {}).lower()
    assert "recipe session" in verbalize("q", {"mode": "ANSWER", "route": "RECIPE_STATE"}, {}).lower()


def test_diagnosis_and_recovery_use_candidates_not_rows():
    dg = {"failure": "CURDLE", "causes": [{"cause": "boiled", "support_sources": 2, "verdict": "CONSISTENT"}],
          "recovery": [{"action": "beat in cold milk", "support_sources": 4}], "prevention": []}
    t = verbalize("q", {"mode": "DIAGNOSE", "route": "DIAGNOSIS", "diagnosis": dg}, {})
    assert "boiled" in t and "2 sources" in t and "consistent with your steps" in t and "may" in t
    r = verbalize("q", {"mode": "RECOVER", "route": "DIAGNOSIS", "diagnosis": dg, "recovery_options": ["beat in cold milk"]}, {})
    assert "beat in cold milk" in r and "boiled" not in r


def test_recover_without_recovery_evidence_does_not_narrate_cause_numbers():
    d = {"mode": "RECOVER", "route": "PROCESS_EFFECT", "recovery_options": [],
         "cause_evidence": {"boil": {"precision": "REPORT_CONFLICT"}}}
    t = verbalize("q", d, {"boil": DIRECT})
    assert "no recovery evidence" in t.lower() and check_claims(t, DIRECT)["numeric_claims"] == 0


def test_compare_and_recommend_per_option():
    d = {"mode": "COMPARE", "route": "PROCESS_EFFECT", "comparison": {"verdict": "OVERLAPPING"},
         "per_option": {"steam": {"precision": "INTERVAL"}, "boil": {"precision": "INTERVAL"}}}
    t = verbalize("q", d, {"steam": NEAR, "boil": DIRECT})
    assert "steam" in t and "boil" in t and "overlap" in t.lower()
    assert all(check_claims(s, DIRECT if "boil" in s else NEAR)["unsupported"] == 0 for s in t.split("\n"))
    d = {"mode": "RECOMMEND", "route": "PROCESS_EFFECT", "alternatives": ["steam"], "per_option": {"steam": {"precision": "QUALITATIVE"}}}
    assert check_claims(verbalize("q", d, {"steam": NEAR}), NEAR)["numeric_claims"] == 0


def test_facts_are_versioned_and_empty_packet_is_unknown():
    f = facts({"mode": "ANSWER", "route": "PROCESS_EFFECT", "precision": "INTERVAL"}, {"boil": EMPTY})
    assert f["version"] == VERSION and f["lines"] == ["boil: UNKNOWN — no evidence rows."]


def test_censored_limits_are_not_printed_as_values():
    h = _hit(5, None, status="CENSORED")
    h.row["derived"]["retention_factor"] = {"status": "CENSORED", "censor": {"kind": "GT_STATED", "limit": 0.9}}
    pk = EvidencePacket("q", Query(), "DIRECT", [h], [])
    assert "0.90" not in verbalize("q", _ans("INTERVAL"), {"boil": pk})


def test_food_labels_are_short_and_case_normalised():
    pk = EvidencePacket("q", Query(), "INTERPOLATED", [], [
        _hit(1, 0.6, "stem, flower, fruit, corn and seed vegetables, such as asparagus, broccoli, Brussels sprouts"),
        _hit(2, 0.7, "POTATOES"), _hit(3, 0.7, "leafy vegetables -, such as boiled, stewed red cabbage")])
    t = verbalize("q", _ans("INTERVAL"), {"boil": pk})
    assert "such as" not in t and "potatoes" in t and "POTATOES" not in t and "leafy vegetables)" in t.replace(" -", "")


def test_prevention_prefers_short_statements():
    dg = {"failure": "CURDLE", "causes": [{"cause": "boiled", "support_sources": 2, "verdict": "UNVERIFIABLE"}],
          "prevention": [{"action": "Boil gently for 1-1/2 hour, and, at the moment of serving, beat in the yolks of "
                                    "the eggs and the vinegar, but do not let it boil", "support_sources": 3},
                         {"action": "do not let it boil", "support_sources": 2}]}
    t = verbalize("q", {"mode": "DIAGNOSE", "route": "DIAGNOSIS", "diagnosis": dg}, {})
    assert "do not let it boil" in t and "1-1/2 hour" not in t
