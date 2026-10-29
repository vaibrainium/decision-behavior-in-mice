"""DDM evidence accumulation driven by the current motion-energy inputs, UCLA and UW side by side (model check).

Inputs: ddm_inputs_global.npz (v1, responded trials only, D003), 1 ms inputs as the fits use them (primacy.stimuli).
Parameters: the primary common model L0U0V1Z0G1, control-split fit (fits_resp_final), one dense mouse per rig.

Rows
  A  mean input (motion energy, % coherence) on control trials per coherence, as fed to the simulator
  B  noise-free accumulated input with unit gain: cumsum(input) * dt, per coherence (same units on both rigs if the
     per-rig calibration is right)
  C  noise-free accumulated pulse component (input with pulse - input without), rightward pulses at 0% coherence,
     per pulse time
  D  example trajectories with the mouse's fitted parameters: 0% coherence early rightward pulse trials, each simulated
     with and without its pulse using the same diffusion noise and drift-variability draw; bounds 0 and a
  E  control trials: observed vs simulated (full model incl. fast guesses, 20 repetitions) P(right) and mean RT

The trajectory function repeats the equations of src/ddm/simulator._simulate_ddm_trials_numba (no leak, no urgency in
this variant) and is checked against it: with identical noise it must reproduce every RT and choice.

Output: dissemination/figures/qc/ddm_accumulation_examples_<date>.{png,pdf}
Usage:  python -m scripts.ddm.ddm_accumulation_examples
"""

from datetime import date

import matplotlib.pyplot as plt
import numpy as np

from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, to_ms
from scripts.ddm.primacy import load_fit, make_model, no_pulse_frames, simulate_outcomes, stimuli
from scripts.ddm.pulse_psychometric import OUT, PROCESSED
from src.ddm.simulator import _simulate_ddm_trials_numba

MICE = {"ucla": "PSUIM6", "uw": "DBM6"}
VARIANT, FITS = "L0U0V1Z0G1", "fits_resp_final"
DT, T_SHOW, N_EXAMPLES, SEED = 0.001, 2.0, 12, 0
COHS = (0, 9, 18, 36, 100)
STAGES = {1: "early", 2: "middle", 3: "late"}


def trajectories(stim, noise, sv_draws, p):
    """Evidence paths (n, T) of the L0U0 model; NaN after the bound is hit. Same update as the numba kernel."""
    n, T = stim.shape
    out = np.full((n, T), np.nan)
    rt, ch = np.full(n, np.nan), np.full(n, np.nan)
    sp = p["z"] * p["a"]
    for i in range(n):
        e = np.float32(sp)
        out[i, 0] = e
        off = p["drift_offset"] + sv_draws[i]
        for t in range(1, T):
            e = e + (p["drift_gain"] * stim[i, t - 1] + off) * DT + noise[i, t - 1]
            out[i, t] = e
            if e >= p["a"]:
                rt[i], ch[i] = t * DT + p["ndt"], 1.0
                break
            if e <= 0.0:
                rt[i], ch[i] = t * DT + p["ndt"], 0.0
                break
    return out, rt, ch


