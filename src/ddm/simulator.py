from __future__ import annotations
import logging
import numpy as np
import pandas as pd
import torch
from numba import jit, prange

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weights of the extra channels of a tuple stimulus (signal, channel 1, channel 2, ...), in order; a missing weight is 1.
CHANNEL_WEIGHTS = ("noise_weight", "noise_weight_2", "noise_weight_3")

# ---------------------------------------------------------------------------
# Private backends
# ---------------------------------------------------------------------------


@jit(nopython=True, parallel=True)
def _simulate_ddm_trials_numba(
    stimulus: np.ndarray,
    noise: np.ndarray,
    sv_draws: np.ndarray,  # (n_trials,) per-trial drift offset ~ N(0, sv)
    z_offsets: np.ndarray,  # (n_trials,) per-trial z offset ~ Uniform(-sz/2, sz/2)
    drift_gain: float,
    drift_offset: float,
    a: float,
    z: float,
    ndt: float,
    dt: float,
    leak_rate: float,
    time_constant: float,
    gain_decay: float,
    sample_threshold: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """sample_threshold > 0: extrema detection (Stine et al. 2020): each step's evidence sample (drift + noise) is
    compared with +-sample_threshold and nothing is accumulated; a, z, leak and urgency are then unused."""
    n_trials, n_timepoints = stimulus.shape
    rt = np.full(n_trials, np.nan, dtype=np.float32)
    choice = np.full(n_trials, np.nan, dtype=np.float32)

    for trial in prange(n_trials):
        z_trial = min(0.99, max(0.01, z + z_offsets[trial]))
        starting_point = z_trial * a
        evidence = starting_point
        trial_drift_offset = drift_offset + sv_draws[trial]

        for t in range(1, n_timepoints):
            if np.isnan(stimulus[trial, t]):
                break

            gain = drift_gain * np.exp(-gain_decay * (t - 1) * dt) if gain_decay != 0.0 else drift_gain
            drift = (gain * stimulus[trial, t - 1] + trial_drift_offset) * dt
            if sample_threshold > 0.0:
                sample = drift + noise[trial, t - 1]
                if sample >= sample_threshold:
                    rt[trial] = t * dt + ndt
                    choice[trial] = 1.0
                    break
                if sample <= -sample_threshold:
                    rt[trial] = t * dt + ndt
                    choice[trial] = 0.0
                    break
                continue
            leak = leak_rate * (evidence - starting_point) * dt
            evidence += drift + noise[trial, t - 1] - leak

            if time_constant != 0.0:
                urgency_factor = 1.0 + t * dt * time_constant
                decision_var = starting_point + (evidence - starting_point) * urgency_factor
            else:
                decision_var = evidence

            if decision_var >= a:
                rt[trial] = t * dt + ndt
                choice[trial] = 1.0
                break
            if decision_var <= 0.0:
                rt[trial] = t * dt + ndt
                choice[trial] = 0.0
                break

    return rt, choice


def front_end_active(params: dict) -> bool:
    """True if a visual front-end transform (primacy plan, amendment 7) changes the input."""
    return float(params.get("fe_gamma", 1.0)) != 1.0 or float(params.get("fe_beta", 0.0)) != 0.0


def front_end_numpy(stim: np.ndarray, params: dict) -> np.ndarray:
    """Front end applied to the drift input x(t) before accumulation (amendment 7); identity with default parameters.
    Power law: x' = sign(x)|x|^fe_gamma. Temporal divisive normalization: x'(t) = x(t) / (1 + fe_beta * p(t)), where
    p is a causal exponential low-pass of |x| with time constant fe_tau (s): p[t] = (1 - k) p[t-1] + k |x[t]|,
    k = dt / fe_tau, p starting at 0. Returns a new array; NaN (no stimulus) stays NaN."""
    gamma, beta = float(params.get("fe_gamma", 1.0)), float(params.get("fe_beta", 0.0))
    x = np.asarray(stim, dtype=np.float32)
    if gamma != 1.0:
        x = (np.sign(x) * np.abs(x) ** gamma).astype(np.float32)
    if beta != 0.0:
        from scipy.signal import lfilter

        k = min(1.0, float(params["dt"]) / float(params["fe_tau"]))
        pool = lfilter([k], [1.0, k - 1.0], np.nan_to_num(np.abs(x)), axis=1)
        x = (x / (1.0 + beta * pool)).astype(np.float32)
    return x


def front_end_torch(stim: torch.Tensor, params: dict) -> torch.Tensor:
    """torch version of front_end_numpy (same definition); the low-pass is an exact FFT convolution with the
    exponential kernel over the whole trial. Never modifies `stim` in place (it may be a cached input)."""
    gamma, beta = float(params.get("fe_gamma", 1.0)), float(params.get("fe_beta", 0.0))
    x = stim
    if gamma != 1.0:
        x = torch.sign(x) * torch.abs(x) ** gamma
    if beta != 0.0:
        n = x.shape[1]
        k = min(1.0, float(params["dt"]) / float(params["fe_tau"]))
        lags = torch.arange(n, device=x.device, dtype=torch.float64)
        kernel = k * (1.0 - k) ** lags
        a = torch.nan_to_num(torch.abs(x)).to(torch.float64)
        pool = torch.fft.irfft(torch.fft.rfft(a, n=2 * n) * torch.fft.rfft(kernel, n=2 * n), n=2 * n)[:, :n]
        x = (x / (1.0 + beta * pool)).to(torch.float32)
    return x


class _NumbaSimulator:
    """Numba JIT backend — fastest on CPU due to per-trial early termination."""

    def simulate_trials(
        self,
        stimulus: np.ndarray,
        params: dict,
        unit_noise: np.ndarray | None = None,
        unit_sv: np.ndarray | None = None,
        unit_sz: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        if isinstance(stimulus, tuple):
            signal, *channels = stimulus
            assert len(channels) <= len(CHANNEL_WEIGHTS), f"{len(channels)} extra channels; weights for {len(CHANNEL_WEIGHTS)}"
            stimulus = np.asarray(signal, dtype=np.float32)
            for name, channel in zip(CHANNEL_WEIGHTS, channels):
                stimulus = stimulus + float(params.get(name, 1.0)) * np.asarray(channel, dtype=np.float32)
        if stimulus.size == 0:
            return np.array([], dtype=np.float32), np.array([], dtype=np.float32)
        stim = np.asarray(stimulus, dtype=np.float32)
        if front_end_active(params):
            stim = front_end_numpy(stim, params)
        n_trials, n_timepoints = stim.shape
        noise_std = np.sqrt(params["variance"] * params["dt"])
        if unit_noise is not None:
            noise = (unit_noise * noise_std).astype(np.float32)
        else:
            noise = np.random.normal(0.0, noise_std, (n_trials, n_timepoints - 1)).astype(np.float32)

        sv = float(params.get("sv", 0.0))
        sz = float(params.get("sz", 0.0))
        if sv > 0.0:
            sv_draws = (unit_sv * sv).astype(np.float32) if unit_sv is not None else np.random.normal(0.0, sv, n_trials).astype(np.float32)
        else:
            sv_draws = np.zeros(n_trials, dtype=np.float32)
        if sz > 0.0:
            z_offsets = ((unit_sz - 0.5) * sz).astype(np.float32) if unit_sz is not None else (np.random.uniform(-0.5, 0.5, n_trials) * sz).astype(np.float32)
        else:
            z_offsets = np.zeros(n_trials, dtype=np.float32)

        return _simulate_ddm_trials_numba(
            stim,
            noise,
            sv_draws,
            z_offsets,
            params["drift_gain"],
            params["drift_offset"],
            params["a"],
            params["z"],
            params["ndt"],
            params["dt"],
            params["leak_rate"],
            params["time_constant"],
            float(params.get("gain_decay", 0.0)),
            float(params.get("extrema_bound", 0.0)) * noise_std,
        )


class _TorchSimulator:
    """
    PyTorch GPU/CPU backend.

    No-leak path: fully vectorized via cumsum — no Python loop over timesteps.
    Leak path: closed-form FFT convolution.
    Fastest when CUDA is available; on CPU, _NumbaSimulator wins due to early
    termination (most trials cross long before the stimulus end).
    """

    def __init__(self, device: str | None = None):
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        self._cache: dict = {}

    def _to_device(self, array: np.ndarray, slot: str) -> torch.Tensor:
        """Upload `array` once and reuse it while the same array (data pointer + shape) is passed again.

        During fitting the same stimulus and per-rep noise arrays are passed thousands of times. Each slot keeps
        one array per data pointer, so all n_reps noise draws stay on the device instead of being re-uploaded
        every rep.
        """
        key = (array.__array_interface__["data"][0], array.shape)
        slot_cache = self._cache.setdefault(slot, {})
        if key not in slot_cache:
            slot_cache[key] = torch.tensor(array, device=self.device, dtype=torch.float32)
        return slot_cache[key]

    def clear_cache(self) -> None:
        self._cache = {}

    def simulate_trials(
        self,
        stimulus: np.ndarray | torch.Tensor,
        params: dict,
        unit_noise: np.ndarray | None = None,
        unit_sv: np.ndarray | None = None,
        unit_sz: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        dev = self.device
        if isinstance(stimulus, tuple):
            # (signal, channel, ...): drift input = signal + sum of CHANNEL_WEIGHTS[k] * channel k
            signal, *channels = (c.to(dev, dtype=torch.float32) if isinstance(c, torch.Tensor) else self._to_device(c, f"stimulus_{i}") for i, c in enumerate(stimulus))
            assert len(channels) <= len(CHANNEL_WEIGHTS), f"{len(channels)} extra channels; weights for {len(CHANNEL_WEIGHTS)}"
            stim = signal
            for name, channel in zip(CHANNEL_WEIGHTS, channels):
                stim = stim + float(params.get(name, 1.0)) * channel
        elif isinstance(stimulus, torch.Tensor):
            stim = stimulus.to(dev, dtype=torch.float32)
        else:
            stim = self._to_device(stimulus, "stimulus")

        if stim.numel() == 0:
            return np.array([], dtype=np.float32), np.array([], dtype=np.float32)
        if front_end_active(params):
            stim = front_end_torch(stim, params)

        n_trials, n_timepoints = stim.shape
        T = n_timepoints - 1

        a = float(params["a"])
        z = float(params["z"])
        ndt = float(params["ndt"])
        drift_gain = float(params["drift_gain"])
        drift_offset = float(params["drift_offset"])
        variance = float(params["variance"])
        dt = float(params["dt"])
        leak_rate = float(params["leak_rate"])
        time_constant = float(params["time_constant"])
        gain_decay = float(params.get("gain_decay", 0.0))
        sv = float(params.get("sv", 0.0))
        sz = float(params.get("sz", 0.0))

        noise_std = (variance * dt) ** 0.5

        valid = ~torch.isnan(stim[:, 1:])  # (N, T)
        if gain_decay != 0.0:
            # time-varying evidence weight: drift_gain * exp(-gain_decay * t), t from stimulus onset (s)
            gain_t = drift_gain * torch.exp(-gain_decay * dt * torch.arange(T, device=dev, dtype=torch.float32))
            drift_inc = torch.nan_to_num((gain_t * stim[:, :-1] + drift_offset) * dt)  # (N, T)
        else:
            drift_inc = torch.nan_to_num((drift_gain * stim[:, :-1] + drift_offset) * dt)  # (N, T)

        # sv: per-trial drift variability — add a constant offset to each trial's drift
        if sv > 0.0:
            if unit_sv is not None:
                sv_draws = self._to_device(unit_sv, "unit_sv").unsqueeze(1) * sv
            else:
                sv_draws = torch.randn(n_trials, 1, device=dev) * sv  # (N, 1)
            drift_inc = drift_inc + sv_draws * dt  # broadcast over T

        # sz: per-trial starting point variability — Uniform(z - sz/2, z + sz/2)
        if sz > 0.0:
            if unit_sz is not None:
                z_offsets = (self._to_device(unit_sz, "unit_sz") - 0.5) * sz
            else:
                z_offsets = (torch.rand(n_trials, device=dev) - 0.5) * sz
            z_trials = torch.clamp(z + z_offsets, 0.01, 0.99)
            sp = (z_trials * a).unsqueeze(1)  # (N, 1)
        else:
            sp = z * a  # scalar

        if unit_noise is not None:
            noise_inc = self._to_device(unit_noise, "unit_noise") * noise_std  # (N, T)
        else:
            noise_inc = torch.randn(n_trials, T, device=dev) * noise_std  # (N, T)

        sample_threshold = float(params.get("extrema_bound", 0.0)) * noise_std
        if sample_threshold > 0.0:
            # extrema detection (Stine et al. 2020): each step's sample is compared with +-threshold, nothing accumulated
            sample = drift_inc + noise_inc
            upper = (sample >= sample_threshold) & valid
            lower = (sample <= -sample_threshold) & valid
        elif leak_rate == 0.0:
            evidence = sp + torch.cumsum((drift_inc + noise_inc) * valid, dim=1)
        else:
            # ------------------------------------------------------------------
            # Leak: e[t] = α·e[t-1] + b[t],  α = 1 − leak·dt
            #
            # Closed-form solution via FFT convolution (no Python time loop):
            #   e[t] = αᵗ·sp  +  Σ_{j=0}^{t-1} α^{t-1-j} · b[j]
            #        = αᵗ·sp  +  (b ★ w)[t-1]   where w[k] = αᵏ
            # ------------------------------------------------------------------
            α = 1.0 - leak_rate * dt
            b = (drift_inc + noise_inc + sp * leak_rate * dt) * valid  # (N, T)
            t_exp = torch.arange(1, T + 1, device=dev, dtype=torch.float32)

            if leak_rate < 0:
                # Negative leak (self-exciting accumulator, α > 1): the FFT weights α^k grow and single-precision FFT
                # loses accuracy (tested: 1-4% of trials off by > 1 ms). Use the rescaled cumulative sum
                #   e[t] = α^t · (sp + Σ_{j<t} α^(−1−j) · b[j]),
                # whose weights α^(−1−j) shrink, in double precision.
                k = torch.arange(T, device=dev, dtype=torch.float64)
                a64 = torch.tensor(α, device=dev, dtype=torch.float64)
                scaled = torch.cumsum(b.double() * a64.pow(-1.0 - k), dim=1)  # (N, T)
                evidence = (a64.pow(t_exp.double()) * (sp + scaled)).float()
            else:
                fft_n = 1 << (2 * T - 1).bit_length()  # next power-of-2 ≥ 2T-1
                k = torch.arange(T, device=dev, dtype=torch.float32)
                w = torch.tensor(α, device=dev, dtype=torch.float32).pow(k)  # (T,)

                particular = torch.fft.irfft(
                    torch.fft.rfft(b, n=fft_n, dim=1) * torch.fft.rfft(w, n=fft_n),
                    n=fft_n,
                    dim=1,
                )[:, :T]  # (N, T)

                evidence = torch.tensor(α, device=dev).pow(t_exp) * sp + particular  # (N, T)

        if sample_threshold <= 0.0:
            if time_constant != 0.0:
                t_idx = torch.arange(1, n_timepoints, device=dev, dtype=torch.float32)
                decision_var = sp + (evidence - sp) * (1.0 + t_idx * dt * time_constant)
            else:
                decision_var = evidence
            upper = (decision_var >= a) & valid
            lower = (decision_var <= 0) & valid
        crossed = upper | lower

        rt = torch.full((n_trials,), float("nan"), device=dev, dtype=torch.float32)
        choice = torch.full((n_trials,), float("nan"), device=dev, dtype=torch.float32)

        has_crossed = crossed.any(dim=1)
        if has_crossed.any():
            first_idx = crossed[has_crossed].int().argmax(dim=1)
            rt[has_crossed] = (first_idx.float() + 1) * dt + ndt
            choice[has_crossed] = upper[has_crossed].gather(1, first_idx.unsqueeze(1)).squeeze(1).float()

        return rt.cpu().numpy(), choice.cpu().numpy()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class DriftDiffusionSimulator:
    """
    Auto-selecting DDM simulator.

    Uses the PyTorch GPU backend when CUDA is available (vectorized, no
    Python loop over timesteps). Falls back to the Numba JIT backend on
    CPU-only machines, which is faster there due to per-trial early
    termination.

    Pass device="cuda" to force GPU (warns and falls back if unavailable).
    Pass device="cpu" to force Numba regardless of GPU availability.
    """

    def __init__(self, device: str | None = None):
        if device == "cuda":
            if not torch.cuda.is_available():
                logger.warning("CUDA requested but unavailable, falling back to Numba CPU.")
                self._backend = _NumbaSimulator()
                self.device = torch.device("cpu")
            else:
                self._backend = _TorchSimulator("cuda")
                self.device = self._backend.device
        elif torch.cuda.is_available() and device != "cpu":
            self._backend = _TorchSimulator()
            self.device = self._backend.device
        else:
            self._backend = _NumbaSimulator()
            self.device = torch.device("cpu")

        logger.info(
            "DriftDiffusionSimulator using %s backend on %s",
            type(self._backend).__name__,
            self.device,
        )

    def precompute_noise(
        self,
        n_trials: int,
        n_timepoints: int,
        n_reps: int = 1,
    ) -> dict:
        """Return precomputed unit draws for CRN across all optimizer iterations.

        Keys:
          unit_noise : (n_reps, n_trials, n_timepoints-1)  standard normal
          unit_sv    : (n_reps, n_trials)                   standard normal (scale by sv)
          unit_sz    : (n_reps, n_trials)                   uniform [0,1)  (map to (-sz/2, sz/2))
        """
        return {
            "unit_noise": np.random.standard_normal((n_reps, n_trials, n_timepoints - 1)).astype(np.float32),
            "unit_sv": np.random.standard_normal((n_reps, n_trials)).astype(np.float32),
            "unit_sz": np.random.uniform(0.0, 1.0, (n_reps, n_trials)).astype(np.float32),
        }

    def simulate_trials(
        self,
        stimulus: np.ndarray | torch.Tensor | tuple,
        params: dict,
        unit_noise: np.ndarray | None = None,
        unit_sv: np.ndarray | None = None,
        unit_sz: np.ndarray | None = None,
        labels: np.ndarray | None = None,
    ) -> pd.DataFrame:
        """Simulate one decision per trial.

        `stimulus` is (n_trials, n_timepoints), or a (signal, noise) tuple of such arrays whose drift input is
        signal + params["noise_weight"] * noise; further channels take the later CHANNEL_WEIGHTS. `labels` gives each trial's condition (e.g. coherence) for the
        likelihood; without it the first stimulus sample is used, which is only right for a constant stimulus.
        """
        rt, choice = self._backend.simulate_trials(stimulus, params, unit_noise=unit_noise, unit_sv=unit_sv, unit_sz=unit_sz)
        if labels is None:
            if isinstance(stimulus, tuple):
                raise ValueError("labels are required for a two-channel stimulus")
            labels = stimulus[:, 0]
        return pd.DataFrame({"signed_coherence": labels, "rt": rt, "choice": choice})

    def clear_cache(self) -> None:
        if hasattr(self._backend, "clear_cache"):
            self._backend.clear_cache()
