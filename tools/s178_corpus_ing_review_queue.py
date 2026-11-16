#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C03-R3 (agent part): build the mention-weighted human review queue of non-exact ingredient phrases.

Reuses the mention rule and lexicon matcher of `tools/s178_analysis_coverage_census.py` (MENTION_RULE_V1, Rung A food lexicon: ACTIVE ING
canonical names + ALIAS surfaces). For each family with ingredient lines (FOODCOM, WIKIBOOKS, TASTESET) every distinct mention phrase whose
class is not EXACT (PARTIAL or MISS) becomes a queue row, ranked by mention count, with:

  cum_share_pct       cumulative share of the family's non-exact mentions
  band                A = rows up to 80 % of non-exact mentions, B = up to 95 %, C = the tail (default confidence LOW_CONFIDENCE_UNREVIEWED)
  candidate_ing_ids   up to 3 ING ids of the LONGEST lexicon sub-span match (AI suggestion from the registry, not a decision)
  n_candidate_ids     size of that id set (> 1 = the matched surface is polysemous in the lexicon)
  covered/tokens      words matched by the sub-span / words in the phrase (the rest is modifier or unknown text)
  reviewer_id, verdict, note   EMPTY: for the human reviewers (T3-C03-R3 human part: verified / rejected labels, reviewer ids)

The CSVs hold ingredient names (short phrases) and so live under data/derived/s178_corpus/ (git-ignored, law 6). The committed summary
`reports/s178/corpus/ing_review_queue_summary_v1.json` holds counts only. Nothing here is a label; a suggestion is never verified.

  python tools/s178_corpus_ing_review_queue.py [--sample N]
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
sys.path.insert(0, str(ROOT / "tools"))

TOOL_VERSION = "s178-corpus-ing-review-queue-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
DERIVED_DIR = "data/derived/s178_corpus"
FAMILIES = ("FOODCOM", "WIKIBOOKS", "TASTESET")
BAND_A, BAND_B = 80.0, 95.0
TARGETS = (50, 80, 90, 95, 99)
FIELDS = ["rank", "phrase", "count", "class", "tokens", "covered_tokens", "n_candidate_ids", "candidate_ing_ids", "cum_share_pct", "band",
          "default_confidence", "reviewer_id", "verdict", "note"]


def longest_submatch(matcher, words: list[str]):
    """(covered tokens, sorted candidate ids) of the longest lexicon match inside the phrase (the first one on a tie)."""
    best, ids = 0, frozenset()
    for i in range(len(words)):
        m = matcher.lex.food_at(words, i)
        if m is not None and m.length > best:
            best, ids = m.length, m.ids
    return best, sorted(ids)


def build_rows(counter: Counter, cls_of: dict, matcher) -> list[dict]:
    nonexact = [(k, c) for k, c in counter.items() if cls_of[k][0] not in ("EXACT_ING", "EXACT_ALIAS")]
    nonexact.sort(key=lambda kv: (-kv[1], " ".join(kv[0])))
    total = sum(c for _, c in nonexact)
    rows, cum = [], 0
    for rank, (k, c) in enumerate(nonexact, 1):
        cum += c
        cl, covered, ntok = cls_of[k]
        _cov, ids = longest_submatch(matcher, list(k)) if cl == "PARTIAL" else (0, [])
        share = 100.0 * cum / total if total else 0.0
        band = "A" if 100.0 * (cum - c) / total < BAND_A else ("B" if 100.0 * (cum - c) / total < BAND_B else "C")
        rows.append({"rank": rank, "phrase": " ".join(k), "count": c, "class": cl, "tokens": ntok, "covered_tokens": covered,
                     "n_candidate_ids": len(ids), "candidate_ing_ids": "|".join(ids[:3]), "cum_share_pct": round(share, 3), "band": band,
                     "default_confidence": "REVIEW_QUEUE" if band != "C" else "LOW_CONFIDENCE_UNREVIEWED", "reviewer_id": "", "verdict": "", "note": ""})
    return rows


