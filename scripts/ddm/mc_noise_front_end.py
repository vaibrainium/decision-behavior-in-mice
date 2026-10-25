"""Monte Carlo noise of the amendment 7 front-end comparison (item 3): F1 (power law) vs F0 (no front end), on the
control-only CV folds (ccv0-ccv4), 15 repetitions as in the fits.

Re-scores the saved ccv fits (no refitting) of each model at 10 evaluation seeds. All models share the noise draws of
a given seed, so the relevant noise is the spread across seeds of the summed difference F1 - F0. Seed EVAL_SEED must
reproduce each saved test_nll (checked). --summarize reports: the summed difference at the grid's seed (the value the
selection used), its mean over seeds, the SD across seeds, and whether the grid-seed difference exceeds 2 SD.
No pulse trial is used.

Usage:
    python -m scripts.ddm.mc_noise_front_end --list
    python -m scripts.ddm.mc_noise_front_end --job_id 3
    python -m scripts.ddm.mc_noise_front_end --summarize
On Slurm: sbatch --array=0-19 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.mc_noise_front_end scripts/slurm/fit_mouse_ddm.slurm
"""

import argparse
import logging
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import CENSOR_AT, DEVICE, EVAL_SEED, LIKELIHOOD_PARAMS, MIN_RT, N_FOLDS, MouseDDM, cv_folds, heldout_nll, load_inputs, make_params, select

logger = logging.getLogger(__name__)

VARIANT, GUESS_MODEL = "L0U0V1Z0G1", "fast_only"
MODELS = {"F0": ("ddm/fits_guess_fast_only", None), "F1": ("ddm/fits_guess_fast_only_fe-power", "power")}
SEEDS = [EVAL_SEED] + list(range(1, 10))
N_REPS = 15


def build_grid(inputs: dict) -> list[dict]:
    return [{"mouse": m, "model": k} for k in MODELS for m in sorted(np.unique(inputs["subject_id"]))]


def run_job(inputs: dict, job: dict, processed: Path) -> pd.DataFrame:
    fits_dir, front_end = MODELS[job["model"]]
    mouse_rows = np.flatnonzero(inputs["subject_id"] == job["mouse"])
    control_rows = mouse_rows[inputs["sched_pulse_type"][mouse_rows] == 0]
    folds = cv_folds(inputs["condition"][control_rows], N_FOLDS)  # as fit_mouse_ddm's ccv splits
    rig = np.unique(inputs["data_source"][mouse_rows]).item()
    free, fixed = make_params(VARIANT, GUESS_MODEL, front_end=front_end)
    model = MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])
    rows = []
    for k in range(N_FOLDS):
        with open(processed / fits_dir / f"{job['mouse']}_{VARIANT}_ccv{k}.pkl", "rb") as f:
            fit = pickle.load(f)
        assert fit.get("front_end") == front_end and fit.get("guess_model") == GUESS_MODEL and fit["n_reps"] == N_REPS
        data, stimulus = select(inputs, control_rows[folds == k])
        for seed in SEEDS:
            t0 = time.time()
            nll = heldout_nll(model, fit["parameters"], data, stimulus, N_REPS, seed)
            rows.append({**job, "fold": k, "seed": seed, "test_nll": nll, "seconds": time.time() - t0,
                         "saved_test_nll": fit["test_nll"] if seed == EVAL_SEED else np.nan})
            if seed == EVAL_SEED:
                ok = np.isclose(nll, fit["test_nll"], rtol=0, atol=1e-3)
                (logger.info if ok else logger.error)("%s fold %d: rescored %.3f vs saved %.3f (%s)", job, k, nll, fit["test_nll"], "reproduced" if ok else "MISMATCH")
        model.simulator.clear_cache()
    return pd.DataFrame(rows)


def summarize(out_dir: Path) -> None:
    df = pd.concat([pd.read_pickle(p) for p in sorted(out_dir.glob("*.pkl"))], ignore_index=True)
    check = df.dropna(subset=["saved_test_nll"])
    print(f"reproduced saved test_nll: {np.isclose(check.test_nll, check.saved_test_nll, rtol=0, atol=1e-3).sum()} / {len(check)}")
    cv = df.pivot_table(index=["seed", "mouse", "fold"], columns="model", values="test_nll")
    d = (cv["F1"] - cv["F0"]).dropna()
    summed = d.groupby(level="seed").sum()
    per_mouse = d.groupby(level=["seed", "mouse"]).sum().groupby(level="mouse").agg(["mean", "std"])
    grid = summed.loc[EVAL_SEED]
    sd = summed.std()
    print(f"F1 - F0 held-out NLL summed over mice and folds: grid seed {grid:.1f}; mean over {len(summed)} seeds {summed.mean():.1f}; SD across seeds {sd:.1f}")
    print(f"2 SD = {2 * sd:.1f}; grid-seed difference beyond 2 SD in F1's favour: {grid < -2 * sd}; mean over seeds beyond 2 SD: {summed.mean() < -2 * sd}")
    print("\nper mouse (sum over folds), mean and SD across seeds:")
    print(per_mouse.round(1).to_string())
    pd.DataFrame({"summed_by_seed": summed}).to_csv(out_dir / "mc_noise_front_end_summary.csv")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz")
    parser.add_argument("--out_dir", default="ddm/mc_noise_front_end")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    processed = Path(dir_config.data.processed)
    out_dir = processed / args.out_dir
    if args.summarize:
        summarize(out_dir)
    else:
        inputs = load_inputs(processed / args.inputs)
        grid = build_grid(inputs)
        if args.list:
            print(f"{len(grid)} jobs: {len(MODELS)} models x {len(grid) // len(MODELS)} mice; --array=0-{len(grid) - 1}")
        else:
            job = grid[args.job_id]
            out = out_dir / f"{job['mouse']}_{job['model']}.pkl"
            if out.exists():
                logger.info("skipping %s: output exists", job)
            else:
                df = run_job(inputs, job, processed)
                out_dir.mkdir(parents=True, exist_ok=True)
                tmp = out.with_suffix(".tmp")
                df.to_pickle(tmp)
                tmp.replace(out)
                logger.info("saved %s (%d evaluations)", out.name, len(df))
