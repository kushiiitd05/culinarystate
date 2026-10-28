# Step 35.0 sign-off sheet for Kush and Parv — DRAFT, UNSIGNED

Source: `reports/step35/preregistration_35_0_v1_draft.md` (the full text; "s" = its section), `README.md`, `foodcom_cuisine_derivation_README.md`, DECISIONS D-033/D-036/D-037. This sheet adds no value of its own. Nothing is evaluated until the rows below are signed and hashed (gate G35-PRE). The THR-35P rows are not in any file under `registry/` (grep found none); they live only in the draft's Appendix A and have never been written to the registry.

## 1. What Step 35 will and will not claim

Review update 2026-10-28: Parv's answers are in
`35_0_parv_review_DRAFT.md` and DECISIONS D-039/D-040. The questions below are
retained as the review checklist; they are not a statement that all remain
unanswered. D4's mapping choices and expanded REGION definition are recorded in
`foodcom_cuisine_derivation_README.md`. Everything remains unsigned; no expert
review or signature is inferred from Parv's single-reviewer choices.

1. WILL: for molecules, ingredients, recipes and cuisines, say whether a simple, explicit representation (counts, overlaps, fingerprints) beats trivial baselines on leakage-safe tests, with confidence intervals. A "no" or "not enough data" is a valid result and is kept.
2. WILL NOT: say anything about "flavour compatibility", "pairs well" or "tastes like". Shared compounds are only tested as a predictor of held-out recipe co-occurrence (a cultural statistic).
3. WILL NOT: use or release FlavorGraph or Recipe1M-derived data in any comparison (rule BAN-35-1); FlavorGraph-derived profiles stay local and analysis-only.
4. WILL NOT: build or train learned models (35g), or claim "state of the art" or "beats X". No single combined similarity score.
5. Taste claims rest on about 603 labelled molecules, 71% from one AGPL-3.0 database, positive-only labels, and a source-database confound; expect wide intervals and some classes marked NEED_DATA.
6. Recipe and cuisine claims are descriptive only until the 07I-S split exists. **Single-reviewer caveat (D-033):** the 07I-C labels are Kush's labels; the 0.88 figure is Kush-declared on the adjudicated basis, not computed, and not an inter-reviewer kappa (the blind kappas were 0.571 and 0.588 and stay on record). Any claim resting on 07I-C must say "single-reviewer basis".

## 2. Decisions needed before anything is evaluated (most important first)

**D1. Sign the threshold rows, the hash gate and the main scores (D35-1, 5, 13, 22, 23, 24).** Question: sign the 43 proposed rows THR-35P-01..43 (the numbers in section 3), including the "one headline score per level" and the splits? Options: (a) sign as drafted; (b) amend then sign; (c) leave unsigned. Recommended: (b), going through section 3 line by line, because many values are round-number proposals and are only protected by being fixed first. If undecided: nothing can be evaluated, including the parts that could run on this server.

**D2. Taste labels: map, negatives, source confound, deprecated edges (D35-4, D35-18).** Question: approve the label-name map (Sweet, Bitter, Sour, others not scored), "confirmed negatives only", and the source-database-only control; and name who finds out why 204 ChemTastesDB edges were deprecated (recorded reason: "no longer derived"). Options: (a) approve rules, name a chemistry-aware reviewer; (b) approve the rules but skip the audit; (c) defer. Recommended: (a); a missing-label molecule is not a negative, and 71% of labels come from one database, so a model could score just by recognising the database. Single-reviewer caution: if only one person reviews the map, state so. If undecided: molecule taste benchmarks (35a) stay blocked.

**D3. Banned inputs and licence stance (D35-20, D35-6, D35-17).** Question: accept that no arm may use FlavorGraph edges/embeddings, ING_CO_OCCURS or any Recipe1M statistic (weaker comparators, but no leak into the test set), and that FlavorGraph profiles, Food.com (licence unverified, unregistered) and BBC stay local; per-item outputs go to git-ignored `features/step35/`. Options: (a) accept; (b) allow some Recipe1M-derived comparators. Recommended: (a); (b) makes the ingredient test impossible to defend. If undecided: the ingredient test (TASK-ING-A) is blocked.

