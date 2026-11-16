# S181 demo snapshot — findings

**Labels: DIAGNOSTIC_ONLY · AI_DRAFTED_SCENARIOS · SELF_WRITTEN_RECIPE_TEXT_ONLY · NO_HUMAN_SIGNOFF_D085.** Written by the coding agent, 17 Nov 2026. Not human-reviewed. No gold exists for any scenario; nothing below is an accuracy claim.

## What was built

- `web/public/snapshot/`: 17 data files + `manifest.json`, `manifest.sig`, `public_key.pem`; **1,103,192 bytes** (1.10 MB) in total.
- Manifest sha256 `bf0f80611429552b1a8264bdedf56b03fef1323630e41b896b1e3cfd81a24025`; git HEAD at build `bbe0e6c2b3fb89d8be8a987a95bd2eed0f6c0fc2` (working tree had the new, uncommitted S181 files); builder `s181-snapshot-1.0.0`; generated_at `2026-11-17T00:00:00Z` (argument, no wall clock).
- `rung_config` = `{"basis": "D-134", "coord_food_guard": true, "lineage_vnext": true}`. Setting `builder.rung` / `builder.binder.rung` after construction worked; no fallback was needed.
- Licence gate: mode `public`, bbc_derived_edges `EXCLUDED`, carbon_figures `EXCLUDED`; no BBC marker string in any file; every `recipe_text` / `recipe_sha256` / graph `raw_sha256` is in the allow-list.
- Evidence rows cited anywhere in the output, looked up in the EVD ledger: `EVD-002765` → ['SRC-000001'] (USDA-RETN-R6); `EVD-002781` → ['SRC-000001'] (USDA-RETN-R6). None is BBC-derived.
- `--verify`: OK. `--check`: FRESH (a full in-memory rebuild was byte-identical to disk). Unit tests: 41 passed (`tests/unit/test_s181_demo_snapshot.py`).
- The private key is at `~/.culinarystate_private/explorer_snapshot_ed25519.pem` (mode 0600, generated on first run). It is not in the repository.

## Route reached at the final state, per scenario

Final state = the last state of the food the question names. Question kind RETENTION_NUMERIC.

| Scenario | Food · final step (action) | vitc route | lycopene route | Evidence applied / near | States differ vNext on vs off |
|---|---|---|---|---|---|
| `tomato-a` | tomato · step 2 (Boil) | DIRECT | DIRECT | applied EVD-002765, applied EVD-002781 | no |
| `tomato-b` | tomato · step 2 (Boil) | UNKNOWN | UNKNOWN | near EVD-002765, near EVD-002781 | no |
| `tomato-c` | tomato · step 2 (Boil) | UNKNOWN | UNKNOWN | near EVD-002765, near EVD-002781 | no |
| `tomato-d` | tomato · step 2 (Boil) | UNKNOWN | UNKNOWN | near EVD-002765, near EVD-002781 | YES |
| `sauce-coref` | tomato · step 5 (Blend) | UNKNOWN | UNKNOWN | none | YES |
| `acid-alternatives` | tomato · step 2 (Boil) | UNKNOWN | UNKNOWN | near EVD-002765, near EVD-002781 | YES |
| `cut-dice` | tomato · step 2 (Boil) | DIRECT | DIRECT | applied EVD-002765, applied EVD-002781 | no |
| `cut-mixed` | tomato · step 5 (Simmer) | UNKNOWN | UNKNOWN | none | no |
| `cut-mixed` | carrot · step 5 (Simmer) | UNKNOWN | — (not asked) | none | no |
| `banana-abstain` | banana · step 3 (Bake) | UNKNOWN | — (not asked) | none | no |

## vNext on (D-134, used for the snapshot) vs off (the `StateBuilder` default)

`StateBuilder.__init__` builds `RungA(coord_food_guard=True)`; D-134 records `lineage_vnext=True` for State v2. `src/` was not edited: the tool replaces the rung on the constructed builder. Each scenario was built under both and the comparison is stored in every scenario file as `vnext_comparison`.

