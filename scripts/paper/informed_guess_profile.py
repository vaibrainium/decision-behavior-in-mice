"""Pre-fit profile of informed fast guesses (plan 2026-11-24-informed-guess-family, step 3).

Takes the fitted pulse-only norm UGM no-sv fits (fits_pulse_norm_ugm, L1U1V0Z0G1, pcv0-4) and adds informed guesses
(guess_w, read_lag) with every other parameter fixed. Scores the held-out pcv fold (audit scorer, nbins 9); guess_w = 0
must reproduce the stored test NLL at seed 12345. Also per held-out fold: the early-pulse right-minus-left effect among
responses < 0.6 s (|coh| <= 36). Control guardrail: the full "pulse" fit simulated on the mouse's control trials,
fast (< 0.6 s) accuracy by |coherence|, against the data.
Outputs: <output>/profile.csv, control_guardrail.csv.
Usage: OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.informed_guess_profile --output <new dir>"""
import argparse
import itertools
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import N_FOLDS, cv_folds, select
from scripts.ddm.primacy import make_model
from scripts.ddm.rescore_fits import inputs
from scripts.paper.audit_pulse_choice_rt_score import predictive_score

DDM = Path("/mnt/data/processed/ddm")
FOLDER, VARIANT = "fits_pulse_norm_ugm", "L1U1V0Z0G1"
GRID = [(0.0, 0.1)] + list(itertools.product([0.25, 0.5, 1.0], [0.1, 0.2, 0.3]))


def fast_pulse_effect(sim, coh, pulse_type, n_trials):
    """Equal-coherence mean of P(right | right early pulse) - P(right | left early pulse), responses 0.3-0.6 s."""
    t = sim["trial"].to_numpy()
    d = pd.DataFrame({"coh": coh[t], "pt": pulse_type[t], "rt": sim["rt"].to_numpy(), "R": (sim["choice"].to_numpy() == 1)})
    d = d[(np.abs(d.pt) == 1) & (d.coh.abs() <= 36) & (d.rt < 0.6) & np.isfinite(d.rt)]
    e = d.groupby(["coh", np.sign(d.pt)]).R.mean().unstack()
    return float(100 * (e[1] - e[-1]).dropna().mean()) if {1, -1} <= set(e.columns) else np.nan


