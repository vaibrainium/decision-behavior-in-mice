import gc
import os
import pickle
from pathlib import Path
from threading import Lock

import numpy as np
import pandas as pd
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn.functional as F

from notebooks.imports import *
from scripts.motion_energy import create_motion_energy_filters_from_degrees, get_stimulus_array_ucla, get_stimulus_array_uw
from scripts.ucla_rdk import DotMotionStim as RDK_ucla
from scripts.uw_rdk import RandomDotMotion as RDK_uw

# Global Locks (reserved for thread-safe operations)
save_lock = Lock()
progress_lock = Lock()

# Distributed training environment variables
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "12365"


def convert_to_frame_units(data):
	frame_conversion = 1000 / 16.67
	data["pulse_onset_frame"] = np.round(data.pulse_onset * frame_conversion) + 1
	data["pulse_offset_frame"] = data.pulse_onset_frame + np.round(data.pulse_duration * frame_conversion)
	data["rt_frame"] = np.ceil(data.reaction_time * frame_conversion) + 1
	return data


def prepare_data(data, processed_dir):
	data = convert_to_frame_units(data)
	rows = data.to_dict(orient="records")

	stimuli_dir = Path(processed_dir) / "stimulus_arrays"
	stimuli_dir.mkdir(parents=True, exist_ok=True)

	# Collect existing agg_codes as strings to skip
	existing_files = {f.stem.split("_", 1)[1] for f in stimuli_dir.glob("stimulus_*.pt")}
	rows_to_process = [row for row in rows if str(row["agg_code"]) not in existing_files]

	print(f"Number of stimuli to process: {len(rows_to_process)}")
	return rows_to_process


def batched(iterable, batch_size):
	for i in range(0, len(iterable), batch_size):
		yield iterable[i : i + batch_size]


def safe_int(val, default=0):
	try:
		return int(val)
	except (ValueError, TypeError):
		return default


def create_stim_array(row, rdk_ucla, rdk_uw, screen_resolution_ucla, screen_resolution_uw, ppd_ucla, ppd_uw):
	try:
		pars = {"seed": row["stimulus_seed"], "coherence": row["signed_coherence"]}

		if pd.notna(row.get("pulse_onset_frame")) and pd.notna(row.get("pulse_offset_frame")):
			pars["pulse"] = [(safe_int(row["pulse_onset_frame"]), row["pulse_coherence"]), (safe_int(row["pulse_offset_frame"]), row["signed_coherence"])]

		rt_frame = safe_int(row.get("rt_frame", 0))

		if row["data_source"] == "ucla":
			array, _ = get_stimulus_array_ucla(screen_resolution_ucla, rdk_ucla, pars, rt_frame, ppd=ppd_ucla, convert_to_degrees=True, return_coords=True)
		else:
			array, _ = get_stimulus_array_uw(screen_resolution_uw, rdk_uw, pars, rt_frame, ppd=ppd_uw, convert_to_degrees=True, return_coords=True)

		return array
	except Exception as e:
		print(f"[{row['agg_code']}] Stimulus error: {e}")
		return None


def prepare_motion_filters(device):
	dx = dy = 1.0 / 10
	dt = 1 / 60
	t_range_s = (0, 0.1)

	right, left, _ = create_motion_energy_filters_from_degrees(rf_size_deg=8.0, surround_width_deg=4.0, temporal_tuning_hz=5.0, x_range_deg=(-6, 6), y_range_deg=(-6, 6), t_range_s=t_range_s, dx=dx, dy=dy, dt=dt, device=device)

	filters = [f.unsqueeze(0).unsqueeze(0) for f in right[:2] + left[:2]]
	return torch.cat(filters, dim=0).to(device)


