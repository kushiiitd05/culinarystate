# PARV — HANDOVER PROMPT, 17 Nov 2026 (CulinaryState)

> **`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · execution handoff.** Paste this whole file into Claude Code
> at the repo root. Resolution rule: **ksh governs** (D-139). This closes no deliverable and no D-085 gate.

**Kush has handed the remaining work to Parv.** This file is the newest instruction. It **adds to**
`handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` (16 Nov), which still holds the thesis, authority
order, language rules, design system and acceptance criteria. Read that one too; where they differ,
this one wins.

**Dates:** technical freeze **19 Nov** · verify **20 Nov** · submit **21 Nov** · rehearsal **24 Nov** ·
present **25–26 Nov**.

---

## 0. First ten minutes

```bash
cd culinarystate && git fetch && git switch kush/s181-explorer-build && git pull
/opt/anaconda3/bin/python -m pytest -q tests/unit/ -k "s181 or s182"     # 76 + 41 tests, must pass
/opt/anaconda3/bin/python -m pytest -q                                    # full suite before quoting a count
```
Then read, in order: this file → `STATUS.md` → tail of `WORKLOG.md` → `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`
→ `reports/s181/human_audit/README.md` → `reports/s181/snapshot_findings.md`.

## 1. What exists now (since the 16 Nov master prompt)

| Piece | Where | State |
|---|---|---|
| Signed precomputed snapshot (9 scenarios, 8 contractual asks, qwen-7B baseline) | `web/public/snapshot/`, builder `tools/s181_build_demo_snapshot.py` | built, Ed25519-signed, `--check` FRESH, 41 tests |
| Explorer UI: landing, `/lab`, `/compare`, `/method` | `web/src/app/**` | built on snapshot data; not yet deployed |
| **Live RAG console `/live`** (new, 17 Nov) | `tools/s182_*.py`, `web/src/app/live`, `web/src/components/live/` | working, 76 tests, browser-checked |
| One-click launcher | `LIVE_DEMO.command` (Finder) / `tools/live_demo.sh` | starts engine + web, opens `/live` |
| Human-audit packets D1/D3/D5 | `reports/s181/human_audit/` | AI-prechecked; **every human column empty** |
| D4 contract metrics | `reports/s181/d4_contract_metrics.md` | computed, honest limits stated |
| Deck builder | `reports/final/deck/build_deck.py` | python-pptx; run it, check it |

### The live console in one paragraph
Same hosted model (`nvidia/nemotron-3-ultra-550b-a55b`, NVIDIA NIM, temperature 0) answers twice: once
**through CulinaryState** and once **plain** (recipe + question only). Three modes, picked from the question:

* **NUTRIENT** (vitamin C / lycopene): State v2 → evidence compiler → **claim packet** → model verbalises the
  packet only → **claim verifier** → deterministic template if the draft fails. Plain answer is checked by the
  same verifier. Showcase: *Tomatoes · vitamin C* → cited USDA 95.0 % [EVD-002765]; plain model invents "40–60 %".
* **ADVICE** (fix / rescue / what went wrong): the model gets the **step-by-step state trace**, physics
  **simulation values**, step-to-step changes, evidence matches, and a **similar public recipe** that the engine
  parsed and simulated live. Every `(step N: field = value)` the model cites is **checked against the trace**
  (e.g. 7/7 match). Labelled *Suggested, unverified* — the advice itself is not checked.
* **SAFETY**: refused before any model call, as the core refuses it.

UI: grouped presets (Fix my dish · Nutrients · Safety, 10 different dishes), a **7-stage live pipeline status**
(read → state → simulation → evidence → similar → model → verify), tabs **Answer · Pipeline · State & simulation ·
Evidence · Similar recipes**, and a *Compare with plain LLM* button.

Similar-recipe search: TF-IDF over all **612,903** recipe titles, local, ~50 ms. Licence policy per family in
`tools/s182_similar.py::policy` — **only Wikibooks (shown + sent) and Gutenberg (title shown) leave the machine;
Food.com, BBC (D-003), TASTEset are counted only, never shown or sent.**

## 2. Set up `/live` on your machine

1. **Your own NVIDIA key** (do not use Kush's): `build.nvidia.com` → key → file
   `~/.config/culinarystate/nvidia.env` containing `NVIDIA_API_KEY=nvapi-…`, then `chmod 600` it. Never commit it.
2. **Data the similar search needs** (git-ignored): `ledgers/recipe_base/recipe_base_v1.parquet` and
   `data/interim/wikibooks/recipes.jsonl`. Copy from Kush's private bundle. Without them the console still works;
   the *Similar recipes* stage shows **skipped**. First run builds `data/derived/s182_similar_index_v1.pkl` (~7 s).
3. Run `./tools/live_demo.sh` from the repo root (or double-click `LIVE_DEMO.command`). Engine on
   `127.0.0.1:8770`, web on `localhost:3000/live`. Ctrl-C stops both.
4. Check every preset once: all ten must reach "Verify". Engine log: `$(getconf DARWIN_USER_TEMP_DIR)culinarystate-live/engine.log`.

## 3. Remaining work — in this order

### A. Human-only (Parv; nothing an agent writes closes these)
| # | Task | Packet | Time |
|---|---|---|---|
| A1 | **D1: hand-verify 40 literature rows** (Kush was to do 20; he is out — do all 40 or report the shortfall honestly) | `reports/s181/human_audit/D1_literature_rows_precheck.csv` + `D1_README.md` | ~2–5 min/row |
| A2 | **D5: one real chef/peer review** of the 8 scenarios | `D5_peer_review_packet.md` | find chef + ~30 min |
| A3 | **Proposal packet**: the 9 rows where ksh and prv differ | per master prompt §4 item 4 | ~20 min |
| A4 | **D3**: spot-audit 10 gold recipes. The P1-A label is **Kush-only** — send him one WhatsApp question; if no answer, use the "not done" wording | `D3_gold_status.md` | ~1 h |
| A5 | Rotate/keep your NVIDIA key; Kush's key was pasted in chat on 17 Nov and is his to rotate | — | 2 min |

Use the exact sentences in `reports/s181/human_audit/REPORT_WORDING.md` for whichever state each gap ends in.

### B. Agent work (Parv's Claude)
| # | Task | Done when |
|---|---|---|
| B1 | **Decision record for the core range bug.** `src/culinarystate/simulation/scenario_layer.py::_triple` crashes on a **tuple** duration range ("cook for 2-5 min") on the in-memory path; batch runs were unaffected (their L1 rows are JSON lists, 0 exceptions over 612,782 recipes). Live is protected by `RangeSafeScenarioLayer` in `tools/s182_live_rag.py`. Either record "keep the adapter, core untouched" or a decision + one-line fix `isinstance(v, (list, tuple))` + test. AI-delegated under D-085/D-139, ksh governs. | `DECISIONS.md` entry; tests green |
| B2 | **Hide `/live` in the public build.** It needs the Mac engine; on Vercel it would only say "offline". Gate the nav link and page on a server-side env flag (no `NEXT_PUBLIC_` secrets). | Vercel build shows Lab/Compare/Method only |
| B3 | **Deploy snapshot-only to Vercel** per `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md`. Never ship the Python core or ledgers (BBC rows, D-003). | public URL, badge "PRECOMPUTED SNAPSHOT · signature verified" |
| B4 | **`tools/preflight.sh`** + Playwright e2e: snapshot pages; `/live` all ten presets locally; engine-down path shows the offline chip | script exits 0 |
| B5 | **Freeze 19 Nov**: rerun `s181_build_demo_snapshot.py --check` (FRESH), re-sign if the engine changed, tag the commit, record manifest hashes | tag + hashes in `STATUS.md` |
| B6 | **Final report → PDF.** Update the latest draft in `reports/final/` with: S181 snapshot, S182 live console (what it is and is not), D1–D5 honest status from the compliance matrix, all negative results. Every number from a frozen artifact. Export PDF (pandoc → HTML → Chrome print works on the Mac). | `reports/final/CulinaryState_final_report.pdf` |
| B7 | **Deck → PPTX + PDF**: run `reports/final/deck/build_deck.py`; add one live-demo slide (screenshot of the pipeline + compare) and one honest-limits slide. Same story and numbers as the report. | `CulinaryState_final.pptx` + PDF |
| B8 | **Submission package 21 Nov** (master prompt §22): frozen tree + manifest hashes, report, deck, demo (snapshot + live), release card, compliance matrix, decisions, worklog. | zip + checklist |
| B9 | **Rehearsal script** (§6 below) and a recorded fallback video of `/live` in case the network fails on the day | video file |
| B10 | Optional, only after B1–B8: `qwen2.5:32b` on vinayak `:11500` as a backup model for `/live` (`NimLLM` is one class; add an Ollama class with the same call signature). Needs VPN. | — |

## 4. What `/live` may and may not claim (report, deck, talk)
* **May:** same model, different context; the system cites evidence or says UNKNOWN with the reason; in advice
  mode every cited state fact is checked and shown ✓/✗; simulation values are labelled *simulated*; food-safety is refused.
* **May not:** "more accurate", "SOTA", "validated", or that the advice is correct. There is **no gold**. The plain
  model is sometimes good (it gave sensible pasta and potato advice in some runs) — say so.
* **Known issues to state:** the verifier is a wording/number check (it can flag a cooking time; it rejects cautious
  replies that don't say "not known"); advice can include unverified chemistry ("salt firms pectin"); similar-recipe
  matches are word overlap (carrots → "Carrot Jam"); pH, salt fraction and fat fraction are **always UNKNOWN**
  (`composition/context_v12.py:71-73`, masses not grounded — 0.6 % groundable, deferred). That is a decision, not a bug.

## 5. Laws (unchanged — break none)
No invented scientific values; UNKNOWN is a valid answer · AI review ≠ human verification (D-071/D-085) ·
**`src/` frozen** — change only with a decision record · ledgers EVD/COND/SRC/MEAS/SNAP byte-identical ·
only public or self-written text to any hosted API · BBC/Food.com raw text never leaves the machine ·
one commit per file, tests first, no AI attribution in commits · push each session · log steps in `WORKLOG.md`.

## 6. Demo script for the talk (≈6 min)
1. `/compare` (snapshot): Tomato A–D — one ingredient changes the route; signature verified.
2. `/live` → **★ Carrots came out mushy** → Ask → let the **Pipeline** tab tick → **Answer** → *Compare with plain LLM*
   → point at the cited simulated thermal dose and the ✓ citations.
3. **Tomatoes · vitamin C**: cited USDA 95.0 % vs the plain model's invented range.
4. **Roast potatoes soggy** → **Similar recipes** tab: 612,903 searched, licence column, the Wikibooks reference the engine simulated.
5. **Chicken · is it safe?**: refused by design.
6. Close on the honest-limits slide.

## 7. Stop conditions — raise to Kush only if truly blocked
Scientific/governance decision a ksh-governed AI verdict cannot make · a credential or login · a required file
missing · anything that would send BBC/Food.com text off the machine. Format: **QUESTION · RECOMMENDED · ALTERNATIVES ·
CONSEQUENCE · DEADLINE IMPACT.**

**The one thing to remember:** the UI, report and deck are agent work; **D1 rows, the chef review and the proposal
packet are human work, and they are what the examiner checks first.**
