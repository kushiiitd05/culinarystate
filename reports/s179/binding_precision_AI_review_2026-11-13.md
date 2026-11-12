# Prehashed100-case binder field review — 13 November 2026

**AI_CHECKED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.** Author-only review (AI-delegated), not human gold or independent inter-rater evidence. Sample selected before source reading: seed20261104,25events each from DRY_HEAT/FAT_HEAT/HEAT_GENERAL/WET_HEAT, Wikibooks only. Public manifest binds selected IDs/producer-row hashes; raw source packet and per-case manual labels remain ignored under data/raw.

| Field | Matches / adjudicated | Conditional precision / Wilson95% | Other100-case dispositions |
|---|---:|---|---|
| Temperature numeric fidelity |10/10|1.000 [0.7225,1.000]|16NON_TEXT_BASIS;74NOT_BOUND|
| Unit/conversion fidelity |37/37|1.000 [0.9059,1.000]|63NOT_BOUND|
| Duration/ownership |30/33|0.9091 [0.7643,0.9686]|66NOT_BOUND;1UNASSESSABLE|
| Medium literal-text extraction |0/0|null interval;unmeasured|70PROCESS_DEFINITION;30NOT_BOUND|
| Event attribution |72/92|0.7826 [0.6879,0.8546]|8UNASSESSABLE|

All100event sentences and every TEXT_STATED numeric-axis fragment/context were read by the root AI after the selection prehash. Obvious noun/adjective/prior-state/negated-event cases are retained as mismatches. Event-sense/ownership ambiguity is UNASSESSABLE, not an automatic match. The three duration mismatches are per-side rather than total duration (BINDREV022), duration attached to a negated boiling mention (076), and duration attached to an endpoint adjective rather than the primary baking action (086). Case063 has ambiguous ownership across heating oil and softening onion. No binder or locked scientific rule was tuned after this review.

The high conditional numeric scores do not represent overall binder accuracy: most axes are absent or based on process definitions, extraction recall is not measured, source qualifier/temperature-location correctness is not certified, and event precision is much lower. Paired Fahrenheit/Celsius text can itself be internally inconsistent; checking the chosen Fahrenheit conversion does not certify the source or the other printed unit. Wilson intervals describe these AI decisions and do not account for within-recipe dependence or systematic AI bias. This sample cannot establish source-family generalization.

The first prepare attempt retained its manifest but failed before source packet creation due an import path. The correctedv2 manifest was created before the successful packet/source review; selection IDs are unchanged. Two diagnostic-helper defects were fixed before review: import the existing SourceText from extraction.interfaces; clamp exact Wilson endpoints for0/n and n/n to avoid floating-point endpoint noise. Three selection/rubric tests pass. Original Binder/scenario sources and all frozen outputs are unchanged.

Full machine-readable counts, private packet/review hashes and preselection hash: `binding_precision_AI_review_2026-11-13.json`; selection `binding_precision_manifest_2026-11-13_v2.json`. The completed artifact satisfies an AI field-review diagnostic, not a scientific or human gate pass. It supplies a concrete error queue for later expert review.
