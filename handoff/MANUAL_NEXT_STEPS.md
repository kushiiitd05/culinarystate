# MANUAL_NEXT_STEPS — human work for Kush + Parv (priority order)

Presentation 25–26 Nov 2026. Code is ready for each task; humans supply judgement. Never let AI fill these in.

| # | Task | Why (deliverable) | Input | Exact steps | Time | Who |
|---|---|---|---|---|---|---|
| 1 | Send professor email (RecipeDB/FlavorDB access) | unblocks RecipeDB crosswalk + NER reproduction | plan Part AS draft | review wording (H1), send | 15 min | Kush |
| 2 | Verify ≥ 40 literature rows | DEL-1 acceptance (currently 0/40) | `registry/evidence/verification_queue_ranked_v1.csv` (Route A first) | open paper → check each listed EVD row (matrix, state, process, T/t, before/after, unit, basis, table) → fill `human_status` (HUMAN_VERIFIED/HUMAN_REJECTED), `verifier`, `verified_at`, `notes` | ~10 min/paper; 8–10 papers each | both |
| 3 | Annotate Gold pilot (20 recipes) independently | DEL-3 Gold; handbook v1.1 | `annotation/gold/templates/*.TEMPLATE.json`, `annotation/annotation_handbook_v1.md` | copy template → `<id>.Kush.json` / `<id>.Parv.json`; annotate; `python tools/gold_cli.py validate <file>` until OK | 15–25 min/recipe | both |
| 4 | Adjudicate pilot | agreement numbers + handbook rules | both files per recipe | `python tools/gold_cli.py agree A B` → fill `annotation/adjudication/<id>.csv` together | 1 h/week | both |
| 5 | Tick FDC crosswalk (top ~300 HIGH) | sourced grams for ~25% more lines | `registry/ingredients/fdc_crosswalk_candidates_v0.csv` | set `human_decision` = ACCEPT / REJECT / other fdc_id | 1–2 h | Parv |
| 6 | Sign off allergen mapping | DEL-5 hard constraints | `registry/allergens/ing_allergen_review.csv` | `human_decision` = YES / NO / UNSURE per row | 45 min | Kush |
| 7 | Download FSIS safe-temperature chart in a browser | WARN food-safety rules | fsis.usda.gov safe temperature chart | save page as HTML/PDF into `data/raw/fsis/` | 2 min | Parv |
| 8 | Cite authorities for metric spoon / cup | UNIT records flagged NEEDS_SOURCE | `registry/units/unit_registry_v1.csv` | find standard/official source; add to notes | 20 min | either |
| 9 | Review ingredient registry rejects + polysemy | registry quality | `registry/ingredients/unresolved_high_frequency.csv`, `alias_collision_report.csv` | mark keep/drop/split | 30 min | either |
| 10 | Author benchmark questions (DEL-4/5) | ≥ 80 dev+test questions, 8 task types | template (coming) | write questions from scenarios; freeze hash before tuning | 3–4 h | both |
| 10b | Review 30 AI-drafted scripted sessions | DEL-3 contract: ≥ 30 sessions (currently 0 reviewed) | `annotation/sessions/SES-*.json`, `reports/del3/sessions_v1.md` | read each turn: are the events what the utterance implies? is the expected end state right? fix, then set `provenance.status` = HUMAN_REVIEWED + `reviewed_by`; `python tools/run_sessions.py` | ~5 min/session | both |
| 11 | Download FooDB CSV bundle in a browser (CC BY-NC 4.0) | compound concentrations per food (SSOT §175.3) | foodb.ca/downloads (refuses scripts, 403) | save the CSV tar.gz into `data/raw/foodb/`; tell Claude the file name | 5 min | either |
| 12 | Request a FoodAtlas bundle (CC BY-NC 4.0 since 2026-10-09) | X13 food–chemical evidence graph | foodatlas.ai downloads page (bot checkpoint; zips are private S3, pre-signed per key holder) | get the latest bundle zip via the site; save into `data/raw/foodatlas/`; record version + date | 10 min | either |

Rules: verification is recorded with the verifier's real name and date; disagreements go to adjudication; nothing is
edited directly in `ledgers/data/` — tools promote verified rows.
