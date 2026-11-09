"""D4 descriptive metrics for the D5 benchmark (S178 lane H1H3H; board T8-C06-R1, T9-C18-R1). AI_DRAFTED, DRAFT.

Implements the definitions of ``reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_D4_DRAFT.md`` (D4-1, M1 and
M2), which is a PROPOSED amendment: until the lock adopts it these numbers are labelled with that status. No
hypothesis, no alpha, no decision rule. Pure functions; the tool reads the frozen benchmark and the run outputs.

M1 retrieval (blocks P1, P2 and each arm of C; P3 has no gold id and is reported separately):
- Recall@K = |gold ∩ top-K| / |gold|, K in {1, 3, 5, 10}; condition-compatible Recall@K counts only gold ids whose
  compatibility vector has no MISMATCH on matrix, process, target, time, temperature or medium (UNKNOWN is never a
  mismatch). A gold id in the top K without a recorded vector is NOT credited (conservative) and is counted.
- A C question's recall is the mean over its arms that have a gold id, so every question weighs once (the amendment
  says "mean over the questions"; listed as an ambiguity in the lane report).
- Interval: question-level percentile bootstrap, 10,000 resamples, seed ``d5-d4-recall`` (seeding as
  ``paired_stats.ucr_diff_upper95``; nearest-rank quantiles). Also "x of n questions have every gold id in the top
  K" with a Clopper-Pearson 95 % interval.
- MRR is not named by the amendment: EXPLORATORY_NOT_IN_PREREG (board T8-C06-R1 asks for it).
- Source-disjoint diagnostic: the same table per gold source family (USDA R6 and Bognar are one lineage cluster
  each, so it is DIAGNOSTIC_ONLY, REV-B G-10).

M2 risk-coverage of the B7 abstention rule (score = ordinal precision class; secondary = sufficiency mode):
- coverage(t) = share of all P and C questions (P3 included) whose score is at least t; risk(t) = share of those with
  error = 1; one point per score level present, Clopper-Pearson 95 % interval on each risk.
- error E1: an unsupported numeric or directional claim under the independent H3 scorer (any claim whose verdict is
  not SUPPORTED, uncited directional sentences included), or gold ABSTAIN and the answer did not abstain (text
  abstention as scored by ``h3_independent``). E2 adds a stated retention value outside the reviewed gold range(s).
- selective risk at coverage 50 / 70 / 90 %: the strictest point whose coverage is at least the target (no
  interpolation, no random tie-breaking). Named by the board (T9-C18-R1), not by the amendment:
  EXPLORATORY_NOT_IN_PREREG.
- NOT reported by design: ECE, Brier score, reliability diagrams, AUROC, area under the curve (``NOT_REPORTED``).
"""
from __future__ import annotations

import functools
import hashlib
import math
import random
import re
import statistics
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.evaluation.h3_independent import clopper_pearson

VERSION = "d4_metrics@0.1"
K_VALUES = (1, 3, 5, 10)
BOOT_SEED = "d5-d4-recall"
N_BOOT = 10_000
COMPAT_AXES = ("matrix", "process", "target", "time", "temperature", "medium")
CONDITION_AXES = ("time", "temperature", "medium")
RETRIEVAL_BLOCKS = ("P1", "P2", "C")
PC_BLOCKS = ("P1", "P2", "P3", "C")
PRIMARY_ORDER = ("QUANTITATIVE", "INTERVAL", "QUALITATIVE", "REPORT_CONFLICT", "ABSTAIN")
SECONDARY_ORDER = ("DIRECT", "NEAR_PARTIAL", "MODEL_INTERPOLATION", "BROAD_QUALITATIVE", "CONFLICTING",
                   "IRRELEVANT_EVIDENCE", "NO_EVIDENCE")
COVERAGE_TARGETS = (0.5, 0.7, 0.9)
ERROR_OPTIONS = ("E1", "E2")
NOT_REPORTED = {
    "ECE": "B7 emits an ordinal rule-based label, not a probability; no calibrator disjoint from D5 exists",
    "Brier score": "same reason as ECE",
    "reliability diagram": "same reason as ECE",
    "AUROC": "same reason as ECE",
    "area under the risk-coverage curve": "a handful of tied levels; the amendment computes no area",
}
PREREG_D4 = "PROPOSED_AMENDMENT_S178_D4 (D4-1 M1/M2); not adopted until the lock"
EXPLORATORY = "EXPLORATORY_NOT_IN_PREREG"
_RANGE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)")


