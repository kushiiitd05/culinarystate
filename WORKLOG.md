# WORKLOG — CulinaryState (Group 17: Kush + Parv)

Append-only, sequential, timestamped (IST). One entry per step. Written by `tools/log_step.py`; never edit past entries — add a correcting step instead.

Presentation: **25–26 Nov 2026**.

### S001 · 2026-10-18 10:43 IST · B00 · Repo scaffold + Bible docs
- **Who:** Kush+Claude
- **Did:** Created culinarystate/ repo (git init, main). Copied SSOT v15, master plan v4.0, R&D plan v2, Max prompt v2, proposal PDF into docs/. Package skeleton src/culinarystate/* and tests/. Found Parv's old repo absent on this machine → rebuild here (D-001).
- **Files:** `docs/`, `src/culinarystate/`, `.gitignore`
- **Verified:** ls tree present

### S002 · 2026-10-18 10:43 IST · B00 · Step logger
- **Who:** Kush+Claude
- **Did:** tools/log_step.py appends timestamped (IST), sequential S### entries to WORKLOG.md; append-only.
- **Files:** `tools/log_step.py`, `WORKLOG.md`
- **Verified:** this entry written by it

### S003 · 2026-10-18 10:43 IST · B01 · SSOT index built and verified
- **Who:** Kush+Claude
- **Did:** tools/build_ssot_index.py: H1–H3 headings with line ranges, ID anchors (RQ16, RQ13E, E16, E13E, G13E, G16, G15, G14, G13, RISK-E, R13E), boxed statements. Checked against plan Appendix 1.
- **Files:** `tools/build_ssot_index.py`, `docs/SSOT_INDEX.md`
- **Verified:** all 14 inventory checks OK (1,799,542 bytes; 45,697 lines; 309 H1; 30/30 RQ16; 14/14 G16; 18/18 G15 …)

### S004 · 2026-10-18 10:43 IST · B02 · Source reachability probe (no API key)
- **Who:** Kush+Claude
- **Did:** Single requests only. Reachable: RecipeDB/FlavorDB/CulinaryDB web pages (200), USDA R6 PDF (200), Phenol-Explorer (200), FDC API DEMO_KEY (200), PubChem PUG-REST (200), FoodOn OWL (200), HF datasets API (200). RecipeDB recipe2-api: timeout. cosylab robots.txt: 404. Local: A1 11,934 BBC recipes + TASTEset NER gold.
- **Verified:** HTTP codes recorded
- **Next:** SNAP-/API- records when ingesting

### S005 · 2026-10-18 10:43 IST · B00 · STATUS / DECISIONS / CLAUDE.md
- **Who:** Kush+Claude
- **Did:** STATUS.md with COMPLETE/ACTIVE/BLOCKED, dated W1–W6 plan to 25–26 Nov, next 20 tasks. DECISIONS D-001…D-004 (rebuild here; JSON Schema over pydantic; A1 BBC + TASTEset as RecipeDB stand-ins; base python).
- **Files:** `STATUS.md`, `DECISIONS.md`, `CLAUDE.md`

### S006 · 2026-10-18 10:49 IST · B00/P2 · Core ledger schemas + ID minter + validators
- **Who:** Kush+Claude
- **Did:** 36 record types (SRC SNAP API STUDY MEAS ING ALIAS ENTITY MOL IMAP PROC TOOL COND SVAR UNIT QNT POR ALLOC REC INST EVT STATE REF GRAPH EVD RXN WARN ALLERGEN DATASET SPLIT MODEL EXP GATE RQ RS CLM) as JSON Schema 2020-12 with common envelope (version, status, provenance, verification). UNKNOWN-aware QVALUE (UNKNOWN/QUALITATIVE can't carry numbers). Laws in rules.py: AI≠human verification; E4 needs HUMAN_VERIFIED; AH1 origin_type/study_ids; locator for E1–E4; percent-change consistency; censor flag; no invented grams (QNT needs POR for non-mass units); POR needs source; IMAP 4 relation types; 'medium heat' never numeric; STATE append-only + observation override; FlavorDB never allergen authority; SOTA claim needs GATE; TEST-selected checkpoint ≠ clean reproduction. Append-only JSONL store with versioned revise(); IdMinter dedups by key, never reuses numbers.
- **Files:** `src/culinarystate/ledgers/`, `tests/unit/test_ledgers.py`, `tests/fixtures/ledger_examples.py`, `ledgers/schemas/`, `tools/export_schemas.py`, `pyproject.toml`
- **Verified:** pytest 103 passed; mutation check: disabling each of 10 rules makes ≥1 test fail
- **Next:** S007 DEL-1: USDA R6 retention factors → EVD (E3)
