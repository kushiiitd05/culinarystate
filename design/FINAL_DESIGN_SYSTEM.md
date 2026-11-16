# CulinaryState Explorer — Design System v1

Next.js · TypeScript · Tailwind 4 · shadcn/ui · React Flow · Recharts/SVG. Presentation 25–26 Nov 2026.

**Every colour below was generated in OKLCH, converted to sRGB, gamut-checked and WCAG-contrast-checked
by script. Zero gamut clips. Zero contrast failures in either mode.** Colour-blindness simulated
(Viénot/Brettel) and measured in OKLab ΔE. **Font claims verified by inspecting the actual font
binaries** with fontTools. Icon names verified against `lucide-static`.
Re-runnable audit: `design/audit/{palette,emit,inspect_fonts,verify}.py`, `design/audit/tokens.json`.

## 0. Verdict on the proposed direction

| Proposal | Verdict | Why |
|---|---|---|
| Warm graphite canvas, warm ivory text | **Confirm** | Right register — but ship **light mode as default** (§0.1) |
| Six semantic hues | **Restructure** | Hues fine; the *architecture* asks colour to carry a six-way distinction that is measurably impossible (§0.2) |
| Fraunces (display) | **Replace** → **Source Serif 4** | No `tnum`/`lnum`, **9 different digit widths**, missing `Δ ₂ →` |
| Instrument Sans (UI) | **Replace** → **IBM Plex Sans** | 343 codepoints, **missing `± ≈ µ Δ ≠ ≥ ≤ ₂ ² †`** — disqualifying |
| DM Mono (IDs) | **Replace** → **JetBrains Mono** | One zero glyph (no disambiguated alternate), no bold, missing `Δ → ₂` |

### 0.1 Default to light mode
Dark washes out on lecture projectors, screenshots badly into a report, prints as grey mud. Ship both
fully tokenised; **light is the default**, dark is a toggle. Dark is for the deployed instrument at a
desk; light is what examiners will actually see.

### 0.2 Why the semantic colour system had to be restructured

Six hues at even lightness, dichromacy simulated. Worst-case pairwise OKLab ΔE (×100):

| Vision | Worst-colliding pair | ΔE |
|---|---|---|
| Normal | scenario / mismatch | 9.0 |
| Protanopia | derived / ai-suggested | 3.6 |
| **Deuteranopia** (~6% of males) | derived / ai-suggested | **1.2** |
| **Tritanopia** | ai-suggested / unknown | **1.2** |

ΔE 1.2 is below the just-noticeable threshold. A search over 1,400 hue assignments found a best
achievable worst case of **ΔE 3.1** — still unusable — and under deuteranopia it still put
**evidence-match / mismatch at ΔE 3.3**. *"This evidence applies"* vs *"this evidence does not apply"* —
the most consequential distinction in the instrument — would be invisible to a colour-blind examiner.

Letting lightness vary raises the worst case to ΔE ~12.3, but lightness is already carrying text
hierarchy, and **staggered lightness down a dense table column looks like a rendering fault**.

**So colour splits into two token sets with two jobs:**
- **`--state-*`** — *even* lightness. Text, table cells, evidence rows, chips. **Colour here is a
  redundant mnemonic only**; the real signal is glyph + marker + border + fill.
- **`--viz-*`** — *staggered* lightness. React Flow nodes, chart series — large marks, nobody reading.
  Measured CVD separation **ΔE 6.5–12.3**.

Not a compromise forced by accessibility — it aligns exactly with the thesis: the instrument claims it
refuses to guess, so epistemic status must be legible in channels that cannot fail.

## 1. Palette

Hue 75 is the warm neutral axis. **Light mode (default):**

```css
:root, .light {
  --cs-canvas: #FCFBF9;  --cs-surface-1: #F7F6F2;  --cs-surface-2: #EFEEE9;  --cs-surface-3: #E7E5E0;
  --cs-border-subtle: #DCD9D3;  --cs-border-default: #C5C2BB;  --cs-border-strong: #817D75;
  --cs-text-muted: #6A645B;  --cs-text-secondary: #504942;  --cs-text-primary: #231E19;
  --cs-focus: #1870A1;

  --state-evidence-match-fg:#226D3D; --state-evidence-match-bg:#E7F5EA; --state-evidence-match-border:#528961;
  --state-derived-fg:#11628F;        --state-derived-bg:#E5F3FD;        --state-derived-border:#4881A8;
  --state-scenario-fg:#7C5213;       --state-scenario-bg:#F9EFE2;       --state-scenario-border:#9A723E;
  --state-ai-suggested-fg:#70419C;   --state-ai-suggested-bg:#F3EDFC;   --state-ai-suggested-border:#866DA3;
  --state-mismatch-fg:#A12B2C;       --state-mismatch-bg:#FEECEA;       --state-mismatch-border:#A76661;
  --state-unknown-fg:#5E5C59;        --state-unknown-bg:#ECEAE5;        --state-unknown-border:#7F7972;
  --state-error-fg:#A52237;          --state-error-bg:#FEEBEB;          --state-error-border:#A76567;

  --viz-evidence-match:#178357; --viz-derived:#025894; --viz-scenario:#BC781A;
  --viz-ai-suggested:#7B6A9A;   --viz-mismatch:#BA343C; --viz-unknown:#8E8C89;
}
```

