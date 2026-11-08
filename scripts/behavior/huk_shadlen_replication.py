"""Behavioural pulse analyses of Huk & Shadlen 2005 (J Neurosci 25:10420) on the mouse data
(plan .agents/plans/2026-10-29-huk-shadlen-replication.md).

1. Joint psychometric + chronometric fit (their Eqs 6-7, Table 2) with the proportional-rate diffusion of Palmer et al.
   2005: P(right) = 1 / (1 + exp(-2 k A C1)), mean RT = A / (k C2) tanh(k A C2) + t_nd, C1 = C + b + gamma * pulse,
   C2 = C + b + (gamma + delta) * pulse; C in fraction coherence, time in ms. Their fit has no bias b ("huk"); "bias"
   adds it. Binomial choices, normal mean RT (correct + error) with measured SE.
2. Relative-RT time course (their Eq 8, Fig 4): bins of RT - pulse onset; logit P(right) = b0 + b1 C + b2 I_pos + b3 I_neg,
   effects b2/b1 and b3/b1 in % coherence; no-pulse trials take the matched virtual onset (control_onset_s).
3. KS tests of standardized RT distributions.

Responded trials (choice by 5 s), symmetric cells; responses before the end of the (virtual) pulse removed.

    python -m scripts.behavior.huk_shadlen_replication [--date YYYY-MM-DD]
"""

import argparse
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.optimize import minimize
from scipy.stats import chi2, ks_2samp, norm, wilcoxon
from statsmodels.stats.multitest import multipletests
from statsmodels.tools.numdiff import approx_hess3

from config import dir_config

PROCESSED = Path(dir_config.data.processed)
TRIAL_TABLE = PROCESSED / "pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv"
OUT = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation"
FINE_BIN_S, FINE_MAX_S = 0.075, 2.1
COARSE_BINS_S = [0.0, 0.3, 0.6, 0.9, 1.2, 1.8, 5.0]
MOUSE_BIN_S, MOUSE_MIN_PULSE = 0.15, 8
# Time-course fits: mice lapse at 100%, which a term linear in coherence cannot follow, and only incongruent pulses occur
# at 100%, so a linear fit loads that misfit on the incongruent term (it reversed the congruency result). Pulse effects
# therefore come from a fit with categorical coherence (all coherences, author 2026-10-30); the slope b1 that converts
# them to % coherence comes from a linear fit to |C| <= 36% (the paper's range ends at 51.2%).
MAX_ABS_COH_SLOPE = 36
MIN_CELL_TRIALS = 5

warnings.filterwarnings("ignore")


def load() -> pd.DataFrame:
    t = pd.read_csv(TRIAL_TABLE, low_memory=False)
    t = t[t.in_ddm_input.astype(bool) & (t.response_side != "none") & t.signs_scheduled_symmetric.astype(bool)
          & t.pulse_category.isin(["control", "positive", "negative"])].copy()
    n_late = int((t.onset_stratum == "late").sum())
    t = t[t.onset_stratum != "late"].copy()  # author 2026-10-30: no late pulses (and no controls with late virtual onsets)
    print(f"{n_late} late-stratum trials dropped (pulse and matched control)")
    pulse = t.pulse_category != "control"
    dur = (t.recorded_offset_s - t.recorded_onset_s).where(pulse)
    t["onset_s"] = np.where(pulse, t.recorded_onset_s, t.control_onset_s)
    t["offset_s"] = t.onset_s + np.where(pulse, dur, t.rig.map(dur.groupby(t.rig).median()))  # virtual pulse: rig median duration
    n0 = len(t)
    t = t[t.rt_s >= t.offset_s].copy()
    t["coh"] = t.coherence_pct / 100
    t["pulse"] = np.where(pulse.loc[t.index], t.pulse_sign, 0)
    t["i_pos"], t["i_neg"] = (t.pulse > 0).astype(float), (t.pulse < 0).astype(float)
    # congruency regressors, signed by the coherence direction: positive coefficient = choices move toward the correct
    # side, so congruent pulses should be > 0 and incongruent < 0 (author 2026-10-30); 0% has none
    t["i_cong"] = t.pulse * (np.sign(t.coherence_pct) == t.pulse)
    t["i_incong"] = -t.pulse * (np.sign(t.coherence_pct) == -t.pulse)
    t["right"] = (t.response_side == "R").astype(float)
    t["rt_ms"] = 1000 * t.rt_s
    t["rel_rt_s"] = t.rt_s - t.onset_s
    print(f"{n0} responded control/pulse trials in symmetric cells; {n0 - len(t)} responded before the (virtual) pulse ended; {len(t)} kept")
    return t


# 1. Joint choice + mean RT fit --------------------------------------------------------------------------------------
def cells(t: pd.DataFrame) -> pd.DataFrame:
    g = t.groupby(["coh", "pulse"])
    c = pd.DataFrame({"n": g.size(), "k_right": g.right.sum(), "rt_mean": g.rt_ms.mean(), "rt_se": g.rt_ms.sem()}).reset_index()
    return c[c.n >= MIN_CELL_TRIALS]


def predict(p, C, pulse, bias: bool, delta: bool):
    k, A, tnd, gamma = p[:4]
    k, A, tnd = abs(k), abs(A), abs(tnd)  # t_nd >= 0 as in the paper; mouse chronometric curves are flat
    b = p[4] if bias else 0.0
    d = p[-1] if delta else 0.0
    c1, c2 = C + b + gamma * pulse, C + b + (gamma + d) * pulse
    pr = 1 / (1 + np.exp(-2 * k * A * c1))
    x = k * A * c2
    td = np.where(np.abs(x) < 1e-6, A**2, A / (k * np.where(c2 == 0, 1e-12, c2)) * np.tanh(x))
    return pr, td + tnd


