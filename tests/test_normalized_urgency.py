"""Check of the normalized urgency used by the urgency-gating variant (plan 2026-11-10-ugm-corner-leak-urgency).

  python -m tests.test_normalized_urgency

With urgency_ref > 0 the simulator should behave as a leaky accumulator whose displacement from the start is multiplied
by (1 + u t) / (1 + u urgency_ref) before comparison with bounds 0 and a. A plain NumPy loop implementing exactly that
(written independently of simulator.normalized_urgency) must give the same choices and RTs as the numba and torch
backends with the same noise draws; without urgency_ref the simulator must be unchanged.
"""

import numpy as np

from src.ddm.simulator import DriftDiffusionSimulator, _NumbaSimulator, _TorchSimulator


def reference(stim, unit_noise, unit_sv, p):
    """Euler loop with the normalized gain written out explicitly (no sz)."""
    n, T = stim.shape
    dt, sd = p["dt"], np.sqrt(p["variance"] * p["dt"])
    norm = 1.0 + p["time_constant"] * p["urgency_ref"]
    rt, choice = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        sp = p["z"] * p["a"]
        disp = 0.0  # E - sp
        off = p["drift_offset"] + unit_sv[i] * p["sv"]
        for t in range(1, T):
            disp += (p["drift_gain"] * stim[i, t - 1] + off) * dt + unit_noise[i, t - 1] * sd - p["leak_rate"] * disp * dt
            dv = sp + disp * (1.0 + t * dt * p["time_constant"]) / norm
            if dv >= p["a"] or dv <= 0.0:
                rt[i], choice[i] = t * dt + p["ndt"], float(dv >= p["a"])
                break
    return rt, choice


def run(backend, stim, noise, sv, p):
    sim = DriftDiffusionSimulator(device="cpu")
    sim._backend = backend
    out = sim.simulate_trials(stim, p, unit_noise=noise, unit_sv=sv, unit_sz=np.zeros(len(stim), dtype=np.float32), labels=np.zeros(len(stim)))
    return out["rt"].to_numpy(dtype=float), out["choice"].to_numpy(dtype=float)


def main():
    rng = np.random.default_rng(0)
    n, T = 400, 3000
    stim = np.repeat(rng.choice([-0.36, -0.1, 0.0, 0.1, 0.36], n)[:, None], T, axis=1).astype(np.float32)
    noise = rng.standard_normal((n, T - 1)).astype(np.float32)
    sv = rng.standard_normal(n).astype(np.float32)
    base = dict(ndt=0.1, a=1.2, z=0.5, drift_gain=8.0, drift_offset=0.0, variance=1.0, dt=0.001, leak_rate=8.0, time_constant=20.0, sv=1.0, sz=0.0, urgency_ref=1.0)
    for label, p in [("UGM u=20 L=8", base), ("u=2 L=3 z=0.4", {**base, "time_constant": 2.0, "leak_rate": 3.0, "z": 0.4, "a": 2.0}),
                     ("u=50 L=20", {**base, "time_constant": 50.0, "leak_rate": 20.0, "a": 0.6, "drift_gain": 30.0})]:
        ref_rt, ref_ch = reference(stim, noise, sv, p)
        for name, backend in [("numba", _NumbaSimulator()), ("torch", _TorchSimulator("cpu"))]:
            rt, ch = run(backend, stim, noise, sv, p)
            same_nan = np.array_equal(np.isnan(rt), np.isnan(ref_rt))
            ok = np.isfinite(rt) & np.isfinite(ref_rt)
            ch_agree = np.mean(ch[ok] == ref_ch[ok])
            rt_close = np.mean(np.abs(rt[ok] - ref_rt[ok]) <= 0.0015)  # float32 vs float64: at most a step apart
            print(f"{label:16s} {name}: decided {ok.mean():.2f}, same undecided {same_nan}, choice agree {ch_agree:.3f}, RT within 1 step {rt_close:.3f}")
            assert same_nan and ch_agree >= 0.99 and rt_close >= 0.99, (label, name)
    # urgency_ref absent or 0: identical to the old behaviour
    p0 = {k: v for k, v in base.items() if k != "urgency_ref"}
    for backend in (_NumbaSimulator(), _TorchSimulator("cpu")):
        a = run(backend, stim, noise, sv, p0)
        b = run(backend, stim, noise, sv, {**p0, "urgency_ref": 0.0})
        assert np.array_equal(a[0], b[0], equal_nan=True) and np.array_equal(a[1], b[1], equal_nan=True)
    print("all checks passed")


if __name__ == "__main__":
    main()
