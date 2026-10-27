"""35d cuisine explicit rungs C0-C2 and nulls, as pure functions.

Pre-registration draft 35.0 v1, section 7 (UNSIGNED). Nothing here reads files;
callers pass in-memory recipe-ingredient incidence. Tested on synthetic data only.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable, Mapping, Sequence

PAIR_MIN_SUPPORT = 20  # THR-35P-24 (draft)
TRIPLET_MIN_SUPPORT = 10  # THR-35P-24 (draft)
NULL_MODELS = ("U", "F", "C", "FC")  # = M0 / MF / MC / MFC of the draft null ladder
EXCLUDED_LEVELS = ("REGION", "UNKNOWN", "CONFLICTING", "NEEDS_HUMAN")


class LeakageError(ValueError):
    """A cuisine feature or weight would use the held-out / predicted cuisine."""


@dataclass(frozen=True)
class LabelledRecipe:
    recipe_id: str
    ingredients: frozenset
    label_level: str  # CUISINE | REGION | NEEDS_HUMAN | UNKNOWN | CONFLICTING (D-037)
    cuisine: str | None = None


@dataclass(frozen=True)
class CuisineCorpus:
    """Single-cuisine recipes grouped by cuisine, plus counts of what was excluded."""

    recipes: Mapping[str, tuple]  # cuisine -> tuple of frozenset ingredient sets
    excluded: Mapping[str, int] = field(default_factory=dict)

    @property
    def n_recipes(self) -> dict:
        return {c: len(r) for c, r in self.recipes.items()}


def require_single_cuisine(r: LabelledRecipe) -> None:
    """Raise unless the recipe carries a single-cuisine (CUISINE-level) label."""
    if r.label_level == "REGION":
        raise ValueError(f"REGION label never enters single-cuisine rungs (D-037): {r.recipe_id}")
    if r.label_level != "CUISINE" or not r.cuisine:
        raise ValueError(f"not a single-cuisine label ({r.label_level}): {r.recipe_id}")


def build_corpus(recipes: Iterable[LabelledRecipe], strict: bool = False) -> CuisineCorpus:
    """Keep CUISINE-level recipes; count and drop REGION/UNKNOWN/CONFLICTING/NEEDS_HUMAN.

    strict=True raises on any REGION recipe instead of dropping it.
    """
    groups: dict = {}
    excluded = {lvl: 0 for lvl in EXCLUDED_LEVELS}
    for r in recipes:
        if r.label_level == "CUISINE":
            require_single_cuisine(r)
            groups.setdefault(r.cuisine, []).append(frozenset(r.ingredients))
        elif r.label_level in excluded:
            if strict and r.label_level == "REGION":
                raise ValueError(f"REGION label never enters single-cuisine rungs (D-037): {r.recipe_id}")
            excluded[r.label_level] += 1
        else:
            raise ValueError(f"unknown label_level {r.label_level!r}: {r.recipe_id}")
    return CuisineCorpus({c: tuple(v) for c, v in groups.items()},
                         {k: v for k, v in excluded.items() if v})


def _active(corpus: CuisineCorpus, exclude: Sequence[str] = ()) -> dict:
    return {c: r for c, r in corpus.recipes.items() if c not in set(exclude)}


def c0_prevalence(corpus: CuisineCorpus, exclude: Sequence[str] = ()) -> dict:
    """C0: P(i | c) = share of the cuisine's recipes that contain ingredient i."""
    out = {}
    for c, recs in _active(corpus, exclude).items():
        counts: dict = {}
        for r in recs:
            for i in r:
                counts[i] = counts.get(i, 0) + 1
        out[c] = {i: n / len(recs) for i, n in counts.items()}
    return out


def c1_specificity(corpus: CuisineCorpus, exclude: Sequence[str] = ()) -> dict:
    """C1: A_i^c = P(i|c) - (1/(K-1)) * sum_{c' != c} P(i|c'), K = retained classes.

    K counts only cuisines not in `exclude` (held-out cuisines never contribute).
    Reported over the full retained vocabulary (absent ingredient -> P = 0).
    """
    p = c0_prevalence(corpus, exclude)
    k = len(p)
    if k < 2:
        raise ValueError("C1 needs K >= 2 retained cuisine classes")
    vocab = {i for d in p.values() for i in d}
    total = {i: sum(d.get(i, 0.0) for d in p.values()) for i in vocab}
    return {c: {i: d.get(i, 0.0) - (total[i] - d.get(i, 0.0)) / (k - 1) for i in vocab}
            for c, d in p.items()}


def idf_cuis(corpus: CuisineCorpus, exclude: Sequence[str] = ()) -> dict:
    """Cuisine-level IDF `idf_cuis` = ln(K / n_cuisines containing i). NOT `idf_rec`.

    The draft names idf_cuis but gives no formula; this is the classical form with
    cuisines as documents (flagged for sign-off).
    """
    p = c0_prevalence(corpus, exclude)
    k = len(p)
    df: dict = {}
    for d in p.values():
        for i in d:
            df[i] = df.get(i, 0) + 1
    return {i: math.log(k / n) for i, n in df.items()}


