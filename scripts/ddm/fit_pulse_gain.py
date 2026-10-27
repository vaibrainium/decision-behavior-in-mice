"""Cross-validated pulse gain for the revised baselines (primacy plan, amendment 6; plan file
.agents/plans/2026-10-23-amendment-6-pulse-gain.md).

The revised model scales the pulse component of each pulse trial's input by a per-mouse gain w_p in [0, 50]:
input = coherence x onset response + w_p x (pulse change x pulse response) + N; w_p = 1 is the original model. All other
parameters stay at the mouse's control-only fit. w_p is the same at every timing; it can still change the predicted
timing pattern (a stronger pulse changes which decisions are still open later), which the timing test then uses.

Per job (baseline, mouse):
  - 5 folds of the mouse's pulse trials, stratified by condition (coherence x scheduled pulse type);
  - for each fold, w_p fitted to the other 4 folds with the censored QMLE likelihood (choices, RTs, censoring), common
    random numbers at --fit_reps repetitions: a coarse grid, then golden-section refinement around its minimum;
  - out-of-fold predictions for the held-out trials (primacy.predict_mouse with the fold's w_p, --n_reps), so every
    trial's prediction uses a gain estimated without it;
  - w_p fitted to all pulse trials with its NLL profile on the grid (approximate 95% interval: NLL within 1.92 of the
    minimum; QMLE, so indicative only).
Output: <out_dir>/<baseline>/<mouse>.pkl in the primacy.py prediction format (trials, reps, commit), plus the fold
gains, profiles and the all-trial gain; `primacy.py --analyze --gate_only --out_dir <out_dir>` runs the revised gate.
No observed pulse outcome is used except the training folds' outcomes in the gain fits (that is the fit).

Usage:
    python -m scripts.ddm.fit_pulse_gain --list
    python -m scripts.ddm.fit_pulse_gain --job_id 3 --fits_dir ddm/fits_final
On Slurm: sbatch --array=0-19 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_pulse_gain,EXTRA_ARGS="--fits_dir ddm/fits_final" scripts/slurm/fit_mouse_ddm.slurm
"""

import argparse
import logging
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import N_FOLDS, cv_folds, load_inputs, responded_only, too_few_responses

logger = logging.getLogger(__name__)

GAIN_BOUNDS = (0.0, 50.0)
GRID = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 14.0, 20.0, 28.0, 38.0, 50.0]
N_REFINE = 10  # golden-section steps after the grid
FIT_REPS = 50
PROFILE_DELTA = 1.92  # chi-square(1) 95% / 2


def gain_nll_function(model, params: dict, inputs: dict, rows: np.ndarray, n_reps: int, seed: int, observed: dict | None = None):
    """NLL(w) on the given pulse trials, with common random numbers (one precompute for every w). `observed` maps
    row -> (rt, choice) arrays aligned with `rows` (synthetic data for the calibration); default: recorded outcomes."""
    without, pulse = primacy.gain_stimuli(inputs, rows)
    rt, choice = (inputs["rt"][rows], inputs["choice"][rows]) if observed is None else (observed["rt"], observed["choice"])
    data = {"rt": rt, "choice": choice, "condition": inputs["condition"][rows]}
    np.random.seed(seed)
    model.simulator.clear_cache()
    model._labels = data["condition"]
    model.precompute(*without.shape, n_reps=n_reps)

    def nll(w: float) -> float:
        result = model._simulate_condition((without, pulse), {**params, "noise_weight": float(w)}, n_reps)
        if result is None or too_few_responses(model.likelihood_calc, result["choice"].to_numpy()):
            return float("inf")
        return float(model.likelihood_calc.compute_nll(result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"],
                                                       result["signed_coherence"].to_numpy(), data["condition"]))
    return nll


def fit_gain(nll) -> tuple[float, dict]:
    """Grid, then golden-section search on the bracket around the grid minimum. Returns w and the evaluated profile."""
    profile = {w: nll(w) for w in GRID}
    i = int(np.argmin([profile[w] for w in GRID]))
    lo, hi = GRID[max(i - 1, 0)], GRID[min(i + 1, len(GRID) - 1)]
    g = (np.sqrt(5) - 1) / 2
    a, b = hi - g * (hi - lo), lo + g * (hi - lo)
    fa, fb = nll(a), nll(b)
    profile.update({a: fa, b: fb})
    for _ in range(N_REFINE):
        if fa < fb:
            hi, b, fb = b, a, fa
            a = hi - g * (hi - lo)
            fa = nll(a)
            profile[a] = fa
        else:
            lo, a, fa = a, b, fb
            b = lo + g * (hi - lo)
            fb = nll(b)
            profile[b] = fb
    best = min(profile, key=profile.get)
    return float(best), dict(sorted(profile.items()))


