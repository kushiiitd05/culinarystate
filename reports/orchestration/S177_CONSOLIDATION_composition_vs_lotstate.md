# S177 CONSOLIDATION: lot composition, `composition/` (A, Mac) vs `lotstate/` (B, server)

Status: **AI_DRAFTED / PROPOSED**. Role CONSOL, 2026-11-09. Read-only on code: no file under `src/`, `tools/`, `tests/`
or `registry/` was edited. This report is the only file written. Nothing here is a human decision. The recommendation
needs a D-079 entry from the orchestrator and sign-off from ksh/prv (D-071) or Kush/Parv.

- **A** = Mac S175: `src/culinarystate/composition/` (sr_legacy, ing_sr_match, line_mass, line_census, food_ph,
  lot_state, lot_census), `registry/ing_sr_defaults_v1.csv` (490 terms), `registry/food_ph_fda2003_v1.csv` (479 rows),
  `tools/s175_line_mass_census.py`, `tools/build_food_ph_registry.py`, `reports/s175/*`, `tests/unit/test_s175_*.py`,
  packet §11.
- **B** = server S176 lanes L-LOT and L-PH: `src/culinarystate/lotstate/` (14 modules),
  `registry/ing_sr_legacy_match_draft_v1.csv`, `registry/ing_sr_legacy_verification_queue_v1.csv`,
  `registry/food_ph_fda_draft_v1.csv` (488 rows), `registry/food_ph_fda_ing_crosswalk_draft_v1.csv`,
  `registry/lotstate_aw_constants_draft_v1.csv`, `reports/lotstate/*`, `tests/unit/test_lotstate_*.py`, S176 L-LOT and
  L-PH reports.
- **Consumer**: `src/culinarystate/mechanism/evidence_gates.py` (target-presence screen and lot-context gate) and
  `registry/ing_sr_target_content_draft_v1.csv`. Both read B's match registry. Note: another S177 lane
  (SCIFIX-ROUTER) was editing `evidence_gates.py`, its table and its tests while this review ran (13:17–13:29 IST).
  Two gate tests failed transiently at 13:15 and all 31 passed at 13:28. Section 5.3 is written against the 13:28
  state, which already has the FINAL-SCI #6 ABSENT rule and the #7 prior-process rule.

---

## 0. Verdict

1. **Make A (`composition/`) canonical.** The Mac owns it and it has run on BBC (11,934 recipes). It is also better
   on the points that decide correctness:
   - its curated identities avoid B's wrong matches;
   - its count-portion rules cover more cases;
   - it bounds composition when a member's mass is unknown, instead of falling back to presence-only.

   B's identity errors that A avoids include custard → custard-apple (B rates it HIGH), chicken thigh → frozen,
   breaded, reheated (HIGH), lemongrass → a branded carrot soup, and herb → chamomile tea.

   Unknown mass is handled as m ∈ [0, ∞): exact, conservative, and it gives an interval in 15.9 % of BBC lots
   against 0 % in B's 1,000-recipe sample.
2. **Port about ten things from B into A** (all proposals for the Mac; §5.2):
   - U+2044 normalisation;
   - the Food.com quantity/part length check;
   - the full SR size set;
   - "POINT only for stated mass";
   - the L-PH pH registry with parent context;
   - three-valued pH flags;
   - the value-record and provenance contract;
   - the `AS_LISTED_NO_PROCESS_EFFECTS` flag;
   - event-level lots from the state-graph lineage;
   - the mention-weighted verification queue.
3. **Router presence screen:** add an adapter in `mechanism/` that takes ING identity from A's registry (kind → band
   mapping, §5.3). B's match file is demoted to a source of *alternative* identities and a fallback that is capped at
   MEDIUM, so it can never support ABSENT on its own. Simulated on vitamin C (floor 1.0 mg/100 g), the number of ING
   screened ABSENT falls from 86 to 52 and their mention share from 18.8 % to 14.1 %. Every ABSENT then rests on a
   curated DIRECT, UK_US or DEFAULT_FORM identity.
4. **FDA pH: the L-PH file `registry/food_ph_fda_draft_v1.csv` (April 2007 revision, 488 rows) is canonical.** A's
   `food_ph_fda2003_v1.csv` has three problems:
   - its parser drops a row ("Pork & Beans, rts.");
   - the 53 indented child rows lose their parent ("White" could be cabbage, egg or rice);
   - it carries the superseded Tamarind value (6.00; FDA later printed 3.00).

   SSOT v16 §285.8 already names the April 2007 revision.
5. **Mark B's `lotstate/` and its two tools SUPERSEDED.** Keep the files: the S176 reports must stay reproducible,
   and the router imports `lotstate.sr_legacy` / `lotstate.intervals` until the adapter lands. Notice text is in §5.4.
   B's provisional pH census is **invalid** because of bug B1.

---

## 1. What I checked (evidence base)

| Check | Result |
|---|---|
| `pytest -q tests/unit/test_s175_*.py` | **54 passed** (7 files) |
| `pytest -q tests/unit/test_lotstate_*.py` | **105 passed** (7 files) |
| `pytest -q tests/unit/test_s176_evidence_gates.py` | 31 passed at 13:28 (2 transient failures at 13:15 while the S177 SCIFIX-ROUTER lane was regenerating the content table) |
| A's `ratio_bounds` vs brute-force corner enumeration and vs B's exact-Fraction solver | 3,000 random boxes: 0 mismatches, worst relative error 3.4e-16. Every case where A returns None is a true unbounded ratio. **Both solvers are exact.** |
| Identity agreement, A's 378 mapped terms vs B's top-3 (same ING) | B top-1 = A: 229 (HIGH 167, MEDIUM 37, LOW 25). A's food is in B's ranks 2–3: 37. Different food entirely: 99 (B band HIGH 8, MEDIUM 27, LOW 64). B has no candidate: 13 |
| Mention coverage of A's registry (B's per-ING mention counts, 4,912,063 mentions over 5 sources) | mapped **76.2 %** (DIRECT 37.2, DEFAULT_FORM 26.9, UK_US 7.4, APPROX 4.6); unmappable 7.8 % (AMBIGUOUS 6.3, NOT_A_FOOD 0.8, NO_SR_EQUIVALENT 0.7); not in registry 16.0 %. Food.com parts: 79.8 % mapped; BBC ledger: 80.1 % |
| Line probes (28 lines, A and B side by side) | see §2 rows 6–12; wrong-value cases in §4 |
| Q0 parity, TASTEset 3,788 lines × 3 locales (legacy parser in A vs rc2 in B) | Both stated mass: 464 of 464 identical grams. A stated mass where rc2 refuses: 45, all "(or …)" alternatives (`UNSUPPORTED_EXPRESSION`). rc2 stated mass where A refuses: 0 |
| U+2044 (fraction slash) in TASTEset through A | 441 of 3,788 lines contain it. Raw: **58 wrong COUNT grams**, 3 stated mass, 380 UNKNOWN. With `⁄`→`/`: 275 volume, 62 stated mass, 8 count |
| FDA HTML, 4 captures in `data/raw/fda_ph/` | 491 `<tr>` each. Tamarind prints `6.00 -` in the Jan 2004 capture and `3.00 -` from the Mar 2005 capture on. "Pork & Beans, rts." is a 3-cell row in every capture |
| Presence-screen simulation (in memory, using the current `TargetPresenceScreen`) | §5.3 |
| Already-run S177 census of A on non-BBC data (`reports/s177/*_manjot.json`, by another lane) | Wikibooks: 18,910 / 32,036 lines with grams (59.0 %); TASTEset: 2,147 / 3,788 (56.7 %); Gutenberg: 0 ingredient lines |

