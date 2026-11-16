"""D5 benchmark scoring harness: router, slots, C block, OOD abstention, decision mode, citations, enforcement cost,
H1 and H3 verdicts, claim-audit sample and merge (S178 lane H1H3H). AI_DRAFTED, DRAFT. Not run on the benchmark.

Board items: T8-C01-R1 router branch accuracy + confusion matrix incl. X; T8-C03-R1 slot accuracy (diagnostic);
T8-C10-R1 C-block comparison + 'cannot separate' rate; T8-C13-R1 OOD abstain recall / false-abstain rate;
T8-C16-R1 citation precision / recall + 30-claim audit sample; T8-C16-R2 enforcement cost; T8-C22-R1 H3 analysis
with decision-mode F1 and zero-claim denominators; H1 (T8-C21-R1 scoring part) with exact McNemar reused from
``paired_stats`` / ``mcnemar_power``. D4 retrieval and risk-coverage are in ``d4_metrics``; ablations in ``ablation``.

Rules this module keeps (from ``reports/del5/d5_benchmark_preregistration_DRAFT.md`` and the two S178 amendment
drafts, which are PROPOSED until the lock):
- It scores; it never tunes. Every function is a pure function of the frozen rows, the run records and the EVD rows.
  The guard (``frozen_guard``) runs before any of it in the tool.
- Every metric carries ``prereg_status`` (``METRIC_REGISTRY``): BASE (S171 text), AMENDMENT_C* / D4 (proposed text),
  or EXPLORATORY_NOT_IN_PREREG. Nothing EXPLORATORY may be used for a claim unless the lock adds it first.
- A rate with an empty denominator is None, never 0 (UCR with no claim, F1 of a class that is absent on both sides,
  precision with no prediction). Counts and n are always shown; proportions carry Clopper-Pearson 95 % intervals.
- Missing inputs are counted, never imputed: no gold branch, no slot, no comparison label -> excluded from the
  denominator and reported; an UNRESOLVED H1 item blocks the H1 test until the rung-blind human check (amendment C5).
- H3 claims are scored by ``h3_independent`` only (independent of ``generation.claims`` / ``generation.enforce``);
  the enforcement checker's own counts are read from the run record and printed with the label the amendment asks for.

Run record (one JSON object per (qid, rung); written by the D5 runner, T8-C15-R1; schema ``RUN_RECORD_FIELDS``):
``qid``, ``rung``, ``answer`` (text); optional ``route`` {branch}, ``slots`` {ingredient_id, process_ids, target,
target_svar}, ``retrieval`` {arm1: [ranked EVD ids], arm2: [...]}, ``gold_compat`` {EVD id: compatibility vector},
``query_states_condition``, ``packet_ids``, ``decision`` {mode, precision, sufficiency, reason, evidence_basis,
per_option {name: {precision, sufficiency, process_id}}, comparison {verdict, order}, ood}, ``predicted_compare``,
``enforce`` {removed: [{reason}], fallback, mode_fallback}, ``s_outcome`` (true / false / "UNRESOLVED"),
``checker`` {numeric_claims, unsupported}, ``mode_violation``, ``latency_s``.
"""
from __future__ import annotations

import csv
import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.evaluation import claim_audit as CA
from culinarystate.evaluation import h3_independent as H3
from culinarystate.evaluation.d4_metrics import cp, parse_gold_range
from culinarystate.evaluation.mcnemar_power import describe_realised
from culinarystate.evaluation.paired_stats import mcnemar_exact, newcombe_paired, ucr_diff_upper95

VERSION = "d5_scoring@0.1"
STATUS = "AI_DRAFTED_HARNESS"
BLOCKS = ("S1", "S2", "P1", "P2", "P3", "C", "U", "X")
H1_BLOCKS = ("S1", "S2")
H3_BLOCKS = ("P1", "P2", "P3", "C")
GOLD_MODES = ("ANSWER", "ANSWER_SIMILAR_ONLY", "ABSTAIN", "COMPARE")
COMPARE_LABELS = ("ARM1_BETTER", "ARM2_BETTER", "CANNOT_SEPARATE")
COMPARE_PRED = COMPARE_LABELS + ("ABSTAINED", "UNRESOLVED")
ALPHA = 0.05
H3_OPTIONS = ("H3-A", "H3-B", "H3-C")
SIDEDNESS = ("one-sided", "two-sided")
H1_TREATMENT, H1_CONTROLS = "B4", ("B1", "B2")
H3_WORSE, H3_BETTER, H3_TEMPLATE = "B2", "B7", "B5T"
# amendment C6: EXACT for P1 and C, SIMILAR for P2; P3 (gold ABSTAIN, no cell evidence) takes the strict EXACT
MIN_RELEVANCE = {"P1": "EXACT", "C": "EXACT", "P2": "SIMILAR", "P3": "EXACT", "U": "EXACT", "X": "EXACT"}
AUDIT_SEED, AUDIT_RUNGS, AUDIT_PER_RUNG = "d5-h3-audit", ("B2", "B7", "B5T"), 10      # 30 claims (consensus size)
H3_BOOT_SEED, H3_N_BOOT = "d5-h3", 10_000
EXPLORATORY = "EXPLORATORY_NOT_IN_PREREG"
F12_CAVEAT = ("B7 and B5T abstain on P3 by construction: gold ABSTAIN on P3 means the ledger is silent for the cell, "
              "and B7's route is the same ledger lookup (REV-B F-12). P3 abstain recall of B7 / B5T is not evidence "
              "that an OOD detector works.")
CHECKER_LABEL = "enforcement checker (claims@0.2), not independent"
H3C_CAVEAT = ("UCR(B7) = 0 by construction; H3 as registered cannot fail whenever B2 has 3 or more questions with an "
              "unsupported claim (REV-B Q26 / G-07).")
RUN_RECORD_FIELDS = ("qid", "rung", "answer", "route", "slots", "retrieval", "gold_compat", "query_states_condition",
                     "packet_ids", "decision", "predicted_compare", "enforce", "s_outcome", "checker",
                     "mode_violation", "latency_s", "config")
