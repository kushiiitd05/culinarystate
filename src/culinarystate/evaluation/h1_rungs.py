"""H1 rungs for the D5 state blocks (reports/del5/d5_benchmark_preregistration_DRAFT.md §2, §4). DRAFT.

What each rung sees for an S question about recipe ``steps`` cut after step ``cut``:
- B0: nothing (LLM only).
- B1: the top-k numbered step chunks by dense similarity to the question (``embed`` injected: texts -> vectors).
- B2: BM25 and dense rankings fused by reciprocal rank (k = 60).
- B4: B2's chunks plus the replayed state at the cut from the Rung A graph: ingredients used, heated so far, last
  action. Answers are requested in a strict format and scored at id level (ING / PROC), never by string similarity.

S178 (REV-B F-13, V16-P30; backward compatible, defaults keep the S173 behaviour): the legacy B4 state block prints
"Heated so far", i.e. the S1 gold computed by the same engine function, and B1/B2/B4 retrieval sees steps after the
cut. ``independent_context`` retrieves from the steps up to the cut only and prints no aggregate answer line.
``state_view`` MINIMAL (its default) prints only the ingredients used and the last action; PRIMITIVES also prints the
engine's event list (action + bound ingredient), from which a plain heat-verb rule rebuilds most S1 gold
(``h1_independence.heated_from_primitives``), so it stays circular. Only blind-first human gold (``h1_independence``)
makes H1 non-circular whichever view is used.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Callable, Sequence

from culinarystate.evaluation import d5_state as DS
from culinarystate.mechanism.router_demo import _attr, _lot_ingredients
from culinarystate.retrieval.bm25 import BM25

ROOT = Path(__file__).resolve().parents[3]
RUNGS = ("B0", "B1", "B2", "B4")
STATE_VIEWS = ("ANSWER", "PRIMITIVES", "MINIMAL", "NONE")   # ANSWER = S173 legacy (prints the S1 gold); NONE = B4 degenerates to B2
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


def state_block(steps: Sequence[str], cut: int, locale: str | None = None, *, view: str = "ANSWER") -> str:
    """Replayed state after step ``cut`` (only ``steps[:cut]`` are read).

    view ANSWER (default, S173 behaviour): ingredients used, "Heated so far", last action.
    view PRIMITIVES: ingredients used, ordered "Actions so far" (action word + bound ingredient names), last action;
    no heat classification, no parent-lot walk, so the S1 gold function is never called.
    view MINIMAL: ingredients used and last action only.
    view NONE: empty string.
    """
    if view not in STATE_VIEWS:
        raise ValueError(f"view must be one of {STATE_VIEWS}")
    if view == "NONE":
        return ""
    g = DS.graph("\n".join(steps[:cut]), locale)
    names = {}
    for e in g.entities:
        ing = _attr(e.attributes, "ingredient_id")
        if ing and e.span is not None:
            names.setdefault(ing, e.span.surface.lower())
    used = sorted(set(names.values()))
    acts = sorted(g.events, key=lambda ev: ev.span.char_start)
    last = acts[-1].span.surface.lower() if acts else "none"
    if view == "MINIMAL":
        return f"State after step {cut}:\nIngredients used: {', '.join(used) or 'none'}\nLast action: {last}"
    if view == "PRIMITIVES":
        items = []
        for ev in acts:
            objs = sorted(names.get(i, i) for i in _lot_ingredients(g, ev.consumes))
            items.append(ev.span.surface.lower() + (f" ({', '.join(objs)})" if objs else ""))
        return (f"State after step {cut}:\nIngredients used: {', '.join(used) or 'none'}\n"
                f"Actions so far: {'; '.join(items) or 'none'}\nLast action: {last}")
    heated = sorted(names.get(i, i) for i in DS.heated_ingredient_ids(g, _family()))
    return (f"State after step {cut}:\nIngredients used: {', '.join(used) or 'none'}\n"
            f"Heated so far: {', '.join(heated) or 'none'}\nLast action: {last}")


def context(rung: str, q: str, steps: Sequence[str], *, cut: int, embed: Callable, k: int = TOP_K,
            locale: str | None = None, pre_cut_only: bool = False, state_view: str = "ANSWER") -> str:
    """Context for one rung. ``pre_cut_only`` restricts the retrieval pool to ``steps[:cut]`` (S178 fix; the S173
    default retrieves from every step, including the ones after the question point)."""
    if rung not in RUNGS:
        raise ValueError(f"rung must be one of {RUNGS}")
    if rung == "B0":
        return ""
    ch = chunks(steps[:cut] if pre_cut_only else steps)
    texts = [t for _, t in ch]
    if not texts:
        return "" if rung != "B4" else state_block(steps, cut, locale, view=state_view)
    order = _dense_rank(q, texts, embed) if rung == "B1" else rrf([_bm25_rank(q, texts), _dense_rank(q, texts, embed)])
    top = sorted(order[:k])
    ctx = "\n".join(texts[i] for i in top)
    if rung != "B4":
        return ctx
    block = state_block(steps, cut, locale, view=state_view)
    return ctx + ("\n\n" + block if block else "")


def independent_context(rung: str, q: str, steps: Sequence[str], *, cut: int, embed: Callable, k: int = TOP_K,
                        locale: str | None = None, state_view: str = "MINIMAL") -> str:
    """The S178 contexts: pre-cut retrieval pool and no aggregate answer line in the B4 state block."""
    return context(rung, q, steps, cut=cut, embed=embed, k=k, locale=locale, pre_cut_only=True, state_view=state_view)


def prompt(block: str, q: str, ctx: str) -> str:
    fmt = ("Answer with a comma-separated list of ingredient names only, or 'none'." if block == "S1"
           else "Answer with one cooking verb only (the next action).")
    head = f"Context:\n{ctx}\n\n" if ctx else ""
    return f"{head}Question: {q}\n{fmt}\nAnswer:"


def score_s1_detail(answer: str, gold_ids: set[str], link: Callable[[str], str | None]) -> dict:
    """Id-level S1 scoring with the link outcome kept: ``link_failed`` is True when any listed name has no ING id.

    A failed link counts as wrong (as in S173) but is reported separately, so a rung whose surface strings the
    engine's own linker cannot resolve is visible (REV-B F-13: linker asymmetry between engine-fed and free-text rungs).
    """
    a = (answer or "").strip().strip(".").lower()
    if a in ("none", "nothing", ""):
        return {"correct": not gold_ids, "link_failed": False, "n_items": 0, "n_unlinked": 0, "said_none": True}
    items = [x.strip(" .") for x in re.split(r",|\band\b", a) if x.strip(" .")]
    ids = [link(x) for x in items]
    unlinked = sum(i is None for i in ids)
    return {"correct": unlinked == 0 and set(ids) == set(gold_ids), "link_failed": unlinked > 0,
            "n_items": len(items), "n_unlinked": unlinked, "said_none": False}


def score_s1(answer: str, gold_ids: set[str], link: Callable[[str], str | None]) -> bool:
    return score_s1_detail(answer, gold_ids, link)["correct"]


def link_failure_rate(details: Sequence[dict]) -> dict:
    """Questions with at least one unlinkable name / questions answered with names (rung-level counts)."""
    named = [d for d in details if not d.get("said_none")]
    failed = sum(bool(d.get("link_failed")) for d in named)
    return {"n_questions": len(details), "n_named": len(named), "n_link_failed": failed,
            "rate": round(failed / len(named), 4) if named else None}


def score_s2(answer: str, gold_proc: str, proc: Callable[[str], str | None]) -> bool:
    m = re.search(r"[a-z][a-z-]*", (answer or "").lower())
    return bool(m) and proc(m.group(0)) == gold_proc
