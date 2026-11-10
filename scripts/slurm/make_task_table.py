"""Task table for scripts/slurm/autosubmit.py: one row per array task (batch, index, mouse, variant, split, output file,
time limit), for the batches of plans/2026-11-06-input-mapping-x-accumulator.md and
plans/2026-11-06-nominal-coherence-joint-fits.md.

Indices come from fit_mouse_ddm.build_grid with each batch's variants and splits, so they are the --job_id the fit
script derives from the array index (JOB_OFFSET 0). Time limits are estimated from finished fits of the same mouse and
variant with the same likelihood and trials (motion-energy joint fits; control-only fits for P1): the slowest of that
mouse's splits, times the 90th-percentile slowdown measured for the input change (front end, nominal input), times
BUFFER, plus OVERHEAD, rounded up to the half hour, between MIN_HOURS and FIRST_MAX_HOURS. autosubmit doubles the
limit for a task that times out.

Run locally (needs the synced fits): python -m scripts.slurm.make_task_table
Writes scripts/slurm/tasks_<date>.csv (a new file per date).

--pulse / --pulse_lu: the pulse-only fits of plans/2026-11-10-pulse-only-fits.md (linear and power, with and without sv,
splits pcv0-pcv4 + pulse): primary and leak+urgency -> scripts/slurm/tasks_2026-11-10_pulse.csv (submitted; keep);
leak only and urgency only -> tasks_2026-11-10_pulse_lu.csv. Time limits (author 2026-11-10: 16 h only
for the fits that needed long before): a task whose earlier counterpart (same mouse, input mapping and accumulator, with
sv, joint fits, slowest split) took more than LONG_HOURS gets 16 h; the others get limit(that runtime).
"""

import datetime
import math
import pickle
from pathlib import Path

import pandas as pd

from config import dir_config
from scripts.ddm.fit_mouse_ddm import build_grid, load_inputs

DDM = Path(dir_config.data.processed) / "ddm"
BUFFER, OVERHEAD, MIN_HOURS, FIRST_MAX_HOURS = 1.5, 0.25, 1.0, 16.0
INTEGRATORS = ["L0U0V1Z0G1", "L1U0V1Z0G1", "L0U1V1Z0G1", "L1U1V1Z0G1"]
JOINT = ["cv0", "cv1", "cv2", "cv3", "cv4", "all"]
CONTROL = ["ccv0", "ccv1", "ccv2", "ccv3", "ccv4", "control"]
# 90th-percentile runtime ratio vs the same fit on linear motion energy, measured 2026-11-06 on the control-only fits:
# fe-norm / fast_only 8.30; nominal_matched C 1.77, E 2.26, ES 2.16. Power law: no finished fits; assumed 2.0 (one
# cheap extra parameter), the timeout retry covers it.
SLOWDOWN = {"norm": 8.3, "power": 2.0, "nominal": {"integrator": 1.77, "E": 2.26, "ES": 2.16}}
# analog: (folder of comparable finished fits, kind) per family
ANALOG = {"integrator": "fits_joint_unfreeze_integrators", "E": "fits_joint_unfreeze_leak20-200", "ES": "fits_joint_unfreeze_es"}

J = "--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --splits cv0 cv1 cv2 cv3 cv4 all --n_reps 15"
N = J + " --nominal_input --nominal_matched"
P = ("--responded_only --guess_model fast_only --front_end power --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control "
     "--inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --out_dir ddm/fits_resp_fast_only_fe-power_v2")
NOMINAL_INTEGRATORS = ["L0U0V1Z0G1", "L0U0V0Z0G1", "L1U0V1Z0G1", "L0U1V1Z0G1", "L1U1V1Z0G1"]
# name, priority (lower first), EXTRA_ARGS without --n_reps override handled per split, variants, splits, kind, slowdowns
BATCHES = [
    ("P1_power", 0, P, ["L0U0V1Z0G1"], CONTROL, "integrator", ["power"]),
    ("N4_nominal_power", 1, f"{N} --front_end power --variants L0U0V1Z0G1 --out_dir ddm/fits_joint_nominal_power", ["L0U0V1Z0G1"], JOINT, "integrator", ["nominal", "power"]),
    ("M_power_integrators", 2, f"{J} --front_end power --variants {' '.join(INTEGRATORS)} --out_dir ddm/fits_joint_power_integrators", INTEGRATORS, JOINT, "integrator", ["power"]),
    ("M_power_leak20-200", 2, f"{J} --front_end power --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_power_leak20-200", ["L1U0V1Z0G1"], JOINT, "E", ["power"]),
    ("M_power_es", 2, f"{J} --front_end power --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_power_es", ["L0U0V1Z0G1"], JOINT, "ES", ["power"]),
    ("M_norm_integrators", 3, f"{J} --front_end norm --variants {' '.join(INTEGRATORS)} --out_dir ddm/fits_joint_norm_integrators", INTEGRATORS, JOINT, "integrator", ["norm"]),
    ("M_norm_leak20-200", 3, f"{J} --front_end norm --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_norm_leak20-200", ["L1U0V1Z0G1"], JOINT, "E", ["norm"]),
    ("M_norm_es", 3, f"{J} --front_end norm --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_norm_es", ["L0U0V1Z0G1"], JOINT, "ES", ["norm"]),
    ("N1_nominal_integrators", 4, f"{N} --variants {' '.join(NOMINAL_INTEGRATORS)} --out_dir ddm/fits_joint_nominal_integrators", NOMINAL_INTEGRATORS, JOINT, "integrator", ["nominal"]),
    ("N2_nominal_leak20-200", 4, f"{N} --variants L1U0V1Z0G1 --leak_bounds 20 200 --out_dir ddm/fits_joint_nominal_leak20-200", ["L1U0V1Z0G1"], JOINT, "E", ["nominal"]),
    ("N3_nominal_es", 4, f"{N} --variants L0U0V1Z0G1 --extrema_samples --out_dir ddm/fits_joint_nominal_es", ["L0U0V1Z0G1"], JOINT, "ES", ["nominal"]),
]


