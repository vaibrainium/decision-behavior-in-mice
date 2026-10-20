"""Fit DDM variants to each mouse's choices and RTs, driven by the trial's own motion energy.

Evidence input, per 1 ms step: drift = drift_gain * ME(t) + drift_offset, where ME is the trial's own motion energy
(scripts/ddm/build_ddm_inputs.py stores it as S + N: S expected from the programmed coherence with any pulse, N the
stimulus noise). An earlier grid weighted N separately (drift_gain * (S + k * N)); a free k improved no mouse's
held-out fit, so the model uses the motion energy as is.
Fast guesses (factor G): with probability p_guess the response is a guess, right with probability guess_bias, at
0.3 s + an exponential delay with mean guess_tau. Responses < 0.6 s are 17-20% of all responses and near chance at
every coherence, which the DDM alone cannot produce (it misses the fast errors at high coherence). The likelihood is the Ratcliff quantile likelihood with a censored
outcome (src/ddm/likelihood_calculator_censored.py), summed over cells of coherence x scheduled pulse condition,
so pulse trials inform the fit.

Recorded outcomes, matched in simulation:
  no response by 5 s (RT > 5 s or none; stimulus kept running) -> censored outcome, fraction fit per cell
  decisions before 0.3 s (minimum viewing time): neither rig could register a response before 0.3 s; the next lick
      after it counts (UCLA RTs pile up at 0.3 s; UW raw response times start when the response window opens and
      preprocessing adds 0.3 s) -> floored at 0.3 s on both rigs. Nothing before 0.3 s was dropped from the data.

Model space: leak, urgency (time_constant), sv, sz and fast guesses each on/off (32 variants, e.g. L1U1V1Z1G1). Each job fits one (mouse, variant, split):
    split = "cv<k>"   train on all folds but k (stratified by condition), score held-out NLL on fold k
    split = "all"     fit all trials (parameters for reporting)
    split = "control" fit control trials only (for predicting pulse trials out of sample: primacy test)

Usage:
    python -m scripts.ddm.fit_mouse_ddm --list                  # print the job grid size
    python -m scripts.ddm.fit_mouse_ddm --job_id 17             # run one job of the grid (skipped if its output exists)
    python -m scripts.ddm.fit_mouse_ddm --mouse PSUIM5 --variant L1U1V1Z1G1 --split cv0 --max_iterations 5   # one fit, e.g. timing
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
MIN_RT = {"ucla": (0.3, "floor"), "uw": (0.3, "floor")}  # never "truncate": the data contain these responses (at 0.3 s+)
DT = 0.001
N_FOLDS = 5
LIKELIHOOD_PARAMS = {"method": "qmle_censored", "nbins": 9, "rt_nllh_weight": 1.0}
EVAL_SEED = 12345  # held-out scoring uses the same noise draws for every variant
DE_TOL = {"tol": 0.0, "atol": 1.0}  # stop when the population's NLL spread is within 1 unit (not 1% of the NLL)

MIN_VIEWING = 0.3  # s; guesses start when the response window opens
FIXED_PARAMS = {"dt": FixedParam(DT), "variance": FixedParam(1.0), "guess_t0": FixedParam(MIN_VIEWING)}
BASE_FREE_PARAMS = {
    "ndt": FreeParam(0.0, 0.8),  # the ~116 ms filter delay is already in the input, so ndt can be small
    "a": FreeParam(0.3, 9.5),  # validate_params requires a < 10
    "z": FreeParam(0.2, 0.8),
    "drift_gain": FreeParam(0.5, 20.0),
    "drift_offset": FreeParam(-2.0, 2.0),
}
OPTIONAL_FREE_PARAMS = {  # factor letter: [(parameter, bounds when free, value when off), ...]
    "L": [("leak_rate", (0.0, 5.0), 0.0)],
    "U": [("time_constant", (-0.15, 2.0), 0.0)],  # urgency factor 1 + t * time_constant must stay > 0 up to CENSOR_AT (>= 0.25 at 5 s)
    "V": [("sv", (0.0, 3.0), 0.0)],
    "Z": [("sz", (0.0, 0.9), 0.0)],
    "G": [("p_guess", (0.0, 0.6), 0.0), ("guess_bias", (0.0, 1.0), 0.5), ("guess_tau", (0.01, 2.0), 1.0)],
}
# Alternative forms of the contaminant factor G (plan step 2); "single" is the grid's default above.
GUESS_MODELS = {
    "single": OPTIONAL_FREE_PARAMS["G"],  # one component, exponential delay up to 2 s (fast guesses and slow lapses)
    "fast_only": [("p_guess", (0.0, 0.6), 0.0), ("guess_bias", (0.0, 1.0), 0.5), ("guess_tau", (0.01, 0.3), 0.1)],
    "guess_lapse": [("p_guess", (0.0, 0.6), 0.0), ("guess_bias", (0.0, 1.0), 0.5), ("guess_tau", (0.01, 0.3), 0.1), ("p_lapse", (0.0, 0.6), 0.0)],
}
LAPSE_WINDOW = {"lapse_t0": FixedParam(0.3), "lapse_t1": FixedParam(5.0)}  # lapse RTs uniform over the response window
# Time-varying evidence weight (plan step 6.5): drift_gain * exp(-gain_decay * t); > 0 primacy, < 0 recency, 0 = constant.
GAIN_DECAY = ("gain_decay", (-0.5, 3.0), 0.0)
VARIANTS = ["".join(f"{f}{int(on)}" for f, on in zip(OPTIONAL_FREE_PARAMS, flags)) for flags in itertools.product([0, 1], repeat=len(OPTIONAL_FREE_PARAMS))]


def make_params(variant: str, guess_model: str = "single", time_varying_gain: bool = False):
    free, fixed = dict(BASE_FREE_PARAMS), dict(FIXED_PARAMS)
    if time_varying_gain:
        free[GAIN_DECAY[0]] = FreeParam(*GAIN_DECAY[1])
    flags = dict(zip(variant[0::2], map(int, variant[1::2])))
    if flags.get("G") and guess_model == "guess_lapse":
        fixed.update(LAPSE_WINDOW)
    for factor, specs in OPTIONAL_FREE_PARAMS.items():
        if factor == "G":
            specs = GUESS_MODELS[guess_model]
        for name, bounds, off_value in specs:
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


def select(inputs: dict, rows: np.ndarray) -> tuple[dict, np.ndarray]:
    """Data and the 1 ms motion-energy input (S + N) of the given trials."""
    frame_rate = int(inputs["frame_rate"])
    data = {"rt": inputs["rt"][rows], "choice": inputs["choice"][rows], "condition": inputs["condition"][rows]}
    stimulus = to_ms(inputs["signal"][rows] + inputs["noise"][rows], frame_rate)
    return data, stimulus


def heldout_nll(model: MouseDDM, params: dict, data: dict, stimulus: np.ndarray, n_reps: int) -> float:
    np.random.seed(EVAL_SEED)
    model.simulator.clear_cache()
    model._labels = data["condition"]
    model.precompute(*stimulus.shape, n_reps=n_reps)
    result = model._simulate_condition(stimulus, params, n_reps)
    if result is None:
        return float("inf")
    return float(model.likelihood_calc.compute_nll(result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"], result["signed_coherence"].to_numpy(), data["condition"]))


ALL_SPLITS = [f"cv{k}" for k in range(N_FOLDS)] + ["all", "control"]


def build_grid(inputs: dict, variants: list[str] | None = None, splits: list[str] | None = None) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"mouse": m, "variant": v, "split": s} for s in (splits or ALL_SPLITS) for v in (variants or VARIANTS) for m in mice]


def default_value(name: str) -> float:
    """Value of an optional parameter when its mechanism is off (used to complete warm-start seeds)."""
    for specs in [*OPTIONAL_FREE_PARAMS.values(), *GUESS_MODELS.values(), [GAIN_DECAY]]:
        for spec_name, _, off_value in specs:
            if spec_name == name:
                return off_value
    raise KeyError(name)


def warm_start_seeds(job: dict, fit_keys: list[str], dirs: list[Path]) -> tuple[list[np.ndarray], list[dict]]:
    """Seeds from earlier fits of the same mouse and split: this variant and every nested variant (one mechanism
    switched off), from each directory. Parameters a seed's model did not have take their "off" value, so each seed
    reproduces that model's fit exactly (same noise draws)."""
    variant = job["variant"]
    candidates = [variant] + [variant[: i + 1] + "0" + variant[i + 2:] for i in range(0, len(variant), 2) if variant[i + 1] == "1"]
    seeds, used = [], []
    for d in dirs:
        for v in candidates:
            path = d / f"{job['mouse']}_{v}_{job['split']}.pkl"
            if path.exists():
                with open(path, "rb") as f:
                    r = pickle.load(f)
                seeds.append(np.array([r["parameters"][k] if k in r["parameters"] else default_value(k) for k in fit_keys], dtype=float))
                used.append({"dir": str(d), "variant": v, "train_nll": float(r["train_nll"])})
    return seeds, used


