# Step 35.0 pre-registration v2: explicit-first representation baselines (DRAFT, READY FOR SIGNATURE, UNSIGNED)

**Status: `READY_FOR_SIGNATURE_UNSIGNED`.** Written 2026-11-03 by AI worker "ksh" (an agent, not Kush or Parv). Under D-045 W1 (`DECISIONS.md` L269) this is an AI draft; Kush and Parv review it and their review is final. Nobody has signed it. It authorises nothing until both sign the hash record named in section 6 (G35-PRE, `THR-35P-01`). The v1 draft and its two unsigned hash records are unchanged; v1 is not edited and stays the historical record.

**What v2 is.** v2 = (1) the full v1 text, bound by sha256 `47c6ba6e6c567a3861c72625de28b78e0fa67c8a1462396fb1e18b421a03d933` (`reports/step35/preregistration_35_0_v1_draft.md`), normative except where sections 2-5 below supersede a named clause; (2) the 43 rows `THR-35P-01..43`, unchanged, extracted byte-for-byte from v1 Appendix A into `reports/step35/35_0_v2_threshold_rows.csv` (tested); (3) the integration of the recorded human answers (D1-D8 in D-039, cuisine rulings in D-040, with D-036/D-037/D-038); (4) the inputs and code bound by sha256 (section 6); (5) Appendix P, the AI-review amendment proposals of D-041, **kept OPEN and NOT ADOPTED**. Where v2 text and v1 text conflict, v2 prevails; no threshold value changes.

**Data seen by this drafter:** none beyond file sha256 values and the text of the cited documents. No count, label, score, similarity, split or model output was computed.

---

## 1. Recorded human answers used here (verbatim)

- Parv's batch reply (D-039 Source, `DECISIONS.md` L226; `reports/step35/35_0_parv_review_DRAFT.md` L19): "D2 Approved D3 yes D4 yes d5 Go. Dont wait, but record the decision D6 Yes to both rules D7 yes to all D8 Yes".
- D1 (`35_0_parv_review_DRAFT.md` L10): "(a), all 43 threshold rows as drafted; reported in the session handoff"; D-039 L227: "D1 remains the earlier choice (a), not a signature."
- D-039 Review choices (L227): "D2 taste-label/confirmed-negative/source-control rules approved; deprecated-edge audit reviewer still pending. D3 banned-input and local-output stance accepted (H2 licence approval remains separate). D4 separate derived/explicit claims and source controls accepted, including a possibly empty headline set; specific mapping, conflict, continent, coverage and reviewer choices not answered. D6 descriptive-only until 07I-S and 0.80 linking floor accepted; crosswalk audit commitment not supplied. D7 all four proposed claim/profile rules accepted. D8 learned models stay deferred until explicit results and signed addendum."
- D-039 D5 action (L228): "pin its installed distribution version 2026.3.6 as optional project extra `step35` ... This is Parv's instruction, not a claim of Kush approval." (`pyproject.toml` L7: `step35 = ["rdkit==2026.3.6"]`.)
- D-040 Lookup rulings (L233): "Tex Mex, Cajun, Pennsylvania Dutch and Native American -> REGION/Americas; Cantonese, Szechuan and Hunan -> REGION/Asia; Creole, Hawaiian and Jewish -> REGION/MIXED. All REGION rows carry cuisine UNKNOWN. American -> CUISINE/American/Americas. Georgian, Southern, Roman and Oriental -> UNKNOWN for cuisine, continent and level. These are Parv's explicit review choices, not agent-inferred labels."
- D-040 REGION definition (L234): "extends to below-country regions, following the existing D-037 Southwestern U.S. precedent. Unclear continent -> MIXED; unclear meaning -> UNKNOWN."
- D-040 Other cuisine choices (L235): "accepts Middle East/Southwest Asia, Southwest Pacific and Mediterranean = REGION/MIXED; Polynesian = REGION/Oceania, without exceptions. Accepts the 20-recipe tag reporting cut and 12.9% mapped cuisine coverage with the limitation disclosed. Exclude conflicting-cuisine recipes from single-cuisine scoring while retaining their CONFLICTING flag and count; no scored CONFLICTING class."
- D-040 Owners (L237): "Parv owns the 50-crosswalk audit (D35-7, approximately 2 h), not yet done. Chemistry reviewer pending, Kush to arrange ... Cuisine expert also pending. Neither audit is treated as complete or waived."
- D-036 (L209): Food.com cuisine is "derived from Food.com's own tags through a written, pre-registered tag-to-cuisine mapping ... signed by Kush and Parv BEFORE any cuisine statistic is computed"; labels "flagged `DERIVED_FROM_TAG` and never mixed with explicit labels in one claim; recipes with no mappable tag stay `UNKNOWN`".
- D-037 item (1) (L215): pan-regional tags "are kept as continent/region-level labels only (`DERIVED_FROM_TAG`, cuisine UNKNOWN); they are used for continent analysis and never for single-cuisine analysis."
- D-033 caveat (carried from v1 sign-off sheet s1 item 6): claims resting on 07I-C labels say "single-reviewer basis".

