"""Directional vs non-directional pulse effects over time, pooled trials (author 2026-10-30; plan
.agents/plans/2026-10-29-huk-shadlen-replication.md, log).

logit P(right) = C(coherence) x C(bin) + C(mouse) + sum_b D_b * pulse * I_b + sum_b S_b * sign(C) * any_pulse * I_b
- pulse = +1 right / -1 left pulse, 0 none: D_b pushes choices toward the pulse (directional part).
- sign(C) * any_pulse: S_b pushes choices toward the correct side whatever the pulse direction (shared part;
  0% pulse trials have none). Congruent effect toward correct = D + S, incongruent = -D + S (logit).
- bin = RT - (virtual) pulse onset; coherence x bin absorbs the time-varying baseline from no-pulse trials.
All coherences, no late pulses (huk_shadlen_replication.load), responses < 100 ms after onset dropped.
Inference: mouse bootstrap (n_boot refits; percentile CIs, two-sided bootstrap p, Holm over bins) is primary. Cluster-
robust SEs and Wald tests (10 clusters for up to 7 restrictions) are reported but unreliable (optimistic).

    python -m scripts.behavior.pulse_decomposition [--date YYYY-MM-DD] [--n_boot N]
"""

import argparse
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from scripts.behavior.huk_shadlen_replication import CONG_BLOCK_S, load

OUT = Path(__file__).resolve().parents[2] / "dissemination/paper_accumulation"
EDGES_S = [CONG_BLOCK_S, 0.3, 0.6, 0.9, 1.2, 1.5, 2.1, 5.0]

warnings.filterwarnings("ignore")


