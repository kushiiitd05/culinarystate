#!/usr/bin/env python3
"""Step 19 P1 packet maker for ONE annotator (A = Kush, B = Parv). DRAFT_PENDING_H4.

  python tools/step19_packet_maker.py --letter A --salt-file ~/.culinarystate_private/p1_salt_A.txt
  (make the salt once: python3 -c "import secrets;print(secrets.token_hex(32))" > that file; chmod 600 it)
Reads registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv (checked against its .sha256), takes the PRIMARY
recipes, reads their text from the local corpora and writes, outside git: annotation/gold/deep_gold_pilot_v1/<letter>/<packet>.json
(blank gold-1.0) and sealed_key_P1_<letter>.json. Tracked, text-free: packets_P1_<letter>.csv and sealed_key_P1_<letter>.sha256.
Refuses to overwrite anything. Run each letter on that annotator's own machine; never build both on one filesystem.
S164 (block J7): the order also uses the annotator's secret salt (file outside the repo; only its sha256 is tracked as
salt_P1_<letter>.sha256); refuses if the local folder is not git-ignored or the other letter's packets/key are present.
S166 (prv review P1-P3 of PR #8): tracked rows and the key hash are salted commitments sha256(salt | hash), so they
cannot link packets to the public recipe ids; per-packet line/step counts are no longer tracked; the other
annotator's salt is refused. Re-issue after an earlier build: first move the old local
annotation/gold/deep_gold_pilot_v1/<letter>/ folder and sealed_key_P1_<letter>.json out of the repository
(e.g. to ~/.culinarystate_private/superseded/), otherwise the tool refuses to overwrite them.
"""
import argparse
import csv
import hashlib
import json
import subprocess
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
    ap.add_argument("--salt-file", required=True, type=Path, help="private salt file outside the repo")
    ap.add_argument("--wave", default="P1", help="wave name; P1 keeps its original paths (S168)")
    a = ap.parse_args()
    try:
        salt = pp.read_salt(a.salt_file.expanduser(), repo_root=ROOT)
    except (OSError, pp.PacketError) as exc:
        raise SystemExit(f"salt: {exc}")
    try:
        w = pp.wave_paths(a.wave, a.letter, tracked=TRACKED, local=LOCAL)
    except pp.PacketError as exc:
        raise SystemExit(str(exc))
    problems = pp.independence_problems(w["local_dir"].parent, a.letter) + pp.salt_reuse_problems(
        salt, tracked_dir=TRACKED, letter=a.letter, wave=a.wave)
    for probe in (w["local_dir"] / "probe.json", w["key"]):
        if subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(probe)]).returncode != 0:
            problems.append(f"LOCAL_NOT_GIT_IGNORED: {probe.relative_to(ROOT)}")
    if problems:
        raise SystemExit("refusing: " + "; ".join(problems))
    manifest = w["manifest"]
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != w["manifest_sha"].read_text().split()[0]:
        raise SystemExit(f"{manifest.name} does not match its recorded sha256")
    rows = [r for r in csv.DictReader(manifest.open()) if r["role"] == "PRIMARY"]
    seed = rows[0]["seed_hex"]
    ids = [r["recipe_id"] for r in rows]
    recs = records(set(ids))
    packets, key = pp.build_packets(ids, recs, letter=a.letter, seed_hex=seed, salt_hex=salt)
    outs = [w["local_dir"] / f"{p['packet_id']}.json" for p in packets]
    keyf = w["key"]
    tracked = [w["packets_csv"], w["key_sha"], w["salt_sha"]]
    for p in outs + [keyf] + tracked:
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p.name}")
    w["local_dir"].mkdir(parents=True, exist_ok=True)
    for p, path in zip(packets, outs):
        path.write_text(json.dumps(p["doc"], indent=2, ensure_ascii=False) + "\n")
    keyf.write_bytes(pp.key_bytes(key))  # same bytes the salted key commitment hashes
    rowsout = pp.manifest_rows(packets, salt_hex=salt)
    with tracked[0].open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rowsout[0]))
        w.writeheader()
        w.writerows(rowsout)
    tracked[1].write_text(pp.key_commitment(key, salt_hex=salt) + f"  sealed_key_{a.wave}_" + a.letter
                          + ".json (salted: sha256(salt|sha256(key file)))\n")
    tracked[2].write_text(pp.salt_commitment(salt) + f"  salt_{a.wave}_" + a.letter + " (secret, outside git)\n")
    print(json.dumps({"letter": a.letter, "packets": len(packets), "blank": all(pp.is_pristine(p["doc"]) for p in packets),
                      "recipes_found": len(recs), "outside_git": str(LOCAL.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
