# r_simulator_vv — First focused deterministic simulator and its V&V (spine steps 26, 27, 28, 32)

Researcher: r_simulator_vv · Date: 2026-10-22 · Mode: PLAN-RESEARCH only (no implementation, no downloads of datasets, no training).
Repo (read-only): `/home/manjot23309/kush_work/culinarystate`. SSOT = `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (cited "SSOT Lnnnn"). Master Plan v4.0 = `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (cited "MP Lnnn").
The 36-step plan with step cards (`CulinaryState Master Execution Plan v1`) is NOT available. Step 26/27/28/32 content below is reconstructed from the brief's step titles (brief §9) and the SSOT/MP. No text is attributed to the missing plan.

Verification tags: [V] = I opened the primary page, the Crossref/Europe PMC metadata, or the PDF. [V-meta] = bibliographic metadata verified, but the claim comes from an abstract or repository record and not the full text. [UNVERIFIED] = search-snippet level only.

---

## 0. Internal context established (repo and SSOT, read-only)

**SSOT anchors**
- §223 three synthetic tiers, SSOT L24064–24268. Contents:
  - S-MECH (L24078). Its examples include "first-order Arrhenius nutrient/pigment degradation" and "two-compartment leaching".
  - Allowed uses (L24130s).
  - Forbidden claim (§223.5).
  - Ratio sweep (§223.10).
  - TSTR/TRTR (§223.11).
  - Hard prohibition: "synthetic/imputed target rows never enter final test or calibration sets" (§223.14).
  - Model-collapse / simulator-gap risks (§223.15).
- Kinetic data hierarchy K0–K4, §210.28 (SSOT L19089–19110). K0 is one before/after endpoint and "supports retention/direction, not detailed kinetics". K2 (several times × several temperatures) is needed for Arrhenius.
- Kinetic evidence schema §210.29 (L19111). Kinetic-experiment table §216.2 (L22800–22824).
- §210.29A (L19137–19163) `[SOURCE-REPORTED]` names **acrylamide/potato frying** and **glucose/glycine Maillard** as the two focused anchor families. It recommends the reference-temperature Arrhenius form and "≥3, preferably ≥4 temperatures with ≥4–5 time points" as a pilot planning rule.
- CV modes §211.25 (L19529): held-out time, temperature, matrix and study. Kinetic evaluation §215.14 (L22119). Kinetic ablation K0–K6 §215.57 (L22486–22501).
- M3/M4 milestones §226.5–226.6 (L24541–24559). Contribution C4 "simulator-pretrained / real-finetuned" §227.5 (L24700).
- Synthetic rollout benchmark §212.46 (L20441). Multi-fidelity §201.13 (L16763).
- §274 "Simulator pretraining — default is NOT YET" (L44339–44394). This is an L13E (cultural-evolution simulator) section, but its controls carry over:
  - a randomized-simulator control (§274.2);
  - real held-out promotion (§274.3);
  - "use simulators first for validation/stress testing; treat pretraining as a gated experiment" (§274.5).

**Master Plan v4.0**
- E1–E7 tiers (MP L587–595): "Only E1–E4 can enter evaluation sets. E6–E7 are priors or stress tests only."
- SX-06-04 kinetic table for acrylamide, Maillard, vitamin C, anthocyanin and chlorophyll (MP L363). SX-06-05 pH effects (MP L364).
- B13: SX-13-02 kinetic fits with profile likelihood (MP L477) and SX-13-05 simulator-pretraining ablation (MP L480).
- I3 worked example "boiling vegetables: leaching vs destruction of water-soluble vitamins … chlorophyll → pheophytin" (MP L614).
- Z1 open questions (MP L2195+), Q4: "how often do reported retention values conflate degradation, leaching and concentration-by-water-loss?"

**Repo contract**
- `docs/simulator_data_contract.md` (S116): `source_class` includes KINETIC, MODEL_GENERATED and SYNTHETIC. STRUCTURAL_RECIPE may not carry a magnitude. Enforced by `TransitionInput` (tests/unit/test_external_data_policy.py).
- `reports/h_state/transition_bootstrap_v0_contract.md` L7: E1–E4 only, no simulated rows.
- DECISIONS.md (ES-1.2, L119): "structured open sources for mechanism/kinetic/physical time series not found (SOURCE_GAP for 13 of 16 priority-cell rows; literature route available)".
- DECISIONS.md L136: RXN/KINETIC/SIM ledgers "not created (BLOCKED_FUTURE_STEP)".
- No simulator code exists in `src/` (grep for simulat/arrhenius/kinetic finds only evidence/ledger code).

**Read-only diagnostic of `ledgers/data/EVD.jsonl` + `COND.jsonl`** (stdlib Python; counts only, nothing sent externally)

| Target | Source | Rows | Duration status | Temperature status |
|---|---|---|---|---|
| vitamin C | USDA-RETN-R6 | 584 | 528 UNKNOWN, 36 RANGE, 20 MEASURED | all UNKNOWN |
| vitamin C | BOGNAR-2002 | 612 | all UNKNOWN | 340 UNKNOWN, 260 RANGE, 12 MEASURED |
| folate | USDA 1,752 / Bognár 748 | — | (K0) | (K0) |
| thiamin | USDA 584 | — | (K0) | (K0) |
| carotene | USDA 1,168 / Bognár 748 | — | (K0) | (K0) |
| chlorophyll, acrylamide, HMF, starch | — | **0** | — | — |

