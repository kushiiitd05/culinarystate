# Process coverage for the physical dataset and the formula router (S174, D-077 extension)

Kush, S174: "we not only have the heating but several other processes as well, all need to be taken care of and
considered for the formula router". Layers 1–2 covered only the heat families (WET, DRY, FAT, HEAT_GENERAL).
Each other family gets its transport or mechanism class, a formula family, the inputs it needs, and the same two
layers: TEXT_STATED, then SCENARIO with ranges from cited defaults. Under §141, no compound-level number appears
until a calibrated model exists.

| Process family (PROC) | What changes in the food | Formula family (router SIMULATE candidate) | Inputs to bind | Build order |
|---|---|---|---|---|
| WET/DRY/FAT/HEAT_GENERAL (heat) | temperature field, thermal dose; drives degradation and texture | transient conduction (slab series), equivalent-time dose; Arrhenius kinetics (M3) | T, t, medium, h, size, T0 | DONE (L1, L2) |
| COOLING: cool, chill, freeze, defrost | temperature falls; ice forms; drip loss on thaw | same conduction series with a cold bath; Plank freezing time; thaw as reverse | target T (fridge/freezer), time, size, h(air) | 1 |
| SEPARATION: drain, strain, rinse, soak-discard | water phase removed, so leached solutes leave the food system | leaching compartment hand-off (sim_aa_1 A_w removed); rinse as a diffusion pulse | which phase is discarded, time | 2 |
| FERMENT_LEAVEN: marinate, soak, brine, ferment, prove | salt/acid/water move in; pH falls; volume rises | Fickian diffusion in a slab (series; Bi → ∞), uptake fraction; pH as a state flag | time, medium (brine/acid/water), size, T | 3 |
| PRESERVATION: dry, pickle, brine, pasteurise, sterilise, can | water activity falls; lethality; salt/acid uptake | drying rate (constant + falling rate), F-value (z = 10, T_ref 121.1 °C), diffusion | T, t, air speed/RH (scenario), size | 4 |
| MECHANICAL_CUT: chop, dice, slice, grate, mince, crush | surface/volume rises; enzymes released (alliinase, myrosinase, PPO) | geometry (size class → L, A/V); enzyme-activation flag with time to the next heat | cut class, time until next heat | 5 |
| MECHANICAL_MIX: whisk, beat, knead, emulsify, fold | air or fat dispersed; gluten network; emulsion | qualitative state flags (AERATED, EMULSIFIED, DEVELOPED); no number | duration, tool | 6 |
| RESTING: rest | carry-over heating, moisture redistribution | conduction continues with the surface in still air | time, previous step's end state | 7 |
| COMBINATION/TRANSFER/SHAPING/SERVING | composition and location only (lots merge or move) | state-graph bookkeeping (already in replay); no physics | none | n/a |
| STORAGE: store, stored at room temperature/refrigerated | slow kinetics over days | Arrhenius kinetics at storage T (needs PARAM, like M3) | storage T, time | 8 |

Router: every family above maps to a FORM candidate, and the 23a gates decide DIRECT, INTERPOLATE, SIMULATE,
QUALITATIVE, ASK or UNKNOWN as before. SIMULATE stays unreachable for a compound until its PARAM rows are human
verified (M3 for vitamin C first). Compute: every family's driver layer runs on the full corpus on vinayak (64–128
workers), tracked in `registry/compute_runs_v1.csv`.
