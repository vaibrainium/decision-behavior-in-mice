"""Pulse effects as congruent vs incongruent, tested with mice as the unit (plan
.agents/plans/2026-10-28-pulse-congruency-tests.md).

Responded trials, symmetric cells, |coherence| 9-36%. Per mouse: effect in the pulse direction, congruent =
sign(c) * (P(R | congruent) - P(R | control)) and incongruent = -sign(c) * (P(R | incongruent) - P(R | control)),
averaged over coherences (congruency_effects in pulse_asymmetry_lapse), in pp. Primary: stages pooled, tests of
congruent, incongruent and congruent - incongruent against 0 (one-sample t and Wilcoxon, Holm over 3). Secondary: the
same per pulse stage (Holm over 9). Bootstrap (author, per pulse stage): hierarchical, resampling mice with replacement
and then trials within each mouse x category x coherence cell (binomial redraws), N_BOOT resamples; 95% percentile CI
and two-sided p = 2 * min(P(boot <= 0), P(boot >= 0)); Holm over the 9 stage x effect tests.

Outputs: dissemination/paper_accumulation/tables/pulse_congruency_{per_mouse,tests,bootstrap}_<date>.csv
Usage: python -m scripts.ddm.pulse_congruency_tests
"""

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from scripts.ddm.pulse_asymmetry_lapse import congruency_effects
from scripts.ddm.pulse_psychometric_stage import STAGES, load_trials

N_BOOT, SEED = 10_000, 0
CATS = ["control", "congruent", "incongruent"]
OUT = Path(__file__).resolve().parents[2] / "dissemination" / "paper_accumulation" / "tables"


def per_mouse(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stage, sel in [("pooled", t.stage > 0)] + [(name, t.stage == s) for s, name in STAGES.items()]:
        e = congruency_effects(t[(t.category == "control") | sel], "right", "pp")
        rows.append(e.assign(stage=stage, congruent_minus_incongruent=e.congruent - e.incongruent).drop(columns="A").reset_index())
    return pd.concat(rows, ignore_index=True)


def tests(pm: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stage, g in pm.groupby("stage", sort=False):
        for effect in ("congruent", "incongruent", "congruent_minus_incongruent"):
            x = g[effect].dropna()
            lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=x.sem())
            rows.append({"stage": stage, "effect": effect, "mean_pp": x.mean(), "ci_lo": lo, "ci_hi": hi, "median_pp": x.median(),
                         "mice_positive": int((x > 0).sum()), "n_mice": len(x), "t": stats.ttest_1samp(x, 0).statistic,
                         "p_t": stats.ttest_1samp(x, 0).pvalue, "p_wilcoxon": stats.wilcoxon(x).pvalue, "dz": x.mean() / x.std(ddof=1)})
    r = pd.DataFrame(rows)
    for family in (r.stage == "pooled", r.stage != "pooled"):
        r.loc[family, "p_t_holm"] = multipletests(r.loc[family, "p_t"], method="holm")[1]
        r.loc[family, "p_wilcoxon_holm"] = multipletests(r.loc[family, "p_wilcoxon"], method="holm")[1]
    return r


def effects_from_p(p: np.ndarray, sign: np.ndarray) -> np.ndarray:
    """p: (..., mice, coh, 3 categories) P(right); returns (..., mice, 3): congruent, incongruent, difference, in pp."""
    cong = 100 * sign * (p[..., 1] - p[..., 0])
    inc = -100 * sign * (p[..., 2] - p[..., 0])
    cong, inc = np.nanmean(cong, axis=-1), np.nanmean(inc, axis=-1)
    return np.stack([cong, inc, cong - inc], axis=-1)


def bootstrap(t: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for s, stage in STAGES.items():
        x = t[t.coh.abs().between(9, 36) & ((t.category == "control") | (t.stage == s)) & t.category.isin(CATS)]
        x = x[x.mouse.isin(t.loc[t.stage == s, "mouse"].unique())]
        g = x.groupby(["mouse", "coh", "category"]).right.agg(["sum", "size"])
        idx = pd.MultiIndex.from_product([sorted(x.mouse.unique()), sorted(x.coh.unique()), CATS])
        g = g.reindex(idx, fill_value=0)
        shape = (len(idx.levels[0]), len(idx.levels[1]), 3)
        n, k = g["size"].to_numpy().reshape(shape), g["sum"].to_numpy().reshape(shape)
        sign = np.sign(np.array(sorted(x.coh.unique())))
        with np.errstate(invalid="ignore"):
            observed = np.nanmean(effects_from_p(k / np.where(n > 0, n, np.nan), sign), axis=0)
            mice = rng.integers(0, shape[0], size=(N_BOOT, shape[0]))
            nb = n[mice]
            kb = rng.binomial(nb, np.where(nb > 0, k[mice] / np.maximum(nb, 1), 0))
            boot = np.nanmean(effects_from_p(kb / np.where(nb > 0, nb, np.nan), sign), axis=1)
        for j, effect in enumerate(["congruent", "incongruent", "congruent_minus_incongruent"]):
            b = boot[:, j]
            rows.append({"stage": stage, "effect": effect, "n_mice": shape[0], "mean_pp": observed[j], "ci_lo": np.percentile(b, 2.5),
                         "ci_hi": np.percentile(b, 97.5), "p_boot": min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))})
    r = pd.DataFrame(rows)
    r["p_boot_holm"] = multipletests(r.p_boot, method="holm")[1]
    return r


def main():
    t = load_trials()
    pm = per_mouse(t)
    r = tests(pm)
    stem = f"{date.today().isoformat()}"
    pm.round(3).to_csv(OUT / f"pulse_congruency_per_mouse_{stem}.csv", index=False)
    r.round(4).to_csv(OUT / f"pulse_congruency_tests_{stem}.csv", index=False)
    b = bootstrap(t)
    b.round(4).to_csv(OUT / f"pulse_congruency_bootstrap_{stem}.csv", index=False)
    print(b.round(3).to_string(index=False))
    print(pm[pm.stage == "pooled"].round(2).to_string(index=False))
    print(r.drop(columns=["p_t", "p_wilcoxon"]).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
