# CulinaryState — status, open work and review prompt (14 Nov 2026, evening)

Group 17 · Kush Tokas + Parv Goyal. Repo branch `kush/s179-finish-fixes`. Submission 21 Nov; technical freeze 19 Nov; verification 20 Nov.
Earlier full picture: `handoff/MASTER_STATUS_AND_PROMPT_2026-11-14.md` (SSOT §14/§70/§79 tables, 36-step audit). This file adds today's work and the plan to completion.

## 1. Contribution (frozen, D-112)
"CulinaryState is an event-sourced, lot-aware and composition-aware representation of cooking state transitions, where structural and physical changes are explicit and chemical effects are introduced only from compatible evidence or validated models; unsupported effects remain UNKNOWN."

State per step: S_t = (G_t structure/lineage, C_t composition/medium, Q_t physics, Y_t chemistry, P_t provenance). Every cell is value + basis, or UNKNOWN + reason.

## 2. Done today (14 Nov)
| # | Work | Result | Evidence |
|---|---|---|---|
| 1 | D-112 scope freeze | recorded | DECISIONS.md D-112 |
| 2 | Parser fix: salt/oil/vinegar read as verbs in lists | 2.9% of step events were spurious; guard (opt-in, frozen default unchanged) + v2 verb blocklist; ksh 0.94, prv 0.92 precision (AI, D-085) | `reports/s179/parser_coord_food_guard_audit_2026-11-14.md`, D-118 |
| 3 | C_t schema v1 → v1.1 | presence TRUE / NOT_DETECTED / UNKNOWN; FOOD vs MEDIUM role; fractions UNKNOWN until masses grounded; no lot pH; contact-phase truth table. **Kush passed (D-120)** | `reports/s179/d116_composition_state_schema_v1_1.md` |
| 4 | Marker table v2 | 115 rows (salt, acid, lipid, aqueous; marker sets; roles) | `registry/composition_markers_v2.csv` |
| 5 | Full-corpus composition runs v1 and v1.1 | 612,782 recipes, 9.22 M rows, 0 exceptions | `reports/s179/state_dataset_fill_full_D116v1{,1}_2026-11-14.json` |
| 6 | C_t v1.2: USDA SR composition per ingredient | 793 ING × fat/water/sodium/protein/sugars copied from SR Legacy (public domain, fdc_id locator); food excluded from its own context | `registry/ing_sr_composition_v1.csv`, `src/culinarystate/composition/context_v12.py` |
| 7 | Item 4: composition-aware routing (existing enums only) | layer over frozen router: added salt/acid/lipid → CONTEXT_MISMATCH with near evidence; UNKNOWN axis never DIRECT; water-only merge restores DIRECT | `src/culinarystate/composition/router_v12.py` |
| 8 | Unstated context suggestion | INGREDIENT_LIST_UNPLACED (listed, never used in a step) and CORPUS_PRIOR (share of same food+process events with the axis stated) → SCENARIO, never stated fact | same module; corpus run below |
| 9 | Tests | 12 router + 6 context + 21 composition/guard pass; Rung A 54 pass | `tests/unit/test_s179_d116_*` |

Boil events, full corpus (v1.1): 123,177; salted 12,185 (9.9%); acidic 9,406 (7.6%); lipid 9,744 (7.9%); all three 881 (0.7%); UNKNOWN 18,429 (15.0%).

### Worked examples (real pipeline output)
| Text | C_t (food context) | Vitamin C route (after item 4) |
|---|---|---|
| A: boil tomatoes in water | plain, AQUEOUS | DIRECT, EVD-002765 (USDA R6, 95%) |
| W: tomatoes + water, boil | plain, AQUEOUS | DIRECT (water-only merge) |
| B: + salt | SALT | CONTEXT_MISMATCH, near EVD-002765 |
| C: + salt + vinegar | SALT+ACID | CONTEXT_MISMATCH |
| D: + salt + vinegar + oil | SALT+ACID+LIPID, AQUEOUS+LIPID | CONTEXT_MISMATCH |
| noodles boiled, then cooked with milk | lipid (fat 3.25 g, fdc 171265), AQUEOUS+LIPID | — (no noodle EVD) |
| noodles boiled, then cooked with tomato sauce | AQUEOUS, fat 0.3 g | — |
| A + salt in ingredient list only | plain (stated) + salt SUGGESTED | DIRECT (stated) + SCENARIO (salted) |

