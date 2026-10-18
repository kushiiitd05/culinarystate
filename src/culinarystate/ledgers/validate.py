"""Validate a record: JSON Schema (structure) + rules (laws)."""
from __future__ import annotations

from functools import lru_cache

from jsonschema import Draft202012Validator, FormatChecker

from .registry import R
from .rules import check


class ValidationFailed(ValueError):
    def __init__(self, record_id: str, errors: list[str]):
        super().__init__(f"{record_id}: " + " | ".join(errors))
        self.errors = errors


@lru_cache(maxsize=None)
def _validator(prefix: str) -> Draft202012Validator:
    schema = R[prefix]
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def errors(record: dict) -> list[str]:
    prefix = record.get("record_type")
    if prefix not in R:
        return [f"unknown record_type {prefix!r}"]
    errs = [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in sorted(_validator(prefix).iter_errors(record), key=lambda e: list(e.absolute_path))]
    if errs:                       # rules assume structurally valid input
        return errs
    return check(record)


def validate(record: dict) -> dict:
    errs = errors(record)
    if errs:
        raise ValidationFailed(str(record.get("id")), errs)
    return record
