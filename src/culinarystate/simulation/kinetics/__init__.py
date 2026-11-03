"""Step 26a kinetic fitting and identifiability library (S159, DRAFT_PENDING_26_0_H4; data-free).

Modules: ``units`` (dimension checker), ``models`` (card-named kinetic forms), ``fitting`` (weighted least
squares with multi-start; numpy Levenberg-Marquardt, optional scipy backend per D-050) and
``identifiability`` (local sensitivity, profile likelihood, per-parameter verdicts).

No parameter value, prior, default start or threshold of any food system is held here. Tests use synthetic
data generated from known parameters inside the tests. Nothing reads or writes a ledger. The 26.0 selection
record and pre-registration (Kush + Parv) and H4 approval of 24a are still required before any real fit
(Plan v2 Step 26 card, R-14), hence the status label.
"""
STATUS = "DRAFT_PENDING_26_0_H4"
