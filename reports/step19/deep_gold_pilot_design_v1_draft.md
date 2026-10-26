# Step 19-D / 19-pilot — Deep Gold PILOT design v1 (DRAFT)

**Status: DRAFT_PENDING_H4 / H5.** Written 2026-10-26 under D-027 ruling R-17 (Plan section 4.2 lane L7), with R-08, R-19 and R-20; revised the same day after the round-3 reviews (governance Review A, science Review B). Design only: no recipe was drawn, no packet was built, no annotation exists, no tool was run or edited, no existing file was modified, and Step 08 is not started. Nothing here is signed. Every numeric threshold is **PROPOSED_PILOT** (not a literature constant; a human must register it in `registry/preregistered_thresholds_v1.csv`, Step 01.6, before any recipe is drawn). The proposed 01.6 rows are in Appendix A (35 rows, `THR-19P-01..35`; rows 31-35 are new in the round-3 revision, rows 03, 04, 05, 11, 12, 16, 18, 19, 20, 26 and 28 were changed or annotated, and the changes only add triggers or checks, none relaxes a gate); the CSV was **not** edited. Local decision ids are `D19-n` and local check ids `PV-n`; none of them is a ledger id or a DECISIONS id.

**What this is.** The R-17 design package for the small, independent, blind Deep Gold pilot: about 20 fresh recipes, annotated blind by Kush and Parv, measuring (1) annotation time, (2) inter-annotator agreement (IAA) and (3) schema problems of the CURRENT contract (v0 schemas + handbook v1 + Addendum A), so that Step 16c (schema freeze) and 19-S (sizing) rest on measurements instead of the plan's 15–25 min vs 30–90 min per-recipe guesses.

**What this is not.** It is not the 19-M main cohort, not a reliability certificate (n = 20 recipes cannot certify alpha or F1 >= 0.80; only 19-M can), not a sizing decision for N > 40, not a re-tiering of the 40 AI-assisted recipes (19-R), and not a model evaluation. No model or AI output is shown to annotators, and AI never annotates, signs as Kush or Parv, fills or adjudicates (`annotation/PILOT_20_TASK.md`, handbook section 8).

Sources read for this draft: Plan v2 header, section 0-1 and Phase D (Steps 16-20, with the Step 16 and Step 19 cards), section 4.5; `tools/gold_cli.py`, `tools/gold_pilot_agreement.py`, `tools/bundle_gold_packs.py`, `tools/make_independent_gold_packs.py`, `tools/make_gold_batch.py`; `annotation/` handbook, Addendum A, checklist, `PILOT_20_TASK.md`, adjudication template, manifests; `reports/gold/*`, `reports/del3/*`; `reports/master_plan/working_notes/research/r_recipe_semantics_gold.md`; Audit v2 section M.8; `registry/preregistered_thresholds_v1.csv` (format only). Only ids, counts, hashes and structural columns of `ledgers/recipe_base` and `ledgers/recipe_identity` were read (read-only, aggregate queries); **no third-party recipe text was opened** (ingredient lines and instructions); no title was read from the recipe base (`title_raw` was never selected). Titles, URL slugs and normalised family names that already sit in committed manifests and batch files (`annotation/batches/pilot_20.csv`, `pilot_20_manifest.csv`, the S116 `selection_manifest_v1.csv`) were incidentally visible in a few command outputs; they belong to already-excluded recipes and are not used by this design.

---

## 1. Goal, questions, and what the pilot cannot show

| # | Question | Measured by | Output |
|---|---|---|---|
| Q-T | How many minutes does a full-depth blind annotation take per recipe per annotator, and how does it vary with source, stratum and complexity? | timing sheet (section 6) | `pilot_timing_v1.csv` + summary in the report |
| Q-A | How well do two independent annotators agree per field family under the CURRENT contract, with what uncertainty? | `gold_pilot_agreement.py` outputs + a new report script (section 7) | `pilot_iaa_report.md` (all IAA labelled DIAGNOSTIC) |
| Q-S | Which phenomena can the v0 schemas + handbook not represent, and which handbook rules are ambiguous? | schema-problem log (section 9) | `pilot_schema_problem_log.md` |
| Q-P | Can independence be enforced and *checked* technically (packets, hash commitments, provenance-validity check)? | provenance check (section 5.5) | `pilot_provenance_check.json` |
| Q-C | Do the measured hours fit the 40 h per-annotator cap, and what would N = 40 cost? | sections 6, 10, 11 | go / no-go to 19-S |

**The pilot cannot show** (stated now so nobody reads it later as a result):

- That any field reaches alpha or F1 >= 0.80 (certification belongs to 19-M, G19.M).
- Any difference between sources, strata or complexity tiers (1-4 recipes per cell).
- Anything about a rare phenomenon (reserve/recombine, implicit events, alternatives) unless it occurs often enough (rule `THR-19P-21`: counts only below 30 units from 5 recipes).
- That the handbook works for annotators outside the project (Kush and Parv wrote or approved it; agreement will overstate outside reliability, as `reports/del3/gold_pilot_20_v1.md` already states).
- A population-level timing: the sample is stratified and (in P2) coverage-enriched, not self-weighting.

---

## 2. Facts verified read-only for this design (they change the design)

| # | Fact | Source |
|---|---|---|
| F1 | There is **no** valid independent annotation anywhere. 40 recipes (20 BBC `pilot_20` incl. the 7 calibration recipes; 20 Food.com `FC100067 ... FC534509`) are `AI_ASSISTED_HUMAN_REVIEWED` and `not_independent: true`. The blank S116 independent bundle for the same 20 Food.com recipes is **exposed** (the same ids were AI-drafted and batch-approved), so it cannot be reused as independent Gold. | `reports/gold/foodcom_v1_1_review_record.json`, `foodcom_ai_assisted_human_review.md`; D-016, D-017; Plan Phase D fact 1 |
| F2 | `ledgers/recipe_base/gold_recipe_index_v1.parquet` holds **50** ids: 20 `PILOT_DEV_GOLD` (REC-), 20 `FOODCOM_AI_ASSISTED_GOLD` (FC), and **10** `EXPANSION_CANDIDATE` Food.com reserves (`FC100711 ... FC532276`, screened, never annotated). The S116 screening log covers **120** distinct Food.com recipes (the 30 selected + 90 AI-screened pool recipes; reviewer of record `claude-ai`, not a human). | `gold_recipe_index_v1.parquet`; `annotation/gold/evidence_first_expansion/{screening_log,selection_manifest_v1}.csv` |
| F3 | The brief for this design said "exclude the 20 AI-assisted Food.com ids". The plan card excludes the **40** AI-assisted recipes, the 7 calibration recipes, the S116 20 Food.com recipes and their title twins. This draft excludes all of these and (conservatively) the 10 reserves and the 90 other screened pool recipes: **the 20 Food.com ids are a subset of the exclusion list** (`THR-19P-03`). | Plan Step 19 card 'Method'; this section |
| F4 | `recipe_base_v1.parquet` families: A1_BBC_GOOD_FOOD 11,934 (local-only, `LOCAL_RESEARCH_ONLY`, locale en-GB, median 3 steps, 9 ingredient lines); FOODCOM 522,517 (`LICENCE_UNVERIFIED`, median 6 steps, 7 lines, **0% explicit cuisine labels**); WIKIBOOKS 3,676 (CC BY-SA, usage class `REDISTRIBUTABLE_WITH_ATTRIBUTION`, redistribution CONDITIONAL in the usage registry); GUTENBERG_SEGMENT 73,955 (public domain; `training_allowed = YES` per `registry/recipe_source_usage_registry_v1.csv`, where it is YES only for GUTENBERG_SEGMENT) and TASTESET 700. **GUTENBERG_SEGMENT has 0 ingredient lines in every row and TASTESET has 0 steps**, so neither can be represented by the gold-1.0 template (`ingredient_lines[]` + `steps[]`). That is a representability gap to log (section 9), not something to sample. | `ledgers/recipe_base/recipe_base_v1.parquet` (aggregate queries); licence and `training_allowed` per `registry/recipe_source_usage_registry_v1.csv` (the parquet has no `training_allowed` column) |
| F5 | Eligible exact-duplicate representatives (4-20 ingredient lines, 2-15 steps, has ingredients and instructions, BBC + Food.com + Wikibooks): BBC 10,599 (LOW 4,066 / MID 5,425 / HIGH 1,108), FOODCOM 418,008 (79,332 / 208,506 / 130,170), WIKIBOOKS 3,169 (509 / 1,586 / 1,074); tiers per `THR-19P-06`. Stratum "simple" (<= 3 steps and <= 6 lines): BBC 1,496, FOODCOM 30,585, WIKIBOOKS 163. Explicit cuisine Indian/Indic: BBC 344, WIKIBOOKS 101, FOODCOM 0. | same |
| F6 | The old `pilot_20` was drawn with `tools/make_gold_batch.py --seed 7` under a filter of **<= 14 ingredient lines and <= 8 steps**, from BBC only, with regex strata. It is therefore easy-leaning and single-source; the new frame widens the caps and adds sources and a complexity axis. | `tools/make_gold_batch.py` |
| F7 | Fallback grouping (no 07I-S yet), computed on ids only (no titles): connected components over exact duplicate group alone = 611,714 (max 18 recipes); + provisional family = 605,476 (max 18); + dish-family candidate = 457,545 (max 261). The 50 Gold-index recipes sit in 50 components containing 129 recipes in total (largest 46). Title-twin edges (normalised title) were **not** computed because they need titles. So a component-based exclusion is cheap (about 129 recipes plus title twins) and there is no giant component at this granularity. | `ledgers/recipe_identity/*.parquet` (ids only) |
| F8 | Tool facts that matter: (a) `gold_pilot_agreement.py` labels a run `INDEPENDENT_HUMAN_VS_HUMAN` whenever no file has the notes marker `AI_DRAFT_HUMAN_REVIEWED`, i.e. its independence label is a **default**, not a check; (b) its denominators for spans, events, coref and state sum **both** annotators' units, lines use one, so a per-category rate understates the per-pair disagreement by up to 2x on matched-pair rows; (c) a span present in only one file is categorised `entity_type`, so omission and label confusion are merged; (d) it hard-codes `<gold>/pilot_20/{Kush,Parv}/<id>.<who>.json` and `pilot_20_manifest.csv`; (e) it reports no confidence interval, alpha, AC1 or specific agreement and no timing; (f) `gold_cli.py agree` writes to `annotation/adjudication/<id>.csv`; (g) `make_independent_gold_packs.py` is wired to the S116 selection manifest and writes `"locale": "US"`. | `tools/*.py` |
| F9 | Environment: A1/BBC raw recipe text is **not** on this server (`make_gold_batch.py` reads `../a1/A1 3/data/raw/recipes_raw.jsonl` on the Mac); Food.com text is local (`data/external/foodcom/recipes.parquet`); `ledgers/recipe_semantics/*` is absent here. The frame builder (which applies regex strata to text) must run where text exists and must emit text-free outputs only. | `ls`; Plan Step 17 status |
| F10 | `registry/recipe_quality_tier_registry_v1.csv` still lets `GOLD_PENDING_INDEPENDENT_IAA` support calibration, contradicting SSOT inv. #14; fixing that is 19-R (tier registry v2), outside this pilot. | Plan Phase D fact 3 |

---

## 3. Design at a glance

| Item | Design |
|---|---|
| Recipes | 20 fresh, never seen by any model or reviewer: **wave P1 = 7**, **wave P2 = 13** (`THR-19P-01`; plan card) |
| Annotators | Kush and Parv, each alone, blank packets with **separate packet ids** and per-annotator seeded order, own machine/account, no model/Silver output (section 5) |
| Contract under test | v0 schemas + handbook v1 + Addendum A for P1; P2 under the handbook revised by a dated **Addendum B** only if P1's review gate requires or the humans choose it; never retro-applied (section 5.6) |
| Tools reused | `gold_cli.py validate/replay`, `gold_pilot_agreement.py` (via a wrapper that stages files into its expected layout; the tool is not edited), `adjudication_template.csv`, `bundle_gold_packs.py`, blank-template format of `make_independent_gold_packs.py` |
| New (to build after approval, none built now): **six scripts** | (1) frame builder + seeded draw, (2) packet maker + sealed key, (3) commit step (commitments, provenance values, interim snapshots), (4) provenance checker + planted-pair test, (5) agreement wrapper, (6) pilot report script (CIs, alpha, AC1, specific agreement, timing, influence) |
| Hours | cap 40 h per annotator including setup and adjudication (`THR-19P-14`); card estimate Kush 16-38 h, Parv 16-38 h, expert 0-4 h |
| Output | `reports/step19/{pilot_iaa_report.md, pilot_timing_v1.csv, pilot_schema_problem_log.md, pilot_provenance_check.json}` and a go / no-go memo to 19-S |

