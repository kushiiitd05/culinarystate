"""Symbolic quantities for state tracking (plan AN2, SSOT §233.6).

A SymQty is a sum of terms coef × base, where base is one parsed amount (mass g / volume mL /
count / qualitative). Terms in different dimensions are never added numerically: "50 g butter,
reserve 1 tbsp" leaves "50 g − 1 tbsp" symbolic with numeric value UNKNOWN. Fractions of an
interval propagate proportionally (half of 100–120 g = 50–60 g). Immutable throughout.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

DIMS = ("g", "mL", "count", "qual")


@dataclass(frozen=True)
class Base:
    dim: str                  # g | mL | count | qual
    low: float | None         # None for qualitative/unknown
    high: float | None
    label: str                # raw text, e.g. "1 tbsp", "a pinch"

    @staticmethod
    def amount(dim: str, value: float, label: str) -> "Base":
        return Base(dim, value, value, label)

    @staticmethod
    def interval(dim: str, low: float, high: float, label: str) -> "Base":
        return Base(dim, min(low, high), max(low, high), label)

    @staticmethod
    def qualitative(label: str) -> "Base":
        return Base("qual", None, None, label)

    @staticmethod
    def from_channels(mass: dict, volume: dict, count: dict, label: str) -> "Base":
        """Pick the best-supported channel from normalize(); never converts between dimensions."""
        for q, dim in ((mass, "g"), (volume, "mL"), (count, "count")):
            if q.get("status") == "MEASURED":
                return Base.amount(dim, q["value"], label)
            if q.get("status") == "RANGE":
                return Base.interval(dim, q["low"], q["high"], label)
        return Base.qualitative(label)


@dataclass(frozen=True)
class SymQty:
    terms: tuple[tuple[Fraction, Base], ...]

    @staticmethod
    def of(base: Base) -> "SymQty":
        return SymQty(((Fraction(1), base),))

    @staticmethod
    def zero() -> "SymQty":
        return SymQty(())

    def scale(self, k: Fraction | float) -> "SymQty":
        k = Fraction(k).limit_denominator(1000)
        return SymQty(tuple((c * k, b) for c, b in self.terms))

    def plus(self, other: "SymQty") -> "SymQty":
        return SymQty(_combine(self.terms + other.terms))

    def minus(self, other: "SymQty") -> "SymQty":
        return self.plus(other.scale(-1))

    @property
    def dims(self) -> set[str]:
        return {b.dim for c, b in self.terms if c != 0}

    def evaluate(self) -> dict:
        """QVALUE-like result. Numeric only if every term is numeric and in one dimension."""
        live = [(c, b) for c, b in self.terms if c != 0]
        if not live:
            return {"status": "MEASURED", "value": 0.0, "unit": None, "raw": "0"}
        dims = {b.dim for _, b in live}
        if len(dims) != 1 or "qual" in dims or any(b.low is None for _, b in live):
            return {"status": "UNKNOWN", "raw": self.render()}
        dim = dims.pop()
        lo = sum(float(c) * (b.low if c > 0 else b.high) for c, b in live)
        hi = sum(float(c) * (b.high if c > 0 else b.low) for c, b in live)
        if abs(hi - lo) < 1e-9:
            return {"status": "MEASURED", "value": round(lo, 6), "unit": dim, "raw": self.render()}
        return {"status": "RANGE", "low": round(lo, 6), "high": round(hi, 6), "unit": dim, "raw": self.render()}

    def render(self) -> str:
        parts = []
        for c, b in self.terms:
            if c == 0:
                continue
            coef = "" if abs(c) == 1 else f"{abs(c)}×"
            sign = "−" if c < 0 else "+"
            parts.append(f"{sign} {coef}{b.label}")
        s = " ".join(parts) or "0"
        return s[2:] if s.startswith("+ ") else s


def _combine(terms: tuple[tuple[Fraction, Base], ...]) -> tuple[tuple[Fraction, Base], ...]:
    acc: dict[Base, Fraction] = {}
    order: list[Base] = []
    for c, b in terms:
        if b not in acc:
            order.append(b)
            acc[b] = Fraction(0)
        acc[b] += c
    return tuple((acc[b], b) for b in order if acc[b] != 0)
