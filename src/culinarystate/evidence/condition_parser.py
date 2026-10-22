"""Step 07H layer D1: RAW PARSER. Syntax only -> typed candidate. No unit conversion, no scientific meaning, no source dialect.

parse_raw(text) -> dict:
  kind: NUMBER | RANGE | BOUND | SLASH_PAIR | LIST | QUALITATIVE | NOT_REPORTED | CENSOR_TOKEN | UNPARSED
  value / low / high (floats, sign applied) ; unit_text (as written, stripped) ; pressure_reference (only if written in the unit text)
  op in {'>','>=','<','<='} for BOUND ; approximate (bool) ; uncertainty {value, unit_text, type} ; basis_hint, variable_hint ; censor_kind ; parts (LIST)
  ambiguities: list of syntax-level flags the semantic layer must turn into AMBIGUOUS (never silently resolved).
Whatever is not recognised is UNPARSED (never guessed). Raw text is returned unchanged in `raw`.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

from .condition_units import split_pressure_unit

REG = Path(__file__).resolve().parents[3] / "registry"
DASH = "-‐‑‒–—−"
NUM = r"\d+(?:\.\d+)?|\.\d+|\d+,\d{1,2}(?!\d)"
THOUSANDS = re.compile(r"\d{1,3},\d{3}(?!\d)")
SIGNED = rf"[{DASH}+]?\s?(?:{NUM})"
UNIT = r"(?:°\s*(?:celsius|fahrenheit|centigrade|kelvin|[CFKcfk])\b|deg(?:rees?)?\s*(?:celsius|fahrenheit|centigrade|kelvin|[CFKcfk]\b)|°(?!\w)|[A-Za-zµμ%]+(?:/[A-Za-z0-9]+)?|[\"\u2033])(?:\s*\(\s*(?:a|g|d|abs|absolute|gauge|ga|diff)\s*\))?"

_NOT_REPORTED = re.compile(r"^(?:not\s+(?:reported|stated|available|given|specified)|n\.?\s?/?\s?r\.?|n/?a|unknown|unreported|missing|nil|[-–—]+)$", re.I)
_NON_DETECT = re.compile(r"^(?:n\.?d\.?|non[\s-]?detect(?:ed|able)?|not\s+detected|bdl)$", re.I)
_CENSOR_BARE = re.compile(r"^(?:(<|≤|<=)\s*(lod|loq)|(?:above|over|exceeds?)\s+(?:the\s+)?cap|capped)$", re.I)
_OPS = [(r"(?:>=|=>|≥|at\s+least|no\s+less\s+than)", ">="), (r"(?:<=|=<|≤|up\s+to|no\s+more\s+than)", "<="),
        (r"(?:>|more\s+than|greater\s+than|above|over|exceeding)", ">"), (r"(?:<|less\s+than|below|under)", "<")]
_OP_RX = [(re.compile(rf"^\s*{p}\s*", re.I), o) for p, o in _OPS]
_BASIS = [(re.compile(r"\b(?:wet|fresh)\s*(?:weight|wt|basis|mass)?\b|\bw\.?b\.?\b|\bas[\s-]is\b", re.I), "WET"), (re.compile(r"\bdry\s*(?:weight|wt|basis|matter\s+basis|mass)?\b|\bd\.?b\.?\b", re.I), "DRY")]
_LABEL_PH = re.compile(r"^\s*ph\s*[:=]?\s*", re.I)
_LABEL_AW = re.compile(r"\b(?:a\s?w|water\s+activity)\b", re.I)
_LABEL_MOIST = re.compile(r"\bmoisture(?:\s+content)?\b", re.I)
_UNCERT = re.compile(rf"^\s*(?P<v>{SIGNED})\s*(?P<u1>{UNIT})?\s*(?:±|\+/-|\+-)\s*(?P<e>{NUM})\s*(?P<u2>{UNIT})?\s*(?P<kind>sd|s\.d\.|se|sem|ci|std)?\s*$", re.I)


def _qualify_patterns() -> list[re.Pattern]:
    """approximation qualifiers come from the notation registry (QUALIFY rows), not from a second hard-coded list"""
    with open(REG / "notation_rule_registry_v1.csv", newline="", encoding="utf-8") as f:
        return [re.compile(r["pattern"], re.I) for r in csv.DictReader(f) if r["action"] == "QUALIFY"]


_APPROX = _qualify_patterns()


def _num(s: str) -> float:
    s = s.strip().replace(" ", "")
    for d in DASH:
        s = s.replace(d, "-")
    return float(s.replace(",", "."))


_VULGAR = {"\u00bc": 0.25, "\u00bd": 0.5, "\u00be": 0.75, "\u2150": 1 / 7, "\u2151": 1 / 9, "\u2152": 0.1, "\u2153": 1 / 3, "\u2154": 2 / 3, "\u2155": 0.2, "\u2156": 0.4, "\u2157": 0.6, "\u2158": 0.8, "\u2159": 1 / 6, "\u215a": 5 / 6,
           "\u215b": 0.125, "\u215c": 0.375, "\u215d": 0.625, "\u215e": 0.875}
_VULGAR_RX = re.compile(r"(?:(\d+)\s?)?([" + "".join(_VULGAR) + r"])")


def _fractions(t: str) -> str:
    """Deterministic fraction normalisation applied before NFKC: vulgar '2\u00bd'->2.5; mixed '2 1/2' and US '1-1/2' -> 1.5; common proper fractions 1/2 1/3 ... -> decimals.
    Other a/b (e.g. '15/20 min', '45/75MIN') are NOT touched: they stay AMBIGUOUS slash notation."""
    t = t.replace("\u2044", "/")  # fraction slash
    def rep(m):
        v = (int(m.group(1)) if m.group(1) else 0) + _VULGAR[m.group(2)]
        return format(round(v, 6), "g")
    t = _VULGAR_RX.sub(rep, t)
    mixed = lambda m: format(round(int(m.group(1)) + int(m.group(2)) / int(m.group(3)), 6), "g") if int(m.group(2)) < int(m.group(3)) <= 8 else m.group(0)
    t = re.sub(r"(?<![\d/.])(\d+)-(\d+)/(\d+)(?![\d/])", mixed, t)
    t = re.sub(r"(?<![\d/.])(\d+)\s+(\d+)/(\d+)(?![\d/])", mixed, t)
    return re.sub(r"(?<![\d/.])(1/2|1/3|2/3|1/4|3/4|1/8|3/8|5/8|7/8)(?![\d/])", lambda m: format(round(int(m.group(1).split("/")[0]) / int(m.group(1).split("/")[1]), 6), "g"), t)


def _clean(text: str) -> str:
    t = unicodedata.normalize("NFKC", _fractions(str(text).replace("\u00ba", "\u00b0").replace("\u2033", '"'))).replace("\u00a0", " ")  # ordinal indicator -> degree sign
    return re.sub(r"\s+", " ", t).strip()


def _result(kind: str, raw, **kw) -> dict:
    d = {"kind": kind, "raw": raw, "value": None, "low": None, "high": None, "unit_text": None, "pressure_reference": None, "op": None, "approximate": False, "uncertainty": None,
         "basis_hint": None, "variable_hint": None, "censor_kind": None, "qualitative": None, "parts": None, "residual": "", "ambiguities": []}
    d.update(kw)
    return d


def _unit(u: str | None):
    """-> (unit_text, pressure_reference_if_written)"""
    if not u:
        return None, None
    u = u.strip()
    base, ref = split_pressure_unit(u)
    return (base, ref) if ref else (u, None)


def parse_raw(text) -> dict:
    raw = text
    if text is None or _clean(text) == "":
        return _result("NOT_REPORTED", raw)
    t = _clean(text)
    if _NOT_REPORTED.match(t):
        return _result("NOT_REPORTED", raw)
    if _NON_DETECT.match(t):
        return _result("CENSOR_TOKEN", raw, censor_kind="NON_DETECT")
    m = _CENSOR_BARE.match(t)
    if m:
        k = {"lod": "BELOW_LOD", "loq": "BELOW_LOQ"}.get((m.group(2) or "").lower(), "ABOVE_CAP")
        return _result("CENSOR_TOKEN", raw, censor_kind=k, op="<" if k != "ABOVE_CAP" else ">")
    if ";" in t:
        parts = [parse_raw(p) for p in t.split(";") if p.strip()]
        return _result("LIST", raw, parts=parts, ambiguities=["LIST_ROLES_UNKNOWN"])
    if THOUSANDS.search(t):
        return _result("UNPARSED", raw, residual=t, ambiguities=["DECIMAL_COMMA_OR_THOUSANDS"])
    approx = False
    for rx in _APPROX:
        if rx.search(t):
            approx = True
            t = rx.sub(" ", t)
    t = _clean(t)
    op = None
    for rx, o in _OP_RX:
        if rx.match(t):
            op, t = o, rx.sub("", t, count=1)
            break
    cens = None
    if op and re.search(r"\blod\b", t, re.I):
        cens = "BELOW_LOD"
    elif op and re.search(r"\bloq\b", t, re.I):
        cens = "BELOW_LOQ"
    var_hint = basis = None
    t = re.sub(r"\b(?:with\s+)?basis\s+(?:missing|not\s+(?:stated|reported|given)|unknown)\b|\bwithout\s+basis\b", " ", t, flags=re.I)
    if _LABEL_PH.match(t):
        var_hint, t = "ph", _LABEL_PH.sub("", t, count=1)
    if _LABEL_AW.search(t):
        var_hint, t = "water_activity", _LABEL_AW.sub(" ", t)
    if _LABEL_MOIST.search(t):
        var_hint, t = "moisture_content", _LABEL_MOIST.sub(" ", t)
    for rx, b in _BASIS:
        if rx.search(t) and (var_hint == "moisture_content" or re.search(r"\bbasis\b|\bweight\b", t, re.I)):
            basis, t = b, rx.sub(" ", t)
            t = re.sub(r"\bbasis\b", " ", t, flags=re.I)
            break
    t = _clean(t.strip(",: "))
    if t.count("(") != t.count(")"):
        t = _clean(t.strip("()"))
    base = dict(approximate=approx, basis_hint=basis, variable_hint=var_hint, censor_kind=cens)
    # uncertainty (kept separate from range)
    u = _UNCERT.match(t)
    if u:
        u1, ref1 = _unit(u.group("u1"))
        u2, _ = _unit(u.group("u2"))
        kind_t = (u.group("kind") or "").lower()
        utype = {"sd": "SD", "s.d.": "SD", "std": "SD", "se": "SE", "sem": "SE", "ci": "CI"}.get(kind_t, "REPORTED_UNSPECIFIED")
        amb = ["UNCERTAINTY_UNIT_CONFLICT"] if u1 and u2 and u1.lower() != u2.lower() else []
        return _result("NUMBER", raw, value=_num(u.group("v")), unit_text=u1 or u2, pressure_reference=ref1, uncertainty={"value": _num(u.group("e")), "unit_text": u2 or u1, "type": utype}, ambiguities=amb, **base)
    # compound amounts: '1 hr 30 mins' / '2 hours and 15 minutes' (all parts NUMBER+unit)
    UC = r"(?!(?:to|and|or|by|x)(?![A-Za-z]))(?:" + UNIT + ")"
    cp = re.fullmatch(rf"(?:{NUM})\s*{UC}(?:\s*(?:and|,|&)?\s*(?:{NUM})\s*{UC})+", t, re.I)
    if cp:
        parts = [(_num(a), b) for a, b in re.findall(rf"({NUM})\s*({UC})", t, re.I)]
        return _result("COMPOUND", raw, parts=[{"value": v, "unit_text": u} for v, u in parts], ambiguities=[], **base)
    # slash pair 15/20 min
    s = re.fullmatch(rf"(?P<a>{NUM})\s*/\s*(?P<b>{NUM})\s*(?P<u>{UNIT})?", t)
    if s:
        un, ref = _unit(s.group("u"))
        return _result("SLASH_PAIR", raw, low=_num(s.group("a")), high=_num(s.group("b")), unit_text=un, pressure_reference=ref, ambiguities=["SLASH_NOTATION_RANGE_OR_ALTERNATIVES"], **base)
    # range  a - b  |  a to b   (first number may carry a sign; a dash directly before the first number is its sign)
    r = re.fullmatch(rf"(?P<a>{SIGNED})\s*(?P<u1>{UNIT})?\s*(?:[{DASH}]|\bto(?![A-Za-z])|\band\b)\s*(?P<b>{SIGNED})\s*(?P<u2>{UNIT})?", t, re.I)
    if r:
        u1, ref1 = _unit(r.group("u1"))
        u2, ref2 = _unit(r.group("u2"))
        un, ref = u2 or u1, ref2 or ref1
        amb = ["RANGE_UNIT_CONFLICT"] if u1 and u2 and u1.lower() != u2.lower() else []
        lo, hi = _num(r.group("a")), _num(r.group("b"))
        if op:
            amb.append("OPERATOR_WITH_RANGE")
        return _result("RANGE", raw, low=lo, high=hi, unit_text=un, pressure_reference=ref, ambiguities=amb, op=op, **base)
    # single number
    n = re.fullmatch(rf"(?P<v>{SIGNED})\s*(?P<u>{UNIT})?", t, re.I)
    if n:
        un, ref = _unit(n.group("u"))
        amb = ["SPACED_DASH_SIGN_OR_RANGE_FRAGMENT"] if re.match(rf"^[{DASH}]\s+\d", t) else []
        if op:
            v = _num(n.group("v"))
            lim = dict(low=v) if op in (">", ">=") else dict(high=v)
            return _result("BOUND", raw, unit_text=un, pressure_reference=ref, op=op, ambiguities=amb, **lim, **base)
        return _result("NUMBER", raw, value=_num(n.group("v")), unit_text=un, pressure_reference=ref, ambiguities=amb, **base)
    # pure words (no digit) -> qualitative ; otherwise unparsed
    if not re.search(r"\d", t):
        if cens or op:
            return _result("CENSOR_TOKEN", raw, censor_kind=cens or "NON_DETECT", op=op)
        return _result("QUALITATIVE", raw, qualitative=_clean(text), **base)
    return _result("UNPARSED", raw, residual=t, **base)
