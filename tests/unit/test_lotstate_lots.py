import json
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace

import pytest

from culinarystate.extraction.rung_a import RungA
from culinarystate.lotstate import ph as P
from culinarystate.lotstate import values as V
from culinarystate.lotstate.composition import KINDS
from culinarystate.lotstate.linker import LineLinker, latest_rows, names_map
from culinarystate.lotstate.lots import LotStateBuilder, _known_fraction
from culinarystate.quantity import rc2_dryrun as D
from tests.unit._lotstate_fx import make_sr

ROOT = Path(__file__).resolve().parents[2]
LED = ROOT / "ledgers" / "data"
pytestmark = pytest.mark.skipif(not (LED / "ING.jsonl").exists(), reason="ledgers not present")


@pytest.fixture(scope="module")
def env():
    names = names_map(LED)
    ing = latest_rows(LED / "ING.jsonl")
    top1 = {names["butter"]: {"fdc_id": 2, "band": "HIGH", "score": 1.0},
            names["onion"]: {"fdc_id": 1, "band": "HIGH", "score": 1.0},
            names["sugar"]: {"fdc_id": 3, "band": "MEDIUM", "score": 0.9}}
    return {"names": names, "top1": top1, "ing_names": {k: v["canonical_name"] for k, v in ing.items()},
            "linker": LineLinker(names), "schema": D.load_schema(), "rung": RungA(), "sr": make_sr()}


def builder(env, ph=None):
    return LotStateBuilder(sr=env["sr"], top1=env["top1"], ing_names=env["ing_names"], linker=env["linker"],
                           schema=env["schema"], rung=env["rung"], ph_registry=ph)


def rec(lines, steps, family="WIKIBOOKS"):
    return {"recipe_id": "T1", "source_family": family, "ingredient_lines": lines, "steps": steps}


def test_pool_has_exact_interval_composition(env):
    out = builder(env).build_recipe(rec(["100 g butter", "1 onion"], ["Melt the butter.", "Add the onion."]))
    pool = [lot for lot in out["lots"] if lot["kind"] == "RECIPE_POOL"][0]
    assert pool["composition"]["kind"] == "INTERVAL_EXACT_BOUNDS"
    w = pool["composition"]["nutrients"]["water"]
    lo, hi = F(16 * 100 + 89 * 70, 170), F(16 * 100 + 89 * 150, 250)       # butter 100 g, onion 70-150 g (SR small-large)
    assert abs(w["low"] - float(lo)) < 1e-9 and abs(w["high"] - float(hi)) < 1e-9 and w["type"] == "INTERVAL"
    assert pool["composition"]["total_mass_g"]["low"] == 170.0 and pool["composition"]["total_mass_g"]["high"] == 250.0
    bases = {m["mass_basis"] for m in pool["members"]}
    assert bases == {"STATED_MASS", "SR_PORTION"}


def test_every_lot_obeys_the_value_contract(env):
    out = builder(env).build_recipe(rec(["100 g butter", "1 onion", "salt"],
                                        ["Melt the butter in a pan.", "Add the chopped onion and stir.",
                                         "Season with salt."]))
    assert out["lots"] and out["stats"]["replay_status"] in ("PASS", "UNKNOWN", "FAIL")
    for lot in out["lots"]:
        assert lot["composition"]["kind"] in KINDS
        assert lot["labels"] == ["MODEL_DERIVED", "NON_CITABLE"]
        for rec_ in (*lot["composition"]["nutrients"].values(), lot["composition"]["total_mass_g"],
                     *lot["solute_load"].values(), lot["water_activity"]):
            assert rec_["type"] in V.TYPES and "mask" in rec_ and "basis" in rec_ and "unit" in rec_
            assert (rec_["mask"] == 0) == (rec_["type"] == "UNKNOWN")
            if rec_["type"] == "UNKNOWN":
                assert "value" not in rec_ and "low" not in rec_
        assert lot["water_activity"]["type"] == "UNKNOWN"                       # constants unsourced: default OFF
        assert lot["ph"]["flags"] == {f: "UNKNOWN" for f in P.FLAGS}              # no registry given
    # the unmatched salt member (no SR match in this fixture) makes its lots presence-only, never interval
    salt_lots = [lot for lot in out["lots"] if any(m.get("ing_id") == env["names"]["salt"] for m in lot["members"])]
    assert salt_lots and all(lot["composition"]["kind"] == "PRESENCE_ONLY" for lot in salt_lots)