Scratch scripts (not committed) are in the session scratchpad `consol/`: `cmp_match.py`, `probe_lines.py`,
`tasteset_u2044.py`, `gate_adapter_sim.py`, `q0_parity.py`. They printed to stdout only and wrote no file.

---

## 2. Feature by feature

| # | Feature | A `composition/` (Mac) | B `lotstate/` (server) | Better / note |
|---|---|---|---|---|
| 1 | Scope | Line → grams; RECIPE_POOL lot (every line a member); counts-only census. ~860 lines | Line → grams; **event-level lots from the Rung A graph lineage** with SPLIT/RESERVE share intervals, plus RECIPE_POOL; per-lot JSONL records; a_w; pH interface. ~2,200 lines | B has the event-level lot unit (packet Q42). A is the leaner core |
| 2 | SR Legacy loading | 11 nutrients incl. **calcium**; floats; **drops non-ingredient categories** {3, 21, 22, 24, 25, 26, 27} (Baby, Fast, Meals, Am. Indian, Restaurant, Branded, QC; ids checked against `food_category.csv`) → 6,781 foods; portions as raw rows; missing nutrient = None | 10 nutrients, exact Fractions, keeps all 7,793 foods (category penalty only); portions classified VOLUME / COUNT / MASS / PACKAGE / OTHER; keeps the category description; skips amount ≤ 0 portions | A's exclusion keeps branded rows out of identities (B's "Mission Foods tortillas", "SMART SOUP"). B is safer on zero-amount portions (A bug A7) |
| 3 | ING → SR method | Curated registry first (490 terms, 7 kinds), then a lexical fallback (all query tokens, head-noun bonus); usable = REGISTRY_MAPPED or AUTO_MATCH_HIGH | IDF lexical scorer over segments, facets and categories, plus an AI phrase table; top-3 with HIGH / MEDIUM / LOW bands (uncalibrated); every ACTIVE ING id (2,048) | A for identity; B for breadth and as a second opinion |
| 4 | Matching quality | In most high-mention disagreements A is right: lemongrass DIRECT; chicken thigh raw; mustard powder; sunflower seed (not seed butter); basmati rice (not sake); ice = water; black peppercorn (not a dressing). Ambiguous names (pepper, cream, cheese, oil, stock, clove, chocolate, bread, vinegar) are **refused** (AMBIGUOUS) rather than guessed. Weak spots: DEFAULT_FORM choices are **UK defaults** (tinned chickpeas, frozen peas, canned tuna, canned anchovy) and are applied unchanged to US sources; a few APPROX rows are coarser than B's pick (rum → "distilled, all (gin, rum, vodka, whiskey)"; black beans → canned low-sodium) | Wrong HIGH: custard → custard-apple, chicken thigh → frozen breaded reheated, pork sausage → chorizo. Wrong MEDIUM: lemongrass → branded soup, herb → chamomile tea, fruit → passion-fruit, vegetable → canned soup, ice → ice cream. AI read (L-LOT): HIGH ≈ 93 %, MEDIUM ≈ 67 % plausible | **A** overall; B is a useful second opinion where A is APPROX. Neither is human-verified |
| 5 | Coverage | 76.2 % of all-source mentions mapped by the registry (BBC lines: 90,714 / 116,699 = 77.7 % REGISTRY_MAPPED, plus 2.4 % AUTO_MATCH_HIGH) | 94.3 % of mentions have a HIGH or MEDIUM top-1 (71.5 + 22.8) | B covers more, but that coverage includes the wrong identities in row 4. A's 16 % "not in registry" falls back to lexical |
| 6 | Quantity parser | Legacy `quantity.grammar.parse_line` + `quantity.normalize` | rc2 `ground_quantity_rc2` (frozen grammar), with U+2044 normalised first | Q0 identical on TASTEset (464/464). The rc2 policy (locale, portion rule) is the SSOT one; A bypasses it (row 11) |
| 7 | SSOT §235.3 q-levels | Stated mass Q0; count × SR portion **Q1** (AUTHORITATIVE_PORTION); volume × SR density **Q2** (AUTHORITATIVE_DENSITY); else Q6; `link_verification_required` on SR grams | Q0; both SR paths **`Q2_PROPOSED`**; Q6 | A's split follows the ladder's names. B's `_PROPOSED` qualifier is right in substance: §285.6 says SR portions need decision T3-C04-R3 against the rc2 HUMAN_VERIFIED rule. **Proposal:** keep A's Q1/Q2 and add `q_status=PROPOSED_PENDING_T3-C04-R3` |
| 8 | Stated mass | `TEXT_STATED_MASS`, SOURCE_STATED, POINT or INTERVAL | `STATED_MASS` from rc2 routes (exact, package, parenthetical) | Equal (row 6). A also accepts "(or …)" lines |
| 9 | Volume → grams | mL interval × [min, max] g/mL over **all** of the food's SR volume portions (e.g. 200 ml double cream → 101–203 g because "cup, whipped" counts) | Same hull, narrowed to the portions whose descriptor matches a prep word in the line ("chopped", "sliced", …) | Both conservative. B's text-stated narrowing is a valid refinement (port, low priority) |
| 10 | Count → grams | Size word; else a portion noun in the line (stick → stalk, rasher → slice); else whole-item portions, including **portions named by the head noun** ("potato medium"). Unsized items omit SR's extra-small, extra-large and jumbo (bug A5) | Unit word in the line ("2 garlic cloves"); size filter; parser misses head-noun portions ("1 medium potato", "1 stick celery", "3 rashers bacon" → NO_SR_PORTION) | A has more coverage; B is wider on unsized counts ("3 eggs" 114–189 g vs A's 114–150) |
| 11 | Unstated locale (Wikibooks, TASTEset, Gutenberg) | Hull over the registered conventions (cup 236.6–250 mL; tbsp 14.8–20 mL) labelled `VOLUME_x_SR_DENSITY` Q2, with no marker | **UNKNOWN** `LOCALE_AMBIGUOUS` (rc2 rule); 41 % of WB/TS lines blocked | A gives grams (Wikibooks 59 % vs B 21 %). But SSOT v16 §285.4 calls this `UNIT_HULL` (T6) and §285.6 wants a historical-unit registry for Gutenberg. A must flag it (gap A6) |
| 12 | Food.com: no units | Every FOODCOM line gets `UNIT_MISSING_IN_SOURCE` (after the QUALITATIVE check) | `FOODCOM_UNIT_STRIPPED` for bare numbers; honours a unit when present; **detects the quantity/part length mismatch** (683 / 859 recipes, 79.5 %) and pairs no quantity there (`FOODCOM_QP_LENGTH_MISMATCH`) | Same outcome today (0 Food.com grams in both). Only B knows `recipes.corpus.iter_foodcom` mis-pairs quantities in most recipes. A reads that iterator, which is harmless now only because of the blanket rule. **Port the check** |
| 13 | Qualitative / no amount | QUALITATIVE, or UNKNOWN `NO_AMOUNT`; the member mass then becomes [0, ∞) in the lot | UNKNOWN `QUALITATIVE` / `NO_QUANTITY`; the lot becomes PRESENCE_ONLY | A: exact and informative (B's report lists this as unbuilt option 6) |
| 14 | U+2044 fraction slash | **Not handled**: "1⁄2 onion" is read as 1 onion (wrong value) | Normalised to "/" before rc2 | B (bug A4) |
| 15 | Lot unit | RECIPE_POOL only ("upper envelope"); packet Q42 asks about event lots | INGREDIENT_LOT / MIXTURE / INTERMEDIATE / RESERVED_PORTION + POOL; members via lineage; share [0, 1] through partial allocations; replay status per lot | B (port, Q42) |
| 16 | Interval exactness | Linear-fractional threshold scan in floats, no outward rounding (≤ 1 ulp inside) | Same algorithm in Fractions, floats rounded outward | Both exact (§1). B is strictly safe at the last ulp; trivial to port |
| 17 | Conservativeness | Unknown mass [0, ∞) ✔. Unknown member identity → component UNKNOWN ✔. Single SR portion → POINT ✘ (§285.6). Identity is top-1 only, no candidate hull ✘ (§285.6, FINAL-SCI #8). Unsized count hull too narrow ✘ (A5) | Unknown mass → presence-only (safe, but uninformative). Single member → POINT independent of mass. Single SR portion → POINT ✘. Top-1 only ✘. ABSENT presence on MEDIUM AI identities ✘ (B6) | Neither is fully §285.6-conservative. A's fixes are small (A5, A6) |
| 18 | Solute units | `sodium_mg_per_g_water` (mg Na / g water) and `sugars_g_per_g_water`. Arithmetic checked: n = mg/100 g ÷ 100, d = g water/100 g ÷ 100. No NaCl constant | `salt_g_per_g_water` = Na × 2.5421 / 100000 ÷ (water/100). FINAL-SCI #1 (100× error) **is fixed** at `composition.py:155`, test at `test_lotstate_composition.py:87` with the < 0.36 saturation guard. 2.5421 is recalled, flagged `NACL_PER_NA_SOURCE_UNVERIFIED_AGENT_RECALLED` | **A**: it reports what SR measures (sodium) and needs no recalled constant. Convert to NaCl only behind a sourced constant (§285.7) |
| 19 | Water activity | `NOT_COMPUTED_NEEDS_SOURCED_MODEL` | Norrish sugar-only model, off by default; K and M constants recalled; UNKNOWN when any salt > 0 (so almost always); float output | **A** for now; §285.7 scopes a_w to high-solute lots with sourced constants. Keep B's constants CSV as a placeholder |
| 20 | FDA pH registry | 479 rows from the 2004-10 webharvest copy (raw on the Mac only). Typed POINT / INTERVAL / LOWER_BOUND_ONLY / UNPARSED (2). Child rows lose parent context. One row dropped. Tamarind 6.00 | 488 rows from the April 2007 revision (Wayback 2008-02-23, raw plus headers on the server, cross-checked against 4 captures). `ph_raw` kept; `parent_item_raw`, `item_context_norm`, `parse_status`, notes; deterministic builder; 7 tests | **B** (§3) |
| 21 | pH lookup | Run time: exact token match → `FDA_ITEM_MATCH`, else the union over every item with the same head noun → `FDA_HEAD_UNION` (conservative hull, but over unrelated foods when context is lost: "egg white" → onion white + cabbage + egg + rice, 5.37–7.96; "white rice" → only "Puffed Rice" 6.27–6.40, which excludes FDA's own cooked-rice rows 6.00–6.80) | ING crosswalk (AI-drafted, 1,718 rows, bands NONE / LOW / MEDIUM / HIGH / EXACT); name lookup on `item_norm`. **EXACT rows are dropped** (bug B1), so processed forms win | A's design with B's data (context) |
| 22 | pH flags | Set semantics: `CONTAINS_ACID_MEMBER`, `ALL_MEMBERS_ACID`, `ANY_MEMBER_PH_UNKNOWN`. Acid class ACID / LOW_ACID / STRADDLES_4_6 / UNKNOWN at 4.6 | Kleene TRUE / FALSE / UNKNOWN for acid, alkaline (7.0) and all-acid; per-member ranges with source id; `mixture_ph: NOT_COMPUTED` | B's three-valued form (port). §285.8 says flags are diagnostics. Neither builds the §285.8 bound [min lo, max hi] yet |
| 23 | Provenance | value_type SOURCE_STATED / MODEL_DERIVED; q_level; `link_verification_required`; lot labels MODEL_DERIVED, COMPOSITION_FROM_SR_LEGACY, PROVISIONAL_SR_LINK_UNVERIFIED; registry rows AGENT_PROPOSED / UNVERIFIED. **No** NON_CITABLE, no per-value record, no "as listed, no process effects" flag | Every value is {type, mask, unit, basis, provenance {method, labels MODEL_DERIVED + NON_CITABLE, inputs, source_ids, flags, verification AI_DRAFTED_UNVERIFIED}, exact}; `check_record` contract; `AS_LISTED_NO_PROCESS_EFFECTS`; registry `status=AI_DRAFTED` + `human_decision` column | B is closer to §199.5 / §285.3. Neither has `link_status`, `tier` or `depends_on` (§285.3–285.4) |
| 24 | Tests | 54: vertex-enumeration check, unbounded / zero-denominator, q-levels, portion rules, typo rows UNPARSED, real-registry smoke | 105: brute-force bounds, outward rounding, UNKNOWN ≠ 0, facets, generic-head cap, Food.com stripped / mismatch, Kleene tables, no recipe text in records, counts-only | Both solid; B's contract tests are worth porting |
| 25 | Runs | BBC 11,934 recipes (Mac); WB / TS / Gutenberg on manjot (S177 lane) | 1,000-recipe seeded sample (86 % Food.com) + 600 WB / TS supplement; match registry over all 2,048 ING | A has the canonical numbers |

---

## 3. FDA pH: 479 vs 488. Which counts are right, and why they differ

The FDA page has **488 item rows** (489 `<tr>` minus 1 header) in every capture. **480** of them print a pH. **8** print
none: 5 group headers (Apples, Bran, Junket type Dessert:, Rice (all cooked), Soup) and 3 bare rows (Dungeness Crab
Meat, Gherkin, Salsa).

| Bucket | A `food_ph_fda2003_v1.csv` | B `food_ph_fda_draft_v1.csv` | Reason for the difference |
|---|---|---|---|
| Rows | 479 | 488 | B keeps the 8 no-pH rows (NONE) by design. A also drops **"Pork & Beans, rts." (pH 5.70)**: its HTML row has a third empty `<td>`, which A's `len(r) == 2` test rejects (bug A1). 488 − 8 − 1 = 479 |
| POINT | 115 | 115 | Same count, different members. A types the printed "5.10 - 5.10" as POINT; B keeps it RANGE but has Pork & Beans as POINT |
| Two-sided range | 345 INTERVAL | 347 RANGE | B's two extra: "5.10 - 5.10", and Guava "3.37 - 4. 10" (whitespace repaired → 4.10, `PARSED_REPAIRED_WS`), which A keeps UNPARSED |
| Lower bound only ("x.xx -") | 17 | 17 | Same |
| Typo rows | 2 UNPARSED (Snippy "5.2l"; Guava "4. 10") | Snippy: low 5.18 kept, high empty (`UNPARSED_REVIEW`); Guava repaired | B's Snippy handling is conservative (lower bound only). The Guava repair is a deterministic whitespace removal; acceptable with its flag, but a human should confirm it |
| Value differences | Tamarind `6.00 -` | Tamarind `3.00 -` | **Source revision.** A's 2004-10 copy predates FDA's correction; the Mar 2005 and every later capture print 3.00. A's acid class for tamarind is LOW_ACID; on the current FDA text it straddles 4.6 (open upper) |
| Parent context | none (53 indented children: "White" ×3, "Canned" ×2, "Juice", "Sweet", "Red", …) | `parent_item_raw`, `item_context_norm` ("eggs, white" 7.96; "rice, white" 6.00–6.70; "cabbage, white" 6.20) | B. One B context is wrong because of the source layout: "Prunes, dried, stewed" is printed indented under Potatoes. A human must check that row |

**Right counts:** 488 table rows; 480 with a printed pH; 478 parse with no repair (461 PARSED + 17 open-ended); 1
whitespace repair; 1 partial (Snippy). A's "479 items" undercounts by one (Pork & Beans). Packet §11's "479 items" and
the SSOT v16 §285.8 sentence "488 rows (115 POINT, 347 RANGE, 17 open-ended)" are both accurate for their own files,
but only B's file is complete.

---

## 4. Correctness bugs (file:line → exact fix)

### 4.1 A (`composition/`): report to the Mac, do not fix here

| ID | Severity | file:line | Problem (evidence) | Exact fix (proposal) |
|---|---|---|---|---|
| **A4** | **MAJOR, wrong values** | `composition/line_census.py:35-37` (`_line`) | The U+2044 fraction slash is not normalised. The legacy parser reads `1⁄2 onion` as NUMBER 1, so the result is `COUNT_x_SR_PORTION` 70–150 g (true value 35–75 g); `1⁄4 cup chopped onion` → 1 onion. TASTEset: 441 / 3,788 lines contain U+2044; **58 get wrong count grams** and 337 lose a recoverable volume or mass. Food.com is masked by the blanket UNIT_MISSING rule. The BBC frequency is unknown (the Mac should count it) | First statement of `_line`: `line = line.replace("⁄", "/").replace("∕", "/")`, before `find_food` and `parse_line`. Test: `1⁄2 onion` → count 0.5 (35–75 g); `1⁄4 cup sugar` (US) → 50.0–50.4 g. Also open a ticket to fix it in `quantity/grammar.py` for every caller |
| **A1** | MAJOR | `composition/food_ph.py:99` | `len(r) == 2` drops "Pork & Beans, rts." (a 3-cell row in all 4 captures) | `if len(r) >= 2 and r[0] and r[1] and r[0] != "Item" and not any(c.strip() for c in r[2:])`. Also count the rows with an empty pH cell instead of dropping them silently. Superseded anyway by moving to the L-PH registry (§5.5) |
| **A2** | MAJOR, can be non-conservative | `composition/food_ph.py:47-70` (`_Cells`) and `:120-131` (`lookup`) | Indented child rows (`<div class="dent">`) lose their parent, so the head-union lookup joins unrelated foods. "white rice" / "brown rice" → only "Puffed Rice" 6.27–6.40, which **excludes** FDA's cooked-rice rows (6.00–6.70, 6.20–6.80). "egg white" → union of onion, cabbage, egg and rice. "apple juice" → every juice, 2.0–6.8, STRADDLES (FDA's Apples → Juice row is 3.35–4.00, ACID) | Read `registry/food_ph_fda_draft_v1.csv` and match on `item_context_norm` (fall back to `item_norm` for top-level rows). Test: "egg white" → `FDA_ITEM_MATCH` 7.96; "white rice" range contains 6.00–6.70 |
| **A3** | MINOR (one row) | `registry/food_ph_fda2003_v1.csv` (Tamarind) and `food_ph.py:21` `SOURCE` | Tamarind is taken from a superseded revision (6.00 vs 3.00) | Use the April 2007 revision (§5.5); keep the 2004 value only in a provenance note |
| **A5** | MAJOR, non-conservative interval | `composition/line_mass.py:37` (`WHOLE_ITEM`), `:70-75` (`_lead`), `:131` | Unsized counts skip SR's "extra small", "extra large" and "jumbo" portions: `_lead` returns "extra" or "jumbo", and neither is in WHOLE_ITEM. "3 eggs" → 114–150 g (SR hull 114–189); "1 banana" → 101–136 (SR 81–152). That breaks the docstring's promise of the "exact min-max over the portions used" for an unsized item | `WHOLE_ITEM = frozenset({...}) \| SIZES \| {"mini"}`. In `_lead`, join two-word sizes (`"extra large"` → `"extra_large"`) and compare `q.size` the same way, so "1 extra large egg" still picks one portion. Test: "3 eggs" → 114–189 g |
| **A6** | MAJOR (§285.6, FINAL-SCI #8) | `composition/line_mass.py:94` | SR-derived grams become POINT when lo == hi (single portion): "1 cup flour" (US) POINT 125 g, "1 litre chicken stock" POINT 1,014.4 g, "1 large onion" POINT 150 g. POINT is reserved for a stated mass | `status = "POINT" if lo == hi and basis == "TEXT_STATED_MASS" else "INTERVAL"`. Add a `flags` field with `SR_SINGLE_PORTION_NO_SPREAD` when lo == hi on an SR basis. Test |
| **A6b** | MAJOR, labelling vs proposed SSOT | `composition/line_census.py:20` (`LOCALE`: WIKIBOOKS, GUTENBERG_SEGMENT, TASTESET = None) and `line_mass.py:110-117` | When no locale is given, the volume is a hull over the registered conventions (cup 236.6–250 mL, tbsp 14.8–20 mL) but carries the Q2 label with no marker. §285.4 classes this as `UNIT_HULL` (T6). The hull has no imperial or breakfast cup, so for pre-metric text it is not guaranteed to contain the true unit; §285.6 requires a historical-unit registry before Gutenberg grams | When `locale is None` and the normalised volume came from more than one convention, set flag `UNIT_HULL_LOCALE_UNKNOWN` and `q_status=UNIT_HULL_T6`. GUTENBERG_SEGMENT → UNKNOWN `HISTORICAL_UNIT_REGISTRY_MISSING`. Human decision: keep the hull for Wikibooks and TASTEset, or follow rc2's LOCALE_AMBIGUOUS |
| **A7** | MINOR, latent crash | `composition/sr_legacy.py:93-94` (`_portions`) | 18 SR portion rows have `amount = "0"`. Nine are count-like ("chicken, bone removed" 171062 / 171450, "breast, bone removed" 171475 / 171492, "chicken, skin only" ×3, "back, …" ×2; `_lead` turns the head-noun ones into whole items). `_from_count` divides `gram_weight / amount` and would raise ZeroDivisionError for any line resolved to one of these foods through the lexical fallback. None is in the registry, so BBC did not trigger it | `if amount <= 0: continue` after line 93 (B does the same at `lotstate/sr_legacy.py` `parse_portion`). Test with a fixture row whose amount is 0 |
| A8 | MINOR | `composition/lot_state.py:110` | When every member's denominator is 0 (no water anywhere), the solute-per-water bound is labelled `NO_POSITIVE_MASS` | Return reason `NO_WATER_IN_LOT` when some member has positive mass but every d = 0 |
| A9 | MINOR | `composition/lot_state.py:100-111`, `ratio_bounds` | Float bounds are not rounded outward (at most 1 ulp inside the exact value) | `lo = math.nextafter(lo, -math.inf)`, `hi = math.nextafter(hi, math.inf)` when not exact, or port B's `float_lo` / `float_hi` |
| A10 | hygiene | `registry/ing_sr_defaults_v1.csv` | 4 terms are the canonical names of non-ACTIVE ING: "bay leaf", "feta cheese" (SUPERSEDED), "red", "white" (DEPRECATED). They are unreachable through the ACTIVE-only lexicon. The successor ING names are not covered under those keys | Re-key them to the successor ING names, or drop them; add a registry test that every term is an ACTIVE canonical name or an ACTIVE alias |
| A11 | design gap | `composition/lot_state.py` docstring and `LotState.labels` | The composition is "as listed" (no evaporation, leaching or fat loss), as in B, but A does not say so | Add label `AS_LISTED_NO_PROCESS_EFFECTS` and `NON_CITABLE` to `BASE_LABELS` |

Checked and not a bug in A:
- the solute-unit arithmetic;
- the vertex-scan solver;
- the [0, ∞) treatment of unknown mass;
- the Food.com blanket rule (it is the §285.6 lean (a));
- `_ing_names` reading every ledger row (the lexicon already keeps ACTIVE ids only).

### 4.2 B (`lotstate/` and L-PH): for the record; B is SUPERSEDED, so fix only what something still reads

| ID | Severity | file:line | Problem (evidence) | Exact fix / action |
|---|---|---|---|---|
| **B1** | **MAJOR, wrong values** | `lotstate/ph.py:36` (`BAND_RANK`), `:80` | The crosswalk band "EXACT" is not in `BAND_RANK`, so all **147 EXACT rank-1 rows are dropped** at any floor (123 ING with an EXACT row get no `by_ing` entry). `by_ing` then holds HIGH `PROCESSED_FORM` ("CORE") rows, which take precedence over the correct name row. Apricot → *canned* 3.40–3.78 (raw 3.30–4.80, ACID instead of MAYBE); carrot → 5.18–5.22 (raw 5.88–6.40); tomato → 3.50–4.70 (raw 4.30–4.90) | `BAND_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXACT": 4}`. Keep only crosswalk rows with `ph_applies_to == "ITEM_AS_PRINTED"` for raw ING. **Action now: label `reports/lotstate/lotstate_census_1000_S176_ph_provisional.json` INVALID (B1)**; do not fix code that is SUPERSEDED |
| B2 | MAJOR | `lotstate/ph.py:35` (`KEY_COLUMNS`), `:93` | Name lookups use `item_norm`, not `item_context_norm`, so the three "White" rows collide and the first one wins (`setdefault`): cabbage white is returned for every "white" | Put `"item_context_norm"` first in `KEY_COLUMNS`. Not needed once A reads the file (§5.5) |
| B3 | coverage | `lotstate/sr_legacy.py:71-125` (`parse_portion`) | Portions named by the food noun with a trailing size ("potato medium …") and the UK nouns stick and rasher are classed OTHER, so "1 medium potato", "1 stick celery" and "3 rashers bacon" give NO_SR_PORTION | none (A's rules are canonical) |
| B4 | MAJOR (§285.6) | `lotstate/values.py:39`, `lotstate/composition.py:115-119` | A single SR portion gives POINT grams, and SINGLE_MEMBER_POINT is independent of mass (FINAL-SCI #8, unfixed) | none (superseded); the A6 fix covers the canonical path |
| B5 | MAJOR (negative claim) | `lotstate/composition.py:137-148` (`_presence`) | ABSENT is asserted when every *usable* (MEDIUM or above, AI-matched) member has an SR zero: a negative claim on an unverified identity, the same class of error as FINAL-SCI #6 | none; do not port presence-only ABSENT |
| B6 | quality | `lotstate/ing_match.py:74-138` (`EXTRA_PHRASES`), `sr_legacy.py:159-160` (no category exclusion) | "cream" → heavy whipping, "chocolate" → semisweet, "clove" → the spice (often garlic in recipes); branded and restaurant rows stay eligible | Keep B's file as alternates only (§5.3) |

### 4.3 Consumer (`mechanism/evidence_gates.py`, current S177 state)

- `evidence_gates.py:129, 199-200, 229, 550` and `tools/build_target_content_table.py:26` import
  `culinarystate.lotstate.sr_legacy` (`NUTRIENT_IDS`, `NUTRIENT_UNITS`, `default_dir`) and `lotstate.intervals.frac`.
  This is the only live dependency on B. The adapter (§5.3) must replace it before `lotstate/` can be removed.
- The S177 ABSENT rule (rank-1 HIGH + all rank 1–3 of any band within the margin + category crosswalk) is sound. Its
  weak point is the *source* of "HIGH": in B's file, HIGH includes custard → custard-apple and chicken thigh → frozen
  breaded. The rule cannot tell those apart. That is why the identity should come from A's curated registry.

---

## 5. Recommendation

### 5.1 Canonical

| Item | Canonical | Status of the other |
|---|---|---|
| Lot-composition code | `src/culinarystate/composition/` (Mac) | `src/culinarystate/lotstate/` SUPERSEDED (kept) |
| ING → SR identity | `registry/ing_sr_defaults_v1.csv` (AGENT_PROPOSED / UNVERIFIED; the human verification sheet for Q44) | `registry/ing_sr_legacy_match_draft_v1.csv` RETAINED as *alternates and fallback* (non-canonical, never sufficient for ABSENT) |
| Verification queue | new sheet over A's 490 rows, ordered by B's mention counts, with B's top-3 as a second-opinion column (§5.2 P9) | `registry/ing_sr_legacy_verification_queue_v1.csv` SUPERSEDED (its mention columns are reused) |
| FDA pH registry | `registry/food_ph_fda_draft_v1.csv` (L-PH, April 2007, 488 rows); propose renaming it on promotion to `registry/food_ph_fda2007_v1.csv` | `registry/food_ph_fda2003_v1.csv` SUPERSEDED |
| pH crosswalk | none consumed; `registry/food_ph_fda_ing_crosswalk_draft_v1.csv` stays a DRAFT review sheet (EXACT / FULL rows only, after a human check) | — |
| a_w constants | none consumed (§285.7) | `registry/lotstate_aw_constants_draft_v1.csv` kept as SOURCE_UNVERIFIED placeholder |
| Census numbers | `reports/s175/*` (BBC, Mac) and `reports/s177/*_manjot.json` (non-BBC, re-run after the fixes) | `reports/lotstate/*` historical; `..._ph_provisional.json` **INVALID** (B1) |

### 5.2 What to port from B into A (proposals for the Mac; the Mac decides and implements)

| P | What | From B | Into A | Priority | Test that proves it |
|---|---|---|---|---|---|
| P1 | U+2044 / U+2215 → "/" | `line_grams.normalise_text` | `line_census._line` (fixes A4) | **now** | `1⁄2 onion` → 35–75 g |
| P2 | Food.com quantity/part length check | `lotstate/corpus._foodcom_record` (`q_len`, `p_len`, unpadded `q_raw`), `units_check.py` | expose `q_len` / `p_len` in `recipes/corpus.iter_foodcom` `extra` (owner of `recipes/` decides), and reason `FOODCOM_QP_LENGTH_MISMATCH` in `line_mass` counts | now (counts only) | unequal-length fixture → no quantity is paired; the units-check verdict stays `CONFIRMED_UNITS_ABSENT` |
| P3 | Full SR size set for unsized counts | `sr_legacy.SIZE_WORDS` (extra small, extra large, jumbo, mini) | `line_mass.WHOLE_ITEM` / `_lead` (fixes A5) | **now** | "3 eggs" → 114–189 g |
| P4 | POINT only for stated mass | FINAL-SCI #8 (unfixed in B too) | `line_mass._interval` (fixes A6) | **now** | SR single portion → INTERVAL + `SR_SINGLE_PORTION_NO_SPREAD` |
| P5 | L-PH registry with parent context | `food_ph_fda_draft_v1.csv` columns `item_context_norm`, `parse_status`, `ph_raw` | `food_ph.load_registry_lph()` + match on context (fixes A1–A3) | **now** | 480 rows with a value, 8 NONE; Pork & Beans present; Tamarind 3.00 open; "egg white" `FDA_ITEM_MATCH` 7.96 |
| P6 | Three-valued pH flags (+ optional alkaline) | `ph.member_status`, `ph.lot_flags` | `lot_state._ph` (replace set semantics with TRUE / FALSE / UNKNOWN) | next | B's Kleene table tests |
| P7 | Value-record and provenance contract | `values.py` (`numeric`, `unknown`, `qualitative`, `check_record`, `NON_CITABLE`), flag `AS_LISTED_NO_PROCESS_EFFECTS` | a `composition/records.py` export view mapping LineMass / Bound / LotState to §285.3 objects with `link_status=AI_MATCHED`, `tier=T6` while any link is unverified, `depends_on` | next | `check_record` on every exported value; tier = weakest link |
| P8 | Event-level lots (packet Q42) | `lots.LotStateBuilder._graph_lots` (lineage, SPLIT / RESERVE / REMAINDER / DISCARD / RECOMBINE shares [0, 1], same-ING roots [0, total], replay status) | a `composition/event_lots.py` that builds A `Member`s; reuse `mechanism.evidence_gates.lot_members` semantics for the lineage | after Q42 is answered | `test_lotstate_lots.py` scenarios re-expressed on A members |
| P9 | Mention-weighted verification queue | `mention_freq.py` counts (BBC ledger, Food.com parts, Wikibooks, TASTEset, Gutenberg) | a review sheet over A's 490 rows: mentions, cumulative share, B's top-3 (fdc, band) and an `A_vs_B` flag (same / in top-3 / differ / B none) | for Q44 | the sheet reproduces 76.2 % mapped mention share |
| P10 | Exact or outward-rounded bounds | `intervals.float_lo` / `float_hi` | `lot_state.ratio_bounds` output (A9) | low | B's rounding tests |
| P11 | Prep-word density narrowing | `line_grams._prep_words` | `line_mass._from_volume` (only when the line states the prep; else keep the full hull) | low | "1 cup chopped onion" uses only the chopped portion |
| — | **Do not port** | NaCl-equivalent (recalled constant), Norrish a_w, presence-only ABSENT, B's lexical bands as identity, B's category-penalty SR set | — | — | — |

### 5.3 Router presence screen: an adapter in `mechanism/` over A's registry (manjot)

The screen's interface already fits: `TargetPresenceScreen(floors, cands, values, categories)` with
`cands[ing_id] = ((fdc_id, band, score), …)` (rank 1 first), `values[(fdc, key)]` and
`categories[ing_id] = (ing_category, sr_food_group)`. The proposal is a new module
`src/culinarystate/mechanism/sr_identity.py`. It imports `composition.ing_sr_match.load_registry` and `normalise`, and
`composition.sr_legacy.load_sr`, and copies nothing. It builds those three maps:

| A registry kind | Candidates given to the screen | Can it support ABSENT? |
|---|---|---|
| DIRECT, UK_US | `(fdc, "HIGH", 1)` alone | yes, if the category is confirmed and the SR value is known and below the floor |
| DEFAULT_FORM | `(fdc, "HIGH", 1)` + B's rank 1–3 foods for that ING as `"LOW"` alternates at the same score (so they sit inside the identity margin). A's default forms are UK defaults (tinned chickpeas, frozen peas, …), so other forms must be checked too | yes, only if **every** form is known and below the floor |
| APPROX | `(fdc, "MEDIUM", 1)` | no (PRESENT only) |
| NO_SR_EQUIVALENT, NOT_A_FOOD, AMBIGUOUS | none (unknown identity) | no |
| term not in the registry (16 % of mentions) | B's rank 1–3 with HIGH capped to MEDIUM | no (PRESENT only) |

Other details:
- `sr_food_group` comes from `food.csv` → `food_category.csv` for the rank-1 fdc.
- `ing_category` comes from the latest ACTIVE ING row.
- Nutrient keys map from B's names ("vitamin_c", as in `target_presence_floor_v1_PROPOSED.csv`) to A's ("vitamin_c_mg"); both are SR nutrient 1162.
- The provenance gains `identity_source = ing_sr_defaults_v1 (+ legacy_match alternates)` and the registry sha256.
- `tools/build_target_content_table.py --identity defaults` writes the shipped table from the adapter, keeping the 11 columns plus `identity_source` and `registry_kind`, so `EvidenceGates.load()` keeps reading a table and needs no `data/raw` at run time.

Simulation (in memory, vitamin C SVAR-000009, floor 1.0, margin 0.15, the current S177 rule, 2,048 ACTIVE ING;
mention weights from B's queue):

| Identity source | ABSENT ING | PRESENT | UNKNOWN | ABSENT share of mentions |
|---|---|---|---|---|
| B match file (current) | 86 | 263 | 1,699 | 18.8 % |
| A registry, DIRECT / UK_US → HIGH only | 41 | 317 | 1,690 | 7.3 % |
| A registry, every curated kind + all B alternates | 28 | 317 | 1,703 | 2.9 % |
| **Recommended mapping (table above)** | **52** | **317** | **1,679** | **14.1 %** |

Under the recommended mapping:
- **Stay or become ABSENT:** butter, flour, olive oil, sugar kinds, black pepper, cream cheese, chicken breast, minced beef, wine, rice, pasta, skimmed milk, curry powder, maple syrup, …
- **Leave ABSENT**, for three reasons. The alternates disagree or lack a value: milk (B's condensed and evaporated alternates carry 1.9–2.6 mg) and sugar (a sugar-substitute alternate has no SR value). A calls the name AMBIGUOUS: cream, vinegar, bread. The row is APPROX or uncurated: sherry, chocolate chips. That is the conservative direction.
- **Gain PRESENT:** basil, nutmeg, apple, corn, mint, sage.

These are AI simulation numbers for sizing, not results. FINAL-SCI #6's human check of the top 50 ABSENT ING by item
count still applies, now on the 52.

### 5.4 SUPERSEDED marks (keep the files; texts to apply later, after D-079)

**`src/culinarystate/lotstate/__init__.py`**: prepend to the docstring and change `STATUS`:

```text
SUPERSEDED (S177 consolidation, D-079 PROPOSED): the canonical lot-composition layer is culinarystate.composition
(Mac, S175). This package is kept read-only so that reports/lotstate/* and S176_L-LOT_report.md stay reproducible.
Do not build on it and do not import it from new code. Live importers until the S177 adapter lands:
mechanism/evidence_gates.py and tools/build_target_content_table.py (sr_legacy.NUTRIENT_IDS / NUTRIENT_UNITS /
default_dir, intervals.frac). Ported pieces and known defects left unfixed on purpose (ph.py EXACT band, item_norm
key, single-portion POINT, presence-only ABSENT): reports/orchestration/S177_CONSOLIDATION_composition_vs_lotstate.md.
```
`STATUS = "SUPERSEDED_S177_BY_COMPOSITION"`

**Each `lotstate/*.py` module and `tools/lotstate_match_ing.py`, `tools/lotstate_census.py`**: first docstring line:
`SUPERSEDED (S177, D-079 PROPOSED) by culinarystate.composition; kept to reproduce S176 reports only.`

**`reports/lotstate/lotstate_census_1000_S176_ph_provisional.json`**: append a note to
`S176_L-LOT_report.md` §6 (do not rewrite the JSON; its sha256 is logged):
`INVALID (S177 CONSOL B1): lotstate/ph.py dropped every EXACT crosswalk row, so processed-form pH ranges replaced raw
ones (apricot, carrot, tomato, …). The flag counts in this file must not be cited.`

**Registry CSVs** (CSV readers cannot take a comment row): a sidecar `registry/SUPERSEDED_S177.md`:

```text
registry/ing_sr_legacy_match_draft_v1.csv       RETAINED, NON-CANONICAL: alternates + fallback (capped MEDIUM) for the
                                                 router presence screen; identity of record is ing_sr_defaults_v1.csv.
registry/ing_sr_legacy_verification_queue_v1.csv SUPERSEDED by the review sheet over ing_sr_defaults_v1.csv (mention
                                                 columns reused).
registry/food_ph_fda2003_v1.csv                  SUPERSEDED by food_ph_fda_draft_v1.csv (April 2007 revision, 488 rows;
                                                 this file lacks "Pork & Beans, rts.", parent context, and has the
                                                 pre-2005 Tamarind value).
registry/food_ph_fda_ing_crosswalk_draft_v1.csv  DRAFT review sheet, not consumed (PROCESSED_FORM rows map processed
                                                 items onto raw ING; only EXACT/FULL ITEM_AS_PRINTED rows are candidates
                                                 after a human check).
registry/lotstate_aw_constants_draft_v1.csv      NOT CONSUMED; SOURCE_UNVERIFIED_AGENT_RECALLED placeholder for §285.7.
```

**SSOT v16 §285.1** (orchestrator-only file, wording proposal): replace "The S176 lane code
`src/culinarystate/lotstate/` … are uncommitted AI drafts" with "The canonical lot-composition code is
`src/culinarystate/composition/` (S175); `lotstate/` (S176) is SUPERSEDED (S177 consolidation)".

### 5.5 Which FDA pH registry is canonical: `registry/food_ph_fda_draft_v1.csv`

1. It is the later FDA revision (April 2007; the table equals the Mar 2005 capture), with the Tamarind correction.
2. It is complete: 488 rows, no row dropped, and the no-pH rows are explicit.
3. It keeps the raw printed text, parse status and notes for every quirk, and repairs nothing by guess (Snippy is left
   open).
4. It keeps parent context for the 53 indented rows.
5. Its raw source sits on the server with its headers and sha256 and was cross-checked against 4 captures. Its builder
   is deterministic, with 7 invariant tests.
6. SSOT v16 §285.8 already cites it.

A's run-time lookup (exact token match, then a head-noun union, then `any_form` bounds) and its acid classes stay as the
consumer logic. Only the data file and the match key (`item_context_norm`) change.

---

## 6. Migration steps, owners and the tests that show nothing regressed

| Step | Owner | Action | Gate (must pass) |
|---|---|---|---|
| M0 | orchestrator (manjot) | Record D-079 PROPOSED: composition canonical, L-PH registry canonical, lotstate SUPERSEDED, no new lotstate features (already in the 09 Nov UPDATE). Send §4.1 and §5.2 to the Mac as a fix list | ksh/prv (D-071) or Kush/Parv sign-off |
| M1 | **Mac** | Fix A4 (P1), A5 (P3), A6 (P4), A7, A11 in `composition/`; add the tests listed in §4.1; bump `line_census.VERSION` / `lot_census.VERSION` to 0.2.0 | `pytest tests/unit/test_s175_*.py` (54 + new) green |
| M2 | **Mac** | P5: `food_ph` reads `registry/food_ph_fda_draft_v1.csv` (copy it from the branch) and matches on `item_context_norm`; mark `food_ph_fda2003_v1.csv` SUPERSEDED; P6 Kleene flags | `test_s175_food_ph.py` updated: 480 valued rows, Pork & Beans, Tamarind 3.00 open, "egg white" 7.96, "white rice" ⊇ 6.00–6.70; `tests/test_food_ph_fda_draft.py` (7) still green |
| M3 | **Mac** | Re-run the BBC line and lot census (D-003: Mac only); report deltas vs `reports/s175/*` | Expected: `lines_with_grams` changes only through U+2044 lines (Mac to count); every other change is a POINT → INTERVAL relabel (A6) or a wider count interval (A5); `ph_flags.CONTAINS_ACID_MEMBER` moves only through context rows and Tamarind; no new crash |
| M4 | manjot | After the SCIFIX-ROUTER lane closes `evidence_gates.py`: add `mechanism/sr_identity.py` (§5.3), switch the gate's `lotstate.sr_legacy` / `intervals` imports to the adapter, and add `tools/build_target_content_table.py --identity defaults` → regenerate `registry/ing_sr_target_content_draft_v1.csv` (or a v2 file) | new `tests/unit/test_s177_sr_identity_adapter.py`: kind → band mapping; unmappable → UNKNOWN; ABSENT never from APPROX or uncurated; regressions lemongrass, herb, coleslaw and custard never ABSENT; the §5.3 counts as a snapshot (52 / 317 / 1,679). Plus `tests/unit/test_s176_evidence_gates.py` (31) and `tests/unit/test_s177_router_gates.py` green, and the never-upgrade property test unchanged |
| M5 | manjot | Re-run the router demo census and gate sensitivity (`tools/router_demo_census.py`, `tools/router_gate_sensitivity.py`) and diff the presence-state counts before and after | Only the presence screen's ABSENT / PRESENT / UNKNOWN counts change; route strengths never rise; protected ledgers `ledgers/data/{EVD,COND,SRC,MEAS,SNAP}.jsonl` sha256 unchanged |
| M6 | manjot | Apply the §5.4 notices (code docstrings, sidecar, L-LOT §6 note); keep `tests/unit/test_lotstate_*.py` running unchanged | `pytest tests/unit/test_lotstate_*.py` still 105 passed (notices are docstring-only) |
| M7 | manjot | Re-run A's non-BBC census (Wikibooks, TASTEset, Gutenberg; Food.com counts-only) with the M1 code, 1,000-recipe sample first (`--seed 20261104`), and log to compute_runs | Wikibooks / TASTEset deltas explained by A4 / A5 / A6b; Food.com 0 grams |
| M8 | manjot → humans | P9 review sheet over A's 490 rows; humans verify (Q44), top 50 ABSENT first (FINAL-SCI #6) | human decisions recorded; PROVISIONAL is lifted only for verified rows |
| M9 | Mac, later | P7 (records, tiers), P8 (event-level lots, after Q42), P2 at the corpus source | contract tests ported from `test_lotstate_composition.py` / `test_lotstate_lots.py` |
| M10 | orchestrator, later | Once nothing imports `culinarystate.lotstate` (`grep -rn "culinarystate.lotstate" src tools` empty apart from lotstate itself), move the package to an archive path or leave it frozen | full `pytest -q` green |

---

## 7. Open questions for the humans (nothing decided here)

1. Approve D-079 as proposed (composition canonical; the L-PH file canonical; lotstate SUPERSEDED)?
2. Unstated-locale volumes (A6b): keep A's convention hull, flagged `UNIT_HULL`, for Wikibooks and TASTEset, or follow
   rc2 (UNKNOWN)? This is the main reason A gets about 59 % grams on Wikibooks where B gets 21 %.
3. Q-level label for SR grams before T3-C04-R3: A's Q1/Q2 with `q_status=PROPOSED`, or B's single `Q2_PROPOSED`?
4. Adapter mapping (§5.3): may DEFAULT_FORM support ABSENT when every alternate agrees? May APPROX ever do so?
5. The Guava whitespace repair and the parent context of "Prunes, dried, stewed" in the L-PH file need a human look.
6. Q41 to Q44 from packet §11 stand. Q42 decides whether P8 (event lots) is built.

---

## 8. Runs

No compute run in the `registry/compute_runs_v1.csv` sense. The probes above are small, single-process,
read-only scripts on manjot-server (nice 10, no GPU): TASTEset 3,788 lines; the 2,048-ING screen simulation; 3,000
random solver boxes. They printed to stdout only, so there is no output sha256. They are recorded here for
traceability:

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
PROBE-S177-CONSOL-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,TASTESET,1,scratchpad consol/q0_parity.py + tasteset_u2044.py,stdout,n/a,2026-11-09T07:49Z,2026-11-09T07:58Z,DONE,"read-only probes; no file written; Q0 parity 464/464; U+2044 441 lines"
PROBE-S177-CONSOL-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,ING ledger + SR Legacy,1,scratchpad consol/cmp_match.py + gate_adapter_sim.py,stdout,n/a,2026-11-09T07:40Z,2026-11-09T07:55Z,DONE,"identity agreement and presence-screen simulation; in memory only"
```
