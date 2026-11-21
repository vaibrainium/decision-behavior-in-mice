"""Pre-fit profile of the transient channel (plan 2026-11-20-transient-channel, step 2). Takes the fitted pulse-only
norm UGM no-sv fits (fits_pulse_norm_ugm, L1U1V0Z0G1, pcv0-4), adds the transient term x'' = x' + fe_h (x' - LP_tau_h(x'))
with every other parameter fixed, and scores the held-out pcv fold (audit scorer, nbins 9). fe_h = 0 must reproduce the
stored test NLL at seed 12345. Also reports the early low-coherence pulse residual (|pulse type| == 1, |coh| 0/9/18).
Output: <output>/profile.csv (one row per mouse, fold, fe_h, fe_tau_h, seed).
Usage: PYTHONPATH=/src .venv/bin/python -W ignore -m scripts.paper.transient_profile --output <new dir>"""
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
GRID = [(0.0, 0.1)] + list(itertools.product([1.0, 3.0, 10.0], [0.05, 0.15]))


def run(out, mice, seeds):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs()
    rows = []
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
            model = make_model(r["variant"], rig, r["fixed_guess_bias"], responded=True, front_end="norm_transient", ugm=True)
            for (h, tau_h), seed in itertools.product(GRID, seeds):
                np.random.seed(seed)
                model.simulator.clear_cache()
                model._labels = data["condition"]
                model.precompute(*model._stimulus_shape(stim), n_reps=r["n_reps"])
                sim = model._simulate_condition(stim, {**r["parameters"], "fe_h": h, "fe_tau_h": tau_h}, r["n_reps"])
                frame, native = predictive_score(model.likelihood_calc, data, sim, training,
                                                 x["signed_coherence"][test], x["sched_pulse_type"][test])
                c = frame.pivot_table(index=["condition", "coherence", "scheduled_pulse"], columns="side",
                                      values=["n", "p_side"], aggfunc="first").reset_index()
                el = c[(c.scheduled_pulse.abs() == 1) & c.coherence.abs().isin([0, 9, 18])]
                n = el[("n", 0)] + el[("n", 1)]
                resid = ((el[("n", 1)] - el[("p_side", 1)] * n) * np.sign(el.scheduled_pulse)).sum() / n.sum()
                rows.append(dict(mouse=mouse, fold=fold, fe_h=h, fe_tau_h=tau_h, seed=seed, nll=native, stored=r["test_nll"],
                                 choice_nll=frame.choice_nll.sum(), rt_nll=frame.rt_nll.sum(), early_lowcoh_resid=resid))
            model.simulator.clear_cache()
        print(mouse, "complete", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "profile.csv", index=False)
    base = df[df.fe_h == 0].set_index(["mouse", "fold", "seed"]).nll
    df["dnll"] = df.nll - df.set_index(["mouse", "fold", "seed"]).index.map(base)
    z = df[(df.fe_h == 0) & (df.seed == 12345)]
    print("fe_h = 0 vs stored, seed 12345: max |diff| =", round((z.nll - z.stored).abs().max(), 3))
    t = df.groupby(["mouse", "fe_h", "fe_tau_h", "seed"]).agg(dnll=("dnll", "sum"), resid=("early_lowcoh_resid", "mean"))
    print(t.groupby(["mouse", "fe_h", "fe_tau_h"]).agg(dnll_mean=("dnll", "mean"), dnll_sd=("dnll", "std"),
                                                       resid_pp=("resid", lambda s: 100 * s.mean())).round(2).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--mice", nargs="+", default=["PSUIM6", "PSUIM7", "DBM5", "DBM12"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456])
    a = ap.parse_args()
    run(a.output, a.mice, a.seeds)