**D4. Cuisine labels (D-036, D-037 DONE; mapping and confound control to sign).**
- DONE D-036: Food.com cuisine is derived from its own tags via a written mapping, signed by Kush and Parv before any cuisine number; labels are flagged `DERIVED_FROM_TAG`, never mixed with explicit labels in one claim; no mappable tag stays UNKNOWN; Food.com stays local research use.
- DONE D-037: pan-regional tags (European, Asian, African, Caribbean, Southwestern U.S., Middle East and similar) are continent/region labels only, never single-cuisine; text-strata regexes run locally; Gutenberg is out of the Deep-Gold pilot.
- STILL OPEN (the mapping itself, unsigned): (i) US-regional and subnational terms (Cajun, Tex Mex, Creole, Cantonese, Szechuan, Hawaiian...): fold into a country, keep separate, or UNKNOWN; (ii) 2,643 recipes with conflicting cuisines: drop, own class `CONFLICTING`, or multi-label; (iii) Southwest Asia and Polynesian continent calls; (iv) is a 12.9% mapped rate acceptable. Recommended: keep separate or UNKNOWN for (i), a `CONFLICTING` class for (ii) (nothing is guessed). Name a cuisine-ontology reviewer, 4-6 h (D35-9).
- Confound control (cuisine = website, since Food.com is 85.3% of recipes): derived and explicit labels are never pooled; a class enters the headline only with >= 100 recipes and >= 2 source families (THR-35P-22), which derived-only Food.com labels cannot meet alone; a source-identity-only baseline is always reported; if cuisine score under source holdout falls to <= 50% of the within-source score the claim is labelled SOURCE_CONFOUNDED (THR-35P-26). The headline cuisine set may be empty; that is a result.
If undecided: no cuisine number may be computed.

**D5. Chemistry toolkit (D35-2, D35-3, D35-21).** Question: add rdkit (and optionally LightGBM) as a pinned project dependency, and on which machine? Open Babel is not proposed. Options: (a) yes, on the Mac; (b) no. Recommended: (a), about 0.5 h; without it the standard ECFP/Morgan fingerprint (SIM-06) and scaffold split are missing and the molecule leaderboard must be labelled "PubChem-881 + descriptors only". 15 molecules with salts or mixtures are excluded until then. If undecided: option (b) applies by default.

**D6. Recipe timing and data coverage (D35-8, D35-14, D35-7).** Question: accept descriptive-only recipe/cuisine runs until 07I-S exists; accept masking of ingredient lines the linker missed (floor 0.80 linked); name who audits the 50 ingredient-to-FlavorGraph crosswalks (Parv, about 2 h). Recommended: accept all three. If undecided: recipe/cuisine work waits entirely.

**D7. Claim labels for weak notions (D35-10, 11, 15, 16, 19).** Question: keep "functional substitutability" a hypothesis (no 200-300 blind-pair annotation, expert 8-15 h); keep taste classes as the SENSORY molecule set (a stated deviation from the plan); park SIM-13 outside the nine notions; minimum profile size 5 for headline ingredient pairs. Recommended: keep all as drafted. If undecided: those notions are reported UNSUPPORTED.

**D8. Learned models stay deferred (35g, THR-35P-29).** Question: confirm no learned model is run or planned until explicit rungs are evaluated and a signed addendum exists. Recommended: confirm. If undecided: treated as deferred.

## 3. Thresholds (copied from the draft Appendix A; all PROPOSED_PILOT, unsigned; none invented)

