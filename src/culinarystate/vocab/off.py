"""Open Food Facts taxonomy (ODbL) text format -> entries.

Blocks are separated by blank lines. In a block:  `< en: parent` (parent), `xx: name, synonym, …` (names per
language), `prop:xx: value` (properties, e.g. wikidata:en: Q34172). `synonyms:` / `stopwords:` blocks and `#`
comments are skipped. Entry id = first language line's first name, e.g. "en:butter".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

LANG_LINE = re.compile(r"^([a-z]{2,3}(?:[-_][A-Za-z]{2,4})?):\s*(.+)$")
PROP_LINE = re.compile(r"^([a-z0-9_]+):([a-z]{2,3}):\s*(.+)$")
INDIAN_LANGS = ("hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur", "or", "as", "sa")


@dataclass
class Entry:
    id: str
    names: dict[str, list[str]] = field(default_factory=dict)
    parents: list[str] = field(default_factory=list)
    props: dict[str, str] = field(default_factory=dict)


def _norm_parent(p: str) -> str:
    lang, _, name = p.partition(":")
    return f"{lang.strip()}:{name.strip().lower()}"


def parse_block(lines: list[str]) -> Entry | None:
    lines = [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines or lines[0].startswith(("synonyms:", "stopwords:")):
        return None
    e = Entry("")
    for ln in lines:
        if ln.startswith("<"):
            e.parents.append(_norm_parent(ln[1:]))
            continue
        pm = PROP_LINE.match(ln)
        if pm:
            e.props[pm.group(1)] = pm.group(3).strip()
            continue
        lm = LANG_LINE.match(ln)
        if lm:
            names = [n.strip() for n in lm.group(2).split(",") if n.strip()]
            if names:
                e.names.setdefault(lm.group(1).lower(), []).extend(names)
                if not e.id:
                    e.id = f"{lm.group(1).lower()}:{names[0].lower()}"
    return e if e.id else None


def parse(path: Path) -> dict[str, Entry]:
    out, block = {}, []
    for ln in path.read_text(encoding="utf-8").splitlines() + [""]:
        if ln.strip():
            block.append(ln)
            continue
        e = parse_block(block)
        if e:
            out[e.id] = e
        block = []
    return out