**Dark mode:**

```css
.dark {
  --cs-canvas:#110F0D;  --cs-surface-1:#1A1714;  --cs-surface-2:#23211D;  --cs-surface-3:#2D2A26;
  --cs-border-subtle:#37342F; --cs-border-default:#4A4641; --cs-border-strong:#75716B;
  --cs-text-muted:#99958D; --cs-text-secondary:#BEB8AF; --cs-text-primary:#E4DFD6;
  --cs-focus:#A0CDD8;

  --state-evidence-match-fg:#89CD9B; --state-evidence-match-bg:#17251B; --state-evidence-match-border:#5D8467;
  --state-derived-fg:#8AC2EA;        --state-derived-bg:#14232D;        --state-derived-border:#567E9A;
  --state-scenario-fg:#E6AF68;       --state-scenario-bg:#2A1F12;       --state-scenario-border:#90734F;
  --state-ai-suggested-fg:#C8ADE8;   --state-ai-suggested-bg:#241E2C;   --state-ai-suggested-border:#817097;
  --state-mismatch-fg:#F99E97;       --state-mismatch-bg:#2D1C1A;       --state-mismatch-border:#9A6B66;
  --state-unknown-fg:#BCBAB7;        --state-unknown-bg:#1F1C19;        --state-unknown-border:#7D7871;
  --state-error-fg:#FC9C9F;          --state-error-bg:#2D1C1C;          --state-error-border:#9A6A6B;

  --viz-evidence-match:#95E6BB; --viz-derived:#50A4EF; --viz-scenario:#F9AB4C;
  --viz-ai-suggested:#B0A3C9;   --viz-mismatch:#DB6B6A; --viz-unknown:#767471;
}
```

**Measured contrast.** Light text: primary 15.97 / secondary 8.56 / muted 5.66 vs canvas; lowest in the
entire light text set is **5.02**. Dark: primary 14.41, muted 4.79 on surface-3. Semantic `-fg` on own
tint: light 5.61–6.35, dark 8.02–8.56. **No pair fails 4.5:1.** Non-text borders 3.53–4.52 (1.4.11 needs 3).

Three values to protect: `text-muted` on `surface-3` is 4.65 light / 4.79 dark — **do not add a
`surface-4`**. Light `--viz-scenario` (3.48) and `--viz-unknown` (3.24) pass 3:1 but need a **2px
minimum stroke, never 1px**.

`--cs-text-primary` is deliberately `#E4DFD6` and **not** brighter — above ~15:1 on near-black,
halation smears 13px table text for astigmatic readers.

`--state-unknown-bg` in dark (`#1F1C19`) is **darker than surface-1**. Intentional — see §3.

### Hue is reserved for epistemic meaning

**Chrome is achromatic.** Primary action, nav, query bar, selection all use the neutral ramp.

```css
--cs-action-solid: var(--cs-text-primary);
--cs-action-on-solid: var(--cs-canvas);
```

A reviewer should be able to say *"every coloured thing on this screen is a claim about knowledge."*

### shadcn / Tailwind v4 mapping

Two deliberate deviations from stock: `--color-input` maps to `--cs-border-strong`, **not** `border`,
because shadcn's default input border measures **1.64:1** and fails 1.4.11. `--color-primary` is
achromatic. Chart 1–5 map to `--viz-*` in order.

## 2. Type

| | Source Serif 4 | IBM Plex Sans | JetBrains Mono |
|---|---|---|---|
| Role | display, headings, small caps | all UI, all table text, all **values** | identifiers, hashes, **predicates** |
| Codepoints | 918 | 891 | **976** |
| Tabular by default | yes | yes | yes |
| x-height | 0.475 em | 0.516 em | **0.550 em** |
| Has `± ≈ µ Δ ≠ ≥ ≤ ₂ ² †` | **all** | **all** | **all** |

