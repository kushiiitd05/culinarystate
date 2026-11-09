# AA kinetics pilot pre-registration: pre-signature amendment draft (S178)

Status: **AI_DRAFTED / PROPOSED. Not a decision, not a signature, not an approval (D-071).** Written 2026-11-09 by the
S178 PREREG lane (an AI agent) for the 9-10 Nov decision sitting: ops pack item **A3** (REV-A V7 / Q16, REV-B F-09 /
G-16 / B2.3) and the "AA prereg wording" entry of the lock (T9-C26-R5). Nothing here edits
`reports/step10/aa_pilot_preregistration_DRAFT.md`; the Mac scribe applies the chosen options there.

- Base text amended: `reports/step10/aa_pilot_preregistration_DRAFT.md`, sha256
  `6233511902461d533b945e91cf4a07be16b60bc64e6b8a02e9531c16ad38eaab` (server worktree, 2026-11-09).
- State today: CAL packet v1 = 16 rows from 4 papers (AAK-01, 06, 09, 11), `PENDING_HUMAN_VERIFICATION`
  (`reports/step10/aa_pilot_CAL_packet_manifest_v1.json`); SIM-VAL PDFs AAK-03, 07, 12 are downloaded and unopened;
  AAK-05 (SIM-VAL) and AAK-02, 04, 08, 10 (CAL) await Kush's browser download. No verdict exists.
- This prereg is **the first one signed** (Tue 10 Nov, S1) because the PDF downloads and the CAL extraction wait on it.

## 0. What the sitting must decide

| Id | Question | Options here | Type | Pack rec. |
|---|---|---|---|---|
| D-AA-1 | Add the A3 lines (domain gate, analyte basis, RESEARCH_ONLY, firewall) | add · sign as is | choice | add |
| D-AA-2 | How the domain gate states pH | **pH-A** range from the CAL papers' stated pH · **pH-B** a fixed bound · **pH-C** no pH gate, pH reported | choice | pH-A, falling back to pH-C |
| D-AA-3 | SIM-VAL firewall | **FW-A** SIM-VAL PDFs moved out of the agent's reach by Kush until the fit hash exists · **FW-B** separate session extracts SIM-VAL · both | choice | both |
| D-AA-4 | Pre-declared sensitivities for CAL rows already seen | add (water-contact paper, non-specific assay) · none | choice | add (primary fit unchanged) |
| D-AA-5 | Licence status per paper (facts) | Kush records what each publisher page says | HUMAN (fact) | — |

## 1. Why this is not a post-hoc weakening

No verdict, fit or SIM-VAL text exists. Every proposed line narrows where a SIMULATE result may be used, makes the
analyte basis explicit, or pre-announces the weaker label (RESEARCH_ONLY) the plan's own rule (G15-f: >= 5
validation groups) already forces. The primary Model A specification (§6) is **not changed**: the agent has already
seen the 16 CAL values (§6 says so), so it proposes no new exclusion from the primary fit, only additional
sensitivity fits reported beside it.

## 2. Changes (old text -> new text)

### C1. Header (L3-L6)

```diff
 dual human extraction. It is labelled MODEL_ASSISTED (D-045); every row is verified by both Kush and Parv.
+Amended before any signature with the S178 options the 9-10 Nov sitting chose
+(`reports/step10/aa_pilot_preregistration_AMENDMENT_S178_DRAFT.md`). Until both humans sign it is a dated AI
+draft. **Step 27 (SIM-VAL) is pre-announced RESEARCH_ONLY** (§5): this pilot shows the SIMULATE pathway on one
+narrow domain; it cannot show that SIMULATE works for recipes.
```

### C2. §1 Sources (L10-L13): licence status per paper, recorded now

