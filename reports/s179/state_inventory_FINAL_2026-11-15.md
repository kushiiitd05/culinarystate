# CulinaryState — finalized state-variable inventory and coverage view (15 Nov 2026)

**Status: FINAL for the 21 Nov submission.** This is the canonical coverage view named by the 15 Nov architecture freeze. It supersedes `state_inventory_gap_matrix_2026-11-14.md` as the view to cite, and adds the compatibility-axis reconciliation and the 36-step owner mapping that the freeze requires. It is **not** a new master plan and introduces **no new architecture name** — every row maps to an existing 36-step owner and to SSOT v15 or an SSOT-v16 change request.

## 0. Frozen pipeline (for reference only, not a new design)

recipe semantic understanding → Typed Event IR → event-sourced CulinaryState `S_t=(G,C,Q,Y,P)` → invariant validator → query-specific evidence compiler → claim packet → LLM verbaliser → claim verifier / template fallback.

Two standing rules this document enforces:

1. **The schema is broad; the observed state is sparse.** `UNKNOWN` with a reason is a valid, complete cell. CulinaryState is **not** defined by the currently populated salt / acid / lipid / water fields — those are what is filled in, not what the representation is.
2. **The state vector is a derived diagnostic, not the state definition.** `STATE_VECTOR_V0` (51 named masked dims) is `DIAGNOSTIC_RETRIEVAL_ONLY`; its weights are fixed, documented and unvalidated, and nothing in it is learned.

## 1. Sources reconciled here

| Source | Path | Status |
|---|---|---|
| SSOT v15 inventory (10-level hierarchy, B03–B14) | `reports/h_state/ssot15_state_program_inventory.md` | authoritative |
| SSOT v16 change set | `docs/SSOT/ssot_v16_change_set_DRAFT.md` | **PROPOSED_ONLY — v15 not edited** |
| Canonical 13-axis compatibility space | `reports/master_plan/master_plan_research_audit_v2.md` §N.7 | spec; registry CSV created 15 Nov |
| State v2 (implementation) | `src/culinarystate/composition/state_full.py` | 183 lines |
| Derived vector | `src/culinarystate/composition/state_vector.py` | 51 dims |
| Compatibility code | `src/culinarystate/retrieval/compatibility.py` | 9 of 13 axes |
| Full-corpus fill rates | `reports/s179/state_dataset_fill_full_2026-11-14.json` | heat-row rates |

**SSOT placement:** State v2 is the first implementation of SSOT **B12 "process-conditioned representation z_{i,t}"**, which the v15 inventory lists as MISSING.

## 2. The freeze introduces nothing new — it lands on existing CRs

This is the central finding of the finalization pass. Each adopt-now item from the 15 Nov directive already has an SSOT-v16 change request, so the work is formalization with minimal code change, not new design.

| Freeze item | Existing SSOT-v16 request | 36-step owner |
|---|---|---|
| 1. Typed Event IR as the parser/LLM → state-engine contract | **CR-25, CR-26** — event fields (kind, implicit args, alternative group, modality, temporal relation, condition profile id, allocation basis); entity parentage/lifecycle; quantity intervals | existing state engine; **no second graph implementation** |
| 2. invariant: UNKNOWN ≠ zero | **CR-07, CR-51** — one missingness/censoring superset, "UNKNOWN ≠ 0" | validator |
| 2. invariant: no unsupported numeric values | **CR-25, CR-26** — `normalized_mass_low_g/high_g`, interval semantics, "never collapse an interval to a fake gram value" | validator |
| 2. invariant: every value carries basis/provenance | **CR-02** — three orthogonal fields `origin_provenance` / `field_status` / `claim_route` | validator (already 100% in State v2 P block) |
| 2. invariant: alternatives are not conjunctions | **CR-25** — alternative group; implemented as flag `VNEXT_ALTERNATIVE_SKIPPED` | lineage vNext (D-132) |
| 3. query-specific evidence compiler, all SSOT axes | **36A.3** canonical 13-axis vector; **CR-57…CR-61, CR-65** packet v2 | 36A |
| 4. Claim Packet | **CR-65** packet v2 fields; RCL claim ledger | 36A |
| 5. claim verifier / template fallback | **CR-57…CR-61** rung enum incl. ABSTAIN; B5T template rung exists | 36C |
| 6. Layer-1 LLM proposer, ambiguity triggers only, span-grounded | **CR-30, CR-32** — MODEL rung requires applicability PASS, all inputs observed, in-domain | 36C whitelist-gated MODEL rung |
| 7. provider-agnostic hosted LLM, stop model hunting | **CR-65** — LLM zero-shot/RAG baselines as controls | 36C |

The v16 change set already labels the RAG contract (CR-57…CR-61, CR-65) **"Design now, implement later — these are breaking changes for Step 36."** The freeze's steps 3–5 are exactly that design work.