SIMILAR_SUFFICIENCY = ("NEAR_PARTIAL",)
METRIC_REGISTRY: dict[str, dict[str, str]] = {
    "router_branch_accuracy": {"board": "T8-C01-R1", "prereg": "BASE §4 Descriptive ('router branch accuracy on all 80')"},
    "router_confusion_matrix": {"board": "T8-C01-R1", "prereg": EXPLORATORY + " (board acceptance; the prereg names accuracy only)"},
    "slot_accuracy": {"board": "T8-C03-R1", "prereg": EXPLORATORY + " (diagnostic)"},
    "retrieval_recall_compat_recall": {"board": "T8-C06-R1 / T9-C18-R1", "prereg": "PROPOSED_AMENDMENT_S178_D4 M1"},
    "retrieval_mrr": {"board": "T8-C06-R1", "prereg": EXPLORATORY},
    "retrieval_source_family": {"board": "T8-C06-R1", "prereg": "PROPOSED_AMENDMENT_S178 C7 (per source family), DIAGNOSTIC_ONLY"},
    "c_block_accuracy_cannot_separate": {"board": "T8-C10-R1", "prereg": EXPLORATORY + " (C is in H3; no C metric is named)"},
    "ood_abstain_recall_false_abstain": {"board": "T8-C13-R1", "prereg": "BASE §4 (P3 abstention) + PROPOSED_AMENDMENT_S178 C6 (false abstention)"},
    "citation_precision_recall": {"board": "T8-C16-R1", "prereg": EXPLORATORY},
    "checker_precision_recall_vs_humans": {"board": "T8-C16-R1", "prereg": "PROPOSED_AMENDMENT_S178 C6 (H3-A/H3-B audit)"},
    "enforcement_sentences_removed_fallback": {"board": "T8-C16-R2", "prereg": "PROPOSED_AMENDMENT_S178 C6 (coverage bullet)"},
    "answer_length": {"board": "T8-C16-R2", "prereg": EXPLORATORY},
    "h3_ucr_coverage_selective_risk": {"board": "T8-C22-R1", "prereg": "BASE §4 (UCR) + PROPOSED_AMENDMENT_S178 C6"},
    "h3_decision_test": {"board": "T8-C22-R1", "prereg": "BASE §4 (H3-C) or PROPOSED_AMENDMENT_S178 C6 (H3-A / H3-B): D-D5-5"},
    "decision_mode_f1": {"board": "T8-C22-R1", "prereg": EXPLORATORY + " (the prereg names 'mode violations' only)"},
    "mode_violations": {"board": "T8-C22-R1", "prereg": "BASE §4 Descriptive"},
    "latency": {"board": "-", "prereg": "BASE §4 Descriptive"},
    "h1_mcnemar": {"board": "T8-C21-R1", "prereg": "BASE §4 H1 (+ AMENDMENT C5 wording, power note)"},
    "d4_risk_coverage": {"board": "T9-C18-R1", "prereg": "PROPOSED_AMENDMENT_S178_D4 M2"},
    "d4_selective_risk_50_70_90": {"board": "T9-C18-R1", "prereg": EXPLORATORY},
    "d4_abstention_precision": {"board": "T9-C18-R1", "prereg": EXPLORATORY},
    "ablation_table": {"board": "T8-C21-R2", "prereg": EXPLORATORY + " (SSOT §245.13 subset; descriptive)"},
    "ux_blocks": {"board": "-", "prereg": "BASE §4 Descriptive (U and X blocks)"},
}


def tag(metric: str) -> dict:
    m = METRIC_REGISTRY[metric]
    return {"metric": metric, "board_item": m["board"], "prereg_status": m["prereg"]}


# ------------------------------------------------------------------ loading and validation

def ids(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [i for i in (s.strip() for s in x.split("|")) if i]
    return [str(i) for i in x if i]


def load_benchmark(paths: Sequence[Path | str]) -> list[dict]:
    """Rows of the benchmark CSV file(s); unique qids and known blocks are required."""
    rows: list[dict] = []
    for p in paths:
        with open(p, newline="", encoding="utf-8-sig") as fh:
            rows += [dict(r) for r in csv.DictReader(fh)]
    validate_rows(rows)
    return rows


def validate_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    dup = [q for q, n in Counter(str(r.get("qid")) for r in rows).items() if n > 1]
    bad = sorted({str(r.get("block")) for r in rows} - set(BLOCKS))
    if dup or bad:
        raise ValueError(f"benchmark rows invalid: duplicate qids {dup[:5]}, unknown blocks {bad}")


def load_runs(path: Path | str) -> dict[str, dict[str, dict]]:
    """``rung -> qid -> record`` from a JSONL file; (qid, rung) must be unique and fields known."""
    recs = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    return index_runs(recs)


def index_runs(recs: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for r in recs:
        unknown = sorted(set(r) - set(RUN_RECORD_FIELDS))
        if unknown or not r.get("qid") or not r.get("rung"):
            raise ValueError(f"run record invalid ({r.get('qid')}, {r.get('rung')}): unknown fields {unknown}")
        slot = out.setdefault(str(r["rung"]), {})
        if r["qid"] in slot:
            raise ValueError(f"duplicate run record ({r['qid']}, {r['rung']})")
        slot[str(r["qid"])] = dict(r)
    return out


def load_evd(path: Path | str) -> dict[str, dict]:
    """EVD rows from a JSONL ledger; the last line of an id wins (``LedgerStore.all_latest`` convention)."""
    out: dict[str, dict] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r
    return out


def by_block(rows: Sequence[Mapping[str, Any]], blocks: Iterable[str]) -> list[Mapping[str, Any]]:
    b = set(blocks)
    return [r for r in rows if str(r.get("block")) in b]


def rungs_for(records: Mapping[str, Mapping[str, Any]], qids: Iterable[str], field: str | None = None) -> list[str]:
    """Rungs with at least one record among ``qids`` (and, if given, carrying ``field``); others are not reported."""
    qs = set(qids)
    return sorted(r for r, rc in records.items() if any(q in qs and (field is None or field in rc[q]) for q in rc))


# ------------------------------------------------------------------ independent claim scoring

def cell_of(row: Mapping[str, Any]) -> dict:
    """The question's cell for ``h3_independent.row_relevance`` (both processes for a C question)."""
    cell: dict[str, list[str]] = {}
    if row.get("ingredient_id"):
        cell["ingredient_ids"] = [str(row["ingredient_id"])]
    if row.get("food"):
        cell["ingredient_names"] = [str(row["food"])]
    pids = [str(row[k]) for k in ("process_id", "process_id_2") if row.get(k)]
    pnames = [str(row[k]) for k in ("process", "process_2") if row.get(k)]
    if pids:
        cell["process_ids"] = pids
    if pnames:
        cell["process_names"] = pnames
    if ids(row.get("target_svars")):
        cell["target_svars"] = ids(row.get("target_svars"))
    if row.get("target"):
        cell["target_names"] = [str(row["target"])]
    return cell


def score_rung(rows: Sequence[Mapping[str, Any]], recs: Mapping[str, Mapping[str, Any]], evd: Mapping[str, Mapping],
               relatives: Mapping[str, Iterable[str]] | None = None,
               blocks: Iterable[str] = H3_BLOCKS + ("U", "X")) -> dict[str, dict]:
    """``qid -> h3_independent.score_answer`` for the rung's answers on the chosen blocks."""
    out = {}
    for r in by_block(rows, blocks):
        rec = recs.get(r["qid"])
        if rec is None:
            continue
        out[r["qid"]] = H3.score_answer(rec.get("answer") or "", evd=evd, cell=cell_of(r),
                                        packet_ids=rec.get("packet_ids"), ing_relatives=relatives,
                                        min_relevance=MIN_RELEVANCE[str(r["block"])])
    return out


def score_all(rows, records, evd, relatives=None) -> dict[str, dict[str, dict]]:
    return {rung: score_rung(rows, recs, evd, relatives) for rung, recs in sorted(records.items())}


# ------------------------------------------------------------------ T8-C01-R1 router

def router_branch_accuracy(rows: Sequence[Mapping[str, Any]], predicted: Mapping[str, str | None]) -> dict:
    """Branch accuracy (all questions with a gold branch), per block (X controls shown), confusion matrix, per-branch
    recall. Rows without ``gold_branch`` are excluded and counted (status INCOMPLETE_GOLD_BRANCH)."""
    gold = {r["qid"]: str(r.get("gold_branch") or "").strip().upper() for r in rows}
    scored = [r for r in rows if gold[r["qid"]]]
    missing = sorted(r["qid"] for r in rows if not gold[r["qid"]])
    pred = {q: (str(predicted.get(q)).upper() if predicted.get(q) else "NO_PREDICTION") for q in gold}
    labels_g = sorted({gold[r["qid"]] for r in scored})
    labels_p = sorted({pred[r["qid"]] for r in scored})
    conf = {g: {p: 0 for p in labels_p} for g in labels_g}
    for r in scored:
        conf[gold[r["qid"]]][pred[r["qid"]]] += 1
    ok = lambda rs: sum(pred[r["qid"]] == gold[r["qid"]] for r in rs)      # noqa: E731
    per_block = {b: cp(ok(rs), len(rs)) for b in BLOCKS if (rs := [r for r in scored if str(r["block"]) == b])}
    per_branch = {g: cp(conf[g].get(g, 0), sum(conf[g].values())) for g in labels_g}
    x = [r for r in scored if str(r["block"]) == "X"]
    return {**tag("router_branch_accuracy"), "status": "OK" if not missing else "INCOMPLETE_GOLD_BRANCH",
            "n_rows": len(rows), "n_scored": len(scored), "gold_branch_missing": missing,
            "accuracy": cp(ok(scored), len(scored)), "per_block": per_block,
            "confusion_matrix": {"rows_gold": labels_g, "cols_predicted": labels_p, "counts": conf,
                                 **{k: v for k, v in tag("router_confusion_matrix").items() if k != "metric"}},
            "per_gold_branch_recall": per_branch,
            "x_controls": {"n": len(x), "correct": ok(x),
                           "pairs": dict(Counter(f"{gold[r['qid']]}->{pred[r['qid']]}" for r in x))},
            "no_tuning": "router rules are frozen with the benchmark (code sha256 in the freeze record)"}


def predicted_branches(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]]
                       ) -> dict[str, str | None]:
    """The router branch per question from the run records; the router is rung-independent, so the records of
    different rungs must agree (a disagreement raises)."""
    out: dict[str, str | None] = {}
    for r in rows:
        seen = {str(b) for rec in records.values()
                if (b := (((rec.get(r["qid"]) or {}).get("route")) or {}).get("branch"))}
        if len(seen) > 1:
            raise ValueError(f"router branch differs between rungs for {r['qid']}: {sorted(seen)}")
        out[r["qid"]] = seen.pop() if seen else None
    return out