def summarise(rows: list[dict], family_mentions: int) -> dict:
    total = sum(r["count"] for r in rows)
    need = {}
    cum = 0
    for i, r in enumerate(rows, 1):
        cum += r["count"]
        for t in TARGETS:
            if t not in need and 100 * cum >= t * total:
                need[t] = i
    by_band = Counter()
    mention_by_band = Counter()
    for r in rows:
        by_band[r["band"]] += 1
        mention_by_band[r["band"]] += r["count"]
    partial = [r for r in rows if r["class"] == "PARTIAL"]
    return {"nonexact_phrases": len(rows), "nonexact_mentions": total,
            "pct_of_all_mentions_nonexact": round(100.0 * total / family_mentions, 3) if family_mentions else None,
            "phrases_for_pct_of_nonexact_mentions": {f"P{t}": need.get(t) for t in TARGETS},
            "rows_by_band": dict(sorted(by_band.items())), "mentions_by_band": dict(sorted(mention_by_band.items())),
            "partial_phrases": len(partial), "miss_phrases": len(rows) - len(partial),
            "partial_with_one_candidate_id": sum(1 for r in partial if r["n_candidate_ids"] == 1),
            "partial_polysemous_more_than_one_candidate_id": sum(1 for r in partial if r["n_candidate_ids"] > 1),
            "partial_with_covered_tokens_equal_tokens_minus_one": sum(1 for r in partial if r["tokens"] - r["covered_tokens"] == 1),
            "mentions_in_phrases_seen_once": sum(r["count"] for r in rows if r["count"] == 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--derived-dir", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    derived = Path(a.derived_dir) if a.derived_dir else root / DERIVED_DIR
    import s178_analysis_coverage_census as C
    from culinarystate.extraction.rung_a_lexicon import tokens
    from culinarystate.quantity.grammar import parse_line
    matcher, info = C.load_matcher(root)
    derived.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    res = {"record": "ING_REVIEW_QUEUE_SUMMARY_S178", "tool_version": TOOL_VERSION, "item": "T3-C03-R3 (agent part)", "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY",
           "contains_text": False, "contains_ids": False, "counts_as_human_gate": False, "mention_rule": C.MENTION_RULE,
           "lexicon_fingerprint": info["lexicon_fingerprint"], "sample_limit_recipes": a.sample,
           "band_rule": {"A_up_to_pct_of_nonexact_mentions": BAND_A, "B_up_to_pct": BAND_B, "C": "tail, default confidence LOW_CONFIDENCE_UNREVIEWED"},
           "human_part": "OPEN: verified / rejected labels with reviewer ids (Kush + Parv, 6-10 h UNVERIFIED estimate); the CSV columns reviewer_id, verdict, note are empty",
           "files": {}, "families": {}}
    for fam in [f for f in a.families.split(",") if f]:
        mention, n_lines = Counter(), 0
        for ing_lines, parts in C.stream_lines(fam, a.sample):
            if fam == "FOODCOM":
                for p in parts:
                    mention[(p or "").strip().lower()] += 1
            else:
                for ln in ing_lines:
                    mention[ln] += 1
        cls_of: dict = {}
        counter: Counter = Counter()
        for s, c in mention.items():
            words = C.mention_words(s, fam, tokens, parse_line)
            k = tuple(words)
            if k not in cls_of:
                cls_of[k] = matcher.classify(words)
            counter[k] += c
        counter.pop((), None)
        rows = build_rows(counter, cls_of, matcher)
        suffix = f"_sample{a.sample}" if a.sample else ""
        path = derived / f"ing_review_queue_{fam}_v1{suffix}.csv"
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        res["files"][fam] = {"path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path), "rows": len(rows), "git_ignored": True,
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        res["families"][fam] = {"mentions": sum(counter.values()), "distinct_phrases": len(counter), **summarise(rows, sum(counter.values()))}
    (out / f"ing_review_queue_summary_v1{'_sample' + str(a.sample) if a.sample else ''}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({f: {k: b[k] for k in ("nonexact_phrases", "phrases_for_pct_of_nonexact_mentions")} for f, b in res["families"].items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
