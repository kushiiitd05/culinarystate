# AI verdict — pending Kush/Parv review

**S160 parts A–C: AI cross-review by worker "prv"** (an agent, not Parv). Date 2026-11-03, branch `cloud/s160-freeze-prep`. Under D-045 W1 (`DECISIONS.md` L269) this is an AI verdict. It is not an approval and not a human review: Kush and Parv review it, and their review is final. Nothing here signs, seals or decides anything.

**Scope.** Worker "ksh"'s S160 A–C:
(A) `reports/step15/pre_freeze_rulings_DRAFT.md`;
(B) the 15a.R seal, `src/culinarystate/lineage/reserved_seal.py` and `tools/step15a_R_seal.py`;
(C) the Step 35 v2 package: `reports/step35/{preregistration_35_0_v2_draft.md, 35_0_v2_threshold_rows.csv, preregistration_35_0_v2_package.sha256.UNSIGNED.json, 35_0_v2_signature_sheet.md}` and `src/culinarystate/representation/explicit_runner.py`;
plus their tests, `tests/unit/test_step15a_R_reserved_seal.py` and `tests/unit/test_step35_v2_package.py`.

**Method.** I re-read every cited line in the files it cites (plan, spine, SSOT, DECISIONS, threshold registries, research notes, ingest code), read both modules end to end, and tried to make the seal and the runner accept inputs they should refuse. Every real defect got a failing test first (`tests/unit/test_s160_review_regressions.py`, commit `d9a65fb`) and then a fix in its own commit. The data bundle is absent from this container, so no real EVD row was read.

## Findings

Severity: MEDIUM = a refusal or binding the package depends on could be bypassed or is wrong; LOW = an accuracy or completeness defect with no bypass; INFO = noted, no change needed.

