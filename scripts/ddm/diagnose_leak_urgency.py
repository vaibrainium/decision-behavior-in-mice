"""Where do leak and urgency help, and do UCLA and UW mice behave differently? (follow-up to plan step 3.2)

Leak and urgency improve held-out fit almost only in PSUIM5/6/7 (three of the four UCLA mice). Two checks, both on
control trials only (no scheduled pulse), so the pulse trials of the primacy test play no part in choosing the model:

1. Model check: simulate the full model (L1U1V1Z0G1) and the model without leak and urgency (L0U0V1Z0G1), each from its
   all-trial fit (best of fits_guess / fits_guess_warm), and split the misfit into cells (|coherence| x outcome
   x RT bin, RT bins = data deciles per |coherence|). Misfit per cell is the G statistic 2 n_obs log(p_obs / p_model);
   summing its decrease by outcome and RT range shows which features the two mechanisms buy.
2. Data check, no model: per mouse, RT quantiles of correct responses, accuracy for fast/medium/slow responses and the
   censored (> 5 s) rate, at matched |coherence|.
3. Censored trials (`censored_trials.csv`, all of them, pulse trials included): share that are responses after 5 s
   (the stimulus kept running; 5 s is our censoring cutoff), their RTs, and their accuracy by coherence and lateness.

Usage: python -m scripts.ddm.diagnose_leak_urgency [--mice PSUIM6 DBM6 ...] [--n_reps 20]   # default: all 10 mice
       python -m scripts.ddm.diagnose_leak_urgency --data_only                              # checks 2-3, no simulation
Writes dissemination/figures/leak_urgency_diagnosis_<date>.png and prints the tables.
"""

import argparse
import datetime
import glob
import logging
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import CENSOR_AT, DEVICE, LIKELIHOOD_PARAMS, MIN_RT, MouseDDM, load_inputs, make_params, select

PROCESSED = Path(dir_config.data.processed)
FULL, STRICT = "L1U1V1Z0G1", "L0U0V1Z0G1"
FIT_DIRS = ["ddm/fits_guess", "ddm/fits_guess_warm"]
RT_RANGES = {"fast <0.6 s": (0, 0.6), "0.6-1.5 s": (0.6, 1.5), "1.5-5 s": (1.5, np.inf)}


def best_fit(mouse: str, variant: str) -> dict:
    fits = [pickle.load(open(p, "rb")) for d in FIT_DIRS for p in glob.glob(str(PROCESSED / d / f"{mouse}_{variant}_all.pkl"))]
    return min(fits, key=lambda r: r["train_nll"])


def control_trials(inputs: dict, mouse: str):
    rows = np.flatnonzero((inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] == 0))
    data, stim = select(inputs, rows)
    obs = pd.DataFrame({"coh": inputs["signed_coherence"][rows], "rt": data["rt"], "choice": data["choice"]})
    return rows, data, stim, obs, str(np.unique(inputs["data_source"][rows]).item())


def simulate(variant: str, mouse: str, data: dict, stim: np.ndarray, coh: np.ndarray, rig: str, n_reps: int) -> pd.DataFrame:
    free, fixed = make_params(variant)
    model = MouseDDM(free, fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])
    sim = model._map_outcomes(model.simulate(stim, best_fit(mouse, variant)["parameters"], n_reps=n_reps, seed=0, labels=data["condition"]))
    return pd.DataFrame({"coh": coh[sim["trial"].to_numpy()], "rt": sim["rt"].to_numpy(), "choice": sim["choice"].to_numpy().astype(int)})


def label_cells(df: pd.DataFrame, edges: dict) -> pd.DataFrame:
    df = df.assign(abs_coh=df.coh.abs())
    correct = (df.choice == 1) == (df.coh > 0)
    df["outcome"] = np.select([df.choice < 0, df.coh == 0, correct], ["no response", "0% response", "correct"], "error")
    df["rt_bin"] = -1
    for c, e in edges.items():
        m = (df.abs_coh == c) & (df.choice >= 0)
        df.loc[m, "rt_bin"] = np.searchsorted(e, df.loc[m, "rt"].to_numpy())
    return df


