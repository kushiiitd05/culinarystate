import csv
from fractions import Fraction as F
from pathlib import Path

import pytest

from culinarystate.lotstate import values as V
from culinarystate.lotstate.composition import (AW_REGISTRY, AwConfig, CompositionConfig, Member, composition,
                                                  solute_load, water_activity)
from tests.unit._lotstate_fx import make_sr

SR = make_sr()
ROOT = Path(__file__).resolve().parents[2]


def M(ing, fdc, lo=None, hi=None, band="HIGH", basis="STATED_MASS"):
    return Member(ing, fdc, band, None if lo is None else (F(lo), F(hi if hi is not None else lo)), basis)


def test_single_member_is_point_and_mass_independent():
    c = composition([M("ING-1", 1)], SR)
    assert c["kind"] == "SINGLE_MEMBER_POINT"
    assert c["nutrients"]["water"]["type"] == "POINT" and c["nutrients"]["water"]["value"] == 89.0
    assert c["nutrients"]["starch"]["value"] == 0.0               # SR starch 0 is a known value
    assert c["nutrients"]["water"]["unit"] == "g/100g" and c["nutrients"]["sodium"]["unit"] == "mg/100g"
    V.check_record(c["nutrients"]["water"])


def test_missing_sr_nutrient_is_unknown_not_zero():
    c = composition([M("ING-5", 5)], SR)                           # olive oil: starch absent in the fixture
    n = c["nutrients"]["starch"]
    assert n["type"] == "UNKNOWN" and n["mask"] == 0 and n.get("value") is None and n["reason"] == "SR_NUTRIENT_MISSING"


def test_interval_bounds_are_exact_for_point_masses():
    # 100 g onion + 100 g butter: water = (89 + 16) / 2 = 52.5
    c = composition([M("ING-1", 1, 100), M("ING-2", 2, 100)], SR)
    assert c["kind"] == "INTERVAL_EXACT_BOUNDS"
    w = c["nutrients"]["water"]
    assert w["type"] == "POINT" and w["value"] == 52.5
    assert c["total_mass_g"]["value"] == 200.0


def test_interval_bounds_over_mass_intervals():
    # onion 50-150 g, butter 100 g: water fraction between (89*50+16*100)/150 and (89*150+16*100)/250
    c = composition([M("ING-1", 1, 50, 150), M("ING-2", 2, 100)], SR)
    w = c["nutrients"]["water"]
    lo, hi = F(89 * 50 + 16 * 100, 150), F(89 * 150 + 16 * 100, 250)
    assert w["type"] == "INTERVAL" and w["low"] <= float(lo) and w["high"] >= float(hi)
    assert abs(w["low"] - float(lo)) < 1e-9 and abs(w["high"] - float(hi)) < 1e-9
    assert w["basis"] == "SR_VALUE+MASS_INTERVAL"


def test_unknown_member_mass_gives_presence_only():
    c = composition([M("ING-1", 1, 100), M("ING-2", 2)], SR)
    assert c["kind"] == "PRESENCE_ONLY"
    assert c["nutrients"]["fat"] == {**c["nutrients"]["fat"], "type": "QUALITATIVE", "label": "PRESENT"}
    # sugars: butter 0, onion 4 -> PRESENT; vitamin C: butter 0, onion 7 -> PRESENT; starch: onion 0, butter missing -> UNKNOWN
    assert c["nutrients"]["vitamin_c"]["label"] == "PRESENT"
    assert c["nutrients"]["starch"]["type"] == "UNKNOWN"


def test_presence_absent_requires_every_member_known_zero():
    c = composition([M("ING-3", 3), M("ING-4", 4)], SR)            # sugar + salt, no masses
    assert c["kind"] == "PRESENCE_ONLY"
    assert c["nutrients"]["fat"]["label"] == "ABSENT"
    assert c["nutrients"]["sodium"]["label"] == "PRESENT"