- All the vitamin rows are `DATABASE_AGGREGATE`, tier E3, with `study_id_status` NOT_IDENTIFIABLE (e.g. EVD-000001).
- Phenol-Explorer 3.6 is the only family with MEASURED time and temperature (5,504 rows with both).
  - Grouping by (study, food, compound, process steps, medium, temperature) gives 152 groups with ≥3 distinct times at one temperature (K1-like), from 26 studies.
  - These are mostly storage: store-ambient 83, refrigerated 42, pasteurize 8, frozen 8, **boil 5**.
  - Only 8 groups (from 2 studies) have ≥3 temperatures × ≥3 times (K2-like).
  - None concern vitamins or pigments.
- **Consequence:** the repo holds no trajectory evidence that can calibrate or validate any candidate cooking simulator. Every candidate needs K1/K2 series acquired through Steps 10–14 (the literature route).

---

## 1. Questions

- **Q1.** Which candidate system should be the FIRST focused deterministic simulator? Candidates: ascorbic acid; chlorophyll→pheophytin; POD/PPO inactivation; starch gelatinisation; acrylamide; Maillard markers (HMF/furosine); thiamine/folate; carotenoid isomerisation. Criteria: established equation, parameter availability across matrices, real held-out validation data (trajectories vs endpoints), confounders, downstream value.
- **Q2.** Is the repo's USDA R6 / Bognár / Phenol-Explorer evidence usable for calibration or held-out validation?
- **Q3.** Which V&V framework should Steps 26–27 follow (ASME V&V 10/20/40, NASA-STD-7009B, Oberkampf & Roy), and how should the domain of validity be represented?
- **Q4.** How should uncertainty be propagated (parameter, input, model-form, measurement)?
- **Q5.** When must simulation be prohibited?
- **Q6.** Is the "E7 synthetic prior" practice (SSOT §223) sound against the literature on simulation-based priors and synthetic data, and what controls are missing?
- **Q7.** How should Step 32 "Focused kinetics" relate to Steps 26–28, given that a simulator cannot be calibrated without kinetic fitting?

---

## 2. Findings per question

### Q1. Candidate comparison

| Candidate | Established equation | Parameter availability / transfer | Real validation data | Main confounders | Downstream value for CulinaryState | Verdict |
|---|---|---|---|---|---|---|
| **Ascorbic acid (AA) in vegetables, water/steam heating 60–100 °C** | Primary model: first-order, sometimes zero-order or Weibull. Secondary: Arrhenius (reference-T form), D–z or Peleg's exponential. Aerobic (AA→DHA→DKG) and anaerobic pathways [V Giannakourou & Taoukis 2021, pp. 5, 14–17; Peleg et al. 2018 CRFSN, metadata V]. Blanching: watercress 82.5–92.5 °C was first-order, Ea ≈150 ± 43 kJ/mol [V-meta Cruz et al. 2008]. | **Many studies, but parameters are not transferable.** Reported Ea spans ~12 kJ/mol (mango juice) to ~120–132 kJ/mol (frozen spinach). There are Arrhenius "breaks" and deviations under aerobic conditions. The review says the multiple approaches "make a comparison between different works almost impossible" [V, pp. 15–19]. Matrix-specific calibration is mandatory. | Largest K1/K2 literature among candidates (many independent groups). The repo holds K0 endpoints only (USDA/Bognár). | **Leaching vs degradation** (major in boiling, absent in steam or sealed heating). AA vs total vitamin C (AA+DHA) measurement basis. Wet vs dry basis and yield. O2/headspace. Ascorbate oxidase active before inactivation. Metal ions. Piece geometry and heat-transfer lag. | High: the MP I3 worked example (MP L614) and Z1-Q4 (MP L2195+). Connects to 1,196 existing E3 vitamin C rows. Inputs (time, medium, T≈100 °C) are partly recoverable from recipes. Nutrition claim → low decision consequence. | **RECOMMENDED first simulator**, scoped (see §3). |
| **Chlorophyll → pheophytin (green colour)** | First-order plus Arrhenius. Pea purée 70–90 °C: chl a 19.5, chl b 17.1, greenness (−a*) 18.2 kcal/mol [V Steet & Tong 1996]. Pyropheophytin dominates in heat-processed spinach [V-meta Schwartz & von Elbe 1983]. Strong pH dependence [V-meta Koca et al. 2007]. | Ea fairly **consistent** across studies (~17–20 kcal/mol in peas; 15–22.8 kcal/mol in spinach purée per a snippet [UNVERIFIED]). Rate is strongly pH-gated. | Fewer groups than AA; many studies use purées. **Zero rows in repo.** | **No leaching** (lipophilic pigment), which removes the biggest AA confound. However: tissue pH shifts (organic-acid release), colour vs HPLC basis, Zn/Cu complexes, pyropheophytin above 100 °C, purée → whole-piece heat-transfer gap. | High: colour is an observable kitchen state ("overcooked greens turn olive"). Tests pH applicability gating (pH usually UNKNOWN in recipes → abstain). | **Pre-registered FALLBACK / second simulator.** Possibly scientifically cleaner; decide with the census in §6. |
| POD / PPO thermal inactivation | First-order, biphasic (labile + resistant isozymes), or fractional conversion. POD in carrot and potato is first-order but has a **curved Arrhenius plot**. PME has labile and resistant forms [V-meta Anthon & Barrett 2002]. Biphasic isozyme method [V-meta Ling & Lund 1978]. | Abundant T × t residual-activity curves. Parameters are matrix- and isozyme-specific. | Good trajectories in the literature; none in repo. | Isozyme multiplicity, extraction method, regeneration. | Low–moderate: the output is "blanching adequacy", not a consumer-facing state. PPO browning is formation chemistry, which differs. | Good **V&V testbed** but low value. Keep as an optional Step-32 extension. |
| Starch gelatinisation | First-order or Avrami from DSC; two Ea regimes; incomplete below ~67.5 °C in potato [UNVERIFIED snippet, Pravisani et al. 1985]. Non-isothermal DSC: different models fit equally well but give very different Ea [UNVERIFIED snippet, Spigno & De Faveri 2004]. Water-limited behaviour (Lund & Lorenz 1984, metadata via citing paper, UNVERIFIED). | Strongly water- and heating-rate-dependent; model form is ambiguous. | In-situ cooking degree-of-gelatinisation trajectories are rare. Zero in repo. | Coupled water uptake and heat transfer; measurement proxy (DSC vs rheology vs birefringence). | High conceptually (texture), but data-starved. | **Reject as first.** Possible later texture-module research. |
| Acrylamide formation/elimination | Multiresponse model in glucose–asparagine at 120–200 °C, pH 6.8: acrylamide is an intermediate that also degrades [V-meta Knol et al. 2005]. In crisps, an **empirical** logistic-exponential model fits best; "precision of the parameter estimates for the degradation of acrylamide was still problematic"; the formation parameter tracks reducing sugar [V-meta Knol et al. 2009]. | Model-system parameters do not transfer to foods without precursor data (reducing sugars, asparagine by cultivar and storage). | Food data are mostly **endpoints at final moisture** (e.g. Pedreschi frying 150–190 °C [UNVERIFIED snippet]). Zero in repo. | Surface T/moisture coupling (heat and mass transfer during frying), precursor variability, oil uptake. | Safety-relevant → **high decision consequence** (V&V 40 model risk). | **Reject as first.** SSOT §210.29A anchor kept for Step 32 extension as RESEARCH_ONLY. |
| Maillard markers (HMF, furosine) | Multiresponse glucose/glycine network [V-meta Martins & van Boekel 2005]. Kinetic limits in foods [V van Boekel 2008 CRFSFS]. | Model-system parameters; food transfer weak; matrix-specific markers (HMF in bakery, furosine in dairy/pasta). | Sparse in cooking contexts. Zero in repo. | Network non-identifiability, aw/pH, precursors. | Moderate. | Reject as first; Step 32 extension only. |
| Folate / thiamine | Folate: thermal degradation **not first-order** and non-monotonic. Spinach losses are mainly diffusion; green beans mainly thermal. Diffusivities 7.4e-12 vs 5.8e-10 m²/s; vitamer shifts [V-meta Delchier et al. 2014]. | Vitamer-specific; complex analytics. | Folate is K0-rich in repo (2,500 rows), but there are no trajectories. | Leaching dominant and matrix-dependent; vitamer interconversion. | Moderate. | Reject as first. Folate is good evidence that leaching vs degradation must be explicit in any water-soluble vitamin simulator. |
| Carotenoid degradation / isomerisation | Fractional-conversion model (plateau). β-carotene in an oil/carrot emulsion at 85–130 °C: degradation Ea ≈45 kJ/mol; isomerisation Ea 70.5 / 75 kJ/mol [V-meta Knockaert et al. 2012; values UNVERIFIED snippet]. | Few independent groups (mostly KU Leuven). Oil presence changes behaviour. | Low study independence. Repo: carotene K0 endpoints. | Oil phase, extractability increases on heating (apparent increases). | Moderate. | Reject as first. Optional later. |

