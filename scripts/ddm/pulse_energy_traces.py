"""Motion-energy traces around scheduled pulses, as fed to the DDM (stimulus check; no behavioural outcome is used
except the responded-only trial selection).

For each signed coherence: the mean motion energy (S + N, % coherence units) of positive- and negative-pulse trials,
aligned to the logged pulse onset, next to the mean of the control trials of the same rig and coherence taken at the
same frames (so the difference is the pulse-evoked energy). Rigs are pooled after subtracting their own control means
(rig as covariate only). Bottom row: peak pulse-evoked energy against the nominal coherence change (pulse at +-100%),
and the energy a sustained 100% coherence reaches, from each rig's onset response.

Output: dissemination/figures/qc/pulse_motion_energy_traces_<date>.{png,pdf}
Usage: python -m scripts.ddm.pulse_energy_traces
"""

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only

TRIAL_TABLE = "pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv"
FRAME = 1 / 60
PRE, POST = 12, 36  # frames before and after pulse onset
OUT = Path(__file__).resolve().parents[2] / "dissemination" / "figures" / "qc"


def aligned(me: np.ndarray, onset_idx: np.ndarray) -> np.ndarray:
    """(n, PRE + POST) windows around each trial's onset frame; NaN outside the 5 s replay."""
    out = np.full((len(me), PRE + POST), np.nan)
    for i, o in enumerate(onset_idx):
        lo, hi = o - PRE, o + POST
        a, b = max(lo, 0), min(hi, me.shape[1])
        out[i, a - lo:b - lo] = me[i, a:b]
    return out


def main():
    processed = Path(dir_config.data.processed)
    inp = responded_only(load_inputs(processed / "ddm/ddm_inputs_global.npz"))
    table = pd.read_csv(processed / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "onset_frame", "n_pulse_frames"]).set_index("trial_id")
    me = (inp["signal"].astype(float) + inp["noise"]) * 100
    sig = inp["signal"].astype(float) * 100
    coh, rig, sched = np.round(inp["signed_coherence"] * 100).astype(int), inp["data_source"], inp["sched_pulse_type"]
    pulse = sched != 0
    onset_idx = np.zeros(len(coh), int)
    onset_idx[pulse] = table.loc[inp["agg_code"][pulse].astype(str), "onset_frame"].to_numpy().astype(int) - 1

    # control mean per (rig, coherence), full 300-frame trace
    ctrl = {(r, c): me[(~pulse) & (rig == r) & (coh == c)].mean(axis=0) for r in np.unique(rig) for c in np.unique(coh)
            if ((~pulse) & (rig == r) & (coh == c)).any()}
    ctrl_s = {(r, c): sig[(~pulse) & (rig == r) & (coh == c)].mean(axis=0) for (r, c) in ctrl}

    levels = sorted(np.unique(coh))
    t = (np.arange(-PRE, POST)) * FRAME * 1000  # ms
    fig = plt.figure(figsize=(16, 13))
    gs = fig.add_gridspec(4, len(levels) // 2 + 1, hspace=0.45, wspace=0.3)
    peaks = []
    for k, c in enumerate(levels):
        ax = fig.add_subplot(gs[k // (len(levels) // 2 + 1), k % (len(levels) // 2 + 1)])
        for sign, colour in [(1, "tab:blue"), (-1, "tab:red")]:
            sel = np.flatnonzero(pulse & (coh == c) & (np.sign(sched) == sign))
            if not len(sel):
                continue
            raw = aligned(me[sel], onset_idx[sel])
            base = np.stack([aligned(ctrl[(rig[i], c)][None], onset_idx[i:i + 1])[0] for i in sel])
            base_s = np.stack([aligned(ctrl_s[(rig[i], c)][None], onset_idx[i:i + 1])[0] for i in sel])
            exp = aligned(sig[sel], onset_idx[sel]) - base_s
            ax.plot(t, np.nanmean(raw, 0), color=colour, lw=1.6, label=f"{'+' if sign > 0 else '−'} pulse (n={len(sel)})")
            ax.plot(t, np.nanmean(base, 0), color=colour, lw=1, ls=":", alpha=0.8)
            d = raw - base
            m, se = np.nanmean(d, 0), np.nanstd(d, 0) / np.sqrt(np.sum(~np.isnan(d), 0))
            win = (t >= 0) & (t <= 300)
            j = np.nanargmax(sign * m[win])
            peaks.append({"coh": c, "sign": sign, "n": len(sel), "peak_measured": m[win][j], "peak_expected": np.nanmean(exp, 0)[win][np.nanargmax(sign * np.nanmean(exp, 0)[win])],
                          "nominal_change": sign * 100 - c, "se": se[win][j]})
        ax.axvspan(0, 3.5 * FRAME * 1000, color="0.85", zorder=0)
        ax.axhline(0, color="0.6", lw=0.6)
        ax.set_title(f"coherence {c:+d}%", fontsize=10)
        ax.set_xlabel("time from pulse onset (ms)", fontsize=8)
        ax.set_ylabel("motion energy (% coh)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=7, frameon=False)
    p = pd.DataFrame(peaks)

    ax = fig.add_subplot(gs[3, :2])
    for sign, colour in [(1, "tab:blue"), (-1, "tab:red")]:
        q = p[p.sign == sign].sort_values("coh")
        ax.errorbar(q.coh, q.peak_measured, yerr=1.96 * q.se, color=colour, marker="o", label=f"{'+' if sign > 0 else '−'} pulse: measured peak (pulse − control)")
        ax.plot(q.coh, q.peak_expected, color=colour, ls="--", marker="x", label="model's expected component (template)")
        ax.plot(q.coh, q.nominal_change, color=colour, ls=":", alpha=0.6, label="nominal coherence change (to ±100%)")
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel("baseline coherence (%)", fontsize=9)
    ax.set_ylabel("peak pulse-evoked energy (% coh)", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    ax.tick_params(labelsize=8)

    ax = fig.add_subplot(gs[3, 2:])
    for r, ls in zip(np.unique(rig), ["-", "--"]):
        on = inp[f"onset_response_{r}"][:60] * 100
        ax.plot(np.arange(60) * FRAME * 1000, on, color="k", ls=ls, label=f"sustained 100% coherence ({r} onset response)")
    ax.set_xlabel("time from motion onset (ms)", fontsize=9)
    ax.set_ylabel("motion energy (% coh)", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    ax.tick_params(labelsize=8)
    fig.suptitle("Motion energy around scheduled pulses (responded trials; solid = pulse trials, dotted = same-coherence controls at the same frames; grey = mean pulse duration)", fontsize=11)

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / f"pulse_motion_energy_traces_{date.today().isoformat()}"
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=150, bbox_inches="tight")
    p.round(2).to_csv(f"{stem}_peaks.csv", index=False)
    print(p.round(2).to_string(index=False))
    print(f"saved {stem}.png/.pdf and _peaks.csv")


if __name__ == "__main__":
    main()
