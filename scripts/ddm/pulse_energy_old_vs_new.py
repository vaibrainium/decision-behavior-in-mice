"""QC: pulse-aligned pulse-evoked ME (pulse - same-rig same-coherence control), old (master, notebook 2.11) vs new filter.
Old shards: processed/motion_data_dict (old filter, cut at RT). Both converted to % coherence by each rig's control slope.
Usage: python -m scripts.ddm.pulse_energy_old_vs_new
"""
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_energy_traces import FRAME, POST, PRE, TRIAL_TABLE, aligned

P = Path(dir_config.data.processed)
inp = responded_only(load_inputs(P / "ddm/ddm_inputs_global.npz"))
table = pd.read_csv(P / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "onset_frame"]).set_index("trial_id")
old = {}
for s in (0, 1):
    old.update({k: np.asarray(v["global"], float) for k, v in pickle.load(open(P / f"motion_data_dict/me_shard_{s}.pkl", "rb")).items()})
codes = inp["agg_code"].astype(str)
keep = np.array([c in old for c in codes])
print(f"{keep.sum()} of {len(codes)} responded trials have old ME")
codes = codes[keep]
coh = np.round(inp["signed_coherence"][keep] * 100).astype(int)
rig, sched = inp["data_source"][keep], inp["sched_pulse_type"][keep]
new = ((inp["signal"].astype(float) + inp["noise"]) * 100)[keep]
o = np.full((len(codes), 300), np.nan)
for i, c in enumerate(codes):
    x = old[c][:300]
    o[i, :len(x)] = x
pulse = sched != 0
onset = np.zeros(len(codes), int)
onset[pulse] = table.loc[codes[pulse], "onset_frame"].to_numpy().astype(int) - 1

# old ME -> % coherence: per-rig slope on control trials, frames 9+ (as for the new calibration)
for r in np.unique(rig):
    m = (~pulse) & (rig == r) & (coh != 0)
    lvl = pd.Series(np.nanmean(o[m, 9:], 1)).groupby(coh[m]).mean()
    x = lvl.index.to_numpy(float)
    slope = (x * lvl.to_numpy()).sum() / (x ** 2).sum()
    o[rig == r] /= slope
    print(r, "old slope per % coh", round(slope, 1))

t = np.arange(-PRE, POST) * FRAME * 1000
levels = sorted(np.unique(coh))
fig, axes = plt.subplots(2, len(levels), figsize=(2.1 * len(levels), 5), sharex=True, sharey=True)
for row, (me, name) in enumerate([(o, "old filter (master / nb 2.11)"), (new, "new mouse filter (DDM inputs)")]):
    ctrl = {(r, c): np.nanmean(me[(~pulse) & (rig == r) & (coh == c)], 0) for r in np.unique(rig) for c in levels
            if ((~pulse) & (rig == r) & (coh == c)).any()}
    for k, c in enumerate(levels):
        ax = axes[row, k]
        for sign, col in [(1, "tab:blue"), (-1, "tab:red")]:
            sel = np.flatnonzero(pulse & (coh == c) & (np.sign(sched) == sign))
            if not len(sel):
                continue
            d = aligned(me[sel], onset[sel]) - np.stack([aligned(ctrl[(rig[i], c)][None], onset[i:i + 1])[0] for i in sel])
            ax.plot(t, np.nanmean(d, 0), color=col, lw=1.4)
        ax.axvspan(0, 3.5 * FRAME * 1000, color="0.88", zorder=0)
        ax.axhline(0, color="0.6", lw=0.6)
        ax.tick_params(labelsize=7)
        if row == 0:
            ax.set_title(f"{c:+d}%", fontsize=9)
        else:
            ax.set_xlabel("ms from pulse onset", fontsize=7)
    axes[row, 0].set_ylabel(f"{name}\npulse − control (% coh)", fontsize=7)
fig.suptitle("Pulse-evoked motion energy, same trials and stimulus replay, old vs new filter (responded trials)", fontsize=9)
fig.tight_layout()
out = Path(__file__).resolve().parents[2] / "dissemination/figures/qc/pulse_motion_energy_old_vs_new_2026-10-27.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(out)
