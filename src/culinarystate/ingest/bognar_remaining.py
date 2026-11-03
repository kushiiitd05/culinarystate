"""Bognar (2002) Part 2: the 11 tables the v1 parser skipped -> 12-local STAGING cells (S157).

Status: PROVISIONAL_PENDING_G12_AUDIT. Staging only (no EVD, no ledger). Input is the
``pdftotext -layout`` text of the SNAP-pinned PDF, exactly as ``tools/ingest_bognar.py`` produces it.
The v1 parser (``ingest/bognar.py``, unchanged and reused for its vocabularies) skipped tables 2, 13,
16, 31, 32, 36, 39 (column-specific sub-variants a)/b)/c)), 35, 37, 38 (product sub-columns) and 29
(no A/B basis line) — ``reports/bognar_v1.md``. The card's 12.2 asks for a licence re-check before
ingestion, so every cell carries ``licence_gate = BOGNAR_LICENCE_RECHECK_PENDING``.

Column reading (conservative; nothing is resolved by meaning)
- The column count k comes from the A/B basis line, else from the most common number of value
  tokens among data rows. A data row with a different count is skipped and logged.
- Every header chunk (2+ spaces separate chunks in layout text) is attached to the nearest value
  column by character position; its raw text is kept per column (``column_header_raw``), split into
  method / sub-variant marks / product sub-column / basis.
- Method per column is accepted only when two readings agree: equal consecutive groups (k divisible
  by the number of method labels) and nearest-label position. Agreement ->
  EQUAL_GROUPS_AND_POSITION_AGREE; disagreement -> MAPPING_CONFLICT (method None); k not divisible ->
  POSITIONAL_ONLY_UNCONFIRMED; no method line -> UNMAPPED_NO_METHOD_LINE. What a)/b)/whole/polished
  mean is not interpreted: the raw marks and the table notes are kept for the human audit (G12-3).
- Values: "-" -> NOT_AVAILABLE (no value); "1.00" -> CENSORED_GT_CAP_CANDIDATE with value origin
  SOURCE_IMPUTATION_POSSIBLE (the v1 reading: the report caps at 1.00 and uses it as a default);
  others MEASURED as exact strings. Constituents in the preface "estimated" list are flagged.
"""
from __future__ import annotations

import hashlib
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from culinarystate.ingest.bognar import CANON, ESTIMATED, SKIP_TARGETS, TABLE, letters_of, methods_of
from culinarystate.ingest.bognar_build import FAMILY, PORTION

STATUS = "PROVISIONAL_PENDING_G12_AUDIT"
PARSER_VERSION = "bognar_remaining_staging@0.1-provisional"
REMAINING_TABLES = (2, 13, 16, 29, 31, 32, 35, 36, 37, 38, 39)
PART2 = "Part 2 : Average retention factors"
VALUE = re.compile(r"(?<!\S)(\d\.\d\d|-)(?!\S)")
CHUNK = re.compile(r"\S+(?: \S+)*")
MARK = re.compile(r"^(?:[a-z]\)|\*+|\d\))$")
NOTE = re.compile(r"^\s*(?:[a-z]\)|\*+|\d\))")
CONSTITUENTS = re.compile(r"(?i)^constituents*\b\s*")


class BognarParseError(ValueError):
    """The text is not the Part 2 layout this parser reads."""


@dataclass(frozen=True)
class BognarResult:
    cells: list[dict] = field(default_factory=list)
    tables: dict[int, dict] = field(default_factory=dict)
    tables_found: tuple[int, ...] = ()
    tables_missing: tuple[int, ...] = ()
    problems: tuple[str, ...] = ()
    input_sha256: str | None = None
    input_bytes: int | None = None


def _chunks(line: str) -> list[tuple[float, str]]:
    out = []
    for m in CHUNK.finditer(line):
        text, start = m.group(0), m.start()
        lead = CONSTITUENTS.match(text)
        if lead:
            text, start = text[lead.end():], start + lead.end()
        if text:
            out.append((start + len(text) / 2, text))
    return out


def _nearest(x: float, centers: list[float]) -> int:
    return min(range(len(centers)), key=lambda i: (abs(centers[i] - x), i))


