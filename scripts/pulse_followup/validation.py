"""Package G1: behavioural validation harness on A's actual design (EXPLORATORY; plan section G1 only).

The design is kept exactly: the frozen trial table's primary-set trials (|coh| <= 36%) with their arms, cells, sessions,
onsets (recorded pulse onsets; control_onset_s for controls), symmetric-schedule flags and the 5 s deadline. Only the
outcomes (response_side, rt_s) are replaced by simulated ones. C's and D's estimators are called from behaviour.py and
response_time.py, not copied. No mechanism model is simulated (G2-G5 wait for F).

DECLARED BEFORE ANY SIMULATION WAS RUN
Base outcome model: for each mouse x signed coherence, the empirical control-trial multinomial P(R), P(L), P(none by
5 s) and side-specific empirical control RT pools (responded RTs <= 5 s). Every trial (any arm) draws side and RT from
its mouse x coherence base. 'none' trials have no RT (censored at 5 s, never an event).
Pulse mechanisms (signed pulse trials only; controls and other categories keep the base draw):
  flip(q, window [a, b] since onset): a positive pulse turns a left response whose RT lies in [onset + a, onset + b]
    into a right response (RT unchanged) with probability q (q < 0: right into left with |q|); a negative pulse
    mirrors this. Responses before onset can never change, by construction (generator iii).
Scenarios (index, name):
  0 no_effect         no pulse effect (generator i; Holm family under the global null)
  1-3 dir3/dir6/dir10 flip over [0, inf): per mouse, true C primary Delta_direction delta_m ~ N(delta, tau), delta in
                      {3, 6, 10} pp, mapped exactly to q_m (|q_m| <= 1) (generator ii; iii is checked in every run)
  4 censor            slowing: on signed pulse trials, RTs at/after onset are delayed by 0.5 s; delayed RTs > 5 s
                      become unresponded at the deadline. No directional effect (generator iv)
  5 timelocal         flip with window [0.5, 1.0] s since onset, delta = 6 pp at 5 s with tau (generator v)
tau rule: tau^2 = max(SD_obs^2 - mean_m Var_null(est_m), 0), where SD_obs is the across-mouse SD of C's observed
primary per-mouse Delta_direction (behaviour/per_mouse.csv) and Var_null(est_m) is the across-dataset variance of
mouse m's estimate in scenario 0. So the simulated observed spread matches the observed 5.7 pp.
Truth: the estimators are linear in outcome indicators given the design counts, so the expected per-mouse contrast is
computed exactly from per-trial expected indicators (pools' ECDFs at each trial's onset), with the estimator's
cell weights (C: behaviour.cell_table on design counts; D onset-eligible: weights from expected eligible counts, a
plug-in large-sample truth that ignores the small randomness of eligible cell support). Population truth averages
over the delta_m distribution (200,000 draws per mouse); conditional truth is the mean over this dataset's mice.
Inference checked: C's two-sided 95% Student-t across mice (primary) and mouse bootstrap (cfg resamples), one-sample
t-test p values, Holm over the cfg family; D's pointwise t-intervals at u in GRID_D (D's estimator on a coarse grid).
Rates get Clopper-Pearson 95% Monte Carlo intervals. Dataset count is fixed before the main run from a timed pilot.

Usage:
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.validation --run-id <RUN_ID> --n-datasets 200
  ... --scratch <dir> --n-datasets 4     # timed pilot; never marked COMPLETE
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import multiprocessing as mp  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.pulse_followup import behaviour as C  # noqa: E402
from scripts.pulse_followup import checks as K  # noqa: E402
from scripts.pulse_followup import io  # noqa: E402
from scripts.pulse_followup import response_time as D  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)
STAGE, SUB = "validation", "g1"
GRID_D = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.58])
SCENARIOS = [
    {"name": "no_effect", "kind": "none"},
    {"name": "dir3", "kind": "flip", "delta": 3.0, "a": 0.0, "b": np.inf},
    {"name": "dir6", "kind": "flip", "delta": 6.0, "a": 0.0, "b": np.inf},
    {"name": "dir10", "kind": "flip", "delta": 10.0, "a": 0.0, "b": np.inf},
    {"name": "censor", "kind": "slow", "s": 0.5},
    {"name": "timelocal", "kind": "flip", "delta": 6.0, "a": 0.5, "b": 1.0},
]
KEEP_COLS = ["trial_id", "mouse", "rig", "session", "coherence_pct", "onset_stratum", "pulse_category",
             "response_side", "rt_s", "recorded_onset_s", "control_onset_s", "in_primary_coherence",
             "signs_scheduled_symmetric"]
C_CONTRASTS = {"pvn": ("positive", "negative", False), "pvc": ("positive", "control", True), "cvn": ("control", "negative", True)}


# ------------------------------------------------------------------------------------------------------------ design
class Design:
    def __init__(self, t, cfg):
        p = t[t.in_primary_coherence][KEEP_COLS].copy().reset_index(drop=True)
        self.template, self.cfg, self.deadline = p, cfg, float(cfg["deadline_s"])
        arm = p.pulse_category.to_numpy()
        self.sign = np.where(arm == "positive", 1, np.where(arm == "negative", -1, 0))
        on = np.where(arm == "control", p.control_onset_s, p.recorded_onset_s).astype(float)
        self.onset = np.where(np.isnan(on), np.inf, on)  # pulse_direction_unknown without onset: never affected
        self.mice = sorted(p.mouse.unique())
        self.midx = p.mouse.map({m: i for i, m in enumerate(self.mice)}).to_numpy()
        keys = list(zip(p.mouse, p.coherence_pct))
        self.gkeys = sorted(set(keys))
        gmap = {k: i for i, k in enumerate(self.gkeys)}
        self.gid = np.array([gmap[k] for k in keys])
        self.trials_of = [np.flatnonzero(self.gid == g) for g in range(len(self.gkeys))]
        ctrl = p[arm == "control"]
        self.pR, self.pL, self.pools = np.zeros(len(self.gkeys)), np.zeros(len(self.gkeys)), []
        for g, (m, c) in enumerate(self.gkeys):
            cg = ctrl[(ctrl.mouse == m) & (ctrl.coherence_pct == c)]
            if len(cg) == 0:
                raise RuntimeError(f"no control trials for {m} at {c}%")
            self.pR[g], self.pL[g] = (cg.response_side == "R").mean(), (cg.response_side == "L").mean()
            self.pools.append([np.sort(cg.rt_s[cg.response_side == s].to_numpy(float)) for s in ("R", "L")])
        self.n = len(p)
        self._truth_setup()

    # ---- simulation
    def simulate(self, rng, mech, q_m=None):
        u = rng.random(self.n)
        pR, pL = self.pR[self.gid], self.pL[self.gid]
        side = np.where(u < pR, "R", np.where(u < pR + pL, "L", "none")).astype(object)
        rt = np.full(self.n, np.nan)
        for g, idx in enumerate(self.trials_of):
            for s, name in ((0, "R"), (1, "L")):
                sel = idx[side[idx] == name]
                pool = self.pools[g][s]
                if len(sel):
                    rt[sel] = pool[rng.integers(0, len(pool), len(sel))]
        base_side, base_rt = side.copy(), rt.copy()
        if mech["kind"] == "flip":
            q = q_m[self.midx]
            d = self.sign * np.sign(q)
            inwin = ~np.isnan(rt) & (rt >= self.onset + mech["a"]) & (rt <= self.onset + mech["b"])
            hit = rng.random(self.n) < np.abs(q)
            side[(d == 1) & inwin & hit & (base_side == "L")] = "R"
            side[(d == -1) & inwin & hit & (base_side == "R")] = "L"
        elif mech["kind"] == "slow":
            post = (self.sign != 0) & ~np.isnan(rt) & (rt >= self.onset)
            rt = np.where(post, rt + mech["s"], rt)
            cens = post & (rt > self.deadline)
            side[cens], rt[cens] = "none", np.nan
        return base_side, base_rt, side, rt

    # ---- exact expectations
    def F(self, s, x, how):
        out = np.zeros(self.n)
        for g, idx in enumerate(self.trials_of):
            pool = self.pools[g][s]
            if len(pool):
                out[idx] = np.searchsorted(pool, x[idx], side=how) / len(pool)
        return out

    def mass(self, s, lo, hi):
        return np.clip(self.F(s, hi, "right") - self.F(s, lo, "left"), 0, None)

    def expected(self, T, mech, qsign=1.0):
        """Per-trial expected indicators of R and L by absolute time T under mech with |q| = 1 (flip, direction
        qsign) or the slow mechanism. Linear in |q| for flip."""
        pR, pL = self.pR[self.gid], self.pL[self.gid]
        eR, eL = pR * self.F(0, T, "right"), pL * self.F(1, T, "right")
        if mech["kind"] == "flip":
            d = self.sign * qsign
            lo, hi = self.onset + mech["a"], np.minimum(self.onset + mech["b"], T)
            mL, mR = pL * self.mass(1, lo, hi), pR * self.mass(0, lo, hi)
            eR = eR + np.where(d == 1, mL, 0) - np.where(d == -1, mR, 0)
            eL = eL + np.where(d == -1, mR, 0) - np.where(d == 1, mL, 0)
        elif mech["kind"] == "slow":
            pulse = self.sign != 0
            out = []
            for s, pX, e in ((0, pR, eR), (1, pL, eL)):
                pre = np.where(T >= self.onset, self.F(s, self.onset, "left"), self.F(s, T, "right"))
                post = np.clip(self.F(s, T - mech["s"], "right") - self.F(s, self.onset, "left"), 0, None)
                out.append(np.where(pulse, pX * (pre + post), e))
            eR, eL = out
        return eR, eL

    def pre_onset(self):
        pR, pL = self.pR[self.gid], self.pL[self.gid]
        return pR * self.F(0, self.onset, "left"), pL * self.F(1, self.onset, "left")

    # ---- truth functionals (per mouse, percentage points)
    def _truth_setup(self):
        p = self.template.assign(response_side="none")
        d = C.with_arm(p, "in_primary_coherence")
        self.cw = {}
        for name, (a, b, sym) in C_CONTRASTS.items():
            dd = d[d.signs_scheduled_symmetric] if sym else d
            w = C.cell_table(dd, a, b, C.CELL)
            w = w[w.supported][C.CELL + ["w"]]
            self.cw[name] = (a, b, w)
        self.cellkey = p[C.CELL].astype(str).agg("|".join, axis=1).to_numpy()
        self.armv = p.pulse_category.to_numpy()
        self.sym = p.signs_scheduled_symmetric.to_numpy()

    def _cell_means(self, vals, a, b, w, denom=None):
        """Per-mouse sum_c w_c (mean_a - mean_b) of per-trial values (dict of arrays). denom: per-trial weights for
        ratio means (eligible truth)."""
        key = w[C.CELL].astype(str).agg("|".join, axis=1)
        df = pd.DataFrame({"key": self.cellkey, "arm": self.armv, **vals, "den": 1.0 if denom is None else denom})
        df = df[df.arm.isin([a, b]) & df.key.isin(set(key))]
        cols = list(vals)
        s = df.groupby(["key", "arm"])[cols + ["den"]].sum()
        mean = s[cols].div(s.den, axis=0)
        ma, mb = mean.xs(a, level="arm"), mean.xs(b, level="arm")
        diff = (ma - mb).reindex(key.to_numpy())
        ww = w.assign(key=key.to_numpy()).set_index("key")
        return {c: (diff[c].to_numpy() * ww.w.to_numpy()) for c in cols}, ww.mouse.to_numpy()

    def truth(self, mech, qsign=1.0):
        """Dict quantity -> per-mouse truth array (pp) for |q| = 1 in direction qsign (flip), or the slow/none mech."""
        out = {}
        eR, eL = self.expected(np.full(self.n, self.deadline), mech, qsign)
        for name, (a, b, w) in self.cw.items():
            parts, mice = self._cell_means({"R": eR, "L": eL, "U": 1 - eR - eL}, a, b, w)
            agg = {c: pd.Series(v).groupby(mice).sum().reindex(self.mice).to_numpy() * 100 for c, v in parts.items()}
            out[f"C_{name}_dir"] = (agg["R"] - agg["L"]) / 2
            out[f"C_{name}_U"] = agg["U"]
            if name == "pvn":
                out["C_pvn_R"], out["C_pvn_L"] = agg["R"], agg["L"]
        # D: positive vs negative on symmetric cells (D's base set); pos vs ctrl survival at 4.58 s
        preR, preL = self.pre_onset()
        pelig = 1 - preR - preL
        for u in GRID_D:
            eR, eL = self.expected(self.onset + u, mech, qsign)
            for summ in ("all_scheduled", "onset_eligible"):
                for name in ("pvn", "pvc"):
                    if name == "pvc" and u != GRID_D[-1]:
                        continue
                    a, b, w = self.cw[name]
                    if summ == "all_scheduled":
                        vals, den = {"R": eR, "L": eL}, None
                        ww = w
                    else:
                        vals, den = {"R": eR - preR, "L": eL - preL}, pelig
                        ww = self._eligible_weights(name, pelig)
                    parts, mice = self._cell_means(vals, a, b, ww, den)
                    agg = {c: pd.Series(v).groupby(mice).sum().reindex(self.mice).to_numpy() * 100 for c, v in parts.items()}
                    if name == "pvn":
                        out[f"D_{summ}_pvn_dir@{u:g}"] = (agg["R"] - agg["L"]) / 2
                    else:
                        out[f"D_{summ}_pvc_dsurv@{u:g}"] = -(agg["R"] + agg["L"])
        return out

    def _eligible_weights(self, name, pelig):
        a, b, w = self.cw[name]
        df = pd.DataFrame({"key": self.cellkey, "arm": self.armv, "pe": pelig})
        s = df[df.arm.isin([a, b])].groupby(["key", "arm"]).pe.sum().unstack()
        key = w[C.CELL].astype(str).agg("|".join, axis=1)
        mn = np.minimum(s[a], s[b]).reindex(key.to_numpy()).to_numpy()
        w2 = w.copy()
        w2["w"] = mn / pd.Series(mn).groupby(w.mouse.to_numpy()).transform("sum").to_numpy()
        return w2


# --------------------------------------------------------------------------------------------------- per dataset
DES, CFG, TRUTH, TAU, NBOOT = None, None, None, None, None


def q_from_delta(delta_m, sl):
    """Exact map from the C primary per-mouse truth delta_m (pp) to q_m, given slopes sl = (T0, S+, S-)."""
    T0, Sp, Sm = sl
    q = np.where(delta_m >= T0, (delta_m - T0) / (Sp - T0), (delta_m - T0) / (Sm - T0))
    q = np.minimum(np.abs(q), 1.0)
    return np.where(delta_m >= T0, q, -q)


def truth_at(q, tr):
    T0, Sp, Sm = tr
    return T0 + np.where(q >= 0, q * (Sp - T0), -q * (Sm - T0))


def one_dataset(args):
    si, k, seed = args
    sc = SCENARIOS[si]
    rng = np.random.default_rng(np.random.SeedSequence([seed, si, k]))
    q_m = None
    tr = TRUTH[sc["name"]]
    if sc["kind"] == "flip":
        dm = sc["delta"] + TAU * rng.standard_normal(len(DES.mice))
        q_m = q_from_delta(dm, tr["C_pvn_dir"])
    bs, br, side, rt = DES.simulate(rng, sc, q_m)
    t = DES.template.copy()
    t["response_side"], t["rt_s"] = side, rt
    rec = {"scenario": sc["name"], "k": k}
    chk = {"pre_onset_unaffected": K.pre_onset_unaffected(bs, br, side, rt, DES.onset, DES.sign),
           "censoring_ok": K.censoring_ok(side, rt, DES.deadline)}
    cond = {q: float(np.mean(truth_at(q_m, v) if q_m is not None else v[0])) for q, v in tr.items()}
    # ---- C
    d = C.with_arm(t, "in_primary_coherence")
    pvals = {}
    for name, (a, b, sym) in C_CONTRASTS.items():
        dd = d[d.signs_scheduled_symmetric] if sym else d
        pm, _ = C.per_mouse(dd, a, b, C.CELL)
        chk[f"C_{name}_sum_zero"] = K.components_sum_to_zero(pm)
        rows = C.group_rows(pm, "sim", name, rng_seed=int(rng.integers(2**31)), n_boot=NBOOT if name == "pvn" else 0)
        for r in rows:
            ep = {"Delta_direction": "dir", "Delta_R": "R", "Delta_L": "L", "Delta_unresponded": "U"}[r["endpoint"]]
            qn = f"C_{name}_{ep}"
            if qn not in tr:
                continue
            tag = "boot" if "bootstrap" in r["method"] else "t"
            rec[f"{qn}|{tag}_lo"], rec[f"{qn}|{tag}_hi"] = r["ci_low"], r["ci_high"]
            if tag == "t":
                rec[f"{qn}|est"], rec[f"{qn}|p"], rec[f"{qn}|cond"] = r["estimate"], r["p_value"], cond[qn]
        if name == "pvn":
            for m, v in zip(pm.mouse, pm.Delta_direction):
                rec[f"mouse_est|{m}"] = v
        pvals[name] = rec[f"C_{name}_dir|p"]
    h = C.holm(pvals)
    for name in pvals:
        rec[f"C_{name}_dir|p_holm"] = h.get(name, np.nan)
    # ---- D
    al = D.aligned(t, CFG)
    for summ in ("all_scheduled", "onset_eligible"):
        for comp in (("pos_vs_neg", "pos_vs_ctrl") if sc["kind"] == "slow" else ("pos_vs_neg",)):
            cur, _ = D.estimate(al, GRID_D, summ, comp, "all")
            for kk, v in K.cif_checks(cur, summ).items():
                if isinstance(v, bool):
                    chk[f"D_{summ}_{comp}_{kk}"] = v
            con = D.contrast_curves(cur, comp)
            for u in GRID_D:
                cu = con[np.isclose(con.t, u)]
                if comp == "pos_vs_neg":
                    qn, vals = f"D_{summ}_pvn_dir@{u:g}", 100 * cu.d_direction.to_numpy()
                elif u == GRID_D[-1]:
                    qn, vals = f"D_{summ}_pvc_dsurv@{u:g}", 100 * cu.d_survival.to_numpy()
                else:
                    continue
                n, m, s, lo, hi = D.tci(vals)
                rec[f"{qn}|est"], rec[f"{qn}|t_lo"], rec[f"{qn}|t_hi"], rec[f"{qn}|cond"] = m, lo, hi, cond[qn]
    for kk, v in chk.items():
        rec[f"check|{kk}"] = bool(v)
    return rec


def _init(des, cfg, truth, tau, nboot):
    global DES, CFG, TRUTH, TAU, NBOOT
    DES, CFG, TRUTH, TAU, NBOOT = des, cfg, truth, tau, nboot


def run_scenarios(sis, n, seed, workers):
    tasks = [(si, k, seed) for si in sis for k in range(n)]
    ctx = mp.get_context("fork")
    with ctx.Pool(workers, initializer=_init, initargs=(DES, CFG, TRUTH, TAU, NBOOT)) as pool:
        return list(pool.imap_unordered(one_dataset, tasks, chunksize=2))


# ------------------------------------------------------------------------------------------------------- summary
def population_truth(tr, sc, tau, seed, n_draw=200_000):
    """quantity -> population truth (pp): mean over mice of E[truth_m(q(delta_m))]."""
    if sc["kind"] != "flip":
        return {q: float(np.mean(v[0])) for q, v in tr.items()}
    rng = np.random.default_rng(np.random.SeedSequence([seed, 999]))
    z = rng.standard_normal((n_draw, len(tr["C_pvn_dir"][0])))
    q = q_from_delta(sc["delta"] + tau * z, tr["C_pvn_dir"])
    return {qn: float(np.mean(truth_at(q, v))) for qn, v in tr.items()}


def summarize(df, poptruth, alpha=0.05):
    rows = []
    for scn, g in df.groupby("scenario"):
        n = len(g)
        quants = sorted({c.split("|")[0] for c in g.columns if c.endswith("|est") and g[c].notna().all()})
        for qn in quants:
            est = g[f"{qn}|est"]
            tp = poptruth[scn][qn]
            r = {"scenario": scn, "quantity": qn, "n_datasets": n, "truth_population_pp": tp,
                 "truth_conditional_mean_pp": g[f"{qn}|cond"].mean(), "mean_estimate_pp": est.mean(),
                 "bias_vs_population_pp": est.mean() - tp, "bias_mcse_pp": est.std(ddof=1) / np.sqrt(n),
                 "bias_vs_conditional_pp": (est - g[f"{qn}|cond"]).mean(), "empirical_sd_pp": est.std(ddof=1),
                 "mean_t_ci_width_pp": (g[f"{qn}|t_hi"] - g[f"{qn}|t_lo"]).mean()}
            for tag in ("t", "boot"):
                if f"{qn}|{tag}_lo" not in g:
                    continue
                for tname, tv in (("population", tp), ("conditional", g[f"{qn}|cond"])):
                    cov = ((g[f"{qn}|{tag}_lo"] <= tv) & (tv <= g[f"{qn}|{tag}_hi"])).sum()
                    lo, hi = K.binom_ci(cov, n)
                    r[f"coverage_{tag}_{tname}"], r[f"coverage_{tag}_{tname}_mc_lo"], r[f"coverage_{tag}_{tname}_mc_hi"] = cov / n, lo, hi
            for pc in ("p", "p_holm"):
                if f"{qn}|{pc}" in g:
                    kk = (g[f"{qn}|{pc}"] < alpha).sum()
                    lo, hi = K.binom_ci(kk, n)
                    r[f"reject_{pc}"], r[f"reject_{pc}_mc_lo"], r[f"reject_{pc}_mc_hi"] = kk / n, lo, hi
            rows.append(r)
        hp = [c for c in g.columns if c.endswith("|p_holm")]
        kk = (g[hp] < alpha).any(axis=1).sum()
        lo, hi = K.binom_ci(kk, n)
        rows.append({"scenario": scn, "quantity": "holm_family_any_rejection", "n_datasets": n,
                     "reject_p_holm": kk / n, "reject_p_holm_mc_lo": lo, "reject_p_holm_mc_hi": hi})
    return pd.DataFrame(rows)


def figure(summary, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = summary[summary.quantity == "C_pvn_dir"].set_index("scenario")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8), layout="constrained")
    xs = [0, 3, 6, 10]
    names = ["no_effect", "dir3", "dir6", "dir10"]
    for col, mk, lab in (("reject_p", "o", "unadjusted p < 0.05"), ("reject_p_holm", "s", "Holm p < 0.05")):
        y = [s.loc[n, col] for n in names]
        e = [[s.loc[n, col] - s.loc[n, col + "_mc_lo"] for n in names], [s.loc[n, col + "_mc_hi"] - s.loc[n, col] for n in names]]
        ax[0].errorbar(xs, y, yerr=e, fmt=mk + "-", capsize=3, label=lab)
    ax[0].axhline(0.05, color="k", lw=0.6, ls=":")
    ax[0].set(xlabel="true mean Δdirection δ (pp)", ylabel="rejection rate", ylim=(0, 1.02),
              title="C primary test (n = 10 mice)\nbars = 95% Monte Carlo CI")
    ax[0].legend(frameon=False, fontsize=7)
    order = [n for n in ["no_effect", "dir3", "dir6", "dir10", "censor", "timelocal"] if n in s.index]
    for j, (col, lab) in enumerate((("coverage_t_population", "t CI"), ("coverage_boot_population", "bootstrap"))):
        y = [s.loc[n, col] for n in order]
        e = [[s.loc[n, col] - s.loc[n, col + "_mc_lo"] for n in order], [s.loc[n, col + "_mc_hi"] - s.loc[n, col] for n in order]]
        ax[1].errorbar(np.arange(len(order)) + 0.15 * j, y, yerr=e, fmt="o", capsize=3, label=lab)
    ax[1].axhline(0.95, color="k", lw=0.6, ls=":")
    ax[1].set_xticks(range(len(order)), order, rotation=30)
    ax[1].set(ylabel="coverage of population truth", ylim=(0.7, 1.0), title="C primary 95% intervals")
    ax[1].legend(frameon=False, fontsize=7)
    io.savefig(fig, path, dpi=300)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------------------------------------- main
def main(argv=None):
    global DES, CFG, TRUTH, TAU, NBOOT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--n-datasets", type=int, required=True, help="datasets per scenario (fixed before the run)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--scratch", help="pilot/test output directory (never marked COMPLETE)")
    args = ap.parse_args(argv)
    timer = io.Timer()
    run = io.run_dir(args.run_id)
    t, CFG = io.load_trials(run)
    if args.scratch:
        out = Path(args.scratch) / SUB
        figdir = Path(args.scratch)
        out.mkdir(parents=True, exist_ok=True)
    else:
        out = io.stage_dir(run, STAGE) / SUB
        figdir = io.figure_dir(args.run_id)
        if (out / "COMPLETE").exists():
            sys.exit(f"{out} is complete")
        out.mkdir(exist_ok=True)
    if any(out.iterdir()):
        sys.exit(f"refusing to write: {out} is not empty")
    seed = int(CFG["control_alignment"]["seed"])
    NBOOT = int(CFG["inference"]["bootstrap_resamples"])
    DES = Design(t, CFG)
    t_design = timer.seconds

    # exact truths (T0 at q = 0; S+ at q = +1; S- at q = -1) per scenario
    TRUTH = {}
    base = DES.truth({"kind": "none"})
    for sc in SCENARIOS:
        if sc["kind"] == "flip":
            sp, sm = DES.truth(sc, 1.0), DES.truth(sc, -1.0)
            TRUTH[sc["name"]] = {q: (base[q], sp[q], sm[q]) for q in base}
        else:
            v = DES.truth(sc)
            TRUTH[sc["name"]] = {q: (v[q],) for q in v}
    t_truth = timer.seconds

    # stage 1: null; derive tau
    TAU = 0.0
    res = run_scenarios([0], args.n_datasets, seed, args.workers)
    null = pd.DataFrame(res)
    var_m = null[[c for c in null if c.startswith("mouse_est|")]].var(ddof=1)
    cpm = pd.read_csv(run / "behaviour" / "per_mouse.csv")
    sd_obs = float(cpm[(cpm.analysis_set == "primary_coherence") & (cpm.contrast == "positive_vs_negative")].Delta_direction.std(ddof=1))
    TAU = float(np.sqrt(max(sd_obs**2 - var_m.mean(), 0.0)))
    t_null = timer.seconds
    # stage 2: the rest, with tau fixed
    res += run_scenarios(list(range(1, len(SCENARIOS))), args.n_datasets, seed, args.workers)
    df = pd.DataFrame(res).sort_values(["scenario", "k"])
    t_all = timer.seconds

    poptruth = {sc["name"]: population_truth(TRUTH[sc["name"]], sc, TAU, seed) for sc in SCENARIOS}
    summary = summarize(df, poptruth)
    chk_cols = [c for c in df if c.startswith("check|")]
    check_rates = {c.split("|", 1)[1]: [int(df[c].dropna().astype(bool).sum()), int(df[c].notna().sum())] for c in chk_cols}
    n_tot = len(df)
    checks = {f"all_datasets_{k}": v[0] == v[1] > 0 for k, v in check_rates.items()}
    checks["n_datasets_as_fixed"] = bool((df.groupby("scenario").size() == args.n_datasets).all())
    checks["null_truths_zero"] = bool(all(abs(v) < 1e-9 for q, v in poptruth["no_effect"].items() if q.startswith("C_")))
    checks["dir_scenarios_C_primary_truth_equals_delta"] = bool(all(
        abs(poptruth[sc["name"]]["C_pvn_dir"] - sc["delta"]) < 0.05 for sc in SCENARIOS if sc["name"].startswith("dir")))

    outputs = [io.write_csv(out / "datasets.csv", df), io.write_csv(out / "summary.csv", summary)]
    meta = {"run_id": args.run_id, "n_datasets_per_scenario": args.n_datasets, "workers": args.workers, "seed": seed,
            "bootstrap_resamples": NBOOT, "tau_pp": TAU, "sd_obs_pp": sd_obs, "mean_null_within_mouse_var_pp2": float(var_m.mean()),
            "null_within_mouse_sd_pp": var_m.pow(0.5).round(3).to_dict(), "population_truth_pp": poptruth,
            "check_pass_counts": check_rates, "n_datasets_total": n_tot, "grid_D": GRID_D.tolist(), "scenarios": SCENARIOS,
            "runtime_s": {"design": t_design, "truth": t_truth - t_design, "null_stage": t_null - t_truth,
                          "other_scenarios": t_all - t_null, "total_before_writing": t_all}}
    outputs.append(io.write_json(out / "meta.json", meta))
    outputs.append(figure(summary, figdir / "validation_g1_power_coverage.png"))
    passed = all(checks.values())
    print(json.dumps({"checks": checks, "tau": TAU, "runtime": meta["runtime_s"]}, indent=1, default=str))
    cmd = "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.validation " + " ".join(argv if argv is not None else sys.argv[1:])
    inputs = {"trial_table": CFG["hashes"]["trial_table"], "analysis_config": io.sha256_file(run / "data" / "analysis_config.json"),
              "behaviour_per_mouse": io.sha256_file(run / "behaviour" / "per_mouse.csv")}
    man = io.stage_manifest("validation/g1", cmd, inputs, outputs, checks, timer.seconds, extra={"status": "exploratory", "package": "G1 only"})
    if args.scratch:
        io.write_json(out / "manifest.json", man)
        return passed
    return io.mark_complete(out, man, passed)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
