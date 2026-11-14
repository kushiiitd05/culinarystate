"""Exact McNemar power and minimum detectable effect for H1 (S178; REV-B Q26, consensus T9-C12-R1; SSOT v16 287.4). DRAFT.

Reuses ``paired_stats.mcnemar_exact`` (decision rule) and ``paired_stats.newcombe_paired`` (descriptive interval).
Nothing here chooses a pre-registered threshold: alpha, target power and the discordance grid are explicit arguments
of the planning functions (the module-level ``PLANNING_*`` tuples are the grid REV-B used and are labelled planning
values, not decisions).

Model. A paired question has four outcomes (both right, only x right, only y right, both wrong). Exact power depends
only on the two discordant cell probabilities ``pi_b`` (only x right) and ``pi_c`` (only y right):
``m ~ Binomial(n, pi_b + pi_c)`` discordant pairs, then ``b | m ~ Binomial(m, pi_b / (pi_b + pi_c))``, and the test
rejects when ``mcnemar_exact(b, m - b) <= alpha``. The accuracy gap is ``delta = pi_b - pi_c`` and the discordance
rate ``d = pi_b + pi_c``; the gap cannot exceed d, and a large gap with a small d means few discordant pairs.

H1 needs B4 > B1 and B4 > B2, both significant (intersection-union). The two tests share B4's answers, so their
joint power is only bounded: Frechet ``max(0, P1 + P2 - 1) <= P(both) <= min(P1, P2)``.

S178 FIX-EVAL (SCI-B E7). At fixed n and d, power is non-decreasing in the gap delta >= 0: m does not depend on delta, and
for each m the two-sided rejection region {b >= k} or {b <= m - k} (k >= (m + 1) / 2) has derivative in the success share p
m [P(Bin(m - 1, p) = k - 1) - P(Bin(m - 1, p) = m - k)] = m C(m-1, k-1) p^(m-k) (1-p)^(m-k) [p^(2k-m-1) - (1-p)^(2k-m-1)]
>= 0 for p >= 1/2 (S179 SCI #8: the bracket was written [(p/(1-p))^(2k-m-1) - 1], which drops a (1-p)^(2k-m-1) factor; the
sign and every number are unchanged; identity checked symbolically for m = 3..11; ``power_monotone_in_delta`` checks the
monotonicity on the grid and a unit test runs it). ``power`` counts rejections on either side, including the wrong
direction {b <= m - k} (y better). On the planning grid (n 30 / 60, d 0.2-0.5) that share is below 1e-6 at each MDE and at
most 0.013 at the smallest gap (delta 0.005); a one-sided H1 claim needs the b >= k side only. The discrete-test sawtooth is
in the number of discordant pairs m (``conditional_power``: e.g. 0.449 at m = 6, 0.393 at m = 7 for delta 0.3, d 0.4), not
in delta; averaged over m ~ Bin(n, d) the planning-grid power was non-decreasing in n for n = 5..80 (checked S178). The MDE
is therefore the first grid point reaching the target power (grid step ``MDE_STEP`` = 0.005); the
S178 EVAL text called it a "conservative reading of a sawtooth in delta", which was wrong (the values do not change).
``planning_table`` states the discordance range each n's MDE range covers (``headline_by_n``) and a common range.
"""
from __future__ import annotations

import math
from typing import Sequence

from culinarystate.evaluation.paired_stats import mcnemar_exact, newcombe_paired

VERSION = "mcnemar_power@0.1"
PLANNING_ALPHA = 0.05
PLANNING_POWER = 0.8
PLANNING_DISCORDANCE = (0.2, 0.3, 0.4, 0.5)          # planning grid only; the realised discordance is unknown until run
PLANNING_N = (30, 60)
MDE_STEP = 0.005


def _binom_pmf(n: int, p: float) -> list[float]:
    if p <= 0.0:
        return [1.0] + [0.0] * n
    if p >= 1.0:
        return [0.0] * n + [1.0]
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def min_discordant_for_significance(alpha: float = PLANNING_ALPHA) -> int:
    """Smallest number of discordant pairs at which the exact two-sided test can reach p <= alpha (all on one side)."""
    m = 1
    while mcnemar_exact(0, m) > alpha:
        m += 1
    return m


