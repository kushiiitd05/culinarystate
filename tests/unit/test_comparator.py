from culinarystate.decision.comparator import compare, summarise
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i, rf, group, status="MEASURED"):
    d = {"status": status, "value": rf, "unit": "fraction"} if status == "MEASURED" else \
        {"status": "CENSORED", "unit": "fraction", "censor": {"kind": "GT_CAP", "limit": rf}}
    return Hit(f"E{i}", 0.5, 1.0, {"vector": {}, "score": 0.5, "hard_mismatch": False},
               {"id": f"E{i}", "independence_group": group, "derived": {"retention_factor": d}})


def _p(hits, cls="DIRECT"):
    return EvidencePacket("q", Query(), cls, hits if cls == "DIRECT" else [], hits if cls != "DIRECT" else [])


def test_summary_uses_group_medians_and_flags_censoring():
    s = summarise(_p([_hit(1, 0.5, "A"), _hit(2, 0.7, "A"), _hit(3, 0.4, "B"), _hit(4, 0.975, "C", "CENSORED")]))
    assert (s["n_rows"], s["n_groups"]) == (4, 3)
    assert s["low"] == 0.4 and s["high"] == 0.975 and s["censored_share"] == 0.25


def test_separated_options_are_ordered():
    a = _p([_hit(1, 0.9, "A"), _hit(2, 0.85, "B")])
    b = _p([_hit(3, 0.4, "A"), _hit(4, 0.5, "B")])
    c = compare({"steam": a, "boil": b})
    assert c["verdict"] == "SEPARATED" and c["order"] == ["steam", "boil"]


def test_overlapping_ranges_are_not_ordered():
    c = compare({"steam": _p([_hit(1, 0.6, "A"), _hit(2, 0.8, "B")]), "boil": _p([_hit(3, 0.7, "A"), _hit(4, 0.5, "B")])})
    assert c["verdict"] == "OVERLAPPING" and c["order"] is None


def test_single_source_or_missing_option_is_insufficient():
    c = compare({"steam": _p([_hit(1, 0.9, "A")]), "boil": _p([_hit(2, 0.2, "A"), _hit(3, 0.3, "B")])})
    assert c["verdict"] == "INSUFFICIENT" and "steam" in c["insufficient"]
    assert compare({"steam": _p([], "UNSUPPORTED"), "boil": _p([_hit(2, 0.2, "A"), _hit(3, 0.3, "B")])})["verdict"] == "INSUFFICIENT"


def test_near_evidence_comparison_is_marked_interpolated():
    c = compare({"steam": _p([_hit(1, 0.9, "A"), _hit(2, 0.85, "B")], "INTERPOLATED"),
                 "boil": _p([_hit(3, 0.4, "A"), _hit(4, 0.5, "B")])})
    assert c["basis"] == "INCLUDES_NEAR_EVIDENCE"
