"""Is the pulse kept or lost? Dilution benchmark on pooled trials (author 2026-10-30; plan
.agents/plans/2026-10-29-huk-shadlen-replication.md, log).

Per bin of RT - (virtual) pulse onset: D = pulse coefficient in logit P(right) ~ C(coherence) + C(mouse) + pulse
(toward the pulse; congruent and incongruent share it), b1 = coherence slope per % from a linear fit to |C| <= 36%
(mouse intercepts), gamma = D / b1 in % coherence, T = mean RT from motion onset. If the pulse adds fixed evidence that
is kept, its coherence equivalent is diluted by later dot evidence as 1/T, so gamma * T is constant (K, % coherence x s).
A drop of gamma * T below K means the pulse's contribution is lost faster than dilution. K = mean gamma * T over the
bins 0.3-1.2 s, where the effect is clear. Benchmark ignores bound selection and disengagement on slow trials.
All coherences, no late pulses (huk_shadlen_replication.load). Mouse bootstrap (n_boot refits) for CIs.

    python -m scripts.behavior.pulse_dilution [--date YYYY-MM-DD] [--n_boot N]
"""

import argparse
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from scripts.behavior.huk_shadlen_replication import load
from scripts.behavior.pulse_decomposition import EDGES_S, design

OUT = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation"
PLATEAU_S = (0.3, 1.2)

warnings.filterwarnings("ignore")


def per_bin(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for b in range(len(EDGES_S) - 1):
        x = d[d.bin == b]
        b1 = smf.logit("right ~ coh + C(mouse)", x[x.coherence_pct.abs() <= 36]).fit(disp=0).params["coh"] / 100
        D = smf.logit("right ~ C(coherence_pct) + C(mouse) + pulse", x).fit(disp=0).params["pulse"]
        rows.append({"lo_s": EDGES_S[b], "hi_s": EDGES_S[b + 1], "D": D, "b1_per_pct": b1, "gamma_pct": D / b1, "T_s": x.rt_s.mean(), "gammaT": D / b1 * x.rt_s.mean()})
    r = pd.DataFrame(rows)
    plateau = (r.lo_s >= PLATEAU_S[0]) & (r.hi_s <= PLATEAU_S[1])
    r["K"] = r.loc[plateau, "gammaT"].mean()
    r["gammaT_minus_K"] = r.gammaT - r.K
    return r


def main(date: str, n_boot: int):
    u, _, _ = design(load())
    obs = per_bin(u)
    obs["n_trials"] = u.groupby("bin").size().to_numpy()
    obs["n_pulse"] = u[u.pulse != 0].groupby("bin").size().to_numpy()
    rng = np.random.default_rng(0)
    groups = {m: g for m, g in u.groupby("mouse")}
    mice = list(groups)
    boot = []
    for _ in range(n_boot):
        pick = rng.choice(mice, len(mice))
        try:
            boot.append(per_bin(pd.concat([groups[m].assign(mouse=f"{m}_{i}") for i, m in enumerate(pick)], ignore_index=True)))
        except Exception:  # separation in a resample
            continue
    for col in ["D", "gamma_pct", "gammaT", "gammaT_minus_K", "K"]:
        vals = np.array([b[col].to_numpy() for b in boot])
        obs[f"{col}_lo"], obs[f"{col}_hi"] = np.percentile(vals, 2.5, axis=0), np.percentile(vals, 97.5, axis=0)
        if col == "gammaT_minus_K":
            obs["p_below_K"] = (vals >= 0).mean(axis=0)  # one-sided bootstrap: gamma*T not below the plateau
    obs["n_boot_ok"] = len(boot)
    obs.to_csv(OUT / f"tables/pulse_dilution_{date}.csv", index=False)

    x = obs.T_s
    K = obs.K.iloc[0]
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))
    a = ax[0]
    a.errorbar(x, obs.gamma_pct, [(obs.gamma_pct - obs.gamma_pct_lo).clip(lower=0), (obs.gamma_pct_hi - obs.gamma_pct).clip(lower=0)], fmt="ko", capsize=3,
               label="data (95% mouse-bootstrap CI)")
    tt = np.linspace(0.45, 3.6, 200)
    a.plot(tt, K / tt, color="tab:green", lw=2, label=f"kept, diluted: gamma = K / T (K = {K:.1f} % coh x s)")
    for xi, (_, r) in zip(x, obs.iterrows()):
        a.annotate(f"{1000 * r.lo_s:.0f}-{1000 * r.hi_s:.0f} ms", (xi, r.gamma_pct), textcoords="offset points", xytext=(6, 6), fontsize=7, color="#555")
    a.axhline(0, color="k", lw=0.5), a.set_xlabel("mean RT from motion onset, T (s)"), a.set_ylabel("pulse effect, gamma (% coherence)")
    a.set_title("pulse value in coherence units vs time of the choice", fontsize=10), a.legend(fontsize=8)
    a = ax[1]
    a.axhspan(obs.K_lo.iloc[0], obs.K_hi.iloc[0], color="tab:green", alpha=0.15, label="plateau K (95% CI), fitted 0.3-1.2 s after pulse")
    a.axhline(K, color="tab:green", lw=2)
    mid = 1000 * (obs.lo_s + obs.hi_s.clip(upper=2.4)) / 2
    a.errorbar(mid, obs.gammaT, [(obs.gammaT - obs.gammaT_lo).clip(lower=0), (obs.gammaT_hi - obs.gammaT).clip(lower=0)], fmt="ko-", capsize=3, lw=2,
               label="gamma x T (95% CI)")
    for xi, (_, r) in zip(mid, obs.iterrows()):
        if r.lo_s >= PLATEAU_S[1] and r.p_below_K < 0.05:
            a.text(xi, r.gammaT_hi + 1, "*", ha="center", fontsize=14)
    a.axhline(0, color="k", lw=0.5), a.axvspan(0, 100, color="#ddd"), a.set_xlim(0, 2500)
    a.set_xlabel("RT - pulse onset (ms; last bin 2.1-5 s drawn at 2.25 s)"), a.set_ylabel("gamma x T (% coherence x s)")
    a.set_title("flat = pulse kept (only diluted); below = lost; * below plateau, one-sided bootstrap p < .05", fontsize=9), a.legend(fontsize=8)
    fig.suptitle(f"Is the pulse kept or lost? Pooled trials, all coherences, no late pulses; {len(boot)} mouse-bootstrap refits")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/pulse_dilution_{date}.png", dpi=140), plt.close(fig)
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(obs.round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    ap.add_argument("--n_boot", type=int, default=300)
    a = ap.parse_args()
    main(a.date, a.n_boot)