def live_router_branches(rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """Run the frozen rule router on each question text (deterministic, no LLM; C07 fallback F1 can run this)."""
    from culinarystate.decision.query_router import route
    return {r["qid"]: route(str(r.get("question") or ""))["branch"] for r in rows}


# ------------------------------------------------------------------ T8-C03-R1 slots

def slot_accuracy(rows: Sequence[Mapping[str, Any]], recs: Mapping[str, Mapping[str, Any]]) -> dict:
    """Per-slot exact accuracy (ingredient id; process id SET, both processes for C; target SVAR in the gold set).
    A row without that gold slot is excluded; a missing prediction is wrong (counted as ``missing_prediction``); a
    target given only as a name (no SVAR) is UNRESOLVED and not credited."""
    out: dict[str, Any] = {**tag("slot_accuracy"), "slots": {}}
    for slot in ("ingredient", "process", "target"):
        per_block: dict[str, dict] = {}
        tot = {"x": 0, "n": 0, "missing": 0, "unresolved": 0}
        for b in BLOCKS:
            x = n = miss = unres = 0
            for r in (r for r in rows if str(r["block"]) == b):
                s = (recs.get(r["qid"]) or {}).get("slots")
                if slot == "ingredient":
                    g = str(r.get("ingredient_id") or "")
                    if not g:
                        continue
                    p = (s or {}).get("ingredient_id")
                    ok = p == g
                elif slot == "process":
                    g = {str(r[k]) for k in ("process_id", "process_id_2") if r.get(k)}
                    if not g:
                        continue
                    p = None if s is None else s.get("process_ids")
                    ok = p is not None and set(ids(p)) == g
                else:
                    g = set(ids(r.get("target_svars")))
                    if not g:
                        continue
                    p = None if s is None else (s.get("target_svar") or None)
                    if p is None and s is not None and s.get("target"):
                        unres += 1
                    ok = p in g
                n += 1
                x += bool(ok)
                miss += p in (None, [], "") and not (slot == "target" and s is not None and s.get("target"))
            if n:
                per_block[b] = {**cp(x, n), "missing_prediction": miss, "target_name_without_svar": unres}
                tot["x"] += x
                tot["n"] += n
                tot["missing"] += miss
                tot["unresolved"] += unres
        out["slots"][slot] = {"all": {**cp(tot["x"], tot["n"]), "missing_prediction": tot["missing"],
                                      "target_name_without_svar": tot["unresolved"]}, "per_block": per_block}
    return out


# ------------------------------------------------------------------ T8-C10-R1 C block

def gold_compare_label(row: Mapping[str, Any]) -> tuple[str | None, str]:
    """Gold comparison of a C row: an explicit reviewed ``gold_compare`` wins; else it is derived from the two gold
    retention ranges (disjoint -> ordered, overlapping -> CANNOT_SEPARATE), tagged so the report can say so."""
    g = str(row.get("gold_compare") or "").strip().upper()
    if g in COMPARE_LABELS:
        return g, "REVIEWED_GOLD_COMPARE"
    r1, r2 = parse_gold_range(row.get("gold_retention_range")), parse_gold_range(row.get("gold_retention_range_2"))
    if not (r1 and r2):
        return None, "NO_GOLD_COMPARE"
    if r1[0] > r2[1]:
        return "ARM1_BETTER", "DERIVED_FROM_GOLD_RANGES"
    if r2[0] > r1[1]:
        return "ARM2_BETTER", "DERIVED_FROM_GOLD_RANGES"
    return "CANNOT_SEPARATE", "DERIVED_FROM_GOLD_RANGES"


def compare_label_from_decision(dec: Mapping[str, Any] | None, row: Mapping[str, Any]) -> str | None:
    """B7-style decision -> comparison label. SEPARATED + order -> the arm whose process id comes first;
    OVERLAPPING / INSUFFICIENT -> CANNOT_SEPARATE (the system declines to rank); ABSTAIN -> ABSTAINED."""
    if not dec:
        return None
    if dec.get("mode") == "ABSTAIN":
        return "ABSTAINED"
    comp = dec.get("comparison") or {}
    v = comp.get("verdict")
    if v in ("OVERLAPPING", "INSUFFICIENT"):
        return "CANNOT_SEPARATE"
    if v == "SEPARATED" and comp.get("order"):
        first = comp["order"][0]
        pid = ((dec.get("per_option") or {}).get(first) or {}).get("process_id", first)
        if pid == row.get("process_id"):
            return "ARM1_BETTER"
        if pid == row.get("process_id_2"):
            return "ARM2_BETTER"
    return None


def predicted_compare(rec: Mapping[str, Any] | None, row: Mapping[str, Any], scored: Mapping[str, Any] | None) -> str:
    if rec is None:
        return "UNRESOLVED"
    p = str(rec.get("predicted_compare") or "").strip().upper()
    if p in COMPARE_PRED:
        return p
    d = compare_label_from_decision(rec.get("decision"), row)
    if d:
        return d
    if scored and scored.get("abstained"):
        return "ABSTAINED"
    return "UNRESOLVED"


def c_block_scores(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]],
                   scored: Mapping[str, Mapping[str, Mapping[str, Any]]]) -> dict:
    """Per rung: exact agreement with the gold comparison, 'cannot separate' rate (rung and gold), wrong-order count,
    abstained and unresolved counts, confusion gold x predicted."""
    c_rows = by_block(rows, ("C",))
    gold = {r["qid"]: gold_compare_label(r) for r in c_rows}
    out: dict[str, Any] = {**tag("c_block_accuracy_cannot_separate"), "n_c": len(c_rows),
                           "gold_origin": dict(Counter(o for _, o in gold.values())),
                           "gold_cannot_separate": cp(sum(g == "CANNOT_SEPARATE" for g, _ in gold.values()),
                                                      sum(g is not None for g, _ in gold.values())),
                           "rungs": {}}
    for rung in rungs_for(records, gold):
        pred = {r["qid"]: predicted_compare(records[rung].get(r["qid"]), r, scored.get(rung, {}).get(r["qid"]))
                for r in c_rows}
        with_gold = [q for q in pred if gold[q][0] is not None]
        conf = {g: {p: 0 for p in COMPARE_PRED} for g in COMPARE_LABELS}
        for q in with_gold:
            conf[gold[q][0]][pred[q]] += 1
        wrong = sum(1 for q in with_gold if {gold[q][0], pred[q]} == {"ARM1_BETTER", "ARM2_BETTER"})
        resolved = [q for q in with_gold if pred[q] in COMPARE_LABELS]
        out["rungs"][rung] = {
            "agreement_with_gold": cp(sum(pred[q] == gold[q][0] for q in with_gold), len(with_gold)),
            "agreement_among_resolved": cp(sum(pred[q] == gold[q][0] for q in resolved), len(resolved)),
            "cannot_separate_rate": cp(sum(pred[q] == "CANNOT_SEPARATE" for q in pred), len(pred)),
            "wrong_order": wrong, "abstained": sum(p == "ABSTAINED" for p in pred.values()),
            "unresolved": sum(p == "UNRESOLVED" for p in pred.values()), "confusion_gold_x_pred": conf}
    out["note"] = ("UNRESOLVED = no comparison label could be read from the record (LLM free text needs the "
                   "rung-blind human label, as for H1 unresolved links); it is never counted as agreement.")
    return out


