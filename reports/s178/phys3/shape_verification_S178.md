# Shape eigen-series verification pack (S178 PHYS3, T4-C08-R1)

Status: DRAFT / AI_DRAFTED. A numerical verification of `shape_series` (infinite cylinder, sphere, finite cylinder, cube / brick) against independent references; not a validation against food and not a human signature. Shapes are NOT wired into Layer 2 in this round: the slab stays the stated slow-side bound.

Reproduce: `python tools/s178_phys3_shape_verification.py --out-json reports/s178/phys3/shape_verification_S178.json --out-md reports/s178/phys3/shape_verification_S178.md`; `results_sha256` = `ab3b285d112e5524078338f425ad1a249cfeec6c210c4193e3721cbbdf996949` (results rounded to 6 significant digits).

**Result: 15 of 15 checks pass.**

| id | check | cases | max abs error | max rel error | tolerance | pass |
|---|---|---:|---:|---:|---|---|
| SV01 | Bi = inf: centre and volume-mean theta of slab, cylinder, sphere against independent Dirichlet series | 36 | 3.33e-16 | 3.33e-16 | 1e-12 (abs) | yes |
| SV02 | Bi -> infinity (Bi = 1e8): cylinder and sphere centre and mean theta against the Dirichlet series | 20 | 2.1e-08 | 2.27e-07 | 1e-06 (abs) | yes |
| SV03 | Bi -> 0: centre and mean theta of cylinder, sphere, finite cylinder (Lz = R, 2R) and cube against lumped capacitance exp(-(h A / k V) alpha t) | 60 | 0.00058 | 0.000587 | 0.001 (abs) | yes |
| SV04 | long-cylinder limit: finite-cylinder centre theta -> infinite cylinder at half-height >= 10 R (and the thin disk -> slab); the mean converges monotonically in Lz / R | 44 | 1.24e-13 | 2.79e-12 | 1e-09 (abs) | yes |
| SV05 | short times: slab surface = semi-infinite solid (exact before the fronts meet); Dirichlet sphere uptake = 6 sqrt(Fo/pi) - 3 Fo (exact up to ierfc terms < 1e-40 at Fo <= 0.02); sphere surface -> semi-infinite solid (error falls monotonically as Fo -> 0, observed order >= 0.5 at the smallest Fo) | 21 | 4.44e-16 | 8.29e-15 | 1e-10 (abs) | yes |
| SV06 | centre, surface and mean theta of slab, cylinder, sphere against a 200-cell finite-volume solve | 144 | 2.14e-05 | 8.76e-05 | 0.002 (abs) | yes |
| SV07 | product rule: finite cylinder (half-height 0.5, 1, 2 R) and square bar, centre, outer corner and mean theta against a 2-D Crank-Nicolson finite-volume solve (60 cells per radius) | 48 | 0.000126 | 0.000462 | 0.003 (abs) | yes |
| SV08 | roots: scaled eigen-condition residual of the first 200 roots (Bi 1e-6 .. 1e6), strictly increasing; exact roots and C_n at Bi = 1 (sphere: pi/2, 4/pi) and Bi = inf (j_01, 2/(j_01 J1(j_01)); 2(-1)^(n+1); 4(-1)^(n+1)/((2n-1) pi)) | 7 | 1.13e-13 | 1.13e-13 | 1e-12 (abs) | yes |
| SV09 | first-term zeta_1 and C_1 of cylinder and sphere versus Bi (textbook table, 4 decimals) against the root finder | 52 | 6.16e-05 | 0.000317 | 0.0006 (abs) | yes |
| SV10 | coefficients: C_n x mean factor against the closed forms 2Bi^2/(z^2(z^2+Bi^2+Bi)), 4Bi^2/(z^2(z^2+Bi^2)), 6Bi^2/(z^2(z^2+Bi^2-Bi)); completeness sum_n C_n m_n + analytic tail = 1 over 4000 terms | 36 | 9.97e-12 | 2.27e-06 | 1e-10 (abs) | yes |
| SV11 | slab bound: centre and mean theta of cylinder, sphere, finite cylinder (Lz = 0.5, 1, 2 R), cube and brick (1:2:3) <= the slab of the smallest half-dimension (Bi 0.01 .. 100, Fo 1e-3 .. 5); sphere <= cylinder <= slab | 1 | 0 | 0 | 0 (abs) | yes |
| SV12 | shape_series slab against physics_drivers (the Layer 2 slab): local and mean theta, Fo >= 0.02 | 80 | 3.33e-16 | 1.79e-14 | 1e-10 (abs) | yes |
| SV13 | one-term (Heisler chart) centre theta of cylinder and sphere against the full series at Fo >= 0.2 | 24 | 0.0104 | 0.0119 | 0.02 (rel) | yes |
| SV14 | truncation: the Fo-adaptive term count against twice as many terms (Fo 1e-5 .. 1, centre to surface, mean) | 270 | 3.11e-15 | 3.11e-15 | 1e-12 (abs) | yes |
| SV15 | dimensional wrapper: slab geometry against physics_drivers.core_and_mean_temperature (degC), cube = slab^3, V/A of each shape | 69 | 1.42e-14 | 7.11e-16 | 1e-08 (abs) | yes |

