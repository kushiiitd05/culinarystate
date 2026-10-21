#!/usr/bin/env python3
"""Fresh linker set: human annotation QC + agreement (no model scored, no pool key opened, no model provenance). Reports malformed rows (never repairs), normalises raw labels to canonical concept IDs (raw kept),
computes agreement/kappa and writes the blinded adjudication file (disagreements only; Kush/Parv randomly mapped to A/B per row).
  python tools/v2dm_fresh_agreement.py <kush.csv> <parv.csv>"""
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
NC, AC, CC = "if_NONE_ingredient_name", "if_AMBIGUOUS_readings", "confidence(1-3)"


def load(p):
    return pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def validate(d, who):
    bad = []
    cands = [c for c in d.columns if c.startswith("cand_")]
    for _, r in d.iterrows():
        n = sum(1 for c in cands if r[c] != "")
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
            if not r[AC].strip():
                bad.append((who, r.item_id, "AMBIGUOUS without readings"))
        else:
            bad.append((who, r.item_id, f"invalid decision '{v}'"))
        if r[CC].strip() not in ("1", "2", "3"):
            bad.append((who, r.item_id, f"confidence '{r[CC]}'"))
    return bad


def norm_label(r):
    v = r[DC].strip()
    m = re.fullmatch(r"(MATCH|PARENT):(\d+)", v)
    if m:
        cid = r[f"cand_{m.group(2)}"].split(" | ")[0].strip()
        return m.group(1), cid
    return v, None


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main(kp, pp):
    K, P = load(kp), load(pp)
    out = {"rows": [len(K), len(P)]}
    bad = validate(K, "Kush") + validate(P, "Parv")
    out["ids_identical_order"] = bool((K.item_id.values == P.item_id.values).all()) if len(K) == len(P) else False
    out["duplicate_ids"] = [int(K.item_id.duplicated().sum()), int(P.item_id.duplicated().sum())]
    out["candidate_columns_identical"] = bool(all((K[c] == P[c]).all() for c in K.columns if c.startswith("cand_") or c in ("mention", "context_line", "stratum"))) if out["ids_identical_order"] else None
    out["malformed"] = bad
    out["byte_identical"] = hashlib.sha256(open(kp, "rb").read()).hexdigest() == hashlib.sha256(open(pp, "rb").read()).hexdigest()
    if bad or len(K) != 441 or len(P) != 441 or not out["ids_identical_order"] or any(out["duplicate_ids"]) or out["byte_identical"]:
        print(json.dumps(out, indent=1))
        return out
    LK, LP = [norm_label(r) for _, r in K.iterrows()], [norm_label(r) for _, r in P.iterrows()]
    ck, cp = [x[0] for x in LK], [x[0] for x in LP]
    exact = [a == b for a, b in zip(LK, LP)]                          # same class and (for MATCH/PARENT) same concept; typed NONE names / AMBIGUOUS readings not compared
    cls = [a == b for a, b in zip(ck, cp)]
    conf = [(int(a), int(b)) for a, b in zip(K[CC], P[CC])]
    out["exact_agreement"] = [int(sum(exact)), len(K)]
    out["class_agreement"] = [int(sum(cls)), len(K)]
    out["kappa_class"] = round(kappa(ck, cp), 4)
    out["class_counts"] = {"Kush": dict(Counter(ck)), "Parv": dict(Counter(cp))}
    out["confusion_class(Kush->Parv)"] = {f"{a}->{b}": n for (a, b), n in sorted(Counter(zip(ck, cp)).items())}
    both_cp = [i for i in range(len(K)) if ck[i] in ("MATCH", "PARENT") and cp[i] in ("MATCH", "PARENT")]
    out["concept_level_agreement_when_both_MATCH/PARENT"] = [int(sum(LK[i][1] == LP[i][1] for i in both_cp)), len(both_cp)]
    both_m = [i for i in range(len(K)) if ck[i] == cp[i] == "MATCH"]
    both_p = [i for i in range(len(K)) if ck[i] == cp[i] == "PARENT"]
    out["same_concept_given_both_MATCH"] = [int(sum(LK[i][1] == LP[i][1] for i in both_m)), len(both_m)]
    out["same_concept_given_both_PARENT"] = [int(sum(LK[i][1] == LP[i][1] for i in both_p)), len(both_p)]
    sk = K.stratum.str.split("_").str[0]
    out["by_stratum"] = {s: {"n": int((sk == s).sum()), "exact": int(sum(e for e, x in zip(exact, sk) if x == s)), "class": int(sum(c for c, x in zip(cls, sk) if x == s)),
                              "kappa": (round(kappa([a for a, x in zip(ck, sk) if x == s], [b for b, x in zip(cp, sk) if x == s]), 3) if (sk == s).sum() > 5 else None)} for s in sorted(set(sk))}
    grp = lambda a, b: "both_3" if a == 3 and b == 3 else "any_1" if min(a, b) == 1 else "any_2(no 1)"
    g = {}
    for i, (a, b) in enumerate(conf):
        s = g.setdefault(grp(a, b), [0, 0, 0])
        s[0] += 1
        s[1] += exact[i]
        s[2] += cls[i]
    out["by_confidence_group"] = {k: {"n": v[0], "exact": v[1], "class": v[2]} for k, v in g.items()}
    out["low_confidence_rate"] = {"Kush_conf1": int((K[CC] == "1").sum()), "Parv_conf1": int((P[CC] == "1").sum()), "either_conf<=2": int(sum(1 for a, b in conf if min(a, b) <= 2)), "either_conf1": int(sum(1 for a, b in conf if min(a, b) == 1))}
    # disagreement categories (descriptive only)
    def kind(i):
        a, b, ca_, cb_ = ck[i], cp[i], LK[i][1], LP[i][1]
        if exact[i]:
            return None
        s = {a, b}
        if a == b == "MATCH":
            return "MATCH vs different MATCH"
        if a == b == "PARENT":
            return "different PARENT"
        if s == {"MATCH", "PARENT"}:
            return "MATCH vs PARENT (same concept)" if ca_ == cb_ else "MATCH vs PARENT (different concepts)"
        return " vs ".join(sorted(s))
    dis = [i for i in range(len(K)) if not exact[i]]
    out["n_requiring_adjudication"] = len(dis)
    out["disagreement_types"] = dict(Counter(kind(i) for i in dis).most_common())
    out["match_parent_boundary"] = {"MATCH vs PARENT same concept": sum(1 for i in dis if kind(i) == "MATCH vs PARENT (same concept)"), "MATCH vs PARENT different concepts": sum(1 for i in dis if kind(i) == "MATCH vs PARENT (different concepts)")}
    out["NONE_typed_names_differ_among_NONE_pairs"] = int(sum(1 for i in range(len(K)) if ck[i] == cp[i] == "NONE" and K[NC][i].strip().lower() != P[NC][i].strip().lower()))
    # adjudication file (blinded A/B)
    rng = random.Random(20261021)
    cands = [c for c in K.columns if c.startswith("cand_")]
    rows = []
    for i in dis:
        flip = rng.random() < 0.5
        A, B = (P, K) if flip else (K, P)
        row = {"item_id": K.item_id[i], "stratum": K.stratum[i], "mention": K.mention[i], "context_line": K.context_line[i], **{c: K[c][i] for c in cands},
               "annotator_A_decision": A[DC][i], "annotator_A_confidence": A[CC][i], "annotator_A_note": (A["note"][i] + (" | NONE name: " + A[NC][i] if A[NC][i] else "") + (" | readings: " + A[AC][i] if A[AC][i] else "")).strip(" |"),
               "annotator_B_decision": B[DC][i], "annotator_B_confidence": B[CC][i], "annotator_B_note": (B["note"][i] + (" | NONE name: " + B[NC][i] if B[NC][i] else "") + (" | readings: " + B[AC][i] if B[AC][i] else "")).strip(" |"),
               "agreement_type": kind(i), "final_adjudicated_decision": "", "final_if_NONE_ingredient_name": "", "final_if_AMBIGUOUS_readings": "", "adjudication_reason": "", "adjudicator_confidence": ""}
        rows.append(row)
    adj = pd.DataFrame(rows)
    adj.to_csv(ROOT / "reports/ner_v2/fresh_linker_adjudication.csv", index=False)
    dest = Path.home() / "Downloads/fresh_linker_annotation/fresh_linker_adjudication.csv"
    try:
        adj.to_csv(dest, index=False)
    except OSError:
        pass
    # normalised table (raw + canonical)
    norm = pd.DataFrame({"item_id": K.item_id, "stratum": K.stratum, "Kush_raw": K[DC], "Kush_class": ck, "Kush_concept": [x[1] for x in LK], "Kush_NONE_name": K[NC], "Kush_readings": K[AC], "Kush_conf": K[CC],
                         "Parv_raw": P[DC], "Parv_class": cp, "Parv_concept": [x[1] for x in LP], "Parv_NONE_name": P[NC], "Parv_readings": P[AC], "Parv_conf": P[CC], "exact_agree": exact, "class_agree": cls})
    norm.to_csv(ROOT / "reports/ner_v2/fresh_linker_labels_normalised_PRE_ADJUDICATION.csv", index=False)
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    man = {"files_sha256": {Path(kp).name: h(kp), Path(pp).name: h(pp), "RUBRIC_AND_INSTRUCTIONS.md": h(Path(kp).parent / "RUBRIC_AND_INSTRUCTIONS.md"),
                            "fresh_linker_adjudication.csv": h(ROOT / "reports/ner_v2/fresh_linker_adjudication.csv"), "fresh_linker_labels_normalised_PRE_ADJUDICATION.csv": h(ROOT / "reports/ner_v2/fresh_linker_labels_normalised_PRE_ADJUDICATION.csv")},
           "model_provenance_opened": False, "models_scored": False, "pool_key_opened": False}
    (ROOT / "reports/ner_v2/fresh_linker_annotation_manifest.json").write_text(json.dumps(man, indent=1))
    (ROOT / "reports/ner_v2/_fresh_linker_agreement.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
