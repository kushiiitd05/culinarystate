# S177 SCIFIX-ROUTER: router findings (FINAL-SCI #6, #7), public mode (FINAL-GOV #2) and the SR identity adapter

Status: **AI_DRAFTED / PROPOSED / NON_CITABLE.** This is not a human gate, signature, approval or nonce.
- Worktree `max/s176-orchestration` @ `a0a5b49+uncommitted`, host manjot-server, 2026-11-09.
- Scientific 23b stays BLOCKED. `applicability.py` is untouched. Labels and `assert_citable` are unchanged.
- No ledger was written. The protected-ledger baseline check passed before and after both final census runs.
- No git write, nothing installed.
- `composition/` was only read, through `load_registry` and `normalise`.

## 1. Result

1. **#7, prior-process lot context (done).**
   - A SINGLE_MEMBER lot whose ancestry holds a heat, leach (SEPARATION family, soak-like processes) or heat-preservation event gets reason `PRIOR_PROCESS_CONTEXT`.
   - DIRECT is withheld and the EVD rows stay visible as `evidence_not_applied`.
   - Ancestry comes from the replay graph: `events[].produces` plus `parent_entity_ids`.
   - A route is never upgraded; the never-upgrade property test was extended.
2. **#6, full ABSENT rule (done).**
   - ABSENT needs three things: a HIGH rank-1 band; every rank 1-3 candidate within the identity margin, of any band, with a known SR value below the floor; and an ING category that matches the SR food group under an explicit, strict, AI_DRAFTED crosswalk.
   - Otherwise UNKNOWN.
   - The content table now holds LOW rows.
   - The reviewers' false-ABSENT cases (herb, coleslaw, lemongrass) are UNKNOWN, and custard is never ABSENT.
3. **Extra scope, SR identity adapter (done).**
   - `mechanism/sr_identity.py` takes ING → SR identity from the Mac's `registry/ing_sr_defaults_v1.csv`.
   - Band mapping: DIRECT, UK_US and DEFAULT_FORM → HIGH; APPROX → MEDIUM; unmappable kinds → no identity.
   - The legacy match file is demoted to alternates and a fallback capped at MEDIUM.
   - The presence screen and the content table point at the adapter. The router no longer imports `lotstate/`.
   - **ABSENT ING for vitamin C (SVAR-000009, floor 1.0, margin 0.15, 2,048 ACTIVE ING): 185 (S175 interim, legacy identity) → 86 (full S177 rule, legacy identity) → 52 (adapter).**
   - PRESENT is 318 and UNKNOWN is 1,678. The consolidation review simulated 52 / 317 / 1,679: ABSENT is identical and one ING differs on the other two.
4. **GOV #2, public mode (done).**
   - `CS_DEMO_PUBLIC` defaults ON for a hosted build or a non-loopback bind, and OFF for local Mac use.
   - `--public` and `--local` override it. An unreadable value fails closed to ON.
   - Every BBC-derived KGE edge is dropped before any candidate is built, and carbon is emptied.
   - Every response carries `demo_mode`, `/api/health` reports it, and the page shows "Public mode" or "Local mode".
5. **Census, full non-BBC (seed 20261104).**
   - DIRECT 34,537 → **40,308** of 35,256,601 items; ungated is 267,933.
   - NOT_APPLICABLE 6,055,991 → **813,547**.
   - Section 6 has the comparison.
6. **Tests.**
   - 61 new (25 + 17 + 19).
   - 396 passed on the router/app/decision set, with a test-only `lxml` stand-in on `PYTHONPATH` in the scratchpad. The new public-mode tests carry their own in-test stand-in.
   - The final re-run of the five directly affected files gave 109 passed.

**Honest cost of #6.**
- ABSENT is now much harder to assert, so the S176 "baked egg has no vitamin C" abstention no longer fires.
- 1,452 of the 2,110 ING rows have no `category`: egg, salt, honey, water, cornflour, double cream, yeast and so on.
- Under the finding's rule an unconfirmed category means UNKNOWN. See section 4 and open question 1.

## 2. Files

