# Report wording — three states per gap

**`AI_DRAFTED`.** Paste the sentence that matches the facts on the day; fill every `<...>`. If no human
acts, state (a) is the only one that may be used. Never write "verified", "chef-reviewed" or
"peer-reviewed" about an AI pass.

## D1 — ≥40 hand-verified literature rows

**(a) Only AI personas have checked:**
"Forty candidate literature rows (16 kinetics, 24 raw-versus-cooked) were pre-checked by AI personas
under D-085: 28 were compared against an opened source and 12 sources could not be opened. No row has
been verified by a human, so the ≥40 hand-verified rows required by the proposal are not met; the
ledger records 0 human-verified rows."

**(b) Humans audited all 40:**
"<n ≥ 40> literature rows were hand-verified by <Kush and/or Parv> on <date> against the primary paper,
with a table or page locator recorded for each: <c> confirmed, <k> corrected, <r> rejected. The
pre-check of these rows was AI-assisted (D-085); the verification is human."

**(c) Partial:**
"<n> of the required 40 literature rows were hand-verified by <names> on <date> (<c> confirmed,
<k> corrected, <r> rejected); the remaining <40 − n> were pre-checked by AI personas only and are not
counted as verified. The ≥40 requirement is therefore not met."

If the potato rows are audited, add: "One import defect was found: <n> rows carry absolute values on the
wrong mass basis (retention ratio unaffected)." Only if a human confirms it.

## D3 — 40 gold recipes

**(a) No human action:**
"D3 was evaluated on 40 development gold recipes (20 BBC Good Food, 20 Food.com) and 7 pilot recipes.
This gold was drafted by an AI and accepted by the authors; it is not independent, not blind and not
held out, and the engine was developed with part of it in view. On it the rule compiler matched 11–20 %
of final state fields, reached merge/split F1 0.36–0.47, and replayed without issue. These are
diagnostic figures, not an accuracy claim."

**(b) Humans spot-audited the gold:**
As (a), then: "On <date>, <names> re-read <n> of the 40 gold recipes against the recipe text and agreed
with <a> of <f> gold state fields and <b> of <e> merge/split events. The gold remains non-independent."

**(c) Partial:**
As (a), then: "A human spot-audit of <n> recipes was started but not completed; no agreement figure is
reported."

Do not use the compliance matrix's "the 40-gold-recipe scoring … was not performed" — a scoring on
non-independent dev gold exists (`reports/del3/compiler_vs_gold_pooled_S179.md`).

## D5 — small chef/peer review

**(a) Only AI personas have reviewed:**
"The eight scenarios were pre-reviewed by three AI personas (structure, food science, working cook)
under D-085. This is not the chef/peer review named in the proposal, which was not performed."

**(b) A human chef has audited all eight:**
"The eight demo scenarios were reviewed on <date> by <n> human reviewer(s), including a <role, e.g.
professional cook with N years in restaurant kitchens>, using a four-question rubric (correctness as
cooking advice, caution level, disputed statements, trust). The reviewer agreed with <a> of 8 AI
pre-review judgements and overturned <o>. In all eight scenarios the system declined or asked rather
than advised; the reviewer judged <x> of those refusals appropriate."
(Name the reviewer only if they ticked consent in the sign-off block.)

**(c) Partial:**
"<k> of the eight scenarios were reviewed on <date> by a <role>; they agreed with <a> and overturned
<o> of the <k> AI pre-review judgements. The remaining <8 − k> were pre-reviewed by AI personas only.
This is a partial chef review, smaller than the proposal describes."
