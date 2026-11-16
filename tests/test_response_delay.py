"""Scientific contract tests for the exploratory postdecision delay model.

Run: OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv/bin/python -m tests.test_response_delay
"""
import numpy as np
import pandas as pd
import torch

from src.ddm.ddm import apply_guesses
from src.ddm.response_delay import ResponseDelaySimulator, response_delays
from src.ddm.simulator import DriftDiffusionSimulator
from scripts.ddm.fit_mouse_ddm import MouseDDM, make_params, RESPONDED_LIKELIHOOD_PARAMS


def fixture():
    rng = np.random.default_rng(111)
    stimulus = rng.normal(.3, .2, (80, 501)).astype(np.float32)
    free, fixed = make_params("L0U0V0Z0G1", "fast_only", n_pulse_times=2)
    p = {k: float(v.value) for k, v in fixed.items()} | dict(
        ndt=.2, a=1., z=.5, drift_gain=4., drift_offset=.1,
        p_guess=.25, guess_bias=.4, guess_tau=.1, noise_weight=1., noise_weight_2=1.)
    draws = dict(unit_noise=rng.normal(size=(80, 500)).astype(np.float32),
                 unit_sv=rng.normal(size=80).astype(np.float32),
                 unit_sz=rng.random(80).astype(np.float32), labels=np.arange(80) % 2)
    return stimulus, free, fixed, p, draws


def run():
    stimulus, free, fixed, p, draws = fixture()
    summary = {}
    for device in ["cpu"] + (["cuda"] if torch.cuda.is_available() else []):
        ref, alt = DriftDiffusionSimulator(device), ResponseDelaySimulator(device)
        a = ref.simulate_trials(stimulus, p, **draws)
        b = alt.simulate_trials(stimulus, {**p, "ndt_sigma": 0.}, **draws)
        pd.testing.assert_frame_equal(a, b, check_exact=True)
        a_sv = ref.simulate_trials(stimulus, {**p, "sv": .4}, **draws)
        b_sv = alt.simulate_trials(stimulus, {**p, "sv": .4, "ndt_sigma": 0.}, **draws)
        pd.testing.assert_frame_equal(a_sv, b_sv, check_exact=True)
        c = alt.simulate_trials(stimulus, {**p, "ndt_sigma": .6}, **draws)
        pd.testing.assert_series_equal(a.choice, c.choice)
        decision = ref.simulate_trials(stimulus, {**p, "ndt": 0.}, **draws)
        delay = response_delays(p["ndt"], .6, draws["unit_sv"])
        np.testing.assert_allclose(c.rt, decision.rt + delay, atol=1e-12)
        pd.testing.assert_frame_equal(c, alt.simulate_trials(stimulus, {**p, "ndt_sigma": .6}, **draws), check_exact=True)
        assert (c.rt.dropna() > 0).all()
        assert np.array_equal(np.isnan(c.rt), np.isnan(decision.rt))
        guesses = np.random.default_rng(44).random((80, 3))
        c_guess = apply_guesses(c, p, guesses)
        ref_guess = apply_guesses(a, p, guesses)
        is_guess = guesses[:, 0] < p["p_guess"]
        pd.testing.assert_frame_equal(c_guess.loc[is_guess], ref_guess.loc[is_guess], check_exact=True)
        model = MouseDDM(free, fixed, device=device, censor_at=.4, min_rt=(.3, "floor"),
                         likelihood_params=RESPONDED_LIKELIHOOD_PARAMS)
        mapped = model._map_outcomes(c_guess)
        late = ~np.isfinite(c_guess.rt) | (c_guess.rt > .4)
        assert (mapped.loc[late, "choice"] == -1).all()
        assert np.isinf(mapped.loc[late, "rt"]).all()
        assert (mapped.loc[~late, "rt"] >= .3).all()
        summary[device] = c
        print(f"PASS {device}: zero-spread exact, drift baseline exact, fixed decision choices, independent delay, guesses, deadline/floor, deterministic draws")
    if "cuda" in summary:
        pd.testing.assert_series_equal(summary["cpu"].choice, summary["cuda"].choice)
        np.testing.assert_allclose(summary["cpu"].rt, summary["cuda"].rt, atol=2e-6)
        print("PASS CPU/GPU equivalence on common draws")
    for args in [(-.1, .2), (.2, -.1), (.2, np.nan)]:
        try:
            response_delays(*args, np.zeros(3))
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid delay parameter accepted")
    try:
        ResponseDelaySimulator("cpu").simulate_trials(stimulus, {**p, "sv": .3, "ndt_sigma": .2}, **draws)
    except ValueError:
        pass
    else:
        raise AssertionError("Correlated drift and delay draw accepted")
    z = np.random.default_rng(123).normal(size=500_000)
    d = response_delays(.4, .8, z)
    assert (d > 0).all() and abs(d.mean() - .4) < .002
    assert abs(d.var() - .4**2 * np.expm1(.8**2)) < .002
    assert np.all(response_delays(0., .8, z) == 0)
    print(f"PASS lognormal moments: mean={d.mean():.6f}, variance={d.var():.6f}; invalid inputs rejected")


if __name__ == "__main__":
    run()
