"""Exploratory postdecision timing alternative to persistent drift variability.

The decision process and contaminant guesses are unchanged. For genuine DDM
responses, D = ndt * exp(ndt_sigma * Z - ndt_sigma**2 / 2) is added *after*
bound crossing. Thus ndt remains the mean response delay, not sensory latency.
The existing independent unit_sv normal draw is reused only when sv is zero;
no random-stream changes are needed and sigma=0 preserves legacy output exactly.
"""
from __future__ import annotations

import numpy as np

from src.ddm.simulator import DriftDiffusionSimulator


def response_delays(mean: float, sigma: float, standard_normal: np.ndarray) -> np.ndarray:
    """Positive, mean-preserving lognormal delays (zero if mean is zero)."""
    if not np.isfinite(mean) or mean < 0:
        raise ValueError("ndt must be finite and nonnegative")
    if not np.isfinite(sigma) or sigma < 0:
        raise ValueError("ndt_sigma must be finite and nonnegative")
    z = np.asarray(standard_normal)
    if not np.isfinite(z).all():
        raise ValueError("Delay normal draws must be finite")
    return mean * np.exp(sigma * z.astype(np.float64) - 0.5 * sigma**2)


class ResponseDelaySimulator(DriftDiffusionSimulator):
    """Legacy simulator with an optional independent postdecision delay spread.

    The returned choices do not depend on delay. Deadline selection and minimum
    RT mapping occur later in DecisionModel, after contaminant replacement.
    """

    def simulate_trials(self, stimulus, params, unit_noise=None, unit_sv=None,
                        unit_sz=None, labels=None):
        sigma = float(params.get("ndt_sigma", 0.0))
        if not np.isfinite(sigma) or sigma < 0:
            raise ValueError("ndt_sigma must be finite and nonnegative")
        if sigma == 0.0:
            return super().simulate_trials(stimulus, params, unit_noise, unit_sv, unit_sz, labels)
        if float(params.get("sv", 0.0)) != 0.0:
            raise ValueError("This alternative replaces sv; do not reuse a draw for both sv and response delay")
        n = self._n_trials(stimulus)
        z = np.random.standard_normal(n) if unit_sv is None else np.asarray(unit_sv)
        if z.shape != (n,):
            raise ValueError(f"Expected {n} independent delay draws, received {z.shape}")
        delay = response_delays(float(params["ndt"]), sigma, z)
        out = super().simulate_trials(stimulus, {**params, "ndt": 0.0},
                                      unit_noise, unit_sv, unit_sz, labels)
        return out.assign(rt=out["rt"].to_numpy(dtype=float) + delay)

    @staticmethod
    def _n_trials(stimulus):
        return (stimulus[0] if isinstance(stimulus, tuple) else stimulus).shape[0]
