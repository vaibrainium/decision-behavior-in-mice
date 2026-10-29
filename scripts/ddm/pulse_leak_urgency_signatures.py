"""Exploratory illustration: what do leak and urgency predict for the pulse effect against the time from the pulse to
the response, at this design? (plan .agents/plans/2026-10-28-pulse-leak-vs-urgency-research.md, step 3)

NOT a fit and NOT a power analysis. For a few mice, the primary control fit (L0U0V1Z0G1, fits_resp_final, control
split) is modified by imposing a leak rate (per s) or an urgency slope (per s; gain 1 + u t on the accumulated
evidence). Bound separation and drift gain are then re-matched to the mouse's control trials by a coarse grid on the
responded-only likelihood (control rows, N_REPS_MATCH repetitions; grid points with > MAX_NONRESP simulated
non-responses are rejected), so that each mechanism keeps roughly the fitted control accuracy and RTs. Each matched
model is simulated on the mouse's control and pulse trials (N_REPS repetitions, one seed), with the pulse component of
the input scaled by a gain w in PULSE_GAINS (1 = the motion-energy input as built; 4 = about the choice-matched gain
of package E in PSUIM6/7).

Statistics, identical for data and simulations (responded trials; symmetric cells; |coh| <= 36):
  profile:  per pulse stage, bins of (RT - pulse onset); effect = P(choice = pulse sign | pulse, coh, bin) -
            P(choice = pulse sign | control, coh, bin), pulse-count-weighted over (coh, sign). Control trials take the
            stage's median onset as a pseudo-onset.
  stage:    the same pooled over bins (early / middle / late).
  rt shift: RT quantiles, pulse minus control, given a choice toward or against the pulse (pulse_readout_checks).
Data uncertainty: bootstrap over trials (B resamples) per (stage, bin).

Outputs: dissemination/figures/qc/pulse_leak_urgency_signatures_<date>.{png,pdf}, _profile.csv, _stage.csv,
         _rtshift.csv, _match.csv; simulation cache in the scratch directory given by --cache.
Usage: python -m scripts.ddm.pulse_leak_urgency_signatures --cache <dir> [--mice PSUIM6 PSUIM7 DBM6] [--quick]
"""

import argparse
import pickle
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select
from scripts.ddm.primacy import gain_stimuli, load_fit, make_model, pulse_rows, simulate_outcomes
from scripts.ddm.pulse_energy_traces import TRIAL_TABLE
from scripts.ddm.pulse_psychometric import OUT, PROCESSED
from scripts.ddm.pulse_readout_checks import QUANTILES

FITS, BASE_VARIANT, SIM_VARIANT = "fits_resp_final", "L0U0V1Z0G1", "L1U1V1Z0G1"
VARIANTS = {"base": (0.0, 0.0), "leak 1/s": (1.0, 0.0), "leak 3/s": (3.0, 0.0), "leak 10/s": (10.0, 0.0),
            "urgency 0.3/s": (0.0, 0.3), "urgency 1/s": (0.0, 1.0), "urgency 3/s": (0.0, 3.0)}
PULSE_GAINS = (1.0, 4.0)
A_MULT = (0.3, 0.45, 0.65, 1.0, 1.5, 2.2)
G_MULT = (0.7, 1.0, 1.5, 2.2, 3.3, 5.0)
REFINE = (0.85, 1.0, 1.18)
N_REPS_MATCH, N_REPS, SEED, MAX_NONRESP, B = 6, 60, 0, 0.3, 300
A_LIMIT = 10.0  # validate_params: 0 < a < 10
BINS = [0.3, 0.6, 0.9, 1.2, 1.6, 2.2, 3.0, 5.0]
STAGES = {1: "early", 2: "middle", 3: "late"}
MAX_ABS_COH = 36
MIN_SIM_BIN = 100  # simulated bins with fewer pulse trials are not drawn (ratio noise)


