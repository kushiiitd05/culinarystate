# Amendments to `external_validation_protocol.md`

## EXT-A1 (2026-10-21) -- supervisor constraint: external text may come only through a recipe API
Trigger: the supervisor indicated that only recipe-API access is available (no downloadable labelled corpus). No external data has been accessed, converted or scored; this amendment precedes all of it.

**What changes**
1. **Route.** Section 2 candidates EXT-A (labelled ingredient-phrase corpus) and EXT-B (FoodBase) become *dormant*: they are used only if a labelled corpus later becomes legitimately obtainable (then the original protocol applies unchanged). The primary route becomes **EXT-API**: recipe text fetched through one recipe API, labelled by us.
2. **An API supplies text, not gold labels.** H1-H3, H5, H6 need span labels, so a **human-labelled sample** is mandatory: >= 1,200 ingredient phrases (stratified; unseen NAME surfaces over-sampled using input text and the train gazetteer only, never model scores), labelled independently by Kush and Parv in the benchmark schema (FOOD/NAME, QUANTITY, UNIT, plus STATE for the RecipeDB3-trained pipeline), adjudicated. The double annotation also gives the annotation-noise ceiling (original section 11). Sizing: about 3,500 core spans -> about 2,400 ACCEPTed (QUANTITY/UNIT ~99% accepted, NAME ~67%) -> pooled n_accept >= 750 is met; per-label verdicts for QUANTITY, UNIT and NAME are possible; STATE/DF-type labels stay descriptive.
3. **A large unlabelled pool** (>= 10,000 phrases, quota permitting) is scored **label-free**: ACCEPT/REVIEW/REJECT rates, unseen-mention rate, confidence-score KS shift, linker top-1 cosine shift, advisory-NOVEL tag rate. This tests whether routing *behaviour* and coverage shift; it says nothing about error and is never reported as validation of the 2% tolerance.
4. **Single new domain.** One API = one source family, so the "H3 PASS on >= 2 of 3 shifted sources" rule is replaced: **TRANSFERS** if H1 not FAIL, H2 PASS, and H3 PASS both pooled and on seen mentions; **PARTIAL** if H3 passes only on seen mentions or is INCONCLUSIVE for size; **DOES NOT TRANSFER** if H3 FAIL pooled. The Holm family becomes {H1, H2, H3, H5}. A single source cannot separate "domain shift" from "this API's idiosyncrasies"; that is a stated limitation.
5. **H4 (unseen accepted)** will almost surely be descriptive: only ~2-11% of unseen spans are ACCEPTed in v1, so 400 unseen NAME spans give ~8-44 accepted. Reported with exact intervals, no pass/fail.
6. **H7 linker.** The 400-mention ledger-ID sub-study draws its mentions from the same labelled sample (FOOD spans, ledger concept ID or NIL, 200 unseen / 200 seen). No BBC-derived text.
7. **Minimum viable tier** if time is short (presentation 25-26 Nov): 600 labelled phrases -> every result descriptive (no PASS/FAIL verdicts), reported with exact intervals and labelled as pilot.

**API eligibility gate G1' (must be VERIFIED before any fetch)**
| API | What it returns | Concern |
|---|---|---|
| Spoonacular | `extendedIngredients[].original` free-text phrases + instructions | terms of use on storing/caching not read yet (only third-party advice to cache); quota/points must be checked against the 10,000-phrase target |
| Edamam Recipe Search | `ingredientLines`, link to source for instructions | its own documentation says the Recipe Search API does **not allow caching**, which makes repeat annotation/scoring a terms violation unless a licensed data dump is used -> **not eligible as is** |
| TheMealDB | numbered `strIngredient1..20` / `strMeasure1..20` fields + free-text instructions | ingredients are pre-split fields, not natural phrases (recombining "measure + ingredient" is a synthetic format -> a different, easier task); small catalogue |
Rules: read and record the API terms (URL, date, hash), confirm research use + local storage are permitted, keep fetched text local and git-ignored, never send it to an external service, never push (H7). If no API passes G1', the external-domain claim stays **unavailable** and H6-C stands unchanged.

**What this amendment does not change:** the frozen system, thresholds, success numbers (section 9), the one-look rule, the post-evaluation restrictions (section 12), and the checkpoint reproduction gate (section 3).
