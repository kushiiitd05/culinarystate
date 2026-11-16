"""Lot composition state (S175): what a mixed lot is made of, as exact bounds — never a guessed point.

A lot is a set of members (ingredient, SR food, grams interval, FDA pH range). Every lot-level quantity here is a
ratio of two member-mass-weighted sums, X = sum m_j n_j / sum m_j d_j (mass fraction: d = 1; solute per water:
d = water fraction). X is linear-fractional in the masses, so over the mass box its extremes sit at a vertex where
m_j is at its upper bound iff n_j/d_j beats the optimum; sorting by n_j/d_j and scanning thresholds gives the exact
bounds. A member with unknown grams has m in [0, inf): its vertex at infinity pulls the bound to its own ratio.

Rules: a component is UNKNOWN when any member's food or that component is unknown (no imputation, UNKNOWN is valid);
pH is reported as member classes and lot flags (21 CFR 113/114 boundary 4.6), never as a mixture pH number; every
state is MODEL_DERIVED, and PROVISIONAL while any member's ING->SR link is unverified (SSOT 235.3, vocab/fdc.py).

S179: the composition is "as listed" (no evaporation, leaching or fat loss), so every state carries
AS_LISTED_NO_PROCESS_EFFECTS and NON_CITABLE (A11). The float scan picks the optimal vertex; its ratio is then
recomputed exactly (fractions.Fraction) and rounded outward, so the true bound always lies inside the reported one
(A9). A lot whose only positive-mass members hold no water gets NO_WATER_IN_LOT for solute-per-water (A8/F5).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from types import MappingProxyType
from typing import Mapping, Sequence

from culinarystate.composition.food_ph import PHRange, acid_class
from culinarystate.composition.line_mass import LineMass
from culinarystate.composition.sr_legacy import NUTRIENTS, SRFood

Term = tuple[float, float | None, float, float]          # (mass low, mass high or None, numerator, denominator)
SOLUTES = MappingProxyType({"sodium_mg_per_g_water": ("sodium_mg", "water_g"),
                            "sugars_g_per_g_water": ("sugars_g", "water_g")})
BASE_LABELS = ("MODEL_DERIVED", "COMPOSITION_FROM_SR_LEGACY", "AS_LISTED_NO_PROCESS_EFFECTS", "NON_CITABLE")
PROVISIONAL = "PROVISIONAL_SR_LINK_UNVERIFIED"


def _ratio(n: float, d: float) -> float:
    if d > 0:
        return n / d
    return math.inf if n > 0 else (-math.inf if n < 0 else math.nan)


def _exact_up(num: Fraction, den: Fraction) -> float:
    """Smallest float >= num / den."""
    q = num / den
    f = float(q)
    return f if Fraction(f) >= q else math.nextafter(f, math.inf)


def _max_ratio(terms: Sequence[Term]) -> float | None:
    """sup of sum m n / sum m d over the box, rounded up to a float; math.inf when unbounded; None when the
    denominator is always 0."""
    live = [t for t in terms if not math.isnan(_ratio(t[2], t[3]))]
    best, arg = -math.inf, None
    for lo, hi, n, d in live:
        if hi is None and _ratio(n, d) > best:
            best, arg = _ratio(n, d), ("ray", n, d)
    order = sorted(live, key=lambda t: -_ratio(t[2], t[3]))
    for k in range(len(order) + 1):
        num = den = 0.0
        ms = []
        for i, (lo, hi, n, d) in enumerate(order):
            m = (hi if hi is not None else lo) if i < k else lo
            ms.append(m)
            num, den = num + m * n, den + m * d
        if den > 0 and num / den > best:
            best, arg = num / den, ("vertex", k, tuple(ms))
        elif den <= 0 and num > 0:
            return math.inf
    if best == -math.inf:
        return None
    if math.isinf(best):
        return best
    if arg[0] == "ray":
        return _exact_up(Fraction(arg[1]), Fraction(arg[2]))
    ms = arg[2]
    return _exact_up(sum((Fraction(m) * Fraction(t[2]) for m, t in zip(ms, order)), Fraction(0)),
                     sum((Fraction(m) * Fraction(t[3]) for m, t in zip(ms, order)), Fraction(0)))


def ratio_bounds(terms: Sequence[Term]) -> tuple[float | None, float | None]:
    """Exact (min, max) of sum m_j n_j / sum m_j d_j for m_j in [lo_j, hi_j] (hi None = unbounded); n, d >= 0."""
    hi = _max_ratio(terms)
    neg = _max_ratio([(lo, h, -n, d) for lo, h, n, d in terms])
    lo = None if neg is None else -neg + 0.0           # + 0.0 turns -0.0 into 0.0 (F5)
    return (None if lo is None or math.isinf(lo) else lo), (None if hi is None or math.isinf(hi) else hi)


@dataclass(frozen=True)
class Bound:
    status: str                    # INTERVAL | UNKNOWN
    low: float | None
    high: float | None             # None with status INTERVAL = unbounded above
    unit: str
    reason: str | None = None


@dataclass(frozen=True)
class Member:
    name: str
    food: SRFood | None
    mass: LineMass
    ph: PHRange
    link_verified: bool = False


@dataclass(frozen=True)
class LotState:
    n_members: int
    total_mass_g: Bound
    composition: Mapping[str, Bound]
    solute: Mapping[str, Bound]
    member_ph: tuple[tuple[str, str], ...]
    ph_flags: tuple[str, ...]
    labels: tuple[str, ...]
    water_activity: str = field(default="NOT_COMPUTED_NEEDS_SOURCED_MODEL")


def _mass(m: LineMass) -> tuple[float, float | None]:
    return (m.low_g, m.high_g) if m.low_g is not None else (0.0, None)


def _unit(key: str) -> str:
    return "mg/g" if key.endswith("_mg") else "g/g"


def _bound(members: Sequence[Member], num: str, den: str | None, unit: str) -> Bound:
    if any(m.food is None for m in members):
        return Bound("UNKNOWN", None, None, unit, "MEMBER_FOOD_UNKNOWN")
    keys = (num,) if den is None else (num, den)
    if any(m.food.nutrient(k) is None for m in members for k in keys):
        return Bound("UNKNOWN", None, None, unit, "MEMBER_COMPOSITION_UNKNOWN")
    terms = [(*_mass(m.mass), m.food.nutrient(num) / 100.0, 1.0 if den is None else m.food.nutrient(den) / 100.0)
             for m in members]
    lo, hi = ratio_bounds(terms)
    if lo is None:
        can_mass = [t for t in terms if t[1] is None or t[1] > 0]
        no_water = den is not None and can_mass and all(t[3] == 0 for t in can_mass)
        return Bound("UNKNOWN", None, None, unit, "NO_WATER_IN_LOT" if no_water else "NO_POSITIVE_MASS")
    return Bound("INTERVAL", lo, hi, unit)


def _ph(members: Sequence[Member]) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...]]:
    classes = tuple((m.name, acid_class(m.ph)) for m in members)
    c = [k for _, k in classes]
    flags = set()
    if "ACID" in c:
        flags.add("CONTAINS_ACID_MEMBER")
    if c and all(k == "ACID" for k in c):
        flags.add("ALL_MEMBERS_ACID")
    if "UNKNOWN" in c:
        flags.add("ANY_MEMBER_PH_UNKNOWN")
    return classes, tuple(sorted(flags))


def lot_state(members: Sequence[Member]) -> LotState:
    if not members:
        raise ValueError("a lot needs at least one member")
    masses = [_mass(m.mass) for m in members]
    his = [h for _, h in masses]
    total = Bound("INTERVAL", sum(lo for lo, _ in masses), None if None in his else sum(his), "g")
    comp = {k: _bound(members, k, None, _unit(k)) for k in NUTRIENTS}
    sol = {k: _bound(members, n, d, "mg/g water" if n.endswith("_mg") else "g/g water") for k, (n, d) in
           SOLUTES.items()}
    member_ph, flags = _ph(members)
    provisional = any(m.food is not None and not m.link_verified for m in members)
    return LotState(len(members), total, MappingProxyType(comp), MappingProxyType(sol), member_ph, flags,
                    BASE_LABELS + ((PROVISIONAL,) if provisional else ()))
