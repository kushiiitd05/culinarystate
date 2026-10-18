from culinarystate.generation.enforce import VERSION, enforce, number_cap
from culinarystate.generation.prompts import b5f_prompt
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i, rf):
    row = {"id": f"EVD-00000{i}", "independence_group": "G", "matrix": {"raw_name": "broccoli"}, "process": {},
           "target": {"raw_name": "Vitamin C"}, "derived": {"retention_factor": {"status": "MEASURED", "value": rf},
                                                          "direction": "DECREASE"}}
    return Hit(row["id"], 0.8, 1.0, {}, row)


PK = {"boil": EvidencePacket("q", Query(), "DIRECT", [_hit(1, 0.55), _hit(2, 0.62)], [])}
ANS = {"mode": "ANSWER", "route": "PROCESS_EFFECT", "precision": "INTERVAL"}


def test_supported_sentences_kept_unsupported_dropped_with_reasons():
    r = enforce("Boiling keeps 0.55 [EVD-000001]. Potatoes keep 75%. See [EVD-999999].", ANS, PK)
    assert r["text"] == "Boiling keeps 0.55 [EVD-000001]." and r["version"] == VERSION and not r["fallback"]
    assert [x["reason"] for x in r["removed"]] == ["UNSUPPORTED_NUMBER", "FABRICATED_CITATION"]


def test_precision_cap_strips_numbers_and_numeric_brackets():
    d = {**ANS, "precision": "QUALITATIVE"}
    r = enforce("Vitamin C mostly decreases [EVD-000001]. It keeps 0.55 [EVD-000001]. Cook briefly [1].", d, PK)
    assert r["text"] == "Vitamin C mostly decreases [EVD-000001]."
    assert {x["reason"] for x in r["removed"]} == {"PRECISION_CAP", "NON_EVIDENCE_CITATION"}


def test_empty_after_enforcement_falls_back_to_template():
    r = enforce("Roughly 90% is lost.", ANS, PK)
    assert r["fallback"] and "EVD-000001" in r["text"]


def test_number_cap_by_route():
    assert number_cap(ANS) is False and number_cap({**ANS, "precision": "REPORT_CONFLICT"}) is True
    assert number_cap({"mode": "DIAGNOSE", "route": "DIAGNOSIS"}) and number_cap({"mode": "RECOVER", "route": "PROCESS_EFFECT"})
    assert number_cap({"mode": "COMPARE", "per_option": {"a": {"precision": "QUALITATIVE"}, "b": {"precision": "INTERVAL"}}}) is False


def test_facts_prompt_contains_only_fact_lines_and_rules():
    p = b5f_prompt("How much vitamin C does boiled broccoli keep?", ANS, PK)
    assert "EVD-000001" in p and "Do not add" in p and "Facts:" in p and "tier" not in p


def test_malformed_evidence_ids_are_non_evidence_citations():
    r = enforce("Vitamin C decreases [EVD-000001]. Texture changes [EVD-1].", ANS, PK)
    assert r["text"] == "Vitamin C decreases [EVD-000001]." and r["removed"][0]["reason"] == "NON_EVIDENCE_CITATION"


def test_ask_without_a_question_falls_back_to_template():
    d = {"mode": "ASK", "ask_for": ["ingredient"], "route": "CLARIFY"}
    r = enforce("The question is missing an ingredient.", d, {})
    assert r["fallback"] and r["text"] == "Which ingredient do you mean?" and r["mode_fallback"]
