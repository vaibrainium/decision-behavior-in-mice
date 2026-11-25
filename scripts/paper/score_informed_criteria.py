"""Evaluate the criteria of plans/2026-11-24-informed-guess-family.md on score_informed_fits output.
Tiers A and A2 as in score_pw_criteria (plans/2026-11-19-choice-misfit-followup), pair
pulse_norm_ugm_informed_no_sv vs pulse_norm_ugm_no_sv. Rules 1-3 and 5 are computed exactly as there. Rule 4 (mechanism)
is specific to this family: guess_w > 0.05 in the full "pulse" fit and in >= 3 of 5 pcv folds, in both PSUIM6 and PSUIM7
(A2: fold median > 0.05). Rule 6 (descriptive): fast (< 0.6 s) control accuracy by |coherence|, full fit, model vs data.
Outputs (in the score dir): criteria_per_mouse.csv, criteria_summary.csv, fast_control_accuracy.csv
Usage: OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.score_informed_criteria <score dir>"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from scripts.paper.score_informed_fits import NEW, PAIRS
from scripts.paper.score_pw_criteria import eg2

DDM = Path("/mnt/data/processed/ddm")
SPECIAL = ["PSUIM6", "PSUIM7"]
THRESH = 0.05


def fast_control_accuracy(families):
    from scripts.ddm.fit_mouse_ddm import select
    from scripts.ddm.primacy import make_model
    from scripts.ddm.pulse_joint_signatures import model_path
    from scripts.ddm.rescore_fits import inputs
    x = inputs()
    out = []
    for mouse in np.unique(x["subject_id"]):
        sel = x["subject_id"] == mouse
        rig = np.unique(x["data_source"][sel & (x["sched_pulse_type"] != 0)]).item()
        ctrl = np.flatnonzero(sel & (x["sched_pulse_type"] == 0) & (x["signed_coherence"] != 0))
        data, stim = select(x, ctrl)
        coh = x["signed_coherence"][ctrl]
        ok = np.isfinite(data["rt"]) & (data["choice"] >= 0) & (data["rt"] < 0.6)
        obs = pd.Series((np.sign(coh[ok]) > 0) == (data["choice"][ok] == 1)).groupby(np.abs(coh[ok])).agg(["mean", "size"])
        for fam in families:
            r = pickle.load(model_path(fam)(mouse).open("rb"))
            model = make_model(r["variant"], rig, r["fixed_guess_bias"], responded=True, front_end=r["front_end"], ugm=r.get("ugm", False))
            sim = model._map_outcomes(model.simulate(stim, r["parameters"], n_reps=10, seed=12345, labels=data["condition"]))
            t = sim["trial"].to_numpy()
            fast = (sim["rt"].to_numpy() < 0.6) & (sim["choice"].to_numpy() >= 0)
            acc = pd.Series((np.sign(coh[t][fast]) > 0) == (sim["choice"].to_numpy()[fast] == 1)).groupby(np.abs(coh[t][fast])).mean()
            for c in obs.index:
                out.append(dict(mouse=mouse, family=fam, abs_coh=c, model_fast_acc=acc.get(c, np.nan),
                                data_fast_acc=obs.loc[c, "mean"], data_n=int(obs.loc[c, "size"])))
            model.simulator.clear_cache()
    return pd.DataFrame(out)


def main(d):
    h = pd.read_csv(d / "heldout/cells.csv.gz")
    rep = pd.read_csv(d / "heldout/reproduction.csv")
    rep["diff"] = rep.recomputed - rep.stored
    print("reproduction (recomputed - stored test NLL, per fold), by family:\n",
          rep.groupby("family")["diff"].agg(["mean", lambda s: s.abs().max()]).round(3).to_string())
    tot = h.groupby(["family", "mouse", "seed"])[["choice_nll", "rt_nll", "penalty"]].sum().sum(axis=1).rename("nll").reset_index()
    parts = h.groupby(["family", "mouse", "seed"])[["choice_nll", "rt_nll"]].sum().reset_index()
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
    for f, b in PAIRS.items():
        x = tot[tot.family == f].merge(tot[tot.family == b], on=["mouse", "seed"], suffixes=("", "_b"))
        x["d"] = x.nll - x.nll_b
        m = x.groupby("mouse").d.agg(mean="mean", sd="std").reset_index()
        pc = parts[parts.family == f].merge(parts[parts.family == b], on=["mouse", "seed"], suffixes=("", "_b"))
        pc = pc.assign(d_choice=pc.choice_nll - pc.choice_nll_b, d_rt=pc.rt_nll - pc.rt_nll_b).groupby("mouse")[["d_choice", "d_rt"]].mean()
        m = m.merge(pc, on="mouse")
        m["improved"] = (m["mean"] < -2 * m["sd"]) & (m["mean"] < -2)
        m["improved_loose"] = (m["mean"] < 0) & (m["mean"].abs() > m["sd"])
        folder, variant = NEW[f]
        for i, r in m.iterrows():
            full = pickle.load(open(DDM / folder / f"{r.mouse}_{variant}_pulse.pkl", "rb"))["parameters"]
            folds = [pickle.load(open(DDM / folder / f"{r.mouse}_{variant}_pcv{k}.pkl", "rb"))["parameters"]["guess_w"] for k in range(5)]
            m.loc[i, "guess_w_full"] = full["guess_w"]
            m.loc[i, "read_lag_full"] = full["read_lag"]
            m.loc[i, "guess_w_pcv_median"] = np.median(folds)
            m.loc[i, "folds_w_gt"] = sum(v > THRESH for v in folds)
            m.loc[i, "mech"] = full["guess_w"] > THRESH and sum(v > THRESH for v in folds) >= 3
            m.loc[i, "mech_loose"] = np.median(folds) > THRESH
            m.loc[i, "resid_new_pp"] = 100 * resid[f, r.mouse]
            m.loc[i, "resid_const_pp"] = 100 * resid[b, r.mouse]
            m.loc[i, "ctrl_excess_new"] = ctrl_mouse[f, r.mouse]
            m.loc[i, "ctrl_excess_const"] = ctrl_mouse[b, r.mouse]
        m.insert(0, "family", f); rows.append(m)
        rest = m[~m.mouse.isin(SPECIAL)]
        w = wilcoxon(rest["mean"]) if (rest["mean"] != 0).any() else None
        sp = m[m.mouse.isin(SPECIAL)].set_index("mouse")
        shrink = lambda s, k: abs(sp.loc[s, "resid_new_pp"]) <= k * abs(sp.loc[s, "resid_const_pp"])
        boot = np.random.default_rng(20261120).choice(rest["mean"].to_numpy(), (2000, len(rest)))
        lo, hi = np.quantile(np.median(boot, axis=1), [.025, .975])
        imp, impl = m[m.improved], m[m.improved_loose]
        cn, cb = ctrl[f], ctrl[b]
        summary.append(dict(
            family=f, constant=b, total_dNLL=m["mean"].sum(),
            c1_improved_mice=f"{int(m.improved.sum())}/10: {','.join(imp.mouse) or '-'}",
            c2_median_dNLL_8=rest["mean"].median(), c2_wilcoxon_p=w.pvalue if w else np.nan,
            c2_pass=bool(w and w.pvalue < .05 and rest["mean"].median() < 0),
            c3_pass=bool(all(sp.loc[s, "improved"] and shrink(s, .5) for s in SPECIAL)),
            c4_pass=bool(sp.mech.all()), c4_detail="; ".join(f"{s}: full {sp.loc[s, 'guess_w_full']:.2f}, {int(sp.loc[s, 'folds_w_gt'])}/5 folds" for s in SPECIAL),
            c5_ctrl_excess_new=cn.mean(), c5_ctrl_excess_const=cb.mean(), c5_const_seed_range=cb.max() - cb.min(),
            c5_pass=bool(cn.mean() - cb.mean() <= cb.max() - cb.min()),
            a2_1_improved_mice=f"{int(m.improved_loose.sum())}/10: {','.join(impl.mouse) or '-'}",
            a2_2_sign_count_8=f"{int((rest['mean'] < 0).sum())}/8 improved", a2_2_median_ci=f"{rest['mean'].median():.2f} [{lo:.2f}, {hi:.2f}]",
            a2_3_pass=bool(all(sp.loc[s, "improved_loose"] and shrink(s, .75) for s in SPECIAL)),
            a2_4_pass=bool(sp.mech_loose.all()),
            a2_5_ctrl_change=cn.mean() - cb.mean(), a2_5_flag=bool(cn.mean() - cb.mean() > 2 * (cb.max() - cb.min()))))
    per_mouse = pd.concat(rows, ignore_index=True); per_mouse.to_csv(d / "criteria_per_mouse.csv", index=False)
    s = pd.DataFrame(summary); s.to_csv(d / "criteria_summary.csv", index=False)
    fa = fast_control_accuracy(list(PAIRS) + list(PAIRS.values()))
    fa.to_csv(d / "fast_control_accuracy.csv", index=False)
    pd.set_option("display.width", 250)
    print("\n== per mouse ==\n", per_mouse.round(3).to_string(index=False))
    print("\n== criteria ==\n", s.round(3).T.to_string())
    print("\n== rule 6: fast control accuracy at |coh| 100 ==\n",
          fa[fa.abs_coh == fa.abs_coh.max()].pivot_table(index="mouse", columns="family", values=["model_fast_acc", "data_fast_acc"]).round(2).to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