Before item 4, B/C/D were all UNKNOWN MERGED_LOT_CONTEXT, which does not tell them apart.

## 3. Corpus prior + naive-lookup headline (done, 612,782 recipes, 0 exceptions)
`reports/s179/context_prior_full_2026-11-14.json` (counts only; (food, process) keys with n >= 30: 13,520 of 41,586).
- **Headline (proxy):** 466,605 heat food-events have an (ingredient, process) EVD pair, i.e. a naive lookup would answer. Of these, **371,011 (79.5%)** sit in a lot with added salt, acid or lipid that the evidence row does not record. Per axis: salt 63.0%, acid 11.9%, lipid 77.0%. Boil only: 83,346 events; salt 55.0%, acid 17.2%, lipid 68.3%.
- **Why so high:** many recipe "boil" events are "bring the sauce to a boil" on an accumulated lot (onions sautéed in oil, then tomatoes, then boil). So the lot really does carry the oil. The count is per food × event, so a large merged lot counts once per member food.
- **Example priors (boil, share of events with the axis stated):** tomato n=3,996, salt 62% PROBABLE, lipid 82% PROBABLE; chicken n=4,159, salt 54%, lipid 68%; rice n=3,682, salt 38% POSSIBLE, lipid 54% PROBABLE; noodles n=1,291, salt 20%, lipid 29% POSSIBLE; pasta n=2,295, salt 20% (just under POSSIBLE), lipid 24% POSSIBLE.
- **Caveats found:** (i) MEMBER_UNLINKED never fires, because Rung A does not create entities for words outside its lexicon. NOT_DETECTED therefore means "no marker among recognised mentions" (0 UNKNOWN in this run). (ii) The INGREDIENT_LIST_UNPLACED counts are inflated by ING-id mismatch (lemon listed vs lemon juice in a step): acid 789,561, salt 539,312, lipid 310,590 events. Treat these as an upper bound, never as figures. (iii) Lipid PROBABLE is very common (13,036 of 13,520 keys have some PROBABLE axis), so the cut-offs need review before use.


### 3b. Headline v2 (D-122 semantics; 612,782 recipes, 0 exceptions) — supersedes the 79.5% wording
`reports/s179/context_prior_v2_full_2026-11-14.json`
- Naive (ingredient, process) answers: 466,605 food×event. **UNCONFIRMED 378,339 (81.1%)**: the recipe states salt/acid/lipid (or the evidence is oil-fried and the query shows no recognised fat), but the evidence row does not record it. NO_STATED_DIFFERENCE: 88,266 (18.9%). MISMATCH: 0 (no evidence row records an absence). QUERY_UNKNOWN: 0 (see caveat i).
- Unique events: 3,715,647 heat events; 369,597 have a naive answer for at least one food; **287,728 (77.8%)** have at least one UNCONFIRMED food.
- Timing of TRUE context (food×event): added at this step vs carried in the lot from earlier steps: salt 15.0% / 85.0%; acid 9.3% / 90.7%; lipid 21.4% / 78.6%. "Carried" means the co-member joined the lot at an earlier step. It is usually still in contact (a mixture), so this is not "history only".
- Report wording: "In 81% of the cases where a simple ingredient-and-process lookup finds evidence, the recipe states a salt, acid or lipid context that the evidence source does not record, so applicability is unconfirmed rather than direct."


