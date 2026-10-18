# STATUS — CulinaryState (Group 17 · Kush Tokas + Parv Goyal)

**Updated:** 2026-10-18 12:20 IST (after S029) · **Final presentation: 25–26 Nov 2026 (T-38 days)**
**Repo:** `~/Desktop/CGAS/culinarystate` (local git; GitHub push only after H7 approval)
**Step-by-step log:** `WORKLOG.md` (timestamped, sequential). **Decisions:** `DECISIONS.md`.
**Bible:** `docs/SSOT/…v15_0.md` (read via `docs/SSOT_INDEX.md`) · plan `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md`

## 1. COMPLETE
| Item | Evidence |
|---|---|
| SSOT v15.0 + Master Plan v4.0 + R&D plan v2 + Max prompt v2 | `docs/SSOT/`, `docs/plan/` |
| Course proposal (DEL-1…DEL-5 contract) | `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf` |
| A1: 11,934 BBC Good Food recipes scraped + ingredient NER (local only) | `../a1/A1 3/data/` |
| A2: frequent itemsets vs random controls; A3: copy-mutate evolution models | `../A2/`, `../A3/` |
| Research notes R1–R5 + verified references | `../research/`, `../cgas_salvage/` |
| SSOT index — all Appendix-1 counts match (30 RQ16, 14 G16, 18 G15 …) | `docs/SSOT_INDEX.md` (S003) |

**Not on this machine:** Parv's Max-plan work (old STATUS/DECISIONS, ~519 evidence candidate cells). Decision D-001: rebuild here; Parv continues from this repo.

## 2. DONE TODAY (S001–S029, see WORKLOG.md)
- Ledgers live & linked: SRC/SNAP/MEAS/STUDY, EVD 10,888 (USDA 7,018 + Phenol-Explorer 3,870 / 125 papers), COND, SVAR, ING 1,997 + ALIAS, PROC 148, TOOL 76 (+535 process↔tool links), UNIT 74, REC 11,934 (+families, REC↔ING), MOL 131, IMAP 592, ALLERGEN 8 (FSSAI).
- Code: schemas+laws, quantity grammar (90% lines), state engine + rule baseline, common scorer, gold toolchain + handbook, EDA generator, DEL-1 data card, DEL-2 pipeline (D0–D7), retrieval core (BM25 + compatibility + Evidence Packet), literature queue (634 rows), handoff docs. 265 tests.
- Results: DEL-1 4/6 clauses (0/40 human-verified rows). DEL-2 USDA: learned models win on random splits, gains vanish on cold splits; conformal coverage 0.72–0.87 under shift. DEL-2 PE: outlier-dominated → needs log-RF/median metrics (next).

## 2b. NEXT (in order)
1. AI pre-check pass over verification queue (AI_PRECHECKED + suggested decision) → humans confirm fast (Kush asked AI to review; AI cannot sign as human).
2. DEL-2 on PE with log-RF target + median AE; experiment cards EXP-D0…D7.
3. Dense embeddings + DEL-4 calibration/abstention eval (A100 — ask VPN first).
4. DEL-5 decision layer (ANSWER…ABSTAIN) + benchmark authoring (confirm D-008).
5. NER baselines on TASTEset (A100 encoder), Silver factory scaffold, B03/B15 small reproductions, WARN (after FSIS manual download).

## 2c. EXPANSION QUEUE (D-009, sequential)
| # | Source | Feeds | State |
|---|---|---|---|
| X1 | FoodOn ontology (CC BY 4.0) | ING external ids + category | ✅ S031: 534 LINKED + 287 CANDIDATE (75% of mentions), 572 categorised |
| X2 | Open Food Facts ingredient taxonomy (ODbL) | ALIAS (multilingual, Hindi), ING refs | ✅ S032: 835 ING linked (81% mentions), +1,770 aliases (14 langs), 560 Wikidata QIDs |
| X2b | ING duplicate merge (plural / "X cheese") | ING, ALIAS, downstream links | ✅ S033: 49 superseded → 1,951 active; 0 dangling refs |
| X3 | Wikibooks Cookbook (CC BY-SA, API) | REC source family 2 (world + Indian) | ✅ S034: +3,676 REC (143 Indian), 97.7% lines linked, +97 ING, +155 aliases, 49k silver NER spans |
| X3b | Wikibooks equipment (130) + technique (81) pages | TOOL / PROC crosswalk + new entries | next |
| X4 | Project Gutenberg cookbooks (public domain) | procedures, TOOL, PROC coverage | queued |
| X5 | Bognár 2002 retention/yield tables (open access PDF) | EVD source family 3 → source-disjoint DEL-2 | queued |
| X6 | Wikidata kitchenware (CC0) | TOOL QIDs + new tools | queued |
| X7 | recipe-scrapers on robots-allowed sites | REC (Indian focus) | queued (needs `pip install recipe-scrapers`) |
| X8 | SOTA ingredient NER (A100, VPN) | ING mentions across all REC sources | queued |

## 3. BLOCKED / WAITING
| Blocker | Impact | Workaround |
|---|---|---|
| RecipeDB / RecipeDB3 API key + licence (Prof. Bagler) | RecipeDB3 NER reproduction; RecipeDB name crosswalk | A1 BBC corpus + TASTEset for NER; `UNRESOLVED_EXTERNAL` crosswalks (AH2) |
| FlavorDB bulk access | molecule ↔ ingredient joins | PubChem PUG-REST (open) + FooDB downloads; FlavorDB later |
| Human verification (Kush/Parv) | E4 rows, Gold recipes, benchmark labels | queues + handbooks ready to work through, no waiting on code |
| rdkit missing in all conda envs | ECFP/Tanimoto | `pip install rdkit` into `recsys_env` (ask before installing) |
| GitHub repo creation (H7) | collaboration | local git; Parv clones from zip/remote once approved |

