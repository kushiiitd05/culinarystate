# CulinaryState Explorer — Frontend Architecture & Component Plan

Hand-to-developer spec. Target demo: 25–26 Nov 2026. The engine is frozen; this document describes a UI that is a **pure consumer** of its JSON.

**Grounding note:** before writing this I read the actual engine shapes rather than inventing a schema. The interfaces below mirror what the Python already emits, so no engine change is implied anywhere.

- `src/culinarystate/composition/state.py:18-23` — `V(v, b) -> {"v": v, "b": b}` and `U(reason) -> {"v": None, "u": reason}`. This is the cell wire format; the whole UNKNOWN design is built on it rather than next to it.
- `src/culinarystate/composition/state_full.py:1-13` — the docstring defines G/C/Q/Y/P exactly; `:158-180` is the literal block assembly, which gave me every real field name.
- `src/culinarystate/retrieval/compatibility.py:11-14` — `AXES`, `WEIGHTS`, `VALUE = {MATCH 1.0, NEAR 0.5, UNKNOWN 0.25, MISMATCH 0.0}`.
- `src/culinarystate/composition/claim_packet.py:83-95` — the claim packet's exact keys.
- `docs/EVENT_IR_CONTRACT.md` — `EventCandidate` / `EntityCandidate` / `AllocationCandidate` / `EventGraph`, `alternative_group`, `condition_profile_id`, and the `OPEN_INVARIANTS` list that `/method` must display verbatim.

---

## 0. Stack, pinned

| Package | Version | Why pinned here |
|---|---|---|
| `next` | 16.4.6 | App Router; `proxy.ts` has replaced `middleware.ts`; `cacheComponents` + `"use cache"` replace implicit caching |
| `react` / `react-dom` | 19.x | shipped with Next 16 |
| `typescript` | 5.9+ | `const` type params, satisfies, exhaustive narrowing |
| `tailwindcss` | 4.x | shadcn CLI v4 requires it; **no `tailwind.config.js`** — theming is CSS-only via `@theme` |
| `shadcn` CLI | v4 (Mar 2026) | `init --base radix` (keep Radix, not Base UI — React Flow + Radix is the better-trodden path); `registry:base`/`registry:font` replace deprecated `registry:build`/`registry:mcp` |
| `@xyflow/react` | 12.12.1 | the lot/state graph. Needs `import '@xyflow/react/dist/style.css'` |
| `elkjs` | 0.12.1 | DAG layout, run in a Web Worker |
| `zustand` | 5.1.0 | session view state |
| `@tanstack/react-query` | 5.x | server-response cache keyed by content hash |
| `zod` | 4.6.7 | the contract decoder at the fetch boundary |
| `motion` | 14.14.0 | state transitions + evidence reveal only |
| `recharts` | 3.10.1 | **only** the thermal-dose / retention curve on the Evidence tab. Everything else is inline SVG |

Deliberately absent: no form library (one textarea, one input), no i18n, no auth, no animation library beyond `motion`.

---

## 1. Route and component tree

Four routes. `(server)` = React Server Component, `(client)` = `'use client'`. `[shadcn]` = generated primitive used as-is or thinly wrapped; `[custom]` = written for this app.

### 1.1 File tree

```
app/
  layout.tsx                      (server)  fonts, theme vars, AppShell
  globals.css                               Tailwind v4 @theme tokens
  page.tsx                        (server)  LANDING — BUILD LAST
  lab/
    page.tsx                      (server)  reads fixture manifest, renders LabWorkbench
    loading.tsx                   (server)  LabSkeleton
    error.tsx                     (client)  LabErrorBoundary
  compare/page.tsx                (server)
  method/page.tsx                 (server)  MDX, zero client JS
  api/
    analyze/route.ts              POST  → gateway
    ask/route.ts                  POST  → gateway
    compare/route.ts              POST  → gateway
    health/route.ts               GET   → gateway
components/…
lib/
  engine/   contracts.ts  decode.ts  client.ts  http-client.ts  fixture-client.ts  errors.ts
  state/    diff.ts  cell.ts  reason-codes.generated.ts  analyte-view.ts
  graph/    build.ts  layout.worker.ts  collapse.ts  focus.ts
  store/    session-store.ts  ui-store.ts
fixtures/<slug>/analyze.json  ask/<questionKey>.json  compare/<pairKey>.json  manifest.json
scripts/  record-fixtures.ts  sync-reason-codes.ts
```

**Route handlers are BFF proxies, not logic.** They hold the gateway URL and any token server-side, kill CORS, and stamp `contract` + `engine` onto every response. The browser calls them; a Server Component never does — fetching your own route handlers from a server component is the documented anti-pattern, so shared logic lives in `lib/` and is imported directly.

### 1.2 Shell (all routes)

| Component | Kind | Responsibility (one line) |
|---|---|---|
| `AppShell` | (server) [custom] | Header, nav between the four routes, footer with engine stamp. |
| `ModeBadge` | (client) [custom + shadcn Badge/Tooltip] | Always-visible LIVE / RECORDED pill — the presenter never has to guess which mode is running. |
| `EngineStampPopover` | (client) [shadcn Popover] | Engine version, `VALIDATOR_ID`, registry SHA, fixture recording date. |
| `ThemeToggle` | (client) [shadcn Button + DropdownMenu] | Light/dark; projector-safe dark is the default. |
| `KeyboardHelp` | (client) [shadcn Dialog] | `?` opens the key map (scrub, tabs, focus query). |
| `ContractDriftDialog` | (client) [shadcn Dialog] | Shown only when the zod decoder rejects a response — names the failing path, offers "switch to recorded". |
| `ReducedMotionProvider` | (client) [custom] | Reads `prefers-reduced-motion` once, puts it in context; every `motion` call reads it. |

### 1.3 `/lab` — the workbench

**Root**

| Component | Kind | Responsibility |
|---|---|---|
| `LabWorkbench` | (client) [custom] | Owns the stores, the keyboard map, and URL sync. The only client root on the route. |
| `LabPanes` | (client) [shadcn Resizable] | `ResizablePanelGroup` → 3 `ResizablePanel` + 2 handles; sizes persisted to `localStorage`, default 24/44/32. |
| `LabSkeleton` | (server) [shadcn Skeleton] | Layout-identical skeleton so pane widths never shift (CLS). |

**Pane A — RECIPE**

| Component | Kind | Responsibility |
|---|---|---|
| `RecipePane` | (client) [custom] | Scroll container for the three sections below. |
| `RecipeSourceBar` | (client) [custom] | Title, source id, `raw_sha256` short hash, "replace recipe" button. |
| `RecipeInputDialog` | (client) [shadcn Dialog + Textarea + Button] | Paste-a-recipe modal; submits to `analyze`. |
| `FixturePicker` | (client) [shadcn Command] | Searchable list of recorded recipes; the demo path. |
| `IngredientList` | (client) [custom] | Ingredient lines in source order. |
| `IngredientRow` | (client) [custom] | One parsed line: raw text preserved, normalised quantity shown beside it, never over it. |
| `LotChip` | (client) [custom] | A lot id + colour swatch; the single shared identity token across all three panes and the graph. |
| `StepList` | (client) [custom] | Steps as a roving-tabindex list; arrow keys scrub. |
| `StepRow` | (client) [custom] | Step text, event chips, delta count badge; active step gets a 2px left rule, not just a tint. |
| `StepSpanHighlight` | (client) [custom] | Marks the `Span` of the hovered/selected event inside the raw step text. |
| `EventChip` | (client) [custom] | One `EventCandidate`: `event_kind`, consumes/produces arity glyph. |
| `AlternativeGroupChip` | (client) [shadcn Badge] | Marks an `alternative_group` — "A **or** B, one selected" — so a viewer can see the IR never treats alternatives as a conjunction. |

**Pane B — STATE TIMELINE + LOT GRAPH**

