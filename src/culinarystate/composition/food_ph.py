"""FDA/CFSAN "Approximate pH of Foods and Food Products" (Oct 2003; webharvest.gov 2004 archive) for lot state (S175).

Each row keeps the raw text; values are typed POINT, INTERVAL or LOWER_BOUND_ONLY ("5.00 -"). Lookup by name:
an item whose tokens equal the query tokens is FDA_ITEM_MATCH; otherwise the union over every item with the same
head noun (last token of the first comma segment) is FDA_HEAD_UNION; else UNKNOWN. ``any_form_*`` is always the
head union (all forms: raw, cooked, canned ...). These are published approximate ranges for single foods, never a
mixture pH: the lot layer derives flags, not a number.

Acid classes use the 4.6 equilibrium-pH boundary of 21 CFR 113.3 (low-acid foods) and 21 CFR 114.3 (acidified).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser

from culinarystate.composition.ing_sr_match import normalise

SOURCE = "FDA/CFSAN Approximate pH of Foods and Food Products, Oct 2003 (webharvest.gov peth04, 2004-10-31)"
ACID_PH_MAX = 4.6
_NUM = r"\d+(?:\.\d+)?"
_RANGE = re.compile(rf"^({_NUM})\s*-\s*({_NUM})?$")
_POINT = re.compile(rf"^({_NUM})$")


@dataclass(frozen=True)
class PHRow:
    item: str
    low: float
    high: float | None
    value_type: str
    raw: str


@dataclass(frozen=True)
class PHRange:
    low: float | None
    high: float | None
    basis: str
    items: tuple[str, ...]
    any_form_low: float | None
    any_form_high: float | None


class _Cells(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _row(item: str, raw: str) -> PHRow:
    if m := _POINT.match(raw):
        v = float(m.group(1))
        return PHRow(item, v, v, "POINT", raw)
    if m := _RANGE.match(raw):
        lo = float(m.group(1))
        if m.group(2) is None:
            return PHRow(item, lo, None, "LOWER_BOUND_ONLY", raw)
        hi = float(m.group(2))
        return PHRow(item, lo, hi, "POINT" if lo == hi else "INTERVAL", raw)
    raise ValueError(f"unparsed pH {raw!r} for item {item!r}")


def parse_fda_html(html: str) -> list[PHRow]:
    p = _Cells()
    p.feed(html)
    return [_row(r[0], r[1]) for r in p.rows
            if len(r) == 2 and r[0] and r[1] and r[0] != "Item"]


def _head(text: str) -> str:
    first = normalise(text.split(",")[0])
    return first[-1] if first else ""


def _span(rows: list[PHRow]) -> tuple[float | None, float | None]:
    if not rows:
        return None, None
    highs = [r.high for r in rows]
    return min(r.low for r in rows), (None if None in highs else max(highs))


class PHTable:
    def __init__(self, rows: list[PHRow]) -> None:
        self.rows = tuple(rows)
        self._tokens = {r.item: frozenset(normalise(r.item)) for r in self.rows}
        self._heads = {r.item: _head(r.item) for r in self.rows}

    def lookup(self, name: str) -> PHRange:
        q = normalise(name)
        head = q[-1] if q else ""
        same_head = sorted((r for r in self.rows if self._heads[r.item] == head), key=lambda r: r.item)
        any_lo, any_hi = _span(same_head)
        exact = sorted((r for r in self.rows if self._tokens[r.item] == frozenset(q)), key=lambda r: r.item)
        if exact:
            lo, hi = _span(exact)
            return PHRange(lo, hi, "FDA_ITEM_MATCH", tuple(r.item for r in exact), any_lo, any_hi)
        if same_head:
            return PHRange(any_lo, any_hi, "FDA_HEAD_UNION", tuple(r.item for r in same_head), any_lo, any_hi)
        return PHRange(None, None, "UNKNOWN", (), None, None)


def acid_class(r: PHRange) -> str:
    if r.basis == "UNKNOWN" or r.low is None:
        return "UNKNOWN"
    if r.high is not None and r.high <= ACID_PH_MAX:
        return "ACID"
    if r.low > ACID_PH_MAX:
        return "LOW_ACID"
    return "STRADDLES_4_6"
