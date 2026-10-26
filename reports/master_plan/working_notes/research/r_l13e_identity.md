# r_l13e_identity — Recipe evolution (L13E) placement + recipe-identity calibration

Researcher: r_l13e_identity · Date 2026-10-22 · Plan-research only (no implementation, no Step 08, packet NOT opened, sealed key NOT read).
Scope: spine Step 07I follow-up (identity calibration), Step 35 (representation ladder), L13E placement.
The 36-step plan card text is MISSING (ctx.md). Everything said about what a step "is" below is reconstructed from the SSOT, Master Plan v4.0 and repo artifacts, and is labelled as reconstruction. No card text is quoted or invented.

---------------------------------------------------------------------------------------------------

## 0. Internal facts used (verified in repo/SSOT, read-only)

| # | Fact | Where |
|---|---|---|
| F1 | L13E is "a parallel extension of Level 13, not a new mandatory sequential level". It does not delay the core project "unless the user decides the cultural-evolution paper itself becomes the primary deliverable". | SSOT L42926-42928, L45582-45590 (§279.5), L45450 (§278.8: "does not block Level-16 implementation unless the specific experiment uses its outputs") |
| F2 | What L13E may influence: identity calibration, novelty, pairing nulls, substitution prior, cuisine views, L12 holdouts, L13 views, L16 historical packet, optional FlavorTwin prior. What it may not: z_m, tau dynamics, kinetics, sensory claims, the provenance hierarchy, UNKNOWN!=0. | SSOT §260.4–260.5 L42969-42995 |
| F3 | Identity must be probabilistic and calibrated; no fixed % rule; threshold only after calibration at a declared operating point, reported with its validation distribution; headline split grouped by source/duplicate family. | SSOT §264.1, 264.6–264.8 L43397-43498 |
| F4 | E13E-05: H0 "ingredient-set distance alone is as good as..."; baselines title-only + ingredient Jaccard; arms I, I+Q, I+Q+role, I+process, full, learned-embedding comparator; metrics AUROC, AUPRC, macro-F1 at calibrated threshold, Brier/ECE, hard-negative error; grouped CV, bootstrap by dish family, calibration split separate from test. Gate G13E-07: "stable source-held-out discrimination + calibration", else descriptive distances only. | SSOT L44868-44892; L45284 |
| F5 | Statistical principles: separate tuning/calibration/test; one sealed final test for any calibrated component; cluster/resample by source. | SSOT §278.1 L45211-45223 |
| F6 | Duplicate-group-disjoint split: near duplicates / mirrored / cross-source copies stay in one split group; RQ16-13 quantifies leakage inflation vs random split. | SSOT L14782-14784; §247.13 L27025-27044 |
| F7 | Master Plan v4.0 maps identity calibration to B14 SX-14-03 "shared with E13E-05"; B15 L13E is parallel (B15 ← B02,B03,B14); "must not block course completion"; "Never let B15 delay DEL-1…5". | MP v4.0 L244, L492, L497-501, L2941-2943, L3860-3865 |
| F8 | Parv's DELTA plan reportedly parks L13E post-course (second-hand only; DELTA not in clone). | reports/step07i/max_plan_consensus.md row "Historical variants" |
| F9 | 07I-R gate PASS (provisional), calibration gate OPEN: 612,782 recipes → 611,714 exact reps; 8,639,518 candidate pairs; 744,615 kept; 6,589 provisional edges (PROVISIONAL_STAR_V1, no chaining); 605,476 families; 46,697 dish candidates; packet 400 pairs, labels_filled 0. | reports/step07i/step07ir_gate_result.json; DECISIONS D-025 |
| F10 | Candidate-recall gaps that the packet cannot measure: ingredient-LSH skipped 4,745 over-cap buckets (791,511 record-in-bucket memberships); Amendment A1 removed recipes with <4 ingredient tokens from ingredient-LSH and lowered cap 200→50. | reports/step07i/identity_summary_v1.json; preregistration_v1.md "Amendment A1" |
| F11 | Packet population = kept pairs only: `keep = score>=0.50 OR family_edge OR REC-family OR (title-block AND title_token>=0.8)` and relation_status==CANDIDATE_NEAR_DUPLICATE. Scored-but-not-kept pairs (~7.9 M) are never sampled. | src/culinarystate/identity/pairwork.py L115; families.py L37; tools/step07i_review_packet.py |
| F12 | Packet strata as built: S01 40, S02 50, S03 60, S04 40, S05 40, S06 40, S07 30, S09 40, S10 40, S11 20 = 400. Stratum **S08_scaled_variant_hint (30 configured) is absent** from the manifest (cause UNVERIFIED: empty hint pool or dropped rows). S11 cultural/regional = only 20 pairs. | reports/step07i/duplicate_calibration_packet_manifest.json vs tools/step07i_review_packet.py STRATA |
| F13 | Packet design strengths: score/stratum hidden in a sealed key; order shuffled; two blind reviewers (Kush, Parv); 6 labels incl. UNCERTAIN; instruction "a false merge is worse than a missed duplicate"; key stores `stratum_pool_size` (enables inverse-probability weighting). Displayed text truncated (≤25 ingredient lines/900 chars; steps ≤1100 chars). | tools/step07i_review_packet.py |
| F14 | Corpus composition: FOODCOM 522,517; GUTENBERG_SEGMENT 73,955; A1_BBC 11,934; WIKIBOOKS 3,676; TASTESET 700. "era" is PUBLISHED_YYYY (web upload year, Food.com) or AUTHOR_BORN_1750s/1800s/1850s (Gutenberg author-birth proxy). Explicit cuisine labels on 9.81% of recipes. Statement: "NOT globally representative". | reports/step07i/final_recipe_database_statistics.md L26-35, L279-330, L426 |
| F15 | Process view used in identity features is noisy: PROC mapping is "CANDIDATE_VERB_FORM_MATCH_POS_UNCHECKED". | final_recipe_database_statistics.md L858-863 |
| F16 | Gold firewall: 50 Gold-indexed, 0 same-group non-Gold members, 2 with family relatives. | max_plan_consensus.md row "Gold" ; ledgers/recipe_identity/gold_firewall_v1.parquet |