def _ids(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [i for i in (s.strip() for s in x.split("|")) if i]
    return [str(i) for i in x if i]


def cp(x: int, n: int) -> dict:
    """Count, rate and two-sided 95 % Clopper-Pearson interval; rate None when n = 0."""
    lo, hi = clopper_pearson(x, n)
    return {"x": x, "n": n, "rate": round(x / n, 4) if n else None,
            "cp95": [round(lo, 4), round(hi, 4)] if n else None}


@functools.lru_cache(maxsize=16)
def _boot_indices(n: int, seed: str, n_boot: int) -> tuple[tuple[int, ...], ...]:
    """Resample index lists, drawn in the order of ``paired_stats.ucr_diff_upper95`` (same seeding rule)."""
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    return tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(n_boot))


def bootstrap_mean_ci(values: Sequence[float], *, seed: str = BOOT_SEED, n_boot: int = N_BOOT) -> dict:
    """Mean with a question-level percentile bootstrap 95 % interval (nearest-rank quantiles, sha256 seed). Every
    metric over the same question set uses the same resamples."""
    vals = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        return {"n": 0, "mean": None, "boot95": None, "n_boot": n_boot, "seed": seed}
    means = sorted(sum(vals[i] for i in idx) / n for idx in _boot_indices(n, seed, n_boot))
    lo = means[max(0, math.ceil(0.025 * n_boot) - 1)]
    hi = means[max(0, math.ceil(0.975 * n_boot) - 1)]
    return {"n": n, "mean": round(sum(vals) / n, 4), "boot95": [round(lo, 4), round(hi, 4)], "n_boot": n_boot,
            "seed": seed}


# ------------------------------------------------------------------ M1 retrieval

def compat_ok(vector: Mapping[str, str] | None) -> bool:
    """No MISMATCH on matrix, process, target, time, temperature or medium; a missing vector is not compatible."""
    if not vector:
        return False
    return all(vector.get(a) != "MISMATCH" for a in COMPAT_AXES)


def recall_at_k(gold: Sequence[str], ranked: Sequence[str], k: int) -> float | None:
    g = set(gold)
    if not g:
        return None
    return len(g & set(list(ranked)[:k])) / len(g)


def compat_recall_at_k(gold: Sequence[str], ranked: Sequence[str], k: int,
                       vectors: Mapping[str, Mapping[str, str]]) -> float | None:
    g = set(gold)
    if not g:
        return None
    return sum(1 for i in g & set(list(ranked)[:k]) if compat_ok(vectors.get(i))) / len(g)


def all_gold_in_top_k(gold: Sequence[str], ranked: Sequence[str], k: int) -> bool | None:
    g = set(gold)
    return None if not g else g <= set(list(ranked)[:k])


def reciprocal_rank(gold: Sequence[str], ranked: Sequence[str]) -> float | None:
    """1 / rank of the first gold id in the ranked list; 0 when none is retrieved; None without gold (EXPLORATORY)."""
    g = set(gold)
    if not g:
        return None
    for r, i in enumerate(ranked, 1):
        if i in g:
            return 1.0 / r
    return 0.0


def arms(row: Mapping[str, Any]) -> list[tuple[str, list[str]]]:
    """Retrieval units of a benchmark row: ``("arm1", gold ids)`` and, for C, ``("arm2", gold ids 2)``."""
    out = [("arm1", _ids(row.get("gold_evd_ids")))]
    if str(row.get("block")) == "C":
        out.append(("arm2", _ids(row.get("gold_evd_ids_2"))))
    return out


def ranked_list(record: Mapping[str, Any] | None, arm: str) -> list[str] | None:
    """The ranked EVD ids a rung retrieved for one arm; None when the rung retrieves nothing (B0) or was not dumped."""
    if not record:
        return None
    ret = record.get("retrieval")
    if not isinstance(ret, Mapping) or arm not in ret or ret[arm] is None:
        return None
    return _ids(ret[arm])


def states_condition(record: Mapping[str, Any] | None, gold: Iterable[str]) -> bool:
    """The question states a condition axis: the run says so, else some gold vector has a stated condition axis."""
    if record and isinstance(record.get("query_states_condition"), bool):
        return record["query_states_condition"]
    vec = (record or {}).get("gold_compat") or {}
    return any(vec.get(i, {}).get(a, "UNKNOWN") != "UNKNOWN" for i in gold for a in CONDITION_AXES)


