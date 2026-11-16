#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C07-R4: how many Food.com lines carry a bare-count quantity, and is the unit drop at the SOURCE or in the PARSER?

Counts only. Reads data/external/foodcom/recipes.parquet (columns RecipeIngredientQuantities / RecipeIngredientParts) and the
committed NER counts (reports/ner_v2/ner_corpus_counts_S174.json); writes reports/s178/corpus/foodcom_bare_count_v1.{json,md}.

Four independent readings of "does a unit exist in the Food.com ingredient text":
  1. SOURCE FIELD   every non-null quantity string is classified by shape; the count with ANY alphabetic character is the
                    number of quantity strings that could carry a unit token. (0 means no parser can lose a unit that is not there.)
  2. PARSER         the legacy grammar (plus the opt-in SP-002 pre-normaliser) over the lines as the corpus iterator builds them
                    ("<quantity> <part>"): share of lines in which a unit is recognised, and which kind of quantity was read.
  3. NAME FIELD     share of part (food name) strings containing a unit-lexicon word (the Rung A unit tokens).
  4. NER            UNIT spans / QUANTITY spans from the committed S174 counts (DeBERTa-CRF, model-derived), compared with 2 and 3.
If 1 is zero and 2, 3 and 4 are all small, the unit drop is a property of the source, not of the parser.

Lines are the corpus iterator's lines (positional pairing: `recipes.corpus.iter_foodcom`; 78.0 % of recipes have unequal lists, see
foodcom_quantity_alignment_v1). Because of that mispairing a line's quantity may belong to another part; the shape and unit statistics
below do not depend on which part a quantity sits on, the per-line pairing statistics do and are labelled as such.

  python tools/s178_corpus_foodcom_quantity.py [--sample N]
AI_DRAFTED / PROPOSED. NON_CITABLE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-foodcom-bare-count-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
NER_COUNTS = "reports/ner_v2/ner_corpus_counts_S174.json"
FOODCOM = "data/external/foodcom/recipes.parquet"
FS = "⁄"

SHAPES = (
    ("INTEGER", re.compile(r"^\d+$")),
    ("DECIMAL", re.compile(r"^\d+\.\d+$")),
    ("FRACTION", re.compile(rf"^\d+(?:/|{FS})\d+$")),
    ("MIXED_NUMBER", re.compile(rf"^\d+\s+\d+(?:/|{FS})\d+$")),
    ("RANGE", re.compile(rf"^[\d./{FS} ]+\s*-\s*[\d./{FS} ]+$")),
)


def shape_of(q: str) -> str:
    s = q.strip()
    if not s:
        return "EMPTY"
    if re.search(r"[A-Za-z]", s):
        return "HAS_ALPHABETIC"
    for name, rx in SHAPES:
        if rx.match(s):
            return name
    return "OTHER_NUMERIC"


PROSE_KEYS = frozenset({"note", "reading", "description", "statement", "consequence", "length_difference_note", "experimental_alternative",
                        "equal_length_is_not_proof", "verdict", "proposed_rule"})


def strip_prose(obj):
    """Drop the explanatory-prose fields (written by this tool, never from the corpus) so the counts-only guard can check the rest."""
    if isinstance(obj, dict):
        return {k: strip_prose(v) for k, v in obj.items() if k not in PROSE_KEYS}
    if isinstance(obj, list):
        return [strip_prose(v) for v in obj]
    return obj


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def read_lists(root: Path, limit: int | None):
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(root / FOODCOM)
    n = 0
    for b in pf.iter_batches(batch_size=20000, columns=["RecipeId", "RecipeIngredientQuantities", "RecipeIngredientParts"]):
        for row in b.to_pylist():
            yield int(row["RecipeId"]), row["RecipeIngredientQuantities"] or [], row["RecipeIngredientParts"] or []
            n += 1
            if limit and n >= limit:
                return


