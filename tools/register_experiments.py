#!/usr/bin/env python3
"""Write experiment cards (experiments/<EXP-id>/card.md) + EXP ledger records from DEL-2 result files.

  /opt/anaconda3/bin/python tools/register_experiments.py
Each card: hypothesis, command, data, per-split winner vs D0 persistence, honest verdict. Re-run after new results.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

DEL2 = ROOT / "reports" / "del2"
RUNS = [  # (key, results file, title, command)
    ("del2:usda", "USDA-RETN-R6_results.json", "DEL-2 D0–D7 on USDA retention factors (R6)",
     "tools/run_del2.py --source USDA-RETN-R6 --n-boot 100"),
    ("del2:pe", "PHENOL-EXPLORER-3.6_results.json", "DEL-2 D0–D7 on Phenol-Explorer (raw RF scale)",
     "tools/run_del2.py --source PHENOL-EXPLORER-3.6 --n-boot 100"),
    ("del2:pe_log", "PHENOL-EXPLORER-3.6_log_results.json", "DEL-2 D0–D7 on Phenol-Explorer (log-RF target)",
     "tools/run_del2.py --source PHENOL-EXPLORER-3.6 --n-boot 100 --log-target"),
    ("del2:bognar", "BOGNAR-2002_results.json", "DEL-2 D0–D7 on Bognár (2002) retention factors",
     "tools/run_del2.py --source BOGNAR-2002 --n-boot 100"),
]
CAVEATS = {"del2:bognar": "Bognár factors are averaged and largely templated across food groups (many identical "
                          "columns), so matrix-disjoint is easy here; this is NOT evidence of generalisation to new foods.",
           "del2:pe": "Raw RF up to ~100 dominates MAE; read with the log-target card.",
           "del2:usda": "USDA is a single source (study_disjoint impossible); 100 reported as censored ≥ 0.975."}
HYP = ("Learned transition models (D3–D7) reduce retention-factor error versus D0 'nothing changes' persistence, "
       "and the gain survives cold-start splits (unseen matrix / process / study).")


def card(title: str, cmd: str, res: dict) -> tuple[str, list[str]]:
    rows = res["results"]
    splits = list(dict.fromkeys(r["split"] for r in rows))
    lines = [f"# {title}", "", f"**Hypothesis:** {HYP}", "", f"**Command:** `/opt/anaconda3/bin/python {cmd}`",
             f"**Data:** {res['rows']:,} rows ({res['censored']:,} censored); matrices {res['matrices']}, "
             f"process signatures {res['processes']}, targets {res['targets']}; seed {res['seed']}", "",
             "| split | D0 MAE | best model | best MAE [95% CI] | median AE | beats D0 beyond CI? |", "|---|---|---|---|---|---|"]
    verdicts = []
    for s in splits:
        rs = [r for r in rows if r["split"] == s and r["mae_censor_aware"] == r["mae_censor_aware"]]
        d0 = next(r for r in rs if r["model"].startswith("D0"))
        best = min(rs, key=lambda r: r["mae_censor_aware"])
        degenerate = best["mae_ci"]["low"] == best["mae_ci"]["high"]      # one test group -> no real CI
        beats = (not degenerate and best["mae_ci"]["high"] is not None
                 and best["mae_ci"]["high"] < d0["mae_censor_aware"])
        if not degenerate:
            verdicts.append((s, beats))
        lines.append(f"| {s} | {d0['mae_censor_aware']:.4f} | {best['model']} | {best['mae_censor_aware']:.4f} "
                     f"[{best['mae_ci']['low']}, {best['mae_ci']['high']}] | {best.get('median_ae')} | "
                     f"{'n/a (degenerate split, 1 group)' if degenerate else 'yes' if beats else 'no'} |")
    cold = [b for s, b in verdicts if s != "random"]
    verdict = ("SUPPORTED on random split only; NOT supported under cold-start" if verdicts and verdicts[0][1]
               and not all(cold) else "SUPPORTED incl. cold-start" if all(b for _, b in verdicts)
               else "NOT SUPPORTED")
    lines += ["", f"**Verdict:** {verdict}.", "", "Notes: " + "; ".join(res.get("notes", []))]
    return "\n".join(lines) + "\n", [verdict]


def main() -> None:
    st = LedgerStore()
    for key, fn, title, cmd in RUNS:
        path = DEL2 / fn
        if not path.exists():
            continue
        res = json.loads(path.read_text())
        eid = st.ids.mint("EXP", key=key)
        text, (verdict,) = card(title, cmd, res)
        if key in CAVEATS:
            text += f"\n**Caveat:** {CAVEATS[key]}\n"
        cdir = ROOT / "experiments" / eid
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "card.md").write_text(text)
        st.upsert({"id": eid, "record_type": "EXP", "status": "ACTIVE", "created_by": "Kush+Claude",
                   "provenance": {"method": "DERIVED", "source_ids": [], "agent": "register_experiments@0.1"},
                   "verification": {"status": "UNVERIFIED"}, "title": title, "hypothesis": HYP,
                   "card_path": f"experiments/{eid}/card.md", "results_path": f"reports/del2/{fn}",
                   "run_status": "DONE", "compute": "CPU (Mac M2)", "command": cmd, "notes": verdict})
        print(eid, title, "->", verdict)


if __name__ == "__main__":
    main()
