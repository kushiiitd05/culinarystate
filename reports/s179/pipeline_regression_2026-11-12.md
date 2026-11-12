# Fifty-recipe source-to-strict-output regression — 12 November 2026

**ENGINEERING_REGRESSION_NOT_SCIENTIFIC_GOLD / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.** This completes a fixed-source integration/reproducibility artifact for T0-C09-R2; it supplies no human gold, accuracy measurement, scientific gate pass or revised frozen result.

## Fixed selection, before pipeline outputs

The seed is `s179-local-pipeline-regression-2026-11-12`. Within each source family, select the smallest SHA256(seed|family|recipe_id) among records with nonempty instructions, without looking at pipeline outcomes. The actual selection has BBC=13, Wikibooks=13, Gutenberg=12 and Food.com=12: 50 identities, balanced across the four instruction-bearing families. TASTEset is excluded because its corpus adapter exposes ingredient lines and no instruction channel. The initial five-family quota check refused before any outcomes; the four-family quota correction was recorded before pipeline execution, not chosen from successful recipes.

`pipeline_regression_selection_2026-11-12.json` stores exact source-file hashes, source IDs, selection ranks and adapter-field hashes. The per-record hash covers adapter identity/title/ingredient-line/step fields; it is not advertised as the hash of the original source-file record bytes. Original instruction strings are joined with newlines for the SourceText input. No raw recipes, queries, ingredient names, source spans, answers or graph text are published in these artifacts.

## Composition and preserved interfaces

Every selected recipe runs through the actual Rung A parser, engine event adapter and deterministic replay. The actual mechanism router processes the same source with Rung A and ingredient-line context. Its first linked food/process pair supplies a metadata query to the evidence packet pipeline and strict-v3 front door; one unlinked recipe uses an explicitly labelled generic fallback. Packet IDs are checked against active EVD IDs. Final display payloads, parse graph, engine log, replay, route and packet summaries are hashed. The replay snapshot is not passed into the retriever because the existing retriever API does not consume it. This is composed source integration, not a claim that that unbuilt state-sharing interface exists.

The strict front door and exact-condition policy remain in force. No context is inferred to force a numeric result. Every original selected recipe is retained; there are no drops based on failure, unknowns or answer coverage.

## Actual results, identical in two local runs

| Stage / scope | Count |
|---|---:|
| Selected recipes | 50 |
| Parse events | 837 |
| Adapted engine events | 1,273 |
| Adapter invented values | 0 |
| Replay status | 42 PASS, 8 UNKNOWN, 0 FAIL |
| Replay issue codes | 0 |
| Replay unknown codes | 11 FRACTION_BASIS_UNSPECIFIED; 11 MASS_BALANCE_UNKNOWN |
| Mechanism route items | 3,204 |
| Route distribution | 5 DIRECT, 10 NOT_APPLICABLE, 3,189 UNKNOWN |
| Metadata evidence packets / hits | 47 / 52 |
| Invalid packet references / handler errors | 0 / 0 |
| Final front-door modes | 46 ASK, 4 ABSTAIN |
| Retention numbers | 0 |
| Recipe/physics responses / physics steps | 5 / 22 |

PASS above is a replay engineering status, not a scientific validity label. DIRECT above retains the legacy source-row-existence semantics; exact condition applicability is not certified. Only five front-door responses include recipe physics; the run does not claim physics/display coverage across all 50 recipes. Conservative refusal and missing-channel/query coverage remain visible. No scientific answer quality is inferred from deterministic outputs or zero invented values.

The complete ordered case payload is byte-equivalent under canonical serialization across the two runs. Core SHA256: `60f1a9e0dcaba2cd0e5307fa3e453d5d9938b63cd1ce1ee6e21a3998c1ebe743`. Both runs use frozen checkout HEAD `034e62a`; exact source hashes and actual UTC timestamps are in each JSON. No source or HEAD change occurred during the runs. `pipeline_regression_golden_2026-11-12.json` stores the expected per-stage hashes as engineering regression baselines, not scientific gold.

## Reproduction and checks

`tools/s179_pipeline_regression.py select --manifest <new-manifest>` creates a selection before outputs. Run `python tools/s179_pipeline_regression.py run --manifest reports/s179/pipeline_regression_selection_2026-11-12.json --out <new-run>`; add `--baseline reports/s179/pipeline_regression_run1_2026-11-12.json` for the second-run comparison. Existing outputs are refused and source/code/selection hashes checked. Local corpus and ledger inputs must be present; BBC text stays local. No SSH, GPU, learned inference or external text transmission is involved.

Integration tests in `tests/integration/test_s179_pipeline_regression.py` first failed for the missing tool, then passed selector order/balance, missing-stratum refusal, source-change detection and a real-component synthetic trace through replay/router/packet/strict refusal. The persisted 50-case golden/repeat pair has a separate integrity test; no second scientific sample or result is manufactured.
