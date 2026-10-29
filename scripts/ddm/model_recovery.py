"""Model recovery for the mouse DDM: can each mechanism of the common model be detected when present and
rejected when absent, at each mouse's own trial count and stimuli?

Generating models: the common model (COMMON, chosen in plan step 3), the models with one of its mechanisms removed, and
the models with leak or urgency added (to check that the comparison would have detected them where present), each with
the mouse's fitted parameters for that model (<mouse>_<variant>_all.pkl, first found in --fits_dir). All use the
GUESS_MODEL form of the guess factor.
For each (mouse, generator, replicate):
  - simulate a training dataset and an independent test dataset from the generator, on the mouse's own trials
    (same stimuli, conditions, censoring at 5 s and the 0.3 s floor as the real fits),
  - each job fits one candidate (one of the same five models) to the training dataset and scores it on the test
    dataset (the held-out NLL used to compare models, without cross-validation refits), plus BIC on the training data.
A mechanism is recovered when, for data generated without it, the model without it scores better, and vice versa.
NLL at the generating parameters vs at the recovered ones checks the optimizer.

--strategy (accumulation-first paper, spine challenge F1a): generators and candidates are the common model and the
rapid-forgetting model (L1U0V1Z0G1, leak 20-200/s); control trials only; generating parameters from the control-trial
fits (<mouse>_<variant>_control.pkl), the common model from the first --fits_dir and E from the second. Asks whether the
control-trial comparison scores E-generated data as E.
--strategy --exact (amendment 13, item 5): the paper-exact Stine et al. 2020 models instead, integration (DDMx, first
--fits_dir) and extrema detection (ESx, second), on nominal coherence input.
--strategy --cross (amendment 14): the cross-family cells of the full recovery matrix over C, E, DDMx and ESx (each of
C/E fitted to DDMx/ESx data and vice versa; 4 --fits_dir: C, E, DDMx, ESx). Generator labels and seeds are those of the
pairwise runs, so the same synthetic datasets fill the within-family cells (F1a and --exact outputs).
--make_datasets DIR / --datasets DIR (control-trial paper, plan 2026-10-29-control-paper.md step 3): GPU synthesis gave
different draws for the same seed on different GPU models, so candidates fitted to "one" dataset saw different trials
(reports/2026-10-28-recovery-synthetic-data-mismatch.md). --make_datasets synthesizes every (mouse, generator, replicate)
train/test pair once on the CPU and writes it with a sha256 manifest; --datasets makes each job load its pair from there
(checked against the manifest) instead of synthesizing. --full gives the whole 4 x 4 grid over C, E, DDMx and ESx.

Usage:
    python -m scripts.ddm.model_recovery --list
    python -m scripts.ddm.model_recovery --job_id 17
On Slurm (500 jobs): sbatch --array=0-249 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery scripts/slurm/fit_mouse_ddm.slurm, then JOB_OFFSET=250
"""

import argparse
import hashlib
import json
import logging
import pickle
import time
import zlib
from pathlib import Path

import numpy as np

from config import dir_config
from scripts.ddm.fit_mouse_ddm import (CENSOR_AT, DE_TOL, DEVICE, EXTREMA_LEAK_BOUNDS, LIKELIHOOD_PARAMS, MIN_RT, MODEL_SETS, RESPONDED_LIKELIHOOD_PARAMS, MouseDDM, heldout_nll,
                                       NOMINAL_VARIANT, load_inputs, make_params, responded_only, select)

logger = logging.getLogger(__name__)

COMMON = "L0U0V1Z0G1"  # chosen 2026-10-22 (strict parsimony rule 2; analysis log 5.6): sv + fast guesses
GUESS_MODEL = "fast_only"
ADDED = ["L", "U"]  # mechanisms dropped from the common model whose detectability is checked
MODELS = ([COMMON] + [COMMON[:i + 1] + "0" + COMMON[i + 2:] for i in range(0, len(COMMON), 2) if COMMON[i + 1] == "1"]  # each mechanism removed
          + [COMMON.replace(f"{f}0", f"{f}1") for f in ADDED])  # leak or urgency added
