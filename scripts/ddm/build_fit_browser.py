"""Data for the fit browser artifact (plans/2026-11-09-fit-browser-artifact.md). EXPLORATORY, descriptive.

For every fitted family (control-only fits, joint all-trial fits under each input mapping, and the sv = 0 counterfactuals),
per group (all mice pooled, then each mouse), per condition (control; early / middle / late x left / right pulse) and
signed coherence: n, P(right), mean RT (s) with binomial / sample SEs, for the data and for the model simulation
(pulse_joint_signatures.simulate: 30 reps, seed 0, the mouse's own responded trials, symmetric cells, all coherences;
cached). Conventions: coh > 0 and pulse sign +1 = rightward. Psychometric fits per condition with the author's method
(src/utils/pmf_utils.fit_psychometric_function, logit_4); correct / error RT histograms (defective densities).

NLL table: the fitting objective (censored quantile QMLE, responded trials): held-out = sum of test NLL over cv0-cv4 per
mouse (joint families); fitted = train NLL of the "all" fit; control-only fits: train NLL on control trials and test NLL
on pulse trials. Values are negative log (quasi-)likelihoods: lower is better; comparable across families only for the
same trials (n_test is reported so mismatches are visible).

Usage: python -m scripts.ddm.build_fit_browser --cache <sim cache> --template scripts/ddm/fit_browser_template.html --html <out.html>
Outputs: dissemination/figures/qc/fit_browser_<date>.json and the HTML page.
"""

import argparse
import json
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")  # tiny fits: threaded BLAS only adds overhead
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from src.utils.pmf_utils import fit_psychometric_function

from scripts.ddm.compare_joint_refits import DDM, FAMILIES, FOLDS, load
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.pulse_joint_signatures import EXTRA_FAMILIES, FE_NORM, FE_POWER, PULSE_ONLY_FAMILIES, REFERENCE, model_path, simulate
import scripts.ddm.pulse_leak_urgency_signatures as PLU
from scripts.ddm.pulse_leak_urgency_signatures import observed
from scripts.ddm.pulse_psychometric import OUT

STAGES = {1: "early", 2: "middle", 3: "late"}
MAX_COH = 100  # all coherences, incl. the +-100% trials (pulse trials exist there too); symmetric cells as elsewhere
RT_EDGES = np.round(np.r_[np.arange(0.3, 2.0, 0.1), 2.0, 2.25, 2.5, 3.0, 4.0, 5.0], 3)
N_BOOT = 200  # data psychometric-fit CIs (resampling trials within each coherence)
PULSE_FOLDS = [f"pcv{k}" for k in range(5)]
PSY_PARAMS = ["mean", "beta", "lapse_rate", "guess_rate"]  # pmf_utils logit_4 coefs: mean = 50% point (% coh), beta = slope
CONDITIONS = ["control"] + [f"{st} {side}" for st in ("early", "middle", "late") for side in ("left", "right")]
CONTROL_ONLY = {  # name: (folder, variant)
    REFERENCE: ("fits_resp_final", "L0U0V1Z0G1"),
    FE_POWER: ("fits_resp_fast_only_fe-power_v2", "L0U0V1Z0G1"),
    FE_NORM: ("fits_resp_fast_only_fe-norm", "L0U0V1Z0G1"),
}
ACC = [("primary", "Integrator (sv)"), ("no_sv", "Integrator, no sv"), ("leak", "Leak"), ("urgency", "Urgency"),
       ("leak_urgency", "Leak + urgency"), ("extrema_E_leak20-200", "Extrema detection (E)"), ("extrema_sampling_ES", "Extrema sampling (ES)")]
PULSE_ONLY_LABELS = [("primary", "Integrator (sv)"), ("no_sv", "Integrator, no sv"), ("leak", "Leak"), ("leak_no_sv", "Leak, no sv"),
                     ("urgency", "Urgency"), ("urgency_no_sv", "Urgency, no sv"), ("leak_urgency", "Leak + urgency"),
                     ("leak_urgency_no_sv", "Leak + urgency, no sv")]
