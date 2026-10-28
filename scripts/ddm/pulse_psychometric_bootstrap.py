"""Hierarchical bootstrap on the fitted psychometric parameters, per pulse stage (plan
.agents/plans/2026-10-28-pulse-psychometric-parameter-bootstrap.md).

Same trials, curves, panel mice and fits as pulse_psychometric_stage: logistic with lapses on group-mean points
weighted by the number of mice; control fits all four parameters, pulse curves fit bias mu and slope beta with the
control's lapses. Per stage: resample the panel's mice with replacement, redraw trials within each mouse x curve x
coherence cell (binomial), rebuild the group means, refit control and then the pulse curves; N_BOOT resamples. Contrasts
of mu and beta: congruent / incongruent / right pulse / left pulse - control, congruent - incongruent, right - left.
95% percentile CI; two-sided p = 2 * min(P(boot <= 0), P(boot >= 0)); Holm over the 18 tests (3 stages x 3 contrasts x
2 parameters) within each curve set.

Outputs: dissemination/paper_accumulation/tables/pulse_psychometric_parameter_bootstrap_<date>.csv (contrasts) and
         _parameters_<date>.csv (per-curve parameters with CIs)
Usage: python -m scripts.ddm.pulse_psychometric_bootstrap
"""

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from statsmodels.stats.multitest import multipletests

from scripts.ddm.pulse_psychometric_stage import MIN_TRIALS, STAGES, fit_curve, load_trials, stage_curves

N_BOOT, SEED = 10_000, 0
CURVES = ["control", "congruent", "incongruent", "right pulse", "left pulse"]
CONTRASTS = {"congruency": [("congruent", "control"), ("incongruent", "control"), ("congruent", "incongruent")],
             "direction": [("right pulse", "control"), ("left pulse", "control"), ("right pulse", "left pulse")]}
PARAMS = ["mu", "beta"]
OUT = Path(__file__).resolve().parents[2] / "dissemination" / "paper_accumulation" / "tables"


def counts(t: pd.DataFrame, stage: int) -> tuple[np.ndarray, dict, dict]:
    """Coherence grid and, per curve, trial counts n and right choices k as (mice, coherences) arrays."""
    curves = stage_curves(t, stage)
    mice = sorted(t.loc[t.stage == stage, "mouse"].unique())
    coh = np.array(sorted(pd.concat([d.coh for d in curves.values()]).unique()))
    n, k = {}, {}
    for name in CURVES:
        g = curves[name].groupby(["mouse", "coh"]).right.agg(["sum", "size"])
        g = g.reindex(pd.MultiIndex.from_product([mice, coh]), fill_value=0)
        n[name], k[name] = (g[col].to_numpy().reshape(len(mice), len(coh)) for col in ("size", "sum"))
    return coh, n, k


def fit_all(coh: np.ndarray, n: dict, k: dict) -> dict:
    """Group-mean points per curve (cells with >= MIN_TRIALS), control fit, pulse fits with the control's lapses."""
    out = {}
    for name in CURVES:
        valid = n[name] >= MIN_TRIALS
        p = np.where(valid, k[name] / np.maximum(n[name], 1), np.nan)
        n_mice = valid.sum(axis=0)
        keep = n_mice > 0
        with np.errstate(invalid="ignore"):
            d = pd.DataFrame({"coh": coh[keep], "p_right": np.nanmean(p[:, keep], axis=0), "n_mice": n_mice[keep]})
        lapses = None if name == "control" else (out["control"]["gamma"], out["control"]["lambda"])
        out[name] = fit_curve(d, lapses)
    return out


def one_resample(coh, n, k, mice, seed) -> dict:
    rng = np.random.default_rng(seed)
    nb = {c: n[c][mice] for c in CURVES}
    kb = {c: rng.binomial(nb[c], k[c][mice] / np.maximum(nb[c], 1)) for c in CURVES}
    f = fit_all(coh, nb, kb)
    return {(c, q): f[c][q] for c in CURVES for q in ("mu", "beta", "gamma", "lambda")}


def boot_p(b: np.ndarray) -> float:
    return min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))


def main():
    t = load_trials()
    seeds = np.random.SeedSequence(SEED)
    contrasts, params = [], []
    for s, stage in STAGES.items():
        coh, n, k = counts(t, s)
        n_mice = n["control"].shape[0]
        observed = fit_all(coh, n, k)
        rng = np.random.default_rng(seeds.spawn(1)[0])
        mice = rng.integers(0, n_mice, size=(N_BOOT, n_mice))
        child = rng.integers(0, 2**63, size=N_BOOT)
        boot = pd.DataFrame(Parallel(n_jobs=-1, batch_size=64)(delayed(one_resample)(coh, n, k, mice[i], child[i]) for i in range(N_BOOT)))
        for c in CURVES:
            for q in ("mu", "beta", "gamma", "lambda"):
                b = boot[(c, q)]
                params.append({"stage": stage, "curve": c, "parameter": q, "n_mice": n_mice, "estimate": observed[c][q],
                               "ci_lo": b.quantile(0.025), "ci_hi": b.quantile(0.975)})
        at_bound = {"mu": lambda x: np.isclose(np.abs(x), 50), "beta": lambda x: np.isclose(x, 0) | np.isclose(x, 1)}
        for set_name, pairs in CONTRASTS.items():
            for a, ref in pairs:
                for q in PARAMS:
                    b = (boot[(a, q)] - boot[(ref, q)]).to_numpy()
                    hit = at_bound[q](boot[(a, q)]) | at_bound[q](boot[(ref, q)])
                    contrasts.append({"set": set_name, "stage": stage, "contrast": f"{a} - {ref}", "parameter": q, "n_mice": n_mice,
                                      "estimate": observed[a][q] - observed[ref][q], "ci_lo": np.percentile(b, 2.5),
                                      "ci_hi": np.percentile(b, 97.5), "p_boot": boot_p(b), "frac_at_bound": hit.mean()})
        print(f"{stage}: done")
    r = pd.DataFrame(contrasts)
    for set_name in CONTRASTS:
        sel = r.set == set_name
        r.loc[sel, "p_boot_holm"] = multipletests(r.loc[sel, "p_boot"], method="holm")[1]
    stem = date.today().isoformat()
    r.round(4).to_csv(OUT / f"pulse_psychometric_parameter_bootstrap_{stem}.csv", index=False)
    pd.DataFrame(params).round(4).to_csv(OUT / f"pulse_psychometric_parameter_bootstrap_parameters_{stem}.csv", index=False)
    print(r.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
