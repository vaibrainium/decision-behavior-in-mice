"""Package D: pulse-aligned joint response distributions (EXPLORATORY; plan section D).

Two sub-commands, run in order:

  d1   Review the frozen control-alignment rule (A's analysis_config.json, control_alignment) against plan D1 using
       metadata only (onsets, pools, counts; no response outcomes) and write response_time/d1_control_alignment.json.
  run  Requires an accepted D1 file. Estimates cell-standardized cumulative incidence of right and left responses and
       the probability still unresponded versus time since (pseudo-)onset, for two distinct summaries:
         all_scheduled   every scheduled trial; responses before onset are retained as mass at u <= 0
         onset_eligible  trials unresponded immediately before onset (rt >= onset or no response); zero mass at onset
       by onset stratum and arm, with per-mouse curves, pointwise t-intervals across mice, risk counts, contrast
       tables, pseudo-onset seed sensitivity, an independent recomputation check, figures, a diagnostic summary for
       package E, the stage manifest and (only if every check passes) the COMPLETE marker.

Contract (not redefined here): trial sets, strata, censoring and weighting come from package A. Cells are
mouse x session x signed coherence x onset stratum; within a comparison a cell is kept if every compared arm has >= 1
trial and weighted by the minimum arm count, weights normalized to 1 within mouse; mice are averaged equally.
UW asymmetric-schedule cells (signs_scheduled_symmetric False) are excluded everywhere. pulse_type_rt_dependent is
never read. Left is a competing event for right; the only censoring is administrative at 5 s, which lies beyond the
common grid (onset + 4.58 s <= 5 s for every trial), so the empirical cell proportions are complete on the grid.

Hazards / late curve shapes condition on post-treatment survival and late cumulative differences can carry an early
effect forward: nothing here is an unselected memory curve, and the closed confirmatory timing test is not run.

Usage:
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.response_time d1  --run-id <RUN_ID>
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.response_time run --run-id <RUN_ID>
"""

import argparse
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats

from scripts.pulse_followup import io

STAGE = "response_time"
ARMS_ALL = ("positive", "negative", "control")
COMPARISONS = {  # name -> arms (first minus second for pairwise contrasts)
    "pos_vs_neg": ("positive", "negative"),
    "pos_vs_ctrl": ("positive", "control"),
    "ctrl_vs_neg": ("control", "negative"),
    "three_arm": ("positive", "negative", "control"),
}
STRATA = ("early", "middle", "late", "all")
SUMMARIES = ("all_scheduled", "onset_eligible")
KEY_TIMES = (0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.58)
WINDOWS = ((0.0, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 4.58))
TOL = 1e-9


# ----------------------------------------------------------------------------------------------------------- loading
def grid_from(cfg):
    g = cfg["time_grid"]["since_onset_s"]
    n = int(round((g["stop"] - g["start"]) / g["step"])) + 1
    return np.round(g["start"] + g["step"] * np.arange(n), 10)


def base_trials(t):
    """Primary coherence set, sign-symmetric cells, signed arms and controls only."""
    keep = t.in_primary_coherence & t.signs_scheduled_symmetric & t.pulse_category.isin(ARMS_ALL)
    return t.loc[keep].copy()


def aligned(t, cfg, control_col="control_onset_s"):
    """One row per trial: arm, cell keys, onset used for alignment, stratum, side, rt, eligibility.
    Pulses: recorded onset and A's stratum. Controls: UW recorded sham (A); UCLA pseudo-onset from `control_col`,
    stratum re-derived with A's boundaries (identical to A's onset_stratum for the default seed)."""
    b = base_trials(t)
    ctrl = b.pulse_category == "control"
    onset = np.where(ctrl, b[control_col], b.recorded_onset_s)
    stratum = b.onset_stratum.to_numpy(dtype=object).copy()
    ucla_ctrl = (ctrl & (b.rig == "ucla")).to_numpy()
    bounds = cfg["strata"]["ucla_onset_stratum"]["boundaries_s"]
    stratum[ucla_ctrl] = np.array(["early", "middle", "late"])[np.digitize(onset[ucla_ctrl], bounds)]
    out = pd.DataFrame({
        "trial_id": b.trial_id.to_numpy(), "mouse": b.mouse.to_numpy(), "session": b.session.to_numpy(),
        "coherence_pct": b.coherence_pct.to_numpy(), "onset_stratum": stratum, "arm": b.pulse_category.to_numpy(),
        "onset": onset.astype(float), "side": b.response_side.to_numpy(), "rt": b.rt_s.to_numpy(float),
    })
    if out.onset.isna().any():
        raise RuntimeError("trial without an alignment onset in the analysis set")
    out["u"] = out.rt - out.onset  # NaN when unresponded by the deadline
    out["eligible"] = out.rt.isna() | (out.rt >= out.onset)
    return out


