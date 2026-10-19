#!/usr/bin/env python3
"""S108: apply ONLY the corrections Kush approved in annotation/gold/gold_v1_correction_queue.csv -> Gold-v1.1.

  /opt/anaconda3/bin/python tools/apply_gold_corrections.py            # approved rows only -> pilot_20_adjudicated_v1_1/
decision column values that count as approval: approve | approved | accept (case-insensitive). Anything else, including an
empty cell, is NOT applied. Every resulting file must pass validate + replay; otherwise nothing is written (a partial approval
can break a dependency, e.g. approving a step that renames an entity a later step uses - the error says which).
Gold-v1 (pilot_20_adjudicated) is never modified. Provenance: AI-assisted + human-reviewed development Gold.
"""
import copy
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events, validate_gold  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

APPROVE = {"approve", "approved", "accept"}


def apply(gold_dir: Path, queue: Path, out_dir: Path, today: str = "2026-10-19",
          base_manifest: Path | None = None, out_manifest: Path | None = None) -> tuple[int, list[str]]:
    docs = {p.name.split(".")[0]: json.loads(p.read_text()) for p in sorted(gold_dir.glob("*.ADJUDICATED.json"))}
    sel = [r for r in csv.DictReader(queue.open()) if r["decision"].strip().lower() in APPROVE
           and json.loads(r["patch_json"]).get("op") not in (None, "none")]
    new, seen, errs = copy.deepcopy(docs), {}, []
    for r in sel:
        p = json.loads(r["patch_json"])
        key = (p["recipe"], p.get("step"), p["op"], p.get("start") if p["op"] == "set_coref" else p.get("line"))
        if key in seen:
            errs.append(f"{r['item_id']} conflicts with {seen[key]} (same target)")
            continue
        seen[key] = r["item_id"]
        if p["op"] == "replace_events":
            new[p["recipe"]]["steps"][p["step"]]["events"] = p["events"]
        elif p["op"] == "set_coref":
            for c in new[p["recipe"]]["steps"][p["step"]]["coref"]:
                if c["start"] == p["start"]:
                    c["entity"] = p["entity"]
        elif p["op"] == "drop_coref":
            st = new[p["recipe"]]["steps"][p["step"]]
            st["coref"] = [c for c in st["coref"] if c["start"] not in p["starts"]]
        elif p["op"] == "set_line_alt":
            ln = new[p["recipe"]]["ingredient_lines"][p["line"]]
            ln["alternatives"] = p["alternatives"]
            ln["spans"] = sorted([x for x in ln["spans"] if x["label"] != "ALTERNATIVE"] + p["spans"], key=lambda x: (x["start"], x["end"]))
    changed = {k[0] for k in seen}
    if not changed and not errs:
        return 0, []                                   # nothing approved: write nothing
    for rid in changed:
        d = {**new[rid], "status": "DONE"}
        e = validate_gold(d)
        iss = [] if e else list(replay(to_events(d)).issues)
        if e or iss:
            errs.append(f"{rid}: {(e or iss)[0]}")
    if errs:
        return 0, errs
    out_dir.mkdir(exist_ok=True)
    ids = {rid: [r["item_id"] for r in sel if json.loads(r["patch_json"])["recipe"] == rid] for rid in changed}
    for rid, d in new.items():
        if rid in changed:
            d = {**d, "notes": f"GOLD-v1.1 (S108): corrections {', '.join(ids[rid])} approved by Kush {today}; AI-assisted + human-reviewed "
                               f"development Gold, not independent. " + d.get("notes", "")}
        (out_dir / f"{rid}.ADJUDICATED.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    if base_manifest is None:
        return len(changed), []                        # library/test use: no manifest
    man = out_manifest
    base = {r["recipe_id"]: r for r in csv.DictReader(base_manifest.open())}
    with man.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["recipe_id", "family_id", "stratum", "raw_content_sha256", "gold_v1_sha256", "gold_v1_1_sha256",
                    "approved_correction_ids", "handbook_version", "schema_version", "provenance", "gold_class"])
        for rid in sorted(new):
            f = out_dir / f"{rid}.ADJUDICATED.json"
            b = base[rid]
            w.writerow([rid, b["family_id"], b["stratum"], b["raw_content_sha256"], b["adjudicated_sha256"],
                        hashlib.sha256(f.read_bytes()).hexdigest(), ";".join(ids.get(rid, [])), b["handbook_version"],
                        b["schema_version"], "AI-assisted + human-reviewed development Gold (corrections approved by Kush)",
                        "PILOT_DEV_GOLD_NOT_INDEPENDENT_NOT_A_TEST_SET"])
    return len(changed), []


def main():
    g = ROOT / "annotation" / "gold"
    n, errs = apply(g / "pilot_20_adjudicated", g / "gold_v1_correction_queue.csv", g / "pilot_20_adjudicated_v1_1",
                    base_manifest=g / "gold_v1_pilot_manifest.csv", out_manifest=g / "gold_v1_1_pilot_manifest.csv")
    if errs:
        print("NOT WRITTEN:", *errs, sep="\n  ")
        return 1
    print(f"Gold-v1.1 written: {n} recipes changed; manifest annotation/gold/gold_v1_1_pilot_manifest.csv" if n else
          "no approved corrections found (decision column empty): nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
