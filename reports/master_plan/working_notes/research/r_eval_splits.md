# r_eval_splits — Evaluation, splits, leakage, statistics, human effort (spine steps 15, 19, 27, 29–36; master-output Parts P/Q/R)

Researcher: r_eval_splits · 2026-10-22 · PLAN-RESEARCH ONLY (no implementation, repo read-only).
The 36-step plan with its step cards is missing (ctx.md). Every "step content" statement below is reconstructed from the SSOT, the Master Plan v4.0 and repo artifacts, and cites them. No card text is quoted, because none exists here.

---

## 0. Internal facts this research rests on (verified read-only on this machine)

| Fact | Evidence |
|---|---|
| Active EVD = 17,978 rows: USDA-RETN-R6 7,018, BOGNAR-2002 7,090, PHENOL-EXPLORER-3.6 3,870 | stdlib count over `ledgers/data/EVD.jsonl` (latest version, status ACTIVE); matches `reports/es1/es1_1_audit.md` L6 |
| `study_id_status`: USDA and Bognár rows are all `NOT_IDENTIFIABLE`. Only Phenol-Explorer rows have study IDs | EVD fields `study_id_status`, `independence_group` |
| There are **127 independence groups** in total: USDA = 1, Bognár = 1, Phenol-Explorer = **125 publications**. PE rows per publication: median 13, max 251 (6.5% of PE) | stdlib count |
| Distinct (raw matrix × raw process) cells: USDA 270, PE 287, Bognár 540. The transition contract counts "independent units" as USDA 171, Bognár retention 123, PE 287, Bognár yield 417 | `reports/h_state/transition_bootstrap_v0_contract.md` L10 |
| Cross-source overlap: USDA↔Bognár L1 has 67 cells / 4 ingredients / 1 step. L2 has 249 cells. PE has **0** target overlap with either | `reports/del2/cross_source_v1.md` |
| DEL-2 PE baselines already show a negative cold-split result. With pair-holdout, D1 global mean (0.726) ≥ D5 GBM (0.790). With study-disjoint, D0 persistence (0.558) beats D5 (0.755), but the grouped CIs overlap heavily. **D7_biased_mf_side_info reproduces D1 to 4 decimals on every split**, so D7 is likely degenerate and collapsing to the global mean | `reports/del2/PHENOL-EXPLORER-3.6_results.md` |
| Recipe identity has 611,714 exact reps, 744,615 kept candidate pairs, but only **6,589 provisional family edges** (strict star clustering, no chaining, `calibrated=false`). The 400-pair blind packet is unlabeled | WORKLOG S134 L920; `reports/step07i/preregistration_v1.md` §1–3, §8 |
| The 07H condition human gate was `NOT_COUNTED_PROVENANCE_INVALID`. Kappa was 0.998, but the two files were written 11 s apart with identical code distributions. Three fields have prevalence 1.00 (kappa-paradox flag). A content bug was also found (calendar months stored as fixed seconds) | `reports/step07/step07h_human_gate_result.json` |
| Gold-v1.1 Food.com is AI-assisted. The annotator is `JOINT`, approval is batch-level, and the review CSV has no row-level decisions | WORKLOG S117–S121, L801–L838; `reports/gold/foodcom_v1_1_review_record.json` |
| H_STATE benchmark: the supported stratum maxes out at **n = 14 over 8 recipe families** (target was 40). Status BLOCKED_HUMAN | `reports/h_state/h_state_benchmark_v1.md` (S114 amendment) |

SSOT/plan anchors used: SSOT §48 L2905–2942 (incl. v4.2 write-back L2933–2942: split assignment at source-entity level *before* de-dup joins); §12.6.5 L12221–12238; §12.6.9–10 L12280–12307; §12.6.15 L12380–12403; §12.7.10 L12940–12954; §191 L14728–14941; §202 L16831–17118 (six split families L16847–16895, headline L16896–16901, statistics L17026–17037, G14 gates L17074–17104, pilot thresholds not frozen); §215.4–16 L22011–22157; G15 gates L22376–22427; §215.53 L22428–22449; §237 L25659–25744; §242.3 L26399–26402; §245 L26604–26711; §257G.9 L34854–34862; §257L card A–G L35081–35143; §278.1/278.3 L45211–45240. Master Plan v4.0: L91–94 (leakage law), L776–780 (bootstrap over families, Holm/BH, analysis plan fixed before test), AH4 L2819–2827 (conformal under shift is empirical), AH5 L2829–2847 (benchmark sizes 104/320/440), AI5–AI6 L3103–3150 (DEL-2 study/publication components), AM3 L3597–3614, AM5 L3626–3633, AW7 L4251–4261, `SPLIT-` registry L4565.

---

## 1. Questions

