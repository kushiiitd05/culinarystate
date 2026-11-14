"""D-116 v1.1 acceptance (markers v2, guard v2): tri-valued presence, roles, no invented lot values."""
from __future__ import annotations

from pathlib import Path

import pytest

from culinarystate.composition import state as CS
from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.quantity.rc2_dryrun import load_schema

ROOT = Path(__file__).resolve().parents[2]
MARKERS, ROLES = CS.load_markers_v2(ROOT / "registry" / "composition_markers_v2.csv")
RUNG, SCHEMA = RungA(coord_food_guard=True), load_schema()
ND = "NOT_DETECTED"
CASES = {
    "A": ("Boil the tomatoes in water for 20 minutes.", (ND, ND, ND), "AQUEOUS"),
    "B": ("Mix the tomatoes, water and salt.\nBoil the mixture for 20 minutes.", (True, ND, ND), "AQUEOUS"),
    "C": ("Mix the tomatoes, water, salt and vinegar.\nBoil the mixture for 20 minutes.", (True, True, ND), "AQUEOUS"),
    "D": ("Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes.", (True, True, True),
          "AQUEOUS+LIPID"),
}


def _boil(text):
    out = RUNG.run(SourceText.from_raw("T", text), RUNG.config(), schema=SCHEMA)
    mem = CS.lot_members_v11(out.graph.entities)
    ev = [e for e in out.graph.events if any(a.field == "proc_id" and a.value == "PROC-000019" for a in e.attributes)]
    assert len(ev) == 1
    return CS.composition_v11(list(ev[0].consumes), mem, MARKERS, ROLES, None)


@pytest.mark.parametrize("name", sorted(CASES))
def test_v11_variant(name):
    text, flags, phase = CASES[name]
    c = _boil(text)
    assert tuple(c[f"{k}_marker_present"]["v"] for k in ("salt", "acid", "lipid")) == flags
    assert c["contact_phase"]["v"] == phase and c["food_lot"]["v"] == ["ING-000010"]
    assert c["lot_acidity_band"] == {"v": None, "u": "LOT_PH_NOT_COMPUTED"}


def test_v11_variants_distinct():
    assert len({str(sorted(_boil(t).items())) for t, _, _ in CASES.values()}) == 4


def test_unlinked_member_gives_unknown_not_false():
    c = CS.composition_v11(["N1"], {"N1": (frozenset({"ING-000010"}), True)}, MARKERS, ROLES, None)
    assert c["salt_marker_present"] == {"v": None, "u": "MEMBER_UNLINKED"}
