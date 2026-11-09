#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C23-R1: the one-page Food.com data card (licence, units, quantity/part misalignment, SP-002), generated from the
committed machine-readable reports so every number has a path. Counts only; no recipe text.

Inputs (all read-only, all must exist):
  data/external/foodcom/PROVENANCE.json                      source, licence declaration, file sha256
  reports/s178/corpus/foodcom_bare_count_v1.json             units: source field vs parser vs name field vs NER
  reports/s178/corpus/foodcom_quantity_alignment_v1.json     misalignment diagnostic and proposed pairing rule
  reports/s178/corpus/sp002_prenorm_rerun_v1.json            U+2044 lines and the rc2 before/after
  reports/s178/corpus/verb_coverage_census_v1.json           instruction text / Rung A verb coverage
  reports/s178/analysis/ing_alias_coverage_census_v1.json    ING / ALIAS coverage of the ingredient names
  reports/s177/line_mass_census_FOODCOM_manjot.json          lines with grams

Output: reports/s178/corpus/foodcom_data_card_v1.md (+ .json holding the numbers and their source paths).
  python tools/s178_corpus_foodcom_card.py
AI_DRAFTED / PROPOSED. Licence wording is the uploader's declaration, not a legal finding; the human licence review (H2) stays open.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_VERSION = "s178-corpus-foodcom-card-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
SRC = {
    "provenance": "data/external/foodcom/PROVENANCE.json",
    "bare": "reports/s178/corpus/foodcom_bare_count_v1.json",
    "align": "reports/s178/corpus/foodcom_quantity_alignment_v1.json",
    "sp002": "reports/s178/corpus/sp002_prenorm_rerun_v1.json",
    "verbs": "reports/s178/corpus/verb_coverage_census_v1.json",
    "ing": "reports/s178/analysis/ing_alias_coverage_census_v1.json",
    "grams": "reports/s177/line_mass_census_FOODCOM_manjot.json",
}


def load(root: Path) -> dict:
    out = {}
    for k, p in SRC.items():
        out[k] = json.loads((root / p).read_text(encoding="utf-8"))
    return out


def n(x) -> str:
    return f"{x:,}"