- Q1. Which leakage types (Kapoor & Narayanan taxonomy) threaten CulinaryState evaluations, and where in the spine are they controlled?
- Q2. For each split in brief §33, which scientific claim does it test? Which splits have no claim, or no data, and should be dropped or deferred?
- Q3. What is the true unit of independence for each evaluation (steps 15, 19, 27, 29–36)? Is study-disjoint or source-disjoint evaluation even feasible with the current EVD?
- Q4. How should grouped / leave-group-out CV and cold-start splits be built, given few groups and provisional duplicate families?
- Q5. What statistical protocol fits: paired cluster bootstrap vs permutation, few-cluster inference, model-selection overfitting, multiple-comparison control, test-set discipline?
- Q6. How should calibration and conformal coverage be evaluated under shift and with grouped data?
- Q7. What are realistic human annotation times and reliability levels for span/event/graph annotation and evidence extraction from papers? How reliable is an LLM as annotator, and how strong is anchoring?
- Q8. Are the Gold and benchmark sizes adequate to detect the differences the gates care about?

---

## 2. Findings per question

### Q1 — Leakage taxonomy (confidence HIGH)
Kapoor & Narayanan (Patterns 2023; arXiv 2207.07048 opened) define eight types: L1.1 no test set; L1.2 pre-processing on train+test; L1.3 feature selection on train+test; L1.4 duplicates; L2 illegitimate features; L3.1 temporal leakage; L3.2 non-independence between train and test; L3.3 sampling bias in the test distribution. Their model info sheet asks for three arguments: clean separation (L1), feature legitimacy (L2), and a test set drawn from the distribution of interest (L3). Corrected leakage erased the claimed superiority of complex ML over logistic regression in civil-war prediction.

Mapping to CulinaryState:
- **L1.4** is near-duplicate recipes and one measurement re-reported by several sources (contract L21).
- **L3.2** is rows from the same study or publication, multiple compounds per food×process cell, and USDA values imputed from donor foods (`provenance_note SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE`).
- **L2** covers study-ID, platform or source-identity features, endpoint phrases ("until golden") as label proxies, and a retrieval index that contains the held-out outcome (SSOT §257L G L35135–35143).
- **L1.2/L1.3** covers propensity/IPW models, imputation and normalisation fitted on all rows. Master Plan L3110 already requires propensity features frozen before outcome inspection.
- **L3.3** applies because the EVD is dominated by two database aggregates, so it is not representative of "literature process effects".

**Consequence:** the §257L A–G card (L35081–35143) already covers most of this. The missing piece is a mandatory **model-info-sheet-style leakage argument per headline claim**, stored with the `SPLIT-` manifest.

### Q2 — Split → claim mapping (confidence HIGH on logic, MEDIUM on feasibility)
Supporting literature:
- Pahikkala et al. 2015 (Brief. Bioinform., opened) define S1 (both entities seen) / S2 / S3 (one side new) / S4 (both new). They show estimates are "optimistically biased" when the split does not match the intended setting: quantitative CI 95.2 in S1 vs 70.0 in S4. Their S4 uses a 3×3 joint CV. They also recommend nested CV.
- Park & Marcotte 2012 (Nat. Methods, PMC3531800 opened): over 99% of random-CV test pairs were C1 (both components seen), while C1 is only ~19% of the real human PPI population. They recommend reporting performance separately per component-overlap class.
- Roberts et al. 2017 (Ecography 40:913–929) recommend block CV for structured data. They warn that blocking can force extrapolation and so overestimate interpolation error. Bibliographic record verified; full text not opened.
- WILDS (Koh et al. ICML 2021, opened) separates domain generalisation (disjoint test domains, average error) from subpopulation shift (worst-group error). The ID–OOD gap persisted under all methods.
- Bernau et al. 2014 (Bioinformatics, opened): cross-study validation gave C-indices ~0.06 lower than within-study CV and **changed algorithm rankings**. They recommend the train-study × test-study matrix summarised by the median.