EXTREMA = "L1U0V1Z0G1"  # with leak 20-200/s (primacy plan, amendment 4)
EXTREMA_SAMPLES = "ES"  # discrete-sample extrema detection (amendment 10): the common model's components, sample rule
STRATEGY_MODELS = [COMMON, EXTREMA]
EXACT_MODELS = ["DDMx", "ESx"]  # paper-exact Stine et al. 2020 models (amendment 13), variant NOMINAL_VARIANT, nominal input
N_REPLICATES = 2


def use_model_set(name: str) -> None:
    """Strategy mode only (amendment 12): the common model and E of the chosen set; the default 5-model grid keeps COMMON."""
    global COMMON, EXTREMA, STRATEGY_MODELS
    COMMON, EXTREMA = MODEL_SETS[name]["primary"], MODEL_SETS[name]["extrema"]
    STRATEGY_MODELS = [COMMON, EXTREMA]


def strategy_models(extrema_samples: bool = False, exact: bool = False) -> list[str]:
    return EXACT_MODELS if exact else [COMMON, EXTREMA_SAMPLES] if extrema_samples else STRATEGY_MODELS


def build_grid(inputs: dict, strategy: bool = False, extrema_samples: bool = False, exact: bool = False, cross: bool = False, full: bool = False) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    if full:
        models = STRATEGY_MODELS + EXACT_MODELS
        return [{"mouse": m, "generator": g, "candidate": c, "replicate": r} for r in range(N_REPLICATES) for g in models for c in models for m in mice]
    if cross:
        fams = [STRATEGY_MODELS, EXACT_MODELS]
        return [{"mouse": m, "generator": g, "candidate": c, "replicate": r} for r in range(N_REPLICATES) for i, f in enumerate(fams) for g in f for c in fams[1 - i] for m in mice]
    models = strategy_models(extrema_samples, exact) if strategy else MODELS
    return [{"mouse": m, "generator": g, "candidate": c, "replicate": r} for r in range(N_REPLICATES) for g in models for c in models for m in mice]


def make_model(variant: str, rig: str, fixed_guess_bias: bool = False, strategy: bool = False, responded: bool = False) -> MouseDDM:
    leak_bounds = EXTREMA_LEAK_BOUNDS if strategy and variant == EXTREMA else None
    samples = variant in (EXTREMA_SAMPLES, "ESx")
    if variant in EXACT_MODELS:
        free, fixed = make_params(NOMINAL_VARIANT, extrema_samples=samples, nominal_input=True)
    else:
        free, fixed = make_params(COMMON if samples else variant, GUESS_MODEL, fixed_guess_bias=fixed_guess_bias, leak_bounds=leak_bounds, extrema_samples=samples)
    likelihood_params = RESPONDED_LIKELIHOOD_PARAMS if responded else LIKELIHOOD_PARAMS
    return MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=likelihood_params, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])


def synthesize(model: MouseDDM, params: dict, stimulus: np.ndarray, condition: np.ndarray, seed: int) -> dict:
    """One simulated outcome per real trial, mapped like the recorded data (censoring, floor)."""
    sim = model._map_outcomes(model.simulate(stimulus, params, n_reps=1, seed=seed, labels=condition))
    if len(sim) != len(condition):
        raise RuntimeError("outcome mapping dropped trials; recovery assumes every simulated trial is kept")
    sim = sim.sort_values("trial")
    return {"rt": sim["rt"].to_numpy(float), "choice": sim["choice"].to_numpy(int), "condition": condition}


def output_path(out_dir: Path, job: dict) -> Path:
    return out_dir / f"{job['mouse']}_gen-{job['generator']}_fit-{job['candidate']}_rep{job['replicate']}.pkl"


def generating_params(fits_dirs: list[Path], mouse: str, variant: str, fixed_guess_bias: bool) -> dict:
    """Parameters of the first all-trial fit of this variant whose guess form matches (any form when guesses are off),
    so a missing fast-only fit never falls back silently to a single-form fit."""
    for d in fits_dirs:
        if (path := d / f"{mouse}_{variant}_all.pkl").exists():
            with open(path, "rb") as f:
                r = pickle.load(f)
            if variant.endswith("G0") or (r.get("guess_model", "single"), r.get("fixed_guess_bias", False)) == (GUESS_MODEL, fixed_guess_bias):
                logger.info("generating parameters from %s", path)
                return r["parameters"]
    raise FileNotFoundError(f"no all-trial fit of {mouse} {variant} ({GUESS_MODEL}, fixed_guess_bias={fixed_guess_bias}) in {[str(d) for d in fits_dirs]}")


