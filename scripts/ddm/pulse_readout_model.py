"""RT-split pulse checks on the primary model's simulated trials, next to the data (plan
.agents/plans/2026-10-27-pulse-readout-model-rt-split.md).

Same trials and statistics as scripts/ddm/pulse_readout_checks.py. Each trial is simulated 200 times (seed 0) from the
mouse's primary control fit (L0U0V1Z0G1, fits_resp_final); simulated responses only. RT bins: the observed control
quintile edges per mouse x |coherence| (secondary: the model's own control quintiles).

Outputs: <processed>/ddm/pulse_readout_model_resp/<mouse>.pkl (simulation cache),
         dissemination/figures/qc/pulse_readout_model_<date>.{png,pdf}, _by_bin.csv, _rt_given_choice.csv
Usage: python -m scripts.ddm.pulse_readout_model
"""

import pickle
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.primacy import load_fit, predict_mouse
from scripts.ddm.pulse_psychometric import OUT, PROCESSED
from scripts.ddm.pulse_readout_checks import N_BINS, assign_bins, bin_edges, effect_by_bin, rt_given_choice, summary, trials

CACHE = PROCESSED / "ddm" / "pulse_readout_model_resp"
FITS, VARIANT, N_REPS, SEED = "fits_resp_final", "L0U0V1Z0G1", 200, 0


def simulated(inputs, t):
    """Simulated responses for every trial in t (index = input row), one row per (trial, rep)."""
    parts = []
    for mouse, g in t.groupby("mouse"):
        path = CACHE / f"{mouse}.pkl"
        if path.exists():
            sim = pickle.load(open(path, "rb"))
        else:
            fit = load_fit(PROCESSED / "ddm" / FITS, mouse, VARIANT, "control", False, None, None, responded=True)
            sim = predict_mouse(inputs, mouse, fit["parameters"], VARIANT, N_REPS, SEED, False, None, rows=g.index.to_numpy(), keep_sim=True)["sim"]
            CACHE.mkdir(parents=True, exist_ok=True)
            pickle.dump(sim, open(path, "wb"))
        sim = sim[sim.choice >= 0]
        meta = g.loc[sim.row, ["mouse", "coh", "s"]].reset_index(drop=True)
        parts.append(meta.assign(choice=np.where(sim.choice.to_numpy() == 1, 1, -1), rt=sim.rt.to_numpy()))
    return pd.concat(parts, ignore_index=True)


def statistics(t):
    e100 = effect_by_bin(t, lambda c: c.abs() == 100).assign(set="±100%")
    e36 = effect_by_bin(t, lambda c: c.abs() <= 36).assign(set="|c| ≤ 36%")
    x = t[(t.coh.abs() == 100) & (t.s == 0)]
    acc = x.assign(correct=(x.choice == np.sign(x.coh))).groupby(["mouse", "bin"]).correct.mean().rename("accuracy").reset_index()
    by_bin = pd.concat([summary(e100, ["set", "bin"], "effect"), summary(e36, ["set", "bin"], "effect"),
                        summary(acc, ["bin"], "accuracy").assign(set="control accuracy ±100%")])
    return by_bin, summary(rt_given_choice(t), ["choice", "q"], "d_ms")


