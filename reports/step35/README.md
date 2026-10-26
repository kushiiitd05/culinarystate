# Step 35.0 — explicit-first baselines pre-registration: index and human-decision checklist

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 under D-027 ruling R-10 (Plan section 4.2 lane L6) and Execution Plan v2 (R-16, R-18, R-19, R-20); **revised in Round 3** after the governance review (A) and the science review (B), see section 7. Pre-registration text only. No fingerprint, similarity, profile, split, metric or model was computed; no tool was written or run; nothing is signed; **Step 08 is not started**. All numbers are PROPOSED_PILOT.

## 1. Index

| Path | Bytes | What it is |
|---|---|---|
| `reports/step35/preregistration_35_0_v1_draft.md` | 114,810 | The 35.0 pre-registration for rungs 35a (molecule), 35b (ingredient compound sets), 35c (recipe), 35d (cuisine) and 35e (typed registry, nine notions): scope and claim boundary, data-seen disclosure, inputs with licence scope and the rdkit gap, tasks / metrics / splits / nulls / negative controls, primary endpoints, promotion rule, gates, the rule that learned rungs (35g) stay DEFERRED; Appendix A = 43 proposed 01.6 rows `THR-35P-01..43` (CSV block, **not** written to the registry; 34 original rows, several amended in Round 3 and marked `[R3]`, plus 9 rows added in Round 3); Appendix B = crosswalk SIM-01..21 -> nine notions (rows 11 and 14 split so that no v2 row mixes notions) |
| `reports/step35/README.md` | (this file) | index and checklist |

Planned but **not created** (Plan Step 35 outputs): `reports/step35/preregistration_v1.md` (+ sha256; the signed form of the draft), `registry/similarity_registry_v2.csv`, `registry/representation_registry_v1.csv`, the evaluation reports and the two decision records, and the data outputs. **Data outputs are directed to the git-ignored `features/step35/`** (profiles, fingerprints, per-item split assignments, `recipe_explicit_v1/`); only sha256 manifests are tracked (`registry/splits/step35_split_hash_manifest_v1.json`, `reports/step35/output_hash_manifest_v1.json`). `.gitignore` is **not** edited; the card's default paths `ledgers/representation/` and `registry/splits/*.json` are not ignored and are not used for per-item outputs (decision D35-17).

## 2. What was and was not touched

- Created: `reports/step35/` with the two files above (Round 3 edited only these two files).
- Not touched: every existing file, including `registry/preregistered_thresholds_v1.csv` (format only), `registry/ssot15_similarity_registry.csv`, all ledgers, schemas, tools, the plan, SSOT, `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`, `.gitignore`.
- Read-only inputs (counts and structure only): `MOL`, `IMAP`, `KGE`, `ING`, `SRC`, `recipe_base_v1.parquet`, `recipe_identity_*.parquet`, `reports/flavorgraph_v1.md`, `fdc_crosswalk_v0.md`, `reports/step07/step07h_full_recipe_base_report.md`. **No ingredient or instruction text of any recipe was opened and no title was read from the recipe base.** `obabel -L fingerprints` was run once to list fingerprint names (no molecule processed). Round 3 recomputed ledger counts on latest versions with `/usr/bin/python3 -I` (counts, edge-note strings of DEPRECATED taste edges, SMILES containing `.`) and ran `git check-ignore -v` on candidate output paths. No git write command.
- **Logging note (review A, INFO):** CLAUDE.md asks that every step be logged with `tools/log_step.py`. This lane did not log (a WORKLOG entry modifies an existing file). The integrating session should log the step with `--files` the two paths above and `--verify` "Appendix A: 43 rows, 16 columns, header identical to the registry, ids unique, no collision with the 47 existing ids; git diff --stat empty".

## 3. Findings that shape the draft (please read)

