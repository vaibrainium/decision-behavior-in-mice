import pickle
from pathlib import Path

import pandas as pd

from config import dir_config
from src.models.ddm.full_ddm import *

raw_dir = Path(dir_config.data.raw)
processed_dir = Path(dir_config.data.processed)

ME_TYPE = "global"
ENABLE_LEAK = True
ENABLE_TIME_DEPENDENCY = True
model_folder = f"ddm_fits_{ME_TYPE}_{'leak' if ENABLE_LEAK else 'no_leak'}_{'time_dep' if ENABLE_TIME_DEPENDENCY else 'no_time_dep'}"
output_dir = processed_dir / "ddm_fits" / model_folder
output_dir.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    data = pd.read_csv(Path(processed_dir, "valid_data.csv"), index_col=None)
    data.reaction_time = (data.reaction_time * 1000).astype(int)
    data = data[data.reaction_time < 5000]

    with open(Path(processed_dir, f"motion_energies_normalized/me_{ME_TYPE}.pkl"), "rb") as f:
        motion_energy_dict = pickle.load(f)

    # filter motion data as well
    valid_keys = set(data.agg_code.values)
    motion_energy_dict = {k: v for k, v in motion_energy_dict.items() if k in valid_keys}
    motion_energy_array = np.array([motion_energy_dict[k] for k in data.agg_code.values])

    assert len(motion_energy_array) == len(data), f"Length mismatch: {len(motion_energy_array)} vs {len(data)}"
