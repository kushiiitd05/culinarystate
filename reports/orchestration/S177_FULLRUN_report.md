# S177 FULLRUN report: composition census at full scale, non-BBC families

Status: AI_DRAFTED / PROPOSED (D-071 labels apply; nothing here is a human signature or approval). Role FULLRUN, round S177, 2026-11-09. Host manjot-server, tree `~/kush_work/culinarystate/.orch` (worktree `max/s176-orchestration`, HEAD a0a5b49, other lanes have uncommitted changes in the tree; `src/culinarystate/composition/`, `tools/s175_line_mass_census.py` and `reports/s175/` are byte-identical to HEAD).

## 1. Verdict

- All 8 runs finished with exit 0: FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS, TASTESET, each in line mode and in `--lots` mode, one family per run, with the unmodified `tools/s175_line_mass_census.py` as a single process (`nice -n 10`). Outputs are `reports/s177/line_mass_census_<FAMILY>_manjot.json` and `reports/s177/lot_census_<FAMILY>_manjot.json` (counts only, about 5 kB in total). Nothing was written under `reports/s175/` or `composition/`.
- Headline: BBC-style gram coverage does NOT carry over. Lines with grams: BBC 75.3%, WIKIBOOKS 59.0%, TASTESET 56.7%, FOODCOM 0.0% (all 4,129,433 lines are `UNIT_MISSING_IN_SOURCE`, as predicted), GUTENBERG_SEGMENT 0 lines (the corpus iterator hard-codes empty `ingredient_lines` for that family, see F6). Recipes whose every quantified line has grams: BBC 17.3%, WIKIBOOKS 10.0%, TASTESET 12.9%.
- Lots with a bounded water fraction: BBC 15.9%, WIKIBOOKS 12.3%, TASTESET 19.3%, FOODCOM 24.7% (envelope only, all masses unknown). pH: `ANY_MEMBER_PH_UNKNOWN` is 98 to 99% of lots in every family, so the FDA 2003 table barely constrains recipe pools.
- Bugs and hazards found (none fixed, per the S177 rule): F1 a parser gap that silently drops 284 TASTESET gram lines (outside `composition/`, `quantity/grammar.py:56-62`), F2 unhandled volume words in `line_mass.py`, F3 count path picks yield rows and does not check the counted noun, F4 uncached `PHTable.lookup` (40% of lot-mode CPU), F5 two cosmetic label issues in `lot_state.py`. Details and proposed fixes in section 7.
- Determinism: WIKIBOOKS line mode was run twice (an interactive run, then RUN-S177-FULL-001) and both outputs have sha256 e4ed9b82...05ed2.

## 2. Method and provenance

- Pre-run: `pytest tests/unit/test_s175_*.py` gave 54 passed in 2.1 s.
- Python: `.venv312` (3.12). Load average at start 67 on 128 cores; disk 532 GB free; this lane wrote under 10 kB of committed-style output and no scratch beyond the session scratchpad.
- Tool sha256 `ebea1ba381d0acbeef3faf0a5c71029bb1d8ea51e83bbfdbd6e9f134c6f299cf`; `registry/ing_sr_defaults_v1.csv` `6d668f4cf2ad36ea0ca1d822502c32bfb6b0dbf5e7777b6911f53dd7211c5957`; `registry/food_ph_fda2003_v1.csv` `e5191f2b72de95332215f9514ac4c494b3d2c6b0b28736b0929e3e1511912cfc`; one hash over `composition/*.py`, `quantity/*.py`, `extraction/rung_a_lexicon.py` and `recipes/corpus.py` (sorted path + file sha256, then sha256) `3266b51ad4d74d5f76040788a226413262deed1bfb16072a75c7596840882657`.
- Timed sample (first 5,000 Food.com recipes, same load): line mode 26.3 s plus 12 s setup, lot mode 100.3 s plus 16 s setup. Extrapolated single-process cost: line about 46 min, lots about 2.9 h. Both are under the 3 h threshold, so the optional parallel wrapper `tools/s177_parallel_census.py` was NOT written and no additivity proof was needed. Measured: FOODCOM line 43.6 min (within 5% of the extrapolation), FOODCOM lots 2.00 h (the sample over-predicted by about 30% because the name caches warm up over a full run).
- Counts-only check: the tool calls `assert_counts_only` before writing, and every run exited 0. Independently, for every family I checked that `sum(basis) == sum(q_level) == sum(match_status) == lines`.
- The three small-family run chains and the two FOODCOM runs ran concurrently (at most 3 processes of this lane at a time, well inside the 32 worker limit).