**Conclusion (confidence MEDIUM–HIGH).** AA in vegetables under water or steam heating is the best-supported first simulator. It has the largest independent trajectory literature, an established equation family, an existing E3 consumer in the repo, a plan-declared scientific question (leaching vs destruction), and low decision consequence.

Its main weakness is well documented: parameters are **not transferable across matrices** and leaching must be separated from degradation. The simulator must therefore be matrix-scoped and two-pathway, and must output intervals. Chlorophyll is the pre-registered fallback because it has no leaching and more consistent Ea. The choice between them should be fixed by an extractability census (§6), not by more reading.

### Q2. Usability of repo evidence (HIGH confidence; from the diagnostic in §0)

- **USDA R6 and Bognár vitamin C rows** are K0 database aggregates. Duration and temperature are almost always UNKNOWN, and the rows have no study identity.
  - They **cannot** calibrate k or Ea.
  - They **cannot** serve as held-out validation, because conditions are unknown, so predictions would need imputed inputs. Imputed inputs used for validation would break the spirit of SSOT §223.14 / MP L595.
  - They also **cannot** be split study-disjointly.
  - Permitted use: a coarse, explicitly labelled **plausibility envelope**, i.e. the simulator's predicted retention at the process's reported duration range should overlap E3 retention ranges. This is reported as a sanity check and never as validation.
  - Note DECISIONS L116: reported retention may be "apparent" (yield-corrected). The comparison must use the same basis.
- **Phenol-Explorer** has real K1 series, but for polyphenols and mostly storage. Only 5 boil groups and 8 K2-like groups exist, from 2 studies. This is not enough for a polyphenol cooking simulator. Polyphenols in boiling also show extractability-driven apparent increases, so they are not a good first target.

### Q3. V&V framework

- **NASA-STD-7009B** (approved 2024-03-05, supersedes 7009A w/Change 1) [V primary PDF]. Its definitions fit our needs:
  - **Domain of Validation**: "region enclosing all sets of M&S inputs for which the M&S' responses compare favorably with the referent".
  - **Domain of Verification**.
  - **M&S Limits** ("M&S can be used to extrapolate outside the domains of V&V, but within the M&S limits").
  - Validation-factor levels 0–4 (Table 9). "Favorable comparison requires, at a minimum, some overlap between the uncertainty intervals around the means." Each model output may have its own domain of validation.
  - Use-assessment levels (Table 15):
    - Level 4: proposed use within domain of validation;
    - Level 3: within domain of verification;
    - Level 2: within M&S limits.
  - Credibility is split into M&S Capability factors (data pedigree, verification, validation, technical review, process management) and M&S Results factors (use assessment, input pedigree, uncertainty characterisation, results robustness, …).
  - **Adopt these definitions and the level scales directly** as registry/SIM fields.
