# Step 19 deep-gold pilot, wave P1: closeout (DRAFT)

Status: **AI_DRAFTED, counts only** (board item T3-C15-R1). This is the coding agent's summary of committed records.
It is not a human statement, approval or signature (D-071). Where a human decided, the decision is cited by its
D-number and quoted only from `DECISIONS.md`. Written 2026-11-10 on `kush/s179-finish-fixes`.

Sources:
- `reports/step19/p1_agreement_counts_S166.json` (record STEP19_P1_AGREEMENT_COUNTS, status
  AI_ENGINEERING_SCORE_COUNTS_ONLY);
- `reports/step19/sp_stamp_proposal_ksh_S168.md`;
- `reports/step19/P1b_design_amendment_PROPOSED.md`;
- `DECISIONS.md` D-069 and D-070;
- `registry/negative_results_register_v1.csv` NEG-0038.

## 1. Verdict

**Handbook gate: HANDBOOK_REVISION_REQUIRED.** This is a negative result, recorded as NEG-0038 (status
DRAFT_PENDING_H4).

The gate (THR-19P-16 / -31) requires per-pair disagreement of 0.20 or less in every category. Five of the nine
categories exceed it.

| Category | Per-pair disagreement rate | Over 0.20 |
|---|---:|:---:|
| coref | 0.956 | yes |
| final_state | 0.817 | yes |
| event_type | 0.763 | yes |
| entity_type | 0.236 | yes |
| event_argument | 0.227 | yes |
| canonical_identity | 0.105 | no |
| quantity | 0.080 | no |
| boundary | 0.032 | no |
| intermediate_identity | 0.000 | no |

The SP-002 sensitivity run normalised U+2044 at scoring time and left the labels unchanged. It gives the same
verdict, the same flagged categories and the same means.

## 2. Label basis (read before any number)

- **label_basis = HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND.** The two annotations of each recipe began as AI drafts,
  which a human then accepted. They are not two blind human annotations.
- The scores therefore measure how far two AI-drafted, human-accepted passes agree. They are **not** inter-annotator
  reliability, and they are not a human gate (`counts_as_human_gate = false`).
- Size: 7 annotator pairs, all 7 replayed. Denominators: 881 spans, 226 coreference links, 194 events, 71 state
  fields, 57 lines. The commitments on the sealed keys were verified (`key_commitments_verified = true`).

## 3. Mean agreement (7 pairs, descriptive)

| Measure | Mean |
|---|---:|
| spans, exact F1 | 0.843 |
| spans, relaxed F1 | 0.880 |
| concept agreement | 0.904 |
| coref B³ F1 | 0.836 |
| intermediate-entity F1 | 0.818 |
| process-link F1 | 0.798 |
| structural-relation F1 | 0.749 |
| relation F1 | 0.665 |
| alive-entity F1 | 0.619 |
| event F1, loose | 0.599 |
| event F1, strict | 0.559 |
| state-field agreement | 0.264 |
| UNKNOWN disagreement rate | 0.048 |

With n = 7 pairs, no interval is narrow enough to support a reliability claim. The report states these as
descriptive only.

## 4. Schema-problem triage (SP-001..SP-004)

The four logged problems were triaged in ksh's proposal (an AI persona) and stamped by Kush in D-070 O2:

| SP | Stamp | Class | Route |
|---|---|---|---|
| SP-001 | WORKAROUND | SCHEMA_GAP | 16A (step-named food kept as UNKNOWN coref) |
| SP-002 | WORKAROUND | TOOLING | parser fix: U+2044 normalised in the adapter, `grammar.py` untouched; implemented after the presentation (D-070 O1) |
| SP-003 | WORKAROUND | HANDBOOK_GAP | Addendum B (partial-use rule) |
| SP-004 | WORKAROUND, with BLOCKING risk noted | SCHEMA_GAP | 16B (alternatives) |

THR-19P-25 (100 % triage) is satisfied per D-070. The SP-002 scale is measured: 1,275,782 of 4,281,956 corpus
ingredient lines contain U+2044 (29.8 %, almost all Food.com; D-069).

The proposal also leaves a residual risk on record. SP-001 and the final_state rate (0.82) both concern state, so
the 16A decision rests on two packets only.

## 5. What P1b would test

Per `P1b_design_amendment_PROPOSED.md` (D-069 "P1b yes"; the design still needs Kush's signature):
- **What:** 3-4 new PRIMARY recipes across the same 7 strata, excluding every P1 recipe and group.
- **Question:** whether the five Addendum B categories fall to 0.20 or below under the stamped Addendum B (D-070 O3).
  It uses the same scorer and gate.
- **Reading:** a handbook calibration check, not reliability evidence. P1b labels are again human-accepted AI drafts,
  and both annotators have seen the P1 disagreements.
- **P1 labels are never edited or re-scored.**
- **Human inputs still missing:** the recipe count, a new pre-frame nonce written by Kush, a signed amendment to the
  start record (H5 authorisation and budget for wave P1b), and who annotates B.

## 6. How the final report may use P1

- **Allowed:** "the P1 pilot found that handbook v1 needs revision: five of nine categories exceeded the 0.20
  disagreement gate on 7 AI-drafted, human-accepted pairs."
- **Not allowed:** any statement that the gold is reliable, validated or inter-annotator agreed.
- **D3 state tracking:** any comparison of D3 to P1 gold carries this label basis and "NOT INDEPENDENT" (T3-C11-R1).