These are single-reviewer answers (Parv). Kush's own answers to D1-D8 are not recorded anywhere; his signature on the section 6 record is the act by which he accepts or does not accept them.

## 2. Integration of D1-D8

| D | Recorded answer (source) | Integrated in v2 as | Still open after v2 |
|---|---|---|---|
| D1 | "(a), all 43 threshold rows as drafted" (parv review L10; D-039 L227) | `THR-35P-01..43` unchanged, byte-identical in `35_0_v2_threshold_rows.csv`; covers D35-1, 3, 5, 13, 15, 17, 19-24 because those decisions are encoded in the rows (D35-3 = row 33, D35-5 = rows 06/21/35, D35-13 = rows 08/09/17/40/41, D35-17 = row 31, D35-19 = row 28, D35-20 = row 38, D35-21 = row 39, D35-22 = row 37, D35-23 = row 40, D35-24 = rows 41/42) | Kush's acceptance (signature). The D-041 amendments of rows 36 and 24 are OPEN (Appendix P); D1 is not read as accepting them (D-041 L245) |
| D2 | "D2 Approved" (L226): Sweet/Bitter/Sour map, confirmed negatives only, database-source control (parv review L11) | `THR-35P-04` and `THR-35P-36` as drafted; v1 s4.4 unchanged | Chemistry reviewer for the map ("before signature", row 04) and the human DEPRECATED-edge reason ("before signature", row 36(c)) not done: section 5 E-5. P-1, P-2 OPEN |
| D3 | "D3 yes" (L226): banned inputs, local-only handling | `THR-35P-38` (BAN-35-1) and `THR-35P-31` as drafted | H2 licence decisions stay Kush's (parv review L12) |
| D4 | "D4 yes" (L226) plus D-040 rulings (L233-L235) | Section 3 (cuisine). `THR-35P-22`, `26`, `41` unchanged; empty headline set is a valid result | Cuisine expert (D35-9) pending; P-3 OPEN |
| D5 | "d5 Go. Dont wait, but record the decision" (L226; D-039 L228) | rdkit 2026.3.6 is the pinned optional extra `step35` (`pyproject.toml` L7); v1 s3/s4.2 "waits for a dependency decision" is superseded; rdkit rungs now wait only for bound scoring code (E-3). LightGBM and TabPFN stay undecided and off (v1 s4.2, D35-2) | Kush's confirmation (Parv's instruction "not a claim of Kush approval", D-039 L228) |
| D6 | "D6 Yes to both rules" (L226): descriptive-only until 07I-S; linking floor 0.80 | `THR-35P-03` and `THR-35P-19` as drafted | 50-crosswalk audit (Parv, D-040 L237) not done; Q-1 (does `recipe_split_groups_v1.parquet` count as 07I-S?) |
| D7 | "D7 yes to all" (L226): FUNCTIONAL stays HYPOTHESIS; taste classes are the SENSORY molecule set; SIM-13 outside the nine; five-compound headline floor | D35-10 (HYPOTHESIS), D35-16, D35-11 (`OUTSIDE_NINE`, RESEARCH_ONLY), `THR-35P-32` as drafted | none beyond signatures |
| D8 | "D8 Yes" (L226): learned models deferred | `THR-35P-29` unchanged; v1 s14 unchanged | none beyond signatures |

