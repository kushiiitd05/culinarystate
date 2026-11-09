"""SP-002 pre-normalisation for the rc2 quantity path (S178, T3-C07-R1). DRAFT_PENDING_H4, OPT-IN ONLY.

The legacy grammar reads "1⁄4 tsp" (U+2044 FRACTION SLASH) as a count of 1 with no unit, "1 1⁄2 cups" as a count of 1,
and "1-1/2 cups" as the inverted range 1..1/2 (SP-002; D-069, D-070, D-072). Frozen behaviour is NOT changed here:
``grammar.py``, ``normalize.py``, ``parse_adapter.py``, ``rc2_grounding.py`` and every default are untouched. This module
adds a versioned pre-normaliser and opt-in entry points that call the frozen functions on the normalised text:

    prenormalise(raw)                        -> PreNorm (text, rules fired, refusal)
    parse_quantity_v2_prenorm(raw, ...)      -> ParsedQuantityV2 (raw text preserved)
    ground_quantity_rc2_prenorm(raw, ...)    -> GroundingResult (same contract as ground_quantity_rc2)

Rules (``RULE_IDS``; ``DEFAULT_RULES`` = all three, the D-070/D-072 change set):

  SP002_U2044          U+2044 / U+2215 (DIVISION SLASH) / U+FF0F (FULLWIDTH SOLIDUS) between digits, optionally with
                       blanks around it, becomes "/".      "1⁄4" -> "1/4"; "1 1⁄2" -> "1 1/2"; "1 ⁄ 2" -> "1/2"
  SP002_GLUED_REFUSE   two or more digits glued to the left of such a slash ("11⁄2": 1 1/2 or 11/2?) is ambiguous. The
                       line is REFUSED: UNKNOWN AST with flag AMBIGUOUS_GLUED_FRACTION, never a guess. (An ASCII "11/2"
                       is a legitimate fraction and is NOT touched.)
  SP002_HYPHEN_MIXED   "N-a/b" with N >= 1 and a proper fraction a/b < 1 is a mixed number, not a range ("1-1/2" =
                       1 1/2; D-072). It becomes "N a/b". "1/2-3/4" and "0-1/2" are left alone.

Guarantee (tested, ``tests/unit/test_s178_corpus_prenorm.py``): for any input that contains none of U+2044, U+2215,
U+FF0F and no ``N-a/b`` shape, ``prenormalise`` returns the input unchanged and every opt-in entry point returns exactly
what the frozen function returns (same object for the parse; ``rule_version`` unchanged). The original text always stays
in ``raw`` fields; the pre-normalised text only feeds the frozen parser.

Not covered here (they live in Rung A's span regex ``extraction/rung_a.py::_NUM``, outside the quantity parser): the
D-072 items "a leading unicode fraction must not be cut from the span" and "decimals are never split".

``ground_quantity_rc2_prenorm`` swaps the module-level ``parse_quantity_v2`` binding of ``rc2_grounding`` for the duration
of one call (try/finally). It is process-local and not thread-safe; use it from worker processes, not threads.
"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator

from . import rc2_grounding
from .draft_contract import ContractError, evaluate_ast, metadata_schema
from .grammar import QuantityParse
from .parse_adapter import ADAPTER_VERSION, ParsedQuantityV2, parse_quantity_v2
from .versioned_normalizer import normalize_v2

PRENORM_VERSION = "CQPO_SP002_PRENORM_V1_DRAFT"
RULE_U2044 = "SP002_U2044"
RULE_GLUED = "SP002_GLUED_REFUSE"
RULE_HYPHEN = "SP002_HYPHEN_MIXED"
RULE_IDS = (RULE_U2044, RULE_GLUED, RULE_HYPHEN)
DEFAULT_RULES = RULE_IDS
GLUED_FLAG = "AMBIGUOUS_GLUED_FRACTION"

_SLASHES = "⁄∕／"
_SLASH_CLASS = f"[{_SLASHES}]"
_TRIGGER = re.compile(_SLASH_CLASS)
_SLASH_BETWEEN_DIGITS = re.compile(rf"(?<=\d)[ \t ]*{_SLASH_CLASS}[ \t ]*(?=\d)")
_GLUED = re.compile(rf"(?<![\d./])\d{{2,}}{_SLASH_CLASS}\d")
_HYPHEN_MIXED = re.compile(r"(?<![\d/.\-])(\d+)-(\d+)/(\d+)(?![\d/])")


@dataclass(frozen=True)
class PreNorm:
    """Result of ``prenormalise``: ``text`` equals ``original`` unless a rule fired (``changed``)."""
    original: str
    text: str
    rules_fired: tuple[str, ...] = ()
    refused: bool = False

    @property
    def changed(self) -> bool:
        return self.text != self.original or self.refused


@dataclass(frozen=True)
class PrenormParsed(ParsedQuantityV2):
    """ParsedQuantityV2 plus the pre-normalisation record; only returned when a rule fired."""
    prenorm: PreNorm | None = None


def _check_rules(rules: Iterable[str]) -> tuple[str, ...]:
    rules = tuple(rules)
    unknown = [r for r in rules if r not in RULE_IDS]
    if unknown:
        raise ValueError(f"unknown pre-normalisation rule(s): {unknown}")
    return rules


def _hyphen_sub(m: re.Match) -> str:
    whole, num, den = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if whole >= 1 and den > 0 and num < den:
        return f"{m.group(1)} {m.group(2)}/{m.group(3)}"
    return m.group(0)


def prenormalise(raw: str, rules: Iterable[str] = DEFAULT_RULES) -> PreNorm:
    """Apply the SP-002 rules to one raw quantity line. Pure; the identity for inputs with no trigger."""
    rules = _check_rules(rules)
    if not isinstance(raw, str) or not raw:
        return PreNorm(raw, raw)
    text, fired = raw, []
    has_slash = _TRIGGER.search(text) is not None
    if has_slash:
        if RULE_GLUED in rules and _GLUED.search(text):
            return PreNorm(raw, raw, (RULE_GLUED,), True)
        if RULE_U2044 in rules:
            new = _SLASH_BETWEEN_DIGITS.sub("/", text)
            if new != text:
                text, fired = new, [RULE_U2044]
    if RULE_HYPHEN in rules and "-" in text and "/" in text:
        new = _HYPHEN_MIXED.sub(_hyphen_sub, text)
        if new != text:
            text = new
            fired.append(RULE_HYPHEN)
    return PreNorm(raw, text, tuple(fired))


# ---------------------------------------------------------------- legacy-level view (no rc2)
def parse_line_prenorm(raw: str, rules: Iterable[str] = DEFAULT_RULES):
    """``grammar.parse_line`` on the pre-normalised text; a refused line parses as NONE with ``GLUED_FLAG``.

    ``QuantityParse.raw`` keeps the original text. For an unaffected input this is exactly ``parse_line(raw)``.
    """
    from .grammar import parse_line
    pn = prenormalise(raw, rules)
    if not pn.changed:
        return parse_line(raw)
    if pn.refused:
        return QuantityParse(raw, "NONE", rest=raw, flags=(GLUED_FLAG,))
    p = parse_line(pn.text)
    return dataclasses.replace(p, raw=raw)


# ---------------------------------------------------------------- rc2 adapter level
def _restore_raw(obj: Any, normalised: str, original: str) -> Any:
    """Copy of ``obj`` with every string equal to the normalised text replaced by the original (``raw`` fields)."""
    if isinstance(obj, str):
        return original if obj == normalised else obj
    if isinstance(obj, dict):
        return {k: _restore_raw(v, normalised, original) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_restore_raw(v, normalised, original) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_restore_raw(v, normalised, original) for v in obj)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.replace(obj, **{f.name: _restore_raw(getattr(obj, f.name), normalised, original)
                                           for f in dataclasses.fields(obj)})
    return obj


def _refused_result(raw: str, source_metadata: Mapping, locale: str | None, pn: PreNorm) -> PrenormParsed:
    if list(Draft202012Validator(metadata_schema()).iter_errors(source_metadata)):
        raise ContractError("Explicit valid source metadata is required")
    meta = copy.deepcopy(dict(source_metadata))
    p = QuantityParse(raw, "NONE", rest=raw, flags=(GLUED_FLAG,))
    normalized = normalize_v2(p, locale=locale)
    ast = {"node_type": "UNKNOWN", "raw": raw, "meta": {**meta, "status": "UNKNOWN"}}
    if meta["status"] in {"UNKNOWN", "NOT_APPLICABLE"}:
        ast = {"node_type": "UNKNOWN", "raw": raw, "meta": meta}
    flags = tuple(dict.fromkeys([*normalized.flags, GLUED_FLAG]))
    return PrenormParsed(raw, p, ast, evaluate_ast(ast), normalized, flags,
                         rule_version=f"{ADAPTER_VERSION}+{PRENORM_VERSION}", prenorm=pn)


def parse_quantity_v2_prenorm(raw: str, *, source_metadata: Mapping, locale: str | None = None,
                              rules: Iterable[str] = DEFAULT_RULES) -> ParsedQuantityV2:
    """Opt-in ``parse_quantity_v2`` over the pre-normalised text; raw text preserved in every ``raw`` field.

    No rule fired: returns the frozen function's own result, untouched. A rule fired: the same pipeline on the
    normalised text, ``rule_version`` ``<adapter>+<prenorm>``, flags gain ``PRENORM_<rule>``. REFUSE: UNKNOWN AST.
    """
    pn = prenormalise(raw, rules)
    if not pn.changed:
        return parse_quantity_v2(raw, source_metadata=source_metadata, locale=locale)
    if pn.refused:
        return _refused_result(raw, source_metadata, locale, pn)
    got = parse_quantity_v2(pn.text, source_metadata=source_metadata, locale=locale)
    restored = _restore_raw(got, pn.text, raw)
    flags = tuple(dict.fromkeys([*restored.flags, *(f"PRENORM_{r}" for r in pn.rules_fired)]))
    return PrenormParsed(restored.raw, restored.parsed, restored.ast, restored.arithmetic, restored.normalized, flags,
                         rule_version=f"{ADAPTER_VERSION}+{PRENORM_VERSION}", prenorm=pn)


@contextlib.contextmanager
def _rc2_parser_swapped(rules: tuple[str, ...]):
    original = rc2_grounding.parse_quantity_v2

    def swapped(raw, *, source_metadata, locale=None):
        return parse_quantity_v2_prenorm(raw, source_metadata=source_metadata, locale=locale, rules=rules)

    rc2_grounding.parse_quantity_v2 = swapped
    try:
        yield
    finally:
        rc2_grounding.parse_quantity_v2 = original


def ground_quantity_rc2_prenorm(raw: str, context, *, schema: Mapping, rules: Iterable[str] = DEFAULT_RULES):
    """Opt-in ``ground_quantity_rc2`` over the pre-normalised text (process-local; see module docstring).

    The returned record's ``raw`` is the original text. ``GroundingResult.pipeline_version`` gains ``+<prenorm>`` only
    when a rule fired, so an unaffected line returns exactly what ``ground_quantity_rc2`` returns.
    """
    rules = _check_rules(rules)
    pn = prenormalise(raw, rules)
    if not pn.changed:
        return rc2_grounding.ground_quantity_rc2(raw, context, schema=schema)
    with _rc2_parser_swapped(rules):
        # the frozen pipeline passes the text it is given to the parser; give it the ORIGINAL so record["raw"] and the
        # AST raw stay original, and let the swapped parser normalise it
        res = rc2_grounding.ground_quantity_rc2(raw, context, schema=schema)
    return dataclasses.replace(res, pipeline_version=f"{rc2_grounding.PIPELINE_VERSION}+{PRENORM_VERSION}")
