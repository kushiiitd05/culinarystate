"""S181: the four D4 contract metrics, from frozen committed artifacts only (POST-HOC DIAGNOSTIC).

The proposal checks D4 by: condition-compatible Recall@K, risk-coverage, unsupported-claim rate, ECE.
This script states, for each, one of ALREADY_REPORTED / COMPUTED_NOW / NOT_COMPUTABLE, and writes
``reports/s181/d4_contract_metrics.json``. It reads only; it changes no frozen file and no gate.

Laws applied here:
  * nothing is imputed, simulated or approximated; a missing input gives NOT_COMPUTABLE and names the input;
  * gold on the 74-question D5 benchmark is model-assisted / AI-delegated (D-085): every figure carries
    MODEL_ASSISTED_GOLD, NO_HUMAN_SIGNOFF_D085 and POST_HOC_DIAGNOSTIC and is not system accuracy in general;
  * every figure was computed after the D5 results were seen: descriptive statistics, not pre-registered tests;
  * H1 and H3 stay RULE_NOT_MET (D-092). Nothing here re-tests, re-tunes or re-reads either rule.

Run:  PYTHONPATH=src /opt/anaconda3/bin/python tools/s181_d4_contract_metrics.py [--check]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from fractions import Fraction
from numbers import Real
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "s181" / "d4_contract_metrics.json"

BENCH_PC = "benchmark/d5/d5_benchmark_v1_D085_PC.csv"
RUNS = "reports/del5/d5_runs_v1_D085.jsonl"
SCORE = "reports/del5/d5_score_v1_D085/d5_scoring_result.json"
EVD = "ledgers/data/EVD.jsonl"
COND = "ledgers/data/COND.jsonl"
CODE = ("src/culinarystate/retrieval/compatibility.py", "src/culinarystate/evaluation/d4_metrics.py",
        "src/culinarystate/decision/confidence.py", "tools/s179_d5_run_rungs.py")
INPUTS = (BENCH_PC, RUNS, SCORE, EVD, COND, *CODE)

VERSION = "s181_d4_contract_metrics@0.1"
LABELS = ("MODEL_ASSISTED_GOLD", "NO_HUMAN_SIGNOFF_D085", "POST_HOC_DIAGNOSTIC")
LABEL_LINE = " · ".join(LABELS)
K_VALUES = (1, 3, 5, 10)
RETRIEVAL_BLOCKS = ("P1", "P2", "C")
RETRIEVAL_RUNG = "B2"
DECISION_RUNGS = ("B5", "B5T", "B7")
UCR_RUNGS = ("B0", "B2", "B5", "B5T", "B7")
ECE_BINS = 10
CONFIDENCE_KEY_PARTS = ("confidence", "probab", "prob_", "p_correct", "calibrated", "score")
CONDITION_COLUMNS = ("time", "time_min", "duration", "temperature", "temperature_c", "medium")
ALREADY, COMPUTED, NOT_COMPUTABLE = "ALREADY_REPORTED", "COMPUTED_NOW", "NOT_COMPUTABLE"


class NotComputable(Exception):
    """A metric input is missing or of the wrong kind. The message names the missing input."""


# ------------------------------------------------------------------ pure metric functions

def recall_at_k(gold: Sequence[str], ranked: Sequence[str], k: int) -> float | None:
    """|gold ∩ top-K| / |gold|; None (not 0) without gold."""
    g = set(gold)
    if not g:
        return None
    return len(g & set(list(ranked)[:k])) / len(g)


def compat_recall_at_k(gold: Sequence[str], ranked: Sequence[str], k: int,
                       compat_ok: Mapping[str, bool]) -> float | None:
    """|{g in gold ∩ top-K: compat_ok[g]}| / |gold|. A retrieved gold id without a flag is refused, not counted 0."""
    g = set(gold)
    if not g:
        return None
    hits = sorted(g & set(list(ranked)[:k]))
    missing = [i for i in hits if i not in compat_ok]
    if missing:
        raise NotComputable(f"no compatibility flag for retrieved gold id(s): {', '.join(missing)}")
    return sum(1 for i in hits if compat_ok[i]) / len(g)


def mean(values: Sequence[float | None]) -> float | None:
    if not values:
        return None
    if any(v is None for v in values):
        raise NotComputable("a per-question value is None; it is neither dropped nor set to 0")
    return sum(values) / len(values)


def aurc_trapezoid(points: Sequence[Mapping[str, Any]]) -> dict:
    """Trapezoid area under risk(coverage) over the OBSERVED coverage span only (exact fractions).

    Each point: ``answered``, ``errors``, ``n_total``. coverage = answered / n_total, risk = errors / answered.
    ``normalized`` = area / span width = mean risk over the observed span. Nothing is extrapolated to coverage 0.
    """
    if len(points) < 2:
        raise NotComputable("fewer than two risk-coverage points: no area")
    xy = []
    for p in points:
        if not p["answered"]:
            raise NotComputable(f"threshold {p.get('threshold')}: no answered question, risk undefined")
        xy.append((Fraction(p["answered"], p["n_total"]), Fraction(p["errors"], p["answered"])))
    if any(b[0] <= a[0] for a, b in zip(xy, xy[1:])):
        raise NotComputable("coverage is not strictly increasing across the points")
    area = sum((b[0] - a[0]) * (a[1] + b[1]) / 2 for a, b in zip(xy, xy[1:]))
    width = xy[-1][0] - xy[0][0]
    return {"partial_area": area, "coverage_span": [xy[0][0], xy[-1][0]], "normalized": area / width,
            "n_points": len(xy), "rule": "trapezoid between observed points; no extrapolation below the first"}


def unsupported_claim_rate(unsupported: int, claims: int) -> Fraction | None:
    if unsupported < 0 or claims < 0 or unsupported > claims:
        raise ValueError(f"impossible counts: unsupported={unsupported}, claims={claims}")
    return None if claims == 0 else Fraction(unsupported, claims)


def expected_calibration_error(confidences: Sequence[float] | None, correct: Sequence[int],
                               n_bins: int = ECE_BINS) -> dict:
    """ECE = sum_b (n_b / n) * |acc_b - conf_b| over ``n_bins`` equal-width bins on [0, 1] (last bin closed)."""
    if confidences is None or len(confidences) == 0:
        raise NotComputable("no per-item numeric confidence")
    if len(confidences) != len(correct):
        raise NotComputable("confidence and correctness lists differ in length")
    for c in confidences:
        if isinstance(c, bool) or not isinstance(c, Real):
            raise NotComputable(f"confidence {c!r} is not numeric (a categorical label is not a probability)")
        if not 0.0 <= c <= 1.0:
            raise NotComputable(f"confidence {c!r} is outside [0, 1]")
    n = len(confidences)
    bins: dict[int, list[tuple[float, int]]] = {}
    for c, y in zip(confidences, correct):
        bins.setdefault(min(int(c * n_bins), n_bins - 1), []).append((float(c), int(bool(y))))
    ece = sum(len(v) / n * abs(sum(y for _, y in v) / len(v) - sum(c for c, _ in v) / len(v)) for v in bins.values())
    return {"ece": ece, "n": n, "n_bins": n_bins, "binning": "equal-width", "non_empty_bins": len(bins)}


def find_numeric_confidence_fields(records: Sequence[Mapping[str, Any]]) -> list[str]:
    """Key paths (dict keys under ``per_option`` collapsed to ``*``) of numeric fields that look like a confidence."""
    found: set[str] = set()

    def walk(o: Any, path: tuple[str, ...]) -> None:
        if not isinstance(o, Mapping):
            return
        for k, v in o.items():
            p = path + ("*" if path and path[-1] == "per_option" else str(k),)
            if isinstance(v, Mapping):
                walk(v, p)
            elif (isinstance(v, Real) and not isinstance(v, bool)
                  and any(part in str(k).lower() for part in CONFIDENCE_KEY_PARTS)):
                found.add(".".join(p))

    for r in records:
        walk(r, ())
    return sorted(found)


def ece_block(records: Sequence[Mapping[str, Any]]) -> dict:
    """ECE on the run records, or NOT_COMPUTABLE with the missing input. No categorical-to-number mapping is made."""
    decision = [r for r in records if isinstance(r.get("decision"), Mapping)]
    fields = find_numeric_confidence_fields(decision)
    emitted = sorted({str(k) for r in decision for k in r["decision"]})
    if not fields:
        return {
            "outcome": NOT_COMPUTABLE, "value": None, "binning_if_it_were_computable": f"{ECE_BINS} equal-width bins",
            "n_decision_records_scanned": len(decision), "numeric_confidence_fields_found": [],
            "decision_fields_emitted": emitted,
            "missing_input": ("a per-item numeric confidence in [0, 1]: the run records carry only categorical "
                              "fields (mode, precision class, sufficiency mode); no probability is emitted or stored"),
            "why_no_mapping": [
                "src/culinarystate/decision/confidence.py:3-4 states the confidence vector holds 'ordinal features in "
                "[0, 1] for a later calibrator (§242.4) — not probabilities'; that vector is also not saved in the "
                "run records",
                "src/culinarystate/evaluation/d4_metrics.py:56-57 (NOT_REPORTED, frozen): 'B7 emits an ordinal "
                "rule-based label, not a probability; no calibrator disjoint from D5 exists'",
                "the §242.4 calibrator was never built, and fitting one on the 40 D5 questions and scoring it on the "
                "same 40 would be circular; assigning numbers to QUANTITATIVE/INTERVAL/QUALITATIVE by hand would be "
                "an invented mapping",
            ],
            "not_a_substitute": "reports/ner/ holds ECE for the NER linker confidence (a different component, D1); "
                                "it says nothing about D4 abstention",
        }
    raise NotComputable(f"numeric confidence-like fields exist ({fields}); this script does not guess their meaning")


# ------------------------------------------------------------------ io

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ids(x: Any) -> list[str]:
    return [i for i in str(x or "").split("|") if i]


def _jsonable(o: Any) -> Any:
    if isinstance(o, Fraction):
        return {"x": o.numerator, "n": o.denominator, "value": round(float(o), 4), "note": "reduced fraction"}
    if isinstance(o, Mapping):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    return round(o, 4) if isinstance(o, float) else o


def _rate(x: int, n: int) -> dict:
    return {"x": x, "n": n, "value": round(x / n, 4) if n else None}


def _latest_by_id(path: Path, wanted: set[str]) -> dict[str, dict]:
    """Last row per id in an append-only ledger file, for the wanted ids only."""
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("id") in wanted:
                out[row["id"]] = row
    return out


# ------------------------------------------------------------------ metric 1: condition-compatible Recall@K

def recall_block(bench: Sequence[Mapping[str, str]], runs: Sequence[Mapping[str, Any]], score: Mapping[str, Any],
                 root: Path) -> dict:
    from culinarystate.evaluation.d4_metrics import COMPAT_AXES, compat_ok   # frozen, read-only
    from culinarystate.retrieval.compatibility import Query, compatibility   # frozen, read-only

    recs = {r["qid"]: r for r in runs if r["rung"] == RETRIEVAL_RUNG}
    per_q, no_list, list_lengths = [], [], []
    for row in bench:
        if row["block"] not in RETRIEVAL_BLOCKS:
            continue
        units = [("arm1", _ids(row.get("gold_evd_ids")))]
        if row["block"] == "C":
            units.append(("arm2", _ids(row.get("gold_evd_ids_2"))))
        units = [(a, g) for a, g in units if g]
        ret = (recs.get(row["qid"]) or {}).get("retrieval") or {}
        if not units or any(ret.get(a) is None for a, _ in units):
            no_list.append(row["qid"])
            continue
        list_lengths += [len(ret[a]) for a, _ in units]
        per_q.append({"qid": row["qid"], "block": row["block"], "units": [(g, list(ret[a])) for a, g in units]})

    hit_ids = {i for q in per_q for g, lst in q["units"] for i in set(g) & set(lst)}
    evd = _latest_by_id(root / EVD, hit_ids)
    cond_ids = {e["process"].get("condition_id") for e in evd.values()} - {None}
    cond = _latest_by_id(root / COND, cond_ids)
    if set(evd) != hit_ids:
        raise NotComputable(f"gold EVD rows absent from the ledger: {sorted(hit_ids - set(evd))}")
    # The query B2 actually retrieved with is the empty Query (tools/s179_d5_run_rungs.py:110, RL.Query()).
    vectors = {i: compatibility(Query(), e, cond.get(e["process"].get("condition_id") or ""), {})["vector"]
               for i, e in evd.items()}
    flags = {i: compat_ok({a: v[a] for a in COMPAT_AXES}) for i, v in vectors.items()}
    axis_values: dict[str, dict[str, int]] = {}
    for v in vectors.values():
        for a in COMPAT_AXES:
            axis_values.setdefault(a, {})
            axis_values[a][v[a]] = axis_values[a].get(v[a], 0) + 1

    frozen = score["retrieval_d4_m1"]["rungs"][RETRIEVAL_RUNG]
    fz = frozen["blocks"]["pooled_P1_P2_C"]
    table, repro_ok = {}, True
    for k in K_VALUES:
        plain = mean([mean([recall_at_k(g, lst, k) for g, lst in q["units"]]) for q in per_q])
        compat = mean([mean([compat_recall_at_k(g, lst, k, flags) for g, lst in q["units"]]) for q in per_q])
        f_plain, f_compat = fz[f"K={k}"]["recall"]["mean"], fz[f"K={k}"]["compat_recall"]["mean"]
        repro_ok &= round(plain, 4) == f_plain
        table[f"K={k}"] = {
            "plain_recall_recomputed": round(plain, 4), "plain_recall_frozen": f_plain,
            "compat_recall_computed_now": round(compat, 4), "compat_recall_frozen_as_recorded": f_compat,
            "frozen_gold_hits_without_compat_vector": fz[f"K={k}"]["gold_in_top_k_without_compat_vector"],
            "gold_hits_scored_now": sum(len(set(g) & set(lst[:k])) for q in per_q for g, lst in q["units"]),
            "all_gold_in_top_k_frozen": fz[f"K={k}"]["all_gold_in_top_k"]}
    n_cond = fz["n_questions_stating_condition_axis"]
    cond_cols = [c for c in (bench[0].keys() if bench else []) if c.lower() in CONDITION_COLUMNS]
    by_block = {b: sum(q["block"] == b for q in per_q) for b in RETRIEVAL_BLOCKS}
    return {
        "plain_recall_at_k": {"outcome": ALREADY, "where": f"{SCORE} :: retrieval_d4_m1.rungs.B2.blocks.pooled_P1_P2_C",
                              "recomputed_equals_frozen": bool(repro_ok)},
        "condition_compatible_recall_at_k": {
            "outcome": COMPUTED, "qualifier": "DEGENERATE_EQUALS_PLAIN_RECALL_NO_CONDITION_AXIS_STATED",
            "definition": "amendment S178_D4 M1: gold hit counts if frozen compatibility() gives no MISMATCH on "
                          "matrix/process/target/time/temperature/medium (d4_metrics.compat_ok); UNKNOWN is not a "
                          "mismatch; mean over questions",
            "query_used": "empty Query() — the query the B2 rung retrieved with (tools/s179_d5_run_rungs.py:110)",
            "condition_discriminating_variant": {
                "outcome": NOT_COMPUTABLE,
                "missing_input": "a benchmark question that states time, temperature or medium, and a stated-"
                                 "condition query in the run record: n_questions_stating_condition_axis = "
                                 f"{n_cond}; benchmark condition columns present = {cond_cols}; the run records "
                                 "carry no gold_compat and no query_states_condition field"},
            "reading": "every gold hit has all six axes UNKNOWN under the run's query, so nothing can mismatch and "
                       "the value equals plain recall by construction (the amendment says so in advance). It shows "
                       "nothing about condition-aware retrieval.",
            "frozen_0.0_explained": "the frozen scorer recorded compat recall 0.0 because the run records carry no "
                                    "gold_compat vectors and compat_ok() treats a missing vector as incompatible "
                                    "(d4_metrics.py:106-110); it is a missing-input artifact, not a measured zero. "
                                    "The frozen JSON is left as it is."},
        "rung": RETRIEVAL_RUNG, "n_questions": len(per_q), "n_by_block": by_block,
        "denominator": "questions in P1/P2/C with gold ids and a dumped ranked list",
        "n_questions_without_list": len(no_list), "questions_without_list": sorted(no_list),
        "n_questions_frozen": fz["n_questions"],
        "other_rungs": {r: frozen_r["status"] for r, frozen_r in score["retrieval_d4_m1"]["rungs"].items()
                        if r != RETRIEVAL_RUNG},
        "ranked_list_length": {"min": min(list_lengths), "max": max(list_lengths)},
        "k_caveat": (f"ranked lists hold at most {max(list_lengths)} ids, so K=10 cannot exceed K={max(list_lengths)}; "
                     "Recall@10 is not a true top-10 figure") if max(list_lengths) < max(K_VALUES) else None,
        "compat_axis_values_over_gold_hits": axis_values, "n_gold_hit_rows": len(vectors),
        "n_gold_hit_rows_compat_ok": sum(flags.values()),
        "table": table, "labels": list(LABELS)}


# ------------------------------------------------------------------ metric 2: risk-coverage (+ AURC)

def risk_coverage_block(score: Mapping[str, Any]) -> dict:
    m2 = score["d4_m2_risk_coverage"]
    rungs = {}
    for rung in DECISION_RUNGS:
        cur = m2["decision_layer_rungs"][rung]["primary_precision_class"]
        n = cur["n_questions"]
        pts = [{"threshold": p["threshold"], "answered": p["answered"], "errors": p["risk"]["x"], "n_total": n}
               for p in cur["points"]]
        a = aurc_trapezoid(pts)
        flat = Fraction(cur["all_answered_risk"]["x"], cur["all_answered_risk"]["n"])
        risks = [Fraction(p["errors"], p["answered"]) for p in pts]
        rungs[rung] = {
            "points_frozen": [{"threshold": p["threshold"], "coverage": _rate(p["answered"], n),
                               "risk": _rate(p["errors"], p["answered"])} for p in pts],
            "aurc_partial_area": a["partial_area"], "aurc_normalized_mean_risk_over_span": a["normalized"],
            "coverage_span": a["coverage_span"], "n_points": a["n_points"],
            "all_answered_risk": flat,
            "normalized_minus_all_answered_risk": round(float(a["normalized"] - flat), 4),
            "risk_non_decreasing_in_coverage": all(y >= x for x, y in zip(risks, risks[1:])),
            "n_questions": n, "error_definition": cur["error"]}
    return {
        "curve_points": {"outcome": ALREADY,
                         "where": f"{SCORE} :: d4_m2_risk_coverage.decision_layer_rungs.<rung>."
                                  "primary_precision_class.points; transcribed in "
                                  "reports/final/sections/S179_D4_retrieval_and_abstention_DRAFT.md (M2 table)"},
        "aurc": {"outcome": COMPUTED, "rule": "trapezoid between the observed step points, exact fractions; "
                                             "partial area over the observed coverage span only; normalized = "
                                             "area / span width",
                 "outside_frozen_amendment": "the frozen amendment and scorer deliberately compute no area "
                                             f"('{m2['not_reported_by_design']['area under the risk-coverage curve']}'"
                                             "). This AURC is a post-hoc addition over 4 tied ordinal levels; it is "
                                             "not a pre-registered quantity and carries no interval.",
                 "not_comparable_to": "a full-range AURC from a continuous confidence; the span starts at the first "
                                      "observed coverage, nothing is extrapolated to coverage 0"},
        "score_used_for_ordering": "ordinal output-precision class (rule-based, not a probability)",
        "denominator": "the 40 P1/P2/P3/C questions per rung", "rungs": rungs, "labels": list(LABELS)}


# ------------------------------------------------------------------ metric 3: unsupported-claim rate

def ucr_block(score: Mapping[str, Any]) -> dict:
    h3 = score["h3_summaries"]
    rungs = {}
    for rung in UCR_RUNGS:
        a = h3["rungs"][rung]["all"]
        r = unsupported_claim_rate(a["n_unsupported"], a["n_numeric_claims"])
        enf = h3["enforcement_checker_ucr"][rung]
        rungs[rung] = {
            "independent_checker": {"unsupported": a["n_unsupported"], "numeric_claims": a["n_numeric_claims"],
                                    "ucr_frozen": a["ucr"], "ucr_recomputed": None if r is None else round(float(r), 4),
                                    "n_questions": a["n_questions"],
                                    "answers_with_no_claim_and_no_abstention": a["answers_with_no_claim_and_no_abstention"],
                                    "version": a["version"]},
            "enforcement_checker_not_independent": {"unsupported": enf["unsupported"],
                                                    "numeric_claims": enf["numeric_claims"], "ucr_frozen": enf["ucr"]}}
        if r is not None and round(float(r), 4) != a["ucr"]:
            raise NotComputable(f"{rung}: frozen UCR {a['ucr']} != x/n {float(r):.4f}")
    return {"outcome": ALREADY, "where": f"{SCORE} :: h3_summaries.rungs.<rung>.all (ucr, n_unsupported, "
                                         "n_numeric_claims) and h3_summaries.enforcement_checker_ucr",
            "not_yet_in_prose": "the figure is in the frozen score JSON; the S179 D4 section and the final report "
                                "draft do not quote it",
            "unit": "numeric claims in the 40 P/C answers per rung (claim-level, not question-level)",
            "checker": "machine checker against the EVD ledger; the human claim audit is "
                       f"{score['audit']['status'].split(':')[0]} (D-092: NOT_RUN), so no human-verified rate exists",
            "reading": "UCR covers numeric claims only and is undefined for an answer with no number; read it next "
                       "to coverage",
            "rungs": rungs, "labels": list(LABELS)}


# ------------------------------------------------------------------ assemble

def build(root: Path = ROOT) -> dict:
    hashes = {p: sha256(root / p) for p in INPUTS}
    score = json.loads((root / SCORE).read_text(encoding="utf-8"))
    with (root / BENCH_PC).open(encoding="utf-8", newline="") as f:
        bench = list(csv.DictReader(f))
    runs = [json.loads(line) for line in (root / RUNS).read_text(encoding="utf-8").splitlines() if line.strip()]
    guard = score.get("meta", {}).get("guard", {})
    pinned = {**guard.get("files_sha256", {}), **guard.get("code_sha256", {})}
    cross = {p: ("MATCHES_FREEZE" if pinned[p] == h else "DIFFERS_FROM_FREEZE") for p, h in hashes.items() if p in pinned}
    out = {
        "version": VERSION, "labels": list(LABELS), "label_line": LABEL_LINE,
        "status": "POST_HOC_DIAGNOSTIC · NON_CITABLE · AI_DRAFTED",
        "post_hoc_statement": "Every figure here was computed after the D5 results were seen. They are descriptive "
                              "statistics on a 74-question benchmark with model-assisted gold (D-085), not "
                              "pre-registered tests and not the accuracy of the system in general.",
        "gates_unchanged": {"H1": "RULE_NOT_MET (D-092)", "H3": "RULE_NOT_MET (D-092)",
                            "note": "transcribed, not recomputed; nothing in this file bears on either rule"},
        "inputs_sha256": hashes, "inputs_vs_d5_freeze_pins": cross,
        "metrics": {
            "condition_compatible_recall_at_k": recall_block(bench, runs, score, root),
            "risk_coverage": risk_coverage_block(score),
            "unsupported_claim_rate": ucr_block(score),
            "ece": {**ece_block(runs), "labels": list(LABELS)},
        }}
    return _jsonable(out)


def render(res: dict) -> str:
    return json.dumps(res, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail unless the committed JSON equals a fresh run")
    a = ap.parse_args(argv)
    text = render(build())
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print(f"MISMATCH: {OUT.relative_to(ROOT)} is not what this script produces", file=sys.stderr)
            return 1
        print("OK: committed JSON equals a fresh run")
        return 0
    if any(v != "MATCHES_FREEZE" for v in json.loads(text)["inputs_vs_d5_freeze_pins"].values()):
        print("WARNING: an input differs from the D5 freeze pin; see inputs_vs_d5_freeze_pins", file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