## 3. Results per family and BBC comparison

BBC columns are copied from `reports/s175/line_mass_census_BBC.json` and `lot_census_BBC.json` (Mac run, not repeated here). Percentages are of lines (line table) or of lots (lot table) unless stated.

### LINE census (counts of ingredient lines)

| metric | BBC (Mac) | WIKIBOOKS | TASTESET | FOODCOM | GUTENBERG_SEG |
|---|---:|---:|---:|---:|---:|
| recipes | 11,934 | 3,676 | 700 | 522,517 | 73,955 |
| ingredient lines | 116,699 | 32,036 | 3,788 | 4,129,433 | 0 |
| lines per recipe | 9.8 | 8.7 | 5.4 | 7.9 | 0.0 |
| **lines with grams (Q0+Q1+Q2)** | 87,891 (75.3%) | 18,910 (59.0%) | 2,147 (56.7%) | 0 (0.0%) | 0 (n/a) |
|   Q0 TEXT_STATED_MASS | 34,822 (29.8%) | 4,141 (12.9%) | 450 (11.9%) | 0 (0.0%) | 0 (n/a) |
|   Q1 COUNT_x_SR_PORTION | 22,571 (19.3%) | 4,073 (12.7%) | 586 (15.5%) | 0 (0.0%) | 0 (n/a) |
|   Q2 VOLUME_x_SR_DENSITY | 30,498 (26.1%) | 10,696 (33.4%) | 1,111 (29.3%) | 0 (0.0%) | 0 (n/a) |
|   Q6 (no grams) | 28,808 (24.7%) | 13,126 (41.0%) | 1,641 (43.3%) | 4,129,433 (100.0%) | 0 (n/a) |
|   of which QUALITATIVE | 4,799 (4.1%) | 1,617 (5.0%) | 103 (2.7%) | 0 (0.0%) | 0 (n/a) |
|   of which UNKNOWN basis | 24,009 (20.6%) | 11,509 (35.9%) | 1,538 (40.6%) | 0 (0.0%) | 0 (n/a) |
|   of which UNIT_MISSING_IN_SOURCE | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 4,129,433 (100.0%) | 0 (n/a) |
| grams resting on unverified SR link | 53,069 (60.4%) | 14,769 (78.1%) | 1,697 (79.0%) | 0 | 0 |
| **recipes: every quantified line has grams** | 2,064 (17.3%) | 368 (10.0%) | 90 (12.9%) | 0 (0.0%) | 0 (0.0%) |
| usable SR link (REGISTRY_MAPPED + AUTO_MATCH_HIGH) | 93,542 (80.2%) | 23,307 (72.8%) | 2,715 (71.7%) | 3,370,746 (81.6%) | 0 (n/a) |
|   REGISTRY_MAPPED | 90,714 (77.7%) | 22,315 (69.7%) | 2,498 (65.9%) | 3,233,174 (78.3%) | 0 (n/a) |
|   AUTO_MATCH_HIGH | 2,828 (2.4%) | 992 (3.1%) | 217 (5.7%) | 137,572 (3.3%) | 0 (n/a) |
|   AUTO_MATCH_LOW (not usable) | 3,787 (3.2%) | 2,615 (8.2%) | 354 (9.3%) | 279,838 (6.8%) | 0 (n/a) |
|   REGISTRY_UNMAPPABLE | 9,360 (8.0%) | 3,424 (10.7%) | 399 (10.5%) | 298,435 (7.2%) | 0 (n/a) |
|   NO_MATCH | 9,278 (8.0%) | 2,152 (6.7%) | 191 (5.0%) | 134,589 (3.3%) | 0 (n/a) |
|   NO_FOOD_MENTION | 732 (0.6%) | 538 (1.7%) | 129 (3.4%) | 45,825 (1.1%) | 0 (n/a) |
| UNKNOWN reason NO_AMOUNT | 6,591 | 4,785 | 334 | 0 | 0 |
| UNKNOWN reason NO_SR_FOOD | 10,574 | 5,238 | 746 | 0 | 0 |
| UNKNOWN reason NO_SR_COUNT_PORTION | 6,540 | 1,274 | 407 | 0 | 0 |
| UNKNOWN reason NO_SR_DENSITY | 304 | 212 | 51 | 0 | 0 |

