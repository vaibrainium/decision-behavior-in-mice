"""Summarize choice_g2_control_training cells: excess G² over its exact Binomial(n, p_model) expectation per
family, mean over seeds, for pulse (in-sample) and control (out-of-sample) scoring.
Usage: .venv/bin/python scripts/paper/choice_g2_control_training_summary.py <dir with cells.csv.gz>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import binom
from scipy.special import xlogy

d = Path(sys.argv[1]); c = pd.read_csv(d / "cells.csv.gz"); c["G2"] = 2 * (c.choice_nll - c.sat); cache = {}
def eg2(n, p):
    if (n, p) not in cache:
        ks = np.arange(n + 1); w = binom.pmf(ks, n, p)
        v = 2 * (xlogy(ks, ks / n) + xlogy(n - ks, (n - ks) / n) - ks * np.log(p) - (n - ks) * np.log(1 - p))
        cache[n, p] = ((w * v).sum(), (w * v * v).sum() - (w * v).sum() ** 2)
    return cache[n, p]
ev = np.array([eg2(int(n), p) for n, p in zip(c.n, c.p1)]); c["EG2"], c["VG2"] = ev[:, 0], ev[:, 1]; c["excess"] = c.G2 - c.EG2
t = c.groupby(["scored", "family", "seed"]).agg(n=("n", "sum"), cells=("n", "size"), excess=("excess", "sum"), V=("VG2", "sum")).reset_index()
t["z"] = t.excess / np.sqrt(t.V)
f = t.groupby(["scored", "family"]).agg(n=("n", "first"), cells=("cells", "first"), excess=("excess", "mean"),
                                        seed_diff=("excess", lambda s: s.max() - s.min()), z=("z", "mean")).reset_index()
f["per100"] = 100 * f.excess / f.n
f.to_csv(d / "summary.csv", index=False)
c[c.scored == "control"].groupby(["mouse", "family", "seed"]).excess.sum().groupby("mouse").mean().to_csv(d / "control_excess_by_mouse.csv")
print(f.round(1).to_string(index=False))