# ------------------------------------------------------------------ T8-C13-R1 OOD gate / abstention

def _gate_fired(rec: Mapping[str, Any] | None) -> bool | None:
    d = (rec or {}).get("decision") or {}
    if isinstance(d.get("ood"), bool):
        return d["ood"]
    flags = [((o or {}).get("support") or {}).get("ood") for o in (d.get("per_option") or {}).values()]
    flags = [f for f in flags if isinstance(f, bool)]
    return any(flags) if flags else None


def ood_abstention(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]],
                   scored: Mapping[str, Mapping[str, Mapping[str, Any]]]) -> dict:
    """Abstain recall on P3 (gold ABSTAIN), false-abstain rate on P1+P2 (and each), text abstention as the primary
    signal; decision-mode ABSTAIN and the OOD flag (precision cap) as secondary columns."""
    out: dict[str, Any] = {**tag("ood_abstain_recall_false_abstain"), "caveat": F12_CAVEAT, "rungs": {}}
    groups = {"P3": by_block(rows, ("P3",)), "P1+P2": by_block(rows, ("P1", "P2")), "P1": by_block(rows, ("P1",)),
              "P2": by_block(rows, ("P2",))}
    for rung in rungs_for(records, [r["qid"] for r in by_block(rows, ("P1", "P2", "P3"))]):
        sc, rc = scored.get(rung, {}), records[rung]
        entry = {}
        for g, rs in groups.items():
            have = [r for r in rs if r["qid"] in sc]
            ab = sum(bool(sc[r["qid"]]["abstained"]) for r in have)
            dm = [r for r in have if ((rc.get(r["qid"]) or {}).get("decision") or {}).get("mode")]
            gate = [f for f in (_gate_fired(rc.get(r["qid"])) for r in have) if f is not None]
            entry[g] = {"text_abstention": cp(ab, len(have)),
                        "decision_mode_abstain": cp(sum(rc[r["qid"]]["decision"]["mode"] == "ABSTAIN" for r in dm), len(dm)),
                        "ood_gate_fired": cp(sum(gate), len(gate))}
        entry["abstain_recall_P3"] = entry["P3"]["text_abstention"]
        entry["false_abstain_rate_P1_P2"] = entry["P1+P2"]["text_abstention"]
        out["rungs"][rung] = entry
    return out


# ------------------------------------------------------------------ T8-C22-R1 decision mode F1

