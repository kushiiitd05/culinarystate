# Step 21 — Mechanism and effect ontology v1 (draft): mechanism classes, effect classes, activation conditions, three-valued applicability

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 under D-027 / Plan v2 §7 and **R-10** (Step 21 may run in parallel with Phases C / D where its input artifacts already exist): contract and documentation work only. Nothing is approved, frozen, signed, minted or applied. No ledger row exists or was created, no evidence was entered, no pipeline was run, no existing file was edited. **Step 08 is not started and not authorised.** Every row of the three vocabulary CSVs carries `registry_status = DRAFT_PENDING_H4`.

Authority: R-10 (parallel lane), **R-15** (APPLICABLE / NOT_APPLICABLE / UNKNOWN; UNKNOWN never silently becomes SIMULATE), **R-14** (ascorbic acid leading, chlorophyll fallback, neither frozen), R-02 (needs are additive v1.1 contracts), R-05 (Step-07 gate is SOFT for 21: no COND value is consumed here), R-18 (no runtime change), R-19 (negative results and rejected items are kept), R-20 (UNKNOWN ≠ 0; recipes ≠ chemistry truth; simulation ≠ measured evidence; an LLM's knowledge is never evidence, SSOT §257A.5).

Files (all new): this document, `registry/schemas/MECH.draft_v1.schema.json`, `registry/mechanism_seed_roster_draft_v1.csv`, `registry/effect_type_registry_draft_v1.csv`, `registry/condition_gate_type_registry_draft_v1.csv`, `reports/step21/README.md` (index, human-decision checklist, proposed contract test). Referenced, not duplicated: `reports/step04/lineage_contract_v1_1.md` (entity chain, lineage keys, leakage rules), `reports/step04/kinetic_trajectory_contract_v1.md` (KIN / KINPT: `compartment`, `analyte_form`, process clock `PROCESS_TAU`, K-level, author-reported fits, R04-4).

Research basis: `reports/master_plan/working_notes/research/r_mechanism_registry.md` (F4.1, F5.1–F5.4, F6.1), `r_simulator_vv.md` (Q1, §3.2, §4 item 7), Audit v2 Part J1 (`reports/master_plan/master_plan_research_audit_v2.md` L10369–10520), SSOT §144.1–144.3 (L8976–9002), §199.6 (L16173–16183), §210.13–210.22, §210.26 (L18838–19071), §213.11, §213.20, §213.29 (L20775, L20926, L21024), §241.3 (L26339–26347), §257A.6 (L28124–28148); plan Step 21 card (L852), Steps 22–25 cards (L873–995), Step 23-M (L915–941).

---

## 0. What this is, and what it is not

**It is** the contract for what a mechanism entry must be able to say (schema), the controlled vocabularies around it (mechanism kind and family, effect type, gate type), the rules for representing when a mechanism can act, and a coverage mapping of the two candidate simulator systems onto those vocabularies.

**It is not** any MECH entry, any gate limit, any rate or kinetic parameter (those are FORM / PARAM, Step 24, gate G21.8), the Step-23 engine, the PROC → MECH crosswalk (21d, which executes HV-010 and is human work), the xref table (21e, which needs external look-ups and human verification), the review packet, the sealed case set, or a test file.

**Why this is parallel-safe (R-10).** The plan card lists the inputs as existing: `PROC` and `SVAR` ledgers, the 40-variable condition registry, `RXN.schema.json`, the ES-1.2 priority cells PC-01…PC-16, SSOT §144.1. Nothing here reads a COND value (R-05 is SOFT for 21) or needs new data. The substeps drafted: **21a** (schema), the *vocabulary part* of **21b** (a seed roster of candidate entries, without entries), **21c** (effect-type registry), and the condition-gate-type registry. Substeps **not** drafted and why: 21b entries (each needs ≥ 1 evidence id with document type and a dual blind review, G21.4 / G21.6), 21d (HV-010, owned by Parv with Kush reviewing, `registry/human_verification_queue.csv`), 21e (collision audit needs live look-ups and a human).

---

## 1. Where Step 21 sits in the decision chain

Step 23-M gates, and what each reads from a MECH record:

| Gate (owner) | Question | Reads from MECH |
|---|---|---|
| G3 candidate effects (22) | which mechanisms, acting on which targets, in which directions | `affected_targets[]` (Step 22 reuses this object as `candidate_effects[]`; identical shape is a check Step 22a should add) |
| G4 mechanism applicability (23) | preconditions ∧ NECESSARY gates ∧ no inhibitor, three-valued | `preconditions[]`, `condition_gates[]`, `inhibitors_mitigators[]`, `history_dependence[]`, `matrix_scope`, `gates_unknown`, `review_status` |
| G5 competing mechanisms (23) | ≥ 2 mechanisms APPLICABLE or UNKNOWN on one target with no joint FORM | `competes_with[]`, `consecutive_with[]` |
| G6–G8 (24, 25, 23) | formula, inputs, parameters, domain | nothing: no formula, no parameter lives in MECH |
| G0, G1, G2, G9 | evidence pre-check, event resolution, deterministic change, route | nothing |

Step 22 derives its `required_state_inputs` and `required_condition_axes` as the union of the states named in `preconditions`, the CV axes (with location) of `condition_gates`, and `history_dependence`; no extra field is needed to list missing inputs.

**Plane (proposal, H4).** A MECH record is knowledge about mechanisms with citations, not an observation. It is proposed as a reference registry of the model plane (P-MOD, `registry/` data-plane rules in `reports/step04/04_6_min_data_plane_rules.md` §1) with `is_evidence = false` fixed by the schema, like EFFSIG and APPDEC (CHG-21-3). The 04.6-min draft has no row for MECH; one would have to be added.

**Ownership boundaries.**

| Object | Owner | Used here as |
|---|---|---|
| History states (`enzyme_activity_state`, `cell_integrity`, `time_since_disruption`, thermal dose, `oxygen_exposure`) | 16a (CHG-21-3, CHG-16-7), additive SVAR v1.1, H4 | `state_ref.ref_status = PROPOSED_KEY`; names only |
| Condition axes | Step 07 registry `registry/condition_variable_registry_v1.csv` (CV-001…040) | `cv_id`; canonical unit |
| Relation verbs | `ledgers/schemas/RXN.schema.json` | alignment of `effect_type` |
| Analyte form, compartment, process clock | 04.3 (KIN) | same vocabularies on `affected_target`, `condition_gate` |
| Rate laws, parameters, domain | 24 / 25 | **absent by design** |
| Applicability verdicts, reason codes, routes | 23 (APPDEC) | **absent by design**; only `missing_input_verdict = UNKNOWN` constants |

---

## 2. Mechanism classes (vocabulary layers)

A mechanism entry has three coordinates before any condition is stated: **kind** (what sort of process), **family** (which SSOT §144.1 group it belongs to), **mechanism_key** (the entry itself).

### 2.1 Kind (7 values; 6 from the card plus one proposed)

| kind | Meaning | Seed examples (roster) |
|---|---|---|
| `CHEMICAL_REACTION` | non-enzymatic reaction | Maillard–Strecker (lumped), caramelisation, acrylamide formation, lipid oxidation, ascorbic-acid aerobic / anaerobic pathways, chlorophyll → pheophytin |
| `ENZYMATIC` | enzyme-catalysed; **requires** an `enzyme` object (EC / GO MF / Rhea xrefs) | alliinase, onion LFS, myrosinase, PPO browning, LOX / HPL, ascorbate-oxidase loss |
| `PHYSICAL_TRANSPORT` | material moves between compartments | leaching, volatilisation, moisture loss, oil uptake |
| `PHASE_STRUCTURAL_TRANSITION` | structure or phase changes | protein denaturation / aggregation, collagen solubilisation, starch gelatinisation / retrogradation, cell-wall softening |
| `MICROBIAL` | organism-driven | lactic fermentation |
| `MECHANICAL_DISRUPTION` | force changes cell integrity | cell disruption by cutting / crushing (proposed entry) |
| `UNRESOLVED_SINK` (**proposed, H4**) | explicit accounting bucket for unexplained loss (SSOT §213.20); no participants, enzyme, gates or targets | `UNRESOLVED_LOSS` |

The card's six kinds come from the Step 21 Method field. The seventh exists because `MECH-UNRESOLVED_LOSS` (a card-listed seed) is not a mechanism of any of the six kinds: SSOT §213.20 asks for "an explicit unresolved sink rather than arbitrary hidden messages", labelled "unresolved / unmeasured, not a discovered molecule". The schema pins the sink down: family `UNRESOLVED`, `edge_semantics = NOT_APPLICABLE`, `gates_unknown = true`, and every list empty. It may be used in mass-balance accounting only; EFFSIG must not emit it as a candidate effect (a rule for Steps 22 / 23 to adopt, H4).

### 2.2 Family (12 values; ten are the SSOT §144.1 families)

| family token | SSOT §144.1 wording | Roster entries |
|---|---|---|
| `MAILLARD_GLYCATION` | Maillard / glycation | Maillard–Strecker (lumped), acrylamide formation |
| `SUGAR_THERMAL_DEGRADATION` | sugar thermal degradation / caramelisation | caramelisation |
| `LIPID_OXIDATION_DECOMPOSITION` | lipid oxidation / decomposition | lipid oxidation |
| `PROTEIN_STRUCTURAL` | protein unfolding, aggregation and gelation | protein denaturation / aggregation |
| `COLLAGEN_TRANSITION` | collagen denaturation / solubilisation | collagen solubilisation |
| `STARCH_TRANSITION` | starch gelatinisation / pasting / retrogradation | gelatinisation, retrogradation |
| `CUTTING_TRIGGERED_ENZYMATIC` | cutting-triggered alliinase, LOX / HPL, myrosinase and PPO chemistry | five enzymatic entries, cell disruption |
| `FERMENTATION` | fermentation | lactic fermentation |
| `VOLATILE_MATERIAL_TRANSFER` | volatile / material transfer | leaching, volatilisation, moisture loss, oil uptake |
| `PIGMENT_CELLWALL_TRANSITION` | pigment / cell-wall transitions | chlorophyll → pheophytin, cell-wall softening, (optional) pyropheophytin |
| `MICRONUTRIENT_DEGRADATION` | *(not a §144.1 family)* | three ascorbic-acid pathways |
| `UNRESOLVED` | *(not a §144.1 family)* | sink |

Two additions: `MICRONUTRIENT_DEGRADATION` because the card lists ascorbic-acid pathways that none of the ten families names, and `UNRESOLVED` for the sink. **Gap found:** G21.2 requires every §144.1 family to have an entry, but the card's 21b list covers only the pigment half of "pigment / cell-wall transitions" (chlorophyll). The roster therefore proposes `CELL_WALL_SOFTENING`; without it G21.2 cannot pass.

### 2.3 Edge semantics

Card values `REACTION`, `TRANSPORT`, `EQUILIBRIUM`, `STATISTICAL` (SSOT §213.11: an edge must mean a known reaction, transport / exchange, equilibrium / interaction, or a validated statistical interaction labelled as such). Phase / structural transitions and mechanical disruption fit none cleanly, so the draft adds `STATE_TRANSITION`, and `NOT_APPLICABLE` for the sink (H4: accept, or collapse into the four). The roster's proposed values: REACTION 15, STATE_TRANSITION 6, TRANSPORT 4, NOT_APPLICABLE 1.

### 2.4 Identity: `mechanism_key`

`mechanism_key` (`^[A-Z][A-Z0-9_]{2,63}$`) is the mint key and the stable human-readable name; ids `MECH-######` are minted from it idempotently, a rename is a new entry, and entries refer to each other by key because the partner may not have an id yet (H4). `PROC.mechanism_families` labels (23 distinct, AI-drafted, 156 / 156 PROC UNVERIFIED) are **not** keys: one label can span several mechanisms (`cell_rupture_enzymatic_reactions` spans six roster entries) and several mechanisms have no label (§8). The card writes the sink id as `MECH-UNRESOLVED_LOSS`, which does not fit the six-digit id pattern; here its key is `UNRESOLVED_LOSS` and its id is minted like any other (H4).

---

## 3. Effect classes

### 3.1 What an effect is

An **effect** is stated on a *target*, not on the mechanism: `affected_target = {target_key, target (state_ref), analyte_form, compartment, effect_type, allowed_directions, trajectory_shape, evidence_ids, status}`. It says what the mechanism can do to that variable and in which direction. It never says how much or how fast: no magnitude, extent, rate, order, half-life or temperature coefficient exists anywhere in the schema (G21.8; the scan list is in the README test).

### 3.2 Target classes

| class | Examples | Admitted effect types |
|---|---|---|
| `SPECIES` | an analyte's amount or concentration | FORMED, DEGRADED, CONSUMED, OXIDIZED, REDUCED, ISOMERIZED, FERMENTED, UNKNOWN_TRANSFORMATION |
| `TRANSFERRED_AMOUNT` | an amount in one compartment of a transfer | LEACHED, VOLATILIZED, ABSORBED |
| `OBSERVABLE` | colour, browning index, texture, force | STRUCTURE_ALTERED, DENATURED, AGGREGATED, GELATINIZED, UNKNOWN_TRANSFORMATION (when species are not asserted) |
| `STATE` | `cell_integrity`, `enzyme_activity_state` | STATE_SET |

`target_class` is a column of the effect-type registry, a guide for reviewers, not a schema field. An observable target (e.g. PPO browning acting on colour) uses `UNKNOWN_TRANSFORMATION` or `STRUCTURE_ALTERED` rather than an invented species.

### 3.3 Effect types (16; `registry/effect_type_registry_draft_v1.csv`)

Aligned to `RXN.schema.json` relation verbs (13 reused verbatim) plus three proposed additions:

| effect_type | Origin | Direction rule (schema-enforced where stated) |
|---|---|---|
| FORMED | RXN | contains INCREASE (also DECREASE only for peak-then-decline or condition-dependent direction, evidence required) — *enforced: must contain INCREASE or be exactly [UNKNOWN]* |
| DEGRADED, CONSUMED | RXN | DECREASE only — *enforced* |
| OXIDIZED, REDUCED, ISOMERIZED | RXN | no fixed direction; state `analyte_form` |
| LEACHED, VOLATILIZED | RXN | by compartment: TISSUE → DECREASE, COOKING_MEDIUM → INCREASE — *enforced*; LEACHED excludes WHOLE_SYSTEM (a transfer conserves the system) — *enforced* |
| DENATURED, AGGREGATED, GELATINIZED, FERMENTED | RXN | no fixed direction |
| UNKNOWN_TRANSFORMATION | RXN | any (the honest type when species are not asserted; MP W6 "never manufacture a balanced reaction") |
| ABSORBED | **proposed** | inward transfer (oil uptake, water uptake): TISSUE → INCREASE, COOKING_MEDIUM → DECREASE — *enforced* |
| STRUCTURE_ALTERED | **proposed** | texture / structure without specified chemistry (cell-wall softening, collagen solubilisation) |
| STATE_SET | **proposed** | sets a non-analyte history state; may belong to Step-18 operators instead (H4) |

`RETAINED` is the one RXN verb with no effect type: it is an outcome (EVD direction NO_CHANGE), not something a mechanism does. The README test asserts that every RXN verb except RETAINED has exactly one effect type.

### 3.4 Directions, and alignment with EVD `derived.direction`

`allowed_directions` ⊆ {INCREASE, DECREASE}, non-empty, **or exactly `[UNKNOWN]`**. `trajectory_shape` ∈ {MONOTONIC, PEAK_THEN_DECLINE, UNKNOWN} records that "products can peak and decline" (SSOT §144.1 frozen caution; §210.17). EVD's `derived.direction` ∈ {INCREASE, DECREASE, NO_CHANGE, MIXED, UNKNOWN} holds *observed outcomes*, so the vocabularies are related, not identical:

| Observed EVD direction | Reading against a MECH target (for Steps 22 / 23 comparisons) |
|---|---|
| INCREASE / DECREASE | consistent iff that direction is in `allowed_directions` |
| MIXED | consistent iff the set has both directions or `trajectory_shape = PEAK_THEN_DECLINE`; otherwise a **conflict flag** for review |
| NO_CHANGE | contradicts nothing: a mechanism can be applicable and offset by a competitor, or act below detection |
| UNKNOWN | no information |

An observed direction outside the allowed set is evidence about the matrix or the entry; it raises a flag and is never an automatic deletion (R-19).

### 3.5 Rules

- **E-1** Effects attach to targets; a mechanism with no target is invalid, except the sink, which has none (schema).
- **E-2** No magnitude, rate or extent of any kind (G21.8).
- **E-3** A marker is not an effect and not an identifier (§4.8).
- **E-4** Endpoint cues ("until golden") are outcomes or stop criteria, never conditions or effects (SSOT §199.8, Step 22).
- **E-5** An observable is not a species: do not manufacture the species (UNKNOWN_TRANSFORMATION).
- **E-6** Open: evaporation versus exudate / drip for moisture loss is not separated by the current types (H4).

---

## 4. Activation conditions: how a mechanism says when it can act

### 4.1 Elements and where they live

| What (the request) | Representation | UNKNOWN handling | Anchor |
|---|---|---|---|
| Temperature | gate on CV-005…008 (setpoint, medium, surface, core); the CV id *is* the location | no value, no location match → UNKNOWN | CV registry notes; 04.3 R04-6 (COND ML-001…006); MP W2 "oven setpoint ≠ core T" |
| pH | gate on CV-013 with `location` TISSUE / MEDIUM (never averaged) | pH UNKNOWN → UNKNOWN | CV-013 note; MP L82 |
| Water activity, moisture | gates on CV-015, CV-016 (CV-016 needs `basis` WET / DRY); moisture gating only where evidenced | absent is UNKNOWN, not 0 | SSOT §210.15 |
| Oxygen | gate on CV-021 (`location` HEADSPACE / MEDIUM …) and history `oxygen_exposure` | absent is UNKNOWN, not 0 | CV-021 note; J1.2.1 |
| Time | gate on CV-001…003 with clock `PROCESS_TAU` only; time since an event is a history item | unknown clock or value → UNKNOWN | 04.3 R04-5; 03.3 pending |
| Substrate | precondition over a per-substance state (`subject_entity`) | state UNKNOWN → UNKNOWN | SVAR-FUT-014 |
| Enzyme state | precondition on `enzyme_activity_state`; the entry's `enzyme` object holds EC / GO MF / Rhea xrefs | UNKNOWN → UNKNOWN | J1.2.1; GO MF probes (F4.1) |
| History | `history_dependence[]` (names owned by 16a) | UNKNOWN → UNKNOWN | SSOT §198.4, §210.13 |
| Inhibitors, mitigators | `inhibitors_mitigators[]` (§4.4) | not formalised → entry UNKNOWN | F5.4(iii) |
| Competing / consecutive mechanisms | `competes_with[]`, `consecutive_with[]` (§4.5) | none declared is **not** "none exist" (§4.5) | SSOT §210.17–210.18, §210.21 |
| Matrix scope | `matrix_scope` per entry and per gate (§4.7) | unlisted matrix → UNKNOWN | F5.3 |
| Markers | `markers[]` with `marker_unique` fixed `false` | — | SSOT §144.1 frozen caution |
| Unexplained loss | the sink entry | — | SSOT §213.20 |

### 4.2 Preconditions

`{precondition_key, state_ref, subject_entity, predicate, missing_input_verdict, evidence_ids, status}`. A predicate is **categorical** (`IS`, `IS_NOT`, `IN`, `NOT_IN`, `PRESENT`, `ABSENT` over string values); numeric conditions are gates. `UNKNOWN` is not an admissible satisfying value (a state that is UNKNOWN makes the precondition UNKNOWN whatever the predicate says). `state_ref` is an SVAR id (`SVAR_ACTIVE`), an `SVAR-FUT-###` registry row (`SVAR_FUTURE`) or a `PROPOSED_KEY` that no registry holds yet; a proposed key is a request to the SVAR owner, never a minted id.

### 4.3 Condition gates

`{gate_key, gate_type, cv_id, location, basis, clock, domain_kind, interval | categories, modulates, independence_assumed, matrix_scope, missing_input_verdict, evidence_ids, status, rationale_raw}`. Types (`registry/condition_gate_type_registry_draft_v1.csv`): **NECESSARY** (outside the evidenced window the mechanism does not act), **MODULATING** (changes direction / selectivity / rate, never the verdict), **INHIBITING** (inside the window the mechanism is blocked).

Axis rules enforced by the schema:

| CV ids | Rule |
|---|---|
| CV-005 setpoint, CV-006 medium, CV-007 surface, CV-008 core | `location = NOT_APPLICABLE` (the id carries it; no second field to disagree). CV-005 stays a setpoint, never product temperature |
| CV-009 temperature unspecified; CV-004, CV-010 trajectory axes | **never gate axes** (an unspecified location is never promoted; a gate needs a scalar or interval input, and trajectory dependence is a history item) |
| CV-013 pH, CV-015 aw, CV-016 moisture, CV-021 oxygen | `location` must be stated (TISSUE, MEDIUM, HEADSPACE, WHOLE_ENTITY) or be `UNKNOWN`; CV-016 additionally needs `basis` WET_BASIS / DRY_BASIS (or UNKNOWN) |
| CV-001…003 time | `clock = PROCESS_TAU` (the only clock admitted until 03.3 is approved, as in 04.3); every other axis has `clock = NOT_APPLICABLE` |
| every other CV | `basis = NOT_APPLICABLE`, `clock = NOT_APPLICABLE` |

Checks that need the CV registry (id exists, `unit` equals the CV canonical unit, domain kind agrees with the CV dimension, categorical vs numeric) are semantic-validator work and are exercised in the README test with the real registry file.

**Interval bounds are never a bare null.** The card writes "interval min / opt / max (nullable)". A bare null can be read as "unbounded", which is an imputation. Each bound therefore carries a status:

| Bound status | Meaning | Query value inside the limit | Beyond the limit | No query value |
|---|---|---|---|---|
| `STATED` (value, inclusive) | the cited evidence gives this limit | APPLICABLE | NOT_APPLICABLE | UNKNOWN |
| `OPEN_STATED` | the evidence states activity is not limited on this side within the studied range | APPLICABLE | — | UNKNOWN |
| `NOT_REPORTED` | the evidence is silent | UNKNOWN | UNKNOWN | UNKNOWN |

A NECESSARY gate's verdict is the Kleene conjunction of its two sides (a certain violation on either side gives NOT_APPLICABLE; otherwise any UNKNOWN gives UNKNOWN). `opt` is an annotation (`STATED` or `NOT_REPORTED` only), never a verdict input. Any `STATED` bound requires `evidence_ids`; an ACCEPTED gate needs evidence, a known `location`, and a known `basis`. This is a **deviation from the card's wording** (nullable → status object) and is H4 item D21-6.

`independence_assumed` ∈ {ASSUMED_INDEPENDENT, INTERACTION_REPORTED, UNKNOWN} (not a boolean, so "not assessed" cannot be coded as false): the cardinal-parameter pattern (Rosso et al. 1995) assumes independent axes; the registry records that assumption and does not exploit it (interaction terms are FORM matters).

**Seeds carry no gates.** No window is drafted in this step: gates come from reviewed evidence (21b), and until then the entry says `gates_unknown = true`. Today's evidence could not populate gates anyway: pH, moisture and aw are UNKNOWN in all 4,414 conditions and only 213 temperatures have a stated location (r_mechanism_registry §0; Step 23 card), and K0 aggregates (USDA R6, Bognár) have no time or temperature to bound a window (R04-4 spirit). Gate evidence will come from Steps 10–14 (HV-002 "mechanism evidence verification").

### 4.4 Inhibitors and mitigators

`{inhibitor_key, role INHIBITOR | MITIGATOR, agent_or_condition_raw, sbo_role (SBO:0000020 inhibitor | SBO:0000019 modifier), extent COMPLETE | PARTIAL | UNKNOWN, evaluated_via, ...}`. To avoid describing one fact twice, an inhibitor is **evaluated through exactly one route**: `GATE` (an INHIBITING gate of the same entry), `STATE_PREDICATE` (inline state + predicate, e.g. an enzyme state set by blanching), or `NOT_EVALUABLE_YET` (documented but not formalised). The last contributes UNKNOWN and **forces `gates_unknown = true`** on the entry (schema): a known but unformalised inhibitor means the entry cannot honestly be called APPLICABLE. `extent`: COMPLETE → NOT_APPLICABLE when present; PARTIAL → the "downgrade to QUALITATIVE" case that Step 23 owns; UNKNOWN → UNKNOWN (proposed reading, D21-11). Mitigations named in the sources (MP I3: chilling, knife sharpness, ventilation, acid, blanching; ES-1.2 PC-06: antioxidant / acid) are candidates for this list, each to be evidenced in review.

### 4.5 Competing and consecutive mechanisms

`competes_with[] = {mechanism_key, shared_target, relation, ...}` with relation ∈ {PARALLEL_PATHWAY (SSOT §210.18), SUBSTRATE_COMPETITION, TRANSPORT_VS_REACTION (degradation vs leaching, §210.21), LUMPED_OVERLAP (a lumped and a specific entry covering the same chemistry, e.g. Maillard–Strecker lumped vs acrylamide formation), UNKNOWN}. `consecutive_with[] = {mechanism_key, order, shared_species}` (§210.17: an intermediate rises, peaks, falls). Both must be declared **on both entries** (the converse order on the partner); a one-sided declaration could hide a competitor from the Step-23 G5 gate, so the symmetric closure is a semantic check. "No competitor declared" means "none recorded", not "none exist": until review, competing mechanisms on a target are an open UNKNOWN, which is one reason non-ACCEPTED entries contribute UNKNOWN.

### 4.6 History dependence

`history_dependence[] = {state_ref, role INPUT_REQUIRED | MODULATES_DIRECTION_OR_SELECTIVITY | UNKNOWN}`. Names assumed from r_mechanism_registry F5.4(v), Audit J1.2.1 and CHG-21-3, **owned by 16a** (not defined here):

| Proposed key | Proposed value set (source) | Used for |
|---|---|---|
| `enzyme_activity_state` | ACTIVE, PARTIALLY_INACTIVATED, INACTIVATED, UNKNOWN (F5.4) | enzymatic preconditions; blanching as inhibitor |
| `cell_integrity` | INTACT, CUT, CRUSHED_PUREED, UNKNOWN (F5.4) | cutting-triggered chemistry |
| `time_since_disruption` | process-clock quantity (SSOT §144.3 garlic crush / rest) | rest-time modulation |
| thermal dose | cumulative exposure Ω (§210.13); the reference temperature and Ea are a **Step-24** matter | history input; not stored here |
| `oxygen_exposure` | covered / uncovered / sealed (J1.2.1) | oxidative pathways |
| precursor depletion; prior acid / salt exposure | categorical or quantity, deferred to 16a | substrate and pH history |

### 4.7 Matrix scope

`{scope_kind, included[], excluded[], unlisted_verdict, note_raw}` at entry level and per gate. A matrix in `included` is in scope; in `excluded`, out of scope (the **only** route to NOT_APPLICABLE by matrix); in neither → **UNKNOWN** (the §199.6 REQUIRED / INCOMPATIBLE / UNKNOWN pattern, applied to matrix). `scope_kind`: `MODEL_SYSTEM` (laboratory or model-system evidence, which does not extend to food matrices by itself: van Boekel 2008, Pin 2004 via F5.3), `FOOD_MATRIX_SPECIFIC`, `FOOD_CLASS`, `GENERIC_MECHANISM` (the SSOT §241.3 match type: a retrieval label, **not** an applicability grant), `UNKNOWN`. Matrices are `ING-` ids, FoodOn CURIEs (cross-reference) or class labels.

### 4.8 Markers

`marker_unique` is the schema constant `false`: HMF, colour, pyrazines and hexanal are not unique pathway identifiers (SSOT §144.1 frozen caution), and an effect signature may not infer a mechanism from a marker alone. Admitting a unique marker would be a v1.1 schema change with an H4 decision.

### 4.9 Evidence and sourcing

- `evidence_refs[]` = `{evidence_id (EVD- / SRC- / DOC- / OBS- / KIN-), doc_type PRIMARY | REVIEW_CONTEXT, supports[], locator, lineage_root_id, lineage_status}`. A review gives context only; a numeric limit needs a PRIMARY source; a PRIMARY ref needs a locator.
- `derivation_anchors[]` say *why an entry is on the list* (SSOT section, master-plan line, step card, ES-1.2 cell, PROC label, research note). **An anchor is not evidence**; SSOT, master-plan and plan text never appear as evidence ids.
- `ai_drafted = true` entries stay CANDIDATE; ACCEPTED requires `HUMAN_VERIFIED` (Kush or Parv), dual blind review done or adjudicated, a valid review-provenance check (the 07H v1–v3 provenance failures), ≥ 2 reviewer ids, and ≥ 1 PRIMARY evidence ref.

---

## 5. Three-valued applicability (R-15)

### 5.1 Verdicts live in Step 23, not in MECH

MECH holds no verdict. APPDEC (Step 23) holds, per gate, one of **APPLICABLE / NOT_APPLICABLE / UNKNOWN** (a gate a route does not need is marked NOT_REQUIRED, a structural marker, not a verdict). What MECH owes Step 23 is a representation in which an *absent* input cannot be mistaken for a *satisfied* one.

### 5.2 Rules the representation enforces

| # | Rule | Where it is enforced |
|---|---|---|
| U-1 | UNKNOWN is a value of its own: never 0, never absent, never a default | status vocabularies; `UNKNOWN` tokens on every enumerated field that can be unknown |
| U-2 | No imputation: no field can hold a default, midpoint or "typical" value; qualitative heat is never numeric | `additionalProperties: false` at every object; no `default` keyword anywhere (test) |
| U-3 | A missing, unaudited or partly bracketed input gives UNKNOWN | `missing_input_verdict` is the constant `"UNKNOWN"` on every precondition, gate and inhibitor; bound statuses (§4.3) |
| U-4 | An unlisted matrix or category is UNKNOWN; NOT_APPLICABLE arises only from an explicit exclusion, a violated STATED bound, a false precondition on a *known* state, or a COMPLETE inhibitor present | `unlisted_verdict` constants; bound statuses; `excluded` lists |
| U-5 | An entry or item that is not ACCEPTED, or with `gates_unknown = true`, contributes UNKNOWN; Steps 22–23 consume only ACCEPTED entries | `review_status`, per-item `status`, `gates_unknown` (rule: no gate and no precondition ⇒ `gates_unknown` must be stated true) |
| U-6 | Conjunction is Kleene strong: any NOT_APPLICABLE ⇒ NOT_APPLICABLE; else any UNKNOWN ⇒ UNKNOWN; else APPLICABLE | Step 23 (this draft only fixes what the records must permit) |
| U-7 | MODULATING never changes the verdict | gate-type registry |
| U-8 | UNKNOWN or NOT_APPLICABLE at any of G4–G8 never reaches SIMULATE | route rule and property test belong to Step 23 (G23.2). Step 21's share: no field can turn a missing input into APPLICABLE (test-local reference in the README test, 3,000 randomised entries) |
| U-9 | Before the Step-07 gate has validly passed, a COND-sourced axis value (`condition_trust = UNAUDITED`) enters as UNKNOWN for gating (R-05) | Step 23; MECH consumes no COND value |

### 5.3 Truth tables (representation level)

| Item | True / inside | False / outside | Else |
|---|---|---|---|
| Precondition on a KNOWN state | APPLICABLE | NOT_APPLICABLE | state UNKNOWN or item not ACCEPTED → UNKNOWN |
| NECESSARY gate | inside both limits → APPLICABLE | beyond a STATED limit → NOT_APPLICABLE | NOT_REPORTED side, missing value, location mismatch → UNKNOWN |
| INHIBITING gate / inhibitor | window not met (absent) → APPLICABLE | present and COMPLETE → NOT_APPLICABLE | extent PARTIAL → Step 23 downgrade; extent or presence UNKNOWN → UNKNOWN |
| Matrix | in `included` → APPLICABLE | in `excluded` → NOT_APPLICABLE | unlisted or query matrix unknown → UNKNOWN |
| Entry (G4) | all of the above APPLICABLE and `gates_unknown = false` | any NOT_APPLICABLE | otherwise UNKNOWN |

**Illustration from the repo's own text.** Chlorophyll → pheophytin is "pH-gated"; pH "is usually UNKNOWN in recipes → abstain" (r_simulator_vv §Q1). A NECESSARY pH gate with the tissue pH UNKNOWN therefore yields UNKNOWN, hence no SIMULATE. The card expects ~100% UNKNOWN for pH- and aw-gated mechanisms on current data and calls that correct behaviour and a data-gap signal for Step 14, not an engine failure.

---

## 6. Candidate systems (R-14): mapping without freezing

**Principle.** Ascorbic acid (SIM-AA-1) is the leading candidate, not frozen; chlorophyll (SIM-CHL-1) is the preregistered fallback; the choice is a single DECISIONS entry made once at 11.D from Step 10 / 11 evidence. Nothing in the schema or the vocabularies names either system. The roster column `r14_system_role` (AA_PATHWAY, CHL_PATHWAY, AA_RELATED_GENERIC, NEITHER) is a removable coverage tag; the README test asserts that both systems are represented and that no cell speaks of a selected or chosen system. All AA-specific criteria in later steps are conditional on the 26.0 selection.

### 6.1 Ascorbic-acid pathways (leading candidate)

| mechanism_key | Kind / family | What the entry must be able to express (sources) | Competes / consecutive (to be evidenced) |
|---|---|---|---|
| `ASCORBIC_ACID_AEROBIC_OXIDATION` | CHEMICAL_REACTION / MICRONUTRIENT_DEGRADATION | activation axes named for the AA group: T, O2, pH, metal ions, enzyme state (r_simulator_vv §4 item 7); oxygen exposure; pathway AA → DHA → DKG (r_simulator_vv Q1) | PARALLEL_PATHWAY with the anaerobic pathway and ascorbate-oxidase loss; TRANSPORT_VS_REACTION with LEACHING; consecutive steps via DHA |
| `ASCORBIC_ACID_ANAEROBIC_DEGRADATION` | CHEMICAL_REACTION / MICRONUTRIENT_DEGRADATION | same axis group; oxygen as the expected discriminator, to be evidenced not assumed | as above |
| `ASCORBATE_OXIDASE_LOSS` | ENZYMATIC / MICRONUTRIENT_DEGRADATION | enzyme state and cell integrity (the enzyme is "active before inactivation", Q1); plan Step 26 lists ascorbate-oxidase loss in raw / cut tissue and dry-heat / frying as an example of applicability UNKNOWN or NOT_APPLICABLE | as above |
| `LEACHING` (generic) | PHYSICAL_TRANSPORT / VOLATILE_MATERIAL_TRANSFER | boiling-water transfer; the main confound of the AA candidate (leaching vs destruction, SSOT §144.2, §210.21) | TRANSPORT_VS_REACTION |

Which axis is NECESSARY, MODULATING or INHIBITING for which pathway is exactly what the 21b review must evidence; none is drafted.

### 6.2 Chlorophyll pathways (fallback)

| mechanism_key | Kind / family | What the entry must be able to express | Competes / consecutive |
|---|---|---|---|
| `CHLOROPHYLL_TO_PHEOPHYTIN` | CHEMICAL_REACTION / PIGMENT_CELLWALL_TRANSITION | "pH-gated" (card 21b); temperature; pH is a required input and UNKNOWN pH gives UNKNOWN; tissue pH is not medium pH and is never averaged | consecutive_with the optional pyropheophytin entry |
| `CHLOROPHYLL_PYROPHEOPHYTIN_FORMATION` (optional, beyond the card) | CHEMICAL_REACTION / PIGMENT_CELLWALL_TRANSITION | a pathway beyond pheophytin ("pyropheophytin dominates in heat-processed spinach", secondary source; plan Step 26: beyond the simulator's stated temperature limit) | consecutive |

**Leaching and chlorophyll.** The SIM-CHL-1 text says "no leaching term". That is a Step-26 scope assumption. The MECH registry does **not** assert it: whether LEACHING applies to chlorophyll is UNKNOWN unless an `excluded` target / matrix scope with evidence says otherwise (UNKNOWN ≠ 0).

### 6.3 What the mapping showed (gaps, none fixed here)

| # | Finding | Consequence |
|---|---|---|
| G-1 | The SVAR registry has only "Vitamin C" content variables (SVAR-000009 "total ascorbic acid", SVAR-000215) and **no** species-level variables (reduced AA, DHA) and none for chlorophyll or pheophytin (colour L*a*b* is SVAR-FUT-008, `FUTURE`) | targets use `PROPOSED_KEY` and `analyte_form`; an additive SVAR proposal is needed (16a / H4) |
| G-2 | No condition axis for metal ions (CV-023 `additive_catalyst_enzyme` is categorical; the 40-variable registry has no ion axis) | AA metal-ion gating can only be a categorical CV-023 gate until a CV is added (Step 07 registry v1.1, H4) |
| G-3 | CV-013 pH has no tissue / medium split | handled by the gate's `location` field |
| G-4 | `PROC.mechanism_families` has **no** vitamin or pigment label, so baseline B0 (PROC label lookup) can never propose an AA or chlorophyll mechanism | B0 recall for these cells is zero by construction; B1 (rules) is the only route; report it as such in Step 22 |
| G-5 | The wet-heat PROC used by the candidate systems (boil, simmer, steam, blanch, parboil) have `required_condition_axes` = duration, temperature only; the six PROC with a pH axis are pickle, sterilise, can, dry, pasteurise, brine | PROC axes cannot seed gate axes; gate axes come from the mechanism evidence |
| G-6 | Asymmetry: the card's list gives AA three pathways plus leaching and the chlorophyll fallback one (two with the optional entry) | not corrected: it reflects the card; schema completeness is symmetric, and chlorophyll's pH gate is the case that exercises UNKNOWN handling |
| G-7 | The repo holds 0 EVD rows for chlorophyll / pheophytin (plan Step 10 text) and AA only as K0 vitamin C aggregates | no gate for either system can be evidenced from existing rows |

---

## 7. Seed roster (`registry/mechanism_seed_roster_draft_v1.csv`)

26 rows of **candidate entries to be authored**, not entries: 23 from the card's 21b list (the card's "starch gelatinisation / retrogradation" is split into two, a proposal), 2 proposed additions (`CELL_WALL_SOFTENING`, `CELL_DISRUPTION_DECOMPARTMENTALISATION`), 1 optional (`CHLOROPHYLL_PYROPHEOPHYTIN_FORMATION`). The card's target of about 20–40 entries is PROPOSED_PILOT.

| By kind | n | By role (R-14) | n |
|---|---|---|---|
| CHEMICAL_REACTION | 8 | AA_PATHWAY | 3 |
| ENZYMATIC | 6 | CHL_PATHWAY | 2 |
| PHASE_STRUCTURAL_TRANSITION | 5 | AA_RELATED_GENERIC (leaching) | 1 |
| PHYSICAL_TRANSPORT | 4 | NEITHER | 20 |
| MICROBIAL / MECHANICAL_DISRUPTION / UNRESOLVED_SINK | 1 each | | |

Every row has a source (`source_anchors`: SSOT line ranges, master-plan lines, ES-1.2 cells, the card), a proposed kind / family / edge semantics, the PROC label it corresponds to under baseline B0, typical effect types (from the cited ES-1.2 mechanism text where one exists, else `UNKNOWN_TRANSFORMATION`; **proposed, AI-drafted, for reviewers**), `entry_status = SEED_NOT_YET_AUTHORED` and `ai_drafted = TRUE`. No gate, parameter, evidence id or scientific value is on the roster.

**Open questions raised by the roster** (full list in the README): (a) cutting / crushing as a MECH entry versus a Step-18 deterministic operator on `cell_integrity`; (b) enzyme thermal inactivation (PC-02, and blanching as mitigation) as a STATE_SET entry versus a Step-18 operator; (c) the gelatinisation / retrogradation split; (d) `LOX_HPL_OXIDATION` has no ES-1.2 cell and no repo text on products, so its effect species must be sourced in review.

---

## 8. PROC label coverage (baseline B0) and gaps

Label-level, AI-drafted, **not** the 21d crosswalk (21d is per PROC, all 156, and executes HV-010). Counts are from `ledgers/data/PROC.jsonl` (latest version of each of the 156 PROC; 552 ledger lines are versions; 93 PROC carry `mechanism_families`; 156 / 156 UNVERIFIED).

| PROC label (PROC carrying it) | Roster key(s) | Disposition |
|---|---|---|
| cell_rupture_enzymatic_reactions (22) | ALLIINASE…, ONION_LFS…, MYROSINASE…, PPO…, LOX_HPL…, CELL_DISRUPTION… | one label, six mechanisms: per-PROC decision in HV-010 |
| maillard (21) | MAILLARD_STRECKER_LUMPED | mapped |
| moisture_loss (21) | MOISTURE_LOSS | mapped |
| lipid_oxidation (21) | LIPID_OXIDATION | mapped |
| protein_denaturation (21) | PROTEIN_DENATURATION_AGGREGATION | mapped |
| leaching (14) | LEACHING | mapped |
| starch_gelatinisation (14) | STARCH_GELATINISATION | mapped |
| cell_wall_softening (14) | CELL_WALL_SOFTENING | mapped to a **proposed** entry |
| oil_uptake (12) | OIL_UPTAKE | mapped |
| acrylamide_formation_starchy (12) | ACRYLAMIDE_FORMATION | mapped |
| caramelisation (9) | CARAMELISATION | mapped |
| microbial_fermentation (5) | LACTIC_FERMENTATION | partial (broader than lactic) |
| starch_retrogradation (4) | STARCH_RETROGRADATION | mapped |
| gelation (4) | PROTEIN_DENATURATION_AGGREGATION | weak (SSOT names gelation with protein aggregation) |
| emulsification (14), aeration (14), gluten_development (14) | — | **gap** |
| phase_change (7), crystallisation (4), co2_leavening (5) | — | **gap** |
| water_activity_reduction (6), acidification (6), microbial_inactivation (6) | — | **gap** |

Result: 73 of the 93 labelled PROC carry at least one mapped label; 57 have all of their labels mapped; **20 PROC carry only unmapped labels** (14 with emulsification + aeration + gluten_development; 6 with water_activity_reduction + acidification + microbial_inactivation). The nine unmapped labels are either state or physical operations that Step 18 handles deterministically (aeration, emulsification, phase change, crystallisation), modifiers of other mechanisms (acidification and water-activity reduction change pH / aw, which are gate axes), or outside the card list (gluten network, CO₂ leavening, microbial inactivation, which is safety-adjacent and belongs with authoritative sources, Step 36). Each needs a human disposition: add an entry, declare "not a mechanism", or fold into another (H4, D21-10). The recorded dispositions are a precondition for G21.7 (crosswalk covers 156 / 156).

---

## 9. External cross-references (21e preview; no table drafted)

External ontologies are cross-references only (no OWL backbone, no reasoner; OLS probes found no usable mechanism hierarchy, F4.1). The `xref` object: `{curie, relation (EXACT | BROADER | NARROWER | RELATED | NOT_EQUIVALENT_COLLISION), match_basis (LABEL_MATCH_ONLY | ID_FROM_SOURCE | HUMAN_CURATED | AI_PROPOSED), xref_status (PROPOSED | ACCEPTED | REJECTED), verification_status, verified_by (Kush | Parv), collision_note}`. Namespaces admitted by the CURIE pattern: GO, EC, RHEA, CHEBI, RXNO, MESH, SBO, FOODON, TRANSFORMON. **Label matching is unsafe**: RXNO contains both Strecker degradation (RXNO:0000224, food-aroma sense) and Strecker reaction (RXNO:0000207, amino-acid synthesis). The schema therefore makes an ACCEPTED xref require `HUMAN_VERIFIED` by Kush or Parv, and keeps a recorded collision as `REJECTED` with a note (not deleted, R-19). The fixture V-12 / N-35 / N-36 in the README test encode this canary. The card marks RXNO and SBO term ids and the GO / ChEBI / FoodOn licences as UNVERIFIED: only CURIEs are stored, never ontology text.

---

## 10. Leakage and review rules specific to Step 21

| # | Rule | Enforced by |
|---|---|---|
| L-21-1 | MECH entries may not cite evaluation cases: the sealed Step-22 / 23 case set (22c) uses an id prefix outside `EVD|SRC|DOC|OBS|KIN` | `evidence_id` pattern; 22c to honour; semantic check against the sealed manifest |
| L-21-2 | **Gate circularity (not in the card; proposed).** A gate limit derived from a study must not be tested on cases drawn from that study. Each evidence ref caches its `lineage_root_id` (04.1 key; `LROOT-` is a PROPOSED prefix) so that Steps 23 / 27 can exclude those cases | `evidence_ref.lineage_root_id`, `lineage_status` |
| L-21-3 | The locked-test labels are not produced only by the MECH authors (card; otherwise G23.1 is DIAGNOSTIC_ONLY) | `created_by`, `review.reviewer_ids` |
| L-21-4 | Dual blind review with technical independence safeguards (07H provenance failures); a review with invalid provenance is redone, not counted | `review.review_provenance_valid` |
| L-21-5 | LLM-proposed candidates (E5 / E6) are `ai_drafted`, CANDIDATE, and never ACCEPTED without a human verification against a PRIMARY source | schema rules in §4.9 |
| L-21-6 | Rejected entries, items and xrefs are kept (`REJECTED`, `RETRACTED`), not deleted (R-19) | status vocabularies; append-only ledger rule |

---

## 11. How this draft supports the card's gates G21.1–G21.8

| Gate | Support in this draft | What remains |
|---|---|---|
| G21.1 schema frozen, validator tests green | schema draft + proposed contract test (README); 60 negative controls, 18 accepted variants, mutation-checked | H4 approval; freeze; port to `ledgers/schemas/MECH.schema.json` and `registry.py` (not done: no prefix registered) |
| G21.2 every §144.1 family + leaching, volatilisation, moisture loss ≥ 1 entry | roster covers all ten families and the three transport keys; test asserts it | the entries themselves; the cell-wall gap needs the proposed entry |
| G21.3 ≥ 1 precondition or gate, or `GATES_UNKNOWN` | schema rule | entries |
| G21.4 ≥ 1 evidence id with document type | `evidence_refs`, `doc_type`; required for ACCEPTED | evidence (Steps 10–14, HV-002) |
| G21.5 0 xrefs accepted without human verification; collisions resolved | `xref` rules; Strecker canary | 21e |
| G21.6 dual blind review, adjudication, provenance validity | `review` object and ACCEPTED rules | review packet and the people (expert availability UNVERIFIED) |
| G21.7 crosswalk 156 / 156 | label-level gap list (§8) | 21d / HV-010 |
| G21.8 0 numeric kinetic fields | `additionalProperties: false` everywhere, forbidden-name scan, no numbers except evidenced condition bounds | — |

---

## 12. Not decided here

The PROC → MECH crosswalk; the xref table; any mechanism entry; any gate limit; the route rule and reason codes (Step 23); EFFSIG fields (Step 22); FORM / PARAM / VAL (Step 24); history-state names and SVAR additions (16a); the first-simulator choice (R-14, 11.D); the benchmark and its sealing (22c); the id prefix registration (04.9-min covers other prefixes; `MECH-` is free in `src/culinarystate/ledgers/registry.py`, which lists 37 prefixes); `tests/` content.

Open decisions for Kush and Parv are collected in `reports/step21/README.md`, section 4 (D21-1 … D21-18).
