"""Joint control + pulse refits (plan 2026-10-29-joint-control-pulse-refits, steps 3-5): audit, held-out ranking next to
the control-only ranking, and parameter shifts.

Joint fits: ddm/fits_joint_unfreeze_* (inputs ddm_inputs_global_ucla_nofreeze.npz; all responded trials; folds cv0-cv4
over control and pulse trials, stratified by coherence x pulse condition, identical across families).
Control-only fits: the responded-only folders of the earlier selection (ccv0-ccv4 folds within control trials; split
"control" = all control trials). Their held-out sets differ from the joint ones, so only rankings are set side by side.

  1. audit: completeness, optimizer success, iterations at the cap, free parameters within 1% of a bound;
  2. per mouse summed held-out NLL over cv0-cv4 per family, minus the primary model (negative = family better); mice
     beyond THRESHOLD either way (as the control-only selection), random-effects BMS over families (mice as units);
     the same for the control-only ccv folds where they exist;
  3. parameters of the joint "all" fit vs the control-only "control" fit, ratio per mouse (rig is listed as a covariate).

Outputs: dissemination/figures/qc/joint_refits_*_<date>.csv and printed tables.
Usage:  python -m scripts.ddm.compare_joint_refits
"""

import glob
import pickle
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.compare_models import rfx_bms
from scripts.ddm.fit_mouse_ddm import make_params
from scripts.ddm.pulse_psychometric import OUT

DDM = Path(dir_config.data.processed) / "ddm"
FOLDS, CFOLDS = [f"cv{k}" for k in range(5)], [f"ccv{k}" for k in range(5)]
THRESHOLD, AT_BOUND, PRIMARY = 10.0, 0.01, "primary"
# family: (joint folder, variant, control-only folder with ccv folds, control-only folder with the "control" split)
FAMILIES = {
    "primary": ("fits_joint_unfreeze_integrators", "L0U0V1Z0G1", "fits_resp_fast_only", "fits_resp_final"),
    "no_sv": ("fits_joint_unfreeze_integrators", "L0U0V0Z0G1", "fits_resp_fast_only", None),
    "no_guess": ("fits_joint_unfreeze_integrators", "L0U0V1Z0G0", "fits_resp_fast_only", None),
    "leak": ("fits_joint_unfreeze_integrators", "L1U0V1Z0G1", "fits_resp_fast_only_cap", None),
    "urgency": ("fits_joint_unfreeze_integrators", "L0U1V1Z0G1", "fits_resp_fast_only", None),
    "leak_urgency": ("fits_joint_unfreeze_integrators", "L1U1V1Z0G1", "fits_resp_fast_only", "fits_resp_final"),
    "fixed_guess_bias": ("fits_joint_unfreeze_FB", "L0U0V1Z0G1", "fits_resp_fast_only_FB", None),
    "extrema_E_leak20-200": ("fits_joint_unfreeze_leak20-200", "L1U0V1Z0G1", "fits_resp_fast_only_leak20-200_cap", "fits_resp_fast_only_leak20-200_cap"),
    "free_leak_0-200": ("fits_joint_unfreeze_leak0-200", "L1U0V1Z0G1", None, "fits_resp_fast_only_leak0-200_cap"),
    "extrema_sampling_ES": ("fits_joint_unfreeze_es", "L0U0V1Z0G1", "fits_resp_fast_only_es_cap", "fits_resp_fast_only_es_cap"),
    "stine_nominal_DDM": ("fits_joint_unfreeze_nominal_ddm", "L0U0V0Z0G0", "fits_resp_nominal_ddm_g001", "fits_resp_nominal_ddm_g001"),
    "stine_nominal_ES": ("fits_joint_unfreeze_nominal_es", "L0U0V0Z0G0", "fits_resp_nominal_es", "fits_resp_nominal_es"),
}