| File | Change |
|---|---|
| `src/culinarystate/mechanism/evidence_gates.py` | Version `evidence-gates-0.2.0-draft`. Adds `CATEGORY_CROSSWALK` and `category_matches`. Adds `TargetPresenceScreen.member_verdict` (state plus blocker), `plausible_all` and `category_ok`. Adds `prior_kind`, `LotMembers.prior` and `lot_members(graph, hierarchy)`. New reason `PRIOR_PROCESS_CONTEXT`. Table reader and writer carry categories and identity columns. `review_rows` is new. All `lotstate` imports removed. |
| `src/culinarystate/mechanism/sr_identity.py` | **New.** The adapter; its module docstring has the kind → band table. |
| `mechanism/router_demo.py`, `router_census.py` | `DEMO_VERSION` and `CENSUS_VERSION` 0.3.0. Per-item `prior_process`, `member_presence`, `member_blocker`. New census counters `prior_process_withheld`, `member_presence`, `member_blocker`, `member_absent_items`, `category_blocked_items`. |
| `src/culinarystate/decision/public_mode.py` | **New.** Switch, BBC test, edge filter, `describe`. |
| `decision/{pipeline,feasibility,demo_context}.py` | `load_lexicon(public=)`, `load_requirements(public=)`, `DemoContext.load(public, host)`, `demo_mode` in every response. An empty substitution answer in public mode adds a note. |
| `app/server.py`, `app/static/index.html` | `--public` / `--local`, mode in `/api/health`, mode banner, reason text for `PRIOR_PROCESS_CONTEXT`. |
| `tools/build_target_content_table.py` | `--identity defaults\|legacy`, LOW rows, category columns, `identity_source`, `registry_kind`. |
| `tools/router_demo_census.py` | `--absent-review-csv`, `--category-blocked-csv`, `--review-from REPORT`. |
| `registry/ing_sr_target_content_draft_v1.csv` | Rebuilt from the adapter. sha256 `24c7b4d047c9a6d95a0024315a732d741e04ff2ac203226c7ae98ea7eb37f7db`. 13 columns, 1,906 rows, 876 ING, rank 1-3 of any band. |
| `tests/unit/test_s177_router_gates.py`, `test_s177_router_public_mode.py`, `test_s177_sr_identity_adapter.py` | **New** (25 + 17 + 19). |
| `reports/s177/absent_top50_for_human_review.csv`, `reports/s177/absent_blocked_by_category_top50_for_human_review.csv` | **New.** Counts and registry names only. `human_verdict` is empty. |
| `reports/step23/router_demo_census_vitc_nonBBC_{1000,full}_S177.json` | **New.** Counts only. |

Unchanged: `registry/target_presence_floor_v1_PROPOSED.csv` and `tools/router_gate_sensitivity.py`. The sensitivity tool still runs; its numbers were not re-run (section 9).

## 3. FINAL-SCI #7: prior-process lot context

- **Rule.**
  - In `evaluate`, a SINGLE_MEMBER lot with a prior process gets `PRIOR_PROCESS_CONTEXT`, `final_precheck = NONE`, and is withheld.
  - Presence ABSENT still wins (NOT_APPLICABLE). MERGED keeps its own reason first.
  - The reason appears only when it actually downgrades, i.e. an EVD row existed.
  - The lot-context value stays SINGLE_MEMBER, so the S176 cross-tab keys are unchanged. The fact is in `item["prior_process"]` (`HEAT`, `LEACH` or both).
- **Classes** (constants in `evidence_gates.py`; a human may narrow them).
  - HEAT: PROC families WET_HEAT, DRY_HEAT, FAT_HEAT and HEAT_GENERAL, plus sterilise, can, pasteurise and dry.
  - LEACH: the whole SEPARATION family (drain, strain, rinse, squeeze, discard, pat-dry, sift and so on) plus soak, marinate, brine and pickle.
  - This follows the finding's "heat or leach (SEPARATION/SOAK)" wording literally and is on the safe side, so "pat dry then fry" is withheld too.
  - A cut or mix is not prior process. An event with no resolved process is not assumed to be one.
- **How it is read.**
  - `lot_members(graph, hierarchy)` marks every entity listed in the `produces` of a HEAT or LEACH event.
  - Each descendant inherits the mark through `parent_entity_ids`.
  - A graph without events has no prior process.
- **Test change flagged.**
  - The finding names `test_s176_evidence_gates.py:227` as encoding the bug.
  - That test is `test_lot_members_known_merged_and_unknown_roots`. It tests membership, not DIRECT, and stays valid.
  - The new behaviour is tested in `test_s177_router_gates.py` instead: boil-then-fry, soak or drain then boil, cut-then-boil stays DIRECT, switch off, precedence, never-upgrade property, census counters.
- **Real-ledger smoke**, public and local mode alike:
  - Boil, drain, fry the potatoes gives Boil DIRECT, Drain UNKNOWN, **Fry UNKNOWN (`PRIOR_PROCESS_CONTEXT`)**.
  - Cut, fry gives Fry DIRECT.

## 4. FINAL-SCI #6: full ABSENT rule, crosswalk, identity adapter

**Rule** (`TargetPresenceScreen.member_verdict`; blockers are listed in the order tested):

| step | condition | else (UNKNOWN, blocker) |
|---|---|---|
| 0 | a usable rank-1 identity exists | `NO_USABLE_IDENTITY` |
| PRESENT | every HIGH / MEDIUM plausible candidate has a known value ≥ floor | (continue) |
| 1 | rank-1 band is HIGH | `RANK1_NOT_HIGH` |
| 2 | every rank 1-3 candidate within the margin, any band, has a **known** value | `SR_VALUE_MISSING` |
| 3 | all those values are below the floor | `IDENTITIES_DISAGREE` |
| 4 | the ING category matches the SR food group of the rank-1 candidate | `CATEGORY_MISMATCH` or `CATEGORY_EMPTY` |