- **ASME V&V 40-2018** (via FDA guidance, issued 2023-11-17 [V primary PDF]).
  - Context of use (COU), model risk = f(model influence, decision consequence), credibility goals, and "applicability" ("the relevance of the validation activities to support the use of the computational model for a context of use").
  - The FDA notes that V&V 40 "assume[s] the ability to perform well-controlled bench testing". Our referent is **literature data**, i.e. less controlled. The FDA guidance explicitly allows "non-traditional" evidence categories.
  - Adopt: COU statement + model-risk grading per output.
  - The AA-retention COU (informational nutrition estimate inside a RAG answer, model influence medium, consequence low) → **low–medium risk**.
  - An acrylamide COU (safety) would be high risk, which is another reason it should not come first.
- **ASME V&V 20-2009** (CFD and heat transfer) [V-meta, Hills 2010 Sandia overview].
  - Validation is quantified at validation points via comparison error E = S − D and a validation uncertainty combining numerical, input and experimental uncertainty. It is not a pass/fail exercise.
  - "Interpolation or extrapolation … is beyond the scope of this Standard".
  - Use its E-vs-u_val formulation per validation point.
  - The 2025 multivariate successor (VVUQ 20.1) is mentioned only by a snippet [UNVERIFIED].
- **ASME V&V 10** (solid mechanics): not domain-relevant beyond general vocabulary; not opened.
- **Oberkampf & Roy** (Cambridge UP 2010 [V metadata]; Roy & Oberkampf 2011 CMAME 200:2131 [V-meta abstract]).
  - Treat aleatory uncertainty as distributions and epistemic uncertainty as intervals.
  - Convert numerical error into epistemic uncertainty.
  - Estimate **model-form uncertainty from validation comparisons** and **extrapolate** it to application conditions.
  - A 2nd edition (2025) is listed on a Cambridge page that I could not open [UNVERIFIED].
- **Food-specific practice** [V-meta Dolan & Mishra 2013 Annu Rev Food Sci Technol 4:401]: "the forward results can be no better than the accuracy of the parameters". Use scaled sensitivity coefficients for identifiability, sequential estimation and optimal experimental design. van Boekel 2008 [V-meta] sets the limits of applying elementary kinetics to complex food matrices.
- **Kennedy & O'Hagan 2001** (JRSS-B 63:425 [V metadata]): Bayesian calibration with an explicit model-discrepancy term. This is the statistical basis for Step 33's "hybrid" = mechanistic + learned discrepancy.

**Synthesis (HIGH confidence on structure).** Use a NASA-7009B vocabulary + V&V 40 COU/risk + V&V 20 point comparisons + Oberkampf–Roy model-form extrapolation stack. No food-specific V&V standard exists. The ES-1.2 census and my search found no open structured kinetic database for food-quality chemistry analogous to ComBase (consistent with DECISIONS L119).

### Q4. Uncertainty propagation (HIGH on the method, MEDIUM on magnitudes)

Sources of uncertainty:
1. **Parameter:** joint posterior of (ln k_ref, Ea) in the **reference-temperature parameterisation** (SSOT §210.29A, L19137+; also Giannakourou & Taoukis eq. 2 [V]). This reduces the k–Ea correlation. One-step global fitting gives narrower and more honest intervals than two-step fitting [V Giannakourou & Taoukis 2021 §7].
2. **Hierarchy:** matrix-level random effects plus study offsets (SSOT §211.21 hierarchical kinetics, L19476). The literature spread of Ea (12–150 kJ/mol) argues for matrix-specific parameters with partial pooling only within a matrix class.
3. **Input:** product core temperature vs bath temperature (heat-transfer lag for pieces), time, water:food ratio, piece size, initial concentration. Monte Carlo over input intervals; UNKNOWN inputs are never silently defaulted.
4. **Model-form:** from the validation residuals (Roy & Oberkampf 2011) or a K–O'H discrepancy term.
5. **Measurement:** study-level analytical error (titration vs HPLC; AA vs AA+DHA).

Propagation: plain Monte Carlo (10³–10⁴ draws; trivial on CPU). Output predictive intervals for ln(C/C0) at each requested time.

Precedent for stochastic AA kinetics:
- Giannakourou & Taoukis 2021 describe Monte Carlo / Bayesian "stochastic" kinetics, and Rigaux et al. 2016 a probabilistic canned-green-bean vitamin C model (cited in the review [V via review text, primary UNVERIFIED]).

### Q5. When simulation must be prohibited (HIGH confidence; follows from NASA-7009B Table 15 and SSOT laws)

Return SIM_PROHIBITED, and fall back to RETRIEVE / QUALITATIVE / ABSTAIN, when any of the following holds:
- (a) Step-23 mechanism applicability is UNKNOWN or NOT_APPLICABLE, or a competing mechanism dominates. Examples: ascorbate-oxidase-driven loss in cut or raw tissue below the inactivation temperature; dry-heat roasting or frying where moisture loss dominates.
- (b) A required input is UNKNOWN with no defensible interval (e.g. duration unknown).
- (c) The request lies outside M&S limits: T > 100 °C at ambient pressure for water systems, oil media, microwave without measured product temperature.
- (d) The matrix has no calibrated analogue in the parameter registry (Step 25 returns no compatible set).
- (e) The output would be used as an evaluation or calibration target (§223.14) or as evidence (simulation ≠ measured evidence law).
- (f) The claim is safety-critical (none for AA).

