"""Baseline and write-target guards protecting the append-only ledgers."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

_PROTECTED_PREFIXES: tuple[tuple[str, ...], ...] = (("ledgers", "data"), ("exports", "evd"))
_CHUNK = 1 << 20
# D-032: STUDY and _ids may be appended to; their baseline bytes must stay an unchanged prefix.
_APPEND_ONLY = ("ledgers/data/STUDY.jsonl", "ledgers/data/_ids.jsonl")


class LedgerBaselineMismatch(RuntimeError):
    """A ledger file differs from the registered 08a baseline."""


class ProtectedPathError(RuntimeError):
    """A write target lies inside a protected ledger/export area."""


def _sha256_and_size(path: Path) -> tuple[str, int]:
    h, size = hashlib.sha256(), 0
    with path.open("rb") as f:
        for block in iter(lambda: f.read(_CHUNK), b""):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size


def _prefix_sha256(path: Path, nbytes: int) -> str:
    h, left = hashlib.sha256(), nbytes
    with path.open("rb") as f:
        while left > 0:
            block = f.read(min(_CHUNK, left))
            if not block:
                break
            h.update(block)
            left -= len(block)
    return h.hexdigest()


def verify_baseline(csv_path: Path, root: Path) -> int:
    """Recompute sha256+size of every file listed in the CSV under root (STUDY/_ids: unchanged prefix, growth allowed).

    Returns the number of files verified; raises LedgerBaselineMismatch
    naming the first differing file (missing files count as a difference).
    """
    with Path(csv_path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise LedgerBaselineMismatch(f"empty baseline CSV: {csv_path}")
    for row in rows:
        rel = row["path"]
        target = Path(root) / rel
        if not target.is_file():
            raise LedgerBaselineMismatch(f"{rel}: file missing")
        if rel in _APPEND_ONLY:
            n = int(row["bytes"])
            if target.stat().st_size < n:
                raise LedgerBaselineMismatch(f"{rel}: shorter than baseline {n}")
            if _prefix_sha256(target, n) != row["sha256"]:
                raise LedgerBaselineMismatch(f"{rel}: baseline prefix changed")
            continue
        digest, size = _sha256_and_size(target)
        if size != int(row["bytes"]):
            raise LedgerBaselineMismatch(f"{rel}: size {size} != baseline {row['bytes']}")
        if digest != row["sha256"]:
            raise LedgerBaselineMismatch(f"{rel}: sha256 differs from baseline")
    return len(rows)


def assert_safe_write_target(path: Path) -> None:
    """Raise ProtectedPathError if path is inside ledgers/data or exports/evd."""
    import os
    parts = Path(os.path.abspath(path)).parts
    for prefix in _PROTECTED_PREFIXES:
        k = len(prefix)
        if any(parts[i:i + k] == prefix for i in range(len(parts) - k + 1)):
            raise ProtectedPathError(f"protected write target: {path}")
