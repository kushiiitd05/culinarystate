#!/usr/bin/env python
"""Build registry/ing_sr_target_content_draft_v1.csv: SR Legacy content of each screened nutrient for the usable
(HIGH / MEDIUM, ranks 1-3) SR candidates of every ING whose rank-1 proposal is usable (S176, L-ROUTER). AI_DRAFTED, derived from public-domain SR Legacy values and the
AI-drafted ING -> SR registry. The evidence gates read this table at run time, so the demo needs no data/raw.

    python tools/build_target_content_table.py [--out registry/ing_sr_target_content_draft_v1.csv] [--check]

``--check`` rebuilds in memory and exits 1 if the committed table differs (no write). Refuses to overwrite without
``--force``. Reads: registry/target_presence_floor_v1_PROPOSED.csv (which nutrient keys), registry/ing_sr_legacy_match_
draft_v1.csv, data/raw/fdc/sr_legacy (read only).
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lotstate.sr_legacy import default_dir  # noqa: E402
from culinarystate.mechanism import evidence_gates as EG  # noqa: E402


def build() -> str:
    floors = EG.read_floors()
    cands = EG.read_candidates()
    keys = sorted({f.nutrient_key for f in floors.values()})
    values = EG.read_sr_values(default_dir(ROOT), {f for c in cands.values() for f, _, _ in c}, keys)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=EG.TABLE_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(EG.build_table_rows(cands, values, keys))
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(EG.TABLE_PATH))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    text, out = build(), Path(a.out)
    if a.check:
        same = out.exists() and out.read_text(encoding="utf-8") == text
        print("TABLE_MATCHES_REBUILD" if same else "TABLE_DIFFERS_OR_MISSING")
        return 0 if same else 1
    if out.exists() and not a.force:
        ap.error("refusing to overwrite an existing table (use --force)")
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({text.count(chr(10)) - 1} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
