# Step 07 condition audit — protocol amendment v4.1 (DRAFT, UNSIGNED)

Applies to the returned files of packet v4 only. Packet v4 (sha256 `533c49ba9a55ec06f4c4a5f77a065d1946b4cc7ae787e36689ac1cbb56118571`, normalizer fingerprint `e7d589136275…`) is NOT edited. Primary gate unchanged and kept verbatim: **pooled Cohen's kappa >= 0.80 AND no systematic critical-field disagreement** (temperature location, pressure reference, basis, retention type, censoring), computed by `tools/step07_agreement.py`.

## 1. Provenance-validity precheck (new, runs first)
`python tools/step07_provenance_precheck.py <Kush_completed.csv> <Parv_completed.csv>` writes `reports/step07/step07_v4_provenance_precheck.json`. The gate result counts only if status is `VALID`:
- header and audit_id set equal the frozen packet;
- every non-judgement cell equals the frozen packet (raw source fields and normalizer output unchanged);
- the two files are not byte-identical;
- mtime separation at least the recorded parameter (PROPOSED 600 s; an indicator, not proof of independence);
- sha256 of each returned file is recorded before the other is opened (Kush records his hash, Parv records hers, in a note committed before either reads the other's file).
The tool reads files only; it never edits or fills a label. It is tested in `tests/unit/test_step07_provenance_precheck.py`. Metadata can only show non-independence; it cannot prove independence.

## 2. Added diagnostics (do not change the pass criteria)
For every field, report raw agreement, positive and negative agreement, and PABAK (and Gwet AC1) when the dominant-code prevalence is above 0.9. `step07_agreement.py` already prints raw agreement and the prevalence warning; the extra statistics are reported alongside, never instead of, pooled kappa. Every disagreement on a high-prevalence field is human-adjudicated (never by an LLM).

## 3. Not adopted
Per-field kappa >= 0.80 as a mandatory criterion; separate per-reviewer packet IDs (would require editing the packet); any change to cases, fields or examples.

## 4. Order of operations
Approve this amendment (D-028) -> reviewers work alone and blind from the unchanged v4 files -> each records the sha256 of the returned file -> run the precheck -> run the agreement tool -> report every disagreement without automatic adjudication -> only then, outcome PASS / FAIL_REVIEWER_DISAGREEMENT / INVALID_AUDIT. If the frozen files change after review starts, the audit is invalid (`python tools/step07hr_freeze.py --verify`).

**Recorded deviation (2026-10-27):** signed AFTER both reviewers had returned their labels (the order of operations above requires approval before any v4 label exists). The primary gate (pooled kappa >= 0.80 and no systematic critical-field disagreement) is unchanged, and no label was edited after the file hashes were fixed (`step07_v4_hash_notes.md`). The report must state this deviation.
**Time-gap ruling (Kush, 2026-10-27):** the mtime separation check is INFORMATIONAL, not a validity condition. The 48 s gap between the two returned files is disclosed; it reflects when each file was saved into the folder. The precheck was run at both 600 s (INVALID_PROVENANCE, only on this item: `step07_v4_provenance_precheck_gap600.json`) and with the gap rule informational (VALID: `step07_v4_provenance_precheck.json`).
**Blind confirmation (Kush, 2026-10-27):** Kush confirms neither reviewer opened the other's returned file before the hashes were recorded.

Signed: Kush Tokas, 2026-10-27   |   Parv: ____________ (signature pending; Parv has not signed)