def strategy_params(fits_dirs: list[Path], mouse: str, variant: str, fixed_guess_bias: bool = False) -> dict:
    """Control-trial fit of the common model (first folder) or of E / ES (second folder); E's leak must lie in 20-200/s.
    Exact models: DDMx from the first folder, ESx from the second."""
    exact = variant in EXACT_MODELS
    stem = NOMINAL_VARIANT if exact else COMMON if variant == EXTREMA_SAMPLES else variant
    folder = {COMMON: 0, EXTREMA: 1, "DDMx": 2, "ESx": 3}[variant] if len(fits_dirs) == 4 else 0 if variant in (COMMON, "DDMx") else 1
    path = fits_dirs[folder] / f"{mouse}_{stem}_control.pkl"
    with open(path, "rb") as f:
        r = pickle.load(f)
    if bool(r.get("extrema_samples", False)) != (variant in (EXTREMA_SAMPLES, "ESx")):
        raise ValueError(f"{path}: extrema_samples={r.get('extrema_samples')} does not match {variant}")
    if bool(r.get("nominal_input", False)) != exact:
        raise ValueError(f"{path}: nominal_input={r.get('nominal_input')} does not match {variant}")
    if not exact and (r.get("guess_model", "single"), r.get("fixed_guess_bias", False)) != (GUESS_MODEL, fixed_guess_bias):
        raise ValueError(f"{path}: guess form does not match")
    if variant == EXTREMA and not EXTREMA_LEAK_BOUNDS[0] <= r["parameters"]["leak_rate"] <= EXTREMA_LEAK_BOUNDS[1]:
        raise ValueError(f"{path}: leak_rate outside the extrema-detection bounds")
    logger.info("generating parameters from %s", path)
    return r["parameters"]


def responded(data: dict, stimulus: np.ndarray) -> tuple[dict, np.ndarray]:
    """Drop simulated trials without a response by 5 s, as the real data are with --responded_only."""
    keep = data["choice"] >= 0
    return {k: v[keep] for k, v in data.items()}, stimulus[keep]


def dataset_path(datasets_dir: Path, mouse: str, generator: str, replicate: int) -> Path:
    return datasets_dir / f"{mouse}_gen-{generator}_rep{replicate}.npz"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(inputs: dict, mouse: str, generator_variant: str, replicate: int, fits_dirs: list[Path], fixed_guess_bias: bool, strategy: bool,
             responded_data: bool) -> tuple[dict, dict]:
    """The unmasked train and test datasets of one (mouse, generator, replicate), synthesized as run_job always did."""
    rows = np.flatnonzero(inputs["subject_id"] == mouse)
    if strategy:
        rows = rows[inputs["sched_pulse_type"][rows] == 0]
    rig = str(np.unique(inputs["data_source"][rows])[0])
    real, stimulus = select(inputs, rows, nominal=generator_variant in EXACT_MODELS)
    true_params = strategy_params(fits_dirs, mouse, generator_variant, fixed_guess_bias) if strategy else generating_params(fits_dirs, mouse, generator_variant, fixed_guess_bias)
    seed = zlib.crc32(f"{mouse}|{generator_variant}|{replicate}".encode())
    generator = make_model(generator_variant, rig, fixed_guess_bias, strategy, responded_data)
    train = synthesize(generator, true_params, stimulus, real["condition"], seed)
    test = synthesize(generator, true_params, stimulus, real["condition"], seed + 1)
    generator.simulator.clear_cache()
    return train, test


