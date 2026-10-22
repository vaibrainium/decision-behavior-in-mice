"""Sensitivity of the primacy test (locked plan section 9; next-steps step 6.6): how much primacy would we detect?

For each mouse, level and dataset: simulate the mouse's real trials (control and pulse, own stimuli, censoring and
floor) from its control-only fit of the primary baseline with primacy added, i.e. the drift gain decaying by
LEVELS (0, 10, 20, 40%) over the first 0.5 s (gain_decay = -ln(1 - level) / 0.5, the model's exponential form).
Then run the analysis unchanged on the synthetic data:
  - refit the control-only baseline (no gain decay) to the synthetic control trials (default; Hyak job), or use the
    generating parameters without the decay (--no_refit; local and approximate: the refit absorbs part of a decay
    into the other parameters, so --no_refit overstates sensitivity);
  - predict the synthetic pulse trials (primacy.predict_mouse) and save predictions + synthetic outcomes.
--summarize assembles the mice of each (level, dataset), runs the section 6 GLMMs (primacy.run_analysis, gate
recorded but not required) and reports, per level, how often the 95% interval of b_middle excludes 0 (and b_late
for UW). Level 0 gives the false-positive rate. Report the smallest level detected in >= 80% of datasets.

Usage:
    python -m scripts.ddm.primacy_sensitivity --list
    python -m scripts.ddm.primacy_sensitivity --job_id 5 --fits_dir ddm/fits_final [--no_refit] [--fixed_guess_bias]
    python -m scripts.ddm.primacy_sensitivity --summarize [--no_refit]
"""

import argparse
import logging
import pickle
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import DE_TOL, load_inputs, select
from scripts.ddm.model_recovery import synthesize

logger = logging.getLogger(__name__)

LEVELS = [0.0, 0.1, 0.2, 0.4]  # fractional decay of the drift gain over the first 0.5 s
N_DATASETS = 20  # plan section 9: >= 20 simulated datasets per level
DETECTION = 0.8
VARIANT = primacy.BASELINES["primary"]


def gain_decay(level: float) -> float:
    return -np.log(1 - level) / 0.5


def run_job(inputs: dict, job: dict, fits_dir: Path, refit: bool, fixed_guess_bias: bool, n_reps: int, fit_reps: int, max_iterations: int) -> dict:
    mouse = job["mouse"]
    truth = primacy.load_fit(fits_dir, mouse, VARIANT, "control", fixed_guess_bias)["parameters"]
    generating = {**truth, "gain_decay": gain_decay(job["level"])}
    rows = np.flatnonzero(inputs["subject_id"] == mouse)
    rig = np.unique(inputs["data_source"][rows]).item()
    _, stimulus = select(inputs, rows)
    seed = zlib.crc32(f"{mouse}|{job['level']}|{job['dataset']}".encode())
    generator = primacy.make_model(VARIANT, rig, fixed_guess_bias, time_varying_gain=True)
    synthetic = synthesize(generator, generating, stimulus, inputs["condition"][rows], seed)  # one outcome per real trial
    generator.simulator.clear_cache()

    params = dict(truth)
    t0 = time.time()
    if refit:
        control = inputs["sched_pulse_type"][rows] == 0
        model = primacy.make_model(VARIANT, rig, fixed_guess_bias)
        data = {k: synthetic[k][control] for k in ("rt", "choice", "condition")}
        start = np.array([truth[k] for k in model.fit_keys])  # warm start at the generating parameters
        fit = model.fit(data=data, stimulus=stimulus[control], labels=data["condition"], n_reps=fit_reps, max_iterations=max_iterations, l1_weight=0.0, verbose=False, seeds=[start], **DE_TOL)
        model.simulator.clear_cache()
        params = {**truth, **{k: float(v) for k, v in fit["parameters"].items()}}
    pred = primacy.predict_mouse(inputs, mouse, params, VARIANT, n_reps, seed + 2, fixed_guess_bias)
    pulse = np.isin(rows, pred["trials"].row.to_numpy())
    pred["synthetic"] = {"rt": synthetic["rt"][pulse], "choice": synthetic["choice"][pulse]}
    pred.update(job=job, generating=generating, refit=refit, fit_seconds=time.time() - t0)
    return pred


