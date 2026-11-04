"""Step 26a unit / dimension checker (S159, DRAFT_PENDING_26_0_H4).

Pure and deterministic. It checks that a unit string has the dimension a model slot asks for; it never
converts a stored raw value in place and never harmonises rate constants across orders (SSOT 210.30).

Conventions shared with KIN v1.1 (``culinarystate.lineage.kinetic_contract``):
- time tokens s / min / h / d / week have the exact factors of ``SECONDS_PER_UNIT``; month and year are
  calendar durations with dimension TIME but **no** factor, so no seconds value is produced from them;
- a missing, empty or ``UNKNOWN`` unit gives verdict UNKNOWN (never a default unit);
- degC is an affine temperature scale: allowed as a bare token, never in a product, a power or an Arrhenius
  term (G24.3: Kelvin in Arrhenius).

Concentration is an **opaque** base dimension CONCENTRATION. Mass-per-mass or molar units are not reduced to
it, because a zero-order k in "mg/100g/min" would otherwise look like a first-order k. The caller declares the
series' concentration tokens through ``opaque`` (for example ``{"u": "CONCENTRATION"}`` or a bracketed token
``{"[mg/100g]": "CONCENTRATION"}``); opaque tokens have no SI factor.

Grammar (left-associative): ``expr := term (('*' | '/') term)*``, ``term := factor ('^' exponent)?``,
``factor := name | '1' | '(' expr ')'``, exponent an integer or a fraction such as ``-1/2``.
Dimension expressions use the base names below joined by ``*`` with ``^`` exponents, plus the alias ENERGY.

Physical constants: the gas constant is the product of the two exact SI defining constants N_A and k_B
(2019 SI). These are definitions, not measured or literature parameters of any food system.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from fractions import Fraction

from culinarystate.lineage.kinetic_contract import SECONDS_PER_UNIT

STATUS = "DRAFT_PENDING_26_0_H4"
CONSISTENT, INCONSISTENT, UNKNOWN = "CONSISTENT", "INCONSISTENT", "UNKNOWN"
BASE_DIMENSIONS = ("AMOUNT", "CONCENTRATION", "LENGTH", "MASS", "TEMPERATURE", "TIME")

AVOGADRO_PER_MOL = 6.02214076e23          # exact, 2019 SI defining constant
BOLTZMANN_J_PER_K = 1.380649e-23          # exact, 2019 SI defining constant
GAS_CONSTANT_J_PER_MOL_K = AVOGADRO_PER_MOL * BOLTZMANN_J_PER_K
GAS_CONSTANT_UNIT = "J/(mol*K)"


class UnitError(ValueError):
    """Unparseable unit or dimension expression."""


@dataclass(frozen=True)
class Dimension:
    """Exponents of base dimensions, sorted by name, zero exponents dropped."""

    exponents: tuple[tuple[str, Fraction], ...] = ()

    @staticmethod
    def of(mapping: Mapping[str, Fraction | int]) -> Dimension:
        return Dimension(tuple(sorted((k, Fraction(v)) for k, v in mapping.items() if Fraction(v) != 0)))

    def as_dict(self) -> dict[str, Fraction]:
        return dict(self.exponents)

    def __mul__(self, other: Dimension) -> Dimension:
        out = self.as_dict()
        for k, v in other.exponents:
            out[k] = out.get(k, Fraction(0)) + v
        return Dimension.of(out)

    def __truediv__(self, other: Dimension) -> Dimension:
        return self * other ** -1

    def __pow__(self, power: Fraction | int) -> Dimension:
        p = Fraction(power)
        return Dimension.of({k: v * p for k, v in self.exponents})

    def is_dimensionless(self) -> bool:
        return not self.exponents

    def __str__(self) -> str:
        if not self.exponents:
            return "1"
        return "*".join(k if v == 1 else f"{k}^{v}" for k, v in self.exponents)


ONE = Dimension()
_ALIASES: Mapping[str, Dimension] = {
    "ENERGY": Dimension.of({"MASS": 1, "LENGTH": 2, "TIME": -2}),
}
_DIM_TERM = re.compile(r"^([A-Z]+)(?:\^(-?\d+(?:/\d+)?))?$")


def dimension(expr: str) -> Dimension:
    """Parse a dimension expression such as ``CONCENTRATION^-1*TIME^-1`` or ``1``."""
    if not isinstance(expr, str) or not expr.strip():
        raise UnitError("empty dimension expression")
    if expr.strip() == "1":
        return ONE
    out = ONE
    for part in expr.split("*"):
        m = _DIM_TERM.match(part.strip())
        if not m:
            raise UnitError(f"bad dimension term {part!r} in {expr!r}")
        name, exp = m.group(1), Fraction(m.group(2) or 1)
        if name in _ALIASES:
            base = _ALIASES[name]
        elif name in BASE_DIMENSIONS:
            base = Dimension.of({name: 1})
        else:
            raise UnitError(f"unknown base dimension {name!r}")
        out = out * base ** exp
    return out


# ----------------------------------------------------------------------------- unit tokens
@dataclass(frozen=True)
class _Token:
    dimension: Dimension
    factor: Fraction | None      # to SI (s, K, mol, kg, m, J); None = no exact factor
    affine: bool = False


def _t(dim: str, factor: Fraction | int | None, affine: bool = False) -> _Token:
    return _Token(dimension(dim), None if factor is None else Fraction(factor), affine)


_TOKENS: dict[str, _Token] = {
    **{u: _t("TIME", f) for u, f in SECONDS_PER_UNIT.items()},
    "month": _t("TIME", None), "year": _t("TIME", None),
    "K": _t("TEMPERATURE", 1), "degC": _t("TEMPERATURE", None, affine=True),
    "mol": _t("AMOUNT", 1), "mmol": _t("AMOUNT", Fraction(1, 1000)), "umol": _t("AMOUNT", Fraction(1, 10**6)),
    "kg": _t("MASS", 1), "g": _t("MASS", Fraction(1, 1000)), "mg": _t("MASS", Fraction(1, 10**6)),
    "ug": _t("MASS", Fraction(1, 10**9)),
    "m": _t("LENGTH", 1), "L": _t("LENGTH^3", Fraction(1, 1000)), "mL": _t("LENGTH^3", Fraction(1, 10**6)),
    "J": _t("ENERGY", 1), "kJ": _t("ENERGY", 1000),
}
_LEX = re.compile(r"\s*(?:(\[[^\]]+\])|([A-Za-z_][A-Za-z0-9_]*)|(\d+(?:/\d+)?)|(-\d+(?:/\d+)?)|([*/^()]))")


@dataclass(frozen=True)
class ParsedUnit:
    raw: str
    dimension: Dimension
    factor_to_si: Fraction | None
    affine: bool


def _lex(text: str) -> list[str]:
    pos, out = 0, []
    while pos < len(text):
        m = _LEX.match(text, pos)
        if not m or m.end() == pos:
            if text[pos:].strip() == "":
                break
            raise UnitError(f"cannot read unit {text!r} at {pos}")
        out.append(next(g for g in m.groups() if g is not None))
        pos = m.end()
    return out


class _Parser:
    def __init__(self, text: str, opaque: Mapping[str, str]) -> None:
        self.toks, self.i, self.text = _lex(text), 0, text
        self.opaque = {k: dimension(v) for k, v in opaque.items()}
        self.affine_seen = 0

    def peek(self) -> str | None:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self) -> str:
        tok = self.peek()
        if tok is None:
            raise UnitError(f"unexpected end of unit {self.text!r}")
        self.i += 1
        return tok

    def expr(self) -> tuple[Dimension, Fraction | None]:
        d, f = self.term()
        while self.peek() in ("*", "/"):
            op = self.take()
            d2, f2 = self.term()
            if op == "*":
                d, f = d * d2, (None if f is None or f2 is None else f * f2)
            else:
                d, f = d / d2, (None if f is None or f2 is None else f / f2)
        return d, f

    def term(self) -> tuple[Dimension, Fraction | None]:
        d, f = self.factor()
        if self.peek() == "^":
            self.take()
            e = Fraction(self.take())
            d = d ** e
            f = None if f is None or e.denominator != 1 else f ** int(e)
        return d, f

    def factor(self) -> tuple[Dimension, Fraction | None]:
        tok = self.take()
        if tok == "(":
            out = self.expr()
            if self.take() != ")":
                raise UnitError(f"unbalanced parenthesis in {self.text!r}")
            return out
        if tok == "1":
            return ONE, Fraction(1)
        if tok in self.opaque:
            return self.opaque[tok], None
        if tok in _TOKENS:
            t = _TOKENS[tok]
            self.affine_seen += int(t.affine)
            return t.dimension, t.factor
        raise UnitError(f"UNIT_TOKEN_UNKNOWN {tok!r} in {self.text!r}")


def parse_unit(unit: str, *, opaque: Mapping[str, str] | None = None) -> ParsedUnit:
    """Parse a unit string; raises ``UnitError`` for an unknown token or a misplaced affine degC."""
    if not isinstance(unit, str) or not unit.strip():
        raise UnitError("empty unit")
    p = _Parser(unit, opaque or {})
    d, f = p.expr()
    if p.peek() is not None:
        raise UnitError(f"trailing text in unit {unit!r}")
    affine = p.affine_seen > 0
    if affine and (len(p.toks) != 1):
        raise UnitError(f"AFFINE_IN_COMPOUND degC cannot be multiplied, divided or raised in {unit!r}")
    return ParsedUnit(unit, d, None if affine else f, affine)


@dataclass(frozen=True)
class UnitCheck:
    verdict: str
    detail: str = ""


def _expected(expected: str | Dimension) -> Dimension:
    return expected if isinstance(expected, Dimension) else dimension(expected)


def _parse_or_check(unit: str | None, opaque: Mapping[str, str] | None) -> ParsedUnit | UnitCheck:
    if unit is None or not str(unit).strip() or unit == "UNKNOWN":
        return UnitCheck(UNKNOWN, "UNIT_MISSING")
    try:
        return parse_unit(unit, opaque=opaque)
    except UnitError as exc:
        msg = str(exc)
        if "AFFINE_IN_COMPOUND" in msg:
            return UnitCheck(INCONSISTENT, msg)
        return UnitCheck(UNKNOWN, msg if "UNIT_TOKEN_UNKNOWN" in msg else f"UNIT_TOKEN_UNKNOWN {msg}")


def check_unit(unit: str | None, expected: str | Dimension, *, opaque: Mapping[str, str] | None = None) -> UnitCheck:
    """CONSISTENT / INCONSISTENT / UNKNOWN for ``unit`` against an expected dimension."""
    exp = _expected(expected)
    parsed = _parse_or_check(unit, opaque)
    if isinstance(parsed, UnitCheck):
        return parsed
    if parsed.dimension != exp:
        return UnitCheck(INCONSISTENT, f"{unit!r} has dimension {parsed.dimension}, expected {exp}")
    return UnitCheck(CONSISTENT)


def rate_constant_dimension(order: Fraction | int | float) -> Dimension:
    """SSOT 210.30: [k] = CONCENTRATION^(1-n) * TIME^-1 for order n."""
    n = Fraction(order).limit_denominator(1000) if isinstance(order, float) else Fraction(order)
    return dimension("CONCENTRATION") ** (1 - n) * dimension("TIME^-1")


_CONCENTRATION_LIKE = (Dimension.of({"MASS": 1}), Dimension.of({"AMOUNT": 1}), Dimension.of({"LENGTH": 3}))


def undeclared_concentration_tokens(unit: str | None, *, opaque: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Mass, amount or volume tokens not declared opaque. In a rate-constant unit they mean an undeclared
    concentration basis: "mg/g/min" reduces to TIME^-1 and would pass as first order (S159 review R1)."""
    if not isinstance(unit, str) or not unit.strip():
        return ()
    try:
        toks = _lex(unit)
    except UnitError:
        return ()
    op = opaque or {}
    return tuple(sorted({t for t in toks if t not in op and t in _TOKENS
                         and _TOKENS[t].dimension in _CONCENTRATION_LIKE}))