# --------------------------------------------------------------------------------------------------------------- D1
def reproduce_pseudo_onsets(t, seed, min_pool):
    """Independent re-implementation of A's documented UCLA pseudo-onset rule (metadata only)."""
    pulses = t[(t.rig == "ucla") & t.pulse_category.isin(["positive", "negative", "null_pulse"]) & t.recorded_onset_s.notna()]
    cell = {k: np.sort(g.recorded_onset_s.to_numpy()) for k, g in pulses.groupby(["session", "abs_coherence_pct"])}
    sess = {k: np.sort(g.recorded_onset_s.to_numpy()) for k, g in pulses.groupby("session")}
    rng = np.random.default_rng(seed)
    res = {}
    for _, r in t[(t.rig == "ucla") & (t.pulse_category == "control")].sort_values("trial_id").iterrows():
        pool = cell.get((r.session, r.abs_coherence_pct), np.array([]))
        if len(pool) < min_pool:
            pool = sess.get(r.session, np.array([]))
        res[r.trial_id] = rng.choice(pool) if len(pool) else np.nan
    return pd.Series(res)


def d1(run_id):
    timer = io.Timer()
    run = io.run_dir(run_id)
    t, cfg = io.load_trials(run)
    out = io.stage_dir(run, STAGE)
    ca, grid = cfg["control_alignment"], grid_from(cfg)
    deadline = cfg["deadline_s"]
    b = base_trials(t)  # metadata columns only are read below
    checks, notes = {}, []

    # rule reproduction and determinism (all UCLA controls, every seed)
    cols = ["control_onset_s"] + [f"control_onset_s_seed{k}" for k in range(1, 6)]
    seeds = [ca["seed"]] + list(ca["sensitivity_seeds"])
    uc = t[(t.rig == "ucla") & (t.pulse_category == "control")].set_index("trial_id")
    repro = {}
    for col, s in zip(cols, seeds):
        r = reproduce_pseudo_onsets(t, s, ca["min_pool"]).reindex(uc.index)
        repro[col] = bool(np.allclose(r.to_numpy(), uc[col].to_numpy(), equal_nan=True, atol=0, rtol=0))
    checks["ucla_pseudo_onsets_reproduced_from_rule_all_seeds"] = repro
    checks["rule_inputs"] = ("session, abs_coherence_pct, pulse_category, recorded_onset_s of scheduled pulses, trial_id order "
                             "and a fixed seed; no response side, RT, event or outcome column")
    rules = b[b.pulse_category == "control"].groupby(["mouse", "control_onset_rule"]).size().rename("n").reset_index()
    checks["control_onset_rule_counts_analysis_set"] = rules.to_dict("records")

    # UW shams
    uwc = b[(b.rig == "uw") & (b.pulse_category == "control")]
    checks["uw_controls_all_have_recorded_sham"] = bool(uwc.sham_onset_recorded.all())
    checks["uw_sham_onsets_equal_pulse_frames"] = sorted(set(np.round(uwc.control_onset_s, 5))) == sorted(
        set(np.round(b[(b.rig == "uw") & (b.pulse_category != "control")].recorded_onset_s, 5)))
    checks["uw_sham_equals_control_onset_s"] = bool(np.allclose(uwc.control_onset_s, uwc.recorded_onset_s))

    # UCLA pool sizes (session x |coh|), analysis-set controls
    up = t[(t.rig == "ucla") & t.pulse_category.isin(["positive", "negative", "null_pulse"]) & t.recorded_onset_s.notna()]
    pool_n = up.groupby(["session", "abs_coherence_pct"]).size()
    ucb = b[(b.rig == "ucla") & (b.pulse_category == "control")]
    used = pool_n.reindex(pd.MultiIndex.from_frame(ucb[["session", "abs_coherence_pct"]])).to_numpy()
    checks["ucla_pool_size_per_control"] = {"min": int(np.nanmin(used)), "median": float(np.nanmedian(used)),
                                            "max": int(np.nanmax(used)), "n_below_min_pool": int((used < ca["min_pool"]).sum())}

    # distribution match: pseudo-onsets vs pulse onsets per mouse x stratum (UCLA); stratum shares per mouse
    rows = []
    for (m, s), g in b[b.rig == "ucla"].groupby(["mouse", "onset_stratum"]):
        pul = g[g.pulse_category != "control"].recorded_onset_s.to_numpy()
        con = g[g.pulse_category == "control"].control_onset_s.to_numpy()
        ks = stats.ks_2samp(pul, con)
        rows.append({"mouse": m, "onset_stratum": s, "n_pulse": len(pul), "n_control": len(con),
                     "mean_pulse_s": pul.mean(), "mean_control_s": con.mean(), "sd_pulse_s": pul.std(ddof=1),
                     "sd_control_s": con.std(ddof=1), "ks_stat": ks.statistic, "ks_p": ks.pvalue})
    dm = pd.DataFrame(rows)
    checks["ucla_onset_distribution_match"] = dm.round(5).to_dict("records")
    checks["ucla_max_abs_mean_diff_ms"] = float(1000 * (dm.mean_pulse_s - dm.mean_control_s).abs().max())
    checks["ucla_max_ks_stat"] = float(dm.ks_stat.max())
    share = []
    for m, g in b[b.rig == "ucla"].groupby("mouse"):
        isp = g.pulse_category != "control"
        share.append({"mouse": m, "frac_early_pulses": float((g[isp].onset_stratum == "early").mean()),
                      "frac_early_controls": float((g[~isp].onset_stratum == "early").mean())})
    checks["ucla_early_share_pulse_vs_control"] = share

    # pre-treatment balance of pseudo-strata (metadata only: trial position in session)
    bal = b[(b.rig == "ucla") & (b.pulse_category == "control")].groupby(["mouse", "onset_stratum"]).position.mean().unstack()
    checks["ucla_control_mean_position_by_pseudo_stratum"] = bal.round(1).reset_index().to_dict("records")

    # three-arm support per mouse x stratum (counts only)
    sup = []
    for (m, s), g in b.assign(stratum=b.onset_stratum).groupby(["mouse", "stratum"]):
        cnt = g.groupby(["session", "coherence_pct", "pulse_category"]).size().unstack(fill_value=0).reindex(columns=list(ARMS_ALL), fill_value=0)
        sup.append({"mouse": m, "rig_schedule": g.rig.iloc[0], "onset_stratum": s,
                    "cells_pos_neg": int(((cnt.positive > 0) & (cnt.negative > 0)).sum()),
                    "cells_pos_ctrl": int(((cnt.positive > 0) & (cnt.control > 0)).sum()),
                    "cells_ctrl_neg": int(((cnt.control > 0) & (cnt.negative > 0)).sum()),
                    "cells_three_arm": int((cnt > 0).all(axis=1).sum()),
                    "n_pos": int(cnt.positive.sum()), "n_neg": int(cnt.negative.sum()), "n_ctrl": int(cnt.control.sum())})
    sp = pd.DataFrame(sup)
    io.write_csv(out / "d1_support.csv", sp)
    checks["support_table"] = "d1_support.csv (mouse x stratum cell and trial counts; counts only)"
    checks["mice_with_three_arm_support_by_stratum"] = sp[sp.cells_three_arm > 0].groupby("onset_stratum").mouse.nunique().to_dict()

    # grid support: every trial followed to onset + grid end
    max_onset = float(np.nanmax(np.where(b.pulse_category == "control", b.control_onset_s, b.recorded_onset_s)))
    seed_max = max(float(np.nanmax(t[c])) for c in cols)
    checks["grid_end_s"] = float(grid[-1])
    checks["max_alignment_onset_s"] = max(max_onset, seed_max)
    checks["grid_within_followup"] = bool(max(max_onset, seed_max) + grid[-1] <= deadline + 1e-12)

    ok = (all(repro.values()) and checks["uw_controls_all_have_recorded_sham"] and checks["uw_sham_onsets_equal_pulse_frames"]
          and checks["ucla_pool_size_per_control"]["n_below_min_pool"] == 0 and checks["grid_within_followup"]
          and checks["ucla_max_abs_mean_diff_ms"] < 15 and dm.ks_stat.max() < 0.2)
    notes += [
        "UW: recorded scheduled sham onsets (preferred by D1) are used; they take the same three frames as pulses.",
        "UCLA: no sham exists; one pseudo-onset per control drawn with a fixed seed from the recorded (applied) onsets of "
        "scheduled pulses in the same mouse x session x |coherence| (D1 says 'coherence'; pooling signed coherences is "
        "accepted because UCLA assigns bursts within coherence blocks independent of sign and onset timing is drawn "
        "independently of coherence). Rule reproduced exactly from metadata; it reads no outcome.",
        "The pool contains applied pulse times (scheduled draw + stimulus-loop latency), i.e. the same quantity used to "
        "align pulse trials, so pseudo-onsets match the pulse alignment rather than the unlogged scheduled draw.",
        "Every UCLA (pseudo-)onset is <= 0.302 s, essentially at the 0.3 s minimum viewing time, so UCLA has no pre-onset "
        "responses; only UW late (0.417 s) carries pre-onset mass. Pseudo-onset stratum is random for each control.",
        "Pseudo-onset seeds 1-5 are a sensitivity only, never pooled as extra observations.",
        "Time grid: A's since_onset_s grid 0..4.58 s, step 0.01 s, accepted unchanged; it lies inside every trial's "
        "follow-up (5 s - onset), so no administrative censoring occurs on the grid and one common range is used for "
        "every comparison.",
        "Distribution-match thresholds (|mean diff| < 15 ms, KS < 0.2 per mouse x stratum) were set by this worker before "
        "running the check; KS p-values are descriptive.",
    ]
    rec = {"accepted": bool(ok), "run_id": run_id, "config_version": cfg["config_version"],
           "rule": ca, "time_grid": {**cfg["time_grid"]["since_onset_s"], "n_points": len(grid), "common_range_s": [0.0, float(grid[-1])]},
           "checks": checks, "notes": notes, "runtime_seconds": timer.seconds,
           "code_sha256": io.sha256_file(__file__)}
    io.write_json(out / "d1_control_alignment.json", rec)
    print(json.dumps({k: rec[k] for k in ("accepted", "time_grid")}, indent=1))
    print("max |mean diff| ms", checks["ucla_max_abs_mean_diff_ms"], "max KS", checks["ucla_max_ks_stat"])
    return rec