**The decisive measurement:** Instrument Sans ships **343 codepoints** and is missing
`± ≈ µ Δ ≠ ≥ ≤ ₂ ² †`. This instrument renders `72 ± 3 °C`, `≈ 18 mg/100 g`, `µg`, `pH ≤ 4.6`,
`C₆H₈O₆`. Every one would fall back mid-word to a different font — in a scientific table that looks
like a bug, and in a screenshot it looks like a bug you didn't notice.

Fraunces has **nine digit widths and no `tnum`/`lnum` at all**, so numbers in a heading jitter and
cannot be fixed; its variable build also defaults to weight 900. DM Mono has **one zero glyph** with no
disambiguated alternate — disqualifying for an interface whose job is letting someone read a long
opaque identifier correctly.

JetBrains Mono's 0.550 x-height lets 12px IDs sit beside 13px Plex with optically matched lowercase
(6.60px vs 6.71px), so the ID column doesn't look smaller than the data column.

### Scale

| Role | Family | Size / LH | Weight | Notes |
|---|---|---|---|---|
| display | Source Serif 4 | `clamp(34px,4.2vw,48px)` / 1.06 | 400 | `opsz:48`. One per page |
| display-2 | Source Serif 4 | 30 / 1.15 | 400 | panel titles, step headings |
| section heading | Source Serif 4 | 19 / 1.30 | 500 | |
| **structural label** | Source Serif 4 | 13 / 1.2 | 500 | `"smcp" 1` — **real small caps. Never `text-transform: uppercase`** |
| prose body | IBM Plex Sans | 16 / 1.60 | 400 | max measure **68ch** |
| ui body | IBM Plex Sans | 15 / 1.50 | 400 | |
| **table cell** | IBM Plex Sans | 13 / **1.35** | 400 | `tabular-nums` |
| table header | IBM Plex Sans | 12 / 1.3 | 600 | sentence case |
| table cell dense | IBM Plex Sans | 12 / 1.30 | 450 | inspector sidebar only |
| **mono ID** | JetBrains Mono | 12 / 1.35 | 450 | `"zero" 1, "calt" 0` |
| caption | IBM Plex Sans | 12 / 1.40 | 450 | muted |
| micro | IBM Plex Sans | 11 / 1.35 | 500 | floor — axis ticks only |

**Values vs identifiers:** numbers and units are **Plex Sans with `tabular-nums`**; identifiers, hashes
and predicates are **JetBrains Mono**. Setting measured values in mono makes a results table read as a
log dump and flattens the distinction between a scientific quantity and a database key — exactly the
distinction this instrument exists to make.

### ⚠️ One critical gotcha

JetBrains Mono ships code ligatures via `calt`. Left on, a predicate containing `>=` renders as a
**single composed glyph the font invented**. In a research instrument displaying applicability
conditions that is a **correctness bug**, not a cosmetic one.

```css
.font-mono { font-feature-settings: "calt" 0, "zero" 1; font-variant-ligatures: none; }
```

Plex Latin has **no Devanagari** — if Indic ingredient names appear, add the sibling family rather than
letting it fall back: `--font-sans: "IBM Plex Sans","IBM Plex Sans Devanagari",system-ui,sans-serif;`

## 3. The semantic state system

Every state is distinguishable through **four independent non-colour channels**, so it survives
dichromacy, greyscale print, a desaturated projector, and a screenshot pasted into Word.

**Shape grammar:** circle → the system reached a verdict · dashed square → a hole in the *input* ·
branch → a counterfactual · asterisk → qualified/unverified · octagon → hard stop, software failed.

**Verified markers.** `✓ ✗ ⊘ ∅` are **absent from all three families** — do not use them, they tofu.

| State | Glyph | Shape | Marker | Border | Left bar | Fill |
|---|---|---|---|---|---|---|
| **MATCH** "Evidence applies" | `circle-check` | circle | `=` | solid | 3px solid | tint |
| **MISMATCH** "Does not apply" | `circle-slash` | circle | `×` | solid | 3px solid | tint + **strike** |
| **UNKNOWN_IN_SOURCE** "Not stated in recipe" | `square-dashed` | dashed sq | `—` | **dashed** | 3px **dashed** | **recessed well** |
| **UNKNOWN_IN_QUERY** "No evidence available" | `circle-question-mark` | circle | `?` | solid | 3px **double** | **well + 45° hatch** |
| **SCENARIO** "Scenario value" | `git-branch` | branch | `Δ` | **dashed** | 3px solid | tint + **global ribbon** |
| **AI_SUGGESTED** "Suggested, unverified" | `asterisk` | asterisk | `*` | solid | 3px **dotted** | **none** |
| **ERROR** "Validator rejected" | `octagon-x` | octagon | `!` | solid | **4px** solid | tint |

