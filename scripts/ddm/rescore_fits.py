"""Rescore every full-data fit at independent noise seeds (plans/2026-11-12-rescore-fitted-nll.md).

The stored train_nll is the objective at the fit's own noise draw, which differential evolution optimized over, so it
is optimistic by a model-dependent amount (reports/2026-11-12-likelihood-check.md). Here each family's full-data fit
(joint "all", pulse-only "pulse", control-only "control") is re-simulated on its own training trials with the fitting
objective at independent seeds, and the NLL is split into the choice (outcome) term and the RT term.
Families: those of the fit browser (build_fit_browser.GROUPS, counterfactuals excluded).

Usage: python -m scripts.ddm.rescore_fits --cache DIR [--n_reps 30] [--seeds 12345 23456] [--families ...] [--shard i/n]
  Runs sequentially on the default device (CUDA if present; forked workers cannot use CUDA). For two GPUs run two
  shards with CUDA_VISIBLE_DEVICES=0 / 1 and the same --cache, then once more without --shard to collect.
Output: dissemination/figures/qc/rescored_nll_<date>.csv (one row per family x mouse x seed)
"""

import argparse
import pickle
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.build_fit_browser import CONTROL_ONLY, GROUPS, fit_path
from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select
from scripts.ddm.primacy import make_model
from scripts.ddm.pulse_joint_signatures import OPTIONS
from scripts.ddm.pulse_psychometric import OUT
from src.ddm.likelihood_calculator_censored import CensoredQMLE

_INPUTS = None


def inputs() -> dict:
    global _INPUTS
    if _INPUTS is None:
        x = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
        with np.load(DDM / "pulse_timing_global.npz") as f:
            assert np.array_equal(f["agg_code"], x["agg_code"])
            x = {**x, **{k: f[k] for k in ("pulse_onset_frame0", "pulse_n_frames", "pulse_coherence")}}
        _INPUTS = responded_only(x)
    return _INPUTS


def terms(q: CensoredQMLE, rp, cp, kp, rd, cd, kd) -> tuple[float, float, float]:
    """Total, choice and RT terms of CensoredQMLE.compute_nll (responded data, include_censored False)."""
    total = q.compute_nll(rp, cp, rd, cd, kp, kd)
    choice = rt = 0.0
    for c in np.unique(kd):
        d, m = kd == c, kp == c
        mc = np.array([(cp[m] == k).sum() for k in (0, 1)])
        if mc.sum() == 0:
            continue  # empty-cell penalty: in total only
        choice += q._multinomial_nll(np.array([(cd[d] == k).sum() for k in (0, 1)]), mc)
        for k in (0, 1):
            x = rd[d & (cd == k)]
            if len(x):
                rt += q._rt_nll(x, rp[m & (cp == k)])
    return total, choice, rt


def rescore(fam: str, mouse: str, n_reps: int, seed: int, cache: Path) -> dict:
    out = cache / f"{fam.replace(' ', '_').replace(',', '')}_{mouse}_{n_reps}_{seed}.pkl"
    if out.exists():
        return pickle.load(open(out, "rb"))
    path = fit_path(fam)(mouse)
    r = pickle.load(open(path, "rb"))
    opt = {"fixed_guess_bias": False} | OPTIONS.get(fam, {})
    assert bool(r.get("fixed_guess_bias")) == opt["fixed_guess_bias"] and bool(r.get("nominal_input")) == opt.get("nominal_input", False), fam
    assert r.get("front_end") == opt.get("front_end") and bool(r.get("ugm")) == opt.get("ugm", False), fam
    x = inputs()
    rows = np.flatnonzero(x["subject_id"] == mouse)
    ctl = x["sched_pulse_type"][rows] == 0
    split = path.stem.rsplit("_", 1)[1]
    train = {"all": rows, "pulse": rows[~ctl], "control": rows[ctl]}[split]
    assert len(train) == r["n_train"], (fam, mouse, len(train), r["n_train"])
    data, stim = select(x, train, nominal=opt.get("nominal_input", False))
    rig = "ucla" if mouse.startswith("PSUIM") else "uw"
    model = make_model(r["variant"], rig, opt["fixed_guess_bias"], leak_bounds=opt.get("leak_bounds"), responded=True,
                       extrema_samples=opt.get("extrema_samples", False), nominal_input=opt.get("nominal_input", False),
                       front_end=opt.get("front_end"), nominal_matched=opt.get("nominal_matched", False), ugm=opt.get("ugm", False))
    q = model.likelihood_calc
    assert isinstance(q, CensoredQMLE) and q.nbins == r["likelihood_params"]["nbins"] and q.include_censored == r["likelihood_params"]["include_censored"], fam
    np.random.seed(seed)
    model.simulator.clear_cache()
    model._labels = data["condition"]
    model.precompute(*model._stimulus_shape(stim), n_reps=n_reps)
    res = model._simulate_condition(stim, r["parameters"], n_reps)
    model.simulator.clear_cache()
    tot, ch, rt = terms(q, res["rt"].to_numpy(), res["choice"].to_numpy(), res["signed_coherence"].to_numpy(), data["rt"], data["choice"], data["condition"])
    row = {"family": fam, "mouse": mouse, "split": split, "seed": seed, "n_reps": n_reps, "n_train": int(r["n_train"]),
           "k": len(r["free_parameters"]), "stored_nll": float(r["train_nll"]), "nll": tot, "choice_nll": ch, "rt_nll": rt}
    cache.mkdir(parents=True, exist_ok=True)
    pickle.dump(row, open(out, "wb"))
    return row


def families() -> list[str]:
    return [f for _, ms in GROUPS for f, _ in ms if "[" not in f]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n_reps", type=int, default=30)
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456])
    ap.add_argument("--shard", default="0/1", help="i/n: run every n-th task from i (output written only for 0/1)")
    ap.add_argument("--families", nargs="*")
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    mice = sorted(set(inputs()["subject_id"]))
    fams = args.families or families()
    tasks = [(f, m, args.n_reps, s, args.cache) for f in fams for m in mice for s in args.seeds]
    i, n = map(int, args.shard.split("/"))
    rows = []
    for j, t in enumerate(tasks[i::n]):
        rows.append(rescore(*t))
        if (j + 1) % 20 == 0:
            print(f"{j + 1}/{len(tasks[i::n])}", flush=True)
    if n > 1:
        return
    d = pd.DataFrame(rows)
    out = OUT / f"rescored_nll_{date.today().isoformat()}{args.tag}.csv"
    d.to_csv(out, index=False)
    print(out)


if __name__ == "__main__":
    main()
