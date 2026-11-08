# S176 L-ROUTER: evidence routing and demo honesty

Status: **AI_DRAFTED · PROPOSED · NON_CITABLE**. Not a human gate, signature, approval or nonce. Worktree `max/s176-orchestration`
@ `07fc0d2+uncommitted`, host manjot-server, 2026-11-08. Scientific 23b stays BLOCKED; the Step 23a engine (`applicability.py`) is
byte-identical to before; NON_CITABLE / DEMO_ONLY semantics, labels and `assert_citable` are unchanged. No ledger was written
(`ledgers/data/*.jsonl` untouched), no git write, nothing installed. `lxml` is still missing in `.venv312` (flag F1 below).

## 1. Result in five lines

1. **Target-presence gate** (before G0) and **lot-context gate** are in, versioned `evidence-gates-0.1.0-draft`, switchable, and can only
   narrow a route (property-tested over random indexes). Without `gates=` the router behaves exactly as in S170/S171.
2. On the fixed 1,000-recipe non-BBC sample (seed 20261104; 57,511 items) vitamin-C **DIRECT falls 450 -> 73** (0.78 % -> 0.13 % of
   items): 59 are screened `TARGET_ABSENT`, 318 are withheld as `MERGED_LOT_CONTEXT`, 73 stay DIRECT. 9,600 items (16.7 %) are
   `NOT_APPLICABLE`. Full non-BBC census: see section 6.2.
3. **Demo honesty:** the green "Answered from data" badge now exists only when every pooled row is for the asked food and process;
   other answers get "Similar foods only", "Other foods only", "Same food, different process", "Direction only (...)" or "Sources
   disagree". A food with none of the asked nutrient gets an explicit `TARGET_ABSENT` abstention (no figure). Food-safety questions get
   an explicit `ABSTAIN_SAFETY` that points to official guidance (no number, no yes/no). "fried" and 22 other process stems/forms (broil, sear, charred, barbecu/bbq, scrambl, parboil, caramel, reheat, sous vide, freez/froze, thaw, defrost, ferment, pickl, dehydrat, dried/drying, canned/canning) are recognised; "sautéed" now parses.
   The BBC-derived "Swap buttermilk" example is replaced by "Swap ricotta" (its only edge is Wikibooks-derived).
4. **Tests:** 120 new tests; the existing router/app suites are green (280 passed without lxml, was 160; 288 with a test-only lxml stub,
   was 168; a further 2,289 tests in the wider decision/generation/contract suites pass with the stub).
5. **Human decisions needed** (section 9): the presence floor (proposed 1.0 mg per 100 g) and the identity margin (proposed 0.15), the
   ING -> SR verification queue, the food-safety referral names, and whether BBC-derived substitution edges may be served at all.

## 2. What was built

| File | Change |
|---|---|
| `src/culinarystate/mechanism/evidence_gates.py` | **new.** `TargetPresenceScreen`, `lot_members` (lineage of the Rung A graph), `EvidenceGates.evaluate`, route-strength ladder |
| `registry/target_presence_floor_v1_PROPOSED.csv` | **new, unsigned.** floor and identity margin per target SVAR (SVAR-000009 and SVAR-000215: 1.0 mg per 100 g, margin 0.15, `PROPOSED_PILOT`, `human_decision` empty) |
| `registry/ing_sr_target_content_draft_v1.csv` + `tools/build_target_content_table.py` | **new.** derived table: SR Legacy vitamin C (nutrient 1162) for the HIGH/MEDIUM rank 1-3 candidates of every ING whose rank-1 SR proposal is usable (1,873 rows, 793 ING). Public-domain SR values; the demo then needs no `data/raw`. `--check` rebuilds and compares |
| `src/culinarystate/mechanism/router_demo.py` | `route_text(..., gates=None)`; `DEMO_VERSION` 0.2.0-draft; per-item `route_ungated`, `gates`, `evidence_not_applied` when gates are on |
| `src/culinarystate/mechanism/router_census.py`, `tools/router_demo_census.py` | `gates` argument, `--gates on|off`, `--presence-floor SVAR=VALUE`; same-pass ungated counters; `CENSUS_VERSION` 0.2.0-draft; the new module is in the code hashes |
| `src/culinarystate/decision/safety.py` | **new.** food-safety cue tiers (STRONG always refuses; WEAK refuses only without a nutrient/quality target), message, referral list |
| `src/culinarystate/decision/evidence_label.py` | **new.** per-answer evidence label from the packet |
| `decision/relevance.py`, `query_router.py`, `front_door.py`, `policy.py`, `pipeline.py`, `generation/verbalize.py` | process lexicon, SAFETY intent and branch (checked first), `ABSTAIN_SAFETY`, `TARGET_ABSENT` text, accent folding for slot parsing |
| `decision/demo_context.py` | loads the gates; recipe branch runs gated; `TARGET_ABSENT` answer; `detail.evidence`; step gates in the recipe summary |
| `src/culinarystate/app/static/index.html` | badge from the evidence label, new chips and reason texts, per-step strongest item, examples |
| `tools/router_gate_sensitivity.py` | **new.** floor x margin sensitivity on one streamed sample (counts only; refuses overwrite) |
| `tests/unit/test_s176_{evidence_gates,safety,process_words,demo_honesty}.py` | **new**, 30 + 37 + 36 + 17 = 120 tests |