- The category check is last, so a `CATEGORY_*` blocker means "would be ABSENT if its category were confirmed".
- A lot is ABSENT only if every member is ABSENT and none has unknown identity. This is unchanged.

**Crosswalk** (`CATEGORY_CROSSWALK`, status `AI_DRAFTED_UNSIGNED`). It is strict on purpose: a pair that is not listed means "not confirmed".

| ING category | SR food groups |
|---|---|
| BEVERAGE | Beverages |
| CEREAL | Cereal Grains and Pasta, Breakfast Cereals, Baked Products |
| CONDIMENT | Soups, Sauces, and Gravies; Spices and Herbs |
| DAIRY, EGG | Dairy and Egg Products |
| FAT_OIL | Fats and Oils |
| FRUIT | Fruits and Fruit Juices |
| HERB_SPICE | Spices and Herbs |
| LEGUME | Legumes and Legume Products |
| MEAT | Beef, Pork, Poultry, Lamb / Veal / Game, Sausages and Luncheon Meats |
| NUT_SEED | Nut and Seed Products |
| SEAFOOD | Finfish and Shellfish Products |
| SWEETENER | Sweets |
| VEGETABLE | Vegetables and Vegetable Products |

- A test checks that every ING category in the registry has a row.
- Fresh herbs that SR files under Vegetables, or juices filed under Fruits, are therefore UNKNOWN, not ABSENT.

**Content table.**
- LOW-band rank 2-3 candidates are in the table, for ING with a usable rank 1, so the margin test sees every alternative.
- `ing_category`, `sr_category`, `identity_source` and `registry_kind` are carried.
- `--check` passes.
- Values are public-domain SR Legacy; identities are AI-proposed.

**Identity adapter** (consolidation review §5.3):
- DIRECT or UK_US → `(fdc, HIGH, 1)` alone.
- DEFAULT_FORM → `(fdc, HIGH, 1)` plus the legacy file's rank 1-3 foods as LOW alternates at score 1. ABSENT therefore needs every form known and below the floor.
- APPROX → `(fdc, MEDIUM, 1)`. PRESENT only.
- NO_SR_EQUIVALENT, NOT_A_FOOD, AMBIGUOUS → no identity and no fallback.
- A term not in the registry → the legacy rank 1-3 with HIGH capped to MEDIUM. PRESENT only.
- Lookup is by canonical name, then by ACTIVE English aliases that all agree. No alias hits anything today.
- Mapping over the 2,048 ACTIVE ING: DIRECT 149, UK_US 58, DEFAULT_FORM 62, APPROX 109, legacy fallback 498. 1,172 have no identity at all.

**ABSENT count change (vitamin C):**

| identity / rule | ABSENT ING |
|---|---|
| S175 interim (HIGH rank 1 + usable identities below the floor), legacy file | 185 (of the 793 ING with a usable legacy rank 1) |
| S177 full rule, legacy file (`--identity legacy`, reproduced by a test) | 86. Of the 99 lost: 82 have an empty ING category and 17 a mismatch; none were lost to LOW alternates. |
| **S177 full rule, adapter (shipped)** | **52**, each on a DIRECT, UK_US or DEFAULT_FORM identity |

- Stay ABSENT: butter, olive oil, rice, pasta, plain flour and the like.
- Leave ABSENT: milk and sugar (an alternate form disagrees or lacks a value), cream, vinegar and bread (the registry calls the name AMBIGUOUS), sherry (APPROX).

**The empty-category problem (needs a human decision).**
- Egg, salt, honey, water, cornflour, double cream and yeast have no `category`, so they are UNKNOWN under the finding's rule.
- On the real ledgers "How much vitamin C does baked egg keep?" is now answered "Answered from data" with the USDA retention-group row EVD-000113 (retention 0.80).
- Only the recipe path flags it, through the `TARGET_PRESENCE_UNKNOWN` reason.
- I did not guess categories.
- `absent_blocked_by_category_top50_for_human_review.csv` lists the top 50 ING that would be ABSENT if their category were confirmed. A human who confirms them, or adds categories to the ING ledger, restores the abstentions.
- In the full census 63 ING / 5,544,505 items are in that state.

**Human check of the top 50 ABSENT ING** (FINAL-SCI asks for it before the demo):
- `reports/s177/absent_top50_for_human_review.csv` has 50 rows: the top 50 by item count of the 52 ING that were ABSENT in the full census.
- Columns: ING id and registry name, ING category, registry kind, rank-1 SR food and group, band, rank-1 SR value and the maximum over the plausible identities, floor, items.
- `human_verdict` and `human_note` are empty.

Top of the ABSENT list:

