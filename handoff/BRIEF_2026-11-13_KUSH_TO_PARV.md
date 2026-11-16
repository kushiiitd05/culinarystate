# Brief — Kush → Parv, 13 Nov 2026 (supersedes the "remaining" list in PARV_TECHNICAL_CLOSEOUT_2026-11-13.md)

Pull first: `git pull --ff-only` on `kush/s179-finish-fixes`. Decisions now run to **D-097a**; Kush's session takes **D-098** (ablations). **Your next decision number is D-099.** Pull before appending to DECISIONS / WORKLOG / STATUS / compute_runs.

## 1. Your blockers are closed (they were on Kush's Mac / vinayak, not missing)

| Your blocker | Where it was (sha256 verified) | Result now |
|---|---|---|
| NER `ckpt_tasteset_base_crf_s1.pt` 582c056ac20625ac | vinayak `~/Kush/culinarystate-ner-bench/`; bound spans `~/Kush/cs_runs/ner_*_S174.jsonl` | T3-C09-R1 done: `reports/s179/ner_vs_runga_agreement_S179_2026-11-13.json` |
| 15a seed + sealed list | Kush's Mac `~/.culinarystate_private/` (never leaves it) | seal 6/6 PASS; T9-C09-R1 done: `registry/split_registry_15a_v1.csv` |
| Accepted P1 annotator-A Gold | Kush's Mac `annotation/gold/deep_gold_pilot_v1/A/` (7, git-ignored) | T3-C11-R1 done via D-097: `reports/s179/d097_runga_type_table_2026-11-13.json` |
| frozen qwen2.5:7b-instruct 845dbda0 | vinayak ollama | used for D-098 ablations / B7 (Kush's session) |
| matched paired contrasts | needed the seal (Mac) | T6-C02-R3 done: `reports/step29/diag/paired_vs_d0_S179_2026-11-13.json` |

Kush reviewed these four results: **ok all** (review sheet block K13, D-097a). Labels unchanged (DIAGNOSTIC / NOT_INDEPENDENT / NON_CITABLE).

## 2. Status after 13 Nov (252 items; 51 POST unchanged)

| | Done | Author edits | Open, data-limited | Not run by decision / needs independent human | Calendar |
|---|---|---|---|---|---|
| MUST (84) | 52 | 12 | 10 | 7 | 3 |
| SHOULD (168) | 88 | 11 | 14 | 4 | — (51 POST) |

## 3. Kush's session is doing (do NOT touch these files)

T3-C17-R2 figure (D-097 intervals), T3-C20-R1 duplicate control (needs the seal), T8-C21-R2 ablations under D-098 and T9-C24-R2 H1/B7 regeneration (both vinayak, frozen 7b), T8-C06-R1 source-held-out retrieval diagnostic if feasible.

## 4. Your work (no server needed)

1. **Records:** dated v2 of the scope matrix and a dependency-check supersession note for `local_model_and_seal_dependencies_2026-11-13.json` (new files; never overwrite v1). Pull Kush's latest first.
2. **Report + deck drafts:** add the 13 Nov numbers with their labels (Phenol-Explorer rungs worse than D0 = negative result, keep it); re-run the number-class lint (T9-C20-R1).
3. **Human-only items you can close:**
   - T2-C09-R2/R3, T2-C07-R2, T2-C18-R1: browser-download AAK-02/04/05/08/10, confirm CC-BY/CC0 or drop and record.
   - **T8-C16-R1:** blind human judge, ≥30 pre-declared claims across rungs, blind to rung and checker output (needs a real human; D-085 cannot cover it).
   - **T2-C05-R1..R4 (4 MUST):** 07.A-R1 was NOT_RUN only because AI personas are not inter-rater evidence. If Kush and you each label your 100-row packet (`annotation/condition_audit/condition_audit_packet_100_R1_{Kush,Parv}.csv`, ~1–2 h each, blind), it can be scored under the existing prereg. Sign the prereg first (human signature).
   - Your author facts, contributions and your report/deck sections (D-094).
4. Timed rehearsal script with the `run_local_demo_v3.py` fallback; get PRs #12 and #11 merge-ready.
5. No new diagnostic lanes.

## 5. Stays open — present as limitations, do not try to close

AA assay/basis/PARAM/SIM-VAL provenance (T2-C02, T2-C09-R4, T4-C14-R3, T4-C21-R1, T5-C01/C05/C07/C08/C10/C11): 0 SIM-VAL eligible, 0 G15 PASS. T0-C06-R2 frozen-answer flags. T8-C01-R1 independent branch Gold. T0-C17-R1 endpoint permission fact (Kush). Recorded deferrals T3-C04-R3, T3-C08-R1, T6-C04-R1, T8-C08-R1.

Labels: AI_PRECHECKED · NON_CITABLE · NO_HUMAN_SIGNOFF_D085 except where a human verdict is recorded.
