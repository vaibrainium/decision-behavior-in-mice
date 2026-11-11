"""AIC and BIC of every fitted family, beside the held-out NLL (author 2026-11-11: "with aic bic"). EXPLORATORY.

Per mouse, from the full-data fit (joint: split "all"; pulse-only: "pulse"; control-only: "control"):
  AIC = 2 NLL + 2 k,  BIC = 2 NLL + k ln(n),  NLL = censored quantile QMLE (multinomial over choice / no response x
  data-quantile RT bins per cell), k = free parameters, n = trials fitted. Summed over the 10 mice (each mouse fitted
  separately). Caveat: the bin probabilities are simulated (15 reps), so NLL carries Monte Carlo noise.
Held-out NLL: sum of the 5 CV folds' test NLL (joint cv0-4, pulse-only pcv0-4), from the same table.
Comparable only within one kind (same trials). Input: the fit browser data (nll table), which reads the fit files.

Usage: python -m scripts.ddm.compare_ic [--browser dissemination/figures/qc/fit_browser_2026-11-11_v5.json]
Outputs: dissemination/figures/qc/model_ic_{summary,per_mouse}_<date>.csv
"""

import argparse
import json
from datetime import date

import numpy as np
import pandas as pd

from scripts.ddm.pulse_psychometric import OUT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser", default=str(OUT / "fit_browser_2026-11-11_v5.json"))
    b = json.load(open(ap.parse_args().browser))
    lab = {f: (v["group"].split(" (")[0], v["label"]) for f, v in b["families"].items()}
    d = pd.DataFrame(b["nll"]).dropna(subset=["fitted_nll", "n_fitted", "k"])
    d = d.groupby("family").filter(lambda g: len(g) == len(b["mice"]))
    d["aic"] = 2 * d.fitted_nll + 2 * d.k
    d["bic"] = 2 * d.fitted_nll + d.k * np.log(d.n_fitted)
    rows = []
    for kind, g in d.groupby("kind"):
        for c in ("aic", "bic", "heldout_nll"):
            if g[c].notna().all():
                p = g.pivot(index="mouse", columns="family", values=c)
                g = g.assign(**{f"best_{c}": g.mouse.map(p.idxmin(axis=1)) == g.family})
        t = g.groupby("family").agg(kind=("kind", "first"), k=("k", "first"), n=("n_fitted", "sum"), nll=("fitted_nll", "sum"),
                                    aic=("aic", "sum"), bic=("bic", "sum"), heldout=("heldout_nll", lambda s: s.sum(min_count=len(s))),
                                    **{f"mice_best_{c}": (f"best_{c}", "sum") for c in ("aic", "bic", "heldout_nll") if f"best_{c}" in g})
        for c in ("aic", "bic", "heldout"):
            t[f"d_{c}"] = t[c] - t[c].min()
            t[f"rank_{c}"] = t[c].rank().astype("Int64") if t[c].notna().all() else pd.NA
        rows.append(t)
    t = pd.concat(rows)
    t.insert(1, "group", [lab[f][0] for f in t.index])
    t.insert(2, "label", [lab[f][1] for f in t.index])
    t = t.reset_index().sort_values(["kind", "bic"])
    day = date.today().isoformat()
    t.round(2).to_csv(OUT / f"model_ic_summary_{day}.csv", index=False)
    d.round(3).to_csv(OUT / f"model_ic_per_mouse_{day}.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
    cols = ["family", "k", "d_aic", "d_bic", "d_heldout", "rank_aic", "rank_bic", "rank_heldout", "mice_best_aic", "mice_best_bic", "mice_best_heldout_nll"]
    for kind, g in t.groupby("kind"):
        print(f"\n== {kind}")
        print(g[[c for c in cols if c in g]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
