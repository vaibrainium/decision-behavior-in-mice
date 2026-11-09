"""Data for the fit browser artifact (plans/2026-11-09-fit-browser-artifact.md). EXPLORATORY, descriptive.

For every fitted family (control-only fits, joint all-trial fits under each input mapping, and the sv = 0 counterfactuals),
per group (all mice pooled, then each mouse), per condition (control; early / middle / late x left / right pulse) and
signed coherence: n, P(right), mean RT (s) with binomial / sample SEs, for the data and for the model simulation
(pulse_joint_signatures.simulate: 30 reps, seed 0, the mouse's own responded trials, symmetric cells, |coh| <= 36;
cached). Conventions: coh > 0 and pulse sign +1 = rightward.

NLL table: the fitting objective (censored quantile QMLE, responded trials): held-out = sum of test NLL over cv0-cv4 per
mouse (joint families); fitted = train NLL of the "all" fit; control-only fits: train NLL on control trials and test NLL
on pulse trials. Values are negative log (quasi-)likelihoods: lower is better; comparable across families only for the
same trials (n_test is reported so mismatches are visible).

Usage: python -m scripts.ddm.build_fit_browser --cache <sim cache> --template scripts/ddm/fit_browser_template.html --html <out.html>
Outputs: dissemination/figures/qc/fit_browser_<date>.json and the HTML page.
"""

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.compare_joint_refits import DDM, FAMILIES, FOLDS, load
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_joint_signatures import EXTRA_FAMILIES, FE_NORM, FE_POWER, REFERENCE, simulate
from scripts.ddm.pulse_leak_urgency_signatures import observed
from scripts.ddm.pulse_psychometric import OUT

STAGES = {1: "early", 2: "middle", 3: "late"}
CONDITIONS = ["control"] + [f"{st} {side}" for st in ("early", "middle", "late") for side in ("left", "right")]
CONTROL_ONLY = {  # name: (folder, variant)
    REFERENCE: ("fits_resp_final", "L0U0V1Z0G1"),
    FE_POWER: ("fits_resp_fast_only_fe-power_v2", "L0U0V1Z0G1"),
    FE_NORM: ("fits_resp_fast_only_fe-norm", "L0U0V1Z0G1"),
}
ACC = [("primary", "Integrator (sv)"), ("no_sv", "Integrator, no sv"), ("leak", "Leak"), ("urgency", "Urgency"),
       ("leak_urgency", "Leak + urgency"), ("extrema_E_leak20-200", "Extrema detection (E)"), ("extrema_sampling_ES", "Extrema sampling (ES)")]
GROUPS = [  # (group label, [(family key, display label)])
    ("Control-only fits (fitted on control trials; pulses predicted)",
     [(REFERENCE, "Integrator, linear"), (FE_POWER, "Integrator, power law"), (FE_NORM, "Integrator, normalization")]),
    ("All trials, linear motion energy",
     ACC + [("no_guess", "Integrator, no fast guesses"), ("fixed_guess_bias", "Integrator, guess bias fixed"), ("free_leak_0-200", "Free leak 0-200 /s")]),
    ("All trials, power law", [(f"power_{k}", l) for k, l in ACC if k != "no_sv"]),
    ("All trials, normalization", [(f"norm_{k}", l) for k, l in ACC if k != "no_sv"]),
    ("All trials, coherence sequence", [(f"nominal_{k}", l) for k, l in ACC]
     + [("nominal_power_primary", "Integrator, power law"), ("stine_nominal_DDM", "Stine 2020 DDM"), ("stine_nominal_ES", "Stine 2020 ES")]),
    ("Counterfactual: fitted parameters with sv = 0 (not fitted)",
     [(f"{k} [sv=0]", l) for k, l in [("primary", "Integrator, linear"), ("leak", "Leak, linear"), ("urgency", "Urgency, linear"),
                                       ("leak_urgency", "Leak + urgency, linear"), ("power_primary", "Integrator, power law"),
                                       ("power_leak_urgency", "Leak + urgency, power law"), ("norm_leak_urgency", "Leak + urgency, normalization"),
                                       ("nominal_primary", "Integrator, coherence sequence")]]),
]


def fit_path(fam: str):
    base = fam.split(" [")[0]
    if base in CONTROL_ONLY:
        folder, variant = CONTROL_ONLY[base]
        return lambda m: DDM / folder / f"{m}_{variant}_control.pkl"
    folder, variant = (FAMILIES.get(base) or EXTRA_FAMILIES[base])[:2]
    return lambda m: DDM / folder / f"{m}_{variant}_all.pkl"


def condition(t: pd.DataFrame) -> pd.Series:
    side = np.where(t.s > 0, "right", "left")
    stage = t.stage.map(STAGES).fillna("")
    return pd.Series(np.where(t.s == 0, "control", stage + " " + side), index=t.index)