**SSOT v16 remains PROPOSED_ONLY.** Nothing here applies it. Per §139 it would be appended as an addendum, never edited in place, and each applied CR needs a `DECISIONS.md` entry.

## 3. State-variable coverage (G / C / Q / Y / P)

Legend: ✅ have · ⚪ partial or exists-but-unwired · ❌ schema only (valid UNKNOWN cell with a reason) · DEFER = ruled out for this submission.

| Variable | Layer | SSOT | State v2 field | Basis | Corpus fill | In vector | 21 Nov |
|---|---|---|---|---|---|---|---|
| food identity / lot / lineage | G | L4, B11 | `lot_members`, `history` | RUNG_A | all events | yes (log_n_members, history_*) | ✅ |
| merge / split / transfer | G | B11 | `event_kind` | RUNG_A | all events | yes (family one-hot) | ✅ vNext B/C DIAGNOSTIC |
| process / family | G/Q | L3, B05 | `process`, `family` | RUNG_A + PROC | all events | yes (18 one-hot) | ✅ |
| cell integrity (intact/cut/crushed) | G | audit | `cell_integrity` | CUT_HISTORY | per step | partial (history_cut) | ✅ |
| piece size / geometry | G/Q | L1 | `piece_size_class` | L1 CUT_HISTORY | 9.7% | **no** | ✅ state / ❌ axis 9 |
| quantity / mass | G/C | B10, CR-26 | — | — | 0.6% groundable | no | **DEFER** (census) |
| salt / acid / lipid / water contact | C | D-116 | `*_present`, `contact_phase` | markers v2 + SR | D116 reports | yes | ✅ (salt/acid AI-check FAIL, D-128) |
| co-member + own composition | C | L5 | `member_composition`, `own_composition` | USDA SR | 793 ING | yes (5 means) | ✅ |
| prior salt / acid exposure | C/hist | audit | `salt/acid_exposure_before` | LINEAGE_C_T | derived | **no** | ✅ state only |
| pH (tissue vs medium) | C | audit | `lot_acidity_band` = UNKNOWN | — | 0% | no | ❌ needs CHEM-D08–D10 |
| water activity / moisture | C/Q | yes | — | — | 0% | no | ❌ |
| molecule set (aroma/taste) | C | L6, IMAP 30,294 | not wired | IMAP / MOL | 313 ING | no | ⚪ CAN |
| medium | Q | yes | `medium` | L1 PROC_DEF / TEXT | 53.8% | **no** | ✅ state only |
| temperature (bath / food) | Q | yes | `temperature_C`, `food_T_typical_C` | L1 + L2 | 16.5% stated / 46.4% scenario | yes | ✅ |
| duration | Q | yes | `duration_min` | L1 TEXT_STATED | 28.2% | yes | ✅ |
| lid / covered | Q | yes | `lid_state` | L1 | 8.8% | **no** | ✅ state only |
| oxygen exposure | Q/Y | audit | `oxygen_exposure_proxy` | LID_STATE_PROXY | ≈ lid rate | **no** | ✅ proxy only |
| start mode (cold/boiling) | Q | yes | `start_mode` | L1 | low | **no** | ✅ state only |
| thermal dose (step / cumulative) | Q/hist | audit | `thermal_dose_typical_min`, `cumulative_thermal_dose_min` | L2 SCENARIO | where L2 runs | **no** | ✅ state only |
| hot-aqueous / hot-fat minutes | Q/hist | leaching | `hot_aqueous_minutes`, `hot_fat_minutes` | SUM_TEXT_STATED | duration-limited | **no** | ✅ state only |
| water:food ratio | Q | L1 `water_ratio` | `NOT_BOUND_V0` | — | 0% | no | ❌ |
| core vs surface temperature | Q | L2 zones | volume-average dose only | L2 | partial | no | ⚪ |
| moisture cap | Q | yes | `moisture_cap_C` | L2 SCENARIO | where L2 runs | no | ✅ state only |
| analyte route + evidence | Y | B06, D4 | `*_route`, `*_evidence`, `*_compat` | router + D-122 | all heat items | yes (10 one-hot) | ✅ |
| vitamin C formula retention | Y | Step 10 | `vitc_formula_retention_typical` | FORMULA_RESEARCH_ONLY | 826 events | yes (2 dims) | ✅ domain-limited |
| enzyme activity state | Y | audit | — | — | 0% | no | ❌ |
| browning / gelatinisation / texture / colour | Y | yes | — | — | 0% | no | ❌ |
| bioaccessibility (≠ content) | Y | CHEM-D03/04 | — | unverified literature | — | no | ⚪ after verification |
| provenance / UNKNOWN reason | P | CR-02 | every cell | — | **100%** | n/a | ✅ |

## 4. Time and conditions: what `S_t` holds vs what the vector sees

This is the sharpest gap the finalization found, and it matters because "state-aware retrieval" is a contribution claim.