| Component | Kind | Responsibility |
|---|---|---|
| `StatePane` | (client) [custom] | Vertical split: delta strip + scrubber on top, graph below (60/40, draggable). |
| `StateDeltaStrip` | (client) [custom SVG] | Whole-recipe overview: one column per step, five rows (G/C/Q/Y/P), cell shaded by change magnitude. Click = scrub. |
| `StepScrubber` | (client) [shadcn Slider + custom ticks] | The t control; ticks carry delta weight so heavy steps are visibly bigger. |
| `TimelineTrack` | (client) [custom] | Horizontal step rail aligned to the **same x scale as the graph**. |
| `TimelineNode` | (client) [custom] | One step marker + `DeltaBadge`. |
| `DeltaLedger` | (client) [custom] | The ΔS(t→t+1) ledger — see §4. |
| `DeltaBlockRow` | (client) [custom] | One of G/C/Q/Y/P with its changed cells. |
| `DeltaCell` | (client) [custom] | One cell's transition, old → new. |
| `DeltaNumber` | (client) [custom] | Numeric transition with signed Δ and direction glyph. |
| `DeltaInterval` | (client) [custom SVG] | Interval transition: old range ghosted behind new range on one axis. |
| `KnownessDot` | (client) [custom] | ● known / ○ unknown / ⊘ n/a. Shape, not colour, carries the meaning. |
| `LotGraph` | (client) [custom] | `next/dynamic(..., { ssr: false })` wrapper — see §5. |
| `LotGraphCanvas` | (client) [@xyflow/react] | `<ReactFlow>` with read-only interaction flags. |
| `IngredientLotNode` / `MixtureNode` / `IntermediateNode` / `DiscardSinkNode` / `AlternativeGroupNode` | (client) [custom] | The five node renderers, all `memo`ised, module-scope registered. |
| `TransformEdge` / `MergeEdge` / `SplitEdge` / `DiscardEdge` / `AlternativeEdge` | (client) [custom] | The five edge renderers. |
| `GraphControls` | (client) [shadcn Button/Toggle] | Fit, focus-mode toggle, expand-collapsed, whole-lineage toggle. |
| `GraphLegend` | (client) [custom] | Node + edge semantics, always visible — this is a research demo, the legend is content. |
| `GraphTextAlternative` | (client) [shadcn Table] | The DAG as a lot→event→lot table. Screen-reader equivalent and a presenter fallback. |

**Pane C — INSPECTOR**

| Component | Kind | Responsibility |
|---|---|---|
| `InspectorPane` | (client) [shadcn Tabs] | Five tabs, `1`–`5` keys, tab persisted in the URL. |
| `StateTab` | (client) [custom] | Full `S_t` for the selected lot at step t. |
| `StateBlockAccordion` | (client) [shadcn Accordion] | G/C/Q/Y/P sections; each header shows known/unknown counts. |
| `CellRow` | (client) [custom] | Field label + `CellValue` + `BasisTag`. |
| **`CellValue`** | (client) [custom] | **The only component allowed to branch on a `Cell`.** Renders known / unknown / n/a via `fold`. |
| `BasisTag` | (client) [shadcn Badge] | The `b` string, monospace, with a `_PARTIAL` suffix warning. |
| `UnknownTag` / `NaTag` | (client) [shadcn Badge + Tooltip] | Reason code + human label; tooltip shows the raw code. |
| `EvidenceTab` | (client) [custom] | Applied / found-not-applied / excluded, in that order. |
| `EvidenceCard` | (client) [shadcn Card] | One `EVD` row: value, unit, tier, matrix, process, and why it did or didn't apply. |
| `AppliedBadge` / `NotAppliedBadge` | (client) [shadcn Badge] | `APPLIED` vs `FOUND_NOT_APPLIED` — the engine's own basis strings. |
| `EvidenceValue` | (client) [custom] | Point or interval; **never collapses an interval**. |
| `RetentionCurve` | (client) [recharts] | The one chart: retention vs thermal dose, with the evidence points overlaid. |
| `CompatibilityTab` | (client) [custom] | The 9-axis vector, inspectable. |
| `CompatMatrix` | (client) [custom] | Axis × evidence-row grid of verdicts. |
| `CompatAxisRow` | (client) [custom] | One axis: verdict, weight, and the compared values side by side. |
| `AxisVerdictCell` | (client) [custom] | MATCH / NEAR / **UNKNOWN** / MISMATCH, with UNKNOWN visually distinct from both MATCH and MISMATCH. |
| `RankingScoreNote` | (client) [custom] | Prints the scalar score with the words "ranking only, not a confidence" attached. Non-removable. |
| `ClaimPacketTab` | (client) [custom] | The packet, rendered as a contract. |
| `AllowedClaimsList` / `ForbiddenClaimsList` / `CaveatList` | (client) [custom] | The three lists; forbidden is shown, not hidden. |
| `PrecisionCapMeter` | (client) [custom SVG] | `max_allowed_precision` as a discrete ladder. |
| `ClaimPacketJsonDrawer` | (client) [shadcn Sheet] | Raw JSON + copy. Credibility device for a research audience. |
| `ProvenanceTab` | (client) [custom] | Where every value came from. |
| `KnownessBar` | (client) [custom SVG] | Stacked known/unknown/na proportion for the selected state. |
| `ProvenanceTree` | (client) [custom] | Cell → basis → producer module → source span. |
| `SpanLink` | (client) [custom] | Jumps to and highlights the span in Pane A. |

**Query bar (persistent, bottom, spans all panes)**

| Component | Kind | Responsibility |
|---|---|---|
| `QueryBar` | (client) [custom] | Sticky footer; owns ask state. |
| `QuestionInput` | (client) [shadcn Input + Command] | Free text with suggestions drawn from the fixture question set. |
| `QuestionChips` | (client) [shadcn Badge] | Four canned demo questions, one click each. |
| `AskStatus` | (client) [custom] | Stage label while the engine works. |
| `AnswerCard` | (client) [shadcn Card] | The answered case. |
| `VerdictPill` | (client) [custom] | ANSWER / ABSTAIN / UNKNOWN. |
| `AbstainCard` | (client) [shadcn Card] | **Same card chrome as `AnswerCard`** — see §7. |
| `UnknownCard` | (client) [shadcn Card] | Value genuinely not determined; lists the `unknown_reasons`. |
| `QuestionHistoryRail` | (client) [shadcn ScrollArea] | The session's M questions; click to restore that answer and its step. |

### 1.4 `/compare`

`CompareWorkbench` (client) · `ScenarioPicker` ×2 [shadcn Command] · `ScenarioColumn` · `StateDiffTable` · `StateDiffRow` · `EvidenceDiffList` · `VerdictDiffRow` · `DiffLegend` · `CompareEmptyState`. Reuses `CellValue`, `DeltaCell`, `KnownessDot`, `EvidenceCard` unchanged — if a component can't be reused here, it was built wrong.

### 1.5 `/method`

All server, zero client JS. MDX page + `MethodSection`, `ContractTable`, `InvariantTable`, `OpenInvariantsCallout`, `FixtureProvenanceTable`, `VocabularyTable`. `OpenInvariantsCallout` renders `OPEN_INVARIANTS` verbatim — the page must not imply coverage the engine doesn't claim.

### 1.6 shadcn primitives to generate

`accordion badge button card command dialog dropdown-menu input popover resizable scroll-area separator sheet skeleton slider sonner switch table tabs textarea toggle tooltip`

```bash
pnpm dlx shadcn@latest init --base radix
pnpm dlx shadcn@latest add accordion badge button card command dialog \
  dropdown-menu input popover resizable scroll-area separator sheet \
  skeleton slider sonner switch table tabs textarea toggle tooltip
```

Use `--dry-run` / `--diff` (new in CLI v4) before any later `add` so generated files aren't clobbered after you've edited them.

---

## 2. TypeScript interfaces

### 2.1 The UNKNOWN core

The engine already emits `{v, b}` or `{v: null, u}`. The type system's job is to make the second shape unrenderable as a value.

```ts
// lib/engine/contracts.ts

/** Engine-owned vocabularies. Branded so a UI string can't be passed as one. */
export type Basis      = string & { readonly __brand: 'Basis' };
export type ReasonCode = string & { readonly __brand: 'ReasonCode' };
export type EventId    = string & { readonly __brand: 'EventId' };
export type EntityId   = string & { readonly __brand: 'EntityId' };
export type EvdId      = string & { readonly __brand: 'EvdId' };

/** Ranking only. Branded so it can never reach a component expecting a confidence. */
export type RankingScore = number & { readonly __brand: 'RankingScore' };

export type Scalar = number | string | boolean;

export interface Interval { readonly low: number; readonly high: number; readonly unit?: string }
export interface Point    { readonly point: number; readonly unit?: string }
export type Quantity = Point | Interval;
export const isInterval = (q: Quantity): q is Interval => 'low' in q;

/* ---------- the three states a value can be in ---------- */

export interface Known<T> {
  readonly kind: 'known';
  readonly value: T;
  readonly basis: Basis;
  /** engine signals this via a `_PARTIAL` basis suffix (e.g. SUM_SCENARIO_PARTIAL) */
  readonly partial: boolean;
}
export interface Unknown     { readonly kind: 'unknown';        readonly reason: ReasonCode }
export interface NotApplicable { readonly kind: 'na';           readonly reason: ReasonCode }

export type Cell<T> = Known<T> | Unknown | NotApplicable;
```

**Why this is unrenderable-as-a-value:** `value` exists only on `Known<T>`. `cell.value` is a compile error on `Cell<T>`; `cell.kind === 'known' && cell.value` is the only way through. There is deliberately **no** `unwrap(cell): T`, no `cell.value ?? '—'`, no default. The only sanctioned consumer is a total fold:

```ts
// lib/state/cell.ts
export interface CellHandlers<T, R> {
  known(value: T, basis: Basis, partial: boolean): R;
  unknown(reason: ReasonCode): R;
  na(reason: ReasonCode): R;
}

export function fold<T, R>(c: Cell<T>, h: CellHandlers<T, R>): R {
  switch (c.kind) {
    case 'known':   return h.known(c.value, c.basis, c.partial);
    case 'unknown': return h.unknown(c.reason);
    case 'na':      return h.na(c.reason);
    default: { const _never: never = c; return _never; }
  }
}
```

Adding a fourth state later breaks every call site at compile time. That is the point.

**Enforcement beyond types** (types can be defeated with `!` or `as`). Add to `eslint.config.ts`:

```ts
// ban raw .value access outside the one sanctioned component + the fold
{
  files: ['components/**/*.tsx'],
  ignores: ['components/cell/**'],
  rules: {
    'no-restricted-syntax': ['error', {
      selector: "MemberExpression[property.name='value'][object.name=/^(cell|c|state|q)$/]",
      message: 'Render a Cell through <CellValue> or fold(). Never read .value directly.',
    }],
    '@typescript-eslint/no-non-null-assertion': 'error',
  },
}
```

### 2.2 Decode, not transform

```ts
// lib/engine/decode.ts
import { z } from 'zod';
import { NA_REASON_CODES } from '@/lib/state/reason-codes.generated';

const wireCell = z.union([
  z.object({ v: z.unknown(), b: z.string() }),
  z.object({ v: z.null(),    u: z.string() }),
]);

/** Structural decode only. No renaming, no inference, no defaults. */
export function cellOf<T>(raw: unknown, value: z.ZodType<T>): Cell<T> {
  const w = wireCell.parse(raw);
  if ('b' in w) {
    return {
      kind: 'known',
      value: value.parse(w.v),
      basis: w.b as Basis,
      partial: w.b.endsWith('_PARTIAL'),
    };
  }
  // SAFE DEFAULT: an unrecognised reason code reads as `unknown`, never as n/a.
  return NA_REASON_CODES.has(w.u)
    ? { kind: 'na',      reason: w.u as ReasonCode }
    : { kind: 'unknown', reason: w.u as ReasonCode };
}
```

Three rules that keep the engine frozen:

1. **`NA_REASON_CODES` is generated, never hand-edited.** `scripts/sync-reason-codes.ts` walks `registry/` and the `U("...")` literals in `src/culinarystate/composition/` and emits the set. A code the UI has never seen defaults to `unknown` — the conservative reading.
2. **Reason codes stay `string`**, not a closed literal union. A new engine code must not break the build. Human labels come from an optional lookup; the fallback is the raw code, shown verbatim.
3. **Flat engine keys stay flat in the contract.** `Y` really is emitted as `vitc_route`, `vitc_compat`, `lycopene_evidence`, … A *view adapter* (`lib/state/analyte-view.ts`, `groupAnalytes(Y): Record<TargetId, AnalyteView>`) regroups them for rendering. The adapter lives in the UI; the engine is never asked to restructure.

### 2.3 `POST /api/analyze`

```ts
export interface EngineStamp {
  readonly engineVersion: string;
  readonly validatorId: string;      // e.g. "V4_STEP18_INVARIANTS"
  readonly validatorStatus: 'DRAFT_PENDING_16c' | 'PROMOTED';
  readonly registrySha: string;
  readonly modelId: string | null;   // null when no LLM rung ran
  readonly builtAt: string;          // ISO
}

export type BlockKey = 'G' | 'C' | 'Q' | 'Y' | 'P';

/* ---- Event IR, mirroring docs/EVENT_IR_CONTRACT.md §2 ---- */

export type EventKind       = string;            // vocabulary-checked by V3, engine-owned
export type EntityType      = 'INGREDIENT_LOT' | 'MIXTURE' | 'INTERMEDIATE' | (string & {});
export type Lifecycle       = 'CREATED' | 'ACTIVE' | 'DISCARDED' | (string & {});
export type AllocationKind  = 'SPLIT' | 'MERGE' | (string & {});

export interface Span {
  readonly textId: string;
  readonly start: number;
  readonly end: number;
  readonly texts: readonly string[];   // V1 round-trips these against raw bytes
}

export interface EventNode {
  readonly eventId: EventId;
  readonly order: readonly [stepIndex: number, ordinal: number];  // TEXT order, not execution order
  readonly span: Span | null;
  readonly consumes: readonly EntityId[];
  readonly produces: readonly EntityId[];
  readonly discards: readonly EntityId[];
  readonly dependsOn: readonly EventId[];          // DAG, enforced by V4
  readonly attributes: readonly ValueClaim[];
  readonly claimRoute: string | null;
  readonly alternativeGroup: string | null;        // CR-25
  readonly conditionProfileId: string | null;      // CR-25
}

export interface EntityNode {
  readonly entityId: EntityId;
  readonly entityType: EntityType;
  readonly lifecycle: Lifecycle;
  readonly parentEntityIds: readonly EntityId[];
  readonly createdByEventId: EventId | null;
  readonly span: Span | null;
  readonly attributes: readonly ValueClaim[];
}

export interface Allocation {
  readonly allocId: string;
  readonly kind: AllocationKind;
  readonly basis: string;                          // CR-26 allocation basis
  readonly parentEntityId: EntityId;
  readonly childEntityId: EntityId;
  readonly eventId: EventId;
  readonly fraction: Cell<number>;                 // may be UNKNOWN — must never render as 0
}

export interface ValueClaim {
  readonly ownerId: string;
  readonly field: string;
  readonly claimKind: string;
  readonly cell: Cell<Scalar | Interval>;          // carries status+origin+route via basis/reason
  readonly origin: string;                         // CR-02
  readonly claimRoute: string | null;              // CR-02
  readonly span: Span | null;
  readonly unit: string | null;
  readonly trace: readonly string[];
}
```

The five blocks, field-for-field from `state_full.py:158-180`:

```ts
export interface StructureBlock {           // G — lineage / structure
  readonly process:           Cell<string>;
  readonly family:            Cell<string>;
  readonly event_kind:        Cell<EventKind>;
  readonly lot_members:       Cell<readonly string[]>;
  readonly history:           Cell<readonly string[]>;     // ordered process history
  readonly cell_integrity:    Cell<string>;                // from cut history
  readonly heat_steps_so_far: Cell<number>;
  readonly is_heat_step:      Cell<boolean>;
}

export interface CompositionBlock {         // C — composition
  readonly salt_present:                 Cell<boolean>;
  readonly acid_present:                 Cell<boolean>;
  readonly lipid_present:                Cell<boolean>;
  readonly aqueous_present:              Cell<boolean>;
  readonly contact_phase:                Cell<'AQUEOUS' | 'LIPID' | 'AQUEOUS+LIPID' | (string & {})>;
  readonly member_composition:           Cell<Readonly<Record<string, number>>>;
  readonly nacl_equiv_fraction_as_added: Cell<number>;
  readonly fat_fraction_as_added:        Cell<number>;
  readonly lot_acidity_band:             Cell<string>;
  readonly own_composition:              Cell<Readonly<Record<string, number>>>;  // USDA SR
  readonly salt_exposure_before:         Cell<boolean>;
  readonly acid_exposure_before:         Cell<boolean>;
}

export interface ConditionBlock {           // Q — physical conditions
  readonly medium:        Cell<string>;
  readonly temperature_c: Cell<Quantity>;
  readonly duration_min:  Cell<Quantity>;
  readonly lid_state:     Cell<string>;
  readonly start_mode:    Cell<string>;
  readonly piece_size:    Cell<string>;
  readonly matrix_class:  Cell<string>;
  readonly food_t_typical:              Cell<Quantity>;     // L2 SCENARIO
  readonly moisture_cap:                Cell<Quantity>;     // L2 SCENARIO
  readonly thermal_dose_typical_min:    Cell<number>;       // L2 SCENARIO
  readonly cumulative_thermal_dose_min: Cell<number>;       // partial flag matters
  readonly hot_aqueous_minutes:         Cell<number>;
  readonly hot_fat_minutes:             Cell<number>;
  readonly oxygen_exposure_proxy:       Cell<'LIMITED_LID' | 'OPEN' | (string & {})>;
}

/** Engine emits flat `${target}_*` keys. Kept flat; regrouped by groupAnalytes() for rendering. */
export interface AnalyteBlock {             // Y — analyte state
  readonly [key: `${string}_route`]:          Cell<string>;
  readonly [key: `${string}_compat`]:         Cell<Readonly<Record<string, AxisVerdict>>>;
  readonly [key: `${string}_frozen_reasons`]: Cell<readonly string[]>;
  readonly [key: `${string}_evidence`]:       Cell<readonly string[]>;
  readonly vitc_formula_retention_typical:    Cell<number>;   // FORMULA_RESEARCH_ONLY, NOT_VALIDATED
}

/** P — provenance roll-up. Derived by walking the other four blocks' basis/reason fields. */
export interface ProvenanceBlock {
  readonly cellsTotal:   number;
  readonly cellsKnown:   number;
  readonly cellsUnknown: number;
  readonly cellsNa:      number;
  readonly byBlock: Readonly<Record<Exclude<BlockKey, 'P'>, {
    readonly known: number; readonly unknown: number; readonly na: number;
  }>>;
  /** fields whose basis carried _PARTIAL — "this sum is incomplete and says so" */
  readonly partialSums: readonly string[];
  readonly labels: readonly ('DERIVED_VIEW' | 'SCENARIO' | 'RESEARCH_ONLY')[];
}

export interface StateAtStep {
  readonly step: number;            // 1-based, engine's numbering
  readonly eventId: EventId;
  readonly action: string;
  readonly foodId: string;
  readonly food: string;
  readonly G: StructureBlock;
  readonly C: CompositionBlock;
  readonly Q: ConditionBlock;
  readonly Y: AnalyteBlock;
  readonly P: ProvenanceBlock;
}

export interface Diagnostic {
  readonly code: string;            // e.g. "VNEXT_ALTERNATIVE_SKIPPED"
  readonly severity: 'INFO' | 'WARN' | 'ISSUE';
  readonly path: string | null;
  readonly message: string;
}

export interface AnalyzeResponse {
  readonly contract: 'culinarystate.analyze.v1';
  readonly engine: EngineStamp;
  readonly source: { readonly textId: string; readonly rawSha256: string };
  readonly recipe: {
    readonly title: string | null;
    readonly ingredients: readonly { readonly raw: string; readonly span: Span; readonly entityId: EntityId | null }[];
    readonly steps: readonly { readonly index: number; readonly raw: string; readonly span: Span }[];
  };
  readonly events:      readonly EventNode[];
  readonly entities:    readonly EntityNode[];
  readonly allocations: readonly Allocation[];
  readonly states:      readonly StateAtStep[];
  readonly diagnostics: readonly Diagnostic[];
  readonly failure:     { readonly code: string; readonly message: string } | null;
  /** V4 scopes reported as NOT CHECKED. Rendered, never hidden. */
  readonly openInvariants: readonly string[];
}
```

