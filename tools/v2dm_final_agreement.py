#!/usr/bin/env python3
"""Final CulinaryLinkDecision set: human annotation QC + agreement (rubric v2). No model scored, pool key NOT opened (strata come from the sampling frame). Never repairs labels.
  python tools/v2dm_final_agreement.py <kush.csv> <parv.csv>"""
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DC = "decision(MATCH:<n> | PARENT:<n> | NONE | AMBIGUOUS)"
NC, AC, CC = "if_NONE_ingredient_name", "acceptable_concepts(for AMBIGUOUS: ING-ids separated by ; or the word NONE)", "confidence(1-3)"
rd = lambda p: pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def cands(r):
    return {r[c].split(" | ")[0].strip() for c in r.index if c.startswith("cand_") and r[c]}


def validate(d, who):
    bad = []
    for _, r in d.iterrows():
        n = sum(1 for c in d.columns if c.startswith("cand_") and r[c] != "")
        v = r[DC].strip()
        m = re.fullmatch(r"(MATCH|PARENT):(\d+)", v)
        if not v:
            bad.append((who, r.item_id, "blank decision"))
        elif m:
            if not 1 <= int(m.group(2)) <= n:
                bad.append((who, r.item_id, f"index {m.group(2)} not in 1..{n}"))
        elif v == "NONE":
            if not r[NC].strip():
                bad.append((who, r.item_id, "NONE without ingredient name"))
        elif v == "AMBIGUOUS":
            toks = [x.strip() for x in r[AC].replace(",", ";").split(";") if x.strip()]
            ok = toks and all(t == "NONE" or t in cands(r) for t in toks)
            if not ok:
                bad.append((who, r.item_id, f"AMBIGUOUS acceptable_concepts missing/invalid: '{r[AC]}'"))
        else:
            bad.append((who, r.item_id, f"invalid decision '{v}'"))
        if r[CC].strip() not in ("1", "2", "3"):
            bad.append((who, r.item_id, f"confidence '{r[CC]}'"))
    return bad


