"""Step 17a quantity stages over the S154 rc2 pipeline (DRAFT_PENDING_16c).

``parse_quantity`` wraps ``parse_adapter.parse_quantity_v2`` and ``ground_quantity``
wraps ``rc2_grounding.ground_quantity_rc2``. Nothing is reimplemented: no
arithmetic, unit resolution, locale choice or POR selection happens here. These
functions only (1) check that the span belongs to the source text, (2) pass the
span's raw surface unchanged, and (3) turn the pipeline's outcome into the common
interface result with an explicit ``Failure`` when no mass is grounded.

``ContractError`` from the pipeline (non-rc2 schema, blank text, locale or
ingredient link without metadata, invalid source metadata) is caller misuse and
propagates. The route -> failure map is a draft choice (needs H4 / 16c review).
"""
from __future__ import annotations

import copy
from typing import Mapping

from culinarystate.quantity.parse_adapter import parse_quantity_v2
from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2

from .interfaces import (
    Failure, FailureCode, InterfaceError, QuantityGroundingResult, QuantityParseResult, SourceText, Span,
    StageConfig, segment_problem,
)

QUANTITY_STAGE_VERSION = "STEP17A_QUANTITY_STAGES_V1_DRAFT"

# rc2 mass_route -> failure code when no mass is grounded (draft mapping).
GROUNDING_FAILURE_MAP: dict[str, FailureCode] = {
    "NO_COMPATIBLE_RECORD": FailureCode.NO_COMPATIBLE_RECORD,
    "UNSUPPORTED_EXPRESSION": FailureCode.PARSE_FAIL,
    "NO_QUANTITY": FailureCode.PARSE_FAIL,
    "AMBIGUOUS_POR_RECORDS": FailureCode.UNRESOLVED,
    "POR_Q_LEVEL_RULING_PENDING": FailureCode.UNRESOLVED,
    "NO_INGREDIENT_LINK": FailureCode.UNRESOLVED,
    "UNIT_ID_UNMAPPED": FailureCode.UNRESOLVED,
    "QUALITATIVE": FailureCode.UNRESOLVED,
    "ALTERNATIVE": FailureCode.UNRESOLVED,
    "OPEN_OR_UNAVAILABLE_OPERAND": FailureCode.UNRESOLVED,
    "NONE": FailureCode.UNRESOLVED,
}


def failure_for_route(mass_route: str, detail: tuple[str, ...] = ()) -> Failure:
    """Explicit failure for a non-grounded rc2 route; unknown routes stay UNRESOLVED."""
    return Failure(GROUNDING_FAILURE_MAP.get(mass_route, FailureCode.UNRESOLVED), mass_route or "NONE", detail)


def require_span_of(source: SourceText, span: Span) -> str:
    """Return the span's raw surface after checking it round-trips into ``source``."""
    if span.text_id != source.text_id or span.raw_sha256 != source.sha256:
        raise InterfaceError("Span does not belong to this source text")
    problem = segment_problem(span.segments, len(source.raw), span.join_policy)
    if problem:
        raise InterfaceError(problem)
    if len(span.segments) != 1:
        raise InterfaceError("Quantity stages take one contiguous raw segment")
    start, end = span.segments[0]
    if span.texts != (source.raw[start:end],):
        raise InterfaceError("SPAN_TEXT_MISMATCH: span text differs from the raw slice")
    return source.raw[start:end]


def _default_id(kind: str, span: Span) -> str:
    return f"{kind}:{span.char_start}-{span.char_end}"


def parse_quantity(source: SourceText, span: Span, config: StageConfig, *, source_metadata: Mapping,
                   locale: str | None = None, result_id: str | None = None) -> QuantityParseResult:
    """Parse one raw quantity expression with the rc2 adapter. An UNKNOWN AST is PARSE_FAIL."""
    expression = require_span_of(source, span)
    parsed = parse_quantity_v2(expression, source_metadata=source_metadata, locale=locale)
    failure = None
    if parsed.ast.get("node_type") == "UNKNOWN":
        failure = Failure(FailureCode.PARSE_FAIL, "AST_UNKNOWN", tuple(parsed.flags))
    return QuantityParseResult(
        result_id=result_id or _default_id("parse", span), span=span, expression=expression,
        source_metadata=copy.deepcopy(dict(source_metadata)), provenance=config.provenance("parse_quantity"),
        ast=copy.deepcopy(parsed.ast), arithmetic_status=parsed.arithmetic.status, flags=tuple(parsed.flags),
        adapter_version=parsed.rule_version, locale=locale, failure=failure, parsed=parsed)


def ground_quantity(source: SourceText, span: Span, context: GroundingContext, config: StageConfig, *,
                    schema: Mapping, result_id: str) -> QuantityGroundingResult:
    """Ground one raw quantity expression with ``ground_quantity_rc2``; never writes anything."""
    expression = require_span_of(source, span)
    grounding = ground_quantity_rc2(expression, context, schema=schema)
    failure = None
    if grounding.exact_mass is None:
        failure = failure_for_route(grounding.mass_route, tuple(grounding.flags))
    return QuantityGroundingResult(result_id=result_id, span=span, provenance=config.provenance("ground_quantity"),
                                   record=grounding.record, grounding=grounding, failure=failure)
