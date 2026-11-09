"""DEL-2 course-cell table: explicit projection of EVD rows to (matrix, process, target) + condition masks.

Plan AM1/AM2: the projection is explicit and per source family (USDA %TR/%AR and Phenol-Explorer
RF=(after/before)×yield are different definitions -> separate datasets, never silently merged).
y is the retention factor on the fraction scale (USDA % / 100). RF > 1 is not clipped.
Censored rows (USDA reported 100 = computed ≥ 100, rounding -> ≥ 0.975) keep y_lower and censored=True.

Firewall (S178 FIX-GOV, GOV-10 / board T6-C09-R2; TB-V0 contract section 1; SSOT 222.9; law 1), pinned by
tests/unit/test_transition_firewall.py:
  * only evidence tiers E1-E4 enter; E5-E7 and a missing or unknown tier are refused;
  * a Layer-2 / scenario / simulated / assumed-default row is refused whatever its tier;
  * an imputed-target row (evidence class "I", SSOT 222.9) never enters a table that feeds test, validation or
    calibration; only an explicit role="train" table may hold it;
  * CENSORED with no usable limit is UNKNOWN (no row; never a zero bound); a GT_* limit is a lower bound; an LT_* limit
    is an upper bound and is never stored as y_lower (the v0 table holds lower-bound censoring only, so the row is left
    out); any other censor kind is UNKNOWN;
  * every refused row is counted in CellTable.excluded by reason code.
On the real ledger (all rows E3, censored rows all GT_CAP with a limit) none of these rules removes a row.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, NamedTuple

import pandas as pd

from culinarystate.ledgers.store import LedgerStore

STRUCTURAL_MODS = ("drippings_included", "coating", "cooking_water", "skin", "shell", "medium", "start_state")
COLUMNS = ["evd_id", "matrix", "matrix_form", "food_group", "ingredient_id", "process", "process_family", "n_steps", "target", "basis",
           "y", "y_lower", "censored", "group", "study", "duration_known", "temperature_known", "medium"]
TB_V0_TIERS = ("E1", "E2", "E3", "E4")          # TB-V0 contract section 1: E5-E7 excluded, no simulated rows
IMPUTED_CLASS = "I"                              # SSOT 222.9: imputed-target training tier, never validation/test/calibration
ROLES = ("all", "train", "validation", "test", "calibration")   # "all": the table feeds every split role (split later)
LAYER2_MARKERS = ("SCENARIO", "LAYER_2", "LAYER2", "LAYER 2", "MODEL_DERIVED", "ASSUMED_DEFAULT", "SIMULAT")   # substrings
LAYER2_TOKENS = ("L2",)                                                                                  # whole values


def process_signature(e: dict) -> str:
    mods = e["process"].get("modifiers") or {}
    sig = ",".join(f"{k}={mods[k]}" for k in STRUCTURAL_MODS if k in mods)
    return ">".join(e["process"].get("steps", [])) + (f"[{sig}]" if sig else "")


def tier_allowed(tier: Any, role: str) -> bool:
    """E1-E4 may take any role; the imputed class I only a training role; anything else (E5-E7, missing) none."""
    if tier in TB_V0_TIERS:
        return True
    return tier == IMPUTED_CLASS and role == "train"


def _num(x: Any) -> float | None:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    return float(x)


class RF(NamedTuple):
    """Retention factor on the fraction scale. status: MEASURED | CENSORED_LOWER | CENSORED_UPPER | UNKNOWN."""
    status: str
    y: float | None
    lower: float | None
    upper: float | None
    reason: str | None


def retention_bounds(e: Mapping) -> RF:
    """The retention value of one EVD row with its censoring side; UNKNOWN (never 0) when a value or limit is missing."""
    rf = (e.get("derived") or {}).get("retention_factor") or {}
    scale = 0.01 if rf.get("unit") == "%" else 1.0
    st = rf.get("status")
    if st == "MEASURED":
        v = _num(rf.get("value"))
        return RF("MEASURED", v * scale, None, None, None) if v is not None else RF("UNKNOWN", None, None, None, "NO_RETENTION_VALUE")
    if st == "CENSORED":
        cen = rf.get("censor") or {}
        lim = _num(cen.get("limit"))
        if lim is None:
            return RF("UNKNOWN", None, None, None, "CENSOR_LIMIT_MISSING")
        kind = str(cen.get("kind") or "")
        if kind.startswith("GT_"):
            return RF("CENSORED_LOWER", None, lim * scale, None, None)
        if kind.startswith("LT_"):
            return RF("CENSORED_UPPER", None, None, lim * scale, "LEFT_CENSORED_UPPER_BOUND_NOT_IN_V0_TABLE")
        return RF("UNKNOWN", None, None, None, "CENSOR_KIND_UNKNOWN")
    return RF("UNKNOWN", None, None, None, "NO_RETENTION_VALUE")


def _rf(e: dict) -> tuple[float | None, float | None, bool]:
    """(y, y_lower, censored) for the v0 table; an upper bound or an UNKNOWN gives (None, None, False)."""
    b = retention_bounds(e)
    if b.status == "MEASURED":
        return b.y, None, False
    if b.status == "CENSORED_LOWER":
        return None, b.lower, True
    return None, None, False


def _strings(x: Any):
    if isinstance(x, str):
        yield x
    elif isinstance(x, Mapping):
        for v in x.values():
            yield from _strings(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from _strings(v)


def is_layer2_or_simulated(e: Mapping) -> bool:
    """True when the row says it is a Layer-2 / scenario / simulated / assumed-default value (law 2: never a measurement)."""
    rf = (e.get("derived") or {}).get("retention_factor") or {}
    fields = [e.get("layer"), e.get("origin_type"), e.get("record_type"), rf.get("layer"), rf.get("basis"), rf.get("label"),
              rf.get("labels"), (e.get("provenance") or {}).get("labels"), (e.get("provenance") or {}).get("layer")]
    vals = [v.strip().upper() for f in fields for v in _strings(f)]
    return any(v in LAYER2_TOKENS or any(m in v for m in LAYER2_MARKERS) for v in vals)


def refusal_reason(e: Mapping, role: str = "all") -> str | None:
    """Why an ACTIVE row of the right family cannot be a cell for ``role`` (None: it can, if it has a value)."""
    tier = e.get("tier")
    if not tier_allowed(tier, role):
        return "IMPUTED_CLASS_I_NOT_IN_HOLDOUT_ROLES" if tier == IMPUTED_CLASS else "TIER_NOT_E1_E4"
    if is_layer2_or_simulated(e):
        return "LAYER2_OR_SIMULATED"
    return None


@dataclass(frozen=True)
class CellTable:
    df: pd.DataFrame
    source_family: str
    excluded: Mapping[str, int] = field(default_factory=dict)   # refused rows of this family by reason code


def build_cells(store: LedgerStore, source_family: str) -> CellTable:
    cond = {c["id"]: c for c in store.all_latest("COND")}
    return cells_from_rows(store.all_latest("EVD"), cond, source_family)


def cells_from_rows(evd_rows, cond: dict, source_family: str, *, role: str = "all") -> CellTable:
    """Same table as build_cells, from caller-supplied EVD rows (S173: 29-diag passes seal-filtered rows).

    ``role``: which split role the table feeds; the default "all" (split later) admits E1-E4 only.
    """
    if role not in ROLES:
        raise ValueError(f"role must be one of {ROLES}")
    rows = []
    excluded: Counter = Counter()
    for e in evd_rows:
        if e["source_family_id"] != source_family or e["status"] != "ACTIVE":
            continue
        why = refusal_reason(e, role)
        if why is not None:
            excluded[why] += 1
            continue
        b = retention_bounds(e)
        if b.status not in ("MEASURED", "CENSORED_LOWER"):
            excluded[b.reason or "NO_RETENTION_VALUE"] += 1
            continue
        y, y_lower, censored = _rf(e)
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
    return CellTable(pd.DataFrame(rows, columns=COLUMNS) if not rows else pd.DataFrame(rows), source_family, dict(sorted(excluded.items())))


def y_train(df: pd.DataFrame) -> pd.Series:
    """Training target. Assumption (recorded in experiment cards): censored rows use their lower bound."""
    return df["y"].where(~df["censored"], df["y_lower"])
