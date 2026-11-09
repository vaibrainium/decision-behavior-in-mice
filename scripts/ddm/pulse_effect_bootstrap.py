"""Sampling uncertainty of the data pulse effect, and model predictions against it (plans/2026-11-09-pulse-effect-bootstrap.md).
EXPLORATORY (author, 2026-11-08): descriptive; no decision rules.

Statistic: the per-mouse window effect of pulse_joint_signatures.stats_of (responded trials, symmetric cells, |coh| <= 36;
per stage and window, pulse-count-weighted mean over (coh, sign) of P(choice = sign | pulse) - P(choice = sign | control),
then pulse-count-weighted over stages; windows 0.3-1.2 s and 1.2-5 s after (pseudo-)onset). Reimplemented with weighted
counts so that a bootstrap replicate is a reweighting of trials; checked to reproduce stats_of exactly (unit weights).
Pseudo-onsets of control trials are fixed at the full-data values.

Resampling, within each mouse, 2,000 replicates, seed 0:
  trial: trials with replacement (primary; sessions are too few in 5 mice for a session bootstrap: 1-3 sessions);
  block: blocks of 50 consecutive trials within a session (keeps slow within-session drift; sensitivity check);
  hierarchical: mice with replacement, then trials within mouse (uncertainty of the 10-mouse mean as a population mean).

Outputs (dissemination/figures/qc/pulse_effect_bootstrap_<date>_*.csv):
  data: per mouse and mean, effect and 95% percentile CI per window and scheme; heterogeneity across mice (Cochran's Q
        with bootstrap SEs, I^2);
  models: for every family in the given pulse_joint_signatures windows CSVs: model - data mean per window with the data
        CI, mice whose prediction lies outside the mouse's 95% CI, and sum over mice of z^2, z = (model - data) / SE,
        SE^2 = bootstrap var * (1 + 1/30) (30 simulation reps), compared with chi-square(10).
Usage: python -m scripts.ddm.pulse_effect_bootstrap [--n_boot 2000] [--block 50]
"""

import argparse
from datetime import date

import numpy as np
import pandas as pd
from scipy import stats

from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_descriptive_package import EARLY_BINS
from scripts.ddm.pulse_joint_signatures import stats_of
from scripts.ddm.pulse_leak_urgency_signatures import observed, pseudo_onsets, with_bins
from scripts.ddm.pulse_psychometric import OUT

WINDOWS = ["0.3-1.2", "1.2-5"]
SIM_REPS = 30
MODEL_RUNS = ["pulse_joint_signatures_2026-11-08_explore_partial", "pulse_joint_signatures_2026-11-09_explore_norm",
              "pulse_joint_signatures_2026-11-09_explore_norm_lu"]


