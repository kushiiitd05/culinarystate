import sys
from fontTools.ttLib import TTFont
CPS={'plusminus':0xB1,'approx':0x2248,'micro':0xB5,'degree':0xB0,'Delta':0x394,'times':0xD7,
     'notequal':0x2260,'ge':0x2265,'le':0x2264,'sub2':0x2082,'sup2':0xB2,'dagger':0x2020,
     'emdash':0x2014,'endash':0x2013,'arrowR':0x2192,'oslash_ring':0x2298,'emptyset':0x2205,
     'bullet':0x2022,'section':0xA7,'middot':0xB7,'tilde':0x223C}
for p in sys.argv[1:]:
    f=TTFont(p,lazy=True); n=p.split('/')[-1]
    cm=set()
    for t in f['cmap'].tables:
        cm |= set(t.cmap.keys())
    have=[k for k,c in CPS.items() if c in cm]; miss=[k for k,c in CPS.items() if c not in cm]
    zeros=[g for g in f.getGlyphOrder() if g.lower().startswith('zero')]
    ones=[g for g in f.getGlyphOrder() if g.lower() in ('one','l','i','iota') or g.lower().startswith('one.')]
    print(f"\n### {n}")
    print(f"  total cmap codepoints: {len(cm)}")
    print(f"  HAVE: {have}")
    print(f"  MISS: {miss}")
    print(f"  zero glyph variants: {zeros}")
