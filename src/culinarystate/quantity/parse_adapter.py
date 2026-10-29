"""Conservative opt-in bridge from the frozen grammar to the rc2 quantity AST.

Unsupported constructs remain UNKNOWN and carry flags. No metadata is inferred
for the caller, no POR/density is selected, and no ledger/recipe file is read.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from jsonschema import Draft202012Validator

from .draft_contract import ContractError, QuantityResult, evaluate_ast, metadata_schema
from .grammar import APPROX_WORDS, NUM, WORD_COUNT, WORD_NUMBERS, normalize_text, parse_line, QuantityParse
from .units import BY_KEY, lookup
from .versioned_normalizer import NormalizedV2, normalize_v2

ADAPTER_VERSION = "CQPO_PARSE_TO_AST_V2"
LEAD = re.compile(rf"^(?P<a>{NUM})(?:\s*(?P<sep>-|–|to|or)\s*(?P<b>{NUM}))?", re.I)
PACKAGE = re.compile(rf"^(?P<count>\d+)\s*x\s*(?P<size>{NUM})", re.I)
APPROX = re.compile(r"^(?:" + "|".join(re.escape(x) for x in sorted(APPROX_WORDS, key=len, reverse=True)) + r")\s+", re.I)
NUMBER_START = r"(?:\d|" + "|".join(re.escape(w) + r"\b" for w in sorted(set(WORD_COUNT) | set(WORD_NUMBERS), key=len, reverse=True)) + ")"
COMPOUND = re.compile(r"(?:\bplus\b|\band\b|\bminus\b|\btimes\b|\bdivided\s+by\b|\+)\s*" + NUMBER_START, re.I)
REST_OPERATOR = re.compile(r"^\s*(?:[-+×/]|x\b|or\b|and\b|plus\b|minus\b|times\b|divided\b)", re.I)


@dataclass(frozen=True)
class ParsedQuantityV2:
    raw: str
    parsed: QuantityParse
    ast: dict
    arithmetic: QuantityResult
    normalized: NormalizedV2
    flags: tuple[str, ...]
    rule_version: str = ADAPTER_VERSION

    @property
    def requires_review(self):
        return bool(self.flags) or self.arithmetic.status not in {"KNOWN", "RANGE"}


def _fraction(text):
    parts = text.strip().split()
    return sum((Fraction(p) for p in parts), Fraction(0))


def _terminating(value):
    d = value.denominator
    for factor in (2, 5):
        while d % factor == 0:
            d //= factor
    return d == 1


def parse_quantity_v2(raw: str, *, source_metadata: Mapping, locale: str | None = None):
    """Preserve the raw parse, explicit source metadata and distinct normalisation.

    Exact arithmetic results describe the parsed expression only; compatibility
    normalisation channels use the v0 float/unit conventions and are separately
    flagged when precision or unsupported syntax prevents complete integration.
    """
    if list(Draft202012Validator(metadata_schema()).iter_errors(source_metadata)):
        raise ContractError("Explicit valid source metadata is required")
    meta = copy.deepcopy(dict(source_metadata))
    derived = {**copy.deepcopy(meta), "origin": "DERIVED_DETERMINISTIC", "claim_route": "INFERRED_RULE"}
    p = parse_line(raw)
    normalized = normalize_v2(p, locale=locale)
    flags = list(normalized.flags)

    def literal(value, unit, metadata=None):
        return {"node_type": "RATIONAL", "numerator": value.numerator, "denominator": value.denominator,
                "unit": unit, "meta": copy.deepcopy(meta if metadata is None else metadata)}

    def op(kind, *children):
        return {"node_type": kind, "children": list(children), "meta": copy.deepcopy(derived), "raw": raw}

    def missing(reason):
        flags.append(reason)
        return {"node_type": "UNKNOWN", "raw": raw,
                "meta": {**copy.deepcopy(meta), "status": "UNKNOWN"}}

    text = APPROX.sub("", normalize_text(raw))
    lead, package = LEAD.match(text), PACKAGE.match(text)
    remainder = normalize_text(p.rest)
    remainder_words = remainder.split()
    unconsumed_unit = p.unit_key is None and any(lookup(" ".join(remainder_words[:n]))
                           for n in range(1, min(3, len(remainder_words)) + 1))
    ast = None
    if "INVALID_NUMBER" in p.flags or "INVALID_NUMERIC_INPUT" in normalized.flags:
        ast = missing("INVALID_NUMBER")
    elif meta["status"] in {"UNKNOWN", "NOT_APPLICABLE"}:
        ast = {"node_type": "UNKNOWN", "raw": raw, "meta": meta}
    elif re.search(r"\d(?:[\d./ ]*)[x×]\s*\d", text, re.I) and not (p.kind == "MULTIPLIER" and package):
        ast = missing("UNSUPPORTED_MULTIPLIER")
    elif len(re.findall(r"\bor\b", text, re.I)) > 1:
        ast = missing("UNRESOLVED_ALTERNATIVE")
    elif re.search(r"\bor\b", text, re.I) and not (p.kind == "RANGE" and lead and lead["sep"].lower() == "or"):
        ast = missing("UNRESOLVED_ALTERNATIVE")
    elif COMPOUND.search(text) or REST_OPERATOR.match(remainder):
        ast = missing("UNSUPPORTED_COMPOUND_AMOUNT")
    elif unconsumed_unit:
        ast = missing("UNCONSUMED_UNIT")
    elif p.size and re.match(r"\d", p.size):
        ast = missing("SIZE_IS_NOT_QUANTITY")
    elif p.alt or re.search(r"[A-Za-z]\s*/\s*\d", text):
        ast = missing("UNSUPPORTED_DUAL_EXPRESSION")
    elif p.part:
        ast = missing("PART_AMOUNT_UNGROUNDED")
    elif p.kind == "QUALITATIVE":
        ast = {"node_type": "QUALITATIVE", "raw": raw, "meta": meta}
    elif p.kind == "MULTIPLIER" and package and p.package_size:
        ast = op("PACKAGE_CONTENT", literal(_fraction(package["count"]), "1"),
                 literal(_fraction(package["size"]), p.package_size[1]))
    elif p.kind == "PACKAGE" and lead and p.package_size:
        ast = op("PACKAGE_CONTENT", literal(Fraction(1), "1", derived),
                 literal(_fraction(lead["a"]), p.package_size[1]))
    elif lead and p.kind == "RANGE" and lead["b"]:
        a, b = _fraction(lead["a"]), _fraction(lead["b"])
        unit = p.unit_key or "item"
        if lead["sep"].lower() == "or":
            ast = op("ALTERNATIVE", literal(a, unit), literal(b, unit))
        elif not _terminating(a) or not _terminating(b):
            ast = missing("NONTERMINATING_RANGE_BOUND")
        else:
            lo = a.numerator if a.denominator == 1 else float(a)
            hi = b.numerator if b.denominator == 1 else float(b)
            if Fraction(str(lo)) != a or Fraction(str(hi)) != b:
                ast = missing("BOUND_FLOAT_PRECISION_LIMIT")
            else:
                ast = {"node_type": "RANGE", "low": lo, "high": hi, "unit": unit, "raw": raw, "meta": meta}
    elif lead and p.kind in {"NUMBER", "FRACTION", "MIXED"}:
        amount = _fraction(lead["a"])
        if not _terminating(amount):
            flags.append("NORMALIZATION_FLOAT_PRECISION_LIMIT")
        ast = literal(amount, p.unit_key or "item")
    elif p.kind == "NUMBER" and p.value is not None:
        words = {**WORD_COUNT, **WORD_NUMBERS}
        word = next((w for w in sorted(words, key=len, reverse=True)
                     if text.casefold().startswith(w + " ")), None)
        if word and words[word] is not None:
            ast = literal(Fraction(str(words[word])), p.unit_key or "item")
    if ast is None:
        ast = missing("UNSUPPORTED_OR_UNSTATED_QUANTITY")
    if p.stated:
        flags.append("PARENTHETICAL_EXPRESSION_SEPARATE")
    if any(x in p.qualifiers for x in ("heaped", "rounded", "scant", "generous", "good")):
        flags.append("QUALIFIED_FILL_UNCERTAINTY")
    if "about" in p.qualifiers or any(re.search(r"\b" + re.escape(w.rstrip('.')) + r"\b", text, re.I)
                                         for w in APPROX_WORDS):
        flags.append("APPROXIMATE_SOURCE_AMOUNT")
    if "plus extra" in p.qualifiers and ast["node_type"] != "UNKNOWN":
        ast = op("ADD", ast, {"node_type": "OPEN_AMOUNT", "raw": "plus extra", "meta": meta})
        flags.append("OPEN_EXTRA_AMOUNT")
    ast.setdefault("raw", raw)
    arithmetic = evaluate_ast(ast)
    unit = BY_KEY.get(arithmetic.unit)
    channel, factor = None, None
    if unit and unit.si is not None and unit.dimension in {"MASS", "VOLUME"}:
        channel = normalized.mass_g if unit.dimension == "MASS" else normalized.volume_ml
        factor = Fraction(str(unit.si))
    elif arithmetic.unit == "item":
        channel, factor = normalized.count, Fraction(1)
    if channel is not None and arithmetic.status in {"KNOWN", "RANGE"}:
        actual = (channel.get("value"), channel.get("value")) if channel["status"] == "MEASURED" else (channel.get("low"), channel.get("high"))
        expected = (arithmetic.low * factor, arithmetic.high * factor)
        if all(v is not None for v in actual) and any(Fraction(str(v)) != e for v, e in zip(actual, expected)):
            flags.append("NORMALIZATION_FLOAT_PRECISION_LIMIT")
    return ParsedQuantityV2(raw, p, ast, arithmetic, normalized, tuple(dict.fromkeys(flags)))
