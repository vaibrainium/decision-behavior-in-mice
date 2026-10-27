"""Calibration and power of the revised primacy analysis (primacy plan, amendment 6, item 6), on synthetic data.

For each (level, dataset, mouse): synthetic outcomes for the mouse's pulse trials, generated from its revised model
(control-only fit of the primary baseline + its all-trial pulse gain w_p from fit_pulse_gain) with the drift gain
decaying by `level` over the first 0.5 s (0 = null; gain_decay = -ln(1 - level) / 0.5). Then the whole revised
pipeline on those outcomes: cross-validated w_p fits, out-of-fold predictions (fit_pulse_gain.run_job), saved per job.
--summarize assembles the mice of each (level, dataset) and runs the gate and the timing GLMMs, then reports per level:
  - how often the gate passes;
  - the timing test's false-positive rate at level 0 (95% interval of b_middle excludes 0, either sign);
  - detection rates (interval entirely below 0, i.e. primacy) across all datasets and conditional on passing the gate;
  - the same for UW late pulses (b_late).
Caveat, by design of amendment 6: the control-only parameters are held at the real fits (they are not refitted to
synthetic control trials), as in the revised pipeline itself; a real decay would also act on control trials and could
be partly absorbed by those fits.

Usage:
    python -m scripts.ddm.primacy_calibration --list
    python -m scripts.ddm.primacy_calibration --job_id 5 [--fits_dir ddm/fits_final --gain_dir ddm/primacy_revised]
    python -m scripts.ddm.primacy_calibration --summarize [--levels 0 0.4]
"""

import argparse
import logging
import pickle
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm import fit_pulse_gain, primacy
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.ddm.model_recovery import synthesize
from scripts.ddm.primacy_sensitivity import gain_decay

logger = logging.getLogger(__name__)

LEVELS = [0.0, 0.1, 0.2, 0.4]
N_DATASETS = 20
DETECTION = 0.8
BASELINE = "primary"


def build_grid(inputs: dict) -> list[dict]:
    mice = sorted(np.unique(inputs["subject_id"]))
    return [{"level": lv, "dataset": d, "mouse": m} for lv in LEVELS for d in range(N_DATASETS) for m in mice]


def run_job(inputs: dict, job: dict, fits_dir: Path, gain_dir: Path, fit_reps: int, n_reps: int, responded: bool = False) -> dict:
    """`responded` (amendment 9): synthetic trials without a response by 5 s are dropped before the gain fits."""
    mouse = job["mouse"]
    variant = primacy.BASELINES[BASELINE]
    params = primacy.load_fit(fits_dir, mouse, variant, "control", None, responded=responded)["parameters"]
    with open(gain_dir / BASELINE / f"{mouse}.pkl", "rb") as f:
        gain = pickle.load(f)
    if bool(gain.get("responded_only", False)) != responded:
        raise ValueError(f"{gain_dir}: pulse gain responded_only={gain.get('responded_only')}, expected {responded}")
    w_true = gain["pulse_gain_all"]
    rows = primacy.pulse_rows(inputs, mouse)
    rig = np.unique(inputs["data_source"][rows]).item()
    seed = zlib.crc32(f"calib|{mouse}|{job['level']}|{job['dataset']}".encode())
    generator = primacy.make_model(variant, rig, time_varying_gain=True)
    synthetic = synthesize(generator, {**params, "noise_weight": w_true, "gain_decay": gain_decay(job["level"])},
                           primacy.gain_stimuli(inputs, rows), inputs["condition"][rows], seed)
    generator.simulator.clear_cache()
    observed = {"rt": synthetic["rt"], "choice": synthetic["choice"]}
    if responded:
        keep = observed["choice"] >= 0
        rows, observed = rows[keep], {k: v[keep] for k, v in observed.items()}
    t0 = time.time()
    res = fit_pulse_gain.run_job(inputs, BASELINE, mouse, fits_dir, fit_reps, n_reps, seed + 1, params=params, observed=observed, rows=rows, responded=responded)
    res.update(job=job, w_true=w_true, synthetic=observed, seconds=time.time() - t0)
    return res


