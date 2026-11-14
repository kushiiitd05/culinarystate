#!/usr/bin/env python3
"""D-116: deterministic composition marker table from ACTIVE ING names (name rules only; AI_DRAFTED_NOT_REVIEWED until
Kush/Parv review). 7B/72B attribute drafts are attached as flags, never used to decide.

    python tools/s179_build_composition_markers.py --out registry/composition_markers_v1.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = [
    ("SALT", r"^(?:(?:sea|kosher|table|rock|coarse|fine|flaky|iodized|pink himalayan|celery|garlic|onion|seasoned) )?salt$"
             r"|^(?:light |dark )?soy sauce$|^fish sauce$|^(?:stock|bouillon) cubes?$|^bouillon$"),
    ("ACID", r"vinegar|^(?:fresh )?(?:lemon|lime) juice$|^(?:lemon|lime)s?$|^citric acid$|^tamarind|(?:^| )wine$"),
    ("LIPID", r"(?:^| )oils?$|^(?:unsalted |salted )?butter$|^ghee$|^lard$|^shortening$|^margarine$|^cooking spray$"
              r"|^dripping$|^suet$"),
    ("AQUEOUS", r"^(?:cold |hot |boiling |warm )?water$|(?:^| )(?:stock|broth)$"),
]
EXCLUDE = re.compile(r"peanut butter|butter(?:milk|nut|scotch)|apple butter|oil-packed|cocoa butter", re.I)


def markers_for(name: str) -> list[str]:
    n = name.strip().lower()
    if EXCLUDE.search(n):
        return []
    return [m for m, rx in RULES if re.search(rx, n)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    last = {}
    for line in (ROOT / "ledgers/data/ING.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            last[r["id"]] = r
    flags = {}
    for f in ("registry/ing_attributes_ai_draft_v1.csv", "registry/ing_attributes_ai_draft_72b_v1.csv"):
        p = ROOT / f
        if p.exists():
            for r in csv.DictReader(p.open()):
                flags.setdefault(r["id"], []).append(r["acidic"])
    rows = []
    for k, v in sorted(last.items()):
        if v.get("status", "ACTIVE") != "ACTIVE":
            continue
        for m in markers_for(v["canonical_name"]):
            rows.append({"ing_id": k, "canonical_name": v["canonical_name"], "marker": m, "rule": "NAME_RULE_V1",
                         "llm_acidic_7b_72b": "/".join(flags.get(k, [])), "status": "AI_DRAFTED_NOT_REVIEWED"})
    with out.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), {m: sum(r["marker"] == m for r in rows) for m, _ in RULES})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
