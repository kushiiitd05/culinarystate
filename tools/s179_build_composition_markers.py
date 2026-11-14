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
# v2 (ksh+prv AI review, D-085, 14 Nov): agreed reclassifications, marker sets, role_default.
RULES_V2 = [
    ("SALT", RULES[0][1] + r"|^miso|^(?:salted butter)$"),
    ("ACID", r"vinegar|^(?:fresh )?(?:lemon|lime|orange) juice$|^(?:lemon|lime)s?$|^citric acid$|^tamarind"
             r"|^(?!rice wine$|shao ?h?sing wine$|shaoxing wine$).*(?:^| )wine$"),
    ("LIPID", RULES[2][1] + r"|^(?:double|heavy|single|whipping) cream$|^(?:duck|goose) fat$|^clarified butter$"),
    ("AQUEOUS", RULES[3][1] + r"|^bouillon$|^rice wine$|^shao ?h?sing wine$|^shaoxing wine$|soy sauce$|^fish sauce$"
                r"|^(?!.*vinegar).*(?:^| )wine$|^(?:double|heavy|single|whipping) cream$|^dashi$"),
]
EXCLUDE = re.compile(r"peanut butter|butter(?:milk|nut|scotch)|apple butter|oil-packed|cocoa butter", re.I)


def markers_for(name: str, rules=RULES) -> list[str]:
    n = name.strip().lower()
    if EXCLUDE.search(n):
        return []
    out = [m for m, rx in rules if re.search(rx, n)]
    if rules is RULES_V2 and n == "bouillon":
        out = [m for m in out if m != "SALT"]
    return out


def role_default(name: str) -> str:
    return "FOOD" if re.search(r"cream$", name.strip().lower()) else "MEDIUM"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--version", choices=("v1", "v2"), default="v1")
    a = ap.parse_args(argv)
    rules = RULES_V2 if a.version == "v2" else RULES
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
        for m in markers_for(v["canonical_name"], rules):
            row = {"ing_id": k, "canonical_name": v["canonical_name"], "marker": m,
                   "rule": "NAME_RULE_V1" if a.version == "v1" else "NAME_RULE_V2",
                   "llm_acidic_7b_72b": "/".join(flags.get(k, [])),
                   "status": "AI_DRAFTED_NOT_REVIEWED" if a.version == "v1" else "AI_DELEGATED_REVIEWED_KSH_PRV_D085"}
            if a.version == "v2":
                row.update(role_default=role_default(v["canonical_name"]), basis="NAME_RULE_V2",
                           source="ING ledger canonical_name; ksh+prv review 2026-11-14")
            rows.append(row)
    with out.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), {m: sum(r["marker"] == m for r in rows) for m, _ in rules})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
