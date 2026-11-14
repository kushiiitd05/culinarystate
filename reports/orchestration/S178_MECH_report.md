# S178 lane MECH report: MECH draft entries + Kleene three-valued mechanism screen

Status: **AI_DRAFTED / PROPOSED / NON_CITABLE / tier T6.** Nothing here is a human review, signature, approval or nonce
(D-071). Worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`); lane base HEAD 32415c4, HEAD at
report time fd93300; all lane files are new and uncommitted. No existing file was edited; nothing was written under
`ledgers/`; no git write. Counts only in committed outputs; no recipe text anywhere.

## 0. Item statuses

| item_id | new status | evidence | what is left |
|---|---|---|---|
| T5-C01-R1 | **PARTIAL** | `registry/mech_entries_draft_v1.jsonl` (32 entries, every roster key; each `mech` object validates MECH v1.1 unchanged, 0 semantic problems, links symmetric / resolved); `reports/s178/mech/mech_entries_check_S178.json`: **G21.2 PASS, G21.3 PASS (32/32), G21.8 PASS (0 numeric leaves besides the record version, 0 kinetic keys), G21.4 NOT MET (0/32 counted)**. Every entry `provenance_class: AI_DRAFTED` (envelope), `evidence_status: UNSOURCED`, `counts_toward_g21_4: false`, CANDIDATE, UNVERIFIED, draft id block `MECH-9000nn` (not minted). | G21.4 needs opened sources with locators minted as DOC/SRC ids (this lane opened none; the 149 condition windows were opened by the S176 L-SRC lane and are cited only as `window_refs`, never as evidence). H4 decisions (section 7). Ledger append is orchestrator-only after review; dual blind review is T5-C01-R3 (humans). |
| T5-C01-R2 | **DONE** | 15 screen-subset entries (>= 14) with preconditions, NECESSARY-gate witnesses, inhibitors and a `screen_binding`, consumed by `mechanism/screen.py` (the screen refuses an entry whose items are not bound to a known evaluator; tested). | Same review / sourcing as R1. |
| T5-C02-R2 | **DONE** | `src/culinarystate/mechanism/{screen,mech_k3,mech_inputs}.py`; 46 tests pass (exhaustive K3 truth tables, verdict properties over every value x basis assignment, random-case view invariants, "UNKNOWN never becomes FALSE" over every evaluator); per-layer views L1 / L2:GENTLE / L2:TYPICAL / L2:INTENSE, each verdict with view, reason code, deciding item and support layer; NOT_POSSIBLE only from an L1-admissible FALSE (measured, analytical SR zeros); edges only between distinct members of the same lot with a mechanism id; **deterministic replay byte-identical** (report and rows, section 4); counts-only census on 1,000 recipes, exceptions 0, invariant violations 0. | Nothing for the agent; the screen stays a T6 diagnostic until entries are reviewed. |
| T5-C02-R3 | **PARTIAL** | Full v04 runs: **GUTENBERG_SEGMENT (73,955), WIKIBOOKS (3,676), TASTESET (700; 0 recipes with steps)**: counts-only JSONs under `reports/s178/mech/`, exceptions 0, invariant violations 0, record alignment 0 foreign, 0 missing records. | **FOODCOM not run on v04** (orchestrator rule: full v04 only if well under an hour; measured GUTENBERG rate extrapolates to about 50 min for FOODCOM's 4.2 M events at load ~100; the started run was stopped after 3 min, no output kept). Re-run all four families on the v05 records with the commands in section 6. BBC leg on the Mac (D-003). Run rows go to `registry/compute_runs_v1.csv` (orchestrator). |

## 1. What the screen says (and what it does not)

Per process event that has a physical-layer record (Layer 1 heat or non-heat binder record), per lot the event consumes
(an entity of the Rung A event graph; members = the linked ING ids of its lineage), per mechanism of the screen subset, per
view: POSSIBLE / NOT_POSSIBLE / UNKNOWN. Strong Kleene AND over the entry's conjuncts (preconditions, NECESSARY gates through a
declared witness, inhibitors as "inhibitor not acting"): FALSE decides, all TRUE gives POSSIBLE, otherwise UNKNOWN; MODULATING
gates never gate (rule M-1). POSSIBLE means *physically possible* (SSOT 141): no extent, rate or direction strength is
assessed; no-switch reactions carry the flags `NO_SWITCH_REACTION`, `DOSE_NOT_ASSESSED`.

Inputs (all read-only; nothing in `composition/`, `simulation/` or the router files was edited):
- **Members and reactants.** Identity of record `mechanism/sr_identity.py` (the Mac's `registry/ing_sr_defaults_v1.csv`);
  SR values from the composition layer loader `composition/sr_legacy.load_sr`; presence by the router's
  `evidence_gates.TargetPresenceScreen` unchanged (PRESENT: every HIGH / MEDIUM plausible identity holds the nutrient; ABSENT:
  HIGH rank-1, every plausible identity of any band known and below the floor, ING category confirmed, and (FIX-ROUTER R4,
  see F1) every zero ANALYTICAL; lot ABSENT only if every member is and none is unlinked; UNKNOWN is never 0). Floor: the
  PROPOSED convention "SR value > 0" (a reaction can act on any non-zero amount; the router's 1 mg vitamin C routing floor
  would turn traces into false NOT_POSSIBLE). The composition layer's lot interval (`lot_state`) is not used for presence:
  with unknown masses (all of Food.com) its lower end is 0 for any lot with a zero member, which says nothing about presence;
  its `high == 0` case is the router's ABSENT minus the identity / category / basis conditions.
- **Taxon classes** (Allium, onion-type Allium, Brassicaceae, PPO-browning foods, green tissue, ascorbate-oxidase foods,
  animal connective tissue) from the SR description / food group of the identity of record; enzyme classes need a raw
  identity (a cooked, dried, canned or powdered identity is not assumed to hold active enzyme). A class can make a reactant
  PRESENT, never ABSENT (no SR nutrient measures alliin, glucosinolates, PPO, chlorophyll or collagen).
- **Event inputs.** L1 axes (medium, temperature_profile, lid_state, aerated, rinse_medium ...) with their bases; for an L2
  view the same plus that bracket's Layer 2 record (surface state, bath temperature). Unrecognised bases raise (counted).
- **Lineage.** Per member, was it heated (`evidence_gates.prior_kind` HEAT) or cut / crushed / blended by an earlier event.

Layer rule: an L2 view uses Layer 2 values only to support TRUE (bases SCENARIO / MODEL_DERIVED / ASSUMED_DEFAULT); an L2
FALSE is read as UNKNOWN (`L2_CANNOT_EXCLUDE__...`); an L2 value in the L1 view raises. Checked during every run:
`L2_EXCLUDED_WITHOUT_L1`, `L2_LOST_L1_POSSIBLE`, `POSSIBLE_WITHOUT_ALL_TRUE` all 0.

### The 15 screen entries (conjuncts; the only route to NOT_POSSIBLE)

| entry | conjuncts (K3 AND) | NOT_POSSIBLE only when |
|---|---|---|
| ALLIINASE_ALLIIN_CLEAVAGE (member-scoped) | raw Allium member; cells disrupted (cut / blend event, or a cut in that member's lineage); enzyme active (no heat in that member's lineage); no foreign member (only Allium tissue or inert fat / water) | never |
| ONION_LACHRYMATORY_FACTOR_SYNTHESIS (member) | raw onion-type member; disrupted; active; no foreign member | never |
| MYROSINASE_GLUCOSINOLATE_HYDROLYSIS (member) | raw Brassicaceae member; disrupted; active; no foreign member | never |
| PPO_ENZYMATIC_BROWNING (member) | raw PPO-class member; disrupted; active; oxygen contact (air-exposed medium, "uncovered" cue or aeration); no foreign member | never |
| ASCORBATE_OXIDASE_AA_OXIDATION (member) | raw broccoli / carrot member; vitamin C present; active; oxygen contact; no foreign member | vitamin C absent (analytical SR zero, every member) |
| ASCORBATE_TO_DHA_OXIDATION | vitamin C present; oxygen contact | vitamin C absent |
| LEACHING (screened analyte vitamin C) | vitamin C present; aqueous contact (immersion, steam condensate, rinse, aqueous soak / brine) | vitamin C absent |
| MAILLARD_STRECKER_LUMPED | amino source (SR protein); carbonyl source (SR sugars; never absent: trace reducing sugars below SR reporting react, e.g. in meat) | protein absent |
| CARAMELISATION | sugars present (animal muscle members are trace-exempt: UNKNOWN, not absent); heat applied at the event | sugars absent |
| STARCH_GELATINISATION | starch present; excess water (immersion); NECESSARY surface-temperature gate via the witness "surface held at the boiling point of water in excess water" | starch absent |
| PROTEIN_DENATURATION_AGGREGATION | protein present; denaturing driver = OR(surface at the boiling point of water, aeration / foaming) | protein absent |
| COLLAGEN_SOLUBILISATION | animal connective tissue present (absent if protein absent); NECESSARY gate via the witness "surface held at T_boil in moist heat" | protein absent |
| CHLOROPHYLL_TO_PHEOPHYTIN | green tissue present (pH is MODULATING, never gating) | never |
| MOISTURE_LOSS | water present | water absent |
| LIPID_OXIDATION | lipid present; oxygen contact | fat absent |

Witness rule (PROPOSED, H4): the cited condition windows (QUALITATIVE_ONLY, `registry/mechanism_condition_windows_draft_v1.csv`)
report onsets below 100 C for starch gelatinisation in excess water, myosin / actin / egg-white denaturation and collagen
denaturation; the screen uses only that qualitative statement, against the physical definition T_boil = 100 C at 1 atm: TRUE
when the surface is held at the boiling point (L1: boil / parboil / steam by physical definition or a stated T >= 100 C in an
aqueous medium; L2: surface state at T_boil, or immersed at a bath >= 100 C), otherwise UNKNOWN, never FALSE (no bound is
reported in MECH). This is why the three brackets differ only for these three entries.

## 2. Results (v04 physical records; counts of (event, lot) units; T6 diagnostics, not results about food)

### 2.1 1,000-recipe sample (all non-BBC families; `reports/s178/mech/screen_census_1000_S178_v04.json`)

1,000 sampled (997 with steps); events in graphs 15,326; screened heat 2,820 + non-heat 4,927 (= every v04 sample record;
0 missing, 0 foreign records in parts); lots 9,297 (members 25,507; 90 lots with an unlinked member; 897 screened events
consumed no lot); exceptions 0; invariant violations 0.

| mechanism | L1 P / N / U | L2 GENTLE / TYPICAL / INTENSE P | L1 P at heat / non-heat events |
|---|---|---|---|
| ALLIINASE_ALLIIN_CLEAVAGE | 108 / 0 / 9,189 | 108 / 108 / 108 | 17 / 91 |
| ASCORBATE_OXIDASE_AA_OXIDATION | 8 / 50 / 9,239 | 8 / 8 / 8 | 8 / 0 |
| ASCORBATE_TO_DHA_OXIDATION | 895 / 50 / 8,352 | 895 / 895 / 895 | 660 / 235 |
| CARAMELISATION | 2,068 / 0 / 7,229 | 2,068 / 2,068 / 2,068 | 1,987 / 81 |
| CHLOROPHYLL_TO_PHEOPHYTIN | 947 / 0 / 8,350 | 947 / 947 / 947 | 324 / 623 |
| COLLAGEN_SOLUBILISATION | 34 / 72 / 9,191 | 40 / 40 / 40 | 34 / 0 |
| LEACHING | 304 / 50 / 8,943 | 304 / 304 / 304 | 281 / 23 |
| LIPID_OXIDATION | 1,504 / 230 / 7,563 | 1,504 / 1,504 / 1,504 | 922 / 582 |
| MAILLARD_STRECKER_LUMPED | 6,318 / 72 / 2,907 | 6,318 / 6,318 / 6,318 | 1,921 / 4,397 |
| MOISTURE_LOSS | 8,111 / 54 / 1,132 | 8,111 / 8,111 / 8,111 | 2,522 / 5,589 |
| MYROSINASE_GLUCOSINOLATE_HYDROLYSIS | 16 / 0 / 9,281 | 16 / 16 / 16 | 3 / 13 |
| ONION_LACHRYMATORY_FACTOR_SYNTHESIS | 77 / 0 / 9,220 | 77 / 77 / 77 | 13 / 64 |
| PPO_ENZYMATIC_BROWNING | 6 / 0 / 9,291 | 6 / 6 / 6 | 4 / 2 |
| PROTEIN_DENATURATION_AGGREGATION | 793 / 72 / 8,432 | 852 / 852 / 862 | 215 / 578 |
| STARCH_GELATINISATION | 26 / 288 / 8,983 | 26 / 26 / 29 | 26 / 0 |

Bracket disagreement (G / T / I): protein 10, starch 3, all `U__U__P`. Edges (L1): Maillard REACTANT_PAIR 47,902;
chlorophyll CONDITION_SUPPLIER (acid-class member -> green member, INCREASES) 408; PPO CONDITION_SUPPLIER (INHIBITS) 3.

### 2.2 Full families (v04): GUTENBERG_SEGMENT + WIKIBOOKS (TASTESET has 0 recipes with steps: nothing to screen)

77,631 recipes (77,454 with steps); screened heat 193,482 + non-heat 316,321 (0 missing, 0 foreign); lots 596,616;
exceptions 0; invariant violations 0.

| mechanism | L1 POSSIBLE | L1 NOT_POSSIBLE | L1 UNKNOWN | L2 G / T / I POSSIBLE |
|---|---|---|---|---|
| ALLIINASE_ALLIIN_CLEAVAGE | 7,930 | 0 | 588,686 | 7,930 / 7,930 / 7,930 |
| ASCORBATE_OXIDASE_AA_OXIDATION | 148 | 4,224 | 592,244 | 148 / 148 / 148 |
| ASCORBATE_TO_DHA_OXIDATION | 33,316 | 4,224 | 559,076 | 33,316 x 3 |
| CARAMELISATION | 127,433 | 0 | 469,183 | 127,433 x 3 |
| CHLOROPHYLL_TO_PHEOPHYTIN | 31,994 | 0 | 564,622 | 31,994 x 3 |
| COLLAGEN_SOLUBILISATION | 3,887 | 1,598 | 591,131 | 5,384 / 5,384 / 5,492 |
| LEACHING | 33,415 | 4,224 | 558,977 | 33,415 x 3 |
| LIPID_OXIDATION | 80,559 | 18,307 | 497,750 | 80,559 x 3 |
| MAILLARD_STRECKER_LUMPED | 345,174 | 1,598 | 249,844 | 345,174 x 3 |
| MOISTURE_LOSS | 512,469 | 649 | 83,498 | 512,469 x 3 |
| MYROSINASE_GLUCOSINOLATE_HYDROLYSIS | 1,455 | 0 | 595,161 | 1,455 x 3 |
| ONION_LACHRYMATORY_FACTOR_SYNTHESIS | 6,769 | 0 | 589,847 | 6,769 x 3 |
| PPO_ENZYMATIC_BROWNING | 326 | 0 | 596,290 | 326 x 3 |
| PROTEIN_DENATURATION_AGGREGATION | 64,428 | 1,598 | 530,590 | 72,117 / 72,118 / 72,949 |
| STARCH_GELATINISATION | 5,267 | 18,089 | 573,260 | 5,267 / 5,267 / 5,473 |

Per-family numbers, reason codes (by verdict), deciding items, L1 -> L2 changes, bracket disagreement, edges and a process-family
breakdown are in the JSONs.

### 2.3 What the numbers say

- **UNKNOWN dominates, honestly.** The largest UNKNOWN reasons: taxon not identified (most lots hold no raw member of the
  class), oxygen contact not stated (the text rarely says "uncovered"; L2 has no oxygen field), SR identity unusable or
  MEDIUM, starch not reported by SR (`SR_VALUE_MISSING`), and `SR_ZERO_NOT_ANALYTICAL` (an assumed / imputed SR zero).
- **NOT_POSSIBLE is rare and comes only from analytical SR zeros**: e.g. starch in a lot of meat / onion / fruit members,
  fat in sugar / water lots, vitamin C in lots of members with analytical zeros. The analytical-basis rule cut vitamin C
  NOT_POSSIBLE in the sample from 718 to 50 (the zeros for meats are mostly assumed), see F1.
- **L2 adds little**, by construction: with no sourced numeric window, Layer 2 can only support the T_boil witnesses
  (starch, protein, collagen), and no L2 value may exclude. Brackets separated 1,146 (event, lot, mechanism) units in the full
  families (all UNKNOWN -> POSSIBLE at INTENSE or TYPICAL).
- **No-switch reactions are POSSIBLE at non-heat events** (Maillard 232,031 of 345,174 L1 POSSIBLE in the full families):
  the reading "rate > 0 at any temperature" (SSOT 144.1: no universal switch). Flagged `DOSE_NOT_ASSESSED`; a human may
  prefer UNKNOWN at non-heat events (decision H3 below).
- The cut-triggered enzymes are POSSIBLE mostly at the cut event itself and at the first heat event of a cut, unheated
  member (enzyme active at the start of the come-up); foreign members (acid, salt, other foods) make them UNKNOWN.

## 3. Files (all new; no existing file edited)

| path | role |
|---|---|
| `src/culinarystate/mechanism/mech_k3.py` | K3 logic, `Conjunct`, `combine` (one view, layer rules), `k_or_verdicts` |
| `src/culinarystate/mechanism/mech_entries.py` | deterministic builder of the draft JSONL (roster + 15 authored screen specs + 17 GATES_UNKNOWN stubs) |
| `src/culinarystate/mechanism/mech_registry_check.py` | schema / semantic / link checks (reuses `mech_contract`), envelope rules, G21.2 / G21.3 / G21.4 / G21.8 |
| `src/culinarystate/mechanism/mech_inputs.py` | member catalog, taxon classes, inert carriers, lot / event contexts, 13 evaluators (only `nutrient_present` and `collagen_present` may return FALSE) |
| `src/culinarystate/mechanism/screen.py` | the screen, edges, lineage, per-recipe screening, record-part reader, counts nesting |
| `tools/s178_mech_build_entries.py` | writes the JSONL + gate check; `--check-only` verifies the file equals a fresh build |
| `tools/s178_mech_screen_run.py` | sample / full runs; physical-record directories are parameters; counts JSON + timing sidecar + rows |
| `tests/unit/test_s178_mech_k3.py`, `test_s178_mech_entries.py`, `test_s178_mech_screen.py` | 46 tests |
| `registry/mech_entries_draft_v1.jsonl` | 32 draft entries (sha256 `9e36ca36e3d6c4e283d5e351c8a27ab06da691c78b3df4d91b71e46f6f9062f5`) |
| `reports/s178/mech/` | `mech_entries_check_S178.json`, `screen_census_{1000,GUTENBERG_SEGMENT_full,WIKIBOOKS_full,TASTESET_full}_S178_v04.json` + `_timing.json` |
| `data/derived/mech_screen_{1000,GUTENBERG_SEGMENT_full,WIKIBOOKS_full,TASTESET_full}_S178v04/` | per-(event, lot) verdict rows (git-ignored; ids and codes only; 143 MB in total) |

Entry format: one JSONL line = envelope (`provenance_class: AI_DRAFTED`, `evidence_status`, `counts_toward_g21_4`,
`window_refs`, `screen_binding`, ...) + `mech` (the MECH v1.1 object). The v1.1 enum has no AI_DRAFTED value, so `mech` says
`provenance_class: INFERRED_LLM` + `ai_drafted: true` (decision H1). All interval bounds NOT_REPORTED; EC xrefs PROPOSED /
UNVERIFIED (from the windows registry's ExPASy rows); 0 ACCEPTED xrefs; `consumable_for_applicability` false for all 32, so
the AASIM SIMULATE lock (`NO_CANDIDATE_MECHANISM`) is unchanged.

## 4. Tests and checks

- `tests/unit/test_s178_mech_{k3,entries,screen}.py`: **46 passed**. K3: exhaustive AND / OR / NOT tables up to 4 inputs
  against min / max over F < U < T, De Morgan, `combine` exhaustive over values (and values x basis class): POSSIBLE iff all
  TRUE, NOT_POSSIBLE iff an L1-basis FALSE, an UNKNOWN conjunct never yields POSSIBLE and yields NOT_POSSIBLE only when another
  conjunct is FALSE, refining an UNKNOWN never flips a decided verdict, member OR. Entries: committed file == fresh build;
  v1.1 schema + semantics + links for all 32; honest labels; 0 numbers; window refs exist; binding covers exactly the
  evaluable items; no NECESSARY T gate on a CHEMICAL_REACTION; negative controls for G21.2 / G21.3 / G21.4 / G21.8 and the
  envelope. Screen: synthetic members (not USDA data): enzyme rules, member-scope (one member must satisfy every conjunct),
  views (boil vs simmer brackets), absent vs unknown identity vs unlinked member, no-switch reactions, trace exemption,
  analytical-basis rule (assumed zero and no basis never give NOT_POSSIBLE), 400 seeded random cases for the view invariants,
  every evaluator UNKNOWN on empty inputs, evaluator guards, edges, lineage propagation, recipe path + replay, part reader.
- Existing suites re-run before the concurrent FIX-ROUTER edit: `test_step21_mech_v1_1_{schema,semantics}`,
  `test_s176_evidence_gates`, `test_s177_router_gates`, `test_s177_sr_identity_adapter`, `test_s175_*`: 136 passed.
- Replay: the sample run twice gives byte-identical reports (`8553eb0b...`) and rows (`b930796b...`); the earlier pair under
  the old router rule was also identical (`765b64be...`). Because `evidence_gates.py` changed again at 14:47:56Z (between the final sample and the full runs), the sample was re-run at 15:03Z against the current file (sha256 `a368a479dc79e771c03daf82ac98f91897dea14b91721eee4953ce375944477b`): report and rows byte-identical again, so the sample and the full runs used equivalent presence rules.

## 5. Findings (no fix made in another lane's file)

- **F1 (concurrent change, not a bug).** FIX-ROUTER changed `evidence_gates.TargetPresenceScreen` (uncommitted, mtime
  14:39Z and 14:47:56Z) so that ABSENT needs an analytical SR zero and a screen without basis is fail-closed. My first
  sample (14:31Z) and first WIKIBOOKS / TASTESET / GUTENBERG runs (14:38-14:41Z) mixed the old and new rule (a new-rule
  screen without basis gives no ABSENT at all); I stopped them, deleted their outputs, passed the SR derivation basis
  (`evidence_gates.read_sr_basis`) to the screen (`mech_inputs` 0.2.0; `basis_supported()` keeps the old signature working)
  and re-ran. **The committed numbers need the FIX-ROUTER `evidence_gates.py` committed with (or before) this lane**; with the
  old file the screen runs with `absent_basis_rule: ROUTER_SCREEN_WITHOUT_BASIS_RULE` and gives more NOT_POSSIBLE (sample
  vitamin C 718 instead of 50). Each report records `evidence_gates_version` and `absent_basis_rule`.
- **F2 (schema consequence).** In MECH v1.1 a categorical gate that lists any allowed / excluded category needs an evidence
  id, so an UNSOURCED entry cannot even state "water medium" as a categorical gate; such drivers are PROPOSED_KEY
  preconditions here (`aqueous_phase_contact`, `oxygen_exposure`, `cell_integrity`, `enzyme_state_*`, SSOT v16 DRAFT 285.9
  names). Same for numeric bounds (none without PRIMARY evidence).
- **F3 (data gap).** 1,417 of 2,048 ACTIVE ING have no category, so the router's ABSENT can never be confirmed for them
  (`CATEGORY_EMPTY`; garlic is one); the INGCAT proposals would change the NOT_POSSIBLE counts when applied.
- **F4 (performance, Mac file).** `composition/food_ph.PHTable.lookup` is uncached (S177 FULLRUN F4); the catalog here
  memoises by name instead of editing it.
- **F5 (coverage).** Gutenberg has no ingredient lines, so the Mac's recipe-pool lot census cannot be built for it (S177
  F6), but the event-level lots used here come from the Rung A graph of the step text, so Gutenberg screens normally.
  Food.com has no units: presence is all the screen needs (no masses are used).

## 6. Re-run commands (record directories are parameters; for v05, replace the four directories, tag, out and rows-dir)

The chunk count is `workers * 8` and must be a multiple of the part count of every directory (v04: L1 / L2 64 parts for the
1,000 sample, GUTENBERG, WIKIBOOKS, TASTESET; 192 for FOODCOM; NH 64 for the sample, 192 for the full families), because
chunk i reads `part-(i mod parts)`; the tool refuses otherwise. `--workers 8` for the sample, `--workers 24` for the full
families. Each run refuses to overwrite its `--out`.

```bash
cd ~/kush_work/culinarystate/.orch
PY=../.venv312/bin/python
# 1,000 sample (v04 as run; for v05 use the v05 1,000-sample directories)
nice -n 10 $PY tools/s178_mech_screen_run.py --seed 20261104 --sample-size 1000 --workers 8 \
  --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET \
  --l1 data/derived/physical_L1_1000_S178v04 --l2 data/derived/physical_L2_1000_S178v04 \
  --nh-l1 data/derived/physical_NH_L1_1000_S178v04 --nh-l2 data/derived/physical_NH_L2_1000_S178v04 \
  --tag 1000_S178_v04 --out reports/s178/mech/screen_census_1000_S178_v04.json \
  --timing-out reports/s178/mech/screen_census_1000_S178_v04_timing.json --rows-dir data/derived/mech_screen_1000_S178v04
