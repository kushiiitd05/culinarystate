"""Step 18a/18c append-only engine event log and canonical JSON (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c. Hard gate 16c (Step 16 schema pack v1) is open, so the
event shape here is an engineering contract draft for the Step 18 replayer, not the
EVT / ENTITY / STATE / ALLOC ledger schema. Nothing here reads or writes a ledger.

Contents
- ``canonical_json``: sorted keys, compact separators, UTF-8 (``ensure_ascii=False``),
  no NaN / infinity, ``Fraction`` as ``"n/d"``, tuples as lists; any other type is
  refused rather than stringified. Plain ``json`` only (plan 18c: no pandas in the core).
- ``EngineEvent``: one engine event (consumes / produces / discards, allocations,
  traced quantity terms, claim route, trajectory, revision). Vocabularies come from
  the Step 16 drafts: ALLOC kind / basis, EVT trajectory, rc2 claim routes. Quantity
  terms must name the grounded QNT result they come from (no untraced amounts) and
  carry exact ``Fraction`` bounds in g, mL or count (never converted between them).
- ``EventLog``: in-memory, append-only, hash-chained. A correction is a new revision
  appended under the same ``event_id`` (revision n+1); earlier entries are never
  rewritten. ``effective()`` gives the latest revision of each event at the position
  where the event first appeared.
- JSONL writers that refuse ``ledgers/``, ``data/``, ``exports/``, ``annotation/gold/``,
  any ledger file name (EVT/ENTITY/STATE/ALLOC/REF/GRAPH/INST ``.jsonl``) and any
  overwrite; ``extend_log_jsonl`` appends only when the file is a byte prefix of the log.

Ids are local to the producer (never minted ledger ids). ``source_ref`` and quantity
``ref`` hold ids only, never raw source text (third-party text stays in ``data/raw``).
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Union

from culinarystate.quantity.draft_contract import CLAIM_ROUTES

STATUS = "DRAFT_PENDING_16c"
EVENT_SCHEMA_VERSION = "step18-engine-event-0.1.0-draft"
LOG_SCHEMA_VERSION = "step18-event-log-0.1.0-draft"
ROOT = Path(__file__).resolve().parents[3]

TRAJECTORIES = ("PLANNED", "OBSERVED_SESSION", "PREDICTED")            # EVT.draft_v1 trajectory
ALLOC_KINDS = ("SPLIT", "RESERVE", "REMAINDER", "RECOMBINE", "DISCARD")  # ALLOC.draft_v1 kind
ALLOC_BASES = ("MASS", "VOLUME", "COUNT", "UNSPECIFIED")                # ALLOC.draft_v1 basis
QUANTITY_DIMS = ("g", "mL", "count")
BASIS_DIM = {"MASS": "g", "VOLUME": "mL", "COUNT": "count"}
GENESIS_SHA256 = "0" * 64

PROTECTED_PREFIXES = (("ledgers",), ("data",), ("exports",), ("annotation", "gold"))
LEDGER_FILE_NAMES = frozenset(f"{n}.JSONL" for n in ("EVT", "ENTITY", "STATE", "ALLOC", "REF", "GRAPH", "INST"))

FractionValue = Union[Fraction, tuple[Fraction, Fraction], None]


class EventLogError(ValueError):
    """Structural contract violation or refused write (programming error, not a data issue)."""


# ---------------------------------------------------------------- canonical JSON
def _plain(obj: Any, path: str = "$") -> Any:
    if obj is None or isinstance(obj, (bool, str)):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise EventLogError(f"non-finite float at {path}")
        return obj
    if isinstance(obj, Fraction):
        return f"{obj.numerator}/{obj.denominator}"
    if isinstance(obj, Enum):
        return _plain(obj.value, path)
    if isinstance(obj, (list, tuple)):
        return [_plain(v, f"{path}[{i}]") for i, v in enumerate(obj)]
    if isinstance(obj, Mapping):
        out = {}
        for k, v in obj.items():
            if not isinstance(k, str):
                raise EventLogError(f"non-string key at {path}")
            out[k] = _plain(v, f"{path}.{k}")
        return out
    raise EventLogError(f"{type(obj).__name__} at {path} has no canonical JSON form")


def canonical_json(obj: Any) -> str:
    """Deterministic JSON text of ``obj`` (see module docstring for the rules)."""
    return json.dumps(_plain(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_canonical(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _frac_out(value: FractionValue) -> Any:
    return list(value) if isinstance(value, tuple) else value


def _frac_in(value: Any) -> FractionValue:
    if value is None:
        return None
    if isinstance(value, list):
        return tuple(Fraction(v) for v in value)  # type: ignore[return-value]
    return Fraction(value)


# ---------------------------------------------------------------- validation helpers
def _nonblank(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise EventLogError(f"{name} must be a nonblank string")


def _ids(value: Any, name: str) -> None:
    if not isinstance(value, tuple):
        raise EventLogError(f"{name} must be a tuple of ids")
    for v in value:
        _nonblank(v, name)


def _pairs(value: Any, name: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, tuple):
        raise EventLogError(f"{name} must be a tuple of (key, value) pairs")
    keys = []
    for item in value:
        if not (isinstance(item, tuple) and len(item) == 2):
            raise EventLogError(f"{name} items must be (key, value) pairs")
        _nonblank(item[0], f"{name} key")
        _nonblank(item[1], f"{name} value")
        keys.append(item[0])
    if len(keys) != len(set(keys)):
        raise EventLogError(f"{name} keys must be unique")
    return tuple(sorted(value))


def _exact(value: Any, name: str) -> None:
    if type(value) is not Fraction:
        raise EventLogError(f"{name} must be an exact Fraction")


@dataclass(frozen=True)
class QuantityTerm:
    """An amount for an entity produced by the event, traced to a grounded QNT result ``ref``."""
    entity_id: str
    dim: str
    low: Fraction
    high: Fraction
    ref: str

    def __post_init__(self) -> None:
        _nonblank(self.entity_id, "quantity entity_id")
        _nonblank(self.ref, "QUANTITY_UNTRACED: quantity ref")
        if self.dim not in QUANTITY_DIMS:
            raise EventLogError(f"quantity dim must be one of {QUANTITY_DIMS} (no unit conversion here)")
        _exact(self.low, "quantity low")
        _exact(self.high, "quantity high")
        if self.low > self.high:
            raise EventLogError("quantity interval is inverted")
        if self.low < 0:
            raise EventLogError("negative quantity (rule OPEN, refused)")

    def to_canonical(self) -> dict:
        return {"entity_id": self.entity_id, "dim": self.dim, "low": self.low, "high": self.high, "ref": self.ref}


@dataclass(frozen=True)
class Allocation:
    """Split / reserve / remainder / recombine / discard relation of one event (ALLOC draft enums)."""
    alloc_id: str
    kind: str
    basis: str
    parent: str
    child: str
    fraction: FractionValue = None

    def __post_init__(self) -> None:
        for name in ("alloc_id", "parent", "child"):
            _nonblank(getattr(self, name), f"allocation {name}")
        if self.kind not in ALLOC_KINDS:
            raise EventLogError(f"allocation kind must be one of {ALLOC_KINDS}")
        if self.basis not in ALLOC_BASES:
            raise EventLogError(f"allocation basis must be one of {ALLOC_BASES}")
        f = self.fraction
        if isinstance(f, tuple):
            if len(f) != 2:
                raise EventLogError("interval fraction must be a (low, high) pair")
            _exact(f[0], "fraction low")
            _exact(f[1], "fraction high")
        elif f is not None:
            _exact(f, "fraction")

    def to_canonical(self) -> dict:
        return {"alloc_id": self.alloc_id, "kind": self.kind, "basis": self.basis, "parent": self.parent,
                "child": self.child, "fraction": _frac_out(self.fraction)}


@dataclass(frozen=True)
class EngineEvent:
    """One engine event. ``order`` is the producer's (step_index, ordinal) order key."""
    event_id: str
    order: tuple[int, int]
    revision: int = 0
    kind: str = "UNSPECIFIED"
    consumes: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    discards: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    produced_types: tuple[tuple[str, str], ...] = ()
    allocations: tuple[Allocation, ...] = ()
    quantities: tuple[QuantityTerm, ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()
    claim_route: str = "INFERRED_RULE"
    trajectory: str = "PLANNED"
    source_ref: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.event_id, "event_id")
        _nonblank(self.kind, "event kind")
        if not (isinstance(self.order, tuple) and len(self.order) == 2 and all(type(x) is int for x in self.order)):
            raise EventLogError("order must be a (step_index, ordinal) tuple of two ints")
        if type(self.revision) is not int or self.revision < 0:
            raise EventLogError("revision must be a non-negative int")
        for name in ("consumes", "produces", "discards", "depends_on"):
            _ids(getattr(self, name), name)
        object.__setattr__(self, "produced_types", _pairs(self.produced_types, "produced_types"))
        object.__setattr__(self, "attributes", _pairs(self.attributes, "attributes"))
        if not {k for k, _ in self.produced_types} <= set(self.produces):
            raise EventLogError("produced_types may only type entities listed in produces")
        for name, cls in (("allocations", Allocation), ("quantities", QuantityTerm)):
            items = getattr(self, name)
            if not (isinstance(items, tuple) and all(isinstance(x, cls) for x in items)):
                raise EventLogError(f"{name} must be a tuple of {cls.__name__}")
        if self.claim_route not in CLAIM_ROUTES:
            raise EventLogError(f"claim_route must be one of {tuple(CLAIM_ROUTES)}")
        if self.trajectory not in TRAJECTORIES:
            raise EventLogError(f"trajectory must be one of {TRAJECTORIES}")
        if self.source_ref is not None:
            _nonblank(self.source_ref, "source_ref")

    def to_canonical(self) -> dict:
        return {"schema_version": EVENT_SCHEMA_VERSION, "event_id": self.event_id, "revision": self.revision,
                "order": list(self.order), "kind": self.kind, "consumes": list(self.consumes),
                "produces": list(self.produces), "discards": list(self.discards),
                "depends_on": list(self.depends_on), "produced_types": dict(self.produced_types),
                "allocations": [a.to_canonical() for a in self.allocations],
                "quantities": [q.to_canonical() for q in self.quantities],
                "attributes": dict(self.attributes), "claim_route": self.claim_route,
                "trajectory": self.trajectory, "source_ref": self.source_ref}

    @classmethod
    def from_canonical(cls, d: Mapping[str, Any]) -> "EngineEvent":
        if d.get("schema_version") != EVENT_SCHEMA_VERSION:
            raise EventLogError("unknown engine event schema_version")
        try:
            return cls(
                event_id=d["event_id"], order=tuple(d["order"]), revision=d["revision"], kind=d["kind"],
                consumes=tuple(d["consumes"]), produces=tuple(d["produces"]), discards=tuple(d["discards"]),
                depends_on=tuple(d["depends_on"]), produced_types=tuple(d["produced_types"].items()),
                allocations=tuple(Allocation(a["alloc_id"], a["kind"], a["basis"], a["parent"], a["child"],
                                             _frac_in(a["fraction"])) for a in d["allocations"]),
                quantities=tuple(QuantityTerm(q["entity_id"], q["dim"], Fraction(q["low"]), Fraction(q["high"]),
                                              q["ref"]) for q in d["quantities"]),
                attributes=tuple(d["attributes"].items()), claim_route=d["claim_route"],
                trajectory=d["trajectory"], source_ref=d["source_ref"])
        except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError) as exc:
            if isinstance(exc, EventLogError):
                raise
            raise EventLogError(f"malformed engine event: {exc}") from exc

    @property
    def sha256(self) -> str:
        return sha256_canonical(self.to_canonical())