| # | ING | name | category | registry kind | SR food group | items |
|---|---|---|---|---|---|---|
| 1 | ING-000130 | flour | CEREAL | DEFAULT_FORM | Cereal Grains and Pasta | 1,333,929 |
| 2 | ING-000001 | butter | DAIRY | DEFAULT_FORM | Dairy and Egg Products | 999,723 |
| 3 | ING-000003 | olive oil | FAT_OIL | DIRECT | Fats and Oils | 333,372 |
| 4 | ING-000112 | rice | CEREAL | DEFAULT_FORM | Cereal Grains and Pasta | 185,610 |
| 5 | ING-000243 | cream cheese | DAIRY | DIRECT | Dairy and Egg Products | 169,897 |
| 6 | ING-000118 | breadcrumbs | CEREAL | DEFAULT_FORM | Baked Products | 129,695 |
| 7 | ING-000244 | pasta | CEREAL | DEFAULT_FORM | Cereal Grains and Pasta | 123,783 |
| 8 | ING-000120 | brown sugar | SWEETENER | DIRECT | Sweets | 112,917 |
| 9 | ING-000182 | black pepper | HERB_SPICE | DIRECT | Spices and Herbs | 96,602 |
| 10 | ING-000078 | almond | NUT_SEED | DIRECT | Nut and Seed Products | 87,949 |
| 11 | ING-000018 | icing sugar | SWEETENER | UK_US | Sweets | 84,297 |
| 12 | ING-000098 | yogurt | DAIRY | DEFAULT_FORM | Dairy and Egg Products | 76,815 |

Top of the category-blocked list:

| # | ING | name | category | registry kind | SR food group | items |
|---|---|---|---|---|---|---|
| 1 | ING-000109 | water | (empty) | DIRECT | Beverages | 1,427,479 |
| 2 | ING-000004 | egg | (empty) | DEFAULT_FORM | Dairy and Egg Products | 1,212,776 |
| 3 | ING-000044 | salt | (empty) | DIRECT | Spices and Herbs | 982,601 |
| 4 | ING-000058 | cornflour | (empty) | UK_US | Cereal Grains and Pasta | 177,754 |
| 5 | ING-000051 | egg yolk | (empty) | DIRECT | Dairy and Egg Products | 161,591 |
| 6 | ING-000086 | egg white | (empty) | DIRECT | Dairy and Egg Products | 155,781 |
| 7 | ING-000032 | honey | (empty) | DIRECT | Sweets | 135,304 |
| 8 | ING-000035 | chicken stock | (empty) | DEFAULT_FORM | Soups, Sauces, and Gravies | 132,697 |
| 9 | ING-000053 | soy sauce | (empty) | DEFAULT_FORM | Legumes and Legume Products | 126,286 |
| 10 | ING-000031 | parmesan | (empty) | DIRECT | Dairy and Egg Products | 118,308 |
| 11 | ING-000135 | paprika | (empty) | DIRECT | Spices and Herbs | 103,403 |
| 12 | ING-000077 | mayonnaise | CONDIMENT | DIRECT | Fats and Oils | 75,654 |

Mayonnaise, with a CONDIMENT category and the SR group "Fats and Oils", is a genuine crosswalk mismatch, not an empty category. Chocolate (NUT_SEED vs Sweets) is another.

## 5. FINAL-GOV #2: public mode

- **Filter.**
  - An edge is BBC-derived if its `corpus_ids` or `support.by_source_family` include `BBCGF-A1`.
  - Extension of the finding: the 39 `PROC_TYPICAL_DURATION` edges carry neither field, so an edge with neither field is also BBC-derived when its `provenance.source_ids` include the BBC source record SRC-000002.
  - In public mode `load_lexicon` and `load_requirements` drop every such ACTIVE edge, and every `ING_CARBON_FOOTPRINT` edge, before `alternatives`, `followed_by`, `processed_by`, `durations`, tools and `carbon` are built.
  - This is wider than the finding's wording. It also covers process candidates, durations and tool requirements, which are the same kind of BBC co-occurrence aggregate.
  - Local mode is unchanged.
- **Switch.**
  - Order: explicit argument or `--public` / `--local`, then env `CS_DEMO_PUBLIC` (1 / true / yes / on / public = ON; 0 / false / no / off / local = OFF), then automatic.
  - Automatic is ON when `CS_DEMO_HOSTED` or a platform marker (`PORT`, `SPACE_ID`, `K_SERVICE` and so on) is set, or when the server binds a non-loopback address. Otherwise OFF.
  - An unreadable value fails closed to ON.
  - **If a local demo is tunnelled to the public, set `CS_DEMO_PUBLIC=1`.**
- **UI.**
  - The page fetches `/api/health` and shows "Public mode. Patterns taken from some recipe sites, and carbon figures, are left out of this build."
  - Or it shows "Local mode. ... for the researcher's own machine only. Do not share its output." If the call fails it shows "Mode unknown".
  - Every `/api/ask` response carries `demo_mode`.
  - An empty substitution answer in public mode adds a sentence saying why a pattern may be missing.
