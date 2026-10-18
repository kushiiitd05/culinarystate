"""C18 session-state updater (SSOT §257B.18): replay session events into a state graph.

SessionState wraps the event-sourced engine (state_graph.engine) and exposes the derived
facts that the decision layer needs:
- process_history(): set of process names applied so far (for diagnosis verification)
- current_state(entity): field beliefs for an entity (for state-conditioned answers)
- update(events): return a NEW SessionState with additional events (immutability rule)

Usage:
  ss = SessionState.from_turns(turns)          # turns = list of dicts with "events"
  history = ss.process_history()               # {"simmer", "fry", ...}
  ss2 = ss.update([Observe("rice pot", "texture", "hard centre")])

Session events are stored as plain dicts (JSON-serialisable) and converted to engine
Event dataclasses on replay.  Unknown event types → issues list (not crash).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

from culinarystate.state_graph.engine import (
    Add, Transform, Merge, Split, Reserve, Discard, Recombine,
    Transfer, Observe, Predict, OmittedStepCandidate, AcceptCandidate,
    Event, Graph, replay,
)

VERSION = "session_state@0.1"

_TYPE_MAP = {
    "Add": Add, "Transform": Transform, "Merge": Merge, "Split": Split,
    "Reserve": Reserve, "Discard": Discard, "Recombine": Recombine,
    "Transfer": Transfer, "Observe": Observe, "Predict": Predict,
    "OmittedStepCandidate": OmittedStepCandidate, "AcceptCandidate": AcceptCandidate,
}


def _to_event(d: dict) -> Event | None:
    """Convert a JSON-style event dict to a typed engine Event, or None if unrecognised."""
    t = d.get("type")
    cls = _TYPE_MAP.get(t)
    if cls is None:
        return None
    kw = {k: v for k, v in d.items() if k != "type"}
    # coerce fields that JSON serialises as a dict/list but the dataclass wants differently
    if "inputs" in kw and isinstance(kw["inputs"], list):
        kw["inputs"] = tuple(kw["inputs"])
    if "outputs" in kw and isinstance(kw["outputs"], list):
        kw["outputs"] = tuple((lbl, Fraction(f) if f is not None else None)
                              for lbl, f in kw["outputs"])
    if "sets" in kw and isinstance(kw["sets"], dict):
        kw["sets"] = tuple(kw["sets"].items())
    if "proposed" in kw and isinstance(kw["proposed"], (list, tuple)):
        kw["proposed"] = tuple(e for raw in kw["proposed"] if (e := _to_event(raw)))
    if "condition" in kw and kw["condition"] is None:
        kw["condition"] = {}
    # qty fields that need Base
    if "qty" in kw and isinstance(kw["qty"], str):
        from culinarystate.state_graph.symqty import Base
        kw["qty"] = Base.qualitative(kw["qty"])
    if "portion" in kw and isinstance(kw["portion"], str):
        from culinarystate.state_graph.symqty import Base
        kw["portion"] = Base.qualitative(kw["portion"])
    if "fraction" in kw and kw["fraction"] is not None:
        kw["fraction"] = Fraction(kw["fraction"])
    try:
        return cls(**kw)
    except TypeError:
        return None  # missing required fields → skip with issue


@dataclass(frozen=True)
class SessionState:
    """Immutable session state: holds events and the replayed graph."""
    events: tuple[Event, ...] = ()
    graph: Graph = field(default_factory=lambda: replay(()))
    issues: tuple[str, ...] = ()
    version: str = VERSION

    @classmethod
    def empty(cls) -> SessionState:
        return cls()

    @classmethod
    def from_events(cls, events: list[Event]) -> SessionState:
        g = replay(events)
        return cls(events=tuple(events), graph=g, issues=tuple(g.issues))

    @classmethod
    def from_session(cls, session: dict) -> SessionState:
        """Build from a full session JSON (with 'ingredients' and 'turns')."""
        turns = session.get("turns", [])
        return cls.from_turns(turns, ingredients=session.get("ingredients"))

    @classmethod
    def from_turns(cls, turns: list[dict], ingredients: list[dict] | None = None) -> SessionState:
        """Build from session JSON turns (each has an 'events' list of dicts).
        If ingredients is provided, Add events are auto-injected at step 0."""
        events: list[Event] = []
        issues: list[str] = []
        if ingredients:
            for ing in ingredients:
                from culinarystate.state_graph.symqty import Base
                events.append(Add(
                    label=ing["entity"],
                    concept_id=ing.get("concept") if ing.get("concept") != "UNKNOWN" else None,
                    qty=Base.qualitative(ing.get("quantity", ing["entity"])),
                    step=0,
                ))
        for t in turns:
            for raw in t.get("events", []):
                ev = _to_event(raw)
                if ev is None:
                    typ = raw.get("type", "?")
                    reason = "unknown type" if typ not in _TYPE_MAP else "missing required fields"
                    issues.append(f"turn {t.get('turn', '?')}: {reason} for event '{typ}'")
                else:
                    events.append(ev)
        g = replay(events)
        return cls(events=tuple(events), graph=g, issues=tuple(list(g.issues) + issues))

    def update(self, new_events: list[Event]) -> SessionState:
        """Return a NEW SessionState with additional events appended (immutable)."""
        all_events = list(self.events) + new_events
        g = replay(all_events)
        return SessionState(events=tuple(all_events), graph=g, issues=tuple(g.issues))

    def process_history(self) -> set[str]:
        """Set of process canonical names applied in this session (for diagnosis verification)."""
        procs = set()
        for ev in self.events:
            if isinstance(ev, Transform):
                procs.add(ev.process)
            elif isinstance(ev, Merge) and ev.process:
                procs.add(ev.process)
        return procs

    def current_state(self, entity: str) -> dict | None:
        """Current field beliefs for an entity, or None if unknown."""
        vs = self.graph.versions.get(entity)
        if not vs:
            return None
        v = vs[-1]
        return {"entity": entity, "alive": v.alive,
                "qty": v.qty.render(), "location": v.location,
                "fields": {k: {"value": b.value, "trajectory": b.trajectory, "source": b.source}
                           for k, b in v.fields}}

    def alive_entities(self) -> list[str]:
        return self.graph.alive()

    def entity_process(self, entity: str) -> str | None:
        """Last process applied to an entity, or None."""
        vs = self.graph.versions.get(entity)
        if not vs:
            return None
        b = vs[-1].get("last_process")
        return b.value if b else None
