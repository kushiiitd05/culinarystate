import sys
from fontTools.ttLib import TTFont

GLYPH_TESTS = {
 'Delta':0x0394,'ring_oslash':0x2298,'dagger':0x2020,'check':0x2713,'cross':0x2717,
 'emdash':0x2014,'asterisk':0x002A,'degree':0x00B0,'micro':0x00B5,'approx':0x2248,
 'minus':0x2212,'plusminus':0x00B1,'arrowR':0x2192,'bullet':0x2022,'devanagari_ka':0x0915,
 'subscript2':0x2082,'superscript1':0x00B9,'infinity':0x221E,'notequal':0x2260,
}

for p in sys.argv[1:]:
    f = TTFont(p, lazy=True)
    name = p.split('/')[-1]
    feats=set()
    for tag in ('GSUB','GPOS'):
        if tag in f:
            t=f[tag].table
            if t.FeatureList:
                for fr in t.FeatureList.FeatureRecord: feats.add(fr.FeatureTag)
    axes=[]
    if 'fvar' in f:
        axes=[(a.axisTag,a.minValue,a.defaultValue,a.maxValue) for a in f['fvar'].axes]
    os2=f['OS/2']; head=f['head']; upm=head.unitsPerEm
    cmap=f.getBestCmap()
    hmtx=f['hmtx']
    digits=[cmap.get(ord(c)) for c in '0123456789']
    widths=sorted({hmtx[g][0] for g in digits if g})
    tabular = len(widths)==1
    # glyph coverage
    missing=[k for k,cp in GLYPH_TESTS.items() if cp not in cmap]
    xh = getattr(os2,'sxHeight',0); ch=getattr(os2,'sCapHeight',0)
    print(f"\n### {name}  upm={upm}")
    print(f"  axes: {axes if axes else 'static'}")
    print(f"  x-height={xh} ({xh/upm:.3f} em)  cap-height={ch} ({ch/upm:.3f} em)  xh/cap={xh/ch:.2f}" if ch else f"  x-height={xh}")
    print(f"  digit widths={widths} default-tabular={tabular}")
    print(f"  num/figure feats: {sorted(t for t in feats if t in ('tnum','pnum','onum','lnum','zero','frac','sups','subs','salt','ss01','ss02','ss03','ss04','ss05','cv01','cv02','case','dnom','numr'))}")
    print(f"  all feats: {sorted(feats)}")
    print(f"  glyphs missing: {missing if missing else 'none of tested'}")