# --------------------------------------------------------------------------------------------------------- estimator
def cell_weights(a, arms):
    """Per-trial weights w_cell / n_cell_arm under A's rule, for the trials of `a` in `arms`."""
    a = a[a.arm.isin(arms)]
    key = ["mouse", "session", "coherence_pct", "onset_stratum"]
    cnt = a.groupby(key + ["arm"]).size().unstack(fill_value=0).reindex(columns=list(arms), fill_value=0)
    cnt = cnt[(cnt > 0).all(axis=1)]
    w = cnt.min(axis=1).astype(float)
    w = w / w.groupby(level="mouse").transform("sum")
    a = a.merge(w.rename("w_cell").reset_index(), on=key, how="inner")
    n = a.groupby(key + ["arm"]).trial_id.transform("size")
    a["wt"] = a.w_cell / n
    a["cell"] = a[key].astype(str).agg("|".join, axis=1)
    return a


def curves_for(a, grid):
    """Weighted CIF_R, CIF_L, independently computed survival and unweighted risk counts on the grid, one trial set."""
    u = a.u.to_numpy()
    resp = ~np.isnan(u)
    res = {}
    for side in ("R", "L"):
        m = resp & (a.side.to_numpy() == side)
        order = np.argsort(u[m])
        us, ws = u[m][order], a.wt.to_numpy()[m][order]
        cs = np.concatenate([[0.0], np.cumsum(ws)])
        res[f"cif_{side}"] = cs[np.searchsorted(us, grid, side="right")]
    # survival by direct indicator sum (separate code path from the CIFs)
    still = ~resp[None, :] | (u[None, :] > grid[:, None])
    res["survival"] = (still * a.wt.to_numpy()[None, :]).sum(axis=1)
    res["n_at_risk"] = still.sum(axis=1)
    return res


