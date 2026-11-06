# P1b design amendment (PROPOSED, 2026-11-06; D-069 P1b yes, D-070 O5; needs Kush's signature)

**Purpose.** A short rule check of the stamped Addendum B (D-070) on NEW recipes before P2, as prv proposed (S166 triage). P1 and P1b are different measurements; P1 labels are never edited or re-scored. Under D-045 W2 / D-060 the P1b labels are again human-accepted AI drafts, so P1b is calibration of the handbook, not reliability evidence (both annotators have seen the P1 disagreements).

**Human facts needed (the agent never supplies them):**
1. Size: 3 or 4 PRIMARY recipes (prv: 3–4), drawn across the same 7 strata with no group used in P1 (all 21 P1 manifest rows and their groups excluded).
2. A new pre-frame nonce written by Kush (design 4.5; `pilot_real.check_prerequisites` refuses `NONCE_SUPPLIER_NOT_KUSH`), committed by sha256 before the frame is rebuilt; seed = SHA-256(frame_sha256 || "P1b" || nonce) per the existing rule.
3. A signed amendment to the start record (`reports/step19/pilot_start_record.SIGNED.json` covers wave P1 only): H5 authorisation for wave P1b, the P1b budget against THR-19P-14/15 (40 h cap; P1 timing was not measured, D-061), and the reserve rule (THR-19P-09 unchanged).
4. Who annotates: as P1 (ksh AI pass for A, prv for B, cross-checks, human stamp), B again on Kush's Mac in the separate clone while Parv's laptop is down (D-064 deviation repeated) — or Parv on his own machine if it is back.

**Tooling changes (AI remit, test-first, once 1–3 exist):**
- `pilot_real`: accept wave `P1b` only when the signed record lists it; exclude every recipe and group of earlier waves' manifests.
- `pilot_commit.WAVE_RE`: allow `P1b` (`P[0-9]+[a-z]?`).
- `step19_packet_maker.py` and `step19_commit_step.py`: `--wave`; per-wave local folders (`annotation/gold/deep_gold_pilot_v1/<wave>/<letter>/`) and wave-scoped file names (`manifest_<wave>.csv`, `packets_<wave>_<letter>.csv`, `sealed_key_<wave>_<letter>.*`, `salt_<wave>_<letter>.sha256`, new salts per wave); P1 paths unchanged.
- `step19_p1_score.py`: score any wave with the same commitment and salted-key checks.

**Scoring and reading.** The same scorer and THR-19P-16/-31 gate; the question is whether the Addendum B categories (coref, event_type, entity_type, event_argument, final_state) fall below 0.20, reported as a handbook calibration check.
