"""Seeded-copy recall test for the duplicate detector (G08-4, THR-08A-05 / THR-08A-17).

Pure deterministic functions. Seeded copies are SCRATCH ONLY: every copy carries SEEDED_MARKER and
`refuse_if_seeded` must be called by any code path that could write to a ledger.
Perturbation classes (THR-08A-17): exact copy; unit conversion; rounding to 1-2 significant figures;
percent <-> fraction; fresh <-> dry weight conversion; subset or reordered rows; a one-cell transcription error.
"""
from __future__ import annotations

import copy as _copy
import random
from typing import Any, Callable, Mapping

from culinarystate.lineage.wilson import wilson_lower

SEEDED_MARKER = "SEEDED_SCRATCH_ONLY"
PERTURBATION_CLASSES = (
    "EXACT_COPY",
    "UNIT_CONVERSION",
    "ROUNDING_1_2_SF",
    "PERCENT_FRACTION",
    "FRESH_DRY_WEIGHT",
    "SUBSET_OR_REORDERED",
    "ONE_CELL_ERROR",
)
MIN_SEEDS_PER_CLASS = 60  # THR-08A-17
LB_FLOOR = 0.90  # THR-08A-17 per-class Wilson 95% lower bound
POINT_FLOOR = 0.95  # THR-08A-05 point recall

# multiplier m such that value_in_to_unit = value_in_from_unit * m
UNIT_FACTORS: dict[tuple[str, str], float] = {
    ("mg/100g", "g/100g"): 0.001,
    ("g/100g", "mg/100g"): 1000.0,
    ("ug/100g", "mg/100g"): 0.001,
    ("mg/100g", "ug/100g"): 1000.0,
    ("g/100g", "ug/100g"): 1_000_000.0,
    ("ug/100g", "g/100g"): 1e-6,
}
_MASS_UNITS = ("mg/100g", "g/100g", "ug/100g")
_UNIT_TARGET = {"mg/100g": "g/100g", "g/100g": "mg/100g", "ug/100g": "mg/100g"}
_ANALYTES = ("vitamin_c", "folate", "beta_carotene", "lycopene", "quercetin", "lutein", "thiamin", "riboflavin")


class SeededRecordError(ValueError):
    """A seeded (scratch-only) record was used where it must never go."""


def is_seeded(record: Mapping[str, Any]) -> bool:
    return bool(record.get(SEEDED_MARKER))


def refuse_if_seeded(record: Mapping[str, Any]) -> None:
    """Guard for any ledger-writing path."""
    if is_seeded(record):
        raise SeededRecordError(f"seeded record {record.get('record_id')} must never be written to a ledger")


def _rng(*parts: object) -> random.Random:
    return random.Random(":".join(str(p) for p in parts))


def make_synthetic_record(seed: int, index: int, kind: str = "mass") -> dict[str, Any]:
    """Synthetic evidence-row-like record (4-8 rows). kind: 'mass' (mass/100g units) or 'proportion' (% or fraction)."""
    if kind not in ("mass", "proportion"):
        raise ValueError(f"kind must be 'mass' or 'proportion', got {kind!r}")
    r = _rng("rec", seed, index, kind)
    n = r.randint(4, 8)
    basis = r.choice(("fresh", "dry"))
    if kind == "mass":
        unit = r.choice(_MASS_UNITS)
    else:
        unit = r.choice(("%", "fraction"))
    rows = []
    for analyte in r.sample(_ANALYTES, n):
        v = round(r.uniform(1.0, 99.0), 3) if unit != "fraction" else round(r.uniform(0.01, 0.99), 4)
        rows.append({"analyte": analyte, "value": v, "unit": unit, "basis": basis})
    return {
        "record_id": f"SYN-{seed}-{index}",
        "matrix": r.choice(("spinach", "carrot", "tomato", "broccoli", "potato")),
        "moisture_fraction": round(r.uniform(0.60, 0.95), 3),
        "rows": rows,
    }


def _copy_base(original: Mapping[str, Any], cls: str) -> dict[str, Any]:
    c = _copy.deepcopy(dict(original))
    c["record_id"] = f"SEEDED-{original['record_id']}-{cls}"
    c[SEEDED_MARKER] = True
    c["seeded_class"] = cls
    c["seeded_from"] = original["record_id"]
    return c


def _round_sf(x: float, sf: int) -> float:
    return float(f"{x:.{sf}g}")