---------------------------------------------------------------------------------------------------

## 1. Questions

Q1. Where should L13E sit relative to the critical path? Should anything block on it?
Q2. Which published culinary-evolution results are reproducible baselines, and what do they say about identifiability of copy-mutate parameters from rank-frequency?
Q3. Which null models are required before any pairing/cultural-similarity claim (feeds Step 35 and FlavorTwin)?
Q4. Rank-frequency / heavy-tail fitting: what protocol, and what can it identify?
Q5. Dating / temporal corpora: can the repo's corpus support temporal (historical t) claims?
Q6. Near-duplicate detection practice (MinHash/LSH, Jaccard thresholds) and dedup for evaluation leakage: what do the primary sources do and how did they set thresholds?
Q7. What is the right calibration protocol for the 400-pair packet (sample size, stratification, metrics, data reuse, operating points)?
Q8. How to preserve culturally meaningful variants while still preventing leakage?
Q9. Which L13E outputs feed identity calibration, null models, historical retrieval, representations, dataset analysis — and what must Steps 07I-follow-up / 35 / 36 change?

---------------------------------------------------------------------------------------------------

## 2. Findings per question

### Q1 — Placement (confidence HIGH)
- SSOT, Master Plan v4.0 and (second-hand) DELTA all agree that L13E is parallel and non-blocking (F1, F7, F8). Literature does not change this: the copy-mutate line produces cultural/descriptive baselines, not inputs that any evidence, mechanism, simulation or transition step (08–34) consumes (SSOT §260.5 forbids it).
- **One exception**: E13E-05 identity calibration is not really "cultural evolution". It is the calibration gate of the recipe identity layer (Step 07I). Its outputs, the split groups, are a hard dependency of every recipe-level held-out evaluation (F6, SSOT L25163 "Near-duplicate recipes/source families stay within one split"). So identity calibration must be pulled OUT of the L13E lane and placed on the recipe-plane path as **07I-C (identity calibration)**. It is a substep of Step 07, not a new top-level step. It does NOT block Step 08 (Step 08 is evidence-plane lineage and uses no recipe identity). It DOES block freezing any recipe-level test split used by Steps 16–20 (semantic Gold/Silver test sets), 29–30 (wherever recipe-derived rows enter), 35 and 36.
- The rest of L13E (E13E-01/02/03/04/06/10–18) becomes an optional parallel lane hosted by Step 35 (descriptive/null/representation work) and Step 36 (historical retrieval, deferred). It gets no hard edge into the critical path.

### Q2 — Copy-mutate baselines and identifiability (confidence HIGH)
- Kinouchi et al. 2008 [verified, full text]: four cookbooks (Dona Benta 1946/1969/2004 editions, Larousse Gastronomique (40% sample), New Penguin Cookery Book, Pleyn Delit). Rank-frequency fitted with a Zipf–Mandelbrot law with exponential cut-off, β≈1.4. Model parameters (T, K, L, M, R0) were found by searching for a good fit to the Larousse curve: T=1200, K=11, L=4, M=3, R0=20. Ingredient fitness is uniform[0,1], and a replacement is accepted if f_j>f_i. The authors themselves state that the effective free parameters R0, L, M "are not determinable from empirical data". They also report that models "without the concept of fitness" failed.
- Jain & Bagler 2018 (Physica A 503:170–176; arXiv 1505.00155) [verified preprint]: Tarladalal-scraped Indian corpus. The text says 2,543 recipes, but the per-cuisine table sums to 2,917, an internal inconsistency. Models: CM-FRand (null), CM-FRank (fitness = empirical frequency, "determined retrospectively"), CMAD (add/delete). Rank-frequency was fitted with a·exp(bx), a different family from Kinouchi's. Both CM variants reproduce rank-frequency. CM-FRank is closer on flavour sharing N̄s. CMAD did not exactly replicate recipe-size distributions.
- Tuwani, Sahoo, Singh & Bagler 2019 (ICDE-W DECOR; arXiv 1904.10138) [verified full text]: 158,544 recipes, 25 regions, 721-entity lexicon based on FlavorDB, 21 categories. Variants: CM-R, CM-C (replacement from same category = SSOT M2), CM-M (50/50), plus a no-mutation Null Model. Parameters m=20, M=4 (CM-R) / 6 (CM-C, CM-M). The evaluation metric is MAE between normalized rank-frequency curves of ingredient *combinations*. **"All the models (including null model) were able to reproduce the rank-frequency distribution of combination of ingredient categories and consequently excluded it from the analysis."** The best variant differed by cuisine with "no discernible trends".
- Consequence: rank-frequency alone is weakly identifying. The original authors say so (Kinouchi) and the data show it (Tuwani: the null matches the category curves). This confirms SSOT §268.7 (L43937-43952) and §273: E13E-02/03 must use a multi-summary panel (recipe-size distribution, k≤3 itemset spectra, category composition, N̄s with coverage, co-occurrence residuals) plus synthetic parameter-recovery before any mechanism claim. A reproduction should report the original fit family (Zipf–Mandelbrot+cutoff; a·exp(bx)) next to the Clauset protocol, not instead of it.
- Look-ahead: E13E-03 needs Tarladalal/RecipeDB-compatible Indian data. The licence for scraped Tarladalal data is UNVERIFIED, and D-015 (CoSyLab permission) is ASSUMED/DERIVED_ONLY per ctx.md. Treat the Indian reproduction as NEED_DATA/licence-gated.

