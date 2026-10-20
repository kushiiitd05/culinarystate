#!/usr/bin/env python3
"""S116 coverage forecast B: for the 20 Gold-v1.1 recipes, which (ingredient, process) states have NO retention cell, and how many
valid cuts / recipes would each new cell unlock?  Gold state only; no system output.
  /opt/anaconda3/bin/python tools/hstate_missing_cells.py   -> reports/h_state/missing_cells_gold20.csv
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from build_hstate_r_candidates import GOLD  # noqa: E402
from culinarystate.state_graph.prefix_state import prefix_state  # noqa: E402
from culinarystate.annotation.gold import to_events  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.state_graph.engine import Add, replay  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402


THERMAL_FAMS = {"DRY_HEAT", "WET_HEAT", "FAT_HEAT"}


def main():
    st = LedgerStore()
    ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    iname = {v: k for k, v in ing.items()}
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    pfam = {p["id"]: (p["canonical_name"], p.get("family")) for p in st.all_latest("PROC")}
    have, anyevd = set(), set()
    for e in st.all_latest("EVD"):
        i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if e["status"] != "ACTIVE" or not (i and p):
            continue
        anyevd.add((i, p))
        if (e.get("derived") or {}).get("retention_factor"):
            have.add((i, p))
    have_fam = {(i, pfam[p][1]) for (i, p) in have if p in pfam}
    seen_pairs = defaultdict(set)                                   # (recipe, ing, proc) -> kinds: EXACT | FAMILY | NONE (thermal only)
    miss = defaultdict(lambda: {"cuts": set(), "recipes": set()})
    unlinked = 0
    for f in sorted(GOLD.glob("*.ADJUDICATED.json")):
        d = json.loads(f.read_text())
        rid, ev = d["recipe_id"], to_events(d)
        concept = {l["entity"]: l["concept"] for l in d["ingredient_lines"]}
        adds = {e.label for e in ev if isinstance(e, Add)}
        idx = [i for i, e in enumerate(ev) if not isinstance(e, Add)]
        for n in range(1, len(idx)):
            k = idx[n - 1] + 1
            g = replay(ev[:k])
            alive = [a for a in g.alive() if a not in adds]
            anc, procs, _, _ = prefix_state(ev, k, concept)
            for ent in alive:
                for b in anc.get(ent, {ent}):
                    iid = ing.get(norm(concept.get(b, "")))
                    for pr in procs.get(ent, set()):
                        pid = proc.get(pr)
                        if not pid:
                            continue
                        if not iid:
                            unlinked += 1
                            continue
                        if pfam[pid][1] in THERMAL_FAMS:
                            kind = "EXACT" if (iid, pid) in have else "FAMILY" if (iid, pfam[pid][1]) in have_fam else "NONE"
                            seen_pairs[(rid, iid, pid)].add(kind)
                        if (iid, pid) not in have:
                            m = miss[(iid, pid)]
                            m["cuts"].add((rid, k))
                            m["recipes"].add(rid)
    rows = [{"ingredient_id": i, "ingredient": iname.get(i, ""), "process_id": p, "process": pfam[p][0], "process_family": pfam[p][1], "recipes_unlocked": len(m["recipes"]),
             "cuts_unlocked": len(m["cuts"]), "has_non_retention_evd": int((i, p) in anyevd)} for (i, p), m in miss.items()]
    rows.sort(key=lambda r: (-r["recipes_unlocked"], -r["cuts_unlocked"], r["ingredient_id"]))
    out = ROOT / "reports" / "h_state" / "missing_cells_gold20.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "missing cells;", "unlinked-concept states skipped:", unlinked)
    detail = {f"{i}|{p}": {"recipes": sorted(m["recipes"]), "cuts": sorted(f"{r}:{k}" for r, k in m["cuts"])} for (i, p), m in miss.items()}
    (ROOT / "reports" / "h_state" / "missing_cells_gold20_detail.json").write_text(json.dumps(detail))
    kinds = {"EXACT": 0, "FAMILY": 0, "NONE": 0}
    for ks in seen_pairs.values():
        kinds["EXACT" if "EXACT" in ks else "FAMILY" if "FAMILY" in ks else "NONE"] += 1
    print("Gold thermal (recipe,ingredient,process) pairs at any cut:", sum(kinds.values()), kinds,
          "| recipes with an EXACT pair:", len({k[0] for k, v in seen_pairs.items() if "EXACT" in v}),
          "| recipes with EXACT or FAMILY pair:", len({k[0] for k, v in seen_pairs.items() if v & {"EXACT", "FAMILY"}}))
    thermal = [r for r in rows if r["process_family"] in ("DRY_HEAT", "WET_HEAT", "FAT_HEAT", "HEAT_GENERAL")]
    left, got = {(r["ingredient_id"], r["process_id"]): r for r in thermal}, 0
    print("thermal-process missing cells:", len(thermal), "(non-thermal = mix/add/chop etc.: no retention evidence is meaningful)")
    for r in thermal[:15]:
        print(r)
    tot = sum(r["recipes_unlocked"] for r in thermal)
    print("total (recipe,cell) pairs unlockable by ALL thermal cells:", tot)


if __name__ == "__main__":
    main()
