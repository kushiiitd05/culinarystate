"""Step 17a invented-value auditor for extraction outputs (DRAFT_PENDING_16c).

Plan Step 17 / G17.1 and R-20: invented grams / temperatures / durations / pH = 0.
This auditor flags every numeric or categorical output value that does not trace
to one of:

- a raw source span that round-trips (V1) and literally contains the value
  (``SPAN_LITERAL``; numbers are read with ``numbers_in_text``, the span may
  hold no other number, and a unit, when given, must be a raw unit token inside
  the span: S155 review R1);
- a deterministic rule re-run on the span text by a caller-supplied recomputer
  returning ``(value, unit)`` (``SPAN_RULE``); an unregistered rule is not
  reproducible and counts as invented;
- a supplied candidate set (``CANDIDATE_SELECTION``) or a categorical label on a
  round-tripping span (``REGISTRY_LABEL``; membership is V3's job);
- a grounded rc2 QNT record (``QNT_RECORD``) whose grams pass the existing
  ``rc2_grounding.audit_invented_values`` (Q0 arithmetic or a selected
  HUMAN_VERIFIED POR) and whose AST, parsed values, normalised, volume and count
  channels are reproduced from its raw span by the existing adapter and units.

Grams and millilitres are accepted only through QNT records. Temperatures,
durations and pH are accepted only from spans. UNKNOWN with no value is valid.
Link-candidate scores are model diagnostics and are not audited. The invented
count is the number of distinct output values (output, path) with at least one
invented finding. Reads nothing from disk and writes nothing.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable, Iterable, Mapping

from culinarystate.quantity.draft_contract import ContractError, evaluate_ast
from culinarystate.quantity.parse_adapter import parse_quantity_v2
from culinarystate.quantity.rc2_grounding import audit_invented_values
from culinarystate.quantity.units import BY_KEY

from .interfaces import (
    MAGNITUDE_KINDS, NUMERIC_KINDS, QuantityGroundingResult, QuantityParseResult, SourceText, StageOutput, TraceKind,
    ValueClaim, ValueKind, channel_value,
)
from .validators import span_issues

STATUS = "DRAFT_PENDING_16c"
AUDITOR_VERSION = "STEP17A_INVENTED_VALUE_AUDITOR_V1_DRAFT"
Recomputer = Callable[[str], tuple[Any, "str | None"]]

ALLOWED_TRACES: dict[ValueKind, frozenset[TraceKind]] = {
    ValueKind.CATEGORICAL: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE, TraceKind.CANDIDATE_SELECTION,
                                      TraceKind.REGISTRY_LABEL}),
    ValueKind.IDENTIFIER: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE, TraceKind.CANDIDATE_SELECTION}),
    ValueKind.TEXT: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE}),
    ValueKind.COUNT: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE, TraceKind.QNT_RECORD}),
    ValueKind.FRACTION: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE}),
    ValueKind.OTHER_NUMERIC: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE}),
    ValueKind.MASS_G: frozenset({TraceKind.QNT_RECORD}),
    ValueKind.VOLUME_ML: frozenset({TraceKind.QNT_RECORD}),
    ValueKind.TEMPERATURE: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE}),
    ValueKind.DURATION: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE}),
    ValueKind.PH: frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE}),
}
_QNT_CHANNEL = {ValueKind.MASS_G: "mass_g", ValueKind.VOLUME_ML: "volume_ml", ValueKind.COUNT: "count"}
_SPAN_TRACES = frozenset({TraceKind.SPAN_LITERAL, TraceKind.SPAN_RULE, TraceKind.REGISTRY_LABEL})
_PARSED_KEYS = ("kind", "value", "low", "high", "multiplier", "unit_raw", "size")

VULGAR = {"½": Fraction(1, 2), "⅓": Fraction(1, 3), "⅔": Fraction(2, 3), "¼": Fraction(1, 4), "¾": Fraction(3, 4),
          "⅕": Fraction(1, 5), "⅖": Fraction(2, 5), "⅗": Fraction(3, 5), "⅘": Fraction(4, 5), "⅙": Fraction(1, 6),
          "⅚": Fraction(5, 6), "⅐": Fraction(1, 7), "⅛": Fraction(1, 8), "⅜": Fraction(3, 8), "⅝": Fraction(5, 8),
          "⅞": Fraction(7, 8), "⅑": Fraction(1, 9), "⅒": Fraction(1, 10)}
_V = "[" + "".join(VULGAR) + "]"
_MINUS = "-\u2212"
_NUMBER = re.compile(rf"(?P<mixed>(?P<mi>\d+)[ \t ]+(?P<mn>\d+)[ \t]*/[ \t]*(?P<md>\d+))"
                     rf"|(?P<iv>(?P<ii>\d+)[ \t ]?(?P<iu>{_V}))"
                     rf"|(?P<frac>(?P<fn>\d+)[ \t]*/[ \t]*(?P<fd>\d+))"
                     rf"|(?P<dec>(?P<di>\d+)\.(?P<df>\d+))"
                     rf"|(?P<int>\d+)"
                     rf"|(?P<vul>{_V})")


def _signed(text: str, start: int) -> bool:
    """True when ``text[start-1]`` is an attached minus sign that is not a range dash."""
    if start == 0 or text[start - 1] not in _MINUS:
        return False
    before = text[:start - 1].rstrip()
    return not before or not (before[-1].isdigit() or before[-1] in VULGAR)


def numbers_in_text(text: str) -> frozenset[Fraction]:
    """Exact values of literal numbers in ``text`` (greedy, left to right).

    Reads integers, decimals with a point, a/b, mixed numbers and Unicode vulgar
    fractions (Unicode decimal digits included). Number words and thousands
    separators are not read: such values need a reproducible ``SPAN_RULE``. A
    hyphen-minus or U+2212 attached to a number is a sign unless it follows another
    number (a range dash): "-18°C" reads -18, "20-25" and "1 - 2" read two
    positive numbers (S155 review R2).
    """
    out: set[Fraction] = set()
    for m in _NUMBER.finditer(text):
        sign = -1 if _signed(text, m.start()) else 1
        if m.group("mixed"):
            if int(m.group("md")):
                out.add(sign * (int(m.group("mi")) + Fraction(int(m.group("mn")), int(m.group("md")))))
        elif m.group("iv"):
            out.add(sign * (int(m.group("ii")) + VULGAR[m.group("iu")]))
        elif m.group("frac"):
            if int(m.group("fd")):
                out.add(sign * Fraction(int(m.group("fn")), int(m.group("fd"))))
            else:
                out.update({sign * Fraction(int(m.group("fn"))), Fraction(0)})
        elif m.group("dec"):
            digits = m.group("df")
            out.add(sign * (int(m.group("di")) + Fraction(int(digits), 10 ** len(digits))))
        elif m.group("int"):
            out.add(sign * Fraction(int(m.group("int"))))
        else:
            out.add(sign * VULGAR[m.group("vul")])
    return frozenset(out)


def _exact(v: Any) -> Fraction | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, Fraction)):
        return Fraction(v)
    if isinstance(v, float) and math.isfinite(v):
        return Fraction(str(v))
    return None


def _numbers(value: Any) -> list[Fraction] | None:
    parts = list(value) if isinstance(value, tuple) else [value]
    exact = [_exact(p) for p in parts]
    return None if any(e is None for e in exact) or len(parts) not in (1, 2) else exact


# literal units TEMP_RE emits (group 3 keeps the text's case); the only ones a "deg" prefix may precede
_TEMP_UNITS = frozenset({"C", "F", "c", "f"})


def _unit_token_in(unit: str, surface: str) -> bool:
    """The unit occurs in the span as a whole token (not letters inside a longer word; S155 review R1).

    "º" (U+00BA) is a Unicode letter, but the temperature rule (``evidence.conditions.TEMP_RE``)
    accepts it as a degree marker, so "350ºF" holds the unit token "F" (S161 real-data finding).
    The same rule accepts "deg", "degree(s)" and "deg." written straight before the unit, so
    "350degF" holds the unit token "F" too (S163 real-data finding). As in TEMP_RE, that prefix
    counts only before the temperature units C/F (either case, as written), and the marker itself
    must start a token. The unit is matched case-sensitively against the span text.
    """
    u = re.escape(unit)
    return bool(unit) and (
        re.search(rf"(?:(?<=º)|(?<![^\W\d_])){u}(?![^\W\d_])", surface) is not None
        or (unit in _TEMP_UNITS
            and re.search(rf"(?<![^\W\d_])(?i:deg(?:rees?)?\.?){u}(?![^\W\d_])", surface) is not None))


def _same(kind: ValueKind, a: Any, b: Any) -> bool:
    if kind in NUMERIC_KINDS:
        na, nb = _numbers(a), _numbers(b)
        return na is not None and na == nb
    return a == b


@dataclass(frozen=True)
class AuditFinding:
    code: str
    path: str
    message: str
    invented: bool = True


@dataclass(frozen=True)
class AuditReport:
    findings: tuple[AuditFinding, ...]
    invented_count: int
    values_checked: int
    auditor_version: str = AUDITOR_VERSION

    @property
    def status(self) -> str:
        return "PASS" if self.invented_count == 0 else "FAIL"

    @property
    def invented_by_code(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            if f.invented:
                out[f.code] = out.get(f.code, 0) + 1
        return dict(sorted(out.items()))

    def counts(self) -> dict[str, Any]:
        """Integer counts and code tokens only (no text, ids or values)."""
        return {"invented_count": int(self.invented_count), "values_checked": int(self.values_checked),
                "findings_total": len(self.findings), "invented_by_code": self.invented_by_code}


def audit_claim(claim: ValueClaim, source: SourceText, *, recomputers: Mapping[str, Recomputer] | None = None,
                groundings: Mapping[str, QuantityGroundingResult] | None = None,
                invented_paths: frozenset[str] = frozenset(), path: str | None = None) -> list[AuditFinding]:
    """Audit one claim; returns at most one invented finding (the first failed requirement)."""
    path = path or claim.field

    def bad(code: str, message: str) -> list[AuditFinding]:
        return [AuditFinding(code, path, message)]

    if claim.status in {"UNKNOWN", "NOT_APPLICABLE"}:
        return bad("UNKNOWN_WITH_VALUE", "UNKNOWN value carries a claim") if claim.value is not None else []
    if claim.value is None:
        return [AuditFinding("KNOWN_WITHOUT_VALUE", path, "KNOWN status without a value", invented=False)]
    if any(isinstance(v, float) and not math.isfinite(v)
           for v in (claim.value if isinstance(claim.value, tuple) else (claim.value,))):
        return bad("NONFINITE_VALUE", "NaN/infinity is never a traced value")
    trace = claim.trace
    if trace.kind is TraceKind.NONE:
        return bad("UNTRACED_VALUE", "Value has no trace to a span, rule, candidate set or QNT record")
    if trace.kind not in ALLOWED_TRACES[claim.kind]:
        code = "MAGNITUDE_TRACE_NOT_ALLOWED" if claim.kind in MAGNITUDE_KINDS else "TRACE_KIND_NOT_ALLOWED"
        return bad(code, f"{trace.kind.value} cannot support a {claim.kind.value} value")
    if trace.kind in _SPAN_TRACES:
        if claim.span is None:
            return bad("SPAN_MISSING", "Span-traced value has no span")
        if span_issues(source, claim.span):
            return bad("SPAN_NOT_IN_SOURCE", "Span does not round-trip to the raw text")
    surface = claim.span.surface if claim.span is not None else ""
    if trace.kind is TraceKind.SPAN_LITERAL:
        if claim.kind in NUMERIC_KINDS:
            nums = _numbers(claim.value)
            if nums is None:
                return bad("NUMERIC_VALUE_NOT_A_NUMBER", "Numeric value is not a finite number")
            present = numbers_in_text(surface)
            if any(n not in present for n in nums):
                return bad("NUMERIC_NOT_IN_SPAN", "Number does not appear literally in its span")
            if not present <= set(nums):
                return bad("SPAN_HAS_OTHER_NUMBERS", "Literal span holds other numbers: number/unit pairing is "
                                                     "not decidable (use a tight span or a SPAN_RULE)")
            if claim.unit is not None and not _unit_token_in(claim.unit, surface):
                return bad("UNIT_NOT_IN_SPAN", "Literal unit is not raw text of the span (normalise via SPAN_RULE)")
        elif str(claim.value) != surface:
            return bad("VALUE_NOT_IN_SPAN", "Literal value differs from its span text")
    elif trace.kind is TraceKind.SPAN_RULE:
        if not trace.rule_id:
            return bad("RULE_ID_MISSING", "Rule-traced value names no rule")
        fn = (recomputers or {}).get(trace.rule_id)
        if fn is None:
            return bad("RULE_NOT_REPRODUCIBLE", "Rule is not registered with the auditor")
        try:
            result = fn(surface)
            value, unit = result
        except Exception:  # noqa: BLE001 - any recomputer failure means the value is not reproducible
            return bad("RULE_NOT_REPRODUCIBLE", "Rule failed on the span text")
        if not _same(claim.kind, value, claim.value) or unit != claim.unit:
            return bad("RULE_MISMATCH", "Re-running the rule on the span gives a different value or unit")
    elif trace.kind is TraceKind.CANDIDATE_SELECTION:
        if claim.value not in trace.candidates:
            return bad("SELECTION_OUTSIDE_CANDIDATES", "Selected value is not among the supplied candidates")
    elif trace.kind is TraceKind.QNT_RECORD:
        ref = trace.ref_ids[0] if trace.ref_ids else None
        g = (groundings or {}).get(ref) if ref is not None else None
        if g is None or g.record is None:
            return bad("QNT_REF_MISSING", "Referenced quantity grounding result is not among the audited outputs")
        channel = _QNT_CHANNEL[claim.kind]
        if {f"{ref}/{channel}", f"{ref}/ast", f"{ref}/raw"} & invented_paths:
            return bad("QNT_REF_INVENTED", "Referenced QNT value is itself invented")
        record_channel = g.record.get(channel) or {}
        if channel_value(record_channel) != claim.value or (claim.unit is not None
                                                           and claim.unit != record_channel.get("unit")):
            return bad("QNT_VALUE_MISMATCH", "Value differs from the referenced QNT record")
    return []


def _num(value: Fraction) -> int | float:
    return value.numerator if value.denominator == 1 else float(value)


def _channel(lo: Fraction, hi: Fraction, unit: str) -> dict:
    if lo == hi:
        return {"status": "MEASURED", "value": _num(lo), "unit": unit}
    return {"status": "RANGE", "low": _num(lo), "high": _num(hi), "unit": unit}


def _known(channel: Any) -> bool:
    return isinstance(channel, Mapping) and channel.get("status") in {"MEASURED", "RANGE"}


def _reparse(expression: str, metadata: Any, locale: str | None):
    try:
        return parse_quantity_v2(expression, source_metadata=metadata, locale=locale)
    except (ContractError, TypeError, ValueError):
        return None


def audit_quantity_parse(result: QuantityParseResult, source: SourceText) -> list[AuditFinding]:
    """Re-run the adapter on the span text; the AST must be reproduced exactly."""
    rid = result.result_id
    if span_issues(source, result.span):
        return [AuditFinding("SPAN_NOT_IN_SOURCE", f"{rid}/span", "Quantity span does not round-trip")]
    if result.expression != result.span.surface:
        return [AuditFinding("QPARSE_EXPRESSION_NOT_SPAN", f"{rid}/expression", "Expression differs from its span")]
    again = _reparse(result.expression, result.source_metadata, result.locale)
    if again is None or again.ast != result.ast:
        return [AuditFinding("QPARSE_AST_NOT_REPRODUCIBLE", f"{rid}/ast", "AST is not reproduced from the span")]
    return []


def audit_grounding(result: QuantityGroundingResult, source: SourceText, *,
                    por_records: Iterable[Mapping] = ()) -> list[AuditFinding]:
    """Audit one rc2 QNT record: rc2 gram audit plus Q0 recomputation of the other channels."""
    rid, rec = result.result_id, result.record
    if rec is None:
        return []
    out: list[AuditFinding] = []

    def add(code: str, field: str, message: str) -> None:
        out.append(AuditFinding(code, f"{rid}/{field}", message))

    if span_issues(source, result.span):
        add("SPAN_NOT_IN_SOURCE", "raw", "Quantity span does not round-trip")
        return out
    if rec.get("raw") != result.span.surface:
        add("QNT_RAW_NOT_SPAN", "raw", "QNT raw text differs from its span")
    for issue in audit_invented_values(rec, por_records=por_records):
        add(issue.code, issue.path.lstrip("/") or "mass_g", issue.message)
    again = _reparse(rec.get("raw", ""), (rec.get("field_metadata") or {}).get("/raw"), rec.get("locale"))
    if again is None or again.ast != rec.get("ast"):
        add("QNT_AST_NOT_REPRODUCIBLE", "ast", "AST is not reproduced from the raw span")
    else:
        parsed = rec.get("parsed") or {}
        if any(parsed.get(k) != getattr(again.parsed, k) for k in _PARSED_KEYS):
            add("QNT_PARSED_NOT_REPRODUCIBLE", "parsed", "Parsed values are not reproduced from the raw span")
    try:
        arith = evaluate_ast(rec["ast"]) if rec.get("ast") else None
    except ContractError:
        arith = None
    known = arith is not None and arith.status in {"KNOWN", "RANGE"}
    unit = BY_KEY.get(arith.unit) if known and arith.unit else None
    norm = rec.get("normalized")
    if _known(norm) and (not known or norm != _channel(arith.low, arith.high, arith.unit)):
        add("QNT_NORMALIZED_MISMATCH", "normalized", "Normalised channel differs from AST arithmetic")
    vol = rec.get("volume_ml")
    if _known(vol) and vol != _expected_volume(arith if known else None, unit, rec.get("locale")):
        add("QNT_VOLUME_NOT_Q0", "volume_ml", "Volume is not reproduced by Q0 unit arithmetic")
    count = rec.get("count")
    if _known(count) and count != _expected_count(rec.get("ast"), arith if known else None, unit):
        add("QNT_COUNT_MISMATCH", "count", "Count is not reproduced from the AST")
    return out


def _expected_volume(arith: Any, unit: Any, locale: str | None) -> dict | None:
    if arith is None or unit is None or unit.dimension != "VOLUME":
        return None
    if unit.si:
        factor = Fraction(str(unit.si))
    elif locale in unit.conventions:
        factor = Fraction(str(unit.conventions[locale][0]))
    else:
        return None
    return _channel(arith.low * factor, arith.high * factor, "mL")


def _expected_count(ast: Any, arith: Any, unit: Any) -> dict | None:
    if arith is None:
        return None
    if isinstance(ast, Mapping) and ast.get("node_type") == "PACKAGE_CONTENT" and unit is not None \
            and unit.dimension == "MASS":
        first = ast["children"][0]
        n = Fraction(first["numerator"], first["denominator"])
        return _channel(n, n, "package")
    if arith.unit == "item" or (unit is not None and (unit.dimension == "COUNT" or unit.unit_type == "REGIONAL")):
        return _channel(arith.low, arith.high, arith.unit)
    return None


def audit_outputs(source: SourceText, outputs: Iterable[StageOutput], *, por_records: Iterable[Mapping] = (),
                  recomputers: Mapping[str, Recomputer] | None = None) -> AuditReport:
    """Audit every value of one source text's outputs and count invented values."""
    outs = list(outputs)
    por = list(por_records)
    findings: list[tuple[int, AuditFinding]] = []
    groundings: dict[str, QuantityGroundingResult] = {}
    checked = 0
    for i, out in enumerate(outs):
        if isinstance(out, QuantityGroundingResult):
            if out.result_id in groundings:
                findings.append((i, AuditFinding("DUPLICATE_RESULT_ID", out.result_id,
                                                 "Result id used twice; references are ambiguous", invented=False)))
            else:
                groundings[out.result_id] = out
            for f in audit_grounding(out, source, por_records=por):
                findings.append((i, f))
            checked += len(out.claims())
        elif isinstance(out, QuantityParseResult):
            findings.extend((i, f) for f in audit_quantity_parse(out, source))
            checked += 1
    invented_paths = frozenset(f.path for _, f in findings if f.invented)
    for i, out in enumerate(outs):
        if isinstance(out, (QuantityGroundingResult, QuantityParseResult)):
            continue
        for claim in out.claims():
            checked += 1
            findings.extend((i, f) for f in audit_claim(claim, source, recomputers=recomputers, groundings=groundings,
                                                        invented_paths=invented_paths))
    invented = {(i, f.path) for i, f in findings if f.invented}
    return AuditReport(tuple(f for _, f in findings), len(invented), checked)
