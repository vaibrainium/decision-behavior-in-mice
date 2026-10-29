"""Exploratory illustration: do race / leaky competing accumulator (LCA) dynamics change the predicted pulse signatures?
(plan .agents/plans/2026-10-29-pulse-weight-joint.md, step 5; author 2026-10-29: "should we also test LCA families?")

NOT a fit. Two accumulators, right (x1) and left (x2), start at 0, 1 ms steps:
    x1 += (c0 + I/2 - k x1 - beta x2) dt + e1,    x2 += (c0 - I/2 - k x2 - beta x1) dt + e2,    I = g x motion energy + offset
e1, e2 ~ N(0, SIGMA^2 dt) with correlation rho; optional floor at 0 (rectify); the first to reach theta decides,
RT = decision time + ndt. With rho = -1, k = beta = 0 and no floor, x1 - x2 is the DDM with drift I, unit variance and
bounds +-2 theta from a midway start (a = 4 theta, z = 0.5); checked trial by trial against the simulator kernel.
Variants: the DDM limit (no sv), races with rho -0.5 and 0, and floored LCAs (Usher & McClelland 2001): balanced
(k = beta), leak-dominant (recency), inhibition-dominant (primacy); and LCAs with a shared baseline input c0 > 0 as in
Kirkpatrick, Turner & Sederberg 2021 (Psychol Rev 128:1051; their NV LCA, fitted k ~ 4.5 /s, beta ~ 5.4 /s after
dividing by tau = 0.1 s). c0 is set so the common-mode equilibrium c0 / (k + beta) is BASE x theta (both accumulators
settle halfway to the bound without evidence), so it follows theta during matching.

Per mouse (PSUIM6, PSUIM7, DBM6) and variant: ndt, fast-guess parameters and the offset/gain ratio come from the primary
joint fit (fits_joint_unfreeze_integrators, all); theta and g are matched to the mouse's control trials by a coarse grid
on the responded-only likelihood (as pulse_leak_urgency_signatures.match; N_REPS_MATCH reps, grid points with > MAX_NONRESP
simulated non-responses rejected). The matched model is simulated on the mouse's control and pulse trials (N_REPS reps)
and scored with the statistics of scripts/ddm/pulse_joint_signatures.py, plus the effect per pulse time (primacy check).

Outputs: dissemination/figures/qc/pulse_lca_signatures_<date>.{png,pdf}, _windows.csv, _stage.csv, _match.csv
Usage:   python -m scripts.ddm.pulse_lca_signatures [--check_only]
"""

import argparse
import pickle
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numba import njit, prange

from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select
from scripts.ddm.primacy import make_model
from scripts.ddm.pulse_descriptive_package import effect
from scripts.ddm.pulse_joint_signatures import stats_of
from scripts.ddm.pulse_leak_urgency_signatures import BINS, MAX_NONRESP, STAGES, observed, pseudo_onsets
from scripts.ddm.pulse_psychometric import OUT
from src.ddm.ddm import apply_guesses
from src.ddm.simulator import _simulate_ddm_trials_numba

MICE = ("PSUIM6", "PSUIM7", "DBM6")
SIGMA, DT, SEED = 0.5, 0.001, 0
N_REPS_MATCH, N_REPS = 6, 60
VARIANTS = {  # name: (rho, k, beta, floor at 0, baseline as a fraction of theta)
    "DDM limit (no sv)": (-1.0, 0.0, 0.0, False, 0.0),
    "race rho -0.5": (-0.5, 0.0, 0.0, False, 0.0),
    "race rho 0": (0.0, 0.0, 0.0, False, 0.0),
    "LCA balanced k=beta=3": (0.0, 3.0, 3.0, True, 0.0),
    "LCA leak-dominant k=6 beta=1": (0.0, 6.0, 1.0, True, 0.0),
    "LCA inhibition-dominant k=1 beta=6": (0.0, 1.0, 6.0, True, 0.0),
    "LCA + baseline k=beta=3": (0.0, 3.0, 3.0, True, 0.5),
    "LCA + baseline k=4.5 beta=5.4 (KTS 2021)": (0.0, 4.5, 5.4, True, 0.5),
}
T_MULT = (0.15, 0.25, 0.4, 0.6, 1.0, 1.5, 2.2)
G_MULT = (0.5, 0.8, 1.2, 1.8, 2.7, 4.0, 6.0)
REFINE = (0.85, 1.0, 1.18)


