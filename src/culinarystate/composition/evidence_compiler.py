"""Query-specific evidence compiler (freeze step 3): the canonical compatibility schema, not a fixed triple.

RAG packet v2 reported five hardcoded keys (ingredient, process, salt, acid, lipid). This module
compiles the **canonical 13-axis** schema instead, selects the axes relevant to the target and the
question *before* applicability checking, and leaves an unavailable axis as UNKNOWN with the reason
the registry gives. UNKNOWN is neutral but never silent: it is listed in ``unknown_axes``.

The axis list is never written in code. It is read from ``registry/rag/compatibility_axes_v1.csv``,
which merges SSOT §241.3 (10 axes), MP AO2 (12) and the repo's 9. Owner: Step 36A.3.

Nothing here estimates a value. The compiler reads State v2 cells and the router's own route and
evidence; it never upgrades a route, never invents a number and never turns UNKNOWN into MATCH.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[3]
AXES_CSV = ROOT / "registry/rag/compatibility_axes_v1.csv"

#: Axes relevant to each question kind, selected before retrieval or applicability checking.
#: A numeric retention claim must carry every hard-exclusion axis (1, 3, 10, 11); a composition
#: question does not involve process conditions; FLAVOUR is selectable but unserviceable today
#: because the molecule set (IMAP, 313 ING) is not wired, so it compiles to UNKNOWN, not silence.
QUESTION_AXES: dict[str, tuple[int, ...]] = {
    "RETENTION_NUMERIC": (1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13),
    "PROCESS_EFFECT": (1, 2, 3, 4, 5, 6, 9, 13),
    "COMPOSITION": (1, 2, 10, 11, 12, 13),
    "LEACHING": (1, 2, 3, 4, 5, 6, 8, 9, 11, 13),
    "FLAVOUR": (1, 2, 10, 13),
}


class CompilerError(ValueError):
    """Raised for an unknown question kind. Never raised for missing data: that is UNKNOWN."""


@dataclass(frozen=True)
class Axis:
    axis_no: int
    axis: str
    match_types: tuple[str, ...]
    hard_exclusion: bool
    bracketing_eligible: bool
    implemented: bool
    code_axis_name: str | None
    status: str
    owner_step: str
    unknown_reason: str | None


@lru_cache(maxsize=1)
def load_axes() -> tuple[Axis, ...]:
    """The canonical 13 axes, in registry order. Cached; the registry is append-only."""
    with AXES_CSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 13:
        raise CompilerError(f"{AXES_CSV.name} must hold the canonical 13 axes, found {len(rows)}")
    return tuple(
        Axis(
            axis_no=int(r["axis_no"]),
            axis=r["axis"],
            match_types=tuple(t.strip() for t in r["match_types"].split("|") if t.strip()),
            hard_exclusion=r["hard_exclusion_from_direct"].startswith("yes"),
            bracketing_eligible=r["bracketing_eligible"] == "yes",
            implemented=r["implemented_2026_11_15"] == "yes",
            code_axis_name=r["code_axis_name"] or None,
            status=r["status"],
            owner_step=r["owner_step"],
            unknown_reason=r["unknown_reason_if_absent"] or None,
        )
        for r in rows
    )


def axis_key(axis_no: int) -> str:
    """Stable packet key for an axis, e.g. 4 -> 'ax04_temperature'."""
    axis = _by_no()[axis_no]
    short = axis.axis.split(" (")[0].replace(" / ", "_").replace(" ", "_").lower()
    return f"ax{axis_no:02d}_{short}"


@lru_cache(maxsize=1)
def _by_no() -> dict[int, Axis]:
    return {a.axis_no: a for a in load_axes()}


def axes_by_no() -> dict[int, Axis]:
    """The registry keyed by axis number. Read-only view for callers and tests."""
    return dict(_by_no())


def select_axes(target: str, question_kind: str) -> tuple[int, ...]:
    """Axes to compile for this target and question, chosen before any applicability check."""
    if question_kind not in QUESTION_AXES:
        raise CompilerError(f"Unknown question kind {question_kind!r}; expected one of "
                            f"{sorted(QUESTION_AXES)}")
    return QUESTION_AXES[question_kind]


def _router_compat(state: Mapping[str, Any], target: str) -> Mapping[str, Any]:
    return ((state["Y"].get(f"{target}_compat") or {}).get("v")) or {}


def _cell_status(cell: Mapping[str, Any] | None) -> tuple[str, str | None]:
    """A State v2 cell to (status, reason). A missing or valueless cell is UNKNOWN with its reason."""
    if not cell:
        return "UNKNOWN", "NO_CELL"
    if cell.get("v") is None:
        return "UNKNOWN", cell.get("u") or "NO_REASON_RECORDED"
    return "PRESENT", None


def ph_axis_cell(state: Mapping[str, Any]) -> dict[str, Any]:
    """Axis 7 from the in-repo FDA/CFSAN 2003 pH table, for ingredients the crosswalk resolves EXACTly.

    The band is reported as the interval it is: no midpoint, no clipping. The crosswalk is
    AI_DRAFTED, so the cell says so and human verification is still owed for anything in a figure.
    """
    from culinarystate.composition import ph_bands as PH

    axis = _by_no()[7]
    base = {"axis": axis.axis, "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}
    band = PH.band_for(str(state.get("food_id") or ""))
    if band is None:
        return {**base, "status": "UNKNOWN", "reason": "NO_PH_BAND_FOR_THIS_INGREDIENT"}
    return {**base, "status": "EVALUABLE", "reason": None,
            "ph_low": band.ph_low, "ph_high": band.ph_high, "value_type": band.value_type,
            "acidity": PH.acidity_band(band.ph_low, band.ph_high),
            "item_as_printed": band.item, "basis": PH.BASIS,
            "source": band.source, "source_sha256": band.source_sha256,
            "verify_status": band.verify_status}


def geometry_axis_cell(state: Mapping[str, Any]) -> dict[str, Any]:
    """Axis 9 from ``Q.piece_size_class``, which State v2 already derives from cut history.

    This wires existing state; it produces nothing and estimates nothing. Evidence rows carry no
    geometry field, so the row side of this axis is unavailable and a known query size can never be
    a match. That case is ``QUERY_ONLY``: the query size is reported with its basis and the reason
    the comparison could not be made. Calling it EVALUABLE would breach the freeze invariant that an
    UNKNOWN evidence context must not be treated as a MATCH.
    """
    axis = _by_no()[9]
    base = {"axis": axis.axis, "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}
    status, reason = _cell_status(state["Q"].get("piece_size_class"))
    if status == "UNKNOWN":
        return {**base, "status": "UNKNOWN", "reason": reason or axis.unknown_reason or "NO_CUT_HISTORY"}
    cell = state["Q"]["piece_size_class"]
    return {**base, "status": "QUERY_ONLY", "reason": "NO_ROW_GEOMETRY_FIELD",
            "piece_size_class": cell["v"], "basis": cell.get("b") or "CUT_HISTORY"}


def _axis_cell(axis: Axis, state: Mapping[str, Any], target: str, has_rows: bool) -> dict[str, Any]:
    """One compiled axis. An axis the code does not implement is UNKNOWN with the registry reason."""
    if axis.axis_no == 7:
        return ph_axis_cell(state)
    if axis.axis_no == 9:
        return geometry_axis_cell(state)
    if not axis.implemented:
        return {"status": "UNKNOWN", "reason": axis.unknown_reason or "NOT_IMPLEMENTED",
                "axis": axis.axis, "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}

    router = _router_compat(state, target)
    name = axis.code_axis_name
    if name in router:
        return {"status": router[name], "reason": None, "axis": axis.axis,
                "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}

    # Axes the router does not score per row are read from the state where a cell exists.
    source = {"temperature": state["Q"].get("temperature_C"),
              "time": state["Q"].get("duration_min"),
              "medium": state["Q"].get("medium"),
              "state": state["G"].get("cell_integrity")}.get(name)
    if source is not None:
        status, reason = _cell_status(source)
        if status == "UNKNOWN":
            return {"status": "UNKNOWN", "reason": reason, "axis": axis.axis,
                    "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}
        return {"status": "EVALUABLE", "reason": None, "axis": axis.axis,
                "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}

    if not has_rows:
        return {"status": "UNKNOWN", "reason": "NO_EVIDENCE_ROW", "axis": axis.axis,
                "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}
    return {"status": "NOT_EVALUATED", "reason": "NOT_SCORED_BY_ROUTER", "axis": axis.axis,
            "owner_step": axis.owner_step, "hard_exclusion": axis.hard_exclusion}


def compile_evidence(state: Mapping[str, Any], target: str, question_kind: str) -> dict[str, Any]:
    """Compile the question-relevant axes for one (food, step) state. Returns a new dict."""
    chosen = select_axes(target, question_kind)
    y = state["Y"]
    route = (y.get(f"{target}_route") or {}).get("v") or "UNKNOWN"
    ev = y.get(f"{target}_evidence") or {}
    applied = ev.get("b") == "APPLIED"
    raw_ids = list(ev.get("v") or [])
    evidence_ids = [s.split("=")[0] for s in raw_ids] if applied else []
    near_ids = [] if applied else [s.split("=")[0] for s in raw_ids]

    compatibility = {axis_key(n): _axis_cell(_by_no()[n], state, target, bool(raw_ids)) for n in chosen}
    unknown_axes = tuple(k for k, c in compatibility.items() if c["status"] == "UNKNOWN")

    return {
        "food": state["food"], "step": state["step"], "action": state["action"], "target": target,
        "question_kind": question_kind,
        "selected_axes": list(chosen),
        "compatibility": compatibility,
        "unknown_axes": list(unknown_axes),
        "route": route,
        "route_reasons": (y.get(f"{target}_route") or {}).get("b"),
        "frozen_router_reasons": list((y.get(f"{target}_frozen_reasons") or {}).get("v") or []),
        "evidence_ids": evidence_ids,
        "evidence_values": raw_ids if applied else [],
        "near_evidence_ids": near_ids,
    }
