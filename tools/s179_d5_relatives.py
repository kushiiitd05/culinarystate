#!/usr/bin/env python3
"""D5 scorer input ``--relatives`` (S179): ING id -> parent ING ids, for every food in the frozen P/C/U/X blocks.

The same relation the P2 drafter used for SIMILAR_ONLY gold (``tools/d5_draft_pc.py``: exact or parent-ingredient EVD
rows; ``lexicon.parents``). Deterministic; ``--check`` compares with the file.

    python tools/s179_d5_relatives.py [--check]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BENCH = ("benchmark/d5/d5_benchmark_v1_D085_PC.csv", "benchmark/d5/d5_benchmark_v1_D085_UX.csv")
OUT = ROOT / "benchmark/d5/d5_relatives_v1_D085.json"


def build() -> str:
    from culinarystate.decision.pipeline import load_lexicon
    from culinarystate.ledgers.store import LedgerStore
    lex, _ = load_lexicon(LedgerStore())
    ings = set()
    for b in BENCH:
        with (ROOT / b).open(encoding="utf-8-sig") as fh:
            ings |= {r["ingredient_id"] for r in csv.DictReader(fh) if r.get("ingredient_id")}
    rel = {i: sorted(lex.parents.get(i, ())) for i in sorted(ings)}
    return json.dumps(rel, indent=1, sort_keys=True) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    text = build()
    if a.check:
        ok = OUT.is_file() and OUT.read_text(encoding="utf-8") == text
        print("OK" if ok else "DIFFERS")
        return 0 if ok else 1
    if OUT.exists() and OUT.read_text(encoding="utf-8") != text:
        raise SystemExit("refusing to overwrite with different content")
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), len(json.loads(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