## 3. Gate semantics (as built)

**Order per item (event x linked ingredient):** presence screen -> lot-context gate -> G0 pre-check -> unchanged 23a engine.

*Lot membership* comes from the Rung A event graph: the members of a consumed lot are the INGREDIENT_LOT roots of its lineage. A root
with no linked ingredient (for example a named "batter" nobody produced) is a member of **unknown identity**.

*Target-presence screen* (nutrient targets that have a floor row; any other target is `NOT_SCREENED` and routes as before):
- A member's identity is its rank-1 SR Legacy proposal (`registry/ing_sr_legacy_match_draft_v1.csv`), usable only when HIGH or MEDIUM.
  Rank-2/3 rows are lexical neighbours ("salt" -> butter without salt, a turkey product), so only candidates whose match score is within
  `identity_score_margin` (0.15) of rank 1 count as plausible alternative identities.
- Member `PRESENT` if every plausible candidate has SR vitamin C >= floor; `ABSENT` if every one has a known value < floor; otherwise
  `UNKNOWN` (missing SR value, disagreeing candidates, unmatched, unknown-identity root). **UNKNOWN is never 0.**
- Lot `PRESENT` if >= 1 member is PRESENT; `ABSENT` only if every member is ABSENT and none is of unknown identity; else `UNKNOWN`.
- `ABSENT` -> route `NOT_APPLICABLE`, reason `TARGET_ABSENT` (EVD rows found are kept as `evidence_not_applied`, never as `evidence`).
  `UNKNOWN` keeps routing and adds `TARGET_PRESENCE_UNKNOWN`.
- The floor is a **screen on measured composition**. No composition value is ever shown to the user or used as an emitted number.

*Lot-context gate:* DIRECT/BRACKETING stands only when the lot the process acts on has the EVD row's food as its **sole** member. A merged
lot (>= 2 members, or one of unknown identity) withholds the pre-check: reason `MERGED_LOT_CONTEXT`, and the engine applies its existing
order to the rest. In the demo (no reviewed mechanism, no FORM/PARAM) that order ends in UNKNOWN; `INTERPOLATE` and `QUALITATIVE` can only
appear when the engine itself derives them, never from a gate. The gate adds the reason only when it actually downgrades.

*Never upgrade:* `tests/unit/test_s176_evidence_gates.py::test_gates_never_upgrade_a_route` runs 40 random (EVD index, screen, switches)
combinations over five texts and asserts `ROUTE_STRENGTH[gated] <= ROUTE_STRENGTH[ungated]` (or `NOT_APPLICABLE`), and that every
surviving DIRECT was DIRECT before and still carries its rows.

## 4. Findings made while building (negative results stay visible)

- **A rank-1-only screen produced a false `TARGET_ABSENT` for bell peppers.** The real-ledger smoke ("Roast the peppers ...") showed
  ING "pepper" (rank 1 = "Spices, pepper, black", 0 mg) screening peppers as having no vitamin C, while its rank-2/3 candidates are sweet
  red and green pepper (127.7 and 80.4 mg per 100 g). The rule was changed to require all plausible identities to agree. Margin 0.10 does
  not catch it (the gap is 0.121); 0.15 does, and it is the smallest margin tried that also keeps sugar, milk and salt screenable
  (0.20 un-screens caster sugar and milk). The margin is a `PROPOSED_PILOT` parameter tuned on this and a handful of cases, not validated.