### 2.4 `POST /api/ask`

```ts
export const COMPAT_AXES = ['matrix','state','process','time','temperature','medium','target','basis','tier'] as const;
export type CompatAxis = typeof COMPAT_AXES[number];

/** UNKNOWN scores 0.25 — distinct from MATCH 1.0 and MISMATCH 0.0. Never collapse to a boolean. */
export type AxisVerdict = 'MATCH' | 'NEAR' | 'UNKNOWN' | 'MISMATCH';

export interface CompatibilityVector {
  readonly axes:    Readonly<Record<CompatAxis, AxisVerdict>>;
  readonly weights: Readonly<Record<CompatAxis, number>>;
  readonly score:   RankingScore;                 // branded: ranking only
  readonly selectedAxes: readonly CompatAxis[];
}

/** Why a piece of evidence did or did not apply. This union is the UI's whole job. */
export type EvidenceApplication =
  | { readonly kind: 'applied';           readonly value: Quantity; readonly basis: Basis }
  | { readonly kind: 'found_not_applied'; readonly blockedBy: readonly CompatAxis[]; readonly reason: ReasonCode }
  | { readonly kind: 'excluded';          readonly reason: ReasonCode };

export interface EvidenceRow {
  readonly evdId: EvdId;
  readonly tier: 'E1'|'E2'|'E3'|'E4'|'E5'|'E6'|'E7';
  readonly matrix: { readonly ingredientId: string | null; readonly rawName: string | null; readonly foodGroup: string | null };
  readonly process: { readonly processId: string | null; readonly family: string | null };
  readonly target: string;
  readonly reported: Cell<Quantity>;
  readonly compatibility: CompatibilityVector;
  readonly application: EvidenceApplication;
  readonly citation: { readonly label: string; readonly doi: string | null; readonly url: string | null };
}

export interface ClaimPacket {              // keys from claim_packet.py:83-95
  readonly food: string;
  readonly step: number;
  readonly action: string;
  readonly target: string;
  readonly questionKind: string;
  readonly route: string;
  readonly allowedClaims:   readonly string[];
  readonly requiredCaveats: readonly string[];
  readonly forbiddenClaims: readonly string[];
  readonly evidenceIds:     readonly EvdId[];
  readonly evidenceValues:  readonly Cell<Quantity>[];
  readonly nearEvidenceIds: readonly EvdId[];
  readonly compatibility:   CompatibilityVector;
  readonly selectedAxes:    readonly CompatAxis[];
  readonly maxAllowedPrecision: 'DIRECTIONAL' | 'ORDER_OF_MAGNITUDE' | 'INTERVAL' | 'POINT';
  readonly unknownReasons:  readonly ReasonCode[];
}

export interface AbstainReason {
  readonly code: ReasonCode;
  readonly axis: CompatAxis | null;           // which axis blocked, when one did
  readonly evdIds: readonly EvdId[];          // evidence that was found but not applied
  readonly message: string;
}

/**
 * Three outcomes, no fourth. ABSTAIN = gates refused the available evidence.
 * UNKNOWN = the value is genuinely not determined. Both are terminal, neither is an error.
 */
export type Verdict =
  | { readonly kind: 'ANSWER';
      readonly statement: string;
      readonly value: Cell<Quantity>;
      readonly precision: ClaimPacket['maxAllowedPrecision'];
      readonly caveats: readonly string[] }
  | { readonly kind: 'ABSTAIN'; readonly reasons: readonly AbstainReason[] }
  | { readonly kind: 'UNKNOWN'; readonly reasons: readonly ReasonCode[] };

export interface AskResponse {
  readonly contract: 'culinarystate.ask.v1';
  readonly engine: EngineStamp;
  readonly question: { readonly raw: string; readonly normalised: string; readonly kind: string };
  readonly scope: { readonly foodId: string; readonly step: number; readonly target: string };
  readonly verdict: Verdict;
  readonly claimPacket: ClaimPacket;
  readonly evidence: readonly EvidenceRow[];     // applied + not-applied + excluded, all of them
  readonly diagnostics: readonly Diagnostic[];
}
```

`Verdict` is a union, not a nullable answer. There is no `statement: string | null` anywhere, so an ABSTAIN cannot be rendered through the answer path — the component for it doesn't accept that shape.

### 2.5 `POST /api/compare`

```ts
export interface ScenarioRef { readonly id: string; readonly label: string; readonly recipeTextId: string }

export interface CellDiff {
  readonly block: BlockKey;
  readonly field: string;
  readonly a: Cell<unknown>;
  readonly b: Cell<unknown>;
  readonly transition: CellTransition;        // §4
}

export interface EvidenceDiff {
  readonly evdId: EvdId;
  readonly a: EvidenceApplication | null;     // null = not retrieved in A at all
  readonly b: EvidenceApplication | null;
}

export interface CompareResponse {
  readonly contract: 'culinarystate.compare.v1';
  readonly engine: EngineStamp;
  readonly a: ScenarioRef;
  readonly b: ScenarioRef;
  readonly stepAlignment: readonly (readonly [aStep: number | null, bStep: number | null])[];
  readonly stateDiff:    readonly CellDiff[];
  readonly evidenceDiff: readonly EvidenceDiff[];
  readonly verdictDiff: {
    readonly question: string;
    readonly a: Verdict;
    readonly b: Verdict;
  } | null;
  readonly diagnostics: readonly Diagnostic[];
}
```

`stepAlignment` carries `null` on either side so an unmatched step is explicit rather than silently dropped — the same discipline as UNKNOWN, applied to alignment.

### 2.6 `GET /api/health`

```ts
export interface HealthResponse {
  readonly contract: 'culinarystate.health.v1';
  readonly status: 'ok' | 'degraded' | 'down';
  readonly engine: EngineStamp;
  readonly capabilities: {
    readonly analyze: boolean;
    readonly ask: boolean;
    readonly compare: boolean;
    readonly llmProposer: boolean;
  };
  readonly latencyMs: number | null;
}
```

Every response carries `contract` and `engine`. The decoder rejects a `contract` mismatch outright and raises `DecodeError`, which is what turns silent engine/UI drift into a visible, named failure (§7).

---

## 3. State management

**Four stores, each with one job. Nothing shared between them.**

