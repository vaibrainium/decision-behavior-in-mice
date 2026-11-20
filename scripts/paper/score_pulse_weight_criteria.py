"""Criteria A / A2 as mapped in A3 (plan 2026-11-19-choice-misfit-followup) for the joint pulse-weight fits, from
score_pulse_weight_joint output. Rules as in score_pw_criteria, with: dNLL over all held-out trials of the joint folds
(pulse and control parts also reported); residual on held-out early low-coherence pulse cells; mechanism = pulse weight
(`noise_weight`) > 1; guardrail = choice excess G² on held-out control cells.
Usage: PYTHONPATH=/src .venv/bin/python -m scripts.paper.score_pulse_weight_criteria <dir>"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from scripts.paper.score_pulse_weight_joint import DDM, FAMILIES, PAIRS
from scripts.paper.score_pw_criteria import SPECIAL, eg2


def main(d):
    h = pd.read_csv(d / "cells.csv.gz")
    rep = pd.read_csv(d / "reproduction.csv"); rep["diff"] = rep.recomputed - rep.stored
    print("reproduction at seed 12345 (max |recomputed - stored| per fold):\n",
          rep[rep.seed == 12345].groupby("family")["diff"].agg(lambda s: s.abs().max()).round(3).to_string())
    h["nll"] = h.choice_nll + h.rt_nll + h.penalty
    h["part"] = np.where(h.scheduled_pulse == 0, "control", "pulse")
    tot = h.groupby(["family", "mouse", "seed"]).nll.sum().rename("nll").reset_index()
    part = h.groupby(["family", "mouse", "part", "seed"]).nll.sum().groupby(["family", "mouse", "part"]).mean().unstack()
    key = ["condition", "mouse", "fold", "family", "seed"]
    s1 = h[h.side == 1][key + ["n", "p_side", "coherence", "scheduled_pulse"]].rename(columns={"n": "k", "p_side": "p1"})
    s0 = h[h.side == 0][key + ["n"]].rename(columns={"n": "n0"})
    g = s1.merge(s0, on=key); g["n"] = g.k + g.n0
    el = g[(g.scheduled_pulse.abs() == 1) & g.coherence.abs().isin([0, 9, 18])].copy()
    el["r"] = (el.k - el.p1 * el.n) * np.sign(el.scheduled_pulse)
    resid = el.groupby(["family", "mouse", "seed"])[["r", "n"]].sum().pipe(lambda s: s.r / s.n).groupby(["family", "mouse"]).mean()
    ch = h.groupby(key).agg(choice_nll=("choice_nll", "sum"), sat=("saturated_choice_nll", "sum"), pulse=("scheduled_pulse", "first")).reset_index()
    ch = ch[ch.pulse == 0].merge(g[key + ["n", "p1"]], on=key)
    ch["excess"] = 2 * (ch.choice_nll - ch.sat) - [eg2(int(n), p) for n, p in zip(ch.n, ch.p1)]
    ctrl = ch.groupby(["family", "seed"]).excess.sum()
    ctrl_mouse = ch.groupby(["family", "mouse", "seed"]).excess.sum().groupby(["family", "mouse"]).mean()

    rows, summary = [], []
    for f, b in PAIRS.items():
        x = tot[tot.family == f].merge(tot[tot.family == b], on=["mouse", "seed"], suffixes=("", "_b"))
        x["d"] = x.nll - x.nll_b
        m = x.groupby("mouse").d.agg(mean="mean", sd="std").reset_index()
        m["improved"] = (m["mean"] < -2 * m["sd"]) & (m["mean"] < -2)
        m["improved_loose"] = (m["mean"] < 0) & (m["mean"].abs() > m["sd"])
        folder, variant, _ = FAMILIES[f]
        for i, r in m.iterrows():
            w_all = pickle.load(open(DDM / folder / f"{r.mouse}_{variant}_all.pkl", "rb"))["parameters"]["noise_weight"]
            w = [pickle.load(open(DDM / folder / f"{r.mouse}_{variant}_cv{k}.pkl", "rb"))["parameters"]["noise_weight"] for k in range(5)]
            m.loc[i, "w_all"], m.loc[i, "w_cv_median"] = w_all, np.median(w)
            m.loc[i, "up_weighted"] = w_all > 1 and sum(v > 1 for v in w) >= 3
            m.loc[i, "up_weighted_loose"] = np.median(w) > 1
            m.loc[i, "dNLL_pulse_part"] = part.loc[(f, r.mouse), "pulse"] - part.loc[(b, r.mouse), "pulse"]
            m.loc[i, "dNLL_control_part"] = part.loc[(f, r.mouse), "control"] - part.loc[(b, r.mouse), "control"]
            m.loc[i, "resid_new_pp"], m.loc[i, "resid_const_pp"] = 100 * resid[f, r.mouse], 100 * resid[b, r.mouse]
            m.loc[i, "ctrl_excess_new"], m.loc[i, "ctrl_excess_const"] = ctrl_mouse[f, r.mouse], ctrl_mouse[b, r.mouse]
        m.insert(0, "family", f); rows.append(m)
        rest = m[~m.mouse.isin(SPECIAL)]
        w8 = wilcoxon(rest["mean"]) if (rest["mean"] != 0).any() else None
        sp = m[m.mouse.isin(SPECIAL)].set_index("mouse")
        shrink = lambda s, k: abs(sp.loc[s, "resid_new_pp"]) <= k * abs(sp.loc[s, "resid_const_pp"])
        boot = np.random.default_rng(20261120).choice(rest["mean"].to_numpy(), (2000, len(rest)))
        lo, hi = np.quantile(np.median(boot, axis=1), [.025, .975])
        imp, impl = m[m.improved], m[m.improved_loose]
        cn, cb = ctrl[f], ctrl[b]
        summary.append(dict(
            family=f, constant=b, total_dNLL=m["mean"].sum(),
            pulse_part_dNLL=m.dNLL_pulse_part.sum(), control_part_dNLL=m.dNLL_control_part.sum(),
            c1_improved_mice=f"{int(m.improved.sum())}/10: {','.join(imp.mouse) or '-'}",
            c2_median_dNLL_8=rest["mean"].median(), c2_wilcoxon_p=w8.pvalue if w8 else np.nan,
            c2_pass=bool(w8 and w8.pvalue < .05 and rest["mean"].median() < 0),
            c3_pass=bool(all(sp.loc[s, "improved"] and shrink(s, .5) for s in SPECIAL)),
            c4_pass=bool(len(imp) and imp.up_weighted.all()), c4_detail=f"{int(imp.up_weighted.sum())}/{len(imp)} improving mice with w > 1",
            c5_ctrl_excess_new=cn.mean(), c5_ctrl_excess_const=cb.mean(), c5_const_seed_range=cb.max() - cb.min(),
            c5_pass=bool(cn.mean() - cb.mean() <= cb.max() - cb.min()),
            a2_1_improved_mice=f"{int(m.improved_loose.sum())}/10: {','.join(impl.mouse) or '-'}",
            a2_2_sign_count_8=f"{int((rest['mean'] < 0).sum())}/8 improved", a2_2_median_ci=f"{rest['mean'].median():.2f} [{lo:.2f}, {hi:.2f}]",
            a2_3_pass=bool(all(sp.loc[s, "improved_loose"] and shrink(s, .75) for s in SPECIAL)),
            a2_4=f"{int(impl.up_weighted_loose.sum())}/{len(impl)} loosely improving mice, fold median w > 1",
            a2_5_ctrl_change=cn.mean() - cb.mean(), a2_5_flag=bool(cn.mean() - cb.mean() > 2 * (cb.max() - cb.min()))))
    per_mouse = pd.concat(rows, ignore_index=True); per_mouse.to_csv(d / "criteria_per_mouse.csv", index=False)
    s = pd.DataFrame(summary); s.to_csv(d / "criteria_summary.csv", index=False)
    pd.set_option("display.width", 250)
    print("\n== per mouse ==\n", per_mouse.round(3).to_string(index=False))
    print("\n== criteria (A3 mapping) ==\n", s.round(3).T.to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
