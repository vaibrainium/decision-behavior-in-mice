"""Monte Carlo noise of the held-out model comparison (plan step 3.1).

Held-out NLLs are simulation-based, so a model difference of a few NLL may be noise. This re-scores the saved
cross-validation fits (no refitting) of the leading model and its nearest neighbours with several evaluation seeds,
at the grid's 15 repetitions and at 50. All models share the noise draws of a given seed (common random numbers),
so the threshold to use is the spread across seeds of the *difference* between two models, per mouse and summed over
mice; compare_noise() computes it.

Each job scores one (mouse, variant) on all 5 folds x SEEDS x N_REPS and saves one row per evaluation. Seed 12345
at 15 repetitions is the grid's own scoring and must reproduce the saved test_nll (checked and logged).

Usage:
    python -m scripts.ddm.mc_noise --list
    python -m scripts.ddm.mc_noise --job_id 17
    python -m scripts.ddm.mc_noise --summarize            # after all jobs: threshold table
On Slurm: sbatch --array=0-69 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.mc_noise scripts/slurm/fit_mouse_ddm.slurm
"""

import argparse
import itertools
import logging
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import CENSOR_AT, DEVICE, EVAL_SEED, LIKELIHOOD_PARAMS, MIN_RT, N_FOLDS, MouseDDM, cv_folds, heldout_nll, load_inputs, make_params, select

logger = logging.getLogger(__name__)

LEADING = "L1U1V1Z0G1"  # best summed held-out NLL in ddm/fits_guess (analysis log, section 5.4)
# The leading model, each of its mechanisms removed, sz added, and the runner-up (L1U0V1Z1G1, +38): the contrasts step 3.2 decides on.
VARIANTS = [LEADING] + [LEADING[:i + 1] + "0" + LEADING[i + 2:] for i in range(0, len(LEADING), 2) if LEADING[i + 1] == "1"] + ["L1U1V1Z1G1", "L1U0V1Z1G1"]
SEEDS = [EVAL_SEED] + list(range(1, 10))
N_REPS = [15, 50]


def build_grid(inputs: dict) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"mouse": m, "variant": v} for v in VARIANTS for m in mice]


def output_path(out_dir: Path, job: dict) -> Path:
    return out_dir / f"{job['mouse']}_{job['variant']}.pkl"


def run_job(inputs: dict, job: dict, fits_dir: Path, out_dir: Path) -> pd.DataFrame:
    mouse_rows = np.flatnonzero(inputs["subject_id"] == job["mouse"])
    folds = cv_folds(inputs["condition"][mouse_rows], N_FOLDS)
    rig = np.unique(inputs["data_source"][mouse_rows]).item()
    free, fixed = make_params(job["variant"])
    model = MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])
    rows = []
    for k in range(N_FOLDS):
        fit_path = fits_dir / f"{job['mouse']}_{job['variant']}_cv{k}.pkl"
        if not fit_path.exists():
            logger.warning("missing fit %s; fold skipped", fit_path.name)
            continue
        with open(fit_path, "rb") as f:
            fit = pickle.load(f)
        test_data, test_stimulus = select(inputs, mouse_rows[folds == k])
        for n_reps, seed in itertools.product(N_REPS, SEEDS):
            t0 = time.time()
            nll = heldout_nll(model, fit["parameters"], test_data, test_stimulus, n_reps, seed)
            rows.append({**job, "fold": k, "n_reps": n_reps, "seed": seed, "test_nll": nll, "seconds": time.time() - t0})
            if seed == EVAL_SEED and n_reps == fit["n_reps"]:
                ok = np.isclose(nll, fit["test_nll"], rtol=0, atol=1e-3)
                (logger.info if ok else logger.error)("fold %d: rescored %.3f vs saved %.3f (%s)", k, nll, fit["test_nll"], "reproduced" if ok else "MISMATCH")
                rows[-1]["saved_test_nll"] = fit["test_nll"]
        model.simulator.clear_cache()
    df = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = output_path(out_dir, job)
    tmp = path.with_suffix(".tmp")
    df.to_pickle(tmp)
    tmp.replace(path)  # atomic, as in fit_mouse_ddm
    logger.info("saved %s (%d evaluations)", path.name, len(df))
    return df


