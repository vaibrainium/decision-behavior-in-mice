"""Compare the guess-component forms of one variant (plan step 2): single (fit_mouse_ddm default), fast_only,
guess_lapse and fast_only with guess_bias fixed at 0.5, plus the same variant without guesses.

Reports per mouse the CV-summed held-out NLL relative to the single form, BIC on all trials, the fitted guess/lapse
parameters, and the lapse implied by the psychometric asymptote (2 x (1 - accuracy) at 100% coherence on control
trials, all RTs and RT >= 0.6 s), the independent check of the fitted lapse rate.

Usage: python -m scripts.ddm.compare_guess_forms [--variant L0U0V1Z0G1]
"""

import argparse
import glob
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.compare_models import load

FORMS = {"single": "ddm/fits_guess", "fast_only": "ddm/fits_guess_fast_only", "guess_lapse": "ddm/fits_guess_guess_lapse",
         "fast_only_FB": "ddm/fits_guess_fast_only_FB"}  # FB: guess_bias fixed at 0.5 (parsimony rule 3); forms without fits are skipped
SHOWN = ["p_guess", "guess_bias", "guess_tau", "p_lapse", "drift_gain", "a"]


def psychometric_lapse(inputs_path: Path) -> pd.DataFrame:
    d = np.load(inputs_path, allow_pickle=True)
    df = pd.DataFrame({k: d[k] for k in ["subject_id", "signed_coherence", "sched_pulse_type", "rt", "choice", "censored"]})
    df = df[(df.censored == 0) & (df.choice >= 0) & (df.sched_pulse_type == 0) & (df.signed_coherence.abs() == 1.0)]
    df["correct"] = (df.signed_coherence > 0) == (df.choice == 1)
    return pd.DataFrame({"n_100pct": df.groupby("subject_id").size(), "implied_lapse": 2 * (1 - df.groupby("subject_id").correct.mean()),
                         "implied_lapse_rt>=0.6": 2 * (1 - df[df.rt >= 0.6].groupby("subject_id").correct.mean())})


def main(processed: Path, variant: str):
    rows = []
    for form, folder in FORMS.items():
        dirs = [processed / folder] + ([processed / "ddm/fits_guess_warm"] if form == "single" else [])
        for d in dirs:
            for path in glob.glob(str(d / f"*_{variant}_*.pkl")):
                with open(path, "rb") as f:
                    r = pickle.load(f)
                rows.append({"form": form, "mouse": r["mouse"], "split": r["split"], "train_nll": r["train_nll"], "test_nll": r.get("test_nll"),
                             "k": len(r["free_parameters"]), "n": r["n_train"], **{p: r["parameters"].get(p, np.nan) for p in SHOWN}})
    g = pd.DataFrame(rows).sort_values("train_nll").drop_duplicates(["form", "mouse", "split"])  # single: warm refit kept when better
    cv = g[g.split.str.startswith("cv")].groupby(["mouse", "form"]).test_nll.sum().unstack()
    nog = load([processed / "ddm/fits_guess", processed / "ddm/fits_guess_warm"])
    no_guess = variant[:-1] + "0"
    cv["no_guess"] = nog[(nog.variant == no_guess) & nog.split.str.startswith("cv")].groupby("mouse").test_nll.sum()
    rel = cv.sub(cv["single"], axis=0)
    print(f"1. held-out NLL summed over 5 folds, relative to the single form ({variant}; no_guess = {no_guess}):")
    print(rel.round(1).to_string())
    print("summed:", rel.sum().round(1).to_dict())
    a = g[g.split == "all"].assign(bic=lambda x: 2 * x.train_nll + x.k * np.log(x.n))
    b = a.pivot(index="mouse", columns="form", values="bic")
    print("\n2. BIC on all trials, relative to the single form:")
    print(b.sub(b["single"], axis=0).round(1).to_string())
    print("\n3. parameters (all-trial fits):")
    for form in a.form.unique():
        print(f"-- {form}\n{a[a.form == form].set_index('mouse')[SHOWN].sort_index().round(3).to_string()}")
    print("\n4. lapse implied by the psychometric asymptote (control trials, 100% coherence):")
    print(psychometric_lapse(processed / "ddm/ddm_inputs_global.npz").round(3).to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--variant", default="L0U0V1Z0G1")
    args = parser.parse_args()
    main(Path(dir_config.data.processed), args.variant)
