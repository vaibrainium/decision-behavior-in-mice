"""Behavioural data exploration before new modelling (plan .agents/plans/2026-10-29-behavior-exploration.md).

Sections: (1) provenance of trials and sessions through the inclusion pipeline of notebooks/0.1-preprocessing-data;
(2) task parameters per mouse; (3) engagement within session; (4) behaviour and pulse effect across sessions;
(5) control psychometry, chronometry and RT distributions; (6) trial history; (7) per-mouse pulse summary.

Analyses use responded trials (choice by 5 s) of the included sessions unless a table says otherwise; rows from excluded
sessions are descriptive only. Mice are the unit for group tests; rig enters only as a column, never as a grouping.

    python -m scripts.behavior.explore_behavior [--date YYYY-MM-DD]
"""

import argparse
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr, wilcoxon
from statsmodels.stats.multitest import multipletests

from config import dir_config, main_config
from src.utils import pmf_utils

PROCESSED = Path(dir_config.data.processed)
OUT = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation"
AC = main_config.acceptance_criteria
DEADLINE_S = 5.0
N_POSITION_BINS = 10
MIN_PULSE_TRIALS_SESSION = 50

warnings.filterwarnings("ignore")


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    """All raw trials in session order with derived columns, and the included trials (valid_data.csv)."""
    a = pd.read_csv(PROCESSED / "aggregate_data.csv", low_memory=False)
    a = a.sort_values(["subject_id", "session_id", "idx_valid_trial", "idx_correction"], kind="stable").reset_index(drop=True)
    a["mouse"], a["corr_trial"] = a.subject_id, a.is_correction_trial.astype(bool)
    a["sess_num"] = a.session_id.str.split("_").str[0].astype(int)
    a["responded"] = a.choice.notna() & (a.reaction_time <= DEADLINE_S) & (a.reaction_time >= AC.min_reaction_time)
    a["late_choice"] = a.choice.notna() & (a.reaction_time > DEADLINE_S)
    a["right"] = (a.choice == 1).astype(float).where(a.choice.notna())
    a["pulse_dir"] = np.sign(a.pulse_type)
    a["stage"] = a.pulse_type.abs()
    a["position"] = a.groupby(["mouse", "session_id"]).cumcount()
    a["position_frac"] = a.position / a.groupby(["mouse", "session_id"]).position.transform("max")
    prev = a.groupby(["mouse", "session_id"])[["choice", "outcome", "reward_amount", "corr_trial"]].shift(1)
    side = prev.choice.map({1.0: 1.0, 0.0: -1.0}).fillna(0.0)
    a["prev_win"] = np.where(prev.outcome == 1, side, 0.0)
    a["prev_lose"] = np.where(prev.outcome == 0, side, 0.0)
    a["prev_none"] = prev.choice.isna().astype(float)
    a["prev_after_corr"] = prev.corr_trial.fillna(False).astype(float)
    a["prev_reward"] = prev.reward_amount.where(prev.outcome == 1)
    v = pd.read_csv(PROCESSED / "valid_data.csv", low_memory=False)
    a["in_valid"] = a.set_index(["mouse", "session_id"]).index.isin(v.set_index(["subject_id", "session_id"]).index)
    return a, v


