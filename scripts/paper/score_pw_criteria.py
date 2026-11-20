"""Evaluate the pre-registered criteria A (plan 2026-11-19-choice-misfit-followup) on score_pw_fits output.
  1 mouse improved: mean over seeds of dNLL (new - constant, held-out pcv, summed over folds) < -2 x seed SD and < -2
  2 cohort (8 mice, not PSUIM6/7): two-sided Wilcoxon on per-mouse seed-mean dNLL, p < .05 and median dNLL < 0
  3 PSUIM6 and PSUIM7 both improved (rule 1) and each one's early low-coherence residual (early pulses, |coh| 0/9/18;
    trial-weighted (observed - model) P(follow pulse)) at most half the constant-gain fit's in absolute size
  4 mechanism: in improving mice gain_decay > 0 / leak_rate < 0 in the full pulse fit and in >= 3 of 5 pcv folds
  5 guardrail: control-trial choice excess G² (full fit, out of sample) does not rise above the constant-gain fit by
    more than the constant-gain fit's seed range (max - min)
Exploratory tier A2 (added 2026-11-20 before any output; decides next steps, never claims):
  1 dNLL < 0 and |dNLL| > 1 x seed SD; 2 sign count of 8, median with mouse-bootstrap 95% CI;
  3 |new residual| <= 0.75 |old|; 4 median over pcv folds on the primacy side; 5 flag if worse by > 2 x seed rangeUsage: .venv/bin/python -m scripts.paper.score_pw_criteria <score_pw_fits output dir>"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binom, wilcoxon
from scipy.special import xlogy

from scripts.paper.score_pw_fits import NEW, PAIRS

DDM = Path("/mnt/data/processed/ddm")
MECH = {"gain": ("gain_decay", 1), "leak": ("leak_rate", -1)}  # parameter, sign on the primacy side
SPECIAL = ["PSUIM6", "PSUIM7"]
cache = {}


def eg2(n, p):
    if (n, p) not in cache:
        ks = np.arange(n + 1); w = binom.pmf(ks, n, p)
        v = 2 * (xlogy(ks, ks / n) + xlogy(n - ks, (n - ks) / n) - ks * np.log(p) - (n - ks) * np.log(1 - p))
        cache[n, p] = (w * v).sum()
    return cache[n, p]


def main(d):
    h = pd.read_csv(d / "heldout/cells.csv.gz")
    rep = pd.read_csv(d / "heldout/reproduction.csv")
    rep["diff"] = rep.recomputed - rep.stored
    print("reproduction (recomputed - stored test NLL, per fold), by family:\n",
          rep.groupby("family")["diff"].agg(["mean", lambda s: s.abs().max()]).round(3).to_string())
    new = [f for f in PAIRS if f in set(h.family)]
    tot = h.groupby(["family", "mouse", "seed"])[["choice_nll", "rt_nll", "penalty"]].sum().sum(axis=1).rename("nll").reset_index()
    # per-condition residual toward the pulse (as choice_g2_by_cell_type)
    key = ["condition", "mouse", "fold", "family", "seed"]
    s1 = h[h.side == 1][key + ["n", "p_side", "coherence", "scheduled_pulse"]].rename(columns={"n": "k", "p_side": "p1"})
    s0 = h[h.side == 0][key + ["n"]].rename(columns={"n": "n0"})
    g = s1.merge(s0, on=key); g["n"] = g.k + g.n0
    early_low = g[(g.scheduled_pulse.abs() == 1) & g.coherence.abs().isin([0, 9, 18])].copy()
    early_low["r"] = (early_low.k - early_low.p1 * early_low.n) * np.sign(early_low.scheduled_pulse)
    resid = early_low.groupby(["family", "mouse", "seed"])[["r", "n"]].sum().pipe(lambda s: s.r / s.n) \
        .groupby(["family", "mouse"]).mean().rename("resid")
    c = pd.read_csv(d / "control/cells.csv.gz"); c = c[c.scored == "control"].copy()
    c["excess"] = 2 * (c.choice_nll - c.sat) - [eg2(int(n), p) for n, p in zip(c.n, c.p1)]
    ctrl = c.groupby(["family", "seed"]).excess.sum()
    ctrl_mouse = c.groupby(["family", "mouse", "seed"]).excess.sum().groupby(["family", "mouse"]).mean()

    rows, summary = [], []
    for f in new:
        b = PAIRS[f]
        x = tot[tot.family == f].merge(tot[tot.family == b], on=["mouse", "seed"], suffixes=("", "_b"))
        x["d"] = x.nll - x.nll_b
        m = x.groupby("mouse").d.agg(mean="mean", sd="std").reset_index()
        m["improved"] = (m["mean"] < -2 * m["sd"]) & (m["mean"] < -2)
        m["improved_loose"] = (m["mean"] < 0) & (m["mean"].abs() > m["sd"])
        folder, variant = NEW[f]
        pname, sign = MECH["gain" if "gain" in f else "leak"]
        for i, r in m.iterrows():
            full = pickle.load(open(DDM / folder / f"{r.mouse}_{variant}_pulse.pkl", "rb"))["parameters"][pname]
            folds = [pickle.load(open(DDM / folder / f"{r.mouse}_{variant}_pcv{k}.pkl", "rb"))["parameters"][pname] for k in range(5)]
            m.loc[i, f"{pname}_full"] = full
            m.loc[i, f"{pname}_pcv_median"] = np.median(folds)
            m.loc[i, "primacy_side"] = sign * full > 0 and sum(sign * v > 0 for v in folds) >= 3
            m.loc[i, "primacy_side_loose"] = sign * np.median(folds) > 0
            m.loc[i, "resid_new_pp"] = 100 * resid[f, r.mouse]
            m.loc[i, "resid_const_pp"] = 100 * resid[b, r.mouse]
            m.loc[i, "ctrl_excess_new"] = ctrl_mouse[f, r.mouse]
            m.loc[i, "ctrl_excess_const"] = ctrl_mouse[b, r.mouse]
        m.insert(0, "family", f); rows.append(m)
        rest = m[~m.mouse.isin(SPECIAL)]
        w = wilcoxon(rest["mean"]) if (rest["mean"] != 0).any() else None
        sp = m[m.mouse.isin(SPECIAL)].set_index("mouse")
        shrink = lambda s, k: abs(sp.loc[s, "resid_new_pp"]) <= k * abs(sp.loc[s, "resid_const_pp"])
        c3 = all(sp.loc[s, "improved"] and shrink(s, .5) for s in SPECIAL)
        e3 = all(sp.loc[s, "improved_loose"] and shrink(s, .75) for s in SPECIAL)
        boot = np.random.default_rng(20261120).choice(rest["mean"].to_numpy(), (2000, len(rest)))
        lo, hi = np.quantile(np.median(boot, axis=1), [.025, .975])
        impl = m[m.improved_loose]
        imp = m[m.improved]
        cn, cb = ctrl[f], ctrl[b]
        summary.append(dict(
            family=f, constant=b, total_dNLL=m["mean"].sum(),
            c1_improved_mice=f"{int(m.improved.sum())}/10: {','.join(imp.mouse) or '-'}",
            c2_median_dNLL_8=rest["mean"].median(), c2_wilcoxon_p=w.pvalue if w else np.nan,
            c2_pass=bool(w and w.pvalue < .05 and rest["mean"].median() < 0),
            c3_pass=bool(c3),
            c4_pass=bool(len(imp) and imp.primacy_side.all()), c4_detail=f"{int(imp.primacy_side.sum())}/{len(imp)} improving mice on primacy side",
            c5_ctrl_excess_new=cn.mean(), c5_ctrl_excess_const=cb.mean(), c5_const_seed_range=cb.max() - cb.min(),
            c5_pass=bool(cn.mean() - cb.mean() <= cb.max() - cb.min()),
            a2_1_improved_mice=f"{int(m.improved_loose.sum())}/10: {','.join(impl.mouse) or '-'}",
            a2_2_sign_count_8=f"{int((rest['mean'] < 0).sum())}/8 improved", a2_2_median_ci=f"{rest['mean'].median():.2f} [{lo:.2f}, {hi:.2f}]",
            a2_3_pass=bool(e3), a2_4=f"{int(impl.primacy_side_loose.sum())}/{len(impl)} loosely improving mice, fold median on primacy side",
            a2_5_ctrl_change=cn.mean() - cb.mean(), a2_5_flag=bool(cn.mean() - cb.mean() > 2 * (cb.max() - cb.min()))))
    per_mouse = pd.concat(rows, ignore_index=True); per_mouse.to_csv(d / "criteria_per_mouse.csv", index=False)
    s = pd.DataFrame(summary); s.to_csv(d / "criteria_summary.csv", index=False)
    pd.set_option("display.width", 250)
    print("\n== per mouse ==\n", per_mouse.round(3).to_string(index=False))
    print("\n== criteria A ==\n", s.round(3).T.to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
