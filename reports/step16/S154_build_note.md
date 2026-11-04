# S154 build note — Step 16 rc2 grounding integration and Step 19 real-pilot gate

2026-11-03. Cloud session on Kush's account, branch `cloud/s154-step16-integration-2026-11-03`.
AI engineering draft only: no human label, signature, H4/H5 verdict, expert review,
nonce, capacity or budget is supplied here. Status of every new contract piece is
DRAFT_PENDING_H4 (Step 16) or PENDING_H5 (Step 19).

## Environment caveat (read first)

The data bundle was **not** available in this session. The setup script's Google
Drive downloads were refused by the environment's network policy (proxy 403 for
`drive.usercontent.google.com`), and the 970 MB tier-1 archive is too large for the
Drive connector. As a result:

- the real-recipe dry-run (A3) was built and tested on synthetic fixtures only.
  **It has not been run over the real recipe base.** Its numbers do not exist yet;
- the baseline suite here had 12 data-dependent failures/errors (listed under
  Verification). They are missing-file errors, unrelated to this change.

The protected ledgers (`ledgers/data/*`) are tracked in git, so the 08a
baseline-hash check *did* run here and passed (7/7 files).

## A. Step 16 — what was built

All new modules are opt-in. The legacy grammar, normaliser and unit catalogue,
the rc1 drafts, the frozen v0 schemas, `draft_contract.py`, `parse_adapter.py` and
`versioned_normalizer.py` are byte-identical. No existing file was modified.

### A1. History-variable contract (`src/culinarystate/quantity/rc2_history.py`)

The inherited rc1 rule says the five history keys (cell_integrity,
enzyme_activity_state, time_since_disruption, thermal_dose, oxygen_exposure) are
never filled from recipe text: a populated value may use only a MODEL or
SIMULATED claim route. The JSON Schema checks only the inline `claim_route`, so a
value with `origin=EXPLICIT_SOURCE, claim_route=MODEL` passes it. The new
`check_history` / `validate_state_rc2`:

- checks both the inline `meta` and the sidecar `field_metadata` copy;
- rejects source-text origins or routes (`HISTORY_FROM_RECIPE_TEXT_FORBIDDEN`);
- reports externally measured history (`origin=EXTERNAL_VERIFIED`) as
  `HISTORY_EXTERNAL_POLICY_PENDING_H4`. It is neither accepted nor labelled as recipe text;
- reports origin/route pairs other than MODEL_ESTIMATED/MODEL and SIMULATED/SIMULATED
  as `HISTORY_ORIGIN_ROUTE_PENDING_H4`;
- returns issues only and never rewrites the record. Policy id: `HISTORY_RC1_INHERITED_MODEL_SIMULATED_ONLY_PENDING_H4`.

### A2. Opt-in rc2 grounding pipeline (`src/culinarystate/quantity/rc2_grounding.py`)

`ground_quantity_rc2(raw, GroundingContext(...), schema=<QNT rc2>)` wires
`parse_quantity_v2` (and through it `normalize_v2`) into one rc2 QNT record
candidate. It follows the Plan Step 17d order:

| Stage | Behaviour |
|---|---|
| Parse | Adapter AST and exact rational arithmetic. Raw text is kept byte-for-byte. Blank input is refused. |
| Unit resolution | `MASS_PHYSICAL`, `VOLUME_PHYSICAL`, `VOLUME_LOCALE_CONVENTION` (the caller supplies a locale with metadata), `VOLUME_LOCALE_AMBIGUOUS` (no locale or no convention for it: volume stays UNKNOWN), `REGIONAL_NO_STANDARD`, `COUNT`, `PACKAGE`. Conventions whose catalogue source is NEEDS_SOURCE are flagged `CONVENTION_NEEDS_SOURCE`. |
| Q0 conversion | Exact `Fraction` arithmetic: mass units, source-stated package content (`2 x 400 g` → 800 g; `0 x 400 g` → 0 g) and parenthetical source-stated mass (`1 cup (240 g)`), the last only when the main expression parsed. |
| POR selection | Only from caller-supplied records that are `HUMAN_VERIFIED` and `ACTIVE`, with exact equality on ingredient, unit id, state, form, packing and locale. A null facet matches only a null facet. 0 matches → `NO_COMPATIBLE_RECORD`; more than 1 → `AMBIGUOUS_POR_RECORDS` (no tie-break). The Q-level comes only from a caller-supplied basis→Q map. `CONVENTION` is never mapped by default (open ruling), so it yields `POR_Q_LEVEL_RULING_PENDING`. |
| Record | rc2 QNT candidate with explicit `field_metadata` for every claim target, `normalized_mass_low/high_g`, `SOURCE_RANGE` / `CONVERSION_UNCERTAINTY` intervals and a machine-readable `TRACE:` entry in `conversion_path`. |
| Checks | `validate_record` (rc2) plus a new `audit_invented_values`. Every gram value is recomputed from its trace (AST Q0, parenthetical, or a supplied POR) and must match exactly, together with the normalised bounds and the Q-level. |