def estimate(al, grid, summary, comparison, stratum):
    """Per-mouse curves for one (summary, comparison, stratum). Returns (curves df, eligibility rows)."""
    arms = COMPARISONS[comparison]
    a = al[al.eligible] if summary == "onset_eligible" else al
    if stratum != "all":
        a = a[a.onset_stratum == stratum]
    a = cell_weights(a, arms)
    rows, elig = [], []
    for (m, arm), g in a.groupby(["mouse", "arm"]):
        c = curves_for(g, grid)
        rows.append(pd.DataFrame({"mouse": m, "arm": arm, "t": grid, **c}))
        elig.append({"summary": summary, "comparison": comparison, "onset_stratum": stratum, "mouse": m, "arm": arm,
                     "n_trials": len(g), "n_cells": g.cell.nunique(), "weight_sum": g.wt.sum()})
    if not rows:
        return pd.DataFrame(), pd.DataFrame(elig)
    return pd.concat(rows, ignore_index=True), pd.DataFrame(elig)


def contrast_curves(cur, comparison):
    """Per-mouse contrast curves. Pairwise: first arm minus second. three_arm: direction (pos - neg)/2 and the common
    effect of both pulse signs vs control."""
    p = cur.pivot_table(index=["mouse", "t"], columns="arm", values=["cif_R", "cif_L", "survival"])
    out = pd.DataFrame(index=p.index)
    if comparison == "three_arm":
        a, b = "positive", "negative"
    else:
        a, b = COMPARISONS[comparison]
    dR = p["cif_R"][a] - p["cif_R"][b]
    dL = p["cif_L"][a] - p["cif_L"][b]
    out["d_cif_R"], out["d_cif_L"], out["d_survival"] = dR, dL, p["survival"][a] - p["survival"][b]
    out["d_direction"] = (dR - dL) / 2
    if comparison == "three_arm":
        for k in ("cif_R", "cif_L", "survival"):
            out[f"common_{k}"] = (p[k]["positive"] + p[k]["negative"]) / 2 - p[k]["control"]
        out["common_responded"] = -out["common_survival"]
    return out.reset_index()