Not answered by anyone and not covered by a row: D35-12 (similarity registry v2 id scheme and statuses, H4). It stays open; 35e may run its lint on working ids only, as v1 s8.1 says.

## 3. Cuisine labels (supersedes v1 s7.2 opening paragraph and item (d))

v1 s7.2 says cuisine labels exist for 9.81% of recipes and "0% for Food.com", and item (d) says "results on Food.com are impossible (no labels)". That was written before D-036. In v2:

1. **Explicit labels** (`cuisine_if_explicit`, BBC/Gutenberg/Wikibooks) and **derived labels** (`DERIVED_FROM_TAG`, Food.com) are separate label sets. They are never pooled in one claim or one class count (D-036).
2. **Derived labels** come only from the bound lookup `registry/cuisine/cuisine_lookup_v1_DRAFT.csv` and map `registry/cuisine/foodcom_tag_cuisine_map_v1_DRAFT.csv`, exact casefolded tag match, no fuzzy matching (`reports/step35/foodcom_cuisine_derivation_README.md`). A recipe with no CUISINE-level tag is UNKNOWN, never guessed (D-036).
3. **Levels.** CUISINE terms feed cuisine analysis; REGION terms (pan-regional per D-037 item 1, and below-country terms per D-040 L234) feed continent analysis only and never single-cuisine analysis; MIXED gives no continent; UNKNOWN gives neither. Parv's term rulings are exactly the D-040 L233 text quoted in section 1; the bound lookup carries them as `basis = PARV_REVIEW_D040_*`.
4. **Conflicts.** A recipe with more than one distinct CUISINE label is flagged CONFLICTING, excluded from single-cuisine scoring, and its flag and count are retained; there is no scored CONFLICTING class (D-040 L235). This answers question (ii) of the v1 sign-off sheet D4. Continent conflicts are flagged the same way.
5. **Coverage.** The 20-recipe reporting cut and the 12.9% mapped cuisine coverage are accepted with the limitation disclosed (D-040 L235); 12.9% is a mapping-coverage count from the README, not a result.
6. **Unchanged from v1:** `THR-35P-22` (a class enters headline macro-F1 only with >= 100 recipes and >= 2 source families, so derived-only Food.com classes cannot qualify alone), `THR-35P-26` (SOURCE_CONFOUNDED flag), `THR-35P-41` (PE-35d), the source-identity-only baseline, and v1 s7.2 (a): no cuisine-class headline before the ontology is reviewed by a cuisine-aware reviewer. Parv's rulings are single-reviewer choices and do not satisfy (a).

## 4. Other v1 clauses superseded or updated

| v1 clause | v2 reading |
|---|---|
| Header: "Status: DRAFT_PENDING_H4"; signed output name `reports/step35/preregistration_v1.md` (+ sha256) (v1 header, s15) | The signed form is this document plus `preregistration_35_0_v2_package.sha256.SIGNED.json` (names pinned in the runner, section 5 E-1); no file is renamed |
| s1.3 "the evaluation entry point must refuse ... (an engineering control, to be built)" | Built: `src/culinarystate/representation/explicit_runner.py` (`run_explicit_baseline`) over `prereg_guard.require_signed_prereg`; both are bound inputs |
| s3 software environment ("rdkit is not installed in any environment"); s4.2 rows waiting for an rdkit dependency decision | Historical server census kept as history. Dependency decision: D5 (section 2). Rungs still need bound scoring code (E-3) |
| s3 "Cuisine ontology ... does not exist" | The lookup and map exist and are bound (section 6); an ontology review by a cuisine expert is still pending |
| s3 / s9 "07I-C labels, 07I-S `SPLITGRP-REC-` do not exist" | `ledgers/recipe_identity_v2/recipe_split_groups_v1.parquet` now exists (07I-C operating points, `basis = single_reviewer_basis`). Whether it is "07I-S" for `THR-35P-03` is not decided here (Q-1); until a human records that it is, recipe/cuisine runs stay descriptive and are labelled `DESCRIPTIVE_CONSERVATIVE_GROUPING` |
| s7.2 opening and item (d) | Section 3 |
| Appendix A `registry_status = DRAFT_PENDING_H4` | Unchanged bytes. After both signatures the rows are appended verbatim to `registry/preregistered_thresholds_v1.csv` by a separate recorded step with human signer fields (as D-046 did for THR-19P); not done here |

