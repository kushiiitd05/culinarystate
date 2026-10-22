#!/usr/bin/env python3
"""Step 07 human gate: agreement between Kush's and Parv's independently completed packets (run ONLY after both are returned; never fabricates labels).
  python tools/step07_agreement.py <packet_Kush.csv> <packet_Parv.csv> -> reports/step07/step07h_human_gate_result.json
Metrics: pooled Cohen's kappa over all per-field codes, per-field kappa + exact agreement, per-status agreement, pooled disagreement matrix, disagreement by stratum, raw exact agreement, overall ACCEPT/REJECT kappa.
Gate: pooled kappa >= 0.80 AND no critical field with systematic disagreement (temperature location, pressure, basis, retention type, censoring)."""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["duration_judgement", "temperature_value_judgement", "temperature_location_judgement", "pressure_judgement", "power_judgement", "medium_judgement", "basis_judgement", "retention_type_judgement", "censoring_judgement"]
CRITICAL = ["temperature_location_judgement", "pressure_judgement", "basis_judgement", "retention_type_judgement", "censoring_judgement"]
CODES = {"CORRECT", "WRONG_TYPE", "WRONG_VALUE", "WRONG_LOCATION", "INFERRED", "SHOULD_BE_AMBIGUOUS", "N/A"}
NORM_COL = {"duration_judgement": "normalised_duration", "temperature_value_judgement": "normalised_temperatures", "temperature_location_judgement": "normalised_temperatures", "pressure_judgement": "normalised_pressure",
            "power_judgement": "normalised_power", "medium_judgement": "normalised_medium", "basis_judgement": "normalised_measurement_context", "retention_type_judgement": "normalised_measurement_context", "censoring_judgement": "normalised_measurement_context"}


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def load(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return {r["audit_id"]: r for r in csv.DictReader(f)}


def main(pa, pb):
    A, B = load(pa), load(pb)
    problems = []
    if set(A) != set(B):
        problems.append("audit_id sets differ")
    ids = sorted(set(A) & set(B))
    fp = {A[i]["normalizer_fingerprint_12"] for i in ids} | {B[i]["normalizer_fingerprint_12"] for i in ids}
    if len(fp) != 1:
        problems.append(f"packets carry different normalizer fingerprints {fp}")
    for who, P in (("A", A), ("B", B)):
        for i in ids:
            for fld in FIELDS + ["overall_judgement"]:
                v = (P[i].get(fld) or "").strip()
                if fld != "overall_judgement" and v not in CODES:
                    problems.append(f"{who}:{i}:{fld} invalid/blank code {v!r}")
                if fld == "overall_judgement" and v not in ("ACCEPT", "REJECT"):
                    problems.append(f"{who}:{i}:overall invalid/blank {v!r}")
    if problems:
        out = {"gate": "INVALID_INPUT", "problems": problems[:50], "n_problems": len(problems)}
        (ROOT / "reports/step07/step07h_human_gate_result.json").write_text(json.dumps(out, indent=1))
        print(json.dumps(out, indent=1))
        return 2
    identical = all(A[i][f] == B[i][f] for i in ids for f in FIELDS + ["overall_judgement"])
    pooled_a = [A[i][f].strip() for i in ids for f in FIELDS]
    pooled_b = [B[i][f].strip() for i in ids for f in FIELDS]
    per_field, flags = {}, []
    for f in FIELDS:
        a, b = [A[i][f].strip() for i in ids], [B[i][f].strip() for i in ids]
        dis = Counter((x, y) for x, y in zip(a, b) if x != y)
        prev = Counter(a + b).most_common(1)[0][1] / (2 * len(a))
        per_field[f] = {"kappa": kappa(a, b), "exact_agreement": sum(x == y for x, y in zip(a, b)) / len(a), "dominant_code_prevalence": prev, "disagreements": sum(dis.values()), "top_disagreement_pairs": [[list(k), v] for k, v in dis.most_common(3)]}
        if f in CRITICAL:
            kk = per_field[f]["kappa"]
            if (kk is not None and kk < 0.8 and prev < 0.95) or per_field[f]["exact_agreement"] < 0.9 or (dis and dis.most_common(1)[0][1] >= 3):
                flags.append(f"{f}: kappa={kk} exact={per_field[f]['exact_agreement']:.2f} top={dis.most_common(1)}  -> adjudicate before promotion")
            if prev >= 0.95:
                flags.append(f"{f}: dominant code prevalence {prev:.2f} (kappa paradox risk: inspect raw agreement)")
    matrix = Counter((x, y) for x, y in zip(pooled_a, pooled_b) if x != y)
    by_stratum = defaultdict(lambda: [0, 0])
    by_status = defaultdict(lambda: [0, 0])
    for i in ids:
        for f in FIELDS:
            ok = A[i][f].strip() == B[i][f].strip()
            by_stratum[A[i]["stratum"]][0] += ok
            by_stratum[A[i]["stratum"]][1] += 1
            st = (A[i][NORM_COL[f]].split("/")[1].split()[0] if "/" in A[i][NORM_COL[f]] else "NA")[:12]
            by_status[st][0] += ok
            by_status[st][1] += 1
    oa, ob = [A[i]["overall_judgement"].strip() for i in ids], [B[i]["overall_judgement"].strip() for i in ids]
    k_all = kappa(pooled_a, pooled_b)
    out = {"gate": "PASS" if (k_all is not None and k_all >= 0.8 and not flags and not identical) else "FAIL_OR_ADJUDICATE", "n_conditions": len(ids), "pooled_kappa": k_all, "pooled_raw_exact_agreement": sum(x == y for x, y in zip(pooled_a, pooled_b)) / len(pooled_a),
           "overall_accept_reject_kappa": kappa(oa, ob), "overall_exact_agreement": sum(x == y for x, y in zip(oa, ob)) / len(oa), "per_field": per_field, "critical_field_flags": flags,
           "disagreement_matrix_pooled": [[list(k), v] for k, v in matrix.most_common()], "agreement_by_stratum": {k: v[0] / v[1] for k, v in sorted(by_stratum.items())}, "agreement_by_normalised_status": {k: [v[0] / v[1], v[1]] for k, v in sorted(by_status.items())},
           "red_flag_identical_files": identical, "normalizer_fingerprint_12": sorted(fp)[0],
           "note": "PASS requires kappa >= 0.80, no critical-field flag, and files not identical. A critical-field flag forces adjudication even when overall kappa passes."}
    (ROOT / "reports/step07/step07h_human_gate_result.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("gate", "pooled_kappa", "pooled_raw_exact_agreement", "overall_accept_reject_kappa", "critical_field_flags", "red_flag_identical_files")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
