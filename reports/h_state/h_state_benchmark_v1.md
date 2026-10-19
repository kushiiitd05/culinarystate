# H_STATE benchmark v1 — authoring pack status (EXP-000007)

**Status: BLOCKED_HUMAN.** Pack, template and validator are built; the 80 question sentences must be written by Kush. No question was generated, no B3/B4 was run, nothing is frozen.

## Built
- `benchmark/h_state/authoring_pack/<recipe>.json` (local; recipe text): per recipe one cut point, the Gold-v1.1 alive state at the cut (quantity, location, fields, base ingredients), events applied/remaining, steps up to the cut, eligible evidence cells.
- `benchmark/h_state/authoring_manifest.csv` (text-free): recipe, family, cut event index, cut step, `gold_state_hash`, events applied/remaining, alive entities, eligible evidence cells.
- `benchmark/h_state/questions_to_write.csv`: 80 slots (20 recipes x Q1-Q3 STATE_DEPENDENT + Q4 CONTROL), prefilled ids/hash/class; `question_text`, `state_information_required`, `gold_mode`, `gold_evidence_cell`, `acceptable_answer_semantics`, `why_state_is_required`, `author` are blank for Kush.
- `tools/validate_hstate_questions.py` (+2 tests): 80 rows, 3+1 per recipe, author Kush, valid mode, evidence = known EVD id(s) or UNSUPPORTED, no near-duplicates, STATE_DEPENDENT questions must not let the production parser recover both an ingredient and a process from the text alone, CONTROL questions must state both. Exits 2 (BLOCKED_HUMAN) while empty.

## Cut-point rule (fixed before any system output; not by difficulty or pronouns)
After n of the N non-Add Gold events, n in [1, N-1], maximising min(n, N-n) (the middle), ties to the smaller n, with at least one derived entity alive. All 20 recipes yield a cut.

## Finding that needs a decision before authoring: ledger evidence is thin for these 20 recipes
Evidence cells are (ingredient, process, target) retention rows. Checked across **all** possible cut points:
- only **10 of 20 recipes** have any ingredient x process pair with a retention cell (R000387 onion/fry, R001894 cheese/bake, R003595 egg/milk/fruit, R006967 chickpea/boil, R007363 onion/tomato/fry, R008469 carrot/onion/boil, R010426 sprouts/beans/boil, R011207 egg/fry), and several are loose matches;
- at the chosen middle cuts only **5 recipes** (R000387, R006967, R007363, R008469, R010426) have a cell in the cut-time state;
- the EXP-000007 card planned >=40 supported questions among 60. With this ledger the supported subset is at most about 30 and realistically 15-25.
This is a ledger-coverage limit, not a design error, and it is known before any system is run. Options for Kush:
(a) keep the 20 recipes and treat most items as UNSUPPORTED/ABSTAIN/ASK (still valid, tests abstention; CC@5 then rests on about 15-25 supported questions: report the wider CI);
(b) re-cut the 10 evidence-bearing recipes at cuts that carry an evidence cell and write the other 10 as abstention items (rule change stated now, before authoring: "prefer a cut with an eligible cell");
(c) add 8-10 new recipes whose ingredients and processes the ledger covers (vegetables boiled, steamed, fried) and Gold-annotate them first (more human work, best statistical power).
Recommendation: (b) now, (c) later if H_STATE looks promising.

## Final report fields (all empty until Kush writes the questions)
recipes represented 20/20 (slots) · state-dependent 0/60 · controls 0/20 · human-authored 0/80 · supported / unsupported / state-field and mode distributions: not yet · benchmark frozen: no.
Next: Kush chooses (a), (b) or (c), then writes the questions into `questions_to_write.csv`; run `tools/validate_hstate_questions.py`; freeze only after it prints OK.