def norm(r):
    v = r[DC].strip()
    m = re.fullmatch(r"(MATCH|PARENT):(\d+)", v)
    if m:
        return m.group(1), r[f"cand_{m.group(2)}"].split(" | ")[0].strip()
    if v == "AMBIGUOUS":
        return "AMBIGUOUS", frozenset(x.strip() for x in r[AC].replace(",", ";").split(";") if x.strip())
    return "NONE", None


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main(kp, pp):
    K, P = rd(kp), rd(pp)
    out = {"rows": [len(K), len(P)], "ids_identical_order": bool(len(K) == len(P) and (K.item_id.values == P.item_id.values).all()), "dups": [int(K.item_id.duplicated().sum()), int(P.item_id.duplicated().sum())],
           "byte_identical": h(kp) == h(pp)}
    out["candidate_columns_identical"] = bool(out["ids_identical_order"] and all((K[c] == P[c]).all() for c in K.columns if c.startswith("cand_") or c in ("mention", "context_line")))
    bad = validate(K, "Kush") + validate(P, "Parv")
    out["malformed_count"] = len(bad)
    out["malformed_by_annotator"] = dict(Counter(b[0] for b in bad))
    out["malformed_types"] = dict(Counter(b[2].split(":")[0].split("'")[0].strip() for b in bad).most_common(6))
    out["malformed_examples"] = bad[:8]
    if len(K) != 850 or len(P) != 850 or not out["ids_identical_order"] or any(out["dups"]) or out["byte_identical"] or bad:
        print(json.dumps(out, indent=1, default=str))
        return
    LK, LP = [norm(r) for _, r in K.iterrows()], [norm(r) for _, r in P.iterrows()]
    ck, cp = [x[0] for x in LK], [x[0] for x in LP]
    exact = [a == b for a, b in zip(LK, LP)]
    cls = [a == b for a, b in zip(ck, cp)]
    out.update({"exact_agreement": [int(sum(exact)), 850], "class_agreement": [int(sum(cls)), 850], "kappa_class": round(kappa(ck, cp), 4), "class_counts": {"Kush": dict(Counter(ck)), "Parv": dict(Counter(cp))},
                "confusion(Kush->Parv)": {f"{a}->{b}": n for (a, b), n in sorted(Counter(zip(ck, cp)).items())}})
    amb = [i for i in range(850) if ck[i] == cp[i] == "AMBIGUOUS"]
    out["ambiguous_both: identical acceptable sets / overlapping sets"] = [int(sum(LK[i][1] == LP[i][1] for i in amb)), int(sum(bool(LK[i][1] & LP[i][1]) for i in amb)), len(amb)]
    bm = [i for i in range(850) if ck[i] in ("MATCH", "PARENT") and cp[i] in ("MATCH", "PARENT")]
    out["concept_agreement_when_both_MATCH/PARENT"] = [int(sum(LK[i][1] == LP[i][1] for i in bm)), len(bm)]
    fr = [json.loads(l) for l in open(ROOT / "features/v2dm/final_link_frame.jsonl")]
    sk = pd.Series([r["stratum"].split("_")[0] for r in fr])
    out["by_stratum(from sampling frame)"] = {s: {"n": int((sk == s).sum()), "exact": int(sum(e for e, x in zip(exact, sk) if x == s)), "class": int(sum(c for c, x in zip(cls, sk) if x == s)),
                                                  "kappa": round(kappa([a for a, x in zip(ck, sk) if x == s], [b for b, x in zip(cp, sk) if x == s]), 3)} for s in sorted(set(sk))}
    conf = [(int(a), int(b)) for a, b in zip(K[CC], P[CC])]
    g = lambda a, b: "both_3" if a == b == 3 else "any_1" if min(a, b) == 1 else "any_2(no 1)"
    out["by_confidence"] = {k: {"n": sum(1 for a, b in conf if g(a, b) == k), "exact": sum(1 for i, (a, b) in enumerate(conf) if g(a, b) == k and exact[i])} for k in ("both_3", "any_2(no 1)", "any_1")}
    out["conf1_counts"] = {"Kush": int((K[CC] == "1").sum()), "Parv": int((P[CC] == "1").sum())}

    def kind(i):
        a, b = ck[i], cp[i]
        if exact[i]:
            return None
        if a == b == "MATCH":
            return "MATCH vs different MATCH"
        if a == b == "PARENT":
            return "different PARENT"
        if a == b == "AMBIGUOUS":
            return "AMBIGUOUS vs AMBIGUOUS (different sets)"
        if {a, b} == {"MATCH", "PARENT"}:
            return "MATCH vs PARENT (same concept)" if LK[i][1] == LP[i][1] else "MATCH vs PARENT (different concepts)"
        return " vs ".join(sorted({a, b}))
    dis = [i for i in range(850) if not exact[i]]
    out["n_requiring_adjudication"] = len(dis)
    out["disagreement_types"] = dict(Counter(kind(i) for i in dis).most_common())
    rng, rows = random.Random(20261021), []
    cc = [c for c in K.columns if c.startswith("cand_")]
    for i in dis:
        A, B = (P, K) if rng.random() < 0.5 else (K, P)
        note = lambda X: (X["note"][i] + (" | NONE name: " + X[NC][i] if X[NC][i] else "") + (" | acceptable: " + X[AC][i] if X[AC][i] else "")).strip(" |")
        rows.append({"item_id": K.item_id[i], "stratum": sk[i], "mention": K.mention[i], "context_line": K.context_line[i], **{c: K[c][i] for c in cc}, "annotator_A_decision": A[DC][i], "annotator_A_acceptable": A[AC][i],
                     "annotator_A_confidence": A[CC][i], "annotator_A_note": note(A), "annotator_B_decision": B[DC][i], "annotator_B_acceptable": B[AC][i], "annotator_B_confidence": B[CC][i], "annotator_B_note": note(B),
                     "agreement_type": kind(i), "final_adjudicated_decision": "", "final_if_NONE_ingredient_name": "", "final_acceptable_concepts(for AMBIGUOUS)": "", "adjudication_reason": "", "adjudicator_confidence": ""})
    pd.DataFrame(rows).to_csv(ROOT / "reports/ner_v2/final_link_adjudication.csv", index=False)
    try:
        pd.DataFrame(rows).to_csv(Path.home() / "Downloads/final_link_annotation/final_link_adjudication.csv", index=False)
    except OSError:
        pass
    pd.DataFrame({"item_id": K.item_id, "stratum": sk, "Kush_raw": K[DC], "Kush_class": ck, "Kush_concept_or_set": [sorted(x[1]) if isinstance(x[1], frozenset) else x[1] for x in LK], "Kush_conf": K[CC],
                  "Parv_raw": P[DC], "Parv_class": cp, "Parv_concept_or_set": [sorted(x[1]) if isinstance(x[1], frozenset) else x[1] for x in LP], "Parv_conf": P[CC], "exact_agree": exact, "class_agree": cls}).to_csv(ROOT / "reports/ner_v2/final_link_labels_normalised_PRE_ADJUDICATION.csv", index=False)
    (ROOT / "reports/ner_v2/final_link_annotation_manifest.json").write_text(json.dumps({"files_sha256": {Path(kp).name: h(kp), Path(pp).name: h(pp), "RUBRIC_V2_INSTRUCTIONS.md": h(Path(kp).parent / "RUBRIC_V2_INSTRUCTIONS.md"),
                                                                                                    "final_link_adjudication.csv": h(ROOT / "reports/ner_v2/final_link_adjudication.csv")}, "pool_key_opened": False, "models_scored": False}, indent=1))
    (ROOT / "reports/ner_v2/_final_link_agreement.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
