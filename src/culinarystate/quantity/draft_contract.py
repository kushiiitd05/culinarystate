"""Proposed Step 16 rc2 contract, pure validation and explicit quantity arithmetic.

No parser, grounding, default portions, unit conversion, metadata backfill or
human verification. Callers explicitly select this draft and supply its schema.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from jsonschema import Draft202012Validator

from culinarystate.annotation.schema_review import ReviewIssue, review_record

ORIGINS = ("EXPLICIT_SOURCE", "EXTERNAL_VERIFIED", "DERIVED_DETERMINISTIC", "INFERRED_LLM",
           "MODEL_ESTIMATED", "IMPUTED", "SIMULATED", "UNKNOWN")
FIELD_STATUSES = ("KNOWN", "UNKNOWN", "NOT_APPLICABLE", "CONFLICTING", "CENSORED")
CLAIM_ROUTES = ("EXPLICIT", "INFERRED_RULE", "INFERRED_LLM", "MODEL", "SIMULATED")
QNT_FIELDS = frozenset(("raw", "parsed", "normalized", "mass_g", "volume_ml", "count", "qualifiers",
    "conversion_method", "conversion_path", "portion_id", "q_level", "locale", "ingredient_id",
    "normalized_mass_low_g", "normalized_mass_high_g", "intervals", "ast", "quantity_scope",
    "measured_state", "as_purchased_vs_edible", "multiplier", "dual_expression_check", "unit_variant",
    "locale_evidence", "unit_system_era"))
STATE_FIELDS = frozenset(("belief", "quantity", "location", "form", "existence", "container"))


class ContractError(ValueError):
    """A draft quantity cannot be safely interpreted as explicit arithmetic."""


def metadata_schema():
    return {"type": "object", "additionalProperties": False,
            "required": ["origin", "status", "claim_route"], "properties": {
                "origin": {"enum": list(ORIGINS)}, "status": {"enum": list(FIELD_STATUSES)},
                "claim_route": {"enum": list(CLAIM_ROUTES)},
                "evidence_refs": {"type": "array", "uniqueItems": True,
                                  "items": {"type": "string", "minLength": 1, "pattern": r"\S"}}}}


def ast_node_schema():
    """Recursive definition using local $defs.ast_node and $defs.field_meta."""
    variants = []
    kinds = ("RATIONAL", "RANGE", "ADD", "MULTIPLY", "FRACTION_OF", "REMAINDER_OF",
             "PACKAGE_CONTENT", "ALTERNATIVE", "QUALITATIVE", "OPEN_AMOUNT", "UNKNOWN")
    for kind in kinds:
        props = {"node_type": {"const": kind}, "meta": {"$ref": "#/$defs/field_meta"},
                 "raw": {"type": "string"}}
        required = ["node_type", "meta"]
        if kind in {"RATIONAL", "RANGE", "UNKNOWN"}:
            props["unit"] = {"type": "string", "minLength": 1, "pattern": r"\S"}
        if kind == "RATIONAL":
            props.update(numerator={"type": "integer", "minimum": 0},
                         denominator={"type": "integer", "minimum": 1})
            required += ["numerator", "denominator", "unit"]
        elif kind == "RANGE":
            props.update(low={"type": "number", "minimum": 0}, high={"type": "number", "minimum": 0})
            required += ["low", "high", "unit"]
        elif kind in {"QUALITATIVE", "OPEN_AMOUNT"}:
            props["raw"]["minLength"] = 1
            props["raw"]["pattern"] = r"\S"
            required += ["raw"]
        elif kind != "UNKNOWN":
            props["children"] = {"type": "array", "minItems": 2,
                                 "items": {"$ref": "#/$defs/ast_node"}}
            if kind in {"MULTIPLY", "FRACTION_OF", "PACKAGE_CONTENT"}:
                props["children"]["maxItems"] = 2
            required += ["children"]
        variant = {"type": "object", "additionalProperties": False, "required": required, "properties": props}
        if kind == "UNKNOWN":
            variant["allOf"] = [{"properties": {"meta": {"properties": {
                "status": {"enum": ["UNKNOWN", "NOT_APPLICABLE"]}}}}}]
        variants.append(variant)
    return {"oneOf": variants}


def ast_schema():
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {"ast_node": ast_node_schema(), "field_meta": metadata_schema()},
            "$ref": "#/$defs/ast_node"}


def make_record_schema(v1_schema: Mapping, kind: str):
    """Create a separate rc2 proposal without modifying a v1/frozen schema."""
    if kind not in {"QNT", "STATE"}:
        raise ValueError("Only QNT and STATE have rc2 proposals")
    if v1_schema.get("properties", {}).get("record_type", {}).get("const") != kind:
        raise ValueError("Source schema record type does not match requested rc2 kind")
    out = copy.deepcopy(v1_schema)
    out["$id"] = f"culinarystate/{kind}.draft_v2.schema.json"
    out["description"] = ("schema_version 1.0.0-rc2, DRAFT_PENDING_H4; optional selection of a new "
                          "contract with explicit semantic-field metadata and typed quantity AST; no automatic migration")
    out["properties"]["schema_version"] = {"const": "1.0.0-rc2"}
    out["required"] = list(dict.fromkeys([*out["required"], "schema_version", "field_metadata"]))
    out["properties"]["field_metadata"] = {
        "type": "object", "propertyNames": {"pattern": "^/"},
        "additionalProperties": {"$ref": "#/$defs/field_meta"},
        "description": "Exact JSON pointers to semantic claim targets; no inherited/backfilled metadata."}

    def replace_meta(value):
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if key == "meta" and isinstance(child, dict) and {"origin", "status", "claim_route"} <= set(child.get("properties", {})):
                    value[key] = {"$ref": "#/$defs/field_meta"}
                else:
                    replace_meta(child)
        elif isinstance(value, list):
            for child in value:
                replace_meta(child)

    replace_meta(out)
    out.setdefault("$defs", {})["field_meta"] = metadata_schema()
    if kind == "QNT":
        out["$defs"]["ast_node"] = ast_node_schema()
        out["properties"]["ast"] = {"$ref": "#/$defs/ast_node"}
    return out


def _pointer(parts):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def _structural_issues(value, schema):
    return [ReviewIssue("SCHEMA", _pointer(e.absolute_path),
                        f"Draft schema constraint {e.validator!r} failed")
            for e in Draft202012Validator(schema).iter_errors(value)]


def _has_claim(value):
    if value is None:
        return False
    if isinstance(value, dict):
        if value.get("node_type") == "UNKNOWN":
            return False
        if value.get("node_type") in {"RATIONAL", "RANGE", "QUALITATIVE", "OPEN_AMOUNT"}:
            return True
        if "node_type" in value:
            return False  # expression structure can be known while its outcome is unknown
        if value.get("status") in {"UNKNOWN", "NOT_APPLICABLE"}:
            return any(value.get(k) is not None for k in ("value", "low", "high", "qualitative", "censor"))
        if "value" in value and not any(value.get(k) is not None for k in ("value", "low", "high", "qualitative", "censor")):
            return False
    return True


def _metadata_issue(value, meta, path):
    if meta.get("status") in {"UNKNOWN", "NOT_APPLICABLE"} and _has_claim(value):
        return [ReviewIssue("UNKNOWN_WITH_CLAIM", path, "Unknown/not-applicable metadata cannot carry a known claim")]
    return []


def validate_ast(node):
    issues = _structural_issues(node, ast_schema())
    if issues:
        return issues

    def walk(n, path):
        issues.extend(_metadata_issue(n, n["meta"], path))
        if n["node_type"] == "RANGE":
            if any(isinstance(n[k], float) and not math.isfinite(n[k]) for k in ("low", "high")):
                issues.append(ReviewIssue("NONFINITE_NUMBER", path, "Range bounds must be finite"))
            elif n["low"] > n["high"]:
                issues.append(ReviewIssue("INVERTED_INTERVAL", path, "Range low must not exceed high"))
        for i, child in enumerate(n.get("children", [])):
            walk(child, path + f"/children/{i}")

    walk(node, "/ast")
    return issues


@dataclass(frozen=True)
class QuantityResult:
    status: str
    low: Fraction | None = None
    high: Fraction | None = None
    unit: str | None = None
    alternatives: tuple[QuantityResult, ...] = ()
    raw: str | None = None
    reason: str = ""
    origins: tuple[str, ...] = ()
    interval_kinds: tuple[str, ...] = ()

    def to_mapping(self):
        """JSON-safe arithmetic result; exact ratios remain ratios, not floats.

        This is not a QNT ledger record or an observed/human-verified value.
        """
        def ratio(value):
            return None if value is None else {"numerator": value.numerator, "denominator": value.denominator}
        return {"status": self.status, "low": ratio(self.low), "high": ratio(self.high),
                "unit": self.unit, "alternatives": [r.to_mapping() for r in self.alternatives],
                "raw": self.raw, "reason": self.reason, "origins": list(self.origins),
                "interval_kinds": list(self.interval_kinds)}


def evaluate_ast(node) -> QuantityResult:
    """Evaluate only declared arithmetic in identical units using exact rationals.

    Unit '1' means an explicit dimensionless factor. No conversion, density,
    portion selection or Q-level assignment is performed. Metadata is asserted
    by the caller; computation does not verify its provenance or human status.
    """
    issues = validate_ast(node)
    if issues:
        raise ContractError("; ".join(f"{i.code} at {i.path}" for i in issues))

    def run(n):
        kind, meta = n["node_type"], n["meta"]
        own = (meta["origin"],)
        if meta["status"] in {"CONFLICTING", "CENSORED", "NOT_APPLICABLE"}:
            def tags(child):
                origins = {child["meta"]["origin"]}
                bands = {"SOURCE_RANGE"} if child["node_type"] == "RANGE" else set()
                for item in child.get("children", []):
                    co, cb = tags(item)
                    origins.update(co)
                    bands.update(cb)
                return origins, bands
            origins, bands = tags(n)
            return QuantityResult("NOT_APPLICABLE" if meta["status"] == "NOT_APPLICABLE" else "UNKNOWN",
                                  unit=n.get("unit"), reason=meta["status"], origins=tuple(sorted(origins)),
                                  interval_kinds=tuple(sorted(bands)))
        if kind in {"QUALITATIVE", "OPEN_AMOUNT", "UNKNOWN"}:
            return QuantityResult(kind, unit=n.get("unit"), raw=n.get("raw"), origins=own)
        if kind == "RATIONAL":
            v = Fraction(int(n["numerator"]), int(n["denominator"]))
            return QuantityResult("KNOWN", v, v, n["unit"], raw=n.get("raw"), origins=own)
        if kind == "RANGE":
            lo, hi = Fraction(str(n["low"])), Fraction(str(n["high"]))
            return QuantityResult("RANGE", lo, hi, n["unit"], raw=n.get("raw"), origins=own,
                                  interval_kinds=("SOURCE_RANGE",))
        children = tuple(run(c) for c in n["children"])
        origins = tuple(sorted(set(own).union(*(set(c.origins) for c in children))))
        bands = tuple(sorted({k for c in children for k in c.interval_kinds}))
        if kind == "ALTERNATIVE":
            return QuantityResult("ALTERNATIVE", alternatives=children, raw=n.get("raw"), origins=origins)
        if any(c.status == "ALTERNATIVE" for c in children):
            raise ContractError("Unresolved ALTERNATIVE cannot enter arithmetic")
        if meta["status"] == "UNKNOWN" or any(c.status not in {"KNOWN", "RANGE"} for c in children):
            return QuantityResult("UNKNOWN", reason="UNAVAILABLE_OPERAND", origins=origins, interval_kinds=bands)
        if kind in {"ADD", "REMAINDER_OF"}:
            if len({c.unit for c in children}) != 1:
                raise ContractError("Arithmetic requires identical declared units; no implicit conversions")
            unit = children[0].unit
            if kind == "ADD":
                lo, hi = sum(c.low for c in children), sum(c.high for c in children)
            else:
                lo = children[0].low - sum(c.high for c in children[1:])
                hi = children[0].high - sum(c.low for c in children[1:])
                if hi < 0:
                    raise ContractError("Allocation exceeds the entire explicit quantity")
                if lo < 0:
                    return QuantityResult("UNKNOWN", unit=unit, reason="POSSIBLE_OVERALLOCATION",
                                          origins=origins, interval_kinds=bands)
        else:
            a, b = children
            if kind in {"FRACTION_OF", "PACKAGE_CONTENT"}:
                if a.unit != "1":
                    raise ContractError("Fraction/package count must be an explicit dimensionless factor")
                if kind == "FRACTION_OF" and a.high > 1:
                    raise ContractError("FRACTION_OF factor must be within [0,1]")
                unit = b.unit
            elif a.unit == "1":
                unit = b.unit
            elif b.unit == "1":
                unit = a.unit
            else:
                raise ContractError("MULTIPLY requires a dimensionless factor; densities are not inferred")
            lo, hi = a.low * b.low, a.high * b.high
        return QuantityResult("KNOWN" if lo == hi else "RANGE", lo, hi, unit,
                              origins=origins, interval_kinds=bands)

    return run(node)


def claim_targets(record: Mapping):
    """Exact JSON-pointer scope of semantic claim metadata, including unknowns."""
    targets = {}
    fields = QNT_FIELDS if record.get("record_type") == "QNT" else STATE_FIELDS
    for field in sorted(fields & record.keys()):
        value = record[field]
        if field == "intervals":
            targets.update({_pointer((field, i)): v for i, v in enumerate(value)})
        else:
            targets[_pointer((field,))] = value
    if record.get("record_type") == "STATE":
        targets.update({_pointer(("variables", key)): value for key, value in record.get("variables", {}).items()})
    return targets


def validate_record(record: Mapping, schema: Mapping, *, family_ids=None):
    """Opt-in rc2 structural + semantic validation; returns issues, never rewrites."""
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0-rc2":
        return [ReviewIssue("DRAFT_SCHEMA", "/schema_version", "Explicit rc2 schema selection is required")]
    issues = _structural_issues(record, schema)
    if issues:
        return issues
    if record.get("record_type") not in {"QNT", "STATE"}:
        return [ReviewIssue("RECORD_TYPE", "/record_type", "rc2 contract supports QNT and STATE only")]
    issues.extend(i for i in review_record(record, family_ids=family_ids, pointer_paths=True)
                  if i.code != "AST_CONTRACT_PENDING")
    targets, metadata = claim_targets(record), record["field_metadata"]
    for path in metadata.keys() - targets.keys():
        issues.append(ReviewIssue("METADATA_PATH", path, "Metadata does not address a declared semantic claim"))
    for path, value in targets.items():
        inline = value.get("meta") if isinstance(value, dict) else None
        mapped = metadata.get(path)
        if inline is not None and mapped is not None and inline != mapped:
            issues.append(ReviewIssue("METADATA_CONFLICT", path, "Inline and field metadata disagree"))
        meta = inline if inline is not None else mapped
        if meta is None:
            issues.append(ReviewIssue("MISSING_METADATA", path, "Every present semantic claim needs explicit metadata"))
        else:
            issues.extend(_metadata_issue(value, meta, path))
    if record.get("ast") is not None:
        ast_issues = validate_ast(record["ast"])
        issues.extend(ast_issues)
        if not ast_issues:
            try:
                evaluate_ast(record["ast"])
            except ContractError as exc:
                issues.append(ReviewIssue("AST_ARITHMETIC", "/ast", str(exc)))
    return issues