# 1. Provenance ----------------------------------------------------------------------------------------------------
def sessions(a: pd.DataFrame) -> pd.DataFrame:
    """Every session with the inclusion criteria of notebooks/0.1 re-applied and the criteria it failed."""
    rows = []
    for (m, s), g in a.groupby(["mouse", "session_id"]):
        nc = g[~g.corr_trial]
        ok = nc[(nc.reaction_time >= AC.min_reaction_time) & (nc.reaction_time <= AC.max_reaction_time)]
        r = {"mouse": m, "rig": g.data_source.iloc[0], "session_id": s, "sess_num": g.sess_num.iloc[0], "n_all": len(g),
             "n_correction": int(g.corr_trial.sum()), "n_no_choice": int(nc.choice.isna().sum()), "n_late_choice": int(nc.late_choice.sum()),
             "n_responded": len(ok), "n_pulse_responded": int((ok.pulse_type != 0).sum()), "acc100": ok[ok.signed_coherence.abs() == 100].outcome.mean(),
             "in_valid": bool(g.in_valid.iloc[0])}
        fail = []
        if len(ok) < AC.min_trials:
            fail.append("n_trials")
        else:
            _, _, model, _, _ = pmf_utils.get_psychometric_data(ok[ok.pulse_type == 0], model_type=main_config.psych_model, x_model_range=[-100, 100])
            k = model.coefs_
            r |= {"lapse": k["lapse_rate"], "guess": k["guess_rate"], "alpha": k["mean"], "beta": k["var"]}
            fail += [n for n, bad in [("lapse", k["lapse_rate"] >= AC.max_lapse_rate), ("guess", k["guess_rate"] >= AC.max_guess_rate),
                                      ("bias", abs(k["mean"]) >= AC.max_abs_alpha), ("beta", k["var"] >= AC.max_beta)] if bad]
        r["failed"] = "+".join(fail) or "pass"
        rows.append(r)
    s = pd.DataFrame(rows).sort_values(["mouse", "sess_num"])
    s["history_rank"] = s.groupby("mouse").sess_num.rank(pct=True)
    assert ((s.failed == "pass") == s.in_valid).all(), "re-applied criteria do not reproduce valid_data"
    return s


def provenance(a: pd.DataFrame, s: pd.DataFrame, v: pd.DataFrame) -> pd.DataFrame:
    kept = s[s.in_valid]
    t = s.groupby("mouse").agg(rig=("rig", "first"), sessions=("session_id", "size"), sessions_kept=("in_valid", "sum"),
                               trials_raw=("n_all", "sum"), correction=("n_correction", "sum"), no_choice=("n_no_choice", "sum"),
                               late_choice=("n_late_choice", "sum"), responded=("n_responded", "sum"), pulse_responded=("n_pulse_responded", "sum"))
    t["responded_kept"] = kept.groupby("mouse").n_responded.sum()
    t["pulse_responded_kept"] = kept.groupby("mouse").n_pulse_responded.sum()
    t["valid_data_rows"] = v.groupby("subject_id").size()
    t = t.fillna(0).astype({c: int for c in t.columns if c != "rig"})
    assert (t.responded_kept == t.valid_data_rows).all()
    late = a[a.late_choice & ~a.corr_trial & a.in_valid]
    t["late_choice_accuracy_kept"] = late.groupby("mouse").outcome.mean().round(3)
    t["late_choice_median_rt_kept"] = late.groupby("mouse").reaction_time.median().round(2)
    return t.reset_index()


