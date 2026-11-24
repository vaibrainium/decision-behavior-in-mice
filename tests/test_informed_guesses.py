"""Checks for informed fast guesses (plan 2026-11-24-informed-guess-family).

  python -m tests.test_informed_guesses

1. rt and choice do not depend on read_step, in both backends (numba exactly; torch exactly against itself).
2. The DV readout of both backends matches an independent float64 NumPy loop (>= 99% of trials; float32 vs float64),
   including readout at step 0, after an earlier bound crossing, and after the input has ended (NaN tail).
3. The numba readout equals the counterfactual kernel of scripts.paper.guess_readout_counterfactual (readout_mid) exactly.
4. apply_guesses with guess_w = 0 is identical to the model without guess_w; guess_w = 1 makes every guess report the DV;
   at intermediate w the blind guesses keep choice probability guess_bias.
5. MouseDDM.simulate with guess_w = 0 reproduces the standard simulation exactly (same seed).
"""
import numpy as np
import pandas as pd

from src.ddm.ddm import apply_guesses, informed_read_steps
from src.ddm.simulator import DriftDiffusionSimulator, _NumbaSimulator, _TorchSimulator, _simulate_ddm_trials_numba


def reference(stim, noise, sv, p, read_step):
    n, T = stim.shape
    dt, sd = p["dt"], np.sqrt(p["variance"] * p["dt"])
    rt, choice, read = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        sp = p["z"] * p["a"]
        e = sp
        dv = sp
        off = p["drift_offset"] + sv[i] * p["sv"]
        if read_step[i] == 0:
            read[i] = float(dv > p["a"] / 2)
        for t in range(1, T):
            if np.isnan(stim[i, t]):
                break
            e += (p["drift_gain"] * stim[i, t - 1] + off) * dt + noise[i, t - 1] * sd - p["leak_rate"] * (e - sp) * dt
            dv = sp + (e - sp) * (1.0 + t * dt * p["time_constant"])
            if dv >= p["a"] or dv <= 0.0:
                rt[i], choice[i] = t * dt + p["ndt"], float(dv >= p["a"])
                break
            if t == read_step[i]:
                read[i] = float(dv > p["a"] / 2)
        if read_step[i] >= 0 and np.isnan(read[i]):
            read[i] = choice[i] if np.isfinite(choice[i]) else float(dv > p["a"] / 2)
    return rt, choice, read


def run(backend, stim, noise, sv, p, read_step=None):
    sim = DriftDiffusionSimulator(device="cpu")
    sim._backend = backend
    out = sim.simulate_trials(stim, p, unit_noise=noise, unit_sv=sv, unit_sz=np.zeros(len(stim), dtype=np.float32),
                              labels=np.zeros(len(stim)), read_step=read_step)
    return out


