import sys, math
sys.path.insert(0,'src')
from culinarystate.evaluation.paired_stats import mcnemar_exact, newcombe_paired, wilson
from scipy.stats import binom
print("== minimum discordant split reaching two-sided exact p<=0.05 ==")
for d in range(4,41):
    k=None
    for kk in range(0,d//2+1):
        if mcnemar_exact(kk,d-kk)<=0.05: k=kk
    print(d, "none" if k is None else f"{d-k}-{k}  (needs b-c >= {d-2*k})")
# power: n questions, each question discordant w.p. pd, given discordant B4-only-correct w.p. psi
def power(n,pd,psi,alpha=0.05):
    tot=0.0
    for d in range(n+1):
        pdw=binom.pmf(d,n,pd)
        if pdw<1e-14: continue
        for b in range(d+1):
            c=d-b
            if b>c and mcnemar_exact(b,c)<=alpha:
                tot+=pdw*binom.pmf(b,d,psi)
    return tot
print("== power single comparison (direction-correct, 2-sided exact alpha .05) ==")
for n in (15,20,30,40):
    print("n=",n)
    for pd in (0.2,0.3,0.4):
        row=[]
        for psi in (0.5,0.7,0.8,0.9,1.0):
            row.append(f"{power(n,pd,psi):.2f}")
        print(f"  pd={pd}: psi=.5/.7/.8/.9/1.0 -> "+" ".join(row))
# convert to accuracy: pB4=pa+b, pB1 = pa+c
print("== example: S block n=30; B4 acc .80 vs B1 .50 => discordant ~ .30+2*(overlap) ==")
# if a=.45,b=.35,c=.05,d=.15: pd=.40, psi=.875, diff .30
print(power(30,0.40,0.875))
# diff .20: a=.5,b=.25,c=.05 ,d=.2 => pd .30 psi .833
print("diff .20 pd.30:",power(30,0.30,0.25/0.30))
# diff .10: b=.15 c=.05 pd=.2 psi=.75
print("diff .10 pd.20:",power(30,0.20,0.75))
# IUT both: simulate dependent comparisons B4>B1 and B4>B2 -- use independent product as lower bound and min as upper
for n,pd,psi in ((30,0.4,0.875),(30,0.3,0.833),(15,0.4,0.875)):
    p=power(n,pd,psi); print("IUT bounds n",n,pd,psi,"upper(min)=",round(p,2),"if independent ~",round(p*p,2))
print("== Newcombe widths n=30 ==")
for (a,b,c,d) in ((14,10,1,5),(10,8,2,10),(15,6,3,6),(20,5,0,5),(12,4,4,10)):
    lo,hi=newcombe_paired(a,b,c,d); print((a,b,c,d), "diff=%.3f CI=(%.3f, %.3f) p=%.4f"%((b-c)/30,lo,hi,mcnemar_exact(b,c)))
