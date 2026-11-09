#!/usr/bin/env python3
"""S178 ANALYSIS lane, T3-C03-R2: ING / ALIAS coverage census of ingredient mentions, by mention-frequency decile.

Counts only. For each non-BBC family that has ingredient lines (FOODCOM, WIKIBOOKS, TASTESET) it takes the
ingredient *mention* (rule MENTION_RULE_V1 below), looks it up in the Rung A food lexicon (ING canonical names and
ALIAS surfaces; ACTIVE records only; the lexicon the Mac line-mass census uses) and reports

  EXACT_ING    the whole mention equals an ING canonical name (plural strip allowed)
  EXACT_ALIAS  the whole mention equals an ALIAS surface (and no canonical name)
  PARTIAL      a sub-span matches (longest match shorter than the mention): a lexicon hit, but not the whole phrase
  MISS         no lexicon match at all

by mention-frequency decile (two definitions), a coverage curve and the size of the unmapped queue. TASTEset also
gets a span-level census over its human-annotated gold FOOD spans. GUTENBERG_SEGMENT has no ingredient lines
(corpus iterator sets them empty; S177 finding F6), so it is reported as NOT_AVAILABLE.

NER FOOD span counts (reports/ner_v2/ner_corpus_counts_S174.json) are echoed as context only: the DeBERTa-CRF
checkpoint needs torch, which is absent from the server venv, so per-span NER output is not re-derived here.

MENTION_RULE_V1: FOODCOM mention = the ingredient *part* string (the name field; the quantity field is never
used, and the two lists are not index-aligned in 79.5 % of recipes, S176 L-LOT). WIKIBOOKS / TASTESET mention =
`quantity.grammar.parse_line(line).rest` with every (...) / [...] group removed (text after the group is kept, so
"200 ml (3/4 cup) boiling water" gives "boiling water"), cut at the first comma, semicolon or " - ", leading
"of / a / an / the" dropped. Lower-case word tokens as in `extraction.rung_a_lexicon.key_of`.

Outputs: reports/s178/analysis/ing_alias_coverage_census_v1.json (+ _tables.csv, .md written by this tool) hold
counts only. The unmapped top-N lists contain short food phrases and therefore go to data/derived/s178_analysis/
(git-ignored), with their sha256 recorded in the JSON.

Also counts lines containing U+2044 FRACTION SLASH (SP-002 verification for the negative-results register).

  python tools/s178_analysis_coverage_census.py [--sample N] [--families FOODCOM,WIKIBOOKS,TASTESET]
AI_DRAFTED / PROPOSED. MODEL_DERIVED? No: a deterministic lexicon lookup. NON_CITABLE, not a gold score.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-ing-alias-coverage-0.1.0-draft"
MENTION_RULE = "MENTION_RULE_V1"
OUT_DIR = "reports/s178/analysis"
DERIVED_DIR = "data/derived/s178_analysis"
NER_COUNTS = "reports/ner_v2/ner_corpus_counts_S174.json"
FAMILIES = ("FOODCOM", "WIKIBOOKS", "TASTESET")
S177_LINE_CENSUS = {f: f"reports/s177/line_mass_census_{f}_manjot.json" for f in FAMILIES}
CLASSES = ("EXACT_ING", "EXACT_ALIAS", "PARTIAL", "MISS")
CURVE_K = (10, 50, 100, 300, 500, 1000, 2000, 5000, 10000, 50000)
COVER_TARGETS = (50, 80, 90, 95, 99)
TOP_N = 500
_CUT = re.compile(r"[,;]| - ")
_PAREN = re.compile(r"\([^()]*\)|\[[^\[\]]*\]")
_LEAD = {"of", "a", "an", "the"}


# ----------------------------------------------------------------------------- lexicon access
class Matcher:
    """Whole-phrase and sub-span lookups over the Rung A food lexicon; keeps the ING-canonical key set apart."""

    def __init__(self, lex, ing_keys: set[tuple[str, ...]]):
        from culinarystate.extraction.rung_a_lexicon import singular_variants
        self.lex, self.ing_keys, self._sv = lex, ing_keys, singular_variants

    def _is_ing(self, words: tuple[str, ...]) -> bool:
        if words in self.ing_keys:
            return True
        return any(words[:-1] + (v,) in self.ing_keys for v in self._sv(words[-1]))

    def classify(self, words: list[str]) -> tuple[str, int, int]:
        """(class, longest_match_len, n_words). Class is one of CLASSES."""
        n = len(words)
        if n == 0:
            return "MISS", 0, 0
        if self.lex.food_at(words, 0, exact_len=n) is not None:
            return ("EXACT_ING" if self._is_ing(tuple(words)) else "EXACT_ALIAS"), n, n
        best = 0
        for i in range(n):
            m = self.lex.food_at(words, i)
            if m is not None and m.length > best:
                best = m.length
        return ("PARTIAL" if best else "MISS"), best, n

    def any_hit(self, words: list[str]) -> bool:
        return any(self.lex.food_at(words, i) is not None for i in range(len(words)))


def load_matcher(root: Path) -> tuple[Matcher, dict]:
    from culinarystate.extraction import rung_a_lexicon as L
    lex = L.load_lexicon(root, cache=False)
    ing = L._latest_active(root / "ledgers/data/ING.jsonl")
    ing_keys = {L.key_of(r["canonical_name"]) for r in ing.values() if r.get("canonical_name")}
    ing_keys.discard(())
    info = {"lexicon_fingerprint": lex.fingerprint, "ing_active": len(ing), "ing_canonical_keys": len(ing_keys),
            "food_lexicon_keys": len(lex.foods), "lexicon_sources_sha256": dict(lex.sources)}
    return Matcher(lex, ing_keys), info


# ----------------------------------------------------------------------------- mention extraction
def mention_words(line: str, family: str, tokens, parse_line) -> list[str]:
    """MENTION_RULE_V1 -> list of lower-case words."""
    if family == "FOODCOM":
        s = line
    else:
        s = parse_line(line).rest or ""
    for _ in range(3):                       # drop (...) and [...] groups, innermost first; text after them is kept
        s = _PAREN.sub(" ", s)
    s = s.replace("(", " ").replace(")", " ")
    s = _CUT.split(s, maxsplit=1)[0]
    words = [w for _, _, w in tokens(s)]
    while len(words) > 1 and words[0] in _LEAD:
        words = words[1:]
    return words


# ----------------------------------------------------------------------------- stats
def deciles_by_mass(rows: list[tuple[str, int, str]]) -> list[dict]:
    """rows sorted (-count, key): (key, count, class). Decile of a type = floor(10 * mentions_before / total)."""
    total = sum(c for _, c, _ in rows)
    acc = [Counter() for _ in range(10)]
    types = [0] * 10
    before = 0
    for _, c, cls in rows:
        d = min(9, (10 * before) // total) if total else 0
        acc[d][cls] += c
        acc[d]["_mentions"] += c
        types[d] += 1
        before += c
    out = []
    for d in range(10):
        m = acc[d]["_mentions"]
        out.append({"decile": d + 1, "types": types[d], "mentions": m,
                    **{f"mentions_{k}": acc[d][k] for k in CLASSES},
                    "pct_exact": round(100.0 * (acc[d]["EXACT_ING"] + acc[d]["EXACT_ALIAS"]) / m, 2) if m else None,
                    "pct_any_hit": round(100.0 * (m - acc[d]["MISS"]) / m, 2) if m else None})
    return out


def deciles_by_rank(rows: list[tuple[str, int, str]]) -> list[dict]:
    """Types sorted by frequency, cut into 10 equal-size groups of types (decile 1 = most frequent 10 % of types)."""
    n = len(rows)
    out = []
    for d in range(10):
        lo, hi = (n * d) // 10, (n * (d + 1)) // 10
        grp = rows[lo:hi]
        acc = Counter()
        for _, c, cls in grp:
            acc[cls] += c
            acc["_m"] += c
        m = acc["_m"]
        out.append({"decile": d + 1, "types": len(grp), "min_count": grp[-1][1] if grp else None,
                    "max_count": grp[0][1] if grp else None, "mentions": m,
                    **{f"mentions_{k}": acc[k] for k in CLASSES},
                    "pct_exact": round(100.0 * (acc["EXACT_ING"] + acc["EXACT_ALIAS"]) / m, 2) if m else None,
                    "pct_any_hit": round(100.0 * (m - acc["MISS"]) / m, 2) if m else None})
    return out


def curve(rows: list[tuple[str, int, str]]) -> dict:
    total = sum(c for _, c, _ in rows)
    nonexact_total = sum(c for _, c, k in rows if k not in ("EXACT_ING", "EXACT_ALIAS"))
    pts, cum, cum_non, nonexact_rank = [], 0, 0, 0
    ks = set(CURVE_K)
    targets = {t: None for t in COVER_TARGETS}
    nontargets = {t: None for t in COVER_TARGETS}
    for i, (_, c, cls) in enumerate(rows, 1):
        cum += c
        is_non = cls not in ("EXACT_ING", "EXACT_ALIAS")
        if is_non:
            cum_non += c
            nonexact_rank += 1
            for t in COVER_TARGETS:
                if nontargets[t] is None and nonexact_total and 100 * cum_non >= t * nonexact_total:
                    nontargets[t] = nonexact_rank
        for t in COVER_TARGETS:
            if targets[t] is None and 100 * cum >= t * total:
                targets[t] = i
        if i in ks:
            pts.append({"top_k_types": i, "pct_of_mentions": round(100.0 * cum / total, 2),
                        "pct_of_nonexact_mentions_in_top_k": round(100.0 * cum_non / nonexact_total, 2)
                        if nonexact_total else None})
    n_nonexact_types = nonexact_rank
    return {"curve": pts, "types_needed_for_pct_of_mentions": {str(k): v for k, v in targets.items()},
            "nonexact_types_needed_for_pct_of_nonexact_mentions": {str(k): v for k, v in nontargets.items()},
            "nonexact_types": n_nonexact_types, "nonexact_mentions": nonexact_total}


def family_block(counter: Counter, cls_of: dict[tuple, tuple[str, int, int]]) -> tuple[dict, list]:
    rows = sorted(((" ".join(k), c, cls_of[k][0]) for k, c in counter.items()), key=lambda r: (-r[1], r[0]))
    total = sum(c for _, c, _ in rows)
    by_cls = Counter()
    for _, c, cls in rows:
        by_cls[cls] += c
    hapax = sum(1 for _, c, _ in rows if c == 1)
    block = {"mentions": total, "types": len(rows), "hapax_types": hapax,
             "hapax_pct_of_types": round(100.0 * hapax / len(rows), 2) if rows else None,
             "mentions_by_class": {k: by_cls[k] for k in CLASSES},
             "pct_by_class": {k: round(100.0 * by_cls[k] / total, 2) if total else None for k in CLASSES},
             "pct_exact": round(100.0 * (by_cls["EXACT_ING"] + by_cls["EXACT_ALIAS"]) / total, 2) if total else None,
             "pct_any_hit": round(100.0 * (total - by_cls["MISS"]) / total, 2) if total else None,
             "types_by_class": dict(Counter(cls for _, _, cls in rows)),
             "deciles_by_mention_mass": deciles_by_mass(rows), "deciles_by_type_rank": deciles_by_rank(rows),
             **curve(rows)}
    return block, rows


# ----------------------------------------------------------------------------- corpus streams
def stream_lines(family: str, limit: int | None):
    from culinarystate.recipes import corpus
    if family == "FOODCOM":
        for rec in corpus.iter_foodcom(limit=limit):
            yield rec["ingredient_lines"], (rec["extra"]["ingredient_parts"])
    elif family == "WIKIBOOKS":
        n = 0
        for rec in corpus.iter_rec_corpora(families=("WIKIBOOKS",)):
            yield rec["ingredient_lines"], None
            n += 1
            if limit and n >= limit:
                return
    elif family == "TASTESET":
        n = 0
        for rec in corpus.iter_tasteset():
            yield rec["ingredient_lines"], None
            n += 1
            if limit and n >= limit:
                return
    else:
        raise ValueError(family)


def census_family(family: str, matcher: Matcher, limit: int | None) -> tuple[dict, list]:
    from culinarystate.extraction.rung_a_lexicon import tokens, key_of
    from culinarystate.quantity.grammar import parse_line
    raw_line = Counter()      # unique whole-line string -> count (line level, for the any-hit check)
    mention = Counter()       # unique mention string (case/space-folded) -> count
    u2044 = 0
    lines = 0
    recipes = 0
    for ing_lines, parts in stream_lines(family, limit):
        recipes += 1
        for ln in ing_lines:
            lines += 1
            if "⁄" in ln:
                u2044 += 1
        if family == "FOODCOM":
            for p in parts:
                mention[(p or "").strip().lower()] += 1
                raw_line[(p or "").strip().lower()] += 1
        else:
            for ln in ing_lines:
                raw_line[ln] += 1
                mention[ln] += 1
    cls_of: dict[tuple, tuple[str, int, int]] = {}
    counter: Counter = Counter()
    for s, c in mention.items():
        words = mention_words(s, family, tokens, parse_line)
        k = tuple(words)
        if k not in cls_of:
            cls_of[k] = matcher.classify(words)
        counter[k] += c
    counter.pop((), None)
    # line-level any-hit (S175 NO_FOOD_MENTION definition) over whole lines (FOODCOM: the part string; the quantity
    # string has no word tokens)
    no_hit = 0
    for s, c in raw_line.items():
        if not matcher.any_hit([w for _, _, w in tokens(s)]):
            no_hit += c
    block, rows = family_block(counter, cls_of)
    block.update({"status": "READ", "recipes": recipes, "ingredient_lines": lines,
                  "lines_with_u2044_fraction_slash": u2044,
                  "lines_without_any_lexicon_food_match": no_hit,
                  "pct_lines_with_any_lexicon_food_match": round(100.0 * (lines - no_hit) / lines, 2) if lines else None,
                  "partial_mean_covered_token_share": None})
    # average covered share for PARTIAL types (type-weighted by mentions)
    num = den = 0
    for k, c in counter.items():
        cl, m, n = cls_of[k]
        if cl == "PARTIAL":
            num += c * (m / n)
            den += c
    block["partial_mean_covered_token_share"] = round(num / den, 4) if den else None
    nonexact = [(r, cls_of[tuple(r[0].split())]) for r in rows if r[2] not in ("EXACT_ING", "EXACT_ALIAS")]
    unmapped = [{"rank": i + 1, "phrase": r[0], "count": r[1], "class": r[2],
                 "covered_tokens": cls_of[tuple(r[0].split())][1], "tokens": cls_of[tuple(r[0].split())][2]}
                for i, (r, _) in enumerate(nonexact[:TOP_N])]
    return block, unmapped


def tasteset_gold_spans(matcher: Matcher, limit: int | None) -> dict:
    """Span-level census over the human-annotated TASTEset FOOD spans (offsets into the recipe's ingredient text)."""
    from culinarystate.extraction.rung_a_lexicon import tokens
    path = ROOT / "data/raw/tasteset/TASTEset.csv"
    if not path.is_file():
        return {"status": "INPUT_MISSING"}
    counter: Counter = Counter()
    cls_of: dict[tuple, tuple[str, int, int]] = {}
    types_seen = Counter()
    n_rows = 0
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            n_rows += 1
            if limit and n_rows > limit:
                break
            text = r["ingredients"] or ""
            for e in json.loads(r["ingredients_entities"] or "[]"):
                types_seen[e["type"]] += 1
                if e["type"] != "FOOD":
                    continue
                words = [w for _, _, w in tokens(text[e["start"]:e["end"]])]
                if not words:
                    continue
                k = tuple(words)
                if k not in cls_of:
                    cls_of[k] = matcher.classify(words)
                counter[k] += 1
    block, _rows = family_block(counter, cls_of)
    block.update({"status": "READ", "gold_entity_types": dict(sorted(types_seen.items())), "recipes": min(n_rows, limit or n_rows),
                  "annotation": "HUMAN_GOLD_FOOD_SPANS_TASTESET (model training data overlaps; not an accuracy claim)"})
    return block


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- output
def tables_csv(res: dict) -> list[list]:
    rows = [["scope", "table", "decile_or_k", "types", "mentions", "pct_exact", "pct_any_hit", "extra"]]
    for scope, blk in res["families"].items():
        if blk.get("status") != "READ":
            continue
        for d in blk["deciles_by_mention_mass"]:
            rows.append([scope, "decile_by_mention_mass", d["decile"], d["types"], d["mentions"], d["pct_exact"], d["pct_any_hit"], ""])
        for d in blk["deciles_by_type_rank"]:
            rows.append([scope, "decile_by_type_rank", d["decile"], d["types"], d["mentions"], d["pct_exact"], d["pct_any_hit"],
                         f"count {d['min_count']}..{d['max_count']}"])
        for p in blk["curve"]:
            rows.append([scope, "coverage_curve", p["top_k_types"], "", "", p["pct_of_mentions"], "",
                         f"nonexact_share_in_top_k {p['pct_of_nonexact_mentions_in_top_k']}"])
    return rows


def md(res: dict) -> str:
    L = ["# ING / ALIAS coverage census (S178, T3-C03-R2)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only, no recipe text. NON_CITABLE. Deterministic lexicon lookup, not a model and not a gold score.",
         f"Tool `{TOOL_VERSION}`; rule {MENTION_RULE}; lexicon fingerprint `{res['lexicon']['lexicon_fingerprint'][:16]}`.", "",
         "A mention is an ingredient phrase (rule above). EXACT = the whole phrase is an ING canonical name or an ALIAS surface. PARTIAL = only a sub-span is, so the lexicon finds *a* food in the phrase but the phrase itself is not a concept. MISS = nothing matches.", "",
         "## Headline", "",
         "| family | mentions | distinct phrases | EXACT (ING+ALIAS) | PARTIAL | MISS | any lexicon hit | lines with no lexicon food match |",
         "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for f, b in res["families"].items():
        if b.get("status") != "READ":
            L.append(f"| {f} | NOT_AVAILABLE | | | | | | {b.get('reason', '')} |")
            continue
        p = b["pct_by_class"]
        nl = b.get("lines_without_any_lexicon_food_match")
        lcell = "n/a (span level)" if nl is None else f"{nl:,} ({100 - (b.get('pct_lines_with_any_lexicon_food_match') or 0):.2f} %)"
        L.append(f"| {f} | {b['mentions']:,} | {b['types']:,} | {b['pct_exact']} % | {p['PARTIAL']} % | {p['MISS']} % | {b['pct_any_hit']} % | {lcell} |")
    for f, b in res["families"].items():
        if b.get("status") != "READ":
            continue
        L += ["", f"## {f}", "",
              f"{b['mentions']:,} mentions, {b['types']:,} distinct phrases, {b['hapax_types']:,} seen once ({b['hapax_pct_of_types']} % of phrases).", "",
              "Decile by mention mass (decile 1 = the most frequent phrases that together hold the first 10 % of mentions):", "",
              "| decile | phrases | mentions | EXACT % | any hit % |", "|---:|---:|---:|---:|---:|"]
        for d in b["deciles_by_mention_mass"]:
            L.append(f"| {d['decile']} | {d['types']:,} | {d['mentions']:,} | {d['pct_exact']} | {d['pct_any_hit']} |")
        L += ["", "Decile by phrase rank (decile 1 = the most frequent 10 % of distinct phrases):", "",
              "| decile | phrases | count range | mentions | EXACT % | any hit % |", "|---:|---:|---|---:|---:|---:|"]
        for d in b["deciles_by_type_rank"]:
            L.append(f"| {d['decile']} | {d['types']:,} | {d['min_count']}..{d['max_count']} | {d['mentions']:,} | {d['pct_exact']} | {d['pct_any_hit']} |")
        L += ["", "Coverage curve (top-k most frequent phrases):", "", "| k | % of all mentions | % of non-EXACT mentions inside top-k |", "|---:|---:|---:|"]
        for p in b["curve"]:
            L.append(f"| {p['top_k_types']:,} | {p['pct_of_mentions']} | {p['pct_of_nonexact_mentions_in_top_k']} |")
        L += ["", f"Phrases needed to hold X % of mentions: {b['types_needed_for_pct_of_mentions']}. "
                  f"Non-EXACT phrases needed to hold X % of the non-EXACT mentions: {b['nonexact_types_needed_for_pct_of_nonexact_mentions']} "
                  f"(of {b['nonexact_types']:,} non-EXACT phrases)."]
    L += ["", "## Notes", ""] + [f"- {n}" for n in res["notes"]]
    return "\n".join(L) + "\n"


def run(root: Path, families, limit: int | None, out_dir: Path, derived: Path) -> dict:
    matcher, info = load_matcher(root)
    res = {"record": "ING_ALIAS_COVERAGE_CENSUS_S178", "tool_version": TOOL_VERSION, "mention_rule": MENTION_RULE,
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "citable": False, "contains_text": False, "contains_ids": False,
           "counts_as_human_gate": False, "sample_limit_recipes": limit, "lexicon": info, "families": {}, "unmapped_lists": {}}
    derived.mkdir(parents=True, exist_ok=True)
    for fam in families:
        blk, unmapped = census_family(fam, matcher, limit)
        res["families"][fam] = blk
        p = derived / f"unmapped_top{TOP_N}_{fam}{'_sample' if limit else ''}.csv"
        with open(p, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["rank", "phrase", "count", "class", "covered_tokens", "tokens"])
            for u in unmapped:
                w.writerow([u["rank"], u["phrase"], u["count"], u["class"], u["covered_tokens"], u["tokens"]])
        res["unmapped_lists"][fam] = {"path": str(p.relative_to(root)) if p.is_relative_to(root) else str(p), "rows": len(unmapped),
                                      "sha256": sha256_file(p), "git_ignored": True,
                                      "note": "short food phrases with counts; kept out of the committed tree (law 6)"}
    res["families"]["GUTENBERG_SEGMENT"] = {"status": "NOT_AVAILABLE",
                                            "reason": "0 ingredient lines (corpus iterator sets them empty, S177 F6); NER FOOD spans not persisted"}
    if "TASTESET" in families:
        res["tasteset_gold_food_spans"] = tasteset_gold_spans(matcher, limit)
        res["families"]["TASTESET_GOLD_FOOD_SPANS"] = res["tasteset_gold_food_spans"]
    ner = json.loads((root / NER_COUNTS).read_text(encoding="utf-8"))
    res["ner_context"] = {"source": NER_COUNTS, "source_sha256": sha256_file(root / NER_COUNTS), "status": ner.get("status"),
                          "families": {f: {"lines": ner["families"][f]["lines"], "lines_with_FOOD": ner["families"][f]["lines_with_FOOD"],
                                           "FOOD_spans": ner["families"][f]["labels"]["FOOD"]} for f in ner["families"]},
                          "note": "model-derived span counts (DeBERTa-CRF, TASTEset DEV F1 0.940 reported by the checkpoint file); "
                                  "per-span outputs not stored, torch absent here, so no per-span ING/ALIAS hit rate for FOODCOM / WIKIBOOKS"}
    # reconciliation with the S177 Mac-tool line census: NO_FOOD_MENTION lines
    rec = {}
    for fam in families:
        p = root / S177_LINE_CENSUS[fam]
        if p.is_file() and not limit:
            d = json.loads(p.read_text(encoding="utf-8"))["families"][fam]
            ref = d["match_status"].get("NO_FOOD_MENTION", 0)
            mine = res["families"][fam]["lines_without_any_lexicon_food_match"]
            rec[fam] = {"s177_no_food_mention_lines": ref, "this_tool_no_lexicon_match_lines": mine, "delta": mine - ref,
                        "source": S177_LINE_CENSUS[fam],
                        "lines_equal": d["lines"] == res["families"][fam]["ingredient_lines"],
                        "note": "the S175 tool takes ING names from every ING line (any status); this tool uses ACTIVE records only"}
    res["reconciliation_with_s177_line_census"] = rec
    res["notes"] = [
        "EXACT is the strict reading of 'hits ING/ALIAS'; PARTIAL + EXACT is the Rung A reading (a food is found in the phrase, which is what the S175/S177 line census calls a food mention).",
        "Phrase-level EXACT is conservative: modifiers (fresh, large, chopped, brand words) keep a phrase from matching even when its head noun is a known concept; the PARTIAL class holds those.",
        "FOODCOM mentions come from the name field only. No quantity is used, so the 79.5 % quantity/part misalignment does not affect this census.",
        "WIKIBOOKS / TASTESET mentions pass through the legacy quantity grammar, which mis-reads U+2044 (SP-002); the affected lines lose their quantity but their food phrase is unaffected, because the quantity is cut before the lexicon lookup.",
        "ING / ALIAS are UNVERIFIED registries (AI-drafted); a hit means 'the registry has this surface', not 'the identity is verified'.",
        "The top-500 non-EXACT lists are written under data/derived/s178_analysis/ (git-ignored). The committed files hold counts only."]
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_sample" if limit else ""
    (out_dir / f"ing_alias_coverage_census_v1{suffix}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    with open(out_dir / f"ing_alias_coverage_census_v1_tables{suffix}.csv", "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(tables_csv(res))
    (out_dir / f"ing_alias_coverage_census_v1{suffix}.md").write_text(md(res), encoding="utf-8")
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--sample", type=int, default=None, help="first N recipes per family (smoke test; writes *_sample files)")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=str(ROOT / OUT_DIR))
    ap.add_argument("--derived-dir", default=str(ROOT / DERIVED_DIR))
    a = ap.parse_args(argv)
    res = run(Path(a.root), [f for f in a.families.split(",") if f], a.sample, Path(a.out_dir), Path(a.derived_dir))
    print(json.dumps({f: {k: b.get(k) for k in ("mentions", "types", "pct_exact", "pct_any_hit")} for f, b in res["families"].items()
                      if b.get("status") == "READ"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
