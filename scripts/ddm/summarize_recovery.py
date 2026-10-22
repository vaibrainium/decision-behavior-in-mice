"""Summarize model recovery (next-steps step 4; scripts/ddm/model_recovery.py output in <processed>/ddm/recovery).

Each result is one candidate model fitted to one dataset simulated from a generator model (the mouse's own trials and
fitted parameters), and scored on an independent simulated test set. Reports:
  1. completeness: results per (generator, candidate), and which (mouse, generator, replicate) datasets are complete;
  2. confusion matrix: how often each candidate has the lowest held-out NLL, per generator (complete datasets only);
  3. per mechanism (sv, guesses: removed from the common model; leak, urgency: added to it): the held-out NLL change
     from including the mechanism, on data generated with and without it. "Detected" = including it lowers held-out NLL
     by more than the threshold; hit rate (data with it) and false-alarm rate (data without it), per mouse and pooled,
     at thresholds 0 and 10 NLL (the step 3.3 criterion). One 15-repetition evaluation per fit, so noisier than the
     10-seed x 50-repetition per-mouse comparison of the real data (analysis log 5.6);
  4. optimizer check (candidate = generator): fitted training NLL minus the NLL at the generating parameters with the
     same noise draws (> 0: the optimizer stopped short of a point it could have reached);
  5. parameter recovery (candidate = generator): generating vs recovered values per parameter, correlation over
     mice and replicates, and median absolute error relative to the parameter's range.
Tables are written to <recovery dir>/summary_*.csv.

Usage: python -m scripts.ddm.summarize_recovery [--recovery_dir ddm/recovery]
"""

import argparse
import glob
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import make_params
from scripts.ddm.model_recovery import COMMON, GUESS_MODEL, MODELS

THRESHOLDS = [0.0, 10.0]
NAMES = {"V": "sv", "G": "guesses", "L": "leak", "U": "urgency"}


def switch(variant: str, letter: str, on: bool) -> str:
    i = variant.index(letter) + 1
    return variant[:i] + str(int(on)) + variant[i + 1:]


def mechanism_pairs() -> dict:
    """mechanism -> (model with it, model without it), both among MODELS."""
    pairs = {}
    for letter, name in NAMES.items():
        with_m, without_m = switch(COMMON, letter, True), switch(COMMON, letter, False)
        if with_m in MODELS and without_m in MODELS and with_m != without_m:
            pairs[name] = (with_m, without_m)
    return pairs


def load(recovery_dir: Path) -> pd.DataFrame:
    rows = []
    for p in glob.glob(str(recovery_dir / "*.pkl")):
        with open(p, "rb") as f:
            r = pickle.load(f)
        rows.append({k: r.get(k) for k in ("mouse", "rig", "n", "generator", "candidate", "replicate", "k", "train_nll", "test_nll", "bic",
                                          "truth_train_nll", "truth_test_nll", "guess_model", "fixed_guess_bias")}
                    | {"true": r["true_parameters"], "fit": r["parameters"], "free": r["free_parameters"]})
    return pd.DataFrame(rows)


def main(recovery_dir: Path):
    df = load(recovery_dir)
    if df.empty:
        raise SystemExit(f"no results in {recovery_dir}")
    print(f"{len(df)} results in {recovery_dir}; guess forms {df[['guess_model', 'fixed_guess_bias']].drop_duplicates().to_dict('records')}")
    counts = df.groupby(["generator", "candidate"]).size().unstack(fill_value=0).reindex(index=MODELS, columns=MODELS, fill_value=0)
    print(f"\n1. results per generator (rows) x candidate (columns); expected {df.mouse.nunique()} mice x {df.replicate.nunique()} replicates each:")
    print(counts.to_string())

    key = ["mouse", "generator", "replicate"]
    nll = df.pivot_table(index=key, columns="candidate", values="test_nll")
    complete = nll.dropna()
    if len(complete) and set(MODELS) <= set(complete.columns):
        best = complete[MODELS].idxmin(axis=1)
        conf = pd.crosstab(pd.Series(best.index.get_level_values("generator"), name="generator"), pd.Series(best.to_numpy(), name="best candidate"), normalize="index").reindex(index=MODELS, columns=MODELS, fill_value=0)
        print(f"\n2. confusion (fraction of {len(complete)} complete datasets in which each candidate has the lowest held-out NLL):")
        print(conf.round(2).to_string())
        conf.to_csv(recovery_dir / "summary_confusion.csv")

    print("\n3. per mechanism: held-out NLL(without) - NLL(with); 'detected' = > threshold")
    mech_rows = []
    for name, (with_m, without_m) in mechanism_pairs().items():
        if with_m not in nll or without_m not in nll:
            continue
        delta = (nll[without_m] - nll[with_m]).dropna().rename("delta").reset_index()
        for gen, label in [(with_m, "present"), (without_m, "absent")]:
            d = delta[delta.generator == gen]
            if d.empty:
                continue
            for thr in THRESHOLDS:
                per_mouse = d.groupby("mouse").delta.apply(lambda x: (x > thr).mean())
                mech_rows.append({"mechanism": name, "data": label, "threshold": thr, "n": len(d), "rate_detected": float((d.delta > thr).mean()),
                                  "mean_delta": float(d.delta.mean()), **{m: float(v) for m, v in per_mouse.items()}})
    mech = pd.DataFrame(mech_rows)
    if len(mech):
        print("   rate_detected: hit rate when present, false-alarm rate when absent; per-mouse columns are the same rate per mouse")
        print(mech.round(2).to_string(index=False))
        mech.to_csv(recovery_dir / "summary_mechanisms.csv", index=False)

    same = df[df.generator == df.candidate].copy()
    if len(same):
        same["train_gap"] = same.train_nll - same.truth_train_nll
        same["test_gap"] = same.test_nll - same.truth_test_nll
        print("\n4. optimizer check (candidate = generator): fitted minus generating-parameter NLL, same noise draws")
        print(same.groupby("generator")[["train_gap", "test_gap"]].agg(["median", "max", lambda x: int((x > 5).sum())]).rename(columns={"<lambda_0>": "n > 5"}).round(1).to_string())

        rec = []
        for _, r in same.iterrows():
            free, _ = make_params(r.generator, GUESS_MODEL, fixed_guess_bias=bool(r.fixed_guess_bias))
            for p in r.free:
                lo, hi = free[p].lower_bound, free[p].upper_bound
                rec.append({"generator": r.generator, "mouse": r.mouse, "replicate": r.replicate, "parameter": p,
                            "true": r.true[p], "fit": r.fit[p], "abs_err_range": abs(r.fit[p] - r.true[p]) / (hi - lo)})
        rec = pd.DataFrame(rec)
        g = rec.groupby(["generator", "parameter"])
        summary = pd.DataFrame({"n": g.size(), "r": g[["true", "fit"]].apply(lambda x: x.corr().iloc[0, 1] if len(x) > 2 and x.true.std() > 0 else np.nan),
                                "median_abs_err_of_range": g.abs_err_range.median()})
        print("\n5. parameter recovery (candidate = generator): correlation of generating vs recovered values over mice x replicates,")
        print("   and median absolute error as a fraction of the parameter's range")
        print(summary.round(3).to_string())
        summary.to_csv(recovery_dir / "summary_parameters.csv")
        rec.to_csv(recovery_dir / "summary_parameters_by_fit.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--recovery_dir", default="ddm/recovery", help="relative to processed")
    args = parser.parse_args()
    main(Path(dir_config.data.processed) / args.recovery_dir)
