"""Pulse signatures of the joint (control + pulse) refits (plan 2026-10-29-joint-control-pulse-refits, step 6).

Each family's joint "all" fit (fits_joint_unfreeze_*) is simulated per mouse on the mouse's own responded trials with the
input it was fitted on (motion energy S + N from ddm_inputs_global_ucla_nofreeze.npz, or the nominal input with the
nominal pulse for the Stine models), N_REPS repetitions, one seed. Reference: the control-only primary fit (fits_resp_final,
split "control"), simulated the same way.

Statistics are those of scripts/ddm/pulse_descriptive_package.py (responded trials, symmetric cells, |coh| <= 36,
effect = pulse-count-weighted P(choice = pulse sign | pulse) - P(... | control), pp):
  windows: effect for responses 0.3-1.2 s and 1.2-5 s after the pulse onset (controls at the stage's median onset), per mouse;
  profile: effect per bin of (RT - onset), stages pooled per mouse;
  S3: median RT shift (pulse - control) for choices toward the pulse, ms;
  control fit: accuracy and median RT per |coh| on control trials; simulated share of non-responses by 5 s (amendment 11 cap 0.5).

Outputs: dissemination/figures/qc/pulse_joint_signatures_<date>.{png,pdf}, _windows.csv, _profile.csv, _control.csv
Usage:   python -m scripts.ddm.pulse_joint_signatures --cache <dir> [--families primary leak_urgency ...]
"""

import argparse
import pickle
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.ddm.compare_joint_refits import DDM, FAMILIES
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select
from scripts.ddm.primacy import make_model, simulate_outcomes
from scripts.ddm.pulse_descriptive_package import EARLY_BINS, effect, rt_shifts
from scripts.ddm.pulse_leak_urgency_signatures import BINS, observed, pseudo_onsets, with_bins
from scripts.ddm.pulse_psychometric import OUT

N_REPS, SEED = 30, 0
REFERENCE = "primary, control-only fit"
FE_NORM = "primary + normalization, control-only fit"  # plan 2026-10-30-normalization-pulse-prediction
FE_POWER = "primary + power law, control-only fit"  # plan 2026-11-06-input-mapping-x-accumulator, P1
# joint "all" fits of plans 2026-11-06-input-mapping-x-accumulator and -nominal-coherence-joint-fits: family -> (folder, variant)
EXTRA_FAMILIES = {
    **{f"{fe}_{name}": (f"fits_joint_{fe}_integrators", var) for fe in ("power", "norm")
       for name, var in [("primary", "L0U0V1Z0G1"), ("leak", "L1U0V1Z0G1"), ("urgency", "L0U1V1Z0G1"), ("leak_urgency", "L1U1V1Z0G1")]},
    **{f"{fe}_extrema_E_leak20-200": (f"fits_joint_{fe}_leak20-200", "L1U0V1Z0G1") for fe in ("power", "norm", "nominal")},
    **{f"{fe}_extrema_sampling_ES": (f"fits_joint_{fe}_es", "L0U0V1Z0G1") for fe in ("power", "norm", "nominal")},
    **{f"nominal_{name}": ("fits_joint_nominal_integrators", var) for name, var in
       [("primary", "L0U0V1Z0G1"), ("no_sv", "L0U0V0Z0G1"), ("leak", "L1U0V1Z0G1"), ("urgency", "L0U1V1Z0G1"), ("leak_urgency", "L1U1V1Z0G1")]},
    "nominal_power_primary": ("fits_joint_nominal_power", "L0U0V1Z0G1"),
}
# pulse-only fits (plan 2026-11-10-pulse-only-fits): split "pulse" (all pulse trials of the mouse); family -> (folder, variant)
PULSE_ONLY_VARIANTS = [("primary", "L0U0V1Z0G1"), ("no_sv", "L0U0V0Z0G1"), ("leak", "L1U0V1Z0G1"), ("leak_no_sv", "L1U0V0Z0G1"),
                       ("urgency", "L0U1V1Z0G1"), ("urgency_no_sv", "L0U1V0Z0G1"), ("leak_urgency", "L1U1V1Z0G1"), ("leak_urgency_no_sv", "L1U1V0Z0G1")]
