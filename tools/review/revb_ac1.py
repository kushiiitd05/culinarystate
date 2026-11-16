import sys
sys.path.insert(0,'src')
from culinarystate.evidence.condition_agreement import gwet_ac1, cohen_kappa
from scipy.stats import beta
import math
# 1. reconstruct v4 pooled: A(Parv)=900 CORRECT; B(Kush)=895 CORRECT + 5 SBA
a=['CORRECT']*900
b=['CORRECT']*895+['SHOULD_BE_AMBIGUOUS']*5
print("v4 reconstruction: kappa",cohen_kappa(a,b),"AC1 q7",gwet_ac1(a,b,q=7),"AC1 q2",gwet_ac1(a,b,q=2),"raw",895/900)
# 2. equivalence table: marginals symmetric, dominant prevalence p, rest spread; po such that kappa=0.8 ; AC1 at that po
def pe_kappa(p): return p*p+(1-p)**2   # collapse rest to one category
def pe_ac1(p,q,spread=True):
    rest=1-p
    if spread:
        k=q-1
        s=p*(1-p)+k*(rest/k)*(1-rest/k)
    else:
        s=2*p*(1-p)
    return s/(q-1)
print("p, po(kappa=.80), AC1(q7,spread) at that po, AC1(q2) at that po, po at AC1=.80 (q7), kappa at AC1=.80 po")
for p in (0.5,0.7,0.8,0.9,0.95,0.98,0.99,0.995):
    pe=pe_kappa(p); po=pe+0.8*(1-pe)
    pe7=pe_ac1(p,7,True); pe2=pe_ac1(p,2,False)
    ac7=(po-pe7)/(1-pe7); ac2=(po-pe2)/(1-pe2)
    po_ac=pe7+0.8*(1-pe7); k_at=(po_ac-pe)/(1-pe)
    print(f"{p:5.3f} po_k={po:.4f} AC1q7={ac7:.4f} AC1q2={ac2:.4f} | po@AC1.8={po_ac:.4f} kappa there={k_at:.3f}  disagreements/900 allowed by kappa.8: {900*(1-po):.1f}; by AC1.8: {900*(1-po_ac):.1f}")
# 3. Clopper-Pearson one-sided 95% upper bound for x defects of n=100
print("CP one-sided 95% UCB, n=100")
for x in range(0,11):
    ub = 1.0 if x==100 else beta.ppf(0.95,x+1,100-x)
    print(x, round(ub,4))
print("n=50:",[ (x, round(beta.ppf(0.95,x+1,50-x),3)) for x in (0,1,2,3)])
# Wilson 5/100
sys.path.insert(0,'src')
from culinarystate.evaluation.paired_stats import wilson
print("wilson 5/100",wilson(5,100))
# 4. seeded controls: P(detect) needed
for m in (8,10,12,15):
    # prob reviewer who misses each planted error indep w.p. .1 detects >=m-1
    pass
