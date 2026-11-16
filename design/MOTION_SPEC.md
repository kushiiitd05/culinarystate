# CulinaryState Explorer — Motion Specification

Next.js + Tailwind + Motion (Framer Motion) + React Flow. Audience: examiners, 25–26 Nov 2026, live,
laptop, possibly a projector. Nothing below is decorative except §9.

Grounded in `docs/EVENT_IR_CONTRACT.md`: `ValueClaim.status`, compatibility
`{MATCH 1.0, NEAR 0.5, UNKNOWN 0.25, MISMATCH 0.0}`, `UNKNOWN_IN_SOURCE`/`UNKNOWN_IN_QUERY`,
`ABSTAIN`, lifecycle `DISCARD`, allocations with `basis`/`fraction`, and the project law
**UNKNOWN ≠ zero**. The motion rules are the UI expression of that law.

## 1. Principles

**P1 — Motion is the delta channel; stillness is a claim.** If a pixel moves, something changed.
Unchanged rows have zero animated properties — no crossfade, no reflow, no opacity dip.
*Why:* the value proposition is "see what changed between `S_t` and `S_t+1` at a glance". If idle rows
animate, motion stops being evidence.

**P2 — Cause before effect, exactly once.** Per step commit: typed event marker (0–160 ms) → state
delta rows (from 200 ms) → evidence (only on query). Never simultaneous, never reversed.
*Why:* the claim is that a typed event explains the state change. Animation order **is** the argument.

**P3 — Absence does not move.** `UNKNOWN`, `NO_RECOGNIZED_MARKER`, `UNKNOWN_IN_SOURCE/QUERY`,
`ABSTAIN` fade **in place**, never translate, never flash, and are the slowest transitions.
*Why:* translation reads as arrival of information. These are the absence of information, and per
project law neither zero nor error.

**P4 — Every animated signal has a static twin.** Each transition ends in a persistent marker
(status rail, hatch, delta chip, `was:` text). No fact exists only during its animation.

**P5 — Interruptible, reversible, never queued.** One in-flight transition per element. A new commit
cancels, never enqueues. Backward scrub animates backward.

**P6 — Budget beats flourish.** Step transition ≤ 1000 ms; evidence table ≤ 600 ms; only `opacity`
and `transform` animate. No `height`/`width`/`top`/`filter` anywhere.

## 2. Tokens

```css
:root {
  --motion-instant: 0ms;            --motion-micro: 120ms;
  --motion-badge: 140ms;            --motion-value-exit: 120ms;
  --motion-value-enter: 160ms;      --motion-state-change: 240ms;
  --motion-state-overlap: -80ms;    --motion-unknown: 380ms;
  --motion-resolve: 240ms;          --motion-event-marker: 160ms;
  --motion-event-gap: 40ms;         --motion-emphasis-hold: 600ms;
  --motion-emphasis-decay: 400ms;   --motion-evidence-row: 180ms;
  --motion-graph-node: 220ms;       --motion-graph-edge-draw: 300ms;
  --motion-graph-dim: 200ms;        --motion-viewport-recenter: 320ms;
  --motion-abstain-pause: 200ms;    --motion-abstain-reveal: 240ms;
  --motion-abstain-rule: 320ms;     --motion-flip-reorder: 260ms;
  --motion-scrub-swap: 80ms;

  --ease-enter:      cubic-bezier(0.20, 0, 0.20, 1);
  --ease-exit:       cubic-bezier(0.40, 0, 1.00, 1);
  --ease-measure:    cubic-bezier(0.33, 0, 0.67, 1);
  --ease-deliberate: cubic-bezier(0.15, 0, 0.25, 1);

  --stagger-delta: 30ms;            --stagger-evidence: 45ms;
  --stagger-badge-offset: 90ms;     --stagger-abstain-reason: 60ms;
  --stagger-graph-children: 60ms;   --stagger-cap-index: 7;

  --scrub-gate: 180ms;              --scrub-settle: 220ms;
  --debounce-viewport: 150ms;
}
```

