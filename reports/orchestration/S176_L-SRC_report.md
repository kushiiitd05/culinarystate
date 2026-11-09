# S176 lane L-SRC: scientific sourcing for scenario defaults and mechanism condition windows

Status: DRAFT / AI_DRAFTED / PROPOSED. Nothing here is a human verification, approval or signature (law 7). The live
defaults registry (`registry/scenario_defaults_v1.csv`), every ledger and every orchestrator-only file are untouched.
Built 2026-11-08 in worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, base `07fc0d2`, uncommitted).

## 1. What was built

| File | Rows | sha256 |
|---|---|---|
| `registry/scenario_defaults_source_review_S176.csv` | 97 (27 heat rows keyed SD-xxx + 70 non-heat rows) | see section 8 |
| `registry/mechanism_condition_windows_draft_v1.csv` | 149 windows over 17 MECH keys | see section 8 |
| `reports/orchestration/S176_L-SRC_report.md` | this report | n/a |

- **Review file.** It has the 11 requested columns in the requested order. Heat rows keep their SD keys.
  - Non-heat rows reuse the keys of the L-NH lane's `registry/scenario_defaults_nonheat_v1.csv` where that lane already has the quantity (NH-xxx; a class split is written `NH-032:BRASSICA`). The L-NH file's sha256 at the time of reading was `047732f4...8cf8d4`.
  - Quantities that lane does not hold get new `LSRC-*` keys: Plank constants, altitude boiling point, oven error, cook value, forced-air h, water ratios, AA leaching, cooling time and others.
  - Every NH row of the L-NH registry is reviewed.
  - The live heat registry has **27** data rows. The packet's "28" counts the header line.
- **Window file.** Its columns are as requested:
  - axis, normalised `condition_axis` plus `axis_detail`, `cv_id_proposed` and schema `location`
  - `window_type` with `window_type_basis` (what the evidence shows and why this type was chosen)
  - matrix scope, and bounds with STATED / OPEN_STATED / NOT_REPORTED status, in the source's unit plus the canonical CV unit (K, s, fraction)
  - evidence locator, verification, `usable_for = QUALITATIVE_ONLY` on every row, and `status = AI_DRAFTED_CANDIDATE_PENDING_H4`

## 2. Method

**Who searched.** Five literature sub-lanes ran in parallel. Each got the same binding rules (`PREAMBLE.md` in the lane scratch dir):
- S1: standards, GOV guidance and physical constants
- S2: heat transfer
- S3: mass transfer and drying
- S4: vitamin C, chlorophyll and cutting-triggered enzymes
- S5: starch, protein, pectin and Maillard

The lane lead covered the culinary bath temperatures, oven, air fryer and pan rows, cut sizes, the EU acrylamide text, FSIS, NCHFP blanching, the latent heats and the chlorophyll pH direction. The lead also assembled, re-checked and validated everything.

**Evidence standard.**
- Numbers come only from PRIMARY papers, HANDBOOK tables, STANDARD texts (EU, CFR, Codex) or GOV pages.
- Reviews are REVIEW_CONTEXT: they give a direction only, never a bound.
- ExPASy ENZYME entries are labelled DATABASE. They are used only for reaction definitions (co-substrates), never for numbers.

**Verification flag (strict definition).** `SOURCE_OPENED_BY_AI` means three things:
1. The cited page was fetched in this session and its text holds the statement.
2. The locator says where, with **"Abstract"** written whenever only the abstract was read.
3. Every number in `proposed_range` is either printed in such a source, derived from printed numbers by arithmetic stated in `notes` (unit conversion, interpolation, Arrhenius evaluation, midpoint), or a stated pick inside a printed band (flagged as a pick).

Anything else is `UNVERIFIED_CANDIDATE`, with the candidate source and where to look.
- If a row has a sourced bound but an unsourced bracket value, it stays UNVERIFIED and the sourced part is noted as a "partial anchor".
- A bound status other than NOT_REPORTED is used only with a PRIMARY source and `SOURCE_OPENED_BY_AI`. The validator enforces this.

