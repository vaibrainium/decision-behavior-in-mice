"""Primacy test (next-steps step 6; locked plan dissemination/reports/primacy-analysis-plan.md with amendments 1-3).

Pieces, in the plan's order:
  predict    per mouse, simulate every scheduled-pulse trial from a control-only fit, with its own motion energy and
             with the pulse removed (the trial's onset response + its noise): p_hat (P(choice in the pulse direction)
             among simulated responses), predicted mean RT and P(censored), plus per-repetition RT quantiles and
             censored fractions for the predictive check. Hyak job per (baseline, mouse); no observed data involved.
  gate       section 7: pooled departure beta0 vs the predicted pulse effect; pulse-trial RT quantiles and censored
             fraction within the spread of the simulated datasets.
  glmm       section 6: logit P(y = 1) = logit(p_hat) + b0 + b_timing + b_rig * rig + u_mouse + v_mouse * timing
             (PyMC; Normal(0, 1) fixed effects, HalfNormal(1) random-effect SDs). Primary: b_middle, early and middle
             pulses of all mice. Secondary: UW mice, early/middle/late and a linear trend. Rig interaction reported
             descriptively.
  rt         secondary outcome: observed minus predicted mean RT per mouse and timing.

Blinding: `analyze` compares predictions with the recorded pulse-trial choices only when --unblind is given. Use it
only once the final fits (plan step 5) exist and the gate rules are fixed. Synthetic data (primacy_sensitivity.py)
go through the same functions without that flag.

Usage:
    python -m scripts.ddm.primacy --list
    python -m scripts.ddm.primacy --predict --job_id 3 --fits_dir ddm/fits_final [--fixed_guess_bias]
    python -m scripts.ddm.primacy --analyze --baseline primary --unblind        # after plan step 5 only
On Slurm: sbatch --array=0-19 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.primacy,EXTRA_ARGS="--predict --fits_dir ..." scripts/slurm/fit_mouse_ddm.slurm
"""

import argparse
import logging
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit

from config import dir_config
from scripts.ddm.fit_mouse_ddm import CENSOR_AT, DEVICE, EXTREMA_LEAK_BOUNDS, LIKELIHOOD_PARAMS, MIN_RT, MouseDDM, load_inputs, make_params, to_ms

logger = logging.getLogger(__name__)

# Baselines (primacy plan, amendment 3): primary = common model, secondary = with leak + urgency. Fast-only guesses.
BASELINES = {"primary": "L0U0V1Z0G1", "secondary": "L1U1V1Z0G1"}
# Strategy model (amendment 4): extrema detection = the common model with a 5-50 ms time constant. Kept out of BASELINES
# so the default prediction grid (and its job ids) is unchanged; request with --baselines extrema.
STRATEGY_MODELS = {"extrema": "L1U0V1Z0G1"}
MODELS = {**BASELINES, **STRATEGY_MODELS}
LEAK_BOUNDS = {"extrema": EXTREMA_LEAK_BOUNDS}
GUESS_MODEL = "fast_only"
TIMING = {1: "early", 2: "middle", 3: "late"}
MAX_ABS_COH = 0.36  # primary analysis (plan section 4); all coherences as robustness
N_REPS = 200  # plan section 3: >= 200 simulated repetitions per trial
RT_QUANTILES = [0.1, 0.3, 0.5, 0.7, 0.9]
PRIOR_SD = 1.0  # Normal(0, 1) fixed effects, HalfNormal(1) random-effect SDs (plan section 6)
# Gates 2-3 pass rule (accepted by V. Thakur, 2026-10-22; the plan says "within the spread of the model's predictions"
# without a number). With 95% ranges, ~5% of cells fall outside by chance.
GATE_MIN_INSIDE = 0.8  # fraction of (mouse x RT quantile) cells, and of mice for the censored fraction, inside


# ---------------------------------------------------------------- inputs

def pulse_rows(inputs: dict, mouse: str) -> np.ndarray:
    return np.flatnonzero((inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] != 0))


