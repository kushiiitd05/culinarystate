#!/usr/bin/env python3
"""Step 19 P1 packet maker for ONE annotator (A = Kush, B = Parv). DRAFT_PENDING_H4.

  python tools/step19_packet_maker.py --letter B
Reads registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv (checked against its .sha256), takes the PRIMARY
recipes, reads their text from the local corpora and writes, outside git: annotation/gold/deep_gold_pilot_v1/<letter>/<packet>.json
(blank gold-1.0) and sealed_key_P1_<letter>.json. Tracked, text-free: packets_P1_<letter>.csv and sealed_key_P1_<letter>.sha256.
Refuses to overwrite anything. Run each letter on that annotator's own machine; never build both on one filesystem.
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation import pilot_packets as pp  # noqa: E402

TRACKED = ROOT / "registry/recipe_semantics/deep_gold_pilot_v1"
LOCAL = ROOT / "annotation/gold/deep_gold_pilot_v1"


def records(wanted):
    from culinarystate.recipes import corpus
    found = {}
    for it in (corpus.iter_rec_corpora(families=("A1_BBC_GOOD_FOOD", "WIKIBOOKS")), corpus.iter_foodcom()):
        for r in it:
            if r["recipe_id"] in wanted:
                found[r["recipe_id"]] = r
                if len(found) == len(wanted):
                    return found
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--letter", required=True, choices=sorted(pp.ANNOTATOR))
    a = ap.parse_args()
    manifest = TRACKED / "manifest_P1.csv"
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != (TRACKED / "manifest_P1.csv.sha256").read_text().split()[0]:
        raise SystemExit("manifest_P1.csv does not match its recorded sha256")
    rows = [r for r in csv.DictReader(manifest.open()) if r["role"] == "PRIMARY"]
    seed = rows[0]["seed_hex"]
    ids = [r["recipe_id"] for r in rows]
    recs = records(set(ids))
    packets, key = pp.build_packets(ids, recs, letter=a.letter, seed_hex=seed)
    outs = [LOCAL / a.letter / f"{p['packet_id']}.json" for p in packets]
    keyf = LOCAL / f"sealed_key_P1_{a.letter}.json"
    tracked = [TRACKED / f"packets_P1_{a.letter}.csv", TRACKED / f"sealed_key_P1_{a.letter}.sha256"]
    for p in outs + [keyf] + tracked:
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p.name}")
    (LOCAL / a.letter).mkdir(parents=True, exist_ok=True)
    for p, path in zip(packets, outs):
        path.write_text(json.dumps(p["doc"], indent=2, ensure_ascii=False) + "\n")
    keyf.write_text(json.dumps(key, indent=1, sort_keys=True) + "\n")
    rowsout = pp.manifest_rows(packets)
    with tracked[0].open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rowsout[0]))
        w.writeheader()
        w.writerows(rowsout)
    tracked[1].write_text(hashlib.sha256(keyf.read_bytes()).hexdigest() + "  sealed_key_P1_" + a.letter + ".json\n")
    print(json.dumps({"letter": a.letter, "packets": len(packets), "blank": all(pp.is_pristine(p["doc"]) for p in packets),
                      "recipes_found": len(recs), "outside_git": str(LOCAL.relative_to(ROOT))}))


main()
