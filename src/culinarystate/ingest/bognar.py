"""Bognár (2002) BFE-R-02-03 Part 2 retention tables (pdftotext -layout) -> rows (X5).

Columns: a header line names cooking methods ("boil  steam  stew  fry in pan  bake in oven  deep fry"), the next line
gives a basis per column (A = food edible part, B = total dish incl. cooking liquid). Column -> method: a new method
starts at every "A" and at a "B" that follows a "B"; the group count must equal the method count, else the table is
skipped (logged). A row is kept only if it has exactly one value token ("0.90" or "-") per column.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

TABLE = re.compile(r"^Table (\d+):\s*(.*)$")
VALUE = re.compile(r"^(\d\.\d\d|-)$")
SKIP_TARGETS = {"fat uptake", "cooking salt"}          # not retention factors (g/100 g; % of salt added)
# preface: retention of these is incomplete -> "estimated" (grey background is lost in text extraction)
ESTIMATED = ("niacin", "biotin", "folate", "pantothenic", "vitamin e", "vitamin k", "vitamin b12", "fatty acid",
             "amino acid", "lysine", "methionine", "cystine", "cholesterol")


@dataclass(frozen=True)
class RetRow:
    table: int
    food_group: str
    description: str
    method: str
    basis: str
    constituent: str
    value: str
    line: int

    @property
    def estimated(self) -> bool:
        return any(k in self.constituent.lower() for k in ESTIMATED)


def method_groups(letters: list[str]) -> list[list[int]]:
    groups: list[list[int]] = []
    for i, x in enumerate(letters):
        if not groups or x == "A" or (x == "B" and letters[i - 1] == "B"):
            groups.append([])
        groups[-1].append(i)
    return groups


METHOD_PHRASES = ("fry in pan", "frying in pan", "fry in oven", "bake in oven", "deep fry", "stew, braise",
                  "pressure boil", "infusion with", "in oven", "boil", "steam", "stew", "braise", "roast", "grill",
                  "microwave", "bake", "fry")
METHOD_RE = re.compile(r"(?<![a-z])(" + "|".join(re.escape(m) for m in METHOD_PHRASES) + r")(?![a-z])", re.I)
VARIANT = re.compile(r"\b[a-c]\)|\*|whole|polished|pasta|flour")


def methods_of(header: str) -> list[str]:
    return [m.lower() for m in METHOD_RE.findall(header)]


def letters_of(line: str) -> list[str] | None:
    toks = re.sub(r"(?i)\bconstituents*\b", " ", line).split()
    return toks if toks and all(t in ("A", "B") for t in toks) else None


def parse_table(no: int, lines: list[tuple[int, str]]) -> tuple[list[RetRow], str | None]:
    first = next((k for k, (_, t) in enumerate(lines) if k > 1 and t.split() and t.split()[0][0].isalpha()
                  and len([x for x in t.split() if re.fullmatch(r"\d\.\d\d?", x)]) >= 1), None)
    if first is None:
        return [], f"table {no}: no data rows"
    head = lines[:first]
    bi = max((k for k, (_, t) in enumerate(head) if letters_of(t)), default=None)
    if bi is None:
        return [], f"table {no}: no A/B basis line"
    cand = [k for k in range(1, bi) if methods_of(head[k][1]) and "such as" not in head[k][1]
            and not head[k][1].lstrip().startswith("-") and "retention" not in head[k][1].lower()]
    if not cand:
        return [], f"table {no}: no method line"
    mline = cand[-1]
    marks = [t.split() for _, t in head[mline + 1: bi] if t.strip()]
    if any(len(set(m)) > 1 or not all(re.fullmatch(r"[a-z*]?\)|\*+|\d\)", x) for x in m) for m in marks):
        return [], f"table {no}: column-specific sub-variants (b)/c) etc.) — skipped"
    rf = next((k for k in range(1, mline) if head[k][1].strip().lower() == "retention factor"), None)
    above = [head[k][1].strip() for k in range((rf if rf is not None else mline) + 1, mline) if head[k][1].strip()]
    above = [a for a in above if a.lower() not in ("constituents", "constituentss")]
    if any(a.lower() not in ("fry/roast",) for a in above):
        return [], f"table {no}: product sub-columns {above} — skipped"
    mlines = [mline]
    meths, letters = methods_of(head[mlines[0]][1]), letters_of(head[bi][1])
    groups = method_groups(letters)
    if len(groups) != len(meths):
        return [], f"table {no}: {len(groups)} column groups vs {len(meths)} methods {meths}"
    col_method = {c: meths[g] for g, cols in enumerate(groups) for c in cols}
    title_lines, desc_lines = [lines[0][1]], []
    for _, t in lines[1:mlines[0]]:
        st = t.strip()
        if not st or "retention factor" in st.lower():
            continue
        (desc_lines if st.startswith("-") or desc_lines else title_lines).append(st)
    title = " ".join(title_lines)
    group_txt = re.sub(r"^.*?by (?:cooking|preparation)(?: of)?\s*", "", title).strip(" -")
    desc = " ".join(desc_lines).strip(" -")
    out = []
    for ln, t in lines[first:]:
        toks = t.split()
        vals = [x for x in toks if VALUE.match(x)]
        if len(vals) != len(letters) or not toks or not toks[0][0].isalpha():
            continue
        name = re.split(r"\s{2,}|\s\d\.\d\d|\s-\s", t.strip())[0]
        name = CANON.get(re.sub(r"\s*\d\)", "", name).strip().lower(), re.sub(r"\s*\d\)", "", name).strip())
        if not name or name.lower() in SKIP_TARGETS:
            continue
        for c, v in enumerate(vals):
            out.append(RetRow(no, group_txt, desc, col_method[c], letters[c], name, v, ln))
    return out, None


CANON = {"cystin": "Cystine", "carotenoide": "Carotenoids", "carotenoid": "Carotenoids", "phosphor": "Phosphorus",
         "other food": "Other food constituents", "other food constituents": "Other food constituents", "coffein": "Caffeine"}


def parse(text: str) -> tuple[list[RetRow], list[str]]:
    lines = [x.replace("\f", "") for x in text.split("\n")]   # pdftotext form feeds are page breaks, not lines
    start = next(i for i, t in enumerate(lines) if t.startswith("Part 2 : Average retention factors"))
    tables, cur = [], None
    for i in range(start, len(lines)):
        m = TABLE.match(lines[i])
        if m:
            if "retention" not in m.group(2).lower() and "retention" not in lines[i + 1].lower():
                cur = None
                continue
            cur = (int(m.group(1)), [(i + 1, lines[i])])
            tables.append(cur)
        elif cur is not None:
            cur[1].append((i + 1, lines[i]))
    rows, problems = [], []
    for no, ls in tables:
        r, p = parse_table(no, ls)
        rows += r
        if p:
            problems.append(p)
    return rows, problems
