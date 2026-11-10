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
    split = "pulse"   fit pulse trials only, score control trials out of sample (plan 2026-11-10-pulse-only-fits)
    split = "pcv<k>"  5-fold CV within pulse trials (stratified by condition)

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
# Responses at 0.3-5 s only (V. Thakur, 2026-10-27: trials without a response by 5 s are not analysed); the likelihood
# is then conditional on a response by 5 s.
RESPONDED_LIKELIHOOD_PARAMS = {**LIKELIHOOD_PARAMS, "include_censored": False}
# The conditional likelihood does not constrain how often a model responds; small mice drifted to ~98% simulated
# non-responses. Responded-only training rejects parameter sets above this share (primacy plan, amendment 11).
MAX_NO_RESPONSE = 0.5


def too_few_responses(likelihood_calc, choice: np.ndarray) -> bool:
    """Amendment 11: in responded-only fits, more than MAX_NO_RESPONSE of simulated trials without a response by 5 s."""
    return not getattr(likelihood_calc, "include_censored", True) and float(np.mean(choice < 0)) > MAX_NO_RESPONSE
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
# Visual front ends (primacy plan, amendment 7): applied to the drift input before accumulation (simulator.front_end_*).
FRONT_ENDS = {
    "power": [("fe_gamma", (0.3, 3.0), 1.0)],  # x' = sign(x)|x|^gamma
    "norm": [("fe_beta", (0.0, 20.0), 0.0), ("fe_tau", (0.02, 1.0), 0.1)],  # x' = x / (1 + beta * lowpass_tau(|x|))
}
# Signed leak (plan step 6.5): leak_rate < 0 is a self-exciting accumulator, which amplifies early evidence (primacy).
# Lower bound -1/s limits the growth to e^5 ~ 148x over the 5 s stimulus.
SIGNED_LEAK_BOUNDS = (-1.0, 5.0)
# Leak range of the extrema-detection model (primacy plan, amendment 4): time constant 5-50 ms, so the decision variable
# tracks recent motion energy and a bound crossing is a threshold crossing by momentary evidence.
EXTREMA_LEAK_BOUNDS = (20.0, 200.0)
# Discrete-sample extrema detection (Stine et al. 2020; primacy plan, amendment 10): each 1 ms evidence sample is compared
# with +-b per-step noise SDs and nothing is accumulated; a and z are unused, drift_gain may reach 200.
EXTREMA_SAMPLE_BOUND = ("extrema_bound", (2.0, 5.0))
EXTREMA_SAMPLE_GAIN_MAX = 200.0
# Paper-exact models of Stine et al. 2020 (primacy plan, amendment 13): nominal signed coherence as input, no sv, guesses,
# leak or urgency; the integrator starts midway (z = 0.5). Their kappa * (C - C0) is drift_gain * C + drift_offset, with
# drift_offset bounds wide enough for |C0| <= NOMINAL_C0_MAX at any gain (C0 = -drift_offset / drift_gain).
NOMINAL_VARIANT = "L0U0V0Z0G0"
# Free pulse weight (plan 2026-10-29-pulse-weight-joint): drift input = no-pulse motion energy + w x pulse component on
# pulse trials (controls have no pulse component); w = 1 is the model as built. The simulator calls the second channel's
# weight noise_weight.
PULSE_WEIGHT = ("noise_weight", (0.0, 20.0), 1.0)
# Per-pulse-time weights (plan 2026-10-30-pulse-time-weights): one weight per pulse time, |sched_pulse_type| = 1, 2, 3
# (UCLA 1-2, UW 1-3; early ~0.05-0.1 s, middle ~0.2-0.3 s, late 0.42 s). Channel k of the simulator stimulus.
PULSE_TIME_WEIGHTS = [("noise_weight", (0.0, 20.0), 1.0), ("noise_weight_2", (0.0, 20.0), 1.0), ("noise_weight_3", (0.0, 20.0), 1.0)]
NOMINAL_C0_MAX = 0.3
# Amendment 13 addendum: in nominal units the integration model's drift_gain sat at 0.5 (the motion-energy bound) in
# 31/60 fits, so its lower bound is 0.01 (the extrema model, gains 3.7-13.1, keeps 0.5).
NOMINAL_DDM_GAIN_MIN = 0.01
# Model sets for the downstream scripts (--model_set). "sv": the common model chosen 2026-10-22 with all trials;
# "nosv": re-selected under the responded-only rule with parsimony rules 2-3 (primacy plan, amendment 12).
MODEL_SETS = {
    "sv": {"primary": "L0U0V1Z0G1", "secondary": "L1U1V1Z0G1", "extrema": "L1U0V1Z0G1", "fixed_guess_bias": False},
    "nosv": {"primary": "L0U0V0Z0G1", "secondary": "L1U1V0Z0G1", "extrema": "L1U0V0Z0G1", "fixed_guess_bias": True},
}
VARIANTS = ["".join(f"{f}{int(on)}" for f, on in zip(OPTIONAL_FREE_PARAMS, flags)) for flags in itertools.product([0, 1], repeat=len(OPTIONAL_FREE_PARAMS))]


