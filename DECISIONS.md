# DECISIONS (ADR log)

Format: ID · date · decision · options considered · evidence · approver. Append-only.

### D-001 · 2026-10-18 · Rebuild programme repo locally in `CGAS/culinarystate`
- **Options:** (a) wait for Parv's Max-plan repo; (b) rebuild here, Parv continues from this repo.
- **Evidence:** no STATUS/DECISIONS/evidence-candidate files on this machine; Kush instructed "forget whatever github we have, he can pick or take from here".
- **Approver:** Kush.

### D-002 · 2026-10-18 · Ledger schemas are JSON Schema (draft 2020-12) + Python semantic validators, not pydantic
- **Options:** pydantic v1 (base env) / pydantic v2 (other envs) / JSON Schema.
- **Evidence:** base env has pydantic 1.10, other envs 2.12 → API split. JSON Schema is language-neutral and `jsonschema 4.19` is in base.
- **Approver:** Claude (reversible; flag for Kush/Parv review).

### D-003 · 2026-10-18 · Recipe corpus without RecipeDB = A1 BBC Good Food (11,934 recipes); NER gold proxy = TASTEset
- **Evidence:** RecipeDB API endpoint timed out; no key. A1 corpus has raw ingredient lines + instruction steps. TASTEset has span-level FOOD/QUANTITY/UNIT/PROCESS labels.
- **Constraint:** BBC text is third-party copyrighted → raw text stays local-only (`data/raw`, git-ignored); only derived annotations/statistics are committed.
- **Approver:** Kush (pending confirmation).

### D-004 · 2026-10-18 · Interpreter = `/opt/anaconda3/bin/python` (base); heavy ML (transformers/lightgbm) = `recsys_env`. No new venvs.
- **Approver:** standing user rule.
