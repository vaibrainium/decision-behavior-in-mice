"""Model-free pulse signatures on all mice (plan .agents/plans/2026-10-29-pulse-descriptive-package.md).

Data only; no fits. Responded trials (D003), symmetric cells, |coh| <= 36, onset = scheduled (uw) else recorded (ucla);
the trial selection, binning and effect measure are those of scripts/ddm/pulse_leak_urgency_signatures.py, so
simulations run through that script are directly comparable.

Effect = pulse-count-weighted mean over (coh, pulse sign) of P(choice = sign | pulse) - P(choice = sign | control),
in pp; the logit version replaces each probability by its log-odds (counts + 0.5).

S1  pulse-to-response profile: effect per (mouse, stage, bin of RT - onset); controls take the stage's median onset.
    Windows: 0.3-1.2 s and 1.2-5 s after onset. Tests over mice (unit = mouse; stages pooled per mouse, weighted by
    pulse trials): window 0.3-1.2 > 0, window 1.2-5 != 0, difference; Holm over the 3 (t tests; Wilcoxon reported).
S2  effect per (mouse, stage, |coh|); per-mouse slope over |coh| of (early - middle); t and Wilcoxon over mice.
S3  RT shift, pulse minus control, for choices toward / against the pulse, coherence-matched (>= MIN_N trials per
    side and cell): quantiles 0.1-0.9, mean, SD; per (mouse, stage); group means, t CIs, sign counts.

Outputs: dissemination/figures/qc/pulse_descriptive_package_<date>.{png,pdf} and _s1_profile/_s1_windows/_s1_tests/
         _s2/_s2_tests/_s3/_s3_group/_counts.csv
Usage:   python -m scripts.ddm.pulse_descriptive_package
"""

from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_leak_urgency_signatures import (BINS, PROCESSED, STAGES, bootstrap_profile, observed,
                                                        pseudo_onsets, with_bins)
from scripts.ddm.pulse_psychometric import OUT

SEED, MIN_N = 0, 5
Q = (0.1, 0.3, 0.5, 0.7, 0.9)
EARLY_BINS, LATE_BINS = (0, 1, 2), (3, 4, 5, 6)


def _logit(k, n):
    return np.log((k + 0.5) / (n - k + 0.5))


def effect(x: pd.DataFrame, by: list[str], scale: str = "pp") -> pd.DataFrame:
    rows = []
    for key, g in x.groupby(by):
        key = key if isinstance(key, tuple) else (key,)
        ctrl = g[g.s == 0]
        for (c, s), p in g[g.s != 0].groupby(["coh", "s"]):
            k = ctrl[ctrl.coh == c]
            if not len(k):
                continue
            if scale == "pp":
                d = 100 * ((p.choice == s).mean() - (k.choice == s).mean())
            else:
                d = _logit((p.choice == s).sum(), len(p)) - _logit((k.choice == s).sum(), len(k))
            rows.append(dict(zip(by, key)) | {"n": len(p), "d": d})
    r = pd.DataFrame(rows)
    return r.groupby(by).apply(lambda m: pd.Series({"effect": np.average(m.d, weights=m.n), "n_pulse": m.n.sum()}),
                               include_groups=False).reset_index()


def mouse_test(v: pd.Series, name: str) -> dict:
    v = v.dropna()
    t = stats.ttest_1samp(v, 0)
    ci = stats.t.interval(0.95, len(v) - 1, loc=v.mean(), scale=stats.sem(v))
    w = stats.wilcoxon(v) if len(v) >= 5 else None
    return {"test": name, "n_mice": len(v), "mean": v.mean(), "ci_lo": ci[0], "ci_hi": ci[1], "dz": v.mean() / v.std(ddof=1),
            "t": t.statistic, "p_t": t.pvalue, "p_wilcoxon": w.pvalue if w else np.nan, "n_positive": int((v > 0).sum())}


def holm(p: pd.Series) -> pd.Series:
    order = p.sort_values().index
    m, run, out = len(p), 0.0, pd.Series(index=p.index, dtype=float)
    for i, idx in enumerate(order):
        run = max(run, min(1.0, (m - i) * p[idx]))
        out[idx] = run
    return out


def group_ci(df: pd.DataFrame, by: list[str], col: str = "effect") -> pd.DataFrame:
    def f(m):
        v = m[col].dropna()
        se = stats.sem(v) if len(v) > 1 else np.nan
        h = stats.t.ppf(0.975, len(v) - 1) * se if len(v) > 1 else np.nan
        return pd.Series({"mean": v.mean(), "ci_lo": v.mean() - h, "ci_hi": v.mean() + h, "n_mice": len(v),
                          "n_positive": int((v > 0).sum())})
    return df.groupby(by).apply(f, include_groups=False).reset_index()