Four easings only. Reject any cubic-bezier whose control-point y leaves `[0,1]` — overshoot implies
physical momentum in a system where nothing is physical. **`type: "spring"` is banned app-wide.**
Mirror tokens in `lib/motion/tokens.ts` as seconds and derive the CSS properties from the same object
so Motion and Tailwind cannot drift.

## 3. State-delta animation (centrepiece)

### 3.0 Layout preconditions — these do more work than the animation

- Each field of `S_t` is a fixed-height row (40 px): `[2px rail][label 180px][value 1fr][chip auto]`.
- **Row set = union of fields in t and t+1**, ordered **G → C → Q → Y → P**, then registry order. A
  field existing only in t+1 occupies a reserved empty row at t.
- **No row ever changes position or height.** Every delta is in-place in the value cell, which is
  `overflow:hidden` with two stacked absolutely-positioned spans, so a crossfade costs no layout.
- `font-variant-numeric: tabular-nums` on all value cells.
- Unchanged rows: `transition: none`, stable React key.

### 3.1 Timeline of one commit

| t (ms) | What |
|---|---|
| 0–160 | Event marker only: `MERGE(vinegar, current sauce)` + span `"Stir in the vinegar."` opacity 0→1, translateY 4→0. Nothing else moves. |
| 160–200 | Deliberate silence. |
| 200 + i·30 | Delta rows, `i` = index among **changed** rows in schema order, capped at i=7. |
| ≤ 1000 | All emphasis decay complete. Hard ceiling. |

Stagger is by **schema order, never severity** — examiners learn row positions over 20 steps.

### 3.2 ADDED
Rail `scaleY 0→1` from top, `--c-added`, 160 ms; value `opacity 0→1`, `translateY 4→0` simultaneously.
Chip `+1 acid_source` fades in at 160–300 ms. **Row tint is a single container-level animation shared
by all changed rows** (hold 200–800, decay 800–1200) — per-row staggering applies only to rail, value
and chip, otherwise the last-staggered row breaks the 1000 ms ceiling. Persistent: rail at 1px/40%,
chip stays.

### 3.3 CHANGED
Cross-slide inside the clipped cell: outgoing `translateY 0→−6px`, `opacity 1→0`, 0–120 ms
`--ease-exit`; incoming `translateY +6px→0`, `opacity 0→1`, 80–240 ms `--ease-enter`. 40 ms overlap —
both values briefly legible, which is the point.
**Direction encodes time direction:** forward → incoming from below; backward scrub → from above.
Pass `custom={direction}`.
**List-valued fields** (`phase`, `history`): animate **only the appended token**; existing tokens get
zero animation; never animate container width.
**Numerics:** count-up 240 ms `--ease-measure` **only** for counts of discrete things
(`member_count`). Never for measured magnitudes, never for intervals — interpolating `(low, high)`
displays values the system never claimed. Intervals crossfade as text.

### 3.4 REMOVED / `DISCARD`
Strike-through `scaleX 0→1` from left, 140 ms; value `opacity 1→0.38`; rail `--c-removed`; chip
`REMOVED`. **The row keeps its height and struck text for the whole time step t+1 is selected** —
removal is information. It disappears on the next commit frame with **no exit animation**; collapsing
height mid-scrub is the largest source of thrash.

### 3.5 BECAME_UNKNOWN — the most important case
Must not read as deletion, must not read as a value. **380 ms — deliberately the slowest delta: the
loss of knowledge is the slowest thing that happens here.**

1. 0–120 ms: outgoing value crossfades to a muted twin (two stacked spans, same text, `--c-unknown`).
   **Never `filter: saturate()`.**
2. 120–220 ms: muted value `opacity → 0`. No translate.
3. 220–380 ms: token `UNKNOWN` (or the exact status string) `opacity 0→0.7`. **Zero translate, zero
   scale.** Max 0.7 so it never competes with known values.
4. Rail: static 45° hatch (inline SVG `<pattern>`, unanimated), fading in 160 ms from 120 ms.
5. Row border: 1px dashed top+bottom, persists while selected.
6. Chip: `NOW UNKNOWN` + `was: lipid` — **the previous value stays visible as text forever.**
7. Forbidden: flash, red, shake, warning glyph, tint pulse, any `scale`.

