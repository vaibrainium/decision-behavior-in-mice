"""Package C: directional behavioural effects of scheduled pulses (exploratory; plan section C).

Uses only the frozen package-A contract (io.load_trials). Nothing here redefines trial sets, strata, censoring,
weighting or estimands; it applies them.

Estimands (cfg["estimands"]). For each mouse, within cells mouse x session x coherence_pct x onset_stratum that hold
>= 1 trial in each arm, with cell weights min(n_a, n_b) normalized to 1 within the mouse:
    Delta_X = sum_cells w * (P(X by 5 s | arm a) - P(X by 5 s | arm b)),  X in {R, L, none}
    Delta_direction = (Delta_R - Delta_L) / 2   (percentage points; primary endpoint)
Unresponded ('none') trials are retained as unresponded at the deadline; responses before the scheduled onset are
retained (assignment analysis). pulse_category is the scheduled label; pulse_type_rt_dependent is never read.
Group: unweighted mean over mice; primary interval two-sided 95% Student-t (df = n - 1); sensitivities: mouse
bootstrap (percentile, cfg bootstrap_resamples, seed = cfg control_alignment seed, the contract's master seed; the
config declares no separate bootstrap seed), leave-one-mouse-out.
Holm family (cfg inference.multiplicity): primary Delta_direction (positive vs negative), positive vs timing-matched
control, timing-matched control vs negative. p values: two-sided one-sample t test of per-mouse Delta_direction = 0.

Robustness checks DECLARED HERE BEFORE ANY EFFECT WAS COMPUTED (C3):
  * analysis sets: all coherences, zero coherence (contract sensitivities); the |coherence| = 100 cells are also
    described separately (genuine pulse vs null pulse where both exist), signed toward the genuine pulse direction.
  * leave-one-mouse-out group estimates.
  * session stability, by chronological session order. Order = integer prefix of session_id (session folder number;
    idx_session is lexicographic within mouse and is NOT chronological). For a mouse with k >= 2 sessions: first half
    = first floor(k/2) sessions, second half = last floor(k/2) sessions; the middle session of an odd k is omitted.
    Mice with one session are not estimable for this split. Cells stay within session, so the contract cells and
    weights are unchanged; only the subset of sessions differs.
  * within-session stability, all mice: first vs second half of each session by trial position
    (position < n_in_session / 2), which splits each contract cell by a pre-treatment variable.
  * matched seeds: cells mouse x seed x coherence_pct (pooled over sessions and onset strata) with both signs on the
    same stimulus seed; only where such matches exist (in this design: no UW mouse has them). Seeds and sessions are
    not independent units; the group interval is still across mice. Reported next to the standard-cell estimate for the
    same mice (a methods comparison, not a subgroup finding).
  * optional secondary: responder-only choice contrasts (cell-standardized P(R | responded) difference and a per-mouse
    logistic regression with cell fixed effects), always next to the response-probability contrasts. They condition
    on responding, which the pulse can affect (selection caveat).
C4 pulse vs control: cells use control onset_stratum (UW recorded sham; UCLA pseudo-onset), restricted to
signs_scheduled_symmetric. Runs only if package D's D1 file accepts the control alignment. Pseudo-onset sensitivity
seeds are reported as a sensitivity (strata re-derived from control_onset_s_seed<k> with the contract boundaries),
never as extra observations.

Usage:
    python -B -m scripts.pulse_followup.behaviour --run-id 20261023T191030Z_fa8de8b
    python -B -m scripts.pulse_followup.behaviour --run-id <id> --scratch <dir>   # test run, no COMPLETE marker
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from scripts.pulse_followup import io

STAGE = "behaviour"
SIDES = ("R", "L", "none")
CELL = ["mouse", "session", "coherence_pct", "onset_stratum"]
SETS = {"primary_coherence": "in_primary_coherence", "sensitivity_all_coherences": "in_all_coherences",
        "sensitivity_zero_coherence": "in_zero_coherence"}
SIGNED = ("positive", "negative")
TOL = 1e-12


# ----------------------------------------------------------------------------------------------------------------
# core estimator
# ----------------------------------------------------------------------------------------------------------------
def cell_table(d, arm_a, arm_b, cell_cols):
    """Per-cell counts by arm and response side, the support flag and the normalized within-mouse weight."""
    d = d[d.arm.isin([arm_a, arm_b])]
    cnt = d.groupby(cell_cols + ["arm", "response_side"]).size().unstack("response_side", fill_value=0)
    for s in SIDES:
        if s not in cnt:
            cnt[s] = 0
    cnt = cnt[list(SIDES)]
    cnt["n"] = cnt.sum(axis=1)
    wide = cnt.unstack("arm", fill_value=0)
    wide.columns = [f"{a}__{s}" for s, a in wide.columns]
    for a in (arm_a, arm_b):
        for s in list(SIDES) + ["n"]:
            if f"{a}__{s}" not in wide:
                wide[f"{a}__{s}"] = 0
    wide = wide.reset_index()
    wide["supported"] = (wide[f"{arm_a}__n"] > 0) & (wide[f"{arm_b}__n"] > 0)
    wide["w_raw"] = np.where(wide.supported, np.minimum(wide[f"{arm_a}__n"], wide[f"{arm_b}__n"]), 0)
    tot = wide.groupby("mouse").w_raw.transform("sum")
    wide["w"] = np.where(tot > 0, wide.w_raw / tot.replace(0, np.nan), 0.0)
    for a in (arm_a, arm_b):
        for s in SIDES:
            wide[f"p_{a}_{s}"] = np.where(wide[f"{a}__n"] > 0, wide[f"{a}__{s}"] / wide[f"{a}__n"].replace(0, np.nan), np.nan)
    return wide


def per_mouse(d, arm_a, arm_b, cell_cols=CELL, analysis_set="", contrast=""):
    """Per-mouse standardized contrasts (percentage points), schema per cfg output_schema.per_mouse_table."""
    w = cell_table(d, arm_a, arm_b, cell_cols)
    rig = d.groupby("mouse").rig.first()
    rows = []
    for mouse, c in w.groupby("mouse"):
        s = c[c.supported]
        if s.empty:
            continue
        row = {"analysis_set": analysis_set, "contrast": contrast, "mouse": mouse, "rig": rig[mouse],
               "n_cells": len(s), "n_trials_pos": int(s[f"{arm_a}__n"].sum()), "n_trials_neg": int(s[f"{arm_b}__n"].sum())}
        for side, name in zip(SIDES, ("Delta_R", "Delta_L", "Delta_unresponded")):
            row[name] = 100 * float((s.w * (s[f"p_{arm_a}_{side}"] - s[f"p_{arm_b}_{side}"])).sum())
        row["Delta_direction"] = (row["Delta_R"] - row["Delta_L"]) / 2
        row.update({"arm_a": arm_a, "arm_b": arm_b, "weight_sum": float(s.w.sum()), "effective_pairs": int(s.w_raw.sum()),
                    "n_cells_total": len(c)})
        for side in SIDES:  # standardized arm probabilities, for display
            row[f"P_{side}_a"] = 100 * float((s.w * s[f"p_{arm_a}_{side}"]).sum())
            row[f"P_{side}_b"] = 100 * float((s.w * s[f"p_{arm_b}_{side}"]).sum())
        rows.append(row)
    return pd.DataFrame(rows), w


def t_summary(x):
    x = np.asarray(x, float)
    n = len(x)
    m = float(x.mean())
    if n < 2:
        return n, m, np.nan, np.nan, np.nan, np.nan
    se = x.std(ddof=1) / np.sqrt(n)
    q = stats.t.ppf(0.975, n - 1)
    p = float(stats.ttest_1samp(x, 0.0).pvalue) if se > 0 else np.nan
    return n, m, m - q * se, m + q * se, p, float(x.std(ddof=1))


def group_rows(pm, analysis_set, contrast, endpoints=("Delta_direction", "Delta_R", "Delta_L", "Delta_unresponded"),
               rng_seed=None, n_boot=0, method_prefix=""):
    """Group table rows (schema cfg output_schema.group_table plus endpoint/sd columns)."""
    rows = []
    for ep in endpoints:
        x = pm[ep].to_numpy()
        n, m, lo, hi, p, sd = t_summary(x)
        rows.append({"analysis_set": analysis_set, "contrast": contrast, "n_mice": n, "estimate": m, "ci_low": lo,
                     "ci_high": hi, "method": f"{method_prefix}student_t_95_across_mice", "p_value": p, "p_holm": np.nan,
                     "endpoint": ep, "sd_across_mice": sd, "dz": m / sd if sd and sd > 0 else np.nan})
        if n_boot and n >= 2:
            rng = np.random.default_rng(rng_seed)
            idx = rng.integers(0, n, size=(n_boot, n))
            bm = x[idx].mean(axis=1)
            rows.append({"analysis_set": analysis_set, "contrast": contrast, "n_mice": n, "estimate": m,
                         "ci_low": float(np.percentile(bm, 2.5)), "ci_high": float(np.percentile(bm, 97.5)),
                         "method": f"{method_prefix}mouse_bootstrap_percentile_{n_boot}_seed{rng_seed}", "p_value": np.nan,
                         "p_holm": np.nan, "endpoint": ep, "sd_across_mice": sd, "dz": np.nan})
    return rows


def holm(pvals):
    """Holm step-down adjusted p values for a dict name -> p (NaN entries are skipped)."""
    items = sorted([(p, k) for k, p in pvals.items() if np.isfinite(p)])
    m = len(items)
    out, running = {}, 0.0
    for i, (p, k) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


# ----------------------------------------------------------------------------------------------------------------
# independent check: explicit loops, no pandas groupby
# ----------------------------------------------------------------------------------------------------------------
def independent_primary(t):
    """Recompute the primary group Delta_direction with plain dictionaries and loops."""
    counts = {}
    cols = ["mouse", "session", "coherence_pct", "onset_stratum", "pulse_category", "response_side", "in_primary_coherence"]
    for mouse, session, coh, stratum, cat, side, flag in t[cols].itertuples(index=False, name=None):
        if not flag or cat not in ("positive", "negative"):
            continue
        key = (mouse, session, coh, stratum)
        c = counts.setdefault(key, {"positive": {"R": 0, "L": 0, "none": 0}, "negative": {"R": 0, "L": 0, "none": 0}})
        c[cat][side] += 1
    by_mouse = {}
    for key, c in counts.items():
        npos, nneg = sum(c["positive"].values()), sum(c["negative"].values())
        if npos == 0 or nneg == 0:
            continue
        by_mouse.setdefault(key[0], []).append((min(npos, nneg), c, npos, nneg))
    est = {}
    for mouse, cells in by_mouse.items():
        wsum = sum(x[0] for x in cells)
        dr = dl = 0.0
        for wr, c, npos, nneg in cells:
            dr += wr / wsum * (c["positive"]["R"] / npos - c["negative"]["R"] / nneg)
            dl += wr / wsum * (c["positive"]["L"] / npos - c["negative"]["L"] / nneg)
        est[mouse] = 100 * (dr - dl) / 2
    total = 0.0
    for v in est.values():
        total += v
    return total / len(est), est


# ----------------------------------------------------------------------------------------------------------------
# helpers for sets and splits
# ----------------------------------------------------------------------------------------------------------------
def with_arm(t, flag):
    d = t[t[flag]].copy()
    d["arm"] = d.pulse_category.where(d.pulse_category.isin(SIGNED + ("control",)), "excluded")
    return d


def session_halves(t):
    """first / second half of each mouse's sessions in chronological session-number order (declared above)."""
    order = t[["mouse", "session", "session_id"]].drop_duplicates()
    order["num"] = order.session_id.str.split("_").str[0].astype(int)
    half = {}
    for mouse, g in order.sort_values(["mouse", "num"]).groupby("mouse"):
        k = len(g)
        if k < 2:
            continue
        h = k // 2
        for s in g.session.iloc[:h]:
            half[s] = "first"
        for s in g.session.iloc[k - h:]:
            half[s] = "second"
    return t.session.map(half), order


