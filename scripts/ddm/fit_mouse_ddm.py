"""Fit DDM variants to each mouse's choices and RTs, driven by the trial's own motion energy.

Evidence input (scripts/ddm/build_ddm_inputs.py), per 1 ms step:
    drift = drift_gain * (S(t) + noise_weight * N(t)) + drift_offset
S is the motion energy expected from the programmed coherence (pulse included), N the stimulus noise;
noise_weight = 1 feeds raw motion energy. The likelihood is the Ratcliff quantile likelihood with a censored
outcome (src/ddm/likelihood_calculator_censored.py), summed over cells of coherence x scheduled pulse condition,
so pulse trials inform the fit.

Recorded outcomes, matched in simulation:
  no response by 5 s (RT > 5 s or none; stimulus kept running) -> censored outcome, fraction fit per cell
  responses before 0.3 s (minimum viewing time): UCLA registered the next lick at 0.3 s -> floored at 0.3 s;
      UW accepted them, but they are at chance and were excluded from the data -> truncated (dropped)

Model space: leak, urgency (time_constant), sv, sz each on/off, and noise_weight free or fixed at 1
(32 variants). Each job fits one (mouse, variant, split):
    split = "cv<k>"   train on all folds but k (stratified by condition), score held-out NLL on fold k
    split = "all"     fit all trials (parameters for reporting)
    split = "control" fit control trials only (for predicting pulse trials out of sample: primacy test)

Usage:
    python -m scripts.ddm.fit_mouse_ddm --list                  # print the job grid size
    python -m scripts.ddm.fit_mouse_ddm --job_id 17             # run one job of the grid (skipped if its output exists)
    python -m scripts.ddm.fit_mouse_ddm --mouse PSUIM5 --variant L0U1V0Z0K1 --split cv0 --max_iterations 5   # one fit, e.g. timing
"""

import argparse
import itertools
import json
import logging
import pickle
import time
from pathlib import Path

import numpy as np
import torch

from config import dir_config
from src.ddm.ddm import DecisionModel, FixedParam, FreeParam

logger = logging.getLogger(__name__)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CENSOR_AT = 5.0  # s; the replayed stimulus is 5 s long
MIN_RT = {"ucla": (0.3, "floor"), "uw": (0.3, "truncate")}
DT = 0.001
N_FOLDS = 5
LIKELIHOOD_PARAMS = {"method": "qmle_censored", "nbins": 9, "rt_nllh_weight": 1.0}
EVAL_SEED = 12345  # held-out scoring uses the same noise draws for every variant
DE_TOL = {"tol": 0.0, "atol": 1.0}  # stop when the population's NLL spread is within 1 unit (not 1% of the NLL)

FIXED_PARAMS = {"dt": FixedParam(DT), "variance": FixedParam(1.0)}
BASE_FREE_PARAMS = {
    "ndt": FreeParam(0.0, 0.8),  # the ~116 ms filter delay is already in the input, so ndt can be small
    "a": FreeParam(0.3, 9.5),  # validate_params requires a < 10
    "z": FreeParam(0.2, 0.8),
    "drift_gain": FreeParam(0.5, 20.0),
    "drift_offset": FreeParam(-2.0, 2.0),
}
OPTIONAL_FREE_PARAMS = {  # factor letter: (parameter, bounds when free, value when off)
    "L": ("leak_rate", (0.0, 5.0), 0.0),
    "U": ("time_constant", (-0.15, 2.0), 0.0),  # urgency factor 1 + t * time_constant must stay > 0 up to CENSOR_AT (>= 0.25 at 5 s)
    "V": ("sv", (0.0, 3.0), 0.0),
    "Z": ("sz", (0.0, 0.9), 0.0),
    "K": ("noise_weight", (0.0, 3.0), 1.0),
}
VARIANTS = ["".join(f"{f}{int(on)}" for f, on in zip(OPTIONAL_FREE_PARAMS, flags)) for flags in itertools.product([0, 1], repeat=len(OPTIONAL_FREE_PARAMS))]


def make_params(variant: str):
    free, fixed = dict(BASE_FREE_PARAMS), dict(FIXED_PARAMS)
    flags = dict(zip(variant[0::2], map(int, variant[1::2])))
    for factor, (name, bounds, off_value) in OPTIONAL_FREE_PARAMS.items():
        if flags[factor]:
            free[name] = FreeParam(*bounds)
        else:
            fixed[name] = FixedParam(off_value)
    return free, fixed


class MouseDDM(DecisionModel):
    def _objective_function(self, values, data, stimulus, n_reps, l1_weight=0.0):
        try:
            params = self._build_params(values)
        except ValueError:
            return 1e6
        result = self._simulate_condition(stimulus, params, n_reps)
        if result is None:
            return 1e6
        return self.likelihood_calc.compute_nll(
            result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"], result["signed_coherence"].to_numpy(), data["condition"]
        )


def load_inputs(path: Path) -> dict:
    with np.load(path) as f:
        return {k: f[k] for k in f.files}


def to_ms(frames: np.ndarray, frame_rate: int, dt: float = DT) -> np.ndarray:
    """Hold each frame's value for its duration on the 1 ms simulation grid."""
    n_steps = int(round(frames.shape[1] / frame_rate / dt))
    return np.ascontiguousarray(frames[:, (np.arange(n_steps) * dt * frame_rate).astype(int)])


