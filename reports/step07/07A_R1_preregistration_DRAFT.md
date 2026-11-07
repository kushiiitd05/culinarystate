# Step 07.A-R1: condition-audit gate, new attempt — pre-registration (DRAFT, UNSIGNED)

Status: **DRAFT_PENDING_SIGNATURES** (Kush and Parv). Written S171, 2026-11-08, by the coding agent from D-075.
Committed **before** the packet is built and before any label exists. Neither reviewer may open the packet until
both have signed this file (block at the end). After signing, nothing in §2–§5 may change; any change is a
dated amendment committed before labelling, or the attempt is void.

## 1. Why a new attempt (nothing is reinterpreted)

07.A on packet v4 (100 conditions, 9 judgement fields, normalizer `e7d589136275`) FAILED its signed gate:
pooled Cohen's kappa 0.0 against ≥ 0.80, raw agreement 0.9944 (900 cells, 5 disagreements). The cause is the
kappa paradox: when one code dominates (here `CORRECT`), chance agreement approaches 1 and kappa collapses even at
near-perfect agreement. That FAIL stays on record (D-027 R-20; `reports/step07/step07_v4_adjudication_result.md`).
The v4 labels are **not** rescored with the statistic below (THR-07A-06, D-027 R-06). This file registers a new
gate attempt on a **fresh, disjoint** packet, with a statistic chosen before any of its labels exist (D-075).

## 2. Packet (built by `tools/step07ar_build_packet.py`; reviewers open it only after both sign)

- 100 conditions referenced by ACTIVE EVD rows, same six strata and quotas as v4 (S1 20, S2 25, S3 15, S4 15, S5 10,
  S6 15), ranked within stratum by sha256(seed ‖ condition_id), seed `step07-condition-audit-R1-2026-11-08`.
- **Disjoint from v1–v4:** every condition id in the v4 packet is excluded before ranking (v1–v4 share v4's 100).
- Same columns, codes and rubric as v4 (`reports/step07/condition_audit_protocol.md`, 07H-R section); same frozen
  normalizer (`e7d589136275`, `tools/step07hr_freeze.py --verify` = FREEZE INTACT at build and at scoring).
- Two copies (`…_R1_Kush.csv`, `…_R1_Parv.csv`, git-ignored: raw third-party strings). The committed manifest holds
  counts, the seed, the excluded-set size and hash, and the SHA-256 of each issued file. No condition ids or text.

## 3. Statistic and gate (registered now)

Codes per field: the fixed 7-code codebook `CORRECT, WRONG_TYPE, WRONG_VALUE, WRONG_LOCATION, INFERRED,
SHOULD_BE_AMBIGUOUS, N/A` (q = 7, from the codebook, not from the codes observed).

**Gwet's AC1** for two raters (Gwet 2008): p_a = share of cells where the two codes agree; for each code k,
π_k = (count of k from reviewer A + count from reviewer B) / (2n); p_e = Σ_k π_k (1 − π_k) / (q − 1);
AC1 = (p_a − p_e) / (1 − p_e). AC1 stays well behaved under high prevalence, unlike kappa.

**PASS** iff all of:
1. Pooled AC1 over all 900 cells (9 fields × 100 conditions) ≥ **0.80** (point estimate, same value as the original
   gate).
2. For each critical field (temperature_location, pressure, basis, retention_type, censoring — THR-07A-02):
   AC1 ≥ 0.80 **and** exact agreement ≥ 0.90 **and** no ordered code pair (A, B) repeated ≥ 3 times among its
   disagreements. Any breach is a flag; a flag means **FAIL_OR_ADJUDICATE**, not PASS.
3. Input validity as THR-07A-07: identical audit-id sets, one normalizer fingerprint, every one of the 10 judgement
   cells per row filled with a valid code (`overall_judgement` ACCEPT/REJECT). Otherwise **INVALID_INPUT**.
4. Provenance as THR-07A-08: the two returned files are not identical in all 10 judgement columns; the non-judgement
   columns of each returned file equal the issued packet row for row; each returned file's SHA-256 is recorded on
   receipt, before scoring. Otherwise **NOT_COUNTED**.

Diagnostics, printed and **never** gating: pooled and per-field Cohen's kappa, PABAK, raw agreement, overall
ACCEPT/REJECT AC1 and kappa (q = 2), per-stratum agreement, the disagreement matrix, and a condition-level bootstrap
95% interval for pooled AC1 (2,000 resamples, seed `07A-R1-bootstrap`).

**Discharge (as THR-07A-06):** disagreements are adjudicated jointly after scoring and recorded; the statistic is
always computed on the original independent labels and is never recomputed after adjudication.

## 4. Conduct

Each reviewer works alone, judges only against the raw strings shown, uses no external source and does not see the
other file. Estimated time: 3–4 h each. Return by **13 Nov 2026** (finish plan M2). The agent does not fill, edit
or tune anything on the labels; the normalizer may not change between packet build and scoring.

## 5. What a PASS opens and what it does not

A PASS of 07.A-R1 is the valid 07.A that D-027 R-05 requires; 23b also needs 15b frozen, so a PASS alone does
not open 23b. A FAIL is recorded as a second failed attempt, and no third attempt is pre-registered here.

## Signatures (human only; D-071: the agent never signs)

- Kush Tokas: ______ date ______  (by signing, Kush confirms no R1 label exists)
- Parv Goyal: ______ date ______

Reference: Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high
agreement. *British Journal of Mathematical and Statistical Psychology*, 61(1), 29–48.
