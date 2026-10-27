"""Pulse-onset-aligned motion energy for each signed coherence (stimulus view; responded trials only).

Same inputs and alignment as scripts/ddm/pulse_energy_traces.py, laid out for comparison across coherences:
top row = mean motion energy (S + N, % coherence) of +/- pulse trials with same-rig, same-coherence controls taken at
the same frames (dotted); bottom row = pulse-evoked energy (pulse - matched control). Shaded bands are +-1 SEM across
trials; y axes are shared within each row; grey = mean logged pulse duration. Rigs pooled after subtracting their own
control means (rig as covariate only).

Output: dissemination/figures/qc/pulse_motion_energy_by_coherence_<date>.{png,pdf}
Usage: python -m scripts.ddm.pulse_energy_by_coherence
"""

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_energy_traces import FRAME, OUT, POST, PRE, TRIAL_TABLE, aligned


def band(ax, t, x, colour, **kw):
    m = np.nanmean(x, 0)
    se = np.nanstd(x, 0) / np.sqrt(np.sum(~np.isnan(x), 0))
    ax.fill_between(t, m - se, m + se, color=colour, alpha=0.25, lw=0)
    ax.plot(t, m, color=colour, **kw)


def main():
    processed = Path(dir_config.data.processed)
    inp = responded_only(load_inputs(processed / "ddm/ddm_inputs_global.npz"))
    table = pd.read_csv(processed / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "onset_frame", "n_pulse_frames"]).set_index("trial_id")
    me = (inp["signal"].astype(float) + inp["noise"]) * 100
    coh, rig, sched = np.round(inp["signed_coherence"] * 100).astype(int), inp["data_source"], inp["sched_pulse_type"]
    pulse = sched != 0
    onset_idx = np.zeros(len(coh), int)
    n_frames = np.full(len(coh), np.nan)
    rows = table.loc[inp["agg_code"][pulse].astype(str)]
    onset_idx[pulse] = rows["onset_frame"].to_numpy().astype(int) - 1
    n_frames[pulse] = rows["n_pulse_frames"].to_numpy()

    ctrl = {(r, c): me[(~pulse) & (rig == r) & (coh == c)].mean(axis=0) for r in np.unique(rig) for c in np.unique(coh)
            if ((~pulse) & (rig == r) & (coh == c)).any()}

    levels = sorted(np.unique(coh))
    t = np.arange(-PRE, POST) * FRAME * 1000  # ms
    fig, axes = plt.subplots(2, len(levels), figsize=(2.1 * len(levels), 5.2), sharex=True, sharey="row")
    for k, c in enumerate(levels):
        top, bot = axes[0, k], axes[1, k]
        for sign, colour in [(1, "tab:blue"), (-1, "tab:red")]:
            sel = np.flatnonzero(pulse & (coh == c) & (np.sign(sched) == sign))
            if not len(sel):
                continue
            raw = aligned(me[sel], onset_idx[sel])
            base = np.stack([aligned(ctrl[(rig[i], c)][None], onset_idx[i:i + 1])[0] for i in sel])
            band(top, t, raw, colour, lw=1.4, label=f"{'+' if sign > 0 else '−'} (n={len(sel)})")
            top.plot(t, np.nanmean(base, 0), color=colour, lw=1, ls=":")
            band(bot, t, raw - base, colour, lw=1.4)
        dur = np.nanmean(n_frames[pulse & (coh == c)]) * FRAME * 1000
        for ax in (top, bot):
            ax.axvspan(0, dur, color="0.88", zorder=0)
            ax.axhline(0, color="0.6", lw=0.6)
            ax.tick_params(labelsize=7)
        top.set_title(f"{c:+d}%", fontsize=9)
        top.legend(fontsize=6, frameon=False, loc="upper left")
        bot.set_xlabel("ms from pulse onset", fontsize=7)
    axes[0, 0].set_ylabel("motion energy (% coh)", fontsize=8)
    axes[1, 0].set_ylabel("pulse − control (% coh)", fontsize=8)
    fig.suptitle("Motion energy aligned to pulse onset, by signed coherence (responded trials; dotted = matched controls; "
                 "bands = ±1 SEM; grey = mean pulse duration)", fontsize=9)
    fig.tight_layout()

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / f"pulse_motion_energy_by_coherence_{date.today().isoformat()}"
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=200, bbox_inches="tight")
    print(f"saved {stem}.png/.pdf")


if __name__ == "__main__":
    main()
