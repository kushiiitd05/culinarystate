# pilot_20 — independent double annotation (Kush and Parv)  ·  STATUS: BLOCKED_HUMAN until both folders are DONE

Read first: `annotation/annotation_handbook_v1.md` (incl. **Addendum A**), `annotation/annotation_checklist.md`,
`annotation/hard_examples.md`, `annotation/UNKNOWN_examples.md`, worked examples `annotation/examples/GOLD-EX-00{1,2,3}.Kush.json`.

**Your files:** Kush → `annotation/gold/pilot_20/Kush/<id>.Kush.json` · Parv → `annotation/gold/pilot_20/Parv/<id>.Parv.json`
(20 recipes each; ids in `annotation/gold/pilot_20_manifest.csv`; same 20 recipes, hard ones included, none swapped).
Blank copies hold only the raw text (`status: DRAFT`). Nothing is pre-labelled.

**Rules:** annotate alone, no LLM pre-fill, do not open the other folder, UNKNOWN when the text does not say, never force an ID.
Set `"status": "DONE"` only when the recipe is finished and `validate` prints OK. About 15–25 min per recipe.

## Commands (run from the repo root, `/opt/anaconda3/bin/python`)
```bash
# 1. validate one file (offsets, schema, events, replay with no issues)
/opt/anaconda3/bin/python tools/gold_cli.py validate annotation/gold/pilot_20/Kush/R002919.Kush.json

# 2. replay your annotation and read the final state it produces (alive entities, qty, fields, location, edges)
/opt/anaconda3/bin/python tools/gold_cli.py replay annotation/gold/pilot_20/Kush/R002919.Kush.json

# 3. (only after BOTH folders are fully DONE) agreement for all 20 recipes -> pilot_20_agreement.json + pilot_20_disagreements.csv
/opt/anaconda3/bin/python tools/gold_pilot_agreement.py
#    prints BLOCKED_HUMAN and exits 2 while any of the 40 files is not DONE+valid

# single-recipe comparison (writes annotation/adjudication/<id>.csv)
/opt/anaconda3/bin/python tools/gold_cli.py agree annotation/gold/pilot_20/Kush/R002919.Kush.json annotation/gold/pilot_20/Parv/R002919.Parv.json
```

## Adjudication (after the agreement run; Kush and Parv together)
Fill `adjudicated`, `rationale`, `handbook_rule` in `annotation/gold/pilot_20_disagreements.csv` (template: `annotation/adjudication_template.csv`).
Write one `annotation/gold/pilot_20_adjudicated/<id>.ADJUDICATED.json` per recipe (`annotator: "ADJUDICATED"`). Never edit either original file.
A rule that recurs 3+ times becomes handbook v1.1, logged in WORKLOG; originals are not retro-fitted.

## What AI may do
Explain the handbook, run `validate` / `replay` for formatting, run the agreement tool after both passes exist.
What AI may not do: sign as Kush or Parv, fill or complete a file, copy one annotator's labels into the other's, or adjudicate.
