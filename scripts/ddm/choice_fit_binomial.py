"""Usage: python -m scripts.ddm.choice_fit_binomial (author 2026-11-12: does no sv fit pulse-trial choices better?). EXPLORATORY.
   Choice-only binomial NLL per mouse, cells condition (control / stage x pulse side) x coherence, from the fit browser
JSON (data counts and model simulations of the full-data fits, 30 reps). Pulse-only and all-trial families."""
import json, numpy as np, pandas as pd
B = json.load(open("dissemination/figures/qc/fit_browser_2026-11-11_v5.json"))
cols = B["columns"]; mice = B["mice"]
def tab(src):
    return pd.concat([pd.DataFrame(src[m]["rows"], columns=cols).assign(mouse=m) for m in mice]).set_index(["mouse", "cond", "coh"])
data = tab(B["data"])
k, n = (data.p * data.n).round(), data.n
ph = (k / n).clip(1e-9, 1 - 1e-9); sat = -(k * np.log(ph) + (n - k) * np.log(1 - ph))
rows = []
for fam, F in B["families"].items():
    if "[" in fam or not all(m in F for m in mice): continue
    s = tab(F).reindex(data.index)
    p = (s.p * s.n + 0.5) / (s.n + 1)
    p = p.fillna(0.5)
    nll = -(k * np.log(p) + (n - k) * np.log(1 - p))
    d = pd.DataFrame({"nll": nll, "dev": 2 * (nll - sat)}).reset_index()
    d["trials"] = np.where(d.cond == "control", "control", "pulse")
    for (tr, m), g in d.groupby(["trials", "mouse"]):
        rows.append({"family": fam, "group": F["group"].split(" (")[0], "label": F["label"], "trials": tr, "mouse": m,
                     "nll": g.nll.sum(), "dev": g.dev.sum(), "dev_le36": g[g.coh.abs() <= 36].dev.sum(), "cells": len(g)})
r = pd.DataFrame(rows)
r.to_csv("dissemination/figures/qc/choice_binomial_nll_2026-11-12.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
t = r.groupby(["trials", "family", "group", "label"])[["dev", "dev_le36"]].sum().reset_index()
print("cells per mouse:", r.groupby("trials").cells.sum().to_dict())
po = t[(t.trials == "pulse") & t.group.str.startswith("Pulse-only")].sort_values("dev")
print("\n== pulse-only fits, choices on PULSE trials (deviance = 2 x NLL above saturated; lower better)")
print(po.round(1).to_string(index=False))
pc = t[(t.trials == "control") & t.group.str.startswith("Pulse-only")].sort_values("dev")
print("\n== pulse-only fits, choices on CONTROL trials (predicted)"); print(pc.round(1).to_string(index=False))
pv = r[r.trials == "pulse"].pivot(index="mouse", columns="family", values="dev")
print()
for fe in ("linear", "power"):
    for v in ("primary", "leak", "urgency", "leak_urgency"):
        a, b = f"pulse_{fe}_{v}", f"pulse_{fe}_{'no_sv' if v == 'primary' else v + '_no_sv'}"
        dd = (pv[b] - pv[a]) / 2  # in NLL units
        print(f"NLL(no sv) - NLL(sv), {fe} {v}: sum {dd.sum():+.1f}; mice no-sv better {(dd < 0).sum()}/10 (by >2: {(dd < -2).sum()}), worse by >2: {(dd > 2).sum()}")