class WindowEffect:
    """Per-mouse window effects as a function of per-trial weights (vectorized)."""

    def __init__(self, obs: pd.DataFrame, onsets: dict):
        x = with_bins(obs, onsets)
        x = x[x.bin.notna()].copy()
        x["win"] = np.where(x.bin.isin(EARLY_BINS), 0, 1)
        # trial index (row in obs) of every expanded row: control trials appear once per stage
        key = obs.reset_index().set_index("row")["index"]
        self.tidx = key.loc[x.row].to_numpy()
        self.mice = sorted(obs.mouse.unique())
        x["mi"] = x.mouse.map({m: i for i, m in enumerate(self.mice)})
        pulse, ctrl = x.s != 0, x.s == 0
        # pulse cells: (mouse, stage, win, coh, s); control cells: (mouse, stage, win, coh)
        x["pcell"], x["ccell"] = -1, -1
        x.loc[pulse, "pcell"] = x[pulse].groupby(["mi", "stage", "win", "coh", "s"]).ngroup()
        x.loc[ctrl, "ccell"] = x[ctrl].groupby(["mi", "stage", "win", "coh"]).ngroup()
        self.p_rows, self.c_rows = np.flatnonzero(pulse), np.flatnonzero(ctrl)
        self.p_cell, self.c_cell = x.pcell.to_numpy()[pulse], x.ccell.to_numpy()[ctrl]
        self.p_hit = (x.choice.to_numpy() == x.s.to_numpy())[pulse].astype(float)
        self.c_right = (x.choice.to_numpy() == 1)[ctrl].astype(float)
        pc = x[pulse].groupby("pcell").first()
        self.pc_s = pc.s.to_numpy()
        # control cell matching each pulse cell
        cmap = x[ctrl].groupby(["mi", "stage", "win", "coh"]).ccell.first()
        self.pc_ccell = np.array([cmap.get((r.mi, r.stage, r.win, r.coh), -1) for r in pc.itertuples()])
        self.pc_mouse, self.pc_win = pc.mi.to_numpy(), pc.win.to_numpy()
        self.n_pc, self.n_cc = len(pc), x.ccell.max() + 1

    def __call__(self, w: np.ndarray) -> np.ndarray:
        """w: weight per obs trial (len(obs)). Returns array (n_mice, 2): effect (pp) per mouse and window."""
        wp, wc = w[self.tidx[self.p_rows]], w[self.tidx[self.c_rows]]
        n_p = np.bincount(self.p_cell, wp, self.n_pc)
        k_p = np.bincount(self.p_cell, wp * self.p_hit, self.n_pc)
        n_c = np.bincount(self.c_cell, wc, self.n_cc)
        r_c = np.bincount(self.c_cell, wc * self.c_right, self.n_cc)
        ok = (self.pc_ccell >= 0) & (n_p > 0)
        ok[ok] &= n_c[self.pc_ccell[ok]] > 0
        cc = self.pc_ccell[ok]
        pr = r_c[cc] / n_c[cc]
        d = 100 * (k_p[ok] / n_p[ok] - np.where(self.pc_s[ok] == 1, pr, 1 - pr))
        g = self.pc_mouse[ok] * 2 + self.pc_win[ok]
        num = np.bincount(g, n_p[ok] * d, 2 * len(self.mice))
        den = np.bincount(g, n_p[ok], 2 * len(self.mice))
        with np.errstate(invalid="ignore"):
            return (num / den).reshape(len(self.mice), 2)


