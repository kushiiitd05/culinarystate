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


# ---------------------------------------------------------------- v1.1 (ksh+prv AI review, D-085, 14 Nov 2026)
BASIS_V2 = "MARKER_TABLE_V2"


def load_markers_v2(path: Path) -> tuple[dict[str, frozenset[str]], dict[str, str]]:
    marks: dict[str, set[str]] = {}
    roles: dict[str, str] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            marks.setdefault(r["ing_id"], set()).add(r["marker"])
            roles[r["ing_id"]] = r.get("role_default") or "MEDIUM"
    return {k: frozenset(v) for k, v in marks.items()}, roles


def lot_members_v11(entities) -> dict[str, tuple[frozenset[str], bool]]:
    """entity_id -> (ingredient ids in lineage, any INGREDIENT_LOT ancestor without an ingredient_id)."""
    by_id = {e.entity_id: e for e in entities}
    memo: dict[str, tuple[frozenset[str], bool]] = {}

    def walk(eid, seen):
        if eid in memo:
            return memo[eid]
        e = by_id.get(eid)
        if e is None or eid in seen:
            return frozenset(), False
        own = {a.value for a in (e.attributes or ()) if a.field == "ingredient_id" and a.value}
        unlinked = e.entity_type == "INGREDIENT_LOT" and not own
        for p in e.parent_entity_ids or ():
            i, u = walk(p, seen | {eid})
            own |= i
            unlinked |= u
        memo[eid] = (frozenset(own), unlinked)
        return memo[eid]

    return {eid: walk(eid, frozenset()) for eid in by_id}


def composition_v11(consumed, members, markers, roles, medium_type):
    """C_t v1.1: presence TRUE / NOT_DETECTED (no marker among linked members) / UNKNOWN (unlinked member)."""
    ings, unlinked = frozenset(), False
    for c in consumed or ():
        i, u = members.get(c, (frozenset(), False))
        ings |= i
        unlinked |= u
    out = {}
    if not ings:
        for k in ("food_lot", "medium_members", "salt_marker_present", "acid_marker_present", "lipid_marker_present",
                  "contact_phase"):
            out[k] = U("NO_LINKED_MEMBERS")
    else:
        medium = sorted(i for i in ings if markers.get(i) and roles.get(i) == "MEDIUM")
        food = sorted(i for i in ings if i not in medium)
        out["food_lot"] = V(food, "RUNG_A_LOT") if food else U("ONLY_MEDIUM_MEMBERS")
        out["medium_members"] = V(medium, BASIS_V2)
        for name, m in (("salt", "SALT"), ("acid", "ACID"), ("lipid", "LIPID")):
            hit = any(m in markers.get(i, ()) for i in ings) or (m == "LIPID" and medium_type in OIL_MEDIA)
            out[f"{name}_marker_present"] = (V(True, BASIS_V2) if hit else U("MEMBER_UNLINKED") if unlinked
                                             else V("NOT_DETECTED", BASIS_V2))
        aq = any("AQUEOUS" in markers.get(i, ()) for i in ings) or medium_type in AQUEOUS_MEDIA
        lip = out["lipid_marker_present"]["v"] is True
        phase = ("AQUEOUS+LIPID" if aq and lip else "AQUEOUS" if aq else "LIPID" if lip
                 else "AIR" if medium_type in {"OVEN_AIR", "RADIANT"} else None)
        out["contact_phase"] = V(phase, BASIS_V2 + "+PHYSICS_V06_L1") if phase else U("MEDIUM_UNKNOWN")
    out["nacl_equiv_fraction_as_added"] = U("MASS_NOT_GROUNDED")
    out["fat_fraction_as_added"] = U("MASS_NOT_GROUNDED")
    out["lot_acidity_band"] = U("LOT_PH_NOT_COMPUTED")
    return out
