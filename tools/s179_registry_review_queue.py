"""S179 P9: write the mention-weighted human review queue for registry/ing_sr_defaults_v1.csv (packet Q44).

    python tools/s179_registry_review_queue.py --families A1_BBC_GOOD_FOOD --out reports/s179/ing_sr_review_queue_BBC.csv

Mentions = ingredient lines whose Rung A food mention resolves to the term (same finder as the S175 census).
D-003: A1_BBC_GOOD_FOOD runs on the Mac only. Output: one row per registry term, counts only, no recipe text.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from culinarystate.composition import review_queue as RQ  # noqa: E402
from culinarystate.extraction.rung_a_lexicon import load_lexicon  # noqa: E402
from s175_line_mass_census import REGISTRY, _ing_names, make_find_food  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--top-n", type=int, default=100)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    from step17b_rung_a_dryrun import corpus_records
    name, freq = _ing_names()
    find = make_find_food(load_lexicon(), name, freq)
    counts: Counter = Counter()
    for rec in corpus_records(tuple(a.families), ROOT):
        for line in rec.get("ingredient_lines") or []:
            if (n := find(line.translate({0x2044: "/", 0x2215: "/"}))) is not None:
                counts[n] += 1
    total = sum(counts.values())
    with open(REGISTRY, newline="", encoding="utf-8") as fh:
        reg = list(csv.DictReader(fh))
    rows = RQ.review_rows(reg, counts, total_mentions=total, top_n=a.top_n)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=RQ.COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "mention_share": f"{r['mention_share']:.6f}",
                        "cumulative_share": f"{r['cumulative_share']:.6f}"})
    top = rows[min(a.top_n, len(rows)) - 1]["cumulative_share"]
    print(f"terms {len(rows)}; food mentions {total}; registry share {rows[-1]['cumulative_share']:.4f}; "
          f"top-{a.top_n} share {top:.4f}; kind checks {sum(1 for r in rows if r['review_reason'].endswith('CHECK'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