1. **rdkit is not installed anywhere I could find on this server** (PATH `python3` = `miniconda3/bin/python3` 3.13.13 stdlib only; `/usr/bin/python3` 3.12.3 with numpy 1.26.4, scipy 1.11.4, jsonschema 4.10.3 and no pandas; `envs/{fd27,fdtf,gsdiff_env,hd_env,hgpp_env,manjot_env}`; `/tmp/v4_kaggle_env`), and **LightGBM, XGBoost and TabPFN are not installed in any environment** (a lightgbm 4.7.0 CPU package sits unlinked in the miniconda `pkgs` cache). WORKLOG S088 says rdkit is in the Mac base environment ("user-approved"); STATUS.md line 76 (a stale section) says missing; the Mac state is not verifiable from here, so the draft treats rdkit as unavailable.
   - **Can be done without rdkit:** E0 identity (full InChIKey and 14-character connectivity block), E1 Tanimoto on the stored PubChem CACTVS-881 fingerprints (after a decode-convention unit test: 222 hex characters = 881 bits MSB-first + 7 zero pad bits), the six PubChem descriptors, label prior / kNN-Tanimoto / logistic / random forest / a scikit-learn GBM stand-in, connectivity-block and 881-cluster splits, all of 35b's PRESENCE-tier set arms (n_ij, Jaccard, Ochiai, IDF, Curveball null) and the 881-based set aggregators, and the specification of 35c, 35d, 35e.
   - **Waits for rdkit (plus a pinned-version dependency decision):** ECFP/Morgan including **SIM-06**, FCFP, MACCS, atom-pair, RDKit2D, Murcko scaffolds and the scaffold split, ECFP-based ingredient kernels, OT ablation, the SSOT G2 reference baseline (also needs LightGBM), and the grouping of the 15 multi-component molecule records by their largest organic fragment. SIM-06 stays DATA-MISSING.
   - **Open Babel 3.1.1 exists on the server** (dpkg; `obabel -V` prints 3.1.0; `/usr/local/bin/obabel`, ECFP0-10, FP2/3/4, MACCS) but is not a project dependency and its ECFP is not RDKit's Morgan; the draft does not propose it and forbids labelling it SIM-06 (decision D35-3).
2. **Recipe incidence for R0/R2 is not on this server** (`ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet`, hash-frozen on the Mac) and was built with exact-alias lookup, not the NER + BGE linker; link coverage by source is unknown, so unlinked mentions are masked, not read as absent.
3. **07I-C / 07I-S do not exist**: recipe and cuisine headline claims wait; descriptive runs on the conservative grouping are allowed and labelled.
4. **The ingredient profile universe is small and selected**: 298 ING have PRESENCE profiles (FlavorGraph-derived, DERIVED_ONLY, upstream Recipe1M + FlavorDB CC BY-NC-SA 3.0, analysis-only), chosen by FlavorGraph's Recipe1M frequency (a selection effect on TASK-ING-A queries); 603 molecules carry >= 1 ACTIVE taste edge (941 edge ids: 737 ACTIVE / 204 DEPRECATED at the latest version; ACTIVE by source: bittersweet 524 AGPL-3.0, ChemTastesDB 204 CC BY 4.0, SweetpredDB 9 ASSUMED, i.e. **71% AGPL-3.0**). Expect wide intervals and several NEED_DATA classes.
5. **Cuisine is close to source**: 9.81% of recipes carry a label, none from Food.com, 59% are "American", 85.6% of labelled recipes are Gutenberg segments. The cuisine headline set may be empty.
6. **KGE `ING_CO_OCCURS` and all other Recipe1M/FlavorGraph-derived inputs are banned from every arm, comparator, mapping and tie-breaker** (BAN-35-1, `THR-35P-38`): 57,496 lines = 36,212 ids, of which 38,394 lines (27,530 ids) come from FlavorGraph/Recipe1M and 19,102 lines (8,682 ids) were mined across the corpus. TASK-ING-A recomputes relevance inside the test partition.
7. **SIM-13 (reaction-center similarity) has no home among the nine notions**; flagged RESEARCH_ONLY (decision D35-11).
8. **Taste labels are positive-unlabelled and source-confounded**: only confirmed negatives are used, a source-database-only baseline is mandatory (`THR-35P-36`); 15 of 1,726 molecule records are multi-component and are excluded from scored sets until a toolkit is approved (`THR-35P-39`).
9. **The nine notions now have separate (evaluation target, null) pairs** (preregistration 8.2): TASK-ING-A is the CULTURAL target and a cross-notion association test, not CHEMICAL's or STRUCTURAL's own evaluation set; "structure -> taste" is the STRUCTURAL x SENSORY separation test.

## 4. Human-decision checklist

Tick when decided; the draft's default is given. Ids are `D35-n` (the plain `D-n` ids of the first draft collided with DECISIONS `D-0nn`). Plan estimates (UNVERIFIED): 35-explicit lane Kush 5.5-9.5 h, Parv 5-9 h, expert 4-6 h; pre-registration threshold sign-off Kush + Parv ~3 h each; rdkit decision ~0.5 h; licence decisions ~2 h; crosswalk audit ~2 h; decision-record sign-offs ~2 h each; cuisine-ontology review 4-6 h.