def min_majority_for_significance(m: int, alpha: float = PLANNING_ALPHA) -> int | None:
    """Smallest majority count b (>= m - b) among ``m`` discordant pairs with exact p <= alpha; None if impossible."""
    for b in range((m + 1) // 2, m + 1):
        if mcnemar_exact(b, m - b) <= alpha:
            return b
    return None


def rejection_table(n: int, alpha: float = PLANNING_ALPHA) -> dict[int, int | None]:
    """m discordant pairs -> minimum majority count that rejects (None = cannot reject at that m), m = 0..n."""
    return {m: min_majority_for_significance(m, alpha) for m in range(n + 1)}


def conditional_power(m: int, delta: float, discordance: float, alpha: float = PLANNING_ALPHA) -> float:
    """P(reject | m discordant pairs): the discrete, saw-toothed part of the power."""
    k = min_majority_for_significance(m, alpha) if m else None
    if k is None:
        return 0.0
    pb = _binom_pmf(m, (discordance + delta) / (2 * discordance))
    return min(1.0, sum(pb[k:]) + sum(pb[:m - k + 1]))


def power(n: int, delta: float, discordance: float, alpha: float = PLANNING_ALPHA) -> float:
    """Exact probability that the two-sided exact McNemar test rejects, for gap ``delta`` and discordance rate d."""
    if n < 1:
        raise ValueError("n must be positive")
    if not 0 <= discordance <= 1:
        raise ValueError("discordance must be in [0, 1]")
    if abs(delta) > discordance + 1e-12:
        raise ValueError("|delta| cannot exceed the discordance rate (pi_b - pi_c <= pi_b + pi_c)")
    if discordance == 0:
        return 0.0
    pi_b = (discordance + delta) / 2
    share = pi_b / discordance
    need = rejection_table(n, alpha)
    total = 0.0
    for m, pm in enumerate(_binom_pmf(n, discordance)):
        k = need[m]
        if k is None or pm == 0.0:
            continue
        pb = _binom_pmf(m, share)
        total += pm * (sum(pb[k:]) + sum(pb[:m - k + 1]))          # majority on either side rejects (two-sided)
    return min(1.0, total)


def _grid(discordance: float, step: float) -> list[float]:
    return [round(i * step, 10) for i in range(1, int(discordance / step + 1e-9) + 1)]


def power_monotone_in_delta(n: int, discordance: float, *, alpha: float = PLANNING_ALPHA, step: float = MDE_STEP,
                            tol: float = 1e-12) -> bool:
    """True when power is non-decreasing over the delta grid (0, step, ..., d) at this n and d."""
    ps = [power(n, g, discordance, alpha) for g in [0.0] + _grid(discordance, step)]
    return all(b >= a - tol for a, b in zip(ps, ps[1:]))


def mde_first_crossing(n: int, discordance: float, *, target_power: float = PLANNING_POWER, alpha: float = PLANNING_ALPHA,
                       step: float = MDE_STEP) -> float | None:
    """First grid gap whose power reaches ``target_power`` (None if none does)."""
    for g in _grid(discordance, step):
        if power(n, g, discordance, alpha) >= target_power:
            return g
    return None


def mde(n: int, discordance: float, *, target_power: float = PLANNING_POWER, alpha: float = PLANNING_ALPHA,
        step: float = MDE_STEP) -> float | None:
    """Smallest gap delta (grid ``step``) from which power stays >= ``target_power`` for every larger gap up to d.

    Power is monotone (non-decreasing) in delta at fixed n and d (module docstring), so this equals the first crossing
    (``mde_first_crossing``); the scan from the top is kept as a guard. None when even delta = d does not reach the target.
    """
    grid = _grid(discordance, step)
    if not grid:
        return None
    ok = [power(n, g, discordance, alpha) >= target_power for g in grid]
    if not ok[-1]:
        return None
    i = len(grid) - 1
    while i > 0 and ok[i - 1]:
        i -= 1
    return grid[i]


def iu_power_bounds(p1: float, p2: float) -> tuple[float, float]:
    """Frechet bounds on P(both tests reject) when the two tests share one arm (B4) and are therefore dependent."""
    return max(0.0, p1 + p2 - 1.0), min(p1, p2)


def design_interval(n: int, p_baseline: float, delta: float, discordance: float) -> dict:
    """Newcombe 95 % interval at the expected counts of a design point (rounded to whole questions)."""
    pi_b, pi_c = (discordance + delta) / 2, (discordance - delta) / 2
    b, c = round(n * pi_b), round(n * pi_c)
    a = round(n * p_baseline) - c
    d_cell = n - a - b - c
    if a < 0 or d_cell < 0:
        raise ValueError("design point infeasible for this baseline accuracy")
    lo, hi = newcombe_paired(a, b, c, d_cell)
    return {"counts_abcd": [a, b, c, d_cell], "diff": round((b - c) / n, 4), "newcombe95": [round(lo, 4), round(hi, 4)],
            "halfwidth": round((hi - lo) / 2, 4)}


def describe_realised(n: int, b: int, c: int, alpha: float = PLANNING_ALPHA) -> dict:
    """What the realised discordant counts can and cannot show (SSOT 287.4 rule 2)."""
    m = b + c
    floor = min_discordant_for_significance(alpha)
    need = min_majority_for_significance(m, alpha) if m else None
    return {"n": n, "discordant": m, "min_discordant_for_alpha": floor, "p_exact": mcnemar_exact(b, c),
            "can_be_significant": m >= floor,
            "min_majority_needed": need, "majority": max(b, c),
            "statement": (f"cannot be significant at this n: {m} discordant pairs < {floor}" if m < floor else
                          "significant" if mcnemar_exact(b, c) <= alpha else "not significant at this n")}


def planning_table(ns: Sequence[int] = PLANNING_N, discordances: Sequence[float] = PLANNING_DISCORDANCE, *,
                   target_power: float = PLANNING_POWER, alpha: float = PLANNING_ALPHA) -> dict:
    """MDE and power grid for the report: per n and discordance rate, the MDE (grid step ``MDE_STEP``), the power at a
    few gaps and the intersection-union Frechet bounds when both tests sit at that MDE; per n the discordance range its
    MDE range covers (``headline_by_n``), and the MDE ranges over the discordance range common to every n."""
    out = {"version": VERSION, "alpha": alpha, "target_power": target_power, "grid_step": MDE_STEP,
           "min_discordant_for_alpha": min_discordant_for_significance(alpha), "rows": []}
    for n in ns:
        for d in discordances:
            m = mde(n, d, target_power=target_power, alpha=alpha)
            row = {"n": n, "discordance": d, "mde": m,
                   "power_at_gap": {str(g): round(power(n, g, d, alpha), 4) for g in (0.1, 0.2, 0.3, 0.4) if g <= d + 1e-12}}
            if m is not None:
                p = power(n, m, d, alpha)
                row["power_at_mde"] = round(p, 4)
                row["iu_power_bounds_at_mde"] = [round(x, 4) for x in iu_power_bounds(p, p)]
            out["rows"].append(row)
    head: dict[str, dict] = {}
    for n in ns:
        rs = [r for r in out["rows"] if r["n"] == n]
        have = [r for r in rs if r["mde"] is not None]
        head[str(n)] = {"discordance_range_with_mde": [min(r["discordance"] for r in have), max(r["discordance"] for r in have)] if have else None,
                        "mde_range": [min(r["mde"] for r in have), max(r["mde"] for r in have)] if have else None,
                        "discordances_without_mde": [r["discordance"] for r in rs if r["mde"] is None],
                        "power_monotone_in_delta_all_d": all(power_monotone_in_delta(n, r["discordance"], alpha=alpha) for r in rs)}
    out["headline_by_n"] = head
    common = sorted(set.intersection(*[{r["discordance"] for r in out["rows"] if r["n"] == n and r["mde"] is not None}
                                       for n in ns])) if ns else []
    out["common_discordance_range"] = {
        "discordance_range": [common[0], common[-1]] if common else None,
        "mde_range_by_n": {str(n): [min(r["mde"] for r in out["rows"] if r["n"] == n and r["discordance"] in common),
                                    max(r["mde"] for r in out["rows"] if r["n"] == n and r["discordance"] in common)]
                           for n in ns} if common else None,
        "reading": "compare n only over the same discordance range; the realised discordance is unknown until the run"}
    return out
