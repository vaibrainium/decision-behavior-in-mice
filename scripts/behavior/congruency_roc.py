"""Non-parametric comparison of congruent and incongruent pulse effects (author request 2026-10-30; plan
.agents/plans/2026-10-29-huk-shadlen-replication.md, log).

Score per pulse trial: 1 if the choice went the pulse's way, minus P(choice in that direction) on no-pulse trials of the
same mouse, coherence and bin of RT - (virtual) pulse onset. AUC (Mann-Whitney) of congruent vs incongruent scores:
0.5 = the pulse moves choices toward itself equally whether it agrees or disagrees with the dots; > 0.5 = congruent
larger. Coherence 9-36% only (both pulse types exist there; no congruent pulse at 100%), no late pulses, responses
< 100 ms after onset blocked. Mice are the unit: per-mouse AUC, Wilcoxon against 0.5, mouse bootstrap CI and an
equivalence check against +-EQ_MARGIN (90% CI inside the margin, TOST logic). Pooled AUC with a hierarchical bootstrap.

    python -m scripts.behavior.congruency_roc [--date YYYY-MM-DD]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon
from statsmodels.stats.multitest import multipletests

from scripts.behavior.huk_shadlen_replication import CONG, CONG_BLOCK_S, bin_fit, load

OUT = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation/tables"
REL_BINS_S = [CONG_BLOCK_S, 0.3, 0.6, 0.9, 1.2, 1.5, 2.1, 5.0]
WINDOWS_S = {"all (>= 0.1 s)": (CONG_BLOCK_S, 5.0), "0.3-1.2 s (post hoc, where the effect is)": (0.3, 1.2)}
EQ_MARGIN = 0.05
N_BOOT = 5000


def scores(t: pd.DataFrame) -> pd.DataFrame:
    u = t[t.coherence_pct.abs().between(9, 36) & (t.rel_rt_s >= CONG_BLOCK_S)].copy()
    u["rel_bin"] = pd.cut(u.rel_rt_s, REL_BINS_S, right=False)
    ctl = u[u.pulse == 0].groupby(["mouse", "coherence_pct", "rel_bin"], observed=True).right.mean().rename("p_right_ctl")
    p = u[u.pulse != 0].join(ctl, on=["mouse", "coherence_pct", "rel_bin"]).dropna(subset=["p_right_ctl"])
    p["toward"] = np.where(p.pulse > 0, p.right, 1 - p.right)
    p["score"] = p.toward - np.where(p.pulse > 0, p.p_right_ctl, 1 - p.p_right_ctl)
    p["cat"] = np.where(np.sign(p.coherence_pct) == p.pulse, "cong", "incong")
    return p


def auc(a, b) -> float:
    return mannwhitneyu(a, b).statistic / (len(a) * len(b)) if len(a) and len(b) else np.nan


N_NULL = 200


def null_auc(w: pd.DataFrame, rng) -> np.ndarray:
    """Mean-over-mice AUC when the pulse has no effect: choices redrawn from the matched no-pulse P(toward). With 0/1
    choices the scores take baseline-dependent values, so this null is not exactly 0.5. It is a no-effect reference, not
    the equal-effect null that the congruency question needs; the test of that is the per-mouse pp difference."""
    base = w.toward - w.score
    out = []
    for _ in range(N_NULL):
        sim = w.assign(score=(rng.random(len(w)) < base).astype(float) - base)
        out.append(np.mean([auc(g[g.cat == "cong"].score, g[g.cat == "incong"].score) for _, g in sim.groupby("mouse")
                            if min((g.cat == "cong").sum(), (g.cat == "incong").sum()) >= 10]))
    return np.array(out)


def analyse(p: pd.DataFrame, rng) -> tuple[pd.DataFrame, pd.DataFrame]:
    per, summ = [], []
    for wname, (lo, hi) in WINDOWS_S.items():
        w = p[(p.rel_rt_s >= lo) & (p.rel_rt_s < hi)]
        rows = []
        for m, g in w.groupby("mouse"):
            c, i = g[g.cat == "cong"].score.to_numpy(), g[g.cat == "incong"].score.to_numpy()
            if min(len(c), len(i)) < 10:
                continue
            rows.append({"window": wname, "mouse": m, "n_cong": len(c), "n_incong": len(i), "auc": auc(c, i), "mw_p": mannwhitneyu(c, i).pvalue,
                         "cong_pp": 100 * c.mean(), "incong_pp": 100 * i.mean()})
        r = pd.DataFrame(rows)
        per.append(r)
        boot = np.array([r.auc.sample(len(r), replace=True, random_state=rng).mean() for _ in range(N_BOOT)])
        groups = {m: (g[g.cat == "cong"].score.to_numpy(), g[g.cat == "incong"].score.to_numpy()) for m, g in w.groupby("mouse")}
        mice = list(groups)
        pooled_boot = []
        for _ in range(N_BOOT // 10):  # hierarchical: mice, then trials within mouse
            pick = rng.choice(mice, len(mice))
            c = np.concatenate([rng.choice(groups[m][0], len(groups[m][0])) for m in pick if len(groups[m][0])])
            i = np.concatenate([rng.choice(groups[m][1], len(groups[m][1])) for m in pick if len(groups[m][1])])
            pooled_boot.append(auc(c, i))
        lo90, hi90 = np.percentile(boot, [5, 95])
        nul = null_auc(w, rng)
        diff = r.cong_pp - r.incong_pp
        summ.append({"window": wname, "n_mice": len(r), "mean_auc": r.auc.mean(), "ci95_lo": np.percentile(boot, 2.5), "ci95_hi": np.percentile(boot, 97.5),
                     "ci90_lo": lo90, "ci90_hi": hi90, "n_mice_auc_gt_0.5": int((r.auc > 0.5).sum()), "wilcoxon_p": wilcoxon(r.auc - 0.5).pvalue,
                     "equivalent_within_margin": bool(lo90 > 0.5 - EQ_MARGIN and hi90 < 0.5 + EQ_MARGIN),
                     "null_auc_mean": nul.mean(), "null_auc_lo": np.percentile(nul, 2.5), "null_auc_hi": np.percentile(nul, 97.5),
                     "p_vs_null": (np.sum(np.abs(nul - nul.mean()) >= abs(r.auc.mean() - nul.mean())) + 1) / (len(nul) + 1),
                     "mean_cong_pp": r.cong_pp.mean(), "mean_incong_pp": r.incong_pp.mean(), "cong_minus_incong_pp": diff.mean(),
                     "n_mice_incong_larger": int((diff < 0).sum()), "wilcoxon_p_pp_diff": wilcoxon(diff).pvalue,
                     "pooled_auc": auc(w[w.cat == "cong"].score, w[w.cat == "incong"].score),
                     "pooled_ci95_lo": np.percentile(pooled_boot, 2.5), "pooled_ci95_hi": np.percentile(pooled_boot, 97.5)})
    return pd.concat(per, ignore_index=True), pd.DataFrame(summ)


def roc_curve(a, b):
    """Empirical ROC: x = P(score_b >= c), y = P(score_a >= c) over thresholds c."""
    th = np.unique(np.concatenate([a, b]))[::-1]
    return np.r_[0, [(b >= c).mean() for c in th]], np.r_[0, [(a >= c).mean() for c in th]]


def figure(p, per, summ, date):
    """Congruent-vs-incongruent ROC curves: one thin line per mouse, pooled trials in bold; one panel per window."""
    fig, ax = plt.subplots(1, len(WINDOWS_S), figsize=(13, 6.2))
    for a, (w, (lo, hi)) in zip(ax, WINDOWS_S.items()):
        g = p[(p.rel_rt_s >= lo) & (p.rel_rt_s < hi)]
        q = per[per.window == w].set_index("mouse")
        for m, gm in g.groupby("mouse"):
            if m not in q.index:
                continue
            x, y = roc_curve(gm[gm.cat == "cong"].score.to_numpy(), gm[gm.cat == "incong"].score.to_numpy())
            a.plot(x, y, color="tab:blue", alpha=0.35, lw=1, label=f"{m} {q.loc[m, 'auc']:.2f}")
        x, y = roc_curve(g[g.cat == "cong"].score.to_numpy(), g[g.cat == "incong"].score.to_numpy())
        sm = summ[summ.window == w].iloc[0]
        a.plot(x, y, color="k", lw=2.5, label=f"pooled {sm.pooled_auc:.3f} [{sm.pooled_ci95_lo:.3f}, {sm.pooled_ci95_hi:.3f}]")
        a.plot([0, 1], [0, 1], "k:", lw=0.8)
        a.set_aspect("equal"), a.set_xlim(0, 1), a.set_ylim(0, 1)
        a.set_xlabel("P(incongruent score >= criterion)"), a.set_ylabel("P(congruent score >= criterion)")
        a.set_title(f"{w}\nmean AUC over mice {sm.mean_auc:.3f} [{sm.ci95_lo:.3f}, {sm.ci95_hi:.3f}]; AUC if the pulse had no effect {sm.null_auc_mean:.3f} "
                    f"[{sm.null_auc_lo:.3f}, {sm.null_auc_hi:.3f}]\ncongruent {sm.mean_cong_pp:.1f} vs incongruent {sm.mean_incong_pp:.1f} pp toward pulse, "
                    f"difference Wilcoxon p {sm.wilcoxon_p_pp_diff:.3f}", fontsize=8)
        a.legend(fontsize=7, loc="upper left", title="AUC", title_fontsize=7)
    fig.suptitle("Congruent vs incongruent pulses: ROC per mouse (thin) and pooled (bold); below the diagonal = incongruent moves choices more\n"
                 "score = choice toward the pulse minus matched no-pulse trials; |coherence| 9-36%, no late pulses, first 100 ms blocked", fontsize=10)
    fig.tight_layout(), fig.savefig(OUT.parent / f"figures/qc/congruency_roc_{date}.png", dpi=140), plt.close(fig)


PANEL4 = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation/tables/huk_shadlen_replication_2026-10-29_congruency_mouse_coarse.csv"
N_PERM = 20000


LATE_START_EDGES_S = [0.25, 0.55, 0.85, 1.15, 1.45, 1.8, 5.0]  # author 2026-10-30: start 250 ms after pulse onset


def panel4_effects(t: pd.DataFrame, edges) -> pd.DataFrame:
    """Per-mouse congruent / incongruent logit effects toward the correct side in the given bins, computed as
    huk_shadlen_replication.mouse_congruency_coarse (all coherences, categorical coherence, 0% pulse trials dropped)."""
    u = t[~((t.coherence_pct == 0) & (t.pulse != 0)) & (t.rel_rt_s >= edges[0])]
    rows = []
    for m, g in u.groupby("mouse"):
        for lo, hi in zip(edges[:-1], edges[1:]):
            try:
                f = bin_fit(g[(g.rel_rt_s >= lo) & (g.rel_rt_s < hi)], False, **CONG)
            except Exception:
                continue
            rows.append({"mouse": m, "lo_s": lo, "hi_s": hi, "cong_logit": f["b_cong"], "incong_logit": f["b_incong"], "n_cong": f["n_cong"], "n_incong": f["n_incong"]})
    return pd.DataFrame(rows)


def panel4_roc(rng, d: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ROC on the per-mouse x bin effects of the pooled congruency figure, panel 4 (logit toward the correct side; from
    huk_shadlen_replication). Magnitude toward the pulse: congruent = cong_logit, incongruent = -incong_logit.
    AUC(congruent vs incongruent magnitude): 0.5 = symmetric, < 0.5 = incongruent larger. Points from separated fits
    (|logit| > 10) dropped. Null: swap the two labels within each mouse x bin pair (pairing kept), N_PERM permutations."""
    d = pd.read_csv(PANEL4) if d is None else d
    d = d[(d.cong_logit.abs() < 10) & (d.incong_logit.abs() < 10)].assign(c=lambda x: x.cong_logit, i=lambda x: -x.incong_logit)

    def perm_p(g):
        c, i = g.c.to_numpy(), g.i.to_numpy()
        obs = auc(c, i)
        null = []
        for _ in range(N_PERM // 10):
            sw = rng.random(len(c)) < 0.5
            null.append(auc(np.where(sw, i, c), np.where(sw, c, i)))
        null = np.array(null)
        return obs, (np.sum(np.abs(null - 0.5) >= abs(obs - 0.5)) + 1) / (len(null) + 1)

    rows = []
    for (lo, hi), g in [((d.lo_s.min(), d.hi_s.max()), d)] + list(d.groupby(["lo_s", "hi_s"])):
        a, pp = perm_p(g)
        rows.append({"bins": "all" if len(g) == len(d) else f"{lo:.2f}-{hi:.2f} s", "n_points": len(g), "n_mice": g.mouse.nunique(), "auc": a, "perm_p": pp,
                     "mean_cong": g.c.mean(), "mean_incong_mag": g.i.mean(), "n_incong_larger": int((g.i > g.c).sum()),
                     "wilcoxon_p": wilcoxon(g.c - g.i).pvalue if len(g) >= 5 else np.nan})
    r = pd.DataFrame(rows)
    ok = (r.bins != "all") & r.perm_p.notna()
    r.loc[ok, "holm_p"] = multipletests(r.loc[ok, "perm_p"], method="holm")[1]
    return d, r


def figure_panel4(d, r, date, tag="", start_s=CONG_BLOCK_S):
    fig, ax = plt.subplots(1, 3, figsize=(20, 6))
    cmap = plt.get_cmap("viridis")
    bins = sorted(d.lo_s.unique())
    for k, lo in enumerate(bins):
        g = d[d.lo_s == lo]
        x, y = roc_curve(g.c.to_numpy(), g.i.to_numpy())
        rr = r[r.bins == f"{lo:.2f}-{g.hi_s.iloc[0]:.2f} s"].iloc[0]
        ax[0].plot(x, y, color=cmap(k / max(1, len(bins) - 1)), lw=1, alpha=0.7, label=f"{rr.bins}: {rr.auc:.2f} (n {rr.n_mice})")
    x, y = roc_curve(d.c.to_numpy(), d.i.to_numpy())
    ra = r[r.bins == "all"].iloc[0]
    ax[0].plot(x, y, "k", lw=2.5, label=f"all bins: AUC {ra.auc:.3f}, permutation p {ra.perm_p:.3f}")
    ax[0].plot([0, 1], [0, 1], "k:", lw=0.8), ax[0].set_aspect("equal")
    ax[0].set_xlabel("P(incongruent magnitude >= criterion)"), ax[0].set_ylabel("P(congruent magnitude >= criterion)")
    ax[0].legend(fontsize=7, loc="lower right", title="time bin: AUC", title_fontsize=7)
    ax[0].set_title("ROC, congruent vs incongruent effect (mouse x bin points)", fontsize=10)
    # scatter: congruent vs incongruent magnitude per mouse x bin; on the diagonal = symmetric
    lim = np.ceil(max(d.c.abs().max(), d.i.abs().max()) * 2) / 2
    for k, lo in enumerate(bins):
        g = d[d.lo_s == lo]
        ax[1].scatter(g.c, g.i, color=cmap(k / max(1, len(bins) - 1)), s=30, edgecolor="k", lw=0.3, label=f"{lo:.2f}-{g.hi_s.iloc[0]:.2f} s")
    ax[1].plot([-lim, lim], [-lim, lim], "k:", lw=0.8), ax[1].axhline(0, color="#ccc", lw=0.5), ax[1].axvline(0, color="#ccc", lw=0.5)
    ax[1].set_xlim(-lim, lim), ax[1].set_ylim(-lim, lim), ax[1].set_aspect("equal")
    ax[1].set_xlabel("congruent effect toward the pulse (logit)"), ax[1].set_ylabel("incongruent effect toward the pulse (logit)")
    ax[1].legend(fontsize=7, title="time bin", title_fontsize=7, loc="upper left")
    ax[1].set_title(f"one point per mouse x bin; above diagonal = incongruent larger ({int(ra.n_incong_larger)}/{int(ra.n_points)})", fontsize=10)
    # difference over time: incongruent - congruent magnitude, per mouse (thin) and mean +- SEM over mice (bold)
    d = d.assign(diff=d.i - d.c, mid=1000 * (d.lo_s + d.hi_s.clip(upper=2.1)) / 2)
    for m, g in d.groupby("mouse"):
        ax[2].plot(g.mid, g["diff"], color="#999", alpha=0.5, lw=0.8)
    sm = d.groupby("mid")["diff"].agg(["mean", "sem"])
    ax[2].errorbar(sm.index, sm["mean"], sm["sem"], fmt="ko-", lw=2.5, capsize=3, label="mean +- SEM over mice")
    for _, rr in r[r.bins != "all"].iterrows():
        lo, hi = (float(v) for v in rr.bins.rstrip(" s").split("-"))
        if rr.holm_p < 0.05:
            ax[2].text(1000 * (lo + min(hi, 2.1)) / 2, sm["mean"].max() + 0.3, "*", ha="center", fontsize=14)
    ax[2].axhline(0, color="k", lw=0.6), ax[2].set_xlabel("RT - pulse onset (ms; bin centres, last bin 1.8-5 s drawn at 1.95 s)")
    ax[2].set_ylabel("incongruent - congruent effect (logit)"), ax[2].legend(fontsize=8)
    ax[2].set_title("asymmetry over time (> 0: incongruent larger); * Holm p < .05", fontsize=10)
    fig.suptitle(f"Is the pulse effect symmetric? Per-mouse effects (panel 4 method), responses from {1000 * start_s:.0f} ms after pulse onset; "
                 "AUC 0.5 = symmetric", fontsize=11)
    fig.tight_layout(), fig.savefig(OUT.parent / f"figures/qc/congruency_roc_panel4{tag}_{date}.png", dpi=140), plt.close(fig)


CHOICE_BINS_S = [0.1, 0.3, 0.6, 0.9, 1.2, 1.5, 2.1]


def choice_effects(p: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Model-free effect of each pulse type on choice: change in P(correct) vs matched no-pulse trials (same mouse,
    coherence, RT - onset bin), percentage points, per mouse x bin; congruent should be > 0, incongruent < 0.
    Equals the score with the incongruent sign flipped (toward the pulse = away from correct)."""
    q = p.assign(d_correct=np.where(p.cat == "cong", p.score, -p.score))
    q = q[q.rel_rt_s < CHOICE_BINS_S[-1]].assign(bin=lambda x: pd.cut(x.rel_rt_s, CHOICE_BINS_S, right=False))
    pm = q.groupby(["mouse", "bin", "cat"], observed=True).agg(d_pp=("d_correct", lambda x: 100 * x.mean()), n=("d_correct", "size")).reset_index()
    pm = pm[pm.n >= 10]
    pm["mid_ms"] = pm.bin.map(lambda b: 1000 * (b.left + b.right) / 2).astype(float)
    rows = []
    for (b, cat), g in pm.groupby(["bin", "cat"], observed=True):
        rows.append({"bin": str(b), "mid_ms": g.mid_ms.iloc[0], "cat": cat, "n_mice": len(g), "mean_pp": g.d_pp.mean(), "sem_pp": g.d_pp.sem(),
                     "n_expected_sign": int((np.sign(g.d_pp) == (1 if cat == "cong" else -1)).sum()), "wilcoxon_p": wilcoxon(g.d_pp).pvalue if len(g) >= 5 else np.nan})
    r = pd.DataFrame(rows)
    ok = r.wilcoxon_p.notna()
    r.loc[ok, "holm_p"] = multipletests(r.loc[ok, "wilcoxon_p"], method="holm")[1]
    return pm, r


def figure_choice_effects(pm, r, date):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for cat, col, lab in [("cong", "tab:blue", "congruent pulse"), ("incong", "tab:red", "incongruent pulse")]:
        for m, g in pm[pm.cat == cat].groupby("mouse"):
            ax.plot(g.mid_ms, g.d_pp, color=col, alpha=0.25, lw=0.8)
        q = r[r.cat == cat]
        ax.errorbar(q.mid_ms + (8 if cat == "incong" else -8), q.mean_pp, q.sem_pp, fmt="o-", color=col, lw=2.5, capsize=3, label=f"{lab} (mean +- SEM over mice)")
        for _, rr in q.iterrows():
            if rr.holm_p < 0.05:
                ax.text(rr.mid_ms, rr.mean_pp + np.sign(rr.mean_pp) * (rr.sem_pp + 2), "*", color=col, ha="center", va="center", fontsize=14)
    ax.axhline(0, color="k", lw=0.6), ax.axvspan(0, 100, color="#ddd"), ax.set_xlim(0, 2100), ax.set_ylim(-40, 40)
    ax.set_xlabel("RT - pulse onset (ms)"), ax.set_ylabel("change in P(correct) vs matched no-pulse (percentage points)")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title("Effect of the pulse on choice, model-free; |coherence| 9-36%, no late pulses\n* Holm p < .05 (Wilcoxon over mice, 12 tests)", fontsize=10)
    fig.tight_layout(), fig.savefig(OUT.parent / f"figures/qc/congruency_choice_effect_{date}.png", dpi=140), plt.close(fig)


def main(date: str):
    rng = np.random.default_rng(0)
    p = scores(load())
    per, summ = analyse(p, rng)
    per.to_csv(OUT / f"congruency_roc_{date}_per_mouse.csv", index=False)
    summ.to_csv(OUT / f"congruency_roc_{date}_summary.csv", index=False)
    figure(p, per, summ, date)
    d4, r4 = panel4_roc(rng)
    r4.to_csv(OUT / f"congruency_roc_{date}_panel4.csv", index=False)
    figure_panel4(d4, r4, date)
    print(r4.round(3).to_string(index=False))
    pm, rc = choice_effects(p)
    pm.to_csv(OUT / f"congruency_choice_effect_{date}_per_mouse.csv", index=False)
    rc.to_csv(OUT / f"congruency_choice_effect_{date}_summary.csv", index=False)
    figure_choice_effects(pm, rc, date)
    print(rc.round(3).to_string(index=False))
    d250 = panel4_effects(load(), LATE_START_EDGES_S)
    d250.to_csv(OUT / f"congruency_roc_{date}_panel4_from250ms_effects.csv", index=False)
    d250, r250 = panel4_roc(rng, d250)
    r250.to_csv(OUT / f"congruency_roc_{date}_panel4_from250ms.csv", index=False)
    figure_panel4(d250, r250, date, tag="_from250ms", start_s=LATE_START_EDGES_S[0])
    print(r250.round(3).to_string(index=False))
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(per.round(3).to_string(index=False), summ.round(3).T.to_string(), sep="\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    main(ap.parse_args().date)
