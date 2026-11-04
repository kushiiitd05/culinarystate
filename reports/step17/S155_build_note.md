# S155 build note — Step 17a interfaces/validators/auditor and 17b Rung A baseline

2026-11-03. Branch `cloud/s155-step17ab`, stacked on `cloud/s154-step16-integration-2026-11-03`; merge S154 first.
Everything new is **DRAFT_PENDING_16c**, because hard gate 16c is still open.

Workflow under D-045: AI workers "ksh" and "prv" built and cross-reviewed the code, and the
coordinator verified the results. Kush and Parv review afterwards, and their review is final.
No step was annotated, signed or approved by an agent.

## Environment

The data bundle is absent from this container (the Drive host is denied by network policy),
so the real-data dry-runs were built and tested on synthetic records only. There are
**no real-data numbers in this note.** The protected ledgers are tracked in git, and the
baseline hash check passed (7/7).

## What was built

### Step 17a (worker ksh), `src/culinarystate/extraction/`

| Module | Content |
|---|---|
| `interfaces.py` | The six plan 17-M stages (`extract_mentions`, `link`, `parse_quantity`, `ground_quantity`, `build_events`, `resolve_refs`), typed results and the four explicit failure codes (UNRESOLVED, NO_VALID_CANDIDATE, PARSE_FAIL, NO_COMPATIBLE_RECORD). Every output carries rung_id, config hash, schema_version, claim_route and a source span. Each constructor enforces "a failure or a value, never both"; a selection can only come from the supplied candidates. |
| `quantity_stages.py` | Thin wrappers over the S154 rc2 parse/grounding. Nothing is reimplemented. |
| `validators.py`, `invariants.py` | V1 span round-trip, V2 schema, V3 vocabulary membership, V4 graph invariants: order, consumption, split fractions, and mass balance only when every term is known. |
| `auditor.py` | Invented-value auditor with an integer `invented_count`. A rule-traced value counts only if its rule is registered and recomputes it from the span text; grams are checked through the rc2 audit. |

### Step 17b (worker prv)

| File | Content |
|---|---|
| `rung_a.py`, `rung_a_lexicon.py`, `rung_a_rules.py`, `rung_a_binding.py` | Deterministic Rung A baseline: longest-match lexicon over the read-only ING/ALIAS/PROC/TOOL/UNIT ledgers; verb → PROC lookup; nearest-noun or recency binding; lexical and pronoun coreference (an ambiguous "it" gives UNRESOLVED); templates for combine, split, reserve and discard. claim_route INFERRED_RULE throughout. Pieces of the rule compiler are reused, not edited. |
| `rung_a_measure.py`, `tools/step17b_rung_a_synthetic_report.py` | Counts-only measurement, written to `reports/step17/rung_a_synthetic_counts.json` and labelled SYNTHETIC_NOT_GOLD. |
| `tools/step17b_rung_a_dryrun.py` | Read-only real-data dry-run over a seeded sample of 1,000 recipes, drawn by ranking sha256(seed‖recipe_id). `--seed` is required. It uses the S154 counts-only guards and the ledger baseline check. **Not run here.** |

### AI cross-review (prv on ksh), `reports/step17/S155_17a_ai_review.md`

Seven real defects were found. Each got a failing test before its fix (R1–R7):

| ID | Severity | Defect |
|---|---|---|
| R1 | HIGH | The auditor paired a number with a unit from a different part of the span: "Bake 20 minutes at 180C" passed as 180 minutes. |
| R2 | HIGH | The minus sign was lost: "-18°C" was read as +18. |
| R3 | | `config_hash` left out claim_route and annotation coverage. |
| R4 | | Ids referenced across outputs were never checked, so ghost ids passed. |
| R5 | | V3 skipped categoricals that had no vocabulary without reporting them as unchecked. |
| R6 | | Float offsets were truncated silently. |
| R7 | | A malformed event order crashed V4. |

Nine items are open (O1–O9). They are listed in block D of
`handoff/REVIEW_SHEET_AI_VERDICTS.md` and are pending Parv's review.

## Synthetic measurement (SYNTHETIC_NOT_GOLD)

| | Fixtures | Hard-case prompts |
|---|---|---|
| Texts / with events / events | 13 / 11 / 25 | 17 / 11 / 15 |
| Values audited | 257 | 137 |
| **invented_count** | **0** | **0** |
| V1–V4 issues | 0 | 0 |
| V4 undecided (fraction basis unspecified) | 2 | 1 |
| Exceptions | 0 | 0 |

These are engineering checks on synthetic inputs. They are not accuracy, gold or G17 gate
evidence. The G17.1 audit (at least 300 real outputs) still has to be run, on real data.

## Decisions recorded this session (as Kush's scribe)

- **D-045:** AI verdict first, then Kush and Parv review it, and their review is final. Labels are MODEL_ASSISTED.
- **D-046:** blocks W, A, B1–B5 and C1–C7 of the review sheet accepted. Parv's pass on S154 relayed by Kush.
  THR-19P-01..35 are signed in `registry/preregistered_thresholds_v1.csv`: 35 new rows matching the bound
  appendix hash `93d781cc…`, with no existing row edited.

## Verification

| Check | Result |
|---|---|
| New tests | 17a: 152; review fixes: 12; Rung A: 27; measurement and dry-run: 12 |
| Full unit suite (thread caps) | **2000 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors are missing bundle files, the same as the S154 baseline. |
| Pre-S155 files modified | DECISIONS.md and the threshold registry (append-only), the review sheet, and the S154 pilot test (now expects signed THR rows). No code module from before S155 was edited. |
| Ledgers / hard-case catalog | Unchanged (hash-checked in tests and by `verify_baseline`) |
| Attribution lines in commits | 0 |
| Files over 800 lines | 0 |

## Needs human

1. **Parv:** block D, covering the R1–R7 fixes, the O1–O9 decisions, the Rung A draft choices and the lexicon gaps.
2. **Kush:** run `python tools/step17b_rung_a_dryrun.py --seed <SEED>` and
   `python tools/step16_rc2_grounding_dryrun.py --workers 8` where the data exists, and review the counts.
3. **N1–N3** for the pilot (Kush's nonce; weekly hours and budget for each of you), so that the signed start record
   can be written (B6 / H5).
4. H4 / 16c: the draft tables, the mention-label set and the registry codes left open by 17a.
