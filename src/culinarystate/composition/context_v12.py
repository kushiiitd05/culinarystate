"""D-116 C_t v1.2: context of one food ingredient inside a heat event's lot.

Context = the other linked members of the consumed lots (the food itself is excluded, so egg noodles' own fat is not
"lipid contact"). A context axis is TRUE when a co-member carries the marker (registry/composition_markers_v2.csv) or
its USDA SR Legacy composition (registry/ing_sr_composition_v1.csv, values copied with fdc_id) passes the threshold.
Thresholds are PROPOSED (not reviewed). Acid has no SR route: pH needs a sourced table (item 8), so acid is marker-only.
Fractions and lot pH stay UNKNOWN. Cells: {"v", "b"} or {"v": None, "u"}.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping, Optional

from culinarystate.composition.state import AQUEOUS_MEDIA, OIL_MEDIA, U, V

BASIS_MARK = "MARKER_TABLE_V2"
BASIS_SR = "USDA_SR_LEGACY_2018_04"
# PROPOSED thresholds (per 100 g of the co-member as purchased), pending ksh+prv / Kush review.
THRESHOLDS = {"lipid": ("fat_g_per_100g", 1.0), "aqueous": ("water_g_per_100g", 50.0),
              "salt": ("sodium_mg_per_100g", 400.0)}
NO_MARK = "NO_RECOGNIZED_MARKER"   # no marker among recognised mentions; words outside the lexicon are invisible
MARKER_OF = {"salt": "SALT", "acid": "ACID", "lipid": "LIPID", "aqueous": "AQUEOUS"}


def load_sr_composition(path: Path) -> dict[str, dict[str, tuple[float, str]]]:
    """ing_id -> nutrient_key -> (amount, fdc_id)."""
    out: dict[str, dict[str, tuple[float, str]]] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["ing_id"], {})[r["nutrient_key"]] = (float(r["amount"]), r["fdc_id"])
    return out


def _axis(axis: str, ctx: list[str], markers, sr, medium_type, unlinked: bool) -> dict:
    why = sorted(f"{BASIS_MARK}:{i}" for i in ctx if MARKER_OF[axis] in markers.get(i, ()))
    if axis in THRESHOLDS:
        key, lim = THRESHOLDS[axis]
        why += sorted(f"{BASIS_SR}:fdc:{sr[i][key][1]}:{key}={sr[i][key][0]:g}" for i in ctx
                      if key in sr.get(i, {}) and sr[i][key][0] >= lim)
    if axis == "lipid" and medium_type in OIL_MEDIA:
        why.append(f"PHYSICS_V06_L1:{medium_type}")
    if axis == "aqueous" and medium_type in AQUEOUS_MEDIA:
        why.append(f"PHYSICS_V06_L1:{medium_type}")
    if why:
        return V(True, "; ".join(why))
    return U("MEMBER_UNLINKED") if unlinked else V(NO_MARK, BASIS_MARK + ("" if axis == "acid" else "+" + BASIS_SR))


def _phase(aq: bool, lip: bool, medium_type: Optional[str]) -> dict:
    phase = ("AQUEOUS+LIPID" if aq and lip else "AQUEOUS" if aq else "LIPID" if lip
             else "AIR" if medium_type in {"OVEN_AIR", "RADIANT"} else None)
    return V(phase, "CONTEXT_AXES_V12") if phase else U("MEDIUM_UNKNOWN")


def context_v12(food: str, consumed, members: Mapping[str, tuple[frozenset, bool]], markers, roles,
                sr: Mapping[str, Mapping[str, tuple[float, str]]], medium_type: Optional[str]) -> dict[str, Any]:
    ings, unlinked = frozenset(), False
    for c in consumed or ():
        i, u = members.get(c, (frozenset(), False))
        ings, unlinked = ings | i, unlinked or u
    out: dict[str, Any] = {"food": V(food, "RUNG_A_LOT") if food in ings else U("FOOD_NOT_IN_LOT")}
    ctx = sorted(ings - {food})
    out["context_members"] = V(ctx, "RUNG_A_LOT")
    for axis in ("salt", "acid", "lipid", "aqueous"):
        out[f"{axis}_present"] = _axis(axis, ctx, markers, sr, medium_type, unlinked)
    out["contact_phase"] = (_phase(out["aqueous_present"]["v"] is True, out["lipid_present"]["v"] is True, medium_type)
                            if ings else U("NO_LINKED_MEMBERS"))
    out["member_composition"] = V({i: {k: v[0] for k, v in sr.get(i, {}).items()} for i in ctx},
                                  BASIS_SR + " (per 100 g as purchased; ING match AI_DRAFTED)")
    out["nacl_equiv_fraction_as_added"] = U("MASS_NOT_GROUNDED")
    out["fat_fraction_as_added"] = U("MASS_NOT_GROUNDED")
    out["lot_acidity_band"] = U("LOT_PH_NOT_COMPUTED")
    return out
