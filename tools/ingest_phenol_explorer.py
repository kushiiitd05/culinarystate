#!/usr/bin/env python3
"""DEL-1: ingest cached Phenol-Explorer retention pages into the ledgers (no network).

  /opt/anaconda3/bin/python tools/ingest_phenol_explorer.py [--root ledgers/data]
Run tools/crawl_phenol_explorer.py first. Missing detail pages are counted and skipped (re-crawl, re-run).
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.phenol_explorer import (CachedFetcher, parse_details, parse_food_processing,  # noqa: E402
                                                  parse_list_page)
from culinarystate.ingest.phenol_explorer_build import build  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=str(ROOT / "ledgers" / "data"))
a = ap.parse_args()
cache = CachedFetcher(ROOT / "data" / "raw" / "phenol_explorer" / "html")


def cached(path):
    p = cache.path_for(path)
    return p.read_text(encoding="utf-8") if p.exists() else None


rows, last = parse_list_page(cached("/retention-factors/polyphenols"))
for pg in range(2, last + 1):
    rows += parse_list_page(cached(f"/retention-factors/polyphenols?page={pg}"))[0]
items, missing, empty = [], Counter(), 0
seen = set()
for fp in sorted({r.fp_path for r in rows}):
    html = cached(fp)
    if html is None:
        missing["fp"] += 1
        continue
    for food in parse_food_processing(html):
        if food.details_path in seen:
            continue
        seen.add(food.details_path)
        dh = cached(food.details_path)
        if dh is None:
            missing["details"] += 1
            continue
        det = parse_details(dh)
        if not det.values:
            empty += 1
            continue
        items.append((food, det))
counts = build(LedgerStore(Path(a.root)), items)
print(f"detail pages parsed {len(items)}, empty {empty}, missing {dict(missing)}")
for (rt, act), n in sorted(counts.items()):
    print(f"{rt:6s} {act:9s} {n}")
