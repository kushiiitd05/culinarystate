# RUNBOOK — rebuild everything, in order

Python: `/opt/anaconda3/bin/python` (written `py` below). Run from the repo root. Every builder is idempotent:
a second run prints `unchanged` / `{}` writes. If a second run writes anything, that is a bug — stop and log it.

## 0. Check
```bash
py -m pytest -q                      # all tests must pass
py -m pytest -q -m ledgers           # integration over real ledgers: release audit, retrieval regression, e2e (~40 s)
git status                           # clean before a rebuild
```

## 1. Raw acquisition (network; cached, safe to re-run)
| Step | Command | Writes (git-ignored) |
|---|---|---|
| USDA R6 | `py tools/ingest_usda_r6.py` | data/raw/usda_r6 + EVD/COND/SRC |
| Phenol-Explorer | `py tools/crawl_phenol_explorer.py && py tools/ingest_phenol_explorer.py` | data/raw/phenol_explorer |
| Bognár 2002 | `py tools/ingest_bognar.py` | data/raw/bognar (PDF + pdftotext) |
| Wikibooks | `py tools/crawl_wikibooks.py` | data/raw/wikibooks/api, data/interim/wikibooks |
| Gutenberg | `py tools/crawl_gutenberg.py` (~2 h, mirror 2 s/req) | data/raw/gutenberg/texts |
| FoodOn / OFF | downloaded inside their builders (pinned URL/commit) | data/raw/foodon, data/raw/off |
| A1 BBC corpus | not re-scraped; read from `../a1/A1 3/data/` | — |

## 2. Ledger build order (dependencies matter)
Builders own specific fields and preserve fields owned by others (see "Field ownership").
```bash
py tools/build_unit_registry.py
py tools/build_ingredient_registry.py      # ING/ALIAS from A1 (+ merges duplicate spellings)
py tools/ingest_wikibooks.py               # REC family 2, new ING from editor links, aliases
py tools/build_foodon_crosswalk.py         # ING.crosswalks.foodon + category
py tools/build_off_aliases.py              # ING OFF/Wikidata refs + multilingual aliases
py tools/build_process_registry.py         # PROC
py tools/link_evidence.py                  # EVD -> ING/PROC links, PROC.evidence_coverage
py tools/build_tool_registry.py            # TOOL + PROC.tool_ids (BBC + Wikibooks steps)
py tools/build_tool_wikidata.py            # TOOL Wikidata refs
py tools/build_recipe_registry.py          # REC family 1 (BBC) + families
py tools/ingest_gutenberg.py               # REC family 3 (public-domain books)
py tools/build_molecule_registry.py        # MOL / IMAP
py tools/build_allergen_registry.py        # ALLERGEN (FSSAI)
py tools/build_fdc_crosswalk.py            # FDC candidates (CSV only, D-006)
py tools/build_kg_edges.py                 # KGE concept edges (needs everything above)
py tools/ingest_flavorgraph.py             # MOL (by InChIKey) + IMAP PRESENCE + KGE ING_CO_OCCURS|FLAVORGRAPH (X9)
py tools/ingest_chemtastesdb.py            # KGE MOL_HAS_TASTE for MOL with a PubChem CID (X11; after FlavorGraph)
py tools/reextract_conditions.py           # Phenol-Explorer COND after extractor changes
py tools/ingest_bognar_yields.py          # Bognár Part-1 weight yields -> EVD yield_factor (after ingest_bognar)
```
External sets (no ledger writes): `py tools/eval_tasteset.py` (X10 NER floor), `py tools/build_openpi_food.py` (X12),
`py tools/build_fdc_pairs.py` (X15 raw/cooked pairs vs R6).
Run steps 2–19 twice; the second pass must write nothing.

## 3. Evidence review + reports
```bash
py tools/precheck_route_a.py               # DOIs + AI pre-check + human review pack (never overwrites human input)
py tools/apply_human_review.py --dry-run   # then without --dry-run, after humans fill the pack
py tools/build_verification_queue.py
py tools/del1_data_card.py && py tools/eda_report.py
py tools/run_del2.py --source USDA-RETN-R6 --n-boot 100
py tools/run_del2.py --source PHENOL-EXPLORER-3.6 --n-boot 100 --log-target
py tools/run_del2.py --source BOGNAR-2002 --n-boot 100
py tools/run_cross_source.py && py tools/register_experiments.py
py tools/build_fdc_pairs.py                # X15 raw/cooked pairs vs R6 (after ingest_bognar_yields for yields)
py tools/run_sessions.py                   # DEL-3 scripted sessions (counts HUMAN_REVIEWED only)
py tools/ask.py --demo                     # DEL-5 rule baseline: gate -> slots -> packets -> feasibility -> decision
```

## 4. Field ownership (who may write what)
| Record field | Owner |
|---|---|
| ING core (name, parents, frequency) | build_ingredient_registry / ingest_wikibooks (own concepts) |
| ING.crosswalks.foodon, ING.category | build_foodon_crosswalk |
| ING.external_refs OFF:/WIKIDATA: | build_off_aliases |
| PROC.tool_ids | build_tool_registry |
| PROC.evidence_coverage | link_evidence |
| TOOL.external_refs WIKIDATA: | build_tool_wikidata |
| EVD.matrix.ingredient_id, process ids | link_evidence |
| EVD.verification AI_PRECHECKED | precheck_route_a · HUMAN_* only via apply_human_review |
| KGE (agent kg_edges@0.1) | build_kg_edges (deprecates stale edges) |

## 5. Logging + commit
```bash
py tools/log_step.py --block <X/DEL> --title "..." --did "..." --files "..." --verify "..." --next "..."
git add -A && git commit -m "<type>: <summary>"      # local only; no push before H7
```