## 4. DATED PLAN TO PRESENTATION
| Week | Dates | Must exist at end of week |
|---|---|---|
| W1 | 18–24 Oct | ledgers+validators; DEL-1 v0 ≥1,000 DB rows; quantity v0; state-engine core; scorer skeleton; annotation handbook v1 |
| W2 | 25–31 Oct | DEL-1 v1 + data card + EDA; verification queue (humans verify ≥40 lit rows); ingredient/process registry v1; DEL-2 splits + D0–D5 scripts; Gold pilot 20 recipes (humans) |
| W3 | 1–7 Nov | DEL-2 runs + CIs; DEL-3 engine on 40 Gold recipes + 30 scripted sessions; BM25+dense retrieval + compatibility |
| W4 | 8–14 Nov | DEL-4 calibration/abstention eval; DEL-5 decision layer; benchmark ≥80 Qs authored + frozen |
| W5 | 15–21 Nov | DEL-5 B0–B5 ladder + ablations; 8-scenario demo; claims review |
| W6 | 22–24 Nov | slides, report, rehearsal, buffer → **present 25–26 Nov** |

## 5. NEXT 20 HIGHEST-VALUE TASKS (in order)
1. Core ledger JSON Schemas (SRC…CLM) + ID minter + validators + unit tests (P2)
2. EVD-/COND-/SVAR-/MEAS-/STUDY- evidence schema with AH1 origin_type rules (P1/P2)
3. Acquire USDA Retention Factors R6 → EVD rows (E3) + SNAP/API records (DEL-1)
4. Acquire Phenol-Explorer retention/processing data → EVD rows (E3) (DEL-1)
5. Literature candidate harvest (OpenAlex/Crossref, bounded) → `verification_queue_ranked_v1.csv`, `conflict_queue.csv`, `rejected_candidates.csv`, `evidence_precheck_report.html` (P1)
6. Quantity grammar + unit map (UNIT/QNT) + POR records + "no invented grams" property tests (P3)
7. Ingredient registry v1 + alias registry + collision report + coverage curve from A1 corpus (P3)
8. Process registry v1 from A1 instruction verbs + coverage (P3)
9. Event-sourced state engine: INST/EVT/STATE/REF/GRAPH + replay + merge/split/reserve fixtures (P6, DEL-3)
10. Gold annotation handbook v1 + gold schema + agreement.py + hard/UNKNOWN examples (P4)
11. Common scorer: span F1 (exact/relaxed, macro), linking Acc@1/R@5, event/relation F1, state-graph metrics (P5)
12. Reusable EDA report generator across all ledgers (P14)
13. NER baselines on TASTEset: rules + one encoder; RecipeDB3 record marked SOURCE_REPORTED (P5)
14. DEL-2 split generators + D0–D5 baselines + bootstrap CIs + MNAR diagnostics (P8)
15. Molecule registry v1 via PubChem for DEL-1 analytes; IMAP typed mappings (P3/P12)
16. ALLERGEN- authority table (FSSAI) + WARN- schema (P11)
17. DEL-4 retrieval: BM25 + dense + filters + compatibility reranker + Evidence Packet (P10)
18. DEL-5 decision interfaces ANSWER…ABSTAIN + B0–B7 cards (P11)
19. Silver factory scaffold (adapters, prompts, validators, 1k→audit gates) — no launch (P7)
20. Handoff docs: RUNBOOK, MANUAL_NEXT_STEPS, EXPERIMENT_QUEUE, BLOCKERS … (P15)

## 5b. LEDGER BUILD QUEUE (one by one, all linked by IDs) — added 2026-10-18 on Kush's request
| # | Ledger | Source | State |
|---|---|---|---|
| 1 | ING / ALIAS | A1 corpus (+FDC candidates) | ✅ v1 (S009–S010) |
| 2 | PROC | corpus verbs + evidence steps | ✅ v1 (S015) |
| 3 | EVD / COND / SVAR / SRC / SNAP / MEAS | USDA R6 | ✅ (S007) |
| 4 | EVD (Phenol-Explorer) + STUDY | polite crawl (D-005) | ⏳ crawl running |
| 5 | EVD → ING / PROC links | registries | next |
| 6 | TOOL (utensils, cookware, appliances, materials) | corpus mining + curated | queued |
| 7 | UNIT records | units.py catalogue | queued |
| 8 | REC (11,934 recipes, hashes, families) | A1 corpus | queued |
| 9 | MOL / IMAP | PubChem PUG-REST (+FlavorDB later) | queued |
| 10 | ALLERGEN | FSSAI labelling regulations | queued |
| 11 | WARN | authority sources + EVD | queued |
| 12 | Books / references | public-domain (Gutenberg) + open textbooks + govt guides only; no pirated copies | queued |

## 6. GATES REQUIRING HUMANS
H1 email to Prof. Bagler (draft in plan Appendix 2 / Part AS) · H2 any new scrape target · H6 any "beats CoSyLab"/SOTA claim · H7 GitHub repo · H8 semester scope cut.
