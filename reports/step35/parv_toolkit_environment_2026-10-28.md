# Step 35 toolkit preparation — 2026-10-28

Parv explicitly said D5: "Go. Dont wait, but record the decision". This
supersedes the earlier session instruction to wait for Kush on this toolkit
choice. This records Parv's authorisation, not Kush's approval or a signature.

The existing interpreter is
`/Users/parvgoyal/wth/CGAS/Project/culinarystate/.venv/bin/python` on Parv's Mac.
Read-only inspection found Python 3.12.4, NumPy 2.5.3, and RDKit distribution
2026.3.6 (runtime string 2026.03.6). No package was installed or environment
created. `pyproject.toml` now pins `rdkit==2026.3.6` in the optional `step35`
extra, leaving unrelated project use independent of the toolkit.

Synthetic-only smoke checks passed:

- Ethanol (`CCO`) produces a nonempty 2048-bit Morgan fingerprint with radius 2
  and `includeChirality=True`, using `rdFingerprintGenerator`.
- Toluene (`Cc1ccccc1`) produces benzene (`c1ccccc1`) as its Murcko scaffold.

These checks establish local API availability only. They do not validate the
scientific pipeline, standardisation/salt grouping, splits, or task performance.
No project molecule, recipe, label or profile was processed. LightGBM, TabPFN
and Open Babel were not added or approved by this action. In particular, the
G2 Morgan-count + LightGBM comparator is not available by implication.

The protocol draft and its unsigned hash template are unchanged. G35-PRE still
blocks real evaluations; per-run versions, input hashes and parameters must be
recorded when a run is eventually authorised. Historical server-environment
statements in the protocol draft remain historical, not observations of this Mac.