**Before any evaluation (G35-PRE)**
- [ ] **D35-1** Sign (or amend) the 43 rows `THR-35P-01..43` in Step 01.6 and agree the hash-gate control (`THR-35P-01`). *Nothing is evaluated before this.*
- [ ] **D35-13** Primary endpoints PE-35a..d (PE-35d as redefined in `THR-35P-41`), the secondary PE-35b-cold, and the promotion deltas (0.01 macro-AUROC / 0.02 macro-AUPRC / 0.01 Recall@10) (`THR-35P-08,09,17,40,41`).
- [ ] **D35-5** The tau_cluster derivation procedure (99th percentile of tau881 over 20,000 seeded random molecule pairs, clipped to [0.60, 0.85], grid +-0.05; `THR-35P-35`), the 30% degenerate-split rule, 60/20/20 recipe partitions (`THR-35P-06,21`).
- [ ] **D35-4** Review and approve the taste-label normalisation map with a chemistry-aware reviewer (`THR-35P-04`); approve the scored-class support rule (`THR-35P-05`).
- [ ] **D35-18** Confirmed-negative rule, the reviewed database x class assay-coverage table, >= 30 negatives per class, NC35-14 and the `SOURCE_DB_CONFOUNDED` rule (`THR-35P-36`); name who establishes the reason of the 204 DEPRECATED edges (counts by reason, before signature).
- [ ] **D35-19** Notion separation: the per-notion (evaluation target, null) pairs of 8.2, TASK-ING-A as the CULTURAL target and a cross-notion association test, ST-1 / ST-2 / SE-1, the shared-split-family table 8.2b (`THR-35P-28`).
- [ ] **D35-20** BAN-35-1 (`THR-35P-38`): accept the weaker comparator set (no FlavorGraph/Recipe1M-derived arm) and the profile-universe selection-effect caveat.
- [ ] **D35-22** Null-draw rule B >= max(1,000, ceil(20 m / q)), a compute budget recorded before the run, and the `Z_CALIBRATED` fallback (`THR-35P-37`).
- [ ] **D35-23** Cold-start definition (20% of profiled ingredients stratified by profile-size quartile; recipes containing them removed from train) and the secondary endpoint PE-35b-cold (`THR-35P-40`).
- [ ] **D35-24** PE-35d on `S-cui-src` minus prevalence with the source-identity baseline on `S-rec-grp` (`THR-35P-41`); recipe split rules for `S-rec-src` and the `S-rec-grp` stratum (`THR-35P-42`).

**Environment and dependencies (H2 / H3)**
- [ ] **D35-2** rdkit (or another structure toolkit) as a project dependency (pinned version; which machine); optionally LightGBM; optionally TabPFN (needs a licence row). Default: no, rdkit rungs WAIT.
- [ ] **D35-3** Allow or forbid Open Babel ECFP as a separately named definition (default: not proposed).
- [ ] **D35-21** Multi-component molecules (15 of 1,726): excluded and listed until a toolkit is approved, then grouped by the block of the largest organic fragment (`THR-35P-39`).
- [ ] **D35-7** Who audits the 50 ING <-> FlavorGraph crosswalks (Parv, ~2 h), and whether `recipe_ingredient_mentions_v1.parquet` is copied to the server (default: no; run on the Mac).