def fit_hours(folder: str) -> pd.DataFrame:
    rows = []
    for p in (DDM / folder).glob("*.pkl"):
        with open(p, "rb") as f:
            r = pickle.load(f)
        rows.append({"mouse": r["mouse"], "variant": r["variant"], "split": r["split"], "hours": r["fit_seconds"] / 3600})
    return pd.DataFrame(rows)


def limit(hours: float) -> float:
    return min(FIRST_MAX_HOURS, max(MIN_HOURS, math.ceil((hours * BUFFER + OVERHEAD) * 2) / 2))


LONG_HOURS = 4.0
PULSE_SPLITS = ["pcv0", "pcv1", "pcv2", "pcv3", "pcv4", "pulse"]
# Two tables, each with its own autosubmit state: "pulse" (submitted 2026-11-10; do not change its variants or indices)
# and "pulse_lu" (leak only, urgency only; added by the author after the first table was running).
PULSE_TABLES = {
    "pulse": ("PO", ["L0U0V1Z0G1", "L0U0V0Z0G1", "L1U1V1Z0G1", "L1U1V0Z0G1"]),
    "pulse_lu": ("PLU", ["L1U0V1Z0G1", "L1U0V0Z0G1", "L0U1V1Z0G1", "L0U1V0Z0G1"]),
}
PJ = "--responded_only --guess_model fast_only --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --n_reps 15"


def pulse_batches(prefix, variants):
    """name, priority, args, folder of the earlier joint fits used for the runtime"""
    v, sp = " ".join(variants), " ".join(PULSE_SPLITS)
    return [(f"{prefix}_linear", 0, f"{PJ} --variants {v} --splits {sp} --out_dir ddm/fits_pulse_linear_integrators", "fits_joint_unfreeze_integrators"),
            (f"{prefix}_power", 0, f"{PJ} --front_end power --variants {v} --splits {sp} --out_dir ddm/fits_pulse_power_integrators", "fits_joint_power_integrators")]


def pulse_main(table):
    prefix, variants = PULSE_TABLES[table]
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    rows = []
    for name, prio, args, analog in pulse_batches(prefix, variants):
        prev = fit_hours(analog).groupby(["mouse", "variant"]).hours.max()
        out_dir = args.split("--out_dir ")[1].split()[0]
        for i, job in enumerate(build_grid(inputs, variants, PULSE_SPLITS)):
            with_sv = job["variant"].replace("V0", "V1")  # no-sv: the same accumulator with sv (slower; no power no-sv fits)
            base = prev[(job["mouse"], with_sv)]
            rows.append({"batch": name, "priority": prio, "index": i, **job, "out": f"{out_dir}/{job['mouse']}_{job['variant']}_{job['split']}.pkl",
                         "est_hours": round(base, 2), "time_hours": FIRST_MAX_HOURS if base > LONG_HOURS else limit(base), "args": args})
    df = pd.DataFrame(rows)
    out = Path(__file__).with_name(f"tasks_2026-11-10_{table}.csv")
    assert not out.exists(), f"{out} exists; not overwriting"
    df.to_csv(out, index=False)
    long = df[df.time_hours >= FIRST_MAX_HOURS].drop_duplicates(["batch", "mouse", "variant"])
    print(df.groupby(["batch", "time_hours"]).size().to_string())
    print("16 h:", ", ".join(f"{r.batch} {r.mouse} {r.variant} (before {r.est_hours} h)" for r in long.itertuples()))
    print(f"\n{len(df)} tasks -> {out}")


