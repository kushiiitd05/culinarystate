# Gold Annotation Handbook v1 — CulinaryState (Kush + Parv)

**Purpose:** produce independent, double-annotated Gold recipes for DEL-3 (≥ 40 recipes, course minimum) and
the semantic parser. Gold files compile directly into state-engine events, so every rule below has a
visible consequence in the replayed state graph.

**Golden rules**
1. Annotate what the text **says**. If it is not stated, the answer is **UNKNOWN** — never a guess.
2. Annotate **independently**. No LLM pre-fill, no looking at the other person's file before both are DONE.
3. Raw text is never edited. Offsets point into the exact text.
4. One file per recipe per annotator: `annotation/gold/<recipe_id>.<Kush|Parv>.json`.
5. When unsure, write it in `unknowns` or `notes` and flag for adjudication — do not silently choose.

Tools: `python tools/gold_cli.py validate <file>`; `python tools/gold_cli.py agree <A.json> <B.json>`
(writes the adjudication sheet). Worked examples: `annotation/examples/GOLD-EX-00{1,2,3}.Kush.json`.

---

## 1. Three identities (never collapse)

| Layer | Field | Example |
|---|---|---|
| Concept (what food) | `concept` | `unsalted butter` (canonical name from `registry/ingredients/ingredient_registry_v1.csv`, or `UNKNOWN`) |
| Entity (this physical lot) | `entity` | `butter`, later `greasing butter`, `roux` |
| Version (state at a moment) | produced by events | `butter@0` → melted `butter@2` → … |

Entity labels are short, unique per recipe, lowercase. Intermediates get new labels (`roux`, `batter`,
`tray veg`). Re-use the **same entity label** for coreference targets.

## 2. Ingredient lines

For each line: `spans`, `entity`, `concept`, optional `optional`, `alternatives`, `quantity_override`.

- `50g unsalted butter` → QUANTITY `50`, UNIT `g`, FOOD `unsalted butter`; concept `unsalted butter`.
- `2 large carrots` → QUANTITY `2`, SIZE `large`, FOOD `carrots`; concept `carrot` (singular canonical).
- `1 red onion, cut into wedges` → FORM `cut into wedges` (prep written in the line is FORM).
- `pinch of grated nutmeg (optional)` → UNIT `pinch`, FORM `grated`, FOOD `nutmeg`, OPTIONAL `optional`; `optional: true`.
- `butter or margarine` → FOOD `butter`, ALTERNATIVE `margarine`; `alternatives: ["margarine"]`, concept = first-listed.
- `2 x 400g cans chopped tomatoes` → QUANTITY `2`, QUANTITY `400`, UNIT `g`, UNIT `cans`, FORM `chopped`, FOOD `tomatoes`.
- `juice of 1 lemon` → FORM `juice`, QUANTITY `1`, FOOD `lemon`; concept `lemon juice` if the registry has it, else `lemon`.
- No quantity written (`salt, to taste`) → no QUANTITY span. Never add one.
- `quantity_override`: only if the line misleads the parser (e.g. two quantities for two foods on one line); write the
  amount text for *this* entity, e.g. `"1 onion"`. Explain in `notes`.

## 3. Span labels (steps and lines)

| Label | Mark | Do not mark |
|---|---|---|
| FOOD | food mention | pronouns (`it`) → coref only |
| QUANTITY | number/range/fraction text | words like "some" (→ UNKNOWN) |
| UNIT | g, tbsp, can, clove, pinch, mugful | size words |
| SIZE | small/medium/large/thick | |
| FORM | chopped, sliced, grated, wedges, chunks | cooking state (→ STATE) |
| STATE | melted, softened, at room temperature, frozen, cooked | |
| ACTION | each process verb: melt, stir, whisk, drain, roast | auxiliary verbs |
| TOOL | saucepan, oven, baking tray, food processor | |
| MEDIUM | boiling water, hot oil, stock (as cooking medium) | |
| TIME | 2 mins, 35–40 mins, overnight | |
| TEMPERATURE | 200C/180C fan/gas 6, low heat, 70 °C core | |
| ENDPOINT | until golden, until thick enough to coat a spoon | |
| INTERMEDIATE | a named product of earlier steps: roux, batter, dressing | |
| OPTIONAL / ALTERNATIVE | "(optional)", "if using" / "or X" | |

