# 07.A-R1 pre-registration: pre-signature amendment draft (S178)

Status: **AI_DRAFTED / PROPOSED. Not a decision, not a signature, not an approval (D-071).** Written 2026-11-09 by the
S178 PREREG lane (an AI agent) for the 9-10 Nov decision sitting (ops pack item **#2, T2-C05-R5**, and C06 / T2-C05-R7).
Nothing here changes `reports/step07/07A_R1_preregistration_DRAFT.md`; that file is a human-gate document and is
edited only by the Mac scribe, after the sitting, with the options the humans chose.

- Base text amended: `reports/step07/07A_R1_preregistration_DRAFT.md`, sha256
  `6886ccef0063b3824d196040b047729525053967e54dab2a8a44a1a536e76cd3` (server worktree, 2026-11-09). If the Mac copy
  hashes differently, stop: this draft was written against these bytes.
- Packet manifest today: `reports/step07/07A_R1_packet_manifest.json` (packet sha256 `f086975a…ca27d`, both copies).
  Nobody has opened the packet (no signature exists), so a re-issue is still clean.
- Numbers below were computed with the project's own code (`condition_agreement.gwet_ac1/cohen_kappa/_bootstrap`)
  on **synthetic** label vectors and with `scipy.stats.beta/binom`. No real R1 label exists. Scripts:
  `reports/orchestration/S178_PREREG_calc/{power_s178,ac1_s178,r1_pool_counts_s178}.py` with their JSON outputs.

## 0. What the sitting must decide

| Id | Question | Options in this file | Type | Pack rec. |
|---|---|---|---|---|
| D-07A-1 | Gate statistic and rule for attempt 07.A-R1 | **A** hardened AC1 + accuracy co-gate + planted rows (= pack B2; **A-keep** = A plus the old `IDENTICAL_JUDGEMENTS` rule, §1) · **B** R-06 kappa gate kept, PABAK diagnostic (= pack A) · **C** accuracy-primary gate · **D** no R1 attempt before 25 Nov · **E** draft as written (= pack B1) | HUMAN (A, C, E amend R-06) | A |
| D-07A-2 | Co-gate thresholds X (only A, C) | X_crit, X_any from the Clopper-Pearson table (§3) | HUMAN | X_crit 0.95, X_any 0.90 |
| D-07A-3 | USDA-dialect floor | **U1** fixed USDA sub-quotas, 100 kept · **U2** extra 20-condition USDA stratum (120) · **U3** no floor, per-source caveat | choice | U1 |
| D-07A-4 | Planted-defect rows (C06: only inside the lock, <= 0.3 h per rater) | **P1** 10 rows, >= 8 of 10 or NOT_COUNTED · **P2** 10 rows, diagnostic only · **P0** none ("AC1 measures agreement, not error detection" in the report) | choice (A and C need P1) | P1 |
| D-07A-5 | Return deadline | **T1** 13 Nov (consensus trigger) · **T2** 13 Nov soft, 20 Nov hard (REV-B) | choice | T2 |
| D-07A-R06 | The DECISIONS entry amending R-06 | template in §4, **written by Kush in his own words** | HUMAN, Kush only | needed for A, C, E |

**Crosswalk to the ops pack labels (to avoid confusion):** this file's A = pack "B2", B = pack "A", E = pack "B1".
C and D are not in the pack.

## 1. Why none of this is a post-hoc weakening (read before choosing)

- The v4 result is **FAILED and stays FAILED** (pooled kappa 0.0 against >= 0.80; raw agreement 0.9944; 900 cells;
  5 disagreements; `reports/step07/step07_v4_adjudication_result.md`). No option relabels, rescores or reinterprets
  it (D-027 R-20, THR-07A-06). The R1 attempt is a **new attempt on a fresh, disjoint packet** (D-075), and every
  option is fixed before any R1 label exists.
- The draft's own gate (pooled AC1 >= 0.80, point estimate) is **looser** than the gate it replaces: on synthetic
  vectors it tolerates 174 of 900 disagreeing cells (19.3 %), and the v4 pattern scores AC1 0.9944 under it (REV-B
  F-03 reproduced). Option E keeps that; it is listed only so the sitting sees it, and this lane does not recommend it.
- Option A is designed so that the **v4 pattern would not pass it** (illustration on the committed v4 summary counts,
  not a rescoring; v4 stays FAILED): the duration field enters the critical set and its 4 identical ordered
  disagreements trip the repeated-pair rule; the 5 adjudicated SHOULD_BE_AMBIGUOUS cells are 5 critical-field defect
  conditions against a co-gate of <= 1; a reviewer coding every cell CORRECT would miss the planted rows and be
  NOT_COUNTED. Note honestly: the pooled-AC1 part alone (lower bound 0.9889 >= 0.95) **would** still have passed v4.
  The co-gate and the planted rows are what make A stricter, so A without them is not offered.
- **The one element of Option A that relaxes a rule:** the `IDENTICAL_JUDGEMENTS` provenance rule (two files equal
  in all 10 judgement columns -> NOT_COUNTED) is removed, because it makes a perfectly agreeing honest pair
  NOT_COUNTED (REV-B F-05). It is a copy check, not the gate statistic, and it is replaced by three stronger copy
  checks (receipt times after both signatures, identical free-text reasons, planted-row detection per reviewer). If
  the sitting prefers no relaxation at all, choose **A-keep**: Option A with the `IDENTICAL_JUDGEMENTS` rule kept in
  addition (then the report must say a perfectly agreeing pair cannot count).
- The report must say **"gate redefined after a failed gate"** under A, C or E (REV-B Q24 (iii)).

## 2. Changes (old text -> new text)

Line numbers refer to the base text above. `-` = original line(s), quoted exactly; `+` = proposed replacement.

### C1. Header (L3-L6): bind the amendment and the R-06 entry

```diff
-Status: **DRAFT_PENDING_SIGNATURES** (Kush and Parv). Written S171, 2026-11-08, by the coding agent from D-075.
-Committed **before** the packet is built and before any label exists. Neither reviewer may open the packet until
-both have signed this file (block at the end). After signing, nothing in §2–§5 may change; any change is a
-dated amendment committed before labelling, or the attempt is void.
+Status: **DRAFT_PENDING_SIGNATURES** (Kush and Parv). Written S171, 2026-11-08, by the coding agent from D-075;
+amended before any signature by the S178 options the 9-10 Nov sitting chose
+(`reports/step07/07A_R1_preregistration_AMENDMENT_S178_DRAFT.md`, choices recorded in D-0NN). Until a human signs,
+this file is a dated AI draft, not a pre-registration. It counts as pre-registered only through the two signature
+files named at the end, each carrying the sha256 of these exact bytes. The gate below is valid only if Kush's
+own DECISIONS entry amending D-027 R-06 for attempt 07.A-R1 (D-0NN) is dated before both signatures [only if
+Option A, C or E]. Neither reviewer may open the packet until both have signed. After signing, nothing in §2–§6
+may change; any change is a dated amendment committed before labelling, or the attempt is void.
```

### C2. §1, append one paragraph after L15

```diff
 gate attempt on a **fresh, disjoint** packet, with a statistic chosen before any of its labels exist (D-075).
+
+Disclosure (REV-B Q24, F-01..F-06): this gate is **redefined after a failed gate**. The S171 draft gate (pooled AC1
+>= 0.80) would have passed the v4 pattern (reconstructed AC1 0.9944) and tolerates about 174 of 900 disagreeing
+cells; it is therefore not used. AC1 and kappa both measure agreement between the two reviewers, not whether the
+normaliser is right; two reviewers who code every cell the same wrong way score AC1 = 1. The gate below adds a
+correctness check and seeded known-wrong rows for that reason. [Option A / C wording; under Option B replace this
+paragraph with: "The gate is the unchanged D-027 R-06 rule; AC1 and PABAK are diagnostics only. At the prevalence
+seen in v4 this rule may FAIL again for the same reason (kappa paradox); that outcome is accepted in advance."]
```

### C3. §2 Packet (L17-L25): planted rows, USDA floor, re-issue

Keep L19-L25 and append the following, choosing one U-block and one P-block.

```diff
 - Two copies (`…_R1_Kush.csv`, `…_R1_Parv.csv`, git-ignored: raw third-party strings). The committed manifest holds
   counts, the seed, the excluded-set size and hash, and the SHA-256 of each issued file. No condition ids or text.
+- **Re-issue (S178).** The packet of 2026-11-08 (sha256 f086975a…ca27d, never opened) is superseded before issue.
+  Its manifest is kept unchanged as history; the new packet gets new file names and a new manifest
+  (`reports/step07/07A_R1_packet_manifest_v2.json`). Same seed, same strata, same exclusion of v1-v4.
```

**OPTION U1 (recommended): fixed USDA sub-quotas inside the existing quotas (100 conditions kept)**
```diff
+- **USDA-dialect floor (REV-B F-06).** The 2026-11-08 draw held USDA 4, Bognar 18, Phenol-Explorer 78, while USDA
+  and Bognar carry about 14.1k of the 17,978 EVD rows. Within S3, S5 and S6 the draw first takes the smallest-rank
+  USDA-RETN-R6 conditions up to a fixed sub-quota (S3 3, S5 3, S6 14 = 20), then fills the stratum by rank from the
+  other conditions. Stratum quotas are unchanged (S1 20, S2 25, S3 15, S4 15, S5 10, S6 15). Pool before the v1-v4
+  exclusion (counts only, 2026-11-09): USDA 270 conditions (S3 18, S5 15, S6 237); none in S1, S2, S4.
+  Consequence stated now: S6 becomes mostly USDA, whose cells are mostly duration/temperature N/A, so the floor
+  mainly tests the USDA measurement-context normalisation (basis, retention type, censoring).
```
**OPTION U2: extra stratum** — as U1, but S7_USDA_FLOOR = 20 USDA conditions added (packet 120 real conditions,
about +20 % rater time); strata S1-S6 unchanged.
**OPTION U3: no floor** — add only: "Agreement is reported per source family; with USDA n = 4 the result says
almost nothing about the USDA dialect, and the report says so."

**OPTION P1 (recommended; needed by Options A and C): 10 planted-defect rows, gating per reviewer**
```diff
+- **Planted-defect rows (C06 / T2-C05-R7, REV-B Q24.3).** 10 extra rows are added to the 100. Each is a real
+  ACTIVE condition outside the 100 and outside v1-v4, drawn by sha256(`07A-R1-planted-2026-11-10` ‖ condition_id),
+  whose normalised display is changed by one fixed edit that contradicts the raw string: E1 duration unit
+  min<->h with the number unchanged; E2 a degF value shown as degC unconverted; E3 location CORE where the raw text
+  states none; E4 pressure value x10; E5 basis fresh<->dry weight; E6 retention type true<->apparent; E7 censoring
+  none<->GT_CAP; E8 a stated interval shown as a point; E9 medium water<->oil; E10 power W<->kW. Each edit is applied
+  to a condition whose raw string populates that field. Audit ids CA-001..CA-110 (CA-130 under U2) are reassigned by
+  sha256(seed ‖ condition_id) rank so planted rows are interleaved. Reviewers are told that 10 rows are planted,
+  not which. The key (audit id, edit type) is a git-ignored file on the Mac; its sha256 is in the lock record; the
+  scorer opens it only after both returned files' sha256 are recorded.
+- A planted row is **detected** by a reviewer when the edited field is coded anything other than CORRECT or N/A.
+  A reviewer who detects fewer than **8 of 10** makes the attempt **NOT_COUNTED** (two valid files are needed).
+  Planted rows are excluded from every agreement and accuracy statistic. Expected cost: about 0.3 h per reviewer.
```
**OPTION P2: planted rows, diagnostic only** — same rows; detection rate per reviewer printed with a one-sided
95 % Clopper-Pearson lower bound, never gating. (Not compatible with Options A or C as written.)
**OPTION P0: none** — add: "No seeded controls. The report states that AC1 measures agreement, not error
detection." (C06 default if the lock cannot carry it.)

### C4. §3 Statistic and gate (L27-L53): replace L36-L53 with ONE of the following

L29-L34 (codebook, AC1 formula) stay unchanged under A, C and E; under B they stay as the diagnostic's definition.

**OPTION A (recommended): hardened AC1 + accuracy co-gate + planted rows**
```diff
-**PASS** iff all of:
-1. Pooled AC1 over all 900 cells (9 fields × 100 conditions) ≥ **0.80** (point estimate, same value as the original
-   gate).
-2. For each critical field (temperature_location, pressure, basis, retention_type, censoring — THR-07A-02):
-   AC1 ≥ 0.80 **and** exact agreement ≥ 0.90 **and** no ordered code pair (A, B) repeated ≥ 3 times among its
-   disagreements. Any breach is a flag; a flag means **FAIL_OR_ADJUDICATE**, not PASS.
-3. Input validity as THR-07A-07: identical audit-id sets, one normalizer fingerprint, every one of the 10 judgement
-   cells per row filled with a valid code (`overall_judgement` ACCEPT/REJECT). Otherwise **INVALID_INPUT**.
-4. Provenance as THR-07A-08: the two returned files are not identical in all 10 judgement columns; the non-judgement
-   columns of each returned file equal the issued packet row for row; each returned file's SHA-256 is recorded on
-   receipt, before scoring. Otherwise **NOT_COUNTED**.
+All statistics in items 3-4 use the 100 real conditions only (900 field cells), on the original independent labels.
+**PASS** iff all of:
+1. Input validity as THR-07A-07: identical audit-id sets, one normalizer fingerprint, every one of the 10 judgement
+   cells per row filled with a valid code (`overall_judgement` ACCEPT/REJECT). Otherwise **INVALID_INPUT**.
+2. Provenance (replaces the `IDENTICAL_JUDGEMENTS` rule, REV-B F-05): the non-judgement columns of each returned
+   file equal the issued packet row for row; each returned file's sha256 and receipt time are recorded before
+   scoring, and both receipt times are later than both signature commits; fewer than 3 audit ids carry an identical
+   non-empty `reason_if_not_correct` in both files (compared after lower-casing and collapsing whitespace and
+   punctuation, strings of 15 or more characters); each reviewer detects >= 8 of the 10 planted rows (§2).
+   Otherwise **NOT_COUNTED**. Two files that agree in every cell are no longer NOT_COUNTED for that reason alone.
+3. Agreement: the lower end of the two-sided 95 % condition-bootstrap interval of pooled AC1 (2,000 resamples, seed
+   `07A-R1-bootstrap`, the 2.5th percentile as `condition_agreement._bootstrap` computes it) >= **0.95**.
+4. Critical fields (THR-07A-02 plus `duration_judgement` and `temperature_value_judgement`; all 5 v4 disagreements
+   sat in those two): for each of the 7, AC1 >= 0.80 **and** exact agreement >= 0.90 **and** no ordered code pair
+   (A, B) repeated >= 3 times among its disagreements. Any breach is a flag; a flag means **FAIL_OR_ADJUDICATE**.
+5. Accuracy co-gate, computed once on the jointly adjudicated labels (§3 discharge): a condition is a
+   *critical defect* if any of the 7 critical fields carries WRONG_TYPE, WRONG_VALUE, WRONG_LOCATION, INFERRED or
+   SHOULD_BE_AMBIGUOUS, and an *any-field defect* if any of the 9 fields does; a cell the reviewers cannot resolve
+   counts as a defect. PASS needs the one-sided 95 % Clopper-Pearson lower bound of the defect-free share
+   >= **X_crit = 0.95** for critical defects (that is, at most 1 of 100) and >= **X_any = 0.90** for any-field
+   defects (at most 4 of 100). Otherwise **FAIL_ACCURACY**.
+Outcomes are reported exactly as INVALID_INPUT, NOT_COUNTED, FAIL_OR_ADJUDICATE, FAIL_ACCURACY or PASS. Joint
+adjudication and the co-gate are run and reported for every outcome except INVALID_INPUT and NOT_COUNTED.
```

**OPTION B: R-06 kappa gate kept unchanged; PABAK diagnostic**
```diff
-**PASS** iff all of:
-1. Pooled AC1 over all 900 cells (9 fields × 100 conditions) ≥ **0.80** (point estimate, same value as the original
-   gate).
-2. For each critical field (temperature_location, pressure, basis, retention_type, censoring — THR-07A-02):
-   AC1 ≥ 0.80 **and** exact agreement ≥ 0.90 **and** no ordered code pair (A, B) repeated ≥ 3 times among its
-   disagreements. Any breach is a flag; a flag means **FAIL_OR_ADJUDICATE**, not PASS.
+**PASS** iff all of (D-027 R-06, unchanged; same rule as `tools/step07_agreement.py` L61-L71 and L85):
+1. Pooled Cohen's kappa over all 900 cells >= **0.80**.
+2. No critical field (temperature_location, pressure, basis, retention_type, censoring) with a flag: kappa < 0.80
+   while its dominant-code prevalence is < 0.95, or exact agreement < 0.90, or >= 3 disagreements with the same code
+   pair; a dominant-code prevalence >= 0.95 also raises a flag that forces adjudication. Any flag means
+   **FAIL_OR_ADJUDICATE**.
```
Items 3 (validity) and 4 (provenance, including the R-06 "files not identical" precondition) stay as in the base
text. Diagnostics add Gwet AC1 (q = 7) and PABAK, never gating. **Accept in advance:** with one reviewer constant,
kappa is 0 exactly (synthetic check: 0 disagreements are tolerated); with about 46 % agreed N/A cells it tolerates
about 100. Most R1 critical fields will be N/A-dominated (prevalence >= 0.95), so flags and adjudication are near
certain. The scorer must **not** be `tools/step07_agreement.py` as it stands: it writes to the hard-coded path
`reports/step07/step07h_human_gate_result.json`, the retained v3 NOT_COUNTED result (R-19), and would overwrite it.

**OPTION C: accuracy-primary gate (not in the pack; larger deviation)**
```diff
+**PASS** iff validity (item 1 of Option A), provenance with planted rows (item 2 of Option A) and the accuracy
+co-gate (item 5 of Option A) all hold. Pooled and per-field AC1, kappa and PABAK are diagnostics only.
```
Reason it exists: the question 07.A must answer is "is the normaliser right"; the planted rows measure each
reviewer's error detection directly, which agreement cannot. Risk: removing every agreement statistic from the gate
after an agreement gate failed is the reading most open to "metric shopping", so it needs the strongest R-06 text.

**OPTION D: no R1 attempt before 25 Nov** — the base file stays unsigned and is labelled "dated AI draft, not run".
07.A stays FAILED on record; 23b stays BLOCKED. Saves 3.5-4 h each. This is the consensus slip default (4.1).

**OPTION E: the S171 draft gate as written** (pooled AC1 >= 0.80, point estimate). Not recommended (§1).

### C5. §3 Diagnostics (L48-L50): extend (all options)

```diff
-Diagnostics, printed and **never** gating: pooled and per-field Cohen's kappa, PABAK, raw agreement, overall
-ACCEPT/REJECT AC1 and kappa (q = 2), per-stratum agreement, the disagreement matrix, and a condition-level bootstrap
-95% interval for pooled AC1 (2,000 resamples, seed `07A-R1-bootstrap`).
+Diagnostics, printed and **never** gating: pooled and per-field Cohen's kappa; PABAK in its q-category form
+(q·p_o − 1)/(q − 1) with q = 7, and the binary form 2·p_o − 1 that the scorer prints today, both labelled; raw
+agreement; overall ACCEPT/REJECT AC1 and kappa (q = 2); agreement per stratum and per source family; AC1 and
+agreement on informative cells only (normalised status VALID or AMBIGUOUS); positive specific agreement on flagged
+cells, 2·(both flagged)/(flagged by A + flagged by B); the disagreement matrix; the condition-level bootstrap 95 %
+interval for pooled AC1 (2,000 resamples, seed `07A-R1-bootstrap`); planted-row detection per reviewer and per
+edit type; the co-gate defect counts with their Clopper-Pearson bounds.
```

### C6. §3 Discharge (L52-L53): define adjudication (all options)

```diff
-**Discharge (as THR-07A-06):** disagreements are adjudicated jointly after scoring and recorded; the statistic is
-always computed on the original independent labels and is never recomputed after adjudication.
+**Discharge (as THR-07A-06):** disagreements are adjudicated jointly after scoring and recorded in a DECISIONS entry
+written by the two humans (T2-C05-R4); cells on which both reviewers agree are final as coded. The agreement
+statistic is always computed on the original independent labels and is never recomputed after adjudication. The
+accuracy co-gate [Options A and C] is computed once, on the adjudicated file, and written to its own result file;
+a cell left unresolved counts as a defect. Neither file is ever rescored.
```

### C7. §4 Conduct (L55-L59)

```diff
-other file. Estimated time: 3–4 h each. Return by **13 Nov 2026** (finish plan M2). The agent does not fill, edit
-or tune anything on the labels; the normalizer may not change between packet build and scoring.
+other file. Estimated time: 3–4 h each (+0.3 h with planted rows). Before returning, each reviewer runs the
+codebook validator the agent supplies (it checks codes and blanks only, never content). Optional: up to 20 minutes
+together on 10 separate practice items that are not in the packet, before either opens the packet (REV-B G-17).
+Each reviewer keeps a time log (date, start, end, rows done). Return by **13 Nov 2026** [T1] | **13 Nov soft,
+20 Nov 2026 hard** [T2]. The agent does not fill, edit or tune anything on the labels; the normalizer may not
+change between packet build and scoring.
```

### C8. §5 (L61-L64): one sentence added

```diff
 not open 23b. A FAIL is recorded as a second failed attempt, and no third attempt is pre-registered here.
+NOT_COUNTED and FAIL_ACCURACY are recorded the same way as a FAIL (second unsuccessful attempt). A PASS opens nothing
+before 25 Nov 2026.
```

### C9. Signatures (L66-L69): replace the typed block (REV-B F-07; typing a name into this file changes its hash)

```diff
-- Kush Tokas: ______ date ______  (by signing, Kush confirms no R1 label exists)
-- Parv Goyal: ______ date ______
+This file is signed only by two files, each typed and committed by its signer from their own session:
+`reports/step07/07A_R1_prereg_signature_Kush.json` and `reports/step07/07A_R1_prereg_signature_Parv.json`
+(final names: the lock note), each `{"prereg_sha256": "<sha256 of this file>", "signed_by": "Kush Tokas" | "Parv
+Goyal", "signed_date": "YYYY-MM-DD", "confirms_no_R1_label_exists": true}`. Nobody types a name into this file.
```

## 3. Numbers behind the options (computed; synthetic vectors, no real labels)

**What each agreement rule tolerates (900 cells, 100 conditions, project code):**

| Construction (synthetic) | AC1 point >= 0.80 | AC1 point >= 0.95 | AC1 bootstrap lower >= 0.95 (Option A) | kappa >= 0.80 (Option B) |
|---|---|---|---|---|
| One reviewer all CORRECT; other differs on 1 cell per condition | 174 | 44 | **35** | 0 (kappa = 0 exactly) |
| Same, disagreements clustered 3 per condition | 174 | 44 | **26** | 0 |
| 46 % of cells agreed N/A (balanced prevalence) | 162 | 41 | **32** | 100 |

**v4 reconstruction (illustration only; v4 stays FAILED and is never rescored):** AC1 0.9944, bootstrap lower 0.9889,
kappa 0.0, raw 0.9944, PABAK binary 0.9889 / q = 7 0.9935, positive specific agreement 0.0; duration field 4
identical ordered disagreements (repeated-pair flag under Option A).

**Accuracy co-gate: one-sided 95 % Clopper-Pearson bound for x defect conditions in 100 (sets X):**

| defects x | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| upper bound on defect rate | 0.0295 | 0.0466 | 0.0616 | 0.0757 | 0.0892 | 0.1023 | 0.1150 |
| lower bound on defect-free share | 0.9705 | **0.9534** | 0.9384 | 0.9243 | **0.9108** | 0.8977 | 0.8850 |

X_crit = 0.95 means at most 1 critical defect; X_crit = 0.93 would allow 2. X_any = 0.90 means at most 4 any-field
defects; 0.89 would allow 5. The sitting sets X; the rule form is the point.

**Planted rows: probability a reviewer with true detection rate theta flags >= k of 10:**

| k | theta 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 0.95 |
|---|---|---|---|---|---|---|
| 7 | 0.172 | 0.382 | 0.650 | 0.879 | 0.987 | 0.999 |
| **8** | 0.055 | 0.167 | 0.383 | 0.678 | **0.930** | 0.988 |
| 9 | 0.011 | 0.046 | 0.149 | 0.376 | 0.736 | 0.914 |

One-sided 95 % Clopper-Pearson lower bound on detection for k/10: 8 -> 0.493, 9 -> 0.606, 10 -> 0.741.

## 4. TEMPLATE for the R-06 amendment (Kush writes it in his own words)

> **TEMPLATE, NOT TEXT TO PASTE.** Under D-071 and REV-B B2.1 an amendment to a ruling is human-only. The agent must
> not write, commit or relay this entry. Kush writes every sentence himself, from his own session; the bracketed
> prompts say what the entry has to contain for the R1 gate to be valid. Needed only for Options A, C or E.

```
### D-0NN · 2026-11-__ · <your title> (decided by Kush; written and committed by Kush)
- Scope: [in your words: this changes D-027 R-06 for attempt 07.A-R1 only; v4 and any later attempt keep R-06]
- Gate for 07.A-R1: [the option you chose (A, C or E) and its numbers: AC1 bound, X_crit, X_any, planted k of 10,
  critical-field set]
- The v4 result: [in your words: FAILED stays on record, pooled kappa 0.0, raw agreement 0.9944, 900 cells,
  5 disagreements; it is never rescored or relabelled]
- Why the statistic changes: [your reason, e.g. the kappa paradox; and that the report will say "gate redefined
  after a failed gate"]
- Cards amended for R1 only: [Step 07 card pass gate, Step 15 G15-g and Step 23 G23.7 lines that say "AC1
  diagnostic only"]
- What a PASS opens: [nothing before 25 Nov; 23b stays BLOCKED until 15b is frozen (R-05, D-075)]
- Timing: [written before either signature file of the 07.A-R1 prereg exists; no R1 label exists]
- Approver: Kush
```
Cites to include: D-027 R-06, R-20, D-075, and REV-B Q24. Parv's agreement, if any, is Parv's own line (not relayed).

## 5. Code needed so every gate item is computable (agent work, Mac; not done by this lane)

| Item | Where | Change | Option |
|---|---|---|---|
| Bootstrap-bound gate | `src/culinarystate/evidence/condition_agreement.py` `score` L148 | gate on `_bootstrap(...)[0] >= 0.95` instead of point `ac1 >= THRESHOLD_AC1` | A |
| Critical set | same, `CRITICAL` L18 | add `duration_judgement`, `temperature_value_judgement` (as an R1 constant; v4 tools untouched) | A |
| Provenance | same, `_provenance` L81-L91 | drop `IDENTICAL_JUDGEMENTS`; add reason-overlap count; receipt-time check needs the receipt log as input | A, C |
| Planted rows | new `planted_detection(key, a, b)`; builder `tools/step07ar_build_packet.py` gains planted rows + U1 sub-quotas, new output names (it refuses to overwrite) | A, C, P1/P2, U1/U2 |
| Co-gate | new tool `tools/step07ar_accuracy_cogate.py` (reads the adjudicated CSV, writes `reports/step07/07A_R1_accuracy_cogate_result.json` once, Clopper-Pearson via `scipy.stats.beta`) | A, C |
| Diagnostics | `score` diagnostics block | q-category PABAK, informative-cell AC1 (needs `normalised_*` status, as `tools/step07_agreement.py` L80 parses it), positive specific agreement, per-source agreement | all |
| Kappa gate mode | `score` with `statistic="KAPPA_R06"` reproducing `tools/step07_agreement.py` L61-L71, L85 and writing to the R1 result path | B |
| Tests | `tests/unit/test_s171_07ar_agreement.py` L57, L69, L75 assert the 0.80 point gate and `IDENTICAL_JUDGEMENTS`; `tests/unit/test_s171_07ar_packet.py` asserts the quota | update with the chosen option |

## 6. Hash after lock

The Mac scribe applies the chosen blocks to the base file in one commit, then everyone hashes the committed blob,
not a working copy:

```bash
# from the repo root, after the lock commit <LOCK> exists
git show <LOCK>:reports/step07/07A_R1_preregistration_DRAFT.md | sha256sum      # macOS: | shasum -a 256
sha256sum reports/step07/07A_R1_preregistration_DRAFT.md                        # must print the same hash
git diff --exit-code <LOCK> -- reports/step07/07A_R1_preregistration_DRAFT.md   # must print nothing
sha256sum reports/step07/07A_R1_preregistration_AMENDMENT_S178_DRAFT.md         # provenance, goes in the lock record
```
The lock record (`reports/orchestration/PREREG_LOCK_2026-11-10.json`, proposed) carries: the prereg sha256, the base
sha256 above, this draft's sha256, the new packet sha256 (both copies), the planted-key sha256, the lock time. Each
signer compares the first command's output with the lock record before typing a signature file; if they differ,
stop.

Sources: ops pack #2 and §3; consensus §4 and T2-C05-R5/R7, T9-C26-R5; REV-B Q24, F-01..F-07, G-01, G-17; D-027 R-06,
R-20; D-075; D-071; `condition_agreement.py`; `tools/step07_agreement.py`; `07A_R1_packet_manifest.json`.
