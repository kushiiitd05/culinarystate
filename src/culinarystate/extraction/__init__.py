"""Step 17 instruction-level extraction package (DRAFT_PENDING_16c).

Hard gate 16c (Step 16 schema pack v1) is open: everything in this package is an
engineering draft that reads no ledger, writes nothing and is not a human
verification. Modules:

- ``interfaces``: the six-stage common interface of Plan Step 17-M with explicit
  failure results and per-output provenance;
- ``quantity_stages``: ``parse_quantity`` / ``ground_quantity`` delegating to the
  existing rc2 adapter and grounding pipeline;
- ``validators``: V1 span round-trip, V2 schema, V3 vocabulary membership;
- ``invariants``: V4 Step-18 graph invariants;
- ``auditor``: invented-value auditor with an integer invented count.
"""
