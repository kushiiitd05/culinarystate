"""Pure draft review overlay, not a schema freeze or human verification.

Use after JSON Schema validation. Checks cross-field invariants and exposes
unresolved contract gaps; never fills missing values or rewrites records.
Metadata enforcement is opt-in so historical v0 validation is unchanged.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Collection, Mapping


@dataclass(frozen=True)
class ReviewIssue:
    code: str
    path: str
    message: str


def review_record(record: Mapping, *, family_ids: Collection[str] | None = None,
                  require_metadata: bool = False, pointer_paths: bool = False) -> list[ReviewIssue]:
    issues = []

    def add(code, path, message):
        issues.append(ReviewIssue(code, path, message))

    def numeric(v):
        return isinstance(v, int) and not isinstance(v, bool) or isinstance(v, float) and math.isfinite(v)

    def child_path(path, key):
        if pointer_paths:
            return path + "/" + str(key).replace("~", "~0").replace("/", "~1")
        return path + f"[{key}]" if isinstance(key, int) else path + "." + key

    def walk(value, path):
        if isinstance(value, float) and not math.isfinite(value):
            add("NONFINITE_NUMBER", path, "NaN/infinity is not a scientific value or UNKNOWN")
        if isinstance(value, list):
            for i, item in enumerate(value):
                walk(item, child_path(path, i))
        if not isinstance(value, dict):
            return
        for lo, hi in [("low", "high"), ("mass_low_g", "mass_high_g"),
                       ("normalized_mass_low_g", "normalized_mass_high_g")]:
            if numeric(value.get(lo)) and numeric(value.get(hi)) and value[lo] > value[hi]:
                add("INVERTED_INTERVAL", path, f"{lo} must not exceed {hi}")
        fam = value.get("process_family_id")
        if fam is not None:
            if not isinstance(fam, str) or not fam.startswith("FAM:"):
                add("PROCESS_FAMILY_NAMESPACE", child_path(path, "process_family_id"), "Family root must use draft FAM: namespace")
            elif family_ids is not None and fam not in family_ids:
                add("UNKNOWN_PROCESS_FAMILY", child_path(path, "process_family_id"), "Reference absent from supplied hierarchy roots")
        meta = value.get("meta")
        if require_metadata and value.get("status") in {"MEASURED", "RANGE", "QUALITATIVE", "CENSORED"}:
            if meta is None:
                add("MISSING_METADATA", path, "Draft evidence requires origin/status/claim_route metadata")
            elif not isinstance(meta, dict) or not all(meta.get(k) for k in ("origin", "status", "claim_route")):
                add("INCOMPLETE_METADATA", path, "All three metadata axes are required")
        if isinstance(meta, dict) and meta.get("status") in {"UNKNOWN", "NOT_APPLICABLE"}:
            if any(value.get(k) is not None for k in ("value", "low", "high", "qualitative", "censor")):
                add("UNKNOWN_WITH_CLAIM", path, "Unknown/not-applicable metadata cannot carry a numeric or qualitative claim")
        kind = value.get("node_type")
        if kind == "RANGE" and not all(numeric(value.get(k)) for k in ("low", "high")):
            add("AST_RANGE_BOUNDS", path, "Executable range requires finite low and high bounds")
        if kind in {"RATIONAL", "ADD", "MULTIPLY", "FRACTION_OF", "REMAINDER_OF", "PACKAGE_CONTENT", "ALTERNATIVE"}:
            add("AST_CONTRACT_PENDING", path, "Type-specific operands and execution semantics need an approved contract")
        for key, item in value.items():
            walk(item, child_path(path, key))

    walk(record, "" if pointer_paths else "$")
    return issues