| Brief §33 split | Claim it tests (the one sentence that can be false) | Spine owner | Feasible now? | Verdict |
|---|---|---|---|---|
| Random | none (sanity / memorisation ceiling only; SSOT L16849–16852) | all | yes | KEEP as reference, never headline |
| Recipe-disjoint | subsumed by the row below | 17, 19, 20, 35, 36 | yes | MERGE into duplicate-group-disjoint |
| Duplicate-group-disjoint | "Recipe-plane model X performs at level m on recipes whose copies/variants were never seen" | 17, 19, 20, 35, 36 | partially: needs a leakage SPLIT_GROUP (see Q4) | KEEP, mandatory default for the recipe plane |
| Source-disjoint (recipe plane) | "Extraction/semantics transfer to a recipe source/template not seen in training" (scale claim of Step 20; NER claim AW7 L4257) | 17, 20 | yes (several recipe sources) | KEEP as headline for extraction |
| Source-disjoint (evidence plane) | "Transition model trained on database A predicts database B" | 29–30 | **effectively no**: 3 sources, PE has zero target overlap, USDA↔Bognár overlap is 67–249 cells on 4 ingredients | RECLASSIFY as a cross-source *agreement diagnostic* (already `cross_source_v1`), not a generalisation benchmark |
| Ingredient cold-start (ingredient-/matrix-disjoint) = S2 | "For a food with no measured evidence, the model beats the hierarchical-fallback lookup" (underwrites Step 36 INTERPOLATE/MODEL modes) | 29–31, 35, 36 | yes (matrix_disjoint already run for PE) | KEEP. Group near-variant matrices (raw/cooked/cultivar of one food) and use food-group-cluster folds as the "scaffold-split analogue" |
| Ingredient × process pair holdout = S1 at cell level | "Compositional generalisation: unseen (food, process) cells from seen food and seen process" (SSOT headline L16896–16901, L22063–22070) | 29–33 | yes | KEEP as headline, with Park–Marcotte C-class reporting. Note that it is the *easiest* cold setting |
| Both-new (S4: food AND process unseen) | "The system abstains or widens intervals when neither side has support" | 36 (CONF/abstention), 29 | yes, small | ADD as an *abstention stratum*, not a performance claim |
| Process-disjoint (leaf held out, parent kept) | "Process hierarchy/physics features transfer to an unseen leaf process" (G15-3) | 31 | weak: 33 PE process signatures, few families | KEEP as leave-one-process-family-out with per-fold reporting. No pooled headline below ~10 folds |
| Condition-OOD | "The kinetic/physics model extrapolates to held-out T/time ranges better than the best tabular baseline" (G15-5) | 27, 32, 33, 34 | **mostly no**: EVD rows are endpoint aggregates with no within-study condition grids | KEEP but NEED_DATA. Block *within study* (e.g. hold out the highest temperature level) and report interpolation vs extrapolation separately (Roberts 2017) |
| Study-disjoint | "Performance is not driven by lab/study-specific effects" (mandatory for literature-mined quantitative claims; L16886–16891, L22097–22102) | 15, 27, 29–33 | **PE only** (125 publications). USDA/Bognár are each one cluster | KEEP. Claim scope must say "PE-only" until Steps 10–14 add identifiable studies |
| Publication-disjoint | the same claim as study-disjoint | 15 | — | MERGE: a single **LINEAGE-COMPONENT-disjoint** split over the publication–study–dataset graph (Master Plan AM3 L3597–3614) |
| Platform-disjoint | "Volatile/analytical predictions transfer across GC-MS / GC-IMS / …" | 30 (volatiles) | **no**: no volatile/platform-varied data in EVD | DEFER. Report stratified by `measurement_method_id` where >1 method exists |
| Matrix-OOD (kinetic food A → food B) | "Simulator/kinetic parameters calibrated on matrix A predict matrix B" | 27, 32 | depends on Step 26 target choice | KEEP for Step 27 V&V only (the ingredient-disjoint idea applied to kinetic datasets) |
| Temporal / historical | "Forecasts future recipe distributions" (E13E-11 L45010–45034) or "dataset-version drift" (§48.x) | L13E lane, 35 | uncertain timestamps | DEFER to the L13E lane. Optional publication-year diagnostic for evidence. Not on the critical path |
| Cuisine holdout | "Representation transfers to an unseen cuisine" (§191.3 L14794–14797 forbids using it for ordinary cuisine classification) | 35 | yes | KEEP only for Step 35 transfer claims |
| Molecular scaffold / fingerprint-cluster | "Molecule encoder generalises to unseen chemotypes" (§12.6.5 L12223–12228) | 35 | yes | KEEP for Step 35 molecule rung. The primary scaffold-split source (Bemis–Murcko / MoleculeNet body) was not opened (UNVERIFIED in my reading); Sheridan 2013 time-split (JCIM 53:783) bibliographic record only |

**Splits dropped or deferred as claim-less or data-less now:** recipe-disjoint (merged), publication-disjoint (merged), platform-disjoint (deferred), temporal (L13E lane only), evidence-plane source-disjoint (demoted to a diagnostic).

### Q3 — Unit of independence (confidence HIGH)
SSOT §278.1 item 10 (L45222) says not to treat millions of recipes from one source as millions of independent sources. SSOT L17030 calls for study-level, not row, bootstrap. The contract (L10) says the number of independent units, not row counts, sets the real sample size.