def calculate_ME(array, filters, device):
	tensor = torch.from_numpy(array).unsqueeze(0).unsqueeze(0).float().to(device)
	pad = tuple((s // 2,) * 2 for s in filters.shape[-3:])
	pad = tuple(p for pair in reversed(pad) for p in pair)
	conv_out = F.conv3d(F.pad(tensor, pad), filters)
	energy = conv_out**2
	return energy[0, 0] + energy[0, 1] - energy[0, 2] - energy[0, 3]


def calculate_motion_dict(me):
	_, h, w = me.shape
	half_h, half_w = h // 2, w // 2

	return {
		"global": me.mean(dim=(1, 2)),
		"center": me[:, h // 4 : 3 * h // 4, w // 4 : 3 * w // 4].mean(dim=(1, 2)),
		"quadrants": {"Q1": me[:, :half_h, :half_w].mean(dim=(1, 2)), "Q2": me[:, :half_h, half_w:].mean(dim=(1, 2)), "Q3": me[:, half_h:, :half_w].mean(dim=(1, 2)), "Q4": me[:, half_h:, half_w:].mean(dim=(1, 2))},
	}


def main_worker(rank, world_size, prepared_data, processed_dir, screen_resolution_ucla, screen_resolution_uw, ppd_ucla, ppd_uw):
	dist.init_process_group("nccl", rank=rank, world_size=world_size)
	torch.cuda.set_device(rank)
	device = torch.device(f"cuda:{rank}")
	print(f"[GPU {rank}] Initialized.")

	stimulus_arrays_dir = Path(processed_dir) / "stimulus_arrays"
	motion_dict_dir = Path(processed_dir) / "motion_data_dict"
	stimulus_arrays_dir.mkdir(parents=True, exist_ok=True)
	motion_dict_dir.mkdir(parents=True, exist_ok=True)

	data_split = prepared_data[rank::world_size]

	rdk_ucla = RDK_ucla()
	rdk_uw = RDK_uw()
	filters = prepare_motion_filters(device)

	total = len(data_split)
	print_step = max(1, int(total * 0.00001))
	counter = 0

	for batch_index, batch in enumerate(batched(data_split, 100)):
		for row in batch:
			agg_code = str(row["agg_code"])
			array = create_stim_array(row, rdk_ucla, rdk_uw, screen_resolution_ucla, screen_resolution_uw, ppd_ucla, ppd_uw)
			if array is None:
				continue

			tensor = torch.from_numpy(array)
			me = calculate_ME(array, filters, device)
			motion_data = calculate_motion_dict(me)

			torch.save(tensor, stimulus_arrays_dir / f"stimulus_{agg_code}.pt")
			with open(motion_dict_dir / f"me_array_{agg_code}.pkl", "wb") as f:
				pickle.dump(motion_data, f)

			counter += 1
			if counter % print_step == 0 or counter == total:
				percent = (counter / total) * 100
				print(f"[GPU {rank}] Progress: {counter}/{total} ({percent:.5f}%)")

		torch.cuda.empty_cache()
		gc.collect()

	dist.destroy_process_group()


if __name__ == "__main__":
	from config import dir_config

	raw_dir = Path(dir_config.data.raw)
	processed_dir = Path(dir_config.data.processed)

	screen_resolution_uw = (1280, 720)
	screen_resolution_ucla = (1920, 1080)
	ppd_uw = 10
	ppd_ucla = 20

	data = pd.read_csv(Path(processed_dir, "valid_data.csv"))
	prepared_data = prepare_data(data, processed_dir)
	print(f"Prepared data: {len(prepared_data)} items.")

	available_gpus = torch.cuda.device_count()
	world_size = max(1, available_gpus // 1)

	if world_size > len(prepared_data):
		print(f"Warning: world_size ({world_size}) > number of data items ({len(prepared_data)}). Adjusting world_size.")
		world_size = len(prepared_data)

	mp.spawn(
		main_worker,
		args=(
			world_size,
			prepared_data,
			processed_dir,
			screen_resolution_ucla,
			screen_resolution_uw,
			ppd_ucla,
			ppd_uw,
		),
		nprocs=world_size,
		join=True,
	)
