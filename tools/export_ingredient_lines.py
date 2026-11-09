#!/usr/bin/env python
"""Export ingredient lines per recipe for corpus NER inference (S173, D-077). Data plane only.

Writes <out>/<FAMILY>.jsonl, one row per recipe: {"recipe_id", "source_family", "lines"}. Refuses A1_BBC_GOOD_FOOD
unless --allow-bbc is given AND the run is on the Mac (D-003: BBC text stays off the servers). The output directory
must be under data/ (git-ignored) or outside the repository, and new or empty.

    python tools/export_ingredient_lines.py --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET \
        --out data/derived/ingredient_lines/
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("_t17", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
BBC = "A1_BBC_GOOD_FOOD"


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--allow-bbc", action="store_true")
    a = ap.parse_args(argv)
    if BBC in a.families and not (a.allow_bbc and platform.system() == "Darwin"):
        ap.error("D-003: BBC Good Food lines are exported only on the Mac with --allow-bbc")
    out = a.out.resolve()
    try:
        parts = out.relative_to(ROOT.resolve()).parts
    except ValueError:
        parts = ("data",)
    if parts[:1] != ("data",):
        ap.error("--out must be under data/ (git-ignored) or outside the repository")
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        ap.error("--out must be new or empty")
    n = Counter()
    src = record_source or T17.corpus_records
    for fam in a.families:
        with open(out / f"{fam}.jsonl", "x", encoding="utf-8") as fh:
            for r in src([fam], ROOT):
                lines = [s.strip() for s in r.get("ingredient_lines") or [] if isinstance(s, str) and s.strip()]
                if not lines:
                    n[(fam, "no_lines")] += 1
                    continue
                fh.write(json.dumps({"recipe_id": r["recipe_id"], "source_family": fam, "lines": lines},
                                    ensure_ascii=False) + "\n")
                n[(fam, "recipes")] += 1
                n[(fam, "lines")] += len(lines)
    print(json.dumps({f"{f}:{k}": v for (f, k), v in sorted(n.items())}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
