#!/usr/bin/env python
"""Build the Step 07.A-R1 condition-audit packet (reports/step07/07A_R1_preregistration_DRAFT.md §2). DRAFT.

Reads COND and EVD (read only), excludes every condition in the issued v4 packet, selects 100 fresh conditions
with the R1 seed, and writes two copies to annotation/condition_audit/ (git-ignored: raw third-party strings) plus
a counts-only manifest. Refuses to overwrite anything. Before writing it rebuilds the v4 rows from the v4
condition ids with the same module and requires them to equal the issued v4 packet (display unchanged).

    python tools/step07ar_build_packet.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evidence import condition_audit_packet as P  # noqa: E402
from culinarystate.evidence import condition_normalizer as N  # noqa: E402

LED = ROOT / "ledgers/data"
ADIR = ROOT / "annotation/condition_audit"
V4 = ADIR / "condition_audit_packet_100_v4_Kush.csv"
OUT = {who: ADIR / f"condition_audit_packet_100_R1_{who}.csv" for who in ("Kush", "Parv")}
MANIFEST = ROOT / "reports/step07/07A_R1_packet_manifest.json"


def latest(name: str) -> dict:
    d = {}
    with open(LED / f"{name}.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                d[r["id"]] = r
    return d


def read_csv(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _s(v) -> str:
    return "" if v is None else str(v)


def main() -> int:
    if any(p.exists() for p in (*OUT.values(), MANIFEST)):
        sys.exit("refusing to overwrite an existing R1 packet or manifest")
    if subprocess.run([sys.executable, str(ROOT / "tools/step07hr_freeze.py"), "--verify"],
                      capture_output=True, text=True).stdout.strip().splitlines()[-1:] != ["FREEZE INTACT"]:
        sys.exit("normalizer freeze check failed: refusing to build")
    fp = N.fingerprint()
    fp12 = fp["combined_sha256"][:12]
    cond, evd = latest("COND"), latest("EVD")
    fam, ctx = P.evd_context(evd)
    v4 = read_csv(V4)
    if {r["normalizer_fingerprint_12"] for r in v4} != {fp12}:
        sys.exit("v4 packet fingerprint differs from the current normalizer")
    mism = [r["audit_id"] for r in v4
            if any(_s(P.build_row(int(r["audit_id"][3:]), r["stratum"], r["condition_id"], cond[r["condition_id"]],
                                  fam, ctx, fp12)[c]) != r[c] for c in P.COLS)]
    if mism:
        sys.exit(f"v4 reproduction check failed on {len(mism)} rows: display differs, refusing to build")
    excluded = frozenset(r["condition_id"] for r in v4)
    pool: dict[str, list[str]] = {}
    for cid in sorted(fam):
        if cid in cond:
            pool.setdefault(P.stratum(cond[cid]), []).append(cid)
    sample = P.select(pool, seed=P.SEED_R1, exclude=excluded)
    rows = [P.build_row(i, s, cid, cond[cid], fam, ctx, fp12) for i, (s, cid) in enumerate(sample, 1)]
    ADIR.mkdir(parents=True, exist_ok=True)
    sha = {}
    for who, path in OUT.items():
        with open(path, "x", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=P.COLS + P.REV)
            w.writeheader()
            w.writerows(rows)
        sha[who] = hashlib.sha256(path.read_bytes()).hexdigest()
    man = {**P.manifest(rows=rows, pool=pool, excluded=excluded, fingerprint=fp, packet_sha=sha),
           "v4_reproduction_check": "PASS_100_OF_100", "freeze_check": "FREEZE_INTACT"}
    with open(MANIFEST, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(man, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: man[k] for k in ("n", "selected_by_stratum", "source_family_counts", "excluded_count",
                                          "v4_reproduction_check")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
