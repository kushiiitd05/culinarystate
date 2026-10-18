from culinarystate.retrieval.bm25 import BM25, tokenize
from culinarystate.retrieval.compatibility import Query, compatibility


def test_bm25_ranks_relevant_first():
    docs = ["spinach boiled vitamin c retention", "potato fried acrylamide", "carrot boiled carotene"]
    bm = BM25(docs)
    assert bm.top("vitamin C in boiled spinach", 1)[0][0] == 0
    assert bm.top("acrylamide fries potatoes", 1)[0][0] == 1
    assert tokenize("Potatoes") == tokenize("potatoe") and tokenize("berries") == ["berry"]   # plural-insensitive


def _evd(ing="ING-1", pid="PROC-1", tgt="Vitamin C", basis="FRESH_WEIGHT", tier="E3"):
    return {"matrix": {"ingredient_id": ing, "food_group": "Vegetables", "initial_state": "raw"},
            "process": {"process_id": pid, "step_process_ids": [pid], "medium": "water"},
            "target": {"raw_name": tgt, "basis": basis}, "tier": tier}


FAM = {"PROC-1": "WET_HEAT", "PROC-2": "WET_HEAT", "PROC-3": "FAT_HEAT"}


def test_unknown_is_not_mismatch():
    r = compatibility(Query(ingredient_id="ING-1", process_id="PROC-1", target="vitamin c"), _evd(), None, FAM)
    assert r["vector"]["time"] == "UNKNOWN" and not r["hard_mismatch"]


def test_near_process_family_and_mismatch():
    near = compatibility(Query(ingredient_id="ING-1", process_id="PROC-2", target="vitamin c"), _evd(), None, FAM)
    far = compatibility(Query(ingredient_id="ING-1", process_id="PROC-3", target="vitamin c"), _evd(), None, FAM)
    assert near["vector"]["process"] == "NEAR" and far["vector"]["process"] == "MISMATCH"
    assert near["score"] > far["score"] and far["hard_mismatch"]


def test_parent_concept_is_near():
    r = compatibility(Query(ingredient_id="ING-9", ingredient_parents=frozenset({"ING-1"}), process_id="PROC-1"),
                      _evd(), None, FAM)
    assert r["vector"]["matrix"] == "NEAR"


def test_time_interval_axis():
    cond = {"duration": {"status": "MEASURED", "value": 10, "unit": "min"}}
    assert compatibility(Query(time_min=(8, 12)), _evd(), cond, FAM)["vector"]["time"] == "MATCH"
    assert compatibility(Query(time_min=(60, 90)), _evd(), cond, FAM)["vector"]["time"] == "MISMATCH"


def test_packet_classes():
    from culinarystate.retrieval.retriever import EvidenceRetriever
    def row(i, ing, pid, d, rf):
        e = _evd(ing=ing, pid=pid)
        e.update({"id": f"EVD-{i:06d}", "status": "ACTIVE", "source_id": "SRC-000001", "independence_group": f"g{i}",
                  "derived": {"direction": d, "retention_factor": {"status": "MEASURED", "value": rf}}})
        e["matrix"]["raw_name"], e["process"]["raw_name"], e["process"]["steps"] = "spinach", "boil", ["boil"]
        return e
    r = EvidenceRetriever([row(1, "ING-1", "PROC-1", "DECREASE", 0.6)], {}, FAM)
    assert r.packet("vitamin c boiled spinach", Query(ingredient_id="ING-1", process_id="PROC-1", target="vitamin c")).evidence_class == "DIRECT"
    assert r.packet("vitamin c fried spinach", Query(ingredient_id="ING-1", process_id="PROC-3", target="vitamin c")).evidence_class == "UNSUPPORTED"
    r2 = EvidenceRetriever([row(1, "ING-1", "PROC-1", "DECREASE", 0.6), row(2, "ING-1", "PROC-1", "INCREASE", 1.2)], {}, FAM)
    assert r2.packet("vitamin c boiled spinach", Query(ingredient_id="ING-1", process_id="PROC-1", target="vitamin c")).evidence_class == "CONFLICT"


def test_ingredient_named_in_group_description_is_near():
    e = {"matrix": {"ingredient_id": None, "raw_name": "stem, flower and seed vegetables, such as broccoli, cauliflower",
                    "food_group": "vegetables"},
         "process": {"process_id": "PROC-1", "step_process_ids": ["PROC-1"]}, "target": {"raw_name": "Vitamin C"}, "tier": "E3"}
    r = compatibility(Query(ingredient_id="ING-1", ingredient_name="broccoli", process_id="PROC-1"), e, None, FAM)
    assert r["vector"]["matrix"] == "NEAR"
    r = compatibility(Query(ingredient_id="ING-1", ingredient_name="pea", process_id="PROC-1"), e, None, FAM)
    assert r["vector"]["matrix"] == "UNKNOWN"                                      # whole words only ("peas" ≠ "pea" here)


def test_r4_relations_give_near_with_categorical_match_type():
    from culinarystate.retrieval.compatibility import Query as Q, compatibility as C
    e = {"matrix": {"ingredient_id": "ING-2", "raw_name": "chard"}, "process": {"process_id": "PROC-1"},
         "target": {"raw_name": "Folate"}, "tier": "E3"}
    q = Q(ingredient_id="ING-1", process_id="PROC-1", target="folate", ingredient_relations=(("ING-2", "SIBLING"),))
    c = C(q, e, None, {})
    assert c["vector"]["matrix"] == "NEAR" and c["match"] == {"matrix": "SIBLING", "process": "EXACT"}
    assert C(Q(ingredient_id="ING-1", process_id="PROC-1"), e, None, {})["match"]["matrix"] == "NONE"


def test_unlinked_food_rows_are_broad_qualitative_not_near():
    from culinarystate.retrieval.retriever import EvidenceRetriever
    e = {"id": "EVD-000009", "status": "ACTIVE", "source_id": "SRC-000001", "independence_group": "g9", "tier": "E3",
         "matrix": {"ingredient_id": None, "raw_name": "SHELLFISH"},
         "process": {"process_id": "PROC-1", "step_process_ids": ["PROC-1"], "raw_name": "boil", "steps": ["boil"]},
         "target": {"raw_name": "Vitamin C"},
         "derived": {"direction": "DECREASE", "retention_factor": {"status": "MEASURED", "value": 0.7}}}
    r = EvidenceRetriever([e], {}, FAM)
    pk = r.packet("vitamin c boiled carrot", Query(ingredient_id="ING-5", ingredient_name="carrot", process_id="PROC-1",
                                                   target="vitamin c"))
    assert pk.evidence_class == "QUALITATIVE" and [h.evd_id for h in pk.near] == ["EVD-000009"]
    assert any("matrix: UNKNOWN" in d for d in pk.condition_differences)
    pk = r.packet("vitamin c boiled", Query(process_id="PROC-1", target="vitamin c"))      # no food asked
    assert pk.evidence_class == "INTERPOLATED"