def _segments(text: str) -> list[tuple[int, list[tuple[int, str]]]]:
    lines = [x.replace("\f", "") for x in text.split("\n")]
    start = next((i for i, t in enumerate(lines) if t.startswith(PART2)), None)
    if start is None:
        raise BognarParseError("no 'Part 2 : Average retention factors' line")
    out: list[tuple[int, list[tuple[int, str]]]] = []
    cur: list[tuple[int, str]] | None = None
    for i in range(start, len(lines)):
        m = TABLE.match(lines[i])
        if m:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if "retention" in m.group(2).lower() or "retention" in nxt.lower():
                cur = [(i + 1, lines[i])]
                out.append((int(m.group(1)), cur))
            else:
                cur = None
        elif re.match(r"^Part \d+\s*:", lines[i]) and i != start:
            cur = None
        elif cur is not None:
            cur.append((i + 1, lines[i]))
    return out


def _is_data(t: str) -> bool:
    s = t.strip()
    return bool(s) and s[0].isalpha() and VALUE.search(t) is not None


def _classify(header: list[tuple[int, str]]) -> dict[str, Any]:
    basis, marks, methods, product = None, None, [], []
    for _, t in header:
        s = t.strip()
        if not s or s.startswith("-"):
            continue
        if letters_of(t):
            basis = t
        elif all(MARK.match(x) for x in s.split()):
            marks = t
        elif methods_of(CONSTITUENTS.sub("", s)) and "such as" not in s and "retention" not in s.lower():
            methods.append(t)
        else:
            product.append(t)
    method_line = methods[-1] if methods else None
    return {"basis": basis, "marks": marks, "method": method_line, "product": methods[:-1] + product}


