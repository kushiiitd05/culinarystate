"""H1 rungs for the D5 state blocks (reports/del5/d5_benchmark_preregistration_DRAFT.md §2, §4). DRAFT.

What each rung sees for an S question about recipe ``steps`` cut after step ``cut``:
- B0: nothing (LLM only).
- B1: the top-k numbered step chunks by dense similarity to the question (``embed`` injected: texts -> vectors).
- B2: BM25 and dense rankings fused by reciprocal rank (k = 60).
- B4: B2's chunks plus the replayed state at the cut from the Rung A graph: ingredients used, heated so far, last
  action. Answers are requested in a strict format and scored at id level (ING / PROC), never by string similarity.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Callable, Sequence

from culinarystate.evaluation import d5_state as DS
from culinarystate.mechanism.router_demo import _attr
from culinarystate.retrieval.bm25 import BM25

ROOT = Path(__file__).resolve().parents[3]
RUNGS = ("B0", "B1", "B2", "B4")
TOP_K = 4
_FAMILY: dict[str, str] = {}


def _family() -> dict[str, str]:
    if not _FAMILY:
        with open(ROOT / "ledgers/data/PROC.jsonl", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    _FAMILY[r["id"]] = r.get("family")
    return _FAMILY


def chunks(steps: Sequence[str]) -> list[tuple[int, str]]:
    return [(i + 1, f"Step {i + 1}: {s}") for i, s in enumerate(steps)]


def rrf(rankings: Sequence[Sequence[int]], k: int = 60) -> list[int]:
    score: dict[int, float] = {}
    for r in rankings:
        for pos, i in enumerate(r):
            score[i] = score.get(i, 0.0) + 1.0 / (k + pos + 1)
    return sorted(score, key=lambda i: (-score[i], i))


def _cos(a, b) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def _dense_rank(q: str, texts: list[str], embed: Callable) -> list[int]:
    vecs = embed([q] + texts)
    sims = [_cos(vecs[0], v) for v in vecs[1:]]
    return sorted(range(len(texts)), key=lambda i: (-sims[i], i))


def _bm25_rank(q: str, texts: list[str]) -> list[int]:
    s = BM25(texts).scores(q)
    return sorted(range(len(texts)), key=lambda i: (-s.get(i, 0.0), i))


def state_block(steps: Sequence[str], cut: int, locale: str | None = None) -> str:
    g = DS.graph("\n".join(steps[:cut]), locale)
    names = {}
    for e in g.entities:
        ing = _attr(e.attributes, "ingredient_id")
        if ing and e.span is not None:
            names.setdefault(ing, e.span.surface.lower())
    heated = sorted(names.get(i, i) for i in DS.heated_ingredient_ids(g, _family()))
    used = sorted(set(names.values()))
    acts = sorted(g.events, key=lambda ev: ev.span.char_start)
    last = acts[-1].span.surface.lower() if acts else "none"
    return (f"State after step {cut}:\nIngredients used: {', '.join(used) or 'none'}\n"
            f"Heated so far: {', '.join(heated) or 'none'}\nLast action: {last}")


def context(rung: str, q: str, steps: Sequence[str], *, cut: int, embed: Callable, k: int = TOP_K,
            locale: str | None = None) -> str:
    if rung not in RUNGS:
        raise ValueError(f"rung must be one of {RUNGS}")
    if rung == "B0":
        return ""
    ch = chunks(steps)
    texts = [t for _, t in ch]
    order = _dense_rank(q, texts, embed) if rung == "B1" else rrf([_bm25_rank(q, texts), _dense_rank(q, texts, embed)])
    top = sorted(order[:k])
    ctx = "\n".join(texts[i] for i in top)
    return ctx + ("\n\n" + state_block(steps, cut, locale) if rung == "B4" else "")


def prompt(block: str, q: str, ctx: str) -> str:
    fmt = ("Answer with a comma-separated list of ingredient names only, or 'none'." if block == "S1"
           else "Answer with one cooking verb only (the next action).")
    head = f"Context:\n{ctx}\n\n" if ctx else ""
    return f"{head}Question: {q}\n{fmt}\nAnswer:"


def score_s1(answer: str, gold_ids: set[str], link: Callable[[str], str | None]) -> bool:
    a = (answer or "").strip().strip(".").lower()
    if a in ("none", "nothing", ""):
        return not gold_ids
    items = [x.strip(" .") for x in re.split(r",|\band\b", a) if x.strip(" .")]
    ids = [link(x) for x in items]
    return None not in ids and set(ids) == set(gold_ids)


def score_s2(answer: str, gold_proc: str, proc: Callable[[str], str | None]) -> bool:
    m = re.search(r"[a-z][a-z-]*", (answer or "").lower())
    return bool(m) and proc(m.group(0)) == gold_proc
