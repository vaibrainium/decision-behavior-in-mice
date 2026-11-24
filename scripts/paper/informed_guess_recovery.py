"""Recovery check for informed fast guesses (plan 2026-11-24-informed-guess-family, step 4).

Synthetic data: PSUIM7's pulse trials simulated once from its full pulse-only norm UGM no-sv fit, with guess_w and
read_lag set to known values (one dataset = the real trial count; responded trials kept, as in the fits). Then
guess_w and read_lag alone are fitted by the production MouseDDM.fit (DE + refinement, qmle_censored nbins 9, n_reps 15,
tol 0, atol 1), every other parameter fixed at its true value. This is a best case: if two parameters cannot be
recovered with everything else known, the full family cannot identify them either.
Output: <output>/recovery.csv
Usage: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=8 .venv/bin/python -W ignore -m scripts.paper.informed_guess_recovery --output <new dir>"""
import argparse
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import CENSOR_AT, MIN_RT, RESPONDED_LIKELIHOOD_PARAMS, MouseDDM, select
from scripts.ddm.rescore_fits import inputs
from src.ddm.ddm import FixedParam, FreeParam

DDM = Path("/mnt/data/processed/ddm")
TRUTHS = [(0.5, 0.12), (0.25, 0.2), (0.0, 0.1)]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--mouse", default="PSUIM7")
    ap.add_argument("--datasets", type=int, default=2)
    ap.add_argument("--max_iterations", type=int, default=60)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    x = inputs()
    with (DDM / "fits_pulse_norm_ugm" / f"{a.mouse}_L1U1V0Z0G1_pulse.pkl").open("rb") as f:
        full = pickle.load(f)
    rows_all = np.flatnonzero((x["subject_id"] == a.mouse) & (x["sched_pulse_type"] != 0))
    rig = np.unique(x["data_source"][rows_all]).item()
    _, stim_all = select(x, rows_all)
    cond_all = x["condition"][rows_all]
    base = dict(full["parameters"])
    out = []
    for w_true, lag_true in TRUTHS:
        for ds in range(a.datasets):
            truth = {**base, "guess_w": w_true, "read_lag": lag_true}
            gen = MouseDDM(fixed_params={k: FixedParam(v) for k, v in truth.items()}, likelihood_params=RESPONDED_LIKELIHOOD_PARAMS,
                           censor_at=CENSOR_AT, min_rt=MIN_RT[rig])
            sim = gen._map_outcomes(gen.simulate(stim_all, truth, n_reps=1, seed=1000 + ds, labels=cond_all))
            sim = sim[sim.choice >= 0]
            keep = sim.trial.to_numpy()
            data = {"rt": sim.rt.to_numpy(), "choice": sim.choice.to_numpy(), "condition": cond_all[keep]}
            stim = stim_all[keep]
            fixed = {k: FixedParam(v) for k, v in base.items() if k not in ("guess_w", "read_lag")}
            model = MouseDDM(free_params={"guess_w": FreeParam(0.0, 1.0), "read_lag": FreeParam(0.05, 0.5)}, fixed_params=fixed,
                             likelihood_params=RESPONDED_LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])
            t0 = time.monotonic()
            fit = model.fit(data=data, stimulus=stim, labels=data["condition"], n_reps=15, max_iterations=a.max_iterations,
                            l1_weight=0.0, verbose=False, tol=0.0, atol=1.0)
            est = fit["parameters"] if "parameters" in fit else fit
            # likelihood at the truth with the same common random numbers, for reference
            nll_truth = model._objective_function(np.array([w_true, lag_true]), data, stim, 15, 0.0)
            row = dict(mouse=a.mouse, w_true=w_true, lag_true=lag_true, dataset=ds, n_trials=len(keep),
                       w_hat=float(est["guess_w"]), lag_hat=float(est["read_lag"]), nll_hat=float(fit["likelihood"]),
                       nll_truth=float(nll_truth), seconds=time.monotonic() - t0)
            out.append(row)
            print(row, flush=True)
            model.simulator.clear_cache()
    pd.DataFrame(out).to_csv(a.output / "recovery.csv", index=False)


if __name__ == "__main__":
    main()
