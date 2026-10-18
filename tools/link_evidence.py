#!/usr/bin/env python3
"""Link all EVD rows to PROC (process_id, step_process_ids) and ING (EXACT/HIGH only) as new versions.

  /opt/anaconda3/bin/python tools/link_evidence.py
Writes registry/evidence/evd_ingredient_link_review.csv (MEDIUM ties + unlinked matrices not yet signed) and
updates PROC.evidence_coverage. MEDIUM/NONE matrices with a human-signed LINKED decision
(registry/evidence/evd_ingredient_link_decisions.csv, tools/apply_link_review.py) get that ingredient_id; signed
HELD / CONCEPT_MISSING matrices stay unlinked and leave the review table. Idempotent (unchanged rows are skipped).
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.linker import IngredientLinker, link_process  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.registry_build import POLYSEMOUS  # noqa: E402

st = LedgerStore()
proc_ids = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC")}
concepts = {r["canonical_name"]: (r["id"], r.get("corpus_frequency") or 0) for r in st.all_latest("ING")
            if r["status"] == "ACTIVE"}
linker = IngredientLinker(concepts, polysemous=set(POLYSEMOUS))
DEC = ROOT / "registry" / "evidence" / "evd_ingredient_link_decisions.csv"
signed = {}
if DEC.exists():
    for d in pd.read_csv(DEC, dtype=str).fillna("").to_dict("records"):
        if d["status"] in ("LINKED", "HELD", "CONCEPT_MISSING"):
            signed[(d["matrix_raw"], d["source_family"])] = d["ingredient_id"] if d["status"] == "LINKED" else None

counts, bands, review, cov = Counter(), Counter(), {}, Counter()
cache: dict[str, object] = {}
for e in st.all_latest("EVD"):
    m = e["matrix"]
    lk = cache.setdefault(m["raw_name"], linker.link(m["raw_name"]))
    bands[(e["source_family_id"], lk.band)] += 1
    primary, steps = link_process(e["process"].get("steps", []), proc_ids)
    for pid in steps:
        cov[pid] += 1
    key = (m["raw_name"], e["source_family_id"])
    if lk.band in ("EXACT", "HIGH"):
        ing = lk.ing_id
    else:
        ing = signed.get(key) or None
        if ing:
            bands[(e["source_family_id"], "+SIGNED")] += 1             # subset of the MEDIUM/NONE count above
    new_m = {**m, "ingredient_id": ing}
    new_p = {**e["process"], "process_id": primary, "step_process_ids": steps}
    counts[st.upsert({**e, "matrix": new_m, "process": new_p})[0]] += 1
    if lk.band in ("MEDIUM", "NONE") and key not in signed:
        r = review.setdefault(m["raw_name"], {"matrix_raw": m["raw_name"], "source_family": e["source_family_id"],
                                              "band": lk.band, "suggested": lk.concept,
                                              "alternatives": "|".join(lk.alternatives), "rows": 0, "human_decision": ""})
        r["rows"] += 1

for p in st.all_latest("PROC"):
    if (p.get("evidence_coverage") or 0) != cov.get(p["id"], 0):
        st.upsert({**p, "evidence_coverage": cov.get(p["id"], 0)})

out = ROOT / "registry" / "evidence"
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(review.values()).sort_values("rows", ascending=False).to_csv(out / "evd_ingredient_link_review.csv",
                                                                           index=False)
print("EVD writes:", dict(counts))
for (fam, band), n in sorted(bands.items()):
    print(f"  {fam:22s} {band:7s} {n:6,}")
print(f"review rows (MEDIUM/NONE matrices): {len(review)}")
