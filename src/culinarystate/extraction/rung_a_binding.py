"""Step 17b Rung A argument binding, templates and coreference (DRAFT_PENDING_16c).

``build_events`` and ``resolve_refs`` share one deterministic binder over the
MentionSet (links and quantities only add traced attributes), so a reference
result always agrees with the graph it is checked against:

- one candidate event per ACTION mention, ordered by (sentence, ordinal) in text;
- nearest-noun binding: FOOD / INTERMEDIATE mentions between the verb and the next
  verb of the sentence (not inside an "until ..." endpoint); "into a/an X" or "into X"
  names the product, "into the X" is an ordinary destination argument;
- recency: a verb without explicit arguments binds the most recently touched live
  entity when exactly one exists (IMPLICIT_ARG_BOUND), else none
  (IMPLICIT_ARG_AMBIGUOUS / IMPLICIT_ARG_NONE); combine verbs (PROC family
  COMBINATION or the rule compiler's COMBINE set) also take the current mixture;
- lexical coref: a repeated food reuses its live entity, or its single live
  descendant, else a new lot is opened (all flagged);
- pronouns: ``it`` / mixture words need a unique most-recent live entity
  (else UNRESOLVED AMBIGUOUS_ANTECEDENT), ``them`` takes the whole most-recent tier,
  ``everything`` all live entities; reserved portions are never implicit; a mixture
  word with no live candidate keeps its NO_VALID_CANDIDATE reference result and opens
  a new MIXTURE entity without producer (INTERMEDIATE_NEW_ENTITY);
- sentence templates: discard -> DISCARD; reserve -> RESERVE (+ REMAINDER when
  "half" is stated); divide into N (digits or one..twelve) -> N SPLIT children;
  combine or a named product -> one output; other verbs transform each input.
  Fractions are given only when stated ("half"); split fractions stay UNKNOWN.

First instruction mentions of a food are typed INGREDIENT_LOT (draft proxy: the
ingredient list is not part of the instruction text; needs H4). No value is
invented: every attribute is a span literal, a registered rule, a candidate
selection or an rc2 QNT record.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from culinarystate.state_graph.rule_compiler import COMBINE

from . import rung_a_rules as R
from .interfaces import (
    AllocationCandidate, EntityCandidate, EventCandidate, EventGraph, Failure, FailureCode, LinkResult, Mention,
    MentionSet, QuantityGroundingResult, ReferenceResult, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim,
    ValueKind, channel_value,
)
from .rung_a_lexicon import RungALexicon, key_of, singular_variants

STATUS = "DRAFT_PENDING_16c"
REFERRING = {"it": "SG", "them": "PL", "everything": "ALL"}
MODIFIERS = frozenset({"gently", "carefully", "quickly", "lightly", "well", "briefly", "finely", "roughly",
                       "thinly", "thickly", "slowly", "constantly", "occasionally", "vigorously", "thoroughly"})
SPLIT_RE = re.compile(r"\binto[ \t]+(\d+|" + "|".join(R.NUMBER_WORDS) + r")\b", re.IGNORECASE)
PRODUCT_RE = re.compile(r"\binto[ \t]+(?:(?:a|an)[ \t]+)?$", re.IGNORECASE)
MAX_SPLIT = 24


@dataclass
class _Ent:
    eid: str
    etype: str
    tick: int
    parents: tuple[str, ...] = ()
    created_by: str | None = None
    span: Span | None = None
    key: tuple | None = None
    mention_id: str | None = None
    live: bool = True
    consumed: bool = False
    discarded: bool = False
    optional: bool = False


@dataclass
class _Ev:
    eid: str
    order: tuple[int, int]
    mention: Mention
    window: tuple[int, int]
    consumes: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    discards: list[str] = field(default_factory=list)
    attrs: list[ValueClaim] = field(default_factory=list)


@dataclass
class _Ref:
    mention: Mention
    candidates: tuple[str, ...]
    antecedents: tuple[str, ...]
    failure: Failure | None


@dataclass
class Bound:
    events: list[_Ev]
    entities: dict[str, _Ent]
    allocations: list[AllocationCandidate]
    refs: list[_Ref]
    flags: list[str]


def _sentences(raw: str) -> list[tuple[int, int]]:
    from .rung_a import sentences
    return sentences(raw)


def _referring(m: Mention) -> str | None:
    if m.label == "INTERMEDIATE_MENTION":
        return "INTERMEDIATE"
    return REFERRING.get(m.span.surface.lower()) if m.label == "FOOD_MENTION" else None


class _Binder:
    def __init__(self, source: SourceText, mentions: MentionSet, lexicon: RungALexicon,
                 rules: Mapping[str, R.Recomputer]) -> None:
        self.source, self.raw, self.lex, self.rules = source, source.raw, lexicon, rules
        self.ms = sorted(mentions.mentions, key=lambda m: (m.span.char_start, m.span.char_end))
        self.endpoints = [m for m in self.ms if m.label == "ENDPOINT"]
        self.ents: dict[str, _Ent] = {}
        self.events: list[_Ev] = []
        self.allocs: list[AllocationCandidate] = []
        self.refs: list[_Ref] = []
        self.flags: list[str] = []
        self.keyed: dict[tuple, str] = {}
        self.tick = 0
        self.current: str | None = None

    # ------------------------------------------------------------ helpers
    def _new(self, etype: str, **kw: Any) -> str:
        eid = f"N{len(self.ents) + 1}"
        self.ents[eid] = _Ent(eid, etype, self.tick, **kw)
        return eid

    def _span(self, start: int, end: int) -> Span:
        return Span.of(self.source, start, end)

    def _in_endpoint(self, m: Mention) -> bool:
        return any(e.span.char_start <= m.span.char_start and m.span.char_end <= e.span.char_end
                   for e in self.endpoints)

    def _live(self, intermediates_only: bool = False) -> list[_Ent]:
        return [e for e in self.ents.values() if e.live and e.etype != "RESERVED_PORTION"
                and not (intermediates_only and e.etype == "INGREDIENT_LOT")]

    @staticmethod
    def _tier(ents: list[_Ent]) -> list[_Ent]:
        top = max((e.tick for e in ents), default=None)
        return [e for e in ents if e.tick == top]

    def _key(self, m: Mention) -> tuple:
        ids = self.lex.food_ids(m.span.surface)
        if len(ids) == 1:
            return ("ING", next(iter(ids)))
        words = list(key_of(m.span.surface))
        if words:
            words[-1] = (singular_variants(words[-1]) or (words[-1],))[-1]
        return ("SURFACE", " ".join(words))

    def _descendants(self, eid: str) -> list[str]:
        out, frontier = [], [eid]
        while frontier:
            nxt = [e.eid for e in self.ents.values() if set(e.parents) & set(frontier)]
            out.extend(nxt)
            frontier = nxt
        return [d for d in dict.fromkeys(out) if self.ents[d].live]

    def _lexical(self, m: Mention) -> str:
        key = self._key(m)
        prev = self.keyed.get(key)
        if prev is not None:
            if self.ents[prev].live:
                self.flags.append("LEXICAL_COREF_REUSE")
                return prev
            desc = self._descendants(prev)
            if len(desc) == 1:
                self.flags.append("LEXICAL_COREF_DESCENDANT")
                return desc[0]
            self.flags.append("LEXICAL_REPEAT_NEW_LOT")
        eid = self._new("INGREDIENT_LOT", span=m.span, key=key, mention_id=m.mention_id)
        self.keyed[key] = eid
        return eid

    def _resolve(self, m: Mention, kind: str) -> _Ref:
        live = self._live()
        cands = tuple(e.eid for e in live)
        pool = self._live(intermediates_only=True) if kind == "INTERMEDIATE" else live
        if not pool:
            reason = "NO_LIVE_INTERMEDIATE" if kind == "INTERMEDIATE" and live else "NO_LIVE_ENTITY"
            return _Ref(m, cands, (), Failure(FailureCode.NO_VALID_CANDIDATE, reason))
        tier = self._tier(pool)
        if kind == "ALL":
            return _Ref(m, cands, cands, None)
        if kind == "PL" or len(tier) == 1:
            return _Ref(m, cands, tuple(e.eid for e in tier), None)
        self.flags.append("AMBIGUOUS_REFERENCE")
        return _Ref(m, cands, (), Failure(FailureCode.UNRESOLVED, "AMBIGUOUS_ANTECEDENT"))

    def _free(self, mentions: list[Mention]) -> None:
        """Mentions outside every action window: open lots / resolve references, bind nothing."""
        if not mentions:
            return
        self.tick += 1
        for m in mentions:
            kind = _referring(m)
            if kind is None:
                self._lexical(m)
            else:
                self.refs.append(self._resolve(m, kind))

    # ------------------------------------------------------------ main loop
    def run(self) -> Bound:
        args = [m for m in self.ms if m.label in ("FOOD_MENTION", "INTERMEDIATE_MENTION") and not self._in_endpoint(m)]
        for si, (ss, se) in enumerate(_sentences(self.raw)):
            acts = [m for m in self.ms if m.label == "ACTION" and ss <= m.span.char_start < se]
            sent_args = [m for m in args if ss <= m.span.char_start < se]
            first = acts[0].span.char_start if acts else se
            self._free([m for m in sent_args if m.span.char_start < first])
            for oi, act in enumerate(acts):
                end = acts[oi + 1].span.char_start if oi + 1 < len(acts) else se
                window = (act.span.char_end, end)
                self._event(si, oi, act, window, [m for m in sent_args if window[0] <= m.span.char_start < end])
        return Bound(self.events, self.ents, self.allocs, self.refs, self.flags)

    def _event(self, si: int, oi: int, act: Mention, window: tuple[int, int], margs: list[Mention]) -> None:
        self.tick += 1
        ev = _Ev(f"E{len(self.events) + 1}", (si, oi), act, window)
        self.events.append(ev)
        ids = self.lex.proc_ids(act.span.surface)
        info = self.lex.proc_info.get(next(iter(ids))) if len(ids) == 1 else None
        product, inputs, ref_failed = None, [], False
        for m in margs:
            kind = _referring(m)
            if kind is None and product is None and PRODUCT_RE.search(self.raw[window[0]:m.span.char_start]):
                product = m
            elif kind is None:
                inputs.append(self._lexical(m))
            else:
                ref = self._resolve(m, kind)
                self.refs.append(ref)
                inputs.extend(ref.antecedents)
                if kind == "INTERMEDIATE" and ref.failure is not None \
                        and ref.failure.code is FailureCode.NO_VALID_CANDIDATE:
                    self.flags.append("INTERMEDIATE_NEW_ENTITY")
                    inputs.append(self._new("MIXTURE", span=m.span))
                else:
                    ref_failed = ref_failed or ref.failure is not None
        inputs = list(dict.fromkeys(inputs))
        if ref_failed:
            self.flags.append("REF_ARG_UNRESOLVED")
        elif not inputs and product is None:
            tier = self._tier(self._live())
            self.flags.append({0: "IMPLICIT_ARG_NONE", 1: "IMPLICIT_ARG_BOUND"}.get(len(tier),
                                                                                  "IMPLICIT_ARG_AMBIGUOUS"))
            if len(tier) == 1:
                inputs = [tier[0].eid]
        combine = info is not None and (info.family == "COMBINATION" or info.canonical in COMBINE)
        cur = self.current
        if combine and cur and self.ents[cur].live and cur not in inputs and (inputs or product):
            inputs.insert(0, cur)
            self.flags.append("COMBINE_WITH_CURRENT")
        text = self.raw[window[0]:window[1]]
        prefix = self.raw[max(0, act.span.char_start - 12):act.span.char_start]
        negated = R.NEGATION_RE.search(prefix)
        if negated:
            self.flags.append("NEGATED_EVENT_NOT_APPLIED")
            base = act.span.char_start - len(prefix)
            ev.attrs.append(R.ruled("modality", ValueKind.CATEGORICAL, "NEGATED",
                                    self._span(base + negated.start(), base + negated.end()), "RA_MODALITY_CUE_V1"))
            return
        opt = R.OPTIONAL_RE.search(text)
        if opt:
            ev.attrs.append(R.ruled("modality", ValueKind.CATEGORICAL, "OPTIONAL",
                                    self._span(window[0] + opt.start(), window[0] + opt.end()), "RA_MODALITY_CUE_V1"))
        canonical = info.canonical if info else ""
        if canonical == "discard" and inputs:
            for i in inputs:
                ev.discards.append(i)
                self.ents[i].live, self.ents[i].discarded = False, True
                self.ents[i].optional = self.ents[i].optional or bool(opt)
            return
        for i in inputs:
            self.ents[i].optional = self.ents[i].optional or bool(opt)
        if info is not None and info.family == "RESERVATION" and inputs:
            self._reserve(ev, inputs, text, window[0])
        elif canonical == "divide" and inputs and self._split(ev, inputs, text, window[0]):
            pass
        elif inputs or product is not None:
            if product is not None or combine:
                out = self._new("MIXTURE" if len(inputs) >= 2 else "INTERMEDIATE", parents=tuple(inputs),
                                created_by=ev.eid, span=product.span if product else None,
                                key=self._key(product) if product else None)
                if product is not None:
                    self.keyed[self._key(product)] = out
                self._consume(ev, inputs, {i: out for i in inputs})
                ev.produces.append(out)
                if combine:
                    self.current = out
            else:
                mapping = {i: self._new("INTERMEDIATE", parents=(i,), created_by=ev.eid) for i in inputs}
                self._consume(ev, inputs, mapping)
                ev.produces.extend(mapping.values())

    def _consume(self, ev: _Ev, inputs: list[str], mapping: Mapping[str, str]) -> None:
        for i in inputs:
            ev.consumes.append(i)
            self.ents[i].live, self.ents[i].consumed = False, True
            if self.current == i:
                self.current = mapping.get(i)

    def _reserve(self, ev: _Ev, inputs: list[str], text: str, offset: int) -> None:
        h = re.search(r"\bhalf\b", text, re.IGNORECASE)
        frac = None
        if h:
            frac = R.ruled("fraction", ValueKind.FRACTION, R.half("half")[0],
                           self._span(offset + h.start(), offset + h.end()), "RA_HALF_V1")
        mapping = {}
        for i in inputs:
            child = self._new("RESERVED_PORTION", parents=(i,), created_by=ev.eid)
            self._alloc("RESERVE", i, child, ev.eid, frac)
            ev.produces.append(child)
            mapping[i] = child
            if h:
                rem = self._new("INTERMEDIATE", parents=(i,), created_by=ev.eid)
                self._alloc("REMAINDER", i, rem, ev.eid, None)
                ev.produces.append(rem)
                mapping[i] = rem
        self._consume(ev, inputs, mapping)

    def _split(self, ev: _Ev, inputs: list[str], text: str, offset: int) -> bool:
        m = SPLIT_RE.search(text)
        if m is None:
            self.flags.append("SPLIT_COUNT_UNKNOWN")
            return False
        token = m.group(1)
        span = self._span(offset + m.start(1), offset + m.end(1))
        n = int(token) if token.isdigit() else R.NUMBER_WORDS[token.lower()]
        if not 2 <= n <= MAX_SPLIT:
            self.flags.append("SPLIT_COUNT_OUT_OF_RANGE")
            return False
        ev.attrs.append(R.literal("split_count", ValueKind.COUNT, n, span) if token.isdigit()
                        else R.ruled("split_count", ValueKind.COUNT, n, span, "RA_NUMBER_WORD_V1"))
        mapping = {}
        for i in inputs:
            for _ in range(n):
                child = self._new("INTERMEDIATE", parents=(i,), created_by=ev.eid)
                self._alloc("SPLIT", i, child, ev.eid, None)
                ev.produces.append(child)
            mapping[i] = None
        self._consume(ev, inputs, mapping)
        return True

    def _alloc(self, kind: str, parent: str, child: str, event_id: str, frac: ValueClaim | None) -> None:
        self.allocs.append(AllocationCandidate(f"A{len(self.allocs) + 1}", kind, "UNSPECIFIED", parent, child,
                                               event_id, frac))



# ------------------------------------------------------------------ graph assembly
def _lifecycle(e: _Ent) -> str:
    if e.discarded:
        return "DISCARDED"
    if e.consumed:
        return "INCORPORATED"
    return "RESERVED" if e.etype == "RESERVED_PORTION" else "ACTIVE"


def _lot_status(e: _Ent) -> str:
    if e.discarded:
        return "DISCARDED"
    if e.optional:
        return "OPTIONAL"
    return "USED" if e.consumed else "APPARENTLY_UNUSED"


def _suffixed(claims: list[ValueClaim]) -> list[ValueClaim]:
    seen: dict[str, int] = {}
    out = []
    for c in claims:
        n = seen.get(c.field, 0)
        seen[c.field] = n + 1
        out.append(c if n == 0 else replace(c, field=f"{c.field}_{n}"))
    return out


def _event_attrs(b: _Binder, ev: _Ev, mentions: list[Mention], quantities: Sequence[QuantityGroundingResult],
                 rules: Mapping[str, R.Recomputer]) -> tuple[ValueClaim, ...]:
    act = ev.mention
    out: list[ValueClaim] = []
    for field_name, rule, kind in (("event_kind", "RA_EVENT_KIND_V1", ValueKind.CATEGORICAL),
                                   ("proc_id", "RA_PROC_LOOKUP_V1", ValueKind.IDENTIFIER)):
        got = R.try_rule(rules[rule], act.span.surface)
        if got is not None:
            out.append(R.ruled(field_name, kind, got[0], act.span, rule))
    out.extend(ev.attrs)
    s, e = ev.window
    prev_words = re.findall(r"[^\W\d_]+", b.raw[max(0, act.span.char_start - 15):act.span.char_start])
    if prev_words and prev_words[-1].lower() in MODIFIERS:
        idx = b.raw.rfind(prev_words[-1], 0, act.span.char_start)
        out.append(R.literal("modifier", ValueKind.TEXT, prev_words[-1], b._span(idx, idx + len(prev_words[-1]))))
    nxt = re.match(r"[ \t]+([^\W\d_]+)", b.raw[s:e])
    if nxt and nxt.group(1).lower() in MODIFIERS:
        out.append(R.literal("modifier", ValueKind.TEXT, nxt.group(1), b._span(s + nxt.start(1), s + nxt.end(1))))
    tools = []
    for m in mentions:
        if not s <= m.span.char_start < e:
            continue
        if m.label in ("DURATION", "TEMPERATURE"):
            out.extend(a for a in m.attributes if a.value is not None)
        elif m.label == "TOOL":
            tools.extend(a for a in m.attributes if a.field == "tool_id")
        elif m.label == "ENDPOINT" and m.span.surface[:5].lower() == "until":
            out.append(R.ruled("temporal_relation", ValueKind.CATEGORICAL, "UNTIL",
                               b._span(m.span.char_start, m.span.char_start + 5), "RA_UNTIL_V1"))
    out.extend(replace(t, field=f"tool_id_{k}") for k, t in enumerate(tools))
    k = 0
    for q in quantities:
        if q.record is None or not s <= q.span.char_start < e:
            continue
        value = channel_value(q.record.get("mass_g"))
        if value is not None:
            out.append(ValueClaim(f"amount_g_{k}", ValueKind.MASS_G, value, origin=R.ORIGIN, claim_route=R.ROUTE,
                                  span=q.span, trace=Trace(TraceKind.QNT_RECORD, ref_ids=(q.result_id,)), unit="g"))
            k += 1
    return tuple(_suffixed(out))


def build_graph(source: SourceText, mentions: MentionSet, links: Sequence[LinkResult],
                quantities: Sequence[QuantityGroundingResult], config: StageConfig, lexicon: RungALexicon,
                rules: Mapping[str, R.Recomputer]) -> EventGraph:
    binder = _Binder(source, mentions, lexicon, rules)
    bound = binder.run()
    link_by = {lr.mention_id: lr for lr in links}
    producers = {eid: e.created_by for eid, e in bound.entities.items()}
    events = []
    for ev in bound.events:
        deps = tuple(dict.fromkeys(p for i in (*ev.consumes, *ev.discards) if (p := producers.get(i))
                                   and p != ev.eid))
        events.append(EventCandidate(ev.eid, ev.order, ev.mention.span, tuple(ev.consumes), tuple(ev.produces),
                                     tuple(ev.discards), deps, _event_attrs(binder, ev, binder.ms, quantities, rules),
                                     claim_route="INFERRED_RULE"))
    entities = []
    for e in bound.entities.values():
        attrs: tuple[ValueClaim, ...] = ()
        lr = link_by.get(e.mention_id or "")
        if lr is not None and lr.selected_id is not None:
            attrs = (R.selected("ingredient_id", lr.selected_id, lr.span, lr.candidate_ids),)
        entities.append(EntityCandidate(e.eid, e.etype, _lifecycle(e), e.parents, e.created_by, e.span, attrs))
    lots = {e.eid: _lot_status(e) for e in bound.entities.values() if e.etype == "INGREDIENT_LOT"}
    return EventGraph(source.text_id, source.sha256, tuple(events), tuple(entities), tuple(bound.allocations),
                      lots, config.provenance("build_events"), diagnostics=tuple(bound.flags))


def resolve_references(source: SourceText, mentions: MentionSet, graph: EventGraph, config: StageConfig,
                       lexicon: RungALexicon) -> tuple[ReferenceResult, ...]:
    """Re-run the binder; a graph that it does not reproduce gets explicit failures."""
    bound = _Binder(source, mentions, lexicon, {}).run()
    prov = config.provenance("resolve_refs")
    same = graph.raw_sha256 == source.sha256 and [e.event_id for e in graph.events] == [e.eid for e in bound.events] \
        and [n.entity_id for n in graph.entities] == list(bound.entities)
    out = []
    for r in sorted(bound.refs, key=lambda r: r.mention.span.char_start):
        if not same:
            out.append(ReferenceResult(r.mention.mention_id, r.mention.span, (), prov,
                                       failure=Failure(FailureCode.UNRESOLVED, "GRAPH_NOT_REPRODUCED")))
        else:
            out.append(ReferenceResult(r.mention.mention_id, r.mention.span, r.candidates, prov,
                                       antecedent_ids=r.antecedents, failure=r.failure))
    return tuple(out)