def nll(p, c, bias, delta):
    pr, rt = predict(p, c.coh.to_numpy(), c.pulse.to_numpy(), bias, delta)
    pr = np.clip(pr, 1e-9, 1 - 1e-9)
    ll_choice = c.k_right * np.log(pr) + (c.n - c.k_right) * np.log(1 - pr)
    ll_rt = -0.5 * ((c.rt_mean - rt) / c.rt_se) ** 2 - np.log(c.rt_se)
    return -(ll_choice.sum() + ll_rt.sum())


SCALE = np.array([0.01, 10.0, 100.0, 0.01, 0.01, 0.01])  # k, A, t_nd, gamma, bias, delta: optimise in O(1) units


def fit_joint(c: pd.DataFrame, bias: bool, delta: bool, start: dict | None = None) -> dict:
    names = ["k", "A", "t_nd_ms", "gamma"] + (["bias"] if bias else []) + (["delta"] if delta else [])
    sc = SCALE[[0, 1, 2, 3] + ([4] if bias else []) + ([5] if delta else [])]
    f = lambda z: nll(z * sc, c, bias, delta)  # noqa: E731
    starts = [[k0, a0, t0, 0.05] + [0.0] * (len(names) - 4) for k0, a0, t0 in [(0.03, 35.0, 300.0), (0.02, 45.0, 100.0), (0.05, 25.0, 600.0), (0.1, 20.0, 800.0)]]
    if start is not None:  # nested model: begin at the smaller model's optimum with the new terms at 0
        starts.insert(0, [start.get(n, 0.0) for n in names])
    best = None
    for z0 in starts:
        r = minimize(f, np.array(z0) / sc, method="Nelder-Mead", options={"maxiter": 20000, "maxfev": 20000, "xatol": 1e-6, "fatol": 1e-8})
        r = minimize(f, r.x, method="Powell", options={"maxiter": 20000, "xtol": 1e-6, "ftol": 1e-10})
        if best is None or r.fun < best.fun:
            best = r
    try:
        cov = np.linalg.inv(approx_hess3(best.x, f)) * np.outer(sc, sc)
        se = np.sqrt(np.diag(cov))
    except Exception:
        se = np.full(len(names), np.nan)
    x = best.x * sc
    x[:3] = np.abs(x[:3])
    out = {n: v for n, v in zip(names, x)} | {f"{n}_se": v for n, v in zip(names, se)}
    return out | {"nll": best.fun, "converged": bool(best.success and x[0] > 0 and x[1] > 0)}