```diff
 confirmed on its landing page before use; a paper that is not CC-BY or CC0 is dropped and recorded, never stored.
 Full texts are stored under `data/raw/aa_pilot/` (git-ignored) with SHA-256 in the extraction file.
+Licence status at the lock (`registry/evidence/aa_kinetics_source_candidates_v1.csv`): CC-BY stated in the PDF only
+for AAK-06 and AAK-09; every other paper reads UNKNOWN, **including AAK-01 and AAK-11, from which CAL rows were
+already extracted**. Kush confirms each licence on the publisher page (AAK-01, 02, 04, 05, 08, 09, 10, 11 before
+verification; the SIM-VAL papers AAK-03, 07, 12 from the landing-page badge only, without opening the text). If
+AAK-01 or AAK-11 is not CC-BY or CC0, its rows are dropped before verification and the report says so. AAK-09: the
+publisher version (CC-BY) is the one used; its repository copy is labelled CC-BY-NC-ND.
```

### C3. §3 Split and firewall (L39-L42)

```diff
-extracted and verified like the others, but **only after** the SIM-CAL fit is frozen (hash committed): the agent is both
-extractor and fitter, so it does not open a SIM-VAL full text before the freeze (Step 11.L firewall).
+extracted and verified like the others, but **only after** the SIM-CAL fit is frozen (hash committed): the agent is both
+extractor and fitter, so it does not open a SIM-VAL full text before the freeze (Step 11.L firewall). The firewall is
+made physical, not only behavioural (REV-B B2.3, F-09):
+[FW-A] Kush moves the SIM-VAL PDFs (AAK-03, 07, 12, and AAK-05 when downloaded: "save it, do not read it") out of
+`data/raw/aa_pilot/` to a folder the agent session does not use, records their sha256, and puts them back only after
+the Model A fit JSON and its sha256 are committed.
+[FW-B] SIM-VAL rows are extracted by a separate agent session that did not run the fit, after the fit hash is
+committed; it is given the frozen fit JSON's hash, never its estimates, before extraction ends.
```

### C4. §5 Then (L58-L60): RESEARCH_ONLY and the minimum for a fit

```diff
-Fit `sim_aa_1` (first-order, Arrhenius in T) on verified SIM-CAL rows only, and freeze and hash the fit. Predict SIM-VAL
-retention and report the error with no threshold (pilot, descriptive). Report everything, including rows lost at each
-step.
+Fit `sim_aa_1` (first-order, Arrhenius in T) on verified SIM-CAL rows only, and freeze and hash the fit. The §4
+target becomes a minimum: if the verified, included rows (§6) do not give at least 3 temperatures in each of at
+least 2 SIM-CAL papers, or the fitter refuses (`simulation/aa_pilot_fit.fit_model_a`: at least 2 papers, and the
+design identifies Ea), Model A is **NEED_DATA**: no PARAM row, no SIMULATE route. Predict SIM-VAL retention and report the
+error with no threshold (pilot, descriptive). **Step 27 is RESEARCH_ONLY from the start:** SIM-VAL holds 4 papers
+(3 if AAK-05 is missing), below the plan's minimum of 5 groups (Step 15 G15-f), so no outcome of this pilot moves
+`sim_aa_1` beyond NOT_VALIDATED / RESEARCH_ONLY. Report everything, including rows lost at each step.
```

### C5. New §7 after §6 (L62-L83): domain gate and analyte basis