**No two rows share a glyph, a marker, a bar treatment, or a fill treatment.**

Markers follow scientific-publishing convention, not invention: `—` is standard "not reported", `*` is
a footnote qualifier, `Δ` is a change. They survive CSV export, so the exported evidence table carries
the same encoding as the screen.

### The three states that carry the thesis

**UNKNOWN_IN_SOURCE** — the recessed well is the one deliberate inversion: both UNKNOWN fills sit
*darker than the surface they're on*, so **absence reads as a hole, not a highlight**. Every other
state sits forward; unknowns sit back. Pre-attentive, non-colour, survives greyscale. Remedy is user
input — needs a **"Supply this value"** affordance.

**UNKNOWN_IN_QUERY — the most important state in the product.** A *circle*, because this **is** a
verdict: the system considered the question and determined it cannot answer. The 45° hatch is the
cartographic convention for unsurveyed territory. Requires a **"What would resolve this"** list —
and it **must be a panel, not a tooltip.** It is the single screen that demonstrates the contribution;
if an examiner has to hover to find it, the design has buried the thesis.
**`circle-question-mark` is reserved** — never a help/tooltip affordance anywhere. Help uses `info`.

**AI_SUGGESTED — deliberately the quietest state, and the only one with no fill.** Lowest epistemic
authority, least visual weight. A tinted "AI card" would promote an unverified guess to the same rank
as a measurement, inverting the product's argument. Requires explicit **Accept / Reject**; nothing
enters the ledger without it.

**MISMATCH is not an error.** It is the system working correctly — evidence found, evaluated,
correctly excluded. `circle-slash` + strike-through means "ruled out". Never fill a row red. Must
state the failed condition inline: *"applies at pH ≤ 4.6; this lot is pH 5.8"*.

**SCENARIO gets a global ribbon** plus `Δ` in the document title whenever active, because **it must be
impossible to screenshot a scenario value and mistake it for a measurement.**

### Two build gates

**Persistent legend** — all seven glyph + marker + label triples, on screen, not in a tooltip. Same
legend in the printed handout.

**CVD/greyscale URL flag** — `?vision=deut|prot|trit|mono` applying an SVG filter over the whole app.
It is the regression test (screenshot, desaturate, confirm all seven states still identifiable), and
during the presentation an examiner can toggle it live. Grafana's own accessibility statement still
lists colour-blind palettes and chart patterns as *planned*; shipping them is a differentiator.

### React Flow · charts

Node **border 2px** (light `viz-scenario`/`viz-unknown` are marginal at 1px); node **fill is always
`--cs-surface-2`**, never the viz colour, so labels keep measured contrast; node carries its state
glyph. Edges 1.5px, UNKNOWN edges `stroke-dasharray: 4 3`.

Series colours applied **strictly in the order given**. **Unknown regions are never a gap** — blank
reads as zero; hatch at 12% `--viz-unknown` and annotate. But apply uncertainty treatment **only to
marks that carry it** — universal indicators lose their meaning. **Every chart gets a "Show data
table" toggle.**

## 4. Spacing, radii, elevation, glass

```css
--space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px; --space-6:24px; --space-8:32px;
--row-h-dense:34px; --row-h-default:40px; --cell-pad:8px 12px; --panel-pad:20px; --touch-min:44px;

--radius-flat:0;      /* table cells, plot area, state bars */
--radius-chip:2px; --radius-control:4px; --radius-panel:8px; --radius-glass:14px;

--border-control: 1px solid var(--cs-border-strong);   /* inputs — 3.53-3.96:1 */
--bar-w:3px; --bar-w-error:4px;
--focus-ring: 2px solid var(--cs-focus); --focus-offset: 2px;
```

**Radii carry information.** Scientific data is flat (0); floating chrome is round (14px). A table cell
and a nav bar sharing a radius is what makes a page look like a template. **Never round a table.**

**Elevation differs by mode** — shadows don't read on near-black. Light: tinted shadow from
`text-primary`, never neutral grey. Dark: surface step + 1px top highlight, no drop shadows. Three
levels max. **Tables, state rows and evidence rows get elevation 0, always** — a raised card per
evidence row is the bento-grid failure mode.

**Glass — measured.** Compositing the tint over pure black and white to find the worst case a label can
land on:

| alpha | dark primary/secondary | light primary/secondary |
|---|---|---|
| 0.70 | 4.95 / **3.33 FAIL** | 7.28 / **3.90 FAIL** |
| **0.86** | **8.90 / 6.00** | **11.11 / 5.95** |

**Alpha 0.86 is the spec; 0.80 the hard floor.** 0.70 — what most glass implementations use — fails.
Glass on exactly four things: top nav, floating query bar, hover overlays, hero/demo selector.
Fallbacks for `@supports not (backdrop-filter)` and `prefers-reduced-transparency`.

## 5. References — what to borrow, what to avoid

**Grafana / Saga** — borrow the discipline about absence: `NO_DATA_COLOR` has been deliberately
achromatic since v7, which is the precedent for `--state-unknown-*` being the only achromatic token.
Borrow the three-tier token architecture. **Avoid** its 14-hue categorical palettes and its habit of
colouring whole rows by threshold — colour-only encoding this project cannot use. Read its
accessibility statement as a to-do list: colour-blind palettes, chart patterns and data-table toggles
are all listed **planned, not shipped**.

**Observable Framework** — borrow the notebook restraint: plot as a thin-bordered box with a caption
and no chrome, muted hairline grids, no chartjunk. Its `theme-air` sets tables at 13px/1.2; we went to
13px/**1.35** because our rows carry bars and glyphs. **Avoid** its blue-dominant default scheme and
its very wide prose measure.

**Vercel Geist** — borrow the step-role contract: 100–300 backgrounds, 400–600 borders, 700–800 fills,
900–1000 accessible text. That is why §1 separates border-subtle/default/strong by **role**. Heed its
own warning that **alpha borders become visible where they overlap** — in a dense evidence table those
intersections are everywhere, so **all borders here are solid, not alpha**. **Avoid** its near-total
monochrome; this instrument needs semantic colour.

**IBM Carbon** — borrow the sequence discipline. The notable gap: Carbon's data-viz colour docs cover
categorical, sequential, diverging and alert semantics with **no treatment of absent data and no
pattern/texture guidance at all.** That absence is the clearest evidence that §3 is the genuinely
novel part of this design — worth one sentence in the presentation.

## 6. Do not do this

1. **Do not drop a glyph because the colour already says it.** The `--state-*` set separates at
   ΔE 1.1–2.4 under dichromacy — colour says nothing to 1 in 12 male readers.
2. **Do not use `✓ ✗ ⊘ ∅`.** Verified absent from all three families.
3. **Do not leave JetBrains Mono's `calt` on.** `pH >= 4.6` would render as an invented ligature — a
   correctness bug.
4. **Do not use `circle-question-mark` for help.** It belongs to UNKNOWN_IN_QUERY. Help uses `info`.
5. **Do not give AI suggestions a tint, a card, or a sparkle.** Lowest authority = quietest on screen.
6. **Do not style MISMATCH as an error.** It is a correct, informative finding.
7. **Do not let a scenario be ambient.** Global ribbon + `Δ` in the title.
8. **Do not round a table.** Radius encodes float; data doesn't float.
9. **Do not raise evidence rows.** Elevation 0 on tables and state rows.
10. **Do not put glass below 0.86 alpha**, and never over a table, state value, evidence row or claim warning.
11. **Do not use `border-subtle`/`border-default` as the only boundary of an interactive control** (1.30:1, 1.64:1).
12. **Do not brighten `--cs-text-primary` past `#E4DFD6`** — halation smears 13px table text.
13. **Do not render an UNKNOWN as an empty cell.** Empty is ambiguous between "not stated",
    "unanswerable" and "we forgot". Always the marker plus an `aria-label`.
14. **Do not show a gap for a missing chart region.** Blank reads as zero. Hatch and annotate.
15. **Do not set structural labels in tracked-out ALL-CAPS.** Source Serif 4 has real small caps.
16. **Do not set measured values in mono.** Mono is for identifiers and predicates.
17. **Do not add a hue to the chrome.**
18. **Do not add a seventh semantic hue.** Six already exceeds what colour can carry. New distinctions
    get a new glyph, marker or treatment — never a new colour.

## 7. The weakest link

Not measured — behavioural. **The whole design depends on developers keeping all four non-colour
channels on every state, every time.** The CVD/greyscale URL flag is what makes that enforceable:
build it early and screenshot through it in CI, or the glyphs will quietly erode into colour-only chips
by the 24th.

**Note:** the `magic-ui` (21st.dev) MCP server failed to authenticate this session and `huggingface`
timed out, so 21st.dev component patterns were not consulted. Worth re-keying before component
build-out.
