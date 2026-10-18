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
