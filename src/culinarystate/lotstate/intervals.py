"""Exact interval arithmetic for lot composition (Fractions; no floats inside).

``ratio_bounds`` solves  min / max of  (sum m_i a_i) / (sum m_i b_i)  over the box  m_i in [lo_i, hi_i]  exactly.
The objective is linear-fractional, so with a positive denominator the optimum sets every m_i to a bound and the
members that sit at ``hi`` are those with the largest (for max) or smallest (for min) ratio a_i / b_i. Testing the
n+1 threshold configurations of the sorted members is therefore exact (Dinkelbach structure); a brute-force vertex
check is in the unit tests.

Mass-weighted composition of a mixture is the special case b_i = 1.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

Member = tuple[Fraction, Fraction, Fraction, Fraction]  # (m_lo, m_hi, a, b)


def frac(x) -> Fraction:
    """Exact Fraction from an int, Fraction or a number read by its decimal text (never binary float noise)."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(repr(x))
    return Fraction(str(x))


def _eval(members: Sequence[Member], at_hi: Sequence[bool]) -> tuple[Fraction, Fraction]:
    n = d = Fraction(0)
    for (lo, hi, a, b), up in zip(members, at_hi):
        m = hi if up else lo
        n += m * a
        d += m * b
    return n, d


def _unbounded_above(members: Sequence[Member]) -> bool:
    """Denominator can reach 0 while the numerator stays positive: the ratio has no finite upper bound."""
    if any(b > 0 and lo > 0 for lo, hi, a, b in members):
        return False
    return any(b == 0 and a > 0 and hi > 0 for lo, hi, a, b in members)


def ratio_bounds(members: Sequence[Member]) -> tuple[Fraction | None, Fraction | None, str]:
    """(low, high, status). high is None when unbounded above; both None when the ratio is undefined
    (no member can carry a positive denominator). status: EXACT | UNBOUNDED_ABOVE | UNDEFINED."""
    live = [m for m in members if m[1] > 0 and (m[2] > 0 or m[3] > 0)]
    if not live:
        return None, None, "UNDEFINED"
    inf = None  # sentinel for ratio +infinity (b == 0, a > 0)

    def key(m: Member):
        lo, hi, a, b = m
        return (1, Fraction(0)) if b == 0 else (0, a / b)   # b == 0 members sort as +infinity

    asc = sorted(live, key=key)
    desc = list(reversed(asc))
    best_hi: Fraction | None = None
    best_lo: Fraction | None = None
    n = len(live)
    for order, want_max in ((desc, True), (asc, False)):
        for k in range(n + 1):
            up = [i < k for i in range(n)]
            num, den = _eval(order, up)
            if den <= 0:
                continue
            r = num / den
            if want_max:
                best_hi = r if best_hi is None or r > best_hi else best_hi
            else:
                best_lo = r if best_lo is None or r < best_lo else best_lo
    if best_hi is None or best_lo is None:
        return None, None, "UNDEFINED"
    if _unbounded_above(live):
        return best_lo, inf, "UNBOUNDED_ABOVE"
    return best_lo, best_hi, "EXACT"


def sum_interval(items: Sequence[tuple[Fraction, Fraction]]) -> tuple[Fraction, Fraction]:
    return sum((lo for lo, _ in items), Fraction(0)), sum((hi for _, hi in items), Fraction(0))


def float_lo(x: Fraction) -> float:
    """Largest float <= x (so a float bound never excludes the exact value)."""
    f = float(x)
    return f if Fraction(f) <= x else math.nextafter(f, -math.inf)


def float_hi(x: Fraction) -> float:
    f = float(x)
    return f if Fraction(f) >= x else math.nextafter(f, math.inf)
