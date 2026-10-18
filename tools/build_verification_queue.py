#!/usr/bin/env python3
"""Priority-1 deliverables: verification_queue_ranked_v1.csv, conflict_queue.csv, rejected_candidates.csv,
evidence_precheck_report.html (registry/evidence/ + reports/).

Route A — Phenol-Explorer publications already in EVD (primary studies): human checks values/conditions against
the original paper -> rows can become human-verified literature rows (DEL-1 needs ≥ 40).
Route B — OpenAlex gap candidates (papers for cells the databases do not cover).
Classes: VERIFY_NOW / STRONG_CANDIDATE / NEEDS_SOURCE / CONFLICT / REJECT. AI pre-check ≠ human verification.

  /opt/anaconda3/bin/python tools/build_verification_queue.py
"""
import html
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.eda.report import cell_key  # noqa: E402
from culinarystate.evidence.literature import GAP_QUERIES, harvest, precheck, to_candidate  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()[:120]


st = LedgerStore()
evd = [e for e in st.all_latest("EVD") if e["status"] == "ACTIVE"]
cond = {c["id"]: c for c in st.all_latest("COND")}
src = {s["id"]: s for s in st.all_latest("SRC")}

# ---------------- Route A: PE publications ranked by verifiable content
by_pub = defaultdict(list)
for e in evd:
    if e["origin_type"] == "PRIMARY_STUDY" and e.get("study_ids"):
        by_pub[e["independence_group"]].append(e)
rows = []
pe_titles = set()
for pub, es in by_pub.items():
    pub_src = next((src[s] for s in es[0]["provenance"]["source_ids"] if s in src and src[s]["kind"] == "PAPER"), None)
    title = pub_src["title"] if pub_src else pub
    pe_titles.add(norm_title(title))
    temp = sum(cond.get(e["process"]["condition_id"], {}).get("completeness_mask", {}).get("temperature")
               in ("MEASURED", "RANGE") for e in es)
    dur = sum(cond.get(e["process"]["condition_id"], {}).get("completeness_mask", {}).get("duration")
              in ("MEASURED", "RANGE") for e in es)
    linked = sum(bool(e["matrix"].get("ingredient_id")) for e in es)
    score = round(min(1.0, 0.4 * (temp + dur) / (2 * len(es)) + 0.3 * min(len(es), 20) / 20 + 0.3 * linked / len(es)), 3)
    cls = "VERIFY_NOW" if score >= 0.6 else "STRONG_CANDIDATE"
    rows.append({"route": "A_phenol_explorer", "class": cls, "score": score, "doi": "", "title": title[:300],
                 "year": pub_src.get("year") if pub_src else None, "evd_rows": len(es),
                 "rows_with_temperature": temp, "rows_with_duration": dur, "ing_linked_rows": linked,
                 "process": "|".join(sorted({s for e in es for s in e["process"].get("steps", [])}))[:120],
                 "target": "|".join(sorted({e["target"]["raw_name"] for e in es}))[:160],
                 "matrix": "|".join(sorted({e["matrix"]["raw_name"] for e in es}))[:160],
                 "evd_ids": "|".join(e["id"] for e in es[:50]), "reasons": "primary study already extracted; verify "
                 "values + conditions against paper", "open_access": "", "url": "", "human_status": "",
                 "verifier": "", "verified_at": "", "notes": ""})

# ---------------- Route B: OpenAlex gap candidates
cache = ROOT / "data" / "raw" / "openalex"
seen_doi, seen_title, rejected = set(), {}, []
for q in GAP_QUERIES:
    for w in harvest(q[0], cache):
        c = to_candidate(w, q)
        if c is None:
            continue
        nt = norm_title(c.title)
        if c.doi.lower() in seen_doi or nt in seen_title:
            continue
        seen_doi.add(c.doi.lower())
        seen_title[nt] = c.doi
        cls, score, reasons = precheck(c)
        if nt in pe_titles:
            cls, reasons = "STRONG_CANDIDATE", reasons + ["already in Phenol-Explorer (lineage duplicate)"]
        row = {"route": "B_openalex_gap", "class": cls, "score": score, "doi": c.doi, "title": c.title[:300],
               "year": c.year, "evd_rows": 0, "rows_with_temperature": "", "rows_with_duration": "",
               "ing_linked_rows": "", "process": c.process, "target": c.target, "matrix": c.matrix, "evd_ids": "",
               "reasons": "; ".join(reasons), "open_access": c.open_access, "url": c.oa_url or f"https://doi.org/{c.doi}",
               "human_status": "", "verifier": "", "verified_at": "", "notes": ""}
        (rejected if cls == "REJECT" else rows).append(row)

