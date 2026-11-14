"""D-116 C_t v1.2: per-food context from co-members (marker table v2 + USDA SR Legacy composition)."""
from __future__ import annotations

from pathlib import Path

from culinarystate.composition import context_v12 as CV
from culinarystate.composition import state as CS
from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity.rc2_dryrun import load_schema

ROOT = Path(__file__).resolve().parents[2]
MARKS, ROLES = CS.load_markers_v2(ROOT / "registry" / "composition_markers_v2.csv")
SR = CV.load_sr_composition(ROOT / "registry" / "ing_sr_composition_v1.csv")
RUNG, SCHEMA = RungA(coord_food_guard=True), load_schema()
NOODLES, MILK, TOMATO_SAUCE, TOMATO = "ING-000757", "ING-000014", "ING-000680", "ING-000010"
COOK, BOIL = "PROC-000031", "PROC-000019"


def _ctx(text: str, proc: str, food: str) -> dict:
    out = RUNG.run(SourceText.from_raw("T", text), RUNG.config(), schema=SCHEMA)
    mem = CS.lot_members_v11(out.graph.entities)
    ev = [e for e in out.graph.events if any(a.field == "proc_id" and a.value == proc for a in e.attributes)][-1]
    return CV.context_v12(food, list(ev.consumes), mem, MARKS, ROLES, SR, medium_type=None)


def _v(c, k):
    return c[k].get("v")


MILK_TXT = "Boil the noodles in water for 10 minutes. Drain.\nCook the noodles with milk for 5 minutes."
SAUCE_TXT = "Boil the noodles in water for 10 minutes. Drain.\nCook the noodles with tomato sauce for 5 minutes."


def test_noodles_with_milk_get_aqueous_lipid_context_from_sr():
    c = _ctx(MILK_TXT, COOK, NOODLES)
    assert _v(c, "context_members") == [MILK]
    assert _v(c, "lipid_present") is True and _v(c, "aqueous_present") is True
    assert _v(c, "contact_phase") == "AQUEOUS+LIPID"
    assert "fdc:171265" in c["lipid_present"]["b"]


def test_noodles_with_tomato_sauce_get_aqueous_low_fat_context():
    c = _ctx(SAUCE_TXT, COOK, NOODLES)
    assert _v(c, "context_members") == [TOMATO_SAUCE]
    assert _v(c, "lipid_present") == "NO_RECOGNIZED_MARKER" and _v(c, "aqueous_present") is True
    assert _v(c, "contact_phase") == "AQUEOUS"


def test_milk_and_tomato_sauce_contexts_differ_but_food_is_noodles():
    a, b = _ctx(MILK_TXT, COOK, NOODLES), _ctx(SAUCE_TXT, COOK, NOODLES)
    assert _v(a, "food") == _v(b, "food") == NOODLES
    assert a != b


def test_food_own_fat_is_not_its_context():
    c = _ctx("Boil the noodles in water for 10 minutes.", BOIL, NOODLES)    # egg noodles 4.44 g fat / 100 g
    assert _v(c, "lipid_present") == "NO_RECOGNIZED_MARKER" and _v(c, "contact_phase") == "AQUEOUS"


def test_tomato_variant_d_context():
    c = _ctx("Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes.", BOIL, TOMATO)
    assert (_v(c, "salt_present"), _v(c, "acid_present"), _v(c, "lipid_present")) == (True, True, True)
    assert _v(c, "contact_phase") == "AQUEOUS+LIPID"
    assert c["lot_acidity_band"] == {"v": None, "u": "LOT_PH_NOT_COMPUTED"}


def test_unlinked_member_gives_unknown_not_false():
    c = CV.context_v12(NOODLES, ["N1"], {"N1": (frozenset({NOODLES}), True)}, MARKS, ROLES, SR, medium_type=None)
    assert c["lipid_present"] == {"v": None, "u": "MEMBER_UNLINKED"}