def test_unmatched_or_low_band_member_blocks_interval_composition():
    c = composition([M("ING-1", 1, 100), Member("ING-9", None, "NONE", (F(10), F(10)), "STATED_MASS")], SR)
    assert c["kind"] == "PRESENCE_ONLY"
    c = composition([M("ING-1", 1, 100), M("ING-2", 2, 100, band="LOW")], SR, CompositionConfig(min_band="MEDIUM"))
    assert c["kind"] == "PRESENCE_ONLY"
    c = composition([M("ING-1", 1, 100), M("ING-2", 2, 100, band="LOW")], SR, CompositionConfig(min_band="LOW"))
    assert c["kind"] == "INTERVAL_EXACT_BOUNDS"
    assert composition([], SR)["kind"] == "NO_MEMBERS"


def test_solute_load_exact():
    # 100 g sugar + 100 g onion water 89: sugar g per g water = (100*1.0 + 100*0.04) / (100*0 + 100*0.89)
    sol = solute_load([M("ING-3", 3, 100), M("ING-1", 1, 100)], SR)
    s = sol["sugar_g_per_g_water"]
    assert s["type"] == "POINT" and abs(s["value"] - (100 + 4) / 89) < 1e-12
    salt = sol["salt_g_per_g_water"]
    # sodium: onion 4 mg/100g -> 4 x 2.5421 / 1000 g NaCl per 100 g -> / 100 per g; water 0.89 g per g (S175 fix)
    assert abs(salt["value"] - (4 * 2.5421 / 1000 / 100) / 0.89) < 1e-12
    assert salt["value"] < 0.36  # never above NaCl saturation in water for a moist food


def test_solute_load_unbounded_without_water():
    # salt (no water) with an onion whose mass may be 0: no finite upper bound
    sol = solute_load([M("ING-4", 4, 5, 10), M("ING-1", 1, 0, 100)], SR)
    s = sol["salt_g_per_g_water"]
    assert s["type"] == "INTERVAL" and s["open_upper"] is True and s["high"] is None


def test_solute_load_unknown_when_a_member_mass_is_unknown():
    sol = solute_load([M("ING-4", 4), M("ING-1", 1, 100)], SR)
    assert sol["salt_g_per_g_water"]["type"] == "UNKNOWN"
    assert sol["salt_g_per_g_water"]["reason"] == "MEMBER_MASS_UNKNOWN"


def test_water_activity_is_unknown_by_default_and_flagged_when_enabled():
    sol = solute_load([M("ING-3", 3, 50), M("ING-18", 18, 50)], SR)
    off = water_activity(sol)
    assert off["type"] == "UNKNOWN" and off["reason"] == "AW_CONSTANTS_UNSOURCED_SWITCH_OFF"
    on = water_activity(sol, AwConfig(allow_unverified_constants=True, registry_path=ROOT / AW_REGISTRY))
    assert on["type"] in ("INTERVAL", "POINT")
    assert 0.0 < on["low"] <= on["high"] < 1.0
    labels = on["provenance"]["labels"]
    assert "MODEL_DERIVED" in labels and "NON_CITABLE" in labels
    assert "SOURCE_UNVERIFIED_CONSTANTS" in on["provenance"]["flags"]
    # more sugar per water -> lower water activity
    more = water_activity(solute_load([M("ING-3", 3, 90), M("ING-18", 18, 10)], SR),
                          AwConfig(allow_unverified_constants=True, registry_path=ROOT / AW_REGISTRY))
    assert more["high"] < on["low"]


def test_water_activity_unknown_with_salt_or_without_registry(tmp_path):
    sol = solute_load([M("ING-3", 3, 50), M("ING-4", 4, 5), M("ING-18", 18, 50)], SR)
    r = water_activity(sol, AwConfig(allow_unverified_constants=True, registry_path=ROOT / AW_REGISTRY))
    assert r["type"] == "UNKNOWN" and r["reason"] == "ELECTROLYTE_PRESENT_NORRISH_NOT_VALID"
    r = water_activity(sol, AwConfig(allow_unverified_constants=True, registry_path=tmp_path / "missing.csv"))
    assert r["reason"] == "AW_CONSTANT_REGISTRY_MISSING"


def test_constants_registry_is_marked_unverified():
    rows = list(csv.DictReader(open(ROOT / AW_REGISTRY, encoding="utf-8")))
    assert rows and {r["status"] for r in rows} == {"SOURCE_UNVERIFIED_AGENT_RECALLED"}