- **The match registry is the weak link.** 1,255 of 2,048 ING (1,009 LOW, 246 NONE) have no usable rank-1 match and are UNKNOWN by construction. Of the 25 ING that
  carry vitamin-C EVD rows (SVAR-000009): 11 ABSENT (egg, milk, bacon, pasta, beef, lamb, turkey, pork, pork sausage, oatmeal, veal),
  6 PRESENT (tomato, potato, ham, fruit, sweet potato, liver), 8 UNKNOWN: chicken (SR 1.6 / 0.2 / 1.6 mg straddle the floor), cheese and
  sausage (one plausible alternative has no SR value), nut (0.5 / 5.6 / 1.2), and the four retention-group ING (green veg, veg, root veg,
  seafood) that have no SR identity at all. For SVAR-000215: 3 ABSENT, 2 PRESENT, 1 UNKNOWN (chicken). Ham is PRESENT at 4.0 mg: cured
  meats can carry added ascorbate, so this is plausible, not an error.
- **Survivors are not all vitamin-C foods.** Of the 73 DIRECT items that survive on the 1,000 sample, 40 are PRESENT and 33 are
  presence-UNKNOWN (mostly chicken, cheese, sausage and the group ING). They keep DIRECT with reason `TARGET_PRESENCE_UNKNOWN`. Resolving
  the ING -> SR queue is what would settle them.
- **REV-A's two gaps are both confirmed on the sample:** 346 of 450 ungated DIRECT items (76.9 %) reach the ingredient through a merged
  lot (28 of those in lots with no vitamin C at all); 31 more are single-member lots of a food with no vitamin C. 83.8 % of the ungated
  DIRECT items do not survive the two gates.
- **"Boiled cabbage" is honest but weak.** With the new label it reads "Similar foods only" (rows for leafy vegetables, measured for stew
  and steam, not boil) and the four recipe steps are UNKNOWN. It is kept as an example because it now shows the system declining to
  over-claim; the stronger demo is "fried potatoes" (below).
- The substitution branch is untouched: 414 of 420 ACTIVE `ING_ALTERNATIVE_TO` edges are BBC-supported (`support.by_source_family`), so any
  other "instead of X" question still returns a BBC-derived score (flag F4).

## 5. Demo behaviour on the real ledgers (smoke, one process, `lxml` stub only on `PYTHONPATH`, not installed)

| Question | Branch / mode | Evidence label |
|---|---|---|
| How much vitamin C do **fried** potatoes keep? (+ "Cut the potatoes into chips. Fry the chips for 8 minutes.") | TRANSFORMATION / ANSWER, 2 rows cited | **Answered from data** (potato, fry); steps: Cut UNKNOWN, Fry DIRECT |
| What happens to vitamin C when potatoes are **deep-fried**? | ANSWER | Answered from data |
| How much vitamin C does boiled cabbage keep? | ANSWER (near rows) | **Similar foods only**; 4 steps UNKNOWN |
| Is steaming or boiling better for vitamin C in broccoli? | COMPARE | **Compared: similar foods only** |
| How much vitamin C does baked egg keep? / Does boiling an egg destroy vitamin C? | **ABSTAIN, reason TARGET_ABSENT**, no figure, nothing cited | none (steps: NOT_APPLICABLE, row EVD-000113 shown as not applied) |
| Is chicken safe to eat if it is still pink inside? / What internal temperature should chicken reach? | **ABSTAIN_SAFETY** | none |
| What can I use instead of ricotta? | RELATIONSHIP / ANSWER_CORPUS_PATTERN ("cottage cheese 0.011") | "From recipe patterns, not data" (grey, never green) |
| Do roasted peppers keep vitamin C? (+ mixed steps) | ABSTAIN (no evidence) | peppers `TARGET_PRESENCE_UNKNOWN` (not ABSENT), eggs NOT_APPLICABLE, "bake" on the merged lot `MERGED_LOT_CONTEXT` |

Load took 78 s here; each question under a second.

## 6. Numbers

