# External-domain validation protocol for CulinaryNER-KF v1 (EXT-v1)

Status: **PROTOCOL, written before any external data is downloaded, converted or scored.** Frozen at the commit that adds this file; later changes are dated amendments (`external_validation_amendments.md`), never silent edits.
Immutable background: `culinaryner_kf_final_report.md` (S128 closeout, tag `ner-v1-closeout`) and `test_freeze_manifest.json`. Nothing in v1 is tuned on external data before the first frozen evaluation.

## 1. Question and hypotheses
v1 = `DeBERTa-base+CRF -> calibrated span confidence + M6 -> label x seen/unseen risk router -> BGE candidate linker + advisory NOVEL`. The only scientific gap left is whether its behaviour survives a change of source. Pre-registered hypotheses (numbers in section 9):

| ID | Question |
|---|---|
| H1 | span F1 under domain shift (per source, core labels) |
| H2 | calibration transfer (ECE / NLL of calibrated+M6 vs raw confidence) |
| H3 | the eps = 2% ACCEPT policy transfers **without retuning** (ACCEPT error, coverage) |
| H4 | seen vs unseen mention performance, incl. whether "accepted unseen mentions are unsafe" replicates |
| H5 | REVIEW/REJECT error capture |
| H6 | per-label risk control (which labels meet eps, which are always-REVIEW) |
| H7 | linker robustness (candidate recall on ledger-present mentions, NIL separation, score shift) |
| H8 | summary: does the risk policy transfer as a whole? |

## 2. Candidate datasets and eligibility (gate: nothing is used until its row says VERIFIED)
| ID | Candidate | What it offers | Known facts | Eligibility status / gate |
|---|---|---|---|---|
| EXT-A | `ingredient-parser` labelled ingredient-phrase corpus (strangetom), per-row `source` field: nyt (30k labelled), bbc (15k), cookstr (15k), allrecipes (15k), tc (6.3k); built from the NYT ingredient-phrase-tagger snapshot and the archive.org `recipes-en-201706` dump | **source-labelled**, so true source-disjoint testing is possible; different publishers, units (BBC metric), sentence styles (Cookstr multi-ingredient lines) | the page states no data licences; NYT repo archived 2019, code Apache-2.0, data licence unstated; labels are token-level manual with acknowledged consistency issues | **UNVERIFIED.** Gate G1: record original URLs, retrieval date, file hashes, and written terms of each source; if terms forbid research use, drop that source. Use = local research only, no redistribution, no phrase text committed (same regime as BBC/Food.com/RecipeDB3) |
| EXT-B | FoodBase (Popovski et al. 2019): 1,000 Allrecipes recipes, 12,844 gold food-entity annotations, full recipe text incl. instructions | FOOD entities in running text (text-type shift) | Allrecipes is also a TASTEset/RecipeDB source, so it is **near-domain** for source but far for text type; licence/download not confirmed | **UNVERIFIED** (gate G1). Reserved as the *second* external set (confirmation set; not opened before EXT-A is analysed) |
| EXT-C | Independent annotation of non-benchmark recipe text (local BBC scrape and/or other local corpora) by Kush + Parv, double annotated, schema identical to our benchmark views incl. PROCESS | exact schema match, can include PROCESS and canonical-ID linker labels | BBC mentions fed the ledger that trained the linker, so BBC text is **not independent for linker/ledger components** | Feasible without third-party licences; cost = annotation time. Used for the linker sub-study (section 10) and annotation-noise audit (section 11) |
Out of scope: Food.com (S116 eligibility screen pending, licence "CC0 declared, uploader authority unverified"), Gold event data, any dataset requiring new model development.
Contamination rules: (i) BBC source rows are excluded from every ledger/linker-dependent metric (H7); (ii) any external phrase whose normalised form or masked-sentence family appears in TASTEset/RecipeDB3 train/dev/calibration/test is removed (reported count); (iii) near-duplicates within the external set are collapsed to one cluster (also the bootstrap unit).

## 3. System under test (frozen; nothing refit on external data in the primary analysis)
Two dataset-specific v1 pipelines, evaluated as trained: **P-R** (trained on RecipeDB3: ingredient-phrase domain; core + STATE) and **P-T** (trained on TASTEset: FOOD/QUANTITY/UNIT/PROCESS). Calibrators, M6 gazetteers, thresholds and strata are the frozen S128 objects (hashes in `test_freeze_manifest.json`).
**Checkpoint gate (required, because v1 saved predictions but no weights):** retrain DeBERTa-base+CRF seed 1 with the manifest hyper-parameters, save the weights, hash them, then regenerate dev/calibration/test predictions with the saved model. Proceed only if exact micro-F1 on in-domain TEST reproduces S128 within 0.002 and the frozen R6 router reproduces S128 ACCEPT error/coverage within the S128 bootstrap CIs. If not, refit calibrator and thresholds from the saved model's OOF/CALIBRATION outputs only (never external data), document it as an amendment, and re-hash before external data is touched. No other change is allowed.

