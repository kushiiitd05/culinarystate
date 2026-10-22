# STEP 07I-R -- plan authority inventory

Machine-readable twin: `registry/plan_authority_map_v1.csv` (28 rows). Precedence applied (as instructed): 1 SSOT v15 definitions/contracts -> 2 approved Master-Plan/SSOT15 programme decisions -> 3 approved decision records (`DECISIONS.md`) -> 4 frozen execution spine / active step contract -> 5 MAX / master implementation plans -> 6 STATUS / WORKLOG -> 7 code -> 8 historical. A MAX plan adds implementation detail and never overrides an SSOT law.

## 1. Repositories searched

| Source | State |
|---|---|
| Local checkout `~/Desktop/CGAS/culinarystate` | `main` @ `6acd578` (+ uncommitted 07I work from the previous session: 4 tools, 1 registry file, 3 small edits; not part of any other step). `git status` / `git branch -vv` / `git log --all` read first. **No `origin` is configured locally.** |
| Remote `https://github.com/ParvGoyal08/CGAS` | `git ls-remote` shows only `refs/heads/main` @ `93768fb` ("Import culinarystate with its full history"). Fetched read-only into the namespaced ref `refs/remotes/parv-origin/main` (no remote added, no merge/rebase/reset/push). **It has no merge-base with the local history** (24 commits, Oct 6-13, Parv's earlier Max-plan session; 336 files). Consistent with D-001 ("rebuild locally ... Parv continues from this repo"). |
| Sibling dirs `~/Desktop/CGAS/{A2,A3,a1,cgas_salvage,research}` | searched; contain course submissions, SSOT v14, and chemistry research notes; no recipe-identity plan. |

## 2. Authoritative vs supplemental

AUTHORITATIVE: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (byte-identical to the copy at the CGAS root and to the copy in `parv-origin/main`). SSOT v14 (`A2/`) is SUPERSEDED.

APPROVED PLAN (implementation detail): `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (181,975 B; byte-identical to `parv-origin/main:Plan_SSOT15_v4_0.md`); `CulinaryState_Claude_Max_Master_Prompt_v2_0.md` is its v2.0 predecessor (Parts A-AF identical -> superseded by v4.0); `CulinaryState_Detailed_RnD_Execution_Plan_v2.md` (recipe-semantics/leakage detail, written against SSOT v14 numbering).

SUPPLEMENTAL (Parv's repo): `DELTA_PLAN_v4.md`, `LANE_PLAN_v5.md`, `ACQUISITION_PLAN.md`, `COVERAGE_MAP.md`, `STATUS.md`, `DECISIONS.md` (DEC-001..041, no authority over local D-001..D-024), plus `src/culinarystate/silver/pipeline.py` which contains a toy `duplicate_families` (O(n^2) word-5-gram Jaccard >= 0.8 with naive chaining) -- classified STALE_PLAN/prototype, not used.

STALE: local `STATUS.md` (S083, declared OBSOLETE by `reports/h_state/ssot15_state_program_inventory.md`).

## 3. What the whole planning corpus says about recipe identity (and what was missing from the earlier 07I design)

Read in full for this topic: SSOT sections 192.5, 247.13, 257A.15, 257E.13, 264 (all), 271.5, E13E-05, Recipe.20 `duplicate_group_id`; Master Plan Laws 10/13/15, H1 (ID table), R2, B07, B14 (SX-14-03), RS-07; Detailed Plan 7.7 and F.3. For L13E/L14/L15/L16/FlavorTwin only the block-level goals, anchors and gates were read (the 1.8 MB SSOT body for those levels was not read in full -- `ssot15_state_program_inventory.md` makes the same disclosure); no statement below depends on unread bodies.

Newly weighed decisions (not wrong before, but not previously cited):
1. SSOT 257A.15 prescribes the order **exact hashes -> near-duplicate detection -> duplicate families -> source/template families -> assign before splits -> freeze**. The pipeline already did exact first; it is now an explicit, separately resumable phase.
2. SSOT 264.8 / E13E-05: **no universal identity threshold until calibration is stable across sources and dish categories**; 264.2: "do not freeze scalar weights a priori". The pre-registered ranking score therefore stays a *ranking aid*, its components are stored separately, nothing coalesces on it.
3. Master Plan H1 / Detailed Plan 7.7: MinHash >= 0.8 is only an *initial duplicate-candidate rule*, "not an automatic proof".
4. Master Plan R2 class C1: MinHash dedup over 1M+ recipes = **sharded batch jobs with checkpoints** -- exactly the redesign.
5. Detailed Plan F.3: derivative-family graph built from raw hashes + normalized hashes + signatures + near-duplicate candidates, *borderline matches reviewed*, grouping precision sampled; "same verbs, different foods are not duplicates" -- consistent with the unlabeled 400-pair calibration packet.
6. Master Plan R4 + H2: raw third-party text is stored only where the licence permits and any dataset with an unclear licence needs human approval (H2); DELTA `ACQUISITION_PLAN.md` marks every licence `[U]` until checked -> consistent with `recipe_source_usage_registry_v1.csv` (no licence invented; Food.com/TASTEset stay UNREGISTERED + H2 items). No new acquisition was performed in 07I-R.
7. DELTA_PLAN_v4: the 60k->100k **Silver** corpus is Lane C, staged and gated; our 612,782-record base is a SOURCE corpus (tier SOURCE_RAW), not Silver.