Everything else in v1 (sections 1-17, Appendices A-C) stands unchanged, including the statements about the 204 DEPRECATED edges (P-2 is OPEN).

## 5. Execution rules added by v2 (each only restricts)

- **E-1 Entry.** Every explicit-baseline run (35a-35e) enters through `run_explicit_baseline(task, runner, root=...)`. It checks this document against `reports/step35/preregistration_35_0_v2_package.sha256.SIGNED.json` with two distinct signers (or a written single-signer override), an ISO date, the current document sha256 and the current sha256 of every input that task requires (`required_inputs(task)`). Callers cannot pass another document or record. Today only the UNSIGNED template exists, so every task is refused (tested).
- **E-2 OPEN items block what they touch.** Until a human decision closes an Appendix P item, the analyses it touches are not run: P-1 and P-2 -> 35a taste tasks (PE-35a, scored classes, NC35-14); P-3 -> cuisine headline claims; P-4 -> C2 triplet motifs and any triplet NPMI. Adopting an item requires a new protocol version (v3) and new signatures; rejecting it is recorded in DECISIONS and leaves the v1/v2 text in force. P-5 touches no analysis.
- **E-3 Code and conventions.** Only bound code computes Step 35 results. New or changed scoring code (for example the 35a fingerprint/descriptor code, which does not exist yet) requires a new hash record signed by both; if the protocol text is unchanged the document hash stays the same. Conventions that neither the rows nor the bound code pin must be registered before the analysis that needs them: frequency-bin edges for frequency-stratified macro Recall (35c build note item 5), the source-stratum assignment of `THR-35P-42` (not implemented, item 6), the MX null and the `Z_CALIBRATED` path of `THR-35P-37` (35d build note). The conventions the bound code does implement (35c items 1-4 and 7-9, 35d items 1-3, 35e items 1-6) are accepted as registered by signature, or must be amended before signing.
- **E-4 Mac-only inputs.** 35b, 35c and 35d also require `MAC_ONLY_INPUTS` (section 6, absent here) in the signed record; they stay refused until a record binding them is signed.
- **E-5 Pre-signature conditions written in the rows.** `THR-35P-04`: "map reviewed by a chemistry-aware reviewer before signature"; `THR-35P-36` (c): "before signature a human establishes the reason of the 204 DEPRECATED edges and the counts by reason are recorded". Neither is done (D-039 L227, D-040 L237). The AI audit RV-01 (`reports/review/AI_REVIEW_2026-10-28.md`) is AI evidence, not the human finding. Signers either complete both first, or record in DECISIONS that they sign with both outstanding and that 35a taste tasks stay unrun until both are done (a human deviation; this document does not make it).

## 6. Bound inputs (sha256 at drafting; the hash record repeats them)