def joint_fits(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m, g in [("pooled", t)] + list(t.groupby("mouse")):
        c = cells(g)
        huk = fit_joint(c, False, False)
        for model, bias in [("huk", False), ("bias", True)]:
            f0 = huk if not bias else fit_joint(c, True, False, start=huk)
            f1 = fit_joint(c, bias, True, start=f0)
            lr = max(0.0, 2 * (f0["nll"] - f1["nll"]))
            rows.append({"mouse": m, "model": model, "n_trials": int(c.n.sum()), **f0, "delta": f1["delta"], "delta_se": f1["delta_se"],
                         "lr_delta": lr, "p_delta": chi2.sf(lr, 1)})
    r = pd.DataFrame(rows)
    for col in ["gamma", "gamma_se", "delta", "delta_se", "bias", "bias_se"]:
        if col in r:
            r[col + "_pct"] = 100 * r[col]
    return r


# 2. Relative-RT time course -------------------------------------------------------------------------------------------
def bin_fit(d: pd.DataFrame, mouse_intercepts: bool, terms=("i_pos", "i_neg"), labels=("pos", "neg")) -> dict:
    """Pulse terms from logit P(right) ~ C(coherence) + terms (+ mouse intercepts); b1 per % coherence from a linear fit
    to |C| <= MAX_ABS_COH_SLOPE in the same trials (see MAX_ABS_COH_SLOPE)."""
    mi = " + C(mouse)" if mouse_intercepts and d.mouse.nunique() > 1 else ""
    r = smf.logit("right ~ C(coherence_pct) + " + " + ".join(terms) + mi, d).fit(disp=0)
    lin = smf.logit("right ~ coh" + mi, d[d.coherence_pct.abs() <= MAX_ABS_COH_SLOPE]).fit(disp=0)
    out = {"n": len(d), "b1_per_pct": lin.params["coh"] / 100}
    for term, lab in zip(terms, labels):
        out |= {f"n_{lab}": int((d[term] != 0).sum()), f"b_{lab}": r.params[term], f"se_{lab}": r.bse[term]}
    return out


def time_course(t: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    edges = np.arange(0, FINE_MAX_S + 1e-9, FINE_BIN_S)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        d = t[(t.rel_rt_s >= lo) & (t.rel_rt_s < hi)]
        if d.i_pos.sum() >= 20 and d.i_neg.sum() >= 20:
            try:
                rows.append({"lo_s": lo, "hi_s": hi, **bin_fit(d, True)})
            except Exception:
                pass
    fine = pd.DataFrame(rows)
    # Deviation from the paper (per-bin b1): b1 is near 0 for responses < 0.4 s after the pulse, so per-bin ratios blow
    # up; one b1 from all trials (mouse intercepts) converts points and SEs. Per-bin ratios kept in *_pct_bin_b1.
    b1 = bin_fit(t, True)["b1_per_pct"]
    fine["pos_pct_bin_b1"], fine["neg_pct_bin_b1"] = fine.b_pos / fine.b1_per_pct, fine.b_neg / fine.b1_per_pct
    fine["pos_pct"], fine["neg_pct"] = fine.b_pos / b1, fine.b_neg / b1
    fine["pos_pct_se"], fine["neg_pct_se"] = fine.se_pos / b1, fine.se_neg / b1
    rows = []
    for m, g in t.groupby("mouse"):
        for lo, hi in zip(COARSE_BINS_S[:-1], COARSE_BINS_S[1:]):
            d = g[(g.rel_rt_s >= lo) & (g.rel_rt_s < hi)]
            try:
                f = bin_fit(d, False)
                rows.append({"mouse": m, "lo_s": lo, "hi_s": hi, **f, "pos_minus_neg_logit": f["b_pos"] - f["b_neg"]})
            except Exception:
                rows.append({"mouse": m, "lo_s": lo, "hi_s": hi, "n": len(d)})
    coarse = pd.DataFrame(rows)
    return fine, coarse


def mouse_time_course(t: pd.DataFrame) -> pd.DataFrame:
    """Fig 4 per mouse with 150 ms bins (75 ms bins hold too few trials per mouse). Effects in % coherence are b2/b1 as
    in the paper, but with b1 from the mouse's fit to all its trials: per-bin b1 is unstable at these counts."""
    edges = np.arange(0, FINE_MAX_S + 1e-9, MOUSE_BIN_S)
    rows = []
    for m, g in t.groupby("mouse"):
        b1 = bin_fit(g, False)["b1_per_pct"]
        for lo, hi in zip(edges[:-1], edges[1:]):
            d = g[(g.rel_rt_s >= lo) & (g.rel_rt_s < hi)]
            if d.i_pos.sum() < MOUSE_MIN_PULSE or d.i_neg.sum() < MOUSE_MIN_PULSE:
                continue
            try:
                f = bin_fit(d, False)
            except Exception:  # separation
                continue
            rows.append({"mouse": m, "lo_s": lo, "hi_s": hi, **f, "b1_mouse_per_pct": b1, "pos_pct": f["b_pos"] / b1, "neg_pct": f["b_neg"] / b1,
                         "pos_pct_se": f["se_pos"] / b1, "neg_pct_se": f["se_neg"] / b1, "pos_pct_bin_b1": f["b_pos"] / f["b1_per_pct"],
                         "neg_pct_bin_b1": f["b_neg"] / f["b1_per_pct"]})
    return pd.DataFrame(rows)


CONG_BLOCK_S = 0.1  # author: block the first 100 ms after pulse onset (Huk Fig 4 shows no effect there)
CONG = dict(terms=("i_cong", "i_incong"), labels=("cong", "incong"))


def congruency_time_course(t: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Huk Fig 4 with congruent / incongruent pulses: effect toward the correct side, % coherence. Pulse trials at 0% coherence
    (neither congruent nor incongruent) dropped; responses < 100 ms after onset blocked. Pooled: 75 ms bins, mouse
    intercepts, one b1 for all bins; per mouse: 150 ms bins, b1 from the mouse's fit to all its trials."""
    u = t[~((t.coherence_pct == 0) & (t.pulse != 0)) & (t.rel_rt_s >= CONG_BLOCK_S)]
    rows = []
    for lo in np.arange(CONG_BLOCK_S, FINE_MAX_S - 1e-9, FINE_BIN_S):
        d = u[(u.rel_rt_s >= lo) & (u.rel_rt_s < lo + FINE_BIN_S)]
        if (d.i_cong != 0).sum() >= 20 and (d.i_incong != 0).sum() >= 20:
            try:
                rows.append({"lo_s": lo, "hi_s": lo + FINE_BIN_S, **bin_fit(d, True, **CONG)})
            except Exception:
                pass
    pooled = pd.DataFrame(rows)
    b1 = bin_fit(u, True)["b1_per_pct"]  # one b1 for all bins, as in time_course
    for lab in CONG["labels"]:
        pooled[f"{lab}_pct"], pooled[f"{lab}_pct_se"] = pooled[f"b_{lab}"] / b1, pooled[f"se_{lab}"] / b1
    rows = []
    for m, g in u.groupby("mouse"):
        b1m = bin_fit(g, False)["b1_per_pct"]
        for lo in np.arange(CONG_BLOCK_S, FINE_MAX_S - 1e-9, MOUSE_BIN_S):
            d = g[(g.rel_rt_s >= lo) & (g.rel_rt_s < lo + MOUSE_BIN_S)]
            if (d.i_cong != 0).sum() < MOUSE_MIN_PULSE or (d.i_incong != 0).sum() < MOUSE_MIN_PULSE:
                continue
            try:
                f = bin_fit(d, False, **CONG)
            except Exception:
                continue
            rows.append({"mouse": m, "lo_s": lo, "hi_s": lo + MOUSE_BIN_S, **f, "b1_mouse_per_pct": b1m,
                         **{f"{lab}_pct": f[f"b_{lab}"] / b1m for lab in CONG["labels"]}, **{f"{lab}_pct_se": f[f"se_{lab}"] / b1m for lab in CONG["labels"]}})
    return pooled, pd.DataFrame(rows)


def figure_congruency(pooled, per_mouse, date):
    mice = sorted(per_mouse.mouse.unique())
    fig, ax = plt.subplots(4, 3, figsize=(16, 15))
    ax = ax.ravel()
    style = [("cong", "tab:blue", "congruent"), ("incong", "tab:red", "incongruent")]
    for k, (lab, col, name) in enumerate(style):
        ax[0].errorbar(pooled.lo_s * 1000 + FINE_BIN_S * 500 + (k - 0.5) * 8, pooled[f"{lab}_pct"], pooled[f"{lab}_pct_se"], fmt="o-", color=col, label=name, ms=4)
    ax[0].set_title("pooled, 75 ms bins (mouse intercepts, one b1)", fontsize=10), ax[0].legend(fontsize=8), ax[0].set_ylim(-40, 80)
    for i, m in enumerate(mice):
        q = per_mouse[per_mouse.mouse == m]
        for k, (lab, col, _) in enumerate(style):
            ax[i + 1].errorbar(q.lo_s * 1000 + MOUSE_BIN_S * 500 + (k - 0.5) * 15, q[f"{lab}_pct"], q[f"{lab}_pct_se"], fmt="o-", color=col, ms=4)
        ax[i + 1].set_title(f"{m}, 150 ms bins", fontsize=10), ax[i + 1].set_ylim(-100, 150)
    for a in ax[: len(mice) + 1]:
        a.axhline(0, color="k", lw=0.5), a.axvspan(0, CONG_BLOCK_S * 1000, color="#ddd"), a.set_xlim(0, FINE_MAX_S * 1000)
        a.set_xlabel("RT - pulse onset (ms)"), a.set_ylabel("effect toward correct side (% coh)")
    for a in ax[len(mice) + 1 :]:
        a.axis("off")
    fig.suptitle("Huk & Shadlen Fig 4 by congruency; first 100 ms after pulse onset blocked (grey); 0% pulse trials excluded")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_congruency.png", dpi=110), plt.close(fig)


OVERLAY_BINS_S = [0.1, 0.3, 0.6, 0.9, 1.2, 1.5, 2.1]
OVERLAY_MIN_PULSE = 20  # per mouse, bin and pulse type; at 8, single bins of ~10 trials dominated the mean


def mouse_overlay(t: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-mouse effects in shared coarse bins (first 100 ms blocked), % coherence with the mouse's overall b1, for the
    direction set (right / left pulse) and the congruency set (toward the correct side); mean +- SEM over mice and Wilcoxon
    per bin and curve (Holm within each set)."""
    sets = {"direction": dict(terms=("i_pos", "i_neg"), labels=("pos", "neg")), "congruency": CONG}
    rows = []
    for m, g in t.groupby("mouse"):
        b1m = bin_fit(g, False)["b1_per_pct"]
        for name, spec in sets.items():
            u = g[~((g.coherence_pct == 0) & (g.pulse != 0))] if name == "congruency" else g
            for lo, hi in zip(OVERLAY_BINS_S[:-1], OVERLAY_BINS_S[1:]):
                d = u[(u.rel_rt_s >= lo) & (u.rel_rt_s < hi)]
                if min((d[x] != 0).sum() for x in spec["terms"]) < OVERLAY_MIN_PULSE:
                    continue
                try:
                    f = bin_fit(d, False, **spec)
                except Exception:
                    continue
                for lab in spec["labels"]:
                    if abs(f[f"b_{lab}"]) < 10:  # drop separated fits
                        rows.append({"set": name, "mouse": m, "lo_s": lo, "hi_s": hi, "curve": lab, "logit": f[f"b_{lab}"], "pct": f[f"b_{lab}"] / b1m,
                                     "n_pulse": f[f"n_{lab}"]})
    per = pd.DataFrame(rows)
    summ = []
    for (name, lo, hi, curve), g in per.groupby(["set", "lo_s", "hi_s", "curve"]):
        summ.append({"set": name, "lo_s": lo, "hi_s": hi, "curve": curve, "n_mice": len(g), "mean_pct": g.pct.mean(), "sem_pct": g.pct.sem(),
                     "median_pct": g.pct.median(), "n_toward_expected": int((np.sign(g.logit) == (-1 if curve in ("neg", "incong") else 1)).sum()),
                     "wilcoxon_p": wilcoxon(g.logit).pvalue if len(g) >= 5 else np.nan})
    summ = pd.DataFrame(summ)
    for name in sets:
        ok = (summ.set == name) & summ.wilcoxon_p.notna()
        summ.loc[ok, "holm_p"] = multipletests(summ.loc[ok, "wilcoxon_p"], method="holm")[1]
    return per, summ


def pooled_coarse(t: pd.DataFrame) -> pd.DataFrame:
    """Pooled (mouse intercepts) effects in the overlay bins, both sets, one b1 per set (as the pooled 75 ms bins)."""
    sets = {"direction": dict(terms=("i_pos", "i_neg"), labels=("pos", "neg")), "congruency": CONG}
    rows = []
    for name, spec in sets.items():
        u = t[~((t.coherence_pct == 0) & (t.pulse != 0))] if name == "congruency" else t
        b1 = bin_fit(u, True)["b1_per_pct"]
        for lo, hi in zip(OVERLAY_BINS_S[:-1], OVERLAY_BINS_S[1:]):
            f = bin_fit(u[(u.rel_rt_s >= lo) & (u.rel_rt_s < hi)], True, **spec)
            for lab in spec["labels"]:
                rows.append({"set": name, "lo_s": lo, "hi_s": hi, "curve": lab, "n_pulse": f[f"n_{lab}"], "logit": f[f"b_{lab}"], "se_logit": f[f"se_{lab}"],
                             "pct": f[f"b_{lab}"] / b1, "pct_se": f[f"se_{lab}"] / b1, "z_p": 2 * norm.sf(abs(f[f"b_{lab}"] / f[f"se_{lab}"]))})
    return pd.DataFrame(rows)


def mouse_congruency_coarse(t: pd.DataFrame) -> pd.DataFrame:
    """Per mouse, congruent and incongruent effects (logit toward the correct side) in COARSE_BINS_S with the first 100 ms
    blocked; no trial minimum (panel 4, as the per-mouse direction panel of the main figure)."""
    u = t[~((t.coherence_pct == 0) & (t.pulse != 0)) & (t.rel_rt_s >= CONG_BLOCK_S)]
    edges = [CONG_BLOCK_S] + COARSE_BINS_S[1:]
    rows = []
    for m, g in u.groupby("mouse"):
        for lo, hi in zip(edges[:-1], edges[1:]):
            try:
                f = bin_fit(g[(g.rel_rt_s >= lo) & (g.rel_rt_s < hi)], False, **CONG)
            except Exception:
                continue
            rows.append({"mouse": m, "lo_s": lo, "hi_s": hi, "cong_logit": f["b_cong"], "incong_logit": f["b_incong"], "n_cong": f["n_cong"], "n_incong": f["n_incong"]})
    return pd.DataFrame(rows)


def figure_pooled_congruency(t, jf, cong_pooled, mcc, date):
    """Main pooled figure by congruency: accuracy and mean RT vs |C| (data; curves from the pooled direction fit with
    bias, averaged over right and left pulses), the 75 ms time course, and per-mouse coarse bins."""
    fig, ax = plt.subplots(1, 4, figsize=(22, 5))
    u = t[t.coherence_pct != 0].assign(abs_coh=lambda d: d.coherence_pct.abs(), correct=lambda d: (d.right == (d.coherence_pct > 0)).astype(float),
                                      cat=lambda d: np.where(d.pulse == 0, "none", np.where(np.sign(d.coherence_pct) == d.pulse, "cong", "incong")))
    p = jf[(jf.mouse == "pooled") & (jf.model == "bias")].iloc[0]
    params = [p.k, p.A, p.t_nd_ms, p.gamma, p.bias]
    cc = np.linspace(0.01, 1, 100)
    style = [("none", "k", "no pulse"), ("cong", "tab:blue", "congruent"), ("incong", "tab:red", "incongruent")]
    for cat, col, lab in style:
        g = u[u.cat == cat].groupby("abs_coh")
        acc = g.correct.agg(["mean", "size"])
        ax[0].errorbar(acc.index, acc["mean"], np.sqrt(acc["mean"] * (1 - acc["mean"]) / acc["size"]), fmt="o", color=col, label=lab)
        rt = g.rt_ms.agg(["mean", "sem"])
        ax[1].errorbar(rt.index, rt["mean"], rt["sem"], fmt="o", color=col)
        s_pulse = {"none": 0, "cong": 1, "incong": -1}[cat]  # pulse sign relative to the coherence sign
        pc_r, rt_r = predict(params, cc, np.full_like(cc, s_pulse), True, False)  # rightward coherence
        pr_l, rt_l = predict(params, -cc, np.full_like(cc, -s_pulse), True, False)  # leftward coherence
        ax[0].plot(100 * cc, (pc_r + (1 - pr_l)) / 2, color=col), ax[1].plot(100 * cc, (rt_r + rt_l) / 2, color=col)
    ax[0].set_xlabel("|coherence| (%)"), ax[0].set_ylabel("P(correct)"), ax[0].legend(fontsize=8)
    ax[0].set_title(f"pooled; curves: direction fit with bias (gamma {100 * p.gamma:.1f}% coh)", fontsize=10)
    ax[1].set_xlabel("|coherence| (%)"), ax[1].set_ylabel("mean RT (ms)"), ax[1].set_title("chronometric (correct + error)", fontsize=10)
    for k, (lab, col, name) in enumerate(style[1:]):
        ax[2].errorbar(1000 * (cong_pooled.lo_s + FINE_BIN_S / 2) + (k - 0.5) * 8, cong_pooled[f"{lab}_pct"], cong_pooled[f"{lab}_pct_se"], fmt="o-", color=col,
                       label=name, ms=4)
    ax[2].axhline(0, color="k", lw=0.5), ax[2].axvspan(0, CONG_BLOCK_S * 1000, color="#ddd"), ax[2].set_xlim(0, FINE_MAX_S * 1000), ax[2].set_ylim(-60, 60)
    ax[2].set_xlabel("RT - pulse onset (ms)"), ax[2].set_ylabel("effect toward correct side (% coherence)"), ax[2].legend(fontsize=8)
    ax[2].set_title("Huk & Shadlen Fig 4 by congruency: 75 ms bins, pooled", fontsize=10)
    x = 1000 * (mcc.lo_s + mcc.hi_s) / 2
    mcc = mcc.assign(x=x)
    for k, (lab, col, name) in enumerate(style[1:]):
        piv = mcc.pivot(index="x", columns="mouse", values=f"{lab}_logit").clip(-3, 3)
        ax[3].plot(piv.index, piv.to_numpy(), color=col, alpha=0.25), ax[3].plot(piv.index, piv.median(axis=1), "o-", color=col, lw=2.5, label=f"{name} (median)")
    ax[3].axhline(0, color="k", lw=0.5), ax[3].axvspan(0, CONG_BLOCK_S * 1000, color="#ddd"), ax[3].set_xlabel("RT - pulse onset (ms)")
    ax[3].set_ylabel("effect toward correct side (logit)"), ax[3].legend(fontsize=8), ax[3].set_title("per mouse (thin, clipped at +-3), median (bold)", fontsize=10)
    fig.suptitle("Congruent vs incongruent, pooled; all coherences, no late pulses; 0% excluded from congruency; first 100 ms after pulse onset blocked")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_pooled_congruency.png", dpi=130), plt.close(fig)


def congruency_cells(g: pd.DataFrame) -> pd.DataFrame:
    """P(correct) and mean RT by |C| and pulse category (no pulse / congruent / incongruent), |C| > 0."""
    u = g[g.coherence_pct != 0].assign(abs_coh=lambda d: d.coherence_pct.abs(), correct=lambda d: (d.right == (d.coherence_pct > 0)).astype(float),
                                      cat=lambda d: np.where(d.pulse == 0, "none", np.where(np.sign(d.coherence_pct) == d.pulse, "cong", "incong")))
    return u.groupby(["cat", "abs_coh"]).agg(p_correct=("correct", "mean"), n=("correct", "size"), rt_mean=("rt_ms", "mean"), rt_se=("rt_ms", "sem")).reset_index()


def congruency_curves(params, cat: str):
    """Model P(correct) and mean RT vs |C| for a category, averaged over rightward and leftward coherence."""
    cc = np.linspace(0.01, 1, 100)
    sp = {"none": 0, "cong": 1, "incong": -1}[cat]
    pr_r, rt_r = predict(params, cc, np.full_like(cc, sp), True, False)
    pr_l, rt_l = predict(params, -cc, np.full_like(cc, -sp), True, False)
    return 100 * cc, (pr_r + 1 - pr_l) / 2, (rt_r + rt_l) / 2


def figure_per_mouse_congruency(t, jf, cong_mouse, date):
    mice = sorted(t.mouse.unique())
    style = [("none", "k", "no pulse"), ("cong", "tab:blue", "congruent"), ("incong", "tab:red", "incongruent")]
    fig, ax = plt.subplots(len(mice), 3, figsize=(16, 3.2 * len(mice)))
    for i, m in enumerate(mice):
        c = congruency_cells(t[t.mouse == m])
        p = jf[(jf.mouse == m) & (jf.model == "bias")].iloc[0]
        params = [p.k, p.A, p.t_nd_ms, p.gamma, p.bias]
        for cat, col, lab in style:
            d = c[(c.cat == cat) & (c.n >= MIN_CELL_TRIALS)]
            ax[i, 0].errorbar(d.abs_coh, d.p_correct, np.sqrt(d.p_correct * (1 - d.p_correct) / d.n), fmt="o", color=col, label=lab, ms=4)
            ax[i, 1].errorbar(d.abs_coh, d.rt_mean, d.rt_se, fmt="o", color=col, ms=4)
            x, pc, rt = congruency_curves(params, cat)
            ax[i, 0].plot(x, pc, color=col), ax[i, 1].plot(x, rt, color=col)
        ax[i, 0].set_ylim(0.3, 1), ax[i, 0].set_ylabel(f"{m}\nP(correct)")
        ax[i, 0].set_title(f"{m}: curves from direction fit with bias, gamma {100 * p.gamma:.1f}% coh", fontsize=9)
        ax[i, 1].set_ylabel("mean RT (ms)"), ax[i, 1].set_title("correct + error", fontsize=9)
        q = cong_mouse[cong_mouse.mouse == m]
        mid = 1000 * (q.lo_s + MOUSE_BIN_S / 2)
        for k, (lab, col, _) in enumerate(style[1:]):
            ax[i, 2].errorbar(mid + (k - 0.5) * 15, q[f"{lab}_pct"], q[f"{lab}_pct_se"], fmt="o-", color=col, ms=4)
        ax[i, 2].axhline(0, color="k", lw=0.5), ax[i, 2].axvspan(0, CONG_BLOCK_S * 1000, color="#ddd")
        ax[i, 2].set_xlim(0, FINE_MAX_S * 1000), ax[i, 2].set_ylim(-100, 100)
        ax[i, 2].set_ylabel("toward correct side (% coh)"), ax[i, 2].set_title(f"150 ms bins (>= {MOUSE_MIN_PULSE} trials per type; b1 per mouse)", fontsize=9)
    ax[0, 0].legend(fontsize=7)
    for j, lab in enumerate(["|coherence| (%)", "|coherence| (%)", "RT - pulse onset (ms)"]):
        ax[-1, j].set_xlabel(lab)
    fig.suptitle("Per mouse by congruency; all coherences, no late pulses; congruent > 0 helps, incongruent < 0 hurts", y=1.0)
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_per_mouse_congruency.png", dpi=110), plt.close(fig)


def figure_overlay(per, summ, date):
    fig, ax = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    styles = {"direction": [("pos", "tab:orange", "right pulse"), ("neg", "tab:purple", "left pulse")],
              "congruency": [("cong", "tab:blue", "congruent"), ("incong", "tab:red", "incongruent")]}
    for a, (name, st) in zip(ax, styles.items()):
        for k, (lab, col, title) in enumerate(st):
            q = per[(per.set == name) & (per.curve == lab)]
            for m, g in q.groupby("mouse"):
                a.plot(1000 * (g.lo_s + g.hi_s) / 2, g.pct.clip(-100, 100), color=col, alpha=0.25, lw=1)
            sm = summ[(summ.set == name) & (summ.curve == lab)]
            x = 1000 * (sm.lo_s + sm.hi_s) / 2 + (k - 0.5) * 20
            a.errorbar(x, sm.mean_pct, sm.sem_pct, fmt="o-", color=col, lw=2.5, ms=6, capsize=3, label=f"{title} (mean +- SEM over mice)")
            for xi, (_, r) in zip(x, sm.iterrows()):
                if r.holm_p < 0.05:
                    a.text(xi, r.mean_pct + r.sem_pct + 4, "*", color=col, ha="center", fontsize=14)
        a.axhline(0, color="k", lw=0.5), a.axvspan(0, 100, color="#ddd"), a.set_xlim(0, 2100), a.set_ylim(-100, 100)
        a.set_xlabel("RT - pulse onset (ms)"), a.legend(fontsize=8), a.set_title(name)
    ax[0].set_ylabel("pulse effect (% coherence; congruency: toward correct side)")
    fig.suptitle(f"Per mouse (thin, clipped at +-100; bins with >= {OVERLAY_MIN_PULSE} trials per pulse type) and mean over mice; all coherences, no late pulses; * Holm p < .05")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_mouse_overlay.png", dpi=130), plt.close(fig)


def coarse_tests(coarse: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (lo, hi), g in coarse.groupby(["lo_s", "hi_s"]):
        x = g.pos_minus_neg_logit.replace([np.inf, -np.inf], np.nan).dropna()
        x = x[x.abs() < 10]  # separation in tiny bins
        rows.append({"lo_s": lo, "hi_s": hi, "n_mice": len(x), "mean_logit": x.mean(), "median_logit": x.median(), "n_positive": int((x > 0).sum()),
                     "wilcoxon_p": wilcoxon(x).pvalue if len(x) >= 5 else np.nan})
    r = pd.DataFrame(rows)
    ok = r.wilcoxon_p.notna()
    r.loc[ok, "holm_p"] = multipletests(r.loc[ok, "wilcoxon_p"], method="holm")[1]
    return r


# 3. RT distribution shape ---------------------------------------------------------------------------------------------
def ks_tests(t: pd.DataFrame) -> pd.DataFrame:
    z = t.groupby(["mouse", "coherence_pct"]).rt_ms.transform(lambda x: (x - x.mean()) / x.std())
    groups = {"none": z[t.pulse == 0], "pos": z[t.pulse > 0], "neg": z[t.pulse < 0], "pulse": z[t.pulse != 0]}
    return pd.DataFrame([{"comparison": f"{a} vs {b}", "ks_stat": ks_2samp(groups[a], groups[b]).statistic, "p": ks_2samp(groups[a], groups[b]).pvalue}
                         for a, b in [("pulse", "none"), ("pos", "neg"), ("pos", "none"), ("neg", "none")]])


def figure(t, jf, fine, coarse, date):
    fig, ax = plt.subplots(1, 4, figsize=(22, 5))
    c = cells(t)
    p = jf[(jf.mouse == "pooled") & (jf.model == "bias")].iloc[0]
    params = [p.k, p.A, p.t_nd_ms, p.gamma, p.bias]
    cc = np.linspace(-1, 1, 201)
    for pu, col, lab in [(1, "tab:orange", "right pulse"), (0, "k", "no pulse"), (-1, "tab:purple", "left pulse")]:
        d = c[c.pulse == pu]
        ax[0].plot(100 * d.coh, d.k_right / d.n, "o", color=col, label=lab)
        ax[1].errorbar(100 * d.coh, d.rt_mean, d.rt_se, fmt="o", color=col)
        pr, rt = predict(params, cc, np.full_like(cc, pu), True, False)
        ax[0].plot(100 * cc, pr, color=col), ax[1].plot(100 * cc, rt, color=col)
    ax[0].set_xlabel("coherence (%)"), ax[0].set_ylabel("P(right)"), ax[0].legend()
    ax[0].set_title(f"pooled, fit with bias: gamma {100 * p.gamma:.1f}% coh")
    ax[1].set_xlabel("coherence (%)"), ax[1].set_ylabel("mean RT (ms)"), ax[1].set_title("chronometric (correct + error)")
    mid = (fine.lo_s + fine.hi_s) / 2 * 1000
    ax[2].errorbar(mid, fine.pos_pct, fine.pos_pct_se, fmt="o-", color="tab:orange", label="right pulse")
    ax[2].errorbar(mid, fine.neg_pct, fine.neg_pct_se, fmt="o-", color="tab:purple", label="left pulse")
    ax[2].axhline(0, color="k", lw=0.5), ax[2].set_xlabel("RT - pulse onset (ms)"), ax[2].set_ylabel("pulse effect (% coherence)")
    ax[2].set_title("Huk & Shadlen Fig 4: 75 ms bins, pooled (mouse intercepts, one b1)"), ax[2].legend(), ax[2].set_ylim(-60, 60)
    piv = coarse.pivot(index="lo_s", columns="mouse", values="pos_minus_neg_logit").clip(-3, 3)
    x = (np.array(COARSE_BINS_S[:-1]) + np.array(COARSE_BINS_S[1:])) / 2
    ax[3].plot(x, piv.to_numpy(), color="#bbb"), ax[3].plot(x, piv.median(axis=1), "k", lw=2.5)
    ax[3].axhline(0, color="k", lw=0.5), ax[3].set_xlabel("RT - pulse onset (s)"), ax[3].set_ylabel("right - left pulse (logit)")
    ax[3].set_title("per mouse (grey, clipped at +-3), median (black)")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}.png", dpi=150), plt.close(fig)


def figure_per_mouse(t, jf, mtc, date):
    mice = sorted(t.mouse.unique())
    fig, ax = plt.subplots(len(mice), 3, figsize=(16, 3.2 * len(mice)))
    cc = np.linspace(-1, 1, 201)
    for i, m in enumerate(mice):
        g = t[t.mouse == m]
        c = cells(g)
        p = jf[(jf.mouse == m) & (jf.model == "bias")].iloc[0]
        params = [p.k, p.A, p.t_nd_ms, p.gamma, p.bias]
        for pu, col, lab in [(1, "tab:orange", "right pulse"), (0, "k", "no pulse"), (-1, "tab:purple", "left pulse")]:
            d = c[c.pulse == pu]
            ax[i, 0].plot(100 * d.coh, d.k_right / d.n, "o", color=col, label=lab, ms=4)
            ax[i, 1].errorbar(100 * d.coh, d.rt_mean, d.rt_se, fmt="o", color=col, ms=4)
            pr, rt = predict(params, cc, np.full_like(cc, pu), True, False)
            ax[i, 0].plot(100 * cc, pr, color=col), ax[i, 1].plot(100 * cc, rt, color=col)
        ax[i, 0].set_ylim(0, 1), ax[i, 0].set_ylabel(f"{m}\nP(right)")
        ax[i, 0].set_title(f"{m}: gamma {100 * p.gamma:.1f} +- {100 * p.gamma_se:.1f}% coh (n {int(p.n_trials)})", fontsize=9)
        h = jf[(jf.mouse == m) & (jf.model == "huk")].iloc[0]
        ax[i, 1].set_ylabel("mean RT (ms)"), ax[i, 1].set_title(f"delta {100 * h.delta:.1f}% coh, LR p {h.p_delta:.2f}; t_nd {p.t_nd_ms:.0f} ms", fontsize=9)
        q = mtc[mtc.mouse == m]
        mid = (q.lo_s + q.hi_s) / 2 * 1000
        ax[i, 2].errorbar(mid - 10, q.pos_pct, q.pos_pct_se, fmt="o-", color="tab:orange", ms=4)
        ax[i, 2].errorbar(mid + 10, q.neg_pct, q.neg_pct_se, fmt="o-", color="tab:purple", ms=4)
        ax[i, 2].axhline(0, color="k", lw=0.5), ax[i, 2].set_ylim(-100, 100), ax[i, 2].set_xlim(0, FINE_MAX_S * 1000)
        ax[i, 2].set_ylabel("pulse effect (% coh)"), ax[i, 2].set_title("150 ms bins of RT - pulse onset (b1 per mouse)", fontsize=9)
    ax[0, 0].legend(fontsize=7)
    for j, lab in enumerate(["coherence (%)", "coherence (%)", "RT - pulse onset (ms)"]):
        ax[-1, j].set_xlabel(lab)
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_per_mouse.png", dpi=110), plt.close(fig)


def main(date: str):
    t = load()
    jf = joint_fits(t)
    tc = t
    fine, coarse = time_course(tc)
    ct = coarse_tests(coarse)
    mtc = mouse_time_course(tc)
    cong_pooled, cong_mouse = congruency_time_course(tc)
    ov_per, ov_summ = mouse_overlay(tc)
    pc = pooled_coarse(tc)
    mcc = mouse_congruency_coarse(tc)
    ks = ks_tests(t)
    stem = OUT / f"tables/huk_shadlen_replication_{date}"
    for name, df in [("joint_fits", jf), ("timecourse_fine", fine), ("timecourse_per_mouse", coarse), ("timecourse_tests", ct), ("timecourse_mouse_150ms", mtc), ("congruency_pooled", cong_pooled), ("congruency_mouse_150ms", cong_mouse), ("overlay_per_mouse", ov_per), ("overlay_summary", ov_summ), ("pooled_coarse", pc), ("congruency_mouse_coarse", mcc), ("ks", ks)]:
        df.to_csv(f"{stem}_{name}.csv", index=False)
    figure(t, jf, fine, coarse, date)
    figure_per_mouse(t, jf, mtc, date)  # psychometric panels show all coherences
    figure_congruency(cong_pooled, cong_mouse, date)
    figure_overlay(ov_per, ov_summ, date)
    figure_pooled_congruency(t, jf, cong_pooled, mcc, date)
    figure_per_mouse_congruency(t, jf, cong_mouse, date)
    pd.set_option("display.width", 250, "display.max_columns", 40)
    cols = ["mouse", "model", "n_trials", "k", "A", "t_nd_ms", "gamma_pct", "gamma_se_pct", "bias_pct", "delta_pct", "delta_se_pct", "p_delta", "converged"]
    print(jf[[c for c in cols if c in jf]].round(3).to_string(index=False), fine.round(2).to_string(index=False), ct.round(4).to_string(index=False),
          ks.round(4).to_string(index=False), sep="\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    main(ap.parse_args().date)
