# CulinaryState — state-variable inventory and gap matrix (14 Nov 2026)

The schema is broad and the observed state is sparse: UNKNOWN with a reason is a valid cell. Sources:
- SSOT v15 inventory (`reports/h_state/ssot15_state_program_inventory.md`, 10-level hierarchy, B03–B14)
- SSOT v16 change set CR-25/26 (`docs/SSOT/ssot_v16_change_set_DRAFT.md`)
- the mechanism audit's 13-axis compatibility space
- State v2 (`src/culinarystate/composition/state_full.py`)

Fill rates are the full-corpus heat-row rates from `reports/s179/state_dataset_fill_full_2026-11-14.json` where they exist.

**SSOT mapping:** State v2 is the first implementation of SSOT **B12 "process-conditioned representation z_{i,t}"**, which the v15 inventory lists as MISSING. It is explicit and per (food, step), and the named masked vector `STATE_VECTOR_V0` is derived from it (DIAGNOSTIC_RETRIEVAL_ONLY; weights not validated).

| Variable | Layer | In SSOT | Producer now (State v2 field) | Basis | Corpus fill | RAG use | Before 21 Nov |
|---|---|---|---|---|---|---|---|
| food identity / lot / lineage | G | yes (L4, B11) | lot_members, history | RUNG_A | all events | yes | ✅ have |
| merge / split / transfer | G | yes (B11) | event_kind | RUNG_A | all events | yes | ✅ have (vNext fixes B/C pending) |
| process / family | G/Q | yes (L3, B05) | process, family | RUNG_A + PROC | all events | yes | ✅ have |
| cell integrity (intact / cut / crushed) | G | yes (audit) | cell_integrity | CUT_HISTORY | derived per step | yes (leaching, enzymes) | ✅ new today |
| piece size / geometry | G/Q | yes (L1) | piece_size_class | L1 CUT_HISTORY | 9.7% | yes | ✅ have |
| quantity / mass | G/C | yes (B10, CR-26) | — | — | 0.6% of recipes fully groundable (census) | for fractions | ❌ DEFER (census) |
| salt / acid / lipid / water contact | C | yes (D-116) | *_present, contact_phase | markers v2 + SR | see D116 reports | yes | ✅ have (salt/acid AI-check FAIL, D-128) |
| co-member + own composition (fat, water, Na, protein, sugars) | C | yes (L5) | member_composition, own_composition | USDA SR | 793 ING | yes | ✅ have |
| prior salt / acid exposure | C/history | yes (audit) | salt/acid_exposure_before | LINEAGE_C_T | derived | yes | ✅ new today |
| pH (tissue vs medium) | C | yes (audit) | lot_acidity_band = UNKNOWN | — | 0% | yes | ❌ schema only; member pH bands need verified CHEM-D08–D10 |
| water activity / moisture | C/Q | yes | — | — | 0% | mechanism-specific | ❌ schema only |
| molecule set (aroma / taste) | C | yes (L6, IMAP 30,294) | not wired | IMAP / MOL | 313 ING | flavour questions | ⚪ CAN (exists, not wired) |
| medium | Q | yes | medium | L1 PROCESS_DEFINITION / TEXT | 53.8% | yes | ✅ have |
| temperature (bath / food) | Q | yes | temperature_C, food_T_typical_C | L1 + L2 SCENARIO | 16.5% stated; 46.4% scenario | yes | ✅ have |
| duration | Q | yes | duration_min | L1 TEXT_STATED | 28.2% | yes | ✅ have |
| lid / covered | Q | yes | lid_state | L1 | 8.8% | situational | ✅ have |
| oxygen exposure | Q/Y | yes (audit) | oxygen_exposure_proxy | LID_STATE_PROXY | ≈ lid rate | vitamin C, lipid oxidation | ✅ proxy only |
| start mode (cold / boiling) | Q | yes | start_mode | L1 | low | leaching | ✅ have |
| thermal dose (step / cumulative) | Q/history | yes (audit) | thermal_dose_typical_min, cumulative_thermal_dose_min | L2 SCENARIO | where L2 computed | yes | ✅ new today |
| hot-aqueous / hot-fat minutes | Q/history | yes (leaching) | hot_aqueous_minutes, hot_fat_minutes | SUM_TEXT_STATED | duration-limited | leaching / uptake | ✅ new today |
| water:food ratio | Q | yes (L1 water_ratio) | water_ratio = NOT_BOUND_V0 | — | 0% | leaching | ❌ schema only |
| core vs surface temperature | Q | yes (L2 zones) | volume-average dose only | L2 | partial | later | ⚪ partial |
| moisture cap | Q | yes | moisture_cap_C | L2 SCENARIO | where L2 computed | yes | ✅ have |
| analyte route + evidence | Y | yes (B06, D4) | *_route, *_evidence, *_compat | router + D-122 | all heat items | yes | ✅ have |
| vitamin C formula retention | Y | yes (Step 10) | vitc_formula_retention_typical | FORMULA_RESEARCH_ONLY | 826 events | scenario only | ✅ have (domain-limited) |
| enzyme activity state | Y | yes (audit) | — | — | 0% | garlic / PPO | ❌ schema only |
| browning / gelatinisation / texture / colour | Y | yes | — | — | 0% | later | ❌ schema only |
| bioaccessibility (≠ content) | Y | yes (CHEM-D03/04) | — | literature, unverified | — | lycopene + oil | ⚪ after verification, SCENARIO |
| provenance / UNKNOWN reason | P | yes (CR-02) | every cell | — | 100% | yes | ✅ have |

**Ranking of missing dimensions by impact on state-aware retrieval and compatibility:**
1. pH band per member, via a verified sourced table (CHEM-D08–D10), cheap once verified.
2. Wiring the molecule set (IMAP) for flavour questions; data exists.
3. water:food ratio (L1 slot exists, unbound).
4. Enzyme state and moisture/aw: need mechanism sources; post-submission.
5. Mass fractions: deferred by the census (0.6% groundable).
