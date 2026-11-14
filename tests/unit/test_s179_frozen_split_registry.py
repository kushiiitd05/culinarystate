"""Frozen registry records exact units without exporting source questions or declaring independence."""
from copy import deepcopy
import json

import pytest

from tools.s179_frozen_split_registry import build_units, summarize, write_new


def sample():
    return [
        {"qid": "SYN-S1", "block": "S1", "recipe_id": "REC-990001", "source_family": "WIKIBOOKS", "question": "PRIVATE TEST TEXT"},
        {"qid": "SYN-S2", "block": "S2", "recipe_id": "REC-990002", "source_family": "GUTENBERG_SEGMENT"},
        {"qid": "SYN-P1", "block": "P1", "ingredient_id": "ING-990001", "process_id": "PROC-990001",
         "target_svars": "SVAR-990001", "gold_evd_ids": "EVD-990001|EVD-990002"},
        {"qid": "SYN-C", "block": "C", "ingredient_id": "ING-990001", "process_id": "PROC-990001",
         "process_id_2": "PROC-990002", "target_svars": "SVAR-990001", "gold_evd_ids": "EVD-990001"},
        {"qid": "SYN-U", "block": "U", "gold_graph_edge_ids": "KGE-990001"},
        {"qid": "SYN-X", "block": "X"},
    ]


def test_units_are_question_free_and_include_ux_and_both_compare_processes():
    rows = sample()
    before = deepcopy(rows)
    units = build_units(rows)
    assert len(units) == len(rows)
    assert "PRIVATE TEST TEXT" not in json.dumps(units)
    assert {u["block"] for u in units} >= {"U", "X"}
    assert "PROC-990002" in next(u["unit_id"] for u in units if u["block"] == "C")
    assert rows == before


def test_overlaps_are_reported_not_silently_dropped():
    rows = sample()
    rows[1]["recipe_id"] = rows[0]["recipe_id"]
    result = summarize(build_units(rows))
    assert result["recipe_overlap_between_blocks"] == {"S1&S2": 1}
    assert result["gold_evd_overlap_between_blocks"] == {"C&P1": 1}


def test_hashes_change_if_a_recipe_assignment_changes():
    a = sample()
    b = deepcopy(a)
    b[0]["recipe_id"] = "REC-999999"
    assert summarize(build_units(a))["unit_assignment_sha256"] != summarize(build_units(b))["unit_assignment_sha256"]


def test_duplicate_qid_is_refused():
    rows = sample()
    with pytest.raises(ValueError, match="duplicate"):
        build_units(rows + rows[:1])


def test_missing_identifier_is_not_filled():
    rows = sample()
    rows[0]["recipe_id"] = ""
    with pytest.raises(ValueError, match="recipe"):
        build_units(rows)


def test_write_refuses_existing_output_without_mutating_it(tmp_path):
    path = tmp_path / "record.json"
    path.write_text("existing")
    with pytest.raises(FileExistsError):
        write_new(path, "changed")
    assert path.read_text() == "existing"