def observed(inputs: dict, mice: list[str]) -> pd.DataFrame:
    """Responded trials of the given mice, symmetric cells, with pulse onset (scheduled for uw, recorded for ucla)."""
    tt = pd.read_csv(PROCESSED / TRIAL_TABLE, low_memory=False,
                     usecols=["trial_id", "signs_scheduled_symmetric", "scheduled_onset_s", "recorded_onset_s"]).set_index("trial_id")
    tt = tt.reindex(inputs["agg_code"].astype(str))
    assert not tt.signs_scheduled_symmetric.isna().any()
    t = pd.DataFrame({"row": np.arange(len(inputs["rt"])), "mouse": inputs["subject_id"], "rig": inputs["data_source"],
                      "coh": np.round(inputs["signed_coherence"] * 100).astype(int), "s": np.sign(inputs["sched_pulse_type"]).astype(int),
                      "stage": np.abs(inputs["sched_pulse_type"]).astype(int), "choice": np.where(inputs["choice"] == 1, 1, -1),
                      "rt": inputs["rt"], "onset": tt.scheduled_onset_s.fillna(tt.recorded_onset_s).to_numpy(),
                      "symmetric": tt.signs_scheduled_symmetric.to_numpy().astype(bool)})
    t = t[t.mouse.isin(mice) & t.symmetric & (t.coh.abs() <= MAX_ABS_COH)].drop(columns="symmetric")
    t.loc[t.stage == 0, "onset"] = np.nan
    assert not t.loc[t.stage > 0, "onset"].isna().any()
    return t.reset_index(drop=True)


def pseudo_onsets(t: pd.DataFrame) -> dict:
    return t[t.stage > 0].groupby(["mouse", "stage"]).onset.median().to_dict()


def with_bins(t: pd.DataFrame, onsets: dict) -> pd.DataFrame:
    """One row per (trial, stage) with time since (pseudo-)onset and its bin; control trials enter every stage the
    mouse has."""
    parts = []
    for (mouse, stage), onset in onsets.items():
        p = t[(t.mouse == mouse) & (t.stage == stage)]
        c = t[(t.mouse == mouse) & (t.stage == 0)].assign(stage=stage, onset=onset)
        parts.append(pd.concat([p, c]))
    x = pd.concat(parts, ignore_index=True)
    x["since"] = x.rt - x.onset
    x["bin"] = pd.cut(x.since, BINS, labels=False)  # NaN outside the bins; groupby drops those rows in the profile
    return x


