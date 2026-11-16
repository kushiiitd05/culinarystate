# Physical-layer verification pack (S178 PHYS2, T4-C07-R1; FIX-PHYS v05)

Status: DRAFT / AI_DRAFTED. A numerical verification of the drivers against independent references; not a validation against food and not a human signature. Textbook constants are recalled by the agent (`SOURCE_UNVERIFIED_AGENT_RECALLED`).

Reproduce: `python tools/s178_phys_verification.py --out-json reports/s178/phys/verification_pack_S178_v05.json --out-md reports/s178/phys/verification_pack_S178_v05.md`; `results_sha256` = `538f5377dd8ac237d921d0b06cb53d09f7e42fc39f8ac8050fc04b42d0c9eb87` (check results rounded to 6 significant digits).

**Independence (S178 FIX-PHYS m7).** INDEPENDENT: 11 of 11 pass; IDENTITY: 2 of 2 pass; SELF_CONSISTENCY: 2 of 2 pass; LOOSE_TOLERANCE: 2 of 2 pass; RECALLED_CONSTANTS: 1 of 1 pass. Only the INDEPENDENT checks compare the drivers with a reference that shares no formula or code path with them; IDENTITY and SELF_CONSISTENCY checks catch coding slips, not a wrong formula; LOOSE_TOLERANCE checks could pass a wrong trend (V14 is now also gated on the trend); RECALLED_CONSTANTS depend on agent-recalled table values.

**Result: 18 of 18 checks pass.** Slab series against the exact independent references (Dirichlet limit, semi-infinite solution, continuity, quadrature, 200-node finite-difference solve): max absolute error in theta 7.6e-06, max relative error 2.86e-05; against the finite-difference solve alone 7.6e-06 absolute / 2.86e-05 relative (theta floor 1e-3); the lumped (Bi -> 0) limit differs from the exact slab by 0.00017 at Bi = 1e-3, the O(Bi) error of the lumped model itself. Exact modal stepper: observed spatial order 2; error 5.61e-06 at 160 nodes. N_TERMS = 60: the series is converged to 1e-10 with 10 terms in the worst case at Fo >= 0.02.

