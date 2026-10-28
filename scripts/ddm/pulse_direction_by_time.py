"""Right vs left pulse at each pulse time: fitted psychometric bias and slope (plan
.agents/plans/2026-10-28-pulse-direction-by-time.md).

Reads the hierarchical-bootstrap tables of pulse_psychometric_bootstrap (same resamples) and keeps the right - left
contrast per stage for bias mu and slope beta; Holm over these 6 tests. Figure: right and left pulse parameters per
stage (top) and right - left (bottom), 95% percentile CIs; filled markers Holm p < 0.05.

Outputs: dissemination/paper_accumulation/tables/pulse_direction_by_time_<date>.csv
         dissemination/paper_accumulation/figures/qc/pulse_direction_by_time_<date>.{png,pdf}
Usage: python -m scripts.ddm.pulse_direction_by_time --date 2026-10-28
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

from scripts.ddm.pulse_psychometric_bootstrap import OUT as TABLES
from scripts.ddm.pulse_psychometric_bootstrap_plot import LABELS
from scripts.ddm.pulse_psychometric_stage import COLOURS, STAGES
from scripts.ddm.pulse_psychometric_stage import OUT as FIGURES

CURVES = ["right pulse", "left pulse"]


def main(day: str):
    params = pd.read_csv(TABLES / f"pulse_psychometric_parameter_bootstrap_parameters_{day}.csv")
    r = pd.read_csv(TABLES / f"pulse_psychometric_parameter_bootstrap_{day}.csv")
    r = r[(r.set == "direction") & (r.contrast == "right pulse - left pulse")].drop(columns=["set", "p_boot_holm"]).copy()
    r["p_boot_holm"] = multipletests(r.p_boot, method="holm")[1]
    r.round(4).to_csv(TABLES / f"pulse_direction_by_time_{day}.csv", index=False)
    print(r.round(4).to_string(index=False))

    stages = list(STAGES.values())
    n_mice = params.groupby("stage").n_mice.first()
    ticks = [f"{s}\n({n_mice[s]} mice)" for s in stages]
    fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.4))
    for j, q in enumerate(["mu", "beta"]):
        ax = axes[0, j]
        for k, name in enumerate(CURVES):
            d = params[(params.curve == name) & (params.parameter == q)].set_index("stage").loc[stages]
            x = np.arange(3) + (k - 0.5) * 0.2
            ax.errorbar(x, d.estimate, yerr=[d.estimate - d.ci_lo, d.ci_hi - d.estimate], fmt="o", ms=4, capsize=0,
                        color=COLOURS[name], label=name)
        ax.set_xticks(range(3), ticks, fontsize=8)
        ax.set_ylabel(LABELS[q], fontsize=9)
        ax.set_title("bias" if q == "mu" else "slope", fontsize=9)
        ax.legend(frameon=False, fontsize=8)
        ax = axes[1, j]
        d = r[r.parameter == q].set_index("stage").loc[stages]
        sig = d.p_boot_holm.to_numpy() < 0.05
        ax.errorbar(range(3), d.estimate, yerr=[d.estimate - d.ci_lo, d.ci_hi - d.estimate], fmt="none", capsize=0, color="0.2")
        ax.scatter(range(3), d.estimate, s=26, zorder=3, edgecolor="0.2", facecolor=np.where(sig, "0.2", "white"))
        ax.axhline(0, color="0.6", lw=0.7, zorder=0)
        ax.set_xticks(range(3), ticks, fontsize=8)
        ax.set_ylabel(f"Right − left, {LABELS[q].lower()}", fontsize=9)
        ax.set_title(f"right − left: {'bias' if q == 'mu' else 'slope'}", fontsize=9)
    fig.suptitle("Right vs left pulse by pulse time; 95% hierarchical-bootstrap CIs (10,000).\n"
                 "Filled: Holm p < 0.05 over the 6 right − left tests", fontsize=9)
    fig.tight_layout()
    stem = FIGURES / f"pulse_direction_by_time_{day}"
    fig.savefig(f"{stem}.png", dpi=200)
    fig.savefig(f"{stem}.pdf")
    print(f"saved {stem}.png/.pdf")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    main(ap.parse_args().date)
