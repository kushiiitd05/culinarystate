"""Step 17b Rung A deterministic rules and their auditor recomputers (DRAFT_PENDING_16c).

Every rule-traced (``SPAN_RULE``) value Rung A emits is produced by one of the
functions below from the raw span text alone, and the same function is
registered with the 17a auditor under its rule id, so the auditor re-runs it and
rejects any mismatch. Rules only read, look up or apply exact definitional unit
factors; none supplies a scientific value:

- ``RA_PROC_LOOKUP_V1`` / ``RA_TOOL_LOOKUP_V1``: span -> the unique PROC / TOOL id
  of the read-only lexicon (an ambiguous or missing surface raises: no value);
- ``RA_EVENT_KIND_V1``: unique PROC family RESTING -> ``WAIT_REST``, else ``ACTION``;
- ``RA_TOOL_CLASS_V1``: unique TOOL id -> its structural class (registry map);
- ``RA_DURATION_TO_MIN_V1``: a duration span in seconds / minutes / hours -> exact
  minutes (1/60, 1, 60); calendar units and decimal commas are not converted;
- ``RA_NUMBER_WORD_V1`` (one..twelve), ``RA_HALF_V1`` (half -> 1/2),
  ``RA_MODALITY_CUE_V1`` (optional cues -> OPTIONAL, negation -> NEGATED) and
  ``RA_UNTIL_V1`` (until -> UNTIL).

Draft choices (cue lists, accepted number forms) need H4 / 16c review.
"""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Callable

from culinarystate.evidence.conditions import DUR_RE, QUAL_HEAT_RE, TEMP_RE

from .interfaces import Span, Trace, TraceKind, ValueClaim, ValueKind
from .rung_a_lexicon import RungALexicon

STATUS = "DRAFT_PENDING_16c"
ROUTE = "INFERRED_RULE"
ORIGIN = "DERIVED_DETERMINISTIC"
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
MINUTE_FACTORS = {"s": Fraction(1, 60), "sec": Fraction(1, 60), "secs": Fraction(1, 60),
                  "second": Fraction(1, 60), "seconds": Fraction(1, 60), "min": Fraction(1), "mins": Fraction(1),
                  "minute": Fraction(1), "minutes": Fraction(1), "h": Fraction(60), "hr": Fraction(60),
                  "hrs": Fraction(60), "hour": Fraction(60), "hours": Fraction(60)}
OPTIONAL_RE = re.compile(r"\b(?:if desired|if you like|if you wish|if preferred|if using|optional(?:ly)?)\b",
                         re.IGNORECASE)
NEGATION_RE = re.compile(r"\b(?:do not|don't|don’t|never)\b", re.IGNORECASE)
UNTIL_RE = re.compile(r"\buntil\b(?:[ \t]+(?!then\b|and then\b)[^\s.;:!?,()]+){1,8}", re.IGNORECASE)
BARE_CF_RE = re.compile(r"(?<![\w./])\d+(?:[.,]\d+)?[ \t]?[CF](?![^\W\d_])")
_COMPLEX_BEFORE = "0123456789/.,½⅓⅔¼¾⅛⅜⅝⅞"
CONDITION_RE = QUAL_HEAT_RE
DURATION_RE = DUR_RE
TEMPERATURE_RE = TEMP_RE

Recomputer = Callable[[str], tuple[Any, "str | None"]]


class RuleNotApplicable(ValueError):
    """The rule gives no value for this span (ambiguous, missing or unsupported)."""


def exact(text: str | None) -> tuple[Fraction | None, str | None]:
    """Exact number for a literal numeral; ``(None, flag)`` when it is not decidable."""
    if text is None:
        return None, None
    t = text.strip()
    if "," in t:
        return None, "DECIMAL_COMMA_UNKNOWN"
    if t[:1] == "–" or re.match(r"^[-−]\s", t):
        return None, "SIGN_NOT_ATTACHED_UNKNOWN"
    t = t.replace("−", "-")
    try:
        return Fraction(t), None
    except (ValueError, ZeroDivisionError):
        return None, "NUMBER_NOT_READ"


def plain(v: Fraction) -> int | Fraction:
    return v.numerator if v.denominator == 1 else v


def interval(lo: Fraction, hi: Fraction | None) -> Any:
    return plain(lo) if hi is None else (plain(lo), plain(hi))


def follows_number(raw: str, start: int) -> bool:
    """True when a numeral match continues an earlier number ("1 1/2 hours", "1/2 hour")."""
    before = raw[:start].rstrip(" \t")
    return bool(before) and before[-1] in _COMPLEX_BEFORE


# ------------------------------------------------------------------ claims
def literal(field: str, kind: ValueKind, value: Any, span: Span, unit: str | None = None) -> ValueClaim:
    return ValueClaim(field, kind, value, origin=ORIGIN, claim_route=ROUTE, span=span,
                      trace=Trace(TraceKind.SPAN_LITERAL), unit=unit)


def ruled(field: str, kind: ValueKind, value: Any, span: Span, rule_id: str, unit: str | None = None) -> ValueClaim:
    return ValueClaim(field, kind, value, origin=ORIGIN, claim_route=ROUTE, span=span,
                      trace=Trace(TraceKind.SPAN_RULE, rule_id=rule_id), unit=unit)