class _NumpyCompatUnpickler(pickle.Unpickler):
    """Reads pickles written under NumPy 2 (the cluster container) with NumPy 1 (numpy._core -> numpy.core)."""

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except ModuleNotFoundError:
            if not module.startswith("numpy._core"):
                raise
            return super().find_class("numpy.core" + module[len("numpy._core"):], name)


def read_rows(path: Path) -> pd.DataFrame:
    with open(path, "rb") as f:
        return _NumpyCompatUnpickler(f).load()


def compare_noise(df: pd.DataFrame, reference: str = LEADING) -> pd.DataFrame:
    """SD across seeds of the CV-summed NLL difference (variant - reference), per mouse and summed over mice.
    Only folds both models have are summed, so a missing fit does not shift the difference."""
    cv = df.pivot_table(index=["n_reps", "seed", "mouse", "fold"], columns="variant", values="test_nll")
    out = []
    for v in [c for c in cv.columns if c != reference]:
        d = (cv[v] - cv[reference]).dropna().groupby(level=["n_reps", "seed", "mouse"]).sum()
        per_mouse = d.groupby(level=["n_reps", "mouse"]).agg(["mean", "std"])
        summed = d.groupby(level=["n_reps", "seed"]).sum().groupby(level="n_reps").agg(["mean", "std"])
        for n_reps, s in summed.iterrows():
            pm = per_mouse.loc[n_reps]
            out.append({"variant": v, "n_reps": n_reps, "delta_summed": s["mean"], "sd_summed": s["std"], "sd_per_mouse_median": pm["std"].median(), "sd_per_mouse_max": pm["std"].max()})
    return pd.DataFrame(out)


def per_mouse_delta(df: pd.DataFrame, n_reps: int = 50, reference: str = LEADING) -> pd.DataFrame:
    """Per mouse: CV-summed NLL difference (variant - reference) averaged over the evaluation seeds, with its standard
    error (SD across seeds / sqrt(n seeds)). Averaging over seeds removes most of the evaluation noise."""
    cv = df[df.n_reps == n_reps].pivot_table(index=["seed", "mouse", "fold"], columns="variant", values="test_nll")
    out = {}
    for v in [c for c in cv.columns if c != reference]:
        d = (cv[v] - cv[reference]).dropna().groupby(level=["seed", "mouse"]).sum().groupby(level="mouse")
        out[(v, "mean")], out[(v, "se")] = d.mean(), d.std() / np.sqrt(d.size())
    return pd.DataFrame(out)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz", help="relative to the processed data directory")
    parser.add_argument("--fits_dir", default="ddm/fits_guess", help="fits to rescore, relative to processed")
    parser.add_argument("--out_dir", default="ddm/mc_noise", help="relative to processed")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    out_dir = processed / args.out_dir
    if args.summarize:
        df = pd.concat([read_rows(p) for p in sorted(out_dir.glob("*.pkl"))], ignore_index=True)
        if "saved_test_nll" in df:
            check = df.dropna(subset=["saved_test_nll"])
            print(f"reproduced saved test_nll: {np.isclose(check.test_nll, check.saved_test_nll, rtol=0, atol=1e-3).sum()} / {len(check)}")
        table = compare_noise(df)
        print(table.round(2).to_string(index=False))
        table.to_csv(out_dir / "mc_noise_summary.csv", index=False)
        pm = per_mouse_delta(df)
        print(f"\nper mouse, {LEADING} vs each variant, mean of {df.seed.nunique()} seeds at 50 repetitions (positive = {LEADING} better):")
        print(pm.round(1).to_string())
        for v in pm.columns.levels[0]:
            m, se = pm[(v, "mean")], pm[(v, "se")]
            print(f"{v}: summed {m.sum():.1f}; mice with difference > 2 SE: {(m > 2 * se).sum()} for {LEADING}, {(m < -2 * se).sum()} against")
        pm.to_csv(out_dir / "mc_noise_per_mouse.csv")
    else:
        inputs = load_inputs(processed / args.inputs)
        grid = build_grid(inputs)
        if args.list:
            print(f"{len(grid)} jobs: {len(grid) // len(VARIANTS)} mice x {len(VARIANTS)} variants ({', '.join(VARIANTS)}); --array=0-{len(grid) - 1}")
        else:
            job = grid[args.job_id]
            if output_path(out_dir, job).exists() and not args.force:
                logger.info("skipping %s: output exists (use --force)", job)
            else:
                logger.info("job %s: %s", args.job_id, job)
                run_job(inputs, job, processed / args.fits_dir, out_dir)