Outputs inside M&S limits but outside the domain of validation are tagged EXTRAPOLATED. They may only be shown with that label and widened intervals, or suppressed when the COU risk requires it.

### Q6. E7 synthetic prior (SSOT §223) against the literature (MEDIUM–HIGH)

What the literature supports:
- **PFNs / TabPFN.** A transformer trained on samples from a prior approximates Bayesian inference [V Müller et al. ICLR 2022]. TabPFN is trained "on millions of synthetic datasets" and is strongest up to ~10,000 samples [V abstract via Europe PMC; size figure V-meta via abstract/press]. **But** this is a *generic* function-family prior used for in-context inference. It is not a mechanistic food simulator, so SSOT §225.7's "synthetic-prior foundation-model analogy" is an analogy, not evidence that S-MECH pretraining will help.
- **Simulator pretraining then real fine-tuning** has precedent in process-guided deep learning for lake temperature [V-meta Read et al. 2019 WRR]. PGDL beat both process-based and pure-DL models, but **only when the pretraining data spanned more variability than the training period**. This directly supports SSOT §223.3 domain randomisation and implies a gate: E7 must cover a wider condition range than the real training set.
- **Theory-guided data science** frames the hybrid approaches [V Karpatne et al. 2017 TKDE].
- **TSTR** origin [V Esteban et al. 2017 arXiv] supports SSOT §223.11.
- **Model collapse** [V Shumailov et al. 2024 Nature 631:755]: indiscriminate training on generated data loses the distribution tails. This applies mainly to statistical/LLM generators (the SSOT §223.9 LOW priority is justified). For S-MECH the analogous risk is that *simulator assumptions replace real tails*. That is why real-only evaluation (§223.14–15) is essential.
- **SBI** [V Cranmer et al. 2020 PNAS] and simulation-based calibration (SSOT §273.6) are appropriate for identifiability and recovery experiments.

Gaps in §223 for L15 (to add in Steps 28 and 33):
1. **Randomized / wrong-physics simulator control** at matched data volume. SSOT §274.2 requires this for L13E only; §223 lacks it for L15.
2. **Real-data learning-curve sweep** (value of the prior vs real-n), in addition to the synthetic ratio sweep (§223.10).
3. **Calibration-leakage control.** The studies used to calibrate the simulator must be a subset of the downstream *training* studies. Otherwise E7 smuggles test-study information into Step 30/33 models.
4. **Provenance fields on every E7 row:** sim_model_id, sim_version, validation_status, param_draw_seed, domain_flag (IN_VALIDATION / EXTRAPOLATED / RANDOMIZED_BEYOND_LIMITS), randomisation spec.
5. **Generation only from a simulator version that passed Step 27.** If Step 27 FAILS, E7 is restricted to identifiability and method-development uses (§223.4). No pretraining claims.

### Q7. Step 32 vs Steps 26–28 (HIGH confidence on the dependency)

Calibrating the Step-26 simulator *is* a focused kinetic fit (K1/K2 series → k_ref, Ea, identifiability). The spine, however, places Step 32 "Focused kinetics" after Steps 26–28.

The fitting/identifiability machinery (SSOT §210.29, §211.9–211.10 two-stage/global Arrhenius, §211.21 hierarchical, §216.2 table; MP SX-13-02) is therefore a **hidden prerequisite** of Step 26. It belongs in Step 26 (as 26a), with Step 24/25 registry inputs.

Step 32 should become the **K0–K6 kinetic ablation and comparison** step (SSOT §215.57) on transition targets, run against Step 30 tabular baselines. It should also extend to a second system (chlorophyll, or acrylamide/Maillard as RESEARCH_ONLY anchors per §210.29A) only if the first passed Step 27.

---

## 3. Architecture recommendation

### 3.1 Recommended: SIM-AA-1 "ascorbic acid retention in vegetable tissue under water-immersion / steam heating"

**Scope (COU).**
- Informational estimate of the AA (and, separately, total vitamin C) fraction remaining in the vegetable piece and the fraction transferred to the cooking water.
- Applies to blanching, boiling and steaming at 60–100 °C, ambient pressure, for matrices with calibration data.
- The output feeds the Step-36 evidence packet as a MODEL ESTIMATE with an interval and a domain flag. It is never evidence and never a test label.

**Structure (modular, deterministic core).**
- C = AA concentration in tissue; W = AA mass in water.
- Degradation: dC/dt = −k_d(T_p(t)) · C, with first-order kinetics and k_d(T) = k_ref · exp[−Ea/R · (1/T − 1/T_ref)].
- Leaching: −k_L · (C − C_w,eq), where k_L is a lumped first-order mass-transfer coefficient scaled by surface/volume class and temperature.
  - It is switched OFF for steam, sealed-bag or no-water media.
  - Water-phase degradation is optional.
- Product temperature T_p(t): by default isothermal at bath T for purées and small pieces (with a stated limit on piece size). A lumped-capacitance or 1-D conduction module is optional for larger pieces, flagged EXTRAPOLATED until validated.
- Weibull / Peleg non-linear primary models are **candidate alternatives**, not the default. Default first-order is supported for blanching (e.g. Cruz et al. 2008). The choice is made in 26a on held-out fit, not AIC alone.
- Mass-balance invariant: C·V_tissue + W + degraded = initial (verification test).

**Parameters.**
- From Step 25 parameter-compatibility retrieval: per matrix class (ln k_ref, Ea, k_L) with posterior covariance and provenance to the K1/K2 series that produced them (SSOT §216.2 rows).
- No cross-matrix default.