| id | independence | check | cases | max abs error | max rel error | tolerance | pass |
|---|---|---|---:|---:|---:|---|---|
| V01 | INDEPENDENT | Bi -> 0: volume-average and centre theta against exp(-Bi Fo) (lumped capacitance) | 12 | 0.000167 | 0.000168 | 0.001 (rel) | yes |
| V02 | INDEPENDENT | Bi -> infinity: centre and volume-average theta against the Dirichlet series (4/pi, 8/pi^2) | 10 | 1e-08 | 5.93e-08 | 1e-05 (rel) | yes |
| V03 | IDENTITY | Fo < 0.02: surface theta against the convective semi-infinite solution exp(u^2) erfc(u), u = Bi sqrt(Fo) | 16 | 5.55e-17 | 5.26e-16 | 1e-09 (rel) | yes |
| V04 | INDEPENDENT | continuity of the local and mean theta across the series / front switch at Fo = 0.02 | 24 | 4.55e-07 | 4.55e-07 | 1e-06 (abs) | yes |
| V05 | RECALLED_CONSTANTS | plane-wall first-term zeta_1 and C_1 versus Bi (textbook table, 4 decimals) against the root finder | 27 | 5.07e-05 | 0.000343 | 0.0006 (abs) | yes |
| V06 | LOOSE_TOLERANCE | centre theta at Fo >= 0.2: full series against the one-term chart curve built from textbook zeta_1, C_1 | 65 | 0.0166 | 0.0181 | 0.02 (rel) | yes |
| V07 | INDEPENDENT | volume-average theta against 32-node Gauss-Legendre integration of the local theta over the slab | 20 | 5.55e-16 | 5.55e-16 | 2e-06 (abs) | yes |
| V08 | INDEPENDENT | centre, surface and volume-average theta against a 200-node Crank-Nicolson finite-difference solve | 48 | 7.6e-06 | 2.86e-05 | 0.002 (abs) | yes |
| V09 | INDEPENDENT | exact modal stepper (n = 160 nodes) against the series for (1 - theta) at the centre, surface and volume mean | 4 | 5.61e-06 | 6.39e-06 | 0.0002 (abs) | yes |
| V10 | INDEPENDENT | exact modal stepper, two stages (ambient 150 -> 60 C), against the analytic superposition of two series | 18 | 0.000301 | 3.99e-06 | 0.05 (abs) | yes |
| V11 | SELF_CONSISTENCY | exact modal stepper against its own Crank-Nicolson mode (same 30-node system, Fo step 5e-4), two stages | 21 | 2.52e-05 | 3.75e-07 | 0.05 (abs) | yes |
| V12 | SELF_CONSISTENCY | N_TERMS = 60 convergence: centre and mean theta against a 400-term series, Fo >= 0.02 | 25 | 0 | 0 | 1e-10 (abs) | yes |
| V13 | IDENTITY | Plank slab freezing time against an integration of the same quasi-steady front ODE (identity), the thaw formula (with identical k and dT it reduces to Plank's form), conduction-only and convection-only limits and 1/dT scaling | 15 | 2.88e-07 | 3.6e-10 | 1e-06 (rel) | yes |
| V14 | LOOSE_TOLERANCE | Plank time against an enthalpy-method Stefan solve at decreasing Stefan number (Plank = the Ste -> 0 limit) | 3 | 16.1 | 0.108 | 0.25 (rel) | yes |
| V15 | INDEPENDENT | Fickian slab uptake fraction against a 200-node Crank-Nicolson diffusion solve, the short-time sqrt and long-time one-term limits and the textbook half-uptake time | 16 | 4.41e-05 | 0.00166 | 0.0005 (abs) | yes |
| V16 | INDEPENDENT | Fo < 0.02: local theta of the convective front solution at xi 0.5 and 0.9 against a 400-node Crank-Nicolson solve (time step Fo 5e-6) | 12 | 2.53e-05 | 2.76e-05 | 0.002 (abs) | yes |
| V17 | INDEPENDENT | zone-mean dose of the layer (8 Gauss-Legendre nodes, 48 graded times) against a dense reference (24 nodes, 1,200 uniform times) | 3 | 0.00168 | 0.00112 | 0.01 (rel) | yes |
| V18 | INDEPENDENT | numerical bias of the zone-mean dose (trapezoid on the graded node grid) and of the dose at the volume-average temperature (midpoint T, uniform 40 steps) against the dense reference; the physical zone / volume-average ratio must exceed twice the bias | 6 | 0.00112 | 0.00112 | 0.005 (rel) | yes |

## Plank against the enthalpy-method Stefan solve (V14)

Plank neglects the sensible heat of the frozen layer, so it is the Stefan number -> 0 limit; the difference must fall with Ste.

| Ste | enthalpy method (s) | Plank (s) | Plank / enthalpy |
|---:|---:|---:|---:|
| 0.4 | 148.91 | 132.84 | 0.8921 |
| 0.2 | 141.08 | 132.84 | 0.9416 |
| 0.1 | 137.02 | 132.84 | 0.9695 |

## Dose-rule biases (V18, SCI-A m9)

The layer's zone-mean dose (trapezoid on the dose rate, graded 48-step node grid) and its dose at the volume-average temperature (midpoint temperature, uniform 40 steps) against a dense reference (24 nodes, 1,200 uniform times). Signs: volume-average-T dose NEGATIVE, zone mean MIXED; the physical zone / volume-average ratio exceeds twice the bias in every case: True.

| case | zone-mean bias | volume-average-T bias | reference zone / vol-avg - 1 |
|---|---:|---:|---:|
| t0_4_bath_100_min_2_L_0.004_h_200_z_33 | +0.00054 | -0.00048 | 0.1525 |
| t0_4_bath_100_min_30_L_0.01_h_500_z_10 | -0.00016 | -0.00112 | 0.0588 |
| t0_20_bath_98_min_1_L_0.005_h_300_z_10 | +0.00112 | -0.00097 | 23.4330 |

## Notes

- V05 and V06 compare with the plane-wall table of the first-term constants (zeta_1, C_1) recalled from the heat-transfer textbook; V15 uses the recalled half-uptake time D t / L^2 = 4 x 0.04919. Both are tagged `SOURCE_UNVERIFIED_AGENT_RECALLED`: the pack does not depend on them for the analytic and finite-difference checks (V01-V04, V07-V18).
- V06: the one-term (Heisler-chart) curve differs from the full series by up to 1.8 % at Fo = 0.2 and by less later, as the textbook says; the driver uses the full series.
- V09 observed order: {"Bi1.0_Fo0.2": [1.999, 2.0, 2.0, 2.0], "Bi1.0_Fo0.5": [2.001, 2.0, 2.0, 2.0], "Bi10.0_Fo0.2": [2.002, 2.0, 2.0, 2.0], "Bi10.0_Fo0.5": [2.002, 2.001, 2.0, 2.0]}.
- V12: the default N_TERMS has a margin of 6x over the worst case in the grid (Bi 0.1-1000, Fo 0.02-1).
- Not covered: shape factors (cylinder, sphere), property variation with temperature, food data. Verification of the drivers says nothing about whether a recipe's food behaves like the model.
