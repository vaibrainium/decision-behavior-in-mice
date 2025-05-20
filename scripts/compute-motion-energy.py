import gc
import pickle
from pathlib import Path
from threading import Lock

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from notebooks.imports import *
from scripts.motion_energy import create_motion_energy_filters_from_degrees, get_stimulus_array_ucla, get_stimulus_array_uw
from scripts.ucla_rdk import DotMotionStim as RDK_ucla
from scripts.uw_rdk import RandomDotMotion as RDK_uw

# Global Locks
save_lock = Lock()
progress_lock = Lock()


def convert_to_frame_units(data):
    frame_conversion = 1000 / 16.67
    data["pulse_onset_frame"] = np.round(data.pulse_onset * frame_conversion) + 1
    data["pulse_offset_frame"] = data.pulse_onset_frame + np.round(data.pulse_duration * frame_conversion)
    data["rt_frame"] = np.ceil(data.reaction_time * frame_conversion) + 1
    return data


def prepare_data(data):
    data = convert_to_frame_units(data)
    rows = data.to_dict(orient="records")

    stimuli_dir = Path(processed_dir) / "stimuli_arrays"
    existing_files = {int(f.stem.split("_")[1]) for f in stimuli_dir.glob("stimulus_*.pt")}
    rows_to_process = [row for row in rows if int(row["agg_code"]) not in existing_files]

    print(f"Number of stimuli to process: {len(rows_to_process)}")
    return rows_to_process


def batched(iterable, batch_size):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def create_stim_array(row, rdk_ucla, rdk_uw):
    try:
        pars = {
            "seed": row["stimulus_seed"],
            "coherence": row["signed_coherence"]
        }

        if row["pulse_onset_frame"] and row["pulse_offset_frame"]:
            pars["pulse"] = [
                (safe_int(row["pulse_onset_frame"]), row["pulse_coherence"]),
                (safe_int(row["pulse_offset_frame"]), row["signed_coherence"])
            ]

        rt_frame = safe_int(row["rt_frame"])

        if row["data_source"] == "ucla":
            array, _ = get_stimulus_array_ucla(
                screen_resolution_ucla, rdk_ucla, pars, rt_frame, ppd=ppd_ucla, convert_to_degrees=True, return_coords=True
            )
        else:
            array, _ = get_stimulus_array_uw(
                screen_resolution_uw, rdk_uw, pars, rt_frame, ppd=ppd_uw, convert_to_degrees=True, return_coords=True
            )

        return array
    except Exception as e:
        print(f"[{row['agg_code']}] Stimulus error: {e}")
        return None


def prepare_motion_filters(device):
    dx = dy = 1.0 / 10
    dt = 1 / 60
    t_range_s = (0, 0.1)

    right, left, _ = create_motion_energy_filters_from_degrees(
        rf_size_deg=8.0, surround_width_deg=4.0, temporal_tuning_hz=5.0,
        x_range_deg=(-6, 6), y_range_deg=(-6, 6), t_range_s=t_range_s,
        dx=dx, dy=dy, dt=dt, device=device
    )

    filters = [f.unsqueeze(0).unsqueeze(0) for f in right[:2] + left[:2]]
    return torch.cat(filters, dim=0).to(device)


def calculate_ME(array, filters, device):
    tensor = torch.from_numpy(array).unsqueeze(0).unsqueeze(0).float().to(device)
    pad = tuple((s // 2,) * 2 for s in filters.shape[-3:])
    pad = tuple(p for pair in reversed(pad) for p in pair)  # Flatten tuple
    conv_out = F.conv3d(F.pad(tensor, pad), filters)
    energy = conv_out ** 2
    return energy[0, 0] + energy[0, 1] - energy[0, 2] - energy[0, 3]


def calculate_motion_dict(me):
    _, h, w = me.shape
    half_h, half_w = h // 2, w // 2

    return {
        "global": me.mean(dim=(1, 2)),
        "center": me[:, h//4:3*h//4, w//4:3*w//4].mean(dim=(1, 2)),
        "quadrants": {
            "Q1": me[:, :half_h, :half_w].mean(dim=(1, 2)),
            "Q2": me[:, :half_h, half_w:].mean(dim=(1, 2)),
            "Q3": me[:, half_h:, :half_w].mean(dim=(1, 2)),
            "Q4": me[:, half_h:, half_w:].mean(dim=(1, 2))
        }
    }


def main_process(queued_data):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    stimulus_arrays_dir = Path(processed_dir / "stimulus_arrays")
    stimulus_arrays_dir.mkdir(parents=True, exist_ok=True)

    motion_dict_dir = Path(processed_dir / "motion_data_dict")
    motion_dict_dir.mkdir(parents=True, exist_ok=True)

    data = prepare_data(queued_data)
    rdk_ucla = RDK_ucla()
    rdk_uw = RDK_uw()
    filters = prepare_motion_filters(device)

    for batch_index, batch in enumerate(batched(data, 100)):
        for row in batch:
            agg_code = str(row["agg_code"])
            array = create_stim_array(row, rdk_ucla, rdk_uw)
            if array is None:
                continue

            tensor = torch.from_numpy(array)
            me = calculate_ME(array, filters, device)
            motion_data = calculate_motion_dict(me)

            with save_lock:
                torch.save(tensor, stimulus_arrays_dir / f"stimulus_{agg_code}.pt")
                with open(motion_dict_dir / f"me_array_{agg_code}.pkl", "wb") as f:
                    pickle.dump(motion_data, f)

        print(f"Processed batch {batch_index + 1}/{(len(data) + 99) // 100}")
        torch.cuda.empty_cache()
        gc.collect()


if __name__ == "__main__":
    from config import dir_config

    raw_dir = Path(dir_config.data.raw)
    processed_dir = Path(dir_config.data.processed)

    screen_resolution_uw = (1280, 720)
    screen_resolution_ucla = (1920, 1080)
    ppd_uw = 10
    ppd_ucla = 20

    data = pd.read_csv(Path(processed_dir, "valid_data.csv"))

    main_process(data)