**Why AA first (explicit rationale):**
1. It has the largest independent trajectory literature.
2. It tests the plan's own unresolved question (MP L614, Z1-Q4: leaching vs destruction vs apparent retention).
3. It has an existing downstream consumer and a sanity envelope (1,196 E3 vitamin C rows).
4. It is a low-risk COU.
5. Its known failure mode (non-transferable Ea) teaches the domain-of-validity machinery that every later simulator needs.

It is **not** chosen for impressiveness, and acrylamide (the SSOT §210.29A anchor) is deliberately postponed because of high consequence and precursor dependence.

### 3.2 Pre-registered fallback: SIM-CHL-1 (chlorophyll a/b → pheophytin; green colour)

Degradation-only first-order with Arrhenius and a pH-gated k (pH as a required input; UNKNOWN → prohibited).

Switch to SIM-CHL-1 if the census (§6) shows AA K1/K2 series too poorly reported to identify k_L, or fewer than the inclusion quotas.

### 3.3 Rejected alternatives (reasons)

- **Acrylamide:** precursor-dependent, high decision consequence, empirical model in crisps with poorly identified degradation parameters (Knol 2009), endpoint-dominated food data.
- **Maillard HMF/furosine:** model-system networks that do not transfer.
- **Starch gelatinisation:** model-form ambiguity and few in-situ trajectories.
- **POD/PPO:** low downstream value (kept as an optional V&V testbed).
- **Folate:** non-first-order, vitamer complexity.
- **Thiamine:** retort/meat-centred.
- **Carotenoids:** low study independence.
- **Polyphenols (Phenol-Explorer):** storage-dominated series and apparent increases.
- **A generic multi-mechanism simulator:** violates "one focused simulator" and the evidence base.

---

## 4. What each spine step must change or add

### Step 26 — Implement one focused deterministic simulator → **MODIFY**

**Substeps**
- **26a — Kinetic fitting and identifiability library.** Moved forward from Step 32:
  - one-step global reference-T Arrhenius fit (nonlinear least squares and Bayesian);
  - hierarchical matrix effects;
  - profile likelihood / scaled sensitivity coefficients;
  - synthetic-truth recovery test (SSOT §273.2 analogue — the legitimate first use of E7).
- **26b — SIM-AA-1 code**, following §3.1.
- **26c — Verification:**
  - analytic first-order solution vs ODE solver under non-isothermal T(t);
  - time-step convergence;
  - mass-balance invariant;
  - unit/dimension checks;
  - parameter-recovery tests on synthetic data;
  - regression tests.
- **26d — Model card + COU + model-risk grade** (V&V 40 / NASA-7009B vocabulary).

**Inputs**
- Step 24 registry entry, Step 25 parameter sets.
- CALIBRATION-split K1/K2 series only (Step 15 frozen split).
- Step 23 applicability verdict.

**Outputs**
- `SIM` model card (model_id, mechanism_id, equations, state variables, parameters with units, assumptions, IC/BC, matrix_scope, condition_scope, domain_of_verification, M&S limits, calibration_source_ids, validation_status = NOT_VALIDATED, credibility levels, sim_version).
- Reference implementation and a verification report.

**Baselines**: none yet (this step is verification only).
**Gate**: all verification tests pass and synthetic recovery coverage is nominal (e.g. 90% CIs cover truth ≈90% across ≥200 synthetic datasets).
**Compute**: CPU only (Mac sufficient); no GPU.

### Step 27 — Validate simulator on real held-out evidence → **MODIFY (sharpen)**

**Held-out design**
- Unit of independence = research group / lab (Step 08 lineage), not the paper.
- **Locked validation set** = all K1/K2 series from ≥30% of independent groups, chosen before any fitting and frozen in Step 15.
- Three tiers:
  - **V1 in-domain:** held-out groups, matrices and T inside the calibration domain.
  - **V2 held-out temperature:** a temperature band withheld (SSOT §211.25).
  - **V3 held-out matrix:** expected to degrade; used to *map* the domain, not to pass.
- Leaching module validated only on studies reporting tissue and water (mass balance), or open vs sealed contrasts.

**Metrics**
- Per-timepoint error on ln(C/C0); trajectory RMSE.
- Predictive-interval coverage at 80/95% with interval width (sharpness) and CRPS.
- V&V 20 comparison error E = S − D vs u_val at each validation point.
- Bias vs temperature and time.
- Study-cluster bootstrap CIs.

**Baselines** (the simulator must beat B1–B3 on V1):
- B0 persistence (retention = 1);
- B1 process-mean retention from E3 (USDA/Bognár by process type);
- B2 empirical log-linear in t, pooled;
- B3 nearest-evidence (same matrix, closest condition);
- B4 small GBM / regularised linear model on (T, t, matrix class, medium).

**Negative controls**: randomized-parameter simulator (Ea and k_ref drawn from the wrong matrix); shuffled-temperature inputs; degradation-only model on boiling data, to show that leaching matters.

**Pass gate (pre-registered)**
- On V1, the simulator is better than B1 and B3 with study-bootstrap CI excluding 0.
- 90% PI coverage within [0.80, 0.97].
- No monotone bias in T.
- Domain-of-validation hull published per output.

**Fail action**: validation_status = RESEARCH_ONLY. The simulator cannot be surfaced in RAG. Step 28 is restricted to identifiability and method development. If the failure is identifiability of k_L → switch to SIM-CHL-1 (pre-registered).

**Outputs**: validation report; per-output domain_of_validation spec (matrix classes, T range, t range, medium, piece-size class, pH and O2 condition); NASA-7009B validation and use-assessment levels; the E3 plausibility-envelope check (labelled NOT VALIDATION).

### Step 28 — Generate controlled E7 synthetic prior → **MODIFY + GATE (default DEFER until Step 27 PASS)**

