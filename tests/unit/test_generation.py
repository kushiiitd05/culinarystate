from culinarystate.generation.claims import check_claims
from culinarystate.generation.prompts import b0_prompt, b5_prompt, render_evidence
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i, rf, unit="fraction"):
    row = {"id": f"EVD-00000{i}", "tier": "E3", "independence_group": "G", "source_id": "SRC-000001",
           "matrix": {"raw_name": "broccoli"}, "process": {"raw_name": "boiled", "steps": ["boil"]},
           "target": {"raw_name": "Vitamin C"}, "derived": {"retention_factor": {"status": "MEASURED", "value": rf, "unit": unit},
                                                          "direction": "DECREASE"}}
    return Hit(row["id"], 0.8, 1.0, {"vector": {}, "score": 0.7, "hard_mismatch": False}, row)


PK = EvidencePacket("q", Query(), "DIRECT", [_hit(1, 0.55), _hit(2, 62, "%")], [])


def test_render_lists_ids_values_and_units():
    t = render_evidence(PK)
    assert "[EVD-000001]" in t and "retention 0.55" in t and "[EVD-000002]" in t and "retention 0.62" in t


def test_prompts_carry_mode_precision_and_disallowed_claims():
    p = b5_prompt("How much vitamin C does boiled broccoli keep?", PK, {"mode": "ANSWER", "precision": "INTERVAL"},
                  ["no exact numeric claim for the asked condition"])
    assert "INTERVAL" in p and "no exact numeric claim" in p and "[EVD-000001]" in p and "cite" in p.lower()
    assert "evidence" not in b0_prompt("How much vitamin C does boiled broccoli keep?").lower()


def test_supported_numbers_must_be_cited_and_match():
    ok = check_claims("Boiling keeps about 55% of vitamin C [EVD-000001].", PK)
    assert ok["numeric_claims"] == 1 and ok["unsupported"] == 0 and ok["ucr"] == 0.0
    bad = check_claims("Boiling keeps 90% of vitamin C [EVD-000001].", PK)
    assert bad["unsupported"] == 1 and bad["claims"][0]["reason"] == "VALUE_NOT_IN_CITED_EVIDENCE"


def test_uncited_numbers_and_fabricated_citations_count():
    r = check_claims("Roughly 60% is retained. See also [EVD-999999].", PK)
    assert r["claims"][0]["reason"] == "UNCITED" and r["fabricated_citations"] == ["EVD-999999"]


def test_ranges_and_fractions_are_matched():
    r = check_claims("Retention ranges from 0.55 to 62% [EVD-000001][EVD-000002].", PK)
    assert r["unsupported"] == 0 and r["numeric_claims"] == 2


def test_non_claim_numbers_ignored():
    r = check_claims("Step 2: boil for 5 minutes [EVD-000001].", PK)
    assert r["numeric_claims"] == 0


def test_multiple_ids_in_one_bracket_are_citations():
    r = check_claims("Retention is about 55% [EVD-000001, EVD-000002].", PK)
    assert r["unsupported"] == 0 and r["claims"][0]["cites"] == ["EVD-000001", "EVD-000002"]


def test_citations_after_the_full_stop_attach_to_the_previous_sentence():
    r = check_claims("Boiling keeps about 55% of vitamin C. [EVD-000001]", PK)
    assert r["unsupported"] == 0 and r["claims"][0]["cites"] == ["EVD-000001"]
    r = check_claims("Boiling keeps 55%. It is similar to kale. [EVD-000001]", PK)
    assert r["claims"][0]["reason"] == "UNCITED"                  # only the sentence right before gets the ids
