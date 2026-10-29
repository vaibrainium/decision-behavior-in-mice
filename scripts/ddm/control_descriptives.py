"""Control-trial descriptive analyses for the control-only paper (plan .agents/plans/2026-10-29-control-paper.md, step 4;
definitions fixed there before any real-data run).

Trials: responded control trials (sched_pulse_type 0, response at 0.3-5 s). Mice are the unit; rig is not a factor.
  (a) Motion-energy kernels: noise N(t) (% coherence; frames before the response), trials with |coh| <= 36%. Per mouse and
      signed coherence, mean N for right minus left choices (cells with >= 5 of each choice), averaged over cells weighted
      by trial count. 100 ms bins, stimulus-aligned 0-1 s and response-aligned -1-0 s. Supplement: trial mean removed.
      K1: per-mouse mean stimulus-aligned kernel over 0.1-0.5 s against 0.
  (b) Chronometry: median correct RT per |coh| (all trials at 0%); RT quantiles by outcome.
      T1: per-mouse Spearman rho(|coh|, median RT) against 0. T2: per-mouse error minus correct mean RT over |coh| 9/18/36%
      cells with >= 10 errors (weighted by error count) against 0.
  Tests two-sided, one-sample t (and Wilcoxon) across mice, Holm over K1, T1, T2; dz = mean / SD.
Model reference (descriptive): the same quantities on outcomes simulated on the CPU from each mouse's control fit of the
common model (fits_resp_final) and of rapid forgetting E (fits_resp_fast_only_leak20-200_cap), 20 repetitions, fixed seeds;
simulated trials without a response by 5 s are dropped like the real ones.

Usage: python -m scripts.ddm.control_descriptives [--n_reps 20] [--no_sim]
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from config import dir_config
from scripts.ddm import primacy
from scripts.ddm.fit_mouse_ddm import EXTREMA_LEAK_BOUNDS, load_inputs, responded_only, select

logger = logging.getLogger(__name__)

FRAME = 1 / 60
STIM_BINS = [(0.1 * i, 0.1 * (i + 1)) for i in range(10)]
RESP_BINS = [(-1.0 + 0.1 * i, -0.9 + 0.1 * i) for i in range(10)]
K1_BINS = slice(1, 5)  # 0.1-0.5 s
MIN_CELL = 5
MIN_ERRORS = 10
QUANTILES = [0.1, 0.3, 0.5, 0.7, 0.9]
TABLES = Path(__file__).resolve().parents[2] / "dissemination/paper_control/tables"
DATE = "2026-10-29"
MODELS = {
    "common": ("L0U0V1Z0G1", "ddm/fits_resp_final", None),
    "E": ("L1U0V1Z0G1", "ddm/fits_resp_fast_only_leak20-200_cap", EXTREMA_LEAK_BOUNDS),
}


def binned(n: np.ndarray, rt: np.ndarray, bins, aligned: str) -> np.ndarray:
    """Per-trial mean of n in each bin over frames before the response; NaN where a bin has no such frame."""
    t = np.arange(n.shape[1]) * FRAME
    out = np.full((len(n), len(bins)), np.nan)
    for j, (lo, hi) in enumerate(bins):
        tt = t[None, :] - (rt[:, None] if aligned == "response" else 0.0)
        valid = (tt >= lo) & (tt < hi) & (t[None, :] < rt[:, None])
        cnt = valid.sum(axis=1)
        out[:, j] = np.where(cnt > 0, np.where(valid, n, 0.0).sum(axis=1) / np.maximum(cnt, 1), np.nan)
    return out


def kernel(b: np.ndarray, choice: np.ndarray, coh: np.ndarray) -> np.ndarray:
    """Right minus left mean per bin, within signed coherence, weighted by the cell's trial count."""
    ks, ws = [], []
    for c in np.unique(coh):
        m = coh == c
        r, left = m & (choice == 1), m & (choice == 0)
        if r.sum() < MIN_CELL or left.sum() < MIN_CELL:
            continue
        ks.append(np.nanmean(b[r], axis=0) - np.nanmean(b[left], axis=0))
        ws.append(m.sum())
    ks, ws = np.array(ks), np.array(ws, float)
    ok = ~np.isnan(ks)
    return np.where(ok, ks, 0).T @ ws / np.maximum(ok.T @ ws, 1) if len(ks) else np.full(b.shape[1], np.nan)