- `tomato-a`: identical; graph diagnostics ['LEXICAL_COREF_DESCENDANT']
- `tomato-b`: identical; graph diagnostics ['LEXICAL_COREF_DESCENDANT']
- `tomato-c`: identical; graph diagnostics ['LEXICAL_COREF_DESCENDANT']
- `tomato-d`: **differs** — state indexes [1] (vNext on: 2 states, off: 2); graph diagnostics ['LEXICAL_COREF_DESCENDANT', 'VNEXT_FAT_STAYS']
- `sauce-coref`: **differs** — state indexes [2, 5, 6] (vNext on: 6 states, off: 7); graph diagnostics ['LEXICAL_COREF_DESCENDANT', 'VNEXT_FAT_STAYS', 'LEXICAL_COREF_DESCENDANT', 'VNEXT_MIXTURE_COREF']
- `acid-alternatives`: **differs** — state indexes [1] (vNext on: 2 states, off: 2); graph diagnostics ['LEXICAL_COREF_DESCENDANT', 'VNEXT_ALTERNATIVE_SKIPPED']
- `cut-dice`: identical; graph diagnostics ['LEXICAL_COREF_DESCENDANT']
- `cut-mixed`: identical; graph diagnostics ['LEXICAL_COREF_DESCENDANT', 'LEXICAL_COREF_DESCENDANT', 'LEXICAL_COREF_DESCENDANT', 'IMPLICIT_ARG_BOUND']
- `banana-abstain`: identical; graph diagnostics ['LEXICAL_COREF_DESCENDANT', 'IMPLICIT_ARG_BOUND']

Three of nine scenarios differ: `tomato-d`, `sauce-coref`, `acid-alternatives`. A, B, C, both cut scenarios and the abstention are identical under both. **The code default and the recorded decision disagree, and it changes demo output**; that needs a human decision, not a tool workaround.

## Which phrasing of tomato D was kept

Three were tried under vNext:

1. "Chop the tomatoes. Add the tomatoes, salt, vinegar and olive oil to a pot of water. Boil for 15 minutes." — oil bound (`lipid_present` true), three states, identical under both configurations.
2. "Chop the tomatoes. Heat the olive oil in a pan. Add the tomatoes, salt and vinegar. Simmer for 15 minutes." — oil **not** bound into the tomato lot (lot = salt, tomato, vinegar; lipid UNKNOWN `NO_RECOGNIZED_MARKER`), and no near evidence.
3. **Kept:** "Chop the tomatoes. Boil the tomatoes in water with salt, vinegar and olive oil for 15 minutes." — oil bound (lot = olive oil, salt, tomato, vinegar, water; `lipid_present` true; diagnostic `VNEXT_FAT_STAYS`).

Phrasing 3 was kept because it is the same sentence frame as A, B and C, so the four differ by one ingredient at a time. It binds the oil only with vNext on; with the default configuration the final state differs. Phrasing 1 binds the oil under both. Phrasing 2, arguably the most natural way to cook this, does not bind the oil at all.

## The eight contractual ask outputs (`ask/*.json`)

