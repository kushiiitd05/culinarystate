# S161 — real-data runs of the S154–S160 tools (2026-11-04)

**Status:** AI engineering runs, counts only. Nothing here is a human gate, a gold score, a review or a signature (D-045). Run by the coding agent in Kush's cloud session on branch `cloud/s161-real-data-runs`.

## 1. Data bundle

- Source: the five-file Drive bundle (SHA256SUMS + tier-1, regenerable outputs, small misc, A1 sibling). The first attempt was refused by the network policy (HTTP 403 on CONNECT to `drive.usercontent.google.com`). After Kush allowed the host, all four archives matched `SHA256SUMS.txt` (tier-1 = 970,136,792 bytes). The optional tier-2 archive was not downloaded.
- Archive safety: 7,666 entries checked; 0 absolute paths, 0 `..` components, 0 links. Extraction overwrote no tracked file (`git status` clean after `git checkout -- .`).
- **macOS AppleDouble files:** the archives carried 3,814 `._*` resource-fork files (all with magic `00051607`, none tracked), including 697 in `data/raw/gutenberg`, 311 in `data/raw/wikibooks` and 25 in `data/raw/openalex`. They were deleted before the final runs. A first 13a-0 run had counted the 25 OpenAlex ones as `files_unreadable`; after the cleanup it reports 0, and all S161 outputs below come from runs after the cleanup.
- Protected ledgers: `verify_baseline(registry/baseline_ledger_hashes_08a_v1.csv)` = 7/7 before the runs, and every tool's own before/after check passed.
- `data/raw/`, `data/interim/` are git-ignored (`.gitignore` L1–L2, checked with `git check-ignore`).

## 2. Test suite with the data

`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest tests/unit -q -p no:cacheprovider`

- Before the S161 fix: **3212 passed, 2 skipped, 1 deselected, 0 failed, 0 errors** (329 s). The cloud-without-data baseline was 3185 passed, 17 skipped, 1 deselected, 1 failed + 11 errors; those 12 now pass, and 15 tests that skipped without data now run.
- After the S161 fix (3 new tests): **3215 passed, 2 skipped, 1 deselected, 0 failed** (section 5).

## 3. Runs and real numbers

| # | Tool | Exit | Output |
|---|---|---|---|
| 1 | `tools/step16_rc2_grounding_dryrun.py --workers 4` | 0 (50 min) | `reports/step16/rc2_grounding_dryrun_counts.json` |
| 2 | `tools/step17b_rung_a_dryrun.py --seed 20261104` | 0 | `reports/step17/rung_a_dryrun_counts.json` (pre-fix copy `rung_a_dryrun_counts_prefix_S161.json`) |
| 2b | same, `--sample-size 612782` (full corpus, extra) | see 3.2b | `reports/step17/rung_a_dryrun_counts_full_corpus.json` |
| 3 | `tools/step12_0_register_local_files.py` | 0 | `registry/staging/step12_0_src_snap_proposed_v1.jsonl` |
| 4 | `tools/step12_local_stage.py --defaults` | 0 | `reports/step12/step12_local_counts_v1.json`; staging in git-ignored `data/interim/step12_local_staging_v1/` |
| 5 | `tools/step13a0_seed_corpus.py` | 0 | `registry/evidence/seed_corpus_13a0_full_v0.jsonl`, `reports/step13/S157_13a0_seed_corpus_full_{counts.json,report.md}` |

### 3.1 Step 16 rc2 grounding (all families)

- Recipes read: **612,782** (A1/BBC 11,934; Food.com 522,517; Gutenberg segments 73,955; TASTEset 700; Wikibooks 3,676). All five families `READ`.
- Ingredient lines grounded: **4,281,956**; contract-valid 4,281,954; exceptions **0**.
- The 2 invalid lines are Wikibooks `INVERTED_INTERVAL` issues (the only issue code). The invented-value audit (`audit_invented_values`) reports through these issue codes, so **invented grams = 0**.
- rc2 mass (Q0): **33,373 lines (0.78 %)**; Q6 (no gram value) 4,248,583. Mass routes: `NO_INGREDIENT_LINK` 4,018,242 (no POR records or ingredient links were supplied to this dry-run: `por_records_supplied 0`, `ingredient_links_supplied false`), `NO_QUANTITY` 201,078, **`UNSUPPORTED_EXPRESSION` 21,172**, `AST_EXACT_PHYSICAL` 27,626, `AST_PACKAGE_SOURCE_STATED` 4,567, `PARENTHETICAL_SOURCE_STATED` 1,180, `QUALITATIVE` 5,913, `OPEN_OR_UNAVAILABLE_OPERAND` 2,163, `ALTERNATIVE` 15.
- Per family, unsupported expressions: A1/BBC 14,345; Food.com 2,487; TASTEset 289; Wikibooks 4,051.
- Legacy vs rc2 mass: both MEASURED 33,239; legacy MEASURED → rc2 UNKNOWN 6,047; legacy QUALITATIVE → rc2 UNKNOWN 6,519; RANGE kept 134; RANGE → UNKNOWN 80. rc2 is stricter than the legacy parser; it never turns a legacy UNKNOWN into a value.
- Lines flagged: 270,737. Largest flags: `UNSUPPORTED_OR_UNSTATED_QUANTITY` 203,092, `CONVENTION_NEEDS_SOURCE` 26,902, `locale_ambiguous` 15,947 / `LOCALE_AMBIGUOUS` 14,385, `UNRESOLVED_ALTERNATIVE` 10,586.
- **Gutenberg segments have 0 ingredient lines by design:** `recipes.corpus.iter_rec_corpora` yields `ingredient_lines: []` for Gutenberg (historical prose), so all 73,955 are `recipes_without_ingredient_lines`. Not a reader failure.

