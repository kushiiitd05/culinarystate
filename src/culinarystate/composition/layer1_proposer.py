"""Layer-1 LLM structured proposer, gated by ambiguity triggers (freeze step 6).

Rules and frozen models run first. The LLM is asked for a structured proposal **only** when an
ambiguity trigger fires, every proposal must carry source-span grounding, and the validator decides
acceptance. The proposer never writes state: ``review`` returns decisions and ``apply`` builds a new
graph, leaving the original alone.

Triggers are not new detection logic. They are the signals the pipeline already emits: the lineage
vNext flags (D-132) and the Rung-A ambiguity codes, plus an unresolved lot status.

What a proposal may say is deliberately narrow. It may bind an ``alternative_group``, name a
``condition_profile_id`` or resolve a referent — all categorical, all span-grounded. It may never
propose a number: no numeric chemistry comes from the model.

The client is injected (see ``ProposerClient``), so the gate is testable without a network call.
Hosted-model choice stays provider-agnostic and is settled in step 7, not here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping, Protocol, Sequence

from culinarystate.extraction import invariants as INV
from culinarystate.extraction.interfaces import EventGraph

#: Signals that license asking the model. Anything else is ignored, never escalated.
TRIGGERS: tuple[str, ...] = (
    "AMBIGUOUS_ACTION",
    "AMBIGUOUS_ANTECEDENT",
    "AMBIGUOUS_CANDIDATES",
    "AMBIGUOUS_OR_MISSING",
    "AMBIGUOUS_REFERENCE",
    "UNRESOLVED_LOT",
    "VNEXT_ALTERNATIVE_SKIPPED",
    "VNEXT_FAT_STAYS",
    "VNEXT_MIXTURE_COREF",
)
#: Event fields a proposal may set. All categorical; ``produces``/``consumes`` are never proposable.
PROPOSABLE_FIELDS: tuple[str, ...] = ("alternative_group",)
#: Reference fields: a valid value is the id of a record that already exists. ``condition_profile_id``
#: is defined by the 36-step plan as a pointer to a 07H COND record; nothing in ``src/`` reads it and
#: no COND records are minted on the recipe side, so there is no referent to point at. A model cannot
#: mint a reference and a non-blank string check cannot tell one from a noun lifted out of the
#: sentence, which is what step 7 recorded ("pan", "chicken", "bowl_content" accepted as condition
#: profiles). The field stays on the Event IR, declared and unpopulated, which is its honest state.
#: Refused with its own code so the reason is not mistaken for a vocabulary miss.
REFERENCE_FIELDS: tuple[str, ...] = ("condition_profile_id",)
#: Which field each trigger licenses. Only the "A or B" trigger licenses anything.
#:
#: Every other trigger previously licensed ``condition_profile_id``, which is a reference field with
#: no referent (see ``REFERENCE_FIELDS``), so they now license nothing and are **declared-open,
#: rules-only**: the ambiguity is detected and recorded as UNKNOWN rather than answered by a model.
#:
#: The coreference triggers are not rescuable. Their answer's destination is either an allocation,
#: which is never proposable, or a cell the rules already fill from a cue span with a basis
#: (``Q.medium``, ``Q.lid_state``) - and a model answer there would be a second, unsourced opinion on
#: a sourced cell. ``VNEXT_FAT_STAYS`` licenses nothing because the rule has already committed the
#: merge before the flag is raised (``extraction/rung_a_binding.py``): whether frying fat stays with
#: the food is a mass-transfer question the text does not state and Layer-1 cannot answer. The keys
#: are kept so a closed trigger stays distinguishable from an unknown one.
TRIGGER_FIELDS: dict[str, tuple[str, ...]] = {
    "AMBIGUOUS_ACTION": (),
    "AMBIGUOUS_ANTECEDENT": (),
    "AMBIGUOUS_CANDIDATES": (),
    "AMBIGUOUS_OR_MISSING": (),
    "AMBIGUOUS_REFERENCE": (),
    "UNRESOLVED_LOT": (),
    "VNEXT_ALTERNATIVE_SKIPPED": ("alternative_group",),
    "VNEXT_FAT_STAYS": (),
    "VNEXT_MIXTURE_COREF": (),
}
#: Every reason the gate may refuse a proposal. Closed: ``_reject`` returns one of these or None, so
#: a rejection histogram can never contain a code that is not declared here.
REJECTION_CODES: tuple[str, ...] = (
    "TRIGGER_NOT_IN_VOCABULARY",
    "TRIGGER_DID_NOT_FIRE",
    "FIELD_REQUIRES_EXISTING_REFERENT",
    "FIELD_NOT_PROPOSABLE",
    "NUMERIC_VALUE_NOT_ALLOWED",
    "FIELD_NOT_LICENSED_BY_TRIGGER",
    "EVENT_NOT_IN_GRAPH",
    "SPAN_OUT_OF_RANGE",
    "SPAN_DOES_NOT_GROUND_VALUE",
    "WOULD_VIOLATE_INVARIANT",
    "MALFORMED_PROPOSAL",
)
#: Coordinators that bind an alternative in recipe prose. ``alternative_group`` is the only
#: proposable field and ``VNEXT_ALTERNATIVE_SKIPPED`` is the only trigger that licenses it, and that
#: trigger fires on coordinated text - so a span that grounds such a value contains one of these as a
#: standalone token. Matched on word boundaries: "for", "colour" and "coriander" all contain "or".
_COORDINATOR = re.compile(r"\b(?:or|either)\b", re.I)
#: "simmer for 20 minutes **or until** thickened" is an endpoint condition, not a branch. The
#: construction is very common in recipe prose, so an "or" that is only ever part of one does not
#: ground an alternatives binding.
_ENDPOINT_OR = re.compile(r"\bor\s+(?:until|till|when|so)\b", re.I)
#: Lot statuses that count as an ambiguity.
_UNRESOLVED_LOT_STATUSES = frozenset({"UNRESOLVED", "APPARENTLY_UNUSED"})
_NUMERIC = re.compile(r"^\s*-?\d+(?:[.,]\d+)?\s*%?\s*$")


class ProposalError(ValueError):
    """Raised when a proposal is structurally invalid (bad span, missing span)."""


class ProposerClient(Protocol):
    """Whatever produces proposals. Provider-agnostic by design."""

    def propose(self, *, raw: str, triggers: Sequence[str], graph: EventGraph) -> Sequence[Any]:
        ...


@dataclass(frozen=True)
class Proposal:
    trigger: str
    field: str
    value: str
    event_id: str
    span_start: int | None
    span_end: int | None
    rationale: str = ""
    claim_route: str = "LLM_PROPOSED"

    def __post_init__(self) -> None:
        if self.span_start is None or self.span_end is None:
            raise ProposalError("A proposal must carry source-span grounding")
        if not isinstance(self.span_start, int) or not isinstance(self.span_end, int):
            raise ProposalError("Span offsets must be integers")
        if self.span_end <= self.span_start or self.span_start < 0:
            raise ProposalError(f"Empty or inverted span ({self.span_start}, {self.span_end})")
        if not str(self.value).strip():
            raise ProposalError("A proposal must carry a value")


@dataclass(frozen=True)
class Decisions:
    accepted: tuple[Proposal, ...] = ()
    rejected: tuple[tuple[Proposal | Any, str], ...] = ()


def triggers_for(*, flags: Iterable[str], lot_accounting: Mapping[str, str]) -> tuple[str, ...]:
    """Triggers that actually fired, deduplicated and sorted. Unknown flags are ignored."""
    found = {f for f in flags if f in TRIGGERS}
    if any(s in _UNRESOLVED_LOT_STATUSES for s in lot_accounting.values()):
        found.add("UNRESOLVED_LOT")
    return tuple(sorted(found))


def span_grounds_value(raw: str, start: int, end: int) -> bool:
    """Does the span actually license an alternatives binding, or is it merely in range?

    The gate used to check only that the offsets lay inside ``raw``. That is a range check, not
    grounding: any in-range offsets passed, and a review of the 14 accepted step-7 proposals found
    **none** whose span supported its value, at distances of 43 to 530 characters from the real
    evidence. The directive requires source-span grounding, so the span must contain a coordinator
    that is not part of an endpoint condition.
    """
    if not (0 <= start < end <= len(raw)):
        return False
    text = raw[start:end]
    without_endpoints = _ENDPOINT_OR.sub(" ", text)
    return bool(_COORDINATOR.search(without_endpoints))


def _reject(proposal: Proposal, graph: EventGraph, fired: Sequence[str]) -> str | None:
    """The first reason this proposal must be refused, or None if it survives the gate."""
    if proposal.trigger not in TRIGGERS:
        return "TRIGGER_NOT_IN_VOCABULARY"
    if proposal.trigger not in fired:
        return "TRIGGER_DID_NOT_FIRE"
    # The numeric prohibition is absolute, so it is checked before every field check: a number is
    # refused as a number, whatever field or trigger it arrived under.
    if _NUMERIC.match(str(proposal.value)):
        return "NUMERIC_VALUE_NOT_ALLOWED"
    # Checked before the generic not-proposable code so the refusal states the real cause. Reporting
    # FIELD_NOT_PROPOSABLE here would be true but misleading: it reads as though some other trigger
    # could license the field, and none can, because the referent does not exist.
    if proposal.field in REFERENCE_FIELDS:
        return "FIELD_REQUIRES_EXISTING_REFERENT"
    if proposal.field not in PROPOSABLE_FIELDS:
        return "FIELD_NOT_PROPOSABLE"
    if proposal.field not in TRIGGER_FIELDS.get(proposal.trigger, ()):
        return "FIELD_NOT_LICENSED_BY_TRIGGER"
    if not any(e.event_id == proposal.event_id for e in graph.events):
        return "EVENT_NOT_IN_GRAPH"
    return None


def review(proposals: Iterable[Any], graph: EventGraph, *, triggers: Sequence[str],
           raw: str) -> Decisions:
    """Gate proposals. The validator decides: anything that would break V4 is refused.

    ``raw`` is required: span grounding is mandatory, so the offsets are always range-checked
    against the text they claim to point at.
    """
    accepted: list[Proposal] = []
    rejected: list[tuple[Any, str]] = []

    for p in proposals:
        if not isinstance(p, Proposal):
            rejected.append((p, "MALFORMED_PROPOSAL"))
            continue
        reason = _reject(p, graph, triggers)
        if reason:
            rejected.append((p, reason))
            continue
        if p.span_end > len(raw):
            rejected.append((p, "SPAN_OUT_OF_RANGE"))
            continue
        if not span_grounds_value(raw, p.span_start, p.span_end):
            rejected.append((p, "SPAN_DOES_NOT_GROUND_VALUE"))
            continue
        before = _issue_codes(graph)
        if _issue_codes(apply([p], graph)) - before:
            rejected.append((p, "WOULD_VIOLATE_INVARIANT"))
            continue
        accepted.append(p)

    return Decisions(tuple(accepted), tuple(rejected))


def _issue_codes(graph: EventGraph) -> frozenset[str]:
    return frozenset(i.code for i in INV.v4_invariants(graph).issues)


def apply(proposals: Iterable[Proposal], graph: EventGraph) -> EventGraph:
    """Return a new graph with the proposals set. The input graph is never mutated."""
    by_event: dict[str, dict[str, str]] = {}
    for p in proposals:
        by_event.setdefault(p.event_id, {})[p.field] = p.value
    if not by_event:
        return graph
    events = tuple(replace(e, **by_event[e.event_id]) if e.event_id in by_event else e
                   for e in graph.events)
    return replace(graph, events=events)


def run(*, raw: str, graph: EventGraph, flags: Iterable[str], lot_accounting: Mapping[str, str],
        client: ProposerClient) -> Decisions:
    """Ask the client only when a trigger fired, then gate what comes back."""
    fired = triggers_for(flags=flags, lot_accounting=lot_accounting)
    if not fired:
        return Decisions()
    return review(client.propose(raw=raw, triggers=fired, graph=graph), graph,
                  triggers=fired, raw=raw)


def span_text(raw: str, proposal: Proposal) -> str:
    """The raw substring a proposal points at, for a reviewer to read."""
    return raw[proposal.span_start:proposal.span_end]


__all__ = ["TRIGGERS", "TRIGGER_FIELDS", "PROPOSABLE_FIELDS", "Proposal", "ProposalError", "ProposerClient",
           "Decisions", "triggers_for", "review", "apply", "run", "span_text"]