def effect(x: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Pulse-count-weighted mean over (coh, sign) of P(choice = s | pulse) - P(choice = s | control) per `by` cell."""
    rows = []
    for key, g in x.groupby(by):
        ctrl = g[g.s == 0]
        for (c, s), p in g[g.s != 0].groupby(["coh", "s"]):
            k = ctrl[ctrl.coh == c]
            if len(k):
                rows.append(dict(zip(by, key)) | {"n": len(p), "d": (p.choice == s).mean() - (k.choice == s).mean()})
    r = pd.DataFrame(rows)
    return r.groupby(by).apply(lambda m: pd.Series({"effect": np.average(m.d, weights=m.n), "n_pulse": m.n.sum()}), include_groups=False).reset_index()


def rt_shift(x: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (mouse, c), g in x.groupby(["mouse", "coh"]):
        for s in (-1, 1):
            for rel, ch in (("toward pulse", s), ("against pulse", -s)):
                p, k = g[(g.s == s) & (g.choice == ch)].rt, g[(g.s == 0) & (g.choice == ch)].rt
                if len(p) >= 5 and len(k) >= 5:
                    d = 1000 * (np.quantile(p, QUANTILES) - np.quantile(k, QUANTILES))
                    rows += [{"mouse": mouse, "coh": c, "s": s, "choice": rel, "q": q, "n": len(p), "d_ms": v} for q, v in zip(QUANTILES, d)]
    r = pd.DataFrame(rows)
    return r.groupby(["mouse", "choice", "q"]).apply(lambda m: np.average(m.d_ms, weights=m.n), include_groups=False).rename("d_ms").reset_index()


def bootstrap_profile(x: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """SE over trial resamples (within mouse, stage, coh, sign) of the per-(mouse, stage, bin) effect."""
    base = effect(x, ["mouse", "stage", "bin"]).set_index(["mouse", "stage", "bin"])
    reps = []
    groups = [g.index.to_numpy() for _, g in x.groupby(["mouse", "stage", "coh", "s"])]
    for _ in range(B):
        idx = np.concatenate([rng.choice(g, len(g), replace=True) for g in groups])
        reps.append(effect(x.loc[idx], ["mouse", "stage", "bin"]).set_index(["mouse", "stage", "bin"]).effect)
    se = pd.concat(reps, axis=1).std(axis=1, ddof=1).rename("se")
    return pd.concat([base.effect, se, base.n_pulse], axis=1).reset_index()


# ---------------------------------------------------------------- matching and simulation

def control_nll(model, params: dict, data: dict, stimulus: np.ndarray, n_reps: int, seed: int) -> tuple[float, float]:
    np.random.seed(seed)
    model.simulator.clear_cache()
    model._labels = data["condition"]
    model.precompute(*stimulus.shape, n_reps=n_reps)
    result = model._simulate_condition(stimulus, params, n_reps)
    if result is None:
        return float("inf"), float("nan")
    nonresp = float((result["choice"].to_numpy() < 0).mean())
    nll = float(model.likelihood_calc.compute_nll(result["rt"].to_numpy(), result["choice"].to_numpy(), data["rt"], data["choice"],
                                                  result["signed_coherence"].to_numpy(), data["condition"]))
    return nll, nonresp


def match(model, base: dict, leak: float, urg: float, data: dict, stimulus: np.ndarray, log: list) -> dict:
    """Coarse grid on (a, drift_gain) multipliers, then one refinement, minimizing the control-trial NLL."""
    def score(am, gm):
        p = {**base, "leak_rate": leak, "time_constant": urg, "a": base["a"] * am, "drift_gain": base["drift_gain"] * gm}
        if not 0 < p["a"] < A_LIMIT:  # outside the simulator's allowed bound separation (src/ddm/ddm.py validate_params)
            log.append({"leak": leak, "urgency": urg, "a_mult": am, "g_mult": gm, "nll": np.inf, "nonresp": np.nan})
            return np.inf, p
        nll, nonresp = control_nll(model, p, data, stimulus, N_REPS_MATCH, SEED)
        log.append({"leak": leak, "urgency": urg, "a_mult": am, "g_mult": gm, "nll": nll, "nonresp": nonresp})
        return (np.inf if nonresp > MAX_NONRESP else nll), p
    best = (np.inf, None, 1.0, 1.0)
    for am in A_MULT:
        for gm in G_MULT:
            v, p = score(am, gm)
            if v < best[0]:
                best = (v, p, am, gm)
    for fa in REFINE:
        for fg in REFINE:
            if (fa, fg) != (1.0, 1.0):
                v, p = score(best[2] * fa, best[3] * fg)
                if v < best[0]:
                    best = (v, p, best[2] * fa, best[3] * fg)
    if best[1] is None:  # no grid point under the cap: take the lowest non-response point and flag it
        r = min((r for r in log if np.isfinite(r["nll"])), key=lambda r: r["nonresp"])
        best = (np.nan, {**base, "leak_rate": leak, "time_constant": urg, "a": base["a"] * r["a_mult"], "drift_gain": base["drift_gain"] * r["g_mult"]}, r["a_mult"], r["g_mult"])
    return best[1]


def simulate(model, params: dict, inputs: dict, obs: pd.DataFrame, mouse: str, cache: Path, name: str) -> pd.DataFrame:
    """Simulated responded trials (one row per trial x rep) for the mouse's control rows and, per pulse gain, its pulse
    rows; returns a table in the same format as `observed`."""
    path = cache / f"{mouse}_{name}.pkl"
    if path.exists():
        return pickle.load(open(path, "rb"))
    rows_c = obs.loc[(obs.mouse == mouse) & (obs.stage == 0), "row"].to_numpy()
    rows_p = obs.loc[(obs.mouse == mouse) & (obs.stage > 0), "row"].to_numpy()
    meta = obs.set_index("row")
    parts = []
    data_c, stim_c = select(inputs, rows_c)
    sim = simulate_outcomes(model, params, stim_c, data_c["condition"], N_REPS, SEED)
    sim = sim[sim.choice >= 0]
    m = meta.loc[rows_c[sim.trial.to_numpy()]]
    for w in PULSE_GAINS:  # controls do not depend on w; duplicated so each gain's table is self-contained
        parts.append(pd.DataFrame({"mouse": mouse, "coh": m.coh.to_numpy(), "s": 0, "stage": 0, "choice": np.where(sim.choice.to_numpy() == 1, 1, -1),
                                   "rt": sim.rt.to_numpy(), "onset": np.nan, "gain": w}))
    without, pulse = gain_stimuli(inputs, rows_p)
    for w in PULSE_GAINS:
        sim = simulate_outcomes(model, {**params, "noise_weight": float(w)}, (without, pulse), inputs["condition"][rows_p], N_REPS, SEED)
        sim = sim[sim.choice >= 0]
        m = meta.loc[rows_p[sim.trial.to_numpy()]]
        parts.append(pd.DataFrame({"mouse": mouse, "coh": m.coh.to_numpy(), "s": m.s.to_numpy(), "stage": m.stage.to_numpy(),
                                   "choice": np.where(sim.choice.to_numpy() == 1, 1, -1), "rt": sim.rt.to_numpy(), "onset": m.onset.to_numpy(), "gain": w}))
    out = pd.concat(parts, ignore_index=True)
    cache.mkdir(parents=True, exist_ok=True)
    pickle.dump(out, open(path, "wb"))
    return out


def control_summary(x: pd.DataFrame) -> dict:
    c = x[x.s == 0]
    acc = c[c.coh != 0].assign(correct=lambda d: d.choice == np.sign(d.coh)).groupby(c.coh.abs()).correct.mean()
    med = c.groupby(c.coh.abs()).rt.median()
    return {f"acc_{k}": v for k, v in acc.items()} | {f"rt50_{k}": v for k, v in med.items()}


def figure(prof_obs: pd.DataFrame, prof_sim: pd.DataFrame, mice: list[str], stem: Path):
    stages = sorted(prof_sim.stage.unique())
    fig, axes = plt.subplots(len(mice), len(stages), figsize=(5.2 * len(stages), 3.6 * len(mice)), squeeze=False)
    centers = [(BINS[i] + BINS[i + 1]) / 2 for i in range(len(BINS) - 1)]
    colours = {"base": "k", "leak 1/s": "#9ecae1", "leak 3/s": "#4292c6", "leak 10/s": "#08306b",
               "urgency 0.3/s": "#fcae91", "urgency 1/s": "#ef3b2c", "urgency 3/s": "#67000d"}
    for i, mouse in enumerate(mice):
        for j, stage in enumerate(stages):
            ax = axes[i, j]
            o = prof_obs[(prof_obs.mouse == mouse) & (prof_obs.stage == stage)]
            if not len(o):  # this mouse has no pulses at this stage
                ax.set_axis_off()
                continue
            if len(o):
                ax.errorbar([centers[int(b)] for b in o.bin], 100 * o.effect, yerr=100 * o.se, fmt="o", color="0.3", ms=4, capsize=2, label="data (±SE)", zorder=5)
            for name, col in colours.items():
                for w, ls in zip(PULSE_GAINS, (":", "-")):
                    s = prof_sim[(prof_sim.mouse == mouse) & (prof_sim.stage == stage) & (prof_sim.variant == name) & (prof_sim.gain == w)]
                    s = s[s.n_pulse >= MIN_SIM_BIN]  # drop bins the simulated model almost never reaches
                    if len(s):
                        ax.plot([centers[int(b)] for b in s.bin], 100 * s.effect, ls, color=col, lw=1.3, label=f"{name}, w={w:g}" if i == j == 0 else None)
            ax.axhline(0, color="0.7", lw=0.6, zorder=0)
            ax.set_title(f"{mouse}, {STAGES[stage]} pulse", fontsize=9)
            ax.set_xlabel("time from pulse onset to response (s)", fontsize=8)
            ax.set_ylabel("pulse effect (pp)", fontsize=8)
            ax.tick_params(labelsize=8)
    axes[0, 0].legend(fontsize=6, ncol=2, frameon=False)
    fig.suptitle("Illustration (not a fit): pulse effect vs time to response under imposed leak or urgency, control-matched; solid w=4, dotted w=1", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=180)
    fig.savefig(f"{stem}.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mice", nargs="+", default=["PSUIM6", "PSUIM7", "DBM6"])
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--quick", action="store_true", help="smoke test: tiny repetitions, base and one variant each")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    global N_REPS, N_REPS_MATCH, B, VARIANTS, A_MULT, G_MULT, REFINE
    if args.quick:
        N_REPS, N_REPS_MATCH, B = 3, 2, 5
        VARIANTS = {k: VARIANTS[k] for k in ("base", "leak 3/s", "urgency 1/s")}
        A_MULT, G_MULT, REFINE = (0.3, 0.65), (1.5, 3.3), (1.0,)
    inputs = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    obs = observed(inputs, args.mice)
    onsets = pseudo_onsets(obs)
    rng = np.random.default_rng(SEED)
    xo = with_bins(obs, onsets)
    prof_obs = bootstrap_profile(xo, rng)
    stage_obs = effect(xo, ["mouse", "stage"]).assign(variant="data", gain=np.nan)
    rts_obs = rt_shift(obs).assign(variant="data", gain=np.nan)
    print(prof_obs.round(4).to_string(index=False))

    prof, stage_rows, rts, matches, grids = [], [stage_obs], [rts_obs], [], []
    for mouse in args.mice:
        rig = obs.loc[obs.mouse == mouse, "rig"].iloc[0]
        base = load_fit(PROCESSED / "ddm" / FITS, mouse, BASE_VARIANT, "control", False, None, None, responded=True)["parameters"]
        rows_c = obs.loc[(obs.mouse == mouse) & (obs.stage == 0), "row"].to_numpy()
        data_c, stim_c = select(inputs, rows_c)
        model_fit = make_model(SIM_VARIANT, rig, False, responded=True)
        model_sim = make_model(SIM_VARIANT, rig, False)
        for name, (leak, urg) in VARIANTS.items():
            log = []
            if name == "base":
                params = {**base, "leak_rate": 0.0, "time_constant": 0.0}
                nll, nonresp = control_nll(model_fit, params, data_c, stim_c, N_REPS_MATCH, SEED)
                log.append({"leak": 0, "urgency": 0, "a_mult": 1, "g_mult": 1, "nll": nll, "nonresp": nonresp})
            else:
                mpath = args.cache / f"match_{mouse}_{name.replace(' ', '_').replace('/', '')}.pkl"
                if mpath.exists():
                    cached = pickle.load(open(mpath, "rb"))
                    params = {**base, "leak_rate": leak, "time_constant": urg, "a": cached["a"], "drift_gain": cached["drift_gain"]}
                    log.append({"leak": leak, "urgency": urg, "a_mult": cached["a_mult"], "g_mult": cached["g_mult"], "nll": cached["control_nll_match"],
                                "nonresp": cached["nonresp_match"], "cached": True})
                else:
                    params = match(model_fit, base, leak, urg, data_c, stim_c, log)
            ok = [r for r in log if np.isfinite(r["nll"]) and r["nonresp"] <= MAX_NONRESP]
            best = min(ok, key=lambda r: r["nll"]) if ok else min((r for r in log if np.isfinite(r["nll"])), key=lambda r: r["nonresp"])
            grids += [{"mouse": mouse, "variant": name, **r} for r in log]
            if name != "base" and not mpath.exists():
                args.cache.mkdir(parents=True, exist_ok=True)
                pickle.dump({"mouse": mouse, "variant": name, "a": params["a"], "drift_gain": params["drift_gain"], "a_mult": best["a_mult"], "g_mult": best["g_mult"],
                             "control_nll_match": best["nll"], "nonresp_match": best["nonresp"], "cap_ok": bool(ok), "n_grid": len(log)}, open(mpath, "wb"))
            sim = simulate(model_sim, params, inputs, obs, mouse, args.cache, name.replace(" ", "_").replace("/", ""))
            cs = control_summary(sim[sim.gain == PULSE_GAINS[0]])
            matches.append({"mouse": mouse, "variant": name, "leak": leak, "urgency": urg, "a": params["a"], "drift_gain": params["drift_gain"],
                            "a_mult": best["a_mult"], "g_mult": best["g_mult"], "control_nll_match": best["nll"], "nonresp_match": best["nonresp"],
                            "cap_ok": bool(ok), "n_grid": len(log)} | cs)
            print(mouse, name, {k: round(v, 3) for k, v in matches[-1].items() if isinstance(v, float)}, flush=True)
            for w in PULSE_GAINS:
                sw = sim[sim.gain == w].drop(columns="gain")
                xs = with_bins(sw, {k: v for k, v in onsets.items() if k[0] == mouse})
                prof.append(effect(xs, ["mouse", "stage", "bin"]).assign(variant=name, gain=w))
                stage_rows.append(effect(xs, ["mouse", "stage"]).assign(variant=name, gain=w))
                rts.append(rt_shift(sw).assign(variant=name, gain=w))
    prof_sim = pd.concat(prof, ignore_index=True)
    day = date.today().isoformat()
    stem = args.out / f"pulse_leak_urgency_signatures_{day}"
    args.out.mkdir(parents=True, exist_ok=True)
    pd.concat([prof_obs.assign(variant="data", gain=np.nan), prof_sim]).round(5).to_csv(f"{stem}_profile.csv", index=False)
    pd.concat(stage_rows).round(5).to_csv(f"{stem}_stage.csv", index=False)
    pd.concat(rts).round(2).to_csv(f"{stem}_rtshift.csv", index=False)
    pd.DataFrame(matches).round(4).to_csv(f"{stem}_match.csv", index=False)
    pd.DataFrame(grids).round(4).to_csv(f"{stem}_grid.csv", index=False)
    figure(prof_obs, prof_sim, args.mice, stem)
    print(pd.DataFrame(matches).round(3).to_string(index=False))
    print(pd.concat(stage_rows).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