**Generation rules**
- Only from a Step-27-passed sim_version.
- Domain randomisation over calibrated posterior and condition ranges wider than the real training set (Read et al. 2019 condition).
- Simulated noise, LOD censoring and sparse sampling per SSOT §223.2.
- Every row carries provenance_class = SIMULATED, tier E7 and the fields listed in Q6-4.

**Required experiments** (executed in Step 30/33, specified here)
- Synthetic ratio sweep 0–5× (§223.10).
- Real-n learning curve.
- TRTR / TSTR / mixed.
- **Matched-volume randomized-simulator control.**
- Calibration-leakage audit.

**Hard rule**: E7 is never in calibration/test (§223.14).
**First legitimate uses** (in order): identifiability and optimal-design studies (SSOT §224.4) to direct Step 14 acquisition; stress tests for Step 34 rollout; pretraining only as a gated ablation.

### Step 32 — Focused kinetics → **MODIFY (re-scope; it is no longer a prerequisite of Step 26)**

**Content**
- K0–K6 kinetic ablation (SSOT §215.57) on transition targets, compared against Step 30 tabular and Step 31 physics features on the **same** study-disjoint test.
- Primary-model selection by held-out performance: first-order, Weibull, fractional-conversion, biphasic.
- Identifiability report (§215.14).
- Extension to a second system only after Step 27 PASS: SIM-CHL-1, or acrylamide/Maillard anchors (§210.29A) as RESEARCH_ONLY.

**Metrics**: §215.14 (trajectory error, residuals, parameter uncertainty, identifiability, condition-OOD, plausibility).
**Gate**: kinetics retained only where it beats tabular on held-out-temperature or condition-OOD (SSOT §211.25 rationale).
**Compute**: CPU.

### Related steps (consumers or providers; brief)

