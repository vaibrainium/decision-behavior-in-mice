"""Corrected, versioned DDM inputs for the pulse follow-up model pilot (coordinator; user decision 2026-10-23).

ddm_inputs_global.npz (v1) labels 38 UCLA no-response pulse trials as controls and replayed them without their
pulse: notebook 0.0 derives the UCLA pulse direction from the response-dependent target (package A report). This
writes a NEW file; v1 and everything derived from it stay untouched.

  - the 38 genuine pulses (pulse_direction_recovered & pulse_sign != 0): replayed with their pulse through the
    existing renderer and ME filter (scripts.motion_energy.render_stimulus_deg / compute_mouse_me), calibrated with
    the v1 per-rig slope; signal rebuilt with the v1 onset and pulse response templates (kept fixed, so every other
    trial stays byte-identical); sched_pulse_type and condition relabelled
  - the 5 recovered null pulses (same-sign 100% pulse on a 100% stimulus) are physically unchanged: kept as in v1
  - the 5 pulse_direction_unknown trials (UCLA 0%, no response): dropped (neither control nor a known pulse)
Before replacing anything, each trial's v1 stimulus must be reproduced exactly: v1 replayed these trials with a pulse
event of NaN coherence (no dot direction changes, but the renderer still spends the onset/offset frames on the
event), so the reconstruction uses that event, not a plain no-pulse replay.

Output: <run>/models/inputs_v2/ddm_inputs_global_v2.npz, changes.csv, manifest.json, COMPLETE.

Usage: python -B -m scripts.pulse_followup.inputs_v2 --run-id <run_id> [--workers 6]
"""

import argparse
import sys
from multiprocessing import get_context

import numpy as np
import pandas as pd

from scripts.pulse_followup import io
from scripts.pulse_followup.config import STRATUM_NAMES

V1 = io.PROCESSED / "ddm" / "ddm_inputs_global.npz"
ME_CAL = io.PROCESSED / "motion_energy_mouse" / "me_calibrated.npz"
PPD = {"ucla": 20, "uw": 10}  # compute_motion_energy_full.PPD
N_FRAMES = 300
CHECK_TOL = 1e-4  # fraction units (0.01% coherence); B found max 5.7e-5 % coherence between replay and stored S+N


def _init():
    import torch

    torch.set_num_threads(1)