def kernels(n: np.ndarray, rt: np.ndarray, choice: np.ndarray, coh: np.ndarray) -> dict:
    keep = np.abs(coh) <= 0.36 + 1e-9
    n, rt, choice, coh = n[keep], rt[keep], choice[keep], coh[keep]
    fl = n - n[:, 10:300].mean(axis=1, keepdims=True)  # supplement: fixed per-trial bias removed (window of fluctuation_kernel.MEAN_FRAMES)
    return {
        "stimulus": kernel(binned(n, rt, STIM_BINS, "stimulus"), choice, coh),
        "response": kernel(binned(n, rt, RESP_BINS, "response"), choice, coh),
        "stimulus_fluct": kernel(binned(fl, rt, STIM_BINS, "stimulus"), choice, coh),
        "response_fluct": kernel(binned(fl, rt, RESP_BINS, "response"), choice, coh),
    }


def chronometry(rt: np.ndarray, choice: np.ndarray, coh: np.ndarray) -> tuple[pd.DataFrame, dict]:
    a = np.round(np.abs(coh), 2)
    correct = (choice == 1) == (coh > 0)
    rows = []
    for c in np.unique(a):
        m = a == c
        for outcome, sel in (("all", m), ("correct", m & correct), ("error", m & ~correct)) if c > 0 else (("all", m),):
            if sel.sum() == 0:
                continue
            q = np.quantile(rt[sel], QUANTILES)
            rows.append({"abs_coh": c, "outcome": outcome, "n": int(sel.sum()), "mean_rt": rt[sel].mean(), "median_rt": np.median(rt[sel]),
                         **{f"q{int(p * 100)}": v for p, v in zip(QUANTILES, q)}, "p_correct": correct[m].mean() if c > 0 else np.nan,
                         "p_right": (choice[m] == 1).mean()})
    df = pd.DataFrame(rows)
    chron = df[(df.outcome == "correct") | (df.abs_coh == 0)]
    rho = stats.spearmanr(chron.abs_coh, chron.median_rt).statistic
    e = df[(df.outcome == "error") & df.abs_coh.isin([0.09, 0.18, 0.36]) & (df.n >= MIN_ERRORS)]
    c = df[df.outcome == "correct"].set_index("abs_coh").mean_rt
    diff = np.average(e.mean_rt.to_numpy() - c.loc[e.abs_coh].to_numpy(), weights=e.n) if len(e) else np.nan
    return df, {"rho": rho, "err_minus_corr": diff, "n_err_cells": len(e)}


def summary_stats(d: dict) -> dict:
    """Per mouse: kernel K1 index, chronometric rho, error minus correct RT."""
    return {"K1": float(np.nanmean(d["kernels"]["stimulus"][K1_BINS])), "T1_rho": d["chron"][1]["rho"], "T2_err_minus_corr": d["chron"][1]["err_minus_corr"]}


def analyse(rt, choice, coh, n) -> dict:
    return {"kernels": kernels(n, rt, choice, coh), "chron": chronometry(rt, choice, coh)}


def simulate(name: str, inputs: dict, rows: np.ndarray, processed: Path, n_reps: int, seed: int) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    variant, folder, leak_bounds = MODELS[name]
    mouse = inputs["subject_id"][rows[0]]
    rig = str(np.unique(inputs["data_source"][rows]).item())
    params = primacy.load_fit(processed / folder, mouse, variant, "control", False, leak_bounds, responded=True)["parameters"]
    model = primacy.make_model(variant, rig, leak_bounds=leak_bounds, responded=True)
    _, stim = select(inputs, rows)
    sim = primacy.simulate_outcomes(model, params, stim, inputs["condition"][rows], n_reps, seed)
    out = []
    for _, s in sim.groupby("rep"):
        s = s.sort_values("trial")
        idx = s["trial"].to_numpy()
        ok = s["choice"].to_numpy() >= 0
        out.append((s["rt"].to_numpy(float)[ok], s["choice"].to_numpy(int)[ok], idx[ok]))
    return out


