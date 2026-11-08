"""Pooled congruency figure without the per-mouse panel (author 2026-10-30: drop panel 4 from the presentation; the
per-mouse view is the congruency overlay). Same data as huk_shadlen_replication's pooled congruency figure, panels 1-3:
P(correct) and mean RT vs |coherence| (no pulse / congruent / incongruent; curves from the pooled fit with bias) and the
75 ms time course toward the correct side. Reads the joint-fit and congruency_pooled tables; trials from load().

    python -m scripts.behavior.figure_pooled_congruency_3panel [--date 2026-10-29]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.behavior.huk_shadlen_replication import CONG_BLOCK_S, FINE_BIN_S, FINE_MAX_S, OUT, congruency_cells, congruency_curves, load


def main(date: str):
    t = load()
    jf = pd.read_csv(OUT / f"tables/huk_shadlen_replication_{date}_joint_fits.csv")
    cp = pd.read_csv(OUT / f"tables/huk_shadlen_replication_{date}_congruency_pooled.csv")
    p = jf[(jf.mouse == "pooled") & (jf.model == "bias")].iloc[0]
    params = [p.k, p.A, p.t_nd_ms, p.gamma, p.bias]
    c = congruency_cells(t)
    style = [("none", "k", "no pulse"), ("cong", "tab:blue", "congruent"), ("incong", "tab:red", "incongruent")]
    fig, ax = plt.subplots(1, 3, figsize=(17, 5))
    for cat, col, lab in style:
        d = c[c.cat == cat]
        ax[0].errorbar(d.abs_coh, d.p_correct, np.sqrt(d.p_correct * (1 - d.p_correct) / d.n), fmt="o", color=col, label=lab)
        ax[1].errorbar(d.abs_coh, d.rt_mean, d.rt_se, fmt="o", color=col)
        x, pc, rt = congruency_curves(params, cat)
        ax[0].plot(x, pc, color=col), ax[1].plot(x, rt, color=col)
    ax[0].set_xlabel("|coherence| (%)"), ax[0].set_ylabel("P(correct)"), ax[0].legend(fontsize=9)
    ax[0].set_title(f"accuracy; curves: pooled fit, pulse = {100 * p.gamma:.1f}% coherence", fontsize=10)
    ax[1].set_xlabel("|coherence| (%)"), ax[1].set_ylabel("mean RT (ms)"), ax[1].set_title("mean RT (correct + error)", fontsize=10)
    for k, (lab, col, name) in enumerate(style[1:]):
        ax[2].errorbar(1000 * (cp.lo_s + FINE_BIN_S / 2) + (k - 0.5) * 8, cp[f"{lab}_pct"], cp[f"{lab}_pct_se"], fmt="o-", color=col, label=name, ms=4)
    ax[2].axhline(0, color="k", lw=0.5), ax[2].axvspan(0, CONG_BLOCK_S * 1000, color="#ddd"), ax[2].set_xlim(0, FINE_MAX_S * 1000), ax[2].set_ylim(-60, 60)
    ax[2].set_xlabel("RT - pulse onset (ms)"), ax[2].set_ylabel("effect toward correct side (% coherence)"), ax[2].legend(fontsize=9)
    ax[2].set_title("time course, 75 ms bins (Huk & Shadlen Fig 4)", fontsize=10)
    fig.suptitle("Congruent vs incongruent, pooled trials (mouse intercepts); all coherences, no late pulses; 0% excluded; first 100 ms blocked", fontsize=11)
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/huk_shadlen_replication_{date}_pooled_congruency_3panel.png", dpi=150), plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-29")
    main(ap.parse_args().date)
