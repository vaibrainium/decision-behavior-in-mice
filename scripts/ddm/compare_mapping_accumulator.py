"""Input mapping x accumulator and nominal-coherence joint fits: audit and the comparisons fixed in advance in
plans/2026-11-06-input-mapping-x-accumulator.md (rules A, B) and plans/2026-11-06-nominal-coherence-joint-fits.md
(rules 5a, 5b). Pulse signatures (rule C / 5c) and the P1 frozen prediction (rule D) are made with pulse_joint_signatures.

All fits: responded control + pulse trials, ddm_inputs_global_ucla_nofreeze.npz, folds cv0-cv4 identical across folders,
so held-out NLLs are paired by mouse. Linear = the motion-energy joint fits of 2026-10-29 (fits_joint_unfreeze_*).

  audit: fits per family, optimizer failures, iteration cap, parameters within 1% of a bound (incl. fe_gamma, fe_beta,
         fe_tau); a family enters a comparison only for mice with all five folds.
  A:  per accumulator, held-out NLL (sum cv0-cv4) of power - linear and norm - linear per mouse; t test and Wilcoxon over
      mice, Holm over the 12 tests. "fits better" = summed difference < -30 AND Holm p < 0.05 (either test reported).
  B:  within each mapping (linear, power, norm, nominal), ranking minus that mapping's primary model; every integrator
      variant vs E and vs ES (paired Wilcoxon, Holm within the mapping); best family per mapping. "Accumulator conclusion
      does not depend on the mapping" if every integrator beats E and ES in every mapping and the best family is the same.
  5a: nominal - linear per family (7 families incl. no_sv), per mouse also per 1,000 held-out trials; t and Wilcoxon, Holm
      over the families present; plus nominal + power vs nominal primary.
Partial data are reported as such (n mice per comparison); final conclusions need 10 mice.

Usage:  python -m scripts.ddm.compare_mapping_accumulator [--tag _partial]
Outputs: dissemination/figures/qc/mapping_accumulator_*_<date><tag>.csv
"""

import argparse
from datetime import date

import numpy as np
import pandas as pd
from scipy import stats

from scripts.ddm.compare_joint_refits import AT_BOUND, FOLDS, THRESHOLD, heldout, load
from scripts.ddm.fit_mouse_ddm import make_params
from scripts.ddm.pulse_psychometric import OUT

GAIN_THRESHOLD = 30.0  # rule A: above the measured 2 SD Monte Carlo noise (28.9) of a summed front-end difference
ACCUMULATORS = {  # name: (variant, folder suffix, options)
    "primary": ("L0U0V1Z0G1", "integrators", {}), "no_sv": ("L0U0V0Z0G1", "integrators", {}),
    "leak": ("L1U0V1Z0G1", "integrators", {}), "urgency": ("L0U1V1Z0G1", "integrators", {}),
    "leak_urgency": ("L1U1V1Z0G1", "integrators", {}),
    "E": ("L1U0V1Z0G1", "leak20-200", {"leak_bounds": (20.0, 200.0)}), "ES": ("L0U0V1Z0G1", "es", {"extrema_samples": True}),
}
INTEGRATORS = ["primary", "no_sv", "leak", "urgency", "leak_urgency"]
MAPPINGS = {  # mapping: (folder prefix, make_params options)
    "linear": ("fits_joint_unfreeze_", {}), "power": ("fits_joint_power_", {"front_end": "power"}),
    "norm": ("fits_joint_norm_", {"front_end": "norm"}), "nominal": ("fits_joint_nominal_", {"nominal_input": True, "nominal_matched": True}),
}
NOMINAL_POWER = ("fits_joint_nominal_power", "L0U0V1Z0G1", {"nominal_input": True, "nominal_matched": True, "front_end": "power"})


def bounds(r: pd.Series, variant: str, opts: dict) -> str:
    free, _ = make_params(variant, "fast_only", **opts)
    out = []
    for name in r.free_parameters:
        lo, hi = free[name].lower_bound, free[name].upper_bound
        v = r.params[name]
        if v <= lo + AT_BOUND * (hi - lo):
            out.append(f"{name}:lo")
        elif v >= hi - AT_BOUND * (hi - lo):
            out.append(f"{name}:hi")
    return " ".join(out)


