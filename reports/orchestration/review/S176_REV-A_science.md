# S176 REV-A: science review of the Max-plan packet (food science, process engineering, physical chemistry)

Status: **AI_DRAFTED · PROPOSED · NON_CITABLE**. Not a human gate, signature, approval or nonce. Under D-071 a persona
proposes; Kush and Parv decide. Reviewer persona REV-A ("Max plan" external reviewer: senior food scientist,
food-process engineer, physical chemist), 2026-11-08. Worktree `max/s176-orchestration` @ `07fc0d2+uncommitted`.
Read-only on the repo apart from this file. Any number in this review that has no repo path or URL next to it is
**SOURCE_UNVERIFIED_AGENT_RECALLED** (leak L-19 in §E.8), including the reviewer's own.

**What I read.** The orchestration brief; the whole packet (`handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md`);
`src/culinarystate/simulation/{physics_drivers,scenario_layer,condition_binding,sim_aa_1,sim_chl_1,choi_okos}.py` and
the product-temperature modes in `sim_core.py`; `src/culinarystate/mechanism/applicability.py` (`_route`) and
`router_demo.py` (`precheck`, `_lot_ingredients`); `registry/{scenario_defaults_v1,process_medium_map_v1,
mechanism_seed_roster_draft_v1,state_variable_registry_v1}.csv`; `ledgers/data/SVAR.jsonl` (counts only);
`registry/evidence/aa_kinetics_source_candidates_v1.csv`; `reports/step10/aa_pilot_preregistration_DRAFT.md`;
`reports/step26/{binding_census_L1,scenario_L2}_*_S17*.json`; `reports/step23/router_demo_census_vitc_full_corpus_S171.json`;
the KGE `PROC_TYPICAL_DURATION` rows; SSOT §4, §141, §144, §199, §208.2–208.4, §208.8, §210.13/.15/.21/.22,
§212.31–212.35, §213.12/.25–.28 (line ranges from `docs/SSOT_INDEX.md`); plan Steps 03, 21, 22, 31 and 35; and the
sibling lane report `reports/orchestration/S176_L-PH_report.md`.

**What I ran** (read-only; scratch scripts only; counts only; listed in §7): (1) `ScenarioLayer.run` on 7 synthetic
heat events; (2) `physics_drivers` comparisons (boundary cap, cube vs slab); (3) a 1,000-recipe seeded (`20261104`)
non-BBC breakdown of vitamin-C DIRECT routes by (ingredient group, process) and lot context.

---

## A. Verdict

The epistemics are better than in most food-informatics projects I review: UNKNOWN is a first-class value, defaults are
labelled, routing puts evidence first, and the failures stay on the record. The science underneath has three
load-bearing problems that the packet does not show, and the first is a physics error already in the full-corpus
outputs. **(1)** The Layer-2 heat model ignores evaporation, so it lets moist cores reach the oven, oil or pan
temperature. I reproduced cores of 163–220 °C for diced, sliced and chopped pieces, with cook values inflated by about 10² (V2). Every
DRY/FAT driver with a size class in `scenario_L2_*` is affected. Fix it before any feature, screen or slide uses those
drivers. **(2)** DIRECT does not mean "a measured value applies". It fires on the (ING id, PROC id) pair alone. That
includes USDA retention groups such as egg, cheese, pasta and beef, which contain almost no vitamin C, and ingredients
buried in merged batters. In a 1,000-recipe sample, 81 % of DIRECT routes are for foods with ≈ 0 mg vitamin C, and 83 %
reach the ingredient through a merged lot (V5, N5). The 0.754 % headline therefore overstates real evidence coverage; a target-presence gate
and a context gate are needed. **(3)** The first SIMULATE system is calibrated on acidic fruit juices and nectars, with
leaching unidentified, but it is meant for vegetables in water. Its validity domain must be gated by matrix, and the
reduced-AA versus total-vitamin-C basis must be matched (V7).

Beyond these three, the lot-state design ([K], packet §5) is sound in spirit but needs four changes to be defensible:
- **Phase-resolved mixtures:** aqueous, lipid, solid pieces and gas, instead of one merged composition.
- **A provenance lattice:** every computed field inherits the weakest basis and claim class of its inputs, computed
  mechanically.
- **Physical interaction edges:** thermal mixing, medium, transport and partition, alongside the mechanism edges.
- **A pH bound instead of flags:** under ideal closed-system mixing, the pH of a mixture lies within its members' pH
  range. This is provable without buffer data (N1), and it supports Kleene gating and counterfactual directions.

Several proposed formulas need correcting. F₀ (121.1 °C, z = 10 °C) is the botulinum reference for canning, not a
cooking-safety reference. Thawing is not the mirror image of freezing. Fick's law bounds uptake from a brine but does not describe
acid marinades. Apart from the human verifications already on the critical path, none of this needs new data before
25 Nov: the fixes are code, registry entries and wording.

---

## V. Repo-verified facts the answers depend on (V-table)

| # | Packet claim or design | What the repo shows | Evidence | Consequence |
|---|---|---|---|---|
| V1 | "810,951 heat events (46 %) get driver trajectories" | 810,951 get a bath T and a duration (plus a surface dose for immersion media). Only **69,995** get a core trajectory, because a size class is needed: 8.6 % of computed scenarios and 4.0 % of the 1,746,405 heat events. Among computed scenarios, **67.7 %** of bath temperatures are SD defaults (549,070 of 810,951) and **60.5 %** of durations are KGE corpus quantiles (490,403). | `reports/step26/scenario_L2_{A1,FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS}_full_S17*.json` (`counts`; the TASTESET file is empty) | Reword the headline. The scenario dataset is mostly default-driven. |
| V2 | "The slab model gives core temperature" | For DRY/FAT media the slab boundary is the medium temperature, with no evaporation term. Moist cores reach **163.7 °C** (bake, diced, 30 min, TYPICAL), **163.4 °C** (deep-fry, diced, 5 min), **170 °C** (sauté, sliced, 8 min) and **220 °C** (roast, INTENSE). Cook values reach 10²–10⁵ equivalent minutes. Capping the boundary at 100 °C, an upper bound for a wet surface at 1 atm, gives 91.9 °C and 94.0 °C, with cook values of **6.3 instead of 601.9** and **1.2 instead of 101.7**. The surface cook value for oil immersion is also computed at the oil temperature (2,668 eq-min for 5 min at 190 °C), although a wet surface sits near 100 °C until it dries. | `scenario_layer.py` `run()` (`bath_c` is used as the boundary for every medium); `physics_drivers.core_temperature`; my runs (§7) | A physics error. It affects every DRY/FAT event with a size class and blocks the uses in Q1 and Q3 until fixed. |
| V3 | GENTLE / TYPICAL / INTENSE | GENTLE and INTENSE are joint corners: every factor sits at its extreme at once. TYPICAL is the per-factor mid, not a mode. k and α stay at mid in all brackets. One property class (`FOOD_HIGH_MOISTURE`) is used for every food, including oil-rich foods, syrups, doughs and frozen food. Durations are per-process quantiles that ignore the food (simmer p10/p50/p90 = 4/20/240 min, so INTENSE simmer is a stock). | `scenario_layer.py`; KGE `PROC_TYPICAL_DURATION` | The brackets are a sensitivity envelope, not a distribution. Never print TYPICAL as "the estimate". |
| V4 | Default durations | All 93 ACTIVE KGE `PROC_TYPICAL_DURATION` rows come from SRC-000002 (A1, BBC Good Food) and SRC-000140 (Wikibooks), with n = 16–3,030 recipes per row (median 124), UNVERIFIED. They fill durations for Food.com and Gutenberg. Several processes have more than one ACTIVE row with different n (simmer: n = 246, 778, 847). `ScenarioLayer.load` silently keeps the last one in file order. | `ledgers/data/KGE.jsonl` (e.g. KGE-007574–007576); `SRC.jsonl` | Population shift (historical and US recipes filled from modern UK ones). A BBC-derived statistic now sets parameters for server outputs; record a D-003 ruling (aggregates are probably fine). Test-split leakage for Step 35 (L-14). |
| V5 | Router "DIRECT 274,058 (0.754 %)" | DIRECT fires whenever any EVD row exists for (ING id, PROC id, SVAR). The demo has no condition, food-form or matrix check (`conditions_consumed: false`), and the domain flag is only appended as a G9 reason: the route is DIRECT whenever the pre-check finds a row. The lineage walk links every ancestor ingredient of a merged lot to the event. The vitamin-C EVD "ingredients" are USDA retention groups; for bake: egg, cheese, pasta, beef, nut, seafood, potato, sweet potato, fruit, veg, green veg, root veg. **1,000-recipe non-BBC sample (N5):** 451 DIRECT, of which **364 (80.7 %)** are groups whose standard SR Legacy items hold ≈ 0 mg vitamin C/100 g (egg, cheese, meat, milk, pasta, nuts). Egg × bake alone is 111 (24.6 %). **372 (82.5 %)** reach the ingredient through a multi-ingredient lot. | `router_demo.precheck`; `applicability._route`; `EvidenceIndex.pairs("SVAR-000009")` | DIRECT means "the pair has a row", not "the evidence applies". Needs target-presence and context gates (C-sci 19–20). |
| V6 | "355 SVAR: 354 chemical, 1 physical" | 355 *records* = **224 distinct ids** (223 chemical, 1 physical; 131 ids have two versions). The registry CSV already reserves **30 FUTURE SVARs**: 12 physical (moisture, a_w, volume, density, phase, viscosity, texture, colour L\*a\*b\*, browning index, particle size, microstructure, surface/core T), 5 procedural, 3 sensory, 3 safety and 7 chemical. | `ledgers/data/SVAR.jsonl`; `registry/state_variable_registry_v1.csv` | For Q11, promote the FUTURE ids instead of minting parallel ones. |
| V7 | sim_aa_1 and the AA pilot | **Basis:** "reduced AA, no DHA compartment", but the target SVAR-000009 is "Vitamin C, total ascorbic acid" (USDA 401). **CAL papers:** rosehip nectar, orange juice, strawberry nectar, canned fruit in syrup, fig juice, mango blanching, baobab pulp, watermelon juice. **SIM-VAL:** an AA case study, butterfly-pea extract (model), juices plus a model solution, broccoli. **Leaching** is unidentified, so WATER_IMMERSION returns UNKNOWN (pre-reg §6). **Structure:** k_L does not depend on T; product T is either bath-equals-product or a lumped lag (valid only for Bi ≲ 0.1), while Layer 2 uses the slab series. | `sim_aa_1.py` docstring; `aa_kinetics_source_candidates_v1.csv`; `aa_pilot_preregistration_DRAFT.md` §3, §6; `sim_core.TP_MODES` | The validity domain is acidic liquid fruit matrices. The same event is described by two inconsistent thermal models. |
| V8 | sim_chl_1 | It needs `medium_ph`, but the relevant variable is tissue pH, which falls during heating as vacuolar acids are released. One g(pH) is shared by chlorophyll a and b. | `sim_chl_1.py` | pH is UNKNOWN for nearly every recipe event, so coverage is about 0 unless pH is bracketed (Q10, N1). |
| V9 | MECH roster | 32 entries, all `SEED_NOT_YET_AUTHORED`, `ai_drafted=TRUE`. Missing entries: solute uptake and osmotic dehydration; chemical leavening (acid + bicarbonate); anthocyanin, carotenoid and betalain chemistry; pectin-methylesterase/Ca²⁺ firming and β-elimination softening; emulsion and foam formation and breaking; gluten development; sugar crystallisation and candy stages; myoglobin and meat colour; microbial inactivation; water absorption and hydration. Several `open_issue` cells say "reviewer-asserted: no repo source yet". | `registry/mechanism_seed_roster_draft_v1.csv` | Of the packet's own §5.2 example interactions, egg yolk + oil emulsion has no MECH entry at all; baking soda + onion and tomato acid + beans have entries (Maillard, cell-wall softening) but none with the needed pH or Ca²⁺ gate. |
| V10 | `CONTAINS_ACID_MEMBER` at pH ≤ 4.6 | 4.6 is the low-acid / acidified canned-food boundary set by *C. botulinum*, not a chemistry threshold. The uncommitted lot-state lane draft `src/culinarystate/lotstate/ph.py` already implements `ACID_MAX = 4.6` as the generic acid flag (YES / NO / MAYBE on the range). | packet §5.2; FDA LACF context; lane draft | Fine as a LACF safety label. A category error if it gates chlorophyll, pectin or anthocyanin mechanisms. |
| V11 | "thaw as reverse" (process coverage plan) | Thawing is not the mirror image of freezing. Heat must cross the thawed layer, which conducts less than ice-rich frozen tissue, and the usable ΔT is small, so thawing is slower. A Plank-type thaw is acceptable as a first pass only with the thawed-layer conductivity and the real ΔT. The uncommitted lane L-NH draft (`nonheat_drivers.thaw_time_s`, flag `THAW_AS_REVERSE_PLANK`) already does this. | `handoff/PROCESS_COVERAGE_PLAN_2026-11-08.md`; `src/culinarystate/simulation/nonheat_drivers.py` (lane draft) | Keep the flag; never assume thaw time ≈ freeze time; sensible heat is neglected in both directions. |
| V12 | `typical_core_reaches_70` | 69,243 of 69,995 (98.9 %) TYPICAL core-known events reach 70 °C, and many exceed 100 °C (V2). | L2 reports | The statistic carries almost no information; "minutes above 70" mostly tracks duration. |
| V13 | FDA pH source | Lane L-PH built a 488-row draft registry from the April 2007 revision (the Oct 2003 table is identical except one row). The FDA text gives approximate pH of foods "in their normal and natural state" and notes considerable variation between varieties, growing conditions and processing. 17 ranges are open-ended. | `reports/orchestration/S176_L-PH_report.md` §1–3 | An open-ended range makes that side of the pH bound UNKNOWN (N1). |
| V14 | Layer-1 binder | Takes the °C/°F value nearest the verb within the sentence. UK strings such as "200C/180C fan/gas 6" are not resolved into fan versus conventional. HEAT_GENERAL verbs ("cook", "heat") get no medium; they are 1,160 of 2,850 heat events (41 %) in the 1k sample. | `condition_binding.py`; `binding_census_L1_1000_S172.json` | A Layer-1 parse risk for UK (A1) recipes; the h class is wrong for fan settings. |
| V15 | "28-row defaults registry" (Q1, Q2) | `scenario_defaults_v1.csv` has **27** data rows (SD-001…013, SD-020, SD-030…035, SD-040/041, SD-050…053, SD-060); SD-020 packs 9 gas-mark values into one row. All 27 are `SOURCE_UNVERIFIED_AGENT_RECALLED`. | `registry/scenario_defaults_v1.csv` | A trivial count difference, but the verification sheet should list 27 rows plus the 9 gas-mark values. |