Schedule (proposal; the humans are shared with 07.A and 07I-C, so packets of different tasks are never interleaved): approval of this design and signature of the 01.6 rows (Kush ~2-3 h, Parv ~2-3 h, Plan section 4.5) -> frame build and P1 draw -> **P1 inside the next 30 days** -> P1 provenance check, agreement run, joint adjudication, Addendum B decision -> **P2 only after 07I-C labelling closes** (so 07I-S groups exist for the P2 draw and the humans are free) -> P2 -> pilot report -> 19-S.

---

## 4. Sample

### 4.1 Frame and eligibility (`THR-19P-02`)

A recipe is eligible if all hold: it is the **exact-duplicate representative** of its group (`recipe_id == representative_recipe_id` in `recipe_identity_fk_v1`); source family is `A1_BBC_GOOD_FOOD`, `FOODCOM` or `WIKIBOOKS`; `has_ingredients` and `has_instructions`; 4-20 ingredient lines; 2-15 steps; text present on the machine that builds the packet. GUTENBERG_SEGMENT and TASTESET are structurally ineligible (F4). The ingredient and step caps keep a single recipe from dominating hours (a 20-line, 15-step recipe is already a heavy item) while being wider than the old <= 14 / <= 8 filter (F6). The caps are design parameters fixed before the frame is built; they are not tuned to the outcome.

Food.com is included only under the standing S116 Gate-1 decision (local research use; recipe text never committed or sent to a service); its source is still unregistered and the eligibility screen is unconfirmed (`foodcom_v1_1_review_record.json`: `s116_eligibility_screen_confirmed: false`). Open decision D19-1.

### 4.2 Exclusions (`THR-19P-03`)

Excluded before any draw, by recipe id, and then expanded to the whole fallback/07I-S group of each excluded recipe:

| Set | Count | Why |
|---|---|---|
| `gold_recipe_index_v1`: 20 BBC pilot_20 (includes the 7 calibration recipes), 20 Food.com AI-assisted, 10 Food.com expansion candidates | 50 | AI-drafted/reviewed or screened; exposure (F1, F2) |
| S116 screening-log pool: the 90 further Food.com recipes AI-screened (matched sentences read by an AI) | 90 | conservative: an AI saw them; a human may have read the matched sentence |
| Exact normalised-title twins of any of the above (the same test `gold_firewall_v1` used; 7 of the 40 Gold recipes have such a twin in the bulk corpus per D-024) | computed at build time | leakage proxy |
| Every recipe sharing a fallback group (exact duplicate group, provisional family, dish-family candidate, same normalised title) or, once it exists, a 07I-S `SPLITGRP-REC-` group with any of the above | about 129 recipes for the 50 Gold-index ids (F7); the 90 pool ids add their own components; plus title twins | R-08: a group is one unit of independence |

The exclusion is a **superset** of the brief's "20 AI-assisted Food.com ids". Any recipe a human has already read for another purpose and wants to declare clean is *not* un-excluded by this draft (a human may attest otherwise, Plan fact 1, but this draft does not propose it).

### 4.3 Grouping and one-per-group (`THR-19P-04`)

Draw **at most one recipe per group**. Group key, in order of preference:

1. `split_group_id` (`SPLITGRP-REC-...`) from 07I-S when it exists (R-08; recall-oriented; plane-qualified, never joined to the evidence plane);
2. otherwise the **conservative fallback** of the card: connected components over exact duplicate group, provisional family, dish-family candidate and same-normalised-title.

P1 will probably run on the fallback (07I-C labelling is shared-human work and P2 waits for it). When 07I-S later exists, each pilot recipe's final 07I-S group is looked up and the **whole group is locked** (`THR-19P-30`) even if 07I-S merges it with other recipes; if the later grouping puts two pilot recipes in one group, both stay DESIGN_PILOT and the clash is logged. If a fallback component that contains an excluded id exceeds `S_max = 500` recipes, only the members tied to the excluded id by exact duplicate group, provisional family or same normalised title are excluded (not the whole dish-family component); no giant component exists at the id level today (F7), so this rule is a safeguard, not a tuning knob. The value 500 was nevertheless fixed after the component sizes were seen (largest 261, F7), and a sub-blocking rule that shrinks an exclusion when a component is large is exactly what Plan 'Reading conventions' conflict #4 (R-08 versus the giant-component guard) flags as open to a reading of tuning to obtain usable sizes. It is therefore a human decision (D19-17): if the clause is not confirmed it is dropped and the whole component of an excluded id is excluded (the stricter reading; it changes nothing today because the largest component is 261).

### 4.4 Strata, quotas, and the 7 existing strata (`THR-19P-05`..`07`)

Three crossed axes, none of which uses model output:

- **Source family (quota 6 / 10 / 4):** A1_BBC_GOOD_FOOD 6, FOODCOM 10, WIKIBOOKS 4. Reason: Food.com dominates the corpus (85%) and has the defect profile the 20 AI-assisted recipes exposed (missing listed ingredients, malformed steps); BBC is editorial text and the old pilot's source; Wikibooks (CC BY-SA) is the only eligible source whose text may later be released, and only under CC BY-SA terms (attribution + share-alike) and after an H2 review (the usage registry records redistribution as CONDITIONAL), which keeps that option open. The quota is not proportional to the corpus on purpose.
- **Dish-type stratum (the 7 existing strata):** baking, drain_discard, indian, multi_component, random, reserve_split, simple, defined exactly as in `tools/make_gold_batch.py`: reserve_split `\b(reserv|set aside|remaining|the rest|divide|half the)\b`; drain_discard `\b(drain|strain|discard)\b`; baking `\b(bake|oven)\b`; multi_component `\b(for the (sauce|dressing|topping|filling|marinade))\b` (all on the lower-cased concatenation of steps and ingredient lines); indian = explicit cuisine label Indian/Indic (BBC `cuisine_raw`, Wikibooks label; **Food.com has no label, so the Indian stratum cannot come from Food.com**); simple = <= 3 steps and <= 6 ingredient lines; random = any eligible recipe (as in `make_gold_batch.py`, which drew `random` from the unselected remainder, tagged or not). Keeping the regexes identical keeps strata comparable with the old pilot. A recipe may carry several tags; for a P1 cell it must carry that cell's tag.
- **Complexity tier:** c = ingredient lines + 2 x steps (a count-only index, fixed before the draw); **LOW c <= 14, MID 15-24, HIGH >= 25**; tier quota LOW 5 / MID 9 / HIGH 6. Cutpoints are round numbers chosen from the frame description (F5 shows each tier is populated in each source family), not from any outcome.

**P1 cells (7, fixed, `THR-19P-07`)** — one per existing stratum, as the card requires, with source and tier fixed so the draw is deterministic and the quotas stay feasible:

| P1 cell | Stratum | Source | Tier |
|---|---|---|---|
| P1-1 | baking | FOODCOM | MID |
| P1-2 | drain_discard | A1_BBC_GOOD_FOOD | LOW |
| P1-3 | indian | WIKIBOOKS | MID |
| P1-4 | multi_component | FOODCOM | HIGH |
| P1-5 | random | A1_BBC_GOOD_FOOD | MID |
| P1-6 | reserve_split | FOODCOM | HIGH |
| P1-7 | simple | WIKIBOOKS | LOW (implied by the definition) |

**P2 cells (13)** fill the remaining quota: BBC 4, FOODCOM 7, WIKIBOOKS 2 and LOW 3 / MID 6 / HIGH 4, as the matrix BBC (1 / 2 / 1), FOODCOM (1 / 3 / 3), WIKIBOOKS (1 / 1 / 0) in (LOW / MID / HIGH). P2 is drawn after P1 is finished and is not a function of P1 results except through the handbook revision (Addendum B), never through which recipes "worked".

If a cell has fewer than 30 eligible recipes after exclusions, the cell falls through to the next source in the fixed order FOODCOM -> A1_BBC_GOOD_FOOD -> WIKIBOOKS (and the fall-through is logged); for the cells defined by structural columns or cuisine labels the eligible counts before exclusions are 45 or more (F5: Wikibooks Indian MID 45 is the tightest; Wikibooks simple 163); for the regex-defined strata the count is known only when the frame is built, so fall-through is possible and is logged.

### 4.5 Draw procedure (`THR-19P-08`, `THR-19P-10`)

1. Build the frame manifest (text-free: recipe id, source family, group key, stratum tags, n_ingredient_lines, n_steps, c, tier, hard-case tags, inclusion probability per cell, raw content sha256) and hash it: `frame_sha256`.
2. **Seed** = first 8 bytes of SHA-256(`frame_sha256` || wave label || `nonce`), where `nonce` is a string Kush writes into the signed 01.6 row **before the frame is built**. The agent that builds the frame never chooses the seed. (The old pilot used first-by-(stratum, recipe_id); the card asks for a pre-registered seeded draw.)
3. **P1:** inside each fixed cell, shuffle eligible candidates with the seed (stable order), skip any whose group is already used, take the first. The next 2 candidates in shuffled order are the cell's ordered **reserves** (the same rule applies to every P2 cell).
4. **P2:** build the candidate list per cell as in step 3, then choose by a seeded greedy coverage rule: repeatedly take the candidate that adds the most §237.5 hard-case classes not yet covered by the already chosen recipes (ties broken by the shuffled order). This oversamples hard phenomena on purpose (SSOT §237.5; `r_recipe_semantics_gold.md` section 3.5: "hard strata oversampled but weighted") while the cell quota fixes source and size. Whether P2 should instead be a pure stratified random draw is open decision D19-10 (it trades hard-case coverage for an unbiased P2 timing).
5. **Hard-case coverage is reported, not enforced.** The 17 classes of SSOT §237.5 split into mechanically taggable ones (mixed fractions and ranges, nested packaging "1 (14 oz) can", count + mass, large/medium/small count items, heaped/packed/level measures, optional/divided/reserved ingredients, "remaining/half of reserved", endpoint phrases, missing quantities, multiple temperatures/times in one sentence) and manual-only ones (pronouns/implicit references, many-to-one and one-to-many, ambiguous words such as clove, regional aliases, compound foods, conflicting source instructions). The tag rules are a separate reviewed spec file (proposed name `registry/recipe_semantics/deep_gold_pilot_tag_rules_v1.csv`, not created now). After the draw, classes with 0 occurrences among the 20 are listed as UNCOVERED for the representability audit; **no redraw** is allowed for coverage (that would be tuning the sample to the schema).
6. Freeze: write the text-free selection manifest to the **tracked** folder `registry/recipe_semantics/deep_gold_pilot_v1/` as `manifest_<wave>.csv` (ids, cells, tags, seeds, `frame_sha256`, reserves; never the packet-id map) together with its sha256; recipe text lives only in git-ignored local files (D-007). The old default path `annotation/gold/deep_gold_pilot_v1/` is ignored by `.gitignore:9` (`annotation/gold/*`, verified with `git check-ignore -v`), so a manifest left there would not be committed; `.gitignore` is not edited here (D19-18).

### 4.6 Reserves and replacement (`THR-19P-09`)

Same rule as the S116 protocol: a reserve replaces a drawn recipe **only before annotation starts** and only for source corruption, a duplicate discovered after freeze, a recipe the gold-1.0 template cannot hold, source unavailable on the annotating machine, or an exposure discovered. Never because a recipe looks difficult or a model fails on it. The replacement is the next reserve in the cell's order; log id, reason, who decided.

### 4.7 Leakage tags and locks (`THR-19P-30`)

Every pilot recipe and its whole group are tagged `DESIGN_PILOT` in the frame manifest and (later) in `split_group_id` records: dev and error analysis only; **never** sealed test, calibration or training; never reused as an independent test item; excluded from Silver, Gold-Light, demo and retrieval exemplar sets (Plan Step 19 leakage line). The adjudicated pilot set is proposed to be named `pilot development Gold, blind two-annotator (independent only if the pilot provenance check passes), prior AI exposure of annotators recorded, design pilot`: the word 'independent' is allowed only when `counts_as_pilot_provenance` is true (section 5.5) and the annotators' AI exposure (D19-4) is recorded with the name. No such status exists in the tier registry yet (D19-13).

### 4.8 Sampling limitations to state in the report

n = 20 with 7 strata, 3 sources and 3 tiers means 1-4 recipes per cell; BBC text is UK English editorial prose, Food.com is user text with typos; no Gutenberg or TASTEset representation; Indian recipes come from BBC and Wikibooks only; P2 is coverage-enriched; the annotators saw 40 AI-drafted recipes of the same type before (a style prior, F1) — a limitation that cannot be removed, only stated.

---

## 5. Independence protocol

### 5.1 Principles

