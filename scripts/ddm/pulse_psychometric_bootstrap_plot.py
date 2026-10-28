"""Plots of the psychometric-parameter bootstrap (pulse_psychometric_bootstrap): fitted bias and slope per curve and
stage, and the tested contrasts, each with 95% percentile CIs. Filled contrast markers: Holm p < 0.05 within the set.

Inputs:  dissemination/paper_accumulation/tables/pulse_psychometric_parameter_bootstrap{,_parameters}_<date>.csv
Outputs: dissemination/paper_accumulation/figures/qc/pulse_psychometric_parameter_bootstrap_<date>.{png,pdf}
Usage: python -m scripts.ddm.pulse_psychometric_bootstrap_plot --date 2026-10-28
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.ddm.pulse_psychometric_bootstrap import CONTRASTS
from scripts.ddm.pulse_psychometric_bootstrap import OUT as TABLES
from scripts.ddm.pulse_psychometric_stage import COLOURS, SETS, STAGES
from scripts.ddm.pulse_psychometric_stage import OUT as FIGURES

LABELS = {"mu": "Bias (% coherence)", "beta": "Slope (per % coherence)"}


def main(day: str):
    params = pd.read_csv(TABLES / f"pulse_psychometric_parameter_bootstrap_parameters_{day}.csv")
    r = pd.read_csv(TABLES / f"pulse_psychometric_parameter_bootstrap_{day}.csv")
    stages = list(STAGES.values())
    n_mice = params.groupby("stage").n_mice.first()
    ticks = [f"{s}\n({n_mice[s]} mice)" for s in stages]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.4))
    for i, (set_name, names) in enumerate(SETS.items()):
        for j, q in enumerate(["beta", "mu"]):
            ax = axes[i, j]
            for k, name in enumerate(names):
                d = params[(params.curve == name) & (params.parameter == q)].set_index("stage").loc[stages]
                x = np.arange(3) + (k - 1) * 0.2
                ax.errorbar(x, d.estimate, yerr=[d.estimate - d.ci_lo, d.ci_hi - d.estimate], fmt="o", ms=4, capsize=0,
                            color=COLOURS[name], label=name)
            ax.set_xticks(range(3), ticks, fontsize=8)
            ax.set_ylabel(LABELS[q], fontsize=9)
            ax.set_title(f"{set_name}: {'slope' if q == 'beta' else 'bias'}", fontsize=9)
            if j == 0:
                ax.legend(frameon=False, fontsize=8)
            ax = axes[i, 2 + j]
            for k, (a, ref) in enumerate(CONTRASTS[set_name]):
                d = r[(r.set == set_name) & (r.parameter == q) & (r.contrast == f"{a} - {ref}")].set_index("stage").loc[stages]
                x = np.arange(3) + (k - 1) * 0.2
                colour = COLOURS[a] if ref == "control" else "0.2"
                ax.errorbar(x, d.estimate, yerr=[d.estimate - d.ci_lo, d.ci_hi - d.estimate], fmt="none", capsize=0, color=colour,
                            label=f"{a} − {ref}".replace(" pulse", ""))
                sig = d.p_boot_holm.to_numpy() < 0.05
                ax.scatter(x, d.estimate, s=22, zorder=3, edgecolor=colour, facecolor=np.where(sig, colour, "white"))
            ax.axhline(0, color="0.6", lw=0.7, zorder=0)
            ax.set_xticks(range(3), ticks, fontsize=8)
            ax.set_ylabel(f"Δ {LABELS[q].lower()}", fontsize=9)
            ax.set_title(f"{set_name}: Δ {'slope' if q == 'beta' else 'bias'}", fontsize=9)
            if j == 0:
                lo, hi = ax.get_ylim()
                ax.set_ylim(lo, hi + 0.4 * (hi - lo))
                ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=1)
    fig.suptitle("Psychometric parameters by pulse time; 95% hierarchical-bootstrap CIs (10,000). "
                 "Filled contrast markers: Holm p < 0.05 (18 tests per set)", fontsize=9)
    fig.tight_layout()
    stem = FIGURES / f"pulse_psychometric_parameter_bootstrap_{day}"
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")
    print(f"saved {stem}.png/.pdf")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    main(ap.parse_args().date)