def summarize(t: pd.DataFrame) -> list[list]:
    """Rows [condition, coh, n, p_right, se_p, rt_mean, se_rt] for one table of trials."""
    t = t.assign(cond=condition(t), right=(t.choice == 1).astype(float))
    g = t.groupby(["cond", "coh"])
    out = []
    for (c, coh), x in g:
        n = len(x)
        p = x.right.mean()
        out.append([c, int(coh), n, round(p, 4), round(float(np.sqrt(p * (1 - p) / n)), 4), round(x.rt.mean(), 4),
                    round(x.rt.std(ddof=1) / np.sqrt(n), 4) if n > 1 else None])
    return out


def nll_table(families: list[str], mice: list[str]) -> list[dict]:
    rows = []
    for fam in families:
        if "[" in fam:
            continue
        if fam in CONTROL_ONLY:
            folder, variant = CONTROL_ONLY[fam]
            df = load(folder, variant)
            df = df[df.split == "control"].set_index("mouse")
            for m in mice:
                if m in df.index:
                    r = df.loc[m]
                    rows.append({"family": fam, "mouse": m, "kind": "control_only", "fitted_nll": r.train_nll, "n_fitted": int(r.n_train),
                                 "pulse_test_nll": r.test_nll, "n_pulse_test": int(r.n_test) if r.n_test == r.n_test else None,
                                 "k": len(r.free_parameters)})
            continue
        folder, variant = (FAMILIES.get(fam) or EXTRA_FAMILIES[fam])[:2]
        df = load(folder, variant)
        cv = df[df.split.isin(FOLDS)]
        nf = cv.groupby("mouse").split.nunique()
        ho, nt = cv.groupby("mouse").test_nll.sum(), cv.groupby("mouse").n_test.sum()
        al = df[df.split == "all"].set_index("mouse")
        for m in mice:
            rows.append({"family": fam, "mouse": m, "kind": "joint",
                         "heldout_nll": float(ho[m]) if m in ho and nf[m] == len(FOLDS) else None,
                         "n_heldout": int(nt[m]) if m in nt and nf[m] == len(FOLDS) else None,
                         "fitted_nll": float(al.loc[m, "train_nll"]) if m in al.index else None,
                         "n_fitted": int(al.loc[m, "n_train"]) if m in al.index else None,
                         "k": len(al.loc[m, "free_parameters"]) if m in al.index else None})
    return rows


def clean(o):
    """JSON-safe: NaN -> None, numpy scalars -> Python."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.generic):
        o = o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--template", type=Path, default=Path("scripts/ddm/fit_browser_template.html"))
    ap.add_argument("--html", type=Path, required=True)
    args = ap.parse_args()
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    with np.load(DDM / "pulse_timing_global.npz") as f:
        assert np.array_equal(f["agg_code"], inputs["agg_code"])
        inputs = {**inputs, **{k: f[k] for k in ("pulse_onset_frame0", "pulse_n_frames", "pulse_coherence")}}
    inputs = responded_only(inputs)
    mice = sorted(set(inputs["subject_id"]))
    obs = observed(inputs, mice)

    data = {"all": summarize(obs), **{m: summarize(obs[obs.mouse == m]) for m in mice}}
    fams, groups = {}, []
    for glabel, members in GROUPS:
        keys = []
        for fam, label in members:
            override = {"sv": 0.0} if fam.endswith("[sv=0]") else None
            path = fit_path(fam)
            sims = [simulate(fam, path(m), inputs, obs, m, args.cache, override) for m in mice]
            allsim = pd.concat(sims, ignore_index=True)
            fams[fam] = {"label": label, "group": glabel, "all": summarize(allsim),
                         **{m: summarize(s) for m, s in zip(mice, sims)}}
            keys.append(fam)
            print(f"summarized {fam}", flush=True)
        groups.append({"label": glabel, "families": keys})
    nll = nll_table(list(fams), mice)
    payload = {"made": date.today().isoformat(), "mice": mice, "conditions": CONDITIONS, "columns": ["cond", "coh", "n", "p", "se_p", "rt", "se_rt"],
               "data": data, "families": fams, "groups": groups, "nll": nll,
               "n_trials": {m: int((obs.mouse == m).sum()) for m in mice}}
    js = json.dumps(clean(payload), separators=(",", ":"), allow_nan=False)
    out = OUT / f"fit_browser_{date.today().isoformat()}.json"
    out.write_text(js)
    html = args.template.read_text().replace("/*__DATA__*/null", js)
    args.html.write_text(html)
    print(f"{out} ({len(js) / 1e6:.2f} MB); {args.html}")


if __name__ == "__main__":
    main()