@njit(parallel=True, cache=True)
def lca_trials(stim, z1, z2, rho, g, off, c0, k, beta, theta, ndt, dt, sigma, floor):
    n, T = stim.shape
    rt = np.full(n, np.nan, dtype=np.float32)
    ch = np.full(n, np.nan, dtype=np.float32)
    s = sigma * np.sqrt(dt)
    c = np.sqrt(max(0.0, 1.0 - rho * rho))
    for i in prange(n):
        x1 = 0.0
        x2 = 0.0
        for t in range(1, T):
            if np.isnan(stim[i, t - 1]):
                break
            inp = g * stim[i, t - 1] + off
            e1 = s * z1[i, t - 1]
            e2 = s * (rho * z1[i, t - 1] + c * z2[i, t - 1])
            n1 = x1 + (c0 + 0.5 * inp - k * x1 - beta * x2) * dt + e1
            n2 = x2 + (c0 - 0.5 * inp - k * x2 - beta * x1) * dt + e2
            if floor:
                n1 = max(n1, 0.0)
                n2 = max(n2, 0.0)
            x1, x2 = n1, n2
            if x1 >= theta:
                rt[i] = t * dt + ndt
                ch[i] = 1.0
                break
            if x2 >= theta:
                rt[i] = t * dt + ndt
                ch[i] = 0.0
                break
    return rt, ch


def check_ddm_limit(inputs: dict, p: dict, mouse: str) -> float:
    """Share of trials with identical choice and RT (within 1 ms) between the LCA kernel in the DDM limit and the
    simulator kernel, same noise (DDM noise n = e1 - e2)."""
    rows = np.flatnonzero(inputs["subject_id"] == mouse)[:2000]
    _, stim = select(inputs, rows)
    rng = np.random.default_rng(SEED)
    z1 = rng.standard_normal((len(rows), stim.shape[1] - 1)).astype(np.float32)
    theta = p["a"] / 4
    rt, ch = lca_trials(stim, z1, z1, -1.0, p["drift_gain"], p["drift_offset"], 0.0, 0.0, 0.0, theta, p["ndt"], DT, SIGMA, False)
    noise = (2 * SIGMA * np.sqrt(DT) * z1).astype(np.float32)  # e1 - e2 with e2 = -e1
    zeros = np.zeros(len(rows), np.float32)
    krt, kch = _simulate_ddm_trials_numba(stim, noise, zeros, zeros, p["drift_gain"], p["drift_offset"], p["a"], 0.5, p["ndt"], DT, 0.0, 0.0, 0.0)
    same = (np.nan_to_num(ch, nan=-1) == np.nan_to_num(kch, nan=-1)) & (np.abs(np.nan_to_num(rt, nan=-1) - np.nan_to_num(krt, nan=-1)) <= 1.01e-3)
    return float(same.mean())


def outcomes(model, stim, labels, draws, z1s, z2s, params: dict) -> pd.DataFrame:
    rho, k, beta, floor, base = params["variant"]
    c0 = base * params["theta"] * (k + beta)
    parts = []
    for r in range(len(z1s)):
        rt, ch = lca_trials(stim, z1s[r], z2s[r], rho, params["g"], params["off"], c0, k, beta, params["theta"], params["ndt"], DT, SIGMA, floor)
        sim = pd.DataFrame({"signed_coherence": labels, "rt": rt, "choice": ch, "trial": np.arange(len(labels))})
        parts.append(model._map_outcomes(apply_guesses(sim, params, draws[r])))
    return pd.concat(parts, ignore_index=True)