def unknown(field: str, kind: ValueKind, span: Span) -> ValueClaim:
    return ValueClaim(field, kind, None, status="UNKNOWN", origin="UNKNOWN", claim_route=ROUTE, span=span)


def selected(field: str, value: str, span: Span, candidates: tuple[str, ...]) -> ValueClaim:
    return ValueClaim(field, ValueKind.IDENTIFIER, value, origin=ORIGIN, claim_route=ROUTE, span=span,
                      trace=Trace(TraceKind.CANDIDATE_SELECTION, candidates=candidates))


def try_rule(fn: Recomputer, surface: str) -> tuple[Any, str | None] | None:
    try:
        return fn(surface)
    except RuleNotApplicable:
        return None


# ------------------------------------------------------------------ rules
def duration_values(surface: str) -> tuple[Any, str, list[str]]:
    """Literal (value, raw unit, flags) of a duration span; value None when not decidable."""
    m = DURATION_RE.fullmatch(surface.strip())
    if m is None:
        raise RuleNotApplicable("NOT_A_DURATION")
    (lo, f1), (hi, f2) = exact(m.group(1)), exact(m.group(2))
    flags = [f for f in (f1, f2) if f]
    if lo is None or (m.group(2) is not None and hi is None) or (hi is not None and hi < lo):
        return None, m.group(3), flags or ["RANGE_INVERTED_UNKNOWN"]
    return interval(lo, hi), m.group(3), flags


def temperature_values(surface: str) -> tuple[Any, str, list[str]]:
    m = TEMPERATURE_RE.fullmatch(surface.strip())
    if m is None:
        raise RuleNotApplicable("NOT_A_TEMPERATURE")
    (lo, f1), (hi, f2) = exact(m.group(1)), exact(m.group(2))
    flags = [f for f in (f1, f2) if f]
    if lo is None or (m.group(2) is not None and hi is None) or (hi is not None and hi < lo):
        return None, m.group(3), flags or ["RANGE_INVERTED_UNKNOWN"]
    return interval(lo, hi), m.group(3), flags


def duration_to_min(surface: str) -> tuple[Any, str]:
    value, unit, _ = duration_values(surface)
    factor = MINUTE_FACTORS.get(unit.lower())
    if value is None or factor is None:
        raise RuleNotApplicable("NOT_CONVERTIBLE")
    if isinstance(value, tuple):
        return (plain(Fraction(value[0]) * factor), plain(Fraction(value[1]) * factor)), "min"
    return plain(Fraction(value) * factor), "min"


def number_word(surface: str) -> tuple[int, None]:
    n = NUMBER_WORDS.get(surface.strip().lower())
    if n is None:
        raise RuleNotApplicable("NOT_A_NUMBER_WORD")
    return n, None


def half(surface: str) -> tuple[Fraction, None]:
    if surface.strip().lower() != "half":
        raise RuleNotApplicable("NOT_HALF")
    return Fraction(1, 2), None


def modality_cue(surface: str) -> tuple[str, None]:
    if OPTIONAL_RE.fullmatch(surface.strip()):
        return "OPTIONAL", None
    if NEGATION_RE.fullmatch(surface.strip()):
        return "NEGATED", None
    raise RuleNotApplicable("NOT_A_MODALITY_CUE")


def until(surface: str) -> tuple[str, None]:
    if surface.strip().lower() != "until":
        raise RuleNotApplicable("NOT_UNTIL")
    return "UNTIL", None


def _unique(ids: frozenset[str]) -> str:
    if len(ids) != 1:
        raise RuleNotApplicable("AMBIGUOUS_OR_MISSING")
    return next(iter(ids))


def recomputers(lexicon: RungALexicon) -> dict[str, Recomputer]:
    """Rule id -> recomputer over the span text (registered with the 17a auditor)."""
    def proc(surface: str) -> tuple[str, None]:
        return _unique(lexicon.proc_ids(surface)), None

    def tool(surface: str) -> tuple[str, None]:
        return _unique(lexicon.tool_ids(surface)), None

    def tool_class(surface: str) -> tuple[str, None]:
        cls = lexicon.tool_classes.get(_unique(lexicon.tool_ids(surface)))
        if not cls:
            raise RuleNotApplicable("NO_STRUCTURAL_CLASS")
        return cls, None

    def event_kind(surface: str) -> tuple[str, None]:
        info = lexicon.proc_info[_unique(lexicon.proc_ids(surface))]
        return ("WAIT_REST" if info.family == "RESTING" else "ACTION"), None

    return {"RA_PROC_LOOKUP_V1": proc, "RA_TOOL_LOOKUP_V1": tool, "RA_TOOL_CLASS_V1": tool_class,
            "RA_EVENT_KIND_V1": event_kind, "RA_DURATION_TO_MIN_V1": duration_to_min,
            "RA_NUMBER_WORD_V1": number_word, "RA_HALF_V1": half, "RA_MODALITY_CUE_V1": modality_cue,
            "RA_UNTIL_V1": until}