| Id | Severity | Evidence | Disposition |
|---|---|---|---|
| R1 | MEDIUM | `reserved_seal.find_ruling` accepted any Approver line containing the substring "kush". Approver lines that already exist in `DECISIONS.md` would have passed: L13 "Claude (reversible; flag for Kush/Parv review)", L18 "Kush (pending confirmation)", L45 "Kush + Parv to confirm before authoring starts". So a pending or AI-approved 15.0 entry with valid marker lines could have run the seal. | **FIXED.** The Approver line must name Kush as a word. A line that names an AI worker or agent is refused (`APPROVER_NOT_HUMAN`), and so is a line with pending, draft or to-confirm wording (`APPROVER_PENDING`). Test `d9a65fb`, fix `fb8a393`. Existing approver styles ("Kush.", "Kush and Parv (Parv relayed by Kush).") still pass. |
| R1b | LOW | Marker lines inside a fenced code block were read as rulings. The 15.0 draft itself carries the marker template in a ```` ```text ```` fence (section 6). If that template were pasted into an entry and filled in, it would have been parsed even though it is shown as a quotation. | **FIXED** in the same commits: fenced blocks are removed from the entry body before parsing. |
| R2 | MEDIUM | `run_explicit_baseline` / `authorise_explicit_run` accepted any two distinct non-empty strings as signers through `prereg_guard`. A record "signed" `["ksh", "prv"]` (the AI worker labels) or `["Kush Tokas", "Someone Else"]` would have authorised every bound task. The 35.0 card and the sheet require Kush and Parv. | **FIXED.** `explicit_runner.check_signer_identity`: each signer must name exactly one of Kush or Parv and no AI label. Both must sign unless the record has a `single_signer_override`. `prereg_guard.py` is pre-S160 and unchanged. Fix `6178ac3`. Follow-up `4669833` renames ksh's synthetic test signers to Kush/Parv; no assertion changed. |
| R3 | LOW | 15.0 draft section 5 quotes the cluster sign-flip rule as `"… never cluster-robust SEs" (Plan L557)`. The rule is on Plan L558, and the plan says "not", not "never". Section 4 cites `Plan L556 / L564` for "K=10 and the 40% giant-component threshold are PROPOSED_PILOT, pending pre-registration", but that sentence is only on L564. | **FIXED** `0fb129e`: exact quote, correct lines. The regression test checks every quoted plan citation in the draft against the cited line. |
| R4 | LOW | v2 section 2, D1 row: "covers D35-1, 3, 5, 13, 15, 17, 19-24". The v1 sign-off sheet (`35_0_signoff_sheet_DRAFT.md` L23) puts D35-1, 5, 13, 22, 23, 24 under D1 and asks D35-3/21 under D5, D35-15/19 under D7 and D35-17/20 under D3. The wider list was the drafter's reading, presented as fact. | **FIXED** `0e9c2b8`: the row quotes the sheet's mapping and labels the extension as "Drafter's reading, not a recorded answer". In the same commit, E-1 now states the signer-identity rule and the runner hash in section 6 is rebound. |
| O1 | MEDIUM | Seed secrecy is the only protection of the RESERVED list, and nothing enforces a minimum seed entropy. `SEED_SHA256` goes into DECISIONS and into the tracked commitment. Group ids are content hashes of tracked ledger fields, and the selection rule is public. So a guessable seed (D-048's nonces were human-chosen phrases) can be brute-forced from its sha256, and the sealed list can then be recomputed from the tracked ledger. | **OPEN (human).** 15.0 should say how the seed is generated, for example from a random source, and how long it must be. The AI does not choose a length. No code change. |
| O2 | LOW | Re-sealing is not prevented. The seal checks only the commitment and sealed-list paths it is given. A second signed 15.0 decision with a different seed and new output paths would seal a different RESERVED set, which is a forking path. | **OPEN (human):** should 15a.R refuse whenever any prior `15a_R_seal_commitment_*.json` exists, with a re-seal possible only by burning, as plan Step 15 describes? |
| O3 | LOW | Signature state is read only from the heading and the Approver line. A body line such as `**Status:** DRAFT` in an otherwise valid entry does not refuse. | **OPEN (human):** say whether body status wording must also refuse. The current heading convention ("(UNSIGNED)", "(single-reviewer; UNSIGNED)") is caught. |
| O4 | LOW | Not every consumed input is bound. The bound tool `tools/step35_foodcom_tag_census.py` reads `data/external/foodcom/recipes.parquet` (L24). That file is neither bound nor in `MAC_ONLY_INPUTS`. Its outputs (census, map, explicit labels) are bound, so the gap matters only if 35d re-runs the census. `pyproject.toml` (the rdkit pin cited by the v2 D5 row) is not bound either. | **OPEN (human):** answer under P-5 (is section 6 the complete companion set?). Adding either file changes the runner's input list and needs a new record. |
| O5 | LOW | G35-PRE is an engineering control, not a cryptographic one. Any process can write a `SIGNED.json`. `Authorisation` can be built directly. The scorer modules (`recipe_rungs`, `cuisine_rungs`, `similarity_registry`) are pure functions that can be called without the entry. `root` is chosen by the caller, so a forged tree in a temp folder can authorise while the runner reads real files. R2 closes the accidental and agent-signing route only. | **OPEN (by design; human process).** The SIGNED record is committed only from the signing human's session (sheet step 4, D-049 F5). Reviewers should reject any agent commit that adds it. |
| I1 | INFO | The 15.0 draft says the tool needs a `### D-NNN` heading. The parser also accepts `## D-NNN`. | No change: the description is stricter than the code. |
| I2 | INFO | `reserved_seal` imports `transition.dataset.process_signature`, which imports pandas. The Step 29 card notes that the server's system Python has no pandas. | **OPEN (environment):** run the seal where pandas exists (the Mac base environment), or authorise pandas. |

### Checked and found accurate (no finding)

