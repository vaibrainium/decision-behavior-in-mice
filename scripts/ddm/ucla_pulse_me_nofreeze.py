"""Recompute UCLA pulse-trial motion energy without the replay's one-frame freeze, and write new DDM inputs.

Plan .agents/plans/2026-10-29-ucla-pulse-me-nofreeze.md. The existing replay applies the UCLA burst update in a 60 Hz
frame without moving the dots ("freeze, 2 moving frames, freeze"); the no-freeze alternative moves the dots in the
same frame as the update (scripts/pulse_followup/stimulus_audit.py, states_replay(nofreeze=True)). Only frames from
the pulse onward differ, so control trials, the onset template and the per-rig calibration are unchanged.

Rows replaced: UCLA, scheduled pulse, responded (choice >= 0; no-response trials are never analysed, D003). Every
other row is copied from v1 unchanged. The UCLA pulse template is refitted on the new ME with the rule of
scripts/ddm/build_ddm_inputs.py (modal 3-frame pulses), and signal / noise rebuilt for the replaced rows.

Checks: (1) the existing convention, replayed here, reproduces v1 S + N on a subset; (2) only intended rows changed;
(3) template ratio new / old, both fitted on the same rows.

Output: <processed>/ddm/ddm_inputs_global_ucla_nofreeze.npz (+ _summary.json). v1 is not modified.
Usage:  python -B -m scripts.ddm.ucla_pulse_me_nofreeze [--workers 30] [--limit N]
"""

import argparse
import json
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.ddm.build_ddm_inputs import PULSE_RESPONSE_FRAMES, pulse_response
from scripts.ddm.pulse_energy_traces import TRIAL_TABLE

PROCESSED = Path(dir_config.data.processed)
V1 = PROCESSED / "ddm" / "ddm_inputs_global.npz"
OUT = PROCESSED / "ddm" / "ddm_inputs_global_ucla_nofreeze.npz"
ME_CAL = PROCESSED / "motion_energy_mouse" / "me_calibrated.npz"
N_FRAMES, N_CHECK, CHECK_TOL = 300, 40, 1e-4  # tolerance in coherence fraction (as inputs_v2)


def _init():
    import torch

    torch.set_num_threads(1)