def question_retrieval(row: Mapping[str, Any], record: Mapping[str, Any] | None,
                       ks: Sequence[int] = K_VALUES) -> dict | None:
    """Per-question M1 values (mean over arms with gold); None when the question has no gold or no ranked list."""
    units = [(a, g) for a, g in arms(row) if g]
    if not units:
        return None
    lists = {a: ranked_list(record, a) for a, _ in units}
    if any(v is None for v in lists.values()):
        return None
    vectors = (record or {}).get("gold_compat") or {}
    res: dict[str, Any] = {"qid": row["qid"], "block": row["block"], "n_arms": len(units),
                           "states_condition": states_condition(record, [i for _, g in units for i in g])}
    for k in ks:
        res[f"recall@{k}"] = sum(recall_at_k(g, lists[a], k) for a, g in units) / len(units)
        res[f"compat_recall@{k}"] = sum(compat_recall_at_k(g, lists[a], k, vectors) for a, g in units) / len(units)
        res[f"all_gold@{k}"] = all(all_gold_in_top_k(g, lists[a], k) for a, g in units)
        res[f"compat_missing@{k}"] = sum(1 for a, g in units for i in set(g) & set(lists[a][:k]) if i not in vectors)
    res["rr"] = sum(reciprocal_rank(g, lists[a]) for a, g in units) / len(units)
    return res


def _retrieval_summary(per_q: Sequence[Mapping[str, Any]], ks: Sequence[int], seed: str, n_boot: int) -> dict:
    out: dict[str, Any] = {"n_questions": len(per_q)}
    n_cond = sum(bool(q["states_condition"]) for q in per_q)
    out["n_questions_stating_condition_axis"] = n_cond
    if per_q and n_cond == 0:
        out["note"] = "no question states a condition axis: compatible recall equals plain recall by construction"
    for k in ks:
        out[f"K={k}"] = {
            "recall": bootstrap_mean_ci([q[f"recall@{k}"] for q in per_q], seed=seed, n_boot=n_boot),
            "compat_recall": bootstrap_mean_ci([q[f"compat_recall@{k}"] for q in per_q], seed=seed, n_boot=n_boot),
            "all_gold_in_top_k": cp(sum(bool(q[f"all_gold@{k}"]) for q in per_q), len(per_q)),
            "gold_in_top_k_without_compat_vector": sum(q[f"compat_missing@{k}"] for q in per_q)}
    out["mrr"] = {"prereg_status": EXPLORATORY,
                  **bootstrap_mean_ci([q["rr"] for q in per_q], seed=seed, n_boot=n_boot)}
    return out


def gold_source_family(row: Mapping[str, Any], evd: Mapping[str, Mapping[str, Any]]) -> str:
    """Source family of a question's gold rows: the one family, MIXED, or NO_GOLD_ROW."""
    fams = {str((evd.get(i) or {}).get("source_family_id") or "UNKNOWN_FAMILY")
            for _, g in arms(row) for i in g}
    return "NO_GOLD_ROW" if not fams else fams.pop() if len(fams) == 1 else "MIXED"


