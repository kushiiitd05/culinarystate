"""Value records for the lot-state layer: (value | interval, unit, type, mask, basis, provenance), SSOT 199.5 / 199.7.

type is one of POINT | INTERVAL | QUALITATIVE | UNKNOWN. mask is 1 when a value (or a stated qualitative label) is
present and 0 when UNKNOWN. UNKNOWN is never 0 and never imputed. Every record carries the labels
MODEL_DERIVED and NON_CITABLE (the lot-state layer is a reference-data calculation, not a measurement).
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

from .intervals import float_hi, float_lo

TYPES = ("POINT", "INTERVAL", "QUALITATIVE", "UNKNOWN")
LABELS = ("MODEL_DERIVED", "NON_CITABLE")
BASIS_STATED_MASS = "STATED_MASS"
BASIS_SR_PORTION = "SR_PORTION"
BASIS_UNKNOWN = "UNKNOWN"
LINE_BASES = (BASIS_STATED_MASS, BASIS_SR_PORTION, BASIS_UNKNOWN)
Q_STATED_MASS = "Q0"
Q_SR_PORTION = "Q2_PROPOSED"   # PROPOSED pending a human ruling (packet Q9); below stated mass (Q0)
Q_UNKNOWN = "Q6"


def provenance(method: str, *, inputs: tuple[str, ...] = (), source_ids: tuple[str, ...] = (),
               flags: tuple[str, ...] = (), **extra: Any) -> dict:
    out = {"method": method, "labels": list(LABELS), "inputs": list(inputs), "source_ids": list(source_ids),
           "flags": list(flags), "verification": "AI_DRAFTED_UNVERIFIED"}
    out.update(extra)
    return out


def numeric(lo: Fraction | None, hi: Fraction | None, unit: str, *, basis: str, prov: Mapping,
            open_upper: bool = False) -> dict:
    """POINT when lo == hi, else INTERVAL. Float bounds are rounded outward; ``exact`` keeps the rationals."""
    if lo is None:
        raise ValueError("numeric() needs a lower bound; use unknown()")
    if hi is not None and lo == hi:
        return {"type": "POINT", "mask": 1, "value": float(lo), "low": float_lo(lo), "high": float_hi(lo),
                "unit": unit, "basis": basis, "provenance": dict(prov), "exact": [str(lo), str(hi)]}
    rec = {"type": "INTERVAL", "mask": 1, "low": float_lo(lo), "high": None if hi is None else float_hi(hi),
           "unit": unit, "basis": basis, "provenance": dict(prov), "exact": [str(lo), None if hi is None else str(hi)]}
    if hi is None or open_upper:
        rec["open_upper"] = True
    return rec


def unknown(unit: str | None, reason: str, *, basis: str = BASIS_UNKNOWN, prov: Mapping | None = None) -> dict:
    return {"type": "UNKNOWN", "mask": 0, "unit": unit, "basis": basis, "reason": reason,
            "provenance": dict(prov or provenance("NONE"))}


def qualitative(label: str, *, basis: str, prov: Mapping, unit: str | None = None) -> dict:
    return {"type": "QUALITATIVE", "mask": 1, "label": label, "unit": unit, "basis": basis, "provenance": dict(prov)}


def check_record(rec: Mapping) -> None:
    """Contract check used by the tests and the census (raises ValueError)."""
    if rec.get("type") not in TYPES:
        raise ValueError("bad type")
    if "mask" not in rec or "basis" not in rec or "provenance" not in rec or "unit" not in rec:
        raise ValueError("record lacks mask / basis / provenance / unit")
    if rec["type"] == "UNKNOWN" and (rec["mask"] != 0 or rec.get("value") is not None):
        raise ValueError("UNKNOWN must have mask 0 and no value")
    if rec["type"] in ("POINT", "INTERVAL", "QUALITATIVE") and rec["mask"] != 1:
        raise ValueError("known record must have mask 1")
    labels = rec["provenance"].get("labels") or []
    if "MODEL_DERIVED" not in labels or "NON_CITABLE" not in labels:
        raise ValueError("derived value must carry MODEL_DERIVED and NON_CITABLE")
    if rec["type"] == "INTERVAL" and rec.get("high") is not None and rec["low"] > rec["high"]:
        raise ValueError("inverted interval")


def compact(rec: Mapping) -> dict:
    """Per-lot storage form: drops the per-value provenance and exact rationals (kept once at lot level)."""
    out = {k: rec[k] for k in ("type", "mask", "unit", "basis") if k in rec}
    for k in ("value", "low", "high", "label", "reason", "open_upper"):
        if k in rec and rec[k] is not None:
            out[k] = rec[k]
    return out