`S_t` represents time three ways — step ordinal, per-step `duration_min`, and cumulative history (`cumulative_thermal_dose_min`, `hot_aqueous_minutes`, `hot_fat_minutes`, with partial sums labelled partial and never silently summed). Conditions are the full physics v06 L1 set plus L2 scenario.

`STATE_VECTOR_V0` sees almost none of it:

| Block | Dims | Content |
|---|---|---|
| G | 24 | 18 family one-hot, `step_position`, `log_n_inputs`, `log_n_members`, history heated/cut/separated |
| C | 13 | salt/acid/lipid/aqueous present, 4 phase one-hot, 5 co-member SR means |
| **Q** | **2** | `temperature_C/100`, `duration_min/60` |
| Y | 12 | vitc/lycopene route one-hot ×5, retention ×2 |

**Q is 2 of 51 dims.** Present in `S_t` but absent from the vector: thermal dose, cumulative dose, hot-aqueous and hot-fat minutes, medium, lid state, piece size, matrix class, start mode, moisture cap, oxygen proxy, prior salt/acid exposure. So the vector's notion of "time" is ordinal position plus raw stated duration — not dose and not accumulated history.

The fix needs no new mechanism: V0's mask design already makes an unfilled dim an explicit UNKNOWN (mask 0), distinct from a known zero. Dims are added **by name only**, weights stay fixed and documented. `learned compatibility` and `new learned state encoder` are both on the do-not-build list, so the vector stays hand-specified.

Recommended Q additions, in impact order, all from producers that already exist: `cumulative_thermal_dose_min`, `hot_aqueous_minutes`, `hot_fat_minutes`, `medium` (one-hot), `lid_state`, `piece_size_class`, `start_mode`. That is state already computed and merely not exposed — the cheapest coverage gain available before freeze.

## 5. Compatibility axes — canonical 13 vs implemented 9

Registry created 15 Nov: **`registry/rag/compatibility_axes_v1.csv`** (the spec file §N.7 referenced but which did not exist). It merges SSOT §241.3 (10 axes), MP AO2 (12 axes) and the repo's 9, keeping categorical match types.

`src/culinarystate/retrieval/compatibility.py` implements exactly **9**: `matrix, state, process, time, temperature, medium, target, basis, tier`.

**Missing 4, now present in the schema as UNKNOWN with a reason:**

| # | Axis | Why absent | Unblocked by |
|---|---|---|---|
| 7 | pH | no sourced pH table | CHEM-D08–D10 verification (freeze step 8) |
| 8 | aw / moisture | no producer | post-submission |
| 9 | geometry / size | `piece_size_class` exists at 9.7% but is not wired to compatibility | wiring only |
| 12 | measurement method / platform | MEAS has 3 rows, PE method null | data |

Axis rules carried into the registry unchanged: hard exclusion from DIRECT on axes 1 / 3 / 10 / 11; UNKNOWN is neutral but never silent (listed in KNOWN UNKNOWNS, lowers D3); censoring compared as intervals with no midpoints and no clipping; no cross-basis pooling except through a deterministic DRV record; bracketing on axes 4 / 5 / 7 / 8 requires ≥2 measured levels from the same study with the query strictly between.

**Directive compliance:** the schema now carries all 13 axes, not salt/acid/lipid. Axes 7, 8, 9, 12 remain UNKNOWN rather than being dropped, which is what lets the compiler select question-relevant axes before retrieval instead of assuming a fixed triple.

## 6. Ranked gaps before 21 Nov

1. **Expose existing Q state in the vector** (§4). No new data, no new producer, no learning. Largest coverage gain per unit effort.
2. **Wire axis 9 (geometry)** to compatibility — `piece_size_class` already exists.
3. **pH band per member** via verified CHEM-D08–D10 (freeze step 8, a MUST, needs Kush/Parv verification per record).
4. **Wire the molecule set (IMAP)** for flavour questions — 313 ING present, unwired. CAN, cut if late.
5. `water:food ratio` — L1 slot exists, unbound.
6. Enzyme state, aw/moisture — need mechanism sources, post-submission.
7. Mass fractions — **DEFER**, 0.6% groundable by census.

## 7. Honest limitations to carry into the report

- **lineage vNext is DIAGNOSTIC.** It changed 29.3% of recipes and completed over 611,902 recipes with 0 exceptions, but **no gold regression set exists**. Aggregate behaviour is consistent with the intended corrections; that is the whole claim. It is not "clean" and not validated.
- `STATE_VECTOR_V0` weights are fixed and unvalidated; the vector is retrieval-only and never decides.
- Markers and SR matches are AI-drafted or AI-delegated (D-085), not human-verified. The salt/acid AI check FAILED (D-128).
- Fill rates are heat-row rates, not whole-corpus rates; a 53.8% medium fill is not 53.8% of all events.
- SSOT v16 is PROPOSED_ONLY. No row here licenses treating a v16 CR as applied.