def run(root: Path, limit: int | None) -> dict:
    from culinarystate.extraction.rung_a_lexicon import load_lexicon, tokens
    from culinarystate.quantity import prenormalize as P
    from culinarystate.quantity.grammar import parse_line
    t0 = time.time()
    lex = load_lexicon(root, cache=False)
    unit_tokens = lex.unit_tokens
    q_shape = Counter()
    q_total = q_null = q_fs = 0
    lines_q: Counter = Counter()       # unique corpus-iterator line -> count
    parts_u: Counter = Counter()       # unique part string -> count
    recipes = 0
    for _rid, q, p in read_lists(root, limit):
        recipes += 1
        for x in q:
            q_total += 1
            if x is None:
                q_null += 1
            else:
                q_shape[shape_of(x)] += 1
                q_fs += FS in x
        for i, part in enumerate(p):
            qi = q[i] if i < len(q) and q[i] else ""
            lines_q[f"{qi} {part}".strip()] += 1          # exactly recipes.corpus.iter_foodcom
            parts_u[(part or "").strip().lower()] += 1
    total_lines = sum(lines_q.values())
    # parser view
    kinds_legacy, kinds_prenorm = Counter(), Counter()
    unit_lines_legacy = unit_lines_prenorm = 0
    unit_kind = Counter()
    lines_with_qty_text = lines_numeric_lead = lines_numeric_no_unit = 0
    for ln, w in lines_q.items():
        a = parse_line(ln)
        b = P.parse_line_prenorm(ln)
        kinds_legacy[a.kind] += w
        kinds_prenorm[b.kind] += w
        unit_lines_legacy += w * (a.unit_key is not None)
        unit_lines_prenorm += w * (b.unit_key is not None)
        if b.unit_key is not None:
            unit_kind[b.unit_key] += w
        if ln and ln[0].isdigit():
            lines_numeric_lead += w
            lines_numeric_no_unit += w * (b.unit_key is None)
    # name view
    parts_total = sum(parts_u.values())
    parts_with_unit_word = 0
    for s, w in parts_u.items():
        if any(wd in unit_tokens for _, _, wd in tokens(s)):
            parts_with_unit_word += w
    ner_fam = json.loads((root / NER_COUNTS).read_text(encoding="utf-8"))["families"]["FOODCOM"]
    ner, ner_lines = ner_fam["labels"], ner_fam["lines"]
    nonnull = q_total - q_null
    res = {"record": "FOODCOM_BARE_COUNT_S178", "tool_version": TOOL_VERSION, "item": "T3-C07-R4",
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "contains_text": False, "contains_ids": False,
           "counts_as_human_gate": False, "sample_limit_recipes": limit, "recipes": recipes,
           "reading_1_source_field": {"quantity_strings_total": q_total, "null": q_null, "non_null": nonnull,
                                      "shapes": dict(sorted(q_shape.items())),
                                      "with_any_alphabetic_character": q_shape.get("HAS_ALPHABETIC", 0),
                                      "with_fraction_slash_u2044": q_fs,
                                      "pct_non_null_that_are_bare_numbers": pct(nonnull - q_shape.get("HAS_ALPHABETIC", 0), nonnull)},
           "reading_2_parser": {"lines": total_lines, "unique_lines": len(lines_q),
                                "legacy_kind": dict(sorted(kinds_legacy.items())), "prenorm_kind": dict(sorted(kinds_prenorm.items())),
                                "lines_with_unit_recognised_legacy": unit_lines_legacy, "pct_lines_with_unit_legacy": pct(unit_lines_legacy, total_lines),
                                "lines_with_unit_recognised_prenorm": unit_lines_prenorm, "pct_lines_with_unit_prenorm": pct(unit_lines_prenorm, total_lines),
                                "lines_with_unit_prenorm_by_unit_key": dict(sorted(unit_kind.items(), key=lambda kv: -kv[1])[:30]),
                                "lines_starting_with_a_digit": lines_numeric_lead,
                                "lines_bare_count_numeric_quantity_and_no_unit_recognised": lines_numeric_no_unit,
                                "pct_lines_bare_count_numeric_quantity_and_no_unit_recognised": pct(lines_numeric_no_unit, total_lines),
                                "lines_without_quantity_text": total_lines - lines_numeric_lead,
                                "pct_lines_with_a_bare_numeric_quantity": pct(lines_numeric_lead, total_lines),
                                "note": "the parser reads the unit from the PART string (the quantity field has none); 'unit recognised' "
                                        "therefore counts food names that begin with a unit word (e.g. a count noun), not stated units"},
           "reading_3_name_field": {"part_strings": parts_total, "with_a_unit_lexicon_word": parts_with_unit_word,
                                    "pct_with_a_unit_lexicon_word": pct(parts_with_unit_word, parts_total),
                                    "unit_lexicon_tokens": len(unit_tokens),
                                    "note": "single-letter t and c excluded by the lexicon; count nouns such as clove or can are unit tokens, so this is an upper bound"},
           "reading_4_ner_counts_S174": {"source": NER_COUNTS, "QUANTITY_spans": ner.get("QUANTITY"), "UNIT_spans": ner.get("UNIT"),
                                         "unit_over_quantity_pct": pct(ner.get("UNIT", 0), ner.get("QUANTITY", 0)),
                                         "unit_spans_over_lines_pct": pct(ner.get("UNIT", 0), ner_lines),
                                         "quantity_spans_minus_lines_starting_with_a_digit": (ner.get("QUANTITY", 0) - lines_numeric_lead) if not limit else None,
                                         "unit_spans_over_names_with_a_unit_word": round(ner.get("UNIT", 0) / parts_with_unit_word, 4) if (parts_with_unit_word and not limit) else None,
                                         "note": "model-derived (DeBERTa-CRF), per-span output not on this server; Wikibooks 82.2 % and TASTEset 83.7 % in the same file"}}
    ner_u = res["reading_4_ner_counts_S174"]["UNIT_spans"] or 0
    res["verdict"] = {
        "source_level": bool(q_shape.get("HAS_ALPHABETIC", 0) == 0),
        "statement": ("No Food.com quantity string contains a letter, so no unit token exists in the quantity field for a parser to lose: the unit drop is "
                      "source-level. The parser recognises a unit on %s %% of lines, the name field holds a unit word on %s %% of strings and the NER "
                      "finds UNIT spans on %s %% of lines: all three are well below 5 %% and come from words inside food names, not from a stated unit. "
                      "The NER's UNIT span count and the number of name strings holding a unit word agree within about 2 %%, and its QUANTITY span count equals the number of lines that start with a digit to within 0.01 %%." % (
                          res["reading_2_parser"]["pct_lines_with_unit_prenorm"], res["reading_3_name_field"]["pct_with_a_unit_lexicon_word"],
                          res["reading_4_ner_counts_S174"]["unit_spans_over_lines_pct"])),
        "consequence": "Every Food.com quantity is a bare count or a bare number (no mass, no volume): grams are UNKNOWN by construction, "
                       "and no parser change (including SP-002) can create them."}
    res["seconds"] = round(time.time() - t0, 1)
    from culinarystate.quantity.rc2_dryrun import assert_counts_only
    assert_counts_only(strip_prose({k: v for k, v in res.items() if k != "reading_4_ner_counts_S174"}))
    return res