GROUPS = [  # (group label, [(family key, display label)])
    ("Control-only fits (fitted on control trials; pulses predicted)",
     [(REFERENCE, "Integrator, linear"), (FE_POWER, "Integrator, power law"), (FE_NORM, "Integrator, normalization")]),
    ("All trials, linear motion energy",
     ACC + [("no_guess", "Integrator, no fast guesses"), ("fixed_guess_bias", "Integrator, guess bias fixed"), ("free_leak_0-200", "Free leak 0-200 /s")]),
    ("All trials, power law", [(f"power_{k}", l) for k, l in ACC if k != "no_sv"]),
    ("All trials, normalization", [(f"norm_{k}", l) for k, l in ACC if k != "no_sv"]),
    ("All trials, coherence sequence", [(f"nominal_{k}", l) for k, l in ACC]
     + [("nominal_power_primary", "Integrator, power law"), ("stine_nominal_DDM", "Stine 2020 DDM"), ("stine_nominal_ES", "Stine 2020 ES")]),
    ("Pulse-only fits, linear motion energy (fitted on pulse trials; controls predicted)",
     [(f"pulse_linear_{k}", l) for k, l in PULSE_ONLY_LABELS]),
    ("Pulse-only fits, power law (fitted on pulse trials; controls predicted)",
     [(f"pulse_power_{k}", l) for k, l in PULSE_ONLY_LABELS]),
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
    return model_path(base)


def condition(t: pd.DataFrame) -> pd.Series:
    side = np.where(t.s > 0, "right", "left")
    stage = t.stage.map(STAGES).fillna("")
    return pd.Series(np.where(t.s == 0, "control", stage + " " + side), index=t.index)


def summarize(t: pd.DataFrame) -> list[list]:
    """Rows [condition, coh, n, p_right, se_p, rt_mean, se_rt] for one table of trials."""
    if "cond" not in t:
        t = t.assign(cond=condition(t), right=(t.choice == 1).astype(float))
    g = t.groupby(["cond", "coh"])
    out = []
    for (c, coh), x in g:
        n = len(x)
        p = x.right.mean()
        out.append([c, int(coh), n, round(p, 4), round(float(np.sqrt(p * (1 - p) / n)), 4), round(x.rt.mean(), 4),
                    round(x.rt.std(ddof=1) / np.sqrt(n), 4) if n > 1 else None])
    return out


def fit_psy(c, k, n) -> np.ndarray:
    """The author's psychometric fit (src/utils/pmf_utils.py, model "logit_4" as in config/main.yaml):
    P(right) = lapse + (1 - guess - lapse) / (1 + exp(-beta (c - mean))), weighted least squares on the proportion
    right per coherence with weights sqrt(n), default bounds. Returns [mean, beta, lapse_rate, guess_rate]; NaN if the
    fit fails."""
    try:
        f = fit_psychometric_function(c, k / n, trial_counts=n, model_type="logit_4")
    except (RuntimeError, ValueError):
        return np.full(4, np.nan)
    return np.array([f.coefs_[x] for x in ("mean", "var", "lapse_rate", "guess_rate")])


def counts(t: pd.DataFrame, cond: str) -> tuple:
    """(coh, n_right, n) for the psychometric fit. Pulse trials at +-100% exist only with the pulse opposing the motion
    (left pulse at +100, right pulse at -100); at the other end a pulse condition borrows the control trials at that
    coherence (author 2026-11-09: "use 100 coh if no pulse at that"), so every curve is anchored at both ends."""
    x = t[t.cond == cond].groupby("coh").right.agg(["sum", "size"])
    if cond != "control":
        ctl = t[t.cond == "control"].groupby("coh").right.agg(["sum", "size"])
        for c in (-MAX_COH, MAX_COH):
            if c not in x.index and c in ctl.index:
                x.loc[c] = ctl.loc[c]
        x = x.sort_index()
    return x.index.to_numpy(float), x["sum"].to_numpy(float), x["size"].to_numpy(float)


def psy_fits(t: pd.DataFrame, rng=None) -> dict:
    """{condition: {"est": [mean, beta, lapse_rate, guess_rate], "lo", "hi" (95% bootstrap, data only)}}; each condition
    fitted on its own, all four parameters free."""
    cnt = {cond: counts(t, cond) for cond in CONDITIONS}
    cnt = {k: v for k, v in cnt.items() if len(v[0]) >= 4}
    est = {cond: fit_psy(*v) for cond, v in cnt.items()}
    rnd = lambda v: [None if not np.isfinite(x) else round(float(x), 5) for x in v]
    res = {cond: {"est": rnd(v)} for cond, v in est.items()}
    if rng is not None:
        for cond, (c, k, n) in cnt.items():
            bs = np.array([fit_psy(c, rng.binomial(n.astype(int), k / n).astype(float), n) for _ in range(N_BOOT)])
            res[cond]["lo"] = rnd(np.nanpercentile(bs, 2.5, axis=0))
            res[cond]["hi"] = rnd(np.nanpercentile(bs, 97.5, axis=0))
            res[cond]["n_failed"] = int(np.isnan(bs[:, 0]).sum())
    return res


def rt_hists(t: pd.DataFrame) -> dict:
    """{condition: [correct density per bin, error density per bin]}: defective densities (per s), i.e. count in the bin /
    (all non-zero-coherence trials of the condition x bin width), so correct + error areas sum to 1. 0% excluded."""
    t = t[t.coh != 0]
    w = np.diff(RT_EDGES)
    out = {}
    for cond, x in t.groupby("cond"):
        corr = x.choice.to_numpy() == np.sign(x.coh.to_numpy())
        rt = x.rt.to_numpy()
        hc = np.histogram(rt[corr], RT_EDGES)[0] / (len(x) * w)
        he = np.histogram(rt[~corr], RT_EDGES)[0] / (len(x) * w)
        out[cond] = [[round(float(v), 4) for v in hc], [round(float(v), 4) for v in he], int(len(x)), round(float(corr.mean()), 4)]
    return out


def describe(t: pd.DataFrame, rng=None) -> dict:
    t = t.assign(cond=condition(t), right=(t.choice == 1).astype(float))
    return {"rows": summarize(t), "psy": psy_fits(t, rng), "rt": rt_hists(t)}


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
        if fam in PULSE_ONLY_FAMILIES:  # held-out = pcv0-pcv4 test NLL (pulse trials); fitted and control test from "pulse"
            folder, variant = PULSE_ONLY_FAMILIES[fam]
            df = load(folder, variant)
            cv = df[df.split.isin(PULSE_FOLDS)]
            nf = cv.groupby("mouse").split.nunique()
            ho, nt = cv.groupby("mouse").test_nll.sum(), cv.groupby("mouse").n_test.sum()
            pf = df[df.split == "pulse"].set_index("mouse")
            for m in mice:
                full = m in ho and nf[m] == len(PULSE_FOLDS)
                rows.append({"family": fam, "mouse": m, "kind": "pulse_only",
                             "heldout_nll": float(ho[m]) if full else None, "n_heldout": int(nt[m]) if full else None,
                             "fitted_nll": float(pf.loc[m, "train_nll"]) if m in pf.index else None,
                             "n_fitted": int(pf.loc[m, "n_train"]) if m in pf.index else None,
                             "control_test_nll": float(pf.loc[m, "test_nll"]) if m in pf.index else None,
                             "n_control_test": int(pf.loc[m, "n_test"]) if m in pf.index else None,
                             "k": len(pf.loc[m, "free_parameters"]) if m in pf.index else None})
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
    ap.add_argument("--html", type=Path)
    ap.add_argument("--families", nargs="*", help="only these families (with --sim_only: fill the cache in parallel runs)")
    ap.add_argument("--sim_only", action="store_true", help="simulate into the cache and stop")
    ap.add_argument("--tag", default="", help="appended to the JSON name")
    args = ap.parse_args()
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    with np.load(DDM / "pulse_timing_global.npz") as f:
        assert np.array_equal(f["agg_code"], inputs["agg_code"])
        inputs = {**inputs, **{k: f[k] for k in ("pulse_onset_frame0", "pulse_n_frames", "pulse_coherence")}}
    inputs = responded_only(inputs)
    mice = sorted(set(inputs["subject_id"]))
    PLU.MAX_ABS_COH = MAX_COH  # observed() reads it at call time
    obs = observed(inputs, mice)

    members_all = [(g, f, l) for g, ms in GROUPS for f, l in ms if not args.families or f in args.families]
    if args.sim_only:
        for _, fam, _ in members_all:
            override = {"sv": 0.0} if fam.endswith("[sv=0]") else None
            for m in mice:
                simulate(fam, fit_path(fam)(m), inputs, obs, m, args.cache, override)
            print(f"simulated {fam}", flush=True)
        return
    rng = np.random.default_rng(0)
    data = {"all": describe(obs, rng), **{m: describe(obs[obs.mouse == m], rng) for m in mice}}
    print("data done", flush=True)
    fams, groups = {}, []
    for glabel, members in GROUPS:
        keys = []
        for fam, label in members:
            if args.families and fam not in args.families:
                continue
            override = {"sv": 0.0} if fam.endswith("[sv=0]") else None
            path = fit_path(fam)
            sims = [simulate(fam, path(m), inputs, obs, m, args.cache, override) for m in mice]
            allsim = pd.concat(sims, ignore_index=True)
            fams[fam] = {"label": label, "group": glabel, "all": describe(allsim), **{m: describe(sm) for m, sm in zip(mice, sims)}}
            keys.append(fam)
            print(f"summarized {fam}", flush=True)
        if keys:
            groups.append({"label": glabel, "families": keys})
    nll = nll_table(list(fams), mice)
    payload = {"made": date.today().isoformat(), "mice": mice, "conditions": CONDITIONS, "columns": ["cond", "coh", "n", "p", "se_p", "rt", "se_rt"],
               "rt_edges": RT_EDGES.tolist(), "psy_params": PSY_PARAMS, "max_coh": MAX_COH,
               "data": data, "families": fams, "groups": groups, "nll": nll,
               "n_trials": {m: int((obs.mouse == m).sum()) for m in mice}}
    js = json.dumps(clean(payload), separators=(",", ":"), allow_nan=False)
    out = OUT / f"fit_browser_{date.today().isoformat()}{args.tag}.json"
    out.write_text(js)
    html = args.template.read_text().replace("/*__DATA__*/null", js)
    args.html.write_text(html)
    print(f"{out} ({len(js) / 1e6:.2f} MB); {args.html}")


if __name__ == "__main__":
    main()
