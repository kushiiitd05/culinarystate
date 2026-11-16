"""D5 benchmark drafting, P/C blocks (reports/del5/d5_benchmark_preregistration_DRAFT.md §1). AI draft; humans review.

stratum: DIRECT (an exact ingredient x process row with a measured value for the target), SIMILAR_ONLY (none exact, but
a parent ingredient has one), NONE (neither: gold ABSTAIN). Phrasings rotate over several templates so the router and
verbaliser are not scored on a single wording. Selection is seeded (smallest sha256(seed || cell)) with a quota per
stratum and a cap per ingredient. Pure functions; the tool loads the ledgers.
"""
from __future__ import annotations

import hashlib
from typing import Mapping, Sequence

GOLD_MODE = {"DIRECT": "ANSWER", "SIMILAR_ONLY": "ANSWER_SIMILAR_ONLY", "NONE": "ABSTAIN"}
EFFECT_TEMPLATES = (
    "How much {target} does {past} {food} keep?",
    "If I {verb} {food}, what happens to its {target}?",
    "Does {verb}ing {food} destroy the {target}?",
    "What share of the {target} is left after {food} is {past}?",
    "I {past} some {food}. How much {target} survives?",
)
COMPARE_TEMPLATES = (
    "Is it better to {p1} or {p2} {food} if I want to keep the {target}?",
    "Which keeps more {target} in {food}: {p1} or {p2}?",
    "For {food}, does {p1} or {p2} lose less {target}?",
)


def stratum(ing: str | None, proc: str, pairs: Mapping[tuple[str, str], list[str]],
            parents: Mapping[str, Sequence[str]]) -> tuple[str, list[str]]:
    if not ing:
        return "NONE", []
    if pairs.get((ing, proc)):
        return "DIRECT", list(pairs[(ing, proc)])
    near = [e for p in parents.get(ing, ()) for e in pairs.get((p, proc), [])]
    return ("SIMILAR_ONLY", near) if near else ("NONE", [])


def phrase_effect(i: int, food: str, past: str, verb: str, target: str) -> str:
    t = EFFECT_TEMPLATES[i % len(EFFECT_TEMPLATES)]
    v = verb[:-1] if t.find("{verb}ing") >= 0 and verb.endswith("e") else verb
    return t.format(food=food, past=past, verb=v, target=target)


def phrase_compare(i: int, food: str, procs: tuple[str, str], target: str) -> str:
    return COMPARE_TEMPLATES[i % len(COMPARE_TEMPLATES)].format(food=food, p1=procs[0], p2=procs[1], target=target)


def seeded_pick(cells: Sequence[Mapping], *, seed: str, quota: Mapping[str, int],
                max_per_ingredient: int | None = None) -> list[dict]:
    out = []
    for s, q in quota.items():
        ranked = sorted((c for c in cells if c["stratum"] == s),
                        key=lambda c: hashlib.sha256((seed + str(c["cell"])).encode()).hexdigest())
        taken, per = [], {}
        for c in ranked:
            ing = c.get("ingredient_id")
            if max_per_ingredient is not None and ing is not None and per.get(ing, 0) >= max_per_ingredient:
                continue
            taken.append(dict(c))
            per[ing] = per.get(ing, 0) + 1
            if len(taken) == q:
                break
        if len(taken) < q:
            raise ValueError(f"stratum {s}: {len(taken)} eligible cells, quota {q}")
        out += taken
    return out