**Access routes.**
- Europe PMC REST abstracts (PubMed, AGRICOLA, AGRIS), the OpenAlex abstract index (11 rows, marked "reconstructed")
- PMC and J-STAGE full texts, govinfo / FSIS PDFs, EUR-Lex, NIST WebBook, NCHFP, USDA ARS and AMS PDFs
- PDFs saved by WebFetch were read with `pdftotext` to stdout. Those saved copies are outside the repo, under `~/.claude/projects/.../tool-results/`.
- No piracy or upload sites were used, and no BBC data.

**What was blocked.**
- 403 / captcha: fsis.usda.gov, Wiley, ScienceDirect, MDPI, cerealsgrains, ACS.
- A US Navy cook glossary mirror had a TLS certificate mismatch. An insecure fetch was refused by the permission layer and was not pursued.

**QA re-checks by the lane lead.** Ten load-bearing sub-lane claims were re-opened and all matched:
- Munyaka 2010 (80 °C / 10 min ascorbate oxidase)
- Bode 1990 (DHA decay at pH 7-8 vs pH 3-5; temperature)
- Gil 1999 (60 % of vitamin C in the cooking water)
- Leong & Oey 2012 (80 °C; 60-70 °C)
- Carson 2006 (15-40 W/m²K)
- Krall & McFeeters 1998 (β-elimination above pH 3.8)
- Martens 1982 (myosin 40-60, actin 66-73, collagen 56-62 °C)
- Plank P/R table (Singh handout)

**Third-party text.**
- The sub-lanes' verbatim audit snippets were dropped; all CSV text is paraphrase.
- Short quoted fragments were reworded.
- A 7-word-shingle check against all snippets leaves 2 overlaps: a run of DSC temperatures and an IUBMB reaction equation (data, not prose).

**Not done.**
- No ledger append and no SRC/EVD id minting: `evidence_id` is left for H4.
- No edit to the live registries and no git writes.
- `tools/log_step.py` (CLAUDE.md) was not run, because orch_ctx makes `WORKLOG.md` orchestrator-only.

## 3. What is verified versus candidate

| Group | Rows | SOURCE_OPENED_BY_AI | UNVERIFIED_CANDIDATE |
|---|---|---|---|
| Heat defaults (SD-001..SD-060) | 27 | 13 | 14 |
| Non-heat quantities (NH-*, LSRC-*) | 70 | 45 | 25 |
| Mechanism windows | 149 | 132 (116 abstract-level, 11 table/section-level, 5 ExPASy definitions) | 17 |

- 77 windows carry numeric bounds, all from verified PRIMARY sources. No NECESSARY T, pH or aw gate sits on a CHEMICAL_REACTION entry (rule E-7: 0 cases).
- Abstract-level verification is honest but shallow. Before any row is ACCEPTED, the full text must be checked at the locator.

### 3.1 Heat defaults: proposed changes (the live registry was NOT edited)

