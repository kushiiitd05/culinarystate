#!/usr/bin/env python
"""J4: stratified sample of V2 INVERTED_INTERVAL cases for human reading (S166; review block J4; D-059). DRAFT.

    python tools/j4_inverted_interval_sample.py --seed 20261104 --workers 32 \
        --out-manifest reports/step17/j4_inverted_interval_sample_manifest.csv \
        --out-private data/interim/j4_inverted_interval/j4_sample_private.csv

Scans every recipe's joined steps with Rung A + V2 (parallel workers), keeps the agreed strata (every case in the
seeded 1,000 sample, all A1 and Wikibooks, 30 Food.com, 30 Gutenberg; P1 manifest recipes excluded) and writes:
a tracked, text-free manifest (hashed recipe id, family, stratum, shape) and a PRIVATE csv with excerpts and empty
reader columns. Refuses a private path that git would track, and refuses to overwrite either file.
"""
from __future__ import annotations

import argparse
import csv
import heapq
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from multiprocessing import get_context
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.extraction import j4_inverted_sample as J  # noqa: E402
from culinarystate.extraction.rung_a_measure import rank  # noqa: E402
from culinarystate.recipes.ledgers import LOCALE  # noqa: E402

_spec = importlib.util.spec_from_file_location("_t17", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
FAMILIES = ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM")
P1_MANIFEST = ROOT / "registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv"
READER_COLS = ("verdict_parv", "verdict_kush", "note")  # codes: MIXED_NUMBER_MISREAD, TRUE_INVERTED_RANGE, OTHER, UNSURE


def _tracked_by_git(path: Path) -> bool:
    p = path.resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(p)]).returncode != 0


def _items(records, seed, top):
    for rec in records:
        rid = rec.get("recipe_id")
        if not isinstance(rid, str) or not rid:
            continue
        key = int(rank(seed, rid), 16)  # same ranking as Step 17b's seeded_sample (all records, steps or not)
        if len(top) < 1000:
            heapq.heappush(top, (-key, rid))
        elif -top[0][0] > key:
            heapq.heapreplace(top, (-key, rid))
        steps = [s for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]
        if not steps:
            continue
        yield rid, rec.get("source_family"), LOCALE.get(rec.get("source_family")), "\n".join(steps)


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out-manifest", required=True, type=Path)
    ap.add_argument("--out-private", required=True, type=Path)
    ap.add_argument("--exclude-manifest", default=str(P1_MANIFEST), help="csv with recipe_id to exclude ('' = none)")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    if _tracked_by_git(a.out_private):
        ap.error("the private excerpt file must be git-ignored or outside the repository")
    for p in (a.out_manifest, a.out_private):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    excluded = ({r["recipe_id"] for r in csv.DictReader(open(a.exclude_manifest, encoding="utf-8"))}
                if a.exclude_manifest else set())
    status: dict = {}
    top: list = []
    items = _items(T17._stream(FAMILIES, Path(a.root), record_source or T17.corpus_records, status), a.seed, top)
    cands, texts = [], Counter()
    if a.workers > 1:
        with get_context("spawn").Pool(a.workers) as pool:
            for hits in pool.imap(J.scan_record, items, chunksize=64):
                cands += hits
    else:
        for it in items:
            cands += J.scan_record(it)
    for c in cands:
        texts[c["recipe_id"]] += 1
    in_1000 = {rid for _, rid in top}
    rows = J.stratified_sample(cands, seed=a.seed, in_1000=in_1000, excluded=excluded)
    man = J.manifest_rows(rows)
    a.out_manifest.parent.mkdir(parents=True, exist_ok=True)
    with a.out_manifest.open("x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(man[0]) if man else ["case_id"], lineterminator="\n")
        w.writeheader()
        w.writerows(man)
    a.out_private.parent.mkdir(parents=True, exist_ok=True)
    with a.out_private.open("x", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["case_id", "recipe_id", "source_family", "stratum", "shape", "excerpt", *READER_COLS])
        for m, r in zip(man, rows):
            w.writerow([m["case_id"], r["recipe_id"], r["source_family"], r["stratum"], r["shape"], r["excerpt"], "", "", ""])
    shapes = Counter(c["shape"] for c in cands)
    print(json.dumps({"cases_found": len(cands), "texts_with_cases": len(texts),
                      "by_family": dict(Counter(c["source_family"] for c in cands)),
                      "top_shapes": dict(shapes.most_common(5)), "sampled": len(rows),
                      "by_stratum": dict(Counter(r["stratum"] for r in rows)), "family_status": status}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