def predicted_mode(rec: Mapping[str, Any] | None) -> tuple[str | None, str]:
    """Decision-layer mode -> gold-mode vocabulary. ANSWER is ANSWER when the evidence basis (or sufficiency) is
    DIRECT, ANSWER_SIMILAR_ONLY when it is similar-only (basis SIMILAR_ONLY, or sufficiency NEAR_PARTIAL); any
    other mode (ASK, RECOMMEND, ...) is ``OTHER:<mode>``. A text-only rung has no machine-readable mode (None)."""
    d = (rec or {}).get("decision")
    if not isinstance(d, Mapping) or not d.get("mode"):
        return None, "TEXT_ONLY"
    m = d["mode"]
    if m in ("ABSTAIN", "COMPARE"):
        return m, "DECISION_LAYER"
    if m == "ANSWER":
        basis = str(d.get("evidence_basis") or "").upper()
        suff = d.get("sufficiency") or d.get("reason")
        if basis == "DIRECT" or (not basis and suff == "DIRECT"):
            return "ANSWER", "DECISION_LAYER"
        if basis == "SIMILAR_ONLY" or (not basis and suff in SIMILAR_SUFFICIENCY):
            return "ANSWER_SIMILAR_ONLY", "DECISION_LAYER"
        return f"OTHER:ANSWER_{suff}", "DECISION_LAYER"
    return f"OTHER:{m}", "DECISION_LAYER"


def f1_table(gold: Sequence[str], pred: Sequence[str | None], classes: Sequence[str]) -> dict:
    """Per-class precision / recall / F1 with explicit zero-denominator handling, macro-F1 and accuracy.

    precision None when the class is never predicted; recall None when it never occurs in gold; F1 = 2TP / (2TP + FP
    + FN), None only when the class is absent on both sides (then it is left out of the macro mean and listed).
    Predictions outside ``classes`` count as misses for the gold class and as no class's false positive.
    """
    if len(gold) != len(pred):
        raise ValueError("gold and pred must have equal length")
    per, macro, excluded = {}, [], []
    for c in classes:
        tp = sum(g == c and p == c for g, p in zip(gold, pred))
        fp = sum(g != c and p == c for g, p in zip(gold, pred))
        fn = sum(g == c and p != c for g, p in zip(gold, pred))
        den = 2 * tp + fp + fn
        f1 = round(2 * tp / den, 4) if den else None
        per[c] = {"tp": tp, "fp": fp, "fn": fn, "n_gold": tp + fn, "n_pred": tp + fp,
                  "precision": round(tp / (tp + fp), 4) if tp + fp else None,
                  "recall": round(tp / (tp + fn), 4) if tp + fn else None, "f1": f1}
        (macro.append(f1) if f1 is not None else excluded.append(c))
    return {"per_class": per, "macro_f1": round(sum(macro) / len(macro), 4) if macro else None,
            "classes_excluded_absent_both_sides": excluded,
            "accuracy": cp(sum(g == p for g, p in zip(gold, pred)), len(gold)),
            "n_outside_classes": sum(p not in classes for p in pred)}


def mode_f1(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]],
            scored: Mapping[str, Mapping[str, Mapping[str, Any]]]) -> dict:
    """4-class decision-mode F1 for decision-layer rungs; binary abstain-vs-answer F1 (text abstention) for all."""
    sel = [r for r in by_block(rows, H3_BLOCKS) if str(r.get("gold_mode")) in GOLD_MODES]
    out: dict[str, Any] = {**tag("decision_mode_f1"), "classes": list(GOLD_MODES), "n_questions": len(sel), "rungs": {}}
    for rung in rungs_for(records, [r["qid"] for r in sel]):
        rc, sc = records[rung], scored.get(rung, {})
        have = [r for r in sel if r["qid"] in rc]
        modes = [predicted_mode(rc[r["qid"]]) for r in have]
        entry: dict[str, Any] = {"n": len(have)}
        if have and all(src == "DECISION_LAYER" for _, src in modes):
            entry["four_class"] = f1_table([str(r["gold_mode"]) for r in have], [m for m, _ in modes], GOLD_MODES)
            entry["other_modes"] = dict(Counter(m for m, _ in modes if m not in GOLD_MODES))
        else:
            entry["four_class"] = "NOT_DEFINED: no machine-readable decision mode for this rung"
        hs = [r for r in have if r["qid"] in sc]
        entry["binary_abstain"] = f1_table(["ABSTAIN" if str(r["gold_mode"]) == "ABSTAIN" else "ANSWERED" for r in hs],
                                           ["ABSTAIN" if sc[r["qid"]]["abstained"] else "ANSWERED" for r in hs],
                                           ("ABSTAIN", "ANSWERED"))
        out["rungs"][rung] = entry
    return out


# ------------------------------------------------------------------ T8-C16-R1 citations

def citation_metrics(rows: Sequence[Mapping[str, Any]], scored: Mapping[str, Mapping[str, Mapping[str, Any]]],
                     records: Mapping[str, Mapping[str, Mapping[str, Any]]]) -> dict:
    """Two readings, both EXPLORATORY_NOT_IN_PREREG:
    support-based (independent scorer): precision = citations that support their claim / citations bound to claims;
    recall = supported claims / all claims (numeric + directional, uncited included).
    gold-based (P1, P2, C): precision = cited ids in the reviewed gold ids / cited ids; recall = gold ids cited /
    gold ids. Micro sums; None when a denominator is 0."""
    out: dict[str, Any] = {**tag("citation_precision_recall"), "rungs": {}}
    gold_rows = {r["qid"]: r for r in by_block(rows, ("P1", "P2", "C"))}
    h3q = {r["qid"] for r in by_block(rows, H3_BLOCKS)}
    for rung in sorted(r for r in scored if any(q in h3q for q in scored[r])):
        pairs = sup_pairs = claims = sup_claims = 0
        cited_n = cited_in_gold = gold_n = gold_cited = 0
        for q, s in sorted(scored[rung].items()):
            if q not in h3q:
                continue
            for c in s["claims"]:
                claims += 1
                sup_claims += c["verdict"] == "SUPPORTED"
                pairs += len(c["cites"])
                sup_pairs += len(set(c["cites"]) & set(c.get("supporting_ids") or []))
            if q in gold_rows:
                g = set(ids(gold_rows[q].get("gold_evd_ids"))) | set(ids(gold_rows[q].get("gold_evd_ids_2")))
                cited = set(H3.EVD_ID.findall((records[rung].get(q) or {}).get("answer") or ""))
                cited_n += len(cited)
                cited_in_gold += len(cited & g)
                gold_n += len(g)
                gold_cited += len(g & cited)
        out["rungs"][rung] = {
            "support_based": {"precision": cp(sup_pairs, pairs), "recall": cp(sup_claims, claims)},
            "gold_based": {"precision": cp(cited_in_gold, cited_n), "recall": cp(gold_cited, gold_n)}}
    out["note"] = "pair-level and id-level counts are not independent draws; the intervals are indicative only"
    return out


# ------------------------------------------------------------------ T8-C16-R2 enforcement cost