All counts-only, from `tools/router_demo_census.py` (Rung A -> unchanged 23a engine -> G0 pre-check for SVAR-000009 vitamin C, total
ascorbic acid), seed 20261104 (only its sha256 is in the reports), non-BBC families, target SVAR-000009, floor 1.0 mg, margin 0.15.
Each gated run also counts the **ungated** route of the same item in the same pass (`route_ungated`), so before and after are measured on
identical items. The gates-off path was checked against REV-A's independent count (section 6.3).

### 6.1 Fixed 1,000-recipe non-BBC sample (`reports/step23/router_demo_census_vitc_nonBBC_1000_S176.json`)

Sample: FOODCOM 859, GUTENBERG_SEGMENT 134, TASTESET 3, WIKIBOOKS 4; 997 texts with steps, 15,326 events, 57,511 items
(55,801 linked, 1,710 unlinked).

| | before (S171 logic) | after (gates on) |
|---|---|---|
| DIRECT items | **450** (0.78 %) | **73** (0.13 %) |
| UNKNOWN items | 57,061 | 47,838 |
| NOT_APPLICABLE items | - | 9,600 (16.7 %) |
| recipes with any DIRECT | 275 | 55 |

Fate of the 450 ungated DIRECT items (presence | lot context -> final route):

| presence | lot context | -> route | items |
|---|---|---|---|
| ABSENT | MERGED | NOT_APPLICABLE | 28 |
| ABSENT | SINGLE_MEMBER | NOT_APPLICABLE | 31 |
| PRESENT | MERGED | UNKNOWN (`MERGED_LOT_CONTEXT`) | 227 |
| UNKNOWN | MERGED | UNKNOWN (`MERGED_LOT_CONTEXT`) | 91 |
| PRESENT | SINGLE_MEMBER | DIRECT | 40 |
| UNKNOWN | SINGLE_MEMBER | DIRECT (`TARGET_PRESENCE_UNKNOWN`) | 33 |

Reason counts after: `TARGET_ABSENT` 9,600, `TARGET_PRESENCE_UNKNOWN` 12,970, `MERGED_LOT_CONTEXT` 318, `EVIDENCE_PREEMPTS` 73.
Surviving DIRECT by process (PROC id): 000001 bake 14, 000019 boil 13, 000071 mash 12, 000003 10, 000031 7, 000016 6, 000020 simmer 5,
000009 fry 3, 000002 roast 2, 000133 1. Lot context over all items: 32,002 PRESENT x MERGED, 5,964 ABSENT x SINGLE_MEMBER,
3,636 ABSENT x MERGED, 2,939 PRESENT x SINGLE_MEMBER, 8,478 UNKNOWN x MERGED, 2,782 UNKNOWN x SINGLE_MEMBER, 1,710 UNKNOWN x NO_LOT.

**Sensitivity** (`reports/step23/router_demo_census_vitc_nonBBC_1000_floor_sensitivity_S176.json`, same 1,000 recipes, same pass logic):

| floor (mg per 100 g) | margin | DIRECT after | NOT_APPLICABLE | ungated DIRECT -> ABSENT | -> merged-lot withheld | survivors PRESENT / UNKNOWN |
|---|---|---|---|---|---|---|
| 0.5 | 0.15 | 74 | 8,478 | 55 | 321 | 40 / 34 |
| **1.0 (proposed)** | **0.15 (proposed)** | **73** | **9,600** | **59** | **318** | **40 / 33** |
| 2.0 | 0.15 | 52 | 11,032 | 94 | 304 | 40 / 12 |
| 5.0 | 0.15 | 45 | 13,190 | 111 | 294 | 33 / 12 |
| 1.0 | 0 (rank 1 only) | 62 | 11,123 | 80 | 308 | 40 / 22 |
| 1.0 | 0.10 | 67 | 10,759 | 70 | 313 | 40 / 27 |
| 1.0 | 0.20 | 76 | 6,608 | 42 | 332 | 38 / 38 |

The merged-lot gate does most of the work at every setting (294-332 of 450); the floor moves 55-111 items between "withheld" and
"not applicable" and decides how many presence-UNKNOWN survivors remain (a floor of 2 mg pushes chicken, SR 1.6 mg, to ABSENT).

### 6.2 Full non-BBC census (`reports/step23/router_demo_census_vitc_nonBBC_full_S176.json`)

