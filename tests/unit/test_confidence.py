from culinarystate.decision.confidence import confidence_vector, output_precision, sufficiency
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i, direction="DECREASE", tier="E3", group="G1", vec=None, status="UNVERIFIED"):
    v = {"matrix": "MATCH", "state": "UNKNOWN", "process": "MATCH", "time": "UNKNOWN", "temperature": "NEAR",
         "medium": "MATCH", "target": "MATCH", "basis": "UNKNOWN", "tier": tier, **(vec or {})}
    row = {"id": f"EVD-{i}", "tier": tier, "independence_group": group, "derived": {"direction": direction},
           "verification": {"status": status}}
    return Hit(f"EVD-{i}", 0.8, 1.0, {"vector": v, "score": 0.7, "hard_mismatch": False}, row)


def _packet(cls, direct=(), near=(), conflicts=()):
    return EvidencePacket("q", Query(ingredient_id="ING-1"), cls, list(direct), list(near), list(conflicts))


def test_vector_dimensions_keep_unknown_as_none():
    q = confidence_vector(_packet("DIRECT", [_hit(1), _hit(2, group="G2")]))
    assert q["retrieval"] == 0.8 and q["process"] == 1.0 and q["target"] == 1.0 and q["source"] == 0.8
    assert q["condition"] == 0.75                      # medium MATCH 1.0, temperature NEAR 0.5; time UNKNOWN ignored
    assert q["measurement"] is None and q["state"] is None and q["model"] is None and q["ood"] is None
    assert q["agreement"] == 1.0 and q["independent_sources"] == 2 and q["extraction"] == "UNVERIFIED"


def test_agreement_with_conflict_and_empty_packet():
    q = confidence_vector(_packet("CONFLICT", [_hit(1), _hit(2, "INCREASE", group="G2"), _hit(3, group="G3")]))
    assert round(q["agreement"], 3) == 0.667
    e = confidence_vector(_packet("UNSUPPORTED"))
    assert e["retrieval"] == 0.0 and e["agreement"] is None and e["independent_sources"] == 0


def test_sufficiency_and_precision_cap():
    assert sufficiency(_packet("DIRECT", [_hit(1)])) == "DIRECT"
    assert sufficiency(_packet("UNSUPPORTED")) == "NO_EVIDENCE"
    assert sufficiency(_packet("UNSUPPORTED", near=[_hit(1)])) == "IRRELEVANT_EVIDENCE"
    assert output_precision("DIRECT", numeric_target=True) == "QUANTITATIVE"
    assert output_precision("DIRECT", numeric_target=False) == "QUALITATIVE"
    assert output_precision("NEAR_PARTIAL") == "INTERVAL" and output_precision("CONFLICTING") == "REPORT_CONFLICT"
    assert output_precision("NO_EVIDENCE") == "ABSTAIN"