- **Effect on the real KGE ledger** (latest version of each id, ACTIVE):

| Predicate | Before | After public filter |
|---|---|---|
| `ING_ALTERNATIVE_TO` | 220 | 4 (216 dropped) |
| `PROC_FOLLOWED_BY` | 63 | 4 (59 dropped) |
| `ING_PROCESSED_BY` | 2,132 | 367 |
| `PROC_TYPICAL_DURATION` | 39 | 0 |
| `PROC_USES_TOOL` | 543 | 13 |
| `ING_CARBON_FOOTPRINT` | 134 | 0 |

  - Through the demo context: alternatives 155 → 4 ING, followed-by 44 → 4, carbon 134 → 0, durations 39 → 0, processed-by 619 → 219.
  - A test asserts that no BBC-derived edge and no carbon edge survives.
  - The "Swap ricotta" example still works (Wikibooks-only edge).
  - "Instead of butter" and "instead of buttermilk" now abstain in public mode. Buttermilk answered "natural yogurt" in local mode.
- **Count correction for the GOV finding.**
  - The 412 of 420 (`ING_ALTERNATIVE_TO`) and 150 of 158 (`PROC_FOLLOWED_BY`) figures count every ACTIVE row **including superseded versions**.
  - The demo reads the latest version of each id: **216 of 220** and **59 of 63** are BBC-supported. That leaves 4 non-BBC edges (2 pairs) of each, not 8.
  - `S176_L-ROUTER_report.md` F4 still says "414 of the 420 … 6". The correction belongs there; it is not my file.
- **Real-ledger smoke, both modes** (`DemoContext.load`, 7 questions each, 230 s): public mode shows no carbon text and substitution answers only from the 4 remaining edges. Local mode keeps all.

## 6. Router census (non-BBC, seed 20261104, target SVAR-000009, floor 1.0, margin 0.15)

- **Run setup.**
  - Both runs: `--gates on`, FOODCOM + GUTENBERG_SEGMENT + WIKIBOOKS + TASTESET, `nice -n 10`.
  - Protected-ledger baseline `PASS_BEFORE_AND_AFTER`; 0 exceptions.
  - They ran together (24 + 8 = 32 workers).
- **"Ungated" side.** It is the S171 behaviour of the same pass, so S176 and S177 are measured on identical items.
- **1,000-sample run.** `code_unchanged_during_run` is true.
- **Full run.** `code_unchanged_during_run` is **false**.
  - Cause: the git HEAD moved and other lanes changed `src/` files during the 2 h 17 min.
  - All 19 census-path code-file hashes (`evidence_gates.py`, `router_demo.py`, `router_census.py`, `applicability.py`, `tools/router_demo_census.py` and so on) are identical before and after.
  - The report's content-table and identity-registry sha256 match the current files.

### 6.1 Fixed 1,000-recipe sample (997 texts with steps, 57,511 items)

| | S176 | S177 | change |
|---|---|---|---|
| DIRECT items | 73 | 73 | +0 |
| UNKNOWN items | 47,838 | 56,093 | +8,255 |
| NOT_APPLICABLE items | 9,600 | 1,345 | −8,255 |
| recipes with any DIRECT | 55 | 67 | +12 |
| reason TARGET_ABSENT | 9,600 | 1,345 | −8,255 |
| reason TARGET_PRESENCE_UNKNOWN | 12,970 | 19,337 | +6,367 |
| reason MERGED_LOT_CONTEXT | 318 | 346 | +28 |
| reason PRIOR_PROCESS_CONTEXT (new) | 0 | 30 | +30 |
| reason EVIDENCE_PREEMPTS (= DIRECT) | 73 | 73 | +0 |

Fate of the 450 ungated DIRECT items:

| presence \| lot context \| final route | S176 | S177 |
|---|---|---|
| ABSENT \| MERGED \| NOT_APPLICABLE | 28 | 0 |
| ABSENT \| SINGLE_MEMBER \| NOT_APPLICABLE | 31 | 1 |
| PRESENT \| MERGED \| UNKNOWN | 227 | 245 |
| PRESENT \| SINGLE_MEMBER \| DIRECT | 40 | 39 |
| PRESENT \| SINGLE_MEMBER \| UNKNOWN (prior process) | 0 | 21 |
| UNKNOWN \| MERGED \| UNKNOWN | 91 | 101 |
| UNKNOWN \| SINGLE_MEMBER \| DIRECT | 33 | 34 |
| UNKNOWN \| SINGLE_MEMBER \| UNKNOWN (prior process) | 0 | 9 |

Prior-process withheld items by kind: HEAT 22, HEAT+LEACH 6, LEACH 2.

### 6.2 Full census

