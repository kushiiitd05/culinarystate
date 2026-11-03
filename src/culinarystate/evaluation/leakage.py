"""DRAFT_PENDING_15aR_15b -- leakage checks for the evaluation harness (synthetic-tested).

Checks (each returns ``CODE: detail`` strings; values are counted, never echoed):

* ``GROUP_OVERLAP``: a value of a declared group column sits in more than one role.
* ``NEAR_DUPLICATE_OVERLAP``: a caller-defined near-duplicate key sits in more than one
  role (no normaliser is chosen here; the caller's key function is the convention).
* ``ROW_NOT_IN_SPLIT``: a row handed to the check is not assigned by the split.

Reserved-group exclusion (15a.R): ``load_sealed_reserved`` verifies a sealed list against
its commitment with ``reserved_seal.verify_sealed_list`` (reused read-only) and refuses on
any mismatch. ``exclude_reserved`` drops every component that contains a reserved row; a
component that also holds DEV rows is counted as burned (plan Step 15: a merged RESERVED/DEV
component is burned). ``assert_reserved_excluded`` refuses any use of a reserved group.
Reports carry counts only, never reserved group ids or row ids.

Modes: ``DIAGNOSTIC`` is the only mode available. ``HEADLINE`` is 15b-only and is always
refused here, because no 15b freeze exists and no 15b record format has been defined.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from culinarystate.evaluation.splits import GroupSplit, group_components, values_on_multiple_roles

STATUS = "DRAFT_PENDING_15aR_15b"
MODES = ("DIAGNOSTIC", "HEADLINE")
DIAGNOSTIC_LABELS = ("DIAGNOSTIC_ONLY", "BOOTSTRAP_UNVERIFIED", "COND_UNAUDITED")


class LeakageRefused(RuntimeError):
    """A leakage rule is violated; ``blockers`` lists every reason as ``CODE: detail``."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("leakage check refused: " + "; ".join(self.blockers))


# ---------------------------------------------------------------- overlap

def check_leakage(split: GroupSplit, rows: Sequence[Mapping[str, Any]], *, id_column: str,
                  group_columns: Sequence[str],
                  near_dup_key: Optional[Callable[[Mapping[str, Any]], Iterable[str]]] = None) -> list[str]:
    """Every leakage finding for ``rows`` under ``split`` (empty list = clean)."""
    out: list[str] = []
    unassigned = [r for r in rows if str(r.get(id_column)) not in split.assignment]
    if unassigned:
        out.append(f"ROW_NOT_IN_SPLIT: {len(unassigned)} row(s) are not assigned by the split")
    for col in group_columns:
        multi = values_on_multiple_roles(split, rows, id_column=id_column, column=col)
        if multi:
            out.append(f"GROUP_OVERLAP: {col}: {len(multi)} value(s) on more than one role")
    if near_dup_key is not None:
        roles_of: dict[str, set[str]] = {}
        for r in rows:
            role = split.assignment.get(str(r.get(id_column)))
            if role is None:
                continue
            for key in near_dup_key(r):
                if key is not None and str(key) != "":
                    roles_of.setdefault(str(key), set()).add(role)
        n = sum(1 for v in roles_of.values() if len(v) > 1)
        if n:
            out.append(f"NEAR_DUPLICATE_OVERLAP: {n} near-duplicate key(s) on more than one role")
    return out


def assert_no_leakage(split: GroupSplit, rows: Sequence[Mapping[str, Any]], *, id_column: str,
                      group_columns: Sequence[str],
                      near_dup_key: Optional[Callable[[Mapping[str, Any]], Iterable[str]]] = None) -> None:
    found = check_leakage(split, rows, id_column=id_column, group_columns=group_columns, near_dup_key=near_dup_key)
    if found:
        raise LeakageRefused(found)


# ---------------------------------------------------------------- 15a.R reserved groups

def load_sealed_reserved(commitment: Mapping[str, Any], sealed_bytes: bytes) -> frozenset[str]:
    """Reserved group ids from a sealed list that verifies against ``commitment``; else refuse."""
    from culinarystate.lineage import reserved_seal as rs  # lazy: the seal module pulls in pandas

    if not rs.verify_sealed_list(sealed_bytes, commitment):
        raise LeakageRefused(["SEAL_COMMITMENT_MISMATCH: sealed list or commitment payload hash differs"])
    ids: list[str] = []
    try:
        for line in sealed_bytes.decode("utf-8").splitlines():
            if line.strip():
                ids.append(str(json.loads(line)["group_id"]))
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
        raise LeakageRefused([f"SEALED_LIST_MALFORMED: {type(exc).__name__}"]) from None
    if len(ids) != len(set(ids)) or len(ids) != commitment.get("n_reserved"):
        raise LeakageRefused(["SEAL_COMMITMENT_MISMATCH: reserved count differs from the commitment"])
    return frozenset(ids)


