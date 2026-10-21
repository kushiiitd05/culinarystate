# V2-DM protocol -- local decision model as REVIEW-span support (written BEFORE any decision model is run on our data)

Status: prospective v2 research, **not part of H6-C**; v1 frozen architecture, thresholds, calibrators, TEST results untouched. v1 TEST (both datasets) is burned and is **never used** here.

## 1. Question
v1 weaknesses: always-REVIEW labels (TASTEset FOOD/PART/PHYSICAL_QUALITY; RecipeDB3 DF/STATE/TEMP), unsafe accepted unseen mentions, weak risk ranking. Can a local decision model, asked bounded questions about each REVIEW span, (a) identify a subset that can be safely accepted, (b) improve error ranking/calibration, without damaging correct predictions and without any external service?

## 2. Models and serving (all local on the A100 lab server)
D2 `tev1:0.8b`, D3 `tev1:4b`, D4 `nimble` (9B). Own Ollama >= 0.35 binary in `~/Kush/ollama-v2`, private port, private model dir, GPU 0; the system Ollama instances are not touched. No `:cloud` model, no ollama.com API. Temperature/determinism and malformed-response rate are measured first (smoke test) and recorded.

## 3. Data (leakage-safe)
| Use | Source | Rule |
|---|---|---|
| prompt design + calibrator/combiner fitting | 5-fold OOF **TRAIN** spans of the frozen DeBERTa-base+CRF (TASTEset 8,225; RecipeDB3 65,716), cross-fitted calibrated scores | gold labels used only to score; decision model never fine-tuned |
| model/gating selection | v1 **DEV** spans not accepted by frozen R6 | DEV was used for v1 selection, so it is a development set here, not a test |
| thresholds | v1 **CALIBRATION** spans (frozen R6 routes) | thresholds only |
| final claim | **fresh data only** (external/API sample or future annotation) | until it exists, V2-DM results are labelled DEV-level evidence |
REVIEW set = spans the frozen R6 routes to REVIEW or REJECT (OOF rows: stratum thresholds applied to cross-fitted scores; approximate membership, documented). Protected recipe text stays on the lab server / local disk; nothing is committed.

## 4. Bounded questions (no free-form output)
Input = the sentence with the proposed span marked `[[ ]]` and the proposed label.
- Q1 (noul): is the span boundary exactly right? Q2 (choice): best label among the dataset's labels + OTHER. Q3 (noul, primary): is the proposed span *and* label exactly correct? Q3 is the decision used for routing; Q1/Q2 are diagnostics. Instructions/criteria text is written and **frozen on OOF TRAIN rows before DEV is scored**, at most 3 pre-listed wording variants, no further edits.
- Linker verification (Q4, choice among top-K candidates + NONE) and NOVEL/unseen (KNOWN / POSSIBLE_NEW_ALIAS / UNKNOWN / INSUFFICIENT_EVIDENCE) are **gated**: run only if the REVIEW stage is GO.

## 5. Arms
D0 frozen R6 only | D1 simple confidence rule (calibrated v1 probability within REVIEW, threshold at eps) | D2/D3/D4 decision model p(Q3) used (i) alone and (ii) as an extra feature in the cross-fitted calibrator [logit conf, M6, logit p_dm] | D5 earlier MiniMax verifier result (reference only, no new run). Marketing numbers are never used for comparison.

## 6. Metrics (frozen)
Per arm on DEV REVIEW spans: decision accuracy, balanced accuracy, precision/recall per decision, NLL, Brier, ECE (raw vs temperature/logistic vs isotonic where n permits), AUROC, tie-aware AURC and selective risk, error capture, REVIEW reduction at fixed ACCEPT error <= 2% (thresholds from CALIBRATION), **fixed errors vs damaged correct predictions** (an arm that damages more correct spans than it fixes errors is REJECTED; "incorrect auto-acceptance" reported separately), latency, GPU/RAM. Paired bootstrap over documents (2,000), Holm over the primary family {REVIEW-reduction gain, AURC, NLL} per model.

## 7. Promotion gate (any one, with the others not worse)
(1) significantly higher error capture at equal or better safe coverage; (2) REVIEW workload reduction at ACCEPT error <= 2% (CI); (3) better unseen/novel discrimination; (4) better linker adjudication -- while computationally reasonable (latency/memory table). Otherwise **REJECT the lane**. Training our own `CulinaryDecision` model is a separate proposal, allowed only after a GO, with fresh train/dev/test, no reuse of v1 TEST labels, and a licence/provenance record.

## 8. Order
smoke test (Choice, Noul; repeatability, malformed rate, latency, memory) -> freeze prompts on OOF TRAIN -> build REVIEW dataset -> D0-D4 on DEV -> calibration check -> GO/NO-GO -> only then NOVEL/unseen -> only then linker verification.
