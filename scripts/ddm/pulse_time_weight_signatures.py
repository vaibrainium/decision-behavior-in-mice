"""Does a fitted early-pulse weight bring the predicted pulse effect up to the data? (plan .agents/plans/2026-10-30-pulse-time-weights.md, step 5)

PSUIM6 (early weight ~3 in both models) and PSUIM7 (early 2.1 without sv, 1.0 with sv). Each mouse's joint all-trial fit
(all weights 1, fits_joint_unfreeze_integrators) and per-pulse-time fit (fits_joint_unfreeze_pulse_time_weights), sv and
no-sv, simulated on the mouse's responded trials with the per-pulse-time input, N_REPS repetitions, one seed. Statistics as
scripts/ddm/pulse_joint_signatures.py (pulse_descriptive_package definitions), plus the window effects per pulse time
(stage) before pooling.

    .venv/bin/python -m scripts.ddm.pulse_time_weight_signatures
"""

import pickle

import numpy as np
import pandas as pd

from scripts.ddm.compare_joint_refits import DDM
from scripts.ddm.fit_mouse_ddm import load_inputs, n_pulse_times, responded_only, select
from scripts.ddm.primacy import make_model, simulate_outcomes
from scripts.ddm.pulse_descriptive_package import EARLY_BINS, effect
from scripts.ddm.pulse_joint_signatures import stats_of
from scripts.ddm.pulse_leak_urgency_signatures import observed, pseudo_onsets, with_bins

MICE = ["PSUIM6", "PSUIM7"]
MODELS = {"sv": "L0U0V1Z0G1", "no_sv": "L0U0V0Z0G1"}
FITS = {"joint (w = 1)": "fits_joint_unfreeze_integrators", "per-time weights": "fits_joint_unfreeze_pulse_time_weights"}
N_REPS, SEED = 30, 0
OUT = "dissemination/figures/qc/pulse_time_weight_signatures_2026-10-31_{}.csv"


def simulate(r: dict, inputs: dict, obs: pd.DataFrame, mouse: str) -> pd.DataFrame:
    rig = obs.loc[obs.mouse == mouse, "rig"].iloc[0]
    model = make_model(r["variant"], rig, False, responded=True)
    rows = np.flatnonzero(inputs["subject_id"] == mouse)
    data, stim = select(inputs, rows, pulse_times=n_pulse_times(inputs, rows))
    sim = simulate_outcomes(model, r["parameters"], stim, data["condition"], N_REPS, SEED)
    keep = obs[obs.mouse == mouse].set_index("row")
    res = pd.DataFrame({"row": rows[sim.trial.to_numpy()], "choice_raw": sim.choice.to_numpy(), "rt": sim.rt.to_numpy()})
    res = res[(res.choice_raw >= 0) & res.row.isin(keep.index)]
    m = keep.loc[res.row]
    return pd.DataFrame({"row": res.row.to_numpy(), "mouse": mouse, "rig": rig, "coh": m.coh.to_numpy(), "s": m.s.to_numpy(), "stage": m.stage.to_numpy(),
                         "choice": np.where(res.choice_raw.to_numpy() == 1, 1, -1), "rt": res.rt.to_numpy(), "onset": m.onset.to_numpy()})


def per_stage(t: pd.DataFrame, onsets: dict) -> pd.DataFrame:
    xb = with_bins(t, {k: v for k, v in onsets.items() if k[0] in set(t.mouse)})
    xb = xb[xb.bin.notna()]
    e = effect(xb.assign(win=np.where(xb.bin.isin(EARLY_BINS), "0.3-1.2", "1.2-5")), ["mouse", "stage", "win"])
    return e.pivot_table(index=["mouse", "stage"], columns="win", values="effect")


def main():
    inputs = responded_only(load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz"))
    obs = observed(inputs, MICE)
    onsets = pseudo_onsets(obs)
    pooled, stages = {}, {}
    win, _, s3, ctl = stats_of(obs, onsets)
    pooled["data"], stages["data"] = win.join(s3).join(ctl), per_stage(obs, onsets)
    for label, variant in MODELS.items():
        for fit_name, folder in FITS.items():
            sims, weights = [], {}
            for mouse in MICE:
                with open(DDM / folder / f"{mouse}_{variant}_all.pkl", "rb") as f:
                    r = pickle.load(f)
                weights[mouse] = [round(r["parameters"].get(k, 1.0), 2) for k in ("noise_weight", "noise_weight_2")]
                sims.append(simulate(r, inputs, obs, mouse))
            t = pd.concat(sims, ignore_index=True)
            name = f"{label}, {fit_name}"
            win, _, s3, ctl = stats_of(t, onsets)
            pooled[name] = win.join(s3).join(ctl).assign(weights=pd.Series({m: str(w) for m, w in weights.items()}))
            stages[name] = per_stage(t, onsets)
            print("simulated", name, weights, flush=True)
    pooled = pd.concat(pooled, names=["model"]).reset_index()
    stages = pd.concat(stages, names=["model"]).reset_index()
    pooled.to_csv(OUT.format("pooled"), index=False)
    stages.to_csv(OUT.format("per_pulse_time"), index=False)
    pd.set_option("display.width", 250)
    print("== pooled over pulse times (pp; RT shift toward pulse in ms; control accuracy at 36% and median RT)")
    print(pooled.round(3).to_string(index=False))
    print("== per pulse time (stage 1 = early, 2 = middle), pp")
    print(stages.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
