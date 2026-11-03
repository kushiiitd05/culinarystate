"""DRAFT_PENDING_15_0 -- group-aware evaluation splits (Steps 29/30/34 harness, synthetic-tested).

Rows are linked whenever they share a value in ANY declared group column (for example
lineage group, study, split group, near-duplicate key); the connected components are
the units of assignment, so no group value and no component can sit on two sides.
Components come from the existing ``lineage.unionfind.components`` (reused read-only).
``transition/splits.py`` is not reused: it needs pandas and carries default fractions
(0.15/0.2) that were never pre-registered.

Nothing is defaulted: role fractions, seed, remainder role and fold count are required.
A missing, empty or literal ``UNKNOWN`` group value is refused (UNKNOWN cannot be placed
safely, and grouping all UNKNOWNs together would fake a giant component).

Assignment rule ``RULE_ID``: rank components by sha256(rule id, seed, component key); in
the order of ``role_fractions`` every non-remainder role takes floor(fraction x n)
components; the remainder role takes the rest. A role left empty is refused.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.lineage.unionfind import components

RULE_ID = "eval-split-sha256-rank-v1"
STATUS = "DRAFT_PENDING_15_0"
UNKNOWN_VALUES = frozenset({"UNKNOWN"})


class SplitRefused(RuntimeError):
    """The split cannot be made; ``blockers`` lists every reason as ``CODE: detail``."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("split refused: " + "; ".join(self.blockers))


