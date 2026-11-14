#!/usr/bin/env python
"""S179 (T3-C11-R1): rule compiler vs the P1 gold (7) and the 40 dev-gold recipes (pilot_20 v1.1 + Food.com v1.1),
pooled counts, Wilson intervals.

    /opt/anaconda3/bin/python tools/s179_compiler_vs_gold_pooled.py

Mac only: the P1 recipes are BBC Good Food (D-003) and every gold folder is git-ignored. Writes ONE counts-only JSON
(no recipe id, no text) and refuses to overwrite it. None of these gold sets is independent (D-017, D-060).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation import compiler_vs_gold_pooled as P  # noqa: E402

TOOL_VERSION = "s179-compiler-vs-gold-pooled-0.1.0"
GOLD = ROOT / "annotation" / "gold"
SETS = (
    ("P1_A_KUSH", GOLD / "deep_gold_pilot_v1" / "A", "DGP-A-*.json", "HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND"),
    ("DEV_PILOT20_V1_1", GOLD / "pilot_20_adjudicated_v1_1", "*.ADJUDICATED.json",
     "AI_ASSISTED_HUMAN_REVIEWED_DEV_GOLD"),
    ("DEV_FOODCOM_V1_1", GOLD / "foodcom_ai_assisted_v1_1", "foodcom_v1_1_joint.json",
     "AI_ASSISTED_HUMAN_REVIEWED_DEV_GOLD"),
)
# Not used: evidence_first_expansion/_split/{Kush,Parv} are DRAFT with 0 step events (lines only), so they cannot score
# events or state.
OUT = ROOT / "reports" / "del3" / "compiler_vs_gold_pooled_S179.json"


def set_digest(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def load_docs(paths: list[Path]) -> list[dict]:
    """One gold-1.0 doc per file, or a bundle file with a ``recipes`` list."""
    docs: list[dict] = []
    for p in paths:
        d = json.loads(p.read_text())
        docs.extend(d["recipes"] if isinstance(d, dict) and "recipes" in d else [d])
    return docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    reg = {r["canonical_name"] for r in csv.DictReader(
        (ROOT / "registry" / "ingredients" / "ingredient_registry_v1.csv").open(newline=""))}
    result = {"record": "S179_COMPILER_VS_GOLD_POOLED", "tool_version": TOOL_VERSION,
              "status": "AI_DIAGNOSTIC_COUNTS_ONLY", "not_independent": True, "sets": {}}
    for name, folder, pattern, basis in SETS:
        paths = sorted(folder.glob(pattern))
        if not paths:
            sys.exit(f"INPUT_MISSING: {name} ({folder})")
        docs = load_docs(paths)
        scored = P.score_set(docs, reg, label_basis=basis)
        scored["input_set_sha256"] = set_digest(paths)
        result["sets"][name] = scored
        lv = scored["levels"]["P"]
        print(name, scored["n_recipes"], "P events_loose F1", lv["events_loose"]["f1"],
              "state acc", lv["state_fields"]["accuracy"], "alive F1", lv["alive_entities"]["f1"])
    with out.open("x") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("wrote", out.relative_to(ROOT), hashlib.sha256(out.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
