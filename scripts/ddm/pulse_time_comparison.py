"""Does the pulse effect change with pulse time (early vs middle vs late)? (plan
.agents/plans/2026-10-28-pulse-time-comparison.md)

Responded trials, symmetric cells (pulse_psychometric_stage.load_trials). Pulse effect = right pulse vs left pulse
(D010). Per mouse and stage, two estimates:
  pp:    P(right | right pulse) - P(right | left pulse), averaged over the coherences the mouse has in all its stages;
  logit: per-mouse logistic regression right ~ C(coh) + direction x stage on control and pulse trials (statsmodels
         GLM); the effect is the right - left log-odds shift (2 x the direction coefficient).
Within-mouse comparisons: early - middle (10 mice), early - late and middle - late (the 6 mice with late pulses); paired
t and Wilcoxon, Holm over the 3, dz; Page's trend test for early > middle > late on the 6 mice.
Hierarchical model (PyMC): logit P(right) = base[mouse, coh] + direction * b[mouse, stage], base partially pooled per
coherence, b[m, s] ~ Normal(B_s + g_s * rig_centred[m], tau_s) (rig covariate for early/middle; late is one rig).
Contrasts are averages over the sample mice of b[m, s1] - b[m, s2] (x2 for right - left); posterior mean, 95% HDI,
P(> 0).
Sensitivity: pulse trials with RT > pulse onset + 100 ms (onset: scheduled for uw, recorded for ucla); per-mouse
estimates from pulse trials only (logit baseline C(coh):C(stage)).

Outputs: dissemination/paper_accumulation/tables/pulse_time_comparison_{per_mouse,tests,bayes}_<date>.csv
         dissemination/paper_accumulation/figures/qc/pulse_time_comparison_<date>.{png,pdf}
Usage: python -m scripts.ddm.pulse_time_comparison
"""

from datetime import date
from pathlib import Path

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

from scripts.ddm.pulse_energy_traces import TRIAL_TABLE
from scripts.ddm.pulse_psychometric import PROCESSED
from scripts.ddm.pulse_psychometric_stage import STAGES, load_trials

ROOT = Path(__file__).resolve().parents[2] / "dissemination" / "paper_accumulation"
RT_MARGIN = 0.1
PAIRS = [("early", "middle"), ("early", "late"), ("middle", "late")]
SEED = 0


def add_onset(t: pd.DataFrame) -> pd.DataFrame:
    tt = pd.read_csv(PROCESSED / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "scheduled_onset_s", "recorded_onset_s"]).set_index("trial_id")
    tt = tt.reindex(t.trial_id)
    onset = tt.scheduled_onset_s.fillna(tt.recorded_onset_s).to_numpy()
    t = t.assign(onset=np.where(t.stage > 0, onset, np.nan), stage_name=t.stage.map(STAGES))
    assert not t.loc[t.stage > 0, "onset"].isna().any()
    return t


def pp_effects(t: pd.DataFrame) -> pd.DataFrame:
    p = t[t.stage > 0]
    rows = []
    for mouse, g in p.groupby("mouse"):
        cell = g.groupby(["stage_name", "coh", "direction"]).right.mean().unstack("direction")
        diff = (cell[1] - cell[-1]).dropna().unstack("stage_name")
        diff = diff.dropna()  # coherences present in all of this mouse's stages, both directions
        rows += [{"mouse": mouse, "stage": s, "pp": 100 * diff[s].mean(), "n_coh": len(diff)} for s in diff.columns]
    return pd.DataFrame(rows)


def logit_effects(t: pd.DataFrame, pulse_only: bool = False) -> pd.DataFrame:
    rows = []
    for mouse, g in t.groupby("mouse"):
        g = g[g.stage > 0] if pulse_only else g
        stages = [s for s in STAGES.values() if (g.stage_name == s).any()]
        g = g.assign(**{f"d_{s}": g.direction * (g.stage_name == s) for s in stages})
        base = "C(coh):C(stage_name)" if pulse_only else "C(coh)"
        res = smf.glm(f"right ~ {base} + " + " + ".join(f"d_{s}" for s in stages), g, family=sm.families.Binomial()).fit()
        rows += [{"mouse": mouse, "stage": s, "logit": 2 * res.params[f"d_{s}"], "logit_se": 2 * res.bse[f"d_{s}"],
                  "n_pulse_trials": int((g.stage_name == s).sum())} for s in stages]
    return pd.DataFrame(rows)