### 3.2 Step 17b Rung A, seeded 1,000-recipe sample (seed sha256 `1037f2ed…01dc`)

- 612,782 recipes streamed, 1,000 sampled (842 Food.com), 997 with steps; exceptions 0; baseline check PASS before and after.
- **First run: invented_count 23**, all `UNIT_NOT_IN_SPAN`, in 9 Food.com texts. Root cause and fix: section 4.
- **After the fix: invented_count 0** (values checked 145,899).
- Validators: V1 0 texts failed; **V2 5 texts failed (`INVERTED_INTERVAL` 5)**; V3 0 failed (not checked: 914 `CATEGORICAL_FIELD_NO_VOCAB__structural_class`, 2 `…temporal_relation_1`); V4 0 failed (its five scope items are listed as not checked for every text, as designed).
- Stage failures: quantity grounding `UNRESOLVED` 564, `PARSE_FAIL` 12; linking `NO_VALID_CANDIDATE` 1,106, `UNRESOLVED` 126; references `UNRESOLVED` 185, `NO_VALID_CANDIDATE` 73.
- Output sizes: 15,472 events; entities 8,344 ingredient lots, 12,258 intermediates, 2,896 mixtures, 164 reserved portions; ambiguity count 1,315.

### 3.2b Step 17b Rung A over the full corpus (extra run; not the specified 1,000-recipe check)

FULL_CORPUS_PLACEHOLDER

### 3.3 Step 12.0 proposed registration

- 3 `PROPOSED_SRC` rows (DS-006 USDA R2 yields, DS-007 FNDDS, DS-014 INFOODS) and 7 `PROPOSED_SNAP` rows; 1 file already registered (`SNAP-000006`, Bognar PDF).
- `ids_minted 0`, `ledger_rows_appended 0`; schema errors 0. Gaps on every row: `created_at`, `created_by` (and `retrieved_at` on SNAP rows).
- DS-014 (3 INFOODS files): licence UNKNOWN, `H2_OPEN` (H2 item 9), `HUMAN_APPROVAL_REQUIRED`, `LOCAL_ONLY`.
- Per D-049, nothing is appended to `ledgers/data/SRC` or `SNAP` until Kush reviews this file and the re-baseline is done.

### 3.4 Step 12-local staging (R2 + Bognar)

- USDA R2: 173 rows staged, 0 skipped, 70 with flags; cooking yield MEASURED 173; fat and moisture change MEASURED 150 each; dispersion SD 110, not reported 63; `min`/`max` not present in the file; 3 unmapped columns.
- Bognar remaining tables: all 11 found (T2, T13, T16, T29, T31, T32, T35–T39); **1,693 cells staged**; T36 `NO_ROW_MATCHES_COLUMN_COUNT` (0 cells); 58 rows skipped or with table problems. Value status: MEASURED 766, `CENSORED_GT_CAP_CANDIDATE` 914, NOT_AVAILABLE 13. Method mapping: `POSITIONAL_ONLY_UNCONFIRMED` 1,268, `EQUAL_GROUPS_AND_POSITION_AGREE` 247, `UNMAPPED_NO_METHOD_LINE` 178. Basis A 705, B 810, UNKNOWN 178.
- The report's `estimated_cells` (528) is far below the 1,693 cells staged. Reported as is; this AI run does not resolve it, and it is part of the G12 audit.
- Diff against the latest active EVD (17,978 rows): 0 staged Bognar cells match an existing EVD key exactly; 251 of 396 staged constituent–method pairs are already seen in existing Bognar rows; 11 constituents are shared with USDA R6 (G08-9 context). `resolution NOT_RESOLVED_REPORT_ONLY`.

