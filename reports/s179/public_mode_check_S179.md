# Public-mode check on the Mac (S179, handoff §4)

Status: AI_DRAFTED, counts only. This is a check of the demo server's data-licence guard (D-003). It is not a
deployment, and nothing was exposed beyond 127.0.0.1. Code at `kush/s179-finish-fixes` 897ede1, run on 2026-11-10.

## 1. Unit tests

The 7 public-mode / server / demo modules (`test_s170_router_demo`, `test_s171_demo_context`, `test_s173_app_server`,
`test_s176_demo_honesty`, `test_s177_router_public_mode`, `test_s178_fixgov_forwarded_public`,
`test_s178_fixphys_public_durations`): 99 passed.

## 2. Live servers on loopback

`python -m culinarystate.app.server --local --port 8798` and `--public --port 8799`. Both were stopped after the check.

`/api/health`:
- local: `bbc_derived_edges INCLUDED_LOCAL_ONLY`, `carbon_figures INCLUDED_LOCAL_ONLY`, 0 edges dropped;
- public: `bbc_derived_edges EXCLUDED`, `carbon_figures EXCLUDED`. Edges dropped by predicate include
  ING_ALTERNATIVE_TO 216, ING_CARBON_FOOTPRINT 134, PROC_TYPICAL_DURATION 39, PROC_TYPICAL_TEMPERATURE 10 and
  PROC_FOLLOWED_BY 59, among 18 predicates in all.

Tunnel-like requests to the **local** server (GET `/`, GET `/api/health`, POST `/api/ask`). The same request to the
public server returned 200 in every case.

| request signal | `/` | health | ask |
|---|---:|---:|---:|
| `X-Forwarded-For` | 503 | 503 | 503 |
| `Forwarded` | 503 | 503 | 503 |
| `CF-Connecting-IP` | 503 | 503 | 503 |
| `X-Forwarded-Host` | 503 | 503 | 503 |
| non-loopback `Host` | 503 | 503 | 503 |
| no `Host` header | | 503 | |
| plain loopback request | | 200 | |

The body of the 503 is `reason LOCAL_MODE_NOT_PUBLIC` and names the signal (for example `FORWARDING_HEADER:x-forwarded-for`).

## 3. Answers

- **Sample questions.** Six questions were asked in both modes: simmer time, butter substitute, beef carbon, potato bake
  time, the step after browning, and vitamin C in boiled broccoli. Outside the `demo_mode` block, no public answer
  carries a BBC marker (`BBCGF-A1`, `SRC-000002`), a carbon figure or a typical duration. Most of these questions route
  to ASK_CLARIFY, so they exercise little of the graph. That is why the sweep below was run.
- **Substitution sweep.** The question "what can I use instead of X" was asked through `DemoContext.respond`, in public
  mode, for every one of the 155 ingredients that have a local substitution pattern.
  - ACTIVE KGE edges: 45,201, of which 11,928 are BBC-derived.
  - ING_ALTERNATIVE_TO pairs: 220 in local mode, 4 in public mode. The 4 public pairs are a subset of the local ones,
    and 220 - 216 dropped = 4.
  - Public answers: 4 ANSWER_CORPUS_PATTERN, 146 ABSTAIN_NO_EDGES (with the note on why a pattern may be missing),
    3 ABSTAIN, 2 ASK.
  - Candidates outside the public edge set: **0**.

## 4. Not covered

Carbon and typical-duration exclusion inside the scenario layer was checked by the unit tests
(`test_s178_fixphys_public_durations`), not by a live sweep. The local demo edits stashed as
`demo-local-edits-pre-s176` were not applied, so this checks the committed server only.