| Key | Current | Proposed | Basis | Flag |
|---|---|---|---|---|
| SD-001 simmer | 85/90/95 | keep | operational definitions 85 °C (Kimindu 2025), 95 °C (Tajima 2001); 70 °C in Flannery 2014 as a sensitivity case | V |
| SD-002 poach | 70/80/90 | keep; eggs up to 100 | only Cano 2026 (eggs poached in boiling water) | U |
| SD-003 blanch | 95/98/100 | 100/100/100 at sea level, local boiling point at altitude | NCHFP blanching page | V |
| SD-004/005 braise, stew | 85/90/95 | keep | no source | U |
| SD-006 pressure-cook | 110/118/121 | **108/115/121** (5/10/15 psig) | NIST saturation rows + NCHFP Guide 1 | V |
| SD-007 scald, SD-009 shallow-fry, SD-011 sweat | – | keep | no source | U |
| SD-008 deep-fry | 160/175/190 | keep (≤175 for potato products) | EU 2017/2158 Annex I(b), II(A); frying studies at 150-190 °C | V |
| SD-010 pan contact | 140/170/200 | **140/180/250** (or split stir-fry/sear) | pan set-points 140-250 °C in 4 primary studies | V |
| SD-012 oven | 160/180/220 | 163/180/220 | FSIS ≥325 °F for roasting; EU 180-220 °C | V |
| SD-013 air fryer | 180/190/200 | 180/200/220 | EU 2017/2158 end-user text | V |
| SD-020 gas marks | table | keep | no official table found | U |
| SD-030 h water | 200/600/1500 | 200/500/1000 | generic band (Incropera, reproduced in a handout) | V |
| SD-031 h steam | 1000/3000/8000 | keep | low end below the opened band | U |
| SD-032 h oil | 250/450/700 | **200/500/850** | 7 frying papers | V |
| SD-033 h still-air oven | 15/25/40 | 10/20/30 provisional | no static-oven value opened | U |
| SD-034 h fan oven / air fryer | 30/50/80 | **split: fan 15/25/40; air fryer 66/71/76** | Carson 2006; Gouyo 2021 | V |
| SD-035 h pan contact | 200/500/1000 | **100/300/512** | Viné; Rocca-Poliméni 2019 | V |
| SD-040 k | 0.45/0.5/0.6 | 0.41/0.50/0.60 | NIST water; potato purée; cocoyam | V |
| SD-041 α | 1.2/1.4/1.6e-7 | 1.10/1.35/1.60e-7 | NIST-derived water α; cocoyam | V |
| SD-050..053 cut sizes | – | keep; diced ≤ 6.35 mm half-thickness (USDA Grade A frozen carrots) as the only GOV anchor | USDA AMS §52.702, Table I | U |
| SD-060 T0 | 4/20/25 | split FRIDGE 3/5/8 (sourced) and ROOM (unsourced) | refrigerator surveys | U |

**Biot triage.**
- Water, steam, oil and pan h all give Bi ≫ 1 (h/50 for k ≈ 0.5 W/mK at 1 cm), so their exact value barely moves the centre trajectory.
- Ovens and air give Bi ≈ 0.3-1.5, so SD-033, SD-034, cut sizes, T0 and durations dominate the sensitivity. Human verification effort should go there first.

### 3.2 Non-heat quantities: what is now sourced

- **Fridge:** NH-001 3/5/8 °C. Two primary surveys (means 5.1 and about 5.9 °C, SD 2.2-2.8) plus FDA, Food Code and FSA ceilings.
- **Freezer:** NH-002 −18 °C, warm bound −15 °C (EU tolerance). The cold bound is unsourced.
- **Defrost:** NH-013, fridge or running water ≤21 °C (Food Code §3-501.13).
- **Dehydrator:** NH-008 60 °C, thermostat range 29-71 °C (NCHFP).
- **Pressure canner:** NH-010 115.6-121.1 °C.
- **h, cold air and water:**
  - still cold air 3/6/10 W/m²K (NH-020/021/025)
  - forced air 10/25/50
  - ice bath / hydrocooling 200/500/900, with the USDA TB 1292 peach hydrocooling value of 710-937 W/m²K
- **Freezing:**
  - Plank P/R for slab, cylinder and sphere: 1/2, 1/8; 1/4, 1/16; 1/6, 1/24.
  - Plank under-predicts by about 25 % (one fish study).
  - L0 = 333.6 kJ/kg; food latent heat = (x_w0 − x_b)·L0.
  - Initial freezing-point classes for produce (HB66): −3.0 to −0.2 °C. Hake mince −1.3 °C.
  - Ice k from the Choi-Okos equation, as reproduced.
- **NaCl diffusivity:**
  - meat 1.24/2.0/4.0e-10 m²/s
  - fish 0.88e-10/2.44e-10/1.45e-9
  - vegetable uptake 1.7e-11 (single value)
