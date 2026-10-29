# Annotation handbook v2 proposal

**AI_DRAFT — synthetic engineering/review only; not the P1 annotation instrument.** Prepared 2026-10-28 under Parv's engineering/pilot instruction. No expert acceptance, H4 freeze, human annotation or source verification is asserted. The current Step19 design uses v0 + handbook v1/Addendum A for P1. This draft and the accompanying catalog are analyst-only until an explicit decision about exposure and instrument version. They must not silently prime a blind wave.

## Evidence and identity

Preserve exact raw text and offsets. Separate food concept, physical lot and state version. Keep a concept UNKNOWN if an exact registry identity is unresolved; a similar spelling is not sufficient identity evidence. Track source spans and stated/derived/unknown distinctions. Where selected schemas support metadata, require explicit per-claim metadata and record source verification separately; successful validation does not verify a claim. Do not backfill certainty, origin or verification from schema defaults.

The synthetic catalog is `hard_case_catalog_v2_DRAFT.jsonl`. Every entry is AI_DRAFT_SYNTHETIC, with a proposed invariant and reviewer fields pending; no entry is Gold or a human verdict. Synthetic ingredients and arbitrary numbers demonstrate arithmetic only, never scientific constants or real recipe facts.

## Quantity and alternatives

Keep exact fractions/ranges, explicit package counts and stated unit dimensions. Zero remains zero. Unknown is not zero. Count, mass and volume stay separate without an explicit justified conversion source. A named vessel does not license a standard volume. Retain raw qualifiers such as heaped, packed and level. Locale choices and conversion sources must be visible, never guessed from source name alone.

Nested packaging multiplies count by stated package content; a count plus mass for one item can describe the same lot. Alternatives describe choices, not simultaneous ingredients and not a product of quantities. Optionality remains conditional; it is not evidence the ingredient was used. Source contradictions remain visible, not averaged or silently resolved.

Synthetic prompt “Use a splash of the reserved liquid”: preserve qualitative unknown partial amount. Do not transfer the whole reserve or invent a volume. If the instrument cannot represent unknown partial transfer faithfully, keep the text, log QUANTITY_MODEL_GAP/BLOCKING and record the available encoding as a workaround only if it does not assert false consumption. New AST arithmetic does not by itself ground that phrase to a physical lot.

For synthetic “divide into four portions”, shares remain unknown unless equality is stated; “four equal portions” supports one quarter each. A remainder is relative to its named parent quantity and prior allocations. “Half the reserved portion” is one half of that reserve, not the original lot. Definite over-allocation is an error; a merely possible interval overrun is unresolved, not silently clamped.

## Entities, actions and time

Maintain parentage across split/reserve/recombine and composition across merge. Repeated mentions do not necessarily create new lots; a new food mention in a step is not permission to fabricate an ingredient-list amount. Ambiguous antecedents stay UNKNOWN with the alternatives recorded in notes when the instrument allows it.

Only textually unavoidable implicit actions may be considered, with the implicit status visible; log unsupported inference rather than completing a plausible cooking story. Text position is a deterministic serialization order, not evidence that “meanwhile” actions occurred sequentially. Preserve temporal/conditional cues and log schema gaps where they cannot be expressed.

Keep oven setpoint distinct from food core temperature. Preserve stated time ranges, raw qualitative duration and endpoint; an endpoint does not imply an invented time or measured state. A later source instruction that contradicts an earlier one remains a source conflict. Structural replay success cannot settle that conflict.

## Hard-case review rubric

For each of the17 SSOT237.5 classes exercised by the synthetic catalog, ask in order: What does the text state? What remains unknown or conflicting? Can this exact selected schema express it without inventing or dropping information? Does validation preserve the intended distinction? Does replay introduce unsupported quantity, identity, order or state? Record any disagreement between structural validity and semantic faithfulness.

Use FAITHFUL when every relevant stated claim and uncertainty is represented; WORKAROUND when a visible convention is required; IMPOSSIBLE when faithful representation requires invention, loss or an ad hoc field. IMPOSSIBLE maps to BLOCKING. Classify issues as quantity, coreference/entity, state variable, vocabulary, tooling, source defect or ambiguous handbook rule, and record affected field family and version. Successful parsing alone never earns FAITHFUL.

Review record fields: `review_id, case_id, status, reviewer_kind, reviewer_name, instrument_version, input_sha256, observed_output_reference, representability, category, severity, field_family, rationale, proposal, changed_paths, evidence_reference, verification_date, human_decision`. Agent records use reviewer_kind=AI_REVIEW and status=AI_DRAFT; human-only fields remain null. Keep expectations separate from actual observed results.

## Rehearsal and later human workflow

Engineering may use the synthetic catalog to test zero handling, interval/fraction arithmetic, alternatives, unknown partial flows, provenance and version boundaries. Record exact input/output hashes, code commit, test result and unresolved questions; no real recipe text or current pilot IDs. A synthetic success is a software observation, not Gold quality or IAA.

For the human pilot, follow the approved instrument and Step19 private packet protocol: own machine/account, blank files, no AI prefill or label repair, private write-only question log, timing and snapshots, commitments before sealed-key opening. Do not consult this analyst proposal or catalog inside a frozen wave unless explicitly part of the approved instrument. Review questions and new conventions only after both commitments. Preserve original labels and version any adjudicated revisions; never re-score exposed recipes as fresh independent data.

The assigned expert later verifies source/quantity/entity/temporal conventions, records accepted/rejected/amended proposals and supplies their own identity/date. Changes require explicit instrument/version impact assessment and fresh synthetic checks; a pilot instrument change also needs a design decision about new independent samples. No pending human-only field is completed by inference.