def seal_group_id(row: Mapping[str, Any], unit: str) -> str:
    """The 15a.R group id of one EVD-shaped row under ``unit`` (same rule as the seal)."""
    from culinarystate.lineage import reserved_seal as rs

    (gid,) = rs.build_groups([row], unit)
    return gid


@dataclass(frozen=True)
class ReservedExclusion:
    kept_rows: tuple[Mapping[str, Any], ...]
    n_rows: int
    n_excluded_rows: int
    n_reserved_rows: int
    n_burned_components: int
    n_burned_dev_rows: int

    def report(self) -> dict[str, Any]:
        """Counts only; safe to write to git."""
        return {"status": STATUS, "n_rows": self.n_rows, "n_kept_rows": len(self.kept_rows),
                "n_excluded_rows": self.n_excluded_rows, "n_reserved_rows": self.n_reserved_rows,
                "n_burned_components": self.n_burned_components, "n_burned_dev_rows": self.n_burned_dev_rows}


def _seal_groups(row_ids: Iterable[str], row_seal_group: Mapping[str, str]) -> dict[str, str]:
    ids = list(row_ids)
    missing = [r for r in ids if not row_seal_group.get(r)]
    if missing:
        raise LeakageRefused([f"SEAL_GROUP_UNKNOWN: {len(missing)} row(s) have no 15a.R group id"])
    return {r: row_seal_group[r] for r in ids}


def exclude_reserved(rows: Sequence[Mapping[str, Any]], *, id_column: str, group_columns: Sequence[str],
                     row_seal_group: Mapping[str, str], reserved: frozenset[str]) -> ReservedExclusion:
    """Drop every component holding a reserved row; components mixing RESERVED and DEV are burned."""
    comp = group_components(rows, id_column=id_column, group_columns=group_columns)
    seal = _seal_groups(comp, row_seal_group)
    is_res = {r: seal[r] in reserved for r in comp}
    res_comps = {comp[r] for r, flag in is_res.items() if flag}
    burned = {c for c in res_comps if any(comp[r] == c and not is_res[r] for r in comp)}
    kept = tuple(row for row in rows if comp[str(row.get(id_column))] not in res_comps)
    return ReservedExclusion(kept_rows=kept, n_rows=len(rows), n_excluded_rows=len(rows) - len(kept),
                             n_reserved_rows=sum(is_res.values()), n_burned_components=len(burned),
                             n_burned_dev_rows=sum(1 for r in comp if comp[r] in burned and not is_res[r]))


def assert_reserved_excluded(row_ids: Iterable[str], *, row_seal_group: Mapping[str, str],
                             reserved: frozenset[str]) -> None:
    """Refuse if any row about to be used belongs to a reserved group (counts only in the message)."""
    seal = _seal_groups(row_ids, row_seal_group)
    used = sum(1 for g in seal.values() if g in reserved)
    if used:
        raise LeakageRefused([f"RESERVED_GROUP_USED: {used} row(s) belong to 15a.R RESERVED groups"])


# ---------------------------------------------------------------- modes

def freeze_15b_status(root: Path | str) -> tuple[bool, str]:
    """(frozen, reason). Always (False, ...) in this scaffold: no 15b freeze record format exists.

    The paper-grade freeze 15b is HARD on a valid Step-07 gate pass, 08a, 08b and Steps 11-14
    (plan Step 15); none of that exists, and a file appearing on disk is not verifiable
    until humans define the 15b record. This function never reads such a file.
    """
    return False, "15b is NOT_FROZEN: no verifiable 15b freeze record is defined (DRAFT_PENDING_15b)"


def require_mode(mode: str, *, root: Path | str) -> tuple[str, ...]:
    """Labels every result in ``mode`` must carry, or refuse (HEADLINE needs a frozen 15b)."""
    if mode not in MODES:
        raise LeakageRefused([f"MODE_UNKNOWN: {mode!r} not in {MODES}"])
    if mode == "HEADLINE":
        # No headline label set exists yet either: even a frozen 15b would need a new, reviewed version.
        _, reason = freeze_15b_status(root)
        raise LeakageRefused([f"HEADLINE_REQUIRES_15B: {reason}"])
    return DIAGNOSTIC_LABELS
