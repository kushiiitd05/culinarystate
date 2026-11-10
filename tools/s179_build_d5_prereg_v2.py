"""S179: build reports/del5/d5_benchmark_preregistration_v2_DRAFT.md from the v1 draft and the S178 amendment draft
with the options of D-080 / D-081 (ksh and prv, AI under D-071). Mechanical: every old text must occur exactly once;
alternatives are deleted; D-D5-6 sidedness stays OPEN for the humans. Writes nothing else; v1 is never edited."""
import re, hashlib
from pathlib import Path
v1p = Path('reports/del5/d5_benchmark_preregistration_DRAFT.md')
v1 = v1p.read_text(encoding='utf-8')
assert hashlib.sha256(v1.encode()).hexdigest() == '53ad89b7c13db57800e4546efb2ccfe29cdb2ef617b49c462c8b78f51415aa6b'
am = Path('reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md').read_text(encoding='utf-8')
sec2 = am[am.index('## 2. Changes'):am.index('## 3. Power')]
fences = re.findall(r'```diff\n(.*?)```', sec2, re.S)
assert len(fences) == 12, len(fences)

def split(f):
    out = []
    for sub in f.split('@@\n'):
        ls = sub.rstrip('\n').split('\n')
        out.append(('\n'.join(l[1:] for l in ls if l[:1] in '- '), '\n'.join(l[1:] for l in ls if l[:1] in '+ ')))
    return out

hunks = []
for i, f in enumerate(fences):
    if i == 7:   # C6 old block (only '-')
        old = split(f)[0][0]
    elif i == 8: # H3-A new block (only '+')
        hunks.append((old, split(f)[0][1]))
    else:
        hunks.extend(split(f))

def resolve(t):
    rep = [
        (' [S30] / 30 [S60]', ''),
        (' (20 per block, 15 enter [S30] | 40 per block, 30 enter [S60]).', ' (20 per block, 15 enter).'),
        ('n = 30 [S30] | 60 [S60]', 'n = 30'),
        ('**Embedding [E5]:**', '**Embedding:**'),
        ('revision `<commit hash, filled from the local cache before\n  the lock; the lock may not be issued with this blank>`',
         'revision `f169b11e22de13617baa190a028a32f3493550b6`'),
        ('**B4 state block [K1]:**', '**B4 state block:**'),
        ('Ollama model digest `<sha256, filled before the lock>`',
         'Ollama model digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` (RUN-S179-PIN-001)'),
        ('seed `<integer, fixed before the lock>`, `num_predict` `<integer>`', 'seed `7`, `num_predict` `200`'),
        ('(C07) [F1]:**', '(C07):**'),
        ('[G-A] The S gold', 'The S gold'),
        ('blind [G-A];', 'blind;'),
        ('**Veto [H3-A]:**', '**Veto:**'),
        ('With blind human gold (G-A) this block', 'With blind human gold this block'),
        ('amended before any signature with the S178 options the\n9-10 Nov sitting chose (`reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md`).',
         'amended before any signature with the S178 options\n(`reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md`) as chosen in D-080 and D-081 (ksh and prv, AI\nunder D-071; not a human sitting); D-D5-6 (sidedness) is still open for the humans.'),
        ('`per_rung` = 10 [30 claims, the\n    consensus size] | 20 [60 claims])', '`per_rung` = 10, 30 claims)'),
    ]
    for a, b in rep:
        t = t.replace(a, b)
    # drop alternative-option sentences/paragraphs
    t = re.sub(r' \[BGE: [^\]]*\]', '', t)
    t = re.sub(r' \[K2: [^\]]*\]', '', t)
    t = re.sub(r' \[F2: [^\]]*\]', '', t)
    t = re.sub(r' \[G-B: [^\]]*\]', '', t)
    t = re.sub(r'\n\[G-B\] [^\n]*(?:\n(?![A-Z\[]|Every|P and)[^\n]*)*', '', t)
    return t

out = v1
for old, new in hunks:
    assert out.count(old) == 1, ('OLD NOT FOUND ONCE', old[:90])
    out = out.replace(old, resolve(new))
# sidedness: leave both, mark OPEN
side_old = 'i.e. at least 5 of 5, 6 of 6, 7 of 7 or 7 of 8, 8 of 9, 9 of 10 [one-sided, `alternative="greater"`] | 6 of 6,'
assert out.count(side_old) == 1
out = out.replace(side_old, '**[OPEN, D-D5-6: sidedness is a human choice (D-081); the lock may not be issued until one option is deleted]** i.e. at least 5 of 5, 6 of 6, 7 of 7 or 7 of 8, 8 of 9, 9 of 10 [one-sided, `alternative="greater"`] | 6 of 6,')
for bad in ('[S60]', '[S30]', '[K2', '[G-B', '[BGE', '[F2', '[E5]', '[K1]', '[F1]', '[G-A]', '[H3-A]', '<commit hash', '<sha256, filled', '<integer'):
    assert bad not in out, bad
hdr = ('<!-- v2 of the D5 pre-registration (S179). Built mechanically from the v1 draft (sha256 53ad89b7...) and the S178 '
       'amendment draft with the options of D-080 and D-081 by '
       'tools/s179_build_d5_prereg_v2.py. One option is still OPEN (D-D5-6 sidedness, human). Unsigned. -->\n')
OUT = Path('reports/del5/d5_benchmark_preregistration_v2_DRAFT.md')


def build() -> str:
    return hdr + out


if __name__ == '__main__':
    OUT.write_text(build(), encoding='utf-8')
    print('hunks', len(hunks), 'chars', len(out))
