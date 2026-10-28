"""Observed psychometric functions on control and pulse trials, per pulse stage (plan
.agents/plans/2026-10-28-pulse-psychometric-by-stage.md).

Responded trials only; asymmetric UW cells (one pulse sign scheduled) excluded via signs_scheduled_symmetric, as in
pulse_asymmetry_lapse. Pulse stage = |sched_pulse_type|: 1 early, 2 middle, 3 late (stage 3 exists only in the UW
design). Two sets of curves per stage, each with the same control curve:
  direction:  right pulse (sched_pulse_type > 0) and left pulse (< 0), all coherences;
  congruency: congruent (pulse toward the trial's coherence) and incongruent (against it); 0% pulses are on neither.
Mouse is the unit: P(right) per mouse and cell, then mean +- SEM over mice. At each coherence all curves of a panel use
the same mice (>= MIN_TRIALS trials in each); points with < MIN_MICE mice are not drawn. Each curve is a logistic
with lapses, p = gamma + (1 - gamma - lambda) / (1 + exp(-beta * (c - mu))), c in % coherence, fitted by least squares
to the drawn group-mean points weighted by their number of mice (descriptive). The control curve fits all four
parameters (lapses in [0, 0.5]); pulse curves share the control curve's lapses and fit only bias mu and slope beta,
because pulse curves lack one or both +-100% points and their lapses would be unconstrained.

Outputs: dissemination/paper_accumulation/figures/qc/pulse_psychometric_stage_<date>.{png,pdf}, _cells.csv, _fits.csv,
         _curves.csv (fitted curves on a 1% grid)
Usage: python -m scripts.ddm.pulse_psychometric_stage
"""

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_energy_traces import TRIAL_TABLE
from scripts.ddm.pulse_psychometric import PROCESSED, trial_table

OUT = Path(__file__).resolve().parents[2] / "dissemination" / "paper_accumulation" / "figures" / "qc"
STAGES = {1: "early", 2: "middle", 3: "late"}
MIN_TRIALS = 5
MIN_MICE = 3
GRID = np.arange(-100, 101)
SETS = {"direction": ["control", "right pulse", "left pulse"], "congruency": ["control", "congruent", "incongruent"]}
COLOURS = {"control": "0.3", "right pulse": "tab:orange", "left pulse": "tab:purple", "congruent": "tab:blue", "incongruent": "tab:red"}


def load_trials() -> pd.DataFrame:
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    sym = pd.read_csv(PROCESSED / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "signs_scheduled_symmetric"]).set_index("trial_id").signs_scheduled_symmetric
    keep = sym.reindex(inputs["agg_code"].astype(str)).to_numpy()
    assert not pd.isna(keep).any()
    t = trial_table(inputs).assign(stage=np.abs(inputs["sched_pulse_type"]))
    print(f"{len(t)} responded trials; {int((~keep.astype(bool)).sum())} in asymmetric cells dropped")
    return t[keep.astype(bool)]


def cells(t: pd.DataFrame) -> pd.DataFrame:
    """Mean +- SEM over mice of P(right) per curve set, stage, curve and coherence. Within a panel and coherence, every
    curve uses the same mice: those with >= MIN_TRIALS trials in each curve present at that coherence (paired points);
    points with fewer than MIN_MICE such mice are marked shown = False."""
    control = t[t.category == "control"]
    rows = []
    for stage in STAGES:
        p = t[t.stage == stage]
        curves = {"control": control, "right pulse": p[p.direction > 0], "left pulse": p[p.direction < 0],
                  "congruent": p[p.category == "congruent"], "incongruent": p[p.category == "incongruent"]}
        for set_name, names in SETS.items():
            pm = {n: curves[n].groupby(["coh", "mouse"]).right.agg(["mean", "size"]) for n in names}
            for coh in sorted(control.coh.unique()):
                present = [n for n in names if coh in pm[n].index.get_level_values("coh")]
                mice = set.intersection(*[set(pm[n].loc[coh].query("size >= @MIN_TRIALS").index) for n in present])
                for n in present:
                    x = pm[n].loc[coh].loc[sorted(mice)] if mice else pm[n].loc[coh].iloc[:0]
                    rows.append({"set": set_name, "stage": STAGES[stage], "curve": n, "coh": coh, "p_right": x["mean"].mean(),
                                 "sem": x["mean"].sem(), "n_mice": len(x), "n_trials": int(x["size"].sum()), "shown": len(x) >= MIN_MICE})
    return pd.DataFrame(rows)


