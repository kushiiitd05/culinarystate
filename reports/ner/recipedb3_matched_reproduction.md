# RecipeDB3 NER matched reproduction + clean grouped control (A100)

Scientific control, NOT our final NER: plain `microsoft/deberta-base` token classification, no CRF, 15 epochs, lr 5e-5, bs 16, max_len 128, bf16 off (fp32), AdamW. No SOTA / superiority claim before H6.

Dataset sha256 `09f61f8f30cf2507…`; repro.py sha256 `f8f4e13558d6b4a8…`; GPU: NVIDIA A100 (shared). Per-seed JSONs in `reports/ner/_raw/`; aggregates `reports/ner/recipedb3_control_summary.json`. Two early runs (theirs seed 48, clean seed 1) were launched before per-label scores and runtimes were logged, so per-label means use 4 of 5 seeds in each protocol.

## Results (test, checkpoint-at-best unless stated)

| Protocol | Selection | Seeds | Macro F1 | Micro F1 | Last-epoch macro |
|---|---|---|---|---|---|
| Their notebook (random 80/20) | test | 5 | 0.9543 ± 0.0020 (95% CI 0.9518–0.9567, n=5) | 0.9603 | 0.9484 |
| Clean (80/10/10, masked-sentence-family grouped) | dev | 5 | 0.9504 ± 0.0034 (95% CI 0.9461–0.9546, n=5) | 0.9594 | 0.9529 |

## Answers

1. **Did the matched reproduction reach the published-value region?** Yes. Notebook (seed 48, final epoch) reports macro 0.9557 / micro 0.9603; our seed 48 gives macro 0.9533 (best-on-test) / micro 0.9620, and the 5-seed mean is 0.9543, within one seed-SD of the published number.
2. **Effect of proper dev-set selection.** Choosing the checkpoint on TEST (their protocol) inflates macro F1 relative to its own last epoch: 0.9543 vs 0.9484. On the clean split, selecting on dev gives 0.9504 (last epoch 0.9529); there the best-on-dev checkpoint is slightly below the last epoch, i.e. no test-selection optimism remains.
3. **Effect of the family-grouped split.** Theirs − clean = +0.0039 macro F1 (Welch p = 0.0674), small and not significant at 5 seeds; the clean split removes leakage but the headline barely moves because most rows are non-leaked.
4. **Leaked vs non-leaked.** In their protocol 13.6% of test rows share a masked family with train and 5.4% are exact duplicates. Leaked rows score micro F1 0.9937; non-leaked rows 0.9558 (clean split: 0.9594, 0% leakage). The headline is flattered by about 0.45 micro-F1 points.
5. **Effect of restoring SIZE.** Paired over seeds [1, 2, 3]: macro delta +0.0008 (per seed [0.002, -0.0019, 0.0022]). macro averages over 7 labels with SIZE vs 6 without, so compare per-label F1 and micro too. See the per-label table below for SIZE itself.
6. **Fair baseline for our new system.** DeBERTa-base on the *frozen benchmark v1* split (`benchmark/ner/`), because the control's per-seed random splits differ from the frozen one. The clean 5-seed mean above is the reference number for context; the S119 comparisons retrain every candidate on the frozen split with the same budget.

## Per-label F1 (mean over seeds that logged it)

| Label | Theirs | Clean |
|---|---|---|
| DF | 0.9624 | 0.9607 |
| NAME | 0.9297 | 0.9311 |
| QUANTITY | 0.9885 | 0.9876 |
| STATE | 0.9462 | 0.9444 |
| TEMP | 0.9238 | 0.9024 |
| UNIT | 0.9764 | 0.9785 |

Clean + SIZE (n=3): macro 0.9524 ± 0.0019 (95% CI 0.9476–0.9572, n=3); per-label {'DF': 0.9604, 'NAME': 0.926, 'QUANTITY': 0.987, 'SIZE': 0.953, 'STATE': 0.9433, 'TEMP': 0.921, 'UNIT': 0.976}

## Per-seed table

| Protocol | Seed | Sel | Best ep | Macro | Micro | Last macro | Leaked frac | Runtime s |
|---|---|---|---|---|---|---|---|---|
| clean | 1 | DEV | 14 | 0.9486 | 0.9564 | 0.9500 | 0.000 | None |
| clean | 2 | DEV | 15 | 0.9564 | 0.9621 | 0.9564 | 0.000 | 5431 |
| clean | 3 | DEV | 14 | 0.9499 | 0.9586 | 0.9556 | 0.000 | 5474 |
| clean | 4 | DEV | 13 | 0.9481 | 0.9589 | 0.9536 | 0.000 | 2573 |
| clean | 5 | DEV | 15 | 0.9488 | 0.9610 | 0.9488 | 0.000 | 2408 |
| clean_size | 1 | DEV | 12 | 0.9506 | 0.9554 | 0.9525 | 0.000 | 6287 |
| clean_size | 2 | DEV | 10 | 0.9544 | 0.9612 | 0.9541 | 0.000 | 4534 |
| clean_size | 3 | DEV | 11 | 0.9521 | 0.9565 | 0.9529 | 0.000 | 6291 |
| theirs | 1 | TEST | 10 | 0.9572 | 0.9632 | 0.9461 | 0.142 | 5875 |
| theirs | 2 | TEST | 12 | 0.9549 | 0.9594 | 0.9457 | 0.136 | 5864 |
| theirs | 3 | TEST | 13 | 0.9540 | 0.9589 | 0.9482 | 0.137 | 2553 |
| theirs | 4 | TEST | 15 | 0.9518 | 0.9580 | 0.9518 | 0.133 | 2598 |
| theirs | 48 | TEST | 14 | 0.9533 | 0.9620 | 0.9500 | 0.134 | None |

## Caveats
- Single dataset, one architecture; BIO conversion assumes consecutive identical tags form one entity (their BIO file is not released).
- Runs shared an A100 with other users; runtimes are not comparable across seeds.
- Two duplicated launcher loops ran for part of the sweep (no seed was run twice; the redundant loop was stopped at 12:24 IST).
