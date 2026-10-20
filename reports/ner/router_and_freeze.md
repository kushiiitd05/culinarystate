# Evidence-closing steps, router, and architecture freeze (S127) -- DEV only; TEST untouched

## 1-2. Linker v2 (true held-out NIL) and BGE vs E5
`tools/build_linker_data.py v2` (script `tools/linker_v2_eval.py`, raw `_linker_v2_eval.json`). Training queries and train gallery are identical to v1; only the evaluation gallery changes to TRAIN concepts only. Validation: dev NIL (252 queries, 181 concepts) and unseen_concept NIL (543, 415 concepts) have 0 exact-surface and 0 concept overlap with the gallery (v1 dev NIL: 252/252 were gallery members); dev/test NIL concept sets disjoint; dev_alias / unseen_alias gold concepts all in the gallery with their own surface held out.
| (5 seeds) | BGE | E5 |
|---|---|---|
| dev_alias Acc@1 (n=61, selection) | 0.708 (sd .012) | 0.682 (sd .022) |
| dev_alias R@5 / MRR | 0.849 / 0.762 | 0.836 / 0.744 |
| unseen_alias Acc@1 (report only) | 0.704 | 0.663 |
| NIL AUROC dev / held-out (top-1 cosine) | 0.720 / 0.665 | 0.725 / 0.660 |
| held-out confidence (dev-fit logistic): ECE / NLL / AUROC | 0.034 / 0.307 / 0.747 | 0.035 / 0.292 / 0.753 |
Paired dev_alias Acc@1 BGE-E5 +0.026 [-0.030,+0.082]; held-out confidence NLL diff -0.002 [-0.013,+0.009]. **Indistinguishable -> BGE and E5 stay a Pareto set (BGE provisional).** NIL via cosine is weak: at the dev-optimal tau, 48% (E5) / 57% (BGE) of known aliases are wrongly flagged NIL for 72% / 80% NIL recall. This corrects the earlier NIL figures (which used the invalid v1 dev set).

## 3. Calibration-method robustness (`tools/calibrator_robustness.py`, 7 pre-listed methods, DEV)
NLL (TASTEset / RecipeDB3): temperature only 0.398 / 0.365 (fails: CRF marginals saturate); Platt 0.1547 / 0.1196; isotonic 0.1533 / 0.1105; Platt+M6 0.1493 / 0.1145; Platt+label 0.1566 / 0.1152; **Platt+isotonic+M6 0.1450 / 0.1092 (best on both)**; Platt+label+M6 0.1518 / 0.1116. Simpler methods are significantly worse on at least one dataset (Platt+M6: RecipeDB3 +0.0053 [+0.003,+0.008]; isotonic: TASTEset +0.0083 [+0.002,+0.017]). **Chosen: logistic + isotonic on [logit conf, M6 exact, M6 fuzzy]** (the simplest supported). Class-conditional probabilities (Platt+label+M6) gain AURC on RecipeDB3 (0.0083 vs 0.0120) but lose NLL on TASTEset (+0.0069 [+0.0008,+0.0132]); class conditioning is therefore left to the router strata.

## 4. Where M6 helps (`tools/m6_analysis.py`; analysis only)
M6 is effectively an **unseen-mention detector**. TASTEset: unseen-mention spans (n=0 in the train gazetteer; 12% of spans, 29.5% error) dNLL -0.091 [-0.148,-0.043], ECE -0.049; boundary-error spans dNLL -0.30. It slightly hurts seen/tail spans (tail +0.017 [+0.002,+0.033]; head +0.001). RecipeDB3: unseen error is only 12% and the gain vanishes (unseen dNLL -0.0001; spurious spans worse, +0.19; NAME +0.0072). The benefit therefore exists in the high-novelty regime (TASTEset) and is neutral where P0 is already well calibrated.

