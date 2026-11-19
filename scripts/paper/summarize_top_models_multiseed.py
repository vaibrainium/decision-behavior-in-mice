"""Summarize the multi-seed top-model rescore: reproduction against the 2026-11-19 audit, per-seed totals and
paired family differences (mean, seed SD, range), with and without PSUIM7.
Usage: .venv/bin/python scripts/paper/summarize_top_models_multiseed.py <rescore dir>"""
import sys
from itertools import combinations
from pathlib import Path
import numpy as np, pandas as pd

d = Path(sys.argv[1]); audit = Path("dissemination/paper_accumulation/draft_2026-11-15/pulse_score_audit_2026-11-19")
cells = pd.read_csv(d / "cells.csv.gz")
cells["total"] = cells.choice_nll + cells.rt_nll + cells.penalty
old = pd.concat([pd.read_csv(f).assign(total=lambda x: x.choice_nll + x.rt_nll + x.penalty)
                 .groupby(["family", "seed"]).total.sum() for f in (audit / "cells.csv.gz", audit / "all_candidates/cells.csv.gz")])
old = old.groupby(level=[0, 1]).agg(["min", "max"])
assert (old["max"] - old["min"]).max() < 1e-6, "audit files disagree with each other"
old = old["min"]
new = cells.groupby(["family", "seed"]).total.sum()
both = pd.concat({"new": new, "audit": old}, axis=1).dropna()
print("reproduction (max |new - audit|):", float((both.new - both.audit).abs().max()), "over", len(both), "family-seed pairs")
rows = []
for tag, c in (("all", cells), ("no_PSUIM7", cells[cells.mouse != "PSUIM7"])):
    t = c.groupby(["family", "seed"]).agg(total=("total", "sum"), choice=("choice_nll", "sum"), rt=("rt_nll", "sum")).reset_index()
    t.assign(subset=tag).to_csv(d / f"totals_{tag}.csv", index=False)
    w = t.pivot(index="seed", columns="family", values="total")
    print(f"\n== {tag}: total held-out NLL per seed ==\n{w.round(1).to_string()}\nmean {w.mean().round(1).to_dict()}\nSD {w.std().round(1).to_dict()}")
    for a, b in combinations(w.columns, 2):
        diff = w[a] - w[b]
        rows.append(dict(subset=tag, a=a, b=b, mean=diff.mean(), sd=diff.std(), min=diff.min(), max=diff.max(),
                         same_sign=int((np.sign(diff) == np.sign(diff.mean())).sum())))
p = pd.DataFrame(rows); p.to_csv(d / "paired_differences.csv", index=False)
print("\npaired differences a - b (negative = a better):\n", p.round(1).to_string(index=False))

# per-mouse paired differences against the best family by mean total (seed-averaged); seeds = Monte Carlo only
m = cells.groupby(["mouse", "family", "seed"]).total.sum().groupby(["mouse", "family"]).mean().unstack()
best = m.sum().idxmin()
dm = m.drop(columns=best).sub(m[best], axis=0)  # positive = best family better in that mouse
dm.to_csv(d / "per_mouse_vs_best.csv")
print(f"\nper-mouse (other - {best}), seed-averaged; positive favours {best}:\n{dm.round(1).to_string()}")
print("mice favouring best:", (dm > 0).sum().to_dict())
