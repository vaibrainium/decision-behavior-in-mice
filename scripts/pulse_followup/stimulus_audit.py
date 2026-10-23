"""Package B: physical stimulus and motion-energy audit of the pulse replays (EXPLORATORY).

Plan: .agents/plans/2026-10-23-pulse-followup-parallel.md, section B (B1-B5).

What it does
  1. Chooses a reproducible, metadata-only subset of genuine pulse trials from the frozen package-A trial table
     (rig x pulse sign x nominal coherence x onset stratum, plus every in-DDM trial with an atypical recorded duration
     and responses before the pulse end). No outcome is used for selection except the recorded-duration/timing flags
     themselves, which are stimulus metadata.
  2. Replays each trial with its pulse and with the pulse events physically omitted (same initial seed), using the
     existing replay modules unchanged (scripts.ucla_rdk, scripts.uw_rdk; drawing as scripts.motion_energy.
     render_stimulus_deg, checked bitwise against it). Labelled alternatives:
       replay            existing replay convention (render_stimulus_deg)
       uw_task_counter   UW task frame-counter convention (NeuRPi StimulusManager: new_stimulus is not drawn, pulse
                         applied when frame_counter == scheduled onset, i.e. on the (P+1)-th move)
       ucla_nofreeze     replay, but the burst update is followed by a move in the same 60 Hz frame
       ucla_pass_R*_L*   UCLA display-loop emulation: R passes/s, 3 px per pass, dot lifetime L passes, burst applied
                         at the first pass at/after the recorded onset and removed at the first pass at/after
                         onset + recorded duration, 60 Hz display shows the latest pass (acquisition facts UNKNOWN)
       ucla_zero_pm0p1   UCLA 0% trials replayed at the task's actual +-0.1 coherence (sign = rewarded side)
  3. Computes motion energy (scripts.motion_energy.compute_mouse_me, causal) for both branches, checks pre-onset
     identity (rendered frames and ME), measures signed (pulse-aligned) and unsigned differences in windows after
     onset, compares the physical omission with the average-component subtraction of the DDM inputs
     (scripts.ddm.primacy.no_pulse_frames), and checks that the replay reproduces the stored ME.
  4. Dot-state audit of ALL genuine pulse trials without rendering: net horizontal motion of the dot directions
     (100 * mean sin(theta), "effective coherence") before the pulse and after the return to baseline, per branch and
     convention.
  5. Writes CSV/JSON/NPZ outputs, figures, a stage manifest and (only if all checks pass) the COMPLETE marker.

Nothing here overwrites existing ME or launches a full recomputation.

Usage
  PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.stimulus_audit --run-id <run_id>
"""

import argparse
import json
import os
import pickle
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.pulse_followup import io

STAGE = "stimulus"
PPD = {"ucla": 20, "uw": 10}
DX_DEG = 0.5
FRAME_S = 1 / 60
# windows relative to the replay onset index o (0-based frame of the first pulse frame), in frames
WINDOWS = {"during_0_333ms": (0, 20), "post_333_1000ms": (20, 60), "late_1000ms_end": (60, None)}
PASS_VARIANTS = {"ucla_pass_R190_L95": (190, 95.0), "ucla_pass_R150_L95": (150, 95.0)}
ME_ZERO_TOL = 1e-6  # relative threshold for "ME differs" (float32 rounding)
ME_REPRO_TOL = 1e-3  # relative tolerance of replayed vs stored ME (float32, possibly different BLAS/threads)


# ----------------------------------------------------------------------------------------------------------------
# replay state generators (dot states per displayed 60 Hz frame); existing replay classes are used unchanged


def _rdk(rig, lifetime=None, framerate=None):
    if rig == "ucla":
        from scripts.ucla_rdk import DotMotionStim

        r = DotMotionStim()
        if framerate is not None:
            r.framerate = framerate
        if lifetime is not None:
            r.lifetime = lifetime
        return r
    from scripts.uw_rdk import RandomDotMotion

    return RandomDotMotion()


def _new(rig, rdk, seed, coh):
    if rig == "ucla":
        rdk.newStimulus(coh, seed)
    else:
        rdk.new_stimulus({"seed": seed, "coherence": coh})


def _snap(rdk):
    return np.asarray(rdk.x, float).copy(), np.asarray(rdk.y, float).copy(), np.asarray(rdk.theta, float).copy()


def states_replay(rig, seed, coh, pulse, n_frames, nofreeze=False):
    """Mirror of scripts.motion_energy.render_stimulus_deg's state sequence (checked bitwise in the audit)."""
    rdk = _rdk(rig)
    pulses = list(pulse or [])
    for i in range(n_frames):
        if i == 0:
            _new(rig, rdk, seed, coh)
        elif pulses and i == pulses[0][0] - 1:
            if rig == "ucla":
                rdk.updateBurst(burstCoherence=pulses[0][1])
                if nofreeze:
                    rdk.moveDots()
            else:
                rdk.move_dots(new_coherence=pulses[0][1])
            pulses.pop(0)
        elif rig == "ucla":
            rdk.moveDots()
        else:
            rdk.move_dots()
        yield rdk, _snap(rdk)


def states_uw_task(seed, coh, pulse, n_frames):
    """NeuRPi StimulusManager convention: initiate_stimulus calls new_stimulus without drawing; update call k
    (frame_counter = k, k = 0, 1, ...) applies the pulse if frame_counter == pulse frame, moves, then draws.
    Displayed frame k therefore shows the state after k + 1 moves. The task's pulse list is
    [(P, pulse), (P + 4, base)] with P = scheduled onset frame = replay onset_frame - 1. Velocity int(350 / fps)
    assumed at fps = 60 (the task uses clock.get_fps(); not logged)."""
    rdk = _rdk("uw")
    _new("uw", rdk, seed, coh)
    pulses = [(int(f) - 1, c) for f, c in (pulse or [])]
    for k in range(n_frames):
        if pulses and k == pulses[0][0]:
            rdk.move_dots(new_coherence=pulses[0][1])
            pulses.pop(0)
        else:
            rdk.move_dots()
        yield rdk, _snap(rdk)


