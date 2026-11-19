"""Split held-out pulse choice excess G² (G² minus its exact Binomial(n, p_model) expectation) by cell type:
pulse direction relative to coherence (congruent / incongruent / zero coherence) x pulse timing (|sched_pulse_type|
1-3 = early/middle/late) x |coherence|, for sv and no-sv families. Input: 2026-11-19 score audit all_candidates cells.
Usage: .venv/bin/python scripts/paper/choice_g2_by_cell_type.py <cells.csv.gz> <out_dir>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import binom
from scipy.special import xlogy

c = pd.read_csv(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=False)
key = ["condition", "mouse", "fold", "family", "seed"]
g = c.groupby(key).agg(choice_nll=("choice_nll", "sum"), sat=("saturated_choice_nll", "sum"),
                       coh=("coherence", "first"), pulse=("scheduled_pulse", "first")).reset_index()
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
g["excess"] = g.G2 - g.EG2
g["sv"] = np.where(g.family.str.endswith("_no_sv"), "no_sv", "sv")
g["direction"] = np.select([g.coh == 0, np.sign(g.coh) == np.sign(g.pulse)], ["zero_coh", "congruent"], "incongruent")
g["timing"] = g.pulse.abs().map({1: "early", 2: "middle", 3: "late"}); g["abs_coh"] = g.coh.abs()
# signed residual toward the pulse direction: positive = data follow the pulse more than the model does
g["resid_pulse"] = (g.k / g.n - g.p1) * np.sign(g.pulse)
g.to_csv(out / "cells_typed.csv.gz", index=False)

def table(by):
    per_fam = g.groupby(["sv", "family"] + by).agg(excess=("excess", "sum"), VG2=("VG2", "sum"), n=("n", "sum"),
                                                     r=("resid_pulse", lambda s: np.average(s, weights=g.loc[s.index, "n"])))
    per_fam["z"] = per_fam.excess / np.sqrt(per_fam.VG2)
    t = per_fam.groupby(["sv"] + by).agg(trials=("n", "first"), mean_excess=("excess", "mean"),
                                         min_excess=("excess", "min"), max_excess=("excess", "max"),
                                         mean_z=("z", "mean"), pulse_follow_pp=("r", lambda s: 100 * s.mean()))
    t["excess_per_100_trials"] = 100 * t.mean_excess / t.trials
    return t.round(2)
for name, by in (("direction", ["direction"]), ("timing", ["timing"]), ("abs_coh", ["abs_coh"]),
                 ("direction_timing", ["direction", "timing"]), ("direction_abs_coh", ["direction", "abs_coh"])):
    t = table(by); t.to_csv(out / f"by_{name}.csv"); print(f"\n== by {name} ==\n{t.to_string()}")
for tag, d in (("all", g), ("no_PSUIM7", g[g.mouse != "PSUIM7"])):
    t = d.groupby(["sv", "direction", "family"]).excess.sum().groupby(["sv", "direction"]).mean().unstack().round(1)
    print(f"\nmean excess by direction ({tag}):\n{t.to_string()}")