| Layer | Tool | Holds | Why |
|---|---|---|---|
| Static content | Server Components | `/`, `/method`, `/lab` fixture manifest | No interactivity; zero client JS. `/method` is the whole literature/contract write-up and must not ship a kilobyte of React. |
| Server responses | TanStack Query | `analyze`, `ask`, `compare`, `health` results | Content-keyed cache. A session is 1 recipe × N steps × M questions; re-asking a question or scrubbing back must be free. |
| Session view state | Zustand (`sessionStore`) | `activeStep`, `selectedLotId`, `selectedEventId`, `inspectorTab`, `graphMode`, `mode: 'live' \| 'recorded'` | Three panes + a graph all read `activeStep`. Selector subscriptions mean a scrub re-renders only the subscribers. |
| Shareable state | URL search params | `?fixture=…&t=7&lot=L3&tab=evidence&q=…` | A presenter can deep-link a slide; a reviewer can send a link to one finding. |

### Why Zustand and not the alternatives

- **React Context is wrong here.** `activeStep` changes on every scrub tick. Context has no selector mechanism, so each tick re-renders every consumer — all three panes plus every graph node. With 30+ nodes that's a dropped frame per tick.
- **URL-as-state is wrong as the primary.** `useSearchParams` + `router.replace` round-trips through the router on every tick. The URL is a *mirror*, written with a 250 ms-debounced `history.replaceState` (no router round-trip, no scroll reset), and read only on mount and on back/forward.
- **Server state is wrong for `t`.** Scrubbing is not navigation and must not re-fetch.
- **Zustand over Redux/Jotai:** 1 store, ~40 lines, selectors built in, no provider, and it reads fine outside React (the layout worker and the keyboard handler both touch it).
- **TanStack Query over `useState` + `fetch`:** it gives the content-keyed cache, in-flight dedupe, retry-with-backoff, and the `onError` hook that drives the fallback flip (§6) — all of which I'd otherwise hand-roll.

```ts
// lib/store/session-store.ts
interface SessionState {
  mode: 'live' | 'recorded';
  recipeKey: string | null;              // sha256 of raw text — the cache key for everything
  activeStep: number;
  selectedLotId: EntityId | null;
  selectedEventId: EventId | null;
  inspectorTab: 'state' | 'evidence' | 'compatibility' | 'claim' | 'provenance';
  graphMode: 'focus' | 'whole';
  expandedCollapsed: ReadonlySet<string>;
  questionLog: readonly { key: string; raw: string; at: number }[];

  setStep(t: number): void;              // clamped; writes the URL mirror, debounced
  selectLot(id: EntityId | null): void;
  setTab(tab: SessionState['inspectorTab']): void;
  degradeToRecorded(why: string): void;  // the single mode-flip entry point
}
```

### Derived data: precompute once, never per frame

On `analyze` success, one pass builds everything the panes need and parks it in the Query cache beside the response:

```ts
// N <= ~40 steps, so this is a few ms total and removes all per-frame work
interface DerivedSession {
  readonly deltas:        readonly StateDelta[];                 // all N-1 deltas, built once
  readonly stripMatrix:   ReadonlyArray<Readonly<Record<BlockKey, number>>>;  // StateDeltaStrip
  readonly graph:         { nodes: GraphNode[]; edges: GraphEdge[] };
  readonly layout:        Readonly<Record<string, { x: number; y: number }>>; // from the worker
  readonly lotsAliveAt:   readonly ReadonlySet<EntityId>[];       // focus mode, per step
  readonly analytes:      Readonly<Record<TargetId, AnalyteView>>;
}
```

Scrubbing then costs one `useSyncExternalStore` read and an array index. Nothing is recomputed while the slider moves.

### Keyboard map (owned by `LabWorkbench`)

`←`/`→` step ±1 · `Shift+←/→` ±5 · `Home`/`End` first/last · `1`–`5` inspector tab · `/` focus query bar · `f` toggle graph focus mode · `?` help. Scrub keys are throttled with `requestAnimationFrame`, not a timer, so held-arrow scrubbing stays at one update per frame.

---

## 4. The state-delta visualisation

Two components at two scales. The strip answers *where in the recipe does anything happen*; the ledger answers *what exactly changed here*.

### 4.1 The transition type

The classification is the design. Six of these eight cases are invisible in a naive before/after table, and two of them are the project's thesis.

```ts
// lib/state/diff.ts
export type CellTransition =
  | { kind: 'unchanged' }
  | { kind: 'value_changed';  from: Known<unknown>; to: Known<unknown> }
  | { kind: 'became_known';   fromReason: ReasonCode; to: Known<unknown> }        // ← thesis
  | { kind: 'became_unknown'; from: Known<unknown>; toReason: ReasonCode }        // ← thesis
  | { kind: 'reason_changed'; fromReason: ReasonCode; toReason: ReasonCode }
  | { kind: 'basis_changed';  from: Known<unknown>; to: Known<unknown> }          // same value, new provenance
  | { kind: 'became_partial'; from: Known<unknown>; to: Known<unknown> }          // sum went incomplete
  | { kind: 'appeared';       to: Cell<unknown> }
  | { kind: 'disappeared';    from: Cell<unknown> };

export interface CellDelta {
  readonly block: BlockKey;
  readonly field: string;
  readonly label: string;
  readonly transition: CellTransition;
  readonly weight: number;      // 0..1, drives strip shading and tick height
}

export interface StateDelta {
  readonly from: number;        // step t
  readonly to: number;          // step t+1
  readonly cells: readonly CellDelta[];
  readonly counts: Readonly<Record<BlockKey, number>>;
  readonly knownessShift: number;   // (+) more known, (−) more unknown
}

export function diffState(a: StateAtStep, b: StateAtStep): StateDelta;  // pure, total, unit-tested
```

`weight` is computed per transition kind: `became_unknown` 1.0, `became_known` 0.9, `value_changed` scaled by relative magnitude (0.3–0.8), `basis_changed` 0.4, `became_partial` 0.5, `reason_changed` 0.2, `unchanged` 0.

### 4.2 `<StateDeltaStrip>` — recipe scale

```tsx
interface StateDeltaStripProps {
  deltas: readonly StateDelta[];
  activeStep: number;
  onScrub: (t: number) => void;
}
```

One inline `<svg>`, width = pane width, height = 96px. N columns × 5 rows (G, C, Q, Y, P top to bottom). Each `<rect>` is `COL_W × 16`, opacity = `0.12 + 0.88 * maxWeight(block, step)`. Columns containing a `became_unknown` get a 2px top-edge marker so the eye finds knowledge *loss* without reading a colour. Active step column carries a full-height 1px rule that **lines up pixel-for-pixel with `TimelineTrack` and the graph's x axis** — the three share one `xScale(step) = step * COL_W + COL_W / 2`.

Why SVG and not Recharts: 5×40 = 200 rects, one `<g>` per row, no axes, no tooltips library, no legend engine. Recharts here would be ~90 KB for a thing that is 40 lines of `<rect>`.

Accessibility: `role="img"` with a generated `aria-label` ("40 steps; largest change at step 12 in block Q; knowledge lost at steps 7 and 23"), plus `<GraphTextAlternative>`-style table behind a disclosure.

### 4.3 `<DeltaLedger>` — step scale

```tsx
interface DeltaLedgerProps {
  delta: StateDelta;
  showUnchanged: boolean;
  onToggleUnchanged: () => void;
  onSelectField: (block: BlockKey, field: string) => void;   // → Inspector State tab, scrolled
}
```

Layout: five `<DeltaBlockRow>`s in a fixed order with fixed heights (no reflow on scrub — this is where CLS would otherwise come from). Each row:

```
G  structure      3 changed              [●2  ○1]
   process        sauté            →  simmer                       RUNG_A
   heat_steps…    1                →  2                            LINEAGE+PHYSICS_V06_HEAT_FLAG
   cell_integrity ○ NO_CUT_CUE     →  ● INTACT                     CUT_HISTORY
```

Changed cells first, sorted by `weight` descending. Unchanged collapsed behind `Show 9 unchanged`.

### 4.4 `<DeltaCell>` — the atom

```tsx
interface DeltaCellProps { delta: CellDelta; dense?: boolean }
```

Rendered as a three-column grid: `field label | from → to | basis`. Every transition kind gets a distinct **non-colour** channel, because a projector will mangle hue:

| Transition | Encoding |
|---|---|
| `value_changed` | 2px left rule; old value at 60% opacity with a strike; new value in semibold; `→` between |
| `became_known` | `○ REASON` → `● value`; the dot glyph does the work |
| `became_unknown` | `● value` → `○ REASON`; **plus** a 2px top rule on the row — the only transition with two channels, because it's the one that matters most |
| `basis_changed` | value unchanged, basis tag gets a dotted underline + `was: <old basis>` on hover |
| `became_partial` | `⊂` prefix on the value, basis suffix `_PARTIAL` shown in full |
| `reason_changed` | `○ OLD_CODE → ○ NEW_CODE` |
| `appeared` / `disappeared` | `+` / `−` gutter marker |
| `unchanged` | 45% opacity, no rule |

