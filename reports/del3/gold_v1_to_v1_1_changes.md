# Gold-v1 -> v1.1 (proposed): review gate, source audit and compiler rerun (S109)

**Status: AWAITING KUSH'S DECISIONS. Gold-v1.1 has NOT been created.** Every proposal is `AI_PROPOSED_CORRECTION`; none is `HUMAN_VERIFIED`. Gold-v1 (`pilot_20_adjudicated`) is unchanged; the provisional set `pilot_20_adjudicated_v1_1_proposed/` (status DRAFT) exists only to show the effect of accepting everything. Final `pilot_20_adjudicated_v1_1/` is written only by `tools/apply_gold_corrections.py` from rows Kush marks `approve`. The compiler is the same as in S107/S108 (`rule_compiler.py` unchanged).

Review material (local, contains source text): `annotation/gold/gold_v1_1_review_sheet.md` (per recipe: source, current vs proposed events, state effect) and `annotation/gold/gold_v1_correction_queue.csv` (decision / reviewer columns). Allowed decisions: APPROVE, REJECT, MODIFY, NEEDS_DISCUSSION.

## Queue (121 rows)
{'UNCONVERTED_EVENT+PADDED_REMAINDER': 1, 'UNCONVERTED_EVENT': 4, 'ANNOTATION_ERROR_FOUND_ON_AUDIT': 2, 'ANNOTATION_ERROR_FOUND_ON_AUDIT+UNCONVERTED_EVENT': 1, 'UNCONVERTED_EVENT+DOWNSTREAM_ARTEFACT': 2, 'DOWNSTREAM_ARTEFACT': 3, 'PADDED_REMAINDER+DOWNSTREAM_ARTEFACT': 1, 'PADDED_REMAINDER': 2, 'UNSUPPORTED_BY_SCHEMA': 1, 'COREF_SPURIOUS': 41, 'COREF_NONREFERRING': 1, 'COREF': 4, 'AUDIT_FLAG': 25, 'AUDIT_CORRECTION': 33}. Rows needing a decision: **95** (42 remove coreference noise, 4 set a genuine coreference, 49 are event/line corrections). 25 AUDIT_FLAG rows are information; each flag is classified in `gold_v1_full20_source_audit.md`; their fixes are separate proposal rows.

## Full source audit (20/20 recipes read against the source text)
18 recipes need substantive corrections, 2 only the coreference-noise removal, 0 are clean. Details and the per-recipe PASS/CORRECTION_REQUIRED table: `reports/del3/gold_v1_full20_source_audit.md`.
The audit changed the earlier picture: besides the 13 unconverted events, the draft has **lineage errors in most recipes** (wrong lot merged, set-aside items merged early, croutons built from soup, glaze built from batter), **9 ingredient lines whose ALTERNATIVE span is the word 'or'**, and an optional grill step recorded as an event.

## Coreference audit (113 draft mentions, corrected)
**78 are not references**: the draft matched the letters 'it' inside words ('with', 'little'). Genuine mentions: 35 = RESOLVABLE_EXPLICIT 2, RESOLVABLE_STRUCTURAL 4, NOT_APPLICABLE 1 (expletive 'it's important'), GENUINELY_AMBIGUOUS 28 (remain `UNKNOWN`; examples: 'the sauce' and 'the remaining butter' in a step with several candidate lots, 'the dough' after several merges). The S108 audit had counted these 78 as 'ambiguous' and proposed resolving some of them; that was wrong and is withdrawn: the S108 structural proposals are replaced by removal of the noise.

## Split / remainder audit (unchanged from S108)
3 converter problems, 1 annotation problem, 0 engine limitations; converter fixed and tested. No synthetic remainder remains in the proposed set.

## Compiler rerun (same compiler; n=20; Gold = proposed v1.1, i.e. IF EVERYTHING IS APPROVED)
| metric (P = raw text) | S107 (v1) | S108 proposed | S109 proposed | S109 O1 (gold concepts) | S109 O2 (gold Adds) |
|---|---|---|---|---|---|
| state-field accuracy | 0.102 | 0.140 | 0.132 | 0.132 | 0.132 |
| alive-entity F1 | 0.312 | 0.395 | 0.340 | 0.325 | 0.340 |
| merge/split/reserve F1 | 0.343 | 0.368 | 0.380 | 0.365 | 0.380 |
| relation F1 | 0.289 | 0.327 | 0.339 | 0.326 | 0.339 |
| event F1 (loose) | 0.199 | 0.237 | 0.245 | 0.235 | 0.245 |
Event counts gold -> predicted (S109 proposed): Merge 87 vs 60, Transform 94 vs 169, Split 19 vs 14, Transfer 21 vs 22, Discard 10 vs 10, Reserve 1 vs 8.
Gold-event replay (C) is 1.000 on every metric; no replay issue in 20/20 proposed files. Per-recipe numbers: `compiler_vs_gold_s109_proposed.json`. These are provisional until the corrections are approved.

## Reading the cascade
- Oracle ingredient identity still adds nothing material (state-field accuracy +0.000, alive F1 -0.015).
- The step-event construction remains the bottleneck: all structural metrics stay at about 0.34-0.38; the compiler writes about 1.8x the Gold Transform count and 8 Reserve events against 1.
- Reference cleanup moved P state-field accuracy 0.102 -> 0.132, alive F1 0.312 -> 0.340, merge/split 0.343 -> 0.380: the conclusions are stable across three versions of the reference.

## Oracle readiness
**GOLD_ORACLE_NOT_READY** - blocking rows: all 95 proposal rows are unreviewed; until Kush decides, Gold-v1 still contains the lineage errors above. Provenance when approved: AI-assisted + human-reviewed development Gold (not independent, not blind, not a test set).