### 3.6 RESOLVED
Hatch rail crossfades to solid `--c-added` 0–160 ms; `UNKNOWN` token `0.7→0` and new value
`opacity 0→1`, `translateY 4→0` at 80–240 ms. Chip `RESOLVED` + source class. The only good-news
moment in the app, and it still gets no glow.

### 3.7 UNCHANGED
Zero animated properties. A stray `transition: all` in the Tailwind config silently destroys P1 —
audit for it.

## 4. Lot graph (React Flow)

### 4.1 Layout does not animate
Positions computed **once per recipe** for the terminal event history, deterministic layered DAG
(`rank = step_index` on x, lot lanes on y), memoized by `(source_text_id, raw_sha256)`. Stepping and
scrubbing never move a node.
*Rationale:* **in a lineage graph, position is semantics.** A node that moves reads as a change in
lineage; a re-layout on MERGE would make every ancestor appear to change. Static layout also makes
30+ nodes survive rapid scrubbing for free.
Nodes not yet existing at step t are **ghosts**: `opacity 0.12`, 1px dashed, label hidden.

### 4.2 Per-event choreography (max 3 nodes change per step)
**Node appears:** ghost → live, `opacity 0.12→1`, 220 ms. `scale 0.96→1` **only** for nodes directly
produced by the current event, and only if ≤2.
**MERGE(a,b→c):** both parent edges draw `stroke-dashoffset L→0`, 300 ms, **simultaneously** — a merge
is one event; sequential draws would imply an ordering the IR does not claim. Dash animation is then
removed from the DOM, not paused. Child activates 300–520 ms. Parents → consumed: fill alpha 1→0.45,
border solid→dashed, **label opacity never below 0.7** (you must still be able to read "vinegar").
**SPLIT:** child edges draw outward simultaneously; children fade in from 240 ms, stagger 60 ms only
if ≤2 children. `basis` + `fraction` labels fade in 400–540 ms. **No count-up** — a fraction is a
claim with a basis, not a measurement sweeping upward.
**DISCARD:** static hatch overlay 180 ms, `opacity → 0.4`. **The node is never removed** — lineage
must stay inspectable, and with static layout it costs nothing.

### 4.3 Keeping 30+ nodes legible
Static layout · ≤3 nodes change per step · **focus scope as one container-level animation, not
thirty** (1-hop neighbours stay at 1, rest to 0.55 over 200 ms, driven by one class on the pane) ·
**no persistent `animated: true` edges** (permanent motion, zero information, keeps the compositor
busy for the whole viva) · auto-recenter is the one exception to "don't move things":
`setCenter(..., {duration: 320})`, debounced 150 ms, **skipped in scrub mode and reduced motion**,
with a static caption `recentred on step 7` so a viewport move is never read as a graph change ·
`will-change` never on graph nodes.

## 5. Evidence reveal

### 5.1 Ordering
Rows reveal in **fixed order — query-clause then schema order, never sorted by outcome.** Sorting by
result leaks the verdict in the first frame and forces a reflow when results arrive.

### 5.2 Base reveal
Container 0–120 ms; row *i* at 120 + i·45 ms (`opacity 0→1`, `translateY 6→0`, 180 ms), capped at
i=7; **badge fades in at row t0 + 90 ms**; entire table readable ≤ 600 ms.
The 90 ms badge offset is deliberate: the examiner reads *field · source value · query value* before
being told the verdict. That ordering is P2 at evidence scale.

### 5.3 Outcomes differ only in ways that mean something
- **MATCH** — badge fade, 140 ms. No rail, no tint, no checkmark draw. *Agreement is quiet.* Emphasis
  here would make MATCH the loudest row, and it is the least interesting row.
- **NEAR** — badge fade plus its **one** animation: value marker eases from band centre to position,
  200 ms `--ease-measure`. NEAR is a magnitude claim; its single motion communicates magnitude.
