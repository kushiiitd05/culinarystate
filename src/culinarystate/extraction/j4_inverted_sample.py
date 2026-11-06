"""J4 sample of V2 INVERTED_INTERVAL cases for human reading (S166; review block J4; D-059). DRAFT.

The full-corpus Step 17b run found 4,511 V2 INVERTED_INTERVAL issues in 3,848 texts; ~94 % have the shape
"9-9/9 <unit>" (a hyphenated mixed number such as 1-1/2 read as an inverted range). Before any rc2 grammar change, Kush
and Parv read a stratified sample (D-059): every case in the seeded 1,000 sample, all A1 and Wikibooks cases, up to 30
Food.com and 30 Gutenberg cases, with every P1 manifest recipe excluded. Recipe text goes only to a git-ignored private
file; the tracked manifest holds hashed recipe ids, family, stratum and a shape mask.
"""
from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import Iterable, Mapping

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.extraction.validators import v2_quantity_records
from culinarystate.quantity import rc2_dryrun as D

CODE = "INVERTED_INTERVAL"
QUOTA = {"FOODCOM": 30, "GUTENBERG_SEGMENT": 30}
ALL_FAMILIES = {"A1_BBC_GOOD_FOOD": "S2_A1_ALL", "WIKIBOOKS": "S3_WIKIBOOKS_ALL"}
QUOTA_STRATUM = {"FOODCOM": "S4_FOODCOM_30", "GUTENBERG_SEGMENT": "S5_GUTENBERG_30"}
S1 = "S1_IN_1000_SAMPLE"


@lru_cache(maxsize=1)
def _engine():
    return RungA(), D.load_schema()


def inverted_spans(raw: str, *, locale: str | None, rung: RungA | None = None,
                   schema: Mapping | None = None) -> list[tuple[int, int]]:
    """(start, end) of every quantity grounding whose rc2 record V2 flags INVERTED_INTERVAL."""
    if rung is None or schema is None:
        rung, schema = _engine()
    source = SourceText.from_raw("J4", raw)
    res = rung.run(source, rung.config(locale=locale), schema=schema)
    spans = {q.result_id: (q.span.char_start, q.span.char_end) for q in res.quantities}
    flagged = {i.path.split("/", 1)[0] for i in v2_quantity_records(res.quantities, schema).issues if i.code == CODE}
    return sorted(spans[r] for r in flagged if r in spans)


def shape(text: str) -> str:
    return re.sub(r"[^\W\d_]+", "a", re.sub(r"\d+", "9", text))


def _rank(seed: str, c: Mapping) -> str:
    return hashlib.sha256(f"{seed}|{c['recipe_id']}|{c['start']}".encode("utf-8")).hexdigest()


def stratified_sample(cands: Iterable[Mapping], *, seed: str, in_1000: set[str], excluded: set[str]) -> list[dict]:
    """The agreed J4 strata; deterministic for a seed; one row per case; excluded recipes never appear."""
    pool = sorted((dict(c) for c in cands if c["recipe_id"] not in excluded), key=lambda c: _rank(seed, c))
    out, taken = [], Counter_like()
    for c in pool:
        if c["recipe_id"] in in_1000:
            out.append({**c, "stratum": S1})
        elif c["source_family"] in ALL_FAMILIES:
            out.append({**c, "stratum": ALL_FAMILIES[c["source_family"]]})
        elif c["source_family"] in QUOTA and taken[c["source_family"]] < QUOTA[c["source_family"]]:
            taken[c["source_family"]] += 1
            out.append({**c, "stratum": QUOTA_STRATUM[c["source_family"]]})
    return sorted(out, key=lambda r: (r["stratum"], _rank(seed, r)))


class Counter_like(dict):
    def __missing__(self, key):
        return 0


def manifest_rows(rows: Iterable[Mapping]) -> list[dict]:
    """Tracked, text-free rows (hashed recipe id, family, stratum, shape mask)."""
    return [{"case_id": f"J4-{n:04d}", "recipe_id_sha256": hashlib.sha256(r["recipe_id"].encode("utf-8")).hexdigest(),
             "source_family": r["source_family"], "stratum": r["stratum"], "shape": r.get("shape", "")}
            for n, r in enumerate(rows, 1)]
