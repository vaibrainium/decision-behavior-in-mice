"""Per-trial log likelihood in bits (plans/2026-11-12-bits-per-trial.md; author 2026-11-12). EXPLORATORY.

A normalized, additive score: each scored trial gets
  choice bits = log2 P_model(choice | cell) - log2 0.5
  RT bits     = log2 P_model(RT bin | choice, cell) - log2 P_null(RT bin | choice)
with P_model from the fit simulated on the scored trials and pooled per cell (coherence x scheduled pulse condition, the
fitting objective's cells), fixed RT bins (BIN_S wide from 0.3 to 5 s; not data quantiles, so the value of a trial does
not depend on how many trials share its cell), add-0.5 smoothing per category as the QMLE, and P_null = the mouse's
pooled RT histogram of that choice over the scored trials, leave-one-out (same for every model). Positive = information gained over
the null, in bits per trial. Sums and means over any subset of trials (mouse, trial type) are directly comparable.
An evaluation score: the fits optimized the quantile likelihood, not this.

Scored trials: full-data fits ("all" / "pulse" / "control") score their training trials (seed independent of the fit);
--heldout scores each CV fold's test trials with that fold's fit (cv0-4 for joint, pcv0-4 for pulse-only; control-only
families have ccv folds only for some, skipped).

Usage: python -m scripts.ddm.bits_per_trial --cache DIR [--heldout] [--bin 0.1] [--n_reps 60] [--seed 34567]
       [--families ...] [--shard i/n]   (one shard per GPU, then once without --shard to collect)
Outputs: dissemination/figures/qc/bits_per_trial_<date>[_heldout][_bin..].csv.gz (one row per trial x family) and
         bits_summary_<date>[...].csv (per family x mouse x trial type: n, mean bits choice / RT / total)
"""

import argparse
import pickle
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.build_fit_browser import fit_path
from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import cv_folds, N_FOLDS, select
from scripts.ddm.primacy import make_model
from scripts.ddm.pulse_joint_signatures import OPTIONS
from scripts.ddm.pulse_psychometric import OUT
from scripts.ddm.rescore_fits import families, inputs

ALPHA = 0.5
STAGE = {0: "control", 1: "early", 2: "middle", 3: "late"}


def scored_sets(fam: str, mouse: str, heldout: bool) -> list[tuple[Path, np.ndarray]]:
    """(fit file, scored trial rows) pairs for one family and mouse."""
    x = inputs()
    rows = np.flatnonzero(x["subject_id"] == mouse)
    ctl = x["sched_pulse_type"][rows] == 0
    full = fit_path(fam)(mouse)
    split = full.stem.rsplit("_", 1)[1]
    pool = {"all": rows, "pulse": rows[~ctl], "control": rows[ctl]}[split]
    if not heldout:
        return [(full, pool)]
    if split == "control":
        return []
    prefix = "cv" if split == "all" else "pcv"
    folds = cv_folds(x["condition"][pool], N_FOLDS)
    return [(full.with_name(full.name.replace(f"_{split}.pkl", f"_{prefix}{k}.pkl")), pool[folds == k]) for k in range(N_FOLDS)]


