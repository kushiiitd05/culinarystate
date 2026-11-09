"""Physical record schema and validator (S178 PHYS2, T4-C02-R2). DRAFT, AI_DRAFTED.

Every field of a physical-layer record is the SSOT tuple (value, unit, type, mask, provenance), stored flat:

- Layer 1 (TEXT_STATED) axis: ``value`` (None when unknown), ``status`` (MEASURED, RANGE, BOUND_UPPER, BOUND_LOWER, QUALITATIVE,
  UNKNOWN = the mask), ``basis`` (how the value was fixed), ``span`` (characters of the joined step text, or None), ``span_id``
  (``C:a-b`` characters, ``E:<event>`` an event verb, ``L:<event>`` the lots the event consumes) and ``row`` (the registry row or the
  code rule that fixed it). An UNKNOWN axis has value None, basis None and a ``reason`` code (the provenance of the absence).
  Units are fixed by the axis (``recipe_adapter.INPUT_SPECS`` for the heat inputs; deg C, minutes, fractions elsewhere).
- Layer 2 (SCENARIO) bracket record: every INPUT field has an entry in ``bases`` (``L1:<basis>`` = taken from Layer 1,
  ``SD-n`` scenario default, ``KGE-n`` corpus duration quantile, ``NH-n`` non-heat default, ``PC-n`` phase-change row; ``|`` and ``+``
  join a stated bound or a stated liquid temperature with the row it overrides); every OUTPUT field is MODEL_DERIVED (record labels
  SCENARIO, MODEL_DERIVED, NON_CITABLE, ASSUMED_DEFAULT) and names the inputs it derives from (``HEAT_DERIVED_FROM``); the record
  carries ``l1_provenance`` (basis, span id, row of the Layer 1 axes used).

``check`` tallies one record; ``Tally.problems`` is empty when 100 % of the fields carry their provenance. The validator reads
records only; it holds no scientific value.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import endpoint_cues as EC

VERSION = "physical-record-schema-1.0.0-draft"
KINDS = ("L1_HEAT", "L1_NONHEAT", "L2_HEAT", "L2_NONHEAT")
STATUSES = ("MEASURED", "RANGE", "BOUND_UPPER", "BOUND_LOWER", "QUALITATIVE", "UNKNOWN")
L1_BASES = ("TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION", "PROCESS_DEFINITION", "CUE", "CUT_HISTORY", "FOOD_GROUP",
            "TEXT_CUE", "LINEAGE", "ORDER_ADJACENT", "LINEAGE_AND_STATED_DURATIONS")
SPAN_ID = re.compile(r"^(?:C:\d+-\d+|E:[\w.-]+|L:[\w.-]+)$")
_TOKEN = re.compile(r"^(?:(?:HEAT_)?L1:[A-Z_]+|(?:SD|KGE|NH|PC)-\d+)$")
LABELS = ("SCENARIO", "MODEL_DERIVED", "NON_CITABLE", "ASSUMED_DEFAULT")
# heat Layer 2 bracket record: input fields (basis in ``bases``), output fields (derived from which inputs), bookkeeping
HEAT_INPUT_FIELDS = {"bath_c": "bath_c", "duration_min": "duration_min", "initial_c": "initial_c", "h": "h",
                     "half_thickness_m": "half_thickness_m", "t_cap_c": "t_cap_c"}
_CORE = ("bath_c", "duration_min", "initial_c", "h", "half_thickness_m", "k", "alpha")
HEAT_DERIVED_FROM: dict[str, tuple[str, ...]] = {
    "boundary_c": ("bath_c",), "surface_state": ("bath_c",), "surface_cook_value_min": ("bath_c", "duration_min"),
    "core_end_c": _CORE, "core_minutes_above_70": _CORE, "core_cook_value_min": _CORE, "volume_avg_end_c": _CORE,
    "cook_value_at_volume_avg_t_min": _CORE, "quality_cook_value_min": _CORE, "zone_mean_cook_value_min": _CORE,
    "zone_nodes": _CORE}
HEAT_BOOKKEEPING = ("bases", "flags")
# L2 input field -> Layer 1 axis whose provenance it must carry when its basis starts with L1:
L1_AXIS_OF = {"bath_c": "temperature_profile", "t_cap_c": "temperature_profile", "duration_min": "duration"}
# non-heat Layer 2: declared output fields per family (every other field must be an input with a basis)
NONHEAT_OUTPUTS = {
    "MECHANICAL_CUT": ("surface_to_volume_cube_per_m", "surface_to_volume_slab_per_m", "disruption_level", "enzyme_system_candidate",
                       "time_until_next_heat", "time_until_next_heat_status", "cut_class", "half_thickness_m"),
    "SEPARATION": ("handoff", "liquid_removed_fraction"), "MECHANICAL_MIX": ("state_flags",),
    "COOLING": ("core_end_c", "core_minutes_above_5c", "core_minutes_above_60c", "freezing_point_c", "freezing_time_min",
                "frozen_within_stated_duration", "thaw_time_min", "thawed_within_stated_duration", "thickness_m", "medium_c",
                "minutes_to_target_food_c",
                "duration_min", "h", "half_thickness_m", "initial_c"),
    "STORAGE": ("duration_bound_min", "duration_bound_status", "kinetics", "storage_c"),
    "FERMENT_LEAVEN": ("D_eff_m2_s", "duration_min", "fourier_number", "half_thickness_m", "state_flags", "uptake_fraction"),
    "RESTING": ("core_end_of_heat_c", "core_peak_c", "carryover_rise_c", "core_end_c", "surface_end_c", "volume_avg_end_c",
                "volume_avg_end_of_heat_c", "boundary_c"),
    "PRESERVATION": ("state_flags", "wet_bulb_c", "constant_rate_end_min", "falling_rate_tau_min", "water_removed_fraction",
                     "moisture_ratio", "time_class", "fourier_number", "uptake_fraction", "f0_upper_bound_at_medium_t_min", "f0_min")}


class Tally(Counter):
    """Counts of fields checked and of problems found (``problems`` = the problem codes with their counts)."""

    @property
    def problems(self) -> dict[str, int]:
        return {k[1]: v for k, v in self.items() if k[0] == "problem"}


def _l1_axis(t: Tally, kind: str, axis: str, x: Mapping[str, Any]) -> None:
    if x.get("status") not in STATUSES:
        t[("problem", "L1_BAD_STATUS")] += 1
        return
    if x["status"] == "UNKNOWN":
        t[(kind, "unknown_axes")] += 1
        ok = x.get("value") is None and x.get("basis") is None and bool(x.get("reason"))
        t[(kind, "unknown_axes_with_reason")] += 1 if x.get("reason") else 0
        if not ok:
            t[("problem", "L1_UNKNOWN_NEEDS_NULL_VALUE_NULL_BASIS_AND_REASON")] += 1
        return
    t[(kind, "bound_axes")] += 1
    if x.get("value") is None:
        t[("problem", "L1_BOUND_WITHOUT_VALUE")] += 1
    if x.get("basis") in L1_BASES:
        t[(kind, "bound_with_basis")] += 1
    else:
        t[("problem", "L1_BASIS_MISSING_OR_UNKNOWN_CODE")] += 1
    sid = x.get("span_id")
    if sid and SPAN_ID.match(sid) and (x.get("span") is None or sid == f"C:{x['span'][0]}-{x['span'][1]}"):
        t[(kind, "bound_with_span_id")] += 1
    else:
        t[("problem", "L1_SPAN_ID_MISSING_OR_INCONSISTENT")] += 1
    if x.get("row"):
        t[(kind, "bound_with_row")] += 1
    else:
        t[("problem", "L1_ROW_MISSING")] += 1


def _l1(t: Tally, kind: str, rec: Mapping[str, Any]) -> None:
    t[(kind, "records")] += 1
    for axis, x in rec.get("inputs", {}).items():
        if axis in EC.ENDPOINT_FIELDS:
            t[("problem", "ENDPOINT_FIELD_IN_INPUTS")] += 1
        _l1_axis(t, kind, axis, x)
    if kind == "L1_HEAT":
        blk = rec.get(EC.BLOCK_KEY)
        if not isinstance(blk, Mapping) or "stopping_criterion" not in blk or "cues" not in blk:
            t[("problem", "ENDPOINT_BLOCK_MISSING")] += 1
        else:
            t[(kind, "endpoint_blocks")] += 1
            classes = set(EC.classes())
            for c in blk["cues"]:
                if c.get("class") not in classes or not (isinstance(c.get("span"), list) and len(c["span"]) == 2):
                    t[("problem", "ENDPOINT_CUE_BAD_CLASS_OR_SPAN")] += 1
            sc = blk["stopping_criterion"]
            if sc.get("status") == "QUALITATIVE" and not (sc.get("span") and sc.get("basis") == "TEXT_CUE"):
                t[("problem", "ENDPOINT_CRITERION_WITHOUT_SPAN")] += 1
    else:
        link = (rec.get("history") or {}).get("prior_heat")
        if link:
            for axis, x in link.get("inputs", {}).items():
                _l1_axis(t, "L1_NONHEAT_PRIOR_HEAT_LINK", axis, x)


def _bases_ok(t: Tally, kind: str, bases: Mapping[str, Any]) -> None:
    for k, v in bases.items():
        toks = [p for p in re.split(r"[+|]", str(v)) if p]
        toks = [re.sub(r"_BOUND$", "", p) for p in toks]
        flat = [q for p in toks for q in re.split(r"\.\.", p)]
        if v and all(_TOKEN.match(q) or re.fullmatch(r"\d+", q) for q in flat):
            t[(kind, "basis_entries_valid")] += 1
        else:
            t[("problem", "L2_BASIS_CODE_INVALID")] += 1
        t[(kind, "basis_entries")] += 1


def _l2_common(t: Tally, kind: str, rec: Mapping[str, Any]) -> None:
    t[(kind, "records")] += 1
    if not set(LABELS) <= set(rec.get("labels", ())):
        t[("problem", "L2_LABELS_MISSING")] += 1
    if not isinstance(rec.get("l1_provenance"), Mapping):
        t[("problem", "L2_L1_PROVENANCE_MISSING")] += 1


def _l2_heat(t: Tally, rec: Mapping[str, Any]) -> None:
    kind = "L2_HEAT"
    _l2_common(t, kind, rec)
    prov = rec.get("l1_provenance") or {}
    for b, sc in (rec.get("scenarios") or {}).items():
        t[(kind, "bracket_records")] += 1
        bases = sc.get("bases") or {}
        _bases_ok(t, kind, bases)
        for f, v in sc.items():
            if f in HEAT_BOOKKEEPING or v is None:  # None = not applicable (no cap on a dry matrix, no core without a size)
                continue
            if f in HEAT_INPUT_FIELDS:
                t[(kind, "input_fields")] += 1
                if bases.get(f):
                    t[(kind, "input_fields_with_basis")] += 1
                    if str(bases[f]).startswith("L1:"):
                        ax = L1_AXIS_OF.get(f)
                        if ax and not (prov.get(ax) or {}).get("span_id"):
                            t[("problem", "L2_L1_INPUT_WITHOUT_L1_SPAN_ID")] += 1
                else:
                    t[("problem", "L2_INPUT_FIELD_WITHOUT_BASIS")] += 1
            elif f in HEAT_DERIVED_FROM:
                t[(kind, "output_fields")] += 1
                if all(bases.get(k) for k in HEAT_DERIVED_FROM[f]):
                    t[(kind, "output_fields_traceable_to_input_bases")] += 1
                else:
                    t[("problem", "L2_OUTPUT_NOT_TRACEABLE_TO_INPUT_BASES")] += 1
            else:
                t[("problem", "L2_UNDECLARED_FIELD")] += 1
                t[("undeclared", f"HEAT__{f}")] += 1
        for k in ("k", "alpha"):
            if k not in bases:
                t[("problem", "L2_PROPERTY_WITHOUT_BASIS")] += 1


def _l2_nonheat(t: Tally, rec: Mapping[str, Any]) -> None:
    kind = "L2_NONHEAT"
    _l2_common(t, kind, rec)
    fam = rec.get("nh_family")
    outs = set(NONHEAT_OUTPUTS.get(fam, ()))
    for b, sc in (rec.get("scenarios") or {}).items():
        t[(kind, "bracket_records")] += 1
        bases = sc.get("bases") or {}
        _bases_ok(t, kind, bases)
        for f, v in sc.items():
            if f in ("bases", "flags") or v is None:
                continue
            if f in bases:  # an input field: its basis is its provenance
                t[(kind, "input_fields")] += 1
                t[(kind, "input_fields_with_basis")] += 1
            elif f in outs:
                t[(kind, "output_fields")] += 1
                if bases:
                    t[(kind, "output_fields_with_input_bases")] += 1
                else:
                    t[("problem", "L2_NONHEAT_OUTPUT_WITHOUT_ANY_INPUT_BASIS")] += 1
            else:
                t[("problem", "L2_UNDECLARED_FIELD")] += 1
                t[("undeclared", f"{fam}__{f}")] += 1
        # state_flags come from the verb itself (record-level process id, not a Layer 1 axis): no axis provenance to carry
        if any(str(v).startswith("L1:") for k, v in bases.items() if k != "state_flags") and not (rec.get("l1_provenance") or {}):
            t[("problem", "L2_L1_INPUT_WITHOUT_L1_PROVENANCE")] += 1


def check(kind: str, rec: Mapping[str, Any], t: Tally | None = None) -> Tally:
    """Tally one record of ``kind`` (one of KINDS)."""
    t = t if t is not None else Tally()
    if kind in ("L1_HEAT", "L1_NONHEAT"):
        _l1(t, kind, rec)
    elif kind == "L2_HEAT":
        _l2_heat(t, rec)
    elif kind == "L2_NONHEAT":
        _l2_nonheat(t, rec)
    else:
        raise ValueError(f"kind must be one of {KINDS}")
    return t


def summary(t: Tally) -> dict:
    """Counts-only summary: per kind the counts and the 100 % ratios, plus the problem codes."""
    out: dict = {}
    for (kind, name), v in sorted((k, v) for k, v in t.items() if k[0] not in ("problem", "undeclared")):
        out.setdefault(kind, {})[name] = v
    ratios = {}
    for kind, d in out.items():
        pairs = (("bound_axes", "bound_with_basis"), ("bound_axes", "bound_with_span_id"), ("bound_axes", "bound_with_row"),
                 ("unknown_axes", "unknown_axes_with_reason"), ("input_fields", "input_fields_with_basis"),
                 ("basis_entries", "basis_entries_valid"), ("output_fields", "output_fields_traceable_to_input_bases"),
                 ("output_fields", "output_fields_with_input_bases"))
        for den, num in pairs:
            if den in d and num in d:
                ratios.setdefault(kind, {})[f"{num}_over_{den}"] = round(d[num] / d[den], 6) if d[den] else None
    undeclared = {k[1]: v for k, v in sorted(t.items()) if k[0] == "undeclared"}
    return {"schema_version": VERSION, "counts": out, "ratios": ratios, "problems": dict(sorted(t.problems.items())),
            "undeclared_fields": undeclared}