def main():
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    data = trials()
    edges = bin_edges(data)
    sim = simulated(inputs, data)
    print(f"{len(data)} trials, {len(sim)} simulated responses ({len(sim) / (len(data) * N_REPS):.3f} of simulated trials)")

    results = {"data": statistics(data), "model (observed bins)": statistics(assign_bins(sim, edges)),
               "model (own bins)": statistics(assign_bins(sim, bin_edges(sim)))}
    stem = OUT / f"pulse_readout_model_{date.today().isoformat()}"
    pd.concat([b.assign(source=k) for k, (b, _) in results.items()]).round(4).to_csv(f"{stem}_by_bin.csv", index=False)
    pd.concat([r.assign(source=k) for k, (_, r) in results.items()]).round(2).to_csv(f"{stem}_rt_given_choice.csv", index=False)

    style = {"data": dict(marker="o", ls="none", capsize=2), "model (observed bins)": dict(ls="-", lw=1.5), "model (own bins)": dict(ls=":", lw=1.2)}
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.8))
    x = np.arange(N_BINS)
    for src, (b, r) in results.items():
        for k, (setname, col) in enumerate((("±100%", "tab:red"), ("|c| ≤ 36%", "tab:blue"))):
            s = b[b.set == setname].sort_values("bin")
            axes[k].errorbar(s.bin, 100 * s["mean"], yerr=100 * s["sem"] if src == "data" else None, color=col, label=src, **style[src])
        s = b[b.set == "control accuracy ±100%"].sort_values("bin")
        axes[2].errorbar(s.bin, s["mean"], yerr=s["sem"] if src == "data" else None, color="k", label=src, **style[src])
        for rel, col in (("toward pulse", "tab:blue"), ("against pulse", "tab:red")):
            s = r[r.choice == rel].sort_values("q")
            axes[3].errorbar(s.q, s["mean"], yerr=s["sem"] if src == "data" else None, color=col, label=f"{rel}, {src}", **style[src])
    titles = ["pulse effect, ±100% (pp)", "pulse effect, |c| ≤ 36% (pp)", "control accuracy, ±100%", "RT pulse − control, same choice (ms)"]
    for k, ax in enumerate(axes):
        ax.set_title(titles[k], fontsize=9)
        ax.tick_params(labelsize=7)
        if k < 3:
            ax.set_xticks(x, [f"Q{i + 1}" for i in x])
            ax.set_xlabel("RT quintile (observed control edges; Q1 fastest)", fontsize=7)
        if k != 2:
            ax.axhline(0, color="0.6", lw=0.6)
    axes[2].axhline(0.5, color="tab:red", ls=":", lw=0.8)
    axes[3].set_xlabel("RT quantile", fontsize=7)
    axes[0].legend(fontsize=7, frameon=False)
    axes[3].legend(fontsize=6, frameon=False)
    fig.suptitle("RT-split pulse checks: data (points, mean ± SEM over mice) vs primary model on the same trials (lines); responded, symmetric cells; exploratory", fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=170, bbox_inches="tight")

    # per-mouse data - model pulse effect per RT bin (observed bins), paired t over mice, Holm over the 5 bins per set
    from scipy import stats
    from statsmodels.stats.multitest import multipletests
    sim_b = assign_bins(sim, edges)
    rows = []
    for setname, sel in (("±100%", lambda c: c.abs() == 100), ("|c| ≤ 36%", lambda c: c.abs() <= 36)):
        d = effect_by_bin(data, sel).merge(effect_by_bin(sim_b, sel), on=["mouse", "bin"], suffixes=("_data", "_model"))
        for b, g in d.groupby("bin"):
            diff = 100 * (g.effect_data - g.effect_model)
            r = stats.ttest_1samp(diff, 0)
            rows.append({"set": setname, "bin": b, "data_minus_model_pp": diff.mean(), "sem": diff.sem(), "t": r.statistic, "p": r.pvalue, "n_mice": len(diff)})
    shortfall = pd.DataFrame(rows)
    shortfall["p_holm"] = shortfall.groupby("set").p.transform(lambda p: multipletests(p, method="holm")[1])
    shortfall.round(4).to_csv(f"{stem}_shortfall.csv", index=False)

    pd.set_option("display.width", 200)
    print(shortfall.round(3).to_string(index=False))
    for k, (b, r) in results.items():
        print(f"== {k}")
        print(b.round(4).to_string(index=False))
        print(r.round(1).to_string(index=False))
    print(f"saved {stem}.png/.pdf, _by_bin.csv, _rt_given_choice.csv")


if __name__ == "__main__":
    main()