def make_params(variant: str, guess_model: str = "single", time_varying_gain: bool = False, signed_leak: bool = False, fixed_guess_bias: bool = False, leak_bounds: tuple[float, float] | None = None, drift_gain_max: float | None = None,
                front_end: str | None = None, extrema_samples: bool = False, nominal_input: bool = False, pulse_weight: bool = False, nominal_matched: bool = False,
                n_pulse_times: int = 0):
    """n_pulse_times > 0: a free weight per pulse time (PULSE_TIME_WEIGHTS) instead of pulse_weight's shared one.
    nominal_matched (control paper D003): nominal coherence input with any variant (sv, guesses, z as in the motion-energy
    model), so the motion-energy models can be compared with their own nominal-input versions."""
    free, fixed = dict(BASE_FREE_PARAMS), dict(FIXED_PARAMS)
    if nominal_input and not nominal_matched and (variant != NOMINAL_VARIANT or front_end or time_varying_gain):
        raise ValueError(f"nominal_input (amendment 13) is the paper-exact model: variant {NOMINAL_VARIANT}, no front end or gain decay")
    if extrema_samples:
        if variant[1] != "0" or variant[3] != "0":
            raise ValueError("extrema_samples takes no leak or urgency")
        del free["a"], free["z"]
        fixed.update(a=FixedParam(1.0), z=FixedParam(0.5))  # unused by the sample rule
        free[EXTREMA_SAMPLE_BOUND[0]] = FreeParam(*EXTREMA_SAMPLE_BOUND[1])
        drift_gain_max = EXTREMA_SAMPLE_GAIN_MAX if drift_gain_max is None else drift_gain_max
    if front_end is not None:
        for name, bounds, _ in FRONT_ENDS[front_end]:
            free[name] = FreeParam(*bounds)
    if drift_gain_max is not None:  # wider gain for the extrema-detection model (primacy plan, amendment 5)
        free["drift_gain"] = FreeParam(BASE_FREE_PARAMS["drift_gain"].lower_bound, drift_gain_max)
    if time_varying_gain:
        free[GAIN_DECAY[0]] = FreeParam(*GAIN_DECAY[1])
    if pulse_weight:
        if nominal_input:
            raise ValueError("pulse_weight is defined on the motion-energy input")
        free[PULSE_WEIGHT[0]] = FreeParam(*PULSE_WEIGHT[1])
    if n_pulse_times:
        if nominal_input or pulse_weight:
            raise ValueError("per-pulse-time weights are on the motion-energy input and replace pulse_weight")
        for name, bounds, _ in PULSE_TIME_WEIGHTS[:n_pulse_times]:
            free[name] = FreeParam(*bounds)
    flags = dict(zip(variant[0::2], map(int, variant[1::2])))
    if flags.get("G") and guess_model == "guess_lapse":
        fixed.update(LAPSE_WINDOW)
    for factor, specs in OPTIONAL_FREE_PARAMS.items():
        if factor == "G":
            specs = GUESS_MODELS[guess_model]
        for name, bounds, off_value in specs:
            if name == "leak_rate" and signed_leak:
                bounds = SIGNED_LEAK_BOUNDS
            if name == "leak_rate" and leak_bounds is not None:
                bounds = tuple(leak_bounds)
            if flags[factor] and not (name == "guess_bias" and fixed_guess_bias):
                free[name] = FreeParam(*bounds)
            else:
                fixed[name] = FixedParam(off_value)
    if nominal_input:
        if not extrema_samples:
            free["drift_gain"] = FreeParam(NOMINAL_DDM_GAIN_MIN, free["drift_gain"].upper_bound)
        c0_offset = NOMINAL_C0_MAX * free["drift_gain"].upper_bound
        free["drift_offset"] = FreeParam(-c0_offset, c0_offset)
        if "z" in free and not nominal_matched:
            del free["z"]
            fixed["z"] = FixedParam(0.5)
    return free, fixed