def build(root: Path) -> dict:
    d = load(root)
    pv, b, a, s, v, i, g = (d[k] for k in ("provenance", "bare", "align", "sp002", "verbs", "ing", "grams"))
    r1, r2, r3 = b["reading_1_source_field"], b["reading_2_parser"], b["reading_3_name_field"]
    ad = a["diagnostic"]
    sf = s["families"]["FOODCOM"]
    vf = v["families"]["FOODCOM"]
    ig = i["families"]["FOODCOM"]
    gf = g["families"]["FOODCOM"]
    nums = {
        "recipes": ad["recipes"], "ingredient_part_lines": ad["lines_parts_total"],
        "quantity_strings": r1["quantity_strings_total"], "quantity_strings_null": r1["null"],
        "quantity_strings_with_a_letter": r1["with_any_alphabetic_character"], "quantity_strings_with_u2044": r1["with_fraction_slash_u2044"],
        "pct_lines_bare_count_no_unit": r2["pct_lines_bare_count_numeric_quantity_and_no_unit_recognised"],
        "pct_lines_with_unit_recognised": r2["pct_lines_with_unit_prenorm"], "pct_names_with_unit_word": r3["pct_with_a_unit_lexicon_word"],
        "lines_with_grams_s177": gf["lines_with_grams"], "lines_unit_missing_in_source_s177": gf["basis"]["UNIT_MISSING_IN_SOURCE"],
        "recipes_unequal_lists": ad["recipes_unequal"], "pct_recipes_unequal_lists": ad["pct_recipes_unequal"],
        "pct_lines_in_unequal_recipes": ad["pct_lines_in_unequal_recipes"], "recipes_equal_lists": ad["recipes"] - ad["recipes_unequal"],
        "lines_paired_equal_length_rule": ad["equal_length_only_rule"]["lines_paired"], "pct_lines_paired_equal_length_rule": ad["equal_length_only_rule"]["pct_of_lines"],
        "lines_with_u2044": sf["lines_by_rule"]["SP002_U2044"], "pct_lines_with_u2044": round(100.0 * sf["lines_by_rule"]["SP002_U2044"] / sf["lines_total"], 2),
        "lines_touched_by_any_sp002_rule": sf["lines_affected_by_any_rule"],
        "lines_amount_changes_after_prenorm": sf["affected_lines_whose_normalised_amount_changes"],
        "rc2_mass_lines_before": sf["before"]["lines_with_rc2_mass"], "rc2_mass_lines_after": sf["after"]["lines_with_rc2_mass"],
        "ing_exact_pct": ig["pct_exact"], "ing_any_hit_pct": ig["pct_any_hit"], "ing_mentions": ig["mentions"], "ing_distinct_phrases": ig["types"],
        "steps_texts": vf["texts_with_steps"], "steps_sentences": vf["sentences"], "action_events": vf["action_events"],
        "verb_slot_candidates_mapped_pct": vf["pct_verb_slot_candidates_mapped"], "sentence_initial_candidates_mapped_pct": vf["pct_sentence_initial_candidates_mapped"],
        "ner_unit_spans": b["reading_4_ner_counts_S174"]["UNIT_spans"], "ner_quantity_spans": b["reading_4_ner_counts_S174"]["QUANTITY_spans"],
        "file_sha256": pv["files"]["recipes.parquet"], "kaggle_declared_licence": pv["kaggle_declared_licence"], "downloaded_utc": pv["downloaded_utc"]}
    sentences = [
        ("LICENCE", f"Food.com recipes come from the Kaggle upload `irkaal/foodcom-recipes-and-reviews` (downloaded {nums['downloaded_utc']}, recipes file sha256 `{nums['file_sha256'][:16]}`), "
                    f"which declares licence {nums['kaggle_declared_licence']}; the declaration is the uploader's, the underlying text is scraped Food.com user content, the uploader's authority to dedicate it "
                    "is NOT verified, so use is derived/analysis only with no redistribution of text until a human licence review (H2) has ruled.", SRC["provenance"]),
        ("SHAPE", f"The corpus has {n(nums['recipes'])} recipes and {n(nums['ingredient_part_lines'])} ingredient part strings; reviews were not downloaded.", SRC["align"]),
        ("NO_UNITS", f"No Food.com quantity string contains a letter ({n(nums['quantity_strings_with_a_letter'])} of {n(nums['quantity_strings'] - nums['quantity_strings_null'])} non-null strings), "
                     f"so the unit drop is in the source, not in the parser: {nums['pct_lines_bare_count_no_unit']} % of lines carry a bare count and no unit, the parser recognises a unit on only "
                     f"{nums['pct_lines_with_unit_recognised']} % of lines and {nums['pct_names_with_unit_word']} % of food-name strings contain a unit word.", SRC["bare"]),
        ("GRAMS", f"Consequently every Food.com line is `UNIT_MISSING_IN_SOURCE` ({n(nums['lines_unit_missing_in_source_s177'])} lines) and {n(nums['lines_with_grams_s177'])} lines have a gram value; "
                  "Food.com quantities may only be used as counts or presence, never as mass or volume.", SRC["grams"]),
        ("MISALIGNMENT", f"The quantity list and the ingredient-part list differ in length in {n(nums['recipes_unequal_lists'])} of {n(nums['recipes'])} recipes ({nums['pct_recipes_unequal_lists']} %), "
                         f"covering {nums['pct_lines_in_unequal_recipes']} % of lines, so positional pairing (`recipes.corpus.iter_foodcom`) puts quantities on the wrong food; the proposed rule "
                         f"pairs only equal-length recipes ({n(nums['lines_paired_equal_length_rule'])} lines, {nums['pct_lines_paired_equal_length_rule']} %) and leaves the rest UNKNOWN.", SRC["align"]),
        ("SP002", f"{n(nums['lines_with_u2044'])} lines ({nums['pct_lines_with_u2044']} %) write fractions with U+2044 FRACTION SLASH, which the frozen quantity parser reads as the digit before the slash only (a count of 1 for 1\u20444, of 3 for 3\u20444); "
                  f"the opt-in SP-002 pre-normaliser changes the normalised amount of {n(nums['lines_amount_changes_after_prenorm'])} lines and moves rc2 mass-grounded lines from "
                  f"{n(nums['rc2_mass_lines_before'])} to {n(nums['rc2_mass_lines_after'])} (Food.com has no units, so mass stays rare); every Food.com quantity figure before the fix carries this caveat.", SRC["sp002"]),
        ("NAMES", f"The ingredient names ({n(nums['ing_mentions'])} mentions, {n(nums['ing_distinct_phrases'])} distinct phrases) hit the ING/ALIAS lexicon exactly on {nums['ing_exact_pct']} % of mentions and find a lexicon "
                  f"food in {nums['ing_any_hit_pct']} %; the ING/ALIAS registries are UNVERIFIED, so a hit means the registry has the surface, not a verified identity.", SRC["ing"]),
        ("STEPS", f"The instruction text has {n(nums['steps_texts'])} texts and {n(nums['steps_sentences'])} sentences; Rung A tags {n(nums['action_events'])} ACTION events and maps "
                  f"{nums['verb_slot_candidates_mapped_pct']} % of the verb-slot words ({nums['sentence_initial_candidates_mapped_pct']} % of sentence-initial ones) to a PROC; this is a rule-based coverage count, not an accuracy.", SRC["verbs"]),
    ]
    return {"record": "FOODCOM_DATA_CARD_S178", "tool_version": TOOL_VERSION, "item": "T3-C23-R1", "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY",
            "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
            "source_files_sha256": {k: hashlib.sha256((root / p).read_bytes()).hexdigest() for k, p in SRC.items()},
            "numbers": nums, "sentences": [{"id": k, "text": t, "source": p} for k, t, p in sentences]}


