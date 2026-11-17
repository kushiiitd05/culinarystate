# Human audit packets — D1, D3, D5 (s181)

**`AI_DELEGATED_D085` · `AI_PRECHECKED` · `NOT_HUMAN_VERIFIED`** · 17 Nov 2026. Three AI personas (`ksh`
structure, `prv` food science, `chef (AI persona, D-085)` working cook; one model) pre-reviewed each gap,
with ksh governing on divergence (D-139). Every human column and block is empty. Nothing here closes a
gap; it shortens the human work. Freeze is 19 Nov.

| Do in this order | Packet | Who | Human time |
|---|---|---|---|
| 1 | **D1** `D1_literature_rows_precheck.csv` + `D1_README.md` — 40 rows (`selected_40 = YES`), 87 reserves | Kush + Parv, 20 rows each | ~60–80 min total (28 rows have locator + arithmetic ready, ~2 min each; 12 are cold, ~3–5 min) |
| 2 | **D5** `D5_peer_review_packet.md` — 8 scenarios, verbatim output (`D5_demo_run_2026-11-17.json`) | one human chef (+ up to two peers) | ~20–30 min per reviewer; ~15 min for Kush to find and brief the chef |
| 3 | **D3** `D3_gold_status.md` | Kush (P1-A label, 10 min); Kush or Parv (spot-audit of 10 gold recipes, 45–60 min) | ~1 h |

D1 first because it is the single clearest contractual gap and only Kush and Parv can do it. D5 second
because it depends on someone outside the team. D3 last because its metrics already exist; only the
wording and the label of the gold are at stake.

## What to look at first

1. **D1 potato caffeic-acid rows** (EVD-008323, EVD-008327 in the 40; ten rows in all): the values in
   the ledger equal the paper's "mg in 500 g" figures divided by 300 g. Ratio unaffected. Possibly a
   Phenol-Explorer conversion, not ours — check the PE page too.
2. **D5 scenarios where chef (AI persona) disagrees with ksh**: SAFETY, METADATA, RECIPE-SEARCH,
   SUBSTITUTION, RETENTION. chef marks SUBSTITUTION and RETENTION `NOT_ACCEPTABLE` as advice. Also
   DEMO-PHYSICS: its record shows 4 displayed numbers but the captured answer is the plain abstention
   sentence — a human should look at what was displayed.
3. **D3**: the compliance matrix says the 40-recipe evaluation was not performed; it was, on
   non-independent dev gold. P1-A files say "awaiting Kush review" while the report calls them
   human-accepted.

## Sentence the report may use

Full three-state wording, with blanks, is in `REPORT_WORDING.md`. In short:

| Gap | If humans do it | If they do not |
|---|---|---|
| D1 | "<n ≥ 40> literature rows were hand-verified by <names> on <date> … <c> confirmed, <k> corrected, <r> rejected." | "No row has been verified by a human, so the ≥40 hand-verified rows required by the proposal are not met." |
| D3 | dev-gold sentence plus "<names> re-read <n> of the 40 gold recipes … agreed with <a> of <f> state fields." | "Evaluated on 40 AI-drafted, author-accepted development gold recipes (not independent) … 11–20 % of final state fields." |
| D5 | "Reviewed on <date> by <role> … agreed with <a> of 8 AI pre-review judgements and overturned <o>." | "Pre-reviewed by three AI personas … This is not the chef/peer review named in the proposal, which was not performed." |

## Files

`D1_literature_rows_precheck.csv`, `D1_README.md`, `D1_build_precheck.py` (seed 181; rebuild needs the
Andlauer author's PDF converted with `pdftotext -layout`, passed as the argument) ·
`D5_peer_review_packet.md`, `D5_demo_run_2026-11-17.json` · `D3_gold_status.md` · `REPORT_WORDING.md`.
Nothing under `src/`, `registry/`, `ledgers/` or any existing report was changed. No commit.