- **Acetic acid diffusivity:** fish 3.4e-10 (single study).
- **Drying:** effective moisture diffusivity 1e-10/4e-10/3.6e-9 m²/s with Ea 28-66 kJ/mol, and a falling-rate-only default.
- **F0 and cook value:** z = 8.9/10/11.1 °C, T_ref 121.1 °C (FDA ITG 7). The cook value convention T_ref 100 °C, z 33 °C is in use (Babu 2022); its origin is unverified.
- **Altitude boiling point:** 99.97 / 96.65 / 94.98 / 93.31 / 89.97 °C at 0 / 1000 / 1500 / 2000 / 3000 m. Derived, and matches FSIS within 0.3 °F.
- **Cooling time limits:** Food Code and FSA.
- **sim_aa_1 inputs:**
  - Water ratios: 8.35 L/kg for blanching (NCHFP) and 5 L/kg for boiling (Lee 2018).
  - Apparent ascorbic acid leaching D: 1.2-2.4e-9 m²/s (potato, 65-93 °C).
  - 60 % of spinach vitamin C ends up in the cooking water.
- **Wet surface cap:** a wet surface stays near 100 °C until a crust forms (Cernela 2015).
- **Oven calibration error:** **no citable source** (LSRC-OVEN-ERR = UNKNOWN).

## 4. Mechanism windows: what the literature shows

Each bullet gives the window type for that axis. All rows are usable only as QUALITATIVE flags.

**Ascorbic acid → DHA (oxidation).**
- An oxidant is NECESSARY. Without O2 the aerobic route stops and loss goes to furfural by the anaerobic route (MCW-0006/0007).
- Cu and Fe catalysis is MODULATING. It is NECESSARY only in metal-free pH 7 buffer, which is not a cooking condition, and the schema encodes catalysts as MODULATING (MCW-0001).
- Temperature (50-90 °C), headspace O2 (10-30 %) and pH (the dissociated form oxidises faster) are MODULATING.
- Cysteine reverses the step.

**DHA → 2,3-diketogulonic acid (hydrolysis).**
- O2-independent.
- Much faster at pH 7-8 than at pH 3-5, and faster at higher temperature. Both axes are MODULATING.
- Bicarbonate catalyses it, with a half-life of minutes in plasma.
- Irreversibility is not stated in any opened abstract.

**Ascorbate oxidase.**
- O2 is a NECESSARY co-substrate. The product is the monodehydroascorbate radical, so the enzyme acts at the same ascorbic acid → DHA node.
- Inactivation is INHIBITING above:
  - ≥80 °C for 10 min (broccoli, nearly complete)
  - 80 °C (carrot, complete)
  - >90 °C for short times (cowpea leaves)
- It stays active at 30-70 °C in crushed tissue, which turns AA into DHA. This is primary support for a start-mode / come-up history item (EQ21-09).
- NCHFP adds that under-blanching stimulates enzymes.

**Leaching.**
- Contact with liquid water is NECESSARY.
- Temperature is MODULATING: Arrhenius over 65-93 °C.

**Chlorophyll → pheophytin.**
- pH is **MODULATING**: the rate constant falls log-linearly as pH rises (Ryan-Stoneham & Tong 2000, opened by the lane lead). This is primary support for rule E-7 on this entry (EQ21-07a).
- Temperature is MODULATING over 70-145 °C.
- Zn complexes form more from pH 4 to 6 and less at pH ≥ 8 (121 °C).
- A 1-min blanch activates chlorophyllase. Its temperature limits are second-hand only.

**Starch gelatinisation.** Onsets were measured at 10 K/min in ≥ 60 % water: wheat 60.3 °C, maize 64.7 °C, tapioca 64.8 °C.
- These are NECESSARY lower bounds on that time scale. Potato, rice, egg and muscle values are peaks and were moved out of the bounds, because a peak is not an onset.
- Limited water pushes melting to a higher-temperature endotherm (Donovan 1979; Eliasson 1980).
- 20 % sucrose raises To by 0.8-3.2 K. NaCl and ion type shift To.
- All of these effects are MODULATING.

