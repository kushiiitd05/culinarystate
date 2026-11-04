"""Step 17b Rung A lexicons, read-only (DRAFT_PENDING_16c).

Rung A (Plan 17-M, B0) tags instruction text by longest match against the
existing lexicons. This module only reads them; it never writes a ledger or
registry and invents no entry:

- ``ledgers/data/ING.jsonl`` canonical names and ``ALIAS.jsonl`` surfaces -> ING ids
  (latest version per id, status ACTIVE only; an alias keeps only ACTIVE targets);
- ``ledgers/data/PROC.jsonl`` canonical names/aliases plus
  ``registry/recipe_process_surface_forms_v1.csv`` rows with a candidate mapping
  (``CANDIDATE_VERB_FORM_MATCH_POS_UNCHECKED``) -> PROC ids, with PROC family/kind;
- ``ledgers/data/TOOL.jsonl`` names/aliases -> TOOL ids and
  ``registry/recipe_tool_structural_class_map_v1.csv`` -> structural class;
- ``ledgers/data/UNIT.jsonl`` aliases of MASS / VOLUME / COUNT units as quantity
  unit tokens (single-letter ``t`` and ``c`` are left out: they collide with
  temperature letters and words).

All entries are UNVERIFIED in their sources; Rung A inherits that status. One
surface may map to several ids: that is kept as an ambiguity, never resolved by
a guess. A lexicon is identified by the SHA-256 ``fingerprint`` of its tables.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping

from culinarystate.state_graph.rule_compiler import _lemma_guess

STATUS = "DRAFT_PENDING_16c"
LEXICON_VERSION = "STEP17B_RUNG_A_LEXICON_V1_DRAFT"
ROOT = Path(__file__).resolve().parents[3]
SOURCE_FILES = ("ledgers/data/ING.jsonl", "ledgers/data/ALIAS.jsonl", "ledgers/data/PROC.jsonl",
                "ledgers/data/TOOL.jsonl", "ledgers/data/UNIT.jsonl",
                "registry/recipe_process_surface_forms_v1.csv", "registry/recipe_tool_structural_class_map_v1.csv")
PROC_SURFACE_STATUS = "CANDIDATE_VERB_FORM_MATCH_POS_UNCHECKED"
QUANTITY_DIMENSIONS = frozenset({"MASS", "VOLUME", "COUNT"})
EXCLUDED_UNIT_TOKENS = frozenset({"t", "c"})


def _mark_class() -> str:
    """Regex class of BMP combining marks (Unicode category M), so Indic vowel signs stay inside words."""
    marks = [chr(c) for c in range(0x300, 0x10000) if unicodedata.category(chr(c)).startswith("M")]
    return "".join(re.escape(ch) for ch in marks)


_L = rf"(?:[^\W\d_]|[{_mark_class()}])"
_WORD = re.compile(rf"{_L}+(?:[-'\u2019]{_L}+)*")

Key = tuple[str, ...]


def tokens(text: str) -> list[tuple[int, int, str]]:
    """Word tokens ``(start, end, lowercased word)``; digits and punctuation are not words."""
    return [(m.start(), m.end(), m.group(0).lower()) for m in _WORD.finditer(text)]


def key_of(surface: str) -> Key:
    return tuple(w for _, _, w in tokens(surface))


def singular_variants(word: str) -> tuple[str, ...]:
    """Deterministic plural strips tried in order (rule ``PLURAL_STRIP``)."""
    out = []
    if word.endswith("ies") and len(word) > 4:
        out.append(word[:-3] + "y")
    if word.endswith("oes") and len(word) > 4:
        out.append(word[:-2])
    if word.endswith("es") and len(word) > 3:
        out.append(word[:-2])
    if word.endswith("s") and not word.endswith("ss") and len(word) > 2:
        out.append(word[:-1])
    return tuple(dict.fromkeys(out))


@dataclass(frozen=True)
class ProcInfo:
    canonical: str
    family: str
    kind: str


@dataclass(frozen=True)
class Match:
    length: int
    ids: frozenset[str]
    flag: str | None = None


@dataclass(frozen=True)
class RungALexicon:
    foods: Mapping[Key, frozenset[str]]
    procs: Mapping[Key, frozenset[str]]
    proc_info: Mapping[str, ProcInfo]
    proc_canonical: Mapping[str, frozenset[str]]
    tools: Mapping[Key, frozenset[str]]
    tool_classes: Mapping[str, str]
    unit_tokens: frozenset[str]
    fingerprint: str
    sources: Mapping[str, str]
    max_n: int = 1

    # ------------------------------------------------------------ matching
    def _longest(self, table: Mapping[Key, frozenset[str]], words: list[str], i: int, plural: bool,
                 exact_len: int | None = None) -> Match | None:
        top = min(self.max_n, len(words) - i)
        for n in range(top, 0, -1):
            if exact_len is not None and n != exact_len:
                continue
            key = tuple(words[i:i + n])
            if key in table:
                return Match(n, table[key])
            if plural:
                for v in singular_variants(key[-1]):
                    alt = key[:-1] + (v,)
                    if alt in table:
                        return Match(n, table[alt], "PLURAL_STRIP")
        return None

    def food_at(self, words: list[str], i: int, exact_len: int | None = None) -> Match | None:
        return self._longest(self.foods, words, i, True, exact_len)

    def tool_at(self, words: list[str], i: int, exact_len: int | None = None) -> Match | None:
        return self._longest(self.tools, words, i, True, exact_len)

    def proc_at(self, words: list[str], i: int, exact_len: int | None = None) -> Match | None:
        """Longest exact PROC surface; a single word falls back to the rule compiler's lemma guess."""
        m = self._longest(self.procs, words, i, False, exact_len)
        if m is not None:
            return self._actions(m)
        if exact_len not in (None, 1):
            return None
        guess = _lemma_guess(words[i])
        ids = self.proc_canonical.get(guess or "")
        return self._actions(Match(1, ids, "PROC_LEMMA_GUESS")) if ids else None

    def _actions(self, m: Match) -> Match | None:
        ids = frozenset(i for i in m.ids if self.proc_info.get(i, ProcInfo("", "", "")).kind == "ACTION")
        return Match(m.length, ids, m.flag) if ids else None

    def _surface(self, finder, surface: str) -> frozenset[str]:
        words = list(key_of(surface))
        if not words:
            return frozenset()
        m = finder(words, 0, exact_len=len(words))
        return m.ids if m is not None else frozenset()

    def food_ids(self, surface: str) -> frozenset[str]:
        return self._surface(self.food_at, surface)

    def tool_ids(self, surface: str) -> frozenset[str]:
        return self._surface(self.tool_at, surface)

    def proc_ids(self, surface: str) -> frozenset[str]:
        return self._surface(self.proc_at, surface)

    def id_sets(self) -> dict[str, frozenset[str]]:
        """Id sets for V3 identifier checks (only ids present in this lexicon)."""
        return {"ING": frozenset().union(*self.foods.values()) if self.foods else frozenset(),
                "PROC": frozenset(self.proc_info),
                "TOOL": frozenset().union(*self.tools.values()) if self.tools else frozenset()}


