#!/usr/bin/env python3
"""Fresh linker gold: merge two independent human annotations + human adjudication into ONE final gold file (never touches model outputs or the pool key).
  python tools/v2dm_fresh_gold_build.py <kush.csv> <parv_final.csv> <adjudication_completed.csv>
Output (local, git-ignored because it carries recipe-derived mention text): annotation/gold/fresh_linker_set/FRESH_LINKER_GOLD_FINAL.csv ; committed: reports/ner_v2/FRESH_LINKER_GOLD_FREEZE_MANIFEST.json (hashes, counts, provenance).
Rules: agreed rows keep the agreed label; disagreed rows take final_adjudicated_decision (same syntax: MATCH:<n> / PARENT:<n> / NONE / AMBIGUOUS, n indexes that row's cand columns). Both original annotations and the adjudication record are preserved as columns.
No label is inferred or repaired; any invalid/blank adjudication on a disagreed row stops the build."""
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DC = "decision(MATCH:<n> | PARENT:<n> | NONE | AMBIGUOUS)"
NC, AC, CC = "if_NONE_ingredient_name", "if_AMBIGUOUS_readings", "confidence(1-3)"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def rd(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def resolve(dec, row):
    m = re.fullmatch(r"(MATCH|PARENT):(\d+)", dec.strip())
    if m:
        cell = row.get(f"cand_{m.group(2)}", "")
        if not cell:
            raise SystemExit(f"{row['item_id']}: candidate index {m.group(2)} does not exist")
        return m.group(1), cell.split(" | ")[0].strip()
    if dec.strip() in ("NONE", "AMBIGUOUS"):
        return dec.strip(), None
    raise SystemExit(f"{row['item_id']}: invalid decision '{dec}'")


def main(kp, pp, ap):
    K, P, A = rd(kp), rd(pp), rd(ap)
    assert len(K) == len(P) == 441 and (K.item_id.values == P.item_id.values).all(), "annotator files must have 441 aligned rows"
    adj = {r.item_id: r for r in A.itertuples(index=False)} if False else {r["item_id"]: r for _, r in A.iterrows()}
    rows, n_adj = [], 0
    for i in range(len(K)):
        k, p = K.iloc[i], P.iloc[i]
        ck, cp = resolve(k[DC], k), resolve(p[DC], p)
        agree = ck == cp
        rec = {"item_id": k.item_id, "stratum": k.stratum, "dataset": k.dataset, "mention": k.mention, "context_line": k.context_line, **{c: k[c] for c in K.columns if c.startswith("cand_")},
               "kush_raw": k[DC], "kush_class": ck[0], "kush_concept": ck[1], "kush_NONE_name": k[NC], "kush_readings": k[AC], "kush_conf": k[CC], "kush_note": k["note"],
               "parv_raw": p[DC], "parv_class": cp[0], "parv_concept": cp[1], "parv_NONE_name": p[NC], "parv_readings": p[AC], "parv_conf": p[CC], "parv_note": p["note"], "human_agreed": agree}
        if agree:
            fin, src = ck, "AGREED_INDEPENDENT"
            rec.update(final_NONE_name=k[NC] or p[NC], final_readings=k[AC] or p[AC], adjudication_reason="", adjudicator_confidence="")
        else:
            a = adj.get(k.item_id)
            if a is None or not str(a["final_adjudicated_decision"]).strip():
                raise SystemExit(f"{k.item_id}: disagreement without a completed adjudication")
            candrow = {c: a[c] for c in A.columns if c.startswith("cand_")}
            candrow["item_id"] = k.item_id
            fin, src = resolve(a["final_adjudicated_decision"], candrow), "HUMAN_ADJUDICATED"
            rec.update(final_NONE_name=a["final_if_NONE_ingredient_name"], final_readings=a["final_if_AMBIGUOUS_readings"], adjudication_reason=a["adjudication_reason"], adjudicator_confidence=a["adjudicator_confidence"])
            n_adj += 1
        rec.update(final_class=fin[0], final_concept=fin[1], final_source=src, provenance="HUMAN_INDEPENDENT_DOUBLE_ANNOTATED + HUMAN_ADJUDICATED")
        rows.append(rec)
    G = pd.DataFrame(rows)
    assert G.item_id.is_unique and len(G) == 441
    out = ROOT / "annotation/gold/fresh_linker_set/FRESH_LINKER_GOLD_FINAL.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    G.to_csv(out, index=False)
    man = {"name": "FRESH_LINKER_GOLD", "provenance": "HUMAN_INDEPENDENT_DOUBLE_ANNOTATED + HUMAN_ADJUDICATED (no AI-generated label)", "n_items": len(G), "n_unique_item_ids": int(G.item_id.nunique()), "n_agreed_independent": int((G.final_source == "AGREED_INDEPENDENT").sum()),
           "n_human_adjudicated": n_adj, "final_class_counts": G.final_class.value_counts().to_dict(), "by_stratum": G.groupby(G.stratum.str.split("_").str[0]).final_class.value_counts().unstack(fill_value=0).to_dict("index"),
           "files_sha256": {Path(kp).name: h(kp), Path(pp).name: h(pp), Path(ap).name: h(ap), "FRESH_LINKER_GOLD_FINAL.csv": h(out), "RUBRIC_AND_INSTRUCTIONS.md": h(Path(kp).parent / "RUBRIC_AND_INSTRUCTIONS.md"),
                            "fresh_linker_annotation_manifest.json": h(ROOT / "reports/ner_v2/fresh_linker_annotation_manifest.json")},
           "pool_key_opened_before_this_manifest": False, "models_scored_before_this_manifest": False}
    (ROOT / "reports/ner_v2/FRESH_LINKER_GOLD_FREEZE_MANIFEST.json").write_text(json.dumps(man, indent=1))
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
