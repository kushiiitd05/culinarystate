"""Bognár (2002) Part 1 weight-yield tables (pdftotext -layout) -> rows.

Row layout: description, raw-product code ("FR/TK m.S"), cooking code(s) ("a", "e/g", "a*"), [core temperature °C
in meat tables, kept as printed: "~ 95", "> 80"], yield with waste
x ±, yield of the edible part x ±, n. Codes come from the table legends; "-" = not available. Sub-part rows
("-  , egg part") have no raw-product code and are not kept. Yield = cooked weight / raw weight.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

TABLE = re.compile(r"^Table (\d+)\s*:\s*Weight yield")
NUM = r"(\d+[.,]\d\d|-)"                        # a few cells print a decimal comma
ROW = re.compile(r"^\s{0,3}(?P<desc>\S.*?)\s{2,}(?P<raw>(?:FR|TK|VK|TP|TR)\*?(?:/(?:FR|TK|VK|TP|TR)\*?)*)\s+"
                 r"(?P<rec>[mo]\.[ZSF])\s+(?P<cook>[a-hmrsCD](?:/[a-hmrsCD])*)(?P<star>\*?)\s+(?:(?P<core>[~<>]\s*\d+|\d+-\d+|\d{2,3}|-)\s+)?"
                 rf"{NUM}\s+{NUM}\s+{NUM}\s+{NUM}\s+(?P<n>\d+|-)\s*$")
RAW = {"FR": "fresh raw", "FR*": "fresh boiled", "TK": "deep frozen raw", "VK": "canned", "TP": "dried product",
       "TR": "dried raw"}
RECIPE = {"m.Z": "with ingredients", "o.Z": "without ingredients", "m.S": "with salt and spice",
          "m.F": "with ingredients and fat absorption"}
COOK = {"a": "boil", "b": "steam", "c": "stew", "d": "fry in pan", "e": "fry in oven", "f": "deep fry",
        "g": "grill", "h": "contact fry", "m": "mix", "r": "heat", "s": "braise",
        "C": "juice centrifuge", "D": "steam juicing"}


@dataclass(frozen=True)
class YieldRow:
    table: int
    description: str
    raw_states: tuple[str, ...]
    recipe: str
    methods: tuple[str, ...]
    with_waste: float | None
    with_waste_ci: float | None
    edible: float | None
    edible_ci: float | None
    n: int | None
    by_producer_instruction: bool
    core_temp_c: str | None
    line: int


def _f(x: str) -> float | None:
    return None if x == "-" else float(x.replace(",", "."))


def parse_yields(text: str) -> list[YieldRow]:
    rows, table = [], None
    for i, line in enumerate(text.split("\n"), 1):
        line = line.lstrip("\x0c")
        t = TABLE.match(line)
        if t:
            table = int(t.group(1))
            continue
        if line.startswith("Table "):
            table = None
        m = ROW.match(line) if table else None
        if not m:
            continue
        dx, dpm, ex, epm = m.group(7, 8, 9, 10)
        rows.append(YieldRow(table, m["desc"].strip(), tuple(RAW[c] for c in m["raw"].split("/")),
                             RECIPE.get(m["rec"], f"{m['rec']} (not in legend)"),
                             tuple(COOK[c] for c in m["cook"].split("/")), _f(dx), _f(dpm), _f(ex), _f(epm),
                             None if m["n"] == "-" else int(m["n"]), bool(m["star"]),
                             None if m["core"] in (None, "-") else m["core"], i))
    return rows