def run(out, mice, seeds):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs()
    rows, guard = [], []
    for mouse in mice:
        pulse_rows = np.flatnonzero((x["subject_id"] == mouse) & (x["sched_pulse_type"] != 0))
        folds = cv_folds(x["condition"][pulse_rows], N_FOLDS)
        rig = np.unique(x["data_source"][pulse_rows]).item()
        for fold in range(N_FOLDS):
            test, train = pulse_rows[folds == fold], pulse_rows[folds != fold]
            data, stim = select(x, test)
            training = {k: x[k][train] for k in ("rt", "choice", "condition")}
            with (DDM / FOLDER / f"{mouse}_{VARIANT}_pcv{fold}.pkl").open("rb") as f:
                r = pickle.load(f)
            assert r["split"] == f"pcv{fold}" and r["n_test"] == len(test) and r["front_end"] == "norm" and r.get("ugm")
            model = make_model(r["variant"], rig, r["fixed_guess_bias"], responded=True, front_end="norm", ugm=True)
            for (w, lag), seed in itertools.product(GRID, seeds):
                np.random.seed(seed)
                model.simulator.clear_cache()
                model._labels = data["condition"]
                model.precompute(*model._stimulus_shape(stim), n_reps=r["n_reps"])
                params = {**r["parameters"], "guess_w": w, "read_lag": lag}
                sim = model._simulate_condition(stim, params, r["n_reps"])
                frame, native = predictive_score(model.likelihood_calc, data, sim, training,
                                                 x["signed_coherence"][test], x["sched_pulse_type"][test])
                fsim = model._map_outcomes(model.simulate(stim, params, n_reps=5, seed=seed, labels=data["condition"]))
                rows.append(dict(mouse=mouse, fold=fold, guess_w=w, read_lag=lag, seed=seed, nll=native, stored=r["test_nll"],
                                 choice_nll=frame.choice_nll.sum(), rt_nll=frame.rt_nll.sum(),
                                 fast_early_pulse_pp=fast_pulse_effect(fsim, x["signed_coherence"][test], x["sched_pulse_type"][test], len(test)),
                                 data_fast_early_pulse_pp=fast_pulse_effect(pd.DataFrame({"trial": np.arange(len(test)), "rt": data["rt"], "choice": data["choice"]}),
                                                                            x["signed_coherence"][test], x["sched_pulse_type"][test], len(test))))
            model.simulator.clear_cache()
        # control guardrail with the full pulse fit (fit on pulse trials only; control trials are out of sample)
        with (DDM / FOLDER / f"{mouse}_{VARIANT}_pulse.pkl").open("rb") as f:
            full = pickle.load(f)
        ctrl = np.flatnonzero((x["subject_id"] == mouse) & (x["sched_pulse_type"] == 0) & (x["signed_coherence"] != 0))
        data, stim = select(x, ctrl)
        coh = x["signed_coherence"][ctrl]
        ok = np.isfinite(data["rt"]) & (data["choice"] >= 0) & (data["rt"] < 0.6)
        obs = pd.Series((np.sign(coh[ok]) > 0) == (data["choice"][ok] == 1)).groupby(np.abs(coh[ok])).agg(["mean", "size"])
        model = make_model(full["variant"], rig, full["fixed_guess_bias"], responded=True, front_end="norm", ugm=True)
        for (w, lag) in GRID:
            sim = model._map_outcomes(model.simulate(stim, {**full["parameters"], "guess_w": w, "read_lag": lag},
                                                     n_reps=10, seed=12345, labels=data["condition"]))
            t = sim["trial"].to_numpy()
            fast = (sim["rt"].to_numpy() < 0.6) & (sim["choice"].to_numpy() >= 0)
            acc = pd.Series((np.sign(coh[t][fast]) > 0) == (sim["choice"].to_numpy()[fast] == 1)).groupby(np.abs(coh[t][fast])).mean()
            for c in obs.index:
                guard.append(dict(mouse=mouse, guess_w=w, read_lag=lag, abs_coh=c, model_fast_acc=acc.get(c, np.nan),
                                  data_fast_acc=obs.loc[c, "mean"], data_n=int(obs.loc[c, "size"])))
        model.simulator.clear_cache()
        print(mouse, "complete", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "profile.csv", index=False)
    pd.DataFrame(guard).to_csv(out / "control_guardrail.csv", index=False)
    key = ["mouse", "fold", "seed"]
    base = df[df.guess_w == 0].set_index(key)
    df["dnll"] = df.nll - df.set_index(key).index.map(base.nll)
    df["dchoice"] = df.choice_nll - df.set_index(key).index.map(base.choice_nll)
    df["drt"] = df.rt_nll - df.set_index(key).index.map(base.rt_nll)
    z = df[(df.guess_w == 0) & (df.seed == 12345)]
    print("guess_w = 0 vs stored, seed 12345: max |diff| =", round((z.nll - z.stored).abs().max(), 4))
    t = df.groupby(["mouse", "guess_w", "read_lag", "seed"]).agg(dnll=("dnll", "sum"), dchoice=("dchoice", "sum"), drt=("drt", "sum"),
                                                                fast=("fast_early_pulse_pp", "mean"), data_fast=("data_fast_early_pulse_pp", "mean"))
    print(t.groupby(["mouse", "guess_w", "read_lag"]).agg(dnll_mean=("dnll", "mean"), dnll_sd=("dnll", "std"), dchoice=("dchoice", "mean"),
                                                         drt=("drt", "mean"), fast_pp=("fast", "mean"), data_fast_pp=("data_fast", "mean")).round(1).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--mice", nargs="+", default=["PSUIM6", "PSUIM7", "DBM5", "DBM12"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456])
    a = ap.parse_args()
    run(a.output, a.mice, a.seeds)
