# S178 lane FIX-ROUTER: report (census 0.4.0 finished S179)

Status: AI_DRAFTED (D-071). Nothing here is a decision or approval. Code: branch `kush/s179-finish-fixes` (fixer snapshot
6f8d1bc; 68 lane tests pass). The fixer stopped after a 1,000-sample census; that sample predated its last edits to
`router_demo.py` and `router_census.py` (code hashes differ), so S179 re-ran the sample and the full census.

## 1. Runs (census `router-demo-census-0.4.0-draft`, target vitamin C SVAR-000009, seed 20261104, gates on)

| run | host | what |
|---|---|---|
| RUN-S179-ROUTER-001 | manjot | 1,000 sample, reference |
| RUN-S179-ROUTER-002 | vinayak | 1,000 sample: **every count key equal to the manjot sample** (inputs sha256-checked equal: Food.com parquet, interim Wikibooks / Gutenberg, SR portions) |
| RUN-S179-ROUTER-003 | vinayak | full non-BBC, 24 workers, 36 min |
| RUN-S179-ROUTER-004 | Mac | BBC leg (D-003), first committed BBC router census |

## 2. Before (S177 0.3.0) / after (S179 0.4.0), full non-BBC

Same inputs: 600,848 recipes, 9,208,811 events, 35,256,601 items in both runs; ungated DIRECT 267,933 in both.

| count | S177 | S179 | why |
|---|---:|---:|---|
| DIRECT (gated) | 40,308 | 30,248 | R2 prior-process context, R3 attributive / serving-suggestion gate, R5 fail-closed ancestors |
| NOT_APPLICABLE | 813,547 | 74,597 | R4: ABSENT now needs analytical SR zeros, so far fewer items are "target absent" |
| member ABSENT | 4,191,765 | 465,816 | R4 (SR_ZERO_NOT_ANALYTICAL now blocks 8,884,851 member checks) |
| ABSENT ingredients | 52 | 13 | R4; the other 39 have imputed / calculated / assumed SR zeros |
| recipes with any DIRECT | 37,773 | 29,180 | |
| prior-process withheld | 11,861 (HEAT 8,012, HEAT_LEACH 2,188, LEACH 1,661) | 12,140 incl. PRESERVED / PROCESSED / UNRESOLVED classes; UNRESOLVED only 1,676 | R2, R5, R6 |
| DIRECT withheld only by event role | — | ATTRIBUTIVE_STATE 1,825, SERVING_SUGGESTION 54 | R3 |

BBC leg (0.4.0): 11,934 recipes, 1,103,301 items, DIRECT 1,058 (ungated 6,125). Whole corpus 0.4.0: DIRECT 31,306.

Review sheets for humans (AI_DRAFTED_FOR_HUMAN_REVIEW, human columns empty): `reports/s179/absent_top50_for_human_review_S179.csv`,
`reports/s179/absent_blocked_by_category_top50_for_human_review_S179.csv`. Each row shows the SR derivation codes and
data points behind the zero (R7: no "unlocks ABSENT" steering).

## 3. Findings

R2 prior process, R3 role gate, R4 analytical zeros, R5 fail-closed ancestors, R6 process classes, R7 neutral sheet,
CORP-2 inverted ranges flagged UNKNOWN, CORP-3 pairing length status: in code with tests (fixer). Their effect is the
table above. An independent SCI re-review of the code is running separately (S179).

## 4. Superseded

`router_demo_census_vitc_nonBBC_full_S177.json` -> `..._full_S179.json`; `..._1000_S177.json` and `..._1000_S178.json` ->
`..._1000_S179_vinayak.json` (recorded in `registry/superseded_outputs_S176.csv`).
All three S179 (0.4.0) files and the S179 ABSENT review CSVs are in turn superseded by the 0.4.1 `..._S179b` files (§6).

## 5. MECH lane (committed with this lane: it needs the analytical-zero ABSENT rule)

The MECH screen was re-run on the v05 physical layers (manjot, RUN-S179-MECH-001..005): 1,000 sample, WIKIBOOKS,
TASTESET, GUTENBERG_SEGMENT and, for the first time, FOODCOM (522,517 recipes, 10.5 min). Every run: 0 invariant
violations, 0 exceptions. Outputs `reports/s178/mech/screen_census_*_S178_v05.json` supersede the v04 screens. The 32
MECH entries stay UNSOURCED drafts (`registry/mech_entries_draft_v1.jsonl`); the screen is a POSSIBLE / NOT_POSSIBLE /
UNKNOWN feasibility screen, not a prediction.

MECH v06 (S179b): re-run on the v06 physical layers (manjot, RUN-S179-MECH6-001..005, same commands). Every run: 0
invariant violations, 0 exceptions. WIKIBOOKS, TASTESET, GUTENBERG_SEGMENT and the 1,000 sample are count-identical to
v05; Food.com moves 6 WET_HEAT events from UNKNOWN to POSSIBLE (protein denaturation 62,142 -> 62,147, collagen
solubilisation 8,862 -> 8,863), from the v06 temperature bindings. `screen_census_*_S179_v06.json` supersede the v05 screens.
SCI #7 (an SR analytical zero read as ABSENT) is open for a human ruling.

## 6. Census 0.4.1 (S179b, after the SCI re-review)

Code: `evidence_gates.post_state_cue()` (SCI #4): a prior-process state stated after the food ("(already boiled)",
"that you boiled", ", previously boiled", "left over") now withholds DIRECT like the pre-food cues. Tests
`test_s179_router_r2_residual.py`. Commit bf2e635.

| run | host | row | result |
|---|---|---|---|
| non-BBC 1,000 sample | vinayak | RUN-S179-ROUTER-005 | before the full run |
| non-BBC full | vinayak | RUN-S179-ROUTER-006 | same items / events; DIRECT 30,248 -> 30,220; prior-process withheld 13,400 -> 13,428 |
| BBC full | Mac (D-003) | RUN-S179-BBC6-005 | counts unchanged (DIRECT 1,058) |

Outputs `router_demo_census_vitc_{nonBBC_full,nonBBC_1000,BBC_full}_S179b.json`, ABSENT review CSVs
`reports/s179/absent_*_S179b.csv`. Vinayak was shown equal to manjot on a 1,000 sample (every count key) before any
full run there.