- **Scale:** 600,848 recipes, 599,968 texts with steps, 9,208,811 events, 35,256,601 items (34,243,815 linked, 1,012,786 unlinked).
- **Wall time:** 2026-11-09T08:22:21Z to 10:40:10Z, 24 workers.

| | S176 | S177 | change |
|---|---|---|---|
| DIRECT items | 34,537 | 40,308 | +5,771 |
| UNKNOWN items | 29,166,073 | 34,402,746 | +5,236,673 |
| NOT_APPLICABLE items | 6,055,991 | 813,547 | −5,242,444 |
| recipes with any DIRECT | 28,849 | 37,773 | +8,924 |
| reason TARGET_ABSENT | 6,055,991 | 813,547 | −5,242,444 |
| reason TARGET_PRESENCE_UNKNOWN | 7,315,681 | 11,303,330 | +3,987,649 |
| reason MERGED_LOT_CONTEXT | 197,068 | 214,098 | +17,030 |
| reason PRIOR_PROCESS_CONTEXT (new) | 0 | 11,861 | +11,861 |
| reason EVIDENCE_PREEMPTS (= DIRECT) | 34,537 | 40,308 | +5,771 |

Fate of the 267,933 ungated DIRECT items:

| presence \| lot context \| final route | S176 | S177 |
|---|---|---|
| ABSENT \| MERGED \| NOT_APPLICABLE | 17,036 | 6 |
| ABSENT \| SINGLE_MEMBER \| NOT_APPLICABLE | 19,292 | 1,660 |
| PRESENT \| MERGED \| UNKNOWN | 148,585 | 159,886 |
| PRESENT \| SINGLE_MEMBER \| DIRECT | 17,608 | 15,481 |
| PRESENT \| SINGLE_MEMBER \| UNKNOWN (prior process) | 0 | 6,397 |
| UNKNOWN \| MERGED \| UNKNOWN | 48,483 | 54,212 |
| UNKNOWN \| SINGLE_MEMBER \| DIRECT | 16,929 | 24,827 |
| UNKNOWN \| SINGLE_MEMBER \| UNKNOWN (prior process) | 0 | 5,464 |

Other full-census counts:
- Member states of the items' own ING: ABSENT 4,191,765, PRESENT 9,873,375, UNKNOWN 20,178,675, no ING (unlinked) 1,012,786.
- Why an UNKNOWN member is not ABSENT:

| Blocker | Items |
|---|---|
| `NO_USABLE_IDENTITY` | 6,315,048 |
| `RANK1_NOT_HIGH` | 5,778,775 |
| `CATEGORY_EMPTY` | 5,220,426 |
| `SR_VALUE_MISSING` | 1,716,672 |
| `IDENTITIES_DISAGREE` | 823,675 |
| `CATEGORY_MISMATCH` | 324,079 |

- Prior-process withheld by kind: HEAT 8,012, HEAT+LEACH 2,188, LEACH 1,661.
- All 52 ABSENT ING occur in the corpus (4,191,765 items). 63 ING (5,544,505 items) are category-blocked.
- Surviving DIRECT by process (top 8): bake 6,904 (PROC-000001), boil 5,836 (000019), 000016 5,135, mash 4,297 (000071), 000031 4,016, 000032 3,665, 000003 2,706, fry 2,555 (000009).
- Evidence coverage is unchanged: 115 EVD pairs for the target, 102 seen, 25 of 25 EVD ingredients seen.

**Reading the numbers.**
1. The ungated side is unchanged, so every difference is the gates.
2. **#7 withholds more DIRECT** (11,861 items, 4.4 % of the ungated DIRECT), and the merged-lot rule withholds 214,098 (79.9 %).
3. **#6 un-screens ABSENT.**
   - ABSENT shrank from 36,328 ungated-DIRECT items (13.6 %) to 1,666 (0.6 %).
   - Most of the rest now route as UNKNOWN-presence.
   - That is why net DIRECT rose (+5,771) and NOT_APPLICABLE fell by 87 %.
4. **Survivors are weaker.**
   - 24,827 of 40,308 surviving DIRECT items (61.6 %) have presence UNKNOWN. In S176 it was 16,929 of 34,537 (49.0 %).
   - Each carries `TARGET_PRESENCE_UNKNOWN`.
   - This is the price of the strict category rule and of the many ING whose category is empty.
5. If the egg-class categories were confirmed by a human, much of this would move back to NOT_APPLICABLE. The category-blocked list sizes that.

## 7. Tests

