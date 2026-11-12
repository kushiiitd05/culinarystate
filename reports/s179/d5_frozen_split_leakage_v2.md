# Frozen D5 split/unit and leakage refresh — 12 November 2026

**AI_PRECHECKED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
Reviewer: author-only review (AI-delegated). This is a provenance/count audit, not independent gold, a scientific
gate pass or a newly created training/test split. Original benchmark files, preregistration, scorer, old split
registry and recorded results remain unchanged.

## Artifacts and scope

- `registry/d5_frozen_split_registry_v2.csv`: eight frozen evaluation block records.
- `reports/s179/d5_frozen_split_units_v2.csv`: 74 question-to-unit records, with no source questions or recipe text.
- `reports/s179/d5_frozen_split_leakage_v2.json`: counts, input/code/output hashes, exact run timestamps and limits.
- `tools/s179_frozen_split_registry.py`: refuses existing outputs and checks the D5 freeze before reading units.

The source is freeze D5-BENCH-2026-11-10b. Unit grouping uses recipe ID for S1/S2; the ordered identifier tuple
(ingredient, process1, process2, target-SVAR set) for P/C; and question ID for U/X. U/X are authored control
questions, not a stochastic train/test draw. S/PC use the original draft seed plus D-090 KEEP/DROP/rank review.
The cell key is a registry description, not a new frozen scientific ontology or an independence claim.

## Frozen blocks

| Block | Questions |
|---|---:|
| C | 10 |
| P1 | 10 |
| P2 | 10 |
| P3 | 10 |
| S1 | 12 |
| S2 | 12 |
| U | 5 |
| X | 5 |

There are 24 distinct S recipes: 22 Gutenberg segments and 2 Wikibooks recipes. S1/S2 share no recipe IDs.
That exact-ID nonoverlap does not establish near-duplicate or source-family independence. Gold remains
AI_DRAFTED_GOLD, not independent human gold. P/C references 79 distinct EVD IDs; overlaps are C/P1=2,
C/P2=1 and P1/P2=9. These shared evidence IDs are explicitly retained, not removed to obtain a zero.

## Refreshed recipe exposure checks

- Gold recipe index: 0 of 24 S recipes overlap the 50 gold IDs.
- Provisional duplicate-group/family membership: 0 S recipes in a gold duplicate group or gold family.
- Seven declared seeded Rung A/dev sample reconstructions: 0 S-recipe overlaps in each.
- J4 manifest: 0 overlaps against 68 recorded recipe-ID hashes.
- Linker concept exposure: 34 distinct S1 gold ING IDs fall into train=25, dev=4, test=5 buckets.
  The 27 P/C question ING IDs fall into train=16, dev=3, test=8. Concept exposure is not recipe-text exposure.
- Full-corpus label-free runs and their subsequent code adjustments are prior exposure; the benchmark is not
  a fresh source-family-heldout experiment.

Identity groups remain PROVISIONAL_STAR_V1/uncalibrated. A zero match in them is not proof that no near duplicate
exists. Human calibration failures and provenance limitations remain on record.

## Evidence-resource and development exposure

- All 79 frozen P/C gold EVD IDs occur in the 17,458-row reconstructed DEL-2 retention pool.
- Retrieval-silver overlap: 2 gold EVD IDs, 1 gold cell, and 13 of 44 ingredient/process pairs.
- The 600-query silver reconstruction contains 2,200 relevant EVD rows; 30/30 sampled BM25 top-100 lists
  reproduce the stored lists exactly. This is a spotcheck, not full reproduction of every ranking.
- No frozen P/C question exactly matches the 20 ladder-development questions under the existing normalizer.
- Three of the 10 P3 ingredient/process pairs have evidence for another target; the existing P3 gold boundary
  is not broadened, and NEG-0051/D-092 remain unchanged.

The by-split role counts in JSON are DEL-2/pre-seal exposure counts, not reconstructed post-seal 29-diag
assignments. A learned model fitted on that evidence resource cannot be presented as held out on these cells.

## Explicit incomplete NER check

The NER exact-line section is NOT_RECOMPUTED, FileNotFoundError. The first missing input is
`data/interim/gutenberg/recipes.jsonl`. The supplied S-context file has steps, not ingredient lines; it is not
substituted to fabricate an ingredient-line comparison. The prior draft-era NER result is not copied into the
new frozen-set result as if it had been rerun. Other checks above completed locally.

## Historical evaluation records

The report binds the existing DIAG29 result and 07.A-R1 manifest by hash and selected recorded fields.
Their status is RECORDED_PROVENANCE_NOT_REDERIVED. No private sealed list/seed was opened, no post-seal
assignment was recreated, and no new packet or human labels were produced. 07.A-R1 remains NOT_RUN under D-085.

Actual diagnostic naming is S-5 food-group-disjoint and S-6 study-disjoint; the historical draft registry kept
its earlier S-5 study-disjoint mapping. That record is preserved rather than silently edited.

## Verification and acceptance

TDD first reproduced the missing tool, then six tests passed: privacy/minimal units, U/X and two-process cells,
explicit overlap reporting, assignment-hash sensitivity, duplicate-ID/missing-ID refusal and overwrite refusal.
The actual artifacts were independently re-read: 74 unique question IDs, eight blocks, every per-block count
and ID/unit hash verified, and original registry/board/freeze bytes compared unchanged to the base commit.

Run started 2026-11-12T07:30:06.109886+00:00; completed 2026-11-12T07:30:12.590886+00:00.
Source/code/output hashes in JSON make these counts checkable without exposing source text.

The D5 registry refresh is complete as an artifact. Full T9-C09-R1/R2 acceptance remains limited by the NER
source absence, provisional identity assumptions, historical private assignment scope and the orchestrator
compute/EXP recording requirement. No claim of zero groups crossing every possible evaluation boundary is made.