def match(model, base: dict, variant: tuple, data: dict, stim: np.ndarray, log: list, name: str, mouse: str) -> dict:
    rng = np.random.default_rng(SEED)
    z1s = [rng.standard_normal((stim.shape[0], stim.shape[1] - 1)).astype(np.float32) for _ in range(N_REPS_MATCH)]
    z2s = [rng.standard_normal((stim.shape[0], stim.shape[1] - 1)).astype(np.float32) for _ in range(N_REPS_MATCH)]
    draws = [rng.uniform(size=(stim.shape[0], 3)) for _ in range(N_REPS_MATCH)]

    def score(tm, gm):
        p = {**base, "variant": variant, "theta": base["a"] / 4 * tm, "g": base["drift_gain"] * gm, "off": base["drift_offset"] * gm}
        sim = outcomes(model, stim, data["condition"], draws, z1s, z2s, p)
        nonresp = float((sim.choice.to_numpy() < 0).mean())
        nll = float(model.likelihood_calc.compute_nll(sim.rt.to_numpy(), sim.choice.to_numpy(), data["rt"], data["choice"],
                                                      sim.signed_coherence.to_numpy(), data["condition"]))
        log.append({"mouse": mouse, "variant": name, "t_mult": tm, "g_mult": gm, "nll": nll, "nonresp": nonresp})
        return (np.inf if nonresp > MAX_NONRESP else nll), p
    best = (np.inf, None, 1.0, 1.0)
    for tm in T_MULT:
        for gm in G_MULT:
            v, p = score(tm, gm)
            if v < best[0]:
                best = (v, p, tm, gm)
    for ft in REFINE:
        for fg in REFINE:
            if (ft, fg) != (1.0, 1.0) and best[1] is not None:
                v, p = score(best[2] * ft, best[3] * fg)
                if v < best[0]:
                    best = (v, p, best[2] * ft, best[3] * fg)
    if best[1] is None:
        raise RuntimeError(f"{mouse} {name}: no grid point under the non-response cap")
    log.append({"mouse": mouse, "variant": name, "t_mult": best[2], "g_mult": best[3], "nll": best[0], "nonresp": np.nan, "chosen": True})
    return best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check_only", action="store_true")
    args = ap.parse_args()
    inputs = responded_only(load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz"))
    fits = {m: pickle.load(open(DDM / "fits_joint_unfreeze_integrators" / f"{m}_L0U0V1Z0G1_all.pkl", "rb"))["parameters"] for m in MICE}
    for m in MICE:
        print(f"{m}: DDM-limit LCA reproduces the simulator kernel on {check_ddm_limit(inputs, fits[m], m):.4f} of 2000 trials", flush=True)
    if args.check_only:
        return
    obs = observed(inputs, list(MICE))
    onsets = pseudo_onsets(obs)
    log, sims = [], {}
    for m in MICE:
        rig = obs.loc[obs.mouse == m, "rig"].iloc[0]
        model = make_model("L0U0V1Z0G1", rig, False, responded=True)
        crow = np.flatnonzero((inputs["subject_id"] == m) & (inputs["sched_pulse_type"] == 0))
        cdata, cstim = select(inputs, crow)
        keep = obs[obs.mouse == m].set_index("row")
        rows = keep.index.to_numpy()
        data, stim = select(inputs, rows)
        for name, variant in VARIANTS.items():
            p = match(model, fits[m], variant, cdata, cstim, log, name, m)
            rng = np.random.default_rng(SEED + 1)
            sim = outcomes(model, stim, data["condition"], [rng.uniform(size=(len(rows), 3)) for _ in range(N_REPS)],
                           [rng.standard_normal((len(rows), stim.shape[1] - 1)).astype(np.float32) for _ in range(N_REPS)],
                           [rng.standard_normal((len(rows), stim.shape[1] - 1)).astype(np.float32) for _ in range(N_REPS)], p)
            nonresp = float((sim.choice < 0).mean())
            sim = sim[sim.choice >= 0]
            mm = keep.loc[rows[sim.trial.to_numpy()]]
            sims.setdefault(name, []).append(pd.DataFrame({"row": mm.index, "mouse": m, "rig": rig, "coh": mm.coh.to_numpy(), "s": mm.s.to_numpy(),
                                                           "stage": mm.stage.to_numpy(), "choice": np.where(sim.choice.to_numpy() == 1, 1, -1),
                                                           "rt": sim.rt.to_numpy(), "onset": mm.onset.to_numpy()}))
            log[-1]["nonresp_sim"] = nonresp
            print(f"{m} {name}: theta x{log[-1]['t_mult']:.2f} gain x{log[-1]['g_mult']:.2f}, control NLL {log[-1]['nll']:.1f}, non-resp {nonresp:.3f}", flush=True)

    res = {"data": obs, **{k: pd.concat(v, ignore_index=True) for k, v in sims.items()}}
    win, stage = [], []
    for name, t in res.items():
        w, _, s3, ctl = stats_of(t, onsets)
        win.append(w.join(s3).join(ctl).assign(model=name))
        x = t.copy()
        st = []
        for (mouse, sg), on in onsets.items():  # effect per pulse time, all responses after the pulse (controls at the median onset)
            p_ = x[(x.mouse == mouse) & (x.stage == sg)]
            c_ = x[(x.mouse == mouse) & (x.stage == 0)].assign(stage=sg, onset=on)
            st.append(pd.concat([p_, c_]))
        st = pd.concat(st)
        st = st[st.rt - st.onset >= BINS[0]]
        stage.append(effect(st, ["mouse", "stage"]).assign(model=name))
    win = pd.concat(win).reset_index()
    stage = pd.concat(stage, ignore_index=True)
    match_log = pd.DataFrame(log)
    ctl_nll = match_log[match_log.get("chosen", False) == True].set_index(["mouse", "variant"]).nll.unstack("variant")  # noqa: E712
    pd.set_option("display.width", 220)
    summ = win.groupby("model", sort=False)[["0.3-1.2", "1.2-5", "rt_shift_toward_ms", "acc_36", "rt50"]].mean()
    summ["mice_late_negative"] = win.groupby("model", sort=False)["1.2-5"].apply(lambda v: int((v < 0).sum()))
    print("\n== mean over the 3 mice (pp, ms)\n" + summ.round(2).to_string())
    print("\n== per mouse 0.3-1.2 / 1.2-5\n" + win.pivot(index="mouse", columns="model", values="0.3-1.2").round(1).to_string()
          + "\n" + win.pivot(index="mouse", columns="model", values="1.2-5").round(1).to_string())
    print("\n== effect per pulse time (pp)\n" + stage.pivot_table(index=["mouse", "stage"], columns="model", values="effect").round(1).to_string())
    print("\n== matched control NLL minus the DDM limit (negative = LCA fits control trials better)\n"
          + ctl_nll.sub(ctl_nll["DDM limit (no sv)"], axis=0).round(1).to_string())

    stem = OUT / f"pulse_lca_signatures_{date.today().isoformat()}"
    win.round(4).to_csv(f"{stem}_windows.csv", index=False)
    stage.round(5).to_csv(f"{stem}_stage.csv", index=False)
    match_log.round(4).to_csv(f"{stem}_match.csv", index=False)
    names = list(res)
    cols = ["k"] + list(plt.cm.tab10(np.arange(len(names) - 1)))
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
    for k_, w in enumerate(["0.3-1.2", "1.2-5"]):
        piv = win.pivot(index="mouse", columns="model", values=w)[names]
        for i, n in enumerate(names):
            ax[k_].scatter(np.full(len(piv), i), piv[n], color=cols[i], s=18)
            ax[k_].plot([i - 0.3, i + 0.3], [piv[n].mean()] * 2, color="k", lw=2)
        ax[k_].axhline(0, color="0.6", lw=0.6)
        ax[k_].set_xticks(range(len(names))); ax[k_].set_xticklabels(names, rotation=55, ha="right", fontsize=7)
        ax[k_].set_ylabel("pulse effect (pp)"); ax[k_].set_title(f"{'AB'[k_]}  responses {w} s after the pulse; dots = mice", fontsize=10)
    sp = stage.groupby(["model", "stage"]).effect.mean().unstack("stage")  # effect() returns pp
    for i, n in enumerate(names):
        ax[2].plot(sp.columns, sp.loc[n], "o-", color=cols[i], lw=2.5 if n == "data" else 1.2, label=n)
    ax[2].set_xticks(list(STAGES)); ax[2].set_xticklabels(STAGES.values()); ax[2].axhline(0, color="0.6", lw=0.6)
    ax[2].set_ylabel("pulse effect (pp), mean over mice"); ax[2].set_title("C  effect per pulse time (primacy / recency)", fontsize=10)
    ax[2].legend(fontsize=6.5, frameon=False)
    fig.suptitle("Race and LCA variants matched to control trials (PSUIM6, PSUIM7, DBM6): pulse signatures vs data", fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=140); fig.savefig(f"{stem}.pdf")
    print(stem)


if __name__ == "__main__":
    main()
