# EVIDENCE REVIEW GUIDE — the 40 hand-verified literature rows (DEL-1)

**Who:** Kush and Parv (only humans can sign; the validator rejects any other verifier name).
**Why:** DEL-1 contract = "≥ 1,000 rows from public retention DBs (done: 10,888) **+ ≥ 40 hand-verified literature rows**" — the only DEL-1 clause still open.
**Time:** ~2–3 min per row → 40 rows ≈ 1.5–2 h total, split between you (20 each).

## What the AI already did (status `AI_PRECHECKED`, not verification)
- Resolved DOIs for 121/125 Phenol-Explorer papers (Crossref, strict title+year match); 15 are open access.
- Rule-checked all 3,870 imported rows: 3,791 `LIKELY_CONFIRM`, 79 `CHECK_VALUES` (RF ≠ values × yield).
- Picked 55 rows (40 MAIN + 15 RESERVE) from the 15 open-access papers — max 5 rows/paper, distinct compounds.

## Your file
`registry/evidence/human_review_pack_v1.csv` (open in Excel/Numbers/Google Sheets; save back as CSV).

## Per row (≈ 2 min)
1. Open `paper_link` (or `https://doi.org/<paper_doi>`).
2. Find the sample described in `sample_after_processing` and the `compound`.
3. Compare `before_value` (raw food) and `after_value` (processed). Phenol-Explorer may have **converted units**
   (e.g. paper mg/kg dry weight → mg/100 g fresh weight). Same ratio after/before = OK.
4. Fill:
   | column | value |
   |---|---|
   | `human_decision` | `CONFIRM` (values + conditions match) · `REJECT` (wrong sample/compound/not in paper) · `CORRECT` (paper gives a different value) |
   | `paper_locator` | where you saw it, e.g. `Table 2, p.4` (**required for CONFIRM**) |
   | `corrected_after_value` | only for CORRECT |
   | `verifier` | `Kush` or `Parv` exactly |
   | `verified_at` | `2026-10-19` (YYYY-MM-DD) |
   | `human_notes` | optional |
5. If a MAIN row cannot be checked (paywall/figure only), leave it blank and do a RESERVE row instead.

## Apply (one command)
```bash
cd ~/Desktop/CGAS/culinarystate
/opt/anaconda3/bin/python tools/apply_human_review.py --dry-run   # shows problems, writes nothing
/opt/anaconda3/bin/python tools/apply_human_review.py             # writes
/opt/anaconda3/bin/python tools/del1_data_card.py                 # DEL-1 clause turns ✅ at 40
```
CONFIRM creates a new EVD row (tier E1/E2, `HUMAN_VERIFIED`, your name + locator) that mirrors the imported row;
the imported E3 row is kept, same study lineage, so nothing is double-counted.

## Other review files (lower priority, optional)
| File | What | Rows |
|---|---|---|
| `registry/evidence/route_a_paper_precheck.csv` | paper-level AI summary | 125 |
| `registry/evidence/verification_queue_ranked_v1.csv` | all candidate papers (Route B = new papers to extract later) | 634 |
| `registry/evidence/evd_ingredient_link_review.csv` | foods the linker could not map to an ingredient | 94 |
| `registry/ingredients/fdc_crosswalk_candidates_v0.csv` | ingredient ↔ USDA FDC candidates (`human_decision`) | — |
| `registry/allergens/ing_allergen_review.csv` | ingredient ↔ FSSAI allergen group | — |
