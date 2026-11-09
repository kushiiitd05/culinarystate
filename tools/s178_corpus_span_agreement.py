#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C09-R1 (PARTIAL, proxy): span agreement between the Rung A food lexicon and the human TASTEset FOOD spans. DIAGNOSTIC, not gold.

T3-C09-R1 asks for NER-vs-Rung A mention agreement. The NER span files (Food.com, Wikibooks) are on the other server and Gutenberg spans were never
persisted (BLOCKED_DATA, S177 F6), so this tool does the part that CAN be done here: Rung A's lexicon food spans against the human-annotated FOOD spans of
TASTEset (the only family with per-span reference labels on this server). It is NOT an NER evaluation and NOT a Rung A accuracy: the lexicon is matched with
no blocking, no ACTION precedence and no noun/verb disambiguation, and TASTEset was also used to train the NER checkpoint.

Counts (per gold FOOD span and per lexicon span, character overlap):
  gold FOOD spans: exact boundary match / contained in a lexicon span / contains a lexicon span / partial overlap / no overlap (missed)
  lexicon spans: overlapping a gold FOOD span / overlapping only a gold span of another type (by type) / overlapping no gold span (extra)
Top missed gold foods and top extra lexicon spans (phrases, by frequency) go to data/derived/s178_corpus/ (git-ignored, law 6); the committed JSON is counts only.

  python tools/s178_corpus_span_agreement.py [--limit N]
AI_DRAFTED / PROPOSED. NON_CITABLE.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-span-agreement-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
DERIVED_DIR = "data/derived/s178_corpus"
TASTESET = "data/raw/tasteset/TASTEset.csv"
TOP_N = 200


def lexicon_spans(lex, text: str, tokens) -> list[tuple[int, int]]:
    """Greedy longest-match food spans over the whole text (the tagging loop of Rung A, without blocking or ACTION precedence)."""
    toks = tokens(text)
    words = [w for _, _, w in toks]
    out, i = [], 0
    while i < len(toks):
        m = lex.food_at(words, i)
        if m is None:
            i += 1
            continue
        out.append((toks[i][0], toks[i + m.length - 1][1]))
        i += m.length
    return out


def overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def compare(gold: list[tuple[int, int, str]], lex: list[tuple[int, int]], c: Counter, missed: Counter, extra: Counter, text: str) -> None:
    food = [(s, e) for s, e, t in gold if t == "FOOD"]
    for g in food:
        c["gold_food_spans"] += 1
        hits = [x for x in lex if overlap(g, x)]
        if not hits:
            c["gold_food_missed_no_overlap"] += 1
            missed[text[g[0]:g[1]].strip().lower()] += 1
        elif g in hits:
            c["gold_food_exact_boundary"] += 1
        elif any(x[0] <= g[0] and g[1] <= x[1] for x in hits):
            c["gold_food_inside_a_longer_lexicon_span"] += 1
        elif any(g[0] <= x[0] and x[1] <= g[1] for x in hits):
            c["gold_food_contains_shorter_lexicon_span"] += 1
        else:
            c["gold_food_partial_overlap"] += 1
    for x in lex:
        c["lexicon_spans"] += 1
        over_food = any(overlap(x, g) for g in food)
        if over_food:
            c["lexicon_overlapping_gold_food"] += 1
            c["lexicon_exact_boundary_gold_food"] += x in food
            continue
        other = Counter(t for s, e, t in gold if t != "FOOD" and overlap(x, (s, e)))
        if other:
            c[f"lexicon_overlapping_only_gold_{other.most_common(1)[0][0]}"] += 1
        else:
            c["lexicon_extra_no_gold_span"] += 1
            extra[text[x[0]:x[1]].strip().lower()] += 1


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def run(root: Path, limit: int | None, derived: Path) -> dict:
    from culinarystate.extraction.rung_a_lexicon import load_lexicon, tokens
    lex = load_lexicon(root, cache=False)
    c, missed, extra = Counter(), Counter(), Counter()
    types = Counter()
    n = 0
    with open(root / TASTESET, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            n += 1
            if limit and n > limit:
                break
            text = r["ingredients"] or ""
            gold = [(e["start"], e["end"], e["type"]) for e in json.loads(r["ingredients_entities"] or "[]")]
            types.update(t for _, _, t in gold)
            compare(gold, lexicon_spans(lex, text, tokens), c, missed, extra, text)
    g, x = c["gold_food_spans"], c["lexicon_spans"]
    covered = g - c["gold_food_missed_no_overlap"]
    derived.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, ctr in (("missed_gold_foods", missed), ("extra_lexicon_spans", extra)):
        p = derived / f"span_agreement_{name}_TASTESET{'_sample' if limit else ''}.csv"
        with open(p, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["rank", "phrase", "count"])
            for i, (k, v) in enumerate(sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_N], 1):
                w.writerow([i, k, v])
        files[name] = {"path": str(p.relative_to(root)) if p.is_relative_to(root) else str(p), "rows": min(len(ctr), TOP_N), "distinct_phrases": len(ctr),
                       "git_ignored": True, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    return {"record": "SPAN_AGREEMENT_TASTESET_S178", "tool_version": TOOL_VERSION, "item": "T3-C09-R1 (PARTIAL proxy)", "label": "DIAGNOSTIC_NOT_GOLD",
            "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
            "ner_vs_rung_a": "BLOCKED_DATA", "reference": "HUMAN_GOLD_FOOD_SPANS_TASTESET_NOT_NER_OUTPUT", "lexicon_fingerprint": lex.fingerprint,
            "sample_limit_recipes": limit, "recipes": min(n, limit or n), "gold_entity_types": dict(sorted(types.items())), "counts": dict(sorted(c.items())),
            "rates_pct": {"gold_food_covered_by_a_lexicon_span": pct(covered, g), "gold_food_exact_boundary": pct(c["gold_food_exact_boundary"], g),
                          "gold_food_missed": pct(c["gold_food_missed_no_overlap"], g),
                          "lexicon_spans_overlapping_gold_food": pct(c["lexicon_overlapping_gold_food"], x),
                          "lexicon_spans_exact_boundary_gold_food": pct(c["lexicon_exact_boundary_gold_food"], x),
                          "lexicon_spans_extra_no_gold_span": pct(c["lexicon_extra_no_gold_span"], x)},
            "derived_lists": files,
            "notes": ["Boundary rate is strict: modifiers (fresh, chopped) make the gold span longer or shorter than the lexicon span; the overlap rates are the fairer reading.",
                      "TASTEset text was used to train the NER checkpoint, so this is not an out-of-domain measure for NER; for Rung A (a lexicon) it is.",
                      "The lexicon is the ACTIVE ING + ALIAS surface set: a missed gold food is a surface the registry lacks (or a spelling variant), not an extraction error of a model."]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--derived-dir", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    res = run(root, a.limit, Path(a.derived_dir) if a.derived_dir else root / DERIVED_DIR)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"span_agreement_tasteset_v1{'_sample' if a.limit else ''}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(res["rates_pct"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
