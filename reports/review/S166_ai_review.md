# S166 AI cross-review: prv (Parv persona) and ksh (Kush persona), 2026-11-06

Status: **prv items PASSED by Kush and Parv (D-054); ksh items AI_VERDICT_PENDING_HUMAN_REVIEW (block K)**.
Two read-only AI reviewers. Neither edited, committed or ssh'd anything; both printed counts, hashes, code and
synthetic strings only. AI review is not human verification (D-045).
- **prv** reviewed PR #8 (S165 Step 19 salt, guards, commit step; head `021a1e0`) and the S166 Step 17b provenance block.
- **ksh** reviewed the S166 Step 26g census tool and its 1,000-recipe rerun (`d7482ed`, `21c9a74`, `d44495b`, `9d195de`).

Main-session checks before review: PR #8 Mac subset 437 passed; vinayak-server full suite 3,242 passed, 3 failed + 11
errors, all no-`.git` or Mac-only git-ignored files (identity parquets, `deep_gold_sampling_frame_v1_DRAFT.csv`).

## prv: PR #8 and Step 17b provenance

| ID | Verdict | Reason | Disposition |
|---|---|---|---|
| P1 | REJECT (J7 not met) | Tracked `packets_P1_<L>.csv` kept `content_sha256` = sha256 of public recipe content; recipe ids are public in `manifest_P1.csv`. prv mapped 7/7 superseded B packets to recipes without the salt. | **Fixed** (S166). The main session found two more links of the same kind: `file_sha256` (a blank packet is fully determined by the public packet id and recipe) and the plain sealed-key hash (one of 7! = 5,040 mappings). Tracked values are now salted commitments `sha256(salt|hash)`; per-packet line/step counts dropped. Test `test_s166_pilot_unlinkable.py` runs the public-data attack. |
| P2 | ACCEPT_WITH_CHANGES | `read_salt` sound; nothing stops A and B sharing a salt; a patterned salt passes the format check. | **Fixed:** the other letter's tracked salt is refused; salts need >= 12 distinct digits and no period <= 32. |
| P3 | ACCEPT_WITH_CHANGES | Re-issue undocumented when old local B files exist (the maker refuses to overwrite). | **Fixed:** packet-maker docstring: move the old local `<letter>/` folder and `sealed_key_P1_<letter>.json` out of the repo first. |
| P4 | ACCEPT | Commit-step guards hold (validated ids, order, DONE hash, MISSING/EXTRA, exclusive write). | — |
| P5 | Recommendation | FIRST_VALIDATE is self-attested (a PV-10 limit to state); `expected_ids=None` bypass. | `expected_ids` now required. Self-attestation stays a stated limit. |
| P6 | ACCEPT | Tests fail against the pre-fix code. | — |
| P7 | ACCEPT | `code_provenance()` closes S163 prv P2 for new runs; null (not wrong) on the no-`.git` server copy. Old JSONs keep no block. | — |
| P8 | Recommendation | Provenance taken before a 3.5 h run; `.DS_Store`/`._*` under `src/` would enter the tree hash. | Follow-up (block K, K9). |

## ksh: Step 26g census

| ID | Verdict | Reason |
|---|---|---|
| K1 | ACCEPT | Chain matches `rung_a_measure` (text join, locale, schema, `seeded_sample`). Independent temp-dir rerun: census block, `census_sha256` `7e660634…` and 23,943 events equal Parv's file; only `adapter_invented_excluded` (2 → 0) and `chain` differ. |
| K2 | ACCEPT_WITH_CHANGES | The 2 → 0 comes from the **S161 `º` rule**, not the S163 deg-prefix fixes: Parv-era auditor (`5b837f8`) gives 2, `020d877` gives 0, HEAD gives 0, census identical in all three. Correct the attribution. |
| K3 | ACCEPT | No text/id leak path; refusals and baseline check hold. `seeded_sample` keeps the sample in memory (~3 GB at full corpus): server only. |
| K4 | ACCEPT_WITH_CHANGES | Tests would miss a wrong stage order, a wrong locale or a sample other than `seeded_sample`; one assertion is tautological; exit codes 3/4 untested. |
| K5 | ACCEPT_WITH_CHANGES | The committed 1,000 JSON was made with `git_dirty: true` at `f34bde9`; hashes trace it, but rerun clean before citing. |
| K6 | Recommendation | J8 closable: a committed, tested tool exists, and the old census was in effect not stale (census block unchanged). |
| K7 | ACCEPT_WITH_CHANGES | All 23,943 events SIM_PROHIBITED is true by construction (no condition or applicability bindings exist yet), but only the module docstring says so; add `bindings_supplied` / `prohibited_by_construction` to the JSON. |

Correction to the main session's S166 summary: it attributed the 2 → 0 to the S163 auditor fixes; K2 shows it is the S161 `º` rule.

## Annotator A's P1 packet build (2026-11-06, commits 0c5b494, ba843f0, 5e5782a): ksh (owner view) and prv (attacker view)

Built on Kush's Mac with the fixed maker and the D-057 salt. prv used only public and tracked data and did not open A's key, packets or salt.

| ID | Verdict | Reason |
|---|---|---|
| KA1–KA5 | ACCEPT | ksh: salt and salted key commitments verify; all 7 rows' salted file/content hashes verify; 7 pristine gold-1.0 packets (annotator Kush, DGP-A-0001..0007, no AI prefill); key recipe set = the 7 PRIMARY ids of `manifest_P1.csv` (sha256 verified); salt 0600 in a 0700 directory outside the repo; key, packets and snapshot log git-ignored; no B material on the Mac. |
| KA7 | ACCEPT | `gold_cli.py validate` runs (blank packet fails as unfinished, as expected); the commit step reads `packets_P1_A.csv`. |
| PA1–PA6 | ACCEPT | prv: 0/28 tracked salted hashes match any of 49 rebuilt (packet id, recipe) docs or 7 content hashes (plain or re-hashed); 0/5,040 key mappings match; ~300k low-entropy salt guesses fail; no ids, counts or text in the three files; row order and sizes non-informative; build used the fixed code path. |
| PA7 | ACCEPT_WITH_CHANGES | `superseded_s164_unsalted/` (B's old unsalted list) is still tracked and still links B's old packets to recipes; unused by A's build. |
| KA8 / PA8 | Recommendation | `tools/step19_packet_maker.py` calls `main()` without an `if __name__ == "__main__"` guard (importing it runs the tool). |
