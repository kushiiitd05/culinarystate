# Step 35.0 v2 signature sheet for Kush and Parv (UNSIGNED)

Prepared 2026-11-03 by AI worker "ksh" (an agent; it signs nothing). Under D-045 your review is final. Protocol: `reports/step35/preregistration_35_0_v2_draft.md` (v2). Nothing is signed; G35-PRE refuses every Step 35 run today (tested).

## 1. What you sign (exact bytes)

| Item | sha256 |
|---|---|
| v2 protocol `reports/step35/preregistration_35_0_v2_draft.md` | `4d63cea2408ddcac995c1112832588087ae70bc27cb295e734b6a63578cd1a53` |
| v1 text it incorporates `reports/step35/preregistration_35_0_v1_draft.md` (unchanged) | `47c6ba6e6c567a3861c72625de28b78e0fa67c8a1462396fb1e18b421a03d933` |
| 43 rows THR-35P-01..43 `reports/step35/35_0_v2_threshold_rows.csv` (= v1 Appendix A bytes) | `8b696b08661c8b630723e0512c82398ca6a1a24bcfe557ad752e80fb957f15e0` |
| UNSIGNED template `reports/step35/preregistration_35_0_v2_package.sha256.UNSIGNED.json` (as committed; its bytes change when you fill it in) | `4f746e1a7af307c8ee1deac30d08ff40716b17015169c4b7f10eefe5609af0d7` |

The template binds 21 inputs (protocol texts, Parv's review record, the D-041 addendum as OPEN text, cuisine lookup/map/labels/census, the census tool, MOL/IMAP/KGE/ING ledgers, recipe split groups, two registries and the five Step 35 code files). Their full paths and 64-character hashes are in v2 section 6 and in the template; a test keeps the two identical. Check them there, not from a summary.

## 2. Two ways to sign (choose one; Q-2)

- **Route A (this container).** Sign the committed template. It cannot bind three Mac-only recipe files, so after signing only 35a and 35e can pass the entry, and 35a is still blocked by E-2 (P-1, P-2) and E-5. 35b, 35c and 35d stay refused.
- **Route B (Mac, recommended by the AI, not decided).** On the Mac, where `recipe_base_v1.parquet`, `recipe_ingredient_mentions_v1.parquet` and `gold_firewall_v1.parquet` exist, regenerate the template:
  ```
  PYTHONPATH=src python -c "import json; from culinarystate.representation.explicit_runner import build_unsigned_record as b; print(json.dumps(b('.'), indent=2))" > /tmp/v2_template.json
  ```
  Check that `sha256` equals the v2 hash above, that `not_bound_absent_here` is empty, and that every other bound hash equals v2 section 6. Then sign that file.

## 3. How to sign

1. Copy the chosen template to `reports/step35/preregistration_35_0_v2_package.sha256.SIGNED.json` (the only name the runner reads).
2. Each of you adds your own name to `signers`, sets `date` (YYYY-MM-DD) and sets `status` to `SIGNED`. Two distinct names are required; a single signer needs a written `single_signer_override` with reason and name.
3. Check: `PYTHONPATH=src python -c "from culinarystate.representation.explicit_runner import authorise_explicit_run as a; print(a('35e', root='.'))"` must print an Authorisation.
4. Commit the SIGNED file from the session of the human who signed (D-049 F5). Never edit the protocol or any bound file afterwards: a change needs a new record (and, for protocol text, v3).
5. Separately, append THR-35P-01..43 verbatim to `registry/preregistered_thresholds_v1.csv` with your signer fields (as D-046 did for THR-19P).

## 4. By signing you accept

- the v1 text and the 43 rows as drafted (Parv's D1 (a); Kush's acceptance is the signature itself);
- the D1-D8 integration (v2 section 2) and the D-040 cuisine rules (v2 section 3), which are Parv's single-reviewer choices, including the REGION extension to below-country terms and Parv's D5 rdkit 2026.3.6 pin;
- the execution rules E-1 to E-5 (v2 section 5), including that OPEN items block what they touch, and that the conventions implemented by the bound code are registered as built (E-3).

## 5. Before you sign (written in the rows you sign)

- **S-1** `THR-35P-04`: the taste-label map is reviewed by a chemistry-aware reviewer "before signature". Not done; reviewer pending (D-040).
- **S-2** `THR-35P-36` (c): a human establishes the reason for the 204 DEPRECATED edges "before signature". Not done; the AI audit RV-01 is not this finding.
- Either complete both, or record in DECISIONS that you sign with them outstanding and 35a taste tasks stay unrun until both are done (E-5). The AI does not choose.

## 6. OPEN amendment questions (D-041; NOT ADOPTED; v2 Appendix P)

| Id | Question | Options | Blocks until decided |
|---|---|---|---|
| P-1 | Confirmed negatives: drop the database-level "assays c" clause of THR-35P-36 (a) for molecule-level negative evidence? | adopt in v3 / reject / adopt after the expert defines the assay criterion | 35a taste tasks |
| P-2 | Replace the "not examined" text on the 204 DEPRECATED edges with the dated AI-audit status? | adopt in v3 / keep v1 wording | 35a |
| P-3 | American class scope and cultural interpretation; M49 is geographic only | expert review before any cuisine headline / recorded narrowing | cuisine headline |
| P-4 | Triplet NPMI can exceed 1 | keep with caveat / reviewed normalisation / descriptive only | C2 triplet motifs |
| P-5 | Is v2 section 6 the complete companion set, with the addendum bound as OPEN text only? | confirm / name missing inputs | nothing |

## 7. Other open questions and human work

- **Q-1** Does `ledgers/recipe_identity_v2/recipe_split_groups_v1.parquet` (07I-C, single-reviewer basis) count as "07I-S exists" for THR-35P-03? Default: no, recipe/cuisine runs stay descriptive.
- **Q-2** Route A or route B (section 2).
- **Q-3** D35-12: similarity registry v2 id scheme and statuses (H4); unanswered.
- **Q-4** Register the conventions no row or code pins (frequency-bin edges; THR-35P-42 stratum assignment; MX null; Z_CALIBRATED path) before the analyses that need them (E-3).
- Human work pending: 50-crosswalk audit (Parv, D-040); chemistry reviewer (Kush to arrange); cuisine expert (4-6 h); H2 licence decisions (Kush).
