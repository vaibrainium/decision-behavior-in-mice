"""Merge motion energy shards from compute_motion_energy_full.py and calibrate them per rig.

Raw ME scale depends on dot size and pixels per degree (UW is ~4x UCLA), so each rig and pooling
region is divided by the slope of mean ME vs nominal signed coherence, fitted on non-pulse
trials after the filters have warmed up. ME is then in equivalent-%-coherence units and
comparable across rigs (methods report, section 3.4). This replaces per-session max
normalization.

Outputs in <processed>:
- motion_energy_mouse/me_calibrated.npz: per region (global, center, Q1-Q4) a float32
  (n_trials, N_FRAMES) array in the row order of `agg_code`, plus rt_frame, data_source and the
  fitted slopes.
- motion_energies_normalized/me_{region}.pkl: {agg_code: array of PAD_LENGTH frames}, cut at
  rt_frame and NaN after it (what was actually shown) - the schema the analysis notebooks read.
- motion_energies_full/me_{region}.pkl: same, but not cut at the RT (frames the stimulus would
  have shown had the animal not responded yet), for the DDM.

Usage: python -m scripts.assemble_motion_energy
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.compute_motion_energy_full import convert_to_frame_units

REGIONS = ["global", "center", "Q1", "Q2", "Q3", "Q4"]
WARMUP_FRAMES = 9  # ~150 ms for the temporal filters to fill
PAD_LENGTH = 600  # frames per trial in the per-region pickles, as in the earlier pipeline


def save_region_dicts(out_dir, agg_codes, arrays, rt_frame=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    for region, array in arrays.items():
        padded = np.full((len(agg_codes), PAD_LENGTH), np.nan, dtype=np.float32)
        padded[:, : array.shape[1]] = array[:, :PAD_LENGTH]
        if rt_frame is not None:
            padded[np.arange(PAD_LENGTH)[None, :] >= rt_frame[:, None]] = np.nan
        with open(out_dir / f"me_{region.lower()}.pkl", "wb") as f:
            pickle.dump(dict(zip(agg_codes, padded)), f)


def load_shards(out_dir):
    me, params, n_frames = {}, None, None
    for path in sorted(out_dir.glob("me_shard_*.pkl")):
        with open(path, "rb") as f:
            shard = pickle.load(f)
        if params is not None and (shard["params"] != params or shard["n_frames"] != n_frames):
            raise ValueError(f"{path.name} was computed with different settings")
        params, n_frames = shard["params"], shard["n_frames"]
        me.update(shard["me"])
    return me, params, n_frames


def main():
    processed_dir = Path(dir_config.data.processed)
    out_dir = processed_dir / "motion_energy_mouse"
    me, params, n_frames = load_shards(out_dir)

    data = convert_to_frame_units(pd.read_csv(processed_dir / "valid_data.csv"))
    missing = ~data.agg_code.isin(me.keys())
    if missing.any():
        print(f"{missing.sum()} trials have no motion energy and are dropped: {data.agg_code[missing].tolist()[:10]}...")
    data = data[~missing].reset_index(drop=True)

    arrays = {region: np.stack([(me[c] if region in ("global", "center") else me[c]["quadrants"])[region] for c in data.agg_code]).astype(np.float32) for region in REGIONS}

    is_pulse = data.is_pulse_trial.to_numpy(bool)
    slopes = {}
    for rig in data.data_source.unique():
        fit_rows = (data.data_source == rig).to_numpy() & ~is_pulse
        coherence = data.signed_coherence.to_numpy(float)[fit_rows]
        for region in REGIONS:
            mean_me = arrays[region][fit_rows, WARMUP_FRAMES:].mean(axis=1)
            slope, intercept = np.polyfit(coherence, mean_me, 1)
            slopes[f"{rig}_{region}"] = slope
            arrays[region][(data.data_source == rig).to_numpy()] /= slope
            if region == "global":
                print(f"{rig}: slope {slope:.4g} raw ME per % coherence, intercept {intercept / slope:+.2f} % coherence")

    # sanity check: calibrated mean ME per nominal coherence should be close to the coherence itself
    summary = pd.DataFrame({"data_source": data.data_source, "coherence": data.signed_coherence, "me": arrays["global"][:, WARMUP_FRAMES:].mean(axis=1)})[~is_pulse]
    print(summary.groupby(["data_source", "coherence"]).me.mean().unstack(0).round(1))

    np.savez(
        out_dir / "me_calibrated.npz",
        agg_code=data.agg_code.to_numpy(str),
        data_source=data.data_source.to_numpy(str),
        rt_frame=data.rt_frame.to_numpy(int),
        slope_keys=np.array(list(slopes)),
        slope_values=np.array(list(slopes.values())),
        params=np.array(repr(params)),
        n_frames=n_frames,
        **arrays,
    )
    print(f"saved {len(data)} trials x {n_frames} frames -> {out_dir / 'me_calibrated.npz'}")

    agg_codes = data.agg_code.tolist()
    save_region_dicts(processed_dir / "motion_energies_normalized", agg_codes, arrays, rt_frame=data.rt_frame.to_numpy(int))
    save_region_dicts(processed_dir / "motion_energies_full", agg_codes, arrays)
    print(f"saved per-region pickles -> {processed_dir / 'motion_energies_normalized'} (cut at RT), {processed_dir / 'motion_energies_full'} (uncut)")


if __name__ == "__main__":
    main()
