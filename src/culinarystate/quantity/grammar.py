"""Ingredient-line quantity grammar v0 (deterministic).

Parses the leading quantity expression of a line, e.g.
  "2 x 400g cans chopped tomatoes", "1 ½ tbsp vegetable oil", "4 leeks (about 500g), sliced",
  "250ml/9fl oz double cream", "good handful pea shoots", "juice of 1 lemon", "5cm piece ginger".
Raw text and spans are preserved; nothing is converted here (see normalize.py).
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

from .units import ALIAS, PHRASE_QUALITATIVE, Unit, lookup

UNICODE_FRAC = {"½": "1/2", "¼": "1/4", "¾": "3/4", "⅓": "1/3", "⅔": "2/3", "⅛": "1/8", "⅜": "3/8",
                "⅝": "5/8", "⅞": "7/8", "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5", "⅙": "1/6", "⅚": "5/6"}
SIZE_WORDS = ("small", "medium", "large", "extra-large", "extra large", "big", "little", "thick", "thin", "jumbo",
              "heaped", "rounded", "level", "scant", "generous", "good", "large-ish", "mini", "baby", "whole",
              "thumb-sized", "thumb sized", "thumb-size", "walnut-sized", "fat", "chunky")
APPROX_WORDS = ("about", "approx.", "approx", "approximately", "around", "roughly", "c.", "up to")
PART_WORDS = ("zest and juice", "juice and zest", "finely grated zest", "grated zest", "zest", "juice")
WORD_NUMBERS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "half": 0.5,
                "a half": 0.5, "a couple of": 2, "couple of": 2, "a few": None}

NUM = r"\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?"
RANGE = rf"(?P<n1>{NUM})(?:\s*(?:-|–|to|or)\s*(?P<n2>{NUM}))?"
_ALIASES = sorted({a for a in ALIAS if len(a) > 1 or a in ("g", "l")}, key=len, reverse=True)
UNIT_ALT = "|".join(re.escape(a) for a in _ALIASES)
UNIT_RE = rf"(?:{UNIT_ALT})\.?(?![a-z])"
SIZE_RE = "|".join(re.escape(s) for s in sorted(SIZE_WORDS, key=len, reverse=True))


@dataclass(frozen=True)
class QuantityParse:
    raw: str
    kind: str                      # NUMBER RANGE FRACTION MIXED MULTIPLIER PACKAGE QUALITATIVE NONE
    value: float | None = None
    low: float | None = None
    high: float | None = None
    multiplier: float | None = None
    unit_key: str | None = None
    unit_raw: str | None = None
    size: str | None = None
    package_key: str | None = None
    package_size: tuple[float, str] | None = None      # (value, unit_key)
    alt: tuple[float, str] | None = None              # second unit expression "250ml/9fl oz"
    stated: tuple[float, str, str] | None = None      # parenthetical (value, unit_key, raw) e.g. (about 500g)
    part: str | None = None                           # juice / zest of
    qualifiers: tuple[str, ...] = ()
    span: tuple[int, int] | None = None
    rest: str = ""
    flags: tuple[str, ...] = field(default_factory=tuple)


def normalize_text(s: str) -> str:
    s = html.unescape(s)
    for k, v in UNICODE_FRAC.items():
        s = re.sub(rf"(\d)\s*{k}", rf"\1 {v}", s)
        s = s.replace(k, v)
    s = s.replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def to_number(tok: str) -> float:
    tok = tok.strip()
    if " " in tok:
        whole, frac = tok.split(None, 1)
        return float(whole) + to_number(frac)
    if "/" in tok:
        a, b = tok.split("/")
        return float(a) / float(b)
    return float(tok)


def _kind_of(n1: str, n2: str | None) -> str:
    if n2:
        return "RANGE"
    if " " in n1.strip():
        return "MIXED"
    if "/" in n1:
        return "FRACTION"
    return "NUMBER"


def _unit(tok: str | None) -> Unit | None:
    return lookup(tok.strip()) if tok else None


_STATED_RE = re.compile(rf"\(\s*(?:{'|'.join(re.escape(a) for a in APPROX_WORDS)})?\s*(?P<v>{NUM})\s*"
                        r"(?P<u>g|kg|ml|l|oz|lb)\b[^)]*\)", re.IGNORECASE)
_MULT_RE = re.compile(rf"^(?P<mult>\d+)\s*x\s*(?P<pv>{NUM})\s*(?P<pu>{UNIT_RE})(?:\s*/\s*{NUM}\s*{UNIT_RE})?"
                      rf"\s*(?P<pkg>{UNIT_RE})?", re.IGNORECASE)
_QTY_RE = re.compile(rf"^(?P<approx>(?:{'|'.join(re.escape(a) for a in APPROX_WORDS)})\s+)?{RANGE}"
                     rf"(?:\s*(?P<u1>{UNIT_RE}))?(?:\s*/\s*(?P<altv>{NUM})\s*(?P<altu>{UNIT_RE}))?"
                     rf"(?:\s+(?P<size>{SIZE_RE}))?(?:\s+(?P<u2>{UNIT_RE}))?", re.IGNORECASE)
_WORDQ_RE = re.compile(rf"^(?P<lead>a couple of|couple of|a few|a half|an|a|one|two|three|four|five|six|half)?\s*"
                       rf"(?P<size>{SIZE_RE})?\s*(?P<u>{UNIT_RE})(?:\s+of\b)?", re.IGNORECASE)
_WORDNUM_RE = re.compile(r"^(?P<lead>a couple of|couple of|a few|a little|a|an|one|two|three|four|five|six|"
                         r"seven|eight|ten|twelve|half an?|some|few)\s+(?!of\b)", re.IGNORECASE)
WORD_COUNT = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
              "eight": 8, "ten": 10, "twelve": 12, "a couple of": 2, "couple of": 2, "half a": 0.5, "half an": 0.5}
_PART_RE = re.compile(rf"^(?:the\s+)?(?P<part>{'|'.join(re.escape(p) for p in PART_WORDS)})\s+(?:of\s+)?"
                      rf"(?P<n>{NUM}|a|an|one|two|half)\b", re.IGNORECASE)


def _qualifiers(text: str) -> list[str]:
    t = text.lower()
    q = [p for p in PHRASE_QUALITATIVE if p in t]
    for w in ("heaped", "rounded", "level", "scant", "generous", "divided", "plus extra", "packed", "softened"):
        if re.search(rf"\b{w}\b", t):
            q.append(w)
    return q


def _clean_rest(rest: str) -> str:
    rest = _STATED_RE.sub(" ", rest)
    rest = re.sub(r"^\s*of\s+", "", rest.strip(), flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", rest).strip(" ,")


def parse_line(raw: str) -> QuantityParse:
    s = normalize_text(raw)
    quals = _qualifiers(s)
    stated = None
    sm = _STATED_RE.search(s)
    if sm:
        su = _unit(sm.group("u"))
        stated = (to_number(sm.group("v")), su.key, sm.group(0)) if su else None

    m = _MULT_RE.match(s)
    if m:
        pu, pkg = _unit(m.group("pu")), _unit(m.group("pkg"))
        return QuantityParse(raw, "MULTIPLIER", value=float(m.group("mult")), multiplier=float(m.group("mult")),
                             unit_key=pkg.key if pkg else None, unit_raw=m.group("pkg"),
                             package_key=pkg.key if pkg and pkg.unit_type == "PACKAGE" else None,
                             package_size=(to_number(m.group("pv")), pu.key) if pu else None, stated=stated,
                             qualifiers=tuple(quals), span=m.span(), rest=_clean_rest(s[m.end():]))

    m = _PART_RE.match(s)
    if m:
        n = m.group("n").lower()
        val = WORD_NUMBERS.get(n, None) if not re.match(r"\d", n) else to_number(n)
        return QuantityParse(raw, "NUMBER", value=val, part=m.group("part").lower(), stated=stated,
                             qualifiers=tuple(quals), span=m.span(), rest=_clean_rest(s[m.end():]))

    m = _QTY_RE.match(s)
    if m:
        n1, n2 = m.group("n1"), m.group("n2")
        u1, u2 = _unit(m.group("u1")), _unit(m.group("u2"))
        size = (m.group("size") or "").lower() or None
        if m.group("approx"):
            quals.append("about")
        lo = to_number(n1)
        hi = to_number(n2) if n2 else None
        kind = _kind_of(n1, n2)
        alt = None
        if m.group("altv") and _unit(m.group("altu")):
            alt = (to_number(m.group("altv")), _unit(m.group("altu")).key)
        flags = []
        unit, unit_raw, pkg_key, pkg_size = u1, m.group("u1"), None, None
        if u1 and u1.unit_type == "LENGTH":                       # "5cm piece ginger": length is a size
            size = f"{m.group('n1')}{m.group('u1')}"
            unit, unit_raw = u2, m.group("u2")
            lo, hi, kind = (1.0, None, "NUMBER") if not u2 or u2.unit_type != "LENGTH" else (lo, hi, kind)
        elif u1 and u2 and u2.unit_type == "PACKAGE" and u1.dimension in ("MASS", "VOLUME"):
            pkg_key, pkg_size = u2.key, (lo, u1.key)               # "200g can tuna" = one 200 g can
            unit, unit_raw, kind = u2, m.group("u2"), "PACKAGE"
            lo, hi = 1.0, None
        elif u1 and u2 and u2.unit_type == "COUNT_PORTION" and u1.dimension in ("MASS", "VOLUME") and not size:
            pkg_size = (lo, u1.key)                                # "375g sheet pastry" = one 375 g sheet
            unit, unit_raw, kind = u2, m.group("u2"), "PACKAGE"
            lo, hi = 1.0, None
        elif u1 and u2 and u2.dimension == u1.dimension == "MASS":
            pass                                                   # "175g gram flour": second token is a food word
        elif u1 is None and u2 is not None:
            unit, unit_raw = u2, m.group("u2")                     # "1 small glass", "2 large handfuls"
        elif u1 is not None and u2 is not None and u2.unit_type != "PACKAGE":
            flags.append(f"second_unit_ignored:{m.group('u2')}")
        if unit and unit.unit_type == "PACKAGE" and pkg_key is None:
            pkg_key = unit.key
            kind = "PACKAGE" if kind == "NUMBER" else kind
        if unit and unit.unit_type == "VERBAL_QUALITATIVE":
            kind = "QUALITATIVE"
        value = lo if hi is None else None
        return QuantityParse(raw, kind, value=value, low=lo if hi is not None else None, high=hi,
                             unit_key=unit.key if unit else None, unit_raw=unit_raw, size=size,
                             package_key=pkg_key, package_size=pkg_size, alt=alt, stated=stated,
                             qualifiers=tuple(quals), span=m.span(), rest=_clean_rest(s[m.end():]), flags=tuple(flags))

    m = _WORDQ_RE.match(s)
    if m:
        u = _unit(m.group("u"))
        lead = (m.group("lead") or "").lower()
        if u and u.unit_type == "VERBAL_QUALITATIVE":
            return QuantityParse(raw, "QUALITATIVE", unit_key=u.key, unit_raw=m.group("u"),
                                 size=(m.group("size") or "").lower() or None, stated=stated,
                                 qualifiers=tuple(quals), span=m.span(), rest=_clean_rest(s[m.end():]))
        if u and not lead and m.group("size") and u.unit_type in ("COUNT_PORTION", "PACKAGE"):
            return QuantityParse(raw, "NUMBER", value=1.0, unit_key=u.key, unit_raw=m.group("u"),
                                 size=m.group("size").lower(), package_key=u.key if u.unit_type == "PACKAGE" else None,
                                 stated=stated, qualifiers=tuple(quals + ["implicit_one"]), span=m.span(),
                                 rest=_clean_rest(s[m.end():]))
        if u and lead:
            val = WORD_NUMBERS.get(lead)
            return QuantityParse(raw, "NUMBER" if val is not None else "QUALITATIVE", value=val, unit_key=u.key,
                                 unit_raw=m.group("u"), size=(m.group("size") or "").lower() or None,
                                 package_key=u.key if u.unit_type == "PACKAGE" else None, stated=stated,
                                 qualifiers=tuple(quals), span=m.span(), rest=_clean_rest(s[m.end():]))

    m = _WORDNUM_RE.match(s)
    if m:
        lead = m.group("lead").lower()
        if lead in WORD_COUNT:
            return QuantityParse(raw, "NUMBER", value=float(WORD_COUNT[lead]), stated=stated,
                                 qualifiers=tuple(quals), span=m.span(), rest=_clean_rest(s[m.end():]))
        return QuantityParse(raw, "QUALITATIVE", unit_raw=lead, stated=stated, qualifiers=tuple(quals),
                             span=m.span(), rest=_clean_rest(s[m.end():]))
    kind = "QUALITATIVE" if any(p in s.lower() for p in ("to taste", "as needed", "as required")) else "NONE"
    return QuantityParse(raw, kind, stated=stated, qualifiers=tuple(quals), rest=s)
