"""FDA/CFSAN "Approximate pH of Foods and Food Products" (Oct 2003; webharvest.gov 2004 archive) for lot state (S175).

Each row keeps the raw text; values are typed POINT, INTERVAL or LOWER_BOUND_ONLY ("5.00 -"). With
``strict=False`` a source typo (e.g. "5.2l") is kept as UNPARSED with no value, never corrected by guess. Lookup by name:
an item whose tokens equal the query tokens is FDA_ITEM_MATCH; otherwise the union over every item with the same
head noun (last token of the first comma segment) is FDA_HEAD_UNION; else UNKNOWN. ``any_form_*`` is always the
head union (all forms: raw, cooked, canned ...). These are published approximate ranges for single foods, never a
mixture pH: the lot layer derives flags, not a number.

Acid classes use the 4.6 equilibrium-pH boundary of 21 CFR 113.3 (low-acid foods) and 21 CFR 114.3 (acidified).

S179 (P5, fixes A1-A3): the canonical table is the L-PH registry ``registry/food_ph_fda_draft_v1.csv`` (April 2007
revision, 488 rows; D-079 PROPOSED). ``load_registry_lph`` keys each row by ``item_context_norm`` so an indented
child keeps its parent ("White" under "Eggs, new-laid, whole" -> "eggs, white"). Rows without a printed pH and the
one UNPARSED_REVIEW typo carry no value; the documented whitespace repair ("4. 10" -> 4.10) is kept. The 2003/2004
registry ``food_ph_fda2003_v1.csv`` stays on record as SUPERSEDED.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from html.parser import HTMLParser

from culinarystate.composition.ing_sr_match import normalise

SOURCE = "FDA/CFSAN Approximate pH of Foods and Food Products, Oct 2003 (webharvest.gov peth04, 2004-10-31)"
SOURCE_LPH = "FDA/CFSAN Approximate pH of Foods and Food Products, Apr 2007 revision (L-PH draft registry v1)"
ACID_PH_MAX = 4.6
_LPH_VALUED = frozenset({"PARSED", "PARSED_OPEN_ENDED", "PARSED_REPAIRED_WS"})
_NUM = r"\d+(?:\.\d+)?"
_RANGE = re.compile(rf"^({_NUM})\s*-\s*({_NUM})?$")
_POINT = re.compile(rf"^({_NUM})$")


@dataclass(frozen=True)
class PHRow:
    item: str
    low: float | None
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


def _row_or_unparsed(item: str, raw: str, strict: bool) -> PHRow:
    try:
        return _row(item, raw)
    except ValueError:
        if strict:
            raise
        return PHRow(item, None, None, "UNPARSED", raw)


def parse_fda_html(html: str, *, strict: bool = True) -> list[PHRow]:
    p = _Cells()
    p.feed(html)
    return [_row_or_unparsed(r[0], r[1], strict) for r in p.rows
            if len(r) >= 2 and r[0] and r[1] and r[0] != "Item" and not any(c.strip() for c in r[2:])]


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
        self.rows = tuple(r for r in rows if r.low is not None)
        self._tokens = {r.item: frozenset(normalise(r.item)) for r in self.rows}
        self._heads = {r.item: _head(r.item) for r in self.rows}
        self._memo: dict[tuple[str, ...], PHRange] = {}

    def lookup(self, name: str) -> PHRange:
        q = normalise(name)
        if q not in self._memo:                 # S179 F4: the table is immutable, so memoise per name
            self._memo[q] = self._lookup(q)
        return self._memo[q]

    def _lookup(self, q: tuple[str, ...]) -> PHRange:
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


def load_registry(path) -> list[PHRow]:
    """Rows of registry/food_ph_fda2003_v1.csv (built by tools/build_food_ph_registry.py)."""
    def num(s: str) -> float | None:
        return float(s) if s.strip() else None

    with open(path, newline="", encoding="utf-8") as fh:
        return [PHRow(r["item"], num(r["ph_low"]), num(r["ph_high"]), r["value_type"], r["ph_raw"])
                for r in csv.DictReader(fh)]


def load_registry_lph(path) -> list[PHRow]:
    """Rows of the L-PH registry (registry/food_ph_fda_draft_v1.csv), item = parent-context name (S179 P5)."""
    def num(x: str) -> float | None:
        return float(x) if x.strip() else None

    def row(r: dict) -> PHRow:
        item = r["item_context_norm"] or r["item_norm"]
        if r["parse_status"] not in _LPH_VALUED:
            vt = "NONE" if r["ph_value_type"] == "NONE" else "UNPARSED"
            return PHRow(item, None, None, vt, r["ph_raw"])
        lo, hi = num(r["ph_low"]), num(r["ph_high"])
        if lo is None:
            raise ValueError(f"{r['ph_id']}: parsed row without ph_low")
        vt = "LOWER_BOUND_ONLY" if hi is None else ("POINT" if lo == hi else "INTERVAL")
        return PHRow(item, lo, hi, vt, r["ph_raw"])

    with open(path, newline="", encoding="utf-8") as fh:
        return [row(r) for r in csv.DictReader(fh)]