# Urgency-gating variant (plan 2026-11-10-ugm-corner-leak-urgency): fit_mouse_ddm --ugm on leak + urgency with and without
# sv, linear and power input, joint fits (cv0-cv4, all) and pulse-only fits (pcv0-pcv4, pulse) -> tasks_2026-11-10_ugm.csv
# (own autosubmit state). Runtime from the same mouse's joint L1U1V1Z0G1 fit with the same input (slowest split).
UGM_VARIANTS = ["L1U1V1Z0G1", "L1U1V0Z0G1"]
UGM_ARGS = PJ + " --ugm"


def ugm_batches():
    v = " ".join(UGM_VARIANTS)
    joint, pulse = ["cv0", "cv1", "cv2", "cv3", "cv4", "all"], PULSE_SPLITS
    out = []
    for mapping, fe, analog in [("linear", "", "fits_joint_unfreeze_integrators"), ("power", " --front_end power", "fits_joint_power_integrators")]:
        for kind, splits in [("joint", joint), ("pulse", pulse)]:
            out.append((f"UGM_{kind}_{mapping}", 0, f"{UGM_ARGS}{fe} --variants {v} --splits {' '.join(splits)} --out_dir ddm/fits_{kind}_{mapping}_ugm", splits, analog))
    return out


def ugm_main():
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    rows = []
    for name, prio, args, splits, analog in ugm_batches():
        prev = fit_hours(analog).groupby(["mouse", "variant"]).hours.max()
        out_dir = args.split("--out_dir ")[1].split()[0]
        for i, job in enumerate(build_grid(inputs, UGM_VARIANTS, splits)):
            base = prev[(job["mouse"], "L1U1V1Z0G1")]
            rows.append({"batch": name, "priority": prio, "index": i, **job, "out": f"{out_dir}/{job['mouse']}_{job['variant']}_{job['split']}.pkl",
                         "est_hours": round(base, 2), "time_hours": FIRST_MAX_HOURS if base > LONG_HOURS else limit(base), "args": args})
    df = pd.DataFrame(rows)
    out = Path(__file__).with_name("tasks_2026-11-10_ugm.csv")
    assert not out.exists(), f"{out} exists; not overwriting"
    df.to_csv(out, index=False)
    print(df.groupby(["batch", "time_hours"]).size().to_string())
    print(f"\n{len(df)} tasks -> {out}")


def main():
    import sys
    if "--ugm" in sys.argv:
        return ugm_main()
    for table in PULSE_TABLES:
        if f"--{table}" in sys.argv:
            return pulse_main(table)
    inputs = load_inputs(DDM / "ddm_inputs_global_ucla_nofreeze.npz")
    analogs = {kind: fit_hours(folder).groupby(["mouse", "variant"]).hours.max() for kind, folder in ANALOG.items()}
    ctl = fit_hours("fits_resp_fast_only").query("variant == 'L0U0V1Z0G1'").groupby("mouse").hours.max()  # 15 reps, ccv
    ctl50 = fit_hours("fits_resp_final").query("variant == 'L0U0V1Z0G1' and split == 'control'").set_index("mouse").hours  # 50 reps
    rows = []
    for name, prio, args, variants, splits, kind, changes in BATCHES:
        out_dir = args.split("--out_dir ")[1].split()[0]
        for i, job in enumerate(build_grid(inputs, variants, splits)):
            if name == "P1_power":
                base = ctl50[job["mouse"]] if job["split"] == "control" else ctl[job["mouse"]]
            else:
                a = analogs[kind]
                base = a.get((job["mouse"], job["variant"]), a.xs(job["mouse"], level="mouse").max())  # no-sv etc.: mouse max
            factor = math.prod(SLOWDOWN[c][kind] if c == "nominal" else SLOWDOWN[c] for c in changes)
            extra = " --n_reps 50" if (name == "P1_power" and job["split"] == "control") else ""
            rows.append({"batch": name, "priority": prio, "index": i, **job, "out": f"{out_dir}/{job['mouse']}_{job['variant']}_{job['split']}.pkl",
                         "est_hours": round(base * factor, 2), "time_hours": limit(base * factor), "args": args + extra})
    df = pd.DataFrame(rows)
    out = Path(__file__).with_name(f"tasks_{datetime.date.today():%Y-%m-%d}.csv")
    assert not out.exists(), f"{out} exists; not overwriting"
    df.to_csv(out, index=False)
    print(df.groupby("batch").agg(n=("index", "size"), est_median=("est_hours", "median"), est_max=("est_hours", "max"),
                                  limit_median=("time_hours", "median"), limit_max=("time_hours", "max"),
                                  at_cap=("time_hours", lambda x: int((x >= FIRST_MAX_HOURS).sum()))).round(2).to_string())
    print(f"\n{len(df)} tasks -> {out}")


if __name__ == "__main__":
    main()
