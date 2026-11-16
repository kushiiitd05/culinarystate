"""Verification of the packet's claim "Food.com source drops units" (counts only, no text kept).

For each Food.com recipe in the given records: how the two Kaggle lists (RecipeIngredientQuantities, RecipeIngredientParts)
relate, whether any quantity string carries a unit word, whether the ingredient part carries one, and what the rc2
grammar finds in the positionally paired line. Wikibooks / TASTEset lines are counted the same way as a contrast.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Mapping

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2
from culinarystate.quantity.units import ALIAS, UNITS

from .line_grams import normalise_text

NUMERIC = re.compile(r"^[0-9\s/.,\-–½⅓⅔¼¾⅛⅜⅝⅞]+$")
_MV = {a.lower() for u in UNITS if u.dimension in ("MASS", "VOLUME") for a in u.aliases if len(a) > 1}
_COUNT = {a.lower() for u in UNITS if u.unit_type in ("COUNT_PORTION", "PACKAGE") for a in u.aliases if len(a) > 1}
_ANY = {k.lower() for k in ALIAS if len(k) > 1}


ZERO_KEYS = ("recipes", "recipes_q_len_equal_p_len", "recipes_q_len_greater_than_p_len", "recipes_q_len_less_than_p_len",
             "parts_total", "quantity_strings_total", "quantity_strings_missing", "quantity_strings_numeric_only",
             "quantity_strings_non_numeric", "quantity_strings_with_ascii_letters", "quantity_strings_with_unit_token",
             "parts_with_leading_unit_token", "parts_with_mass_or_volume_unit_token",
             "parts_with_count_or_package_unit_token", "paired_lines", "paired_lines_with_stated_mass",
             "paired_lines_with_other_unit", "paired_lines_bare_number_no_unit", "paired_lines_no_quantity_or_other")


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z]+", (s or "").lower())


def units_check(records: Iterable[Mapping], schema: Mapping | None = None) -> dict:
    schema = schema or D.load_schema()
    ctx = GroundingContext(source_metadata=D.SOURCE_META, locale="US", locale_metadata=D.LOCALE_META)
    c: Counter = Counter({k: 0 for k in ZERO_KEYS})
    contrast: Counter = Counter()
    for rec in records:
        fam = rec.get("source_family")
        if fam == "FOODCOM":
            ex = rec.get("extra") or {}
            parts, q = list(ex.get("ingredient_parts") or []), list(ex.get("q_raw") or [])
            c["recipes"] += 1
            c["recipes_q_len_equal_p_len" if len(q) == len(parts) else
              "recipes_q_len_greater_than_p_len" if len(q) > len(parts) else "recipes_q_len_less_than_p_len"] += 1
            c["parts_total"] += len(parts)
            for s in q:
                c["quantity_strings_total"] += 1
                if s is None or not str(s).strip():
                    c["quantity_strings_missing"] += 1
                    continue
                t = normalise_text(str(s))
                c["quantity_strings_numeric_only" if NUMERIC.match(t) else "quantity_strings_non_numeric"] += 1
                if re.search(r"[A-Za-z]", t):
                    c["quantity_strings_with_ascii_letters"] += 1
                if any(w in _ANY for w in _tokens(t)):
                    c["quantity_strings_with_unit_token"] += 1
            for p in parts:
                toks = _tokens(p)
                c["parts_with_leading_unit_token"] += bool(toks and toks[0] in _ANY)
                c["parts_with_mass_or_volume_unit_token"] += any(w in _MV for w in toks)
                c["parts_with_count_or_package_unit_token"] += any(w in _COUNT for w in toks)
            if len(q) == len(parts):                                      # only aligned recipes are paired
                for s, p in zip(q, parts):
                    text = f"{normalise_text(str(s)) if s else ''} {p}".strip()
                    try:
                        r = ground_quantity_rc2(text, ctx, schema=schema)
                    except Exception:  # noqa: BLE001
                        c["paired_lines_exception"] += 1
                        continue
                    c["paired_lines"] += 1
                    kind = r.record["parsed"]["kind"]
                    unit_raw = r.record["parsed"].get("unit_raw")
                    if r.exact_mass is not None:
                        c["paired_lines_with_stated_mass"] += 1
                    elif unit_raw is not None:
                        c["paired_lines_with_other_unit"] += 1
                    elif kind in ("NUMBER", "FRACTION", "RANGE", "MIXED"):
                        c["paired_lines_bare_number_no_unit"] += 1
                    else:
                        c["paired_lines_no_quantity_or_other"] += 1
        elif fam in ("WIKIBOOKS", "TASTESET"):
            for line in rec.get("ingredient_lines") or []:
                if not isinstance(line, str) or not line.strip():
                    continue
                try:
                    r = ground_quantity_rc2(normalise_text(line), ctx, schema=schema)
                except Exception:  # noqa: BLE001
                    continue
                contrast[f"{fam}_lines"] += 1
                if r.exact_mass is not None:
                    contrast[f"{fam}_lines_with_stated_mass"] += 1
                elif r.record["parsed"].get("unit_raw") is not None:
                    contrast[f"{fam}_lines_with_other_unit"] += 1
                elif r.record["parsed"]["kind"] in ("NUMBER", "FRACTION", "RANGE", "MIXED"):
                    contrast[f"{fam}_lines_bare_number_no_unit"] += 1
    out = dict(sorted(c.items()))
    pl = c["paired_lines"] or 1
    verdict = ("CONFIRMED_UNITS_ABSENT" if c["quantity_strings_with_unit_token"] == 0
               and c["paired_lines_with_stated_mass"] * 100 < pl else "NOT_CONFIRMED_UNITS_PRESENT_IN_SOME_LINES")
    return {"record": "FOODCOM_UNITS_CHECK_S176", "status": "AI_ENGINEERING_COUNTS_ONLY", "contains_ids": False,
            "contains_text": False, "counts_as_human_gate": False, "foodcom": out, "contrast_other_sources": dict(sorted(contrast.items())),
            "verdict_rule": "NO_UNIT_TOKEN_IN_ANY_QUANTITY_STRING_AND_UNDER_1PCT_PAIRED_LINES_WITH_STATED_MASS",
            "verdict": verdict}