Independence is **enforced and checked**, not assumed: the 07H condition audit (two files written 11 s apart, 899/900 judgement cells identical, `step07h_human_gate_result.json`) and the linker human gate (byte-identical files) are the reason (R-19). Deep Gold is annotated **blank**: no model, compiler, Silver, Gold-v1.1, B3/B4, NER or LLM output is shown, embedded or used to select what a recipe looks like. Assisted-vs-blank (anchoring) studies are out of scope (audit E19.3 not adopted).

### 5.2 Packets

- One gold-1.0 blank template per recipe per annotator (format of `make_independent_gold_packs.py`: `entity`/`concept` = `TODO` guards so `validate` fails until finished, empty spans/events/coref/unknowns, `status: DRAFT`), but with **separate packet ids per annotator** (`DGP-A-nnnn` for Kush, `DGP-B-nnnn` for Parv; which letter is whom is fixed in the signed row; `DGP-` is a local packet label, not a ledger id, and is never minted; registering it in the 04.9-min section 4 table or renaming it to a file-name token, and re-running the section 5 collision scan, is decision D19-24) and a **per-annotator seeded order**. The map packet id -> recipe id is a sealed key file, hashed at issue (the key file stays in the git-ignored folder; only its sha256 is tracked, `registry/recipe_semantics/deep_gold_pilot_v1/sealed_key_<wave>.sha256`) and opened only at the agreement step (after both commitments are tracked in git, PV-9). Recipe content hashes are checked equal across the two packets (existing `recipe_hashes_match` logic).
- Each annotator receives only their own packet set, on their own machine or account; the other's files never exist on the same filesystem before both commitments are made. This replaces the old "do not open the other folder" convention with a technical separation.
- Packet manifests (ids, hashes, counts, `ai_prefill: NONE`, `model_outputs_embedded: NONE`) are text-free and committed to the tracked folder `registry/recipe_semantics/deep_gold_pilot_v1/`; packet content (recipe text) stays in the git-ignored `annotation/gold/deep_gold_pilot_v1/{A,B,adjudicated}/` (D-007). Why two places: `.gitignore:9` ignores everything under `annotation/gold/` except named manifests, so the commitments that carry the independence control must live under a path that a plain `git add` does not skip (D19-18).

### 5.3 What annotators may and may not use