def profile_interval(profile: dict) -> tuple[float, float]:
    best = min(profile.values())
    inside = [w for w, v in profile.items() if v <= best + PROFILE_DELTA]
    return float(min(inside)), float(max(inside))


def run_job(inputs: dict, baseline: str, mouse: str, fits_dir: Path, fit_reps: int, n_reps: int, seed: int,
            params: dict | None = None, observed: dict | None = None, rows: np.ndarray | None = None, responded: bool = False) -> dict:
    """`params` overrides the control-only fit and `observed` (rt, choice arrays over the mouse's pulse trials, in
    pulse_rows order, or over `rows`) replaces the recorded outcomes; all three are used by the calibration.
    `responded`: likelihood conditional on a response by 5 s (amendment 9); the data must contain responses only."""
    variant = primacy.BASELINES[baseline]
    if params is None:
        params = primacy.load_fit(fits_dir, mouse, variant, "control", False, responded=responded)["parameters"]
    rows = primacy.pulse_rows(inputs, mouse) if rows is None else rows
    obs_of = (lambda sel: None) if observed is None else (lambda sel: {k: v[sel] for k, v in observed.items()})  # noqa: E731
    rig = np.unique(inputs["data_source"][rows]).item()
    folds = cv_folds(inputs["condition"][rows], N_FOLDS)
    model = primacy.make_model(variant, rig, responded=responded)

    fold_gain, fold_profile, parts, sims = {}, {}, [], []
    for k in range(N_FOLDS):
        train, test = rows[folds != k], rows[folds == k]
        w, prof = fit_gain(gain_nll_function(model, params, inputs, train, fit_reps, seed + k, obs_of(folds != k)))
        model.simulator.clear_cache()
        fold_gain[k], fold_profile[k] = w, prof
        pred = primacy.predict_mouse(inputs, mouse, params, variant, n_reps, seed + 100 + k, rows=test, pulse_gain=w, keep_sim=True)
        parts.append(pred["trials"].assign(fold=k, pulse_gain=w))
        sims.append(pred["sim"])
        logger.info("%s %s fold %d: w_p = %.3f", baseline, mouse, k, w)
    w_all, prof_all = fit_gain(gain_nll_function(model, params, inputs, rows, fit_reps, seed + 50, obs_of(np.ones(len(rows), bool))))
    model.simulator.clear_cache()

    trials = pd.concat(parts).set_index("row").loc[rows].reset_index()  # back to the original trial order
    sim = pd.concat(sims)
    assert len(trials) == len(rows) and trials.row.is_unique, "each pulse trial must be predicted exactly once"
    return {"mouse": mouse, "rig": rig, "variant": variant, "baseline": baseline, "params": params, "n_reps": n_reps, "seed": seed,
            "trials": trials, "reps": primacy.per_rep_summary(sim), "fold_gain": fold_gain, "fold_profile": fold_profile,
            "pulse_gain_all": w_all, "profile_all": prof_all, "pulse_gain_interval": profile_interval(prof_all),
            "fit_reps": fit_reps, "fit_path": str(fits_dir), "commit": primacy.git_commit(), "responded_only": responded}


def build_grid(inputs: dict) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"baseline": b, "mouse": m} for b in primacy.BASELINES for m in mice]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz")
    parser.add_argument("--fits_dir", default="ddm/fits_final", help="control-only fits (plan step 5), relative to processed")
    parser.add_argument("--out_dir", default="ddm/primacy_revised", help="relative to processed")
    parser.add_argument("--fit_reps", type=int, default=FIT_REPS)
    parser.add_argument("--n_reps", type=int, default=primacy.N_REPS)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--responded_only", action="store_true", help="amendment 9: responded trials only, conditional likelihood")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / args.inputs)
    if args.responded_only:
        inputs = responded_only(inputs)
    grid = build_grid(inputs)
    if args.list:
        print(f"{len(grid)} jobs: {len(primacy.BASELINES)} baselines x {len(grid) // len(primacy.BASELINES)} mice; --array=0-{len(grid) - 1}")
    else:
        job = grid[args.job_id]
        out = processed / args.out_dir / job["baseline"] / f"{job['mouse']}.pkl"
        if out.exists():
            logger.info("skipping %s: output exists", job)
        else:
            t0 = time.time()
            res = run_job(inputs, job["baseline"], job["mouse"], processed / args.fits_dir, args.fit_reps, args.n_reps, args.seed, responded=args.responded_only)
            res["seconds"] = time.time() - t0
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_suffix(".tmp")
            with open(tmp, "wb") as f:
                pickle.dump(res, f)
            tmp.replace(out)
            logger.info("saved %s: w_p (all) %.3f, interval %s, folds %s (%.0f s)", out, res["pulse_gain_all"], res["pulse_gain_interval"], res["fold_gain"], res["seconds"])
