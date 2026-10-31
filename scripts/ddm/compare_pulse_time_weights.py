"""Per-pulse-time pulse weights vs the shared-weight and joint fits (plan .agents/plans/2026-10-30-pulse-time-weights.md, step 4).

Same mice, folds (cv0-cv4 over all responded trials) and likelihood. Weights: noise_weight = early (UCLA 0.02-0.12 s,
UW 0.05 s), noise_weight_2 = middle (UCLA 0.20-0.30 s, UW 0.23 s), noise_weight_3 = late (UW 0.42 s). Held-out NLL summed
over folds per mouse; mice are the unit (Wilcoxon signed-rank, Holm over all tests in the summary).

    .venv/bin/python -m scripts.ddm.compare_pulse_time_weights
"""

import pandas as pd
from scipy.stats import wilcoxon

from scripts.ddm.compare_joint_refits import load
from scripts.ddm.compare_pulse_weight import FOLDS, MODELS, holm

FOLDERS = {"joint": "fits_joint_unfreeze_integrators", "shared_w": "fits_joint_unfreeze_pulse_weight", "time_w": "fits_joint_unfreeze_pulse_time_weights"}
WEIGHTS = {"noise_weight": "w_early", "noise_weight_2": "w_middle", "noise_weight_3": "w_late"}
OUT = "dissemination/figures/qc/pulse_time_weights_{}_2026-10-31.csv"


def main():
    rows, weights = [], []
    for label, variant in MODELS.items():
        for model, folder in FOLDERS.items():
            df = load(folder, variant)
            assert df.success.all() and (df[df.split.isin(FOLDS)].groupby("mouse").split.nunique() == 5).all(), (label, model)
            for m, g in df.groupby("mouse"):
                cv = g[g.split.isin(FOLDS)]
                rows.append({"sv": label, "model": model, "mouse": m, "heldout_nll": cv.test_nll.sum(), "train_nll_all": g[g.split == "all"].train_nll.item(),
                             "at_iteration_cap": int((g.n_iterations >= g.max_iterations).sum())})
            if model == "time_w":
                for _, r in df.iterrows():
                    weights.append({"sv": label, "mouse": r.mouse, "split": r.split, **{v: r.params.get(k) for k, v in WEIGHTS.items()},
                                    "drift_gain": r.params.get("drift_gain"), "sv_param": r.params.get("sv", 0.0), "a": r.params.get("a")})
    t = pd.DataFrame(rows)
    wide = t.pivot_table(index=["sv", "mouse"], columns="model", values=["heldout_nll", "train_nll_all"])
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    for ref in ("joint", "shared_w"):
        wide[f"d_heldout_vs_{ref}"] = wide.heldout_nll_time_w - wide[f"heldout_nll_{ref}"]
        wide[f"d_train_all_vs_{ref}"] = wide.train_nll_all_time_w - wide[f"train_nll_all_{ref}"]
    w = pd.DataFrame(weights)
    w_all = w[w.split == "all"].drop(columns="split")
    w_cv = w[w.split.isin(FOLDS)].groupby(["sv", "mouse"])[list(WEIGHTS.values())].median().add_suffix("_cv_median").reset_index()
    wide = wide.merge(w_all, on=["sv", "mouse"]).merge(w_cv, on=["sv", "mouse"])

    tests = []
    for label, g in wide.groupby("sv"):
        for ref in ("joint", "shared_w"):
            d = g[f"d_heldout_vs_{ref}"]
            tests.append({"sv": label, "test": f"heldout time_w - {ref}", "n_mice": len(d), "sum": d.sum(), "median": d.median(),
                          "n_better_by_10": int((d < -10).sum()), "n_worse_by_10": int((d > 10).sum()), "p": wilcoxon(d).pvalue})
        for a, b in (("w_early", "w_middle"), ("w_middle", "w_late"), ("w_early", "w_late")):
            h = g.dropna(subset=[a, b])
            d = h[a] - h[b]
            tests.append({"sv": label, "test": f"{a} - {b} (all-trial fits)", "n_mice": len(d), "sum": d.sum(), "median": d.median(),
                          "n_positive": int((d > 0).sum()), "p": wilcoxon(d).pvalue})
    tests = pd.DataFrame(tests)
    tests["p_holm"] = holm(list(tests.p))

    wide.to_csv(OUT.format("per_mouse"), index=False)
    pd.DataFrame(weights).to_csv(OUT.format("parameters"), index=False)
    tests.to_csv(OUT.format("summary"), index=False)
    pd.set_option("display.width", 250)
    print(wide[["sv", "mouse", "d_heldout_vs_joint", "d_heldout_vs_shared_w", "d_train_all_vs_joint", "w_early", "w_middle", "w_late",
                "w_early_cv_median", "w_middle_cv_median", "w_late_cv_median"]].round(2).to_string(index=False))
    print(t.groupby(["sv", "model"]).at_iteration_cap.sum())
    print(tests.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
