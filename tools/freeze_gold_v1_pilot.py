#!/usr/bin/env python3
"""D-017: freeze the pilot_20 Gold-v1 as an AI-assisted, human-reviewed development set.

  /opt/anaconda3/bin/python tools/freeze_gold_v1_pilot.py
Kush's set = AI draft converted to gold-1.0 (D-016), reviewed by Kush. Parv delegated his review to Kush (Kush's statement):
Parv's 20 files are the same content with annotator Parv, status DONE, and a note saying who actually reviewed. Because both
sets descend from one AI draft they are identical by construction: no inter-annotator agreement is computed or claimed, and
adjudication is vacuous (no disagreements). Writes annotation/gold/pilot_20_adjudicated/<id>.ADJUDICATED.json and the text-free
annotation/gold/gold_v1_pilot_manifest.csv. Refuses to overwrite a Parv file that contains independent work.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events, validate_gold  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

GOLD = ROOT / "annotation" / "gold"
PARV_NOTE = ("Parv delegated his review of this AI-assisted set to Kush, who checked it against Parv's list and reported it good "
             "(Kush's statement); Parv did not annotate independently. ")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    man = list(csv.DictReader((GOLD / "pilot_20_manifest.csv").open()))
    (GOLD / "pilot_20_adjudicated").mkdir(exist_ok=True)
    out = []
    for m in man:
        rid = m["recipe_id"]
        kp, pp = GOLD / "pilot_20" / "Kush" / f"{rid}.Kush.json", GOLD / "pilot_20" / "Parv" / f"{rid}.Parv.json"
        k, cur = json.loads(kp.read_text()), json.loads(pp.read_text())
        assert k["status"] == "DONE" and "AI_DRAFT_HUMAN_REVIEWED" in k["notes"]
        independent = any(l["spans"] for l in cur["ingredient_lines"]) and "AI_DRAFT_HUMAN_REVIEWED" not in cur.get("notes", "")
        if independent:
            sys.exit(f"{rid}: Parv file holds independent work - refusing to overwrite")
        pv = {**k, "annotator": "Parv", "notes": PARV_NOTE + k["notes"]}
        assert not validate_gold(pv) and not replay(to_events(pv)).issues
        pp.write_text(json.dumps(pv, indent=2, ensure_ascii=False) + "\n")
        adj = {**k, "annotator": "ADJUDICATED", "status": "DONE",
               "notes": "ADJUDICATION VACUOUS (D-017): Kush and Parv sets are identical (one shared AI draft), so there is no disagreement to resolve. " + k["notes"]}
        assert not validate_gold(adj)
        ap = GOLD / "pilot_20_adjudicated" / f"{rid}.ADJUDICATED.json"
        ap.write_text(json.dumps(adj, indent=2, ensure_ascii=False) + "\n")
        out.append({"recipe_id": rid, "family_id": m["family_id"], "stratum": m["stratum"],
                    "raw_content_sha256": m["raw_content_sha256"], "kush_sha256": sha(kp), "parv_sha256": sha(pp),
                    "adjudicated_sha256": sha(ap), "kush_status": "DONE", "parv_status": "DONE",
                    "adjudication_status": "VACUOUS_IDENTICAL_SETS", "handbook_version": m["handbook_version"],
                    "schema_version": m["schema_version"],
                    "provenance": "AI_ASSISTED_HUMAN_REVIEWED (OpenAI GPT-5.6 Sol draft; Kush reviewed; Parv's review delegated to Kush)",
                    "gold_class": "PILOT_DEV_GOLD_NOT_INDEPENDENT_NOT_A_TEST_SET"})
    with (GOLD / "gold_v1_pilot_manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(len(out), "recipes frozen as Gold-v1 pilot (AI-assisted)")


if __name__ == "__main__":
    main()