def load(folder: str, variant: str) -> pd.DataFrame:
    rows = []
    for p in glob.glob(str(DDM / folder / f"*_{variant}_*.pkl")):
        with open(p, "rb") as f:
            r = pickle.load(f)
        rows.append({k: r.get(k) for k in ("mouse", "split", "train_nll", "test_nll", "n_train", "n_test", "success", "n_iterations",
                                            "max_iterations", "fit_seconds", "guess_model", "fixed_guess_bias", "leak_bounds",
                                            "drift_gain_max", "extrema_samples", "nominal_input", "free_parameters")} | {"params": r["parameters"]})
    return pd.DataFrame(rows)


def bound_flags(r: pd.Series, variant: str) -> str:
    free, _ = make_params(variant, r.guess_model or "fast_only", fixed_guess_bias=bool(r.fixed_guess_bias), leak_bounds=r.leak_bounds,
                          drift_gain_max=r.drift_gain_max, extrema_samples=bool(r.extrema_samples), nominal_input=bool(r.nominal_input))
    out = []
    for name in r.free_parameters:
        lo, hi = free[name].lower_bound, free[name].upper_bound
        tol = AT_BOUND * (hi - lo)
        v = r.params[name]
        if v <= lo + tol:
            out.append(f"{name}:lo")
        elif v >= hi - tol:
            out.append(f"{name}:hi")
    return " ".join(out)


def heldout(df: pd.DataFrame, folds: list[str]) -> pd.Series:
    d = df[df.split.isin(folds)]
    n = d.groupby("mouse").split.nunique()
    return d.groupby("mouse").test_nll.sum()[n == len(folds)]


def ranking(table: pd.DataFrame, label: str) -> pd.DataFrame:
    """table: mouse x family summed held-out NLL (complete mice only)."""
    table = table.dropna()
    delta = table.sub(table[PRIMARY], axis=0)
    _, _, pxp, bor = rfx_bms(-table.to_numpy())
    out = pd.DataFrame({"sum_delta_vs_primary": delta.sum(), "median_delta": delta.median(),
                        "mice_better_gt10": (delta < -THRESHOLD).sum(), "mice_worse_gt10": (delta > THRESHOLD).sum(),
                        "mice_best": table.idxmin(axis=1).value_counts().reindex(table.columns).fillna(0).astype(int),
                        "pxp": pxp, "n_mice": len(table)}).sort_values("sum_delta_vs_primary")
    out.index.name = label
    print(f"\n== {label}: held-out NLL minus primary, summed over folds (negative = better); BOR {bor:.3f}")
    print(out.round(2).to_string())
    return out, delta


