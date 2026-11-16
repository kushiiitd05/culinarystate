# S176 lane DEPLOY: deployment, demo and presentation plan

Status: PROPOSED / AI_DRAFTED. No ledger, registry, DECISIONS, WORKLOG, STATUS or SSOT file was edited. No install, deployment, account, git write or network write was made.
Worktree `~/kush_work/culinarystate/.orch`, branch `max/s176-orchestration`, HEAD `1924c6f` (the brief said `07fc0d2`; the orchestrator has since committed S175 docs), uncommitted.

## What was built

| File | What |
|---|---|
| `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md` | the plan asked for: (1) runtime architecture with mermaid diagram, measured data files and 14 gaps; (2) licence-based shipping rules and a data-bundle spec; (3) hosting and LLM options with a recommendation and an offline fallback; (4) runbook, controls table, 28-row smoke list, rollback; (5) storyline, 14 + 6 slides mapped to result files, dates and fallback levels L0-L3, live-demo script, 24 Nov rehearsal checklist; (6) links index template |
| this report | |

Nothing else was written in the repo. Scratch (not in the repo): `/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad/deploy/` (`probe_demo.py`, `probe_demo2.py`, outputs and logs).

## Tests and checks run

- `nice -n 10 .venv312/bin/python -m pytest -q -p no:cacheprovider tests/unit/test_s173_app_server.py test_s171_front_door.py test_s171_query_router.py test_s171_demo_context.py test_policy.py test_enforce.py test_generation.py`: **70 passed, 1 deselected** (26.7 s). The deselected test is the real-ledger test (marker `ledgers`).
- Router-only check of 17 questions through `query_router.route` (no ledger).
- Two read-only probes of the real `DemoContext.load()` plus `respond()` on 32 questions (the first start failed: `ModuleNotFoundError: lxml`; both runs used a scratchpad-only `lxml` stub, which the demo path never calls).
- Ledger counts by a read-only scan (EVD by source, vitamin C rows by source, KGE demo predicates and their family tags, troubleshooting rows by family).
- sha256 of the 20 data files the demo opens (table in plan s1.4).
- Web: Hugging Face Spaces overview and Render free-tier docs (fetched), searches on Render plans, Fly pricing and Cloudflare quick tunnels.

## Runs (rows for `registry/compute_runs_v1.csv`, header `run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes`)

```
RUN-S176-DEPLOY-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),1924c6f+uncommitted,none (ledger-only; no recipe text opened),1,"nice -n 10 .venv312/bin/python -I -u probe_demo.py probe_out.json (DemoContext.load + 16 respond calls; lxml stub)",/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad/deploy/probe_out.json,7ee0782727fbb007c54a29f6cf3d795068e916825ba4d241214f8f61f6c5a9f4,2026-11-08T19:11:09+05:30,2026-11-08T19:22:09+05:30,DONE,"load 644.8 s wall at load average ~185; peak RSS 1216 MB; 20 repo files opened; scratchpad only, not committed"
RUN-S176-DEPLOY-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),1924c6f+uncommitted,none (ledger-only; no recipe text opened),1,"nice -n 10 .venv312/bin/python -I -u probe_demo2.py probe_out2.json (DemoContext.load + 16 respond calls; lxml stub)",/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad/deploy/probe_out2.json,f0ab8912fcdb4839126c03543f25811928da20d2a2ec190af49250837c5ba41b,2026-11-08T19:21:10+05:30,2026-11-08T19:25:53+05:30,DONE,"load 282.8 s wall; peak RSS 1242 MB; scratchpad only, not committed"
```

Times are IST (+05:30). Both runs were single-process and niced; the server's load average was about 185 throughout, so the timings are upper bounds.

## Findings the orchestrator should know (details and evidence in the plan)

1. The demo cannot start in `.venv312` (no `lxml`; `vocab/foodon.py` imports it at module top). `pyproject.toml` has no runtime dependencies and there is no requirements or lock file.
2. Hugging Face Docker and Gradio Spaces now require a paid plan; only Static Spaces are free. Render free is 512 MB / 0.1 CPU and cannot hold the demo (1.2 GB RSS, about 60 CPU-seconds to load). FINISH_PLAN M6 and `T8-C18-R2` assume a free host and need rewording.
3. The demo is stateless: `SessionState`, replay and B4 state conditioning are not called by the server path. The H1 task types (current state, next action) cannot be demonstrated.
4. A shipped example ("Swap buttermilk") is a BBC-only derived edge; REV-B Q36 and G-14 forbid BBC-derived examples on a hosted demo or slides.
5. Real-output weaknesses: router misses "fried"; green "Answered from data" badge on qualitative answers from unrelated foods; no safety refusal; the 27 Layer 2 defaults are all `SOURCE_UNVERIFIED_AGENT_RECALLED`; the physical estimate is printed without ASSUMED_DEFAULT chips.
6. Vitamin C evidence is entirely USDA (SVAR-000009, 270 rows) and Bognar (SVAR-000215, 153 rows); Phenol-Explorer (3,870 rows, redistribution needs permission) can be excluded from a public bundle without touching the four demo questions. The 6 KGE predicates the demo reads carry no Food.com family.
7. `reports/final/FINAL_REPORT_DRAFT_S168.md` is stale relative to S171-S175 (says D4 not started, no demo).
8. `handoff/FINISH_PLAN_2026-11-07.md` M6 says "FastAPI + UI"; the code is the Python standard library.

## Open questions and what a human must decide

Kush: H-1 to H-9 in plan s0.2 (approve the hosting shape; the licence calls H-2; the supervisor email H-3; the machine and Python for the demo H-4; static-page host H-5; `cloudflared` H-6; talk length and slot H-7; the screen recording H-8; any paid host H-9, default no). Parv: read the live-demo script and the "do not demo" list. Orchestrator: decide whether the agent tasks T-D1 to T-D7 (about 15-20 agent-hours, plan s4) go into the 36-step plan and who owns the `src/culinarystate/app` patches; fix the M6 wording; decide the DECISIONS entry for H-1 and H-2 (scribe agent). UNVERIFIED items are listed in plan Appendix B.
