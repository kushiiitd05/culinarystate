import json, sys
from collections import Counter
sys.path.insert(0, "src")
from culinarystate.evidence import condition_audit_packet as P
def latest(name):
    d = {}
    with open(f"ledgers/data/{name}.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line); d[r["id"]] = r
    return d
cond, evd = latest("COND"), latest("EVD")
fam, ctx = P.evd_context(evd)
c = Counter()
for cid in sorted(fam):
    if cid in cond:
        c[(P.stratum(cond[cid]), fam[cid])] += 1
for k in sorted(c): print(k, c[k])
print("total by family", Counter({f: v for (s, f), v in c.items()} ) )
tot = Counter()
for (s,f),v in c.items(): tot[f]+=v
print(dict(tot))
