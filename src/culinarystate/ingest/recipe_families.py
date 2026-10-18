"""Near-duplicate recipe families (plan H1: MinHash ≥ 0.8 on instructions + title/ingredient signature).

Pure-Python MinHash over word 5-shingles with banded LSH for candidates, then exact Jaccard (on the
shingle sets) to confirm; families are connected components of confirmed pairs. Deterministic.
"""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict

import numpy as np

_MERSENNE = (1 << 61) - 1


def shingles(text: str, k: int = 5) -> set[int]:
    w = re.findall(r"[a-z0-9]+", text.lower())
    if len(w) < k:
        return {int.from_bytes(hashlib.blake2b(" ".join(w).encode(), digest_size=8).digest(), "big")} if w else set()
    return {int.from_bytes(hashlib.blake2b(" ".join(w[i:i + k]).encode(), digest_size=8).digest(), "big")
            for i in range(len(w) - k + 1)}


def minhash(sh: set[int], n: int = 64, seed: int = 20261018) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.integers(1, _MERSENNE, n, dtype=np.uint64)
    b = rng.integers(0, _MERSENNE, n, dtype=np.uint64)
    if not sh:
        return np.full(n, np.iinfo(np.uint64).max, dtype=np.uint64)
    x = np.fromiter(sh, dtype=np.uint64) % np.uint64(_MERSENNE)
    with np.errstate(over="ignore"):
        h = (np.outer(x, a) + b) % np.uint64(_MERSENNE)
    return h.min(axis=0)


def families(docs: dict[str, str], threshold: float = 0.8, bands: int = 16) -> tuple[dict[str, str], list[tuple]]:
    """Return (doc_id -> family_id, confirmed pairs [(a, b, jaccard)])."""
    ids = sorted(docs)
    sh = {i: shingles(docs[i]) for i in ids}
    sigs = {i: minhash(sh[i]) for i in ids}
    rows = len(next(iter(sigs.values()))) // bands if sigs else 0
    buckets: dict[tuple, list[str]] = defaultdict(list)
    for i in ids:
        for bnd in range(bands):
            buckets[(bnd, sigs[i][bnd * rows:(bnd + 1) * rows].tobytes())].append(i)
    cand = set()
    for members in buckets.values():
        if 1 < len(members) <= 200:
            for x in range(len(members)):
                for y in range(x + 1, len(members)):
                    cand.add((members[x], members[y]))
    pairs = []
    for a_, b_ in sorted(cand):
        sa, sb = sh[a_], sh[b_]
        if sa and sb:
            j = len(sa & sb) / len(sa | sb)
            if j >= threshold:
                pairs.append((a_, b_, round(j, 4)))
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a_, b_, _ in pairs:
        ra, rb = find(a_), find(b_)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    return {i: f"FAM-{find(i)}" for i in ids}, pairs
