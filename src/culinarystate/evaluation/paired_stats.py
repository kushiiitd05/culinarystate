"""Paired statistics for H1 (reports/del5/d5_benchmark_preregistration_DRAFT.md §4). Pure functions.

paired_counts(x, y) -> (a both correct, b only x correct, c only y correct, d neither).
mcnemar_exact(b, c): two-sided exact binomial test on discordant pairs.
newcombe_paired(a, b, c, d): 95 % interval for p_x - p_y, Newcombe (1998) method 10 (Wilson score based).
"""
from __future__ import annotations

import hashlib
import math
import random
from typing import Sequence

Z95 = 1.959963984540054


def paired_counts(x: Sequence[int], y: Sequence[int]) -> tuple[int, int, int, int]:
    if len(x) != len(y):
        raise ValueError("paired vectors must have equal length")
    a = sum(1 for p, q in zip(x, y) if p and q)
    b = sum(1 for p, q in zip(x, y) if p and not q)
    c = sum(1 for p, q in zip(x, y) if q and not p)
    return a, b, c, len(x) - a - b - c


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def wilson(x: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = x / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, mid - half), min(1.0, mid + half)


def newcombe_paired(a: int, b: int, c: int, d: int, z: float = Z95) -> tuple[float, float]:
    n = a + b + c + d
    if n == 0:
        raise ValueError("no pairs")
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    if den == 0:
        phi = 0.0
    else:
        num = a * d - b * c
        num = max(num - n / 2, 0.0) if num > 0 else num
        phi = num / math.sqrt(den)
    diff = p1 - p2
    dl = math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    du = math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return max(-1.0, diff - dl), min(1.0, diff + du)


def ucr(per_question: Sequence[tuple[int, int]]) -> float:
    """Unsupported-claim rate: sum unsupported / sum numeric claims over questions (0 when no claim)."""
    claims = sum(c for c, _ in per_question)
    return sum(u for _, u in per_question) / claims if claims else 0.0


def ucr_diff_upper95(x: Sequence[tuple[int, int]], y: Sequence[tuple[int, int]], *, n_boot: int = 10_000,
                     seed: str = "d5-h3") -> float:
    """One-sided 95 % upper bound of UCR(x) - UCR(y), resampling questions (paired, same indices for x and y)."""
    if len(x) != len(y) or not x:
        raise ValueError("paired, non-empty question lists required")
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    n = len(x)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(ucr([x[i] for i in idx]) - ucr([y[i] for i in idx]))
    diffs.sort()
    return diffs[int(math.ceil(0.95 * n_boot)) - 1]