def check_rate_constant_unit(unit: str | None, order: Fraction | int | float, *,
                             opaque: Mapping[str, str] | None = None) -> UnitCheck:
    """UNKNOWN when the unit carries an undeclared concentration basis (declare it through ``opaque``)."""
    undeclared = undeclared_concentration_tokens(unit, opaque=opaque)
    if undeclared:
        return UnitCheck(UNKNOWN, f"CONCENTRATION_TOKENS_UNDECLARED {list(undeclared)} in {unit!r}: declare the "
                                  "series concentration unit through opaque (SSOT 210.30)")
    return check_unit(unit, rate_constant_dimension(order), opaque=opaque)


def check_arrhenius_units(ea_unit: str | None, temperature_unit: str | None, *,
                          opaque: Mapping[str, str] | None = None) -> UnitCheck:
    """Ea / (R T) must be dimensionless with T on the absolute (Kelvin) scale."""
    ea = check_unit(ea_unit, "ENERGY*AMOUNT^-1", opaque=opaque)
    if ea.verdict != CONSISTENT:
        return ea
    t = _parse_or_check(temperature_unit, opaque)
    if isinstance(t, UnitCheck):
        return t
    if t.affine:
        return UnitCheck(INCONSISTENT, "ARRHENIUS_NEEDS_KELVIN: affine degC is not an absolute temperature")
    if t.dimension != dimension("TEMPERATURE"):
        return UnitCheck(INCONSISTENT, f"temperature unit {temperature_unit!r} has dimension {t.dimension}")
    return UnitCheck(CONSISTENT)


def check_dimensionless(factors: Iterable[tuple[str, int | Fraction]], *,
                        opaque: Mapping[str, str] | None = None) -> UnitCheck:
    """The product of unit**power over ``factors`` must be dimensionless (for example k * tau)."""
    out = ONE
    for unit, power in factors:
        parsed = _parse_or_check(unit, opaque)
        if isinstance(parsed, UnitCheck):
            return parsed
        if parsed.affine:
            return UnitCheck(INCONSISTENT, "AFFINE_IN_COMPOUND degC in a dimensionless group")
        out = out * parsed.dimension ** power
    return UnitCheck(CONSISTENT) if out.is_dimensionless() else UnitCheck(INCONSISTENT, f"group has dimension {out}")


def to_si(value: float, unit: str, *, opaque: Mapping[str, str] | None = None) -> float | None:
    """Value in SI base units, or None when no exact factor exists (month, year, degC, opaque tokens)."""
    try:
        parsed = parse_unit(unit, opaque=opaque)
    except UnitError:
        return None
    if parsed.factor_to_si is None:
        return None
    return float(value) * float(parsed.factor_to_si)