FOODCOM 522,517 + GUTENBERG_SEGMENT 73,955 + WIKIBOOKS 3,676 + TASTESET 700 = **600,848 recipes** (all READ, 0 exceptions), 599,968 texts
with steps, 9,208,811 events, **35,256,601 items** (34,243,815 linked, 1,012,786 unlinked). Seed 20261104, 24 workers, `nice -n 10`,
2026-11-08T15:18:02Z to 17:07:18Z (1 h 49 min), protected-ledger baseline PASS before and after.

| | before (S171 logic, same items) | after (gates on) |
|---|---|---|
| DIRECT items | **267,933** (0.760 %) | **34,537** (0.098 %), 87.1 % fewer |
| UNKNOWN items | 34,988,668 | 29,166,073 |
| NOT_APPLICABLE items | - | 6,055,991 (17.2 %) |
| recipes with any DIRECT (of 599,968 texts with steps) | 168,654 (28.1 %) | 28,849 (4.8 %) |

Fate of the 267,933 ungated DIRECT items (presence | lot context -> final route):

| presence | lot context | -> route | items |
|---|---|---|---|
| ABSENT | MERGED | NOT_APPLICABLE | 17,036 |
| ABSENT | SINGLE_MEMBER | NOT_APPLICABLE | 19,292 |
| PRESENT | MERGED | UNKNOWN (`MERGED_LOT_CONTEXT`) | 148,585 |
| UNKNOWN | MERGED | UNKNOWN (`MERGED_LOT_CONTEXT`) | 48,483 |
| PRESENT | SINGLE_MEMBER | DIRECT | 17,608 |
| UNKNOWN | SINGLE_MEMBER | DIRECT (`TARGET_PRESENCE_UNKNOWN`) | 16,929 |

So 13.6 % are screened target-absent, 73.6 % are withheld as merged-lot, 12.9 % stay DIRECT; 79.9 % of the ungated DIRECT items were
reached through a merged lot (REV-A: 82.5 % by its event-level count on 1,000 recipes; this run counts lot membership in the graph).
Of the 34,537 survivors, 17,608 are presence-PRESENT and 16,929 presence-UNKNOWN (the same half-and-half as on the 1,000 sample, section 4).
Reason counts after: `TARGET_ABSENT` 6,055,991, `TARGET_PRESENCE_UNKNOWN` 7,315,681, `MERGED_LOT_CONTEXT` 197,068,
`EVIDENCE_PREEMPTS` 34,537. Lot context over all items: PRESENT x MERGED 20,097,657; UNKNOWN x MERGED 4,606,540; ABSENT x SINGLE_MEMBER
3,468,956; ABSENT x MERGED 2,587,035; PRESENT x SINGLE_MEMBER 1,787,272; UNKNOWN x SINGLE_MEMBER 1,696,355; UNKNOWN x NO_LOT 1,012,786.
Surviving DIRECT by process (PROC id): 000001 bake 7,003; 000071 mash 6,296; 000019 boil 5,201; 000031 4,914; 000003 3,121; 000016 2,365;
000009 fry 1,904; 000020 simmer 870; 000133 701; 000002 roast 668; 000014 581; the rest under 400 each.
Evidence coverage unchanged: 115 EVD (ingredient, process) pairs for the target, 102 seen in the sample; 25 of 25 EVD ingredients seen.

**Comparison with S171.** The S171 JSON (`router_demo_census_vitc_full_corpus_S171.json`) pools all five families, BBC included, and holds
**no per-family counts**, so there is no S171 non-BBC subtotal to read. The same-pass ungated counters are the S171 behaviour on exactly
these recipes (verified exact against REV-A, section 6.3). Subtracting them from the pooled S171 figures gives an *implied* BBC remainder
(an inference, not a measurement; BBC data is not on this server): 11,934 recipes (all with steps), 261,379 events, 1,103,301 items,
**6,125 DIRECT** (0.56 %) and 3,696 recipes with any DIRECT, against S171's pooled 612,782 recipes, 9,470,190 events, 36,359,902 items,
274,058 DIRECT (0.754 %), 172,350 recipes. The non-BBC ungated DIRECT rate (0.760 %) is close to the pooled one, as it must be when the
remainder is small. One EVD pair seen in S171 (103) is absent here (102): it occurs only in BBC recipes. **The gated BBC figure is not
known**; the BBC census must be re-run on the Mac with `--gates on` for a pooled "after" number.


### 6.3 Reproduction check against REV-A