| Evaluation | Unit of independence (resample / fold unit) | Nested non-independent units |
|---|---|---|
| Step 15 evidence freeze statistics | lineage component (publication ∪ study ∪ dataset-reuse edges). For DB aggregates: the database is **one** cluster; within-DB (matrix×process) cells are descriptive units only | rows, compounds per cell, censored rows |
| Step 19 Gold state-trajectory | recipe SPLIT_GROUP (leakage-conservative duplicate component) | events, entities, state fields within a recipe; annotator pairs |
| Step 27 simulator validation | independent study / experimental campaign (and matrix within it). Validation studies must be lineage-disjoint from parameter-source studies | time points within a trajectory |
| Steps 29–33 transition | lineage component for literature rows. For database rows: (matrix × process × source) cell, with multiple targets grouped | targets/compounds per cell |
| Step 34 rollout | study trajectory | time steps |
| Step 35 representation | recipe SPLIT_GROUP; ingredient entity (+ variants); molecule scaffold cluster | — |
| Step 36 RAG benchmark | benchmark item nested in recipe SPLIT_GROUP and in evidence cell; the authoring session is a possible cluster | paraphrases of one item |

**Feasibility, stated plainly:** with today's EVD, a study-disjoint test with ≥10 independent clusters exists **only for Phenol-Explorer polyphenol retention**. Any "study-disjoint nutrient-retention" claim is impossible until Steps 08/10–14 add identifiable literature studies. Step 14's coverage objective must therefore be stated in **independent lineage components per headline cell**, not rows.

### Q4 — Grouped CV with few groups and provisional families (confidence MEDIUM-HIGH)
- Varoquaux 2017/2018 (arXiv 1706.07581, opened): CV error bars are ±10% at n≈100, and the standard error across folds is "much too optimistic". Journal ref NeuroImage 2018 is from memory; the arXiv page lists none.
- Bates, Hastie & Tibshirani (JASA 2023, arXiv 2104.00673, opened): naive CV intervals under-cover because fold estimates are correlated. They propose nested CV for the variance.
- Cawley & Talbot 2010 (JMLR 11:2079–2107, opened): over-fitting in model selection can be "comparable in size to differences between learning algorithms".

Consequences:
1. With leave-one-group-out on few groups (PE 125 publications, ~10–30 process families), report the full per-fold vector or Bernau matrix and the median. Do not use the across-fold SE as a CI.
2. Hyperparameters are tuned only in **inner grouped folds** (nested).
3. Recipe identity is built for precision (6,589 strict star edges out of 744,615 scored pairs). That is the wrong object for leakage control. **A leakage SPLIT_GROUP must be recall-oriented**: connected components over the candidate graph at a lenient, pre-declared score, plus exact groups, plus mirrored copies. It stays separate from FAMILY. Report the giant-component share. If one component dominates, sub-block it by dish key and report residual cross-split similarity (max IDF-Jaccard of test→train) as a leakage diagnostic.

This follows SSOT §48.x (L2937–2941: assign splits at source-entity level before de-dup joins) and §237.1 L25683 (use duplicate-group and source-family information against leakage). Confidence MEDIUM, because the lenient threshold is a design choice with no literature value. It should be fixed using the 400-pair calibration packet once that is labelled.

### Q5 — Statistical protocol (confidence HIGH on principles; MEDIUM on few-cluster specifics)
- Cameron, Gelbach & Miller 2008 (REStat 90:414–427; NBER t0344 opened): with 5–30 clusters, cluster-robust tests over-reject (10% instead of 5%). Cluster bootstrap-t corrects this.
- Dror et al. ACL 2018 (opened): significance testing in NLP is "often ignored or misused".
- Demšar 2006 (JMLR 7:1–30, opened) recommends Wilcoxon signed-rank for two methods across datasets, and Friedman plus post-hoc tests for more.
- Bouthillier et al. 2021 (arXiv 2103.03098, opened; MLSys acceptance not confirmed on the page): data-sampling, initialisation and hyperparameter variance all "impact markedly the results". Seed variance alone understates uncertainty.
- Dwork et al. 2015 (arXiv 1506.02629, opened): reusing a holdout adaptively overfits it unless reuse is controlled.
- Nosek et al. 2018 (PNAS 115:2600–2606; bibliographic record verified): preregistration separates prediction from postdiction.
- Koehn 2004 (paired bootstrap, EMNLP): metadata only verified.

Recommended protocol:
1. **Claim freeze** (§257L A): one primary metric × one primary split per confirmatory claim, pre-registered in the `SPLIT-`/`EXP-` record before any test access (Master Plan L780).
2. **Paired cluster bootstrap of the metric difference** over the unit of independence (B ≥ 10,000; percentile or BCa CI). Same folds for both models.
3. **If fewer than ~20–30 clusters:** cluster-level sign-flip permutation test on the per-cluster paired differences (exact if ≤ 20 clusters), plus per-cluster tables. Report n_clusters beside every number (contract L24).
4. **Promotion rule as a margin test:** the complex model is promoted only if the lower CI bound of its improvement over the best simple baseline exceeds a pre-declared practical margin δ, on the headline split, without breaching calibration (Master Plan AM5 L3626–3633; SSOT L17092–17104). Otherwise the simple model ships, which is a valid result.
5. **Multiplicity:** Holm across the small confirmatory family per gate. BH-FDR for exploratory slices (SSOT §278.1(4) L45215; Master Plan L778).
6. **Seeds:** ≥ 5 for stochastic learners (SSOT L17029), reported as an additional variance source, never as a substitute for data/cluster resampling.
7. **Locked test:** sealed with a hash commitment and an access log (count of reads per claim). One read per confirmatory claim. Any second read needs a recorded H5 approval (Master Plan L139) and is labelled exploratory.
8. **Effect sizes with CIs; negative results retained** (SSOT §278.1(1,8)).