def enforcement_cost(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]],
                     summaries: Mapping[str, Mapping[str, Any]]) -> dict:
    """Per rung over the H3 blocks: sentences removed (total, per reason, questions touched), template-fallback rate,
    mode fallbacks, answer length (words, characters), coverage on answerable questions (from the H3 summary)."""
    sel = by_block(rows, H3_BLOCKS)
    out: dict[str, Any] = {**tag("enforcement_sentences_removed_fallback"),
                           "answer_length_status": METRIC_REGISTRY["answer_length"]["prereg"], "rungs": {}}
    for rung in rungs_for(records, [r["qid"] for r in sel]):
        rc = records[rung]
        have = [rc[r["qid"]] for r in sel if r["qid"] in rc]
        enf = [x["enforce"] for x in have if isinstance(x.get("enforce"), Mapping)]
        words = [len((x.get("answer") or "").split()) for x in have]
        chars = [len(x.get("answer") or "") for x in have]
        entry: dict[str, Any] = {
            "n_answers": len(have),
            "words": {"mean": round(sum(words) / len(words), 2) if words else None,
                      "median": statistics.median(words) if words else None},
            "characters_mean": round(sum(chars) / len(chars), 2) if chars else None,
            "coverage_answerable": (summaries.get(rung) or {}).get("coverage_answerable")}
        if enf:
            reasons = Counter(str(x.get("reason")) for e in enf for x in (e.get("removed") or []))
            entry.update({"enforced_answers": len(enf), "sentences_removed": sum(reasons.values()),
                          "removed_by_reason": dict(sorted(reasons.items())),
                          "answers_with_removal": sum(bool(e.get("removed")) for e in enf),
                          "template_fallback": cp(sum(bool(e.get("fallback")) for e in enf), len(enf)),
                          "mode_fallback": sum(bool(e.get("mode_fallback")) for e in enf)})
        else:
            entry["enforcement"] = "NA (rung not enforced)"
        out["rungs"][rung] = entry
    return out


# ------------------------------------------------------------------ H3

def h3_summaries(rows, scored, *, evd: Mapping | None = None) -> dict:
    """``h3_independent.summarize_rung`` per rung over P1-P3 + C, per block, and per gold source family."""
    from culinarystate.evaluation.d4_metrics import gold_source_family
    sel = by_block(rows, H3_BLOCKS)
    modes = {r["qid"]: str(r.get("gold_mode")) for r in sel}
    out: dict[str, Any] = {}
    for rung, sc in sorted(scored.items()):
        res = {q: sc[q] for q in modes if q in sc}
        if not res:
            continue
        blk = {r["qid"]: str(r["block"]) for r in sel}
        entry = {"all": H3.summarize_rung(res, modes),
                 "per_block": {b: H3.summarize_rung({q: res[q] for q in res if blk[q] == b}, modes) for b in H3_BLOCKS}}
        if evd is not None:
            fam = {r["qid"]: gold_source_family(r, evd) for r in sel}
            entry["per_source_family"] = {f: H3.summarize_rung({q: res[q] for q in res if fam[q] == f}, modes)
                                          for f in sorted(set(fam.values()))}
        out[rung] = entry
    return out


def _sign_test(worse: Mapping[str, Mapping], better: Mapping[str, Mapping], sidedness: str) -> dict:
    cmpd = H3.compare_rungs(worse, better)
    b, c = cmpd["b_worse_only_unsupported"], cmpd["c_better_only_unsupported"]
    alt = "greater" if sidedness == "one-sided" else "two-sided"
    p = H3.sign_test_exact(b, c, alternative=alt)
    n_min = next(m for m in range(1, 100) if H3.sign_test_exact(m, 0, alternative=alt) <= ALPHA)
    return {**cmpd, "sidedness": sidedness, "p": p, "min_discordant_for_alpha": n_min,
            "can_be_significant": b + c >= n_min, "passes": b > c and p <= ALPHA,
            "statement": (f"cannot be shown at this n: {b + c} discordant questions < {n_min}" if b + c < n_min else
                          "B7 better (p <= 0.05)" if b > c and p <= ALPHA else "not shown at this n")}


def weighted_human_unsupported(key_rows: Sequence[Mapping[str, Any]], labels: Mapping[str, bool]) -> dict:
    """Design-weighted human-judged unsupported share per rung (weight = stratum population / sampled)."""
    out: dict[str, Any] = {}
    for rung in sorted({str(r["rung"]) for r in key_rows}):
        num = den = 0.0
        n = 0
        for r in key_rows:
            if str(r["rung"]) != rung or r["audit_id"] not in labels:
                continue
            w = float(r["stratum_population"]) / float(r["stratum_sampled"])
            num += w * bool(labels[r["audit_id"]])
            den += w
            n += 1
        out[rung] = {"n_labelled": n, "weighted_unsupported_share": round(num / den, 4) if den else None}
    return out


def h3_verdicts(rows, scored, *, audit_shares: Mapping[str, Mapping[str, Any]] | None = None,
                n_boot: int = H3_N_BOOT, boot_seed: str = H3_BOOT_SEED) -> dict:
    """H3 under every registered option and sidedness (the lock picks one, D-D5-5 / D-D5-6).

    H3-C (S171 base): bootstrap one-sided 95 % upper bound of UCR(B7) - UCR(B2) < 0 AND P3 abstention B7 >= B2.
    H3-B: exact sign test passes AND the P3 condition. H3-A: H3-B AND the human-audit veto does not fire (the
    design-weighted human-judged unsupported share of B7 is lower than that of B2); without labels: PENDING.
    """
    sel = by_block(rows, H3_BLOCKS)
    modes = {r["qid"]: str(r.get("gold_mode")) for r in sel}
    p3 = {r["qid"] for r in by_block(sel, ("P3",))}
    w, b = scored.get(H3_WORSE), scored.get(H3_BETTER)
    out: dict[str, Any] = {**tag("h3_decision_test"), "worse": H3_WORSE, "better": H3_BETTER}
    if w is None or b is None:
        out["status"] = f"NOT_COMPUTED: rung {H3_WORSE} or {H3_BETTER} missing"
        return out
    w = {q: w[q] for q in modes if q in w}
    b = {q: b[q] for q in modes if q in b}
    qids = sorted(set(w) & set(b))
    abst = {name: H3.summarize_rung({q: s[q] for q in s if q in p3}, modes)["abstention_on_abstain_gold"]
            for name, s in ((H3_WORSE, w), (H3_BETTER, b))}
    p3_ok = (abst[H3_BETTER]["rate"] is not None and abst[H3_WORSE]["rate"] is not None
             and abst[H3_BETTER]["rate"] >= abst[H3_WORSE]["rate"])
    tuples = lambda s: [(s[q]["n_numeric"], s[q]["n_numeric_unsupported"]) for q in qids]     # noqa: E731
    upper = ucr_diff_upper95(tuples(b), tuples(w), n_boot=n_boot, seed=boot_seed) if qids else None
    out.update({"n_paired": len(qids), "p3_abstention": abst, "p3_condition_met": p3_ok,
                "bootstrap_ucr_diff_B7_minus_B2_upper95": upper,
                "bootstrap": {"seed": boot_seed, "n_boot": n_boot, "role": "decision rule only under H3-C; else descriptive"}})
    veto = None
    if audit_shares and H3_WORSE in audit_shares and H3_BETTER in audit_shares:
        sw = audit_shares[H3_WORSE]["weighted_unsupported_share"]
        sb = audit_shares[H3_BETTER]["weighted_unsupported_share"]
        veto = None if sw is None or sb is None else not (sb < sw)
    out["audit_veto_fires"] = veto
    out["options"] = {}
    for side in SIDEDNESS:
        st = _sign_test(w, b, side)
        out["options"][f"H3-B|{side}"] = {"sign_test": st, "meets_rule": st["passes"] and p3_ok}
        out["options"][f"H3-A|{side}"] = {"sign_test": st,
                                          "meets_rule": ("PENDING_HUMAN_AUDIT" if veto is None and st["passes"] and p3_ok
                                                         else st["passes"] and p3_ok and veto is False)}
    out["options"]["H3-C"] = {"meets_rule": upper is not None and upper < 0 and p3_ok, "caveat": H3C_CAVEAT}
    t = scored.get(H3_TEMPLATE)
    if t is not None:
        out["B5T_vs_B7_descriptive"] = {side: _sign_test({q: t[q] for q in modes if q in t}, b, side) for side in SIDEDNESS}
    return out