def gather():
    """{(mapping, accumulator): fits DataFrame} for every folder that exists, plus the audit table."""
    fits, audit = {}, []
    for mapping, (prefix, mopts) in MAPPINGS.items():
        for acc, (variant, suffix, aopts) in ACCUMULATORS.items():
            folder = prefix + suffix
            if mapping in ("power", "norm") and acc == "no_sv":
                continue  # not in the mapping plan
            df = load(folder, variant)
            if df.empty:
                continue
            opts = {**mopts, **aopts}
            df["bounds"] = df.apply(bounds, axis=1, variant=variant, opts=opts)
            fits[(mapping, acc)] = df
            audit.append(audit_row(mapping, acc, df))
    df = load(NOMINAL_POWER[0], NOMINAL_POWER[1])
    if not df.empty:
        df["bounds"] = df.apply(bounds, axis=1, variant=NOMINAL_POWER[1], opts=NOMINAL_POWER[2])
        fits[("nominal_power", "primary")] = df
        audit.append(audit_row("nominal_power", "primary", df))
    return fits, pd.DataFrame(audit).set_index(["mapping", "accumulator"])


def audit_row(mapping: str, acc: str, df: pd.DataFrame) -> dict:
    return {"mapping": mapping, "accumulator": acc, "n_fits": len(df), "n_mice": df.mouse.nunique(),
            "mice_all_folds": int((df[df.split.isin(FOLDS)].groupby("mouse").split.nunique() == len(FOLDS)).sum()),
            "has_all_split": int((df.split == "all").sum()), "failed": int((~df.success.astype(bool)).sum()),
            "iter_cap": int((df.n_iterations >= df.max_iterations).sum()),
            "bounds": "; ".join(f"{k} x{v}" for k, v in pd.Series(" ".join(df.bounds).split()).value_counts().items())}


def paired(a: pd.Series, b: pd.Series) -> dict:
    """a - b per mouse (complete mice in both)."""
    d = (a - b).dropna()
    n = len(d)
    out = {"n_mice": n, "sum": d.sum(), "median": d.median() if n else np.nan, "mice_better_gt10": int((d < -THRESHOLD).sum()),
           "mice_worse_gt10": int((d > THRESHOLD).sum()), "t_p": np.nan, "wilcoxon_p": np.nan, "dz": np.nan}
    if n >= 3 and d.std(ddof=1) > 0:
        out.update(t_p=stats.ttest_1samp(d, 0).pvalue, dz=d.mean() / d.std(ddof=1))
    if n >= 3 and (d != 0).any():
        out["wilcoxon_p"] = stats.wilcoxon(d).pvalue
    return out


