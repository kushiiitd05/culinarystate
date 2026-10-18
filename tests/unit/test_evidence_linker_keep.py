from culinarystate.evidence.linker import keep_linker_fields


def test_rebuild_keeps_linker_and_review_fields():
    prev = {"matrix": {"raw_name": "carrot", "ingredient_id": "ING-1"},
            "process": {"raw_name": "boil", "process_id": "PROC-1", "step_process_ids": ["PROC-1"]},
            "verification": {"status": "AI_PRECHECKED"}}
    rec = {"matrix": {"raw_name": "carrot", "ingredient_id": None}, "process": {"raw_name": "boil", "process_id": None},
           "verification": {"status": "UNVERIFIED"}, "tier": "E3"}
    out = keep_linker_fields(prev, rec)
    assert out["matrix"]["ingredient_id"] == "ING-1" and out["process"]["step_process_ids"] == ["PROC-1"]
    assert out["verification"]["status"] == "AI_PRECHECKED" and out["tier"] == "E3"
    assert keep_linker_fields(None, rec) is rec
