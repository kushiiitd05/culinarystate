"""Explicit, opt-in rc2 CQPO grounding pipeline (S154; DRAFT_PENDING_H4).

Wires ``parse_adapter.parse_quantity_v2`` (which itself uses the versioned
``versioned_normalizer.normalize_v2``) into one rc2 QNT record candidate, in the
Plan Step 17d order:

1. grammar parse -> rc2 AST + exact arithmetic (adapter);
2. unit resolution: the caller supplies the locale (with metadata) or the
   culinary-volume unit stays AMBIGUOUS; regional vessels have no volume;
3. deterministic same-dimension conversion (Q0) with exact rationals: mass
   units, source-stated package content and parenthetical source-stated mass;
4. POR selection by hard filters over caller-supplied records (HUMAN_VERIFIED
   and ACTIVE only; ingredient/unit/state/form/packing/locale equality). Zero
   matches -> NO_COMPATIBLE_RECORD; several -> AMBIGUOUS_POR_RECORDS (no tie
   break). A POR Q-level is used only from a caller-supplied basis->Q map; the
   CONVENTION basis has an open ruling and is never mapped by default;
5. interval + Q-level + conversion record, or UNKNOWN; then rc2 validation and
   an invented-value audit (every gram must trace to Q0 or a selected POR).

The legacy grammar/normaliser and the frozen recipe base are not touched; this
module runs only when called with an rc2 schema. It reads no files and writes
nothing. Placeholder id ``QNT-000000`` is used when no envelope is supplied: it
is never minted, written or reused as a ledger id.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Iterable, Mapping

from culinarystate.annotation.schema_review import ReviewIssue

from .draft_contract import ContractError, evaluate_ast, validate_record
from .parse_adapter import parse_quantity_v2
from .units import BY_KEY, SOURCES

PIPELINE_VERSION = "CQPO_RC2_GROUNDING_V1_DRAFT"
PLACEHOLDER_ID = "QNT-000000"
_DERIVED = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE"}
_DERIVED_UNKNOWN = {**_DERIVED, "status": "UNKNOWN"}
_UNK = {"status": "UNKNOWN"}
_POR_FACETS = ("state", "form", "packing", "locale")
_POR_Q_LEVELS = {"Q1", "Q2", "Q3", "Q4"}


@dataclass(frozen=True)
class GroundingContext:
    """Everything the caller asserts. Nothing here is inferred by the pipeline."""
    source_metadata: Mapping
    locale: str | None = None
    locale_metadata: Mapping | None = None
    locale_evidence: str | None = None
    ingredient_id: str | None = None
    ingredient_metadata: Mapping | None = None
    facets: Mapping = field(default_factory=dict)
    por_records: tuple = ()
    unit_ids: Mapping = field(default_factory=dict)
    por_q_levels: Mapping = field(default_factory=dict)
    quantity_scope: str = "INGREDIENT_LINE"
    envelope: Mapping | None = None


@dataclass(frozen=True)
class GroundingResult:
    record: dict
    unit_resolution: str
    mass_route: str
    ast_root: str
    arithmetic_status: str
    flags: tuple[str, ...]
    issues: tuple[ReviewIssue, ...]
    exact_mass: tuple[Fraction, Fraction] | None
    compatibility_mass_status: str
    pipeline_version: str = PIPELINE_VERSION


def _num(value: Fraction):
    return value.numerator if value.denominator == 1 else float(value)


def _channel(lo: Fraction, hi: Fraction, unit: str):
    if lo == hi:
        return {"status": "MEASURED", "value": _num(lo), "unit": unit}
    return {"status": "RANGE", "low": _num(lo), "high": _num(hi), "unit": unit}


def _exactly_representable(value: Fraction) -> bool:
    return value.denominator == 1 or Fraction(float(value)) == value


def _default_envelope():
    return {"id": PLACEHOLDER_ID, "version": 1, "status": "ACTIVE", "created_at": "1970-01-01T00:00:00Z",
            "created_by": PIPELINE_VERSION, "provenance": {"method": "RULE", "source_ids": [],
                                                           "notes": "dry-run candidate; never written or minted"},
            "verification": {"status": "UNVERIFIED"}}


def _por_grams(rec: Mapping):
    g = rec.get("grams_per_unit") or {}
    if g.get("status") == "MEASURED" and g.get("value") is not None:
        v = Fraction(str(g["value"]))
        return v, v
    if g.get("status") == "RANGE" and g.get("low") is not None and g.get("high") is not None:
        return Fraction(str(g["low"])), Fraction(str(g["high"]))
    return None


def _por_eligible(rec: Mapping) -> bool:
    return (isinstance(rec, Mapping) and rec.get("status") == "ACTIVE"
            and (rec.get("verification") or {}).get("status") == "HUMAN_VERIFIED"
            and _por_grams(rec) is not None)


def _select_por(unit_key: str, context: GroundingContext):
    """Hard-filter selection. Returns (route, record_or_None)."""
    if not context.ingredient_id:
        return "NO_INGREDIENT_LINK", None
    unit_id = context.unit_ids.get(unit_key)
    if not unit_id:
        return "UNIT_ID_UNMAPPED", None
    compatible = [r for r in context.por_records if _por_eligible(r)
                  and r.get("ingredient_id") == context.ingredient_id and r.get("from_unit_id") == unit_id
                  and all(r.get(f) == context.facets.get(f) for f in _POR_FACETS)]
    if not compatible:
        return "NO_COMPATIBLE_RECORD", None
    if len(compatible) > 1:
        return "AMBIGUOUS_POR_RECORDS", None
    if context.por_q_levels.get(compatible[0].get("basis")) not in _POR_Q_LEVELS:
        return "POR_Q_LEVEL_RULING_PENDING", None
    return "POR_SELECTED", compatible[0]


def _trace_mass(record: Mapping, por_records: Iterable[Mapping]):
    """Recompute exact mass bounds from the record's own trace, or return an issue code."""
    traces = [p for p in record.get("conversion_path") or [] if isinstance(p, str) and p.startswith("TRACE:")]
    if len(traces) != 1:
        return "MASS_WITHOUT_TRACE", None
    parts = traces[0].split(":")
    kind = parts[1]
    try:
        result = evaluate_ast(record["ast"]) if record.get("ast") else None
    except ContractError:
        return "MASS_WITHOUT_TRACE", None
    if kind in {"AST_EXACT_PHYSICAL", "AST_PACKAGE_SOURCE_STATED"}:
        unit = BY_KEY.get(result.unit) if result else None
        if not unit or unit.dimension != "MASS" or result.status not in {"KNOWN", "RANGE"}:
            return "MASS_WITHOUT_TRACE", None
        f = Fraction(str(unit.si))
        return None, (result.low * f, result.high * f, "Q0")
    if kind == "PARENTHETICAL_SOURCE_STATED" and len(parts) == 4:
        unit = BY_KEY.get(parts[3])
        if not unit or unit.dimension != "MASS":
            return "MASS_WITHOUT_TRACE", None
        v = Fraction(parts[2]) * Fraction(str(unit.si))
        return None, (v, v, "Q0")
    if kind == "POR_SELECTED" and len(parts) == 3:
        matches = [r for r in por_records if isinstance(r, Mapping) and r.get("id") == parts[2] and _por_eligible(r)]
        if len(matches) != 1 or result is None or result.status not in {"KNOWN", "RANGE"}:
            return "MASS_WITHOUT_TRACE", None
        if record.get("portion_id") != parts[2]:
            return "MASS_TRACE_MISMATCH", None
        g_lo, g_hi = _por_grams(matches[0])
        return None, (result.low * g_lo, result.high * g_hi, "POR")
    return "MASS_WITHOUT_TRACE", None