def paired_tests(pmw: pd.DataFrame, measure: str, analysis: str) -> pd.DataFrame:
    w = pmw.pivot(index="mouse", columns="stage", values=measure)
    rows = []
    for a, b in PAIRS:
        x = (w[a] - w[b]).dropna()
        rows.append({"analysis": analysis, "measure": measure, "contrast": f"{a} - {b}", "n_mice": len(x), "mean": x.mean(),
                     "ci_lo": x.mean() - stats.t.ppf(0.975, len(x) - 1) * x.sem(), "ci_hi": x.mean() + stats.t.ppf(0.975, len(x) - 1) * x.sem(),
                     "mice_positive": int((x > 0).sum()), "t": stats.ttest_1samp(x, 0).statistic, "p_t": stats.ttest_1samp(x, 0).pvalue,
                     "p_wilcoxon": stats.wilcoxon(x).pvalue, "dz": x.mean() / x.std(ddof=1)})
    r = pd.DataFrame(rows)
    r["p_t_holm"] = multipletests(r.p_t, method="holm")[1]
    r["p_wilcoxon_holm"] = multipletests(r.p_wilcoxon, method="holm")[1]
    full = w[["late", "middle", "early"]].dropna()  # columns in predicted increasing order
    page = stats.page_trend_test(full.to_numpy())
    r["page_L"], r["page_p"], r["n_monotone"] = page.statistic, page.pvalue, int(((full.early > full.middle) & (full.middle > full.late)).sum())
    return r


def bayes(t: pd.DataFrame) -> tuple[pd.DataFrame, az.InferenceData]:
    mice = sorted(t.mouse.unique())
    cohs = sorted(t.coh.unique())
    m = t.mouse.map({k: i for i, k in enumerate(mice)}).to_numpy()
    k = t.coh.map({c: i for i, c in enumerate(cohs)}).to_numpy()
    s = np.maximum(t.stage.to_numpy() - 1, 0)
    d = (t.direction * (t.stage > 0)).to_numpy().astype(float)
    uw = np.array([t.loc[t.mouse == mo, "rig"].iloc[0] == "uw" for mo in mice], float)
    rigc = uw - uw.mean()
    with pm.Model():
        mu_c = pm.Normal("mu_c", 0, 2.5, shape=len(cohs))
        sigma_c = pm.HalfNormal("sigma_c", 1.5)
        base = pm.Deterministic("base", mu_c + sigma_c * pm.Normal("base_z", 0, 1, shape=(len(mice), len(cohs))))
        B = pm.Normal("B", 0, 1, shape=3)
        g = pm.Normal("g", 0, 1, shape=2)
        tau = pm.HalfNormal("tau", 0.5, shape=3)
        z = pm.Normal("z", 0, 1, shape=(len(mice), 3))
        gfull = pm.math.concatenate([g, np.zeros(1)])
        b = pm.Deterministic("b", B + gfull * rigc[:, None] + tau * z)
        pm.Bernoulli("y", logit_p=base[m, k] + d * b[m, s], observed=t.right.to_numpy())
        idata = pm.sample(1000, tune=1000, chains=4, target_accept=0.9, random_seed=SEED, progressbar=False)
    post = 2 * idata.posterior["b"].stack(draw_=("chain", "draw")).to_numpy()  # (mice, stages, draws), right - left
    has_late = np.array([(t[(t.mouse == mo)].stage == 3).any() for mo in mice])
    names = list(STAGES.values())
    rows = []
    for a, bb in PAIRS:
        sel = has_late if "late" in (a, bb) else np.ones(len(mice), bool)
        c = (post[sel, names.index(a)] - post[sel, names.index(bb)]).mean(axis=0)
        lo, hi = az.hdi(c, hdi_prob=0.95)
        rows.append({"contrast": f"{a} - {bb}", "n_mice": int(sel.sum()), "mean_logodds": c.mean(), "hdi_lo": lo, "hdi_hi": hi, "p_gt_0": (c > 0).mean()})
    for j, st in enumerate(names):
        sel = has_late if st == "late" else np.ones(len(mice), bool)
        c = post[sel, j].mean(axis=0)
        lo, hi = az.hdi(c, hdi_prob=0.95)
        rows.append({"contrast": f"{st} (effect)", "n_mice": int(sel.sum()), "mean_logodds": c.mean(), "hdi_lo": lo, "hdi_hi": hi, "p_gt_0": (c > 0).mean()})
    summ = az.summary(idata, var_names=["B", "g", "tau", "sigma_c"])
    print(summ.round(3).to_string())
    print(f"divergences: {int(idata.sample_stats.diverging.sum())}; max r_hat (all): {max(float(v.max()) for v in az.rhat(idata).data_vars.values()):.3f}; min ess_bulk: {min(float(v.min()) for v in az.ess(idata).data_vars.values()):.0f}")
    return pd.DataFrame(rows), idata


