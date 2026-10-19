#!/usr/bin/env python3
"""S101: freeze the pilot_20 annotation input and create two independent blank annotator copies.

  /opt/anaconda3/bin/python tools/freeze_gold_pilot.py
Source = annotation/gold/templates/<id>.TEMPLATE.json (raw text only, no labels) for the recipes in annotation/batches/pilot_20.csv.
Writes annotation/gold/pilot_20/{Kush,Parv}/<id>.<Annotator>.json (status DRAFT, never HUMAN_VERIFIED here) and
annotation/gold/pilot_20_manifest.csv (IDs, family, hashes, no recipe text; committed). Existing annotator files that differ
from the pristine template are human work and are NEVER overwritten. Refuses to run if any template carries labels.
"""
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

GOLD = ROOT / "annotation" / "gold"
HANDBOOK, SCHEMA = "annotation_handbook_v1+addendumA", "gold-1.0"
ANNOTATORS = ("Kush", "Parv")


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def pristine(doc: dict) -> bool:
    return (not any(l["spans"] or l["entity"] != "TODO" or l["concept"] != "TODO" for l in doc["ingredient_lines"])
            and not any(s["spans"] or s["events"] or s.get("coref") for s in doc["steps"]) and not doc["unknowns"])


def main() -> None:
    batch = list(csv.DictReader((ROOT / "annotation" / "batches" / "pilot_20.csv").open()))
    rec_by_a1 = {}
    st = LedgerStore()
    for r in st.all_latest("REC"):
        for ref in r.get("external_refs") or []:
            if ref.startswith("A1:"):
                rec_by_a1[ref[3:]] = r
    fam_size = {}
    for r in rec_by_a1.values():
        fam_size[r["family_id"]] = fam_size.get(r["family_id"], 0) + 1
    rows, frozen_at = [], datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for b in batch:
        rid = b["recipe_id"]
        tpl = json.loads((GOLD / "templates" / f"{rid}.TEMPLATE.json").read_text())
        if not pristine(tpl):
            sys.exit(f"{rid}: template carries labels - refusing to freeze")
        raw = {"title": b["title"], "ingredients": [l["text"] for l in tpl["ingredient_lines"]],
               "steps": [s["text"] for s in tpl["steps"]]}
        content_sha = hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        rec = rec_by_a1[rid]
        row = {"recipe_id": rid, "rec_id": rec["id"], "family_id": rec["family_id"],
               "family_size_in_corpus": fam_size[rec["family_id"]], "stratum": b["stratum"], "tags": b["tags"],
               "source": "BBC Good Food (A1 scrape, UK, local only D-003)", "source_url": rec["source_url"],
               "n_ingredient_lines": len(raw["ingredients"]), "n_steps": len(raw["steps"]),
               "raw_content_sha256": content_sha, "rec_content_sha256": rec["content_sha256"],
               "hash_matches_rec": content_sha == rec["content_sha256"], "handbook_version": HANDBOOK,
               "schema_version": SCHEMA, "frozen_at_utc": frozen_at}
        for who in ANNOTATORS:
            p = GOLD / "pilot_20" / who / f"{rid}.{who}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            blank = {**tpl, "annotator": who, "status": "DRAFT"}
            if p.exists():
                cur = json.loads(p.read_text())
                if not pristine(cur) or cur["status"] != "DRAFT":
                    row[f"{who.lower()}_file_state"] = f"HUMAN_WORK_PRESERVED:{cur['status']}"
                    continue
            p.write_text(json.dumps(blank, indent=2, ensure_ascii=False) + "\n")
            row[f"{who.lower()}_file_state"] = "BLANK_DRAFT"
        row["adjudication_status"] = "NOT_STARTED"
        rows.append(row)
    cols = list(rows[0])
    with (GOLD / "pilot_20_manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    bad = [r["recipe_id"] for r in rows if not r["hash_matches_rec"]]
    fams = [r["family_id"] for r in rows]
    print(f"{len(rows)} recipes; hash==REC for {len(rows) - len(bad)}; mismatches {bad}; distinct families {len(set(fams))}; "
          f"max family size {max(r['family_size_in_corpus'] for r in rows)}")


if __name__ == "__main__":
    main()