def score(fam: str, mouse: str, heldout: bool, bin_s: float, n_reps: int, seed: int, cache: Path) -> pd.DataFrame:
    out = cache / f"{fam.replace(' ', '_').replace(',', '')}_{mouse}_{'ho' if heldout else 'full'}_{bin_s:g}_{n_reps}_{seed}.pkl"
    if out.exists():
        return pickle.load(open(out, "rb"))
    x = inputs()
    edges = np.round(np.arange(0.3, 5.0 + bin_s / 2, bin_s), 6)
    nb = len(edges) - 1
    parts = []
    for path, rows in scored_sets(fam, mouse, heldout):
        r = pickle.load(open(path, "rb"))
        opt = {"fixed_guess_bias": False} | OPTIONS.get(fam.split(" [")[0], {})
        assert bool(r.get("nominal_input")) == opt.get("nominal_input", False) and r.get("front_end") == opt.get("front_end"), fam
        pw, nt = bool(r.get("pulse_weight")), int(r.get("n_pulse_times") or 0)
        data, stim = select(x, rows, nominal=opt.get("nominal_input", False), pulse_weight=pw, pulse_times=nt)
        model = make_model(r["variant"], "ucla" if mouse.startswith("PSUIM") else "uw", opt["fixed_guess_bias"], leak_bounds=opt.get("leak_bounds"),
                           responded=True, extrema_samples=opt.get("extrema_samples", False), nominal_input=opt.get("nominal_input", False),
                           front_end=opt.get("front_end"), nominal_matched=opt.get("nominal_matched", False), ugm=opt.get("ugm", False),
                           pulse_weight=pw, n_pulse_times=nt)
        np.random.seed(seed)
        model.simulator.clear_cache()
        model._labels = data["condition"]
        model.precompute(*model._stimulus_shape(stim), n_reps=n_reps)
        sim = model._simulate_condition(stim, r["parameters"], n_reps)
        model.simulator.clear_cache()
        sc, sk, sr = sim["signed_coherence"].to_numpy(), sim["choice"].to_numpy(), sim["rt"].to_numpy()
        keep = sk >= 0  # responded simulated trials (the likelihood conditions on a response)
        sc, sk, sb = sc[keep], sk[keep].astype(int), np.clip(np.digitize(sr[keep], edges) - 1, 0, nb - 1)
        dc, dk, db = data["condition"], data["choice"].astype(int), np.clip(np.digitize(data["rt"], edges) - 1, 0, nb - 1)
        cells = np.unique(dc)
        ci = {c: i for i, c in enumerate(cells)}
        counts = np.zeros((len(cells), 2, nb))
        m = np.isin(sc, cells)
        np.add.at(counts, (np.vectorize(ci.get)(sc[m]), sk[m], sb[m]), 1)
        n_choice = counts.sum(2)
        p_choice = (n_choice + ALPHA) / (n_choice.sum(1, keepdims=True) + 2 * ALPHA)
        p_bin = (counts + ALPHA) / (n_choice[..., None] + ALPHA * nb)
        i = np.vectorize(ci.get)(dc)
        parts.append(pd.DataFrame({"row": rows, "fit": path.stem.rsplit("_", 1)[1], "cond": dc, "choice": dk, "bin": db,
                                   "log2_p_choice": np.log2(p_choice[i, dk]), "log2_p_bin": np.log2(p_bin[i, dk, db])}))
    if not parts:
        return pd.DataFrame()
    t = pd.concat(parts, ignore_index=True)
    # null RT distribution: the mouse's pooled histogram per choice over the scored trials, leave-one-out (the trial
    # itself removed), so the null has no in-sample advantage
    h = np.zeros((2, nb))
    k, b = t.choice.to_numpy(), t["bin"].to_numpy()
    np.add.at(h, (k, b), 1)
    p0 = (h[k, b] - 1 + ALPHA) / (h.sum(1)[k] - 1 + ALPHA * nb)
    t["bits_choice"] = t.log2_p_choice + 1.0
    t["bits_rt"] = t.log2_p_bin - np.log2(p0)
    t["bits"] = t.bits_choice + t.bits_rt
    sched = x["sched_pulse_type"][t.row.to_numpy()]
    t["type"] = [STAGE[abs(int(v))] for v in sched]
    t["coh"] = np.round(x["signed_coherence"][t.row.to_numpy()] * 100).astype(int)
    t.insert(0, "family", fam)
    t.insert(1, "mouse", mouse)
    t = t.drop(columns=["log2_p_choice", "log2_p_bin"])
    cache.mkdir(parents=True, exist_ok=True)
    pickle.dump(t, open(out, "wb"))
    return t


def summarize(t: pd.DataFrame) -> pd.DataFrame:
    g = t.groupby(["family", "mouse", "type"])
    s = g.agg(n=("bits", "size"), bits_choice=("bits_choice", "mean"), bits_rt=("bits_rt", "mean"), bits=("bits", "mean")).reset_index()
    a = t.groupby(["family", "mouse"]).agg(n=("bits", "size"), bits_choice=("bits_choice", "mean"), bits_rt=("bits_rt", "mean"),
                                           bits=("bits", "mean")).reset_index().assign(type="all")
    return pd.concat([a, s], ignore_index=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--heldout", action="store_true")
    ap.add_argument("--bin", type=float, default=0.1)
    ap.add_argument("--n_reps", type=int, default=60)
    ap.add_argument("--seed", type=int, default=34567)
    ap.add_argument("--families", nargs="*")
    ap.add_argument("--shard", default="0/1")
    args = ap.parse_args()
    mice = sorted(set(inputs()["subject_id"]))
    tasks = [(f, m) for f in (args.families or families()) for m in mice]
    i, n = map(int, args.shard.split("/"))
    out = []
    for j, (f, m) in enumerate(tasks[i::n]):
        out.append(score(f, m, args.heldout, args.bin, args.n_reps, args.seed, args.cache))
        if (j + 1) % 20 == 0:
            print(f"{j + 1}/{len(tasks[i::n])}", flush=True)
    if n > 1:
        return
    t = pd.concat([o for o in out if len(o)], ignore_index=True)
    tag = f"{date.today().isoformat()}{'_heldout' if args.heldout else ''}{'' if args.bin == 0.1 else f'_bin{args.bin:g}'}"
    t.to_csv(OUT / f"bits_per_trial_{tag}.csv.gz", index=False, float_format="%.5f")
    s = summarize(t)
    s.to_csv(OUT / f"bits_summary_{tag}.csv", index=False, float_format="%.5f")
    print(OUT / f"bits_summary_{tag}.csv")


if __name__ == "__main__":
    main()