---

## B. Answers (Q1–Q19, Q29, Q31, Q32)

"Lean" column: **AGREE**, **PARTLY** or **DISAGREE** with the agent's stated or implied lean; **NO LEAN** where the
packet asks without proposing an answer. Longer derivations are in the notes N1–N6 below the table.

| Q | Recommendation | Lean | Reason | Risk if ignored | How to settle |
|---|---|---|---|---|---|
| **Q1** Layer-2 circularity | Use option (a) for every claim and headline model. Allow Layer 2 only in a pre-registered sensitivity arm "A5-L2" with: per-field basis masks; a **permuted-registry negative control** (SD rows shuffled across processes; the gain must vanish); a registry-perturbation sensitivity (low and high swapped); a process-family-disjoint split; and a comparator of equal capacity (process one-hot + family ordinal). Fix V2 first. | **DISAGREE** with (b) as the default | The USDA R6 and Bognár rows, the bulk of the 17,978 E3 rows, carry no T or t (Step 31 card: USDA T MEASURED on 0 rows, Bognár t on 0; Phenol-Explorer has both on 1,561 rows, mostly storage series). Layer-2 drivers for those rows are therefore a deterministic function of (process id, cut class, registry): a hand-written embedding of the process label with no new information. Any gain comes from the registry's ordering, which makes the registry an untested hyperparameter. On the recipe side, L2 values also encode the process id and corpus statistics (L-02, L-15). | A spurious "physics adds value" result (G31-B) that is really a re-parametrised process label, and results that change whenever someone edits an SD row. The current V2 error correlates with process family, so it would look like signal. | Step 31 arms: A3 vs A5-L1only vs A5-L2 vs A5-L2-permuted vs A3+ordinal, on the cooking stratum, condition-OOD and process-family-disjoint splits, with paired cluster CIs. Pre-register that a gain counts only if A5-L2 beats both A5-L2-permuted and A3+ordinal. |
| **Q2** Sources for defaults | Handbook ranges with page and edition, read by one human and spot-checked by a second on a random 20 %, tiered by quantity type. **Properties:** composition models (Choi–Okos 1986), freezing data from the ASHRAE Refrigeration handbook chapter "Thermal Properties of Foods" (Ch. 19 in the 2018 edition), steam tables. **Process conventions** (simmer, poach, frying T): cooking-science references, marked `CONVENTION`, not measurement; for frying, the EU 2017/2158 acrylamide benchmark advice is a regulatory anchor (SD-008 cites it from recall; the regulation must be opened). **h for pans and frying:** wide ranges marked `LOW_CONFIDENCE`. **Cut half-thickness:** use the distribution of author-stated sizes in the corpus ("1 cm dice", "¼-inch slices"), computed on the training split, not recall. **Starting temperature:** add a frozen start. Rename `source_hint` to `agent_recall_hint` until verified. | **AGREE**, with tiering | A handbook range is enough for a scenario envelope. Primary measurements are needed only where a number enters a claim, and Layer 2 never does. h and cut size have no single authority. Today's hints look like citations ("McGee 2004", "Singh and Heldman"), so they invite misreading (L-01). | Recalled numbers become de facto sources, and one wrong row that a reviewer spots discredits the dataset. | A verification sheet for the 27 rows (the packet says 28; SD-020 packs 9 gas marks into one row), with page, range and verifier; a diff report against current values; a Layer-2 re-run with counts compared. ASHRAE is copyrighted, so cite values with the page and never commit the table. |
| **Q3** Surface vs core | Yes, and it is a correctness fix, not only a browning add-on. Cap every moist zone at T_evap: T_boil(P) in oil and pans, the wet-bulb temperature (≤ T_boil at 1 atm, humidity-dependent) in ovens. Add a surface-regime state (WET → DRYING → CRUST) with a bracketed crust-onset time from a surface energy balance. Maillard, crust and caramelisation gates read the surface zone, never the core. Compute quality doses at the volume-average temperature and safety at the core. Details in N2. | **AGREE** (wider scope) | §141 already says "wet surfaces are evaporation-limited until drying changes the energy balance", and the code does not implement it (V2). The core is the coldest point: the right place for lethality, a lower bound for quality loss. The two-region crust/core moving-boundary model of Farkas, Singh & Rumsey (1996) is the textbook reference for frying; implement only a reduced-order version. | Every dry/fat dose is wrong by ~10². Browning gates fire on the core. One displayed "chicken core 160 °C" loses a food-science audience. | A unit invariant: no moist zone exceeds T_evap + ε while modelled water remains. Compare with textbook frying and roasting core curves, and with recipe-stated internal-temperature endpoints (D-VAL, C-sci 29). |
| **Q4** Geometry | Add Newman product solutions (cube = slab³; finite cylinder = infinite cylinder × slab) and sphere and infinite-cylinder series (N3). Map cut class → shape family + dimension bracket: DICED → cube, SLICED → slab, CHOPPED → bracket from slab to sphere, MINCED/GRATED → particulate. For minced or grated items, the geometry is the formed mass (patty, ball), not the particle. WHOLE → sphere or cylinder by food class, with size from SR portion mass + density (equivalent sphere). If the shape is unknown, the bracket spans slab (slowest) to sphere (fastest) at the same half-dimension. | **AGREE** | The slab is the slowest shape at a given L, so it is conservative for "not yet cooked or safe" claims and anti-conservative for nutrient-loss claims; which bound applies depends on the claim. Example run (boiling, L = 5 mm, 4 min): slab centre 91.4 °C vs cube centre 99.9 °C. Pan contact is one-sided (full thickness, adiabatic top). Large items need item geometry, not the cut history. | Systematic dose bias by cut class, and "roast chicken" handled at dice size. | Unit tests against Heisler/Incropera values and a 1-D/3-D finite-difference check for one case per shape; a sensitivity table of core T against shape. |
| **Q5** Non-heat formulas | **Plank:** acceptable as a first pass with a bias flag. It neglects sensible heat, so it underestimates freezing time; a Pham- or Cleland–Earle-type correction comes later. Foods freeze over a range below 0 °C (initial freezing point from composition; ASHRAE table). **Thaw:** never the mirror of freezing; a Plank-type thaw is acceptable only with the thawed-layer k and the real ΔT (V11; the L-NH draft does this). **Fick slab uptake:** a bound for salt or sugar from a stirred brine (Bi_m → ∞) only. It does not fit dry salting (a surface brine forms, so the boundary condition changes with time), acid marinades (reaction–diffusion: proteins buffer and denature, so the front lags Fick) or osmotic dehydration (counter-current flows; raw vs heat-damaged membranes change D by orders of magnitude). Acid uptake stays QUALITATIVE. **Drying (constant + falling rate):** fine structurally, but needs air T, RH, velocity and a sorption isotherm (GAB), so in recipes it is scenario-only; in ovens, merge it with the Q3 surface model rather than run two models. **F₀ (z = 10 °C, T_ref 121.1 °C):** botulinum spores in low-acid canning only. For cooking safety use authority time–temperature rules at the coldest point (N4). **Mixing:** qualitative flags are fine; add stabiliser presence (yolk lecithin, mustard, proteins). **Add** hydration and absorption (Peleg-type soaking; rice and pasta absorption) and an evaporation/reduction mass balance from stated endpoints. | **DISAGREE** in part (F₀, thaw, marinades); AGREE on Plank and drying as first passes | Each listed formula is textbook-correct only inside its own assumptions, and the plan applies three of them outside those assumptions. D values for salt or acid in meat and vegetables must come from primary diffusion studies scoped by matrix and T; Rahman's handbook can locate them but carries no authority of its own. | A botulinum F₀ attached to roast chicken; claims that the marinade reaches the core; thawing times that are too short. | Per family, compare against 2–3 primary datasets (salt uptake curves in pork and fish, freezing-time data). For safety, unit tests that reproduce the authority tables. Document each validity domain. |
| **Q6** Equipment and altitude | Model nothing new before 25 Nov, but add the assumption flags now: `PRESSURE_ASSUMED_1ATM` on every PHYSICAL_DEFINITION 100 °C; `OVEN_SETPOINT_NOT_PRODUCT_T`; `FAN_VS_CONVENTIONAL_UNRESOLVED` (V14). Fold oven deviation and cycling into the Layer-2 bath bracket rather than adding a variable. Altitude: boiling point from steam tables when a user supplies it (H4 or interactive ASK), never for corpus recipes. The pressure-cooker T comes from gauge pressure (steam tables). Microwave and radiant heating stay UNSUPPORTED, stated as a limitation. | **NO LEAN** | The author's altitude and oven are unknowable for the corpus, so flags are honest and models would be imputation. A fan oven differs from a conventional one in both setpoint and h. | Silent 1-atm and setpoint-equals-product assumptions surfacing in answers; UK recipes misread. | Counts of flagged events; a parse test on "200C/180C fan/gas 6" strings (on the Mac for A1). |
| **Q7** ING → USDA match | Verify by impact, not frequency alone: priority = recipe mass share × spread of the key fields among plausible SR candidates × whether the field gates a mechanism (salt, sugar, fat, water, acid). Carry ambiguity as a **composition hull** (an INTERVAL over the top-k candidates) instead of choosing top-1, so AI-matched rows can feed MODEL_DERIVED intervals honestly. Match the state (raw / cooked / canned / drained / dried) and edible portion vs as-purchased (refuse %). Estimate accuracy per score band on a dual-labelled stratified sample of ≈ 200 ING (Wilson CI); only bands whose lower bound clears a pre-registered threshold feed composition without per-item checks. High-risk items: salt kinds, salted/unsalted butter, flour kinds, milk/cream fat, "oil", stock/broth (sodium), cheese, sugar kinds, chocolate. | **PARTLY** | An 80 % frequency cover leaves the dangerous errors in place: one wrong top-1 for "salt" or "stock" propagates to hundreds of thousands of lots through the solute load, a_w and pH gates. | Systematic composition errors that look precise. | The per-band accuracy table, hull-width distribution, and the sensitivity of downstream flags to the match (top-1 vs hull). |
| **Q8** Food.com has no units | (a) presence-only composition. Do not impute units (c). If anything, compute a **unit-ambiguity hull**: the mass interval over the units plausible for that ingredient. Solute load, a_w and the mass-weighted pH bound are UNKNOWN for Food.com. Pursue (b) only through a source with clear terms; scraping food.com is a new acquisition with unclear terms. Gutenberg needs a historical-unit registry (teacupful, gill). | **AGREE** | The quantities that matter are ratios (salt per water, sugar per water, fat fraction), and teaspoon vs cup is a factor of 48. An imputation error dominates every ratio, and a learned unit model silently becomes a composition source. | Imputed "composition" leaks into mechanism gates for 85 % of the corpus. | Remove the units from Wikibooks/TASTESET lines, check that the hull contains the true mass (100 % by construction), and report hull widths to decide whether it is useful. |
| **Q9** Volume/count → grams | Accept SR portion weights as a new basis `SR_PORTION` through an explicit decision record (rc2 is a frozen rule, so do not relax it silently). Grams are always INTERVALs spanning the plausible portion records (chopped/sliced/whole; small/medium/large; packed or not), never POINT. Keep the phrase → portion link `AI_MATCHED` until verified. Record refuse and edible-portion semantics separately. Liquid densities are physical constants. | **AGREE**, via a decision record | SR portions are published reference measurements (some calculated), so they are acceptable as reference data; the weak point is the AI link and the false precision. | Precise-looking grams; edible vs as-purchased mismatch; a frozen rule broken quietly. | Compare SR-portion grams with lines that state both volume and mass (counts only; BBC on the Mac). |
| **Q10** Mixture pH | Emit a **pH INTERVAL** for the lot's aqueous phase: [min of member low bounds, max of member high bounds]. Under ideal closed-system acid–base mixing this is provable without buffer data (N1). The corollary gives directions: adding a member whose pH is below the lot's cannot raise the lot pH. Add violation flags (CO₂ loss, acid-producing reactions, precipitation, temperature, tissue acid release, non-equilibrated solids). Include **water as a member** (tap-water pH, alkalinity and hardness UNKNOWN unless asked). Gate with Kleene logic: TRUE / FALSE only when the interval lies on one side of the threshold. Do not use 4.6 as a chemistry flag (V10): each mechanism needs its own window, and MODULATING axes (chlorophyll) never gate possibility. Titratable acidity and buffer models wait until after the paper's first round. | **DISAGREE** (flags are weaker than what can be proven) | `CONTAINS_ACID_MEMBER` does not imply an acidic mixture: lemon juice in a large pot of water and vegetables can end anywhere in the members' range. The bound is the strongest statement available without buffer data, and it is honest when wide. Tissue pH drops during cooking, so "no acid member" does not mean "no pheophytinisation". The FDA values are approximate ranges for foods in their "normal and natural state" (V13). | Flags misused as gates; 4.6 misused; water and heating effects ignored; chlorophyll coverage stuck at 0. | Unit tests of the bound and its monotonicity. A one-hour bench check with a calibrated pH meter on 5–10 kitchen mixtures (lemon + water + vegetables, tomato sauce, baking soda in water before and after boiling). Literature values for sauces with known pH. |
| **Q11** Missing state variables | Additive SVAR v1.1 (H4, owner 16a per CHG-16-7). **Promote** the 30 FUTURE ids (V6) where they fit (moisture FUT-001, a_w FUT-002, phase FUT-005, colour FUT-008, browning index FUT-009, surface/core T FUT-012, cut FUT-024, mixture identity FUT-026, cooked/raw FUT-027, pathogen-control FUT-028, allergen FUT-029) and **add** history variables: `cell_integrity`, `time_since_disruption`, `enzyme_state[family]`, `thermal_history` (per zone: T_max, Ω at registered (T_ref, z), minutes above registered thresholds), `surface_regime`, `contact_log`, `liquid_fate`, `freeze_history`, `starch_state`, `protein_state`, `gluten_development`, `dispersion_state`, `oxygen_exposure`, `salt_in_water`, `sugar_in_water`, `pH_interval`. Definitions, units, types and owners are in §E.4 and §E.6. | **NO LEAN** (my set: §E.6) | Without history variables, cut → rest → heat, cold vs hot start, rinse after salting and drained vs consumed liquid cannot be represented, and those are where the food science lives. | Parallel naming; history baked into ad-hoc flags; Step 21/22 gates stay NOT_EVALUABLE_YET. | H4 review of §E.6; one fixture recipe per variable (garlic crush/rest/heat; salt/rinse aubergine; drained vs soup vegetables). |
| **Q12** Interaction definition | Mechanism-mediated edges alone are **not sufficient**. Add physical edge kinds, all deterministic: **THERMAL** (an enthalpy balance on merge: a cold or frozen addition lowers the bath T, which then recovers; needs the water-to-food ratio); **MEDIUM** (one member's liquid or fat is another's heat or mass-transfer medium: tomato juice for braising, rendered fat for frying); **TRANSPORT** (salt, sugar or acid moving from i to j; leaching from j into the liquid); **PARTITION** (carotenoids, lipophilic aroma and fat-soluble vitamins into the lipid phase; volatiles into headspace); **CONDITION_SUPPLIER** (i changes the aqueous pH, solute load or a_w seen by j); plus the existing **REACTANT_PAIR**. Every edge carries a contact interval and a phase. **Validate** with: (i) a curated set of 20–40 two-arm literature contrasts (with/without salt, acid, baking soda, sugar, Ca²⁺) as positive and negative controls; (ii) blinded expert review of sampled edges (precision) and expert-written expected interactions for sampled recipes (recall); (iii) negative controls (shuffle members across recipes; shuffle processes); (iv) a structural rule: no edge unless both supplier roles are present. Never co-occurrence or learned weights (§213.12). | **DISAGREE** with mechanism-only | Most real "ingredient affects ingredient" effects in cooking are physical: heat sinks, media, diffusion, partitioning. Leaving them out makes the edge set chemistry-flavoured but physically incomplete. | Missed first-order effects, for example a large cold addition stopping the boil, which is exactly where the water-ratio UNKNOWN matters. | The contrast set, expert review and negative controls above, reported as precision and recall with Wilson CIs. |
| **Q13** Mixture factorisation | Both, but **phase-resolved**: a lot is {aqueous continuous phase (water + dissolved solutes), lipid phase, solid-piece classes (each with its own geometry and thermal history), gas (foam), structured phase (dough, gel)}. Each mixture property lives on the phase where it is physically defined: pH, a_w and solute load on the aqueous phase; heat transfer on the pieces; partition between phases. The merged bulk composition is only for nutrition totals. Members are allocated to phases deterministically from SR composition (milk = aqueous + lipid emulsion; butter ≈ fat + water). | **AGREE** (with phases) | A stew's pH is a property of its liquid, not of the carrot pieces until they equilibrate; heat conduction is a property of the pieces. A single merged composition mixes these up. | Wrong physical meaning for solute load and pH; a_w computed over fat. | Fixture recipes (vinaigrette, stew, batter) checked by hand; invariant: phase masses sum to the lot mass. |
| **Q14** Order effects | Yes: record a **contact log** in the lot state. For each (solute or agent source, receiving member): start event, end event (or the discard/rinse that ends it), duration interval (L1/L2), T during contact, phase (dry surface vs brine). Uptake fraction = an interval from `slab_uptake_fraction` with a scenario D interval, QUALITATIVE claims only. Discard and rinse events reset external solute. The same log carries enzyme timing (cut → rest → heat). | **AGREE** | Solute uptake depends on contact time and L²/D, not on whether both items are in the same lot. Recipe order is known; contact durations mostly come from L1/L2. | "Salt then rinse" and "salt at the end" look identical in the state. | Non-commutativity unit tests (§212.38): those two sequences must give different logs and flags. |
| **Q15** Mechanism windows | Numeric windows only from primary sources scoped by matrix and **water content**: DSC for gelatinisation and protein denaturation; inactivation kinetics (D/z or k/Ea) for enzymes in that matrix; PME and pectin studies. Handbooks only when they cite primary measurements for the same matrix; reviews are context. Separate **phase transitions** (onset ranges that shift with water content; starch needs available water) from **reactions**, which have no switch and continuous Arrhenius rates. Store reaction windows as timescale-scoped dose criteria ("rate-relevant within culinary times"), not temperature switches. While all 32 entries are unreviewed, the screen is useful for engineering diagnostics (coverage, missing-input census, recall on the sealed case set) and must not feed routes, QUALITATIVE outputs or headline numbers (G21.6 and the Step 21 fail action). | **AGREE**, with refinements | §144.1: no universal switch. A temperature window for a reaction is a category error unless a timescale is attached. | AI-drafted windows reach answers (L-08); "Maillard impossible below X °C" style mistakes. | G21.6 dual blind review; Step 22 sealed case-set recall; an external expert spot-check (C-sci 11). |
| **Q16** One calibrated system; chlorophyll second? | One system is enough to show the SIMULATE **pathway** end to end (verified PARAM → frozen fit → held-out check → domain-gated route). It is not enough to claim SIMULATE works for recipes. Gate the domain on **matrix class** (liquid, acidic fruit), pH range, T 60–100 °C and NO_WATER_CONTACT, not on T alone. In the talk, show SIMULATE on that narrow domain (heated juices, compotes, fruit sauces) and say why vegetables in water stay UNKNOWN (leaching unidentified). Match the basis: SIM-VAL comparisons need the paper's analyte basis (AA vs AA + DHA); total-vitamin-C EVD rows are basis-mismatched for a reduced-AA model. Second system, for the paper only: **finish sim_aa_1's leaching branch** (k_L, K_p from boiling studies that assay the water, with k_L ∝ D/L² scaling by size) before chlorophyll. Chlorophyll later needs kinetics measured in vegetables and an interval of g(pH) over the N1 bound. | **DISAGREE** on order (leaching before chlorophyll); **AGREE** that one system suffices as a pathway demo | V7: acidic, liquid, often low-O₂ CAL matrices against solid vegetables at pH ~5–7 in air and water. Leaching is widely reported as the dominant vitamin-C loss route when vegetables are boiled (reviewer recall; check against the boiling papers), and SSOT §144.2 already insists on separating leaching from destruction. Chlorophyll coverage is ≈ 0 while pH is UNKNOWN (V8). | A SIMULATE number for boiled broccoli from a juice fit; a basis-mismatch error read as model error. | The Step 27 pre-registered SIM-VAL; a domain census (events inside the gate); for leaching, a CAL set of ≥ 3 boiling papers that assay the water. |
| **Q17** Evidence quality for the talk | Minimum: (i) the dual-verified CAL rows (16 now, target ≈ 20) as the only verified kinetic evidence; (ii) the 17,978 E3 rows presented as **unverified reference-table values**, with a random human transcription audit of 50–100 rows against the source tables (error rate with Wilson CI); (iii) say plainly that USDA R6 values are partly calculated or imputed (nearest 5 %, imputed from similar foods, TR/AR undisclosed; SVAR registry notes); (iv) report D1's hand-verified literature rows as 0 if still 0. | **NO LEAN** | A transcription audit costs about an hour and turns "unverified" into a measured error rate. Calling R6 values measurements would be wrong. | Overclaiming D1; reviewers treating R6 as measured. | The audit itself. |
| **Q18** Censoring at 0.975 | Stratifying by the cap is **not enough**. (i) R6 values are rounded to the nearest 5 %, so treat them as interval-censored (±0.025). (ii) Use a censored likelihood (SSOT §211.8; Tobit-type right-censoring at the cap) or at least report fits with and without capped rows plus a cap sensitivity (0.95 / 0.975 / 1.0). (iii) A cap is meaningful for TR only: AR on a fresh-weight basis exceeds 1 when water is lost (and, for some compounds, through better extractability), and R6 does not say which it is (RT-004). (iv) Report errors on uncapped rows separately. | **DISAGREE** ("stratify" is not enough) | Capping censors information in a way that depends on the retention type, and the type is undisclosed. | Biased low-loss estimates; spurious agreement near the cap. | A cap-sensitivity table and a censored vs naive fit comparison in 29-diag. |
| **Q19** Prior exposure | Diagnostics only from rows already read (DEL-2, S160). An H2 claim needs a confirmatory set nobody has read: Step 11–14 verified rows, or a pre-registered untouched subset. Add an **imputation-duplicate control** before any H2 diagnostic: R6 "many values imputed from similar foods" implies identical retention values across foods within (process, nutrient). A process-only model reproduces those copies, which inflates "process beats identity". Cluster identical (process, nutrient, value) groups into one fold, or drop them, and report the duplicate share (N6). DEL-2's "D7a matched D1 to four decimals" may be this effect. | **AGREE** + control | Copied targets are the classic shortcut for this hypothesis, and they favour H2. | A false H2 signal from database construction. | The duplicate census on EVD (counts only) and 29-diag re-run with duplicate clusters as groups. |
| **Q29** What is "the state representation"? | Rung 0 = the explicit lot-step state (§E), but Step 35 reads a **firewalled export view** (§E.7), never the raw state. **Non-circular targets:** (1) Step 19 human gold state labels (for D3); (2) **text-observed endpoints masked from the input** ("until golden / tender / reduced by half / internal temperature X"), weak but independent labels for surface regime, softening, evaporation and core T; (3) EVD measured outcomes, but those belong to Steps 29–33 because EVD rows are not recipe lot-steps; (4) held-out steps and completion, valid only if the state is **recomputed after masking** and target-event L2 fields are removed. **Never** a target: L1/L2 fields predicted from their own inputs, MECH-screen outputs, or co-occurrence. Free physics validation set: recipes that state oven T, time, size and the target internal temperature (D-VAL). | **AGREE** + firewall | §208.2 E ≠ T and §199.8: endpoint phrases are outcomes. In masked completion, the lot state's composition, pH bound and edges contain the masked member unless recomputed, which is direct leakage. L2 fields are functions of the process id, which leaks when the target is the next process. | Leaky Step 35 headline numbers; a representation that "learns" the registry. | A property test: for every task τ, no exported field's dependency closure intersects the banned set B(τ) (§E.7). |
| **Q31** Cheaper 35f | Mechanism-screen-profile similarity is cheaper and can be non-circular, but it is a **different notion**: "mechanism-opportunity" similarity (which mechanisms *could* act), not process-response (how the food *does* change). Register it as a separate typed notion with its own null (shuffle members within recipes, keeping the process; a degree-preserving null). It must beat ingredient-category × process-family incidence, because the screen is largely a deterministic function of those. While the 32 MECH entries are unreviewed it is DESCRIPTIVE only. | **DISAGREE** (not a 35f version) | 35f's meaning is measured Δ-profiles; renaming a feasibility screen as a response would mislabel a claim. | A "process-response" claim with no response data behind it. | Its own separation test (§35e) and the incidence baseline. |
| **Q32** Generic behaviour | Registry facts (reviewed, evidence-backed MECH entries with driver-window-scoped directions) are **test oracles**. Learned models get pre-registered metamorphic consistency tests, never training labels: at equal dose, boiling ≤ steaming for vitamin-C retention; adding an acid member lowers predicted chlorophyll retention; monotone dose response inside the evidence domain. A model's consistency is not evidence for the fact. | **AGREE** | Training on the facts would be circular. Testing against them is §215.22 "mechanistic consistency". | Circular "learning" of the registry. | A consistency test suite pre-registered in Step 33, reporting violation rates. |

