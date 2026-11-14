"""Step 17b Rung A deterministic instruction baseline (DRAFT_PENDING_16c).

Rung A (Plan Step 17-M, B0) implements the six-stage 17a ``RungInterface`` with
rules only (no model, no GPU, no network, no file writes):

- ``extract_mentions``: numeric phrases first (``evidence.conditions`` duration / temperature regexes,
  number + UNIT-lexicon quantities, qualitative heat cues, "until ..." endpoints), then
  longest-match lexicon tagging of TOOL, ACTION (verb -> PROC lookup; noun-like verbs
  need the rule compiler's verb slot; never right after a determiner or number) and
  FOOD_MENTION (ING / ALIAS); ``it`` / ``them``
  / ``everything`` are FOOD_MENTION referring expressions, mixture words
  INTERMEDIATE_MENTION. MEDIUM is not annotated (MISSING, never O);
- ``link``: the unique lexicon candidate, else UNRESOLVED (ambiguous) or
  NO_VALID_CANDIDATE: never a nearest-id guess;
- ``parse_quantity`` / ``ground_quantity``: ``quantity_stages`` (rc2 pipeline);
- ``build_events`` / ``resolve_refs``: see ``rung_a_binding``.

Every output carries claim_route INFERRED_RULE; values are span literals, registered
rules (``rung_a_rules``), candidate selections or rc2 QNT records. Uncertainty is
reported only as rule-fired flags and ambiguity codes in ``diagnostics``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Sequence

from culinarystate.quantity.rc2_grounding import GroundingContext
from culinarystate.state_graph.rule_compiler import _VERB_SLOT, MIXTURE_WORDS, NOUNY

from . import quantity_stages as qs
from . import rung_a_rules as R
from .interfaces import (
    EventGraph, Failure, FailureCode, InterfaceError, LinkCandidate, LinkResult, Mention, MentionSet,
    QuantityGroundingResult, QuantityParseResult, ReferenceResult, SourceText, Span, StageConfig, StageOutput,
    ValueKind,
)
from .rung_a_binding import REFERRING, build_graph, resolve_references
from .rung_a_lexicon import LEXICON_VERSION, RungALexicon, load_lexicon, tokens

STATUS = "DRAFT_PENDING_16c"
RUNG_ID = "A"
RULES_VERSION = "STEP17B_RUNG_A_RULES_V1_DRAFT"
RUNG_A_LABELS = frozenset({"ACTION", "FOOD_MENTION", "INTERMEDIATE_MENTION", "TOOL", "DURATION", "TEMPERATURE",
                           "ENDPOINT", "QUANTITY_IN_STEP", "CONDITION_CUE"})
LINKABLE = ("FOOD_MENTION", "ACTION", "TOOL")
QUANTITY_SCOPE = "INSTRUCTION_ALLOCATION"
QUANTITY_SOURCE_META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
                        "evidence_refs": ["RUNG_A_INSTRUCTION_SPAN"]}
LOCALE_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
               "evidence_refs": ["CALLER_SUPPLIED_LOCALE"]}
AUX_WORDS = frozenset({"can", "will", "may", "might", "should", "must", "would", "could", "do", "does", "did",
                       "be", "is", "are", "was", "were", "have", "has", "had"})
QUANTITY_QUALIFIERS = ("heaped", "level", "rounded", "scant", "generous", "large", "small", "medium")
_DETERMINERS = ("the", "a", "an", "some", "each", "every", "this", "that", "these", "those", "your", "its", "of",
                "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")
_COORD_GAP = re.compile(r"\s*(?:,\s*(?:and|or)?|and|or)\s+", re.IGNORECASE)
_OBJECT_WORDS = frozenset({"it", "them", "the", "a", "an", "this", "these", "each", "both", "well", "lightly",
                           "generously", "with", "to", "over", "all", "evenly", "liberally"})
_NOMINAL_SLOT = re.compile(r"(?:\b(?:" + "|".join(_DETERMINERS) + r")|\d)[ \t]+$", re.IGNORECASE)
_NUM = (r"(?:\d+[ \t]+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?(?:[ \t]?[½⅓⅔¼¾⅛])?"
        r"|[½⅓⅔¼¾⅛⅜⅝⅞])")


@dataclass(frozen=True)
class RungAOutputs:
    mentions: MentionSet
    links: tuple[LinkResult, ...]
    quantities: tuple[QuantityGroundingResult, ...]
    graph: EventGraph
    refs: tuple[ReferenceResult, ...]

    def all(self) -> list[StageOutput]:
        return [self.mentions, *self.links, *self.quantities, self.graph, *self.refs]


def sentences(raw: str) -> list[tuple[int, int]]:
    """Sentence ranges: split after . ! ? ; followed by whitespace, and at line breaks."""
    out, start = [], 0
    for m in re.finditer(r"(?<=[.!?;])[ \t]+|\s*\n\s*", raw):
        if m.start() > start:
            out.append((start, m.start()))
        start = m.end()
    if start < len(raw):
        out.append((start, len(raw)))
    return out


def _overlaps(a: tuple[int, int], spans: Sequence[tuple[int, int]]) -> bool:
    return any(a[0] < e and s < a[1] for s, e in spans)


class RungA:
    """Deterministic Rung A over a read-only lexicon (default: the repository lexicons)."""

    def __init__(self, lexicon: RungALexicon | None = None, *, coord_food_guard: bool = False) -> None:
        self.lexicon = lexicon or load_lexicon()
        # D-116 prerequisite (14 Nov): opt-in guard; False reproduces every frozen Rung A output byte for byte.
        self.coord_food_guard = coord_food_guard
        units = sorted(self.lexicon.unit_tokens, key=lambda u: (-len(u), u))
        unit_alt = "|".join(re.escape(u) for u in units) or r"(?!x)x"
        quals = "|".join(QUANTITY_QUALIFIERS)
        self._qty = re.compile(
            rf"(?<![\w/.,]){_NUM}(?:[ \t]*(?:-|–|to|or)[ \t]*{_NUM})?(?:[ \t]*[x×][ \t]*{_NUM})?"
            rf"[ \t]*(?:(?:{quals})[ \t]+)?(?:{unit_alt})(?![^\W\d_])", re.IGNORECASE)
        self._rules = R.recomputers(self.lexicon)

    # ------------------------------------------------------------ configuration
    def config(self, locale: str | None = None) -> StageConfig:
        return StageConfig(rung_id=RUNG_ID, claim_route="INFERRED_RULE", annotated_labels=RUNG_A_LABELS,
                           params={"rules_version": RULES_VERSION, "lexicon_version": LEXICON_VERSION,
                                   "lexicon_fingerprint": self.lexicon.fingerprint, "locale": locale,
                                   "quantity_stage_version": qs.QUANTITY_STAGE_VERSION})

    def _check(self, config: StageConfig) -> None:
        if config.rung_id != RUNG_ID or config.claim_route != "INFERRED_RULE":
            raise InterfaceError("Rung A runs with rung_id A and claim_route INFERRED_RULE only")
        if config.params.get("lexicon_fingerprint") != self.lexicon.fingerprint:
            raise InterfaceError("Configuration names a different lexicon fingerprint")

    def recomputers(self) -> dict[str, R.Recomputer]:
        """Rule id -> recomputer, to register with ``auditor.audit_outputs``."""
        return dict(self._rules)

    # ------------------------------------------------------------ extract_mentions
    def extract_mentions(self, source: SourceText, config: StageConfig) -> MentionSet:
        self._check(config)
        raw = source.raw
        found: list[tuple[int, int, str]] = []
        flags: list[str] = []
        blocked: list[tuple[int, int]] = []

        def take(start: int, end: int, label: str) -> None:
            found.append((start, end, label))
            blocked.append((start, end))

        for m in R.TEMPERATURE_RE.finditer(raw):
            if R.follows_number(raw, m.start()):
                flags.append("TEMPERATURE_COMPLEX_NUMBER")
                continue
            take(m.start(), m.end(), "TEMPERATURE")
        for m in R.DURATION_RE.finditer(raw):
            if _overlaps((m.start(), m.end()), blocked):
                continue
            if R.follows_number(raw, m.start()):
                flags.append("DURATION_COMPLEX_NUMBER")
                continue
            take(m.start(), m.end(), "DURATION")
        for m in R.BARE_CF_RE.finditer(raw):
            if not _overlaps((m.start(), m.end()), blocked):
                flags.append("BARE_TEMPERATURE_UNIT_AMBIGUOUS")
                blocked.append((m.start(), m.end()))
        for m in self._qty.finditer(raw):
            if not _overlaps((m.start(), m.end()), blocked):
                take(m.start(), m.end(), "QUANTITY_IN_STEP")
        for m in R.CONDITION_RE.finditer(raw):
            if not _overlaps((m.start(), m.end()), blocked):
                take(m.start(), m.end(), "CONDITION_CUE")
        endpoints = []
        for m in R.UNTIL_RE.finditer(raw):
            if not _overlaps((m.start(), m.end()), blocked):
                found.append((m.start(), m.end(), "ENDPOINT"))
                endpoints.append((m.start(), m.end()))
        for ss, se in sentences(raw):
            self._tag_tokens(raw, ss, se, blocked, endpoints, found, flags)
        found.sort(key=lambda t: (t[0], -t[1], t[2]))
        mentions = tuple(self._mention(source, f"M{i + 1}", s, e, label, flags)
                         for i, (s, e, label) in enumerate(found))
        return MentionSet(source.text_id, source.sha256, mentions, config.provenance("extract_mentions"),
                          diagnostics=tuple(flags))

    def _tag_tokens(self, raw: str, ss: int, se: int, blocked: list, endpoints: list,
                    found: list, flags: list) -> None:
        toks = [t for t in tokens(raw[ss:se])]
        words = [w for _, _, w in toks]
        lex = self.lexicon
        i = 0
        while i < len(toks):
            s, e = ss + toks[i][0], ss + toks[i][1]
            if _overlaps((s, e), blocked):
                i += 1
                continue
            hit = self._action_at(raw, ss, toks, words, i, endpoints)
            if hit is not None and self.coord_food_guard and self._coordinated_food(raw, toks, words, i, ss, found):
                flags.append("COORD_FOOD_GUARD")
                hit = None
            if hit is not None:
                n, flag = hit
                end = ss + toks[i + n - 1][1]
                found.append((s, end, "ACTION"))
                if flag:
                    flags.append(flag)
                i += n
                continue
            for label, finder in (("TOOL", lex.tool_at), ("FOOD_MENTION", lex.food_at)):
                m = finder(words, i)
                if m is not None and not _overlaps((s, ss + toks[i + m.length - 1][1]), blocked):
                    found.append((s, ss + toks[i + m.length - 1][1], label))
                    if m.flag:
                        flags.append(m.flag)
                    if len(m.ids) > 1:
                        flags.append(f"AMBIGUOUS_{label}")
                    i += m.length
                    break
            else:
                if words[i] in REFERRING:
                    found.append((s, e, "FOOD_MENTION"))
                elif words[i] in MIXTURE_WORDS:
                    found.append((s, e, "INTERMEDIATE_MENTION"))
                i += 1

    def _coordinated_food(self, raw: str, toks: list, words: list[str], i: int, ss: int, found: list) -> bool:
        """A food word right after ',', 'and' or 'or' that follows a FOOD_MENTION in the same list, and is not followed
        by an object word ('salt it', 'oil the pan'), is a list member, not a verb."""
        if self.lexicon.food_at(words, i) is None or not found or found[-1][2] != "FOOD_MENTION":
            return False
        gap = raw[found[-1][1]:ss + toks[i][0]]
        if not _COORD_GAP.fullmatch(gap):
            return False
        nxt = words[i + 1] if i + 1 < len(words) else ""
        return nxt not in _OBJECT_WORDS

    def _action_at(self, raw: str, ss: int, toks: list, words: list[str], i: int,
                   endpoints: list) -> tuple[int, str | None] | None:
        if words[i] in AUX_WORDS:
            return None
        m = self.lexicon.proc_at(words, i)
        if m is None:
            return None
        start = ss + toks[i][0]
        if _overlaps((start, ss + toks[i + m.length - 1][1]), endpoints):
            return None
        prefix = raw[ss:start]
        nouny = words[i] in NOUNY or self.lexicon.food_at(words, i) is not None \
            or self.lexicon.tool_at(words, i) is not None
        if nouny and not _VERB_SLOT.search(prefix):
            return None
        if words[i].endswith("ed") and re.search(r"\bthe\s+$", prefix, re.IGNORECASE):
            return None
        if _NOMINAL_SLOT.search(prefix):
            return None
        if len(m.ids) > 1:
            return m.length, "AMBIGUOUS_ACTION"
        return m.length, m.flag

    def _mention(self, source: SourceText, mid: str, start: int, end: int, label: str, flags: list) -> Mention:
        span = Span.of(source, start, end)
        surface = span.surface
        attrs = []
        if label == "DURATION":
            value, unit, fl = R.duration_values(surface)
            flags.extend(fl)
            attrs.append(R.literal("duration", ValueKind.DURATION, value, span, unit) if value is not None
                         else R.unknown("duration", ValueKind.DURATION, span))
            norm = R.try_rule(self._rules["RA_DURATION_TO_MIN_V1"], surface)
            if norm is not None:
                attrs.append(R.ruled("duration_min", ValueKind.DURATION, norm[0], span, "RA_DURATION_TO_MIN_V1",
                                     norm[1]))
        elif label == "TEMPERATURE":
            value, unit, fl = R.temperature_values(surface)
            flags.extend(fl)
            attrs.append(R.literal("temperature", ValueKind.TEMPERATURE, value, span, unit) if value is not None
                         else R.unknown("temperature", ValueKind.TEMPERATURE, span))
        elif label in ("ACTION", "TOOL"):
            for field, rule, kind in (("proc_id", "RA_PROC_LOOKUP_V1", ValueKind.IDENTIFIER),) if label == "ACTION" \
                    else (("tool_id", "RA_TOOL_LOOKUP_V1", ValueKind.IDENTIFIER),
                          ("structural_class", "RA_TOOL_CLASS_V1", ValueKind.CATEGORICAL)):
                got = R.try_rule(self._rules[rule], surface)
                if got is not None:
                    attrs.append(R.ruled(field, kind, got[0], span, rule))
        return Mention(mid, label, span, tuple(attrs))

    # ------------------------------------------------------------ link
    def link(self, source: SourceText, mention: Mention, config: StageConfig) -> LinkResult:
        self._check(config)
        prov = config.provenance("link")
        snap = self.lexicon.fingerprint
        surface = mention.span.surface
        if mention.label not in LINKABLE:
            return LinkResult(mention.mention_id, mention.span, (), prov, registry_snapshot=snap,
                              failure=Failure(FailureCode.NO_VALID_CANDIDATE, "LABEL_NOT_LINKABLE"))
        if mention.label == "FOOD_MENTION" and surface.lower() in REFERRING:
            return LinkResult(mention.mention_id, mention.span, (), prov, registry_snapshot=snap,
                              failure=Failure(FailureCode.NO_VALID_CANDIDATE, "REFERRING_EXPRESSION"))
        ids = {"FOOD_MENTION": self.lexicon.food_ids, "ACTION": self.lexicon.proc_ids,
               "TOOL": self.lexicon.tool_ids}[mention.label](surface)
        cands = tuple(LinkCandidate(i) for i in sorted(ids))
        if len(cands) == 1:
            return LinkResult(mention.mention_id, mention.span, cands, prov, selected_id=cands[0].concept_id,
                              registry_snapshot=snap)
        failure = Failure(FailureCode.UNRESOLVED, "AMBIGUOUS_CANDIDATES") if cands else \
            Failure(FailureCode.NO_VALID_CANDIDATE, "NO_LEXICON_ENTRY")
        return LinkResult(mention.mention_id, mention.span, cands, prov, failure=failure, registry_snapshot=snap)

    # ------------------------------------------------------------ quantities (rc2)
    def parse_quantity(self, source: SourceText, span: Span, config: StageConfig, *, source_metadata: Mapping,
                       locale: str | None = None) -> QuantityParseResult:
        self._check(config)
        return qs.parse_quantity(source, span, config, source_metadata=source_metadata, locale=locale)

    def ground_quantity(self, source: SourceText, span: Span, context: GroundingContext, config: StageConfig, *,
                        schema: Mapping, result_id: str) -> QuantityGroundingResult:
        self._check(config)
        return qs.ground_quantity(source, span, context, config, schema=schema, result_id=result_id)

    def grounding_context(self, config: StageConfig) -> GroundingContext:
        locale = config.params.get("locale")
        return GroundingContext(source_metadata=QUANTITY_SOURCE_META, locale=locale,
                                locale_metadata=LOCALE_META if locale else None, quantity_scope=QUANTITY_SCOPE)

    # ------------------------------------------------------------ events / references
    def build_events(self, source: SourceText, mentions: MentionSet, links: Sequence[LinkResult],
                     quantities: Sequence[QuantityGroundingResult], config: StageConfig) -> EventGraph:
        self._check(config)
        return build_graph(source, mentions, links, quantities, config, self.lexicon, self._rules)

    def resolve_refs(self, source: SourceText, mentions: MentionSet, graph: EventGraph,
                     config: StageConfig) -> tuple[ReferenceResult, ...]:
        self._check(config)
        return resolve_references(source, mentions, graph, config, self.lexicon)

    # ------------------------------------------------------------ convenience
    def run(self, source: SourceText, config: StageConfig, *, schema: Mapping) -> RungAOutputs:
        """All six stages over one instruction text, in interface order."""
        mentions = self.extract_mentions(source, config)
        links = tuple(self.link(source, m, config) for m in mentions.mentions if m.label in LINKABLE)
        context = self.grounding_context(config)
        quantities = tuple(self.ground_quantity(source, m.span, context, config, schema=schema, result_id=f"Q{k}")
                           for k, m in enumerate((m for m in mentions.mentions if m.label == "QUANTITY_IN_STEP"), 1))
        graph = self.build_events(source, mentions, links, quantities, config)
        refs = self.resolve_refs(source, mentions, graph, config)
        return RungAOutputs(mentions, links, quantities, graph, refs)
