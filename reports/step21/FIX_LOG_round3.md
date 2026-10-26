# Step 21 / MECH schema: round-3 fix log

Status: DRAFT_PENDING_H4 (nothing approved, frozen, minted, committed or pushed). Written 2026-10-26 by the round-3 fixer.
Inputs: `reports/master_plan/review_queue/round3_review_A_governance.md` (A), `round3_review_B_science.md` (B), `rulings_D-027_R01-R20.md` (R-14, R-15, R-20 binding).
Status vocabulary: FIXED (change made and, where it is a schema rule, covered by a negative control that was mutation-checked) / OPEN_QUESTION (a domain fact the repo does not state is **not asserted**; the item is recorded in the document and in README section 4) / NOT_APPLICABLE (the item belongs to Step 19 or Step 35, or is not an edit).
Line numbers are those of the files as they stand after this revision. `S` = `registry/schemas/MECH.draft_v1.schema.json`, `O` = `reports/step21/mechanism_effect_ontology_v1_draft.md`, `R` = `reports/step21/README.md`, roster / effect / gate = the three CSVs in `registry/`.

Verification: see the end (section 4).

## 1. Review A

| Item | Status | Evidence |
|---|---|---|
| K-1a (Step-04 README: "jsonschema not installed") | FIXED | `reports/step04/README.md:43` now states jsonschema 4.10.3 for `/usr/bin/python3` on the server, none for the PATH miniconda python, pytest absent, `$id` caveat, and that the 220-case run was not repeated with jsonschema. The server facts are those of Review A; on this Mac `/usr/bin/python3` has **no** jsonschema (checked) and anaconda has 4.19.2 |
| K-1b (">= 4.18" and `Draft202012Validator(load(name))`) | FIXED | `reports/step04/README.md:51` (needs >= 4.0, relative `$id` stripped for < 4.18); `:76` strips `$id` |
| K-1c (README:611 "stdlib only, no pytest / jsonschema") | FIXED | `reports/step04/README.md:611` |
| K-1d (lineage contract) | FIXED | `reports/step04/lineage_contract_v1_1.md:285` |
| K-1e (Step-02 classification) | FIXED | `reports/step02/r_min_08a_input_classification.md:39` and `:57` name the interpreter |
| Same error inside Step 21 (README section 3) | FIXED | `R:30-31` (how the contract test is run, which interpreter has jsonschema, `$id` stripping); test header `R:92` |
| #1 UNKNOWN token accepted in categories / predicate values | FIXED | `S:853` (predicate.values), `S:1056`, `S:1068` (categories.allowed / excluded): case-insensitive `not` pattern. Controls N-59..N-62 (`R:435-438`) |
| #2 ACCEPTED without an evidence id on 6 item types | FIXED | `allOf` rule on `precondition` (`S:1561`), `competes_with` (`S:2522`), `consecutive_with` (`S:2581`), `affected_target` (`S:2644`), `marker` (`S:3146`), `history_item` (`S:3197`). Controls N-63..N-68; structure test `test_r15_constants_are_in_the_schema` asserts the rule on all eight item types |
| #3 lone MODULATING gate gives vacuous APPLICABLE | FIXED | root rule `S:3361-3392`: `gates_unknown = false` needs >= 1 precondition or >= 1 NECESSARY gate. `O:208` (4.3), `O:269` (U-5), `O` G21.3 row, gate CSV annotations. Controls N-69, N-70 (and V-5, V-13 rewritten). Reviewer B's third branch (history INPUT_REQUIRED) not adopted: OPEN_QUESTION D21-20 (`R:68`) |
| #4 VOLATILIZED / WHOLE_SYSTEM mismatch (CSV vs schema vs ontology) | FIXED | schema rules in `affected_target.allOf` (`S:3040-3075`): LEACHED / ABSORBED exclude WHOLE_SYSTEM, VOLATILIZED admits it DECREASE only, the COOKING_MEDIUM INCREASE-only rule applies to LEACHED only; effect CSV row 9 (`VOLATILIZED`), rows 8, 15; `O` 3.3 table; new test `test_direction_rules_in_the_effect_csv_match_the_schema` (`R:553`); controls N-71, N-72; V-19, V-20 |
| #5, #6, #7, #8, #10, #16, #18, #20, #21, #22, #25, #26, #28, #29, #30, #31, #32, #33, #34 | NOT_APPLICABLE | Step 19 / Step 35 documents (outside the files this fixer may edit) |
| #9 identifier collisions (D-n, NC-n, L1..L5) | NOT_APPLICABLE for Step 21 | Step 21 already uses `D21-n`; the Step 19 / 35 renames are theirs |
| #11 `$comment` claims every evaluated item carries `missing_input_verdict` | FIXED | `S:6` rewritten to the true list (precondition, gate, modifier, matrix_scope, categories); the rest contribute UNKNOWN through status; H4 item D21-21 (`R:69`) |
| #12 species-level effect types without a source (CARAMELISATION, LIPID_OXIDATION) | FIXED | roster rows 8 and 10: `UNKNOWN_TRANSFORMATION`; `O` section 7 states the rule and the correction |
| #13 R-14 comment false (analyte_form description names both systems) | FIXED | `S:2747` neutral wording; `S:6` now reads "no field, enum value, rule or description ... names or prefers either candidate system"; test `test_r14_...` greps the schema text for ascorb / chlorophyll / pheoph / vitamin c (`R:629`); mutation M12 caught |
| #14 local key patterns collide with gate / task names | FIXED | `^CG\d{2}$` (`S:1651`, `:2237`, `:2281`), `^PRE\d{2}$` (`S:1576`), `^INH\d{2}$` (`S:2182`), `^TGT\d{2}$` (`S:2662`), `^MRK\d{2}$` (`S:3159`); fixtures updated; controls N-75..N-77 |
| #15 xref namespaces MESH / TRANSFORMON beyond the card | FIXED | removed from `S:1263`; `O` section 9; D21-19 (`R:67`); control N-80 |
| #17 `DOC- OBS- KIN- LROOT-` evidence prefixes depend on unreserved prefixes | FIXED | `R` D21-1 (`R:40`) and `O` 4.9 state the dependency and the narrowing to `(EVD|SRC)` |
| #19 LEACHING tagged AA_RELATED_GENERIC | FIXED | roster row `LEACHING` -> `NEITHER`; test allows only AA_PATHWAY / CHL_PATHWAY / NEITHER (`R:` r14 test); `O` section 6 |
| #23 `DGP-` unscanned | FIXED (reservation only) | `reports/step04/04_9_min_namespace_reservation.md:56`; open decision list item 2 updated |
| #24 `T-ING-*` is the rejected `T-` form | FIXED (reservation only) | `04_9_min_namespace_reservation.md:57` records `TASK-`; the rename inside the Step 35 draft is theirs (NOT_APPLICABLE here) |
| `MECH-` missing from the 04.9-min reservation (requested by the lead) | FIXED | `04_9_min_namespace_reservation.md:55` (also scanned free in `registry.py`, test `test_prefix_is_free_in_the_python_registry`) |
| #27 `local_process_module` source undocumented | FIXED | `S:306` description (SSOT 213.29, not a simulator selection) |
| #35 authority wording (Plan section 7 vs R-10 / lane L5) | FIXED | `R:3`, `O:3` |
| #36 log the step (`tools/log_step.py`) | NOT_APPLICABLE | would modify WORKLOG, outside the permitted files; for the integrating session |
| #37, #39 | NOT_APPLICABLE | Step 35 notes |
| #38 mutation check not re-run; 21/21 does not cover #1-#4 | FIXED | new controls cover them; mutation check repeated, section 4 |

