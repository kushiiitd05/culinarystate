"""USDA R6 versus Bognar 2002 reference-list overlap (Step 08a.4, gate G08-9, THR-08A-11).

Method (stated before coding, D-032):
  1. extract_references: find the LAST line that is only "References" (or "Literature
     cited" / "Bibliography"); the block ends at the first form feed or "Appendix" line.
     Entries are split on "[n]" markers when present, else on blank lines. Each entry
     becomes a Reference(surname, year, title_words, venue); the raw entry text is not kept.
  2. normalise_key: lowercase, accent-folded, punctuation stripped:
     "<first-author surname>|<year>|<first 3 title words>".
  3. match: EXACT = equal normalise_key. FUZZY (conservative, not already exact) = same
     surname, |year difference| <= 1, and Jaccard of stop-word-free title words >= 0.5.
     Counted separately.
  4. verdict, in the THR-08A-11 vocabulary: NOT_DETERMINABLE if either list is empty or any
     entry lacks a surname or year (extraction not reliable); OVERLAP_FOUND if any exact or
     fuzzy match; otherwise NO_OVERLAP_FOUND_IN_BIBLIOGRAPHY.
This is the agent's mechanical verdict; the expert reading (G08-9 human step) is pending.
All functions are pure and deterministic.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_HEADING = re.compile(r"^\s*(references|literature cited|bibliography)\s*:?\s*$", re.I)
_MARKER = re.compile(r"^\s*\[(\d+)\]\s*")
_YEAR = re.compile(r"\b(1[5-9]\d\d|20[0-3]\d)\b")
_VENUE = re.compile(r"(?:journal|j\.)\s+(?:of\s+)?([a-z ]+?)(?=[.,;:]|\s\d|$)", re.I)
_STOP = frozenset("a an and as at by for from in of on or the to with".split())
_FUZZY_JACCARD = 0.5
_TITLE_KEY_WORDS = 3
_TITLE_KEEP = 8


@dataclass(frozen=True)
class Reference:
    surname: str
    year: int | None
    title_words: tuple[str, ...]
    venue: str


@dataclass(frozen=True)
class MatchResult:
    exact: tuple[tuple[str, int, str], ...]
    fuzzy: tuple[tuple[str, int, str], ...]

    @property
    def exact_count(self) -> int:
        return len(self.exact)

    @property
    def fuzzy_count(self) -> int:
        return len(self.fuzzy)


def _fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def _words(text: str) -> tuple[str, ...]:
    return tuple(re.sub(r"[^a-z0-9 ]+", " ", _fold(text).lower()).split())


def _reference_block(text: str) -> list[str]:
    lines = text.split("\n")
    heads = [i for i, ln in enumerate(lines) if _HEADING.match(ln)]
    if not heads:
        return []
    out: list[str] = []
    for ln in lines[heads[-1] + 1:]:
        if "\x0c" in ln:
            before = ln.split("\x0c")[0]
            if before.strip():
                out.append(before)
            break
        if re.match(r"^\s*appendix\b", ln, re.I):
            break
        out.append(ln)
    return out


def _split_entries(block: list[str]) -> list[str]:
    if any(_MARKER.match(ln) for ln in block):
        entries: list[str] = []
        for ln in block:
            if _MARKER.match(ln):
                entries.append(_MARKER.sub("", ln).strip())
            elif entries and ln.strip():
                entries[-1] += " " + ln.strip()
        return entries
    entries, cur = [], []
    for ln in block + [""]:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            entries.append(" ".join(cur))
            cur = []
    return entries


def _parse(entry: str) -> Reference:
    folded = _fold(entry)
    sm = re.match(r"[A-Za-z0-9]+", folded.strip())
    surname = sm.group(0).lower() if sm else ""
    ym = _YEAR.search(folded)
    year = int(ym.group(1)) if ym else None
    title = ""
    if ym and re.match(r"\s*[\).]", folded[ym.end():]):
        title = folded[ym.end():].lstrip(" ).;:,")
    else:
        parts = folded.split(". ", 1)
        title = parts[1] if len(parts) > 1 else ""
    if not title.strip() and ym:
        title = folded[:ym.start()].split(".", 1)[-1] if "." in folded[:ym.start()] else folded[:ym.start()]
    vm = _VENUE.search(title or folded)
    venue = " ".join(_words(vm.group(1))[:3]) if vm else ""
    return Reference(surname, year, _words(title)[:_TITLE_KEEP], venue)


def extract_references(text: str) -> list[Reference]:
    """Parse the reference list of ``text``; [] when no heading is found."""
    entries = _split_entries(_reference_block(text))
    return [_parse(e) for e in entries if re.search(r"[A-Za-z]", e)]


def normalise_key(ref: Reference) -> str:
    return f"{ref.surname}|{ref.year}|{' '.join(ref.title_words[:_TITLE_KEY_WORDS])}"


def _content(ref: Reference) -> frozenset[str]:
    return frozenset(w for w in ref.title_words if w not in _STOP)


def _short(ref: Reference) -> tuple[str, int, str]:
    return (ref.surname, ref.year or 0, ref.venue)


def _fuzzy_pair(a: Reference, b: Reference) -> bool:
    if a.year is None or b.year is None or a.surname != b.surname or abs(a.year - b.year) > 1:
        return False
    ca, cb = _content(a), _content(b)
    return bool(ca and cb) and len(ca & cb) / len(ca | cb) >= _FUZZY_JACCARD


def match(a: list[Reference], b: list[Reference]) -> MatchResult:
    """Exact and fuzzy matches between two reference lists (each A entry counted once)."""
    keys_b = {normalise_key(r) for r in b}
    exact, fuzzy = [], []
    for ra in a:
        if normalise_key(ra) in keys_b:
            exact.append(_short(ra))
        elif any(_fuzzy_pair(ra, rb) for rb in b):
            fuzzy.append(_short(ra))
    return MatchResult(tuple(exact), tuple(fuzzy))


def _reliable(refs: list[Reference]) -> bool:
    return bool(refs) and all(r.surname and r.year is not None for r in refs)


def verdict(a: list[Reference], b: list[Reference], result: MatchResult) -> str:
    if not (_reliable(a) and _reliable(b)):
        return "NOT_DETERMINABLE"
    if result.exact_count or result.fuzzy_count:
        return "OVERLAP_FOUND"
    return "NO_OVERLAP_FOUND_IN_BIBLIOGRAPHY"


def cites_title(refs: list[Reference], title_phrase: str) -> list[tuple[str, int]]:
    """Short keys of refs whose title words contain every word of ``title_phrase``."""
    need = set(_words(title_phrase))
    return [(r.surname, r.year or 0) for r in refs if need and need <= set(r.title_words)]
