"""Does the behavioural pulse effect scale with the coherence change the pulse adds? (exploratory; plan
.agents/plans/2026-10-27-pulse-effect-vs-coherence-change.md)

Responders only (R/L counts of package C cells; no-response trials dropped). Per mouse and arm (baseline signed coherence
c, pulse sign s): effect = s * [logit P(R | pulse) - logit P(R | control)] over pooled supported cells (Haldane +0.5), with
coherence change |D| = 100 - s * c. Per mouse, weighted regression of effect on |D|; proportionality index
PI = slope * mean|D| / mean effect (1 = proportional, evidence-like; 0 = constant, event-like). Mouse is the unit.

Output: <run>/behaviour_delta/{arms.csv, per_mouse.csv, group.json, effect_vs_delta.png}
Usage: python -m scripts.pulse_followup.effect_vs_delta
"""

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from scripts.pulse_followup import io

RUN = io.OUTPUT_ROOT / "20261023T191030Z_fa8de8b"
ARMS = {"positive_vs_control": ("positive", 1), "control_vs_negative": ("negative", -1)}


def logit(r, l):
    return np.log((r + 0.5) / (l + 0.5)), 1 / (r + 0.5) + 1 / (l + 0.5)


def arm_table(cells):
    rows = []
    for contrast, (arm, s) in ARMS.items():
        x = cells[(cells.analysis_set == "primary_coherence") & (cells.contrast == contrast)]
        x = x[(x[f"{arm}__R"] + x[f"{arm}__L"] > 0) & (x.control__R + x.control__L > 0)]  # responder-supported
        g = x.groupby(["mouse", "coherence_pct"])[[f"{arm}__R", f"{arm}__L", "control__R", "control__L"]].sum().reset_index()
        lp, vp = logit(g[f"{arm}__R"], g[f"{arm}__L"])
        lc, vc = logit(g.control__R, g.control__L)
        rows.append(pd.DataFrame({
            "mouse": g.mouse, "coh": g.coherence_pct, "sign": s, "delta": 100 - s * g.coherence_pct,
            "n_pulse": g[f"{arm}__R"] + g[f"{arm}__L"], "n_control": g.control__R + g.control__L,
            "effect": s * (lp - lc), "var": vp + vc,
            "pp": s * (g[f"{arm}__R"] / (g[f"{arm}__R"] + g[f"{arm}__L"]) - g.control__R / (g.control__R + g.control__L)) * 100,
        }))
    return pd.concat(rows, ignore_index=True)


def responder_pp(cells, contrast="positive_vs_control"):
    """Package C responder estimand (cell weight min(responders), normalized within mouse; mean over mice)."""
    arm, s = ARMS[contrast]
    x = cells[(cells.analysis_set == "primary_coherence") & (cells.contrast == contrast)].copy()
    rp, rc = x[f"{arm}__R"] + x[f"{arm}__L"], x.control__R + x.control__L
    x = x[(rp > 0) & (rc > 0)].assign(w=np.minimum(rp, rc)[(rp > 0) & (rc > 0)])
    x["d"] = s * (x[f"{arm}__R"] / (x[f"{arm}__R"] + x[f"{arm}__L"]) - x.control__R / (x.control__R + x.control__L))
    return 100 * x.groupby("mouse").apply(lambda m: np.average(m.d, weights=m.w)).mean()


def main():
    out = RUN / "behaviour_delta"
    out.mkdir(exist_ok=True)
    cells = pd.read_csv(RUN / "behaviour" / "cells.csv")
    arms = arm_table(cells)

    per_mouse = []
    for mouse, m in arms.groupby("mouse"):
        w = 1 / m["var"]
        X = np.column_stack([np.ones(len(m)), m.delta])
        beta, *_ = np.linalg.lstsq(X * np.sqrt(w.to_numpy())[:, None], m.effect * np.sqrt(w), rcond=None)
        mean_d, mean_e = np.average(m.delta, weights=w), np.average(m.effect, weights=w)
        per_mouse.append({"mouse": mouse, "n_arms": len(m), "n_pulse": int(m.n_pulse.sum()), "intercept": beta[0],
                          "slope_per_100pct": beta[1] * 100, "mean_effect": mean_e, "mean_delta": mean_d,
                          "PI": beta[1] * mean_d / mean_e})
    pm = pd.DataFrame(per_mouse)

    def t1(x, mu):
        r = stats.ttest_1samp(x, mu)
        ci = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
        return {"mean": x.mean(), "ci95": list(ci), "t": r.statistic, "p": r.pvalue, "df": len(x) - 1}

    group = {
        "slope_per_100pct_vs_0": t1(pm.slope_per_100pct, 0),
        "mean_effect_logit_vs_0": t1(pm.mean_effect, 0),
        # added after the first run: PI divides by mean effects near 0 in some mice; test the slope against each
        # mouse's proportional prediction (mean effect / mean |D|) directly
        "slope_minus_proportional_vs_0": t1(pm.slope_per_100pct - 100 * pm.mean_effect / pm.mean_delta, 0),
        "PI_vs_1": t1(pm.PI, 1), "PI_vs_0": t1(pm.PI, 0), "PI_median": pm.PI.median(),
        "n_mice": len(pm), "n_mice_positive_slope": int((pm.slope_per_100pct > 0).sum()),
        "check_positive_vs_control_responder_pp": responder_pp(cells),
    }
    arms.round(4).to_csv(out / "arms.csv", index=False)
    pm.round(4).to_csv(out / "per_mouse.csv", index=False)
    json.dump(group, open(out / "group.json", "w"), indent=2, default=float)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    for mouse, m in arms.groupby("mouse"):
        m = m.sort_values("delta")
        ax.plot(m.delta, m.effect, color="0.75", lw=0.8, marker=".", ms=3)
    bins = arms.groupby("delta").apply(lambda m: pd.Series({"e": m.groupby("mouse").effect.mean().mean(),
                                                            "se": stats.sem(m.groupby("mouse").effect.mean())}))
    ax.errorbar(bins.index, bins.e, yerr=bins.se, color="k", marker="o", lw=1.5, label="mean over mice ± SEM")
    d = np.array([60, 140])
    ax.plot(d, d * pm.mean_effect.mean() / pm.mean_delta.mean(), "--", color="tab:blue", label="proportional (evidence)")
    ax.axhline(pm.mean_effect.mean(), ls=":", color="tab:red", label="constant (event)")
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel("coherence change |Δ| (%)")
    ax.set_ylabel("pulse effect, Δ logit P(pulse direction)")
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    ax.scatter(pm.PI, np.arange(len(pm)), color="k", s=12)
    ax.set_yticks(np.arange(len(pm)), pm.mouse, fontsize=7)
    for v, c in [(0, "tab:red"), (1, "tab:blue")]:
        ax.axvline(v, color=c, ls=":")
    ax.set_xlabel("proportionality index (0 event, 1 evidence)")
    fig.suptitle("Behavioural pulse effect vs coherence change (responders, |c| ≤ 36%, pulse vs control)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "effect_vs_delta.png", dpi=150)

    print(pm.round(3).to_string(index=False))
    print(json.dumps(group, indent=1, default=float))
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