## 4. Label mapping (common "unified core" = FOOD/NAME, QUANTITY, UNIT; secondary STATE for P-R)
| EXT-A tag | maps to | note |
|---|---|---|
| B_NAME_TOK, I_NAME_TOK, NAME_VAR, NAME_MOD | NAME / FOOD (contiguous run = one span; NAME_SEP breaks spans) | NAME_VAR/NAME_MOD are treated as name tokens; sensitivity run without them is a secondary analysis |
| QTY | QUANTITY | |
| UNIT | UNIT | |
| PREP | STATE (P-R only) | approximate; reported as secondary, not in the primary family |
| SIZE, PURPOSE, COMMENT, PUNC, OTHER | O (not scored) | SIZE excluded as in the published RecipeDB3 view |
| TEMP, DF (P-R), PROCESS (P-T) | not available | not evaluated on EXT-A; PROCESS only via EXT-C/EXT-B-instructions if annotated |
Conversion rules: token labels -> character spans by whitespace tokenisation of the stored sentence; 100% token round-trip is required (failures listed and excluded, count reported); sentences with any OTHER tag excluded (as in the source project). The converter and its hash are frozen before scoring. Predicted spans of unscored labels (e.g. P-R TEMP/DF) are dropped before scoring and reported as a count.

## 5. Splits inside the external set (set by hash, before any scoring)
EXT-CAL = 10% of clusters (used only for the *secondary* recalibration analysis, section 12); EXT-TEST = 90% (all primary results). Assignment = SHA-256 of the cluster id mod 10; no model sees EXT-TEST labels at any point.