### LOT census (one RECIPE_POOL lot per recipe with at least one line)

| metric | BBC (Mac) | WIKIBOOKS | TASTESET | FOODCOM | GUTENBERG_SEG |
|---|---:|---:|---:|---:|---:|
| recipes | 11,934 | 3,676 | 700 | 522,517 | 73,955 |
| lots | 11,934 (100.0%) | 3,676 (100.0%) | 700 (100.0%) | 520,298 (99.6%) | 0 (0.0%) |
| **lots with bounded water fraction (INTERVAL)** | 1,892 (15.9%) | 451 (12.3%) | 135 (19.3%) | 128,710 (24.7%) | 0 (n/a) |
| lots with water UNKNOWN | 10,042 (84.1%) | 3,225 (87.7%) | 565 (80.7%) | 391,588 (75.3%) | 0 (n/a) |
|   water width: < 0.05 | 697 (36.8%) | 138 (30.6%) | 41 (30.4%) | 8,636 (6.7%) | 0 (n/a) |
|   water width: 0.05-0.2 | 358 (18.9%) | 59 (13.1%) | 25 (18.5%) | 8,005 (6.2%) | 0 (n/a) |
|   water width: 0.2-0.5 | 319 (16.9%) | 44 (9.8%) | 14 (10.4%) | 10,829 (8.4%) | 0 (n/a) |
|   water width: >= 0.5 | 518 (27.4%) | 210 (46.6%) | 55 (40.7%) | 101,240 (78.7%) | 0 (n/a) |
| **pH flag ANY_MEMBER_PH_UNKNOWN** | 11,868 (99.4%) | 3,630 (98.7%) | 687 (98.1%) | 502,903 (96.7%) | 0 (n/a) |
| pH flag CONTAINS_ACID_MEMBER | 5,431 (45.5%) | 1,170 (31.8%) | 219 (31.3%) | 197,614 (38.0%) | 0 (n/a) |
| pH flag ALL_MEMBERS_ACID | 1 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1,184 (0.2%) | 0 (n/a) |
| lots labelled PROVISIONAL_SR_LINK_UNVERIFIED | 11,906 (99.8%) | 3,645 (99.2%) | 692 (98.9%) | 516,368 (99.2%) | 0 (n/a) |


Food.com lot note: 520,298 of 522,517 recipes form a lot (2,219 recipes have no ingredient lines). Because Food.com lines carry no units, every member mass is unknown (an unbounded interval), so the lot water interval is just the envelope of the member water fractions, not a mass-weighted estimate: 128,710 lots (24.7%) are bounded and 78.7% of those are at least 0.5 wide. The 1,184 `ALL_MEMBERS_ACID` lots and 197,614 `CONTAINS_ACID_MEMBER` lots (38.0%) are the only informative Food.com lot numbers (pH classes do not need masses). Do not read the Food.com water bounds as composition.


### How to read the comparison