The v2 compatibility channel is compared, not trusted. When the AST refuses an
expression but `normalize_v2` would still emit a mass, the mass is masked and
flagged `COMPATIBILITY_CHANNEL_MASKED`. Synthetic example: `1 lb plus 2 oz`, where
the legacy mass is 453.59 g because the `plus 2 oz` is dropped. Placeholder id
`QNT-000000` is used when no envelope is supplied. It is never minted or written.

### A3. Read-only, counts-only dry-run

- `src/culinarystate/quantity/rc2_dryrun.py`: aggregates integer counts per
  source family by mass route, unit resolution, AST root, arithmetic status,
  Q-level, flag code, validator/audit issue code, legacy-vs-rc2 mass status,
  and exceptions (by class name only).
- `tools/step16_rc2_grounding_dryrun.py`: reads the existing corpus iterators
  (`culinarystate.recipes.corpus`, the same ones used to build recipe_base_v1)
  and hash-checks the protected ledgers before and after the run. It refuses to
  start if that check fails (exit 2) and writes one new JSON file (never
  overwrites; refuses `ledgers/`, `data/`, `exports/`, `annotation/gold/`).
- No-text guarantee: `assert_counts_only` rejects any key or string that is not a
  short code token. Flag payloads after `:` are dropped; for example, the legacy
  grammar's `second_unit_ignored:<raw unit text>` becomes `second_unit_ignored`. Tests plant
  sentinel tokens in recipe ids and lines and assert they never reach the
  report or stdout. Exception messages are never recorded.
- Locale comes from the legacy source-family map used by the recipe base
  (`recipes.ledgers.LOCALE`: BBC=UK, Food.com=US, others unknown). No POR records
  and no ingredient links are supplied, so count/volume lines report
  `NO_INGREDIENT_LINK`. That is by construction, not a measured gap.

Run it locally where the bundle is extracted. It takes about 2.5 ms per line on one
core, so use workers:

```bash
python tools/step16_rc2_grounding_dryrun.py --workers 8
```

Output: `reports/step16/rc2_grounding_dryrun_counts.json` (counts only; safe to
commit after a look). Exit 3 means at least one family input was missing; the
report's `family_status` says which.

## B. Step 19 — real-pilot gate (`src/culinarystate/annotation/pilot_real.py`, `tools/step19_real_pilot.py`)

`check` lists every missing human prerequisite with its owner. `draw` refuses
unless that list is empty and `--execute` is given. It never edits the start
record and never supplies a nonce, signature, capacity, budget or H5 decision.

Output of `python tools/step19_real_pilot.py check --record reports/step19/pilot_start_record.UNSIGNED.json`
on 2026-11-03 (ready = false; design and bound-file hashes still match):

| Blocker | Owner | Meaning |
|---|---|---|
| START_RECORD_UNSIGNED | Kush+Parv | No signers or date. Both annotators are required; no single-signer override for the pilot. |
| H5_START_AUTHORIZATION_MISSING | Kush | No H5 start decision with a DECISIONS.md id covering wave P1 |
| NONCE_MISSING | Kush | Pre-frame nonce absent. Must be Kush-supplied, with `nonce_commitment` = SHA-256(nonce) and a timezone-aware `nonce_committed_at` |
| CAPACITY_MISSING | Kush | Weekly hours for Kush and Parv |
| BUDGET_MISSING | Kush+Parv | Per-annotator B_h |
| THRESHOLDS_NOT_SIGNED | Kush+Parv | 0 of 35 THR-19P rows are in the registry and signed |
| INSTRUMENT_NOT_SELECTED | Kush+Parv | Measurement instrument version not selected |
| PILOT_COLUMN_NOT_CONFIRMED | Kush | Parv chose `reserve_split_v2`; Kush has not confirmed |
| METHOD_AMENDMENTS_UNRESOLVED | Kush+Parv+expert | PM-01..12 / PR01..10 need a recorded ruling (`{status: RESOLVED, decision_id}`) |
| DRAW_SPEC_NOT_BOUND | Kush+Parv | Signed record must name `STEP19_P1_DRAW_SHA256_RANK_V1_DRAFT` |

Further checks that pass today but are enforced: design and bound-file hashes,
`real_draw_performed` false, nonce supplier is Kush, frame files newer than the
nonce commitment, frame/strata columns text-free and allowlisted, no existing
manifest (no redraw), and output never in protected paths. P2 is refused
(`WAVE_P2_NOT_SUPPORTED`): D19-10 and the tag-rule spec are open, and P1 is unfinished.