REV-A (`S176_REV-A_science.md` N5) reported 451 DIRECT and 57,107 UNKNOWN items on its 1,000-recipe non-BBC sample (FOODCOM 861,
GUTENBERG_SEGMENT 135, WIKIBOOKS 4). The unchanged-behaviour path (`--gates off`, families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM, same seed)
gives **57,558 items: 451 DIRECT, 57,107 UNKNOWN, exactly REV-A's numbers**, so the "before" side is the S171 behaviour. The 4-family
sample above differs by the 3 TASTESET recipes the stream adds (450 / 57,061 ungated).

## 7. Tests

| Change | Tests (file::what) |
|---|---|
| presence screen | `test_s176_evidence_gates`: member/lot states, floor equality (>=), missing SR value is UNKNOWN, unmatched is UNKNOWN, unknown-identity root blocks ABSENT, identity-ambiguity case ("pepper"), margin and floor sensitivity, floor file shape and "AI never signs" (`human_decision` empty), refusal of a 0 floor / bad key / bad unit / bad margin, registry candidate reading (LOW, rank 4, unusable rank 1 dropped), table round trip (empty stays UNKNOWN) and agreement with SR Legacy when present, `build_target_content_table.py` reproduces the shipped table |
| lot-context gate | `lot_members` on a synthetic graph (transform keeps sole member, merge, unknown root, dangling parent); merged lot withholds DIRECT; context gate switchable alone; presence precedes context; target without a floor is NOT_SCREENED |
| never upgrade, determinism | `test_gates_never_upgrade_a_route` (40 random combinations x 5 texts); same input, same output; labels and `assert_citable` unchanged; no gates = old behaviour |
| census | gated and ungated counts add up and are counts-only; parallel equals serial; CLI `--gates`, `--presence-floor`; sensitivity tool |
| badge / labels | `test_s176_demo_honesty`: the only from-data label needs asked food + asked process on every row; near-evidence cases (other process, similar foods, group row, other foods, mixed pool takes the weakest); direction-only wording; conflict; COMPARE takes the weakest; no label for ABSTAIN/ASK/...; the page assigns the green class only through `from_data` |
| `TARGET_ABSENT` answer | food without the nutrient abstains with no figure and no citation; with the nutrient it answers and is labelled; unknown presence, no gates, no floor row change nothing |
| process words | `test_s176_process_words`: 26 positive questions (fried, deep-fried, pan-/stir-/air-fried, sautéed, seared, charred, broiled, barbecued, BBQ, scrambled, parboiled, caramelised/-ized, reheated, frozen/freezing/thawing, fermented, pickled, dried, canning, sous vide, plus the old lexicon) route to TRANSFORMATION; 6 negatives ("search", "charcoal", "smoking", "fries", ...) do not |
| SAFETY | `test_s176_safety`: 23 safety questions are detected, routed to SAFETY, refused by the front door with no handler called, no digit in the answer; 10 retention/other questions are not refused; strong vs weak cue tier; the policy refuses for any caller |
| example | the page contains no "buttermilk" and no unconditional "Answered from data" |

Counts (venv as is, no `lxml`, `hypothesis` missing): **160 -> 280 passed** on the router/app set
(`test_s170_router_demo, test_s171_{router_census,query_router,front_door,demo_context}, test_s173_app_server, test_relevance, test_policy,
test_generation, test_verbalize, test_step23a_{applicability_engine,appdec_schema}`) plus the four new files. With a test-only `lxml`
stub on `PYTHONPATH` (lives in the scratchpad, not installed): **168 -> 288** (adds `test_pipeline`). Wider decision / generation /
contract / property / integration suites, stub on: **2,289 passed** (7 of those modules cannot be collected without `lxml`, as before).
`test_step23a_appdec_properties` needs `hypothesis`, which is also absent (not run, as before).

## 8. Runs (rows for `registry/compute_runs_v1.csv`; the orchestrator appends them)

Header: `run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes`

