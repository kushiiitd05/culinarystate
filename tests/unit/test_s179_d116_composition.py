"""D-116 acceptance: tomato variants share BOIL but get distinct CompositionState / MediumState."""
from __future__ import annotations

from pathlib import Path

import pytest

from culinarystate.composition import state as CS
from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity.rc2_dryrun import load_schema

ROOT = Path(__file__).resolve().parents[2]
MARKERS = CS.load_markers(ROOT / "registry" / "composition_markers_v1.csv")
RUNG, SCHEMA = RungA(coord_food_guard=True), load_schema()
BOIL = "PROC-000019"
CASES = {
    "A": ("Boil the tomatoes in water for 20 minutes.", (False, False, False), "AQUEOUS"),
    "B": ("Mix the tomatoes, water and salt.\nBoil the mixture for 20 minutes.", (True, False, False), "AQUEOUS"),
    "C": ("Mix the tomatoes, water, salt and vinegar.\nBoil the mixture for 20 minutes.", (True, True, False), "AQUEOUS"),
    "D": ("Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes.", (True, True, True),
          "AQUEOUS+LIPID"),
}


def _boil_state(text: str) -> dict:
    out = RUNG.run(SourceText.from_raw("T", text), RUNG.config(), schema=SCHEMA)
    mem = CS.lot_members(out.graph.entities)
    boil = [e for e in out.graph.events if any(a.field == "proc_id" and a.value == BOIL for a in e.attributes)]
    assert len(boil) == 1, "each variant has exactly one BOIL event"
    return CS.composition(list(boil[0].consumes), mem, MARKERS, medium_type=None)


@pytest.mark.parametrize("name", sorted(CASES))
def test_variant_composition(name):
    text, (salt, acid, lipid), phase = CASES[name]
    c = _boil_state(text)
    assert (c["salt_present"]["v"], c["acid_present"]["v"], c["lipid_present"]["v"]) == (salt, acid, lipid)
    assert c["contact_phase"]["v"] == phase
    assert c["food_lot"]["v"] == ["ING-000010"]                       # tomato is the food lot in every variant
    assert c["salt_fraction"] == {"v": None, "u": "MASS_NOT_GROUNDED"}
    assert c["acidity_band"] == {"v": None, "u": "NO_SOURCED_PH_TABLE"}


def test_four_variants_are_distinct():
    sig = {n: tuple((k, str(v)) for k, v in sorted(_boil_state(t).items())) for n, (t, _, _) in CASES.items()}
    assert len(set(sig.values())) == 4


def test_oil_medium_sets_lipid_without_oil_member():
    c = CS.composition(["N1"], {"N1": frozenset({"ING-000010"})}, MARKERS, medium_type="OIL_IMMERSION")
    assert c["lipid_present"]["v"] is True and c["contact_phase"]["v"] == "LIPID"
