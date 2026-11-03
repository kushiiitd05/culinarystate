# Step 26.0 system selection record — TEMPLATE, UNSIGNED

Prepared by AI worker prv (S159) as a blank template. It is not a decision, not a verdict on which system to use
and not a signature (D-045). Machine-readable twin: `reports/step26/system_selection_record_TEMPLATE.UNSIGNED.json`.

## What this record is for

- Plan v2 Step 26 card, "Selection rule (26.0)": *transcribe, do not re-decide,* the single 11.D DECISIONS entry
  (AA, CHL or NEED_DATA), made once by applying the 10a rule to VERIFIED counts. 26.0 records that entry and the
  pre-registered quotas, and states which quota set 11.D applied. NEED_DATA routes to Step 14.
- D-027: SIM-AA-1 is the **leading candidate**, chlorophyll (SIM-CHL-1) the **pre-registered fallback**; the final
  choice comes after Step 10/11 evidence. R-14: SIM-AA-1 is not frozen; one switch only, no fishing.
- Written and signed by Kush **and** Parv before any parameter fit. The two signatures are separate files that
  must not be identical (lesson from the 07H provenance-invalid audit).

## 1. Source 11.D entry (transcribed, not re-decided)

| Field | Value |
|---|---|
| DECISIONS entry id | ____ |
| Date | ____ |
| Quota set applied by 11.D | ____ |
| Step 10 census report (path, sha256) | ____ |

Selected system: ____ (one of `sim_aa_1`, `sim_chl_1`, `NEED_DATA`)

## 2. Candidates

| System | Role (D-027) | 26b structure | Implementation | Evidence refs |
|---|---|---|---|---|
| `sim_aa_1` | leading candidate | SIM-AA-1-STRUCTURE-0.1.0-draft: tissue / water / degraded compartments, reference-T Arrhenius degradation, lumped leaching with K_p/r back-exchange, optional k_dw, optional lumped T_p lag | `src/culinarystate/simulation/sim_aa_1.py` (DRAFT_PENDING_26_0_H4) | ____ |
| `sim_chl_1` | pre-registered fallback | SIM-CHL-1-STRUCTURE-0.1.0-draft: Chl a / b to pheophytin a / b, first-order Arrhenius times a caller-supplied g(pH) value, no leaching term, optional T_p lag | `src/culinarystate/simulation/sim_chl_1.py` (DRAFT_PENDING_26_0_H4) | ____ |

Both sit behind one interface (`systems.simulate`), so a switch costs only calibration. Their 26c synthetic
verification is engineering evidence for the code. It says nothing about which system the data support.

## 3. Criteria (pre-registered quotas): all fields blank

The card's Data & licence row lists PROPOSED_PILOT quotas. They are **not** adopted here. The value column holds
the number the signers pre-register; the count column holds the VERIFIED count 11.D used.

| Criterion | Applies to | Pre-registered value | VERIFIED count | Evidence refs | Met? |
|---|---|---|---|---|---|
| Q-K1-SERIES: K1+ kinetic series | AA, CHL | ____ | ____ | ____ | ____ |
| Q-LAB-GROUPS: independent lab groups and SIM-CAL / SIM-VAL / DS-TEST allocation | AA, CHL | ____ | ____ | ____ | ____ |
| Q-MATRICES: distinct matrices | AA, CHL | ____ | ____ | ____ | ____ |
| Q-TEMPERATURES: distinct temperatures | AA, CHL | ____ | ____ | ____ | ____ |
| Q-K2-GROUPS: groups with K2 designs | AA, CHL | ____ | ____ | ____ | ____ |
| Q-LEACHING: leaching-informative studies (water assay or open-vs-sealed) | AA | ____ | ____ | ____ | ____ |
| Q-SIM-VAL-RESERVE: groups reserved for SIM-VAL | AA, CHL | ____ | ____ | ____ | ____ |
| Q-CHL-SET: chlorophyll quota set (set at 10a) | CHL | ____ | ____ | ____ | ____ |

## 4. Pre-registration binding

| Field | Value |
|---|---|
| Pre-registration document (`reports/step26/preregistration_v1.md`) | ____ |
| sha256 of the pre-registration | ____ |
| Frozen before any data seen? | ____ |
| `data_seen_before_registration` | ____ |
| Written before any parameter fit? | ____ |
| Switch used (one only) and rationale | ____ |

## 5. Open items carried into this record (from S159 26b, for the signers' attention)

- K_p dimension (r kept in mL/g, so K_p is volume per mass rather than the card's dimensionless "default 1").
- g(pH) functional form for SIM-CHL-1 is not given by the card; the 26b draft takes a caller value per pH band.
- tau_h per size class and the Choi-Okos coefficients are caller PARAM inputs; none are entered.
- M&S limits belong to the 26e model card; G26-VER / G26-CAL numbers are PROPOSED_PILOT until pre-registered.

## 6. Signatures (blank)

| Signer | Signed | Date | Signature file | sha256 |
|---|---|---|---|---|
| Kush Tokas | no | ____ | ____ | ____ |
| Parv Goyal | no | ____ | ____ | ____ |

Status: UNSIGNED. Nothing in this template is a choice.
