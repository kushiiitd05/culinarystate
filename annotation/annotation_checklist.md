# Annotation checklist (run through before marking a file DONE)

- [ ] Annotated alone; no LLM pre-fill; did not open the other annotator's file.
- [ ] Every ingredient line has `entity` (unique) and `concept` (registry name or `UNKNOWN`).
- [ ] Quantities: only written numbers are QUANTITY spans; no quantity added to "to taste"/"for frying".
- [ ] Optional / alternative lines flagged (`optional`, `alternatives`).
- [ ] Every process verb in steps is an ACTION span and has a matching event (or a note why not).
- [ ] Intermediates have new entity labels (roux, batter, dressing) created by Merge.
- [ ] Reserve / remaining / reserved / set aside → Reserve + later coref/Recombine.
- [ ] Drain / discard / strain → Split and/or Discard (what is kept, what is thrown away).
- [ ] Oven temperatures are one TEMPERATURE span; never treated as core temperature.
- [ ] Endpoints ("until golden") recorded as ENDPOINT span + `endpoint` field; no invented times.
- [ ] Implicit events marked `"implicit": true` and only when unavoidable.
- [ ] Coreference: definite NPs, repeats and pronouns linked to entity labels; unclear → `UNKNOWN` + note.
- [ ] `unknowns` lists every important fact the recipe leaves unstated.
- [ ] `python tools/gold_cli.py validate <file>` prints OK (offsets, schema, events, replay with no issues).