```csv
RUN-S176-ROUTER-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,16,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 1000 --workers 16 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --gates on --out reports/step23/router_demo_census_vitc_nonBBC_1000_S176.json",reports/step23/router_demo_census_vitc_nonBBC_1000_S176.json,a895166d3103b29149e0a1c896ba1cc4c97d5106bdb2f7752165b8e3b0457bba,2026-11-08T15:13:52Z,2026-11-08T15:16:15Z,DONE,"gates on; before/after in one pass (450 -> 73 DIRECT); code_unchanged_during_run true; two earlier validation runs of this sample (pre-margin gate) were discarded and their outputs deleted"
RUN-S176-ROUTER-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,8,"nice -n 10 python tools/router_gate_sensitivity.py --seed 20261104 --sample-size 1000 --workers 8 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --out <scratchpad>/sens_tool.json (copied to the output path)",reports/step23/router_demo_census_vitc_nonBBC_1000_floor_sensitivity_S176.json,4cedf3a859bebbf857aa68fc7f144cc6dbb1b5ecd108277452353f9437817628,2026-11-08T17:09:30Z,2026-11-08T17:20:14Z,DONE,"7 floor x margin variants on the same 1000 recipes; counts identical to the first run of the same logic from a scratch script (2026-11-08T15:13:53Z-15:18:46Z; variant keys renamed)"
RUN-S176-ROUTER-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS,8,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 1000 --workers 8 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM --gates off --out <scratchpad>/revA_repro_1000_gatesoff.json (copied to the output path)",reports/step23/router_demo_census_vitc_nonBBC_1000_gatesoff_REVA_repro_S176.json,1959c43c7d8d274a1865f68baf2c8ee7bf991f8fe3c3a81d2f620acad222201f,2026-11-08T15:03:58Z,2026-11-08T15:09:30Z,DONE,"reproduces REV-A N5 exactly (57558 items: 451 DIRECT, 57107 UNKNOWN); code_unchanged_during_run false because decision/ files were edited during the run (the census path files were not)"
RUN-S176-ROUTER-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,24,"nice -n 10 python tools/router_demo_census.py --seed 20261104 --sample-size 700000 --workers 24 --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --gates on --out reports/step23/router_demo_census_vitc_nonBBC_full_S176.json",reports/step23/router_demo_census_vitc_nonBBC_full_S176.json,ebff5d6928a0931acfbab32d18f139073e0fbfcab66abb7f4942973477e9ebd6,2026-11-08T15:18:02Z,2026-11-08T17:07:18Z,DONE,"600848 recipes, 35256601 items; DIRECT 267933 -> 34537; baseline check PASS before and after; code_unchanged_during_run false: HEAD moved e137130 -> b2ae1f2 (L-NH, L-PHYS commits) and src/culinarystate/simulation/* changed during the run; every file on the census path hashes identically before and after"
RUN-S176-ROUTER-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,none (demo smoke on real ledgers),1,"PYTHONPATH=<scratchpad>/lxml_stub nice -n 10 python <scratchpad>/e2e_demo.py (DemoContext.load, 13 questions)",<scratchpad>/e2e_demo_out.json,6c00b32183108410cf188922dff0a457bdbd64f5d875e474614693207678b591,2026-11-08T15:11:40Z,2026-11-08T15:13:31Z,DONE,"second smoke, after the identity-margin fix; the first smoke (2026-11-08T15:04:48Z-15:06:13Z, output overwritten) had exposed the false TARGET_ABSENT for bell peppers; output not committed; lxml stub is a test-only shim on PYTHONPATH, nothing installed"
```

No run used a GPU. The 32-worker cap held: the largest overlap was the full run (24 workers) with the tail of the scratch sensitivity run (8 workers) for under a minute.

## 9. Human decisions and open items

**Decisions only a human can make (all values are unsigned, `PROPOSED_PILOT`):**
1. **Presence floor**, proposed 1.0 mg vitamin C per 100 g edible portion (SR Legacy). Section 6.1 shows 0.5 / 1 / 2 / 5. Exact zeros are
   ABSENT at any floor above 0; the floor only decides trace foods (chicken 1.6, walnut 1.3, some nuts and cured meats). A floor of 2 mg
   moves chicken to ABSENT and cuts presence-UNKNOWN survivors from 33 to 12 of the 1,000-sample DIRECT items. No source was opened for any
   "trace level" convention; do not cite the number.
2. **Identity margin**, proposed 0.15 (rank-2/3 candidates within 0.15 match-score of rank 1 count as plausible identities). Tuned on the
   "pepper" case and three or four others; not validated.
3. **ING -> SR verification.** The screen is only as good as the AI_DRAFTED rank-1 matches (`human_decision` blank on all 5,428 rows). The
   ING that matter most for the vitamin-C story are chicken, cheese, sausage, nut, pepper and the four retention-group ING (no SR identity):
   a human verdict on those would decide 16,929 of the 34,537 surviving DIRECT items in the full census.
