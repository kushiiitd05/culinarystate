"""Corpus mention frequency per ING concept, for ordering the human verification queue (counts only).

Sources actually used (each is a separate column; nothing here keeps recipe text or recipe ids):
- ``bbc_ledger``       ING.corpus_frequency from the ledger (BBC Good Food line mentions counted when the registry was
                       built; BBC text itself is not on this server, D-003). Latest ACTIVE ING rows.
- ``foodcom_parts``    every Food.com ingredient part (recipes.parquet, column RecipeIngredientParts, all rows)
                       linked with the lot-state linker; counted once per unique string, multiplied by its count.
- ``wikibooks_lines``  rows of registry/recipes/wikibooks_ingredient_links_v1.csv (ingredient lines linked earlier).
- ``tasteset_lines``   TASTEset ingredient lines linked with the lot-state linker (quantity stripped).
- ``gutenberg_recipes`` rows of registry/recipes/gutenberg_ingredient_links_v1.csv (recipe x ING pairs from step text;
                       Gutenberg has no ingredient lines).
``mentions_total`` is the plain sum of the five columns (units differ slightly: lines, parts, recipes).
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Iterable

from .linker import LineLinker

SOURCES = ("bbc_ledger", "foodcom_parts", "wikibooks_lines", "tasteset_lines", "gutenberg_recipes")


def foodcom_part_counts(parquet: Path, batch_size: int = 20000) -> tuple[Counter, int]:
    """(Counter of unique part strings, recipes read). Reads only the parts column."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(parquet)
    parts: Counter = Counter()
    recipes = 0
    for batch in pf.iter_batches(batch_size=batch_size, columns=["RecipeIngredientParts"]):
        col = batch.column(0).to_pylist()
        recipes += len(col)
        for row in col:
            for p in row or ():
                if isinstance(p, str) and p.strip():
                    parts[p] += 1
    return parts, recipes


def link_counts(parts: Counter, linker: LineLinker) -> tuple[Counter, int, int]:
    """(ING id -> mentions, linked mentions, unlinked mentions)."""
    out: Counter = Counter()
    unlinked = 0
    for p, c in parts.items():
        h = linker.link_part(p)
        if h:
            out[h] += c
        else:
            unlinked += c
    return out, sum(out.values()), unlinked


def tasteset_counts(csv_path: Path, linker: LineLinker) -> tuple[Counter, int, int]:
    out: Counter = Counter()
    unlinked = 0
    with open(csv_path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            for line in (r.get("ingredients") or "").split("\n"):
                if not line.strip():
                    continue
                h = linker.link_line(line)
                if h:
                    out[h] += 1
                else:
                    unlinked += 1
    return out, sum(out.values()), unlinked


def csv_id_counts(path: Path, column: str = "ing_id") -> Counter:
    out: Counter = Counter()
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            v = (r.get(column) or "").strip()
            if v:
                out[v] += 1
    return out


def cumulative(order: Iterable[tuple[str, int]], threshold: float = 0.8) -> tuple[list[tuple[str, int, float]], int]:
    """[(id, mentions, cumulative share)] in the given order and the number of rows needed to reach ``threshold``."""
    rows = list(order)
    total = sum(m for _, m in rows) or 1
    acc, out, need = 0, [], None
    for i, (k, m) in enumerate(rows, 1):
        acc += m
        out.append((k, m, acc / total))
        if need is None and acc / total >= threshold:
            need = i
    return out, need if need is not None else len(rows)
