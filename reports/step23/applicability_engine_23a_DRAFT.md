# Steps 22a and 23a: process signatures and the applicability engine (S158 drafts)

**Status: 22a DRAFT_PENDING_21b_H4; 23a DRAFT_PENDING_21b_22a_H4.** Written 2026-11-03 in session S158 by the AI
worker "prv" (an agent, not Parv). AI draft under D-045: Kush and Parv review it. Nothing is approved, sealed,
signed, minted or written to a ledger. Every test uses SYNTHETIC placeholders (`SYNTH_*`, `PROC-SYN*`, dummy bounds).
No real process-to-mechanism rule, case, label or threshold exists. 23b stays BLOCKED (07.A, 15b).

## 1. Files

| Path | What |
|---|---|
| `src/culinarystate/mechanism/process_signatures.py` | 22a: PROC hierarchy reader, `SignatureRule`, `ProcessSignature`, builder, validator, matcher, firewall counters |
| `src/culinarystate/mechanism/case_seal.py` | 22c sealing helper: hash commitment, human-only sealers, rule-cites-test-case check (helper only) |
| `src/culinarystate/mechanism/applicability.py` | 23a engine: K3 gates G0..G9, route rule, APPDEC records, 23b refusal, 26g projection |
| `registry/schemas/APPDEC.draft_v1.schema.json` | APPDEC record schema, with the SIMULATE invariant at record level |
| `registry/mechanisms/applicability_reason_code_registry_v1_DRAFT.csv` | 56 reason codes: 11 from plan 23-M (`origin = PLAN_23M`), the rest marked `S158_AI_DRAFT` |
| `registry/mechanisms/route_enum_v1_DRAFT.csv` | DIRECT, INTERPOLATE, SIMULATE, QUALITATIVE, ASK, UNKNOWN (design only, R-18) |
| `tests/fixtures/step22a_23a_fixtures.py` | synthetic hierarchy rows, MECH entries and rules |
| `tests/unit/test_step22a_{process_signatures,case_seal}.py` | 22a tests (25) |
| `tests/unit/test_step23a_{appdec_schema,applicability_engine,appdec_properties}.py` | 23a tests (57; the property file runs 400 + 100 hypothesis examples and a seeded loop of 10^4 queries) |

## 2. Step 22a: process-level signatures

- **Input:** MECH v1.1 entries (read only through `mech_contract`), the PROC hierarchy draft
  `registry/processes/process_hierarchy_v1_DRAFT.csv` (1,112 rows, 17 families, 9 endpoints outside the tree; it
  loads without structural problems) and caller-supplied `SignatureRule`s. **The module ships no rule.** A rule
  names a family (`FAM:*`) or PROC leaf, optional descendants, modifier predicates and mechanism keys; aliases and
  endpoint rows are refused as triggers.
- **Modifiers:** INTENSITY / GEOMETRY / GRANULARITY / MEDIUM (SSOT 257A.3). ENDPOINT is refused in rules and in
  event modifiers: an endpoint cue is an outcome or stop criterion, never a condition input (SSOT 199.8).
  Predicate values are upper-case codes; UNKNOWN is never a value. No modifier vocabulary is approved yet.
- **Output per (rule, mechanism):** the MECH read-API projections copied unchanged (state inputs, condition axes
  including modifier gates, candidate effects with sign sets only), Step-18 deterministic change refs
  (`ALLOC_KINDS` only), `requires_gate_eval = true`, `provenance_class = MODEL_ESTIMATED`, label CANDIDATE,
  `is_evidence = false`. The validator recomputes every projection from the entry, so nothing can be dropped,
  added or widened, and it rejects any magnitude-like key.
- **Recall-oriented:** an entry that Step 23 may not consume still yields a signature. It carries
  `mech_consumable = false` and the reasons, and Step 23 refuses it.
- **Matching:** a predicate on a missing modifier keeps the signature as MODIFIER_UNKNOWN (Step 23 then reads the
  mechanism as UNKNOWN); a predicate that fails on a stated modifier excludes it.
- **Not built:** 22b (event-bound signatures over Step-18 replay), the B0 `PROC.mechanism_families` baseline (those
  labels are AI-drafted family names, not MECH keys), EFFSIG ledger schema, gate report.

**Case-set sealing (human gate, OPEN).** `case_seal.seal_manifest` builds a manifest only for sealers named in
`HUMAN_SEALERS` (Kush Tokas, Parv Goyal) and only when no rule set exists. The commitment is
`sha256(nonce || "\n" || canonical cases)`, and the nonce is never put in the manifest. Nothing was sealed and no
case was authored. `CASE_SET_STATUS = NOT_SEALED_HUMAN_GATE_OPEN`.

## 3. Step 23a: engine

Decision unit (entity_version_id, event_id, target). Gates are K3 (any NOT_APPLICABLE gives NOT_APPLICABLE, else
any UNKNOWN gives UNKNOWN, else APPLICABLE). NOT_REQUIRED marks G0 / G2 / G9.

