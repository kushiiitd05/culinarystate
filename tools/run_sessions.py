#!/usr/bin/env python3
"""DEL-3 scripted sessions: validate, replay, check expectations -> reports/del3/sessions_v1.md/json.

  /opt/anaconda3/bin/python tools/run_sessions.py
Contract count (plan AH6: ≥ 30) uses HUMAN_REVIEWED sessions only; AI_DRAFTED ones are engine tests.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.sessions import check_session, validate_session  # noqa: E402

docs = [json.loads(p.read_text()) for p in sorted((ROOT / "annotation" / "sessions").glob("SES-*.json"))]
results, invalid = [], {}
for d in docs:
    errs = validate_session(d)
    if errs:
        invalid[d.get("session_id", "?")] = errs
        continue
    results.append({**check_session(d), "scenario": d["scenario"], "status": d["provenance"]["status"]})
status = Counter(r["status"] for r in results)
reviewed_pass = sum(r["pass"] for r in results if r["status"] == "HUMAN_REVIEWED")
summary = {"sessions": len(docs), "invalid": invalid, "passed": sum(r["pass"] for r in results),
           "checks": sum(r["checks"] for r in results), "deterministic_replay": all(r["replay"]["deterministic"] for r in results),
           "by_status": dict(status), "by_scenario": dict(Counter(r["scenario"] for r in results)),
           "contract_count_reviewed_and_passing": reviewed_pass}
out = ROOT / "reports" / "del3"
out.mkdir(parents=True, exist_ok=True)
(out / "sessions_v1.json").write_text(json.dumps({"summary": summary, "results": results}, indent=1, default=str))
lines = ["# DEL-3 scripted sessions v1", "", *(f"- {k}: {v}" for k, v in summary.items()), "",
         f"Contract (≥ 30 reviewed): {reviewed_pass}/30 — AI_DRAFTED sessions need human review "
         "(`provenance.status` = HUMAN_REVIEWED, `reviewed_by` = name) before they count.", "",
         "| session | scenario | status | pass | checks | engine issues |", "|---|---|---|---|---|---|"]
lines += [f"| {r['session_id']} | {r['scenario']} | {r['status']} | {'✅' if r['pass'] else '❌ ' + '; '.join(r['failures'])} | "
          f"{r['checks']} | {len(r['issues'])} |" for r in results]
(out / "sessions_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines[:12]))