### 3c. Late evening (D-122 to D-130)
- D-122: semantics v1.2.1. Evidence context is PRESENT / ABSENT / UNKNOWN_IN_SOURCE; query context is TRUE / NO_RECOGNIZED_MARKER / UNKNOWN. Tomato B/C/D become UNKNOWN (unconfirmed in source), with near evidence EVD-002765.
- D-124: external flow-graph corpus skipped; external human-gold validation is DECLARED_NOT_RUN.
- D-126 / D-128: blind 50-context check, labelled by ksh+prv (AI, D-085). Gate FAIL: salt P 0.75 / R 0.71; acid P 0.75 / R 0.50; salt suggestion 0.53. PASS: lipid P 0.88 / R 0.76; water P 0.87 / R 0.82. Rater κ 0.78–1.00. Error classes: salty foods missing from the marker table; USDA default butter is salted; acidic foods without a pH route; the food's own salt or acid not counted; "A or B" alternatives; 7/50 food-to-step binding errors. Score: `reports/s179/d116_human_check_score_ai_2026-11-14.json`.
- D-130: Kush accepts v1.2.1 with the FAIL recorded; no human review round.
- Item 8: `registry/chemistry_packet_d116_v1_DRAFT.csv`, 13 records. 2 are existing USDA ledger rows (DIRECT, plain context); 8 come from the literature/pH tables, all VERIFY_AGAINST_PRIMARY; 3 are GAPs (salt × vitamin C, salt/acid × lycopene, vitamin C leaching). Lycopene–oil records concern bioaccessibility, a different target from content, so they are SCENARIO, never DIRECT.
- Parv: no new GitHub commits since the 13 Nov candidate (`reports/final/submission_candidate_2026-11-13/`). Open PRs #11, #12.

## 4. D-112 execution list
| # | Item | Status |
|---|---|---|
| 1 | contribution frozen | ✅ |
| 2 | parser fix measured before/after | ✅ (guard v2 corpus-wide in v1.1 run) |
| 3 | C_t schema | ✅ v1.1 passed; v1.2 SR thresholds PROPOSED |
| 4 | router composition axes | ✅ built + tested; corpus count running |
| 5 | embeddings retrieve, structure decides | ⏸ not started (SHOULD; cut if time) |
| 6 | tomato A–D acceptance | ✅ |
| 7 | full-corpus composition counts | ✅ v1, v1.1; prior/headline running |
| 8 | chemistry packet (vitamin C, lycopene, acid/pH, salt, lipid) | ⏸ next: sourced records with locator, licence, route class; Kush/Parv verify |
| 9 | contrast-case ablation, DIAGNOSTIC_ONLY | ⏸ not run |
| 10 | report / PDF / slides | ⏸ not started for the new results; Parv's 13 Nov candidate exists |

## 5. Open MUST / SHOULD (to reach completion)
Board on 13 Nov: MUST 52/84 done, SHOULD 89/117. Open MUST = 12 author edits (human), 10 data-limited/partial, 7 not run/deferred, 3 calendar. Those still reachable by 19 Nov, with today's additions:

**MUST (submission cannot go without these)**
1. Chemistry packet (item 8): about 10–20 sourced records for vitamin C (acid stability, leaching to water, salt), lycopene (oil, heat isomerisation), acidity (sourced pH table for tomato, tomato sauce, vinegar). AI drafts; **Kush/Parv verify each record** used in a figure. Owner: agent drafts, humans verify.
2. Review of v1.2 PROPOSED thresholds (fat ≥ 1 g, water ≥ 50 g, sodium ≥ 400 mg per 100 g; prior PROBABLE ≥ 0.5, POSSIBLE ≥ 0.2, n ≥ 30). Owner: ksh+prv AI, then Kush.
3. Full-corpus headline number + figure (state representation diagram, tomato A–D, noodles). Owner: agent.
4. Report + deck updated with the frozen contribution, today's results and the honest negatives (H1/H3 RULE_NOT_MET, NER ties lab, AI-delegated reviews ≠ human). Owner: Parv (start now) + Kush.
5. Author edits and person-only facts (12 board items). Owner: Kush, Parv.
6. Parv's candidate rebuilt on the final revision (v2), with verification manifest. Owner: Parv.
7. 20 Nov verification: full test suite, hashes, no host paths or recipe text in public files.