### Q3 — Null models for pairing / cultural similarity (confidence HIGH)
- Ahn et al. 2011 [arXiv abstract verified]: the direction of food pairing is cuisine-dependent (Western positive, East Asian negative).
- Jain, Rakhi & Bagler 2015, PLoS ONE e0139539 [verified]: four random-cuisine controls (uniform; frequency-preserving; category-preserving; category+frequency). The frequency-preserving control reproduces the negative pairing ("frequency of occurrence of ingredients emerged as the most central aspect"), while category-only looks like the uniform null. So any pairing / co-occurrence similarity claim that is not frequency-controlled is uninterpretable.
- Strona et al. 2014, Nat Commun 5:4114 (Curveball) [verified abstract]: uniform sampling of binary matrices with fixed row and column totals, fast enough for >10^8 cells. This is the right tool for the exact degree-preserving null that SSOT §269.3 (L43982-43985) asks to compare against frequency-weighted sampling. A recipe×ingredient matrix of ~611k × a few thousand canonical ingredients is sparse. Running Curveball on it is CPU work (cost estimate UNVERIFIED; needs a pilot).
- Teng, Lin & Adamic 2012 (WebSci; arXiv 1111.3919) [verified abstract]: the complement (co-occurrence) network splits sweet/savory, while the substitute network is built from user modification suggestions. This supports SSOT §261.3: substitution is a distinct functional/cultural signal and not flavour similarity. The repo has no modification/review corpus (Food.com interactions not ingested; licence UNVERIFIED), so the substitution prior is NEED_DATA.
- Sajadmanesh et al. 2017 (WWW'17 companion, DOI 10.1145/3041021.3055137; arXiv 1610.08469) [verified abstract]: >157k web recipes, >200 cuisines; geographic/cultural similarity shapes recipes. This supports a "CULTURAL" similarity view in Step 35. It is web-era and cross-sectional and says nothing about evolution.

### Q4 — Rank-frequency / heavy tails (confidence HIGH)
- Clauset, Shalizi & Newman 2009, SIAM Rev 51:661 [verified abstract]: MLE + KS-based GOF + likelihood-ratio comparison to alternatives; least squares on log-log is inaccurate and is not a test. Broido & Clauset 2019, Nat Commun 10:1017 [verified abstract]: across ~1,000 networks only ~4% show the strongest evidence of power-law degree distributions. This is a strong prior that "universality" claims will reduce to "heavy-tailed, family undetermined".
- Consequence: E13E-01 is cheap descriptive work (CPU, minutes–hours). Its value to the core project is (a) a dataset-paper corpus descriptor and (b) a source-bias diagnostic (Food.com vs Gutenberg vs BBC). It should never gate anything except G13E-03 claims.

### Q5 — Dating / temporal corpora (confidence MEDIUM-HIGH)
- Isaksson et al. 2015, PLoS ONE e0122092 [verified]: 7 NW-European cookbooks, 1200–1999. Publication dates are "sometimes approximate". The chronologically adjacent book was usually the most similar (6/7). Animal products were the most conservative, while spices and vegetables changed more. Their sampling unit is the *book*, which supports SSOT §268.6/§275.5 (source = sampling unit).
- Bhagwat, van Erp, Paccosi & Hoekstra 2025, LDK 2025 pp. 43–49 [verified abstract]: Dutch trends 1910–1995 from housekeeping-school cookbooks and newspaper recipes. Shows dated corpora exist, but per-recipe dating method is not stated on the abstract page.
- Repo reality (F14): Food.com "PUBLISHED_YYYY" is web upload year (t_document, 1999–2019). Gutenberg era is AUTHOR_BORN_decade, a proxy that is neither t_document nor t_recipe-origin. SSOT §270.1's date_basis enum {exact_publication, edition, archive_estimate, first_attestation, inferred, unknown} has no value for author-birth proxies. The pooled web-vs-Gutenberg contrast is a domain shift, not evolution (SSOT §270.8 L44099-44115).
- **Verdict: G13E-01 DATA currently FAILS for temporal claims.** Only descriptive, source-qualified cross-sectional L13E work is possible on the current corpus. Historical-t work is NEED_DATA plus licence/date audit (RELISH, Open Recipe Archive, Dutch corpus: all [VERIFY] per SSOT §275.2).

### Q6 — Near-duplicate detection practice and leakage (confidence HIGH)
- Broder 1997 (SEQUENCES'97) [verified full text]: resemblance = Jaccard over w-shingles, estimated by min-wise sampling. 1−r is a metric, but **"resemblance is not transitive"**. This justifies the repo's star clustering without chaining for identity/merge decisions.
- Lee et al. 2022 (ACL, DOI 10.18653/v1/2022.acl-long.577) [verified full text]: NearDup = MinHash on space-tokenised 5-grams, k=9,000 (b=20, r=450), followed by an edit-similarity filter >0.8. Clusters are **connected components** of the match graph. In C4 most clusters are pairs, but 280 clusters exceed 5,000 docs and one has 250,933. Thresholds were chosen by histogram/tail inspection (comparing 0.8 vs 0.9 configurations), **not by human-labelled calibration**. Validation-set overlap with train affects >4% of standard datasets' validation examples. When duplicated across splits they kept the eval copy and removed the train copy.
- Allamanis 2019 (Onward! 2019; arXiv 1812.06469) [verified full text]: SourcererCC-style Jaccard thresholds t0=0.8 (set), t1=0.7 (multiset), taken from tool defaults plus experimentation ("fairly robust to these thresholds"). Transitivity is assumed for speed. Human check: the author inspected 100 random detected pairs per dataset and found perfect precision, but recall was not measured. Metrics were inflated "up to 100%". Best practices: the target application dictates the dedup granularity; "simply removing exact matches ... clearly insufficient"; project/source splits help "but duplication often still exists"; **include naive memorization (kNN) baselines**; down-weight duplicates instead of discarding them.
- Bień et al. 2020 RecipeNLG (INLG, DOI 10.18653/v1/2020.inlg-1.4) [verified full text]: recipe-domain precedent. Same-URL dedup, then exact, then near-match by TF-IDF cosine over ingredients+instructions. **The threshold was chosen by maximising F1 against a set of known duplicates** (Recipe1M+ ↔ gathered pairs with the same URL; best F1 0.92). 523,040 records were removed.
- Elangovan, He & Verspoor 2021 (EACL, DOI 10.18653/v1/2021.eacl-main.113) [verified abstract]: train/test overlap inflates NLP results (NER, RE). This is relevant to the closed NER block if its test split was not duplicate-group-disjoint (flag to auditors; not verified here).
- Christen 2012 (IEEE TKDE 24(9):1537–1555) [verified preprint]: blocking/indexing quality = **pairs completeness PC = matched candidate pairs / all true matches** and reduction ratio. PC is the recall ceiling of any downstream classifier, and it is the metric the repo currently cannot estimate (F10, F11).
- Marchant & Rubinstein 2017 OASIS (arXiv 1703.00617; venue per page: arXiv only, PVLDB publication UNVERIFIED) [verified abstract]: under extreme match/non-match imbalance, adaptive importance sampling cut labels needed for precision/recall/F estimates by up to 83%. This supports biased (stratified/importance) sampling with inverse-probability weighting rather than uniform sampling.
- Synthesis: published dedup thresholds in ML practice (0.8 Jaccard/edit, 0.8/0.7 SourcererCC, F1-optimal cosine) are tool defaults or proxy-label optima. None is a human-calibrated identity threshold, and none transfers to recipes, where a SAME_DISH_DIFFERENT_RECIPE pair can have high ingredient Jaccard. This confirms SSOT §264.1/264.8. The repo's 0.80 IDF-Jaccard in the provisional family rule must remain "uncalibrated" until 07I-C.

### Q7 — Calibration protocol for the 400-pair packet (confidence MEDIUM-HIGH; numbers are my own binomial computations)
Wilson 95% CIs for precision, by sample size:
| n | p=0.95 | p=0.90 | 0 errors → 95% upper bound on error (rule of 3) |
|---|---|---|---|
| 20 (S11) | 0.764–0.991 | 0.699–0.972 | 15% |
| 40 (typical stratum) | 0.835–0.986 | 0.769–0.960 | 7.5% |
| 60 (S03) | 0.863–0.983 | 0.799–0.953 | 5% |
| 100 | 0.888–0.978 | 0.826–0.945 | 3% |
| 200 | 0.910–0.973 | 0.851–0.934 | 1.5% |
| 400 | 0.924–0.967 | 0.867–0.926 | 0.75% |
Approximate SE of a 2-rater binary Cohen's κ≈0.8: ≈0.06 (n=100), ≈0.04 (n=200), ≈0.03 (n=400) at 50% prevalence, and larger at skewed prevalence (my approximation; see Sim & Wright 2005 for tabulated sample sizes [verified bibliographic/abstract only]).
Conclusions:
1. v1 (400) is adequate as a **development/calibration** set: pooled curve fit, IAA estimate, and failure taxonomy. It is NOT adequate as a sealed test of a high-precision operating point per stratum or per source (stratum CIs ±7–12 points), and it cannot test the G13E-07 "stability across sources/dish categories" requirement.
2. v1 cannot estimate recall at all. It only samples kept pairs (F11) from a capped candidate generator (F10). PC is unknown.
3. S08 (scaled variants) is missing and S11 (cultural, n=20) is too small for the cultural-variant law (F12).
4. Reusing v1 to both choose and evaluate a threshold violates SSOT §278.1 (#5–6, L45211-45223) and E13E-05 ("calibration split separate from test").
→ Protocol (Section 3B) = label v1 as dev/calibration, then build a **v2 sealed test + recall-probe packet** (~300–400 pairs).

### Q8 — Cultural variant preservation (confidence HIGH on principle, MEDIUM on implementation)
- Literature (Isaksson 2015, SSOT §261.16) treats variants as transmitted lineages, and Teng 2012 treats substitutions as meaningful. Collapsing variants destroys exactly the signal L13E and the substitution prior need.
- Leakage control and identity merging have opposite cost asymmetries:
  - For **split grouping** (leakage), a missed duplicate leaks and a false merge only enlarges a group. This calls for a recall-oriented, permissive grouping (connected components are acceptable, as in Lee 2022), with a giant-component guard.
  - For **identity/consensus/merge** (source memory, family consensus, cultural analysis), a false merge erases a variant. This calls for precision-oriented, non-transitive decisions (Broder), as in the current star rule. Merges are never destructive (SSOT law: source recipes immutable).
- Therefore keep TWO derived products: `recipe_split_groups` (permissive, for splits only) and `recipe_identity_relations` (precise, typed relations). The SAME_DISH_DIFFERENT_RECIPE / RELATED relations are preserved as edges and never coalesced. Pairs with explicit cuisine disagreement are never auto-coalesced (already preregistered family rule (5)), but they ARE put in the same split group if the permissive rule links them.

### Q9 — L13E outputs → consumers (confidence HIGH)
| L13E output | Consumer | Gate before use |
|---|---|---|
| E13E-05 calibrated p_same(view) model + 2 operating points + identity Gold labels | 07I-C → split manifest for Steps 16–20, 29–30, 35, 36; RQ16-13 leakage study | G07I-C (Section 4) ≈ G13E-07 |
| E13E-04 null lattice (U/F/C/FC/[E]/FCE + Curveball) + coverage audit | Step 35 CULTURAL/CO-OCCURRENCE similarity baselines; Step 36/FlavorTwin pairing statements | G13E-06 |
| E13E-01 rank-frequency fits + source-balanced bootstrap | dataset paper descriptors; source-bias ledger (§275.4) | G13E-03 (claims only) |
| E13E-02/03 copy-mutate reproductions (multi-summary) | Step 35 optional generative baseline; L13E paper | G13E-04/05 |
| E13E-06 novelty vector | Step 35 / FlavorTwin descriptive features | G13E-08 |
| E13E-10/11 temporal drift/forecast; E13E-18 historical-context RAG | Step 36 separate evidence class | G13E-01 + G13E-02 (currently FAIL/NEED_DATA) |
| Historical schema (§275.3) | REC/source metadata (recipe plane) | none (schema only) |

---------------------------------------------------------------------------------------------------

## 3. Architecture recommendations

### 3A. L13E placement (RECOMMENDED)
- **Keep L13E OFF the critical path.** No top-level step is added: the anti-scope-creep conditions A–D (brief §4) are not met.
- Split L13E into three homes inside existing steps:
  1. **07I-C Identity calibration** (substep of Step 07 / follow-up of 07I-R) = E13E-05 + SX-14-03. This is ON the recipe-plane path, parallel to 08–15, and must PASS before any recipe-level test split is frozen (Steps 16/17 Gold–Silver test sets, 19, 20, 29/30 where recipe-derived, 35, 36). It does not block Step 08.
  2. **35-E "cultural/null descriptive lane"** (optional substep of Step 35, runnable any time after ingredient canonical IDs + categories exist; CPU-only): E13E-01, E13E-04 (+coverage audit), E13E-02 (Kinouchi, publication parameters; no data needed), E13E-03 only if licence/data pass. These are baselines for the Step 35 cultural/co-occurrence views.
  3. **36-H historical-context retrieval**: DEFER (G13E-01 fails on current corpus).
- Everything else in L13E (E13E-06..17, SBI, pretraining, contact/introduction) is DEFERRED behind G13E-01/02 and human choice of paper (SSOT §279.8).
- Rejected alternatives:
  - (a) A new top-level L13E step: no SSOT contradiction, no orphaned dependency, no invalidated downstream claim. SSOT itself says "parallel extension".
  - (b) Leaving identity calibration inside the L13E lane (as SSOT §278.7 Phase E3 and MP B14/B15 place it): it would then inherit the "may be parked post-course" status (F8), while every recipe split depends on it, so this is a hidden prerequisite.
  - (c) Blocking Step 08 on identity calibration: no artifact dependency (different data plane).
  - (d) Running copy-mutate SBI/pretraining now: Kinouchi's own non-identifiability statement and Tuwani's null-matches-category result make it premature (G13E-12 first).

### 3B. Identity calibration protocol (07I-C) — RECOMMENDED
Stage 0 (before labels are unsealed; no data peeking)
- Pre-register: label→target mapping, operating-point rules, metrics, and what happens to UNCERTAIN. Write it as an amendment to reports/step07i/preregistration_v1.md, committed before the key is opened.
  - Y_copy = {SAME_RECIPE_COPY, SAME_RECIPE_MINOR_VARIANT} → leakage-critical "same recipe".
  - Y_dish = Y_copy ∪ {SAME_DISH_DIFFERENT_RECIPE} → dish-family / permissive split grouping.
  - RELATED, DISTINCT → negatives for both. UNCERTAIN → excluded from point estimates; sensitivity analysis with UNCERTAIN→positive and UNCERTAIN→negative; UNCERTAIN rate reported per stratum.
- Investigate and document why S08 is empty (F12) without opening labels.

Stage 1: label v1 (400) independently (Kush, Parv; already blind)
- Lock both independent label files (hash) BEFORE adjudication.
- Agreement: raw % agreement, Cohen's κ on the 6-class labels, on Y_copy and on Y_dish, plus Gwet's AC1 (robust to the skewed prevalence expected in S01/S02). Report per-stratum agreement descriptively only (n=20–60).
- Adjudication: the two reviewers discuss disagreements, with the sealed key still closed. If unresolved → UNCERTAIN, or a third reviewer for culturally specific pairs (S11). Keep pre- and post-adjudication labels and a reason field.
- Estimated time: ~5–8 h per reviewer at ~1 min/pair (UNVERIFIED estimate; measure it).

Stage 2: fit + choose operating points on v1 (development only)
- Treat each stratum as a pseudo-random sample (selection by seeded hash). Weight each pair by stratum_pool_size / n_sampled (Horvitz–Thompson) to estimate population quantities over the *kept-pair* population. Caveat: strata overlap and were filled in priority order, so the weights are approximate. Recompute exact inclusion sets by replaying the deterministic selection.
- Models (E13E-05 arms):
  - Baselines: title-token Jaccard alone; IDF-ingredient Jaccard alone; the preregistered ranking score.
  - Arms: + instruction shingle; + process sequence; + quantity profile; full logistic.
  - Optional learned-embedding comparator only if CPU-cheap.
  - Use a monotone, low-capacity calibrator (logistic/Platt-type on the score or a ≤8-feature logistic regression). Avoid non-parametric isotonic at n≈400 (the small-data concern is per Niculescu-Mizil & Caruana 2005; the detailed claim is UNVERIFIED here).
  - Grouped CV with groups = dish-family key ∪ source family (no pair's recipes on both sides).
- Metrics: weighted AUPRC (primary for Y_copy), AUROC, Brier, reliability diagram/ECE with ≤5 bins, precision and recall at the operating points with Wilson CIs, hard-negative error on S05/S09/S10, cross-cultural false-merge count on S11, per-source (FOODCOM vs GUTENBERG vs BBC vs WIKIBOOKS) descriptive breakdown.
- Two operating points (declared per SSOT §264.8):
  - OP-MERGE (Y_copy, high precision): the lowest threshold whose v1 Wilson lower bound on precision ≥ the human-chosen target (proposal: ≥0.95 point / ≥0.90 lower bound; HUMAN DECISION).
  - OP-SPLIT (Y_dish, high recall): threshold at estimated recall ≥0.95 within kept pairs (proposal; HUMAN DECISION), with groups formed by connected components ∪ exact groups ∪ dish-family candidates. Add a giant-component guard: if a component exceeds a size cap, fall back to source-level grouping for that component and report it, as Lee 2022 saw a 250,933-doc cluster.

Stage 3: v2 sealed test + recall probes (~300–400 pairs, new seed, same blind protocol, built AFTER OP choice and BEFORE anyone sees v2)
- (a) ~150–200 pairs sampled around and above OP-MERGE and OP-SPLIT. This gives ≥100 predicted positives for a precision Wilson half-width of ≈±4–5 points.
- (b) **Recall probes** for pairs completeness (Christen PC):
  - pairs from over-cap skipped LSH buckets;
  - same-normalized-title pairs among recipes with <4 ingredient tokens (excluded by A1);
  - scored-but-not-kept pairs (score <0.50) with high title or ingredient similarity;
  - ≥50 random same-source/same-category pairs as a base-rate sanity check.
- (c) ≥30 scaled-variant pairs (replaces the missing S08).
- (d) ≥60 cultural/regional pairs (cuisine/locale disagreement, Gutenberg cross-era, cross-source).
  - Include a reviewer with relevant cuisine knowledge where possible.
- (e) Show full text, or mark truncation explicitly (F13).
- v2 is used ONCE to report final precision/PC/calibration; it is never used for tuning (SSOT §278.1).
- Optional label-efficiency upgrade: OASIS-style adaptive importance sampling (Marchant & Rubinstein 2017) instead of fixed strata.

Stage 4: freeze
- Write `recipe_identity_calibration_v1` (model, thresholds, CIs, label hashes) and `recipe_split_groups_v1` (permissive groups, for splits only).
- Re-label nothing in the source; star families stay; add calibrated typed relations.
- Run RQ16-13 (leakage inflation: random vs group split) on the first downstream model as the empirical justification.
- Labels are feature-independent assets: if Step 17/20 later improve the process view (F15), re-fit the calibrator on the same v1 labels and re-confirm on a fresh small v3 test. Do not relabel.

Rejected calibration alternatives:
- Adopting a literature threshold (0.8 Jaccard/edit; SourcererCC 0.8/0.7): these are defaults or proxy-optima for code/text, not recipe identity, and SSOT §264.1 rejects fixed rules.
- RecipeNLG-style proxy-label F1 (same-URL pairs as positives): the repo has 0 MIRRORED_COPY groups and exact copies are trivial positives. Usable only as an extra sanity check, not as calibration.
- Using v1 for both selection and evaluation: violates SSOT §278.1.
- Uniform random pair sampling: base rate is ≪1% over 611k² pairs, so it yields almost no positives.
- Transitive closure for identity merging: Broder's non-transitivity plus the giant-component evidence in Lee 2022 argue against it.

### 3C. Step 35 representation consequences
- Every Step 35 evaluation must be split by `recipe_split_groups_v1` (and source-disjoint where claimed).
- Following Allamanis 2019, add a kNN/memorization baseline (nearest recipe by IDF-ingredient Jaccard) to every recipe-level task. If it is "too good", that signals leakage.
- Use duplicates by down-weighting rather than discarding.
- Similarity views: COMPOSITIONAL (IDF-Jaccard; identity distances d_I, d_Q, d_P from §264) and CULTURAL/CO-OCCURRENCE (must be reported against null lattice F/FC + Curveball; frequency is the dominant confound per Jain 2015). SUBSTITUTION is NEED_DATA (Teng-style modification data absent). Keep them separate from CHEMICAL/SENSORY (brief §24; SSOT §260.4).

---------------------------------------------------------------------------------------------------

## 4. What each affected step must change / add (reconstructed step contents; card text missing)

### Step 07 → 07I-C Identity calibration (NEW SUBSTEP; human-gated; parallel to 08–15)
- Inputs: ledgers/recipe_identity/candidate_pairs_v1.parquet, recipe_identity_features_v1.parquet, annotation/duplicate_calibration/duplicate_pairs_v1_{Kush,Parv}.csv (+ sealed key), recipe_family_members_v1, dish_family_candidates_v1, gold_firewall_v1.
- Outputs: `identity_labels_v1` (independent + adjudicated, hashed); `identity_iaa_v1.md`; `recipe_identity_calibration_v1.json` (model, OP-MERGE, OP-SPLIT, CIs, weights); `duplicate_pairs_v2` sealed test + recall probes; `identity_test_report_v2.md`; `recipe_split_groups_v1.parquet` (recipe_id → split_group_id, method, giant-component flag); typed relation table (calibrated relation_status).
- Schema fields:
  - Pair level: label_kush, label_parv, label_adjudicated, adjudication_reason, uncertain_flag, y_copy, y_dish, stratum, inclusion_weight, packet_version.
  - Recipe level: split_group_id, split_group_method, split_group_size, giant_component_fallback.
  - Relation level: p_same_copy, p_same_dish, calibrated=true/false, calibration_version.
- Baselines: title-only; IDF-ingredient Jaccard; preregistered score.
- Metrics: κ/AC1/% agreement; weighted AUPRC/AUROC; Brier/ECE; precision & recall @OP with Wilson CI; pairs completeness (v2 probes); hard-negative and cross-cultural false-merge rates; per-source breakdown.
- Gate G07I-C (PROPOSED thresholds, human to approve before unsealing):
  - (i) binary κ on Y_copy ≥0.70 (else revise guideline + relabel a 100-pair subset);
  - (ii) v2 precision at OP-MERGE Wilson lower bound ≥0.90;
  - (iii) PC estimated and reported with CI (no pass threshold until base rates are known; if PC point estimate <0.8 → widen candidate generation (raise caps on a CPU pilot) before freezing splits);
  - (iv) zero auto-coalesced pairs with explicit cuisine disagreement;
  - (v) split groups frozen before any recipe-level test set is used.
- Fail action: keep descriptive distances only (G13E-07 fail path). Use the permissive grouping (dish-family candidate ∪ family ∪ exact, or source-level) for splits so leakage control never waits on calibration.

### Step 35 Representation ladder
- Add inputs: recipe_split_groups_v1; identity calibration; null-lattice outputs; ingredient category map + FlavorDB coverage table.
- Add substep 35-E (optional, CPU): E13E-01 rank-frequency (Clauset protocol, source-block bootstrap), E13E-04 null lattice incl. Curveball, E13E-02 Kinouchi reproduction from publication parameters (T=1200, K=11, L=4, M=3, R0=20) with a multi-summary panel; E13E-03 only if data/licence pass.
- Baselines: kNN memorization baseline; frequency-preserving null for any co-occurrence/cultural similarity.
- Metrics: per SSOT §278.2.
- Gates: G13E-03/04/06/07 for corresponding claims; no cultural/pairing claim from a uniform null.
- Leakage: group-disjoint by split_group_id; source-disjoint variant for cross-source claims.

### Step 36 CulinaryState-RAG
- Historical/cultural packet = separate evidence class (SSOT §260.2). DEFER E13E-18 until G13E-01/02 pass on an audited dated corpus.
- Retrieval de-duplication of near-copies in result lists should use OP-SPLIT groups (avoid returning 5 copies as 5 sources; SSOT L25309 lineage principle).

### Steps 16–20 (recipe semantics; look-ahead consumers)
- Sample Silver/Gold-Light/Deep-Gold by split_group/family (one representative per group per tier), to save human hours and avoid Gold leakage.
- Gold test sets are drawn only after 07I-C freezes split groups.

---------------------------------------------------------------------------------------------------

## 5. Look-ahead requirements for earlier / parallel steps

1. REC/source metadata (recipe plane, owned by Step 07/07I, not Step 08):
   - Add SSOT §275.3 historical fields.
   - Add a date_basis value for proxies (e.g. AUTHOR_BIRTH_PROXY; proposal only, an SSOT change request because the §270.1 enum lacks it).
   - Add a `source_document_id` for every Gutenberg book so source-block bootstrap (§268.6) is possible.
   - Food.com year = t_document (upload year), never t_recipe-origin.
2. Ingredient canonicalization (ING/ALIAS): needs a category label per canonical ingredient (C/FC nulls; CM-C model) and a FlavorDB(2) mapping with coverage counts (Ns coverage audit §269.4). Report mapped fraction, not database size (SSOT §261.18 #7).
3. Quantity (CQPO): d_Q uses mass-grounded shares only; missing = mask, not zero (already in 07I-R). Soft-mutation (M5) stays deferred (G13E-09).
4. Process (Steps 17/20): an improved event sequence later enables d_P (edit distance/DTW). Keep human identity labels reusable (feature-independent).
5. Closed NER/linker block: confirm its TEST split was duplicate-group-disjoint (Elangovan 2021 / Lee 2022 risk). UNVERIFIED here; flag to the NER auditor; do not reopen unless leakage is found.
6. Licence: E13E-03 Indian data (Tarladalal/RecipeDB) and any Food.com interactions for substitution need licence verification (D-015 is ASSUMED/DERIVED_ONLY). No data contents go to external services.

---------------------------------------------------------------------------------------------------

## 6. Residual uncertainty; pilot vs reading

- UNKNOWN: base rates of Y_copy/Y_dish in kept pairs; reviewer agreement; pairs completeness of the capped candidate generator; why S08 is empty; the size distribution of permissive split groups (giant-component risk). **More reading cannot resolve any of these. Empirical work is cheaper:**
  - (a) label v1: ~5–8 h per reviewer;
  - (b) a CPU-only pilot on the existing 1-in-20 sample re-running candidate generation without bucket caps / without A1, to measure how many high-score pairs the caps lose (minutes on this server, per benchmark report scale);
  - (c) a connected-components dry run of OP-SPLIT candidates on kept pairs to see group-size distribution.
- Copy-mutate identifiability is already settled enough by primary sources (Kinouchi's own statement; Tuwani's null result) to defer SBI. No further reading needed.
- Stop rule (brief §8) met: the evidence suffices to choose architecture (#1), searches stopped yielding new information for dedup thresholds (#2), and the remaining uncertainty is empirical (#5).
- Confidence: placement HIGH; protocol structure HIGH; specific numeric gate thresholds MEDIUM (they are proposals for human approval, not literature values).

## Sources opened (see StructuredOutput bibliography for full list)
Kinouchi 2008 (full text), Jain & Bagler 2018 preprint (full text via ar5iv), Tuwani et al. 2019 (full text), Jain/Rakhi/Bagler 2015 (article page), Ahn 2011 (arXiv abstract), Teng 2012 (arXiv abstract), Sajadmanesh 2017 (arXiv abstract + bib), Clauset 2009 (arXiv abstract), Broido & Clauset 2019 (arXiv abstract), Isaksson 2015 (PMC full page), Bhagwat 2025 (ACL anthology page), Strona 2014 (RePEc abstract), Broder 1997 (full text), Lee 2022 (full text), Allamanis 2019 (full text), RecipeNLG 2020 (full text), Elangovan 2021 (abstract), Christen 2012 (preprint full text), Marchant & Rubinstein 2017 (arXiv abstract), Sim & Wright 2005 (repository abstract page), Niculescu-Mizil & Caruana 2005 (abstract page).
