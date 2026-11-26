"""Build the prespecified choice--RT Pareto refit task table.

The existing pulse-only normalized UGM/no-sv model has RT weight 1.  This
table adds RT weights .5, .25, .125 and 0, equivalent (up to a positive
objective rescaling) to relative choice weights 2, 4, 8 and a choice-only
endpoint.  Every task is warm-started from the corresponding weight-1 fit.

This script only writes a task table.  It never submits jobs.
"""
from __future__ import annotations

import argparse
import math
import pickle
from pathlib import Path

import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import build_grid, load_inputs


DDM = Path(dir_config.data.processed) / "ddm"
OUTPUT = Path("scripts/slurm/tasks_2026-11-26_choice_weight.csv")
VARIANT = "L1U1V0Z0G1"
SPLITS = ["pcv0", "pcv1", "pcv2", "pcv3", "pcv4", "pulse"]
WEIGHTS = [
    ("CW2_norm_ugm", 0.5, "fits_pulse_norm_ugm_choice_w2"),
    ("CW4_norm_ugm", 0.25, "fits_pulse_norm_ugm_choice_w4"),
    ("CW8_norm_ugm", 0.125, "fits_pulse_norm_ugm_choice_w8"),
    ("CWonly_norm_ugm", 0.0, "fits_pulse_norm_ugm_choice_only"),
]
BASE_ARGS = (
    "--responded_only --guess_model fast_only "
    "--inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --n_reps 15 "
    "--ugm --front_end norm --warm_start_from ddm/fits_pulse_norm_ugm "
    f"--variants {VARIANT} --splits {' '.join(SPLITS)}"
)


def limit(hours: float) -> float:
    """Match the established autosubmit first-pass policy."""
    return min(16.0, max(1.0, math.ceil((hours * 1.5 + 0.25) * 2) / 2))


def baseline_hours() -> pd.Series:
    rows = []
    for p in (DDM / "fits_pulse_norm_ugm").glob(f"*_{VARIANT}_*.pkl"):
        with p.open("rb") as f:
            r = pickle.load(f)
        if r["split"] in SPLITS:
            assert r["likelihood_params"]["rt_nllh_weight"] == 1.0
            rows.append({"mouse": r["mouse"], "variant": r["variant"], "split": r["split"],
                         "hours": r["fit_seconds"] / 3600})
    frame = pd.DataFrame(rows)
    assert len(frame) == 60 and not frame.duplicated(["mouse", "variant", "split"]).any()
    return frame.set_index(["mouse", "variant", "split"]).hours


def build() -> pd.DataFrame:
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    baseline = baseline_hours()
    jobs = build_grid(inputs, [VARIANT], SPLITS)
    assert len(jobs) == 60
    rows = []
    for priority, (batch, rt_weight, folder) in enumerate(WEIGHTS):
        args = f"{BASE_ARGS} --rt_nllh_weight {rt_weight:g} --out_dir ddm/{folder}"
        for index, job in enumerate(jobs):
            hours = float(baseline[(job["mouse"], job["variant"], job["split"])])
            rows.append({
                "batch": batch, "priority": priority, "index": index, **job,
                "out": f"ddm/{folder}/{job['mouse']}_{job['variant']}_{job['split']}.pkl",
                "est_hours": round(hours, 2), "time_hours": limit(hours), "args": args,
                "rt_nllh_weight": rt_weight,
            })
    frame = pd.DataFrame(rows)
    assert len(frame) == 240
    assert frame.groupby("batch").size().eq(60).all()
    assert not frame.duplicated(["batch", "index"]).any()
    assert frame.out.is_unique
    return frame


def main() -> None:
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--check", action="store_true", help="validate and summarize without writing")
    a = p.parse_args()
    frame = build()
    print(frame.groupby(["batch", "rt_nllh_weight", "time_hours"]).size().to_string())
    print(f"\n{len(frame)} tasks; estimated baseline-equivalent compute {frame.est_hours.sum():.1f} h")
    if a.check:
        return
    if a.output.exists():
        raise FileExistsError(f"refusing to overwrite {a.output}")
    frame.to_csv(a.output, index=False)
    print(f"wrote {a.output}")


if __name__ == "__main__":
    main()
