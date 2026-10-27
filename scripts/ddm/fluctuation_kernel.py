"""Psychophysical kernels on within-trial motion-energy fluctuations (plan .agents/plans/2026-10-25-fluctuation-kernel-power.md).

The stimulus noise N(t) is ~57% a fixed per-trial bias (hidden coherence) and ~43% fluctuation within the trial
(correlation time ~200 ms). Removing each trial's mean leaves the fluctuation f(t), which can be reverse-correlated
with choices to estimate how evidence is weighted over time.

Kernel per mouse: mean f in 100 ms bins (0.1–0.9 s after onset, frames before the response only), rightward minus
leftward choices, on responded control trials with |coh| <= 36%. The reaction-time task makes later bins rest on fewer
open trials, so the reference is the same kernel computed on choices simulated from the flat-weighting model (control
fit, primary model) for the same stimuli. Statistic per mouse: primacy index = (early 0.1-0.4 s minus late 0.5-0.9 s) of K - K_ref (% coherence; > 0 primacy);
group: mean over mice, t-test across mice.

--power (synthetic only): "observed" datasets simulated with drift-gain decay 0 / 20 / 40% over 0.5 s, reference from
the generating parameters without decay (no refit, so power is if anything overstated). Also response-aligned kernels
of the integrator and extrema detection (E) to see whether their shapes separate.
Real-data mode (--observed) refuses without --unblind; not used before the power check is reported.

--resp_power (synthetic only): late-weight index of the response-aligned kernel (last 0.2 s minus 0.6-0.4 s before the
response) on datasets from the integrator and from E, classified by distance to each model's predicted index.

--observed --unblind (amendment 8, primacy-analysis-plan.md): the late-weight index of the recorded choices, classified
against the saved v2 predictions with the pre-specified verdict rule; no simulation.

Usage: python -m scripts.ddm.fluctuation_kernel --power | --resp_power [--datasets 20] [--ref_reps 10] | --observed --unblind
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import EXTREMA_LEAK_BOUNDS, load_inputs, select
from scripts.ddm.primacy_sensitivity import gain_decay

FRAME = 1 / 60
BINS = [(0.1 + 0.1 * i, 0.2 + 0.1 * i) for i in range(8)]  # stimulus-aligned, s
RESP_BINS = [(-0.6 + 0.1 * i, -0.5 + 0.1 * i) for i in range(6)]  # response-aligned, s before the response
MEAN_FRAMES = slice(10, 300)  # trial-mean window for removing the fixed bias (after the onset response settles)
VARIANT = primacy.BASELINES["primary"]
# 48 UCLA pulse trials without a response are labelled controls in the DDM inputs (pulse-data report 2026-10-23); excluded here
PULSE_TABLE = "pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv"


def mislabelled_pulses(processed: Path) -> set:
    t = pd.read_csv(processed / PULSE_TABLE, usecols=["trial_id", "in_ddm_input", "ddm_sched_pulse_type", "pulse_category", "no_response_recorded"])
    m = t[t.in_ddm_input.astype(bool) & (t.ddm_sched_pulse_type == 0) & (t.pulse_category != "control") & t.no_response_recorded.astype(bool)]
    assert len(m) == 48, len(m)
    return set(m.trial_id.astype(str))


def mouse_trials(inputs: dict, mouse: str) -> np.ndarray:
    m = (inputs["subject_id"] == mouse) & (inputs["sched_pulse_type"] == 0) & (np.abs(inputs["signed_coherence"]) <= 0.36 + 1e-9)
    return np.flatnonzero(m & ~inputs["mislabelled_pulse"])


def fluctuation(inputs: dict, rows: np.ndarray) -> np.ndarray:
    n = inputs["noise"][rows].astype(float) * 100  # % coherence units
    return n - n[:, MEAN_FRAMES].mean(axis=1, keepdims=True)


def binned(f: np.ndarray, rt: np.ndarray, bins, aligned: str) -> np.ndarray:
    """Per-trial mean fluctuation in each bin, using frames before the response; NaN where a bin has no valid frame."""
    t = np.arange(f.shape[1]) * FRAME
    out = np.full((len(f), len(bins)), np.nan)
    for j, (lo, hi) in enumerate(bins):
        tt = t[None, :] - (rt[:, None] if aligned == "response" else 0.0)
        valid = (tt >= lo) & (tt < hi) & (t[None, :] < rt[:, None]) & (t[None, :] >= 0.1)
        cnt = valid.sum(axis=1)
        s = np.where(valid, f, 0.0).sum(axis=1)
        out[:, j] = np.where(cnt > 0, s / np.maximum(cnt, 1), np.nan)
    return out


def kernel(f: np.ndarray, rt: np.ndarray, choice: np.ndarray, bins, aligned: str = "stimulus") -> np.ndarray:
    ok = choice >= 0
    b = binned(f[ok], rt[ok], bins, aligned)
    c = choice[ok]
    return np.nanmean(b[c == 1], axis=0) - np.nanmean(b[c == 0], axis=0)


EARLY, LATE = slice(0, 3), slice(4, 8)  # bins 0.1-0.4 s and 0.5-0.9 s


def primacy_index(k_obs: np.ndarray, k_ref: np.ndarray) -> float:
    """(early - late) of K_obs - K_ref, % coherence. 0 under flat weighting (the reference carries the reaction-time
    termination effects); > 0 when weight declines over time (primacy), < 0 when it grows (recency). No division by the
    small, noisy reference kernel."""
    d = k_obs - k_ref
    return float(np.nanmean(d[EARLY]) - np.nanmean(d[LATE]))


def simulate(model, params: dict, stim: np.ndarray, condition: np.ndarray, n_reps: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    sim = model._map_outcomes(model.simulate(stim, params, n_reps=n_reps, seed=seed, labels=condition))
    model.simulator.clear_cache()
    out = []
    for _, s in sim.groupby("rep"):
        s = s.sort_values("trial")
        out.append((s["rt"].to_numpy(float), s["choice"].to_numpy(int)))
    return out


def power(inputs: dict, processed: Path, datasets: int, ref_reps: int, levels=(0.0, 0.2, 0.4)) -> pd.DataFrame:
    mice = sorted(np.unique(inputs["subject_id"]))
    rows_out, resp = [], {}
    for mouse in mice:
        rows = mouse_trials(inputs, mouse)
        rig = np.unique(inputs["data_source"][rows]).item()
        _, stim = select(inputs, rows)
        cond = inputs["condition"][rows]
        f = fluctuation(inputs, rows)
        params = primacy.load_fit(processed / "ddm/fits_final", mouse, VARIANT, "control", False)["parameters"]
        model = primacy.make_model(VARIANT, rig, time_varying_gain=True)
        refs = simulate(model, {**params, "gain_decay": 0.0}, stim, cond, ref_reps, 1000)
        k_ref = np.nanmean([kernel(f, rt, ch, BINS) for rt, ch in refs], axis=0)
        resp[(mouse, "integrator")] = np.nanmean([kernel(f, rt, ch, RESP_BINS, "response") for rt, ch in refs], axis=0)
        for lv in levels:
            sims = simulate(model, {**params, "gain_decay": gain_decay(lv)}, stim, cond, datasets, 2000 + int(lv * 100))
            for d, (rt, ch) in enumerate(sims):
                rows_out.append({"mouse": mouse, "level": lv, "dataset": d, "b": primacy_index(kernel(f, rt, ch, BINS), k_ref), "n": int((ch >= 0).sum())})
        e_params = primacy.load_fit(processed / "ddm/fits_guess_fast_only_leak20-200", mouse, "L1U0V1Z0G1", "control", False, EXTREMA_LEAK_BOUNDS)["parameters"]
        e_model = primacy.make_model("L1U0V1Z0G1", rig, leak_bounds=EXTREMA_LEAK_BOUNDS)
        e_sims = simulate(e_model, e_params, stim, cond, ref_reps, 3000)
        resp[(mouse, "extrema")] = np.nanmean([kernel(f, rt, ch, RESP_BINS, "response") for rt, ch in e_sims], axis=0)
        print(f"{mouse}: {len(rows)} trials; reference kernel (stimulus-aligned, % coh): {np.round(k_ref, 2).tolist()}", flush=True)
    return pd.DataFrame(rows_out), resp


def late_index(k: np.ndarray) -> float:
    """Response-aligned late-weight index: mean of the last two bins (-0.2..0 s) minus the first two (-0.6..-0.4 s)."""
    return float(np.nanmean(k[-2:]) - np.nanmean(k[:2]))


def resp_power(inputs: dict, processed: Path, datasets: int, ref_reps: int) -> pd.DataFrame:
    """Integrator (I) vs extrema detection (E): late-weight index of datasets from each generator, with each model's
    prediction per mouse from separate repetitions."""
    rows_out = []
    for mouse in sorted(np.unique(inputs["subject_id"])):
        rows = mouse_trials(inputs, mouse)
        rig = np.unique(inputs["data_source"][rows]).item()
        _, stim = select(inputs, rows)
        cond = inputs["condition"][rows]
        f = fluctuation(inputs, rows)
        models = {
            "I": (primacy.make_model(VARIANT, rig), primacy.load_fit(processed / "ddm/fits_final", mouse, VARIANT, "control", False)["parameters"]),
            "E": (primacy.make_model("L1U0V1Z0G1", rig, leak_bounds=EXTREMA_LEAK_BOUNDS),
                  primacy.load_fit(processed / "ddm/fits_guess_fast_only_leak20-200", mouse, "L1U0V1Z0G1", "control", False, EXTREMA_LEAK_BOUNDS)["parameters"]),
        }
        pred = {}
        for name, (model, params) in models.items():
            pred[name] = np.nanmean([late_index(kernel(f, rt, ch, RESP_BINS, "response")) for rt, ch in simulate(model, params, stim, cond, ref_reps, 4000)])
        for name, (model, params) in models.items():
            for d, (rt, ch) in enumerate(simulate(model, params, stim, cond, datasets, 5000)):
                rows_out.append({"mouse": mouse, "generator": name, "dataset": d, "index": late_index(kernel(f, rt, ch, RESP_BINS, "response")),
                                 "pred_I": pred["I"], "pred_E": pred["E"]})
        print(f"{mouse}: {len(rows)} trials; predicted late-weight index I {pred['I']:.2f}, E {pred['E']:.2f}", flush=True)
    return pd.DataFrame(rows_out)


def resp_report(df: pd.DataFrame) -> None:
    from scipy import stats

    df = df.assign(dI=(df["index"] - df.pred_I) ** 2, dE=(df["index"] - df.pred_E) ** 2)
    g = df.groupby(["generator", "dataset"]).agg(dI=("dI", "sum"), dE=("dE", "sum"), mean=("index", "mean"), sd=("index", "std"), n=("index", "count"))
    g["chosen"] = np.where(g.dI < g.dE, "I", "E")
    g["t"] = g["mean"] / (g["sd"] / np.sqrt(g["n"]))
    crit = stats.t.ppf(0.975, g["n"] - 1)
    g["sig_pos"], g["sig_neg"] = g.t > crit, g.t < -crit
    g = g.reset_index()
    g["correct"] = g.chosen == g.generator
    print("\nlate-weight index, integrator vs extrema detection (per generator, over datasets):")
    print(g.groupby("generator").agg(mean_index=("mean", "mean"), sd_of_mean=("mean", "std"), correct=("correct", "mean"),
                                     sig_pos=("sig_pos", "mean"), sig_neg=("sig_neg", "mean")).round(3).to_string())
    print("\nper-mouse SD of the index across datasets:")
    print(df.groupby(["mouse", "generator"])["index"].std().unstack().round(2).to_string())


def observed(inputs: dict, processed: Path) -> pd.DataFrame:
    """Amendment 8 (primacy-analysis-plan.md): late-weight index of the recorded choices, scored against the saved
    v2 predictions and the synthetic reference distributions of the summed squared distance. No simulation."""
    syn = pd.read_csv(processed / "ddm" / "fluctuation_kernel_resp_power_v2.csv")
    pred = syn.groupby("mouse")[["pred_I", "pred_E"]].first()
    rows_out = []
    for mouse in sorted(np.unique(inputs["subject_id"])):
        rows = mouse_trials(inputs, mouse)
        f = fluctuation(inputs, rows)
        k = kernel(f, inputs["rt"][rows], inputs["choice"][rows], RESP_BINS, "response")
        rows_out.append({"mouse": mouse, "index": late_index(k), "n": int((inputs["choice"][rows] >= 0).sum()),
                         **pred.loc[mouse].to_dict(), **{f"k{j}": v for j, v in enumerate(k)}})
    return pd.DataFrame(rows_out), syn


def observed_report(df: pd.DataFrame, syn: pd.DataFrame) -> None:
    from scipy import stats

    s_i, s_e = ((df["index"] - df.pred_I) ** 2).sum(), ((df["index"] - df.pred_E) ** 2).sum()
    syn = syn.assign(dI=(syn["index"] - syn.pred_I) ** 2, dE=(syn["index"] - syn.pred_E) ** 2)
    g = syn.groupby(["generator", "dataset"])[["dI", "dE"]].sum()
    q_i, q_e = np.percentile(g.loc["I", "dI"], 95), np.percentile(g.loc["E", "dE"], 95)
    fits_i, fits_e = s_i <= q_i, s_e <= q_e
    if s_i < s_e and fits_i and not fits_e:
        verdict = "supports accumulation"
    elif s_e < s_i and fits_e and not fits_i:
        verdict = "supports extrema detection"
    elif not fits_i and not fits_e:
        verdict = "neither model fits"
    else:
        verdict = "not distinguished"
    m, sd, n = df["index"].mean(), df["index"].std(), len(df)
    h = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    print("\nper mouse (late-weight index, % coh):")
    print(df[["mouse", "n", "index", "pred_I", "pred_E"]].round(3).to_string(index=False))
    print(f"\nS_I = {s_i:.2f} (q95 under I {q_i:.2f}); S_E = {s_e:.2f} (q95 under E {q_e:.2f})")
    print(f"group mean index {m:.3f}, 95% t interval [{m - h:.3f}, {m + h:.3f}] (n = {n}; descriptive)")
    print(f"VERDICT (amendment 8): {verdict}")


def report(df: pd.DataFrame, resp: dict) -> None:
    from scipy import stats

    g = df.groupby(["level", "dataset"]).b.agg(["mean", "std", "count"])
    g["t"] = g["mean"] / (g["std"] / np.sqrt(g["count"]))
    crit = stats.t.ppf(0.975, g["count"] - 1)
    g["primacy"] = g["t"] > crit  # index > 0 = primacy
    g["any"] = np.abs(g["t"]) > crit
    print("\ngroup test of the primacy index (mean over mice, t-test across mice; % coherence), per level:")
    print(g.groupby("level").agg(mean_b=("mean", "mean"), sd_of_mean_b=("mean", "std"), detect_primacy=("primacy", "mean"), any_departure=("any", "mean")).round(3).to_string())
    mice = sorted({m for m, _ in resp})
    ki = np.nanmean([resp[(m, "integrator")] for m in mice], axis=0)
    ke = np.nanmean([resp[(m, "extrema")] for m in mice], axis=0)
    print("\nresponse-aligned kernels, mean over mice (bins -0.6..0 s before the response):")
    print("  integrator:", np.round(ki, 2).tolist())
    print("  extrema:   ", np.round(ke, 2).tolist())
    print("  last-bin share of the summed kernel: integrator %.2f, extrema %.2f" % (ki[-1] / np.nansum(ki), ke[-1] / np.nansum(ke)))


if __name__ == "__main__":
    logging.disable(logging.WARNING)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--power", action="store_true")
    parser.add_argument("--datasets", type=int, default=20)
    parser.add_argument("--ref_reps", type=int, default=10)
    parser.add_argument("--resp_power", action="store_true", help="integrator vs extrema detection, response-aligned (synthetic)")
    parser.add_argument("--observed", action="store_true", help="kernels of the recorded choices (after the power check only)")
    parser.add_argument("--unblind", action="store_true")
    args = parser.parse_args()
    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / "ddm/ddm_inputs_global.npz")
    inputs["mislabelled_pulse"] = np.isin(inputs["agg_code"].astype(str), list(mislabelled_pulses(processed)))
    print(f"excluded {inputs['mislabelled_pulse'].sum()} pulse trials mislabelled as controls", flush=True)
    if args.observed:
        if not args.unblind:
            raise SystemExit("refusing to compute kernels of recorded choices without --unblind (power check first)")
        df, syn = observed(inputs, processed)
        df.to_csv(processed / "ddm" / "fluctuation_kernel_observed_2026-10-26.csv", index=False)
        observed_report(df, syn)
    if args.power:
        df, resp = power(inputs, processed, args.datasets, args.ref_reps)
        df.to_csv(processed / "ddm" / "fluctuation_kernel_power_v2.csv", index=False)
        report(df, resp)
    if args.resp_power:
        df = resp_power(inputs, processed, args.datasets, args.ref_reps)
        df.to_csv(processed / "ddm" / "fluctuation_kernel_resp_power_v2.csv", index=False)
        resp_report(df)