def summarize(out_dir: Path, levels: list[float] | None, **kw) -> pd.DataFrame:
    jobs = {}
    for p in sorted(out_dir.glob("*.pkl")):
        with open(p, "rb") as f:
            r = pickle.load(f)
        if levels is None or r["job"]["level"] in levels:
            jobs.setdefault((r["job"]["level"], r["job"]["dataset"]), {})[r["mouse"]] = r
    rows = []
    n_mice = max(len(v) for v in jobs.values())
    for (level, dataset), preds in sorted(jobs.items()):
        if len(preds) < n_mice:
            logger.warning("level %.2f dataset %d: %d of %d mice, skipped", level, dataset, len(preds), n_mice)
            continue
        tables = {m: primacy.attach_observed(pr, pr["synthetic"]["rt"], pr["synthetic"]["choice"]) for m, pr in preds.items()}
        t = primacy.analysis_table(list(tables.values()))
        res = {"gate_departure": primacy.gate_departure(t, **kw), "gate_distributions": primacy.gate_distributions(preds, tables)}
        responded = {bool(pr.get("responded_only", False)) for pr in preds.values()}
        assert len(responded) == 1, f"level {level} dataset {dataset}: mixed responded_only"
        row = {"level": level, "dataset": dataset, "gate_pass": primacy.gate_pass(res, responded.pop()),
               "w_true_vs_fit_r": float(np.corrcoef([p["w_true"] for p in preds.values()], [p["pulse_gain_all"] for p in preds.values()])[0, 1])}
        for key, timings, name in [("primary", [1, 2], "middle"), ("uw_late", [1, 2, 3], "late")]:
            sub = t if key == "primary" else t[t.rig == "uw"]
            if len(sub):
                b = primacy.glmm(sub, timings, **kw)[f"b_{name}"]
                row.update({f"{key}_mean": b["mean"], f"{key}_excludes0": b["hi"] < 0 or b["lo"] > 0, f"{key}_primacy": b["hi"] < 0})
        rows.append(row)
        logger.info("level %.2f dataset %d: %s", level, dataset, row)
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / ("calibration_summary.csv" if levels is None else f"calibration_summary_levels{'_'.join(f'{lv:g}' for lv in levels)}.csv"), index=False)
    return df


def report(df: pd.DataFrame) -> None:
    print("gate pass rate by level:")
    print(df.groupby("level").gate_pass.mean().round(2).to_string())
    for key in ["primary", "uw_late"]:
        if f"{key}_excludes0" not in df:
            continue
        null = df[df.level == 0]
        print(f"\n{key}: false-positive rate at level 0 (interval excludes 0): {null[f'{key}_excludes0'].mean():.2f} of {len(null)}"
              f" (given gate pass: {null[null.gate_pass][f'{key}_excludes0'].mean():.2f} of {int(null.gate_pass.sum())})")
        tab = pd.DataFrame({"detected_all": df.groupby("level")[f"{key}_primacy"].mean(),
                            "detected_given_gate": df[df.gate_pass].groupby("level")[f"{key}_primacy"].mean(),
                            "n_gate_pass": df.groupby("level").gate_pass.sum(), "n": df.groupby("level").size(),
                            "mean_b": df.groupby("level")[f"{key}_mean"].mean()})
        print(tab.round(2).to_string())
        hit = tab.index[(tab.detected_all >= DETECTION) & (tab.index > 0)]
        print(f"smallest decay detected in >= {DETECTION:.0%} of all datasets: {hit.min() if len(hit) else 'none of ' + str(LEVELS[1:])}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz")
    parser.add_argument("--fits_dir", default="ddm/fits_final")
    parser.add_argument("--gain_dir", default="ddm/primacy_revised", help="real-data fit_pulse_gain output (the generating w_p)")
    parser.add_argument("--out_dir", default="ddm/primacy_calibration")
    parser.add_argument("--fit_reps", type=int, default=fit_pulse_gain.FIT_REPS)
    parser.add_argument("--n_reps", type=int, default=primacy.N_REPS)
    parser.add_argument("--job_id", type=int)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--levels", type=float, nargs="*", help="summarize only these levels (for parallel runs)")
    parser.add_argument("--report", action="store_true", help="report from the per-level summary files")
    parser.add_argument("--responded_only", action="store_true", help="amendment 9: responded trials only, conditional likelihood")
    parser.add_argument("--model_set", choices=list(primacy.MODEL_SETS), default="sv", help="amendment 12")
    args = parser.parse_args()
    primacy.use_model_set(args.model_set)

    processed = Path(dir_config.data.processed)
    out_dir = processed / args.out_dir
    if args.summarize:
        report(summarize(out_dir, args.levels, draws=500, tune=500))
    elif args.report:  # combine per-level summaries written by parallel --summarize --levels runs
        report(pd.concat([pd.read_csv(f) for f in sorted(out_dir.glob("calibration_summary_levels*.csv"))], ignore_index=True))
    else:
        inputs = load_inputs(processed / args.inputs)
        if args.responded_only:
            inputs = responded_only(inputs)
        grid = build_grid(inputs)
        if args.list:
            print(f"{len(grid)} jobs: {len(LEVELS)} levels x {N_DATASETS} datasets x {len(grid) // len(LEVELS) // N_DATASETS} mice; --array=0-{len(grid) - 1}")
        else:
            job = grid[args.job_id]
            out = out_dir / f"{job['mouse']}_lv{job['level']:.2f}_ds{job['dataset']:02d}.pkl"
            if out.exists():
                logger.info("skipping %s: output exists", job)
            else:
                res = run_job(inputs, job, processed / args.fits_dir, processed / args.gain_dir, args.fit_reps, args.n_reps, args.responded_only)
                out_dir.mkdir(parents=True, exist_ok=True)
                tmp = out.with_suffix(".tmp")
                with open(tmp, "wb") as f:
                    pickle.dump(res, f)
                tmp.replace(out)
                logger.info("saved %s (w_true %.2f, fitted %.2f; %.0f s)", out.name, res["w_true"], res["pulse_gain_all"], res["seconds"])