- **MISMATCH** — badge fade; 2px left rail `scaleY 0→1` top→bottom 180 ms (readable peripherally);
  conflicting cells get `--c-mismatch / 8%` tint, held 200 ms, decayed 400 ms. Rail persists.
  **No shake, no flash, no red fill.** A mismatch needs *locating*, not an alarm.
- **UNKNOWN_IN_SOURCE / UNKNOWN_IN_QUERY** — **same reveal timing as every other row: no delay, no
  de-emphasis, no skipping.** Static hatch (45° = source, 135° = query) fades in 160 ms; content
  **fades only, never translates**. Distinguishable with motion and colour both removed: explicit text
  token + hatch angle. Badge reads the literal status string, never a paraphrase like "n/a".

### 5.4 Group-by-outcome (opt-in)
FLIP reorder, Motion `layout`, 260 ms. **The only place `layout` appears in the app** — permitted
because the user asked for the reordering, so the movement is the answer to their action.

### 5.5 ABSTAIN — deliberate, not broken
Total **760 ms**, intentionally longer than a decided verdict (240 ms): *considered, not failed.*

| t (ms) | What |
|---|---|
| 0–200 | **Nothing happens.** The silence is the dignity — it reads as the system finishing its check. |
| 200–520 | 1px top border draws left→right, `scaleX 0→1`, `--ease-deliberate`. The single deliberate gesture in the app. |
| 240–480 | Verdict content fades in, no translate. Height pre-reserved. |
| 400 + i·60 | Reason list staggers in: `2 of 5 rows UNKNOWN_IN_SOURCE`, `mass balance UNKNOWN — terms missing, not zero`. |
| 200–400 | Blocking rows' hatch rails `0.6→1`. No other row changes — the verdict is visually the **sum** of the UNKNOWNs it points at. |

Hard rules: `--c-unknown`/neutral slate, **never amber, never red**; no triangle, no `!`; same hatch
motif as UNKNOWN cells; `role="status"` + `aria-live="polite"`, **never `role="alert"`** — it must not
use the error channel in the accessibility tree either. Copy is declarative and complete:
`ABSTAIN — answer withheld. 2 of 5 evidence rows UNKNOWN_IN_SOURCE.` An abstention without a reason
looks like a crash no matter how it animates.

## 6. Step scrubbing

1. **No queueing by construction.** No `AnimatePresence mode="wait"` anywhere (it queues by
   definition). Value cells use stacked spans driven by state, not presence. `initial={false}` so
   loading at step 7 doesn't animate 7 steps of history.
2. **Velocity gate → SCRUB MODE.** Two commits within 180 ms: value changes become opacity-only swaps
   (80 ms), emphasis suppressed, markers snap, edge draws / `setCenter` / focus dimming skipped.
   220 ms after the last commit, exit and **play the full §3 animation once for the step landed on** —
   the landing is what the examiner is reading; intermediate frames are not.
3. **Debounce the expensive, never the cheap.** Delta computation is O(fields) — run it synchronously
   every commit. Debounce only `setCenter` and focus scope. The evidence panel does **not** re-query
   during scrub: keep the last result with a static `stale — step 7` rail, never a spinner.
4. **The scrubber thumb is never animated from state** — it follows the pointer at 0 ms.
5. **Direction carried explicitly**: `direction = sign(t_new − t_old)` as Motion `custom`.
6. ≤8 ms main-thread work per commit. `will-change: opacity` on the ~12 value cells only.
7. **Acceptance:** hold ArrowRight 5 s then release → settled within 1 s, no backlog · scrub 1→14→1
   in 2 s → CLS 0, no node moves, no spinner · commit ≤8 ms p95 with a 32-node graph.

## 7. Reduced motion — substitution, not removal

`<MotionConfig reducedMotion="user">` + `useReducedMotion()` + `data-reduced-motion="true"` on
`<html>`. Durations collapse to 0; **every persistent marker is upgraded, and anything legible only
during motion becomes text.**