## 2. Review B (Step 21 part)

| Item | Status | Evidence |
|---|---|---|
| 21-1 AA -> DHA -> DKG lumped | FIXED structure; chemistry OPEN_QUESTION | roster rows 15 `ASCORBATE_TO_DHA_OXIDATION` (card label kept in `synonyms`) and 16 `DHA_HYDROLYSIS_TO_DKG`; chain AA -> DHA -> DKG and the AA vs AA + DHA basis are in the repo (r_simulator_vv Q1); reversibility, O2 / metal / pH dependence and "hydrolytic, O2-independent" are not in the repo and are marked OPEN_QUESTION in `open_issue` (D21-23). `O` 6.1 |
| 21-2 ascorbate oxidase as a parallel loss | FIXED structure; EC number OPEN_QUESTION | roster row 19 `ASCORBATE_OXIDASE_AA_OXIDATION`: PARALLEL_PATHWAY on reduced AA plus consecutive with the DHA step, no double counting; EC 1.10.3.3 and "same node" asserted by the reviewer only: OPEN_QUESTION in the row |
| 21-3 no catalyst / promoter construct | FIXED | `inhibitor` def (`S:2165-2520`): roles CATALYST / PROMOTER, SBO ids (both already in the schema's participant enum), `extent NOT_APPLICABLE`, `acts_on_modifier_key`, role / sbo / extent coupling; rule M-1 (`O:220`, `O` 1); semantic checks (`R:653-700`); controls N-81..N-84, V-21; mutation M8. The list keeps the card name `inhibitors_mitigators` (rename = D21-11 alternative); SBO:0000459 for PROMOTER needs human verification (D21-19) |
| 21-4 no enzyme-inactivation entry | FIXED structure; one claim OPEN_QUESTION | roster row 31 `ENZYME_THERMAL_INACTIVATION` (PC-02, MP I3); history roles `ACTIVE_UNTIL_STATE_CHANGE`, `INPUT_REQUIRED_START_MODE` (`S:3215`); D21-14 updated. "Enzyme activity rises in the come-up window" is not in the repo: OPEN_QUESTION in the row |
| 21-5 G5 dead end for SIM-AA-1 | FIXED (MECH side); FORM side is a cross-step need | roster row 18 `ASCORBIC_ACID_APPARENT_LOSS_LUMPED` (plan L1175 supports one apparent k_d); `O:224` joint-coverage rule; `covers_mechanism_keys` is owned by Step 24: `R` section 6 item 12 |
| 21-6 chlorophyllase pathway missing | FIXED structure; science OPEN_QUESTION | roster rows 21, 22 (`CHLOROPHYLLASE_DEPHYTYLATION`, `CHLOROPHYLLIDE_TO_PHEOPHORBIDE`): not in the repo, reviewer-sourced, marked OPEN_QUESTION and droppable in 21b (D21-23); `O` 6.2 |
| 21-7 pH as NECESSARY window | FIXED (default rule); chemistry OPEN_QUESTION | `O:214` rule E-7, `O:283` illustration rewritten (pH MODULATING, UNKNOWN pH blocks at G7; repo basis: SSOT 144.1 no universal switch, plan L1184 SIM-CHL-1 pH as FORM input); roster row 20 note; gate CSV annotation; semantic check `R:693`. That Mg loss occurs across the practical pH range is not in the repo: D21-20 asks for confirmation |
| 21-8 vacuous APPLICABLE | FIXED | same as A#3; the reviewer's third branch not adopted (D21-20) |
| 21-9 OPEN_STATED extrapolates to APPLICABLE | FIXED | `bound` (`S:929`, rule: STATED / OPEN_STATED need number + inclusive), description (`S:1016`); `O:207`, U-4; reference evaluator `side()` (`R:785`): beyond the studied extreme is UNKNOWN; N-6 rewritten, interval and property tests extended; mutation M5 |
| 21-10 min / opt / max completes a cardinal model | FIXED (deviation from the card, D21-6) | `opt` and `opt_bound` removed (`S:1018`, gate rule list); `O:208`; L-21-7 (`O:402`); control N-79 |
| 21-11 OXIDIZED / REDUCED direction open | FIXED | `target_role` on `affected_target` (`S:2667`, rules `S:3084`, `S:3115`); effect CSV rows 4-5; controls N-73, N-74, N-85; V-22; mutation M9 |
| 21-12 analyte form free text | OPEN_QUESTION | token list + a 4th registry CSV is outside the permitted files and is domain content: D21-22 (`R:70`), note in `O` 3.1 |
| 21-13 CV-021 location / dissolved O2 / CV-036 / water ions | FIXED (schema, gaps); dissolved-O2 chemistry OPEN_QUESTION | `S:2141-2150` CV-021 location HEADSPACE / UNKNOWN; `O` gaps G-2, G-8, G-9; control N-78; mutation M6 |
| 21-14 coupled redox not representable | FIXED (relation); pairs OPEN_QUESTION | `COUPLED_REDOX` in `competes_with.relation` (`S:2547`); `O` 4.5; PPO roster row note |
| 21-15 leaching and oxidation also consecutive; water:food ratio axis | FIXED | `O` 6.1 (both compartments, consecutive_with LEACHING, supported by the plan's k_dw term), gap G-9 |
| 21-16 Zn / Cu metallo-chlorophyll | FIXED structure; science OPEN_QUESTION | roster row 33 `METALLO_CHLOROPHYLL_COMPLEX_FORMATION` (no repo source; no safety claim, D21-18) |
| 21-17 colour non-monotone early in blanching | OPEN_QUESTION | not encoded; noted in `O` 6.2 and D21-23 |
| 21-18 DEGRADED vs CONSUMED for named reactants | FIXED | `CHLOROPHYLL_TO_PHEOPHYTIN` -> `CONSUMED;FORMED`; `ASCORBATE_TO_DHA_OXIDATION` -> `OXIDIZED;FORMED` |
| 21-19 anaerobic route markers non-unique | OPEN_QUESTION | note in the anaerobic roster row (`marker_unique` is already the constant false) |
| 21-20 (INFO) legitimate qualitative -> quantitative use | FIXED | `O:425` |
| 19-1 .. 19-9, 35-1 .. 35-14 | NOT_APPLICABLE | Step 19 / Step 35 documents |

Counts (Step 21 scope, items with an action): Review A 23 FIXED (K-1a..e = 5, the same error inside the Step-21 README, #1, #2, #3, #4, #11, #12, #13, #14, #15, #17, #19, #23, #24, #27, #35, #38, and the `MECH-` reservation); Review B 17 FIXED (21-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 20), of which 8 also carry an OPEN_QUESTION on chemistry the repo does not state (21-1, 2, 4, 6, 7, 13, 14, 16), and 3 OPEN_QUESTION only (21-12, 21-17, 21-19). Total: 40 FIXED, 3 OPEN_QUESTION only, rest NOT_APPLICABLE (Steps 19 and 35, and the WORKLOG entry).
Not asserted, marked OPEN_QUESTION in the documents (D21-20, D21-22, D21-23): the chemistry of the DHA step (reversibility, O2 / metal / pH dependence), the ascorbate-oxidase EC number, the chlorophyllase / pheophorbide / metal-complex pathways, dissolved oxygen as a driver, E-7's chemistry (Mg loss over the whole practical pH range; no T / pH at which Arrhenius chemistry stops), non-monotone colour early in blanching, enzyme behaviour in the heating come-up window, the shared markers of the anaerobic route, SBO:0000459 as the PROMOTER id, and the analyte-form token list.

## 3. Files touched

`reports/step21/README.md`, `reports/step21/mechanism_effect_ontology_v1_draft.md`, `reports/step21/FIX_LOG_round3.md` (new), `registry/schemas/MECH.draft_v1.schema.json`, `registry/mechanism_seed_roster_draft_v1.csv` (new `synonyms` column; 26 -> 32 rows), `registry/effect_type_registry_draft_v1.csv`, `registry/condition_gate_type_registry_draft_v1.csv`, `reports/step04/README.md`, `reports/step04/lineage_contract_v1_1.md`, `reports/step02/r_min_08a_input_classification.md`, `reports/step04/04_9_min_namespace_reservation.md` (three reservation rows and the open-decision list item 2 only). Nothing committed or pushed; no `tests/` file created (the test is the code block in README section 5).

## 4. Verification

- All JSON files parse (schema; the Step-21 schema round-trips with `indent=2`).
- Contract test (README section 5, extracted unchanged to a scratch directory, `$id` stripped inside the test): **22 passed** under `/opt/anaconda3/bin/python` 3.11.8 with jsonschema 4.19.2 (Mac); 87 negative controls and 23 accepted variants. The `/usr/bin/python3` of this Mac has no jsonschema, so the 4.10.3 run of the server could not be repeated here; the test avoids >= 4.18-only features by stripping `$id`.
- Mutation check of the new rules (12 deliberate defects in scratch copies: UNKNOWN pattern removed, ACCEPTED rule removed, root rule weakened, VOLATILIZED rules removed, OPEN_STATED null re-admitted, CV-021 rule removed, old key pattern, modifier rules removed, target_role rules removed, LEACHED medium rule removed, MESH re-admitted, an ascorbic term in the schema): 12 of 12 caught.