| Allowed | Not allowed |
|---|---|
| Handbook v1 + Addendum A (+ Addendum B for P2 if issued), checklist, hard examples, UNKNOWN examples, the three worked examples `GOLD-EX-001..003` (not pilot recipes), `registry/ingredients/ingredient_registry_v1.csv`, `registry/processes/process_registry_v1.csv` | any LLM, compiler, Silver or Gold-v1.1 output on pilot recipes; the other annotator's files, screenshots, partial results or any discussion of labels before both commitments exist; consulting the AI-drafted sets of other recipes as models while annotating (having seen them earlier is a stated limitation, section 4.8, not something a rule can undo) |
| `gold_cli.py validate` and `replay` on their own file (the replay is the engine's deterministic function of their own labels, Addendum A item 7) | AI completing, repairing, inferring or signing any annotation (`PILOT_20_TASK.md`) |
| Writing questions in a **question log** (one file per annotator) that contains no example labels. The log is **write-only during a wave**: each entry records the packet id and the UTC time (so the timing impact can be analysed), neither annotator reads the other's file, questions are answered only after both commitments of the wave exist, and **no convention changes inside a wave** (a rule that recurs becomes a dated Addendum B for the next wave, section 5.6; an unanswerable question is logged as AMBIGUOUS_HANDBOOK_RULE and the annotator applies their best reading) | giving each other label examples; answering a question, or changing or clarifying a convention, between packet issue and both commitments (an answer would be an anchoring channel) |

Replay feedback can pull both annotators toward engine-conformant encodings (shared tool-induced convergence). It is part of the contract being tested, so it stays, but each session records the number of validate and replay runs (section 6) so the effect can be discussed.

### 5.4 Hash commitments (per wave)

1. Each annotator finishes their wave, sets `DONE` only when `validate` prints OK, and runs the commit step on their own machine. **At commitment time** (not reconstructed later) the step records, for every label file, `{packet_id, sha256, size_bytes, mtime_utc}`, the hashes and UTC times of its interim snapshots (the step's `snapshot` subcommand is run at the first `validate` and again at `DONE`; PV-10), the annotator letter, the handbook version, the UTC commitment timestamp and the sha256 of the private question log and representability checklist -> `commitments_<letter>_<wave>.json` in the **tracked** folder `registry/recipe_semantics/deep_gold_pilot_v1/`, committed to git from that person's own account/session. Label content stays in the git-ignored `annotation/gold/deep_gold_pilot_v1/`. The tracked folder holds no recipe text (ids, hashes, sizes, times, cells only). It is not under `annotation/gold/` because `.gitignore:9` (`annotation/gold/*`) would silently skip it (checked with `git check-ignore -v`), and the commitment-before-key-opening control (PV-6) needs a git timestamp; `.gitignore` is not edited (D19-18).
2. Only after both commitments files are tracked in git (`git ls-files --error-unmatch <file>` succeeds, PV-9) are files exchanged to the agreement step. A file whose hash differs from its commitment is excluded from agreement and the violation is recorded; if independence was violated, agreement is **not** computed (the S116 protocol rule).
3. The sealed key is opened (its sha256 must equal the tracked `sealed_key_<wave>.sha256`), files are staged into the layout the agreement tool expects (section 7.6), and the provenance check runs first.

### 5.5 Provenance-validity check (`THR-19P-11`, `THR-19P-12`)

A new script (pattern of `step07h_human_gate_result.json`) produces `pilot_provenance_check.json` with a boolean `counts_as_pilot_provenance`. Checks (all PROPOSED_PILOT; the ids PV-1..PV-10 are local check labels, not registry ids):

| Id | Check | Result if violated |
|---|---|---|
| PV-1 | no two files (any annotator, any recipe) have identical bytes/sha256 | FAIL |
| PV-2 | share of recipes whose normalised label content (spans + links + events + coref) is identical between the annotators <= 0.10 (<= 2 of 20; 0 of 7 for P1) | REVIEW (a human decides with the timing sheet; very short recipes can legitimately coincide) |
| PV-3 | every file's mtime **as recorded in its commitment** (`mtime_utc`, written on the annotator's own machine at commitment time) lies inside the time window the timing sheet records for that packet (+/- 10 min) and before that annotator's commitment timestamp. The live filesystem mtime is not used: git checkout, `cp`, `scp` and staging copies (section 7.6) do not preserve it and `touch` forges it; the recorded value is still self-attested, which is why PV-9 and PV-10 add an external anchor and an interim history | FAIL |
| PV-4 | active minutes per recipe >= 5 per annotator (the old assumption was 15-25 min; 5 min is an implausibility floor) | REVIEW |
| PV-5 | `annotator` field matches the packet letter; commitments authored from two separate git identities/sessions (self-attested if not) | REVIEW |
| PV-6 | each commitment timestamp precedes the opening of the sealed key | FAIL |
| PV-7 | no field with >= 100 coded cells and dominant-class share < 0.95 shows identical codes in >= 98% of cells together with identical marginals (the 07H pattern 899/900). For a field with dominant-class share >= 0.95 (`THR-19P-22`) raw identity is expected and is not the test: the chance-corrected identity (p_o - p_e) / (1 - p_e) must be < 0.98 on >= 100 cells; a field with p_e = 1 is skipped and listed in the JSON (never silently dropped) | REVIEW |
| PV-8 | **planted-pair unit test**: on a synthetic fixture the checker flags a planted identical-file pair, a planted 11-second pair and a planted identical-content pair, a planted commitments file that is not tracked in git (PV-9 FAIL) and a planted label file with no interim snapshots (PV-10 REVIEW), and does not flag a planted clean pair (100% detection, 0 false positives) | the check is not usable until this test passes |
| PV-9 | each wave's two commitments files are tracked in git (`git ls-files --error-unmatch registry/recipe_semantics/deep_gold_pilot_v1/commitments_<letter>_<wave>.json` succeeds for both), and the git commit time of each precedes the sealed-key opening time recorded by the opener (the commit hash and time are written into the provenance JSON). This makes PV-6 checkable by a party other than the annotators | FAIL |
| PV-10 | each label file has >= 2 hashed interim snapshots listed in its commitment (first `validate` run and `DONE`), the last snapshot's sha256 equals the committed file hash, and every snapshot time lies inside the packet's timing-sheet window; a file with no interim history (a whole-file copy made at the end of a session) | REVIEW (written statement by the annotator, stored with the JSON) |

FAIL on any wave -> that wave's agreement is `NOT_COUNTED`, packets are re-issued on **fresh** recipes (the exposed ones are not reused), and nothing is claimed (G19.P(1), 07H precedent). REVIEW items go to Kush for a written statement of how the files were produced; the statement and the decision are stored with the JSON. Because `gold_pilot_agreement.py` labels runs independent by default (F8a), the pilot report may print "independent" only when `counts_as_pilot_provenance` is true.

### 5.6 Handbook freeze and Addendum B (`THR-19P-31`; `THR-19P-16` kept for comparability)

- P1 is annotated under handbook v1 + Addendum A **on purpose** (the pilot measures the current contract's problems; Plan Step 19 inputs). The handbook is frozen from packet issue until both commitments of the wave exist, and the question logs follow the same freeze (section 5.3): no answer, clarification or convention change reaches either annotator inside a wave.
- After P1: run the review gate: a disagreement category above 20% of its relevant units, by the existing tool's rate (`THR-19P-16`, unchanged and kept for comparability) **or** by the per-pair-normalised rate (`THR-19P-31`), i.e. max(rates) > 0.20 -> `HANDBOOK_REVISION_REQUIRED`; otherwise `NO_MECHANICAL_FLAG (read the table before CALIBRATION_PASS)`. Then joint adjudication, then a **dated Addendum B** carrying only rules that recur (>= 3 times, handbook section 7) or are needed to resolve a BLOCKING schema problem. P1 labels are never edited or re-scored under Addendum B.
- P2 runs under v1 + A + B (or v1 + A if no Addendum B was needed). P1 and P2 are therefore **different measurements** and are not pooled for any reliability statement (`THR-19P-23`); pooled-20 numbers are descriptive and labelled "mixed handbook versions". P2 agreement is expected to be higher than P1 because Addendum B was derived from P1 adjudication; that is calibration, not independent evidence of reliability.

### 5.7 Scheduling rule

Kush and Parv also label the 400-pair identity packet (07I-C) and the Step-07 audit packet v4 (07.A). Different tasks are never interleaved in one sitting; each sitting is single-task and timed (the timing sheet's `SETUP` and task tags make this checkable).

---

## 6. Timing sheet

One row per sitting per packet, filled by the annotator at the end of each sitting (stopwatch for active time; clock for start and end). `pilot_timing_v1.csv` columns (proposed; a header-only template is in Appendix C):

`session_id, annotator_letter, packet_id, wave, phase, start_utc, end_utc, wall_minutes, break_minutes, active_minutes_self, validate_runs, replay_runs, handbook_lookups, difficulty_1_5, status_after, schema_problem_ids, note`

- `phase` in {SETUP, READ_PLAN, LABEL, VALIDATE_FIX, ADJUDICATE, OTHER}; `READ_PLAN` (reading and planning the recipe) and `LABEL` are the optional split, `VALIDATE_FIX` is the correction loop after `validate`/`replay`.
- `status_after` in {DRAFT, DONE, TIMEBOX_EXCEEDED}. **Time-box (`THR-19P-13`): 120 active minutes per recipe.** On reaching it, the annotator stops, marks `TIMEBOX_EXCEEDED`, logs the reason as a schema problem, and the recipe's time is reported as right-censored (>= 120), with and without it. A time-box is not silently extended: a recipe that does not fit 120 minutes is a finding about depth.
- `active_minutes_self` vs `wall_minutes - break_minutes` is itself logged (the ratio shows how accurate self-timing is).
- Adjudication and setup sittings are logged with phase `ADJUDICATE` / `SETUP` and count toward the 40 h cap (`THR-19P-14`).
- **Question-log time.** Each question-log entry (section 5.3) records the packet id and UTC time; the minutes spent on questions in a sitting are reported next to the sitting's active minutes.
- **Per-recipe representability checklist (`THR-19P-33`; companion sheet `pilot_representability_v1.csv`, header in Appendix C).** After labelling a recipe and before commitment, each annotator adds one row per hard-case class of the handbook's hard-example list (the classes that also appear in SSOT 237.5) that occurs in that recipe, marked FAITHFUL (the contract holds it), WORKAROUND (held only through a recorded convention) or IMPOSSIBLE (cannot be held without inventing or dropping content), plus one free row 'OTHER' for anything outside the list. It is filled after the recipe is labelled (not as a pre-read prompt), is private until both commitments exist, and its sha256 is part of the commitment. An IMPOSSIBLE mark is a BLOCKING item and must also appear in the schema-problem log; WORKAROUND marks are counted and reported as **silent schema debt** next to the BLOCKING count. The analyst-only known-gap list (section 9) is not part of the checklist, so it cannot prime the annotators.

Summaries (all reported with n and the sittings they come from): per annotator and wave: median, IQR, min-max, and the geometric mean with a 95% t-interval on ln(time); by source, stratum, tier and order index (learning effect); minutes per ingredient line and per step as a size-adjusted view; validate/replay runs per recipe; self-rated difficulty vs minutes. Two numbers go to 19-S: **t_all** (median of all 20 per annotator) and **t_P2** (median of P2, the steady-state estimate after the handbook revision and some practice). The wide interval of both is shown, not hidden: with ln-time standard deviation 0.5-0.7 the 95% interval on a 20-recipe geometric mean is about multiply-or-divide by 1.26-1.39 (13 recipes: multiply-or-divide by 1.35-1.53; 7 recipes: multiply-or-divide by 1.59-1.91; sigma_ln is an assumption, UNVERIFIED, Appendix B).

---

## 7. IAA plan

### 7.1 Field families and units

Existing tool outputs map to the SSOT §237.3 task list. "Core" and "secondary" follow the PP gates of the Plan (core >= 0.80; implicit args / state attributes >= 0.667) and are PROPOSED_PILOT (`THR-19P-17`, D19-5). The cut-offs 0.80 / 0.667 are applied to two different kinds of quantity, so they sit in two rows: Krippendorff's alpha on the **categorical** families is chance-corrected and the cut-offs are its published convention (`THR-19P-18`); F1 on the **span, event, edge, coreference and entity** families is **not** chance-corrected (for spans it equals positive specific agreement), so the same numbers are used there only as a **routing convention**, never read as equal to an alpha of the same size and never a reliability claim (`THR-19P-35`; the Plan card's single 'alpha or F1' wording is not inherited silently, D19-19). Unitizing alpha for the span families, if the report script implements it, is a diagnostic printed beside F1 and is not routed on. The column 'Routed on' says which row applies:

| Family | Existing metric (tool) | Unit | Class | Routed on |
|---|---|---|---|---|
| Ingredient-line structure: FOOD / QUANTITY / UNIT / SIZE / FORM / STATE spans | span P/R/F1 exact and relaxed, per label; char kappa | spans | core | F1 (`THR-19P-35`) |
| Canonical concept link (incl. UNKNOWN as a class) | `concept_agreement`, `unknown_disagreement_rate` | ingredient lines | core | alpha (`THR-19P-18`) |
| Quantity structure (`quantity_override`, QUANTITY/UNIT spans) | category `quantity` rate | lines | core | alpha on `quantity_override`; F1 on the QUANTITY/UNIT spans |
| Process / ACTION mapping | `process_link_f1` | events | core | F1 (`THR-19P-35`) |
| Event structure (type, arguments) | `event_f1_strict`, `event_f1_loose`, category `event_type`, `event_argument` | events | core | F1 on events and arguments; alpha on event type |
| Structural relations (Merge / Split / Reserve / Recombine) | `structural_relation_f1`, `relation_f1_all` | edges | core | F1 (`THR-19P-35`) |
| Coreference | `coref_b_cubed_f1` | mentions | secondary | F1 (`THR-19P-35`) |
| Intermediate and alive entities | `intermediate_entity_f1`, `alive_entity_f1` | entities | secondary | F1 (`THR-19P-35`) |
| Final state fields (UNKNOWN as a class) | `state_field_agreement` | state fields | secondary (state attributes) | alpha (`THR-19P-18`) |
| Implicit events (`implicit: true`) | derived from `event_f1` restricted to implicit events (new) | events | secondary (implicit args) | F1 (`THR-19P-35`) |
| Replay consistency | `replay_consistent_fraction` | recipes | validity, not agreement | none |

### 7.2 Statistics (new report script; no existing tool is edited)

For each family, always show **raw agreement, specific agreement (positive and negative), prevalence, n units, n recipes**, never one pooled score, never a kappa alone (kappa paradox; the 07H audit had three fields at prevalence 1.00):

- spans / events / edges / coref / entities: P, R, F1 (exact and relaxed for spans), micro over pooled units and macro over recipes; F1 is symmetric under swapping annotators for exact matches (P and R swap) and is **not chance-corrected** (the report prints that sentence under every F1 table; routing per `THR-19P-35`);
- categorical fields (concept link, state attributes with UNKNOWN as a class, event types): raw agreement, Cohen's kappa, **Krippendorff's alpha (nominal, with missing handled)**, Gwet's AC1, PABAK (diagnostic only), and per-class specific agreement; if the dominant-class share is >= 0.95 (`THR-19P-22`, the same prevalence value as THR-07A-03), kappa and alpha are **printed but not interpreted** and AC1/specific agreement carry the reading;
- the existing 20% category-rate review gate is reported unchanged (`THR-19P-16`, kept for comparability) and a **per-pair-normalised rate** (category rows / the units of ONE annotator; where the tool's denominator sums both annotators' units, half the sum, and where the two annotators' counts differ, their mean) is computed beside it. The review decision gates on the larger of the two (`THR-19P-31`: max(tool rate, per-pair rate) > 0.20), so the F8(b) deflation (up to 2x on matched-pair rows) can no longer hide a category. A stricter rule registered before any data exist is not a weakening of the old one: every case the old rule flags is still flagged.

### 7.3 Confidence intervals (`THR-19P-20`, `THR-19P-21`)

Unit of independence = **recipe** (one per split group by construction). Primary CI = **recipe-cluster bootstrap**, B = 10,000 resamples of recipes with replacement, percentile interval, recomputing each pooled statistic from per-recipe sufficient statistics (TP/FP/FN or agreement counts, which the new script exports per recipe); plus a leave-one-recipe-out table showing which recipe moves each statistic most. Wilson intervals on pooled units are **not** used as primary because they treat correlated units within a recipe as independent. A per-class statistic is reported only with >= 30 units from >= 5 recipes; below that, counts only, no interval, no claim. With 7 recipes (P1 alone) a percentile bootstrap undercovers; P1 intervals carry the label "7 clusters: indicative only". It undercovers with 13 clusters too, so every decision rule that reads an interval bound (the lower bound in EXTENSION-ELIGIBLE, the bound reported with the falsification rule, the upper bound in GO-40) uses the **more conservative of three intervals** computed for each statistic: the percentile bootstrap, the BCa bootstrap and a cluster-level t interval on the per-recipe statistics (df = n_recipes - 1); for a lower bound the smallest of the three lower limits, for an upper bound the largest of the three upper limits; all three are reported (`THR-19P-34`, D19-22). **All intervals are conditional on annotators A and B** (two fixed annotators who wrote or approved the handbook): they quantify recipe sampling variance only, say nothing about annotator-to-annotator variance, and do not estimate reliability for any other annotator.

### 7.4 What n supports (assumptions in Appendix B, all UNVERIFIED until data exist)

| Question | n | Supported | Not supported |
|---|---|---|---|
| Pooled event/edge/span F1 near 0.85 | 20 recipes, 8-30 units each, ICC 0.1-0.3 | 95% half-width about +/-0.06 to +/-0.10 | claims about differences < 0.1 |
| Same, P2 alone | 13 recipes | about +/-0.07 to +/-0.12 | |
| Same, P1 alone | 7 recipes | about +/-0.10 to +/-0.17 | anything beyond "indicative" |
| Kappa/alpha on a categorical field, balanced (p_o 0.90, p_e 0.5) | n_eff ~139 units for +/-0.10 | feasible only for frequent fields (line concept link, event types) | rare categories; state attributes with high UNKNOWN prevalence |
| Kappa at high prevalence (p_o 0.95, p_e 0.8) | n_eff ~457 units for +/-0.10 | **not reachable** in 20 recipes; use AC1 and specific agreement | any "kappa >= 0.80" statement |
| Rate of unrepresentable phenomena | 0 observed in 20 recipes | one-sided 95% upper bound 13.9% of recipes **in the pilot design population** (stratified; P2 coverage-enriched; 7 recipes: 34.8%; 13: 20.6%); not a corpus rate | "the schema is complete"; any corpus-level rate |
| Minutes per recipe | 20 recipes | geometric mean multiply-or-divide by 1.26-1.39 (sigma_ln 0.5-0.7) | stratum-specific times |
| Detecting a category above the 20% review gate | denominators in the hundreds of spans, tens of events | gross problems (a category at 30-40%) | borderline categories (15-25%) |

### 7.5 Reporting template (`pilot_iaa_report.md`)

Per wave and pooled-descriptive: provenance verdict first; table per family (n units, n recipes, raw, specific +/-, prevalence, kappa/alpha/AC1 or F1 with bootstrap CI, flag); disagreement categories with counts, existing-rule rate, per-pair-normalised rate; leave-one-out influence; the timing summary; the schema-problem summary; an explicit "claims not made" paragraph. The header of every interval table prints "Intervals are conditional on annotators A and B; they do not estimate reliability for other annotators", and every F1 table prints "F1 is not chance-corrected; the 0.80 / 0.667 cut-offs are a routing convention". The report also lists the representability checklist counts (FAITHFUL / WORKAROUND / IMPOSSIBLE; WORKAROUND = silent schema debt), the BLOCKING items dismissed at adjudication, the three intervals of `THR-19P-34`, and the question-log counts and minutes. All IAA is labelled **DIAGNOSTIC** (G19.P(4)). Negative or poor results are reported and kept (R-19).

### 7.6 Using the existing tools without editing them

`gold_pilot_agreement.py main(argv, gold: Path)` reads `<gold>/pilot_20/{Kush,Parv}/<id>.<who>.json` and `<gold>/pilot_20_manifest.csv`. A thin wrapper (to be written) stages **derived copies** into a scratch layout with that shape *after* the sealed key is opened, runs `--tag p1` / `--tag p2` (outputs `pilot_20_<tag>_*`), and deletes nothing from the originals. The tool refuses (exit 2, BLOCKED_HUMAN) until all selected recipes are DONE and valid for both, which is the behaviour wanted. Files named `Kush` / `Parv` in the staging layout are an artefact of the tool; the report uses annotator letters.

---

## 8. Adjudication

- **Who/when:** Kush and Parv jointly, after both commitments and the provenance verdict; one wave at a time. Expert or third reviewer for cultural/regional cases (Indian, historical or Wikibooks regional terms) is optional (0-4 h; D19-6); if used, their role is "tie-break reviewer", recorded.
- **Sheet:** the tool's `*_disagreements.csv` extended with the template column `handbook_version_at_annotation` (the template has it; the tool's writer does not). Per row: `adjudicated`, `rationale` as a class (HANDBOOK_RULE_APPLIES / ERROR_A / ERROR_B / BOTH_VALID_AMBIGUOUS / HANDBOOK_GAP / SCHEMA_GAP / SOURCE_DEFECT) plus free text, `handbook_rule`, who decided, date, handbook version. **100% of rows completed** before the set is called adjudicated (`THR-19P-24`).
- **Preservation:** pre-adjudication labels are never edited (hash-committed originals); adjudicated recipes are new files `<id>.ADJUDICATED.json` with `annotator: "ADJUDICATED"`; the change log lists who / why / version for every changed field.
- **Then:** `validate` + `replay` on every adjudicated file, Step-18 replay determinism (twice, identical), lock by hash, group lock (section 4.7).
- **Limitations stated:** the adjudicators are the annotators and the handbook authors; adjudication time is logged and counts toward the cap; the adjudicated set is not independent of its own annotators and is **not** a test set.
- **Recurring rules:** a disagreement class recurring >= 3 times becomes a handbook rule in Addendum B (handbook section 7).
- **Schema-problem items:** the merged schema-problem log (section 9) is adjudicated in the same sitting: every item gets a `field_family` (the section 7.1 family) and an `adjudication_class` (SCHEMA_GAP / HANDBOOK_GAP / SOURCE_DEFECT / BOTH_VALID_AMBIGUOUS / NOT_A_PROBLEM). An item logged by only one annotator can be downgraded or dismissed only with a written rationale, and every dismissed BLOCKING item is listed in the report, so that the people with an incentive to under-report cannot do it silently (`THR-19P-32`).

---

## 9. Schema-problem log

Each annotator keeps a **private** log while annotating (no discussion until both commitments exist), then the logs are merged at adjudication; this keeps the log itself independent and lets a problem found by both be counted as convergent evidence.

`pilot_schema_problem_log` columns (proposed; template in Appendix C): `sp_id, wave, packet_id, logged_by (A|B|JOINT), unit (line/step/event/entity/global), category, severity, handbook_rule_ref, what_the_annotator_did, proposed_fix, owner_step (16a/16b/16c/17/18/handbook), convergent (A|B|BOTH), field_family, adjudication_class, triage_status, triage_note, date` (`field_family` and `adjudication_class` are filled at adjudication; they are what `THR-19P-32` counts).

- **category:** UNREPRESENTABLE_PHENOMENON (the text states something the contract cannot hold); AD_HOC_FIELD_NEEDED; AMBIGUOUS_HANDBOOK_RULE; VOCAB_GAP (PROC / TOOL / ING / UNIT / SVAR); QUANTITY_MODEL_GAP; COREF_OR_ENTITY_GAP; STATE_VARIABLE_GAP; TOOLING_ISSUE (validate / replay / template); SOURCE_TEXT_DEFECT (missing listed ingredient, corrupted step); TIMEBOX_EXCEEDED; OTHER.
- **severity:** BLOCKING (cannot annotate faithfully without inventing or dropping content; an IMPOSSIBLE mark in the representability checklist is always BLOCKING), WORKAROUND (annotated with a recorded convention; counted as silent schema debt, `THR-19P-33`), COSMETIC.
- **triage (every item, `THR-19P-25`):** OPEN -> TRIAGED_TO_16A / TRIAGED_TO_16B / ADDENDUM_B / TOOLING_BACKLOG / SOURCE_DEFECT_NO_ACTION / WONTFIX_WITH_REASON. 16c consumes the log (Plan Step 16 card, G16.1: 0 unrepresentable phenomena and 0 ad-hoc fields at freeze; the pilot measures how far v0 is from that).
- **Known-gap list (analyst-only, sealed from annotators until their logs are done, to avoid priming):** the v0 gaps the plan already lists — QNT has scalar `mass_g` only; POR has no low/high; ENTITY has no parentage/lifecycle; PROC is flat with ENDPOINT mixed in; no event_kind, modality, alternative groups, implicit-argument flag, conditional/parallel relations. The report computes a "known-gap hit rate" and, separately, the **unexpected** problems (more informative).
- **Representability reading:** G16.1 is zero-tolerance, the pilot is n = 20: report counts of BLOCKING items **and of WORKAROUND items (silent schema debt)**, the rule-of-three bound if zero (Section 7.4; it applies to the pilot design population only), and the UNCOVERED hard-case classes (section 4.5) as "not exercised", not "handled". The routing rule counts adjudicated BLOCKING items on a field family in >= 2 recipes **whoever logged them** (`THR-19P-32`); the older rule that needs three distinct categories logged by both annotators (`THR-19P-26`) stays as a supplementary trigger, because convergence is a high bar: a problem seen only by the more careful annotator, or logged as WORKAROUND by an annotator who wrote the handbook, would otherwise never count.
- **Source defects** (the Food.com audit found missing listed ingredients in 14 of 20 recipes) are logged but are not schema problems unless the contract cannot hold them honestly (e.g. a step-only entity); S118 handled those as `STEP_ONLY_ENTITY` notes.

---

## 10. Decision rules

### 10.1 Within-pilot stops and checks

| Trigger | Action |
|---|---|
| Provenance FAIL on P1 | stop; wave `NOT_COUNTED`; re-issue P1 on fresh recipes; P2 not started |
| P1 category rate > 0.20 by the tool's rate (`THR-19P-16`) or by the per-pair-normalised rate (`THR-19P-31`; max rule) | `HANDBOOK_REVISION_REQUIRED`: Addendum B before P2 |
| After P1: projected pilot hours per annotator = (P1 hours so far + 13 x P1 median minutes / 60 + adjudication estimate + setup) > 40 h | pause; `NEED_HUMAN_CAPACITY` decision (shrink P2, or approve an exception) before P2 is issued (`THR-19P-15`) |
| Any BLOCKING item (including any IMPOSSIBLE checklist mark) | logged and triaged; annotation continues with the recorded workaround (no ad-hoc fields invented); counted in 10.2 |
| A recipe hits the 120-min time-box | stop that recipe, `TIMEBOX_EXCEEDED`, right-censor, log |

### 10.2 End-of-pilot outcome (information for 16c and 19-S; **not an authorisation**) (`THR-19P-18`..`19`, `26`..`28`, `31`..`35`)

| Outcome | Condition (all PROPOSED_PILOT) | Consequence |
|---|---|---|
| **STOP-INVALID** | provenance FAIL on a wave | wave `NOT_COUNTED`; fresh recipes; no claims |
| **STOP-SCHEMA** | any of: (i) point estimate of alpha (categorical families, `THR-19P-18`) or of F1 (span / event / edge families, `THR-19P-35`; routing convention, not chance-corrected) < 0.667 on a **core** field in **both** waves (G16.5); (ii) >= 2 recipes each carrying an adjudicated SCHEMA_GAP or HANDBOOK_GAP item of severity BLOCKING on the same field family, **whoever logged it** (`THR-19P-32`); (iii) >= 3 distinct BLOCKING categories logged by both annotators (`THR-19P-26`, retained as a supplementary trigger) | escalate to Step 16: contract incoherent for that field; field demoted to descriptive/Gold-Light; no 16c freeze on it; a mini-wave of <= 5 NEW recipes after redesign (never re-score the same recipes as independent) |
| **REVISE** | 0.667 <= alpha (`THR-19P-18`) or F1 (`THR-19P-35`) < 0.80 on a core field in P2, or a category still above 20% by max(tool rate, per-pair rate) (`THR-19P-31`) | handbook Addendum C / revision; field "tentative" for 19-M; re-measure on a NEW subset inside 19-M |
| **GO-40** | provenance PASS; no STOP; and N x t_P2 (Kush, Parv separately; with the upper t-interval) plus the adjudication projection <= the per-annotator budget B_h a human declares | 19-S may choose N <= 40 (the current mandate, MP AH6 course minimum) |
| **NEED_HUMAN_CAPACITY** | hours would exceed 40 h in the pilot, or N = 40 does not fit B_h | keep the achieved size with honest intervals; downgrade dependent claims (G16-CAL, Step 36 calibration) to descriptive (Step 19 fail action) |
| **EXTENSION-ELIGIBLE (information only)** | provenance PASS in both waves; P2 core-field point estimate >= 0.80 **and** lower 95% bound >= 0.667 (the most conservative of the three intervals of `THR-19P-34`; conditional on annotators A and B); 0 open BLOCKING items; N x t_P2 fits B_h | the humans may *consider* a separate **H5 / H8** decision for N = 100 / 200 etc. The pilot never authorises it, and cannot certify 0.80 (n = 20) |

### 10.3 19-S inputs the report hands over

Hours per annotator for N recipes = N x t (Appendix B shows N = 20, 40, 100, 200 at t = 30, 45, 60, 90 min: N = 40 costs 20-60 h annotation at 30-90 min), plus adjudication hours from (disagreements per recipe) x (minutes per disagreement measured in the pilot), plus 8-12 h for session review (Plan 19-M formula, UNVERIFIED). The pilot replaces the ranges by measurements with intervals; the plan's 15-25 min (PILOT_20_TASK, v1 depth) vs 30-90 min (Deep Gold estimate) disagreement is exactly what the timing sheet resolves.

### 10.4 What the pilot can and cannot authorise

It can inform: 16c (consume the schema-problem log, timing, IAA; re-encode the 20 recipes in v1 for the representability audit), and the 19-S sizing. It cannot authorise: starting 19-M (H5), sizing N > 40 (H5/H8), changing the tier registry (19-R, H4), lifting any Step-07/Step-17 dependency, or any reliability claim.

---

## 11. Hours and the cap

Plan card: pilot Kush 16-38 h, Parv 16-38 h (annotation 10-30 h = 20 recipes x 30-90 min, + joint adjudication 4-6 h + design approval ~2 h), expert 0-4 h; Plan section 4.5 lists 19-D design at 2-3 h each. This draft adds **1 h setup** per annotator (packet check, handbook re-read, commitment step; PROPOSED).

Per-annotator total = 20 x t/60 + adjudication + 1 + 2. Appendix B table: the **40 h cap binds at about t = 93 min per recipe** with 6 h adjudication (at 90 min: 39 h; at 60 min: 27-29 h; at 45 min: 22-24 h; at 30 min: 17-19 h). If the first wave shows t > ~90 min, 13 further recipes at that pace would breach the cap, which is why the capacity check (`THR-19P-15`) sits between P1 and P2. All hour figures are UNVERIFIED until the pilot; the weekly capacity of Kush and Parv is not recorded anywhere and must be set by Kush (Plan section 4.5; D19-8).

---

## 12. Planned outputs and tooling (nothing created now)

| Planned artefact | Notes |
|---|---|
| `registry/recipe_semantics/deep_gold_pilot_frame_v1.csv` (text-free) + `frame_sha256` | Step 16b/19-D shared frame; also feeds 16b's `deep_gold_sampling_frame_v1.csv` |
| `registry/recipe_semantics/deep_gold_pilot_tag_rules_v1.csv` | stratum and hard-case tag rules, human-reviewed |
| **Tracked, text-free:** `registry/recipe_semantics/deep_gold_pilot_v1/{manifest_<wave>.csv, commitments_<letter>_<wave>.json, sealed_key_<wave>.sha256}` (ids, hashes, sizes, times only; not ignored, verified with `git check-ignore -v`) | review A #5; the plan card's output layout puts these under `annotation/gold/`, which `.gitignore:9` ignores, so the plan card needs the path reconciled by the integrating session (D19-18) |
| **Git-ignored, local only:** `annotation/gold/deep_gold_pilot_v1/{A,B,adjudicated}/` (labels, recipe text) and the sealed key file | D-007 |
| `reports/step19/{pilot_iaa_report.md, pilot_timing_v1.csv, pilot_representability_v1.csv, pilot_schema_problem_log.md, pilot_provenance_check.json}` | card outputs (+ the representability sheet, `THR-19P-33`) |
| **Six scripts** in `tools/`, to write after approval (D19-9): (1) frame builder + seeded draw; (2) packet maker + sealed key (blank templates, separate ids, per-annotator order, locale per source); (3) commit step (commitments with provenance values, `snapshot` subcommand); (4) provenance checker + `tests/` planted-pair test; (5) agreement wrapper; (6) pilot report script (CIs incl. the three intervals, alpha, AC1, specific agreement, timing, influence) | reuse, never edit: `gold_cli.py`, `gold_pilot_agreement.py`, `bundle_gold_packs.py`, `make_independent_gold_packs.py`; env: the frame and packet steps need the machine that holds the recipe text (BBC: Mac only, F9) |

---

## 13. Risks and honest limitations

1. n = 20 is feasibility evidence; every IAA number is wide and DIAGNOSTIC; no sentence in the report may read as a reliability claim.
2. The annotators share a handbook they wrote or approved and have seen AI drafts of 40 other recipes: agreement overstates reliability for outsiders and may carry a style prior.
3. P2 follows an Addendum B derived from P1: its agreement is post-calibration.
4. Adjudication by the annotators is not independent and is not a test set; the pilot set is dev-only by lock.
5. The coverage-enriched P2 biases timing upward (conservative for capacity, not representative).
6. Food.com's licence status and the S116 eligibility screen are unresolved; BBC text is local-only and not on this server; Gutenberg and TASTEset cannot be represented.
7. The existing agreement tool has the F8 properties; a mistaken read of its default independence label or of its deflated rates is the main way the pilot could mislead; the report script and the provenance gate exist to prevent that.
8. Time-boxing right-censors the hardest recipes; the censored count must be shown with any time summary.
9. Shared humans: an interleaved packet (07.A, 07I-C) would contaminate timing and invite fatigue; section 5.7 forbids it.
10. Schema problems are easy to under-detect (representability is the pilot's most decision-relevant output for 16c): the adjudicated, any-logger rule (`THR-19P-32`), the representability checklist and the silent-schema-debt count (`THR-19P-33`) exist for that reason; zero BLOCKING items still bounds the rate only to 13.9% of the design population.
11. The independence evidence is partly self-attested (recorded mtimes, snapshots); the external anchors are the git timestamps of the tracked commitments (PV-9) and the interim snapshot history (PV-10); a determined annotator could still fabricate a history, which is why a REVIEW outcome needs a written statement and why nothing here is called a certificate.

---

## 14. Open decisions for humans (checklist in `reports/step19/README.md`)

| Id | Decision | Default in this draft |
|---|---|---|
| D19-1 | Approve the frame: sources (BBC, Food.com under S116 Gate 1, Wikibooks), caps (4-20 lines, 2-15 steps), quotas 6/10/4 and tiers 5/9/6 | as drafted |
| D19-2 | Confirm the exclusion list is the superset (50 Gold-index ids + 90 screened-pool ids + groups + title twins), i.e. "20 AI-assisted Food.com ids" is a subset | superset |
| D19-3 | Kush supplies the seed nonce **before** the frame is inspected; who runs the draw | Kush nonce; agent builds frame |
| D19-4 | Accept the stated exposure limitation (40 AI-drafted recipes seen by Kush; Parv approval relayed); or attest otherwise for specific recipes | accept as limitation |
| D19-5 | Core vs secondary field classes and the 0.80 / 0.667 routing (`THR-19P-17`..`19`, `35`) | as drafted |
| D19-6 | Third reviewer/expert for cultural cases (0-4 h) | optional, off |
| D19-7 | 120-minute time-box with right-censoring | on |
| D19-8 | Weekly hour capacity per person; P1 within 30 days; P2 after 07I-C closes | Kush to set |
| D19-9 | Authorise the agent to write the **six scripts** of section 12 (1 frame builder + seeded draw, 2 packet maker + sealed key, 3 commit step, 4 provenance checker + planted-pair test, 5 agreement wrapper, 6 pilot report script) for human review (no recipe text leaves the machine) | not authorised until H5 |
| D19-10 | P2: coverage-greedy (default) vs pure stratified random | coverage-greedy |
| D19-11 | Confirm BBC and Food.com pilot content stays local-only; Gold text release blocked until H2 (SSOT §250.7) | local-only |
| D19-12 | Confirm the exposed S116 blank bundle is **not** reused | not reused |
| D19-13 | Name/status for the adjudicated pilot set in tier registry v2 (19-R; H4) | `pilot development Gold, blind two-annotator (independent only if pilot provenance check PASS), prior AI exposure of annotators recorded, design pilot` (proposal only) |
| D19-14 | Keep the existing tool's 20% rule (`THR-19P-16`, unchanged, kept for comparability) and gate on max(tool rate, per-pair-normalised rate) > 0.20 through the new row `THR-19P-31` (which supersedes `THR-19P-16` for gating only), or choose differently (a different gate needs a new threshold row, not an edit) | keep + max rule |
| D19-15 | Pilot runs on the CURRENT contract (no pre-pilot handbook edits) | current contract |
| D19-16 | Timing breakdown by phase (READ_PLAN / LABEL / VALIDATE_FIX) vs a single total per sitting | phases optional |
| D19-17 | The `S_max = 500` sub-blocking clause of `THR-19P-04` (Plan 'Reading conventions' conflict #4: R-08 versus the giant-component guard; the value was fixed after the largest component, 261, was seen): confirm or drop | drop if not confirmed (whole component excluded; no effect today) |
| D19-18 | Tracked location of the independence artefacts: `registry/recipe_semantics/deep_gold_pilot_v1/` (manifests, commitments, sealed-key hash; `.gitignore:9` ignores the plan card's `annotation/gold/deep_gold_pilot_v1/`, `.gitignore` not edited) and check PV-9 (`git ls-files --error-unmatch`); the integrating session reconciles the plan card's output path | tracked path + PV-9 |
| D19-19 | Split the routing cut-offs: alpha on categorical families (`THR-19P-18`) and F1 on span / event / edge families as a routing convention only (`THR-19P-35`); optional unitizing alpha as a diagnostic | split |
| D19-20 | STOP-SCHEMA: add the any-logger adjudicated rule (`THR-19P-32`), keep `THR-19P-26` as a supplementary trigger, and add the per-recipe representability checklist and silent-schema-debt count (`THR-19P-33`) | add |
| D19-21 | Commitment-time provenance values (packet id, sha256, size, mtime) and >= 2 interim snapshots per file (PV-3 now runs on the recorded values; PV-10); the extra annotator effort (`snapshot` at first `validate` and at `DONE`) | on |
| D19-22 | Interval rule for every decision that reads a bound: the more conservative of percentile, BCa and cluster-level t intervals (`THR-19P-34`) | on |
| D19-23 | Question log is write-only during a wave; answers only after both commitments; no convention change inside a wave (anchoring control) | on |
| D19-24 | Register `DGP-` as a local packet label (not a ledger id) in the 04.9-min section 4 table, or rename it to a file-name token, and re-run the section 5 collision scan | register as local label |
| D19-25 | PV-7 (identical-codes check) restricted to fields with dominant-class share < 0.95; chance-corrected identity (p_o - p_e) / (1 - p_e) >= 0.98 for the others | restricted |

---

## Appendix A. Proposed rows for `registry/preregistered_thresholds_v1.csv` (Step 01.6) — NOT written to the CSV

All rows: `registry_status = DRAFT_PENDING_H4`, `value_status = PROPOSED_PILOT`, unsigned (`signed_by`, `signed_at`, `commit` empty). `data_seen_before_registration` = `N` (no pilot data exists; no recipe has been drawn) except rows that depend on counts read from data (frame counts, the 50 gold-index ids, the 90 screened-pool ids, component sizes), marked `DESCRIPTIVE_COUNTS_SEEN` (the aggregate frame counts of section 2, F5, were read; no label, timing or agreement exists). Ids follow the `THR-<step>-NN` pattern (`19P` = 19-pilot; final namespace owned by 01.3). Round-3 revision: rows `THR-19P-31..35` are new; rows 03, 04, 05, 11, 12, 16, 17, 18, 19, 20, 26 and 28 were changed or annotated (all are unsigned drafts, so no signed row was edited); `THR-19P-16` is kept and marked superseded for gating by `-31`; `THR-19P-18` now covers alpha only and `-35` carries the F1 routing (the review's '18a / 18b'); `THR-19P-26` is retained as a supplementary trigger beside `-32`. A changed row only adds a trigger, a check or a label: none relaxes a gate.

```csv
threshold_id,registry_status,step,quantity,value,value_status,rationale,source,data_seen_before_registration,signed_by,signed_at,commit,ci_rule,unit_of_independence,n_min,supersedes
THR-19P-01,DRAFT_PENDING_H4,19-D,Pilot size and waves,20 fresh recipes = wave P1 7 (one per existing stratum) + wave P2 13,PROPOSED_PILOT,Plan card value (MP AH6 design pilot; X6). Not a reliability certificate: n = 20 cannot certify alpha/F1 >= 0.80.,docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card; reports/step19/deep_gold_pilot_design_v1_draft.md s3,N,,,,,recipe (one per split group),,
THR-19P-02,DRAFT_PENDING_H4,19-pilot,Frame eligibility,"exact-duplicate representative; source in {A1_BBC_GOOD_FOOD, FOODCOM, WIKIBOOKS}; has ingredients and instructions; 4-20 ingredient lines; 2-15 steps; text present on the annotating machine",PROPOSED_PILOT,"Caps keep one recipe from dominating hours and widen the old pilot filter (<= 14 lines, <= 8 steps; make_gold_batch.py). GUTENBERG_SEGMENT (0 ingredient lines) and TASTESET (0 steps) are structurally ineligible. Aggregate frame counts were read, no label or timing exists.",reports/step19/deep_gold_pilot_design_v1_draft.md s2 F4 F5 s4.1,DESCRIPTIVE_COUNTS_SEEN,,,,,recipe,,
THR-19P-03,DRAFT_PENDING_H4,19-pilot,Exclusion list (applied before any draw),"50 ids of gold_recipe_index_v1 (20 BBC pilot_20 incl. 7 calibration, 20 Food.com AI-assisted, 10 Food.com expansion candidates) + 90 further S116 screening-pool Food.com ids + every member of their fallback/07I-S group + exact normalised-title twins",PROPOSED_PILOT,"Exposure rule (Plan Phase D fact 1; CHG-19-4). A superset of the brief's ""20 AI-assisted Food.com ids"" and of the card list (40 AI-assisted, 7 calibration, S116 20, title twins). Built from ids and counts read from data (50 ids of gold_recipe_index_v1, 90 screened-pool ids of the S116 log, F2/F3/F7); no label, timing or agreement exists.",reports/step19/deep_gold_pilot_design_v1_draft.md s4.2; reports/gold/foodcom_v1_1_review_record.json; annotation/gold/evidence_first_expansion/screening_log.csv,DESCRIPTIVE_COUNTS_SEEN,,,,,split group,,
THR-19P-04,DRAFT_PENDING_H4,19-pilot,Grouping and one-per-group,"at most 1 recipe per split_group_id (07I-S SPLITGRP-REC-) or, before it exists, per connected component of exact duplicate group + provisional family + dish-family candidate + same normalised title; if a component with an excluded id exceeds S_max = 500 recipes exclude only exact/family/title-tied members",PROPOSED_PILOT,"R-08. Component sizes at id level (no titles): max 261; the 50 Gold-index recipes sit in components of 129 recipes in total. S_max is a safeguard, not tuned. S_max = 500 was fixed after the largest component (261) was seen; Plan 'Reading conventions' conflict #4 (R-08 vs the giant-component guard) says a sub-blocking rule could be read as tuning to obtain usable sizes and humans must confirm (D19-17). If not confirmed the clause is dropped and the whole component is excluded (stricter).",reports/step19/deep_gold_pilot_design_v1_draft.md s4.3 F7,DESCRIPTIVE_COUNTS_SEEN,,,,,split group,,
THR-19P-05,DRAFT_PENDING_H4,19-pilot,Source quota,"A1_BBC_GOOD_FOOD 6; FOODCOM 10; WIKIBOOKS 4 (P1: 2/3/2, P2: 4/7/2)",PROPOSED_PILOT,"Deliberately not proportional to the corpus (Food.com 85%): editorial BBC text, user-text Food.com with defects, Wikibooks (CC BY-SA 4.0; release CONDITIONAL on attribution, share-alike and H2). Food.com use rests on the S116 Gate-1 local-research decision.",reports/step19/deep_gold_pilot_design_v1_draft.md s4.4,DESCRIPTIVE_COUNTS_SEEN,,,,,recipe,,
THR-19P-06,DRAFT_PENDING_H4,19-pilot,"Complexity index, tiers and tier quota",c = n_ingredient_lines + 2 * n_steps; LOW c <= 14; MID 15 <= c <= 24; HIGH c >= 25; quota LOW 5 / MID 9 / HIGH 6 (P2 3/6/4),PROPOSED_PILOT,Count-only index fixed before the draw; round cutpoints; every tier is populated in each source (frame counts read). Not tuned to any outcome.,reports/step19/deep_gold_pilot_design_v1_draft.md s4.4 F5,DESCRIPTIVE_COUNTS_SEEN,,,,,recipe,,
THR-19P-07,DRAFT_PENDING_H4,19-pilot,P1 cells (stratum x source x tier),baking FOODCOM MID; drain_discard BBC LOW; indian WIKIBOOKS MID; multi_component FOODCOM HIGH; random BBC MID; reserve_split FOODCOM HIGH; simple WIKIBOOKS LOW. Strata regexes exactly as tools/make_gold_batch.py; indian = explicit cuisine label Indian/Indic; fall-through order FOODCOM -> BBC -> WIKIBOOKS if a cell has < 30 eligible,PROPOSED_PILOT,"Card: P1 = 7 recipes, one per existing stratum, mechanical pre-registered seeded draw. Source and tier fixed per cell so the quotas stay feasible. Food.com has no cuisine label, so the Indian cell cannot come from it.",reports/step19/deep_gold_pilot_design_v1_draft.md s4.4; tools/make_gold_batch.py STRATA,DESCRIPTIVE_COUNTS_SEEN,,,,,recipe,30 eligible per cell,
THR-19P-08,DRAFT_PENDING_H4,19-pilot,Draw seed rule,seed = first 8 bytes of SHA-256(frame_sha256 || wave label || human nonce written into the signed row before the frame is built); stable shuffle inside each cell; first unused-group candidate is drawn; the next 2 per cell are ordered reserves,PROPOSED_PILOT,"Pre-registered seeded draw (card); the agent that builds the frame never chooses the seed; S102 used first-by-(stratum, recipe_id).",reports/step19/deep_gold_pilot_design_v1_draft.md s4.5,N,,,,,recipe,,
THR-19P-09,DRAFT_PENDING_H4,19-pilot,Reserve use,"replacement only before annotation starts and only for source corruption, duplicate found after freeze, template cannot hold the recipe, text unavailable on the machine, or exposure discovered; never for difficulty or model failure; reason and decider logged",PROPOSED_PILOT,Same rule as the S116 selection protocol.,reports/step19/deep_gold_pilot_design_v1_draft.md s4.6; annotation/gold/evidence_first_expansion/selection_protocol_v1.md,N,,,,,recipe,,
THR-19P-10,DRAFT_PENDING_H4,19-pilot,Hard-case coverage,"reported, not enforced: P2 chosen by seeded greedy coverage of mechanically taggable SSOT s237.5 classes; classes with 0 occurrences are listed UNCOVERED; no redraw for coverage",PROPOSED_PILOT,"Card says ""checked against the s237.5 list"". Redrawing for coverage would tune the sample to the schema. P2 is therefore coverage-enriched (open decision D19-10).",reports/step19/deep_gold_pilot_design_v1_draft.md s4.5; SSOT s237.5,N,,,,,recipe,,
THR-19P-11,DRAFT_PENDING_H4,19-pilot,Provenance-validity checks (counts_as_pilot_provenance),"FAIL: identical file bytes (PV-1); recorded mtime (written into the commitment at commitment time) outside the timing-sheet window or after the commitment (PV-3); commitment after the sealed key was opened (PV-6); a commitments file not tracked in git, or committed after the sealed key was opened (PV-9). REVIEW: identical normalised label content in > 10% of recipes (PV-2); active minutes < 5 per recipe (PV-4); authorship not separate (PV-5); a field with >= 100 cells and dominant-class share < 0.95 with >= 98% identical codes and identical marginals, or a field with dominant-class share >= 0.95 with chance-corrected identity (p_o - p_e) / (1 - p_e) >= 0.98 on >= 100 cells (PV-7); a label file with fewer than 2 hashed interim snapshots or a final snapshot hash different from the committed hash (PV-10)",PROPOSED_PILOT,"Pattern of step07h_human_gate_result.json (counts_as_human_gate): two files 11 s apart, 899/900 cells identical. FAIL => wave NOT_COUNTED (07H precedent). The five-minute and 98% values are plausibility floors, not literature values. Round-3 changes: PV-3 runs on values recorded at commitment (file mtimes do not survive git checkout, cp or scp and are forgeable by touch); PV-9 adds a git timestamp that someone other than the annotator can check; PV-10 adds an interim history against whole-file copies; PV-7 is chance-corrected for high-prevalence fields so it does not fire on natural near-identity (a field with p_e = 1 is skipped and listed, not dropped). Every earlier trigger remains.",reports/step19/deep_gold_pilot_design_v1_draft.md s5.4 s5.5; reports/step07/step07h_human_gate_result.json,N,,,,,packet / recipe,20 recipes (7 in P1),
THR-19P-12,DRAFT_PENDING_H4,19-pilot,Planted-pair test of the provenance checker,"100% detection of a planted identical-file pair, a planted 11-second pair, a planted identical-content pair, a planted commitments file not tracked in git (PV-9 FAIL) and a planted label file without interim snapshots (PV-10 REVIEW); 0 false positives on a planted clean pair; the checker is unusable until this passes",PROPOSED_PILOT,Card pass gate G19.P(1) requires a planted-pair unit test.,reports/step19/deep_gold_pilot_design_v1_draft.md s5.5 PV-8; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (Pass gate),N,,,,,synthetic fixture,,
THR-19P-13,DRAFT_PENDING_H4,19-pilot,Per-recipe time-box,"120 active minutes; on reaching it the annotator stops, marks TIMEBOX_EXCEEDED, logs a schema problem; time is right-censored and reported with and without",PROPOSED_PILOT,Prevents one recipe from consuming the cap; a recipe that does not fit is a finding about depth. 120 min = upper end of the Deep Gold 30-90 min estimate plus 30 min.,reports/step19/deep_gold_pilot_design_v1_draft.md s6,N,,,,,recipe-annotator,,
THR-19P-14,DRAFT_PENDING_H4,19-pilot,Hard hour cap per annotator,"40 h including setup, annotation, validate/replay, and joint adjudication; else NEED_HUMAN_CAPACITY",PROPOSED_PILOT,"Plan card G19.P(5), unchanged. Setup 1 h added by this draft.",docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (Pass gate G19.P(5)); reports/step19/deep_gold_pilot_design_v1_draft.md s11,N,,,,,annotator,,
THR-19P-15,DRAFT_PENDING_H4,19-pilot,Capacity check between P1 and P2,projected hours = P1 hours so far + 13 * P1 median minutes / 60 + adjudication estimate + setup; if > 40 h pause and decide before issuing P2,PROPOSED_PILOT,At 6 h adjudication the cap binds at about 93 min per recipe.,reports/step19/deep_gold_pilot_design_v1_draft.md s10.1 s11 Appendix B,N,,,,,annotator,,
THR-19P-16,DRAFT_PENDING_H4,19-pilot,"Handbook review gate (existing tool rule, unchanged; superseded for gating by THR-19P-31, kept for comparability)","a disagreement category > 20% of its relevant units => HANDBOOK_REVISION_REQUIRED (tools/gold_pilot_agreement.py GATE_RATE = 0.20, tool denominators); this rate is still computed and reported, and the gate fires on max(this rate, THR-19P-31 rate)",PROPOSED_PILOT,"Verbatim existing rule (S102 gate). The tool sums both annotators' units in most denominators, so the rule is harder to trigger than a per-pair reading (up to 2x on matched-pair rows); THR-19P-31 adds the per-pair rate to the gate. This row is not weakened: every case it flags is still flagged.",reports/step19/deep_gold_pilot_design_v1_draft.md s5.6 s7.2 F8; tools/gold_pilot_agreement.py,N,,,,none in the gate (point rate); report cluster-bootstrap CI beside it,category rate,,
THR-19P-17,DRAFT_PENDING_H4,19-pilot,Core vs secondary field classes,"core: ingredient-line spans, canonical concept link, quantity structure, ACTION/process mapping, event structure, merge/split/reserve/recombine relations; secondary: coreference, intermediate/alive entities, final state attributes, implicit events",PROPOSED_PILOT,"Plan PP split (core >= 0.80; state attributes and implicit args >= 0.667). Definition of ""core"" for the pilot falsification rule. Routing quantity per family: alpha for categorical families (THR-19P-18), F1 for span / event / edge / coreference / entity families (THR-19P-35).",reports/step19/deep_gold_pilot_design_v1_draft.md s7.1; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (Pass gate G19.M),N,,,,,field family,,
THR-19P-18,DRAFT_PENDING_H4,19-pilot,"Routing thresholds on Krippendorff's alpha (categorical families: concept link, event type, quantity_override, final state fields)","alpha >= 0.80 reportable as met (diagnostic); 0.667 <= alpha < 0.80 => handbook revision and re-measure on NEW recipes; alpha < 0.667 => redesign or demote field. The F1 families are routed by THR-19P-35, not by this row",PROPOSED_PILOT,"Krippendorff (2004) convention for chance-corrected agreement, used for routing only; the pilot certifies nothing. Round-3 split: the Plan card applied one pair of cut-offs to 'alpha or F1', quantities on different scales (an F1 of 0.70 and an alpha of 0.70 do not mean the same).",reports/step19/deep_gold_pilot_design_v1_draft.md s7 s10.2; reports/master_plan/working_notes/research/r_recipe_semantics_gold.md Q7; Audit v2 M.8,N,,,,recipe-cluster bootstrap (THR-19P-20),recipe,see THR-19P-21,(F1 part moved to THR-19P-35; own earlier draft combined wording; row never signed)
THR-19P-19,DRAFT_PENDING_H4,19-pilot,Pilot falsification rule (G16.5),"point estimate of alpha (THR-19P-18 families) or F1 (THR-19P-35 families; routing convention) < 0.667 on a core field in both waves => STOP the Step 16 freeze for that field; plus report whether the upper 95% bound (most conservative of the three intervals, THR-19P-34) is also < 0.667",PROPOSED_PILOT,"Plan Step 16 G16.5 falsification rule, unchanged; P1 alone (7 recipes) is indicative only.",reports/step19/deep_gold_pilot_design_v1_draft.md s10.2; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 16 card (Pass gate G16.5),N,,,,point estimate for the rule; bootstrap interval reported,recipe,7 (P1) and 13 (P2) recipes,
THR-19P-20,DRAFT_PENDING_H4,19-pilot,Confidence interval method,"recipe-cluster bootstrap, B = 10000, percentile interval (plus BCa and cluster-level t interval, reported together; rules that read a bound use THR-19P-34), recomputed from per-recipe sufficient statistics; leave-one-recipe-out influence table; Wilson on pooled units is not primary; all intervals are conditional on annotators A and B",PROPOSED_PILOT,Units within a recipe are correlated; recipe is the unit of independence (one per split group).,reports/step19/deep_gold_pilot_design_v1_draft.md s7.3,N,,,,percentile cluster bootstrap B = 10000; BCa and cluster t per THR-19P-34,recipe,7 recipes: label indicative only,
THR-19P-21,DRAFT_PENDING_H4,19-pilot,Minimum units for a per-class statistic,">= 30 units from >= 5 recipes; below that report counts only (no interval, no claim)",PROPOSED_PILOT,"Prevents interval-free claims on rare classes (reserve/recombine, implicit events).",reports/step19/deep_gold_pilot_design_v1_draft.md s1 s7.3,N,,,,,class,"30 units, 5 recipes",
THR-19P-22,DRAFT_PENDING_H4,19-pilot,High-prevalence rule,dominant-class share >= 0.95 on a categorical field => kappa and alpha printed but not interpreted; AC1 and specific agreement carry the reading,PROPOSED_PILOT,Same prevalence value as THR-07A-03; kappa paradox (Feinstein and Cicchetti 1990).,reports/step19/deep_gold_pilot_design_v1_draft.md s7.2; registry THR-07A-03,N,,,,,field,,
THR-19P-23,DRAFT_PENDING_H4,19-pilot,Wave pooling,"P1 and P2 are different handbook versions: never pooled for a reliability statement; pooled-20 numbers are descriptive and labelled ""mixed handbook versions""",PROPOSED_PILOT,P2 follows an Addendum B derived from P1 adjudication.,reports/step19/deep_gold_pilot_design_v1_draft.md s5.6,N,,,,,wave,,
THR-19P-24,DRAFT_PENDING_H4,19-pilot,Adjudication completeness,"100% of disagreement rows carry adjudicated value, rationale class, handbook rule, version, decider and date; pre-adjudication labels preserved by hash; adjudicated files are new files",PROPOSED_PILOT,Plan: every adjudication has who / why / version (G19.M); applied to the pilot.,reports/step19/deep_gold_pilot_design_v1_draft.md s8,N,,,,,disagreement row,,
THR-19P-25,DRAFT_PENDING_H4,19-pilot,Schema-problem triage completeness,100% of logged items triaged (OPEN counts as not triaged),PROPOSED_PILOT,Card pass gate G19.P(3): every item triaged.,reports/step19/deep_gold_pilot_design_v1_draft.md s9; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (Pass gate G19.P(3)),N,,,,,log item,,
THR-19P-26,DRAFT_PENDING_H4,19-pilot,STOP-SCHEMA by blocking items logged by both annotators (retained as a supplementary trigger; the main rule is THR-19P-32),>= 3 distinct BLOCKING categories logged by both annotators => escalate to Step 16 (contract incoherent),PROPOSED_PILOT,"Operationalises ""schema incoherent"" (M.10) for a pilot; BLOCKING = cannot annotate faithfully without inventing or dropping content. Zero BLOCKING in 20 recipes bounds the per-recipe rate only at 13.9% (one-sided 95%). Retained unchanged as a supplementary trigger because it needs convergence and three coarse categories, so it under-detects (Review B 19-2); THR-19P-32 is the primary rule and no trigger is removed.",reports/step19/deep_gold_pilot_design_v1_draft.md s9 s10.2 App. B,N,,,,,log item category,,
THR-19P-27,DRAFT_PENDING_H4,19-pilot,GO-40 condition,"provenance PASS; no STOP; N * t_P2 (upper t-interval, per annotator) + adjudication projection <= per-annotator budget B_h declared by a human (no default)",PROPOSED_PILOT,Only N <= 40 is within the current mandate (MP AH6); B_h is a human capacity input that does not exist in the repo.,reports/step19/deep_gold_pilot_design_v1_draft.md s10.2; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (19-S sizing table),N,,,,95% t-interval on ln(time),annotator,13 recipes (P2),
THR-19P-28,DRAFT_PENDING_H4,19-pilot,Extension eligibility (information only),"provenance PASS both waves; P2 core-field point estimate >= 0.80 and lower 95% bound >= 0.667 (the most conservative of percentile, BCa and cluster-t, THR-19P-34); 0 open BLOCKING items; N * t_P2 fits B_h. Never an authorisation: N > 40 needs a separate H5/H8 decision; intervals are conditional on annotators A and B",PROPOSED_PILOT,The pilot cannot certify 0.80 with n = 20; the rule only says when it is reasonable to ask.,reports/step19/deep_gold_pilot_design_v1_draft.md s10.2 s10.4; Plan CHG-19-2,N,,,,min of percentile / BCa / cluster-t lower bounds (THR-19P-34),recipe,13 recipes,
THR-19P-29,DRAFT_PENDING_H4,19-pilot,Third reviewer / expert hours,"0-4 h in the pilot, only for cultural/regional adjudication cases; recorded role",PROPOSED_PILOT,Plan card: expert 0-4 h.,reports/step19/deep_gold_pilot_design_v1_draft.md s8; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (Human gate and hours),N,,,,,expert hour,,
THR-19P-30,DRAFT_PENDING_H4,19-pilot,Pilot recipe lock,"pilot recipes and their whole split groups tagged DESIGN_PILOT: dev and error analysis only; never sealed test, calibration or training; never reused as independent test items",PROPOSED_PILOT,Plan Step 19 leakage line; R-08.,reports/step19/deep_gold_pilot_design_v1_draft.md s4.7; docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 19 card (Metrics and leakage controls),N,,,,,split group,,
THR-19P-31,DRAFT_PENDING_H4,19-pilot,Handbook review gate on the per-pair-normalised rate (supersedes THR-19P-16 for gating),"HANDBOOK_REVISION_REQUIRED if max(tool rate, per-pair-normalised rate) > 0.20 for any disagreement category; per-pair rate = category rows / units of ONE annotator (half the tool's summed denominator where it sums both annotators; the mean of the two counts if they differ)",PROPOSED_PILOT,"The tool's denominators sum both annotators' units (F8(b)), up to 2x deflation, a known under-trigger. A stricter rule registered before any data exist is not a weakening: every case THR-19P-16 flags is still flagged. THR-19P-16 stays for comparability.",reports/step19/deep_gold_pilot_design_v1_draft.md s5.6 s7.2 s10.1 F8(b); tools/gold_pilot_agreement.py; Review B 19-3,N,,,,none in the gate (point rate); report cluster-bootstrap CI beside it,category rate,,"THR-19P-16 (gating role only; THR-19P-16 retained verbatim for comparability; own earlier draft, row never signed)"
THR-19P-32,DRAFT_PENDING_H4,19-pilot,"STOP-SCHEMA by adjudicated blocking items, any logger",">= 2 recipes each carrying an adjudicated schema-problem item with adjudication_class SCHEMA_GAP or HANDBOOK_GAP and severity BLOCKING on the same field family => STOP-SCHEMA for that family (escalate to Step 16), whoever logged it; a single-annotator BLOCKING item may be downgraded or dismissed only with a written rationale and every dismissed BLOCKING item is listed in the report",PROPOSED_PILOT,"Operationalises 'schema incoherent' without requiring both annotators to log the same three categories (THR-19P-26 needs convergence and a high bar, so a problem seen by one careful annotator never counts). Representability (Q-S) is the pilot's most decision-relevant output for 16c. THR-19P-26 is retained as a supplementary trigger.",reports/step19/deep_gold_pilot_design_v1_draft.md s8 s9 s10.2; Review B 19-2,N,,,,count rule; report the rule-of-three bound if zero (pilot design population only),recipe (>= 2 recipes per field family),2 recipes,
THR-19P-33,DRAFT_PENDING_H4,19-pilot,Per-recipe representability checklist and silent schema debt,after labelling each recipe and before commitment each annotator marks every hard-case class present (handbook hard-example list = SSOT 237.5 classes) FAITHFUL / WORKAROUND / IMPOSSIBLE plus one free OTHER row; IMPOSSIBLE = a BLOCKING log item; WORKAROUND counts are reported as silent schema debt next to BLOCKING; the sheet is private until both commitments and its hash is committed,PROPOSED_PILOT,"Makes under-detection of schema problems visible (Review B 19-2). Reporting rule; no pass threshold, no gate is weakened. The analyst-only known-gap list stays sealed so the checklist does not prime annotators.",reports/step19/deep_gold_pilot_design_v1_draft.md s6 s9; SSOT 237.5; Review B 19-2,N,,,,none (counts reported),recipe-annotator,,
THR-19P-34,DRAFT_PENDING_H4,19-pilot,Interval rule for decisions that read a bound,"for each statistic compute the percentile cluster bootstrap, the BCa cluster bootstrap and a cluster-level t interval on per-recipe statistics (df = n_recipes - 1); any rule that reads a lower bound uses the smallest lower limit, any rule that reads an upper bound the largest upper limit; all three are reported; 7-recipe intervals stay 'indicative only'; all intervals are conditional on annotators A and B",PROPOSED_PILOT,"Percentile intervals undercover with few clusters (stated for 7, equally true for 13); the pilot has exactly two fixed annotators who wrote the handbook, so no interval estimates annotator variance. Choosing the more conservative limit can only make a pass harder.","reports/step19/deep_gold_pilot_design_v1_draft.md s7.3 App. B; Review B 19-6, 19-7",N,,,,"min / max of percentile, BCa and cluster-t limits",recipe,7 recipes: indicative only; 13 recipes,
THR-19P-35,DRAFT_PENDING_H4,19-pilot,"Routing thresholds on F1 (span, event, edge, coreference, entity families); routing convention only","F1 >= 0.80 reportable as met (diagnostic); 0.667 <= F1 < 0.80 => handbook revision and re-measure on NEW recipes; F1 < 0.667 => redesign or demote field. F1 is not chance-corrected (for spans it equals positive specific agreement): the Krippendorff cut-offs are borrowed as a routing convention, an F1 of x is never read as an alpha of x and no F1 supports a reliability claim; unitizing alpha is an optional diagnostic and is not routed on",PROPOSED_PILOT,"Round-3 split of THR-19P-18 (Review B 19-1): the same numeric cut-offs are kept, so no gate is weakened, but they are labelled for what they are on this scale.",reports/step19/deep_gold_pilot_design_v1_draft.md s7.1 s7.2 s10.2; Review B 19-1; reports/master_plan/working_notes/research/r_recipe_semantics_gold.md Q7,N,,,,"recipe-cluster bootstrap (THR-19P-20, THR-19P-34)",recipe,see THR-19P-21,"THR-19P-18 (F1 part of the earlier combined 'alpha or F1' wording; own earlier draft, row never signed)"
```

## Appendix B. Arithmetic behind sections 6, 7.4, 10.3 and 11 (assumptions, not measurements)

Script and tables were produced with the Python standard library in a scratch directory (not in the repo); the formulas are all that is needed to reproduce them.

1. **Cluster design effect.** DEFF = 1 + (m - 1) rho for m units per recipe and intra-recipe correlation rho; n_eff = n_recipes x m / DEFF; 95% half-width for a proportion/F1 p = 0.85: 1.96 sqrt(p (1 - p) / n_eff). Results (m = 8 / 15 / 30; rho = 0.1 / 0.3):

| Recipes | m=8, rho .1 | m=8, rho .3 | m=15, rho .1 | m=15, rho .3 | m=30, rho .1 | m=30, rho .3 |
|---|---|---|---|---|---|---|
| 7 | 0.122 | 0.165 | 0.106 | 0.156 | 0.095 | 0.150 |
| 13 | 0.089 | 0.121 | 0.078 | 0.114 | 0.070 | 0.110 |
| 20 | 0.072 | 0.097 | 0.063 | 0.092 | 0.056 | 0.089 |

2. **Kappa.** Var(kappa) ~ p_o (1 - p_o) / (n (1 - p_e)^2). n_eff for a +/-0.10 half-width: p_o 0.90, p_e 0.5 -> 139; p_o 0.85, p_e 0.5 -> 196; p_o 0.95, p_e 0.8 -> 457 (this is the kappa paradox: high agreement, high prevalence, wide kappa). At n_eff = 200: +/-0.083 (0.90 / 0.5), +/-0.151 (0.95 / 0.8).
3. **Zero events.** One-sided 95% upper bound for a rate with 0 events in n recipes = 1 - 0.05^(1/n): n = 5: 45.1%; 7: 34.8%; 13: 20.6%; 20: 13.9%; 40: 7.2%.
4. **Timing.** Multiplicative 95% t-interval on a geometric mean = exp(t_(n-1) sigma_ln / sqrt(n)): n = 20 -> multiply-or-divide by 1.15 (sigma 0.3), 1.26 (0.5), 1.39 (0.7); n = 13 -> 1.20 / 1.35 / 1.53; n = 7 -> 1.32 / 1.59 / 1.91. sigma_ln is **assumed** (no timing data exist).
5. **Hours per annotator for the pilot** = 20 t/60 + adjudication (4 or 6) + 1 (setup) + 2 (design): t = 20 min -> 13.7-15.7 h; 30 -> 17.0-19.0; 45 -> 22.0-24.0; 60 -> 27.0-29.0; 75 -> 32.0-34.0; 90 -> 37.0-39.0; 93 -> 38.0-40.0; 105 -> 42.0-44.0; 120 -> 47.0-49.0.
6. **Annotation hours for N recipes** (per annotator, N x t/60): t = 30 -> 10 / 20 / 50 / 100 h for N = 20 / 40 / 100 / 200; t = 45 -> 15 / 30 / 75 / 150; t = 60 -> 20 / 40 / 100 / 200; t = 90 -> 30 / 60 / 150 / 300. Adjudication and session review are extra.

## Appendix C. Templates (headers only, no data)

`pilot_timing_v1.csv`:

```csv
session_id,annotator_letter,packet_id,wave,phase,start_utc,end_utc,wall_minutes,break_minutes,active_minutes_self,validate_runs,replay_runs,handbook_lookups,difficulty_1_5,status_after,schema_problem_ids,note
```

`pilot_schema_problem_log.csv` (rendered into `pilot_schema_problem_log.md`):

```csv
sp_id,wave,packet_id,logged_by,unit,category,severity,handbook_rule_ref,what_the_annotator_did,proposed_fix,owner_step,convergent,field_family,adjudication_class,triage_status,triage_note,date
```

`pilot_representability_v1.csv` (one row per recipe per annotator per hard-case class present, plus an OTHER row; rating in {FAITHFUL, WORKAROUND, IMPOSSIBLE}; private until both commitments):

```csv
packet_id,annotator_letter,wave,hardcase_class,rating,sp_id_if_logged,note
```

`question_log_<letter>_<wave>.csv` (one per annotator, write-only during the wave):

```csv
entry_id,packet_id,utc_time,question,minutes_spent,answered_after_commitments
```

`adjudication` sheet (template columns plus the tool's, in this order):

```csv
recipe_id,category,where,field,kush,parv,adjudicated,rationale_class,rationale,handbook_rule,handbook_version_at_annotation,decided_by,decided_on
```

`commitments_<letter>_<wave>.json` in the tracked folder `registry/recipe_semantics/deep_gold_pilot_v1/` (shape only, synthetic placeholders; provenance values are recorded at commitment time, no recipe text): `{"annotator_letter": "A", "wave": "P1", "handbook_version": "<id>", "created_utc": "<ts>", "question_log_sha256": "<64 hex>", "representability_sha256": "<64 hex>", "files": [{"packet_id": "DGP-A-0001", "sha256": "<64 hex>", "size_bytes": 0, "mtime_utc": "<ts>", "committed_utc": "<ts>", "snapshots": [{"sha256": "<64 hex>", "utc": "<ts>", "event": "FIRST_VALIDATE"}, {"sha256": "<64 hex>", "utc": "<ts>", "event": "DONE"}]}]}`. `sealed_key_<wave>.sha256` holds one 64-hex line.

## Appendix D. Provenance and non-actions

- Created: this file and `reports/step19/README.md` only; revised in place on 2026-10-26 after the round-3 reviews (the original drafts were not committed). The only commands run against the repo for the revision were read-only (`git check-ignore -v` on candidate paths: `annotation/gold/deep_gold_pilot_v1/{commitments.json,manifest.csv,A/x.json}` are ignored by `.gitignore:9`; `registry/recipe_semantics/deep_gold_pilot_v1/{manifest.csv,commitments_A_P1.json,sealed_key_P1.sha256}` are not ignored). `.gitignore` was not edited.
- Logging (review A #36): CLAUDE.md asks that each step is logged with `tools/log_step.py`; this lane did not log (a WORKLOG entry would modify an existing file). The integrating session should log it with `--files` the two Step-19 paths and `--verify` 'git diff --stat on tracked files empty; Appendix A row check (35 rows, 16 fields, unique ids)'.
- Not touched: every existing file, ledger, tool, packet, annotation, registry and report (`registry/preregistered_thresholds_v1.csv` was read for format only), the SSOT, the plan, `DECISIONS.md`, `WORKLOG.md`.
- No git write command, no pipeline, no ingredient/instruction text opened, no title read from the recipe base, no model run (committed manifests that carry titles or slugs of already-excluded recipes were incidentally visible; see the header). Aggregate counts of `recipe_base_v1.parquet`, `recipe_identity_*.parquet` and ledger metadata were read read-only with `pandas`/`pyarrow` from an existing environment; Appendix B arithmetic used the standard library.
