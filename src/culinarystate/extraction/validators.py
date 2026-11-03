"""Step 17a validators V1-V3 (DRAFT_PENDING_16c).

Plan Step 17a names the validators V1 span round-trip, V2 schema, V3 vocabulary
membership and V4 Step-18 invariants (V4 lives in ``invariants``). SSOT §240.1
numbers its stack differently (V1 schema/JSON, V2 ontology/ID, V3
arithmetic/unit/quantity, V4 temporal graph/state); this module follows the Plan
17a labels and the discrepancy is left for human review. Only rules stated in
the sources are checked:

- V1 (RD "Invariants checked in CI" 1; SSOT §240.2): every span round-trips to raw
  offsets of the hashed raw text; every EXPLICIT_SOURCE / EXPLICIT claim has a span.
- V2 (SSOT §240.2): JSON parses and exactly matches the declared schema version;
  record validates against the selected Step 16 draft schema (rc2 through the
  existing ``validate_record``; rc1 through JSON Schema plus the existing review
  overlay).
- V3: categorical codes are members of the draft registries in
  ``registry/recipe_semantics`` (all DRAFT_PENDING_H4), the ALLOC draft enums and
  the SSOT §239.1 provenance classes. A scope with no supplied vocabulary is
  reported as not checked, never as passing.

Validators return reports and never rewrite an output. They read draft files
only and write nothing.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator

from culinarystate.annotation.schema_review import review_record
from culinarystate.quantity.draft_contract import ORIGINS, validate_record

from .interfaces import (
    EventGraph, LinkResult, MentionSet, QuantityGroundingResult, QuantityParseResult, SourceText, Span,
    StageOutput, segment_problem, sha256_text,
)

STATUS = "DRAFT_PENDING_16c"
ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = Path("reports") / "step16" / "schema_drafts"
REGISTRY_DIR = Path("registry") / "recipe_semantics"
VOCAB_FILES = {
    "annotation_mode": "annotation_mode_registry_v1_DRAFT.csv",
    "claim_route": "claim_route_registry_v1_DRAFT.csv",
    "entity_type": "entity_type_registry_v1_DRAFT.csv",
    "event_kind": "event_kind_registry_v1_DRAFT.csv",
    "field_status": "field_status_registry_v1_DRAFT.csv",
    "lifecycle": "lifecycle_registry_v1_DRAFT.csv",
    "modality": "modality_registry_v1_DRAFT.csv",
    "temporal_relation": "temporal_relation_registry_v1_DRAFT.csv",
    "tool_role": "tool_role_registry_v1_DRAFT.csv",
    "transformation_mode": "transformation_mode_registry_v1_DRAFT.csv",
}
# Claim field name (last path segment) -> vocabulary; other categorical fields are not vocabulary-checked.
CLAIM_FIELD_VOCAB = {name: name for name in ("event_kind", "modality", "temporal_relation", "transformation_mode",
                                             "tool_role", "entity_type", "lifecycle")}
_ID_PREFIX = re.compile(r"^([A-Z][A-Z0-9_]*)[-:]")
_DECLARED = re.compile(r"\bschema_version\s+([0-9][^\s,;()]*)")


@dataclass(frozen=True)
class ValidatorIssue:
    validator: str
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """``issues`` fail; ``unknown`` could not be decided; ``not_checked`` names scopes without a vocabulary/rule."""
    validator: str
    issues: tuple[ValidatorIssue, ...] = ()
    unknown: tuple[ValidatorIssue, ...] = ()
    not_checked: tuple[str, ...] = ()

    @property
    def status(self) -> str:
        if self.issues:
            return "FAIL"
        return "UNKNOWN" if self.unknown else "PASS"


class _Collector:
    def __init__(self, validator: str) -> None:
        self.validator = validator
        self.issues: list[ValidatorIssue] = []
        self.unknown: list[ValidatorIssue] = []
        self.not_checked: list[str] = []

    def fail(self, code: str, path: str, message: str) -> None:
        self.issues.append(ValidatorIssue(self.validator, code, path, message))

    def undecided(self, code: str, path: str, message: str) -> None:
        self.unknown.append(ValidatorIssue(self.validator, code, path, message))

    def skip(self, scope: str) -> None:
        if scope not in self.not_checked:
            self.not_checked.append(scope)

    def report(self) -> ValidationReport:
        return ValidationReport(self.validator, tuple(self.issues), tuple(self.unknown), tuple(self.not_checked))


def _outputs(outputs: StageOutput | Iterable[StageOutput]) -> list[StageOutput]:
    return [outputs] if hasattr(outputs, "spans") else list(outputs)


# ------------------------------------------------------------------ V1
def span_issues(source: SourceText, span: Span) -> list[str]:
    """Issue codes for one span against the hashed raw text (empty list = round-trips)."""
    out = []
    if span.text_id != source.text_id:
        out.append("SPAN_TEXT_ID_MISMATCH")
    if span.raw_sha256 != source.sha256:
        out.append("SPAN_RAW_HASH_MISMATCH")
    problem = segment_problem(span.segments, len(source.raw), span.join_policy)
    if problem:
        out.append(problem)
        return out
    if len(span.texts) != len(span.segments):
        out.append("SPAN_TEXT_COUNT")
        return out
    if any(t != source.raw[s:e] for (s, e), t in zip(span.segments, span.texts)):
        out.append("SPAN_TEXT_MISMATCH")
    return out


def v1_span_roundtrip(source: SourceText, outputs: StageOutput | Iterable[StageOutput]) -> ValidationReport:
    """V1: every span equals ``raw[start:end]`` of the hashed raw text; explicit claims carry spans."""
    c = _Collector("V1_SPAN_ROUNDTRIP")
    if source.sha256 != sha256_text(source.raw):
        c.fail("SOURCE_HASH_MISMATCH", "source", "Raw text no longer matches its recorded SHA-256")
    for i, out in enumerate(_outputs(outputs)):
        prefix = f"outputs[{i}]"
        raw_hash = getattr(out, "raw_sha256", None)
        if raw_hash is not None and raw_hash != source.sha256:
            c.fail("OUTPUT_RAW_HASH_MISMATCH", prefix, "Output was produced from a different raw text")
        text_id = getattr(out, "source_text_id", None)
        if text_id is not None and text_id != source.text_id:
            c.fail("OUTPUT_TEXT_ID_MISMATCH", prefix, "Output names a different source text")
        for j, span in enumerate(out.spans()):
            for code in span_issues(source, span):
                c.fail(code, f"{prefix}/spans[{j}]", "Span does not round-trip to the raw text")
        for claim in out.claims():
            if claim.span is None and (claim.origin == "EXPLICIT_SOURCE" or claim.claim_route == "EXPLICIT"):
                c.fail("EXPLICIT_WITHOUT_SPAN", f"{prefix}/{claim.field}", "Every EXPLICIT_SOURCE field needs a span")
        if isinstance(out, QuantityParseResult) and out.expression != out.span.surface:
            c.fail("QUANTITY_EXPRESSION_NOT_SPAN", f"{prefix}/expression", "Parsed expression differs from its span")
        if isinstance(out, QuantityGroundingResult) and out.record is not None \
                and out.record.get("raw") != out.span.surface:
            c.fail("QNT_RAW_NOT_SPAN", f"{prefix}/record/raw", "QNT raw text differs from its span")
    return c.report()


# ------------------------------------------------------------------ V2
def load_draft_schema(name: str, draft: int, *, root: Path | None = None) -> dict:
    """Read ``reports/step16/schema_drafts/<name>.draft_v<draft>.schema.json`` (explicit selection)."""
    path = (root or ROOT) / SCHEMA_DIR / f"{name}.draft_v{draft}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def declared_schema_version(schema: Mapping) -> str | None:
    """rc2: the ``schema_version`` const; rc1: the version stated in the schema description."""
    const = (schema.get("properties") or {}).get("schema_version", {}).get("const")
    if isinstance(const, str):
        return const
    match = _DECLARED.search(str(schema.get("description") or ""))
    return match.group(1) if match else None


def _reject_constant(token: str) -> Any:
    raise ValueError(f"non-finite JSON constant {token}")


def _pointer(parts: Iterable[Any]) -> str:
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def v2_schema(record: Mapping | str, schema: Mapping, *, family_ids: Iterable[str] | None = None) -> ValidationReport:
    """V2: strict JSON, exact declared schema version, then draft schema validation."""
    c = _Collector("V2_SCHEMA")
    if isinstance(record, str):
        try:
            record = json.loads(record, parse_constant=_reject_constant)
        except ValueError as exc:
            c.fail("JSON_PARSE", "", f"JSON does not parse strictly: {exc}")
            return c.report()
    if not isinstance(record, Mapping):
        c.fail("JSON_NOT_OBJECT", "", "A record must be a JSON object")
        return c.report()
    declared = declared_schema_version(schema)
    if declared is None:
        c.fail("SCHEMA_VERSION_UNDECLARED", "/schema_version", "Selected schema declares no version")
        return c.report()
    if "schema_version" not in record:
        c.fail("SCHEMA_VERSION_MISSING", "/schema_version", f"Record must declare schema_version {declared}")
        return c.report()
    if record["schema_version"] != declared:
        c.fail("SCHEMA_VERSION_MISMATCH", "/schema_version", f"Record version differs from declared {declared}")
        return c.report()
    families = set(family_ids) if family_ids is not None else None
    if (schema.get("properties") or {}).get("schema_version", {}).get("const") == "1.0.0-rc2":
        for issue in validate_record(record, schema, family_ids=families):
            c.fail(issue.code, issue.path, issue.message)
        return c.report()
    for err in sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.absolute_path)):
        c.fail("SCHEMA", _pointer(err.absolute_path), err.message)
    for issue in review_record(record, family_ids=families, pointer_paths=True):
        if issue.code == "AST_CONTRACT_PENDING":
            c.undecided(issue.code, issue.path, issue.message)
        else:
            c.fail(issue.code, issue.path, issue.message)
    return c.report()


def v2_quantity_records(results: Iterable[QuantityGroundingResult], schema: Mapping) -> ValidationReport:
    """V2 over the rc2 records of quantity grounding results (paths prefixed by result id)."""
    c = _Collector("V2_SCHEMA")
    for r in results:
        if r.record is None:
            continue
        sub = v2_schema(r.record, schema)
        c.issues.extend(ValidatorIssue(i.validator, i.code, f"{r.result_id}{i.path}", i.message) for i in sub.issues)
        c.unknown.extend(ValidatorIssue(i.validator, i.code, f"{r.result_id}{i.path}", i.message)
                         for i in sub.unknown)
    return c.report()


# ------------------------------------------------------------------ V3
@dataclass(frozen=True)
class Vocabulary:
    name: str
    codes: frozenset[str]
    source: str
    sha256: str | None
    enumerated: bool = True
    statuses: frozenset[str] = frozenset()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_draft_vocabularies(*, root: Path | None = None) -> dict[str, Vocabulary]:
    """Read the draft registries and ALLOC draft enums (read-only)."""
    base = root or ROOT
    out: dict[str, Vocabulary] = {}
    for name, filename in VOCAB_FILES.items():
        path = base / REGISTRY_DIR / filename
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        codes = frozenset(r["code"] for r in rows)
        out[name] = Vocabulary(name, codes, str(REGISTRY_DIR / filename), _file_sha(path),
                               enumerated=codes != frozenset({"OPEN"}),
                               statuses=frozenset(r.get("status", "") for r in rows))
    alloc_path = base / SCHEMA_DIR / "ALLOC.draft_v1.schema.json"
    alloc = json.loads(alloc_path.read_text(encoding="utf-8"))["properties"]
    for name, key in (("alloc_kind", "kind"), ("alloc_basis", "basis")):
        out[name] = Vocabulary(name, frozenset(alloc[key]["enum"]), f"{SCHEMA_DIR / alloc_path.name}#{key}",
                               _file_sha(alloc_path), statuses=frozenset({"DRAFT_PENDING_H4"}))
    out["origin"] = Vocabulary("origin", frozenset(ORIGINS),
                               "culinarystate.quantity.draft_contract.ORIGINS (SSOT §239.1 rule 3)", None)
    return out


def v3_vocabulary(outputs: StageOutput | Iterable[StageOutput], vocabularies: Mapping[str, Vocabulary] | None = None,
                  *, mention_labels: frozenset[str] | None = None,
                  id_sets: Mapping[str, frozenset[str]] | None = None) -> ValidationReport:
    """V3: categorical codes are members of the supplied (default: draft) vocabularies."""
    vocab = dict(vocabularies) if vocabularies is not None else load_draft_vocabularies()
    c = _Collector("V3_VOCABULARY")

    def member(name: str, value: Any, code: str, path: str) -> None:
        v = vocab.get(name)
        if v is None:
            c.skip(f"VOCAB:{name}")
        elif not v.enumerated:
            c.undecided(f"{name.upper()}_REGISTRY_OPEN", path, f"Registry {name} has no enumerated members")
        elif value not in v.codes:
            c.fail(code, path, f"{value!r} is not in vocabulary {name} ({v.source})")

    for i, out in enumerate(_outputs(outputs)):
        prefix = f"outputs[{i}]"
        prov = out.provenance
        member("claim_route", prov.claim_route, "PROVENANCE_CLAIM_ROUTE_NOT_IN_VOCAB", f"{prefix}/provenance")
        if prov.annotation_mode is not None:
            member("annotation_mode", prov.annotation_mode, "ANNOTATION_MODE_NOT_IN_VOCAB", f"{prefix}/provenance")
        for claim in out.claims():
            path = f"{prefix}/{claim.field}"
            member("claim_route", claim.claim_route, "CLAIM_ROUTE_NOT_IN_VOCAB", path)
            member("field_status", claim.status, "CLAIM_STATUS_NOT_IN_VOCAB", path)
            member("origin", claim.origin, "CLAIM_ORIGIN_NOT_IN_VOCAB", path)
            name = CLAIM_FIELD_VOCAB.get(claim.field.rsplit("/", 1)[-1])
            if name is not None and claim.value is not None:
                member(name, claim.value, "VOCAB_MEMBERSHIP", path)
        if isinstance(out, MentionSet):
            _mention_labels(c, out, prefix, mention_labels)
        elif isinstance(out, EventGraph):
            for e in out.events:
                if e.claim_route is not None:
                    member("claim_route", e.claim_route, "EVENT_CLAIM_ROUTE_NOT_IN_VOCAB", f"{prefix}/{e.event_id}")
            for n in out.entities:
                member("entity_type", n.entity_type, "ENTITY_TYPE_NOT_IN_VOCAB", f"{prefix}/{n.entity_id}")
                member("lifecycle", n.lifecycle, "LIFECYCLE_NOT_IN_VOCAB", f"{prefix}/{n.entity_id}")
            for a in out.allocations:
                member("alloc_kind", a.kind, "ALLOC_KIND_NOT_IN_VOCAB", f"{prefix}/{a.alloc_id}")
                member("alloc_basis", a.basis, "ALLOC_BASIS_NOT_IN_VOCAB", f"{prefix}/{a.alloc_id}")
        elif isinstance(out, LinkResult) and out.selected_id is not None:
            match = _ID_PREFIX.match(out.selected_id)
            ns = match.group(1) if match else "UNPREFIXED"
            ids = (id_sets or {}).get(ns)
            if ids is None:
                c.skip(f"LINK_TARGET_IDS:{ns}")
            elif out.selected_id not in ids:
                c.fail("LINK_TARGET_NOT_IN_VOCAB", f"{prefix}/{out.mention_id}/link",
                       f"Selected id is absent from the supplied {ns} id set")
    return c.report()


def _mention_labels(c: _Collector, out: MentionSet, prefix: str, labels: frozenset[str] | None) -> None:
    if not out.mentions:
        return
    if labels is None:
        c.skip("MENTION_LABELS")
    if out.provenance.annotated_labels is None:
        c.skip("ANNOTATED_LABELS_UNDECLARED")
    for m in out.mentions:
        path = f"{prefix}/{m.mention_id}/label"
        if labels is not None and m.label not in labels:
            c.fail("MENTION_LABEL_NOT_IN_VOCAB", path, f"{m.label!r} is not in the supplied mention label set")
        if out.provenance.annotated_labels is not None and m.label not in out.provenance.annotated_labels:
            c.fail("MENTION_LABEL_NOT_ANNOTATED", path, "Producer emitted a label outside its declared coverage")
