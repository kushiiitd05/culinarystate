# Compute ledger of the remaining runs, 9-23 Nov 2026 (T9-C25-R1)

Status: **AI_DRAFTED / PROPOSED** (S178 GOVDOC lane, Mon 9 Nov 2026 about 16:00 IST, manjot-server, tree `~/kush_work/culinarystate/.orch`, HEAD `4a95380` plus uncommitted work). Nothing here is a decision, signature or approval (D-071). It refines sec 9 of `reports/orchestration/S178_EXECUTION_BOARD.md` (the compute plan) and adds what sec 9 lacks: workers, depends_on, VPN risk per job, a disk budget and a worker-concurrency plan. Machine-readable twin: `reports/s178/compute_ledger_remaining.csv` (same rows).

**How to read the numbers.** Every wall time carries a basis. **MEASURED** = a logged run in `registry/compute_runs_v1.csv` (load average 67-410 on 128 cores, so upper-end for an idle host). **Scaled** = measured per-recipe rate x the new recipe count (arithmetic, not a run). **UNVERIFIED** = a planning figure from the board or the agent; no timing exists. `agent h` is the board's remaining agent-hours for the *whole item*, not only the compute; items that appear in two jobs (T3-C08-R2, T3-C13-R1, T5-C05-R2, T8-C15-R1) are summed once in the totals.

## 1. Summary by host