def checker_ucr(records: Mapping[str, Mapping[str, Mapping[str, Any]]], qids: Iterable[str]) -> dict:
    """claims@0.2 UCR as stored by the runner, printed only with its label."""
    out = {}
    qs = list(qids)
    for rung in rungs_for(records, qs, "checker"):
        rc = records[rung]
        ch = [rc[q]["checker"] for q in qs if q in rc and isinstance(rc[q].get("checker"), Mapping)]
        n = sum(int(c.get("numeric_claims") or 0) for c in ch)
        u = sum(int(c.get("unsupported") or 0) for c in ch)
        out[rung] = {"label": CHECKER_LABEL, "n_answers": len(ch), "numeric_claims": n, "unsupported": u,
                     "ucr": round(u / n, 4) if n else None}
    return out


def mode_violations(records, qids) -> dict:
    qs = list(qids)
    return {**tag("mode_violations"),
            "rungs": {rung: cp(sum(bool(rc[q].get("mode_violation")) for q in qs if q in rc and "mode_violation" in rc[q]),
                               sum(1 for q in qs if q in rc and "mode_violation" in rc[q]))
                      for rung, rc in sorted(records.items()) if rung in rungs_for(records, qs, "mode_violation")}}


# ------------------------------------------------------------------ H1

def s1_outcome(detail: Mapping[str, Any]) -> bool | str:
    """S1 outcome from ``h1_rungs.score_s1_detail``: a name the shared linker cannot resolve makes the item
    UNRESOLVED (amendment C5: it goes to the rung-blind human check before unblinding), never silently False."""
    return "UNRESOLVED" if detail.get("link_failed") else bool(detail.get("correct"))


def s2_outcome(answer: str, gold_proc: str, proc) -> bool | str:
    """S2 outcome with the same first-verb rule as ``h1_rungs.score_s2``; an unmapped verb is UNRESOLVED."""
    m = re.search(r"[a-z][a-z-]*", (answer or "").lower())
    if not m:
        return False
    pid = proc(m.group(0))
    return "UNRESOLVED" if pid is None else pid == gold_proc


def apply_human_resolutions(records: Mapping[str, Mapping[str, Mapping[str, Any]]],
                            resolved: Mapping[tuple[str, str], bool]) -> dict[str, dict[str, dict]]:
    """Replace UNRESOLVED S outcomes by the rung-blind human verdict ``{(qid, rung): bool}``. Only UNRESOLVED items
    may be resolved; a resolution for any other item raises (no re-scoring of decided items)."""
    out = {rung: {q: dict(r) for q, r in rc.items()} for rung, rc in records.items()}
    for (q, rung), v in resolved.items():
        rec = out.get(rung, {}).get(q)
        if rec is None or rec.get("s_outcome") != "UNRESOLVED" or not isinstance(v, bool):
            raise ValueError(f"({q}, {rung}) is not an UNRESOLVED item or the verdict is not boolean")
        rec["s_outcome"] = v
    return out


