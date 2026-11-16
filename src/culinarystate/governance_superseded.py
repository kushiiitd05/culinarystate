"""Superseded-output guard (S178 FIX-GOV, GOV-1 / GOV-2).

``registry/superseded_outputs_S176.csv`` lists every committed output that a later run replaced or found invalid
(columns ``path, sha256, superseded_by, superseded_by_sha256, reason, recorded_at, status``). A live tool calls
:func:`assert_not_superseded` on the paths it is about to read; the call raises :class:`SupersededInputError` when
any of them is registered, so a table or slide can no longer be built from a superseded layer by accident.

Rules
- Paths are compared repo-relative and normalised (``./``, ``..`` and absolute paths under the root are resolved).
- A registry path ending in ``/`` names a directory: every file under it is refused too.
- Every row is refused whatever its ``status`` (SUPERSEDED_* and INVALID_* alike). A row is "declared deleted" only
  when its status contains ``DELETED``; the integrity test then expects the file to be absent.
- A missing registry fails closed (``FileNotFoundError``): the guard never passes silently.

The guard reads only the registry CSV. It does not decide what is superseded; the registry rows do (AI_DRAFTED,
appended by lanes and the orchestrator).
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Iterable

REGISTRY = "registry/superseded_outputs_S176.csv"
COLUMNS = ("path", "sha256", "superseded_by", "superseded_by_sha256", "reason", "recorded_at", "status")
_ROOT = Path(__file__).resolve().parents[2]


class SupersededInputError(RuntimeError):
    """An input path is listed in the superseded-output registry."""


def load_registry(root: Path | str | None = None) -> list[dict]:
    root = Path(root) if root is not None else _ROOT
    with open(root / REGISTRY, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def declared_deleted(row: dict) -> bool:
    return "DELETED" in (row.get("status") or "").upper()


def is_repo_path(value: str) -> bool:
    """True when a ``superseded_by`` cell names a repo file (not prose such as 'PENDING_MAC_RERUN (BBC, D-003)')."""
    v = (value or "").strip()
    return bool(v) and " " not in v and "/" in v and not v.endswith("/") and "." in v.rsplit("/", 1)[-1]


def _norm(p: Path | str, root: Path) -> str:
    s = str(p)
    is_dir = s.endswith("/")
    q = Path(s)
    if q.is_absolute():
        try:
            q = Path(os.path.normpath(q)).relative_to(Path(os.path.normpath(root)))
        except ValueError:
            return os.path.normpath(s) + ("/" if is_dir else "")
    out = os.path.normpath(q.as_posix()).replace(os.sep, "/")
    return out + ("/" if is_dir else "")


def find_superseded(paths: Iterable[Path | str], root: Path | str | None = None) -> list[tuple[str, dict]]:
    """[(normalised input path, registry row)] for every input that the registry lists (file or directory match)."""
    root = Path(root) if root is not None else _ROOT
    rows = load_registry(root)
    exact = {_norm(r["path"], root).rstrip("/"): r for r in rows if r.get("path")}
    dirs = [(k, r) for k, r in exact.items() if r["path"].endswith("/")]
    hits = []
    for p in paths:
        n = _norm(p, root).rstrip("/")
        row = exact.get(n)
        if row is None:
            row = next((r for k, r in dirs if n.startswith(k + "/")), None)
        if row is not None:
            hits.append((n, row))
    return hits


def assert_not_superseded(paths: Iterable[Path | str], root: Path | str | None = None) -> None:
    hits = find_superseded(list(paths), root)
    if hits:
        lines = [f"{p} (status {r.get('status')}; superseded_by {r.get('superseded_by')}; reason: {r.get('reason')})" for p, r in hits]
        raise SupersededInputError("refusing superseded input(s) listed in " + REGISTRY + ":\n  " + "\n  ".join(lines))