### Q6 — Calibration and coverage under shift (confidence HIGH)
- Ovadia et al. NeurIPS 2019 (opened): calibration degrades under dataset shift and post-hoc calibration "falls short", so calibration must be measured on the cold/OOD splits, not ID.
- Tibshirani et al. 2019 (arXiv 1904.06019, opened; venue NeurIPS 2019 from memory): weighted conformal needs a known or well-estimated likelihood ratio.
- Barber et al. (arXiv 2202.13415, opened; Ann. Statist. 2023 from memory): weighted conformal loses less coverage under non-exchangeability, with no general guarantee.
- Dunn, Wasserman & Ramdas (arXiv 1809.07441, opened; accepted JASA): conformal sets for two-layer hierarchical data, covering a new group. CDF pooling suits asymptotic coverage; repeated subsampling suits finite-sample coverage.

Consequence: this confirms Master Plan AH4 (L2819–2827). Report **empirical coverage and width per split family and per cluster (worst-cluster coverage, WILDS-style)**. Calibration sets must be **lineage-disjoint from test and from training** (§242.3 L26399–26402; G15-6 L22376+). Group-aware (Dunn) conformal should be the default experiment for study-grouped data, because the target claim is coverage for a *new study*. Classification calibration: ECE + Brier + reliability. Regression: interval coverage/width + risk–coverage.

### Q7 — Human effort and LLM-annotator reliability (confidence MEDIUM; hours are transferred estimates)
Measured benchmarks (all primary sources opened unless noted):
- **Procedural text (closest analogue to recipe event graphs):** wet-lab protocols, 622 protocols, 10 annotators. **~33 min per 40-sentence protocol** for actions + entities + relations. Krippendorff α 0.76 (entities+actions) and **0.66 (relations)**. Source: Kulkarni et al. NAACL 2018.
- **Recipe flow graphs:** English r-FG has 300 recipes with IAA 82.3–90.5 F1 and model F1 71.1–87.5 (Yamakata et al. LREC 2020). Time per recipe was not obtained (UNVERIFIED).
- **Clinical NER:** 36.6–52.7 s per entity unassisted, 28.7–45.4 s with dictionary pre-annotation (13.85–21.5% saving). About 10.5–12.3 min per clinical-trial announcement unassisted (derived from 17.5–20.5 h per 100 documents). No IAA difference detected. Source: Lingren et al. JAMIA 2014.
- **Evidence extraction from papers:**
  - Single extraction plus verification takes 36.1% less time than independent double extraction but makes 21.7% more errors (Buscemi et al. J Clin Epidemiol 2006, abstract opened).
  - Extraction error rates reach up to 50% (Mathes et al. BMC MRM 2017; metadata/abstract via search, PMC page blocked: partially verified).
  - An LLM (Claude 2) extracted 160 data elements from 10 RCTs at 96.3% accuracy. The dominant error was *missed items* (Gartlehner et al. Res Synth Methods 2024; abstract via RTI opened).
  - Environmental systematic reviews take ~164 FTE-days, and extraction plus appraisal takes as long as screening (Haddaway & Westgate, Conserv Biol 2019; search-level only, UNVERIFIED).
- **LLM-as-annotator:**
  - GPT-4 annotation quality varies by task across 27 tasks, so it must be validated per task against human labels (Pangakis et al. 2023, arXiv preprint).
  - The alt-test (Calderon, Reichart & Dror, ACL 2025, opened) is a statistical procedure that uses a modest human-annotated subset to justify replacing human annotators with an LLM.
- **Anchoring:** when shown LLM suggestions, experts' agreement with the LLM rose from **43.9% to 71.5%** while speed rose 133% (Choi et al. EMNLP 2024, opened). AI-suggestion review shows over-reliance that depends on the reviewer's attitudes (Beck et al. 2025 arXiv preprint, opened).
- **Kappa paradox:** high agreement can come with low or unstable kappa under skewed prevalence (Feinstein & Cicchetti, J Clin Epidemiol 43:543–549, 1990; bibliographic record only). The repo's 07H gate already flags prevalence 1.00 fields.

