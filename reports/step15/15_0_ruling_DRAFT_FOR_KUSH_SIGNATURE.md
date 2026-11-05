# 15.0 ruling: draft for Kush's signature (NOT A DECISION)

Prepared 2026-11-04 at Parv's instruction ("use the commonly agreed fractions"). Not signed: the 15a.R tool only accepts a `### D-NNN` entry in DECISIONS.md whose Approver line names Kush, and no agent may write that. Kush copies the block below into DECISIONS.md (changing any value) to authorise the seal.

Values (from `pre_freeze_rulings_DRAFT.md`, section 7): C2-a, H-3 for 15b (TB-V0 order for 15a diagnostics), X-1, G-1, K-1; RESERVED fraction 1/5 (the common 80/20 split); unit STUDY_THEN_CELL; stratify SOURCE_FAMILY.

Seed: generated with Python `secrets` (48 hex characters) on Parv's Mac, stored at `~/.culinarystate_private/15aR_seed.txt` (outside git, mode 600), never printed. Only the sha256 below is published. Kush may replace it with his own seed and hash; the tool needs the seed file at seal time on the machine that runs it.

Effect to expect: floor(1/5 x n_groups) per stratum, so Phenol-Explorer (125 publications) reserves 25; USDA and Bognar are each one cluster, so they reserve cells but add no independent test cluster.

```text
### D-0NN · 2026-11-0N · Step 15.0 pre-freeze rulings (decided by Kush; entered as scribe)
- **Decision:** C2-a, H-3 (15b) with TB-V0 order for 15a diagnostics, X-1, G-1, K-1 as in reports/step15/pre_freeze_rulings_DRAFT.md.
- **15.0 RESERVED_FRACTION:** 1/5
- **15.0 RESERVED_UNIT:** STUDY_THEN_CELL
- **15.0 RESERVED_STRATIFY:** SOURCE_FAMILY
- **15a.R SEED_SHA256:** d3075c68bc54fe6fe7f4c20bf12527ad7be18e62acf6511e1c5c4080314c3e54
- **Approver:** Kush
```

Then, on Parv's Mac:
`python tools/step15a_R_seal.py check --decision D-0NN --seed-file ~/.culinarystate_private/15aR_seed.txt --sealed-out ~/.culinarystate_private/15aR_sealed_list.json`, and `seal ... --execute` only after the check is clean.