## 6. Sample-size targets (achieved sizes must be reported; shortfalls downgrade the affected claim to descriptive)
Binomial arithmetic at the policy target (true error 2%): n_accept = 750 -> SE 0.51 pp, one-sided 95% upper bound about 2.8%; n = 300 -> about 3.3%; n = 150 -> about 3.9%.
| Quantity | Target |
|---|---|
| Unique clusters after hygiene | >= 20,000 (>= 5,000 in each of >= 3 shifted sources: nyt, cookstr, bbc; allrecipes as near-domain control) |
| Core spans (NAME + QUANTITY + UNIT) in EXT-TEST | >= 60,000 |
| **Unseen NAME mentions** (normalised surface absent from the pipeline's train gazetteer) | >= 3,000 overall, >= 1,000 in each of >= 2 shifted sources |
| ACCEPTed spans, pooled / per source | >= 750 / >= 300 |
| ACCEPTed spans per label for a per-label verdict | >= 300 (else descriptive) |
| ACCEPTed unseen spans for a pass/fail verdict on H4 | >= 150 (else descriptive with exact CI) |
Because only about 2-11% of unseen spans were ACCEPTed in v1, the unseen target cannot be met by random sampling alone: unseen NAME mentions are **over-sampled by input text only** (selection looks at surfaces and train gazetteers, never at gold labels or model scores), and every reported rate is reweighted/stratified accordingly.

## 7. Frozen metrics (computed with the existing frozen code paths; new code limited to conversion + reporting)
Span quality (exact and relaxed micro/macro F1, per label, boundary error, type error; seen vs unseen mention F1; head vs tail by train frequency); calibration (NLL, Brier, ECE for raw, calibrated, calibrated+M6; overall, NAME-only, unseen-mention, seen-mention); risk discrimination (tie-aware AURC on the continuous score, kept distinct from calibration); router (R1, R2, R3, R3s, R6: ACCEPT coverage, ACCEPT error with Clopper-Pearson interval, REVIEW/REJECT rates, error capture, per-label and seen/unseen tables, always-REVIEW labels, cost per 100 spans with the v1 cost model); domain-shift descriptors (unseen-mention rate, gazetteer coverage, length, unit-system mix, KS distance of confidence scores vs in-domain); linker (section 10); compute (unchanged from v1). NOVEL remains advisory; no NOVEL accuracy claim is made.

## 8. Statistical procedures
Exact Clopper-Pearson intervals for every error rate; paired cluster bootstrap (2,000 resamples, clusters as defined in section 2) for differences in F1, NLL, ECE, AURC and capture; Holm correction over the **primary family {H1, H2, H3, H5}** (per shifted source, so 3 sources x 4 = 12 tests); H4, H6, H7 are reported with intervals and the pre-declared thresholds below but are not pooled into the primary family. One look at EXT-TEST only. Seeds: the frozen seed-1 pipeline; seed variance is not re-estimated (stated limitation).

## 9. Success / failure criteria (fixed now)
| ID | PASS | FAIL | otherwise |
|---|---|---|---|
| H1 | exact micro-F1 (core labels) >= in-domain TEST core F1 - 0.05 | < in-domain - 0.10 | DEGRADED |
| H2 | ECE(calibrated+M6) <= 0.05 **and** NLL(calibrated+M6) < NLL(raw) with CI excluding 0 | ECE > 0.10 or calibrated NLL worse than raw | PARTIAL |
| H3 (pooled and per shifted source) | one-sided 95% upper bound of ACCEPT error <= 3.0%, point <= 2.5%, coverage >= 0.40 | one-sided 95% lower bound > 2.0% (tolerance significantly exceeded) | INCONCLUSIVE |
| H4 | n/a (descriptive finding): "unsafe accepted unseen mentions" **replicates** if ACCEPT error lower bound > 2% with >= 150 accepted unseen spans | - | reported with exact CI |
| H5 | error capture outside ACCEPT >= 0.60 | < 0.50 | PARTIAL |
| H6 | every label with >= 300 ACCEPTs meets the H3 PASS rule | any such label meets the H3 FAIL rule | PARTIAL |
| H7 | candidate Acc@1 >= 0.60 on ledger-present EXT-C mentions (v1 held-out 0.70, allowance 0.10) | < 0.50 | PARTIAL; NIL AUROC and KS shift are descriptive |
**H8 verdict:** *RISK POLICY TRANSFERS* if H1 is not FAIL on any source, H2 PASS, and H3 PASS on >= 2 of the 3 shifted sources with none FAIL; *PARTIAL TRANSFER* if H3 PASS on seen mentions but not pooled, or any source INCONCLUSIVE; *DOES NOT TRANSFER* if H3 FAIL on >= 2 shifted sources. A failure is a result, reported as such, and does not by itself trigger new model development.

## 10. Linker sub-study (EXT-C, Kush + Parv)
400 external FOOD mentions (200 whose surface is unseen by the ledger and 200 seen), no BBC-derived text, independently labelled with a ledger concept ID or NIL, adjudicated; report Acc@1, Recall@5, MRR on ledger-present mentions (BGE frozen; E5 reported as the documented alternative, no selection), NIL AUROC, false-NIL rate at the frozen dev tau, and top-1 cosine shift vs in-domain. n = 400 gives about +/-5 pp on Acc@1.

## 11. Annotation-noise ceiling
300 random EXT-A phrases independently re-labelled by two humans; the observed agreement F1 is reported as the noise ceiling, and H1 is also reported relative to that ceiling (descriptive).

## 12. What can and cannot change after evaluation
**Cannot:** any v1 component, threshold, calibrator, stratum, feature, linker choice, checkpoint, label mapping, success criterion, or the choice of sources after seeing results; EXT-TEST is burned after one evaluation.
**Can (clearly labelled post-hoc/secondary, never replacing the primary result):** error analysis; sensitivity to the mapping choices in section 4; a *recalibration* analysis that refits calibrator and thresholds on EXT-CAL only and re-evaluates on EXT-TEST (answers "would a small in-domain calibration set restore eps = 2%?"); per-source breakdowns; additional amendments dated before any new data are scored.
**Any v2 system** needs a new protocol and a fresh external test set (EXT-B and/or EXT-C are reserved for that and are not examined during EXT-A analysis).

## 13. Sequence and gates
1. G1 licence/provenance verification (EXT-A sources, EXT-B); record hashes. 2. Reference values: in-domain TEST core-label F1 and S128 router numbers extracted from frozen artifacts and hashed (`external_reference_values.json`). 3. Converter + hygiene + split, hashes frozen; sizes reported against section 6 *without* scoring. 4. Checkpoint gate (section 3). 5. Single scoring run on EXT-TEST. 6. Primary report, then secondary analyses, then EXT-C sub-studies. Compute: one server run for checkpoint retraining/inference (about 40 min on a shared A100) plus laptop analysis; SSH only after explicit VPN confirmation.

## 14. Pre-registered risks
Label-schema mismatch (PREP vs STATE; NAME_VAR); source annotation inconsistency (noise ceiling, section 11); same-site overlap for Allrecipes (near-domain control, not counted as shift); ingredient-phrase text has no PROCESS, so the P-T pipeline is evaluated on FOOD/QUANTITY/UNIT only; seed-1 pipeline only; unseen strata may stay below the target n (then descriptive).