def design(t: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    u = t[t.rel_rt_s >= EDGES_S[0]].copy()
    u["bin"] = pd.cut(u.rel_rt_s, EDGES_S, right=False, labels=False).astype(int)
    shared = np.sign(u.coherence_pct) * (u.pulse != 0)
    d_terms, s_terms = [], []
    for b in range(len(EDGES_S) - 1):
        u[f"D{b}"], u[f"S{b}"] = u.pulse * (u.bin == b), shared * (u.bin == b)
        d_terms.append(f"D{b}"), s_terms.append(f"S{b}")
    return u, d_terms, s_terms


def fit(u, d_terms, s_terms, cluster: bool):
    f = "right ~ C(coherence_pct):C(bin) + C(mouse) + " + " + ".join(d_terms + s_terms)
    m = smf.logit(f, u)
    if cluster:
        return m.fit(disp=0, maxiter=200, cov_type="cluster", cov_kwds={"groups": pd.factorize(u.mouse)[0]})
    return m.fit(disp=0, maxiter=200)


def main(date: str, n_boot: int):
    u, d_terms, s_terms = design(load())
    r = fit(u, d_terms, s_terms, cluster=True)
    rng = np.random.default_rng(0)
    mice = u.mouse.unique()
    groups = {m: g for m, g in u.groupby("mouse")}
    boot = []
    for k in range(n_boot):
        pick = rng.choice(mice, len(mice))
        b = pd.concat([groups[m].assign(mouse=f"{m}_{i}") for i, m in enumerate(pick)], ignore_index=True)
        try:
            boot.append(fit(b, d_terms, s_terms, cluster=False).params[d_terms + s_terms])
        except Exception:
            continue
    boot = pd.DataFrame(boot)
    rows = []
    for b in range(len(EDGES_S) - 1):
        n = u[u.bin == b]
        row = {"lo_s": EDGES_S[b], "hi_s": EDGES_S[b + 1], "n_trials": len(n), "n_pulse": int((n.pulse != 0).sum())}
        for kind, term in [("D", f"D{b}"), ("S", f"S{b}")]:
            row |= {f"{kind}": r.params[term], f"{kind}_se_cluster": r.bse[term], f"{kind}_p_cluster": r.pvalues[term],
                    f"{kind}_boot_lo": boot[term].quantile(0.025), f"{kind}_boot_hi": boot[term].quantile(0.975),
                    f"{kind}_p_boot": min(1.0, 2 * min((boot[term] <= 0).mean(), (boot[term] >= 0).mean()) + 1 / (len(boot) + 1))}
        row["cong_toward_correct"], row["incong_toward_correct"] = row["D"] + row["S"], -row["D"] + row["S"]
        rows.append(row)
    res = pd.DataFrame(rows)
    for kind in "DS":
        res[f"{kind}_holm_cluster"] = multipletests(res[f"{kind}_p_cluster"], method="holm")[1]
        res[f"{kind}_holm_boot"] = multipletests(res[f"{kind}_p_boot"], method="holm")[1]
    w_s = r.wald_test(", ".join(f"{t} = 0" for t in s_terms), scalar=True)
    w_d = r.wald_test(", ".join(f"{d_terms[0]} = {t}" for t in d_terms[1:]), scalar=True)
    tests = pd.DataFrame([{"test": "all shared S_b = 0", "chi2": float(w_s.statistic), "df": len(s_terms), "p": float(w_s.pvalue)},
                          {"test": "directional D_b equal across bins", "chi2": float(w_d.statistic), "df": len(d_terms) - 1, "p": float(w_d.pvalue)}])
    tests["n_boot_ok"] = len(boot)
    stem = OUT / f"tables/pulse_decomposition_{date}"
    res.to_csv(f"{stem}_bins.csv", index=False), tests.to_csv(f"{stem}_tests.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    x = 1000 * (res.lo_s + res.hi_s.clip(upper=2.4)) / 2
    for kind, col, lab in [("D", "tab:purple", "directional D (toward the pulse)"), ("S", "tab:green", "shared S (toward correct side, any pulse)")]:
        ax[0].errorbar(x, res[kind], [(res[kind] - res[f"{kind}_boot_lo"]).clip(lower=0), (res[f"{kind}_boot_hi"] - res[kind]).clip(lower=0)], fmt="o-", color=col, lw=2.2, capsize=3, label=lab)
        for xi, (_, rr) in zip(x, res.iterrows()):
            if rr[f"{kind}_holm_boot"] < 0.05:
                ax[0].text(xi, rr[f"{kind}_boot_hi"] + 0.05, "*", color=col, ha="center", fontsize=14)
    ax[0].set_title(f"pooled logit decomposition (95% mouse-bootstrap CI, {len(boot)} refits; * Holm p < .05, bootstrap)\n"
                    f"cluster Wald (10 clusters, unreliable): all S = 0 p {tests.p[0]:.3g}; D constant p {tests.p[1]:.3g}", fontsize=9)
    ax[1].plot(x, res.cong_toward_correct, "o-", color="tab:blue", lw=2.2, label="congruent = D + S")
    ax[1].plot(x, res.incong_toward_correct, "o-", color="tab:red", lw=2.2, label="incongruent = -D + S")
    ax[1].set_title("implied effects toward the correct side", fontsize=10)
    for a in ax:
        a.axhline(0, color="k", lw=0.6), a.set_xlim(0, 2500), a.axvspan(0, 100, color="#ddd")
        a.set_xlabel("RT - pulse onset (ms; last bin 2.1-5 s drawn at 2.25 s)"), a.set_ylabel("logit"), a.legend(fontsize=8)
    fig.suptitle("Directional vs non-directional pulse effects, pooled trials (mouse intercepts, coherence x time-bin baseline); all coherences, no late pulses")
    fig.tight_layout(), fig.savefig(OUT / f"figures/qc/pulse_decomposition_{date}.png", dpi=140), plt.close(fig)
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(res.round(3).to_string(index=False), tests.round(4).to_string(index=False), sep="\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    ap.add_argument("--n_boot", type=int, default=300)
    a = ap.parse_args()
    main(a.date, a.n_boot)
