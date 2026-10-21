#!/usr/bin/env python3
"""ES-1.1: build the normalised EVD export (non-destructive) and the SVAR duplicate mapping.
  python tools/build_evd_export_v1.py
Writes: registry/svar_duplicate_mapping_v1.csv, exports/evd/evd_export_v1.jsonl, exports/evd/evd_matrix_table_v1.csv, exports/evd/evd_prior_state_table_v1.csv, exports/evd/evd_export_v1.manifest.json.
Never writes under ledgers/."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.evd_export import build_export, canon_json, file_sha256, latest_records  # noqa: E402

REG = ROOT / "registry"
OUT = ROOT / "exports" / "evd"
OUT.mkdir(parents=True, exist_ok=True)

# ---- duplicate / equivalent-candidate mapping (from the frozen MP-1 variable registry; rule = normalised analyte name) ----
sv, _ = latest_records("SVAR")
reg = list(csv.DictReader(open(REG / "state_variable_registry_v1.csv", newline="", encoding="utf-8")))
byid = {r["state_variable_id"]: r for r in reg}
rows = []
for r in reg:
    if r["status"] == "DUPLICATE":
        c = byid[r["canonical_variable_id"]]
        rows.append({"duplicate_id": r["state_variable_id"], "canonical_id": c["state_variable_id"], "duplicate_name": r["name"], "canonical_name": c["name"], "relation": "DUPLICATE_SAME_ANALYTE",
                     "rule": "normalised analyte name equal (strip ' content', trailing element symbol, spaces/hyphens, case)", "evidence_rows_duplicate": r["current_row_count"], "evidence_rows_canonical": c["current_row_count"],
                     "source_families_duplicate": r["source_families"], "source_families_canonical": c["source_families"], "reversible": "yes: both ids kept in every export row (target_state_variable_id, canonical_variable_id)",
                     "mapping_status": "PROVISIONAL_NAME_RULE_MEASUREMENT_BASIS_EQUIVALENCE_NOT_VERIFIED", "note": "no ledger id is deleted or rewritten"})
    elif "equivalent-candidate" in (r.get("notes") or ""):
        rows.append({"duplicate_id": r["state_variable_id"], "canonical_id": "", "duplicate_name": r["name"], "canonical_name": "", "relation": "EQUIVALENT_CANDIDATE_NOT_MERGED",
                     "rule": "one name is a comma-qualified form of the other; definitions may differ", "evidence_rows_duplicate": r["current_row_count"], "evidence_rows_canonical": "", "source_families_duplicate": r["source_families"], "source_families_canonical": "",
                     "reversible": "n/a (not merged)", "mapping_status": "NEEDS_HUMAN_OR_ANALYTICAL_CHECK", "note": r["notes"]})
cols = list(rows[0].keys())
with open(REG / "svar_duplicate_mapping_v1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

# ---- export ----
before = {n: file_sha256(ROOT / "ledgers/data" / f"{n}.jsonl") for n in ("EVD", "SVAR", "COND", "PROC", "ING", "SRC")}
export, mt, pt, meta = build_export()
with open(OUT / "evd_export_v1.jsonl", "w", encoding="utf-8") as f:
    for r in export:
        f.write(canon_json(r) + "\n")
with open(OUT / "evd_matrix_table_v1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    keys = ["ingredient_id", "raw_name", "food_group", "variety", "part", "form", "prior_processing", "initial_state", "geometry", "storage_ripeness"]
    w.writerow(["matrix_id"] + keys)
    for k in sorted(mt):
        w.writerow([k] + [mt[k].get(x) for x in keys])
with open(OUT / "evd_prior_state_table_v1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["prior_state_id", "initial_state_normalised", "prior_processing_normalised", "vocabulary_status"])
    for k in sorted(pt):
        w.writerow([k, pt[k]["initial_state"], pt[k]["prior_processing"], "RAW_DESCRIPTOR_HASH (controlled vocabulary pending MP-5A/ES-1.x)"])
after = {n: file_sha256(ROOT / "ledgers/data" / f"{n}.jsonl") for n in before}
assert before == after, "ledger files changed during export"
meta.update({"export_file": "exports/evd/evd_export_v1.jsonl", "export_sha256": file_sha256(OUT / "evd_export_v1.jsonl"), "export_rows": len(export),
             "mapping_file": "registry/svar_duplicate_mapping_v1.csv", "mapping_sha256": file_sha256(REG / "svar_duplicate_mapping_v1.csv"),
             "matrix_table_sha256": file_sha256(OUT / "evd_matrix_table_v1.csv"), "prior_state_table_sha256": file_sha256(OUT / "evd_prior_state_table_v1.csv"),
             "ledger_sha256_before_after": {"before": before, "after": after, "unchanged": before == after}})
(OUT / "evd_export_v1.manifest.json").write_text(json.dumps(meta, indent=1, sort_keys=True))
print(json.dumps({k: meta[k] for k in ("active_rows", "export_rows", "ledger_version_lines", "ledger_ids_latest", "export_sha256")}, indent=1))
print("mapping rows:", len(rows), {x["relation"] for x in rows})