def task(args):
    from scripts.pulse_followup.stimulus_audit import _me, render, states_replay

    trial_id, seed, coh, pc, on, off, check = args
    pulse = [(int(on), float(pc)), (int(off), float(coh))]
    stim, _, _ = render("ucla", states_replay("ucla", int(seed), float(coh), pulse, N_FRAMES, nofreeze=True), N_FRAMES)
    out = {"trial_id": trial_id, "me_nofreeze": _me(stim)[0]}
    if check:
        stim, _, _ = render("ucla", states_replay("ucla", int(seed), float(coh), pulse, N_FRAMES), N_FRAMES)
        out["me_replay"] = _me(stim)[0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=30)
    ap.add_argument("--limit", type=int, help="smoke test on the first N trials (no file written)")
    args = ap.parse_args()
    if OUT.exists() and not args.limit:
        raise FileExistsError(OUT)
    t0 = time.time()
    v1 = dict(np.load(V1))
    slope = float(dict(zip(*(lambda c: (c["slope_keys"], c["slope_values"]))(np.load(ME_CAL))))["ucla_global"])
    tt = pd.read_csv(PROCESSED / TRIAL_TABLE, low_memory=False,
                     usecols=["trial_id", "seed", "coherence_pct", "pulse_coherence_pct", "onset_frame", "offset_frame"]).set_index("trial_id")
    rows = np.flatnonzero((v1["data_source"] == "ucla") & (v1["sched_pulse_type"] != 0) & (v1["choice"] >= 0))
    if args.limit:
        rows = rows[: args.limit]
    meta = tt.loc[v1["agg_code"][rows].astype(str)]
    assert np.allclose(meta.coherence_pct.to_numpy() / 100, v1["signed_coherence"][rows])
    tasks = [(tid, r.seed, r.coherence_pct, r.pulse_coherence_pct, r.onset_frame, r.offset_frame, k < N_CHECK)
             for k, (tid, r) in enumerate(meta.iterrows())]
    print(f"{len(tasks)} UCLA responded pulse trials; {args.workers} workers")
    with get_context("spawn").Pool(args.workers, initializer=_init) as pool:
        res = pool.map(task, tasks, chunksize=4)
    print(f"replayed in {time.time() - t0:.0f} s")

    stored = (v1["signal"][rows].astype(np.float64) + v1["noise"][rows]) * 100  # % coherence
    me_new = np.stack([r["me_nofreeze"] for r in res]) / slope
    errs = [np.abs(r["me_replay"] / slope - stored[k]).max() / 100 for k, r in enumerate(res) if "me_replay" in r]
    coh = meta.coherence_pct.to_numpy(float)
    delta = (meta.pulse_coherence_pct - meta.coherence_pct).to_numpy(float)
    onset = meta.onset_frame.to_numpy(int) - 1
    length = (meta.offset_frame - meta.onset_frame).to_numpy(int)
    onset_resp = v1["onset_response_ucla"][:N_FRAMES].astype(np.float64)
    usable = (length == 3) & (onset >= 1) & (onset + PULSE_RESPONSE_FRAMES <= N_FRAMES) & (delta != 0)
    resid = lambda me: me[usable] - coh[usable, None] * onset_resp[None, :]
    tmpl_old = pulse_response(resid(stored), onset[usable], delta[usable], PULSE_RESPONSE_FRAMES)
    tmpl_new = pulse_response(resid(me_new), onset[usable], delta[usable], PULSE_RESPONSE_FRAMES)

    signal = coh[:, None] * onset_resp[None, :]
    for i in range(len(rows)):
        n = min(PULSE_RESPONSE_FRAMES, N_FRAMES - onset[i])
        signal[i, onset[i]: onset[i] + n] += delta[i] * tmpl_new[:n]
    summary = {
        "n_trials": int(len(rows)), "n_template_trials": int(usable.sum()), "seconds": round(time.time() - t0),
        "check_replay_reproduces_v1_max_err_frac": float(max(errs)), "check_passed": bool(max(errs) < CHECK_TOL),
        "template_v1_stored": np.round(v1["pulse_response_ucla"], 4).tolist(),
        "template_old_same_rows": np.round(tmpl_old, 4).tolist(), "template_new": np.round(tmpl_new, 4).tolist(),
        "template_peak_ratio_new_old": float(tmpl_new.max() / tmpl_old.max()),
        "template_sum_0_333ms_ratio_new_old": float(tmpl_new[:20].sum() / tmpl_old[:20].sum()),
        "template_peak_uw_v1": float(v1["pulse_response_uw"].max()),
        "note": "UCLA responded pulse rows replayed with ucla_nofreeze; all other rows and the onset template as v1",
    }
    print(json.dumps({k: v for k, v in summary.items() if not k.startswith("template_") or "ratio" in k or "uw" in k}, indent=1))
    if args.limit:
        return
    assert summary["check_passed"], "existing convention does not reproduce v1"
    new = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in v1.items()}
    new["signal"][rows] = (signal / 100).astype(np.float32)
    new["noise"][rows] = ((me_new - signal) / 100).astype(np.float32)
    new["pulse_response_ucla"] = tmpl_new.astype(v1["pulse_response_ucla"].dtype)
    other = np.setdiff1d(np.arange(len(v1["agg_code"])), rows)
    assert np.array_equal(new["signal"][other], v1["signal"][other]) and np.array_equal(new["noise"][other], v1["noise"][other])
    np.savez(OUT, **new, input_version="v1_ucla_nofreeze")
    Path(str(OUT).replace(".npz", "_summary.json")).write_text(json.dumps(summary, indent=1))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