**Muscle and egg.**
- Beef: myosin denatures over 40-60 °C, actin over 66-73 °C and collagen over 56-62 °C.
- Fish is lower: carp myosin peaks near 50 °C, and blue grenadier skin collagen shrinks at 48 °C.
- pH and salt shift the transitions (NaCl −4 K, CaCl2 −6.5 K).
- Collagen solubilisation is a time × temperature process (24 h at 60 °C; sous vide at 55-75 °C). No hard ≥ 70-80 °C NECESSARY bound is supported.
- Egg white peaks: ovotransferrin 65 °C (70 °C at pH 9), ovalbumin 84 °C, S-ovalbumin 92.5 °C.
- Acidified yolk gels at 70-73 °C.

**Pectin.**
- β-elimination dominates above pH 3.8, and also at pH 4-4.5 when pectin is highly methylated.
- Every pathway speeds up over 80-110 °C. No pH stops degradation, so pH and temperature are MODULATING.
- Ca2+ speeds β-elimination of soluble pectin but firms tissue. The sign depends on the matrix.
- PME is irreversibly activated at ≥ 45 °C. Firming needs 60-65 °C for more than 30 min (carrot), and PME is inactivated from 45 to 57.5 °C. These effects are MODULATING, not INHIBITING.

**PPO, alliinase, myrosinase.**
- O2 (PPO) and water (myrosinase) are NECESSARY by definition.
- Thermal inactivation is INHIBITING:
  - PPO: 65 °C for 6 min (mushroom extract); 80 °C for 5 min (apple)
  - alliinase: about 90 % loss after 30 s in a microwave
- PPO is activated at 45-65 °C early in heating (come-up).
- Alliinase is blocked below pH 3.6. This comes from an abstract and may be background.
- Myrosinase loss starts at 35 °C in cabbage. A 60 °C pre-heat removes ESP but spares myrosinase. Steaming at 100 °C for 4 min removes only 64 % (red cabbage).

**Maillard.**
- It runs at 20-60 °C in storage and at 100 °C in water.
- The rate peaks at aw 0.63 (20 °C) or 0.82 (120-200 °C), and rises with pH.
- Every axis is MODULATING. There is **no onset temperature**.

## 5. The 10 most important gaps (where a human should look)

1. **Still-air and fan-oven apparent h.** Look in Sakin et al. 2009 (J Food Eng 94:344-349, full-text tables) and Becker & Fricke 2004 (Int J Refrig 27:540-551). These are the highest-sensitivity defaults (Bi 0.3-1.5).
2. **Home cut-size classes** (minced, sliced, chopped, julienne). Only the commercial USDA Grade A diced limit (≤ ½ inch) is sourced. A culinary standard or the corpus's own stated sizes is needed.
3. **Room temperature and cold tap water** (T0, cool, rinse). ISO 554 and IUPAC SATP were not opened, and no survey was found.
4. **Oven set-point error and thermostat cycling.** No citable source exists. IEC 60350-1 is paywalled, and the DOE 10 CFR 430 Appendix I was not opened.
5. **Vitamin C leaching vs degradation split and the water-ratio effect** (sim_aa_1 k_L, K_p). Only Gil 1999 (spinach, 60 % in water) and Arroqui 2002 (potato, apparent D) are sourced. The Nakashima 2014 J-STAGE full text (Japanese) and the Vallejo broccoli study were not reached. Turning D into k_L needs piece geometry.
6. **Enzyme state history.**
   - No primary compares a cold-water start with a boiling start directly.
   - No T × t window for complete inactivation of chlorophyllase, alliinase or myrosinase.
   - No low-pH inhibition of a food PPO.
   - DHA irreversibility and the Khan & Martell 1967 metal kinetics are unopened.
