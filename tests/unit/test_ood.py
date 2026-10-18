from culinarystate.decision.ood import SupportIndex, cap_precision

EVD = [
    {"status": "ACTIVE", "matrix": {"ingredient_id": "ING-1", "raw_name": "carrot"}, "process": {"process_id": "PROC-1"},
     "derived": {"retention_factor": {"status": "MEASURED", "value": 0.8}}},
    {"status": "ACTIVE", "matrix": {"ingredient_id": None, "raw_name": "root vegetables, such as beetroot, parsnip"},
     "process": {"process_id": "PROC-2"}, "derived": {"retention_factor": {"status": "MEASURED", "value": 0.7}}},
    {"status": "ACTIVE", "matrix": {"ingredient_id": "ING-9", "raw_name": "okra"}, "process": {"process_id": "PROC-1"},
     "derived": {"yield_factor": {"status": "MEASURED", "value": 0.9}}},          # yields do not count as retention support
]
IDX = SupportIndex(EVD)


def test_supported_pair_is_not_ood():
    s = IDX.support("ING-1", (), "carrot", "PROC-1")
    assert (s["ingredient"], s["process"], s["pair"], s["ood"]) == (1, 1, 1, False)


def test_group_row_counts_for_named_ingredient():
    s = IDX.support("ING-5", (), "parsnip", "PROC-2")
    assert s["pair"] == 1 and not s["ood"] and s["pair_level"] == "GROUP"


def test_cold_ingredient_is_ood_with_axis_named():
    s = IDX.support("ING-7", (), "kohlrabi", "PROC-1")
    assert s["ood"] and s["cold_axes"] == ["ingredient"] and s["process"] == 1


def test_unknown_slots_are_not_called_cold():
    s = IDX.support(None, (), None, "PROC-1")
    assert s["ood"] is None and s["cold_axes"] == []


def test_precision_cap():
    assert cap_precision("INTERVAL", {"ood": True}) == ("QUALITATIVE", "OOD_SUPPORT_CAP")
    assert cap_precision("QUANTITATIVE", {"ood": False}) == ("QUANTITATIVE", None)
    assert cap_precision("ABSTAIN", {"ood": True}) == ("ABSTAIN", None)


def test_targets_for_pair_counts_evidence_targets():
    idx = SupportIndex([
        {"status": "ACTIVE", "matrix": {"ingredient_id": "ING-1", "raw_name": "carrot"}, "process": {"process_id": "PROC-1"},
         "target": {"raw_name": "beta-Carotene"}, "derived": {"retention_factor": {}}},
        {"status": "ACTIVE", "matrix": {"ingredient_id": "ING-1", "raw_name": "carrot"}, "process": {"process_id": "PROC-1"},
         "target": {"raw_name": "Vitamin C"}, "derived": {"retention_factor": {}}},
        {"status": "ACTIVE", "matrix": {"ingredient_id": "ING-1", "raw_name": "carrot"}, "process": {"process_id": "PROC-1"},
         "target": {"raw_name": "Vitamin C"}, "derived": {"retention_factor": {}}}])
    assert idx.targets_for("ING-1", (), "carrot", "PROC-1") == [("vitamin c", 2), ("beta-carotene", 1)]
    assert idx.targets_for("ING-1", (), "carrot", "PROC-9") == []
