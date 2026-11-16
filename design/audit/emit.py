import sys, itertools
sys.path.insert(0,'/private/tmp/claude-501/-Users-bournesmartasfuck-kush/41b21b0e-f0f0-476c-8476-ce50e99d1c2b/scratchpad')
from palette import *
NH=75.0; CLIPS=[]
def H(L,C,h,l=''):
    if clipped(L,C,h): CLIPS.append(l)
    return hexf(L,C,h)
SEM=['evidence-match','derived','scenario','ai-suggested','mismatch','unknown','error']
SH={'evidence-match':152,'derived':240,'scenario':72,'ai-suggested':305,'mismatch':25,'unknown':NH,'error':18}
DC={'evidence-match':0.100,'derived':0.082,'scenario':0.110,'ai-suggested':0.088,'mismatch':0.110,'unknown':0.0045,'error':0.115}
LC={'evidence-match':0.105,'derived':0.102,'scenario':0.093,'ai-suggested':0.145,'mismatch':0.155,'unknown':0.0060,'error':0.165}
DN={k:H(*v,l=k) for k,v in {'canvas':(0.1700,0.0060,NH),'surface-1':(0.2080,0.0070,NH),'surface-2':(0.2480,0.0080,NH),
 'surface-3':(0.2880,0.0085,NH),'border-subtle':(0.3250,0.0090,NH),'border-default':(0.3980,0.0100,NH),
 'border-strong':(0.5500,0.0110,NH),'text-muted':(0.6700,0.0120,80),'text-secondary':(0.7850,0.0140,80),
 'text-primary':(0.9050,0.0130,85),'focus':(0.8200,0.0500,215)}.items()}
LN={k:H(*v,l=k) for k,v in {'canvas':(0.9890,0.0035,95),'surface-1':(0.9720,0.0050,92),'surface-2':(0.9480,0.0065,90),
 'surface-3':(0.9220,0.0075,88),'border-subtle':(0.8850,0.0085,85),'border-default':(0.8150,0.0100,85),
 'border-strong':(0.5900,0.0130,80),'text-muted':(0.5050,0.0150,75),'text-secondary':(0.4100,0.0150,72),
 'text-primary':(0.2400,0.0120,70),'focus':(0.5200,0.1100,240)}.items()}
DFG={k:H(0.7900,DC[k],SH[k],'dfg'+k) for k in SEM}
DBG={k:H(0.2480,(0.028 if k!='unknown' else 0.0080),SH[k],'dbg'+k) for k in SEM}
DBD={k:H(0.5750,(0.062 if k!='unknown' else 0.0115),SH[k],'dbd'+k) for k in SEM}
LFG={k:H(0.4750,LC[k],SH[k],'lfg'+k) for k in SEM}
LBG={k:H(0.9560,(0.0200 if k!='unknown' else 0.0075),SH[k],'lbg'+k) for k in SEM}
LBD={k:H(0.5800,(0.085 if k!='unknown' else 0.0135),SH[k],'lbd'+k) for k in SEM}
DV={k:H(*v,l='dv'+k) for k,v in {'evidence-match':(0.8600,0.100,160),'derived':(0.7000,0.138,248),'scenario':(0.8000,0.142,68),
 'ai-suggested':(0.7400,0.055,300),'mismatch':(0.6600,0.142,22),'unknown':(0.5600,0.0050,NH)}.items()}
LV={k:H(*v,l='lv'+k) for k,v in {'evidence-match':(0.5400,0.115,160),'derived':(0.4500,0.120,248),'scenario':(0.6300,0.130,68),
 'ai-suggested':(0.5600,0.075,300),'mismatch':(0.5300,0.170,22),'unknown':(0.6400,0.0050,NH)}.items()}