- Gram yield falls from 75.3% (BBC) to about 57 to 59% (WIKIBOOKS, TASTESET) because the metric-gram habit is gone: TEXT_STATED_MASS is 29.8% of BBC lines but 12.9% and 11.9% here, and US volume lines (VOLUME_x_SR_DENSITY, 33.4% and 29.3%) take their place. Volume grams are density intervals over the SR volume portions, so they are wider and all of them rest on an unverified ING to SR link.
- The share of gram lines that rest on an unverified SR link rises from 60.4% (BBC) to 78.1% and 79.0%. In this census every Q1/Q2 gram is link-unverified by rule; only Q0 (stated mass) is not.
- SR link coverage is similar across families (usable link 71.7 to 81.6% of lines). Food.com has a usable link on 81.6% of its 4.13 million lines but no grams at all, so the Food.com corpus can feed ingredient identity and co-occurrence only, never mass.
- The recipe-level number (every quantified line has grams) is small everywhere (10.0 to 17.3%), because one line without grams (NO_SR_FOOD, NO_SR_COUNT_PORTION, NO_AMOUNT) disqualifies the recipe.
- Lot water: the lot-level water status is all-or-nothing. In my scratch analysis, 100% of UNKNOWN-water lots in WIKIBOOKS (3,225) and TASTESET (565) are `MEMBER_FOOD_UNKNOWN` (some member line has no usable SR food), none are `MEMBER_COMPOSITION_UNKNOWN`. Number of members without an SR food per recipe: WIKIBOOKS 0: 12.3%, 1: 25.3%, 2: 23.6%, 3: 17.3%, 4: 9.9%, 5 or more: 11.6%; TASTESET 0: 19.3%, 1: 32.7%, 2: 30.0%, 3: 12.9%, 4 or more: 5.2%. So tolerating exactly one unresolved member (as an unknown-mass member with water fraction in [0, 1]) would roughly triple the bounded-lot share, at the price of very wide intervals. That is a design choice for the Mac, not a bug.
- Gutenberg: 73,955 recipe records (73,778 with step text, 177 stubs flagged `RAW_SEGMENT_MISSING_LOCALLY`), 0 ingredient lines, 0 lots. The census cannot say anything about this family until ingredient lines are extracted from the step text.

## 4. Wall times

| run id | family | mode | start (UTC) | end (UTC) | wall | exit |
|---|---|---|---|---|---:|---:|
| RUN-S177-FULL-001 | WIKIBOOKS | line | 2026-11-09T07:44:00Z | 2026-11-09T07:44:59Z | 59 s | 0 |
| RUN-S177-FULL-002 | WIKIBOOKS | lots | 2026-11-09T07:44:59Z | 2026-11-09T07:46:25Z | 86 s | 0 |
| RUN-S177-FULL-003 | TASTESET | line | 2026-11-09T07:46:25Z | 2026-11-09T07:46:52Z | 28 s | 0 |
| RUN-S177-FULL-004 | TASTESET | lots | 2026-11-09T07:46:53Z | 2026-11-09T07:47:30Z | 38 s | 0 |
| RUN-S177-FULL-005 | GUTENBERG_SEGMENT | line | 2026-11-09T07:47:31Z | 2026-11-09T07:48:21Z | 51 s | 0 |
| RUN-S177-FULL-006 | GUTENBERG_SEGMENT | lots | 2026-11-09T07:48:21Z | 2026-11-09T07:48:54Z | 33 s | 0 |
| RUN-S177-FULL-007 | FOODCOM | line | 2026-11-09T07:44:00Z | 2026-11-09T08:27:38Z | 43.6 min (0.73 h) | 0 |
| RUN-S177-FULL-008 | FOODCOM | lots | 2026-11-09T07:44:00Z | 2026-11-09T09:44:08Z | 120.1 min (2.00 h) | 0 |

Single process each; the host was loaded (load average 67 to 80 on 128 cores) the whole time, so wall times are upper-end for an idle machine.

## 5. compute_runs rows (CSV, header copied from `registry/compute_runs_v1.csv`)

