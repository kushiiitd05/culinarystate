"""Pure helpers for the D5 leakage audit (S178; consensus T9-C09-R2). DRAFT. Counts only; no text is returned.

The audit asks two questions about the D5 benchmark draft:
- S blocks: do the recipes behind S1/S2 also sit in a set the engine, the NER or the linker was built or tuned on
  (gold recipes, their duplicate groups, seeded Rung A dev samples, NER training lines, linker concept splits)?
- P/C blocks: are the EVD rows behind the gold the same rows DEL-2 trained and tested on, and the rows the retrieval
  silver set was drawn from (the data the retrieval weights were tuned on)?

These helpers do the set arithmetic; ``tools/s178_leakage_audit_d5.py`` reads the data and calls them.
"""
from __future__ import annotations

import hashlib
import random
import re
import unicodedata
from collections import defaultdict
from typing import Iterable, Mapping, Sequence

VERSION = "leakage_audit_d5@0.1"


# ------------------------------------------------------------------ seeded samples (same rule as rung_a_measure)

def rank(seed: str, recipe_id: str) -> str:
    """sha256(seed || recipe_id): the ranking key of ``rung_a_measure.seeded_sample``."""
    return hashlib.sha256(seed.encode("utf-8") + recipe_id.encode("utf-8")).hexdigest()


def seeded_set(id_family: Mapping[str, str], seed: str, size: int, families: Iterable[str] | None = None) -> set[str]:
    """The ``size`` ids with the smallest (rank, id) among ``families`` (all when None)."""
    fams = None if families is None else set(families)
    keyed = sorted((rank(seed, i), i) for i, f in id_family.items() if fams is None or f in fams)
    return {i for _, i in keyed[:size]}


def overlap(target: Iterable[str], other: Iterable[str]) -> dict:
    t, o = set(target), set(other)
    return {"n_target": len(t), "n_other": len(o), "n_overlap": len(t & o)}


def expected_random_overlap(n_target: int, sample_size: int, population: int) -> float:
    """Expected overlap of ``n_target`` fixed ids with a uniformly random sample (rank order is a random draw)."""
    return round(n_target * min(sample_size, population) / population, 4) if population else 0.0


# ------------------------------------------------------------------ line normalisation and linker split

def norm_line(s: str) -> str:
    """Case, accent and punctuation folded line (the normalisation of ``tools/build_linker_data.norm``)."""
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def linker_bucket(key: str) -> float:
    return int(hashlib.sha256(f"LINK-v1|{key}".encode()).hexdigest()[:12], 16) / 16 ** 12


def linker_split(ing_id: str) -> str:
    """Concept split of ``tools/build_linker_data.py`` (test >= 0.8, dev >= 0.7, else train)."""
    b = linker_bucket(ing_id)
    return "test" if b >= 0.8 else "dev" if b >= 0.7 else "train"


def exact_line_matches(lines: Iterable[str], corpus_norm: set[str]) -> dict:
    ls = [norm_line(x) for x in lines]
    ls = [x for x in ls if x]
    return {"n_lines": len(ls), "n_exact_match": sum(x in corpus_norm for x in ls)}


# ------------------------------------------------------------------ retrieval silver set (tools/export_retrieval_set.py)

def silver_queries(evd_rows: Sequence[Mapping], *, seed: int = 20261018, max_cells: int = 600) -> list[dict]:
    """The silver retrieval queries as ``tools/export_retrieval_set.py`` draws them: cells (matrix name, process id,
    target name, source family) with >= 2 retention rows, <= ``max_cells`` per run split evenly over families, drawn
    with ``random.Random(seed)``. Returns cell keys and the relevant EVD ids (no question text)."""
    evd = [e for e in evd_rows if e["status"] == "ACTIVE"]
    cells: dict[tuple, list[str]] = defaultdict(list)
    for e in evd:
        if "retention_factor" in e["derived"] and (e["process"] or {}).get("process_id"):
            cells[(e["matrix"]["raw_name"].lower(), e["process"]["process_id"], e["target"]["raw_name"].lower(),
                   e["source_family_id"])].append(e["id"])
    by_fam: dict[str, list[tuple]] = defaultdict(list)
    for k, ids in cells.items():
        if len(ids) >= 2:
            by_fam[k[3]].append(k)
    rng = random.Random(seed)
    per = max_cells // max(1, len(by_fam))
    picked = [k for f in sorted(by_fam) for k in rng.sample(sorted(by_fam[f]), min(per, len(by_fam[f])))]
    rel: dict[tuple, set[str]] = defaultdict(set)
    for (m, p, t, _), ids in cells.items():
        rel[(m, p, t)] |= set(ids)
    return [{"cell": k[:3], "family": k[3], "relevant": sorted(rel[k[:3]])} for k in picked]


def evd_cell(row: Mapping) -> tuple[str, str, str]:
    return (row["matrix"]["raw_name"].lower(), (row["process"] or {}).get("process_id") or "", row["target"]["raw_name"].lower())
