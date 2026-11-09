"""S175: FDA approximate-pH archive (data/raw/fda_ph, git-ignored) -> registry/food_ph_fda2003_v1.csv.

    python tools/build_food_ph_registry.py
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.composition import food_ph as PH  # noqa: E402

RAW = ROOT / "data/raw/fda_ph/lacf_phs_2004.html"
OUT = ROOT / "registry/food_ph_fda2003_v1.csv"


def main() -> int:
    data = RAW.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    rows = PH.parse_fda_html(data.decode("latin-1"), strict=False)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["item", "ph_low", "ph_high", "value_type", "ph_raw", "source", "source_sha256"])
        for r in rows:
            w.writerow([r.item, "" if r.low is None else r.low, "" if r.high is None else r.high, r.value_type,
                        r.raw, PH.SOURCE, sha])
    kinds: dict[str, int] = {}
    for r in rows:
        kinds[r.value_type] = kinds.get(r.value_type, 0) + 1
    print(len(rows), kinds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
