"""Shared JSON Schema building blocks for every ledger record.

Every record carries the same envelope (id, version, status, provenance,
verification) so that versioning, provenance and human-vs-AI verification are
uniform across ledgers. Scientific quantities use `qvalue`, which makes UNKNOWN
a first-class state that can never carry a number.
"""
from __future__ import annotations

SCHEMA_VERSION = "1.0.0"
ID_DIGITS = 6

HUMANS = frozenset({"Kush", "Parv"})

VERIFICATION_STATUS = [
    "UNVERIFIED",
    "AI_PRECHECKED",      # an LLM/agent looked at it — NOT human verification
    "HUMAN_VERIFIED",
    "HUMAN_REJECTED",
    "NEEDS_SOURCE",
    "CONFLICT",
]
RECORD_STATUS = ["ACTIVE", "DEPRECATED", "SUPERSEDED", "RETRACTED"]
PROVENANCE_METHOD = ["MANUAL", "IMPORT", "RULE", "LLM", "MODEL", "DERIVED", "SCRAPE"]
VALUE_STATUS = ["MEASURED", "RANGE", "QUALITATIVE", "CENSORED", "UNKNOWN", "NOT_APPLICABLE"]


def id_pattern(prefix: str) -> str:
    return rf"^{prefix}-\d{{{ID_DIGITS}}}$"


def ref(prefix: str) -> dict:
    return {"type": "string", "pattern": id_pattern(prefix)}


def ref_or_null(prefix: str) -> dict:
    return {"anyOf": [ref(prefix), {"type": "null"}]}


def refs(prefix: str, min_items: int = 0) -> dict:
    return {"type": "array", "items": ref(prefix), "minItems": min_items, "uniqueItems": True}


def enum(*values: str) -> dict:
    return {"type": "string", "enum": list(values)}


def nullable(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


STR = {"type": "string", "minLength": 1}
OPT_STR = nullable({"type": "string"})
NUM = {"type": "number"}
OPT_NUM = nullable(NUM)
INT0 = {"type": "integer", "minimum": 0}
BOOL = {"type": "boolean"}
DATETIME = {"type": "string", "format": "date-time"}
STR_LIST = {"type": "array", "items": {"type": "string"}}

# UNKNOWN-aware scalar. Numbers allowed only where the status says so.
QVALUE = {
    "type": "object",
    "required": ["status"],
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": VALUE_STATUS},
        "value": OPT_NUM,
        "low": OPT_NUM,
        "high": OPT_NUM,
        "unit": OPT_STR,
        "uncertainty": OPT_NUM,
        "qualitative": OPT_STR,
        "censor": nullable({
            "type": "object",
            "required": ["kind", "limit"],
            "additionalProperties": False,
            "properties": {"kind": enum("LT_LOD", "LT_LOQ", "GT_ULOQ", "GT_CAP", "ND", "GT_STATED", "LT_STATED"), "limit": OPT_NUM},
        }),
        "raw": OPT_STR,
    },
    "allOf": [
        {"if": {"properties": {"status": {"enum": ["UNKNOWN", "NOT_APPLICABLE", "QUALITATIVE"]}}},
         "then": {"properties": {"value": {"type": "null"}, "low": {"type": "null"}, "high": {"type": "null"}}}},
        {"if": {"properties": {"status": {"const": "MEASURED"}}},
         "then": {"required": ["value", "unit"], "properties": {"value": NUM}}},
        {"if": {"properties": {"status": {"const": "RANGE"}}},
         "then": {"required": ["low", "high", "unit"], "properties": {"low": NUM, "high": NUM}}},
        {"if": {"properties": {"status": {"const": "QUALITATIVE"}}},
         "then": {"required": ["qualitative"], "properties": {"qualitative": STR}}},
        {"if": {"properties": {"status": {"const": "CENSORED"}}},
         "then": {"required": ["censor"], "properties": {"censor": {"type": "object"}}}},
    ],
}

PROVENANCE = {
    "type": "object",
    "required": ["method", "source_ids"],
    "additionalProperties": False,
    "properties": {
        "method": {"type": "string", "enum": PROVENANCE_METHOD},
        "source_ids": refs("SRC"),
        "snapshot_ids": refs("SNAP"),
        "agent": OPT_STR,            # e.g. "claude-opus-5-5", "rule:quantity_grammar@0.1"
        "locator": OPT_STR,          # page / table / figure / span / json path
        "notes": OPT_STR,
    },
}

VERIFICATION = {
    "type": "object",
    "required": ["status"],
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": VERIFICATION_STATUS},
        "verifier": OPT_STR,
        "verified_at": nullable(DATETIME),
        "ai_reviewer": OPT_STR,
        "notes": OPT_STR,
    },
}


def envelope(prefix: str) -> dict:
    """Properties every record has."""
    return {
        "id": {"type": "string", "pattern": id_pattern(prefix)},
        "record_type": {"const": prefix},
        "schema_version": {"type": "string"},
        "version": {"type": "integer", "minimum": 1},
        "status": {"type": "string", "enum": RECORD_STATUS},
        "superseded_by": ref_or_null(prefix),
        "created_at": DATETIME,
        "created_by": STR,
        "provenance": PROVENANCE,
        "verification": VERIFICATION,
        "external_refs": STR_LIST,   # SSOT IDs (RQ16-04, G16-QTY), FoodOn/FDC IDs, DOIs …
        "notes": OPT_STR,
    }


ENVELOPE_REQUIRED = ["id", "record_type", "version", "status", "created_at", "created_by",
                     "provenance", "verification"]
