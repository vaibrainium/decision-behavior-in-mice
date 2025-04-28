import gc
import logging
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import torch
from torch.nn import functional as F

from config import dir_config
from scripts.motion_energy import create_motion_energy_filters_from_degrees

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Directories
raw_dir = Path(dir_config.data.raw)
processed_dir = Path(dir_config.data.processed)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Stimulus files
missing_keys = []
stimuli_dir = Path(processed_dir) / "stimuli_arrays"
stimulus_files = sorted(stimuli_dir.glob("stimulus_*.pt"))
stimulus_files_indices = [int(f.stem.split("_")[1]) for f in stimulus_files]
stimulus_files_to_process = [f for f in stimulus_files if int(f.stem.split("_")[1]) in list(missing_keys)]

# Output directory
output_dir = Path(processed_dir) / "motion_energy_arrays"
output_dir.mkdir(parents=True, exist_ok=True)

# Motion energy filter settings
ppd = 10  # Pixels per degree
x_range_deg = (-6, 6)
y_range_deg = (-6, 6)
dx = 1.0 / ppd
dy = 1.0 / ppd
dt = 1 / 60  # 60 FPS
t_range_s = (0, 0.1)

# Create filters
right_filters, left_filters, (x, y, t) = create_motion_energy_filters_from_degrees(
	rf_size_deg=8.0,
	surround_width_deg=4.0,
	temporal_tuning_hz=5.0,
	x_range_deg=x_range_deg,
	y_range_deg=y_range_deg,
	t_range_s=t_range_s,
	dx=dx,
	dy=dy,
	dt=dt,
	device=device,
)

right_filters_tensor = [f.unsqueeze(0).unsqueeze(0) for f in right_filters]
left_filters_tensor = [f.unsqueeze(0).unsqueeze(0) for f in left_filters]
all_filters = right_filters_tensor[:2] + left_filters_tensor[:2]
filters_tensor = torch.cat(all_filters, dim=0).to(device)


# Function to calculate motion energy
def calculate_ME(stimulus_array, filters_tensor, device="cuda"):
	stimulus_tensor = stimulus_array.unsqueeze(0).unsqueeze(0).float().to(device)
	_, _, kD, kH, kW = filters_tensor.shape
	pad = (kW // 2, kW // 2, kH // 2, kH // 2, kD // 2, kD // 2)
	stimulus_padded = F.pad(stimulus_tensor, pad)
	conv_out = F.conv3d(stimulus_padded, filters_tensor, padding=0)
	conv_out_sq = conv_out**2
	ME = conv_out_sq[0, 0] + conv_out_sq[0, 1] - conv_out_sq[0, 2] - conv_out_sq[0, 3]
	return ME


# Custom Dataset
class StimulusDataset:
	def __init__(self, stimulus_files, filters_tensor, device):
		self.stimulus_files = stimulus_files
		self.filters_tensor = filters_tensor
		self.device = device

	def __len__(self):
		return len(self.stimulus_files)

	def __getitem__(self, idx):
		stimulus_file = self.stimulus_files[idx]
		agg_index = int(stimulus_file.stem.split("_")[1])
		try:
			stimulus_array = torch.load(stimulus_file).float().to(self.device)
		except Exception as e:
			print(f"Error loading {stimulus_file}: {e}")
			return None, None
		ME = calculate_ME(stimulus_array, self.filters_tensor)
		return agg_index, ME


# Save function
def save_motion_energy(agg_index, me_array, output_dir):
	save_path = output_dir / f"me_array_{agg_index:05d}.pt"
	torch.save(me_array, save_path)


# Example usage
dataset = StimulusDataset(stimulus_files_to_process, filters_tensor, device)

with ThreadPoolExecutor(max_workers=8) as executor:
	futures = []
	completed = 0

	for i in range(len(dataset)):
		agg_index, me_array = dataset[i]
		if agg_index is None or me_array is None:
			continue
		me_array = me_array.cpu()
		futures.append(executor.submit(save_motion_energy, agg_index, me_array, output_dir))

	for future in as_completed(futures):
		future.result()
		completed += 1
		if completed % 100 == 0:
			print(f"Processed {completed} files...")


# Function to load motion data
def load_motion(filepath):
	try:
		motion_energy = torch.load(filepath)
		_, h, w = motion_energy.shape
		h_half = h // 2
		w_half = w // 2

		h_start_c = (h - h_half) // 2
		h_end_c = h_start_c + h_half
		w_start_c = (w - w_half) // 2
		w_end_c = w_start_c + w_half

		me_global = motion_energy.mean(dim=(1, 2))
		me_center = motion_energy[:, h_start_c:h_end_c, w_start_c:w_end_c].mean(dim=(1, 2))
		me_first_quadrant = motion_energy[:, 0:h_half, 0:w_half].mean(dim=(1, 2))
		me_second_quadrant = motion_energy[:, 0:h_half, w_half:w].mean(dim=(1, 2))
		me_third_quadrant = motion_energy[:, h_half:h, 0:w_half].mean(dim=(1, 2))
		me_fourth_quadrant = motion_energy[:, h_half:h, w_half:w].mean(dim=(1, 2))

		return {
			"global": me_global,
			"center": me_center,
			"quadrants": {
				"Q1": me_first_quadrant,
				"Q2": me_second_quadrant,
				"Q3": me_third_quadrant,
				"Q4": me_fourth_quadrant,
			},
		}
	except Exception as e:
		logger.error(f"Failed to process {filepath}: {e}")
		return None


# Batch processing helper
def process_batch(batch_files):
	motion_data_list = []
	for file in batch_files:
		data = load_motion(file)
		if data is not None:
			motion_data_list.append(data)
	return motion_data_list


# Main motion processing function
def process_motion_files(processed_dir, save_every=100):
	motion_energy_dir = Path(processed_dir) / "motion_energy_arrays"
	motion_files = sorted(motion_energy_dir.glob("*.pt"))

	motion_data_dict = {}
	files_to_delete = []
	processed_count = 0

	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	base_filename = processed_dir / f"motion_data_dict_{timestamp}"

	for idx, motion_file in enumerate(motion_files, 1):
		try:
			file_stem = motion_file.stem
			file_idx = int(file_stem.replace("me_array_", ""))
			data = load_motion(motion_file)
			motion_data_dict[file_idx] = data
			files_to_delete.append(motion_file)
		except ValueError as e:
			print(f"❌ Failed to extract file index from {motion_file.stem}: {e}")
			continue
		except Exception as e:
			print(f"❌ Failed to load file {motion_file}: {e}")
			continue

		del data
		torch.cuda.empty_cache()
		gc.collect()

		if idx % 100 == 0 or idx == len(motion_files):
			print(f"📥 Processed {idx}/{len(motion_files)} files")

		if idx % save_every == 0 or idx == len(motion_files):
			checkpoint_filename = f"{base_filename}_part_{(idx // save_every)}.pkl"
			with open(checkpoint_filename, "wb") as f:
				pickle.dump(motion_data_dict, f)
			print(f"✅ Saved checkpoint: {checkpoint_filename}")

			for file in files_to_delete:
				try:
					file.unlink()
					print(f"🗑️ Deleted file: {file}")
				except Exception as e_del:
					print(f"❌ Failed to delete file {file}: {e_del}")

			motion_data_dict.clear()
			files_to_delete.clear()

		processed_count += 1


# Run
process_motion_files(processed_dir, save_every=100)
