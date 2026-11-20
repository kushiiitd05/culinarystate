# D1 — 40 literature rows: AI pre-check for human audit

**`AI_DELEGATED_D085` · `AI_PRECHECKED` · `NOT_HUMAN_VERIFIED`** · 17 Nov 2026 · personas, not people.
Contract clause: *"≥40 hand-verified literature rows (raw-vs-cooked, kinetics)"*.
**The ledger's human-verified count is 0 and this packet does not change it.** Nothing here is a
verification. It is triage so that Kush and Parv audit instead of starting cold.

File: `D1_literature_rows_precheck.csv` — 127 rows; the 40 to audit are `selected_40 = YES`
(`audit_no` 1–40), the other 87 are `RESERVE` (swap one in when a selected row cannot be opened).
Built by `D1_build_precheck.py`, selection seed **181**.

## What the 40 are

| Block | Rows | Kind | Source held? |
|---|---|---|---|
| AAP-001…016 | 16 | **kinetics** — ascorbic-acid rate constants / activation energies, 4 papers (rosehip nectar, watermelon juice, mango, fig juice) | PDF + text in `data/raw/aa_pilot/` |
| Andlauer 2003 | 12 | **raw-vs-cooked** — zucchini, carrot, green bean, potato; 3 rows per food, seeded | open author's version (URL in the row); fetched to session scratch, not stored in the repo |
| 12 other papers | 12 | raw-vs-cooked / storage / canning, one row per paper, seeded | **not opened by the agent** |

Honest caveat on the first block: the 16 AA rows live in the AA-pilot calibration sheet
(`annotation/aa_pilot/aa_pilot_verify_CAL_v1_Kush.csv`), **not in the EVD ledger**. They are literature
kinetics rows of the kind the contract names, but if the humans decide the 40 must all be EVD-ledger
rows, replace them with RESERVE rows (48 further Andlauer rows are in RESERVE, most with a table comparison already done).
That is a human call; it is not decided here.

## What the AI actually did — selected 40

| Resolved AI pre-check (ksh governs, D-139) | n |
|---|---|
| `MATCHES_SOURCE` — figure found in the opened source | 21 |
| `DIFFERS_FROM_SOURCE` — opened, recorded value differs | 2 |
| `AMBIGUOUS` — source opened, could not settle by rule | 5 |
| `SOURCE_NOT_ACCESSIBLE` — primary paper not opened | 12 |

So **28 of 40 were compared against an opened source (23 with a definite outcome), 12 could not be.**
For the 12, nothing is asserted about what the paper says. Reasons are in the row: two hosts returned
HTTP 403 to a plain request and were not retried; the rest are publisher or repository landing pages
that need a human browser. No access control was worked around.

Personas on the 40: ksh judged 40, prv judged 40, chef (AI persona, D-085) gave an opinion on 8 and is
`NOT_APPLICABLE` on 32. ksh and prv differ on 12 rows; chef differs from ksh on 7.

## Look at these first

1. **Potato / caffeic acid rows (EVD-008319…008328; two are in the 40: EVD-008323, EVD-008327).**
   The source's Table 6 is headed *"mg in 500 g fresh weight"*; the ledger's mg/100 g values equal the
   table figures divided by **300 g**, not 500 g (e.g. sample 1: paper 4.5 mg/500 g = 0.90 mg/100 g;
   ledger 1.5). All ten potato caffeic-acid rows show the same pattern. The after/before ratio, and so
   the retention factor, is unaffected. ksh: `DIFFERS_FROM_SOURCE`; prv: `AMBIGUOUS` (ratio right, basis
   wrong). The error may be Phenol-Explorer's own conversion rather than this project's import — the
   agent did not compare against the Phenol-Explorer page. Table 6's rows are also unnumbered, and the
   source says different tubers were used raw and cooked.
2. **chef vs ksh, 7 rows (Andlauer small-water arm).** The value matches, but the ledger calls the
   process "boiled / cooked in boiling water at 100 °C" while the paper cooked 300 g of vegetable with
   30–50 mL of water — a cook would call that sweating or steaming. This is a condition-label question,
   not a value question.
3. **AAP-010…012 (mango).** The number is in the source row; which of the two columns is L-ascorbic
   acid was not re-read from the table header. One look at Table 2, p.255 settles all three (and AAP-013).
4. **prv flags on AAP-006…009 and AAP-014…016.** Numbers match; prv questions what they mean (iodine
   titration is not ascorbic-acid specific; fig-juice k barely moves between 30 and 90 °C). An earlier
   AI closeout of these 16 rows (`reports/s179/ksh_CAL_source_review_closeout_2026-11-13.json`) found
   the numbers consistent and corrected metadata on all 16; read it alongside.

## Auditing one row in under two minutes

1. Open the row's `local_copy` if there is one, otherwise `url` (or `https://doi.org/<doi>`).
2. Go straight to `source_locator` (table and row are given where the agent could determine them).
3. Read `what_ai_checked` — it states the arithmetic (e.g. "27.1 mg / 300 g = 9.033 mg/100 g").
   Confirm the table cell, the unit header, and that the sample/condition is the one in
   `conditions_as_recorded`.
4. Write **your own** verdict in `kush_HUMAN_verdict` or `parv_HUMAN_verdict`: `CONFIRM`, `CORRECT`
   (put the paper's value in `human_note`) or `REJECT`. Put where you saw it in `human_locator`
   (e.g. `Table 3, row 1`). `chef_HUMAN_verdict` is for a human cook only, if one is consulted on the
   process label.
5. `SOURCE_NOT_ACCESSIBLE` rows take longer (a cold check, ~3 min); if a paper is paywalled, skip it
   and take the next RESERVE row.

Do not copy an AI column into a human column. Agreeing with the AI is a judgement you make after
looking at the source.

## What counts as verified

A row counts toward the 40 only when **a human (Kush or Parv) opened the primary paper, found the
value at a stated locator, and wrote CONFIRM or CORRECT with their name and date.** Under the existing
procedure (`handoff/EVIDENCE_REVIEW_GUIDE.md`) the result is applied with
`tools/apply_human_review.py`, whose input is `registry/evidence/human_review_pack_v1.csv` (columns
`human_decision`, `paper_locator`, `verifier`, `verified_at`). This packet does not write to that file;
for EVD rows the humans transfer their decisions there. The AA rows have their own sheet with
`verdict` / `verifier_comment` columns. An AI `MATCHES_SOURCE` is never a verification, and neither is
a `resolved_AI_precheck`.

## Limits of this pass

- Text was machine-extracted from PDFs; table cells were matched by rule with a 0.01 rounding tolerance.
- The Andlauer copy is the author's version, not the journal's typeset article; page numbers differ.
- Two personas of one model share a prior. The ksh/prv agreement rate is not inter-rater evidence and
  must not be reported as one.
- 12 of the 17 source papers in the 40 were not opened at all.