def cv_folds(condition: np.ndarray, n_folds: int, seed: int = 0) -> np.ndarray:
    """Fold index per trial, stratified by condition."""
    rng = np.random.default_rng(seed)
    folds = np.empty(len(condition), dtype=int)
    for c in np.unique(condition):
        idx = rng.permutation(np.flatnonzero(condition == c))
        folds[idx] = np.arange(len(idx)) % n_folds
    return folds


def select(inputs: dict, rows: np.ndarray) -> tuple[dict, tuple]:
    frame_rate = int(inputs["frame_rate"])
    data = {"rt": inputs["rt"][rows], "choice": inputs["choice"][rows], "condition": inputs["condition"][rows]}
    stimulus = (to_ms(inputs["signal"][rows], frame_rate), to_ms(inputs["noise"][rows], frame_rate))
    return data, stimulus


def heldout_nll(model: MouseDDM, params: dict, data: dict, stimulus: tuple, n_reps: int) -> float:
    np.random.seed(EVAL_SEED)
    model.simulator.clear_cache()
    model._labels = data["condition"]
    model._precomputed = model.simulator.precompute_noise(*stimulus[0].shape, n_reps=n_reps)
    result = model._simulate_condition(stimulus, params, n_reps)
    if result is None:
        return float("inf")
    return float(model.likelihood_calc.compute_nll(result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"], result["signed_coherence"].to_numpy(), data["condition"]))


def build_grid(inputs: dict) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    splits = [f"cv{k}" for k in range(N_FOLDS)] + ["all", "control"]
    return [{"mouse": m, "variant": v, "split": s} for s in splits for v in VARIANTS for m in mice]


def output_path(out_dir: Path, job: dict) -> Path:
    return out_dir / f"{job['mouse']}_{job['variant']}_{job['split']}.pkl"


def run_job(inputs: dict, job: dict, out_dir: Path, n_reps: int, max_iterations: int) -> dict:
    mouse_rows = np.flatnonzero(inputs["subject_id"] == job["mouse"])
    is_control = inputs["sched_pulse_type"][mouse_rows] == 0
    split = job["split"]
    if split.startswith("cv"):
        folds = cv_folds(inputs["condition"][mouse_rows], N_FOLDS)
        train, test = mouse_rows[folds != int(split[2:])], mouse_rows[folds == int(split[2:])]
    elif split == "all":
        train, test = mouse_rows, None
    elif split == "control":
        train, test = mouse_rows[is_control], mouse_rows[~is_control]
    else:
        raise ValueError(f"unknown split {split}")

    free, fixed = make_params(job["variant"])
    rigs = np.unique(inputs["data_source"][mouse_rows])
    assert len(rigs) == 1, f"{job['mouse']} has trials from {rigs}"
    min_rt = MIN_RT[rigs[0]]
    model = MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=min_rt)
    data, stimulus = select(inputs, train)
    t0 = time.time()
    fit = model.fit(data=data, stimulus=stimulus, labels=data["condition"], n_reps=n_reps, max_iterations=max_iterations, l1_weight=0.0, verbose=True, **DE_TOL)
    result = {
        **job,
        "n_train": len(train),
        "train_nll": float(fit["likelihood"]),
        "parameters": {k: float(v) for k, v in fit["parameters"].items()},
        "free_parameters": list(free),
        "success": fit["success"],
        "n_iterations": fit["n_iterations"],
        "fit_seconds": time.time() - t0,
        "n_reps": n_reps,
        "max_iterations": max_iterations,
        "de_tol": DE_TOL,
        "likelihood_params": LIKELIHOOD_PARAMS,
        "censor_at": CENSOR_AT,
        "min_rt": min_rt,
        "n_train_censored": int(inputs["censored"][train].sum()),
    }
    if test is not None and len(test):
        test_data, test_stimulus = select(inputs, test)
        result["n_test"] = len(test)
        result["test_nll"] = heldout_nll(model, fit["parameters"], test_data, test_stimulus, n_reps)
    model.simulator.clear_cache()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = output_path(out_dir, job)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(result, f)
    tmp.replace(path)  # atomic: a preempted job never leaves a partial result that a rerun would skip
    logger.info("saved %s: %s", path.name, json.dumps({k: result[k] for k in ("train_nll", "test_nll", "fit_seconds") if k in result}))
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz", help="relative to the processed data directory")
    parser.add_argument("--out_dir", default="ddm/fits", help="relative to the processed data directory")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--mouse")
    parser.add_argument("--variant")
    parser.add_argument("--split")
    parser.add_argument("--n_reps", type=int, default=15)
    parser.add_argument("--max_iterations", type=int, default=1000)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--force", action="store_true", help="refit even if the output exists")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / args.inputs)
    grid = build_grid(inputs)
    if args.list:
        print(f"{len(grid)} jobs: {len(np.unique(inputs['subject_id']))} mice x {len(VARIANTS)} variants x {N_FOLDS + 2} splits")
        per_split = len(grid) // (N_FOLDS + 2)
        for i, split in enumerate([f"cv{k}" for k in range(N_FOLDS)] + ["all", "control"]):
            print(f"  job_id {i * per_split}-{(i + 1) * per_split - 1}: split {split}")
    else:
        job = grid[args.job_id] if args.job_id is not None else {"mouse": args.mouse, "variant": args.variant, "split": args.split}
        if output_path(processed / args.out_dir, job).exists() and not args.force:
            logger.info("skipping %s: output exists (use --force to refit)", job)
        else:
            logger.info("job %s: %s", args.job_id, job)
            run_job(inputs, job, processed / args.out_dir, args.n_reps, args.max_iterations)