## Reading

- Finite-volume references: 1-D (200 cells, exact in time) max abs error in theta by shape {"SLAB": 7.86138e-06, "INFINITE_CYLINDER": 1.01119e-05, "SPHERE": 2.14426e-05}; 2-D Crank-Nicolson (60 cells per radius) of the finite cylinder and the square bar {"FINITE_CYLINDER_H0.5": 7.73837e-05, "FINITE_CYLINDER_H1.0": 0.000126026, "FINITE_CYLINDER_H2.0": 9.27751e-05, "SQUARE_BAR_H1.0": 7.86663e-05}. The 2-D check is the product rule (Heisler products) against a solve that does not separate variables.
- Slab bound (SV11): 1512 comparisons on the grid Bi 0.01-100, Fo 1e-3-5; violations 0, ordering violations (sphere <= cylinder <= slab) 0. This is numerical evidence for the bound on that grid, not a proof.
- Long-cylinder limit (SV04): centre and mean error by half-height / radius {"1.0": [0.138697, 0.92291], "2.0": [0.035865, 0.552522], "5.0": [5.64677e-05, 0.221721], "10.0": [1.24456e-13, 0.11086], "30.0": [8.88178e-16, 0.0369535], "100.0": [6.66134e-16, 0.011086]} ([centre abs, mean rel]); the centre reaches the infinite cylinder at Lz >= 10 R, the mean converges like R / Lz.
- Short times (SV05): sphere surface against the semi-infinite solid, observed order in Fo {"Bi0.5": [1.0, 1.0, 1.0, 1.0], "Bi2.0": [0.995, 0.99, 0.98, 0.96], "Bi10.0": [0.968, 0.938, 0.88, 0.78], "Bi50.0": [0.848, 0.727, 0.55, 0.35]} (1 while Bi sqrt(Fo) << 1).
- Truncation (SV14): the term count is chosen from Fo (tail < 1e-14); the largest count used in the grid is 581; Fo below 2.09e-07 is refused (semi-infinite regime).
- SV09 compares with first-term constants recalled from the heat-transfer textbook tables and SV13 relies on the recalled statement that one term is within about 2 % at Fo >= 0.2: both tagged `SOURCE_UNVERIFIED_AGENT_RECALLED`, both also covered by exact checks (SV01, SV08) that do not depend on recall.
- Not covered: property variation with temperature, irregular shapes, food data. The map from cut / ingredient class to shape (`registry/shape_map_v1.csv`) is ASSUMED_DEFAULT and is not verified by this pack.
