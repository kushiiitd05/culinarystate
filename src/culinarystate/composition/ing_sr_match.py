"""ING canonical name -> SR Legacy food, lexical matcher (S175). Every match is UNVERIFIED until a human checks it.

A candidate must contain every query token. Score: +10 when the query head (last token of a recipe name; last
token of the first comma segment of an SR-ordered synonym target, e.g. "wheat flour, white") is the head noun of
the description, i.e. the last token of its first comma segment, +5 more when that segment's
tokens equal the query tokens exactly, +2 for "raw", minus 0.5 per extra description token. AUTO_MATCH_HIGH needs the head bonus and a margin >= 2 over the runner-up;
otherwise AUTO_MATCH_LOW. No candidate -> NO_MATCH (never a guess). Ties break on the smaller fdc_id.

``resolve`` first consults the curated defaults registry (registry/ing_sr_defaults_v1.csv): a mapped term gives
REGISTRY_MAPPED with its kind (DIRECT, UK_US, DEFAULT_FORM, APPROX); NO_SR_EQUIVALENT, NOT_A_FOOD and AMBIGUOUS
terms give REGISTRY_UNMAPPABLE with no food. Only terms absent from the registry fall back to the lexical match.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from culinarystate.composition.sr_legacy import SRFood

HEAD_BONUS, EXACT_FIRST_BONUS, RAW_BONUS, EXTRA_PENALTY, HIGH_MARGIN = 10.0, 5.0, 2.0, 0.5, 2.0
_SPLIT = re.compile(r"[^a-z0-9]+")


def _singular(w: str) -> str:
    if len(w) <= 3 or w.endswith(("ss", "us", "is")):
        return w
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("oes"):
        return w[:-2]
    if w.endswith("sses"):
        return w[:-2]
    return w[:-1] if w.endswith("s") else w


def normalise(name: str) -> tuple[str, ...]:
    return tuple(_singular(t) for t in _SPLIT.split(name.lower()) if t)


@dataclass(frozen=True)
class IndexEntry:
    fdc_id: int
    tokens: frozenset[str]
    first: frozenset[str]
    head: str


@dataclass(frozen=True)
class MatchResult:
    query: str
    status: str
    fdc_id: int | None
    description: str | None
    score: float | None
    runner_up_fdc_id: int | None
    runner_up_score: float | None
    via_synonym: str | None
    verification: str = "UNVERIFIED"
    kind: str | None = None


MAPPED_KINDS = frozenset({"DIRECT", "UK_US", "DEFAULT_FORM", "APPROX"})
UNMAPPABLE_KINDS = frozenset({"NO_SR_EQUIVALENT", "NOT_A_FOOD", "AMBIGUOUS"})


@dataclass(frozen=True)
class RegistryEntry:
    term: str
    fdc_id: int | None
    kind: str


def load_registry(path: Path | str) -> dict[tuple[str, ...], RegistryEntry]:
    """Normalised term -> entry. Mapped kinds need an fdc_id; unmappable kinds must not carry one."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out: dict[tuple[str, ...], RegistryEntry] = {}
    for r in rows:
        term, kind, fdc = r["term"].strip(), r["kind"].strip(), r["fdc_id"].strip()
        if kind not in MAPPED_KINDS | UNMAPPABLE_KINDS:
            raise ValueError(f"unknown kind {kind!r} for {term!r} in {path}")
        if (kind in MAPPED_KINDS) != bool(fdc):
            raise ValueError(f"kind {kind} for {term!r} needs fdc_id iff mapped (fdc_id={fdc!r})")
        key = normalise(term)
        if not key or key in out:
            raise ValueError(f"empty or duplicate term {term!r} in {path}")
        out[key] = RegistryEntry(term, int(fdc) if fdc else None, kind)
    return out


def load_synonyms(path: Path | str) -> dict[str, str]:
    """term -> SR-ordered query from a registry CSV (columns term, sr_query, kind, rationale, status)."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out: dict[str, str] = {}
    for r in rows:
        term, q = r["term"].strip(), r["sr_query"].strip()
        if not term or not q:
            raise ValueError(f"empty term or sr_query in {path}: {r}")
        if term in out:
            raise ValueError(f"duplicate synonym term {term!r} in {path}")
        out[term] = q
    return out


def build_index(foods: Mapping[int, SRFood]) -> tuple[IndexEntry, ...]:
    out = []
    for f in sorted(foods.values(), key=lambda f: f.fdc_id):
        first = normalise(f.description.split(",")[0])
        out.append(IndexEntry(f.fdc_id, frozenset(normalise(f.description)), frozenset(first),
                              first[-1] if first else ""))
    return tuple(out)


def _query(name: str, synonyms: Mapping[str, str]) -> tuple[tuple[str, ...], str, str | None]:
    q = normalise(name)
    for key, target in synonyms.items():
        if normalise(key) == q:
            t, t0 = normalise(target), normalise(target.split(",")[0])
            return t, (t0[-1] if t0 else ""), key
    return q, (q[-1] if q else ""), None


def _score(e: IndexEntry, q: frozenset[str], head: str) -> float:
    extra = len(e.tokens - q - {"raw"})
    return ((HEAD_BONUS if head and head == e.head else 0.0) + (EXACT_FIRST_BONUS if e.first == q else 0.0)
            + (RAW_BONUS if "raw" in e.tokens else 0.0) - EXTRA_PENALTY * extra)


def match(name: str, foods: Mapping[int, SRFood], synonyms: Mapping[str, str],
          index: tuple[IndexEntry, ...] | None = None) -> MatchResult:
    q, head, via = _query(name, synonyms)
    qs = frozenset(q)
    idx = index if index is not None else build_index(foods)
    ranked = sorted(((_score(e, qs, head), e) for e in idx if qs and qs <= e.tokens),
                    key=lambda t: (-t[0], t[1].fdc_id))
    if not ranked:
        return MatchResult(name, "NO_MATCH", None, None, None, None, None, via)
    (s, best), runner = ranked[0], (ranked[1] if len(ranked) > 1 else None)
    high = bool(head) and head == best.head and (runner is None or s - runner[0] >= HIGH_MARGIN)
    return MatchResult(name, "AUTO_MATCH_HIGH" if high else "AUTO_MATCH_LOW", best.fdc_id,
                       foods[best.fdc_id].description, s, runner[1].fdc_id if runner else None,
                       runner[0] if runner else None, via)


def resolve(name: str, foods: Mapping[int, SRFood], registry: Mapping[tuple[str, ...], RegistryEntry],
            synonyms: Mapping[str, str] | None = None, index: tuple[IndexEntry, ...] | None = None) -> MatchResult:
    e = registry.get(normalise(name))
    if e is None:
        return match(name, foods, synonyms or {}, index)
    if e.fdc_id is None:
        return MatchResult(name, "REGISTRY_UNMAPPABLE", None, None, None, None, None, e.term, kind=e.kind)
    if e.fdc_id not in foods:
        raise ValueError(f"registry fdc_id {e.fdc_id} for {e.term!r} not in the loaded SR foods")
    return MatchResult(name, "REGISTRY_MAPPED", e.fdc_id, foods[e.fdc_id].description, None, None, None, e.term,
                       kind=e.kind)