**Licence and scope (H2)**
- [ ] **D35-6** Confirm the stance: FlavorGraph-derived profiles analysis-only / DERIVED_ONLY (upstream Recipe1M + FlavorDB, CC BY-NC-SA 3.0; repository Apache-2.0; ASSUMED); ChemTastesDB (CC BY 4.0), bittersweet (AGPL-3.0; 71% of ACTIVE taste edges) and SweetpredDB (ASSUMED) taste labels; Food.com `LICENCE_UNVERIFIED` and **unregistered** (no SRC row, D-024, H2; CC0 is uploader-declared only), local use for explicit statistics; BBC local-only (`THR-35P-31`).
- [ ] **D35-17** Output locations: per-item outputs to the git-ignored `features/step35/`, sha256 manifests tracked, `.gitignore` **not** edited (departs from the card's default paths, which are not ignored). Alternative: approve a `.gitignore` edit instead.

**Data and labels**
- [ ] **D35-8** Accept descriptive-only recipe / cuisine runs until 07I-S exists (`THR-35P-03`).
- [ ] **D35-9** Name a cuisine-ontology reviewer (4-6 h) and approve the support rule >= 100 recipes and >= 2 source families (`THR-35P-22`).
- [ ] **D35-14** Recipe link-coverage floor 0.80 and masking of unlinked mentions (`THR-35P-19`).
- [ ] **D35-15** Minimum profile size 5 for headline pair metrics (`THR-35P-32`).
- [ ] **D35-10** FUNCTIONAL stays HYPOTHESIS, or commission 200-300 blind two-annotator substitution pairs (expert 8-15 h).
- [ ] **D35-16** Accept taste-class labels as the SENSORY molecule set (deviation from the Plan nine-notion table); status "HYPOTHESIS (taste classes only; odour NEED_DATA + licence)"; ingredient UNSUPPORTED.

**Registry**
- [ ] **D35-12** Final id scheme and statuses of `similarity_registry_v2` (Step 01.3, H4); the draft uses working ids only; the known `SIM-` double meaning (04.9-min section 6) stays open.
- [ ] **D35-11** Where SIM-13 lives given the nine-notion rule (default: outside the nine, RESEARCH_ONLY).

**Learned rungs**
- [ ] Confirm that 35g stays DEFERRED under the LR-1..LR-5 entry rule and the "learned" boundary (`THR-35P-29`): no 35g run, schedule or pre-registration until the explicit rungs are evaluated and a signed addendum exists.

## 5. After the decisions (order of work)

1. Sign the rows and freeze the draft as `reports/step35/preregistration_v1.md` with its sha256 -> 2. on the server (existing environment): unit tests on synthetic fixtures, PubChem-881 decode test, split-auditor planted-pair tests (including NC35-15, NC35-16, NC35-17), registry lint -> 3. label-free tau_cluster derivation, then evaluate 35a-lite and 35b PRESENCE arms (descriptive recipes/cuisines only until 07I-S) -> 4. on the Mac: 35c / 35d with the incidence ledger, and 35a ECFP rungs once rdkit is decided -> 5. 35e registry and separation tests -> 6. 35h decision records v1 (PROMOTED / FAILED / DATA-BLOCKED). 35f waits for Steps 15, 27, 30, 33; 35g stays deferred.

## 6. Cross-references

Plan v2 Phase H and the Step 35 card (nine-notion table, architecture detail); `r_representation_flavortwin.md` (evidence base, pilot P35-0); SSOT s133.2 (circularity), s159.3 (null ladder), s183.4 (L12 completion gate), s190.16 and s191 (non-circular matrix, tasks, splits, confound audits); `registry/ssot15_similarity_registry.csv` (SIM-01..21, not edited); `reports/step04/README.md` (plane-qualified `SPLITGRP-` ids, 01.6 row format); `reports/step19/` (Step-19 `DESIGN_PILOT` groups are excluded from Step-35 partitions).

## 7. Round-3 revision summary (what changed and why)

- **Counts** now use latest-version ids and state ledger lines next to ids (IMAP 31,972 lines = 30,294 ids; PRESENCE 31,334 lines = 29,656 ids; MOL_HAS_TASTE 1,145 lines = 941 ids = 737 ACTIVE + 204 DEPRECATED; `ING_CO_OCCURS` 57,496 lines = 36,212 ids; others likewise). The wrong "supersession" of SIM-02's 30,294 was removed (30,294 is the correct id count).
- **Notion separation** (A8, B 35-1, A22, A33): own (evaluation target, null) pairs, shared split families listed, TASK-ING-A re-labelled, Appendix B rows 11 and 14 split, SENSORY molecule status deviation recorded (D35-16).
- **Leakage and contamination** (B 35-2): BAN-35-1 and the NC35-17 manifest lint. **Labels** (B 35-3): confirmed negatives, source-database baseline, DEPRECATED audit. **Splits** (B 35-4, 35-6, 35-9): multi-component handling, group-disjoint `S-rec-src`, label-free tau_cluster. **Endpoints and nulls** (B 35-5, 35-7, 35-8): PE-35d, draw count compatible with BH, cold-start endpoint.
- **Reporting additions** (B 35-10 to 35-13, A25): decode convention, identical profiles, masked IDF 0/0, kNN-alarm distribution, falsifiable reading of the structure -> taste result.
- **Governance** (A6, A7, A9, A10, A24, A26, A28, A29, A31, A32, A34, A35): ids renamed (`D35-n`, `NC35-n`, `LR-1..5`, `TASK-ING-A/B`), authority line, git-ignored output paths with `.gitignore` untouched, Food.com unregistered, FlavorGraph upstream Recipe1M + FlavorDB, environment census, `DESCRIPTIVE_COUNTS_SEEN` flags (`THR-35P-21`).
- **Not changed:** no gate was weakened; no registry, ledger, schema, tool or `.gitignore` was edited; nothing was signed. Items intentionally left open for humans are the checklist above.
