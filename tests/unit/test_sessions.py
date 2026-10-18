import copy

from culinarystate.annotation.sessions import check_session, to_events, validate_session

DOC = {
    "session_id": "SES-T01", "title": "reserve pasta water, then loosen sauce", "scenario": "RESERVE_RECOMBINE",
    "locale": "UK",
    "ingredients": [{"entity": "pasta", "concept": "UNKNOWN", "quantity": "200g pasta"},
                    {"entity": "water", "concept": "UNKNOWN", "quantity": "2 litres water"},
                    {"entity": "sauce", "concept": "UNKNOWN", "quantity": "300ml tomato sauce"}],
    "turns": [
        {"turn": 1, "user": "Pasta is boiling in the water.", "events": [
            {"type": "Merge", "inputs": ["pasta", "water"], "output": "pot", "process": "boil"}]},
        {"turn": 2, "user": "I kept back a quarter of the pot, then drained the rest into the sink.", "events": [
            {"type": "Reserve", "target": "pot", "output": "pasta water", "fraction": "1/4"},
            {"type": "Discard", "target": "pot", "value": "cooking water"}]},
        {"turn": 3, "user": "Sauce looks too thick.", "events": [
            {"type": "Observe", "target": "sauce", "field": "consistency", "value": "too thick"}]},
        {"turn": 4, "user": "Added the pasta water to the sauce.", "events": [
            {"type": "Recombine", "target": "pasta water", "output": "sauce"}]},
    ],
    "expected": {"alive": ["sauce"], "dead": ["pasta water", "pasta", "water"],
                 "fields": {"sauce.consistency": "too thick"},
                 "edges": [["pasta", "MERGES_INTO", "pot"], ["pot", "RESERVED_AS", "pasta water"],
                           ["pasta water", "RECOMBINED_WITH", "sauce"]]},
    "provenance": {"authored_by": "Claude", "status": "AI_DRAFTED", "reviewed_by": None},
}


def test_valid_doc_compiles_and_passes():
    assert validate_session(DOC) == []
    assert len(to_events(DOC)) == 3 + 5
    r = check_session(DOC)
    assert r["pass"], r["failures"]
    assert r["replay"]["deterministic"] and r["checks"] == 1 + 3 + 1 + 3


def test_wrong_expectation_is_reported_not_hidden():
    bad = copy.deepcopy(DOC)
    bad["expected"]["fields"]["sauce.consistency"] = "thin"
    r = check_session(bad)
    assert not r["pass"] and any("sauce.consistency" in f for f in r["failures"])


def test_schema_rejects_unknown_event_and_unreviewed_human_status():
    bad = copy.deepcopy(DOC)
    bad["turns"][0]["events"][0]["type"] = "Teleport"
    assert validate_session(bad)
    bad = copy.deepcopy(DOC)
    bad["provenance"]["status"] = "HUMAN_REVIEWED"            # reviewed needs a reviewer name
    assert any("reviewed_by" in e for e in validate_session(bad))
