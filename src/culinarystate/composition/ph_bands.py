"""pH bands per ingredient, from the in-repo FDA/CFSAN 2003 table (freeze step 8, axis 7).

The gap matrix recorded pH as 0% fill and "schema only", and the known limitations said there was no
sourced pH table, so tomato sauce could not be called acidic. A sourced table was already in the
repo: ``registry/food_ph_fda2003_v1.csv`` — 479 rows from *FDA/CFSAN Approximate pH of Foods and
Food Products*, Oct 2003, public domain, each row carrying the source's own SHA-256. The ING
crosswalk is ``registry/food_ph_fda_ing_crosswalk_draft_v1.csv``.

Two rules keep this honest:

* **Only EXACT / FULL crosswalk rows are used.** The crosswalk is AI_DRAFTED, and a LOW-confidence
  generalisation ("abalone mushroom" → "mushroom") is not evidence. Everything else stays UNKNOWN.
* **An interval stays an interval.** No midpoint is computed and nothing is clipped (D-013). A band
  that straddles the FDA 4.6 acid-food threshold is INCONCLUSIVE, not forced to a side.

The band is sourced but the *mapping* is not yet human-verified, so every band reports
``verify_status = UNVERIFIED_CROSSWALK_AI_DRAFTED``. Step 8's human verification is still owed for
any band used in a figure (D-085: AI review ≠ human verification).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PH_CSV = ROOT / "registry/food_ph_fda2003_v1.csv"
XWALK_CSV = ROOT / "registry/food_ph_fda_ing_crosswalk_draft_v1.csv"

BASIS = "FDA_PH_2003_VIA_AI_DRAFTED_CROSSWALK"
VERIFY_STATUS = "UNVERIFIED_CROSSWALK_AI_DRAFTED"
#: FDA acid-food threshold: at or below pH 4.6 a food is treated as acid.
ACID_THRESHOLD = 4.6


@dataclass(frozen=True)
class PhBand:
    ing_id: str
    ing_name: str
    item: str
    ph_low: float
    ph_high: float | None
    value_type: str
    source: str
    source_sha256: str
    confidence: str
    match_basis: str
    ph_applies_to: str
    verify_status: str = VERIFY_STATUS


def _number(text: str) -> float | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


@lru_cache(maxsize=1)
def load_ph_bands() -> dict[str, PhBand]:
    """ING id -> pH band, built from EXACT/FULL crosswalk rows only."""
    with PH_CSV.open(encoding="utf-8", newline="") as fh:
        by_item = {r["item"].strip().lower(): r for r in csv.DictReader(fh)}

    out: dict[str, PhBand] = {}
    with XWALK_CSV.open(encoding="utf-8", newline="") as fh:
        for x in csv.DictReader(fh):
            if x["confidence_band"] != "EXACT" or x["match_basis"] != "FULL":
                continue
            ing = (x["ing_id"] or "").strip()
            if not ing or ing in out:
                continue
            row = by_item.get((x["item_norm"] or "").strip().lower())
            if not row:
                continue
            low = _number(row["ph_low"])
            if low is None:
                continue
            out[ing] = PhBand(
                ing_id=ing,
                ing_name=x.get("ing_canonical_name", ""),
                item=row["item"],
                ph_low=low,
                ph_high=_number(row["ph_high"]),
                value_type=row["value_type"],
                source=row["source"],
                source_sha256=row["source_sha256"],
                confidence=x["confidence_band"],
                match_basis=x["match_basis"],
                ph_applies_to=x.get("ph_applies_to", ""),
            )
    return out


def band_for(ing_id: str) -> PhBand | None:
    """The band for one ingredient, or None. None means UNKNOWN, never a guess."""
    return load_ph_bands().get(ing_id)


def acidity_band(ph_low: float, ph_high: float | None) -> str:
    """Classify an interval against the FDA 4.6 threshold without collapsing it.

    ACIDIC when the whole interval is at or below the threshold, LOW_ACID when all of it is above,
    and INCONCLUSIVE when the interval straddles it or is open on the side that would decide it.
    """
    if ph_high is None:
        return "LOW_ACID" if ph_low > ACID_THRESHOLD else "INCONCLUSIVE_OPEN_INTERVAL"
    if ph_high <= ACID_THRESHOLD:
        return "ACIDIC"
    if ph_low > ACID_THRESHOLD:
        return "LOW_ACID"
    return "INCONCLUSIVE_SPANS_THRESHOLD"
