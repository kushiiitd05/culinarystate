#!/usr/bin/env python3
"""Scan all locally indexed recipe text against draft artifacts, with bounded memory.

Only hashes, counts and source IDs leave memory. No release clearance is granted.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from itertools import chain
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Visible(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def visible_html(text):
    parser = Visible()
    parser.feed(text)
    return " ".join(parser.parts)


def tokens(text):
    return re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold())


def artifact_index(artifacts, *, window):
    if window < 1:
        raise ValueError("positive window required")
    index = defaultdict(lambda: defaultdict(set))
    for path, text in artifacts.items():
        words = tokens(text)
        for i in range(len(words) - window + 1):
            part = tuple(words[i:i + window])
            index[part[0]][part].add(path)
    return index


def match_text(text, index, *, window):
    words, found = tokens(text), set()
    for i in range(len(words) - window + 1):
        if words[i] not in index:
            continue
        part = tuple(words[i:i + window])
        for path in index[words[i]].get(part, ()):
            found.add((path, hashlib.sha256(" ".join(part).encode()).hexdigest()))
    return found


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, action="append", required=True)
    parser.add_argument("--source-text", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--window", type=int, default=12)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("refusing to overwrite")
    artifacts = {str(p): visible_html(p.read_text()) if p.suffix == ".html" else p.read_text() for p in args.artifact}
    index = artifact_index(artifacts, window=args.window)
    from culinarystate.recipes import corpus
    counts, missing, hits = Counter(), Counter(), []
    started = datetime.now(timezone.utc).isoformat()
    source_paths = [corpus.A1_DIR / "recipes_processed.jsonl", corpus.ROOT / "data/interim/wikibooks/recipes.jsonl",
                    corpus.ROOT / "data/interim/gutenberg/recipes.jsonl", corpus.FOODCOM, corpus.TASTESET,
                    corpus.ROOT / "ledgers/data/REC.jsonl"] + args.source_text
    inputs = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in source_paths}
    recipes = chain(corpus.iter_rec_corpora(), corpus.iter_foodcom(), corpus.iter_tasteset())
    for recipe in recipes:
        family = recipe["source_family"]
        counts[family] += 1
        missing[family] += bool((recipe.get("extra") or {}).get("raw_segment_missing"))
        texts = [recipe.get("title") or "", *recipe.get("ingredient_lines", []), *recipe.get("steps", [])]
        found = set()
        for text in texts:
            found.update(match_text(text, index, window=args.window))
        for artifact, digest in sorted(found):
            hits.append({"artifact": artifact, "source_family": family, "source_id": recipe["recipe_id"], "window_sha256": digest})
        if sum(counts.values()) % 100000 == 0:
            print(f"Scanned {sum(counts.values())} recipes", flush=True)
    for source in args.source_text:
        for artifact, digest in sorted(match_text(source.read_text(), index, window=args.window)):
            hits.append({"artifact": artifact, "source_family": "SUPPLIED_TEXT", "source_id": source.name, "window_sha256": digest})
    report = {"record": "LOCAL_INDEXED_CORPUS_DRAFT_TEXT_SCAN", "started_at_utc": started,
              "completed_at_utc": datetime.now(timezone.utc).isoformat(), "window_words": args.window,
              "normalization": "NFKC_CASEFOLD_UNICODE_WORDS_PER_SOURCE_FIELD", "recipes_by_family": dict(counts),
              "missing_raw_segments_by_family": dict(missing), "matched_windows": len(hits), "findings": hits,
              "input_sha256": inputs, "artifact_sha256": {str(p): sha(p) for p in args.artifact},
              "tool_sha256": sha(__file__), "release_clearance": False,
              "labels": ["NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"],
              "limitations": ["Local indexed corpus adapter fields and supplied text only; no unindexed/unavailable sources.",
                              "PDF raster appearance, images, OCR, paraphrases and shorter excerpts are not scanned.",
                              "Per-field windows do not detect quotations concatenated across separate source fields.",
                              "Shared generic wording can match; a match is a review queue, not a licence judgement.",
                              "Artifacts are drafts; final edits need a new scan. No release clearance."]}
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"recipes": dict(counts), "matches": len(hits)}))


if __name__ == "__main__":
    main()
