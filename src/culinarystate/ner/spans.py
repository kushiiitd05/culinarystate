"""S119 span-level knowledge features (Aprilab strategy items 1, 2, 4): candidates over ALL n-grams (<= 6 tokens) generated BEFORE NER, features per
(span, label) from a TRAIN-only gazetteer, 5-fold out-of-fold for train docs, projection to tokens with separate B-slot / I-slot channels.
No NER output or gold span is used to decide which spans get features, so train-time and test-time features are built identically.
Pure numpy / stdlib; runs on the laptop."""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

WORD = re.compile(r"\w+|[^\w\s]")
MAX_N = 6
FEATS = ("exact", "log_count", "fuzzy", "ext_exact")        # per label; plus span length appended once


def tokens(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in WORD.finditer(text)]


def candidate_spans(toks: Sequence[Tuple[int, int]], max_n: int = MAX_N) -> List[Tuple[int, int]]:
    """All (start_token, end_token_exclusive) n-grams with n <= max_n. Deterministic, independent of any labels."""
    return [(i, j) for i in range(len(toks)) for j in range(i + 1, min(len(toks), i + max_n) + 1)]


def _tri(s: str) -> set:
    s = f"  {s} "
    return {s[i:i + 3] for i in range(len(s) - 2)}


class Gazetteer:
    """(label, surface) counts from a set of docs + trigram index for fuzzy lookup. Build from TRAIN (or train folds) only."""

    def __init__(self, labels: Sequence[str], ext_aliases: Dict[str, set] | None = None):
        self.labels, self.count, self.ext = list(labels), Counter(), ext_aliases or {}
        self.index: Dict[str, Dict[str, set]] = {l: defaultdict(set) for l in labels}
        self.surfaces: Dict[str, List[str]] = {l: [] for l in labels}

    @classmethod
    def build(cls, docs: Iterable[Tuple[str, Sequence[tuple]]], labels: Sequence[str], ext_aliases=None) -> "Gazetteer":
        g = cls(labels, ext_aliases)
        for text, spans in docs:
            for s, e, lab in spans:
                if lab in g.index:
                    g.count[(lab, text[s:e].lower())] += 1
        for (lab, surf) in g.count:
            k = len(g.surfaces[lab])
            g.surfaces[lab].append(surf)
            for t in _tri(surf):
                g.index[lab][t].add(k)
        return g

    def fuzzy(self, lab: str, surf: str) -> float:
        tg = _tri(surf)
        hit = Counter(k for t in tg for k in self.index[lab].get(t, ()))
        best = 0.0
        for k, c in hit.most_common(20):
            other = len(_tri(self.surfaces[lab][k]))
            best = max(best, c / (len(tg) + other - c))
        return best

    def features(self, surf: str) -> np.ndarray:
        surf = surf.lower()
        out = []
        for lab in self.labels:
            n = self.count.get((lab, surf), 0)
            ex = 1.0 if n else 0.0
            out += [ex, math.log1p(n), ex if ex else self.fuzzy(lab, surf), 1.0 if surf in self.ext.get(lab, ()) else 0.0]
        return np.array(out + [min(len(surf.split()), MAX_N) / MAX_N], dtype=np.float32)

    @property
    def dim(self) -> int:
        return len(self.labels) * len(FEATS) + 1


def doc_features(text: str, gaz: Gazetteer) -> Tuple[List[Tuple[int, int]], np.ndarray]:
    """Features for every candidate span of one doc. Returns ((start_tok, end_tok) list, [n_spans, dim])."""
    toks = tokens(text)
    cands = candidate_spans(toks)
    X = np.stack([gaz.features(text[toks[i][0]:toks[j - 1][1]]) for i, j in cands]) if cands else np.zeros((0, gaz.dim), np.float32)
    return cands, X


def crossfit_features(train_docs: Sequence[Tuple[str, Sequence[tuple]]], labels: Sequence[str], k: int = 5, seed: int = 0, ext_aliases=None):
    """Out-of-fold span features for TRAIN docs: doc i's features come from a gazetteer built on the other folds only."""
    n = len(train_docs)
    fold = np.random.RandomState(seed).permutation(n) % k
    out: List = [None] * n
    for f in range(k):
        gaz = Gazetteer.build((train_docs[i] for i in range(n) if fold[i] != f), labels, ext_aliases)
        for i in np.where(fold == f)[0]:
            out[i] = doc_features(train_docs[i][0], gaz)
    return out, fold


def project_to_tokens(n_tok: int, cands: Sequence[Tuple[int, int]], X: np.ndarray) -> np.ndarray:
    """m_i = [max over spans STARTING at i ; max over spans CONTINUING through i (start < i < end)] -> [n_tok, 2*dim]."""
    d = X.shape[1] if len(X) else 0
    B, I = np.zeros((n_tok, d), np.float32), np.zeros((n_tok, d), np.float32)
    for (i, j), x in zip(cands, X):
        B[i] = np.maximum(B[i], x)
        for t in range(i + 1, j):
            I[t] = np.maximum(I[t], x)
    return np.concatenate([B, I], axis=1)


def mask_metadata(m: np.ndarray, rng: np.random.RandomState, p: float = 0.3) -> np.ndarray:
    """Metadata dropout: zero the WHOLE m for a sentence with probability p (training only)."""
    return np.zeros_like(m) if rng.rand() < p else m