# full families, one per run (FOODCOM still to run)
for F in FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET; do
  nice -n 10 $PY tools/s178_mech_screen_run.py --seed 20261104 --sample-size 600000 --workers 24 --families $F \
    --l1 data/derived/physical_L1_full_S178v04/$F --l2 data/derived/physical_L2_full_S178v04/$F \
    --nh-l1 data/derived/physical_NH_L1_${F}_full_S178v04 --nh-l2 data/derived/physical_NH_L2_${F}_full_S178v04 \
    --tag ${F}_full_S178_v04 --out reports/s178/mech/screen_census_${F}_full_S178_v04.json \
    --timing-out reports/s178/mech/screen_census_${F}_full_S178_v04_timing.json \
    --rows-dir data/derived/mech_screen_${F}_full_S178v04
done
```

Measured wall time (v04, load 70-100 on 128 cores): sample 242 s (231 s of it setup: corpus read, SR, manifests), WIKIBOOKS
47 s, TASTESET 19 s, GUTENBERG 415 s; FOODCOM estimated about 50 min (4.2 M events). The entries are rebuilt with
`$PY tools/s178_mech_build_entries.py` (or verified with `--check-only`).

## 7. Decisions for humans (all PROPOSED; the screen runs with the defaults shown)

- **H1** MECH v1.1 `provenance_class` has no AI_DRAFTED value: keep the envelope label + `INFERRED_LLM`, or add the enum value
  (H4, D21-n). Mint real MECH ids after review (draft block `MECH-9000nn` is not minted).
- **H2** Accept "SR value > 0" as the mechanism-screen floor (not the router's 1 mg vitamin C routing floor) and accept an
  analytical SR zero as "absent" per mechanism (an expert should look at the zero-based NOT_POSSIBLE rows: starch, fat,
  vitamin C, water, protein). The animal-muscle trace exemption for caramelisation sugars is an AI judgement.
- **H3** No-switch reactions (Maillard, caramelisation once heated, AA oxidation, chlorophyll, lipid oxidation, moisture
  loss): POSSIBLE whenever the reactants and NECESSARY non-thermal conditions hold, at any event (current), or UNKNOWN at
  non-heat events until a timescale-scoped dose criterion is sourced (SSOT v16 DRAFT 285.12).
- **H4** The T_boil witness rule (qualitative use of QUALITATIVE_ONLY windows against the 100 C physical definition).
- **H5** The taxon class lists (`mech_inputs.CLASS_HEADS`, `CLASS_QUALIFIER`), the inert-carrier names and the
  ascorbate-oxidase food list (broccoli, carrot only, from the windows) are AI-drafted for expert review.
- **H6** G21.4: who opens and mints the sources (the 149 S176 windows could become DOC / SRC ids after a human re-opens them;
  entries then flip to SOURCED and count).
- **H7** Whether Layer 2 should carry an oxygen-exposure scenario default (today L2 cannot separate any oxygen-gated entry).

## 8. Open questions

- Precursor depletion after a cut (alliin, glucosinolates) is not modelled: a later event of a cut, unheated member is
  POSSIBLE (enzyme active at the start of the come-up). Should depletion be an explicit UNKNOWN conjunct?
- Steam-condensate leaching is TRUE (physical: steaming heats by condensation); some reviewers may want UNKNOWN.
- ONION_LACHRYMATORY_FACTOR_SYNTHESIS excludes leek and chive from the onion class (LFS presence not established here);
  garlic is UNKNOWN, not "no LFS".
- 897 of 7,747 screened sample events consume no graph lot (Rung A lineage): they are counted, not screened.

## 9. Run rows (PROPOSED for `registry/compute_runs_v1.csv`; the orchestrator owns the file)

No run of this lane was in flight at the 19:50 IST session restart (the smoke run had ended at 13:58Z; the next run started
at 14:31Z), so no ABORTED_SESSION_RESTART row applies.

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-MECH-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,NONE,1,python tools/s178_mech_build_entries.py,registry/mech_entries_draft_v1.jsonl,9e36ca36e3d6c4e283d5e351c8a27ab06da691c78b3df4d91b71e46f6f9062f5,2026-11-09T13:59:57Z,2026-11-09T13:59:58Z,DONE,"32 draft entries; gate check reports/s178/mech/mech_entries_check_S178.json sha256 4b17cf3b5aff4419f64640e324ba2e45fc9c152f1caf9c4618d74f78cb84764e (G21.2/3/8 PASS, G21.4 0/32); --check-only re-verified"
RUN-S178-MECH-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,tools/s178_mech_screen_run.py --sample-size 1000 (smoke; v04 sample records),scratchpad (not kept),c02965627f015037476097a92d1707ddf456f63a9988fc5b4aadc74d4abc68eb,2026-11-09T13:57:50Z,2026-11-09T13:58:25Z,SCRATCH,"smoke before tests; code changed after it"
RUN-S178-MECH-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,tools/s178_mech_screen_run.py --seed 20261104 --sample-size 1000 --workers 8 (v04 sample records),reports/s178/mech/screen_census_1000_S178_v04.json (moved to scratch),765b64bee59117619f2367fbaa85e5c4870b8467e4181880aab420e00aee5ba7,2026-11-09T14:31:18Z,2026-11-09T14:34:54Z,SUPERSEDED,"old router ABSENT rule (no analytical-basis check); replay byte-identical; superseded by RUN-S178-MECH-008 after the concurrent FIX-ROUTER change"
RUN-S178-MECH-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,WIKIBOOKS,24,tools/s178_mech_screen_run.py --sample-size 600000 --workers 24 --families WIKIBOOKS (v04),deleted,d66532237deb83edc4f7163b8470eb755c64d95e733b7203edef0ecefc1ff6de,2026-11-09T14:38:46Z,2026-11-09T14:39:42Z,SUPERSEDED_DELETED,"started across the concurrent evidence_gates change; output deleted"
RUN-S178-MECH-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,TASTESET,24,tools/s178_mech_screen_run.py --sample-size 600000 --workers 24 --families TASTESET (v04),deleted,6e34191af5c90db240af10bebdf6230b41f1afd4084d0dd3f3a9d378107743eb,2026-11-09T14:39:46Z,2026-11-09T14:40:08Z,SUPERSEDED_DELETED,"as RUN-S178-MECH-004"
RUN-S178-MECH-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,GUTENBERG_SEGMENT,24,tools/s178_mech_screen_run.py --sample-size 600000 --workers 24 --families GUTENBERG_SEGMENT (v04),none,NONE,2026-11-09T14:40:10Z,2026-11-09T14:41:00Z,ABORTED,"start and end approximate; stopped by the lane on finding the concurrent evidence_gates change; no output"
RUN-S178-MECH-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,tools/s178_mech_screen_run.py --sample-size 1000 (replay of RUN-S178-MECH-008),scratchpad (not kept),8553eb0bd62f070d470ded09f5399c1e8d1880e0080240cd8353d075c85c7486,2026-11-09T14:47:10Z,2026-11-09T14:50:16Z,DONE,"start approximate (began right after RUN-S178-MECH-008); replay: report and rows (b930796b716f4a18b9b6570793b616343972ffadbe992884084cbf264f84c36a) byte-identical to RUN-S178-MECH-008"
RUN-S178-MECH-008,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,nice -n 10 python tools/s178_mech_screen_run.py --seed 20261104 --sample-size 1000 --workers 8 --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET --l1 data/derived/physical_L1_1000_S178v04 --l2 data/derived/physical_L2_1000_S178v04 --nh-l1 data/derived/physical_NH_L1_1000_S178v04 --nh-l2 data/derived/physical_NH_L2_1000_S178v04 --tag 1000_S178_v04,reports/s178/mech/screen_census_1000_S178_v04.json,8553eb0bd62f070d470ded09f5399c1e8d1880e0080240cd8353d075c85c7486,2026-11-09T14:43:06Z,2026-11-09T14:47:08Z,DONE,"v04 sample; exceptions 0; invariant violations 0; rows data/derived/mech_screen_1000_S178v04 (9,297 rows, sha256 of concatenated parts b930796b716f4a18b9b6570793b616343972ffadbe992884084cbf264f84c36a)"
RUN-S178-MECH-009,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,WIKIBOOKS,24,nice -n 10 python tools/s178_mech_screen_run.py --seed 20261104 --sample-size 600000 --workers 24 --families WIKIBOOKS --l1 data/derived/physical_L1_full_S178v04/WIKIBOOKS --l2 data/derived/physical_L2_full_S178v04/WIKIBOOKS --nh-l1 data/derived/physical_NH_L1_WIKIBOOKS_full_S178v04 --nh-l2 data/derived/physical_NH_L2_WIKIBOOKS_full_S178v04 --tag WIKIBOOKS_full_S178_v04,reports/s178/mech/screen_census_WIKIBOOKS_full_S178_v04.json,2faaa041ff46556bdcd9bd961ae2e6b69fccbfba92e222bfe1c93ce3666b4234,2026-11-09T14:50:18Z,2026-11-09T14:51:04Z,DONE,"v04 full; exceptions 0; rows 36,969 sha256 94e77cba23afd96ed6d3679d1e81041310d21e52253196ca1c55d14325be1179"
RUN-S178-MECH-010,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,TASTESET,24,same command with --families TASTESET and the TASTESET v04 directories,reports/s178/mech/screen_census_TASTESET_full_S178_v04.json,0bace192dc117ac7b43a50b5837ceeca765ee6078c7433cd706d1177e4c6ad89,2026-11-09T14:51:07Z,2026-11-09T14:51:26Z,DONE,"v04 full; 700 recipes, 0 with steps; exceptions 0"
RUN-S178-MECH-011,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,GUTENBERG_SEGMENT,24,same command with --families GUTENBERG_SEGMENT and the GUTENBERG_SEGMENT v04 directories,reports/s178/mech/screen_census_GUTENBERG_SEGMENT_full_S178_v04.json,9faf9088da7018d83a8b27e2d77363926e39818675e57de2c88ea62e4b861a7c,2026-11-09T14:51:28Z,2026-11-09T14:58:17Z,DONE,"v04 full; exceptions 0; rows 559,647 sha256 c51ec8d9d3a5f6b6915ca864b191274ba48d1cd727b15d797dcfb846381bb62c"
RUN-S178-MECH-012,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,FOODCOM,24,same command with --families FOODCOM and the FOODCOM v04 directories,none,NONE,2026-11-09T14:58:19Z,2026-11-09T15:01:31Z,ABORTED,"times approximate (process age 3:12 at the stop); stopped by the lane after 3 min (setup): orchestrator rule (full v04 only if well under an hour); estimated about 50 min; left for the v05 re-run"
RUN-S178-MECH-013,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),fd93300+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,tools/s178_mech_screen_run.py --sample-size 1000 (recheck against evidence_gates.py sha256 a368a479dc79e771c03daf82ac98f91897dea14b91721eee4953ce375944477b),scratchpad (not kept),8553eb0bd62f070d470ded09f5399c1e8d1880e0080240cd8353d075c85c7486,2026-11-09T15:02:56Z,2026-11-09T15:07:19Z,DONE,"report and rows byte-identical to RUN-S178-MECH-008"
```
