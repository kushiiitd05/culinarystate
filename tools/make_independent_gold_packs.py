#!/usr/bin/env python3
"""S116: blank, identical, independent annotation packs for the PRIMARY evidence-first recipes. No AI labels, no model output.

  /opt/anaconda3/bin/python tools/make_independent_gold_packs.py [--check-only]
Reads annotation/gold/evidence_first_expansion/selection_manifest_v1.csv, takes recipe text from the local Food.com parquet, writes
{Kush,Parv}/<id>.<Annotator>.json (schema gold-1.0, status DRAFT_HUMAN_INDEPENDENT, entity/concept TODO) and preannotation_manifest.csv
(ids + hashes + validation flags, NO recipe text). Existing annotator files that are not pristine are human work and are never overwritten.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import select_evidence_first_gold as sel  # noqa: E402

D = sel.D
ANNOTATORS = ("Kush", "Parv")
STATUS = "DRAFT_HUMAN_INDEPENDENT"


def template(rid: str, rec: dict, who: str) -> dict:
    return {"schema_version": "gold-1.0", "recipe_id": rid, "source_ref": f"Food.com recipe {rid[2:]} (Kaggle irkaal; local-only); annotation_status={STATUS}", "annotator": who, "status": "DRAFT",
            "locale": "US", "ingredient_lines": [{"line_index": i, "text": t, "spans": [], "entity": "TODO", "concept": "TODO"} for i, t in enumerate(rec["ings"])],
            "steps": [{"step_index": i, "text": t, "spans": [], "events": [], "coref": []} for i, t in enumerate(rec["steps"])], "unknowns": [], "notes": ""}


def pristine(doc: dict) -> bool:
    return (not any(l["spans"] or l["entity"] != "TODO" or l["concept"] != "TODO" for l in doc["ingredient_lines"])
            and not any(s["spans"] or s["events"] or s.get("coref") for s in doc["steps"]) and not doc["unknowns"] and not doc.get("notes"))


def raw_hash(doc: dict) -> str:
    return sel.recipe_hash(None, [l["text"] for l in doc["ingredient_lines"]], [s["text"] for s in doc["steps"]])


def main():
    man = list(csv.DictReader((D / "selection_manifest_v1.csv").open()))
    prim = sorted({r["source_recipe_id"] for r in man if r["selection_role"] == "PRIMARY"})
    rec = sel.load_recipes(set(prim))
    rows = []
    for rid in prim:
        docs = {}
        for who in ANNOTATORS:
            p = D / who / f"{rid}.{who}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists() and not pristine(json.loads(p.read_text())):
                docs[who] = (p, json.loads(p.read_text()), "HUMAN_WORK_PRESERVED")
                continue
            doc = template(rid, rec[rid], who)
            if "--check-only" not in sys.argv:
                p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
            docs[who] = (p, doc, "BLANK_DRAFT")
        h = {w: raw_hash(d[1]) for w, d in docs.items()}
        rows.append({"source_recipe_id": rid, "recipe_content_sha256_kush": h["Kush"], "recipe_content_sha256_parv": h["Parv"],
                     "recipe_hashes_match": h["Kush"] == h["Parv"], "kush_file_sha256": hashlib.sha256(docs["Kush"][0].read_bytes()).hexdigest() if docs["Kush"][0].exists() else "",
                     "parv_file_sha256": hashlib.sha256(docs["Parv"][0].read_bytes()).hexdigest() if docs["Parv"][0].exists() else "",
                     "kush_blank": pristine(docs["Kush"][1]), "parv_blank": pristine(docs["Parv"][1]), "annotation_status": STATUS,
                     "kush_state": docs["Kush"][2], "parv_state": docs["Parv"][2], "n_ingredient_lines": len(docs["Kush"][1]["ingredient_lines"]), "n_steps": len(docs["Kush"][1]["steps"]),
                     "ai_prefill": "NONE", "model_outputs_embedded": "NONE"})
    with (D / "preannotation_manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ok = all(r["recipe_hashes_match"] and r["kush_blank"] and r["parv_blank"] for r in rows)
    print(f"{len(rows)} recipes; hashes match + both blank for all: {ok}")
    sys.exit(0 if ok and len(rows) == sel.PRIMARY_N else 1)


if __name__ == "__main__":
    main()