class MouseDDM(DecisionModel):
    def _objective_function(self, values, data, stimulus, n_reps, l1_weight=0.0):
        try:
            params = self._build_params(values)
        except ValueError:
            return 1e6
        result = self._simulate_condition(stimulus, params, n_reps)
        if result is None or too_few_responses(self.likelihood_calc, result["choice"].to_numpy()):
            return 1e6
        return self.likelihood_calc.compute_nll(
            result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"], result["signed_coherence"].to_numpy(), data["condition"]
        )


def load_inputs(path: Path) -> dict:
    with np.load(path) as f:
        return {k: f[k] for k in f.files}


def responded_only(inputs: dict) -> dict:
    """Drop trials without a response by 5 s (choice -1) from every per-trial array."""
    keep = inputs["choice"] >= 0
    return {k: (v[keep] if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == len(keep) else v) for k, v in inputs.items()}


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


def select(inputs: dict, rows: np.ndarray, nominal: bool = False, pulse_weight: bool = False, pulse_times: int = 0) -> tuple[dict, np.ndarray | tuple]:
    """Data and the 1 ms motion-energy input (S + N) of the given trials; with `nominal` (amendment 13), the trial's
    nominal signed coherence held from stimulus onset, plus the scheduled pulse coherence over the logged pulse frames on
    pulse trials (needs the pulse timing arrays)."""
    frame_rate = int(inputs["frame_rate"])
    data = {"rt": inputs["rt"][rows], "choice": inputs["choice"][rows], "condition": inputs["condition"][rows]}
    if nominal:
        n_steps = int(round(inputs["signal"].shape[1] / frame_rate / DT))
        stimulus = np.repeat(inputs["signed_coherence"][rows, None].astype(np.float32), n_steps, axis=1)
        pulsed = np.flatnonzero(inputs["sched_pulse_type"][rows] != 0)
        if len(pulsed):  # joint fits (plan 2026-10-29-joint-control-pulse-refits): scheduled pulse coherence over the
            if "pulse_onset_frame0" not in inputs:  # logged pulse frames, no lead (as primacy.nominal_stimuli, lead 0)
                raise ValueError("nominal input with pulse trials needs --pulse_timing (scripts/ddm/build_pulse_timing.py)")
            for i in pulsed:
                r = rows[i]
                start = int(round(inputs["pulse_onset_frame0"][r] / frame_rate / DT))
                stop = int(round((inputs["pulse_onset_frame0"][r] + inputs["pulse_n_frames"][r]) / frame_rate / DT))
                stimulus[i, start:stop] = inputs["pulse_coherence"][r]
        return data, stimulus
    if pulse_weight or pulse_times:  # (no-pulse input, pulse component) for PULSE_WEIGHT; as primacy.gain_stimuli
        rig = np.unique(inputs["data_source"][rows]).item()
        without = inputs["signed_coherence"][rows, None] * inputs[f"onset_response_{rig}"][None, : inputs["signal"].shape[1]] + inputs["noise"][rows]
        pulse = (inputs["signal"][rows] + inputs["noise"][rows]) - without
        if pulse_times:  # one pulse channel per pulse time 1..pulse_times (PULSE_TIME_WEIGHTS), zero on other trials
            when = np.abs(inputs["sched_pulse_type"][rows])
            channels = [np.where((when == k)[:, None], pulse, 0.0) for k in range(1, pulse_times + 1)]
            return data, (to_ms(without.astype(np.float32), frame_rate), *(to_ms(c.astype(np.float32), frame_rate) for c in channels))
        return data, (to_ms(without.astype(np.float32), frame_rate), to_ms(pulse.astype(np.float32), frame_rate))
    stimulus = to_ms(inputs["signal"][rows] + inputs["noise"][rows], frame_rate)
    return data, stimulus