- **15.0 draft citations:** spine L49/L50/L52; DECISIONS L195 (D-034), L269 (D-045 W1); Plan L25, L29, L30, L37, L552, L555, L557, L559, L561, L564, L577, L614 (CHG-15-3, "Needs human approval? Yes"), L615, L617, L620, L638; SSOT L16651–16663, L16664, L16690, L16886–16891, L16896–16901; `state_representation_contract_v1.md` L66; `evidence_tier_provenance_map_v1.csv` L2–L8 (E3 17,978 rows, E4 0); TB contract L20; `ssot_change_requests_v2.md` L7–L12 (PROPOSED_ONLY); research audit L271, L858, L3712; `preregistered_thresholds_v1.csv` L29 (THR-08A-08 "> 40%", signed by Kush, 39.0% / 39.4% caution), L36, L42 (Kish n_eff, share <= 0.40, "evaluated ONCE", weaker label applies); `_DRAFT.csv` L8, L15; r_eval_splits L89–L92, L97, L123, L235; ingest code PE L161, USDA L115, Bognár L101.
- **15.0 draft content:** every recommendation is labelled "AI recommendation (not a decision)". No D-number was added: the only S160 DECISIONS change is D-052, entered by Kush. The RESERVED fraction and the seed are UNKNOWN, and no value is proposed.
- **Seal determinism:** the payload hash excludes only `sealed_at_utc`, `sealed_list_location` and `payload_sha256`. Selection ranks by sha256(rule, snapshot, seed, group id) and floors per stratum. The reproducibility test passes.
- **Leakage into git:** the commitment holds no seed and no group id. The sealed list and the seed file must be outside git or git-ignored, and both are checked. CLI output goes to stdout only. The real repository is refused before any EVD row is read (tested).
- **v2 quotes** against `DECISIONS.md` L209, L215, L226–L228, L233–L237, L245, against `35_0_parv_review_DRAFT.md` L10–L12 and L19, and against `pyproject.toml` L7: all verbatim or marked with an ellipsis. E-5 lists the only rows whose text still requires a human act "before signature" (04 and 36 (c)). Rows 02 and 07 mention "before signature" but are satisfied by their own text.
- **v1 unchanged:** sha256 `47c6ba6e…1a53` equals the value bound in v2. The last commit touching v1 or its two UNSIGNED records is `18242ba` (2026-10-28). The 43 rows are byte-identical to Appendix A (tested).
- **Reachability today:** no `SIGNED.json` exists, so every task 35a–35e is refused on the real repository (tested). After R2, a record with AI or incomplete signers is refused too.

## Package hashes (changed by R2/R4)

The fixes changed two files of the v2 package: the runner, which is a bound input, and the protocol text, which is the record's document. The UNSIGNED record was regenerated with `explicit_runner.build_unsigned_record`, and the regenerated bytes differ only in these two hashes. The signature sheet carries the new values, and the builder-reproducibility and section-6 tests pass.

| File | before | after |
|---|---|---|
| `reports/step35/preregistration_35_0_v2_draft.md` | `4d63cea2408ddcac995c1112832588087ae70bc27cb295e734b6a63578cd1a53` | `009c9047ce78da21dd7d7061a64bc9fbb86d38d3eada5b3d8c9769ce5dd60145` |
| `src/culinarystate/representation/explicit_runner.py` | `75eac7f5e146d250cd3b1f05a58bb201587b276fa1e389c573aab1bc198d36db` | `c548cdf3e84eae16738fa14bab44ef687ab41ec15d5930ddf965dc648dbf9d68` |
| `reports/step35/preregistration_35_0_v2_package.sha256.UNSIGNED.json` | `4f746e1a7af307c8ee1deac30d08ff40716b17015169c4b7f10eefe5609af0d7` | `8885a63a0dc0181d4aec5d05fea124776d6a0afbbe5a1e162da7cbb9a4b582e5` |

All other bound hashes are unchanged. `reserved_seal.py` is not part of the v2 package.

## For Kush and Parv

1. Accept or reject R1–R4 as fixed.
2. Decide O1 (seed generation rule in the 15.0 entry), O2 (re-seal policy), O3 (body status wording) and O4 (bind the census source parquet and `pyproject.toml`, or confirm the set under P-5).
3. Note O5 and I2.

The 15.0 rulings, the RESERVED fraction and the seed are still not supplied, so the seal still refuses (tested).
