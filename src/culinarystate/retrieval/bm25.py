"""Minimal Okapi BM25 (no external dependency) for evidence retrieval."""
from __future__ import annotations

import math
import re
from collections import Counter

_TOK = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "an", "of", "and", "or", "in", "on", "for", "to", "with", "by", "is", "it", "how", "what", "much",
        "does", "do", "i", "my", "after", "when"}


def tokenize(text: str) -> list[str]:
    out = []
    for w in _TOK.findall(text.lower()):
        if w in STOP:
            continue
        if w.endswith("ies") and len(w) > 4:
            w = w[:-3] + "y"
        elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
            w = w[:-1]
        out.append(w)
    return out


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.4, b: float = 0.75):
        self.k1, self.b = k1, b
        self.toks = [tokenize(d) for d in docs]
        self.tf = [Counter(t) for t in self.toks]
        self.len = [len(t) for t in self.toks]
        self.avg = sum(self.len) / max(1, len(self.len))
        df = Counter(w for t in self.toks for w in set(t))
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        self.postings: dict[str, list[int]] = {}
        for i, tf in enumerate(self.tf):
            for w in tf:
                self.postings.setdefault(w, []).append(i)

    def scores(self, query: str) -> dict[int, float]:
        out: dict[int, float] = {}
        for w in set(tokenize(query)):
            idf = self.idf.get(w)
            if idf is None:
                continue
            for i in self.postings[w]:
                f = self.tf[i][w]
                denom = f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
                out[i] = out.get(i, 0.0) + idf * f * (self.k1 + 1) / denom
        return out

    def top(self, query: str, k: int = 10) -> list[tuple[int, float]]:
        s = self.scores(query)
        return sorted(s.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