### 3.5 Step 13a-0 seed corpus (full)

- 1,868 records read from 8 artifacts → **715 seeds, 703 with a valid DOI**, 12 without; 0 invalid syntax; 1,153 DOI records merged into earlier ones (exact normalised DOI only). Network calls 0; abstracts not included (519 OpenAlex abstracts dropped).
- Licence: `STATED_BY_INPUT_UNVERIFIED` 327, UNKNOWN 388. TDM: UNKNOWN 715. OA flag TRUE 517, FALSE 190, UNKNOWN 8.
- The seed file holds DOI/title/venue/year metadata only.

## 4. Failure found on real data and its fix (test first)

- **Symptom:** Step 17b invented_count 23 (`UNIT_NOT_IN_SPAN`), all TEMPERATURE claims in Food.com texts.
- **Diagnosis** (character-shape masks only, no text printed): every case is a temperature written `<number>ºF` or `<number>ºC` with `º` = U+00BA MASCULINE ORDINAL INDICATOR, not `°` (U+00B0). `evidence.conditions.TEMP_RE` accepts `º` as a degree marker, so Rung A correctly emits the literal unit F/C. But U+00BA is a Unicode letter (category Lo), so the auditor's whole-token check (`_unit_token_in`, added for S155 review R1) read `ºF` as one word and refused the unit. The value and unit really do appear in the span: this was an auditor false positive, not an invented value.
- **Test:** `tests/unit/test_s161_ordinal_degree_unit.py` (synthetic text): `ºF`/`ºC` literal units pass; the R1 letter-boundary refusals (`Cook 180` with unit C, `90aF`) still refuse; Rung A on a synthetic `ºF`/`ºC` text invents nothing. It failed before the fix (commit `d09a3aa`).
- **Fix:** `src/culinarystate/extraction/auditor.py` `_unit_token_in` allows `º` immediately before the unit (commit `95e8401`). No other auditor rule changed. `auditor.py` is not bound by any signed or unsigned record.

## 5. Verification

- Targeted: the 3 new tests plus the 17a auditor and review-fix tests: 54 passed; all `-k 17` tests: 208 passed, 1 skipped.
- Full suite after the fix: **3215 passed, 2 skipped, 1 deselected, 0 failed, 0 errors** (346 s; the 3,212 before plus the 3 new tests).
- Every committed output was inspected: counts, hashes, codes and ids only (`contains_recipe_text`/`contains_text` false, `contains_recipe_ids`/`contains_ids` false in the 16/17b reports; the 13a-0 seed file has paper metadata only). No recipe text, ingredient line, recipe title or abstract is in git, a commit message or this report.

## 6. What this does and does not establish

- Every S154–S160 tool that is allowed to run on real data has now run on the full local bundle: Step 16 (S154), Step 17b (S155), 12.0 / 12-local / 13a-0 (S157).
- Not run, by design or by gate:
  - S156 (event engine, 26g census), S158 (kinetic/mechanism contracts, 23a) and S159 (simulators) are libraries used by later steps; they have no standalone real-data run.
  - S160 tools refuse: 15a.R seal (no 15.0 marker lines, fraction or seed; `check --decision D-053` lists 7 blockers), the Step 35 runner (no SIGNED record), 29-diag and Step 30 (no human values).
  - Step 19 P1 draw (C2): prerequisites met (D-048), not run here; it waits for Kush's go after the frame/strata rebuild.
- None of these numbers is a G16/G17 gate result. Coverage, unsupported-expression and failure counts are engineering counts for Kush and Parv to read.

## 7. Still needs humans

1. **Checkpoint H-A remainder** (D-053 accepted the AI recommendations; these stay open):
   - the RESERVED fraction and a high-entropy seed (O1), and the seal decision (I2, O2);
   - Step 35: P-1..P-5 answers; S-1 chemistry reviewer and S-2 human finding on the 204 deprecated edges (or recorded deviations); Q-1, Q-3, Q-4; then the Route B regeneration on the Mac and the SIGNED record committed from the signer's own session (O5);
   - δ_30, ρ, c_floor, the 34a.0 circularity check, the 34c thresholds and actions, and the 15a freeze-record and 29-diag formats.
2. **Review of these runs:** the 12.0 proposed rows (then the D-049 re-baseline); the 12-local G12 audit, including T36, the positional-only method mapping and `estimated_cells`; the Step 16 unsupported-expression and flag counts; the Step 17b V2 inverted intervals and the auditor fix.
3. **C2 go:** rebuild the P1 frame and strata with data, then the draw.
4. H2 licence decisions (including DS-014 / H2 item 9), expert questions EQ21-01..14, and the 26.0 inputs listed in D-052.
