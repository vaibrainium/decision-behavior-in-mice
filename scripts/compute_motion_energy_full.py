"""Regenerate per-trial motion energy for the current valid_data.csv, keyed by agg_code.

Unlike compute-motion-energy.py / motion-energy-multi-gpu.py, this does NOT persist the
raw per-trial stimulus array (only the pooled global/center/quadrant time series are kept) -
the stimulus is generated, convolved with the motion-energy filters, pooled, and discarded
in the same step. Stimulus generation (CPU, cv2-bound) is parallelized across worker
processes per GPU shard; a bounded result queue (maxsize below) gives explicit backpressure
so producers block instead of piling up unconsumed stimulus arrays in memory if the GPU
consumer falls behind - this is what caused an OOM (host cgroup memory) in an earlier version
that used Pool.imap_unordered, whose internal result buffering has no such bound.

Usage: run once per GPU, in parallel, e.g.:
  python -m scripts.compute_motion_energy_full --gpu 0 --shard 0 --num-shards 2
  python -m scripts.compute_motion_energy_full --gpu 1 --shard 1 --num-shards 2
"""

import argparse
import pickle
import time
from multiprocessing import Process, Queue
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from config import dir_config
from scripts.motion_energy import create_motion_energy_filters_from_degrees, get_stimulus_array_ucla, get_stimulus_array_uw
from scripts.ucla_rdk import DotMotionStim as RDK_ucla
from scripts.uw_rdk import RandomDotMotion as RDK_uw

SCREEN_RESOLUTION = {"ucla": (1920, 1080), "uw": (1280, 720)}
PPD = {"ucla": 20, "uw": 10}
_STOP = "__STOP__"


def convert_to_frame_units(data):
    frame_conversion = 1000 / 16.67
    data["pulse_onset_frame"] = np.round(data.pulse_onset * frame_conversion) + 1
    data["pulse_offset_frame"] = data.pulse_onset_frame + np.round(data.pulse_duration * frame_conversion)
    data["rt_frame"] = np.ceil(data.reaction_time * frame_conversion) + 1
    return data


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _generate_stimulus(row, rdk_ucla, rdk_uw):
    try:
        pars = {"seed": row["stimulus_seed"], "coherence": row["signed_coherence"]}
        if pd.notna(row.get("pulse_onset_frame")) and pd.notna(row.get("pulse_offset_frame")):
            pars["pulse"] = [(safe_int(row["pulse_onset_frame"]), row["pulse_coherence"]), (safe_int(row["pulse_offset_frame"]), row["signed_coherence"])]

        rt_frame = safe_int(row.get("rt_frame", 0))
        if rt_frame <= 0:
            return row["agg_code"], None

        if row["data_source"] == "ucla":
            array = get_stimulus_array_ucla(SCREEN_RESOLUTION["ucla"], rdk_ucla, pars, rt_frame, ppd=PPD["ucla"], convert_to_degrees=True)
        else:
            array = get_stimulus_array_uw(SCREEN_RESOLUTION["uw"], rdk_uw, pars, rt_frame, ppd=PPD["uw"], convert_to_degrees=True)
        return row["agg_code"], array
    except Exception as e:
        print(f"[{row['agg_code']}] stimulus error: {e}")
        return row["agg_code"], None


def _worker_loop(rows, result_q):
    """Generates stimuli for `rows` and pushes them to the bounded result_q (blocks when full)."""
    rdk_ucla = RDK_ucla()
    rdk_uw = RDK_uw()
    for row in rows:
        result_q.put(_generate_stimulus(row, rdk_ucla, rdk_uw))
    result_q.put(_STOP)


def prepare_motion_filters(device):
    dx = dy = 1.0 / 10
    dt = 1 / 60
    right, left, _ = create_motion_energy_filters_from_degrees(
        rf_size_deg=8.0, surround_width_deg=4.0, temporal_tuning_hz=5.0, x_range_deg=(-6, 6), y_range_deg=(-6, 6), t_range_s=(0, 0.1), dx=dx, dy=dy, dt=dt, device=device
    )
    filters = [f.unsqueeze(0).unsqueeze(0) for f in right[:2] + left[:2]]
    return torch.cat(filters, dim=0).to(device)


def calculate_ME(array, filters, device):
    tensor = torch.from_numpy(array).unsqueeze(0).unsqueeze(0).float().to(device)
    pad = tuple((s // 2,) * 2 for s in filters.shape[-3:])
    pad = tuple(p for pair in reversed(pad) for p in pair)
    conv_out = F.conv3d(F.pad(tensor, pad), filters)
    energy = conv_out**2
    return energy[0, 0] + energy[0, 1] - energy[0, 2] - energy[0, 3]


def pool_me(me):
    _, h, w = me.shape
    half_h, half_w = h // 2, w // 2
    return {
        "global": me.mean(dim=(1, 2)).cpu(),
        "center": me[:, h // 4 : 3 * h // 4, w // 4 : 3 * w // 4].mean(dim=(1, 2)).cpu(),
        "quadrants": {
            "Q1": me[:, :half_h, :half_w].mean(dim=(1, 2)).cpu(),
            "Q2": me[:, :half_h, half_w:].mean(dim=(1, 2)).cpu(),
            "Q3": me[:, half_h:, :half_w].mean(dim=(1, 2)).cpu(),
            "Q4": me[:, half_h:, half_w:].mean(dim=(1, 2)).cpu(),
        },
    }


def main(gpu_id, shard, num_shards, num_workers, checkpoint_every, limit=None, queue_maxsize=None):
    processed_dir = Path(dir_config.data.processed)
    out_dir = processed_dir / "motion_data_dict"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(processed_dir / "valid_data.csv")
    data = convert_to_frame_units(data)
    rows = data.to_dict(orient="records")
    rows = rows[shard::num_shards]
    if limit is not None:
        rows = rows[:limit]
    total = len(rows)
    print(f"[shard {shard}/{num_shards} gpu {gpu_id}] {total} trials queued", flush=True)

    device = torch.device(f"cuda:{gpu_id}")
    filters = prepare_motion_filters(device)

    queue_maxsize = queue_maxsize or (2 * num_workers)
    result_q = Queue(maxsize=queue_maxsize)
    workers = [Process(target=_worker_loop, args=(rows[w::num_workers], result_q), daemon=True) for w in range(num_workers)]
    for w in workers:
        w.start()

    results = {}
    t0 = time.time()
    done_workers = 0
    i = 0
    while done_workers < num_workers:
        item = result_q.get()
        if item == _STOP:
            done_workers += 1
            continue
        agg_code, array = item
        i += 1
        if array is not None:
            me = calculate_ME(array, filters, device)
            results[agg_code] = pool_me(me)
            del me

        if i % checkpoint_every == 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            eta = (total - i) / rate if rate > 0 else float("nan")
            print(f"[shard {shard}] {i}/{total} ({rate:.2f} trials/s, ETA {eta / 60:.1f} min)", flush=True)
            with open(out_dir / f"me_shard_{shard}.pkl", "wb") as f:
                pickle.dump(results, f)

    for w in workers:
        w.join()

    with open(out_dir / f"me_shard_{shard}.pkl", "wb") as f:
        pickle.dump(results, f)
    print(f"[shard {shard}] done: {len(results)}/{total} trials -> {out_dir / f'me_shard_{shard}.pkl'}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--checkpoint-every", type=int, default=500)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    main(args.gpu, args.shard, args.num_shards, args.num_workers, args.checkpoint_every, args.limit)