def assert_no_heldout(used_cuisines: Iterable[str], heldout: str | Iterable[str]) -> None:
    held = {heldout} if isinstance(heldout, str) else set(heldout)
    bad = held & set(used_cuisines)
    if bad:
        raise LeakageError(f"held-out cuisine(s) used by features: {sorted(bad)}")


def assert_weight_not_target_derived(weight_source: str, predicting: str) -> None:
    if weight_source == predicting:
        raise LeakageError(f"weight derived from cuisine {predicting!r} used to predict {predicting!r}")


def npmi(n_joint: int, n_each: Sequence[int], n_total: int) -> float:
    """Normalised PMI of an itemset: ln(p(xyz)/prod p(x)) / -ln p(xyz).

    Conventions: p(joint) = 1 gives 1.0. Triplet NPMI is the direct generalisation
    (draft says only "NPMI"; flagged for sign-off).
    """
    if n_joint <= 0 or n_total <= 0 or any(n <= 0 for n in n_each):
        raise ValueError("NPMI undefined for zero joint or marginal count")
    pj = n_joint / n_total
    if pj >= 1.0:
        return 1.0
    pmi = math.log(pj) - sum(math.log(n / n_total) for n in n_each)
    return pmi / -math.log(pj)


def c2_motifs(corpus: CuisineCorpus, cuisine: str, min_pair: int = PAIR_MIN_SUPPORT,
              min_triplet: int = TRIPLET_MIN_SUPPORT) -> dict:
    """C2: pair/triplet motifs inside one cuisine with support thresholds and NPMI."""
    if cuisine not in corpus.recipes:
        raise LookupError(f"cuisine {cuisine!r} not in corpus")
    recs = corpus.recipes[cuisine]
    n = len(recs)
    single: dict = {}
    pairs: dict = {}
    trips: dict = {}
    for r in recs:
        items = sorted(r)
        for i in items:
            single[i] = single.get(i, 0) + 1
        for pr in combinations(items, 2):
            pairs[pr] = pairs.get(pr, 0) + 1
        for tr in combinations(items, 3):
            trips[tr] = trips.get(tr, 0) + 1

    def pack(d, thr):
        return {m: {"support": s, "npmi": npmi(s, [single[i] for i in m], n)}
                for m, s in d.items() if s >= thr}

    return {"pairs": pack(pairs, min_pair), "triplets": pack(trips, min_triplet), "n_recipes": n}


def curveball(incidence: Mapping[str, frozenset], seed: int, n_trades: int | None = None) -> dict:
    """Degree-preserving Curveball randomisation (row and column sums kept). Seeded."""
    rng = random.Random(seed)
    keys = sorted(incidence)
    rows = {k: set(incidence[k]) for k in keys}
    if len(keys) >= 2:
        for _ in range(n_trades if n_trades is not None else 5 * len(keys)):
            a, b = rng.sample(keys, 2)
            only_a = sorted(rows[a] - rows[b])
            only_b = sorted(rows[b] - rows[a])
            if not only_a or not only_b:
                continue
            pool = only_a + only_b
            rng.shuffle(pool)
            rows[a] = (rows[a] - set(only_a)) | set(pool[:len(only_a)])
            rows[b] = (rows[b] - set(only_b)) | set(pool[len(only_a):])
    return {k: frozenset(v) for k, v in rows.items()}


def _sample(rng: random.Random, pool: Sequence[str], weights: Sequence[float] | None, k: int) -> list:
    if weights is None:
        return rng.sample(list(pool), k)
    keyed = sorted(((rng.random() ** (1.0 / w), i) for i, w in zip(pool, weights)), reverse=True)
    return [i for _, i in keyed[:k]]


def null_draw(incidence: Mapping[str, frozenset], model: str, seed: int,
              categories: Mapping[str, str] | None = None) -> dict:
    """One draw from U / F / C / FC (draft M0 / MF / MC / MFC); recipe size preserved.

    U: uniform over vocabulary. F: weighted by ingredient frequency. C: per-recipe
    category counts preserved, uniform within category. FC: C with frequency weights.
    """
    if model not in NULL_MODELS:
        raise ValueError(f"model must be one of {NULL_MODELS}")
    if model in ("C", "FC") and categories is None:
        raise ValueError(f"model {model} needs an ingredient -> category map")
    rng = random.Random(seed)
    freq: dict = {}
    for v in incidence.values():
        for i in v:
            freq[i] = freq.get(i, 0) + 1
    vocab = sorted(freq)
    weighted = model in ("F", "FC")
    by_cat: dict = {}
    if categories is not None:
        for i in vocab:
            if i not in categories:
                raise ValueError(f"ingredient {i!r} has no category")
            by_cat.setdefault(categories[i], []).append(i)
    out = {}
    for rid in sorted(incidence):
        ings = incidence[rid]
        if model in ("U", "F"):
            groups = [(vocab, len(ings))]
        else:
            counts: dict = {}
            for i in ings:
                counts[categories[i]] = counts.get(categories[i], 0) + 1
            groups = [(by_cat[c], n) for c, n in sorted(counts.items())]
        chosen: list = []
        for pool, k in groups:
            w = [freq[i] for i in pool] if weighted else None
            chosen += _sample(rng, pool, w, k)
        out[rid] = frozenset(chosen)
    return out