Colour is layered **on top** of those glyphs, never instead of them, and the palette is tested at both themes.

### 4.5 `<DeltaNumber>` and `<DeltaInterval>`

```tsx
interface DeltaNumberProps { from: number; to: number; unit?: string }
```
Renders `180 → 185 °C` plus `(+5)` in a tabular-nums span. Sign glyph is `▲`/`▼`, so direction survives greyscale.

```tsx
interface DeltaIntervalProps { from: Interval; to: Interval; unit?: string }
```
A 160×20 inline SVG on one shared linear scale over `[min(from.low,to.low), max(from.high,to.high)]`: old range as a hollow 6px-tall outlined bar, new range as a filled 10px bar in front of it. Widening vs shifting is then a single glance. **Never** reduced to a midpoint — the engine refuses to collapse intervals and so does the UI.

### 4.6 Motion

`motion` is used in exactly two places on this route:

1. **Delta chips.** Each `DeltaCell` carries `layoutId={`${block}.${field}`}`, so when the step advances, a cell that changes value slides its new value in rather than popping. `transition: { duration: 0.18, ease: [0.4, 0, 0.2, 1] }`.
2. **Evidence reveal.** `EvidenceCard`s stagger in at 30 ms intervals, capped at 8 cards (beyond that, no stagger — a 40-card stagger is 1.2 s of nothing happening).

Guards: `ReducedMotionProvider` forces `duration: 0` and opacity-only when `prefers-reduced-motion: reduce`; and while the scrubber is being *dragged*, layout animation is disabled entirely (`layout={!isScrubbing}`) — animating 30 chips per tick is the easiest way to drop frames in this whole app.

---

## 5. React Flow graph plan

`@xyflow/react@12.12.1`. Read-only view, not an editor.

### 5.1 Node types

Registered at **module scope**, never inline — a fresh `nodeTypes` object per render makes React Flow rewrap every node component, which is the single most common performance bug in this library.

```ts
// module scope, outside any component
export const nodeTypes = {
  ingredientLot:    IngredientLotNode,
  mixture:          MixtureNode,
  intermediate:     IntermediateNode,
  discardSink:      DiscardSinkNode,
  alternativeGroup: AlternativeGroupNode,
} as const;
```

| Node type | Backed by | Visual | Data |
|---|---|---|---|
| `ingredientLot` | `EntityCandidate` with no `parentEntityIds` | Rounded rect, left-anchored, ingredient colour swatch | `{ entityId, name, lotColor, quantity: Cell<Quantity>, span }` |
| `mixture` | entity with ≥2 parents | Hexagon, parent swatches stacked along the left edge | `{ entityId, parentIds, memberCount }` |
| `intermediate` | entity with exactly 1 parent | Rect, inherits parent swatch | `{ entityId, processLabel, collapsedCount }` |
| `discardSink` | `discards` target | Small ⊘ terminal | `{ entityId, reason }` |
| `alternativeGroup` | `alternative_group` | Dashed container, "1 of N selected" header | `{ groupId, memberEventIds, committedEventId }` |

Every node also carries `{ stepIndex, lifecycle, knowness: {known, unknown, na} }`. `knowness` drives a 3px bottom bar on the node — the viewer sees provenance density on the graph itself without opening the Inspector.

### 5.2 Edge types and semantics

```ts
export const edgeTypes = {
  transform:   TransformEdge,
  merge:       MergeEdge,
  split:       SplitEdge,
  discard:     DiscardEdge,
  alternative: AlternativeEdge,
} as const;
```

| Edge | Arity | Stroke | Label | Data |
|---|---|---|---|---|
| `transform` | 1→1 | solid 1.5px | process name at zoom > 1.1 | `{ eventId, processLabel }` |
| `merge` | n→1 | solid 2px, converging into one port | — | `{ eventId, parentIds }` |
| `split` | 1→n | solid, fanning from one port | `fraction` + `basis`, or `○ UNKNOWN` | `{ eventId, allocId, fraction: Cell<number>, basis }` |
| `discard` | 1→⊘ | dashed, thin | discard reason | `{ eventId, reason }` |
| `alternative` | 1→n | dotted, 50% opacity | group id | `{ groupId, committed: boolean }` |

Two semantics that must not be fudged:

- **A `split` whose `fraction` is UNKNOWN renders `○` on the edge, not a guessed share.** Rendering `0.5` there would invent a number the engine refused to invent.
- **`alternative` edges are mutually exclusive.** Only the committed member gets a solid node border; the others are dotted at 50%. That is the `_alternatives` invariant made visible — "A or B" is a labelled choice, not two facts.

### 5.3 Layout

**The graph's x axis is time.** Not a layout output — a constraint.

```
1. build.ts        EventGraph JSON → { nodes, edges }, deterministic id order
2. layout.worker.ts  elkjs, 'layered', direction RIGHT,
                     elk.layered.layering.strategy = NETWORK_SIMPLEX
                     elk.layered.nodePlacement.strategy = BRANDES_KOEPF
                     elk.layered.considerModelOrder.strategy = NODES_AND_EDGES
                     elk.layered.crossingMinimization.strategy = LAYER_SWEEP
3. post-pass       OVERWRITE x := stepIndex * COL_W.  Keep elk's y.
4. cache           keyed by graphHash (sha of node/edge ids + types); survives scrubbing
```

Step 3 is the whole trick. elk is used **only** for crossing minimisation and lane assignment on the y axis; x is pinned to the step index so that the graph, `TimelineTrack` and `StateDeltaStrip` share one x scale and a viewer reads left-to-right as time. Without it, elk's layering drifts from step numbering as soon as a long-running lot spans several steps, and the three visualisations stop agreeing.

elk runs in a Web Worker (`new Worker(new URL('./layout.worker.ts', import.meta.url))`) so a 60-event layout never blocks the main thread. Results are deterministic — same input, same positions, every run, which matters when the demo is rehearsed.

### 5.4 Keeping it readable at 30+ events

Seven levers, in order of effect:

1. **Focus mode (default on).** Show only lots alive at step `t`, plus one lineage hop upstream and downstream. `lotsAliveAt[t]` is precomputed. A 60-event graph typically shows 6–12 nodes. `f` or the toolbar toggles to whole-lineage. This is the single biggest win and the reason the graph is usable at all on a projector.
2. **1:1 chain collapsing.** Consecutive `transform` events on the same lot with no branch collapse into one `intermediate` node with a `×4` badge; click expands. Typically removes 40–60% of nodes. `lib/graph/collapse.ts`, pure, memoised by `graphHash`.
3. **Read-only flags.** `nodesDraggable={false} nodesConnectable={false} elementsSelectable edgesFocusable={false}` — removes drag bookkeeping and a whole class of store updates.
4. **`onlyRenderVisibleElements`.** Documented as the large-graph optimisation; it adds per-pan overhead, so it's switched on only above 40 nodes: `onlyRenderVisibleElements={nodes.length > 40}`.
5. **Three zoom tiers (LOD).** `useStore(s => s.transform[2])` with a throttled selector: `< 0.6` → 10px dot, no text, no edge labels; `0.6–1.1` → node label only; `> 1.1` → label + knowness bar + edge labels. Text layout is what makes big React Flow graphs slow, so this is where the frames come back.
6. **No `animated` edges above 25 edges.** Each animated edge is a running CSS animation and a continuous repaint. Animation on the graph is reserved for the single edge belonging to the active step.
7. **`fitView` on scrub, not re-layout.** `fitView({ nodes: focusIds.map(id => ({ id })), duration: 150, padding: 0.2 })`. Positions never change while scrubbing; only the viewport moves.

### 5.5 Mounting

```tsx
// components/graph/LotGraph.tsx
'use client';
import dynamic from 'next/dynamic';

const LotGraphCanvas = dynamic(() => import('./LotGraphCanvas'), {
  ssr: false,
  loading: () => <GraphSkeleton />,
});
```

`dynamic(..., { ssr: false })` must be called from a **client** component — doing it in a Server Component is unsupported in Next 16 and errors. So `LotGraph.tsx` is `'use client'` and is the only thing `StatePane` imports; React Flow + elk land in their own lazy chunk that `/method` and `/` never download.

`LotGraphCanvas` imports `@xyflow/react/dist/style.css` and wraps in `<ReactFlowProvider>` so `useReactFlow()` works in `GraphControls`.

### 5.6 Accessibility

