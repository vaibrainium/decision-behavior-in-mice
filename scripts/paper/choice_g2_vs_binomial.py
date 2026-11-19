import sys, numpy as np, pandas as pd
from scipy.stats import binom
from scipy.special import xlogy
c = pd.read_csv(sys.argv[1])
# one row per cell (condition x mouse x fold x family x seed) with both sides; collapse to cell
key = ["condition","mouse","fold","family","seed"]
side1 = c[c.side==1][key+["n","p_side"]].rename(columns={"n":"k","p_side":"p1"})
side0 = c[c.side==0][key+["n"]].rename(columns={"n":"n0"})
g = c.groupby(key).agg(choice_nll=("choice_nll","sum"), sat=("saturated_choice_nll","sum"),
                       rt_nll=("rt_nll","sum"), coh=("coherence","first"), pulse=("scheduled_pulse","first")).reset_index()
g = g.merge(side1,on=key).merge(side0,on=key); g["n"]=g.k+g.n0
g["G2"] = 2*(g.choice_nll-g.sat)
def eg2(n,p):  # exact E[G2] and Var under Binomial(n,p) with model p
    ks=np.arange(n+1); w=binom.pmf(ks,n,p)
    sat=xlogy(ks,ks/n)+xlogy(n-ks,(n-ks)/n); mod=ks*np.log(p)+(n-ks)*np.log(1-p)
    v=2*(sat-mod); return (w*v).sum(), (w*v*v).sum()-(w*v).sum()**2
ev=[eg2(int(n),p) for n,p in zip(g.n,g.p1)]; g["EG2"]=[e for e,_ in ev]; g["VG2"]=[v for _,v in ev]
g["obs_p"]=g.k/g.n; g["resid"]=g.obs_p-g.p1
for (fam,seed),d in g.groupby(["family","seed"]):
    z=(d.G2.sum()-d.EG2.sum())/np.sqrt(d.VG2.sum())
    print(f"{fam:28s} {seed}  cells={len(d)}  trials={d.n.sum()}  G2={d.G2.sum():7.0f}  E[G2|model]={d.EG2.sum():7.0f}  excess={d.G2.sum()-d.EG2.sum():6.0f} (z={z:5.1f})")
d=g[g.seed==g.seed.min()]
print("\ntrials per cell: median", d.n.median(), " IQR", d.n.quantile([.25,.75]).tolist())
print("\nper-mouse excess G2 (first seed):")
print(d.assign(ex=d.G2-d.EG2).pivot_table(index="mouse",columns="family",values="ex",aggfunc="sum").round(0))
# systematic? signed residual vs coherence: model too shallow => resid has same sign as coherence
d=d.assign(sgn=np.sign(d.coh))
print("\nmean (obs - model) P(choice=1), trial-weighted, by coherence sign:")
print(d.groupby(["family","sgn"]).apply(lambda x: np.average(x.resid,weights=x.n)).unstack().round(3))
print("\nby |coh| and family (signed toward coherence direction):")
d=d.assign(r_al=d.resid*np.where(d.coh<0,-1,1), ac=d.coh.abs())
print(d[d.coh!=0].groupby(["family","ac"]).apply(lambda x: np.average(x.r_al,weights=x.n)).unstack().round(3))