def main():
    stamp = date.today().isoformat()
    joint, ctrl = {}, {}
    audit = []
    for fam, (jdir, var, cdir, _) in FAMILIES.items():
        df = load(jdir, var)
        joint[fam] = df
        df["bounds"] = df.apply(bound_flags, axis=1, variant=var)
        audit.append({"family": fam, "n_fits": len(df), "n_mice": df.mouse.nunique(), "failed": int((~df.success.astype(bool)).sum()),
                      "iter_cap": int((df.n_iterations >= df.max_iterations).sum()), "any_bound": int((df.bounds != "").sum()),
                      "bounds": "; ".join(f"{k} x{v}" for k, v in pd.Series(" ".join(df.bounds).split()).value_counts().items()),
                      "median_fit_min": round(df.fit_seconds.median() / 60, 1), "max_fit_min": round(df.fit_seconds.max() / 60, 1)})
        if cdir:
            ctrl[fam] = load(cdir, var)
    audit = pd.DataFrame(audit).set_index("family")
    print("== audit (joint fits)\n" + audit.to_string())
    nested = joint["primary"].merge(joint["no_sv"], on=["mouse", "split"], suffixes=("", "_nosv"))
    worse = nested[nested.train_nll > nested.train_nll_nosv + THRESHOLD]
    print(f"\nnested check: primary train NLL > no-sv + {THRESHOLD} in {len(worse)} of {len(nested)} fits "
          + ", ".join(f"{r.mouse} {r.split} {r.train_nll - r.train_nll_nosv:+.1f}" for r in worse.itertuples()))
    for big, small in [("leak", "primary"), ("urgency", "primary"), ("leak_urgency", "leak"), ("leak_urgency", "urgency"), ("primary", "no_guess"), ("primary", "fixed_guess_bias")]:
        m = joint[big].merge(joint[small], on=["mouse", "split"], suffixes=("", "_s"))
        w = m[m.train_nll > m.train_nll_s + THRESHOLD]
        print(f"nested check: {big} train NLL > {small} + {THRESHOLD} in {len(w)} of {len(m)} fits "
              + ", ".join(f"{r.mouse} {r.split} {r.train_nll - r.train_nll_s:+.1f}" for r in w.itertuples()))

    jt = pd.DataFrame({fam: heldout(df, FOLDS) for fam, df in joint.items()})
    jrank, jdelta = ranking(jt, "joint folds cv0-cv4 (control + pulse)")
    ct = pd.DataFrame({fam: heldout(df, CFOLDS) for fam, df in ctrl.items()})
    crank, cdelta = ranking(ct, "control-only folds ccv0-ccv4")
    side = jrank[["sum_delta_vs_primary", "mice_better_gt10", "mice_worse_gt10", "pxp"]].join(
        crank[["sum_delta_vs_primary", "mice_better_gt10", "mice_worse_gt10", "pxp"]], rsuffix="_ctrl")
    side["rank_joint"] = side.sum_delta_vs_primary.rank().astype(int)
    side["rank_ctrl"] = side.sum_delta_vs_primary_ctrl.rank()
    print("\n== side by side\n" + side.round(2).to_string())
    print("\n== per-mouse joint delta vs primary\n" + jdelta.round(1).to_string())

    rig = {m: ("ucla" if m.startswith("PSUIM") else "uw") for m in jt.index}
    shifts = []
    for fam, (jdir, var, _, cfdir) in FAMILIES.items():
        if not cfdir:
            continue
        c = load(cfdir, var)
        c = c[c.split == "control"].set_index("mouse")
        j = joint[fam][joint[fam].split == "all"].set_index("mouse")
        for m in j.index.intersection(c.index):
            for name in j.loc[m, "free_parameters"]:
                cv, jv = c.loc[m, "params"].get(name), j.loc[m, "params"][name]
                shifts.append({"family": fam, "mouse": m, "rig": rig.get(m), "parameter": name, "control": cv, "joint": jv,
                               "ratio": jv / cv if cv else np.nan})
    shifts = pd.DataFrame(shifts)
    piv = shifts.pivot_table(index=["family", "parameter"], columns="rig", values="ratio", aggfunc="median")
    print("\n== parameter ratio joint all / control-only, median over mice (rig as covariate)\n" + piv.round(2).to_string())

    audit.to_csv(OUT / f"joint_refits_audit_{stamp}.csv")
    side.to_csv(OUT / f"joint_refits_ranking_{stamp}.csv")
    jt.to_csv(OUT / f"joint_refits_heldout_nll_{stamp}.csv")
    shifts.to_csv(OUT / f"joint_refits_parameter_shifts_{stamp}.csv", index=False)
    pd.concat({fam: df.drop(columns=["params", "free_parameters"]).assign(**{k: df.params.map(lambda p, k=k: p.get(k)) for k in
               ["ndt", "a", "z", "drift_gain", "drift_offset", "sv", "leak_rate", "time_constant", "p_guess", "guess_bias", "guess_tau"]})
               for fam, df in joint.items()}, names=["family"]).to_csv(OUT / f"joint_refits_fits_{stamp}.csv")
    print(OUT / f"joint_refits_*_{stamp}.csv")


if __name__ == "__main__":
    main()
