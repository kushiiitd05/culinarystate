# Physical-layer verification pack (S178 PHYS2, T4-C07-R1)

Status: DRAFT / AI_DRAFTED. A numerical verification of the drivers against independent references; not a validation against food and not a human signature. Textbook constants are recalled by the agent (`SOURCE_UNVERIFIED_AGENT_RECALLED`).

Reproduce: `python tools/s178_phys_verification.py --out-json reports/s178/phys/verification_pack_S178.json --out-md reports/s178/phys/verification_pack_S178.md`; `results_sha256` = `212b07e9b752a7ba3b90606d063171d1f01f0258a4d3ed3ed7ffb2adcb904bd8` (check results rounded to 6 significant digits).

**Result: 15 of 15 checks pass.** Slab series against the exact independent references (Dirichlet limit, semi-infinite solution, continuity, quadrature, 200-node finite-difference solve): max absolute error in theta 7.6e-06, max relative error 2.86e-05; against the finite-difference solve alone 7.6e-06 absolute / 2.86e-05 relative (theta floor 1e-3); the lumped (Bi -> 0) limit differs from the exact slab by 0.00017 at Bi = 1e-3, the O(Bi) error of the lumped model itself. Exact modal stepper: observed spatial order 2; error 5.61e-06 at 160 nodes. N_TERMS = 60: the series is converged to 1e-10 with 10 terms in the worst case at Fo >= 0.02.

| id | check | cases | max abs error | max rel error | tolerance | pass |
|---|---|---:|---:|---:|---|---|
| V01 | Bi -> 0: volume-average and centre theta against exp(-Bi Fo) (lumped capacitance) | 12 | 0.000167 | 0.000168 | 0.001 (rel) | yes |
| V02 | Bi -> infinity: centre and volume-average theta against the Dirichlet series (4/pi, 8/pi^2) | 10 | 1e-08 | 5.93e-08 | 1e-05 (rel) | yes |
| V03 | Fo < 0.02: surface theta against the convective semi-infinite solution exp(u^2) erfc(u), u = Bi sqrt(Fo) | 16 | 5.55e-17 | 5.26e-16 | 1e-09 (rel) | yes |
| V04 | continuity of the local and mean theta across the series / front switch at Fo = 0.02 | 24 | 4.55e-07 | 4.55e-07 | 1e-06 (abs) | yes |
| V05 | plane-wall first-term zeta_1 and C_1 versus Bi (textbook table, 4 decimals) against the root finder | 27 | 5.07e-05 | 0.000343 | 0.0006 (abs) | yes |
| V06 | centre theta at Fo >= 0.2: full series against the one-term chart curve built from textbook zeta_1, C_1 | 65 | 0.0166 | 0.0181 | 0.02 (rel) | yes |
| V07 | volume-average theta against 32-node Gauss-Legendre integration of the local theta over the slab | 20 | 5.55e-16 | 5.55e-16 | 2e-06 (abs) | yes |
| V08 | centre, surface and volume-average theta against a 200-node Crank-Nicolson finite-difference solve | 48 | 7.6e-06 | 2.86e-05 | 0.002 (abs) | yes |
| V09 | exact modal stepper (n = 160 nodes) against the series for (1 - theta) at the centre, surface and volume mean | 4 | 5.61e-06 | 6.39e-06 | 0.0002 (abs) | yes |
| V10 | exact modal stepper, two stages (ambient 150 -> 60 C), against the analytic superposition of two series | 18 | 0.000301 | 3.99e-06 | 0.05 (abs) | yes |
| V11 | exact modal stepper against its own Crank-Nicolson mode (same 30-node system, Fo step 5e-4), two stages | 21 | 2.52e-05 | 3.75e-07 | 0.05 (abs) | yes |
| V12 | N_TERMS = 60 convergence: centre and mean theta against a 400-term series, Fo >= 0.02 | 25 | 0 | 0 | 1e-10 (abs) | yes |
| V13 | Plank slab freezing time against an independent integration of the quasi-steady front ODE, thaw mirror, conduction-only and convection-only limits and 1/dT scaling | 15 | 2.88e-07 | 3.6e-10 | 1e-06 (rel) | yes |
| V14 | Plank time against an enthalpy-method Stefan solve at decreasing Stefan number (Plank = the Ste -> 0 limit) | 3 | 16.1 | 0.108 | 0.25 (rel) | yes |
| V15 | Fickian slab uptake fraction against a 200-node Crank-Nicolson diffusion solve, the short-time sqrt and long-time one-term limits and the textbook half-uptake time | 16 | 4.41e-05 | 0.00166 | 0.0005 (abs) | yes |

## Plank against the enthalpy-method Stefan solve (V14)

Plank neglects the sensible heat of the frozen layer, so it is the Stefan number -> 0 limit; the difference must fall with Ste.

| Ste | enthalpy method (s) | Plank (s) | Plank / enthalpy |
|---:|---:|---:|---:|
| 0.4 | 148.91 | 132.84 | 0.8921 |
| 0.2 | 141.08 | 132.84 | 0.9416 |
| 0.1 | 137.02 | 132.84 | 0.9695 |

## Notes

- V05 and V06 compare with the plane-wall table of the first-term constants (zeta_1, C_1) recalled from the heat-transfer textbook; V15 uses the recalled half-uptake time D t / L^2 = 4 x 0.04919. Both are tagged `SOURCE_UNVERIFIED_AGENT_RECALLED`: the pack does not depend on them for the analytic and finite-difference checks (V01-V04, V07-V15).
- V06: the one-term (Heisler-chart) curve differs from the full series by up to 1.8 % at Fo = 0.2 and by less later, as the textbook says; the driver uses the full series.
- V09 observed order: {"Bi1.0_Fo0.2": [1.999, 2.0, 2.0, 2.0], "Bi1.0_Fo0.5": [2.001, 2.0, 2.0, 2.0], "Bi10.0_Fo0.2": [2.002, 2.0, 2.0, 2.0], "Bi10.0_Fo0.5": [2.002, 2.001, 2.0, 2.0]}.
- V12: the default N_TERMS has a margin of 6x over the worst case in the grid (Bi 0.1-1000, Fo 0.02-1).
- Not covered: shape factors (cylinder, sphere), property variation with temperature, food data. Verification of the drivers says nothing about whether a recipe's food behaves like the model.