def states_ucla_pass(seed, coh, events, n_frames, rate, lifetime):
    """UCLA StimDisplay loop emulation (alternative, acquisition UNKNOWN). Each 'ShowStimulus' pass calls moveDots()
    with frames = 60 (3 px per pass at HEAD Settings.csv DotVel = 3) and draws; an 'updateBurst' pass changes the
    directions without moving or drawing and is assumed to take no time. Passes at p / rate s; the 60 Hz display
    frame k shows the latest pass with p / rate <= k / 60 (no vsync, tearing ignored). events = [(t_s, coherence)]."""
    rdk = _rdk("ucla", lifetime=lifetime, framerate=60)  # framerate 60 -> factor 1 -> vel px per pass
    _new("ucla", rdk, seed, coh)
    ev = list(events or [])
    p = 0
    for k in range(n_frames):
        while p / rate <= k * FRAME_S + 1e-12:
            while ev and ev[0][0] <= p / rate:
                rdk.updateBurst(burstCoherence=ev[0][1])
                ev.pop(0)
            rdk.moveDots()
            p += 1
        yield rdk, _snap(rdk)


def variant_states(variant, row, with_pulse, n_frames):
    rig, seed = row["rig"], int(row["seed"])
    coh = float(row["coherence_pct"])
    pc = float(row["pulse_coherence_pct"])
    on, off = int(row["onset_frame"]), int(row["offset_frame"])
    if variant == "ucla_zero_pm0p1":
        coh = 0.1 * float(row["target"])
        pc = float(np.sign(pc)) * 100
    pulse = [(on, pc), (off, coh)] if with_pulse else None
    if variant in ("replay", "ucla_zero_pm0p1"):
        return states_replay(rig, seed, coh, pulse, n_frames)
    if variant == "ucla_nofreeze":
        return states_replay(rig, seed, coh, pulse, n_frames, nofreeze=True)
    if variant == "uw_task_counter":
        return states_uw_task(seed, coh, pulse, n_frames)
    if variant in PASS_VARIANTS:
        rate, life = PASS_VARIANTS[variant]
        t_on, dur = float(row["recorded_onset_s"]), float(row["recorded_duration_s"])
        events = [(t_on, pc), (t_on + dur, coh)] if with_pulse else None
        return states_ucla_pass(seed, coh, events, n_frames, rate, life)
    raise ValueError(variant)


def variants_for(row):
    if row["rig"] == "uw":
        return ["replay", "uw_task_counter"]
    v = ["replay", "ucla_nofreeze", *PASS_VARIANTS]
    if row["coherence_pct"] == 0 and pd.notna(row["target"]):
        v.append("ucla_zero_pm0p1")
    return v


# ----------------------------------------------------------------------------------------------------------------
# rendering and ME (worker side)


def render(rig, gen, n_frames):
    """Draw as render_stimulus_deg: native-resolution filled circles, cv2.INTER_AREA onto the 0.5 deg grid.
    Returns stimulus (n_frames, ny, nx) uint8 and per-frame (effective coherence, x, y, theta)."""
    import cv2

    w, h = (1920, 1080) if rig == "ucla" else (1280, 720)
    out_size = (round(w / (PPD[rig] * DX_DEG)), round(h / (PPD[rig] * DX_DEG)))
    stim = np.empty((n_frames, out_size[1], out_size[0]), dtype=np.uint8)
    frame = np.zeros((h, w), dtype=np.uint8)
    effcoh, snaps = np.empty(n_frames), []
    for i, (rdk, (x, y, th)) in enumerate(gen):
        frame.fill(0)
        for xx, yy in zip(rdk.x, rdk.y):
            cv2.circle(frame, (int(xx), int(yy)), rdk.radius, 255, -1)
        stim[i] = cv2.resize(frame, out_size, interpolation=cv2.INTER_AREA)
        effcoh[i] = 100 * np.mean(np.sin(np.deg2rad(th)))
        snaps.append((x, y, th))
    return stim, effcoh, snaps


_KERNELS = None


def _me(stim):
    import torch

    from scripts.motion_energy import compute_mouse_me, mouse_me_kernels_torch, pool_mouse_me

    global _KERNELS
    if _KERNELS is None:
        _KERNELS = mouse_me_kernels_torch(torch.device("cpu"))
    with torch.no_grad():
        pooled = pool_mouse_me(compute_mouse_me(torch.from_numpy(stim), _KERNELS))
    return pooled["global"].numpy().astype(np.float64), pooled["center"].numpy().astype(np.float64)


def _init_worker():
    import torch

    torch.set_num_threads(1)


def replay_task(args):
    """One trial x variant: both branches rendered, compared, ME computed."""
    row, variant, n_frames, check_existing = args
    t0 = time.time()
    rig = row["rig"]
    s_with, e_with, sn_with = render(rig, variant_states(variant, row, True, n_frames), n_frames)
    s_wo, e_wo, sn_wo = render(rig, variant_states(variant, row, False, n_frames), n_frames)
    t_render = time.time() - t0
    g_with, c_with = _me(s_with)
    g_wo, c_wo = _me(s_wo)
    t_me = time.time() - t0 - t_render

    differs = np.array([not np.array_equal(a, b) for a, b in zip(s_with, s_wo)])
    first_stim_diff = int(np.argmax(differs)) if differs.any() else -1
    max_pix = np.abs(s_with.astype(int) - s_wo.astype(int)).reshape(n_frames, -1).max(axis=1)
    pos_diff = np.array([np.mean((a[0] != b[0]) | (a[1] != b[1])) for a, b in zip(sn_with, sn_wo)])
    dir_diff = np.array([np.mean(a[2] != b[2]) for a, b in zip(sn_with, sn_wo)])
    out = {
        "trial_id": row["trial_id"], "variant": variant,
        "me_global_with": g_with, "me_global_without": g_wo, "me_center_with": c_with, "me_center_without": c_wo,
        "effcoh_with": e_with, "effcoh_without": e_wo, "frac_pos_diff": pos_diff, "frac_dir_diff": dir_diff,
        "max_pixel_diff": max_pix, "first_stim_diff_frame": first_stim_diff,
        "render_s": t_render, "me_s": t_me, "n_frames": n_frames,
    }
    if check_existing:  # the replay mirror against the existing interface, both branches
        from scripts.motion_energy import render_stimulus_deg

        pars = {"seed": int(row["seed"]), "coherence": float(row["coherence_pct"])}
        ref_wo = render_stimulus_deg(rig, _rdk(rig), dict(pars), n_frames, PPD[rig])
        pars["pulse"] = [(int(row["onset_frame"]), float(row["pulse_coherence_pct"])), (int(row["offset_frame"]), float(row["coherence_pct"]))]
        ref_with = render_stimulus_deg(rig, _rdk(rig), pars, n_frames, PPD[rig])
        out["mirror_equal_with"] = bool(np.array_equal(ref_with, s_with))
        out["mirror_equal_without"] = bool(np.array_equal(ref_wo, s_wo))
    return out


