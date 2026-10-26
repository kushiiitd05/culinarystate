# r_transition_ml — research notes for spine Steps 29–34 (Phase G, Transition Science)

Researcher: r_transition_ml · Date 2026-10-22 · PLAN-RESEARCH ONLY (no training, no downloads, no git writes).
The 36-step plan step cards are MISSING (ctx.md). This file does not quote them. Step content below is
reconstructed from the SSOT, the Master Plan v4.0, the MP-1 contract and the DEL-2 code and reports, and each claim says which.

## 0. Internal evidence base (read-only, verified in this session)

| Item | Where | What it says |
|---|---|---|
| Canonical ladder D0–D11 | SSOT §209.17 L18543–18616 | D0 persistence → D1 global mean-delta → D2 process mean → D3 hierarchical shrinkage → D4 nearest evidence → D5 GBDT → D6 TabPFN → D7 low-rank/side-info completion (BPMF/Macau/FM/tensor) → D8 classical kinetics → D9 hybrid residual → D10 neural multi-output/latent dynamics → D11 UDE/neural ODE. "sparse-data structure appears before neural dynamics" |
| Tabular baseline definition | SSOT §209.6 L18338–18361 | x = [z_i, P, θ, S_t, source/platform controls, physics features]. Ridge, LightGBM/XGBoost, TabPFN "define the credibility floor" |
| Physics exposure features | SSOT L15834–15847 | peak/mean T, time above threshold, log-duration, 1/T, Arrhenius exposure integrals at representative Ea, F-value. These are "features/inductive biases, not proof of mechanism" |
| Physics constraints | SSOT §201.12 L16752–16762 | non-negativity, degradation-only monotonicity, mass/retention bounds. Not for formed compounds or open systems |
| Hierarchical kinetics | SSOT §211.21 L19476–19487 | log k_i ~ N(μ_k, σ_k²), "only when targets/definitions are comparable" |
| Sequential hybrid fitting | SSOT §211.45 L19745–19755 | Fit the mechanistic model → freeze it → residuals → ML on the residuals with grouped data |
| Rollout evaluation | SSOT §215.16–17 L22142–22165 | Report E(1..K), final-state error, constraint violations, coverage, trust horizon, D(k)=E(k)/E(1) |
| Null-transition test | SSOT §215.24 L22236 | "Persistence remains a real benchmark" |
| Gate system G15-1..12 | SSOT §215.38 L22375–22398 | G15-2 D0–D6 before D7+. G15-3 process signal on process-disjoint split. G15-4 identifiable kinetic fit. G15-5 condition-OOD value over the best non-kinetic tabular model. G15-6 real **study-disjoint** calibration. G15-8 consistency. G15-9 D7 must beat D5/D6 on cold tests or be rejected. G15-11 rollout only where true intermediate states exist |
| G15-HYB | SSOT L22412–22415 | A hybrid needs held-out/OOD/calibration value beyond **both** the mechanistic model and pure ML |
| Kinetic identifiability acquisition | SSOT §224.4 L24304–24314 | Choose T/time/initial condition to maximise information on k, Ea |
| MP-1 TRANSITION_BOOTSTRAP_V0 contract | reports/h_state/transition_bootstrap_v0_contract.md | E1–E4 only. B-0..B-4 deterministic, B-5 tabular. S-1..S-7 splits. Headline = min over S-2..S-5. **Supported only if paired LB>0 vs B-0 on S-3 or S-4**. No complexity escalation on V0. Independent units: USDA 171, Bognár 123, PE 287 matrix×process signatures |
| Master Plan ladder (conflicting numbering) | docs/plan/…v4_0.md AZ6 L4696–4720 | D0 persistence, D1 process mean, D2 nearest, D3 linear/tree, D4 neural residual, D5 conditioning, D6 multi-output, D7 sparse completion, D8 kinetics… **This ordering and numbering differ from SSOT §209.17**. The AI6 DEL-2 list L3127–3139 does follow the SSOT |
| DEL-2 code | src/culinarystate/transition/{baselines,splits,evaluate}.py | D5 = sklearn HistGradientBoosting on categorical + mask features (no physics numerics). D3 = target×process→process→global empirical-Bayes. It does not pool over matrix/food group or study. D7 = biased MF matrix×(process,target). Conformal = split-conformal on absolute residuals, labelled empirical (AH4). D6 TabPFN SKIPPED |
| DEL-2 results (negative result) | reports/del2/*.md; WORKLOG L117, L276 | **USDA**: random D5 0.025 vs D0 0.121. matrix-disjoint D0 0.059 vs D4 0.057 vs D5 0.069 (CIs overlap: cold-food gain vanishes). Conformal-90 coverage on cold splits 0.72–0.87. **Phenol-Explorer** (log): study-disjoint best is D1 global mean, 0.487 [0.24,0.73]. D5 0.61 is worse than D0 0.56 on the raw scale. Matrix-disjoint: all models ≈ D0. **Bognár**: D5 wins on all splits, but the factors are templated (7 process signatures, grid density 0.62) and the process split is degenerate. Cross-source USDA↔Bognár: same-cell MAE 0.075–0.083, Spearman 0.61–0.69. FDC dry-basis vs R6 MAE 0.167 |

### Read-only diagnostics run here (stdlib Python on ledgers/data, latest versions, ACTIVE; heuristic keys; UNVERIFIED E3 rows)
- EVD ACTIVE by source: USDA-RETN-R6 7,018; BOGNAR-2002 7,090; PHENOL-EXPLORER-3.6 3,870 (total 17,978, matching WORKLOG S129).
- Condition completeness on EVD rows. **USDA: temperature MEASURED on 0 rows** (duration MEASURED 259, RANGE 468). **Bognár: duration MEASURED on 0 rows** (T MEASURED 384, T RANGE 3,403). **PE: both T and duration MEASURED on 1,561 rows.** Moisture and pH are UNKNOWN on every COND row (4,414).
- Pseudo-time series in PE: an endpoint retention reported at ≥3 durations for the same (publication, raw matrix, steps, compound, T). There are **152 series from 26 of 125 publications** (116 with T known). Series with ≥3 temperatures at a fixed time: **29 series from 3 publications**. This means first-order or Weibull retention-vs-time fits are possible for roughly 26 publications. Arrhenius (Ea) identifiability from current EVD exists for at most about 3 publications.
- Multi-step process rows (composite start→end, no intermediate state): USDA 1,429 rows with ≥2 steps, PE 195, Bognár 0. **No row in EVD records a true intermediate state.**

## 1. Questions

- Q1. Do tabular deep-vs-tree benchmarks tell us which model family fits about 18k EVD rows / ~600 independent cells across 3 source families?
- Q2. Is TabPFN v2 (or later tabular foundation models) valid for this regime, and what are its limits (size, shift, licence, compute)?
- Q3. Regularised linear, mixed-effects, hierarchical Bayesian and meta-regression for multi-study retention data: what is credible, and is the current D3 enough?
- Q4. Gaussian processes and multitask learning: useful here?
- Q5. Matrix/tensor completion and factorisation machines for ingredient×process×nutrient cells under MNAR: when do they win?
- Q6. Conformal prediction under covariate/group shift and cold start: what guarantees exist and what should Step 30 report?
- Q7. Physics-informed, hybrid and grey-box ML in food processing (2022–2026): maturity and data needs?
- Q8. Neural ODE/CDE/UDE for kinetics: when are they justified?
- Q9. Rollout error compounding: what evaluation and training controls are standard?
- Q10. Is the order bootstrap → tabular → physics features → kinetics → hybrid → rollout right, and what is the baseline ladder?

## 2. Findings per question

### Q1 Tree vs deep benchmarks — confidence HIGH (for IID); MEDIUM (transfer to our grouped regime)
- Grinsztajn, Oyallon & Varoquaux (NeurIPS 2022 D&B; arXiv 2207.08815) used 45 datasets with a 20,000 compute-hour search. Trees remain state of the art on ~10k-sample tabular data. NNs are hurt by uninformative features, rotation invariance, and difficulty fitting irregular functions.
- McElfresh et al. (NeurIPS 2023 D&B; arXiv 2305.02997) compared 19 algorithms on 176 datasets. The NN-vs-GBDT gap is often negligible. **Light GBDT tuning matters more than the family choice.** GBDTs handle skewed and heavy-tailed features better. TabPFN was the best on average even when subsampled to 3,000 training points.
- Gorishniy et al. (NeurIPS 2021; arXiv 2106.11959) found "no universally superior solution" between FT-Transformer/ResNet and GBDT. TabM (Gorishniy, Kotelnikov, Babenko, ICLR 2025; arXiv 2410.24210) is the best tabular DL model, using MLP ensembling.
- TabArena (Erickson et al., NeurIPS 2025 D&B spotlight; arXiv 2506.16791 v4) covers 51 datasets with 500–250k training samples. **It includes IID data only and explicitly excludes "temporal dependencies, subject groups, or distribution shifts".** CatBoost is the best single model under conventional tuning. TabM, LightGBM and RealMLP lead only with post-hoc ensembling. Foundation models lead on small data. TabArena recommends inner CV over holdout and repeated outer CV.
- Gardner, Popovic & Schmidt, TableShift (NeurIPS 2023 D&B; arXiv 2312.07577): OOD accuracy is roughly linear in ID accuracy. Domain-robustness methods narrow the gap at an ID cost. The shift gap tracks label-distribution shift.
- **Consequence:** the public benchmark evidence is IID. It supports "a tuned GBDT is the strong-baseline floor" but says nothing about our cold-group splits. Our own DEL-2 result is the relevant evidence there: GBDT gains vanish on matrix- and study-disjoint splits. The deciding factor is the **effective sample size (≈100–300 independent cells per source) and the shift**, not the family.

### Q2 TabPFN v2 and tabular foundation models — confidence HIGH on limits; LOW on cold-group value
- Hollmann et al., Nature 637:319–326 (2025), doi:10.1038/s41586-024-08328-6 (PMC11711098, opened). The claimed scope is "up to 10,000 samples and 500 features". **Evaluation used random 90/10 splits only.** Data drift is listed as future work. A GPU is recommended for speed (1–3 orders of magnitude), though the model "can run on consumer hardware for most datasets". Regression was tested on 28 AMLB/CTR23 datasets.
- TabPFN-2.5 (arXiv 2511.08667; HF model card opened) raises the scope to ≤50k samples and ≤2k features. **The weights licence (tabpfn-2.5-license-v1.1) forbids commercial and production use.** Research and internal benchmarking are permitted.
- TabPFN-3.5 Technical Report (arXiv 2609.17895, v2 22 Sep 2026, a vendor preprint, opened) claims SOTA extended to "non-i.i.d. data with temporal or grouped splits". The abstract gives no numbers. This is not independent or peer-reviewed, so it is treated as UNVERIFIED for planning.
- **Consequence:** our sizes (≤7k rows per source) are inside TabPFN v2's scope, and CPU inference is feasible at this size (latency is not a constraint offline). No peer-reviewed evidence shows TFMs fix cold-group extrapolation. D6 should be run as one more comparator under the same grouped splits, with the licence recorded and no headline dependence. TabPFN's in-context nature also makes **split hygiene critical**: the context set must contain only training groups.

### Q3 Regularised linear, mixed-effects, hierarchical Bayesian, meta-regression — confidence MEDIUM-HIGH
- In a food analogue, Karamcheti et al., Food Microbiology 128:104731 (2025), doi:10.1016/j.fm.2025.104731, pooled 476 D-values from 27 articles. They used a hierarchical Bayesian linear mixed model with random effects for strain **and study**. The best model had both, and **between-study variability exceeded strain variability**. Models were compared on predictive ability, Bayes-R² and WAIC. This is direct evidence that study random effects belong in any multi-study food-process model.
- SSOT §211.21 already prescribes partial pooling of log k. The repo's D3 is a nested target×process→process→global shrinkage: it does not pool over matrix/food group or study, and it has no crossed random effects.
- van Boekel, CRFSFS 7:144–158 (2008), doi:10.1111/j.1541-4337.2007.00036.x (metadata verified) and J Food Eng 306:110634 (2021), doi:10.1016/j.jfoodeng.2021.110634 (metadata verified; content NOT read) are the standard food-kinetics statistical workflow references.
- **Consequence:** add a **D3+ crossed random-effects model** on the logit/log retention scale: matrix (nested in food group) + process (nested in family) + target (nested in class) + source/study random intercepts, plus a few interactions (food group×process family, target class×process family). Fit it by REML or a Bayesian equivalent. It is the natural "simple but strong" model for cold matrix and process prediction: it predicts the food-group/process-family mean for an unseen matrix. It also gives honest study-level variance, which is exactly what the study-disjoint splits measure. It runs on CPU in seconds to minutes. A biased MF (D7) is its bilinear extension, so D3+ is the right control for G15-9.

### Q4 Gaussian processes and multitask — confidence MEDIUM
- Bonilla, Chai & Williams, NIPS 20 (2007) multitask GP: a shared input kernel times a task covariance. **With noise-free data in a block design (all tasks observed at the same inputs), transfer cancels.** Transfer helps only for unobserved cells, which is our cold case, but the input kernel needs meaningful similarity over matrices and processes. We lack that for cold matrices beyond food group and the FDC/USDA nutrient composition.
- **Consequence:** do not add GPs as a headline arm. For the PE subset that has numeric T and time, a GP over (log t, 1/T) per compound class is a reasonable smooth-interpolation baseline inside Step 31/32. Multitask learning is already captured by D3+ (shared random effects across targets) and D7 (latent factors across targets). A separate neural multitask net is D10 territory and must not skip D0–D7 (SSOT §209.17).

### Q5 Matrix/tensor completion, FMs, MNAR — confidence MEDIUM
- Rendle, ICDM 2010 (doi:10.1109/ICDM.2010.127): FMs generalise MF to arbitrary features (side information). Simm et al., Macau (arXiv 1509.04610): Bayesian multi-relational/tensor factorisation with side features, which are "crucial for predicting sparsely observed relations".
- MNAR: Schnabel et al., ICML 2016 (arXiv 1602.05352) introduced propensity-debiased evaluation and training. Ma & Chen, NeurIPS 2019 (arXiv 1910.12774) estimate missingness propensities via low-nuclear-norm completion of the observation mask.
- Repo evidence: D7 biased MF never beats D5 or D4 on USDA cold splits. On PE matrix-disjoint log it is nominally best (0.738 vs D0 0.767), but the CIs overlap heavily. Propensity AUC is 0.81–0.91, which is strong MNAR.
- **Consequence:** keep D7 per G15-9, but specify it as an FM or tensor model with side features (food group, nutrient-composition vector from FDC raw food, process family, medium, water contact, target class). Pure-ID MF cannot predict a cold row or column except through biases. G15-9's "or is rejected" is the likely outcome and is acceptable. Use IPW/propensity-weighted metrics as a reported sensitivity (already in DEL-2), not as the headline.

### Q6 Conformal under shift and cold start — confidence HIGH (theory)
- Split/jackknife+/CV+ guarantees need exchangeability: Barber, Candès, Ramdas & Tibshirani, jackknife+ (arXiv 1905.02928). Weighted conformal under covariate shift needs a known or well-estimated likelihood ratio (Tibshirani et al., arXiv 1904.06019). Barber et al., Ann. Statist. 51(2):816–845 (2023), doi:10.1214/23-AOS2276: weighted quantiles bound the coverage loss under drift but do not restore guarantees.
- Hierarchical data: Dunn, Wasserman & Ramdas, JASA 118(544):2491–2502 (2023), doi:10.1080/01621459.2022.2060112 propose CDF pooling and subsampling; **use repeated subsampling, one point per group, when finite-sample coverage is needed**.
- CQR (Romano, Patterson & Candès, arXiv 1905.03222; NeurIPS 2019) gives adaptive widths.
- Repo evidence: split conformal calibrated on a random calibration set under-covers on cold splits (USDA process-disjoint D4 0.72; PE matrix-disjoint 0.74–0.82).
- **Consequence:** the calibration set must be **group-disjoint in the same way as the test split** (calibrate on held-out matrices for a matrix-cold claim, and on held-out studies for G15-6). Use group-level subsampling (Dunn et al.) or group-CV+. Report per-split coverage and width. When in-split coverage at nominal 90% falls below a pre-registered floor (for example 0.85), the route must downgrade to QUALITATIVE/ABSTAIN rather than widen silently. Coverage stays labelled "empirical" (AH4) for cold-start, because no method guarantees coverage for a genuinely new group without exchangeability across groups.

### Q7 Physics-informed and hybrid ML in food processing — confidence MEDIUM
- Purlis, Curr. Food Sci. Technol. Rep. 2(1):1–6 (2024; online Dec 2023), doi:10.1007/s43555-023-00012-6 (metadata verified; body not read): PIML in food process modelling is "in a development phase", mainly PDE/transport problems.
- Khan, Sablani, Nayak & Gu, CRFSFS 21 (2022), doi:10.1111/1541-4337.12912 (metadata verified; body not read) is an orientation review.
- von Stosch et al., Comput. Chem. Eng. 60:86–101 (2014), doi:10.1016/j.compchemeng.2013.08.008 (metadata verified) is the canonical hybrid semi-parametric reference in process systems. Hybrid value arises with **time-resolved process data**.
- Closest domain comparator: Naravane & Tagkopoulos, Curr. Res. Food Sci. 6:100500 (2023), doi:10.1016/j.crfs.2023.100500 (PMC10160345, opened). Using 425 raw/cooked pairs from USDA SR Legacy, ML beat USDA retention factors by RMSE −43% (wet heat) and −18% (dry heat). But the **split was not described as food-held-out**, food source and cooking method are fully confounded, each food has one sample, cooking time/temperature/water are absent, and the authors say much more data is needed. This supports the repo's caution: published "ML beats retention factors" gains are not cold-split evidence.
- **Consequence:** hybrid modelling is justified only for systems with time and temperature resolved data (D-C). For endpoint retention aggregates, "physics" is limited to features and soft constraints (SSOT §201.12; L15834).

### Q8 Neural ODE/CDE/UDE — confidence HIGH (that they are not justified now)
- Chen et al., Neural ODE (NeurIPS 2018; arXiv 1806.07366). Kidger et al., Neural CDE (NeurIPS 2020; arXiv 2005.08926) target irregular, partially observed multivariate time series. Rackauckas et al., UDE (arXiv 2001.04385) embed known equations and learn missing terms.
- All of these need **trajectories**. EVD has none (endpoint only). The PE pseudo-series are single-endpoint retentions at different durations from ~26 publications, which are better served by closed-form first-order/Weibull fits.
- **Consequence:** D11 stays DEFERRED (SSOT §209.17 already says "focused time-resolved systems only"). Gate it on a curated D-C dataset with ≥N independent time-resolved series (proposal: ≥20 series from ≥5 independent studies for one system). It must also beat the closed-form kinetic model under G15-HYB.

### Q9 Rollout error compounding — confidence HIGH
- Venkatraman, Hebert & Bagnell, AAAI 29 (2015), doi:10.1609/aaai.v29i1.9590 (DaD): one-step training lets errors compound and shift the input distribution. Treating multi-step prediction as imitation learning bounds the multi-step error.
- Lambert, Pister & Calandra (arXiv 2203.09637, preprint) find the system's own dynamics are the strongest factor in the shape of compounding error.
- SSOT §215.16–17 already specifies E(k), D(k) and trust horizon, and G15-11 requires true intermediate states.
- **Consequence:** quantitative rollout (R2/R3 in SSOT §212.44) cannot be validated on current data. One cheap, legitimate proxy is available: the **two-step composition test**. Predict RF(step1)·RF(step2), or chain the model, for USDA/PE multi-step rows (1,429 + 195), and compare against the observed composite endpoint. This tests composition and semigroup consistency (G15-8), not a trust horizon. Caveat: USDA multi-step factors may themselves be computed by multiplication (circularity UNVERIFIED; check the R6 documentation first). Qualitative rollout (R0/R1) belongs with Step 18/19 event-sourcing and Gold trajectories.

### Q10 Order and ladder — confidence MEDIUM-HIGH
The order is right in principle. It is the SSOT's own ladder, and DEL-2 confirms that simple sparse-structure models must be exhausted first. Three corrections:
1. **Steps 29 and 30 overlap with DEL-2, which already ran D0–D5 and D7.** Step 29 should be "freeze and re-run MP-1 V0 on the frozen DATA-EVIDENCE v1 (Step 15) with the corrected calibration protocol". It is not a new build.
2. **Step 31 is an ablation arm, not a new model family.** It can only be tested where numeric conditions exist (PE ~1.5k rows today) and should run inside the Step-30 harness. Data-wise it is closely coupled to Step 32.
3. **Steps 32–34 are DATA-GATED.** They depend on D-C/D-D acquisition (Steps 11/13/14 → 15) and overlap with Steps 24/26/27 (formula registry, the focused simulator and its validation). Step 32 must reuse the Step-26 kinetic model and parameters and not refit them independently. Step 34 is NEED_DATA for quantitative rollout.

## 3. Architecture recommendation

### 3.1 Recommended canonical ladder (single numbering = SSOT §209.17; retire the Master Plan AZ6 numbering)
| Rung | Model | Status/notes |
|---|---|---|
| D0 | persistence (RF=1, yield=1) | Mandatory null (SSOT §215.24). Wins or ties on several cold splits today |
| D1 | global mean (per target class) | |
| D2 | process / process-family mean | |
| D3 | nested empirical-Bayes shrinkage (existing) | Keep for continuity |
| **D3+** | **crossed random-effects / hierarchical Bayesian GLMM on logit- or log-retention: matrix⊂food group, process⊂family, target⊂class, source/study intercepts, plus selected interactions** | **NEW sub-rung (within Step 30)**. Expected strongest cold baseline. Gives the study variance component |
| D3-R | ridge / elastic-net on one-hot + side features | SSOT §209.6 already lists ridge; it is currently absent from the code |
| D4 | nearest compatible evidence (hierarchical fallback = MP-1 B-4) | Retrieval baseline, and the RAG "INTERPOLATE" rung |
| D5 | tuned GBDT (CatBoost or LightGBM; HistGB acceptable). Light tuning by **group-aware inner CV** | Per McElfresh/TabArena, tuning matters more than the family |
| D6 | TabPFN v2 (CPU, ≤10k rows, research licence recorded) | Comparator only. Context = training groups only |
| D7 | FM / tensor factorisation with side features (Macau/BPMF-like); biased MF retained as a sub-arm | Must beat D5/D6 *and D3+* on cold tests (G15-9) or be rejected |
| D8 | closed-form kinetics (first-order / Weibull / Arrhenius) per focused system, hierarchical log k | Data-gated (D-C) |
| D9 | sequential hybrid: frozen D8 + residual (GBDT or D3+ on residuals) | G15-HYB |
| D10/D11 | neural multi-output, FiLM, latent state, neural ODE/CDE/UDE | DEFERRED; trajectory gate |

Uncertainty layer for all rungs: group-disjoint split-conformal / CV+ calibrated on the **same grouping as the test split** (Dunn et al. repeated subsampling for hierarchical data), CQR for heteroscedastic targets, and empirical coverage labelled AH4.

### 3.2 Credible models for ~18k EVD rows across 3 source families
- Credible headline candidates: D0–D4, D3+, D5. D6 and D7 are comparators that must earn their place.
- The real n is the number of independent groups (USDA 171, Bognár 123, PE 287 matrix×process signatures; PE 125 publications; USDA effectively one source family whose factors are partly imputed (WORKLOG L117)). With ≈100–300 independent units per source, any model with more than a few hundred effective parameters per source will be variance-dominated on cold splits.
- **Model per source family, and test pooling explicitly.** Pooling USDA+Bognár on nutrients (17 shared nutrients, cross-source MAE 0.075–0.083) is a legitimate source-disjoint test (S-7) and the best available generalisation test for nutrients. PE (polyphenols) has no target overlap. Pool it only via target-class random effects, never as if it were the same target.
- Treat Bognár as a templated-factor source. Its in-sample wins (process-disjoint has only 7 signatures, so that split is degenerate) must never be a headline claim.

### 3.3 Rejected or deferred alternatives
| Alternative | Decision | Reason |
|---|---|---|
| Deep tabular (FT-Transformer, TabM, RealMLP) as a headline | REJECT for now | IID benchmarks give at best parity with GBDT; TabArena excludes grouped/shift data; n_eff ≈ hundreds per source; DEL-2 shows that even GBDT does not transfer cold |
| TabPFN as a headline or production model | REJECT (comparator only) | Random-split evidence only (Nature 2025); grouped-split claims are vendor-only (TabPFN-3.5); 2.5 weights are non-commercial |
| GP as a headline | DEFER | Needs a meaningful kernel over cold matrices; MTGP transfer cancels in block designs; acceptable as a small baseline on the numeric T/t PE subset |
| Set/graph neural transition models | DEFER to D10 | No evidence they beat D3+/D5 at this n; SSOT forbids skipping D0–D7 |
| Neural ODE/CDE/UDE | DEFER (trajectory gate) | No trajectories in EVD |
| End-to-end PINN on retention aggregates | REJECT | No governing PDE/state for endpoint aggregates; SSOT §201.12 limits constraints to valid subsets |
| Joint (non-sequential) hybrid fitting | REJECT as the first hybrid | SSOT §211.45: sequential fitting protects interpretability; identifiability unknown |
| Long-horizon quantitative rollout | REJECT now | G15-11 requires true intermediate states (none); SSOT §215.37 |

## 4. Per-step changes (Steps 29–34). Reconstructed scope; card text is unavailable.

### Step 29 TRANSITION_BOOTSTRAP_V0 — KEEP + CLARIFY (CPU; MEDIUM-HIGH)
- **Input:** DATA-EVIDENCE v1 freeze (Step 15) EVD snapshot hash; COND (Step 07 normaliser); STUDY/lineage (Step 08) for independence groups; the MP-1 contract.
- **Do:** re-run B-0..B-4, plus B-5 = D5 only after B-0..B-4 are reported. Use the frozen D-card IDs mapped 1:1 (B-0=D0, B-1=D1, B-2=D3 matrix-arm, B-3=D2, B-4=D4, B-5=D5). Publish the mapping table.
- **Add:**
  - (a) a calibration split that is group-disjoint in the same family as each test split;
  - (b) n_independent_groups beside every metric (already in the contract);
  - (c) source/basis shortcut controls (contract §6);
  - (d) a **label-noise ceiling**: cross-source same-cell disagreement (USDA↔Bognár MAE ≈0.075–0.083; FDC↔R6 0.167) reported as the irreducible-error floor. No model claim may beat this floor by more than its CI without explanation;
  - (e) a USDA imputed-factor flag. Rows imputed from similar foods stay in the donor fold (contract §4) and need a field marking them (see §5).
- **Gate:** contract §6 unchanged. Pre-registered, no post-hoc weakening.
- **Output:** V0 report + EXP card + frozen split manifest (hashes).
- **Fail action:** report non-cold (already the case for USDA/PE); proceed to Step 30 only as a "can structure help cold?" study, not as escalation on V0.

### Step 30 Strong tabular / sparsity bake-off — MODIFY (CPU; MEDIUM)
- **Add rungs:** D3+ crossed random-effects/hierarchical; D3-R ridge/elastic-net; D5 tuned (CatBoost/LightGBM, group-aware inner CV with a small fixed budget); D6 TabPFN v2 on CPU (licence row in the registry); D7 upgraded to FM/tensor with side features (FDC raw-food nutrient vector, food group, process family, medium, water contact, target class).
- **Splits:** S-2..S-7 as in MP-1. Headline = min over cold splits. S-6 study-disjoint for PE (125 publications) and any Step-11/12 sources with study lineage.
- **Metrics:**
  - censor-aware MAE with a Tobit/interval likelihood option (D3+ can model censoring directly instead of the "lower bound 0.975" assumption in DEL-2);
  - log-scale MAE;
  - paired grouped bootstrap vs D0 and vs the best deterministic rung;
  - conformal coverage/width per split with group-disjoint calibration;
  - IPW sensitivity;
  - a risk–coverage curve (feeds G15-7).
- **Gates:** G15-2 (D0–D6 on all headline splits before any D7 claim); G15-9 (D7 vs D5/D6 **and D3+**); G15-6 study-disjoint calibration on PE.
- **Negative controls:**
  - target-shuffled within source;
  - matrix-ID-only model (memorisation probe);
  - a source-family-only model (shortcut probe).
- **Fail action:** if no rung beats D0/D3 with paired LB>0 on any cold split, freeze "retrieve/lookup + hierarchical fallback" (D4/D3+) as the production transition estimator for Step 36. That is a valid outcome and does not trigger escalation.

### Step 31 Physics / condition features — MODIFY (ablation inside the Step-30 harness; CPU; MEDIUM)
- **Inputs:** COND numeric T/time (PE 1,561 rows today; USDA T = 0 rows; Bognár time = 0 rows), medium, water contact, pressure/power where present, SSOT L15834 feature list.
- **Feature families:**
  - log t;
  - 1/T(K);
  - Arrhenius exposure integrals at 2–3 representative Ea **declared before outcome inspection**;
  - degree of water contact / leaching proxy (water:food ratio, cut surface area — currently UNKNOWN, see §5);
  - dry vs wet heat;
  - drippings or cooking water included;
  - basis (true vs apparent retention; FW/DW);
  - yield.
- **Experiments:**
  - A5 "+physics" ablation (SSOT L22478) on D3+/D5, restricted to rows where features are MEASURED, with an identical row set across arms;
  - a missing-indicator arm (UNKNOWN ≠ 0, so features are never imputed as 0);
  - **condition-OOD split** = held-out temperature/time bins within PE (G15-5);
  - a monotonicity-constrained GBDT (degradation-only targets, SSOT §201.12) as the "physics-constraint" arm.
- **Gate:** G15-3 (process signal) and the precondition of G15-5. Report the effect size with CI, not only a point gain.
- **Look-ahead:** the result decides whether Step 32 kinetic fits add anything beyond the features.

### Step 32 Focused kinetics — KEEP but NEED_DATA; merge parameters with Steps 24/26 (CPU; MEDIUM-LOW)
- **Data now:** PE pseudo-series give ~152 retention-vs-time series from 26 publications (fixed T). Only 3 publications have ≥3 temperatures, so the Arrhenius Ea is not identifiable for most systems from EVD. Real D-C datasets must come from Steps 11/13/14 (ES-1.2 census: kinetic sources = SOURCE_GAP; DS-043/044/045 literature routes).
- **Architecture:**
  - D8 = closed-form zero/first-order/Weibull per series;
  - hierarchical log k (SSOT §211.21) with study random effects (Karamcheti 2025 template);
  - profile-likelihood or bootstrap intervals (G15-4);
  - model discrimination by AIC/WAIC, plus a held-out time point in each series as validation.
- **Must reuse** the Step-24 registry IDs and the Step-26 simulator's kinetic law and parameters (do not duplicate). Step 32 generalises across series and studies; Step 26 is one validated system.
- **Gate:** G15-4. **Fail:** RESEARCH_ONLY for that system; the transition route stays D3+/D4.

### Step 33 Mechanistic vs ML vs hybrid — KEEP, gated on Step 32 PASS (CPU; MEDIUM)
- Three arms on identical rows and splits: D8 alone, best non-kinetic ML (from Step 30/31), and D9 sequential hybrid (frozen D8 → residual model trained on grouped folds, SSOT §211.45).
- **Splits:** condition-OOD (held-out T and longer t: extrapolation in time is the hybrid's claimed advantage) plus study-disjoint.
- **Metrics:**
  - MAE;
  - coverage and width;
  - constraint-violation rate (non-negativity, monotone degradation);
  - extrapolation error vs horizon.
- **Gate:** G15-HYB and G15-5. The hybrid must beat **both** arms with paired LB>0 or show a separately demonstrated physical-consistency advantage.
- **Fail:** keep the simpler winner (law: complexity must beat simple baselines).

### Step 34 Short rollout — MODIFY to split into 34a/34b; 34b NEED_DATA (CPU)
- **34a (feasible now):** two-step **composition test** on USDA (1,429) and PE (195) multi-step composite rows. Chained one-step predictions (or a multiplicative composition of the predicted RF) are compared to the observed composite endpoint.
  - Metrics: composite MAE, D(2)=E(2)/E(1) proxy, constraint violations, coverage of propagated intervals (Monte Carlo through the conformal/posterior).
  - First, check whether the R6 multi-step factors are multiplicative derivations (circularity).
- **34b (data-gated):** true trust-horizon evaluation E(1..K) on D-C/D-D series with intermediate states (from Step 11/13 acquisition, or Step 19 Gold state trajectories for qualitative R0/R1).
  - Require scheduled-sampling/DaD-style training ablations only if a learned multi-step model is used.
  - Gate G15-11: no rollout claim without true intermediate states.
- Rollout abstention (SSOT §212.22) ties into the Step 36 cascade: when the evidence distance or interval width exceeds a threshold, the answer becomes QUALITATIVE/ASK/ABSTAIN.

## 5. Look-ahead requirements for earlier steps (backward propagation)
| Earlier step | Requirement from Steps 29–34 |
|---|---|
| 07 Condition normalisation | Keep numeric T and time *per row* with location (core/surface/medium), ranges as intervals, and an explicit UNKNOWN status. Add fields **water:food ratio, cut size/surface area, lid/covered, medium volume, pre-treatment (blanch), held-out-time bins**. Moisture and pH are currently UNKNOWN on all rows, so Step 31 cannot use aw/moisture gating without new acquisition |
| 08 Source lineage | Study/publication IDs for every row. **Derivation flags**: USDA "calculated/imputed from similar food" and Bognár "estimated" (grey shading lost; reports/del2/cross_source_v1.md). Shared-yield-source links across PE rows. Duplicate-measurement links across sources. Without these, S-6/S-7 and G15-6 are not computable |
| 09 Extraction/verification | Table extraction must capture **per-time-point values** (series), replicates/SD/n, and before/after basis (FW/DW, true/apparent). Endpoint-only extraction would starve Steps 32–34 |
| 10–14 Acquisition | Prioritise D-C systems with ≥3 temperatures × ≥4 time points from ≥5 independent studies, for 1–3 focused systems aligned with the Step-26 simulator choice (SSOT §224.4 design-for-identifiability). Prioritise multi-step sequences with intermediate measurements (e.g. blanch→freeze→cook) for 34b. Prioritise nutrient sources overlapping USDA/Bognár cells for source-disjoint tests |
| 15 DATA-EVIDENCE v1 freeze | Freeze the split manifests (S-1..S-7 plus condition-OOD bins) and calibration sets *with* the data snapshot. Freeze the propensity features before outcome inspection (Master Plan AI6 L3108–3111) |
| 16–20 Procedure/state | Event schema must carry process parameters in the same COND vocabulary (T, t, medium, ratio) so the transition model is callable from recipe events (Step 22/36). Step 19 Gold trajectories should record the *observable intermediate states* needed for qualitative rollout (R0/R1) |
| 24 Formula/model registry | Entries need the fields Steps 32/33 read: model_id, law (order/Weibull), parameters with units and uncertainty, condition scope (T, t, matrix), identifiability status, calibration/validation source IDs |
| 26–28 Simulation | Step 28 E7 synthetic prior may enter Step 30/33 training only in a ratio-sweep ablation (G15-10). Never in test or calibration |

Schema fields to add to the transition-event table (SSOT §216.1 L22733–22799) / EVD derived rows. Proposed; verify against §216.1 before adding:
`independence_group_id`, `study_component_id`, `derivation_status {MEASURED, CALCULATED, IMPUTED_FROM_SIMILAR, ESTIMATED_TEMPLATE}`, `donor_row_ids`, `basis {TRUE_RETENTION, APPARENT_RETENTION}`, `weight_basis {FW, DW}`, `censor_type/interval`, `time_point_index`, `series_id`, `replicates_n`, `sd`, `split_membership{S1..S7, cond_ood}`, `calibration_membership`.

## 6. Residual uncertainty, and pilot vs reading
- Peer-reviewed evidence that any tabular foundation model improves *grouped/cold* regression is missing (vendor-only claim: TabPFN-3.5). Whether D3+ beats D4/D0 on cold splits, and whether FM side features rescue D7, are both unanswerable from literature.
- **A pilot is cheaper than more reading.** The DEL-2 harness already exists (615 lines, USDA run 23 s on CPU). A D3+ and D6 extension with group-disjoint calibration is a few hours of CPU and settles Step 30's architecture. Constraint: this is an *implementation* action, so it needs authorisation after the plan review and must run on the frozen Step-15 snapshot to avoid touching locked splits. It is NOT done here.
- **Unverified items:**
  - USDA multi-step factor circularity;
  - the exact count of USDA imputed rows;
  - the Bognár "estimated" flags;
  - contents of the Purlis / Khan / van Boekel 2021 reviews (metadata only);
  - the TabPFN v2 (2.0) weights licence terms (only 2.5 checked).
- **Stop rule:** satisfied (§8 rules 1, 2 and 5). The evidence is enough to choose the ladder. Further searches on TFMs under shift produced only vendor or preprint material. An empirical pilot is now more informative.