7. **Initial freezing points of meat, poultry, fish, egg and dairy.** Only hake mince is sourced. Look in the ASHRAE "Thermal Properties of Foods" table and Whiteman 1957 (USDA).
8. **Diffusivities beyond single studies.**
   - Acetic acid in vegetables and meat.
   - NaCl in beef, and its temperature dependence from 2 to 25 °C.
   - The skin-limited model for whole produce (Passos 2005 shows Bi → ∞ is wrong for whole cucumbers).
9. **Culinary conventions with no authoritative source:** poach, braise, stew, scald, sweat, shallow-fry, gas marks. Simmer has only operational definitions in three primary papers. BBC Good Food is excluded under D-003.
10. **Onset (To) rather than peak temperatures** for egg white, whole muscle, yolk, potato and rice starch. The DSC 10 K/min time-scale caveat also applies to long holds such as sous vide (collagen shrinks at 55-60 °C when heating is slow).

## 6. Recommendations for packet Q2, Q5 and Q15

**Q2: sources for the defaults.**
- **Source classes.**
  - A handbook or GOV value with a range and an exact locator is acceptable for Layer 2 SCENARIO rows.
  - Prefer primary measurements where the number moves the trajectory (oven and air h, size, T0, duration).
  - Accept generic engineering bands where Bi ≫ 1 makes the value irrelevant (water, steam, oil h).
  - Safety conventions should cite the regulation or GOV text: fridge, freezer, canning, F0, cooling limits.
- **Culinary word definitions** (simmer, poach, scald, gas mark) are *conventions*, not physics. Label them CONVENTION. Cite operational definitions from primary studies or a culinary standard, or keep the step UNKNOWN or qualitative.
- **Status ladder.** Adopt three states: `SOURCE_UNVERIFIED_AGENT_RECALLED` → `SOURCE_LOCATED_AI_OPENED` (what this file supplies, with locators) → `SOURCE_VERIFIED_HUMAN` (a human opens the locator).
  - Do not promote any row on this file alone.
  - Change only `source_status` and `source_hint`. The SD triples change only where a human accepts a proposal from §3.1.

**Q5: non-heat formulas.**
- **Plank** (verified P/R) is adequate for a first pass. Treat it as the short-time (GENTLE) side, since it under-predicts by about 25 %, and keep the Cleland/Pham-type form (Cuesta 2021) as an upgrade.
  - Inputs: L = (x_w0 − x_b)·333.6 kJ/kg; initial freezing-point classes; still-air h 3-10 or forced-air h 10-50 W/m²K.
- **Fickian slab uptake** is consistent for meat slabs and cut pieces. Ozuna 2013 assumed negligible external resistance.
  - It is wrong for whole unpeeled produce, which is skin- or stomata-limited. Add a finite-Bi skin term or keep those steps QUALITATIVE.
  - Use the diffusivities in §3.2. In pre-salted fish, salt uptake was not Fickian.
- **Drying:** use falling-rate only as the default. A constant-rate period was absent (banana) or lasted only minutes (carrot).
- **F-value:** z = 10 °C (8.9-11.1) and T_ref 121.1 °C are verified. Apply them only to canning or sterilising steps; ordinary cooking gives F0 ≈ 0.
- **Cook value** (100 °C, z = 33 °C): keep as a dose index, not a nutrient model.
- **Extra pieces needed:** an altitude correction of the boiling point (Q6: yes, as a Layer 2 uncertainty), the wet-surface cap, a thawing-medium switch, and cooling-time bounds.

**Q15: mechanism condition windows.**
- **Acceptable sources:**
  - PRIMARY papers for every numeric bound. Abstract-level is acceptable for drafting only; check the full text before ACCEPTED.
  - Curated enzyme databases for co-substrate NECESSARY windows.
  - Reviews for direction only.
  - Extension or GOV guidance for qualitative practice statements.