def dotstate_task(row):
    """No rendering: effective coherence before the pulse and after the return to baseline, per convention."""
    rig = row["rig"]
    off = int(row["offset_frame"])
    n = off + 3  # a few frames past the replay offset (index off - 1)
    out = {"trial_id": row["trial_id"]}
    convs = ["replay"] + (["uw_task_counter"] if rig == "uw" else ["ucla_nofreeze", *PASS_VARIANTS])
    if rig == "ucla" and row["coherence_pct"] == 0 and pd.notna(row["target"]):
        convs.append("ucla_zero_pm0p1")
    for v in convs:
        nn = n if v not in PASS_VARIANTS else int(np.ceil((row["recorded_onset_s"] + row["recorded_duration_s"]) * 60)) + 3
        last_w = last_wo = None
        for (rw, sw), (rwo, swo) in zip(variant_states(v, row, True, nn), variant_states(v, row, False, nn)):
            last_w, last_wo = sw, swo
        # programmed coherence = signed fraction of dots in the task's coherent set (directions +-90 by construction)
        base_sign = np.sign(row["coherence_pct"]) if v != "ucla_zero_pm0p1" else np.sign(row["target"])
        out[f"{v}__n_cohdots_pre"] = int(len(rwo.cohDots))
        out[f"{v}__n_cohdots_post"] = int(len(rw.cohDots))
        out[f"{v}__n_dots"] = int(rw.nDots)
        out[f"{v}__programmed_coh_change_pct"] = float(base_sign * 100 * (len(rw.cohDots) - len(rwo.cohDots)) / rw.nDots)
        ew = 100 * np.mean(np.sin(np.deg2rad(last_w[2])))
        ewo = 100 * np.mean(np.sin(np.deg2rad(last_wo[2])))
        out[f"{v}__effcoh_pre"] = ewo  # without branch: directions never change after onset
        out[f"{v}__effcoh_post"] = ew
        out[f"{v}__n_coherent_post"] = int(np.sum(np.abs(np.sin(np.deg2rad(last_w[2]))) == 1.0))
        out[f"{v}__n_coherent_pre"] = int(np.sum(np.abs(np.sin(np.deg2rad(last_wo[2]))) == 1.0))
        out[f"{v}__frac_dir_changed"] = float(np.mean(last_w[2] != last_wo[2]))
        out[f"{v}__theta_sha"] = io.sha256_bytes(np.asarray(last_wo[2], float).tobytes())[:16]
    return out


# ----------------------------------------------------------------------------------------------------------------
# selection


def select_subset(trials, cfg, n_per_cell):
    """Metadata-only stratified subset (fixed seed)."""
    seed = int(cfg["control_alignment"]["seed"])  # MASTER_SEED of the frozen contract
    rng = np.random.default_rng(seed + 2)  # stage-B offset; documented in the manifest
    g = trials[trials.pulse_category.isin(["positive", "negative"]) & trials.in_ddm_input & trials.onset_frame.notna()
               & trials.offset_frame.notna() & (trials.n_pulse_frames > 0)]
    modal = g.groupby("rig").n_pulse_frames.agg(lambda s: s.mode().iloc[0])
    base = g[g.coherence_pct.isin([-100, -36, -9, 0, 9, 36, 100]) & ~g.response_before_pulse_end
             & (g.n_pulse_frames == g.rig.map(modal))]
    picks = []
    for key, cell in base.groupby(["rig", "pulse_sign", "coherence_pct", "onset_stratum"]):
        idx = rng.choice(cell.index.to_numpy(), size=min(n_per_cell, len(cell)), replace=False)
        picks.append(trials.loc[np.sort(idx)].assign(selection="stratified_cell"))
    extra = g[(g.n_pulse_frames != g.rig.map(modal)) | (g.response_before_pulse_end & (g.rig == "ucla"))]
    picks.append(trials.loc[extra.index].assign(selection="atypical_duration_or_response_during_pulse"))
    sub = pd.concat(picks).drop_duplicates("trial_id").reset_index(drop=True)
    return sub, {"rng": f"numpy default_rng({seed} + 2)", "n_per_cell": n_per_cell,
                 "cells": "rig x pulse_sign x coherence_pct in {-100,-36,-9,0,9,36,100} x onset_stratum",
                 "eligibility": "genuine positive/negative pulse, in_ddm_input, valid onset/offset frames, modal pulse "
                 "length, response_before_pulse_end False (UCLA atypical/early-response trials added separately)",
                 "modal_pulse_frames": modal.to_dict()}


# ----------------------------------------------------------------------------------------------------------------
# summaries


def t_interval(x):
    from scipy import stats

    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return {"n": n, "mean": float(x.mean()) if n else None, "sd": None, "ci_low": None, "ci_high": None}
    m, sd = x.mean(), x.std(ddof=1)
    h = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    p = float(stats.ttest_1samp(x, 0).pvalue)
    return {"n": n, "mean": float(m), "sd": float(sd), "ci_low": float(m - h), "ci_high": float(m + h), "p_vs_0": p}


def window_slice(o, w, n):
    a, b = w
    return slice(o + a, n if b is None else min(o + b, n))


