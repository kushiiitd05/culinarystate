"""D-116 CompositionState / MediumState (C_t of S_t = (G, C, Q, Y, P)). Derived view only: lot members come from the
Rung A entity lineage (ingredient_id claims + parent_entity_ids); markers from `registry/composition_markers_v1.csv`.
Every field is {"v": value, "b": basis} or {"v": None, "u": reason}. v1 never fills a mixture pH, salt or fat fraction
(no grounded masses / sourced pH table in this path)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping, Optional

MARKERS = ("SALT", "ACID", "LIPID", "AQUEOUS")
WATER_MEDIA = {"WATER", "STEAM"}
OIL_MEDIA = {"OIL_IMMERSION", "PAN_CONTACT_OIL"}
AQUEOUS_MEDIA = WATER_MEDIA | {"LIQUID", "LIQUID_PARTIAL"}
BASIS = "MARKER_TABLE_V1"


def V(v, b):
    return {"v": v, "b": b}


def U(reason):
    return {"v": None, "u": reason}


def load_markers(path: Path) -> dict[str, frozenset[str]]:
    out: dict[str, set[str]] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["ing_id"], set()).add(r["marker"])
    return {k: frozenset(v) for k, v in out.items()}


def lot_members(entities) -> dict[str, frozenset[str]]:
    """entity_id -> ingredient ids of the entity and all its ancestors."""
    by_id = {e.entity_id: e for e in entities}
    memo: dict[str, frozenset[str]] = {}

    def walk(eid: str, seen: frozenset) -> frozenset[str]:
        if eid in memo:
            return memo[eid]
        e = by_id.get(eid)
        if e is None or eid in seen:
            return frozenset()
        own = {a.value for a in (e.attributes or ()) if a.field == "ingredient_id" and a.value}
        for p in e.parent_entity_ids or ():
            own |= walk(p, seen | {eid})
        memo[eid] = frozenset(own)
        return memo[eid]

    return {eid: walk(eid, frozenset()) for eid in by_id}


def composition(consumed: list[str], members: Mapping[str, frozenset[str]], markers: Mapping[str, frozenset[str]],
                medium_type: Optional[str]) -> dict[str, Any]:
    """C_t for one event: union of consumed lots' members, split into food lot vs medium markers."""
    ings = frozenset().union(*(members.get(c, frozenset()) for c in consumed)) if consumed else frozenset()
    has = {m: sorted(i for i in ings if m in markers.get(i, ())) for m in MARKERS}
    food = sorted(i for i in ings if not markers.get(i))
    out: dict[str, Any] = {}
    if not ings:
        for k in ("food_lot", "salt_present", "acid_present", "lipid_present", "aqueous_solutes", "contact_phase"):
            out[k] = U("NO_LINKED_MEMBERS")
    else:
        out["food_lot"] = V(food, "RUNG_A_LOT") if food else U("ONLY_MARKER_MEMBERS")
        out["salt_present"] = V(bool(has["SALT"]), BASIS)
        out["acid_present"] = V(bool(has["ACID"]), BASIS)
        out["lipid_present"] = V(bool(has["LIPID"] or (medium_type in OIL_MEDIA)), BASIS)
        out["aqueous_solutes"] = V([m for m in ("SALT", "ACID") if has[m]], BASIS)
        aq = bool(has["AQUEOUS"]) or medium_type in AQUEOUS_MEDIA
        lip = out["lipid_present"]["v"]
        phase = ("AQUEOUS+LIPID" if aq and lip else "AQUEOUS" if aq else "LIPID" if lip
                 else "AIR" if medium_type in {"OVEN_AIR", "RADIANT"} else None)
        out["contact_phase"] = V(phase, BASIS) if phase else U("MEDIUM_UNKNOWN")
    out["salt_fraction"] = U("MASS_NOT_GROUNDED")
    out["fat_fraction"] = U("MASS_NOT_GROUNDED")
    out["acidity_band"] = U("NO_SOURCED_PH_TABLE")
    return out