def heldout_nll(model: MouseDDM, params: dict, data: dict, stimulus: np.ndarray, n_reps: int, seed: int = EVAL_SEED) -> float:
    np.random.seed(seed)
    model.simulator.clear_cache()
    model._labels = data["condition"]
    model.precompute(*model._stimulus_shape(stimulus), n_reps=n_reps)
    result = model._simulate_condition(stimulus, params, n_reps)
    if result is None:
        return float("inf")
    return float(model.likelihood_calc.compute_nll(result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"], result["signed_coherence"].to_numpy(), data["condition"]))


ALL_SPLITS = [f"cv{k}" for k in range(N_FOLDS)] + ["all", "control"]
# Cross-validation within control trials only (plan step 3.3: does the model choice depend on pulse trials?).
# Not in ALL_SPLITS, so the default grid and its job ids are unchanged; request with --splits ccv0 ... ccv4.
CONTROL_CV_SPLITS = [f"ccv{k}" for k in range(N_FOLDS)]
# Pulse-only fits (plan 2026-11-10-pulse-only-fits), also outside ALL_SPLITS: --splits pcv0 ... pcv4 pulse.
PULSE_SPLITS = [f"pcv{k}" for k in range(N_FOLDS)] + ["pulse"]


def n_pulse_times(inputs: dict, rows: np.ndarray) -> int:
    return int(np.abs(inputs["sched_pulse_type"][rows]).max())


def build_grid(inputs: dict, variants: list[str] | None = None, splits: list[str] | None = None) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"mouse": m, "variant": v, "split": s} for s in (splits or ALL_SPLITS) for v in (variants or VARIANTS) for m in mice]


def default_value(name: str) -> float:
    """Value of an optional parameter when its mechanism is off (used to complete warm-start seeds)."""
    for specs in [*OPTIONAL_FREE_PARAMS.values(), *GUESS_MODELS.values(), [GAIN_DECAY], [PULSE_WEIGHT], PULSE_TIME_WEIGHTS, *FRONT_ENDS.values()]:
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
                # a shared pulse weight seeds every per-pulse-time weight, so that fit is reproduced exactly
                seeds.append(np.array([r["parameters"][k] if k in r["parameters"] else r["parameters"]["noise_weight"] if k.startswith("noise_weight_") and "noise_weight" in r["parameters"]
                                       else default_value(k) for k in fit_keys], dtype=float))
                used.append({"dir": str(d), "variant": v, "train_nll": float(r["train_nll"])})
    return seeds, used


def output_path(out_dir: Path, job: dict) -> Path:
    return out_dir / f"{job['mouse']}_{job['variant']}_{job['split']}.pkl"


def checkpoint_path(out_dir: Path, job: dict) -> Path:
    return output_path(out_dir, job).with_suffix(".ckpt")


