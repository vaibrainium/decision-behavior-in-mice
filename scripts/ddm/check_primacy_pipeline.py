"""Validate the primacy pipeline on synthetic data only (no recorded pulse-trial outcome is read).

Generating parameters: each mouse's control-only fit of L0U0V1Z0G1 from --fits_dir (any guess form; this checks the
machinery, not results). For each level of added gain decay, simulate synthetic outcomes for every real trial,
predict the pulse trials from the generating parameters without the decay (as primacy_sensitivity --no_refit), and
run the gate and the GLMMs (primacy.run_analysis, gate not required). Expected: level 0 gives b_middle near 0 with
an interval covering 0 and a passing gate; a large decay gives b_middle < 0. Also checks that predictions are
reproducible with a fixed seed.

Usage: python -m scripts.ddm.check_primacy_pipeline [--mice DBM13 DBM14 PSUIM10] [--levels 0 0.4 0.8] [--n_reps 50]
"""

import argparse
import logging
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import load_inputs, select
from scripts.ddm.model_recovery import synthesize
from scripts.ddm.primacy_sensitivity import VARIANT, gain_decay


def main(mice: list[str], levels: list[float], n_reps: int, fits_dir: Path, datasets: int):
    logging.disable(logging.WARNING)
    inputs = load_inputs(Path(dir_config.data.processed) / "ddm/ddm_inputs_global.npz")
    import pickle
    truth = {m: pickle.load(open(fits_dir / f"{m}_{VARIANT}_control.pkl", "rb"))["parameters"] for m in mice}

    a = primacy.predict_mouse(inputs, mice[0], truth[mice[0]], VARIANT, 5, 7)["trials"]
    b = primacy.predict_mouse(inputs, mice[0], truth[mice[0]], VARIANT, 5, 7)["trials"]
    print(f"predictions reproducible with a fixed seed: {a.equals(b)}")

    preds = {m: primacy.predict_mouse(inputs, m, truth[m], VARIANT, n_reps, 1) for m in mice}  # baseline: no decay
    print("mean predicted pulse effect (logit), |coh| <= 36%, by timing:")
    t = pd.concat([p["trials"] for p in preds.values()])
    t = t[t.coh.abs() <= 0.36 + 1e-9]
    print((primacy.logit(t.p_hat) - primacy.logit(t.nopulse_p_hat)).groupby([t.mouse, t.timing]).mean().unstack().round(2).to_string())
    rows = []
    for level in levels:
        for d in range(datasets):
            tables = {}
            for m in mice:
                r = np.flatnonzero(inputs["subject_id"] == m)
                rig = np.unique(inputs["data_source"][r]).item()
                _, stim = select(inputs, r)
                gen = primacy.make_model(VARIANT, rig, time_varying_gain=True)
                syn = synthesize(gen, {**truth[m], "gain_decay": gain_decay(level)}, stim, inputs["condition"][r], zlib.crc32(f"{m}|{level}|{d}".encode()))
                gen.simulator.clear_cache()
                pulse = np.isin(r, preds[m]["trials"].row.to_numpy())
                tables[m] = primacy.attach_observed(preds[m], syn["rt"][pulse], syn["choice"][pulse])
            res = primacy.run_analysis(preds, tables, require_gate=False, draws=500, tune=500, chains=4)
            row = {"level": level, "dataset": d, "gate_pass": res["gate_pass"], "b0": round(res["gate_departure"]["b0"]["mean"], 3),
                   "b_middle": round(res["primary"]["b_middle"]["mean"], 3), "middle_lo": round(res["primary"]["b_middle"]["lo"], 3), "middle_hi": round(res["primary"]["b_middle"]["hi"], 3),
                   "divergences": res["primary"]["divergences"], "max_rhat": round(res["primary"]["max_rhat"], 3)}
            if "uw_late" in res:
                row.update(b_late=round(res["uw_late"]["b_late"]["mean"], 3), late_hi=round(res["uw_late"]["b_late"]["hi"], 3))
            rows.append(row)
            print(row, flush=True)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mice", nargs="+", default=["DBM13", "DBM14", "PSUIM10"])
    parser.add_argument("--levels", nargs="+", type=float, default=[0.0, 0.4, 0.8])
    parser.add_argument("--n_reps", type=int, default=50)
    parser.add_argument("--datasets", type=int, default=2)
    parser.add_argument("--fits_dir", default="ddm/fits_guess", help="relative to processed")
    args = parser.parse_args()
    main(args.mice, args.levels, args.n_reps, Path(dir_config.data.processed) / args.fits_dir, args.datasets)
