# Step 16 review workspace — DRAFT, pending Parv and H4

2026-10-28. The findings below are AI technical review, not Parv's comments,
human labels, approval, or a freeze. Parv's review comments: PENDING.

Follow-up AI review: `reports/review/AI_REVIEW_2026-10-28.md` is the current
disposition of the initial findings below. The EVT FAM: namespace mismatch is
fixed in the draft, and a pure semantic review overlay now reports several
cross-field gaps. H4 is still pending. Parv selected pilot v2 in D-040, retaining
v1 for comparison; only Kush's confirmation remains pending for that choice.

S151 follow-up: the separate rc2 proposal now implements explicit claim metadata,
all eleven typed AST payloads, arithmetic checks and exact rational serialisation.
See `metadata_quantity_contract_v2_DRAFT.md` and its synthetic examples. This
implements proposed solutions to the metadata/AST gaps without migrating rc1 or
freezing them. Grounding/integration, history policy, coverage acceptance and the
human pilot remain open. The additional legacy zero-multiplier defect is recorded
in that build note; it is not silently patched in the older path.

## Checks completed

- Baseline unit suite: 1,510 passed, 1 skipped, 8 deselected
  (`-k 'not test_transition'`).
- Ten draft schemas pass their existing Draft 2020-12 and compatibility tests;
  the ten frozen v0 schema hashes are unchanged. The targeted schema, vocabulary,
  preregistration-guard and similarity-registry suite passes 147 tests after the
  independent CSV parser fix (two new synthetic regression cases).
- All ten enum registry CSVs and every CSV in `registry/processes/` and
  `registry/tools/` parse with consistent row widths. Process hierarchy: 1,112
  unique IDs; tool hierarchy: 329 unique IDs. Neither has dangling parents or
  cycles. This checks structure, not the correctness of human vocabulary choices.
- EVD, COND, SRC, MEAS and SNAP match their full baseline hashes. STUDY and `_ids`
  preserve the baseline byte prefix. No ledger changes made by this review.
  The batch-1 README's historical note about the STUDY-size test failure is
  stale: the current lineage guard permits append-only growth and its test passes.
- The text-strata file matches the D-038 hash
  `ddbd302801e5bebd1bccb563fe3223eadb24bca1f70bf09b3ca761e041580728`.
  Parv's pilot-column choice is v2 (D-040, DRAFT_PENDING_KUSH); no sample drawn.

## Reproduced issues and review questions

1. **Family IDs disagree across drafts.**
   `registry/processes/process_hierarchy_v1_DRAFT.csv` uses `FAM:<family>` roots,
   whereas `schema_drafts/EVT.draft_v1.schema.json` accepts only `PROC-######`
   for `process_family_id`. A synthetic record using the actual hierarchy root
   `FAM:DRY_HEAT` is rejected; an
   unrelated syntactically valid `PROC-999999` is accepted. The batch-2 README
   already lists the PROC-family encoding as an assumption. H4 must settle the
   encoding; do not mint ledger IDs or reinterpret existing PROC IDs silently.
2. **The metadata triple is optional and partial.**
   The plan's Step 16 Method cell calls for per-field metadata on STATE/QNT.
   A synthetic measured STATE variable without `meta` validates today. New
   top-level quantity bounds also lack a metadata wrapper. Decide how v1 records
   require complete metadata while v0 fixtures retain compatibility. Keep the
   independent value-shape status and evidence status axes distinct.
3. **Quantity ordering needs semantic validation.**
   QNT accepts synthetic `normalized_mass_low_g=130` with
   `normalized_mass_high_g=100`. POR likewise accepts synthetic bounds
   `mass_low_g=150`, `mass_high_g=100`. Add an ordering invariant to the appropriate semantic validator before
   operational use; do not infer missing bounds or replace UNKNOWN with zero.
   Cross-field comparison is not provided by the current standard JSON Schemas.
4. **AST payloads remain incomplete by design.**
   A QNT AST containing only `{"node_type":"RANGE"}` validates. The batch-2
   README explicitly defers type-specific payloads. H4/quantity-contract review
   must define operands, rational denominators, and ALTERNATIVE behavior before
   these ASTs can be treated as executable arithmetic.
5. **Vocabulary interpretation still needs humans.**
   `annotation_mode` has only OPEN; most enum definitions are placeholders.
   Eight tool nodes lack a proposed parent. CANDIDATE/POS-unchecked process
   aliases and informational UNVERIFIED tool structural classes must retain
   their caveats. Parsing and hierarchy tests do not approve these mappings.
6. **History fields retain a proposed restriction.**
   The MODEL/SIMULATED-only rule for populated history variables is an existing
   interpretation of the recipe-text prohibition, not a newly approved policy.
   Confirm it at H4, including how externally measured history would be handled.

The initial review changed no schema, vocabulary, sampling frame or human
annotation. The later draft-only schema correction is identified above. The
issues are inputs to H4 and the Step 19 pilot problem log;
16c still waits for the pilot. The full SSOT was not loaded.