def run_job(inputs: dict, job: dict, out_dir: Path, n_reps: int, max_iterations: int, guess_model: str = "single", warm_dirs: list[Path] | None = None, time_varying_gain: bool = False, signed_leak: bool = False, fixed_guess_bias: bool = False, leak_bounds: tuple[float, float] | None = None, drift_gain_max: float | None = None,
            front_end: str | None = None, likelihood_params: dict = LIKELIHOOD_PARAMS, extrema_samples: bool = False, nominal_input: bool = False, pulse_weight: bool = False,
            nominal_matched: bool = False, pulse_time_weights: bool = False) -> dict:
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
    elif split.startswith("ccv"):
        control_rows = mouse_rows[is_control]
        folds = cv_folds(inputs["condition"][control_rows], N_FOLDS)
        train, test = control_rows[folds != int(split[3:])], control_rows[folds == int(split[3:])]
    elif split == "pulse":
        train, test = mouse_rows[~is_control], mouse_rows[is_control]
    elif split.startswith("pcv"):
        pulse_rows = mouse_rows[~is_control]
        folds = cv_folds(inputs["condition"][pulse_rows], N_FOLDS)
        train, test = pulse_rows[folds != int(split[3:])], pulse_rows[folds == int(split[3:])]
    else:
        raise ValueError(f"unknown split {split}")
    if nominal_input and split == "control":
        test = None  # pulse trials need the pulse in nominal units (amendment 13, item 4), not built here

    n_times = n_pulse_times(inputs, mouse_rows) if pulse_time_weights else 0
    free, fixed = make_params(job["variant"], guess_model, time_varying_gain, signed_leak, fixed_guess_bias, leak_bounds, drift_gain_max, front_end, extrema_samples, nominal_input, pulse_weight, nominal_matched, n_times)
    rigs = np.unique(inputs["data_source"][mouse_rows])
    assert len(rigs) == 1, f"{job['mouse']} has trials from {rigs}"
    min_rt = MIN_RT[rigs[0]]
    model = MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=likelihood_params, censor_at=CENSOR_AT, min_rt=min_rt)
    data, stimulus = select(inputs, train, nominal_input, pulse_weight, n_times)
    t0 = time.time()
    seeds, seeds_used = warm_start_seeds(job, list(free), warm_dirs or [])
    if seeds_used:
        logger.info("warm start from %d fits: %s", len(seeds_used), seeds_used)
    ckpt = checkpoint_path(out_dir, job)  # resumes a preempted / requeued / timed-out attempt of this fit
    fit = model.fit(data=data, stimulus=stimulus, labels=data["condition"], n_reps=n_reps, max_iterations=max_iterations, l1_weight=0.0, verbose=True, seeds=seeds,
                    checkpoint=ckpt, **DE_TOL)
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
        "likelihood_params": likelihood_params,
        "guess_model": guess_model,
        "time_varying_gain": time_varying_gain,
        "signed_leak": signed_leak,
        "fixed_guess_bias": fixed_guess_bias,
        "leak_bounds": list(leak_bounds) if leak_bounds is not None else None,
        "drift_gain_max": drift_gain_max,
        "front_end": front_end,
        "extrema_samples": extrema_samples,
        "nominal_input": nominal_input,
        "nominal_matched": nominal_matched,
        "pulse_weight": pulse_weight,
        "n_pulse_times": n_times,
        "warm_start_seeds": seeds_used,
        "resumed_from_generation": fit["resumed_from_generation"],  # None = not resumed; -1 = DE done, refinement redone
        "censor_at": CENSOR_AT,
        "min_rt": min_rt,
        "n_train_censored": int(inputs["censored"][train].sum()),
    }
    if test is not None and len(test):
        test_data, test_stimulus = select(inputs, test, nominal_input, pulse_weight, n_times)
        result["n_test"] = len(test)
        result["test_nll"] = heldout_nll(model, fit["parameters"], test_data, test_stimulus, n_reps)
    model.simulator.clear_cache()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = output_path(out_dir, job)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(result, f)
    tmp.replace(path)  # atomic: a preempted job never leaves a partial result that a rerun would skip
    ckpt.unlink(missing_ok=True)
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
    parser.add_argument("--splits", nargs="*", help="restrict the grid to these splits (default: cv0-cv4, all, control; also ccv0-ccv4, CV within control trials; pcv0-pcv4 and pulse, pulse trials only)")
    parser.add_argument("--job_file", help="text file of grid job ids (one per line, in the full or restricted grid); --job_id then indexes this list")
    parser.add_argument("--guess_model", default="single", choices=list(GUESS_MODELS), help="form of the guess factor G (plan step 2)")
    parser.add_argument("--warm_start_from", nargs="*", default=[], help="fit folders (relative to processed) whose fits of this variant and its nested variants seed the optimizer")
    parser.add_argument("--time_varying_gain", action="store_true", help="add a free gain_decay: evidence weight drift_gain * exp(-gain_decay * t) (plan step 6.5)")
    parser.add_argument("--signed_leak", action="store_true", help="allow leak_rate down to -1/s (self-exciting accumulator) in variants with leak (plan step 6.5)")
    parser.add_argument("--fixed_guess_bias", action="store_true", help="fix guess_bias at 0.5 (guesses at chance; parsimony rule 3)")
    parser.add_argument("--leak_bounds", type=float, nargs=2, metavar=("LO", "HI"), help="leak_rate bounds (/s) in variants with leak, e.g. 20 200 for the extrema-detection model (primacy plan, amendment 4)")
    parser.add_argument("--front_end", choices=list(FRONT_ENDS), help="visual front end on the drift input (primacy plan, amendment 7): power or norm")
    parser.add_argument("--responded_only", action="store_true", help="drop trials without a response by 5 s; likelihood conditional on a response")
    parser.add_argument("--extrema_samples", action="store_true", help="discrete-sample extrema detection (amendment 10); use with a variant without leak or urgency")
    parser.add_argument("--drift_gain_max", type=float, help="upper bound of drift_gain (default 20); amendment 5: 200 for the extrema-detection model if its fits reach 20")
    parser.add_argument("--pulse_timing", default="ddm/pulse_timing_global.npz", help="scheduled pulse timing (build_pulse_timing.py); read only with --nominal_input, for pulse trials")
    parser.add_argument("--nominal_matched", action="store_true", help="with --nominal_input: any variant (control paper D003: C, E, ES on nominal coherence with their own components)")
    parser.add_argument("--pulse_weight", action="store_true", help="free weight on the pulse component of pulse trials (noise_weight; plan 2026-10-29-pulse-weight-joint)")
    parser.add_argument("--pulse_time_weights", action="store_true", help="a free pulse weight per pulse time (PULSE_TIME_WEIGHTS; plan 2026-10-30-pulse-time-weights)")
    parser.add_argument("--nominal_input", action="store_true", help=f"paper-exact Stine et al. 2020 models (amendment 13): nominal coherence input, variant {NOMINAL_VARIANT}; with --extrema_samples their extrema detector")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    args.out_dir = args.out_dir or (("ddm/fits_guess" if args.guess_model == "single" else f"ddm/fits_guess_{args.guess_model}") + ("_W" if args.time_varying_gain else "") + ("_NL" if args.signed_leak else "") + ("_FB" if args.fixed_guess_bias else "") + (f"_leak{args.leak_bounds[0]:g}-{args.leak_bounds[1]:g}" if args.leak_bounds else "") + (f"_gain{args.drift_gain_max:g}" if args.drift_gain_max else "") + (f"_fe-{args.front_end}" if args.front_end else "") + ("_nominal" if args.nominal_input else ""))
    inputs = load_inputs(processed / args.inputs)
    if args.nominal_input and (processed / args.pulse_timing).exists():
        with np.load(processed / args.pulse_timing) as f:
            if not np.array_equal(f["agg_code"], inputs["agg_code"]):
                raise ValueError(f"{args.pulse_timing} is not aligned with {args.inputs}")
            inputs = {**inputs, **{k: f[k] for k in ("pulse_onset_frame0", "pulse_n_frames", "pulse_coherence")}}
    if args.responded_only:
        inputs = responded_only(inputs)
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
            run_job(inputs, job, processed / args.out_dir, args.n_reps, args.max_iterations, args.guess_model, [processed / d for d in args.warm_start_from], args.time_varying_gain, args.signed_leak, args.fixed_guess_bias, args.leak_bounds, args.drift_gain_max, args.front_end,
                    RESPONDED_LIKELIHOOD_PARAMS if args.responded_only else LIKELIHOOD_PARAMS, args.extrema_samples, args.nominal_input, args.pulse_weight,
                    args.nominal_matched, args.pulse_time_weights)
