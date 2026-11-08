"""Congruency-only version of the per-mouse overlay (author 2026-10-30: drop right vs left from the presentation).
Reads the tables written by huk_shadlen_replication (overlay_per_mouse, overlay_summary); effects toward the correct
side in % coherence, per mouse (thin) and mean +- SEM over mice (bold).

    python -m scripts.behavior.figure_overlay_congruency [--date 2026-10-29]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation"


def main(date: str):
    per = pd.read_csv(OUT / f"tables/huk_shadlen_replication_{date}_overlay_per_mouse.csv")
    summ = pd.read_csv(OUT / f"tables/huk_shadlen_replication_{date}_overlay_summary.csv")
    per, summ = per[per.set == "congruency"], summ[summ.set == "congruency"]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for k, (lab, col, name) in enumerate([("cong", "tab:blue", "congruent"), ("incong", "tab:red", "incongruent")]):
        for _, g in per[per.curve == lab].groupby("mouse"):
            ax.plot(1000 * (g.lo_s + g.hi_s) / 2, g.pct.clip(-100, 100), color=col, alpha=0.25, lw=1)
        sm = summ[summ.curve == lab]
        x = 1000 * (sm.lo_s + sm.hi_s) / 2 + (k - 0.5) * 20
        ax.errorbar(x, sm.mean_pct, sm.sem_pct, fmt="o-", color=col, lw=2.5, ms=6, capsize=3, label=f"{name} (mean +- SEM over mice)")
        for xi, (_, r) in zip(x, sm.iterrows()):
            ax.text(xi, -95, f"{int(r.n_mice)}", color=col, ha="center", fontsize=8)
    ax.axhline(0, color="k", lw=0.5), ax.axvspan(0, 100, color="#ddd"), ax.set_xlim(0, 2100), ax.set_ylim(-100, 100)
    ax.set_xlabel("RT - pulse onset (ms)"), ax.set_ylabel("effect toward the correct side (% coherence)")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title("Per mouse (thin, clipped at +-100) and mean over mice; numbers at bottom: mice per point\n"
                 "bins with >= 20 trials per pulse type; all coherences, no late pulses; first 100 ms blocked", fontsize=9)
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_mouse_overlay_congruency.png", dpi=150), plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-29")
    main(ap.parse_args().date)
