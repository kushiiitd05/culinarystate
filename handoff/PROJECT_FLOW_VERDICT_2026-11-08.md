# CulinaryState: how the whole system works, what is done, what is left (verdict, 2026-11-08)

Written by the coding agent (S172) for Kush and Parv, from SSOT v15 (§4, §6, §39, §106, §112–113, §141, §245.12),
the v16 change set (draft, not applied) and the 36-step plan v2. Live task list: `FINISH_PLAN_2026-11-07.md`.

## 1. The flow: one recipe, end to end

```
recipe text ─► [A] extraction (Rung A, deterministic) ─► entities, quantities, events, process ids
            ─► [A'] NER (DeBERTa-CRF) ─────────────────► ingredient mentions (2nd opinion, fills unlinked lots)
            ─► [B] event replay (state tracker S_t)  ──► what exists, what was done to it, in what order
            ─► [C] condition binding ─────────────────► per event: T, time, medium, lid, size, water ratio, start
            ─► [D] physics drivers θ(t) ──────────────► time-at-temperature, surface/core T estimate, thermal dose
            ─► [E] formula router (23a gates G0–G9) ───► per event × target: DIRECT / INTERPOLATE / SIMULATE /
                                                          QUALITATIVE / ASK / UNKNOWN, with reasons
            ─► [F] process-effect model T(S_t, P, θ) ──► ΔC chemical, ΔP physical (+ uncertainty), §112 heads
            ─► S_{t+1}  (repeat per event)
question ──► [G] query router (§39) ─► [H] evidence packets + decision layer ─► cited answer / ASK / ABSTAIN
                                     (state from [B], routes from [E], numbers only from [F] or measured EVD)
learning ──► [I] transition models on EVD + θ features (Steps 29–33) ─► learns the generic behaviour
            ("heating in water leaches and degrades vitamin C; acid speeds chlorophyll loss")
            [J] representations (Step 35; §113 explicit + latent) ─► ingredient / recipe / state vectors
```

**The formula router [E], in its fixed order (support first, semantics never decides):** G0 is there a
measured row for this exact food × process × target → DIRECT. If not: is the case bracketed by measured rows →
INTERPOLATE. If not: is there a reviewed mechanism whose activation conditions are met (G1–G4), a formula (FORM)
for it, and parameters (PARAM) whose calibration domain contains these conditions (G5–G8, Step 25) → SIMULATE.
If not: the mechanism's direction only → QUALITATIVE. If an input is missing and asking would change the
answer → ASK. Otherwise → UNKNOWN. Text or embedding similarity is used only to *find* candidate rows and
mechanisms; it never chooses a route or a number (SSOT §39, §141 frozen output contract).

## 2. Status of every block (honest)

| Block | What exists | Run on the 600k corpus? | Left (heavy H / light L) |
|---|---|---|---|
| A Rung A extraction | done, deterministic, invented 0 | **yes** (14.6 M events) | L: gold comparison (needs P1b) |
| A' NER | DeBERTa-CRF trained on TASTEset (DEV F1 0.940) + RecipeDB3; checkpoints on vinayak | **no**: trained and benchmarked only, never run over the corpus | **H (GPU):** run on ~4.3 M ingredient lines → MENTION ledger; agreement with Rung A |
| B replay / state tracker | done | **yes** | L: gold check (D3) |
| C condition binding | missing: all 14.6 M events lack all 8 simulator inputs | no | **H (CPU):** bind stated T/time/medium/lid/size/water from Rung A quantities and cues |
| D physics drivers | sim_core + Choi–Okos structure, no values | no | **H (CPU):** text-only layer + cited-default scenario layer (D-077) |
| E formula router | 23a engine + demo mode | **yes** (36.4 M route checks, 0.75 % DIRECT) | L: re-run once C/D/F exist (SIMULATE becomes reachable) |
| F process-effect model | sim_aa_1 structure; AA pilot fit tool | no | **H (human):** M3 verification; then fit + held-out check (light compute) |
| G/H answering (D4/D5) | router, front door, pipeline, template answers, ladder code | demo on real ledgers | L: web demo (M6), rung code; **H (human):** benchmark review |
| I generic behaviour (29–33) | scaffolds, one exploratory run | no | **H (CPU/GPU):** bootstrap on EVD + θ features; bake-off |
| J representations (35) | ladder code, synthetic-tested | no | **H (GPU):** state/recipe embeddings from B + D; needs the Step 35 signature |

So, **are we lacking?** Yes, in the middle of the chain: extraction and replay are done at full scale, and so is
the router. But the inputs the physics needs (C), the physics itself (D) and any verified parameter (F) do not
exist yet. Every UNKNOWN in the 36 M router checks says exactly this. NER was trained, not deployed.

## 3. The physical dataset (D-077): two layers, never mixed

- **Layer 1, TEXT_STATED:** only what the recipe says, plus physical definitions (water boils at 100 °C at
  1 atm). Each value has its span. Missing stays UNKNOWN.
- **Layer 2, SCENARIO (cited defaults):** a registry of literature-typical values with source and range (e.g.
  deep-fry oil 160–190 °C; simmer 85–95 °C; size class from "diced/sliced/whole"). Each event is run at the low,
  mid and high values, labelled ASSUMED_DEFAULT, MODEL_DERIVED, NON_CITABLE. Under §141 this layer produces
  driver trajectories and `physically_possible` transitions with direction. It produces **no** nutrient number
  until the M3 fit is frozen and checked on held-out data (Step 27).
- Uses: features for Steps 30–33 (learning the generic behaviour) and input to state representations (Step 35).
  This layer is a scenario dataset, not the Step 28 E7 prior: E7 waits for Step 27 (R-13).

## 4. Compute plan (all tracked)

| Resource | Job |
|---|---|
| vinayak A100 ×2 | NER inference on non-BBC ingredient lines; Ollama LLM rungs for H1/H3; embeddings for Step 35 |
| vinayak 128 CPU cores | condition binding + physics layers on non-BBC recipes (sharded fork pool); router re-run |
| manjot A100 (GPU 1 only; GPU 0 is another user's job) + CPUs | second NER shard / embedding shard; overflow CPU shards |
| Mac (8 GB) | BBC Good Food recipes (D-003 kept: BBC text stays off servers), orchestration, commits, tests |

Every run writes a row to `registry/compute_runs_v1.csv`: run id, host, tree, git commit, code hashes, input
hash, command, start/end time, output path and hash, status. Server copies are synced from tracked files only.

## 5. Order of work to 25 Nov

1. **Now (agent, server):** condition binding (C) → Layer 1 → Layer 2 on all non-BBC recipes; NER inference;
   BBC on the Mac. In parallel on the Mac: M6 web demo, H1/H3 rung code.
2. **When humans return M3 (15 Nov):** fit, freeze, held-out check → router re-run shows SIMULATE for vitamin C.
3. **When humans return M2 (13 Nov) and M5 (16 Nov):** 07.A-R1 score; frozen benchmark → H1/H3 runs (19 Nov).
4. **Steps 29–33 bootstrap** on EVD + θ features (diagnostic, E3-unverified, labelled); **Step 35** representations
   (after its signature).
5. **22–24 Nov:** report and slides from the real results only.
