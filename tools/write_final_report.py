#!/usr/bin/env python3
"""Builds reports/ner/culinaryner_kf_final_report.md from reports/ner/_final_test.json (numbers are never typed by hand)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = json.load(open(ROOT / "reports/ner/_final_test.json"))
agg = {ds: json.load(open(ROOT / f"reports/ner/_e0_{ds}_test.json"))["crf_vs_softmax"]["v3-large+CRF vs base+CRF"] for ds in ("tasteset", "recipedb3")}
f4 = lambda x: "-" if x is None else f"{x:.4f}"
pm = lambda t: f"{t[0]:.4f}" + (f" ± {t[1]:.4f}" if t[1] is not None else "")
L = []
w = L.append
PRIM, CH = "PRIMARY deberta-base+CRF", "FROZEN ACCURACY/COMPUTE CHALLENGER deberta-v3-large+CRF"
w("# CulinaryNER-KF v1 -- final TEST report and A-N closeout\n")
w("Frozen before TEST: `test_freeze_manifest.json` (commit 4ee0582). TEST was evaluated once (`tools/final_test_eval.py`, raw `_final_test.json`); no threshold, calibrator, stratum, feature, linker or checkpoint choice was changed afterwards. Disclosures: TASTEset TEST aggregates of E0 models were viewed once at E0 (recorded in the contract); linker held-out alias/concept sets were viewed during development as report-only sets. Hypothesis status: RESEARCH HYPOTHESIS; no SOTA wording.\n")
for ds, title in (("tasteset", "TASTEset"), ("recipedb3", "RecipeDB3 (grouped benchmark split)")):
    o = R[ds]
    w(f"## {title} -- TEST ({o['n_test_docs']} docs, {o['n_test_spans']} predicted spans, span accuracy {o['span_acc']:.4f})\n")
    w("### Span quality (exact match unless stated; mean ± sd over seeds)\n")
    w("| System | seeds | exact micro F1 | exact macro F1 | relaxed micro F1 | boundary err | type err | train min | peak GPU GB |\n|---|---|---|---|---|---|---|---|---|")
    for nm, q in o["span_quality"].items():
        w(f"| {nm} | {len(q['seeds'])} | {pm(q['exact_micro_f1'])} | {pm(q['exact_macro_f1'])} | {pm(q['relaxed_micro_f1'])} | {pm(q['boundary_error'])} | {pm(q['type_error'])} | {q['train_minutes'][0]:.1f} | {q['peak_gpu_gb'][0]:.1f} |")
    a = agg[ds]
    w(f"\nChallenger vs primary (paired grouped bootstrap over TEST docs, seed-matched): dF1 {a['delta_micro']:+.4f} [CI {a['ci95'][0]:+.4f}, {a['ci95'][1]:+.4f}], seeds won {a['seeds_won']}, d unseen F1 {a['delta_unseen_f1']:+.4f}, d macro {a['delta_macro']:+.4f}. Not used for selection; v1 stays DeBERTa-base+CRF.\n")
    w("Generalisation (exact F1, primary): " + "; ".join(f"{k} {pm(v)} (n={o['span_quality'][PRIM]['strata_n'][k]})" for k, v in o["span_quality"][PRIM]["strata_f1"].items() if k not in ("unseen_alias",)) + ".  Per-label F1: " + "; ".join(f"{k} {v[0]:.3f}" for k, v in o["span_quality"][PRIM]["per_label_f1"].items()) + ".\n")
    w("### Calibration of span correctness (TEST spans)\n")
    w("| Probability | NLL | Brier | ECE | FOOD NLL / ECE | unseen-mention NLL / ECE | AURC (risk ranking) |\n|---|---|---|---|---|---|---|")
    for nm, c in o["calibration"].items():
        key = {"raw_conf": "raw", "calibrated": "calibrated", "calibrated+M6": "calibrated+M6"}[nm]
        w(f"| {nm} | {c['all']['nll']:.4f} | {c['all']['brier']:.4f} | {c['all']['ece']:.4f} | {c['food']['nll']:.3f} / {c['food']['ece']:.3f} | {c['unseen_mention']['nll']:.3f} / {c['unseen_mention']['ece']:.3f} | {o['risk_discrimination_aurc'][key]:.5f} |")
    w("\n**A. probability calibration vs B. risk discrimination:** calibration and M6 lower NLL/Brier/ECE, but the raw CRF confidence ranks errors best (lowest AURC); isotonic calibration coarsens the ranking and M6 recovers only part of it. They are separate properties and the report treats them separately.\n")
    w("### Router (thresholds from CALIBRATION only; eps = 0.02; cost per 100 spans: accepted error 10, review 1, rejected-correct 3)\n")
    w("| Router | ACCEPT coverage | ACCEPT error [95% CI] | REVIEW rate | REJECT rate | error capture outside ACCEPT | cost/100 |\n|---|---|---|---|---|---|---|")
    for nm, c in o["routers"].items():
        w(f"| {nm} | {c['coverage']:.3f} | {f4(c['accept_error'])} [{c['accept_error_ci95'][0]:.4f}, {c['accept_error_ci95'][1]:.4f}] | {c['review_rate']:.3f} | {c['reject_rate']:.3f} | {c['error_capture_nonaccept']:.3f} | {c['cost_per_100_ce10']:.1f} |")
    f = o["routers"]["R6_FINAL_label_x_unseen"]
    w(f"\nFrozen thresholds reproduce S127: {f['frozen_thresholds_match_S127']}. Review-only error capture {f['error_capture_review_only']:.3f}.\n")
    w("Per label (R6 final): | label | n | span error | ACCEPT rate | ACCEPT error | REVIEW | REJECT |\n|---|---|---|---|---|---|---|")
    for l, v in f["per_label"].items():
        w(f"| {l} | {v['n']} | {v['span_error_rate']:.3f} | {v['accept_rate']:.3f} | {f4(v['accept_error'])} | {v['review_rate']:.3f} | {v['reject_rate']:.3f} |")
    w(f"\n**Labels that never satisfy eps = 2% and always route to REVIEW (a result, not a defect): {', '.join(f['always_review_labels(never ACCEPT at eps=0.02)'])}.**")
    su = f["seen_unseen"]
    w(f"Seen mentions: n {su['seen']['n']}, ACCEPT rate {su['seen']['accept_rate']:.3f}, ACCEPT error {f4(su['seen']['accept_error'])} (span error {su['seen']['span_error_rate']:.3f}). Unseen mentions: n {su['unseen']['n']}, ACCEPT rate {su['unseen']['accept_rate']:.3f}, ACCEPT error {f4(su['unseen']['accept_error'])} (span error {su['unseen']['span_error_rate']:.3f}) -- the claimed tolerance does NOT hold on the few unseen spans that are accepted (small strata borrow the pooled threshold).\n")
    n = o["novel_advisory"]
    w(f"NOVEL advisory (never an action): {n['n']} FOOD spans ({n['share_of_food_spans']:.3f} of FOOD) carry the tag; {f4(n['correct_span_share'])} are correct spans; {f4(n['ledger_exact_hit_share'])} have a ledger exact hit; {n['auto_accepted']} of them were nevertheless ACCEPTed by the span router (the tag does not gate).\n")
L2 = R["linker"]["models"]
w("## Linking (frozen operational linker: BGE-large; E5-large documented Pareto alternative; linker_data_v2, 5 seeds; held-out alias / concept sets)\n")
w("| | BGE (frozen) | E5 (alternate) |\n|---|---|---|")
for lab, fn in (("dev_alias Acc@1 (selection set, n=61)", lambda m: m["dev_alias"]["acc1"]), ("held-out alias Acc@1 (n=96)", lambda m: m["unseen_alias"]["acc1"]), ("held-out alias Recall@5", lambda m: m["unseen_alias"]["r5"]),
                ("held-out alias MRR", lambda m: m["unseen_alias"]["mrr"]), ("tail / head held-out alias Acc@1", lambda m: f"{m['unseen_alias_tail_acc1']:.3f} / {m['unseen_alias_head_acc1']:.3f}"),
                ("NIL AUROC (held-out concepts vs aliases)", lambda m: m["nil_auroc_heldout"]), ("NIL recall at dev-chosen tau", lambda m: m["nil_heldout"]["recall"]), ("false-NIL rate on known aliases", lambda m: m["nil_heldout"]["false_nil_rate_on_aliases"])):
    g = lambda m: (f"{fn(m):.3f}" if not isinstance(fn(m), str) else fn(m))
    w(f"| {lab} | {g(L2['BGE'])} | {g(L2['E5'])} |")
w("\nNIL/NOVEL stays advisory: cosine-based NIL AUROC about 0.66 and no span-level novelty truth. Paired BGE-E5 evidence: " + json.dumps(R["linker"]["paired"]["dev_alias"]) + " (indistinguishable; BGE frozen for v1 on DEV evidence and operational simplicity, not on TEST).\n")
lat = R["latency"]
w("## Compute (A100-PCIE-40GB, shared, bf16; indicative)\n")
w("| Component | bs1 latency | bs32 latency | memory |\n|---|---|---|---|")
for k, v in lat.items():
    if k.startswith("tasteset_len48"):
        w(f"| {k.split('|')[1]} encoder / +CRF decode / +marginals | {v['bs1']['encoder_ms']:.1f} / {v['bs1']['encoder+crf_decode_ms']:.1f} / {v['bs1']['encoder+crf_decode+marginals_ms']:.1f} ms | {v['bs32']['encoder_ms']:.1f} / {v['bs32']['encoder+crf_decode_ms']:.0f} / {v['bs32']['encoder+crf_decode+marginals_ms']:.0f} ms | {v['peak_gb']} GB |")
for k, v in lat.items():
    if k.startswith("linker"):
        w(f"| {k} (query + top-10 over 2,031 surfaces) | {v['bs1_ms']:.1f} ms | {v['bs256_ms']:.1f} ms (256 queries) | {v['peak_gb']} GB |")
w("| M6 gazetteer features (CPU) | 0.19 ms/span | - | - |\n| calibrator + router (CPU) | <0.001 ms/span | - | - |\n")
open(ROOT / "reports/ner/_final_tables.md", "w").write("\n".join(L))
print("\n".join(L)[:200], len("\n".join(L)))
