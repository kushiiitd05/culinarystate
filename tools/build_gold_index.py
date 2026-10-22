#!/usr/bin/env python3
"""STEP 07H-R: gold_recipe_index_v1.parquet + _gold_membership.json (consumed by build_recipe_base.py).
Links recipe_id -> existing Gold annotation artifacts WITHOUT copying or opening label content beyond file names/manifests. All existing Gold is AI-drafted + human-reviewed (D-016/D-017), NOT independent -> GOLD_PENDING_INDEPENDENT_IAA.
Sealed linker sets (final_link_set, fresh_linker_set) are NOT recipe-level gold and are not read."""
import csv
import glob
import json
import os
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.recipes import corpus as C  # noqa: E402

G = ROOT / "annotation/gold"
rec = C.rec_latest()
a1 = {}
for r in rec.values():
    for e in r.get("external_refs") or []:
        if e.startswith("A1:"):
            a1[e[3:]] = r["id"]
AI = "AI-drafted (OpenAI/Claude) and human-reviewed by Kush (+Parv relayed); NOT independent blind annotation (D-016, D-017)"
rows, member = [], {}
fam_override = {}


def add(rid, version, annotators, ptr, notes, role, extra=None):
    rows.append({"recipe_id": rid, "gold_status": "GOLD_PENDING_INDEPENDENT_IAA", "annotation_version": version, "annotators": annotators, "independent_annotation": False, "adjudicated": True, "iaa_available": False, "eligible_for_training": False,
                 "eligible_for_calibration": True, "eligible_for_test": False, "annotation_artifact_pointer": ptr, "notes": notes, "gold_role": role})
    member[rid] = {"tier": "GOLD_PENDING_INDEPENDENT_IAA", "annotation_status": "AI_DRAFT_HUMAN_REVIEWED_NOT_INDEPENDENT", "human_status": "HUMAN_REVIEWED_AI_DRAFT", "iaa": "PENDING_STEP_19_INDEPENDENT_REANNOTATION", "has_events": True, "has_states": True}


p20 = list(csv.DictReader(open(G / "gold_v1_pilot_manifest.csv")))
p7 = {r["recipe_id"] for r in csv.DictReader(open(G / "pilot_7_calibration_manifest.csv"))}
for r in p20:
    rid = a1.get(r["recipe_id"])
    if not rid:
        continue
    add(rid, "v1;v1.1", "ADJUDICATED(Kush+Parv; shared AI draft)", f"annotation/gold/pilot_20_adjudicated_v1_1/{r['recipe_id']}.ADJUDICATED.json", f"A1 recipe {r['recipe_id']}; stratum={r['stratum']}; gold_class={r['gold_class']}; {AI}" + ("; also in pilot_7 calibration set" if r["recipe_id"] in p7 else ""), "PILOT_DEV_GOLD")
fc = sorted(os.path.basename(p).split(".")[0] for p in glob.glob(str(G / "foodcom_ai_assisted/Kush/*.json")))
for fid in fc:
    add(fid, "v1;v1.1_joint", "Kush;Parv;JOINT(v1.1)", f"annotation/gold/foodcom_ai_assisted/Kush/{fid}.Kush.json;annotation/gold/foodcom_ai_assisted/Parv/{fid}.Parv.json;annotation/gold/foodcom_ai_assisted_v1_1/foodcom_v1_1_joint.json", f"Food.com recipe (local-only, not in REC); {AI}", "FOODCOM_AI_ASSISTED_GOLD")
sel = list(csv.DictReader(open(G / "evidence_first_expansion/selection_manifest_v1.csv")))
for r in sel:
    fam_override[r["source_recipe_id"]] = r["recipe_family"]
for fid in sorted({r["source_recipe_id"] for r in sel} - set(fc)):
    rows.append({"recipe_id": fid, "gold_status": "GOLD_CANDIDATE_SCREENED_NOT_ANNOTATED", "annotation_version": None, "annotators": None, "independent_annotation": False, "adjudicated": False, "iaa_available": False, "eligible_for_training": False,
                 "eligible_for_calibration": False, "eligible_for_test": False, "annotation_artifact_pointer": "annotation/gold/evidence_first_expansion/selection_manifest_v1.csv", "notes": "selected for Gold expansion, AI-screened (screening pending human confirm); no annotation yet; tier stays SOURCE_RAW", "gold_role": "EXPANSION_CANDIDATE"})
sch = [("recipe_id", pa.string()), ("gold_status", pa.string()), ("annotation_version", pa.string()), ("annotators", pa.string()), ("independent_annotation", pa.bool_()), ("adjudicated", pa.bool_()), ("iaa_available", pa.bool_()), ("eligible_for_training", pa.bool_()),
       ("eligible_for_calibration", pa.bool_()), ("eligible_for_test", pa.bool_()), ("annotation_artifact_pointer", pa.string()), ("notes", pa.string()), ("gold_role", pa.string())]
t = pa.table({n: pa.array([r.get(n) for r in rows], type=ty) for n, ty in sch})
(ROOT / "ledgers/recipe_base").mkdir(parents=True, exist_ok=True)
pq.write_table(t, ROOT / "ledgers/recipe_base/gold_recipe_index_v1.parquet", compression="zstd")
member["_family_override"] = fam_override
json.dump(member, open(ROOT / "reports/step07/_gold_membership.json", "w"), indent=1, sort_keys=True)
print(len(rows), "gold index rows;", sum(1 for k in member if not k.startswith("_")), "recipes with annotations; candidates", len(rows) - sum(1 for k in member if not k.startswith("_")))
