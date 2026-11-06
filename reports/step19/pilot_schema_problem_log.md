# Step 19 pilot schema-problem log (text-free)

Entries use packet ids and field families only; no recipe text. Created S166 (D-063) from prv's re-check of annotator A's AI pass.

| SP id | Wave | Packet | Field family | Problem | Category | Rating effect | Status |
|---|---|---|---|---|---|---|---|
| SP-001 | P1 | DGP-A-0007 | steps.events / coref | The engine creates entities only from ingredient lines, so an ingredient named in the steps but absent from the ingredient lines cannot be an entity or an event target; it is kept as UNKNOWN coref plus an `unknowns` entry. The dish state loses a stated main component. | coreference/entity (tooling) | WORKAROUND (Kush, D-063; strict reading would be IMPOSSIBLE) | OPEN: needs a schema/engine decision (e.g. allow step-introduced entities) before P2 |
