"""Step 07.A-R1 scorer: Gwet AC1 gate (reports/step07/07A_R1_preregistration_DRAFT.md §3). DRAFT_PENDING_SIGNATURES.

``score(issued, a, b)`` takes the issued packet rows and the two returned packets (lists of dicts, CSV rows) and
returns gate PASS / FAIL_OR_ADJUDICATE / INVALID_INPUT / NOT_COUNTED with the registered statistic and the
diagnostics. Pure: no file I/O, no label is ever written or changed. The output holds codes, numbers and audit ids
(CA-nnn) only, never condition ids or raw strings. Kappa, PABAK and the bootstrap interval are diagnostics only.
"""
from __future__ import annotations

import hashlib
import random
from collections import Counter
from typing import Mapping, Sequence

FIELDS = ("duration_judgement", "temperature_value_judgement", "temperature_location_judgement",
          "pressure_judgement", "power_judgement", "medium_judgement", "basis_judgement",
          "retention_type_judgement", "censoring_judgement")
CRITICAL = ("temperature_location_judgement", "pressure_judgement", "basis_judgement", "retention_type_judgement",
            "censoring_judgement")
CODES = frozenset({"CORRECT", "WRONG_TYPE", "WRONG_VALUE", "WRONG_LOCATION", "INFERRED", "SHOULD_BE_AMBIGUOUS",
                   "N/A"})
OVERALL = ("ACCEPT", "REJECT")
JUDGEMENT_COLS = (*FIELDS, "overall_judgement", "reason_if_not_correct")
Q = 7
THRESHOLD_AC1, THRESHOLD_EXACT, REPEAT_PAIR = 0.80, 0.90, 3
BOOT_N, BOOT_SEED = 2000, "07A-R1-bootstrap"
SCORER_VERSION = "07A-R1-scorer-0.1.0-draft"


def _check(a: Sequence[str], b: Sequence[str]) -> int:
    if len(a) != len(b) or not a:
        raise ValueError("code lists must be non-empty and of equal length")
    return len(a)


def gwet_ac1(a: Sequence[str], b: Sequence[str], *, q: int) -> float:
    """Gwet (2008) AC1 for two raters; q = number of categories in the codebook."""
    if q < 2:
        raise ValueError("q must be >= 2")
    n = _check(a, b)
    pa = sum(x == y for x, y in zip(a, b)) / n
    counts = Counter(a) + Counter(b)
    pe = sum((c / (2 * n)) * (1 - c / (2 * n)) for c in counts.values()) / (q - 1)
    return 1.0 if pe == 1 else (pa - pe) / (1 - pe)


def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> float:
    n = _check(a, b)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def _exact(a: Sequence[str], b: Sequence[str]) -> float:
    return sum(x == y for x, y in zip(a, b)) / _check(a, b)


def _by_id(rows: Sequence[Mapping]) -> dict[str, Mapping]:
    return {str(r.get("audit_id", "")).strip(): r for r in rows}


def _validity(I: dict, A: dict, B: dict) -> list[str]:
    probs = []
    if set(A) != set(I) or set(B) != set(I):
        probs.append("AUDIT_ID_SETS_DIFFER")
    ids = sorted(set(I) & set(A) & set(B))
    fps = {str(P[i].get("normalizer_fingerprint_12", "")).strip() for P in (I, A, B) for i in ids}
    if len(fps) != 1:
        probs.append("NORMALIZER_FINGERPRINTS_DIFFER")
    for who, P in (("A", A), ("B", B)):
        for i in ids:
            for f in FIELDS:
                if str(P[i].get(f) or "").strip() not in CODES:
                    probs.append(f"{who}:{i}:{f}:INVALID_OR_BLANK")
            if str(P[i].get("overall_judgement") or "").strip() not in OVERALL:
                probs.append(f"{who}:{i}:overall_judgement:INVALID_OR_BLANK")
    return probs


def _provenance(I: dict, A: dict, B: dict, ids: list[str]) -> list[str]:
    probs = []
    for who, P in (("A", A), ("B", B)):
        for i in ids:
            for col in I[i]:
                if col not in JUDGEMENT_COLS and str(P[i].get(col) or "") != str(I[i].get(col) or ""):
                    probs.append(f"{who}:{i}:{col}:DIFFERS_FROM_ISSUED")
    if all(str(A[i].get(c) or "").strip() == str(B[i].get(c) or "").strip()
           for i in ids for c in (*FIELDS, "overall_judgement")):
        probs.append("IDENTICAL_JUDGEMENTS")
    return probs