def replay(task):
    """Global ME (raw filter units) of one trial as replayed in v1 (NaN pulse event) and with its pulse."""
    import torch

    from scripts.motion_energy import compute_mouse_me, mouse_me_kernels_torch, pool_mouse_me, render_stimulus_deg
    from scripts.ucla_rdk import DotMotionStim
    from scripts.uw_rdk import RandomDotMotion

    trial_id, rig, seed, coh, onset, offset, pulse_coh = task
    kernels = mouse_me_kernels_torch(torch.device("cpu"))
    out = {}
    for with_pulse in (False, True):
        pars = {"seed": int(seed), "coherence": float(coh),
                "pulse": [(int(onset), float(pulse_coh) if with_pulse else float("nan")), (int(offset), float(coh))]}
        rdk = DotMotionStim() if rig == "ucla" else RandomDotMotion()
        stim = render_stimulus_deg(rig, rdk, pars, N_FRAMES, PPD[rig])
        with torch.no_grad():
            out[with_pulse] = pool_mouse_me(compute_mouse_me(torch.from_numpy(stim), kernels))["global"].numpy().astype(np.float64)
    return trial_id, out[False], out[True]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-id", required=True)
    p.add_argument("--workers", type=int, default=6)
    args = p.parse_args(argv)
    timer = io.Timer()
    rd = io.run_dir(args.run_id)
    t, _ = io.load_trials(rd)
    out = io.stage_dir(rd, "models") / "inputs_v2"
    if (out / "COMPLETE").exists():
        raise FileExistsError(f"{out} is complete")
    out.mkdir(exist_ok=True)

    v1 = dict(np.load(V1))
    cal = np.load(ME_CAL)
    slopes = dict(zip(cal["slope_keys"], cal["slope_values"].astype(float)))
    index = {c: i for i, c in enumerate(v1["agg_code"])}

    fix = t[t.in_ddm_input & t.pulse_direction_recovered & (t.pulse_sign != 0)].copy()
    drop = t[t.in_ddm_input & (t.pulse_category == "pulse_direction_unknown")]
    assert (fix.rig == "ucla").all() and fix.n_pulse_frames.gt(0).all() and fix.onset_frame.notna().all()
    tasks = [(r.trial_id, r.rig, r.seed, r.coherence_pct, r.onset_frame, r.offset_frame, r.pulse_coherence_pct) for r in fix.itertuples()]
    with get_context("spawn").Pool(args.workers, initializer=_init) as pool:
        results = pool.map(replay, tasks)

    checks, rows = {}, []
    new = {k: (v.copy() if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == len(v1["agg_code"]) else v) for k, v in v1.items()}
    max_err = 0.0
    for (trial_id, me_wo, me_with), r in zip(results, fix.itertuples()):
        i = index[trial_id]
        slope = slopes[f"{r.rig}_global"]
        stored = (v1["signal"][i].astype(np.float64) + v1["noise"][i]) * 100  # % coherence
        err = np.abs(me_wo / slope - stored).max() / 100
        max_err = max(max_err, err)
        me = me_with / slope  # % coherence
        onset_resp = v1[f"onset_response_{r.rig}"][:N_FRAMES]
        pulse_resp = v1[f"pulse_response_{r.rig}"]
        delta = r.pulse_coherence_pct - r.coherence_pct
        signal = r.coherence_pct * onset_resp
        o = int(r.onset_frame) - 1  # build_ddm_inputs: onset_frame - 1
        n = min(len(pulse_resp), N_FRAMES - o)
        signal[o : o + n] += delta * pulse_resp[:n]
        new["signal"][i] = (signal / 100).astype(np.float32)
        new["noise"][i] = ((me - signal) / 100).astype(np.float32)
        stratum = STRATUM_NAMES.index(r.onset_stratum) + 1
        new["sched_pulse_type"][i] = int(r.pulse_sign * stratum)
        new["condition"][i] = int(round(r.coherence_pct)) * 10 + new["sched_pulse_type"][i]
        locked = (me[o : o + 20] - me[o - 1]) * r.pulse_sign
        rows.append({"trial_id": trial_id, "action": "relabel_and_replay_with_pulse", "sched_v1": int(v1["sched_pulse_type"][i]),
                     "sched_v2": int(new["sched_pulse_type"][i]), "v1_reconstruction_max_abs_err_frac": err,
                     "pulse_locked_peak_pct": float(locked.max())})
    checks["v1_reconstruction_reproduces_v1"] = bool(max_err < CHECK_TOL)
    checks["v1_reconstruction_max_abs_err_frac"] = float(max_err)

    keep = ~np.isin(new["agg_code"], drop.trial_id.to_numpy())
    for k, v in list(new.items()):
        if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == len(v1["agg_code"]):
            new[k] = v[keep]
    rows += [{"trial_id": d, "action": "dropped_direction_unknown"} for d in drop.trial_id]

    # checks: only the intended rows changed; labels now agree with the frozen table
    changed = set(fix.trial_id)
    same = np.array([c not in changed for c in new["agg_code"]])
    v1_rows = np.array([index[c] for c in new["agg_code"]])
    for k in ("signal", "noise", "sched_pulse_type", "condition", "rt", "choice", "censored", "signed_coherence"):
        checks[f"unchanged_rows_identical_{k}"] = bool(np.array_equal(new[k][same], v1[k][v1_rows[same]]))
    for k in ("onset_response_ucla", "onset_response_uw", "pulse_response_ucla", "pulse_response_uw"):
        checks[f"template_identical_{k}"] = bool(np.array_equal(new[k], v1[k]))
    tt = t.set_index("trial_id").loc[new["agg_code"]]
    stratum_index = tt.onset_stratum.map({n: i + 1 for i, n in enumerate(STRATUM_NAMES)}).fillna(0).to_numpy()
    expected = np.where(tt.pulse_sign != 0, tt.pulse_sign * stratum_index, 0)
    checks["sched_pulse_type_matches_frozen_table"] = bool((new["sched_pulse_type"] == expected).all())
    peaks = np.array([r["pulse_locked_peak_pct"] for r in rows if "pulse_locked_peak_pct" in r])
    checks["replayed_pulse_present_mean_peak_pct_gt_10"] = bool(peaks.mean() > 10)  # single trials are noisy (~8%)
    checks["replayed_pulse_mean_peak_pct"] = float(peaks.mean())
    checks["n_trials_v2"] = int(keep.sum())
    checks["n_relabelled"] = len(fix)
    checks["n_dropped"] = int((~keep).sum())
    passed = all(v for k, v in checks.items() if isinstance(v, bool))
    for k, v in checks.items():
        print(f"  {k}: {v}")

    path = out / "ddm_inputs_global_v2.npz"
    if path.exists():
        raise FileExistsError(path)
    np.savez(path, **new, input_version="v2", v1_sha256=io.sha256_file(V1))
    io.write_csv(out / "changes.csv", pd.DataFrame(rows))
    manifest = io.stage_manifest("models/inputs_v2", " ".join(["python -B -m scripts.pulse_followup.inputs_v2", *(argv or sys.argv[1:])]),
                                 {"ddm_inputs_v1": io.sha256_file(V1), "me_calibrated": io.sha256_file(ME_CAL)},
                                 [path, out / "changes.csv"], checks, timer.seconds,
                                 extra={"v2_sha256": io.sha256_file(path), "note": "templates and all other trials as v1; control fits not refitted"})
    io.mark_complete(out, manifest, passed)
    print(f"v2: {checks['n_trials_v2']} trials ({len(fix)} relabelled + replayed, {checks['n_dropped']} dropped); passed = {passed}; {timer.seconds} s")


if __name__ == "__main__":
    main()