def group_test(x: np.ndarray) -> dict:
    x = x[~np.isnan(x)]
    t = stats.ttest_1samp(x, 0.0)
    ci = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
    return {"n_mice": len(x), "mean": x.mean(), "ci_low": ci[0], "ci_high": ci[1], "median": np.median(x), "sd": x.std(ddof=1),
            "t": t.statistic, "p_t": t.pvalue, "p_wilcoxon": stats.wilcoxon(x).pvalue, "dz": x.mean() / x.std(ddof=1)}


def holm(p: np.ndarray) -> np.ndarray:
    order = np.argsort(p)
    adj = np.empty(len(p))
    run = 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(run, 1.0)
    return adj


def main(n_reps: int, no_sim: bool) -> None:
    processed = Path(dir_config.data.processed)
    inputs = responded_only(load_inputs(processed / "ddm/ddm_inputs_global.npz"))
    control = inputs["sched_pulse_type"] == 0
    assert not (inputs["rt"][control] > 5).any() and (inputs["rt"][control] >= 0.3).all()
    k_rows, chron_rows, per_mouse = [], [], []
    for mouse in sorted(np.unique(inputs["subject_id"])):
        rows = np.flatnonzero(control & (inputs["subject_id"] == mouse))
        coh, noise = inputs["signed_coherence"][rows], inputs["noise"][rows].astype(float) * 100
        sources = {"data": [(inputs["rt"][rows], inputs["choice"][rows], np.arange(len(rows)))]}
        if not no_sim:
            for i, name in enumerate(MODELS):
                sources[name] = simulate(name, inputs, rows, processed, n_reps, 7000 + i)
        for src, reps in sources.items():
            for r, (rt, ch, idx) in enumerate(reps):
                d = analyse(rt, ch, coh[idx], noise[idx])
                for kind, k in d["kernels"].items():
                    bins = RESP_BINS if kind.startswith("response") else STIM_BINS
                    k_rows += [{"mouse": mouse, "source": src, "rep": r, "kind": kind, "bin_start": lo, "kernel": v} for (lo, _), v in zip(bins, k)]
                chron_rows.append(d["chron"][0].assign(mouse=mouse, source=src, rep=r))
                per_mouse.append({"mouse": mouse, "source": src, "rep": r, "n_trials": len(rt), **summary_stats(d)})
        logger.info("%s: %d trials; data %s", mouse, len(rows), per_mouse[-1 - (0 if no_sim else 2 * n_reps)])
    TABLES.mkdir(parents=True, exist_ok=True)
    k_df, c_df, m_df = pd.DataFrame(k_rows), pd.concat(chron_rows, ignore_index=True), pd.DataFrame(per_mouse)
    k_df.to_csv(TABLES / f"control_kernels_{DATE}.csv", index=False)
    c_df.to_csv(TABLES / f"control_chronometry_{DATE}.csv", index=False)
    m_df.to_csv(TABLES / f"control_per_mouse_{DATE}.csv", index=False)
    data = m_df[m_df.source == "data"].set_index("mouse")
    tests = pd.DataFrame([{"test": k, **group_test(data[k].to_numpy(float))} for k in ("K1", "T1_rho", "T2_err_minus_corr")])
    tests["p_t_holm"], tests["p_wilcoxon_holm"] = holm(tests.p_t.to_numpy()), holm(tests.p_wilcoxon.to_numpy())
    tests.to_csv(TABLES / f"control_tests_{DATE}.csv", index=False)
    print(tests.round(4).to_string())
    print(m_df.groupby(["source", "mouse"])[["K1", "T1_rho", "T2_err_minus_corr"]].mean().round(3).to_string())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n_reps", type=int, default=20)
    parser.add_argument("--no_sim", action="store_true", help="real data only")
    args = parser.parse_args()
    main(args.n_reps, args.no_sim)