Project-specific estimates. These are DERIVED, not measured, and must be replaced by timing logs from the first pilots:
| Task | Estimate per item per annotator | Basis |
|---|---|---|
| Deep-Gold recipe state trajectory (entities, events, intermediates, state fields; ~10–15 steps) | 45–90 min | Kulkarni 33 min / 40 sentences, scaled up for a richer schema |
| Adjudication | +30–50% of one pass | general practice (UNVERIFIED) |
| Course Deep Gold 40 recipes, double-annotated + adjudicated | ≈ 80–160 person-hours | arithmetic on the rows above |
| Verifying one LLM-extracted EVD row against its source table/span | 2–6 min | Gartlehner + Buscemi (ESTIMATE) |
| Full extraction of one food-processing paper (10–30 rows) | 30–90 min single; ×1.36–2 for independent double | Buscemi ratio |
| Duplicate-pair judgement (400-pair packet) | 20–60 s → 2–7 h per reviewer | ESTIMATE |

**Internal evidence that the independence protocol must be enforced technically, not by instruction:**
- The 07H packet files (11 s apart, identical distributions) were invalid as a human gate.
- Gold-v1.1 is `JOINT` and AI-assisted, with only batch approval.
- Under SSOT §237.1 (L25663–25664) and §236.2 (L25599–25602), neither counts as independent Deep Gold. They are, at best, Gold-Light / AI-assisted human-reviewed data.

### Q8 — Are benchmark and Gold sizes adequate? (confidence HIGH; arithmetic)
95% CI half-width for a proportion at p = 0.8 (p = 0.5), before any cluster design effect:

| n | ±(p=0.8) | ±(p=0.5) |
|---|---|---|
| 14 | 0.21 | 0.26 |
| 40 | 0.12 | 0.16 |
| 80 | 0.09 | 0.11 |
| 104 | 0.08 | 0.10 |
| 240 | 0.05 | 0.06 |
| 320 | 0.04 | 0.06 |

Paired comparison (McNemar, α = 0.05, power 0.8): detecting a 10 pp difference needs **≈155 items** at 20% discordance and ≈233 at 30%. A 5 pp difference needs ≈626.

So:
- The Master Plan minimum (80 locked test items, L2845) cannot distinguish systems that differ by 10 pp. The **240 locked target (L2846) is the minimum for a 10 pp paired claim**.
- H_STATE-R at n = 14 / 8 families can only give descriptive results.
- Clustering inflates all of these by the design effect 1 + (m−1)·ICC.

---

## 3. Architecture recommendation

**R-1. Claim-first split registry (`SPLIT-`, Master Plan L4565).** Each split manifest carries:
- `claim_id` (§257L A sentence), `plane` (RECIPE | EVIDENCE | MOLECULE | BENCHMARK), `split_family`, `independence_unit`;
- `group_key_definition` + version hash, `n_groups_{train,val,calib,test}`, `n_rows_*`, `giant_component_share`;
- `feasibility_status` (FEASIBLE | DIAGNOSTIC_ONLY | NEED_DATA);
- `leakage_argument` (model-info-sheet L1/L2/L3 text);
- `test_seal_hash`, `test_access_log`, `primary_metric`, `margin_delta`, `multiplicity_family`.

A split with no claim_id is not built.

**R-2. Two grouping objects on the recipe plane.** FAMILY (precision-oriented identity; exists) and SPLIT_GROUP (recall-oriented leakage component; new, inside Step 07I/15 artifacts). All Gold, benchmark and model splits use SPLIT_GROUP. A Gold recipe's SPLIT_GROUP is excluded from every training set that model is evaluated against.

**R-3. One lineage-component split on the evidence plane.** Components come from the Step 08 graph (SOURCE → DOCUMENT → STUDY → EXPERIMENT, plus `re-reports`/`compiled_from` edges between databases and papers). Study-disjoint and publication-disjoint merge into it. Rows with `NOT_IDENTIFIABLE` study keep their database as one component.

**R-4. Headline evidence-plane benchmark = pair-holdout (C-class reported) ∩ lineage-component-disjoint, with ingredient-cluster-disjoint as the second headline** (SSOT L16896–16901 retained). Process-disjoint and condition-OOD are claim-specific (Steps 31, 32–33). Both-new is an abstention stratum.

**R-5. Statistical protocol as in Q5:** pre-registered primary claim, paired cluster bootstrap / cluster permutation, margin-based promotion, Holm (confirmatory) + BH (exploratory), nested grouped tuning, a sealed test with an access log, and n_clusters always reported.