## 5-6. Router (thresholds on CALIBRATION only; eps = 0.02 finite-sample risk control; evaluated on DEV; cost per 100 spans with accepted error 10, review/novel 1, rejected-correct 3)
| Router | TASTEset cov / ACCEPT err [CI] / error-capture / cost | RecipeDB3 cov / ACCEPT err [CI] / error-capture / cost |
|---|---|---|
| R1 raw span threshold | .863 / .0135 [.008,.020] / .81 / 25.4 | .939 / .0153 [.013,.018] / .59 / 20.5 |
| R2 calibrated span | .865 / .0140 / .81 / 25.6 | .942 / .0162 / .56 / 21.0 |
| R3 calibrated + M6 | .885 / .0169 [.011,.024] / .76 / 26.5 | .936 / .0174 [.014,.021] / .53 / 22.7 |
| R3s + label strata | .592 / .0213 [.012,.035] / .80 / 53.4 | .509 / .0107 [.008,.014] / .84 / 54.6 |
| R3s + label x unseen strata | .596 / .0146 [.008,.024] / .86 / 49.2 | .722 / .0127 [.010,.016] / .74 / 37.0 |
| R4 + linker/NIL gate (balanced tau_l) | identical (gate never fires) | .628 / .0108 / .81 / 44.0 (NOVEL 2.6%) |
| R5 R4 + REJECT (P<1/3) | REJECT 1.2% (83% wrong) | REJECT 0.2% (90% wrong) |
| **R6 FINAL: label x unseen strata + REJECT, linker advisory only** | **.596 / .0146 [.008,.024] / .86 / 48.6** | **.722 / .0127 [.010,.016] / .74 / 36.8** |
Findings: (a) global thresholds look best on cost but hide per-label risk: global-R3 accepted FOOD spans have 3.5% error (TASTEset) and NAME 3.0% (RecipeDB3), STATE 2.8%; stratified routers control ACCEPT error per stratum. (b) With label x unseen strata ACCEPT error is within eps on both datasets and error capture in non-ACCEPT is 86% / 74%. (c) FOOD (TASTEset) and STATE/DF (RecipeDB3) are never auto-ACCEPTed at eps = 2%: span confidence cannot isolate error-free subsets; they go to REVIEW. (d) The linker/NIL gate costs coverage (RecipeDB3 .722 -> .628) for a 0.0019 ACCEPT-error reduction (CIs overlap) and is inert on TASTEset: **the linker does not earn an ACCEPT gate; it remains candidate generator + advisory NOVEL tag** (FOOD spans above the reject bar with no ledger candidate: TASTEset 33 spans, 73% correct spans, 12% have a ledger exact hit; RecipeDB3 526 spans, 92% correct, 6% ledger hit; none auto-accepted). Automatic NOVEL actions are INCONCLUSIVE: no span-level truth for novelty exists and NIL AUROC is 0.66. (e) Several small strata borrow the pooled threshold, so their control is pooled, not per-stratum. Risk-coverage AURC (continuous scores, DEV): TASTEset raw .0109 / calibrated .0105 / +M6 .0103; RecipeDB3 .0092 / .0150 / .0120 (isotonic calibration lowers ranking resolution on RecipeDB3: score for ranking = raw/class-conditional, calibrated probability for thresholds).

## 7. Latency / compute (A100-PCIE-40GB shared; bf16; indicative) and Mac-side
| Component | Latency | Memory / train cost |
|---|---|---|
| DeBERTa-base encoder, bs1 / bs32 | 19.5 ms / 19.3 ms (len 48) | 0.9 GB inference; train 2.4 min, 3.6 GB (TASTEset E0) |
| + CRF Viterbi decode | 21.0 ms bs1; 129 ms bs32 (python decode loop) | - |
| + CRF span marginals (confidence) | 50.9 ms bs1; 493 ms bs32 (unbatched per-document forward-backward: the dominant cost) | - |
| DeBERTa-v3-large (challenger) | 33.5 ms bs1 (+CRF 36.7; +marginals 80.6) | 2.6 GB inference; train 3.7 min, 10.5 GB |
| BGE-large / E5-large linker, 1 query / 256 queries + 2,031-surface gallery top-10 | 16.4 / 15.6 ms ; 15.7 / 15.7 ms | 2.1 GB; train 0.15 min per 4 epochs |
| Gazetteer features (M6), CPU | 0.19 ms per span (fuzzy trigram, unmemoised) | - |
| Calibrator (logreg + isotonic) | 0.0004 ms per span | - |
| Router | `_router_*.json` router_ms_per_1000_spans | - |
RecipeDB3 len-24 numbers are in `_latency_bench.json`. Marginals cost is a candidate for batching if throughput matters; not pursued.

## Router freeze (CALIBRATION thresholds; no TEST)
**FROZEN ARCHITECTURE v1 (candidate for the single TEST run):** DeBERTa-base+CRF (per-dataset; seed policy: seed 1, 5-fold OOF for calibrator fit) -> span marginal confidence -> logistic+isotonic calibrator on [logit conf, M6 exact, M6 fuzzy] fit on OOF train spans -> router R6: eps = 0.02, label x seen/unseen (train-gazetteer count 0) strata thresholds from CALIBRATION via finite-sample risk control (pooled borrow when stratum < 30), REJECT when P(correct) < 1/3, otherwise REVIEW; ACCEPT only above the stratum threshold; linker (BGE provisional, E5 alternate) supplies candidates and an advisory NOVEL tag, never an ACCEPT gate. Challenger kept un-run: DeBERTa-v3-large+CRF. Threshold files: `reports/ner/_router_tasteset.json`, `_router_recipedb3.json` (sha256 prefix ddb54a37d99000fa / e8b5ec2c175ff153). Final ACCEPT-error and coverage on DEV: see R6 row.
Known limitations carried into the A-N report: no span-level truth for link/novelty; RecipeDB3 has no source field (no source-disjoint test); metadata M6 gain is regime-conditional; F1 ties are broken by class strata only.
