"""Would separate pulse weights per pulse time help? (plan .agents/plans/2026-10-30-pulse-time-weight-profile.md)

For each mouse and model (sv / no-sv joint all-trial fit, ddm/fits_joint_unfreeze_integrators), scale the pulse component of
the trials in one pulse-time bin by w (others at 1, every other parameter at its fit) and compute the train NLL on all
responded trials with the fixed evaluation seed (common random numbers across w). Bins: UW onsets 0.05 / 0.23 / 0.42 s;
UCLA jittered onsets split at 0.15 s. Rig only sets the binning.

    .venv/bin/python -m scripts.ddm.pulse_time_weight_profile [MOUSE ...]
"""

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import fit_mouse_ddm as F

PROCESSED = Path(dir_config.data.processed)
FITS = PROCESSED / "ddm/fits_joint_unfreeze_integrators"
VARIANTS = {"sv": "L0U0V1Z0G1", "no_sv": "L0U0V0Z0G1"}
WEIGHTS = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
OUT = Path("dissemination/figures/qc")


def pulse_bins(inputs: dict) -> np.ndarray:
    """Pulse-time bin per responded trial (-1 = control)."""
    full = F.load_inputs(PROCESSED / "ddm/ddm_inputs_global_ucla_nofreeze.npz")
    with np.load(PROCESSED / "ddm/pulse_timing_global.npz") as f:
        assert np.array_equal(f["agg_code"], full["agg_code"])
        onset = f["pulse_onset_frame0"]
    pos = {c: i for i, c in enumerate(full["agg_code"])}
    onset_s = onset[[pos[c] for c in inputs["agg_code"]]] / inputs["frame_rate"]
    uw = np.digitize(onset_s, [0.15, 0.33])  # 0.05 / 0.23 / 0.42 s
    ucla = (onset_s >= 0.15).astype(int)
    b = np.where(inputs["data_source"] == "uw", uw, ucla)
    return np.where(inputs["sched_pulse_type"] == 0, -1, b)


def main(mice: list[str]):
    inputs = F.responded_only(F.load_inputs(PROCESSED / "ddm/ddm_inputs_global_ucla_nofreeze.npz"))
    bins = pulse_bins(inputs)
    mice = mice or sorted(np.unique(inputs["subject_id"]))
    rows = []
    for mouse in mice:
        sel = np.flatnonzero(inputs["subject_id"] == mouse)
        rig = np.unique(inputs["data_source"][sel]).item()
        data, (without, pulse) = F.select(inputs, sel, False, True)
        b = bins[sel]
        for label, variant in VARIANTS.items():
            with open(FITS / f"{mouse}_{variant}_all.pkl", "rb") as f:
                fit = pickle.load(f)
            free, fixed = F.make_params(variant, "fast_only", pulse_weight=True)
            model = F.MouseDDM(free_params=free, fixed_params=fixed, device=F.DEVICE, likelihood_params=F.RESPONDED_LIKELIHOOD_PARAMS, censor_at=F.CENSOR_AT, min_rt=F.MIN_RT[rig])
            params = {**fit["parameters"], "noise_weight": 1.0}
            base = F.heldout_nll(model, params, data, (without, pulse), fit["n_reps"])
            rows.append({"mouse": mouse, "rig": rig, "model": label, "bin": -1, "n_bin": 0, "w": 1.0, "nll": base, "fit_train_nll": fit["train_nll"]})
            print(mouse, label, "baseline", round(base, 2), "fit", round(fit["train_nll"], 2), flush=True)
            for k in sorted(set(b[b >= 0])):
                for w in WEIGHTS:
                    scale = np.where(b == k, w, 1.0).astype(np.float32)[:, None]
                    nll = base if w == 1.0 else F.heldout_nll(model, params, data, (without, pulse * scale), fit["n_reps"])
                    rows.append({"mouse": mouse, "rig": rig, "model": label, "bin": k, "n_bin": int((b == k).sum()), "w": w, "nll": nll, "fit_train_nll": fit["train_nll"]})
                    print(mouse, label, f"bin {k} (n={(b == k).sum()}) w={w}: {nll - base:+.2f}", flush=True)
            pd.DataFrame(rows).to_csv(OUT / f"pulse_time_weight_profile_2026-10-30_{'_'.join(mice) if len(mice) < 10 else 'all'}.csv", index=False)


if __name__ == "__main__":
    main(sys.argv[1:])
