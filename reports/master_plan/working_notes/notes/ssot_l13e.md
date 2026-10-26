# READER ssot_l13e — SSOT §259 (v14 return point) + Level-13E §§260–279 (+ V15 refs)

Source: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (SSOT), lines L42796–L45697, read in full (all bodies, not just headings). Line ranges from `docs/SSOT_INDEX.md` rows 3692–3937.
Cross-checked against: `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (PLAN), `reports/step07i/*`, `reports/step07/*`, `ledgers/data/REC.jsonl`, `ledgers/data/SRC.jsonl`, `registry/recipe_source_usage_registry_v1.csv`, `registry/ssot15_state_experiment_map.csv`, `tools/step07i_consensus.py`, `data/raw/gutenberg/{pg_catalog,cookbook_selection}.csv` (headers/first rows only), `data/external/foodcom/PROVENANCE.json` and Food.com parquet footer (column names only). Nothing was modified. The 36-step plan ("Master Execution Plan v1") is MISSING; all spine mappings in §8 are my reconstruction from SSOT/PLAN/repo and are labelled as such. No card text is attributed to the missing plan.

---

## 0. Headline verdict (where L13E belongs)

- SSOT's own verdict: "INCLUDE Level-13E as a parallel empirical research track, not as a universal causal theory of cuisine" (SSOT L42947). It is "a parallel extension of Level 13, not a new mandatory sequential level between 13 and 14" (L42927).
- SSOT explicitly removes it from the critical path: "The Level-12 molecule/ingredient track runs in parallel. Level-13E does not block Level-16 implementation unless the specific experiment uses its outputs." (L45449). "It should not delay the core project unless the user decides the cultural-evolution paper itself becomes the primary deliverable." (L45589). Critical path restated at L45566–45576 (L12 evidence/classical baselines + L16 schema/Deep Gold/semantic+quantity engine → 10k Silver pilot + evidence ledger + state graph → retrieval/confidence/transition fallback/decision).
- PLAN agrees: B15 "parallel track" ← B02,B03,B14 (PLAN L244, L497–501); AH12 "B15 Level-13E remains parallel… must not block course completion… one bounded reproduction chain… Everything else stays PARKED_POST_COURSE" (PLAN L2941–2953); Lane C lists "Level-13E full historical/cultural programme" (PLAN L2722); Lane B allows "one B15 Level-13E reproduction/null baseline if CPU/time allows" (PLAN L2710).
- Recommended placement in the 36-step spine (my reconstruction; anti-scope-creep §4 of the brief): NO new top-level step. None of brief §4 conditions A–D hold: no SSOT contradiction, the core spine has no hard dependency on L13E outputs (L45449), and continuing without it invalidates no downstream core claim. Home = a parallel, optional **Lane 35-E** attached to Step 35 (representation ladder, "recipe / cuisine" rung = Level 13, of which L13E is the extension), with integration sub-experiments in Step 36 (E13E-17 FlavorTwin prior, E13E-18 historical RAG).
- **Exceptions that are NOT optional / should be pulled earlier** (small, cheap, schema-level):
  1. Clock separation `tau` vs `t` (L42996–43021, L44231–44236) → Step 03 state semantics.
  2. Historical/source/date metadata block (L44422–44448; L44031–44047) as *nullable* fields → Steps 04/06/07 (recipe base) and 16 (schema). Cost is near zero now; retrofit later is expensive (brief §38).
  3. Recipe identity calibration (E13E-05, L44868–44891; §264 L43395–43537) is shared with PLAN SX-14-03 (PLAN L492) and with the already-built 07I-R 400-pair packet (unlabeled). Duplicate/lineage-group-safe splits are a near-term core artifact (SSOT §259.4 item 8 "duplicate/source-safe split registry", L42879). So a minimal identity-label pass is a soft dependency for Steps 17–20/29–30 split hygiene, not just L13E.
  4. Firewall rules (L42983–42995, L44374–44384) → Steps 04/05/15/24/28: historical/cultural and synthetic-history records never enter the EVD / chemistry evidence plane.
- Everything else (Phases E1–E7, L45356–45424) is parallel, deferrable, CPU-tier C0, and gated by G13E-01 DATA (L45278), which on current repo data will likely only pass for a narrow web-era (Food.com 1999–2019) analysis, not for historical evolution (see §5, §9).

---

## 1. Definitions, entities and data contracts

### 1.1 §259 v14 return point (L42796–42912) — context, still-binding parts
- Learning status box: L7–L11 FROZEN → L12…L16 SPEC COMPLETE (L42800–42814); "no longer needs another mandatory conceptual level before implementation. Level 17 … optional" (L42816).
- Immediate implementation order (L42824–42838), 13 items: 1 freeze schemas/provenance/validators; 2 build 100–500 difficult gold seed recipes; 3 bootstrap canonical ingredient/process/state/unit vocabularies; 4 deterministic quantity/portion engine; 5 10k Silver pilot; 6 audit and repair; 7 continue L12 and L14/15 evidence/model tracks in parallel; 8 scale Gold-Light/Silver only after gates; 9 state-aware retrieval + evidence packets; 10 calibrate abstention; 11 decision/diagnosis/recovery; 12 benchmark B0–B7; 13 only then FlavorTwin process-conditioned search. "Do not start with a polished chatbot UI and do not start by generating 100k annotations in one batch" (L42820).
- Authoritative flow box (L42842–42866): Schema/Ontology → Gold → Semantic+Quantity Engine → Silver Data Factory → Evidence Ledger → State Graph → Retrieval/Compatibility → Confidence/Abstention → Transition Fallback → Decision → FlavorTwin Inverse Search; "Levels 12–15 running as scientific evidence/model subprograms rather than being reimplemented inside the RAG layer" (L42868).
- Near-term artifacts (L42872–42881): 1 schema pack; 2 annotation handbook + Claude prompt pack; 3 Deep-Gold seed; 4 canonical ingredient/alias registry; 5 CQPO/unit/portion engine; 6 recipe event/state graph parser; 7 evidence atom/source ledger; 8 duplicate/source-safe split registry; 9 10k Silver pilot report; 10 L12 and L15 baseline reports.
- 10-question admission rule for any new idea (L42885–42898) — the operational form of the brief's anti-scope-creep rule; "If these questions cannot be answered, the idea does not enter the core architecture yet" (L42898). Q10 "Can it wait until the current critical path is empirically validated?" (L42896) is the governing test for L13E.
- Principle: "Build the evidence and semantic substrate first; let models earn the right to fill the gaps." (L42904).
- Note: §259 is superseded as the *current* return point by §279.8 (L45631–45644) but its sequence is reaffirmed by §279.5 (L45566–45576).

### 1.2 Naming / scope (§260, L42915–43062)
- Name: Level-13E = "Level-13 Evolution / Historical Dynamics" (L42924); rename because v14 reserves Level 13 for recipe/cuisine representations (L42921).
- Status table (L42931–42941): spec COMPLETE; historical-data audit OPEN; exact Kinouchi reproduction OPEN; exact Jain–Bagler reproduction OPEN; identity/novelty calibration OPEN; rank–frequency comparison OPEN; temporal holdout OPEN; SBI "DEFER until simulator parameter recovery succeeds on synthetic truth" (L42938); simulator pretraining "DEFER by default; must earn itself against real-only pretraining and randomized-simulator controls" (L42939); FlavorTwin scope unchanged (L42940); CulinaryState-RAG scope unchanged; historical evidence "a distinct evidence class; it cannot override process chemistry or direct current-state observations" (L42941).
- Core use chain (L42953–42959): historical/cultural data → null models + temporal priors + recipe-family structure + diffusion hypotheses → better controls / splits / identity calibration / substitution priors. NOT historical popularity → chemical truth / sensory equivalence / causal mechanism (L42962–42967).
- Allowed-influence table (L42971–42981), 9 rows: food-pairing claims; recipe identity ("no arbitrary fixed '30% changed = new recipe' rule"); novelty ("novelty ≠ quality, palatability or creativity"); substitution (cultural/context prior; cannot replace structural/sensory/process evidence); cuisine representation (temporal distribution/drift/diffusion; source bias explicit); L12 evaluation (may define source/time/geography holdouts; "does not change molecule representation z_m"); L13 representation (adds historical/cultural views to z_R/z_C where task-justified; not mandatory); L16 RAG (historical provenance packet; separate evidence class); FlavorTwin (optional prior p(candidate | cuisine, era, role)).
- NOT influenced by default (L42985–42994): z_m; fingerprints/descriptors; within-recipe transition dynamics tau in L14–15; kinetic constants/pathways/pH/concentration "unless independently measured"; sensory equivalence/palatability; L16 data-provenance hierarchy; frozen FlavorTwin V2 boundary; UNKNOWN != 0; cultural frequency ≠ mechanistic importance; association ≠ causality.
- Two clocks (L42996–43021): `tau` = within-recipe process time (s–h), `t` = historical/cultural time (years–centuries). "Never write a single state equation that silently mixes them." (L43008). Process: z_{i,τ+1}=T_φ(z_{i,τ},p_τ,θ_τ) (L43013). Cultural objects: P_{i,c}(t), R_c(t), G_c(t), F_{i|c,t} (L43019).
- Evidence labels for PART XIII (L43024–43030): [ESTABLISHED], [REPRODUCE], [HYPOTHESIS], [OPEN], [PROPOSED], [USER-REPORTED], [VERIFY].
- A2 inheritance (L43032–43043): A2 pipeline implements binary recipe–ingredient transactions, exact itemsets k<=3, size-preserving uniform random cuisine, frequency-weighted size-preserving random cuisine, normalized frequency–rank q_i=f_i/N, deterministic seeds/assertions → "may seed M0 null-model code" but does not establish evolution/fitness/selection/diffusion.
  - Repo reality: `src/culinarystate/classical/` contains only an empty `__init__.py` (verified). A2/A3 live in `../A2`, `../A3` (STATUS.md L15) which are NOT on this machine; `registry/ssot15_state_experiment_map.csv` row SX-03-05 = PARTIAL "../A3 copy-mutate models (624/624 assignment checks); exact Kinouchi reproduction not verified". → A2/A3 claims UNVERIFIED here.
- Deliverable crosswalk (L43047–43059): D1–D11 all "COMPLETE SPEC"; D3 "gold labels OPEN"; D8 "audits OPEN".

### 1.3 Interface contract (§262, L43277–43317)
Table L43281–43288 (inputs consumed / outputs produced / forbidden shortcut):
| Layer | L13E consumes | L13E may produce | Forbidden |
|---|---|---|---|
| L12 | canonical ingredients; optional z_i; flavor compound sets **with coverage metadata** | historical usage prior; substitution/co-use prior | prevalence altering molecular structure |
| L13 | R, z_R, z_C, quantities/roles/process when available | temporal recipe/cuisine views; recipe-family graph; cultural distance | "same-cuisine pairs universally similar" |
| L14 | process labels/conditions only as recipe descriptors | process adoption/change statistics over historical t | mixing t with tau |
| L15 | optional validated process effects | no new chemical transitions; only historical priors on process usage | inferring kinetics from historical recipe frequency |
| L16 | canonical entities, quantities, events, provenance, source metadata | historical evidence packets; source-aware priors | upgrading inferred dates/cultural hypotheses to fact |
| FlavorTwin | target/candidate role/context | optional cultural/substitution prior | cultural prevalence = flavor equivalence |
- View vector: V_R(t) = [x_R, q_R, role_R, process_R, z_R, meta_{c,t,source}] (L43295). Model target: P(V_R(t+Δt) | V_R(t), c, C(t), J(t)), C(t) = contact/context, J(t) = external introduction events (L43301–43304). "This is not the Level-15 equation" (L43306).
- Optionality law: "missing historical date does not invalidate a recipe; it invalidates date-dependent inference." (L43313); recipe without reliable metadata "remains valid for Level 13/16 but is excluded from date-sensitive Level-13E claims" (L43310). ⇒ all historical fields must be nullable with explicit UNKNOWN (consistent with UNKNOWN != 0).

### 1.4 Canonical notation (§263, L43318–43394) — field-level
Table L43322–43359 (symbol | meaning | type | unit | source | status). Key data-contract symbols:
- `I` canonical ingredient universe (FROZEN concept); `N_I`; `c` cuisine/geo-cultural context, categorical ontology ID, observed/curated; `t` historical time scalar/interval year/era "uncertain allowed"; `tau` process time "separate clock"; `R` recipe; `n_R` unique ingredient count; `K` mean/target simulator recipe size; `R_c(t)`, `N_c(t)`; `O_{i,c,t}` recipe-incidence count; `P_{i,c,t}`=O/N prevalence; `O^W_{i,c,t}` quantity-weighted occurrence "only when grounded"; `A_{i,c,t}` relative prevalence/authenticity "descriptive, not value judgment"; `C_i` flavor-compound set "coverage-limited"; `N_s(R)`, `Delta N_s`, `chi_i` ("as defined in cited food-pairing work", historical baseline); `d_R(a,b)` calibrated recipe distance; `p_same(a,b)` (calibrated gold); `Novelty(R|B)`; `F_{i|c,t}` observed fitness-feature vector; `eta_{i|c,t}` latent selection parameter "latent, not observed"; simulator params `N0`, `R0`, `L`, `L/K` ("experiment axis"), `M` ("define per reproduction"), `gamma` [0,1]; `H_{cc'}(t)` contact intensity (hypothesis); `J_i(t)` exogenous availability {0,1}/prob (uncertain); `Q_{ji}` mean-field mutation matrix; `x_i(t)` simplex share; **`s` source/cookbook/domain ID (observed, provenance)**; **`d_low,d_high` date interval (year)**; **`e_date` date evidence class {exact/edition/estimated/unknown} "required"** (L43359).
- §263.1 (L43361–43363): do not unify N, R/N and Kinouchi's M "from memory"; keep paper's own definitions + explicit conversion table.
- §263.2 (L43365–43381): prevalence P = O/N_c(t) vs slot share S = O/Σ_j O_j; "Never mix them in the same rank–frequency analysis without labeling."
- §263.3 (L43383–43391): A_{i,c,t} = P_{i,c,t} − Σ_{c'≠c} w_{c'} P_{i,c',t}, weights declared; does not mean ownership/quality/origin/legitimacy.

### 1.5 Recipe identity / distance / novelty (§264, L43395–43537)
- Fixed % rule rejected (L43399); identity calibrated on same-dish / variant / different-dish judgments (L43401).
- Multi-view distance d(R_a,R_b)=g(d_I,d_Q,d_role,d_P,d_G) (L43408); d_I ingredient-set; d_Q aligned quantity; d_role culinary-role mismatch; d_P process/event sequence; d_G recipe-state/flow-graph (L43413–43417). "Do not freeze scalar weights a priori." (L43419).
- d_I baseline weighted Jaccard J_w; weights binary / IDF / role / quantity-grounded; "The chosen regime is an ablation, not a hidden choice." (L43426–43430).
- d_Q: log-ratio/compositional on aligned ingredients; "Missing quantities receive masks; they are not treated as zero."; baseline d_Q = mean |log(q_a+ε) − log(q_b+ε)|; interval/Monte-Carlo uncertainty if quantities are intervals (L43434–43442).
- d_P baselines: normalized Levenshtein; DTW on event embeddings; graph edit distance; learned encoder promoted only if it beats edit-distance baselines on same-family discrimination (L43452–43458).
- p_same = P(Y_same=1 | d_I,d_Q,d_role,d_P,d_G, confounds), report calibration; "Do not treat embedding cosine as an intrinsic identity probability." (L43465–43470).
- Calibration strata (L43476–43483): same exact source duplicate; same named dish / same edition variant; same dish family / different author or era; near neighbor / same category; hard negative with similar ingredients; obvious different dish. Independent human/expert labels on a subset; "Headline split must group by source/duplicate family" (L43485–43487).
- Threshold only after calibration at declared operating point (equal error / high precision / task cost); "not universal and must be reported with its validation distribution" (L43491–43497).
- Novelty vector N(R) = [N_ingredient, N_quantity, N_process, N_pair, N_culture, N_evidence] (L43506–43507); N_density(R) = −log p̂(R|B) with model class and reference corpus B declared (L43513–43516); novelty ≠ tastiness/safety/appropriateness/creativity/superiority (L43518–43524).
- Historical novelty: Novelty_t(R) = −log p̂(R | R_{≤t}); future recipes in B = leakage (L43528–43534).
- Repo status vs §264 (from `reports/step07i/max_plan_consensus.md` L15, L30, L43, L48): 07I-R implemented d_I (id Jaccard, IDF Jaccard, multiset), d_P (set + LCS), d_Q (cosine of mass shares — SSOT baseline is log-ratio, flagged IMPLEMENTATION_DETAIL "revisit with E13E-05"), title, condition; d_role and d_G unavailable; fixed-weight ranking score allowed only as ranking aid; no threshold; 400-pair blind packet `reports/step07i/duplicate_calibration_packet_manifest.json`: 400 pairs, 10 strata (S01_very_high 40, S02_high 50, S03_boundary_family_rule 60, S04_moderate 40, S05_same_title_low_structure 40, S06_cross_source 40, S07_same_source 30, S09_high_ingredient_diff_process 40, S10_high_text_diff_ingredient 40, S11_regional_cultural_hint 20), `labels_filled: 0`. Label set (`reports/step07i/preregistration_v1.md` L33): SAME_RECIPE_COPY, SAME_RECIPE_MINOR_VARIANT, SAME_DISH_DIFFERENT_RECIPE, RELATED, DISTINCT, UNCERTAIN.
  - Gap vs SSOT L43476–43483: no "same edition variant" and no "different author or era" stratum; only 20 regional/cultural pairs; no era stratum at all. → E13E-05 needs an augmentation packet if historical identity is ever claimed.

### 1.6 Fitness (§265, L43538–43646)
- Split: F_{i|c,t} observed/context feature vector vs η_{i|c,t} latent simulator selection parameter (L43546–43553).
- Candidate F components (L43559–43571): prevalence, persistence, geographic spread, relative prevalence, availability, cost, seasonality, cultural/religious constraints, nutrition, sensory/context compatibility, source/evidence quality. "Most of these are incomplete historically. Missingness is explicit." (L43574).
- Context: F_{i|c,t,r}, r = role/dish context (L43585–43588).
- Acceptance utility u(i|c,t)=β^T F + η_i + ε; P(accept)=σ(u_new−u_old); "But the exact Kinouchi hard rule must be reproduced first." (L43595–43604).
- **Anti-circularity rule** (L43606–43623): if P_{i,c,t} enters fitness, same-period prevalence cannot be the headline target. Forbidden triple: fitness := current prevalence; predicts current prevalence; success := correlation with current prevalence. Acceptable: P at t0 → t1; non-prevalence fitness → future prevalence; fit some cuisines/eras → predict held-out; different targets (persistence, substitution acceptance).
- Validation target: P_{i,c,t+1} or ΔP_{i,c,t→t+1} under temporal/source holdout (L43629–43633).
- Non-normative (L43637–43643).

### 1.7 Mutation operators (§267, L43754–43879)
- Hard replacement R' = (R \ {i}) ∪ {j} (L43759); add/delete (L43767); soft attenuation w_i' = γ w_i, mass/share-conserving w_j' = w_j + (1−γ) w_i (L43777–43784), reference pseudocode `attenuate()` (L43791–43802); semantics of weights (mass vs normalized share vs uncertain household unit) must be recorded (L43804).
- **Discontinuity** (L43806–43818): for γ>0 binary N_s and incidence prevalence are unchanged — "key correction to simplistic 'diminish versus remove' reasoning".
- Quantity-weighted pairing N_s^W (L43825–43831) [PROPOSED]; quantity-weighted prevalence P^W (L43840–43844) "Only use when w has consistent semantics across recipes."
- Dose curves vs λ = L/K (L43851) reporting identity probability, d_I, pairing, category composition, cultural-classifier probability, process distance (L43854–43861).
- Higher order: nested H1 singletons, H2 +pairs, H3 +triples, H4 selected; promote k+1 only on held-out gain after regularization/complexity penalty; sparse hierarchical/log-linear/FM preferred (L43868–43876).

### 1.8 Rank–frequency (§268, L43880–43952)
- Three curves: prevalence-rank P_i=O_i/N_recipes; slot-share-rank S_i; raw count O_i (L43884–43886).
- Rank normalization ρ_i=(r_i−1)/(M−1) (L43895) (symbol collision, see §9).
- Universality H0/H1 (L43902–43903); "Do not equate visual curve collapse with proof of one evolutionary mechanism." (L43905).
- Fitting: MLE, lower cutoff, bootstrap KS GOF, LR/non-nested comparisons, uncertainty; "Do not fit a line by least squares on log–log axes" (L43909–43917). Alternatives: power law, truncated PL, lognormal, exponential, stretched exponential; discrete count models (L43924–43931).
- Source-balanced bootstrap (L43935). Many-to-one θ→summary map: rank-frequency "Usually not" identifying (L43939–43949).

### 1.9 Food-pairing / null lattice (§269, L43953–44028)
- Frozen: N_s(R) = 2/(n_R(n_R−1)) Σ_{i<j}|C_i∩C_j| for n_R≥2; ΔN_s = N̄_s^real − N̄_s^null (L43960–43966).
- Null lattice table (L43973–43980): U (size ✓), F (size + frequency ✓/approx), C (size + category), FC, E (size + era/source), FCE ("strongest feasible matched null"). "Every headline pairing result must state which structural features are held fixed." (L43971).
- A2 weighted sampler p_i∝f_i ≠ exact degree preservation; compare bipartite degree-preserving edge swaps for headline nulls (L43984).
- Coverage control mandatory audits (L43990–43997): compound-set size distribution; source count per ingredient; cuisine-specific fraction of mapped ingredients; matched-coverage resampling; sensitivity excluding low-coverage ingredients; Jaccard/cosine-normalized overlap.
- Network alternatives (L44001–44008); group effects with BH-FDR plus raw effect sizes/CIs (L44012–44021); "culinary fingerprint is descriptive" (L44025).

### 1.10 Temporal / dating / lineage (§270, L44029–44115)
- Per recipe/source fields (YAML, L44035–44047): `source_publication_year`, `source_edition_year`, `recipe_date_low`, `recipe_date_high`, `date_basis: [exact_publication, edition, archive_estimate, first_attestation, inferred, unknown]`, `date_confidence`, `source_author_editor`, `source_type`, `source_language`, `translation_status`, `ocr_quality`.
- t_document vs t_recipe-origin (L44053–44063): "If origin is unknown, do not backdate from intuition."
- Interval-censored t_R ∈ [t_low, t_high]; propagate by multiple imputation / interval weighting / sensitivity runs (L44069–44073).
- Era bins justified by data density/historical events + sensitivity (L44077); learned/Fourier time embeddings only after date quality adequate (L44081).
- Temporal holdout: train ≤ t0, validation next era, final test later era or held-out sources; "Duplicate/edition lineages must not cross the temporal split." (L44087–44093).
- Edition/derivative leakage: build lineage/near-dup groups and assign wholly to one split (L44097).
- Web vs cookbook shift (8 axes L44101–44110): "Never use a pooled web-vs-historical comparison as pure temporal evolution without a source-domain control." (L44112).

### 1.11 Contact / diffusion (§271, L44116–44186)
- H_{cc'}(t) ≥ 0 (geographic proximity, trade, migration, recipe-similarity flow); "Do not fabricate historical contact weights" (L44122–44128).
- Adoption hazard λ_{i,c}(t) = α_i + β^T X_{i,c,t} + Σ_{c'≠c} H_{cc'}(t) P_{i,c',t} + δ J_i(t) — "statistical hypothesis, not a causal guarantee" (L44135–44142).
- J_i(t) only after historians/primary sources support date+geography; Columbian exchange = type example, "not a license to hard-code every ingredient's arrival year from general knowledge" (L44146–44148).
- Event study: pre/post windows, matched controls, source composition, trajectories, avoid causal language if parallel-trend/contact assumptions fail (L44152–44158).
- Recipe-family lineage DAG/tree only for documented lineage; global = branching + borrowing + convergence + hybridization; reticulate default (L44162–44173).
- Process adoption states P(process=k | c,t) (L44179–44183).

### 1.12 Replicator–mutator (§272, L44187–44236)
- ẋ_i = Σ_j x_j f_j(x,t) Q_{ji} − f̄(x,t) x_i + u_i(t) (L44194); interpretation L44201–44204.
- Appropriate: aggregate prevalence target, combinatorial structure secondary, enough time points, mean-field reasonable (L44208–44213). Inappropriate: recipe-level process sequence, chemical kinetics, dish identity, exact substitution mechanism, causal fitness from cross-sectional data (L44217–44223).
- Clock firewall: "Code modules and variable names should enforce this separation." (L44233).

### 1.13 Inference (§273, L44237–44338)
- θ_E = [N0, R0, K, L, M, ψ_fitness, ψ_category, ψ_contact, ψ_intro, γ, …] (L44244).
- First gate synthetic truth recovery (5 steps L44253–44257); "If known parameters cannot be recovered from ideal simulator output, do not interpret real-data estimates mechanistically." (L44259).
- Summary vector s(D) (L44266–44275): recipe-size distribution, rank frequency, category composition, pair/triple residuals, network degree, N_s, ΔN_s, identity/novelty distribution, temporal adoption curves; "smallest sufficient-ish set that passes recovery" (L44278).
- ABC first (rejection/SMC) (L44282–44291); NPE promotion 4 conditions (L44295–44300); SBC rank uniformity + RMSE/bias, coverage, contraction, PPC, posterior correlations, multimodality (L44304–44313); fixed subsets pre-registered, repeated on random/stratified subsets, "Never select the subset after seeing which one gives the cleanest result." (L44317–44319); predictive adequacy vs identifiability reported separately (L44325–44335).

### 1.14 Simulator pretraining (§274, L44339–44394)
- P0 none; P1 real SSL (masked ingredient, masked process, temporal order discrimination, same-dish variant discrimination, next-era ingredient distribution) ; P2 simulator (M1–M6) → real fine-tune (L44343–44357).
- Required randomized-simulator control matched on volume/architecture (L44360).
- Promotion gate (L44364–44372): improves held-out **real** performance on ≥1 predeclared target (future-era ingredient prediction; source/cuisine cold-start; recipe-family identity; substitution ranking; representation calibration) without worsening calibration or shortcut dependence.
- "Simulator output is never historical evidence" — allowed uses pretraining, stress tests, identifiability tests, augmentation; "may not populate the evidence ledger as observed cultural facts" (L44376–44383).
- Near-term: simulators first for validation/stress testing; pretraining a gated experiment (L44389).

### 1.15 Data plan / schema / bias ledger (§275, L44395–44487)
- Data roles (L44399–44406): cross-sectional ← large modern corpora; historical evolution ← dated cookbooks/archives with source lineage; substitution behaviour ← user edits/reviews/substitution corpora; pairing ← ingredient–compound mappings + coverage metadata; quantity evolution ← normalized historical/modern measurement data; process evolution ← parsed event/process vocabulary over dated corpora.
- **Required schema additions to Recipe / Recipe Event-State** (`historical:` block, L44424–44448), 22 fields: `source_document_id, source_title, source_author_editor, source_publication_year, source_edition_year, recipe_date_low, recipe_date_high, date_basis, date_confidence, era_id, region_id, cuisine_id, language, translation_status, canonical_dish_name, variant_group_id, lineage_group_id, source_type, copyright_license, redistribution_allowed, ocr_quality, extraction_quality`.
- Bias ledger (13 items L44452–44466): class audience; professional vs household authorship; gendered editorial history; urban/rural; market access; literacy/publishing selection; colonial/trade context; religious/seasonal norms; genre; OCR survivorship; language/translation; digitization selection; web platform incentives. "These are confounds/limitations, not nuisance text to hide in discussion." (L44468).
- Sampling unit: source/cookbook/edition may be the cluster (L44472).
- Balancing on recipe count, dish-category composition, recipe-size distribution, source count, source type, flavor coverage, date precision (L44476–44484).
- PLAN AY8 (PLAN L4579–4596) implements as "dedicated HIST- records or a typed table under the source/recipe registry" with edition/publication date, recipe date interval, date basis, date confidence, region, cuisine, language, translation, source genre, lineage/duplicate family, historical-contact metadata, bias/confound fields. PLAN AX7 adds release `DATA-HISTORICAL` (PLAN L4460). PLAN AX6: "Historical sources do not enter the physical chemistry evidence plane." (PLAN L4443).

---

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 Generative/evolution ladder M0–M8 (§266, L43647–43753) with promotion gates (quoted)
| Rung | Content | Gate (quoted) |
|---|---|---|
| M0 randomized nulls (L43649–43662): M0-U size-preserving uniform; M0-F frequency/degree-preserving; M0-C category; M0-FC; M0-E era/source; M0-FCE | "Gate to M1: real historical/cuisine structure is not explained by matched nulls." (L43662) |
| M1 exact Kinouchi copy–mutate (L43664–43676): seed pool, initial recipes, fixed/target K, copy parent, mutate L loci, pool-growth relation, publication-specific fitness sampler/acceptance | "locally reproduce paper-level summary behavior within documented tolerance on a compatible dataset or replicate the qualitative curves if exact source data are unavailable." (L43676) |
| M2 category-constrained (new ∈ Category(old) or empirical replacement compatibility) (L43678–43688) | "improves held-out category composition / pairing / recipe plausibility beyond M1." (L43688) |
| M3 data-informed context fitness F_{i|c,t} (L43690–43694) | "predicts held-out future/cuisine statistics better than frequency-only and random-fitness baselines without circularity." (L43694) |
| M4 pairing/co-occurrence-aware mutation u(new|R)=β_F^T F_new + β_C Compat(new,R) (L43696–43706) | "adds held-out predictive value after frequency/category controls. N_s alone is not privileged; co-use/role/process alternatives must be compared." (L43706) |
| M5 soft attenuation w_i'=γw_i (L43708–43718) | "quantity data coverage and held-out gain justify the additional state." (L43718) |
| M6 multi-cuisine contact H(t) + J_i(t) (L43720–43724) | "dated/geographic/contact evidence exists and a contact model improves temporal/geographic holdout beyond cuisine-independent models." (L43724) |
| M7 mean-field replicator–mutator ODE (L43726–43736) | "ingredient/type frequencies are an adequate state summary for the target; agent-level recipe structure is not required." (L43736) |
| M8 neural generator (autoregressive/graph/diffusion) (L43738–43742) | "M0–M7 leave a clear held-out failure that the neural model addresses; the model beats explicit baselines on future/source/cuisine holdouts; novelty is not merely memorization; calibration/provenance remain auditable." (L43742) |
- Default stop rule: "If M1–M3 explain the held-out statistics, stop. Do not promote complexity for aesthetics." (L43748).
- Literature-mandated baselines before any learned historical generator: Kinouchi random-fitness CM; frequency/rank-informed CM; add/delete (CMAD) "if implementable" (L43160–43166).

### 2.2 Per-problem baseline ladders (from §§264, 267–269, 273–274, 277)
- **Identity** (E13E-05 L44873–44876): title-only, ingredient-Jaccard → I+Q → I+Q+role → I+process → full multiview → learned embedding comparator. d_P: Levenshtein → DTW → graph edit → learned encoder (L43452–43458).
- **Novelty** (E13E-06 L44899–44901): ingredient rarity score, random rare-ingredient injection, source-classifier score → set novelty → quantity/process novelty → density novelty → combined calibrated vector.
- **Rank–frequency** (E13E-01 L44776): descriptive empirical curve; PL; truncated PL; lognormal; exponential; stretched exponential.
- **Pairing** (E13E-04): U → F → C → FC → E → FCE nulls; raw shared count N_s → coverage-normalized overlaps → food-bridging/co-use descriptors (L44849–44851); A2 sampler vs degree-preserving swaps (L43984).
- **Co-occurrence** (E13E-09 L44970–44972): frequency-only → pairwise → +triple sparse → FM → selected higher-order; select "simplest within one SE" (L44982, L44976).
- **Temporal forecast** (E13E-11 L45016–45018): persistence, previous-era prevalence, source-matched bootstrap → frequency baseline → copy–mutate → context fitness → contact model (if data pass).
- **Diffusion** (E13E-12 L45041–45043): internal-prevalence-only, randomized degree/geography-preserving contact network → geographic proximity → observed contact proxy → learned latent contact.
- **Aggregate dynamics** (E13E-14 L45089–45091): persistence, independent trends → replicator → replicator–mutator → agent copy–mutate.
- **Inference** (§273, E13E-15 L45112–45114): prior-only posterior/random estimator → ABC rejection/SMC → NPE "only after baseline".
- **Pretraining** (E13E-16 L45139–45141): real-only → real SSL → simulator→real → randomized simulator→real.
- **FlavorTwin prior** (E13E-17 L45164–45166): base FlavorTwin static/process-conditioned → +co-use prior → +substitution-network prior → +historical/context prior; frequency-only ablation (L45177).
- **Historical RAG** (E13E-18 L45188–45190): ordinary dense RAG → structured source/date filters → evidence packets + conflict/date-uncertainty handling.

### 2.3 Compute tiers (§278.4, L45245–45272)
- C0 CPU: null models, itemsets, rank-frequency fits, copy–mutate, historical descriptive, identity classical baselines, bootstrap/permutation, event studies, simple ABC (L45249–45259).
- C1 single GPU "only when justified": learned recipe/sequence encoders, NPE, neural generator baselines, large-scale dense retrieval/embedding (L45263–45268).
- C2 multi-GPU "Not approved by default" (L45272).
- Consequence for this project's compute reality (ctx: shared GPUs unusable; A100 over slow VPN): essentially all of Phases E0–E5 are C0 and fit the 128-core Linux server/Mac CPU. Only E13E-15 NPE, E13E-16 pretraining, E13E-18 generator need C1 — all are DEFER-by-default items.

---

## 3. Experiments / hypotheses / RQs

### 3.1 RQ portfolio (§276, L44488–44756) — 22 RQs, every one "Current evidence status. OPEN" and all share the identical promotion rule: "Keep the added complexity only if the predeclared held-out metric improves with uncertainty reported and the gain survives the relevant source/frequency/coverage confound audits." (e.g. L44500).
| RQ | Lines | Question (short) | Settling experiment |
|---|---|---|---|
| 01 Scope value | L44490–44500 | does historical/cultural dynamics improve any decision beyond static reps? | ablate L13E features from matched L13/16 tasks |
| 02 Rank-freq universality | L44502–44512 | common family after source/size controls? | source-balanced MLE/GOF → E13E-01 |
| 03 Copy-mutate reproduction | L44514–44524 | faithful Kinouchi reimplementation reproduces summary classes? | E13E-02 |
| 04 Indian evolution reproduction | L44526–44536 | random-fitness / rank-informed / add-delete under cleaned pipeline? | E13E-03 |
| 05 Fitness representation | L44538–44548 | vector vs random/scalar/frequency fitness on future/held-out cuisines | temporal/cuisine holdout choice model → E13E-11 |
| 06 Anti-circular fitness | L44550–44560 | optimism gap circular vs prospective | "mandatory circularity audit" (L44556) — NO dedicated E13E experiment |
| 07 Recipe identity | L44562–44572 | which distance combo separates same-dish variants | E13E-05 |
| 08 Novelty | L44574–44584 | novelty predicts expert novelty without collapsing to rarity/source? | E13E-06 |
| 09 Mutation load | L44586–44596 | L/K dose response | E13E-07 |
| 10 Attenuation | L44598–44608 | soft vs hard mutation; "Only attempt if quantity coverage passes gate" | E13E-08 |
| 11 Higher-order | L44610–44620 | triples beyond pairs | E13E-09 |
| 12 Pairing nulls | L44622–44632 | which conclusions survive U/F/C/FC/E/FCE + coverage | E13E-04 |
| 13 Historical drift | L44634–44644 | chronological neighbours more similar after source control? | E13E-10 (+E13E-11) |
| 14 Diffusion/contact | L44646–44656 | contact features vs internal prevalence | E13E-12 |
| 15 Introduction shocks | L44658–44668 | verified events explain adoption changes? | E13E-13 |
| 16 Mean-field adequacy | L44670–44680 | ODE vs agent model | E13E-14 |
| 17 Identifiability | L44682–44692 | which params recoverable | E13E-15 |
| 18 Simulator pretraining | L44694–44704 | beyond real-only + randomized-sim controls | E13E-16 |
| 19 FlavorTwin prior | L44706–44716 | cultural/substitution prior improves ranking w/o hurting sensory/chemical validity | E13E-17 |
| 20 Historical RAG | L44718–44728 | structured historical evidence improves explanations w/ citation precision + abstention | E13E-18 |
| 21 Process evolution | L44730–44740 | technique vs ingredient co-use for identity/forecast | "Dated process-event corpora; ingredient-only vs process-only vs combined" — NO dedicated E13E experiment |
| 22 Source-domain bias | L44742–44752 | drift explained by source composition | "Matched/resampled analyses plus hierarchical source random effects" — NO dedicated E13E experiment |
- Index cross-check (`docs/SSOT_INDEX.md` L30): RQ13E-01, 06, 21, 22 have no E13E back-reference → orphan RQs without a runnable protocol (see §9).

### 3.2 Experiment registry (§277, L44757–45208) — 18 experiments
Common: `SEEDS = [20261006, 20261007, 20261008, 20261009, 20261010]` (L44762) "unless a later power/variance analysis justifies expansion"; group/source-aware resampling (L44765); every experiment has identical boilerplate Controls ("freeze source/duplicate groups, recipe-size definition, ingredient canonicalization and relevant frequency/category/coverage confounds before model fitting", e.g. L44775) and identical Required artifact ("frozen config + seed manifest + source/split manifest + result table + error/limitation note", e.g. L44792).

| ID | Lines | RQ | H0 / H1 (short) | Data | Metrics | Compute | Decision gate (quoted) |
|---|---|---|---|---|---|---|---|
| E13E-01 | L44768–44792 | 02 | different families vs common family | several cuisine×era/source corpora, canonical IDs, **source IDs mandatory** | MLE LL, KS GOF, LR/non-nested, bootstrap CI, normalized curve distance; `bootstrap_gof(B=2000)` (L44787) | CPU min–h | "Do not claim Zipf/power-law universality unless GOF is acceptable and alternatives are not materially better." (L44780) |
| E13E-02 | L44794–44816 | 03 | cannot / can reproduce | publication parameters + compatible cookbook stats if licensed | rank-freq distance, recipe size, ingredient degree, total-fitness/founder descriptors | CPU cheap | "No extension model may be called 'improved copy–mutate' until this passes or the reproduction failure is documented." (L44806) |
| E13E-03 | L44818–44841 | 04 | variants don't / do improve over random-fitness | Indian regional corpus compatible with published definitions; mappings/licence verified | rank-freq, size dist, category composition, ΔN_s where coverage permits | CPU | "Keep only the variant that improves held-out / replicated target statistics; preserve negative result." (L44830) |
| E13E-04 | L44843–44866 | 12 | effect disappears / robust under stronger nulls | recipes + canonical ingredients + compound sets + category + source/era | ΔN_s, empirical p, standardized effect, CI, mapped-ingredient coverage; BH-FDR | CPU moderate | "No cultural pairing mechanism claim if effect depends only on the weakest null or low compound coverage." (L44855) |
| E13E-05 | L44868–44891 | 07 | ingredient-only as good / extra view helps | expert/curated same-dish/variant/different pairs with source/duplicate family IDs | AUROC, AUPRC, macro-F1 at calibrated threshold, Brier/ECE, hard-negative error; grouped CV by `dish_source_family` (L44884); calibration split separate from test | CPU / 1 GPU if learned | "No universal identity threshold until calibration is stable across sources/dish categories." (L44880) |
| E13E-06 | L44893–44915 | 08 | novelty ≈ rarity/source / aligns with experts | pairs/ratings with expert novelty labels; reference corpus frozen by time/source (`freeze_reference_corpus(before_time=t0)` L44908) | Spearman/Kendall, pairwise accuracy, partial associations | CPU | "If novelty collapses to rarity, keep descriptive components rather than headline score." (L44905) |
| E13E-07 | L44917–44939 | 09 | no / model-dependent dose response | real seed recipes + calibrated identity model + simulator | p_same, d_I, d_process, ΔN_s, cuisine-classifier score, invalid mutation rate | CPU | "Use curves as sensitivity analysis; do not promote a fixed 'new recipe' threshold from simulator alone." (L44929) |
| E13E-08 | L44941–44962 | 10 | no gain / soft mutation better | quantity-grounded variant pairs/substitutions | quantity distance, weighted pairing, identity prob, target similarity; γ grid `np.linspace(1,0,21)` (L44956) | CPU | "Do not keep M5 if quantity coverage or conversion uncertainty makes results unstable." (L44953) |
| E13E-09 | L44964–44985 | 11 | no / selected higher-order help | large deduplicated corpus with source/cuisine groups | held-out log-loss, NDCG/Recall masked ingredient, calibration, params/runtime; grouped CV, corrected paired tests | CPU→1 GPU | "Stop at lowest interaction order within uncertainty of best result." (L44976) |
| E13E-10 | L44987–45008 | 13 | no / chronological proximity predicts similarity | dated source sequences with canonical ingredients + source IDs | distance vs lag, neighbour−non-neighbour, autocorrelation; permutation within strata, source-block bootstrap, mixed effects | CPU | "Do not claim cultural transmission if result vanishes after source/genre controls." (L44999) |
| E13E-11 | L45010–45033 | 05/13 | no / beats persistence | **≥3 chronological bins or rolling windows with sufficient source diversity** (L45015) | JSD/EMD, top-k adoption recall, Brier/log-loss, calibration; rolling-origin | CPU | "Historical model must beat persistence; otherwise retain descriptive analysis only." (L45022) |
| E13E-12 | L45035–45057 | 14 | no / contact helps | dated cuisine-region panels + defensible contact proxies | log-loss/Brier, adoption Recall@K, calibration, coefficient uncertainty; region-held-out + time-held-out; edge permutation | CPU/1 GPU | "Do not infer historical diffusion from latent contact alone without source corroboration." (L45047) |
| E13E-13 | L45059–45081 | 15 | no / reproducible change | **only historically verified introduction events** + dated panels | pre/post slope, hazard, event-study coefficients, CI; placebo dates | CPU | "Event becomes a model input only if source support and robustness are adequate." (L45071) |
| E13E-14 | L45083–45104 | 16 | mean-field loses / matches | dated ingredient-frequency panels | forecast error, adoption/retention error, runtime, identifiability | CPU | "Use ODE only for aggregate targets where it earns adequacy; never as recipe-chemistry model." (L45095) |
| E13E-15 | L45106–45131 | 17 | not / subset recoverable | synthetic θ known; real only after pass; `sample_prior(n=5000)` (L45121) | RMSE, bias, coverage, SBC uniformity, contraction, PPC | CPU ABC; 1 GPU NPE | "Real-data parameter interpretation forbidden for parameters failing synthetic recovery." (L45118) |
| E13E-16 | L45133–45156 | 18 | no gain / gain | real train/cal/test + simulator data "generated only from training-fitted parameters" (L45138) | downstream metric, Brier/ECE, source/cuisine/time OOD, compute | 1 GPU | "Drop simulator pretraining if gain is within uncertainty or disappears against matched synthetic control." (L45145) |
| E13E-17 | L45158–45180 | 19 | no / prior helps w/o validity loss | known substitution/context cases with recipe role, optional era/cuisine | Recall@K/NDCG, invalid substitution rate, chemical/sensory evidence score, calibration | CPU/1 GPU | "Prior remains optional and is removed if it merely rewards popularity or harms evidence-grounded similarity." (L45170) |
| E13E-18 | L45182–45204 | 20 | adds verbosity/unsupported / improves | gold cultural-history QA with source spans + date uncertainty | citation P/R, unsupported-claim rate, correctness, abstention calibration; paired query bootstrap | 1 GPU/API | "Historical context enters Level-16 only if citation/support metrics improve; otherwise keep separate research interface." (L45194) |

### 3.3 Recommended minimal chain (SSOT)
- "These are a menu governed by dependencies and gates, not forty mandatory experiments for one semester." (L45617). Semester chain: E13E-01 + E13E-02/03 + E13E-04 + E13E-05 + E13E-10/11 "or a narrower simulator/identity paper" (L45621–45629).
- PLAN AH12 course minimum: rank-frequency/null fit → one Kinouchi/Jain reproduction → one source-safe null comparison (PLAN L2947–2951).
- PLAN B03 already absorbs SX-03-03 degree-preserving null lattice, SX-03-04 FlavorDB vs FlavorDB2 coverage sensitivity, SX-03-05 Kinouchi exact reproduction "shared with B15" (PLAN L303–310). B14 SX-14-03 identity calibration "shared with E13E-05" (PLAN L492).

---

## 4. Gates, promotion and stop rules (exact, with line numbers)

### 4.1 G13E-01…15 (§278.5, L45274–45292) — quoted pass criteria / fail actions
| Gate | Line | Question | Pass criterion | Evidence | If failed |
|---|---|---|---|---|---|
| G13E-01 DATA | L45278 | Are historical dates/sources usable? | "sufficient dated, source-diverse corpus for stated RQ" | audit table + date/source coverage | "descriptive only / acquire data" |
| G13E-02 LINEAGE | L45279 | Is duplicate/edition leakage controlled? | "lineage groups frozen before split" | duplicate/lineage audit | "no temporal forecast claim" |
| G13E-03 RANK | L45280 | Is power-law/Zipf claim justified? | "GOF + alternative comparison supports it" | E13E-01 | "report best-fitting alternative/no universality" |
| G13E-04 REPRO-K | L45281 | Kinouchi reproduction credible? | "reference summaries reproduced/documented" | E13E-02 | "debug or document non-reproduction" |
| G13E-05 REPRO-I | L45282 | Indian baselines reproduced? | "published-style baseline behavior recovered" | E13E-03 | "do not claim extension improvement" |
| G13E-06 NULL | L45283 | Pairing survives strong nulls? | "effect robust to required matched controls" | E13E-04 | "narrow/drop pairing claim" |
| G13E-07 ID | L45284 | Identity calibrated? | "stable source-held-out discrimination + calibration" | E13E-05 | "keep descriptive distances only" |
| G13E-08 NOV | L45285 | Novelty more than rarity? | "expert-aligned signal after rarity/source controls" | E13E-06 | "report component vector only" |
| G13E-09 QTY | L45286 | Quantity coverage adequate for soft mutation? | "declared coverage/uncertainty threshold from data audit" | quantity audit | "defer M5" |
| G13E-10 TEMP | L45287 | Evolution beats persistence? | "future-era gain beyond uncertainty" | E13E-11 | "keep historical description, not forecast model" |
| G13E-11 CONTACT | L45288 | Contact helps? | "held-out gain vs internal prevalence + shuffled-contact null" | E13E-12 | "drop contact mechanism" |
| G13E-12 SBI | L45289 | Parameters recoverable? | "synthetic recovery + coverage passes" | E13E-15 | "no real mechanism parameter claims" |
| G13E-13 PRETRAIN | L45290 | Simulator pretraining helps real data? | "real held-out gain vs real-only + random-sim control" | E13E-16 | "use simulator only for stress tests" |
| G13E-14 FT | L45291 | Cultural prior improves FlavorTwin? | "ranking gain without evidence-quality loss" | E13E-17 | "keep FlavorTwin unchanged" |
| G13E-15 RAG-HIST | L45292 | Historical retrieval improves evidence? | "citation/UCR gain with calibrated abstention" | E13E-18 | "keep historical module separate" |
- NOTE: No G13E gate has a numeric threshold. Every pass criterion is qualitative ("sufficient", "stable", "beyond uncertainty", "declared … threshold from data audit"). The only numbers in L13E are procedural: 5 seeds (L44762), B=2000 GOF bootstrap (L44787), n=5000 prior draws (L45121), 21-point γ grid (L44956), one-SE rule (L44982). Thresholds must be pre-registered per experiment before running (brief law "no post-hoc gate weakening"). → UNDERSPECIFIED (see §9).
- G13E-09's evidence "quantity audit" maps to no E13E experiment.
- Index anomaly: `docs/SSOT_INDEX.md` L34/L36 maps E13E-01→45280, E13E-02→45281 etc. (i.e. gate-row mentions); G13E-ids appear exactly once each (L45278–45292). No other gate definitions exist in PART XIII.

### 4.2 Rung gates (M0–M8) and stop rule — see §2.1 (L43662, L43676, L43688, L43694, L43706, L43718, L43724, L43736, L43742, L43748).

### 4.3 Other promotion/stop rules in the body
- Complexity promotion: "complexity can only be promoted if a simpler rung fails on held-out historical data." (L43238).
- Learned process encoder only if it beats explicit edit-distance baselines (L43458).
- Higher-order: promote k+1 only with held-out gain after regularization/complexity penalty (L43874).
- NPE promotion 4 conditions (L44295–44300).
- Simulator pretraining promotion gate (L44364–44372) + randomized-simulator control (L44360).
- Synthetic recovery gate: "If known parameters cannot be recovered from ideal simulator output, do not interpret real-data estimates mechanistically." (L44259).
- RQ13E-01 scope rule: L13E remains "only if they improve a predeclared null, prior, split, identity or forecasting task" (L44496) — this is effectively the **kill switch for the whole track**.
- Statistical principles (L45213–45222): effect sizes; CIs/bootstrap; cluster by source; BH-FDR; "Keep one final test set sealed for any learned/calibrated component"; separate tuning/calibration/test; multiple seeds; report negatives; empirical null tests; "Do not treat millions of recipes from one source as millions of independent historical sources." (L45222).
- Multiple comparisons (L45240–45243): predeclare primary RQs/metrics; FDR on exploratory panels; raw effects + CIs alongside q; "do not turn a large-N tiny effect into a substantive cultural claim."
- Phase E6 inference "Only after E2/E5 simulator adequacy" (L45411).
- §279.3 DROP list (L45521–45528): one universal fitness scalar; fixed identity % threshold; global strict phylogenetic tree; "Zipf law" from straight log–log line; food-pairing as single law; historical popularity as sensory equivalence; good simulator fit as causal history; synthetic recipes as historical evidence.
- §279.3 POSTPONE UNTIL DATA GATES PASS (L45509–45517): quantity attenuation; contact/migration causal claims; exogenous introduction event studies; replicator–mutator fitting; ABC/SBI; neural generator; simulator pretraining; FlavorTwin cultural-prior integration; historical RAG integration.
- FlavorTwin rule: separable prior P_culture(candidate | source, era, cuisine, role) "only after E13E-17. It may rerank; it may not redefine the target flavor space." (L45610–45613).

---

## 5. Data requirements and named sources (licence notes)

### 5.1 SSOT-named sources (§275.2 L44408–44420; §261; refs L45656–45696)
| Source | SSOT role / decision | SSOT licence note | Repo status (verified) |
|---|---|---|---|
| RecipeDB (~118k, weak dating) | KEEP cross-sectional, "not historical truth" (L44412; L43170) | "paper is CC BY; database-use terms still audit" | `registry/sources/external_data_source_registry.csv` XS-D02 Foodoscope RecipeDB/FlavorDB: API key "not held"; licence "ASSUMED per D-015 (Bagler); written confirmation pending" |
| Recipe1M+ (>1M, web-era) | OPTIONAL representation/pretraining; not historical (L44413) | access/licence audit | XS-A03: request form, terms UNVERIFIED (paper CC BY-NC-SA per registry; dataset terms not read) |
| Food.com interactions | substitutions/preferences/reviews; dated web activity 2000s–2010s (L44414) | exact licence [VERIFY]; redistribution [VERIFY] | `data/external/foodcom/recipes.parquet` 522,517 rows; Kaggle uploader-declared CC0, "uploader authority … NOT verified; keep DERIVED/analysis use" (PROVENANCE.json); **reviews NOT downloaded** ("reviews_not_downloaded": true) → substitution-behaviour role (Teng-style) has no data. Columns present (parquet footer): RecipeId, Name, AuthorId, AuthorName, DatePublished, RecipeCategory, Keywords, RecipeIngredientParts, RecipeIngredientQuantities, RecipeInstructions, ReviewCount, AggregatedRating, CookTime, PrepTime, RecipeServings, RecipeYield, nutrition fields |
| Historical public-domain cookbooks | "CORE historical route" (L44415) | "often public domain, scan/OCR terms vary" | Project Gutenberg: 346 books downloaded, 337 with ≥1 kept recipe, 73,778–73,955 segments (`reports/gutenberg_v1.md`; base count 73,955 in `reports/step07/step07h_full_recipe_base_report.md` L9). Licence "Public domain in the USA" VERIFIED per SRC rows (`registry/recipe_source_usage_registry_v1.csv`: PUBLIC_OPEN, training/redistribution YES; "non-US status not assessed"). Segmentation heuristic, ~80–85% precision on 30-sample (DECISIONS D-012); "ingredient list = mentions" (REC notes); ingredient_lines_per_recipe = 0 at all quantiles (`final_recipe_database_statistics.md` L398–406). English only. |
| RELISH historical recipe dataset (2026) | "HIGH-PRIORITY AUDIT" (L44416) | Zenodo/project licence [VERIFY] | NOT in repo, NOT in external source registry (grep: no hit) |
| Open Recipe Archive (>50k, many countries) | CANDIDATE, not automatic gold (L44417) | community; licence/source QA required | NOT in repo/registry |
| Dutch historical recipe-trends corpus | CANDIDATE benchmark (L44418) | repository licence/source audit | NOT in repo/registry; SSOT reference R13E-19 unnamed |
| FlavorDB2 (25,595 molecules; 2,254 linked to 936 natural ingredients, 34 categories) | KEEP with coverage controls (L44419; L43198) | database terms audit | via XS-D02 (key not held). PLAN B03 SX-03-04 FlavorDB vs FlavorDB2 coverage sensitivity (PLAN L308). Project ING = 5,387 rows (`step07h_full_recipe_base_report.md` L25) — mapped fraction unknown (UNVERIFIED) |
| Ahn/Jain pairing datasets | CORE reproduction (L44420) | paper/SI licence | NOT in repo |
| Teng et al. 2012 substitution networks | distinct signal (L43091–43107) | — | no data in repo |
| Transylvania multiethnic network study 2026 (Foods 15(6):1006) | methodological precedent (L43202; R13E-18 L45692) | — | — |
| Historical food-mobility/trade scholarship | required to validate any contact/introduction claim (R13E-20 L45696; L44146) | — | none |
- External landscape note (`reports/sources/external_data_landscape_v1.md` L30): "L13E cultural: XiaChuFang, endangered recipes (later)"; Kaggle multi-dataset row XS-A09 tagged ROBUSTNESS_TEST;L13E_CULTURAL with licences UNVERIFIED. These are NOT SSOT-named sources.
- Literature ledger required (§261.18 item 10, L43273): fields `claim_id, source, exact_span/table, evidence_class, verified_date, notes`.
- Audit backlog before manuscript (§261.18 L43264–43273, 10 items) — all OPEN in repo.

### 5.2 Current temporal metadata reality (verified in repo)
- `reports/step07i/final_recipe_database_statistics.md` L304–330: `era_known_pct` 93.03; distribution e.g. PUBLISHED_2007 70,204 … UNKNOWN 26,373; AUTHOR_BORN_1850s 21,673; AUTHOR_BORN_1800s 19,082; AUTHOR_BORN_1750s 5,663.
- Derivation (`tools/step07i_consensus.py` L38–60, `era_map`): Gutenberg era = **author birth year** parsed from PG catalog `Authors` field (regex `(\d{4})\??-`) bucketed to 50-year bins; Food.com era = `DatePublished` year (web upload). PG catalog column `Issued` is the eBook release date (e.g. #930 *The Cook's Decameron* Issued 1997-06-01; `data/raw/gutenberg/cookbook_selection.csv` row 2) — NOT a publication date. `ledgers/data/SRC.jsonl` Gutenberg rows have authors/title/licence but **no publication or edition year** field.
- Consequences: (a) AUTHOR_BORN_* is not in the SSOT `date_basis` enum (L44040) — closest is `inferred` with low `date_confidence`; it is a proxy for t_document at best, never t_recipe-origin (L44053–44063). (b) The Gutenberg set includes at least one evidently modern book ("The Perdue Chicken Cookbook (Project Gutenberg #1979)", SRC-000146, author Mitzi Perdue) — "Gutenberg = historical" is false as a blanket rule [publication year UNVERIFIED]. (c) Food.com DatePublished is a web-era t_document (1999–2019 range in stats) on ONE platform → source diversity for E13E-11 ("sufficient source diversity", L45015) fails unless AuthorId is used as cluster and the claim is restricted to platform drift.
- Cross-source title overlap (`reports/step07/step07h_full_recipe_base_audit.json` L173–186): 6,249 cross-source same-title groups incl. FOODCOM+GUTENBERG_SEGMENT 3,431; but `cross_source_exact_groups` = 0 (`final_recipe_database_statistics.md` L93). → web re-posts of historical recipes are a plausible §270.7 leakage channel; must be resolved via near-dup/lineage groups before any web-vs-historical claim (L44112).
- Cuisine labels: explicit_cuisine_labelled_pct 9.81; Food.com 0.0; Gutenberg 69.63 (from PG catalog subjects, i.e. book-level, not recipe-level); top: American 35,516, English 7,640, British 3,411, French 3,382 … Indian 501 (L279–302). `representativeness_statement`: "NOT globally representative … no claim of cultural coverage is made" (L426). → E13E-03 (Indian regional, 8 cuisines) has no compatible local data (501 "Indian" labels); requires RecipeDB/Jain–Bagler data (key not held, licence ASSUMED).
- Quantities: Food.com and BBC `has_quantities` ≈0.5% in a coverage table (`final_recipe_database_statistics.md` L220–226; table semantics UNVERIFIED — may be a "missing" fraction table); unit_coverage_pct_of_numeric 2.55 (L767). G13E-09 QTY therefore likely fails for M5/E13E-08 until Step 07/20 quantity grounding improves. [interpretation of that table UNVERIFIED]

### 5.3 Data-role verdict per G13E-01 (my assessment, not SSOT text)
- Cross-sectional (E13E-01 per-source rank-frequency, E13E-04 pairing nulls, E13E-09 co-occurrence): feasible on local corpus once canonical ING IDs are frozen (07H-R) — but pairing needs FlavorDB/FlavorDB2 compound sets (access pending).
- Historical evolution (E13E-10/11/12/13/14): G13E-01 likely FAIL on current data (no reliable publication years, English-only, 337 books, heuristic segmentation). Requires the SSOT DO FIRST item 1 "Audit 2–4 dated historical corpora and licences" (L45497).
- Web-era platform drift (Food.com 1999–2019): possible narrow "descriptive drift" study with AuthorId clustering; must be labelled as platform drift, not cultural evolution (L44112, RISK-E1).
- Substitution behaviour (E13E-17): no data (reviews not downloaded).
- Historical RAG (E13E-18): needs a gold cultural-history QA set — none exists.

---

## 6. Dependencies on other levels / steps

- SSOT dependency graph (§278.8, L45427–45447): semantic canonicalization/provenance → historical source + date audit → classical nulls/rank-frequency/drift → exact copy–mutate reproductions → identity/novelty calibration → controlled evolution extensions → temporal/contact forecasting → synthetic parameter recovery → OPTIONAL SBI/simulator pretraining → OPTIONAL FlavorTwin/RAG integration.
- Phased roadmap (§278.7 L45356–45424): E0 freeze definitions + audit data (notation, historical schema, source/date/licence audit, duplicate/edition lineage plan, exact recipe-identity annotation handbook) → E1 classical descriptive (rank-freq, source-balanced drift, M0 lattice, itemset/network baselines, flavor coverage audit) → E2 reproduction (Kinouchi M1, Jain–Bagler M1/M3/add-delete, reproduction decision record) → E3 identity/novelty (gold pair labels, E13E-05/06) → E4 controlled extensions (L/K, category, context fitness, soft attenuation only if quantity gate passes, higher-order) → E5 time/contact (forecast, diffusion, selected introduction events, process/technology evolution) → E6 inference (only after E2/E5 adequacy: ABC, synthetic recovery, neural SBI only if needed) → E7 integration (pretraining gate, FlavorTwin prior ablation, historical RAG).
- Hard upstream inputs (from §262.1 L43281–43288 + experiments):
  - L16 / Steps 07, 07I, 16–17: canonical ingredient IDs (I), aliases incl. era/language aliases (RISK-E3 L45309), quantities (q_R) with masks, roles (role_R), canonical process events (process_R), flow graph (d_G), provenance & source metadata, duplicate/lineage groups.
  - L12 / Steps 12 (structured DB evidence), 35: flavor compound sets C_i WITH coverage metadata (compound-set size, source count per ingredient), optional z_i.
  - L13 / Step 35: z_R, z_C; the L13 gate §193.8 (G13-0..4) via PLAN B14 (PLAN L495).
  - L14: process labels/conditions only as descriptors.
  - L15: none required (optional validated effects).
- Downstream consumers of L13E outputs (allowed, L42971–42981): Step 35 (cuisine/recipe views, cultural similarity SIM-13/14/15 per `reports/h_state/ssot15_state_program_inventory.md` L32), Step 36 RAG (historical evidence packets, G13E-15) and FlavorTwin (optional prior, G13E-14), core split registry (identity calibration, lineage groups; G13E-02/07), L12 evaluation holdouts (source/time/geography).
- PLAN dependency: B15 ← B02, B03, B14 (PLAN L244). Tension: SSOT puts identity calibration inside L13E (E13E-05, Phase E3) while PLAN puts it in B14 SX-14-03 "shared with E13E-05" and makes B15 depend on B14 — i.e. B14's gate and B15's E3 share one experiment; must be owned once (recommend: owned by the identity follow-up of 07I-R / Step 19 human-label queue, consumed by both).
- Human dependency: expert labels for identity (E13E-05) and novelty (E13E-06), historians/primary sources for introduction events (E13E-13, L44146), source-grounded cultural-history QA gold (E13E-18). PLAN role "Historical/Cultural Researcher — L13E, date/source lineage, cultural evidence" (PLAN L2117) — no named person in repo (UNVERIFIED who).
- Licence dependency: H2 approval items for Food.com/TASTEset (`DECISIONS.md` L134 area), RecipeDB/FlavorDB written confirmation (D-015).
- Compute: C0 CPU for all of E0–E5; no dependency on GPU/A100.

---

## 7. Risks / failure modes

SSOT risk register (§278.6, L45294–45355), verbatim names with mitigations:
- RISK-E1 source/editorial bias — "Cookbooks encode editorial selection, not population consumption." Mitigation: source-aware inference, source-level bootstrap, domain-matched comparisons (L45296–45299).
- RISK-E2 false historical precision — date intervals/evidence classes; sensitivity (L45301–45304). **Live in repo**: AUTHOR_BORN_* era buckets (tools/step07i_consensus.py L53).
- RISK-E3 ontology drift — preserve raw terms, era/language aliases, ambiguity states; human audit high-impact terms (L45306–45309). Live: `reports/gutenberg_v1.md` lists historic tool phrases not in TOOL vocab (soup-kettle, chaffendish, gallipot …).
- RISK-E4 modern quantity normalization imposed on historical measures — historical-unit provenance and conversion uncertainty; "do not force modern FDC portions" (L45311–45314). Directly constrains Step 07/20 CQPO on Gutenberg text.
- RISK-E5 flavor coverage bias — coverage-matched controls, source-count audits, non-chemical co-use baselines (L45316–45319).
- RISK-E6 popularity/fitness circularity — prospective/held-out targets; anti-circularity gate (L45321–45324). Note: there is NO G13E gate named for circularity; RQ13E-06 has no E13E experiment (gap).
- RISK-E7 simulator non-identifiability (L45326–45329).
- RISK-E8 phylogenetic overclaim — reticulate by default (L45331–45334).
- RISK-E9 cultural essentialism — language policy; within-cuisine heterogeneity (L45336–45339).
- RISK-E10 simulator pretraining shortcut — randomized-simulator control + real OOD (L45341–45344).
- RISK-E11 FlavorTwin contamination — separable prior, ablate, cap/regularize, preserve base ranking (L45346–45349).
- RISK-E12 historical RAG hallucination — claim-level sources/date intervals/conflict packets/abstention (L45351–45354).

Additional project-specific risks (my analysis):
- R-A Scope creep / critical-path capture: the 22 RQs + 18 experiments (L45617) compete for the same human hours (Kush/Parv) needed for Gold/identity labels; SSOT §279.8 offers L13E as candidate "first paper-grade" thread (L45643), which, if chosen, inverts priorities. Requires an explicit human decision (record in DECISIONS).
- R-B Clock conflation in code: Food.com has `CookTime/PrepTime` (tau) and `DatePublished` (t) side by side; a generic `time`/`date` column name in recipe_base or state schema would violate L43008/L44233.
- R-C Synthetic-history contamination of SIMULATION memory: Step 28 "E7 synthetic prior" (chemistry) and L13E copy–mutate simulator outputs both live in "simulation memory"; without a `clock`/`domain` tag they could be mixed. Also naming collision "E7" (Step 28 synthetic prior) vs "Phase E7" (L13E integration, L45417).
- R-D Leakage: web re-posts of historical recipes (3,431 FOODCOM+GUTENBERG title groups) and edition reprints across PG books → temporal forecast memorization (L44097) unless lineage groups exist (G13E-02).
- R-E Identity gold anchoring: the 07I 400-pair packet hides score/stratum (preregistration L33) — good; but the same labels feeding both duplicate thresholds (core) and E13E-05 (research) require a sealed test subset (L45217).
- R-F Reproduction impossibility: Kinouchi's original cookbook statistics and Jain–Bagler data may be unavailable/licence-restricted → G13E-04/05 may end as "document non-reproduction" (allowed by L43676, L44806).
- R-G Coverage: FlavorDB2 maps 936 natural ingredients (L43198); project ING = 5,387 → large unmapped fraction expected; E13E-04 may be dominated by low-coverage ingredients (gate L44855).
- R-H Single-language corpus: English-only base (language en 612,782; `final_recipe_database_statistics.md` L270–272) → cross-cuisine claims are confounded by translation/anglophone selection (bias ledger L44464).

---

## 8. MAPPING TO THE 36-STEP SPINE (brief §9)

(Reconstruction: the 36-step card text is missing; content below derives from SSOT §§259–279, PLAN B03/B14/B15/AH12/AX6/AY8/AZ4, and repo state. "Requires" = what this L13E material obliges that step to provide or respect.)

**01 Freeze project authority** — Record: L13E = parallel extension of L13, non-blocking (L42927, L45449, L45589); SSOT §279.8 choice of "first paper-grade execution" among 4 threads (L45639–45644) is an OPEN human decision → add a DECISIONS entry ("L13E = optional Lane 35-E; not primary deliverable unless decided"). PLAN B15/AH12 (PLAN L497–501, L2941–2953) as implementation authority. Output: authority row in `registry/plan_authority_map_v1.csv` for PART XIII. Gate: none beyond recorded decision.

**02 Audit implementation state** — L13E status = NOT STARTED in repo (`src/culinarystate/classical/` empty; max_plan_consensus L31 "not started"); A2/A3 outside repo, UNVERIFIED (SX-03-05 PARTIAL). Partial assets: 07I-R identity tables (duplicate_group, recipe_family, dish_family_candidates 46,697), 400-pair packet unlabeled, era proxy map. Output: status rows for RQ13E-01..22, E13E-01..18, G13E-01..15 (PLAN L281–282 says `experiments.csv`/`gates.csv` must be seeded with all of them. Verified: `registry/` has no experiments.csv/gates.csv, and `registry/ssot15_state_experiment_map.csv` has only one line mentioning 13E-family ids (via SX-03-05/SX-14-03 "shared with" text); no RQ13E/E13E/G13E rows are registered → the registry gap is real).

**03 Freeze state semantics** — Must encode the two-clock law: `tau` (process, s–h) vs `t` (historical, years–centuries) (L43001–43005; L44231–44233; L45546–45560). State schema must name process time fields unambiguously (`tau_*`, `process_time_s`) and keep any historical date out of state vectors z_{i,τ}. "Never write a single state equation that silently mixes them." (L43008). Gate addition (proposed): schema validator rejects a generic `time` field without clock tag.

**04 Freeze evidence / provenance / similarity contracts** — Requires: (a) a distinct evidence class `HISTORICAL_CULTURAL` (L42941, L42980, L45473) that cannot be cited as process-chemistry evidence; (b) `SYNTHETIC_HISTORY` class that may never enter evidence ledger (L44383); (c) SSOT PART XIII evidence labels [ESTABLISHED]/[REPRODUCE]/[HYPOTHESIS]/[OPEN]/[PROPOSED]/[USER-REPORTED]/[VERIFY] (L43024–43030) mapped to project claim-status vocabulary; (d) similarity contract: recipe identity = calibrated p_same over separately stored views d_I,d_Q,d_role,d_P,d_G, no a-priori scalar weights, no cosine-as-probability (L43408–43470); novelty ≠ identity ≠ rarity (L43499–43524); cultural/co-occurrence similarity (SIM-13) separate from flavour/structural similarity (L45488–45489); (e) date-evidence contract `e_date`/`date_basis`/`d_low,d_high` (L43358–43359, L44040). Metric hooks: AUPRC/AUROC + Brier/ECE for identity (L45230).

**05 Normalize EVD** — Requirement is negative: no historical/cultural or simulator-derived row may enter EVD (L44383; PLAN L4443). Optional: EVD `source_type` vocabulary should include a value that lets future historical evidence be excluded by filter rather than by convention.

**06 Freeze source acquisition manifest** — If L13E is retained at all: add audit entries (not downloads) for RELISH, Open Recipe Archive, Dutch historical trends, Ahn/Jain datasets/SI, RecipeDB terms, FlavorDB2 terms, Food.com reviews terms, Recipe1M+ terms (L44408–44420; §261.18 items 5–7 L43268–43270). Fields per source: publication/edition year availability, date precision, language, translation, OCR quality, lineage, licence, redistribution_allowed, bias-ledger items (L44452–44466; PLAN AX6 L4435–4441). SSOT DO FIRST #1: "Audit 2–4 dated historical corpora and licences." (L45497). Gate = G13E-01 DATA input (audit table + date/source coverage, L45278). Current ES-1.2 64-source manifest contains none of these (UNVERIFIED in detail; grep found no RELISH/ORA). Parallel, non-blocking.

**07 Condition & measurement normalization (incl. 07H-R base, 07I-R identity)** — Requires: (a) historical-unit provenance + conversion uncertainty, never forcing modern FDC portions (RISK-E4 L45311–45314) → quantity rows carry `unit_system_era`/`conversion_basis`/interval; (b) missing quantities masked not zero (L43434); (c) 07I-R: lineage/near-dup groups frozen BEFORE any split (G13E-02 L45279; L44093, L44097); identity calibration on the 400-pair packet → E13E-05 (shared SX-14-03); report d_Q log-ratio baseline alongside cosine (max_plan_consensus row 8); no threshold until calibration stable (L44880); (d) replace/annotate the AUTHOR_BORN_* era proxy with `date_basis=inferred`, `date_confidence=low`, and keep `t_document` separate from `t_recipe_origin` (L44053–44063). Augment identity packet with era/edition and different-author strata if historical identity is ever claimed (L43476–43483).

**08 Scientific source lineage** — Not a consumer of L13E. Two touch-points: (a) the L13E literature ledger (`claim_id, source, exact_span/table, evidence_class, verified_date, notes`, L43273) can reuse Step-08 SOURCE→DOCUMENT lineage machinery; (b) conceptually parallel "edition/derivative lineage" for cookbooks (L44095–44097) — but this belongs to recipe identity (07I/16), NOT to the scientific STUDY lineage. Do not let Step 08 absorb cookbook lineage; keep planes separate. L13E imposes no requirement that would change Step 08 start.

**09 Evidence extraction & verification machinery** — Only for E13E-18 (historical RAG): claim-level extraction with source spans and date intervals (L45187, RISK-E12 L45354). Defer; no requirement now.

**10–11 Mechanism pilot / Wave-1 evidence** — No L13E requirement (L42985–42989: kinetics/pathways/pH/concentration not influenced). Firewall: historical frequency never used as mechanism evidence (L43286).

**12 Structured database evidence** — FlavorDB/FlavorDB2 ingredient→compound sets must be captured WITH coverage metadata: per-ingredient compound-set size, number of underlying sources per ingredient, mapped/unmapped status per canonical ING, database version (L43283, L43990–43997, RISK-E5). Output consumed by E13E-04 / B03 SX-03-04. Metric: "mapped-ingredient coverage" (L44852); report "mapped fraction rather than citing database size alone" (L43270).

**13 Large literature discovery corpus** — Optional: food-history scholarship for introduction events / contact claims (L43271, L44146, R13E-20 L45696) and recipe-genealogy literature (L43272). Low priority; must be tagged HISTORICAL_CULTURAL class, not process evidence.

**14 Coverage-driven evidence growth** — No requirement.

**15 Freeze DATA-EVIDENCE v1** — Must exclude historical/cultural and synthetic-history rows; `DATA-HISTORICAL` is a separate release (PLAN AX7 L4460). Gate check: zero rows with historical/synthetic evidence class in DATA-EVIDENCE.

**16 Instruction semantic schema** — Requires the §275.3 `historical:` block (22 fields, L44424–44448) as nullable typed fields (or PLAN AY8 `HIST-` records, PLAN L4581–4595); canonical process event sequence (d_P, L43446–43450); culinary roles per ingredient (d_role); flow-graph structure (d_G); `canonical_dish_name`, `variant_group_id`, `lineage_group_id`; `ocr_quality`, `extraction_quality`; raw historical terms + era/language aliases + ambiguity state (RISK-E3). Missing date must not invalidate a recipe (L43313).

**17 Instruction-level extraction** — Must produce, for historical text (Gutenberg), role labels and canonical process events with `extraction_quality`; preserve raw historic tool/process terms (gutenberg_v1 list). Enables RQ13E-21 process evolution (L44730–44740) and d_P for E13E-05. Process vocabulary must be versioned to detect "technology/process vocabulary drift" (L43218).

**18 Event-sourcing engine** — Provides d_G (recipe-state/flow graph distance, L43417) and process_R. No L13E-specific requirement beyond stable event IDs and clock tag (tau only).

**19 Gold state-trajectory pilot** — Human-label queue should include (separately sealed) identity pair labels (E13E-05) because they also gate core duplicate-safe splits (L42879). Gold must be split by duplicate/lineage family (L43487). Optional novelty labels (E13E-06) are NOT core — defer. IAA requirements for identity labels UNSPECIFIED in SSOT L13E (gap).

**20 Scale procedural semantic corpus** — Quantity coverage audit → G13E-09 QTY (L45286) decides M5/E13E-08; process events over dated subsets enable E13E-10 process arm (L44995). Sampling for Silver should stratify by source/era where the cultural paper is pursued (balancing variables L44476–44484).

**21–25 Mechanism intelligence** — L13E must NOT feed applicability, formula or parameter registries (L42985–42988, L43286). Step 24 formula/model registry: if the replicator–mutator ODE or copy–mutate simulators are registered anywhere, they need `clock=t_historical`, `domain=cultural`, and must be barred from mechanism applicability (L44215–44223, L45095).

**26–28 Controlled simulation** — Separate the two simulator families: food-process simulators (Step 26–28) vs cultural copy–mutate simulators (L13E). L13E simulators: synthetic truth recovery first (L44249–44259), never evidence (L44376–44383). Step 28 "E7 synthetic prior" naming must not collide with L13E "Phase E7". No requirement on Step 26–28 deliverables.

**29–34 Transition science** — No L13E input (L43286 "inferring kinetics from historical recipe frequency" forbidden). Historical date must not appear as a transition feature. Optional reuse: SSOT statistical principles (source-clustered bootstrap, sealed test, BH-FDR; L45213–45222) apply equally.

**35 Representation ladder (HOME of Lane 35-E)** — Inputs: canonical I, C_i with coverage, z_R/z_C, identity tables, historical block. Sub-steps (proposed, map to Phases E0–E7):
- 35E.0 (E0) notation/conversion table (L43361–43363), historical schema populated, source/date/licence audit, lineage plan, identity handbook (L45358–45366). Gate G13E-01, G13E-02.
- 35E.1 (E1) per-source rank-frequency with Clauset protocol (E13E-01; G13E-03); M0 null lattice incl. degree-preserving swaps (E13E-04; G13E-06; shared with B03 SX-03-03/04); itemset/co-occurrence baselines (E13E-09); flavor coverage audit; source-balanced descriptive drift (E13E-10 descriptive).
- 35E.2 (E2) Kinouchi exact (E13E-02; G13E-04), Jain–Bagler (E13E-03; G13E-05).
- 35E.3 (E3) identity/novelty (E13E-05 shared with SX-14-03 → G13E-07; E13E-06 → G13E-08).
- 35E.4–E6 POSTPONED per L45507–45517.
- Outputs consumable by core Step 35: cultural/co-occurrence similarity view with nulls, cuisine fingerprints as descriptive vectors (L44025), temporal views only where G13E-01 passes. Baselines: per §2.2. Metrics: §278.2 table (L45226–45236). Kill switch RQ13E-01 (L44496).

**36 Evidence compiler → CulinaryState-RAG → FlavorTwin** — E13E-18 historical-context RAG (G13E-15; separate evidence packet class; citation precision/UCR + abstention, L45191, L45236); E13E-17 FlavorTwin cultural prior P_culture(candidate | source, era, cuisine, role) as a separable reranker only (L45610–45613; G13E-14; RISK-E11). Evidence packet should reserve a `HISTORICAL_CONTEXT` section and a "disallowed claim" rule: historical statements cannot override process chemistry/current state (L42941). Both deferred until upstream gates pass (L45516–45517).

---

## 9. Contradictions, stale items, underspecified parts, open questions

### 9.1 Contradictions / internal tensions
1. **Ordering of identity calibration vs temporal work.** §278.8 puts identity/novelty calibration AFTER classical nulls and copy–mutate reproductions (L45436), but G13E-02 requires "lineage groups frozen before split" (L45279) and §270.6/270.7 require lineage groups before any temporal holdout (L44093, L44097); lineage groups depend on calibrated near-duplicate identity (L43487). So identity (at least near-dup/lineage) must precede E1 drift/E5 forecasting. Recommend: split E13E-05 into 05a near-dup/lineage calibration (Phase E0, also core) and 05b same-dish/variant multiview (Phase E3).
2. **PLAN B15 ← B14 vs SSOT parallelism.** PLAN L244 makes B15 depend on B14 (L13 representation), while SX-14-03 in B14 is "shared with E13E-05" (PLAN L492) — the same experiment is both a B14 gate input and a B15 phase. Needs single ownership.
3. **Fitness ownership.** PLAN B14 claims fitness representation (PLAN L486–488) while SSOT puts it in L13E §265 (L43538–43646). Not substantive but must be one owner.
4. **§279.5 vs §279.8.** §279.5 says L13E "should not delay the core project unless the user decides…" (L45589); §279.8 lists L13E as one of four candidates for "first paper-grade execution" (L45643). Not a contradiction but an open human decision that the plan must close.
5. **Symbol collision `M`.** §263 defines M as pool ratio (L43351) and §263.1 warns not to unify symbols (L43363), but §268.2 reuses M as vocabulary size in ρ_i=(r_i−1)/(M−1) (L43895). Also `C` used for compound set C_i (L43338) and contact/context C(t) (L43301–43304), while contact intensity is separately H_{cc'}(t) (L43353). Request notation fix (SSOT change request, PROPOSED_ONLY).
6. **date_basis enum mismatch.** §263 `e_date` ∈ {exact/edition/estimated/unknown} (L43359) vs §270.1 `date_basis` ∈ {exact_publication, edition, archive_estimate, first_attestation, inferred, unknown} (L44040). Two vocabularies for the same concept; repo uses neither (AUTHOR_BORN_*, PUBLISHED_YYYY).
7. **M1 gate tolerance vs "qualitative curves" fallback** (L43676) can be read as permitting a pass on visual qualitative match — tension with L43111 ("prohibits declaring 'Zipf law' solely from a visually linear rank plot"). Need a predeclared numeric tolerance.

### 9.2 Stale items
- [USER-REPORTED] label definition "not independently rerun by ChatGPT" (L43029) — authorship artefact; should read "not independently rerun in this project".
- §261.12 2024 recommender preprint (Palermo et al., arXiv:2406.15533, R13E-13 L45682) and §261.10 generative grammar (Bagler arXiv:2211.09059, R13E-11 L45678) flagged [VERIFY] — publication status unknown as of SSOT.
- R13E-05 (PLOS ONE 2015 e0122092) has no author list (L45666); R13E-12 lacks venue/authors (L45680); R13E-16 RELISH, R13E-17 Open Recipe Archive, R13E-19 Dutch trends lack any checkable identifier (L45688–45694).
- STATUS.md L15 cites ../A2, ../A3 (copy–mutate "624/624") — STATUS body stale (ctx) and those dirs are absent here → cannot count as E13E-02 progress.
- PLAN RS-14 item 8 "Replicating Zipf/Heaps/Menzerath analyses (Bagler 2026)" (PLAN L1030) — not mentioned in SSOT L13E body; source UNVERIFIED.

### 9.3 Underspecified
- No numeric thresholds in any G13E gate (§4.1). "Sufficient dated, source-diverse corpus" (G13E-01) needs minimum #sources, #eras, date precision; "stable" calibration (G13E-07) needs ECE bound and cross-source variance bound; G13E-09 "declared coverage/uncertainty threshold" undefined; G13E-10 "beyond uncertainty" needs CI rule (e.g. paired bootstrap CI excludes 0).
- RQ13E-06 (anti-circularity), RQ13E-21 (process evolution), RQ13E-22 (source-domain bias) have no E13E protocol; RQ13E-01 has none either (index L30 shows no E13E backlink for 01, 06, 21, 22).
- No IAA/annotation protocol for identity or novelty labels (who labels, how many, kappa target, adjudication) — §264.7 only "independent human/expert labels on a subset" (L43485).
- Sample sizes for identity gold / novelty ratings / historical QA gold unspecified.
- Five seeds (L44762) fixed without power analysis ("unless a later power/variance analysis justifies expansion").
- E13E-03 "eight-cuisine or available compatible data" (L44534) with no fallback if data unavailable.
- Introduction-event verification standard ("historians/primary sources support", L44146) lacks a source-quality rubric.
- How historical metadata attaches: SSOT says "Recipe / Recipe Event-State" schema (L44422); PLAN AY8 offers HIST- records OR typed table (PLAN L4581) — undecided.
- `canonical_dish_name` (L44440) has no ontology/authority specified.

### 9.4 Open questions needing external research (do not resolve from memory)
1. RELISH European Historical Recipe Dataset (Zenodo 2026): existence, version, licence, languages, date precision, size. [VERIFY]
2. Open Recipe Archive: provenance, licence, ">50k recipes" claim (L44417). [VERIFY]
3. Identity of the "Dutch historical recipe trends" corpus/paper and its licence. [VERIFY]
4. Kinouchi et al. 2008 exact algorithm: definition of M, fitness acceptance rule, reported summaries, availability of source cookbook counts (L43264).
5. Jain & Bagler 2018 Physica A 503:170–176: CM-random / CM-ranked / CMAD parameterization and data availability (L43265).
6. Whether Project Gutenberg metadata (RDF/catalog) or external catalogues (e.g. library records) provide original publication years for the 337 local books; otherwise G13E-01 fails for Gutenberg. [research]
7. Licence/terms of Food.com reviews (substitution mining, Teng-style) and of Kaggle irkaal re-distribution. [VERIFY]
8. FlavorDB2 terms and achievable mapping fraction vs project ING (5,387). [VERIFY]
9. SBI tooling maturity (sbi, BayesFlow) and SBC practice — only relevant if Phase E6 is ever unlocked (PLAN RS-15.3).
10. 2015–2026 literature on recipe genealogy / reticulate cultural transmission with directly linked recipe families (L43272).
11. Clauset-protocol implementations for discrete heavy tails (e.g. `powerlaw` Python package) — implementation detail, low priority.

---

## 10. LOOK-AHEAD: fields/metadata earlier steps must capture so L13E is usable later

Principle: capture as nullable typed fields with explicit UNKNOWN now (cheap); never backfill by intuition (L44063); missing date must not invalidate a recipe (L43313).

**Step 03 (state semantics)**
- Clock tag on every time-like field: `clock ∈ {TAU_PROCESS, T_HISTORICAL, T_RECORD_CREATED}`; reserve `tau_*` names for process time (L43001–43005, L44233).

**Step 04 (evidence/provenance/similarity contracts)**
- Evidence classes: `HISTORICAL_CULTURAL`, `SYNTHETIC_HISTORY` (never ledger-eligible), `INFERRED_DATE`.
- Claim-status mapping to [ESTABLISHED]/[REPRODUCE]/[HYPOTHESIS]/[OPEN]/[PROPOSED]/[USER-REPORTED]/[VERIFY] (L43024–43030).
- Identity relation vocabulary aligned with §264.7 strata incl. `SAME_EDITION_VARIANT` and `SAME_DISH_DIFFERENT_AUTHOR_OR_ERA` (L43478–43480).
- Similarity registry entries keep d_I, d_Q, d_role, d_P, d_G as separate stored components (L43408–43419).

**Step 05 (EVD)**
- `evidence_class`/`source_type` values sufficient to filter out historical/cultural and synthetic rows by query.

**Step 06 (source manifest)** — per source (L44035–44047, L44424–44448, L44452–44466):
- `source_document_id, source_title, source_author_editor, source_type (cookbook/newspaper/web/archive), source_language, translation_status, source_publication_year, source_edition_year, edition_lineage_parent, digitization_provider, digitization_date (≠ publication), ocr_quality, copyright_license, redistribution_allowed, date_basis, date_confidence`, bias-ledger fields (class audience, authorship type, genre, region, colonial/trade context, digitization selection, platform incentives).
- For Gutenberg specifically: store PG `Issued` as `digitization_date`, NOT as a publication date; store author birth/death years as `author_life_years` (evidence for `date_basis=inferred`), not as era.

**Step 07 / 07H-R / 07I-R (conditions, quantities, recipe base, identity)**
- Quantity rows: `raw_unit`, `unit_system/era` (historic measures e.g. gill, teacupful), `conversion_basis`, `conversion_uncertainty` (interval), mask for missing (L43434, RISK-E4).
- Recipe base: `t_document` (Food.com DatePublished; book publication year when known), `t_recipe_origin_low/high` (null unless evidenced), `date_basis`, `date_confidence`, `era_id` (only derived after bin justification L44077), `region_id`, `cuisine_id` + `cuisine_label_level ∈ {recipe, book_subject, dataset}` (Gutenberg cuisine comes from book-level catalog subjects), `author_or_contributor_id` (Food.com AuthorId) as cluster unit (L44472), `source_family`, `source_id`.
- Identity: `duplicate_group_id` (exists), `recipe_family_id` (exists), `dish_family_candidate_id` (exists), plus `lineage_group_id` (edition/derivative/web re-post lineage across sources; L44097) and `variant_group_id`; identity label set with sealed calibration/test partitions (L45217–45218).
- Retain raw historic terms and alias provenance (`alias_era`, `alias_language`, `ambiguity_state`) for ING/PROC/TOOL (RISK-E3; gutenberg_v1 historic tool list).

**Step 08 (scientific source lineage)**
- Reusable literature-ledger schema with `claim_id, source, exact_span/table, evidence_class, verified_date, notes` (L43273) — make Step 08's lineage objects capable of hosting non-chemistry (historical scholarship) sources under a separate class, so introduction-event evidence (L44146) can later be recorded without polluting STUDY rows.

**Step 09 (extraction/verification)**
- Span-level citation + date-interval fields in extracted claims (needed by E13E-18; RISK-E12).

**Steps 10–15 (evidence acquisition)**
- Step 12: FlavorDB/FlavorDB2 ingredient–compound joins with `db_version`, per-ingredient `compound_set_size`, `n_sources_per_ingredient`, `mapping_status` to canonical ING, `mapping_confidence` (L43990–43997).
- Step 13: if food-history literature is touched, tag as HISTORICAL_CULTURAL; capture event `date_low/high`, `geography`, `primary_source_ref`.
- Step 15: release manifest asserts zero HISTORICAL_CULTURAL / SYNTHETIC_HISTORY rows in DATA-EVIDENCE; DATA-HISTORICAL separate (PLAN L4460).

**Steps 16–20 (procedure/state)**
- Step 16: `historical:` block (22 fields, L44424–44448); `canonical_dish_name`, roles per ingredient line, canonical process-event sequence, flow-graph edges, `extraction_quality`.
- Step 17: per-recipe `extraction_quality` and `ocr_quality` propagated; process vocabulary version ID (vocabulary drift, L43218).
- Step 18: stable event IDs; event clock = tau only.
- Step 19: identity pair labels (E13E-05) with labeler ID, independent double labels, adjudication, sealed test; groups by duplicate/lineage family (L43487).
- Step 20: Silver sampling stratification variables (source, source_type, era/date precision, cuisine label level, recipe size, dish category) so later corpus balancing (L44476–44484) is possible; quantity coverage statistics per source (input to G13E-09).

**Step 28 / simulation memory (forward note)**
- Every simulated record: `simulator_family ∈ {FOOD_PROCESS, CULTURAL_COPY_MUTATE, …}`, `clock`, `theta`, `seed`, `fitted_on_split` (E13E-16 requires simulator data "generated only from training-fitted parameters", L45138).
