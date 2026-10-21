#!/usr/bin/env python3
"""Final CulinaryLinkDecision gold: merge two independent human annotations + human adjudication (rubric v2). Fail-closed; never scores a model, never opens the pool key.
Agreed rows (exact label agreement) keep the shared label; every other row takes the adjudicated label. AMBIGUOUS sets may contain NONE as a member (decision 1, 2026-10-21).
  python tools/v2dm_final_gold_build.py <kush.csv> <parv.csv> <adjudication_FILLED.csv>"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v2dm_final_agreement import AC, CC, DC, NC, norm, rd, validate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "annotation/gold/final_link_set/FINAL_LINK_GOLD.csv"
ADC, ADN, ADA = "final_adjudicated_decision", "final_if_NONE_ingredient_name", "final_acceptable_concepts(for AMBIGUOUS)"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def cid(r, n):
    return r[f"cand_{n}"].split(" | ")[0].strip()


def adjudicated(a, K_row):
    v = a[ADC].strip()
    m = re.fullmatch(r"(MATCH|PARENT):(\d+)", v)
    if m:
        n = int(m.group(2))
        assert K_row.get(f"cand_{n}", "") != "", (a.item_id, "index out of range")
        assert a[f"cand_{n}"] == K_row[f"cand_{n}"], (a.item_id, "candidate mismatch")
        return m.group(1), cid(K_row, n), []
    if v == "NONE":
        assert a[ADN].strip(), (a.item_id, "NONE without name")
        return "NONE", "", []
    assert v == "AMBIGUOUS", (a.item_id, v)
    toks = [x.strip() for x in a[ADA].replace(",", ";").split(";") if x.strip()]
    ids = {cid(K_row, n) for n in range(1, 40) if K_row.get(f"cand_{n}", "")}
    assert toks and all(t == "NONE" or t in ids for t in toks), (a.item_id, "bad acceptable set", toks)
    return "AMBIGUOUS", "", sorted(set(toks))


def main(kp, pp, ap):
    K, P, A = rd(kp), rd(pp), rd(ap)
    assert not validate(K, "Kush") and not validate(P, "Parv"), "annotation files invalid"
    assert len(K) == len(P) == 850 and (K.item_id.values == P.item_id.values).all() and K.item_id.is_unique
    LK, LP = [norm(r) for _, r in K.iterrows()], [norm(r) for _, r in P.iterrows()]
    dis = [K.item_id[i] for i in range(850) if LK[i] != LP[i]]
    assert A.item_id.is_unique and sorted(A.item_id) == sorted(dis), "adjudication rows != disagreement set"
    adj = A.set_index("item_id")
    frame = {json.loads(l)["mention"]: json.loads(l) for l in open(ROOT / "features/v2dm/final_link_frame.jsonl")}
    rows = []
    for i, (_, k) in enumerate(K.iterrows()):
        iid = k.item_id
        if iid in adj.index:
            a = adj.loc[iid].copy()
            a["item_id"] = iid
            cls, con, st = adjudicated(a, k)
            prov = "HUMAN_ADJUDICATED"
        else:
            cls, x = LK[i]
            con = x if cls in ("MATCH", "PARENT") else ""
            st = sorted(x) if cls == "AMBIGUOUS" else []
            prov = "HUMAN_AGREED"
        fr = frame[k.mention]
        rows.append({"item_id": iid, "stratum": fr["stratum"].split("_")[0], "dataset": fr["dataset"], "split": fr["split"], "mention": k.mention, "context_line": k.context_line, "final_class": cls, "final_concept": con,
                     "final_acceptable_set": ";".join(st), "provenance": prov, "kush_decision": k[DC], "parv_decision": P[DC][i], "kush_conf": k[CC], "parv_conf": P[CC][i],
                     **{c: k[c] for c in K.columns if c.startswith("cand_")}})
    G = pd.DataFrame(rows)
    assert len(G) == 850 and G.item_id.is_unique and G.final_class.isin(["MATCH", "PARENT", "NONE", "AMBIGUOUS"]).all()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    G.to_csv(OUT, index=False)
    man = {"gold_rows": 850, "class_counts": G.final_class.value_counts().to_dict(), "provenance_counts": G.provenance.value_counts().to_dict(),
           "ambiguous_sets_containing_NONE": int(sum("NONE" in s.split(";") for s in G.final_acceptable_set if s)),
           "files_sha256": {Path(kp).name: h(kp), Path(pp).name: h(pp), Path(ap).name: h(ap), "FINAL_LINK_GOLD.csv": h(OUT), "RUBRIC_V2_INSTRUCTIONS.md": h(Path(kp).parent / "RUBRIC_V2_INSTRUCTIONS.md")},
           "provenance": "HUMAN_INDEPENDENT_DOUBLE_ANNOTATED + HUMAN_ADJUDICATED (adjudicator attests human decisions; adjudication_reason text is templated; summary counts were AI-tallied only)",
           "scoring_rule_decided_before_scoring": "AMBIGUOUS acceptable set may contain NONE as a member: system answer NONE or any listed id is acceptable",
           "pool_key_opened": False, "models_scored": False}
    (ROOT / "reports/ner_v2/FINAL_LINK_GOLD_FREEZE_MANIFEST.json").write_text(json.dumps(man, indent=1))
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
