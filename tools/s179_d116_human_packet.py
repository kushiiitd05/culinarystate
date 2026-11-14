#!/usr/bin/env python3
"""D-116 T5: blind 50-context human check of C_t v1.2.1 (Kush = A, Parv = B label the same packet independently).

Pool: heat events x food members in WIKIBOOKS and GUTENBERG_SEGMENT (open-licence text only). Strata (10 each, one
item per recipe, deterministic by sha256(seed|recipe|event|food)): SALT_TRUE, ACID_TRUE, LIPID_TRUE, NONE_TRUE,
SUGGESTED (an unstated-context suggestion fires). Humans see the steps (the event's action marked >>like this<<) and
the food, never our flags. Our predictions go to a separate key file. Packet and key live under data/raw (git-ignored);
the committed manifest has hashes and counts only.

    python tools/s179_d116_human_packet.py --seed 20261114 --outdir data/raw/d116_human_check \
        --manifest reports/s179/d116_human_check_manifest_2026-11-14.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

FAMILIES = ("WIKIBOOKS", "GUTENBERG_SEGMENT")
STRATA = ("SALT_TRUE", "ACID_TRUE", "LIPID_TRUE", "NONE_TRUE", "SUGGESTED")
PER_STRATUM = 10
HUMAN_COLS = ["salt_in_contact", "acid_in_contact", "lipid_in_contact", "water_liquid_contact",
              "salt_likely_but_unstated", "notes"]
INSTRUCTIONS = ("For the FOOD at the step marked >>like this<<: is salt / an acid (vinegar, citrus juice, wine, "
                "tomato-based sauce counts as acid) / a fat or oil / water or a watery liquid IN CONTACT with it at that "
                "step? Answer Y, N or ? (cannot tell). salt_likely_but_unstated: Y if the text does not say salt here "
                "but a cook would very probably salt it at this point. Do not use any tool or model.")


def _h(*parts) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()


def candidates(rec, S):
    from culinarystate.composition import context_v12 as CV, router_v12 as RV, state as CS
    from culinarystate.extraction.interfaces import SourceText
    raw = "\n".join(str(s) for s in (rec.get("steps") or []))
    if not raw.strip():
        return
    rung, schema = S["rung"], S["schema"]
    parsed = rung.run(SourceText.from_raw("HP", raw), rung.config(), schema=schema)
    mem = CS.lot_members_v11(parsed.graph.entities)
    step_ings = set().union(*(m[0] for m in mem.values())) if mem else set()
    lines = [str(x) for x in (rec.get("ingredient_lines") or []) if str(x).strip()]
    list_ings = {a.value for e in (rung.run(SourceText.from_raw("HPL", "\n".join(lines)), rung.config(),
                                            schema=schema).graph.entities if lines else ())
                 for a in (e.attributes or ()) if a.field == "ingredient_id" and a.value}
    unplaced = RV.unplaced_from_list(list_ings, step_ings, S["marks"])
    for e in parsed.graph.events:
        proc = next((a.value for a in e.attributes if a.field == "proc_id"), None)
        if S["family"].get(proc) not in S["heat"] or not e.span.segments:
            continue
        ings = set()
        for c in e.consumes:
            ings |= mem.get(c, (frozenset(), False))[0]
        for food in sorted(i for i in ings if not (S["marks"].get(i) and S["roles"].get(i) == "MEDIUM")):
            ctx = CV.context_v12(food, list(e.consumes), mem, S["marks"], S["roles"], S["sr"], medium_type=None)
            sug = RV.suggest_context(ctx, unplaced, S["prior"].get(f"{food}|{proc}"))
            vals = {a: ctx[f"{a}_present"].get("v") for a in ("salt", "acid", "lipid", "aqueous")}
            strata = [f"{a.upper()}_TRUE" for a in ("salt", "acid", "lipid") if vals[a] is True]
            if not strata:
                strata.append("NONE_TRUE")
            if any(sug.values()):
                strata.append("SUGGESTED")
            s, t = e.span.segments[0]
            marked = raw[:s] + ">>" + raw[s:t] + "<<" + raw[t:]
            yield strata, {"recipe_id": rec["recipe_id"], "event_id": e.event_id, "family": rec.get("source_family"),
                           "food_id": food, "process_id": proc, "text": marked, "pred": vals,
                           "pred_phase": ctx["contact_phase"].get("v"), "suggestion": sug}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args(argv)
    outdir, man = Path(a.outdir), Path(a.manifest)
    if outdir.exists() or man.exists():
        sys.exit("refusing to overwrite packet or manifest")
    import s179_context_prior as CP
    from culinarystate.lotstate import corpus as C
    S = CP._setup()
    S["heat"] = CP.HEAT_FAMILIES
    S["prior"] = json.loads((ROOT / "reports/s179/context_prior_v2_full_2026-11-14.json").read_text())["prior"]
    names = {}
    for line in (ROOT / "ledgers/data/ING.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            names[r["id"]] = r["canonical_name"]
    best: dict[str, list] = {s: [] for s in STRATA}
    for rec in C.stream(FAMILIES, ROOT):
        try:
            for strata, item in candidates(rec, S):
                key = _h(a.seed, item["recipe_id"], item["event_id"], item["food_id"])
                for st in strata:
                    best[st].append((key, item))
                    if len(best[st]) > 400:
                        best[st] = sorted(best[st], key=lambda x: x[0])[:200]
        except Exception:
            continue
    chosen, used = [], set()
    for st in STRATA:
        k = 0
        for key, item in sorted(best[st], key=lambda x: x[0]):
            if item["recipe_id"] in used:
                continue
            chosen.append((st, key, item))
            used.add(item["recipe_id"])
            k += 1
            if k == PER_STRATUM:
                break
    chosen.sort(key=lambda x: x[1])                                   # stratum order hidden from labellers
    outdir.mkdir(parents=True)
    rows, key_rows = [], []
    for n, (st, _, it) in enumerate(chosen, 1):
        iid = f"H{n:02d}"
        rows.append({"item": iid, "food": names.get(it["food_id"], it["food_id"]), "steps": it["text"],
                     **{c: "" for c in HUMAN_COLS}})
        key_rows.append({"item": iid, "stratum": st, **{k: it[k] for k in ("recipe_id", "event_id", "family", "food_id",
                                                                         "process_id")},
                         "pred": it["pred"], "pred_phase": it["pred_phase"], "suggestion": it["suggestion"]})
    for who in ("A_kush", "B_parv"):
        with (outdir / f"packet_{who}.csv").open("x", newline="", encoding="utf-8") as f:
            f.write("# " + INSTRUCTIONS + "\n")
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    (outdir / "key_SEALED.json").write_text(json.dumps(key_rows, indent=1))
    digest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(outdir.iterdir())}
    man.write_text(json.dumps({"tool": "s179_d116_human_packet", "seed": a.seed, "families": FAMILIES,
                               "per_stratum": PER_STRATUM, "n_items": len(rows),
                               "strata": {s: sum(r["stratum"] == s for r in key_rows) for s in STRATA},
                               "sha256": digest, "contains_text": False, "human_cols": HUMAN_COLS,
                               "status": "ISSUED_NOT_LABELLED"}, indent=1))
    print(len(rows), {s: sum(r["stratum"] == s for r in key_rows) for s in STRATA})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