| Path | sha256 | Tasks |
|---|---|---|
| `ledgers/data/IMAP.jsonl` | `d09aeead076401e1325f3f588ce67251d8a84b5862e5418d5ac83d9cd2386c78` | 35b |
| `ledgers/data/ING.jsonl` | `ef439951982b98efa9a21787f7b646a162c3c4912718405cdae6ed56dc1cd574` | 35b, 35c, 35d |
| `ledgers/data/KGE.jsonl` | `1c9ffda0d74dcaaa71b9f45c0667489a4e5268759e9e1810067e54502cf39bd8` | 35a, 35b |
| `ledgers/data/MOL.jsonl` | `f9d25b373ae2a4a92ed625f81f3a6f642c34683ea3a59176f1ddb00d2a2489dc` | 35a, 35b |
| `ledgers/recipe_identity_v2/recipe_split_groups_v1.parquet` | `b0e26ddca5133882e33bf2f7b9cdbf2f28987d25b9f9965966e9b64953790868` | 35b, 35c, 35d |
| `registry/cuisine/cuisine_lookup_v1_DRAFT.csv` | `dbdc384f8d9d82f83a75d06ea39644a9b195e18f16e20d7626afd1af9413b7e5` | 35d |
| `registry/cuisine/explicit_cuisine_labels_v1.csv` | `3a47ba169783d04e487457cde7500a4eb4bf91d1b07fa05261eab1c25c8448ab` | 35d |
| `registry/cuisine/foodcom_tag_census_v1.csv` | `af4a401b4f02321cac8ea122f929ce4e3e8933d28da24f6dc5470f7eb3a103af` | 35d |
| `registry/cuisine/foodcom_tag_cuisine_map_v1_DRAFT.csv` | `f1b653f2d29125c55e1ed03812e90aefe9d5428742d73618ede4688db6d49645` | 35d |
| `registry/recipe_source_usage_registry_v1.csv` | `325238d610fffdcaffec768c4ee26abd3fe6a9f71396a3987b97f0007793f1c7` | 35b, 35c, 35d |
| `registry/ssot15_similarity_registry.csv` | `ecfe4886050aaac138be8b5ea99587e27db264ea9d02b43b0ce259b3de6bd26c` | 35e |
| `reports/review/protocol_review_addendum_DRAFT.md` | `2432500692bbdff0f83b1b229f88b5166fdface3e8aa30416a8005307d7b3c8c` | all (bound as OPEN proposals, not as adopted text) |
| `reports/step35/35_0_parv_review_DRAFT.md` | `175a498fcaeea6281bbae709f101c2d01cc857e68c136efedba2b19d98899c11` | all |
| `reports/step35/35_0_v2_threshold_rows.csv` | `8b696b08661c8b630723e0512c82398ca6a1a24bcfe557ad752e80fb957f15e0` | all |
| `reports/step35/preregistration_35_0_v1_draft.md` | `47c6ba6e6c567a3861c72625de28b78e0fa67c8a1462396fb1e18b421a03d933` | all |
| `src/culinarystate/representation/cuisine_rungs.py` | `ce86e019ae0fb003852e11cd48eca000a1d68ea19d2252c0875456e3d581dff7` | 35d |
| `src/culinarystate/representation/explicit_runner.py` | `75eac7f5e146d250cd3b1f05a58bb201587b276fa1e389c573aab1bc198d36db` | all |
| `src/culinarystate/representation/prereg_guard.py` | `d617ff9b37655361431f2bd7d6dcf1b6a80b334a08eeee1491390c9c99789d32` | all |
| `src/culinarystate/representation/recipe_rungs.py` | `752e343d50cf5ebdf958f72a53802b2ea8c2d9357b49b8841869c477514de355` | 35b, 35c, 35d |
| `src/culinarystate/representation/similarity_registry.py` | `bb52549a821dce6be4308ac8ac8e29a1344af51cc146a33f37de8dcc00cd4cfc` | 35e |
| `tools/step35_foodcom_tag_census.py` | `de5c423bd2b9a032f8e61053a241fa68efe9f9d049a9c9b0f1ef547c69cf4b28` | 35d |

The lookup and map hashes equal those bound in `preregistration_35_0_review_package.sha256.UNSIGNED.json`, i.e. the bytes Parv reviewed under D-040.

