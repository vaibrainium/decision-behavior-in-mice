"""Score the joint pulse-weight fits and the joint constant fits they extend on their held-out joint folds (cv0-4 over
all responded trials), per cell, at several seeds (plan 2026-11-19-choice-misfit-followup, step 4h2, criteria A3).
Cells are scored with the committed audit scorer (audit_pulse_choice_rt_score.predictive_score, nbins 9), unchanged;
control and pulse cells are told apart by scheduled_pulse == 0.
Output: <output>/cells.csv.gz, reproduction.csv (stored vs recomputed fold NLL).
Usage: python -m scripts.paper.score_pulse_weight_joint --output <new dir> [--seeds ...]"""
import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import N_FOLDS, cv_folds, select
from scripts.ddm.primacy import make_model
from scripts.ddm.rescore_fits import inputs
from scripts.paper.audit_pulse_choice_rt_score import predictive_score

DDM = Path("/mnt/data/processed/ddm")
FAMILIES = {"pw_shared": ("fits_joint_unfreeze_pulse_weight", "L0U0V1Z0G1", True),
            "pw_shared_no_sv": ("fits_joint_unfreeze_pulse_weight", "L0U0V0Z0G1", True),
            "joint_primary": ("fits_joint_unfreeze_integrators", "L0U0V1Z0G1", False),
            "joint_no_sv": ("fits_joint_unfreeze_integrators", "L0U0V0Z0G1", False)}
PAIRS = {"pw_shared": "joint_primary", "pw_shared_no_sv": "joint_no_sv"}


def run(out, seeds):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs()
    rows, totals = [], []
    for mouse in np.unique(x["subject_id"]):
        mouse_rows = np.flatnonzero(x["subject_id"] == mouse)
        folds = cv_folds(x["condition"][mouse_rows], N_FOLDS)
        rig = np.unique(x["data_source"][mouse_rows]).item()
        for fold in range(N_FOLDS):
            test, train = mouse_rows[folds == fold], mouse_rows[folds != fold]
            training = {k: x[k][train] for k in ("rt", "choice", "condition")}
            for family, (folder, variant, pw) in FAMILIES.items():
                with (DDM / folder / f"{mouse}_{variant}_cv{fold}.pkl").open("rb") as f:
                    r = pickle.load(f)
                assert r["split"] == f"cv{fold}" and r["n_test"] == len(test) and r["n_train"] == len(train)
                assert r["n_reps"] == 15 and r["guess_model"] == "fast_only" and bool(r.get("pulse_weight")) == pw
                assert r.get("front_end") is None and not r.get("ugm", False) and not r.get("fixed_guess_bias")
                data, stim = select(x, test, pulse_weight=pw)
                model = make_model(r["variant"], rig, r["fixed_guess_bias"], responded=True, pulse_weight=pw)
                for seed in seeds:
                    np.random.seed(seed)
                    model.simulator.clear_cache()
                    model._labels = data["condition"]
                    model.precompute(*model._stimulus_shape(stim), n_reps=r["n_reps"])
                    sim = model._simulate_condition(stim, r["parameters"], r["n_reps"])
                    frame, native = predictive_score(model.likelihood_calc, data, sim, training,
                                                     x["signed_coherence"][test], x["sched_pulse_type"][test])
                    meta = dict(mouse=mouse, fold=fold, family=family, seed=seed)
                    rows.append(frame.assign(**meta))
                    totals.append(dict(**meta, stored=r["test_nll"], recomputed=native))
                model.simulator.clear_cache()
        print(mouse, "complete", flush=True)
    pd.concat(rows, ignore_index=True).to_csv(out / "cells.csv.gz", index=False)
    pd.DataFrame(totals).to_csv(out / "reproduction.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456, 34567, 45678, 56789])
    a = ap.parse_args()
    run(a.output, a.seeds)