def main():
    inp = responded_only(load_inputs(PROCESSED / "ddm/ddm_inputs_global.npz"))
    coh = np.round(inp["signed_coherence"] * 100).astype(int)
    sched = inp["sched_pulse_type"].astype(int)
    rng = np.random.default_rng(SEED)
    fig, ax = plt.subplots(6, 2, figsize=(12, 24))
    colours = plt.cm.viridis(np.linspace(0, 0.9, len(COHS)))
    for j, (rig, mouse) in enumerate(MICE.items()):
        p = load_fit(PROCESSED / "ddm" / FITS, mouse, VARIANT, "control", False, None, None, responded=True)["parameters"]
        assert p.get("leak_rate", 0) == 0 and p.get("time_constant", 0) == 0
        rig_rows = inp["data_source"] == rig
        t = np.arange(int(T_SHOW / DT)) * DT

        # A, B: control trials of the whole rig, per coherence
        for c, col in zip(COHS, colours):
            rows = np.flatnonzero(rig_rows & (sched == 0) & (coh == c))
            x = stimuli(inp, rows)[0][:, : len(t)].astype(float) * 100
            ax[0, j].plot(t, x.mean(0), color=col, label=f"{c}% (n={len(rows)})")
            ax[1, j].plot(t, np.cumsum(x.mean(0)) * DT, color=col, label=f"{c}%")
        ax[0, j].set_title(f"A {rig.upper()}: mean input, control trials", fontsize=10)
        ax[0, j].set_ylabel("motion energy (% coh)")
        ax[1, j].set_title(f"B {rig.upper()}: accumulated input, unit gain, no noise", fontsize=10)
        ax[1, j].set_ylabel("cumsum(input) x dt (% coh x s)")

        # C: pulse component at 0% coherence, rightward pulses
        for st, ls in STAGES.items():
            rows = np.flatnonzero(rig_rows & (sched == st) & (coh == 0))
            if not len(rows):
                continue
            w, wo = stimuli(inp, rows)
            d = (w[:, : len(t)].astype(float) - wo[:, : len(t)]) * 100
            ax[2, j].plot(t, np.cumsum(d.mean(0)) * DT, label=f"{ls} (n={len(rows)})")
        ax[2, j].set_title(f"C {rig.upper()}: accumulated pulse component, 0% coh, rightward", fontsize=10)
        ax[2, j].set_ylabel("cumsum(pulse input) x dt (% coh x s)")

        # D: example trajectories, mouse parameters, with vs without pulse (common random numbers)
        rows = np.flatnonzero((inp["subject_id"] == mouse) & (sched == 1) & (coh == 0))[:N_EXAMPLES]
        w, wo = stimuli(inp, rows)
        T = w.shape[1]
        noise = rng.normal(0, np.sqrt(p["variance"] * DT), (len(rows), T - 1)).astype(np.float32)
        sv = rng.normal(0, p["sv"], len(rows)).astype(np.float32)
        tw, rw, cw = trajectories(w, noise, sv, p)
        two, rwo, cwo = trajectories(wo, noise, sv, p)
        # check against the model's own kernel with the same random numbers
        zeros = np.zeros(len(rows), np.float32)
        kr, kc = _simulate_ddm_trials_numba(w.astype(np.float32), noise, sv, zeros, p["drift_gain"], p["drift_offset"], p["a"], p["z"],
                                           p["ndt"], DT, 0.0, 0.0, 0.0, 0.0)
        ok = np.allclose(kr, rw, equal_nan=True, atol=1e-6) and np.array_equal(np.nan_to_num(kc, nan=-1), np.nan_to_num(cw, nan=-1))
        print(f"{mouse}: trajectory function reproduces the simulator kernel: {ok}")
        on = np.median(inp["pulse_onset_frame0"][rows]) / 60 if "pulse_onset_frame0" in inp else None
        for k in range(len(rows)):
            ax[3, j].plot(t, two[k, : len(t)], color="0.6", lw=0.7)
            ax[3, j].plot(t, tw[k, : len(t)], color="#c0392b", lw=0.9)
        ax[3, j].axhline(p["a"], color="k"); ax[3, j].axhline(0, color="k")
        ax[3, j].axhline(p["z"] * p["a"], color="k", ls=":", lw=0.6)
        ax[3, j].set_title(f"D {mouse}: 0% coh, early rightward pulse (red) vs same noise, no pulse (grey)\n"
                           f"{len(rows)} trials; kernel check {'passed' if ok else 'FAILED'}", fontsize=9)
        ax[3, j].set_ylabel("decision variable")
        ax[3, j].text(0.98, 0.02, f"a={p['a']:.2f} z={p['z']:.2f} gain={p['drift_gain']:.2f} offset={p['drift_offset']:.2f}\n"
                      f"sv={p['sv']:.2f} ndt={p['ndt']:.3f} s; decision time shown (RT = DT + ndt)",
                      transform=ax[3, j].transAxes, ha="right", va="bottom", fontsize=7)
        # pulse component per trial in drift units for the same trials (how big the pulse is relative to noise)
        d = (w[:, : len(t)].astype(float) - wo[:, : len(t)]) * p["drift_gain"]
        ax[4, j].plot(t, np.cumsum(d, axis=1).T * DT, color="#c0392b", lw=0.6)
        ax[4, j].plot(t, np.sqrt(t * p["variance"]), "k--", lw=1, label="diffusion noise SD, sqrt(t)")
        ax[4, j].set_title(f"D' {mouse}: accumulated pulse in decision units (drift_gain x pulse) vs noise SD", fontsize=9)
        ax[4, j].set_ylabel("decision units"); ax[4, j].legend(fontsize=7, frameon=False)

        # E: control trials, observed vs simulated
        rows = np.flatnonzero((inp["subject_id"] == mouse) & (sched == 0))
        model = make_model(VARIANT, rig, False, responded=True)
        sim = simulate_outcomes(model, p, stimuli(inp, rows)[0], inp["condition"][rows], 20, SEED)
        sim = sim[(sim.choice >= 0) & (sim.rt <= 5)]
        sc = coh[rows][sim.trial.to_numpy()]
        levels = np.unique(coh[rows])
        obs_p = [np.mean(inp["choice"][rows][coh[rows] == c] == 1) for c in levels]
        obs_rt = [np.mean(inp["rt"][rows][coh[rows] == c]) for c in levels]
        sim_p = [np.mean(sim.choice.to_numpy()[sc == c] == 1) for c in levels]
        sim_rt = [np.mean(sim.rt.to_numpy()[sc == c]) for c in levels]
        a2 = ax[5, j].twinx()
        ax[5, j].plot(levels, obs_p, "ko", label="P(right) data"); ax[5, j].plot(levels, sim_p, "k-", label="P(right) model")
        a2.plot(levels, obs_rt, "s", color="C1", label="mean RT data"); a2.plot(levels, sim_rt, "-", color="C1", label="mean RT model")
        ax[5, j].set_ylabel("P(right)"); a2.set_ylabel("mean RT (s)", color="C1")
        ax[5, j].set_xlabel("signed coherence (%)")
        ax[5, j].set_title(f"E {mouse}: control trials, data (points) vs fitted model (lines)", fontsize=10)
        ax[5, j].legend(fontsize=7, loc="upper left", frameon=False); a2.legend(fontsize=7, loc="lower right", frameon=False)
        for r in range(5):
            ax[r, j].set_xlabel("time from stimulus onset (s)")
            ax[r, j].axhline(0, color="0.7", lw=0.5)
        ax[0, j].legend(fontsize=7, frameon=False); ax[1, j].legend(fontsize=7, frameon=False); ax[2, j].legend(fontsize=7, frameon=False)
    for r in range(3):  # same y range across rigs for A-C
        lo = min(ax[r, 0].get_ylim()[0], ax[r, 1].get_ylim()[0]); hi = max(ax[r, 0].get_ylim()[1], ax[r, 1].get_ylim()[1])
        ax[r, 0].set_ylim(lo, hi); ax[r, 1].set_ylim(lo, hi)
    fig.suptitle("DDM accumulation with the current motion-energy inputs (v1), UCLA vs UW; primary model, control fits", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    stem = OUT / f"ddm_accumulation_examples_{date.today().isoformat()}"
    fig.savefig(f"{stem}.png", dpi=130)
    fig.savefig(f"{stem}.pdf")
    print(stem)


if __name__ == "__main__":
    main()