**SHOULD**
8. Small human spot check (Kush/Parv, about 50 contexts): composition flags and suggestions, so at least one human number exists. This is the cheapest way to answer "human evaluation not met".
9. Contrast-case retrieval ablation (item 9), DIAGNOSTIC_ONLY.
10. D-098 ablations / frozen-7B H1/B7 regeneration (Parv's list).
11. Hosted demo (Vercel UI + container backend; needs `vercel login`), only after the report and deck are done.
12. Cheap gate closes (steps 01, 02, 08, 14, 36) from the 36-step audit.

**CAN / cut if late**
Item 5 multi-view embeddings; L4 BBC leg; D-108 lot formula; formula vs EVD check; bare "Drain." zero-object linking (known limitation: an object-less step attaches to no lot; lineage across it is still correct).

## 6. Day plan
| Day | Agent | Kush | Parv |
|---|---|---|---|
| 14 Nov eve | merge prior run, headline, threshold review packet | pass/fail thresholds | start report/deck update |
| 15 Nov | chemistry packet draft (item 8), figures | verify chemistry records | report/deck |
| 16 Nov | router with verified records (SCENARIO/DIRECT where compatible); 50-context spot-check sheet | spot check | spot check, deck |
| 17 Nov | contrast ablation (diagnostic), numbers into report | author edits | candidate v2 rebuild |
| 18 Nov | final full-corpus rerun on the frozen revision | review | review |
| 19 Nov | **technical freeze** | | |
| 20 Nov | verification pass | sign-off | sign-off |
| 21 Nov | **submit** | | |

## 7. Known limitations (say them in the report)
- Chemistry evidence is thin. The only DIRECT tomato rows are generic USDA R6 retention rows (medium not recorded). Salted, acidic or oily boiling has no ledger evidence yet, so it stays CONTEXT_MISMATCH / UNKNOWN.
- Acidity: no sourced pH table, so tomato sauce is not yet "acidic". Acid comes from markers only.
- Marker table and SR matches are AI-drafted or AI-delegated (D-085), not human-verified.
- The ingredient-list "unplaced" check compares ING ids, so "lemon" listed and "lemon juice" in a step count as unplaced (over-suggests acid).
- The naive-lookup headline is a proxy: (ingredient, process) EVD pair exists. Other router gates are not applied.
- Human evaluation: 07.A human audit FAILED; later reviews are AI personas, not inter-rater evidence.
- NER: RecipeDB3 0.9557 vs lab 0.9543, a tie rather than a win. H1 and proposal H3 are RULE_NOT_MET.

---

## 8. Prompt for an external LLM review (paste everything below this line, plus §1–§7 above)

You are reviewing a student research project (IIIT Delhi, submission 21 Nov 2026, technical freeze 19 Nov). Read §1–§7. Be specific and critical; do not invent results.

Answer in this order:
1. **Claim check.** Is the frozen contribution sentence supported by the evidence listed? Which words in it are over-claimed or under-supported, and what minimal wording change would fix that?
2. **Method check of C_t v1.2 and the composition router.** Are TRUE / NOT_DETECTED / UNKNOWN, CONTEXT_MISMATCH for added salt/acid/lipid, and the water-only exception sound? Name concrete failure cases (recipe sentences) where they give the wrong route.
3. **Unstated-context suggestion.** Are INGREDIENT_LIST_UNPLACED and CORPUS_PRIOR acceptable as SCENARIO (not fact)? Are the cut-offs (p ≥ 0.5 / 0.2, n ≥ 30) and the SR thresholds (fat ≥ 1 g, water ≥ 50 g, sodium ≥ 400 mg per 100 g) defensible? Suggest better ones only with a reason.
4. **Headline.** Is "share of naive-lookup answers whose lot has unrecorded added salt/acid/lipid" a fair and interesting result? What control or caveat must accompany it?
5. **Chemistry packet.** For vitamin C, lycopene, acidity/pH, salt and lipid in boiled tomato (and pasta/noodles), list the kind of primary sources (no invented numbers) that would let a row route DIRECT or SCENARIO, and which effects should honestly stay UNKNOWN.
6. **Priorities.** Given 5 days and two students, rank the open MUST/SHOULD items in §5. What would you cut? What single addition would most raise the evaluation (e.g. a 50-item human spot check)?
7. **Positioning.** Compare with related work (procedural text state tracking such as ProPara / Neural Process Networks, recipe flow graphs, FoodKG / RecipeDB, USDA retention factors, food-composition-aware nutrition estimation). Where is this work genuinely new, and where is it not?

Rules: no invented numbers or citations; say "not known" where you cannot verify; keep each answer under 200 words.