# ---------------------------------------------------------------- append-only log
@dataclass(frozen=True)
class LogEntry:
    seq: int
    event: EngineEvent
    prev_sha256: str
    entry_sha256: str

    def to_canonical(self) -> dict:
        return {"log_schema_version": LOG_SCHEMA_VERSION, "seq": self.seq, "prev_sha256": self.prev_sha256,
                "entry_sha256": self.entry_sha256, "event": self.event.to_canonical()}


def _entry_hash(seq: int, prev: str, event: EngineEvent) -> str:
    return sha256_canonical({"log_schema_version": LOG_SCHEMA_VERSION, "seq": seq, "prev_sha256": prev,
                             "event": event.to_canonical()})


class EventLog:
    """In-memory append-only event log. There is no operation that removes or rewrites an entry,
    and the constructor takes no entries: every entry goes through ``append`` and the hash chain."""

    __slots__ = ("_entries", "_last_revision")

    def __init__(self) -> None:
        self._entries: list[LogEntry] = []
        self._last_revision: dict[str, int] = {}

    def append(self, event: EngineEvent) -> LogEntry:
        if not isinstance(event, EngineEvent):
            raise EventLogError("only EngineEvent instances can be appended")
        last = self._last_revision.get(event.event_id)
        expected = 0 if last is None else last + 1
        if event.revision != expected:
            code = "DUPLICATE_EVENT_REVISION" if last is not None and event.revision <= last else "REVISION_GAP"
            raise EventLogError(f"{code}: {event.event_id} needs revision {expected}, got {event.revision}")
        seq = len(self._entries)
        prev = self.head_sha256
        entry = LogEntry(seq, event, prev, _entry_hash(seq, prev, event))
        self._entries.append(entry)
        self._last_revision[event.event_id] = event.revision
        return entry

    @property
    def entries(self) -> tuple[LogEntry, ...]:
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def head_sha256(self) -> str:
        return self._entries[-1].entry_sha256 if self._entries else GENESIS_SHA256

    def effective(self) -> tuple[EngineEvent, ...]:
        """Latest revision of each event, at the log position where the event first appeared."""
        first: dict[str, int] = {}
        latest: dict[str, EngineEvent] = {}
        for entry in self._entries:
            first.setdefault(entry.event.event_id, entry.seq)
            latest[entry.event.event_id] = entry.event
        return tuple(latest[eid] for eid in sorted(first, key=first.__getitem__))

    def to_jsonl(self) -> str:
        return "".join(canonical_json(e.to_canonical()) + "\n" for e in self._entries)

    @classmethod
    def from_jsonl(cls, text: str) -> "EventLog":
        """Rebuild a log, refusing non-canonical lines, a broken hash chain or bad revisions."""
        log = cls()
        if text and not text.endswith("\n"):
            raise EventLogError("JSONL log must end with a newline")
        for n, line in enumerate(text.splitlines()):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EventLogError(f"line {n}: not JSON") from exc
            if canonical_json(rec) != line:
                raise EventLogError(f"line {n}: not canonical JSON")
            if rec.get("log_schema_version") != LOG_SCHEMA_VERSION:
                raise EventLogError(f"line {n}: unknown log schema version")
            entry = log.append(EngineEvent.from_canonical(rec.get("event") or {}))
            if (rec.get("seq"), rec.get("prev_sha256"), rec.get("entry_sha256")) != \
                    (entry.seq, entry.prev_sha256, entry.entry_sha256):
                raise EventLogError(f"line {n}: hash chain mismatch (log was edited or truncated)")
        return log


