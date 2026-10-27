"""Step 07I-C: agreement between two blind reviewers on the 400-pair packet.

Follows THR-07IC-01..04 (registry/preregistered_thresholds_v1.csv). Read-only:
never edits a label, never opens the sealed key. Usage:
  python tools/step07ic_agreement.py A.csv B.csv OUT.json
"""
from __future__ import annotations

import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

LABELS = (
    "SAME_RECIPE_COPY",
    "SAME_RECIPE_MINOR_VARIANT",
    "SAME_DISH_DIFFERENT_RECIPE",
    "RELATED",
    "DISTINCT",
    "UNCERTAIN",
)
COPY_POS = {"SAME_RECIPE_COPY", "SAME_RECIPE_MINOR_VARIANT"}
DISH_POS = COPY_POS | {"SAME_DISH_DIFFERENT_RECIPE"}
KAPPA_TARGET = 0.70  # THR-07IC-04


def load(path: str) -> dict[str, str]:
    raw = Path(path).read_text(encoding="utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    return {r["pair_id"]: r["label"].strip() for r in rows}


def y_copy(label: str) -> int:
    return int(label in COPY_POS)


def y_dish(label: str, related_positive: bool = False) -> int:
    return int(label in DISH_POS or (related_positive and label == "RELATED"))


def cohen_kappa(a: list[int], b: list[int]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe == 1:
        return None  # both reviewers constant and equal: undefined
    return (po - pe) / (1 - pe)


def gwet_ac1(a: list[int], b: list[int]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pi = (sum(a) + sum(b)) / (2 * n)
    pe = 2 * pi * (1 - pi)
    if pe == 1:
        return None
    return (po - pe) / (1 - pe)


def binary_stats(ya: list[int], yb: list[int]) -> dict:
    n = len(ya)
    return {
        "n": n,
        "raw_agreement": (sum(x == y for x, y in zip(ya, yb)) / n) if n else None,
        "cohen_kappa": cohen_kappa(ya, yb),
        "gwet_ac1": gwet_ac1(ya, yb),
        "positives_A": sum(ya),
        "positives_B": sum(yb),
    }


def target_block(A: dict[str, str], B: dict[str, str], mapper) -> dict:
    ids = sorted(A)
    keep = [i for i in ids if A[i] != "UNCERTAIN" and B[i] != "UNCERTAIN"]
    ya, yb = [mapper(A[i]) for i in keep], [mapper(B[i]) for i in keep]
    out = binary_stats(ya, yb)
    out["pairs_excluded_uncertain_either"] = len(ids) - len(keep)
    # best/worst case: every UNCERTAIN cell (either reviewer) set to all-positive / all-negative
    for name, val in (("all_uncertain_positive", 1), ("all_uncertain_negative", 0)):
        za = [val if A[i] == "UNCERTAIN" else mapper(A[i]) for i in ids]
        zb = [val if B[i] == "UNCERTAIN" else mapper(B[i]) for i in ids]
        s = binary_stats(za, zb)
        out[name] = {"cohen_kappa": s["cohen_kappa"], "gwet_ac1": s["gwet_ac1"], "raw_agreement": s["raw_agreement"]}
    k = out["cohen_kappa"]
    out["meets_kappa_target"] = None if k is None else k >= KAPPA_TARGET
    return out


def compare(A: dict[str, str], B: dict[str, str]) -> dict:
    if set(A) != set(B):
        raise ValueError("pair_id sets differ")
    for name, d in (("A", A), ("B", B)):
        bad = {v for v in d.values() if v not in LABELS}
        if bad:
            raise ValueError(f"reviewer {name} has labels outside the six allowed: {sorted(bad)}")
    ids = sorted(A)
    six = sum(A[i] == B[i] for i in ids) / len(ids)
    out = {
        "n_pairs": len(ids),
        "six_class_raw_agreement": six,
        "Y_copy": target_block(A, B, y_copy),
        "Y_dish_primary_related_is_0": target_block(A, B, y_dish),
        "Y_dish_sensitivity_related_is_1": target_block(A, B, lambda x: y_dish(x, related_positive=True)),
        "label_counts_A": dict(Counter(A.values())),
        "label_counts_B": dict(Counter(B.values())),
        "six_class_confusion": [[list(k), v] for k, v in Counter((A[i], B[i]) for i in ids).most_common()],
        "disagreeing_pair_ids": [
            {"pair_id": i, "A": A[i], "B": B[i]} for i in ids if A[i] != B[i]
        ],
        "binary_disagreement_pair_ids_Y_copy": [
            i for i in ids if "UNCERTAIN" not in (A[i], B[i]) and y_copy(A[i]) != y_copy(B[i])
        ],
        "note": (
            "UNCERTAIN pairs are excluded from kappa and reported with best/worst-case bounds (THR-07IC-03). "
            "CONTRACT-AMBIGUITY: THR-07IC-04 does not say whether the 0.70 target applies to Y_copy, Y_dish or both; "
            "both are reported and no pass/fail is declared here. Nothing is adjudicated automatically."
        ),
    }
    return out


def main(a_path: str, b_path: str, out_path: str) -> int:
    res = compare(load(a_path), load(b_path))
    Path(out_path).write_text(json.dumps(res, indent=1))
    brief = {
        "n_pairs": res["n_pairs"],
        "six_class_raw_agreement": res["six_class_raw_agreement"],
        "Y_copy": {k: res["Y_copy"][k] for k in ("n", "raw_agreement", "cohen_kappa", "gwet_ac1", "pairs_excluded_uncertain_either")},
        "Y_dish_primary": {k: res["Y_dish_primary_related_is_0"][k] for k in ("n", "raw_agreement", "cohen_kappa", "gwet_ac1")},
        "Y_dish_sensitivity": {k: res["Y_dish_sensitivity_related_is_1"][k] for k in ("n", "raw_agreement", "cohen_kappa", "gwet_ac1")},
        "n_disagreements_six_class": len(res["disagreeing_pair_ids"]),
    }
    print(json.dumps(brief, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