When every prerequisite holds, the P1 draw follows design §4.4–4.5 / THR-19P-07/08
with an explicit byte-level specification (module docstring). Output is a
text-free `manifest_P1.csv` plus `.sha256` in
`registry/recipe_semantics/deep_gold_pilot_v1/`: 7 primaries plus 2 ordered
reserves per cell, with no group used twice. The frame must be rebuilt
after the nonce. The existing draft frame predates it and is refused by the
mtime check. The tool takes the frame and text-strata CSVs produced by
`tools/step16b_build_frame.py` and `tools/step16b_text_strata.py`.

## Verification

| Check | Result |
|---|---|
| Baseline before changes (this container, no data bundle) | 1653 passed, 17 skipped, 1 deselected; 1 failed + 11 errors, all `FileNotFoundError` for bundle files (`recipe_base_v1.parquet`, `deep_gold_sampling_frame_v1_DRAFT.csv`, a gold split file) |
| New targeted tests (written first; each RED before its module existed) | history 18, grounding 78 (incl. 300-example hypothesis property: no generated gram lacks a trace), dry-run 16, real pilot 32 = **144 passed** |
| Full unit suite after (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) | **1797 passed**, 17 skipped, 1 deselected; same 1 failed + 11 errors as baseline (data absent) |
| Protected ledgers | `verify_baseline(registry/baseline_ledger_hashes_08a_v1.csv)`: 7/7 match |
| Existing files modified | 0 (`git diff --diff-filter=M` empty); `git diff --check` clean |
| Real start record | read only; bytes unchanged (asserted in test) |
| Real-data dry-run | **NOT RUN** (bundle unavailable here) |

Python 3.13.18 with jsonschema 4.19.2 and RDKit 2026.3.6 (installed per the setup
script). Not the Mac `/opt/anaconda3` environment, so rerun the suite there before merging.

## Engineering choices that need human review (not decided, listed)

1. Draw byte encoding. These are new specifics inside THR-19P-08; they must be bound by signature before use:
   - plain concatenation of frame-sha hex, wave and nonce;
   - frame_sha256 over the two CSV hashes;
   - SHA-256 rank as the "stable shuffle";
   - reserves also consume groups.
2. Underfilled cell (< 30 eligible) **stops** the draw instead of applying the
   design's source fall-through, because fall-through can break the signed quotas (PM-06).
   Humans choose the reallocation.
3. Pilot start requires **both** Kush and Parv as signers. The Step 35 guard's
   single-signer override is deliberately not accepted for a two-annotator pilot.
4. History policy: whether externally measured history is ever allowed, and the
   origin/route pairing rule. Both are reported as pending, not decided.
5. POR selection: exact facet equality with null≠value (never merge across
   state/form/locale); `HUMAN_VERIFIED` only. The basis→Q-level map is the open
   CONVENTION→Q3/Q4 ruling plus the "other approved national table" Q-level.
6. Dual-expression conflict is exact inequality of the two Q0 masses. The legacy
   path used a 25 % tolerance. No threshold was invented; H4 may want one.
7. The dry-run reuses the legacy family locale map (Food.com=US). That map is an
   existing assumption, not verified locale evidence.

## What still needs humans

- **Step 16:** H4 review of rc2 coverage/payload/arithmetic/wire conventions, the
  history policy (items 4–6) and this grounding order; Kush runs the real-data
  dry-run and reads the counts. POR records stay at 0 until humans verify them
  (D-006). 16c still waits for the Step 19 pilot.
- **Step 19:** every row of the blocker table above, in particular Kush's nonce
  committed *before* the frame is rebuilt, H5, both signatures, capacity and
  B_h, signed THR-19P-01..35, instrument choice, pilot-column confirmation and a
  ruling on the AI methods amendments (an expert is needed for PM-01..04).
- Unchanged: G08-3 FAIL and the 07.A FAIL stand; Step 35 domain reviews,
  crosswalk audit and all signatures remain open.

## Notes for Kush

- Parv's session notes and WORKLOG record **no permission error**. The only
  recorded blocker is that two delegated Step 35 chemistry/cuisine agent reviews
  "hit the service usage limit before producing reports" (S152, D-043). No exact
  error text, tool or location is recorded; his session ran on his Mac
  (`/Users/parvgoyal/...`). His branch push (S153) succeeded, and remote `main` now
  equals that branch head (`2154406`). Ask Parv directly for the exact message.
- In this session, the blocker was the environment network policy denying
  `drive.usercontent.google.com` (setup-script data download). To fix it for future
  cloud sessions, allow that host in the environment's network settings.