def rt_shifts(x: pd.DataFrame) -> pd.DataFrame:
    """Per (mouse, stage, choice relative to pulse): coherence-matched pulse - control RT quantiles, mean, SD (ms)."""
    rows = []
    for (mouse, stage, c), g in x.groupby(["mouse", "stage", "coh"]):
        for s in (-1, 1):
            for rel, ch in (("toward pulse", s), ("against pulse", -s)):
                p, k = g[(g.s == s) & (g.choice == ch)].rt, g[(g.s == 0) & (g.choice == ch)].rt
                if len(p) < MIN_N or len(k) < MIN_N:
                    continue
                d = {f"q{q}": 1000 * v for q, v in zip(Q, np.quantile(p, Q) - np.quantile(k, Q))}
                rows.append({"mouse": mouse, "stage": stage, "choice": rel, "n": len(p),
                             "mean": 1000 * (p.mean() - k.mean()), "sd": 1000 * (p.std() - k.std())} | d)
    r = pd.DataFrame(rows)
    cols = ["mean", "sd"] + [f"q{q}" for q in Q]
    return r.groupby(["mouse", "stage", "choice"]).apply(
        lambda m: pd.Series({c: np.average(m[c], weights=m.n) for c in cols} | {"n_pulse": m.n.sum()}),
        include_groups=False).reset_index()


def figure(prof, prof_g, s2_g, s3_g, win, stem):
    centers = [(BINS[i] + BINS[i + 1]) / 2 for i in range(len(BINS) - 1)]
    fig, ax = plt.subplots(2, 3, figsize=(15, 8.5))
    for j, st in enumerate((1, 2, 3)):
        a = ax[0, j]
        for _, m in prof[prof.stage == st].groupby("mouse"):
            a.plot([centers[int(b)] for b in m.bin], m.effect, color="0.75", lw=0.7)
        g = prof_g[prof_g.stage == st]
        a.errorbar([centers[int(b)] for b in g.bin], g["mean"], yerr=[g["mean"] - g.ci_lo, g.ci_hi - g["mean"]],
                   fmt="o-", color="k", capsize=2, label="mean over mice (95% CI)")
        a.axhline(0, color="0.6", lw=0.6)
        a.axvline(1.2, color="0.6", ls=":", lw=0.6)
        n = int(g.n_mice.max()) if len(g) else 0
        a.set_title(f"S1 {STAGES[st]} pulse ({n} mice; grey = single mice)", fontsize=9)
        a.set_xlabel("time from pulse onset to response (s)", fontsize=8)
        a.set_ylabel("pulse effect (pp)", fontsize=8)
        a.set_ylim(-45, 55)
    ax[0, 0].legend(fontsize=7, frameon=False)
    a = ax[1, 0]
    for st, col in zip((1, 2, 3), ("C0", "C1", "C2")):
        g = s2_g[s2_g.stage == st]
        a.errorbar(g.ac + (st - 2) * 0.8, g["mean"], yerr=[g["mean"] - g.ci_lo, g.ci_hi - g["mean"]], fmt="o-", color=col,
                   capsize=2, label=f"{STAGES[st]}")
    a.axhline(0, color="0.6", lw=0.6)
    a.set_title("S2 pulse effect by |coherence| (mean over mice, 95% CI)", fontsize=9)
    a.set_xlabel("|coherence| (%)", fontsize=8); a.set_ylabel("pulse effect (pp)", fontsize=8); a.legend(fontsize=7, frameon=False)
    for k, ch in enumerate(("toward pulse", "against pulse")):
        a = ax[1, 1 + k]
        for st, col in zip((1, 2, 3), ("C0", "C1", "C2")):
            g = s3_g[(s3_g.stage == st) & (s3_g.choice == ch) & s3_g.stat.str.startswith("q")]
            qs = [float(s[1:]) for s in g.stat]
            a.errorbar(np.array(qs) + (st - 2) * 0.015, g["mean"], yerr=[g["mean"] - g.ci_lo, g.ci_hi - g["mean"]],
                       fmt="o-", color=col, capsize=2, label=STAGES[st])
        a.axhline(0, color="0.6", lw=0.6)
        a.set_title(f"S3 RT shift, choices {ch} (pulse - control)", fontsize=9)
        a.set_xlabel("RT quantile", fontsize=8); a.set_ylabel("ms", fontsize=8); a.legend(fontsize=7, frameon=False)
    fig.suptitle("Pulse descriptive package, responded trials, |coh| <= 36%, symmetric cells; mouse = unit", fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=170)
    fig.savefig(f"{stem}.pdf")


