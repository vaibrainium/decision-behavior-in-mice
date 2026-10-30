"""Pulse-weight fits vs the joint fits they extend (plan .agents/plans/2026-10-29-pulse-weight-joint.md, step 3).

Same mice, same folds (cv0-cv4 over all responded trials), same likelihood; the pulse-weight model adds one free weight on
the pulse component (w = 1 is the joint model). Held-out NLL summed over folds per mouse; mice are the unit.

    .venv/bin/python -m scripts.ddm.compare_pulse_weight
"""

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from scripts.ddm.compare_joint_refits import load

FOLDS = [f"cv{k}" for k in range(5)]
MODELS = {"sv": "L0U0V1Z0G1", "no_sv": "L0U0V0Z0G1"}
OUT = "dissemination/figures/qc/pulse_weight_{}_2026-10-30.csv"


def holm(p: list[float]) -> list[float]:
    order = np.argsort(p)
    adj, running = np.empty(len(p)), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - rank) * p[i]))
        adj[i] = running
    return list(adj)


def main():
    rows, params = [], []
    for label, variant in MODELS.items():
        pw, joint = load("fits_joint_unfreeze_pulse_weight", variant), load("fits_joint_unfreeze_integrators", variant)
        for df, model in ((pw, "pulse_weight"), (joint, "joint")):
            assert set(df.split) >= set(FOLDS + ["all"]) and df.success.all(), (label, model)
            cv = df[df.split.isin(FOLDS)]
            assert (cv.groupby("mouse").split.nunique() == 5).all()
            for m, g in cv.groupby("mouse"):
                rows.append({"sv": label, "model": model, "mouse": m, "heldout_nll": g.test_nll.sum(), "n_test": g.n_test.sum(),
                             "train_nll_all": df[(df.mouse == m) & (df.split == "all")].train_nll.item()})
        for _, r in pw.iterrows():
            params.append({"sv": label, "mouse": r.mouse, "split": r.split, **{("sv_param" if k == "sv" else k): r.params.get(k, 0.0) for k in ("noise_weight", "drift_gain", "sv", "a", "drift_offset", "p_guess")},
                           "n_iterations": r.n_iterations})
    table = pd.DataFrame(rows).pivot_table(index=["sv", "mouse"], columns="model", values=["heldout_nll", "train_nll_all"]).reset_index()
    table.columns = ["sv", "mouse", "heldout_joint", "heldout_pw", "train_all_joint", "train_all_pw"]
    table["d_heldout"] = table.heldout_pw - table.heldout_joint
    table["d_train_all"] = table.train_all_pw - table.train_all_joint
    pars = pd.DataFrame(params)
    w = pars[pars.split.isin(FOLDS)].groupby(["sv", "mouse"]).noise_weight.agg(["median", "min", "max"]).add_prefix("w_cv_")
    table = table.merge(w.reset_index(), on=["sv", "mouse"]).merge(pars[pars.split == "all"][["sv", "mouse", "noise_weight"]].rename(columns={"noise_weight": "w_all"}), on=["sv", "mouse"])

    summary = []
    for label, g in table.groupby("sv"):
        stat = wilcoxon(g.d_heldout)
        summary.append({"sv": label, "n_mice": len(g), "sum_d_heldout": g.d_heldout.sum(), "median_d_heldout": g.d_heldout.median(),
                        "mice_pw_better_by_10": int((g.d_heldout < -10).sum()), "mice_pw_worse_by_10": int((g.d_heldout > 10).sum()),
                        "wilcoxon_W": stat.statistic, "p": stat.pvalue, "median_w_all": g.w_all.median()})
    # sv vs no-sv within the pulse-weight model (the D005 question with the weight free)
    pw_sv = table.set_index(["sv", "mouse"]).heldout_pw.unstack(0)
    d = pw_sv["no_sv"] - pw_sv["sv"]
    stat = wilcoxon(d)
    summary.append({"sv": "no_sv minus sv (pulse_weight)", "n_mice": len(d), "sum_d_heldout": d.sum(), "median_d_heldout": d.median(),
                    "mice_pw_better_by_10": int((d < -10).sum()), "mice_pw_worse_by_10": int((d > 10).sum()), "wilcoxon_W": stat.statistic, "p": stat.pvalue})
    summary = pd.DataFrame(summary)
    summary["p_holm"] = holm(list(summary.p))

    table.to_csv(OUT.format("heldout"), index=False)
    pars.to_csv(OUT.format("parameters"), index=False)
    summary.to_csv(OUT.format("summary"), index=False)
    pd.set_option("display.width", 220)
    print(table.round(2).to_string(index=False))
    print(summary.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
