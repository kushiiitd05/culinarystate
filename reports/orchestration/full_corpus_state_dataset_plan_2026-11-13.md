# Full-corpus state dataset — architecture and six-lane plan (13 Nov 2026)

Owner: Kush session as ksh+prv (AI, D-085); Kush reviews ok / not ok. Decisions D-100, D-102, D-104, D-106 recorded;
D-108 and D-110 below are new. Laws: no invented scientific values; UNKNOWN is valid; every filled cell carries a basis;
counts committed, per-row data git-ignored; new output paths only.

## Goal
Every one of the **612,782 recipes** gets every SSOT state column **filled**: either a value with a basis
(TEXT_STATED / LEDGER / PHYSICS_V06 / FORMULA / SCENARIO_DEFAULT / AI_DRAFTED) or `UNKNOWN` with a reason. "Filled" never
means guessed. The selling point: for each recipe step, which state change happens, to which ingredient lots, under which
process conditions, and what that does to nutrients — backed by EVD rows (DIRECT) or a physical formula (SIMULATE).

## Current architecture (what exists)
Recipe text → Rung A parser (events, consumes/produces) → state-graph engine (replay; 14.6 M events) → physics v06
(L1 condition binding: T, t, medium, matrix, lid, size; L2 scenarios: GENTLE/TYPICAL/INTENSE, moisture cap, core T) →
MECH screen → router (DIRECT / SIMULATE / UNKNOWN per ingredient item) → decision layer / demo.
Gaps found 13 Nov: State contract columns code-only (0 rows); router SIMULATE = 0 on 36.4 M items (no FORM/PARAM wired);
event-level formula gate reaches 1 / 49,662 BBC events (matrices are mixed); Transfer/Reserve never typed (fixed by D-102).

## Six lanes

| # | Lane | Output (counts committed; rows ignored) | Host |
|---|---|---|---|
| L1 | **SSOT column map v2** — 210 §238 fields × {ledger rows, physics-v06 derived counts, ABSENT + disposition} | `reports/s179/ssot_column_map_v2_*.{csv,json}` | Mac |
| L2 | **State dataset fill (D-110)** — one row per recipe × event × lot with the State-contract columns (state type D-102, process, process family, T, t, medium, matrix class, lid, piece size, zone dose, phase/moisture cap, lot ingredients, step position) from Rung A + v06 L1/L2 + lot-state; value+basis or UNKNOWN+reason; per-column fill-rate table over all 612,782 recipes | `data/derived/state_dataset_v1/` + `reports/s179/state_dataset_fill_v1.json` | vinayak + manjot (+ Mac for BBC) |
| L3 | **Lot-level formula (D-108)** — process × ingredient-lot combination: apply frozen AA Model A to a lot (not the whole event) when the lot is an acidic liquid fruit lot (juice, purée, tomato, citrus) in a liquid/partial-liquid medium, 60–100 °C, no water contact; retention interval per lot × scenario | `reports/s179/formula_census_aa_lot_*.json` | manjot |
| L4 | **Process × ingredient effect map, all 224 EVD targets** — full-corpus DIRECT census per (ingredient, process, target) using the frozen router; plus the external check where an EVD vitamin-C value and an in-domain formula value coexist | `reports/s179/effect_map_224_*.json` | vinayak |
| L5 | **Process → state-change map** (running) + D-102 types over the corpus; recipe-progression profiles per family | `reports/s179/process_state_map_full_2026-11-13.json` | Mac (running) |
| L6 | **Ollama support (qwen2.5:7b-instruct 845dbda0, vinayak)** — (a) event typing on the 47 gold recipes vs D-102 (prompt registered first); (b) ING attribute drafting for the L3 gate: physical form (LIQUID/SOLID/POWDER/PASTE), acidic (pH < 4.6 YES/NO/UNKNOWN), vitamin-C bearing (YES/NO/UNKNOWN) for every ACTIVE ING row → `registry/ing_attributes_ai_draft_v1.csv`, AI_DRAFTED, reviewed by Kush/Parv before L3 uses it as anything but a labelled draft | registry + report | vinayak via tunnel |

Order: L5 finishing → L6b (needed by L3) and L1 in parallel → L3 + L4 on servers → L2 last (consumes all) → review sheet.

## D-108 (lot-level formula gate), fixed before computing
A lot is IN_DOMAIN for one heat event and scenario iff: its ingredients are all ING rows with L6b form ∈ {LIQUID, PASTE}
and acidic = YES (AI_DRAFTED until reviewed; reported as such), or EVD/ledger categories FRUIT with form LIQUID; the event
medium ∈ {LIQUID, LIQUID_PARTIAL} (WATER/STEAM = WATER_CONTACT, leaching UNKNOWN); food T = min(bath, cap) in 60–100 °C;
t > 0. Same frozen `predict_ln_k`, same labels as D-104/D-106. Lots failing a condition are counted by reason.

## D-110 (state dataset fill rule), fixed before computing
A State column is filled with a value only from a recorded basis; physics scenario values are SCENARIO_DEFAULT; formula
values are FORMULA_RESEARCH_ONLY; AI-drafted attributes are AI_DRAFTED. Otherwise UNKNOWN with the upstream reason code.
The fill-rate table reports, per column and family, VALUE_BY_BASIS vs UNKNOWN_BY_REASON over all 612,782 recipes.

## Risks
Mac 8 GB (L5 only); BBC stays on the Mac (D-003); AI-drafted ING attributes can be wrong → L3 numbers inherit that label;
formula intervals are wide (σ_between 0.84 in ln k); none of this validates the simulator (Step 27 stays not passed).