def holm(p: pd.Series) -> pd.Series:
    p = p.astype(float)
    ok = p.dropna().sort_values()
    m = len(ok)
    adj = np.minimum(1, np.maximum.accumulate([(m - i) * v for i, v in enumerate(ok.to_numpy())]))
    return pd.Series(adj, index=ok.index).reindex(p.index)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", default="", help="appended to the output names (e.g. _partial)")
    args = ap.parse_args()
    stamp = f"{date.today().isoformat()}{args.tag}"
    fits, audit = gather()
    print("== audit\n" + audit.to_string())
    ho = pd.DataFrame({k: heldout(df, FOLDS) for k, df in fits.items()})
    ho.columns = pd.MultiIndex.from_tuples(ho.columns, names=["mapping", "accumulator"])
    n_test = {k: df[df.split.isin(FOLDS)].groupby("mouse").n_test.sum() for k, df in fits.items()}

    # A: power / norm vs linear, per accumulator
    rows = []
    for fe in ("power", "norm"):
        for acc in ACCUMULATORS:
            if (fe, acc) in ho and ("linear", acc) in ho:
                rows.append({"comparison": f"{fe} - linear", "accumulator": acc, **paired(ho[(fe, acc)], ho[("linear", acc)])})
    ruleA = pd.DataFrame(rows)
    if len(ruleA):
        for test in ("t_p", "wilcoxon_p"):
            ruleA[f"{test}_holm"] = holm(ruleA[test]).to_numpy()
        ruleA["fits_better"] = (ruleA["sum"] < -GAIN_THRESHOLD) & ((ruleA.t_p_holm < 0.05) | (ruleA.wilcoxon_p_holm < 0.05))
        ruleA["complete"] = ruleA.n_mice == 10
        print(f"\n== rule A: mapping minus linear, summed held-out NLL over cv0-cv4 (negative = mapping better); Holm over {len(ruleA)} tests\n"
              + ruleA.round(3).to_string(index=False))

    # B: ranking within each mapping; integrators vs E and ES
    rankings, versus, best = [], [], {}
    for mapping in ("linear", "power", "norm", "nominal"):
        cols = [acc for acc in ACCUMULATORS if (mapping, acc) in ho]
        if "primary" not in cols:
            continue
        t = ho[mapping][cols].dropna()
        if t.empty:
            continue
        delta = t.sub(t["primary"], axis=0)
        r = pd.DataFrame({"sum_delta_vs_primary": delta.sum(), "median_delta": delta.median(), "mice_better_gt10": (delta < -THRESHOLD).sum(),
                          "mice_worse_gt10": (delta > THRESHOLD).sum(), "mice_best": t.idxmin(axis=1).value_counts().reindex(cols).fillna(0).astype(int),
                          "n_mice": len(t)}).sort_values("sum_delta_vs_primary")
        r.insert(0, "mapping", mapping)
        rankings.append(r)
        best[mapping] = r.index[0]
        vs = []
        for integ in [c for c in cols if c in INTEGRATORS and c != "no_sv"]:  # the plan's integrators (no_sv only in linear/nominal)
            for ext in [c for c in cols if c in ("E", "ES")]:
                vs.append({"mapping": mapping, "integrator": integ, "vs": ext, **paired(t[integ], t[ext])})
        vs = pd.DataFrame(vs)
        if len(vs):
            vs["wilcoxon_p_holm"] = holm(vs.wilcoxon_p).to_numpy()
            vs["integrator_better"] = (vs["sum"] < 0) & (vs.wilcoxon_p_holm < 0.05)
            versus.append(vs)
    if rankings:
        rankings = pd.concat(rankings)
        print("\n== rule B: ranking within each mapping (minus that mapping's primary model; complete mice only)\n" + rankings.round(2).to_string())
    if versus:
        versus = pd.concat(versus)
        print("\n== rule B: integrator minus extrema model, per mapping (negative = integrator better), Holm within mapping\n"
              + versus.round(3).to_string(index=False))
        all_beat = bool(versus.integrator_better.all())
        same_best = len(set(best.values())) == 1
        complete = bool((versus.n_mice == 10).all()) and set(best) == {"linear", "power", "norm", "nominal"}
        print(f"\nbest family per mapping: {best}")
        print(f"every integrator beats E and ES in every mapping: {all_beat}; same best family: {same_best}; "
              f"all four mappings with 10 mice: {complete}"
              + ("" if complete else "  (PARTIAL: not the final rule-B verdict)"))

    # 5a: nominal - linear per family (+ per 1,000 held-out trials), nominal power vs nominal primary
    rows = []
    for acc in ACCUMULATORS:
        if ("nominal", acc) in ho and ("linear", acc) in ho:
            row = paired(ho[("nominal", acc)], ho[("linear", acc)])
            per1k = ((ho[("nominal", acc)] - ho[("linear", acc)]) / n_test[("linear", acc)] * 1000).dropna()
            rows.append({"comparison": "nominal - linear", "accumulator": acc, **row, "mean_per_1000_trials": per1k.mean()})
    nom = pd.DataFrame(rows)
    if len(nom):
        for test in ("t_p", "wilcoxon_p"):
            nom[f"{test}_holm"] = holm(nom[test]).to_numpy()
        print(f"\n== rule 5a: nominal coherence minus motion energy (negative = nominal better); Holm over {len(nom)} families\n"
              + nom.round(3).to_string(index=False))
    if ("nominal_power", "primary") in ho and ("nominal", "primary") in ho:
        npw = pd.DataFrame([{"comparison": "nominal power - nominal linear", "accumulator": "primary",
                             **paired(ho[("nominal_power", "primary")], ho[("nominal", "primary")])}])
        print("\n== nominal + power law minus nominal (primary model)\n" + npw.round(3).to_string(index=False))
        nom = pd.concat([nom, npw], ignore_index=True)

    params = pd.concat({f"{m}|{a}": df[df.split == "all"].set_index("mouse").params.apply(pd.Series) for (m, a), df in fits.items()
                        if (df.split == "all").any()}, names=["family"])
    fe = [c for c in ("fe_gamma", "fe_beta", "fe_tau") if c in params]
    if fe:
        print("\n== front-end parameters of the 'all' fits\n" + params[fe].dropna(how="all").round(3).to_string())

    audit.to_csv(OUT / f"mapping_accumulator_audit_{stamp}.csv")
    ho.to_csv(OUT / f"mapping_accumulator_heldout_nll_{stamp}.csv")
    for name, t in [("ruleA", ruleA), ("ruleB_ranking", rankings), ("ruleB_vs_extrema", versus), ("nominal", nom)]:
        if isinstance(t, pd.DataFrame) and len(t):
            t.to_csv(OUT / f"mapping_accumulator_{name}_{stamp}.csv")
    params.to_csv(OUT / f"mapping_accumulator_params_{stamp}.csv")
    print(f"\n{OUT}/mapping_accumulator_*_{stamp}.csv")


if __name__ == "__main__":
    main()