```diff
+## 7. Where a SIMULATE number may be used (added S178, before any verification or fit)
+
+- **Domain gate.** A `sim_aa_1` output may be emitted only for an event that passes all of: (i) the matrix is on a
+  matrix-class list of liquid or pulpy acidic fruit matrices (juices, nectars, pulps, purées, fruit in syrup),
+  written as ING ids by the agent from the CAL matrices and committed with the lock; (ii) the pH condition below;
+  (iii) temperature within 60-100 °C (the fit range, §6); (iv) NO_WATER_CONTACT, by a medium-to-contact map
+  committed with the lock (`simulation/systems.py` requires the caller to supply it; unmapped media are refused).
+  Any event outside the gate, or with any gate input UNKNOWN, gets no SIMULATE output (UNKNOWN never routes to
+  SIMULATE). Leaching stays UNKNOWN (no CAL paper identifies k_L or K_p), so vegetables boiled in water stay UNKNOWN.
+- **pH condition** [pH-A]: "matrix pH as stated in the paper, else NOT_REPORTED_BY_SOURCE" is added to the
+  extracted fields of §2 for the CAL papers and verified with the other fields. The gate range is the minimum to
+  maximum stated pH over the verified CAL papers. An event passes only if its food's pH interval in
+  `registry/food_ph_fda2003_v1.csv` lies inside that range; a lower-bound-only entry or no entry is UNKNOWN. If fewer
+  than 2 CAL papers state pH, the gate falls back to pH-C. [pH-B: a fixed upper bound written here with its opened
+  source; the agent proposes no recalled number.] [pH-C: no pH gate; the matrix-class list carries the acidity
+  restriction and the report says "pH not gated".]
+- **Analyte basis.** `sim_aa_1` models reduced L-ascorbic acid with no DHA compartment, while the target SVAR-000009
+  is total vitamin C (USDA 401). Every SIMULATE output is labelled "reduced ascorbic acid retention" and carries
+  `BASIS_MISMATCH_TOTAL_VITC` wherever it is shown beside a total-vitamin-C value. SIM-VAL comparisons use only rows
+  with the same analyte basis as the CAL rows; rows on another basis are reported separately.
+- **Pre-declared sensitivities (D-AA-4; the primary Model A is unchanged):** Model A refitted (a) without CAL papers
+  whose process has water contact (AAK-09, mango blanching, if its verified rows say so) and (b) without rows whose
+  assay is not AA-specific (the AI flag on AAK-06, iodine titration, if verification confirms it). Both are reported
+  beside the primary fit, never instead of it.
```

### C6. Signatures (L85-L88)

```diff
-- Kush Tokas: ______ date ______
-- Parv Goyal: ______ date ______
+This file is signed only by `reports/step10/aa_pilot_prereg_signature_Kush.json` and
+`reports/step10/aa_pilot_prereg_signature_Parv.json` (final names: the lock note), each typed and committed by its
+signer before any verdict is read: `{"prereg_sha256": "<sha256 of this file>", "signed_by": "Kush Tokas" | "Parv
+Goyal", "signed_date": "YYYY-MM-DD"}`. Nobody types a name into this file.
```

## 3. Code needed so every rule is computable (agent work; not done by this lane)

| Item | Where | Option |
|---|---|---|
| Matrix-class list and medium-to-contact map | two small registry files, committed with the lock | all |
| pH field | CAL extraction schema + verification sheet column; gate reads `registry/food_ph_fda2003_v1.csv` (`ph_low`, `ph_high`, `value_type`) | pH-A |
| NEED_DATA | the caller of `aa_pilot_fit.fit_model_a` maps `FitRefused` to NEED_DATA | all |
| Basis label | the SIMULATE output record (router SIMULATE wiring, T5-C11-R4) | all |
| Sensitivities | `aa_pilot_fit` called on filtered row sets; written beside the primary fit JSON | D-AA-4 |

## 4. Hash after lock

```bash
git show <LOCK>:reports/step10/aa_pilot_preregistration_DRAFT.md | sha256sum      # macOS: | shasum -a 256
sha256sum reports/step10/aa_pilot_preregistration_DRAFT.md                        # must match
git diff --exit-code <LOCK> -- reports/step10/aa_pilot_preregistration_DRAFT.md   # must print nothing
sha256sum reports/step10/aa_pilot_preregistration_AMENDMENT_S178_DRAFT.md         # provenance, for the lock record
```
The lock record also carries the CAL packet sha256 (`471585da…74ea`), the matrix-class list and contact map hashes,
and (FW-A) the sha256 of each sealed SIM-VAL PDF.

Sources: ops pack A3, §4.3; consensus T2-C09-R1..R4, T5-C10-R5/R6, T9-C26-R5; REV-A V7, Q16; REV-B F-09, G-16, B2.3;
D-076; `aa_kinetics_source_candidates_v1.csv`; `aa_pilot_CAL_packet_manifest_v1.json`; `simulation/aa_pilot_fit.py`;
`simulation/systems.py`.
