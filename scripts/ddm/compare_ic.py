"""AIC and BIC of every fitted family, beside the held-out NLL (author 2026-11-11: "with aic bic"). EXPLORATORY.

Per mouse, from the full-data fit (joint: split "all"; pulse-only: "pulse"; control-only: "control"):
  AIC = 2 NLL + 2 k,  BIC = 2 NLL + k ln(n),  NLL = censored quantile QMLE (multinomial over choice / no response x
  data-quantile RT bins per cell), k = free parameters, n = trials fitted. Summed over the 10 mice (each mouse fitted
  separately).
NLL source (--rescored): the fit re-simulated at independent seeds (rescore_fits.py; mean over seeds; seed_sd = SD of
  the per-family sum across seeds, a Monte Carlo noise estimate). Without it, the stored train_nll, which is optimistic
  by a model-dependent amount (reports/2026-11-12-likelihood-check.md); the stored-based AIC/BIC are kept as
  *_stored columns for comparison.
Held-out NLL: sum of the 5 CV folds' test NLL (joint cv0-4, pulse-only pcv0-4), from the browser table.
Comparable only within one kind (same trials). Input: the fit browser data (nll table), which reads the fit files.

Usage: python -m scripts.ddm.compare_ic [--browser ...v5.json] [--rescored dissemination/figures/qc/rescored_nll_<date>.csv]
Outputs: dissemination/figures/qc/model_ic_{summary,per_mouse}_<date>[_rescored].csv
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
    ap.add_argument("--rescored", nargs="+")
    args = ap.parse_args()
    b = json.load(open(args.browser))
    lab = {f: (v["group"].split(" (")[0], v["label"]) for f, v in b["families"].items()}
    d = pd.DataFrame(b["nll"]).dropna(subset=["fitted_nll", "n_fitted", "k"])
    d = d.groupby("family").filter(lambda g: len(g) == len(b["mice"]))
    if "stored_fitted_nll" in d:  # browser data v6+: fitted_nll holds the rescored value, the stored one is kept aside
        d["fitted_nll"] = d.stored_fitted_nll.fillna(d.fitted_nll)
    d["aic_stored"] = 2 * d.fitted_nll + 2 * d.k
    d["bic_stored"] = 2 * d.fitted_nll + d.k * np.log(d.n_fitted)
    sd = None
    if args.rescored:
        r = pd.concat([pd.read_csv(f) for f in args.rescored], ignore_index=True)
        per = r.groupby(["family", "mouse"]).agg(nll=("nll", "mean"), choice_nll=("choice_nll", "mean"), rt_nll=("rt_nll", "mean"),
                                                 stored_check=("stored_nll", "first"), n_check=("n_train", "first"), k_check=("k", "first")).reset_index()
        d = d.merge(per, on=["family", "mouse"], how="inner", validate="one_to_one")
        assert np.allclose(d.stored_check, d.fitted_nll) and (d.n_check == d.n_fitted).all() and (d.k_check == d.k).all()
        d["optimism"] = d.nll - d.fitted_nll
        sd = r.groupby(["family", "seed"]).nll.sum().groupby("family").std()
    else:
        d["nll"] = d.fitted_nll
    d["aic"] = 2 * d.nll + 2 * d.k
    d["bic"] = 2 * d.nll + d.k * np.log(d.n_fitted)
    rows = []
    for kind, g in d.groupby("kind"):
        for c in ("aic", "bic", "heldout_nll"):
            if g[c].notna().all():
                p = g.pivot(index="mouse", columns="family", values=c)
                g = g.assign(**{f"best_{c}": g.mouse.map(p.idxmin(axis=1)) == g.family})
        extra = {c: (c, "sum") for c in ("choice_nll", "rt_nll", "optimism") if c in g}
        t = g.groupby("family").agg(kind=("kind", "first"), k=("k", "first"), n=("n_fitted", "sum"), nll=("nll", "sum"), nll_stored=("fitted_nll", "sum"),
                                    aic=("aic", "sum"), bic=("bic", "sum"), aic_stored=("aic_stored", "sum"), bic_stored=("bic_stored", "sum"),
                                    heldout=("heldout_nll", lambda s: s.sum(min_count=len(s))), **extra,
                                    **{f"mice_best_{c}": (f"best_{c}", "sum") for c in ("aic", "bic", "heldout_nll") if f"best_{c}" in g})
        if sd is not None:
            t["seed_sd"] = sd.reindex(t.index)
        for c in ("aic", "bic", "heldout", "aic_stored", "bic_stored"):
            t[f"d_{c}"] = t[c] - t[c].min()
            t[f"rank_{c}"] = t[c].rank().astype("Int64") if t[c].notna().all() else pd.NA
        rows.append(t)
    t = pd.concat(rows)
    t.insert(1, "group", [lab[f][0] for f in t.index])
    t.insert(2, "label", [lab[f][1] for f in t.index])
    t = t.reset_index().sort_values(["kind", "bic"])
    day, tag = date.today().isoformat(), "_rescored" if args.rescored else ""
    t.round(2).to_csv(OUT / f"model_ic_summary_{day}{tag}.csv", index=False)
    d.round(3).to_csv(OUT / f"model_ic_per_mouse_{day}{tag}.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
    cols = ["family", "k", "d_aic", "d_bic", "d_heldout", "d_bic_stored", "rank_aic", "rank_bic", "rank_heldout", "rank_bic_stored",
            "mice_best_bic", "mice_best_heldout_nll", "optimism", "seed_sd"]
    for kind, g in t.groupby("kind"):
        print(f"\n== {kind}")
        print(g[[c for c in cols if c in g]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
