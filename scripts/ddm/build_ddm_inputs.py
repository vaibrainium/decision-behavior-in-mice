"""Build per-trial DDM evidence inputs from the replayed motion energy.

Each trial's motion energy (ME, full 5 s replay, equivalent % coherence) is split into
  S(t): the ME expected from the programmed coherence time course (base coherence plus any pulse):
        the coherence at onset passed through the onset step response (fit on control trials), plus the
        pulse passed through the measured pulse response (mean pulse-locked ME change per % coherence change,
        fit on pulse trials). A step response from onset would be wrong for pulses: at onset the filters are
        still filling after a blank screen, so they respond ~50 ms later than to a change in an ongoing stimulus.
  N(t): ME - S, the stimulus noise (mostly the seed's fixed hidden coherence).
S + N is exactly the trial's ME, so a DDM with drift g * (S + k * N) has k = 1 for raw ME and k = 0 for
programmed coherence only. Both channels carry the same ~116 ms filter delay.

Trials are labelled by their *scheduled* pulse condition (`condition`), not by `pulse_type`: preprocessing
sets pulse_type = 0 when the response came before the pulse ended, which would group trials by outcome.

Trials: valid_data (responses at 0.3-5 s) plus censored_trials.csv (no response by 5 s: RT > 5 s or none, in the
same sessions; rt = inf, choice = -1).

Output: <processed>/ddm/ddm_inputs_<region>.npz, inputs in coherence fraction units (% / 100), 60 Hz frames.

Usage: python -m scripts.ddm.build_ddm_inputs [--region global]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from config import dir_config
from scripts.assemble_motion_energy import load_shards
from scripts.compute_motion_energy_full import convert_to_frame_units

FRAME_RATE = 60
PULSE_BINS_S = [0.0, 0.16, 0.32, 0.48]  # onset bins of preprocessing notebook 0.1 (early, middle, late)
PULSE_RESPONSE_FRAMES = 60  # 1 s: the ME response to a 50-67 ms pulse is over well before this


def scheduled_pulse(data):
    """Scheduled pulse condition: sign(pulse coherence) * onset bin (1-3), 0 if no coherence change was scheduled."""
    has_pulse = data["is_pulse_trial"] & (data["pulse_coherence"] != data["signed_coherence"])
    onset_bin = np.digitize(data["pulse_onset"].fillna(-1), PULSE_BINS_S[1:]) + 1
    return np.where(has_pulse, onset_bin * np.sign(data["pulse_coherence"].fillna(0)), 0).astype(int)


def step_response(me, coherence):
    """ME per % coherence at each frame after a coherence step at frame 0 (least squares through the origin)."""
    c = coherence[:, None]
    return (c * me).sum(axis=0) / (c**2).sum()


def pulse_response(residual, onset, delta, n_lags):
    """Mean pulse-locked change per % coherence change in `residual` (ME minus the expected onset response),
    relative to the frame before the pulse. Removing the onset response first matters for early pulses, which
    arrive while the onset response is still rising.

    Each rig uses a single pulse length (UCLA 3 frames, UW 4), so the response to the whole pulse is
    measured directly instead of being built from a step response.
    """
    y = np.stack([residual[i, o : o + n_lags] - residual[i, o - 1] for i, o in enumerate(onset)])
    return (delta[:, None] * y).sum(axis=0) / (delta**2).sum()


def expected_me(trace_onset, onset_response, pulse_onset, pulse_delta, response_to_pulse, n_frames):
    """Onset coherence through the onset step response, plus each trial's pulse through the pulse response."""
    out = trace_onset[:, None] * onset_response[None, :n_frames]
    for i in np.flatnonzero(pulse_delta != 0):
        o = pulse_onset[i]
        n = min(len(response_to_pulse), n_frames - o)
        out[i, o : o + n] += pulse_delta[i] * response_to_pulse[:n]
    return out