PULSE_ONLY_FAMILIES = {f"pulse_{fe}_{name}": (f"fits_pulse_{fe}_integrators", var) for fe in ("linear", "power") for name, var in PULSE_ONLY_VARIANTS}
OPTIONS = {  # family -> make_model options (as the fits)
    "fixed_guess_bias": dict(fixed_guess_bias=True), "extrema_E_leak20-200": dict(leak_bounds=(20, 200)),
    "free_leak_0-200": dict(leak_bounds=(0, 200)), "extrema_sampling_ES": dict(extrema_samples=True),
    "stine_nominal_DDM": dict(nominal_input=True), "stine_nominal_ES": dict(nominal_input=True, extrema_samples=True),
    FE_NORM: dict(front_end="norm"), FE_POWER: dict(front_end="power")}
for _fam in EXTRA_FAMILIES:
    _opt = {}
    if _fam.startswith(("power_", "nominal_power")):
        _opt["front_end"] = "power"
    if _fam.startswith("norm_"):
        _opt["front_end"] = "norm"
    if _fam.startswith("nominal_"):
        _opt.update(nominal_input=True, nominal_matched=True)
    if "extrema_E" in _fam:
        _opt["leak_bounds"] = (20, 200)
    if "extrema_sampling" in _fam:
        _opt["extrema_samples"] = True
    OPTIONS[_fam] = _opt
for _fam in PULSE_ONLY_FAMILIES:
    OPTIONS[_fam] = dict(front_end="power") if _fam.startswith("pulse_power_") else {}


def model_path(fam: str):
    """Fit file per mouse: joint families use the "all" fit, pulse-only families the "pulse" fit."""
    if fam in PULSE_ONLY_FAMILIES:
        folder, variant = PULSE_ONLY_FAMILIES[fam]
        return lambda m: DDM / folder / f"{m}_{variant}_pulse.pkl"
    folder, variant = (FAMILIES.get(fam) or EXTRA_FAMILIES[fam])[:2]
    return lambda m: DDM / folder / f"{m}_{variant}_all.pkl"


def simulate(fam: str, path: Path, inputs: dict, obs: pd.DataFrame, mouse: str, cache: Path, override: dict | None = None) -> pd.DataFrame:
    """override: parameter values replacing the fitted ones (counterfactual, e.g. {'sv': 0.0}); the family name then
    carries the override (e.g. 'leak [sv=0]') and so does the cache file."""
    out = cache / f"{fam.replace(' ', '_').replace(',', '')}_{mouse}.pkl"
    if out.exists():
        return pickle.load(open(out, "rb"))
    with open(path, "rb") as f:
        r = pickle.load(f)
    base = fam.split(" [")[0]  # counterfactual families: '<family> [name=value,...]'
    opt = {"fixed_guess_bias": False} | OPTIONS.get(base, {})
    assert bool(r.get("fixed_guess_bias")) == opt["fixed_guess_bias"] and bool(r.get("nominal_input")) == opt.get("nominal_input", False)
    assert r.get("front_end") == opt.get("front_end") and bool(r.get("nominal_matched")) == opt.get("nominal_matched", False)
    rig = obs.loc[obs.mouse == mouse, "rig"].iloc[0]
    model = make_model(r["variant"], rig, opt["fixed_guess_bias"], leak_bounds=opt.get("leak_bounds"), responded=True,
                       extrema_samples=opt.get("extrema_samples", False), nominal_input=opt.get("nominal_input", False),
                       front_end=opt.get("front_end"), nominal_matched=opt.get("nominal_matched", False))
    rows = np.flatnonzero(inputs["subject_id"] == mouse)  # all responded trials, for the non-response share
    data, stim = select(inputs, rows, nominal=opt.get("nominal_input", False))
    params = dict(r["parameters"])
    for k, v in (override or {}).items():
        assert k in params, f"{k} not a parameter of {fam}"
        params[k] = v
    sim = simulate_outcomes(model, params, stim, data["condition"], N_REPS, SEED)
    keep = obs[obs.mouse == mouse].set_index("row")
    rr = rows[sim.trial.to_numpy()]
    res = pd.DataFrame({"row": rr, "choice_raw": sim.choice.to_numpy(), "rt": sim.rt.to_numpy()})
    nonresp = float((res.choice_raw < 0).mean())
    res = res[(res.choice_raw >= 0) & res.row.isin(keep.index)]
    m = keep.loc[res.row]
    t = pd.DataFrame({"row": res.row.to_numpy(), "mouse": mouse, "rig": rig, "coh": m.coh.to_numpy(), "s": m.s.to_numpy(),
                      "stage": m.stage.to_numpy(), "choice": np.where(res.choice_raw.to_numpy() == 1, 1, -1), "rt": res.rt.to_numpy(),
                      "onset": m.onset.to_numpy()})
    t.attrs["nonresp"] = nonresp
    cache.mkdir(parents=True, exist_ok=True)
    pickle.dump(t, open(out, "wb"))
    return t


