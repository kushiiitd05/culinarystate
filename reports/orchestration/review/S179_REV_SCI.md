# S179 re-review, SCI pass (fixer snapshot 6f8d1bc + S179 composition fixes)

AI review (Opus subagent), read-only, with synthetic probes through Binder -> ScenarioLayer, route_text, EvidenceGates,
PHTable; the 8 fix test files pass (178 tests). AI review is not human verification (D-071).

**Verdict: no blockers; 2 MAJOR, 6 MINOR open.**

| # | Severity | Finding | Where | Proposed fix |
|---|---|---|---|---|
| 1 | MAJOR | M1 residual: a food target after an until-clause cut is still bound as the medium temperature ("Fry the chicken until the juices run clear and the meat is 165 F" -> fry 73.9 °C; "Simmer the sauce until it thickens and reaches 160 F" -> bath 71.1 °C; "Roast the beef until done (140 F for rare)" -> oven 60 °C; "Bake the bread until it sounds hollow, about 200 F inside" -> oven 93.3 °C) | `simulation/endpoint_cues.py` `_UNTIL_END` cuts at `and/or/,/(` | extend the clause across and/or when no event verb starts the next conjunct; treat "N F for rare/medium/well" and "N F inside/internal" as targets; RED tests with the four inputs |
| 2 | MAJOR | M4/M5 residual: lift gate fires on dilute liquids (one SWEETENER member or a sugar word = "syrup stage"); piece surface dose computed at the lifted temperature (9,583.8 vs 120 at 100 °C) while carrying SURFACE_DOSE_AT_TBOIL_WET_PERIOD_ONLY; immersed piece gets SURFACE_DRYING_POSSIBLE | `phase_change.py:189-221`, `condition_binding.py:109`, `scenario_layer.py:307` | lift only on a true stage cue (named stage, candy / jam thermometer, owner object itself syrup / jam / caramel / candy); with a piece, surface dose at the piece boundary, liquid dose separate. Stricter than the SCI-A rule (b): **needs Kush's Q1 ruling** |
| 3 | MINOR | M1 corpus counter vacuous: audit tests `syrup_exempt`, records carry `temperatures[].role` | `tools/s178_phys_fixphys_audit.py:93` | count by TARGET_ROLES vs EXEMPT_ROLES; report the non-exempt count |
| 4 | MINOR | R2 residual: text order taken as time order ("Fry the potatoes that you boiled yesterday", "(already boiled)"); "left over" (two words) missing | `mechanism/evidence_gates.py:174-185` | add cues + tests |
| 5 | MINOR | A2 residual: pH head fallback on the last query token ("large egg white" -> 'onion white' 5.37-5.85); `any_form` of "egg white" excludes the item match | `composition/food_ph.py` | strip size / quantity adjectives; head union must share the parent token; assert any_form ⊇ item |
| 6 | MINOR | SPLIT_FRACTIONS_EXCEED_ONE 0/0/0 is vacuous on the corpus (0 checkable groups) | `replay_invariants_corpus_v2.md` | mark NOT_CHECKABLE_ON_CORPUS |
| 7 | MINOR | MECH NOT_POSSIBLE from an SR analytical 0 (ZERO_FLOOR 1e-6) means "below reporting limit", not absence; ABSENT on 1 data point for 3 ING | `mechanism/mech_inputs.py:14,43` | reason SR_BELOW_REPORTING; human ruling before it means NOT_POSSIBLE |
| 8 | MINOR | McNemar power docstring derivative misses a factor; wrong-direction rejections counted (≤0.002, acknowledged) | `evaluation/mcnemar_power.py` | docstring fix |

Per original finding: SCI-A FIXED M2, M3, M5 (core), M7, m1-m11 (m10 row 3c open as stated); PARTIAL M1 (#1), M4 (#2),
M6 (caveat added; boundary-model axis OPEN_NOT_COMPUTED). SCI-B FIXED R1, R3-R7, E1-E8, P1, P2, CORP-4/5/6, B5; PARTIAL
R2 (#4). Composition: FIXED A1, A3-A9, A11, F2-F4 (A6b human choice open); PARTIAL A2 (#5); A10 not reviewed.

Verified directly: no moist-piece core above T_boil; water bath boundary 100 °C; setter / oven temperatures no longer
cross media; candy stage ("Boil the syrup to 240 F") kept; the 13 remaining ABSENT ING are all derivation A with ≥1 data
point; MDE table identical v1 -> v2; heat statuses unchanged.

## Disposition (S179b, same night)

| # | Status | Commits / note |
|---|---|---|
| 1 M1 residual | FIXED, tests first | RED tests e413099 `test_s179_phys_m1_residual.py` (the four probes + 3 controls); `endpoint_cues` 0.3.0: clause runs across and/or when no event verb starts the next conjunct, subject read from the last conjunct, "N F for rare/medium/well" and "N F inside / internal" are food targets; L1 0.3.1. Re-run as v06 (BBC on the Mac: TEXT_STATED temperatures 5,669 -> 5,664; non-BBC on manjot) |
| 2 M4/M5 residual | OPEN, needs Kush (Q1) | stricter lift gate than SCI-A rule (b) changes the signed-off direction; not changed by an agent |
| 3 audit counter | FIXED | `test_s179_fixphys_audit_roles.py`; audit counts by role (target / exempt / unclassified); v05 audit re-run with the fixed tool in the v06 chain |
| 4 R2 residual | FIXED, tests first | `test_s179_router_r2_residual.py`; post-food state cue + two-word "left over"; census 0.4.1 (BBC route counts unchanged; non-BBC re-run on vinayak) |
| 5 A2 residual | FIXED, tests first | size words dropped before lookup; item-match `any_form` = its parent family (always contains the item) |
| 6 split-sum vacuous | NOTED | CORPUS correction section: SPLIT_FRACTIONS_EXCEED_ONE is NOT_CHECKABLE_ON_CORPUS (0 checkable groups) |
| 7 MECH SR "0" | OPEN, needs a human ruling | renaming the reason / treating analytical 0 as below reporting limit changes MECH semantics |
| 8 power docstring | FIXED (docstring only) | 4add9ba: bracket [p^(2k-m-1) - (1-p)^(2k-m-1)] with factor m (checked symbolically m = 3..11); wrong-direction rejections stated: below 1e-6 at each planning MDE, at most 0.013 at delta 0.005 (the review's 0.002 holds only near the MDE); no number changed |