def output_path(out_dir: Path, job: dict) -> Path:
    return out_dir / f"{job['mouse']}_{job['variant']}_{job['split']}.pkl"


def run_job(inputs: dict, job: dict, out_dir: Path, n_reps: int, max_iterations: int, guess_model: str = "single", warm_dirs: list[Path] | None = None, time_varying_gain: bool = False) -> dict:
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

    free, fixed = make_params(job["variant"], guess_model, time_varying_gain)
    rigs = np.unique(inputs["data_source"][mouse_rows])
    assert len(rigs) == 1, f"{job['mouse']} has trials from {rigs}"
    min_rt = MIN_RT[rigs[0]]
    model = MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=min_rt)
    data, stimulus = select(inputs, train)
    t0 = time.time()
    seeds, seeds_used = warm_start_seeds(job, list(free), warm_dirs or [])
    if seeds_used:
        logger.info("warm start from %d fits: %s", len(seeds_used), seeds_used)
    fit = model.fit(data=data, stimulus=stimulus, labels=data["condition"], n_reps=n_reps, max_iterations=max_iterations, l1_weight=0.0, verbose=True, seeds=seeds, **DE_TOL)
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
        "guess_model": guess_model,
        "time_varying_gain": time_varying_gain,
        "warm_start_seeds": seeds_used,
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
    parser.add_argument("--out_dir", help="relative to the processed data directory (default: ddm/fits_guess, or ddm/fits_guess_<guess_model> for the other guess forms)")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--mouse")
    parser.add_argument("--variant")
    parser.add_argument("--split")
    parser.add_argument("--n_reps", type=int, default=15)
    parser.add_argument("--max_iterations", type=int, default=1000)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--force", action="store_true", help="refit even if the output exists")
    parser.add_argument("--variants", nargs="*", help="restrict the grid to these variants")
    parser.add_argument("--splits", nargs="*", help="restrict the grid to these splits")
    parser.add_argument("--job_file", help="text file of grid job ids (one per line, in the full or restricted grid); --job_id then indexes this list")
    parser.add_argument("--guess_model", default="single", choices=list(GUESS_MODELS), help="form of the guess factor G (plan step 2)")
    parser.add_argument("--warm_start_from", nargs="*", default=[], help="fit folders (relative to processed) whose fits of this variant and its nested variants seed the optimizer")
    parser.add_argument("--time_varying_gain", action="store_true", help="add a free gain_decay: evidence weight drift_gain * exp(-gain_decay * t) (plan step 6.5)")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    args.out_dir = args.out_dir or (("ddm/fits_guess" if args.guess_model == "single" else f"ddm/fits_guess_{args.guess_model}") + ("_W" if args.time_varying_gain else ""))
    inputs = load_inputs(processed / args.inputs)
    grid = build_grid(inputs, args.variants, args.splits)
    job_ids = [int(x) for x in Path(args.job_file).read_text().split()] if args.job_file else None
    if args.list:
        splits, variants = args.splits or ALL_SPLITS, args.variants or VARIANTS
        print(f"{len(grid)} jobs: {len(np.unique(inputs['subject_id']))} mice x {len(variants)} variants x {len(splits)} splits")
        per_split = len(grid) // len(splits)
        for i, split in enumerate(splits):
            print(f"  job_id {i * per_split}-{(i + 1) * per_split - 1}: split {split}")
        if job_ids:
            print(f"--job_file lists {len(job_ids)} of these: --array=0-{len(job_ids) - 1}")
    else:
        if args.job_id is not None:
            job = grid[job_ids[args.job_id]] if job_ids else grid[args.job_id]
        else:
            job = {"mouse": args.mouse, "variant": args.variant, "split": args.split}
        if output_path(processed / args.out_dir, job).exists() and not args.force:
            logger.info("skipping %s: output exists (use --force to refit)", job)
        else:
            logger.info("job %s: %s", args.job_id, job)
            run_job(inputs, job, processed / args.out_dir, args.n_reps, args.max_iterations, args.guess_model, [processed / d for d in args.warm_start_from], args.time_varying_gain)
