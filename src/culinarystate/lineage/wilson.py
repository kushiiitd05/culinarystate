"""Wilson score interval for a binomial proportion."""
from __future__ import annotations

from math import sqrt

Z95 = 1.959964


def wilson_interval(successes: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Return (lower, upper) Wilson bounds; (0.0, 1.0) when n == 0."""
    if n < 0 or successes < 0 or successes > n:
        raise ValueError(f"need 0 <= successes <= n, got {successes}/{n}")
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def wilson_lower(successes: int, n: int, z: float = Z95) -> float:
    """Lower Wilson bound."""
    return wilson_interval(successes, n, z)[0]