| id | quantity | proposed value |
|---|---|---|
| 01 | hash gate | document + rows sha256-hashed before first run; runner refuses otherwise |
| 04 | taste classes | ACTIVE edges only; Sweet, Bitter, Sour scored; Bitter/Sweet counts as both; Multitaste, Miscellaneous, Tastelessness etc. = OTHER (not scored) |
| 05 | class support | >= 30 positives, >= 10 clusters, >= 5 test positives in >= 3 of 5 folds |
| 36 | negatives / confound | >= 30 confirmed negatives; SOURCE_DB_CONFOUNDED if lower 95% bound of (best arm minus source-only baseline) is not above 0.02 AUPRC; reason for 204 deprecated edges = UNKNOWN until audited |
| 06 | molecule splits | 14-char key + cluster; 5 seeds x 5 folds; DEGENERATE if largest component > 30% |
| 35 | tau_cluster | 99th percentile of Tanimoto over 20,000 seeded random pairs, clipped to [0.60, 0.85], grid +-0.05 (value itself UNKNOWN until computed, label-free) |
| 08 | promotion margin, molecules | 0.01 macro-AUROC; 0.02 macro-AUPRC |
| 09 | promotion margin, retrieval | 0.01 Recall@10, on >= 2 task families and 2 split types |
| 10 / 11 | uncertainty | cluster bootstrap B = 10,000; BH q < 0.05 per family; >= 5 seeds x 5 folds |
| 12 | IDF weight | max(0, ln(N/(1+df))), N = 298 |
| 13 | Curveball null | 5 x n_ingredients trades, 1,000 randomisations |
| 14 / 15 | coverage gate | abs(Spearman rho) > 0.3 persisting under 4 size bins, 1,000 resamples = COVERAGE_CONFOUNDED |
| 16 | dropout check | 10%, 25%, 50%; no pass value |
| 17 | primary endpoints | PE-35a..d, one per level (definitions in s11; PE-35d per row 41) |
| 18 | held-out co-occurrence | query >= 10 relevant partners; relevant = >= 5 test recipes, NPMI >= 0 |
| 19 | link coverage floor | 0.80; coverage by source = UNKNOWN (not yet measured) |
| 20 | memorisation alarm | nearest-train IDF-Jaccard >= 0.80 flagged; not a gate |
| 21 | recipe partition | 60/20/20 by split group; 50 gold-firewall recipes excluded |
| 22 | cuisine class support | >= 100 recipes and >= 2 source families |
| 24 | motif support | pairs >= 20, triplets >= 10 recipes |
| 26 | cuisine = source flag | cuisine F1 under source holdout <= 50% of within-source |
| 27 | separation object sets | 298 ingredients; 1,726 molecules; 100,000 sampled recipe pairs |
| 32 | min profile size | 5 compounds for headline pairs |
| 37 | null draws | B >= max(1,000, ceil(20 m / 0.05)); compute budget = UNKNOWN until recorded before the run |
| 40 | cold-start | 20% of ingredients; query >= 3 partners; relevant = >= 2 test co-occurrences |
| 38, 39, 41, 42, 43, 02, 03, 07, 23, 25, 28-31, 33, 34 | procedural rules | see draft Appendix A (bans, handling rules, labels; no free numbers) |

## 4. What may start now versus what is blocked

**May start without signature (R-10, THR-35P-02):** writing specs; unit tests on synthetic fixtures; the PubChem-881 decoding test on published example fingerprints; split-auditor planted-pair tests; environment pinning; descriptive count tables of inputs; descriptive explicit baselines that compute no metric on real labels, profiles or recipes.

**Blocked until signed (G35-PRE):** any score, similarity, co-occurrence, split result, model or metric on real taste labels, real ingredient profiles or real recipes; any cuisine statistic (D-036 needs the signed mapping first). **Also blocked after signing:** recipe/cuisine headline claims (need 07I-S; before that descriptive only, labelled `DESCRIPTIVE_CONSERVATIVE_GROUPING`); rdkit-dependent rungs (need D5); learned rungs (deferred).

## 5. Human hours (copied from the plan cards, UNVERIFIED)

35-explicit lane: Kush 5.5-9.5 h, Parv 5-9 h, expert 4-6 h. Itemised: threshold sign-off about 3 h each; rdkit decision 0.5 h; licence decisions 2 h; crosswalk audit 2 h; decision-record sign-offs 2 h each; cuisine-ontology review 4-6 h. Whole Step 35: Kush 12-16 h, Parv 10-14 h, expert 12-21 h. These come from the plan, not from measurement.