A canvas DAG is not keyboard-navigable in any honest sense, so the graph is `role="application"` with `aria-describedby` pointing at `GraphLegend`, and `<GraphTextAlternative>` renders the identical data as a `<table>` (lot · created by event · consumed by event · fraction · lifecycle) behind a "View as table" disclosure. The table is also the presenter's escape hatch if WebGL/canvas misbehaves on unfamiliar hardware.

---

## 6. Fallback mode

One interface, two implementations, one decoder. Nothing branches on mode above the client layer.

```ts
// lib/engine/client.ts
export interface EngineClient {
  readonly mode: 'live' | 'recorded';
  health(): Promise<HealthResponse>;
  analyze(req: { recipe: string }): Promise<AnalyzeResponse>;
  ask(req: { recipeKey: string; question: string }): Promise<AskResponse>;
  compare(req: { a: string; b: string }): Promise<CompareResponse>;
}
```

### The rule that makes this clean

**Fixtures are recorded responses, not hand-written objects.**

```bash
pnpm tsx scripts/record-fixtures.ts --recipes fixtures/recipes.txt --questions fixtures/questions.txt
# → fixtures/<slug>/analyze.json
#   fixtures/<slug>/ask/<questionKey>.json
#   fixtures/<slug>/compare/<pairKey>.json
#   fixtures/manifest.json   (slug, title, engine stamp, recordedAt, sha256 of each file)
```

Consequences that fall out for free:

- Both clients return bytes that came out of the same engine, so **both go through the same zod decoder**. A fixture that drifts from the contract fails the decoder — and a CI test (`fixtures.spec.ts`) decodes every fixture on every commit, so drift is caught at build time, not on stage.
- No parallel hand-maintained schema to keep in sync.
- The recorded `EngineStamp` is real, so `EngineStampPopover` tells the truth in recorded mode: "engine 0.9.3, recorded 2026-11-22".

```ts
// lib/engine/fixture-client.ts
export class FixtureEngineClient implements EngineClient {
  readonly mode = 'recorded' as const;

  async ask({ recipeKey, question }: AskReq): Promise<AskResponse> {
    const key = questionKey(question);                 // lowercase, collapse ws, strip punctuation
    const hit = await loadFixture(recipeKey, 'ask', key);
    if (hit) return decodeAsk(hit);

    // A miss returns a REAL, typed ABSTAIN — never a fabricated answer.
    return abstainNotRecorded(recipeKey, question);     // reason: QUESTION_NOT_IN_FIXTURE_SET
  }
}
```

That last line matters more than it looks: the fallback's failure mode is an honest abstention, which is on-thesis rather than embarrassing. If someone asks an unrehearsed question during Q&A, the app says it has no basis for an answer — exactly what it says when the live engine's gates refuse.

### Resolution and degradation

```ts
// lib/engine/resolve.ts
export async function resolveEngineClient(): Promise<EngineClient> {
  if (process.env.NEXT_PUBLIC_ENGINE_MODE === 'recorded') return new FixtureEngineClient();
  try {
    const h = await withTimeout(fetch('/api/health'), 1500);
    const parsed = decodeHealth(await h.json());
    if (parsed.status !== 'down' && parsed.capabilities.analyze) {
      return new HttpEngineClient({ onDegrade: degradeToRecorded });
    }
  } catch { /* fall through */ }
  return new FixtureEngineClient();
}
```

`HttpEngineClient` wraps each call in an 8 s timeout. On timeout, network error, 5xx, or `DecodeError` it calls `onDegrade(reason)`, which:

1. flips `sessionStore.mode` to `'recorded'`,
2. retries the same call once through `FixtureEngineClient`,
3. fires one `sonner` toast ("Backend unreachable — switched to recorded results"),
4. flips `ModeBadge` to RECORDED.

No pane ever sees an error for a degradable call. The presenter sees a badge change and keeps talking.

Three env knobs: `ENGINE_GATEWAY_URL` (server-only, used by the route handlers), `NEXT_PUBLIC_ENGINE_MODE = auto | live | recorded`, `NEXT_PUBLIC_FIXTURE_SLUG` (the default recipe). Rehearse with `recorded`, demo with `auto`.

---

## 7. Loading, error, empty, and ABSTAIN

### Per-pane matrix

| Pane | Loading | Empty | Error |
|---|---|---|---|
| Recipe | `SkeletonPane` with 4 ingredient + 6 step rows at real heights | "Paste a recipe, or pick a recorded one" + `FixturePicker` | Parse failure → the engine's `failure.code` + the raw text, still shown |
| Timeline / graph | Strip skeleton (grey 5×N grid), graph skeleton (3 grey nodes) | "No events extracted" + the `diagnostics` list | Layout worker failure → fall back to a pure-CSS vertical lineage list, graph degraded, nothing blank |
| Inspector | Per-tab skeleton; tab bar is live immediately | "Select a lot" with the three lot chips inline | Per-tab error, other tabs keep working |
| Query bar | `AskStatus` with stage labels | Four `QuestionChips` | Retryable error with the question preserved in the input |

Loading rules: a skeleton appears within 100 ms of a request (no spinner-flash threshold games — `analyze` always takes long enough to warrant one). Skeletons are **layout-identical** to the loaded content, so CLS stays near zero. Panes carry `aria-busy="true"` while loading and announce completion through a single `aria-live="polite"` region, so a screen-reader user isn't told about three separate panes settling.

### ABSTAIN is not an error

This is the design decision the whole app exists to make.

```tsx
interface AbstainCardProps {
  question: string;
  reasons: readonly AbstainReason[];
  claimPacket: ClaimPacket;
  evidence: readonly EvidenceRow[];   // includes found_not_applied
  onInspectAxis: (axis: CompatAxis) => void;
}
```

`AbstainCard` uses **the same `Card`, the same width, the same type scale, the same padding** as `AnswerCard`. The only difference is the `VerdictPill` and the body sections. It is not a yellow warning box, not an alert, not smaller. A viewer scanning the screen must not be able to tell from layout alone whether the engine answered or declined — only from reading the verdict.

Body, in this order:

1. **What was asked** — the normalised question and the scope (food, step, target).
2. **Why no claim is licensed** — the `AbstainReason[]`, each naming its blocking axis. Clicking one jumps to that row in `CompatMatrix`. This is the "why" the brief asks for, and it's clickable rather than prose.
3. **What was found but not applied** — the `found_not_applied` evidence rows at full detail, each showing its reported value, its tier, and `blockedBy`. "We have numbers; here they are; here is why they don't transfer to this state."
4. **What would change the answer** — generated from `blockedBy`: "a measurement on this matrix at 95–105 °C would be applicable". Derived from the engine's own axes, not invented advice.
5. **`forbidden_claims`** — rendered, not hidden. The packet's refusals are content.

`UnknownCard` is the sibling case: the value is genuinely not determined. Same chrome again; body is the `unknown_reasons` list with human labels, plus the `KnownessBar` for the relevant block so the viewer sees how much of `S_t` is unknown at that step.

### Error taxonomy

```ts
export type GatewayError =
  | { kind: 'offline' }
  | { kind: 'timeout';  ms: number }
  | { kind: 'http';     status: number; body: string }
  | { kind: 'decode';   issues: readonly { path: string; message: string }[] }  // ← contract drift
  | { kind: 'engine';   code: string; message: string };                        // engine said no, legitimately
```

- `offline` / `timeout` / `http` → degrade to recorded (§6), one toast, carry on.
- `engine` → **not** a UI error. The engine declining or failing a parse is a result; render it in the pane with its code.
- `decode` → the one loud failure. `ContractDriftDialog` opens and names the failing JSON path. In dev it shows the zod issues; in production it says "the response did not match the frozen contract (`culinarystate.analyze.v1`)" and offers recorded mode. This is the mechanism that stops the UI from quietly mis-rendering a changed engine, and it's why every response carries `contract`.

`app/lab/error.tsx` is the last resort: the three-pane frame survives, and the body offers "reload in recorded mode".

---

## 8. Performance budget

### Budget

| Metric | Budget | Measured by |
|---|---|---|
| `/lab` first-load JS (excl. graph chunk) | ≤ 220 KB gzip | `@next/bundle-analyzer`, CI gate |
| Graph lazy chunk (`@xyflow/react` + `elkjs`) | ≤ 190 KB gzip | same, separate gate |
| `/method` client JS | **0 KB** | CI asserts no `'use client'` in its import graph |
| LCP, recorded mode | ≤ 1.8 s | Lighthouse CI, mobile throttle |
| LCP, live mode | ≤ 2.5 s | — |
| CLS | < 0.05 | layout-identical skeletons |
| INP, question submit | ≤ 200 ms to first paint of `AskStatus` | Playwright + `PerformanceObserver` |
| Scrub frame time, p95 | ≤ 16.7 ms on the 40-event fixture | `perf.spec.ts`, **fails CI above 25 ms** |
| elk layout, 60 events | ≤ 120 ms, in a worker, cached | worker-side `performance.now()` log |
| `diffState` × N, once per analyze | ≤ 20 ms total | unit benchmark |
| Lighthouse Performance / Accessibility | ≥ 90 / ≥ 95 | Lighthouse CI on `/lab` and `/method` |