def tci(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 2:
        return n, (x.mean() if n else np.nan), np.nan, np.nan, np.nan
    m, s = x.mean(), x.std(ddof=1)
    h = stats.t.ppf(0.975, n - 1) * s / np.sqrt(n)
    return n, m, s, m - h, m + h


def rmst(t, s):
    return float(np.trapezoid(s, t)) if hasattr(np, "trapezoid") else float(np.trapz(s, t))


# ------------------------------------------------------------------------------------------------------------- run
def run(run_id):
    timer = io.Timer()
    run_path = io.run_dir(run_id)
    t, cfg = io.load_trials(run_path)
    out = io.stage_dir(run_path, STAGE)
    d1p = out / "d1_control_alignment.json"
    if not d1p.exists():
        raise RuntimeError("run `d1` first")
    d1rec = json.loads(d1p.read_text())
    grid = grid_from(cfg)
    accepted = d1rec["accepted"]
    comps = list(COMPARISONS) if accepted else ["pos_vs_neg"]
    checks = {}

    al = aligned(t, cfg)
    b = base_trials(t)
    checks["default_seed_ucla_control_strata_match_A"] = bool(
        (al.set_index("trial_id").onset_stratum.reindex(b.trial_id).to_numpy() == b.onset_stratum.to_numpy()).all())
    checks["no_asymmetric_cells"] = bool(t.set_index("trial_id").loc[al.trial_id, "signs_scheduled_symmetric"].all())
    checks["grid_within_followup"] = bool((al.onset + grid[-1] <= cfg["deadline_s"] + 1e-12).all())

    all_cur, all_elig, all_con = [], [], []
    for summ in SUMMARIES:
        for comp in comps:
            for st in STRATA:
                cur, el = estimate(al, grid, summ, comp, st)
                if cur.empty:
                    continue
                meta = {"analysis_set": "primary_coherence", "comparison": comp, "onset_stratum": st, "summary": summ, "control_seed": "default"}
                all_cur.append(cur.assign(**meta))
                all_elig.append(el)
                all_con.append(contrast_curves(cur, comp).assign(**meta))
    cur = pd.concat(all_cur, ignore_index=True)
    elig = pd.concat(all_elig, ignore_index=True)
    con = pd.concat(all_con, ignore_index=True)
    rig_of = t.groupby("mouse").rig.first()

    # ---- checks on per-mouse curves
    gkeys = ["summary", "comparison", "onset_stratum", "arm", "mouse"]
    srt = cur.sort_values(gkeys + ["t"])
    dif = srt.groupby(gkeys)[["cif_R", "cif_L"]].diff()
    checks["cif_nondecreasing"] = bool((dif.fillna(0) >= -TOL).all().all())
    checks["risk_nonincreasing"] = bool((srt.groupby(gkeys).n_at_risk.diff().fillna(0) <= 0).all())
    pr = cur[["cif_R", "cif_L", "survival"]].to_numpy()
    checks["probabilities_in_0_1"] = bool(((pr >= -TOL) & (pr <= 1 + TOL)).all())
    checks["max_abs_sum_error"] = float(np.abs(cur.cif_R + cur.cif_L + cur.survival - 1).max())
    checks["cif_R_plus_cif_L_plus_survival_eq_1"] = checks["max_abs_sum_error"] < TOL
    e0 = cur[(cur.summary == "onset_eligible") & (cur.t == 0)]
    checks["onset_eligible_zero_mass_at_onset_max"] = float((e0.cif_R + e0.cif_L).max())
    checks["onset_eligible_zero_mass_at_onset"] = checks["onset_eligible_zero_mass_at_onset_max"] <= TOL
    checks["weights_sum_to_1_per_mouse_arm"] = bool(np.allclose(elig.weight_sum, 1.0))

    # all-scheduled CIF(0) equals the weighted pre-onset response fraction (independent of the searchsorted path)
    a0 = cell_weights(al, COMPARISONS["pos_vs_neg"])
    a0 = a0.assign(pre=(a0.rt < a0.onset).astype(float) * a0.wt).groupby(["mouse", "arm"]).pre.sum()
    c0 = cur[(cur.summary == "all_scheduled") & (cur.comparison == "pos_vs_neg") & (cur.onset_stratum == "all") & (cur.t == 0)]
    c0 = (c0.set_index(["mouse", "arm"]).cif_R + c0.set_index(["mouse", "arm"]).cif_L).reindex(a0.index)
    checks["all_scheduled_cif0_equals_pre_onset_fraction"] = bool(np.allclose(c0, a0, atol=1e-12))

    # ---- group curves (mean across mice) and pointwise t-intervals
    grp_rows = []
    for k, g in cur.groupby(["summary", "comparison", "onset_stratum", "arm", "t"]):
        r = dict(zip(["summary", "comparison", "onset_stratum", "arm", "t"], k))
        for v in ("cif_R", "cif_L", "survival"):
            n, m, s, lo, hi = tci(g[v])
            r.update({v: m, f"{v}_ci_low": lo, f"{v}_ci_high": hi})
        r.update({"n_mice": len(g), "n_at_risk": int(g.n_at_risk.sum())})
        grp_rows.append(r)
    grp = pd.DataFrame(grp_rows)
    checks["group_cif_R_plus_cif_L_plus_survival_eq_1"] = bool(np.abs(grp.cif_R + grp.cif_L + grp.survival - 1).max() < TOL)

    ccols = [c for c in con.columns if c.startswith(("d_", "common_"))]
    gc_rows = []
    for k, g in con.groupby(["summary", "comparison", "onset_stratum", "t"]):
        r = dict(zip(["summary", "comparison", "onset_stratum", "t"], k))
        for v in ccols:
            if g[v].notna().any():
                n, m, s, lo, hi = tci(g[v])
                r.update({v: m, f"{v}_ci_low": lo, f"{v}_ci_high": hi, "n_mice": n})
        gc_rows.append(r)
    gcon = pd.DataFrame(gc_rows)

    # ---- key-time, window and RMST contrast table (per mouse and group)
    def summarize(con_df, seed_label):
        rows = []
        for (summ, comp, st), g in con_df.groupby(["summary", "comparison", "onset_stratum"]):
            vs = [c for c in ccols if c in g and g[c].notna().any()]
            per = []
            for m, gm in g.groupby("mouse"):
                gm = gm.set_index("t")
                rec = {"mouse": m}
                for kt in KEY_TIMES:
                    for v in vs:
                        rec[f"{v}@{kt:g}"] = gm.loc[kt, v]
                for lo, hi in WINDOWS:
                    for v in ("d_direction", "d_survival") + (("common_survival",) if comp == "three_arm" else ()):
                        rec[f"{v}_window_{lo:g}-{hi:g}"] = gm.loc[hi, v] - gm.loc[lo, v]
                surv_col = "common_survival" if comp == "three_arm" else "d_survival"
                rec[f"rmst_{surv_col}_s"] = rmst(gm.index.to_numpy(), gm[surv_col].to_numpy())
                per.append(rec)
            per = pd.DataFrame(per)
            for col in per.columns.drop("mouse"):
                for _, pm in per.iterrows():
                    rows.append({"summary": summ, "comparison": comp, "onset_stratum": st, "control_seed": seed_label,
                                 "quantity": col, "mouse": pm.mouse, "rig_schedule": rig_of[pm.mouse], "estimate": pm[col]})
                n, m, s, lo, hi = tci(per[col])
                rows.append({"summary": summ, "comparison": comp, "onset_stratum": st, "control_seed": seed_label,
                             "quantity": col, "mouse": "group_mean", "rig_schedule": "", "estimate": m, "sd": s,
                             "n_mice": n, "ci_low": lo, "ci_high": hi,
                             "method": "pointwise two-sided 95% Student-t across mice (df = n_mice - 1); no multiplicity correction; descriptive"})
        return pd.DataFrame(rows)

    table = summarize(con, "default")

    # ---- pseudo-onset seed sensitivity (UCLA controls only change)
    seed_tabs = []
    if accepted:
        for k in range(1, 6):
            als = aligned(t, cfg, f"control_onset_s_seed{k}")
            cs = []
            for summ in SUMMARIES:
                for comp in ("pos_vs_ctrl", "ctrl_vs_neg", "three_arm"):
                    for st in STRATA:
                        c_, _ = estimate(als, grid, summ, comp, st)
                        if not c_.empty:
                            cs.append(contrast_curves(c_, comp).assign(summary=summ, comparison=comp, onset_stratum=st))
            seed_tabs.append(summarize(pd.concat(cs, ignore_index=True), f"seed{k}"))
    seed_tab = pd.concat(seed_tabs, ignore_index=True) if seed_tabs else pd.DataFrame()

    # ---- risk counts at key times (summed across mice) and eligibility
    risk = cur[cur.t.isin(KEY_TIMES)].groupby(["summary", "comparison", "onset_stratum", "arm", "t"]).agg(
        n_at_risk=("n_at_risk", "sum"), n_mice=("mouse", "nunique")).reset_index()
    elig_sum = elig.groupby(["summary", "comparison", "onset_stratum", "arm"]).agg(
        n_mice=("mouse", "nunique"), n_trials=("n_trials", "sum"), n_cells=("n_cells", "sum")).reset_index()

    # ---- independent recomputation (simpler code path): onset-eligible pos_vs_neg pooled strata, d_direction at 1 s
    ind = independent_check(t, cfg, u_check=1.0)
    main = table[(table.summary == "onset_eligible") & (table.comparison == "pos_vs_neg") & (table.onset_stratum == "all")
                 & (table.quantity == "d_direction@1") & (table.mouse != "group_mean")].set_index("mouse").estimate
    checks["independent_recomputation_max_abs_diff"] = float((main - ind.reindex(main.index)).abs().max())
    checks["independent_recomputation_matches"] = checks["independent_recomputation_max_abs_diff"] < 1e-12 and set(main.index) == set(ind.index)

    # ---- write outputs
    curves_out = pd.concat([
        cur.assign(mouse=cur.mouse),
        grp.assign(mouse="group_mean", analysis_set="primary_coherence", control_seed="default"),
    ], ignore_index=True)
    schema_cols = cfg["output_schema"]["curves"]
    extra = ["summary", "control_seed", "n_mice"] + [c for c in grp.columns if c.endswith(("_ci_low", "_ci_high"))]
    curves_out = curves_out[schema_cols + extra]
    outputs = []
    outputs.append(io.write_csv(out / "curves.csv.gz", curves_out, compression="gzip"))
    outputs.append(io.write_csv(out / "contrast_curves_per_mouse.csv.gz", con, compression="gzip"))
    outputs.append(io.write_csv(out / "contrast_curves_group.csv.gz", gcon, compression="gzip"))
    outputs.append(io.write_csv(out / "contrast_table.csv", table))
    if not seed_tab.empty:
        outputs.append(io.write_csv(out / "contrast_table_seed_sensitivity.csv", seed_tab))
    outputs.append(io.write_csv(out / "risk_counts.csv", risk))
    outputs.append(io.write_csv(out / "eligibility_per_mouse.csv", elig))
    outputs.append(io.write_csv(out / "eligibility_summary.csv", elig_sum))

    diag = diagnostic_summary(table, seed_tab, elig_sum, grp)
    outputs.append(io.write_json(out / "diagnostic_summary_for_E.json", diag))
    outputs += make_figures(run_id, grp, con, gcon)

    checks_bool = {k: v for k, v in checks.items() if isinstance(v, bool)}
    passed = all(checks_bool.values())
    print(json.dumps(checks, indent=1))
    inputs = {"trial_table": cfg["hashes"]["trial_table"], "analysis_config": io.sha256_file(run_path / "data" / "analysis_config.json"),
              "d1_control_alignment": io.sha256_file(d1p)}
    man = io.stage_manifest(STAGE, " ".join(["PYTHONDONTWRITEBYTECODE=1", ".venv/bin/python", "-B", "-m", "scripts.pulse_followup.response_time"] + sys.argv[1:]),
                            inputs, outputs + [d1p, out / "d1_support.csv"], checks, timer.seconds,
                            extra={"run_id": run_id, "d1_accepted": accepted, "status": "exploratory",
                                   "code_sha256_response_time": io.sha256_file(__file__)})
    io.mark_complete(out, man, passed)
    return passed


def independent_check(t, cfg, u_check):
    """Plain loop over cells, no shared helpers: onset-eligible, pos vs neg, all strata, d_direction at u_check."""
    res = {}
    keep = t.in_primary_coherence & t.signs_scheduled_symmetric & t.pulse_category.isin(["positive", "negative"])
    d = t[keep]
    d = d[d.rt_s.isna() | (d.rt_s >= d.recorded_onset_s)]
    for m, dm in d.groupby("mouse"):
        tot_w, acc = 0.0, 0.0
        cells = []
        for _, dc in dm.groupby(["session", "coherence_pct", "onset_stratum"]):
            pos, neg = dc[dc.pulse_category == "positive"], dc[dc.pulse_category == "negative"]
            if len(pos) and len(neg):
                cells.append((min(len(pos), len(neg)), pos, neg))
        tot_w = sum(c[0] for c in cells)
        for w, pos, neg in cells:
            def p(x, side):
                hit = (x.response_side == side) & (x.rt_s <= x.recorded_onset_s + u_check)
                return hit.mean()
            acc += (w / tot_w) * ((p(pos, "R") - p(neg, "R")) - (p(pos, "L") - p(neg, "L"))) / 2
        res[m] = acc
    return pd.Series(res)


# --------------------------------------------------------------------------------------------- diagnostic summary
def diagnostic_summary(table, seed_tab, elig_sum, grp):
    g = table[table.mouse == "group_mean"]

    def pick(summary, comp, st, q):
        r = g[(g.summary == summary) & (g.comparison == comp) & (g.onset_stratum == st) & (g.quantity == q)]
        if r.empty:
            return None
        r = r.iloc[0]
        return {"estimate": r.estimate, "ci_low": r.ci_low, "ci_high": r.ci_high, "n_mice": int(r.n_mice)}

    out = {"status": "EXPLORATORY; pointwise 95% t-intervals across mice, no multiplicity correction; 10 mice (6 for late)",
           "units": "probability (multiply by 100 for percentage points); RMST differences in seconds over 0-4.58 s since onset",
           "sign_convention": "d_* = first arm minus second; positive = rightward pulse; d_direction = (dR - dL)/2; "
                              "common_* = mean(positive, negative) minus control (three-arm common support)",
           "direction": {}, "common_effect": {}, "window_increments": {}, "rmst": {}, "seed_sensitivity_range": {},
           "caveats": ["Hazard and late-curve shapes condition on post-treatment survival; late cumulative differences can "
                       "carry an earlier effect forward. Not an unselected memory curve.",
                       "Late stratum exists only in the UW schedule (6 mice); this is a schedule fact, not a rig comparison.",
                       "Closed confirmatory timing/primacy test not run."]}
    for summ in SUMMARIES:
        for st in STRATA:
            key = f"{summ}/{st}"
            out["direction"][key] = {f"u={kt:g}": pick(summ, "pos_vs_neg", st, f"d_direction@{kt:g}") for kt in (0.3, 0.5, 1.0, 2.0, 4.58)}
            out["common_effect"][key] = {f"responded_u={kt:g}": pick(summ, "three_arm", st, f"common_responded@{kt:g}") for kt in (0.3, 0.5, 1.0, 2.0, 4.58)}
            out["window_increments"][key] = {f"{lo:g}-{hi:g}": pick(summ, "pos_vs_neg", st, f"d_direction_window_{lo:g}-{hi:g}") for lo, hi in WINDOWS}
            out["rmst"][key] = {"pos_minus_neg_d_survival_s": pick(summ, "pos_vs_neg", st, "rmst_d_survival_s"),
                                "common_survival_s": pick(summ, "three_arm", st, "rmst_common_survival_s")}
    if not seed_tab.empty:
        sg = seed_tab[seed_tab.mouse == "group_mean"]
        for q in ("common_responded@4.58", "rmst_common_survival_s", "d_direction@4.58"):
            for summ in SUMMARIES:
                for comp in ("three_arm", "pos_vs_ctrl", "ctrl_vs_neg"):
                    r = sg[(sg.summary == summ) & (sg.comparison == comp) & (sg.onset_stratum == "all") & (sg.quantity == q)]
                    if len(r):
                        out["seed_sensitivity_range"][f"{summ}/{comp}/all/{q}"] = [float(r.estimate.min()), float(r.estimate.max())]
    out["eligibility"] = elig_sum.to_dict("records")
    return out


# ---------------------------------------------------------------------------------------------------------- figures
def make_figures(run_id, grp, con, gcon):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fdir = io.figure_dir(run_id)
    colors = {"positive": "#D55E00", "negative": "#0072B2", "control": "#555555"}
    styles = {"positive": "-", "negative": "--", "control": ":"}
    paths = []
    strata = ("early", "middle", "late")
    for summ in SUMMARIES:
        # joint curves: three-arm common support
        fig, axes = plt.subplots(3, 3, figsize=(10, 8), sharex=True, sharey="row", layout="constrained")
        for j, st in enumerate(strata):
            for i, (v, lab) in enumerate((("cif_R", "P(right response by onset+u)"), ("cif_L", "P(left response by onset+u)"),
                                          ("survival", "P(still unresponded)"))):
                ax = axes[i, j]
                for arm in ARMS_ALL:
                    g = grp[(grp.summary == summ) & (grp.comparison == "three_arm") & (grp.onset_stratum == st) & (grp.arm == arm)]
                    if g.empty:
                        continue
                    ax.plot(g.t, g[v], styles[arm], color=colors[arm], lw=1.4, label=f"{arm} (n={int(g.n_mice.iloc[0])} mice)")
                    ax.fill_between(g.t, g[f"{v}_ci_low"], g[f"{v}_ci_high"], color=colors[arm], alpha=0.15, lw=0)
                if i == 0:
                    ax.set_title(f"{st} onset")
                if j == 0:
                    ax.set_ylabel(lab)
                if i == 2:
                    ax.set_xlabel("time since (pseudo-)onset u (s)")
                ax.set_ylim(-0.02, 1.02)
        axes[0, 0].legend(fontsize=7, frameon=False)
        fig.suptitle(f"{summ.replace('_', ' ')}: cell-standardized joint response curves, |coh| <= 36%, three-arm common support\n"
                     "lines = mean of per-mouse curves; bands = pointwise 95% t-interval across mice (EXPLORATORY)", fontsize=9)
        paths.append(io.savefig(fig, fdir / f"response_time_joint_curves_{summ}.png", dpi=200))
        plt.close(fig)

        # contrasts: direction (pos vs neg) and common response effect (three-arm), per-mouse lines + group
        fig, axes = plt.subplots(2, 4, figsize=(12, 6), sharex=True, sharey="row", layout="constrained")
        for j, st in enumerate(strata + ("all",)):
            for i, (comp, v, lab) in enumerate((("pos_vs_neg", "d_direction", "directional contrast (dR - dL)/2, pos - neg"),
                                                ("three_arm", "common_responded", "common effect on P(responded):\nmean(pos, neg) - control"))):
                ax = axes[i, j]
                pm = con[(con.summary == summ) & (con.comparison == comp) & (con.onset_stratum == st)]
                for _, gm in pm.groupby("mouse"):
                    ax.plot(gm.t, 100 * gm[v], color="#999999", lw=0.6, alpha=0.8)
                gg = gcon[(gcon.summary == summ) & (gcon.comparison == comp) & (gcon.onset_stratum == st)]
                if not gg.empty:
                    ax.plot(gg.t, 100 * gg[v], color="k", lw=1.6, label="mean across mice")
                    ax.fill_between(gg.t, 100 * gg[f"{v}_ci_low"], 100 * gg[f"{v}_ci_high"], color="k", alpha=0.15, lw=0,
                                    label="pointwise 95% t-interval")
                    ax.set_title(f"{st} onset (n={int(gg.n_mice.max())} mice)", fontsize=9)
                ax.axhline(0, color="k", lw=0.5)
                if j == 0:
                    ax.set_ylabel(lab + " (pp)", fontsize=8)
                if i == 1:
                    ax.set_xlabel("time since (pseudo-)onset u (s)")
        axes[0, 0].legend(fontsize=7, frameon=False)
        fig.suptitle(f"{summ.replace('_', ' ')}: pulse contrasts vs time since onset (grey = individual mice). EXPLORATORY; "
                     "late cumulative values carry earlier effects forward", fontsize=9)
        paths.append(io.savefig(fig, fdir / f"response_time_contrasts_{summ}.png", dpi=200))
        plt.close(fig)
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["d1", "run"])
    ap.add_argument("--run-id", required=True, help="coordinator run ID, e.g. 20261023T191030Z_fa8de8b")
    a = ap.parse_args(argv)
    if a.command == "d1":
        d1(a.run_id)
    else:
        ok = run(a.run_id)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
