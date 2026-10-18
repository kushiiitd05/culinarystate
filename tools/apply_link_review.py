#!/usr/bin/env python3
"""Turn the signed ingredient-link review into decisions that tools/link_evidence.py applies (RUNBOOK §4).

  /opt/anaconda3/bin/python tools/apply_link_review.py                     # decisions from filled rows only
  /opt/anaconda3/bin/python tools/apply_link_review.py --sign-as Kush --date 2026-10-18 --basis "..."
      fills EMPTY human_decision cells with the AI recommendation, ONLY on that human's explicit instruction
      (bulk sign-off of the AI pre-check; the basis text is stored per row).
Reads registry/evidence/evd_ingredient_link_review_AI_prechecked.csv; writes
registry/evidence/evd_ingredient_link_decisions.csv. Then run tools/link_evidence.py.
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.link_review import DATE, decide  # noqa: E402
from culinarystate.ledgers.common import HUMANS  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

EV = ROOT / "registry" / "evidence"
REVIEW, OUT = EV / "evd_ingredient_link_review_AI_prechecked.csv", EV / "evd_ingredient_link_decisions.csv"


def names(st: LedgerStore) -> dict:
    out = {norm(r["canonical_name"]): r["id"] for r in st.all_latest("ING") if r["status"] == "ACTIVE"}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en":
            out.setdefault(norm(a["normalized"]), a["ingredient_id"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sign-as")
    ap.add_argument("--date")
    ap.add_argument("--basis", default="")
    a = ap.parse_args()
    df = pd.read_csv(REVIEW, dtype=str).fillna("")
    for c in ("human_reviewer", "human_review_date", "human_signoff_basis"):
        if c not in df:
            df[c] = ""
    if a.sign_as:
        if a.sign_as not in HUMANS or not DATE.match(a.date or "") or not a.basis:
            sys.exit("--sign-as must be Kush or Parv, with --date YYYY-MM-DD and a --basis")
        empty = df.human_decision.str.strip() == ""
        df.loc[empty, "human_decision"] = df.loc[empty, "ai_review_decision"]
        df.loc[empty, ["human_reviewer", "human_review_date", "human_signoff_basis"]] = [a.sign_as, a.date, a.basis]
        df.to_csv(REVIEW, index=False)
        print(f"signed {int(empty.sum())} rows as {a.sign_as}")
    lex = names(LedgerStore())
    dec = pd.DataFrame([decide(r, lex) for r in df.to_dict("records")])
    dec = dec.merge(df[["matrix_raw", "source_family", "rows"]], on=["matrix_raw", "source_family"], how="left")
    dec.to_csv(OUT, index=False)
    st = Counter(dec.status)
    print(dict(st), "| EVD rows LINKED:", int(pd.to_numeric(dec[dec.status == "LINKED"].rows).sum()))
    if st["INVALID_SIGNOFF"] or st["INVALID_DECISION"]:
        sys.exit("invalid sign-off rows present; fix the review CSV")


if __name__ == "__main__":
    main()