def no_pulse_frames(inputs: dict, rows: np.ndarray) -> np.ndarray:
    """The trial's motion energy with the pulse removed: base coherence through the rig's onset step response, plus
    the trial's own noise N (= ME - S). On control trials this equals S + N exactly (checked in check_inputs)."""
    rig = np.unique(inputs["data_source"][rows]).item()
    onset = inputs[f"onset_response_{rig}"][: inputs["signal"].shape[1]]
    return inputs["signed_coherence"][rows, None] * onset[None, :] + inputs["noise"][rows]


def check_inputs(inputs: dict, mouse: str) -> float:
    """Largest |S - coherence x onset response| on the mouse's control trials (should be ~float32 rounding)."""
    rows = np.flatnonzero((inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] == 0))
    return float(np.abs(no_pulse_frames(inputs, rows) - (inputs["signal"][rows] + inputs["noise"][rows])).max())


def stimuli(inputs: dict, rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """1 ms inputs with and without the pulse."""
    fr = int(inputs["frame_rate"])
    return to_ms(inputs["signal"][rows] + inputs["noise"][rows], fr), to_ms(no_pulse_frames(inputs, rows).astype(np.float32), fr)


def make_model(variant: str, rig: str, fixed_guess_bias: bool = False, time_varying_gain: bool = False, leak_bounds: tuple[float, float] | None = None) -> MouseDDM:
    free, fixed = make_params(variant, GUESS_MODEL, time_varying_gain=time_varying_gain, fixed_guess_bias=fixed_guess_bias, leak_bounds=leak_bounds)
    return MouseDDM(free_params=free, fixed_params=fixed, device=DEVICE, likelihood_params=LIKELIHOOD_PARAMS, censor_at=CENSOR_AT, min_rt=MIN_RT[rig])


def load_fit(fits_dir: Path, mouse: str, variant: str, split: str, fixed_guess_bias: bool, leak_bounds: tuple[float, float] | None = None, drift_gain_max: float | None = None) -> dict:
    """A fit whose guess form (and leak range) matches; refuses silently mismatched fits (as model_recovery does)."""
    path = fits_dir / f"{mouse}_{variant}_{split}.pkl"
    with open(path, "rb") as f:
        r = pickle.load(f)
    form = (r.get("guess_model", "single"), r.get("fixed_guess_bias", False))
    if form != (GUESS_MODEL, fixed_guess_bias):
        raise ValueError(f"{path} has guess form {form}, expected {(GUESS_MODEL, fixed_guess_bias)}")
    fit_bounds = r.get("leak_bounds")
    if (tuple(fit_bounds) if fit_bounds else None) != (tuple(leak_bounds) if leak_bounds else None):
        raise ValueError(f"{path} has leak bounds {fit_bounds}, expected {leak_bounds}")
    if r.get("drift_gain_max") != drift_gain_max:
        raise ValueError(f"{path} has drift_gain_max {r.get('drift_gain_max')}, expected {drift_gain_max}")
    return r


# ---------------------------------------------------------------- predictions

def simulate_outcomes(model: MouseDDM, params: dict, stimulus: np.ndarray, condition: np.ndarray, n_reps: int, seed: int) -> pd.DataFrame:
    sim = model._map_outcomes(model.simulate(stimulus, params, n_reps=n_reps, seed=seed, labels=condition))
    model.simulator.clear_cache()
    return sim


def summarize_predictions(sim: pd.DataFrame, direction: np.ndarray, n_trials: int, prefix: str) -> pd.DataFrame:
    """Per trial: P(choice in the pulse direction | response), P(censored), mean RT of responses."""
    trial = sim["trial"].to_numpy()
    responded = (sim["choice"] >= 0).to_numpy()
    toward = responded & ((sim["choice"].to_numpy() == 1) == (direction[trial] > 0))
    n_sim = np.bincount(trial, minlength=n_trials)
    n_resp = np.bincount(trial, weights=responded, minlength=n_trials)
    n_toward = np.bincount(trial, weights=toward, minlength=n_trials)
    rt_sum = np.bincount(trial[responded], weights=sim["rt"].to_numpy()[responded], minlength=n_trials)
    return pd.DataFrame({
        f"{prefix}p_hat": (n_toward + 0.5) / (n_resp + 1.0),  # never exactly 0 or 1, so logit(p_hat) is finite
        f"{prefix}p_censored": 1 - n_resp / np.maximum(n_sim, 1),
        f"{prefix}mean_rt": np.where(n_resp > 0, rt_sum / np.maximum(n_resp, 1), np.nan),
        f"{prefix}n_resp": n_resp,
    })


def per_rep_summary(sim: pd.DataFrame) -> dict:
    """Each repetition is one simulated dataset of the mouse's pulse trials: its RT quantiles and censored fraction."""
    q, cens = [], []
    for _, s in sim.groupby("rep"):
        resp = s[s.choice >= 0]
        q.append(np.quantile(resp.rt, RT_QUANTILES) if len(resp) else np.full(len(RT_QUANTILES), np.nan))
        cens.append(1 - len(resp) / len(s))
    return {"rt_quantiles": np.array(q), "censored_fraction": np.array(cens)}


def predict_mouse(inputs: dict, mouse: str, params: dict, variant: str, n_reps: int, seed: int, fixed_guess_bias: bool = False, leak_bounds: tuple[float, float] | None = None) -> dict:
    """Predictions for one mouse's pulse trials from `params` (no observed choices or RTs are read)."""
    rows = pulse_rows(inputs, mouse)
    rig = np.unique(inputs["data_source"][rows]).item()
    model = make_model(variant, rig, fixed_guess_bias, time_varying_gain="gain_decay" in params and params["gain_decay"] != 0, leak_bounds=leak_bounds)
    with_pulse, without = stimuli(inputs, rows)
    condition = inputs["condition"][rows]
    direction = np.sign(inputs["sched_pulse_type"][rows])
    sim = simulate_outcomes(model, params, with_pulse, condition, n_reps, seed)
    sim0 = simulate_outcomes(model, params, without, condition, n_reps, seed)  # same seed: common random numbers
    trials = pd.DataFrame({
        "row": rows, "mouse": mouse, "rig": rig,
        "timing": np.abs(inputs["sched_pulse_type"][rows]), "direction": direction,
        "coh": inputs["signed_coherence"][rows],
    })
    trials = pd.concat([trials, summarize_predictions(sim, direction, len(rows), ""), summarize_predictions(sim0, direction, len(rows), "nopulse_")], axis=1)
    return {"mouse": mouse, "rig": rig, "variant": variant, "params": params, "n_reps": n_reps, "seed": seed, "trials": trials, "reps": per_rep_summary(sim)}


# ---------------------------------------------------------------- observed data and the analysis table

def attach_observed(pred: dict, rt: np.ndarray, choice: np.ndarray) -> pd.DataFrame:
    """Add observed outcomes (real, with --unblind, or synthetic) to a mouse's prediction table."""
    t = pred["trials"].copy()
    t["rt"], t["choice"] = rt, choice
    t["responded"] = choice >= 0
    t["y"] = np.where(t.responded, ((choice == 1) == (t.direction > 0)).astype(float), np.nan)
    return t


def analysis_table(tables: list[pd.DataFrame], max_abs_coh: float | None = MAX_ABS_COH) -> pd.DataFrame:
    t = pd.concat(tables, ignore_index=True)
    t = t[t.responded]
    if max_abs_coh is not None:
        t = t[t.coh.abs() <= max_abs_coh + 1e-9]
    return t.assign(offset=logit(t.p_hat), pred_effect=logit(t.p_hat) - logit(t.nopulse_p_hat))


# ---------------------------------------------------------------- GLMM (PyMC)

def glmm(t: pd.DataFrame, timings: list[int], rig_term: bool = True, rig_interaction: bool = False, trend: bool = False,
         draws: int = 1000, tune: int = 1000, chains: int = 4, seed: int = 0) -> dict:
    """Mixed-effects logistic regression with offset logit(p_hat). Timing coded with early as reference (or, with
    trend=True, as a linear slope over the timings 0, 1, 2 for early, middle, late); random intercept and timing
    slope(s) per mouse, non-centred. Returns posterior summaries of the fixed effects and per-mouse timing effects."""
    import pymc as pm

    t = t[t.timing.isin(timings)]
    mice = sorted(t.mouse.unique())
    m = t.mouse.map({k: i for i, k in enumerate(mice)}).to_numpy()
    uw = (t.rig == "uw").to_numpy(float)
    rig_term = rig_term and 0 < uw.mean() < 1
    level = t.timing.map({k: i for i, k in enumerate(sorted(timings))}).to_numpy()
    n_slopes = 1 if trend else len(timings) - 1  # 0: intercept-only model (gate 1)
    X = level[:, None].astype(float) if trend else np.stack([level == j for j in range(1, len(timings))] or [np.zeros(len(t))], axis=1).astype(float)[:, :n_slopes]
    names = ["trend"] if trend else [TIMING[k] for k in sorted(timings)[1:]]
    with pm.Model():
        b0 = pm.Normal("b0", 0, PRIOR_SD)
        sd_u = pm.HalfNormal("sd_u", PRIOR_SD)
        z_u = pm.Normal("z_u", 0, 1, shape=len(mice))
        if n_slopes:
            b = pm.Normal("b_timing", 0, PRIOR_SD, shape=n_slopes)
            sd_v = pm.HalfNormal("sd_v", PRIOR_SD, shape=n_slopes)
            z_v = pm.Normal("z_v", 0, 1, shape=(len(mice), n_slopes))
        eta = t.offset.to_numpy() + b0 + sd_u * z_u[m]
        if n_slopes:
            eta = eta + ((b + sd_v * z_v[m]) * X).sum(axis=1)
        if rig_term:
            eta = eta + pm.Normal("b_rig", 0, PRIOR_SD) * uw
        if rig_interaction:
            eta = eta + (pm.Normal("b_timing_x_uw", 0, PRIOR_SD, shape=n_slopes) * X).sum(axis=1) * uw
        if n_slopes:
            pm.Deterministic("mouse_timing", b + sd_v * z_v)
        pm.Bernoulli("y", logit_p=eta, observed=t.y.to_numpy().astype(int))
        idata = pm.sample(draws, tune=tune, chains=chains, cores=chains, random_seed=seed, progressbar=False, target_accept=0.95)
    post = idata.posterior

    def summ(x):
        x = np.asarray(x).ravel()
        return {"mean": float(x.mean()), "lo": float(np.quantile(x, 0.025)), "hi": float(np.quantile(x, 0.975)), "p_neg": float((x < 0).mean())}

    out = {"n_trials": len(t), "n_mice": len(mice), "names": names, "b0": summ(post["b0"])}
    for j, n in enumerate(names):
        out[f"b_{n}"] = summ(post["b_timing"][..., j])
        out[f"mice_{n}"] = {mk: summ(post["mouse_timing"][..., i, j]) for i, mk in enumerate(mice)}
        if rig_interaction:
            out[f"b_{n}_x_uw"] = summ(post["b_timing_x_uw"][..., j])
    if rig_term:
        out["b_rig"] = summ(post["b_rig"])
    import arviz as az
    s = az.summary(idata, var_names=["b0"] + (["b_timing"] if n_slopes else []), kind="diagnostics")
    out["max_rhat"], out["min_ess_bulk"] = float(s.r_hat.max()), float(s.ess_bulk.min())
    out["divergences"] = int(idata.sample_stats.diverging.sum())
    return out


def gate_departure(t: pd.DataFrame, **kw) -> dict:
    """Gate 1: pooled departure b0 (all timings, intercept-only model with random intercepts) against the predicted
    pulse effect. Passes if the 95% interval of b0 contains 0 or |mean b0| < 25% of the mean predicted effect."""
    g = glmm(t.assign(timing=1), [1], **kw)
    effect = float(t.pred_effect.mean())
    passed = (g["b0"]["lo"] <= 0 <= g["b0"]["hi"]) or abs(g["b0"]["mean"]) < 0.25 * abs(effect)
    return {"b0": g["b0"], "predicted_effect": effect, "pass": bool(passed), "diagnostics": {k: g[k] for k in ("max_rhat", "min_ess_bulk", "divergences")}}


def gate_distributions(preds: dict, tables: dict) -> pd.DataFrame:
    """Gates 2-3, per mouse: observed pulse-trial RT quantiles and censored fraction (all timings, all coherences)
    against the 2.5-97.5% range over simulated datasets (each repetition is one dataset of the mouse's trials)."""
    rows = []
    for mouse, pred in preds.items():
        t = tables[mouse]
        reps = pred["reps"]
        obs_q = np.quantile(t.rt[t.responded], RT_QUANTILES)
        lo, hi = np.nanquantile(reps["rt_quantiles"], [0.025, 0.975], axis=0)
        obs_c = 1 - t.responded.mean()
        clo, chi = np.quantile(reps["censored_fraction"], [0.025, 0.975])
        rows.append({"mouse": mouse, **{f"rt_q{int(q * 100)}_inside": bool(a <= o <= b) for q, o, a, b in zip(RT_QUANTILES, obs_q, lo, hi)},
                     "censored_obs": obs_c, "censored_lo": clo, "censored_hi": chi, "censored_inside": bool(clo <= obs_c <= chi)})
    return pd.DataFrame(rows).set_index("mouse")


def rt_residuals(tables: list[pd.DataFrame]) -> pd.DataFrame:
    """Secondary outcome: observed minus predicted mean RT (responses only) per mouse and timing."""
    t = pd.concat(tables, ignore_index=True)
    t = t[t.responded]
    g = t.groupby(["mouse", "timing"])
    return pd.DataFrame({"observed": g.rt.mean(), "predicted": g.apply(lambda x: np.average(x.mean_rt, weights=x.n_resp)), "n": g.size()}).assign(residual=lambda x: x.observed - x.predicted)


def gate_pass(res: dict) -> bool:
    d = res["gate_distributions"]
    rt_inside = d[[c for c in d if c.startswith("rt_q")]].to_numpy().mean()
    return res["gate_departure"]["pass"] and rt_inside >= GATE_MIN_INSIDE and d.censored_inside.mean() >= GATE_MIN_INSIDE


def run_analysis(preds: dict, tables: dict, max_abs_coh: float | None = MAX_ABS_COH, require_gate: bool = True, **kw) -> dict:
    """Gate, then the timing tests (plan sections 6-7). The timing tests are not run when the gate fails (plan
    section 7: the model is revised first), unless require_gate=False."""
    t = analysis_table(list(tables.values()), max_abs_coh)
    res = {"gate_departure": gate_departure(t, **kw), "gate_distributions": gate_distributions(preds, tables), "rt_residuals": rt_residuals(list(tables.values()))}
    res["gate_pass"] = gate_pass(res)
    if require_gate and not res["gate_pass"]:
        logger.warning("predictive check failed; timing tests not run (revise the model first)")
        return res
    res["primary"] = glmm(t, [1, 2], **kw)
    res["rig_interaction"] = glmm(t, [1, 2], rig_interaction=True, **kw)
    uw = t[t.rig == "uw"]
    if len(uw):
        res["uw_late"] = glmm(uw, [1, 2, 3], **kw)
        res["uw_trend"] = glmm(uw, [1, 2, 3], trend=True, **kw)
    return res


# ---------------------------------------------------------------- strategy test (amendments 4-5)

STRATEGY_SD_THRESHOLD = 3.0  # amendment 4, item 5
STRATEGY_MIN_MICE = 6  # of 10, same sign as the summed difference


def trial_loglik(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Per-trial Bernoulli log-likelihood of the observed choice."""
    return y * np.log(p) + (1 - y) * np.log(1 - p)


def strategy_test(tables_a: dict, tables_b: dict, max_abs_coh: float | None = MAX_ABS_COH) -> dict:
    """Model a vs model b on the same pulse trials (amendment 5). Primary statistic, per trial: the log-likelihood
    gained by each model's predicted pulse effect, g = ll(p_hat) - ll(p_hat without the pulse), and the paired
    difference g_a - g_b, summed over trials and mice. Secondary: the paired difference of total log-likelihood
    ll_a - ll_b. Each comes with its SD from the paired per-trial differences (variance across trials x n, summed over
    mice; a Vuong-type SD). Each trial's prediction noise is part of that spread, so it is not added again (adding it
    double-counts and, for the pulse gain, ignores that the with- and without-pulse predictions share random numbers).
    Model a (b) is favoured if the sum exceeds STRATEGY_SD_THRESHOLD SDs in its favour
    and the per-mouse sums have that sign in >= STRATEGY_MIN_MICE mice; otherwise "not distinguished"."""
    per_mouse = []
    for mouse in sorted(tables_a):
        a, b = tables_a[mouse], tables_b[mouse]
        assert (a.row.to_numpy() == b.row.to_numpy()).all(), f"{mouse}: models predicted different trials"
        keep = a.responded.to_numpy() & ((a.coh.abs() <= max_abs_coh + 1e-9) if max_abs_coh is not None else True)
        y = a.y.to_numpy()[keep]
        out = {"mouse": mouse, "n": int(keep.sum())}
        lla, ll0a = trial_loglik(y, a.p_hat.to_numpy()[keep]), trial_loglik(y, a.nopulse_p_hat.to_numpy()[keep])
        llb, ll0b = trial_loglik(y, b.p_hat.to_numpy()[keep]), trial_loglik(y, b.nopulse_p_hat.to_numpy()[keep])
        for stat, d in [("pulse_gain", (lla - ll0a) - (llb - ll0b)), ("total", lla - llb)]:
            out[f"{stat}_sum"] = float(d.sum())
            out[f"{stat}_var"] = float(d.var(ddof=1) * len(d)) if len(d) > 1 else 0.0
        per_mouse.append(out)
    pm = pd.DataFrame(per_mouse).set_index("mouse")
    res = {"per_mouse": pm}
    for stat in ["pulse_gain", "total"]:
        total, sd = pm[f"{stat}_sum"].sum(), np.sqrt(pm[f"{stat}_var"].sum())
        same_sign = int((np.sign(pm[f"{stat}_sum"]) == np.sign(total)).sum())
        favoured = ("a" if total > 0 else "b") if abs(total) > STRATEGY_SD_THRESHOLD * sd and same_sign >= STRATEGY_MIN_MICE else "not distinguished"
        res[stat] = {"sum": float(total), "sd": float(sd), "z": float(total / sd) if sd > 0 else np.nan, "mice_same_sign": same_sign, "favoured": favoured}
    return res


# ---------------------------------------------------------------- CLI

def build_grid(inputs: dict, baselines: list[str] | None = None) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"baseline": b, "mouse": m} for b in (baselines or BASELINES) for m in mice]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz")
    parser.add_argument("--fits_dir", help="control-only fits of the baselines, relative to processed (plan step 5)")
    parser.add_argument("--out_dir", default="ddm/primacy", help="relative to processed")
    parser.add_argument("--fixed_guess_bias", action="store_true")
    parser.add_argument("--n_reps", type=int, default=N_REPS)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--predict", action="store_true")
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--baseline", choices=list(MODELS), default="primary")
    parser.add_argument("--baselines", nargs="*", choices=list(MODELS), help="models in the prediction grid (default: primary, secondary; extrema needs its own --fits_dir)")
    parser.add_argument("--all_coherences", action="store_true", help="robustness: no |coherence| limit")
    parser.add_argument("--unblind", action="store_true", help="compare with the recorded pulse-trial choices (after plan step 5 only)")
    parser.add_argument("--drift_gain_max", type=float, help="extrema model fitted with a wider drift_gain bound (amendment 5)")
    parser.add_argument("--strategy_test", action="store_true", help="amendment 4 item 5 / amendment 5: extrema vs primary baseline (after gate 1, with --unblind)")
    args = parser.parse_args()

    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / args.inputs)
    baselines = args.baselines or list(BASELINES)
    grid = build_grid(inputs, baselines)
    if args.list:
        print(f"{len(grid)} prediction jobs: {len(baselines)} models x {len(grid) // len(baselines)} mice; --array=0-{len(grid) - 1}")
    elif args.predict:
        job = grid[args.job_id]
        out = processed / args.out_dir / job["baseline"] / f"{job['mouse']}.pkl"
        if out.exists():
            logger.info("skipping %s: output exists", job)
        else:
            variant = MODELS[job["baseline"]]
            leak_bounds = LEAK_BOUNDS.get(job["baseline"])
            gain_max = args.drift_gain_max if job["baseline"] in STRATEGY_MODELS else None
            fit = load_fit(processed / args.fits_dir, job["mouse"], variant, "control", args.fixed_guess_bias, leak_bounds, gain_max)
            t0 = time.time()
            pred = predict_mouse(inputs, job["mouse"], fit["parameters"], variant, args.n_reps, args.seed, args.fixed_guess_bias, leak_bounds)
            pred.update(fit_path=str(processed / args.fits_dir), fixed_guess_bias=args.fixed_guess_bias, seconds=time.time() - t0)
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_suffix(".tmp")
            with open(tmp, "wb") as f:
                pickle.dump(pred, f)
            tmp.replace(out)
            logger.info("saved %s (%d pulse trials, %.0f s)", out, len(pred["trials"]), pred["seconds"])
    elif args.strategy_test:
        if not args.unblind:
            raise SystemExit("refusing to compare with recorded pulse-trial choices without --unblind (after gate 1 only)")
        tables = {}
        for model in ["extrema", "primary"]:
            tables[model] = {}
            for p in sorted((processed / args.out_dir / model).glob("*.pkl")):
                with open(p, "rb") as f:
                    pr = pickle.load(f)
                tables[model][p.stem] = attach_observed(pr, inputs["rt"][pr["trials"].row], inputs["choice"][pr["trials"].row])
        res = strategy_test(tables["extrema"], tables["primary"])
        out = processed / args.out_dir / "results_strategy.pkl"
        with open(out, "wb") as f:
            pickle.dump(res, f)
        print(res["per_mouse"].round(2).to_string())
        print({k: res[k] for k in ("pulse_gain", "total")}, "(a = extrema, b = primary)")
    elif args.analyze:
        if not args.unblind:
            raise SystemExit("refusing to compare with recorded pulse-trial choices without --unblind (plan step 5 must be done)")
        preds = {}
        for p in sorted((processed / args.out_dir / args.baseline).glob("*.pkl")):
            with open(p, "rb") as f:
                preds[p.stem] = pickle.load(f)
        tables = {m: attach_observed(pr, inputs["rt"][pr["trials"].row], inputs["choice"][pr["trials"].row]) for m, pr in preds.items()}
        res = run_analysis(preds, tables, None if args.all_coherences else MAX_ABS_COH)
        out = processed / args.out_dir / f"results_{args.baseline}{'_allcoh' if args.all_coherences else ''}.pkl"
        with open(out, "wb") as f:
            pickle.dump(res, f)
        logger.info("saved %s", out)
