# Step 07H -- normalizer production hardening: automated gate

**Overall: PASS**  (normalizer `condition_normalizer@2.0.0-07H`, combined hash `a5991a9cda56a867b0a1b845ec5376a088840962dfc0b45c06a826cc2d2f646e`)

| gate | result |
|---|---|
| G1_unit_tests_pass | PASS |
| G2_schema_tests_pass | PASS |
| G3_golden_pass | PASS |
| G4_open_bound_pass | PASS |
| G5_trajectory_pass | PASS |
| G6_property_pass | PASS |
| G7_current_data_regression_completed_4414_17978 | PASS |
| G8_source_ledgers_byte_identical | PASS |
| G9_deterministic_two_rebuilds | PASS |
| G10_no_unsupported_abbreviation_promoted | PASS |

## Test counts

- 1 unit tests (units, normalizer, dialect, agreement tool): {'passed': 45, 'returncode': 0}
- 2 schema tests: {'passed': 138, 'returncode': 0}
- 3 golden syntax cases: {'passed': 123, 'returncode': 0}
- 4 inequality / open-bound tests: {'passed': 49, 'returncode': 0}
- 5 trajectory tests: {'passed': 6, 'returncode': 0}
- 6 property-based tests (Hypothesis, 300 examples each): {'passed': 10, 'returncode': 0}

## Current-data regression (4,414 conditions / 17,978 EVD references)

- fields compared 15872; unchanged 15718; changed 154; **unexplained 0**
- every change, by cause:
  - 85 x UNIT_FACTOR_PRECISION (psi factor 6894.757293168 -> exact lbf/in2 6894.757293168361; relative change < 1e-9, status unchanged) | POINT/AMBIGUOUS -> POINT/AMBIGUOUS
  - 69 x OPEN_BOUND_FIX (GT_*: old open_high=True, new open_low=True; same endpoint, same status) | INTERVAL/VALID -> INTERVAL/VALID
- audit count sections changed vs pre-07H: none; reason-count changes: none
- ledgers byte-identical: True; audit deterministic over two rebuilds: True