def stratum_from_onset(onset, boundaries):
    lo, hi = boundaries
    return np.where(onset < lo, "early", np.where(onset < hi, "middle", "late"))


def d1_status(run):
    path = run / "response_time" / "d1_control_alignment.json"
    if not path.exists():
        return None, path, None
    obj = json.loads(path.read_text())
    return obj, path, io.sha256_file(path)


def d1_accepted(obj):
    if obj is None:
        return False
    for key in ("accepted", "alignment_accepted", "control_alignment_accepted"):
        if key in obj:
            return bool(obj[key])
    for key in ("verdict", "status", "decision"):
        if isinstance(obj.get(key), str):
            return obj[key].strip().lower().startswith("accept")
    return False


# ----------------------------------------------------------------------------------------------------------------
# responder-only secondary
# ----------------------------------------------------------------------------------------------------------------
def responder_only(d, analysis_set):
    """Cell-standardized P(R | responded) difference and per-mouse conditional logistic-style fixed-effect GLM."""
    import statsmodels.api as sm

    w = cell_table(d, "positive", "negative", CELL)
    rows = []
    for mouse, c in w.groupby("mouse"):
        s = c[c.supported].copy()
        rp = s["positive__R"] + s["positive__L"]
        rn = s["negative__R"] + s["negative__L"]
        s = s[(rp > 0) & (rn > 0)]
        rp, rn = s["positive__R"] + s["positive__L"], s["negative__R"] + s["negative__L"]
        ww = s.w_raw / s.w_raw.sum()  # contract weights (all-trial min), renormalized over responder-supported cells
        diff = 100 * float((ww * (s["positive__R"] / rp - s["negative__R"] / rn)).sum())
        # logistic regression, responders only, cell fixed effects; cells whose responders are all one side carry no
        # information about the pulse coefficient under cell fixed effects and are dropped before fitting.
        dm = d[(d.mouse == mouse) & d.arm.isin(SIGNED) & (d.response_side != "none")].copy()
        key = dm[CELL].astype(str).agg("|".join, axis=1)
        keep_cells = set(s[CELL].astype(str).agg("|".join, axis=1))
        dm = dm[key.isin(keep_cells)]
        key = dm[CELL].astype(str).agg("|".join, axis=1)
        y = (dm.response_side == "R").astype(float)
        informative = y.groupby(key).transform(lambda v: 0 < v.mean() < 1)
        dm, y, key = dm[informative], y[informative], key[informative]
        beta = se = np.nan
        conv = False
        if len(dm) > 0 and dm.arm.nunique() == 2:
            X = pd.get_dummies(key, drop_first=False, dtype=float)
            X["positive"] = (dm.arm == "positive").astype(float)
            try:
                fit = sm.GLM(y.to_numpy(), X.to_numpy(), family=sm.families.Binomial()).fit(maxiter=200)
                beta, se, conv = float(fit.params[-1]), float(fit.bse[-1]), bool(fit.converged)
            except Exception as exc:  # recorded, not hidden
                conv = f"failed: {exc}"
        rows.append({"analysis_set": analysis_set, "mouse": mouse, "rig": d.loc[d.mouse == mouse, "rig"].iloc[0],
                     "n_cells_responder_supported": len(s), "n_responders_pos": int(rp.sum()), "n_responders_neg": int(rn.sum()),
                     "Delta_P_R_given_responded_pp": diff, "logit_positive_vs_negative": beta, "logit_se_trial_level": se,
                     "logit_n_trials": len(dm), "logit_n_cells_informative": int(key.nunique()) if len(dm) else 0,
                     "logit_converged": conv})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------------------------------------------------