def misfit(obs: pd.DataFrame, sims: dict) -> pd.DataFrame:
    """G statistic per (|coh|, outcome, RT bin) cell for each simulated model; probabilities within |coherence|."""
    edges = {c: np.quantile(g.rt[g.choice >= 0], np.linspace(0.1, 0.9, 9)) for c, g in obs.assign(abs_coh=obs.coh.abs()).groupby("abs_coh")}
    keys = ["abs_coh", "outcome", "rt_bin"]
    o = label_cells(obs, edges)
    n_obs = o.groupby(keys).size().rename("n_obs")
    p_obs = n_obs / n_obs.groupby(level="abs_coh").transform("sum")
    out = pd.DataFrame({"n_obs": n_obs})
    for name, sim in sims.items():
        s = label_cells(sim, edges).groupby(keys).size()
        p_mod = (s.reindex(n_obs.index).fillna(0) + 0.5) / (s.groupby(level="abs_coh").sum().reindex(n_obs.index.get_level_values("abs_coh")).to_numpy() + 0.5)
        out[name] = 2 * n_obs * np.log(p_obs / p_mod)
    out = out.reset_index()
    rt_mid = {c: np.concatenate([[0], e, [np.inf]]) for c, e in edges.items()}
    out["rt_lo"] = [rt_mid[c][b] if b >= 0 else np.nan for c, b in zip(out.abs_coh, out.rt_bin)]
    out["rt_range"] = pd.cut(out.rt_lo, [-1, 0.6, 1.5, np.inf], labels=list(RT_RANGES), right=False).astype(str).str.replace("nan", "(no RT)")
    return out


def data_features(obs: pd.DataFrame) -> pd.Series:
    r = obs[obs.choice >= 0].assign(abs_coh=obs.coh.abs())
    r = r[r.abs_coh > 0].assign(correct=lambda x: (x.choice == 1) == (x.coh > 0))
    f = {}
    for lo_hi_name, (lo, hi) in RT_RANGES.items():
        sub = r[(r.rt >= lo) & (r.rt < hi)]
        f[f"acc {lo_hi_name}"] = sub.correct.mean()
        f[f"frac {lo_hi_name}"] = len(sub) / len(r)
    for q in [0.25, 0.5, 0.9]:
        f[f"RT q{int(q * 100)} correct, |coh|>=0.36"] = r[r.correct & (r.abs_coh >= 0.36)].rt.quantile(q)
    f["no response"] = (obs.choice < 0).mean()
    f["n control"] = len(obs)
    return pd.Series(f)


def data_checks(inputs: dict):
    feats = {}
    for mouse in sorted(np.unique(inputs["subject_id"])):
        _, _, _, obs, rig = control_trials(inputs, mouse)
        feats[f"{mouse} ({rig})"] = data_features(obs)
    ft = pd.DataFrame(feats).T.sort_index(key=lambda i: i.str.contains("uw"))
    print("\n2. data only, control trials (accuracy excludes 0%; 'no response' = censored, > 5 s):")
    print(ft.round(3).to_string())


def late_responses():
    c = pd.read_csv(PROCESSED / "censored_trials.csv")
    c["late"] = c.censored_rt.notna()
    print("\n3. censored trials: share that are responses after 5 s (rest: no response recorded), per mouse:")
    print(c.groupby("subject_id").late.agg(["mean", "size"]).round(2).T.to_string())
    r = c[c.late].assign(abs_coh=lambda x: x.signed_coherence.abs())
    r = r[r.abs_coh > 0].assign(correct=lambda x: (x.choice == 1) == (x.signed_coherence > 0))
    print("RT of responses after 5 s, quantiles (s):", c.censored_rt.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(1).to_dict())
    print("accuracy by rig and |coherence|:")
    print(r.groupby(["data_source", "abs_coh"]).correct.agg(["mean", "count"]).round(2).T.to_string())
    strong = r[r.abs_coh >= 0.36]
    print("accuracy at |coh| >= 36%, per mouse:")
    print(strong.groupby("subject_id").correct.agg(["mean", "count"]).round(2).T.to_string())
    print("accuracy at |coh| >= 36%, by RT window (s):")
    print(strong.groupby(pd.cut(strong.censored_rt, [5, 8, 15, 61]), observed=True).correct.agg(["mean", "count"]).round(2).T.to_string())