print("GAMUT CLIPS:", CLIPS if CLIPS else "NONE")
def chk(name,N,FG,BG,BD,V):
    print(f"\n######## {name} — PASS/FAIL AUDIT")
    fails=[]
    for k in ('text-primary','text-secondary','text-muted'):
        for b in ('canvas','surface-1','surface-2','surface-3'):
            c=cr(N[k],N[b])
            if c<4.5: fails.append(f"{k} on {b} = {c:.2f}")
    for k in SEM:
        for b in ('canvas','surface-1','surface-2','surface-3'):
            c=cr(FG[k],N[b])
            if c<4.5: fails.append(f"{k}-fg on {b} = {c:.2f}")
        c=cr(FG[k],BG[k])
        if c<4.5: fails.append(f"{k}-fg on {k}-bg = {c:.2f}")
        for b in ('canvas','surface-1','surface-2'):
            c=cr(BD[k],N[b])
            if c<3: fails.append(f"{k}-border on {b} = {c:.2f} (<3)")
    for b in ('canvas','surface-1','surface-2'):
        c=cr(N['border-strong'],N[b])
        if c<3: fails.append(f"border-strong on {b} = {c:.2f} (<3)")
        c=cr(N['focus'],N[b])
        if c<3: fails.append(f"focus on {b} = {c:.2f} (<3)")
    for k in V:
        c=cr(V[k],N['canvas'])
        if c<3: fails.append(f"viz-{k} on canvas = {c:.2f} (<3)")
    print("  FAILS:", fails if fails else "none")
    print("\n  key ratios (vs canvas / surface-1 / surface-2 / surface-3):")
    for k in ('text-primary','text-secondary','text-muted'):
        print(f"   {k:<16} {N[k]}  "+" / ".join(f"{cr(N[k],N[b]):.2f}" for b in ('canvas','surface-1','surface-2','surface-3')))
    for k in SEM:
        print(f"   {k+'-fg':<16} {FG[k]}  "+" / ".join(f"{cr(FG[k],N[b]):.2f}" for b in ('canvas','surface-1','surface-2','surface-3'))+f"   | on own -bg {BG[k]}: {cr(FG[k],BG[k]):.2f}")
    for k in SEM:
        print(f"   {k+'-border':<16} {BD[k]}  "+" / ".join(f"{cr(BD[k],N[b]):.2f}" for b in ('canvas','surface-1','surface-2'))+f"   | vs own -bg {cr(BD[k],BG[k]):.2f}")
    print(f"   {'border-strong':<16} {N['border-strong']}  "+" / ".join(f"{cr(N['border-strong'],N[b]):.2f}" for b in ('canvas','surface-1','surface-2')))
    print(f"   {'focus':<16} {N['focus']}  "+" / ".join(f"{cr(N['focus'],N[b]):.2f}" for b in ('canvas','surface-1','surface-2')))
    for k in V: print(f"   viz-{k:<13} {V[k]}  vs canvas {cr(V[k],N['canvas']):.2f}")
    for kind in ('none','prot','deut','trit'):
        sim={k:(v if kind=='none' else simulate(v,kind)) for k,v in V.items()}
        pr=sorted((dE(sim[a],sim[b]),a,b) for a,b in itertools.combinations(V,2))
        print(f"   viz CVD {kind:<5} worst {pr[0][1]}/{pr[0][2]} dE={pr[0][0]:.1f}")
chk("DARK",DN,DFG,DBG,DBD,DV); chk("LIGHT",LN,LFG,LBG,LBD,LV)
print("\n\n################ CSS ################")
def blk(sel,N,FG,BG,BD,V):
    o=[f"{sel} {{"]
    for k,v in N.items(): o.append(f"  --cs-{k}: {v};")
    for k in SEM:
        o.append(f"  --state-{k}-fg: {FG[k]};  --state-{k}-bg: {BG[k]};  --state-{k}-border: {BD[k]};")
    for k in V: o.append(f"  --viz-{k}: {V[k]};")
    o.append("}")
    return "\n".join(o)
print(blk(":root, .light",LN,LFG,LBG,LBD,LV)); print(); print(blk(".dark",DN,DFG,DBG,DBD,DV))
