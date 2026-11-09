# S178 RELWORK: targeted related-work re-search (board item T0-C02-R1)

Status: **AI_DRAFTED · PROPOSED · NON_CITABLE until a human opens the sources**. This is not a human gate, signature or approval.
Lane RELWORK, worktree `max/s176-orchestration` @ `07fc0d2+uncommitted` plus S175/S177 merges, 2026-11-09.

**What I wrote:** only the two files below. No ledger, registry, board CSV, WORKLOG, DECISIONS, STATUS or handoff file was touched,
and there was no git write. `tools/log_step.py` was not run because WORKLOG is orchestrator-only under the S176 brief.

## 1. What was built

**Deliverable:** `reports/s178/related_work/related_work_2026-11.md` (542 lines, about 9,600 words). It covers six themes:
- procedural/recipe state tracking;
- food KGs and process-aware food QA;
- cooking simulation linked to recipes;
- nutrient retention from recipes;
- RAG with abstention and evidence sufficiency;
- agent memory.

Each theme has a closest-works table (what the work does, and what CulinaryState does differently) and a calibrated novelty block
(can claim / cannot claim / needs an experiment). The file also contains:
- a cross-theme map of which work covers which link of the chain (§4);
- seven experiments that would turn hypotheses into claims (§5);
- errata for other files (§6);
- a bibliography of **67 new works** (§7), with 15 marked core for the report and slides;
- the negative searches (Appendix A).

**Verification.** Every row was opened on a primary page or an authoritative index: ACL Anthology, arXiv, OpenReview API, Crossref,
Europe PMC, OpenAlex or the publisher. The flags break down as follows:

| Flag | Rows | Meaning |
|---|---|---|
| YES-2 | 18 | Opened by a search lane and again independently by the lead. This covers all 15 core rows except PizzaCommonSense, Kümpel and Trust-Align, which are YES-1. |
| YES-1 | 47 | Opened once. |
| PARTIAL | 2 | Metadata only (Gil-Gaxiola 2025/26; Kato & Hasegawa 2013). |

No row is unverified. Items that were seen but not opened are listed separately and are not cited.

**Load-bearing full-text statements.** The lead confirmed these in the full text, and they are paraphrased in the deliverable:
- Vijayakumar et al. 2024: only 42.62 % of recipe ingredients were matched to a retention factor.
- Kalra et al. 2020: no consolidated cooking-yield resource exists.
- Yun et al. 2025: the authors call for nutrient databases that reflect cooking conditions.

**Method.** Three general-purpose search agents ran in parallel, two themes each, with explicit "do not fabricate; open every source"
rules. The lead then spot-checked the core items and every 2026 item that a novelty claim depends on, and made all editorial and
novelty judgements. About 70 queries were run.

## 2. Files

| Path | sha256 |
|---|---|
| `reports/s178/related_work/related_work_2026-11.md` | `46ceca190bae4af5cd3ee64d95e5d1f3b57940bc2cbeaed0418bec379ff4e526` |
| `reports/orchestration/S178_RELWORK_report.md` | this file |

Scratch (not committed; session scratchpad, deleted at the end of the lane): downloaded full texts used to confirm the three
statements above, and the v2 citation list.

## 3. Tests and runs

- **Tests:** none apply (documentation only). Checks I ran:
  - each bibliography row has a flag (67 of 67);
  - core count is 15;
  - no verbatim third-party passages: quotes were converted to paraphrase, under law 6;
  - no personal details, hosts or credentials (the repo is public).
- **Compute runs:** none. Web lookups only; no corpus, ledger or GPU use, so there are no `compute_runs_v1.csv` rows.

## 4. Key findings (for the orchestrator)

**Nothing found joins the CulinaryState chain.** That chain is:
1. recipe text;
2. deterministic event replay into lots;
3. per-event conditions with text-stated versus assumed values kept apart;
4. a physical model;
5. evidence-applicability gates;
6. deterministic ASK/ABSTAIN.

The nearest work for each link:

| Link | Nearest works |
|---|---|
| States | PizzaCommonSense (Findings EMNLP 2024), SIMMER (COLM 2026 per arXiv) |
| Conditions | Kumbhakern et al. 2025 (hand-encoded, one recipe) |
| Physics | Digital twins, sensor-driven (Kannapinn et al., J. Food Eng. 2026) |
| Nutrients | Vijayakumar et al. 2024 (default-method retention factors, 42.62 % factor coverage); FoodBench-QA 2026 (ingredient sum, always answers) |
| Abstention | Adaptive-RAG (learned router), Trust-Align (trained refusal), ClinDet-Bench (ACL 2026; determinability under missing data, the closest to our Kleene gates) |
| Memory | Eywa (preprint 2026, "evidence before belief"), MIRIX, event-sourced agent runtimes (2026 preprints) |

**Status corrections:**
- Self-RAG is ICLR 2024 oral, so v2's "venue not verified" can be dropped.
- CRAG is an arXiv preprint only (its ICLR 2025 submission was withdrawn).
- CoALA is TMLR 2024.
- MemGPT is a preprint, with no venue found.

**Resolved:** R&D plan v2 [S34], the "must appear in the novelty audit" item, is Kümpel et al., Frontiers in Robotics and AI
12:1682031 (2025). It has no temperature values and only an empty "duration" slot. Its authors note that their action groups do not
yet model cooking processes.

## 5. Board item status

| item_id | New status | Evidence | What is left |
|---|---|---|---|
| T0-C02-R1 | **DONE (AI part)**: acceptance met. Every row has an opened-source check, and every gap sentence is worded as a hypothesis bounded by Appendix A. | `reports/s178/related_work/related_work_2026-11.md` §0, §3–§4, §7 | The 1–2 h human read (W4 / 22–23 Nov edit) before any citation goes into the report, slides or paper. Humans must open the core rows themselves. |

## 6. Open questions and human decisions

1. **Memory-class wording.** SSOT §233.7 lists Source / Semantic / Episode-session / Evidence / Model, with simulation inside Model.
   The 36-step USP map lists source / evidence / state / model / simulation ("F-6 pending"). Pick one list for the report and slides.
2. **Errata to `research_bibliography_v2.md`** (Self-RAG venue; keep CRAG as a preprint). The orchestrator or a human should apply
   these. This lane did not edit v2.
3. **Concurrent-work preprints.** Decide whether to cite single-author 2026 preprints (Eywa, The Log is the Agent, PROJECTMEM) as
   concurrent work, or to leave them out of the slides. This lane recommends a footnote-level mention only.
4. **E1 and E2 before 25 Nov** (§5 of the deliverable):
   - E1 is a human audit of 100 gate decisions, about 1 h.
   - E2 is a counts-only run comparing default-method retention with gated routes on the 1,000 sample. It is cheap and would make
     novelty claim 2 much stronger.
5. **Kalra et al. 2020** is a prior IIIT-Delhi paper. Frame it as the predecessor whose stated gap we address, not as a weak
   baseline.

## 7. Summary: three defensible claims and three to avoid

**Defensible**, each worded as a hypothesis or a measurement:
1. **Integration.** In a bounded 2023–2026 search, no system replays recipe text deterministically into lot state, attaches stated
   versus assumed physical conditions, and uses them to decide whether a food-science answer is supported. The integration is the
   contribution; no single part is.
2. **Evidence applicability is separate from retrieval.** The target-presence and lot-context gates cut vitamin C DIRECT routes from
   450 to 73 on the fixed sample. Prior recipe-nutrient work applies factors by a default method, ignores cooking, or imputes until
   every profile is complete.
3. **Recipe text under-determines physics, measured at scale.** Only 3.3 % of heat events state both time and temperature, and the
   missing values stay UNKNOWN. Prior work names this gap but does not measure it.

**Avoid:**
1. "First" state tracking or event sourcing for recipes.
2. A "novel memory architecture" (CoALA, MIRIX and Eywa cover it).
3. "Calibrated", "guaranteed", "beats RAG" or "digital-twin simulation". H1 and H3 are untested, there is no calibration set, and no
   simulator is validated.