def audit_invented_values(record: Mapping, *, por_records: Iterable[Mapping] = ()) -> list[ReviewIssue]:
    """Invented grams = 0: every gram value must be reproducible from the record's trace."""
    por_records = list(por_records)
    issues = []
    mass = record.get("mass_g") or {}
    values = [mass.get(k) for k in ("value", "low", "high") if mass.get(k) is not None]
    bounds = [record.get("normalized_mass_low_g"), record.get("normalized_mass_high_g")]
    grams_intervals = [iv for iv in record.get("intervals") or [] if iv.get("unit") == "g"]
    if not values and all(b is None for b in bounds) and not grams_intervals:
        return issues
    code, expected = _trace_mass(record, por_records)
    if code:
        return [ReviewIssue(code, "/mass_g", "Gram value does not trace to Q0 arithmetic or a selected POR")]
    lo, hi, level = expected
    if mass.get("status") == "MEASURED":
        observed = (mass.get("value"), mass.get("value"))
    else:
        observed = (mass.get("low"), mass.get("high"))
    if observed != (_num(lo), _num(hi)):
        issues.append(ReviewIssue("MASS_TRACE_MISMATCH", "/mass_g", "Gram value differs from its recomputed trace"))
    if tuple(bounds) != (mass.get("value", mass.get("low")), mass.get("value", mass.get("high"))):
        issues.append(ReviewIssue("NORMALIZED_BOUNDS_MISMATCH", "/normalized_mass_low_g",
                                  "Normalized mass bounds must equal the mass channel bounds"))
    if (level == "Q0") != (record.get("q_level") == "Q0"):
        issues.append(ReviewIssue("MASS_TRACE_MISMATCH", "/q_level", "Q-level does not match the mass trace"))
    return issues


