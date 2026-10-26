# H4 answers log (Kush), step-by-step walk-through

Records the answers Kush gave in the 2026-10-26 session, in order. These are Kush's answers, entered by Claude as the scribe. Nothing here is signed until Kush sets `signed_by` / `signed_at` in the registry files, and nothing here authorises Step 08a (that is a separate written line in `DECISIONS.md`).

| # | Question | Kush's answer | Date | Status |
|---|---|---|---|---|
| 1 | Where does Step 08a run? | "vinayak server if heavy, else Mac". 08a is estimated at CPU seconds to minutes, so it runs on the Mac; vinayak (A100 host, confirm VPN first) only if a run proves heavy. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 2 | Baseline sha256 of the seven ledger files (no human input needed) | Recorded by Claude in `registry/baseline_ledger_hashes_08a_v1.csv`. EVD, COND, SRC and MEAS match the hashes recorded earlier; STUDY, SNAP and `_ids` are new baselines. | 2026-10-26 | DONE (to be re-checked immediately before any 08a write) |
| 3 | Must `registry/data_source_acquisition_manifest_v1_1.csv` exist before 08a runs? | No, the v1 manifest is enough; v1.1 is built later as step 06.3-min. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 4 | Approve the Step 04.1 entity chain (SRC > DOC > STUDY > SEXP > SMP > OBS > AGG/DRV) and typed edges as drafted in `reports/step04/lineage_contract_v1_1.md` section 1? | Approved the chain. The sub-choices D-11..D-17 are asked one by one next. | 2026-10-26 | ANSWERED (main design only), not yet in DECISIONS.md |
| 5 | 04.1 D-2: AGG/DRV storage | Accept default: extra fields on export-v2 rows, no separate ledgers. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 6 | 04.1 D-3: reserve LROOT-, CGRID-, DFORM- | Accept default: reserve all three. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 7 | 04.1 D-4: same-lab grouping only in optional strict tier; shared-reference grouping default | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 8 | 04.1 D-5: UNKNOWN independence rows TRAIN-only | Accept the stricter rule. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 9 | 04.1 D-6: port approved schemas into `registry.py` at 08a | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 10 | 04.1 D-8: unidentifiable-member aggregate = one lineage root per release | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 11 | 04.1 D-9 and D-10: STUDY authoritative for DOC-STUDY links; Phenol-Explorer = PUBLICATION_ONLY | Accept both. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 12 | 04.1 D-11: DOC mint key `<src_id>|sha256:<hex>` | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 13 | 04.1 D-12: hub rule | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 14 | 04.1 D-13: UNKNOWN leakage screen plus sensitivity run | Accept default. Threshold value THR-08A-19 stays OPEN (must be set before that gate row can be signed). | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 15 | 04.1 D-14: giant-component rule (largest share <= 0.40, n_eff >= 10, weaker label wins) | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 16 | 04.1 D-15: mandatory lab_group_id (UNKNOWN allowed); reserve LABGRP-, MBSET- | Accept default. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 17 | 04.1 D-16: split `retention_definition` with an evidence field | Accept the split. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 18 | 04.1 D-17: absent SEXP.context = UNKNOWN | Accept UNKNOWN. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 19 | 04.2-min item 1: approve field set and enumerations (method_indicator and dispersion lists are agent drafts) | Approved. Registry files (censoring, value origin, measurement basis v1.1) to be created after approval, by Claude, as drafts. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 20 | 04.2-min items 2 and 7: official censor ids CS-011..CS-014 | Add the ids. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 21 | 04.2-min item 4: lod/loq storage | On each observation (OBS), method level as fallback. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 22 | 04.2-min items 6 and 8: bases MB-009..011 with alias settlements; digitisation record with two-read rule (THR-04K-03) | Accept both. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 23 | 04.6-min items 1-3: six-plane codes; DOC in P-SRC; ESTIMATED_FROM_SUMMARY never a label/test value | Approve all three. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 24 | 04.6-min PQ-1: plane-qualified split_group_id (SPLITGRP-EVD-/SPLITGRP-REC-), no cross-plane join | Ratified. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 25 | 04.9-min: reserve the 13 prefixes (incl. THR-, NEG-, MECH-, DGP-, TASK-); no KINETIC- prefix | Accept all; no KINETIC-. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 26 | 04.6-min item 5: create the data-plane registry now | Create now as DRAFT_PENDING_H4 (to be created by Claude as a draft). | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 27 | Sign THR-08A-01..15 (the original plan's own gate numbers) as written | Signed. signed_by=Kush Tokas, signed_at=2026-10-26 set in `registry/preregistered_thresholds_v1.csv`. | 2026-10-26 | ANSWERED |
| 28 | Does `data_seen_before_registration = DESCRIPTIVE_COUNTS_SEEN` satisfy the Step 01.6 rule (only group sizes of source families were seen; no edge, label or lineage computed)? | Yes, it satisfies the rule. No second signer required. | 2026-10-26 | ANSWERED |
| 29 | Sign the agent-drafted rows THR-08A-16, 17, 18, 20, 21, 23 as written | Signed (same fields). | 2026-10-26 | ANSWERED |
| 30 | THR-08A-19 (recall threshold for the UNKNOWN-row screen) and THR-08A-22 (N years, same-lab rule) | Kush will give the numbers now. NOTE: row 19's own text says the value must be set before 08a runs, so it blocks 08a until set. Rows 19 and 22 remain unsigned. | 2026-10-26 | ANSWERED |
| 31 | THR-08A-19: cut-off for the UNKNOWN-row screen | Rule: the loosest B3 score with seeded-copy recall >= 0.95 on scratch seeded data, frozen before any real UNKNOWN row is screened. Signed. | 2026-10-26 | ANSWERED, signed |
| 32 | THR-08A-22: same-lab window N | N = 3 years. Signed. | 2026-10-26 | ANSWERED, signed |