def _parse_table(no: int, seg: list[tuple[int, str]]) -> tuple[list[dict], dict, list[str]]:
    title = seg[0][1].strip()
    summary: dict[str, Any] = {"table": no, "title_raw": title, "cells": 0, "columns": 0, "method_mapping": None,
                               "basis_line": False, "skipped_non_retention_rows": 0, "skipped_ragged_rows": 0,
                               "notes_raw": (), "problem": None}
    first = next((k for k, (_, t) in enumerate(seg) if k > 0 and _is_data(t)), None)
    if first is None:
        summary["problem"] = "NO_DATA_ROWS"
        return [], summary, [f"table {no}: no data rows"]
    header = seg[1:first]
    rf = max((k for k, (_, t) in enumerate(header) if "retention factor" in t.lower()), default=None)
    header = header[rf + 1:] if rf is not None else header
    cls = _classify(header)
    letters = letters_of(cls["basis"]) if cls["basis"] else None
    data = [(ln, t, list(VALUE.finditer(t))) for ln, t in seg[first:] if _is_data(t)]
    notes = tuple(t.strip() for _, t in seg[first:] if NOTE.match(t) and not VALUE.search(t))
    k = len(letters) if letters else Counter(len(v) for _, _, v in data).most_common(1)[0][0]
    full = [(ln, t, v) for ln, t, v in data if len(v) == k]
    if not full:
        summary["problem"] = "NO_ROW_MATCHES_COLUMN_COUNT"
        return [], summary, [f"table {no}: no data row has {k} values"]
    centers = [statistics.median((v[c].start() + v[c].end()) / 2 for _, _, v in full) for c in range(k)]

    def per_column(line: str | None) -> list[str | None]:
        cols: list[list[str]] = [[] for _ in range(k)]
        for x, text in _chunks(line or ""):
            cols[_nearest(x, centers)].append(text)
        return [" ".join(c) if c else None for c in cols]

    labels = [(x, ms[0]) for x, text in _chunks(cls["method"] or "") if (ms := methods_of(text))]
    if not labels:
        method_of, mapping = [None] * k, "UNMAPPED_NO_METHOD_LINE"
    else:
        lab_x = [x for x, _ in labels]
        pos = [_nearest(c, lab_x) for c in centers]
        if k % len(labels) == 0:
            eq = [c // (k // len(labels)) for c in range(k)]
            mapping = "EQUAL_GROUPS_AND_POSITION_AGREE" if eq == pos else "MAPPING_CONFLICT"
            method_of = [labels[i][1] for i in eq] if eq == pos else [None] * k
        else:
            mapping, method_of = "POSITIONAL_ONLY_UNCONFIRMED", [labels[i][1] for i in pos]
    marks = per_column(cls["marks"])
    product_cols = [per_column(t) for t in cls["product"]]
    subcol = [" / ".join(p[c] for p in product_cols if p[c]) or None for c in range(k)]
    head_cols = [per_column(t) for t in (*cls["product"], cls["method"], cls["marks"], cls["basis"]) if t]
    header_raw = [" | ".join(h[c] for h in head_cols if h[c]) or None for c in range(k)]
    basis = list(letters) if letters else ["UNKNOWN"] * k
    cells, problems = [], []
    for ln, t, vals in data:
        if len(vals) != k:
            summary["skipped_ragged_rows"] += 1
            problems.append(f"table {no} line {ln}: {len(vals)} values vs {k} columns, row skipped")
            continue
        name = re.sub(r"\s*\d\)", "", t[:vals[0].start()].strip()).strip()
        name = CANON.get(name.lower(), name)
        if name.lower() in SKIP_TARGETS:
            summary["skipped_non_retention_rows"] += 1
            continue
        for c, m in enumerate(vals):
            v = m.group(1)
            cell: dict[str, Any] = {
                "record": "BOGNAR_STAGED_CELL", "status": STATUS, "parser_version": PARSER_VERSION,
                "staging_key": f"bognar:part2:T{no}:L{ln}:C{c}", "table": no, "source_line": ln, "column_index": c,
                "constituent_raw": name, "column_header_raw": header_raw[c], "method_raw": method_of[c],
                "method_mapping": mapping, "sub_variant_raw": marks[c], "sub_column_raw": subcol[c],
                "basis": basis[c], "portion": PORTION.get(basis[c], "UNKNOWN"), "value_raw": v,
                "estimated": any(e in name.lower() for e in ESTIMATED), "source_family_id": FAMILY,
                "plane": "12-E", "regime": "D-A", "aggregation_level": "COMPILED_MEAN", "time_series": "NONE",
                "temperature": {"status": "UNKNOWN"}, "duration": {"status": "UNKNOWN"},
                "independence_resolution": "SOURCE_FAMILY_ONLY", "licence_gate": "BOGNAR_LICENCE_RECHECK_PENDING"}
            if v == "-":
                cell.update(value_status="NOT_AVAILABLE", value_origin="UNKNOWN")
            elif v == "1.00":
                cell.update(value_status="CENSORED_GT_CAP_CANDIDATE", value=v,
                            value_origin="SOURCE_IMPUTATION_POSSIBLE")
            else:
                cell.update(value_status="MEASURED", value=v, value_origin="REPORTED")
            cells.append(cell)
    summary.update(cells=len(cells), columns=k, method_mapping=mapping, basis_line=letters is not None,
                   notes_raw=notes, methods_raw=tuple(m for _, m in labels))
    return cells, summary, problems


def parse_remaining(text: str, tables: tuple[int, ...] = REMAINING_TABLES) -> BognarResult:
    cells: list[dict] = []
    summaries: dict[int, dict] = {}
    problems: list[str] = []
    for no, seg in _segments(text):
        if no not in tables or no in summaries:
            continue
        c, s, p = _parse_table(no, seg)
        cells += c
        summaries[no] = s
        problems += p
    found = tuple(sorted(summaries))
    return BognarResult(cells=cells, tables=dict(sorted(summaries.items())), tables_found=found,
                        tables_missing=tuple(t for t in tables if t not in summaries), problems=tuple(problems))


def parse_remaining_file(path: Path | str, tables: tuple[int, ...] = REMAINING_TABLES) -> BognarResult:
    data = Path(path).read_bytes()
    res = parse_remaining(data.decode("utf-8"), tables)
    return BognarResult(cells=res.cells, tables=res.tables, tables_found=res.tables_found,
                        tables_missing=res.tables_missing, problems=res.problems,
                        input_sha256=hashlib.sha256(data).hexdigest(), input_bytes=len(data))
