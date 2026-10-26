# H4 answers log (Kush), step-by-step walk-through

Records the answers Kush gave in the 2026-10-26 session, in order. These are Kush's answers, entered by Claude as the scribe. Nothing here is signed until Kush sets `signed_by` / `signed_at` in the registry files, and nothing here authorises Step 08a (that is a separate written line in `DECISIONS.md`).

| # | Question | Kush's answer | Date | Status |
|---|---|---|---|---|
| 1 | Where does Step 08a run? | "vinayak server if heavy, else Mac". 08a is estimated at CPU seconds to minutes, so it runs on the Mac; vinayak (A100 host, confirm VPN first) only if a run proves heavy. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
| 2 | Baseline sha256 of the seven ledger files (no human input needed) | Recorded by Claude in `registry/baseline_ledger_hashes_08a_v1.csv`. EVD, COND, SRC and MEAS match the hashes recorded earlier; STUDY, SNAP and `_ids` are new baselines. | 2026-10-26 | DONE (to be re-checked immediately before any 08a write) |
| 3 | Must `registry/data_source_acquisition_manifest_v1_1.csv` exist before 08a runs? | No, the v1 manifest is enough; v1.1 is built later as step 06.3-min. | 2026-10-26 | ANSWERED, not yet in DECISIONS.md |