def load_existing_me(trial_ids):
    from scripts.assemble_motion_energy import load_shards

    out = {}
    for d in ("motion_energy_mouse", "motion_energy_mouse_censored"):
        me, _, _ = load_shards(io.PROCESSED / d)
        for k in trial_ids:
            if k in me and k not in out:
                out[k] = np.asarray(me[k]["global"], float)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True, help="frozen package-A run ID (e.g. 20261023T191030Z_fa8de8b)")
    ap.add_argument("--n-per-cell", type=int, default=3, help="trials per rig x sign x coherence x stratum cell")
    ap.add_argument("--n-frames", type=int, default=180, help="frames replayed per branch (ME is causal)")
    ap.add_argument("--workers", type=int, default=6, help="worker processes (1 torch thread each; cap 8)")
    ap.add_argument("--skip-dotstate-all", action="store_true", help="skip the all-trial dot-state audit")
    ap.add_argument("--resume-saved-replays", type=float, default=None, metavar="REPLAY_WALL_S",
                    help="reuse subset.csv, per_trial_replay_metrics.csv and traces.npz written by an earlier invocation "
                    "that stopped after the replay step (the subset is re-derived and must match); pass the replay wall "
                    "time printed by that invocation")
    args = ap.parse_args()
    if args.workers > 8:
        sys.exit("--workers is capped at 8 (shared machine)")
    command = "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.stimulus_audit " + " ".join(sys.argv[1:])

    timer = io.Timer()
    run = io.run_dir(args.run_id)
    out = io.stage_dir(run, STAGE)
    resume = args.resume_saved_replays is not None
    saved = {"subset.csv", "per_trial_replay_metrics.csv", "traces.npz"}
    present = {p.name for p in out.iterdir()}
    if resume and present != saved:
        sys.exit(f"--resume-saved-replays needs exactly {sorted(saved)} in {out}; found {sorted(present)}")
    if not resume and present:
        sys.exit(f"{out} is not empty; refusing to mix outputs (remove only if you created it in an aborted run)")
    figdir = io.figure_dir(args.run_id)
    trials, cfg = io.load_trials(run)
    outputs, checks = [], {}

    # ---------------- subset
    sub, sel_info = select_subset(trials, cfg, args.n_per_cell)
    sub_cols = ["trial_id", "mouse", "rig", "session", "seed", "coherence_pct", "target", "pulse_category", "pulse_sign",
                "pulse_coherence_pct", "pulse_delta_pct", "onset_stratum", "recorded_onset_s", "recorded_duration_s",
                "onset_frame", "offset_frame", "n_pulse_frames", "scheduled_onset_frame", "response_before_pulse_end",
                "selection"]
    if resume:
        old = pd.read_csv(out / "subset.csv", dtype={"session": str})
        if list(old.trial_id) != list(sub.trial_id):
            sys.exit("saved subset.csv does not match the re-derived subset")
        outputs.append(out / "subset.csv")
    else:
        outputs.append(io.write_csv(out / "subset.csv", sub[sub_cols]))
    print(f"subset: {len(sub)} trials ({sub.groupby('rig').size().to_dict()})", flush=True)

    me_cal = np.load(io.PROCESSED / "motion_energy_mouse" / "me_calibrated.npz")
    slopes = dict(zip(me_cal["slope_keys"], me_cal["slope_values"].astype(float)))
    ddm = np.load(io.PROCESSED / "ddm" / "ddm_inputs_global.npz")
    ddm_row = {k: i for i, k in enumerate(ddm["agg_code"])}
    by_id = sub.set_index("trial_id")
    n = args.n_frames
    ctx = get_context("fork")
    if resume:
        replay_wall = args.resume_saved_replays
        per = pd.read_csv(out / "per_trial_replay_metrics.csv")
        z = np.load(out / "traces.npz")
        keys = list(zip(z["trial_id"].tolist(), z["variant"].tolist()))
        traces = {name: dict(zip(keys, z[name])) for name in ("diff_global_pct", "me_without_raw", "frac_pos_diff")}
        traces["ddm_gap"] = dict(zip(z["ddm_trial_id"].tolist(), z["ddm_gap_pct"]))
        traces["ddm_component"] = dict(zip(z["ddm_trial_id"].tolist(), z["ddm_component_pct"]))
        outputs += [out / "per_trial_replay_metrics.csv", out / "traces.npz"]
        res = [None] * len(per)
        print(f"resumed {len(per)} saved replay rows", flush=True)
    else:
        rows = sub.to_dict(orient="records")
        tasks = [(r, v, args.n_frames, v == "replay") for r in rows for v in variants_for(r)]
        ctx = get_context("fork")
        t_rep = time.time()
        with ctx.Pool(args.workers, initializer=_init_worker) as pool:
            res = []
            for i, r in enumerate(pool.imap_unordered(replay_task, tasks, chunksize=1)):
                res.append(r)
                if (i + 1) % 50 == 0:
                    print(f"  replay {i + 1}/{len(tasks)} ({time.time() - t_rep:.0f} s)", flush=True)
        replay_wall = time.time() - t_rep
        print(f"replays done: {len(res)} tasks in {replay_wall:.0f} s wall", flush=True)

        # ---------------- per-trial metrics
        existing = load_existing_me(sub.trial_id.tolist())

        recs, traces = [], {}
        for r in res:
            m = by_id.loc[r["trial_id"]]
            rig, sign = m["rig"], int(m["pulse_sign"])
            o = int(m["onset_frame"]) - 1  # replay index of the first pulse frame
            sl = slopes[f"{rig}_global"]
            d_raw = r["me_global_with"] - r["me_global_without"]
            d = d_raw / sl  # equivalent % coherence
            dc = (r["me_center_with"] - r["me_center_without"]) / slopes[f"{rig}_center"]
            tol = ME_ZERO_TOL * np.abs(r["me_global_with"]).max()
            nz = np.flatnonzero(np.abs(d_raw) > tol)
            rec = {"trial_id": r["trial_id"], "variant": r["variant"], "rig": rig, "pulse_sign": sign,
                   "coherence_pct": int(m["coherence_pct"]), "onset_stratum": m["onset_stratum"], "replay_onset_index": o,
                   "n_pulse_frames": int(m["n_pulse_frames"]), "selection": m["selection"],
                   "first_stim_diff_frame": r["first_stim_diff_frame"], "first_me_diff_frame": int(nz[0]) if len(nz) else -1,
                   "pre_onset_max_pixel_diff": int(r["max_pixel_diff"][:o].max()) if o > 0 else 0,
                   "pre_onset_max_abs_me_diff": float(np.abs(d_raw[:o]).max()) if o > 0 else 0.0,
                   "pre_onset_max_frac_pos_diff": float(r["frac_pos_diff"][:o].max()) if o > 0 else 0.0,
                   "frac_pos_diff_at_end": float(r["frac_pos_diff"][-1]), "frac_dir_diff_at_end": float(r["frac_dir_diff"][-1]),
                   "effcoh_pre": float(r["effcoh_without"][-1]), "effcoh_post": float(r["effcoh_with"][-1]),
                   "signed_effcoh_change": sign * float(r["effcoh_with"][-1] - r["effcoh_without"][-1]),
                   "render_s": r["render_s"], "me_s": r["me_s"]}
            for w, ww in WINDOWS.items():
                s = window_slice(o, ww, n)
                rec[f"signed_mean_{w}"] = float(sign * d[s].mean())
                rec[f"unsigned_mean_{w}"] = float(np.abs(d[s]).mean())
                rec[f"signed_mean_center_{w}"] = float(sign * dc[s].mean())
            rec["signed_sum_0_333ms_pctframes"] = float(sign * d[window_slice(o, (0, 20), n)].sum())
            if "mirror_equal_with" in r:
                rec["mirror_equal_with"], rec["mirror_equal_without"] = r["mirror_equal_with"], r["mirror_equal_without"]
            if r["variant"] == "replay":
                if r["trial_id"] in existing:
                    ex = existing[r["trial_id"]][:n]
                    rec["existing_me_max_rel_err"] = float(np.abs(ex - r["me_global_with"]).max() / max(np.abs(ex).max(), 1e-12))
                if r["trial_id"] in ddm_row:
                    j = ddm_row[r["trial_id"]]
                    sig, noi = ddm["signal"][j, :n] * 100.0, ddm["noise"][j, :n] * 100.0
                    rec["ddm_me_max_abs_err_pct"] = float(np.abs((sig + noi) - r["me_global_with"] / sl).max())
                    onset_resp = ddm[f"onset_response_{rig}"][:n]
                    no_pulse = float(m["coherence_pct"]) * onset_resp + noi  # primacy.no_pulse_frames, in %
                    phys_wo = r["me_global_without"] / sl
                    gap = no_pulse - phys_wo  # average-component subtraction minus physical omission
                    comp = (sig + noi) - no_pulse  # the DDM pulse component (delta x pulse response)
                    for w, ww in WINDOWS.items():
                        s = window_slice(o, ww, n)
                        rec[f"ddm_gap_signed_{w}"] = float(sign * gap[s].mean())
                        rec[f"ddm_gap_unsigned_{w}"] = float(np.abs(gap[s]).mean())
                        rec[f"ddm_component_signed_{w}"] = float(sign * comp[s].mean())
                    rec["ddm_gap_pre_onset_max_abs"] = float(np.abs(gap[:o]).max()) if o > 0 else 0.0
                    rec["ddm_gap_sd_post_333ms"] = float(gap[o + 20:].std())
                    rec["phys_diff_sd_post_333ms"] = float(d[o + 20:].std())
                    traces.setdefault("ddm_gap", {})[r["trial_id"]] = gap.astype(np.float32)
                    traces.setdefault("ddm_component", {})[r["trial_id"]] = comp.astype(np.float32)
            recs.append(rec)
            traces.setdefault("diff_global_pct", {})[(r["trial_id"], r["variant"])] = d.astype(np.float32)
            traces.setdefault("me_without_raw", {})[(r["trial_id"], r["variant"])] = r["me_global_without"].astype(np.float32)
            traces.setdefault("frac_pos_diff", {})[(r["trial_id"], r["variant"])] = r["frac_pos_diff"].astype(np.float32)
        per = pd.DataFrame(recs).sort_values(["rig", "variant", "trial_id"]).reset_index(drop=True)
        outputs.append(io.write_csv(out / "per_trial_replay_metrics.csv", per))

        # save traces (npz, keys documented)
        keys = sorted(traces["diff_global_pct"])
        np.savez_compressed(
            out / "traces.npz",
            trial_id=np.array([k[0] for k in keys]), variant=np.array([k[1] for k in keys]),
            diff_global_pct=np.stack([traces["diff_global_pct"][k] for k in keys]),
            me_without_raw=np.stack([traces["me_without_raw"][k] for k in keys]),
            frac_pos_diff=np.stack([traces["frac_pos_diff"][k] for k in keys]),
            ddm_trial_id=np.array(sorted(traces.get("ddm_gap", {}))),
            ddm_gap_pct=np.stack([traces["ddm_gap"][k] for k in sorted(traces.get("ddm_gap", {}))]),
            ddm_component_pct=np.stack([traces["ddm_component"][k] for k in sorted(traces.get("ddm_component", {}))]),
            note="diff = (ME with pulse - ME with pulse physically omitted) / per-rig global calibration slope, "
            "equivalent % coherence, frame index from stimulus onset (60 Hz); ddm_gap = no_pulse_frames - physical "
            "omission (replay variant); ddm_component = DDM S+N minus no_pulse_frames.",
        )
        outputs.append(out / "traces.npz")

    # ---------------- checks on the replay variant
    rp = per[per.variant == "replay"]
    checks["mirror_bitwise_equal_render_stimulus_deg"] = bool(rp.mirror_equal_with.all() and rp.mirror_equal_without.all())
    checks["pre_onset_pixels_identical_all_variants"] = bool((per.pre_onset_max_pixel_diff == 0).all())
    checks["pre_onset_me_identical_all_variants"] = {"max_abs_raw": float(per.pre_onset_max_abs_me_diff.max()), "n_exact_zero": int((per.pre_onset_max_abs_me_diff == 0).sum()), "n": len(per),
                                                     "pass": bool((per.pre_onset_max_abs_me_diff <= ME_ZERO_TOL * 1e3).all())}
    nonpass = per[~per.variant.isin(PASS_VARIANTS)]
    checks["first_stim_diff_at_replay_onset_index(non-pass variants)"] = bool((nonpass.first_stim_diff_frame >= nonpass.replay_onset_index).all())
    checks["no_me_difference_before_first_stimulus_difference"] = bool((per.first_me_diff_frame >= per.first_stim_diff_frame).all())
    has_ex = rp.existing_me_max_rel_err.notna()
    checks["replay_reproduces_stored_me"] = {"n": int(has_ex.sum()), "max_rel_err": float(rp.existing_me_max_rel_err.max()),
                                             "pass": bool(rp.existing_me_max_rel_err.max() < ME_REPRO_TOL)}
    checks["replay_reproduces_ddm_S_plus_N"] = {"n": int(rp.ddm_me_max_abs_err_pct.notna().sum()),
                                                "max_abs_err_pct": float(rp.ddm_me_max_abs_err_pct.max()),
                                                "pass": bool(rp.ddm_me_max_abs_err_pct.max() < 0.05)}

    # ---------------- aggregates
    agg = {}
    for (rig, var), g in per.groupby(["rig", "variant"]):
        a = {"n_trials": len(g)}
        for w in WINDOWS:
            a[f"signed_{w}"] = t_interval(g[f"signed_mean_{w}"])
            a[f"unsigned_{w}"] = t_interval(g[f"unsigned_mean_{w}"])
        a["signed_sum_0_333ms_pctframes"] = t_interval(g["signed_sum_0_333ms_pctframes"])
        a["signed_effcoh_change"] = t_interval(g["signed_effcoh_change"])
        a["frac_pos_diff_at_end"] = t_interval(g["frac_pos_diff_at_end"])
        a["frac_dir_diff_at_end"] = t_interval(g["frac_dir_diff_at_end"])
        a["first_stim_minus_onset_index"] = {int(k): int(v) for k, v in g.eval("first_stim_diff_frame - replay_onset_index").value_counts().sort_index().items()}
        a["first_me_minus_first_stim_diff"] = {int(k): int(v) for k, v in g.eval("first_me_diff_frame - first_stim_diff_frame").value_counts().sort_index().items()}
        if var == "replay" and "ddm_gap_signed_during_0_333ms" in g:
            for w in WINDOWS:
                a[f"ddm_gap_signed_{w}"] = t_interval(g[f"ddm_gap_signed_{w}"])
                a[f"ddm_gap_unsigned_{w}"] = t_interval(g[f"ddm_gap_unsigned_{w}"])
                a[f"ddm_component_signed_{w}"] = t_interval(g[f"ddm_component_signed_{w}"])
            a["ddm_gap_pre_onset_max_abs"] = float(g.ddm_gap_pre_onset_max_abs.max())
            a["ddm_gap_sd_post_333ms_median"] = float(g.ddm_gap_sd_post_333ms.median())
            a["phys_diff_sd_post_333ms_median"] = float(g.phys_diff_sd_post_333ms.median())
        # by pulse sign separately (directional check)
        a["by_sign_signed_post_333_1000ms"] = {int(s): t_interval(gg["signed_mean_post_333_1000ms"]) for s, gg in g.groupby("pulse_sign")}
        a["by_sign_signed_late_1000ms_end"] = {int(s): t_interval(gg["signed_mean_late_1000ms_end"]) for s, gg in g.groupby("pulse_sign")}
        agg[f"{rig}__{var}"] = a

    # pulse energy of each UCLA variant relative to the replay, scale-corrected by the variant's own coherence slope
    # (fit on the no-pulse branches of the subset: mean raw ME over frames 30..end vs nominal coherence)
    energy = {}
    me_wo = dict(zip(zip(np.array([k[0] for k in keys]), np.array([k[1] for k in keys])), [traces["me_without_raw"][k] for k in keys]))
    for rig in ("ucla", "uw"):
        for var in per[per.rig == rig].variant.unique():
            ids = per[(per.rig == rig) & (per.variant == var)].trial_id
            c = by_id.loc[ids, "coherence_pct"].to_numpy(float)
            y = np.array([me_wo[(i, var)][30:].mean() for i in ids])
            slope_v = float(np.polyfit(c, y, 1)[0]) if len(np.unique(c)) > 2 else np.nan
            g = per[(per.rig == rig) & (per.variant == var)]
            raw_sum = g.signed_sum_0_333ms_pctframes.to_numpy() * slopes[f"{rig}_global"] / slope_v  # in variant's own % units
            delta = np.abs(by_id.loc[g.trial_id, "pulse_delta_pct"].to_numpy(float))
            energy[f"{rig}__{var}"] = {"own_slope_raw_per_pct": slope_v, "stored_slope_raw_per_pct": slopes[f"{rig}_global"],
                                       "signed_sum_0_333ms_per_pct_delta": t_interval(raw_sum / delta)}
    for rig in ("ucla", "uw"):
        ref = energy[f"{rig}__replay"]["signed_sum_0_333ms_per_pct_delta"]["mean"]
        for k, v in energy.items():
            if k.startswith(rig):
                m_ = v["signed_sum_0_333ms_per_pct_delta"]["mean"]
                v["ratio_to_replay"] = None if (m_ is None or ref is None) else m_ / ref
    ddm_pulse_sum = {rig: float(ddm[f"pulse_response_{rig}"][:20].sum()) for rig in ("ucla", "uw")}
    energy["ddm_pulse_response_sum_0_333ms_per_pct"] = ddm_pulse_sum

    # ---------------- all-trial dot-state audit
    dot_summary = {}
    if not args.skip_dotstate_all:
        g = trials[trials.pulse_category.isin(["positive", "negative"]) & trials.onset_frame.notna() & trials.offset_frame.notna()
                   & (trials.n_pulse_frames > 0) & trials.recorded_duration_s.notna()]
        t_dot = time.time()
        with ctx.Pool(args.workers, initializer=_init_worker) as pool:
            dres = list(pool.imap_unordered(dotstate_task, g.to_dict(orient="records"), chunksize=20))
        dot_wall = time.time() - t_dot
        dots = pd.DataFrame(dres).merge(g[["trial_id", "rig", "pulse_sign", "coherence_pct", "onset_stratum", "in_ddm_input"]], on="trial_id")
        outputs.append(io.write_csv(out / "dotstate_all_pulse_trials.csv", dots))
        for rig, gg in dots.groupby("rig"):
            convs = [c[: -len("__effcoh_pre")] for c in gg.columns if c.endswith("__effcoh_pre") and gg[c].notna().any()]
            ds = {"n_trials": len(gg), "wall_s": round(dot_wall, 1)}
            for v in convs:
                h = gg[gg[f"{v}__effcoh_pre"].notna()]
                ch = h.pulse_sign * (h[f"{v}__effcoh_post"] - h[f"{v}__effcoh_pre"])
                ds[v] = {
                    "signed_effcoh_change": t_interval(ch),
                    "signed_effcoh_change_by_sign": {int(s): t_interval(c) for s, c in ch.groupby(h.pulse_sign)},
                    "signed_effcoh_change_by_abs_coh": {int(a): t_interval(c) for a, c in ch.groupby(h.coherence_pct.abs())},
                    "n_coherent_post_minus_pre": {int(k): int(c) for k, c in (h[f"{v}__n_coherent_post"] - h[f"{v}__n_coherent_pre"]).value_counts().sort_index().items()},
                    "pulse_aligned_programmed_coh_change_pct": t_interval(h.pulse_sign * h[f"{v}__programmed_coh_change_pct"]),
                    "programmed_change_table": [
                        {"abs_coh": int(a), "congruent": bool(cg), "n": len(x),
                         "cohdot_change_values": {int(k): int(c) for k, c in (x[f"{v}__n_cohdots_post"] - x[f"{v}__n_cohdots_pre"]).value_counts().sort_index().items()},
                         "pulse_aligned_change_pct_mean": float((x.pulse_sign * x[f"{v}__programmed_coh_change_pct"]).mean())}
                        for (a, cg), x in h.groupby([h.coherence_pct.abs(), np.sign(h.coherence_pct) == h.pulse_sign])],
                    "noise_only_signed_effcoh_change": t_interval(ch - h.pulse_sign * h[f"{v}__programmed_coh_change_pct"]),
                    "frac_dir_changed_median": float(h[f"{v}__frac_dir_changed"].median()),
                    "corr_pre_post": float(np.corrcoef(h[f"{v}__effcoh_pre"], h[f"{v}__effcoh_post"])[0, 1]),
                    "sd_pre": float(h[f"{v}__effcoh_pre"].std()), "sd_post": float(h[f"{v}__effcoh_post"].std()),
                }
            for v in convs:
                if v == "replay":
                    continue
                h = gg[gg[f"{v}__effcoh_pre"].notna()]
                ds[v]["corr_with_replay_pre"] = float(np.corrcoef(h["replay__effcoh_pre"], h[f"{v}__effcoh_pre"])[0, 1])
                ds[v]["corr_with_replay_post"] = float(np.corrcoef(h["replay__effcoh_post"], h[f"{v}__effcoh_post"])[0, 1])
                ds[v]["frac_initial_theta_identical_to_replay"] = float((h["replay__theta_sha"] == h[f"{v}__theta_sha"]).mean())
                ds[v]["post_minus_replay_post_sd"] = float((h[f"{v}__effcoh_post"] - h["replay__effcoh_post"]).std())
            dot_summary[rig] = ds

    # ---------------- runtime and extrapolation
    rp_t = per[per.variant == "replay"].groupby("rig")[["render_s", "me_s"]].mean()
    n_trials_all = trials.groupby("rig").size().to_dict()
    runtime = {"replay_tasks": len(res), "replay_wall_s": round(replay_wall, 1), "workers": args.workers, "frames_per_branch": n,
               "mean_s_per_branch_pair_replay_variant": rp_t.to_dict(orient="index"),
               "machine_note": "32-core host shared with other workers (load average ~33 at start); 1 torch thread per worker; no CUDA device available (NVML error, torch.cuda False)"}
    extrap = {}
    for rig, rr in rp_t.iterrows():
        per_pair_300 = (rr.render_s + rr.me_s) * 300 / n  # both branches, one trial, 300 frames, one core
        extrap[rig] = {"trials": int(n_trials_all[rig]), "core_hours_both_branches_300_frames": round(per_pair_300 * n_trials_all[rig] / 3600, 2)}
    extrap["total_core_hours"] = round(sum(v["core_hours_both_branches_300_frames"] for v in extrap.values() if isinstance(v, dict)), 2)
    extrap["wall_hours_at_8_workers"] = round(extrap["total_core_hours"] / 8, 2)
    extrap["note"] = "one replay convention, with and without pulse, all 30,045 contract trials (controls need only one branch, so this is an upper bound); each additional convention adds the same again"
    runtime["full_replay_extrapolation"] = extrap

    summary = {"run_id": args.run_id, "status": "EXPLORATORY", "selection": sel_info, "n_subset": len(sub),
               "subset_by_rig": sub.groupby("rig").size().to_dict(), "windows_frames_from_onset_index": WINDOWS,
               "calibration_slopes_raw_per_pct": slopes, "aggregates": agg, "pulse_energy": energy,
               "dotstate_all_trials": dot_summary, "runtime": runtime, "checks": checks}
    outputs.append(io.write_json(out / "summary.json", summary))

    # ---------------- figures
    outputs += make_figures(per, keys, traces, by_id, ddm, dots if not args.skip_dotstate_all else None, figdir, n)

    # ---------------- manifest
    all_pass = all(v if isinstance(v, bool) else v["pass"] for v in checks.values())
    code_files = ["scripts/pulse_followup/stimulus_audit.py", "scripts/motion_energy.py", "scripts/ucla_rdk.py", "scripts/uw_rdk.py",
                  "scripts/compute_motion_energy_full.py", "scripts/ddm/build_ddm_inputs.py", "scripts/ddm/primacy.py",
                  "scripts/assemble_motion_energy.py"]
    inputs = {"trial_table": cfg["hashes"]["trial_table"],
              "me_calibrated.npz": io.sha256_file(io.PROCESSED / "motion_energy_mouse" / "me_calibrated.npz"),
              "ddm_inputs_global.npz": io.sha256_file(io.PROCESSED / "ddm" / "ddm_inputs_global.npz"),
              **{f: io.sha256_file(io.REPO / f) for f in code_files}}
    for d in ("motion_energy_mouse", "motion_energy_mouse_censored"):
        for p in sorted((io.PROCESSED / d).glob("me_shard_*.pkl")):
            inputs[f"{d}/{p.name}"] = io.sha256_file(p)
    import torch, cv2

    manifest = io.stage_manifest(STAGE, command, inputs, outputs, checks, timer.seconds,
                                 extra={"run_id": args.run_id, "torch": torch.__version__, "opencv": cv2.__version__,
                                        "selection": sel_info, "analysis_set": "genuine positive/negative pulses, in_ddm_input (subset); all genuine pulses with valid durations (dot-state audit)",
                                        "task_source_commits": {"NeuRPi": "fcfb603", "RDK-Task": "6fb3878"}})
    ok = io.mark_complete(out, manifest, all_pass)
    print(json.dumps(checks, indent=1))
    print(f"COMPLETE written: {ok}; outputs in {out}")


