"""Per-cell choice counts for pulse-only full fits (split "pulse") scored on
  pulse    their own training trials (in-sample), at seeds independent of the fit's own (42), and
  control  control trials, never seen by these fits (out of sample).
Output feeds choice_g2_all_candidates-style G² vs exact binomial expectation.

Usage: python -m scripts.paper.choice_g2_control_training --output <new dir> [--seeds 12345 23456]
"""
import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import xlogy

from scripts.ddm.fit_mouse_ddm import EVAL_SEED, select
from scripts.ddm.primacy import make_model
from scripts.ddm.pulse_joint_signatures import model_path
from scripts.ddm.rescore_fits import inputs

CANDIDATES = Path("dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv")


def cell_counts(model, data, sim, coh, pulse):
    alpha = model.likelihood_calc.alpha
    assert alpha == .5 and not model.likelihood_calc.include_censored
    rd, cd, kd = (data[k] for k in ["rt", "choice", "condition"])
    cp, kp = sim["choice"].to_numpy(), sim["signed_coherence"].to_numpy()
    out = []
    for c in np.unique(kd):
        use, pred = kd == c, kp == c
        k1, n = int((cd[use] == 1).sum()), int(use.sum())
        m = np.array([np.sum(cp[pred] == s) for s in (0, 1)])
        p1 = (m[1] + alpha) / (m.sum() + 2 * alpha)
        choice_nll = -(k1 * np.log(p1) + (n - k1) * np.log(1 - p1))
        sat = -(xlogy(k1, k1 / n) + xlogy(n - k1, (n - k1) / n))
        out.append(dict(condition=c, coherence=int(round(100 * coh[use][0])), scheduled_pulse=int(pulse[use][0]),
                        n=n, k=k1, n_model=int(m.sum()), p1=p1, choice_nll=choice_nll, sat=sat))
    return out


def run(out, families, seeds):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs()
    rows = []
    for mouse in np.unique(x["subject_id"]):
        sel = x["subject_id"] == mouse
        sets = {"pulse": np.flatnonzero(sel & (x["sched_pulse_type"] != 0)),
                "control": np.flatnonzero(sel & (x["sched_pulse_type"] == 0))}
        rig = np.unique(x["data_source"][sets["pulse"]]).item()
        for family in families:
            with model_path(family)(mouse).open("rb") as f:
                r = pickle.load(f)
            assert r["split"] == "pulse" and r["n_train"] == len(sets["pulse"]) and r["guess_model"] in ("fast_only", "informed")
            model = make_model(r["variant"], rig, r["fixed_guess_bias"], responded=True,
                               front_end=r["front_end"], ugm=r.get("ugm", False))
            for scored, idx in sets.items():
                data, stim = select(x, idx)
                for seed in seeds:
                    np.random.seed(seed)
                    model.simulator.clear_cache()
                    model._labels = data["condition"]
                    model.precompute(*model._stimulus_shape(stim), n_reps=r["n_reps"])
                    sim = model._simulate_condition(stim, r["parameters"], r["n_reps"])
                    for rec in cell_counts(model, data, sim, x["signed_coherence"][idx], x["sched_pulse_type"][idx]):
                        rows.append(rec | dict(mouse=mouse, family=family, scored=scored, seed=seed))
            model.simulator.clear_cache()
        print(mouse, "complete", flush=True)
    pd.DataFrame(rows).to_csv(out / "cells.csv.gz", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--seeds", type=int, nargs="+", default=[EVAL_SEED, 23456])
    a = ap.parse_args()
    run(a.output, pd.read_csv(CANDIDATES).query("kind=='pulse_only'").family.to_list(), a.seeds)
