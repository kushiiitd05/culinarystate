"""DEL-2 course-cell table: explicit projection of EVD rows to (matrix, process, target) + condition masks.

Plan AM1/AM2: the projection is explicit and per source family (USDA %TR/%AR and Phenol-Explorer
RF=(after/before)×yield are different definitions -> separate datasets, never silently merged).
y is the retention factor on the fraction scale (USDA % / 100). RF > 1 is not clipped.
Censored rows (USDA reported 100 = computed ≥ 100, rounding -> ≥ 0.975) keep y_lower and censored=True.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from culinarystate.ledgers.store import LedgerStore

STRUCTURAL_MODS = ("drippings_included", "coating", "cooking_water", "skin", "shell", "medium", "start_state")


def process_signature(e: dict) -> str:
    mods = e["process"].get("modifiers") or {}
    sig = ",".join(f"{k}={mods[k]}" for k in STRUCTURAL_MODS if k in mods)
    return ">".join(e["process"].get("steps", [])) + (f"[{sig}]" if sig else "")


def _rf(e: dict) -> tuple[float | None, float | None, bool]:
    rf = (e.get("derived") or {}).get("retention_factor") or {}
    scale = 0.01 if rf.get("unit") == "%" else 1.0
    if rf.get("status") == "MEASURED":
        return rf["value"] * scale, None, False
    if rf.get("status") == "CENSORED":
        return None, (rf.get("censor") or {}).get("limit", 0) * scale, True
    return None, None, False


@dataclass(frozen=True)
class CellTable:
    df: pd.DataFrame
    source_family: str


def build_cells(store: LedgerStore, source_family: str) -> CellTable:
    cond = {c["id"]: c for c in store.all_latest("COND")}
    return cells_from_rows(store.all_latest("EVD"), cond, source_family)


def cells_from_rows(evd_rows, cond: dict, source_family: str) -> CellTable:
    """Same table as build_cells, from caller-supplied EVD rows (S173: 29-diag passes seal-filtered rows)."""
    rows = []
    for e in evd_rows:
        if e["source_family_id"] != source_family or e["status"] != "ACTIVE":
            continue
        y, y_lower, censored = _rf(e)
        if y is None and not censored:
            continue
        c = cond.get(e["process"].get("condition_id") or "", {})
        mask = c.get("completeness_mask", {})
        steps = e["process"].get("steps", [])
        rows.append({
            "evd_id": e["id"], "matrix": e["matrix"]["raw_name"].lower(),
            "matrix_form": e["matrix"].get("form") or "", "food_group": e["matrix"].get("food_group") or "",
            "ingredient_id": e["matrix"].get("ingredient_id"), "process": process_signature(e),
            "process_family": steps[0] if steps else "", "n_steps": len(steps),
            "target": e["target"]["raw_name"].lower(), "basis": e["target"]["basis"],
            "y": y, "y_lower": y_lower, "censored": censored,
            "group": e.get("independence_group") or e["source_family_id"],
            "study": (e.get("study_ids") or [None])[0],
            "duration_known": mask.get("duration") in ("MEASURED", "RANGE"),
            "temperature_known": mask.get("temperature") in ("MEASURED", "RANGE"),
            "medium": c.get("medium") or "",
        })
    return CellTable(pd.DataFrame(rows), source_family)


def y_train(df: pd.DataFrame) -> pd.Series:
    """Training target. Assumption (recorded in experiment cards): censored rows use their lower bound."""
    return df["y"].where(~df["censored"], df["y_lower"])