def figure(pmw: pd.DataFrame, pmw_rt: pd.DataFrame, bt: pd.DataFrame, stem: Path):
    names = list(STAGES.values())
    fig, axes = plt.subplots(1, 4, figsize=(15, 4), gridspec_kw={"width_ratios": [1, 1, 1, 1.15]})
    for ax, (df, col, title, unit) in zip(axes[:3], [(pmw, "pp", "Per mouse, all trials", "Right − left P(right) (pp)"),
                                                     (pmw, "logit", "Per mouse, logistic", "Right − left (log-odds)"),
                                                     (pmw_rt, "logit", f"Per mouse, logistic, RT > onset + {int(RT_MARGIN * 1000)} ms", "Right − left (log-odds)")]):
        w = df.pivot(index="mouse", columns="stage", values=col).reindex(columns=names)
        for mouse, row in w.iterrows():
            ax.plot(range(3), row.to_numpy(), "-o", color="0.7", ms=3, lw=0.8)
        ax.errorbar(np.arange(3) - 0.1, w.mean(), yerr=w.sem(), fmt="o", color="k", ms=5, capsize=0, label="all mice")
        six = w.dropna()
        ax.errorbar(np.arange(3) + 0.1, six.mean(), yerr=six.sem(), fmt="o", color="k", mfc="white", ms=5, capsize=0,
                    label=f"{len(six)} mice with late")
        if col == "pp":
            ax.legend(frameon=False, fontsize=7)
        ax.axhline(0, color="0.6", lw=0.7, zorder=0)
        ax.set_xticks(range(3), [f"{s}\n({w[s].notna().sum()} mice)" for s in names], fontsize=8)
        ax.set_ylabel(unit, fontsize=9)
        ax.set_title(title, fontsize=9)
    ax = axes[3]
    c = bt[~bt.contrast.str.contains("effect")].reset_index(drop=True)
    ax.errorbar(c.mean_logodds, range(len(c)), xerr=[c.mean_logodds - c.hdi_lo, c.hdi_hi - c.mean_logodds], fmt="o", color="k", capsize=0)
    ax.axvline(0, color="0.6", lw=0.7)
    ax.set_yticks(range(len(c)), [f"{r.contrast} ({r.n_mice} mice)" for r in c.itertuples()], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Difference in right − left (log-odds)", fontsize=9)
    ax.set_title("Hierarchical model,\nwithin-mouse contrasts (95% HDI)", fontsize=9)
    fig.suptitle("Pulse effect by pulse time; grey: mice; black: mean ± SEM over all mice (filled) or the mice with late pulses (open)", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")


def main():
    t = add_onset(load_trials())
    pulse = t.stage > 0
    late_rt = t[pulse & (t.rt > t.onset + RT_MARGIN)]
    t_rt = pd.concat([t[~pulse], late_rt])
    print("pulse trials kept with RT > onset + margin:", (late_rt.groupby("stage_name").size() / t[pulse].groupby("stage_name").size()).round(3).to_dict())
    pmw = pp_effects(t).merge(logit_effects(t), on=["mouse", "stage"])
    pmw_rt = pp_effects(t_rt).merge(logit_effects(t_rt, pulse_only=True), on=["mouse", "stage"])
    tests = pd.concat([paired_tests(pmw, "pp", "all trials"), paired_tests(pmw, "logit", "all trials"),
                       paired_tests(pmw_rt, "pp", "RT > onset + 100 ms"), paired_tests(pmw_rt, "logit", "RT > onset + 100 ms")], ignore_index=True)
    bt, _ = bayes(t)
    day = date.today().isoformat()
    out = ROOT / "tables"
    pd.concat([pmw.assign(analysis="all trials"), pmw_rt.assign(analysis="RT > onset + 100 ms")]).round(4).to_csv(out / f"pulse_time_comparison_per_mouse_{day}.csv", index=False)
    tests.round(4).to_csv(out / f"pulse_time_comparison_tests_{day}.csv", index=False)
    bt.round(4).to_csv(out / f"pulse_time_comparison_bayes_{day}.csv", index=False)
    figure(pmw, pmw_rt, bt, ROOT / "figures" / "qc" / f"pulse_time_comparison_{day}")
    print(pmw.round(3).to_string(index=False))
    print(tests.drop(columns=["p_t", "p_wilcoxon"]).round(3).to_string(index=False))
    print(bt.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
