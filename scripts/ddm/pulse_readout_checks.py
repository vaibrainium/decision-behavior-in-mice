"""Descriptive checks of a pulse readout-bias (slow-trial) account (plan .agents/plans/2026-10-27-pulse-readout-bias-checks.md).

Responded trials, symmetric cells. RT bins = per mouse x |coherence| quintiles of control RTs.
1. pulse effect by RT bin (±100% and |c| <= 36%): P(choice = pulse sign | pulse) - same on controls at that coherence
2. control accuracy by RT bin at ±100%
3. RT quantiles given choice, pulse minus control (pulse-direction and opposite choices), |c| <= 36%

Outputs: dissemination/figures/qc/pulse_readout_checks_<date>.{png,pdf}, _by_bin.csv, _rt_given_choice.csv
Usage: python -m scripts.ddm.pulse_readout_checks
"""

from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_energy_traces import TRIAL_TABLE
from scripts.ddm.pulse_psychometric import OUT, PROCESSED

N_BINS = 5
QUANTILES = [0.1, 0.3, 0.5, 0.7, 0.9]


def trials():
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    sym = pd.read_csv(PROCESSED / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "signs_scheduled_symmetric"]).set_index("trial_id").signs_scheduled_symmetric
    t = pd.DataFrame({"mouse": inputs["subject_id"], "coh": np.round(inputs["signed_coherence"] * 100).astype(int),
                      "s": np.sign(inputs["sched_pulse_type"]), "choice": np.where(inputs["choice"] == 1, 1, -1), "rt": inputs["rt"]})
    t = t[sym.reindex(inputs["agg_code"].astype(str)).to_numpy().astype(bool)].copy()
    return assign_bins(t, bin_edges(t))


def bin_edges(t):
    """Inner RT quintile edges of control trials per (mouse, |coherence|)."""
    return {k: np.quantile(g.rt[g.s == 0], np.linspace(0, 1, N_BINS + 1))[1:-1] for k, g in t.groupby([t.mouse, t.coh.abs()])}


def assign_bins(t, edges):
    t = t.copy()
    t["bin"] = -1
    for k, g in t.groupby([t.mouse, t.coh.abs()]):
        t.loc[g.index, "bin"] = np.digitize(g.rt, edges[k])
    return t


def effect_by_bin(t, coh_set):
    """Per mouse x bin: pulse-count-weighted mean over (c, s) of P(choice = s | pulse) - P(choice = s | control)."""
    rows = []
    x = t[coh_set(t.coh)]
    for (mouse, c, b), g in x.groupby(["mouse", "coh", "bin"]):
        ctrl = g[g.s == 0]
        for s in (-1, 1):
            p = g[g.s == s]
            if len(p) and len(ctrl):
                rows.append({"mouse": mouse, "coh": c, "s": s, "bin": b, "n": len(p), "d": (p.choice == s).mean() - (ctrl.choice == s).mean()})
    r = pd.DataFrame(rows)
    pm = r.groupby(["mouse", "bin"]).apply(lambda m: np.average(m.d, weights=m.n), include_groups=False).rename("effect").reset_index()
    return pm


def rt_given_choice(t):
    """Per mouse: pulse-count-weighted mean over (c, s) of RT quantile(pulse, choice) - RT quantile(control, choice), ms."""
    rows = []
    x = t[t.coh.abs() <= 36]
    for (mouse, c), g in x.groupby(["mouse", "coh"]):
        for s in (-1, 1):
            for rel, ch in (("toward pulse", s), ("against pulse", -s)):
                p, k = g[(g.s == s) & (g.choice == ch)].rt, g[(g.s == 0) & (g.choice == ch)].rt
                if len(p) >= 5 and len(k) >= 5:
                    d = 1000 * (np.quantile(p, QUANTILES) - np.quantile(k, QUANTILES))
                    rows += [{"mouse": mouse, "coh": c, "s": s, "choice": rel, "q": q, "n": len(p), "d_ms": v} for q, v in zip(QUANTILES, d)]
    r = pd.DataFrame(rows)
    return r.groupby(["mouse", "choice", "q"]).apply(lambda m: np.average(m.d_ms, weights=m.n), include_groups=False).rename("d_ms").reset_index()


def summary(pm, by, value):
    return pm.groupby(by)[value].agg(["mean", "sem", "count"]).reset_index()


def main():
    t = trials()
    e100 = effect_by_bin(t, lambda c: c.abs() == 100).assign(set="±100%")
    e36 = effect_by_bin(t, lambda c: c.abs() <= 36).assign(set="|c| ≤ 36%")
    x = t[(t.coh.abs() == 100) & (t.s == 0)]
    acc = x.assign(correct=(x.choice == np.sign(x.coh))).groupby(["mouse", "bin"]).correct.mean().rename("accuracy").reset_index()
    rtc = rt_given_choice(t)

    stem = OUT / f"pulse_readout_checks_{date.today().isoformat()}"
    by_bin = pd.concat([summary(e100, ["set", "bin"], "effect"), summary(e36, ["set", "bin"], "effect"),
                        summary(acc, ["bin"], "accuracy").assign(set="control accuracy ±100%")])
    by_bin.round(4).to_csv(f"{stem}_by_bin.csv", index=False)
    rts = summary(rtc, ["choice", "q"], "d_ms")
    rts.round(2).to_csv(f"{stem}_rt_given_choice.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    labels = [f"Q{i + 1}" for i in range(N_BINS)]
    ax = axes[0]
    for pm, col in ((e100, "tab:red"), (e36, "tab:blue")):
        s = summary(pm, ["bin"], "effect")
        ax.errorbar(s.bin, 100 * s["mean"], yerr=100 * s["sem"], marker="o", color=col, capsize=2, label=pm.set.iloc[0])
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xticks(range(N_BINS), labels)
    ax.set_xlabel("RT quintile (control-defined; Q1 fastest)", fontsize=8)
    ax.set_ylabel("pulse − control, P(choice = pulse dir.) (pp)", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    s = summary(acc, ["bin"], "accuracy")
    for mouse, m in acc.groupby("mouse"):
        ax.plot(m.bin, m.accuracy, color="0.8", lw=0.6)
    ax.errorbar(s.bin, s["mean"], yerr=s["sem"], marker="o", color="k", capsize=2)
    ax.axhline(0.5, color="tab:red", ls=":", lw=0.8)
    ax.set_ylim(0.4, 1.0)
    ax.set_xticks(range(N_BINS), labels)
    ax.set_xlabel("RT quintile", fontsize=8)
    ax.set_ylabel("control accuracy at ±100%", fontsize=8)
    ax = axes[2]
    for rel, col in (("toward pulse", "tab:blue"), ("against pulse", "tab:red")):
        s = rts[rts.choice == rel]
        ax.errorbar(s.q, s["mean"], yerr=s["sem"], marker="o", color=col, capsize=2, label=f"choice {rel}")
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel("RT quantile", fontsize=8)
    ax.set_ylabel("RT pulse − control, same choice (ms)", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    for a in axes:
        a.tick_params(labelsize=7)
    fig.suptitle("Readout-bias checks (responded trials, symmetric cells; mean ± SEM over mice; exploratory)", fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=170, bbox_inches="tight")

    pd.set_option("display.width", 200)
    print(by_bin.round(4).to_string(index=False))
    print(rts.round(1).to_string(index=False))
    print(f"saved {stem}.png/.pdf, _by_bin.csv, _rt_given_choice.csv")


if __name__ == "__main__":
    main()
