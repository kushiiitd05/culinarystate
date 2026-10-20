#!/usr/bin/env python3
"""S119 Part IX prep (laptop): span-knowledge feature tables for the frozen benchmark.

  nice -n 10 /opt/anaconda3/bin/python tools/build_span_features.py tasteset      # -> features/<ds>_span_feats_v1.npz
Train docs: 5-fold out-of-fold gazetteer; calibration/dev/test: full-train gazetteer (train split ONLY, never calibration/dev/test text).
Candidates = all n-grams <= 6 tokens generated before NER. Output per word position (aligned with the trainer's WORD tokenisation):
m_i = [B-slot ; I-slot] max-pooled span features, float16. Layout: M [total_words, 2*dim], offsets [n_docs+1].
Surface-level memoisation keeps RecipeDB3 tractable on 8 GB."""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.ner import benchmark as B  # noqa: E402
from culinarystate.ner import spans as S  # noqa: E402
import freeze_ner_benchmark as F  # noqa: E402


class MemoGaz(S.Gazetteer):
    def features(self, surf):
        k = surf.lower()
        if k not in self._memo:
            self._memo[k] = super().features(k)
        return self._memo[k]


def build(gaz_cls_docs, labels, ext=None):
    g = MemoGaz.build(gaz_cls_docs, labels, ext)
    g._memo = {}
    return g


def doc_matrix(text, gaz):
    cands, X = S.doc_features(text, gaz)
    return S.project_to_tokens(len(S.tokens(text)), cands, X)


def main():
    ds = sys.argv[1]
    if ds == "tasteset":
        df = pd.read_csv(F.TASTE)
        docs_fn = lambda idx: F.docs_taste(df, idx)
        labels = sorted(B.VIEWS["tasteset_native"])
    else:
        df, _ = F.load_rdb3()
        docs_fn = lambda idx: F.docs_rdb3(df, idx)
        labels = sorted(B.VIEWS["recipedb3_published"])
    sp = json.loads((ROOT / "benchmark/ner/splits" / f"{ds}_split_v1.json").read_text())["indices"]
    n_all = max(max(v) for k, v in sp.items() if k in ("train", "calibration", "dev", "test") and v) + 1
    mats = [None] * n_all
    t0 = time.time()
    tr_docs = docs_fn(sp["train"])
    k = 5
    fold = np.random.RandomState(0).permutation(len(tr_docs)) % k
    for f in range(k):
        gz = build((tr_docs[i] for i in range(len(tr_docs)) if fold[i] != f), labels)
        for i in np.where(fold == f)[0]:
            mats[sp["train"][i]] = doc_matrix(tr_docs[i][0], gz)
        print("fold", f, round(time.time() - t0), "s", flush=True)
    full = build(tr_docs, labels)
    for part in ("calibration", "dev", "test"):
        for i, d in zip(sp[part], docs_fn(sp[part])):
            mats[i] = doc_matrix(d[0], full)
    dim = next(m for m in mats if m is not None).shape[1]
    mats = [m if m is not None else np.zeros((0, dim), np.float32) for m in mats]
    off = np.cumsum([0] + [len(m) for m in mats])
    out = ROOT / "features"
    out.mkdir(exist_ok=True)
    np.savez_compressed(out / f"{ds}_span_feats_v1.npz", M=np.concatenate(mats).astype(np.float16), offsets=off, labels=np.array(labels), fold=fold)
    print(ds, "docs", n_all, "dim", dim, "seconds", round(time.time() - t0))


if __name__ == "__main__":
    main()