4. **Food-safety wording and referral names** (`decision/safety.py`): FSSAI, USDA FSIS / FoodSafety.gov, Food Standards Agency (UK), WHO
   "Five Keys to Safer Food", and the sentence "When you are unsure about a food, don't eat it" are agent-recalled
   (`SOURCE_UNVERIFIED_AGENT_RECALLED`); Kush checks each name before the page goes public. The cue list is a recall-oriented rule baseline:
   it also refuses some harmless questions ("is the cake done?"), by design.
5. **BBC-derived substitution edges** (flag F4): keep, restrict to Wikibooks-supported edges (8 edges, 4 ING pairs: ricotta/cottage cheese,
   palm oil/vegetable oil, potato starch/cornflour), or drop `ING_ALTERNATIVE_TO` from any public bundle (deployment plan H-2).
6. **Promote the gate reasons into the engine?** `TARGET_ABSENT`, `TARGET_PRESENCE_UNKNOWN`, `MERGED_LOT_CONTEXT` and the demo route
   `NOT_APPLICABLE` live at demo level (like `NO_LINKED_INGREDIENT`); they are not in `applicability_reason_code_registry_v1_DRAFT.csv`,
   `route_enum_v1_DRAFT.csv` or the APPDEC schema, because the 23a engine had to stay unchanged. REV-A (H4) asked for `TARGET_ABSENT` and
   `CONTEXT_MISMATCH` in the route enum; that is an engine and schema change for the orchestrator and, for 23b, a human.

**Flags:**
- **F1 `lxml` is still missing in `.venv312`.** `decision/pipeline.py` (and so `DemoContext.load`, `test_pipeline`, seven other test modules)
  cannot be imported here. I did not install it. The real-ledger smoke and the stub test run used a test-only stub package kept in the
  scratchpad and put on `PYTHONPATH`; `vocab/foodon.py` was not touched (G1 / T-D4 owns the lazy import).
- **F2** `hypothesis` is missing too (`test_step23a_appdec_properties` not run, as before).
- **F3 Bundle:** `DemoContext.load` now needs `registry/target_presence_floor_v1_PROPOSED.csv` and
  `registry/ing_sr_target_content_draft_v1.csv` at run time and fails loudly if they are missing; it does not need `data/raw`. Add both to
  the `demo_bundle_v1` file list (the table is derived from public-domain SR Legacy values and the AI-drafted ING -> SR registry).
- **F4** 414 of the 420 ACTIVE `ING_ALTERNATIVE_TO` edges are BBC-supported: any "instead of X" question except ricotta, cottage cheese,
  potato starch and cornflour still returns a BBC-derived co-occurrence score.
- **F5 Census provenance flag.** The full run's `code_unchanged_during_run` is `false`: the orchestrator's commits (HEAD e137130 -> b2ae1f2)
  and L-PHYS edits under `src/culinarystate/simulation/` landed during the 1 h 49 min. Only `git_commit` and `src_tree_sha256` differ;
  all hashes of the census path (`extraction/*.py`, `router_demo.py`, `router_census.py`, `applicability.py`, `evidence_gates.py`,
  `tools/router_demo_census.py`) are identical before and after (checked).
- **F6** `index.html` got a dark-mode badge-colour fix after the full run; the page is not on the census path.
- **F7 Scope.** Only vitamin C has a floor row. Other nutrient SVARs (calcium, iron, thiamin, ...) are `NOT_SCREENED` until a human
  sets a floor for each and the SR nutrient key is added to `lotstate.sr_legacy.NUTRIENT_IDS` (10 keys today). The question path applies
  only the "food alone has none of the nutrient" abstention; the merged-lot gate has no meaning for a one-food question. The gated BBC
  figure needs a Mac run (`--gates on`).
- **F8 Load.** manjot ran at a load average of 90-280 on 128 cores; routing cost about 0.5 CPU-seconds per recipe in a timing probe
  (gated and ungated alike: the gates add no measurable cost), against about 0.08 implied for S171 on vinayak.
- **F9** The page was checked by reading and by the string-level tests; no browser was available here (no `node`), so the JavaScript was not
  executed. Render the five examples once before the talk.