def build_grid(inputs: dict) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"level": lv, "dataset": d, "mouse": m} for lv in LEVELS for d in range(N_DATASETS) for m in mice]


def summarize(out_dir: Path, max_abs_coh: float | None = primacy.MAX_ABS_COH, **kw) -> pd.DataFrame:
    rows = []
    paths = sorted(out_dir.glob("*.pkl"))
    jobs = {}
    for p in paths:
        with open(p, "rb") as f:
            r = pickle.load(f)
        jobs.setdefault((r["job"]["level"], r["job"]["dataset"]), {})[r["mouse"]] = r
    for (level, dataset), preds in sorted(jobs.items()):
        tables = {m: primacy.attach_observed(pr, pr["synthetic"]["rt"], pr["synthetic"]["choice"]) for m, pr in preds.items()}
        res = primacy.run_analysis(preds, tables, max_abs_coh, require_gate=False, **kw)
        row = {"level": level, "dataset": dataset, "n_mice": len(preds), "gate_pass": res["gate_pass"]}
        for key, name in [("primary", "middle"), ("uw_late", "late"), ("uw_late", "middle")]:
            if key in res and f"b_{name}" in res[key]:
                b = res[key][f"b_{name}"]
                row[f"{key}_{name}_mean"], row[f"{key}_{name}_detected"] = b["mean"], b["hi"] < 0  # primacy: negative
        rows.append(row)
        logger.info("level %.1f dataset %d: %s", level, dataset, row)
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "sensitivity_summary.csv", index=False)
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz")
    parser.add_argument("--fits_dir", help="control-only fits of the primary baseline, relative to processed")
    parser.add_argument("--out_dir", help="relative to processed (default ddm/primacy_sensitivity[_norefit])")
    parser.add_argument("--no_refit", action="store_true")
    parser.add_argument("--fixed_guess_bias", action="store_true")
    parser.add_argument("--n_reps", type=int, default=primacy.N_REPS, help="prediction repetitions per pulse trial")
    parser.add_argument("--fit_reps", type=int, default=15)
    parser.add_argument("--max_iterations", type=int, default=1000)
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    out_dir = processed / (args.out_dir or ("ddm/primacy_sensitivity" + ("_norefit" if args.no_refit else "")))
    if args.summarize:
        df = summarize(out_dir)
        cols = [c for c in df if c.endswith("_detected")]
        table = df.groupby("level")[cols + ["gate_pass"]].mean()
        print(table.round(2).to_string())
        for c in cols:
            hit = table.index[(table[c] >= DETECTION) & (table.index > 0)]
            print(f"{c}: smallest decay detected in >= {DETECTION:.0%} of datasets: {hit.min() if len(hit) else 'none of ' + str(LEVELS[1:])}")
    else:
        inputs = load_inputs(processed / args.inputs)
        grid = build_grid(inputs)
        if args.list:
            print(f"{len(grid)} jobs: {len(LEVELS)} levels x {N_DATASETS} datasets x {len(grid) // len(LEVELS) // N_DATASETS} mice; --array=0-{len(grid) - 1}")
        else:
            job = grid[args.job_id]
            out = out_dir / f"{job['mouse']}_lv{job['level']:.2f}_ds{job['dataset']:02d}.pkl"
            if out.exists():
                logger.info("skipping %s: output exists", job)
            else:
                pred = run_job(inputs, job, processed / args.fits_dir, not args.no_refit, args.fixed_guess_bias, args.n_reps, args.fit_reps, args.max_iterations)
                out_dir.mkdir(parents=True, exist_ok=True)
                tmp = out.with_suffix(".tmp")
                with open(tmp, "wb") as f:
                    pickle.dump(pred, f)
                tmp.replace(out)
                logger.info("saved %s (%.0f s)", out.name, pred["fit_seconds"])
