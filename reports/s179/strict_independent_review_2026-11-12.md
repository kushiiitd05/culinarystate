# Strict runtime independent AI engineering review — 12 November 2026

**AI_PRECHECKED / ENGINEERING_DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
Reviewer: author-only review (AI-delegated), separate agent context. This is an independent pass over the engineering implementation, not independent human review, inter-rater evidence or scientific validation. Original scientific gates and frozen D5 results are unchanged.

## Scope and findings

Read-only review covered the frozen strict-v2 renderer, adapter, physical provenance serializer, original server/static page, scenario producer and prior regression controls. The v2 engineering snapshot remains byte-identical. Defects below are fixed in a separate strict-v3 path, ready for a new dated engineering snapshot/adoption by the orchestrator.

| Finding | Reproduction / consequence | Separate v3 correction |
|---|---|---|
| Fixed-decimal point rendering can invent displayed zero | Synthetic measured retention factor0.004 survives authorization but v2 formats it as0.00. The source metadata remains positive. | `generation/strict_v3.py` retains v2 authorization, constructs the final text from finite source values using their Python representation, records `display_value` and checks that exact canonical text after any renderer/fallback. It never authorizes a new source row. |
| Strict-v2 launcher serves legacy source-row chips | Legacy page calls DIRECT “Measured data” and says data are measured for this food/process. The recipe route is a row-existence screen, not the strict condition checker. | New view marks “Unverified source row only” and `applicability_certified=false`; other routes do not become scientific applicability determinations. Original route IDs remain metadata for reproduction. |
| Physical provenance exists in JSON but legacy browser ignores it | Legacy page does not render per-number basis/status/unit/references. A user sees an estimate without the new metadata. | Separate view model enumerates each non-null quantity endpoint and requires known basis/status/unit and finite numeric value before display. Every displayed quantity carries basis/status/unit and available source/default references. Raw fields remain separately available; no source text is normalized in place. |
| Legacy null conversion creates visible numbers | Legacy `Math.round(null)` yields0; only the lower range endpoint is checked. A missing upper or typical value can therefore become a visible zero. | New view has no graph/axis constants or numeric coercion of null endpoints. Each endpoint needs its own metadata and finite value. Missing/unknown numbers are omitted with an unavailable notice. |
| Heat-only events can disappear | Legacy UI renders physical output only while iterating recipe-route steps; if a unique target/recipe route is absent, existing heat steps are hidden. | View includes heat events absent from the route list, labels them physical-scenario-only, and does not apply an evidence effect. |
| Strongest-only route selection hides weaker ingredient rows | Legacy display keeps the strongest route per event, potentially omitting unknown rows for other ingredients. | New view retains each route item; there is no strongest-only promotion. |
| External font request unnecessary for local review | Legacy page requests hosted fonts. | New page uses local system fonts; browser rehearsal detected no external page requests. |

No v2 or original generation/scorer/prompt/benchmark/ledger/grammar file was edited. New policy deliberately continues to refuse default numeric retention answers when exact declared source context is absent. It is not an improvement claim for scientific answer quality or coverage.

## Adversarial checks and integration

`tests/unit/test_s179_strict_final_review.py` contains10 controls: frozen-v2 small-point defect reproduction; v3 point display; final fallback refusal; null/unknown omission; independent endpoint metadata; nonfinite/boolean/text rejection; row-only badge and heat-only preservation; offline safe static rendering; linked-identity/precision adapter boundary; and new-server asset/GOV-4 forwarding behavior.

Initial test-first result:7 failures and1 passing baseline reproduction, before implementation. After new v3 implementation,10 reviewer tests pass. Targeted reviewer plus retained v2 adapter/emission/reviewer/physical modules: **68 passed in0.98s**. These are synthetic engineering controls, not biological/chemical measurements or accuracy estimates. Frozen strict-v2 snapshot file hashes were rechecked unchanged.

New files:

- `src/culinarystate/generation/strict_v3.py`
- `src/culinarystate/decision/demo_context_v3.py`
- `src/culinarystate/decision/strict_display_v3.py`
- `src/culinarystate/app/strict_server_v3.py`
- `src/culinarystate/app/static/strict_v3.html`
- `tools/run_local_demo_v3.py`
- `tools/s179_strict_browser_driver.mjs`
- `tools/s179_strict_browser_rehearsal.py`
- `tests/unit/test_s179_strict_final_review.py`

All new source files are below800 lines. The v3 server reuses original request validation, rate limiting, JSON API and per-request GOV-4 guard; the separate page overrides only its own static route.

## Actual browser technical rehearsal and fallback

`reports/s179/strict_v3_browser_rehearsal_2026-11-12.json` records an actual isolated headless Chrome session against the loopback public-filtered v3 server. A fresh temporary browser profile was used; no real user profile or remote page was accessed. Four scripted synthetic cases exercised transformation/physical display, substitution, food safety and unsupported input. All four completed without UI errors, nonfinite visible output, missing quantity basis or “Measured data” source-row mislabelling. The transformation case displayed four quantities, each with its own basis. A planted missing-value browser control displayed zero quantities and no fabricated zero.

The case elapsed times were67.658,28.201,27.232 and28.242ms; these include driver polling and are diagnostic timing only, not performance benchmark estimates. Whole browser/check run timestamps are2026-11-12T14:19:30.672000+00:00–14:19:38.067960+00:00. The first temporary harness attempt encountered an empty DevTools port-file readiness race; the harness was corrected to wait for populated content. No product change was needed for that harness failure.

`reports/s179/strict_v3_fallback_2026-11-12.png` is the browser screenshot of the synthetic transformation case. The reviewer viewed it: the refusal, four basis-labelled quantities, unknown applicability, unavailable-value notice and NON_CITABLE footer are visible without overlap at the recorded desktop viewport. This is a static technical fallback asset, not experimental evidence or a report/deck final edit.

The hash-bound JSON records no external page requests. The persisted browser driver is byte-identical to the driver whose hash appears in that result. For a fresh run, use the project Python environment:

```sh
python tools/run_local_demo_v3.py
python tools/s179_strict_browser_rehearsal.py --out reports/s179/strict_v3_browser_rehearsal_NEW.json --screenshot reports/s179/strict_v3_fallback_NEW.png
```

The browser rehearsal tool starts and closes its own loopback server and isolated Chrome session; it does not need a separately running launcher. Use new output paths; it refuses overwrite. Requires local Chrome and Node with WebSocket support. This12Nov technical rehearsal is explicitly **not** the required24Nov timed presentation event, and no author facts or final edits were supplied.

## Remaining scope boundaries

The old346-answer audit retains30 flagged records. Strict-v3 is a separate runtime and does not repair or re-score frozen answers. Source validity, exact registry membership, scientific condition applicability, unverified scenario defaults, genuine PARAM/VAL eligibility, natural-query coverage, mobile/browser-family accessibility and every possible free-form scientific assertion are not certified by this engineering review. Legacy launchers intentionally retain historical behavior. Use the v3 launcher for the corrected local view after its new engineering snapshot/adoption is recorded. No original scientific acceptance or human/time gate is marked passed.
