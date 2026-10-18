#!/usr/bin/env python3
"""Route A AI pre-check: resolve Phenol-Explorer paper DOIs + OA links, rule-check every imported row,
build the human review pack (40 rows + reserve) for DEL-1's hand-verified literature rows.

  /opt/anaconda3/bin/python tools/precheck_route_a.py
Writes: SRC revisions (doi/url), EVD verification=AI_PRECHECKED (never HUMAN_VERIFIED),
registry/evidence/route_a_paper_precheck.csv, registry/evidence/human_review_pack_v1.csv,
doi/url/ai columns in verification_queue_ranked_v1.csv.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.doi_resolve import resolve  # noqa: E402
from culinarystate.evidence.precheck import check_row  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

AI = "claude-opus-5-5 via evidence.precheck@0.1 (rule checks)"
PACK_MAIN, PACK_RESERVE, PER_PAPER = 40, 30, 5
CACHE = ROOT / "data" / "raw" / "doi_resolve"
OUT = ROOT / "registry" / "evidence"

st = LedgerStore()
cond = {c["id"]: c for c in st.all_latest("COND")}
papers = {s["id"]: s for s in st.all_latest("SRC") if s["kind"] == "PAPER" and s["status"] == "ACTIVE"}

# 1. DOI resolution (cached) -> SRC revisions
res, src_w = {}, Counter()
for sid, s in papers.items():
    r = resolve(s["title"], CACHE)
    res[sid] = r
    if r.status == "RESOLVED" and s.get("doi") != r.doi:
        note = f"DOI resolved via Crossref (title match {r.match}); OA={r.is_oa} ({r.oa_status})."
        src_w[st.upsert({**s, "doi": r.doi, "url": r.oa_url or f"https://doi.org/{r.doi}", "notes": note})[0]] += 1
print("DOI:", Counter(r.status for r in res.values()), "| OA:", sum(bool(r.is_oa) for r in res.values()),
      "| SRC writes:", dict(src_w))

# 2. rule pre-check of every PE row -> AI_PRECHECKED
by_paper, evd_w, sugg = defaultdict(list), Counter(), Counter()
for e in st.all_latest("EVD"):
    if e["source_family_id"] != "PHENOL-EXPLORER-3.6" or e["status"] != "ACTIVE":
        continue
    chk = check_row(e, cond.get(e["process"].get("condition_id") or ""))
    sugg[chk["suggestion"]] += 1
    pid = next((s for s in e["provenance"]["source_ids"] if s in papers), None)
    by_paper[pid].append((e, chk))
    if e["verification"]["status"] in ("UNVERIFIED", "AI_PRECHECKED"):
        v = {"status": "AI_PRECHECKED", "ai_reviewer": AI,
             "notes": f"{chk['suggestion']}: " + ("; ".join(chk["flags"]) or "all rule checks passed")}
        evd_w[st.upsert({**e, "verification": v})[0]] += 1
print("pre-check:", dict(sugg), "| EVD writes:", dict(evd_w))

# 3. paper-level table
prow = []
for pid, items in by_paper.items():
    r, s = res.get(pid), papers.get(pid, {})
    n_ok = sum(c["suggestion"] == "LIKELY_CONFIRM" for _, c in items)
    prow.append({"src_id": pid, "citation": s.get("title"), "doi": r.doi if r else None, "is_oa": r.is_oa if r else None,
                 "oa_url": r.oa_url if r else None, "rows": len(items), "likely_confirm": n_ok,
                 "check_values": sum(c["suggestion"] == "CHECK_VALUES" for _, c in items),
                 "check_conditions": sum(c["suggestion"] == "CHECK_CONDITIONS" for _, c in items),
                 "ai_paper_suggestion": "PICK_FOR_HUMAN_PACK" if (r and r.is_oa and n_ok >= 3) else
                 ("NEEDS_LIBRARY_ACCESS" if r and r.doi else "RESOLVE_DOI_MANUALLY")})
papers_df = pd.DataFrame(prow).sort_values(["ai_paper_suggestion", "likely_confirm"], ascending=[False, False])
papers_df.to_csv(OUT / "route_a_paper_precheck.csv", index=False)

# 4. human review pack: OA papers, clean rows, distinct targets, ≤ PER_PAPER rows per paper
pack = []
for _, p in papers_df[papers_df.ai_paper_suggestion == "PICK_FOR_HUMAN_PACK"].iterrows():
    seen_t, n = set(), 0
    for e, c in sorted(by_paper[p.src_id], key=lambda x: (x[1]["suggestion"] != "LIKELY_CONFIRM",
                                                       not x[1]["has_temperature"], x[0]["id"])):
        if c["suggestion"] != "LIKELY_CONFIRM" or e["target"]["raw_name"] in seen_t or n >= PER_PAPER:
            continue
        seen_t.add(e["target"]["raw_name"])
        n += 1
        d = e["derived"]
        pack.append({
            "evd_id": e["id"], "paper_doi": p.doi, "paper_link": p.oa_url, "citation": p.citation,
            "food": e["matrix"]["raw_name"], "sample_after_processing": e["process"]["modifiers"].get("food_after_raw"),
            "process": "|".join(e["process"].get("steps", [])), "compound": e["target"]["raw_name"],
            "before_value": e["before"]["value"], "after_value": e["after"]["value"], "unit": e["after"]["unit"],
            "retention_factor": d["retention_factor"]["value"],
            "yield_factor": (d.get("yield_factor") or {}).get("value"),
            "ai_suggestion": c["suggestion"], "ai_notes": "all rule checks passed",
            "human_decision": "", "paper_locator": "", "corrected_after_value": "", "verifier": "",
            "verified_at": "", "human_notes": ""})
pack_df = pd.DataFrame(pack)
pack_df.insert(0, "pack", ["MAIN" if i < PACK_MAIN else "RESERVE" for i in range(len(pack_df))])
pack_df = pack_df.head(PACK_MAIN + PACK_RESERVE)
pack_path = OUT / "human_review_pack_v1.csv"
if pack_path.exists():                                     # never overwrite human input
    old = pd.read_csv(pack_path, dtype=str).fillna("")
    if (old[["human_decision", "verifier"]] != "").any().any():
        sys.exit(f"{pack_path} already has human decisions — not overwriting. Rename it to regenerate.")
pack_df.to_csv(pack_path, index=False)
print(f"pack: {len(pack_df)} rows from {pack_df.paper_doi.nunique()} OA papers -> {pack_path.relative_to(ROOT)}")

# 5. queue: Route A doi/url/ai columns
qp = OUT / "verification_queue_ranked_v1.csv"
q = pd.read_csv(qp)
title2 = {papers[p]["title"][:300]: p for p in papers}
for col in ("ai_suggested_decision", "ai_notes"):
    if col not in q:
        q[col] = ""
for i, row in q[q.route == "A_phenol_explorer"].iterrows():
    pid = title2.get(row.title)
    r = res.get(pid)
    if not r:
        continue
    pr = papers_df.set_index("src_id").loc[pid]
    q.loc[i, ["doi", "url", "open_access"]] = [r.doi or "", r.oa_url or (f"https://doi.org/{r.doi}" if r.doi else ""),
                                              bool(r.is_oa)]
    q.loc[i, "ai_suggested_decision"] = pr.ai_paper_suggestion
    q.loc[i, "ai_notes"] = f"{pr.likely_confirm}/{pr.rows} rows pass rule checks; {pr.check_values} need value check"
q.to_csv(qp, index=False)
print("queue updated:", q[q.route == "A_phenol_explorer"].ai_suggested_decision.value_counts().to_dict())
