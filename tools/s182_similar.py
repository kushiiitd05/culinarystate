"""S182 similar-recipe index over the whole recipe base (612,782 recipes), searched locally.

What leaves the machine is decided per family by ``policy``, from ``recipe_base_v1.parquet``'s
``licence_status`` / ``local_only`` columns:

* WIKIBOOKS (CC BY-SA, not local-only): title, link and steps may be shown and sent to the hosted model.
* GUTENBERG_SEGMENT (public domain, not local-only): title may be shown; steps are not held locally.
* everything else (BBC D-003, Food.com uploader-declared CC0 with unverified authority, TASTEset):
  COUNT_ONLY. Matched locally, counted, never shown, never sent.

TF-IDF over titles (plus Wikibooks ingredient/technique names), cosine similarity. Diagnostic only:
"similar" means shared words, not a judged culinary equivalence.
"""
from __future__ import annotations

import json
import pickle
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
RECIPE_BASE = ROOT / "ledgers/recipe_base/recipe_base_v1.parquet"
WIKIBOOKS = ROOT / "data/interim/wikibooks/recipes.jsonl"
CACHE = ROOT / "data/derived/s182_similar_index_v1.pkl"   # git-ignored (data/derived/)
MIN_SCORE = 0.25
TOP_N = 300
SHOW = 4
REFERENCE_CANDIDATES = 5
_POLICY = {"WIKIBOOKS": "SHOW_AND_SEND", "GUTENBERG_SEGMENT": "SHOW_TITLE"}
_LICENCE = {"WIKIBOOKS": "CC BY-SA (Wikibooks Cookbook)", "GUTENBERG_SEGMENT": "Public domain (Project Gutenberg)"}


_WORD = re.compile(r"[a-z][a-z]+")