def _table(entries: Mapping[str, Iterable[str]]) -> dict[Key, frozenset[str]]:
    out: dict[Key, set[str]] = {}
    for surface, ids in entries.items():
        key = key_of(surface)
        if key:
            out.setdefault(key, set()).update(ids)
    return {k: frozenset(v) for k, v in out.items() if v}


def _canon(table: Mapping[Key, frozenset[str]]) -> list:
    return sorted([" ".join(k), sorted(v)] for k, v in table.items())


def build_lexicon(*, foods: Mapping[str, Iterable[str]], procs: Mapping[str, Iterable[str]],
                  proc_info: Mapping[str, tuple[str, str, str]], tools: Mapping[str, Iterable[str]],
                  tool_classes: Mapping[str, str], units: Iterable[str],
                  sources: Mapping[str, str] | None = None) -> RungALexicon:
    """Build a lexicon from in-memory tables (surface -> ids); used by ``load_lexicon`` and tests."""
    food_t, proc_t, tool_t = _table(foods), _table(procs), _table(tools)
    info = {pid: ProcInfo(*v) for pid, v in proc_info.items()}
    canonical: dict[str, set[str]] = {}
    for pid, p in info.items():
        canonical.setdefault(p.canonical, set()).add(pid)
    unit_tokens = frozenset(u.lower() for u in units if u and u.lower() not in EXCLUDED_UNIT_TOKENS)
    blob = json.dumps({"version": LEXICON_VERSION, "foods": _canon(food_t), "procs": _canon(proc_t),
                       "proc_info": sorted([k, list(v)] for k, v in proc_info.items()),
                       "tools": _canon(tool_t), "tool_classes": sorted(tool_classes.items()),
                       "units": sorted(unit_tokens)}, sort_keys=True, ensure_ascii=False)
    return RungALexicon(food_t, proc_t, info, {k: frozenset(v) for k, v in canonical.items()}, tool_t,
                        dict(tool_classes), unit_tokens, hashlib.sha256(blob.encode("utf-8")).hexdigest(),
                        dict(sources or {}), max((len(k) for k in (*food_t, *proc_t, *tool_t)), default=1))