def main(region):
    processed_dir = Path(dir_config.data.processed)
    me_file = np.load(processed_dir / "motion_energy_mouse" / "me_calibrated.npz")
    slopes = dict(zip(me_file["slope_keys"], me_file["slope_values"]))
    me_by_code = dict(zip(me_file["agg_code"], me_file[region]))

    # censored trials (no response by 5 s): replayed separately, calibrated with the same per-rig slopes
    censored_me, _, _ = load_shards(processed_dir / "motion_energy_mouse_censored")
    censored = pd.read_csv(processed_dir / "censored_trials.csv")
    for code, rig in zip(censored["agg_code"], censored["data_source"]):
        if code in censored_me:
            pooled = censored_me[code]
            raw = pooled[region] if region in ("global", "center") else pooled["quadrants"][region]
            me_by_code[code] = np.asarray(raw, dtype=np.float32) / slopes[f"{rig}_{region}"]

    valid = pd.read_csv(processed_dir / "valid_data.csv").assign(censored=False)
    data = convert_to_frame_units(pd.concat([valid, censored.assign(censored=True)], ignore_index=True))
    invalid_pulse = data["pulse_onset"].notna() & ~(data["pulse_offset_frame"] > data["pulse_onset_frame"])
    print(f"dropping {invalid_pulse.sum()} trials with a missing or non-positive pulse duration (stimulus unknown)")
    data = data[~invalid_pulse & data["agg_code"].isin(me_by_code.keys())].reset_index(drop=True)
    data["sched_pulse_type"] = scheduled_pulse(data)
    print(f"{(~data['censored']).sum()} responded trials (0.3-5 s), {data['censored'].sum()} censored (no response by 5 s)")

    me = np.stack([me_by_code[c] for c in data["agg_code"]]).astype(np.float64)
    n_frames = me.shape[1]

    onset_frame = data["pulse_onset_frame"].fillna(0).to_numpy(int) - 1
    pulse_frames = (data["pulse_offset_frame"] - data["pulse_onset_frame"]).fillna(0).to_numpy(int)
    delta = (data["pulse_coherence"] - data["signed_coherence"]).fillna(0).to_numpy(float)

    signal = np.zeros_like(me)
    responses, pulse_responses = {}, {}
    for rig in data["data_source"].unique():
        rows = (data["data_source"] == rig).to_numpy()
        fit_rows = rows & (data["sched_pulse_type"] == 0).to_numpy() & (data["signed_coherence"] != 0).to_numpy() & ~data["censored"].to_numpy()
        responses[rig] = step_response(me[fit_rows], data["signed_coherence"].to_numpy(float)[fit_rows])
        pulsed = rows & (data["sched_pulse_type"] != 0).to_numpy()  # censored trials included: their pulse is in the replay
        lengths, counts = np.unique(pulse_frames[pulsed], return_counts=True)
        main_length = lengths[np.argmax(counts)]
        if len(lengths) > 1:
            print(f"{rig}: pulse lengths {dict(zip(lengths.tolist(), counts.tolist()))} frames; response fit on {main_length}-frame pulses and applied to all")
        usable = np.flatnonzero(pulsed & (pulse_frames == main_length) & (onset_frame >= 1) & (onset_frame + PULSE_RESPONSE_FRAMES <= n_frames))
        onset_part = data["signed_coherence"].to_numpy(float)[usable, None] * responses[rig][None, :]
        pulse_responses[rig] = pulse_response(me[usable] - onset_part, onset_frame[usable], delta[usable], PULSE_RESPONSE_FRAMES)
        rig_delta = np.where(pulsed, delta, 0.0)[rows]
        signal[rows] = expected_me(data["signed_coherence"].to_numpy(float)[rows], responses[rig], onset_frame[rows], rig_delta, pulse_responses[rig], n_frames)
    noise = me - signal

    # checks: the noise should have ~zero mean per coherence, and no pulse-locked residue
    print("ME per % coherence at 0, 50, 100, 150, 250, 500, 983 ms:")
    for rig in responses:
        print(f"  {rig} onset step: {np.round(responses[rig][[0, 3, 6, 9, 15, 30, 59]], 2).tolist()}")
        print(f"  {rig} pulse:      {np.round(pulse_responses[rig][[0, 3, 6, 9, 15, 30, 59]], 2).tolist()}")
    per_coh = pd.DataFrame(noise[:, 9:].mean(axis=1), columns=["n"]).groupby(data["signed_coherence"]).n.mean()
    print("mean noise (% coherence) per coherence after 150 ms:", per_coh.round(2).to_dict())
    pulsed = np.flatnonzero(data["sched_pulse_type"].to_numpy() != 0)
    on = data["pulse_onset_frame"].to_numpy()[pulsed].astype(int) - 1
    direction = np.sign(data["pulse_coherence"].to_numpy()[pulsed] - data["signed_coherence"].to_numpy()[pulsed])
    window = np.arange(0, 30)
    locked_noise = np.array([noise[i, o + window] * s for i, o, s in zip(pulsed, on, direction) if o + 30 <= n_frames])
    locked_me = np.array([(me[i, o + window] - me[i, max(o - 1, 0)]) * s for i, o, s in zip(pulsed, on, direction) if o + 30 <= n_frames])
    print(f"pulse-locked (0-500 ms, sign-aligned): peak mean ME change {locked_me.mean(0).max():.1f}, peak |mean noise| {np.abs(locked_noise.mean(0)).max():.1f} (% coherence)")

    out_dir = processed_dir / "ddm"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ddm_inputs_{region}.npz"
    np.savez(
        out_path,
        agg_code=data["agg_code"].to_numpy(str),
        subject_id=data["subject_id"].to_numpy(str),
        idx_session=data["idx_session"].to_numpy(),
        data_source=data["data_source"].to_numpy(str),
        signed_coherence=data["signed_coherence"].to_numpy(float) / 100,
        pulse_type=data["pulse_type"].to_numpy(int),
        sched_pulse_type=data["sched_pulse_type"].to_numpy(int),
        condition=(data["signed_coherence"].round().astype(int) * 10 + data["sched_pulse_type"]).to_numpy(int),
        rt=np.where(data["censored"], np.inf, data["reaction_time"]).astype(float),  # inf = no response by 5 s
        choice=np.where(data["censored"], -1, data["choice"].fillna(-1)).astype(int),  # -1 = censored
        censored=data["censored"].to_numpy(bool),
        signal=(signal / 100).astype(np.float32),
        noise=(noise / 100).astype(np.float32),
        onset_response_ucla=responses.get("ucla"),
        onset_response_uw=responses.get("uw"),
        pulse_response_ucla=pulse_responses.get("ucla"),
        pulse_response_uw=pulse_responses.get("uw"),
        frame_rate=FRAME_RATE,
        region=region,
    )
    print(f"saved {len(data)} trials x {n_frames} frames -> {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="global")
    main(parser.parse_args().region)