| Surface | Replacement |
|---|---|
| **State delta** | Instant swaps. Rail permanent 2px at 100%. Chip mandatory and explicit: `ADDED`, `CHANGED (was: lipid)`, `REMOVED`, `NOW UNKNOWN (was: PRESENT)`, `RESOLVED`. **The `was:` value becomes visible text** — the crossfade's job was showing the old value, so the old value is printed. |
| **Stagger order** | The Delta panel (open by default here): ordered list `acid_source +1`, `member_count +1`, `process_family → mechanical_mix`. The order the stagger conveyed becomes list order. |
| **BECAME_UNKNOWN** | Static hatch rail + dashed border + `NOW UNKNOWN` chip immediately; row also listed under a `became UNKNOWN` heading, so "what did we lose" stays answerable at a glance. |
| **Lot graph** | Pure static encoding: pending 1px dashed @40%, live solid, consumed 45° hatch @45%, discarded strike+hatch. Current event's edges 2px full contrast, others 1px @60% — **the edge draw becomes edge weight.** |
| **Viewport recenter** | `duration: 0` jump + the `recentred on step 7` caption held 2 s — the caption carries what the pan carried: *you moved, the graph didn't.* |
| **Evidence** | All rows + badges at once, same order. NEAR marker at final position, band labelled numerically. MISMATCH tint becomes **permanent** rather than decaying. |
| **ABSTAIN** | Renders immediately, fully expanded, reasons open, blocking rows tagged `BLOCKING`. The deliberateness 760 ms conveyed is carried by the wording. |
| **Step direction** | Static glyph: `◀ step 7 of 14`, plus Delta panel heading `step 6 → 7`. |
| **Hero decoration** | Off. **No fallback — it carried no information, which is the test of whether it was allowed to exist.** |

## 8. What NOT to animate

1. **Measured magnitudes and intervals.** Never interpolate `(low, high)` — the sweep displays numbers
   the system never claimed. Count-up only for counts of discrete things.
2. **Anything representing UNKNOWN as a quantity.** No bar growing from zero for an UNKNOWN or an
   abstention score. `UNKNOWN ≠ zero` is a project law; a bar animating up from 0 asserts exactly what
   the law forbids.
3. **Graph layout and node positions.** Position is lineage. Movement = a lineage claim you didn't make.
4. **Row order** (except the explicit user-triggered group-by).
5. **Container height or width.** Pre-reserve. Main CLS risk during a live demo.
6. **Loading affordances for memoized work.** No spinner under 400 ms — it invents latency the system
   doesn't have.
7. **Labels, units, field names, step-counter digits.** Only *values* change; animating chrome makes
   chrome look like data.
8. **ABSTAIN / UNKNOWN / MISMATCH as error affordances.** No shake, flash, red, bounce, warning icon,
   `role="alert"`. All three are results the system is entitled to produce.
9. **Hover on data cells** beyond 120 ms opacity/underline.
10. **Persistent marching-ants edges.**
11. **Route transitions with displacement.** Content-only crossfade ≤120 ms.
12. **The scrubber thumb**, or anything tracking the pointer.

## 9. The one permitted decoration

Landing/hero only: two static layered SVG lineage-graph plates at 3–6% alpha, cross-fading on a 24 s
loop (`opacity` only), `IntersectionObserver`-paused off-screen, unmounted once the examiner enters a
working view, off under reduced motion. **If a second decoration is proposed, this one is what it has
to replace.**

## 10. Implementation notes

`lib/motion/tokens.ts` — single source for `DUR`, `EASE`, `STAGGER`; generate the CSS properties from
it. `lib/motion/variants.ts` — direction-aware variants via `custom`. `useStepTransition(t)` owns the
velocity gate and returns `{direction, scrubbing, deltas}`.

**Audit the Tailwind config for `transition-all`** — one stray global transition silently violates P1
and is the most likely way this spec fails in practice.

**Pre-demo checklist:** (a) unchanged rows have zero animated properties · (b) CLS = 0 across a
1→14→1 scrub · (c) no `height` in any transition · (d) exactly four easings · (e) no `type: "spring"`
· (f) ABSTAIN is `role="status"` · (g) reduced-motion run shows every `was:` value as text ·
(h) 32-node graph commit ≤8 ms p95.
