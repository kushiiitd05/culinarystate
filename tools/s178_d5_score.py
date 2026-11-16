#!/usr/bin/env python3
"""S178 H1H3H: D5 scoring harness (router, slots, retrieval, C block, OOD, mode F1, citations, enforcement cost, H1,
H3, D4 risk-coverage, ablations). AI_DRAFTED. Nothing here is a result until a human-approved freeze exists.

  # synthetic fixture only (stamps every output SYNTHETIC_FIXTURE_NOT_A_RESULT):
  python tools/s178_d5_score.py --fixture [--out-dir reports/s178/d5_harness]

  # frozen benchmark (refuses unless the freeze record is human-approved and every hash matches):
  python tools/s178_d5_score.py --freeze-record registry/freezes/<D5 freeze>.json \\
      --benchmark <frozen csv> [...] --runs <run jsonl> --evd ledgers/data/EVD.jsonl --relatives <json> \\
      --h3-option H3-A|H3-B|H3-C --sidedness one-sided|two-sided --d4-error E1|E2 --out-dir reports/del5/<dir> \\
      [--router-live] [--ablation-runs <jsonl>] [--audit-key K --audit-sheet-a A --audit-sheet-b B] [--audit-dir D]

The fixture mode reads only tests/fixtures/d5_synthetic/ (manifest-hashed, SYN- qids, EVD-99xxxx ids). The real mode
runs ``frozen_guard.require_real_inputs`` before reading any row: freeze record FREEZE_D5_BENCHMARK, status FROZEN,
both humans approved (no AI marker), every input listed with a matching sha256, scorer code and prereg bytes pinned,
the record committed in git. Outputs are counts and rates only; deterministic (no timestamp inside).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation import ablation as AB  # noqa: E402
from culinarystate.evaluation import claim_audit as CA  # noqa: E402
from culinarystate.evaluation import d4_metrics as D4  # noqa: E402
from culinarystate.evaluation import d5_scoring as DS  # noqa: E402
from culinarystate.evaluation import frozen_guard as FG  # noqa: E402

TOOL_VERSION = "s178-d5-score-0.1.0-draft"
FIXTURE_FILES = ("benchmark_synthetic.csv", "runs_synthetic.jsonl", "evd_synthetic.jsonl", "relatives_synthetic.json",
                 "ablation_runs_synthetic.jsonl")
FIXTURE_OUT = "reports/s178/d5_harness"
OUT_NAME = "d5_scoring_result.json"


def git_committed(path: Path) -> bool:
    """Read-only: the file is tracked and has no uncommitted change."""
    try:
        rel = Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
        clean = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", rel], capture_output=True).returncode == 0
        return tracked and clean
    except (ValueError, OSError):
        return False


def score(rows, records, evd, relatives, *, ablation_records=None, audit=None, d4_error="E1", n_boot=None,
          live_router=False) -> dict:
    """Every section of the harness on already-guarded inputs."""
    nb = {} if n_boot is None else {"n_boot": n_boot}
    scored = DS.score_all(rows, records, evd, relatives)
    summaries = DS.h3_summaries(rows, scored, evd=evd)
    h3q = [r["qid"] for r in DS.by_block(rows, DS.H3_BLOCKS)]
    branches = DS.live_router_branches(rows) if live_router else DS.predicted_branches(rows, records)
    res = {
        "router": DS.router_branch_accuracy(rows, branches),
        "slots": {rung: DS.slot_accuracy(rows, rc) for rung, rc in sorted(records.items())
                  if any("slots" in x for x in rc.values())},
        "retrieval_d4_m1": D4.retrieval_table(rows, records, evd, **nb),
        "c_block": DS.c_block_scores(rows, records, scored),
        "ood_abstention": DS.ood_abstention(rows, records, scored),
        "decision_mode_f1": DS.mode_f1(rows, records, scored),
        "citations": DS.citation_metrics(rows, scored, records),
        "enforcement_cost": DS.enforcement_cost(rows, records, {k: v["all"] for k, v in summaries.items()}),
        "h3_summaries": {**DS.tag("h3_ucr_coverage_selective_risk"), "rungs": summaries,
                         "enforcement_checker_ucr": DS.checker_ucr(records, h3q)},
        "h3_verdicts": DS.h3_verdicts(rows, scored, audit_shares=(audit or {}).get("human_weighted_unsupported_share"),
                                      **({"n_boot": n_boot} if n_boot else {})),
        "h1": DS.h1_analysis(rows, records),
        "mode_violations": DS.mode_violations(records, h3q),
        "latency": {**DS.tag("latency"), "rungs": {rung: D4.latency_summary(records[rung], h3q)
                                                   for rung in DS.rungs_for(records, h3q, "latency_s")}},
        "ux_blocks": DS.ux_blocks(rows, records, scored),
    }
    d4 = {}
    for rung in sorted(records):
        rc = records[rung]
        if not any(isinstance(x.get("decision"), dict) for x in rc.values()):
            continue
        prim = D4.risk_coverage(rows, rc, scored.get(rung, {}), error_option=d4_error)
        sec = D4.risk_coverage(rows, rc, scored.get(rung, {}), order=D4.SECONDARY_ORDER, error_option=d4_error)
        d4[rung] = {"primary_precision_class": prim, "secondary_sufficiency_mode": sec,
                    "selective_risk_primary": D4.selective_risk_at_coverage(prim),
                    "abstention_precision_recall": D4.abstention_precision_recall(rows, scored.get(rung, {}))}
    res["d4_m2_risk_coverage"] = {"error_option": d4_error, "decision_layer_rungs": d4,
                                  "reference_all_answered": {rung: D4.all_answered_risk(rows, scored.get(rung, {}), error_option=d4_error)
                                                             for rung in DS.rungs_for(records, h3q)},
                                  "random_abstention_expected_risk": "equals the all-answered risk of the same rung",
                                  "not_reported_by_design": D4.NOT_REPORTED}
    smp = DS.audit_sample(rows, records, scored)
    res["audit_sample"] = {**{k: v for k, v in smp.items() if k != "sample"}, "n_sampled": len(smp["sample"]),
                           **{k: v for k, v in DS.tag("checker_precision_recall_vs_humans").items() if k != "metric"}}
    res["audit"] = audit or {"status": "PENDING_HUMAN_LABELS: Kush and Parv label the rung-blind sheets; the H3-A veto "
                                       "is PENDING until then"}
    if ablation_records is not None:
        res["ablation"] = AB.table_from_records(rows, ablation_records, evd, relatives)
    else:
        res["ablation"] = {**DS.tag("ablation_table"), "status": "NOT_RUN: no ablation records given"}
    return res


def write_audit_sheets(rows, records, evd, relatives, out_dir: Path) -> dict:
    scored = DS.score_all(rows, records, evd, relatives)
    smp = DS.audit_sample(rows, records, scored)
    w = CA.write_audit_files(smp["sample"], evd, out_dir, seed=DS.AUDIT_SEED)
    return {"n_items": w["n_items"], "sha256": w["sha256"], "design": smp["design"], "shortfalls": smp["shortfalls"]}


def _md(res: dict, mode: str, header: list[str]) -> str:
    L = list(header)
    r = res["router"]
    L += ["", "## Router branch accuracy (T8-C01-R1)", "",
          f"accuracy {r['accuracy']['x']}/{r['accuracy']['n']} = {r['accuracy']['rate']} (CP95 {r['accuracy']['cp95']}); "
          f"status {r['status']}; X controls {r['x_controls']['correct']}/{r['x_controls']['n']}"]
    h1 = res["h1"]
    L += ["", "## H1 (exact two-sided McNemar)", "", f"verdict {h1['verdict']['code']} ({h1['verdict']['wording_base']}); "
          f"gold label {h1['verdict']['gold_label']}"]
    for k, v in h1["comparisons"].items():
        if v.get("status") == "OK":
            p = v["pooled"]
            L.append(f"- {k}: b {p['b_treatment_only']} / c {p['c_control_only']}, p {round(p['p_exact_two_sided'], 4)}, "
                     f"diff {p['diff']} (Newcombe {p['newcombe95_descriptive']}): {p['realised']['statement']}")
        else:
            L.append(f"- {k}: {v.get('status')}")
    h3 = res["h3_verdicts"]
    L += ["", "## H3 (independent scorer; all options, the lock picks one)", ""]
    for k, v in h3.get("options", {}).items():
        st = v.get("sign_test")
        L.append(f"- {k}: meets rule = {v['meets_rule']}" + (f"; b {st['b_worse_only_unsupported']} / c "
                                                             f"{st['c_better_only_unsupported']}, p {round(st['p'], 4)}: {st['statement']}" if st else
                                                             f"; bootstrap upper95 {h3.get('bootstrap_ucr_diff_B7_minus_B2_upper95')}"))
    L += ["", "## D4 risk-coverage (primary score), decision-layer rungs", ""]
    for rung, v in res["d4_m2_risk_coverage"]["decision_layer_rungs"].items():
        pts = "; ".join(f"{p['threshold']} cov {p['coverage']} risk {p['risk']['x']}/{p['risk']['n']}" for p in v["primary_precision_class"]["points"])
        L.append(f"- {rung}: {pts}")
    L += ["", "## Retrieval Recall@K (pooled P1+P2+C)", ""]
    for rung, v in res["retrieval_d4_m1"]["rungs"].items():
        if v.get("status") != "OK":
            L.append(f"- {rung}: {v.get('status')}")
            continue
        pool = v["blocks"]["pooled_P1_P2_C"]
        L.append(f"- {rung}: n {pool['n_questions']}; " + "; ".join(
            f"R@{k} {pool[f'K={k}']['recall']['mean']} (compat {pool[f'K={k}']['compat_recall']['mean']})" for k in D4.K_VALUES)
            + f"; MRR {pool['mrr']['mean']} (EXPLORATORY)")
    L += ["", "## C block, OOD abstention, enforcement", ""]
    for rung, v in res["c_block"]["rungs"].items():
        L.append(f"- C {rung}: agreement {v['agreement_with_gold']['x']}/{v['agreement_with_gold']['n']}, cannot separate "
                 f"{v['cannot_separate_rate']['x']}/{v['cannot_separate_rate']['n']}, wrong order {v['wrong_order']}, "
                 f"unresolved {v['unresolved']}")
    for rung, v in res["ood_abstention"]["rungs"].items():
        a, f = v["abstain_recall_P3"], v["false_abstain_rate_P1_P2"]
        L.append(f"- OOD {rung}: P3 abstain {a['x']}/{a['n']}; false abstain P1+P2 {f['x']}/{f['n']}")
    for rung, v in res["enforcement_cost"]["rungs"].items():
        if "sentences_removed" in v:
            L.append(f"- enforcement {rung}: removed {v['sentences_removed']} sentences, fallback "
                     f"{v['template_fallback']['x']}/{v['template_fallback']['n']}, mean words {v['words']['mean']}")
    if "table" in res["ablation"]:
        L += ["", "## Ablations (EXPLORATORY, descriptive)", ""]
        for t in res["ablation"]["table"]:
            L.append(f"- {t['ssot_245_13']}: {t['status']}" + (f" (errors added {t['paired_E1']['errors_added']}, removed "
                                                               f"{t['paired_E1']['errors_removed']})" if t["status"] == "RUN" else
                                                               f" ({t.get('reason')})"))
    L += ["", f"Full detail: `{OUT_NAME if mode == 'REAL' else 'SYNTHETIC_FIXTURE_' + OUT_NAME}` (every section carries "
          "`prereg_status`)."]
    return "\n".join(L) + "\n"


def _write(path: Path, text: str) -> str:
    """Write once; an identical re-run is allowed, a different one refuses (no silent overwrite)."""
    data = text.encode("utf-8")
    if path.exists() and path.read_bytes() != data:
        raise SystemExit(f"refusing to overwrite {path} with different content; remove it deliberately first")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def run_fixture(out_dir: Path, n_boot: int | None = None) -> dict:
    fdir = ROOT / FG.FIXTURE_DIR
    guard = FG.require_fixture_inputs(fdir, [fdir / f for f in FIXTURE_FILES])
    rows = DS.load_benchmark([fdir / "benchmark_synthetic.csv"])
    FG.assert_synthetic_rows(rows)
    evd = DS.load_evd(fdir / "evd_synthetic.jsonl")
    FG.assert_synthetic_evd(evd)
    records = DS.load_runs(fdir / "runs_synthetic.jsonl")
    if any(not FG.SYNTHETIC_QID.match(q) for rc in records.values() for q in rc):
        raise FG.GuardRefused(["NON_SYNTHETIC_RUN_RECORD"])
    relatives = json.loads((fdir / "relatives_synthetic.json").read_text(encoding="utf-8"))
    abl: dict = {}
    for line in (fdir / "ablation_runs_synthetic.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            abl.setdefault(rec["config"], {})[rec["qid"]] = rec
    res = score(rows, records, evd, relatives, ablation_records=abl, n_boot=n_boot)
    with tempfile.TemporaryDirectory() as td:                    # sheets hold (synthetic) answer text: never committed
        res["audit_sample"]["sheets"] = write_audit_sheets(rows, records, evd, relatives, Path(td) / "sheets")
    meta = {"tool": TOOL_VERSION, "mode": "FIXTURE", "guard": guard, "status": DS.STATUS,
            "metric_registry": DS.METRIC_REGISTRY,
            "warning": "SYNTHETIC FIXTURE: invented questions, answers, ids and values; not a D5 result; no number here "
                       "may be quoted as a finding"}
    out = FG.stamp({"meta": meta, **res})
    FG.assert_stamped(out)
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    sha_json = _write(out_dir / f"SYNTHETIC_FIXTURE_{OUT_NAME}", text)
    md = _md(res, "FIXTURE", [f"# {FG.STAMP}: D5 scoring harness, synthetic fixture run", "",
                               f"**{FG.STAMP}.** Invented data (tests/fixtures/d5_synthetic, manifest-hashed). These numbers "
                               "test the harness; they are not D5 results and say nothing about any rung.", "",
                               f"Tool `{TOOL_VERSION}`; harness `{DS.VERSION}`, `{D4.VERSION}`, `{AB.VERSION}`, `{FG.VERSION}`."])
    sha_md = _write(out_dir / f"SYNTHETIC_FIXTURE_{OUT_NAME[:-5]}.md", md)
    return {"json_sha256": sha_json, "md_sha256": sha_md, "out_dir": str(out_dir)}


def run_real(a) -> dict:
    need = ("freeze_record", "benchmark", "runs", "evd", "relatives", "h3_option", "sidedness", "out_dir")
    miss = [k for k in need if not getattr(a, k)]
    if miss:
        raise SystemExit(f"real mode needs --{', --'.join(m.replace('_', '-') for m in miss)} (the lock fixes the H3 option)")
    out_dir = Path(a.out_dir).resolve()
    for bad in (ROOT / FIXTURE_OUT, ROOT / "tests"):
        if out_dir == bad.resolve() or bad.resolve() in out_dir.parents:
            raise SystemExit(f"real outputs may not go to {bad.relative_to(ROOT)} (reserved for synthetic fixtures / tests)")
    inputs = [*a.benchmark, a.evd, a.relatives]
    guard = FG.require_real_inputs(ROOT, a.freeze_record, inputs, committed_check=git_committed)
    rows = DS.load_benchmark(a.benchmark)
    FG.assert_real_rows(rows)
    evd = DS.load_evd(a.evd)
    records = DS.load_runs(a.runs)
    relatives = json.loads(Path(a.relatives).read_text(encoding="utf-8"))
    abl = None
    if a.ablation_runs:
        abl = {}
        for line in Path(a.ablation_runs).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                abl.setdefault(rec["config"], {})[rec["qid"]] = rec
    audit = None
    if a.audit_key and a.audit_sheet_a and a.audit_sheet_b:
        rd = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8-sig")))      # noqa: E731
        scored = DS.score_all(rows, records, evd, relatives)
        audit = DS.audit_report(rd(a.audit_key), rd(a.audit_sheet_a), rd(a.audit_sheet_b),
                                {k: v["all"] for k, v in DS.h3_summaries(rows, scored).items()})
    res = score(rows, records, evd, relatives, ablation_records=abl, audit=audit, d4_error=a.d4_error,
                live_router=a.router_live)
    if a.audit_dir:
        res["audit_sample"]["sheets"] = write_audit_sheets(rows, records, evd, relatives, Path(a.audit_dir))
    key = a.h3_option if a.h3_option == "H3-C" else f"{a.h3_option}|{a.sidedness}"
    res["h3_selected"] = {"option": a.h3_option, "sidedness": a.sidedness, "result": res["h3_verdicts"]["options"][key]}
    runs_sha = FG.sha256_file(a.runs)
    meta = {"tool": TOOL_VERSION, "mode": "REAL", "guard": guard, "runs_sha256": runs_sha, "status": DS.STATUS,
            "metric_registry": DS.METRIC_REGISTRY, "label": "MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers"}
    text = json.dumps({"meta": meta, **res}, indent=1, sort_keys=True) + "\n"
    sha_json = _write(out_dir / OUT_NAME, text)
    md = _md(res, "REAL", ["# D5 scoring (frozen benchmark)", "", f"Freeze {guard['freeze_id']}; files "
                                                                  f"{json.dumps(guard['files_sha256'])}; runs sha256 {runs_sha}.",
                           "Label: MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers."])
    sha_md = _write(out_dir / f"{OUT_NAME[:-5]}.md", md)
    return {"json_sha256": sha_json, "md_sha256": sha_md, "out_dir": str(out_dir)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture", action="store_true", help="score the synthetic fixture only")
    ap.add_argument("--out-dir")
    ap.add_argument("--n-boot", type=int, help="fixture only: fewer bootstrap resamples (tests)")
    ap.add_argument("--freeze-record")
    ap.add_argument("--benchmark", nargs="+")
    ap.add_argument("--runs")
    ap.add_argument("--evd")
    ap.add_argument("--relatives")
    ap.add_argument("--h3-option", choices=DS.H3_OPTIONS)
    ap.add_argument("--sidedness", choices=DS.SIDEDNESS)
    ap.add_argument("--d4-error", choices=D4.ERROR_OPTIONS, default="E1")
    ap.add_argument("--router-live", action="store_true")
    ap.add_argument("--ablation-runs")
    ap.add_argument("--audit-key")
    ap.add_argument("--audit-sheet-a")
    ap.add_argument("--audit-sheet-b")
    ap.add_argument("--audit-dir")
    a = ap.parse_args(argv)
    try:
        if a.fixture:
            real_args = [k for k in ("freeze_record", "benchmark", "runs", "evd", "relatives", "ablation_runs",
                                     "audit_key", "audit_sheet_a", "audit_sheet_b", "audit_dir") if getattr(a, k)]
            if real_args:
                raise SystemExit(f"--fixture takes no input paths (got {real_args}); it reads only {FG.FIXTURE_DIR}")
            info = run_fixture(Path(a.out_dir) if a.out_dir else ROOT / FIXTURE_OUT, a.n_boot)
        else:
            if a.n_boot:
                raise SystemExit("--n-boot is fixture-only; the real run uses the pre-registered resample counts")
            info = run_real(a)
    except FG.GuardRefused as e:
        print(f"REFUSED: {e.problems}", file=sys.stderr)
        return 2
    print(json.dumps(info, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
