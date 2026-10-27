"""Scheduled pulse timing per trial, aligned with ddm_inputs_<region>.npz by agg_code (primacy plan, amendment 13, item 4).

The DDM inputs file holds the pulse only as filtered motion energy; the paper-exact Stine et al. models need it in
nominal units. This writes, for every trial of the inputs file (same order):
  pulse_onset_frame0  0-based 60 Hz frame at which the pulse starts (as in build_ddm_inputs), -1 without a scheduled pulse
  pulse_n_frames      pulse length in frames (0 without)
  pulse_coherence     scheduled pulse coherence (fraction), nan without
Check: in each pulse trial, the pulse component of the input (signal - coherence x onset response) is zero before
pulse_onset_frame0 and peaks within the pulse response's peak lag of it.

Output: <processed>/ddm/pulse_timing_<region>.npz (the inputs file is not changed).

Usage: python -m scripts.ddm.build_pulse_timing [--region global]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.compute_motion_energy_full import convert_to_frame_units
from scripts.ddm.fit_mouse_ddm import load_inputs


def main(region):
    processed = Path(dir_config.data.processed)
    inputs = load_inputs(processed / "ddm" / f"ddm_inputs_{region}.npz")
    trials = pd.concat([pd.read_csv(processed / "valid_data.csv"), pd.read_csv(processed / "censored_trials.csv")], ignore_index=True)
    trials = convert_to_frame_units(trials.copy())
    assert trials.agg_code.is_unique, "agg_code must identify a trial"
    t = trials.set_index("agg_code").loc[inputs["agg_code"]]

    pulsed = inputs["sched_pulse_type"] != 0
    onset = np.where(pulsed, t.pulse_onset_frame.fillna(0).to_numpy() - 1, -1).astype(int)
    n_frames = np.where(pulsed, (t.pulse_offset_frame - t.pulse_onset_frame).fillna(0).to_numpy(), 0).astype(int)
    coherence = np.where(pulsed, t.pulse_coherence.to_numpy() / 100, np.nan)
    assert (n_frames[pulsed] > 0).all() and (onset[pulsed] >= 0).all() and np.isfinite(coherence[pulsed]).all()
    assert np.array_equal(np.sign(coherence[pulsed] - inputs["signed_coherence"][pulsed]), np.sign(inputs["sched_pulse_type"][pulsed]))

    worst_before, lag_off = 0.0, []
    for rig in np.unique(inputs["data_source"]):
        rows = np.flatnonzero(pulsed & (inputs["data_source"] == rig))
        component = inputs["signal"][rows] - inputs["signed_coherence"][rows, None] * inputs[f"onset_response_{rig}"][None, : inputs["signal"].shape[1]]
        peak_lag = int(np.argmax(inputs[f"pulse_response_{rig}"]))
        for c, o in zip(component, onset[rows]):
            worst_before = max(worst_before, float(np.abs(c[:o]).max()) if o > 0 else 0.0)
            if o + peak_lag < len(c):
                lag_off.append(int(np.argmax(np.abs(c[o:]))) - peak_lag)
    lag_off = np.array(lag_off)
    print(f"{pulsed.sum()} pulse trials; largest |pulse component| before onset {worst_before:.2e}; "
          f"peak at the response's peak lag in {np.mean(lag_off == 0):.3f} of trials (offsets {dict(zip(*np.unique(lag_off, return_counts=True)))})")

    out = processed / "ddm" / f"pulse_timing_{region}.npz"
    np.savez(out, agg_code=inputs["agg_code"], pulse_onset_frame0=onset, pulse_n_frames=n_frames, pulse_coherence=coherence)
    print(f"saved {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="global")
    main(parser.parse_args().region)