def test_records_hold_no_recipe_text(env):
    out = builder(env).build_recipe(rec(["100 g butter"], ["Melt the butter in a very distinctive pan."]))
    blob = json.dumps(out)
    assert "distinctive" not in blob and "Melt" not in blob and "100 g butter" not in blob


def test_ph_flags_flow_into_lots(env, tmp_path):
    f = tmp_path / "ph.csv"
    f.write_text(f"name,ph_low,ph_high,source_id\n{env['names']['butter']},6.1,6.4,SYN\n", encoding="utf-8")
    out = builder(env, P.PhRegistry.load(f)).build_recipe(rec(["100 g butter"], ["Melt the butter."]))
    single = [lot for lot in out["lots"] if lot["kind"] == "INGREDIENT_LOT"][0]
    assert single["ph"]["flags"]["CONTAINS_ACID_MEMBER"] == "FALSE"
    assert single["ph"]["flags"]["ALL_MEMBERS_ACID"] == "FALSE"


def test_foodcom_units_stripped_and_length_mismatch(env):
    base = {"recipe_id": "FC1", "source_family": "FOODCOM", "ingredient_lines": [], "steps": []}
    aligned = {**base, "extra": {"ingredient_parts": ["sugar", "butter"], "q_raw": ["2", "1⁄2"], "q_len": 2, "p_len": 2}}
    out = builder(env).build_recipe(aligned)
    assert [l["reason"] for l in out["lines"]] == ["FOODCOM_UNIT_STRIPPED", "FOODCOM_UNIT_STRIPPED"]
    assert all(l["basis"] == "UNKNOWN" and "grams_low" not in l for l in out["lines"])
    pool = out["lots"][0]
    assert pool["kind"] == "RECIPE_POOL" and pool["composition"]["kind"] == "PRESENCE_ONLY"
    mismatched = {**base, "extra": {"ingredient_parts": ["sugar", "butter"], "q_raw": ["2", "1", "3"], "q_len": 3, "p_len": 2}}
    out = builder(env).build_recipe(mismatched)
    assert [l["reason"] for l in out["lines"]] == ["FOODCOM_QP_LENGTH_MISMATCH"] * 2
    assert out["stats"]["foodcom_qp_mismatch"] == 1
    with_unit = {**base, "extra": {"ingredient_parts": ["sugar", "butter"], "q_raw": ["2 cups", "100 g"], "q_len": 2, "p_len": 2}}
    out = builder(env).build_recipe(with_unit)
    assert [l["basis"] for l in out["lines"]] == ["SR_PORTION", "STATED_MASS"]          # unit present in text: honoured


def test_known_fraction_only_for_exact_mass_fractions():
    claim = SimpleNamespace(status="KNOWN", value=F(1, 2))
    assert _known_fraction(SimpleNamespace(kind="SPLIT", basis="MASS", fraction=claim)) == (F(1, 2), F(1, 2))
    assert _known_fraction(SimpleNamespace(kind="SPLIT", basis="VOLUME", fraction=claim)) == (F(0), F(1))
    assert _known_fraction(SimpleNamespace(kind="SPLIT", basis="MASS", fraction=None)) == (F(0), F(1))
    assert _known_fraction(SimpleNamespace(kind="RECOMBINE", basis="MASS", fraction=claim)) == (F(0), F(1))
    bad = SimpleNamespace(status="KNOWN", value=F(3, 2))
    assert _known_fraction(SimpleNamespace(kind="SPLIT", basis="MASS", fraction=bad)) == (F(0), F(1))
