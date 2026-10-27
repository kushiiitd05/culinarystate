"""Step 35c recipe explicit rungs R0-R3 as pure functions (synthetic-safe).

Definitions follow reports/step35/preregistration_35_0_v1_draft.md section 6.
Nothing here reads files or touches real data. UNKNOWN is returned as None,
never as 0. All inputs are left unmodified; outputs are new objects.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Collection, Iterable, Mapping, Optional, Sequence

GROUPING_LABEL = "DESCRIPTIVE_CONSERVATIVE_GROUPING"
SINGLE_REVIEWER_CAVEAT = (
    "07I-C groups rest on a single-reviewer basis (DECISIONS D-033: 0.88 is a "
    "Kush-declared adjudicated-basis figure, not an inter-reviewer kappa); "
    "descriptive only, not headline."
)
# PROPOSED_PILOT, unsigned (THR-35P-19, THR-35P-21).
PROPOSED_COVERAGE_FLOOR = 0.80
PROPOSED_SPLIT_FRACTIONS = (0.6, 0.2, 0.2)
PARTITIONS = ("train", "dev", "test")


class LeakageError(ValueError):
    """A split group spans more than one partition (or is unassigned)."""


# ---------------------------------------------------------------- R0
def r0_jaccard(a: Collection[str], b: Collection[str]) -> Optional[float]:
    """Binary-incidence Jaccard; None (UNKNOWN) when both sets are empty."""
    sa, sb = set(a), set(b)
    union = len(sa | sb)
    return None if union == 0 else len(sa & sb) / union


def r0_cosine(a: Collection[str], b: Collection[str]) -> Optional[float]:
    """Binary-incidence cosine; None when either set is empty."""
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return None
    return len(sa & sb) / math.sqrt(len(sa) * len(sb))


# ---------------------------------------------------------------- idf_rec
def compute_idf_rec(train_recipes: Iterable[Collection[str]]) -> dict[str, float]:
    """Recipe-level IDF (idf_rec) from TRAINING-partition recipes only.

    w = max(0, ln(N / (1 + df))). Not to be confused with cuisine-level idf_cuis.
    """
    recipes = [set(r) for r in train_recipes]
    n = len(recipes)
    df: dict[str, int] = {}
    for r in recipes:
        for ing in r:
            df[ing] = df.get(ing, 0) + 1
    return {ing: max(0.0, math.log(n / (1 + d))) for ing, d in sorted(df.items())}


def idf_rec_weight(idf_rec: Mapping[str, float], n_train: int, ing: str) -> float:
    """Weight of an ingredient; unseen in training means df = 0."""
    if ing in idf_rec:
        return idf_rec[ing]
    return max(0.0, math.log(n_train / 1)) if n_train > 0 else 0.0


def _w(idf_rec: Mapping[str, float], n_train: int, ing: str) -> float:
    return idf_rec_weight(idf_rec, n_train, ing)


def idf_jaccard(a, b, idf_rec, n_train) -> Optional[float]:
    """IDF-weighted Jaccard (kNN memorisation alarm); None if union weight is 0."""
    sa, sb = set(a), set(b)
    union = sum(_w(idf_rec, n_train, i) for i in sa | sb)
    if union == 0:
        return None
    return sum(_w(idf_rec, n_train, i) for i in sa & sb) / union


# ---------------------------------------------------------------- R2
def r2_tfidf_cosine(a, b, idf_rec, n_train) -> Optional[float]:
    """TF-IDF incidence cosine (binary tf); None when either vector has zero norm."""
    sa, sb = set(a), set(b)
    na = math.sqrt(sum(_w(idf_rec, n_train, i) ** 2 for i in sa))
    nb = math.sqrt(sum(_w(idf_rec, n_train, i) ** 2 for i in sb))
    if na == 0 or nb == 0:
        return None
    dot = sum(_w(idf_rec, n_train, i) ** 2 for i in sa & sb)
    return dot / (na * nb)


# ---------------------------------------------------------------- R1
@dataclass(frozen=True)
class R1Result:
    vector: Optional[tuple[float, ...]]
    n_profiled: int
    n_total: int
    coverage: float
    label: str = "COVERAGE_LIMITED_PROFILED_ING"


def r1_mean_profile(recipe: Collection[str],
                    z: Mapping[str, Sequence[float]]) -> R1Result:
    """Mean of explicit z_i over profiled ingredients only; others are masked."""
    ings = sorted(set(recipe))
    prof = [i for i in ings if i in z]
    cov = len(prof) / len(ings) if ings else 0.0
    if not prof:
        return R1Result(None, 0, len(ings), cov)
    dim = len(z[prof[0]])
    vec = tuple(sum(z[i][d] for i in prof) / len(prof) for d in range(dim))
    return R1Result(vec, len(prof), len(ings), cov)


# ---------------------------------------------------------------- R3
def r3_mass_shares(mass: Mapping[str, Optional[float]]) -> Optional[dict[str, float]]:
    """Quantity-weighted mass shares; None (masked) if any mass is missing."""
    if not mass or any(v is None for v in mass.values()):
        return None
    total = sum(mass.values())  # type: ignore[arg-type]
    if total <= 0:
        return None
    return {k: v / total for k, v in mass.items()}  # type: ignore[operator]


# ---------------------------------------------------------------- shortcut
def frequency_only_ranking(train_recipes: Iterable[Collection[str]],
                           exclude: Collection[str] = ()) -> tuple[str, ...]:
    """Rank ingredients by training prevalence, ties broken by id."""
    cnt: dict[str, int] = {}
    for r in train_recipes:
        for i in set(r):
            cnt[i] = cnt.get(i, 0) + 1
    ex = set(exclude)
    return tuple(i for i, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
                 if i not in ex)


# ---------------------------------------------------------------- masking
@dataclass(frozen=True)
class CoverageResult:
    kept: tuple[str, ...]
    excluded: tuple[str, ...]
    coverage: dict
    n_excluded: int
    n_no_lines: int
    floor: float


def apply_link_coverage_floor(recipes: Mapping[str, tuple[int, int]],
                              floor: float = PROPOSED_COVERAGE_FLOOR) -> CoverageResult:
    """recipes: id -> (linked_lines, total_lines). Below floor (or no lines) is
    excluded and counted, never imputed. coverage == floor is kept."""
    if not 0.0 <= floor <= 1.0:
        raise ValueError("floor must be in [0, 1]")
    kept, excl, cov, no_lines = [], [], {}, 0
    for rid in sorted(recipes):
        linked, total = recipes[rid]
        if linked < 0 or total < 0 or linked > total:
            raise ValueError(f"invalid line counts for {rid}: {linked}/{total}")
        if total == 0:
            cov[rid] = None
            excl.append(rid)
            no_lines += 1
            continue
        c = linked / total
        cov[rid] = c
        (kept if c >= floor else excl).append(rid)
    return CoverageResult(tuple(kept), tuple(excl), cov, len(excl), no_lines, floor)


# ---------------------------------------------------------------- metrics
def _check_k(k: int) -> None:
    if k < 1:
        raise ValueError("k must be >= 1")


def hit_at_k(ranked: Sequence[str], relevant: Collection[str], k: int) -> Optional[float]:
    _check_k(k)
    rel = set(relevant)
    if not rel:
        return None
    return 1.0 if any(x in rel for x in ranked[:k]) else 0.0


def recall_at_k(ranked: Sequence[str], relevant: Collection[str], k: int) -> Optional[float]:
    _check_k(k)
    rel = set(relevant)
    if not rel:
        return None
    return len(rel & set(ranked[:k])) / len(rel)


def mrr(ranked: Sequence[str], relevant: Collection[str]) -> Optional[float]:
    rel = set(relevant)
    if not rel:
        return None
    for pos, x in enumerate(ranked, start=1):
        if x in rel:
            return 1.0 / pos
    return 0.0


def ndcg_at_k(ranked: Sequence[str], relevant: Collection[str], k: int) -> Optional[float]:
    """Binary-gain nDCG with log2(rank+1) discount."""
    _check_k(k)
    rel = set(relevant)
    if not rel:
        return None
    dcg = sum(1.0 / math.log2(p + 1) for p, x in enumerate(ranked[:k], 1) if x in rel)
    idcg = sum(1.0 / math.log2(p + 1) for p in range(1, min(len(rel), k) + 1))
    return dcg / idcg


@dataclass(frozen=True)
class StratifiedRecall:
    per_bin: dict
    n_per_bin: dict
    macro: Optional[float]


def frequency_bin(freq: float, edges: Sequence[float]) -> int:
    """Bin index = number of edges <= freq (edges ascending, supplied by caller)."""
    return sum(1 for e in edges if freq >= e)


def frequency_stratified_macro_recall(queries: Iterable[tuple[str, Sequence[str]]],
                                      freq: Mapping[str, float],
                                      edges: Sequence[float], k: int) -> StratifiedRecall:
    """queries: (masked target item, ranked list). Binned by the target's
    corpus frequency; macro = unweighted mean over non-empty bins."""
    _check_k(k)
    sums: dict[int, float] = {}
    ns: dict[int, int] = {}
    for target, ranked in queries:
        b = frequency_bin(freq[target], edges)
        r = recall_at_k(ranked, {target}, k)
        sums[b] = sums.get(b, 0.0) + r  # type: ignore[operator]
        ns[b] = ns.get(b, 0) + 1
    per_bin = {b: sums[b] / ns[b] for b in sorted(sums)}
    macro = sum(per_bin.values()) / len(per_bin) if per_bin else None
    return StratifiedRecall(per_bin, {b: ns[b] for b in sorted(ns)}, macro)


# ---------------------------------------------------------------- splitter
@dataclass(frozen=True)
class SplitResult:
    recipe_partition: dict
    group_partition: dict
    seed: int
    fractions: tuple
    grouping_label: str = GROUPING_LABEL
    headline_eligible: bool = False
    caveat: str = SINGLE_REVIEWER_CAVEAT


def _h(seed: int, group: str) -> str:
    return hashlib.sha256(f"{seed}|{group}".encode()).hexdigest()


def split_by_group(table: Mapping[str, str], seed: int,
                   fractions: Sequence[float] = PROPOSED_SPLIT_FRACTIONS,
                   strata: Optional[Mapping[str, str]] = None) -> SplitResult:
    """Deterministic group-level train/dev/test split; whole groups stay together.

    table: recipe_id -> split_group_id. strata (optional): group_id -> stratum;
    groups are ordered by hash inside each stratum and cut by fraction.
    """
    if not table:
        raise ValueError("empty recipe->group table")
    if len(fractions) != 3 or abs(sum(fractions) - 1.0) > 1e-9 or min(fractions) < 0:
        raise ValueError("fractions must be 3 non-negative values summing to 1")
    groups = sorted(set(table.values()))
    by_stratum: dict[str, list[str]] = {}
    for g in groups:
        by_stratum.setdefault(strata[g] if strata else "", []).append(g)
    gpart: dict[str, str] = {}
    for s in sorted(by_stratum):
        gs = sorted(by_stratum[s], key=lambda g: (_h(seed, g), g))
        n = len(gs)
        n_tr = round(n * fractions[0])
        n_dev = round(n * fractions[1])
        for i, g in enumerate(gs):
            gpart[g] = PARTITIONS[0] if i < n_tr else (
                PARTITIONS[1] if i < n_tr + n_dev else PARTITIONS[2])
    rec = {r: gpart[g] for r, g in sorted(table.items())}
    res = SplitResult(rec, dict(sorted(gpart.items())), seed, tuple(fractions))
    assert_group_disjoint(table, rec)
    return res


def assert_group_disjoint(table: Mapping[str, str],
                          recipe_partition: Mapping[str, str]) -> None:
    """Raise LeakageError if any group spans >1 partition or a recipe is unassigned."""
    seen: dict[str, set[str]] = {}
    for rid, g in table.items():
        if rid not in recipe_partition:
            raise LeakageError(f"recipe {rid} has no partition")
        seen.setdefault(g, set()).add(recipe_partition[rid])
    bad = sorted(g for g, p in seen.items() if len(p) > 1)
    if bad:
        raise LeakageError(f"groups span multiple partitions: {bad}")
