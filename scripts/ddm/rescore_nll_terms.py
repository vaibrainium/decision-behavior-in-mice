"""Rescore full-data fits with the fitting objective at an independent noise seed (EVAL_SEED), split into the choice
(outcome) term and the RT term (author 2026-11-12: "is our likelihood calculation incorrect?"). EXPLORATORY.
Pulse-only fits (split "pulse", train = pulse trials), three sv / no-sv pairs, 10 mice. Stored train_nll is the value at
the fitting seed (DE optimized over that fixed noise draw), so rescored - stored = optimism of the fitted NLL.
Usage: python -m scripts.ddm.rescore_nll_terms   Output: dissemination/figures/qc/rescore_nll_terms_<date>.csv"""
import pickle
from datetime import date

import numpy as np
import pandas as pd

from scripts.ddm.pulse_psychometric import OUT
from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select, EVAL_SEED
from scripts.ddm.primacy import make_model
from src.ddm.likelihood_calculator_censored import CensoredQMLE
inputs = responded_only(load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz"))
pairs = [("fits_pulse_linear_integrators", "L1U1V1Z0G1", "L1U1V0Z0G1"), ("fits_pulse_power_integrators", "L1U0V1Z0G1", "L1U0V0Z0G1"),
         ("fits_pulse_linear_integrators", "L0U0V1Z0G1", "L0U0V0Z0G1")]
rows = []
for folder, *vs in pairs:
    for v in vs:
        for m in sorted(set(inputs["subject_id"])):
            r = pickle.load(open(DDM / folder / f"{m}_{v}_pulse.pkl", "rb"))
            mr = np.flatnonzero(inputs["subject_id"] == m)
            train = mr[inputs["sched_pulse_type"][mr] != 0]
            data, stim = select(inputs, train)
            rig = "ucla" if m.startswith("PSUIM") else "uw"
            model = make_model(v, rig, False, responded=True, front_end=r["front_end"])
            np.random.seed(EVAL_SEED); model.simulator.clear_cache(); model._labels = data["condition"]
            model.precompute(*model._stimulus_shape(stim), n_reps=r["n_reps"])
            res = model._simulate_condition(stim, r["parameters"], r["n_reps"])
            q = model.likelihood_calc; assert isinstance(q, CensoredQMLE)
            rp, cp, kp = res["rt"].to_numpy(), res["choice"].to_numpy(), res["signed_coherence"].to_numpy()
            rd, cd, kd = data["rt"], data["choice"], data["condition"]
            total = q.compute_nll(rp, cp, rd, cd, kp, kd)
            choice = rt = 0.0
            for c in np.unique(kd):
                d, mm = kd == c, kp == c
                dc = np.array([(cd[d] == k).sum() for k in (0, 1)]); mc = np.array([(cp[mm] == k).sum() for k in (0, 1)])
                choice += q._multinomial_nll(dc, mc)
                for k in (0, 1):
                    x = rd[d & (cd == k)]
                    if len(x): rt += q._rt_nll(x, rp[mm & (cp == k)])
            rows.append(dict(folder=folder, variant=v, mouse=m, stored=r["train_nll"], rescored=total, choice=choice, rt=rt))
            print(folder, v, m, round(r["train_nll"], 2), round(total, 2), round(choice, 1), round(rt, 1), flush=True)
pd.DataFrame(rows).to_csv(OUT / f"rescore_nll_terms_{date.today().isoformat()}.csv", index=False)
