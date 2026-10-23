"""Package F candidate model for the tau_p pilot (EXPLORATORY; frozen spec models/f2_spec_tau_pilot.json).

input = no-pulse input + w * (pulse component convolved with a causal exponential kernel exp(-t/tau_p)/tau_p of unit
area), on the 1 ms simulator grid. tau_p = 0 is the identity (the existing amendment 6 revised model). The pulse
component and the no-pulse input come from scripts.ddm.primacy.gain_stimuli (pulse change x pulse-response template);
the ME filter delay is not modified. The kernel is the discrete first-order filter y[t] = a y[t-1] + (1 - a) x[t],
a = exp(-1 ms / tau_p), whose impulse response (1 - a) a^n sums to exactly 1 (unit area) and is causal.

Simulation goes through the existing MouseDDM (two-channel stimulus, noise_weight = w), with common random numbers drawn
once per (mouse, seed) and reused for every (tau_p, w), exactly as scripts.ddm.fit_pulse_gain.gain_nll_function does.

CLI (benchmark one point before a full run):
  NUMBA_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m scripts.pulse_followup.models benchmark \
      --run-id <RUN_ID> --mouse PSUIM7 --tau 100 --w 2.0
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

from scripts.pulse_followup import io

RUN_SUB = "tau_pilot"
DT_MS = 1.0


def spec_path(run_path):
    return Path(run_path) / "models" / "f2_spec_tau_pilot.json"


def load_spec(run_path, expected_sha=None):
    p = spec_path(run_path)
    if expected_sha and io.sha256_file(p) != expected_sha:
        raise RuntimeError(f"{p} does not match the frozen sha256")
    spec = json.loads(p.read_text())
    if io.sha256_file(spec["inputs"]["ddm_inputs"]) != spec["inputs"]["ddm_inputs_sha256"]:
        raise RuntimeError("v2 DDM inputs do not match the sha256 frozen in the spec")
    return spec


def exp_kernel(pulse_ms: np.ndarray, tau_ms: float) -> np.ndarray:
    """Causal unit-area exponential filter along time (axis 1). tau_ms = 0 returns the input unchanged."""
    if tau_ms == 0:
        return pulse_ms
    a = np.exp(-DT_MS / tau_ms)
    return lfilter([1 - a], [1, -a], pulse_ms, axis=1).astype(np.float32)


def candidate_stimuli(inputs, rows, tau_ms):
    """(no-pulse input, filtered pulse component) at 1 ms, from primacy.gain_stimuli."""
    from scripts.ddm import primacy

    without, pulse = primacy.gain_stimuli(inputs, rows)
    return without, exp_kernel(pulse, tau_ms)


class CandidateSimulator:
    """One mouse, one CRN seed: precompute the random numbers once, then simulate any (tau_p, w)."""

    def __init__(self, inputs, rows, params, variant, rig, seed, n_reps):
        from scripts.ddm import primacy

        self.params, self.n_reps, self.rows = params, n_reps, rows
        self.cond = inputs["condition"][rows]
        self.model = primacy.make_model(variant, rig)
        self.without, self._pulse = primacy.gain_stimuli(inputs, rows)
        np.random.seed(seed)  # same sequence as fit_pulse_gain.gain_nll_function / diagnostics.simulate
        self.model.simulator.clear_cache()
        self.model._labels = self.cond
        self.model.precompute(*self.without.shape, n_reps=n_reps)
        self._tau, self._filtered = None, None

    def simulate(self, tau_ms, w):
        if tau_ms != self._tau:
            self.model.simulator.clear_cache()
            self._filtered, self._tau = exp_kernel(self._pulse, tau_ms), tau_ms
        n = len(self.rows)
        res = self.model._simulate_condition((self.without, self._filtered), {**self.params, "noise_weight": float(w)}, self.n_reps)
        if res is None or len(res) != self.n_reps * n:
            raise RuntimeError("simulation lost rows")
        if not (res["signed_coherence"].to_numpy().reshape(self.n_reps, n) == self.cond[None, :]).all():
            raise RuntimeError("label order differs from trial order")
        return res["rt"].to_numpy().reshape(self.n_reps, n), res["choice"].to_numpy().astype(int).reshape(self.n_reps, n)


def benchmark(run_id, mouse, tau, w):
    from scripts.ddm import primacy
    from scripts.ddm.fit_mouse_ddm import load_inputs
    from scripts.pulse_followup import diagnostics

    run = io.run_dir(run_id)
    spec = load_spec(run)
    out = io.stage_dir(run, "models") / RUN_SUB
    out.mkdir(exist_ok=True)
    if (out / "COMPLETE").exists():
        raise FileExistsError(f"{out} is complete")
    inputs = load_inputs(Path(spec["inputs"]["ddm_inputs"]))
    pr = diagnostics.load_revised("primary", mouse)
    rows = primacy.pulse_rows(inputs, mouse)
    t0 = time.time()
    sim = CandidateSimulator(inputs, rows, pr["params"], pr["variant"], pr["rig"], seed=50, n_reps=spec["simulation"]["reps"])
    t_pre = time.time() - t0
    t1 = time.time()
    sim.simulate(tau, w)
    t_sim = time.time() - t1
    rec = {"mouse": mouse, "tau_ms": tau, "w": w, "n_trials": len(rows), "n_reps": sim.n_reps, "precompute_s": round(t_pre, 2),
           "one_point_s": round(t_sim, 2), "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    io.write_json(out / f"benchmark_{mouse}_tau{tau:g}_w{w:g}.json", rec)
    print(json.dumps(rec))
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["benchmark"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--mouse", default="PSUIM7")
    ap.add_argument("--tau", type=float, default=100.0, help="ms")
    ap.add_argument("--w", type=float, default=2.0)
    a = ap.parse_args(argv)
    benchmark(a.run_id, a.mouse, a.tau, a.w)


if __name__ == "__main__":
    main()
