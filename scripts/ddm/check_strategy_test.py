"""Validate the strategy test (primacy plan, amendment 5) on synthetic data only; no recorded pulse outcome is read.

1. Calibration: model A against itself (two independent prediction runs) on datasets simulated from A. The z
   statistics should have mean ~0 and SD <= 1 (the SD is conservative by construction).
2. Discrimination (machinery only): A against B = A with a 5-50 ms leak and scaled gain. This crude B is not a fitted
   extrema model and predicted no pulse effect in the check of 2026-10-23, so only the total statistic separates them;
   the real power check uses the fitted E (primacy plan, amendment 5, item 4).
Generating parameters: each mouse's control-only L0U0V1Z0G1 fit in --fits_dir (any guess form).

Usage: python -m scripts.ddm.check_strategy_test [--mice DBM13 DBM14 PSUIM10] [--datasets 20] [--n_reps 100]
       python -m scripts.ddm.check_strategy_test --null_only --datasets 150      # amendment 5 calibration
"""

import argparse
import logging
import pickle
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import load_inputs, select
from scripts.ddm.model_recovery import synthesize

VARIANT = "L0U0V1Z0G1"


def synthetic_tables(inputs, preds: dict, params: dict, variant: str, leak_bounds, tag: str) -> dict:
    tables = {}
    for m, pr in preds.items():
        rows = pr["trials"].row.to_numpy()
        rig = np.unique(inputs["data_source"][rows]).item()
        _, stim = select(inputs, rows)
        gen = primacy.make_model(variant, rig, leak_bounds=leak_bounds)
        syn = synthesize(gen, params[m], stim, inputs["condition"][rows], zlib.crc32(f"{m}|{tag}".encode()))
        gen.simulator.clear_cache()
        tables[m] = syn
    return tables


def null_calibration(inputs, A: dict, datasets: int, n_reps: int):
    """Model A against itself (prediction seeds 11, 12) on `datasets` datasets simulated from A."""
    mice = list(A)
    pa1 = {m: primacy.predict_mouse(inputs, m, A[m], VARIANT, n_reps, 11) for m in mice}
    pa2 = {m: primacy.predict_mouse(inputs, m, A[m], VARIANT, n_reps, 12) for m in mice}
    gens = {}
    for m in mice:
        rows = pa1[m]["trials"].row.to_numpy()
        _, stim = select(inputs, rows)
        gens[m] = (primacy.make_model(VARIANT, np.unique(inputs["data_source"][rows]).item()), stim, inputs["condition"][rows])
    z, sums = {"pulse_gain": [], "total": []}, {"pulse_gain": [], "total": []}
    for d in range(datasets):
        syn = {m: synthesize(g, A[m], st, c, zlib.crc32(f"null|{m}|{d}".encode())) for m, (g, st, c) in gens.items()}
        r = primacy.strategy_test({m: primacy.attach_observed(pa1[m], syn[m]["rt"], syn[m]["choice"]) for m in mice},
                                  {m: primacy.attach_observed(pa2[m], syn[m]["rt"], syn[m]["choice"]) for m in mice})
        for k in z:
            z[k].append(r[k]["z"])
            sums[k].append(r[k]["sum"])
    for k in z:
        a, s = np.array(z[k]), np.array(sums[k])
        print(f"{k}: null z mean {a.mean():.2f}, SD {a.std():.2f}, |z| > 3 in {(abs(a) > 3).sum()}/{datasets}; "
              f"SD of the sums {s.std():.2f} vs mean estimated SD {np.mean(s / a):.2f}")


def main(mice, datasets, n_reps, fits_dir, leak, null_only=False):
    logging.disable(logging.WARNING)
    inputs = load_inputs(Path(dir_config.data.processed) / "ddm/ddm_inputs_global.npz")
    A = {m: pickle.load(open(fits_dir / f"{m}_{VARIANT}_control.pkl", "rb"))["parameters"] for m in mice}
    if null_only:
        null_calibration(inputs, A, datasets, n_reps)
        return
    # B: same parameters with a short time constant; drift gain scaled by the leak so the steady-state signal matches
    # the integrator's evidence after ~1 s (a crude stand-in, not a fit)
    B = {m: {**A[m], "leak_rate": leak, "drift_gain": min(A[m]["drift_gain"] * leak / 4, 200.0)} for m in mice}
    bounds = (20.0, 200.0)
    pa1 = {m: primacy.predict_mouse(inputs, m, A[m], VARIANT, n_reps, 1) for m in mice}
    pa2 = {m: primacy.predict_mouse(inputs, m, A[m], VARIANT, n_reps, 2) for m in mice}
    pb = {m: primacy.predict_mouse(inputs, m, B[m], "L1U0V1Z0G1", n_reps, 3, leak_bounds=bounds) for m in mice}
    t = pd.concat([p["trials"] for p in pb.values()])
    t = t[t.coh.abs() <= 0.36 + 1e-9]
    print("predicted pulse effect (logit) by timing, B:", (primacy.logit(t.p_hat) - primacy.logit(t.nopulse_p_hat)).groupby(t.timing).mean().round(3).to_dict())

    rows = []
    for d in range(datasets):
        for gen_name, params, variant, lb in [("A", A, VARIANT, None), ("B", B, "L1U0V1Z0G1", bounds)]:
            syn = synthetic_tables(inputs, pa1, params, variant, lb, f"{gen_name}|{d}")
            obs = lambda preds: {m: primacy.attach_observed(preds[m], syn[m]["rt"], syn[m]["choice"]) for m in mice}  # noqa: E731
            if gen_name == "A":
                null = primacy.strategy_test(obs(pa1), obs(pa2))
                rows.append({"test": "A vs A (null)", "dataset": d, **{f"{k}_z": null[k]["z"] for k in ("pulse_gain", "total")}, **{f"{k}_fav": null[k]["favoured"] for k in ("pulse_gain", "total")}})
            r = primacy.strategy_test(obs(pa1), obs(pb))  # a = A, b = B
            rows.append({"test": f"A vs B, data from {gen_name}", "dataset": d, **{f"{k}_z": r[k]["z"] for k in ("pulse_gain", "total")}, **{f"{k}_fav": r[k]["favoured"] for k in ("pulse_gain", "total")}})
        print(rows[-3:], flush=True)
    df = pd.DataFrame(rows)
    print(df.groupby("test")[["pulse_gain_z", "total_z"]].agg(["mean", "std"]).round(2).to_string())
    for c in ["pulse_gain_fav", "total_fav"]:
        print(c, df.groupby("test")[c].value_counts().unstack(fill_value=0).to_string(), sep="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mice", nargs="+", default=["DBM13", "DBM14", "PSUIM10"])
    parser.add_argument("--datasets", type=int, default=20)
    parser.add_argument("--n_reps", type=int, default=100)
    parser.add_argument("--leak", type=float, default=50.0)
    parser.add_argument("--fits_dir", default="ddm/fits_guess")
    parser.add_argument("--null_only", action="store_true", help="calibration only (the amendment 5 numbers: --null_only --datasets 150)")
    args = parser.parse_args()
    main(args.mice, args.datasets, args.n_reps, Path(dir_config.data.processed) / args.fits_dir, args.leak, args.null_only)