| Gate | 23a behaviour |
|---|---|
| G0 | case-stated evidence pre-check (`DIRECT` / `BRACKETING` / `NONE` / `NOT_EVALUATED`, default NOT_EVALUATED with `G0_NOT_EVALUATED`); no evidence is read |
| G1 | process resolved and in the hierarchy, else UNKNOWN |
| G2 | deterministic change refs carried from matched signatures, never recomputed |
| G3 | candidates = matched signatures whose candidate effects name the query target |
| G4 | per mechanism: refusal when `consumable_for_applicability` is false (UNKNOWN, `MECH_NOT_CONSUMABLE` plus `MECH_<reason>`); target, matrix scope, preconditions, NECESSARY / INHIBITING gates, inhibitors. Target level: A if any candidate is A, else U if any is U, else NA |
| G5 | 2 or more A without a joint FORM gives NA; 1 A and 1 or more U gives U; a non-ACCEPTED `competes_with` of the active mechanism gives U |
| G6 / G8 | UNKNOWN (`NO_FORM`, `PARAM_UNCONFIRMABLE`) unless the constructed case states them (`CaseGate`) |
| G7 | UNKNOWN if a modulating-gate, catalyst / promoter or history input is missing (rule M-1) or the case does not state FORM-input observability; never NOT_APPLICABLE |
| G9 | route rule (below); reasons explain why SIMULATE was not chosen |

**Route rule** (SIMULATE is the narrowest branch): G0 DIRECT / BRACKETING gives DIRECT / INTERPOLATE (with a
SIMULATE cross-check only under the SIMULATE conditions). Next, G1 and G4..G8 all APPLICABLE, no partial
inhibition, domain IN_VALIDATION_DOMAIN and safety NO give SIMULATE. The same with domain IN_CALIBRATION_ONLY /
EXTRAPOLATED_WITHIN_LIMITS gives QUALITATIVE with a RESEARCH_ONLY / EXTRAPOLATED label. Otherwise G4 APPLICABLE with
one known sign over the APPLICABLE and UNKNOWN candidates gives QUALITATIVE; a missing input the case marks
user-observable gives ASK; anything else gives UNKNOWN. `sim_run_id` is always null.

**Safety properties (tested):** no UNKNOWN or NOT_APPLICABLE in G1 / G4..G8 reaches SIMULATE (property tests plus
the APPDEC schema); a required NECESSARY axis that is missing, None, at another location or in another unit never
gives an APPLICABLE mechanism; a non-consumable entry is never APPLICABLE; records are byte-identical on replay.
The engine validates every record against the APPDEC schema before it returns it.

**Refusals (ApplicabilityError):** `mode="23b"` (BLOCKED: 07.A gate and 15b), any other mode, an axis value whose
source is not CONSTRUCTED_CASE or cites a COND id (spine: no COND consumed), schema-invalid or semantically defective
MECH entries, signatures that fail the 22a validator, malformed case gates, and imputed or free-text values.

## 4. AI readings that need H4 (not decided here)

1. G4 for a target with several candidates: "some candidate APPLICABLE" (G5 then guards competition).
2. A gate whose matrix scope does not include the query matrix gives UNKNOWN (`GATE_MATRIX_UNLISTED`).
3. An INHIBITING window with no qualifying inhibitor item, when present, gives NOT_APPLICABLE. With an inhibitor
   item, extent COMPLETE gives NA, PARTIAL gives APPLICABLE but QUALITATIVE only, UNKNOWN gives U (README D21-11).
4. A STATE_PREDICATE inhibitor whose predicate holds means "present".
5. A missing MODULATING-gate axis makes G7 UNKNOWN even when no catalyst names the gate.
6. A safety status that is not stated, and a domain that is not stated, both block SIMULATE.
7. The SIMULATE cross-check under DIRECT / INTERPOLATE also needs the domain and safety conditions (stricter than
   the plan text).
8. ASK does not compute a value of information; it is a design route only (Step-36 channel needed).

## 5. 26g compatibility (S156 `recipe_adapter`, not edited)

26g consumes `ApplicabilityBinding(event_id, system_id, status, ref)`. A non-UNKNOWN status needs a non-blank
ref. `applicability.to_applicability_binding(record, system_id)` maps an APPDEC record to it: APPLICABLE only for
route SIMULATE; NOT_APPLICABLE when the record's applicability is NOT_APPLICABLE; UNKNOWN otherwise (including
QUALITATIVE, ASK and DIRECT / INTERPOLATE pre-emption). The ref is always `appdec_id`
(`APPDEC-DRAFT-<16 hex>`, a content id, not a minted ledger id). Tested end to end: an APPDEC SIMULATE record
lets `build_simulation_inputs` route SIMULATE on a synthetic replay with every input bound, and UNKNOWN records
give SIM_PROHIBITED with `APPLICABILITY_UNKNOWN`. **Result: compatible.** Two differences are documented. (a) APPDEC is
per target and 26g is per (event, system). Two APPDEC records for one event and system with different statuses
become 26g's APPLICABILITY_CONFLICT (UNKNOWN), which is safe. (b) Which simulator system a target belongs to is a
26b matter: the caller names `system_id`, and the engine names no system (R-14; tested).

## 6. Open for humans

- Seal the shared 22c case set before any rule is coded (spine 22a human gate); author and blind-label cases;
  pre-register G22 / G23 thresholds.
- Author and review the first real `SignatureRule`s (needs reviewed 21b entries; none is ACCEPTED today, so every
  real query would be UNKNOWN).
- Modifier vocabulary for INTENSITY / GEOMETRY / GRANULARITY / MEDIUM.
- Items 1-8 of section 4, and the 45 reason codes marked `S158_AI_DRAFT` in the registry.
- Whether ASK and the RESEARCH_ONLY label belong in the Step-36 route enum (R-18: design only).
- 23b remains BLOCKED until the Step-07 gate validly passes and DATA-EVIDENCE v1 (15b) is frozen.