def retrieval_table(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]],
                    evd: Mapping[str, Mapping[str, Any]] | None = None, *, ks: Sequence[int] = K_VALUES,
                    seed: str = BOOT_SEED, n_boot: int = N_BOOT) -> dict:
    """M1 per rung, per block (P1, P2, C, pooled), per source family, plus the P3 'returned evidence anyway' share.

    ``records``: rung -> qid -> run record. A rung with no ranked list for any question (B0) is NA.
    """
    out: dict[str, Any] = {"version": VERSION, "metric": "M1_condition_compatible_recall", "prereg_status": PREREG_D4,
                           "K": list(ks), "bootstrap": {"seed": seed, "n_boot": n_boot}, "rungs": {}}
    sel = [r for r in rows if str(r.get("block")) in RETRIEVAL_BLOCKS]
    p3 = [r for r in rows if str(r.get("block")) == "P3"]
    pc_qids = {r["qid"] for r in sel} | {r["qid"] for r in p3}
    for rung in sorted(rg for rg, rc in records.items() if pc_qids & set(rc)):
        recs = records[rung]
        per_q = [x for x in (question_retrieval(r, recs.get(r["qid"]), ks) for r in sel) if x is not None]
        no_list = sum(1 for r in sel if any(g for _, g in arms(r)) and question_retrieval(r, recs.get(r["qid"]), ks) is None)
        if not per_q:
            out["rungs"][rung] = {"status": "NA_NO_RETRIEVAL_LIST", "n_questions_without_list": no_list}
            continue
        blocks = {b: _retrieval_summary([q for q in per_q if q["block"] == b], ks, seed, n_boot) for b in RETRIEVAL_BLOCKS}
        blocks["pooled_P1_P2_C"] = _retrieval_summary(per_q, ks, seed, n_boot)
        p3_lists = [ranked_list(recs.get(r["qid"]), "arm1") for r in p3]
        p3_known = [x for x in p3_lists if x is not None]
        entry: dict[str, Any] = {"status": "OK", "n_questions_without_list": no_list, "blocks": blocks,
                                 "p3_returned_evidence_anyway": {"descriptive": "not a recall",
                                                                 **cp(sum(bool(x) for x in p3_known), len(p3_known))}}
        if evd is not None:
            fam_of = {r["qid"]: gold_source_family(r, evd) for r in sel}
            fams = sorted({fam_of[q["qid"]] for q in per_q})
            entry["source_disjoint_diagnostic"] = {
                "label": "DIAGNOSTIC_ONLY (USDA R6 and Bognar are one lineage cluster each)",
                "families": {f: _retrieval_summary([q for q in per_q if fam_of[q["qid"]] == f], ks, seed, n_boot)
                             for f in fams}}
        out["rungs"][rung] = entry
    return out


# ------------------------------------------------------------------ M2 risk-coverage

def parse_gold_range(s: Any) -> tuple[float, float] | None:
    """``"0.65-0.80 fraction retained (n=3)"`` -> (0.65, 0.80); None when empty or not parseable."""
    m = _RANGE.match(str(s or ""))
    if not m:
        return None
    lo, hi = float(m.group(1)), float(m.group(2))
    return (lo, hi) if lo <= hi else (hi, lo)


def question_error(row: Mapping[str, Any], scored: Mapping[str, Any], *, option: str = "E1",
                   tol: float = 0.0) -> int:
    """Per-question error of the amendment (D-D4-3). ``scored`` is ``h3_independent.score_answer`` output."""
    if option not in ERROR_OPTIONS:
        raise ValueError(f"option must be one of {ERROR_OPTIONS}")
    bad_claim = any(c.get("verdict") != "SUPPORTED" for c in scored.get("claims", []))
    missed_abstain = str(row.get("gold_mode")) == "ABSTAIN" and not scored.get("abstained")
    err = bad_claim or missed_abstain
    if option == "E2" and not err:
        ranges = [x for x in (parse_gold_range(row.get("gold_retention_range")),
                              parse_gold_range(row.get("gold_retention_range_2"))) if x]
        if ranges:
            for c in scored.get("claims", []):
                if c.get("kind") == "NUMERIC" and c.get("value") is not None and not any(
                        lo - tol <= float(c["value"]) <= hi + tol for lo, hi in ranges):
                    err = True
    return int(err)


def score_level(record: Mapping[str, Any], *, order: Sequence[str] = PRIMARY_ORDER) -> tuple[str, str]:
    """Ordinal score of a decision-layer answer and the rule used.

    Primary: the precision class after the OOD cap. Secondary: the sufficiency mode. A COMPARE answer takes the
    lowest level over its options (a comparison is only as precise as its weaker arm; listed ambiguity). ABSTAIN,
    ASK or a missing value -> the lowest level of the order.
    """
    d = record.get("decision") or {}
    primary = tuple(order) == PRIMARY_ORDER
    key = "precision" if primary else "sufficiency"
    lowest = order[-1]
    mode = d.get("mode")
    if mode == "COMPARE" and isinstance(d.get("per_option"), Mapping) and d["per_option"]:
        vals = [o.get(key) for o in d["per_option"].values()]
        if all(v in order for v in vals):
            return max(vals, key=order.index), "COMPARE_MIN_OVER_OPTIONS"
        return lowest, "COMPARE_OPTION_LEVEL_MISSING"
    v = d.get(key) if primary else (d.get("sufficiency") or d.get("reason"))
    if mode in ("ABSTAIN", "ASK") and not (not primary and v in order):
        return lowest, f"MODE_{mode}"
    if v in order:
        return v, "DECISION_FIELD"
    return lowest, "LEVEL_MISSING"


