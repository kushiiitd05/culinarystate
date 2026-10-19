#!/usr/bin/env python3
"""Register existing hand-written experiment cards (EXP-000005..7) in the append-only EXP ledger (S101).

  /opt/anaconda3/bin/python tools/register_exp_cards.py
IDs are minted in order and must equal the card directory names (the minter's next IDs are exactly 5, 6, 7); anything
else aborts before a write. Card text is not touched; hypothesis/gates/dependencies are copied into the record fields.
RQ/GATE ids are kept in `notes` because the RQ and GATE ledgers do not exist yet (refs would dangle).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

CARDS = [
    {"id": "EXP-000005", "key": "e16a:partk_tasteset", "title": "Plan Part K hybrid NER layers on TASTEset (X8)",
     "hypothesis": "Each Part K layer (encoder > rules; + CRF; + kNN-NER; larger encoder) improves entity-level exact F1 "
                   "on held-out TASTEset recipes over the layer below, beyond seed variation.",
     "results_path": "reports/ner/tasteset_encoders_v1.json", "run_status": "DONE", "compute": "A100 (VPN) + CPU",
     "command": "gpu/ner_tasteset/run_all.sh; tools/summarise_ner_runs.py",
     "notes": "RQ/gate: E16-A (SSOT §245), Part K. Verdict: SUPPORTED for encoder > rules and CRF; kNN-NER NULL. "
              "Gate: no RecipeDB-matched claim (API blocked). Depends on: X10 TASTEset, rule floor S047. "
              "Card text predates GLiNER zero-shot (S083) and error analysis (S077); see reports/ner/."},
    {"id": "EXP-000006", "key": "rq1603:silver_pilot", "title": "RQ16-03 evidence compatibility reranker - silver dev pilot",
     "hypothesis": "On scientifically close hard negatives built from the evidence ledger, a structured compatibility "
                   "scorer separates the true evidence cell from hard negatives with higher AUROC than a generic "
                   "cross-encoder (bge-reranker-large) on food-cold and process-cold splits.",
     "results_path": "reports/del4/rq1603_pilot_v1.json", "run_status": "DONE", "compute": "CPU + A100 (CE scoring)",
     "command": "tools/build_rq1603_pairs.py --n 800; tools/score_pairs_ce.py; tools/eval_rq1603.py",
     "notes": "RQ16-03. Success gate met on silver (S2 AUROC 0.995 oracle / 0.975 predicted slots vs CE-large 0.924); "
              "null gate: CIs overlap -> keep structured retriever; negative gate: CE beats structured -> MODIFY. "
              "Headline NEED_DATA: human-labelled pairs and free-text questions. Depends on: EVD ledger, targets lexicon."},
    {"id": "EXP-000007", "key": "hstate:b3_vs_b4", "title": "H_STATE - explicit reconstructed state vs no state (B4 vs B3)",
     "hypothesis": "On questions whose ingredient and/or process are supplied only by the cooking context, rung B4 "
                   "(B3 plus slots and retrieval text filled from the reconstructed session state) returns more "
                   "condition-compatible evidence in the top 5 and a better answer mode than B3, with a paired grouped "
                   "bootstrap 95% CI excluding 0 and no increase in unsupported-claim rate.",
     "results_path": None, "run_status": "PLANNED", "compute": "CPU (Mac); no GPU needed",
     "command": None,
     "notes": "RQ16-01 (RQ16-14 not tested). Gates: success CC@5 CI>0 and UCR not worse; null: oracle gain with predicted CI "
              "spanning 0 -> keep B3, MODIFY extraction; negative: B4<B3 -> DROP state conditioning in retrieval; invalid: "
              "oracle gain ~0 -> questions not state-dependent. Depends on: Gold-v1 pilot_20 (S101, BLOCKED_HUMAN), "
              "60+20 questions (S10x), cut-point harness (not built), answer(use_state) (S100)."},
]


def main() -> None:
    st = LedgerStore()
    existing = {e["id"] for e in st.all_latest("EXP")}
    for c in CARDS:
        if c["id"] in existing:
            print("already registered:", c["id"])
            continue
        if not (ROOT / "experiments" / c["id"] / "card.md").exists():
            sys.exit(f"missing card for {c['id']}")
        eid = st.ids.mint("EXP", key=c["key"])
        if eid != c["id"]:
            sys.exit(f"minter returned {eid}, expected {c['id']}: stop, no replacement IDs")
        rec = {"id": eid, "record_type": "EXP", "status": "ACTIVE", "created_by": "Kush+Claude",
               "provenance": {"method": "DERIVED", "source_ids": [], "agent": "register_exp_cards@0.1"},
               "verification": {"status": "UNVERIFIED"}, "title": c["title"], "hypothesis": c["hypothesis"],
               "card_path": f"experiments/{eid}/card.md", "run_status": c["run_status"], "compute": c["compute"],
               "notes": c["notes"]}
        for k in ("results_path", "command"):
            if c[k]:
                rec[k] = c[k]
        print(eid, st.upsert(rec)[0])


if __name__ == "__main__":
    main()
