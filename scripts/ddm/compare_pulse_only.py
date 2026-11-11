"""Pulse-only fits vs all-trial fits (plans/2026-11-10-pulse-only-fits.md, step 4). EXPLORATORY, descriptive.

1. Parameters: each pulse-only fit (split "pulse") against the joint "all" fit of the same mouse, mapping and variant
   (only variants with a joint fit: linear primary / no sv / leak / urgency / leak+urgency; power with sv).
2. NLL: per family, summed over mice: held-out (pcv0-pcv4, pulse trials), fitted (split "pulse"), control trials
   predicted by the "pulse" fit; differences to pulse_linear_primary and mice beyond 10; sv vs no-sv pairs.
Pulse-effect predictions vs data are in pulse_effect_bootstrap_2026-11-11_pulseonly_models.csv (separate script).

Usage: python -m scripts.ddm.compare_pulse_only
Outputs: dissemination/figures/qc/pulse_only_{params,nll,sv_pairs}_<date>.csv
"""

from datetime import date

import numpy as np
import pandas as pd

from scripts.ddm.compare_joint_refits import load
from scripts.ddm.pulse_joint_signatures import PULSE_ONLY_FAMILIES, PULSE_ONLY_VARIANTS
from scripts.ddm.pulse_psychometric import OUT

JOINT = {"linear": "fits_joint_unfreeze_integrators", "power": "fits_joint_power_integrators"}
PCV = [f"pcv{k}" for k in range(5)]
REF = "pulse_linear_primary"


def params() -> pd.DataFrame:
    rows = []
    for fam, (folder, variant) in PULSE_ONLY_FAMILIES.items():
        fe = fam.split("_")[1]
        j = load(JOINT[fe], variant)
        if j.empty:
            continue
        p = load(folder, variant)
        p, j = p[p.split == "pulse"].set_index("mouse"), j[j.split == "all"].set_index("mouse")
        for m in p.index.intersection(j.index):
            for k in p.loc[m, "free_parameters"]:
                rows.append({"family": fam, "mapping": fe, "variant": variant, "mouse": m, "param": k,
                             "pulse_only": p.loc[m, "params"][k], "all_trials": j.loc[m, "params"].get(k, np.nan)})
    d = pd.DataFrame(rows)
    d["ratio"] = d.pulse_only / d.all_trials
    return d.groupby(["family", "param"], sort=False).agg(
        all_trials_median=("all_trials", "median"), pulse_only_median=("pulse_only", "median"),
        ratio_median=("ratio", "median"), mice_higher=("ratio", lambda r: int((r > 1).sum())), n_mice=("ratio", "size")).reset_index()


def nll() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for fam, (folder, variant) in PULSE_ONLY_FAMILIES.items():
        d = load(folder, variant)
        cv = d[d.split.isin(PCV)].groupby("mouse")
        assert (cv.split.nunique() == len(PCV)).all(), fam
        pf = d[d.split == "pulse"].set_index("mouse")
        for m, g in cv:
            rows.append({"family": fam, "mouse": m, "heldout": g.test_nll.sum(), "n_heldout": g.n_test.sum(),
                         "fitted": pf.loc[m, "train_nll"], "control_pred": pf.loc[m, "test_nll"], "n_control": pf.loc[m, "n_test"],
                         "k": len(pf.loc[m, "free_parameters"])})
    per = pd.DataFrame(rows)
    w = {c: per.pivot(index="mouse", columns="family", values=c) for c in ("heldout", "control_pred")}
    t = per.groupby("family").agg(heldout=("heldout", "sum"), n_heldout=("n_heldout", "sum"), fitted=("fitted", "sum"),
                                  control_pred=("control_pred", "sum"), n_control=("n_control", "sum"), k=("k", "first"))
    for c in ("heldout", "control_pred"):
        dm = w[c].sub(w[c][REF], axis=0)
        t[f"d_{c}"] = t[c] - t.loc[REF, c]
        t[f"{c}_mice_better10"], t[f"{c}_mice_worse10"] = (dm < -10).sum(), (dm > 10).sum()
    pairs = []
    for fe in ("linear", "power"):
        for name, _ in PULSE_ONLY_VARIANTS[::2]:
            s, ns = f"pulse_{fe}_{name}", f"pulse_{fe}_{'no_sv' if name == 'primary' else name + '_no_sv'}"
            dd = {c: w[c][ns] - w[c][s] for c in w}
            pairs.append({"mapping": fe, "model": name, "heldout_no_sv_minus_sv": dd["heldout"].sum(),
                          "mice_no_sv_better10": int((dd["heldout"] < -10).sum()), "mice_no_sv_worse10": int((dd["heldout"] > 10).sum()),
                          "control_pred_no_sv_minus_sv": dd["control_pred"].sum()})
    return t.sort_values("heldout").reset_index(), pd.DataFrame(pairs)


def main():
    stem = OUT / "pulse_only"
    p = params()
    t, pairs = nll()
    p.round(4).to_csv(f"{stem}_params_{date.today().isoformat()}.csv", index=False)
    t.round(2).to_csv(f"{stem}_nll_{date.today().isoformat()}.csv", index=False)
    pairs.round(2).to_csv(f"{stem}_sv_pairs_{date.today().isoformat()}.csv", index=False)
    pd.set_option("display.width", 250)
    print(t.round(1).to_string(index=False), "\n", pairs.round(1).to_string(index=False))
    print(p[p.param.isin(["ndt", "p_guess", "drift_offset"])].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