**R-6. Human-annotation protocol with enforced independence:**
- packets issued per annotator with separate IDs;
- Deep Gold never shows model output;
- per-item start/end timestamps logged;
- labels hash-committed before the other annotator's file is opened;
- IAA reported as raw agreement + kappa/α + prevalence (+ PABAK or positive/negative agreement where prevalence > 0.9);
- an automatic "provenance validity" check (file mtimes, identical-distribution test, as built in 07H) runs before any human gate counts;
- LLM-as-annotator is allowed only for Silver/Gold-Light after an alt-test-style validation on a human-labelled subset per task.

Rejected alternatives:
- (a) **Build all 12+ split families for every step.** No claim for several of them, and no data for platform-disjoint or study-disjoint nutrients. Inflates the multiplicity family and human work.
- (b) **Random CV with post-hoc stratified reporting.** Leaves L1.4/L3.2 leakage in (Park & Marcotte >99% C1). Ruled out by SSOT §48.x.
- (c) **Using provisional FAMILY as the split group.** It under-groups near-duplicates by construction (6,589 edges out of 744,615 candidate pairs).
- (d) **Row-level bootstrap or fold-SE CIs.** Under-cover (Bates 2023; Varoquaux 2018; SSOT L17030).
- (e) **Nominal conformal guarantees under shift.** Invalid without exchangeability (Barber 2023; AH4).
- (f) **Kappa alone as the human gate.** The paradox under skewed prevalence; 07H shows it.
- (g) **AI-assisted joint annotation as Deep Gold.** The anchoring evidence (Choi 2024) and SSOT §237.1 rule it out.

---

## 4. What each affected spine step must change or add

(Step content is reconstructed; the step cards are missing.)

- **Step 15 Freeze DATA-EVIDENCE v1:**
  - Add outputs: lineage-component table; evidence-plane `SPLIT-` manifests for the claim-mapped families (random-ref, pair-holdout + C-class, ingredient-cluster-disjoint, lineage-disjoint, process-family-disjoint, condition-OOD = NEED_DATA flag, both-new stratum); feasibility report (n components per split and headline cell; giant-component share); sealed locked-test hash + access log; dataset card with n_independent_groups per target/process family (§236.7 L25655–25658, §257G.9 L34854–34862).
  - **Gate:** every *headline* split has ≥ K independent test clusters (PROPOSED_PILOT K = 10; not literature-derived). Otherwise the claim is downgraded to DIAGNOSTIC_ONLY in the registry. Zero SPLIT_GROUP / lineage components cross splits (§257G.9).
- **Step 19 Gold state-trajectory pilot:**
  - Input: SPLIT_GROUP assignment before sampling.
  - Add: the R-6 protocol; per-item timing; per-task IAA (§237.3 L25703–25716); `annotation_mode` ∈ {INDEPENDENT_BLIND, AI_ASSISTED, JOINT}, `seen_model_output`, `annotator_id`, timestamps.
  - Output: minutes-per-recipe estimate that sizes Step 20 Gold.
  - **Gate:** a provenance-validity check passes AND pre-registered IAA thresholds pass (PROPOSED_PILOT; e.g. relation-level α/F1 thresholds set from the Kulkarni/Yamakata ranges, 0.66–0.90). Existing Gold-v1.1 is relabelled AI_ASSISTED (Gold-Light) unless re-annotated blind.
- **Step 27 Validate simulator:**
  - Validation evidence must be lineage-disjoint from parameter/calibration sources (automatic check against the Step 24 registry `parameter_source`/`calibration_source`).
  - Primary splits: matrix-OOD and condition-OOD within the chosen target.
  - Metrics: trajectory error, residuals, interval coverage per study, comparison vs the B-4 nearest-compatible-evidence lookup with a paired cluster test over studies.
  - Fewer than ~5 independent validation studies → result is RESEARCH_ONLY (brief §40).
- **Step 29 TRANSITION_BOOTSTRAP_V0** (`reports/h_state/transition_bootstrap_v0_contract.md`):
  - Keep S-1..S-5.
  - S-6 scope: "PE-only".
  - S-7 becomes DIAGNOSTIC_ONLY.
  - Add C-class reporting, the both-new stratum, paired cluster bootstrap vs B-0 and vs the best deterministic baseline, and the n_clusters column.
  - **Investigate D7 ≡ D1** (degenerate MF) before any D7 claim.