def make_figures(per, keys, traces, by_id, ddm, dots, figdir, n):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    files = []
    t_ms = lambda k: np.arange(k) * 1000 / 60
    # 1. sign-aligned physical difference traces, replay variant, per rig, with the DDM average component
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), constrained_layout=True)
    for col, rig in enumerate(("ucla", "uw")):
        g = per[(per.rig == rig) & (per.variant == "replay")]
        lag = np.arange(-10, 120)
        mats, comps = [], []
        for _, r in g.iterrows():
            d = traces["diff_global_pct"][(r.trial_id, "replay")] * r.pulse_sign
            o = r.replay_onset_index
            idx = o + lag
            ok = (idx >= 0) & (idx < n)
            row = np.full(len(lag), np.nan)
            row[ok] = d[idx[ok]]
            mats.append(row / abs(by_id.loc[r.trial_id, "pulse_delta_pct"]) * 100)
            if r.trial_id in traces.get("ddm_component", {}):
                c = traces["ddm_component"][r.trial_id] * r.pulse_sign
                rc = np.full(len(lag), np.nan)
                rc[ok] = c[idx[ok]]
                comps.append(rc / abs(by_id.loc[r.trial_id, "pulse_delta_pct"]) * 100)
        mats = np.array(mats)
        x = lag * 1000 / 60
        ax = axes[0, col]
        for m in mats:
            ax.plot(x, m, color="0.6", lw=0.4, alpha=0.5)
        ax.plot(x, np.nanmean(mats, 0), color="C0", lw=2, label="physical difference, mean")
        if comps:
            ax.plot(x, np.nanmean(comps, 0), color="C3", lw=1.5, ls="--", label="DDM average pulse component")
        ax.axvline(0, color="k", lw=0.8)
        ax.axhline(0, color="k", lw=0.5)
        ax.set_title(f"{rig.upper()} replay: (with - without) x pulse sign, per 100% pulse change (n={len(mats)})", fontsize=9)
        ax.set_xlabel("time from replay pulse onset (ms)")
        ax.set_ylabel("ME difference (equiv. % coherence)")
        ax.legend(fontsize=7)
        ax = axes[1, col]
        m = np.nanmean(mats, 0)
        se = np.nanstd(mats, 0, ddof=1) / np.sqrt(np.sum(np.isfinite(mats), 0))
        post = x > 333
        ax.fill_between(x[post], (m - 1.96 * se)[post], (m + 1.96 * se)[post], color="C0", alpha=0.3)
        ax.plot(x[post], m[post], color="C0")
        ax.axhline(0, color="k", lw=0.5)
        ax.set_title(f"{rig.upper()} after 333 ms: mean +- 95% (normal) band", fontsize=9)
        ax.set_xlabel("time from replay pulse onset (ms)")
        ax.set_ylabel("ME difference (equiv. % coherence)")
    p = figdir / "stimulus_paired_difference_traces.png"
    files.append(io.savefig(fig, p, dpi=150))
    plt.close(fig)

    # 2. dot-state audit: signed change in effective coherence after return; UW replay vs task-counter post
    if dots is not None:
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
        for ax, rig in zip(axes[:2], ("ucla", "uw")):
            h = dots[dots.rig == rig]
            ch = h.pulse_sign * (h["replay__effcoh_post"] - h["replay__effcoh_pre"])
            for s, c in ((1, "C0"), (-1, "C1")):
                ax.hist(ch[h.pulse_sign == s], bins=60, alpha=0.5, color=c, label=f"pulse sign {s:+d} (n={int((h.pulse_sign == s).sum())})")
            ax.axvline(0, color="k", lw=0.8)
            ax.set_title(f"{rig.upper()} replay: pulse-aligned change in dot-direction\nnet motion after return (all genuine pulses)", fontsize=9)
            ax.set_xlabel("sign x (post - pre) effective coherence (%)")
            ax.legend(fontsize=7)
        h = dots[dots.rig == "uw"]
        axes[2].scatter(h["replay__effcoh_post"], h["uw_task_counter__effcoh_post"], s=2, alpha=0.3)
        axes[2].set_xlabel("replay: post-return effective coherence (%)")
        axes[2].set_ylabel("UW task-counter convention (%)")
        axes[2].set_title("UW: post-return noise, replay vs task convention", fontsize=9)
        p = figdir / "stimulus_direction_reset.png"
        files.append(io.savefig(fig, p, dpi=150))
        plt.close(fig)

    # 3. UCLA alternatives: mean pulse-aligned difference per variant
    fig, ax = plt.subplots(figsize=(6.5, 4), constrained_layout=True)
    lag = np.arange(-5, 40)
    for var in per[per.rig == "ucla"].variant.unique():
        g = per[(per.rig == "ucla") & (per.variant == var)]
        mats = []
        for _, r in g.iterrows():
            d = traces["diff_global_pct"][(r.trial_id, var)] * r.pulse_sign
            idx = r.replay_onset_index + lag
            ok = (idx >= 0) & (idx < n)
            row = np.full(len(lag), np.nan)
            row[ok] = d[idx[ok]]
            mats.append(row / abs(by_id.loc[r.trial_id, "pulse_delta_pct"]) * 100)
        ax.plot(lag * 1000 / 60, np.nanmean(mats, 0), label=f"{var} (n={len(mats)})")
    ax.axvline(0, color="k", lw=0.8)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel("time from replay pulse onset (ms)")
    ax.set_ylabel("mean pulse-aligned ME difference\n(stored-slope % coh., per 100% change)")
    ax.set_title("UCLA labelled replay alternatives (not calibrated to each variant's own scale)", fontsize=9)
    ax.legend(fontsize=7)
    p = figdir / "stimulus_ucla_alternatives.png"
    files.append(io.savefig(fig, p, dpi=150))
    plt.close(fig)
    return files


if __name__ == "__main__":
    main()
