"""Step 12-local staging writer, diff against existing EVD and counts-only report (S157).

Status: PROVISIONAL_PENDING_G12_AUDIT. Nothing here writes EVD or any ledger, and nothing is merged.

- Staging (``write_staging``): the parsed R2 rows and Bognar cells carry raw third-party text, so
  they may only be written inside the repository's git-ignored ``data/interim/`` (default
  ``data/interim/step12_local_staging_v1``) or outside the repository. Existing files are never
  overwritten.
- Diff (``diff_against_evd``): read-only counts of how the staged rows relate to the latest ACTIVE
  EVD versions: Bognar rows already in EVD for the remaining tables, exact-key overlap,
  constituent+method pairs already seen, constituents shared with USDA R6 (G08-9 context: the
  USDA / Bognar overlap question stays with the human expert reading), yield rows by family,
  Phenol-Explorer yields citing a USDA yield source and R2 descriptions equal to an EVD matrix name.
  The result is labelled NOT_RESOLVED_REPORT_ONLY.
- Report (``counts_report`` / ``write_report``): integers, booleans, upper-case code tokens and
  input hashes / locators only, enforced by ``assert_counts_only``; it is the only output meant
  for git. It refuses ``data/`` (git-ignored) and protected areas.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from culinarystate.ingest import bognar_remaining as B
from culinarystate.ingest import usda_yields_r2 as Y
from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target

STATUS = "PROVISIONAL_PENDING_G12_AUDIT"
STAGE_VERSION = "step12_local_stage@0.1-provisional"
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_STAGING_DIR = "data/interim/step12_local_staging_v1"
_PROTECTED = (("ledgers",), ("exports",), ("annotation", "gold"))
_P2 = re.compile(r"Part 2 table (\d+)(?:, ([^,()]+), ([AB])\))?")
_CODE = re.compile(r"^[A-Z0-9_.:\-]+$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
_KEY = re.compile(r"^(?:[A-Za-z0-9_]+|[A-Z0-9_.\-]+)$")
_PATH = re.compile(r"^[A-Za-z0-9_./@\-]+$")
_FREE_SUBTREES = ("versions", "inputs")


class StagingError(ValueError):
    """Refused write or a report that is not counts-only."""


# ---------------------------------------------------------------- paths
def _rel_parts(target: Path, root: Path) -> tuple[str, ...] | None:
    try:
        return tuple(x.casefold() for x in target.relative_to(Path(root).resolve()).parts)
    except ValueError:
        return None


def _safe(target: Path) -> None:
    try:
        assert_safe_write_target(target)
    except ProtectedPathError as e:
        raise StagingError(str(e)) from e


def guard_staging_dir(path: Path | str, *, root: Path | str = ROOT) -> Path:
    """Inside the repository only ``data/interim/...`` (git-ignored) is accepted; outside it any path."""
    target = Path(path).resolve()
    parts = _rel_parts(target, Path(root))
    if parts is not None and (len(parts) < 3 or parts[:2] != ("data", "interim")):
        raise StagingError("staging holds raw third-party text: use data/interim/<dir> or a path outside the repo")
    _safe(target)
    return target


def guard_report_path(path: Path | str, root: Path | str) -> Path:
    target = Path(path).resolve()
    parts = _rel_parts(target, Path(root)) or ()
    if any(parts[:len(p)] == p for p in _PROTECTED) or parts[:1] == ("data",):
        raise StagingError("the counts report goes outside ledgers/, exports/, annotation/gold/ and data/")
    _safe(target)
    if target.exists():
        raise StagingError("refusing to overwrite an existing report")
    return target


def _jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records)


def write_staging(out_dir: Path | str, *, r2: Y.R2Result | None = None, bognar: B.BognarResult | None = None,
                  root: Path | str = ROOT) -> dict[str, Path]:
    d = guard_staging_dir(out_dir, root=root)
    files: dict[str, list[dict]] = {}
    note = "LOCAL ONLY: raw third-party text; never commit; not EVD"
    if r2 is not None:
        head = {"record": "STAGING_HEADER", "status": STATUS, "parser_version": Y.PARSER_VERSION,
                "input_sha256": r2.input_sha256, "count": len(r2.rows), "problems": list(r2.problems), "note": note}
        files["r2_rows.jsonl"] = [head, *r2.rows]
    if bognar is not None:
        head = {"record": "STAGING_HEADER", "status": STATUS, "parser_version": B.PARSER_VERSION,
                "input_sha256": bognar.input_sha256, "count": len(bognar.cells), "note": note}
        files["bognar_remaining_cells.jsonl"] = [head, *bognar.cells]
        tabs = [{"record": "BOGNAR_STAGED_TABLE", **{k: (list(v) if isinstance(v, tuple) else v) for k, v in t.items()}}
                for t in bognar.tables.values()]
        tab_head = {**head, "count": len(tabs), "problems": list(bognar.problems)}
        files["bognar_remaining_tables.jsonl"] = [tab_head, *tabs]
    if not files:
        raise StagingError("nothing to stage")
    targets = {name: d / name for name in files}
    if any(t.exists() for t in targets.values()):
        raise StagingError("refusing to overwrite existing staging files")
    d.mkdir(parents=True, exist_ok=True)
    for name, recs in files.items():
        with open(targets[name], "x", encoding="utf-8", newline="\n") as fh:
            fh.write(_jsonl(recs))
    return targets


# ---------------------------------------------------------------- diff (read-only, report only)
def _norm(s: Any) -> str:
    return " ".join(str(s or "").lower().split())


def _head(s: Any) -> str:
    return _norm(str(s or "").split(",")[0])


def latest_active_evd(path: Path | str) -> list[dict]:
    latest: dict[str, dict] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                latest[r["id"]] = r
    return [r for r in latest.values() if r.get("status") == "ACTIVE"]


def diff_against_evd(evd_path: Path | str, *, r2: Y.R2Result | None = None,
                     bognar: B.BognarResult | None = None) -> dict:
    evd = latest_active_evd(evd_path)
    out: dict[str, Any] = {"evd_rows_read_latest_active": len(evd), "context_gate": "G08-9",
                           "resolution": "NOT_RESOLVED_REPORT_ONLY"}
    if bognar is not None:
        per_table = Counter()
        keys, pairs = set(), set()
        for r in evd:
            if r.get("source_family_id") != "BOGNAR-2002":
                continue
            m = _P2.search((r.get("provenance") or {}).get("locator") or "")
            if not m:
                continue
            t = int(m.group(1))
            per_table[t] += 1
            target = _norm((r.get("target") or {}).get("raw_name"))
            method = _norm((r.get("process") or {}).get("raw_name"))
            keys.add((t, target, method, m.group(3) or "UNKNOWN"))
            pairs.add((target, method))
        usda = {_head((r.get("target") or {}).get("raw_name")) for r in evd
                if r.get("source_family_id") == "USDA-RETN-R6"}
        staged_pairs = {(_norm(c["constituent_raw"]), _norm(c["method_raw"])) for c in bognar.cells}
        out["bognar_remaining"] = {
            "existing_evd_rows_in_remaining_tables": {f"T{t}": per_table.get(t, 0) for t in B.REMAINING_TABLES},
            "staged_cells_exact_key_in_existing_evd": sum(
                (c["table"], _norm(c["constituent_raw"]), _norm(c["method_raw"]), c["basis"]) in keys
                for c in bognar.cells),
            "staged_constituent_method_pairs": len(staged_pairs),
            "staged_constituent_method_pairs_seen_in_existing_bognar": len(staged_pairs & pairs),
            "g08_9_context_constituents_shared_with_usda_r6": len({_head(c["constituent_raw"]) for c in bognar.cells}
                                                                  & usda),
        }
    if r2 is not None:
        yields = Counter(r.get("source_family_id") or "UNKNOWN" for r in evd
                         if (r.get("derived") or {}).get("yield_factor"))

        def yield_source(r: dict) -> str:
            return str(((r.get("process") or {}).get("modifiers") or {}).get("yield_source") or "").lower()
        pe_usda = sum(1 for r in evd
                      if r.get("source_family_id") == "PHENOL-EXPLORER-3.6" and "usda" in yield_source(r))
        names: dict[str, set[str]] = {}
        for r in evd:
            fam = r.get("source_family_id") or "UNKNOWN"
            names.setdefault(_norm((r.get("matrix") or {}).get("raw_name")), set()).add(fam)
        match = Counter()
        for row in r2.rows:
            for fam in names.get(_norm(row["normalised"]["description"].get("raw")), ()):
                match[fam] += 1
        out["r2"] = {"existing_evd_rows_with_yield_factor_by_family": dict(sorted(yields.items())),
                     "pe_rows_with_usda_yield_source": pe_usda,
                     "staged_rows_description_exact_match_in_evd_by_family": dict(sorted(match.items()))}
    return out


# ---------------------------------------------------------------- counts-only report
def assert_counts_only(obj: Any, _free: bool = False) -> None:
    """Integers, booleans, None, upper-case codes and sha256 only (paths/versions in their subtrees)."""
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            if not isinstance(k, str) or not _KEY.match(k):
                raise StagingError(f"report key is not a code token: {k!r}")
            assert_counts_only(v, _free or k in _FREE_SUBTREES)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            assert_counts_only(v, _free)
    elif isinstance(obj, str):
        if not (_CODE.match(obj) or _HEX.match(obj) or (_free and _PATH.match(obj) and len(obj) <= 300)):
            raise StagingError("report string is not a code, hash or input locator")
    elif obj is not None and not isinstance(obj, (bool, int)):
        raise StagingError(f"report value of type {type(obj).__name__} is not a count")


def counts_report(*, r2: Y.R2Result | None, bognar: B.BognarResult | None, diff: Mapping[str, Any],
                  inputs: Mapping[str, Any]) -> dict:
    rep: dict[str, Any] = {"status": STATUS, "versions": {"stage": STAGE_VERSION, "r2_parser": Y.PARSER_VERSION,
                                                         "bognar_parser": B.PARSER_VERSION},
                           "inputs": dict(inputs), "ledger_rows_appended": 0, "ids_minted": 0,
                           "raw_text_included": False}
    if r2 is not None:
        by_role = {role: dict(sorted(Counter(r["normalised"][role]["status"] for r in r2.rows).items()))
                   for role in Y.ROLE_NAMES}
        rep["r2"] = {"rows_staged": len(r2.rows), "rows_skipped": len(r2.problems),
                     "header_columns": len(r2.header_raw), "unmapped_columns": len(r2.unmapped_columns),
                     "status_counts_by_role": by_role,
                     "dispersion_type_counts": dict(sorted(Counter(r["dispersion_type"] for r in r2.rows).items())),
                     "rows_with_flags": sum(bool(r["flags"]) for r in r2.rows),
                     "release_year_1975_rows": sum(r["release_year_flag"] == "RELEASE_YEAR_1975" for r in r2.rows)}
    if bognar is not None:
        cells = bognar.cells
        rep["bognar_remaining"] = {
            "cells_staged": len(cells), "tables_found": list(bognar.tables_found),
            "tables_missing": list(bognar.tables_missing), "rows_skipped_or_table_problems": len(bognar.problems),
            "per_table": {f"T{no}": {"cells": t["cells"], "columns": t["columns"],
                                     "method_mapping": t["method_mapping"],
                                     "basis_line": t["basis_line"], "skipped_ragged_rows": t["skipped_ragged_rows"],
                                     "skipped_non_retention_rows": t["skipped_non_retention_rows"],
                                     "table_problem": t["problem"]} for no, t in bognar.tables.items()},
            "value_status_counts": dict(sorted(Counter(c["value_status"] for c in cells).items())),
            "method_mapping_counts": dict(sorted(Counter(c["method_mapping"] for c in cells).items())),
            "basis_counts": dict(sorted(Counter(c["basis"] for c in cells).items())),
            "estimated_cells": sum(c["estimated"] for c in cells)}
    rep["diff"] = dict(diff)
    assert_counts_only(rep)
    return rep


def write_report(rep: Mapping[str, Any], path: Path | str, *, root: Path | str = ROOT) -> Path:
    assert_counts_only(rep)
    target = guard_report_path(path, root)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    return target