def risk_coverage(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Any]],
                  scored: Mapping[str, Mapping[str, Any]], *, order: Sequence[str] = PRIMARY_ORDER,
                  error_option: str = "E1") -> dict:
    """Risk-coverage step points over all P and C questions for one decision-layer rung (B7)."""
    sel = [r for r in rows if str(r.get("block")) in PC_BLOCKS]
    lv, rules, err = {}, {}, {}
    missing = []
    for r in sel:
        q = r["qid"]
        if q not in records or q not in scored:
            missing.append(q)
            continue
        lv[q], rules[q] = score_level(records[q], order=order)
        err[q] = question_error(r, scored[q], option=error_option)
    n = len(lv)
    points = []
    for t in order:
        if t not in lv.values():
            continue
        ans = [q for q in lv if order.index(lv[q]) <= order.index(t)]
        points.append({"threshold": t, "answered": len(ans), "coverage": round(len(ans) / n, 4) if n else None,
                       "risk": cp(sum(err[q] for q in ans), len(ans))})
    rule_counts: dict[str, int] = {}
    for v in rules.values():
        rule_counts[v] = rule_counts.get(v, 0) + 1
    return {"metric": "M2_risk_coverage", "prereg_status": PREREG_D4, "order": list(order), "error": error_option,
            "n_questions": n, "missing_questions": sorted(missing), "level_rules": rule_counts, "points": points,
            "all_answered_risk": cp(sum(err.values()), n),
            "no_calibration_claim": "ordinal rule-based score; not a probability; no 'calibration' wording"}


def selective_risk_at_coverage(curve: Mapping[str, Any], targets: Sequence[float] = COVERAGE_TARGETS) -> dict:
    """For each coverage target: the strictest risk-coverage point with coverage >= target (achieved coverage shown)."""
    pts = curve.get("points") or []
    out = {"prereg_status": EXPLORATORY, "rule": "strictest level whose coverage >= target; no interpolation",
           "targets": {}}
    for t in targets:
        ok = [p for p in pts if p["coverage"] is not None and p["coverage"] >= t - 1e-12]
        out["targets"][f"{int(round(t * 100))}%"] = (
            {"threshold": ok[0]["threshold"], "achieved_coverage": ok[0]["coverage"], **ok[0]["risk"]} if ok else
            {"threshold": None, "achieved_coverage": None, "x": None, "n": 0, "rate": None, "cp95": None})
    return out


def all_answered_risk(rows: Sequence[Mapping[str, Any]], scored: Mapping[str, Mapping[str, Any]], *,
                      error_option: str = "E1") -> dict:
    """Reference point for a rung without abstention (B5 at coverage 1): error share over all P and C questions."""
    sel = [r for r in rows if str(r.get("block")) in PC_BLOCKS and r["qid"] in scored]
    return cp(sum(question_error(r, scored[r["qid"]], option=error_option) for r in sel), len(sel))


def abstention_precision_recall(rows: Sequence[Mapping[str, Any]], scored: Mapping[str, Mapping[str, Any]]) -> dict:
    """Abstention as a detector of gold ABSTAIN over P and C questions (text abstention). Board T9-C18-R1;
    recall is the amendment's 'abstention on ABSTAIN gold', precision is EXPLORATORY_NOT_IN_PREREG."""
    sel = [r for r in rows if str(r.get("block")) in PC_BLOCKS and r["qid"] in scored]
    abst = [r for r in sel if scored[r["qid"]].get("abstained")]
    gold = [r for r in sel if str(r.get("gold_mode")) == "ABSTAIN"]
    tp = sum(1 for r in abst if str(r.get("gold_mode")) == "ABSTAIN")
    return {"precision": {"prereg_status": EXPLORATORY, **cp(tp, len(abst))},
            "recall": {"prereg_status": "PROPOSED_AMENDMENT_S178_C6 (abstention on ABSTAIN gold)", **cp(tp, len(gold))}}


def latency_summary(records: Mapping[str, Mapping[str, Any]], qids: Iterable[str]) -> dict:
    vals = [float(records[q]["latency_s"]) for q in qids if q in records and isinstance(records[q].get("latency_s"), (int, float))]
    return {"n": len(vals), "median_s": round(statistics.median(vals), 4) if vals else None,
            "mean_s": round(sum(vals) / len(vals), 4) if vals else None}
