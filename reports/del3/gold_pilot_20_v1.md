# Gold pilot_20 v1 — freeze and double-annotation status (S101, 2026-10-19)

**Status: BLOCKED_HUMAN.** Kush and Parv have not yet annotated. No annotation, agreement or adjudication number exists in this report because none
may be fabricated. Run `tools/gold_pilot_agreement.py` after both folders are DONE; it refuses to run before that.

## What S101 prepared (automated)
| Item | Result |
|---|---|
| EXP registration | EXP-000005, -006, -007 registered with their existing IDs (minter asserted next IDs = 5, 6, 7; no replacement IDs); ledger now EXP-000001…7, contiguous; each record's `card_path` exists; results paths exist for 1–6; 007 is PLANNED; hypotheses in `hypothesis`, RQ/gate/dependencies in `notes` (RQ and GATE ledgers do not exist, so no dangling refs). Card text untouched. EXP-000005's card predates GLiNER (S083); flagged in its record. |
| Frozen input | `annotation/batches/pilot_20.csv` unchanged (20 recipes, strata reserve_split 3, drain_discard 3, baking 3, indian 3, simple 3, multi_component 3, random 2). No recipe replaced. |
| Immutable reference | `annotation/gold/pilot_20_manifest.csv` (committed, no recipe text): recipe id, REC id, family id, stratum, source URL, line/step counts, `raw_content_sha256` over title + ingredient lines + step texts = **identical to the ledger's `content_sha256` for 20/20 recipes**, handbook and schema versions, frozen_at. 20 distinct near-duplicate families, none shared (max family size 1), so no family leaks between recipes. |
| Independent copies | `annotation/gold/pilot_20/Kush/` and `…/Parv/` — 20 blank `DRAFT` files each (raw text only; spans, entities, concepts, events, coref, unknowns all empty; `TODO` guards make `validate` fail until finished). Local only (D-007 third-party text). The freeze tool never overwrites an annotator file that holds work. Neither is marked DONE or HUMAN_VERIFIED. |
| Handbook package | handbook v1 unchanged + **Addendum A** (9 clarifications from S100: file locations, automatic `Add`, no `Observe`, how relations are encoded, canonical-link policy, time/temperature/endpoint fields, final state derived by replay, DONE rule, rule-change policy); checklist, hard examples (H1–H16), UNKNOWN examples exist; `annotation/PILOT_20_TASK.md` holds the exact commands. |
| Commands | validate: `tools/gold_cli.py validate <file>` · replay Gold state (new): `tools/gold_cli.py replay <file>` · compare Kush vs Parv: `tools/gold_pilot_agreement.py` (all 20; exits 2 BLOCKED_HUMAN until 40 files are DONE+valid) or `tools/gold_cli.py agree <K> <P>` (one recipe) · adjudication template: `annotation/adjudication_template.csv`. |
| Agreement tooling | `annotation/pilot_agreement.py`: exact/relaxed span F1 and per-label F1; concept agreement and UNKNOWN-disagreement rate; process-link F1; event F1 (strict and loose); relation F1 (all and structural merge/split/reserve/recombine); coref B³; intermediate-entity F1; alive-entity F1; state-field agreement; replay consistency. B's entity labels are mapped onto A's (`align_entities`) so choosing a different name for an intermediate is not counted as disagreement (tested). Disagreement table has the nine required categories: boundary, entity type, canonical identity, event type, event argument, coref, intermediate identity, quantity, final state. 3 unit tests pass; they run on the 3 worked examples with synthetic perturbations, never on pilot_20. |

## Known limitations of the protocol (stated before the data exist)
- Two annotators from one project, both familiar with the handbook; agreement will overstate reliability for outside annotators.
- 20 recipes from one source (BBC Good Food, UK); not a test set. Gold-v1 will be a pilot/development set.
- Quantity agreement is on spans, overrides and replayed symbolic quantity; gold grams do not exist by design.
- A span present in only one file is categorised `entity_type`; a QUANTITY/UNIT span in any mismatch is `quantity` (documented in the module).
- The compiler's 3 development fixtures (GOLD-EX-001/002/003) are not part of pilot_20; compiler evaluation on Gold-v1 will therefore be the first non-contaminated number.

## Final answers
1. Gold recipes completed / 20: **0**
2. Independently double-annotated / 20: **0**
3. Adjudicated / 20: **0**
4. Major disagreement categories: **not yet measurable** (table categories fixed in advance, listed above)
5. Agreement metrics: **none yet** (tooling ready and tested on synthetic perturbations only)
6. Annotation contract stable enough for compiler evaluation: **cannot be determined yet**; it will be judged after the first agreement run (criteria: no category with systematic > 20% of spans/events in disagreement without a resolving rule; replay-consistent in 40/40 files after adjudication)
7. Recommended S102: **Kush and Parv each annotate the same first 5 recipes (one per stratum: R011207, R002919, R010532, R006967, R007017), run `tools/gold_cli.py validate` and `replay`, then ask for a partial agreement run on those 5** to expose handbook gaps before the other 15. (The agreement tool currently requires all 20; if you want a 5-recipe partial run, S102 adds a `--only` filter, otherwise do all 20.)