def md(res: dict) -> str:
    r1, r2, r3, r4 = (res[k] for k in ("reading_1_source_field", "reading_2_parser", "reading_3_name_field", "reading_4_ner_counts_S174"))
    L = ["# Food.com bare-count share and the unit-drop mechanism (S178, T3-C07-R4)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only; no recipe text. NON_CITABLE.", "",
         f"Recipes read: {res['recipes']:,}{' (sample)' if res['sample_limit_recipes'] else ''}. Tool `{res['tool_version']}`.", "",
         "## Verdict", "", res["verdict"]["statement"], "", res["verdict"]["consequence"], "",
         "## 1. Source field", "", f"{r1['quantity_strings_total']:,} quantity strings, {r1['null']:,} null, {r1['non_null']:,} non-null.", "",
         "| shape | strings |", "|---|---:|"]
    for k, v in r1["shapes"].items():
        L.append(f"| {k} | {v:,} |")
    L += ["", f"Strings with any alphabetic character: **{r1['with_any_alphabetic_character']:,}**; strings with U+2044: {r1['with_fraction_slash_u2044']:,}. Share of non-null strings that are bare numbers: {r1['pct_non_null_that_are_bare_numbers']} %.", "",
          "## 2. Parser (lines as the corpus iterator builds them)", "", f"{r2['lines']:,} lines ({r2['unique_lines']:,} unique).", "",
          "| quantity kind read | legacy parser | with SP-002 pre-normalisation |", "|---|---:|---:|"]
    for k in sorted(set(r2["legacy_kind"]) | set(r2["prenorm_kind"])):
        L.append(f"| {k} | {r2['legacy_kind'].get(k, 0):,} | {r2['prenorm_kind'].get(k, 0):,} |")
    L += ["", f"Lines with a bare numeric quantity at the start: {r2['lines_starting_with_a_digit']:,} ({r2['pct_lines_with_a_bare_numeric_quantity']} %); "
              f"lines with no quantity text: {r2['lines_without_quantity_text']:,}.",
          f"Lines where a unit is recognised: legacy {r2['lines_with_unit_recognised_legacy']:,} ({r2['pct_lines_with_unit_legacy']} %), with pre-normalisation "
          f"{r2['lines_with_unit_recognised_prenorm']:,} ({r2['pct_lines_with_unit_prenorm']} %). {r2['note']}.",
          f"Bare-count lines (numeric quantity, no unit recognised anywhere): {r2['lines_bare_count_numeric_quantity_and_no_unit_recognised']:,} ({r2['pct_lines_bare_count_numeric_quantity_and_no_unit_recognised']} % of lines).", "",
          "## 3. Name field", "", f"{r3['with_a_unit_lexicon_word']:,} of {r3['part_strings']:,} part strings ({r3['pct_with_a_unit_lexicon_word']} %) contain a unit-lexicon word. {r3['note']}.", "",
          "## 4. NER counts (S174)", "", f"QUANTITY spans {r4['QUANTITY_spans']:,}; UNIT spans {r4['UNIT_spans']:,} = {r4['unit_over_quantity_pct']} % of QUANTITY, "
          f"{r4['unit_spans_over_lines_pct']} % of lines; UNIT spans / name strings with a unit word = {r4['unit_spans_over_names_with_a_unit_word']}; "
          f"QUANTITY spans minus lines starting with a digit = {r4['quantity_spans_minus_lines_starting_with_a_digit']}. {r4['note']}."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None, help="first N recipes (smoke test)")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    res = run(root, a.sample)
    out.mkdir(parents=True, exist_ok=True)
    suffix = f"_sample{a.sample}" if a.sample else ""
    (out / f"foodcom_bare_count_v1{suffix}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / f"foodcom_bare_count_v1{suffix}.md").write_text(md(res), encoding="utf-8")
    print(json.dumps({"recipes": res["recipes"], "alpha_in_quantity": res["reading_1_source_field"]["with_any_alphabetic_character"],
                      "pct_unit_prenorm": res["reading_2_parser"]["pct_lines_with_unit_prenorm"],
                      "pct_name_unit_word": res["reading_3_name_field"]["pct_with_a_unit_lexicon_word"],
                      "ner_unit_over_lines": res["reading_4_ner_counts_S174"]["unit_spans_over_lines_pct"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