def main():
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    mice = sorted(set(inputs["subject_id"]))
    obs = observed(inputs, mice)
    onsets = pseudo_onsets(obs)
    x = with_bins(obs, onsets)
    rng = np.random.default_rng(SEED)
    stem = OUT / f"pulse_descriptive_package_{date.today().isoformat()}"

    # counts: pulse trials per stage, and how many fall before 0.3 s after onset (outside S1 bins)
    pul = x[x.s != 0]
    counts = pul.groupby(["mouse", "stage"]).apply(lambda m: pd.Series({
        "n_pulse": len(m), "n_before_0.3s": int((m.since < BINS[0]).sum()), "n_in_bins": int(m.bin.notna().sum())}),
        include_groups=False).reset_index()

    # S1
    prof = bootstrap_profile(x[x.bin.notna()], rng)
    prof["effect"], prof["se"] = 100 * prof.effect, 100 * prof.se
    prof_g = group_ci(prof, ["stage", "bin"])
    xw = x[x.bin.notna()].assign(win=lambda d: np.where(d.bin.isin(EARLY_BINS), "0.3-1.2", "1.2-5"))
    win = effect(xw, ["mouse", "stage", "win"])
    win_l = effect(xw, ["mouse", "stage", "win"], "logit")
    win = win.merge(win_l.rename(columns={"effect": "effect_logit"}).drop(columns="n_pulse"), on=["mouse", "stage", "win"])
    per_mouse = win.groupby(["mouse", "win"]).apply(lambda m: pd.Series({
        "effect": np.average(m.effect, weights=m.n_pulse), "effect_logit": np.average(m.effect_logit, weights=m.n_pulse),
        "n_pulse": m.n_pulse.sum()}), include_groups=False).unstack("win")
    tests = []
    for scale, col in (("pp", "effect"), ("logit", "effect_logit")):
        e, l = per_mouse[(col, "0.3-1.2")], per_mouse[(col, "1.2-5")]
        tests += [mouse_test(e, f"{scale}: window 0.3-1.2 s"), mouse_test(l, f"{scale}: window 1.2-5 s"),
                  mouse_test(e - l, f"{scale}: 0.3-1.2 minus 1.2-5")]
    tests = pd.DataFrame(tests)
    tests["p_holm"] = tests.groupby(tests.test.str.split(":").str[0]).p_t.transform(holm)

    # S2 (controls duplicated per stage in x; bins ignored)
    xs = x.assign(ac=x.coh.abs())
    s2 = effect(xs, ["mouse", "stage", "ac"]).merge(
        effect(xs, ["mouse", "stage", "ac"], "logit").rename(columns={"effect": "effect_logit"}).drop(columns="n_pulse"),
        on=["mouse", "stage", "ac"])
    s2_g = group_ci(s2, ["stage", "ac"])
    s2_tests = []
    for scale, col in (("pp", "effect"), ("logit", "effect_logit")):
        w = s2.pivot_table(index=["mouse", "ac"], columns="stage", values=col)
        dif = (w[1] - w[2]).dropna().reset_index(name="d")
        slopes = dif.groupby("mouse").apply(lambda m: np.polyfit(m.ac / 100, m.d, 1)[0] if m.ac.nunique() >= 2 else np.nan,
                                            include_groups=False)
        s2_tests.append(mouse_test(slopes, f"{scale}: slope of (early - middle) per 100% |coh|"))
    s2_tests = pd.DataFrame(s2_tests)

    # S3 (pulse trials of each stage vs all controls; onset irrelevant)
    s3 = rt_shifts(x)
    s3_long = s3.melt(id_vars=["mouse", "stage", "choice", "n_pulse"], var_name="stat", value_name="effect")
    s3_g = group_ci(s3_long, ["stage", "choice", "stat"])

    counts.to_csv(f"{stem}_counts.csv", index=False)
    prof.round(4).to_csv(f"{stem}_s1_profile.csv", index=False)
    win.round(4).to_csv(f"{stem}_s1_windows.csv", index=False)
    tests.round(5).to_csv(f"{stem}_s1_tests.csv", index=False)
    s2.round(4).to_csv(f"{stem}_s2.csv", index=False)
    s2_tests.round(5).to_csv(f"{stem}_s2_tests.csv", index=False)
    s3.round(2).to_csv(f"{stem}_s3.csv", index=False)
    s3_g.round(2).to_csv(f"{stem}_s3_group.csv", index=False)
    prof_g.round(3).to_csv(f"{stem}_s1_group.csv", index=False)
    s2_g.round(3).to_csv(f"{stem}_s2_group.csv", index=False)
    figure(prof, prof_g, s2_g, s3_g, win, stem)

    pd.set_option("display.width", 220); pd.set_option("display.max_rows", 300)
    print(counts.to_string(index=False))
    print(prof_g.round(2).to_string(index=False))
    print(per_mouse.round(3).to_string())
    print(tests.round(4).to_string(index=False))
    print(s2_g.round(2).to_string(index=False))
    print(s2_tests.round(4).to_string(index=False))
    print(s3_g[s3_g.stat.isin(["mean", "sd", "q0.5", "q0.9"])].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
