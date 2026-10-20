#!/usr/bin/env python3
"""S119 alias/concept leakage audit (design contract D.7): may ledger ING names + aliases be used as an external gazetteer for the NER benchmark?

  /opt/anaconda3/bin/python tools/audit_alias_leakage.py      # -> reports/ner/alias_leakage_audit.json + .md
Checks (DEV and CALIBRATION only; TEST surfaces are not inspected):
 1. provenance: do any ACTIVE ING / ALIAS records derive from the benchmark corpora (RecipeDB3, TASTEset, CoSyLab ingredient files)?
 2. coverage: share of DEV gold FOOD/NAME surfaces (all, unseen-in-train, tail) that exactly match a ledger surface -> upper bound on what an external
    gazetteer could add; reported so a later gain is attributable to knowledge, not to leakage.
Verdict ALLOWED only if no provenance link to the benchmark corpora exists."""
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.ner import benchmark as B  # noqa: E402
import freeze_ner_benchmark as F  # noqa: E402
import pandas as pd  # noqa: E402

BAD = re.compile(r"recipedb|cosylab|tasteset|ingredient_annotated|foodoscope", re.I)


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def main():
    st = LedgerStore()
    surf, prov, bad = set(), Counter(), []
    for kind in ("ING", "ALIAS"):
        for r in st.all_latest(kind):
            if r["status"] != "ACTIVE":
                continue
            p = json.dumps(r.get("provenance") or {}) + json.dumps(r.get("external_refs") or "")
            cw = r.get("crosswalks") or {}
            linked = [k for k, v in cw.items() if BAD.search(k) and (v or {}).get("status") != "UNRESOLVED_EXTERNAL"]     # key present but unresolved = no data
            prov[(kind, (r.get("provenance") or {}).get("agent", "?").split("@")[0])] += 1
            if BAD.search(p) or linked:
                bad.append((kind, r["id"]))
            surf.add(norm(r.get("canonical_name") or r.get("normalized") or r.get("surface")))
    out = {"ledger_surfaces": len(surf), "provenance_counts": {f"{k}:{a}": n for (k, a), n in prov.items()}, "records_linked_to_benchmark_corpora": bad[:20], "n_bad": len(bad), "datasets": {}}
    for ds, view, getdocs, labs in (("tasteset", "tasteset_native", lambda i: F.docs_taste(pd.read_csv(F.TASTE), i), {"FOOD"}),
                                    ("recipedb3", "recipedb3_published", lambda i: F.docs_rdb3(F.load_rdb3()[0], i), {"NAME"})):
        sp = json.loads((ROOT / "benchmark/ner/splits" / f"{ds}_split_v1.json").read_text())["indices"]
        counts = B.surface_counts(getdocs(sp["train"]))
        for part in ("dev", "calibration"):
            tot = cov = cov_unseen = n_unseen = cov_tail = n_tail = 0
            for text, spans in getdocs(sp[part]):
                for s, e, lab in spans:
                    if lab not in labs:
                        continue
                    k = B.stratum(lab, text[s:e], counts)
                    hit = norm(text[s:e]) in surf
                    tot += 1
                    cov += hit
                    if k == "unseen":
                        n_unseen += 1
                        cov_unseen += hit
                    if k == "tail":
                        n_tail += 1
                        cov_tail += hit
            out["datasets"][f"{ds}:{part}"] = {"gold_food_spans": tot, "ledger_exact_cover": round(cov / max(tot, 1), 4), "unseen_spans": n_unseen,
                                               "ledger_cover_of_unseen": round(cov_unseen / max(n_unseen, 1), 4), "tail_spans": n_tail, "ledger_cover_of_tail": round(cov_tail / max(n_tail, 1), 4)}
    out["verdict"] = "ALLOWED_AS_EXTERNAL_GAZETTEER" if not bad else "BLOCKED_PROVENANCE_LINK_TO_BENCHMARK_CORPORA"
    out["conditions"] = ["use only for features/calibrator, ablated with and without (feature removed -> measure)", "never include test surfaces when building or filtering the gazetteer",
                         "re-run this audit if the ledgers are rebuilt from any new corpus"]
    (ROOT / "reports/ner/alias_leakage_audit.json").write_text(json.dumps(out, indent=1) + "\n")
    lines = ["# Alias / concept leakage audit (S119, design contract D.7)", "", f"Verdict: **{out['verdict']}**", "",
             f"- Ledger surfaces (ING canonical + ALIAS, normalised): {len(surf)}", f"- Records whose provenance/crosswalks mention the benchmark corpora: {len(bad)}",
             f"- Provenance: {out['provenance_counts']}", "", "| split | gold FOOD/NAME spans | ledger exact cover | unseen spans | cover of unseen | tail spans | cover of tail |", "|---|---|---|---|---|---|---|"]
    for k, v in out["datasets"].items():
        lines.append(f"| {k} | {v['gold_food_spans']} | {v['ledger_exact_cover']} | {v['unseen_spans']} | {v['ledger_cover_of_unseen']} | {v['tail_spans']} | {v['ledger_cover_of_tail']} |")
    lines += ["", "TEST surfaces were not inspected. Coverage is an upper bound on what an external gazetteer could contribute.", "", "Conditions: " + "; ".join(out["conditions"])]
    (ROOT / "reports/ner/alias_leakage_audit.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
