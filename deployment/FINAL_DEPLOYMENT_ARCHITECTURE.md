# CulinaryState — demo gateway and deployment architecture

> **`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · architecture decision record.**
> Footprint, cold-start and memory figures are **measured on this machine** and supersede the
> “~25 MB” estimate given earlier in the same session. Vercel limits were checked at time of
> writing — **re-verify before relying on them**. Resolution rule: **ksh governs** (D-139).
> Closes no deliverable.

**For the 25–26 Nov 2026 presentation. Written 16 Nov 2026. The scientific core is frozen; nothing
here modifies it.**

## 0. Measured first — the premise was wrong

An earlier estimate in this session put the request-path footprint at "~25 MB". **That was `du` on
`src/` and `registry/` and never traced what the runtime actually loads.** Measured:

| Quantity | Earlier claim | **Measured** |
|---|---|---|
| `src/` excl. `__pycache__` | ~10 MB | **3.6 MB** |
| Registry read at startup | ~13 MB | **~3 MB** |
| **Ledger JSONL read at startup** | *not mentioned* | **~153 MB** |
| Cold load `DemoContext.load()` | *not mentioned* | **9.72 s** |
| Peak RSS after load | *not mentioned* | **1.21 GB** |
| Per-query latency | *not mentioned* | **20–30 ms** |

`DemoContext.load()` calls `LedgerStore.all_latest()` on EVD (85 MB), KGE (58 MB), ING, COND, ALIAS,
PROC, ALLERGEN. `REC.jsonl` (90 MB), `IMAP` and `_ids` are **not** on the request path. The 3.2 GB
`data/` tree genuinely is build-time only — that part of the earlier story held.

**The shape that matters: 9.7 s to load, 1.21 GB resident, 0.03 s to answer.** Load-once/serve-forever
— the anti-shape for scale-to-zero serverless, the right shape for one long-lived process.

## 1. Decision

> **Build (d): snapshot-primary, live-optional.**
> - **Vercel** hosts the Next.js UI, BFF routes, and a **committed, Ed25519-signed precomputed
>   snapshot**. The snapshot is the **default serving mode**, not a fallback. No Python on Vercel.
> - **The live deterministic backend runs on the presenter's Mac** as the existing audited
>   `app/strict_server_v3.py`, behind a Cloudflare Tunnel. **Not the GPU server.**
> - **Ollama is removed from the request path entirely.**

### Current Vercel limits (checked, not assumed)

| Limit | Value |
|---|---|
| Python runtime | 3.12 / 3.13 / 3.14 on Fluid Compute |
| **Python bundle, uncompressed** | **500 MB** (not 250 MB — Python has a raised limit); 5 GB via large-functions beta |
| Duration default | **300 s on every plan**, Hobby included |
| Memory | Standard 2 GB / 1 vCPU; 4 GB Performance is Pro/Enterprise only |
| Request/response body | 4.5 MB |

So the earlier rejection of a Vercel-hosted core **on bundle size was wrong on the facts** — ~280 MB
fits inside 500 MB. It is rejected for four other reasons.

### Why not run the core on Vercel

1. **Licensing — the hard blocker.** `EVD.jsonl` and `KGE.jsonl` contain BBC Good Food–derived rows.
   `decision/public_mode.py` filters them **at load time, on rows already read from disk** — not at
   file level. Uploading them to a third-party build system and CDN violates D-003 /
   `LOCAL_RESEARCH_ONLY`. Making it legal needs a build-time pack builder plus an equivalence proof
   against the runtime filter — new code against a frozen core, nine days out.
2. **Memory.** 1.21 GB against a 2 GB Standard instance is 60% baseline occupancy; Fluid shares one
   instance across concurrent invocations. A few simultaneous clicks reach `FUNCTION_INVOCATION_FAILED`
   — an opaque 500, mid-presentation.
3. **Cold start.** 9.7 s on an M2 Pro with a warm cache; 20–40 s on one shared vCPU cold. It will not
   error (300 s limit) — it will hang while the room watches. Scale-to-zero means the first click of
   the talk pays it, and so does any click after a few minutes of Q&A.
4. **The whole answer space is precomputable** at 30 ms/query, so "offline" is an exact replay, not
   degradation.

### Why not the GPU server

The deterministic path needs no GPU, yet hosting there couples the always-needed path to FortiClient
VPN, a shared A100, and a disk at 93%. A Cloudflare Tunnel does fix inbound ports and removes the VPN
requirement — genuinely useful — but cannot survive the university network going down, which is a
stated hard requirement.

**The Mac is the right live host:** the only machine that may legally hold the BBC-derived ledgers,
physically in the room, 1.21 GB fits in 8 GB, loads once and stays warm (30 ms queries), and
`cloudflared` needs no VPN.

**Cutting Ollama deletes three risks at once:** the 800 s tail, the VPN dependency and the GPU
dependency. The promoted C16/B5T template verbaliser is already LLM-free.

## 2. Gateway API

**Two corrections to the proposed design.**

**Do not chain six endpoints across the tunnel.** Six round trips per user action multiplies failure
probability by six and makes partial failure a state the UI must model. The six seams should exist
for debugging and the pipeline-stages view, but **the BFF calls one composite endpoint per action**
and the gateway runs the chain in-process.

**Do not write a FastAPI gateway.** `src/culinarystate/app/server.py` already exists, is
standard-library only, and already implements body caps, JSON-only parsing, per-IP rate limiting,
strict CSP, `no-store`, stack-trace suppression and the GOV-4 public-mode guard. Replacing it
discards the one security-reviewed component. Extend it.

Internal (never browser-reachable), `POST /v1/internal/`: `/propose` · `/state` · `/retrieve` ·
`/compile` · `/verbalize` · `/verify`.

Public: `GET /api/health` · `GET /api/scenarios` (static, CDN, **cannot fail** — the opening screen
is built on it) · `POST /api/trace` · `POST /api/ask` (already implemented).

Every response carries a `serving` envelope: `mode`, `snapshot_id`, `generated_at`, `signature`,
`demo_mode`, `degraded_reason`, `latency_ms`.

## 3. Auth

**Layer 1 — Cloudflare Access service token.** Rejects unauthenticated traffic **at Cloudflare's
edge**, so the laptop is never exposed to scanners and revocation is instant.
**Layer 2 — app key** `X-CS-Gateway-Key`, compared with `hmac.compare_digest`, never `==`.

Secrets in Vercel environment variables only. **Never a `NEXT_PUBLIC_` prefix** — the repo is public
and that prefix ships the value into the browser bundle. Gateway accepts a **set** of keys so
rotation never needs both sides deployed simultaneously.

### ⚠️ The single most likely cause of a dead demo

`public_mode.resolve()` returns local mode for a process bound to `127.0.0.1`. But `cloudflared` adds
forwarding headers, so `forwarded_request_signal` classifies every tunnelled request as public, and
`refusal_for_request` then returns **503 on every path — page, health and ask** — when the context is
not in public mode.

**The gateway must be started with `--public` (or `CS_DEMO_PUBLIC=1`), or the entire demo returns 503
through the tunnel.** Invisible on localhost. Preflight assertion #1.

The guard is a genuine strength — it fails *closed*, so BBC-derived data cannot leak through a tunnel
by accident. Force public mode; do not weaken it.

**Also:** the rate limiter keys on `client_address[0]`, which through `cloudflared` is always
`127.0.0.1`, so the 30/min limit is **global, not per-user**. Start with `--per-minute 120` and have
the BFF treat 429 as a live failure that falls through to snapshot.

## 4. Snapshot — the primary path

`tools/build_demo_snapshot.py`, run **on the Mac**:
1. `DemoContext.load(public=True)` — one 9.7 s load.
2. **Assert and refuse to write otherwise:** `public is True`, `bbc_derived_edges == "EXCLUDED"`,
   `carbon_figures == "EXCLUDED"`.
3. 4 self-written recipes × trace; ~50–60 curated questions spanning **every** decision mode:
   `ANSWER`, `COMPARE`, `ABSTAIN`, `TARGET_ABSENT`, `ANSWER_CORPUS_PATTERN`, `ABSTAIN_NO_EDGES`, the
   safety refusal, `ASK`.
4. **Licence gate — fail the build on any hit:** scan output for `BBCGF-A1`, `SRC-000002`, and any
   recipe sha256 not in the self-written set. *The most valuable twenty lines in the design.*
5. Write per-scenario JSON + `manifest.json`.

~2 s of compute total, so wire regeneration into the 21 Nov freeze and a stale snapshot becomes
structurally impossible.

Lookup key: `sha256(nfkc(lower(collapse_ws(q))) + "|" + (recipe_sha256 or ""))` so typed questions
still hit.

**Stored committed at `web/public/snapshot/`** — atomic with the deploy, versioned in git, rollback is
`git revert`, **zero runtime dependency** on Blob/S3/any database. A fallback whose availability
depends on another service is not a fallback.

**Ed25519 detached signature.** Private key stays in `~/.culinarystate_private`. Verified at build
time (CI fails the deploy), in the BFF on cold start, and exposed as `manifest_sha256` in
`/api/health`. For a presentation about evidence-bounded answers, "this is provably what the frozen
system answered" is worth thirty lines.

**Mode badge, persistent and non-dismissable:** LIVE green "Answering live · 41 ms" / SNAPSHOT amber
"Recorded 21 Nov 2026 · signature verified". **Never silently fake live** — a system whose thesis is
honest provenance labelling cannot be dishonest about its own.

Circuit breaker: two consecutive live failures pin SNAPSHOT for 60 s. Oscillation is worse than
either mode.

**Recommendation: present with `CS_LIVE_ENABLED=0`** and flip live on as a deliberate "and here it is
actually running" moment.

Offline miss returns `ABSTAIN / OFFLINE_NOT_IN_SNAPSHOT`: *"The live backend is offline and this exact
question isn't in the recorded set. Nothing was guessed."* That last clause is the project's own law.

## 5. Timeouts

With Ollama gone, live is 30 ms compute + tunnel RTT; realistic p99 ~300 ms.

| Hop | Timeout | Retries | On failure |
|---|---|---|---|
| Browser → BFF | 6 s hard abort | 0 | show snapshot |
| BFF → `/health` probe | 1.5 s | 0, cached 10 s | mark live ineligible |
| BFF → `/api/ask`, `/v1/trace` | **3 s** | **0** | fall straight to snapshot |

**No retry on timeout, deliberately.** A retry doubles dead air to 6 s and only helps if the failure
was transient — but the gateway either has its context loaded (30 ms) or is gone. Only retry on a
*connection-reset*, which costs ~0 ms. **The UI is promised an answer within 3 s, always. The gateway
is promised nothing and may be absent.** That asymmetry is the design.

## 6. Observability — minimum worth having

1. **`tools/preflight.sh` — the highest-value artefact here.** Asserts: tunnel `/health` 200 ·
   **`health.mode.public == true`** · snapshot signature verifies and matches the frozen tag · all
   four scenarios 200 in **both** modes · a known-answer question returns `ANSWER` and a known-abstain
   returns `ABSTAIN`. Run at the 24 Nov rehearsal and 30 minutes before the talk.
2. `/api/health` as the single pane of glass.
3. One structured JSON log line per request. **Log `sha256(question)` and length, never the text** —
   a pasted question may contain third-party recipe text, which would recreate the licensing problem
   in a log file.
4. Vercel runtime logs — free, already there.

**Do not build:** OpenTelemetry, Prometheus, Grafana, alerting, SLOs, APM, distributed tracing. All
correct for production, all wrong for a nine-day-old single-presentation demo.

## 7. Top risks

| # | What breaks | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **Gateway without `--public` → 503 everywhere through tunnel** | **High — it is the default** | Total | `CS_DEMO_PUBLIC=1`; preflight assertion #1 |
| 2 | University network down | Medium | **None under (d)** | Snapshot-primary, CDN-served |
| 3 | GPU server / VPN down | High | **None** | Ollama removed from request path |
| 4 | Snapshot stale vs frozen core | Medium | Credibility | Regenerate in the freeze step; assert manifest sha against the tag |
| 5 | Mac sleeps mid-talk | Medium | Live dies, snapshot fine | `caffeinate -dimsu` |
| 7 | Rate limiter global via tunnel → 429 | Medium | Live stalls | `--per-minute 120`; 429 → snapshot |
| 11 | BBC-derived data reaches Vercel | **Certain if core deployed there** | **Severe — licensing** | (d) ships no ledgers; build-time scan |
| 12 | Vercel incident | Low | Total | Unhedgeable. Keep a local `next start` and the deck |

## 8. Build order

| Day | Work |
|---|---|
| **17 Nov** | `build_demo_snapshot.py` + licence scan + signing. **This alone makes a working presentation possible.** |
| **18 Nov** | Next.js UI + BFF, four routes, snapshot-only. **Deployable demo with no backend at all by end of day.** |
| **19 Nov** | `/api/trace` on the stdlib gateway; tunnel + Access token; `--public`, `--per-minute 120`. |
| **20 Nov** | Live/snapshot switching, badge, circuit breaker, timeouts, `preflight.sh`, Playwright e2e in both modes. |
| **21 Nov** | Freeze. Regenerate, re-sign, deploy, full preflight. |
| 22–24 Nov | Fixes only. Rehearsal with the tunnel deliberately killed mid-demo. |

**A complete, honest, presentable demo exists by end of 18 Nov with no backend whatsoever.**
Everything after is upside.

## One-sentence version

Per-query cost is 30 ms over a fixed scenario set, so the whole demo is precomputable; precompute it,
sign it, serve it from Vercel's CDN as the default, keep the frozen core live on the presenter's Mac
behind a Cloudflare Tunnel as an opt-in flourish, and delete Ollama from the request path — which
removes the GPU server, the VPN and the 800 s tail from the critical path at once.