**Absent in this container (Mac-only; sha256 UNKNOWN here; required for 35b, 35c, 35d):** `ledgers/recipe_base/recipe_base_v1.parquet`, `ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet`, `ledgers/recipe_identity/gold_firewall_v1.parquet`. Any further recipe-identity file a recipe runner reads (for the conservative grouping) must be added to the runner's input list, which changes the runner's hash and so requires a new record.

**Hash record.** `reports/step35/preregistration_35_0_v2_package.sha256.UNSIGNED.json`, produced by `explicit_runner.build_unsigned_record` (which calls `prereg_guard.sign_record_template`; signers empty, date empty, status `UNSIGNED_TEMPLATE`). `require_signed_prereg` refuses it (tested). Signing steps and the exact list of hashes are in `reports/step35/35_0_v2_signature_sheet.md`.

## 7. What signing v2 does and does not authorise

Signing authorises explicit-baseline runs through E-1 for tasks whose inputs are bound and that E-2 to E-5 do not block, under every v1 rule (descriptive-only recipe/cuisine runs before 07I-S, `THR-35P-03`; outputs to git-ignored `features/step35/`, `THR-35P-31`). It does not authorise: learned rungs (35g, `THR-35P-29`) or 35f; any licence decision (H2); headline recipe/cuisine claims before 07I-S; a cuisine headline before the cuisine-expert ontology review; release of FlavorGraph-derived outputs; adoption of any Appendix P item; any change to ledgers or to the threshold registry.

---

## Appendix P. Pending decision: D-041 AI-review amendment proposals (NOT ADOPTED)

Source: `reports/review/protocol_review_addendum_DRAFT.md` (bound, sha256 `24325006...b7c3c8c`), D-041 L245: "Scientific corrections proposed, not adopted ... Parv's prior D1 answer is not retroactively treated as acceptance of these later amendments." Nothing below is in force. Each item needs an explicit human decision; until then E-2 applies.

### P-1 Confirmed negatives (v1 s4.4, `THR-35P-36` (a)) — OPEN
Proposal: replace the database-level alternative ("or from a source database that assays c per a reviewed assay-coverage table") with: a molecule is a negative for class c only with an explicit negative label or a documented molecule-level assay outcome meeting a preregistered criterion; database-level coverage alone is insufficient; conflicting evidence is CONFLICTING and excluded. The expert defines the assay criterion. Options: adopt (v3 with a superseding row), reject (row 36 (a) stands), or adopt with the expert criterion first. Touches: 35a taste tasks.

### P-2 Status text for the 204 DEPRECATED edges (v1 s2, s4.4, D35-18) — OPEN
Proposal: replace "underlying cause ... is not examined" with the dated AI-audit status (204/204 linked to unique active replacements; a migration explanation, not a validity finding; human chemistry review pending). Options: adopt in v3, or keep the v1 wording. Either way the human finding of `THR-35P-36` (c) is still required (E-5). Touches: 35a.

### P-3 Cuisine definitions after D-040 — OPEN
The D-040 rulings themselves are human decisions and are integrated in section 3 (they are not taken from this proposal). What remains OPEN from the proposal: "American's class scope and cultural interpretation still need expert review"; "M49 validates geographic grouping, not cultural equivalence or annotation reliability". Options: expert review before any cuisine headline (already required by v1 s7.2 (a)), or a recorded human narrowing of the American class. Touches: cuisine headline claims.

### P-4 Triplet NPMI convention (35d C2, `THR-35P-24` triplets) — OPEN
The implemented direct triplet generalisation can exceed 1. Options named by the proposal: retain it with an explicit formula, name and range caveat; normalise it with a reviewed multi-variable definition; or demote triplets to descriptive reporting. No option is adopted and the formula is not changed. Touches: C2 triplet motifs.

### P-5 Environment and signature binding — OPEN (confirmation only)
The RDKit pin enters v2 from D-039 (a human decision), not from this proposal; bound-file hashing is implemented (section 6). Open question: do the signers confirm that section 6 is the complete companion-input set, and that binding the addendum bytes records them as OPEN proposals only? Touches: no analysis.
