"""Model recovery for the mouse DDM: can each mechanism of the common model be detected when present and
rejected when absent, at each mouse's own trial count and stimuli?

Generating models: the common model (COMMON; set it to the model chosen in the comparison) and the models with one
of its mechanisms removed, each with the mouse's fitted parameters for that model (<fits_dir>/<mouse>_<variant>_all.pkl).
For each (mouse, generator, replicate):
  - simulate a training dataset and an independent test dataset from the generator, on the mouse's own trials
    (same stimuli, conditions, censoring at 5 s and the 0.3 s floor as the real fits),
  - each job fits one candidate (one of the same five models) to the training dataset and scores it on the test
    dataset (the held-out NLL used to compare models, without cross-validation refits), plus BIC on the training data.
A mechanism is recovered when, for data generated without it, the model without it scores better, and vice versa.
NLL at the generating parameters vs at the recovered ones checks the optimizer.

Usage:
    python -m scripts.ddm.model_recovery --list
    python -m scripts.ddm.model_recovery --job_id 17
On Slurm: sbatch --array=0-249 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery scripts/slurm/fit_mouse_ddm.slurm
"""

import argparse
import json
import logging
import pickle
import time
import zlib
from pathlib import Path

import numpy as np

from config import dir_config
from scripts.ddm.fit_mouse_ddm import CENSOR_AT, DE_TOL, DEVICE, LIKELIHOOD_PARAMS, MIN_RT, MouseDDM, heldout_nll, load_inputs, make_params, select

logger = logging.getLogger(__name__)

COMMON = "L1U1V1Z1G1"  # provisional: update once the comparison with fast guesses has picked the common model
MODELS = [COMMON] + [COMMON[:i + 1] + "0" + COMMON[i + 2:] for i in range(0, len(COMMON), 2) if COMMON[i + 1] == "1"]  # and each mechanism removed
N_REPLICATES = 2


def build_grid(inputs: dict) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"mouse": m, "generator": g, "candidate": c, "replicate": r} for r in range(N_REPLICATES) for g in MODELS for c in MODELS for m in mice]


def make_model(variant: str, rig: str) -> MouseDDM:
    free, fixed = make_params(variant)
    return MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])


def synthesize(model: MouseDDM, params: dict, stimulus: np.ndarray, condition: np.ndarray, seed: int) -> dict:
    """One simulated outcome per real trial, mapped like the recorded data (censoring, floor)."""
    sim = model._map_outcomes(model.simulate(stimulus, params, n_reps=1, seed=seed, labels=condition))
    if len(sim) != len(condition):
        raise RuntimeError("outcome mapping dropped trials; recovery assumes every simulated trial is kept")
    sim = sim.sort_values("trial")
    return {"rt": sim["rt"].to_numpy(float), "choice": sim["choice"].to_numpy(int), "condition": condition}


def output_path(out_dir: Path, job: dict) -> Path:
    return out_dir / f"{job['mouse']}_gen-{job['generator']}_fit-{job['candidate']}_rep{job['replicate']}.pkl"


def run_job(inputs: dict, job: dict, fits_dir: Path, out_dir: Path, n_reps: int, max_iterations: int) -> dict:
    rows = np.flatnonzero(inputs["subject_id"] == job["mouse"])
    rig = str(np.unique(inputs["data_source"][rows])[0])
    real, stimulus = select(inputs, rows)
    with open(fits_dir / f"{job['mouse']}_{job['generator']}_all.pkl", "rb") as f:
        true_params = pickle.load(f)["parameters"]

    seed = zlib.crc32(f"{job['mouse']}|{job['generator']}|{job['replicate']}".encode())
    generator = make_model(job["generator"], rig)
    train = synthesize(generator, true_params, stimulus, real["condition"], seed)
    test = synthesize(generator, true_params, stimulus, real["condition"], seed + 1)

    model = make_model(job["candidate"], rig)
    t0 = time.time()
    fit = model.fit(data=train, stimulus=stimulus, labels=train["condition"], n_reps=n_reps, max_iterations=max_iterations, l1_weight=0.0, verbose=True, **DE_TOL)
    k = len(model.fit_keys)
    truth_train_nll = None
    if job["candidate"] == job["generator"]:
        # objective at the generating parameters with the fit's own noise draws: recovered > truth means the optimizer
        # stopped short; recovered <= truth with different parameters means the parameters are not identifiable
        truth_train_nll = float(model._objective_function(np.array([true_params[p] for p in model.fit_keys]), train, stimulus, n_reps))
    result = {
        **job,
        "rig": rig,
        "n": len(rows),
        "k": k,
        "true_parameters": true_params,
        "parameters": {p: float(v) for p, v in fit["parameters"].items()},
        "free_parameters": list(model.fit_keys),
        "train_nll": float(fit["likelihood"]),
        "bic": 2 * float(fit["likelihood"]) + k * np.log(len(rows)),
        "test_nll": heldout_nll(model, fit["parameters"], test, stimulus, n_reps),
        "fit_seconds": time.time() - t0,
        "n_reps": n_reps,
        "max_iterations": max_iterations,
        "truth_train_nll": truth_train_nll,
    }
    if job["candidate"] == job["generator"]:
        result["truth_test_nll"] = heldout_nll(model, true_params, test, stimulus, n_reps)
    model.simulator.clear_cache()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = output_path(out_dir, job)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(result, f)
    tmp.replace(path)
    logger.info("saved %s: %s", path.name, json.dumps({k: result[k] for k in ("train_nll", "test_nll", "fit_seconds")}))
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz", help="relative to the processed data directory")
    parser.add_argument("--fits_dir", default="ddm/fits_guess", help="real-data fits with the generating parameters")
    parser.add_argument("--out_dir", default="ddm/recovery", help="relative to the processed data directory")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--n_reps", type=int, default=15)
    parser.add_argument("--max_iterations", type=int, default=1000)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--force", action="store_true", help="refit even if the output exists")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / args.inputs)
    grid = build_grid(inputs)
    if args.list:
        print(f"{len(grid)} jobs: {len(np.unique(inputs['subject_id']))} mice x {len(MODELS)} generators x {len(MODELS)} candidates x {N_REPLICATES} replicates")
        print("models:", MODELS)
    else:
        job = grid[args.job_id]
        if output_path(processed / args.out_dir, job).exists() and not args.force:
            logger.info("skipping %s: output exists (use --force to refit)", job)
        else:
            logger.info("job %s: %s", args.job_id, job)
            run_job(inputs, job, processed / args.fits_dir, processed / args.out_dir, args.n_reps, args.max_iterations)