def _style():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
    return plt


def fig_primary(pm, grp, path, title):
    plt = _style()
    eps = [("Delta_direction", "Direction\n(ΔR − ΔL)/2"), ("Delta_R", "Right\nΔR"), ("Delta_L", "Left\nΔL"),
           ("Delta_unresponded", "Unresponded\nΔnone")]
    fig, ax = plt.subplots(figsize=(4.6, 3.2), layout="constrained")
    mice = sorted(pm.mouse)
    offs = np.linspace(-0.18, 0.18, len(mice))
    for i, (ep, _) in enumerate(eps):
        v = pm.set_index("mouse").loc[mice, ep].to_numpy()
        ax.scatter(i + offs, v, s=12, color="0.55", zorder=2, label="mouse" if i == 0 else None)
        g = grp[(grp.endpoint == ep) & grp.method.str.startswith("student_t")].iloc[0]
        ax.errorbar(i + 0.33, g.estimate, yerr=[[g.estimate - g.ci_low], [g.ci_high - g.estimate]], fmt="D", ms=5,
                    color="#0072B2", capsize=3, zorder=3, label="mean, 95% t CI" if i == 0 else None)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(range(len(eps)), [e[1] for e in eps])
    ax.set_ylabel("Positive − negative pulse\n(percentage points, by 5 s)")
    ax.set_title(title, fontsize=8)
    ax.legend(frameon=False, fontsize=7, loc="best")
    io.savefig(fig, path)
    plt.close(fig)
    return path


