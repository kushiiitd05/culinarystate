"""Step 4: pH registry INTERFACE and lot pH flags. No mixture pH number is ever computed (buffering unknown).

Registry interface (CSV, any extra columns ignored). One row = one food or ING with a pH range:
    key columns (first present): ``ing_id`` | ``name`` | ``item_norm`` | ``food_name``   (ING id or a food name)
    ``ph_low`` , ``ph_high``   (``ph_high`` empty = lower bound only, an open range, never a POINT)
    ``source_id``              provenance id of the registry row's source
A row whose key starts with ``ING-`` is looked up by ING id; any other key is looked up by normalised name against the
ING canonical name. An optional crosswalk CSV (``ph_id`` -> ``ing_id``, ``confidence_band``) maps rows whose key is a
food name (the other lane's ``registry/food_ph_fda_draft_v1.csv`` + ``..._ing_crosswalk_draft_v1.csv`` have exactly
that shape; ``ph_id``, ``item_norm`` are read when present).

Member status against a threshold is three-valued (Kleene):
- acid:      YES if ph_high <= ACID_MAX (4.6, packet section 5.2); NO if ph_low > ACID_MAX; MAYBE if the range
             straddles it; UNKNOWN if the member has no pH row or no usable bounds.
- alkaline:  YES if ph_low > ALKALINE_MIN (7.0, neutral at 25 C by definition); NO if ph_high <= 7.0;
             MAYBE if straddling or open above; UNKNOWN without a row.
Lot flags (TRUE / FALSE / UNKNOWN):
    CONTAINS_ACID_MEMBER      TRUE if any member YES; FALSE if all members NO; else UNKNOWN
    CONTAINS_ALKALINE_MEMBER  TRUE if any member YES; FALSE if all members NO; else UNKNOWN
    ALL_MEMBERS_ACID          TRUE if all members YES; FALSE if any member NO; else UNKNOWN
With no registry every flag is UNKNOWN. A lot with no members has UNKNOWN flags.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .linker import norm

ACID_MAX = 4.6
ALKALINE_MIN = 7.0
FLAGS = ("CONTAINS_ACID_MEMBER", "CONTAINS_ALKALINE_MEMBER", "ALL_MEMBERS_ACID")
KEY_COLUMNS = ("ing_id", "name", "item_norm", "food_name")
BAND_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}


@dataclass(frozen=True)
class PhRange:
    low: float | None
    high: float | None
    source_id: str
    row_ref: str = ""


def _f(x) -> float | None:
    x = (x or "").strip() if isinstance(x, str) else x
    if x in ("", None):
        return None
    try:
        return float(x)
    except ValueError:
        return None


class PhRegistry:
    def __init__(self, by_ing: Mapping[str, PhRange], by_name: Mapping[str, PhRange], source: str = ""):
        self.by_ing, self.by_name, self.source = dict(by_ing), dict(by_name), source

    def __len__(self) -> int:
        return len(self.by_ing) + len(self.by_name)

    def lookup(self, ing_id: str | None, ing_name: str | None = None) -> PhRange | None:
        if ing_id and ing_id in self.by_ing:
            return self.by_ing[ing_id]
        if ing_name:
            return self.by_name.get(norm(ing_name))
        return None

    @classmethod
    def load(cls, path: Path, *, crosswalk: Path | None = None, crosswalk_min_band: str = "HIGH") -> "PhRegistry":
        by_ing: dict[str, PhRange] = {}
        by_name: dict[str, PhRange] = {}
        xw: dict[str, list[str]] = {}
        if crosswalk is not None:
            with open(crosswalk, encoding="utf-8", newline="") as fh:
                for r in csv.DictReader(fh):
                    if (r.get("ing_id") and r.get("ph_id")
                            and BAND_RANK.get(r.get("confidence_band", ""), 0) >= BAND_RANK[crosswalk_min_band]
                            and str(r.get("rank", "1")) in ("1", "")):
                        xw.setdefault(r["ph_id"], []).append(r["ing_id"])
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                key = next((r[c].strip() for c in KEY_COLUMNS if r.get(c) and r[c].strip()), "")
                lo, hi = _f(r.get("ph_low")), _f(r.get("ph_high"))
                if not key or (lo is None and hi is None):
                    continue
                rng = PhRange(lo, hi, (r.get("source_id") or "").strip(), r.get("ph_id") or key)
                if key.startswith("ING-"):
                    by_ing.setdefault(key, rng)
                else:
                    by_name.setdefault(norm(key), rng)
                for ing in xw.get(r.get("ph_id") or "", ()):
                    by_ing.setdefault(ing, rng)
        return cls(by_ing, by_name, str(path))


def member_status(rng: PhRange | None) -> dict[str, str]:
    """{"acid": YES|NO|MAYBE|UNKNOWN, "alkaline": ...} for one member."""
    if rng is None or (rng.low is None and rng.high is None):
        return {"acid": "UNKNOWN", "alkaline": "UNKNOWN"}
    lo, hi = rng.low, rng.high
    # acid
    if hi is not None and hi <= ACID_MAX:
        acid = "YES"
    elif lo is not None and lo > ACID_MAX:
        acid = "NO"
    else:
        acid = "MAYBE"
    # alkaline
    if lo is not None and lo > ALKALINE_MIN:
        alk = "YES"
    elif hi is not None and hi <= ALKALINE_MIN:
        alk = "NO"
    else:
        alk = "MAYBE"
    return {"acid": acid, "alkaline": alk}


def _any(vals: Sequence[str]) -> str:
    return "TRUE" if "YES" in vals else "FALSE" if vals and all(v == "NO" for v in vals) else "UNKNOWN"


def lot_flags(statuses: Sequence[Mapping[str, str]]) -> dict[str, str]:
    acid = [s["acid"] for s in statuses]
    alk = [s["alkaline"] for s in statuses]
    all_acid = ("TRUE" if acid and all(v == "YES" for v in acid) else "FALSE" if "NO" in acid else "UNKNOWN")
    return {"CONTAINS_ACID_MEMBER": _any(acid), "CONTAINS_ALKALINE_MEMBER": _any(alk), "ALL_MEMBERS_ACID": all_acid}


def ph_record(members: Iterable[tuple[str | None, str | None]], registry: PhRegistry | None) -> dict:
    """Lot pH record: flags + per-member ranges. ``members`` = (ing_id, ing_canonical_name). No mixture pH number."""
    ms = list(members)
    prov = {"method": "PH_MEMBER_RANGE_FLAGS", "labels": ["MODEL_DERIVED", "NON_CITABLE"], "mixture_ph": "NOT_COMPUTED",
            "registry": registry.source if registry else "ABSENT", "thresholds": {"acid_max": ACID_MAX,
                                                                                    "alkaline_min": ALKALINE_MIN},
            "verification": "AI_DRAFTED_UNVERIFIED"}
    if registry is None:
        return {"type": "QUALITATIVE", "mask": 0, "unit": "pH", "basis": "NO_REGISTRY", "provenance": prov,
                "flags": {f: "UNKNOWN" for f in FLAGS}, "member_ranges": []}
    ranges = [registry.lookup(i, n) for i, n in ms]
    st = [member_status(r) for r in ranges]
    flags = lot_flags(st) if ms else {f: "UNKNOWN" for f in FLAGS}
    known = any(v != "UNKNOWN" for v in flags.values())
    return {"type": "QUALITATIVE", "mask": 1 if known else 0, "unit": "pH", "basis": "MEMBER_RANGES", "provenance": prov,
            "flags": flags,
            "member_ranges": [None if r is None else {"low": r.low, "high": r.high, "source_id": r.source_id}
                              for r in ranges]}