| Host | Role and limits | Jobs | Distinct board items | Wall-clock (sum, if run one after another) | Peak workers | VPN dependence |
|---|---|---|---|---|---|---|
| Mac (Kush's Mac) | BBC-only jobs (D-003), git merge/push, scribing of human gates, operator of vinayak. 8 GB RAM, swaps under load; earlier full-suite runs were reaped | 6 (M-01, 02, 03, 05, 06, 07) + M-04 shared | 15 | about 3-6 h of compute, mostly minutes each; the real constraint is that one Mac agent also scribes the lock, merges and operates vinayak in the same days | 4 | none for its own jobs |
| manjot-server | non-BBC CPU only; shared host (load average 92 on 128 cores at 15:36 IST 9 Nov); `nice -n 10`; at most 32 workers; no GPU; no torch | 12 (J-01..J-12) | 22 | about 13-30 h sequential; about 8-14 h elapsed with the concurrency plan in sec 4 | 32 (cap) | only J-12 (NER spans) |
| vinayak-server (through the Mac agent) | GPU/Ollama rungs only (qwen2.5:7b, GPU 1 only) | 2 (V-01, V-02) + M-04 leg | 4 | about 1.3-4 h GPU (UNVERIFIED) | 1 GPU | **all of it** |

## 2. Job table (host, job, workers, wall time, depends_on)

| id | host | job | workers | wall time | basis | when | depends_on | VPN risk | board items | agent h (whole items) |
|---|---|---|---|---|---|---|---|---|---|---|
| M-01 | Mac | BBC non-heat L1/L2 census + BBC heat L2 v03 re-run (commands in reports/orchestration/S176_L-PHYS_report.md sec 9) | 2-4 | calendar slot 1-3 h (board); scaled compute about 0.3-0.6 h | UNVERIFIED scaling from measured manjot non-heat rates (about 0.1-0.15 worker-s per recipe x 11,934 BBC recipes) | Tue 10 - Wed 11 | Mac merges max/s176-orchestration (G3); S177 lanes committed (G1) | none (Mac-local, D-003) | T4-C11-R1 T4-C11-R3 T4-C12-R2 T4-C14-R2 | 1.5 |
| M-02 | Mac | BBC line census + lot census re-run after Mac tickets A4-A6 | 1 | about 1 h (board) | measured anchor: BBC line census 44.6 s, 365 MB (RUN-S175-001 note); lot census unlogged | Wed 11 - Thu 12 | tickets A4, A5, A6 fixed test-first (G2) | none | T3-C08-R2 T3-C13-R1 | 3.0 |
| M-03 | Mac | hypothesis property test, at least 10^4 cases, UNKNOWN/NOT_APPLICABLE never reaches SIMULATE (G23.2) | 1 | minutes | UNVERIFIED | Tue 10 - Thu 12 | decision #20 = A (pinned Mac venv); else report says NOT_RUN | none | T5-C05-R1 | 0.5 |
| M-04 | Mac+vinayak+manjot | learning-environment lock file per host + smoke import + transition test suite | 1 each | minutes per host | UNVERIFIED | Tue 10 - Wed 11 | decision #20; Parv authorises (0.3 h) | vinayak leg needs VPN | T6-C19-R1 | 1.5 |
| M-05 | Mac | 15A seal check (full) + 29-diag run twice (byte-identical) + 07.A-R1 scoring + AA CAL extraction/registration | 1 | under 1 h total (board) | board sec 9 (minutes each, UNVERIFIED) | Sat 14 | signatures Wed 11 noon; scikit-learn in Mac venv (#20); both 07.A label files back Fri 13 | none | T2-C14-R1 T6-C03-R3 T2-C05-R3 T2-C09-R3 T2-C09-R4 | 6.15 |
| M-06 | Mac | BBC router census with gates (BBC leg) | 1-2 | about 1-2 h (board); scaled about 1 h | scaled from measured non-BBC router run (RUN-S176-ROUTER-004: 109 min at 24 workers for 600,848 recipes = about 0.26 worker-s per recipe) | Thu 19 | SCIFIX-ROUTER committed; Mac fixes; PARAM decision | none | T5-C05-R2 | 3.0 |
| M-07 | Mac | leakage grep of slides/report/screenshots against git-ignored text hashes; Rung A vs P1 gold diagnostic | 1 | minutes | UNVERIFIED | Sat 21 (grep); W2 (gold) | report draft (grep); P1 gold on the Mac only | none | T9-C30-R1 T3-C11-R1 | 7.5 |
| J-01 | manjot | non-BBC line census re-run (Food.com, Gutenberg, Wikibooks, TASTEset) | 1 per family process | Food.com 0.73 h (43.6 min); the other three families under 2 min each | MEASURED (RUN-S177-FULL-001/003/005/007, load 67-80, nice 10) | Thu 12 - Fri 13 | Mac fixes A4-A6 merged into the worktree; 1,000-recipe sample first | none (manjot-local) | T3-C08-R2 | 1.5 |
| J-02 | manjot | non-BBC lot census re-run | 1 per family process | Food.com 2.00 h (120.1 min); the other three families under 2 min each; run in parallel with J-01 so about 2.0 h elapsed | MEASURED (RUN-S177-FULL-002/004/006/008; board sec 9 said about 2.9 h, an extrapolation) | Thu 12 - Fri 13 | same as J-01 | none | T3-C13-R1 | 1.5 |
| J-03 | manjot | quantity-grammar fix (U+2044/U+2215) and non-BBC grounding re-run | 4 | 1-2 h (board); rc2 took 50 min on 4 workers | board sec 9 (UNVERIFIED for the next run) | Fri 13 - Sat 14 | Mac ticket A4/P1 so both trees normalise the same way; decision #13 | none | T3-C07-R1 | 5.0 |
| J-04 | manjot | EVD export v2 regeneration + byte-reproducibility hash; 3 run ids reproduced with matching sha256 | 1 | minutes to under 1 h | UNVERIFIED | Fri 13 - Sat 14; Sat 21 (reproduction) | ledger state final (15A-BOOT freeze rule: no ledger append after approval) | none | T2-C01-R2 T9-C24-R2 | 3.25 |
| J-05 | manjot | D5 split registry + leakage audit re-run on the frozen benchmark | 1 | minutes | measured on the draft by the EVAL lane (reports/s178/*) | Mon 16 - Tue 17 | both D5 review sheets back, reconciled; benchmark frozen (hard stop Tue 17) | none | T8-C20-R3 T9-C09-R1 | 2.0 |
| J-06 | manjot | deterministic rungs B0/B1/B2/B4/B5T fallback + retrieval metrics, router accuracy, OOD, slot accuracy, H3 analysis, claim-audit merge | 1-8 | minutes to 1 h each | board sec 9 (UNVERIFIED). Flag: manjot has no torch, so B1/B2 embeddings must be pre-computed or run elsewhere (see T7-C01-R5 in S178_GOVDOC_report.md) | Tue 17 - Thu 19 | benchmark frozen; D5 prompts pinned (prompt_registry, T8-C17-R1) | none | T8-C06-R1 T8-C01-R1 T8-C13-R1 T8-C03-R1 T8-C22-R1 T8-C16-R1 | 12.0 |
| J-07 | manjot | 26g simulability census re-run with Layer 1 bindings (14.6 M engine events; sample first) | up to 32 | 1-4 h (UNVERIFIED); S168 planned the original full run at about 4 h on vinayak | UNVERIFIED anchor (WORKLOG S168 note, not a logged run) | Tue 17 - Wed 18 | T4-C04-R1; counts-only output (per-event records would be about 13 GB at the measured 0.9 kB per event, so do NOT write them) | none | T4-C21-R1 | 5.0 |
| J-08 | manjot | router census, full non-BBC re-run with gates after fixes + PARAM | 24 | about 1.8 h (measured 109 min at 24 workers); board says 1-3 h | MEASURED anchor RUN-S176-ROUTER-004 | Wed 18 - Fri 20 | SCIFIX-ROUTER committed; PARAM minted (or NEED_DATA) | none | T5-C05-R2 T5-C05-R3 | 9.0 |
| J-09 | manjot | Kleene mechanism screen, non-BBC full run (stretch lane, first to be cut) | up to 24 | 1-3 h (UNVERIFIED) | UNVERIFIED | Wed 18 - Fri 20 | T5-C02-R2 built on composition/ (read-only); decision T5-C01-R4 | none | T5-C02-R3 | 1.5 |
| J-10 | manjot | Model A fit freeze, sim_aa_1 calibration + identifiability, simulability census v1 with calibrated sim_aa_1 | 1-8 | fit/calibration minutes (scipy, CPU); census 1-3 h (UNVERIFIED) | UNVERIFIED | Mon 16 (freeze); Tue 17 - Fri 20 | AA CAL rows dual-verified Sun 15 (else NEED_DATA and the census is void); SIM-VAL stays closed until the fit hash is committed | none | T5-C07-R5 T5-C11-R3 T5-C11-R6 | 12.0 |
| J-11 | manjot | cheap ablations on the frozen set (state conditioning, evidence compat, claim enforcement, OOD gate) | 1-4 | minutes to 1 h each | UNVERIFIED | Wed 18 - Fri 20 | frozen benchmark; first to be cut if results are late | none | T8-C21-R2 | 4.0 |
| J-12 | manjot | NER vs Rung A mention agreement (needs the vinayak NER span files, 4.16 M lines) | 1 | minutes after the files arrive | UNVERIFIED; span file sizes not measured | Tue 17 - Fri 20 | span files copied from vinayak via the Mac (T9-C25-R3); else the item goes POST | HIGH for this job (no VPN = no spans) | T3-C09-R1 | 5.0 |
| V-01 | vinayak (via Mac agent) | D5 dry run on a subset: B0/B1/B2/B4/B5/B7/B5T with qwen2.5:7b, temperature 0, fixed seed, digest and prompt sha pinned | GPU 1 only | about 0.3-1 h | UNVERIFIED planning range: assumes about 100 questions x 6 LLM rungs and 5-20 s per generation (the agent has not timed this model on this GPU) | Sat 14 | ssh/VPN works (decision #21, Fri 13); T8-C15-R3 digest + prompt sha; prompt_registry (T8-C17-R1) | HIGH: whole job | T8-C15-R1 T8-C15-R3 T8-C17-R1 | 7.0 |
| V-02 | vinayak (via Mac agent) | full rung runs on the frozen benchmark (LLM rungs), then H1 McNemar/Newcombe (CPU seconds, can run on manjot from the raw outputs) | GPU 1 only | about 1-3 h GPU (UNVERIFIED, same assumption as V-01) | UNVERIFIED | Tue 17 - Thu 19 | benchmark frozen Mon 16 (hard stop Tue 17); VPN | HIGH: LLM rungs only. Fallback (pre-written, ops pack 5.2): deterministic rungs on manjot CPU, LLM rungs NOT_RUN | T8-C15-R1 T8-C21-R1 | 6.5 |

Distinct items across the table: 39, 88.4 agent-hours of whole-item board hours (the per-row column sums to 98.4 because items shared by two jobs are counted in each). By board status: 1 BLOCKED_DATA, 7 BLOCKED_HUMAN, 21 OPEN, 10 PARTIAL.

Runs that are not repeated and so are not in this table: the 55 manjot rows of S174/S176/S177 (all logged), the S178 ANALYSIS/EVAL/PREREG lane runs (15 rows, see sec 6).

## 3. Day by day (compute only)

| Day | Mac | manjot | vinayak |
|---|---|---|---|
| Tue 10 | M-03, M-04 (after decision #20); M-01 starts once the merge (G3) is done | idle (agents write amendments and drafts; the 2 GOVDOC runs are minutes) | ssh test by Kush (human) |
| Wed 11 | M-01 finishes; M-02 starts after tickets A4-A6 | M-04 manjot leg | none |
| Thu 12 | M-02 finishes | J-01 + J-02 start (2 processes, about 2.0 h) | none |
| Fri 13 | scribing, report skeleton | J-02 finishes; J-03 starts (4 workers, 1-2 h); J-04 | VPN decision #21 |
| Sat 14 | M-05 (seal check, 29-diag twice, 07.A-R1 scoring, AA registration) | J-03 finishes | V-01 dry run |
| Sun 15 | none | none | none |
| Mon 16 | none | J-10 Model A fit freeze (minutes); J-05 after the benchmark freeze | none |
| Tue 17 | none | J-05, J-06 start (8 workers), J-07 sample then full (up to 16 workers); J-12 if spans arrived | V-02 starts (hard stop for the benchmark freeze is Tue 17) |
| Wed 18 | none | J-07 finishes; J-08 starts (24 workers); J-10 calibration | V-02 |
| Thu 19 | M-06 (BBC router, 1-2 h) | J-08 finishes; J-06 results; J-11 | V-02 ends; results in (gate: else level L3) |
| Fri 20 | none | J-09 (stretch), J-10 census | none |
| Sat 21 | M-07 leakage grep | J-04 reproduction of 3 run ids | none |
| Sun 22 - Mon 23 | none | none (code and result freeze Sat 21) | none |

## 4. Concurrency plan on manjot (32-worker cap)

At most 32 worker processes at any time across all lanes of the session, `nice -n 10`, 1,000-recipe sample before each full run, seed 20261104. Proposed packing: Thu 12 - Fri 13: J-01 (1) + J-02 (1) + J-03 (4) = 6. Tue 17 - Wed 18: J-06 (8) + J-07 (16) = 24. Wed 18 - Fri 20: J-08 (24) + J-09 (8, stretch) = 32. Do not start J-07 and J-08 together (40 workers). If another user's load pushes the 128-core host harder than the 67-410 seen so far, J-07 is the job to shrink or sample, not the router run.

## 5. VPN risk

| Item | Evidence in the repo | Rating (AI judgment) |
|---|---|---|
| History | WORKLOG records VPN failures in several sessions: earlier GPU runs deferred ("VPN not working, SSH timeout, no route"), S170 ("VPN dropped mid-session"), S173-S174 ("VPN route missing all session"; Food.com and GPU NER waited until servers came back on 8 Nov). No private address is quoted here (the repo is public). | repeated: plan on the VPN failing at least once in 9-23 Nov |
| What it takes out | V-01, V-02 (all LLM rungs, so H1 and the LLM part of H3), J-12 (NER span transfer), the vinayak leg of M-04. Nothing else in this ledger needs it: the Mac and manjot jobs are local. | impact bounded to the LLM rungs |
| Fallback (pre-written, ops pack sec 5.2 Tue 17 row, board sec 9) | deterministic rungs B0/B1/B2/B4/B5T and all scoring and analysis run on manjot CPU (J-06); LLM rungs NOT_RUN; the sentence is written into the D5 prereg inside the Tue 10 lock | the fallback keeps the minimum publishable claim set; it needs decision A7 to be human-adopted to count as agreed |
| Checks | Kush: ssh test Tue 10; decision #21 on Fri 13. One thing the agent cannot check from manjot: whether the Mac can reach vinayak. | not testable from this host |
| Embedding dependency | B1/B2 need an embedding model (decision #4); manjot has no torch (T7-C01-R5 check), so the deterministic fallback is only fully deterministic for B0/B4/B5T unless embeddings are pre-computed or served from the Mac/vinayak. | open: ask at decision #4 |

## 6. Disk budget

| Host | Free now | Plan | Notes |
|---|---|---|---|
| manjot | 527 GB free of 11 TB (96 % used; measured `df -h` 15:36 IST 9 Nov); `data/derived/` already holds 16 GB written in S176-S177 | every job above writes a counts-only JSON (kilobytes); keep each lane under 15 GB; no per-event records for J-07 (about 13 GB at the measured 0.9 kB per event, from 1.5 GB for 1.75 M heat events) | candidates to remove if the orchestrator confirms v03 supersedes them: the S176 and S176v02 non-heat L2 directories (about 3.7 GB) and `physical_L2_full_S176v02` (2.4 GB), about 6 GB in all. The agent deleted nothing. |
| Mac | not measurable from here | M-01 reproduces about the same record sizes for 11,934 BBC recipes (a few hundred MB at most, scaled UNVERIFIED); outputs stay git-ignored or counts-only (D-003) | ask Kush for `df` on the Mac before M-01 |
| vinayak | not measurable from here | outputs are model answers for about 100 questions x 7 rungs (kilobytes to a few MB) | NER spans of S174 already live in `~/Kush/cs_runs/` |

## 7. Gaps in the run log itself (feeds T9-C11-R2, T9-C25-R4)

- 21 S178 lane run rows exist only in lane reports and are not in `registry/compute_runs_v1.csv` at the time of writing: RUN-S178-ANA-001, RUN-S178-ANA-002, RUN-S178-ANA-003, RUN-S178-ANA-004, RUN-S178-ANA-005, RUN-S178-ANA-006, RUN-S178-ANA-007, RUN-S178-EVAL-001, RUN-S178-EVAL-002, RUN-S178-EVAL-003, RUN-S178-EVAL-004, RUN-S178-EVAL-005, RUN-S178-GOV-001, RUN-S178-GOV-002, RUN-S178-GOV-003, RUN-S178-GOV-004, RUN-S178-GOV-005, RUN-S178-GOV-006, RUN-S178-PREREG-001, RUN-S178-PREREG-002, RUN-S178-PREREG-003.
- The full-corpus 26g census 0.2.0 (S168-S170, vinayak) predates the run log and has no row; the "about 4 h" figure is a planning note, not a logged run.
- Manjot rows record UTC (`...Z`); older Mac rows record local time without a zone. A reader comparing the two must convert (IST = UTC + 5:30).
- After T9-C11-R2, 22 of 86 rows in `registry/compute_runs_v1.csv` still lack a start and/or an end (12 mac, 6 manjot-server, 4 vinayak-server); 18 have neither. Nothing in the repo records those times; commit-time bounds are in `reports/orchestration/S178_GOVDOC_report.md`.