| File | Tests | Covers |
|---|---|---|
| `test_s177_router_gates.py` | 25 | Prior-process classes; ancestry from `produces`; boil-then-fry, soak / drain-then-boil, cut-then-boil; switch; precedence; never-upgrade property (30 random combinations); census counters. ABSENT needs HIGH + known LOW alternates + category; blockers; crosswalk. Shipped-table invariants (every ABSENT member satisfies all three conditions; the reviewers' three ids are UNKNOWN). Build `--check`; table round trip; review lists and `--review-from`. |
| `test_s177_router_public_mode.py` | 17 | Switch precedence and fail-closed. BBC test incl. zero count and source-record fallback. Edge filter. The repo KGE ledger has nothing BBC-derived left. `load_lexicon` / `load_requirements` / `extra_candidates` local vs public. The context answers or abstains. `demo_mode` on every response. `/api/health`. `server.main` flags. The page. |
| `test_s177_sr_identity_adapter.py` | 19 | Kind → band. Unmappable → none. DEFAULT_FORM alternates. APPROX and fallback never ABSENT. Aliases. Categories. Table columns. No `lotstate` import. The 52 / 318 / 1,678 snapshot. Every ABSENT on a curated identity. Herb, lemongrass, coleslaw, custard never ABSENT. Legacy rebuild gives 86. Direct-SR screen equals the shipped table. |

**Existing tests changed.** Each one encodes a reviewed bug or the consolidation change; none was loosened.
- In `test_s176_evidence_gates.py`:
  - The `_screen` helper now supplies a matching category, because ABSENT needs one.
  - `test_candidates_are_read_from_the_match_registry` keeps the LOW rank-3 row (#6: LOW alternatives were dropped before the margin test).
  - The table test checks the rank-1 band only.
  - The census-version assertion follows `RC.CENSUS_VERSION`; this is a mechanical version bump, not a reviewed bug.
  - `test_shipped_table_matches_sr_legacy_when_present` compares to the adapter identity.
- **Outside my list (flagged):** `test_s176_demo_honesty.py`'s `_gates` helper got the same matching-category pair. Two TARGET_ABSENT tests failed without it.

**Counts.**
- 396 passed on the router / app / decision / generation / contract set, with a test-only `lxml` stand-in in the scratchpad on `PYTHONPATH`.
- Without the stand-in, the pipeline-dependent modules cannot be collected, as before.
- `hypothesis` is still missing, so `test_step23a_appdec_properties` was not run, as before.

## 8. Runs (rows for `registry/compute_runs_v1.csv`; the orchestrator appends them)

Header: `run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes`

```csv
RUN-S177-ROUTER-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,none (SR Legacy + registries),1,"python tools/build_target_content_table.py --force (legacy match file only, LOW rows and category columns added)",<scratchpad>/ing_sr_target_content_S177_legacyidentity.csv,12d384339343b9cdf901f9ee783ee4bacbe11e2f5b5a6d6e8fce03a1c3b2d651,,,DISCARDED_SUPERSEDED,"first S177 table (2232 rows; 86 ABSENT ING); superseded by the adapter table; start and end not logged (before 2026-11-09T07:59Z); reproducible with --identity legacy"
RUN-S177-ROUTER-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,16,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 1000 --workers 16 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --gates on --out reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json",<scratchpad>/pre_adapter_1000_S177.json,f2c19a610b136a86ea9d6faf2ee53af1d7c2c05f915876467eb0ee6a02eda89f,2026-11-09T08:04:22Z,2026-11-09T08:08:57Z,DISCARDED_SUPERSEDED,"before the identity adapter (DIRECT 70, NOT_APPLICABLE 1907); an earlier start at 2026-11-09T07:59:15Z was stopped because code changed during the run and left no output; the finished output was moved out of reports/"
RUN-S177-ROUTER-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,none (demo smoke on real ledgers),1,"PYTHONPATH=src:<scratchpad>/lxml_stub nice -n 10 python <scratchpad>/s177_smoke.py (DemoContext.load public and local, 7 questions each)",<scratchpad>/s177_smoke_out.txt,,2026-11-09T08:07:51Z,2026-11-09T08:10:43Z,DONE_SUPERSEDED,"pre-adapter; first look at public vs local; lxml stand-in is a test-only shim on PYTHONPATH, nothing installed"
RUN-S177-ROUTER-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,24,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 700000 --workers 24 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --gates on --out reports/step23/router_demo_census_vitc_nonBBC_full_S177.json",,,2026-11-09T08:11:12Z,2026-11-09T08:15:00Z,STOPPED,"stopped by me when the coordinator added the identity adapter (code would have changed during the run); no output; end time approximate"
RUN-S177-ROUTER-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,none (SR Legacy + registries),1,"python tools/build_target_content_table.py --force (identity defaults)",registry/ing_sr_target_content_draft_v1.csv,24c7b4d047c9a6d95a0024315a732d741e04ff2ac203226c7ae98ea7eb37f7db,2026-11-09T08:15:35Z,2026-11-09T08:15:50Z,DONE,"1906 rows, 876 ING (149 DIRECT, 58 UK_US, 62 DEFAULT_FORM, 109 APPROX, 498 legacy fallback); --check passes; end time approximate"
RUN-S177-ROUTER-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,8,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 1000 --workers 8 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --gates on --out reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json",reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json,9250e8274460e8f15d5bc6da62c58cc9f8b12688b6b0ec068b3742d77db0b862,2026-11-09T08:22:23Z,2026-11-09T08:28:16Z,DONE,"final code; code_unchanged_during_run true; baseline PASS_BEFORE_AND_AFTER; DIRECT 450 -> 73, NOT_APPLICABLE 1345"
RUN-S177-ROUTER-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,24,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 700000 --workers 24 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --gates on --out reports/step23/router_demo_census_vitc_nonBBC_full_S177.json --absent-review-csv reports/s177/absent_top50_for_human_review.csv --category-blocked-csv reports/s177/absent_blocked_by_category_top50_for_human_review.csv",reports/step23/router_demo_census_vitc_nonBBC_full_S177.json,16a13887c1536bb842ea220d66f9b66491b361d564a1ad67cf624f626f91e513,2026-11-09T08:22:21Z,2026-11-09T10:40:10Z,DONE,"600848 recipes, 35256601 items; DIRECT 267933 ungated -> 40308; baseline PASS_BEFORE_AND_AFTER; code_unchanged_during_run false: git HEAD moved and other lanes changed src/ during the run, all 19 census-path code-file hashes identical; also wrote the two review CSVs (sha256 c57d4f592f662b80de3ca76e127137e288bd9ad389bd67868544d5b4d1e9b099 and 40ad176c7b15437b6af82a810529c4509709e0643eadeb544556f0f0479afbd6); ran together with RUN-006 (24 + 8 = 32 workers)"
RUN-S177-ROUTER-008,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,none (demo smoke on real ledgers),1,"PYTHONPATH=src:<scratchpad>/lxml_stub nice -n 10 python <scratchpad>/s177_smoke.py",<scratchpad>/s177_smoke2_out.txt,,2026-11-09T08:28:32Z,2026-11-09T08:32:22Z,DONE,"final code; public and local mode; output not committed; end time from the script's own 230 s timer"
```

- No run used a GPU.
- At most 32 workers ran at once.
- Server load average was 70-90 throughout.
- The earlier pre-adapter sample output was moved to the scratchpad. I did not delete anything under `reports/`.

## 9. Open questions and human decisions

1. **ING categories (blocks the egg-style abstentions).**
   - Confirm categories for the ING in `absent_blocked_by_category_top50_for_human_review.csv` (egg, salt, honey, water, cornflour, double cream, yeast and so on), or add `category` to those ING rows.
   - Until then they are UNKNOWN, by the finding's own rule, and the demo answers "baked egg" from the USDA retention-group row.
   - An optional approved-category registry hook would be a small change in `sr_identity.py`. I did not add one because it needs a new registry file and a human decision.
2. **Crosswalk.** `CATEGORY_CROSSWALK` is AI_DRAFTED and strict. A human may widen it, for example for fresh herbs filed under Vegetables. Mayonnaise (CONDIMENT vs Fats and Oils) and chocolate (NUT_SEED vs Sweets) are real mismatches that a human should look at.
3. **Top 50 ABSENT ING check.** Fill `human_verdict` in `absent_top50_for_human_review.csv`. The shipped table has 52 ABSENT ING; the list holds the top 50 of the 52 seen in the census.
4. **Adapter mapping** (consolidation Q4).
   - DEFAULT_FORM supports ABSENT only when every alternate form agrees; APPROX never does. This is as built.
   - Say if that should change.
5. **Prior-process classes.** LEACH is the whole SEPARATION family plus soak, marinate, brine and pickle. HEAT includes dry. Narrowing (for example dropping pat-dry and sift) is a human choice. The census counts the two kinds separately.
6. **Public-mode scope.** It also drops BBC-derived process, duration and tool edges, which is wider than the finding. If you want only substitution, sequence and carbon filtered, say so.
7. **Hosted detection.** `PORT` counts as a hosted marker. A local run with `PORT` set becomes public mode; use `--local` or `CS_DEMO_PUBLIC=0`.
8. **Not done.**
   - `tools/router_gate_sensitivity.py` was not re-run on the new identity. Only the census was.
   - `S176_L-ROUTER_report.md` F4 ("414 / 6") needs correcting to 216 of 220 and 4. That is not my file.
   - The `lotstate/` SUPERSEDED notice is the orchestrator's. It is now unused by the router.
9. **Engine and schema.**
   - `PRIOR_PROCESS_CONTEXT` lives at demo level, like `TARGET_ABSENT` and `MERGED_LOT_CONTEXT`.
   - It is not in the reason-code registry or the APPDEC schema.
10. **Flags.**
    - `lxml` and `hypothesis` are still missing from `.venv312`.
    - The page JavaScript was only bracket-checked and read (no `node`). Render it once before the talk.

---
*Saved by the orchestrator from the lane handback.*
