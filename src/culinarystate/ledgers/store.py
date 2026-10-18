"""Append-only, versioned JSONL ledger store with a never-reuse ID minter.

Layout (under `root`, default `ledgers/data/`):
  _ids.jsonl          one line per minted id: {id, prefix, key, minted_at}
  <PREFIX>.jsonl      every version of every record, in append order

Updating a record = appending version n+1 with the same id. Nothing is rewritten.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from .common import ID_DIGITS, SCHEMA_VERSION
from .registry import R
from .validate import validate

DEFAULT_ROOT = Path(__file__).resolve().parents[3] / "ledgers" / "data"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


class IdMinter:
    """Mint `PREFIX-000123`. Same dedup key -> same id. Numbers are never reused."""

    def __init__(self, root: Path = DEFAULT_ROOT):
        self.path = Path(root) / "_ids.jsonl"
        self._by_key: dict[tuple[str, str], str] = {}
        self._max: dict[str, int] = {}
        for row in _read_jsonl(self.path):
            self._index(row)

    def _index(self, row: dict) -> None:
        n = int(row["id"].rsplit("-", 1)[1])
        self._max[row["prefix"]] = max(self._max.get(row["prefix"], 0), n)
        if row.get("key") is not None:
            self._by_key[(row["prefix"], row["key"])] = row["id"]

    def lookup(self, prefix: str, key: str) -> str | None:
        return self._by_key.get((prefix, key))

    def mint(self, prefix: str, key: str | None = None) -> str:
        if prefix not in R:
            raise KeyError(f"unknown prefix {prefix}")
        if key is not None and (prefix, key) in self._by_key:
            return self._by_key[(prefix, key)]
        new_id = f"{prefix}-{self._max.get(prefix, 0) + 1:0{ID_DIGITS}d}"
        row = {"id": new_id, "prefix": prefix, "key": key, "minted_at": now_iso()}
        _append_jsonl(self.path, row)
        self._index(row)
        return new_id


class LedgerStore:
    def __init__(self, root: Path = DEFAULT_ROOT):
        self.root = Path(root)
        self.ids = IdMinter(self.root)
        self._cache: dict[str, list[dict]] = {}

    def _rows(self, prefix: str) -> list[dict]:
        if prefix not in self._cache:
            self._cache[prefix] = _read_jsonl(self.root / f"{prefix}.jsonl")
        return self._cache[prefix]

    def history(self, record_id: str) -> list[dict]:
        prefix = record_id.split("-", 1)[0]
        return [copy.deepcopy(r) for r in self._rows(prefix) if r["id"] == record_id]

    def latest(self, record_id: str) -> dict | None:
        h = self.history(record_id)
        return h[-1] if h else None

    def all_latest(self, prefix: str) -> list[dict]:
        last: dict[str, dict] = {}
        for r in self._rows(prefix):
            last[r["id"]] = r
        return [copy.deepcopy(r) for r in last.values()]

    def append(self, record: dict) -> dict:
        """Validate and append. Returns the stored copy (input is not mutated)."""
        rec = copy.deepcopy(record)
        rec.setdefault("schema_version", SCHEMA_VERSION)
        rec.setdefault("created_at", now_iso())
        prefix = rec.get("record_type")
        minted = self.ids._max.get(prefix, 0)
        rid = rec.get("id", "")
        if not rid.startswith(f"{prefix}-") or int(rid.rsplit("-", 1)[1] or 0) > minted:
            raise ValueError(f"{rid}: id was not minted by IdMinter for {prefix}")
        prev = self.latest(rid)
        expected = prev["version"] + 1 if prev else 1
        if rec.get("version") != expected:
            raise ValueError(f"{rid}: version must be {expected}, got {rec.get('version')}")
        validate(rec)
        _append_jsonl(self.root / f"{prefix}.jsonl", rec)
        self._rows(prefix).append(rec)
        return copy.deepcopy(rec)

    def revise(self, record_id: str, changes: dict, created_by: str) -> dict:
        """Append a new version built from the latest one plus `changes`."""
        prev = self.latest(record_id)
        if prev is None:
            raise KeyError(record_id)
        new = {**prev, **copy.deepcopy(changes), "version": prev["version"] + 1,
               "created_at": now_iso(), "created_by": created_by}
        return self.append(new)
