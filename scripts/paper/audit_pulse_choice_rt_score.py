"""Audit pulse-only choice and RT scores at the stored out-of-fold parameters."""
import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import xlogy

from scripts.ddm.fit_mouse_ddm import EVAL_SEED, N_FOLDS, cv_folds, select
from scripts.ddm.primacy import make_model
from scripts.ddm.pulse_joint_signatures import model_path
from scripts.ddm.rescore_fits import inputs
from src.ddm.likelihood_calculator_censored import EMPTY_CELL_PENALTY

FINALISTS = ("pulse_norm_ugm_no_sv", "pulse_linear_leak_urgency", "pulse_linear_leak")
CANDIDATES = Path("dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv")


def predictive_score(q, data, sim, training, coh, pulse):
    """Resolve the original score and score the same simulations on train-defined RT tertiles."""
    rd, cd, kd = (data[k] for k in ["rt", "choice", "condition"])
    rp, cp, kp = (sim[k].to_numpy() for k in ["rt", "choice", "signed_coherence"])
    assert q.alpha == .5 and q.nbins == 9 and q.rt_nllh_weight == 1 and not q.include_censored
    native = q.compute_nll(rp, cp, rd, cd, kp, kd)
    records = []
    for c in np.unique(kd):
        use, pred = kd == c, kp == c
        observed = np.bincount(cd[use], minlength=2)
        simulated = np.array([np.sum(cp[pred] == side) for side in (0, 1)])
        n = observed.sum()
        p = (simulated + q.alpha) / (simulated.sum() + 2 * q.alpha)
        empty = simulated.sum() == 0
        for side in (0, 1):
            t = rd[use & (cd == side)]
            h = rp[pred & (cp == side)]
            train_side = training["choice"] == side
            local = training["rt"][train_side & (training["condition"] == c)]
            reference = local if len(local) >= 15 else training["rt"][train_side]
            assert len(reference) > 0
            interior = np.unique(np.quantile(reference, [1/3, 2/3]))
            edges = np.r_[-np.inf, interior, np.inf]
            test_bins = np.histogram(t, edges)[0]
            model_bins = np.histogram(h, edges)[0]
            rt_tertile = q._multinomial_nll(test_bins, model_bins)
            native_rt = q._rt_nll(t, h)
            choice = -observed[side] * np.log(p[side])
            saturated = -xlogy(observed[side], observed[side] / n)
            records.append(dict(condition=c, coherence=int(round(100 * coh[use][0])),
                                scheduled_pulse=int(pulse[use][0]), side=side, n=len(t),
                                n_train=len(local), n_model=len(h), n_condition=n,
                                p_side=p[side], choice_nll=choice if not empty else 0.,
                                saturated_choice_nll=saturated, rt_nll=native_rt if not empty else 0.,
                                ternary_rt_nll=rt_tertile if not empty else 0.,
                                pooled_edges=len(local) < 15, penalty=EMPTY_CELL_PENALTY*len(t) if empty else 0.))
    frame = pd.DataFrame(records)
    assert np.isclose(native, frame[["choice_nll", "rt_nll", "penalty"]].to_numpy().sum(), atol=1e-8, rtol=0)
    return frame, native


def run(out, families, seeds):
    out.mkdir(parents=True, exist_ok=False)
    x = inputs()
    rows, totals, support = [], [], []
    for mouse in np.unique(x["subject_id"]):
        pulse_rows = np.flatnonzero((x["subject_id"] == mouse) & (x["sched_pulse_type"] != 0))
        folds = cv_folds(x["condition"][pulse_rows], N_FOLDS)
        rig = np.unique(x["data_source"][pulse_rows]).item()
        for fold in range(N_FOLDS):
            test, train = pulse_rows[folds == fold], pulse_rows[folds != fold]
            data, stim = select(x, test)
            training = {k:x[k][train] for k in ("rt", "choice", "condition")}
            design = pd.MultiIndex.from_product([np.unique(x["condition"][pulse_rows]), [0, 1]], names=["condition", "side"])
            counts = pd.DataFrame(index=design)
            for key, subset in (("n", test), ("n_train", train)):
                pairs = pd.DataFrame({"condition": x["condition"][subset], "side": x["choice"][subset]})
                counts[key] = pairs.value_counts().reindex(design, fill_value=0)
            support.append(counts.reset_index().assign(mouse=mouse, fold=fold))
            for family in families:
                full = model_path(family)(mouse)
                path = full.with_name(full.name.removesuffix("_pulse.pkl") + f"_pcv{fold}.pkl")
                with path.open("rb") as stream:
                    r = pickle.load(stream)
                assert r["split"] == f"pcv{fold}" and r["n_test"] == len(test) and r["n_train"] == len(train)
                assert r["n_reps"] == 15 and r["guess_model"] in ("fast_only", "informed")
                model = make_model(r["variant"], rig, r["fixed_guess_bias"], responded=True,
                                   front_end=r["front_end"], ugm=r.get("ugm", False))
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
    cells = pd.concat(rows, ignore_index=True)
    cells.to_csv(out / "cells.csv.gz", index=False)
    summary = cells.groupby(["family", "seed"])[["choice_nll", "rt_nll", "ternary_rt_nll", "saturated_choice_nll", "penalty", "n"]].sum()
    summary["total"] = summary.choice_nll + summary.rt_nll + summary.penalty
    summary["train_tertiles_total"] = summary.choice_nll + summary.ternary_rt_nll + summary.penalty
    summary["choice_deviance"] = 2 * (summary.choice_nll - summary.saturated_choice_nll)
    summary.to_csv(out / "summary.csv")
    scores = pd.DataFrame(totals)
    scores.to_csv(out / "reproduction.csv", index=False)
    counts = pd.concat(support, ignore_index=True)
    assert counts.n.sum() == 11479 and counts.n_train.sum() == 4 * 11479
    counts.to_csv(out / "coverage.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--all-models", action="store_true")
    parser.add_argument("--seeds", type=int, nargs="+", default=[EVAL_SEED, 23456, 34567])
    args = parser.parse_args()
    models = pd.read_csv(CANDIDATES).query("kind=='pulse_only'").family.to_list() if args.all_models else FINALISTS
    run(args.output, models, args.seeds)