def main():
    rng = np.random.default_rng(1)
    n, T = 600, 2000
    stim = np.repeat(rng.choice([-0.36, -0.1, 0.0, 0.1, 0.36], n)[:, None], T, axis=1).astype(np.float32)
    stim[:, 300:500] += rng.choice([-1.0, 0.0, 1.0], n)[:, None]  # pulses
    stim[: n // 6, 1200:] = np.nan  # input ends early on some trials
    noise = rng.standard_normal((n, T - 1)).astype(np.float32)
    sv = rng.standard_normal(n).astype(np.float32)
    read_step = rng.integers(-1, 1800, n).astype(np.int64)
    read_step[:20] = 0
    base = dict(ndt=0.2, a=1.6, z=0.55, drift_gain=6.0, drift_offset=0.1, variance=1.0, dt=0.001, leak_rate=0.0, time_constant=0.0,
                sv=0.5, sz=0.0)
    for label, p in [("plain", base), ("leak+urgency", {**base, "leak_rate": 3.0, "time_constant": 2.0}),
                     ("strong urgency", {**base, "leak_rate": 2.0, "time_constant": 15.0, "a": 2.5})]:
        rrt, rch, rread = reference(stim, noise, sv, p, read_step)
        has = read_step >= 0
        for name, backend in [("numba", _NumbaSimulator()), ("torch", _TorchSimulator("cpu"))]:
            plain = run(backend, stim, noise, sv, p)
            out = run(backend, stim, noise, sv, p, read_step)
            # 1. rt/choice unchanged by the readout
            assert np.array_equal(np.nan_to_num(plain.rt.to_numpy(), nan=-9), np.nan_to_num(out.rt.to_numpy(), nan=-9)), (label, name)
            assert np.array_equal(np.nan_to_num(plain.choice.to_numpy(), nan=-9), np.nan_to_num(out.choice.to_numpy(), nan=-9)), (label, name)
            assert "read_choice" not in plain and np.isnan(out.read_choice.to_numpy()[~has]).all()
            # 2. readout vs float64 reference
            agree = np.mean(out.read_choice.to_numpy()[has] == rread[has])
            print(f"{label:15s} {name}: readout agrees with reference {agree:.4f}; undecided trials {np.isnan(rrt).mean():.2f}")
            assert agree >= 0.99, (label, name, agree)
        # 3. exact equality with the counterfactual kernel (same float32 operations)
        from scripts.paper.guess_readout_counterfactual import kernel as cf_kernel
        zoff = np.zeros(n, dtype=np.float32)
        args = (stim, (noise * np.sqrt(p["variance"] * p["dt"])).astype(np.float32), (sv * p["sv"]).astype(np.float32), zoff,
                p["drift_gain"], p["drift_offset"], p["a"], p["z"], p["ndt"], p["dt"], p["leak_rate"], p["time_constant"])
        _, _, prod_read = _simulate_ddm_trials_numba(*args, 0.0, 0.0, read_step)
        _, _, cf_mid, _ = cf_kernel(*args, read_step)
        assert np.array_equal(prod_read[has], cf_mid[has]), label
    # 4. apply_guesses
    m = 20000
    draws = rng.uniform(size=(m, 3))
    sim = pd.DataFrame({"rt": rng.uniform(0.4, 2, m), "choice": rng.integers(0, 2, m).astype(float),
                        "read_choice": rng.integers(0, 2, m).astype(float)})
    g = dict(p_guess=0.3, guess_bias=0.7, guess_tau=0.2, guess_t0=0.3, dt=0.001, read_lag=0.1)
    a0 = apply_guesses(sim, {**g, "guess_w": 0.0}, draws)
    b0 = apply_guesses(sim.drop(columns="read_choice"), g, draws)
    assert a0[["rt", "choice"]].equals(b0[["rt", "choice"]])
    assert informed_read_steps({**g, "guess_w": 0.0}, draws) is None
    guess = draws[:, 0] < g["p_guess"]
    a1 = apply_guesses(sim, {**g, "guess_w": 1.0}, draws)
    assert np.array_equal(a1.choice.to_numpy()[guess], sim.read_choice.to_numpy()[guess])
    w = 0.4
    ah = apply_guesses(sim, {**g, "guess_w": w}, draws)
    blind = guess & (draws[:, 1] >= w)
    print(f"blind-guess right fraction {ah.choice.to_numpy()[blind].mean():.3f} (guess_bias {g['guess_bias']})")
    assert abs(ah.choice.to_numpy()[blind].mean() - g["guess_bias"]) < 0.03
    steps = informed_read_steps({**g, "guess_w": w}, draws)
    informed = guess & (draws[:, 1] < w)
    assert np.array_equal(steps >= 0, informed)
    # 5. MouseDDM.simulate: guess_w = 0 identical to the standard model
    from scripts.ddm.primacy import make_model
    model = make_model("L0U0V0Z0G1", "ucla", fixed_guess_bias=False, responded=True)
    p = dict(dt=0.001, variance=1.0, guess_t0=0.3, leak_rate=0.0, time_constant=0.0, sv=0.0, sz=0.0, ndt=0.2, a=2.0, z=0.5,
             drift_gain=1.0, drift_offset=0.0, p_guess=0.2, guess_bias=0.5, guess_tau=0.2)
    s0 = model.simulate(stim[:200], p, n_reps=2, seed=7, labels=np.zeros(200))
    s1 = model.simulate(stim[:200], {**p, "guess_w": 0.0, "read_lag": 0.1}, n_reps=2, seed=7, labels=np.zeros(200))
    assert s0[["rt", "choice"]].equals(s1[["rt", "choice"]])
    s2 = model.simulate(stim[:200], {**p, "guess_w": 1.0, "read_lag": 0.1}, n_reps=2, seed=7, labels=np.zeros(200))
    assert len(s2) == len(s0)
    print("all informed-guess checks passed")


if __name__ == "__main__":
    main()