- **Step 24 registry.** Model-card schema as above, plus credibility levels and domain fields. A JSON-schema model card with a reference Python implementation is sufficient. SBML/CellML is unnecessary for single first-order models (my judgement, MEDIUM); reconsider for reaction networks (Maillard).
- **Step 25.** Must return parameter sets with matrix/condition compatibility and "no compatible set" → prohibition.
- **Step 33.** Hybrid = SIM-AA-1 + learned discrepancy (K–O'H style) vs pure ML vs pure mechanistic, on V1/V2.
- **Step 34.** Rollout uses SIM-AA-1 only inside the validation domain; the trust horizon equals the domain exit.
- **Step 36.** Cascade DIRECT → INTERPOLATE → MODEL(only IN_VALIDATION_DOMAIN) → QUALITATIVE → ABSTAIN. The packet shows the sim_version, interval and domain flag.

---

## 5. Look-ahead requirements for earlier steps (must be captured before Step 26)

1. **Step 07 / COND schema.** Add UNKNOWN-default fields:
   - product (core) temperature vs medium temperature;
   - start mode (cold-water vs boiling-start);
   - water:food ratio;
   - lid/covered;
   - piece geometry (size class, shape, cut);
   - medium pH and tissue pH;
   - O2 / packaging / headspace;
   - microwave power + measured product T;
   - pressure.

   Current `completeness_mask` covers only duration, moisture, pH, pressure and temperature (`src/culinarystate/ingest/*_build.py`).
2. **Step 08 lineage.** Independence groups at the **research-group / lab** level and shared-sample detection. This is required for study-disjoint kinetic validation (several AA and carotenoid groups publish many papers).
3. **Step 09 extraction.** Must capture:
   - **time series from tables and figures**, with digitisation provenance and digitisation uncertainty;
   - replicate n and SD/SE;
   - analyte basis: AA vs total vitamin C (AA+DHA); chl a/b vs −a*;
   - analytical method (HPLC vs DCPIP titration);
   - wet/dry/initial-basis and yield;
   - whether cooking water was assayed (mass balance);
   - open vs sealed conditions.

   Raw timepoints must be stored separately from fitted parameters (SSOT §216.2 last line).
4. **Step 10 pilot (20 rows).** Include ≥5 AA kinetic series and ≥3 chlorophyll series. This doubles as the Step-26 extractability census (§6).
5. **Steps 11–14 acquisition quotas for Step 26/27** (proposals; justify or revise after the census):
   - AA: ≥30 K1+ series from ≥10 independent groups, ≥5 matrices, ≥4 distinct temperatures overall;
   - ≥3 independent groups with K2 designs (≥3 T × ≥4 t, matching the SSOT §210.29A pilot rule);
   - ≥3 mass-balance or open-vs-sealed leaching studies;
   - the same census for chlorophyll as fallback.
6. **Step 15 freeze.** Freeze the study-disjoint assignment of kinetic series into SIM-CALIBRATION / SIM-VALIDATION (locked) / DOWNSTREAM-TEST **before** any parameter fitting. Simulator-calibration groups must be a subset of downstream training groups.
7. **Steps 21–23 mechanism / applicability.**
   - Represent AA pathways (aerobic oxidation, anaerobic, enzymatic ascorbate oxidase, physical leaching) with activation conditions (T, O2, pH, metal ions, enzyme state).
   - Step 23 must output APPLICABLE / NOT_APPLICABLE / UNKNOWN; UNKNOWN → SIM_PROHIBITED.
8. **Steps 16–20 recipe semantics.** To call SIM-AA-1 from a recipe, events must carry: process type, duration, medium and amount, cut size, lid and start mode. Without them the simulator runs only on evidence rows, and recipe calls abstain.
9. **Step 04 contracts.** The SIM / E7 provenance fields (Q6-4) and the domain_flag enum must be added to the evidence/provenance contract. The existing `source_class` already has MODEL_GENERATED / SYNTHETIC (S116).

---

## 6. Residual uncertainty and pilot vs more reading

**Residual uncertainties**
- **(U1)** Whether enough AA K1/K2 cooking series report piece geometry, water ratio and analyte basis for k_L to be identifiable. *This decides AA vs chlorophyll.*
- **(U2)** Whether first-order is adequate at 60–100 °C across matrices, or Weibull/fractional-conversion is needed (literature mixed; resolve by held-out fit in 26a).
- **(U3)** Heat-transfer lag significance for whole pieces vs purées.
- **(U4)** Whether the V1 pass gate is achievable given the cross-study Ea spread; the hierarchical model may give honest but very wide intervals.
- **(U5)** Whether E7 pretraining adds anything beyond hierarchical Bayesian kinetics. This is plausibly small, which is why Step 28 is DEFERred and gated.

**Pilot vs reading.** Further reading will not resolve U1–U4 (stop rule §8.5 applies). A bounded **extractability census** is cheaper and more informative:
- Screen ~50–80 candidate AA and chlorophyll kinetic papers already reachable via the repo's Route-B OpenAlex verification queue (WORKLOG L150).
- Count series meeting the inclusion criteria and record reporting completeness of each look-ahead field.
- Effort: ~2–3 human-days. CPU only. No dataset download beyond metadata/abstracts.

This census belongs inside Step 10/11 (not now; Step 08 is the next authorised step).

**Overall confidence**
- First-simulator choice: MEDIUM–HIGH (AA vs chlorophyll is the only live alternative).
- V&V structure: HIGH.
- E7 practice: MEDIUM–HIGH (sound tiers; missing controls identified).
- Step-32 dependency correction: HIGH.

---

## Sources (see the bibliography in the structured return; tags as above)

- Giannakourou & Taoukis 2021, Foods 10:2630, doi:10.3390/foods10112630 [V PDF pp. 1–6, 14–22, 26–27].
- Peleg, Normand, Dixon, Goulette 2018, CRFSN 58(9):1478–1494, doi:10.1080/10408398.2016.1264360 [V metadata].
- Cruz, Vieira, Silva 2008, IFSET 9:483–488 [V-meta].
- Delchier et al. 2014, Food Chem 157:439–447, doi:10.1016/j.foodchem.2014.02.054 [V-meta abstract via AGRIS].
- Delchier, Reich, Renard 2012, LWT 49:197–201, doi:10.1016/j.lwt.2012.06.017 [V metadata; claim UNVERIFIED].
- Steet & Tong 1996, J Food Sci 61:924–928, doi:10.1111/j.1365-2621.1996.tb10903.x [V abstract via Crossref].
- Schwartz & von Elbe 1983, J Food Sci 48:1303–1306, doi:10.1111/j.1365-2621.1983.tb09216.x [V metadata].
- Koca, Karadeniz, Burdurlu 2007, Food Chem 100:609–615, doi:10.1016/j.foodchem.2005.09.079 [V metadata].
- Anthon & Barrett 2002, JAFC 50:4119–4125, doi:10.1021/jf011698i [V-meta].
- Ling & Lund 1978, J Food Sci 43:1307–1310 [UNVERIFIED beyond a citing reference].
- Knol et al. 2005, JAFC 53:6133–6139, doi:10.1021/jf050504m [V metadata + repository abstract].
- Knol et al. 2009, Food Chem 113:103–109, doi:10.1016/j.foodchem.2008.07.032 [V metadata + abstract via catalogue].
- Martins & van Boekel 2005, Food Chem 90:257–269, doi:10.1016/j.foodchem.2004.04.006 [V metadata].
- van Boekel 2008, CRFSFS 7:144–158, doi:10.1111/j.1541-4337.2007.00036.x [V].
- Knockaert et al. 2012, JAFC 60:10312–10319, doi:10.1021/jf3025776 [V metadata].
- Dolan & Mishra 2013, Annu Rev Food Sci Technol 4:401–422, doi:10.1146/annurev-food-022811-101247 [V].
- Datta 2008, CRFSFS 7:121–129, doi:10.1111/j.1541-4337.2007.00030.x [V].
- NASA-STD-7009B (2024-03-05) [V PDF].
- FDA 2023 guidance "Assessing the Credibility of Computational Modeling and Simulation in Medical Device Submissions" (issued 2023-11-17) [V PDF].
- ASME V&V 40-2018 [via FDA; standard itself not opened].
- ASME V&V 20-2009 [V-meta via Hills 2010 Sandia overview].
- Oberkampf & Roy 2010, CUP, doi:10.1017/CBO9780511760396 [V metadata].
- Roy & Oberkampf 2011, CMAME 200:2131–2144, doi:10.1016/j.cma.2011.03.016 [V metadata; abstract via search].
- Kennedy & O'Hagan 2001, JRSS-B 63:425–464, doi:10.1111/1467-9868.00294 [V metadata].
- Hollmann et al. 2025, Nature 637:319–326, doi:10.1038/s41586-024-08328-6 [V abstract].
- Müller et al. 2022 ICLR, arXiv:2112.10510 [V].
- Read et al. 2019, WRR 55:9173–9190, doi:10.1029/2019WR024922 [V abstract].
- Karpatne et al. 2017, IEEE TKDE 29:2318–2331, doi:10.1109/TKDE.2017.2720168 [V metadata].
- Esteban, Hyland, Rätsch 2017, arXiv:1706.02633 [V].
- Shumailov et al. 2024, Nature 631:755–759, doi:10.1038/s41586-024-07566-y [V abstract].
- Cranmer, Brehmer, Louppe 2020, PNAS 117:30055–30062, doi:10.1073/pnas.1912789117 [V metadata].
