"""USDA Table of Cooking Yields for Meat and Poultry, Release 2 (DS-006) -> 12-local STAGING rows (S157).

Status: PROVISIONAL_PENDING_G12_AUDIT. Staging only: nothing here writes EVD or any ledger. Rows go
to a git-ignored staging area chosen by ``culinarystate.evidence.step12_local``; the committed
report holds counts and hashes only.

Format (as read by ``tools/infoods_transition_candidates.py``): one CSV header line with columns such
as ``NDB``, ``Yield Description``, ``Preparation Method1``, ``Cooking Yield %``, ``n``, ``SD``,
``Moisture Gain/ Loss %``, ``Fat   Gain/ Loss %``, ``Release Year2`` (trailing digits are footnote
marks). Header names are matched after normalisation (case, spaces, footnote digits); unknown
columns are kept raw and listed as unmapped. Card 12.1 typing: plane 12-E, regime D-A,
``aggregation_level = COMPILED_MEAN``, n / SD / min / max / moisture and fat change kept, T and t
UNKNOWN, ``time_series = NONE``, ``independence_resolution = SOURCE_FAMILY_ONLY``.

Laws: every raw cell is preserved verbatim; normalised values are a new column (exact decimal
strings, never floats); a blank cell is NOT_REPORTED (never 0); an unparseable cell is UNPARSED with
its raw text; a ragged row is skipped and logged, never padded. ``censor_kind`` stays NOT_ASSESSED:
the "nearest 5%" rounding rule needs the data dictionary read by a human (card 12.1).
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

STATUS = "PROVISIONAL_PENDING_G12_AUDIT"
PARSER_VERSION = "usda_yields_r2_staging@0.1-provisional"
ROLE_NAMES: dict[str, tuple[str, ...]] = {
    "ndb": ("ndb", "ndb no", "ndb number"),
    "description": ("yield description",),
    "preparation_method": ("preparation method",),
    "cooking_yield_pct": ("cooking yield %",),
    "n": ("n",),
    "sd": ("sd",),
    "min": ("min", "minimum"),
    "max": ("max", "maximum"),
    "moisture_change_pct": ("moisture gain/loss %",),
    "fat_change_pct": ("fat gain/loss %",),
    "release_year": ("release year",),
}
REQUIRED = ("ndb", "description", "preparation_method", "cooking_yield_pct")
TEXT_ROLES = ("ndb", "description", "preparation_method")
NUMERIC_ROLES = tuple(r for r in ROLE_NAMES if r not in TEXT_ROLES)


class R2ParseError(ValueError):
    """The file does not have the structure this parser reads (nothing is guessed)."""


@dataclass(frozen=True)
class R2Result:
    rows: list[dict] = field(default_factory=list)
    header_raw: tuple[str, ...] = ()
    column_roles: dict[str, str | None] = field(default_factory=dict)
    unmapped_columns: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()
    encoding: str | None = None
    input_sha256: str | None = None
    input_bytes: int | None = None


def normalise_header(h: str) -> str:
    s = " ".join(h.strip().lower().split())
    s = re.sub(r"\s*/\s*", "/", s)
    return re.sub(r"(?<=[a-z])\d+$", "", s)


def _roles(header: list[str]) -> dict[str, str | None]:
    lookup = {n: role for role, names in ROLE_NAMES.items() for n in names}
    seen_norm: set[str] = set()
    out: dict[str, str | None] = {}
    for h in header:
        norm = normalise_header(h)
        if norm in seen_norm:
            raise R2ParseError(f"duplicate header after normalisation: {norm!r}")
        seen_norm.add(norm)
        out[h] = lookup.get(norm)
    missing = [r for r in REQUIRED if r not in out.values()]
    if missing:
        raise R2ParseError(f"required columns missing: {missing}")
    return out


def _numeric(raw: str) -> dict[str, Any]:
    s = raw.strip()
    if not s:
        return {"status": "NOT_REPORTED", "raw": raw}
    try:
        d = Decimal(s)
    except InvalidOperation:
        return {"status": "UNPARSED", "raw": raw}
    if not d.is_finite():
        return {"status": "UNPARSED", "raw": raw}
    return {"status": "MEASURED", "value": format(d, "f"), "raw": raw}


def parse_r2_text(text: str) -> R2Result:
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration as e:
        raise R2ParseError("empty file") from e
    roles = _roles(header)
    by_role = {r: h for h, r in roles.items() if r}
    rows: list[dict] = []
    problems: list[str] = []
    for cells in reader:
        line = reader.line_num
        if not any(c.strip() for c in cells):
            continue
        if len(cells) != len(header):
            problems.append(f"line {line}: {len(cells)} cells vs {len(header)} header columns, row skipped")
            continue
        raw = dict(zip(header, cells))
        norm: dict[str, dict[str, Any]] = {}
        flags: list[str] = []
        for role in ROLE_NAMES:
            h = by_role.get(role)
            if h is None:
                norm[role] = {"status": "NOT_PRESENT_IN_FILE"}
            elif role in TEXT_ROLES:
                v = raw[h]
                norm[role] = {"status": "PRESENT", "raw": v} if v.strip() else {"status": "NOT_REPORTED", "raw": v}
            else:
                norm[role] = _numeric(raw[h])
            if norm[role]["status"] == "UNPARSED":
                flags.append(f"UNPARSED:{role}")
            if role in REQUIRED and norm[role]["status"] == "NOT_REPORTED":
                flags.append(f"REQUIRED_BLANK:{role}")
        ry = norm["release_year"]
        rows.append({
            "record": "R2_STAGED_ROW", "status": STATUS, "parser_version": PARSER_VERSION,
            "staging_row_id": f"usda_yields_r2:line{line}", "source_line": line, "raw": raw, "normalised": norm,
            "flags": flags, "plane": "12-E", "regime": "D-A", "aggregation_level": "COMPILED_MEAN",
            "dispersion_type": "SD" if norm["sd"]["status"] == "MEASURED" else "NOT_REPORTED",
            "value_origin": "REPORTED", "imputation": "UNKNOWN", "censor_kind": "NOT_ASSESSED",
            "temperature": {"status": "UNKNOWN"}, "duration": {"status": "UNKNOWN"}, "time_series": "NONE",
            "independence_resolution": "SOURCE_FAMILY_ONLY", "source_family_id": None,
            "release_year_flag": "RELEASE_YEAR_1975" if ry.get("status") == "MEASURED" and Decimal(ry["value"]) == 1975
            else None,
        })
    return R2Result(rows=rows, header_raw=tuple(header), column_roles=roles,
                    unmapped_columns=tuple(h for h, r in roles.items() if r is None), problems=tuple(problems))


def parse_r2_file(path: Path | str) -> R2Result:
    data = Path(path).read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        enc, text = "utf-8-sig", data.decode("utf-8-sig")
    else:
        try:
            enc, text = "utf-8", data.decode("utf-8")
        except UnicodeDecodeError:
            enc, text = "cp1252", data.decode("cp1252")
    res = parse_r2_text(text)
    return R2Result(rows=res.rows, header_raw=res.header_raw, column_roles=res.column_roles,
                    unmapped_columns=res.unmapped_columns, problems=res.problems, encoding=enc,
                    input_sha256=hashlib.sha256(data).hexdigest(), input_bytes=len(data))
