"""Regenerate per-trial motion energy for the current valid_data.csv, keyed by agg_code.

Uses the mouse-tuned, causal, separable motion energy from scripts/motion_energy.py
(MOUSE_ME_PARAMS; see dissemination/reports/motion-energy-methods.md, section 3). Every trial is
replayed for N_FRAMES (5 s), past the observed RT, so the DDM can simulate responses later than
the animal's; cut at rt_frame for anything that should only see what was shown.

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
then calibrate and assemble with scripts/assemble_motion_energy.py.
"""

import argparse
import pickle
import time
from multiprocessing import Process, Queue
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from config import dir_config
from scripts.motion_energy import MOUSE_ME_PARAMS, compute_mouse_me, mouse_me_kernels_torch, pool_mouse_me, render_stimulus_deg
from scripts.ucla_rdk import DotMotionStim as RDK_ucla
from scripts.uw_rdk import RandomDotMotion as RDK_uw

PPD = {"ucla": 20, "uw": 10}
N_FRAMES = 300  # 5 s at 60 Hz, the longest RT
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
        onset, offset = row.get("pulse_onset_frame"), row.get("pulse_offset_frame")
        if pd.notna(onset) and pd.notna(offset) and offset > onset:
            pars["pulse"] = [(safe_int(onset), row["pulse_coherence"]), (safe_int(offset), row["signed_coherence"])]
        elif pd.notna(onset):
            print(f"[{row['agg_code']}] invalid pulse offset ({offset} after onset {onset}); replaying without pulse")

        rdk = rdk_ucla if row["data_source"] == "ucla" else rdk_uw
        return row["agg_code"], render_stimulus_deg(row["data_source"], rdk, pars, N_FRAMES, PPD[row["data_source"]])
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


def save_shard(path, results):
    with open(path, "wb") as f:
        pickle.dump({"params": MOUSE_ME_PARAMS, "n_frames": N_FRAMES, "me": results}, f)


def main(gpu_id, shard, num_shards, num_workers, checkpoint_every, limit=None, queue_maxsize=None, trials="valid_data.csv", out_name="motion_energy_mouse"):
    processed_dir = Path(dir_config.data.processed)
    out_dir = processed_dir / out_name
    out_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(processed_dir / trials)
    data = convert_to_frame_units(data)
    rows = data.to_dict(orient="records")
    rows = rows[shard::num_shards]
    if limit is not None:
        rows = rows[:limit]
    total = len(rows)
    print(f"[shard {shard}/{num_shards} gpu {gpu_id}] {total} trials queued", flush=True)

    device = torch.device(f"cuda:{gpu_id}")
    kernels = mouse_me_kernels_torch(device)

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
            me = compute_mouse_me(torch.from_numpy(array).to(device), kernels)
            pooled = pool_mouse_me(me)
            results[agg_code] = {
                "global": pooled["global"].cpu().numpy(),
                "center": pooled["center"].cpu().numpy(),
                "quadrants": {q: v.cpu().numpy() for q, v in pooled["quadrants"].items()},
            }
            del me

        if i % checkpoint_every == 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            eta = (total - i) / rate if rate > 0 else float("nan")
            print(f"[shard {shard}] {i}/{total} ({rate:.2f} trials/s, ETA {eta / 60:.1f} min)", flush=True)
            save_shard(out_dir / f"me_shard_{shard}.pkl", results)

    for w in workers:
        w.join()

    save_shard(out_dir / f"me_shard_{shard}.pkl", results)
    print(f"[shard {shard}] done: {len(results)}/{total} trials -> {out_dir / f'me_shard_{shard}.pkl'}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--num-workers", type=int, default=15)
    parser.add_argument("--checkpoint-every", type=int, default=500)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--trials", default="valid_data.csv", help="trial table (relative to the processed data directory)")
    parser.add_argument("--out-dir", default="motion_energy_mouse", help="output directory (relative to the processed data directory)")
    args = parser.parse_args()
    main(args.gpu, args.shard, args.num_shards, args.num_workers, args.checkpoint_every, args.limit, trials=args.trials, out_name=args.out_dir)