def _codes(P: dict, ids: list[str], fields=FIELDS) -> list[str]:
    return [str(P[i][f]).strip() for i in ids for f in fields]


def _bootstrap(A: dict, B: dict, ids: list[str]) -> list[float]:
    rng = random.Random(int(hashlib.sha256(BOOT_SEED.encode()).hexdigest(), 16))
    per = {i: (_codes(A, [i]), _codes(B, [i])) for i in ids}
    vals = []
    for _ in range(BOOT_N):
        pick = [ids[rng.randrange(len(ids))] for _ in ids]
        a = [c for i in pick for c in per[i][0]]
        b = [c for i in pick for c in per[i][1]]
        vals.append(gwet_ac1(a, b, q=Q))
    vals.sort()
    return [vals[int(0.025 * BOOT_N)], vals[int(0.975 * BOOT_N) - 1]]


def _field(a: list[str], b: list[str]) -> tuple[dict, Counter]:
    dis = Counter((x, y) for x, y in zip(a, b) if x != y)
    prev = Counter(a + b).most_common(1)[0][1] / (2 * len(a))
    return {"ac1": gwet_ac1(a, b, q=Q), "exact_agreement": _exact(a, b), "kappa_diagnostic": cohen_kappa(a, b),
            "dominant_code_prevalence": prev, "disagreements": sum(dis.values()),
            "top_disagreement_pairs": [[list(k), v] for k, v in dis.most_common(3)]}, dis


def score(issued: Sequence[Mapping], a: Sequence[Mapping], b: Sequence[Mapping]) -> dict:
    """Registered 07.A-R1 gate on the original independent labels."""
    I, A, B = _by_id(issued), _by_id(a), _by_id(b)
    base = {"attempt": "07A-R1", "scorer_version": SCORER_VERSION, "statistic": "GWET_AC1", "q": Q,
            "threshold_ac1": THRESHOLD_AC1, "counts_as_human_gate": False}
    probs = _validity(I, A, B)
    if probs:
        return {**base, "gate": "INVALID_INPUT", "problems": probs[:50], "n_problems": len(probs)}
    ids = sorted(I)
    probs = _provenance(I, A, B, ids)
    if probs:
        return {**base, "gate": "NOT_COUNTED", "problems": probs[:50], "n_problems": len(probs)}
    pa, pb = _codes(A, ids), _codes(B, ids)
    per_field, flags = {}, []
    for f in FIELDS:
        stats, dis = _field(_codes(A, ids, (f,)), _codes(B, ids, (f,)))
        per_field[f] = stats
        if f in CRITICAL:
            top = dis.most_common(1)[0][1] if dis else 0
            if stats["ac1"] < THRESHOLD_AC1 or stats["exact_agreement"] < THRESHOLD_EXACT or top >= REPEAT_PAIR:
                flags.append(f"{f}:ac1={stats['ac1']:.4f}:exact={stats['exact_agreement']:.4f}:top_pair={top}")
    ac1 = gwet_ac1(pa, pb, q=Q)
    oa, ob = _codes(A, ids, ("overall_judgement",)), _codes(B, ids, ("overall_judgement",))
    raw = _exact(pa, pb)
    strata: dict[str, list[int]] = {}
    for i in ids:
        s = strata.setdefault(str(I[i].get("stratum") or "NA"), [0, 0])
        s[0] += sum(x == y for x, y in zip(_codes(A, [i]), _codes(B, [i])))
        s[1] += len(FIELDS)
    gate = "PASS" if ac1 >= THRESHOLD_AC1 and not flags else "FAIL_OR_ADJUDICATE"
    return {**base, "gate": gate, "n_conditions": len(ids), "n_cells": len(pa), "pooled_ac1": ac1,
            "critical_field_flags": flags, "per_field": per_field,
            "diagnostics": {"pooled_kappa": cohen_kappa(pa, pb), "pooled_raw_exact_agreement": raw,
                            "pooled_pabak": 2 * raw - 1, "overall_ac1": gwet_ac1(oa, ob, q=2),
                            "overall_kappa": cohen_kappa(oa, ob), "overall_exact_agreement": _exact(oa, ob),
                            "agreement_by_stratum": {k: v[0] / v[1] for k, v in sorted(strata.items())},
                            "disagreement_matrix_pooled": [[list(k), v] for k, v in Counter(
                                (x, y) for x, y in zip(pa, pb) if x != y).most_common()],
                            "pooled_ac1_bootstrap95": _bootstrap(A, B, ids), "bootstrap_resamples": BOOT_N}}