# ------------------------------------------------------------ read-only file loading
def _latest_active(path: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            rid = r.get("id")
            prev = latest.get(rid)
            if prev is None or int(r.get("version") or 0) >= int(prev.get("version") or 0):
                latest[rid] = r
    return {k: v for k, v in latest.items() if v.get("status") == "ACTIVE"}


def _rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _add(out: dict[str, set[str]], surface: str | None, rid: str) -> None:
    if isinstance(surface, str) and surface.strip():
        out.setdefault(surface.strip().lower(), set()).add(rid)


def read_tables(root: Path) -> dict:
    """Read the seven source files (read-only) into ``build_lexicon`` keyword tables."""
    led = root / "ledgers" / "data"
    ing = _latest_active(led / "ING.jsonl")
    foods: dict[str, set[str]] = {}
    for rid, r in ing.items():
        _add(foods, r.get("canonical_name"), rid)
    for r in _latest_active(led / "ALIAS.jsonl").values():
        targets = [t for t in (r.get("candidate_ingredient_ids") or [r.get("ingredient_id")]) if t in ing]
        for t in targets:
            _add(foods, r.get("surface"), t)
            _add(foods, r.get("normalized"), t)
    proc = _latest_active(led / "PROC.jsonl")
    procs: dict[str, set[str]] = {}
    for rid, r in proc.items():
        _add(procs, r.get("canonical_name"), rid)
        for a in r.get("aliases") or []:
            _add(procs, a, rid)
    for row in _rows(root / "registry" / "recipe_process_surface_forms_v1.csv"):
        if row.get("mapping_status") == PROC_SURFACE_STATUS and row.get("canonical_mapping") in proc:
            _add(procs, row.get("surface_form"), row["canonical_mapping"])
    tool = _latest_active(led / "TOOL.jsonl")
    tools: dict[str, set[str]] = {}
    for rid, r in tool.items():
        _add(tools, r.get("canonical_name"), rid)
        for a in r.get("aliases") or []:
            _add(tools, a, rid)
    classes = {row["tool_id"]: row["structural_class"]
               for row in _rows(root / "registry" / "recipe_tool_structural_class_map_v1.csv")
               if row.get("tool_id") in tool and row.get("structural_class")}
    units: set[str] = set()
    for r in _latest_active(led / "UNIT.jsonl").values():
        if r.get("dimension") in QUANTITY_DIMENSIONS:
            units.update(a for a in [r.get("canonical_name"), *(r.get("aliases") or [])] if isinstance(a, str))
    return {"foods": foods, "procs": procs,
            "proc_info": {rid: (r.get("canonical_name") or "", r.get("family") or "", r.get("kind") or "")
                          for rid, r in proc.items()},
            "tools": tools, "tool_classes": classes, "units": sorted(units)}


def source_hashes(root: Path) -> dict[str, str]:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in SOURCE_FILES}


@lru_cache(maxsize=4)
def _cached(root: str) -> RungALexicon:
    path = Path(root)
    return build_lexicon(**read_tables(path), sources=source_hashes(path))


def load_lexicon(root: Path | None = None, *, cache: bool = True) -> RungALexicon:
    """Read-only load of the repository lexicons (default: this checkout)."""
    path = Path(root or ROOT).resolve()
    if cache:
        return _cached(str(path))
    return build_lexicon(**read_tables(path), sources=source_hashes(path))