def stats_of(t: pd.DataFrame, onsets: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    x = with_bins(t, {k: v for k, v in onsets.items() if k[0] in set(t.mouse)})
    xb = x[x.bin.notna()]
    win = effect(xb.assign(win=np.where(xb.bin.isin(EARLY_BINS), "0.3-1.2", "1.2-5")), ["mouse", "stage", "win"])  # stages pooled per
    win = win.groupby(["mouse", "win"]).apply(lambda m: np.average(m.effect, weights=m.n_pulse), include_groups=False).unstack("win")  # mouse as the package
    prof = effect(xb, ["mouse", "bin"])
    s3 = rt_shifts(x)
    s3 = s3[s3.choice == "toward pulse"].groupby("mouse").apply(lambda m: np.average(m["q0.5"], weights=m.n_pulse), include_groups=False).rename("rt_shift_toward_ms")
    c = t[t.s == 0]
    ctl = pd.DataFrame({"acc_36": c[c.coh.abs() == 36].assign(k=lambda d: d.choice == np.sign(d.coh)).groupby("mouse").k.mean(),
                        "rt50": c.groupby("mouse").rt.median()})
    return win, prof, s3, ctl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--families", nargs="*", default=list(FAMILIES))
    ap.add_argument("--fe_power", action="store_true", help="add the control-only fit with the power-law front end (fits_resp_fast_only_fe-power_v2)")
    ap.add_argument("--fe_norm", action="store_true", help="add the control-only fit with the normalization front end (fits_resp_fast_only_fe-norm)")
    ap.add_argument("--tag", default="", help="appended to the output names")
    ap.add_argument("--override", nargs="*", default=[], metavar="NAME=VALUE",
                    help="counterfactual: also simulate each listed family with these parameters replaced (fitted values otherwise), e.g. sv=0")
    ap.add_argument("--mice", nargs="*", help="subset of mice (default all); per-mouse simulations do not depend on the others")
    args = ap.parse_args()
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    with np.load(DDM / "pulse_timing_global.npz") as f:
        assert np.array_equal(f["agg_code"], inputs["agg_code"])
        inputs = {**inputs, **{k: f[k] for k in ("pulse_onset_frame0", "pulse_n_frames", "pulse_coherence")}}
    inputs = responded_only(inputs)
    mice = sorted(args.mice or set(inputs["subject_id"]))
    obs = observed(inputs, mice)
    onsets = pseudo_onsets(obs)
    models = {REFERENCE: lambda m: DDM / "fits_resp_final" / f"{m}_L0U0V1Z0G1_control.pkl"}
    if args.fe_norm:
        models[FE_NORM] = lambda m: DDM / "fits_resp_fast_only_fe-norm" / f"{m}_L0U0V1Z0G1_control.pkl"
    if args.fe_power:
        models[FE_POWER] = lambda m: DDM / "fits_resp_fast_only_fe-power_v2" / f"{m}_L0U0V1Z0G1_control.pkl"
    for fam in args.families:
        models[fam] = model_path(fam)
    override = {k: float(v) for k, v in (o.split("=") for o in args.override)}
    overrides = {}
    if override:
        tag = ",".join(f"{k}={v:g}" for k, v in override.items())
        for fam in args.families:
            models[f"{fam} [{tag}]"] = models[fam]
            overrides[f"{fam} [{tag}]"] = override
    results = {"data": stats_of(obs, onsets)}
    nonresp = {}
    for name, path in models.items():
        sims = [simulate(name, path(m), inputs, obs, m, args.cache, overrides.get(name)) for m in mice]
        nonresp[name] = {m: s.attrs.get("nonresp", np.nan) for m, s in zip(mice, sims)}
        results[name] = stats_of(pd.concat(sims, ignore_index=True), onsets)
        print(f"simulated {name}", flush=True)

    win = pd.concat({k: v[0].join(v[2]) for k, v in results.items()}, names=["model"]).reset_index()
    ctl = pd.concat({k: v[3] for k, v in results.items()}, names=["model"]).reset_index()
    ctl["sim_nonresp_share"] = [nonresp.get(r.model, {}).get(r.mouse, np.nan) for r in ctl.itertuples()]
    prof = pd.concat({k: v[1] for k, v in results.items()}, names=["model"]).reset_index(level=0)
    data = win[win.model == "data"].set_index("mouse")
    win["err_0.3-1.2"] = win["0.3-1.2"] - win.mouse.map(data["0.3-1.2"])
    win["err_1.2-5"] = win["1.2-5"] - win.mouse.map(data["1.2-5"])
    summ = win.groupby("model", sort=False)[["0.3-1.2", "1.2-5", "rt_shift_toward_ms", "err_0.3-1.2", "err_1.2-5"]].mean()
    summ["rmse_0.3-1.2"] = win.groupby("model", sort=False)["err_0.3-1.2"].apply(lambda e: np.sqrt(np.mean(e ** 2)))
    summ["mice_late_negative"] = win.groupby("model", sort=False)["1.2-5"].apply(lambda v: int((v < 0).sum()))
    summ["max_nonresp"] = pd.Series({k: max(v.values()) for k, v in nonresp.items()})
    pd.set_option("display.width", 250)
    print("\n== window effects (pp), mean over mice; err = model - data\n" + summ.round(2).to_string())
    print("\n== per mouse 0.3-1.2 s / 1.2-5 s effect (pp)\n" + win.pivot(index="mouse", columns="model", values="0.3-1.2").round(1).to_string()
          + "\n\n" + win.pivot(index="mouse", columns="model", values="1.2-5").round(1).to_string())
    print("\n== control trials: accuracy at 36% and median RT; simulated non-response share\n" + ctl.pivot(index="mouse", columns="model", values="sim_nonresp_share").round(3).to_string())

    stem = OUT / f"pulse_joint_signatures_{date.today().isoformat()}{args.tag}"
    win.round(4).to_csv(f"{stem}_windows.csv", index=False)
    prof.round(5).to_csv(f"{stem}_profile.csv", index=False)
    ctl.round(4).to_csv(f"{stem}_control.csv", index=False)
    summ.round(4).to_csv(f"{stem}_summary.csv")

    names = list(models)
    fig, ax = plt.subplots(1, 3, figsize=(17, 5.5))
    mids = (np.array(BINS[:-1]) + np.array(BINS[1:])) / 2
    gp = prof.groupby(["model", "bin"]).effect.mean().unstack("bin")
    cols = plt.cm.tab20(np.linspace(0, 1, len(names)))
    ax[0].plot(mids[gp.columns.astype(int)], gp.loc["data"], "ko-", lw=2.5, label="data", zorder=5)
    for n, c in zip(names, cols):
        ax[0].plot(mids[gp.columns.astype(int)], gp.loc[n], "-", color=c, lw=1.8 if n in (REFERENCE, "primary", "leak_urgency") else 0.9,
                   ls="--" if n == REFERENCE else "-", label=n)
    ax[0].axhline(0, color="0.6", lw=0.6); ax[0].set_xscale("log")
    ax[0].set_xlabel("response time - pulse onset (s, bin centres)"); ax[0].set_ylabel("pulse effect (pp), mean over mice")
    ax[0].set_title("A  pulse-to-response profile (stages pooled)", fontsize=10); ax[0].legend(fontsize=6.5, frameon=False, ncol=2)
    order = ["data"] + names
    for k, w in enumerate(["0.3-1.2", "1.2-5"]):
        a = ax[1 + k]
        piv = win.pivot(index="mouse", columns="model", values=w)[order]
        for i, n in enumerate(order):
            a.scatter(np.full(len(piv), i) + np.random.default_rng(i).uniform(-0.15, 0.15, len(piv)), piv[n], s=12,
                      color="k" if n == "data" else cols[i - 1], alpha=0.7)
            a.plot([i - 0.3, i + 0.3], [piv[n].mean()] * 2, color="k", lw=2)
        a.axhline(0, color="0.6", lw=0.6)
        a.axhline(piv["data"].mean(), color="k", ls=":", lw=0.8)
        a.set_xticks(range(len(order))); a.set_xticklabels(order, rotation=60, ha="right", fontsize=7)
        a.set_ylabel("pulse effect (pp)"); a.set_title(f"{'BC'[k]}  responses {w} s after pulse onset; dots = mice, bar = mean", fontsize=10)
    fig.suptitle("Joint (control + pulse) refits: simulated pulse effect vs data (10 mice, responded trials)", fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{stem}.png", dpi=140); fig.savefig(f"{stem}.pdf")
    print(stem)


if __name__ == "__main__":
    main()
