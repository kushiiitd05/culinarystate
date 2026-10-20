#!/usr/bin/env python3
"""S116: top-5 process-state evidence acquisition queue (candidates only; nothing is promoted to a ledger).
Selection from reports/h_state/hstate_missing_evidence_cells_ranked.csv: specific thermal processes only (no generic cook/heat), distinct
ingredients, highest recipes_unlocked then cuts_unlocked, with a physically measurable state attribute and a realistic chance of primary evidence.
  /opt/anaconda3/bin/python tools/make_evidence_queue.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PICK = [("onion", "simmer", "flavonoid (quercetin) and vitamin C retention in simmered onion; widely studied (Phenol-Explorer style papers)"),
        ("carrot", "roast", "carotenoid / vitamin retention on roasting: many cooking-method studies; unlocks the most Gold cuts"),
        ("garlic", "fry", "alliin/allicin and polyphenol change on frying; sauteed aromatics occur in most Gold recipes"),
        ("garden pea", "steam", "vitamin C retention in steamed peas: classic retention-study vegetable, 22 cuts unlocked"),
        ("ginger", "fry", "gingerol retention on frying; completes the aromatic-vegetable set and reuses the garlic extraction route")]
OUT = ROOT / "evidence" / "queues" / "hstate_top5_process_state_evidence.csv"


def main():
    rows = list(csv.DictReader((ROOT / "reports/h_state/hstate_missing_evidence_cells_ranked.csv").open()))
    out = []
    for ing, proc, why in PICK:
        r = next(x for x in rows if x["ingredient"] == ing and x["process"] == proc)
        out.append({"ingredient": ing, "ingredient_id": r["ingredient_id"], "process": proc, "process_id": r["process_id"], "state_attribute_needed": r["state_attribute_needed"],
                    "recipes_unlocked": r["recipes_unlocked"], "cuts_unlocked": r["cuts_unlocked"], "evidence_type_needed": r["evidence_type_needed"],
                    "candidate_sources": r["candidate_sources"], "priority_reason": why,
                    "promotion_status": "CANDIDATE_ONLY: source span/table -> provenance -> human verification -> ledger promotion"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(len(out), [(o["ingredient"], o["process"], o["recipes_unlocked"], o["cuts_unlocked"]) for o in out])


if __name__ == "__main__":
    main()
