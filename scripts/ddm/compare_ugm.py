"""UGM region of leak + urgency vs the standard integrators (plans/2026-11-10-ugm-corner-leak-urgency.md, step 6).
EXPLORATORY. Criterion 1 of the plan (confirmed by the author 2026-11-11 before this was run): the UGM is viable for a
mouse if its held-out NLL is within 10 units of the best standard integrator for that mouse, same input, same CV splits.

Held-out NLL = sum of test NLL over 5 folds:
  joint fits: cv0-cv4 (all trials of the mouse); standard integrators fits_joint_{unfreeze,power,norm}_integrators
    (every G1 variant in the folder: linear L0U0V1, L0U0V0, L1U0V1, L0U1V1, L1U1V1; power and norm the four with sv);
  pulse-only fits: pcv0-pcv4 (pulse trials); standard fits_pulse_{linear,power}_integrators (8 variants);
    normalization input has no standard pulse-only fit: UGM pulse-only norm is described, not compared.
Checks that each comparison scores the same trials (n_test per mouse equal).
Criterion 2 (pulse profile) is in pulse_effect_bootstrap_<date>_ugm_models.csv.

Usage: python -m scripts.ddm.compare_ugm
Outputs: dissemination/figures/qc/ugm_nll_{per_mouse,summary}_<date>.csv, ugm_params_<date>.csv
"""

import glob
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.compare_joint_refits import DDM, load
from scripts.ddm.pulse_psychometric import OUT

THRESHOLD = 10.0
JOINT_FOLDS, PULSE_FOLDS = [f"cv{k}" for k in range(5)], [f"pcv{k}" for k in range(5)]
UGM = {"L1U1V1Z0G1": "ugm", "L1U1V0Z0G1": "ugm_no_sv"}
SETS = [  # (kind, input, UGM folder, standard folder or None, folds)
    ("joint", "linear", "fits_joint_linear_ugm", "fits_joint_unfreeze_integrators", JOINT_FOLDS),
    ("joint", "power", "fits_joint_power_ugm", "fits_joint_power_integrators", JOINT_FOLDS),
    ("joint", "norm", "fits_joint_norm_ugm", "fits_joint_norm_integrators", JOINT_FOLDS),
    ("pulse", "linear", "fits_pulse_linear_ugm", "fits_pulse_linear_integrators", PULSE_FOLDS),
    ("pulse", "power", "fits_pulse_power_ugm", "fits_pulse_power_integrators", PULSE_FOLDS),
    ("pulse", "norm", "fits_pulse_norm_ugm", None, PULSE_FOLDS),
]
FULL_SPLIT = {"joint": "all", "pulse": "pulse"}


def variants(folder: str) -> list[str]:
    names = {Path(p).stem.split("_")[1] for p in glob.glob(str(DDM / folder / "*.pkl"))}
    return sorted(v for v in names if v.endswith("G1"))


def heldout(folder: str, variant: str, folds: list[str]) -> pd.DataFrame:
    d = load(folder, variant)
    d = d[d.split.isin(folds)]
    g = d.groupby("mouse")
    out = pd.DataFrame({"nll": g.test_nll.sum(), "n": g.n_test.sum(), "folds": g.split.nunique()})
    assert (out.folds == len(folds)).all(), (folder, variant)
    return out[["nll", "n"]]


def main():
    per, params = [], []
    for kind, fe, ufolder, sfolder, folds in SETS:
        std = {v: heldout(sfolder, v, folds) for v in variants(sfolder)} if sfolder else {}
        if std:
            nll_std = pd.DataFrame({v: s.nll for v, s in std.items()})
            n_std = pd.DataFrame({v: s.n for v, s in std.items()})
            assert (n_std.nunique(axis=1) == 1).all(), sfolder
        for v, name in UGM.items():
            u = heldout(ufolder, v, folds)
            full = load(ufolder, v)
            full = full[full.split == FULL_SPLIT[kind]].set_index("mouse")
            for m in u.index:
                row = {"kind": kind, "input": fe, "model": name, "mouse": m, "ugm_heldout": u.loc[m, "nll"], "n_heldout": int(u.loc[m, "n"])}
                if std:
                    assert n_std.loc[m].iloc[0] == u.loc[m, "n"], (kind, fe, m)
                    best_v = nll_std.loc[m].idxmin()
                    row |= {"best_std_variant": best_v, "best_std_heldout": nll_std.loc[m, best_v],
                            "d_vs_best": u.loc[m, "nll"] - nll_std.loc[m, best_v]}
                    same = "L1U1" + v[4:]  # standard leak + urgency with the same sv
                    if same in nll_std:
                        row["d_vs_std_leak_urgency"] = u.loc[m, "nll"] - nll_std.loc[m, same]
                    row["viable_nll"] = bool(row["d_vs_best"] <= THRESHOLD)
                per.append(row)
                p = full.loc[m, "params"]
                params.append({"kind": kind, "input": fe, "model": name, "mouse": m, "leak_rate": p["leak_rate"],
                               "tau_ms": 1000 / p["leak_rate"], "urgency": p["time_constant"], "drift_gain": p["drift_gain"],
                               "a": p["a"], "sv": p["sv"], "ndt": p["ndt"]})
    per, params = pd.DataFrame(per), pd.DataFrame(params)
    g = per.groupby(["kind", "input", "model"], sort=False)
    summ = g.agg(ugm_heldout=("ugm_heldout", "sum"), best_std_heldout=("best_std_heldout", "sum"), d_vs_best_sum=("d_vs_best", "sum"),
                 d_vs_best_median=("d_vs_best", "median"), d_vs_best_min=("d_vs_best", "min"), d_vs_best_max=("d_vs_best", "max"),
                 mice_viable_nll=("viable_nll", "sum"), d_vs_std_leak_urgency_sum=("d_vs_std_leak_urgency", "sum"),
                 mice_better10_than_std_lu=("d_vs_std_leak_urgency", lambda s: int((s < -THRESHOLD).sum())),
                 mice_worse10_than_std_lu=("d_vs_std_leak_urgency", lambda s: int((s > THRESHOLD).sum())),
                 n_mice=("mouse", "size")).reset_index()
    summ.loc[summ.best_std_heldout.isna() | (summ.best_std_heldout == 0), [c for c in summ if c.startswith(("best", "d_", "mice"))]] = np.nan
    stem, day = OUT / "ugm", date.today().isoformat()
    per.round(2).to_csv(f"{stem}_nll_per_mouse_{day}.csv", index=False)
    summ.round(2).to_csv(f"{stem}_nll_summary_{day}.csv", index=False)
    params.round(4).to_csv(f"{stem}_params_{day}.csv", index=False)
    pd.set_option("display.width", 250)
    print(summ.round(1).to_string(index=False))
    print(per.pivot_table(index="mouse", columns=["kind", "input", "model"], values="d_vs_best").round(0).to_string())


if __name__ == "__main__":
    main()