- **Rule E-7 is supported.** For non-enzymatic chemistry (ascorbic acid oxidation, DHA hydrolysis, chlorophyll, pectin, Maillard) the literature shows continuous rate changes with temperature, pH and aw, never absence. Keep these axes MODULATING.
- **NECESSARY is well founded for:**
  - co-reactants: O2, water
  - enzyme presence
  - phase-transition onsets, scoped to matrix and heating rate
- **Enzyme inactivation** is a T × t INHIBITING window. It needs the thermal-dose history item, not a scalar T gate.
- **Is the screen useful while all 32 MECH entries are unreviewed? Yes, but only as QUALITATIVE flags.**
  - Rows stay CANDIDATE, and recipe inputs (pH, aw, O2, metal ions, cell integrity) are mostly UNKNOWN. So the screen will return UNKNOWN for most lot-steps. The card calls that correct behaviour.
  - It already earns its keep in three ways: routing (which evidence to look for), explaining interaction edges, and blocking false NOT_POSSIBLE results from folk thresholds such as "Maillard needs 140 °C".
  - Review first the ~16 vitamin C pilot rows: MCW-0004, -0005, -0006, -0007, -0009, -0012, -0013, -0015, -0020, -0021, -0022, -0025, -0026, -0029, -0030, -0132.
  - Then review the chlorophyll rows (MCW-0031..0042) for sim_chl_1.

## 7. Open questions for the humans (H4; nothing decided here)

1. **MCW-0001 (metal catalysis).** Accept MODULATING rather than the literature's model-system NECESSARY (D21-20 / rule M-1)?
2. **Peak values.** Accept that peak (Tp) values, and one undefined "Tgel", are never used as NECESSARY lower bounds? Eight rows were moved to notes.
3. **Bracket semantics** for quantities with no "heat exposure" direction (freezing point, h in cooling, defrost medium). Are GENTLE / TYPICAL / INTENSE ordered by exposure or by value?
4. **Row splits:** SD-034 (fan oven vs air fryer), SD-010 (stir-fry/sear vs pan-fry), SD-060 (fridge vs room start).
5. **Abstract-level verification.** Is it enough for SOURCE_LOCATED, with full text required for SOURCE_VERIFIED_HUMAN?
6. **Evidence ids.** SRC/DOC ids for the about 119 cited documents are unminted (ledgers append-only and lane-forbidden). The humans decide when and how to mint them.

## 8. Tests, checks and runs

- **Validation script** (lane scratch, `validate_lsrc.py`). It checks:
  - headers
  - unique keys
  - all 27 SD keys present, every NH key present in the L-NH registry, all NH rows reviewed
  - flag and source-type vocabularies
  - bounds only from verified PRIMARY sources; NOT_REPORTED ⇒ empty value
  - schema `location` enum and mechanism keys present in the roster
  - E-7 and quote characters
  - 7-word overlap with verbatim snippets

  Result: **0 failures**. The 2 residual overlaps are a run of DSC temperatures and an enzyme reaction equation.
- **Repo test.** `pytest tests/unit/test_external_data_policy.py::test_no_credentials_in_repository_files` could not be collected: `lxml` is missing from `.venv312` (environment issue, unrelated). Instead its secret regex was run over the three lane files: no match.
- **Compute runs:** none. This is a literature lane, so no rows are added to `registry/compute_runs_v1.csv`. Its header is `run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes`.
- **Builder and sources.** The files were built by `build_lsrc.py` (lane scratch) from the sub-lane JSONL files. Those files hold verbatim audit snippets: keep them out of commits. Scratch dir: `/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad/lsrc/`.
- **sha256 at hand-off** (computed after the last build):
  - `registry/scenario_defaults_source_review_S176.csv`: `8b72cf3fbcf290b3df4fb4bc3affdec51bdfc31b059b581303e6ac51a6ad0342`
  - `registry/mechanism_condition_windows_draft_v1.csv`: `759daa1ad6aaae361eae29032b0faebd7a1de9384e4ae140c867008d951d6439`