# 2. Task parameters -----------------------------------------------------------------------------------------------
def task_parameters(v: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m, g in v.groupby("subject_id"):
        p = g[g.pulse_type != 0]
        r = {"mouse": m, "rig": g.data_source.iloc[0], "coherences": " ".join(map(str, sorted(g.signed_coherence.unique()))),
             "fixation_s_median": g.fixation_duration.median(), "iti_s_median": g.intertrial_delay.median(), "iti_s_p90": g.intertrial_delay.quantile(0.9),
             "stimulus_duration_s": g.stimulus_duration.median(), "reward_rewarded_mean": g[g.outcome == 1].reward_amount.mean(),
             "reward_left_minus_right": g[(g.outcome == 1) & (g.target == -1)].reward_amount.mean() - g[(g.outcome == 1) & (g.target == 1)].reward_amount.mean(),
             "pulse_duration_ms_median": 1000 * p.pulse_duration.median(), "pulse_coherence_values": " ".join(map(str, sorted(p.pulse_coherence.abs().unique())))}
        for st in (1, 2, 3):
            q = p[p.pulse_type.abs() == st].pulse_onset * 1000
            r[f"onset_ms_stage{st}"] = f"{q.min():.0f}-{q.max():.0f}" if len(q) else ""
        rows.append(r)
    return pd.DataFrame(rows).round(3)


# 3. Engagement within session -------------------------------------------------------------------------------------
def within_session(a: pd.DataFrame) -> pd.DataFrame:
    k = a[a.in_valid & ~a.corr_trial].copy()
    k["bin"] = np.minimum((k.position_frac * N_POSITION_BINS).astype(int), N_POSITION_BINS - 1)
    r = k[k.responded]
    out = pd.DataFrame({
        "no_response": k.groupby(["mouse", "bin"]).responded.apply(lambda x: 1 - x.mean()),
        "acc100": r[r.signed_coherence.abs() == 100].groupby(["mouse", "bin"]).outcome.mean(),
        "acc_9_36": r[r.signed_coherence.abs().between(9, 36)].groupby(["mouse", "bin"]).outcome.mean(),
        "p_right": r.groupby(["mouse", "bin"]).right.mean(),
        "median_rt": r.groupby(["mouse", "bin"]).reaction_time.median(),
        "n": k.groupby(["mouse", "bin"]).size()})
    return out.reset_index()


def trend_tests(df: pd.DataFrame, x: str, metrics: list[str], label: str) -> pd.DataFrame:
    """Per-mouse Spearman rho of each metric against x; Wilcoxon of the rhos over mice; Holm over the metrics."""
    rows = []
    for met in metrics:
        rho = df.dropna(subset=[met]).groupby("mouse").apply(lambda g: spearmanr(g[x], g[met])[0] if g[x].nunique() > 2 else np.nan).dropna()
        rows.append({"analysis": label, "metric": met, "n_mice": len(rho), "mean_rho": rho.mean(), "n_positive": int((rho > 0).sum()),
                     "wilcoxon_p": wilcoxon(rho).pvalue if len(rho) >= 5 else np.nan})
    t = pd.DataFrame(rows)
    ok = t.wilcoxon_p.notna()
    t.loc[ok, "holm_p"] = multipletests(t.loc[ok, "wilcoxon_p"], method="holm")[1]
    return t


# 4. Across sessions -----------------------------------------------------------------------------------------------
def per_session(a: pd.DataFrame, s: pd.DataFrame) -> pd.DataFrame:
    """Behaviour of every session (included or not) and its pulse effect (logit of right on pulse direction given
    coherence); excluded sessions are descriptive only."""
    rows = []
    for (m, sid), g in a[~a.corr_trial].groupby(["mouse", "session_id"]):
        r = g[g.responded]
        row = {"mouse": m, "session_id": sid, "no_response": 1 - g.responded.mean(), "median_rt": r.reaction_time.median(),
               "acc100": r[r.signed_coherence.abs() == 100].outcome.mean(), "acc_9_36": r[r.signed_coherence.abs().between(9, 36)].outcome.mean(),
               "p_right_control": r[r.pulse_type == 0].right.mean()}
        p = r[r.pulse_type != 0]
        row["n_pulse"] = len(p)
        if len(p) >= MIN_PULSE_TRIALS_SESSION:
            try:
                fit = smf.logit("right ~ C(signed_coherence) + pulse_dir", r[r.stage.isin([0, 1, 2, 3])]).fit(disp=0)
                row["pulse_logit"], row["pulse_logit_se"] = fit.params["pulse_dir"], fit.bse["pulse_dir"]
            except Exception:  # perfect separation in small sessions
                pass
        rows.append(row)
    return s[["mouse", "rig", "session_id", "sess_num", "history_rank", "in_valid", "failed"]].merge(pd.DataFrame(rows), on=["mouse", "session_id"])


# 5. Control behaviour -----------------------------------------------------------------------------------------------
def control_curves(a: pd.DataFrame) -> pd.DataFrame:
    c = a[a.in_valid & ~a.corr_trial & a.responded & (a.pulse_type == 0)].copy()
    c["abs_coh"] = c.signed_coherence.abs()
    psy = c.groupby(["mouse", "signed_coherence"]).right.agg(p_right="mean", n="size").reset_index()
    chrono = c.groupby(["mouse", "abs_coh", "outcome"]).reaction_time.agg(median_rt="median", n="size").reset_index()
    chrono["outcome"] = chrono.outcome.map({1.0: "correct", 0.0: "error"})
    return psy, chrono, c


def late_choice_accuracy(a: pd.DataFrame) -> pd.DataFrame:
    """Accuracy of choices made after the 5 s deadline (excluded from analyses) vs responded trials, included sessions."""
    k = a[a.in_valid & ~a.corr_trial & a.choice.notna()].assign(abs_coh=lambda d: d.signed_coherence.abs(), late=lambda d: d.reaction_time > DEADLINE_S)
    pm = k.groupby(["late", "abs_coh", "mouse"]).outcome.mean().groupby(["late", "abs_coh"]).agg(mouse_mean="mean", n_mice="size")
    return pm.join(k.groupby(["late", "abs_coh"]).size().rename("n_trials")).reset_index()


def rt_summary(c: pd.DataFrame) -> pd.DataFrame:
    g = c.groupby("mouse").reaction_time
    return pd.DataFrame({"median": g.median(), "p10": g.quantile(0.1), "p90": g.quantile(0.9), "frac_below_0_5s": g.apply(lambda x: (x < 0.5).mean()),
                         "frac_below_0_35s": g.apply(lambda x: (x < 0.35).mean()), "frac_above_3s": g.apply(lambda x: (x > 3).mean()),
                         "acc100_fast_lt_0_5s": c[(c.reaction_time < 0.5) & (c.abs_coh == 100)].groupby("mouse").outcome.mean(),
                         "acc100_rest": c[(c.reaction_time >= 0.5) & (c.abs_coh == 100)].groupby("mouse").outcome.mean()}).round(3).reset_index()


# 6. Trial history -------------------------------------------------------------------------------------------------
HISTORY_TERMS = ["prev_win", "prev_lose", "prev_none"]


def history(a: pd.DataFrame) -> pd.DataFrame:
    """Per mouse: right ~ C(coherence) + pulse_dir + prev_win + prev_lose + prev_none (previous trial = the trial before
    in the session, correction and late trials included; win/lose = +1 right, -1 left choice when rewarded/unrewarded)."""
    k = a[a.in_valid & ~a.corr_trial & a.responded]
    rows = []
    for m, g in k.groupby("mouse"):
        terms = [t for t in HISTORY_TERMS if g[t].std() > 0]  # no choice-less trials in some mice
        fit = smf.logit("right ~ C(signed_coherence) + pulse_dir + " + " + ".join(terms), g).fit(disp=0)
        rows.append({"mouse": m, "n": len(g), "n_after_no_choice": int(g.prev_none.sum()), **{t: fit.params.get(t, np.nan) for t in HISTORY_TERMS},
                     **{f"{t}_p": fit.pvalues.get(t, np.nan) for t in HISTORY_TERMS},
                     "pulse_dir": fit.params["pulse_dir"], "rt_after_error_minus_correct": g[g.prev_lose != 0].reaction_time.median() - g[g.prev_win != 0].reaction_time.median()})
    return pd.DataFrame(rows)


def group_tests(h: pd.DataFrame, cols: list[str], label: str) -> pd.DataFrame:
    t = pd.DataFrame([{"analysis": label, "metric": c, "n_mice": h[c].notna().sum(), "mean": h[c].mean(), "n_positive": int((h[c] > 0).sum()),
                       "wilcoxon_p": wilcoxon(h[c].dropna()).pvalue} for c in cols])
    t["holm_p"] = multipletests(t.wilcoxon_p, method="holm")[1]
    return t


# Figures ----------------------------------------------------------------------------------------------------------
def figures(s, ws, ps, psy, chrono, c, h, date):
    mice = sorted(s.mouse.unique())
    kept_mice = sorted(s[s.in_valid].mouse.unique())
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    reasons = ["pass", "n_trials", "lapse", "guess", "bias", "beta"]
    first = s.failed.str.split("+").str[0]
    ct = pd.crosstab(s.mouse, first).reindex(columns=reasons, fill_value=0).reindex(mice)
    ct.plot.bar(stacked=True, ax=ax[0], color=["k", "#bbb", "#e41a1c", "#377eb8", "#ff7f00", "#984ea3"], width=0.8)
    ax[0].set_ylabel("sessions"), ax[0].set_title("Sessions per mouse by first failed criterion (pass = in valid_data)")
    for i, m in enumerate(mice):
        g = s[s.mouse == m]
        ax[1].scatter(g.sess_num, np.full(len(g), i), c=np.where(g.in_valid, "k", "#ccc"), s=14)
    ax[1].set_yticks(range(len(mice)), mice), ax[1].set_xlabel("session number"), ax[1].set_title("Included (black) and excluded sessions in each mouse's history")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/behavior_exploration_{date}_provenance.png", dpi=150), plt.close(fig)

    mets = ["no_response", "acc100", "acc_9_36", "p_right", "median_rt"]
    fig, ax = plt.subplots(1, len(mets), figsize=(20, 4))
    for i, met in enumerate(mets):
        piv = ws.pivot(index="bin", columns="mouse", values=met)
        ax[i].plot((piv.index + 0.5) / N_POSITION_BINS, piv, color="#bbb", lw=0.8)
        ax[i].plot((piv.index + 0.5) / N_POSITION_BINS, piv.mean(axis=1), "k", lw=2.5)
        ax[i].set_title(met), ax[i].set_xlabel("position in session")
    fig.suptitle("Within session, included sessions (grey: mice, black: mean over mice)"), fig.tight_layout()
    fig.savefig(OUT / f"figures/qc/behavior_exploration_{date}_within_session.png", dpi=150), plt.close(fig)

    fig, ax = plt.subplots(2, 7, figsize=(24, 7), sharey="row")
    for i, m in enumerate(mice[:14]):
        g = ps[(ps.mouse == m)]
        r = ax[0 if i < 7 else 1, i % 7]
        q = g.dropna(subset=["pulse_logit"])
        r.errorbar(q.sess_num, q.pulse_logit, q.pulse_logit_se, fmt="none", ecolor="#ccc")
        r.scatter(q.sess_num, q.pulse_logit, c=np.where(q.in_valid, "k", "#aaa"), s=18, zorder=3)
        r2 = r.twinx()
        r2.plot(g.sess_num, g.acc100, color="tab:green", lw=1), r2.set_ylim(0.4, 1)
        r.axhline(0, color="k", lw=0.5), r.set_title(m), r.set_xlabel("session")
    ax[0, 0].set_ylabel("pulse effect (logit)"), ax[1, 0].set_ylabel("pulse effect (logit)")
    fig.suptitle("Pulse effect per session (black: included, grey: excluded; bars SE) and accuracy at 100% (green, right axis)")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/behavior_exploration_{date}_across_sessions.png", dpi=150), plt.close(fig)

    fig, ax = plt.subplots(3, len(kept_mice), figsize=(3 * len(kept_mice), 9))
    for i, m in enumerate(kept_mice):
        g = psy[psy.mouse == m]
        ax[0, i].plot(g.signed_coherence, g.p_right, "ko-"), ax[0, i].set_ylim(0, 1), ax[0, i].axhline(0.5, color="#ccc"), ax[0, i].set_title(m)
        for oc, col in [("correct", "k"), ("error", "tab:red")]:
            q = chrono[(chrono.mouse == m) & (chrono.outcome == oc) & (chrono.n >= 10)]
            ax[1, i].plot(q.abs_coh, q.median_rt, "o-", color=col, label=oc)
        ax[1, i].set_ylim(0.3, 2.5)
        ax[2, i].hist(c[c.mouse == m].reaction_time, bins=np.arange(0.3, 5.01, 0.1), color="#555")
        ax[2, i].set_xlabel("RT (s)")
    ax[0, 0].set_ylabel("P(right), control"), ax[1, 0].set_ylabel("median RT (s)"), ax[1, 0].legend(), ax[2, 0].set_ylabel("trials")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/behavior_exploration_{date}_control.png", dpi=150), plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    for j, t in enumerate(HISTORY_TERMS + ["pulse_dir"]):
        ax.scatter(np.full(len(h), j) + np.linspace(-0.15, 0.15, len(h)), h[t], color="#777")
        ax.plot([j - 0.25, j + 0.25], [h[t].mean()] * 2, "k", lw=2)
    ax.axhline(0, color="k", lw=0.5), ax.set_xticks(range(4), ["prev win\n(+1 right)", "prev lose\n(+1 right)", "prev no choice", "pulse direction"])
    ax.set_ylabel("logit weight"), ax.set_title("History weights per mouse (points), mean (bar)")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/behavior_exploration_{date}_history.png", dpi=150), plt.close(fig)


def main(date: str):
    a, v = load()
    s = sessions(a)
    prov = provenance(a, s, v)
    tp = task_parameters(v)
    ws = within_session(a)
    ps = per_session(a, s)
    psy, chrono, c = control_curves(a)
    rts = rt_summary(c)
    late = late_choice_accuracy(a)
    h = history(a)
    ps_kept = ps[ps.in_valid]
    tests = pd.concat([
        trend_tests(ws, "bin", ["no_response", "acc100", "acc_9_36", "p_right", "median_rt"], "within session (included sessions)"),
        trend_tests(ps_kept, "sess_num", ["pulse_logit", "acc100", "acc_9_36", "median_rt", "no_response"], "across included sessions (mice with >= 3)"),
        trend_tests(ps, "sess_num", ["pulse_logit", "acc100"], "across all sessions (exploratory, includes excluded)"),
        group_tests(h, HISTORY_TERMS + ["rt_after_error_minus_correct"], "trial history")], ignore_index=True)
    het = []
    for m, g in ps_kept.dropna(subset=["pulse_logit"]).groupby("mouse"):
        if len(g) >= 2:
            w = 1 / g.pulse_logit_se**2
            mu = (w * g.pulse_logit).sum() / w.sum()
            het.append({"mouse": m, "n_sessions": len(g), "weighted_mean": mu, "Q": (w * (g.pulse_logit - mu) ** 2).sum(), "df": len(g) - 1})
    het = pd.DataFrame(het)
    from scipy.stats import chi2
    het["p_heterogeneity"] = chi2.sf(het.Q, het.df)
    (OUT / "figures/qc").mkdir(parents=True, exist_ok=True)
    stem = OUT / f"tables/behavior_exploration_{date}"
    for name, df in [("sessions", s), ("provenance", prov), ("task_parameters", tp), ("within_session", ws), ("per_session", ps), ("psychometric", psy),
                     ("chronometric", chrono), ("rt_summary", rts), ("history", h), ("late_choice_accuracy", late), ("tests", tests), ("pulse_heterogeneity", het)]:
        df.to_csv(f"{stem}_{name}.csv", index=False)
    figures(s, ws, ps, psy, chrono, c, h, date)
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(late.round(3).to_string(index=False), prov.to_string(index=False), tp.to_string(index=False), rts.to_string(index=False), h.round(3).to_string(index=False),
          het.round(3).to_string(index=False), tests.round(4).to_string(index=False), sep="\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    main(ap.parse_args().date)
