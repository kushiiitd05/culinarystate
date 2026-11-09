"""S175: FDA/CFSAN approximate pH list (2003/2004 archive) -> registry rows and per-ingredient pH ranges."""
from __future__ import annotations

import pytest

from culinarystate.composition import food_ph as PH

HTML = """<html><body><table>
<tr><td></td><td></td></tr>
<tr><th>Item</th><th>Approximate pH</th></tr>
<tr><td>Carrots</td><td>4.90 - 5.20</td></tr>
<tr><td>Carrots, cooked</td><td>5.58 - 6.03</td></tr>
<tr><td>Lemon juice</td><td>2.00 - 2.60</td></tr>
<tr><td>Abalone mushroom</td><td>5.00 -</td></tr>
<tr><td>Cauliflower</td><td>5.60</td></tr>
<tr><td>Onions, red</td><td>5.30 - 5.80</td></tr>
<tr><td>Onions, white</td><td>5.37 - 5.85</td></tr>
<tr><td>Milk, cow</td><td>6.40 - 6.80</td></tr>
</table></body></html>"""


def rows():
    return PH.parse_fda_html(HTML)


def test_parse_keeps_raw_and_types_each_value() -> None:
    r = {x.item: x for x in rows()}
    assert set(r) == {"Carrots", "Carrots, cooked", "Lemon juice", "Abalone mushroom", "Cauliflower", "Onions, red",
                      "Onions, white", "Milk, cow"}
    assert (r["Carrots"].low, r["Carrots"].high, r["Carrots"].value_type) == (4.9, 5.2, "INTERVAL")
    assert (r["Cauliflower"].low, r["Cauliflower"].high, r["Cauliflower"].value_type) == (5.6, 5.6, "POINT")
    a = r["Abalone mushroom"]
    assert (a.low, a.high, a.value_type, a.raw) == (5.0, None, "LOWER_BOUND_ONLY", "5.00 -")


def test_bad_value_fails_loudly() -> None:
    with pytest.raises(ValueError, match="Carrots"):
        PH.parse_fda_html(HTML.replace("4.90 - 5.20", "about five"))


def test_lookup_specific_item_then_head_union() -> None:
    tab = PH.PHTable(rows())
    lj = tab.lookup("lemon juice")
    assert (lj.low, lj.high, lj.basis) == (2.0, 2.6, "FDA_ITEM_MATCH") and lj.items == ("Lemon juice",)
    on = tab.lookup("onion")             # no plain "Onions" row: union over every Onions row
    assert (on.low, on.high, on.basis) == (5.3, 5.85, "FDA_HEAD_UNION")
    assert set(on.items) == {"Onions, red", "Onions, white"}
    c = tab.lookup("carrot")
    assert (c.low, c.high, c.basis) == (4.9, 5.2, "FDA_ITEM_MATCH")
    assert (c.any_form_low, c.any_form_high) == (4.9, 6.03)


def test_unknown_and_open_bound() -> None:
    tab = PH.PHTable(rows())
    u = tab.lookup("saffron")
    assert (u.basis, u.low, u.high) == ("UNKNOWN", None, None)
    m = tab.lookup("abalone mushroom")
    assert (m.low, m.high) == (5.0, None)


def test_acid_classes_use_the_21cfr114_threshold() -> None:
    assert PH.ACID_PH_MAX == 4.6
    tab = PH.PHTable(rows())
    assert PH.acid_class(tab.lookup("lemon juice")) == "ACID"            # high <= 4.6
    assert PH.acid_class(tab.lookup("milk")) == "LOW_ACID"               # low > 4.6
    assert PH.acid_class(tab.lookup("saffron")) == "UNKNOWN"
    straddle = PH.PHRange(4.2, 5.0, "FDA_ITEM_MATCH", ("x",), 4.2, 5.0)
    assert PH.acid_class(straddle) == "STRADDLES_4_6"


def test_non_strict_keeps_source_typos_as_unparsed_rows() -> None:
    bad = HTML.replace("4.90 - 5.20", "5.18 - 5.2l")
    r = {x.item: x for x in PH.parse_fda_html(bad, strict=False)}
    c = r["Carrots"]
    assert (c.low, c.high, c.value_type, c.raw) == (None, None, "UNPARSED", "5.18 - 5.2l")
    assert PH.PHTable(list(r.values())).lookup("carrot").low == 5.58     # unparsed rows never feed a range


def test_real_registry_loads_and_matches_known_rows() -> None:
    from pathlib import Path
    rows = PH.load_registry(Path(__file__).resolve().parents[2] / "registry/food_ph_fda2003_v1.csv")
    assert len(rows) >= 470 and {r.value_type for r in rows} <= {"POINT", "INTERVAL", "LOWER_BOUND_ONLY", "UNPARSED"}
    by = {r.item: r for r in rows}
    assert (by["Carrots, cooked"].low, by["Carrots, cooked"].high) == (5.58, 6.03)
    assert PH.acid_class(PH.PHTable(rows).lookup("lemon juice")) == "ACID"
