"""Two checks on the pulse effect (plan .agents/plans/2026-10-27-pulse-asymmetry-lapse-checks.md); responded trials,
asymmetric UW cells excluded.

1. Asymmetry: per mouse, incongruent - congruent pulse effect (pulse - control in P(pulse direction | response), mean
   over |c| 9-36) observed vs each model variant's own prediction on the same trials; paired t over mice, Holm.
2. Lapses at +-100%: excess errors per trial on incongruent pulse trials over controls, by RT bin.

Outputs: dissemination/figures/qc/pulse_asymmetry_lapse_<date>.{png,pdf}, _asymmetry.csv, _lapse.csv
Usage: python -m scripts.ddm.pulse_asymmetry_lapse   (after scripts.ddm.pulse_psychometric has filled its cache)
"""

from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import logit
from statsmodels.stats.multitest import multipletests

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_energy_traces import TRIAL_TABLE
from scripts.ddm.pulse_psychometric import OUT, PROCESSED, VARIANTS, model_predictions, trial_table

RT_BINS = [0.3, 0.5, 1.0, 2.0, 5.0]


def congruency_effects(t, value, scale):
    """Per mouse: congruent and incongruent effect (mean over |c| 9-36 of pulse - control, pulse-direction aligned)."""
    x = t[t.coh.abs().between(9, 36)]
    cell = x.groupby(["mouse", "coh", "category"])[value].mean().clip(1e-3, 1 - 1e-3)
    cell = (logit(cell) if scale == "logit" else 100 * cell).unstack("category")
    out = {}
    for cat, s in (("congruent", 1), ("incongruent", -1)):
        sign = s * np.sign(cell.index.get_level_values("coh"))
        out[cat] = (sign * (cell[cat] - cell["control"])).groupby("mouse").mean()
    return pd.DataFrame(out).assign(A=lambda d: d.incongruent - d.congruent)


def asymmetry(t, scale):
    obs = congruency_effects(t, "right", scale)
    rows = [{"source": "observed", "A_mean": obs.A.mean(), "A_sem": obs.A.sem(), "diff_mean": np.nan, "diff_ci_lo": np.nan, "diff_ci_hi": np.nan,
             "t": stats.ttest_1samp(obs.A, 0).statistic, "p": stats.ttest_1samp(obs.A, 0).pvalue, "n_mice": len(obs)}]
    for name in VARIANTS:
        mod = congruency_effects(t, name, scale)
        d = (obs.A - mod.A).dropna()
        r = stats.ttest_1samp(d, 0)
        lo, hi = stats.t.interval(0.95, len(d) - 1, loc=d.mean(), scale=d.sem())
        rows.append({"source": name, "A_mean": mod.A.mean(), "A_sem": mod.A.sem(), "diff_mean": d.mean(), "diff_ci_lo": lo, "diff_ci_hi": hi,
                     "t": r.statistic, "p": r.pvalue, "n_mice": len(d)})
    a = pd.DataFrame(rows)
    m = a.source != "observed"
    a.loc[m, "p_holm"] = multipletests(a.loc[m, "p"], method="holm")[1]
    return a.assign(scale=scale), obs


def lapse(t):
    """Per mouse and RT bin at +-100%: errors per trial, incongruent pulse minus control."""
    x = t[(t.coh.abs() == 100) & t.category.isin(["control", "incongruent"])].copy()
    x["error"] = (x.right == 1) != (x.coh > 0)
    x["bin"] = pd.cut(x.rt, RT_BINS, right=False)
    n = x.groupby(["mouse", "category"]).size()
    errs = x[x.error].groupby(["mouse", "category", "bin"], observed=False).size()
    rate = (errs / n.reindex(errs.index.droplevel("bin")).to_numpy()).unstack("category")
    excess = (100 * (rate["incongruent"] - rate["control"])).rename("excess_pp").reset_index()
    med = x[x.error].groupby(["mouse", "category"]).rt.median().unstack("category").add_prefix("median_error_rt_")
    return excess, med, n.unstack("category")


def main():
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    sym = pd.read_csv(PROCESSED / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "signs_scheduled_symmetric"]).set_index("trial_id").signs_scheduled_symmetric
    t = trial_table(inputs).assign(rt=inputs["rt"])
    keep = sym.reindex(inputs["agg_code"].astype(str)).to_numpy()
    assert not pd.isna(keep).any()
    preds = model_predictions(inputs, sorted(np.unique(inputs["subject_id"])))
    for name, p in preds.items():
        t[name] = p.reindex(t.index).to_numpy()
    t = t[keep.astype(bool) & (t.category != "zero_coherence_pulse")]
    print(f"{len(t)} responded trials in symmetric cells; categories {t.category.value_counts().to_dict()}")

    a_pp, obs_pp = asymmetry(t, "pp")
    a_lg, _ = asymmetry(t, "logit")
    asym = pd.concat([a_pp, a_lg])
    excess, med, counts = lapse(t)

    stem = OUT / f"pulse_asymmetry_lapse_{date.today().isoformat()}"
    asym.round(4).to_csv(f"{stem}_asymmetry.csv", index=False)
    excess.round(3).to_csv(f"{stem}_lapse.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    ax = axes[0]
    y = np.arange(len(a_pp))
    ax.errorbar(a_pp.A_mean, y, xerr=a_pp.A_sem, fmt="o", color="k", ms=4)
    ax.scatter(obs_pp.A, np.zeros(len(obs_pp)) - 0.25, s=8, color="0.6", label="observed, per mouse")
    ax.set_yticks(y, a_pp.source, fontsize=7)
    ax.axvline(0, color="0.6", lw=0.6)
    ax.axvline(a_pp.A_mean.iloc[0], color="tab:orange", ls=":", lw=1)
    ax.invert_yaxis()
    ax.set_xlabel("incongruent − congruent pulse effect (pp), mean ± SEM over mice", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    g = excess.groupby("bin", observed=False).excess_pp.agg(["mean", "sem"])
    ax.bar(np.arange(len(g)), g["mean"], yerr=g["sem"], color="tab:red", alpha=0.7)
    for mouse, m in excess.groupby("mouse"):
        ax.plot(np.arange(len(m)), m.excess_pp, color="0.6", lw=0.6, marker=".", ms=3)
    ax.set_xticks(np.arange(len(g)), [f"{b.left:g}–{b.right:g}" for b in g.index], fontsize=8)
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel("RT bin (s from motion onset)", fontsize=8)
    ax.set_ylabel("excess errors per trial at ±100% (pp)\nincongruent pulse − control", fontsize=8)
    fig.suptitle("Pulse congruency asymmetry vs model predictions (left) and timing of excess errors at ±100% (right); responded trials, symmetric cells", fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=170, bbox_inches="tight")

    pd.set_option("display.width", 200)
    print(asym.round(3).to_string(index=False))
    print(g.round(2).to_string())
    print(f"total excess (pp): {excess.groupby('mouse').excess_pp.sum().agg(['mean', 'sem']).round(2).to_dict()}")
    print(pd.concat([med, counts], axis=1).round(3).to_string())
    print(f"saved {stem}.png/.pdf, _asymmetry.csv, _lapse.csv")


if __name__ == "__main__":
    main()