def make_datasets(inputs: dict, grid: list[dict], fits_dirs: list[Path], datasets_dir: Path, fixed_guess_bias: bool, strategy: bool, responded_data: bool) -> None:
    """Write every (mouse, generator, replicate) pair of the grid once, plus manifest.json with sha256 and device."""
    if DEVICE.type != "cpu":
        raise RuntimeError("--make_datasets must run on the CPU (GPU draws depend on the GPU model)")
    datasets_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = datasets_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for mouse, gen, rep in sorted({(j["mouse"], j["generator"], j["replicate"]) for j in grid}):
        path = dataset_path(datasets_dir, mouse, gen, rep)
        if path.name in manifest and path.exists():
            continue
        train, test = generate(inputs, mouse, gen, rep, fits_dirs, fixed_guess_bias, strategy, responded_data)
        np.savez(path, **{f"train_{k}": v for k, v in train.items()}, **{f"test_{k}": v for k, v in test.items()})
        manifest[path.name] = {"sha256": sha256(path), "device": DEVICE.type, "n": len(train["choice"]),
                               "n_train_responded": int((train["choice"] >= 0).sum()), "n_test_responded": int((test["choice"] >= 0).sum())}
        manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))
        logger.info("wrote %s %s", path.name, manifest[path.name])


def load_dataset(datasets_dir: Path, mouse: str, generator_variant: str, replicate: int, condition: np.ndarray) -> tuple[dict, dict]:
    path = dataset_path(datasets_dir, mouse, generator_variant, replicate)
    expected = json.loads((datasets_dir / "manifest.json").read_text())[path.name]["sha256"]
    if sha256(path) != expected:
        raise ValueError(f"{path}: sha256 does not match the manifest")
    with np.load(path) as f:
        train, test = ({k: f[f"{part}_{k}"] for k in ("rt", "choice", "condition")} for part in ("train", "test"))
    if not (np.array_equal(train["condition"], condition) and np.array_equal(test["condition"], condition)):
        raise ValueError(f"{path}: trials do not match the inputs")
    logger.info("synthetic data from %s (sha256 %s)", path, expected[:12])
    return train, test


