#!/usr/bin/env python
"""S179: apply the S178 pre-signature amendment drafts to the three pre-registration DRAFT files, in place, with the
options of D-080 / D-081 / D-082 (ksh and prv, AI under D-071). The signature checkers bind the DRAFT paths
(`evaluation/frozen_guard.PREREG`, `evaluation/freeze_records.PREREG`), so the amended text must live there.

Mechanical and reproducible: the base text is read from git at the commit whose sha256 the amendment names; every old
text must occur exactly once; alternatives are deleted; open human choices stay visibly OPEN. Nothing is signed.

    /opt/anaconda3/bin/python tools/s179_apply_prereg_amendments.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIBE_LINE = ("as chosen in D-080 to D-083 (ksh and prv, AI under D-071; not a human sitting)")


def _d5_fix(t: str) -> str:
    rep = [
        (' [S30] / 30 [S60]', ''),
        (' (20 per block, 15 enter [S30] | 40 per block, 30 enter [S60]).', ' (20 per block, 15 enter).'),
        ('n = 30 [S30] | 60 [S60]', 'n = 30'),
        ('**Embedding [E5]:**', '**Embedding:**'),
        ('revision `<commit hash, filled from the local cache before\n  the lock; the lock may not be issued with this blank>`',
         'revision `f169b11e22de13617baa190a028a32f3493550b6`'),
        ('**B4 state block [K1]:**', '**B4 state block:**'),
        ('With blind human gold (G-A) this block', 'With blind human gold this block'),
        ('Ollama model digest `<sha256, filled before the lock>`',
         'Ollama model digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` (RUN-S179-PIN-001)'),
        ('seed `<integer, fixed before the lock>`, `num_predict` `<integer>`', 'seed `7`, `num_predict` `200`'),
        ('(C07) [F1]:**', '(C07):**'),
        ('[G-A] The S gold', 'The S gold'),
        ('blind [G-A];', 'blind;'),
        ('**Veto [H3-A]:**', '**Veto:**'),
        ('`per_rung` = 10 [30 claims, the\n    consensus size] | 20 [60 claims])', '`per_rung` = 10, 30 claims)'),
        ('amended before any signature with the S178 options the\n9-10 Nov sitting chose (',
         'amended before any signature with the S178 options\n('),
        ('_AMENDMENT_S178_DRAFT.md`). Until both humans sign', '_AMENDMENT_S178_DRAFT.md`) ' + SCRIBE_LINE +
         '; D-D5-6 (sign-test sidedness) is two-sided (D-083). Until both humans sign'),
    ]
    for a, b in rep:
        t = t.replace(a, b)
    for tag in ('BGE', 'K2', 'F2', 'G-B'):
        t = re.sub(r' \[' + tag + r': [^\]]*\]', '', t)
    t = re.sub(r'\n\[G-B\] [^\n]*(?:\n(?![A-Z\[]|Every|P and)[^\n]*)*', '', t)
    side = ('i.e. at least 5 of 5, 6 of 6, 7 of 7 or 7 of 8, 8 of 9, 9 of 10 [one-sided, `alternative="greater"`] | 6 of 6,\n'
            '    7 of 7, 8 of 8, 8 of 9, 9 of 10 [two-sided]. Fewer than 5 [one-sided] or 6 [two-sided] such questions: "cannot\n'
            '    be shown at this n".')
    if t.count(side) != 1:
        raise SystemExit("D5: sidedness text not found exactly once")
    t = t.replace(side, 'two-sided (`alternative="two-sided"`; D-D5-6, D-083), i.e. at least 6 of 6, 7 of 7, 8 of 8, 8 of 9,\n'
                        '    9 of 10. Fewer than 6 such questions: "cannot be shown at this n".')
    return t


def _d29_fix(t: str) -> str:
    t = t.replace('Amended before signature with the S178 options the 9-10 Nov sitting chose\n(',
                  'Amended before signature with the S178 options\n(')
    t = t.replace('_AMENDMENT_S178_DRAFT.md`). Until Kush signs', '_AMENDMENT_S178_DRAFT.md`) ' + SCRIBE_LINE +
                  '. Until Kush signs')
    t = t.replace(' [K-A]:**', ':**').replace(', B2 [K-A] and D5', ', B2 and D5')
    t = re.sub(r'\n   \[K-B instead: [^\]]*\]', '', t)
    return t


def _aa_fix(t: str) -> str:
    t = t.replace('Amended before any signature with the S178 options the 9-10 Nov sitting chose\n(',
                  'Amended before any signature with the S178 options\n(')
    t = t.replace('_AMENDMENT_S178_DRAFT.md`). Until both humans sign', '_AMENDMENT_S178_DRAFT.md`) ' + SCRIBE_LINE +
                  '. Until both humans sign')
    t = t.replace('\n[FW-A] Kush moves', '\n(a) Kush moves').replace('\n[FW-B] SIM-VAL rows', '\nand (b) SIM-VAL rows')
    t = t.replace('- **pH condition** [pH-A]:', '- **pH condition:**')
    t = re.sub(r' \[pH-B: [^\]]*\]', '', t)
    t = t.replace('the gate falls back to pH-C. [pH-C: no pH gate; the matrix-class list carries the acidity\n'
                  '  restriction and the report says "pH not gated".]',
                  'the gate falls back to: no pH gate; the matrix-class list carries the acidity restriction and the\n'
                  '  report says "pH not gated".')
    return t


DOCS = {
    "D5": dict(draft="reports/del5/d5_benchmark_preregistration_DRAFT.md",
               amend="reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md",
               base_sha="53ad89b7c13db57800e4546efb2ccfe29cdb2ef617b49c462c8b78f51415aa6b", base_commit="d2edac2",
               pair=(7, 8), fix=_d5_fix,
               must_not=('[S60]', '[S30]', '[K2', '[G-B', '[BGE', '[F2', '[E5]', '[K1]', '[F1]', '[G-A]', '[H3-A]',
                         '<commit hash', '<sha256, filled', '<integer', '9-10 Nov sitting', '[one-sided', 'OPEN, D-D5-6')),
    "D29": dict(draft="reports/step29/29diag_preregistration_DRAFT.md",
                amend="reports/step29/29diag_preregistration_AMENDMENT_S178_DRAFT.md",
                base_sha="b78704aeab3b4177ed3fea4f5b130e36a5cc2bdac06f371cee0e2965bd03f2a3", base_commit="1bcabf7",
                pair=None, fix=_d29_fix, must_not=('[K-A]', '[K-B', 'D3 = B-2', '9-10 Nov sitting')),
    "AA": dict(draft="reports/step10/aa_pilot_preregistration_DRAFT.md",
               amend="reports/step10/aa_pilot_preregistration_AMENDMENT_S178_DRAFT.md",
               base_sha="6233511902461d533b945e91cf4a07be16b60bc64e6b8a02e9531c16ad38eaab", base_commit="aebec7b",
               pair=None, fix=_aa_fix, must_not=('[FW-A]', '[FW-B]', '[pH-A]', '[pH-B', '[pH-C', '9-10 Nov sitting')),
}


def _split(f: str) -> list[tuple[str, str]]:
    out = []
    for sub in f.split('@@\n'):
        ls = sub.rstrip('\n').split('\n')
        out.append(('\n'.join(l[1:] for l in ls if l[:1] in '- '), '\n'.join(l[1:] for l in ls if l[:1] in '+ ')))
    return out


def base_text(cfg: dict) -> str:
    t = subprocess.run(["git", "show", f"{cfg['base_commit']}:{cfg['draft']}"], cwd=ROOT, capture_output=True,
                       check=True).stdout
    if hashlib.sha256(t).hexdigest() != cfg["base_sha"]:
        raise SystemExit(f"base text of {cfg['draft']} at {cfg['base_commit']} does not match the amendment's sha256")
    return t.decode("utf-8")


def build(name: str) -> str:
    cfg = DOCS[name]
    am = (ROOT / cfg["amend"]).read_text(encoding="utf-8")
    sec = am[am.index('## 2. Changes'):am.index('## 3.')]
    fences = re.findall(r'```diff\n(.*?)```', sec, re.S)
    hunks: list[tuple[str, str]] = []
    old = None
    for i, f in enumerate(fences):
        if cfg["pair"] and i == cfg["pair"][0]:
            old = _split(f)[0][0]
        elif cfg["pair"] and i == cfg["pair"][1]:
            hunks.append((old, _split(f)[0][1]))
        else:
            hunks.extend(_split(f))
    out = base_text(cfg)
    for o, n in hunks:
        if o == "":   # pure insertion (AA C5, "new §7 after §6"): placed just before the signature section
            anchor = "\n## Signatures"
            if out.count(anchor) != 1:
                raise SystemExit(f"{name}: insertion anchor not found exactly once")
            out = out.replace(anchor, "\n" + n + "\n" + anchor, 1)
            continue
        if out.count(o) != 1:
            raise SystemExit(f"{name}: old text not found exactly once: {o[:80]!r}")
        out = out.replace(o, n)
    out = cfg["fix"](out)
    for bad in cfg["must_not"]:
        if bad in out:
            raise SystemExit(f"{name}: unresolved {bad!r}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if a DRAFT differs from its build")
    a = ap.parse_args()
    bad = 0
    for name, cfg in DOCS.items():
        text = build(name)
        p = ROOT / cfg["draft"]
        if a.check:
            ok = p.read_text(encoding="utf-8") == text
            bad += not ok
            print(name, "OK" if ok else "DIFFERS")
        else:
            p.write_text(text, encoding="utf-8")
            print(name, "written", hashlib.sha256(text.encode()).hexdigest())
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
