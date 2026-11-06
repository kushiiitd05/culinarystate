#!/usr/bin/env python
"""Step 19 P1 agreement score after both commitments exist (S166; D-066). DRAFT_PENDING_H4.

    python tools/step19_p1_score.py --key-a <A sealed key> --key-b <B sealed key> \
        --labels-a annotation/gold/deep_gold_pilot_v1/A --labels-b <B label folder> --out reports/step19/<new>.json

Commitments default to the tracked registry/recipe_semantics/deep_gold_pilot_v1/commitments_<L>_P1.json. Refuses any
label file that differs from its commitment, writes ONE counts-only JSON (no recipe ids, keys, entity names or text)
and refuses to overwrite or to write in ledgers/, data/, exports/ or annotation/gold/. Labels are human-accepted AI
drafts (D-045 W2, D-060): the score is not a blind inter-annotator agreement and not a human gate.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation import pilot_p1_score as S  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

TRACKED = ROOT / "registry/recipe_semantics/deep_gold_pilot_v1"


def pp_error():
    from culinarystate.annotation import pilot_packets as pp
    return pp.PacketError


def _load(p: Path):
    return json.loads(Path(p).expanduser().read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("key-a", "key-b", "labels-a", "labels-b", "out"):
        ap.add_argument(f"--{name}", required=True, type=Path)
    ap.add_argument("--commitment-a", type=Path, default=TRACKED / "commitments_A_P1.json")
    ap.add_argument("--commitment-b", type=Path, default=TRACKED / "commitments_B_P1.json")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--salt-a", type=Path, help="A's private salt file: verifies the sealed key against its commitment")
    ap.add_argument("--salt-b", type=Path, help="B's private salt file")
    a = ap.parse_args(argv)
    try:
        verified = bool(a.salt_a and a.salt_b)
        if verified:
            from culinarystate.annotation import pilot_packets as pp
            probs = []
            for letter, key, salt in (("A", a.key_a, a.salt_a), ("B", a.key_b, a.salt_b)):
                line = (TRACKED / f"sealed_key_P1_{letter}.sha256").read_text(encoding="utf-8")
                probs += S.key_problems(_load(key), salt_hex=pp.read_salt(salt.expanduser(), repo_root=ROOT),
                                        tracked_line=line, letter=letter)
            if probs:
                raise S.ScoreError("; ".join(probs))
        rep = S.score(_load(a.key_a), _load(a.key_b), labels_a=a.labels_a.expanduser(), labels_b=a.labels_b.expanduser(),
                      commitment_a=_load(a.commitment_a), commitment_b=_load(a.commitment_b))
        rep["key_commitments_verified"] = verified
        D.write_report(a.out, rep, root=a.root)
    except (OSError, S.ScoreError, D.DryRunError, pp_error()) as exc:
        ap.error(str(exc))
    print(json.dumps({"output": str(a.out), "pairs": rep["pairs"], "replay_ok_pairs": rep["replay_ok_pairs"],
                      "event_f1_strict": rep["mean"]["event_f1_strict"], "label_basis": rep["label_basis"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