The orchestrator owns `registry/compute_runs_v1.csv`; these rows are PROPOSED for it. `git_commit` is HEAD plus other lanes' uncommitted changes; the code under test (composition, quantity, tool) is identical to HEAD.

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S177-FULL-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,WIKIBOOKS,1,nice -n 10 python tools/s175_line_mass_census.py --families WIKIBOOKS --out reports/s177/line_mass_census_WIKIBOOKS_manjot.json,reports/s177/line_mass_census_WIKIBOOKS_manjot.json,e4ed9b825a3136d827b3f5346790c1ef673e0bb3aa6cbbc17232d38c82f05ed2,2026-11-09T07:44:00Z,2026-11-09T07:44:59Z,DONE,"line census, unmodified tools/s175_line_mass_census.py (single process); wall 59 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,WIKIBOOKS,1,nice -n 10 python tools/s175_line_mass_census.py --lots --families WIKIBOOKS --out reports/s177/lot_census_WIKIBOOKS_manjot.json,reports/s177/lot_census_WIKIBOOKS_manjot.json,75d48214d107045ff506b5134f76eb03000b63fcd638a2d4c7999a21c772791f,2026-11-09T07:44:59Z,2026-11-09T07:46:25Z,DONE,"lots census, unmodified tools/s175_line_mass_census.py (single process); wall 86 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,TASTESET,1,nice -n 10 python tools/s175_line_mass_census.py --families TASTESET --out reports/s177/line_mass_census_TASTESET_manjot.json,reports/s177/line_mass_census_TASTESET_manjot.json,c5d18fa0a2144089cde5b983a3944a61ee1a3008a99f673495c32738b1f3fd42,2026-11-09T07:46:25Z,2026-11-09T07:46:52Z,DONE,"line census, unmodified tools/s175_line_mass_census.py (single process); wall 28 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,TASTESET,1,nice -n 10 python tools/s175_line_mass_census.py --lots --families TASTESET --out reports/s177/lot_census_TASTESET_manjot.json,reports/s177/lot_census_TASTESET_manjot.json,143004edf709c1ba733e8464a092fad1c75a6f203b1db27abac46dfdcf48a714,2026-11-09T07:46:53Z,2026-11-09T07:47:30Z,DONE,"lots census, unmodified tools/s175_line_mass_census.py (single process); wall 38 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,GUTENBERG_SEGMENT,1,nice -n 10 python tools/s175_line_mass_census.py --families GUTENBERG_SEGMENT --out reports/s177/line_mass_census_GUTENBERG_SEGMENT_manjot.json,reports/s177/line_mass_census_GUTENBERG_SEGMENT_manjot.json,b1fc1782b5d26ed803cf438ba69d4e1c29a81757c82a145c74707ffdd9b9891f,2026-11-09T07:47:31Z,2026-11-09T07:48:21Z,DONE,"line census, unmodified tools/s175_line_mass_census.py (single process); wall 51 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,GUTENBERG_SEGMENT,1,nice -n 10 python tools/s175_line_mass_census.py --lots --families GUTENBERG_SEGMENT --out reports/s177/lot_census_GUTENBERG_SEGMENT_manjot.json,reports/s177/lot_census_GUTENBERG_SEGMENT_manjot.json,4ecc2b975b064647f26b479d71637c86578368e503b9a81626eaa6b2b537d7f5,2026-11-09T07:48:21Z,2026-11-09T07:48:54Z,DONE,"lots census, unmodified tools/s175_line_mass_census.py (single process); wall 33 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,FOODCOM,1,nice -n 10 python tools/s175_line_mass_census.py --families FOODCOM --out reports/s177/line_mass_census_FOODCOM_manjot.json,reports/s177/line_mass_census_FOODCOM_manjot.json,9dcbf2142f52d41f368055b1b7dfca381bc1bee14b32f73a84be7708e4892416,2026-11-09T07:44:00Z,2026-11-09T08:27:38Z,DONE,"line census, unmodified tools/s175_line_mass_census.py (single process); wall 2618 s; counts-only assert passed (tool exit 0)"
RUN-S177-FULL-008,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),a0a5b49+uncommitted,FOODCOM,1,nice -n 10 python tools/s175_line_mass_census.py --lots --families FOODCOM --out reports/s177/lot_census_FOODCOM_manjot.json,reports/s177/lot_census_FOODCOM_manjot.json,e8ebe6707f34bdea04869321b3c91971ebe3b9ec76de9f3f8c5b05a2eb1a4c7b,2026-11-09T07:44:00Z,2026-11-09T09:44:08Z,DONE,"lots census, unmodified tools/s175_line_mass_census.py (single process); wall 7208 s; counts-only assert passed (tool exit 0)"
```

## 6. What a human must decide

1. F1 (U+2044) lives in `quantity/`, not `composition/`; decide who fixes it and then re-run TASTESET (about 30 s per mode). The Mac's duplicate `lotstate/` code already normalises U+2044 (`tests/unit/test_lotstate_line_grams.py:51`), so the consolidation review should carry that over whichever package becomes canonical.
2. F3: choose between excluding yield rows, a counted-noun guard, or only a plausibility flag; this changes the BBC numbers as well, so the BBC census would need a Mac re-run after the change.
3. Whether Food.com lots (all masses unknown) should be reported at all: their water interval is a pure envelope over member water fractions with unbounded masses. I ran them as asked and the tool labels them like any other lots; I propose a note that FOODCOM lot numbers are composition envelopes, not mass-weighted estimates.
4. Gutenberg needs an ingredient-line source before it can enter the line or lot census.

## 7. Findings: composition/ and its call path (none fixed; proposals only)

F1. Outside `composition/` but inside the call path of `line_census._line`: `src/culinarystate/quantity/grammar.py:56-62` (`normalize_text`) handles the vulgar fractions in `UNICODE_FRAC` (line 16) but not U+2044 FRACTION SLASH. TASTESET writes fractions that way: 441 of 3,788 lines (11.6%) contain U+2044 and parse as "1 item" with no volume (for example a fraction of a cup parses as count 1). Result: 380 of those lines are UNKNOWN and 58 get a COUNT_x_SR_PORTION gram value computed from the mis-parsed quantity (one item instead of a fraction of a cup or spoon). Measured by a scratch run that monkey-patches `normalize_text` at runtime (no file edited): TASTESET lines with grams 2,147 to 2,431 (+284), recipes with all quantified lines in grams 90 to 126 (+36), COUNT lines 586 to 536 (-50), VOLUME lines 1,111 to 1,386 (+275), UNKNOWN 1,538 to 1,253. Proposed fix: first statement after `s = html.unescape(s)` add `s = s.replace("⁄", "/")`, plus a unit test with "1⁄2 cup" and "1 1⁄4 teaspoons". No WIKIBOOKS line contains U+2044; Food.com does but is units-missing anyway.

F2. `src/culinarystate/composition/line_mass.py:34-36` (`_NOT_COUNT`) and `:78-87` (`portion_ml`): SR Legacy portion descriptions that start with `quart` (32 rows), `pint` (3), `liter` (3), `ml` (5) or `milliliter` (1) are volume measures but are neither converted by `portion_ml` (only cup, tbsp, tsp, fl oz) nor excluded from the count pool, so they count as per-item portions and are left out of the density interval. Effect: 40 foods compute density from fewer portions than exist, and 4 foods (fdc_id 170276, 171910, 171915, 174176) have only such rows, so any volume line for them ends as NO_SR_DENSITY instead of grams. Impact is small (BBC NO_SR_DENSITY is 304 lines). Proposed fix: add quart, pint, liter, ml, milliliter (and gallon) to `_VOLUME_WORDS` with NIST HB44 values from `quantity.units`, or at least add them to `_NOT_COUNT`.

F3. `src/culinarystate/composition/line_mass.py:120-131` (`_count_portions`, WHOLE_ITEM fallback at line 131). Two hazards. (a) `unit` is in WHOLE_ITEM, so the 182 SR rows named "unit (yield from 1 lb ...)" are used as per-item weights; they are yield conversions of a whole product, not item weights. (b) The count path never checks that the counted noun is the SR food's own item: a count of a chicken product that is not a whole bird (a wing part, an egg of a hen, a skewered dish) resolves to the whole-bird rows and gets 276 to 920 g per count. In WIKIBOOKS plus TASTESET, 128 of 4,659 COUNT lines (2.7%) use a yield row, and 64 COUNT lines have a high bound above 2 kg (WIKIBOOKS 53, TASTESET 11; VOLUME lines above 2 kg: 107; stated masses above 2 kg: 59, mostly real bulk quantities). All of these carry the SR_LINK_UNVERIFIED and PROVISIONAL labels, so this is a plausibility hazard, not a law violation. Proposed fixes (pick one, Mac decides): (1) drop portions whose description contains "yield" from `countable` (line 121-122), accepting that "1 whole chicken" then becomes NO_SR_COUNT_PORTION; or (2) in the WHOLE_ITEM fallback require that no unexplained noun stands between the count and the food term; or (3) add a per-line plausibility flag (for example high_g above 2000) to the census counts. Changing this alters the BBC numbers too (BBC NO_SR_COUNT_PORTION is 6,540 and COUNT lines 22,571).

F4. `src/culinarystate/composition/food_ph.py:120-131` (`PHTable.lookup`): scans and sorts the whole pH table on every call, no memo. In `cProfile` over 1,000 Food.com recipes (lot mode) `lookup` is 9.9 s of 25.3 s (about 40%) while there are only a few thousand distinct names. Proposed fix: memoise on the normalised name tuple (the table is immutable), for example a dict cache inside `PHTable.lookup`. This should cut the FOODCOM lot census from the measured 2.0 h to roughly 1.2 h (estimate from the profile share, not measured).

F5 (cosmetic). `src/culinarystate/composition/lot_state.py:109-110` and `:59`: for a lot whose positive-mass members all have zero water (for example only sugar), the water interval is `[-0.0, 0.0]` (negative zero from `lo = -neg`), and the solute-per-water bounds come back UNKNOWN with reason `NO_POSITIVE_MASS` although the mass is positive and it is the water that is zero (the ratio is unbounded). Proposed fix: return reason `NO_WATER_DENOMINATOR` in that case and normalise `-0.0` to `0.0`. No census number is affected (only `water_g` is reported).

F6 (structural, not a bug). `src/culinarystate/recipes/corpus.py` (GUTENBERG_SEGMENT branch of `iter_rec_corpora`) sets `ingredient_lines` to `[]` for every Gutenberg record, so line and lot census are empty by construction.

Verified OK (no bug): `lot_state.ratio_bounds` (the exact bound of a linear-fractional ratio over a mass box) agrees with a vertex enumeration on 20,000 random cases with zero mismatches (scratch test, bounded members, unbounded members and zero denominators included). The counts-only guard held in all runs.

Observations about links (registry and finder, not `composition/`): the longest-food-mention finder picks the herb for a ground-spice line of the same name (so "ground coriander" gets leaf densities), picks the dill herb for dill seed, and picks the first-listed food for compound product names (a boxed mix named after its flavour resolves to the flavour's raw meat). These are exactly why every SR gram is labelled link-unverified; they inflate the 2 kg tail and the wide intervals above.

## 8. Scratch diagnostics (session scratchpad only, not committed)

`time_sample.py`, `time_sample_lot.py`, `prof_lot.py` (timing and profile), `bf_ratio.py` (brute-force check of `ratio_bounds`), `extremes.py` (largest and widest gram intervals), `frac.py` and `fracfix.py` (U+2044 count and the runtime-patched what-if), `why_unknown.py` and `nofood_hist.py` (why lot water is UNKNOWN), `run1.sh` (run wrapper that records start, end, wall time and sha256). Third-party recipe text was printed to the terminal during diagnostics only and is not reproduced in this report.
