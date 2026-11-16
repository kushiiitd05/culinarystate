# Learning environment per host (S179, T6-C19-R1; also T6-C02-R2)

Status: AI_DRAFTED, read-only. Code at `440dbeb` on all three hosts. The manjot and vinayak copies were brought to
this commit with an incremental git bundle and a fast-forward merge; vinayak had 5 untracked copies, each
byte-equal to the incoming blob, which were removed first. No package was installed on any host (D-080 #20).

| Host | Python | Packages in the lock | numpy / pandas / scipy | scikit-learn | hypothesis | Transition tests (56) |
|---|---|---:|---|---|---|---|
| Mac (`/opt/anaconda3`) | 3.11.8 | 435 | 1.26.4 / 2.1.4 / 1.11.4 | 1.2.2 | 6.170.5 | 56 passed, 13 s |
| vinayak (`.venv311`) | 3.11.18 | 38 | 1.26.4 / 2.1.4 / 1.11.4 | 1.2.2 | 6.170.5 | 56 passed, 40 s |
| manjot (`.venv312`) | 3.12.3 | 19 | 1.26.4 / 2.1.4 / 1.17.1 | not installed | not installed | 53 passed, 3 failed, 1 s |

- **Files:** `<host>_S179.txt` is the lock (`pip list --format=freeze`, sorted, local install paths redacted).
  `<host>_S179.json` holds the smoke import of the transition and 29-diag modules (all OK on every host), the
  package versions and the test line.
- **Test set:** `tests/unit/test_transition.py`, `test_transition_firewall.py` and `test_s179_diag29_additions.py`.
- **T6-C02-R2, the "test_transition hang" (WORKLOG S134):** not reproduced. The file finishes in 3 s on the Mac, and
  the whole set finishes within 41 s on every host.
- **manjot failures:** the 3 tests fail because `sklearn` is missing. Two need `D5Boosting` (`baselines.py` L142),
  one needs `propensity_weights` (`evaluate.py` L42). This is a missing package, not a hang.
- **Consequence:** under D-080 #20 (no installs on manjot), every run that needs D5 or propensity weights stays on
  the Mac or vinayak. This includes the 29-diag run.