**Temperatures:** `200C/180C fan/gas 6` is **one** TEMPERATURE span (three equivalent oven setpoints). An oven setpoint is
never the food's core temperature. "low/medium/high heat" is qualitative — mark it, never convert to °C.

## 4. Events (one or more per step)

Events are what the state engine replays. Use exactly these types and fields:

| Type | Required fields | Meaning | Example |
|---|---|---|---|
| Transform | target, process (+ time, temperature, endpoint, tool, medium, sets) | same entity changes state | `Cut the carrots into chunks` |
| Merge | inputs[], output, process | ≥1 entities combine → new intermediate | flour + butter → `roux` |
| Split | target, outputs[{label, fraction}] | one entity divides; fraction `"1/4"` or `null` if unstated | `Divide the dough into 4` |
| Reserve | target, output, portion *or* fraction | set aside part; rest stays as target | `spoon out 1 tbsp and set aside` |
| Discard | target (+ portion/fraction, value) | throw away all or part | `Drain` (discard water) |
| Recombine | target (= reserved entity), output (= destination) | reserved part goes back | `add a splash of the reserved water` |
| Transfer | target, location | moves to tool/location | `Tip into a baking tray`, implicit `into the oven` |
| Observe | target, field, value | **session only**: what the cook reports | not used for recipe text |

Rules:
- **Order** events as they happen in the step.
- **Implicit** events (not written but required, e.g. putting the tray in the oven) get `"implicit": true`.
  Only add them when the text makes them unavoidable; otherwise write a note.
- `sets` records observable state the text asserts: `{"form": "chunks"}`, `{"phase": "melted"}`, `{"colour": "golden"}`.
- Endpoint words go in `endpoint` and as an ENDPOINT span. Do not invent times for endpoints.
- `Drain, reserving a mugful of water` = Split (pasta / cooking water) → Reserve (1 mug) → Discard (rest).
- "the remaining butter" after a Reserve = coref to `butter` (the remainder is the same entity, new version).
- Fractions only when stated (`half` → `"1/2"`, `into 8` → eight outputs of `"1/8"` **only if** "equal" or obvious
  division; otherwise `null`).

## 5. Coreference

In each step, list mentions that refer to an existing entity: `{"mention": "the remaining butter", "start", "end",
"entity": "butter"}`. Include definite NPs (`the mixture`, `the sauce`), bare repeats (`onion`), and intermediate names.
Pronouns (`it`, `them`) are coref mentions too. If the antecedent is unclear → entity `UNKNOWN` and a note.

## 6. UNKNOWN policy (most important)

Write UNKNOWN / leave empty when the text does not state it. Record non-obvious gaps in `unknowns`.
See `annotation/UNKNOWN_examples.md`. Examples: grams of `2 large carrots`; volume of `a mugful`; how much of the
reserved water is used; core temperature when only the oven setpoint is given; which salt; heat level.

## 7. Workflow and time budget

1. Pick recipes from `annotation/batches/` (stratified: easy / reserve-split / multi-component / Indian / baking).
2. Annotate alone (target 15–25 min per recipe). Run `validate` until it prints `OK`.
3. When both files are DONE: `agree` → `annotation/adjudication/<recipe_id>.csv`. Meet weekly; fill `adjudicated`,
   `rationale`, `handbook_rule`. Produce `<recipe_id>.ADJUDICATED.json`.
4. Every disagreement class that recurs ≥ 3 times becomes a handbook rule (v1.1, v1.2 …) with an example.
5. Report agreement per batch (span F1, char κ, concept agreement, merge/split F1) in `reports/gold_agreement.md`.

Targets (plan AH6): pilot 20 hard recipes → course Deep Gold ≥ 40 double-annotated → Gold-Light 100–160 → 30 scripted sessions.

## 8. What AI may and may not do

- May: draft this handbook, compute offsets, validate, compute agreement, propose *candidate* annotations for
  Silver data (never Gold).
- May not: pre-fill Gold, adjudicate, or be named as annotator/verifier. AI review is never human verification.

See also `annotation/annotation_checklist.md`, `annotation/hard_examples.md`, `annotation/adjudication_template.csv`.
