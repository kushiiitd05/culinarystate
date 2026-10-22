"""STEP 07H-R: recipe expression probe unit tests (synthetic recipes; no corpus needed)."""
import pytest

from culinarystate.recipes import probe as PR


def rec(steps=(), lines=(), times=None, fam="A1_BBC_GOOD_FOOD"):
    return {"recipe_id": "T1", "source_id": "S", "source_family": fam, "source_record_id": "x", "ingredient_lines": list(lines), "steps": list(steps), "structured_times": times or {}, "family_id": "FAM-T1"}


def by(rows, fam):
    return [r for r in rows if r["expression_family"] == fam]


def test_oven_compound_preserved_not_merged_not_mapped():
    rows = PR.probe_recipe(rec(["Heat oven to 180C/160C fan/gas 4."]))
    t, g = by(rows, "TEMPERATURE"), by(rows, "GAS_MARK")
    assert [x["raw_expression"] for x in t] == ["180C", "160C fan"] and len(g) == 1
    assert {x["compound_group_id"] for x in t + g} != {None} and len({x["compound_group_id"] for x in t + g}) == 1
    assert all(x["measurement_location"] == "SETPOINT" for x in t)                      # oven wording supports a setpoint candidate only
    assert g[0]["canonical_value"] is None and g[0]["mapping_status"] == "UNSUPPORTED_NO_SOURCED_MAPPING"   # gas marks never converted without a sourced mapping


def test_recipe_text_is_not_physical_truth():
    rows = PR.probe_recipe(rec(["Bring to the boil, then cook on a medium heat until golden. Cool completely."]))
    assert not by(rows, "TEMPERATURE") and by(rows, "QUALITATIVE_HEAT")[0]["canonical_value"] is None
    assert all(r["observation_class"] == "TEXT_STATED" and r["source_plane"] == "RECIPE" for r in rows)
    assert not any("tier" in k for r in rows for k in r)


def test_unspecified_location_stays_ambiguous():
    r = by(PR.probe_recipe(rec(["Cook at 180C for 20 mins."])), "TEMPERATURE")[0]
    assert r["measurement_location"] == "UNSPECIFIED" and r["normalized_status"] == "AMBIGUOUS"


def test_times_compound_fraction_calendar():
    rows = by(PR.probe_recipe(rec(["Bake for 1 hr 30 mins, then rest 1½ hours or 1/2 hour. Keeps for 3 months."])), "TIME")
    got = {r["raw_expression"]: (r["normalized_status"], r["canonical_value"]) for r in rows}
    assert got["1 hr 30 mins"] == ("VALID", 5400.0) and got["1½ hours"][1] == 5400.0 and got["1/2 hour"][1] == 1800.0
    assert got["3 months"][0] == "AMBIGUOUS" and got["3 months"][1] is None   # calendar durations never converted


def test_quantity_syntax_only_no_invented_grams():
    rows = by(PR.probe_recipe(rec(lines=["2 x 400g tins chopped tomatoes", "1½ tsp salt", "a pinch of sugar", "3 eggs"])), "QUANTITY")
    d = {r["raw_expression"]: r for r in rows}
    assert d["2 x 400g"]["canonical_value"] == pytest.approx(0.8) and d["2 x 400g"]["canonical_unit"] == "kg"
    assert d["1½ tsp"]["canonical_value"] is None and "UNIT_RECOGNISED_NO_CONVERSION" in d["1½ tsp"]["reason_codes"]
    assert d["a pinch of"]["normalized_value_type"] == "QUALITATIVE" and d["3"]["reason_codes"].find("UNITLESS_NUMBER") >= 0


def test_power_pressure_geometry_and_structured_time():
    rows = PR.probe_recipe(rec(["Microwave at 800W. Cook at 15 psi in a 20 x 30cm dish."], times={"total_time_raw": "PT1H45M"}))
    assert by(rows, "POWER")[0]["canonical_value"] == 800.0
    p = by(rows, "PRESSURE")[0]
    assert p["normalized_status"] == "AMBIGUOUS" and "PRESSURE_REFERENCE_UNSPECIFIED" in p["reason_codes"]
    assert by(rows, "GEOMETRY")[0]["reason_codes"] == "MULTI_DIMENSION_EXPRESSION"
    assert by(rows, "TIME_STRUCTURED_FIELD")[0]["canonical_value"] == 6300.0


def test_deterministic_ids_and_rerun_equal():
    r = rec(["Bake at 200C for 20 minutes until golden."], ["1 onion"])
    assert PR.probe_recipe(r) == PR.probe_recipe(r)