def run_job(inputs: dict, job: dict, fits_dirs: list[Path], out_dir: Path, n_reps: int, max_iterations: int, fixed_guess_bias: bool = False, strategy: bool = False,
            responded_data: bool = False, datasets_dir: Path | None = None) -> dict:
    rows = np.flatnonzero(inputs["subject_id"] == job["mouse"])
    if strategy:
        rows = rows[inputs["sched_pulse_type"][rows] == 0]
    rig = str(np.unique(inputs["data_source"][rows])[0])
    real, stimulus = select(inputs, rows, nominal=job["generator"] in EXACT_MODELS)
    # each model sees its own input of the same trials: motion energy (C, E) or nominal coherence (DDMx, ESx)
    fit_input = stimulus if (job["candidate"] in EXACT_MODELS) == (job["generator"] in EXACT_MODELS) else select(inputs, rows, nominal=job["candidate"] in EXACT_MODELS)[1]
    true_params = strategy_params(fits_dirs, job["mouse"], job["generator"], fixed_guess_bias) if strategy else generating_params(fits_dirs, job["mouse"], job["generator"], fixed_guess_bias)

    if datasets_dir is not None:
        train, test = load_dataset(datasets_dir, job["mouse"], job["generator"], job["replicate"], real["condition"])
    else:
        train, test = generate(inputs, job["mouse"], job["generator"], job["replicate"], fits_dirs, fixed_guess_bias, strategy, responded_data)
    train_stimulus, test_stimulus = fit_input, fit_input
    if responded_data:
        train, train_stimulus = responded(train, fit_input)
        test, test_stimulus = responded(test, fit_input)

    model = make_model(job["candidate"], rig, fixed_guess_bias, strategy, responded_data)
    t0 = time.time()
    fit = model.fit(data=train, stimulus=train_stimulus, labels=train["condition"], n_reps=n_reps, max_iterations=max_iterations, l1_weight=0.0, verbose=True, **DE_TOL)
    k = len(model.fit_keys)
    truth_train_nll = None
    if job["candidate"] == job["generator"]:
        # objective at the generating parameters with the fit's own noise draws: recovered > truth means the optimizer
        # stopped short; recovered <= truth with different parameters means the parameters are not identifiable
        truth_train_nll = float(model._objective_function(np.array([true_params[p] for p in model.fit_keys]), train, train_stimulus, n_reps))
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
        "test_nll": heldout_nll(model, fit["parameters"], test, test_stimulus, n_reps),
        "fit_seconds": time.time() - t0,
        "n_reps": n_reps,
        "max_iterations": max_iterations,
        "truth_train_nll": truth_train_nll,
        "guess_model": GUESS_MODEL,
        "fixed_guess_bias": fixed_guess_bias,
        "strategy": strategy,
        "responded_only": responded_data,
        "n_train": len(train["choice"]),
        "n_test": len(test["choice"]),
        "datasets_dir": None if datasets_dir is None else str(datasets_dir),
    }
    if job["candidate"] == job["generator"]:
        result["truth_test_nll"] = heldout_nll(model, true_params, test, test_stimulus, n_reps)
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
    parser.add_argument("--fits_dir", nargs="+", default=["ddm/fits_guess_fast_only", "ddm/fits_guess"], help="real-data fits with the generating parameters, searched in order (relative to processed)")
    parser.add_argument("--fixed_guess_bias", action="store_true", help="guess_bias fixed at 0.5 (use with the _FB fits)")
    parser.add_argument("--out_dir", default="ddm/recovery", help="relative to the processed data directory")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--n_reps", type=int, default=15)
    parser.add_argument("--max_iterations", type=int, default=1000)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--force", action="store_true", help="refit even if the output exists")
    parser.add_argument("--responded_only", action="store_true", help="real and simulated trials without a response by 5 s dropped; conditional likelihood")
    parser.add_argument("--model_set", choices=list(MODEL_SETS), default="sv", help="with --strategy: sv (default) or nosv (amendment 12; implies --fixed_guess_bias)")
    parser.add_argument("--extrema_samples", action="store_true", help="with --strategy: discrete-sample extrema detection (ES) instead of E; second --fits_dir holds its fits")
    parser.add_argument("--strategy", action="store_true", help="common model vs E on control trials (fits_dir: common-model folder, then E folder)")
    parser.add_argument("--cross", action="store_true", help="with --strategy: cross-family cells of the C/E/DDMx/ESx matrix (amendment 14); fits_dir: C, E, DDMx, ESx folders")
    parser.add_argument("--exact", action="store_true", help="with --strategy: paper-exact DDMx vs ESx (amendment 13); fits_dir: DDMx folder, then ESx folder")
    parser.add_argument("--full", action="store_true", help="with --strategy: the whole 4 x 4 grid over C, E, DDMx, ESx (4 --fits_dir: C, E, DDMx, ESx)")
    parser.add_argument("--make_datasets", action="store_true", help="write the grid's synthetic datasets on the CPU into --datasets, then stop")
    parser.add_argument("--datasets", help="folder of pre-generated synthetic datasets (relative to processed); jobs load instead of synthesizing")
    args = parser.parse_args()

    if args.strategy:
        use_model_set(args.model_set)
        args.fixed_guess_bias = args.fixed_guess_bias or MODEL_SETS[args.model_set]["fixed_guess_bias"]
    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / args.inputs)
    if args.responded_only:
        inputs = responded_only(inputs)
    grid = build_grid(inputs, args.strategy, args.extrema_samples, args.exact, args.cross, args.full)
    datasets_dir = processed / args.datasets if args.datasets else None
    models = STRATEGY_MODELS + EXACT_MODELS if args.cross or args.full else strategy_models(args.extrema_samples, args.exact) if args.strategy else MODELS
    if args.make_datasets:
        make_datasets(inputs, grid, [processed / d for d in args.fits_dir], datasets_dir, args.fixed_guess_bias, args.strategy, args.responded_only)
    elif args.list:
        print(f"{len(grid)} jobs: {len(np.unique(inputs['subject_id']))} mice x {len(models)} generators x {len(models)} candidates x {N_REPLICATES} replicates")
        print("models:", models)
    else:
        job = grid[args.job_id]
        if output_path(processed / args.out_dir, job).exists() and not args.force:
            logger.info("skipping %s: output exists (use --force to refit)", job)
        else:
            logger.info("job %s: %s", args.job_id, job)
            run_job(inputs, job, [processed / d for d in args.fits_dir], processed / args.out_dir, args.n_reps, args.max_iterations, args.fixed_guess_bias, args.strategy, args.responded_only,
                    datasets_dir)
