#!/usr/bin/env python3
"""D-126: score C_t v1.2.1 against the 50-context labels (gate fixed in DECISIONS.md D-126 before labelling).

    python tools/s179_d116_human_score.py --key data/raw/d116_human_check/key_SEALED.json \
        --labels ksh=data/raw/d116_human_check_ai/ksh/labels_ksh.csv prv=data/raw/d116_human_check_ai/prv/labels_prv.csv \
        --out reports/s179/d116_human_check_score_ai_2026-11-14.json
Output: counts, metrics and item ids only (no text).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

AXES = {"salt": "salt_in_contact", "acid": "acid_in_contact", "lipid": "lipid_in_contact",
        "aqueous": "water_liquid_contact"}
PREC_MIN, REC_MIN, MIN_DEN, SUG_MIN = 0.80, 0.60, 5, 0.60


def read_labels(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(l for l in fh if not l.startswith("# ")))
    out = {r["item"].strip(): {k: (v or "").strip().upper() for k, v in r.items()} for r in rows}
    if len(out) != 50:
        sys.exit(f"{path}: expected 50 items, got {len(out)}")
    return out


def kappa(a: list[str], b: list[str]) -> float | None:
    pairs = [(x, y) for x, y in zip(a, b) if x in "YN" and y in "YN" and x and y]
    if not pairs:
        return None
    po = sum(x == y for x, y in pairs) / len(pairs)
    pa, pb = sum(x == "Y" for x, _ in pairs) / len(pairs), sum(y == "Y" for _, y in pairs) / len(pairs)
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def score(key: list[dict], labels: dict[str, dict[str, dict]]) -> dict:
    (na, A), (nb, B) = list(labels.items())[:2]
    res = {"raters": [na, nb], "axes": {}, "failures": {}}
    passed = True
    for ax, col in AXES.items():
        tp = fp = fn = tn = 0
        fails = []
        for k in key:
            a, b = A[k["item"]][col], B[k["item"]][col]
            if a != b or a not in ("Y", "N"):
                continue
            pred = k["pred"][ax] is True
            gold = a == "Y"
            tp += pred and gold
            fp += pred and not gold
            fn += gold and not pred
            tn += (not pred) and (not gold)
            if pred != gold:
                fails.append(k["item"])
        prec = round(tp / (tp + fp), 3) if tp + fp else None
        rec = round(tp / (tp + fn), 3) if tp + fn else None
        judged = (tp + fp) >= MIN_DEN and (tp + fn) >= MIN_DEN
        ok = (prec >= PREC_MIN and rec >= REC_MIN) if judged else None
        passed &= ok is not False
        res["axes"][ax] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec, "recall": rec,
                           "consensus_n": tp + fp + fn + tn, "verdict": {True: "PASS", False: "FAIL", None: "INSUFFICIENT"}[ok],
                           "kappa_raters": kappa([A[k["item"]][col] for k in key], [B[k["item"]][col] for k in key])}
        res["failures"][ax] = fails
    sug = [k for k in key if (k["suggestion"] or {}).get("salt")]
    hit = den = 0
    for k in sug:
        a, b = A[k["item"]], B[k["item"]]
        va = "Y" if "Y" in (a["salt_in_contact"], a["salt_likely_but_unstated"]) else a["salt_likely_but_unstated"]
        vb = "Y" if "Y" in (b["salt_in_contact"], b["salt_likely_but_unstated"]) else b["salt_likely_but_unstated"]
        if va == vb and va in ("Y", "N"):
            den += 1
            hit += va == "Y"
    s_ok = (hit / den >= SUG_MIN) if den >= MIN_DEN else None
    passed &= s_ok is not False
    res["salt_suggestion"] = {"items": len(sug), "consensus_n": den, "supported": hit,
                              "share": round(hit / den, 3) if den else None,
                              "verdict": {True: "PASS", False: "FAIL", None: "INSUFFICIENT"}[s_ok]}
    res["gate"] = "PASS" if passed else "FAIL"
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--labels", nargs=2, required=True, help="name=path name=path")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    key = json.loads(Path(a.key).read_text())
    labels = {s.split("=", 1)[0]: read_labels(Path(s.split("=", 1)[1])) for s in a.labels}
    res = {"decision": "D-126", "status": "AI_DELEGATED_D085_NOT_HUMAN", "contains_text": False, **score(key, labels)}
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("gate", "salt_suggestion")}),
          {ax: (v["precision"], v["recall"], v["verdict"], v["kappa_raters"]) for ax, v in res["axes"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
