"""Step 18b/18c deterministic event-sourcing replay with hard invariants (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c. Hard gate 16c is open, so this is an engineering contract
draft. It reads and writes no ledger; the snapshot and transaction shapes are not the
EVT / ENTITY / STATE ledger schema.

Plan Step 18 method, as implemented here:
(1) one append-only transaction per event = input snapshot hash + event revision +
    output entity versions + quantity changes + issues + config hash (plus ids, status,
    undecided items, mass-balance records and the output snapshot hash); identical
    replay gives an identical snapshot hash and byte-identical JSONL.
(2) invariants are hard validators: an event with any issue is REJECTED and changes
    nothing (no partial application, no clamping). Checked: order regression,
    dependencies, nothing consumed before it is produced or after DISCARD / consumption,
    ids never reused, allocation parent / child roles, split fractions <= 1 per basis,
    quantity terms only for produced entities, mass balance, trajectory, and (in
    ``EXPLICIT_ONLY`` scope) inferred events never feeding explicit-only results.
(3) issue codes (``ISSUE_CODES``) and undecided codes (``UNKNOWN_CODES``), never a silent fix.
(4) quantities are exact linear terms over traced bases (QNT ref, dim, low, high), so
    split children stay correlated: two halves of 100-120 g recombine to exactly that base.

Quantity policy (R-20, "no invented grams"): an amount enters only as a traced
``QuantityTerm``. The engine derives amounts only by exact allocation algebra: a known
exact fraction on a MASS / VOLUME / COUNT basis matching the parent's single dimension,
and a REMAINDER as parent minus its known siblings. Transforms and merges propagate
nothing (a process may change mass; whether a pure combine conserves it is OPEN), and
units are never converted. Mass balance is checked per allocation parent only when
every term is known in one dimension; otherwise it is UNKNOWN, not FAIL, except that
known outputs already exceeding the input are a FAIL.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping

from .event_log import (
    BASIS_DIM, ROOT, TRAJECTORIES, Allocation, EngineEvent, EventLog, EventLogError, QuantityTerm, canonical_json,
    sha256_canonical, write_canonical_jsonl,
)

STATUS = "DRAFT_PENDING_16c"
ENGINE_VERSION = "step18-replay-0.1.0-draft"
SNAPSHOT_SCHEMA_VERSION = "step18-snapshot-0.1.0-draft"
SCOPES = ("ALL", "EXPLICIT_ONLY")
PARTITION_KINDS = frozenset({"SPLIT", "RESERVE", "REMAINDER", "DISCARD"})
LIFECYCLE_BY_TYPE = {"RESERVED_PORTION": "RESERVED", "DISCARDED_PORTION": "DISCARDED"}
LOT_EXPECTED_LIFECYCLE = {"USED": frozenset({"INCORPORATED"}), "DISCARDED": frozenset({"DISCARDED"}),
                          "APPARENTLY_UNUSED": frozenset({"ACTIVE", "RESERVED"})}

ISSUE_CODES = frozenset({
    "ORDER_REGRESSION", "DEPENDENCY_NOT_APPLIED", "INFERRED_DEPENDENCY_IN_EXPLICIT_SCOPE", "TRAJECTORY_MISMATCH",
    "ENTITY_ROLE_CONFLICT", "ENTITY_UNKNOWN", "ENTITY_REUSED_AFTER_DISCARD", "ENTITY_ALREADY_CONSUMED",
    "ENTITY_ID_REUSED", "ALLOC_PARENT_NOT_CONSUMED", "ALLOC_CHILD_NOT_PRODUCED", "SPLIT_FRACTIONS_EXCEED_ONE",
    "QUANTITY_FOR_UNPRODUCED_ENTITY", "QUANTITY_CONFLICT", "MASS_BALANCE_FAIL", "LOT_STATUS_CONTRADICTS_REPLAY",
    "LOT_NOT_IN_REPLAY",
})
UNKNOWN_CODES = frozenset({
    "FRACTION_BASIS_UNSPECIFIED", "FRACTION_UNKNOWN", "FRACTION_INTERVAL_UNDECIDED", "FRACTION_INTERVAL_INVERTED",
    "NEGATIVE_FRACTION_RULE_OPEN", "MASS_BALANCE_UNKNOWN",
})
QUANTITY_REASONS = frozenset({
    "NOT_PROPAGATED", "MULTIPLE_ALLOCATIONS", "PARENT_QUANTITY_UNKNOWN", "FRACTION_UNKNOWN",
    "FRACTION_BASIS_UNSPECIFIED", "FRACTION_INTERVAL_NOT_PROPAGATED", "FRACTION_OUT_OF_RANGE",
    "BASIS_DIMENSION_MISMATCH", "MULTIPLE_REMAINDERS", "SIBLING_QUANTITY_UNKNOWN",
})
NOT_CHECKED = ("SPAN_ROUNDTRIP_SEE_V1", "LOT_ACCOUNTING_COMPLETENESS_SEE_V4", "INVENTED_VALUES_SEE_ADAPTER_AUDIT",
               "MERGE_AND_TRANSFORM_QUANTITIES_NOT_PROPAGATED", "OBSERVATION_OVERRIDE_NOT_IMPLEMENTED",
               "TRANSITION_TUPLES_AND_PREFIX_PACKETS_NOT_IMPLEMENTED")

Base = tuple[str, str, Fraction, Fraction]  # (QNT ref, dim, low, high)


def _fs(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


# ---------------------------------------------------------------- exact linear quantities
@dataclass(frozen=True)
class Quantity:
    """Exact sum of coef x base terms; bases are traced measurements and are never converted."""
    terms: tuple[tuple[Fraction, Base], ...]

    @staticmethod
    def _norm(terms: Iterable[tuple[Fraction, Base]]) -> "Quantity":
        acc: dict[Base, Fraction] = {}
        for c, b in terms:
            acc[b] = acc.get(b, Fraction(0)) + c
        return Quantity(tuple((acc[b], b) for b in sorted(acc) if acc[b] != 0))

    @classmethod
    def of(cls, term: QuantityTerm) -> "Quantity":
        return cls(((Fraction(1), (term.ref, term.dim, term.low, term.high)),))

    @classmethod
    def zero(cls) -> "Quantity":
        return cls(())

    def scale(self, k: Fraction) -> "Quantity":
        if type(k) is not Fraction:
            raise EventLogError("quantities scale by exact Fractions only")
        return Quantity._norm((c * k, b) for c, b in self.terms)

    def plus(self, other: "Quantity") -> "Quantity":
        return Quantity._norm(self.terms + other.terms)

    def minus(self, other: "Quantity") -> "Quantity":
        return self.plus(other.scale(Fraction(-1)))

    @property
    def dims(self) -> tuple[str, ...]:
        return tuple(sorted({b[1] for _, b in self.terms}))

    def bounds(self) -> tuple[str | None, Fraction, Fraction] | None:
        """(dim, low, high) exactly; ``None`` when terms span several dimensions."""
        if not self.terms:
            return (None, Fraction(0), Fraction(0))
        if len(self.dims) != 1:
            return None
        lo = sum((c * (b[2] if c > 0 else b[3]) for c, b in self.terms), Fraction(0))
        hi = sum((c * (b[3] if c > 0 else b[2]) for c, b in self.terms), Fraction(0))
        return (self.dims[0], lo, hi)

    def to_canonical(self) -> dict:
        b = self.bounds()
        return {"terms": [{"coef": _fs(c), "ref": r, "dim": d, "low": _fs(lo), "high": _fs(hi)}
                          for c, (r, d, lo, hi) in self.terms],
                "bounds": None if b is None else {"dim": b[0], "low": _fs(b[1]), "high": _fs(b[2])}}


def _sum(qs: Iterable[Quantity]) -> Quantity:
    out = Quantity.zero()
    for q in qs:
        out = out.plus(q)
    return out


# ---------------------------------------------------------------- snapshot
@dataclass(frozen=True)
class EntityVersion:
    entity_id: str
    version: int
    lifecycle: str
    entity_type: str
    event_id: str
    event_revision: int
    claim_route: str
    trajectory: str
    parents: tuple[str, ...]
    quantity: Quantity | None
    quantity_reason: str | None

    def to_canonical(self) -> dict:
        return {"entity_id": self.entity_id, "version": self.version, "lifecycle": self.lifecycle,
                "entity_type": self.entity_type, "event_id": self.event_id, "event_revision": self.event_revision,
                "claim_route": self.claim_route, "trajectory": self.trajectory, "parents": list(self.parents),
                "quantity": None if self.quantity is None else self.quantity.to_canonical(),
                "quantity_reason": self.quantity_reason}


@dataclass(frozen=True)
class Snapshot:
    """Entity version histories (append-only) and the applied (event_id, revision) sequence."""
    entities: tuple[tuple[str, tuple[EntityVersion, ...]], ...]
    applied: tuple[tuple[str, int], ...]

    def entity_ids(self) -> tuple[str, ...]:
        return tuple(k for k, _ in self.entities)

    def versions(self, entity_id: str) -> tuple[EntityVersion, ...]:
        return dict(self.entities)[entity_id]

    def current(self, entity_id: str) -> EntityVersion:
        return self.versions(entity_id)[-1]

    def to_canonical(self) -> dict:
        return {"schema_version": SNAPSHOT_SCHEMA_VERSION,
                "entities": {k: [v.to_canonical() for v in vs] for k, vs in self.entities},
                "applied": [[e, r] for e, r in self.applied]}

    @property
    def sha256(self) -> str:
        return sha256_canonical(self.to_canonical())


def empty_snapshot() -> Snapshot:
    return Snapshot((), ())


# ---------------------------------------------------------------- config / records
@dataclass(frozen=True)
class ReplayConfig:
    trajectory: str = "PLANNED"
    scope: str = "ALL"
    engine_version: str = ENGINE_VERSION

    def __post_init__(self) -> None:
        if self.trajectory not in TRAJECTORIES:
            raise EventLogError(f"trajectory must be one of {TRAJECTORIES}")
        if self.scope not in SCOPES:
            raise EventLogError(f"scope must be one of {SCOPES}")

    def to_canonical(self) -> dict:
        return {"trajectory": self.trajectory, "scope": self.scope, "engine_version": self.engine_version,
                "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION}

    @property
    def config_sha256(self) -> str:
        return sha256_canonical(self.to_canonical())


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    event_id: str | None = None

    def to_canonical(self) -> dict:
        return {"code": self.code, "path": self.path, "event_id": self.event_id}


@dataclass(frozen=True)
class Transaction:
    seq: int
    event_id: str
    event_revision: int
    event_sha256: str
    input_snapshot_sha256: str
    output_entity_versions: tuple[EntityVersion, ...]
    quantity_changes: tuple[dict, ...]
    issues: tuple[Issue, ...]
    unknown: tuple[Issue, ...]
    mass_balance: tuple[dict, ...]
    config_sha256: str
    status: str  # APPLIED | REJECTED | SKIPPED_SCOPE
    output_snapshot_sha256: str

    def to_canonical(self) -> dict:
        return {"seq": self.seq, "event_id": self.event_id, "event_revision": self.event_revision,
                "event_sha256": self.event_sha256, "input_snapshot_sha256": self.input_snapshot_sha256,
                "output_entity_versions": [v.to_canonical() for v in self.output_entity_versions],
                "quantity_changes": [dict(c) for c in self.quantity_changes],
                "issues": [i.to_canonical() for i in self.issues],
                "unknown": [i.to_canonical() for i in self.unknown],
                "mass_balance": [dict(m) for m in self.mass_balance], "config_sha256": self.config_sha256,
                "status": self.status, "output_snapshot_sha256": self.output_snapshot_sha256}


@dataclass(frozen=True)
class ReplayResult:
    config: ReplayConfig
    transactions: tuple[Transaction, ...]
    snapshot: Snapshot
    final_issues: tuple[Issue, ...]
    not_checked: tuple[str, ...]

    @property
    def issues(self) -> tuple[Issue, ...]:
        return tuple(i for t in self.transactions for i in t.issues) + self.final_issues

    @property
    def unknown(self) -> tuple[Issue, ...]:
        return tuple(i for t in self.transactions for i in t.unknown)

    @property
    def status(self) -> str:
        if self.issues:
            return "FAIL"
        return "UNKNOWN" if self.unknown else "PASS"

    @property
    def snapshot_sha256(self) -> str:
        return self.snapshot.sha256

    def records(self) -> list[dict]:
        head = {"record": "REPLAY_HEADER", "draft_status": STATUS, "engine_version": self.config.engine_version,
                "config": self.config.to_canonical(), "config_sha256": self.config.config_sha256}
        statuses: dict[str, int] = {}
        for t in self.transactions:
            statuses[t.status] = statuses.get(t.status, 0) + 1
        tail = {"record": "REPLAY_RESULT", "replay_status": self.status, "snapshot_sha256": self.snapshot_sha256,
                "snapshot": self.snapshot.to_canonical(), "final_issues": [i.to_canonical() for i in self.final_issues],
                "not_checked": list(self.not_checked),
                "counts": {"transactions": len(self.transactions), "by_status": statuses,
                           "issues": len(self.issues), "unknown": len(self.unknown)}}
        return [head, *({"record": "TRANSACTION", **t.to_canonical()} for t in self.transactions), tail]

    def to_jsonl(self) -> str:
        return "".join(canonical_json(r) + "\n" for r in self.records())

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_jsonl().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- engine
@dataclass(frozen=True)
class _Derived:
    quantity: Quantity | None
    reason: str | None
    remainder: bool = False


class _Run:
    def __init__(self, config: ReplayConfig) -> None:
        self.config = config
        self.cfg = config.config_sha256
        self.state: dict[str, list[EntityVersion]] = {}
        self.applied: list[tuple[str, int]] = []
        self.applied_ids: set[str] = set()
        self.skipped_ids: set[str] = set()
        self.skipped_entities: set[str] = set()
        self.max_order: tuple[int, int] | None = None
        self.snap_sha = empty_snapshot().sha256

    def snapshot(self) -> Snapshot:
        return Snapshot(tuple((k, tuple(self.state[k])) for k in sorted(self.state)), tuple(self.applied))

    def _qty(self, entity_id: str) -> Quantity | None:
        vs = self.state.get(entity_id)
        return vs[-1].quantity if vs else None

    def step(self, seq: int, ev: EngineEvent) -> Transaction:
        issues: list[Issue] = []
        unknown: list[Issue] = []

        def fail(code: str, path: str) -> None:
            issues.append(Issue(code, path, ev.event_id))

        def undecided(code: str, path: str) -> None:
            unknown.append(Issue(code, path, ev.event_id))

        def tx(status: str, versions: tuple = (), changes: tuple = (), mb: tuple = ()) -> Transaction:
            return Transaction(seq, ev.event_id, ev.revision, ev.sha256, input_sha, versions, changes,
                               tuple(issues), tuple(unknown), mb, self.cfg, status, self.snap_sha)

        input_sha = self.snap_sha
        regression = self.max_order is not None and ev.order < self.max_order
        self.max_order = ev.order if self.max_order is None else max(self.max_order, ev.order)
        if self.config.scope == "EXPLICIT_ONLY" and ev.claim_route != "EXPLICIT":
            self.skipped_ids.add(ev.event_id)
            self.skipped_entities.update(ev.produces)
            return tx("SKIPPED_SCOPE")
        if ev.trajectory != self.config.trajectory:
            fail("TRAJECTORY_MISMATCH", "trajectory")
        if regression:
            fail("ORDER_REGRESSION", f"order/{ev.order[0]}/{ev.order[1]}")
        for dep in ev.depends_on:
            if dep not in self.applied_ids:
                fail("INFERRED_DEPENDENCY_IN_EXPLICIT_SCOPE" if dep in self.skipped_ids else "DEPENDENCY_NOT_APPLIED",
                     f"depends_on/{dep}")
        self._roles(ev, fail)
        terms = self._quantity_terms(ev, fail)
        self._fractions(ev, fail, undecided)
        mb: tuple = ()
        derived: dict[str, _Derived] = {}
        if not issues:
            derived = self._derive(ev, terms)
            mb = self._mass_balance(ev, derived, fail, undecided)
        if issues:
            return tx("REJECTED", mb=mb)
        versions, changes = self._apply(ev, derived)
        self.snap_sha = self.snapshot().sha256
        return tx("APPLIED", versions, changes, mb)

    # ------------------------------------------------------------ checks
    def _roles(self, ev: EngineEvent, fail: Any) -> None:
        for role in ("consumes", "produces", "discards"):
            seen: set[str] = set()
            for x in getattr(ev, role):
                if x in seen:
                    fail("ENTITY_ROLE_CONFLICT", f"{role}/{x}")
                seen.add(x)
        for x in sorted(set(ev.consumes) & set(ev.discards)):
            fail("ENTITY_ROLE_CONFLICT", f"consumes+discards/{x}")
        for role in ("consumes", "discards"):
            for x in dict.fromkeys(getattr(ev, role)):
                vs = self.state.get(x)
                if vs is None:
                    fail("INFERRED_DEPENDENCY_IN_EXPLICIT_SCOPE" if x in self.skipped_entities else "ENTITY_UNKNOWN",
                         f"{role}/{x}")
                elif vs[-1].lifecycle == "DISCARDED":
                    fail("ENTITY_REUSED_AFTER_DISCARD", f"{role}/{x}")
                elif vs[-1].lifecycle == "INCORPORATED":
                    fail("ENTITY_ALREADY_CONSUMED", f"{role}/{x}")
        for x in dict.fromkeys(ev.produces):
            if x in self.state or x in self.skipped_entities:
                fail("ENTITY_ID_REUSED", f"produces/{x}")
        consumed, produced = set(ev.consumes), set(ev.produces)
        for a in ev.allocations:
            if a.parent not in consumed:
                fail("ALLOC_PARENT_NOT_CONSUMED", f"allocations/{a.alloc_id}/parent/{a.parent}")
            if a.child not in produced:
                fail("ALLOC_CHILD_NOT_PRODUCED", f"allocations/{a.alloc_id}/child/{a.child}")

    def _quantity_terms(self, ev: EngineEvent, fail: Any) -> dict[str, QuantityTerm]:
        by: dict[str, list[QuantityTerm]] = {}
        for q in ev.quantities:
            if q.entity_id not in ev.produces:
                fail("QUANTITY_FOR_UNPRODUCED_ENTITY", f"quantities/{q.entity_id}")
            by.setdefault(q.entity_id, []).append(q)
        for k, v in by.items():
            if len(v) > 1:
                fail("QUANTITY_CONFLICT", f"quantities/{k}")
        return {k: v[0] for k, v in by.items()}

    def _fractions(self, ev: EngineEvent, fail: Any, undecided: Any) -> None:
        groups: dict[tuple[str, str], list[Allocation]] = {}
        for a in ev.allocations:
            if a.kind in PARTITION_KINDS:
                groups.setdefault((a.parent, a.basis), []).append(a)
        for (parent, basis), allocs in groups.items():
            path = f"fractions/{parent}/{basis}"
            if basis == "UNSPECIFIED":
                undecided("FRACTION_BASIS_UNSPECIFIED", path)
                continue
            lo_sum = hi_sum = Fraction(0)
            missing = negative = inverted = False
            for a in allocs:
                f = a.fraction
                if f is None:
                    missing = missing or a.kind != "REMAINDER"   # a remainder without a fraction is "the rest"
                    continue
                lo, hi = f if isinstance(f, tuple) else (f, f)
                if lo > hi:
                    inverted = True
                elif lo < 0:
                    negative = True
                else:
                    lo_sum, hi_sum = lo_sum + lo, hi_sum + hi
            if negative:
                undecided("NEGATIVE_FRACTION_RULE_OPEN", path)
            elif lo_sum > 1:                                       # unknown shares are >= 0: still over one
                fail("SPLIT_FRACTIONS_EXCEED_ONE", path)
            elif inverted:
                undecided("FRACTION_INTERVAL_INVERTED", path)
            elif missing:
                undecided("FRACTION_UNKNOWN", path)
            elif hi_sum > 1:
                undecided("FRACTION_INTERVAL_UNDECIDED", path)

    # ------------------------------------------------------------ quantities
    def _scaled(self, a: Allocation) -> _Derived:
        parent = self._qty(a.parent)
        if parent is None:
            return _Derived(None, "PARENT_QUANTITY_UNKNOWN")
        if a.fraction is None:
            return _Derived(None, "FRACTION_UNKNOWN")
        if a.basis == "UNSPECIFIED":
            return _Derived(None, "FRACTION_BASIS_UNSPECIFIED")
        if isinstance(a.fraction, tuple):
            return _Derived(None, "FRACTION_INTERVAL_NOT_PROPAGATED")
        if not 0 <= a.fraction <= 1:
            return _Derived(None, "FRACTION_OUT_OF_RANGE")
        b = parent.bounds()
        if b is None or b[0] != BASIS_DIM[a.basis]:
            return _Derived(None, "BASIS_DIMENSION_MISMATCH")
        return _Derived(parent.scale(a.fraction), None)

    def _derive(self, ev: EngineEvent, terms: Mapping[str, QuantityTerm]) -> dict[str, _Derived]:
        by_child: dict[str, list[Allocation]] = {}
        for a in ev.allocations:
            by_child.setdefault(a.child, []).append(a)
        out: dict[str, _Derived] = {}
        pending: dict[str, Allocation] = {}
        for c in dict.fromkeys(ev.produces):
            allocs = by_child.get(c, [])
            if c in terms:
                out[c] = _Derived(Quantity.of(terms[c]), None)
            elif not allocs:
                out[c] = _Derived(None, "NOT_PROPAGATED")
            elif len(allocs) > 1:
                out[c] = _Derived(None, "MULTIPLE_ALLOCATIONS")
            elif allocs[0].kind == "RECOMBINE":
                out[c] = _Derived(None, "NOT_PROPAGATED")
            elif allocs[0].kind == "REMAINDER" and allocs[0].fraction is None:
                pending[c] = allocs[0]
            else:
                out[c] = self._scaled(allocs[0])
        for c, a in pending.items():
            parent = self._qty(a.parent)
            sibs = [s.child for s in ev.allocations if s.parent == a.parent and s.kind in PARTITION_KINDS
                    and s.child != c]
            if parent is None:
                out[c] = _Derived(None, "PARENT_QUANTITY_UNKNOWN")
            elif any(s in pending for s in sibs):
                out[c] = _Derived(None, "MULTIPLE_REMAINDERS")
            elif any(out[s].quantity is None for s in sibs):
                out[c] = _Derived(None, "SIBLING_QUANTITY_UNKNOWN")
            else:
                out[c] = _Derived(parent.minus(_sum(out[s].quantity for s in sibs)), None, remainder=True)
        return {c: out[c] for c in dict.fromkeys(ev.produces)}

    def _mass_balance(self, ev: EngineEvent, derived: Mapping[str, _Derived], fail: Any,
                      undecided: Any) -> tuple[dict, ...]:
        records = []
        parents = dict.fromkeys(a.parent for a in ev.allocations if a.kind in PARTITION_KINDS)
        for p in parents:
            children = dict.fromkeys(a.child for a in ev.allocations if a.parent == p and a.kind in PARTITION_KINDS)
            status, reason = self._balance(self._qty(p), [derived[c] for c in children])
            records.append({"parent": p, "status": status, "reason": reason})
            if status == "FAIL":
                fail("MASS_BALANCE_FAIL", f"mass_balance/{p}")
            elif status == "UNKNOWN":
                undecided("MASS_BALANCE_UNKNOWN", f"mass_balance/{p}/{reason}")
        return tuple(records)

    @staticmethod
    def _balance(parent: Quantity | None, children: list[_Derived]) -> tuple[str, str | None]:
        outs = [d for d in children if not d.remainder]
        has_rem = any(d.remainder for d in children)
        known = [d.quantity for d in outs if d.quantity is not None]
        dims = {x for q in ([parent] if parent is not None else []) + known for x in q.dims}
        if len(dims) > 1:
            return "UNKNOWN", "DIMENSION_MIXED"
        if parent is None or len(known) < len(outs):
            if parent is not None and known:
                out_lo = sum((q.bounds()[1] for q in known), Fraction(0))
                if out_lo > parent.bounds()[2]:
                    return "FAIL", "OUTPUTS_EXCEED_INPUT"
            return "UNKNOWN", "TERM_UNKNOWN"
        _, lo, hi = parent.minus(_sum(known)).bounds()
        if hi < 0:
            return "FAIL", "OUTPUTS_EXCEED_INPUT"
        if has_rem:
            return ("PASS", None) if lo >= 0 else ("UNKNOWN", "INTERVALS_OVERLAP")
        if lo == hi == 0:
            return "PASS", None
        return ("UNKNOWN", "PARTITION_INCOMPLETE") if lo > 0 else ("UNKNOWN", "INTERVALS_OVERLAP")

    # ------------------------------------------------------------ apply
    def _apply(self, ev: EngineEvent, derived: Mapping[str, _Derived]) -> tuple[tuple, tuple]:
        versions: list[EntityVersion] = []
        changes: list[dict] = []
        for role, life in (("consumes", "INCORPORATED"), ("discards", "DISCARDED")):
            for x in dict.fromkeys(getattr(ev, role)):
                prev = self.state[x][-1]
                v = replace(prev, version=prev.version + 1, lifecycle=life, event_id=ev.event_id,
                            event_revision=ev.revision, claim_route=ev.claim_route, trajectory=ev.trajectory)
                self.state[x].append(v)
                versions.append(v)
        types = dict(ev.produced_types)
        discard_children = {a.child for a in ev.allocations if a.kind == "DISCARD"}
        for c in dict.fromkeys(ev.produces):
            etype = types.get(c, "UNSPECIFIED")
            life = "DISCARDED" if c in discard_children else LIFECYCLE_BY_TYPE.get(etype, "ACTIVE")
            parents = tuple(dict.fromkeys(a.parent for a in ev.allocations if a.child == c)) \
                or tuple(dict.fromkeys(ev.consumes))
            d = derived[c]
            v = EntityVersion(c, 0, life, etype, ev.event_id, ev.revision, ev.claim_route, ev.trajectory, parents,
                              d.quantity, d.reason)
            self.state[c] = [v]
            versions.append(v)
            changes.append({"entity_id": c, "version": 0, "before": None,
                            "after": None if d.quantity is None else d.quantity.to_canonical(), "reason": d.reason})
        self.applied.append((ev.event_id, ev.revision))
        self.applied_ids.add(ev.event_id)
        return tuple(versions), tuple(changes)

    def lots(self, lot_accounting: Mapping[str, str] | None, not_checked: list[str]) -> tuple[Issue, ...]:
        out = []
        for lot in sorted(lot_accounting or {}):
            if lot not in self.state:
                if lot in self.skipped_entities:
                    if "LOT_ACCOUNTING_PARTIAL_IN_SCOPE" not in not_checked:
                        not_checked.append("LOT_ACCOUNTING_PARTIAL_IN_SCOPE")
                    continue
                out.append(Issue("LOT_NOT_IN_REPLAY", lot))
                continue
            expected = LOT_EXPECTED_LIFECYCLE.get(lot_accounting[lot])  # type: ignore[index]
            if expected is not None and self.state[lot][-1].lifecycle not in expected:
                out.append(Issue("LOT_STATUS_CONTRADICTS_REPLAY", lot))
        return tuple(out)


def replay_events(events: Iterable[EngineEvent], config: ReplayConfig | None = None, *,
                  lot_accounting: Mapping[str, str] | None = None) -> ReplayResult:
    """Replay events in the given order (never re-sorted: a shuffled input must show issues)."""
    config = config or ReplayConfig()
    run = _Run(config)
    txs = []
    for seq, ev in enumerate(events):
        if not isinstance(ev, EngineEvent):
            raise EventLogError("replay takes EngineEvent instances")
        txs.append(run.step(seq, ev))
    not_checked = list(NOT_CHECKED)
    final = run.lots(lot_accounting, not_checked)
    return ReplayResult(config, tuple(txs), run.snapshot(), final, tuple(not_checked))


def replay_log(log: EventLog, config: ReplayConfig | None = None, *,
               lot_accounting: Mapping[str, str] | None = None) -> ReplayResult:
    """Replay the effective view of an append-only log (latest revision of each event)."""
    return replay_events(log.effective(), config, lot_accounting=lot_accounting)


def write_replay_jsonl(result: ReplayResult, path: Path | str, *, root: Path = ROOT) -> Path:
    """Write the replay JSONL to a new file outside protected areas (never overwrites)."""
    return write_canonical_jsonl(result.records(), path, root=root)