def h1_analysis(rows: Sequence[Mapping[str, Any]], records: Mapping[str, Mapping[str, Mapping[str, Any]]], *,
                alpha: float = ALPHA) -> dict:
    """H1 (S1 + S2 pooled): accuracy per rung, B4 vs B1 and B4 vs B2 paired exact McNemar (two-sided) with the
    Newcombe interval (descriptive), 'cannot be significant' statement, gold-origin label. Any UNRESOLVED or
    missing outcome in a compared rung blocks the test (the rung-blind human check comes first)."""
    from culinarystate.evaluation.h1_independence import gold_independence_report
    sel = by_block(rows, H1_BLOCKS)
    qids = [r["qid"] for r in sel]
    block = {r["qid"]: str(r["block"]) for r in sel}

    def outcome(rung: str, q: str) -> Any:
        rec = (records.get(rung) or {}).get(q)
        v = None if rec is None else rec.get("s_outcome")
        return v if v in (True, False) else ("UNRESOLVED" if v == "UNRESOLVED" else "MISSING")

    out: dict[str, Any] = {**tag("h1_mcnemar"), "n_questions": len(sel), "gold_independence": gold_independence_report(sel),
                           "accuracy": {}, "comparisons": {}}
    for rung in rungs_for(records, qids):
        oc = {q: outcome(rung, q) for q in qids}
        ok = [q for q in qids if oc[q] in (True, False)]
        out["accuracy"][rung] = {"all": cp(sum(oc[q] is True for q in ok), len(ok)),
                                 **{b: cp(sum(oc[q] is True for q in ok if block[q] == b), sum(block[q] == b for q in ok))
                                    for b in H1_BLOCKS},
                                 "unresolved": sum(v == "UNRESOLVED" for v in oc.values()),
                                 "missing": sum(v == "MISSING" for v in oc.values()),
                                 "unresolved_rate": cp(sum(v == "UNRESOLVED" for v in oc.values()), len(qids))}
    verdicts = []
    for ctrl in H1_CONTROLS:
        key = f"{H1_TREATMENT}_vs_{ctrl}"
        if H1_TREATMENT not in records or ctrl not in records:
            out["comparisons"][key] = {"status": "NOT_COMPUTED_RUNG_MISSING"}
            verdicts.append(None)
            continue
        x = {q: outcome(H1_TREATMENT, q) for q in qids}
        y = {q: outcome(ctrl, q) for q in qids}
        blocked = [q for q in qids if x[q] not in (True, False) or y[q] not in (True, False)]
        if blocked:
            out["comparisons"][key] = {"status": "BLOCKED_UNRESOLVED_OR_MISSING", "n_blocked": len(blocked)}
            verdicts.append(None)
            continue
        res = {}
        for name, qs in (("pooled", qids), *((b, [q for q in qids if block[q] == b]) for b in H1_BLOCKS)):
            a = sum(x[q] and y[q] for q in qs)
            bb = sum(x[q] and not y[q] for q in qs)
            c = sum(y[q] and not x[q] for q in qs)
            d = len(qs) - a - bb - c
            nw = newcombe_paired(a, bb, c, d) if qs else None
            res[name] = {"n": len(qs), "a_both": a, "b_treatment_only": bb, "c_control_only": c, "d_neither": d,
                         "diff": round((bb - c) / len(qs), 4) if qs else None,
                         "newcombe95_descriptive": [round(nw[0], 4), round(nw[1], 4)] if nw else None,
                         "p_exact_two_sided": mcnemar_exact(bb, c),
                         "realised": describe_realised(len(qs), bb, c, alpha) if qs else None,
                         "role": "decision" if name == "pooled" else "descriptive only (per block)"}
        pooled = res["pooled"]
        sig = pooled["b_treatment_only"] > pooled["c_control_only"] and pooled["p_exact_two_sided"] <= alpha
        out["comparisons"][key] = {"status": "OK", **res, "treatment_better_and_significant": sig}
        verdicts.append(sig)
    if any(v is None for v in verdicts):
        code = "NOT_COMPUTED"
    else:
        code = "RULE_MET" if all(verdicts) else "RULE_NOT_MET"
    out["verdict"] = {"code": code, "rule": "B4 > B1 and B4 > B2, both exact two-sided McNemar p <= 0.05 (intersection-union)",
                      "wording_base": {"RULE_MET": "supported", "RULE_NOT_MET": "not supported at this n"}.get(code),
                      "wording_amendment_C5": {"RULE_MET": "meets the pre-registered pilot rule",
                                               "RULE_NOT_MET": "not shown at this n"}.get(code),
                      "gold_label": out["gold_independence"]["label"]}
    return out


# ------------------------------------------------------------------ T8-C16-R1 audit sample and merge

def audit_answers(rows, records, scored, rungs: Sequence[str] = AUDIT_RUNGS) -> list[dict]:
    qtext = {r["qid"]: r.get("question", "") for r in rows}
    out = []
    for rung in rungs:
        for q, s in sorted((scored.get(rung) or {}).items()):
            if q not in qtext or q not in (records.get(rung) or {}):
                continue
            rec = records[rung][q]
            ch = rec.get("checker") if isinstance(rec.get("checker"), Mapping) else None
            out.append({"qid": q, "rung": rung, "question": qtext[q], "answer": rec.get("answer") or "", "scored": s,
                        "checker_unsupported": None if ch is None else int(ch.get("unsupported") or 0)})
    return out


def audit_sample(rows, records, scored, *, per_rung: int = AUDIT_PER_RUNG, seed: str = AUDIT_SEED,
                 rungs: Sequence[str] = AUDIT_RUNGS) -> dict:
    """Seeded, stratified, rung-blind claim sample (claim_audit) over the H3 blocks: 3 rungs x 10 = 30 claims."""
    h3q = {r["qid"] for r in by_block(rows, H3_BLOCKS)}
    sc = {rung: {q: s for q, s in (scored.get(rung) or {}).items() if q in h3q} for rung in rungs}
    items = CA.audit_items(audit_answers(rows, records, sc, rungs))
    return CA.stratified_audit_sample(items, per_rung=per_rung, seed=seed, rungs=rungs)


def audit_report(key_rows: Sequence[Mapping[str, Any]], sheet_a: Sequence[Mapping[str, str]],
                 sheet_b: Sequence[Mapping[str, str]], summaries: Mapping[str, Mapping[str, Any]] | None = None) -> dict:
    """After both humans labelled: reviewer agreement, checker precision / recall (weighted), the design-weighted
    human-judged unsupported share per rung next to the scorer UCR, and human-vs-scorer agreement."""
    merged = CA.merge_reviewer_labels(sheet_a, sheet_b)
    labels = merged["agreed"]
    quality = CA.estimate_checker_quality(key_rows, labels)
    shares = weighted_human_unsupported(key_rows, labels)
    agree = {}
    for scorer in ("independent", "s173_checker"):
        rs = [r for r in key_rows if r["audit_id"] in labels]
        flag = (lambda r: str(r["independent_verdict"]) != "SUPPORTED") if scorer == "independent" else \
            (lambda r: str(r["checker_flags_answer"]).lower() == "true")
        agree[scorer] = cp(sum(flag(r) == bool(labels[r["audit_id"]]) for r in rs), len(rs))
    for rung, s in shares.items():
        s["independent_scorer_ucr"] = ((summaries or {}).get(rung) or {}).get("ucr")
    return {**tag("checker_precision_recall_vs_humans"), "reviewer_raw_agreement": merged["raw_agreement"],
            "n_agreed": len(labels), "disputed": merged["disputed"], "unusable": merged["unusable"],
            "checker_quality": quality, "human_weighted_unsupported_share": shares,
            "human_vs_automatic_raw_agreement": agree,
            "note": "disputed items are reconciled jointly by the humans before this is final; labels are human, never AI"}


# ------------------------------------------------------------------ U and X blocks

def ux_blocks(rows, records, scored) -> dict:
    """U and X descriptive: per rung, abstention on abstain / refuse-type gold, numeric claims made there."""
    out: dict[str, Any] = {**tag("ux_blocks"), "rungs": {}}
    sel = by_block(rows, ("U", "X"))
    refuse = [r for r in sel if re.match(r"^(ABSTAIN|REFUSE)", str(r.get("gold_mode") or "").upper())]
    for rung in rungs_for(records, [r["qid"] for r in sel]):
        sc = scored.get(rung, {})
        have = [r for r in refuse if r["qid"] in sc]
        out["rungs"][rung] = {
            "abstain_on_abstain_or_refuse_gold": cp(sum(bool(sc[r["qid"]]["abstained"]) for r in have), len(have)),
            "numbers_on_abstain_or_refuse_gold": sum(sc[r["qid"]]["n_numeric"] > 0 for r in have),
            "per_block_n": {b: sum(1 for r in sel if str(r["block"]) == b and r["qid"] in sc) for b in ("U", "X")}}
    return out