| Case | Branch | Mode | Answer (first 110 chars) |
|---|---|---|---|
| DEMO-METADATA | METADATA | ABSTAIN_NOT_BUILT | This kind of question (metadata) is not wired up yet, so I won't guess an answer. |
| DEMO-PHYSICS | TRANSFORMATION | ABSTAIN | I cannot give a numeric result for those conditions from the available evidence. |
| DEMO-RECIPE-SEARCH | SEMANTIC | ABSTAIN_NOT_BUILT | This kind of question (semantic) is not wired up yet, so I won't guess an answer. |
| DEMO-RETENTION | TRANSFORMATION | ABSTAIN | I cannot give a numeric result for those conditions from the available evidence. |
| DEMO-SAFETY | SAFETY | ABSTAIN_SAFETY | I can't answer food-safety questions (safe temperatures, doneness, bacteria, or how long food keeps), so I won |
| DEMO-SUBSTITUTION | RELATIONSHIP | ABSTAIN_NO_EDGES | I have no substitution pattern for butter in the recipe corpus, so I won't guess. This public build leaves out |
| DEMO-UNKNOWN | UNKNOWN | ASK | I couldn't tell what you're asking. Please name the food, the process and what you care about (for example vit |
| DEMO-VISION | MULTIMODAL | ABSTAIN_UNSUPPORTED | Images, audio and video are not supported yet, so I can't judge this. |

## Plain-LLM baseline (arm B0_LLM_ONLY) — DIAGNOSTIC_ONLY

One model (`qwen2.5:7b-instruct` via `ask_local` in `tools/s180_run_layer1_arms.py`, ollama on vinayak-server), one prompt, temperature 0, no system contract, no gold. Prompt: `Recipe: <self-written text>\n\nQuestion: <question> Answer in two sentences.` 19 of 19 questions answered; replies are stored verbatim in `demo/baseline_cache_v1.json` and copied into each scenario file as `baseline`, with `claim_verifier.verify(baseline_text, claim_packet)` as `baseline_check`. This table states what each side did. It does not rank them.

| Scenario · question | System route | System answer (template) | Baseline answer (first 120 chars) | Numbers the verifier read in the baseline (matches packet evidence?) | Verifier verdict on baseline |
|---|---|---|---|---|---|
| `tomato-a` · vitc-retention | DIRECT | For tomato at step 2, the measured vitc value is EVD-002765=95.0% [EVD-002765]. This is taken from the cited evidence and nothing is inferred beyond i | After boiling tomatoes in water for 15 minutes, some of the vitamin C content will be lost due to heat exposure and leac | none | OK |
| `tomato-a` · lycopene-retention | DIRECT | For tomato at step 2, the measured lycopene value is EVD-002781=95.0% [EVD-002781]. This is taken from the cited evidence and nothing is inferred beyo | After boiling tomatoes for 15 minutes, some of the lycopene content may be lost due to heat exposure, but a significant  | none | OK |
| `tomato-a` · vitc-leaching | DIRECT | For tomato at step 2, the measured vitc value is EVD-002765=95.0% [EVD-002765]. This is taken from the cited evidence and nothing is inferred beyond i | Yes, some vitamin C can leach into the cooking water when tomatoes are boiled for an extended period like 15 minutes. To | none | OK |
| `tomato-b` · vitc-retention | UNKNOWN | For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_ | The boiling process can reduce the amount of vitamin C in tomatoes, and depending on the duration and temperature, appro | 20 (no) | FAIL: FORBIDDEN_NUMERIC_CLAIM, REQUIRED_CAVEAT_MISSING |
| `tomato-b` · lycopene-retention | UNKNOWN | For tomato at step 2, lycopene is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_MET | The boiling process can break down some of the cell walls, making lycopene more readily available to the body, but it do | 15 (no) | FAIL: FORBIDDEN_NUMERIC_CLAIM, REQUIRED_CAVEAT_MISSING |
| `tomato-c` · vitc-retention | UNKNOWN | For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_ | The boiling process can reduce the amount of vitamin C in tomatoes, but the addition of salt and vinegar might slightly  | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `tomato-c` · lycopene-retention | UNKNOWN | For tomato at step 2, lycopene is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_MET | The amount of lycopene remaining in the tomatoes after boiling them in water with salt and vinegar for 15 minutes is lik | 20 (no) | FAIL: FORBIDDEN_NUMERIC_CLAIM, REQUIRED_CAVEAT_MISSING |
| `tomato-d` · vitc-retention | UNKNOWN | For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_ | The amount of vitamin C remaining in the tomatoes after boiling them in water with salt, vinegar, and olive oil for 15 m | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `tomato-d` · lycopene-retention | UNKNOWN | For tomato at step 2, lycopene is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_MET | The process of boiling tomatoes in water with salt, vinegar, and olive oil for 15 minutes can increase the bioavailabili | 20 (no) | FAIL: FORBIDDEN_NUMERIC_CLAIM, REQUIRED_CAVEAT_MISSING |
| `sauce-coref` · vitc-retention | UNKNOWN | For tomato at step 5, vitc is not known from the evidence available for this context. Reasons: matrix: NO_EVIDENCE_ROW; process: NO_EVIDENCE_ROW; temp | The cooking process described, including chopping, frying, and simmering, can reduce the vitamin C content in tomatoes,  | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `sauce-coref` · lycopene-retention | UNKNOWN | For tomato at step 5, lycopene is not known from the evidence available for this context. Reasons: matrix: NO_EVIDENCE_ROW; process: NO_EVIDENCE_ROW;  | The cooking process described, including chopping, frying, simmering, and blending, does not significantly reduce the am | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `acid-alternatives` · vitc-retention | UNKNOWN | For tomato at step 2, vitc is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_ | The boiling of tomatoes with lemon juice or vinegar can enhance the solubility and absorption of certain nutrients, incl | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `acid-alternatives` · lycopene-retention | UNKNOWN | For tomato at step 2, lycopene is not known from the evidence available for this context. Reasons: measurement method platform: MEAS_HAS_3_ROWS_PE_MET | The boiling process can increase the availability of lycopene, a carotenoid antioxidant, due to the breakdown of cell wa | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `cut-dice` · vitc-retention | DIRECT | For tomato at step 2, the measured vitc value is EVD-002765=95.0% [EVD-002765]. This is taken from the cited evidence and nothing is inferred beyond i | After boiling tomatoes for 15 minutes, some of the vitamin C content will be lost due to heat exposure, but the exact am | none | OK |
| `cut-dice` · lycopene-retention | DIRECT | For tomato at step 2, the measured lycopene value is EVD-002781=95.0% [EVD-002781]. This is taken from the cited evidence and nothing is inferred beyo | After boiling tomatoes for 15 minutes, some of the lycopene content may be released into the water, but a significant am | none | OK |
| `cut-mixed` · vitc-retention | UNKNOWN | For tomato at step 5, vitc is not known from the evidence available for this context. Reasons: matrix: NO_EVIDENCE_ROW; process: NO_EVIDENCE_ROW; temp | The cooking process described, including boiling the carrots and then simmering with the tomatoes, generally does not si | 10 (no) | FAIL: FORBIDDEN_NUMERIC_CLAIM, REQUIRED_CAVEAT_MISSING |
| `cut-mixed` · lycopene-retention | UNKNOWN | For tomato at step 5, lycopene is not known from the evidence available for this context. Reasons: matrix: NO_EVIDENCE_ROW; process: NO_EVIDENCE_ROW;  | The amount of lycopene remaining in the tomatoes after this recipe is likely to be similar to that before cooking, as bo | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `cut-mixed` · carrot-vitc-retention | UNKNOWN | For carrot at step 5, vitc is not known from the evidence available for this context. Reasons: matrix: NO_EVIDENCE_ROW; process: NO_EVIDENCE_ROW; temp | The amount of vitamin C remaining in the carrots after boiling them for 10 minutes and then simmering with tomatoes for  | none | FAIL: REQUIRED_CAVEAT_MISSING |
| `banana-abstain` · vitc-retention | UNKNOWN | For banana at step 3, vitc is not known from the evidence available for this context. Reasons: matrix: NO_EVIDENCE_ROW; process: NO_EVIDENCE_ROW; temp | The baking process itself does not significantly reduce the amount of vitamin C in bananas; however, prolonged exposure  | none | FAIL: REQUIRED_CAVEAT_MISSING |

### Reading the baseline table honestly

- **On the five DIRECT questions (tomato-a ×3, cut-dice ×2) the plain model gave no number, said the amount cannot be precisely determined, and the verifier passed it.** The system stated the cited 95.0%. Here the plain model was the more cautious of the two.
- The plain model asserted a retention/loss figure with no source in 3 of 19 replies ("20-30%": tomato-b vitc, tomato-c lycopene, tomato-d lycopene). For tomato-d lycopene it wrote that 20-30% *remains*; for tomato-c lycopene that 20-30% is *lost*. The verifier flagged each as FORBIDDEN_NUMERIC_CLAIM.
- **Two FORBIDDEN_NUMERIC_CLAIM verdicts are verifier false positives, not model claims:** tomato-b lycopene (the number is "15" from "a 15-minute boil") and cut-mixed tomato vitc ("10" from "10-15 minutes"). `claimed_numbers` does not treat a hyphenated or ranged duration as a context unit. It also reads only the first number of a range ("20" of "20-30%").
- **REQUIRED_CAVEAT_MISSING on the baseline is a wording check.** The verifier accepts only `not known | unknown | cannot be determined | no evidence`. Replies such as "cannot be precisely determined" or "difficult to quantify" (tomato-c vitc, tomato-d vitc, acid-alternatives lycopene, cut-mixed carrot) are cautious in substance and still fail. So 14 FAIL of 19 overstates how often the plain model was substantively overconfident: at least 4 of the 14 failing replies explicitly decline to quantify.
- The plain model made mechanistic statements nothing here can check (e.g. salt and vinegar "might slightly preserve" vitamin C "due to their acidity"; lemon juice or vinegar "enhance the solubility and absorption" of vitamin C). No gold exists, so these are neither confirmed nor refuted.

## Surprises and things a reader would find odd

1. **None of the eight contractual ask cases returns an ANSWER.** All eight abstain or ask, including DEMO-RETENTION and DEMO-PHYSICS ("I cannot give a numeric result for those conditions") and DEMO-SUBSTITUTION (`ABSTAIN_NO_EDGES` in public mode). Deployment §4 asks the snapshot to span `ANSWER`, `COMPARE`, `TARGET_ABSENT`, `ANSWER_CORPUS_PATTERN`; the eight verbatim queries reach none of these. The only numeric answers in the snapshot come from the State v2 → claim-packet path (tomato-a, cut-dice). The ~50–60 curated questions of §4 were not built; only the eight were requested.
2. **The UNKNOWN reason shown for tomato B/C/D does not mention salt, vinegar or oil.** The template answer says `measurement method platform: MEAS_HAS_3_ROWS_PE_METHOD_NULL`. The composition reason (`COMPOSITION_UNCONFIRMED_IN_SOURCE:SALT+ACID+LIPID`) lives only in the basis of `Y.vitc_route`. On stage, the sentence that explains the central contrast is not the sentence the template produces.
3. **LEACHING on tomato-a gets the retention sentence.** Asked whether vitamin C leaches into the water, the template replies "the measured vitc value is EVD-002765=95.0%". `template_answer` has one DIRECT wording for every question kind.
4. **`sauce-coref`: the onions and the oil disappear from the mixture.** "Add the tomatoes and salt" yields a lot of salt + tomato only; "the mixture" and "the sauce" then continue that lot (`VNEXT_MIXTURE_COREF`), so coreference works, but the fried onions and olive oil are never merged in, `lipid_present` stays UNKNOWN for the tomato, and the onion has no state after step 2. The final state (Blend, not a heat step) has no evidence and no near evidence. With vNext off the scenario has 7 states instead of 6.
5. **`sauce-coref` and `banana-abstain`: blending and mashing leave `cell_integrity` = `CUT`**, not `CRUSHED_PUREED`. In the banana scenario `Peel` alone already sets `CUT`.
6. **`cut-mixed`: the diced tomato is reported as `SLICED`.** After "Add the tomatoes to the carrots. Simmer", `Q.piece_size_class` for the tomato is `SLICED` (the carrots' cut). This scenario was kept in the snapshot, labelled `explicit_cut_two_foods`, precisely so this is visible; `cut-dice` is the clean single-food cut (`DICED`, DIRECT). Whoever runs the demo should decide whether `cut-mixed` is shown.
7. **`piece_size_class` is UNKNOWN on the cutting step itself** and populated only on the next heat step (basis `CUT_HISTORY`).
8. **Boiled sliced carrot has no vitamin C evidence row** on this path (`cut-mixed` step 3: UNKNOWN, `NO_EVIDENCE_ROW`), while boiled tomato does.
9. **`acid-alternatives`: the choice is resolved by taking the first-named option.** The lot contains lemon juice and not vinegar (diagnostic `VNEXT_ALTERNATIVE_SKIPPED`), so it is not a conjunction, but `alternative_group` is `None` on every event: the graph does not record that a choice existed. With vNext off the state differs.
10. **Both DIRECT rows report 95.0%** (EVD-002765 vitamin C, EVD-002781 lycopene, both USDA-RETN-R6 / SRC-000001). Correct per the ledger as read; a viewer may take the identical figures for a bug.
11. All 280 template answers pass the verifier (0 failures), which is expected since the verifier was written against them.
12. `tomato-b` was first drafted as "Add the tomatoes and salt to a pot of water. Boil…"; that phrasing differed between vNext on/off, the kept "Boil the tomatoes in water with salt…" does not.

## Scope notes

- `--check` rebuilds with the `git_head` and `generated_at` recorded in the committed manifest, because committing the snapshot moves HEAD. It detects any change in engine output, scenarios, baseline cache or the builder file (`inputs` hashes), not the commit the snapshot sits in. `git_head` therefore names the commit the build ran on top of.
- The recipe-sha allow-list is the nine scenario texts plus the one recipe text inside the contractual case DEMO-PHYSICS ("Boil carrots in water at 90 C for 5 minutes.", authored in `tools/s179_submission_demo.py`). The two sets are listed separately in the manifest.
- Claim packets were compiled for every state × {vitc, lycopene} × all five question kinds in `QUESTION_AXES` (including FLAVOUR, which the compiler documents as unserviceable).
- The baseline needed ssh to vinayak-server; it ran after the coordinator reported the VPN up. Rebuilding does not need the server: the build reads only the cache. `--run-baseline` refills missing or NOT_RUN entries.
- Not done: `tools/log_step.py` (it writes outside the allowed directories), the python-reviewer pass, any commit.