# ---------------- conflicts: same cell, opposite direction, independent groups
by_cell = defaultdict(list)
for e in evd:
    by_cell[cell_key(e, cond)].append(e)
conf = []
for k, es in by_cell.items():
    dirs = {e["derived"].get("direction") for e in es} & {"INCREASE", "DECREASE"}
    groups = {e.get("independence_group") for e in es}
    if len(dirs) == 2 and len(groups) > 1:
        rfs = [e["derived"].get("retention_factor", {}).get("value") for e in es]
        conf.append({"class": "CONFLICT", "matrix": k[0], "form": k[1], "steps": ">".join(k[2]), "target": k[3],
                     "n_rows": len(es), "n_groups": len(groups),
                     "rf_values": "|".join(f"{x:g}" for x in rfs if x is not None)[:200],
                     "evd_ids": "|".join(e["id"] for e in es), "human_status": "", "resolution": ""})

out = ROOT / "registry" / "evidence"
out.mkdir(parents=True, exist_ok=True)
order = {"VERIFY_NOW": 0, "STRONG_CANDIDATE": 1, "NEEDS_SOURCE": 2}
q = pd.DataFrame(rows)
q["_o"] = q["class"].map(order)
q = q.sort_values(["_o", "score", "evd_rows"], ascending=[True, False, False]).drop(columns="_o")
q.insert(0, "queue_rank", range(1, len(q) + 1))
q.to_csv(out / "verification_queue_ranked_v1.csv", index=False)
pd.DataFrame(conf).to_csv(out / "conflict_queue.csv", index=False)
pd.DataFrame(rejected).to_csv(out / "rejected_candidates.csv", index=False)

summ = q.groupby(["route", "class"]).size().unstack(fill_value=0)
top = q.head(40)
rowsh = "".join(f"<tr><td>{r.queue_rank}</td><td>{r['class']}</td><td>{r.score}</td><td>{html.escape(str(r.title)[:110])}"
                f"</td><td>{r.evd_rows}</td><td>{html.escape(str(r.target)[:60])}</td></tr>" for _, r in top.iterrows())
page = f"""<!doctype html><html><head><meta charset='utf-8'><title>Evidence precheck</title><style>
body{{font:14px/1.4 -apple-system,system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;background:#fff;color:#1f2328}}
table{{border-collapse:collapse}}td,th{{border-bottom:1px solid #d0d7de;padding:3px 8px;text-align:left;vertical-align:top}}
@media (prefers-color-scheme:dark){{body{{background:#0d1117;color:#e6edf3}}td,th{{border-color:#30363d}}}}</style></head><body>
<h1>Evidence pre-check report v1</h1><p>AI pre-check only — <b>not human verification</b>. Humans fill
<code>human_status/verifier/verified_at</code> in <code>registry/evidence/verification_queue_ranked_v1.csv</code>.</p>
<h2>Queue by route × class</h2>{summ.to_html()}
<p>Conflict cells (opposite directions across independent groups): <b>{len(conf)}</b>. Rejected (off-topic): <b>{len(rejected)}</b>.</p>
<h2>Top 40 to verify</h2><table><tr><th>#</th><th>class</th><th>score</th><th>title</th><th>EVD rows</th><th>targets</th></tr>{rowsh}</table>
<h2>How to verify a Route-A paper (≈10 min)</h2><ol><li>Open paper (DOI/title). <li>For each listed EVD row check matrix,
state, process, temperature/time, before/after value, unit, basis, table/figure. <li>Record HUMAN_VERIFIED / HUMAN_REJECTED
+ verifier + date; note corrections. <li>Verified rows are promoted to E1/E2 literature rows by tools (never by hand-editing the ledger).</ol>
</body></html>"""
(ROOT / "reports" / "evidence_precheck_report.html").write_text(page)
print(summ.to_string())
print(f"queue rows {len(q)}, conflicts {len(conf)}, rejected {len(rejected)}")