- **Step 30 Tabular/sparsity bake-off:** nested grouped CV; inner tuning only; confirmatory family = {best D5+ vs best D0–D4} per headline split, Holm-corrected; margin-δ promotion. TabPFN/learned models are optional and CPU-first.
- **Step 31 Physics/condition features:** claim = condition contribution over label-only (G14-7 L17083), on process-family-disjoint and condition-OOD splits. Grouped permutation and ablation of feature families (L16947–16960).
- **Step 32 Focused kinetics:** within-study fits; parameter transfer evaluated leave-one-study-out; AICc/BIC + held-out (L22130–22141); identifiability report.
- **Step 33 Mechanistic vs ML vs hybrid:** the single pre-registered confirmatory comparison of Phase G, on condition-OOD + matrix-OOD; G15-HYB L22412–22415.
- **Step 34 Short rollout:** only datasets with true intermediate states. Unit = study trajectory. Trust horizon with cluster CI (G15-11).
- **Step 35 Representation ladder:** molecule scaffold/fingerprint-cluster split; ingredient-cluster-disjoint; recipe SPLIT_GROUP + recipe-source-disjoint; cuisine holdout for transfer only; non-circular rule §191.9; frequency panel §191.7.
- **Step 36 RAG:**
  - Benchmark items carry `split_group_id` and `evidence_cell_id`.
  - When evaluating the transition-fallback mode, the retrieval index excludes held-out test evidence (L2 leakage).
  - Abstention evaluation includes the both-new stratum.
  - Locked test ≥ 240 for any 10 pp paired claim.
  - Report the achieved tier (AH5).
- **Parts P/Q/R of the master output:**
  - P = R-1..R-5 plus the split→claim table.
  - Q: all evaluation statistics are CPU-cheap (bootstrap of a few hundred clusters × 10k resamples is seconds to minutes on 128 cores); no GPU is needed for evaluation.
  - R: the human-hour table in Q7, plus the rule that pilots log time.

---

## 5. Look-ahead requirements for earlier steps

1. **Step 07I identity:**
   - Emit SPLIT_GROUP (recall-oriented components at a pre-declared lenient score), its giant-component share, and a cross-split residual-similarity diagnostic.
   - Fix the lenient threshold from the 400-pair packet once it is labelled.
   - Never auto-merge (preserves the law that source recipes are immutable).
2. **Step 07 conditions:** keep per-study condition grids (multiple T/time levels) as structured lists, so condition-OOD blocking is possible. The 07H months→seconds content bug must be fixed before any condition-OOD split.
3. **Step 08 lineage (not started; NOT authorised here):** must provide:
   - DOCUMENT (DOI / publication ID, year), STUDY, EXPERIMENT/campaign, optional lab/author group;
   - `re_reports` / `compiled_from` edges linking database rows to the papers they compile (so cross-source copies fall in one component);
   - `value_reuse_of`, `donor_food` for USDA imputations when identifiable;
   - `is_trajectory` / time-series flag, `replicate_n`;
   - `measurement_method_id` (exists) for platform stratification.

   Without these, Step 15 cannot build lineage-disjoint splits.
4. **Step 09 extraction machinery:** store a source span/table locator for every LLM-extracted value (G15-H L22396) and the verification mode, to enable row-level human verification and timing.
5. **Steps 10–14 acquisition:**
   - Coverage targets in **independent lineage components per (matrix-family × process-family × target) cell**, with a minimum (PROPOSED K ≥ 10 for headline cells).
   - Prefer studies with within-study condition variation (needed for condition-OOD and kinetics).
   - Step 10's 20-row pilot must log minutes per row for extraction and verification, single vs double.
6. **Steps 16–17:** annotation schema includes `annotation_mode`, `seen_model_output`, timestamps and annotator IDs. Endpoint phrases are flagged as potential label proxies for state targets (L2).
7. **Step 24 registry:** `parameter_source` and `calibration_source` must reference lineage components, so Step 27 can verify disjointness automatically.

---

## 6. Residual uncertainty, and pilot vs more reading

- **Feasibility of study-disjoint headlines after acquisition** is the dominant uncertainty, and an empirical census is cheaper than reading. After Step 08, count lineage components per headline cell with stdlib on the CPU (minutes). Until then, the only study-disjoint claim is PE polyphenols.
- **Human hours** are transferred estimates from other domains (MEDIUM/LOW). Timing logs in the duplicate-packet review, the condition packet v4, the Step 10 pilot and the Step 19 pilot will settle them. That is cheaper than more literature, so research stops here (§8 rule 5).
- **SPLIT_GROUP threshold and giant-component risk:** decided by the labelled 400-pair packet. No literature value exists.
- **K (minimum clusters), δ (practical margins), IAA thresholds:** PROPOSED_PILOT values only, calibrated after the first baseline run (SSOT §202.17 L17106–17118 forbids treating them as literature standards).
- **D7 ≡ D1 anomaly:** a bug or a degenerate model. A cheap read-only check is needed before Step 30.
- **Unverified items:** Field & Welsh (cluster bootstrap theory) not opened. Roberts 2017, Nosek 2018, Feinstein & Cicchetti 1990, Sheridan 2013, Haddaway & Westgate 2019 and Mathes 2017 verified only at bibliographic/search level. Yamakata 2020 annotation time not found. Koehn 2004 content not read (PDF unreadable).

Stop rule met: the evidence suffices to choose the split architecture (R-1..R-6). Remaining questions are empirical and cheaper to answer by census or pilot.