def tokens(text: str) -> list[str]:
    """Lower-case words with a light plural fold: tomatoes -> tomato, eggs -> egg (kept picklable)."""
    out = []
    for w in _WORD.findall(text.lower()):
        if len(w) > 4 and w.endswith("oes"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def policy(family: str) -> str:
    return _POLICY.get(family, "COUNT_ONLY")


def _wikibooks_docs(path: Path = WIKIBOOKS) -> list[dict[str, Any]]:
    docs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        names = [l[2] for part in (r.get("ingredients") or []) for l in (part.get("links") or [])]
        steps = " ".join(s.get("text", "") for s in (r.get("steps") or []))
        docs.append({"id": f"WIKIBOOKS:{r['pageid']}", "family": "WIKIBOOKS", "title": r["title"],
                     "text": " ".join(names), "url": r.get("url"), "steps": steps or None})
    return docs


def _base_docs(skip_families: Iterable[str] = ("WIKIBOOKS",)) -> list[dict[str, Any]]:
    import pandas as pd
    df = pd.read_parquet(RECIPE_BASE, columns=["recipe_id", "source_family", "title_raw"])
    df = df[~df["source_family"].isin(list(skip_families))]
    return [{"id": rid, "family": fam, "title": str(t or ""), "text": "", "url": None, "steps": None}
            for rid, fam, t in zip(df["recipe_id"], df["source_family"], df["title_raw"])]


class SimilarIndex:
    def __init__(self, vectorizer, matrix, meta: list[dict[str, Any]]) -> None:
        self.vec, self.X, self.meta = vectorizer, matrix, meta

    @classmethod
    def from_docs(cls, docs: list[Mapping[str, Any]], *, min_df: int = 2) -> "SimilarIndex":
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        stop = sorted({t for w in ENGLISH_STOP_WORDS for t in tokens(w)})
        vec = TfidfVectorizer(tokenizer=tokens, lowercase=False, token_pattern=None, stop_words=stop,
                              sublinear_tf=True, min_df=min_df)
        X = vec.fit_transform([f"{d['title']} {d['title']} {d.get('text') or ''}" for d in docs])
        meta = [{k: d.get(k) for k in ("id", "family", "title", "url", "steps")} for d in docs]
        return cls(vec, X, meta)

    @classmethod
    def load(cls, cache: Path = CACHE) -> "SimilarIndex":
        """Build once (~30 s over 612k titles), then load the pickle (~2 s). The cache never leaves data/derived/."""
        if cache.exists():
            with cache.open("rb") as fh:
                return pickle.load(fh)
        idx = cls.from_docs(_wikibooks_docs() + _base_docs())
        cache.parent.mkdir(parents=True, exist_ok=True)
        with cache.open("wb") as fh:
            pickle.dump(idx, fh, protocol=pickle.HIGHEST_PROTOCOL)
        return idx

    def _scores(self, recipe_text: str, foods: list[str], processes: Iterable[str]):
        """Cosine scores, zeroed for documents that contain none of the recipe's foods."""
        import numpy as np
        if foods:
            query = " ".join([*foods, *foods, *foods, *processes])
        else:
            query = re.sub(r"\s+", " ", recipe_text)[:2000]
        scores = (self.X @ self.vec.transform([query]).T).toarray().ravel()
        vocab = self.vec.vocabulary_
        cols = sorted({vocab[t] for f in foods for t in tokens(f) if t in vocab})
        if cols:
            has_food = np.asarray((self.X[:, cols] > 0).sum(axis=1)).ravel() > 0
            scores = np.where(has_food, scores, 0.0)
        elif foods:
            scores = np.zeros_like(scores)
        return scores

    def search(self, recipe_text: str, foods: list[str], processes: Iterable[str] = ()) -> dict[str, Any]:
        processes = list(processes)
        scores = self._scores(recipe_text, foods, processes)
        import numpy as np
        families = np.array([m["family"] for m in self.meta]) if not hasattr(self, "_fam") else self._fam
        self._fam = families
        fam, n = np.unique(families[scores >= MIN_SCORE], return_counts=True)
        counts = {str(f): int(c) for f, c in zip(fam, n)}
        order = scores.argsort()[::-1][:TOP_N]
        public, hidden, seen = [], [], set()
        for i in order:
            s = float(scores[i])
            if s < MIN_SCORE:
                break
            m = self.meta[i]
            rule = policy(m["family"])
            if rule == "COUNT_ONLY":
                hidden.append({"family": m["family"], "score": round(s, 3)})
                continue
            key = (m["family"], m["title"].strip().lower())
            if key in seen:
                continue
            seen.add(key)
            public.append({"id": m["id"], "family": m["family"], "title": m["title"], "score": round(s, 3),
                           "url": m["url"], "licence": _LICENCE[m["family"]],
                           "steps_available": rule == "SHOW_AND_SEND" and bool(m["steps"])})
        cands = self._top_wikibooks(scores, REFERENCE_CANDIDATES)
        wiki = [self._public_row(rid, scores) for rid in cands[:SHOW // 2]]
        others = [p for p in public if p["family"] != "WIKIBOOKS" and p["id"] not in cands]
        shown = (wiki + others)[:SHOW]
        return {"query_foods": list(foods), "query_processes": processes, "counts": counts, "shown": shown,
                "hidden": hidden, "searched": len(self.meta), "min_score": MIN_SCORE,
                "reference_id": cands[0] if cands else None, "reference_candidates": cands}

    def _public_row(self, rid: str, scores) -> dict[str, Any]:
        i = self._pos[rid] if hasattr(self, "_pos") else next(j for j, m in enumerate(self.meta) if m["id"] == rid)
        m = self.meta[i]
        return {"id": m["id"], "family": m["family"], "title": m["title"], "score": round(float(scores[i]), 3),
                "url": m["url"], "licence": _LICENCE[m["family"]], "steps_available": bool(m["steps"])}

    def _top_wikibooks(self, scores, k: int) -> list[str]:
        ranked = sorted(((float(scores[i]), m["id"]) for i, m in enumerate(self.meta)
                         if m["family"] == "WIKIBOOKS" and m["steps"] and scores[i] >= MIN_SCORE / 2), reverse=True)
        return [rid for _, rid in ranked[:k]]

    def public_steps(self, rid: str) -> dict[str, Any] | None:
        m = next((m for m in self.meta if m["id"] == rid and policy(m["family"]) == "SHOW_AND_SEND"), None)
        if m is None:
            return None
        return {"id": m["id"], "family": m["family"], "title": m["title"], "url": m["url"],
                "licence": _LICENCE[m["family"]], "steps": m["steps"]}

    def best_public_steps(self, result: Mapping[str, Any]) -> dict[str, Any] | None:
        """The best-scoring Wikibooks recipe (any rank) for this query, with its steps text."""
        rid = result.get("reference_id")
        return self.public_steps(rid) if rid else None