def ground_quantity_rc2(raw: str, context: GroundingContext, *, schema: Mapping) -> GroundingResult:
    """Ground one quantity expression into an rc2 QNT candidate. Never writes anything."""
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0-rc2":
        raise ContractError("Explicit rc2 QNT schema selection is required")
    if not isinstance(raw, str) or not raw.strip():
        raise ContractError("A nonblank raw quantity expression is required")
    if context.locale and not context.locale_metadata:
        raise ContractError("A supplied locale needs explicit locale metadata")
    if context.ingredient_id and not context.ingredient_metadata:
        raise ContractError("A supplied ingredient link needs explicit metadata")
    parsed = parse_quantity_v2(raw, source_metadata=context.source_metadata, locale=context.locale)
    p, a, norm = parsed.parsed, parsed.arithmetic, parsed.normalized
    flags = list(parsed.flags)
    known = a.status in {"KNOWN", "RANGE"}
    unit = BY_KEY.get(a.unit) if a.unit else None
    mass = volume = count = None
    path: list[str] = []
    intervals: list[dict] = []
    method, q_level, mass_route, portion = "NONE", "Q6", None, None
    exact_mass = None
    dual = None

    # Stage 2: unit resolution
    if not known:
        resolution = "NONE"
    elif a.unit == "item":
        resolution = "COUNT"
    elif unit is None:
        resolution = "UNKNOWN_UNIT"
    elif unit.dimension == "MASS":
        resolution = "MASS_PHYSICAL"
    elif unit.dimension == "VOLUME" and unit.si:
        resolution = "VOLUME_PHYSICAL"
    elif unit.dimension == "VOLUME" and unit.conventions:
        resolution = "VOLUME_LOCALE_CONVENTION" if context.locale in unit.conventions else "VOLUME_LOCALE_AMBIGUOUS"
    elif unit.unit_type == "REGIONAL":
        resolution = "REGIONAL_NO_STANDARD"
    elif unit.dimension == "COUNT":
        resolution = "PACKAGE" if unit.unit_type == "PACKAGE" else "COUNT"
    else:
        resolution = "UNKNOWN_UNIT"

    # Stage 3: deterministic conversion with exact rationals
    if resolution == "MASS_PHYSICAL":
        f = Fraction(str(unit.si))
        exact_mass = (a.low * f, a.high * f)
        package = parsed.ast["node_type"] == "PACKAGE_CONTENT"
        method = "SOURCE_STATED" if package else "EXACT_PHYSICAL"
        mass_route = "AST_PACKAGE_SOURCE_STATED" if package else "AST_EXACT_PHYSICAL"
        path.append(f"TRACE:{mass_route}")
        path.append(f"{a.unit}->g x{unit.si} [{unit.si_source}]")
        if package:
            n = parsed.ast["children"][0]
            n = Fraction(n["numerator"], n["denominator"])
            count = _channel(n, n, "package")
    elif resolution == "VOLUME_PHYSICAL":
        f = Fraction(str(unit.si))
        volume = _channel(a.low * f, a.high * f, "mL")
        method = "EXACT_PHYSICAL"
        path.append(f"{a.unit}->mL x{unit.si} [{unit.si_source}]")
    elif resolution == "VOLUME_LOCALE_CONVENTION":
        ml, src = unit.conventions[context.locale]
        f = Fraction(str(ml))
        volume = _channel(a.low * f, a.high * f, "mL")
        method = "LOCALE_CONVENTION"
        path.append(f"{a.unit}@{context.locale}={ml}mL [{src}:{SOURCES[src][2]}]")
        if SOURCES[src][2] == "NEEDS_SOURCE":
            flags.append("CONVENTION_NEEDS_SOURCE")
    elif resolution == "VOLUME_LOCALE_AMBIGUOUS":
        flags.append("LOCALE_AMBIGUOUS")
    elif resolution in {"COUNT", "PACKAGE", "REGIONAL_NO_STANDARD"}:
        count = _channel(a.low, a.high, a.unit)
        if resolution == "REGIONAL_NO_STANDARD":
            flags.append("REGIONAL_VESSEL_NO_STANDARD_VOLUME")
    if volume and volume["status"] == "RANGE":
        intervals.append({"kind": "SOURCE_RANGE", "low": volume["low"], "high": volume["high"], "unit": "mL"})

    if p.stated:
        sv, su, _ = p.stated
        s_unit = BY_KEY.get(su)
        dual = {"conflict": None, "notes": "parenthetical expression kept separate"}
        if known and s_unit and s_unit.dimension == "MASS":
            stated = Fraction(str(sv)) * Fraction(str(s_unit.si))
            if exact_mass is not None:
                dual["conflict"] = exact_mass != (stated, stated)
            else:
                exact_mass = (stated, stated)
                method, mass_route = "SOURCE_STATED", "PARENTHETICAL_SOURCE_STATED"
                path.append(f"TRACE:PARENTHETICAL_SOURCE_STATED:{Fraction(str(sv))}:{su}")

    # Stage 4: POR selection only when no Q0 mass exists
    if exact_mass is None:
        if known and resolution in {"COUNT", "PACKAGE", "VOLUME_PHYSICAL", "VOLUME_LOCALE_CONVENTION",
                                    "REGIONAL_NO_STANDARD", "VOLUME_LOCALE_AMBIGUOUS"}:
            mass_route, portion = _select_por(a.unit, context)
            if portion is not None:
                g_lo, g_hi = _por_grams(portion)
                exact_mass = (a.low * g_lo, a.high * g_hi)
                method, q_level = "PORTION_RECORD", context.por_q_levels[portion["basis"]]
                path.append(f"TRACE:POR_SELECTED:{portion['id']}")
                if g_lo != g_hi:
                    intervals.append({"kind": "CONVERSION_UNCERTAINTY", "low": _num(a.low * g_lo),
                                      "high": _num(a.high * g_hi), "unit": "g"})
        elif a.status in {"QUALITATIVE", "ALTERNATIVE"}:
            mass_route = a.status
        elif parsed.ast["node_type"] == "UNKNOWN":
            unstated = "UNSUPPORTED_OR_UNSTATED_QUANTITY" in flags and p.kind == "NONE" and not p.unit_key
            mass_route = "NO_QUANTITY" if unstated else "UNSUPPORTED_EXPRESSION"
        else:
            mass_route = "OPEN_OR_UNAVAILABLE_OPERAND"
    else:
        q_level = q_level if mass_route == "POR_SELECTED" else "Q0"

    if exact_mass is not None:
        mass = _channel(exact_mass[0], exact_mass[1], "g")
        if not all(_exactly_representable(v) for v in exact_mass):
            flags.append("MASS_FLOAT_REPRESENTATION")
        if mass["status"] == "RANGE" and mass_route != "POR_SELECTED":
            intervals.append({"kind": "SOURCE_RANGE", "low": mass["low"], "high": mass["high"], "unit": "g"})

    compat = norm.mass_g.get("status", "UNKNOWN")
    if mass is None and compat in {"MEASURED", "RANGE"}:
        flags.append("COMPATIBILITY_CHANNEL_MASKED")
    elif mass is not None and compat in {"MEASURED", "RANGE"} and mass_route != "POR_SELECTED":
        legacy = (norm.mass_g.get("value", norm.mass_g.get("low")), norm.mass_g.get("value", norm.mass_g.get("high")))
        if any(abs(float(e) - float(v)) > 1e-6 * max(1.0, abs(float(e))) for e, v in zip(exact_mass, legacy)):
            flags.append("COMPATIBILITY_CHANNEL_DISAGREES")

    if a.status == "QUALITATIVE":
        normalized = {"status": "QUALITATIVE", "qualitative": parsed.ast.get("raw") or raw}
    elif known:
        normalized = _channel(a.low, a.high, a.unit)
    else:
        normalized = dict(_UNK)

    record = {**copy.deepcopy(dict(context.envelope or _default_envelope())),
              "record_type": "QNT", "schema_version": "1.0.0-rc2", "raw": raw,
              "parsed": {"kind": p.kind, "value": p.value, "low": p.low, "high": p.high,
                         "multiplier": p.multiplier, "unit_raw": p.unit_raw, "size": p.size,
                         "qualifier": ",".join(p.qualifiers) or None},
              "normalized": normalized, "mass_g": mass or dict(_UNK), "volume_ml": volume or dict(_UNK),
              "count": count or dict(_UNK), "qualifiers": list(p.qualifiers), "conversion_method": method,
              "conversion_path": path, "q_level": q_level,
              "normalized_mass_low_g": mass.get("value", mass.get("low")) if mass else None,
              "normalized_mass_high_g": mass.get("value", mass.get("high")) if mass else None,
              "intervals": intervals, "ast": copy.deepcopy(parsed.ast), "quantity_scope": context.quantity_scope}
    if p.kind == "MULTIPLIER" and p.multiplier is not None:
        record["multiplier"] = p.multiplier
    if p.package_size:
        record["parsed"]["package_size"] = {"status": "MEASURED", "value": p.package_size[0], "unit": p.package_size[1]}
    if dual is not None:
        record["dual_expression_check"] = dual
    if portion is not None:
        record["portion_id"] = portion["id"]
    if context.locale:
        record["locale"] = context.locale
        if context.locale_evidence:
            record["locale_evidence"] = context.locale_evidence
    if context.ingredient_id:
        record["ingredient_id"] = context.ingredient_id

    fm = {"/raw": copy.deepcopy(dict(context.source_metadata))}
    for key in ("parsed", "normalized", "mass_g", "volume_ml", "count", "qualifiers", "conversion_method",
                "conversion_path", "q_level", "normalized_mass_low_g", "normalized_mass_high_g",
                "quantity_scope", "multiplier", "dual_expression_check", "portion_id"):
        if key not in record:
            continue
        value = record[key]
        unknown = value is None or isinstance(value, dict) and value.get("status") == "UNKNOWN"
        fm["/" + key] = dict(_DERIVED_UNKNOWN if unknown else _DERIVED)
    if portion is not None:
        for key in ("mass_g", "portion_id"):
            fm["/" + key]["evidence_refs"] = [portion["id"]]
    for i in range(len(intervals)):
        fm[f"/intervals/{i}"] = dict(_DERIVED)
    for key, meta in (("locale", context.locale_metadata), ("locale_evidence", context.locale_metadata),
                      ("ingredient_id", context.ingredient_metadata)):
        if key in record:
            fm["/" + key] = copy.deepcopy(dict(meta))
    record["field_metadata"] = fm

    issues = list(validate_record(record, schema))
    issues.extend(audit_invented_values(record, por_records=context.por_records))
    return GroundingResult(record, resolution, mass_route or "NONE", parsed.ast["node_type"], a.status,
                           tuple(dict.fromkeys(flags)), tuple(issues), exact_mass, compat)