def _transcription_error(v: float, r: random.Random) -> float:
    s = f"{v:.3f}"
    pos = [i for i, ch in enumerate(s) if ch.isdigit()]
    i = r.choice(pos)
    new = r.choice([d for d in "0123456789" if d != s[i]])
    return float(s[:i] + new + s[i + 1:])


def perturb(original: Mapping[str, Any], cls: str, seed: int) -> dict[str, Any]:
    """Return a new marked copy of `original` perturbed per class `cls`; the original is never mutated."""
    if cls not in PERTURBATION_CLASSES:
        raise ValueError(f"unknown perturbation class {cls!r}")
    r = _rng("perturb", seed, cls, original["record_id"])
    c = _copy_base(original, cls)
    rows = c["rows"]
    if cls == "EXACT_COPY":
        pass
    elif cls == "UNIT_CONVERSION":
        for row in rows:
            to = _UNIT_TARGET[row["unit"]]
            row["value"] = row["value"] * UNIT_FACTORS[(row["unit"], to)]
            row["unit"] = to
    elif cls == "ROUNDING_1_2_SF":
        sf = r.choice((1, 2))
        for row in rows:
            row["value"] = _round_sf(row["value"], sf)
    elif cls == "PERCENT_FRACTION":
        for row in rows:
            if row["unit"] == "%":
                row["value"], row["unit"] = row["value"] / 100.0, "fraction"
            elif row["unit"] == "fraction":
                row["value"], row["unit"] = row["value"] * 100.0, "%"
            else:
                raise ValueError("PERCENT_FRACTION needs rows with unit '%' or 'fraction'")
    elif cls == "FRESH_DRY_WEIGHT":
        w = original["moisture_fraction"]
        for row in rows:
            if row["basis"] == "fresh":
                row["value"], row["basis"] = row["value"] / (1.0 - w), "dry"
            else:
                row["value"], row["basis"] = row["value"] * (1.0 - w), "fresh"
    elif cls == "SUBSET_OR_REORDERED":
        n = len(rows)
        while True:
            k = r.randint(2, n)
            idx = r.sample(range(n), k)
            if idx != list(range(k)):
                break
        c["rows"] = [rows[i] for i in idx]
    else:  # ONE_CELL_ERROR
        row = rows[r.randrange(len(rows))]
        row["value"] = _transcription_error(row["value"], r)
    return c


def generate_seeded_pairs(seed: int, n_per_class: int = MIN_SEEDS_PER_CLASS) -> list[dict[str, Any]]:
    """>= 60 (original, seeded copy) pairs per class, deterministic in `seed`."""
    if n_per_class < MIN_SEEDS_PER_CLASS:
        raise ValueError(f"n_per_class must be >= {MIN_SEEDS_PER_CLASS} (THR-08A-17), got {n_per_class}")
    out = []
    for ci, cls in enumerate(PERTURBATION_CLASSES):
        kind = "proportion" if cls == "PERCENT_FRACTION" else "mass"
        for i in range(n_per_class):
            orig = make_synthetic_record(seed, ci * 100_000 + i, kind=kind)
            out.append({"seeded_class": cls, "original": orig, "copy": perturb(orig, cls, seed=seed * 1_000_003 + i)})
    return out


def seeded_recall(pairs: list[Mapping[str, Any]], detector: Callable[[Any, Any], bool]) -> dict[str, Any]:
    """Per-class recall with Wilson 95% lower bound. `detector(original, copy) -> bool` (True = duplicate edge proposed).

    A class passes iff Wilson LB >= 0.90 AND point recall >= 0.95 (THR-08A-17 / THR-08A-05)."""
    tally: dict[str, list[int]] = {cls: [0, 0] for cls in PERTURBATION_CLASSES}
    for p in pairs:
        if not is_seeded(p["copy"]):
            raise SeededRecordError("recall pair copy lacks the seeded marker")
        cls = p["seeded_class"]
        if cls not in tally:
            raise ValueError(f"unknown perturbation class {cls!r}")
        tally[cls][1] += 1
        tally[cls][0] += 1 if detector(p["original"], p["copy"]) else 0
    classes = {}
    for cls, (hits, n) in tally.items():
        recall = hits / n if n else 0.0
        lb = wilson_lower(hits, n)
        classes[cls] = {"hits": hits, "n": n, "recall": recall, "wilson_lower": lb,
                        "passes": bool(n >= MIN_SEEDS_PER_CLASS and lb >= LB_FLOOR and recall >= POINT_FLOOR)}
    return {"classes": classes, "all_pass": all(v["passes"] for v in classes.values())}