# ---------------------------------------------------------------- JSONL writers
def guard_output_path(path: Path | str, *, root: Path = ROOT) -> Path:
    """Resolve ``path`` and refuse protected areas and ledger file names."""
    target = Path(path).resolve()
    if target.name.upper() in LEDGER_FILE_NAMES:
        raise EventLogError("refusing to write a file named like an EVT/ENTITY/STATE/ALLOC/REF/GRAPH/INST ledger")
    try:
        parts = target.relative_to(Path(root).resolve()).parts
    except ValueError:
        parts = ()
    if any(parts[:len(p)] == p for p in PROTECTED_PREFIXES):
        raise EventLogError("refusing to write inside ledgers/, data/, exports/ or annotation/gold/")
    return target


def _write_new(text: str, path: Path | str, root: Path) -> Path:
    target = guard_output_path(path, root=root)
    if target.exists():
        raise EventLogError("refusing to overwrite an existing file")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return target


def write_log_jsonl(log: EventLog, path: Path | str, *, root: Path = ROOT) -> Path:
    """Write the whole log to a new JSONL file (never overwrites)."""
    return _write_new(log.to_jsonl(), path, root)


def write_canonical_jsonl(records: Iterable[Any], path: Path | str, *, root: Path = ROOT) -> Path:
    """Write canonical JSON lines (e.g. replay transactions) to a new file (never overwrites)."""
    return _write_new("".join(canonical_json(r) + "\n" for r in records), path, root)


def extend_log_jsonl(log: EventLog, path: Path | str, *, root: Path = ROOT) -> int:
    """Append the log's new entries to an existing file whose bytes are a prefix of the log."""
    target = guard_output_path(path, root=root)
    if not target.is_file():
        raise EventLogError("nothing to extend: file does not exist (use write_log_jsonl)")
    existing = target.read_bytes()
    full = log.to_jsonl().encode("utf-8")
    if not full.startswith(existing) or (existing and not existing.endswith(b"\n")):
        raise EventLogError("refusing to extend: file is not a prefix of this log (would rewrite history)")
    tail = full[len(existing):]
    with open(target, "ab") as fh:
        fh.write(tail)
    return tail.count(b"\n")
