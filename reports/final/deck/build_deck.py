"""Build CulinaryState_final.pptx with the project Python and python-pptx."""
from pathlib import Path
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures_s180_2026-11-16"
OUT = Path(os.environ.get("CS_DECK_OUTPUT", str(HERE.parent / "CulinaryState_final.pptx")))

BG, INK = RGBColor(0xFC, 0xFB, 0xF9), RGBColor(0x23, 0x1E, 0x19)
BLUE, AMBER = RGBColor(0x1B, 0x36, 0xC4), RGBColor(0xC7, 0x78, 0x00)
SLATE, MUTED = RGBColor(0x5E, 0x5C, 0x59), RGBColor(0x6A, 0x64, 0x5B)
SURF, BORDER = RGBColor(0xF7, 0xF6, 0xF2), RGBColor(0xC5, 0xC2, 0xBB)
AMBER_BG, BLUE_BG, SLATE_BG = RGBColor(0xFB, 0xF3, 0xE6), RGBColor(0xEC, 0xEF, 0xFB), RGBColor(0xEC, 0xEA, 0xE5)
SERIF, SANS, MONO = "Georgia", "Helvetica Neue", "Menlo"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def new_slide(title, kicker=None):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    if kicker:
        text(s, kicker, 0.6, 0.32, 12, 0.3, size=11, color=MUTED, font=MONO)
    text(s, title, 0.6, 0.55, 12.1, 0.8, size=28, font=SERIF, color=INK)
    n = len(prs.slides)
    text(s, f"CulinaryState · Group 17 · {n}", 10.6, 7.08, 2.1, 0.3, size=9, color=MUTED,
         align=PP_ALIGN.RIGHT, font=MONO)
    return s


def text(s, content, x, y, w, h, size=16, color=INK, font=SANS, bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.1):
    """content: str or list of str / (str, dict) runs-per-paragraph."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = Inches(0.02)
    paras = content if isinstance(content, list) else [content]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align; para.line_spacing = spacing
        runs = p if isinstance(p, tuple) and isinstance(p[0], list) else None
        for seg in (runs[0] if runs else [p]):
            t, opt = (seg, {}) if isinstance(seg, str) else seg
            r = para.add_run(); r.text = t
            f = r.font; f.size = Pt(opt.get("size", size)); f.name = opt.get("font", font)
            f.bold = opt.get("bold", bold); f.color.rgb = opt.get("color", color)
    return tb


def R(*segs):
    """A paragraph made of runs: R("plain ", ("bold", {...}))."""
    return ([s for s in segs],)


def box(s, x, y, w, h, fill=SURF, line=BORDER, lw=1.0, shape=MSO_SHAPE.RECTANGLE):
    b = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb = fill
    b.line.color.rgb = line; b.line.width = Pt(lw); b.shadow.inherit = False
    return b


def labelled_box(s, x, y, w, h, body, fill=SURF, line=BORDER, lw=1.0, size=13, **kw):
    box(s, x, y, w, h, fill, line, lw)
    return text(s, body, x + 0.12, y + 0.08, w - 0.24, h - 0.16, size=size, **kw)


def caveat(s, body, x, y, w, h, size=12, head="LIMITATION"):
    box(s, x, y, w, h, AMBER_BG, AMBER, 2.0)
    text(s, head, x + 0.14, y + 0.08, w - 0.28, 0.25, size=9, color=AMBER, font=MONO, bold=True)
    text(s, body, x + 0.14, y + 0.33, w - 0.28, h - 0.4, size=size)


def source(s, body):
    text(s, "Source: " + body, 0.6, 6.92, 9.8, 0.5, size=8.5, color=MUTED, font=SANS)


def arrow(s, x1, y1, x2, y2, color=BORDER):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(1.5)
    ln = c.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return c


def table(s, rows, x, y, col_w, row_h=0.42, size=12, header_fill=SLATE_BG, fills=None):
    shp = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                             Inches(sum(col_w)), Inches(row_h * len(rows)))
    t = shp.table
    for j, w in enumerate(col_w):
        t.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            cell = t.cell(i, j); cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            opt = {}
            if isinstance(val, tuple):
                val, opt = val
            cell.text = ""
            p = cell.text_frame.paragraphs[0]; r = p.add_run(); r.text = val
            r.font.size = Pt(opt.get("size", size)); r.font.name = opt.get("font", SANS)
            r.font.bold = opt.get("bold", i == 0); r.font.color.rgb = opt.get("color", INK)
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if i == 0 else (
                (fills or {}).get((i, j), opt.get("fill", BG if i % 2 else SURF)))
    return t


def picture(s, name, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    path = Path(name)
    return s.shapes.add_picture(str(path if path.is_absolute() else FIG / path), Inches(x), Inches(y), **kw)

# ---------------------------------------------------------------- slides
from slides import build  # noqa: E402  (slide content lives in slides.py)
build(globals())
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