def logistic4(params, c):
    mu, beta, gamma, lam = params
    return gamma + (1 - gamma - lam) / (1 + np.exp(-beta * (c - mu)))


def fit_curve(d: pd.DataFrame, lapses: tuple[float, float] | None = None) -> dict:
    """Free lapses without `lapses`; otherwise lapses fixed and only mu, beta fitted."""
    w, c, y = np.sqrt(d.n_mice.to_numpy()), d.coh.to_numpy(), d.p_right.to_numpy()
    if lapses is None:
        res = least_squares(lambda q: w * (logistic4(q, c) - y), x0=[0.0, 0.05, 0.1, 0.1], bounds=([-50, 0, 0, 0], [50, 1, 0.5, 0.5]))
        params = res.x
    else:
        res = least_squares(lambda q: w * (logistic4([*q, *lapses], c) - y), x0=[0.0, 0.05], bounds=([-50, 0], [50, 1]))
        params = [*res.x, *lapses]
    return dict(zip(["mu", "beta", "gamma", "lambda"], params)) | {"lapses_from_control": lapses is not None,
                                                                  "rmse": float(np.sqrt(np.mean((res.fun / w) ** 2))), "n_points": len(d)}


def fits(c: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, curves = [], []
    shown = c[c.shown]
    for (set_name, stage), panel in shown.groupby(["set", "stage"]):
        ctl = fit_curve(panel[panel.curve == "control"])
        for name, d in panel.groupby("curve"):
            f = ctl if name == "control" else fit_curve(d, (ctl["gamma"], ctl["lambda"]))
            rows.append({"set": set_name, "stage": stage, "curve": name, **f})
            curves.append(pd.DataFrame({"set": set_name, "stage": stage, "curve": name, "coh": GRID,
                                        "p_fit": logistic4([f["mu"], f["beta"], f["gamma"], f["lambda"]], GRID)}))
    return pd.DataFrame(rows), pd.concat(curves, ignore_index=True)


def main():
    t = load_trials()
    c = cells(t)
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / f"pulse_psychometric_stage_{date.today().isoformat()}"
    c.round(4).to_csv(f"{stem}_cells.csv", index=False)
    f, curves = fits(c)
    f.round(4).to_csv(f"{stem}_fits.csv", index=False)
    curves.round(4).to_csv(f"{stem}_curves.csv", index=False)
    print(f.round(3).to_string(index=False))
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.4), sharex=True, sharey=True)
    for i, (set_name, names) in enumerate(SETS.items()):
        for j, stage in enumerate(STAGES.values()):
            ax = axes[i, j]
            for name in names:
                d = c[(c.set == set_name) & (c.stage == stage) & (c.curve == name) & c.shown]
                ax.errorbar(d.coh, d.p_right, yerr=d["sem"], fmt="o", ms=3.5, capsize=0, color=COLOURS[name], label=name)
                k = curves[(curves.set == set_name) & (curves.stage == stage) & (curves.curve == name)]
                ax.plot(k.coh, k.p_fit, lw=1.2, color=COLOURS[name])
            n = c[(c.set == set_name) & (c.stage == stage) & c.shown & (c.curve != "control")].n_mice
            ax.set_title(f"{stage} pulse ({n.min()}-{n.max()} mice per point)", fontsize=9)
            ax.axhline(0.5, color="0.8", lw=0.6, zorder=0)
            ax.axvline(0, color="0.8", lw=0.6, zorder=0)
            ax.set_xticks([-100, -36, 0, 36, 100])
            if j == 0:
                ax.set_ylabel("P(right)")
                ax.legend(frameon=False, fontsize=8, loc="upper left")
            if i == 1:
                ax.set_xlabel("Signed coherence (%)")
    fig.suptitle("Responded trials, symmetric cells; mean ± SEM over mice, logistic fits (pulse curves share control lapses)", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")
    print(f"saved {stem}.png/.pdf, _cells.csv")


if __name__ == "__main__":
    main()
