# EXP-M3.1-AUX — MiniMax M3.1 Flash auxiliary utility evaluation: CLOSED (NO-GO), 2026-10-20

Free window: until 2026-10-22 23:59 UTC (model page). Access: https://ollama.com/api/chat, 1 concurrent request (free tier), no rate-limit headers, no HTTP 429 seen.
Data sent: TASTEset DEV (MIT) cases and project ledger vocabulary only. No Food.com, RecipeDB3 or BBC text was ever sent.

| Task | Result | Decision |
|---|---|---|
| 1. Constrained verifier on TASTEset DEV disagreements (base+CRF vs large+CRF) | prompt v1 (10 cases): 0/5 neither-right cases declined. Prompt v2, train-only few-shot (60 prompt-dev cases): 16/29 right on one-right-side cases (55%, equal to the best trivial rule, always-A 55%), 11 wrong commits, 7/31 neither-right cases declined. EVAL split never touched. 70 calls. | NO-GO |
| 6. Ledger audit | not completed: first attempts failed silently (model "thinking" tokens consumed the output cap, empty answers logged as OK). Fixed, but stopped by decision before results. | not pursued |
| 5. Linker augmentation, 2/3/4/7/8 (taxonomy, silver, adversarial, code review) | not run | not pursued |

Reasons: (1) the verifier did not beat a trivial baseline, (2) the model does not follow TASTEset's annotation conventions (the dataset itself is inconsistent), so any silver labels from it would be noisy, (3) every result that decides CulinaryNER-KF (RecipeDB3 confirmation, linker, calibration) is GPU-side and not accelerated by it.
Does not change any planned experiment. Code kept for reproducibility: tools/m31_verifier_pilot.py, m31_ledger_audit.py, m31_linker_augment.py (+ linker_train.py --aug flag, unused).
Lessons: reasoning tokens count against num_predict even with think=false; record real call status in the ledger; the single-slot queue blocks if an earlier long request is killed client-side.