def boot_weights(obs: pd.DataFrame, scheme: str, rng, block: int, mouse_draw: np.ndarray | None = None) -> np.ndarray:
    w = np.zeros(len(obs))
    for m, idx in obs.groupby("mouse").indices.items():
        if scheme == "trial":
            w[idx] = rng.multinomial(len(idx), np.full(len(idx), 1 / len(idx)))
        else:
            blocks = obs.iloc[idx].groupby(["sess", "blk"]).indices
            keys = list(blocks)
            draw = rng.integers(0, len(keys), len(keys))
            for b in draw:
                w[idx[blocks[keys[b]]]] += 1
    return w


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n_boot", type=int, default=2000)
    ap.add_argument("--block", type=int, default=50)
    args = ap.parse_args()
    inputs = responded_only(load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz"))
    mice = sorted(set(inputs["subject_id"]))
    obs = observed(inputs, mice)
    onsets = pseudo_onsets(obs)
    obs["sess"] = inputs["idx_session"][obs.row]
    obs["blk"] = obs.groupby("sess").cumcount() // args.block  # rows are chronological within a session (checked)

    W = WindowEffect(obs, onsets)
    est = W(np.ones(len(obs)))
    ref = stats_of(obs, onsets)[0][WINDOWS].loc[W.mice].to_numpy()
    assert np.allclose(est, ref, atol=1e-9), np.abs(est - ref).max()
    print(f"weighted-count statistic reproduces stats_of (max |diff| {np.abs(est - ref).max():.1e})")

    rng = np.random.default_rng(0)
    boots = {}
    for scheme in ("trial", "block"):
        boots[scheme] = np.stack([W(boot_weights(obs, scheme, rng, args.block)) for _ in range(args.n_boot)])
        print(f"{scheme} bootstrap done", flush=True)
    # hierarchical: resample mice, then trials within each drawn mouse (reuse trial replicates of independent draws)
    tb = boots["trial"]
    n = len(W.mice)
    hier = np.array([np.nanmean(tb[rng.integers(0, args.n_boot, n), rng.integers(0, n, n), :], axis=0) for _ in range(args.n_boot)])

    # data table
    rows = []
    for j, w in enumerate(WINDOWS):
        for i, m in enumerate(W.mice + ["mean over mice"]):
            r = {"window": w, "mouse": m, "effect": est[:, j].mean() if i == len(W.mice) else est[i, j]}
            for scheme, b in boots.items():
                v = b[:, :, j].mean(axis=1) if i == len(W.mice) else b[:, i, j]
                r[f"se_{scheme}"] = np.nanstd(v, ddof=1)
                r[f"lo_{scheme}"], r[f"hi_{scheme}"] = np.nanpercentile(v, [2.5, 97.5])
            if i == len(W.mice):
                r["se_hier"] = np.std(hier[:, j], ddof=1)
                r["lo_hier"], r["hi_hier"] = np.percentile(hier[:, j], [2.5, 97.5])
            rows.append(r)
    data = pd.DataFrame(rows)
    het = []
    for j, w in enumerate(WINDOWS):
        se = boots["trial"][:, :, j].std(axis=0, ddof=1)
        e = est[:, j]
        wts = 1 / se ** 2
        mu = np.sum(wts * e) / wts.sum()
        Q = float(np.sum(wts * (e - mu) ** 2))
        df = len(e) - 1
        het.append({"window": w, "Q": Q, "df": df, "p": stats.chi2.sf(Q, df), "I2": max(0.0, (Q - df) / Q),
                    "sd_across_mice": e.std(ddof=1), "median_within_mouse_se": np.median(se)})
    het = pd.DataFrame(het)

    # models
    win = pd.concat([pd.read_csv(OUT / f"{run}_windows.csv") for run in MODEL_RUNS])
    win = win[win.model != "data"].drop_duplicates(["model", "mouse"])
    se_m = {w: boots["trial"][:, :, j].std(axis=0, ddof=1) for j, w in enumerate(WINDOWS)}
    lo_m = {w: np.nanpercentile(boots["trial"][:, :, j], 2.5, axis=0) for j, w in enumerate(WINDOWS)}
    hi_m = {w: np.nanpercentile(boots["trial"][:, :, j], 97.5, axis=0) for j, w in enumerate(WINDOWS)}
    mean_lo = {w: data[(data.window == w) & (data.mouse == "mean over mice")].iloc[0] for w in WINDOWS}
    out = []
    for fam, g in win.groupby("model", sort=False):
        g = g.set_index("mouse").reindex(W.mice)
        r = {"model": fam}
        for j, w in enumerate(WINDOWS):
            pred = g[w].to_numpy()
            r[f"mean_{w}"] = np.nanmean(pred)
            r[f"diff_{w}"] = np.nanmean(pred) - est[:, j].mean()
            d = mean_lo[w]
            r[f"outside_mean_CI_{w}"] = not (d.lo_trial <= np.nanmean(pred) <= d.hi_trial)
            r[f"mice_outside_CI_{w}"] = int(np.sum((pred < lo_m[w]) | (pred > hi_m[w])))
            z = (pred - est[:, j]) / (se_m[w] * np.sqrt(1 + 1 / SIM_REPS))
            r[f"chi2_{w}"] = float(np.nansum(z ** 2))
            r[f"chi2_p_{w}"] = stats.chi2.sf(r[f"chi2_{w}"], np.sum(~np.isnan(z)))
        out.append(r)
    models = pd.DataFrame(out)

    pd.set_option("display.width", 250)
    print("\n== data: effect (pp) with 95% CI per window; trial and 50-trial-block bootstrap within mouse; mean also hierarchical\n"
          + data.round(2).to_string(index=False))
    print("\n== heterogeneity across mice (Cochran's Q with trial-bootstrap SEs)\n" + het.round(3).to_string(index=False))
    print("\n== models vs data (trial bootstrap; chi2 = sum over mice of z^2, df = 10)\n" + models.round(3).to_string(index=False))
    stem = OUT / f"pulse_effect_bootstrap_{date.today().isoformat()}"
    data.to_csv(f"{stem}_data.csv", index=False)
    het.to_csv(f"{stem}_heterogeneity.csv", index=False)
    models.to_csv(f"{stem}_models.csv", index=False)
    print(stem)


if __name__ == "__main__":
    main()
