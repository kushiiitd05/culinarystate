"""D-132 opt-in lineage vNext (A guard prepositions, B fat stays, C mixture coref, D alternatives); frozen when off."""
import json
from pathlib import Path

import pytest

from culinarystate.composition import state as CS
from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity.rc2_dryrun import load_schema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = load_schema()
NAMES = {json.loads(l)["id"]: json.loads(l)["canonical_name"] for l in (ROOT / "ledgers/data/ING.jsonl").read_text().splitlines()
         if l.strip()}
TXT = ("Chop the tomatoes.\nFry the onion in oil for 5 minutes.\nAdd the tomatoes and salt to the onion.\n"
       "Boil the mixture for 20 minutes.\nStir in the vinegar and boil the sauce for 5 minutes.")


def _events(text, vnext):
    r = RungA(coord_food_guard=True, lineage_vnext=vnext)
    out = r.run(SourceText.from_raw("T", text), r.config(), schema=SCHEMA)
    mem = CS.lot_members_v11(out.graph.entities)
    return [(" ".join(e.span.texts).lower(), sorted({NAMES.get(i, i) for c in e.consumes for i in mem.get(c, (frozenset(),))[0]}),
             len(e.produces)) for e in out.graph.events], out


def test_frozen_behaviour_unchanged_when_off():
    ev, _ = _events(TXT, False)
    assert ("salt", ["onion", "tomato"], 1) in ev                     # bug A still present in the frozen version
    assert ("fry", ["oil", "onion"], 2) in ev                          # bug B: fat split off
    assert ev[-1][1] == ["sauce"]                                      # bug C: new lot


def test_a_salt_stays_an_ingredient():
    ev, _ = _events(TXT, True)
    assert all(a != "salt" for a, _, _ in ev) and "salt" in ev[2][1]


def test_b_fat_stays_in_the_lot():
    ev, _ = _events(TXT, True)
    assert ev[1] == ("fry", ["oil", "onion"], 1) and "oil" in ev[2][1]


def test_c_sauce_continues_the_mixture():
    ev, out = _events(TXT, True)
    assert ev[-1][1] == ["oil", "onion", "salt", "tomato", "vinegar"]
    assert "VNEXT_MIXTURE_COREF" in out.graph.diagnostics if hasattr(out.graph, "diagnostics") else True


@pytest.mark.parametrize("text,kept,dropped", [("Melt the butter or oil in a pan.", "butter", "oil")])
def test_d_alternative_binds_first_only(text, kept, dropped):
    ev, _ = _events(text, True)
    members = {m for _, ms, _ in ev for m in ms}
    assert kept in members and dropped not in members
    ev0, _ = _events(text, False)
    assert dropped in {m for _, ms, _ in ev0 for m in ms}
