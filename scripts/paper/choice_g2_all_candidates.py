"""Choice G² vs exact binomial expectation for every pulse-only family in the 2026-11-19 score audit
(all_candidates/cells.csv.gz, seed 12345), with and without PSUIM7, plus the slope residual pattern.
Usage: .venv/bin/python scripts/paper/choice_g2_all_candidates.py <cells.csv.gz> <out_dir>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import binom
from scipy.special import xlogy

c = pd.read_csv(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=False)
key = ["condition", "mouse", "fold", "family", "seed"]
g = c.groupby(key).agg(choice_nll=("choice_nll", "sum"), sat=("saturated_choice_nll", "sum"), rt_nll=("rt_nll", "sum"),
                       coh=("coherence", "first")).reset_index()
s1 = c[c.side == 1][key + ["n", "p_side"]].rename(columns={"n": "k", "p_side": "p1"})
s0 = c[c.side == 0][key + ["n"]].rename(columns={"n": "n0"})
g = g.merge(s1, on=key).merge(s0, on=key); g["n"] = g.k + g.n0
g["G2"] = 2 * (g.choice_nll - g.sat)
cache = {}
def eg2(n, p):
    if (n, p) not in cache:
        ks = np.arange(n + 1); w = binom.pmf(ks, n, p)
        v = 2 * (xlogy(ks, ks / n) + xlogy(n - ks, (n - ks) / n) - ks * np.log(p) - (n - ks) * np.log(1 - p))
        cache[n, p] = ((w * v).sum(), (w * v * v).sum() - (w * v).sum() ** 2)
    return cache[n, p]
ev = np.array([eg2(int(n), p) for n, p in zip(g.n, g.p1)]); g["EG2"], g["VG2"] = ev[:, 0], ev[:, 1]
g["resid"] = (g.k / g.n - g.p1) * np.where(g.coh < 0, -1, 1)  # toward coherence direction
g.to_csv(out / "cells_g2.csv.gz", index=False)
def summ(d):
    t = d.groupby("family").agg(G2=("G2", "sum"), EG2=("EG2", "sum"), VG2=("VG2", "sum"), choice_nll=("choice_nll", "sum"),
                                rt_nll=("rt_nll", "sum"), n=("n", "sum"))
    t["excess"] = t.G2 - t.EG2; t["z"] = t.excess / np.sqrt(t.VG2); t["total_nll"] = t.choice_nll + t.rt_nll
    for col in ("excess", "choice_nll", "total_nll"):
        t["rank_" + col] = t[col].rank().astype(int)
    return t.sort_values("excess")
for tag, d in (("all", g), ("no_PSUIM7", g[g.mouse != "PSUIM7"])):
    t = summ(d); t.to_csv(out / f"summary_{tag}.csv")
    print(f"\n== {tag} ==\n", t[["n", "excess", "z", "choice_nll", "rt_nll", "total_nll", "rank_excess", "rank_total_nll"]].round(1).to_string())
sl = g[g.coh != 0].groupby(["family", g.coh.abs()]).apply(lambda x: np.average(x.resid, weights=x.n), include_groups=False).unstack()
sl.to_csv(out / "slope_residual_by_abs_coh.csv")
print("\n(obs - model) P(choice toward coherence), trial-weighted, pp:\n", (100 * sl).round(1).to_string())