### The graph is the risk — what to watch

1. **Re-render count per scrub must be O(changed nodes), not O(all nodes).** Verify with the React DevTools profiler on the 40-event fixture: a single step advance should re-render the active-step nodes and the `DeltaLedger`, nothing else. If every node re-renders, the cause is almost always (a) a non-memoised `nodeTypes`/`edgeTypes` object, (b) a new `nodes` array identity per render, or (c) a non-memoised callback prop on `<ReactFlow>`. All three are documented React Flow footguns; all three are addressed by module-scope type maps, cached layout, and `useCallback` on every handler.
2. **Node count.** Above 40 nodes, auto-enable `onlyRenderVisibleElements` and keep focus mode on. Add a dev-only `GraphStats` overlay showing node/edge count, visible count, and last layout ms.
3. **Animated edges.** Hard cap: at most one animated edge (the active step's). An `expect(animatedEdgeCount).toBeLessThanOrEqual(1)` assertion in the perf test, because this regresses silently.
4. **Layout thrash.** The layout must be computed once per `graphHash`, never per scrub. A dev assertion counts worker messages per session; more than one per distinct graph is a bug.
5. **`motion` during drag.** `layout` animation off while `isScrubbing` — 30 simultaneous layout animations per tick is the worst case in the app.
6. **`StateDeltaStrip` rect count.** 5 × N rects; at N > 80 switch to one `<path>` per block row instead of per-step rects. Not needed for a 40-step recipe, but the threshold is written down.
7. **Recharts is scoped to one component.** It is imported only inside `RetentionCurve`, which is itself lazily loaded inside the Evidence tab. If it shows up in the `/lab` initial chunk, something imported it at module scope — the bundle gate catches it.

### Measurement setup

`next build --turbopack` + `@next/bundle-analyzer`; Lighthouse CI on `/lab?fixture=…&t=12` and `/method`; a Playwright `perf.spec.ts` that drags the scrubber across all 40 steps while recording a trace and asserts p95 frame time; `axe-core` via `@axe-core/playwright` on all four routes with zero serious/critical violations as a merge gate.

---

## 9. Build order

The brief fixes this; here it is as a sequence with a shippable checkpoint at each stage.

1. **Contracts + fixtures.** `contracts.ts`, `decode.ts`, `cell.ts`, `fold`, `diffState` + unit tests. Record 3 recipes × 6 questions. No UI at all. *Checkpoint: `fixtures.spec.ts` green.*
2. **`/lab` frame.** `LabWorkbench`, `LabPanes`, skeletons, `FixturePicker`, `sessionStore`, URL mirror. *Checkpoint: three resizable panes, scrubbing changes a number.*
3. **Pane A + Pane C State tab.** `CellValue`, `BasisTag`, `UnknownTag`, `StateBlockAccordion`. *Checkpoint: full `S_t` renders, unknowns look like unknowns.*
4. **Delta visualisation.** `StateDeltaStrip`, `DeltaLedger`, `DeltaCell`, `DeltaInterval`. *Checkpoint: scrub and the change is obvious without reading.*
5. **Query bar + ABSTAIN.** `QueryBar`, `AnswerCard`, `AbstainCard`, `UnknownCard`, Evidence/Compatibility/Claim/Provenance tabs. *Checkpoint: the demo's core argument is demonstrable end to end.*
6. **Graph.** `build.ts`, worker layout, five node types, five edge types, focus mode, collapsing, LOD. *Checkpoint: 60-event fixture readable and at frame budget.*
7. **Live mode.** `HttpEngineClient`, route handlers, degradation, `ModeBadge`. *Checkpoint: pull the gateway's plug mid-demo and nothing breaks.*
8. **`/compare`.** Reuses everything from 3–5.
9. **`/method`.** MDX, invariant tables, `OPEN_INVARIANTS` verbatim.
10. **`/` landing.** Last. By now you know what the screenshots are.

Stages 1–5 are the whole argument. If the schedule slips, 8–10 are the cut line; the graph (6) is not, because it's what makes the lineage legible, and 7 is not, because the fallback is the insurance.

---

## 10. What I checked

- **Next.js 16.4.5 docs** via Context7 (`/vercel/next.js/v16.4.5`): `migrating-to-cache-components.mdx` (Route Handlers prerender unless they touch runtime data; `'use cache'` can't sit on the `GET` export, so it goes on a helper), `proxy.mdx` (`middleware.ts` → `proxy.ts`, with a codemod; the docs actively discourage relying on it — this app needs neither), `authentication-with-cache-components.mdx` and `use-cache-private.mdx` (`cacheComponents: true` in `next.config.ts`).
- **Next.js App Router practice**, web search: Server Components by default with client code pushed to the leaves; `next/dynamic` with `ssr: false` is unsupported from a Server Component (so `LotGraph` is `'use client'`); don't fetch your own Route Handlers from Server Components — put shared logic in `lib/`; async `cookies()`/`headers()` and Promise-based `params`/`searchParams` in 16. Sources: [awesome-copilot Next.js instructions](https://awesome-copilot.github.com/instruction/nextjs/), [nextjs.instructions.md](https://git.cynarski.dev/Awesome/awesome-copilot/src/branch/main/instructions/nextjs.instructions.md), [Next.js 16 App Router guide for 2026](https://dev.to/getcraftly/nextjs-16-app-router-the-complete-guide-for-2026-2hi3), [RSC architecture mistakes in production](https://www.buildmvpfast.com/blog/rsc-architecture-mistakes-production-coupling-waterfalls-2026), [nextjs-app-router skill](https://skills.sh/giuseppe-trisciuoglio/developer-kit/nextjs-app-router).
- **shadcn CLI v4 changelog** (Mar 2026), fetched directly: [ui.shadcn.com/docs/changelog/2026-03-cli-v4](https://ui.shadcn.com/docs/changelog/2026-03-cli-v4) — `init --base` (Radix or Base UI), `registry:base` + `registry:font` replacing deprecated `registry:build`/`registry:mcp`, new `--dry-run` / `--diff` / `--view` inspection flags, `init --preset` and `init --template`, plus `info` and `docs` commands. Also [ui.shadcn.com/docs/tailwind-v4](https://ui.shadcn.com/docs/tailwind-v4) (Tailwind v4 required, CSS-only theming, no `tailwind.config`) and the [changelog index](https://ui.shadcn.com/docs/changelog). `Resizable` and `Tabs` confirmed present, which is what the three-pane layout and Inspector need.
- **React Flow docs** via Context7 (`/websites/reactflow_dev`): [`onlyRenderVisibleElements`](https://reactflow.dev/api-reference/react-flow) (helps on large graphs, adds overhead — hence the conditional), [performance guide](https://reactflow.dev/learn/advanced-use/performance) (`React.memo` custom nodes, `useCallback` handlers, `useMemo` object props), [v10 migration notes](https://reactflow.dev/learn/troubleshooting/migrate-to-v10) (never build `nodeTypes`/`edgeTypes` inline), [dagre](https://reactflow.dev/examples/layout/dagre) and [elkjs](https://reactflow.dev/examples/layout/elkjs) layout examples, [`fitView({ nodes: [{ id }], duration: 150 })`](https://reactflow.dev/learn/tutorials/slide-shows-with-react-flow), and [SSR/SSG configuration](https://reactflow.dev/learn/advanced-use/ssr-ssg-configuration).
- **npm registry**, current versions as of today: `next 16.4.6`, `@xyflow/react 12.12.1`, `motion 14.14.0`, `zustand 5.1.0`, `elkjs 0.12.1`, `@dagrejs/dagre 3.1.3`, `recharts 3.10.1`, `zod 4.6.7`.
- **The engine itself**, read in `/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate`: `src/culinarystate/composition/state.py:18-23`, `src/culinarystate/composition/state_full.py:1-13` and `:150-180`, `src/culinarystate/retrieval/compatibility.py:1-60`, `src/culinarystate/composition/claim_packet.py:83-95`, `docs/EVENT_IR_CONTRACT.md`, `CLAUDE.md`.

---

### Two notes for the parent agent

1. **Nothing here asks the engine to change.** Every interface mirrors an existing emitted shape; where the UI needs a different arrangement (grouping `Y`'s flat `${target}_*` keys, rolling up the `P` block, classifying unknown vs n/a), that work is a UI-side adapter or a generated file, and I've named the module each time.
2. This document is the deliverable itself — ready to publish as a doc or artifact for the developer if you want a shareable link rather than terminal text.
