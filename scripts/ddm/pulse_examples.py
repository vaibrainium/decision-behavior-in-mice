"""Example pulse trials next to control trials, every trial type, one figure per rig (stimulus display only).

Rows: pulse time (early / middle / late). Columns: coherence (0 and the positive levels; negative levels mirror them).
Each panel: motion energy fed to the DDM (signal + noise, % coherence units) from stimulus onset, for one example
trial and the mean of each of: rightward pulse (+), leftward pulse (-), control (no pulse), same rig and coherence.
Shading: the pulse window (median onset to median offset of the panel's pulse trials).
Responded trials only (D003). No behavioural outcome is used. Rigs are shown separately because their pulse schedules
differ (stimulus design), not to compare results between sites.

Output: dissemination/figures/qc/pulse_examples_{ucla,uw}_<date>.{png,pdf}
Usage:  python -m scripts.ddm.pulse_examples
"""

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_energy_traces import FRAME, OUT, TRIAL_TABLE

T_MAX, SEED = 1.5, 0
STAGES = {1: "early", 2: "middle", 3: "late"}
COLOURS = {1: "#c0392b", -1: "#2471a3", 0: "0.45"}
LABELS = {1: "rightward pulse", -1: "leftward pulse", 0: "control"}


def main():
    processed = Path(dir_config.data.processed)
    inp = responded_only(load_inputs(processed / "ddm/ddm_inputs_global.npz"))
    tt = pd.read_csv(processed / TRIAL_TABLE, low_memory=False, usecols=["trial_id", "onset_frame", "offset_frame"]).set_index("trial_id")
    tt = tt.reindex(inp["agg_code"].astype(str))
    me = (inp["signal"].astype(float) + inp["noise"]) * 100
    coh = np.round(inp["signed_coherence"] * 100).astype(int)
    rig, sched = inp["data_source"], inp["sched_pulse_type"].astype(int)
    stage, sign = np.abs(sched), np.sign(sched)
    n = int(T_MAX / FRAME)
    t = np.arange(n) * FRAME
    rng = np.random.default_rng(SEED)
    for r in ("ucla", "uw"):
        stages = sorted(s for s in np.unique(stage[rig == r]) if s > 0)
        levels = sorted(c for c in np.unique(coh[rig == r]) if c >= 0)
        fig, axes = plt.subplots(len(stages), len(levels), figsize=(3.3 * len(levels), 2.9 * len(stages)), sharex=True, squeeze=False)
        for i, st in enumerate(stages):
            for j, c in enumerate(levels):
                ax = axes[i, j]
                pulse_rows = np.where((rig == r) & (coh == c) & (stage == st))[0]
                if len(pulse_rows):
                    on = np.nanmedian(tt.onset_frame.to_numpy()[pulse_rows]) - 1
                    off = np.nanmedian(tt.offset_frame.to_numpy()[pulse_rows]) - 1
                    ax.axvspan(on * FRAME, off * FRAME, color="gold", alpha=0.35, lw=0)
                for s in (1, -1, 0):
                    rows = np.where((rig == r) & (coh == c) & ((stage == st) & (sign == s) if s else (stage == 0)))[0]
                    if not len(rows):
                        continue
                    ex = rng.choice(rows)
                    ax.plot(t, me[ex, :n], color=COLOURS[s], lw=0.6, alpha=0.6)
                    ax.plot(t, me[rows, :n].mean(axis=0), color=COLOURS[s], lw=2, label=f"{LABELS[s]} (n={len(rows)})")
                ax.axhline(c, color="k", ls=":", lw=0.6)
                ax.set_title(f"{STAGES[st]} pulse, coherence {c}%", fontsize=9)
                ax.tick_params(labelsize=7)
                ax.legend(fontsize=6, frameon=False, loc="lower right")
                if j == 0:
                    ax.set_ylabel("motion energy (% coh)", fontsize=8)
                if i == len(stages) - 1:
                    ax.set_xlabel("time from stimulus onset (s)", fontsize=8)
        fig.suptitle(f"{r.upper()}: example pulse and control trials (thin = one example trial, thick = mean; "
                     "shaded = pulse window; dotted = nominal coherence)", fontsize=10)
        fig.tight_layout()
        stem = OUT / f"pulse_examples_{r}_{date.today().isoformat()}"
        fig.savefig(f"{stem}.png", dpi=150)
        fig.savefig(f"{stem}.pdf")
        print(stem)


if __name__ == "__main__":
    main()
