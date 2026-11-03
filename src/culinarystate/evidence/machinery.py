"""Step 09 evidence extraction/verification machinery (S157). Status: PROVISIONAL_PENDING_09_GATE.

Consolidates the pre-spine prototypes (``precheck.py`` rule checks, ``link_review.py`` human sign-off
rule, ``tools/apply_human_review.py`` verifier rule, the ranked verification queue) into one tested
module. Nothing here is a gate result; G09-1..7 are not evaluated; no ledger is read or written.

Laws applied (CLAUDE.md, D-045, card STEP 09)
- An extractor (AI model, rule or a human doing single extraction) only PROPOSES a field value with an
  exact locator (span / table cell / figure). Raw text is preserved; normalisation is a new column.
- Deterministic field-class validators only FLAG; they never correct, default or invent a value.
  A value must occur literally in the cited span (seeded fabricated values are caught).
- A queue item's verification status has no setter and no constructor argument. It is derived by
  ``_derive_status`` from one ``HumanReview`` whose reviewer is a named human (Kush, Parv; AI names
  and the worker labels "ksh"/"prv" are refused). Reviews enter only through ``read_human_reviews``
  (a human-filled CSV, hashed) and ``write_queue_jsonl`` re-reads that file and refuses any review
  that is not present in it byte-for-byte. There is no sign-as / bulk-fill entry point.
- No E5 -> E4 promotion happens here. ``evidence_tier_candidate`` can at most say
  ``E4_ELIGIBLE_PENDING_ADJ`` (dual extraction + blind human confirmation with a checked locator);
  the ADJ record and the promotion itself belong to the approved 09.1 schemas, which do not exist yet.
- Span text is hashed, never stored, so a queue file carries no third-party passage.

Layout: field classes, locators, proposals and validators live in ``extraction_fields`` (no review
or status code there) and are re-exported here, so ``machinery`` is the single import surface.

PROPOSED (AI choices awaiting the 09 gate / Kush and Parv): the critical-class marks, the scientific
unit vocabulary, the prompt-injection patterns and the E4-eligibility rule (blind only; see D-045 W2).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from culinarystate.evidence.extraction_fields import (  # noqa: F401  (re-exported public surface)
    ABSENT_TOKENS,
    CRITICAL_FIELD_CLASSES,
    CRITICAL_STATUS,
    DISPERSION_TYPES,
    EXTRACTOR_KINDS,
    FIELD_CLASSES,
    K_LEVELS,
    KINETIC_PARAMETERS,
    LOCATOR_KINDS,
    MACHINERY_VERSION,
    ROOT,
    STATUS,
    FieldClassSpec,
    Locator,
    MachineryError,
    Proposal,
    check_percent_change,
    check_retention_arithmetic,
    normalise_value,
    prompt_injection_flags,
    validate_proposal,
)
from culinarystate.ledgers.common import HUMANS
from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target

DECISIONS = ("CONFIRM", "REJECT", "CORRECT", "UNSURE")
REVIEW_MODES = ("INDEPENDENT_BLIND", "AI_ASSISTED", "JOINT")
VERIFICATION_STATUSES = ("UNVERIFIED", "AI_PROPOSED", "HUMAN_VERIFIED", "HUMAN_REJECTED",
                         "HUMAN_CORRECTED_PENDING_REEXTRACTION", "HUMAN_UNSURE")
TIER_CANDIDATES = ("E5", "E4_ELIGIBLE_PENDING_ADJ")
AI_NAME = re.compile(r"(claude|gpt|llm|gemini|agent|\bai\b|bot|model|anthropic|openai)", re.IGNORECASE)
BLOCKING_FLAGS = frozenset({"VALUE_NOT_IN_SPAN", "NO_SPAN_TEXT", "PROMPT_INJECTION_SUSPECTED",
                            "EXTRACTOR_DISAGREEMENT"})

# ---------------------------------------------------------------- human review (read from a human file only)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?)?$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class HumanReview:
    reviewer: str
    reviewed_at: str
    decision: str
    review_mode: str
    seen_model_output: bool
    review_source_sha256: str
    checked_locator: str | None = None
    corrected_raw_value: str | None = None
    minutes: int | None = None
    queue_item_id: str | None = None

    def __post_init__(self) -> None:
        who = str(self.reviewer or "")
        if who not in HUMANS or AI_NAME.search(who):
            raise MachineryError(f"reviewer must be a named human in {sorted(HUMANS)}; AI review is not verification")
        if not _DATE.match(str(self.reviewed_at or "")):
            raise MachineryError("reviewed_at must be an ISO date")
        if self.decision not in DECISIONS:
            raise MachineryError(f"decision must be one of {DECISIONS}")
        if self.review_mode not in REVIEW_MODES:
            raise MachineryError(f"review_mode must be one of {REVIEW_MODES}")
        if not isinstance(self.seen_model_output, bool):
            raise MachineryError("seen_model_output must be a bool")
        if self.review_mode == "INDEPENDENT_BLIND" and self.seen_model_output:
            raise MachineryError("an INDEPENDENT_BLIND review cannot have seen model output")
        if not _HEX64.match(str(self.review_source_sha256 or "")):
            raise MachineryError("review_source_sha256 must be the sha256 of the human review file")
        if self.decision == "CONFIRM" and not str(self.checked_locator or "").strip():
            raise MachineryError("CONFIRM needs the locator the human checked")
        if self.decision == "CORRECT" and not str(self.corrected_raw_value or "").strip():
            raise MachineryError("CORRECT needs the corrected raw value")
        if self.minutes is not None and (not isinstance(self.minutes, int) or self.minutes < 0):
            raise MachineryError("minutes must be a non-negative integer")

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in ("reviewer", "reviewed_at", "decision", "review_mode",
                                              "seen_model_output", "review_source_sha256", "checked_locator",
                                              "corrected_raw_value", "minutes", "queue_item_id")}

    def comparable(self) -> dict:
        d = self.to_dict()
        d.pop("queue_item_id")
        return d


HUMAN_COLUMNS = ("human_decision", "reviewer", "reviewed_at", "review_mode", "seen_model_output",
                 "checked_locator", "corrected_raw_value", "minutes")
REVIEW_SHEET_COLUMNS = ("queue_item_id", "document_id", "field_class", "locator", "proposed_values", *HUMAN_COLUMNS)
_BOOL = {"true": True, "yes": True, "1": True, "false": False, "no": False, "0": False}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_human_reviews(path: Path | str) -> tuple[dict[str, HumanReview], list[str]]:
    """Human-filled review sheet -> reviews by queue item id, plus row errors (invalid rows are not reviews)."""
    p = Path(path)
    sha = _sha256_file(p)
    reviews: dict[str, HumanReview] = {}
    errors: list[str] = []
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = {"queue_item_id", *HUMAN_COLUMNS} - set(reader.fieldnames or ())
        if missing:
            raise MachineryError(f"review sheet lacks columns {sorted(missing)}")
        for n, row in enumerate(reader, start=2):
            if not (row.get("human_decision") or "").strip():
                continue
            qid = (row.get("queue_item_id") or "").strip()
            try:
                seen = _BOOL.get((row.get("seen_model_output") or "").strip().lower())
                if seen is None:
                    raise MachineryError("seen_model_output must be true/false")
                mins = (row.get("minutes") or "").strip()
                if mins and not mins.isdigit():
                    raise MachineryError("minutes must be a non-negative integer")
                rv = HumanReview(reviewer=(row.get("reviewer") or "").strip(),
                                 reviewed_at=(row.get("reviewed_at") or "").strip(),
                                 decision=(row.get("human_decision") or "").strip().upper(),
                                 review_mode=(row.get("review_mode") or "").strip().upper(), seen_model_output=seen,
                                 review_source_sha256=sha,
                                 checked_locator=(row.get("checked_locator") or "").strip() or None,
                                 corrected_raw_value=(row.get("corrected_raw_value") or "").strip() or None,
                                 minutes=int(mins) if mins else None, queue_item_id=qid or None)
                if not qid:
                    raise MachineryError("queue_item_id is required")
                if qid in reviews:
                    raise MachineryError(f"duplicate review for {qid}")
            except MachineryError as e:
                errors.append(f"row {n}: {e}")
                continue
            reviews[qid] = rv
    return reviews, errors


# ---------------------------------------------------------------- queue items
def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _compare_key(norm: dict) -> str:
    for k in ("value_K", "value_s", "value", "censoring"):
        if k in norm:
            return str(norm[k])
    return " ".join(str(norm.get("raw", "")).split()).casefold()


@dataclass(frozen=True)
class QueueItem:
    document_id: str
    field_class: str
    proposals: tuple[Proposal, ...]
    span_sha256: str | None
    proposal_flags: tuple[tuple[str, ...], ...]
    normalised: tuple[Mapping[str, Any], ...]
    flags: tuple[str, ...]
    licence_status: str = "UNKNOWN"
    human_review: HumanReview | None = None

    @classmethod
    def build(cls, proposals: Sequence[Proposal], *, span_text: str | None,
              licence_status: str = "UNKNOWN") -> QueueItem:
        props = tuple(proposals)
        if not props or not all(isinstance(p, Proposal) for p in props):
            raise MachineryError("a queue item needs at least one Proposal")
        if len({p.field_class for p in props}) != 1 or len({p.locator.document_id for p in props}) != 1:
            raise MachineryError("proposals of one item share field class and document")
        if len({p.extractor_id for p in props}) != len(props):
            raise MachineryError("one proposal per extractor")
        pflags = tuple(validate_proposal(p, span_text) for p in props)
        norms = tuple(normalise_value(p) for p in props)
        flags = sorted({f for fs in pflags for f in fs})
        if len({_compare_key(n) for n in norms}) > 1:
            flags.append("EXTRACTOR_DISAGREEMENT")
        span_sha = None if span_text is None else hashlib.sha256(span_text.encode("utf-8")).hexdigest()
        return cls(props[0].locator.document_id, props[0].field_class, props, span_sha, pflags, norms,
                   tuple(sorted(set(flags))), licence_status)

    def _identity(self) -> dict:
        return {"document_id": self.document_id, "field_class": self.field_class, "span_sha256": self.span_sha256,
                "licence_status": self.licence_status, "proposals": [p.to_dict() for p in self.proposals]}

    @property
    def queue_item_id(self) -> str:
        return "vq:" + hashlib.sha256(_canonical(self._identity()).encode("utf-8")).hexdigest()[:16]

    @property
    def verification_status(self) -> str:
        return _derive_status(self)

    @property
    def evidence_tier_candidate(self) -> str:
        return _tier_candidate(self)

    def with_human_review(self, review: HumanReview) -> QueueItem:
        if not isinstance(review, HumanReview):
            raise MachineryError("with_human_review takes a HumanReview read from a human review file")
        if self.human_review is not None:
            raise MachineryError("item already carries a human review; a new review is a new queue version")
        if review.queue_item_id is not None and review.queue_item_id != self.queue_item_id:
            raise MachineryError("review belongs to another queue item")
        return replace(self, human_review=replace(review, queue_item_id=self.queue_item_id))

    def to_dict(self) -> dict:
        props = [{**p.to_dict(), "flags": list(f), "normalised": dict(n)}
                 for p, f, n in zip(self.proposals, self.proposal_flags, self.normalised)]
        return {"record": "VERIFICATION_QUEUE_ITEM", "status": STATUS, "machinery_version": MACHINERY_VERSION,
                "queue_item_id": self.queue_item_id, "document_id": self.document_id, "field_class": self.field_class,
                "critical": self.field_class in CRITICAL_FIELD_CLASSES, "span_sha256": self.span_sha256,
                "licence_status": self.licence_status, "proposals": props, "flags": list(self.flags),
                "human_review": None if self.human_review is None else self.human_review.to_dict(),
                "verification_status": self.verification_status,
                "evidence_tier_candidate": self.evidence_tier_candidate}

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> QueueItem:
        try:
            props = tuple(Proposal(field_class=p["field_class"], raw_value=p["raw_value"],
                                   extractor_id=p["extractor_id"],
                                   extractor_kind=p["extractor_kind"], locator=Locator(**p["locator"]),
                                   attributes=p.get("attributes") or {}) for p in d["proposals"])
            rv = d.get("human_review")
            item = cls(d["document_id"], d["field_class"], props, d.get("span_sha256"),
                       tuple(tuple(p.get("flags") or ()) for p in d["proposals"]),
                       tuple(dict(p.get("normalised") or {}) for p in d["proposals"]), tuple(d.get("flags") or ()),
                       d.get("licence_status", "UNKNOWN"), None if rv is None else HumanReview(**rv))
        except (KeyError, TypeError) as e:
            raise MachineryError(f"malformed queue item: {e}") from e
        if d.get("queue_item_id") != item.queue_item_id:
            raise MachineryError("queue_item_id does not match the item content")
        if d.get("verification_status") != item.verification_status:
            raise MachineryError("stored verification_status differs from the status derived from the human review")
        if d.get("evidence_tier_candidate") != item.evidence_tier_candidate:
            raise MachineryError("stored evidence_tier_candidate differs from the derived one")
        return item


def _derive_status(item: QueueItem) -> str:
    """The ONLY place a human status is named: it is read off a HumanReview, never chosen by code."""
    rv = item.human_review
    if rv is None:
        return "AI_PROPOSED" if any(p.extractor_kind == "AI_MODEL" for p in item.proposals) else "UNVERIFIED"
    return {"CONFIRM": "HUMAN_VERIFIED", "REJECT": "HUMAN_REJECTED",
            "CORRECT": "HUMAN_CORRECTED_PENDING_REEXTRACTION", "UNSURE": "HUMAN_UNSURE"}[rv.decision]


def _tier_candidate(item: QueueItem) -> str:
    rv = item.human_review
    if (rv is None or rv.decision != "CONFIRM" or rv.review_mode != "INDEPENDENT_BLIND" or rv.seen_model_output
            or not rv.checked_locator or len({p.family for p in item.proposals}) < 2
            or BLOCKING_FLAGS & set(item.flags)):
        return "E5"
    return "E4_ELIGIBLE_PENDING_ADJ"


# ---------------------------------------------------------------- writers
_PROTECTED = (("ledgers",), ("exports",), ("annotation", "gold"))
_LEDGER_NAMES = frozenset(f"{n}.JSONL" for n in ("EVD", "XTR", "ADJ", "KIN", "KINPT", "OBS", "SEXP", "SMP", "DOC",
                                                 "LIN", "SRC", "SNAP", "COND", "MEAS", "STUDY", "_IDS", "AGG", "DRV"))


def guard_output_path(path: Path | str, *, root: Path = ROOT) -> Path:
    target = Path(path).resolve()
    if target.name.upper() in _LEDGER_NAMES:
        raise MachineryError("refusing a file named like a ledger")
    try:
        parts = tuple(x.casefold() for x in target.relative_to(Path(root).resolve()).parts)
    except ValueError:
        parts = ()
    if any(parts[:len(p)] == p for p in _PROTECTED):
        raise MachineryError("refusing to write inside ledgers/, exports/ or annotation/gold/")
    try:
        assert_safe_write_target(target)
    except ProtectedPathError as e:
        raise MachineryError(str(e)) from e
    if target.exists():
        raise MachineryError("refusing to overwrite an existing file")
    return target


def _check_reviews_against_files(items: Sequence[QueueItem], review_files: Sequence[Path | str]) -> None:
    by_sha: dict[str, dict[str, HumanReview]] = {}
    for f in review_files:
        by_sha[_sha256_file(Path(f))] = read_human_reviews(f)[0]
    for it in items:
        rv = it.human_review
        if rv is None:
            continue
        src = by_sha.get(rv.review_source_sha256)
        if src is None:
            raise MachineryError(f"{it.queue_item_id}: human review file sha256 {rv.review_source_sha256[:12]} not given")
        rec = src.get(it.queue_item_id)
        if rec is None or rec.comparable() != rv.comparable():
            raise MachineryError(f"{it.queue_item_id}: review differs from the human review file")


def write_queue_jsonl(items: Iterable[QueueItem], path: Path | str, *, root: Path = ROOT,
                      review_files: Sequence[Path | str] = ()) -> Path:
    """Header + one canonical line per item to a new file; every human review must match its human file."""
    items = list(items)
    if not all(isinstance(i, QueueItem) for i in items):
        raise MachineryError("write_queue_jsonl takes QueueItem instances")
    ids = [i.queue_item_id for i in items]
    if len(ids) != len(set(ids)):
        raise MachineryError("duplicate queue items")
    target = guard_output_path(path, root=root)
    _check_reviews_against_files(items, review_files)
    counts: dict[str, int] = {}
    for i in items:
        counts[i.verification_status] = counts.get(i.verification_status, 0) + 1
    head = {"record": "VERIFICATION_QUEUE_HEADER", "status": STATUS, "machinery_version": MACHINERY_VERSION,
            "count": len(items), "status_counts": dict(sorted(counts.items())), "statuses_set_by_code": 0}
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="utf-8", newline="\n") as fh:
        fh.writelines(_canonical(rec) + "\n" for rec in (head, *(i.to_dict() for i in items)))
    return target


def write_review_sheet(items: Iterable[QueueItem], path: Path | str, *, root: Path = ROOT, blind: bool = True) -> Path:
    """Review sheet with every human column blank. ``blind`` hides the proposed values (INDEPENDENT_BLIND)."""
    target = guard_output_path(path, root=root)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(REVIEW_SHEET_COLUMNS))
        w.writeheader()
        for it in items:
            loc = it.proposals[0].locator.to_dict()
            w.writerow({"queue_item_id": it.queue_item_id, "document_id": it.document_id, "field_class": it.field_class,
                        "locator": _canonical({k: v for k, v in loc.items() if v is not None}),
                        "proposed_values": "HIDDEN_BLIND" if blind else " | ".join(p.raw_value for p in it.proposals),
                        **{c: "" for c in HUMAN_COLUMNS}})
    return target


# ---------------------------------------------------------------- JSON schema of a queue item
_STR = {"type": "string"}
_OPT_STR = {"type": ["string", "null"]}
QUEUE_ITEM_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "culinarystate/provisional/evidence_verification_queue_item_v1.schema.json",
    "title": "Evidence verification queue item (Step 09 machinery)",
    "description": f"{STATUS}. One field of one document with >= 1 extractor proposals, validator flags, at most one "
                   "human review read from a human-filled review file, and statuses derived from that review. "
                   "Not a ledger schema; not approved; XTR-/ADJ- (09.1) are still reserved only.",
    "type": "object",
    "additionalProperties": False,
    "required": ["record", "status", "machinery_version", "queue_item_id", "document_id", "field_class", "critical",
                 "span_sha256", "licence_status", "proposals", "flags", "human_review", "verification_status",
                 "evidence_tier_candidate"],
    "properties": {
        "record": {"const": "VERIFICATION_QUEUE_ITEM"},
        "status": {"const": STATUS},
        "machinery_version": _STR,
        "queue_item_id": {"type": "string", "pattern": "^vq:[0-9a-f]{16}$"},
        "document_id": {"type": "string", "minLength": 1},
        "field_class": {"enum": list(FIELD_CLASSES)},
        "critical": {"type": "boolean"},
        "span_sha256": {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"},
        "licence_status": _STR,
        "flags": {"type": "array", "items": _STR},
        "proposals": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["field_class", "raw_value", "extractor_id", "extractor_kind", "locator", "attributes",
                         "flags", "normalised"],
            "properties": {
                "field_class": {"enum": list(FIELD_CLASSES)}, "raw_value": _STR, "extractor_id": _STR,
                "extractor_kind": {"enum": list(EXTRACTOR_KINDS)},
                "locator": {"type": "object", "additionalProperties": False,
                            "required": ["document_id", "kind"],
                            "properties": {"document_id": _STR, "kind": {"enum": list(LOCATOR_KINDS)},
                                           "page": {"type": ["integer", "null"]}, "table": _OPT_STR, "row": _OPT_STR,
                                           "column": _OPT_STR, "char_start": {"type": ["integer", "null"]},
                                           "char_end": {"type": ["integer", "null"]}, "figure": _OPT_STR}},
                "attributes": {"type": "object", "additionalProperties": _STR},
                "flags": {"type": "array", "items": _STR},
                "normalised": {"type": "object", "required": ["raw", "status"]}}}},
        "human_review": {"anyOf": [{"type": "null"}, {
            "type": "object", "additionalProperties": False,
            "required": ["reviewer", "reviewed_at", "decision", "review_mode", "seen_model_output",
                         "review_source_sha256", "checked_locator", "corrected_raw_value", "minutes", "queue_item_id"],
            "properties": {"reviewer": {"enum": sorted(HUMANS)}, "reviewed_at": _STR,
                           "decision": {"enum": list(DECISIONS)}, "review_mode": {"enum": list(REVIEW_MODES)},
                           "seen_model_output": {"type": "boolean"},
                           "review_source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                           "checked_locator": _OPT_STR, "corrected_raw_value": _OPT_STR,
                           "minutes": {"type": ["integer", "null"], "minimum": 0}, "queue_item_id": _OPT_STR}}]},
        "verification_status": {"enum": list(VERIFICATION_STATUSES)},
        "evidence_tier_candidate": {"enum": list(TIER_CANDIDATES)},
    },
}
