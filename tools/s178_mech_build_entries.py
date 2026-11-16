"""S178 lane MECH: write registry/mech_entries_draft_v1.jsonl and its gate check (counts only). AI_DRAFTED.

    python tools/s178_mech_build_entries.py                      # write the JSONL + reports/s178/mech/mech_entries_check_S178.json
    python tools/s178_mech_build_entries.py --check-only         # verify the committed JSONL equals a fresh build, then check

The JSONL is rebuilt deterministically from the seed roster and the specs in ``mechanism/mech_entries.py``; nothing is
minted and nothing is written under ``ledgers/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.mechanism import mech_entries as ME  # noqa: E402
from culinarystate.mechanism import mech_registry_check as RC  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

CHECK_OUT = ROOT / "reports" / "s178" / "mech" / "mech_entries_check_S178.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ME.OUT_PATH))
    ap.add_argument("--check-out", default=str(CHECK_OUT))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    text = ME.dumps(ME.build())
    out = Path(a.out)
    if a.check_only:
        if out.read_text(encoding="utf-8") != text:
            print("MISMATCH: the JSONL differs from a fresh build", file=sys.stderr)
            return 2
    else:
        out.write_text(text, encoding="utf-8")
    entries = ME.load(out)
    rep = RC.check(entries)
    rep["entries_file"] = str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else out.name
    rep["entries_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    rep["builder_version"] = ME.BUILDER_VERSION
    D.assert_counts_only({k: v for k, v in rep.items() if k != "envelope_problems"})
    if rep["envelope_problems"]:
        print(json.dumps(rep["envelope_problems"], indent=1), file=sys.stderr)
    Path(a.check_out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.check_out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("entries", "screen_subset_entries", "G21_2", "G21_3", "G21_4", "G21_8")}))
    bad = rep["schema_invalid_entries"] or rep["semantic_problem_entries"] or rep["envelope_problems"] \
        or rep["asymmetric_links"] or rep["unresolved_links"] or rep["duplicate_keys"]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
