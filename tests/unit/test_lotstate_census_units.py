from collections import Counter

from culinarystate.lotstate import census as CS
from culinarystate.lotstate.units_check import units_check
from culinarystate.quantity import rc2_dryrun as D


def fc(rid, parts, q):
    return {"recipe_id": f"FC{rid}", "source_family": "FOODCOM", "ingredient_lines": [],
            "extra": {"ingredient_parts": parts, "q_raw": q, "q_len": len(q), "p_len": len(parts)}}


def test_units_check_confirms_when_no_unit_token_and_reports_length_mismatch():
    recs = [fc(1, ["sugar", "butter", "garlic cloves"], ["1⁄4", "2", "3"]),
            fc(2, ["flour", "salt"], ["1", None, "2"]),                       # q longer than p: not paired
            {"recipe_id": "WB1", "source_family": "WIKIBOOKS", "ingredient_lines": ["100 g flour", "2 cups sugar", "3 eggs"]}]
    rep = units_check(recs)
    f = rep["foodcom"]
    assert f["recipes"] == 2 and f["recipes_q_len_equal_p_len"] == 1 and f["recipes_q_len_greater_than_p_len"] == 1
    assert f["quantity_strings_with_unit_token"] == 0 and f["quantity_strings_with_ascii_letters"] == 0
    assert f["quantity_strings_numeric_only"] == 5 and f["quantity_strings_missing"] == 1
    assert f["paired_lines"] == 3 and f["paired_lines_bare_number_no_unit"] == 3
    assert f.get("paired_lines_with_stated_mass", 0) == 0
    assert f["parts_with_count_or_package_unit_token"] >= 1                   # "garlic cloves": a unit word inside the part
    assert rep["verdict"] == "CONFIRMED_UNITS_ABSENT"
    assert rep["contrast_other_sources"]["WIKIBOOKS_lines_with_stated_mass"] == 1
    assert rep["contrast_other_sources"]["WIKIBOOKS_lines_bare_number_no_unit"] == 1
    D.assert_counts_only(rep)


def test_units_check_not_confirmed_when_units_present():
    recs = [fc(i, ["sugar"], ["100 g"]) for i in range(10)]
    rep = units_check(recs)
    assert rep["verdict"] != "CONFIRMED_UNITS_ABSENT"


def test_tally_and_summary_are_counts_only():
    line = {"source_family": "WIKIBOOKS", "link": "LINKED", "sr_band": "HIGH", "basis": "STATED_MASS", "reason": "STATED_MASS",
            "grams_low": 1.0, "grams_high": 1.0, "ambiguous": False}
    lot = {"source_family": "WIKIBOOKS", "kind": "RECIPE_POOL", "is_leaf": True, "members": [{"ing_id": "ING-1", "sr_band": "HIGH", "mass_g": [1, 1]}],
           "composition": {"kind": "INTERVAL_EXACT_BOUNDS", "match_floor": "HIGH",
                           "nutrients": {"water": {"type": "POINT"}}},
           "solute_load": {"salt_g_per_g_water": {"type": "UNKNOWN", "reason": "X"}, "sugar_g_per_g_water": {"type": "POINT"}},
           "water_activity": {"type": "UNKNOWN"},
           "ph": {"mask": 0, "flags": {"CONTAINS_ACID_MEMBER": "UNKNOWN", "CONTAINS_ALKALINE_MEMBER": "UNKNOWN",
                                       "ALL_MEMBERS_ACID": "UNKNOWN"}}}
    out = {"stats": {"graph_attempted": 0, "graph_failed": 0, "replay_status": "NONE", "foodcom_qp_mismatch": 0},
           "lines": [line], "lots": [lot]}
    t = Counter()
    t["recipes"] = 1
    CS.tally(out, "MEDIUM", t)
    rep = CS.summarise(t, "MEDIUM")
    assert rep["lines"]["pct_usable_grams"] == 100.0 and rep["lots"]["pct_interval_composition"] == 100.0
    assert rep["lots"]["pct_ph_flag_unknown"]["CONTAINS_ACID_MEMBER"] == 100.0
    D.assert_counts_only({"x": rep})
