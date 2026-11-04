"""rc2 history-variable contract check (S154; DRAFT_PENDING_H4, opt-in).

Encodes the inherited rc1 rule (Card 16-A layer 4, SSOT L26288-26289): the five
history-dependent STATE variables are never filled from recipe text, and a
non-UNKNOWN value is allowed only on a MODEL or SIMULATED claim route.

The rc1/rc2 JSON Schemas check only the inline ``claim_route``. This module also
checks the sidecar ``field_metadata`` copy and the ``origin`` axis, so a value
whose origin says "source text" cannot pass by declaring a model route.

Externally measured history (origin EXTERNAL_VERIFIED) is NOT decided here: H4
has not ruled on it, so it is reported as pending rather than accepted or
called recipe text. Mismatched origin/route pairs are reported the same way.
Nothing is rewritten; the function returns issues only.
"""
from __future__ import annotations

from typing import Mapping

from culinarystate.annotation.schema_review import ReviewIssue

from .draft_contract import _pointer, validate_record

HISTORY_KEYS = ("cell_integrity", "enzyme_activity_state", "time_since_disruption",
                "thermal_dose", "oxygen_exposure")
HISTORY_POLICY_ID = "HISTORY_RC1_INHERITED_MODEL_SIMULATED_ONLY_PENDING_H4"

_ALLOWED_ROUTES = {"MODEL", "SIMULATED"}
_TEXT_ORIGINS = {"EXPLICIT_SOURCE", "INFERRED_LLM"}
_ROUTE_ORIGIN = {"MODEL": {"MODEL_ESTIMATED"}, "SIMULATED": {"SIMULATED"}}
_NUMERIC_KEYS = ("value", "low", "high", "qualitative", "censor")


def _populated(value) -> bool:
    if not isinstance(value, Mapping):
        return value is not None
    if value.get("status") not in (None, "UNKNOWN", "NOT_APPLICABLE"):
        return True
    return any(value.get(k) is not None for k in _NUMERIC_KEYS)


def _check_meta(meta: Mapping, path: str) -> list[ReviewIssue]:
    origin, route = meta.get("origin"), meta.get("claim_route")
    if route not in _ALLOWED_ROUTES or origin in _TEXT_ORIGINS:
        return [ReviewIssue("HISTORY_FROM_RECIPE_TEXT_FORBIDDEN", path,
                            "History variables are never filled from recipe text (MODEL/SIMULATED route only)")]
    if origin == "EXTERNAL_VERIFIED":
        return [ReviewIssue("HISTORY_EXTERNAL_POLICY_PENDING_H4", path,
                            "Externally measured history has no reviewed policy yet; not accepted")]
    if origin not in _ROUTE_ORIGIN[route]:
        return [ReviewIssue("HISTORY_ORIGIN_ROUTE_PENDING_H4", path,
                            f"Origin {origin!r} with route {route!r} has no reviewed policy; not accepted")]
    return []


def check_history(record: Mapping) -> list[ReviewIssue]:
    """Return history-policy issues for a STATE record; never modifies the record."""
    if not isinstance(record, Mapping) or record.get("record_type") != "STATE":
        raise ValueError("History contract applies to STATE records only")
    issues: list[ReviewIssue] = []
    variables = record.get("variables") or {}
    sidecar = record.get("field_metadata") or {}
    for key in HISTORY_KEYS:
        if key not in variables or not _populated(variables[key]):
            continue
        path = _pointer(("variables", key))
        value = variables[key]
        copies = [m for m in (value.get("meta") if isinstance(value, Mapping) else None, sidecar.get(path))
                  if isinstance(m, Mapping)]
        if not copies:
            issues.append(ReviewIssue("HISTORY_METADATA_MISSING", path,
                                      "A populated history variable needs explicit metadata"))
            continue
        seen = set()
        for meta in copies:
            for issue in _check_meta(meta, path):
                if issue.code not in seen:
                    seen.add(issue.code)
                    issues.append(issue)
    return issues


def validate_state_rc2(record: Mapping, schema: Mapping) -> list[ReviewIssue]:
    """rc2 structural/semantic validation plus the explicit history policy check."""
    issues = validate_record(record, schema)
    if isinstance(record, Mapping) and record.get("record_type") == "STATE":
        issues.extend(check_history(record))
    return issues