def _canon(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class GroupSplit:
    roles: tuple[str, ...]
    assignment: Mapping[str, str]
    component_of: Mapping[str, str]
    group_columns: tuple[str, ...]
    seed: str
    rule_id: str = RULE_ID
    n_excluded_components: int = 0
    note: str = field(default="")

    def rows(self, role: str) -> tuple[str, ...]:
        return tuple(sorted(r for r, x in self.assignment.items() if x == role))

    @property
    def n_rows(self) -> dict[str, int]:
        return {role: len(self.rows(role)) for role in self.roles}

    @property
    def n_components(self) -> dict[str, int]:
        out: dict[str, set[str]] = {role: set() for role in self.roles}
        for rid, role in self.assignment.items():
            out[role].add(self.component_of[rid])
        return {role: len(v) for role, v in out.items()}

    def sha256(self) -> str:
        return _canon({"rule_id": self.rule_id, "seed": self.seed, "group_columns": list(self.group_columns),
                       "roles": list(self.roles), "assignment": dict(sorted(self.assignment.items()))})

    def manifest(self) -> dict[str, Any]:
        """Counts and hashes only: no row values, no group values."""
        return {"status": STATUS, "rule_id": self.rule_id, "group_columns": list(self.group_columns),
                "seed": self.seed, "roles": list(self.roles), "n_rows": self.n_rows,
                "n_components": self.n_components, "n_excluded_components": self.n_excluded_components,
                "assignment_sha256": self.sha256(), "note": self.note}


def _values(row: Mapping[str, Any], col: str) -> list[str]:
    v = row.get(col)
    items = list(v) if isinstance(v, (list, tuple, set, frozenset)) else [v]
    return [str(x) for x in items if x is not None and str(x).strip() != ""]


def group_components(rows: Sequence[Mapping[str, Any]], *, id_column: str,
                     group_columns: Sequence[str]) -> dict[str, str]:
    """row id -> component key ("C-" + sha256 of its sorted member row ids)."""
    blockers: list[str] = []
    cols = tuple(group_columns)
    if not cols:
        blockers.append("NO_GROUP_COLUMNS: at least one group column is required")
    ids: list[str] = []
    edges: list[tuple[str, str]] = []
    seen: set[str] = set()
    missing: dict[str, list[str]] = {}
    unknown: dict[str, list[str]] = {}
    for i, row in enumerate(rows):
        rid = row.get(id_column)
        if rid is None or str(rid).strip() == "":
            blockers.append(f"ROW_ID_MISSING: row #{i} has no {id_column!r}")
            continue
        rid = str(rid)
        if rid in seen:
            blockers.append(f"ROW_ID_DUPLICATE: {rid}")
            continue
        seen.add(rid)
        ids.append(rid)
        for col in cols:
            vals = _values(row, col)
            if not vals:
                missing.setdefault(col, []).append(rid)
            elif any(v in UNKNOWN_VALUES for v in vals):
                unknown.setdefault(col, []).append(rid)
            for v in vals:
                edges.append((f"R\x00{rid}", f"V\x00{col}\x00{v}"))
    for col, rids in sorted(missing.items()):
        blockers.append(f"GROUP_VALUE_MISSING: {len(rids)} row(s) without {col!r}, e.g. {rids[0]}")
    for col, rids in sorted(unknown.items()):
        blockers.append(f"GROUP_VALUE_UNKNOWN: {len(rids)} row(s) with {col!r} = UNKNOWN, e.g. {rids[0]}")
    if blockers:
        raise SplitRefused(blockers)
    root_of, _ = components([f"R\x00{r}" for r in ids], edges)
    members: dict[str, list[str]] = {}
    for rid in ids:
        members.setdefault(root_of[f"R\x00{rid}"], []).append(rid)
    out: dict[str, str] = {}
    for rids in members.values():
        key = "C-" + _canon(sorted(rids))
        for rid in rids:
            out[rid] = key
    return out


def _fraction(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ValueError(value)
    if isinstance(value, (Fraction, int)):
        f = Fraction(value)
    else:
        s = str(value).strip()
        if not s or any(c not in "0123456789./" for c in s):
            raise ValueError(value)
        f = Fraction(s)
    if not 0 < f < 1:
        raise ValueError(value)
    return f


def _rank(keys: Iterable[str], seed: str) -> list[str]:
    return sorted(set(keys), key=lambda k: (hashlib.sha256(f"{RULE_ID}\n{seed}\n{k}".encode("utf-8")).hexdigest(), k))


def group_aware_split(rows: Sequence[Mapping[str, Any]], *, id_column: str, group_columns: Sequence[str],
                      role_fractions: Mapping[str, Any], seed: str, remainder_role: str,
                      exclude_components: Iterable[str] = ()) -> GroupSplit:
    """Assign whole components to roles; refuses with every blocker collected."""
    blockers: list[str] = []
    fracs: dict[str, Fraction] = {}
    for role, value in role_fractions.items():
        try:
            fracs[str(role)] = _fraction(value)
        except (ValueError, ZeroDivisionError):
            blockers.append(f"FRACTION_INVALID: {role!r} needs a fraction strictly between 0 and 1")
    if not blockers and sum(fracs.values()) != 1:
        blockers.append(f"FRACTIONS_NOT_ONE: role fractions sum to {sum(fracs.values())}")
    if remainder_role not in role_fractions:
        blockers.append(f"REMAINDER_ROLE_UNKNOWN: {remainder_role!r} is not one of the roles")
    if not isinstance(seed, str) or not seed:
        blockers.append("SEED_MISSING: a non-empty seed string is required")
    if blockers:
        raise SplitRefused(blockers)
    comp = group_components(rows, id_column=id_column, group_columns=group_columns)
    excluded = set(exclude_components)
    usable = _rank((c for c in comp.values() if c not in excluded), seed)
    n = len(usable)
    role_of_comp: dict[str, str] = {}
    pos = 0
    for role, frac in fracs.items():
        if role == remainder_role:
            continue
        k = math.floor(frac * n)
        for c in usable[pos:pos + k]:
            role_of_comp[c] = role
        pos += k
    for c in usable[pos:]:
        role_of_comp[c] = remainder_role
    roles = tuple(fracs)
    counts = {role: sum(1 for r in role_of_comp.values() if r == role) for role in roles}
    empty = [role for role, k in counts.items() if k == 0]
    if empty:
        raise SplitRefused([f"ROLE_EMPTY: role {role!r} gets 0 of {n} components" for role in empty])
    assignment = {rid: role_of_comp[c] for rid, c in comp.items() if c in role_of_comp}
    return GroupSplit(roles=roles, assignment=assignment, component_of={r: comp[r] for r in assignment},
                      group_columns=tuple(group_columns), seed=seed,
                      n_excluded_components=len(excluded & set(comp.values())))


def group_kfold(rows: Sequence[Mapping[str, Any]], *, id_column: str, group_columns: Sequence[str],
                n_folds: int, seed: str, exclude_components: Iterable[str] = ()) -> list[GroupSplit]:
    """Grouped K-fold over components (rank position mod n_folds); each fold is (train, test)."""
    if not isinstance(seed, str) or not seed:
        raise SplitRefused(["SEED_MISSING: a non-empty seed string is required"])
    comp = group_components(rows, id_column=id_column, group_columns=group_columns)
    excluded = set(exclude_components)
    ranked = _rank((c for c in comp.values() if c not in excluded), seed)
    if not isinstance(n_folds, int) or isinstance(n_folds, bool) or not 2 <= n_folds <= len(ranked):
        raise SplitRefused([f"N_FOLDS_INVALID: need 2 <= n_folds <= {len(ranked)} components, got {n_folds!r}"])
    fold_of = {c: i % n_folds for i, c in enumerate(ranked)}
    out = []
    for k in range(n_folds):
        assignment = {rid: ("test" if fold_of[c] == k else "train") for rid, c in comp.items() if c in fold_of}
        out.append(GroupSplit(roles=("train", "test"), assignment=assignment,
                              component_of={r: comp[r] for r in assignment}, group_columns=tuple(group_columns),
                              seed=seed, n_excluded_components=len(excluded & set(comp.values())),
                              note=f"fold {k + 1} of {n_folds}"))
    return out


def values_on_multiple_roles(split: GroupSplit, rows: Sequence[Mapping[str, Any]], *, id_column: str,
                             column: str) -> dict[str, list[str]]:
    """Group values of ``column`` that occur in more than one role (empty dict = disjoint)."""
    roles_of: dict[str, set[str]] = {}
    for row in rows:
        role = split.assignment.get(str(row.get(id_column)))
        if role is None:
            continue
        for v in _values(row, column):
            roles_of.setdefault(v, set()).add(role)
    return {v: sorted(r) for v, r in sorted(roles_of.items()) if len(r) > 1}
