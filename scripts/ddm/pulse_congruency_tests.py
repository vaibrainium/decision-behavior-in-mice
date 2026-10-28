"""Pulse effects as congruent vs incongruent, tested with mice as the unit (plan
.agents/plans/2026-10-28-pulse-congruency-tests.md).

Responded trials, symmetric cells, |coherence| 9-36%. Per mouse: effect in the pulse direction, congruent =
sign(c) * (P(R | congruent) - P(R | control)) and incongruent = -sign(c) * (P(R | incongruent) - P(R | control)),
averaged over coherences (congruency_effects in pulse_asymmetry_lapse), in pp. Primary: stages pooled, tests of
congruent, incongruent and congruent - incongruent against 0 (one-sample t and Wilcoxon, Holm over 3). Secondary: the
same per pulse stage (Holm over 9).

Outputs: dissemination/paper_accumulation/tables/pulse_congruency_{per_mouse,tests}_<date>.csv
Usage: python -m scripts.ddm.pulse_congruency_tests
"""

from datetime import date
from pathlib import Path

import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from scripts.ddm.pulse_asymmetry_lapse import congruency_effects
from scripts.ddm.pulse_psychometric_stage import STAGES, load_trials

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


def main():
    t = load_trials()
    pm = per_mouse(t)
    r = tests(pm)
    stem = f"{date.today().isoformat()}"
    pm.round(3).to_csv(OUT / f"pulse_congruency_per_mouse_{stem}.csv", index=False)
    r.round(4).to_csv(OUT / f"pulse_congruency_tests_{stem}.csv", index=False)
    print(pm[pm.stage == "pooled"].round(2).to_string(index=False))
    print(r.drop(columns=["p_t", "p_wilcoxon"]).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