def censored_by_coherence(inputs: dict, mice: list[str]):
    print("\n4. P(censored, > 5 s) by |coherence| (%), control trials:")
    out = {}
    for mouse in mice:
        obs = control_trials(inputs, mouse)[3]
        out[mouse] = obs.assign(a=(obs.coh.abs() * 100).round().astype(int)).groupby("a").choice.apply(lambda c: (c < 0).mean())
    print(pd.DataFrame(out).T.round(3).to_string())


def main(mice: list[str], n_reps: int, data_only: bool = False):
    logging.disable(logging.WARNING)
    inputs = load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz")
    if data_only:
        data_checks(inputs)
        late_responses()
        censored_by_coherence(inputs, mice)
        return
    summary, by_cell = [], {}
    for mouse in mice:
        rows, data, stim, obs, rig = control_trials(inputs, mouse)
        sims = {v: simulate(v, mouse, data, stim, obs.coh.to_numpy(), rig, n_reps) for v in [STRICT, FULL]}
        m = misfit(obs, sims)
        by_cell[mouse] = (obs, sims)
        m["gain"] = m[STRICT] - m[FULL]  # positive: the full model fits this cell better
        g = m.groupby(["outcome", "rt_range"]).gain.sum().round(1)
        summary.append(g.rename(f"{mouse} ({rig})"))
        print(f"{mouse} ({rig}, {len(obs)} control trials): total G strict {m[STRICT].sum():.1f}, full {m[FULL].sum():.1f}")
    print("\n1. misfit removed by leak + urgency (G strict - G full), by outcome and RT range; positive = full model better:")
    print(pd.concat(summary, axis=1).fillna(0).to_string())

    data_checks(inputs)
    late_responses()
    censored_by_coherence(inputs, mice)

    fig, axes = plt.subplots(2, len(mice), figsize=(3.0 * len(mice), 5.6), sharey="row", squeeze=False)
    bins = np.linspace(0.3, 5, 48)
    for j, mouse in enumerate(mice):
        obs, sims = by_cell[mouse]
        for row, keep in enumerate([lambda d: (d.choice >= 0) & (((d.choice == 1) == (d.coh > 0)) & (d.coh != 0)), lambda d: (d.choice >= 0) & (((d.choice == 1) != (d.coh > 0)) & (d.coh != 0))]):
            ax = axes[row, j]
            ax.hist(obs.rt[keep(obs)], bins=bins, density=True, color="0.7", label="data")
            for v, col in [(STRICT, "#d11149"), (FULL, "#1a8fe3")]:
                s = sims[v]
                h, e = np.histogram(s.rt[keep(s)], bins=bins, density=True)
                ax.plot(0.5 * (e[1:] + e[:-1]), h * keep(s).sum() / len(s) * len(obs) / keep(obs).sum(), color=col, lw=1.5, label=v)
            ax.set_title(f"{mouse}, {'correct' if row == 0 else 'error'}", fontsize=9, loc="left")
            ax.set_yscale("log")
        axes[1, j].set_xlabel("RT (s)")
    axes[0, 0].legend(fontsize=7, frameon=False)
    fig.suptitle("Control trials, RT density (model scaled to the data's share of responses); log scale", fontsize=10)
    fig.tight_layout()
    out = Path("dissemination/figures") / f"leak_urgency_diagnosis_{datetime.date.today():%Y%m%d}.png"
    fig.savefig(out, dpi=110)
    print(f"\nfigure: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mice", nargs="+", default=["PSUIM10", "PSUIM5", "PSUIM6", "PSUIM7", "DBM12", "DBM13", "DBM14", "DBM15", "DBM5", "DBM6"])
    parser.add_argument("--n_reps", type=int, default=20)
    parser.add_argument("--data_only", action="store_true", help="skip the simulations (checks 2-4 only)")
    args = parser.parse_args()
    main(args.mice, args.n_reps, args.data_only)