def md(card: dict) -> str:
    L = ["# Food.com data card (S178, T3-C23-R1)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only; no recipe text. NON_CITABLE. One page for every T3 report that uses Food.com: copy the sentences, keep the source path.", "",
         "| id | sentence | source |", "|---|---|---|"]
    for s in card["sentences"]:
        L.append(f"| {s['id']} | {s['text']} | `{s['source']}` |")
    L += ["", "## Rules for using Food.com in a report", "",
          "1. Never print a Food.com quantity as grams or millilitres. A count or a presence flag is the strongest statement the source supports (sentences NO_UNITS, GRAMS).",
          "2. Any per-line statistic that pairs a quantity with a food (lot composition, line mass) must say which pairing rule it used; the current positional pairing is defective (MISALIGNMENT). The ingredient-name census is unaffected because it never reads the quantity.",
          "3. Quantity figures produced before the SP-002 fix carry the U+2044 caveat (SP002); the opt-in pre-normaliser is `culinarystate.quantity.prenormalize` and is not applied by default.",
          "4. Licence: derived counts and aggregates only; no Food.com text in a committed file; the licence is an uploader declaration that has not been verified (LICENCE).",
          "5. Model-derived numbers (NER spans) are labelled MODEL_DERIVED and are not gold.", "",
          f"Generated by `{card['tool_version']}` from the committed reports named in the table; source sha256 values are in the companion JSON."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    card = build(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "foodcom_data_card_v1.json").write_text(json.dumps(card, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / "foodcom_data_card_v1.md").write_text(md(card), encoding="utf-8")
    print(json.dumps({"sentences": len(card["sentences"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
