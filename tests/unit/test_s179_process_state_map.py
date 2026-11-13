"""D-100 Lane T: process -> state-change map over recipe progression (counts only)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("psm", ROOT / "tools" / "s179_process_state_map.py")
psm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(psm)

REC = {"recipe_id": "T1", "source_family": "WIKIBOOKS", "ingredient_lines": ["1 cup flour", "1 cup sugar"],
       "steps": ["Mix the flour and sugar in a bowl.", "Bake for 20 minutes.", "Divide the cake in half."]}


def test_tally_one_recipe_counts_types_positions_and_bigrams():
    t = psm.tally_records([REC])
    assert t["n_recipes"] == 1 and t["n_events"] >= 3 and t["exceptions"] == 0
    fam = t["by_family"]["WIKIBOOKS"]
    assert fam["Merge"] >= 1
    assert sum(t["position_type"][d][k] for d in t["position_type"] for k in t["position_type"][d]) == t["n_events"]
    assert sum(t["type_bigrams"].values()) == t["n_events"] - 1
    assert any(k.startswith("PROC-") for k in t["proc_type"])


def test_merge_combines_counters():
    a, b = psm.tally_records([REC]), psm.tally_records([REC])
    m = psm.merge([a, b])
    assert m["n_recipes"] == 2 and m["n_events"] == 2 * a["n_events"]
    assert m["by_family"]["WIKIBOOKS"]["Merge"] == 2 * a["by_family"]["WIKIBOOKS"]["Merge"]


def test_bad_record_is_counted_not_raised():
    t = psm.tally_records([{"recipe_id": "X", "source_family": "WIKIBOOKS", "ingredient_lines": [], "steps": None}])
    assert t["n_recipes"] == 1 and t["n_events"] == 0


def test_decile_bounds():
    assert psm.decile(0, 1) == 0 and psm.decile(9, 10) == 9 and psm.decile(4, 10) == 4