### Notes

**N1. Mixture-pH bound (Q10): statement, proof sketch, use.**
For member *i* (an ideal dilute aqueous acid–base system), let *h_i*(pH) = *V_i*([H⁺] − [OH⁻]) + Σ_s z_s·n_s(pH): the
net charge of member *i*'s own species plus its share of H⁺ and OH⁻. For ideal solutions each species' charge fraction
depends only on pH, so *h_i* strictly decreases with pH, and *h_i*(pH_i) = 0 (member *i*'s own charge balance). After
ideal mixing, the charge balance is Σ_i *h_i*(pH_mix) = 0. Below min pH_i every *h_i* > 0, and above max pH_i every
*h_i* < 0, so **min_i pH_i ≤ pH_mix ≤ max_i pH_i**. **Corollary (direction):** adding a member with pH below the
current lot pH cannot raise it.

Each assumption becomes a violation flag, and a raised flag widens the bound or makes it UNKNOWN:
- **Closed system.** CO₂ loss breaks it: acid + bicarbonate; bicarbonate heated to carbonate can *raise* pH above the highest
  member pH; boiling drives CO₂ off.
- **No proton-producing or proton-consuming reaction within the step:** fermentation, Maillard acid formation,
  hydrolysis, protein unfolding.
- **No precipitation or complexation:** Ca²⁺ + phosphate in dairy; metal–pigment complexes.
- **Constant temperature:** pKa depends on T, and the FDA values were taken at ambient temperature.
- **Small activity effects.**
- **Solids equilibrated with the liquid:** see the contact log. Tissue pH ≠ liquid pH until then.
- **Member range valid for the member's state:** FDA "normal and natural state", raw vs cooked.

How to apply it:
- **Interval form:** [min_i lo_i, max_i hi_i]. An open-ended or missing member range makes that side UNKNOWN (V13).
- **Water** is a member.
- **Kleene gating:** a NECESSARY gate "pH ≤ x" is TRUE if hi ≤ x, FALSE if lo > x, otherwise UNKNOWN.

**N2. Evaporative boundary (Q3), the minimal fix.**
While a surface is wet, T_surface ≤ T_evap. T_evap is T_boil(P) (100 °C at 1 atm) in oil and pans. In ovens it is the
wet-bulb temperature, which depends on the oven humidity and cannot exceed T_boil at 1 atm. The moist core cannot
exceed T_evap.
1. **Upper bound on core heating during the wet period:** core trajectory with boundary T_b,eff = min(T_medium,
   T_evap,hi).
2. **Flux-limited lower bound:** heat flux h(T_medium − T_s), with T_s = T_wb,lo from a Layer-2 humidity bracket.
3. **Surface regime:** an enum IMMERSED_WET / WET_EVAPORATION_LIMITED / DRYING / CRUST. The crust-onset bracket comes
   from a surface-layer energy balance (the latent heat of the surface water against the net flux). Outputs are
   QUALITATIVE.
4. **Surface dose in oil and pans:** at T_evap until crust onset, then rising toward T_medium. Also QUALITATIVE.
5. **Later reference** for a reduced-order crust/core moving-boundary model: Farkas, Singh & Rumsey (1996), *J. Food
   Eng.* 29(2):211–226 and 227–248.

My illustration (diced, TYPICAL, boundary capped at 100 °C, same h): bake 30 min, core 91.9 °C and cook value 6.3 (now
163.7 °C and 601.9); deep-fry 5 min, core 94.0 °C and 1.2 (now 163.4 °C and 101.7). The cap is a bound, not a validated
model.

**N3. Shapes (Q4).** These are standard mathematical results (Heisler/Incropera) and need no sourcing. For constant
properties:
- Cube of side 2L: θ = θ_slab(L)³.
- Finite cylinder (radius R, half-length L): θ = θ_cyl(R)·θ_slab(L).
- Sphere centre: θ = Σ C_n exp(−ζ_n² Fo), with C_n = 4(sin ζ_n − ζ_n cos ζ_n)/(2ζ_n − sin 2ζ_n) and
  1 − ζ_n cot ζ_n = Bi.
- Infinite cylinder: ζ_n J₁(ζ_n)/J₀(ζ_n) = Bi, with C_n = (2/ζ_n)·J₁(ζ_n)/(J₀²(ζ_n) + J₁²(ζ_n)).

A lumped lag (sim_core `LUMPED_LAG`) is valid only for Bi ≲ 0.1. With the registry's own h and L ranges, boiled or fried pieces have Bi ≈ 0.6–36, so one
thermal model (the series solution, zone-resolved) should feed both Layer 2 and the kinetic simulators (V7).

**N4. Food-safety references (Q5, C-sci 3).**
- **F₀** (T_ref 121.1 °C, z = 10 °C) is the botulinum-spore reference for low-acid canning. It is relevant only to
  pressure canning and retorts.
- **Cooking safety** for vegetative pathogens is set by authority-specific time–temperature rules at the coldest point.
  Examples: the UK equivalents 60 °C/45 min, 65 °C/10 min, 70 °C/2 min, 75 °C/30 s and 80 °C/6 s (seen only on
  secondary copies; a Quebec MAPAQ table gives the 6-log *L. monocytogenes* basis; by my arithmetic they imply
  z ≈ 7.4–7.7 °C); the USDA-FSIS lethality tables for meat and poultry; the FDA Food Code minimum internal temperatures.
- **Output** only "consistent / not consistent with <rule> under <layer/bracket>" (SVAR-FUT-028), never "safe". A human
  must open the primary documents before any use.

**N5. DIRECT context (V5): 1,000-recipe non-BBC sample.** Seed `20261104`; Food.com 861, Gutenberg 135, Wikibooks 4
recipes; unchanged `router_demo.route_text`. Items: 451 DIRECT, 57,107 UNKNOWN.

| DIRECT for vitamin C (SVAR-000009) | n | % |
|---|---|---|
| Groups whose standard SR Legacy item has ≈ 0 mg vitamin C/100 g (egg, cheese, beef, milk, pasta, chicken/turkey/lamb, pork, nuts, ham, sausage) | 364 | 80.7 |
| of which egg × bake | 111 | 24.6 |
| Potato, tomato, fruit, sweet potato, seafood | 87 | 19.3 |
| DIRECT reached through a multi-ingredient (merged) lot | 372 | 82.5 |
| DIRECT on a single-ingredient lot | 79 | 17.5 |
| By process: bake 209, boil 46, grill 37, simmer 37, cook 26, fry 21, brown 20, heat 16, … | | |

SR Legacy vitamin C (nutrient 401) for reference items, read from `data/raw/fdc/sr_legacy/.../food_nutrient.csv`:

| SR Legacy item | fdc_id | mg/100 g |
|---|---|---|
| Egg, whole, raw, fresh | 171287 | 0 |
| Milk, whole, 3.25 % | 171265 | 0 |
| Beef, ground 80/20, raw | 174036 | 0 |
| Pasta, dry, enriched | 169736 | 0 |
| Almonds | 170567 | 0 |
| Walnuts | 170187 | 1.3 |
| Potatoes, flesh and skin, raw | 170026 | 19.7 |
| Cheeses (blue, brie, edam; top-3 crosswalk candidates) | — | 0 |

The classification is at group level. Exceptions exist (chestnuts, giblets and cured meats with added ascorbate
contain vitamin C), which is one more reason for a member-level presence gate rather than a group rule.

Side finding for Q7: the crosswalk's top-ranked candidate for the ING "milk" is "Milk, human, mature, fluid". This is
exactly the kind of high-impact match error that frequency-only verification misses.

Fix: (i) a **target-presence gate**: when the member's reference content of the target is ≈ 0 or below the LOQ, route
TARGET_ABSENT, not DIRECT; (ii) a **context gate**: food form, alone vs in a mixture, leaf-level process, and condition
overlap; otherwise CONTEXT_MISMATCH or an INTERPOLATE candidate. Re-run the census with both gates and report the old
and new DIRECT counts side by side. The current figure stays on the record (R-20).

**N6. R6 imputation duplicates (Q19).** The SVAR registry notes for R6 say "%TR vs %AR not disclosed at row level;
nearest 5%; many values imputed from similar foods". Identical values across foods within (process, nutrient) are
probably copies. A process-only model reproduces copies, so ingredient-disjoint and pair-holdout splits look better
than they are. Control: group by (process, nutrient, value) and keep each group within one fold, or deduplicate; report
the duplicate share. Use interval censoring at ±0.025 for nearest-5 % values.

---

## C. Missing physics and chemistry (C-sci), mapped to the 36-step plan

Priority codes: **CRIT** = fix before any slide or feature uses the affected output; **H / M / L** = value for the
25 Nov talk / the later paper.

### C.1 Verdicts on packet §9 items 1–11

| # | Item (packet §9) | Verdict | What a food scientist expects; what to do | Plan step(s) | Talk / paper |
|---|---|---|---|---|---|
| 1 | Mass balance and cooking yield | **AGREE, essential** | Lot mass with explicit sinks: evaporation, drip, fat drip, leaching into the liquid, discard (§212.31). Use SR `retention_factor.csv` (on the server) and the USDA cooking-yield tables for meat and poultry (public domain) as reference rows. Without yields, TR cannot become a dish-level amount and AR > 1 cannot be interpreted. | 12 (data), 18 (operator), 23 (TR/AR consistency), 31 | M / H |
| 2 | Surface / drying front | **AGREE, upgraded to a correctness fix** (V2, N2) | Evaporative cap plus the surface-regime state; browning gates read the surface zone. | 26 (thermal model shared with the sims), 31 | **CRIT** / H |
| 3 | Food-safety layer | **AGREE, with scope limits** | Consistency with an authority's time–temperature rule at the coldest point; never "safe". F₀ is for canning only (N4). Opening the primary documents and signing off is a human gate (expert). | 23 (G9 safety input), 31, 36 | Say "not evaluated" / M |
| 4 | Allergen propagation | **AGREE, cheap and deterministic** | The ALLERGEN ledger's lineage union, as "contains via ingredient"; cross-contact UNKNOWN. | 18, 36 | M / L |
| 5 | Uncertainty propagation | **AGREE; use two tracks** | (a) Interval arithmetic for hard bounds: composition and unit hulls, the pH bound. (b) Monte Carlo over Layer-2 factor ranges with *independent* sampling, plus shared factors across steps (same oven, same pot), for scenario spreads; this replaces corner brackets (V3). Never merge an L1 and an L2 number in one interval. | 34 (+ 31) | L / H |
| 6 | Salt and acid uptake | **AGREE, within limits** (Q5) | Salt or sugar from a brine: Fick bound. Acid: reaction–diffusion, QUALITATIVE. Dry salting: osmotic exudate. Add MECH entries `SOLUTE_UPTAKE` and `OSMOTIC_DEHYDRATION`. | 21, 31 | L / M |
| 7 | Enzyme history | **AGREE, high value** | Deterministic operators: `cell_integrity`, `time_since_disruption`, and `enzyme_state` from thermal history and matrix-scoped inactivation windows (alliinase in a garlic rest, myrosinase, PPO, ascorbate oxidase in cold vs hot start). | 16a, 18, 21 (`ENZYME_THERMAL_INACTIVATION`) | M (the garlic crush/rest/heat example makes a strong slide) / H |
| 8 | Oil uptake and fat exchange | **AGREE, mechanism note** | Uptake is concentrated in the crust and, as I recall the frying literature (verify), much of it happens while the food cools after removal. It therefore couples to the Q3 crust state and to moisture loss. Fat also moves the other way (meat fat renders into the oil). Use SR fried-food composition as a reference. | 21 (`OIL_UPTAKE`), 12, 31 | L / M |
| 9 | Sensory fields left UNKNOWN | **AGREE** | SVAR-FUT-020…022 exist. Keep them UNKNOWN; no proxies. | 03 / 16a | — |
| 10 | Physical and history SVARs | **AGREE**; promote the FUTURE ids (V6) | List in §E.6. | 16a (owner), 03 | L / H |
| 11 | External validation | **AGREE, strongly; schedule now** | One external food scientist for (a) the physics corrections (V2, N1–N4), (b) 20–30 MECH windows, (c) 20–30 benchmark answers. Record as a human gate. | 21, 22c, 36 (REV-B covers Q25) | H / H |

### C.2 New items 12–40

| # | Missing item | Why it matters | Concrete action | Plan step(s) | Talk / paper |
|---|---|---|---|---|---|
| 12 | **Evaporative cap and surface regime** (bug, V2) | Moist cores cannot exceed T_evap; dry/fat doses are about 10² too high. | N2; unit invariant; re-run L2 for DRY/FAT. Mark the current `scenario_L2_*` DRY/FAT core fields SUPERSEDED, without deleting them. | 26, 31 | **CRIT** / H |
| 13 | Where the kinetic temperature is taken | Quality kinetics need the volume-average (or profile-integrated) temperature, safety needs the core. Layer 2 and sim_aa_1 use different thermal models (V7). | One zone-resolved series model feeds both; allow `LUMPED_LAG` only when Bi ≲ 0.1. | 26, 31 | M / H |
| 14 | Composition-dependent thermophysical properties | One `FOOD_HIGH_MOISTURE` class is applied to oil, syrups, doughs and frozen foods. | Choi–Okos k, ρ, c_p, α as intervals over the composition hull; frozen state with ice fraction; the `choi_okos.py` structure exists. | 31 (+ 12, 24b PROPERTY_MODEL) | L / H |
| 15 | Thermal mixing on merges | Adding a cold or frozen mass drops the bath temperature, and the boil recovers later; this is where the water-to-food ratio matters. | An enthalpy balance (Σ m·c_p·T, plus latent heat for frozen additions) when masses are known; recovery time UNKNOWN (heat input unknown). | 18, 31 | L / M |
| 16 | Phase-resolved lots | pH, a_w and solute load are aqueous-phase properties; conduction belongs to the pieces (Q13). | §E.4, group C. | 16, 18 | M / H |
| 17 | Water as a member | Tap-water pH and alkalinity (chlorophyll) and hardness (Ca²⁺ firms pectin, slows legume softening); salted water. | WATER member with UNKNOWN or ASK properties; it enters the pH bound (N1). | 07 / 16, 21 | L / M |
| 18 | Liquid fate and dish-level retention semantics | Leached vitamin C stays in a soup that is eaten but is lost when the liquid is drained. USDA TR refers to the drained food. | `liquid_fate`; the route checks it against the EVD row's retention definition. | 23, 36 | M (explains UNKNOWN) / H |
| 19 | **Target-presence gate** | 80.7 % of vitamin-C DIRECT routes in the sample are for foods with ≈ 0 content (N5). | Route TARGET_ABSENT when the reference content is ≈ 0 or below the LOQ. | 23 (G0/G1), 12 | **H** / H |
| 20 | **DIRECT context gate** | 82.5 % of DIRECT reach the ingredient through a merged lot (N5). Retention measured on the food cooked alone does not transfer to a minor ingredient of a batter. | Check food form, alone vs mixture, leaf process and condition overlap; otherwise CONTEXT_MISMATCH or an INTERPOLATE candidate. | 23, 25 | **H** / H |
| 21 | Hydration, absorption and reduction mass balance | Rice, pasta and legumes take up water; sauces reduce. Both dominate the yield. | Peleg-type soaking as a scenario; "reduce by half" as a TEXT_OBSERVED mass change; MECH `WATER_ABSORPTION`. | 18, 31, 21 | L / M |
| 22 | Acid–base reactions and chemical leavening | Bicarbonate + acid → CO₂; bicarbonate decomposing on heating raises pH. Alkalinity speeds browning, as in the packet's own "baking soda + onion". | MECH entries; pH-bound violation flags (N1). | 21 | L / M |
| 23 | Pigments beyond chlorophyll | Anthocyanin colour depends on pH (red cabbage); betalains respond to heat and pH; carotenoids isomerise and oxidise, and fat raises their *bioaccessibility*, which is not their *content*. | MECH entries with target-basis notes. | 21 | L / M |
| 24 | Pectin and cell-wall chemistry | PME activation at moderate temperatures plus Ca²⁺ cross-links firm tissue (low-temperature pre-cooking). β-elimination softens tissue at neutral or alkaline pH (baking soda + beans). Acid slows softening (tomato + beans). | Split `CELL_WALL_SOFTENING` into PME/Ca firming, β-elimination softening and acid stability. | 21 | L / H (needed for the packet's own examples) |
| 25 | Colloids and structure | Emulsions need an emulsifier plus energy and break under heat, acid or excess oil. Foams: protein-stabilised, inhibited by fat, stabilised by sugar. Gluten needs water plus work; salt strengthens it, fat and sugar weaken it. Sugar syrups: the boiling point indicates concentration (boiling-point elevation; candy stages). Fat melts and crystallises (tempering). | MECH entries; history states in §E.6. | 21, 16a | L / M |
| 26 | Meat-specific chemistry | Myoglobin states and doneness colour; cook loss against core T; brining raises water-holding through salt-solubilised myofibrillar proteins. | MECH entries; USDA yields. | 21, 12 | L / M |
| 27 | Oxygen and metal axes | Ascorbic-acid and lipid oxidation depend on O₂ (lid, stirring, deaerated boiling water) and are catalysed by Cu/Fe. | QUALITATIVE axes, mostly UNKNOWN or ASK. | 07 / 16, 21 | L / M |
| 28 | Endpoint cues as state | §199.8 bans them as inputs, but they are valid **observations** of state and valid validation labels (Q29). | Basis `TEXT_OBSERVED_ENDPOINT` behind the firewall (§E.7). | 16, 17, 22, 35 | M / H |
| 29 | **Physics validation against author-stated endpoints (D-VAL)** | The only non-circular check of the drivers that exists today. | Recipes stating oven T, time, size and target internal T: does the stated endpoint fall inside the predicted core-T bracket at the stated time? Report coverage. | New substep under 26/27 (or 31.0) | **H** / H |
| 30 | Basis harmonisation for vitamin C | SR Legacy carries separate nutrients: total AA (401), reduced AA (402), dehydro-AA (403). Fresh vs dry weight; TR vs AR. | A basis check at G0/G8 and in SIM-VAL. | 05, 10, 27 | H / H |
| 31 | Imputed or duplicated reference values | Shortcut that favours H2 (N6). | Duplicate census and group splits. | 05, 15, 29 | L / H |
| 32 | UK oven strings and qualitative heat | Fan vs conventional; gas marks; "medium heat" mappings are hypotheses (§199.7). | Parser rules; `FAN_VS_CONVENTIONAL_UNRESOLVED`. | 07, 17 | L / L |
| 33 | Freezing physics | Freezing-point depression, ice fraction, drip loss, slower thawing (V11). | ASHRAE initial-freezing-point data (cite the page, do not commit the table); `FROZEN_THAWED` cell integrity. | 31 (non-heat family 1) | L / M |
| 34 | Scope of water activity | Norrish suits sugar syrups; NaCl needs an electrolyte-specific model; Ross's product rule for mixtures (tested on intermediate-moisture foods by Chirife) holds only in that range. Low-moisture foods need sorption isotherms (GAB). Most fresh foods have a_w close to 1, which carries little information. | Compute a_w only when the solute load is high (cures, candied fruit, jams, brines, doughs), with saturation caps; elsewhere report "high, not informative". | 31, 16a | L / M |
| 35 | Corpus-statistic defaults leak into evaluation | KGE quantiles and IDF are computed on all recipes, including test recipes. | Recompute on the training split for every Step 35 / H1 evaluation. | 15, 35 | M / H |
| 36 | Microwave and radiant heating | UNSUPPORTED (142 of 2,850 heat events, 5 %, in the 1k sample). | State it as a limitation. | 31 (later) | L / L |
| 37 | Carry-over cooking and resting | Needs the end-of-heating spatial profile (surface hotter than core); the core alone cannot give it. | The zone model (item 13). | 31 (resting family) | — / L |
| 38 | Frying-oil state | Oil degradation (polar compounds) and smoke point affect flavour and acrylamide. | Defer; `LIPID_OXIDATION` covers it broadly. | 21 | — / L |
| 39 | Holding and cooling safety | Time spent in the growth range during cooling and holding. | Authority cooling rules (cooling family), output as consistency only. | 31, 36 | — / L |
| 40 | Food-specific default durations | Per-process quantiles ignore what is cooked (V3). | Condition the quantiles on (process, food group, size class) with training-split counts, or keep them per process with the bracket labelled "process-only". | 31 | L / M |

---

## E. Revised lot-state schema (proposal; DRAFT; owner steps named)

### E.1 Design principles

| # | Principle | Why |
|---|---|---|
| P1 | One record per (lot, event, **layer view**). L1 and each L2 view (GENTLE, TYPICAL, INTENSE, later Monte Carlo draws) are separate records linked by lot and event keys, so the layers are never mixed (D-077). Food **reference properties** (SR composition, SR portions, FDA pH) are a third, separately labelled class, REFERENCE. They are neither text-stated nor a scenario assumption about the cook. | **Frozen-rule note:** D-077 names two layers for *conditions* and does not say where table-derived *food properties* go. Lane L-PH put pH into Layer 2. I propose a REFERENCE class instead. This is an extension for H4 to rule on, not a silent workaround. |
| P2 | Phase-resolved: aqueous, lipid, solid-piece classes, gas, structured (Q13). | Each property is defined on its physical phase. |
| P3 | **Provenance lattice.** Every field carries `depends_on`, and its claim tier is the *weakest* tier in its dependency closure (E.3), computed mechanically. | Stops defaults or AI matches being laundered through arithmetic. |
| P4 | Computed only. Learned outputs (Steps 29–35) never write back. | Packet §5.3; §213.12. |
| P5 | UNKNOWN is never 0. Intervals are closed; open ends are flagged. Corners are labelled as corners. | §141, §199.7. |
| P6 | Directions are scoped to a driver window (§4.4.x). | Formation and destruction run at the same time. |
| P7 | The Step 35 / Step 36 export is a **view with a firewall**, not the raw state (E.7). | Q29 non-circularity. |

### E.2 Value object (every field)

| Key | Type | Allowed values / notes |
|---|---|---|
| `v` / `lo`, `hi` / `cat` | number / numbers / enum | POINT / INTERVAL / QUALITATIVE payload |
| `vtype` | enum | POINT · INTERVAL · QUALITATIVE · UNKNOWN (§199.7) |
| `unit` | string | from the unit registry; clock-tagged for time (03.3: PROCESS_TAU) |
| `view` | enum | L1 · L2:GENTLE · L2:TYPICAL · L2:INTENSE · L2:MC#k |
| `basis` | enum | E.3 |
| `prov` | object | `source_ids[]`, `registry_row_ids[]` (SD-/KGE-/SRC-), `span` (a pointer, never text), `code_version`, `input_sha256` |
| `link_status` | enum | HUMAN_VERIFIED · AI_MATCHED · NONE (for SR / FDA / portion joins) |
| `depends_on` | list | field ids, member ids, registry rows, spans: the basis of the firewall |
| `tier` | derived | T0–T7, weakest link (E.3) |
| `flags` | set | e.g. PRESSURE_ASSUMED_1ATM, SLAB_GEOMETRY_ASSUMED, MATRIX_SORPTION_IGNORED, CO2_LOSS_POSSIBLE |
| `mask` | bool | for learners |

### E.3 Basis codes and claim tiers (what Step 36 may say)

| Tier | Bases | What may be emitted |
|---|---|---|
| T0 EVIDENCE | `EVD_MEASURED` (+ retention type, basis, censoring) | numbers (§141) |
| T1 CALIBRATED_MODEL | `CALIBRATED_MODEL` (frozen PARAM fit id + SIM-VAL id), only inside the validated domain | numbers with intervals, in-domain only |
| T2 TEXT_FACT | `TEXT_STATED`, `CARRIED_SETPOINT`, `CUE`, `CUT_HISTORY`, `PHYSICAL_DEFINITION` (with assumption flags), `TEXT_OBSERVED_ENDPOINT` | "the recipe says / by definition" |
| T3 REFERENCE_VERIFIED | `SR_COMPOSITION`, `SR_PORTION`, `FDA_PH_RANGE` with a HUMAN_VERIFIED link | a property of the named food, with its source; not a property of this dish |
| T4 MODEL_DERIVED | `ARITHMETIC`, `PHYSICS_MODEL` over T0–T3 inputs only | directions / `physically_possible`; NON_CITABLE |
| T5 SCENARIO | anything depending on `SCENARIO_DEFAULT` (SD-) or `CORPUS_QUANTILE` (KGE-) | bracket sets, labelled; NON_CITABLE |
| T6 AI_DRAFTED | `AI_MATCHED` links, `MECH_SCREEN` (unreviewed), `NER_FILL`, `UNIT_HULL` | diagnostics only; never in an answer |
| T7 UNKNOWN | — | UNKNOWN |

The weakest-link rule: tier(field) = max tier over `depends_on`. For example, a pH bound built from AI-matched FDA rows is
T6 even though the bound itself is a theorem.

### E.4 Fields per lot-step

| Field | Type | Unit | Allowed vtypes | Basis / provenance | Computed / learned | Owner step | Leak |
|---|---|---|---|---|---|---|---|
| **A. Keys and lineage** | | | | | | | |
| `lotstep_id`, `lot_id`, `parent_lot_ids[]`, `event_id`, `event_index` | ids | — | POINT | Rung A + replay | computed | 17, 18 | — |
| `process_tau_min` | interval | min (PROCESS_TAU) | INTERVAL / UNKNOWN | ARITHMETIC over durations (L1 view: L1 only) | computed | 03.3, 18 | L-02 (L2 view) |
| `lot_kind` | enum: INGREDIENT_RAW, CUT_PIECES, PIECES_IN_LIQUID, LIQUID_MIX, DOUGH_BATTER, EMULSION, FOAM, DRY_MIX, UNKNOWN | — | QUAL / UNKNOWN | rules on members + events | computed | 16, 18 | — |
| **B. Members and quantities** | | | | | | | |
| `members[]` | {ing_id, role ∈ SOLID_PIECE, LIQUID, FAT, SOLUTE, ACIDULANT, ALKALI_LEAVENING, WATER, SEASONING, UNKNOWN; link_status; ner_fill} | — | POINT | Rung A link; NER fill flagged | computed | 17, 18 | L-18 |
| `member_mass[ing]` | interval | g | POINT (stated mass only) / INTERVAL / UNKNOWN | TEXT_STATED · SR_PORTION · UNIT_HULL | computed | 12 (+ rc2 rule version) | L-06 |
| `lot_mass` | interval | g | INTERVAL / UNKNOWN | ARITHMETIC (members − sinks + absorbed water) | computed | 18 | inherits |
| `mass_sinks[]` | {kind ∈ EVAPORATION, DRIP, FAT_DRIP, LEACH_TO_LIQUID, DISCARD, ABSORBED_WATER; amount} | g | INTERVAL / QUAL / UNKNOWN | REFERENCE (USDA yields) · TEXT_OBSERVED ("reduce by half") · PHYSICS_MODEL | computed | 12, 18 | L-01 if SD |
| `water_to_food_ratio` | interval | g/g | INTERVAL / UNKNOWN | TEXT_STATED · ARITHMETIC | computed | 17 | — |
| **C. Phase-resolved composition** | | | | | | | |
| `phases[]` | {phase ∈ AQUEOUS, LIPID, SOLID:<class>, GAS, STRUCTURED; member allocation} | — | — | deterministic allocation from SR composition | computed | 16, 18 | L-05 |
| `comp[phase][c]`, c ∈ water, protein, fat, available CHO, sugars, starch, fibre, ash, Na, K, Ca, vitamin C (401 / 402 / 403 kept apart) | interval | g/g (minerals and vitamins mg/g) | INTERVAL / QUAL (presence) / UNKNOWN | SR hull over the candidate set; ARITHMETIC | computed | 12 | L-05; state mismatch (raw vs cooked; refuse) |
| `target_content_ref[svar]` | interval | mg/100 g | INTERVAL / UNKNOWN | REFERENCE (SR) | computed | 12 | feeds TARGET_ABSENT (C-sci 19) |
| **D. Aqueous-phase chemistry** | | | | | | | |
| `salt_in_water`, `sugar_in_water` | interval | g/g water | INTERVAL / UNKNOWN (Food.com: UNKNOWN) | ARITHMETIC (C) × `solute_distribution` | computed | 31 | L-05, L-06 |
| `solute_distribution` | enum: DISSOLVED_HOMOGENEOUS, SURFACE_APPLIED, PARTIAL_UPTAKE, IN_DISCARDED_LIQUID, UNKNOWN | — | QUAL | contact log + events | computed | 18 | — |
| `aw_solution_bound` | interval | — | INTERVAL / UNKNOWN | PHYSICS_MODEL (Norrish / electrolyte model / Ross product), flags MATRIX_SORPTION_IGNORED, SATURATION | computed | 31 | constants need sources (L-01 type) |
| `ph_interval` | interval | pH | INTERVAL / UNKNOWN | FDA_PH_RANGE (L-PH registry + crosswalk) + N1 bound | computed | 12 (data), 31 (rule) | L-07 |
| `ph_bound_flags` | set: CO2_LOSS_POSSIBLE, ACID_PRODUCING_REACTION, FERMENTATION, PRECIPITATION_POSSIBLE, TEMPERATURE_SHIFT, TISSUE_ACID_RELEASE, SOLIDS_NOT_EQUILIBRATED, MEMBER_RANGE_OPEN | — | QUAL | rules | computed | 31 | — |
| `titratable_acidity`, `buffer_capacity` | reserved | — | UNKNOWN | — | — | later | — |
| `water_quality` | {hardness, alkalinity} | — | UNKNOWN / user value | ASK | user | 36 | — |
| `oxygen_exposure` | enum: LID_ON, LID_OFF, PARTIAL, AGITATED, DEAERATED_BOILING, SEALED, UNKNOWN | — | QUAL | CUE · PROCESS_DEFINITION | computed | 17, 31 | — |
| **E. Geometry and thermal zones** (per solid-piece class) | | | | | | | |
| `geometry` | {shape ∈ SLAB, CUBE, CYLINDER, SPHERE, PARTICULATE, FORMED_MASS, UNKNOWN; half_dim; A/V} | m; 1/m | INTERVAL / UNKNOWN | TEXT_STATED size · CUT_HISTORY → SD bracket · REFERENCE mass + density → equivalent sphere | computed | 31 | L-01 (SD-05x) |
| `thermal_props` | {k, ρ, c_p, α} | SI | INTERVAL | PHYSICS_MODEL (Choi–Okos over C) or SD fallback | computed | 31 | L-16 |
| `medium_T` | {setpoint, effective (after thermal mixing)} | °C | POINT / INTERVAL / UNKNOWN | TEXT_STATED · CARRIED_SETPOINT · PHYSICAL_DEFINITION · SCENARIO_DEFAULT | computed | 17, 31 | L-01, L-03 |
| `zone_T[zone]`, zone ∈ SURFACE, CORE, VOLUME_AVG | {T_end, T_max} | °C | INTERVAL / UNKNOWN | PHYSICS_MODEL with evaporative cap (N2) | computed | 31 (shared with 26) | L-04 |
| `surface_regime` | enum: IMMERSED_WET, WET_EVAPORATION_LIMITED, DRYING, CRUST, UNKNOWN | — | QUAL | PHYSICS_MODEL | computed | 31 | L-04 |
| `dose[zone][kernel]` | interval | equivalent min | INTERVAL / UNKNOWN | PHYSICS_MODEL; registered kernels only ((T_ref, z) or Step 24 Ea grid) | computed | 31 | L-01, L-04 |
| `minutes_above[zone][θ]` | interval | min | INTERVAL / UNKNOWN | PHYSICS_MODEL; θ from a sourced thresholds registry | computed | 31 | — |
| **F. History (H_t)** (definitions in E.6) | | | | | | | |
| `cell_integrity` | enum | — | QUAL / UNKNOWN | operator on events | computed | 16a, 18 | — |
| `time_since_disruption` | interval | min (PROCESS_TAU) | INTERVAL / UNKNOWN | ARITHMETIC over durations | computed | 16a, 18 | L-02 (L2 view) |
| `enzyme_state[family]`, family ∈ ALLIINASE, MYROSINASE, PPO, LOX, ASCORBATE_OXIDASE, PME, CHLOROPHYLLASE, PEROXIDASE | enum: ACTIVE, PARTLY_INACTIVATED, INACTIVATED, UNKNOWN | — | QUAL | thermal history vs matrix-scoped windows (MECH `ENZYME_THERMAL_INACTIVATION`) | computed | 16a, 21 | L-08 |
| `thermal_history` | {T_max_ever[zone], Ω_cum[zone][kernel], wet_heat_min, n_heat_cycles} | °C, eq-min, min | INTERVAL | PHYSICS_MODEL | computed | 16a, 31 | L-04 |
| `contact_log[]` | E.5 | — | — | replay + durations | computed | 16a, 18 | L-02 |
| `uptake_fraction[contact]` | interval | — | INTERVAL / UNKNOWN | `slab_uptake_fraction` with a scenario D interval | computed | 31 | L-01 (D defaults) |
| `liquid_fate` | enum: RETAINED_IN_DISH, DRAINED_DISCARDED, REDUCED, PARTLY_RETAINED, UNKNOWN | — | QUAL | events (drain, strain, discard, serve) | computed | 16a, 18 | — |
| `freeze_history`, `fermentation_state` | {frozen_ever, cycles}; enum | — | QUAL | events (+ MECH) | computed | 16a, 18 | — |
| **G. Structure and colloids** | | | | | | | |
| `starch_state` · `protein_state` · `gluten_development` · `dispersion_state` · `crust_present` · `cookedness` | enums (E.6) | — | QUAL / UNKNOWN | MECH windows (water-scoped) + thermal history + cues | computed | 16a, 21, 22 | L-08 (T6 until G21.6) |
| **H. Mechanism screen** | | | | | | | |
| `mech_screen[mech_id]` | {reactants K3, drivers K3, inhibitors K3, verdict ∈ POSSIBLE, NOT_POSSIBLE, UNKNOWN; view; mech_status; window_evidence_ids} | — | three-valued | MECH roster + fields above | computed | 22, 23 | L-08 |
| **I. Interaction edges** | E.5 | | | | computed | 22, 23 | L-08 |
| **J. Observed endpoints** | | | | | | | |
| `endpoints[]` | {span pointer, class ∈ COLOUR_BROWN, CRISP, TENDER, REDUCED_FRACTION, THICKENED, SET, INTERNAL_T, BOILING, …; value + unit; firewall_targets[]} | per class | POINT / QUAL | TEXT_OBSERVED_ENDPOINT | computed | 16, 17, 22 | L-12 |
| **K. Routes and nutrient values** | | | | | | | |
| `route[svar]` | {route ∈ DIRECT, INTERPOLATE, SIMULATE, QUALITATIVE, ASK, UNKNOWN, TARGET_ABSENT, CONTEXT_MISMATCH; value (T0 / T1 only); retention_type; liquid_fate_check; basis_check; domain_check; reasons} | per SVAR | per §141 | router | computed | 23, 25–27, 36 | L-09, L-10, L-11 |
| **L. Safety and allergens** | | | | | | | |
| `allergens` | set | — | QUAL | lineage union of ALLERGEN | computed | 18, 36 | — |
| `pathogen_control[authority]` | enum: CONSISTENT, NOT_CONSISTENT, UNKNOWN (CORE zone, per view) | — | QUAL | PHYSICS_MODEL + authority table (human-opened) | computed | 31, 36 + human gate | L-01, L-04 |

### E.5 Interaction edge and contact-log objects

| Key | Type | Allowed values / rule |
|---|---|---|
| `edge_id` | string | minted |
| `kind` | enum | **REACTANT_PAIR** (chemical; needs a MECH id) · **CONDITION_SUPPLIER** (i shifts the pH, solute load or a_w seen by j; needs a MECH id) · **TRANSPORT** (solute moves from i to j, or leaches from j into the liquid) · **THERMAL** (enthalpy exchange on merge) · **MEDIUM** (i's liquid or fat is j's heat or mass-transfer medium) · **PARTITION** (lipophilic or volatile compounds into the lipid phase or headspace) |
| `supplier`, `receiver` | member or phase ids | both must exist in the lot at the contact time |
| `phase` | enum | AQUEOUS · LIPID · SURFACE · HEADSPACE |
| `mechanism_id` | MECH id / null | required for REACTANT_PAIR and CONDITION_SUPPLIER; null for physical kinds |
| `direction` | QUAL | INCREASES · DECREASES · ENABLES · INHIBITS · UNKNOWN, with its driver window (§4.4.x) |
| `contact_ref` | contact_log id | — |
| `created_from` | list of field ids | **mandatory**: no edge without both supplier roles being present |
| `basis`, `evidence_ids`, `review_status`, `tier` | — | PHYSICS_MODEL (physical kinds) or MECH_SCREEN; AI_DRAFTED until G21.6; weakest-link tier |
| **Contact-log entry** | {contact_id, agent ∈ SALT, SUGAR, ACID, ALKALI, WATER, FAT, HEAT_MEDIUM, ENZYME_TRIGGER; source; receiver; phase; start_event; end_event; ended_by ∈ DISCARD, RINSE, DRAIN, SERVE, END; duration interval (PROCESS_TAU); T_during interval; basis} | the same contact log serves Q14 (order) and enzyme timing (cut → rest → heat) |
| Forbidden | — | edges from co-occurrence, PMI or learned attention weights (§213.12). Learned weights may be *compared* with edges in an evaluation, never written as edges. |

### E.6 Physical and history variables for SVAR v1.1 (Q11; additive, H4; owner 16a)

| Variable | Definition | Type / unit | Computed by | SVAR id |
|---|---|---|---|---|
| moisture content | g water per 100 g of lot or phase, wet basis | INTERVAL g/100 g | ARITHMETIC ± sinks | promote **FUT-001** |
| water activity (solution bound) | a_w of the aqueous phase treated as a solution; *not* a measured a_w | INTERVAL | D4 model | promote **FUT-002**, basis `SOLUTION_BOUND` |
| phase state | `lot_kind` + `phases[]` | enum | rules | promote **FUT-005** |
| zone temperatures | SURFACE, CORE, VOLUME_AVG | INTERVAL °C | physics | promote **FUT-012** (one id per zone) |
| colour, browning index | measured observables | UNKNOWN unless measured | — | **FUT-008/009** stay UNKNOWN; `surface_regime` is not a colour |
| form / cut / mixture identity / cooked-raw | procedural | enum / id | events | **FUT-023/024/026/027** |
| pathogen control; allergen state | authority consistency; contains-via-lineage | enum; set | physics + table; lineage | **FUT-028**, **FUT-029** |
| `cell_integrity` | INTACT · CUT · CRUSHED_PUREED · FROZEN_THAWED · HEAT_DISRUPTED · UNKNOWN | enum | event operator | new |
| `time_since_disruption` | minutes from the last disruption event to now | INTERVAL min | durations | new |
| `enzyme_state[family]` | ACTIVE · PARTLY_INACTIVATED · INACTIVATED · UNKNOWN | enum | thermal history vs windows | new |
| `thermal_history` | T_max_ever, Ω_cum per registered kernel, minutes above registered θ, per zone | INTERVAL | physics | new |
| `surface_regime`, `crust_present` | E.4 | enum | physics | new |
| `liquid_fate` | E.4 | enum | events | new |
| `contact_log` | E.5 | object | replay | new |
| `freeze_history`, `fermentation_state` | E.4 | enum | events | new |
| `starch_state` | NATIVE · PARTIAL · GELATINISED · RETROGRADING · UNKNOWN | enum | water-scoped window + history | new |
| `protein_state` | NATIVE · DENATURED · AGGREGATED_GEL · ACID_DENATURED · UNKNOWN | enum | window + history + pH | new |
| `gluten_development` | NONE · LOW · DEVELOPED · UNKNOWN (cue: knead/mix + water + time) | enum | cues | new |
| `dispersion_state` | NONE · EMULSION · FOAM · BROKEN · UNKNOWN (needs a stabiliser present + a mixing cue) | enum | cues + composition | new |
| `oxygen_exposure` | E.4 | enum | cues | new |
| `salt_in_water`, `sugar_in_water`, `ph_interval` | E.4 | INTERVAL | arithmetic / N1 | new |

Rule: no variable here is ever the training target of a model whose features include that variable's own inputs.

### E.7 Feeding Step 35 without circularity (Q29): export views and firewall

The field classes are:
- **FC1** lineage and members
- **FC2** masses and reference composition
- **FC3** aqueous chemistry
- **FC4** L1 conditions and L1-only physics
- **FC5** L2 scenario fields and any physics over L2 inputs
- **FC6** history
- **FC7** AI-drafted fields: structure states, MECH screen, REACTANT_PAIR and CONDITION_SUPPLIER edges, AI-matched links
- **FC8** observed endpoints
- **FC9** routes and values
- **FC10** NER fills

| Task view | FC1 | FC2 | FC3 | FC4 | FC5 | FC6 | FC7 | FC8 | FC9 | FC10 |
|---|---|---|---|---|---|---|---|---|---|---|
| (a) D3 state tracking vs Step 19 gold (lot state is the *prediction*; input = text) | pred | pred | pred | pred | BAN | pred | BAN | input-text only | BAN | separate arm |
| (b) H1 state-aware retrieval | ALLOW | ALLOW | ALLOW | ALLOW | ABLATION-ONLY | ALLOW | BAN (display-only) | ALLOW, except for questions about that same state | T0/T1 only | flagged arm |
| (c) Masked-ingredient completion | RECOMPUTE | RECOMPUTE | RECOMPUTE | ALLOW | ABLATION-ONLY (train-split statistics) | RECOMPUTE | BAN | BAN if it names the masked item | BAN | flagged arm |
| (d) Next-step / process prediction | ≤ t−1 | ≤ t−1 | ≤ t−1 | ≤ t−1 | ≤ t−1, ABLATION-ONLY; **BAN for the target event** | ≤ t−1 | BAN | BAN for the target step | BAN | flagged arm |
| (e) Physics validation (D-VAL) | ALLOW | ALLOW | — | input | input | ALLOW | BAN | **target** (masked from input) | — | — |
| (f) Transition learning (Steps 29–33) | — | EVD conditions only | EVD | EVD | ABLATION-ONLY + permuted-registry control (Q1) | — | BAN | — | EVD targets | — |

RECOMPUTE: rebuild the lot state with the masked member removed. Any field whose `depends_on` closure contains the
masked member is dropped. BAN: the field is never exported for that task.

Mechanics:
1. Every field stores `depends_on`. The exporter computes the closure and refuses to export when closure ∩ B(task) ≠ ∅.
   Make this a property test.
2. Corpus statistics (KGE quantiles, IDF) are recomputed on the training split.
3. Embeddings never write back to the lot state.
4. The export carries tiers and masks, so each learner can be audited by tier ("T5 removed", "T6 removed" ablations).

### E.8 Leak register: every place a default or AI guess could reach a claim

| ID | Where | What could leak | Into which claim | Control (owner step) |
|---|---|---|---|---|
| L-01 | `scenario_defaults_v1.csv` (27 rows, `SOURCE_UNVERIFIED_AGENT_RECALLED`, citation-like `source_hint`) | recalled numbers read as sourced | every L2 field; displayed scenarios; features | rename the column `agent_recall_hint`; tier T5; Step 36 prints L2 values only with bracket + label (31, 36) |
| L-02 | KGE `PROC_TYPICAL_DURATION` (BBC + Wikibooks, UNVERIFIED, per process) | population shift; a BBC-derived parameter; test-split statistics | 60.5 % of L2 durations → doses, minutes above, features | `CORPUS_QUANTILE` basis; condition on food; training-split recompute; D-003 note (31, 35) |
| L-03 | `PHYSICAL_DEFINITION` 100 °C | 1 atm and pure water assumed | doses; safety consistency | `PRESSURE_ASSUMED_1ATM` flag (17) |
| L-04 | DRY/FAT boundary error (V2) | doses wrong by about 10² | features, screens, slides | N2 fix; mark old fields SUPERSEDED (26, 31) |
| L-05 | AI-drafted ING→SR and ING→FDA-pH matches | the wrong food (e.g. milk → human milk) | composition, solute load, a_w, pH bound → screen, edges, QUALITATIVE | tier T6 until verified; per-band accuracy; hulls (12) |
| L-06 | SR_PORTION links; Food.com unit hulls | false precision | masses → ratios → solute gates | intervals only; Food.com ratios UNKNOWN (12) |
| L-07 | FDA pH ("normal and natural state", approximate); the 4.6 threshold | raw values applied to cooked tissue; a safety threshold used as chemistry | chlorophyll, pectin, anthocyanin gates | N1 flags incl. `TISSUE_ACID_RELEASE`; per-mechanism windows (21, 31) |
| L-08 | MECH roster text and windows (AI-drafted; some "reviewer-asserted") | unreviewed chemistry | screen, edges, structure states → QUALITATIVE (Q21) | tier T6, DESCRIPTIVE only until G21.6 (21–23) |
| L-09 | AA fit domain (acidic juices) | domain transfer | SIMULATE for vegetables in water | matrix / pH / water-contact domain gate (25, 27) |
| L-10 | Basis mismatch (reduced vs total AA; TR vs AR; FW vs DW) | incompatible quantities compared | SIM-VAL error; DIRECT values | basis checks at G0/G8 (05, 27) |
| L-11 | DIRECT without presence and context gates | numbers for absent targets and minor ingredients | DIRECT headline; answers | C-sci 19–20 (23) |
| L-12 | Endpoint cues used as inputs | outcome leakage | browning / tenderness predictions | `TEXT_OBSERVED` basis + firewall (16, 22, 35) |
| L-13 | TYPICAL read as "the estimate" | the mid of corners is not a mode | answers, slides | always show the bracket set; Monte Carlo spreads later (36) |
| L-14 | Corpus statistics including test recipes | test leakage | Step 35 / H1 scores | training-split recompute (15, 35) |
| L-15 | L2 fields deterministic in the process id | target leakage | next-step / process tasks | ban for the target event (35) |
| L-16 | `FOOD_HIGH_MOISTURE` properties applied to all foods | wrong properties for oils, syrups, frozen food | doses | composition-based properties or UNKNOWN (31) |
| L-17 | R6 imputed duplicates | copied targets | H2 diagnostic | duplicate clustering (29) |
| L-18 | NER second-opinion fills | a model output treated as fact | members → composition → routes | flag; separate arm; never gold (17) |
| L-19 | LLM recall in persona reviews, including this one | recalled facts | defaults, windows, MECH text | everything recalled marked `SOURCE_UNVERIFIED_AGENT_RECALLED` until a human opens the source (all) |
| L-20 | "egg × bake vitamin C" DIRECT | a meaningless figure shown as coverage | the talk's router slide | re-run with the gates; show both figures (23) |

---

## 5. Counts and top points

**Lean tally over the 22 questions answered:**

| Tally | n | Questions |
|---|---|---|
| AGREE | 11 | Q2, Q3, Q4, Q8, Q9, Q13, Q14, Q15, Q19, Q29, Q32 (most with additions) |
| PARTLY | 1 | Q7 |
| DISAGREE | 7 | Q1, Q5, Q10, Q12, Q16 (order), Q18, Q31 |
| NO LEAN stated | 3 | Q6, Q11, Q17 (position given) |

So 12 agree (counting Q7) and 7 disagree; 22 in total.

**Top points, in order of urgency:**
1. **The Layer-2 boundary has no evaporation term (V2).** Moist cores reach 160–220 °C in ovens, oil and pans, and
   doses are about 10² too high. Cap moist zones at T_evap and add a surface regime (N2) before any feature, screen or
   slide uses DRY/FAT drivers.
2. **DIRECT is not applicability (V5, N5).** 81 % of vitamin-C DIRECT routes in the sample are for foods with ≈ 0 mg
   vitamin C (egg × bake alone is 25 %), and 83 % come through merged lots. Add the target-presence and context gates
   and show the old and new counts side by side.
3. **The SIMULATE domain is acidic fruit liquids (V7).** Gate by matrix, pH and water contact; match the AA vs
   total-vitamin-C basis. Finish the leaching branch before adding chlorophyll.
4. **pH: emit a provable mixture-pH interval** (closed-system bound plus violation flags, water as a member) instead of
   flags. Never use 4.6 as a chemistry threshold (N1, V10).
5. **Keep Layer 2 out of claim-bearing learned features** (Q1). Allow it only as an ablation with a permuted-registry
   control, because on EVD rows it is a re-encoding of the process label.
6. **The lot state needs phases, a provenance lattice (weakest-link tiers) and physical interaction edges** (thermal,
   medium, transport, partition) next to the mechanism edges (§E).
7. **Formula corrections:** F₀ only for canning, cooking safety from authority time–temperature rules at the core
   (N4); thaw is not the mirror of freezing; Fick bounds brines only; quality doses at the volume-average temperature.
8. **Step 35 firewall:** recompute the state after masking, ban target-event L2 fields, train-split corpus statistics,
   and use text-observed endpoints as non-circular labels, including D-VAL against author-stated internal temperatures.

**Science items that fit before 25 Nov:** all of them are code, registry or wording, with no new data:
- the N2 fix with its invariant test;
- the presence and context gates, then a census re-run;
- the domain gate for the AA pilot;
- renaming the SD hint column;
- the N1 pH-bound function with tests;
- reporting V1 numbers honestly;
- a D-VAL count of recipes that state an internal temperature.

---

## 6. Sources consulted on the web (load-bearing facts only)

| Fact checked | Source(s) | Used for |
|---|---|---|
| The FDA/CFSAN "Approximate pH of Foods and Food Products" table exists (Oct 2003 and April 2007 revisions); approximate values, variation by variety, growing conditions and processing | [webharvest.gov Oct 2003 capture](https://webharvest.gov/peth04/20041014211751/http:/www.cfsan.fda.gov/~comm/lacf-phs.html); [riverstonehealth.org print copy](https://riverstonehealth.org/wp-content/uploads/FDA-Approximate-pH-of-Foods.pdf); lane L-PH report | Q10, V13 |
| UK time–temperature equivalents (60 °C/45 min … 80 °C/6 s) and their 6-log *L. monocytogenes* basis | [High Speed Training sheet (secondary)](https://www.highspeedtraining.co.uk/hub/wp-content/uploads/2021/04/HST_CookTempRecordDoc-1.pdf); [MAPAQ pasteurisation-equivalence table](https://www.mapaq.gouv.qc.ca/SiteCollectionDocuments/TransformationPortail/PRIS/Baremedepasteurisationequivalent70-2.pdf); [sagentia article](https://sagentia.com/?p=8719) | N4 (secondary only; a human must open the primary FSA/ACMSF text) |
| Farkas, Singh & Rumsey (1996), a two-region moving-boundary immersion-frying model, *J. Food Eng.* 29(2):211–226 and 227–248 | [Scilit record](https://www.scilit.net/publications/dc05de87c5b8d4b000781b65a15175a1); [zhenzhi record](https://data.zhenzhi.com/details/1/887965821) | Q3, N2 |
| True vs apparent retention (Murphy, Criner & Gray 1975); USDA R6 retention table | [USDA NAL archived scan](https://webarchive.library.unt.edu/eot2008/20080916112152/http:/www.nal.usda.gov/fnic/foodcomp/Data/Classics/retn_murphy.pdf); [Ag Data Commons R6](https://agdatacommons.nal.usda.gov/articles/dataset/USDA_Table_of_Nutrient_Retention_Factors_Release_6_2007_/24660888/1) | Q18, C-sci 1/18 |
| Norrish (1966) for confectionery syrups; Ross (1975) for intermediate-moisture foods, tested by Chirife | [OUP IJFST reference list](https://academic.oup.com/ijfst/article/16/4/409/7910737); [Chirife record](https://bdu3.siu.edu.ar/bdu/Record/paper:paper_09505423_v13_n5_p417_CHIRIFE) | C-sci 34, D4 |
| ASHRAE Refrigeration handbook chapter "Thermal Properties of Foods" (Ch. 19 in 2018) includes initial freezing points and Choi–Okos models; copyrighted | [ASHRAE 2018 Refrigeration contents](https://www.ashrae.org/technical-resources/publications-library/ashrae-handbook/table-of-contents-2018-ashrae-handbook-refrigeration); [GlobalSpec page for the 2006 ASHRAE Refrigeration edition](https://www.globalspec.com/reference/53600/203279/food-storage-and-equipment) | Q2, Q5, C-sci 33 |

Everything else in this review is either computed from repo files (paths given), a standard mathematical result (N1
derivation, N3 series), or reviewer recall, marked as such (L-19).

---

## 7. Runs (rows matching `registry/compute_runs_v1.csv`; outputs in the session scratchpad, not committed)

```
RUN-S176-REVA-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS,1,"nice -n 10 python -I <scratchpad>/reva/direct_breakdown.py <scratchpad>/reva/direct_breakdown_1000.json 1000 (seeded_sample seed 20261104; unchanged router_demo.route_text; SVAR-000009)",<scratchpad>/reva/direct_breakdown_1000.json,6e6851b067fc21aa250098db8890811c01e323122bc50e8d2f05db181992d7e4,2026-11-08T13:07Z (approx),2026-11-08T13:14:55Z,DONE,"REV-A read-only check; counts only (no text, no recipe ids); BBC not on server so A1 excluded; load avg ~50 at start (shared server), single process"
RUN-S176-REVA-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE (synthetic events),1,"python -c ScenarioLayer.load().run(<7 synthetic records>); physics_drivers core_trajectory/minutes_above/trajectory_dose comparisons",stdout (values quoted in V2/N2/N3),n/a,2026-11-08T13:0xZ,2026-11-08T13:0xZ,DONE,"<1 s each; no data read except registry/scenario_defaults_v1.csv and KGE PROC_TYPICAL_DURATION"
```

Here `<scratchpad>` is `/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad`.
The SR Legacy lookups in N5 read `data/raw/fdc/sr_legacy/.../{nutrient,food,food_nutrient}.csv` and
`registry/ingredients/fdc_crosswalk_candidates_v0.csv` (read-only, a few seconds). No ledger, registry or tracked file
was modified; this file is the only write.

## 8. For the humans (decisions this review needs; nothing here is decided)

1. Accept or reject the N2 boundary fix, and mark the DRY/FAT core fields of the current `scenario_L2_*` reports
   SUPERSEDED (they stay on file under R-20).
2. Add TARGET_ABSENT and CONTEXT_MISMATCH to the route enum (H4) and re-run the vitamin-C census.
3. Add a REFERENCE class for food properties alongside D-077's L1 and L2 (P1), or rule on where SR and FDA values live.
4. Record the AA-pilot SIMULATE domain gate (matrix class, pH, water contact) in the Step 27 pre-registration before
   the fit is frozen.
5. Ratify the provenance-lattice rule (weakest-link tier) as a Step 36 claim-enforcement rule.
6. Approve the SVAR v1.1 list in §E.6 (H4; owner 16a), promoting the FUTURE ids.
7. Name an external food scientist (C-sci 11) and give them N1–N4 plus 20–30 MECH windows.
