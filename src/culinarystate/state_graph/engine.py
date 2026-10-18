"""Event-sourced recipe/session state engine (DEL-3; SSOT §233; plan AN1–AN4).

Identity layers (never collapsed):
  concept  = ING- id (what food it is)
  entity   = a physical lot/intermediate in this recipe/session ("the onions", "the batter")
  version  = an entity's state at a point in the event log (append-only)

`replay(events)` is a pure function: same events -> same graph -> same sha256. Nothing is mutated;
each event produces new versions/edges. Observations override the current belief for that field but
the superseded belief is kept in the audit log. Omitted-step candidates are stored, never applied
unless an AcceptCandidate event exists.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from fractions import Fraction
from typing import Union

from .symqty import Base, SymQty

TRAJECTORIES = ("PLANNED", "OBSERVED_SESSION", "PREDICTED")


# ------------------------------------------------------------------ events
@dataclass(frozen=True)
class Add:
    label: str
    concept_id: str | None
    qty: Base
    form: str | None = None
    step: int = 0


@dataclass(frozen=True)
class Transform:            # chop, fry, whisk… same entity, new version
    target: str
    process: str
    condition: dict = field(default_factory=dict)
    sets: tuple[tuple[str, str], ...] = ()    # field -> value (e.g. ("form","chopped"))
    step: int = 0


@dataclass(frozen=True)
class Merge:                # inputs consumed -> new intermediate entity
    inputs: tuple[str, ...]
    output: str
    process: str = "combine"
    step: int = 0


@dataclass(frozen=True)
class Split:                # one entity -> several, by fraction (Fraction) or qualitative share (None)
    source: str
    outputs: tuple[tuple[str, Fraction | None], ...]
    step: int = 0


@dataclass(frozen=True)
class Reserve:              # take a portion aside; remainder stays as new version of source
    source: str
    output: str
    portion: Base | None = None          # absolute amount, or
    fraction: Fraction | None = None     # fraction of source
    step: int = 0


@dataclass(frozen=True)
class Discard:
    source: str
    portion: Base | None = None
    fraction: Fraction | None = None     # None and no portion = discard all
    what: str | None = None              # e.g. "cooking water"
    step: int = 0


@dataclass(frozen=True)
class Recombine:            # reserved entity goes back into target
    reserved: str
    target: str
    step: int = 0


@dataclass(frozen=True)
class Transfer:
    target: str
    location: str
    step: int = 0


@dataclass(frozen=True)
class Observe:              # user/sensor observation for one field
    target: str
    field: str
    value: str
    source: str = "user"
    step: int = 0


@dataclass(frozen=True)
class Predict:              # model/evidence prediction for one field
    target: str
    field: str
    value: str
    model_ref: str
    step: int = 0


@dataclass(frozen=True)
class OmittedStepCandidate:
    cid: str
    after_step: int
    description: str
    rationale: str
    proposed: tuple = ()                 # events to apply if accepted


@dataclass(frozen=True)
class AcceptCandidate:
    cid: str
    by: str


Event = Union[Add, Transform, Merge, Split, Reserve, Discard, Recombine, Transfer, Observe, Predict,
              OmittedStepCandidate, AcceptCandidate]


# ------------------------------------------------------------------ state
@dataclass(frozen=True)
class Belief:
    value: str
    trajectory: str
    source: str
    event_index: int


@dataclass(frozen=True)
class Version:
    entity: str
    n: int
    qty: SymQty
    fields: tuple[tuple[str, Belief], ...]
    location: str | None
    alive: bool
    event_index: int

    def get(self, name: str) -> Belief | None:
        return dict(self.fields).get(name)


@dataclass(frozen=True)
class Edge:
    src: str        # "entity@version"
    dst: str
    relation: str
    event_index: int
    detail: str = ""


@dataclass
class _Acc:                                   # private accumulator used only inside replay()
    versions: dict[str, list[Version]] = field(default_factory=dict)
    concepts: dict[str, str | None] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    audit: list[dict] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    candidates: dict[str, OmittedStepCandidate] = field(default_factory=dict)
    accepted: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Graph:
    versions: dict
    concepts: dict
    edges: tuple[Edge, ...]
    audit: tuple[dict, ...]
    issues: tuple[str, ...]
    candidates: tuple[str, ...]
    accepted: tuple[tuple[str, str], ...]

    def current(self, entity: str) -> Version:
        return self.versions[entity][-1]

    def alive(self) -> list[str]:
        return [e for e, vs in self.versions.items() if vs[-1].alive]

    def sha256(self) -> str:
        return hashlib.sha256(canonical_json(self).encode()).hexdigest()


def _ref(v: Version) -> str:
    return f"{v.entity}@{v.n}"


def _new_version(acc: _Acc, prev: Version, i: int, **changes) -> Version:
    v = replace(prev, n=prev.n + 1, event_index=i, **changes)
    acc.versions[prev.entity].append(v)
    return v


def _live(acc: _Acc, label: str, i: int) -> Version | None:
    vs = acc.versions.get(label)
    if not vs:
        acc.issues.append(f"event {i}: unknown entity '{label}'")
        return None
    if not vs[-1].alive:
        acc.issues.append(f"event {i}: entity '{label}' already consumed/discarded")
        return None
    return vs[-1]


def _set_fields(fields: tuple, updates: dict[str, Belief]) -> tuple:
    d = dict(fields)
    d.update(updates)
    return tuple(sorted(d.items()))


def _apply(acc: _Acc, i: int, ev: Event) -> None:  # noqa: C901 — one branch per event type
    if isinstance(ev, Add):
        if ev.label in acc.versions:
            acc.issues.append(f"event {i}: entity '{ev.label}' added twice")
            return
        fields = {"form": Belief(ev.form, "PLANNED", "recipe", i)} if ev.form else {}
        acc.versions[ev.label] = [Version(ev.label, 0, SymQty.of(ev.qty), tuple(sorted(fields.items())), None,
                                          True, i)]
        acc.concepts[ev.label] = ev.concept_id
    elif isinstance(ev, Transform):
        prev = _live(acc, ev.target, i)
        if prev:
            upd = {k: Belief(v, "PLANNED", f"process:{ev.process}", i) for k, v in ev.sets}
            upd["last_process"] = Belief(ev.process, "PLANNED", "recipe", i)
            v = _new_version(acc, prev, i, fields=_set_fields(prev.fields, upd))
            acc.edges.append(Edge(_ref(prev), _ref(v), "TRANSFORMS_INTO", i,
                                  json.dumps({"process": ev.process, **ev.condition}, sort_keys=True)))
    elif isinstance(ev, Merge):
        if ev.output in acc.versions:                       # never overwrite an entity's history
            acc.issues.append(f"event {i}: merge output '{ev.output}' already exists")
            return
        parents = [p for p in (_live(acc, x, i) for x in ev.inputs) if p]
        if len(parents) != len(ev.inputs):
            return
        qty = SymQty.zero()
        for p in parents:
            qty = qty.plus(p.qty)
            dead = _new_version(acc, p, i, alive=False)
            acc.edges.append(Edge(_ref(dead), f"{ev.output}@0", "MERGES_INTO", i, ev.process))
        acc.versions[ev.output] = [Version(ev.output, 0, qty, (("last_process", Belief(ev.process, "PLANNED",
                                                                                           "recipe", i)),),
                                           parents[0].location if parents else None, True, i)]
        acc.concepts[ev.output] = None
    elif isinstance(ev, Split):
        prev = _live(acc, ev.source, i)
        if not prev:
            return
        clash = [lbl for lbl, _ in ev.outputs if lbl in acc.versions]
        if clash:
            acc.issues.append(f"event {i}: split outputs already exist: {clash}")
            return
        known = [f for _, f in ev.outputs if f is not None]
        if sum(known) > 1:
            acc.issues.append(f"event {i}: split fractions sum to {sum(known)} > 1")
            return
        dead = _new_version(acc, prev, i, alive=False)
        for label, frac in ev.outputs:
            qty = prev.qty.scale(frac) if frac is not None else SymQty.of(Base.qualitative(f"share of {ev.source}"))
            acc.versions[label] = [Version(label, 0, qty, prev.fields, prev.location, True, i)]
            acc.concepts[label] = acc.concepts.get(ev.source)
            acc.edges.append(Edge(_ref(dead), f"{label}@0", "SPLITS_INTO", i, str(frac) if frac is not None
                                  else "unspecified share"))
    elif isinstance(ev, Reserve):
        prev = _live(acc, ev.source, i)
        if not prev or ev.output in acc.versions:
            if ev.output in acc.versions:
                acc.issues.append(f"event {i}: reserve output '{ev.output}' already exists")
            return
        taken = SymQty.of(ev.portion) if ev.portion else prev.qty.scale(ev.fraction or Fraction(0))
        rem = _new_version(acc, prev, i, qty=prev.qty.minus(taken))
        acc.versions[ev.output] = [Version(ev.output, 0, taken, prev.fields, prev.location, True, i)]
        acc.concepts[ev.output] = acc.concepts.get(ev.source)
        acc.edges.append(Edge(_ref(prev), f"{ev.output}@0", "RESERVED_AS", i, taken.render()))
        acc.edges.append(Edge(_ref(prev), _ref(rem), "TRANSFORMS_INTO", i, "remainder after reserve"))
    elif isinstance(ev, Discard):
        prev = _live(acc, ev.source, i)
        if not prev:
            return
        if ev.portion is None and ev.fraction is None:
            v = _new_version(acc, prev, i, alive=False)
            acc.edges.append(Edge(_ref(v), "DISCARD", "DISCARDED_FROM", i, ev.what or "all"))
        else:
            gone = SymQty.of(ev.portion) if ev.portion else prev.qty.scale(ev.fraction)
            v = _new_version(acc, prev, i, qty=prev.qty.minus(gone))
            acc.edges.append(Edge(_ref(prev), _ref(v), "DISCARDED_FROM", i, ev.what or gone.render()))
    elif isinstance(ev, Recombine):
        res, tgt = _live(acc, ev.reserved, i), _live(acc, ev.target, i)
        if res and tgt:
            dead = _new_version(acc, res, i, alive=False)
            v = _new_version(acc, tgt, i, qty=tgt.qty.plus(res.qty))
            acc.edges.append(Edge(_ref(dead), _ref(v), "RECOMBINED_WITH", i))
    elif isinstance(ev, Transfer):
        prev = _live(acc, ev.target, i)
        if prev:
            v = _new_version(acc, prev, i, location=ev.location)
            acc.edges.append(Edge(_ref(prev), _ref(v), "TRANSFERRED_TO", i, ev.location))
            acc.edges.append(Edge(_ref(v), f"LOC:{ev.location}", "LOCATED_IN", i))
    elif isinstance(ev, (Observe, Predict)):
        prev = _live(acc, ev.target, i)
        if not prev:
            return
        traj = "OBSERVED_SESSION" if isinstance(ev, Observe) else "PREDICTED"
        src = ev.source if isinstance(ev, Observe) else f"model:{ev.model_ref}"
        old = prev.get(ev.field)
        if isinstance(ev, Predict) and old and old.trajectory == "OBSERVED_SESSION":
            acc.audit.append({"event": i, "entity": ev.target, "field": ev.field, "kept": asdict(old),
                              "ignored_prediction": ev.value, "reason": "observation outranks prediction"})
            return
        if old:
            acc.audit.append({"event": i, "entity": ev.target, "field": ev.field, "superseded": asdict(old),
                              "by": traj})
        v = _new_version(acc, prev, i, fields=_set_fields(prev.fields, {ev.field: Belief(ev.value, traj, src, i)}))
        if isinstance(ev, Observe):
            acc.edges.append(Edge(_ref(prev), _ref(v), "OBSERVED_AS", i, f"{ev.field}={ev.value}"))
    elif isinstance(ev, OmittedStepCandidate):
        acc.candidates[ev.cid] = ev
    elif isinstance(ev, AcceptCandidate):
        cand = acc.candidates.get(ev.cid)
        if not cand:
            acc.issues.append(f"event {i}: accept of unknown candidate '{ev.cid}'")
            return
        acc.accepted[ev.cid] = ev.by
        for sub in cand.proposed:
            _apply(acc, i, sub)


def replay(events: list[Event] | tuple[Event, ...]) -> Graph:
    acc = _Acc()
    for i, ev in enumerate(events):
        _apply(acc, i, ev)
    return Graph({k: tuple(v) for k, v in acc.versions.items()}, dict(acc.concepts), tuple(acc.edges),
                 tuple(acc.audit), tuple(acc.issues), tuple(sorted(acc.candidates)), tuple(sorted(acc.accepted.items())))


def canonical_json(g: Graph) -> str:
    def ver(v: Version) -> dict:
        return {"n": v.n, "qty": v.qty.render(), "qty_eval": v.qty.evaluate(), "alive": v.alive,
                "location": v.location, "event": v.event_index,
                "fields": {k: asdict(b) for k, b in v.fields}}
    obj = {"versions": {e: [ver(v) for v in vs] for e, vs in sorted(g.versions.items())},
           "concepts": dict(sorted(g.concepts.items())), "edges": [asdict(e) for e in g.edges],
           "audit": list(g.audit), "issues": list(g.issues), "candidates": list(g.candidates),
           "accepted": list(g.accepted)}
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