def fig_forest(rows, path, title, xlabel="Δdirection (percentage points)"):
    """rows: list of (label, estimate, lo, hi, mouse_values or None)."""
    plt = _style()
    fig, ax = plt.subplots(figsize=(6.0, 0.28 * len(rows) + 1.0), layout="constrained")
    for i, (label, est, lo, hi, pts) in enumerate(rows):
        y = len(rows) - 1 - i
        if pts is not None and len(pts):
            ax.scatter(pts, np.full(len(pts), y) + np.linspace(-0.15, 0.15, len(pts)), s=6, color="0.45", zorder=4)
        if np.isfinite(lo):
            ax.plot([lo, hi], [y, y], color="#0072B2", lw=1.5, zorder=2)
        ax.plot(est, y, "D", color="#0072B2", ms=4, zorder=3)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=8)
    io.savefig(fig, path)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True, help="run ID created by package A")
    ap.add_argument("--scratch", help="write into this directory instead of the run (test run; never marked COMPLETE)")
    ap.add_argument("--skip-c4", action="store_true", help="do not run C4 even if D1 accepts the alignment")
    args = ap.parse_args(argv)
    timer = io.Timer()

    run = io.run_dir(args.run_id)
    t, cfg = io.load_trials(run)
    assert "pulse_type_rt_dependent" in t  # present in the table; never used below
    if args.scratch:
        out = Path(args.scratch) / STAGE
        figdir = Path(args.scratch) / "figures"
        out.mkdir(parents=True, exist_ok=True)
        figdir.mkdir(parents=True, exist_ok=True)
    else:
        out = io.stage_dir(run, STAGE)
        figdir = io.figure_dir(args.run_id)
    if any(out.iterdir()):
        sys.exit(f"refusing to write: {out} is not empty")
    if list(figdir.glob(f"{STAGE}_*")):
        sys.exit(f"refusing to write: {figdir} already has {STAGE}_* figures")

    seed = int(cfg["control_alignment"]["seed"])
    n_boot = int(cfg["inference"]["bootstrap_resamples"])
    checks, notes, outputs = {}, [], []
    per_mouse_tabs, group_tabs, cell_tabs = [], [], []

    def add(pm, cells, analysis_set, contrast, boot=True, prefix=""):
        per_mouse_tabs.append(pm)
        c = cells.copy()
        c.insert(0, "contrast", contrast)
        c.insert(0, "analysis_set", analysis_set)
        cell_tabs.append(c)
        rows = group_rows(pm, analysis_set, contrast, rng_seed=seed, n_boot=n_boot if boot else 0, method_prefix=prefix)
        group_tabs.extend(rows)
        return rows

    # ---------------- C1/C2: positive vs negative, three analysis sets ----------------
    pms = {}
    for name, flag in SETS.items():
        d = with_arm(t, flag)
        pm, cells = per_mouse(d, "positive", "negative", CELL, name, "positive_vs_negative")
        pms[name] = pm
        add(pm, cells, name, "positive_vs_negative")
        # checks: components sum to zero, weights, probabilities, coverage vs package A support summary
        checks[f"{name}_components_sum_to_zero"] = bool(np.all(np.abs(pm.Delta_R + pm.Delta_L + pm.Delta_unresponded) < 1e-9))
        checks[f"{name}_weights_sum_to_one"] = bool(np.all(np.abs(pm.weight_sum - 1) < 1e-9))
        pcols = [c for c in cells if c.startswith("p_")]
        checks[f"{name}_probabilities_in_unit_interval"] = bool(((cells[pcols].fillna(0) >= 0) & (cells[pcols].fillna(0) <= 1)).all().all())
        checks[f"{name}_n_mice_10"] = len(pm) == 10

    support = pd.read_csv(run / "data" / cfg["files"]["support_summary"])
    cov_rows = []
    for name, flag in SETS.items():
        pm = pms[name].set_index("mouse")
        s = support[support.analysis_set == name].set_index("mouse")
        d = t[t[flag]]
        for mouse in s.index:
            dm = d[d.mouse == mouse]
            r = {"analysis_set": name, "mouse": mouse, "rig": s.loc[mouse, "rig"],
                 "n_trials_in_set": len(dm),
                 "n_positive": int((dm.pulse_category == "positive").sum()), "n_negative": int((dm.pulse_category == "negative").sum()),
                 "n_control": int((dm.pulse_category == "control").sum()), "n_null_pulse_excluded": int((dm.pulse_category == "null_pulse").sum()),
                 "n_direction_unknown_excluded": int((dm.pulse_category == "pulse_direction_unknown").sum()),
                 "n_positive_in_asymmetric_cells": int(((dm.pulse_category == "positive") & ~dm.signs_scheduled_symmetric).sum()),
                 "n_cells_total": int(s.loc[mouse, "n_cells_total"]),
                 "n_cells_supported": int(pm.loc[mouse, "n_cells"]) if mouse in pm.index else 0,
                 "n_signed_trials_in_support": int(pm.loc[mouse, "n_trials_pos"] + pm.loc[mouse, "n_trials_neg"]) if mouse in pm.index else 0,
                 "effective_pairs": int(pm.loc[mouse, "effective_pairs"]) if mouse in pm.index else 0,
                 "n_signed_trials_outside_support": int(s.loc[mouse, "n_pulse_trials"] - s.loc[mouse, "n_pulse_trials_in_support"]),
                 "n_pre_onset_responses_retained_in_support": 0, "n_unresponded_in_support": 0}
            cov_rows.append(r)
            ok = (r["n_cells_supported"] == s.loc[mouse, "n_cells_supported"] and r["n_signed_trials_in_support"] == s.loc[mouse, "n_pulse_trials_in_support"]
                  and r["effective_pairs"] == s.loc[mouse, "effective_pairs"])
            checks.setdefault(f"{name}_coverage_matches_package_A_support_summary", True)
            checks[f"{name}_coverage_matches_package_A_support_summary"] &= bool(ok)
    coverage = pd.DataFrame(cov_rows)
    # pre-onset responses and unresponded trials inside supported primary cells
    for name, flag in SETS.items():
        d = with_arm(t, flag)
        cells = [c for c in cell_tabs if c.analysis_set.iloc[0] == name][0]
        keys = cells[cells.supported][CELL]
        m = d[d.arm.isin(SIGNED)].merge(keys, on=CELL)
        pre = m.groupby("mouse").pre_onset_response.sum()
        unr = m.groupby("mouse").apply(lambda g: int((g.response_side == "none").sum()), include_groups=False)
        sel = coverage.analysis_set == name
        coverage.loc[sel, "n_pre_onset_responses_retained_in_support"] = coverage.loc[sel, "mouse"].map(pre).fillna(0).astype(int)
        coverage.loc[sel, "n_unresponded_in_support"] = coverage.loc[sel, "mouse"].map(unr).fillna(0).astype(int)

    # asymmetric UW cells: no negative arm, so they cannot be in positive-vs-negative support
    asym = t[~t.signs_scheduled_symmetric]
    checks["asymmetric_cells_have_no_negative_pulse"] = bool((asym.pulse_category != "negative").all())
    prim_cells = [c for c in cell_tabs if c.analysis_set.iloc[0] == "primary_coherence"][0]
    sup_keys = set(map(tuple, prim_cells[prim_cells.supported][CELL].astype(str).to_numpy()))
    asym_keys = set(map(tuple, asym[CELL].astype(str).to_numpy()))
    checks["asymmetric_cells_absent_from_positive_vs_negative_support"] = len(sup_keys & asym_keys) == 0

    # all-coherence vs primary: identical cells?
    ac = [c for c in cell_tabs if c.analysis_set.iloc[0] == "sensitivity_all_coherences"][0]
    ac_sup = ac[ac.supported]
    notes.append(f"all-coherence supported cells with |coherence| > 36: {int((ac_sup.coherence_pct.abs() > 36).sum())}")
    all_equals_primary = bool(np.allclose(pms["sensitivity_all_coherences"].set_index("mouse").Delta_direction.sort_index(),
                                          pms["primary_coherence"].set_index("mouse").Delta_direction.sort_index()))

    # independent recomputation
    ind_mean, ind_mouse = independent_primary(t)
    prim = pms["primary_coherence"].set_index("mouse")
    checks["independent_recomputation_matches_group"] = bool(abs(ind_mean - prim.Delta_direction.mean()) < 1e-9)
    checks["independent_recomputation_matches_each_mouse"] = bool(all(abs(ind_mouse[m] - prim.loc[m, "Delta_direction"]) < 1e-9 for m in prim.index))

    # |coherence| = 100: genuine pulse vs null pulse, signed toward the genuine pulse direction (descriptive)
    d100 = t[t.in_all_coherences & (t.abs_coherence_pct == 100)].copy()
    d100["arm"] = np.where(d100.pulse_category.isin(SIGNED), "genuine", np.where(d100.pulse_category == "null_pulse", "null", "excluded"))
    pm100, cells100 = per_mouse(d100, "genuine", "null", CELL, "coherence_100_descriptive", "genuine_vs_null_pulse")
    if len(pm100):
        # within a cell the genuine pulse sign is fixed (opposite to the stimulus); sign the contrast by it
        sgn = d100[d100.arm == "genuine"].groupby(CELL).pulse_sign.agg(lambda v: v.iloc[0] if v.nunique() == 1 else np.nan).reset_index()
        c100 = cells100[cells100.supported].merge(sgn, on=CELL)
        checks["coherence_100_genuine_sign_constant_within_cell"] = bool(c100.pulse_sign.notna().all())
        rows = []
        for mouse, c in c100.groupby("mouse"):
            toward = 100 * float((c.w * c.pulse_sign * ((c.p_genuine_R - c.p_null_R) - (c.p_genuine_L - c.p_null_L)) / 2).sum())
            dunr = 100 * float((c.w * (c.p_genuine_none - c.p_null_none)).sum())
            rows.append({"mouse": mouse, "n_cells": len(c), "n_genuine": int(c.genuine__n.sum()), "n_null": int(c.null__n.sum()),
                         "Delta_toward_pulse_pp": toward, "Delta_unresponded_pp": dunr})
        pm100 = pd.DataFrame(rows)
        n, m, lo, hi, p, sd = t_summary(pm100.Delta_toward_pulse_pp)
        coh100 = {"n_mice": n, "estimate": m, "ci_low": lo, "ci_high": hi, "method": "student_t_95_across_mice (descriptive)"}
    else:
        coh100 = {"n_mice": 0}

    # ---------------- C3 robustness ----------------
    prim_d = with_arm(t, "in_primary_coherence")
    x = prim.Delta_direction
    lomo = pd.DataFrame([{"left_out": m, "n_mice": len(x) - 1, "estimate": x.drop(m).mean(),
                          "ci_low": t_summary(x.drop(m))[2], "ci_high": t_summary(x.drop(m))[3], "p_value": t_summary(x.drop(m))[4]}
                         for m in x.index])

    half, order = session_halves(t)
    prim_d["session_half"] = half.loc[prim_d.index]
    rob = []
    split_pm = {}
    for h in ("first", "second"):
        pm, cells = per_mouse(prim_d[prim_d.session_half == h], "positive", "negative", CELL, "primary_coherence", f"positive_vs_negative_session_half_{h}")
        split_pm[f"session_{h}"] = pm
        add(pm, cells, "primary_coherence", f"positive_vs_negative_session_half_{h}", boot=False)
    prim_d["within_half"] = np.where(prim_d.position < prim_d.n_in_session / 2, "first", "second")
    for h in ("first", "second"):
        pm, cells = per_mouse(prim_d[prim_d.within_half == h], "positive", "negative", CELL, "primary_coherence", f"positive_vs_negative_within_session_half_{h}")
        split_pm[f"within_{h}"] = pm
        add(pm, cells, "primary_coherence", f"positive_vs_negative_within_session_half_{h}", boot=False)
    for kind in ("session", "within"):
        a, b = split_pm[f"{kind}_first"].set_index("mouse"), split_pm[f"{kind}_second"].set_index("mouse")
        common = a.index.intersection(b.index)
        diff = b.loc[common, "Delta_direction"] - a.loc[common, "Delta_direction"]
        n, m, lo, hi, p, sd = t_summary(diff)
        rob.append({"check": f"{kind}_halves_second_minus_first", "n_mice": n, "estimate": m, "ci_low": lo, "ci_high": hi,
                    "method": "student_t_95_across_mice (descriptive; pointwise)", "mice": ",".join(common)})

    # matched seeds
    seed_cells = ["mouse", "seed", "coherence_pct"]
    pm_seed, cells_seed = per_mouse(prim_d, "positive", "negative", seed_cells, "primary_coherence", "positive_vs_negative_matched_seed")
    add(pm_seed, cells_seed, "primary_coherence", "positive_vs_negative_matched_seed", boot=False)
    seed_mice = list(pm_seed.mouse)
    ref = prim.loc[seed_mice].reset_index()
    group_tabs.extend(group_rows(ref, "primary_coherence", "positive_vs_negative_standard_cells_same_mice_as_matched_seed", rng_seed=seed, n_boot=0))
    checks["matched_seed_cells_hold_same_seed"] = True  # by construction of the grouping key
    notes.append(f"matched-seed mice: {seed_mice}; matched cells per mouse: {dict(zip(pm_seed.mouse, pm_seed.n_cells))}")

    # responder-only secondary
    resp = responder_only(prim_d, "primary_coherence")
    for col, ep in (("Delta_P_R_given_responded_pp", "Delta_P_R_given_responded"), ("logit_positive_vs_negative", "logit_positive_vs_negative")):
        v = resp[col].dropna()
        n, m, lo, hi, p, sd = t_summary(v)
        group_tabs.append({"analysis_set": "primary_coherence", "contrast": "positive_vs_negative_responders_only", "n_mice": n,
                           "estimate": m, "ci_low": lo, "ci_high": hi, "method": "student_t_95_across_mice (secondary; conditions on responding)",
                           "p_value": np.nan, "p_holm": np.nan, "endpoint": ep, "sd_across_mice": sd, "dz": np.nan})

    # ---------------- C4: pulse vs timing-matched control ----------------
    d1, d1_path, d1_hash = d1_status(run)
    c4 = {"d1_path": str(d1_path), "d1_exists": d1 is not None, "d1_sha256": d1_hash, "d1_accepted": d1_accepted(d1)}
    pvc = {}
    if d1_accepted(d1) and not args.skip_c4:
        dsym = prim_d[prim_d.signs_scheduled_symmetric].copy()
        b = cfg["strata"]["ucla_onset_stratum"]["boundaries_s"]
        ctrl = dsym.arm == "control"
        # control stratum consistency with the contract's pseudo-onset / sham rule
        ucla_ctrl = ctrl & (dsym.rig == "ucla")
        checks["ucla_control_stratum_matches_pseudo_onset"] = bool((stratum_from_onset(dsym.loc[ucla_ctrl, "control_onset_s"], b) == dsym.loc[ucla_ctrl, "onset_stratum"]).all())
        checks["every_control_has_onset_stratum"] = bool(dsym.loc[ctrl, "onset_stratum"].isin(["early", "middle", "late"]).all())
        for a_, b_, name in (("positive", "control", "positive_vs_control"), ("control", "negative", "control_vs_negative")):
            pm, cells = per_mouse(dsym, a_, b_, CELL, "primary_coherence", name)
            pvc[name] = pm
            add(pm, cells, "primary_coherence", name)
            checks[f"{name}_components_sum_to_zero"] = bool(np.all(np.abs(pm.Delta_R + pm.Delta_L + pm.Delta_unresponded) < 1e-9))
            checks[f"{name}_weights_sum_to_one"] = bool(np.all(np.abs(pm.weight_sum - 1) < 1e-9))
        checks["pulse_vs_control_excludes_asymmetric_cells"] = bool(dsym.signs_scheduled_symmetric.all())
        # pseudo-onset seed sensitivity: re-derive UCLA control strata from the sensitivity seeds
        sens = []
        for k in range(1, len(cfg["control_alignment"]["sensitivity_seeds"]) + 1):
            dk = dsym.copy()
            m_ = (dk.arm == "control") & (dk.rig == "ucla")
            dk.loc[m_, "onset_stratum"] = stratum_from_onset(dk.loc[m_, f"control_onset_s_seed{k}"], b)
            for a_, b_, name in (("positive", "control", "positive_vs_control"), ("control", "negative", "control_vs_negative")):
                pm, _ = per_mouse(dk, a_, b_, CELL, "primary_coherence", name)
                n, m, lo, hi, p, sd = t_summary(pm.Delta_direction)
                sens.append({"contrast": name, "pseudo_onset_seed_index": k, "seed": cfg["control_alignment"]["sensitivity_seeds"][k - 1],
                             "n_mice": n, "estimate": m, "ci_low": lo, "ci_high": hi})
        sens = pd.DataFrame(sens)
        # POST HOC (added after viewing the C4 estimates, not declared before): per-mouse difference between the two
        # pulse-vs-control contrasts. Descriptive, pointwise; the two contrasts use different cell weights.
        a_, b_ = pvc["positive_vs_control"].set_index("mouse"), pvc["control_vs_negative"].set_index("mouse")
        common = a_.index.intersection(b_.index)
        for ep in ("Delta_direction", "Delta_unresponded"):
            diff = a_.loc[common, ep] - b_.loc[common, ep]
            n, m, lo, hi, p, sd = t_summary(diff)
            group_tabs.append({"analysis_set": "primary_coherence", "contrast": "posthoc_positive_vs_control_minus_control_vs_negative",
                               "n_mice": n, "estimate": m, "ci_low": lo, "ci_high": hi,
                               "method": "student_t_95_across_mice (post hoc descriptive, pointwise; not a test)",
                               "p_value": np.nan, "p_holm": np.nan, "endpoint": ep, "sd_across_mice": sd, "dz": np.nan})
        outputs.append(io.write_csv(out / "c4_pseudo_onset_seed_sensitivity.csv", sens))
    else:
        notes.append("C4 not run: D1 file missing, not accepted, or --skip-c4")

    # ---------------- Holm family ----------------
    group = pd.DataFrame(group_tabs)
    fam = {"primary Delta_direction (positive vs negative)": ("primary_coherence", "positive_vs_negative"),
           "Delta_direction positive vs timing-matched control": ("primary_coherence", "positive_vs_control"),
           "Delta_direction timing-matched control vs negative": ("primary_coherence", "control_vs_negative")}
    fam_p, estimable = {}, {}
    for label, (s_, c_) in fam.items():
        r = group[(group.analysis_set == s_) & (group.contrast == c_) & (group.endpoint == "Delta_direction") & group.method.str.startswith("student_t")]
        estimable[label] = bool(len(r) == 1 and np.isfinite(r.p_value.iloc[0]))
        fam_p[label] = float(r.p_value.iloc[0]) if estimable[label] else np.nan
    adj = holm(fam_p)
    for label, (s_, c_) in fam.items():
        if label in adj:
            sel = (group.analysis_set == s_) & (group.contrast == c_) & (group.endpoint == "Delta_direction") & group.method.str.startswith("student_t")
            group.loc[sel, "p_holm"] = adj[label]
    holm_record = {"family": list(fam), "estimable": estimable, "p_unadjusted": fam_p, "p_holm": adj,
                   "m_in_correction": len(adj), "correction": cfg["inference"]["multiplicity"]["correction"]}
    # descriptive rows outside the family: drop their p values so they are not read as tests
    in_family = group.apply(lambda r: (r.analysis_set, r.contrast) in fam.values() and r.endpoint == "Delta_direction", axis=1)
    group["p_value_role"] = np.where(in_family & group.method.str.startswith("student_t"), "holm_family",
                                     np.where(group.p_value.notna(), "descriptive_pointwise_not_a_test", ""))

    # ---------------- write tables ----------------
    schema = cfg["output_schema"]
    per_mouse_all = pd.concat(per_mouse_tabs, ignore_index=True)
    per_mouse_all = per_mouse_all[schema["per_mouse_table"] + [c for c in per_mouse_all if c not in schema["per_mouse_table"]]]
    group = group[schema["group_table"] + [c for c in group if c not in schema["group_table"]]]
    checks["per_mouse_schema_columns_present"] = list(per_mouse_all.columns[:len(schema["per_mouse_table"])]) == schema["per_mouse_table"]
    checks["group_schema_columns_present"] = list(group.columns[:len(schema["group_table"])]) == schema["group_table"]
    outputs += [io.write_csv(out / "per_mouse.csv", per_mouse_all), io.write_csv(out / "group.csv", group),
                io.write_csv(out / "coverage.csv", coverage), io.write_csv(out / "cells.csv", pd.concat(cell_tabs, ignore_index=True)),
                io.write_csv(out / "robustness_leave_one_mouse_out.csv", lomo),
                io.write_csv(out / "robustness_split_differences.csv", pd.DataFrame(rob)),
                io.write_csv(out / "robustness_session_order.csv", order.assign(half=order.session.map(half.groupby(t.session).first())).sort_values(["mouse", "num"])),
                io.write_csv(out / "secondary_responder_only.csv", resp),
                io.write_csv(out / "descriptive_coherence_100.csv", pm100)]
    summary = {"run_id": args.run_id, "config_version": cfg["config_version"], "holm": holm_record, "c4": c4,
               "independent_recomputation": {"group_Delta_direction": ind_mean, "per_mouse": ind_mouse},
               "all_coherences_identical_to_primary": all_equals_primary, "coherence_100_descriptive": coh100,
               "notes": notes, "bootstrap_seed": seed, "bootstrap_resamples": n_boot}
    outputs.append(io.write_json(out / "summary.json", summary))

    # ---------------- figures ----------------
    tag = "behaviour"
    gp = group[(group.analysis_set == "primary_coherence") & (group.contrast == "positive_vs_negative")]
    outputs.append(fig_primary(pms["primary_coherence"], gp, figdir / f"{tag}_primary_components.png",
                               f"Primary set (|coh| ≤ 36%), n = {len(pms['primary_coherence'])} mice; points = mice"))

    def g(s_, c_, ep="Delta_direction", meth="student_t"):
        r = group[(group.analysis_set == s_) & (group.contrast == c_) & (group.endpoint == ep) & group.method.str.startswith(meth)]
        return r.iloc[0]

    rows = []
    r = g("primary_coherence", "positive_vs_negative")
    rows.append((f"Primary, t CI (n={r.n_mice})", r.estimate, r.ci_low, r.ci_high, prim.Delta_direction.to_numpy()))
    r = g("primary_coherence", "positive_vs_negative", meth="mouse_bootstrap")
    rows.append((f"Primary, mouse bootstrap", r.estimate, r.ci_low, r.ci_high, None))
    for s_, lab in (("sensitivity_all_coherences", "All coherences"), ("sensitivity_zero_coherence", "Zero coherence")):
        r = g(s_, "positive_vs_negative")
        rows.append((f"{lab} (n={r.n_mice})", r.estimate, r.ci_low, r.ci_high, pms[s_].Delta_direction.to_numpy()))
    for c_, lab in (("session_half_first", "Sessions, first half"), ("session_half_second", "Sessions, second half"),
                    ("within_session_half_first", "Within session, first half"), ("within_session_half_second", "Within session, second half"),
                    ("matched_seed", "Matched seed cells"), ("standard_cells_same_mice_as_matched_seed", "Standard cells, same mice")):
        r = g("primary_coherence", f"positive_vs_negative_{c_}")
        pts = per_mouse_all[(per_mouse_all.contrast == f"positive_vs_negative_{c_}")].Delta_direction.to_numpy() if "same_mice" not in c_ else ref.Delta_direction.to_numpy()
        rows.append((f"{lab} (n={r.n_mice})", r.estimate, r.ci_low, r.ci_high, pts))
    for _, l_ in lomo.iterrows():
        rows.append((f"Leave out {l_.left_out}", l_.estimate, l_.ci_low, l_.ci_high, None))
    fig_forest(rows, figdir / f"{tag}_robustness_forest.png", "Positive − negative Δdirection, robustness (exploratory)\ndiamond = mean; bar = 95% t CI (bootstrap row: percentile); grey = mice")
    outputs.append(figdir / f"{tag}_robustness_forest.png")

    rr = resp.set_index("mouse")
    rows = [(f"Δdirection, all trials (n={len(prim)})", *g("primary_coherence", "positive_vs_negative")[["estimate", "ci_low", "ci_high"]], prim.Delta_direction.to_numpy())]
    r = group[(group.contrast == "positive_vs_negative_responders_only") & (group.endpoint == "Delta_P_R_given_responded")].iloc[0]
    rows.append((f"ΔP(R | responded) (n={r.n_mice})", r.estimate, r.ci_low, r.ci_high, rr.Delta_P_R_given_responded_pp.to_numpy()))
    r = g("primary_coherence", "positive_vs_negative", ep="Delta_unresponded")
    rows.append((f"Δunresponded, all trials", r.estimate, r.ci_low, r.ci_high, prim.Delta_unresponded.to_numpy()))
    fig_forest(rows, figdir / f"{tag}_responder_only_vs_probabilities.png",
               "Responder-only contrast (conditions on responding)\nnext to all-trial probabilities; grey = mice",
               xlabel="Positive − negative (percentage points)")
    outputs.append(figdir / f"{tag}_responder_only_vs_probabilities.png")

    if pvc:
        rows = [(f"Positive − negative, primary (n={len(prim)})", *g("primary_coherence", "positive_vs_negative")[["estimate", "ci_low", "ci_high"]], prim.Delta_direction.to_numpy())]
        for name, lab in (("positive_vs_control", "Positive − control"), ("control_vs_negative", "Control − negative")):
            for ep, el in (("Delta_direction", "Δdirection"), ("Delta_unresponded", "Δunresponded")):
                r = g("primary_coherence", name, ep=ep)
                rows.append((f"{lab}, {el} (n={r.n_mice})", r.estimate, r.ci_low, r.ci_high, pvc[name][ep].to_numpy()))
        fig_forest(rows, figdir / f"{tag}_pulse_vs_control.png", "Pulse vs timing-matched control (symmetric cells; exploratory)\nbars = 95% t CI across mice; grey = mice",
                   xlabel="Contrast (percentage points)")
        outputs.append(figdir / f"{tag}_pulse_vs_control.png")

    # ---------------- manifest ----------------
    c4_done = bool(pvc)
    checks["c4_completed_or_explicitly_blocked"] = c4_done or not d1_accepted(d1) or args.skip_c4
    passed = all(bool(v) for v in checks.values())
    inputs = {"trial_table": cfg["hashes"]["trial_table"], "analysis_config": io.sha256_file(run / "data" / "analysis_config.json"),
              "support_summary": io.sha256_file(run / "data" / cfg["files"]["support_summary"])}
    if d1_hash:
        inputs["d1_control_alignment"] = d1_hash
    cmd = "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.behaviour " + " ".join(argv if argv is not None else sys.argv[1:])
    manifest = io.stage_manifest(STAGE, cmd, inputs, outputs, checks, timer.seconds,
                                 extra={"c4_completed": c4_done, "holm": holm_record, "bootstrap_seed": seed})
    print(json.dumps({"checks": checks, "holm": holm_record, "c4": c4}, indent=1, default=str))
    if args.scratch:
        io.write_json(out / "manifest.json", manifest)
        print("scratch run: no COMPLETE marker")
        return passed
    if not c4_done:
        io.write_json(out / "manifest.json", manifest)
        print("C4 not completed: COMPLETE marker withheld")
        return False
    return io.mark_complete(out, manifest, passed)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
