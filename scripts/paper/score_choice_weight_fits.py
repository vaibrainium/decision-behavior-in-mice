"""Common-scale held-out scoring for the choice--RT Pareto refits.

Every stored weighted fit is simulated and scored with the original
``rt_nllh_weight=1`` likelihood.  The weighted training objectives are never
used for cross-weight model comparison.

Run after all 240 fits have synced::

  OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore \
    -m scripts.paper.score_choice_weight_fits --output <new directory>

``--check`` validates registrations, metadata and expected paths without
running simulations and can be used before submission.
"""
from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import pandas as pd

from config import dir_config
from scripts.ddm import pulse_joint_signatures as pjs


DDM = Path(dir_config.data.processed) / "ddm"
TASKS = Path("scripts/slurm/tasks_2026-11-26_choice_weight.csv")
VARIANT = "L1U1V0Z0G1"
FAMILIES = {
    "pulse_norm_ugm_choice_w2": ("fits_pulse_norm_ugm_choice_w2", VARIANT, 0.5),
    "pulse_norm_ugm_choice_w4": ("fits_pulse_norm_ugm_choice_w4", VARIANT, 0.25),
    "pulse_norm_ugm_choice_w8": ("fits_pulse_norm_ugm_choice_w8", VARIANT, 0.125),
    "pulse_norm_ugm_choice_only": ("fits_pulse_norm_ugm_choice_only", VARIANT, 0.0),
}
BASELINE = "pulse_norm_ugm_no_sv"


for family, (folder, variant, _) in FAMILIES.items():
    pjs.PULSE_ONLY_FAMILIES[family] = (folder, variant)
    pjs.OPTIONS[family] = {"ugm": True, "front_end": "norm"}


def validate(require_new: bool) -> pd.DataFrame:
    tasks = pd.read_csv(TASKS)
    assert len(tasks) == 240 and tasks.out.is_unique
    records = []
    for family, (folder, variant, expected_weight) in FAMILIES.items():
        expected = tasks[tasks.out.str.contains(f"/{folder}/", regex=False)]
        assert len(expected) == 60
        for row in expected.itertuples():
            path = DDM / folder / f"{row.mouse}_{variant}_{row.split}.pkl"
            if not path.exists():
                records.append({"family": family, "mouse": row.mouse, "split": row.split,
                                "path": str(path), "exists": False, "rt_nllh_weight": expected_weight})
                continue
            with path.open("rb") as stream:
                fit = pickle.load(stream)
            assert fit["mouse"] == row.mouse and fit["variant"] == variant and fit["split"] == row.split
            assert fit["front_end"] == "norm" and fit.get("ugm") and fit["guess_model"] == "fast_only"
            assert fit["likelihood_params"] == {
                "method": "qmle_censored", "nbins": 9,
                "rt_nllh_weight": expected_weight, "include_censored": False,
            }
            records.append({"family": family, "mouse": row.mouse, "split": row.split,
                            "path": str(path), "exists": True, "rt_nllh_weight": expected_weight})
    frame = pd.DataFrame(records)
    if require_new:
        missing = frame[~frame.exists]
        if len(missing):
            raise FileNotFoundError(f"{len(missing)} weighted fits are missing; first: {missing.path.iloc[0]}")
    # Existing weight-1 baseline: 10 mice x six pulse splits.
    base = list((DDM / "fits_pulse_norm_ugm").glob(f"*_{VARIANT}_*.pkl"))
    base = [p for p in base if p.stem.rsplit("_", 1)[-1] in {"pcv0", "pcv1", "pcv2", "pcv3", "pcv4", "pulse"}]
    assert len(base) == 60
    for path in base:
        with path.open("rb") as stream:
            fit = pickle.load(stream)
        assert fit["likelihood_params"]["rt_nllh_weight"] == 1.0
    return frame


def summarize(output: Path) -> None:
    summary = pd.read_csv(output / "heldout/summary.csv")
    weight = {BASELINE: 1.0, **{f: w for f, (_, _, w) in FAMILIES.items()}}
    summary["rt_nllh_weight_fit"] = summary.family.map(weight)
    summary["relative_choice_weight"] = summary.rt_nllh_weight_fit.map(
        lambda w: float("inf") if w == 0 else 1 / w
    )
    summary.to_csv(output / "pareto_scores_by_seed.csv", index=False)
    cells = pd.read_csv(output / "heldout/cells.csv.gz")
    per_mouse = cells.groupby(["family", "seed", "mouse"], as_index=False).agg(
        choice_nll=("choice_nll", "sum"), rt_nll=("rt_nll", "sum"),
        penalty=("penalty", "sum"), saturated_choice_nll=("saturated_choice_nll", "sum"),
        n=("n", "sum"),
    )
    per_mouse["joint_nll"] = per_mouse.choice_nll + per_mouse.rt_nll + per_mouse.penalty
    per_mouse["choice_deviance"] = 2 * (per_mouse.choice_nll - per_mouse.saturated_choice_nll)
    per_mouse["rt_nllh_weight_fit"] = per_mouse.family.map(weight)
    per_mouse.to_csv(output / "pareto_scores_by_mouse_seed.csv", index=False)
    group = summary.groupby(["family", "rt_nllh_weight_fit", "relative_choice_weight"], as_index=False).agg(
        choice_nll=("choice_nll", "mean"), rt_nll=("rt_nll", "mean"),
        joint_nll=("total", "mean"), choice_deviance=("choice_deviance", "mean"),
        seed_sd_joint=("total", "std"), seeds=("seed", "nunique"), n=("n", "first"),
    )
    group.sort_values("rt_nllh_weight_fit", ascending=False).to_csv(output / "pareto_summary.csv", index=False)
    reproduction = pd.read_csv(output / "heldout/reproduction.csv")
    reproduction = reproduction.rename(columns={
        "stored": "stored_weighted_test_nll", "recomputed": "unweighted_test_nll"
    })
    reproduction["rt_nllh_weight_fit"] = reproduction.family.map(weight)
    reproduction["same_objective_as_stored"] = reproduction.rt_nllh_weight_fit.eq(1.0)
    reproduction.to_csv(output / "heldout/reproduction.csv", index=False)


def main() -> None:
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--output", type=Path)
    p.add_argument("--seeds", type=int, nargs="+", default=[12345, 23456, 34567, 45678, 56789])
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    state = validate(require_new=not a.check)
    print(state.groupby(["family", "exists"]).size().to_string())
    if a.check:
        return
    if a.output is None:
        p.error("--output is required unless --check is used")
    from scripts.paper.audit_pulse_choice_rt_score import run as run_heldout
    from scripts.paper.choice_g2_control_training import run as run_control
    a.output.mkdir(parents=True, exist_ok=False)
    families = [BASELINE, *FAMILIES]
    run_heldout(a.output / "heldout", families, a.seeds)
    run_control(a.output / "control", families, a.seeds)
    summarize(a.output)


if __name__ == "__main__":
    main()
